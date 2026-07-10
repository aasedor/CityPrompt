"""AI generation provider adapter layer.

Processing tasks own workflow, persistence, and storage. Engine adapters encapsulate
provider-specific API calls, polling, refinement, and remote asset download.
"""

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
# PREVIEW + REFINE, leaving headroom to download/upload a ~30 MB GLB. The
# Celery soft_time_limit is derived from it (see tasks/processing.py) so the
# two can never drift back out of sync.
MESHY_PREVIEW_TIMEOUT_S = 600   # 10 min
MESHY_REFINE_TIMEOUT_S = 900    # 15 min; on timeout we keep the preview mesh
MESHY_IO_HEADROOM_S = 300       # GLB download + S3 upload + thumbnail
MESHY_MAX_RUNTIME_S = (
    MESHY_PREVIEW_TIMEOUT_S + MESHY_REFINE_TIMEOUT_S + MESHY_IO_HEADROOM_S
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

        result = await client.poll_until_done(task_id, timeout=MESHY_PREVIEW_TIMEOUT_S, task_type=task_type)
        preview_glb_url = (result.get("model_urls") or {}).get("glb")
        if preview_callback and preview_glb_url:
            try:
                preview_callback(await self._download_bytes(preview_glb_url))
            except Exception as exc:
                logger.warning("Failed to download Meshy preview model (non-fatal): %s", exc)

        final_task_id = task_id
        if mode == "text" and refine:
            self._emit_progress(progress_callback, 0.55, "refining")
            try:
                refine_task_id = await client.text_to_3d_refine(
                    task_id,
                    texture_prompt=f"realistic architectural materials and textures for: {prompt[:200]}",
                )
                logger.info("Refine task started: %s (from preview %s)", refine_task_id, task_id)
                self._emit_task_id(task_callback, refine_task_id)
                final_task_id = refine_task_id
                result = await client.poll_until_done(refine_task_id, timeout=MESHY_REFINE_TIMEOUT_S, task_type="text")
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
            except Exception as exc:
                logger.error("Refine step FAILED for building %s: %s", building_id, exc, exc_info=True)
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
        refine: bool = True,
        negative_prompt: str | None = None,
        building_id: str | None = None,
        progress_callback: ProgressCallback | None = None,
        task_callback: TaskCallback | None = None,
        preview_callback: PreviewCallback | None = None,
    ) -> GenerationResult:
        # Tripo doesn't support refine or preview_callback (single-step generation)
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