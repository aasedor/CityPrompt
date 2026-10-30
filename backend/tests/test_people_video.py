"""Free admission and provider-contract checks for the four-second people pilot."""

import base64
import io
import uuid

from fastapi import HTTPException
from PIL import Image
import pytest
from pydantic import ValidationError

from app.api.v1 import video
from app.services import omni_video
from app.services.video_media import validate_omni_source_media
from tests.test_omni_video import _jpeg_data_url


def _reference(width=64, height=128, format="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (110, 72, 40)).save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


def _preview_request(**updates):
    return video.VideoPilotRequest(
        **{
            "project_id": uuid.uuid4(),
            "guide_frame_base64": _jpeg_data_url(),
            "route_points": [{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
            "control_mode": "preview_video",
            "duration_seconds": 4,
            "preview_video_base64": base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode(),
            "preview_video_mime_type": "video/webm",
            **updates,
        }
    )


def test_four_second_request_validates_96_frame_audit_and_keeps_eight_second_default():
    request = _preview_request(
        capture_profile={
            "encoder": "webcodecs_h264",
            "fixed_timestep": True,
            "frame_count": 96,
            "fps": 24,
            "width": 1280,
            "height": 720,
            "render_width": 1280,
            "render_height": 720,
            "tile_warmup_frame_count": 96,
            "tile_set_held": True,
        }
    )
    video._preflight_values(request)
    assert request.duration_seconds == 4
    assert request.capture_profile.frame_count == 96
    assert _preview_request(duration_seconds=8).duration_seconds == 8
    with pytest.raises(HTTPException, match="frame count"):
        video._preflight_values(request.model_copy(update={"duration_seconds": 8}))
    with pytest.raises(ValidationError):
        _preview_request(duration_seconds=6)


def test_people_follow_admits_only_omni_preview_and_describes_tracking():
    request = _preview_request(camera_motion="people_follow")
    *_, prompt, _reference_image = video._preflight_values(request)
    assert "primary walking subject" in prompt
    assert "camera" in prompt and "timing" in prompt
    assert "architecture" in prompt or "building footprints" in prompt
    for changes in [
        {"provider": "seedance_mini"},
        {"provider": "internal_enhance"},
        {"control_mode": "single_frame"},
        {"control_mode": "multi_keyframe"},
    ]:
        with pytest.raises(HTTPException, match="Omni preview"):
            video._preflight_values(request.model_copy(update={"duration_seconds": 8, **changes}))


def test_people_follow_prompt_does_not_change_other_motion_contracts():
    values = dict(
        route_points=[{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
        scene_brief="An authored city street with three adults.",
        duration_seconds=4,
        control_mode="preview_video",
        provider="omni",
    )
    tracking = omni_video.build_cinematic_prompt(camera_motion="people_follow", **values)
    baseline = omni_video.build_cinematic_prompt(camera_motion="street_walkby", **values)
    assert "primary walking subject" in tracking
    assert "primary walking subject" not in baseline
    assert "camera path, framing, speed and timing exactly" in baseline
    with pytest.raises(ValueError, match="Omni preview"):
        omni_video.build_cinematic_prompt(camera_motion="people_follow", **(values | {"control_mode": "single_frame"}))


@pytest.mark.parametrize(
    "provider,mode",
    [
        ("omni", "single_frame"),
        ("omni", "multi_keyframe"),
        ("seedance_mini", "preview_video"),
        ("internal_enhance", "preview_video"),
    ],
)
@pytest.mark.parametrize("feature", ["duration", "reference"])
def test_people_inputs_require_omni_preview(provider, mode, feature):
    request = _preview_request(
        provider=provider,
        control_mode=mode,
        duration_seconds=4 if feature == "duration" else 8,
        character_reference_base64=_reference() if feature == "reference" else None,
    )
    with pytest.raises(HTTPException, match="Omni preview"):
        video._preflight_values(request)


@pytest.mark.parametrize("format,mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
def test_character_reference_uses_verified_pixels_and_declared_mime(format, mime):
    reference = omni_video.decode_character_reference(_reference(format=format), mime)
    assert (reference.width, reference.height, reference.mime_type) == (64, 128, mime)
    assert reference.data == base64.b64decode(_reference(format=format))


@pytest.mark.parametrize(
    "value,mime,match",
    [
        ("!not base64!", "image/png", "base64"),
        (base64.b64encode(b"not an image").decode(), "image/png", "readable"),
        ("", "image/png", "empty"),
        (_reference(format="JPEG"), "image/png", "MIME"),
        (_reference(format="GIF"), "image/png", "PNG or JPEG"),
        (_reference(width=4097, height=1), "image/png", "4096"),
        (base64.b64encode(b"x" * (8 * 1024 * 1024 + 1)).decode(), "image/png", "8 MiB"),
    ],
    ids=["base64", "unreadable", "empty", "mime", "format", "dimensions", "bytes"],
)
def test_character_reference_rejects_invalid_or_unbounded_media(value, mime, match):
    with pytest.raises(ValueError, match=match):
        omni_video.decode_character_reference(value, mime)


def test_reference_is_an_identity_input_separate_from_source_video_and_first_frame():
    payload = omni_video.build_omni_payload(
        model="gemini-omni-1.1-flash",
        guide_base64=_jpeg_data_url(),
        guide_mime_type="image/jpeg",
        prompt="Keep the authored scene.",
        duration_seconds=4,
        control_mode="preview_video",
        preview_video_base64="c291cmNl",
        preview_video_mime_type="video/mp4",
        character_reference_base64=_reference(),
        character_reference_mime_type="image/png",
    )
    assert [part["type"] for part in payload["input"]] == ["video", "image", "text"]
    assert payload["input"][0]["data"] == "c291cmNl"
    assert payload["input"][1] == {"type": "image", "data": _reference(), "mime_type": "image/png"}
    prompt = payload["input"][-1]["text"]
    assert "[# Sources <VIDEO_0>@Video1]" in prompt
    assert "[# References <IMAGE_REF_0>@Image1]" in prompt
    assert "identity and appearance" in prompt
    assert "not" in prompt and "first frame" in prompt
    assert payload["generation_config"]["video_config"]["task"] == "edit"
    assert "duration" not in payload["response_format"]


def test_four_second_source_requires_96_decoded_frames_and_reports_requested_duration():
    media = {"width": 1280, "height": 720, "fps": 24, "frame_count": 96, "duration_seconds": 4}
    validate_omni_source_media(media, expected_seconds=4)
    with pytest.raises(ValueError, match="four-second"):
        validate_omni_source_media(media | {"frame_count": 192, "duration_seconds": 8}, expected_seconds=4)
