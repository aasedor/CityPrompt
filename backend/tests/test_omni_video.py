import base64
import io

import pytest
from PIL import Image
from pydantic import ValidationError

from app.api.v1.video import PILOT_MAX_PROVIDER_CALLS, VideoPilotRequest, _count_provider_calls
from app.services.omni_video import (
    build_cinematic_prompt,
    build_omni_payload,
    decode_guide_image,
    find_omni_video_content,
    parse_omni_video,
)


def _jpeg_data_url(width: int = 1280, height: int = 720) -> str:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (42, 54, 66)).save(buffer, format="JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def test_decode_guide_image_inspects_real_format_and_dimensions():
    guide = decode_guide_image(_jpeg_data_url())

    assert guide.mime_type == "image/jpeg"
    assert (guide.width, guide.height) == (1280, 720)
    assert len(guide.data) > 100


def test_decode_guide_image_rejects_tiny_capture():
    with pytest.raises(ValueError, match="at least 640 px"):
        decode_guide_image(_jpeg_data_url(320, 180))


def test_video_request_exposes_motion_not_visual_style_or_reference_images():
    assert "style" not in VideoPilotRequest.model_fields
    assert "reference_images_base64" not in VideoPilotRequest.model_fields

    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id="00000000-0000-0000-0000-000000000001",
            guide_frame_base64=_jpeg_data_url(),
            route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
            camera_motion="orbit_left",
        )

    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id="00000000-0000-0000-0000-000000000001",
            guide_frame_base64=_jpeg_data_url(),
            route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
            style="watercolour",
        )


def test_prompt_locks_scene_and_single_shot_constraints():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.5, "y": 0.85}, {"x": 0.48, "y": 0.55}, {"x": 0.38, "y": 0.2}],
        camera_motion="path_follow",
        scene_brief="Two courtyard buildings frame one rectangular central park.",
        duration_seconds=8,
    )

    assert "single continuous, unbroken 8-second" in prompt
    assert "there is intentionally no route graphic burned into the first frame" in prompt
    assert "Internal prompt identifiers are organizational metadata only" in prompt
    assert "Each building zone is one indivisible persistent object" in prompt
    assert "persistent identity and fixed world coordinates across all 192 frames" in prompt
    assert "Architecture and site geometry are immutable" in prompt
    assert "Do not invent a fountain, pool, monument" in prompt
    assert "remove every car and pedestrian baked into the source map tiles" in prompt
    assert "Keep every street and sidewalk empty for this pilot" in prompt
    assert "Do not preserve, invent, spawn, fade" in prompt
    assert "No facade warping" in prompt


def test_omni_payload_is_one_inline_image_to_video_request():
    data_url = _jpeg_data_url()
    payload = build_omni_payload(
        model="gemini-omni-flash-preview",
        guide_base64=data_url,
        guide_mime_type="image/jpeg",
        prompt="one continuous shot",
        duration_seconds=8,
    )

    assert payload["generation_config"] == {"video_config": {"task": "image_to_video"}}
    assert payload["response_format"] == {
        "type": "video",
        "aspect_ratio": "16:9",
        "duration": "8s",
        "delivery": "inline",
    }
    assert payload["background"] is False
    assert payload["store"] is False
    assert payload["stream"] is False
    assert [item["type"] for item in payload["input"]] == ["image", "text"]
    assert not payload["input"][0]["data"].startswith("data:")


def test_omni_payload_accepts_exactly_one_visual_source():
    payload = build_omni_payload(
        model="gemini-omni-flash-preview",
        guide_base64=_jpeg_data_url(),
        guide_mime_type="image/jpeg",
        prompt="animate the captured scene without redesigning it",
        duration_seconds=8,
    )

    assert payload["generation_config"] == {"video_config": {"task": "image_to_video"}}
    assert [item["type"] for item in payload["input"]] == ["image", "text"]


def test_street_walkby_is_pedestrian_height_and_detail_locked():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.66}, {"x": 0.6, "y": 0.64}],
        camera_motion="street_walkby",
        scene_brief="One authored facade.",
        duration_seconds=8,
    )

    assert "pedestrian-height architectural walk-by" in prompt
    assert "1.7 metres above the sidewalk" in prompt
    assert "Travel no more than 4 metres" in prompt
    assert "every already-visible joint, window frame, railing" in prompt
    assert "source level of detail" in prompt


def test_prompt_locks_courtyard_topology_and_limits_aerial_scale_change():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.52, "y": 0.62}, {"x": 0.5, "y": 0.46}],
        camera_motion="path_follow",
        scene_brief="Two authored buildings frame one authored beer garden.",
        duration_seconds=8,
    )

    assert "COURTYARD TOPOLOGY CHECKSUM" in prompt
    assert "BUILDING SEPARATION CHECKSUM" in prompt
    assert "Never bridge, join, fuse, wrap, or extend one building toward another" in prompt
    assert "exact count, perimeter, length, width, aspect ratio" in prompt
    assert "Never lengthen, widen, shrink, merge, split, fill, or invent a courtyard" in prompt
    assert "one sixteenth of the shorter authored building dimension" in prompt
    assert "increase the apparent building scale by more than two percent" in prompt
    assert "Image1 already contains the final approved design and look" in prompt
    assert "Newly revealed pixels caused by the small camera move" in prompt
    assert "CONTEXT ISOLATION — FINAL OVERRIDE" in prompt
    assert "it is not global art direction" in prompt
    assert "Any new background instance of an authored archetype is a failed result" in prompt
    assert prompt.endswith("preserve Image1 unchanged.")


def test_prompt_makes_omni_an_animator_without_visual_style_instructions():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.52, "y": 0.62}, {"x": 0.5, "y": 0.46}],
        camera_motion="path_follow",
        scene_brief="B1 and B2 frame P1.",
        duration_seconds=8,
    )

    assert "OMNI IS THE ANIMATOR ONLY" in prompt
    assert "do not improve, beautify, materialize, regenerate, relight, recolor, sharpen" in prompt
    assert "Do not apply a photographic or artistic style" in prompt
    assert "newly revealed pixels" in prompt.lower()
    assert "watercolour" not in prompt
    assert "golden-hour" not in prompt
    assert "PBR materials" not in prompt
    assert prompt.endswith("preserve Image1 unchanged.")


@pytest.mark.parametrize(
    "response",
    [
        {"id": "interaction-1", "output_video": {"type": "video", "data": base64.b64encode(b"mp4").decode()}},
        {"id": "interaction-2", "outputs": [{"type": "text", "text": "done"}, {"type": "video", "data": base64.b64encode(b"mp4").decode(), "mime_type": "video/mp4"}]},
    ],
)
def test_parse_omni_video_supports_current_response_shapes(response):
    result = parse_omni_video(response)

    assert result.video_bytes == b"mp4"
    assert result.mime_type == "video/mp4"
    assert result.interaction_id.startswith("interaction-")


def test_find_omni_video_content_supports_nested_uri_delivery():
    output = find_omni_video_content({
        "id": "interaction-uri",
        "status": "completed",
        "steps": [{"type": "model_output", "content": [{
            "type": "video",
            "uri": "https://generativelanguage.googleapis.com/v1beta/files/generated-video",
            "mime_type": "video/mp4",
        }]}],
    })

    assert output.data is None
    assert output.uri and output.uri.endswith("generated-video")
    assert output.mime_type == "video/mp4"


def test_parse_omni_video_rejects_missing_output():
    with pytest.raises(ValueError, match="without video data or a video URI"):
        parse_omni_video({"status": "failed", "outputs": []})


def test_pilot_ledger_counts_every_started_call_regardless_of_outcome():
    attempts = [
        {"status": "reserved"},
        {"status": "complete", "provider_call_started_at": "2026-08-03T00:00:00Z"},
        {"status": "failed", "provider_call_started_at": "2026-08-03T00:01:00Z"},
    ]

    assert PILOT_MAX_PROVIDER_CALLS == 40
    assert _count_provider_calls(attempts) == 2
