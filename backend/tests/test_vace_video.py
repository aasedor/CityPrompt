import pytest

from app.services.vace_video import (
    VACE_DEPTH_ENDPOINT,
    VACE_SEED,
    VaceRequestError,
    _output_video_url,
    build_vace_depth_arguments,
    estimate_vace_depth_cost,
    vace_runtime_error,
)


def test_cost_is_ten_cents_per_output_second():
    assert estimate_vace_depth_cost(output_video_seconds=8) == 0.80
    assert VACE_DEPTH_ENDPOINT == "fal-ai/wan-22-vace-fun-a14b/depth"


def test_arguments_send_our_depth_track_as_the_control_and_keep_the_prompt_as_written():
    arguments = build_vace_depth_arguments(
        prompt="Blue-hour night.",
        negative_prompt="text, watermark",
        control_video_url="https://fal.media/depth.mp4",
    )
    assert arguments["video_url"] == "https://fal.media/depth.mp4"
    assert arguments["preprocess"] is False
    assert arguments["enable_prompt_expansion"] is False
    assert (arguments["num_frames"], arguments["frames_per_second"]) == (192, 24)
    assert arguments["match_input_num_frames"] is True and arguments["match_input_frames_per_second"] is True
    assert (arguments["resolution"], arguments["aspect_ratio"]) == ("720p", "16:9")
    assert arguments["seed"] == VACE_SEED
    assert "ref_image_urls" not in arguments and "first_frame_url" not in arguments


def test_anchor_becomes_reference_and_first_frame():
    arguments = build_vace_depth_arguments(
        prompt="p",
        negative_prompt="n",
        control_video_url="https://fal.media/depth.mp4",
        ref_image_urls=["https://fal.media/anchor.png"],
        first_frame_url="https://fal.media/anchor.png",
    )
    assert arguments["ref_image_urls"] == ["https://fal.media/anchor.png"]
    assert arguments["first_frame_url"] == "https://fal.media/anchor.png"


def test_output_url_must_be_https():
    assert _output_video_url({"video": {"url": "https://fal.media/out.mp4"}}) == "https://fal.media/out.mp4"
    with pytest.raises(ValueError, match="HTTPS"):
        _output_video_url({"video": {"url": "http://fal.media/out.mp4"}})
    with pytest.raises(ValueError):
        _output_video_url({})


def test_request_error_keeps_the_fal_request_id():
    error = VaceRequestError("queue failed", request_id="req-1")
    assert error.request_id == "req-1"


def test_runtime_error_mentions_the_missing_dependency(monkeypatch):
    monkeypatch.setattr("app.services.vace_video.shutil.which", lambda _name: None)
    message = vace_runtime_error()
    assert message is None or "ffmpeg" in message or "fal-client" in message
