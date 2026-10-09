import base64
import io
from types import SimpleNamespace

import httpx
import pytest
from PIL import Image
from fastapi import HTTPException

from app.api.v1 import render


def raster(fmt="PNG"):
    output = io.BytesIO()
    Image.new("RGB", (16, 12), "green").save(output, format=fmt)
    return base64.b64encode(output.getvalue()).decode()


@pytest.mark.asyncio
async def test_invalid_optional_reference_never_reaches_provider(monkeypatch):
    captured = {}
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, **kwargs):
            captured.update(kwargs)
            return httpx.Response(200, json={"data": [{"b64_json": raster()}]})
    monkeypatch.setattr(render.httpx, "AsyncClient", Client)
    pointer = base64.b64encode(b"version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 123\n").decode()
    req = render.RenderRequest(prompt="Keep the scene", image_base64="data:image/jpeg;base64," + raster("JPEG"),
        archetype_images=[render.ArchetypeImage(label="Missing facade", image_base64=pointer),
                          render.ArchetypeImage(label="Valid facade", image_base64=raster())],
        previous_render_base64=pointer)
    await render._call_openai_image_edit(req, SimpleNamespace(openai_api_key="test"), "gpt-image-2.5-sunburst",
        include_mask=False, site_pack={"images": [("bad", "image/jpeg", pointer), ("good", "image/png", raster("JPEG"))], "prompt_block": "Context"})
    files = captured["files"]
    assert len(files) == 3
    for _, (name, data, mime) in files:
        with Image.open(io.BytesIO(data)) as img:
            img.load()
            assert mime == Image.MIME[img.format]
    assert "final 1 attached images" in captured["data"]["prompt"]
    assert len(req.archetype_images) == 2  # Sanitizing must not mutate the incoming request.


@pytest.mark.asyncio
async def test_invalid_primary_capture_stops_before_network(monkeypatch):
    def forbidden(**kwargs):
        pytest.fail("Invalid primary image reached provider client")
    monkeypatch.setattr(render.httpx, "AsyncClient", forbidden)
    with pytest.raises(HTTPException) as exc:
        await render._call_openai_image_edit(render.RenderRequest(prompt="p", image_base64=base64.b64encode(b"not pixels").decode()),
            SimpleNamespace(openai_api_key="test"), "gpt-image-2.5-sunburst", include_mask=False)
    assert "capture" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_provider_failure_has_no_raw_json(monkeypatch):
    async def fail(*args, **kwargs):
        return httpx.Response(400, json={"error": {"code": "invalid_image_file", "message": "Invalid image data."}})
    monkeypatch.setattr(render, "_call_openai_image_edit", fail)
    with pytest.raises(HTTPException) as exc:
        await render._generate_openai_render(render.RenderRequest(prompt="p", image_base64=raster()),
            SimpleNamespace(openai_api_key="test"), "gpt-image-2.5-sunburst")
    assert "{" not in exc.value.detail
    assert "try" in exc.value.detail.lower()
