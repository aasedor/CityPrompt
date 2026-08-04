"""Self-hosted, source-locked cleanup for City Prompt route videos.

The internal pipeline deliberately starts as restoration rather than scene
generation.  It receives the deterministic Direct 3D route recording, which
already contains the approved GLB skins and open-space kits, and strengthens
only signal that is present in those pixels.  An optional Real-ESRGAN NCNN
binary can add a model-backed super-resolution pass; the deterministic ffmpeg
restoration remains the portable fallback.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from app.services.omni_video import PreviewVideo

INTERNAL_VIDEO_MODEL = "city-prompt-internal-restoration-v1"
INTERNAL_VIDEO_FPS = 24
INTERNAL_VIDEO_WIDTH = 1280
INTERNAL_VIDEO_HEIGHT = 720
INTERNAL_HIGH_VIDEO_WIDTH = 1920
INTERNAL_HIGH_VIDEO_HEIGHT = 1080
INTERNAL_UPSCALER_MODEL = "realesrgan-x4plus"


@dataclass(frozen=True)
class InternalVideoRuntime:
    model: str
    engine: str
    upscaler_path: Path | None


@dataclass(frozen=True)
class InternalVideoResult:
    video_bytes: bytes
    mime_type: str
    model: str
    engine: str
    frame_count: int
    processing_seconds: float
    fallback_reason: str | None = None


def build_internal_video_contract(scene_brief: str) -> str:
    """Describe the deliberately narrow authority of the local cleanup pass."""
    return (
        "SELF-HOSTED CITY PROMPT RESTORATION. The deterministic route preview is the complete "
        "camera, geometry, context, material, and timing authority. Its pixels already contain the "
        "approved render-locked GLB skins and open-space kits. Preserve every footprint, courtyard, "
        "roof, opening, tree, path, Google context building, and frame timestamp exactly. The only "
        "authorized changes are conservative denoising, antialiasing, compression cleanup, tonal "
        "stabilization, and recovery of detail already present in the source. Do not synthesize, "
        "replace, extend, or redesign any object.\n\n"
        f"{scene_brief.strip()}"
    )


def _configured_upscaler() -> Path | None:
    configured = os.getenv("INTERNAL_VIDEO_UPSCALER_PATH", "").strip()
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate.resolve()
    discovered = shutil.which("realesrgan-ncnn-vulkan") or shutil.which("realesrgan-ncnn-vulkan.exe")
    return Path(discovered).resolve() if discovered else None


def internal_video_runtime() -> InternalVideoRuntime:
    upscaler = _configured_upscaler()
    if upscaler:
        return InternalVideoRuntime(
            model=f"{INTERNAL_VIDEO_MODEL}+{INTERNAL_UPSCALER_MODEL}",
            engine="realesrgan_ncnn_vulkan",
            upscaler_path=upscaler,
        )
    return InternalVideoRuntime(
        model=INTERNAL_VIDEO_MODEL,
        engine="ffmpeg_restoration",
        upscaler_path=None,
    )


def internal_video_runtime_error(*, require_upscaler: bool = False) -> str | None:
    if shutil.which("ffmpeg") is None:
        return "ffmpeg is required for the self-hosted video cleanup pipeline."
    if require_upscaler and _configured_upscaler() is None:
        return "The optional GPU Detail model is not installed on this render worker."
    return None


def internal_video_dimensions(render_quality: str) -> tuple[int, int]:
    if render_quality == "high":
        return INTERNAL_HIGH_VIDEO_WIDTH, INTERNAL_HIGH_VIDEO_HEIGHT
    return INTERNAL_VIDEO_WIDTH, INTERNAL_VIDEO_HEIGHT


def _restoration_filter(*, model_upscaled: bool, width: int, height: int) -> str:
    filters: list[str] = []
    if not model_upscaled:
        # Browser fallback recorders timestamp frames from wall-clock time.
        # Rebuild presentation timestamps from decoded frame order so the
        # indexed City Prompt camera path remains a true 24 fps sequence.
        filters.extend(
            [
                f"setpts=N/({INTERNAL_VIDEO_FPS}*TB)",
                f"fps={INTERNAL_VIDEO_FPS}",
            ]
        )
    filters.extend(
        [
            f"scale={width}:{height}:flags=lanczos",
            # Conservative temporal/spatial cleanup. Values are intentionally
            # low so facade joints, railings, trees, and tile texture survive.
            "hqdn3d=0.65:0.65:2.4:2.4",
            "eq=contrast=1.025:saturation=1.015:gamma=1.005",
            "unsharp=5:5:0.32:3:3:0.08",
        ]
    )
    return ",".join(filters)


async def _run_process(
    *args: str,
    timeout_seconds: int,
    cwd: Path | None = None,
) -> None:
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except TimeoutError:
        process.kill()
        await process.communicate()
        raise RuntimeError("The internal video process timed out.") from None
    if process.returncode != 0:
        detail = stderr.decode("utf-8", errors="replace")[-700:]
        raise RuntimeError(f"The internal video process failed: {detail}")


async def _encode_restoration(
    *,
    ffmpeg: str,
    input_path: Path,
    output_path: Path,
    duration_seconds: int,
    width: int,
    height: int,
) -> None:
    await _run_process(
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-t",
        str(duration_seconds),
        "-an",
        "-vf",
        _restoration_filter(model_upscaled=False, width=width, height=height),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
        timeout_seconds=180,
    )


async def _encode_model_restoration(
    *,
    ffmpeg: str,
    upscaler: Path,
    input_path: Path,
    output_path: Path,
    duration_seconds: int,
    temp_root: Path,
    width: int,
    height: int,
) -> None:
    input_frames = temp_root / "source-frames"
    enhanced_frames = temp_root / "enhanced-frames"
    input_frames.mkdir()
    enhanced_frames.mkdir()
    await _run_process(
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-t",
        str(duration_seconds),
        "-vf",
        (f"fps={INTERNAL_VIDEO_FPS}," f"scale={width}:{height}:flags=lanczos"),
        str(input_frames / "%06d.png"),
        timeout_seconds=180,
    )

    model_dir = upscaler.parent / "models"
    upscaler_args = [
        str(upscaler),
        "-i",
        str(input_frames),
        "-o",
        str(enhanced_frames),
        "-n",
        INTERNAL_UPSCALER_MODEL,
        "-s",
        "2",
        "-t",
        "256",
        "-j",
        "1:2:2",
        "-f",
        "png",
    ]
    if model_dir.is_dir():
        upscaler_args.extend(["-m", str(model_dir)])
    await _run_process(*upscaler_args, timeout_seconds=1200, cwd=upscaler.parent)

    if not any(enhanced_frames.glob("*.png")):
        raise RuntimeError("The local upscaler returned no enhanced frames.")
    await _run_process(
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(INTERNAL_VIDEO_FPS),
        "-i",
        str(enhanced_frames / "%06d.png"),
        "-t",
        str(duration_seconds),
        "-an",
        "-vf",
        _restoration_filter(model_upscaled=True, width=width, height=height),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
        timeout_seconds=240,
    )


async def enhance_video_locally(
    *,
    preview: PreviewVideo,
    duration_seconds: int,
    allow_upscaler: bool = True,
    render_quality: str = "draft",
) -> InternalVideoResult:
    """Restore one deterministic route video without contacting an API."""
    runtime_error = internal_video_runtime_error()
    if runtime_error:
        raise RuntimeError(runtime_error)
    if not preview.data:
        raise ValueError("The deterministic route preview is empty.")

    runtime = internal_video_runtime()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:  # Covered by the runtime check; retained for type narrowing.
        raise RuntimeError("ffmpeg is required for internal video cleanup.")
    started_at = perf_counter()
    fallback_reason: str | None = None
    used_model = bool(allow_upscaler and runtime.upscaler_path)
    width, height = internal_video_dimensions(render_quality)

    with tempfile.TemporaryDirectory(prefix="city-prompt-internal-video-") as temp_dir:
        temp_root = Path(temp_dir)
        suffix = ".mp4" if preview.mime_type == "video/mp4" else ".webm"
        input_path = temp_root / f"route-preview{suffix}"
        output_path = temp_root / "internal-enhance.mp4"
        input_path.write_bytes(preview.data)

        if used_model and runtime.upscaler_path:
            try:
                await _encode_model_restoration(
                    ffmpeg=ffmpeg,
                    upscaler=runtime.upscaler_path,
                    input_path=input_path,
                    output_path=output_path,
                    duration_seconds=duration_seconds,
                    temp_root=temp_root,
                    width=width,
                    height=height,
                )
            except Exception as exc:
                fallback_reason = str(exc)[:500]
                used_model = False
                await _encode_restoration(
                    ffmpeg=ffmpeg,
                    input_path=input_path,
                    output_path=output_path,
                    duration_seconds=duration_seconds,
                    width=width,
                    height=height,
                )
        else:
            await _encode_restoration(
                ffmpeg=ffmpeg,
                input_path=input_path,
                output_path=output_path,
                duration_seconds=duration_seconds,
                width=width,
                height=height,
            )

        video_bytes = output_path.read_bytes() if output_path.exists() else b""
        if len(video_bytes) < 1024:
            raise RuntimeError("The internal video cleanup returned an empty output.")

    engine = "realesrgan_ncnn_vulkan" if used_model else "ffmpeg_restoration"
    model = f"{INTERNAL_VIDEO_MODEL}+{INTERNAL_UPSCALER_MODEL}" if used_model else INTERNAL_VIDEO_MODEL
    return InternalVideoResult(
        video_bytes=video_bytes,
        mime_type="video/mp4",
        model=model,
        engine=engine,
        frame_count=duration_seconds * INTERNAL_VIDEO_FPS,
        processing_seconds=round(perf_counter() - started_at, 2),
        fallback_reason=fallback_reason,
    )
