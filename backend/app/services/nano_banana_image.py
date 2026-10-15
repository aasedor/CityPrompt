"""One paid Google Interactions request; no retries, searches or provider fallback.

Contract: https://ai.google.dev/api/interactions-api
Image options: https://ai.google.dev/gemini-api/docs/image-generation
Keep a canonical PNG of the decoded provider pixels separately from the
viewport-aligned copy; the live model currently returns JPEG only.
"""

from __future__ import annotations

import base64
import io
import math
import re
from dataclasses import dataclass

import httpx
from PIL import Image

from app.core.image_models import NANO_BANANA_MODEL

RATIOS = (
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
    "1:4",
    "4:1",
    "1:8",
    "8:1",
)


class NanoBananaProviderError(RuntimeError):
    def __init__(
        self,
        message,
        *,
        billing_status="unknown",
        provider_status_code=None,
        provider_request_id=None,
        transport_interrupted=False,
        provider_image_base64=None,
    ):
        super().__init__(message)
        self.billing_status = billing_status
        self.provider_status_code = provider_status_code
        self.provider_request_id = provider_request_id
        self.transport_interrupted = transport_interrupted
        self.provider_image_base64 = provider_image_base64


@dataclass(frozen=True)
class NanoBananaImage:
    image: Image.Image
    provider_image_base64: str


def _read_image(encoded: str) -> Image.Image:
    raw = base64.b64decode(encoded.split(",", 1)[-1], validate=True)
    if len(raw) > 40_000_000:
        raise ValueError("Image exceeds the payload limit")
    image = Image.open(io.BytesIO(raw))
    if (
        image.format not in {"PNG", "JPEG", "WEBP"}
        or getattr(image, "n_frames", 1) != 1
    ):
        raise ValueError("A single PNG, JPEG or WebP image is required")
    if max(image.size) > 16384 or image.width * image.height > 32_000_000:
        raise ValueError("Image exceeds the decoded pixel limit")
    image.load()
    return image.convert("RGB")


def _png(image: Image.Image) -> str:
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("ascii")


async def generate_nano_banana_image(
    api_key: str,
    parts: list[dict],
    *,
    target_size: tuple[int, int],
    same_camera_images: set[str] | None = None,
    resolution: str = "2K",
) -> NanoBananaImage:
    if not api_key:
        raise NanoBananaProviderError(
            "Google image generation is not configured", billing_status="unproduced"
        )
    width, height = target_size
    if (
        min(width, height) <= 0
        or max(width, height) > 16384
        or width * height > 32_000_000
    ):
        raise NanoBananaProviderError(
            "Invalid source viewport size", billing_status="unproduced"
        )
    if resolution not in {"1K", "2K", "4K"}:
        raise NanoBananaProviderError(
            "Nano Banana supports 1K, 2K or 4K output", billing_status="unproduced"
        )
    ratio = min(
        RATIOS,
        key=lambda value: abs(
            math.log(
                (int(value.split(":")[0]) / int(value.split(":")[1])) / (width / height)
            )
        ),
    )
    horizontal, vertical = map(int, ratio.split(":"))
    unit = math.ceil(max(width / horizontal, height / vertical))
    canvas_size = (unit * horizontal, unit * vertical)
    offset = ((canvas_size[0] - width) // 2, (canvas_size[1] - height) // 2)
    same_camera_images = same_camera_images or set()
    contents = [
        {
            "type": "text",
            "text": "Make one architectural image using the supplied scene and labelled controls. "
            "Any black padding around a scene/control image is a framing margin: keep its width "
            "and position unchanged. Do not crop, zoom, invent new geometry, or copy control colours.",
        }
    ]
    count = 0
    try:
        for part in parts:
            if "text" in part:
                contents.append({"type": "text", "text": part["text"]})
            elif "inlineData" in part:
                inline = part["inlineData"]
                encoded = inline["data"]
                image = _read_image(encoded)
                if encoded in same_camera_images:
                    if image.size != target_size:
                        raise ValueError(
                            "Same-camera controls must match the source viewport"
                        )
                    padded = Image.new("RGB", canvas_size, "black")
                    padded.paste(image, offset)
                    image = padded
                contents.append(
                    {"type": "image", "mime_type": "image/png", "data": _png(image)}
                )
                count += 1
        if count > 14:
            raise ValueError(
                "Nano Banana accepts at most 14 image attachments; reduce the references"
            )
    except Exception as exc:
        raise NanoBananaProviderError(
            f"Cannot prepare Google image inputs: {exc}", billing_status="unproduced"
        ) from exc
    payload = {
        "model": NANO_BANANA_MODEL,
        "input": contents,
        "store": False,
        "response_format": {
            "type": "image",
            # Live Nano Banana 2.1 rejects PNG output (HTTP 400), despite
            # generic guide examples. Decode JPEG once and preserve those
            # pixels as PNG for the existing gallery/capture contract.
            "mime_type": "image/jpeg",
            "aspect_ratio": ratio,
            "image_size": resolution,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/interactions",
                json=payload,
                headers={"x-goog-api-key": api_key},
            )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout) as exc:
        raise NanoBananaProviderError(
            "Google image connection failed before submission",
            billing_status="unproduced",
        ) from exc
    except httpx.HTTPError as exc:
        raise NanoBananaProviderError(
            "Google image request outcome is unknown; do not submit it again automatically",
            transport_interrupted=True,
        ) from exc
    if response.status_code != 200:
        detail = ""
        try:
            message = response.json().get("error", {}).get("message", "")
            if isinstance(message, str):
                detail = re.sub(r"(?:AIza|AQ\.)[A-Za-z0-9_.-]+", "[redacted]", message.replace(api_key, "[redacted]"))[:500]
        except (ValueError, TypeError, AttributeError):
            pass
        raise NanoBananaProviderError(
            f"Google image generation failed (HTTP {response.status_code})" + (f": {detail}" if detail else ""),
            billing_status=(
                "unproduced"
                if response.status_code in {400, 401, 403, 404, 413, 422, 429}
                else "unknown"
            ),
            provider_status_code=response.status_code,
        )
    try:
        body = response.json()
        image_parts = [
            part
            for step in body.get("steps", [])
            if step.get("type") == "model_output"
            for part in step.get("content", [])
            if part.get("type") == "image" and part.get("data")
        ]
        # SDK-style output_image is accepted for gateways that unwrap that
        # convenience field; the native REST contract returns model-output steps.
        if not image_parts and isinstance(body.get("output_image"), dict):
            image_parts = [body["output_image"]]
        if len(image_parts) != 1 or body.get("status") != "completed":
            raise ValueError("Google did not return one completed image")
    except (ValueError, AttributeError, TypeError) as exc:
        raise NanoBananaProviderError(
            "Google did not return one completed image",
            provider_request_id=(
                body.get("id") if isinstance(locals().get("body"), dict) else None
            ),
        ) from exc
    original = None
    try:
        generated = _read_image(image_parts[0]["data"])
        original = _png(generated)
        if (
            abs((generated.width / generated.height) / (horizontal / vertical) - 1)
            > 0.02
        ):
            raise ValueError("Google output does not match the requested aspect ratio")
        # Undo only the framing padding, then resample to the pipeline's exact
        # viewport size. No image stretch, new crop composition, or paid retry.
        bounds = (
            round(offset[0] / canvas_size[0] * generated.width),
            round(offset[1] / canvas_size[1] * generated.height),
            round((offset[0] + width) / canvas_size[0] * generated.width),
            round((offset[1] + height) / canvas_size[1] * generated.height),
        )
        aligned = generated.crop(bounds).resize(target_size, Image.Resampling.LANCZOS)
        return NanoBananaImage(aligned, original)
    except Exception as exc:
        raise NanoBananaProviderError(
            f"Google produced an unusable image: {exc}",
            billing_status="produced",
            provider_request_id=body.get("id"),
            provider_image_base64=original,
        ) from exc
