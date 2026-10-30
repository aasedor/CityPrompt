import copy
import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from app.services.fixed_public_realm import validate_fixed_public_realm

MANIFEST = Path(__file__).resolve().parents[1] / "app/data/public_realm_release_20261023.json"


def fixture(*, pending=False):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = next(
        row for row in manifest["models"] if row["candidate"] == "clay-ice-rink-market-square-clay-v007-park-only-r001"
    )
    if pending:
        row["status"] = "runtime_trial"
        row["visual_review"]["status"] = "pending"
        row["runtime_review"]["status"] = "pending"
    asset = row["asset"]
    properties = copy.deepcopy(asset["properties"])
    properties.update(
        pick_place_asset=asset["id"],
        pick_place_model_revision=asset["model"]["revision"],
        pick_place_definition_version=asset["definitionVersion"],
    )
    lng, lat, yaw = -114.04, 51.04, 0.37
    width, depth = row["fixture"]["dimensions"]
    ring = [
        (
            lng + (x * math.cos(yaw) - y * math.sin(yaw)) / (111320 * math.cos(math.radians(lat))),
            lat + (x * math.sin(yaw) + y * math.cos(yaw)) / 111320,
        )
        for x, y in [(-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2)]
    ]
    return manifest, row, properties, Polygon(ring)


def approve(row):
    row["status"] = "ready"
    row["visual_review"].update(status="passed", evidence_sha256="a" * 64, unresolved_p0=0, unresolved_p1=0)
    row["runtime_review"].update(status="passed", evidence_sha256="b" * 64)


def test_manifests_are_synchronized():
    frontend = MANIFEST.parents[3] / "frontend/src/data/publicRealmRelease20261023.json"
    assert json.loads(frontend.read_text(encoding="utf-8")) == json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_compact_crossing_ownership_is_pinned_independently_of_saved_claims():
    from app.services.fixed_public_realm import release_gate_errors

    frontend = MANIFEST.parents[3] / "frontend/src/data/publicRealmRelease20261023.json"
    row = next(
        row
        for row in json.loads(frontend.read_text(encoding="utf-8"))["models"]
        if row["candidate"] == "clay-barcelona-passatge-clay-v006"
    )
    assert "identity_mismatch" not in release_gate_errors(row)
    row["fixture"]["ownershipSha256"] = "0" * 64
    row["asset"]["properties"]["public_realm_ownership_sha256"] = "0" * 64
    assert "identity_mismatch" in release_gate_errors(row)


def test_exact_browser_scene_stamp_removes_legacy_family_pending_fallback(monkeypatch):
    from types import SimpleNamespace
    from geoalchemy2 import WKTElement
    from app.core.config import get_settings
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone, _stamp_community_3d

    monkeypatch.setattr(get_settings(), "app_env", "development")
    _, row, props, polygon = fixture()
    props["public_realm_fallback"] = {
        "schema_version": 1,
        "state": "family_pending",
        "kind": "park",
        "generator": "park_kit",
        "archetype_id": "outdoor_ice_rink",
        "variant_id": "outdoor_ice_rink_v0",
        "target_source": "zone_geometry",
    }
    zone = SimpleNamespace(
        id="actual-rink", zone_type="green_space", properties=props, geometry=WKTElement(polygon.wkt, srid=4326)
    )
    recipe = _public_realm_recipe_for_zone(zone, "park")
    assert recipe is None  # Exact browser-mounted native scene, not a procedural recipe.
    _stamp_community_3d(zone, "park", "2026-10-23T00:00:00Z", public_realm_recipe=recipe)
    assert "public_realm_fallback" not in zone.properties
    assert "public_realm_lego" not in zone.properties
    assert zone.properties["native_public_realm_url"] == row["fixture"]["url"]
    assert zone.properties["community_3d"]["state"] == "compiled"


@pytest.mark.parametrize(
    "field,value", [("native_public_realm_url", "/forged.glb"), ("pick_place_model_revision", "0" * 64)]
)
def test_stamp_never_exempts_a_forged_fixed_claim_from_fallback_validation(monkeypatch, field, value):
    from types import SimpleNamespace
    from geoalchemy2 import WKTElement
    from fastapi import HTTPException
    from app.core.config import get_settings
    from app.api.v1.lego_assembly import _stamp_community_3d

    monkeypatch.setattr(get_settings(), "app_env", "development")
    _, _, props, polygon = fixture()
    props[field] = value
    zone = SimpleNamespace(
        id="forged-rink", zone_type="green_space", properties=props, geometry=WKTElement(polygon.wkt, srid=4326)
    )
    with pytest.raises(HTTPException) as caught:
        _stamp_community_3d(zone, "park", "2026-10-23T00:00:00Z")
    assert caught.value.status_code == 422
    assert caught.value.detail["code"] == "fixed_public_realm_incompatible"


@pytest.mark.parametrize(
    "candidate", ["clay-halifax-public-gardens-clay-v005-park-only-r001", "clay-princes-island-park-clay-v005"]
)
def test_raw_claim_remains_disabled_and_never_substitutes_optimized_bytes(monkeypatch, candidate):
    from app.core.config import get_settings

    manifest, _, _, polygon = fixture()
    raw = next(row for row in manifest["models"] if row["candidate"] == candidate)
    optimized = next(row for row in manifest["models"] if row["candidate"] == raw["candidate"] + "-gpu-r001")
    assert raw["status"] == "prepared"
    assert optimized["status"] == "ready"
    assert raw["asset"]["id"] != optimized["asset"]["id"]
    assert raw["fixture"]["url"] != optimized["fixture"]["url"]
    assert raw["source_sha256"] == optimized["source_sha256"]
    properties = {
        **raw["asset"]["properties"],
        "pick_place_asset": raw["asset"]["id"],
        "pick_place_model_revision": raw["runtime_sha256"],
        "pick_place_definition_version": raw["asset"]["definitionVersion"],
    }
    monkeypatch.setattr(get_settings(), "app_env", "development")
    with pytest.raises(ValueError, match="review"):
        validate_fixed_public_realm("green_space", polygon, properties, manifest=manifest)
    properties.update(
        native_public_realm_url=optimized["fixture"]["url"], pick_place_model_revision=optimized["runtime_sha256"]
    )
    with pytest.raises(ValueError):
        validate_fixed_public_realm("green_space", polygon, properties, manifest=manifest)


def test_local_runtime_pilot_has_no_production_authority(monkeypatch):
    from app.core.config import get_settings

    manifest, row, props, polygon = fixture(pending=True)
    monkeypatch.setattr(get_settings(), "app_env", "development")
    assert validate_fixed_public_realm("green_space", polygon, props, manifest=manifest)
    monkeypatch.setattr(get_settings(), "app_env", "production")
    with pytest.raises(ValueError, match="review"):
        validate_fixed_public_realm("green_space", polygon, props, manifest=manifest)
    approve(row)
    assert validate_fixed_public_realm("green_space", polygon, props, manifest=manifest)
    row["visual_review"]["runtime_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="review"):
        validate_fixed_public_realm("green_space", polygon, props, manifest=manifest)


@pytest.mark.parametrize(
    "field,value",
    [
        ("pick_place_model_revision", "0" * 64),
        ("native_public_realm_url", "/other.glb"),
        ("public_realm_release_asset", "unknown"),
        ("green_space_selected_variant_id", "other"),
        ("validation_fixed_fixture", True),
        ("public_realm_trial_asset", "claude_trial_wrong"),
        ("pick_place_asset", "unknown"),
        ("pick_place_definition_version", 99),
        ("_plan_scenario", "ai"),
    ],
)
def test_identity_mismatch_is_rejected(monkeypatch, field, value):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "development")
    manifest, _, props, polygon = fixture()
    props[field] = value
    with pytest.raises(ValueError):
        validate_fixed_public_realm("green_space", polygon, props, manifest=manifest)


def test_no_stretching_holes_or_generic_fallback(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "development")
    manifest, _, props, polygon = fixture()
    ring = list(polygon.exterior.coords)
    ring[0] = (ring[0][0] + 0.0001, ring[0][1])
    with pytest.raises(ValueError, match="native"):
        validate_fixed_public_realm("green_space", Polygon(ring), props, manifest=manifest)
    with pytest.raises(ValueError):
        validate_fixed_public_realm("road", polygon, props, manifest=manifest)
    assert validate_fixed_public_realm("green_space", polygon, {}, manifest=manifest) is False


def test_compiler_dispatch_rejects_pending_production_and_does_not_substitute(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from geoalchemy2 import WKTElement
    from fastapi import HTTPException
    from app.core.config import get_settings
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone
    from app.services import fixed_public_realm

    manifest, _, props, polygon = fixture(pending=True)
    registry = tmp_path / "pending-release.json"
    registry.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(fixed_public_realm, "MANIFEST", registry)
    zone = SimpleNamespace(
        id="fixed-scene", zone_type="green_space", properties=props, geometry=WKTElement(polygon.wkt, srid=4326)
    )
    monkeypatch.setattr(get_settings(), "app_env", "development")
    assert _public_realm_recipe_for_zone(zone, "park") is None
    monkeypatch.setattr(get_settings(), "app_env", "production")
    with pytest.raises(HTTPException) as caught:
        _public_realm_recipe_for_zone(zone, "park")
    assert caught.value.detail["code"] == "fixed_public_realm_incompatible"
