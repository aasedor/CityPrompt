"""fal Seedance helpers for the bounded City Prompt reference-video pilot.

Uploads and media downloads do not create generations. ``request_seedance_video_once``
submits exactly one queue job; retry and quota policy remain the API layer's job.
"""

from __future__ import annotations

import asyncio
import importlib.util
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import httpx

from app.services.omni_video import GuideImage, PreviewVideo

SEEDANCE_MINI_ENDPOINT = "bytedance/seedance-2.0/mini/reference-to-video"
SEEDANCE_OUTPUT_COST_PER_SECOND_USD = 0.1547
SEEDANCE_INPUT_VIDEO_COST_PER_SECOND_USD = 0.0928
SEEDANCE_SEED = 7941


@dataclass(frozen=True)
class SeedanceVideoResult:
    request_id: str
    video_bytes: bytes
    mime_type: str
    seed: int | None


class SeedanceRequestError(RuntimeError):
    """Preserve a submitted fal request id when later queue/download work fails."""

    def __init__(self, message: str, *, request_id: str | None = None):
        super().__init__(message)
        self.request_id = request_id


def estimate_seedance_mini_cost(
    *,
    input_video_seconds: int,
    output_video_seconds: int,
) -> float:
    return round(
        input_video_seconds * SEEDANCE_INPUT_VIDEO_COST_PER_SECOND_USD
        + output_video_seconds * SEEDANCE_OUTPUT_COST_PER_SECOND_USD,
        2,
    )


def seedance_runtime_error(preview_mime_type: str) -> str | None:
    if importlib.util.find_spec("fal_client") is None:
        return "fal-client is not installed on the Video Render server."
    if preview_mime_type == "video/webm" and shutil.which("ffmpeg") is None:
        return "ffmpeg is required to prepare the browser route preview for Seedance."
    return None


def build_seedance_arguments(
    *,
    prompt: str,
    preview_url: str,
    keyframe_urls: Sequence[str],
    duration_seconds: int,
    seed: int = SEEDANCE_SEED,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "video_urls": [preview_url],
        "image_urls": list(keyframe_urls),
        "resolution": "720p",
        "duration": str(duration_seconds),
        "aspect_ratio": "16:9",
        "generate_audio": False,
        "seed": seed,
    }


async def _preview_as_mp4(preview: PreviewVideo) -> bytes:
    if preview.mime_type == "video/mp4":
        return preview.data

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to convert the WebM route preview to MP4.")

    with tempfile.TemporaryDirectory(prefix="city-prompt-seedance-") as temp_dir:
        input_path = Path(temp_dir) / "route-preview.webm"
        output_path = Path(temp_dir) / "route-preview.mp4"
        input_path.write_bytes(preview.data)
        process = await asyncio.create_subprocess_exec(
            ffmpeg,
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-movflags",
            "+faststart",
            str(output_path),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        except TimeoutError:
            process.kill()
            await process.communicate()
            raise RuntimeError("The route-preview MP4 conversion timed out.") from None
        if process.returncode != 0 or not output_path.exists():
            detail = stderr.decode("utf-8", errors="replace")[-500:]
            raise RuntimeError(f"The route-preview MP4 conversion failed: {detail}")
        converted = output_path.read_bytes()
        if not converted:
            raise RuntimeError("The route-preview MP4 conversion returned an empty file.")
        return converted


def _output_video_url(payload: Mapping[str, Any]) -> str:
    video = payload.get("video")
    url = video.get("url") if isinstance(video, Mapping) else None
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("Seedance returned no HTTPS output video URL.")
    return url


async def request_seedance_video_once(
    *,
    api_key: str,
    preview: PreviewVideo,
    keyframes: Sequence[GuideImage],
    prompt: str,
    duration_seconds: int,
    timeout_seconds: int,
) -> SeedanceVideoResult:
    """Upload controls, submit one fal queue job, then download its result."""
    from fal_client import AsyncClient

    client = AsyncClient(key=api_key, default_timeout=float(timeout_seconds))
    preview_mp4 = await _preview_as_mp4(preview)
    preview_url = await client.upload(preview_mp4, "video/mp4", "city-prompt-route-preview.mp4")
    keyframe_urls: list[str] = []
    for index, frame in enumerate(keyframes, start=1):
        extension = "png" if frame.mime_type == "image/png" else "jpg"
        keyframe_urls.append(
            await client.upload(
                frame.data,
                frame.mime_type,
                f"city-prompt-route-keyframe-{index:02d}.{extension}",
            )
        )

    arguments = build_seedance_arguments(
        prompt=prompt,
        preview_url=preview_url,
        keyframe_urls=keyframe_urls,
        duration_seconds=duration_seconds,
    )
    request_id: str | None = None
    try:
        handle = await client.submit(SEEDANCE_MINI_ENDPOINT, arguments)
        request_id = str(handle.request_id)
        result = await asyncio.wait_for(handle.get(), timeout=float(timeout_seconds))
    except Exception as exc:
        raise SeedanceRequestError(
            f"Seedance queue request failed: {str(exc)[:600]}",
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
            raise ValueError("Seedance returned an empty video download.")
        video = result.get("video") if isinstance(result, Mapping) else None
        declared_mime = video.get("content_type") if isinstance(video, Mapping) else None
        mime_type = str(declared_mime or response.headers.get("content-type") or "video/mp4").split(";", 1)[0]
        seed_value = result.get("seed") if isinstance(result, Mapping) else None
        return SeedanceVideoResult(
            request_id=request_id or "",
            video_bytes=response.content,
            mime_type=mime_type,
            seed=int(seed_value) if isinstance(seed_value, int) else None,
        )
    except Exception as exc:
        raise SeedanceRequestError(
            f"Seedance output download failed: {str(exc)[:600]}",
            request_id=request_id,
        ) from exc
