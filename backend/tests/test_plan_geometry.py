"""Plan Geometry Engine — deterministic drawing verified against the P2 gates:
blocks in scale, parcels street-fronting, fire clear-widths pass, honest
degradation on degenerate sites, locked-streets path, ceiling clamps."""

import math

from shapely.geometry import Polygon, mapping

from app.services.plan_geometry.community_rules import MIN_ROW_M, resolve_rules
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.parceling import building_mass_for_block, subdivide_block
from app.services.plan_geometry.street_graph import generate_street_network

# ~500 x 340 m site in the Beltline (WGS84)
LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=500.0, depth_m=340.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


def _road_feature(start, end):
    return {"geometry": mapping(__import__("shapely.geometry", fromlist=["LineString"]).LineString([start, end])),
            "properties": {"full_name": "12 AV SW", "ctp_class": "Arterial Street"}}


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "buildings.development_type": {"value": "mixed_use"},
}


def test_rules_enforce_fire_clear_width_floor():
    rules, notes = resolve_rules("as_of_right", {"streets.row_width_m": {"value": 7.0}})
    assert rules.row_width_m == MIN_ROW_M
    assert rules.clear_width_m >= 6.0
    assert any(n["code"] == "FIRE_CLEAR_WIDTH_FLOOR" for n in notes)


def test_full_generation_meets_p2_gates():
    roads = [
        _road_feature(_offset(-80, 170), _offset(80, 170)),   # entering from the west
        _road_feature(_offset(250, -80), _offset(250, 80)),   # entering from the south
    ]
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP Aligned",
        parameters=PARAMS, road_features=roads, district_features=[],
    )

    types = {z["zone_type"] for z in result.zones}
    assert {"road", "green_space", "building"} <= types
    assert result.block_count >= 2
    assert result.parcel_count >= result.block_count  # every block subdivided
    assert all(len(z["coordinates"]) >= 3 for z in result.zones)
    assert all(z["properties"]["_plan_scenario"] == "lap_compliant" for z in result.zones)
    assert all(z["properties"]["_imported_from"] == "Plan — LAP Aligned" for z in result.zones)

    codes = {n["code"] for n in result.notes}
    assert "FIRE_CLEAR_WIDTH_OK" in codes
    assert "PARCELS_LANDLOCKED" not in codes
    assert "MASS_STREET_COLLISION" not in codes

    gi = result.geometry_inputs
    # Land budget closes: streets + open + blocks ≈ gross (small boundary slivers allowed)
    assert abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"]
               - gi["site_area_m2"]) / gi["site_area_m2"] < 0.06
    assert gi["building_footprint_m2"] > 0
    assert gi["gfa_m2"] >= gi["building_footprint_m2"] * 5  # ~6 storeys

    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert all(z["properties"]["floors"] > 0 and z["properties"]["height"] > 0 for z in buildings)
    assert result.intersection_density_per_km2 > 0


def test_block_scale_via_street_network():
    from app.services.site_engine import (
        build_transformer, cleanup_developable_blocks, local_metric_crs_for_polygon, project_geometry,
    )

    site = _site()
    crs = local_metric_crs_for_polygon(site)
    boundary_m = project_geometry(site, build_transformer("EPSG:4326", crs))
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    network = generate_street_network(boundary_m, rules, [])
    # Same morphological opening the generator applies (hairline-bridge severing).
    developable = boundary_m.difference(network.street_area).buffer(-0.05).buffer(0.05)
    blocks = cleanup_developable_blocks(developable, sliver_area_threshold=400)
    assert len(blocks) >= 4
    for block in blocks:
        rect = block.minimum_rotated_rectangle
        coords = list(rect.exterior.coords)
        long_edge = max(math.hypot(x2 - x1, y2 - y1)
                        for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
        assert long_edge <= rules.block_target_m + rules.row_width_m + 1.0


def test_parcels_front_the_street_and_slivers_merge():
    block = Polygon([(0, 0), (180, 0), (180, 70), (0, 70)])
    parcels = subdivide_block(block, 22.0)
    assert 6 <= len(parcels) <= 10
    assert all(p.area >= 120.0 for p in parcels)
    for parcel in parcels:
        assert parcel.distance(block.exterior) < 0.5  # street-fronting


def test_building_mass_respects_coverage_cap():
    from app.services.plan_geometry.community_rules import resolve_rules as rr
    rules, _ = rr("climate_first", PARAMS)  # coverage 0.45
    block = Polygon([(0, 0), (150, 0), (150, 120), (0, 120)])
    mass, info = building_mass_for_block(block, rules)
    assert mass is not None
    assert info["coverage_of_block"] <= rules.coverage_ratio + 0.05


def test_tiny_site_degrades_to_single_block_plan():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(60, 45), scenario_id="as_of_right", scenario_label="AoR",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    codes = {n["code"] for n in result.notes}
    assert codes & {"SITE_TOO_SMALL", "NO_INTERNAL_STREETS"}
    assert result.block_count == 1
    assert any(z["zone_type"] == "building" for z in result.zones)  # still buildable


def test_locked_streets_are_reused_not_regenerated():
    site = _site()
    first = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id="lap_compliant", scenario_label="LAP",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    street_rings = [z["coordinates"] for z in first.zones if z["zone_type"] == "road"]
    assert street_rings
    from shapely.ops import unary_union
    locked = unary_union([Polygon(r) for r in street_rings])

    second = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id="lap_compliant", scenario_label="LAP",
        parameters={**PARAMS, "streets.row_width_m": {"value": 20.0}},  # would change streets if unlocked
        road_features=[], district_features=[], locked_street_area_wgs84=locked,
    )
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    locked_area = locked.area
    second_street_area = sum(
        Polygon(z["coordinates"]).area for z in second.zones if z["zone_type"] == "road"
    )
    assert abs(second_street_area - locked_area) / locked_area < 0.02  # same network


def test_floors_clamped_by_district_ceiling():
    district = {
        "geometry": mapping(_site(1000, 1000)),  # covers everything
        "properties": {"lu_code": "CC-MH", "height": 19.2},  # 6 storeys at 3.2 m
    }
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="as_of_right", scenario_label="AoR",
        parameters={**PARAMS, "buildings.floors": {"value": 20}},
        road_features=[], district_features=[district],
    )
    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert buildings
    assert all(z["properties"]["floors"] <= 6.01 for z in buildings)
    assert any(n["code"] == "FLOORS_CLAMPED" for n in result.notes)
