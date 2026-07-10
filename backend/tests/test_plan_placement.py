"""Placement policy — strategic per-zone variety verified: deterministic
tagging, density transect, street hierarchy, park mix, typology massing,
laneways/pond/roundabouts, and graceful degradation on locked streets."""

import math

from shapely.geometry import Polygon

from app.services.plan_geometry.community_rules import LANE_ROW_M, MIN_ROW_M
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.placement import CATALOG_DEV_TYPES
from app.services.site_engine import (
    build_transformer,
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


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "buildings.development_type": {"value": "mixed_use"},
    "buildings.development_aesthetic": {"value": "contemporary"},
    "landscape.tree_density": {"value": 0.6},
}


def _generate(scenario_id="climate_first", label="Climate First", site=None, params=None):
    return generate_plan_geometry(
        site_polygon_wgs84=site or _site(), scenario_id=scenario_id, scenario_label=label,
        parameters=params or PARAMS, road_features=[], district_features=[],
    )


def _metric_area(zone, site) -> float:
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    return project_geometry(Polygon(zone["coordinates"]), tf).area


def test_generation_is_deterministic():
    a = _generate()
    b = _generate()
    assert [(z["name"], z["properties"]) for z in a.zones] == \
           [(z["name"], z["properties"]) for z in b.zones]
    assert [z["coordinates"] for z in a.zones] == [z["coordinates"] for z in b.zones]


def test_transect_bands_and_single_anchor():
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    bands = {z["properties"]["_plan_band"] for z in buildings}
    assert "edge" in bands

    # Edge steps down; every type comes from the catalog; real variety.
    edge_floors = [z["properties"]["floors"] for z in buildings
                   if z["properties"]["_plan_band"] == "edge"]
    other_floors = [z["properties"]["floors"] for z in buildings
                    if z["properties"]["_plan_band"] not in ("edge", "anchor")]
    assert edge_floors and max(edge_floors) <= 3.5
    assert other_floors and max(other_floors) > max(edge_floors)

    dev_types = {z["properties"]["development_type"] for z in buildings}
    assert dev_types <= CATALOG_DEV_TYPES
    assert len(dev_types) >= 3

    # Exactly one anchor BLOCK (its mass may decompose into several zones).
    anchor_blocks = {z["name"].split(" · Building")[0] for z in buildings
                     if z["properties"]["_plan_band"] == "anchor"}
    assert len(anchor_blocks) == 1


def test_street_hierarchy_spine_and_locals():
    result = _generate()
    roads = [z for z in result.zones if z["zone_type"] == "road"]
    spine = [z for z in roads if z["properties"].get("street_role") == "spine"]
    locals_ = [z for z in roads if z["properties"].get("street_role") == "local"]
    assert spine and all(z["properties"]["width"] >= 22.0 for z in spine)
    assert locals_ and all(MIN_ROW_M <= z["properties"]["width"] < 15.0 for z in locals_)

    # as_of_right stamps the arterial directly (unreachable via width bands).
    aor = _generate("as_of_right", "AoR")
    aor_spine = [z for z in aor.zones if z["properties"].get("street_role") == "spine"]
    assert aor_spine and all(
        z["properties"]["road_archetype_id"] == "arterial_boulevard" for z in aor_spine
    )


def test_park_mix_and_resolver_gap():
    site = _site()
    result = _generate(site=site)
    greens = [z for z in result.zones if z["properties"].get("_plan_role") == "open_space"]
    areas_banded = [_metric_area(z, site) for z in greens
                    if not z["properties"].get("green_space_archetype_id")]
    assert any(a >= 2000.0 for a in areas_banded)          # neighborhood park
    assert any(200.0 <= a <= 900.0 for a in areas_banded)  # pocket park
    # 900-2000 m² falls between the pocket and neighborhood catalog ranges —
    # band-resolved greens must never land there (direct-id zones are exempt).
    assert not any(900.0 < a < 2000.0 for a in areas_banded)


def test_palette_stays_under_render_caps():
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    triples = {(z["properties"]["development_type"], z["properties"]["development_aesthetic"],
                z["properties"]["floors"]) for z in buildings}
    assert len(triples) <= 6
    ids = {z["properties"].get("road_archetype_id") for z in result.zones} | \
          {z["properties"].get("green_space_archetype_id") for z in result.zones}
    assert len(triples) + len(ids - {None}) + 3 <= 16  # + street bands; GPT keeps 15 refs


def test_typology_masses_are_hole_free_and_courtyards_only_on_perimeter():
    for scenario in ("climate_first", "as_of_right", "lap_compliant"):
        result = _generate(scenario, scenario)
        buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
        assert buildings
        for zone in buildings:
            poly = Polygon(zone["coordinates"])
            assert poly.is_valid and len(poly.interiors) == 0
            assert zone["properties"]["coverage_of_block"] <= 0.66  # cap + tolerance
        # Courtyards may only come from perimeter-typology blocks.
        perimeter_blocks = {z["name"].split(" · Building")[0] for z in buildings
                            if z["properties"].get("typology") == "perimeter_block"}
        for zone in result.zones:
            if zone["properties"].get("_plan_role") != "courtyard":
                continue
            block_name = zone["name"].rsplit(" courtyard", 1)[0]
            assert block_name in perimeter_blocks


def test_phase3_lanes_pond_roundabout_and_budget():
    site = _site()
    result = _generate(site=site)  # climate_first: laneways + water feature

    gi = result.geometry_inputs
    assert abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"]
               - gi["site_area_m2"]) / gi["site_area_m2"] < 0.06

    lanes = [z for z in result.zones if z["properties"].get("street_role") == "lane"]
    assert lanes
    assert all(z["properties"]["width"] == LANE_ROW_M for z in lanes)
    assert all(z["properties"]["road_archetype_id"] == "toronto_laneway" for z in lanes)

    ponds = [z for z in result.zones
             if z["properties"].get("green_space_archetype_id") == "stormwater_retention_pond"]
    assert ponds
    pond_area = sum(_metric_area(z, site) for z in ponds)
    assert 300.0 <= pond_area <= 9600.0
    greenways = [z for z in result.zones
                 if z["properties"].get("green_space_archetype_id") == "linear_park_greenway"]
    assert greenways
    for zone in ponds + greenways:
        poly = Polygon(zone["coordinates"])
        assert poly.is_valid and len(poly.interiors) == 0

    roundabouts = [z for z in result.zones
                   if z["properties"].get("road_archetype_id") == "roundabout"]
    assert roundabouts
    radius = (result.rules["spine_row_width_m"] + 6.0) / 2
    for zone in roundabouts:
        assert abs(_metric_area(zone, site) - math.pi * radius ** 2) / (math.pi * radius ** 2) < 0.15

    # Pond geometry is stable across runs (site-hash seeded, no RNG).
    again = _generate(site=site)
    ponds_b = [z for z in again.zones
               if z["properties"].get("green_space_archetype_id") == "stormwater_retention_pond"]
    assert [z["coordinates"] for z in ponds] == [z["coordinates"] for z in ponds_b]


def test_locked_streets_degrade_gracefully():
    from shapely.ops import unary_union

    site = _site()
    first = _generate(site=site)
    locked = unary_union([Polygon(z["coordinates"]) for z in first.zones
                          if z["zone_type"] == "road"])
    second = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id="climate_first", scenario_label="Climate First",
        parameters=PARAMS, road_features=[], district_features=[],
        locked_street_area_wgs84=locked,
    )
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    roads = [z for z in second.zones if z["zone_type"] == "road"]
    assert roads
    # No new lanes on a frozen network — the user locked circulation.
    assert not any(z["properties"].get("street_role") == "lane" for z in roads)
    buildings = [z for z in second.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings and all(
        z["properties"]["development_type"] in CATALOG_DEV_TYPES for z in buildings
    )
