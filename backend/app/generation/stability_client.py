"""
Async client for Stability AI image generation API.
Used for generating photorealistic architectural render previews.
"""

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def build_architectural_prompt(
    base_prompt: str,
    building_type: str | None = None,
    materials: str | None = None,
    floors: int | None = None,
    height: float | None = None,
    style_prefix: str | None = None,
    style_suffix: str | None = None,
) -> str:
    """Build a detailed architectural prompt from building data and style info."""
    parts = []

    if style_prefix:
        parts.append(style_prefix)

    parts.append(base_prompt)

    details = []
    if building_type:
        details.append(f"{building_type} building")
    if floors:
        details.append(f"{floors} stories")
    if height:
        details.append(f"{height:.0f}m tall")
    if materials:
        details.append(f"{materials} facade")
    if details:
        parts.append(", ".join(details))

    if style_suffix:
        parts.append(style_suffix)

    parts.append("photorealistic architectural visualization, professional rendering, daylight, urban context")

    return ", ".join(parts)


class StabilityClient:
    """Async client for Stability AI image generation."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.stability_api_key
        self.base_url = (base_url or settings.stability_api_base).rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*",
            },
            timeout=120.0,
        )

    async def text_to_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style_preset: str | None = None,
        negative_prompt: str | None = None,
    ) -> bytes:
        """Generate an image from a text prompt. Returns PNG image bytes."""
        async with self._client() as client:
            form_data = {
                "prompt": prompt,
                "output_format": "png",
            }
            if negative_prompt:
                form_data["negative_prompt"] = negative_prompt

            # Use Stable Image Core endpoint (simpler, good quality)
            resp = await client.post(
                "/v2beta/stable-image/generate/core",
                data=form_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "image/*",
                },
            )
            resp.raise_for_status()
            logger.info(f"Stability text-to-image generated ({len(resp.content)} bytes)")
            return resp.content

    async def image_to_image(
        self,
        image_bytes: bytes,
        prompt: str,
        strength: float = 0.7,
        negative_prompt: str | None = None,
    ) -> bytes:
        """Transform an image using a prompt (sketch-to-render). Returns PNG bytes."""
        async with self._client() as client:
            files = {"image": ("input.png", image_bytes, "image/png")}
            data = {
                "prompt": prompt,
                "strength": str(strength),
                "output_format": "png",
            }
            if negative_prompt:
                data["negative_prompt"] = negative_prompt

            resp = await client.post(
                "/v2beta/stable-image/generate/sd3",
                files=files,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "image/*",
                },
            )
            resp.raise_for_status()
            logger.info(f"Stability image-to-image generated ({len(resp.content)} bytes)")
            return resp.content

    async def get_balance(self) -> dict:
        """Fetch current credit balance."""
        async with self._client() as client:
            resp = await client.get(
                f"{self.base_url}/v1/user/balance",
                headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()
