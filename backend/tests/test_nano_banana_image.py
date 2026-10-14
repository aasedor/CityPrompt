import base64
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import httpx
import pytest
from PIL import Image


def png(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return base64.b64encode(out.getvalue()).decode()


def provider(monkeypatch, response):
    from app.services import nano_banana_image as nano

    calls = []

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, **kwargs):
            calls.append((url, kwargs))
            if isinstance(response, Exception):
                raise response
            return response

    monkeypatch.setattr(nano.httpx, "AsyncClient", Client)
    return nano, calls


@pytest.mark.asyncio
async def test_google_interactions_keeps_roles_camera_frame_and_original_without_openai(
    monkeypatch,
):
    # The arbitrary browser aspect is padded, never stretched, to Google's
    # supported ratio; the returned viewport removes only that same padding.
    original = png(Image.new("RGB", (324, 216), "green"))
    nano, calls = provider(
        monkeypatch,
        httpx.Response(
            200,
            json={
                "status": "completed",
                "id": "receipt-1",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "image",
                                "mime_type": "image/png",
                                "data": original,
                            }
                        ],
                    }
                ],
            },
        ),
    )
    source = png(Image.new("RGB", (160, 100), "blue"))
    result = await nano.generate_nano_banana_image(
        "google-key",
        [
            {"text": "Scene capture"},
            {"inlineData": {"mimeType": "image/png", "data": source}},
            {"text": "Preserve the placed buildings and landmarks."},
        ],
        target_size=(160, 100),
        same_camera_images={source},
    )
    assert len(calls) == 1
    url, params = calls[0]
    assert url == "https://generativelanguage.googleapis.com/v1beta/interactions"
    assert params["headers"]["x-goog-api-key"] == "google-key"
    body = params["json"]
    assert body["model"] == "gemini-nano-banana-2.1"
    assert body["response_format"] == {
        "type": "image",
        "mime_type": "image/png",
        "aspect_ratio": "3:2",
        "image_size": "2K",
    }
    assert body["store"] is False
    assert "tools" not in body and "temperature" not in body
    assert body["input"][-1]["text"].endswith(
        "Preserve the placed buildings and landmarks."
    )
    image_part = next(part for part in body["input"] if part["type"] == "image")
    padded = Image.open(io.BytesIO(base64.b64decode(image_part["data"])))
    assert padded.size == (162, 108)
    assert padded.getpixel((1, 4)) == (0, 0, 255)
    assert result.image.size == (160, 100)
    assert result.provider_image_base64 == original


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,billing", [(401, "unproduced"), (429, "unproduced"), (500, "unknown")]
)
async def test_provider_failure_never_retries_or_falls_back(
    monkeypatch, status, billing
):
    nano, calls = provider(
        monkeypatch,
        httpx.Response(status, json={"error": {"message": "Provider unavailable"}}),
    )
    with pytest.raises(nano.NanoBananaProviderError) as err:
        await nano.generate_nano_banana_image(
            "google-key", [{"text": "Render"}], target_size=(512, 512)
        )
    assert err.value.billing_status == billing
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_unreadable_inputs_are_rejected_before_a_paid_request(monkeypatch):
    nano, calls = provider(monkeypatch, httpx.Response(200, json={}))
    with pytest.raises(nano.NanoBananaProviderError) as err:
        await nano.generate_nano_banana_image(
            "google-key",
            [{"inlineData": {"data": "not-an-image", "mimeType": "image/png"}}],
            target_size=(512, 512),
        )
    assert err.value.billing_status == "unproduced"
    assert calls == []


@pytest.mark.asyncio
async def test_text_only_or_incomplete_response_cannot_be_called_a_success(monkeypatch):
    nano, calls = provider(
        monkeypatch,
        httpx.Response(
            200,
            json={
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Cannot render"}],
                    }
                ],
            },
        ),
    )
    with pytest.raises(nano.NanoBananaProviderError) as err:
        await nano.generate_nano_banana_image(
            "google-key", [{"text": "Render"}], target_size=(512, 512)
        )
    assert err.value.billing_status == "unknown"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_classic_and_saved_edit_path_routes_google_and_keeps_mask_roles(
    monkeypatch,
):
    from app.api.v1 import render

    original = png(Image.new("RGB", (512, 512), "green"))
    nano, calls = provider(
        monkeypatch,
        httpx.Response(
            200,
            json={
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "image",
                                "data": original,
                                "mime_type": "image/png",
                            }
                        ],
                    }
                ],
            },
        ),
    )
    req = render.RenderRequest(
        prompt="Make a lively courtyard",
        image_base64=original,
        previous_render_base64=original,
        mask_base64=png(Image.new("RGB", (512, 512), "white")),
        model="gemini-nano-banana-2.1",
    )
    result = await render._generate_render_image(
        req,
        SimpleNamespace(
            gemini_api_key="google-key", openai_api_key="", vertex_ai_project=""
        ),
        req.model,
    )
    assert result.image_base64
    assert result.provider_image_base64 == original
    assert len(calls) == 1
    assert calls[0][1]["json"]["model"] == req.model
    assert "white = edit" in str(calls[0][1]["json"]["input"])
    assert req.model in render._ALLOWED_MODELS


@pytest.mark.asyncio
async def test_google_queue_admission_does_not_require_openai(monkeypatch):
    from app.services import render_attempts as attempts
    from tests.test_direct_3d_render import _request

    request = _request(
        model="gemini-nano-banana-2.1", presentation_mode="scene"
    ).model_copy(update={"project_id": uuid.UUID(int=1)})
    db = AsyncMock()
    db.add = MagicMock()
    db.scalar.return_value = None
    db.scalars.return_value = SimpleNamespace(all=lambda: [])
    monkeypatch.setattr(
        attempts,
        "get_settings",
        lambda: SimpleNamespace(
            direct_3d_jobs_enabled=True,
            direct_3d_images_enabled=True,
            gemini_api_key="google-key",
            openai_api_key="",
            direct_3d_queue_limit=16,
            direct_3d_project_queue_limit=2,
        ),
    )
    for name in (
        "check_project_permission",
        "reserve_image_trial_slot",
        "write_evidence",
        "deliver_attempt",
    ):
        monkeypatch.setattr(attempts, name, AsyncMock())
    attempt = await attempts.submit_attempt(
        db, SimpleNamespace(id=uuid.UUID(int=2)), request, "test-google-only"
    )
    assert attempt.model == "gemini-nano-banana-2.1"
    attempts.write_evidence.assert_awaited_once()
    attempts.deliver_attempt.assert_awaited_once_with(attempt.id)
    assert db.commit.await_count == 1
