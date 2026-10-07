import io
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
from PIL import Image
from pydantic import ValidationError
import pytest

from app.services import kling_video as kling
from app.api.v1.render_animation import RenderAnimationRequest
from app.api.v1.video import VideoPilotRequest, _public_attempt, _provider_usage


def png(width=1600, height=900):
    stream = io.BytesIO()
    Image.new("RGB", (width, height), "#7f8973").save(stream, "PNG")
    return stream.getvalue()


def test_saved_still_payload_matches_documented_schema_and_price():
    assert kling.build_kling_arguments("https://fal.media/finished.png") == {
        "start_image_url": "https://fal.media/finished.png",
        "duration": "5",
        "generate_audio": False,
        "cfg_scale": 0.5,
        "prompt": kling.ANIMATION_PROMPT,
        "negative_prompt": kling.ANIMATION_NEGATIVE_PROMPT,
    }
    assert kling.estimate_kling_cost(0.112) == 0.56
    assert kling.validate_endpoint("fal-ai/kling-video/v3/pro/image-to-video")
    with pytest.raises(ValueError):
        kling.validate_endpoint("https://untrusted.example/submit")


def test_separate_request_forbids_client_images_model_options_and_fake_route_controls():
    import uuid

    body = dict(
        project_id=uuid.uuid4(),
        source_render_id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        confirm_paid_submission=True,
    )
    assert RenderAnimationRequest(**body).source_render_id == body["source_render_id"]
    for field, value in [
        ("start_image_url", "https://example.org/thumb.png"),
        ("duration_seconds", 8),
        ("resolution", "4k"),
        ("route_points", []),
        ("confirm_paid_submission", False),
    ]:
        with pytest.raises(ValidationError):
            RenderAnimationRequest(**{**body, field: value})
    # Existing route contract is still eight seconds, with at least two points.
    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id=body["project_id"], guide_frame_base64="x" * 100, route_points=[]
        )
    with pytest.raises(ValidationError):
        VideoPilotRequest(
            project_id=body["project_id"],
            guide_frame_base64="x" * 100,
            route_points=[{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
            duration_seconds=5,
        )


@pytest.mark.asyncio
async def test_upload_keeps_finished_pixels_and_full_resolution(monkeypatch):
    original = png()
    source = kling.validate_source_image(original)
    upload = AsyncMock(return_value="https://fal.media/exact-source.png")
    monkeypatch.setattr(kling, "_fal_client", lambda _: SimpleNamespace(upload=upload))
    assert (
        await kling.upload_kling_source("mock-key", source)
        == "https://fal.media/exact-source.png"
    )
    upload.assert_awaited_once_with(original, content_type="image/png")
    assert (source.width, source.height) == (1600, 900)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["timeout", "server_error"])
async def test_paid_submission_never_retries_an_uncertain_http_result(
    monkeypatch, failure
):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.headers["Authorization"] == "Key mock-key"
        if failure == "timeout":
            raise httpx.ReadTimeout("receipt lost")
        return httpx.Response(503, json={"error": "unavailable"})

    monkeypatch.setattr(
        kling.httpx, "AsyncHTTPTransport", lambda **_: httpx.MockTransport(handler)
    )
    with pytest.raises(httpx.HTTPError):
        await kling.submit_kling_once(
            "mock-key",
            "fal-ai/kling-video/v3/pro/image-to-video",
            kling.build_kling_arguments("https://fal.media/source.png"),
        )
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_poll_recreates_the_original_handle_and_reads_a_completed_result(
    monkeypatch,
):
    from fal_client import Completed

    handle = SimpleNamespace(
        status=AsyncMock(return_value=Completed(logs=None, metrics={})),
        get=AsyncMock(
            return_value={"video": {"url": "https://fal.media/retained.mp4"}}
        ),
    )
    client = SimpleNamespace(
        get_handle=AsyncMock(return_value=handle), submit=AsyncMock()
    )
    monkeypatch.setattr(kling, "_fal_client", lambda _: client)
    result = await kling.poll_kling_request(
        "mock-key", "fal-ai/kling-video/v3/pro/image-to-video", "already-paid"
    )
    assert result == ("saving", "https://fal.media/retained.mp4")
    client.get_handle.assert_awaited_once_with(
        "fal-ai/kling-video/v3/pro/image-to-video", "already-paid"
    )
    client.submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_provider_failure_is_terminal_and_does_not_fetch_or_resubmit(
    monkeypatch,
):
    from fal_client import Completed

    handle = SimpleNamespace(
        status=AsyncMock(
            return_value=Completed(logs=None, metrics={}, error="Generation failed")
        ),
        get=AsyncMock(),
    )
    client = SimpleNamespace(
        get_handle=AsyncMock(return_value=handle), submit=AsyncMock()
    )
    monkeypatch.setattr(kling, "_fal_client", lambda _: client)
    with pytest.raises(kling.KlingGenerationFailed):
        await kling.poll_kling_request(
            "mock-key", "fal-ai/kling-video/v3/pro/image-to-video", "already-paid"
        )
    handle.get.assert_not_awaited()
    client.submit.assert_not_awaited()


def test_animation_does_not_consume_omni_cap_or_receive_route_fidelity_claims():
    entry = dict(
        id="a",
        request_id="r",
        provider="kling",
        mode="saved_render_animation",
        status="queued",
        style="architectural_film",
        camera_motion="slow_push_in",
        duration_seconds=5,
        created_at="2026-01-01T00:00:00+00:00",
        provider_call_started_at="2026-01-01T00:00:00+00:00",
        estimated_cost_usd=0.56,
        interaction_id="fal-id",
    )
    public = _public_attempt(entry)
    assert public.status == "queued" and public.recoverable
    assert public.fidelity_status is None and public.scene_revision_sha256 is None
    assert _provider_usage([entry], "omni").attempts_used == 0
    assert _provider_usage([entry], "kling").attempts_used == 1
