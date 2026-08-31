"""Live Direct 3D contract: the provider image is normally the product.

Presentation-first (DIRECT_3D_PRESENTATION_FIRST = True, the shipped default)
returns ordinary scene and reproject images untouched. Server-certified
source-locked RLASM scenes protect exact instance pixels; projection-changing
RLASM views are review-required. The legacy fail-closed machinery keeps its
regression coverage in test_direct_3d_render.py with the flag pinned False.
"""

import base64
import hashlib
import io
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from app.api.v1 import direct_3d_render as direct_api
from app.schemas.direct_3d_render import Direct3DRenderDiagnostics
from app.services import direct_3d_render as direct_service
from app.services.direct_3d_render import Direct3DRenderService, prepare_direct_3d_capture

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


@pytest.mark.asyncio
async def test_source_locked_rlasm_scene_restores_exact_instance_pixels(monkeypatch):
    request = _request(presentation_mode="scene", style="photorealistic")
    capture = prepare_direct_3d_capture(request)
    provider = capture.normalized_beauty.copy().point(lambda value: min(255, value + 29))

    async def _fake_call_openai(self, req, prepared, *, server_inventory=None):
        return provider.convert("RGB")

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", _fake_call_openai)
    inventory = [
        {
            "instance_id": "zone:test-building:building",
            "semantic_class": "building",
            "source_locked_rlasm": True,
        }
    ]

    result = await Direct3DRenderService("test-key").generate(
        request,
        server_inventory=inventory,
    )

    returned = np.asarray(_decoded(result.image_base64))
    source = np.asarray(capture.normalized_beauty.convert("RGB"))
    provider_pixels = np.asarray(provider.convert("RGB"))
    instance_pixels = np.asarray(capture.normalized_instance_id.convert("RGB"))
    protected = np.all(instance_pixels == np.asarray((1, 0, 1), dtype=np.uint8), axis=2)

    assert result.outcome == "review_required"
    assert np.array_equal(returned[protected], source[protected])
    assert np.array_equal(returned[~protected], provider_pixels[~protected])
    assert result.diagnostics["source_locked_rlasm_instance_count"] == 1
    assert result.diagnostics["source_locked_rlasm_pixel_lock_applied"] is True
    assert result.diagnostics["source_locked_rlasm_pixel_coverage"] == pytest.approx(
        float(np.count_nonzero(protected) / protected.size)
    )
    assert result.diagnostics["returned_safety_strategy"] == ("provider_full_scene_rlasm_pixel_lock")
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
async def test_source_locked_rlasm_reproject_is_never_auto_accepted(monkeypatch):
    request = _request(presentation_mode="reproject", style="isometric")
    beauty, _object_id, _instance_id = _structured_scene()
    provider = beauty.copy().point(lambda value: min(255, value + 17))

    async def _fake_call_openai(self, req, capture, *, server_inventory=None):
        return provider.convert("RGB")

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", _fake_call_openai)
    result = await Direct3DRenderService("test-key").generate(
        request,
        server_inventory=[
            {
                "instance_id": "zone:test-building:building",
                "semantic_class": "building",
                "source_locked_rlasm": True,
            }
        ],
    )

    assert result.outcome == "review_required"
    assert _png_b64(_decoded(result.image_base64)) == _png_b64(provider.convert("RGB"))
    assert result.diagnostics["source_locked_rlasm_pixel_lock_applied"] is False
    assert "cannot be registered" in result.warnings[0]
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


def test_server_inventory_marks_only_server_certified_source_locked_rlasm():
    trusted = SimpleNamespace(
        generation_engine="rlasm",
        specifications={
            "rlasm": {
                "source_locked": True,
                "delivery_sha256": "a" * 64,
            }
        },
    )
    generic = SimpleNamespace(
        generation_engine="lego_assembly",
        specifications={"rlasm": {"source_locked": True}},
    )
    inventory = [
        {"instance_id": "trusted", "building_id": "building-trusted"},
        {"instance_id": "generic", "building_id": "building-generic"},
    ]

    annotated = direct_api._annotate_source_locked_rlasm_inventory(
        inventory,
        {
            "building-trusted": trusted,
            "building-generic": generic,
        },
    )

    assert annotated[0]["source_locked_rlasm"] is True
    assert annotated[0]["rlasm_delivery_sha256"] == "a" * 64
    assert "source_locked_rlasm" not in annotated[1]
    assert "source_locked_rlasm" not in inventory[0]
