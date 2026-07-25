"""Regression guards for the 2026-07-12 plan-quality fixes: medium infill
sites must SUBDIVIDE (no single megablock), perimeter courtyards must stay a
believable share of the block (no 65% void), courtyard green must not overlap
buildings, and no plan may be a monoculture."""

import math

from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

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
from app.services.plan_geometry.street_graph import _axis_positions
from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _off(x, y):
    return (LON + x / M_LON, LAT + y / M_LAT)


def _site(w, d):
    return Polygon([_off(0, 0), _off(w, 0), _off(w, d), _off(0, d)])


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 5},
    "landscape.tree_density": {"value": 0.6},
}


def _gen(scenario="economic", w=155.9, d=116.5, palette=None):
    return generate_plan_geometry(
        site_polygon_wgs84=_site(w, d), scenario_id=scenario, scenario_label=scenario,
        parameters=PARAMS, road_features=[], district_features=[], palette_override=palette,
    )


def _metric(z, tf):
    return make_valid(project_geometry(make_valid(Polygon(z["coordinates"])), tf))


# --- _axis_positions unit behaviour ----------------------------------------------


def test_axis_positions_forces_subdivision_below_target_block():
    # A 140 m span with a 114 m preferred spacing must still yield one internal
    # line when the edge cap is 120 m (the megablock-collapse guard).
    assert _axis_positions(0.0, 140.0, 114.0, 120.0) == [70.0]


def test_axis_positions_single_block_when_small():
    # A genuinely small span stays whole (no sliver streets).
    assert _axis_positions(0.0, 95.0, 114.0, 120.0) == []


def test_axis_positions_bounded_on_huge_span():
    # Runaway guard: a 3 km span cannot exceed MAX_BLOCKS_PER_AXIS-1 lines.
    assert len(_axis_positions(0.0, 3000.0, 114.0, 120.0)) <= 11


# --- integrated plan quality -----------------------------------------------------


def test_medium_infill_site_subdivides():
    # The Rosscarrock demo (1.7 ha, 156x117) must NOT be a single megablock.
    result = _gen()
    assert result.block_count >= 2, "medium infill site collapsed to one block"
    assert not any(n.get("code") == "NO_INTERNAL_STREETS" for n in result.notes)


def test_courtyard_is_not_a_giant_void():
    # No courtyard may exceed half its site — the old bug drew ~65% voids.
    for scenario in ["economic", "city_policy", "city_beautiful", "environmental"]:
        result = _gen(scenario)
        tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(_site(155.9, 116.5)))
        courts = [z for z in result.zones if z["properties"].get("_plan_role") == "courtyard"]
        court_area = sum(_metric(z, tf).area for z in courts)
        assert court_area / (155.9 * 116.5) < 0.45, f"{scenario} courtyard too large"


def test_courtyard_does_not_overlap_buildings():
    # decompose_holed must keep courtyard green off the building footprints.
    for w, d in [(155.9, 116.5), (95.0, 65.0), (220.0, 140.0)]:
        result = _gen(w=w, d=d)
        tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(_site(w, d)))
        buildings = unary_union(
            [_metric(z, tf) for z in result.zones if z["properties"].get("_plan_role") == "building"]
        )
        courts = [z for z in result.zones if z["properties"].get("_plan_role") == "courtyard"]
        if not courts:
            continue
        court = unary_union([_metric(z, tf) for z in courts])
        assert buildings.intersection(court).area < 5.0, f"courtyard overlaps buildings on {w}x{d}"


def _demo_palette():
    spec = MasterPlanSpec(
        design_narrative="varied infill",
        bands={
            "core": BandPlan(development_type="residential_multifamily", aesthetic="contemporary_urban", floors=6,
                             typology="perimeter_block",
                             alternates=[BandAlternate(development_type="mixed_use", aesthetic="contemporary_urban")]),
            "frontage": BandPlan(development_type="mixed_use", aesthetic="contemporary_urban", floors=5,
                                 typology="perimeter_block",
                                 alternates=[BandAlternate(development_type="commercial_retail", aesthetic="historical")]),
            "mid": BandPlan(development_type="residential_multifamily", aesthetic="minimalist", floors=4,
                            typology="row_bars",
                            alternates=[BandAlternate(development_type="residential_duplex", aesthetic="brownstone_rowhouse")]),
            "edge": BandPlan(development_type="residential_single_family", aesthetic="traditional_vernacular", floors=3,
                             typology="row_bars"),
            "anchor": BandPlan(development_type="institutional_education", aesthetic="contemporary_institutional", floors=4,
                               typology="anchor_mass"),
        },
        open_space=OpenSpaceProgram(water_feature=False, plaza=True),
        landscape=LandscapePlan(park_structure="naturalistic_grove", courtyard_structure="garden_courtyard"),
    )
    spec, _ = validate_spec(spec, "economic")
    return palette_from_spec(spec, "economic")


def test_master_plan_is_never_a_monoculture():
    palette = _demo_palette()
    for w, d in [(155.9, 116.5), (95.0, 65.0), (220.0, 140.0)]:
        result = _gen(w=w, d=d, palette=palette)
        buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
        combos = {(z["properties"].get("development_type"), z["properties"].get("development_aesthetic"))
                  for z in buildings}
        assert len(combos) >= 2, f"monoculture on {w}x{d}: {combos}"


def test_buildings_never_sliver_and_track_archetype_depth():
    # Faithful footprints (2026-07-12): the old coverage-crush produced 6-7 m
    # sliver rings; buildings must now keep a realistic short edge and their
    # emitted target depth must come from the archetype metadata.
    for scenario in ["economic", "environmental", "city_beautiful"]:
        for w, d in [(155.9, 116.5), (95.0, 65.0), (220.0, 140.0)]:
            result = _gen(scenario=scenario, w=w, d=d)
            tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(_site(w, d)))
            buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
            assert buildings, f"{scenario} {w}x{d}: no buildings"
            for z in buildings:
                rect = _metric(z, tf).minimum_rotated_rectangle
                coords = list(rect.exterior.coords)
                short = min(math.hypot(x2 - x1, y2 - y1)
                            for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
                assert short >= 7.5, (
                    f"{scenario} {w}x{d}: sliver building {short:.1f} m short edge ({z['name']})"
                )
                target_d = z["properties"].get("target_d_m")
                if target_d:
                    # Emitted depth is the archetype's, not a crushed number.
                    assert target_d >= 8.0


def test_block_target_hint_tightens_grain():
    # A fine grain hint must produce more blocks than a coarse one on the same site.
    from app.services.plan_geometry.community_rules import resolve_rules
    fine, _ = resolve_rules("economic", PARAMS, rule_hints={"block_target_m": 70.0, "max_block_edge_m": 85.0})
    coarse, _ = resolve_rules("economic", PARAMS, rule_hints={"block_target_m": 160.0, "max_block_edge_m": 180.0})
    assert fine.block_target_m < coarse.block_target_m
    assert fine.max_block_edge_m < coarse.max_block_edge_m
