"""Free, real-codec media checks before spending on video generation."""

import cv2
import numpy as np
import pytest

from app.services.video_media import inspect_video_media, validate_omni_source_media


@pytest.mark.parametrize("seconds,frames", [(4, 96), (8, 192)])
def test_media_inspection_measures_the_decoded_file(tmp_path, seconds, frames):
    path = tmp_path / "source.mp4"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 24, (640, 360))
    assert writer.isOpened()
    try:
        for index in range(frames):
            writer.write(np.full((360, 640, 3), index, dtype=np.uint8))
    finally:
        writer.release()
    media = inspect_video_media(path.read_bytes(), "video/mp4")
    assert media == {
        "width": 640,
        "height": 360,
        "fps": 24.0,
        "frame_count": frames,
        "duration_seconds": float(seconds),
        "duration_basis": "decoded_frames/fps",
    }
    validate_omni_source_media(media, expected_seconds=seconds)


def test_magic_bytes_alone_do_not_establish_a_readable_video():
    with pytest.raises(ValueError, match="decoded"):
        inspect_video_media(b"\x00\x00\x00\x20ftyp" + b"0" * 2048, "video/mp4")


@pytest.mark.parametrize(
    "overrides",
    [
        {"duration_seconds": 3},
        {"fps": 12},
        {"width": 320},
        {"frame_count": 96},
    ],
)
def test_incompatible_source_is_rejected_before_a_paid_call(overrides):
    media = {"width": 1280, "height": 720, "fps": 24.0, "frame_count": 192, "duration_seconds": 8.0}
    with pytest.raises(ValueError, match="route recording"):
        validate_omni_source_media(media | overrides, expected_seconds=8)
