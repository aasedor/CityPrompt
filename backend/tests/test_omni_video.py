import base64
import io

import pytest
from PIL import Image

from app.api.v1.video import PILOT_MAX_PROVIDER_CALLS, _count_provider_calls
from app.services.omni_video import (
    GuideImage,
    bind_reference_roles,
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


def test_prompt_locks_scene_and_single_shot_constraints():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.5, "y": 0.85}, {"x": 0.48, "y": 0.55}, {"x": 0.38, "y": 0.2}],
        style="golden_hour",
        camera_motion="forward_descent",
        scene_brief="Two courtyard buildings frame one rectangular central park.",
        duration_seconds=8,
    )

    assert "single continuous, unbroken 8-second" in prompt
    assert "there is intentionally no route graphic burned into the first frame" in prompt
    assert "zone tokens are internal prompt identifiers only" in prompt
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


def test_omni_payload_binds_first_frame_and_archetype_references():
    payload = build_omni_payload(
        model="gemini-omni-flash-preview",
        guide_base64=_jpeg_data_url(),
        guide_mime_type="image/jpeg",
        reference_images=[
            GuideImage(data=base64.b64decode(_jpeg_data_url().split(",", 1)[1]), mime_type="image/jpeg", width=1280, height=720),
            GuideImage(data=base64.b64decode(_jpeg_data_url().split(",", 1)[1]), mime_type="image/jpeg", width=1280, height=720),
        ],
        prompt=bind_reference_roles("preserve the authored scene", 2),
        duration_seconds=8,
    )

    assert payload["generation_config"] == {"video_config": {"task": "reference_to_video"}}
    assert [item["type"] for item in payload["input"]] == ["image", "image", "image", "text"]
    assert "<FIRST_FRAME>@Image1" in payload["input"][-1]["text"]
    assert "<IMAGE_REF_0>@Image2" in payload["input"][-1]["text"]
    assert "<IMAGE_REF_1>@Image3" in payload["input"][-1]["text"]


def test_street_walkby_is_pedestrian_height_and_detail_locked():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.66}, {"x": 0.6, "y": 0.64}],
        style="crisp_daylight",
        camera_motion="street_walkby",
        scene_brief="One authored facade.",
        duration_seconds=8,
    )

    assert "pedestrian-height architectural walk-by" in prompt
    assert "1.7 metres above the sidewalk" in prompt
    assert "Travel no more than 8 metres" in prompt
    assert "stone joints, window frames, balcony railings" in prompt


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

    assert PILOT_MAX_PROVIDER_CALLS == 20
    assert _count_provider_calls(attempts) == 2
