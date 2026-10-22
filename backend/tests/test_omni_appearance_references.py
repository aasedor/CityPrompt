"""A photographic look reference must not replace the source video's layout."""
import pytest
from fastapi import HTTPException

from app.api.v1 import video
from app.services.omni_video import build_omni_payload
from tests.test_people_video import _preview_request, _reference
from tests.test_omni_video import _jpeg_data_url


@pytest.mark.parametrize("count", [1, 2])
@pytest.mark.parametrize("has_character", [False, True])
def test_appearance_reference_roles_survive_preflight_and_transport(count, has_character):
    custom = "Film this exact development with realistic materials and clear daylight."
    req = _preview_request(
        omni_reference_mode="appearance_references",
        route_keyframes_base64=[_jpeg_data_url()] * count,
        character_reference_base64=_reference() if has_character else None,
        custom_prompt=custom,
        use_custom_prompt_only=True,
    )
    _, frames, _, _, prompt, _ = video._preflight_values(req)
    assert len(frames) == count
    assert custom in prompt
    assert "appearance references" in prompt
    assert "materials, lighting" in prompt
    assert "architectural identity references" not in prompt
    assert "not as first or last frames" in prompt
    assert "Video1 controls" in prompt and "scene layout" in prompt
    if has_character:
        assert "Image1 only for the walking subject's identity" in prompt
        assert "Use Image2" in prompt
    else:
        assert "Use Image1" in prompt
    payload = build_omni_payload(
        model="gemini-omni-1.1-flash", guide_base64=req.guide_frame_base64,
        guide_mime_type="image/jpeg", prompt=prompt, duration_seconds=4,
        control_mode="preview_video", preview_video_base64=req.preview_video_base64,
        preview_video_mime_type="video/webm",
        character_reference_base64=req.character_reference_base64,
        route_keyframes=[(_jpeg_data_url(), "image/jpeg")] * count,
        omni_reference_mode="appearance_references",
    )
    parts = payload["input"]
    assert [part["type"] for part in parts] == ["video"] + ["image"] * (count + has_character) + ["text"]
    assert parts[0]["data"] == req.preview_video_base64.split(",", 1)[-1]
    assert parts[-2]["data"] == _jpeg_data_url().split(",", 1)[-1]
    assert parts[-1]["text"] == prompt
    assert prompt.count("[# Sources") == 1
    assert payload["generation_config"]["video_config"]["task"] == "edit"


@pytest.mark.parametrize("count", [0, 3])
def test_appearance_mode_requires_one_or_two_images(count):
    req = _preview_request(omni_reference_mode="appearance_references",
                           route_keyframes_base64=[_jpeg_data_url()] * count)
    with pytest.raises(HTTPException, match="one or two"):
        video._preflight_values(req)


@pytest.mark.parametrize("provider,mode", [
    ("seedance_mini", "preview_video"), ("internal_enhance", "preview_video"),
    ("omni", "single_frame"), ("omni", "multi_keyframe"),
])
def test_appearance_mode_cannot_be_sent_to_another_provider_or_control_mode(provider, mode):
    req = _preview_request(provider=provider, control_mode=mode, duration_seconds=8,
        omni_reference_mode="appearance_references", route_keyframes_base64=[_jpeg_data_url()])
    with pytest.raises(HTTPException, match="Appearance references require Omni preview"):
        video._preflight_values(req)
