"""Curvilinear street engine — translated bow-curve crescents with the
graduated (all -> spine -> straight) deterministic fallback guard.

Covers: byte-identical straight defaults, bow geometry + intersection parity,
scenario gating (curvilinear palettes vs city_beautiful/legacy straight),
crescent archetype tagging, end-to-end invariants on curved plans (budget,
partition, hole-free massing), the pure fallback predicate, degenerate/skinny/
L-shaped sites, locked-street round-trips, opt-in roundabouts on a bowed spine,
decompose_holed's cumulative ladder, and refinement stability."""

import math

import pytest
from shapely.geometry import Polygon

from app.services.plan_geometry.community_rules import MIN_ROW_M, resolve_rules
from app.services.plan_geometry.generator import (
    _curvilinear_fallback_reason,
    generate_plan_geometry,
)
from app.services.plan_geometry.parceling import decompose_holed
from app.services.plan_geometry.placement import PALETTES, effective_palette, palette_for, site_hash
from app.services.plan_geometry.street_graph import (
    CURVE_AMPLITUDE_MIN_M,
    generate_street_network,
)
from app.services.site_engine import (
    build_transformer,
    iter_polygons,
    local_metric_crs_for_polygon,
    project_geometry,
)

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=700.0, depth_m=520.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


def _l_site(width_m=700.0, depth_m=520.0, notch_w=300.0, notch_d=260.0) -> Polygon:
    """L-shaped site: rectangle minus its upper-right corner notch."""
    return Polygon(
        [
            _offset(0, 0),
            _offset(width_m, 0),
            _offset(width_m, depth_m - notch_d),
            _offset(width_m - notch_w, depth_m - notch_d),
            _offset(width_m - notch_w, depth_m),
            _offset(0, depth_m),
        ]
    )


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "landscape.tree_density": {"value": 0.6},
}

CURVE_NOTE_CODES = {"CURVILINEAR_APPLIED", "CURVILINEAR_FALLBACK", "CURVILINEAR_SKIPPED"}


def _metric_boundary(site):
    crs = local_metric_crs_for_polygon(site)
    return project_geometry(site, build_transformer("EPSG:4326", crs))


def _generate(scenario_id, site=None, **kwargs):
    return generate_plan_geometry(
        site_polygon_wgs84=site or _site(),
        scenario_id=scenario_id,
        scenario_label=scenario_id,
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        **kwargs,
    )


def _metric_area(zone, site) -> float:
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    return project_geometry(Polygon(zone["coordinates"]), tf).area


def _curve_notes(result):
    return [n for n in result.notes if n["code"] in CURVE_NOTE_CODES]


# ---------------------------------------------------------------------------
# Straight defaults stay byte-identical; palette gating matrix
# ---------------------------------------------------------------------------


def test_default_paths_stay_straight():
    boundary = _metric_boundary(_site())
    rules, _ = resolve_rules("city_policy", PARAMS)
    network = generate_street_network(boundary, rules, [])
    assert network.curve_mode == "none"
    assert all(len(seg.line.coords) == 2 for seg in network.segments)
    assert all(seg.sagitta_m == 0.0 for seg in network.segments)

    assert PALETTES["economic"].curvilinear and PALETTES["city_policy"].curvilinear
    assert PALETTES["environmental"].curvilinear
    assert PALETTES["environmental"].crescent_archetype_id is None
    assert not PALETTES["city_beautiful"].curvilinear
    for legacy in ("as_of_right", "lap_compliant", "climate_first"):
        assert not PALETTES[legacy].curvilinear
    assert not effective_palette("economic", "urban_grid").curvilinear
    assert effective_palette("economic", "transect_green").curvilinear
    assert not palette_for("custom_x", "city_beautiful").curvilinear


def test_curved_network_bows_and_keeps_intersection_parity():
    boundary = _metric_boundary(_site())
    rules, _ = resolve_rules("city_policy", PARAMS)
    seed = site_hash(boundary)
    straight = generate_street_network(boundary, rules, [])
    curved = generate_street_network(boundary, rules, [], curve_mode="all", seed=seed)

    assert curved.curve_mode == "all"
    spine = [s for s in curved.segments if s.role == "spine"]
    assert spine and spine[0].sagitta_m >= CURVE_AMPLITUDE_MIN_M
    assert all(line.is_simple for line in curved.centerlines)
    assert len(curved.intersections) == len(straight.intersections)
    # Slope cap: sagitta never exceeds 0.11 x work-frame span (+ tolerance).
    minx, _, maxx, _ = boundary.bounds
    assert all(s.sagitta_m <= 0.11 * (maxx - minx) + 1.0 for s in curved.segments)


def test_spine_mode_bows_only_the_spine():
    boundary = _metric_boundary(_site())
    rules, _ = resolve_rules("city_policy", PARAMS)
    curved = generate_street_network(boundary, rules, [], curve_mode="spine", seed=4)
    assert curved.curve_mode == "spine"
    for seg in curved.segments:
        if seg.role == "spine":
            assert seg.sagitta_m >= CURVE_AMPLITUDE_MIN_M
        else:
            assert seg.sagitta_m == 0.0


# ---------------------------------------------------------------------------
# End-to-end invariants on curved plans
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("scenario_id", ["economic", "city_policy", "environmental"])
def test_curved_scenarios_end_to_end_invariants(scenario_id):
    site = _site()
    result = _generate(scenario_id, site=site)

    notes = _curve_notes(result)
    assert len(notes) == 1, [n["code"] for n in notes]

    gi = result.geometry_inputs
    assert (
        abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"] - gi["site_area_m2"])
        / gi["site_area_m2"]
        < 0.06
    )

    # Street partition: road-zone areas (incl. lanes) sum to row_area exactly.
    road_area = sum(_metric_area(z, site) for z in result.zones if z["zone_type"] == "road")
    assert abs(road_area - gi["row_area_m2"]) < 1.0

    # Hole-free massing asserted on the IN-MEMORY masses (zone rings drop holes
    # at emission, so zone-coordinate assertions would be vacuous).
    mass_polys = [p for m in result.masses_m for p in iter_polygons(m)]
    assert mass_polys
    assert all(p.is_valid and len(p.interiors) == 0 for p in mass_polys)
    assert abs(sum(p.area for p in mass_polys) - gi["building_footprint_m2"]) < 1.0

    drawn = sum(_metric_area(z, site) for z in result.zones if z["zone_type"] == "building")
    assert abs(drawn - gi["building_footprint_m2"]) / gi["building_footprint_m2"] < 0.05

    framework = [z for z in result.zones if z["properties"].get("_plan_role") == "framework_height"]
    assert len(framework) == result.block_count
    codes = {n["code"] for n in result.notes}
    assert "PARCELS_LANDLOCKED" not in codes
    assert "MASS_STREET_COLLISION" not in codes

    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    triples = {
        (z["properties"]["development_type"], z["properties"]["development_aesthetic"], z["properties"]["floors"])
        for z in buildings
    }
    assert len(triples) <= 6


def test_curvilinear_scenarios_actually_curve_on_the_big_site():
    """The flagship path: on the 700x520 harness the guard must ACCEPT the
    curve for all three curvilinear scenarios — a silent fallback here means
    the feature is invisible exactly where it should shine."""
    for scenario_id in ("economic", "city_policy", "environmental"):
        result = _generate(scenario_id)
        notes = _curve_notes(result)
        assert notes and notes[0]["code"] == "CURVILINEAR_APPLIED", (scenario_id, notes)


def test_city_beautiful_and_legacy_stay_straight():
    for scenario_id in ("city_beautiful", "lap_compliant"):
        result = _generate(scenario_id)
        assert not _curve_notes(result), scenario_id
        roads = [z for z in result.zones if z["zone_type"] == "road"]
        assert not any(z["properties"].get("road_archetype_id") == "london_crescent_road" for z in roads)
    beautiful = _generate("city_beautiful")
    spine = [z for z in beautiful.zones if z["properties"].get("street_role") == "spine"]
    assert spine and all(z["properties"].get("road_archetype_id") == "haussmann_boulevard" for z in spine)
    greens = [z for z in beautiful.zones if z["zone_type"] == "green_space"]
    assert any(z["properties"].get("green_kind") == "pond" for z in greens)
    assert any(z["properties"].get("green_kind") == "plaza" for z in greens)


def test_crescent_tagging():
    for scenario_id in ("economic", "city_policy"):
        result = _generate(scenario_id)
        locals_ = [z for z in result.zones if z["properties"].get("street_role") == "local"]
        crescents = [z for z in locals_ if z["properties"].get("road_archetype_id") == "london_crescent_road"]
        assert crescents, scenario_id
        assert all(MIN_ROW_M <= z["properties"]["width"] < 15 for z in crescents)
        # Straight cross-streets survive alongside the crescents, and the
        # LEGO-only public-realm contract now gives those ordinary locals a
        # deterministic measured street archetype instead of leaving them
        # untyped for the frontend to infer.
        assert any(z["properties"].get("road_archetype_id") != "london_crescent_road" for z in locals_), scenario_id
        assert all(
            isinstance(z["properties"].get("road_archetype_id"), str) and z["properties"]["road_archetype_id"]
            for z in locals_
        ), scenario_id

    environmental = _generate("environmental")
    env_locals = [z for z in environmental.zones if z["properties"].get("street_role") == "local"]
    assert env_locals and all(z["properties"].get("road_archetype_id") == "woonerf_shared_street" for z in env_locals)


def test_curved_determinism():
    a = _generate("economic")
    b = _generate("economic")
    assert [(z["name"], z["properties"]) for z in a.zones] == [(z["name"], z["properties"]) for z in b.zones]
    assert [z["coordinates"] for z in a.zones] == [z["coordinates"] for z in b.zones]


# ---------------------------------------------------------------------------
# Fallback guard
# ---------------------------------------------------------------------------


def test_fallback_reason_matrix():
    base = dict(
        n_curved=8, n_straight=8, n_curved_large=6, n_straight_large=6, sliver_curved=0.005, sliver_straight=0.005
    )
    assert _curvilinear_fallback_reason(**base) is None
    assert _curvilinear_fallback_reason(**{**base, "n_curved": 1}) == "BLOCKS_COLLAPSED"
    assert _curvilinear_fallback_reason(**{**base, "n_curved": 6}) == "BLOCKS_MERGED"
    assert _curvilinear_fallback_reason(**{**base, "n_curved_large": 1}) == "BLOCKS_FRAGMENTED"
    assert (
        _curvilinear_fallback_reason(**{**base, "sliver_curved": 0.03, "sliver_straight": 0.005}) == "SLIVER_EXCESS_REL"
    )
    assert (
        _curvilinear_fallback_reason(**{**base, "sliver_curved": 0.05, "sliver_straight": 0.045}) == "SLIVER_EXCESS_ABS"
    )


def test_skinny_site_skips_with_exactly_one_note():
    # 480x90: the short axis stays a single block (< the 120 m edge cap), so the
    # long axis has no interior rows to bow (NO_LONG_AXIS_ROWS). (A 140 m depth
    # now subdivides under the inner-city grain, so it no longer qualifies.)
    result = _generate("economic", site=_site(480, 90))
    notes = _curve_notes(result)
    assert len(notes) == 1
    assert notes[0]["code"] == "CURVILINEAR_SKIPPED"
    gi = result.geometry_inputs
    assert (
        abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"] - gi["site_area_m2"])
        / gi["site_area_m2"]
        < 0.06
    )


def test_l_shaped_site_survives_curving():
    site = _l_site()
    result = _generate("city_policy", site=site)
    assert len(_curve_notes(result)) == 1
    gi = result.geometry_inputs
    assert (
        abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"] - gi["site_area_m2"])
        / gi["site_area_m2"]
        < 0.06
    )
    assert result.block_count >= 2
    road_area = sum(_metric_area(z, site) for z in result.zones if z["zone_type"] == "road")
    assert abs(road_area - gi["row_area_m2"]) < 1.0


def test_tiny_site_stays_note_free():
    result = _generate("economic", site=_site(110, 100))
    assert not _curve_notes(result)  # degenerate paths never mention curvature
    assert result.block_count == 1


def test_curved_locked_streets_roundtrip():
    from shapely.ops import unary_union

    site = _site()
    first = _generate("economic", site=site)
    assert _curve_notes(first)[0]["code"] == "CURVILINEAR_APPLIED"
    locked = unary_union([Polygon(z["coordinates"]) for z in first.zones if z["zone_type"] == "road"])
    second = _generate("economic", site=site, locked_street_area_wgs84=locked)
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    assert not _curve_notes(second)  # locked = user froze circulation
    roads = [z for z in second.zones if z["zone_type"] == "road"]
    assert roads and not any(z["properties"].get("street_role") == "lane" for z in roads)
    locked_area = sum(_metric_area(z, site) for z in first.zones if z["zone_type"] == "road")
    second_area = sum(_metric_area(z, site) for z in second.zones if z["zone_type"] == "road")
    assert abs(second_area - locked_area) / locked_area < 0.02


def test_roundabouts_are_opt_in_and_survive_curved_spine():
    site = _site()
    result = _generate("city_policy", site=site)
    assert _curve_notes(result)[0]["code"] == "CURVILINEAR_APPLIED"
    roundabouts = [z for z in result.zones if z["properties"].get("road_archetype_id") == "roundabout"]
    assert not roundabouts

    boundary = _metric_boundary(site)
    rules, _ = resolve_rules("city_policy", PARAMS)
    network = generate_street_network(
        boundary,
        rules,
        [],
        include_roundabouts=True,
        curve_mode="spine",
        seed=site_hash(boundary),
    )
    assert network.curve_mode == "spine"
    assert network.roundabouts
    spine = next(segment.line for segment in network.segments if segment.role == "spine")
    assert all(point.distance(spine) < 0.5 for point, _radius in network.roundabouts)


# ---------------------------------------------------------------------------
# decompose_holed cumulative ladder
# ---------------------------------------------------------------------------


def test_decompose_holed_offset_hole():
    # The hole sits away from BOTH centroid cut axes — a single centered cross
    # leaves it intact; the cumulative ladder re-cuts at the hole and clears it.
    from shapely.geometry import box

    frame = box(0, 0, 200, 200)
    mass = frame.difference(box(160, 160, 185, 185))
    assert any(p.interiors for p in iter_polygons(mass))
    result = decompose_holed(mass, frame)
    pieces = list(iter_polygons(result))
    assert pieces and all(len(p.interiors) == 0 for p in pieces)
    assert abs(sum(p.area for p in pieces) - mass.area) / mass.area < 0.01


def test_decompose_holed_crescent_annulus():
    from shapely.geometry import Point as ShapelyPoint

    ring = ShapelyPoint(100, 100).buffer(80).difference(ShapelyPoint(100, 100).buffer(50))
    frame = ShapelyPoint(100, 100).buffer(80)
    result = decompose_holed(ring, frame)
    pieces = list(iter_polygons(result))
    assert pieces and all(len(p.interiors) == 0 for p in pieces)


# ---------------------------------------------------------------------------
# Refinement stability
# ---------------------------------------------------------------------------


def test_refinement_stability_curved():
    from app.services.plan_geometry.refinement import run_refinement_loop

    def run():
        return run_refinement_loop(
            site_polygon_wgs84=_site(),
            scenario_id="economic",
            scenario_label="Economic",
            parameters=PARAMS,
            dna={},
            road_features=[],
            district_features=[],
        )

    result_a, _, iterations_a = run()
    result_b, _, iterations_b = run()
    assert _curve_notes(result_a)
    assert len(iterations_a) == len(iterations_b)
    assert [z["coordinates"] for z in result_a.zones] == [z["coordinates"] for z in result_b.zones]
