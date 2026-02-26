"""
Async client for Tripo3D v2 API — text-to-3D, image-to-3D, and post-processing.
"""

import asyncio
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TripoClient:
    """Async client for Tripo3D v2 API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.tripo_api_key
        self.base_url = (base_url or settings.tripo_api_base).rstrip("/")
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

    async def text_to_3d(self, prompt: str, negative_prompt: str | None = None) -> str:
        """Start a text-to-3D task. Returns task_id."""
        async with self._client() as client:
            payload = {
                "type": "text_to_model",
                "prompt": prompt,
            }
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

            resp = await client.post("/v2/openapi/task", json=payload)
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("data", {}).get("task_id") or data.get("task_id")
            logger.info(f"Tripo text-to-3D started: {task_id}")
            return task_id

    async def image_to_3d(self, image_url: str) -> str:
        """Start an image-to-3D task. Returns task_id."""
        async with self._client() as client:
            payload = {
                "type": "image_to_model",
                "file": {"url": image_url},
            }
            resp = await client.post("/v2/openapi/task", json=payload)
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("data", {}).get("task_id") or data.get("task_id")
            logger.info(f"Tripo image-to-3D started: {task_id}")
            return task_id

    async def smart_low_poly(self, original_task_id: str) -> str:
        """Start AI-aware retopology for web-ready LOD. Returns task_id."""
        async with self._client() as client:
            payload = {
                "type": "retopology",
                "original_model_task_id": original_task_id,
            }
            resp = await client.post("/v2/openapi/task", json=payload)
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("data", {}).get("task_id") or data.get("task_id")
            logger.info(f"Tripo smart_low_poly started: {task_id} (from {original_task_id})")
            return task_id

    async def mesh_segmentation(self, original_task_id: str) -> str:
        """Start mesh segmentation (split into architectural components). Returns task_id."""
        async with self._client() as client:
            payload = {
                "type": "segmentation",
                "original_model_task_id": original_task_id,
            }
            resp = await client.post("/v2/openapi/task", json=payload)
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("data", {}).get("task_id") or data.get("task_id")
            logger.info(f"Tripo mesh_segmentation started: {task_id}")
            return task_id

    async def get_task(self, task_id: str) -> dict:
        """Get the status and result of a Tripo task."""
        async with self._client() as client:
            resp = await client.get(f"/v2/openapi/task/{task_id}")
            resp.raise_for_status()
            return resp.json().get("data", resp.json())

    async def poll_until_done(
        self,
        task_id: str,
        timeout: int = 120,
        poll_interval: int = 5,
    ) -> dict:
        """Poll a task until it reaches success or failure status.

        Returns:
            The final task result dict with model URLs.

        Raises:
            TimeoutError: If the task doesn't complete within the timeout.
            RuntimeError: If the task fails.
        """
        elapsed = 0
        while elapsed < timeout:
            result = await self.get_task(task_id)
            task_status = result.get("status", "").lower()

            if task_status in ("success", "succeeded"):
                logger.info(f"Tripo task {task_id} succeeded")
                # Extract model_url from nested output structure
                output = result.get("output", {})
                model_info = output.get("model", {})
                if model_info.get("url"):
                    result["model_url"] = model_info["url"]
                return result
            elif task_status in ("failed", "error", "cancelled"):
                error_msg = result.get("message") or result.get("error") or "Unknown error"
                raise RuntimeError(f"Tripo task {task_id} failed: {error_msg}")

            logger.debug(f"Tripo task {task_id} status: {task_status} (progress: {result.get('progress', 0)})")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Tripo task {task_id} timed out after {timeout}s")

    async def download_model(self, url: str) -> bytes:
        """Download a GLB model file from a Tripo URL."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            logger.info(f"Downloaded Tripo model ({len(resp.content)} bytes)")
            return resp.content
