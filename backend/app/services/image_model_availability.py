"""Read-only discovery during model rollouts; no image calls or paid retries."""

import asyncio
import hashlib
import time

import httpx

from app.core.image_models import OPENAI_IMAGE_CREDIT_MULTIPLIERS

_cache: tuple[str, float, dict] | None = None
_lock = asyncio.Lock()


async def get_image_model_availability(api_key: str) -> dict:
    global _cache
    key_id = hashlib.sha256(api_key.encode()).hexdigest()
    async with _lock:
        if _cache and _cache[0] == key_id and _cache[1] > time.monotonic():
            return _cache[2]
        available: set[str] | None = set() if not api_key else None
        if api_key:
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    response.raise_for_status()
                    available = {item["id"] for item in response.json()["data"]}
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                # Listing permissions can differ from generation permissions.
                # Unknown availability must not disable an existing engine.
                pass
        default_model = "gpt-image-2.5-flare" if available and "gpt-image-2.5-flare" in available else "gpt-image-2"
        result = {
            "default_model": default_model,
            "models": [
                {"id": model, "available": None if available is None else model in available}
                for model in OPENAI_IMAGE_CREDIT_MULTIPLIERS
            ],
        }
        _cache = (key_id, time.monotonic() + (300 if available is not None else 30), result)
        return result
