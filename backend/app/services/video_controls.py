"""Control videos: per-frame geometry tracks that ride beside the route preview.

The browser renders the depth track from the same 192 camera poses as the
beauty preview (8-bit inverse depth, bright = near). The backend validates it,
normalises it for engines that want a fixed size, and lets the fidelity scorer
compare finished frames against the geometry that produced them.
"""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import numpy as np

from app.services.omni_video import decode_video_blob

try:  # OpenCV ships in the deployed image; light test installs may omit it.
    import cv2
except ModuleNotFoundError:  # pragma: no cover - exercised by deployment smoke checks.
    cv2 = None  # type: ignore[assignment]

ControlVideoRole = Literal["depth"]
ControlVideoEncoding = Literal["inverse_depth_8bit"]

MAX_CONTROL_VIDEO_BYTES = 12 * 1024 * 1024
MIN_CONTROL_VIDEO_FRAMES = 150
FFMPEG_TIMEOUT_SECONDS = 180


@dataclass(frozen=True)
class DepthWindow:
    near_meters: float
    far_meters: float


@dataclass(frozen=True)
class ControlVideo:
    role: ControlVideoRole
    data: bytes
    mime_type: str
    width: int
    height: int
    frame_count: int
    fps: int
    encoding: ControlVideoEncoding
    depth_window: DepthWindow | None

    @property
    def suffix(self) -> str:
        return ".webm" if self.mime_type == "video/webm" else ".mp4"


@dataclass(frozen=True)
class ControlVideoProbe:
    frame_count: int
    width: int
    height: int
    mean_gray: float
    std_gray: float


def _require_cv2():
    if cv2 is None:
        raise RuntimeError("Control video inspection requires opencv-python-headless.")
    return cv2


def decode_control_video(
    *,
    role: ControlVideoRole,
    video_base64: str,
    mime_type: str,
    width: int,
    height: int,
    frame_count: int,
    fps: int,
    encoding: ControlVideoEncoding,
    depth_window: DepthWindow | None,
) -> ControlVideo:
    blob = decode_video_blob(
        video_base64,
        mime_type,
        max_bytes=MAX_CONTROL_VIDEO_BYTES,
        label=f"{role} control video",
    )
    if role == "depth" and depth_window is None:
        raise ValueError("The depth control video must declare its depth window.")
    return ControlVideo(
        role=role,
        data=blob.data,
        mime_type=blob.mime_type,
        width=width,
        height=height,
        frame_count=frame_count,
        fps=fps,
        encoding=encoding,
        depth_window=depth_window,
    )


def probe_control_video(data: bytes, suffix: str, *, sample_limit: int = 12) -> ControlVideoProbe:
    """Decode the container once: frame count, size, and a coarse brightness check."""
    cv = _require_cv2()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(data)
        path = Path(handle.name)
    try:
        capture = cv.VideoCapture(str(path))
        if not capture.isOpened():
            raise ValueError("The control video could not be decoded.")
        width = int(capture.get(cv.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv.CAP_PROP_FRAME_HEIGHT) or 0)
        means: list[float] = []
        stds: list[float] = []
        frame_count = 0
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                break
            frame_count += 1
            if len(means) < sample_limit and (frame_count == 1 or frame_count % 16 == 0):
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
                means.append(float(np.mean(gray)))
                stds.append(float(np.std(gray)))
        capture.release()
    finally:
        path.unlink(missing_ok=True)
    if frame_count == 0:
        raise ValueError("The control video contains no decodable frames.")
    return ControlVideoProbe(
        frame_count=frame_count,
        width=width,
        height=height,
        mean_gray=float(np.mean(means)) if means else 0.0,
        std_gray=float(np.mean(stds)) if stds else 0.0,
    )


def inspect_control_video(
    control: ControlVideo,
    *,
    expected_width: int | None,
    expected_height: int | None,
) -> ControlVideoProbe:
    """Reject a track that cannot stand in for the preview's geometry."""
    probe = probe_control_video(control.data, control.suffix)
    if expected_width and expected_height and (probe.width, probe.height) != (expected_width, expected_height):
        raise ValueError(
            f"The {control.role} control video is {probe.width}×{probe.height}; "
            f"the route preview is {expected_width}×{expected_height}."
        )
    if probe.frame_count < MIN_CONTROL_VIDEO_FRAMES:
        raise ValueError(
            f"The {control.role} control video has {probe.frame_count} frames; at least {MIN_CONTROL_VIDEO_FRAMES} are required."
        )
    if control.role == "depth" and probe.std_gray < 2.0:
        raise ValueError("The depth control video is flat; the depth window did not cover the scene.")
    return probe


def control_video_runtime_error() -> str | None:
    if cv2 is None:
        return "opencv-python-headless is required to inspect control videos."
    if shutil.which("ffmpeg") is None:
        return "ffmpeg is required to prepare control videos for video engines."
    return None


async def _run_ffmpeg(arguments: Sequence[str], *, timeout_seconds: int = FFMPEG_TIMEOUT_SECONDS) -> None:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        *arguments,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        process.kill()
        raise RuntimeError("ffmpeg timed out while preparing a control video.") from exc
    if process.returncode != 0:
        detail = (stderr or b"").decode("utf-8", "replace")[-400:]
        raise RuntimeError(f"ffmpeg failed while preparing a control video: {detail}")


def normalize_control_video_arguments(source: Path, output: Path, *, width: int, height: int, fps: int = 24) -> list[str]:
    """Grey, constant-frame-rate H.264 that keeps the depth gradient intact.

    The luma channel carries the whole signal, so chroma subsampling cannot
    damage it; a low CRF keeps the smooth ramps from banding.
    """
    return [
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-an",
        "-vf",
        f"scale={width}:{height}:flags=lanczos,format=gray,format=yuv420p",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "12",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]


async def normalize_control_video(
    control: ControlVideo,
    *,
    width: int,
    height: int,
    fps: int = 24,
) -> bytes:
    """Return an MP4 of the control track scaled to the engine's working size."""
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / f"control{control.suffix}"
        output = Path(directory) / "control-normalized.mp4"
        source.write_bytes(control.data)
        await _run_ffmpeg(normalize_control_video_arguments(source, output, width=width, height=height, fps=fps))
        data = output.read_bytes()
    if len(data) < 1024:
        raise RuntimeError("ffmpeg produced an empty normalized control video.")
    return data


async def first_frame_png(data: bytes, mime_type: str) -> bytes:
    """The first frame of a browser video, as PNG (used as an engine reference)."""
    suffix = ".webm" if mime_type == "video/webm" else ".mp4"
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / f"video{suffix}"
        output = Path(directory) / "first-frame.png"
        source.write_bytes(data)
        await _run_ffmpeg(
            ["-y", "-hide_banner", "-loglevel", "error", "-i", str(source), "-frames:v", "1", "-c:v", "png", str(output)]
        )
        png = output.read_bytes()
    if len(png) < 100:
        raise RuntimeError("ffmpeg produced an empty first frame.")
    return png
