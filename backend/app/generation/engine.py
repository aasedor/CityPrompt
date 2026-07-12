"""AI generation provider adapter layer.

Processing tasks own workflow, persistence, and storage. Engine adapters encapsulate
provider-specific API calls, polling, refinement, and remote asset download.
"""

import asyncio
import enum
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

import httpx

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync

logger = logging.getLogger(__name__)
settings = get_settings()

ProgressCallback = Callable[[float, str], None]
TaskCallback = Callable[[str], None]
PreviewCallback = Callable[[bytes], None]

# ── Meshy runtime ceilings ───────────────────────────────────────────────
# Meshy's latency has grown (Meshy-6 meshes + PBR texturing). The old poll
# ceilings (300s preview + 600s refine) summed to EXACTLY the Celery soft
# limit of 900s, so any slow refine guaranteed a soft-kill part-way through
# the upload — the task died after Meshy had already been paid, and the retry
# re-ran the whole generation from scratch.
#
# INVARIANT: MESHY_MAX_RUNTIME_S must stay strictly greater than
# PREVIEW + (attempts × REFINE), leaving headroom to download/upload a ~30 MB
# GLB. The Celery soft_time_limit is derived from it (see tasks/processing.py)
# so the two can never drift back out of sync.
MESHY_PREVIEW_TIMEOUT_S = 600   # 10 min
MESHY_REFINE_TIMEOUT_S = 900    # 15 min; on timeout we keep the preview mesh
MESHY_REFINE_ATTEMPTS = 2       # refine failures are intermittent — retry once
MESHY_IO_HEADROOM_S = 300       # GLB download + S3 upload + thumbnail
# multi_image fuses up to 4 views + remesh + PBR in a single task (no refine
# leg), so it gets one longer poll: 1800 + IO headroom = 2100 < MAX_RUNTIME.
MESHY_MULTI_IMAGE_TIMEOUT_S = 1800
# Two-stage chain: an Image-to-Image multi-view synth (stage 1) feeds
# multi_image_to_3d (stage 2). Stage 1 is transient-failure-prone, so it gets
# a shared retry deadline; the whole stage stays within this ceiling.
MESHY_IMAGE_TO_IMAGE_TIMEOUT_S = 600
MESHY_MULTIVIEW_ATTEMPTS = 3
# poll_until_done checks its wall-clock deadline only at each loop top, so a
# poll leg can overrun its timeout by one status GET (60s) + one poll_interval
# (10s). Both provider paths run two poll legs (preview+refine, or chain
# stage1+stage2), so budget ~140s of intrinsic slack — otherwise the zero-sum
# sub-timeouts equal the soft_time_limit exactly and a degraded API trips it.
MESHY_POLL_OVERRUN_S = 2 * (60 + 10)
# The Celery soft_time_limit derives from this. It must cover the LONGEST
# provider path: text (preview + 2 refines) OR the chain (stage 1 + stage 2).
# Both come to 2400s of Meshy work; +IO headroom +poll overrun.
MESHY_MAX_RUNTIME_S = (
    max(
        MESHY_PREVIEW_TIMEOUT_S + MESHY_REFINE_ATTEMPTS * MESHY_REFINE_TIMEOUT_S,
        MESHY_IMAGE_TO_IMAGE_TIMEOUT_S + MESHY_MULTI_IMAGE_TIMEOUT_S,
    )
    + MESHY_IO_HEADROOM_S
    + MESHY_POLL_OVERRUN_S
)


class GenerationEngine(str, enum.Enum):
    """Available AI 3D generation engine identifiers."""
    MESHY = "meshy"
    TRIPO = "tripo"


@dataclass
class GenerationResult:
    """Provider output returned to the task orchestrator."""
    glb_data: bytes
    engine: str
    task_id: str
    lod_glb_data: dict[str, bytes] = field(default_factory=dict)
    thumbnail_url: str | None = None
    metadata: dict = field(default_factory=dict)


class BaseGenerationEngine(ABC):
    """Abstract base class for AI 3D generation providers."""

    engine_id: str = ""

    def _emit_progress(
        self,
        callback: ProgressCallback | None,
        progress: float,
        step: str,
    ) -> None:
        if callback:
            callback(progress, step)

    def _emit_task_id(self, callback: TaskCallback | None, task_id: str | None) -> None:
        if callback and task_id:
            callback(task_id)

    async def _download_bytes(self, url: str, timeout: float = 60.0) -> bytes:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    @abstractmethod
    async def run_generation(
        self,
        *,
        prompt: str,
        mode: str = "text",
        image_url: str | None = None,
        image_urls: list[str] | None = None,
        target_polycount: int | None = None,
        multiview_prompt: str | None = None,
        refine: bool = True,
        negative_prompt: str | None = None,
        building_id: str | None = None,
        progress_callback: ProgressCallback | None = None,
        task_callback: TaskCallback | None = None,
        preview_callback: PreviewCallback | None = None,
    ) -> GenerationResult:
        """Run provider-specific generation and return downloaded model assets."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is configured."""
        ...


class MeshyEngine(BaseGenerationEngine):
    """Provider adapter for Meshy."""

    engine_id = "meshy"

    def is_available(self) -> bool:
        return bool(settings.meshy_api_key)

    async def run_generation(
        self,
        *,
        prompt: str,
        mode: str = "text",
        image_url: str | None = None,
        image_urls: list[str] | None = None,
        target_polycount: int | None = None,
        multiview_prompt: str | None = None,
        refine: bool = True,
        negative_prompt: str | None = None,
        building_id: str | None = None,
        progress_callback: ProgressCallback | None = None,
        task_callback: TaskCallback | None = None,
        preview_callback: PreviewCallback | None = None,
    ) -> GenerationResult:
        from app.generation.meshy_client import MeshyClient

        client = MeshyClient()
        negative = negative_prompt or ""

        # Balance-floor guard: refuse to START a paid generation when the
        # account balance is at/below the configured floor. Balance check
        # failures don't block (the guard is best-effort, not a gate on
        # Meshy API availability).
        if settings.meshy_min_balance_floor > 0:
            try:
                balance = (await client.get_balance()).get("balance")
            except Exception:
                balance = None
            if balance is not None and balance <= settings.meshy_min_balance_floor:
                raise RuntimeError(
                    f"Meshy balance {balance} at/below floor "
                    f"{settings.meshy_min_balance_floor} — generation refused "
                    "(meshy_min_balance_floor in config)."
                )

        self._emit_progress(progress_callback, 0.1, "calling_meshy")

        if mode == "image":
            if not image_url:
                raise ValueError("image_url is required for Meshy image mode")
            task_id = await client.image_to_3d(image_url)
            task_type = "image"
            log_api_usage_sync(
                provider=self.engine_id,
                operation="image_to_3d",
                credits_used=20,
                task_id=task_id,
                building_id=building_id,
            )
        elif mode == "multi_image":
            if not image_urls:
                raise ValueError("image_urls is required for Meshy multi_image mode")
            # prompt doubles as the texture_prompt here — geometry comes from
            # the views, so callers send materials/colors language, not massing.
            if multiview_prompt:
                # Two-stage chain: synthesize mutually-consistent, auto-isolated
                # views (Image-to-Image multi-view), then reconstruct from them.
                # Fixes cross-view inconsistency (warped windows) and strips
                # entourage without a separate cleanup pass. Stage 1 fast-fails
                # intermittently, so retry within a shared deadline that keeps
                # the whole stage inside MESHY_IMAGE_TO_IMAGE_TIMEOUT_S.
                self._emit_progress(progress_callback, 0.2, "synthesizing_views")
                loop = asyncio.get_event_loop()
                stage1_deadline = loop.time() + MESHY_IMAGE_TO_IMAGE_TIMEOUT_S
                iresult = None
                last_exc: Exception | None = None
                for attempt in range(1, MESHY_MULTIVIEW_ATTEMPTS + 1):
                    if stage1_deadline - loop.time() < 30:
                        break
                    try:
                        i2i_id = await client.image_to_image_multiview(image_urls, multiview_prompt)
                        # Re-sample AFTER the create POST so its time is charged
                        # against the shared deadline — keeps stage 1 <= ceiling.
                        poll_budget = int(stage1_deadline - loop.time())
                        if poll_budget < 30:
                            break
                        iresult = await client.poll_until_done(
                            i2i_id, timeout=poll_budget, task_type="image_to_image"
                        )
                        break
                    except Exception as exc:
                        last_exc = exc
                        logger.warning(
                            "Multi-view synthesis attempt %d/%d failed: %s",
                            attempt, MESHY_MULTIVIEW_ATTEMPTS, exc,
                        )
                if iresult is None:
                    raise RuntimeError(
                        f"Multi-view synthesis failed after {MESHY_MULTIVIEW_ATTEMPTS} attempts: {last_exc}"
                    )
                log_api_usage_sync(
                    provider=self.engine_id,
                    operation="image_to_image_multiview",
                    credits_used=9,
                    task_id=iresult.get("id"),
                    building_id=building_id,
                )
                task_id = await client.multi_image_to_3d(
                    input_task_id=iresult["id"],
                    texture_prompt=prompt or "",
                    target_polycount=target_polycount or 30000,
                )
            else:
                task_id = await client.multi_image_to_3d(
                    image_urls,
                    texture_prompt=prompt or "",
                    target_polycount=target_polycount or 30000,
                )
            task_type = "multi_image"
            log_api_usage_sync(
                provider=self.engine_id,
                operation="multi_image_to_3d",
                credits_used=30,
                task_id=task_id,
                building_id=building_id,
            )
        else:
            task_id = await client.text_to_3d_preview(prompt, negative_prompt=negative)
            task_type = "text"
            log_api_usage_sync(
                provider=self.engine_id,
                operation="text_to_3d_preview",
                credits_used=10,
                task_id=task_id,
                building_id=building_id,
            )

        self._emit_task_id(task_callback, task_id)
        self._emit_progress(progress_callback, 0.3, "polling")

        poll_timeout = (
            MESHY_MULTI_IMAGE_TIMEOUT_S if mode == "multi_image" else MESHY_PREVIEW_TIMEOUT_S
        )
        result = await client.poll_until_done(task_id, timeout=poll_timeout, task_type=task_type)
        preview_glb_url = (result.get("model_urls") or {}).get("glb")
        if preview_callback and preview_glb_url:
            try:
                preview_callback(await self._download_bytes(preview_glb_url))
            except Exception as exc:
                logger.warning("Failed to download Meshy preview model (non-fatal): %s", exc)

        final_task_id = task_id
        if mode == "text" and refine:
            self._emit_progress(progress_callback, 0.55, "refining")
            # Refine failures are intermittent on Meshy's side (observed live:
            # 2 of 4 failed, immediate siblings succeeded) — one retry converts
            # most would-be clay fallbacks into textured models.
            for attempt in range(1, MESHY_REFINE_ATTEMPTS + 1):
                try:
                    refine_task_id = await client.text_to_3d_refine(
                        task_id,
                        texture_prompt=f"realistic architectural materials and textures for: {prompt[:200]}",
                    )
                    logger.info(
                        "Refine task started: %s (from preview %s, attempt %d)",
                        refine_task_id, task_id, attempt,
                    )
                    self._emit_task_id(task_callback, refine_task_id)
                    result = await client.poll_until_done(refine_task_id, timeout=MESHY_REFINE_TIMEOUT_S, task_type="text")
                    final_task_id = refine_task_id
                    logger.info(
                        "Meshy refine result keys: %s, model_urls: %s",
                        list(result.keys()),
                        (result.get("model_urls") or {}).keys() if result.get("model_urls") else "NONE",
                    )
                    log_api_usage_sync(
                        provider=self.engine_id,
                        operation="text_to_3d_refine",
                        credits_used=10,
                        task_id=refine_task_id,
                        building_id=building_id,
                    )
                    break
                except Exception as exc:
                    logger.error(
                        "Refine attempt %d FAILED for building %s: %s",
                        attempt, building_id, exc, exc_info=True,
                    )
                    if attempt == MESHY_REFINE_ATTEMPTS:
                        logger.warning("Falling back to preview model (will lack textures)")
        elif mode == "text":
            logger.info("Refine disabled for building %s - using preview model", building_id)

        self._emit_progress(progress_callback, 0.7, "downloading")

        model_urls = result.get("model_urls", {})
        glb_url = model_urls.get("glb") or model_urls.get("obj")
        if not glb_url:
            raise RuntimeError("No GLB model URL in Meshy result")

        glb_data = await self._download_bytes(glb_url)
        return GenerationResult(
            glb_data=glb_data,
            engine=self.engine_id,
            task_id=final_task_id,
            thumbnail_url=result.get("thumbnail_url"),
            metadata=result,
        )


class TripoEngine(BaseGenerationEngine):
    """Provider adapter for Tripo."""

    engine_id = "tripo"

    def is_available(self) -> bool:
        return bool(settings.tripo_api_key)

    async def run_generation(
        self,
        *,
        prompt: str,
        mode: str = "text",
        image_url: str | None = None,
        image_urls: list[str] | None = None,
        target_polycount: int | None = None,
        multiview_prompt: str | None = None,
        refine: bool = True,
        negative_prompt: str | None = None,
        building_id: str | None = None,
        progress_callback: ProgressCallback | None = None,
        task_callback: TaskCallback | None = None,
        preview_callback: PreviewCallback | None = None,
    ) -> GenerationResult:
        # Tripo doesn't support refine or preview_callback (single-step generation)
        if mode == "multi_image":
            raise ValueError("Tripo does not support multi_image mode")

        from app.generation.tripo_client import TripoClient

        client = TripoClient()

        self._emit_progress(progress_callback, 0.1, "calling_tripo")

        if mode == "image":
            if not image_url:
                raise ValueError("image_url is required for Tripo image mode")
            task_id = await client.image_to_3d(image_url)
            log_api_usage_sync(
                provider=self.engine_id,
                operation="image_to_3d",
                credits_used=30,
                task_id=task_id,
                building_id=building_id,
            )
        else:
            task_id = await client.text_to_3d(prompt, negative_prompt=negative_prompt)
            log_api_usage_sync(
                provider=self.engine_id,
                operation="text_to_3d",
                credits_used=30,
                task_id=task_id,
                building_id=building_id,
            )

        self._emit_task_id(task_callback, task_id)
        self._emit_progress(progress_callback, 0.3, "polling_tripo")

        result = await client.poll_until_done(task_id, timeout=120)
        model_url_remote = result.get("model_url") or result.get("output", {}).get("model", {}).get("url")
        if not model_url_remote:
            raise RuntimeError("No model URL in Tripo result")

        lod_glb_data: dict[str, bytes] = {}
        try:
            self._emit_progress(progress_callback, 0.5, "smart_low_poly")
            low_poly_task_id = await client.smart_low_poly(task_id)
            low_poly_result = await client.poll_until_done(low_poly_task_id, timeout=120)
            lod_model_url_remote = low_poly_result.get("model_url") or low_poly_result.get("output", {}).get("model", {}).get("url")
            log_api_usage_sync(
                provider=self.engine_id,
                operation="retopology",
                credits_used=10,
                task_id=low_poly_task_id,
                building_id=building_id,
            )
            if lod_model_url_remote:
                lod_glb_data["1"] = await client.download_model(lod_model_url_remote)
        except Exception as exc:
            logger.warning("Tripo smart_low_poly failed (non-fatal): %s", exc)

        self._emit_progress(progress_callback, 0.7, "downloading")
        glb_data = await client.download_model(model_url_remote)

        return GenerationResult(
            glb_data=glb_data,
            engine=self.engine_id,
            task_id=task_id,
            lod_glb_data=lod_glb_data,
            metadata=result,
        )


_ENGINES: dict[str, BaseGenerationEngine] = {
    GenerationEngine.MESHY.value: MeshyEngine(),
    GenerationEngine.TRIPO.value: TripoEngine(),
}


def get_engine(engine_id: str) -> BaseGenerationEngine:
    """Get a provider adapter by ID."""
    engine = _ENGINES.get(str(engine_id))
    if not engine:
        raise ValueError(f"Unknown engine: {engine_id}")
    return engine


def get_best_available_engine(preference: str | None = None) -> BaseGenerationEngine:
    """Get the best available AI provider, respecting preference with fallback."""
    if preference and preference in _ENGINES:
        engine = _ENGINES[preference]
        if engine.is_available():
            return engine
        logger.warning("Preferred engine '%s' is not available, falling back", preference)

    default = _ENGINES.get(settings.default_generation_engine)
    if default and default.is_available():
        return default

    for engine in _ENGINES.values():
        if engine.is_available():
            return engine

    raise RuntimeError("No AI generation engine is configured. Set MESHY_API_KEY or TRIPO_API_KEY.")