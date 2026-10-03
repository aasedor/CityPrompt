from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from app.core import classroom_scope
from app.core.config import Settings


@pytest.mark.asyncio
@pytest.mark.parametrize("path,query,blocked", [
    ("/api/v1/render/generate", "", True),
    ("/api/v1/render/generate-direct-3d", "", True),
    ("/api/v1/video/generate", "", True),
    ("/api/v1/video/benchmark", "", True),
    ("/api/v1/buildings/one/generate", "", True),
    ("/api/v1/buildings/one/generate-from-image", "", True),
    ("/api/v1/buildings/one/render-preview", "", True),
    ("/api/v1/site-zones/projects/one/generate-all", "", True),
    ("/api/v1/site-zones/one/render-site-preview", "", True),
    ("/api/v1/custom-style/expand", "", True),
    ("/api/v1/model-cache/prewarm", "", True),
    ("/api/v1/urban-dna/zones/one/scenarios", "", True),
    ("/api/v1/documents/projects/one/upload", "", True),
    ("/api/v1/documents/projects/one/upload", "?process_mode=reference", False),
    ("/api/v1/render/direct-3d-attempts", "", False),
    ("/api/v1/lego-assembly/place-community", "", False),
    ("/api/v1/site-landscape/one/preview", "", False),
    ("/api/v1/site-landscape/one/apply", "", False),
    ("/api/v1/student-reports/project/one", "", False),
    ("/api/v1/site-zones/projects/one/restore-snapshot", "", False),
])
async def test_classroom_blocks_deferred_paid_operations_before_dispatch(monkeypatch, path, query, blocked):
    monkeypatch.setattr(classroom_scope, "get_settings", lambda: SimpleNamespace(classroom_release=True))
    app = FastAPI(dependencies=[Depends(classroom_scope.require_classroom_scope)])
    dispatch = AsyncMock()
    @app.post(path)
    async def endpoint():
        await dispatch()
        return {"ok": True}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(path + query)
    assert response.status_code == (403 if blocked else 200)
    assert dispatch.await_count == (0 if blocked else 1)
    if blocked:
        assert response.json()["detail"]["billed"] is False


def classroom_settings(**changes):
    values = dict(_env_file=None, classroom_release=True, direct_3d_jobs_enabled=True,
                  direct_3d_images_enabled=False, openai_api_key="mock-only", anthropic_api_key="",
                  gemini_api_key="", meshy_api_key="", tripo_api_key="", stability_api_key="", fal_key="", vertex_ai_project="")
    return Settings(**{**values, **changes})


def test_classroom_refuses_uncapped_production_images_and_extra_provider_keys():
    with pytest.raises(ValueError, match="positive RENDER_GLOBAL_DAILY_TOKEN_CAP"):
        classroom_settings(app_env="production", direct_3d_images_enabled=True, render_global_daily_token_cap=0)
    with pytest.raises(ValueError, match="deferred AI"):
        classroom_settings(anthropic_api_key="mock-only")
    with pytest.raises(ValueError, match="DIRECT_3D_JOBS_ENABLED"):
        classroom_settings(direct_3d_jobs_enabled=False)
    assert classroom_settings().layout_ai_provider == "none"


@pytest.mark.asyncio
@pytest.mark.parametrize("classroom,images,status", [(True, True, 403), (False, False, 503)])
async def test_internal_landscape_call_cannot_bypass_classroom_or_image_pause(monkeypatch, classroom, images, status):
    from fastapi import HTTPException
    from app.api.v1 import render, site_landscape
    settings = SimpleNamespace(classroom_release=classroom, direct_3d_images_enabled=images)
    monkeypatch.setattr(render, "get_settings", lambda: settings)
    monkeypatch.setattr(site_landscape, "get_settings", lambda: settings)
    reserve = AsyncMock()
    provider = AsyncMock()
    monkeypatch.setattr(render, "_reserve_render", reserve)
    monkeypatch.setattr(render, "_generate_render_image", provider)
    with pytest.raises(HTTPException) as error:
        await render.generate_render(render.RenderRequest(prompt="pool surround"), SimpleNamespace(), AsyncMock())
    assert error.value.status_code == status
    reserve.assert_not_awaited()
    provider.assert_not_awaited()
    assert (await site_landscape.landscape_options(SimpleNamespace()))["custom_enabled"] is False
