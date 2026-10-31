"""Paid originals survive alignment, gallery persistence and interrupted responses."""

from dataclasses import asdict, replace
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from PIL import Image
import pytest

from app.api.v1 import direct_3d_render as api
from app.services import render_attempts as jobs
from app.services.direct_3d_render import Direct3DRenderService
from tests.test_direct_3d_render import _request, _fake_service_result, _png_b64, _project_preflight_db


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["gemini-nano-banana-2.1", "gpt-image-2.5-flare"])
@pytest.mark.parametrize("strategy", [None, "provider_full_scene"])
@pytest.mark.parametrize("distinct", [False, True])
async def test_gallery_retains_each_distinct_provider_original(monkeypatch, model, strategy, distinct):
    request = _request(model=model)
    result = _fake_service_result(_png_b64(Image.new("RGB", (2, 2), "white")))
    original = _png_b64(Image.new("RGB", (4, 3), "blue")) if distinct else result.image_base64
    result = replace(result, provider_image_base64=original)
    result.diagnostics["returned_safety_strategy"] = strategy
    gallery = AsyncMock(return_value=None)
    monkeypatch.setattr(api, "persist_render_to_gallery", gallery)
    monkeypatch.setattr(
        api, "_reserve_direct_render", AsyncMock(return_value=SimpleNamespace(id=uuid.uuid4(), tokens_spent=13))
    )
    monkeypatch.setattr(api, "_finalize_direct_audit", AsyncMock())
    monkeypatch.setattr(Direct3DRenderService, "generate", AsyncMock(return_value=result))
    monkeypatch.setattr(
        api,
        "get_settings",
        lambda: SimpleNamespace(
            openai_api_key="mock-never-sent",
            gemini_api_key="mock-never-sent",
            render_global_daily_token_cap=0,
            direct_3d_jobs_enabled=False,
            direct_3d_images_enabled=True,
        ),
    )

    await api.generate_direct_3d_render(
        request,
        user=SimpleNamespace(role="admin", email="admin@example.com", id="admin"),
        db=_project_preflight_db(monkeypatch),
    )

    assert gallery.await_count == (2 if distinct else 1)
    assert gallery.await_args_list[0].kwargs["variant"] == "final"
    if distinct:
        saved = gallery.await_args_list[1]
        assert saved.kwargs["variant"] == "provider_original"
        assert saved.args[2].image_base64 == original


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["accepted", "review_required"])
async def test_interrupted_response_recovers_original_without_another_provider_call(monkeypatch, outcome):
    result = replace(
        _fake_service_result("unused-source"),
        outcome=outcome,
        provider_image_base64=_png_b64(Image.new("RGB", (4, 3), "blue")),
    )
    evidence = {"result": asdict(result), "model": "gemini-nano-banana-2.1"}
    read = AsyncMock(side_effect=lambda attempt, part: evidence if part == "provider-result" else None)
    provider = AsyncMock(side_effect=AssertionError("Recovery must not repeat paid generation"))
    monkeypatch.setattr(jobs, "read_evidence", read)
    monkeypatch.setattr(Direct3DRenderService, "generate", provider)

    recovered = await jobs.recover_result(SimpleNamespace())
    assert recovered.image_base64 == result.image_base64
    assert recovered.provider_image_base64 == result.provider_image_base64
    assert recovered.model == evidence["model"]
    assert recovered.outcome == outcome
    provider.assert_not_awaited()


def test_legacy_evidence_without_an_original_still_recovers():
    result = asdict(_fake_service_result("unused-source"))
    result.pop("provider_image_base64", None)
    assert jobs.response_from_evidence({"result": result, "model": "gpt-image-2"}).provider_image_base64 is None
