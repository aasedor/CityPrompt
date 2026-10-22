"""Architectural images are edit references, never replacement source frames."""
import pytest
from fastapi import HTTPException

from app.api.v1 import video
from app.services.omni_video import build_omni_payload
from tests.test_people_video import _preview_request, _reference
from tests.test_omni_video import _jpeg_data_url


def test_explicit_skyline_edit_is_not_overridden_by_an_unconditional_size_lock():
    edit = "Bring only the background skyline closer and taller. Keep the photographic foreground unchanged."
    req = _preview_request(omni_reference_mode="architecture_references",
        route_keyframes_base64=[_jpeg_data_url()], custom_prompt=edit, use_custom_prompt_only=True)
    _, _, _, _, prompt, _ = video._preflight_values(req)
    assert edit in prompt
    assert "Video1 controls camera, framing, apparent building sizes" not in prompt
    assert "Follow the explicit scene edits requested above" in prompt
    assert "otherwise retain" in prompt


@pytest.mark.parametrize("count", [1, 2])
def test_preview_admits_explicit_architectural_references_without_changing_camera_mode(count):
    req = _preview_request(omni_reference_mode="architecture_references",
                           route_keyframes_base64=[_jpeg_data_url()] * count)
    _, frames, _, _, prompt, _ = video._preflight_values(req)
    assert len(frames) == count
    assert "<VIDEO_0>@Video1" in prompt
    assert "<IMAGE_REF_0>@Image1" in prompt
    assert "architectural identity" in prompt
    assert "not as first or last frames" in prompt


@pytest.mark.parametrize("count", [0, 3])
def test_architectural_mode_rejects_missing_or_excess_references_before_provider_contact(count):
    req = _preview_request(omni_reference_mode="architecture_references",
                           route_keyframes_base64=[_jpeg_data_url()] * count)
    with pytest.raises(HTTPException, match="one or two"):
        video._preflight_values(req)


@pytest.mark.parametrize("provider,mode", [
    ("seedance_mini", "preview_video"), ("internal_enhance", "preview_video"),
    ("omni", "single_frame"), ("omni", "multi_keyframe"),
])
def test_architectural_mode_is_exclusive_to_omni_video_edits(provider, mode):
    req = _preview_request(provider=provider, control_mode=mode, duration_seconds=8,
        omni_reference_mode="architecture_references", route_keyframes_base64=[_jpeg_data_url()])
    with pytest.raises(HTTPException, match="Architectural references require Omni preview"):
        video._preflight_values(req)


def test_default_video_only_mode_still_rejects_undeclared_reference_images():
    with pytest.raises(HTTPException, match="without route keyframe"):
        video._preflight_values(_preview_request(route_keyframes_base64=[_jpeg_data_url()]))


def test_character_and_architectural_images_keep_separate_roles_and_preflight_matches_payload():
    req = _preview_request(omni_reference_mode="architecture_references",
        route_keyframes_base64=[_jpeg_data_url()], character_reference_base64=_reference())
    _, _, _, _, prompt, _ = video._preflight_values(req)
    payload = build_omni_payload(model="gemini-omni-1.1-flash", guide_base64=req.guide_frame_base64,
        guide_mime_type="image/jpeg", prompt=prompt, duration_seconds=4, control_mode="preview_video",
        preview_video_base64=req.preview_video_base64, preview_video_mime_type="video/webm",
        character_reference_base64=req.character_reference_base64,
        route_keyframes=[(_jpeg_data_url(), "image/jpeg")], omni_reference_mode="architecture_references")
    parts = payload["input"]
    assert [part["type"] for part in parts] == ["video", "image", "image", "text"]
    assert parts[1]["data"] == _reference()
    assert parts[2]["data"] == _jpeg_data_url().split(",", 1)[-1]
    assert parts[-1]["text"] == prompt
    assert "<IMAGE_REF_1>@Image2" in prompt
    assert "Image1 only for" in prompt and "Image2" in prompt
    assert prompt.count("[# Sources") == 1
    assert payload["generation_config"]["video_config"]["task"] == "edit"
