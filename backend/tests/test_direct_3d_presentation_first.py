"""Live Direct 3D contract: the provider image is the product.

Presentation-first (DIRECT_3D_PRESENTATION_FIRST = True, the shipped default)
returns the provider image untouched for scene and reproject renders — no
registration, inventory gates, repairs, or source-lock fallbacks. The legacy
fail-closed machinery keeps its regression coverage in test_direct_3d_render.py
with the flag pinned False.
"""

import base64
import hashlib
import io

import pytest
from PIL import Image

from app.services import direct_3d_render as direct_service
from app.services.direct_3d_render import Direct3DRenderService

from tests.test_direct_3d_render import (
    _png_b64,
    _request,
    _structured_scene,
)


def _decoded(image_b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")


def test_presentation_first_is_the_shipped_default():
    assert direct_service.DIRECT_3D_PRESENTATION_FIRST is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("presentation_mode", "style"),
    [
        ("scene", "photorealistic"),
        ("scene", "night"),
        ("reproject", "isometric"),
        ("reproject", "site-plan"),
    ],
)
async def test_provider_image_returned_untouched_and_accepted(monkeypatch, presentation_mode, style):
    request = _request(presentation_mode=presentation_mode, style=style)
    beauty, object_id, instance_id = _structured_scene()
    del object_id, instance_id

    # A deliberately different provider image (not a copy of the capture) so
    # any surviving fusion/fallback would visibly change the returned bytes.
    provider = beauty.copy().rotate(1, expand=False).point(lambda v: min(255, v + 17))

    async def _fake_call_openai(self, req, capture, *, server_inventory=None):
        return provider.convert("RGB")

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", _fake_call_openai)

    result = await Direct3DRenderService("test-key").generate(request)

    assert result.outcome == "accepted"
    assert result.warnings == ()
    returned = _decoded(result.image_base64)
    assert _png_b64(returned) == _png_b64(provider.convert("RGB"))
    assert result.provider_image_base64 is not None
    assert hashlib.sha256(base64.b64decode(result.image_base64)).hexdigest() == result.output_fingerprint

    diagnostics = result.diagnostics
    assert diagnostics["provider_first"] is True
    assert diagnostics["provider_spatial_pixels_retained"] is True
    assert diagnostics["returned_safety_strategy"] == "provider_full_scene"
    assert diagnostics["finish_fusion"] is None
    assert diagnostics["registration"] is None
    assert diagnostics["macro_design_fidelity"] is None
    assert diagnostics["structural_edge_fidelity"] is None
    expected_view_lock = "camera_registered" if presentation_mode == "scene" else "not_applicable_layout_guided"
    assert diagnostics["view_lock"] == expected_view_lock


@pytest.mark.asyncio
async def test_fidelity_policy_does_not_change_the_returned_image(monkeypatch):
    beauty, _object_id, _instance_id = _structured_scene()
    provider = beauty.copy().point(lambda v: max(0, v - 23))

    async def _fake_call_openai(self, req, capture, *, server_inventory=None):
        return provider.convert("RGB")

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", _fake_call_openai)

    outputs = set()
    for policy in ("precise", "balanced", "expressive"):
        request = _request(
            presentation_mode="scene",
            style="photorealistic",
            fidelity_policy=policy,
        )
        result = await Direct3DRenderService("test-key").generate(request)
        assert result.outcome == "accepted"
        outputs.add(result.output_fingerprint)
    assert len(outputs) == 1
