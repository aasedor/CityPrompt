"""One-shot fal submission and read-only recovery for saved-render animation.

Keep uploads and polling on the existing fal client. Queue submission uses the
documented REST API with transport retries disabled: fal-client's submit helper
retries POSTs, which is unsafe when the first paid receipt was lost.
"""

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
import io
import re

import httpx
from PIL import Image

ANIMATION_SECONDS = 5
ANIMATION_PROMPT = (
    "A single continuous architectural film shot of the building shown in the input image. "
    "The camera makes a very slow, smooth forward dolly with a level horizon and fixed focal length. "
    "The building remains rigid, with consistent rooflines, windows, façade divisions and material "
    "boundaries throughout. Preserve the lighting and colour treatment of the image. Existing foliage "
    "moves gently in a light breeze. Reflections respond subtly to the camera movement. Calm, natural "
    "motion, stable exposure and sharp architectural detail. No cuts."
)
ANIMATION_NEGATIVE_PROMPT = (
    "Warped architecture, bending edges, changing windows, melting surfaces, texture flicker, "
    "sudden camera movement, exposure pulsing, cuts, new buildings."
)
ANIMATION_SETTINGS = {"duration": "5", "generate_audio": False, "cfg_scale": 0.5}
MAX_SOURCE_BYTES = 25 * 1024 * 1024
MAX_VIDEO_BYTES = 200 * 1024 * 1024


class KlingGenerationFailed(Exception):
    """The saved fal request completed with an explicit provider failure."""


@dataclass(frozen=True)
class SourceImage:
    data: bytes
    mime_type: str
    width: int
    height: int


def validate_source_image(data: bytes) -> SourceImage:
    if not data or len(data) > MAX_SOURCE_BYTES:
        raise ValueError("The finished render must be an image under 25 MB.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}.get(
                image.format
            )
            if (
                not mime
                or min(image.size) < 128
                or image.width * image.height > 40_000_000
            ):
                raise ValueError(
                    "Use a finished PNG, JPEG or WebP render, at least 128 pixels on each side."
                )
            width, height = image.size
            image.verify()
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("The saved render is not a valid image.") from exc
    # No resize, crop, compositing or thumbnail substitution.
    return SourceImage(data, mime, width, height)


def validate_endpoint(endpoint: str) -> str:
    if (
        not re.fullmatch(
            r"fal-ai/kling-video/[A-Za-z0-9./_-]+/image-to-video", endpoint
        )
        or ".." in endpoint
    ):
        raise ValueError(
            "KLING_ANIMATION_ENDPOINT must be a fal Kling image-to-video model ID."
        )
    return endpoint


def animation_prompt(scene_direction: str = "") -> str:
    direction = scene_direction.strip()
    return ANIMATION_PROMPT + (f" Scene direction: {direction}" if direction else "")


def build_kling_arguments(start_image_url: str, scene_direction: str = "") -> dict:
    return {
        "start_image_url": start_image_url,
        **ANIMATION_SETTINGS,
        "prompt": animation_prompt(scene_direction),
        "negative_prompt": ANIMATION_NEGATIVE_PROMPT,
    }


def estimate_kling_cost(cost_per_second: float) -> float:
    return float(
        (Decimal(str(cost_per_second)) * ANIMATION_SECONDS).quantize(Decimal("0.01"))
    )


@lru_cache(maxsize=1)
def _fal_client(api_key: str):
    from fal_client import AsyncClient

    # Reuse the SDK connection pool across frequent status reads.
    return AsyncClient(key=api_key, default_timeout=60)


async def upload_kling_source(api_key: str, source: SourceImage) -> str:
    client = _fal_client(api_key)
    return await client.upload(source.data, content_type=source.mime_type)


async def submit_kling_once(api_key: str, endpoint: str, arguments: dict) -> str:
    validate_endpoint(endpoint)
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=0), timeout=60
    ) as client:
        response = await client.post(
            f"https://queue.fal.run/{endpoint}",
            headers={"Authorization": f"Key {api_key}"},
            json=arguments,
        )
        response.raise_for_status()
        request_id = response.json().get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError(
                "fal did not return a request ID. Review the provider queue before starting another clip."
            )
        return request_id


async def poll_kling_request(
    api_key: str, endpoint: str, request_id: str
) -> tuple[str, str | None]:
    from fal_client import Completed, Queued

    client = _fal_client(api_key)
    handle = await client.get_handle(endpoint, request_id)
    state = await handle.status(with_logs=False)
    if not isinstance(state, Completed):
        return ("queued" if isinstance(state, Queued) else "generating"), None
    if getattr(state, "error", None):
        raise KlingGenerationFailed(state.error)
    result = await handle.get()
    url = (result.get("video") or {}).get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError(
            "fal completed the request without a downloadable HTTPS video."
        )
    return "saving", url


async def download_kling_video(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("The provider video must use HTTPS.")
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=0),
        timeout=120,
        follow_redirects=True,
    ) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            chunks, total = [], 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > MAX_VIDEO_BYTES:
                    raise ValueError(
                        "The provider video exceeds the storage size limit."
                    )
                chunks.append(chunk)
    if not total:
        raise ValueError("The provider returned an empty video.")
    return b"".join(chunks)
