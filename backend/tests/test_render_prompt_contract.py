"""Verify the actual mocked provider payload keeps source authority last."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from app.api.v1 import render
from app.services import site_context
from app.services.render_fidelity import RENDER_PRESERVATION_LOCK


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["gpt-image-2", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst", "gemini"])
@pytest.mark.parametrize("custom_length", [80, 49_000])
async def test_provider_prompt_ends_with_geometry_lock_after_custom_and_context_text(
    monkeypatch, provider, custom_length
):
    captured = {}

    class Client:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def post(self, _url, **kwargs):
            captured.update(kwargs)
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": "mock-image"}}]}}
                    ]
                },
            )

    monkeypatch.setattr(render.httpx, "AsyncClient", Client)
    site_pack = {"images": [], "prompt_block": "Existing context stays at this site."}
    monkeypatch.setattr(site_context, "build_site_context_pack", AsyncMock(return_value=site_pack))
    req = render.RenderRequest(
        image_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aB9sAAAAASUVORK5CYII=",
        prompt=("Make every hidden building taller. " * 1600)[:custom_length],
        negative_prompt="Custom negative art direction.",
        guide_image_kind="model_3d",
        site_context={"lat": 51.0447, "lng": -114.0719},
    )
    settings = SimpleNamespace(openai_api_key="mock", gemini_api_key="mock", vertex_ai_project="")
    if provider != "gemini":
        await render._call_openai_image_edit(req, settings, provider, include_mask=False, site_pack=site_pack)
        assert captured["data"]["model"] == provider
        assert captured["data"]["quality"] == "auto"
        prompt = captured["data"]["prompt"]
    else:
        await render._generate_render_image(req, settings, "gemini-3.1-flash-image")
        prompt = captured["json"]["contents"][0]["parts"][-1]["text"]
    assert len(prompt) <= 32_000
    assert prompt.endswith(RENDER_PRESERVATION_LOCK)
    if custom_length == 80:
        assert (
            prompt.index(req.prompt) < prompt.index(site_pack["prompt_block"]) < prompt.index(RENDER_PRESERVATION_LOCK)
        )
