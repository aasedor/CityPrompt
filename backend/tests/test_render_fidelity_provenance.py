import copy
import io
import json
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock

import numpy as np
import pytest
from PIL import Image
from shapely.geometry import box

from app.api.v1 import render as render_api
from app.schemas.direct_3d_render import Direct3DCameraManifest
from app.services.direct_3d_render import (
    _instance_presence_diagnostics,
    _presentation_prompt,
    assess_instance_source_presence,
    assess_macro_design_fidelity,
    prepare_direct_3d_capture,
)
from app.services.render_fidelity import (
    RENDER_PRESERVATION_LOCK,
    append_render_preservation_lock,
)
from app.services.render_provenance import build_render_source_snapshot
from tests.test_direct_3d_render import TEST_ZONE_ID, _png_b64, _request


def _snapshot_inputs():
    request = _request()
    zone = SimpleNamespace(
        id=TEST_ZONE_ID,
        zone_type="building",
        geometry=box(-114.1, 51, -114.09, 51.01),
        properties={"_plan_scenario": "A", "height": 12},
        building_id="building-1",
    )
    building = SimpleNamespace(
        id="building-1",
        footprint=zone.geometry,
        height_meters=12,
        floor_count=4,
        specifications={"source": "chosen archetype"},
    )
    camera = Direct3DCameraManifest(
        projection="perspective",
        projection_matrix=np.eye(4).flatten().tolist(),
        matrix_world=np.eye(4).flatten().tolist(),
        position=(1, 2, 3),
        quaternion=(0, 0, 0, 1),
    )
    request = request.model_copy(update={"camera": camera})
    return request, zone, building


def test_snapshot_tracks_actual_plan_scenario_and_camera_without_mutable_references():
    request, zone, building = _snapshot_inputs()
    initial = build_render_source_snapshot(
        request, [zone], [building], captured_at="first"
    )
    assert initial["plan_evidence"] == "server_project_state_after_claim_validation"
    assert initial["camera_evidence"] == "validated_client_capture_manifest"
    same = build_render_source_snapshot(
        request, [zone], [building], captured_at="later"
    )
    assert initial["plan_revision_sha256"] == same["plan_revision_sha256"]
    zone.properties["_plan_scenario"] = "B"
    changed = build_render_source_snapshot(
        request, [zone], [building], captured_at="later"
    )
    assert initial["plan"]["zones"][0]["properties"]["_plan_scenario"] == "A"
    assert initial["plan_revision_sha256"] != changed["plan_revision_sha256"]
    building.height_meters = 22
    raised = build_render_source_snapshot(
        request, [zone], [building], captured_at="later"
    )
    assert raised["plan_revision_sha256"] != changed["plan_revision_sha256"]
    camera_before = raised["camera_revision_sha256"]
    request.camera.position = (2, 2, 3)
    moved = build_render_source_snapshot(
        request, [zone], [building], captured_at="later"
    )
    assert moved["camera_revision_sha256"] != camera_before
    assert moved["plan_revision_sha256"] == raised["plan_revision_sha256"]


def test_missing_camera_or_visible_edges_do_not_claim_positive_evidence():
    request, zone, building = _snapshot_inputs()
    request.camera = None
    snapshot = build_render_source_snapshot(
        request, [zone], [building], captured_at="now"
    )
    assert snapshot["camera_revision_sha256"] is None
    assert snapshot["camera_evidence"] == "not_supplied"
    blank = Image.new("RGB", (64, 64), "white")
    mask = Image.new("L", blank.size, 255)
    macro = assess_macro_design_fidelity(blank, blank, mask)
    assert macro.passed is False
    assert macro.coarse_edge_recall == 0
    result = assess_instance_source_presence(
        blank, blank, mask, None, None, fidelity_policy="balanced"
    )
    diagnostics = _instance_presence_diagnostics(result)
    assert diagnostics["passed"] is None
    assert diagnostics["status"] == "not_evaluated"


def test_occluded_instance_remains_unevaluated_without_moving_or_failing_it():
    request = _request(presentation_mode="scene")
    capture = prepare_direct_3d_capture(request)
    descriptor = next(iter(request.instance_id_manifest.values()))
    hidden = descriptor.model_copy(update={"instance_id": "hidden-building"})
    result = assess_instance_source_presence(
        capture.normalized_beauty,
        capture.normalized_beauty,
        capture.normalized_proposal_mask,
        capture.normalized_instance_id,
        {**request.instance_id_manifest, "#020202": hidden},
        fidelity_policy="balanced",
    )
    assert result.instance_recalls["hidden-building"] is None
    assert "hidden-building" not in result.missing_instance_ids


def test_custom_art_direction_cannot_truncate_geometry_and_occlusion_lock():
    conflicting = "Add a tower, move the hidden houses into view. " * 1000
    bounded = append_render_preservation_lock(conflicting)
    assert len(bounded) <= 32000
    assert bounded.endswith(RENDER_PRESERVATION_LOCK)
    assert "cafe seating" in bounded
    prompt = _presentation_prompt(
        conflicting,
        presentation_mode="scene",
        style="photorealistic",
        object_id_manifest=None,
    )
    assert len(prompt) <= 32000
    assert prompt.endswith(RENDER_PRESERVATION_LOCK)


@pytest.mark.asyncio
async def test_gallery_sidecar_embeds_server_snapshot_and_dedupes_by_source_revision(
    monkeypatch,
):
    request, zone, building = _snapshot_inputs()
    snapshot = build_render_source_snapshot(
        request, [zone], [building], captured_at="now"
    )
    original_snapshot = copy.deepcopy(snapshot)
    project = SimpleNamespace(metadata_={})
    db = SimpleNamespace(
        execute=AsyncMock(
            return_value=SimpleNamespace(scalar_one_or_none=lambda: project)
        ),
        commit=AsyncMock(),
    )
    uploads = {}

    async def upload(key, content, kind):
        uploads[key] = (content, kind)

    monkeypatch.setattr("app.api.v1.documents._upload_to_storage", upload)
    save = render_api.SaveRenderRequest(
        image_base64=_png_b64(Image.new("RGB", (256, 256), "green")),
        prompt="cafe activity",
        source_snapshot={"forged": True},
        outcome="accepted",
        presentation_strategy="authoritative_source",
        capture_fingerprint="forged",
    )
    assert "source_snapshot" not in save.model_dump()
    assert "presentation_strategy" not in save.model_dump()
    result = await render_api.persist_render_to_gallery(
        db,
        request.project_id,
        save,
        variant="final",
        outcome="review_required",
        presentation_strategy="authoritative_source",
        source_snapshot=snapshot,
        capture_fingerprint="c" * 64,
        output_fingerprint="d" * 64,
    )
    sidecar = next(
        json.loads(data)
        for key, (data, kind) in uploads.items()
        if kind == "application/json"
    )
    assert sidecar["source_snapshot"] == original_snapshot
    assert sidecar["outcome"] == "review_required"
    assert sidecar["presentation_strategy"] == "authoritative_source"
    assert sidecar["capture_fingerprint"] == "c" * 64
    png = next(data for _, (data, kind) in uploads.items() if kind == "image/png")
    embedded = json.loads(Image.open(io.BytesIO(png)).info["cityprompt:provenance"])
    assert (
        embedded["source"]["plan_revision_sha256"] == snapshot["plan_revision_sha256"]
    )
    assert embedded["source"]["outcome"] == "review_required"
    assert embedded["source"]["presentation_strategy"] == "authoritative_source"
    assert result.provenance_url.endswith(".provenance.json")
    zone.properties["height"] = 18
    changed = build_render_source_snapshot(
        request, [zone], [building], captured_at="later"
    )
    second = await render_api.persist_render_to_gallery(
        db,
        request.project_id,
        save,
        variant="final",
        outcome="review_required",
        source_snapshot=changed,
        capture_fingerprint="c" * 64,
        output_fingerprint="d" * 64,
    )
    assert second.id != result.id
    assert len(project.metadata_["saved_renders"]) == 2
    manual = await render_api.persist_render_to_gallery(db, request.project_id, save)
    assert manual.plan_revision_sha256 is None
    assert manual.capture_fingerprint is None
    assert manual.outcome is None
    assert manual.presentation_strategy is None


@pytest.mark.asyncio
@pytest.mark.parametrize("changed_field", [
    "outcome", "presentation_strategy", "camera_revision_sha256",
    "scene_revision_sha256", "output_fingerprint", "style",
])
async def test_identical_gallery_pixels_do_not_reuse_a_different_result_or_provenance(
    monkeypatch, changed_field,
):
    request, zone, building = _snapshot_inputs()
    snapshot = build_render_source_snapshot(request, [zone], [building], captured_at="now")
    project = SimpleNamespace(metadata_={})
    db = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: project)),
        commit=AsyncMock(),
    )
    upload = AsyncMock()
    monkeypatch.setattr("app.api.v1.documents._upload_to_storage", upload)
    save = render_api.SaveRenderRequest(
        image_base64=_png_b64(Image.new("RGB", (256, 256), "green")),
        prompt="cafe activity", style="photorealistic", model="gpt-image-2", image_quality="high",
    )
    initial = {
        "variant": "final", "outcome": "review_required",
        "presentation_strategy": "provider_full_scene_local_repairs",
        "source_snapshot": snapshot, "scene_revision_sha256": "a" * 64,
        "capture_fingerprint": "b" * 64, "output_fingerprint": "c" * 64,
    }
    first = await render_api.persist_render_to_gallery(db, request.project_id, save, **initial)
    old_entry = copy.deepcopy(project.metadata_["saved_renders"][0])
    changed = copy.deepcopy(initial)
    if changed_field == "camera_revision_sha256":
        changed["source_snapshot"][changed_field] = "f" * 64
    elif changed_field == "style":
        save = save.model_copy(update={"style": "watercolor"})
    else:
        changed[changed_field] = {
            "outcome": "accepted", "presentation_strategy": "authoritative_source",
        }.get(changed_field, "f" * 64)
    second = await render_api.persist_render_to_gallery(db, request.project_id, save, **changed)
    assert second.id != first.id
    assert project.metadata_["saved_renders"][1] == old_entry
    assert second.outcome == changed["outcome"]
    assert second.presentation_strategy == changed["presentation_strategy"]
    assert second.provenance_url != first.provenance_url
    # A retry of the same complete result can reuse its own immutable artifact.
    retry = await render_api.persist_render_to_gallery(db, request.project_id, save, **changed)
    assert retry.id == second.id
    assert len(project.metadata_["saved_renders"]) == 2
    assert upload.await_count == 4


def test_legacy_compound_gallery_outcome_is_normalized_without_mutating_history():
    existing = {
        "id": "old", "image_url": "/files/old.png", "prompt": "finish", "created_at": "then",
        "outcome": "review_required · authoritative_source",
    }
    parsed = render_api.SavedRenderResponse(**existing)
    assert parsed.outcome == "review_required"
    assert parsed.presentation_strategy == "authoritative_source"
    assert existing["outcome"] == "review_required · authoritative_source"
    explicit = render_api.SavedRenderResponse(**{**existing, "presentation_strategy": "provider_original"})
    assert explicit.presentation_strategy == "provider_original"


@pytest.mark.asyncio
@pytest.mark.parametrize("source_fallback", [False, True])
async def test_direct_endpoint_freezes_server_plan_before_provider_and_returns_saved_entry(monkeypatch, source_fallback):
    from app.api.v1 import direct_3d_render as endpoint
    from app.services.direct_3d_render import Direct3DRenderService
    from tests.test_direct_3d_render import _fake_service_result

    request, zone, building = _snapshot_inputs()
    db = SimpleNamespace(execute=AsyncMock(side_effect=[
        SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [zone])),
        SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [building])),
    ]))
    monkeypatch.setattr(endpoint, "check_project_permission", AsyncMock())
    monkeypatch.setattr(endpoint, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(endpoint, "_validate_direct_3d_project_zones", lambda *_: [])
    monkeypatch.setattr(endpoint, "get_settings", lambda: SimpleNamespace(openai_api_key="fake", render_global_daily_token_cap=0))
    monkeypatch.setattr(endpoint, "_reserve_direct_render", AsyncMock(return_value=SimpleNamespace(id="reservation")))
    monkeypatch.setattr(endpoint, "_finalize_direct_audit", AsyncMock())
    entry = render_api.SavedRenderResponse(id="saved-source", image_url="/files/saved.png", prompt="finish", created_at="now")
    save = AsyncMock(return_value=entry)
    monkeypatch.setattr(endpoint, "persist_render_to_gallery", save)

    async def generate(self, req, capture, **kwargs):
        zone.properties["height"] = 99
        result = _fake_service_result(capture.audit_input_base64)
        if source_fallback:
            return replace(
                result, outcome="review_required",
                diagnostics={**result.diagnostics, "returned_safety_strategy": "authoritative_source"},
                provider_image_base64=_png_b64(Image.new("RGB", (2, 2), "red")),
            )
        return result

    monkeypatch.setattr(Direct3DRenderService, "generate", generate)
    result = await endpoint.generate_direct_3d_render(request, user=SimpleNamespace(id="user"), db=db)
    provenance = save.await_args_list[0].kwargs
    assert provenance["source_snapshot"]["plan"]["zones"][0]["properties"]["height"] == 12
    assert provenance["capture_fingerprint"] == result.capture_fingerprint
    assert provenance["output_fingerprint"] == result.output_fingerprint
    assert provenance["scene_revision_sha256"]
    assert result.saved_render.id == "saved-source"
    assert provenance["outcome"] == result.outcome
    assert provenance["presentation_strategy"] == ("authoritative_source" if source_fallback else None)
    if source_fallback:
        assert result.provider_original_render.id == "saved-source"
        original = save.await_args_list[1].kwargs
        assert original["outcome"] == "review_required"
        assert original["presentation_strategy"] == "provider_original"
    else:
        assert result.provider_original_render is None
