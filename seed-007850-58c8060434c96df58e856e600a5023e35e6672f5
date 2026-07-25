"""Master Planner — spec validation/repair, palette conversion, and the
engine's execution of variety (band rotation, per-bar characters, landscape
structure stamping, single-block typology)."""

import math
from dataclasses import replace

import pytest
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from app.services.master_planner.spec import (
    BandAlternate,
    BandPlan,
    LandscapePlan,
    MasterPlanSpec,
    OpenSpaceProgram,
    palette_from_spec,
    validate_spec,
)
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.placement import (
    PALETTES,
    BlockContext,
    palette_for,
    plan_blocks,
)
from app.services.plan_geometry.community_rules import resolve_rules

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=700.0, depth_m=520.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "landscape.tree_density": {"value": 0.6},
}


def _spec(**overrides) -> MasterPlanSpec:
    base = MasterPlanSpec(
        design_narrative="A varied, walkable quarter.",
        layout_strategy="transect_green",
        curvilinear=False,
        laneways=True,
        bands={
            "core": BandPlan(development_type="residential_multifamily", aesthetic="contemporary_urban",
                             floors=7, typology="perimeter_block",
                             alternates=[BandAlternate(development_type="residential_multifamily", aesthetic="classical")]),
            "frontage": BandPlan(development_type="mixed_use", aesthetic="parisian", floors=5,
                                 typology="perimeter_block",
                                 alternates=[BandAlternate(development_type="commercial_retail", aesthetic="historical")]),
            "mid": BandPlan(development_type="residential_multifamily", aesthetic="scandinavian_nordic",
                            floors=4, typology="row_bars",
                            alternates=[BandAlternate(development_type="residential_duplex", aesthetic="brownstone_rowhouse")]),
            "edge": BandPlan(development_type="residential_single_family", aesthetic="traditional_vernacular",
                             floors=2, typology="row_bars"),
            "anchor": BandPlan(development_type="institutional_education", aesthetic="collegiate_gothic",
                               floors=4, typology="anchor_mass"),
        },
        open_space=OpenSpaceProgram(water_feature=True, plaza=True,
                                    water_archetype_id="pond_lake",
                                    central_park_archetype_id="neighborhood_park"),
        landscape=LandscapePlan(park_structure="naturalistic_grove",
                                courtyard_structure="formal_quad",
                                greenway_structure="formal_allee"),
    )
    return base.model_copy(update=overrides)


# --- validation / repair ----------------------------------------------------------


def test_validate_repairs_bad_band_and_ids():
    spec = _spec()
    spec.bands["core"] = BandPlan(development_type="floating_sky_city", aesthetic="x",
                                  floors=99, typology="hoverdome")
    spec.spine_archetype_id = "totally_fake_street"
    spec.landscape.park_structure = "chaos_scatter"
    validated, notes = validate_spec(spec, "city_policy")
    codes = {n["code"] for n in notes}
    # Unknown dev type: band dropped (conversion re-fills from the preset).
    assert "core" not in validated.bands
    assert "MASTER_PLAN_BAND_REPAIRED" in codes
    assert validated.spine_archetype_id is None
    assert "MASTER_PLAN_ID_DROPPED" in codes
    assert validated.landscape.park_structure == "naturalistic_grove"
    assert "MASTER_PLAN_LANDSCAPE_REPAIRED" in codes


def test_validate_clamps_floors_and_keeps_good_bands():
    spec = _spec()
    spec.bands["mid"] = BandPlan(development_type="Residential Multifamily",
                                 aesthetic="Scandinavian Nordic", floors=99,
                                 typology="row_bars")
    validated, _ = validate_spec(spec, "city_policy")
    band = validated.bands["mid"]
    assert band.development_type == "residential_multifamily"  # normalized
    assert band.floors == 40  # clamped, not rejected
    assert validated.bands["anchor"].development_type == "institutional_education"


def test_validate_clamps_block_target_grain():
    spec = _spec(block_target_m=30.0)   # below the 60 m floor
    validated, notes = validate_spec(spec, "city_policy")
    assert validated.block_target_m == 60.0
    assert any(n["code"] == "MASTER_PLAN_GRAIN_CLAMPED" for n in notes)
    # A sensible grain passes through untouched.
    ok, _ = validate_spec(_spec(block_target_m=95.0), "city_policy")
    assert ok.block_target_m == 95.0
    # Absent grain stays None (scenario default used).
    default, _ = validate_spec(_spec(), "city_policy")
    assert default.block_target_m is None


def test_validate_drops_catalog_less_alternates():
    spec = _spec()
    spec.bands["mid"].alternates.append(BandAlternate(development_type="unobtainium_towers"))
    validated, notes = validate_spec(spec, "city_policy")
    alt_types = [a.development_type for a in validated.bands["mid"].alternates]
    assert "unobtainium_towers" not in alt_types
    assert any(n["code"] == "MASTER_PLAN_ALTERNATE_DROPPED" for n in notes)


# --- palette conversion -----------------------------------------------------------


def test_palette_from_spec_maps_bands_and_fallbacks():
    spec, _ = validate_spec(_spec(), "city_policy")
    # This test exercises conversion, not cross-family coherence. Validation
    # correctly drops the intentionally New York duplex alternate from the
    # inferred Calgary family, so insert a validated-shape alternate here to
    # prove palette_from_spec preserves the raw triple for final-floor lookup.
    spec.bands["mid"].alternates = [
        BandAlternate(development_type="residential_duplex", aesthetic="brownstone_rowhouse")
    ]
    del spec.bands["edge"]  # simulate a band the planner failed to author
    palette = palette_from_spec(spec, "city_policy")
    assert palette.bands["core"].floors_abs == 7.0
    assert palette.bands["core"].floors_delta is None
    assert palette.bands["mid"].typology == "row_bars"
    # Missing band keeps the preset BandSpec (relative floors intact).
    assert palette.bands["edge"] is PALETTES["city_policy"].bands["edge"]
    assert palette.alternates["mid"] == (("residential_duplex", "brownstone_rowhouse", None),)
    assert palette.landscape["courtyard"] == "formal_quad"
    assert palette.central_archetype_id == "neighborhood_park"
    assert palette.water_archetype_id == "pond_lake"
    assert palette.laneways is True


# --- band rotation + per-bar options ----------------------------------------------


def _mid_context(index: int) -> BlockContext:
    return BlockContext(
        index=index, area_m2=8000.0, dist_to_centroid_m=50.0, dist_to_edge_m=100.0,
        transect=0.5, fronts_spine=False, touches_boundary=False,
        dist_to_green_m=math.inf, abuts_low_rise=False, ceiling_floors=None,
    )


def test_plan_blocks_rotates_band_alternates_across_blocks():
    rules, _ = resolve_rules("city_policy", PARAMS)
    palette = replace(
        palette_for("city_policy"),
        alternates={"mid": (("residential_multifamily", "scandinavian_nordic", None),
                            ("mixed_use", "contemporary_urban", None))},
    )
    contexts = [_mid_context(i) for i in range(4)]
    plans = plan_blocks(contexts=contexts, palette=palette, rules=rules,
                        base_type=None, base_aesthetic=None)
    combos = {(p.development_type, p.aesthetic) for p in plans.values()}
    assert len(combos) >= 2, f"rotation produced a monoculture: {combos}"
    # Rotation is deterministic: same inputs, same assignment.
    again = plan_blocks(contexts=contexts, palette=palette, rules=rules,
                        base_type=None, base_aesthetic=None)
    assert {i: (p.development_type, p.aesthetic) for i, p in plans.items()} == \
           {i: (p.development_type, p.aesthetic) for i, p in again.items()}


def test_plan_blocks_resolves_width_compatible_bar_options():
    rules, _ = resolve_rules("city_policy", PARAMS)
    palette = replace(
        palette_for("city_policy"),
        alternates={"mid": (("residential_multifamily", "classical", None),
                            ("residential_multifamily", "mediterranean", None))},
    )
    plans = plan_blocks(contexts=[_mid_context(0)], palette=palette, rules=rules,
                        base_type=None, base_aesthetic=None)
    plan = plans[0]
    assert plan.bar_options, "expected variant + alternate bar options"
    # Variant options lead: same archetype as the primary, distinct variant ids.
    variant_opts = [o for o in plan.bar_options if o.archetype_id == plan.archetype_id]
    assert variant_opts, "primary archetype's variants missing from bar options"
    assert len({o.variant_id for o in variant_opts}) == len(variant_opts)
    # Cross-archetype alternates that survived the width filter are resolved.
    alt_opts = [o for o in plan.bar_options if o.archetype_id != plan.archetype_id]
    assert all(o.archetype_id for o in alt_opts)


def test_presets_rotate_variants_not_archetypes():
    rules, _ = resolve_rules("city_policy", PARAMS)
    contexts = [_mid_context(i) for i in range(3)]
    plans = plan_blocks(contexts=contexts, palette=palette_for("city_policy"),
                        rules=rules, base_type=None, base_aesthetic=None)
    combos = {(p.development_type, p.aesthetic) for p in plans.values()}
    assert len(combos) == 1  # presets keep their single-character bands
    # Fine-grain variety now comes from the archetype's OWN variants: every
    # bar option shares the primary archetype, differing only by variant.
    for p in plans.values():
        assert all(o.archetype_id == p.archetype_id for o in p.bar_options)
        assert all(o.variant_id for o in p.bar_options)


# --- engine integration -----------------------------------------------------------


def test_generated_plan_carries_variety_and_landscape():
    spec, _ = validate_spec(_spec(), "city_policy")
    palette = palette_from_spec(spec, "city_policy")
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="city_policy", scenario_label="MP",
        parameters=PARAMS, road_features=[], district_features=[],
        palette_override=palette,
    )
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings
    combos = {(z["properties"]["development_type"], z["properties"]["development_aesthetic"])
              for z in buildings}
    assert len(combos) >= 2, f"plan is a monoculture: {combos}"

    greens = [z for z in result.zones if z["properties"].get("_plan_role") == "open_space"]
    planted = [z for z in greens if z["properties"].get("green_kind") != "pond"]
    assert planted
    assert all(z["properties"].get("planting_structure") for z in planted)

    courtyards = [z for z in result.zones if z["properties"].get("_plan_role") == "courtyard"]
    for z in courtyards:
        assert z["properties"]["planting_structure"] == "formal_quad"


def test_preset_scenarios_stamp_landscape_structures():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="environmental", scenario_label="Env",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    greens = [z for z in result.zones
              if z["properties"].get("_plan_role") == "open_space"
              and z["properties"].get("green_kind") in ("central", "pocket", "greenway")]
    assert greens
    assert all(z["properties"].get("planting_structure") for z in greens)
    ponds = [z for z in result.zones
             if z["properties"].get("green_kind") == "pond"]
    greenways = [z for z in result.zones
                 if z["properties"].get("green_kind") == "greenway"]
    assert ponds
    assert all(z["properties"].get("green_space_archetype_id")
               == "stormwater_retention_pond" for z in ponds)
    assert greenways
    assert all(z["properties"].get("green_space_archetype_id")
               == "linear_park_greenway" for z in greenways)


def test_city_beautiful_stamps_fountain_and_civic_plaza_archetypes():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="city_beautiful", scenario_label="Beautiful",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    open_spaces = [z for z in result.zones
                   if z["properties"].get("_plan_role") == "open_space"]
    fountains = [z for z in open_spaces
                 if z["properties"].get("green_kind") == "pond"]
    plazas = [z for z in open_spaces
              if z["properties"].get("green_kind") == "plaza"]
    assert fountains
    assert all(z["properties"].get("green_space_archetype_id")
               == "fountain_water_feature" for z in fountains)
    assert plazas
    assert all(z["properties"].get("green_space_archetype_id")
               == "formal_civic_plaza" for z in plazas)


@pytest.mark.parametrize("scenario_id", sorted(PALETTES))
def test_every_nonwater_public_space_connects_to_the_plan_network(scenario_id):
    from app.services.site_engine import (
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    site = _site()
    result = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id=scenario_id,
        scenario_label=f"Connected {scenario_id}", parameters=PARAMS,
        road_features=[], district_features=[],
    )
    public_spaces = [
        zone for zone in result.zones
        if zone["properties"].get("_plan_role") == "open_space"
        and zone["properties"].get("green_kind") != "pond"
    ]

    assert public_spaces
    assert all(
        zone["properties"].get("park_access_points")
        for zone in public_spaces
    ), [
        (zone.get("name"), zone["properties"].get("green_kind"))
        for zone in public_spaces
        if not zone["properties"].get("park_access_points")
    ]

    to_metric = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    street_ground = unary_union([
        project_geometry(Polygon(zone["coordinates"]), to_metric)
        for zone in result.zones
        if zone["properties"].get("_plan_role") == "street"
    ])
    for zone in public_spaces:
        park = project_geometry(Polygon(zone["coordinates"]), to_metric)
        for coordinates in zone["properties"]["park_access_points"]:
            gateway = project_geometry(Point(coordinates), to_metric)
            assert park.boundary.distance(gateway) < 0.1
            assert street_ground.distance(gateway) < 3.1


def test_single_block_site_honors_master_plan_typology():
    spec, _ = validate_spec(_spec(single_block_typology="row_bars"), "city_policy")
    palette = palette_from_spec(spec, "city_policy")
    small = _site(width_m=130.0, depth_m=110.0)  # too tight for internal streets
    result = generate_plan_geometry(
        site_polygon_wgs84=small, scenario_id="city_policy", scenario_label="Tiny",
        parameters=PARAMS, road_features=[], district_features=[],
        palette_override=palette,
    )
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    if result.block_count == 1 and buildings:
        typologies = {z["properties"].get("typology") for z in buildings}
        # row_bars requested; perimeter_block only as the degenerate fallback.
        assert typologies <= {"row_bars", "perimeter_block"}
        assert "row_bars" in typologies
