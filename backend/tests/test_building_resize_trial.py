"""Building resize pilot: server authority for one stretched mid-rise.

The pilot is gated by ENABLE_BUILDING_RESIZE_TRIAL (default off). These tests
prove the off state is inert, the on state validates on the server, and the
select-and-place default is released only through the explicit trial contract.
"""

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.lego_assembly import (
    Community3DCompileItem,
    LegoAssemblyPlanRequest,
    _assert_ai_lego_recipes_are_current,
    _building_reuse_keys,
    _locked_building_target,
)
from app.core.config import Settings
from app.models.models import SiteZone
from app.services import building_flex_contract as contracts
from app.services.building_placement_edges import building_contact_geometry, building_edge_contracts
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    _fixed_landmark_is_select_and_place,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)
from app.services.master_planner.lego_catalog import build_lego_planning_catalog
from app.services.model_contract import catalogue_housing_programme, uses_placement_plot
from app.services.residual_landscape import community_3d_source_hash, community_3d_source_properties
from tools.rlasm_clay_library import clay_seed_rows

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "seed/model-library/rlasm-architectural-clay/library.json"
FRONTEND_CONTRACT = ROOT / "frontend/src/data/buildingResizeTrial.json"

PROGRAM = contracts.RESIZE_TRIAL_PROGRAM_ID
ASSET = "final_seniors_apartments"
VARIANT = "final-seniors-apartments-v1"
CANDIDATE = "final-seniors-apartments-clay-v003"
NATIVE_W = 32.36000061035156
NATIVE_D = 17.980000495910645
NATIVE_H = 18.989999771118164


@pytest.fixture
def trial_on(monkeypatch):
    monkeypatch.setattr(contracts, "building_resize_trial_enabled", lambda: True)


def library_entries():
    payload = json.loads(LIBRARY.read_text(encoding="utf-8"))
    return [SimpleNamespace(**{**row, "metadata_": row["metadata"]}) for row in clay_seed_rows(payload)]


def descriptors(entries=None):
    return [
        descriptor
        for entry in (entries or library_entries())
        if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]


def seniors_module():
    return next(module for module in descriptors() if module.source_variant_id == VARIANT)


def properties(mode="exact_model", width=1.0, depth=1.0, **overrides):
    values = dict(
        pick_place_asset=ASSET,
        development_archetype_id="final-seniors-apartments",
        development_selected_variant_id=VARIANT,
        pick_place_model_revision=CANDIDATE,
        native_plot_axes=True,
        floors=5,
        floor_count=5,
        building_footprint_program_id=PROGRAM,
        building_footprint_mode=mode,
        building_footprint_width_scale=width,
        building_footprint_depth_scale=depth,
        # Deliberately false client claims. The server must never read them.
        building_footprint_native_width_m=999,
        building_footprint_native_depth_m=999,
    )
    values.update(overrides)
    return values


def rectangle(width, depth):
    return [(-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2)]


def zone(props, local_ring):
    east = 111320 * math.cos(math.radians(51))
    ring = [(-114 + x / east, 51 + y / 111320) for x, y in [*local_ring, local_ring[0]]]
    return SiteZone(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type="building",
        updated_at=datetime.now(timezone.utc),
        properties=props,
        geometry="SRID=4326;POLYGON((" + ",".join(f"{x} {y}" for x, y in ring) + "))",
    )


def stretch_request(width, depth, plot=(60.0, 40.0), program=PROGRAM):
    return AssemblyRequest(
        NATIVE_W * width,
        NATIVE_D * depth,
        5,
        archetype_id=VARIANT,
        # The browser derives the same keys from the saved building identity.
        reuse_keys=_building_reuse_keys(properties()),
        footprint_local_m=tuple(rectangle(*plot)),
        model_revision=CANDIDATE,
        footprint_program_id=program,
    )


# --- Flag and contract files ------------------------------------------------


def test_the_server_flag_defaults_off_and_reads_its_environment_name(monkeypatch):
    monkeypatch.delenv("ENABLE_BUILDING_RESIZE_TRIAL", raising=False)
    assert Settings(_env_file=None).enable_building_resize_trial is False
    monkeypatch.setenv("ENABLE_BUILDING_RESIZE_TRIAL", "true")
    assert Settings(_env_file=None).enable_building_resize_trial is True


def test_the_backend_contract_mirrors_the_frontend_tuning_file_byte_for_byte():
    assert contracts.RESIZE_TRIAL_MANIFEST.read_bytes() == FRONTEND_CONTRACT.read_bytes()


def test_the_trial_pins_the_exact_reviewed_library_entry():
    payload = json.loads(LIBRARY.read_text(encoding="utf-8"))
    entry = next(row for row in payload["entries"] if row["candidate"] == CANDIDATE)
    family = contracts._resize_trial_manifest().families[0]
    assert (family.asset_id, family.variant_id, family.archetype_id) == (
        entry["picker"]["id"],
        entry["variant_id"],
        entry["archetype_id"],
    )
    assert family.sha256 == entry["model"]["sha256"]
    assert family.native_storeys == entry["native_floors"]
    dimensions = entry["model"]["native_dimensions_m"]
    assert (family.native_width_m, family.native_depth_m, family.native_height_m) == (
        dimensions["width"],
        dimensions["depth"],
        dimensions["height"],
    )
    assert entry["review"]["status"] == "PASS_INDEPENDENT_ARCHITECTURAL_CLAY"
    raw = json.loads(FRONTEND_CONTRACT.read_text(encoding="utf-8"))
    assert raw["status"] == "LOCAL_TRIAL_ONLY"
    assert raw["stretch"]["vertical_scale"] == 1.0
    assert (raw["stretch"]["minimum_scale"], raw["stretch"]["maximum_scale"]) == (0.7, 1.4)
    assert raw["families"][0]["bytes"] == entry["model"]["bytes"]


def test_a_band_beyond_the_hard_ceiling_is_refused(monkeypatch, tmp_path):
    payload = json.loads(FRONTEND_CONTRACT.read_text(encoding="utf-8"))
    payload["stretch"]["maximum_scale"] = 2.5
    widened = tmp_path / "buildingResizeTrial.json"
    widened.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(contracts, "RESIZE_TRIAL_MANIFEST", widened)
    contracts._resize_trial_manifest.cache_clear()
    try:
        with pytest.raises(ValueError, match="bounded runtime range"):
            contracts._resize_trial_manifest()
    finally:
        contracts._resize_trial_manifest.cache_clear()


# --- Flag off: the programme does not exist ---------------------------------


def test_flag_off_ignores_the_trial_programme_like_any_unknown_programme():
    assert contracts.building_resize_trial_enabled() is False
    assert contracts.resize_trial_contract() is None
    assert contracts.trusted_building_footprint_target(properties(width=0.8, depth=1.2)) is None
    assert contracts.resize_trial_state(properties(width=5, depth=5)) is None
    assert contracts.resize_trial_is_shape_freely(properties(mode="shape_freely")) is False
    assert contracts.resize_trial_outline_problem(rectangle(1, 1)) is None
    assert uses_placement_plot(properties(mode="shape_freely")) is True


def test_flag_off_keeps_the_model_select_and_place_even_when_the_programme_is_declared():
    module = seniors_module()
    assert _fixed_landmark_is_select_and_place(module) is True
    # A target at least as large as the model places it unscaled, as before.
    plan = plan_vertical_assembly(descriptors(), stretch_request(1.125, 1.22), allow_forced_fit=False)
    assert plan["instances"][0]["scale"] == [1.0, 1.0, 1.0]
    assert plan["fit"]["native_scale_locked"] is True
    assert "resize_trial" not in plan["fit"]
    # A smaller target is still refused exactly as it was before the pilot.
    with pytest.raises(AssemblyPlanningError, match="fixed at its native size"):
        plan_vertical_assembly(descriptors(), stretch_request(0.8, 1.2), allow_forced_fit=False)


def test_flag_off_measures_the_saved_plot_not_the_declared_stretch():
    placed = zone(properties(width=0.8, depth=1.2), rectangle(40, 30))
    assert _locked_building_target(placed)[:2] == (40.0, 30.0)


# --- Flag on: validation ----------------------------------------------------


def test_native_dimensions_come_from_the_packaged_manifest(trial_on):
    assert contracts.trusted_building_footprint_target(properties()) == pytest.approx((NATIVE_W, NATIVE_D))
    assert contracts.trusted_building_footprint_target(properties(width=0.7, depth=1.4)) == pytest.approx(
        (NATIVE_W * 0.7, NATIVE_D * 1.4)
    )
    assert contracts.resize_trial_stretch_program_id(properties(width=1.4, depth=0.7)) == PROGRAM


@pytest.mark.parametrize(
    "overrides",
    [
        {"building_footprint_width_scale": 0.69},
        {"building_footprint_depth_scale": 1.41},
        {"building_footprint_width_scale": float("nan")},
        {"building_footprint_depth_scale": float("inf")},
        {"building_footprint_width_scale": True},
        {"building_footprint_width_scale": "wide"},
        {"building_footprint_depth_scale": None},
        {"building_footprint_mode": None},
        {"building_footprint_mode": "stretch_anything"},
        {"development_selected_variant_id": "another_variant"},
        {"pick_place_model_revision": "another_revision"},
        {"pick_place_asset": "another_asset"},
    ],
)
def test_an_invalid_declared_state_fails_closed(trial_on, overrides):
    with pytest.raises(ValueError):
        contracts.trusted_building_footprint_target(properties(**overrides))
    with pytest.raises(HTTPException) as caught:
        _locked_building_target(zone(properties(**overrides), rectangle(60, 40)))
    assert caught.value.status_code == 409


def test_unrelated_buildings_never_open_the_trial_manifest(trial_on, monkeypatch):
    def unavailable():
        raise FileNotFoundError("Trial manifest unavailable")

    monkeypatch.setattr(contracts, "_resize_trial_manifest", unavailable)
    assert contracts.trusted_building_footprint_target({}) is None
    assert contracts.trusted_building_footprint_target({"building_footprint_program_id": "unknown"}) is None
    assert contracts.resize_trial_state({"pick_place_asset": ASSET}) is None
    assert contracts.resize_trial_is_shape_freely({}) is False


def test_shape_freely_keeps_the_drawn_polygon_as_its_target(trial_on):
    freely = properties(mode="shape_freely")
    assert contracts.trusted_building_footprint_target(freely) is None
    assert contracts.resize_trial_stretch_program_id(freely) is None
    assert contracts.resize_trial_is_shape_freely(freely) is True
    assert contracts.resize_trial_is_shape_freely(properties()) is False
    assert uses_placement_plot(freely) is False
    assert uses_placement_plot(properties(width=1.2)) is True


def test_a_reshaped_building_claims_no_reviewed_dwelling_programme(trial_on):
    assert catalogue_housing_programme(properties(width=1.2)) is None
    assert catalogue_housing_programme(properties(mode="shape_freely")) is None


# --- Flag on: planner -------------------------------------------------------


@pytest.mark.parametrize(("width", "depth"), [(0.7, 0.7), (0.7, 1.4), (1.0, 1.0), (1.4, 0.7), (1.4, 1.4), (0.85, 1.15)])
def test_the_exact_model_stretches_independently_with_unit_height(trial_on, width, depth):
    module = seniors_module()
    plan = plan_vertical_assembly(descriptors(), stretch_request(width, depth), allow_forced_fit=False)
    instance = plan["instances"][0]
    assert [row["role"] for row in plan["instances"]] == ["assembled"]
    assert instance["asset_id"] == module.id
    assert instance["scale"] == [width, depth, 1.0]
    assert instance["rotation_degrees"] == 0.0
    assert instance["native_dimensions_m"] == [NATIVE_W, NATIVE_D, NATIVE_H]
    assert plan["assembled_height_m"] == pytest.approx(NATIVE_H, abs=1e-4)
    assert plan["target"]["width_m"] == pytest.approx(NATIVE_W * width)
    assert plan["target"]["depth_m"] == pytest.approx(NATIVE_D * depth)
    fit = plan["fit"]
    assert fit["native_scale_locked"] is False
    assert fit["delivery_format"] == "architectural_clay"
    assert fit["resize_trial"] == {
        "program_id": PROGRAM,
        "width_scale": width,
        "depth_scale": depth,
        "vertical_scale": 1.0,
    }
    assert fit["compatibility_source"] == (
        "resize_trial_native" if (width, depth) == (1.0, 1.0) else "resize_trial_stretch"
    )
    assert fit["scale_band"]["min"] == 0.7 and fit["scale_band"]["max"] == 1.4


@pytest.mark.parametrize(("width", "depth"), [(0.69, 1.0), (1.0, 1.41), (2.0, 2.0), (0.1, 1.0)])
def test_a_stretch_outside_the_band_is_refused_by_the_planner(trial_on, width, depth):
    with pytest.raises(AssemblyPlanningError, match="stretch range") as caught:
        plan_vertical_assembly(
            descriptors(), stretch_request(width, depth, plot=(200.0, 200.0)), allow_forced_fit=False
        )
    assert caught.value.code == "family_incompatible"


def test_the_stretched_building_must_stay_inside_its_plot(trial_on):
    snug = (NATIVE_W * 1.2 + 0.1, NATIVE_D + 0.1)
    assert plan_vertical_assembly(descriptors(), stretch_request(1.2, 1.0, plot=snug), allow_forced_fit=False)
    with pytest.raises(AssemblyPlanningError, match="does not fit inside its plot"):
        plan_vertical_assembly(
            descriptors(), stretch_request(1.2, 1.0, plot=(NATIVE_W * 1.2 - 0.5, 40.0)), allow_forced_fit=False
        )


def test_the_default_is_released_only_through_the_explicit_contract(trial_on):
    contract = contracts.resize_trial_contract()
    pinned = seniors_module()
    assert _fixed_landmark_is_select_and_place(pinned) is True
    assert _fixed_landmark_is_select_and_place(pinned, resize_trial=contract) is False
    others = [module for module in descriptors() if module.source_variant_id != VARIANT]
    assert len(others) > 20
    assert all(_fixed_landmark_is_select_and_place(module, resize_trial=contract) for module in others)


def test_an_existing_placement_without_the_programme_is_unchanged_with_the_flag_on(trial_on):
    """Switching the flag on must not stretch buildings that never asked for it."""
    plan = plan_vertical_assembly(descriptors(), stretch_request(1.125, 1.22, program=None), allow_forced_fit=False)
    assert plan["instances"][0]["scale"] == [1.0, 1.0, 1.0]
    assert plan["fit"]["native_scale_locked"] is True
    assert _locked_building_target(zone({**properties(), "building_footprint_program_id": None}, rectangle(40, 30)))[
        :2
    ] == (40.0, 30.0)


def test_different_bytes_under_the_same_variant_are_not_released(trial_on):
    entries = library_entries()
    for entry in entries:
        if entry.metadata_["rlasm"]["variant_id"] == VARIANT:
            entry.metadata_ = {
                **entry.metadata_,
                "rlasm": {**entry.metadata_["rlasm"], "model_sha256": "0" * 64},
            }
    plan = plan_vertical_assembly(descriptors(entries), stretch_request(1.125, 1.22), allow_forced_fit=False)
    assert plan["instances"][0]["scale"] == [1.0, 1.0, 1.0]
    assert plan["fit"]["native_scale_locked"] is True
    assert "resize_trial" not in plan["fit"]
    with pytest.raises(AssemblyPlanningError, match="fixed at its native size"):
        plan_vertical_assembly(descriptors(entries), stretch_request(0.8, 1.2), allow_forced_fit=False)


def test_another_clay_building_cannot_borrow_the_programme(trial_on):
    other = next(module for module in descriptors() if module.source_variant_id == "nordic_timber_mass_timber")
    request = AssemblyRequest(
        other.width_m * 1.2,
        other.depth_m * 1.2,
        other.native_floors,
        archetype_id=other.source_variant_id,
        footprint_local_m=tuple(rectangle(80, 80)),
        model_revision=other.model_revision,
        footprint_program_id=PROGRAM,
    )
    plan = plan_vertical_assembly(descriptors(), request, allow_forced_fit=False)
    assert plan["instances"][0]["scale"] == [1.0, 1.0, 1.0]
    assert plan["fit"]["native_scale_locked"] is True


def test_the_plan_endpoint_accepts_only_a_bounded_programme_id():
    assert LegoAssemblyPlanRequest(target_width_m=1, target_depth_m=1, target_floors=1).footprint_program_id is None
    with pytest.raises(ValueError):
        LegoAssemblyPlanRequest(target_width_m=1, target_depth_m=1, target_floors=1, footprint_program_id="x" * 121)


# --- Flag on: saved zone certification --------------------------------------


def compile_item(placed, plan=None, entries=None):
    if plan is None:
        return Community3DCompileItem(zone_id=placed.id, source_updated_at=placed.updated_at)
    return Community3DCompileItem(
        zone_id=placed.id,
        source_updated_at=placed.updated_at,
        recipe=dict(
            module_family=plan["family"],
            archetype_id=plan["archetype_id"],
            reuse_keys=plan["reuse_keys"],
            target=plan["target"],
            instances=plan["instances"],
            assembled_height_m=plan["assembled_height_m"],
            fit=plan["fit"],
            catalog_fingerprint=build_lego_planning_catalog(entries).fingerprint,
        ),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(("width", "depth"), [(0.7, 1.4), (1.0, 1.0), (1.25, 0.9)])
async def test_a_saved_stretch_is_certified_against_the_server_target(trial_on, width, depth):
    entries = library_entries()
    plot = (NATIVE_W * width + 4.04, NATIVE_D * depth + 4.02)
    placed = zone(properties(width=width, depth=depth), rectangle(*plot))
    target = _locked_building_target(placed)
    assert target[:2] == pytest.approx((NATIVE_W * width, NATIVE_D * depth))
    assert target[2:4] == (5, "rectangle")
    plan = plan_vertical_assembly(
        descriptors(entries), stretch_request(width, depth, plot=plot), allow_forced_fit=False
    )
    await _assert_ai_lego_recipes_are_current(
        None, None, placed.project_id, [(compile_item(placed, plan, entries), placed, "building")], entries=entries
    )
    assert placed.properties["target_w_m"] == pytest.approx(NATIVE_W * width)
    assert placed.properties["target_d_m"] == pytest.approx(NATIVE_D * depth)


@pytest.mark.anyio
async def test_a_recipe_planned_for_another_stretch_is_refused(trial_on):
    entries = library_entries()
    plot = (60.0, 40.0)
    placed = zone(properties(width=1.2, depth=1.0), rectangle(*plot))
    stale = plan_vertical_assembly(descriptors(entries), stretch_request(1.0, 1.0, plot=plot), allow_forced_fit=False)
    with pytest.raises(HTTPException) as caught:
        await _assert_ai_lego_recipes_are_current(
            None, None, placed.project_id, [(compile_item(placed, stale, entries), placed, "building")], entries=entries
        )
    assert caught.value.status_code == 409


@pytest.mark.anyio
async def test_a_stretch_without_its_recipe_cannot_slip_through_as_massing(trial_on):
    entries = library_entries()
    placed = zone(properties(width=1.2, depth=1.0), rectangle(60, 40))
    with pytest.raises(HTTPException) as caught:
        await _assert_ai_lego_recipes_are_current(
            None, None, placed.project_id, [(compile_item(placed), placed, "building")], entries=entries
        )
    assert caught.value.status_code == 409
    assert "recipe is missing" in caught.value.detail


@pytest.mark.anyio
async def test_shape_freely_is_certified_as_explicit_massing_without_a_recipe(trial_on):
    entries = library_entries()
    l_shape = [(-25, -15), (25, -15), (25, 0), (0, 0), (0, 15), (-25, 15)]
    placed = zone(properties(mode="shape_freely"), l_shape)
    before = dict(placed.properties)
    await _assert_ai_lego_recipes_are_current(
        None, None, placed.project_id, [(compile_item(placed), placed, "building")], entries=entries
    )
    assert placed.properties == before


@pytest.mark.anyio
async def test_shape_freely_refuses_a_detailed_recipe_and_an_undersized_outline(trial_on):
    entries = library_entries()
    plot = (60.0, 40.0)
    placed = zone(properties(mode="shape_freely"), rectangle(*plot))
    plan = plan_vertical_assembly(descriptors(entries), stretch_request(1.0, 1.0, plot=plot), allow_forced_fit=False)
    with pytest.raises(HTTPException) as caught:
        await _assert_ai_lego_recipes_are_current(
            None, None, placed.project_id, [(compile_item(placed, plan, entries), placed, "building")], entries=entries
        )
    assert caught.value.status_code == 409 and "Shape freely" in caught.value.detail

    small = zone(properties(mode="shape_freely"), rectangle(30, 6))
    with pytest.raises(HTTPException) as caught:
        await _assert_ai_lego_recipes_are_current(
            None, None, small.project_id, [(compile_item(small), small, "building")], entries=entries
        )
    assert caught.value.status_code == 409 and "at least 9 m wide" in caught.value.detail


@pytest.mark.parametrize(
    ("ring", "message"),
    [
        (rectangle(8.9, 30), "at least 9 m wide"),
        (rectangle(30, 8.9), "at least 9 m wide"),
        ([(0, 0), (20, 0), (0.5, 9.5)], "at least 100 m²"),
        (rectangle(121, 30), "at most 120 m"),
        (
            [(math.cos(i / 25 * math.tau) * 30, math.sin(i / 25 * math.tau) * 30) for i in range(25)],
            "at most 24 corners",
        ),
        ([(0, 0), (20, 0)], "at least three"),
    ],
)
def test_outline_limits_are_measured_on_the_server(trial_on, ring, message):
    assert message in contracts.resize_trial_outline_problem(ring)


def test_a_sensible_outline_passes_including_a_rotated_one(trial_on):
    assert contracts.resize_trial_outline_problem(rectangle(9, 12)) is None
    angle = math.radians(37)
    rotated = [
        (x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle))
        for x, y in rectangle(9, 12)
    ]
    assert contracts.resize_trial_outline_problem([*rotated, rotated[0]]) is None


# --- Neighbour contact and compiled-proof freshness -------------------------


def edge_zone(**overrides):
    row = next(
        row
        for row in building_edge_contracts().values()
        if (row["left"] == "abut" or row["right"] == "abut") and not row.get("plotFit")
    )
    plot = (row["nativeWidthM"] + 6, row["nativeDepthM"] + 6)
    props = dict(
        pick_place_asset=row["assetId"],
        development_selected_variant_id=row["variantId"],
        pick_place_model_revision=row["revision"],
        native_plot_axes=True,
    )
    props.update(overrides)
    return zone(props, rectangle(*plot))


def test_a_reshaped_trial_building_keeps_its_whole_plot_as_its_contact_envelope():
    from shapely import wkt

    def contact(placed):
        source = wkt.loads(str(placed.geometry).split(";", 1)[1])
        return source, building_contact_geometry(placed, source)

    source, reviewed = contact(edge_zone())
    assert reviewed.area < source.area  # the reviewed native envelope releases padding
    trial = dict(building_footprint_program_id=PROGRAM, building_footprint_mode="exact_model")
    source, unit = contact(edge_zone(**trial, building_footprint_width_scale=1, building_footprint_depth_scale=1))
    assert unit.area < source.area
    for state in (
        dict(**trial, building_footprint_width_scale=1.2, building_footprint_depth_scale=1),
        dict(**trial, building_footprint_width_scale=1, building_footprint_depth_scale=0.8),
        dict(**trial, building_footprint_width_scale="wide", building_footprint_depth_scale=1),
        dict(building_footprint_program_id=PROGRAM, building_footprint_mode="shape_freely"),
    ):
        source, kept = contact(edge_zone(**state))
        assert kept.equals(source)


def test_a_stretch_edit_changes_the_compiled_source_fingerprint():
    from shapely.geometry import Polygon

    geometry = Polygon(rectangle(0.001, 0.001))
    ordinary = {key: value for key, value in properties().items() if not key.startswith("building_footprint_")}
    assert "resize_trial" not in community_3d_source_properties("building", ordinary)
    unrelated = {
        **ordinary,
        "building_footprint_program_id": "house-flex-pilot-v001",
        "building_footprint_width_scale": 1.3,
    }
    assert community_3d_source_hash("building", geometry, unrelated) == community_3d_source_hash(
        "building", geometry, ordinary
    )
    hashes = {
        community_3d_source_hash("building", geometry, state)
        for state in (
            ordinary,
            properties(),
            properties(width=1.2),
            properties(depth=1.2),
            properties(mode="shape_freely"),
        )
    }
    assert len(hashes) == 5
