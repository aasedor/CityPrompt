import asyncio
import shutil
import subprocess

import pytest

from app.services.internal_video import (
    INTERNAL_VIDEO_MODEL,
    _restoration_filter,
    enhance_video_locally,
    internal_video_dimensions,
    internal_video_runtime,
    internal_video_runtime_error,
)
from app.services.omni_video import PreviewVideo


def test_internal_runtime_prefers_configured_upscaler(monkeypatch, tmp_path):
    executable = tmp_path / "realesrgan-ncnn-vulkan.exe"
    executable.write_bytes(b"placeholder")
    monkeypatch.setenv("INTERNAL_VIDEO_UPSCALER_PATH", str(executable))

    runtime = internal_video_runtime()

    assert runtime.upscaler_path == executable.resolve()
    assert runtime.engine == "realesrgan_ncnn_vulkan"
    assert "realesrgan" in runtime.model


def test_gpu_detail_reports_when_the_optional_model_is_missing(monkeypatch):
    monkeypatch.delenv("INTERNAL_VIDEO_UPSCALER_PATH", raising=False)
    monkeypatch.setattr("app.services.internal_video._configured_upscaler", lambda: None)
    monkeypatch.setattr(
        "app.services.internal_video.shutil.which",
        lambda executable: "ffmpeg" if executable == "ffmpeg" else None,
    )

    assert "not installed" in (internal_video_runtime_error(require_upscaler=True) or "")


def test_internal_filter_is_conservative_and_fixed_resolution():
    filter_graph = _restoration_filter(model_upscaled=False, width=1280, height=720)

    assert "setpts=N/(24*TB)" in filter_graph
    assert "fps=24" in filter_graph
    assert "scale=1280:720" in filter_graph
    assert "hqdn3d=0.65" in filter_graph
    assert "unsharp=5:5:0.32" in filter_graph


def test_high_quality_internal_output_preserves_1080p_delivery():
    assert internal_video_dimensions("draft") == (1280, 720)
    assert internal_video_dimensions("high") == (1920, 1080)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is unavailable")
def test_internal_restoration_produces_a_playable_mp4(tmp_path):
    source = tmp_path / "source.webm"
    subprocess.run(
        [
            shutil.which("ffmpeg") or "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=12",
            "-t",
            "1",
            "-c:v",
            "libvpx-vp9",
            str(source),
        ],
        check=True,
    )

    result = asyncio.run(
        enhance_video_locally(
            preview=PreviewVideo(data=source.read_bytes(), mime_type="video/webm"),
            duration_seconds=1,
            allow_upscaler=False,
        )
    )

    assert result.video_bytes[4:8] == b"ftyp"
    assert result.mime_type == "video/mp4"
    assert result.model == INTERNAL_VIDEO_MODEL
    assert result.engine == "ffmpeg_restoration"
    assert result.frame_count == 24
