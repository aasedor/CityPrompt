"""
Async client for Meshy.ai API — text-to-3D (v2) and image-to-3D (v1) generation.

Meshy's image-to-3D endpoint exists only under /openapi/v1/ — posting to
/openapi/v2/image-to-3d returns 404 (verified live 2026-07-10).
"""

import asyncio
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Meshy's text-to-3D API rejects prompts over 800 chars with a 400. Our
# compose_zone_prompt output runs ~2,300 chars (rich site context, good for
# the render pipeline), so it must be trimmed before it reaches Meshy.
MESHY_PROMPT_MAX = 800


def _cap_prompt(text: str, limit: int = MESHY_PROMPT_MAX) -> str:
    """Trim to Meshy's char limit, preferring a word boundary."""
    if not text or len(text) <= limit:
        return text or ""
    cut = text[:limit]
    space = cut.rfind(" ")
    return cut[:space] if space > limit * 0.6 else cut


class MeshyClientError(RuntimeError):
    """A PERMANENT Meshy client error (4xx other than 429) — retrying it just
    burns the same request again (e.g. prompt too long, bad params)."""


class MeshyClient:
    """Async client for Meshy.ai v2 API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.meshy_api_key
        self.base_url = (base_url or settings.meshy_api_base).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=60.0,
        )

    @staticmethod
    def _check(resp: httpx.Response, operation: str) -> None:
        """raise_for_status, but KEEP Meshy's response body in the message.

        Meshy 4xxs carry the actual reason ("concurrent task limit", "prompt
        too long", ...) in the body — a bare status line made failures
        undiagnosable (12 buildings failed with empty errors on 2026-07-07).
        """
        if resp.status_code >= 400:
            body = resp.text[:300]
            msg = f"Meshy {operation} failed: HTTP {resp.status_code} — {body}"
            # 4xx (except 429 rate-limit) is a permanent client error — flag it
            # so the task doesn't retry a request that can only fail again.
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                raise MeshyClientError(msg)
            raise RuntimeError(msg)

    async def text_to_3d_preview(
        self,
        prompt: str,
        art_style: str = "realistic",
        negative_prompt: str = "",
        target_polycount: int | None = 30000,
    ) -> str:
        """Start a text-to-3D preview task. Returns task_id.

        Without an explicit target_polycount the raw mesh arrives at 1M+
        triangles (a salvaged refine came back 41MB, ~90% geometry,
        2026-07-11) — same trap as image-to-3D's should_remesh default.
        """
        async with self._client() as client:
            payload = {
                "mode": "preview",
                "prompt": _cap_prompt(prompt),
                "art_style": art_style,
                "topology": "triangle",
            }
            if target_polycount is not None:
                payload["target_polycount"] = target_polycount
            if negative_prompt:
                payload["negative_prompt"] = _cap_prompt(negative_prompt)

            resp = await client.post("/openapi/v2/text-to-3d", json=payload)
            self._check(resp, "text_to_3d_preview")
            data = resp.json()
            task_id = data.get("result") or data.get("task_id") or data.get("id")
            logger.info(f"Meshy text-to-3D preview started: {task_id}")
            return task_id

    async def text_to_3d_refine(self, preview_task_id: str, texture_prompt: str = "") -> str:
        """Start a text-to-3D refine task from a completed preview. Returns task_id."""
        async with self._client() as client:
            payload = {
                "mode": "refine",
                "preview_task_id": preview_task_id,
                "enable_pbr": True,
                "texture_richness": "high",
            }
            if texture_prompt:
                payload["texture_prompt"] = texture_prompt
            resp = await client.post("/openapi/v2/text-to-3d", json=payload)
            self._check(resp, "text_to_3d_refine")
            data = resp.json()
            task_id = data.get("result") or data.get("task_id") or data.get("id")
            logger.info(f"Meshy text-to-3D refine started: {task_id} (pbr=True)")
            return task_id

    async def image_to_3d(
        self,
        image_url: str,
        *,
        enable_pbr: bool = True,
        target_polycount: int | None = 30000,
        should_remesh: bool = True,
    ) -> str:
        """Start an image-to-3D task. Returns task_id.

        image_url may be a public http(s) URL or a base64 data URI.

        should_remesh defaults to False on meshy-6 and target_polycount is
        ignored without it — the raw mesh comes back at ~1.6M triangles
        (70MB+ GLB, verified 2026-07-10), so remesh stays on here.
        """
        async with self._client() as client:
            payload: dict = {
                "image_url": image_url,
                "enable_pbr": enable_pbr,
                "should_remesh": should_remesh,
            }
            if target_polycount is not None and should_remesh:
                payload["target_polycount"] = target_polycount
            resp = await client.post("/openapi/v1/image-to-3d", json=payload)
            self._check(resp, "image_to_3d")
            data = resp.json()
            task_id = data.get("result") or data.get("task_id") or data.get("id")
            logger.info(f"Meshy image-to-3D started: {task_id}")
            return task_id

    async def get_task(self, task_id: str) -> dict:
        """Get the status and result of a Meshy task."""
        async with self._client() as client:
            resp = await client.get(f"/openapi/v2/text-to-3d/{task_id}")
            resp.raise_for_status()
            return resp.json()

    async def get_image_task(self, task_id: str) -> dict:
        """Get the status and result of an image-to-3D task."""
        async with self._client() as client:
            resp = await client.get(f"/openapi/v1/image-to-3d/{task_id}")
            resp.raise_for_status()
            return resp.json()

    async def poll_until_done(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 10,
        task_type: str = "text",
    ) -> dict:
        """Poll a task until it reaches SUCCEEDED or FAILED status.

        Args:
            task_id: The Meshy task ID to poll.
            timeout: Maximum seconds to wait before timing out.
            poll_interval: Seconds between poll requests.
            task_type: 'text' or 'image' — determines which endpoint to poll.

        Returns:
            The final task result dict, including model_urls.glb when successful.

        Raises:
            TimeoutError: If the task doesn't complete within the timeout.
            RuntimeError: If the task fails.
        """
        get_fn = self.get_task if task_type == "text" else self.get_image_task
        # Wall-clock deadline, not sleep-accounting: slow status GETs (each up
        # to 60s under a degraded API) would otherwise stretch a "600s" poll
        # to multiples of that and blow the MESHY_MAX_RUNTIME_S invariant the
        # Celery limits are derived from.
        deadline = asyncio.get_event_loop().time() + timeout

        while asyncio.get_event_loop().time() < deadline:
            result = await get_fn(task_id)
            status = result.get("status", "").upper()

            if status == "SUCCEEDED":
                logger.info(f"Meshy task {task_id} succeeded")
                return result
            elif status in ("FAILED", "EXPIRED"):
                # Meshy v2 reports failure detail in task_error.message; the
                # top-level message/error keys are usually absent (which is why
                # failures used to surface as "Unknown error").
                task_error = result.get("task_error") or {}
                error_msg = (
                    (task_error.get("message") if isinstance(task_error, dict) else str(task_error))
                    or result.get("message") or result.get("error") or "Unknown error"
                )
                logger.error("Meshy task %s %s — full payload: %s", task_id, status, result)
                raise RuntimeError(f"Meshy task {task_id} failed: {error_msg}")

            logger.debug(f"Meshy task {task_id} status: {status} (progress: {result.get('progress', 0)}%)")
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Meshy task {task_id} timed out after {timeout}s")

    async def get_balance(self) -> dict:
        """Fetch current credit balance."""
        async with self._client() as client:
            resp = await client.get(f"{self.base_url}/openapi/v1/balance")
            resp.raise_for_status()
            return resp.json()
