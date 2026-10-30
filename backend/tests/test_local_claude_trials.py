import copy
import json
import math
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from geoalchemy2 import WKTElement
from shapely.geometry import Polygon

from app.api.v1.lego_assembly import _public_realm_recipe_for_zone

MANIFEST = Path(__file__).resolve().parents[2] / "frontend/src/data/claudeAssetLocalTrial.json"


def fixture():
    row = next(
        r for r in json.loads(MANIFEST.read_text())["models"] if r["category"] == "park" and not r.get("retired")
    )
    props = copy.deepcopy(row["asset"]["properties"])
    props.update(pick_place_asset=row["asset"]["id"], pick_place_model_revision=row["asset"]["model"]["revision"])
    lng, lat = -114.04, 51.04
    width, depth = row["fixture"]["dimensions"]
    yaw = 0.37
    ring = [
        [
            lng + (x * math.cos(yaw) - y * math.sin(yaw)) / (111320 * math.cos(math.radians(lat))),
            lat + (x * math.sin(yaw) + y * math.cos(yaw)) / 111320,
        ]
        for x, y in [(-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2)]
    ]
    return (
        SimpleNamespace(
            id=uuid.uuid4(),
            zone_type="green_space",
            properties=props,
            geometry=WKTElement(Polygon(ring).wkt, srid=4326),
        ),
        ring,
    )


def test_exact_local_fixed_park_compiles_without_substituting_a_generic_park(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "development")
    zone, _ = fixture()
    assert _public_realm_recipe_for_zone(zone, "park") is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("pick_place_model_revision", "0" * 64),
        ("validation_native_url", "/different.glb"),
        ("public_realm_trial_asset", "unregistered"),
        ("green_space_selected_variant_id", "wrong"),
        ("validation_fixed_fixture", False),
        ("pick_place_asset", "unregistered"),
    ],
)
def test_local_trial_rejects_mismatched_identity(monkeypatch, field, value):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "development")
    zone, _ = fixture()
    zone.properties[field] = value
    with pytest.raises(HTTPException):
        _public_realm_recipe_for_zone(zone, "park")


def test_local_trial_rejects_stretching_and_ai_planner_claim(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "development")
    zone, ring = fixture()
    ring[0][0] += 0.0001
    zone.geometry = WKTElement(Polygon(ring).wkt, srid=4326)
    with pytest.raises(HTTPException):
        _public_realm_recipe_for_zone(zone, "park")
    zone, _ = fixture()
    zone.properties["_plan_scenario"] = "not-a-validated-executable-family"
    with pytest.raises(HTTPException):
        _public_realm_recipe_for_zone(zone, "park")


def test_production_does_not_trust_local_fixture_manifest(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "app_env", "production")
    zone, _ = fixture()
    with pytest.raises(HTTPException):
        _public_realm_recipe_for_zone(zone, "park")
