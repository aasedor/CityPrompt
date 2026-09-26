"""xAI Grok Imagine helpers for the bounded City Prompt video pilot.

``request_grok_video_once`` creates exactly one xAI video job, polls it, and
downloads the result immediately because xAI's default output URL is
ephemeral. Retry and quota policy remain the API layer's job.

The deterministic City Prompt route preview is the authority for the camera,
buildings, parks, streets, plots and Google context. Preview-video mode edits
that route video with ``grok-imagine-video`` (which keeps its camera, length
and frame, capped at 720p); image modes animate route images with
``grok-imagine-video-1.5``. Grok may change light, weather, grade and small
living motion only.

Docs: https://docs.x.ai/developers/model-capabilities/video/editing and
https://docs.x.ai/developers/model-capabilities/video/generation
"""

from __future__ import annotations

import asyncio
import base64
import logging
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import httpx

from app.services.omni_video import GuideImage, PreviewVideo
from app.services.seedance_video import _preview_as_mp4
from app.services.video_prompts import LookSheet, build_grok_look_prompt

logger = logging.getLogger(__name__)

XAI_API_BASE_URL = "https://api.x.ai/v1"
# Published per-second output prices (docs.x.ai/developers/pricing). The API
# also reports each job's actual cost, which the attempt records.
GROK_VIDEO_COST_PER_SECOND_USD = {
    "grok-imagine-video-1.5": 0.08,
    "grok-imagine-video": 0.05,
}
GROK_VIDEO_RESOLUTION = "720p"
GROK_VIDEO_ASPECT_RATIO = "16:9"
GROK_POLL_INTERVAL_SECONDS = 5.0
# grok-imagine-video-1.5 pins at most four keyframes after the start frame
# (five images in total), at 1/3-second steps strictly inside the clip.
GROK_MAX_KEYFRAMES = 4
_KEYFRAME_STEPS_PER_SECOND = 3
# Synchronous rejections of the route video itself (no job is created).
_INPUT_REJECTION_STATUSES = {400, 413, 415, 422}

GrokReferenceMode = Literal["preview_video_edit", "guide_frame_fallback", "route_keyframes", "guide_frame"]

# Image modes have no camera in their input, so the shot brief spells it out.
# Preview-video mode edits the route video and uses the shared look sheet.
GROK_LOCK = (
    "Animate this exact City Prompt route. Keep every building footprint, height, roof, facade opening, "
    "park kit, street, sidewalk, plot boundary, and background context in the same place and shape. "
    "Do not add buildings, roads, parks, cars that change the plan, or landmarks. Do not orbit, zoom, or "
    "change altitude except as the source camera already moves. 8 seconds, 16:9, 24fps. Silent."
)
GROK_CAMERA = {
    "path_follow": "Follow the source aerial truck exactly: slow constant-altitude move, gentle bank only on curves.",
    "street_walkby": "Follow the source pedestrian walk-by exactly: 1.7m lens height, level verticals, walking pace.",
    "detail_flythrough": "Follow the source 6m corridor fly-through exactly: level verticals, no wall clipping.",
}


@dataclass(frozen=True)
class GrokVideoResult:
    request_id: str
    video_bytes: bytes
    mime_type: str
    provider_cost_usd: float | None
    model: str
    reference_mode: GrokReferenceMode


class GrokRequestError(RuntimeError):
    """Preserve a submitted xAI request id when polling or download fails."""

    def __init__(self, message: str, *, request_id: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.request_id = request_id
        self.status_code = status_code


def build_grok_video_prompt(*, camera_motion: str, control_mode: str, sheet: LookSheet) -> str:
    """Preview-video edits use the shared look sheet; image modes add the lock and camera."""
    if control_mode == "preview_video":
        return build_grok_look_prompt(sheet)
    look = sheet.look[0].upper() + sheet.look[1:]
    parts = [GROK_LOCK, GROK_CAMERA[camera_motion], f"{look}. {sheet.entourage}"]
    if sheet.note_sentence:
        parts.append(f"{sheet.note_sentence} (This never changes the plan.)")
    return "\n".join(parts)


def grok_model_for(control_mode: str, *, generation_model: str, edit_model: str) -> str:
    return edit_model if control_mode == "preview_video" else generation_model


def estimate_grok_video_cost(*, model: str, output_video_seconds: int) -> float:
    per_second = GROK_VIDEO_COST_PER_SECOND_USD.get(model, GROK_VIDEO_COST_PER_SECOND_USD["grok-imagine-video-1.5"])
    return round(per_second * output_video_seconds, 2)


def grok_runtime_error(control_mode: str, preview_mime_type: str | None) -> str | None:
    if control_mode == "preview_video" and preview_mime_type == "video/webm" and shutil.which("ffmpeg") is None:
        return "ffmpeg is required to prepare the browser route preview for Grok Video."
    return None


def _data_url(data: bytes, mime_type: str) -> str:
    return f"data:{mime_type};base64,{base64.b64encode(data).decode('ascii')}"


def keyframe_schedule(frame_count: int, duration_seconds: int) -> list[tuple[int, float]]:
    """Pin chronological route frames after the start frame at 1/3-second steps.

    Route keyframes are sampled at equal intervals of the route, so frame ``i``
    of ``n`` belongs at ``i / (n - 1)`` of the clip. The start frame is the
    literal first frame; the rest are pinned strictly inside the clip, keeping
    the final route frame when more than four are supplied.
    """
    if frame_count < 2:
        return []
    later = list(range(1, frame_count))
    if len(later) > GROK_MAX_KEYFRAMES:
        step = (len(later) - 1) / (GROK_MAX_KEYFRAMES - 1)
        later = [later[round(index * step)] for index in range(GROK_MAX_KEYFRAMES)]
    last_step = duration_seconds * _KEYFRAME_STEPS_PER_SECOND - 1
    schedule: list[tuple[int, float]] = []
    previous_step = 0
    for index in later:
        step = round(index / (frame_count - 1) * duration_seconds * _KEYFRAME_STEPS_PER_SECOND)
        step = min(max(step, previous_step + 1), last_step)
        if step <= previous_step:
            continue
        schedule.append((index, step / _KEYFRAME_STEPS_PER_SECOND))
        previous_step = step
    return schedule


def build_grok_generation_payload(
    *,
    model: str,
    prompt: str,
    guide: GuideImage,
    route_keyframes: Sequence[GuideImage],
    duration_seconds: int,
) -> dict[str, Any]:
    """Image-to-video from the first route image, with later route images pinned."""
    frames = list(route_keyframes) or [guide]
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "image": {"url": _data_url(frames[0].data, frames[0].mime_type)},
        "duration": duration_seconds,
        "aspect_ratio": GROK_VIDEO_ASPECT_RATIO,
        "resolution": GROK_VIDEO_RESOLUTION,
        "generate_audio": False,
    }
    schedule = keyframe_schedule(len(frames), duration_seconds)
    if schedule:
        payload["keyframes"] = [
            {"image": {"url": _data_url(frames[index].data, frames[index].mime_type)}, "timestamp_s": timestamp}
            for index, timestamp in schedule
        ]
    return payload


def build_grok_edit_payload(*, model: str, prompt: str, preview_mp4: bytes) -> dict[str, Any]:
    """Edit the route video; xAI keeps its duration and frame, capped at 720p."""
    return {"model": model, "prompt": prompt, "video": {"url": _data_url(preview_mp4, "video/mp4")}}


def _error_detail(response: httpx.Response) -> str:
    try:
        body: Any = response.json()
    except ValueError:
        return response.text[:400]
    if isinstance(body, Mapping):
        error = body.get("error")
        if isinstance(error, Mapping):
            return f"{error.get('code', '')}: {error.get('message', '')}".strip(": ")
        if isinstance(error, str):
            return error
        if "detail" in body:
            return str(body["detail"])[:400]
    return str(body)[:400]


def _finished_video(result: Mapping[str, Any]) -> tuple[str, float | None]:
    video = result.get("video")
    if not isinstance(video, Mapping):
        raise ValueError("xAI returned no video object.")
    url = video.get("url")
    if video.get("respect_moderation") is False or not url:
        raise ValueError("xAI withheld the video after moderation review.")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("xAI returned no HTTPS output video URL.")
    usage = result.get("usage")
    ticks = usage.get("cost_in_usd_ticks") if isinstance(usage, Mapping) else None
    # xAI bills in ticks: 10^10 ticks per US dollar.
    cost = round(ticks / 10_000_000_000, 4) if isinstance(ticks, (int, float)) else None
    return url, cost


async def _silent(video_bytes: bytes) -> bytes:
    """Drop any audio track; the product output is silent."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return video_bytes
    with tempfile.TemporaryDirectory(prefix="city-prompt-grok-") as temp_dir:
        source, output = Path(temp_dir) / "grok.mp4", Path(temp_dir) / "silent.mp4"
        source.write_bytes(video_bytes)
        process = await asyncio.create_subprocess_exec(
            ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(source),
            "-an", "-c:v", "copy", "-movflags", "+faststart", str(output),
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(process.communicate(), timeout=60)
        except TimeoutError:
            process.kill()
            await process.communicate()
            return video_bytes
        if process.returncode != 0 or not output.exists() or not output.stat().st_size:
            logger.warning("Could not strip audio from a Grok video; keeping the provider file.")
            return video_bytes
        return output.read_bytes()


async def _submit(client: httpx.AsyncClient, path: str, payload: Mapping[str, Any]) -> str:
    try:
        submitted = await client.post(path, json=dict(payload))
    except httpx.HTTPError as exc:
        raise GrokRequestError(f"xAI video submission failed: {str(exc)[:400]}") from exc
    if submitted.status_code >= 400:
        raise GrokRequestError(
            f"xAI rejected the video request (HTTP {submitted.status_code}): {_error_detail(submitted)}",
            status_code=submitted.status_code,
        )
    request_id = str((submitted.json() or {}).get("request_id") or "")
    if not request_id:
        raise GrokRequestError("xAI accepted the request but returned no request_id.")
    return request_id


async def _await_video(
    client: httpx.AsyncClient,
    request_id: str,
    *,
    timeout_seconds: int,
    poll_interval_seconds: float,
) -> Mapping[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            polled = await client.get(f"/videos/{request_id}")
        except httpx.HTTPError as exc:
            raise GrokRequestError(f"xAI video polling failed: {str(exc)[:400]}", request_id=request_id) from exc
        if polled.status_code >= 400:
            raise GrokRequestError(
                f"xAI video polling failed (HTTP {polled.status_code}): {_error_detail(polled)}",
                request_id=request_id,
            )
        # HTTP 202 means still in progress and may carry no body.
        try:
            result = polled.json() if polled.content else {}
        except ValueError:
            result = {}
        state = result.get("status") if isinstance(result, Mapping) else None
        if state == "done":
            return result
        if state in {"failed", "expired"}:
            detail = _error_detail(polled) if state == "failed" else "the request expired before completion"
            raise GrokRequestError(f"xAI video generation {state}: {detail}", request_id=request_id)
        if time.monotonic() >= deadline:
            raise GrokRequestError(
                f"xAI video generation did not finish within {timeout_seconds} seconds.",
                request_id=request_id,
            )
        await asyncio.sleep(poll_interval_seconds)


async def request_grok_video_once(
    *,
    api_key: str,
    prompt: str,
    control_mode: str,
    guide: GuideImage,
    route_keyframes: Sequence[GuideImage],
    preview: PreviewVideo | None,
    duration_seconds: int,
    generation_model: str,
    edit_model: str,
    timeout_seconds: int,
    poll_interval_seconds: float = GROK_POLL_INTERVAL_SECONDS,
    transport: httpx.AsyncBaseTransport | None = None,
) -> GrokVideoResult:
    """Create one xAI video job, poll it to completion, then download the MP4.

    Preview-video mode edits the route video. If xAI rejects that video before
    creating a job, the same prompt animates the guide frame instead, so at
    most one job (and one charge) is created per request.
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    timeout = httpx.Timeout(120.0, connect=20.0)
    async with httpx.AsyncClient(
        base_url=XAI_API_BASE_URL, headers=headers, timeout=timeout,
        transport=transport or httpx.AsyncHTTPTransport(retries=0),
    ) as client:
        generation = {
            "model": generation_model, "prompt": prompt, "guide": guide, "duration_seconds": duration_seconds,
        }
        reference_mode: GrokReferenceMode
        if control_mode == "preview_video":
            if preview is None:
                raise GrokRequestError("Grok preview-video mode requires the deterministic route preview.")
            try:
                preview_mp4 = await _preview_as_mp4(preview)
                model, reference_mode = edit_model, "preview_video_edit"
                request_id = await _submit(client, "/videos/edits", build_grok_edit_payload(
                    model=edit_model, prompt=prompt, preview_mp4=preview_mp4))
            except GrokRequestError as exc:
                if exc.status_code not in _INPUT_REJECTION_STATUSES:
                    raise
                logger.warning("xAI rejected the route preview (HTTP %s); animating the guide frame", exc.status_code)
                model, reference_mode = generation_model, "guide_frame_fallback"
                request_id = await _submit(client, "/videos/generations", build_grok_generation_payload(
                    route_keyframes=[], **generation))
        else:
            frames = list(route_keyframes) if control_mode == "multi_keyframe" else []
            model = generation_model
            reference_mode = "route_keyframes" if frames else "guide_frame"
            request_id = await _submit(client, "/videos/generations", build_grok_generation_payload(
                route_keyframes=frames, **generation))

        result = await _await_video(
            client, request_id, timeout_seconds=timeout_seconds, poll_interval_seconds=poll_interval_seconds,
        )
        try:
            output_url, provider_cost = _finished_video(result)
            # The output host is not the API host and needs no xAI credentials.
            async with httpx.AsyncClient(timeout=timeout,
                                         transport=transport or httpx.AsyncHTTPTransport(retries=0)) as downloader:
                response = await downloader.get(output_url)
                response.raise_for_status()
            if not response.content:
                raise ValueError("xAI returned an empty video download.")
        except Exception as exc:
            raise GrokRequestError(f"xAI output download failed: {str(exc)[:400]}", request_id=request_id) from exc
        return GrokVideoResult(
            request_id=request_id,
            video_bytes=await _silent(response.content),
            mime_type="video/mp4",
            provider_cost_usd=provider_cost,
            model=model,
            reference_mode=reference_mode,
        )
