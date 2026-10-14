"""Read-only discovery during model rollouts; no image calls or paid retries."""

import asyncio
import hashlib
import time

import httpx

from app.core.image_models import OPENAI_IMAGE_CREDIT_MULTIPLIERS, NANO_BANANA_MODEL

_cache: tuple[str, float, dict] | None = None
_lock = asyncio.Lock()


async def _google_availability(api_key: str) -> bool | None:
    if not api_key:
        return False
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models/{NANO_BANANA_MODEL}",
                headers={"x-goog-api-key": api_key},
            )
            if response.status_code in {400, 401, 404}:
                return False
            if (
                response.status_code == 403
                and "reported as leaked"
                in response.json().get("error", {}).get("message", "").lower()
            ):
                return False
            response.raise_for_status()
            return (
                True
                if response.json().get("name") == f"models/{NANO_BANANA_MODEL}"
                else None
            )
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        # Metadata permission need not equal image-generation permission.
        return None


async def _openai_availability(api_key: str) -> set[str] | None:
    if not api_key:
        return set()
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            return {item["id"] for item in response.json()["data"]}
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return None


async def get_image_model_availability(api_key: str, gemini_api_key: str = "") -> dict:
    global _cache
    key_id = hashlib.sha256((api_key + "\0" + gemini_api_key).encode()).hexdigest()
    async with _lock:
        if _cache and _cache[0] == key_id and _cache[1] > time.monotonic():
            return _cache[2]
        available, google = await asyncio.gather(
            _openai_availability(api_key), _google_availability(gemini_api_key)
        )
        default_model = (
            "gpt-image-2.5-flare"
            if available and "gpt-image-2.5-flare" in available
            else "gpt-image-2"
        )
        result = {
            "default_model": default_model,
            "models": [
                {
                    "id": model,
                    "available": None if available is None else model in available,
                }
                for model in OPENAI_IMAGE_CREDIT_MULTIPLIERS
            ]
            + [{"id": NANO_BANANA_MODEL, "available": google}],
        }
        _cache = (
            key_id,
            time.monotonic()
            + (300 if available is not None and google is not None else 30),
            result,
        )
        return result
