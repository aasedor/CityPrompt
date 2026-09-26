import base64
import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.services.video_controls import (
    MAX_CONTROL_VIDEO_BYTES,
    ControlVideo,
    DepthWindow,
    decode_control_video,
    inspect_control_video,
    normalize_control_video_arguments,
    probe_control_video,
)

cv2 = pytest.importorskip("cv2")

MP4_MAGIC = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 1024


def _data_url(data: bytes, mime: str = "video/mp4") -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def _decode(**overrides) -> ControlVideo:
    base = {
        "role": "depth",
        "video_base64": _data_url(MP4_MAGIC),
        "mime_type": "video/mp4",
        "width": 1280,
        "height": 720,
        "frame_count": 192,
        "fps": 24,
        "encoding": "inverse_depth_8bit",
        "depth_window": DepthWindow(near_meters=50, far_meters=1500),
    }
    return decode_control_video(**{**base, **overrides})


def test_decode_accepts_a_browser_mp4_and_keeps_its_window():
    control = _decode()
    assert control.role == "depth"
    assert control.mime_type == "video/mp4"
    assert control.suffix == ".mp4"
    assert control.depth_window == DepthWindow(near_meters=50, far_meters=1500)


def test_decode_rejects_mime_mismatch_oversize_and_missing_window():
    with pytest.raises(ValueError, match="MP4 content"):
        _decode(video_base64=_data_url(b"\x1aE\xdf\xa3" + b"0" * 2048), mime_type="video/mp4")
    with pytest.raises(ValueError, match="12 MB"):
        _decode(video_base64=_data_url(MP4_MAGIC + b"0" * MAX_CONTROL_VIDEO_BYTES))
    with pytest.raises(ValueError, match="depth window"):
        _decode(depth_window=None)


def _synthetic_video(frames: int, size: tuple[int, int], *, flat: bool) -> bytes:
    width, height = size
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "control.mp4"
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 24, (width, height))
        if not writer.isOpened():
            pytest.skip("OpenCV cannot write mp4v in this environment.")
        for index in range(frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            if not flat:
                frame[:, :] = np.linspace(20, 120, width, dtype=np.uint8)[None, :, None]
                frame[height // 3:, width // 4 + index // 8: width // 2 + index // 8] = 220
            writer.write(frame)
        writer.release()
        return path.read_bytes()


def test_probe_and_inspect_accept_a_structured_track():
    data = _synthetic_video(192, (320, 180), flat=False)
    probe = probe_control_video(data, ".mp4")
    assert (probe.width, probe.height) == (320, 180)
    assert probe.frame_count == 192
    assert probe.std_gray > 2
    control = ControlVideo(
        role="depth", data=data, mime_type="video/mp4", width=320, height=180,
        frame_count=192, fps=24, encoding="inverse_depth_8bit", depth_window=DepthWindow(2, 400),
    )
    inspect_control_video(control, expected_width=320, expected_height=180)
    with pytest.raises(ValueError, match="route preview is 640"):
        inspect_control_video(control, expected_width=640, expected_height=360)


def test_inspect_rejects_short_and_flat_tracks():
    short = _synthetic_video(24, (320, 180), flat=False)
    control = ControlVideo(
        role="depth", data=short, mime_type="video/mp4", width=320, height=180,
        frame_count=192, fps=24, encoding="inverse_depth_8bit", depth_window=DepthWindow(2, 400),
    )
    with pytest.raises(ValueError, match="at least 150"):
        inspect_control_video(control, expected_width=320, expected_height=180)
    flat = _synthetic_video(192, (320, 180), flat=True)
    control = ControlVideo(
        role="depth", data=flat, mime_type="video/mp4", width=320, height=180,
        frame_count=192, fps=24, encoding="inverse_depth_8bit", depth_window=DepthWindow(2, 400),
    )
    with pytest.raises(ValueError, match="flat"):
        inspect_control_video(control, expected_width=320, expected_height=180)


def test_normalize_arguments_keep_luma_only_constant_frame_rate_h264():
    arguments = normalize_control_video_arguments(Path("in.mp4"), Path("out.mp4"), width=1280, height=720)
    joined = " ".join(arguments)
    assert "scale=1280:720:flags=lanczos,format=gray,format=yuv420p" in joined
    assert "-r 24" in joined
    assert "-c:v libx264" in joined
    assert "-crf 12" in joined
    assert "-an" in arguments
    assert arguments[-1] == "out.mp4"
