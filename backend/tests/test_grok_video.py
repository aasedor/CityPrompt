"""xAI Grok Video helpers, with xAI mocked at the HTTP layer."""
import json

import httpx
import pytest

from app.services import grok_video
from app.services.grok_video import (
    GROK_LOCK,
    GrokRequestError,
    build_grok_generation_payload,
    build_grok_video_prompt,
    estimate_grok_video_cost,
    grok_model_for,
    keyframe_schedule,
    request_grok_video_once,
)
from app.services.omni_video import GuideImage, PreviewVideo
from app.services.video_prompts import build_grok_look_prompt, build_look_sheet

MP4 = PreviewVideo(data=b"\x00\x00\x00\x18ftypmp42" + b"0" * 2048, mime_type="video/mp4")


def _frame(tag: bytes) -> GuideImage:
    return GuideImage(data=b"\xff\xd8" + tag, mime_type="image/jpeg", width=1280, height=720)


def test_cost_follows_published_per_second_pricing_by_mode():
    assert grok_model_for("preview_video", generation_model="g", edit_model="e") == "e"
    assert grok_model_for("multi_keyframe", generation_model="g", edit_model="e") == "g"
    assert estimate_grok_video_cost(model="grok-imagine-video-1.5", output_video_seconds=8) == 0.64
    assert estimate_grok_video_cost(model="grok-imagine-video", output_video_seconds=8) == 0.40


def test_preview_mode_uses_the_shared_look_sheet_and_image_modes_add_lock_and_camera():
    sheet = build_look_sheet(look_style="night", add_people=True, student_note="  soft   rain\nglow ")
    edit_prompt = build_grok_video_prompt(camera_motion="street_walkby", control_mode="preview_video", sheet=sheet)
    assert edit_prompt == build_grok_look_prompt(sheet)
    assert edit_prompt.startswith("Change only the look of this video: blue-hour night")
    assert "Keep everything else the same" in edit_prompt
    assert GROK_LOCK not in edit_prompt

    image_prompt = build_grok_video_prompt(camera_motion="street_walkby", control_mode="multi_keyframe", sheet=sheet)
    lines = image_prompt.split("\n")
    assert lines[0] == GROK_LOCK
    assert lines[1].startswith("Follow the source pedestrian walk-by exactly")
    assert lines[2].startswith("Blue-hour night:")
    assert "A few pedestrians" in lines[2]
    assert lines[3] == "Note: soft rain glow. (This never changes the plan.)"
    quiet = build_grok_video_prompt(camera_motion="path_follow", control_mode="single_frame", sheet=build_look_sheet())
    assert "Note:" not in quiet


def test_generation_payload_is_8s_720p_16x9_silent_image_to_video():
    payload = build_grok_generation_payload(model="grok-imagine-video-1.5", prompt="p", guide=_frame(b"g"),
                                            route_keyframes=[], duration_seconds=8)
    assert payload["image"]["url"].startswith("data:image/jpeg;base64,")
    assert (payload["duration"], payload["resolution"], payload["aspect_ratio"], payload["generate_audio"]) == (8, "720p", "16:9", False)
    assert "keyframes" not in payload


def test_route_frames_pin_at_most_five_images_on_the_third_second_grid():
    frames = [_frame(bytes([index])) for index in range(6)]
    payload = build_grok_generation_payload(model="m", prompt="p", guide=_frame(b"g"),
                                            route_keyframes=frames, duration_seconds=8)
    times = [keyframe["timestamp_s"] for keyframe in payload["keyframes"]]
    assert 1 + len(times) == 5
    assert times == sorted(set(times))
    assert all(0 < t < 8 and abs(t * 3 - round(t * 3)) < 1e-9 for t in times)
    assert times[-1] == pytest.approx(23 / 3)
    assert keyframe_schedule(3, 8) == [(1, 4.0), (2, pytest.approx(23 / 3))]


def _transport(responses, calls):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return responses.pop(0)
    return httpx.MockTransport(handler)


def _done(url="https://vidgen.x.ai/out.mp4", **video):
    return httpx.Response(200, json={"status": "done", "video": {"url": url, "respect_moderation": True, **video},
                                     "usage": {"cost_in_usd_ticks": 4_000_000_000}})


async def _run(responses, calls, **overrides):
    arguments = dict(api_key="secret-key", prompt="p", control_mode="preview_video", guide=_frame(b"g"),
                     route_keyframes=[], preview=MP4, duration_seconds=8, generation_model="grok-imagine-video-1.5",
                     edit_model="grok-imagine-video", timeout_seconds=60, poll_interval_seconds=0,
                     transport=_transport(responses, calls))
    return await request_grok_video_once(**{**arguments, **overrides})


@pytest.fixture(autouse=True)
def no_ffmpeg(monkeypatch):
    # Keep downloads byte-exact in tests; audio stripping is exercised by ffmpeg in the runtime.
    monkeypatch.setattr(grok_video.shutil, "which", lambda _: None)


@pytest.mark.asyncio
async def test_preview_mode_edits_the_route_video_once_and_downloads_without_credentials():
    calls: list[httpx.Request] = []
    responses = [httpx.Response(200, json={"request_id": "req-1"}), httpx.Response(202),
                 httpx.Response(200, json={"status": "pending", "progress": 40}), _done(),
                 httpx.Response(200, content=b"mp4-bytes", headers={"content-type": "video/mp4"})]
    result = await _run(responses, calls)
    assert (result.request_id, result.video_bytes, result.model, result.reference_mode) == (
        "req-1", b"mp4-bytes", "grok-imagine-video", "preview_video_edit")
    assert result.provider_cost_usd == 0.4
    assert [c.method for c in calls] == ["POST", "GET", "GET", "GET", "GET"]
    body = json.loads(calls[0].content)
    assert calls[0].url.path == "/v1/videos/edits" and body["model"] == "grok-imagine-video"
    assert body["video"]["url"].startswith("data:video/mp4;base64,")
    assert calls[0].headers["authorization"] == "Bearer secret-key"
    assert calls[-1].url.host == "vidgen.x.ai" and "authorization" not in calls[-1].headers


@pytest.mark.asyncio
async def test_rejected_route_preview_falls_back_to_the_guide_frame_with_one_job():
    calls: list[httpx.Request] = []
    responses = [httpx.Response(422, json={"error": {"code": "invalid_argument", "message": "unsupported video"}}),
                 httpx.Response(200, json={"request_id": "req-2"}), _done(),
                 httpx.Response(200, content=b"mp4")]
    result = await _run(responses, calls)
    assert result.reference_mode == "guide_frame_fallback" and result.model == "grok-imagine-video-1.5"
    assert [c.url.path for c in calls[:2]] == ["/v1/videos/edits", "/v1/videos/generations"]
    assert json.loads(calls[1].content)["image"]["url"].startswith("data:image/jpeg")


@pytest.mark.asyncio
async def test_auth_and_rate_limit_rejections_do_not_fall_back():
    for status in (401, 429):
        calls: list[httpx.Request] = []
        with pytest.raises(GrokRequestError) as error:
            await _run([httpx.Response(status, json={"error": "no"})], calls)
        assert error.value.status_code == status and len(calls) == 1


@pytest.mark.asyncio
async def test_keyframe_mode_uses_image_to_video():
    calls: list[httpx.Request] = []
    responses = [httpx.Response(200, json={"request_id": "req-3"}), _done(), httpx.Response(200, content=b"mp4")]
    result = await _run(responses, calls, control_mode="multi_keyframe", preview=None,
                        route_keyframes=[_frame(b"a"), _frame(b"b"), _frame(b"c")])
    assert result.reference_mode == "route_keyframes"
    assert calls[0].url.path == "/v1/videos/generations" and len(json.loads(calls[0].content)["keyframes"]) == 2


@pytest.mark.asyncio
async def test_failed_filtered_expired_and_empty_results_are_failures_with_request_id():
    for terminal, download in (
        (httpx.Response(200, json={"status": "failed", "error": {"code": "invalid_argument", "message": "blocked"}}), None),
        (httpx.Response(200, json={"status": "done", "video": {"url": "", "respect_moderation": False}}), None),
        (httpx.Response(200, json={"status": "expired"}), None),
        (_done(), httpx.Response(200, content=b"")),
    ):
        calls: list[httpx.Request] = []
        responses = [httpx.Response(200, json={"request_id": "req-4"}), terminal] + ([download] if download else [])
        with pytest.raises(GrokRequestError) as error:
            await _run(responses, calls, control_mode="single_frame", preview=None)
        assert error.value.request_id == "req-4"


@pytest.mark.asyncio
async def test_polling_stops_at_the_timeout():
    calls: list[httpx.Request] = []
    responses = [httpx.Response(200, json={"request_id": "req-5"})] + [httpx.Response(202) for _ in range(3)]
    with pytest.raises(GrokRequestError) as error:
        await _run(responses, calls, control_mode="single_frame", preview=None, timeout_seconds=0)
    assert "did not finish" in str(error.value) and error.value.request_id == "req-5"
