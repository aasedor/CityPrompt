"""Fixed scenes bind exact runtime bytes and heading before any paid capture."""

import copy
import json
import math
from pathlib import Path
from types import SimpleNamespace
import uuid

import pytest
from fastapi import HTTPException
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon

from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones
from app.api.v1.lego_assembly import _stamp_community_3d
from app.models.models import SiteZone
from app.services.residual_landscape import community_3d_source_hash


@pytest.fixture(params=["park", "street"])
def fixed_zone(request):
    manifest = json.loads((Path(__file__).parents[1] / "app/data/public_realm_release_20261023.json").read_text())
    row = next(
        row
        for row in manifest["models"]
        if row["category"] == request.param and row["status"] in ("ready", "runtime_trial")
    )
    asset = row["asset"]
    props = copy.deepcopy(asset["properties"])
    props.update(
        pick_place_asset=asset["id"],
        pick_place_model_revision=asset["model"]["revision"],
        pick_place_definition_version=asset["definitionVersion"],
    )
    width, depth = row["fixture"]["dimensions"]
    lng, lat = -114.04, 51.04
    ring = [
        (lng + x / (111320 * math.cos(math.radians(lat))), lat + y / 111320)
        for x, y in [(-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2)]
    ]
    return SiteZone(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type=asset["zoneType"],
        geometry=from_shape(Polygon(ring), srid=4326),
        properties=props,
    )


def stamp_and_claim(zone):
    kind = "park" if zone.zone_type == "green_space" else "street"
    _stamp_community_3d(zone, kind, "2026-10-23T00:00:00Z")
    meta = zone.properties["community_3d"]
    claim = SimpleNamespace(
        zone_id=zone.id,
        source_hash=meta["source_hash"],
        representation_hash=meta["representation_hash"],
        building_id=None,
    )
    return SimpleNamespace(community_3d_claims=[claim], details_revision=None, residual_landscape_claim=None)


def turn_half_circle(zone):
    ring = list(to_shape(zone.geometry).exterior.coords)[:-1]
    zone.geometry = from_shape(Polygon(ring[2:] + ring[:2]), srid=4326)


def test_half_turn_invalidates_fixed_scene_source_and_representation(fixed_zone):
    request = stamp_and_claim(fixed_zone)
    before = dict(fixed_zone.properties["community_3d"])
    turn_half_circle(fixed_zone)
    stamp_and_claim(fixed_zone)
    after = fixed_zone.properties["community_3d"]
    assert after["source_hash"] != before["source_hash"]
    assert after["representation_hash"] != before["representation_hash"]
    assert "public_realm_lego" not in fixed_zone.properties
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)
    assert caught.value.detail["billed"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("pick_place_asset", "claude_public_realm:other:123456789012"),
        ("public_realm_release_asset", "claude_public_realm:other:123456789012"),
        ("pick_place_model_revision", "0" * 64),
        ("native_public_realm_url", "/park-kits/claude-20261023/other.glb"),
        ("pick_place_definition_version", 99),
    ],
)
def test_exact_runtime_identity_changes_invalidate_existing_capture(fixed_zone, field, value):
    request = stamp_and_claim(fixed_zone)
    _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)
    fixed_zone.properties = {**fixed_zone.properties, field: value}
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def test_legacy_public_realm_keeps_its_existing_geometric_normalization(fixed_zone):
    props = {"road_archetype_id": "calgary_local", "road_selected_variant_id": "calgary_local_v0"}
    geometry = to_shape(fixed_zone.geometry)
    original = community_3d_source_hash("road", geometry, props)
    turn_half_circle(fixed_zone)
    assert community_3d_source_hash("road", to_shape(fixed_zone.geometry), props) == original
    assert (
        community_3d_source_hash(
            "road",
            geometry,
            {
                **props,
                "pick_place_asset": "ordinary-legacy-id",
                "pick_place_model_revision": "0" * 64,
                "native_public_realm_url": "/unrelated.glb",
            },
        )
        == original
    )


@pytest.mark.parametrize("approval_state", ["pending_local_trial", "revoked_runtime_review"])
def test_capture_rechecks_current_fixed_release_approval(fixed_zone, monkeypatch, tmp_path, approval_state):
    """A valid old compiled hash does not authorize pending or revoked bytes."""
    from app.core.config import get_settings
    from app.services import fixed_public_realm

    settings = get_settings()
    monkeypatch.setattr(settings, "app_env", "development")
    manifest = json.loads(fixed_public_realm.MANIFEST.read_text(encoding="utf-8"))
    row = next(row for row in manifest["models"] if row["asset"]["id"] == fixed_zone.properties["pick_place_asset"])
    row["status"] = "runtime_trial"
    row["visual_review"]["status"] = "pending"
    row["runtime_review"]["status"] = "pending"
    registry = tmp_path / "release.json"
    registry.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(fixed_public_realm, "MANIFEST", registry)
    request = stamp_and_claim(fixed_zone)
    _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)

    if approval_state == "revoked_runtime_review":
        row["status"] = "ready"
        row["visual_review"].update(status="passed", evidence_sha256="a" * 64, unresolved_p0=0, unresolved_p1=0)
        row["runtime_review"].update(status="passed", evidence_sha256="b" * 64)
        registry.write_text(json.dumps(manifest), encoding="utf-8")
        monkeypatch.setattr(settings, "app_env", "production")
        _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)
        row["runtime_review"]["status"] = "pending"
        registry.write_text(json.dumps(manifest), encoding="utf-8")
    else:
        monkeypatch.setattr(settings, "app_env", "production")

    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [fixed_zone], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False
