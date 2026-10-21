"""Bounded local decoding; never contacts a video provider."""
from __future__ import annotations

import math
from pathlib import Path
import tempfile

import cv2


def inspect_video_media(data: bytes, mime_type: str) -> dict:
    """Measure CFR media from decoded frames, retaining no frame array history."""
    suffix = ".webm" if mime_type.split(";", 1)[0] == "video/webm" else ".mp4"
    with tempfile.TemporaryDirectory(prefix="cityprompt-video-check-") as folder:
        path = Path(folder) / ("video" + suffix)
        path.write_bytes(data)
        capture = cv2.VideoCapture(str(path))
        try:
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            if not capture.isOpened() or not math.isfinite(fps) or not 1 <= fps <= 120:
                raise ValueError("The video could not be decoded with a valid frame rate.")
            declared_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
            count, dimensions = 0, None
            while True:
                ok, frame = capture.read()
                if not ok or frame is None:
                    break
                size = (frame.shape[1], frame.shape[0])
                if dimensions is not None and dimensions != size:
                    raise ValueError("The decoded video changes dimensions mid-clip.")
                dimensions = size
                count += 1
                if count > 1200:
                    raise ValueError("The decoded video exceeds the bounded inspection limit.")
            if count < 2 or (math.isfinite(declared_frames) and declared_frames > count + 1):
                raise ValueError("The video could not be decoded completely.")
            return {"width": dimensions[0], "height": dimensions[1], "fps": round(fps, 4),
                    "frame_count": count, "duration_seconds": round(count / fps, 4),
                    "duration_basis": "decoded_frames/fps"}
        finally:
            capture.release()


def validate_omni_source_media(media: dict, *, expected_seconds: int) -> None:
    """Require the deterministic 24 fps route clip, not just a plausible header."""
    if (media["width"] < 640 or media["height"] < 360
            or abs(media["fps"] - 24) > .1
            or abs(media["duration_seconds"] - expected_seconds) > .1
            or abs(media["frame_count"] - expected_seconds * 24) > 1):
        raise ValueError("The route recording must be a complete eight-second, 24 fps video at least 640×360. Re-capture the free preview.")
