"""
Generation engine abstraction layer.

Provides a unified interface for multiple 3D generation backends
(Meshy.ai, Tripo3D, and procedural) with automatic fallback.
"""

import enum
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GenerationEngine(str, enum.Enum):
    """Available 3D generation engine identifiers."""
    MESHY = "meshy"
    TRIPO = "tripo"
    PROCEDURAL = "procedural"


@dataclass
class GenerationResult:
    """Result from a 3D generation engine."""
    glb_data: bytes | None = None
    lod_urls: dict[str, str] = field(default_factory=dict)
    engine: str = ""
    task_id: str = ""
    metadata: dict = field(default_factory=dict)


class BaseGenerationEngine(ABC):
    """Abstract base class for 3D generation engines."""

    @abstractmethod
    async def generate(self, prompt: str, style: str | None = None, **kwargs) -> str:
        """Start generation and return a task_id."""
        ...

    @abstractmethod
    async def poll(self, task_id: str, timeout: int = 300) -> GenerationResult:
        """Poll for completion and return the result."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is configured and available."""
        ...


class MeshyEngine(BaseGenerationEngine):
    """Wrapper around existing MeshyClient."""

    def is_available(self) -> bool:
        return bool(settings.meshy_api_key)

    async def generate(self, prompt: str, style: str | None = None, **kwargs) -> str:
        from app.generation.meshy_client import MeshyClient
        client = MeshyClient()
        negative = kwargs.get("negative_prompt", "")
        task_id = await client.text_to_3d_preview(prompt, negative_prompt=negative)
        return task_id

    async def poll(self, task_id: str, timeout: int = 300) -> GenerationResult:
        from app.generation.meshy_client import MeshyClient
        client = MeshyClient()
        result = await client.poll_until_done(task_id, timeout=timeout)
        model_urls = result.get("model_urls", {})
        glb_url = model_urls.get("glb") or model_urls.get("obj")
        glb_data = None
        if glb_url:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as http:
                resp = await http.get(glb_url)
                glb_data = resp.content
        return GenerationResult(
            glb_data=glb_data,
            engine="meshy",
            task_id=task_id,
            metadata=result,
        )


class TripoEngine(BaseGenerationEngine):
    """Wrapper around TripoClient."""

    def is_available(self) -> bool:
        return bool(settings.tripo_api_key)

    async def generate(self, prompt: str, style: str | None = None, **kwargs) -> str:
        from app.generation.tripo_client import TripoClient
        client = TripoClient()
        negative = kwargs.get("negative_prompt")
        task_id = await client.text_to_3d(prompt, negative_prompt=negative)
        return task_id

    async def poll(self, task_id: str, timeout: int = 120) -> GenerationResult:
        from app.generation.tripo_client import TripoClient
        client = TripoClient()
        result = await client.poll_until_done(task_id, timeout=timeout)
        model_url = result.get("model_url")
        glb_data = None
        if model_url:
            glb_data = await client.download_model(model_url)
        return GenerationResult(
            glb_data=glb_data,
            engine="tripo",
            task_id=task_id,
            metadata=result,
        )


_ENGINES: dict[str, BaseGenerationEngine] = {
    "meshy": MeshyEngine(),
    "tripo": TripoEngine(),
}


def get_engine(engine_id: str) -> BaseGenerationEngine:
    """Get a generation engine by ID."""
    engine = _ENGINES.get(engine_id)
    if not engine:
        raise ValueError(f"Unknown engine: {engine_id}")
    return engine


def get_best_available_engine(preference: str | None = None) -> BaseGenerationEngine:
    """Get the best available engine, respecting user preference with fallback."""
    if preference and preference in _ENGINES:
        engine = _ENGINES[preference]
        if engine.is_available():
            return engine
        logger.warning(f"Preferred engine '{preference}' is not available, falling back")

    # System default
    default = _ENGINES.get(settings.default_generation_engine)
    if default and default.is_available():
        return default

    # Any available
    for engine in _ENGINES.values():
        if engine.is_available():
            return engine

    raise RuntimeError("No AI generation engine is configured. Set MESHY_API_KEY or TRIPO_API_KEY.")
