"""fal Wan 2.2 VACE depth helpers: the "Structure Lock" video engine.

The engine receives City Prompt's own depth track as its control video, so
the buildings, parks and streets are data it must follow rather than prose
it may reinterpret. Uploads and downloads never create generations;
``request_vace_depth_video_once`` submits exactly one queue job and the API
layer owns retries and quotas.
"""

from __future__ import annotations

import asyncio
import importlib.util
import shutil
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import httpx

from app.services.omni_video import GuideImage

VACE_DEPTH_ENDPOINT = "fal-ai/wan-22-vace-fun-a14b/depth"
VACE_OUTPUT_COST_PER_SECOND_USD = 0.10
VACE_SEED = 7941
VACE_RESOLUTION = "720p"
VACE_ASPECT_RATIO = "16:9"
VACE_GUIDANCE_SCALE = 5


@dataclass(frozen=True)
class VaceVideoResult:
    request_id: str
    video_bytes: bytes
    mime_type: str
    seed: int | None


class VaceRequestError(RuntimeError):
    """Preserve a submitted fal request id when later queue/download work fails."""

    def __init__(self, message: str, *, request_id: str | None = None):
        super().__init__(message)
        self.request_id = request_id


def estimate_vace_depth_cost(*, output_video_seconds: int) -> float:
    return round(output_video_seconds * VACE_OUTPUT_COST_PER_SECOND_USD, 2)


def vace_runtime_error() -> str | None:
    if importlib.util.find_spec("fal_client") is None:
        return "fal-client is not installed on the Video Render server."
    if shutil.which("ffmpeg") is None:
        return "ffmpeg is required to prepare the depth track for Structure Lock."
    return None


def build_vace_depth_arguments(
    *,
    prompt: str,
    negative_prompt: str,
    control_video_url: str,
    ref_image_urls: Sequence[str] = (),
    first_frame_url: str | None = None,
    frame_count: int = 192,
    fps: int = 24,
    seed: int = VACE_SEED,
) -> dict[str, Any]:
    arguments: dict[str, Any] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "video_url": control_video_url,
        # The control video already is depth; never let fal re-estimate it.
        "preprocess": False,
        "num_frames": frame_count,
        "frames_per_second": fps,
        "match_input_num_frames": True,
        "match_input_frames_per_second": True,
        "resolution": VACE_RESOLUTION,
        "aspect_ratio": VACE_ASPECT_RATIO,
        "guidance_scale": VACE_GUIDANCE_SCALE,
        "seed": seed,
        # Prompt expansion would regrow the look sheet into the prose we removed.
        "enable_prompt_expansion": False,
    }
    if ref_image_urls:
        arguments["ref_image_urls"] = list(ref_image_urls)
    if first_frame_url:
        arguments["first_frame_url"] = first_frame_url
    return arguments


def _output_video_url(payload: Mapping[str, Any]) -> str:
    video = payload.get("video")
    url = video.get("url") if isinstance(video, Mapping) else None
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("Structure Lock returned no HTTPS output video URL.")
    return url


async def request_vace_depth_video_once(
    *,
    api_key: str,
    endpoint: str,
    control_video_mp4: bytes,
    references: Sequence[GuideImage],
    first_frame: GuideImage | None,
    prompt: str,
    negative_prompt: str,
    timeout_seconds: int,
) -> VaceVideoResult:
    """Upload the depth track and references, submit one fal queue job, download its result."""
    from fal_client import AsyncClient

    client = AsyncClient(key=api_key, default_timeout=float(timeout_seconds))
    control_url = await client.upload(control_video_mp4, "video/mp4", "city-prompt-depth-control.mp4")
    ref_image_urls: list[str] = []
    for index, image in enumerate(references, start=1):
        extension = "png" if image.mime_type == "image/png" else "jpg"
        ref_image_urls.append(
            await client.upload(image.data, image.mime_type, f"city-prompt-reference-{index:02d}.{extension}")
        )
    first_frame_url: str | None = None
    if first_frame is not None:
        extension = "png" if first_frame.mime_type == "image/png" else "jpg"
        first_frame_url = await client.upload(
            first_frame.data, first_frame.mime_type, f"city-prompt-first-frame.{extension}"
        )

    arguments = build_vace_depth_arguments(
        prompt=prompt,
        negative_prompt=negative_prompt,
        control_video_url=control_url,
        ref_image_urls=ref_image_urls,
        first_frame_url=first_frame_url,
    )
    request_id: str | None = None
    try:
        handle = await client.submit(endpoint, arguments)
        request_id = str(handle.request_id)
        result = await asyncio.wait_for(handle.get(), timeout=float(timeout_seconds))
    except Exception as exc:
        raise VaceRequestError(
            f"Structure Lock queue request failed: {str(exc)[:600]}",
            request_id=request_id,
        ) from exc

    try:
        output_url = _output_video_url(result)
        transport = httpx.AsyncHTTPTransport(retries=0)
        timeout = httpx.Timeout(120.0, connect=20.0)
        async with httpx.AsyncClient(transport=transport, timeout=timeout) as downloader:
            response = await downloader.get(output_url)
            response.raise_for_status()
        if not response.content:
            raise ValueError("Structure Lock returned an empty video download.")
        video = result.get("video") if isinstance(result, Mapping) else None
        declared_mime = video.get("content_type") if isinstance(video, Mapping) else None
        mime_type = str(declared_mime or response.headers.get("content-type") or "video/mp4").split(";", 1)[0]
        seed_value = result.get("seed") if isinstance(result, Mapping) else None
        return VaceVideoResult(
            request_id=request_id or "",
            video_bytes=response.content,
            mime_type=mime_type,
            seed=int(seed_value) if isinstance(seed_value, (int, float)) else None,
        )
    except VaceRequestError:
        raise
    except Exception as exc:
        raise VaceRequestError(
            f"Structure Lock result download failed: {str(exc)[:600]}",
            request_id=request_id,
        ) from exc
