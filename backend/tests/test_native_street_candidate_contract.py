from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    build_public_realm_capability_catalog,
    plan_public_realm_recipe,
    public_realm_recipe_identity,
)


MANIFEST = Path(__file__).resolve().parents[2] / "frontend/src/data/nativeStreetPilots.json"


def test_new_route_capabilities_do_not_convert_saved_fixed_rectangles():
    from shapely.geometry import Polygon
    from app.services.public_realm_lego import plan_public_realm_zone_recipe, PublicRealmPlanningError
    geometry = Polygon([(-114, 51), (-113.9999, 51), (-113.9999, 51.0001), (-114, 51.0001)])
    props = dict(validation_fixed_fixture=True, road_archetype_id='student_quiet_residential_street_v1',
                 road_selected_variant_id='student_quiet_residential_street_v1', width=18)
    assert plan_public_realm_zone_recipe('road', geometry, props, strict=False) is None
    with pytest.raises(PublicRealmPlanningError):
        plan_public_realm_zone_recipe('road', geometry, {**props, 'road_archetype_id':'unknown'}, strict=True)


def test_native_street_generated_mirrors_and_rosters_are_identical():
    backend_data = Path(__file__).resolve().parents[1] / 'app/data'
    assert json.loads(MANIFEST.read_text()) == json.loads((backend_data/'nativeStreetPilots.json').read_text())
    native = lambda path: [row for row in json.loads(path.read_text())['entries'] if row['representation']=='native-modules']
    assert native(MANIFEST.with_name('classroomStarter.json')) == native(backend_data/'classroomStarter.json')


def test_frontend_runtime_fixtures_keep_their_trusted_saved_identity():
    fixtures = MANIFEST.parents[1] / "components/viewer/globe/__fixtures__/classroomStreetRecipes.json"
    for recipe in json.loads(fixtures.read_text(encoding="utf-8")):
        identity = public_realm_recipe_identity(recipe)
        assert identity is not None
        assert identity['recipe'] == recipe


def test_native_street_runtime_compiles_the_same_exact_locked_recipes_as_review():
    catalog = build_native_street_candidate_catalog(MANIFEST)
    rows = {row["id"]: row for row in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    assert {cap.selections[0].variant_id for cap in catalog.capabilities} == {
        'student_main_street_v1', 'student_market_street_v1',
        'student_quiet_residential_street_v1', 'student_planted_shared_lane_v1',
        'brt_bus_rapid_transit_corridor_v0',
        'amsterdam_gracht_v1',
        'landmark_signature_bridge_v2',
        'student_cycle_avenue_v1',
        'student_green_alley_v1',
        'student_school_street_v1',
        'student_grass_tram_avenue_v1',
        'student_vine_pergola_promenade_v1',
        'student_grand_haussmann_boulevard_v1',
        'student_london_cobbled_mews_v1',
        'student_cherry_blossom_street_v1',
        'student_barcelona_shaded_promenade_v1',
        'student_elevated_garden_rail_v1',
        'skytrain_elevated_corridor_v0',
        'elevated_rail_transit_corridor_v0',
    }
    assert catalog.prompt_vocabulary == ""
    active = build_public_realm_capability_catalog()
    for capability in catalog.capabilities:
        selection = capability.selections[0]
        pilot = rows[selection.variant_id]
        assert selection.archetype_id == pilot["sourceArchetypeId"]
        assert capability.family_id in active.family_ids
        assert selection.variant_id in active.variants_by_archetype.get(selection.archetype_id, ())
        recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id,
            variant_id=selection.variant_id,
            preferred_family_id=capability.family_id,
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=max(120, pilot.get("program", {}).get("minLengthM", 0))),
        ), catalog=catalog)
        assert recipe.component_set_ids == selection.component_set_ids
        assert f"source_recipe:{pilot['sourceRecipeSha256']}" in recipe.component_set_ids
        assert len(recipe.component_set_ids) == len(pilot["modules"]) + 3 + bool(pilot.get('program'))
        live_recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id, variant_id=selection.variant_id,
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=max(120, pilot.get("program", {}).get("minLengthM", 0))),
        ))
        assert live_recipe.component_set_ids == recipe.component_set_ids
        assert live_recipe.profile_id == recipe.profile_id
        assert recipe.recipe_hash == plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id,
            variant_id=selection.variant_id,
            preferred_family_id=capability.family_id,
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=max(120, pilot.get("program", {}).get("minLengthM", 0))),
        ), catalog=catalog).recipe_hash


def test_candidate_contract_rejects_untrusted_parent_and_changed_module_hash(tmp_path: Path):
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows[0]["sourceArchetypeId"] = "invented_street"
    changed = tmp_path / "pilots.json"
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="trusted street parent"):
        build_native_street_candidate_catalog(changed)
    rows[0]["sourceArchetypeId"] = "neighborhood_main_street"
    first_module = next(iter(rows[0]["modules"].values()))
    original_sha = first_module["sha256"]
    first_module["sha256"] = "not-a-hash"
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="source or module hash"):
        build_native_street_candidate_catalog(changed)
    first_module["sha256"] = original_sha
    rows[0]["sections"][1]["x"] += 0.2
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="metric section"):
        build_native_street_candidate_catalog(changed)
