"""The modular bridge remains a locked native recipe, never an at-grade road."""

import copy
import hashlib
import json
import math
from types import SimpleNamespace
import uuid
from pathlib import Path

import pytest

from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
from app.services.native_specialist_streets import validate_specialist_ground, validate_specialist_properties
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    PublicRealmPlanningError,
    StreetSegmentTarget,
    plan_public_realm_recipe,
    public_realm_recipe_hash,
    public_realm_recipe_identity,
    plan_public_realm_zone_recipe,
    build_public_realm_capability_catalog,
    public_realm_fallback_marker,
)


VARIANT = "timber_covered_bridge_route_v1"
PARENT = "urban_pedestrian_footbridge"
MODULES = ("bridge_left_stair", "bridge_left_end", "bridge_bay", "bridge_right_end", "bridge_right_stair")


def bridge_row():
    program = {
        "adapter": "modular-bridge-v1",
        "minLengthM": 32,
        "maxLengthM": 240,
        "baseLiftM": 0,
        "bridge": {"approachM": 4, "endM": 3, "bayM": 6, "deckHeightM": 2.4, "clearWidthM": 4.2},
        "surfaceRegions": [],
    }
    return {
        "id": VARIANT,
        "sourceArchetypeId": PARENT,
        "title": "Timber Covered Bridge Route",
        "status": "candidate",
        "sourceRecipeSha256": "1" * 64,
        "sourceAssemblySha256": "2" * 64,
        "referenceSha256": "3" * 64,
        "programSha256": hashlib.sha256(
            json.dumps(program, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "widthM": 6,
        "fixtureLengthM": 48,
        "routeAxis": "local_y",
        "junctionSurface": "pavers",
        "sections": [{"name": "bridge_walk", "x": 0, "width": 6, "material": "timber"}],
        "placements": [],
        "modules": {
            kind: {"url": f"/street-kits/pilots/{VARIANT}/{kind}.glb", "sha256": str(index + 4) * 64}
            for index, kind in enumerate(MODULES)
        },
        "program": program,
    }


def write_catalog(tmp_path, row):
    manifest = tmp_path / "pilots.json"
    manifest.write_text(json.dumps([row]), encoding="utf-8")
    return build_native_street_candidate_catalog(manifest)


def test_native_registry_includes_the_separate_bridge_supplement(tmp_path):
    source = Path(__file__).resolve().parents[1] / "app/data/nativeStreetPilots.json"
    old_row = json.loads(source.read_text(encoding="utf-8"))[0]
    (tmp_path / "nativeStreetPilots.json").write_text(json.dumps([old_row]), encoding="utf-8")
    (tmp_path / "nativeBridgePilots.json").write_text(json.dumps([bridge_row()]), encoding="utf-8")
    catalog = build_native_street_candidate_catalog(tmp_path / "nativeStreetPilots.json")
    assert {selection.variant_id for capability in catalog.capabilities for selection in capability.selections} == {
        old_row["id"],
        VARIANT,
    }


def test_pending_bridge_explicit_recipe_stays_outside_ai_planning_vocabulary():
    catalog = build_public_realm_capability_catalog()
    assert VARIANT in catalog.variants_by_archetype[PARENT]
    assert VARIANT not in catalog.prompt_vocabulary
    assert "student_main_street_v1" in catalog.prompt_vocabulary


def test_modular_bridge_never_has_an_ordinary_procedural_street_fallback():
    assert public_realm_fallback_marker("road", route_properties()) is None


def test_modular_bridge_recipe_obeys_its_finite_program_envelope(tmp_path):
    catalog = write_catalog(tmp_path, bridge_row())
    for length in (32, 45, 80, 150, 240):
        recipe = plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=PARENT, variant_id=VARIANT, target=StreetSegmentTarget(row_width_m=6, length_m=length)
            ),
            catalog=catalog,
        )
        assert public_realm_recipe_identity(recipe, catalog=catalog)["recipe"]["target"]["length_m"] == length
        assert len(recipe.component_set_ids) == 9
    for length in (31, 241):
        with pytest.raises(PublicRealmPlanningError):
            plan_public_realm_recipe(
                PublicRealmPlanRequest(
                    archetype_id=PARENT, variant_id=VARIANT, target=StreetSegmentTarget(row_width_m=6, length_m=length)
                ),
                catalog=catalog,
            )
    for width in (5.99, 6.01):
        with pytest.raises(PublicRealmPlanningError):
            plan_public_realm_recipe(
                PublicRealmPlanRequest(
                    archetype_id=PARENT, variant_id=VARIANT, target=StreetSegmentTarget(row_width_m=width, length_m=80)
                ),
                catalog=catalog,
            )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update(id="unknown_modular_bridge"),
        lambda row: row.update(sourceArchetypeId="landmark_signature_bridge"),
        lambda row: row["modules"].pop("bridge_left_stair"),
        lambda row: row["program"].update(surfaceRegions=[{"material": "pavers"}]),
        lambda row: row["program"]["bridge"].update(bayM=0),
        lambda row: row["program"]["bridge"].update(clearWidthM=7),
        lambda row: row["program"].update(minLengthM=8),
    ],
)
def test_modular_bridge_manifest_rejects_unsupported_structural_contract(tmp_path, mutation):
    row = bridge_row()
    mutation(row)
    row["programSha256"] = hashlib.sha256(
        json.dumps(row["program"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ValueError):
        write_catalog(tmp_path, row)


@pytest.mark.parametrize("lock", ["source_recipe", "source_assembly", "program", "module_bridge_bay"])
def test_modular_bridge_cannot_bless_tampered_locks_by_rehashing_recipe(tmp_path, lock):
    catalog = write_catalog(tmp_path, bridge_row())
    recipe = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id=PARENT, variant_id=VARIANT, target=StreetSegmentTarget(row_width_m=6, length_m=80)
        ),
        catalog=catalog,
    ).model_dump(mode="json")
    recipe["component_set_ids"] = [
        f"{lock}:{'a' * 64}" if item.startswith(f"{lock}:") else item for item in recipe["component_set_ids"]
    ]
    recipe["recipe_hash"] = public_realm_recipe_hash(recipe)
    assert public_realm_recipe_identity(recipe, catalog=catalog) is None


def test_modular_bridge_stale_program_recipe_is_rejected(tmp_path):
    row = bridge_row()
    old_catalog = write_catalog(tmp_path, row)
    old_recipe = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id=PARENT, variant_id=VARIANT, target=StreetSegmentTarget(row_width_m=6, length_m=80)
        ),
        catalog=old_catalog,
    )
    changed = copy.deepcopy(row)
    changed["program"]["bridge"]["deckHeightM"] = 2.6
    changed["programSha256"] = hashlib.sha256(
        json.dumps(changed["program"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert public_realm_recipe_identity(old_recipe, catalog=write_catalog(tmp_path, changed)) is None


@pytest.fixture
def bridge_profile(tmp_path, monkeypatch):
    from app.services import native_modular_bridge

    manifest = tmp_path / "nativeStreetPilots.json"
    manifest.write_text(json.dumps([bridge_row()]), encoding="utf-8")
    monkeypatch.setattr(native_modular_bridge, "MANIFEST", manifest)
    native_modular_bridge.modular_bridge_profiles.cache_clear()
    yield
    native_modular_bridge.modular_bridge_profiles.cache_clear()


def route_properties(length=80):
    return {
        "road_selected_variant_id": VARIANT,
        "road_archetype_id": PARENT,
        "width": 6,
        "lane_count": 0,
        "plan_centerline": [[0, 0], [0, length / 111320]],
    }


@pytest.mark.parametrize("length", [32, 45, 80, 150, 240])
def test_modular_bridge_accepts_complete_finite_two_endpoint_routes(bridge_profile, length):
    properties = route_properties(length)
    validate_specialist_properties(properties)
    properties["plan_centerline"].reverse()
    validate_specialist_properties(properties)
    properties["plan_centerline"] = [[0, 0], [length / 111320 / 2**0.5, length / 111320 / 2**0.5]]
    validate_specialist_properties(properties)


@pytest.mark.parametrize("length", [0, 31, 241])
def test_modular_bridge_rejects_routes_outside_its_program(bridge_profile, length):
    with pytest.raises(ValueError, match="long"):
        validate_specialist_properties(route_properties(length))


@pytest.mark.parametrize(
    "route",
    [
        [[0, 0], [float("nan"), 0.001]],
        [[0, 0], [0, float("inf")]],
        [[0, 0], [True, 0.001]],
        [[0, 0], [0, 0.0003], [0.0001, 0.0007]],
        [[0, 0], [0, 0.001], [0, 0.0007]],
        [[0, 0], [0, 0.0003], [0, 0.0007]],
        [[0, 91], [0.001, 91]],
    ],
)
def test_modular_bridge_rejects_invalid_bent_or_retraced_controls(bridge_profile, route):
    with pytest.raises(ValueError):
        validate_specialist_properties({**route_properties(), "plan_centerline": route})


@pytest.mark.parametrize(
    "changes",
    [
        {"road_archetype_id": "landmark_signature_bridge"},
        {"width": 6.01},
        {"width": float("nan")},
        {"connect_to_public_road": True},
        {"validation_fixed_fixture": True},
        {"lane_count": 2},
        {"lane_count": None},
        {"road_selected_variant_id": "unknown_bridge_route"},
        {"road_selected_variant_id": None},
    ],
)
def test_modular_bridge_rejects_identity_section_and_legacy_bypass(bridge_profile, changes):
    with pytest.raises(ValueError):
        validate_specialist_properties({**route_properties(), **changes})


def test_modular_bridge_rejects_unavailable_source_profile(bridge_profile):
    from app.services import native_modular_bridge

    native_modular_bridge.MANIFEST.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="trusted"):
        validate_specialist_properties(route_properties())


@pytest.mark.parametrize("variant", ["urban_pedestrian_footbridge_v0", "urban_pedestrian_footbridge_v2"])
def test_original_fixed_footbridge_identity_stays_outside_route_guard(variant):
    validate_specialist_properties({"road_selected_variant_id": variant, "road_archetype_id": PARENT, "width": 90})
    validate_specialist_properties(
        {**route_properties(), "road_selected_variant_id": variant, "validation_fixed_fixture": True}
    )


@pytest.mark.parametrize(
    "boundary",
    [{}, {"terrain_strategy": "landscape", "community_3d_mask_existing_tiles": True}],
)
def test_modular_bridge_requires_prepared_level_ground(bridge_profile, boundary):
    with pytest.raises(ValueError, match="prepared"):
        validate_specialist_ground(route_properties(), boundary)
    validate_specialist_ground(route_properties(), {"community_3d_mask_existing_tiles": True})


def test_modular_bridge_cannot_bypass_compilation_as_a_fixed_rectangle(bridge_profile):
    from shapely.geometry import Polygon
    from app.services.public_realm_lego import plan_public_realm_zone_recipe

    with pytest.raises(ValueError):
        plan_public_realm_zone_recipe(
            "road",
            Polygon([(-0.00003, 0), (0.00003, 0), (0.00003, 0.0007), (-0.00003, 0.0007)]),
            {**route_properties(), "validation_fixed_fixture": True},
            strict=False,
        )


def bridge_geometry(length=80, width=6):
    from shapely.geometry import Polygon

    lng, lat = -114.04, 51.04
    sx = 111320 * math.cos(math.radians(lat))
    geometry = Polygon(
        [
            (lng + x / sx, lat + y / 111320)
            for x, y in [(-width / 2, 0), (width / 2, 0), (width / 2, length), (-width / 2, length)]
        ]
    )
    properties = {**route_properties(length), "plan_centerline": [[lng, lat], [lng, lat + length / 111320]]}
    return geometry, properties


@pytest.mark.parametrize("length", [32, 80, 240])
def test_modular_bridge_compiler_binds_route_length_at_real_latitude(bridge_profile, tmp_path, length):
    geometry, properties = bridge_geometry(length)
    recipe = plan_public_realm_zone_recipe(
        "road", geometry, properties, strict=True, catalog=write_catalog(tmp_path, bridge_row())
    )
    assert recipe.target.length_m == length
    assert recipe.target.row_width_m == 6


@pytest.mark.parametrize("width,length", [(5, 80), (7, 80), (6, 120)])
def test_modular_bridge_compiler_rejects_a_false_route_footprint(bridge_profile, tmp_path, width, length):
    geometry, properties = bridge_geometry(length, width)
    properties["plan_centerline"][-1][1] = properties["plan_centerline"][0][1] + 80 / 111320
    with pytest.raises(ValueError):
        plan_public_realm_zone_recipe(
            "road", geometry, properties, strict=True, catalog=write_catalog(tmp_path, bridge_row())
        )


def compile_bridge_state():
    from geoalchemy2.shape import from_shape
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone, _stamp_community_3d
    from app.models.models import SiteZone

    geometry, properties = bridge_geometry()
    zone = SiteZone(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type="road",
        geometry=from_shape(geometry, srid=4326),
        properties=properties,
    )
    recipe = _public_realm_recipe_for_zone(zone, "street")
    _stamp_community_3d(zone, "street", "2026-10-30T00:00:00Z", public_realm_recipe=recipe)
    assert zone.properties["public_realm_lego"]["variant_id"] == VARIANT
    assert len(zone.properties["public_realm_lego"]["component_set_ids"]) == 9
    claim = SimpleNamespace(
        zone_id=zone.id,
        source_hash=zone.properties["community_3d"]["source_hash"],
        representation_hash=zone.properties["community_3d"]["representation_hash"],
        building_id=None,
    )
    request = SimpleNamespace(community_3d_claims=[claim], details_revision=None, residual_landscape_claim=None)
    boundary = SiteZone(
        id=uuid.uuid4(),
        project_id=zone.project_id,
        zone_type="site_boundary",
        geometry=zone.geometry,
        is_active_boundary=True,
        properties={"community_3d_mask_existing_tiles": True},
    )
    return zone, boundary, request


@pytest.fixture
def compiled_bridge(bridge_profile, tmp_path, monkeypatch):
    """Inject only the staged manifest provider; execute real recipe/capture code."""
    from app.services import native_street_candidate_contract

    staged = write_catalog(tmp_path, bridge_row())
    retained = tuple(
        capability
        for capability in native_street_candidate_contract.native_street_runtime_capabilities()
        if capability.family_id != f"street_native_{VARIANT}"
    )
    monkeypatch.setattr(
        native_street_candidate_contract,
        "native_street_runtime_capabilities",
        lambda: (*retained, *staged.capabilities),
    )
    native_street_candidate_contract.flush_native_street_junction_levels.cache_clear()
    yield compile_bridge_state()
    native_street_candidate_contract.flush_native_street_junction_levels.cache_clear()


def test_delivered_modular_bridge_closes_exact_source_bytes_and_runtime_recipe():
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones
    from app.services.native_street_candidate_contract import flush_native_street_junction_levels

    root = Path(__file__).resolve().parents[2]
    rows = json.loads((root / "backend/app/data/nativeBridgePilots.json").read_text(encoding="utf-8"))
    row = next(row for row in rows if row['id']==VARIANT)
    assert row["sourceAssemblySha256"] == "0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad"
    assert set(row["modules"]) == set(MODULES)
    for module in row["modules"].values():
        path = root / "frontend/public" / module["url"].lstrip("/")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == module["sha256"]
    zone, boundary, request = compile_bridge_state()
    zone.properties = json.loads(json.dumps(zone.properties))
    recipe = zone.properties["public_realm_lego"]
    assert f"program:{row['programSha256']}" in recipe["component_set_ids"]
    assert f"source_recipe:{row['sourceRecipeSha256']}" in recipe["component_set_ids"]
    assert public_realm_recipe_identity(recipe) is not None
    assert _validate_direct_3d_project_zones(request, [boundary, zone], {}, bind_capture_instances=False) == []
    assert VARIANT not in flush_native_street_junction_levels()


def test_modular_bridge_compiles_reloadable_recipe_and_captures_on_prepared_ground(compiled_bridge):
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    zone, boundary, request = compiled_bridge
    zone.properties = json.loads(json.dumps(zone.properties))
    assert public_realm_recipe_identity(zone.properties["public_realm_lego"]) is not None
    assert _validate_direct_3d_project_zones(request, [boundary, zone], {}, bind_capture_instances=False) == []


@pytest.mark.parametrize(
    "changed_boundary", [None, {}, {"terrain_strategy": "landscape", "community_3d_mask_existing_tiles": True}]
)
def test_modular_bridge_capture_rechecks_prepared_ground(compiled_bridge, changed_boundary):
    from fastapi import HTTPException
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    zone, boundary, request = compiled_bridge
    boundary.properties = changed_boundary
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(
            request, [zone] if changed_boundary is None else [boundary, zone], {}, bind_capture_instances=False
        )
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def test_modular_bridge_capture_never_proves_an_at_grade_junction(compiled_bridge):
    from app.api.v1.direct_3d_render import _street_supports_v1_four_way_junction
    from app.services.native_street_candidate_contract import flush_native_street_junction_levels

    zone, _, _ = compiled_bridge
    assert _street_supports_v1_four_way_junction(zone) is False
    assert VARIANT not in flush_native_street_junction_levels()


@pytest.mark.parametrize("lock", ["source_assembly", "program", "module_bridge_bay"])
def test_modular_bridge_capture_rejects_a_rehashed_stale_recipe(compiled_bridge, lock):
    from fastapi import HTTPException
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    zone, boundary, request = compiled_bridge
    recipe = copy.deepcopy(zone.properties["public_realm_lego"])
    recipe["component_set_ids"] = [
        f"{lock}:{'a' * 64}" if item.startswith(f"{lock}:") else item for item in recipe["component_set_ids"]
    ]
    recipe["recipe_hash"] = public_realm_recipe_hash(recipe)
    zone.properties = {**zone.properties, "public_realm_lego": recipe}
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [boundary, zone], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def test_modular_bridge_capture_requires_its_native_recipe(compiled_bridge):
    from fastapi import HTTPException
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones
    from app.api.v1.lego_assembly import _stamp_community_3d

    zone, boundary, request = compiled_bridge
    _stamp_community_3d(zone, "street", "2026-10-30T00:00:01Z")
    metadata = zone.properties["community_3d"]
    claim = request.community_3d_claims[0]
    claim.source_hash, claim.representation_hash = metadata["source_hash"], metadata["representation_hash"]
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [boundary, zone], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def crossing_zone_at_bridge(zone, station, *, path=False):
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Polygon
    from app.models.models import SiteZone

    lng, lat = zone.properties["plan_centerline"][0]
    sx = 111320 * math.cos(math.radians(lat))
    width = 1.8 if path else 16
    geometry = Polygon(
        [
            (lng + x / sx, lat + y / 111320)
            for x, y in [
                (-40, station - width / 2),
                (40, station - width / 2),
                (40, station + width / 2),
                (-40, station + width / 2),
            ]
        ]
    )
    return SiteZone(
        id=uuid.uuid4(),
        project_id=zone.project_id,
        zone_type="road",
        geometry=from_shape(geometry, srid=4326),
        properties={
            "road_archetype_id": "campus_pedestrian_spine" if path else "calgary_local",
            "road_selected_variant_id": "concrete_neighbourhood_walk_v1" if path else "calgary_local_v0",
            "lane_count": 0 if path else 2,
            "width": width,
            "plan_centerline": [[lng - 40 / sx, lat + station / 111320], [lng + 40 / sx, lat + station / 111320]],
        },
    )


def add_capture_claim(request, zone):
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone, _stamp_community_3d

    recipe = _public_realm_recipe_for_zone(zone, "street")
    _stamp_community_3d(zone, "street", "2026-10-30T00:00:00Z", public_realm_recipe=recipe)
    metadata = zone.properties["community_3d"]
    request.community_3d_claims.append(
        SimpleNamespace(
            zone_id=zone.id,
            source_hash=metadata["source_hash"],
            representation_hash=metadata["representation_hash"],
            building_id=None,
        )
    )


@pytest.mark.parametrize("station", [3, 40])
def test_modular_bridge_capture_rejects_saved_motor_road_collisions(compiled_bridge, station):
    from fastapi import HTTPException
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    zone, boundary, request = compiled_bridge
    other = crossing_zone_at_bridge(zone, station)
    add_capture_claim(request, other)
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [boundary, zone, other], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def test_road_first_capture_cannot_hide_a_collision_with_an_existing_bridge(compiled_bridge):
    from fastapi import HTTPException
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    bridge, boundary, request = compiled_bridge
    other = crossing_zone_at_bridge(bridge, 3)
    add_capture_claim(request, other)
    with pytest.raises(HTTPException) as caught:
        _validate_direct_3d_project_zones(request, [boundary, other, bridge], {}, bind_capture_instances=False)
    assert caught.value.status_code == 409
    assert caught.value.detail["billed"] is False


def test_modular_bridge_capture_allows_a_clear_native_path_underpass(compiled_bridge):
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    zone, boundary, request = compiled_bridge
    path = crossing_zone_at_bridge(zone, 40, path=True)
    add_capture_claim(request, path)
    assert _validate_direct_3d_project_zones(request, [boundary, zone, path], {}, bind_capture_instances=False) == []
