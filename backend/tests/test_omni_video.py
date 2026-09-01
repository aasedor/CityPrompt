import base64
import io
import uuid

import pytest
from PIL import Image
from pydantic import ValidationError

from app.api.v1.video import (
    INTERNAL_ENHANCE_MAX_RUNS,
    PILOT_MAX_PROVIDER_CALLS,
    SEEDANCE_PILOT_MAX_PROVIDER_CALLS,
    VideoPilotRequest,
    _best_automatic_benchmark_index,
    _count_provider_calls,
    _provider_usage,
    _storage_key_from_file_url,
)
from app.services.omni_video import (
    build_cinematic_prompt,
    build_omni_payload,
    decode_guide_image,
    decode_preview_video,
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


def test_decode_preview_video_accepts_browser_webm_and_rejects_mime_mismatch():
    webm = b"\x1aE\xdf\xa3" + b"0" * 1024
    encoded = "data:video/webm;base64," + base64.b64encode(webm).decode()

    assert decode_preview_video(encoded, "video/webm;codecs=vp9").data == webm
    with pytest.raises(ValueError, match="MP4 content"):
        decode_preview_video(encoded, "video/mp4")


def test_video_request_exposes_only_bounded_finish_style_not_arbitrary_visual_style():
    assert "style" not in VideoPilotRequest.model_fields
    assert "finish_style" in VideoPilotRequest.model_fields
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

    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id="00000000-0000-0000-0000-000000000001",
            guide_frame_base64=_jpeg_data_url(),
            route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
            finish_style="watercolour",
        )


def test_internal_enhance_defaults_to_the_fast_source_locked_tier():
    request = VideoPilotRequest(
        project_id="00000000-0000-0000-0000-000000000001",
        provider="internal_enhance",
        guide_frame_base64=_jpeg_data_url(),
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
    )

    assert request.internal_enhance_quality == "fast"


def test_video_request_defaults_to_high_quality_and_validates_capture_audit():
    request = VideoPilotRequest(
        project_id="00000000-0000-0000-0000-000000000001",
        guide_frame_base64=_jpeg_data_url(),
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
        capture_profile={
            "encoder": "webcodecs_h264",
            "fixed_timestep": True,
            "frame_count": 192,
            "fps": 24,
            "width": 1920,
            "height": 1080,
            "render_width": 2560,
            "render_height": 1440,
            "tile_warmup_frame_count": 192,
            "tile_set_held": True,
            "geometry_checkpoint_count": 6,
            "semantic_checkpoint_count": 6,
            "instance_checkpoint_count": 6,
            "depth_checkpoint_count": 6,
            "normal_checkpoint_count": 6,
            "motion_frame_count": 192,
        },
    )

    assert request.render_quality == "high"
    assert request.capture_profile is not None
    assert request.capture_profile.render_width == 2560

    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id="00000000-0000-0000-0000-000000000001",
            guide_frame_base64=_jpeg_data_url(),
            route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
            render_quality="ultra",
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


def test_omni_payload_supports_ordered_route_keyframes():
    frames = [(_jpeg_data_url(), "image/jpeg") for _ in range(6)]
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
        camera_motion="path_follow",
        scene_brief="Two buildings and one park.",
        duration_seconds=8,
        control_mode="multi_keyframe",
        keyframe_count=6,
    )
    payload = build_omni_payload(
        model="gemini-omni-flash-preview",
        guide_base64=_jpeg_data_url(),
        guide_mime_type="image/jpeg",
        prompt=prompt,
        duration_seconds=8,
        control_mode="multi_keyframe",
        route_keyframes=frames,
    )

    assert prompt.startswith("[# Sources <FIRST_FRAME>@Image1]")
    assert "<IMAGE_REF_4>@Image6" in prompt
    assert "later images are geometric and geographic route checkpoints" in prompt
    assert payload["generation_config"] == {"video_config": {"task": "reference_to_video"}}
    assert [item["type"] for item in payload["input"]] == ["image"] * 6 + ["text"]


def test_omni_payload_supports_deterministic_preview_video_edit():
    preview = "data:video/webm;base64," + base64.b64encode(b"preview").decode()
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
        camera_motion="path_follow",
        scene_brief="Two buildings and one park.",
        duration_seconds=8,
        control_mode="preview_video",
    )
    payload = build_omni_payload(
        model="gemini-omni-flash-preview",
        guide_base64=_jpeg_data_url(),
        guide_mime_type="image/jpeg",
        prompt=prompt,
        duration_seconds=8,
        control_mode="preview_video",
        preview_video_base64=preview,
        preview_video_mime_type="video/webm",
    )

    assert "Copy the supplied video's camera positions, headings, speed, timing" in prompt
    assert "VISUAL FINISH — CONTROLLED EXCEPTION" in prompt
    assert "physically convincing facade materials" in prompt
    assert "realistic glazing with restrained reflections" in prompt
    assert "natural contact shadows and ambient occlusion" in prompt
    assert "subtle foliage movement" in prompt
    assert "small number of correctly scaled pedestrians" in prompt
    assert "Never spawn, fade, dissolve, teleport, duplicate" in prompt
    assert "subtle environmental ambience only, with no dialogue or music" in prompt
    assert "Match the source video's total travel distance" in prompt
    assert payload["generation_config"] == {"video_config": {"task": "edit"}}
    assert [item["type"] for item in payload["input"]] == ["video", "text"]
    assert payload["response_format"] == {"type": "video"}


def test_documentary_finish_is_photographic_only_and_keeps_architecture_locked():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
        camera_motion="path_follow",
        scene_brief="Three RLASM buildings at different whole-bay widths.",
        duration_seconds=8,
        control_mode="preview_video",
        provider="omni",
        finish_style="documentary",
    )

    assert "DOCUMENTARY VISUAL FINISH — CONTROLLED EXCEPTION" in prompt
    assert "flat natural daylight" in prompt
    assert "restrained true-to-life colour" in prompt
    assert "new signage, blind windows, extra doors" in prompt
    assert "bay count, entrance assembly" in prompt
    assert "Do not apply a photographic or artistic style" not in prompt


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


def test_detail_flythrough_is_low_and_source_route_locked():
    prompt = build_cinematic_prompt(
        route_points=[
            {"x": 0.25, "y": 0.7},
            {"x": 0.5, "y": 0.52},
            {"x": 0.75, "y": 0.68},
        ],
        camera_motion="detail_flythrough",
        scene_brief="Two authored buildings and one park.",
        duration_seconds=8,
        control_mode="preview_video",
    )

    assert "low detail architectural-drone fly-through" in prompt
    assert "six metres above the route surface" in prompt
    assert "between the authored buildings" in prompt
    assert "Match the source video's total travel distance" in prompt
    assert "Never fly through a solid wall, roof, tree, or facade" in prompt


def test_prompt_uses_premium_architectural_camera_language_and_ground_contact_lock():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.22, "y": 0.72}, {"x": 0.5, "y": 0.55}, {"x": 0.78, "y": 0.48}],
        camera_motion="path_follow",
        scene_brief="Three authored buildings, one park, and one street.",
        duration_seconds=8,
        control_mode="preview_video",
        provider="omni",
    )

    assert "ARCHITECTURAL CINEMATOGRAPHY" in prompt
    assert "gentle acceleration into the move" in prompt
    assert "gentle deceleration into the final hold" in prompt
    assert "coherent foreground-to-background parallax" in prompt
    assert "No roll, dutch angle, yaw hunting, orbiting, speed ramp" in prompt
    assert "autofocus breathing, rack focus" in prompt
    assert "GROUND-CONTACT LOCK" in prompt
    assert "Never raise, lower, tilt, bury, float, hover" in prompt
    assert "sink its base below the ground plane" in prompt
    assert "720p" not in prompt
    assert "highest resolution supported by the supplied control video" in prompt


def test_prompt_ends_with_explicit_clean_plate_override_for_zone_id_artifacts():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.25, "y": 0.65}, {"x": 0.75, "y": 0.48}],
        camera_motion="path_follow",
        scene_brief="B1, B2, and B3 frame P1 beside S1.",
        duration_seconds=8,
        control_mode="preview_video",
        provider="omni",
    )

    assert "CLEAN-PLATE OUTPUT - ABSOLUTE FINAL CHECK" in prompt
    assert "no B1, B2, B3, P1, S1, zone IDs" in prompt
    assert "no typography or interface graphics anywhere" in prompt
    assert prompt.endswith("preserve the corresponding source-video pixels unchanged.")


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
    assert "The control input already contains the final approved design and look" in prompt
    assert "Newly revealed pixels caused by the small camera move" in prompt
    assert "CONTEXT ISOLATION — FINAL OVERRIDE" in prompt
    assert "it is not global art direction" in prompt
    assert "Any new background instance of an authored archetype is a failed result" in prompt
    assert "When motion or visual quality conflicts with context fidelity, preserve Image1 unchanged." in prompt
    assert prompt.endswith("preserve the corresponding source-video pixels unchanged.")


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
    assert "When motion or visual quality conflicts with context fidelity, preserve Image1 unchanged." in prompt
    assert prompt.endswith("preserve the corresponding source-video pixels unchanged.")


@pytest.mark.parametrize(
    "response",
    [
        {"id": "interaction-1", "output_video": {"type": "video", "data": base64.b64encode(b"mp4").decode()}},
        {
            "id": "interaction-2",
            "outputs": [
                {"type": "text", "text": "done"},
                {"type": "video", "data": base64.b64encode(b"mp4").decode(), "mime_type": "video/mp4"},
            ],
        },
    ],
)
def test_parse_omni_video_supports_current_response_shapes(response):
    result = parse_omni_video(response)

    assert result.video_bytes == b"mp4"
    assert result.mime_type == "video/mp4"
    assert result.interaction_id.startswith("interaction-")


def test_find_omni_video_content_supports_nested_uri_delivery():
    output = find_omni_video_content(
        {
            "id": "interaction-uri",
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [
                        {
                            "type": "video",
                            "uri": "https://generativelanguage.googleapis.com/v1beta/files/generated-video",
                            "mime_type": "video/mp4",
                        }
                    ],
                }
            ],
        }
    )

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

    assert PILOT_MAX_PROVIDER_CALLS == 49
    assert _count_provider_calls(attempts) == 2


def test_seedance_ledger_has_an_independent_hard_four_call_cap():
    attempts = [
        {"provider": "omni", "provider_call_started_at": "2026-08-03T00:00:00Z"},
        {"provider": "seedance_mini", "provider_call_started_at": "2026-08-03T00:01:00Z"},
        {"provider": "seedance_mini", "provider_call_started_at": "2026-08-03T00:02:00Z"},
    ]

    usage = _provider_usage(attempts, "seedance_mini")

    assert SEEDANCE_PILOT_MAX_PROVIDER_CALLS == 4
    assert _count_provider_calls(attempts, "seedance_mini") == 2
    assert usage.attempts_used == 2
    assert usage.attempts_remaining == 2
    assert usage.max_attempts == 4


def test_internal_enhance_ledger_counts_unlimited_local_runs_without_paid_provider_calls():
    attempts = [
        {
            "provider": "internal_enhance",
            "status": "complete",
            "local_run_started_at": "2026-08-03T12:00:00Z",
        },
        {
            "provider": "internal_enhance",
            "status": "failed",
            "local_run_started_at": "2026-08-03T12:05:00Z",
        },
        {
            "provider": "omni",
            "status": "complete",
            "provider_call_started_at": "2026-08-03T12:10:00Z",
        },
    ]

    usage = _provider_usage(attempts, "internal_enhance")

    assert INTERNAL_ENHANCE_MAX_RUNS is None
    assert _count_provider_calls(attempts, "internal_enhance") == 2
    assert usage.attempts_used == 2
    assert usage.attempts_remaining is None
    assert usage.max_attempts is None


def test_automatic_benchmark_prefers_score_then_worst_frame_then_earlier_result():
    attempts = [
        {
            "provider": "omni",
            "status": "complete",
            "style": "source_fidelity",
            "fidelity_score": 71.0,
            "fidelity_min_score": 48.0,
        },
        {
            "provider": "omni",
            "status": "complete",
            "style": "source_fidelity",
            "fidelity_score": 74.0,
            "fidelity_min_score": 44.0,
        },
        {
            "provider": "omni",
            "status": "complete",
            "style": "source_fidelity",
            "fidelity_score": 74.0,
            "fidelity_min_score": 52.0,
        },
        {
            "provider": "seedance_mini",
            "status": "complete",
            "style": "source_fidelity",
            "fidelity_score": 99.0,
            "fidelity_min_score": 99.0,
        },
    ]

    assert _best_automatic_benchmark_index(attempts) == 2


def test_fidelity_storage_keys_are_scoped_to_the_authorized_project():
    project_id = uuid.uuid4()
    own_url = f"/api/v1/files/projects/{project_id}/video-render/attempt/omni.mp4"
    other_url = f"/api/v1/files/projects/{uuid.uuid4()}/video-render/attempt/omni.mp4"

    assert _storage_key_from_file_url(own_url, project_id) == own_url.split("/api/v1/files/", 1)[1]
    assert _storage_key_from_file_url(other_url, project_id) is None
