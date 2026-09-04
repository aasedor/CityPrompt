"""Live Direct 3D contract: the provider image is normally the product.

Presentation-first keeps source context and measures same-camera scene finishes.
Generative results are review-required; failed checks return the clean capture. Server-certified
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
from app.services.direct_3d_render import (
    Direct3DRenderService,
    prepare_direct_3d_capture,
)

from tests.test_direct_3d_render import (
    _png_b64,
    _request,
    _structured_scene,
    _registration_context_scene,
)


def _decoded(image_b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")


def test_presentation_first_is_the_shipped_default():
    assert direct_service.DIRECT_3D_PRESENTATION_FIRST is True


def _scene_request(**kwargs):
    beauty, mask, building_ids = _structured_scene()
    context, _ = _registration_context_scene()
    beauty.paste(context, mask=Image.fromarray(255 - np.asarray(mask)))
    request = _request(beauty=beauty, mask=mask, **kwargs)
    objects = np.zeros((512, 512, 3), dtype=np.uint8)
    instances = objects.copy()
    active = np.asarray(mask) > 0
    buildings = np.asarray(building_ids)[..., 0] > 0
    objects[active] = (0, 255, 0)
    objects[buildings] = (255, 0, 0)
    instances[active] = (1, 0, 2)
    instances[buildings] = (1, 0, 1)
    payload = request.model_dump()
    payload.update(
        object_id_image_base64=_png_b64(Image.fromarray(objects)),
        object_id_manifest={"#FF0000": "building", "#00FF00": "park"},
        instance_id_image_base64=_png_b64(Image.fromarray(instances)),
        instance_id_manifest={
            "#010001": request.instance_id_manifest["#010001"],
            "#010002": {
                "instance_id": "zone:test-park:park",
                "semantic_class": "park",
                "zone_id": request.community_3d_claims[0].zone_id,
            },
        },
    )
    return request.__class__(**payload)


@pytest.mark.asyncio
@pytest.mark.parametrize("policy", ["precise", "balanced", "expressive"])
async def test_same_camera_finish_has_measured_checks_and_source_context(
    monkeypatch, policy
):
    request = _scene_request(presentation_mode="scene", fidelity_policy=policy)
    capture = prepare_direct_3d_capture(request)
    provider = capture.normalized_beauty.point(lambda v: min(255, v + 17))

    async def fake(self, req, capture, *, server_inventory=None):
        return provider

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", fake)
    result = await Direct3DRenderService("test-key").generate(request)
    assert result.outcome == "review_required"
    assert (
        result.diagnostics["returned_safety_strategy"]
        == "provider_full_scene_local_repairs"
    )
    assert result.diagnostics["registration"] is not None
    assert result.diagnostics["macro_design_fidelity"]["passed"] is True
    assert (
        result.diagnostics["instance_source_presence"]["evaluated_instance_count"] > 0
    )
    assert result.diagnostics["view_lock"] == "camera_registered"
    returned = np.asarray(_decoded(result.image_base64))
    exterior = np.asarray(capture.normalized_proposal_mask) == 0
    assert np.array_equal(
        returned[exterior], np.asarray(capture.normalized_beauty)[exterior]
    )
    assert not np.array_equal(
        returned[~exterior], np.asarray(capture.normalized_beauty)[~exterior]
    )
    assert result.diagnostics["exterior_max_channel_delta"] == 0
    assert (
        hashlib.sha256(base64.b64decode(result.image_base64)).hexdigest()
        == result.output_fingerprint
    )
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["missing-building", "blank", "new-tower"])
async def test_redesigned_candidate_returns_clean_source_and_retains_provider(
    monkeypatch, failure
):
    from PIL import ImageDraw

    request = _scene_request(presentation_mode="scene")
    capture = prepare_direct_3d_capture(request)
    provider = capture.normalized_beauty.copy()
    scale = provider.width / 512
    draw = ImageDraw.Draw(provider)
    if failure == "blank":
        provider = Image.new("RGB", provider.size, "white")
    elif failure == "missing-building":
        draw.rectangle(
            tuple(round(v * scale) for v in (75, 72, 231, 250)), fill=(126, 142, 116)
        )
    else:
        draw.rectangle(
            tuple(round(v * scale) for v in (231, 120, 278, 390)),
            fill="black",
            outline="white",
            width=5,
        )

    async def fake(self, req, prepared, *, server_inventory=None):
        return provider

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", fake)
    result = await Direct3DRenderService("test-key").generate(request)
    assert result.outcome == "review_required"
    assert result.diagnostics["returned_safety_strategy"] == "authoritative_source"
    assert result.diagnostics["view_lock"] == "source_pixel_locked"
    assert _png_b64(_decoded(result.image_base64)) == _png_b64(
        capture.normalized_beauty
    )
    assert result.provider_image_base64 == _png_b64(provider)
    assert "Clean 3D source" in result.warnings[0]
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
@pytest.mark.parametrize("blank", [False, True])
async def test_reproject_has_no_false_registration_or_auto_acceptance(
    monkeypatch, blank
):
    request = _scene_request(presentation_mode="reproject", style="isometric")
    capture = prepare_direct_3d_capture(request)
    provider = (
        Image.new("RGB", capture.normalized_beauty.size, "white")
        if blank
        else capture.normalized_beauty.point(lambda v: min(255, v + 17))
    )

    async def fake(self, req, prepared, *, server_inventory=None):
        return provider

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", fake)
    result = await Direct3DRenderService("test-key").generate(request)
    assert result.outcome == "review_required"
    assert result.diagnostics["registration"] is None
    assert result.diagnostics["reproject_output_sanity"]["passed"] is (not blank)
    expected = capture.normalized_beauty if blank else provider
    assert _png_b64(_decoded(result.image_base64)) == _png_b64(expected)
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
async def test_source_locked_rlasm_scene_restores_exact_instance_pixels(monkeypatch):
    request = _scene_request(presentation_mode="scene", style="photorealistic")
    capture = prepare_direct_3d_capture(request)
    provider = capture.normalized_beauty.copy().point(
        lambda value: min(255, value + 29)
    )

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
    instance_pixels = np.asarray(capture.normalized_instance_id.convert("RGB"))
    protected = np.all(instance_pixels == np.asarray((1, 0, 1), dtype=np.uint8), axis=2)

    assert result.outcome == "review_required"
    assert np.array_equal(returned[protected], source[protected])
    exterior = np.asarray(capture.normalized_proposal_mask) == 0
    assert np.array_equal(returned[exterior], source[exterior])
    assert result.diagnostics["source_locked_rlasm_instance_count"] == 1
    assert result.diagnostics["source_locked_rlasm_pixel_lock_applied"] is True
    assert result.diagnostics["source_locked_rlasm_pixel_coverage"] == pytest.approx(
        float(np.count_nonzero(protected) / protected.size)
    )
    assert result.diagnostics["returned_safety_strategy"] == (
        "provider_full_scene_rlasm_pixel_lock"
    )
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
async def test_source_locked_rlasm_reproject_is_never_auto_accepted(monkeypatch):
    request = _scene_request(presentation_mode="reproject", style="isometric")
    provider = prepare_direct_3d_capture(request).normalized_beauty.point(
        lambda value: min(255, value + 17)
    )

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


@pytest.mark.asyncio
async def test_street_provider_content_failure_keeps_street_source_camera(monkeypatch):
    request = _scene_request(presentation_mode="scene").model_copy(update={"view_mode": "street"})
    capture = prepare_direct_3d_capture(request)

    async def fake(self, req, prepared, *, server_inventory=None):
        return Image.new("RGB", prepared.normalized_beauty.size, "white")

    monkeypatch.setattr(Direct3DRenderService, "_call_openai", fake)
    result = await Direct3DRenderService("test-key").generate(request)
    assert result.diagnostics["returned_safety_strategy"] == "authoritative_source"
    assert result.diagnostics["reproject_output_sanity"]["passed"] is False
    assert _png_b64(_decoded(result.image_base64)) == _png_b64(capture.normalized_beauty)
    assert "street-level" in result.warnings[0]
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)
