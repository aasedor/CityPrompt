import asyncio

from app.services.omni_video import PreviewVideo, build_cinematic_prompt
from app.services.seedance_video import (
    SEEDANCE_MINI_ENDPOINT,
    _output_video_url,
    _preview_as_mp4,
    build_seedance_arguments,
    estimate_seedance_mini_cost,
)


def test_seedance_mini_cost_counts_eight_input_and_eight_output_seconds():
    assert estimate_seedance_mini_cost(input_video_seconds=8, output_video_seconds=8) == 1.98


def test_seedance_arguments_are_bounded_silent_and_reproducible():
    arguments = build_seedance_arguments(
        prompt="Animate @Video1 without changing the buildings.",
        preview_url="https://example.com/route.mp4",
        keyframe_urls=["https://example.com/first.jpg", "https://example.com/middle.jpg"],
        duration_seconds=8,
    )

    assert SEEDANCE_MINI_ENDPOINT.endswith("/mini/reference-to-video")
    assert arguments["video_urls"] == ["https://example.com/route.mp4"]
    assert arguments["image_urls"] == [
        "https://example.com/first.jpg",
        "https://example.com/middle.jpg",
    ]
    assert arguments["resolution"] == "720p"
    assert arguments["duration"] == "8"
    assert arguments["aspect_ratio"] == "16:9"
    assert arguments["generate_audio"] is False
    assert arguments["seed"] == 7941


def test_seedance_prompt_names_video_and_three_geometry_anchors():
    prompt = build_cinematic_prompt(
        route_points=[{"x": 0.4, "y": 0.6}, {"x": 0.6, "y": 0.4}],
        camera_motion="path_follow",
        scene_brief="Two courtyard buildings frame one park.",
        duration_seconds=8,
        control_mode="preview_video",
        keyframe_count=3,
        provider="seedance_mini",
    )

    assert "@Video1 is City Prompt's deterministic render" in prompt
    assert "@Image1 through @Image3" in prompt
    assert "Use the ordered images only as immutable geometry anchors" in prompt
    assert "SEEDANCE MINI IS THE ANIMATOR ONLY" in prompt


def test_mp4_preview_passes_through_without_transcoding():
    preview = PreviewVideo(data=b"already-an-mp4", mime_type="video/mp4")

    assert asyncio.run(_preview_as_mp4(preview)) == preview.data


def test_seedance_output_requires_https_video_url():
    assert _output_video_url({"video": {"url": "https://fal.media/result.mp4"}}).endswith("result.mp4")
