"""Plan Geometry Engine — deterministic drawing verified against the P2 gates:
blocks in scale, parcels street-fronting, fire clear-widths pass, honest
degradation on degenerate sites, locked-streets path, ceiling clamps."""

import math

import pytest
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.ops import unary_union

from app.services.plan_geometry.community_rules import MIN_ROW_M, resolve_rules
from app.services.plan_geometry.generator import (
    _pack_exact_target_cells,
    _is_drivable_context_feature,
    _normalize_site_polygon,
    _park_access_points_m,
    generate_plan_geometry,
)
from app.services.plan_geometry.layout_validation import validate_plan
from app.services.plan_geometry.parceling import building_mass_for_block, subdivide_block
from app.services.plan_geometry.street_graph import (
    _append_context_connectors,
    _context_grid_angle_deg,
    StreetNetwork,
    StreetSegment,
    entry_points_from_paths,
    entry_points_from_roads,
    generate_street_network,
)
from app.services.plan_geometry.archetypes import TargetFootprint

# ~500 x 340 m site in the Beltline (WGS84)
LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=500.0, depth_m=340.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


def _road_feature(start, end):
    return {
        "geometry": mapping(__import__("shapely.geometry", fromlist=["LineString"]).LineString([start, end])),
        "properties": {"full_name": "12 AV SW", "ctp_class": "Arterial Street"},
    }


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "buildings.development_type": {"value": "mixed_use"},
    "buildings.development_aesthetic": {"value": "contemporary"},
    "landscape.tree_density": {"value": 0.6},
}


def test_site_polygon_normalizer_repairs_only_a_negligible_closing_sliver():
    site = Polygon(
        [
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
            (0.0001, -0.0001),
        ]
    )

    repaired, note = _normalize_site_polygon(site)

    assert repaired.is_valid
    assert repaired.area > 99.9
    assert note and note["code"] == "SITE_BOUNDARY_REPAIRED"


def test_site_polygon_normalizer_rejects_material_bow_tie():
    site = Polygon([(0.0, 0.0), (10.0, 10.0), (0.0, 10.0), (10.0, 0.0)])

    with pytest.raises(ValueError, match="multiple material areas"):
        _normalize_site_polygon(site)


def test_rules_enforce_fire_clear_width_floor():
    rules, notes = resolve_rules("as_of_right", {"streets.row_width_m": {"value": 7.0}})
    assert rules.row_width_m == MIN_ROW_M
    assert rules.clear_width_m >= 6.0
    assert any(n["code"] == "FIRE_CLEAR_WIDTH_FLOOR" for n in notes)


def test_full_generation_meets_p2_gates():
    roads = [
        _road_feature(_offset(-80, 170), _offset(80, 170)),  # entering from the west
        _road_feature(_offset(250, -80), _offset(250, 80)),  # entering from the south
    ]
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="lap_compliant",
        scenario_label="LAP Aligned",
        parameters=PARAMS,
        road_features=roads,
        district_features=[],
    )

    types = {z["zone_type"] for z in result.zones}
    assert {"road", "green_space", "building"} <= types
    assert result.block_count >= 2
    assert result.parcel_count >= result.block_count  # every block subdivided
    assert all(len(z["coordinates"]) >= 3 for z in result.zones)
    assert all(Polygon(z["coordinates"]).is_valid for z in result.zones)
    assert all(z["properties"]["_plan_scenario"] == "lap_compliant" for z in result.zones)
    # Plan zones share one layer; height-framework zones form their OWN layer.
    for zone in result.zones:
        expected = (
            "Height framework — LAP Aligned"
            if zone["properties"].get("_plan_role") == "framework_height"
            else "Plan — LAP Aligned"
        )
        assert zone["properties"]["_imported_from"] == expected

    codes = {n["code"] for n in result.notes}
    assert "FIRE_CLEAR_WIDTH_OK" in codes
    assert "PARCELS_LANDLOCKED" not in codes
    assert "MASS_STREET_COLLISION" not in codes
    assert "MASS_OPEN_SPACE_COLLISION" not in codes
    assert "MASS_MASS_COLLISION" not in codes

    gi = result.geometry_inputs
    # Land budget closes: streets + open + blocks ≈ gross (small boundary slivers allowed)
    assert (
        abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"] - gi["site_area_m2"])
        / gi["site_area_m2"]
        < 0.06
    )
    assert gi["building_footprint_m2"] > 0
    assert gi["gfa_m2"] >= gi["building_footprint_m2"] * 5  # ~6 storeys

    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert all(z["properties"]["floors"] > 0 and z["properties"]["height"] > 0 for z in buildings)
    assert result.intersection_density_per_km2 > 0

    # Semantic hints for the render pipeline's archetype resolver: per-zone
    # strategic tagging — every value a real catalog developmentType, and the
    # placement policy produces genuine variety, not one uniform type.
    from app.services.plan_geometry.placement import CATALOG_DEV_TYPES

    dev_types = {z["properties"]["development_type"] for z in buildings}
    assert dev_types <= CATALOG_DEV_TYPES
    assert len(dev_types) >= 2
    assert all(z["properties"].get("development_aesthetic") for z in buildings)
    parks = [
        z for z in result.zones if z["zone_type"] == "green_space" and z["properties"].get("_plan_role") == "open_space"
    ]
    assert parks and all(z["properties"]["tree_density"] == 0.6 for z in parks)
    assert any(z["properties"].get("park_access_points") for z in parks)

    # Street hierarchy: a wide main spine plus narrower locals, every full
    # street at or above the CSPS033-derived minimum ROW.
    roads = [z for z in result.zones if z["zone_type"] == "road"]
    widths = {z["properties"]["width"] for z in roads}
    assert len(widths) >= 2
    assert max(widths) >= 22.0
    non_lane = [z["properties"]["width"] for z in roads if z["properties"].get("street_role") != "lane"]
    assert non_lane and all(w >= MIN_ROW_M for w in non_lane)


def test_collision_validation_rejects_buildings_over_parks_but_allows_shared_edges():
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    building = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    overlapping_park = Polygon([(5, 0), (15, 0), (15, 10), (5, 10)])
    edge_touching_park = Polygon([(10, 0), (20, 0), (20, 10), (10, 10)])

    overlap_notes = validate_plan(
        rules=rules,
        network=StreetNetwork(),
        blocks_m=[],
        parcels_by_block=[],
        masses_m=[building],
        open_spaces_m=[overlapping_park],
    )
    touching_notes = validate_plan(
        rules=rules,
        network=StreetNetwork(),
        blocks_m=[],
        parcels_by_block=[],
        masses_m=[building],
        open_spaces_m=[edge_touching_park],
    )

    assert any(note["code"] == "MASS_OPEN_SPACE_COLLISION" for note in overlap_notes)
    assert all(note["code"] != "MASS_OPEN_SPACE_COLLISION" for note in touching_notes)


def test_collision_validation_rejects_overlapping_building_masses():
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    first = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    second = Polygon([(5, 0), (15, 0), (15, 10), (5, 10)])

    notes = validate_plan(
        rules=rules,
        network=StreetNetwork(),
        blocks_m=[],
        parcels_by_block=[],
        masses_m=[first, second],
    )

    assert any(note["code"] == "MASS_MASS_COLLISION" for note in notes)


def test_block_scale_via_street_network():
    from app.services.site_engine import (
        build_transformer,
        cleanup_developable_blocks,
        local_metric_crs_for_polygon,
        project_geometry,
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
        long_edge = max(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
        assert long_edge <= rules.block_target_m + rules.row_width_m + 1.0


def test_context_entries_detect_parallel_frontages_not_only_crossings():
    boundary = Polygon([(0, 0), (120, 0), (120, 90), (0, 90)])
    frontage_road = LineString([(-20, -18), (140, -18)])
    distant_road = LineString([(-20, -80), (140, -80)])
    frontage_path = LineString([(24, -12), (54, -12)])

    road_entries = entry_points_from_roads([frontage_road, distant_road], boundary)
    path_entries = entry_points_from_paths([frontage_path], boundary)

    assert len(road_entries) == 1
    assert road_entries[0].distance(Point(60, 0)) < 1.0
    assert len(path_entries) == 1
    assert path_entries[0].distance(Point(39, 0)) < 1.0


def test_context_grid_orientation_recovers_a_rotated_orthogonal_pattern():
    boundary = Polygon([(0, 0), (400, 0), (400, 250), (0, 250)])
    angle = math.radians(30.0)
    along = (math.cos(angle), math.sin(angle))
    across = (-math.sin(angle), math.cos(angle))
    center = Point(200, 125)
    roads = []
    for offset in (-90.0, 0.0, 90.0):
        origin = Point(center.x + across[0] * offset, center.y + across[1] * offset)
        roads.append(
            LineString(
                [
                    (origin.x - along[0] * 400, origin.y - along[1] * 400),
                    (origin.x + along[0] * 400, origin.y + along[1] * 400),
                ]
            )
        )
    for offset in (-100.0, 100.0):
        origin = Point(center.x + along[0] * offset, center.y + along[1] * offset)
        roads.append(
            LineString(
                [
                    (origin.x - across[0] * 300, origin.y - across[1] * 300),
                    (origin.x + across[0] * 300, origin.y + across[1] * 300),
                ]
            )
        )

    orientation = _context_grid_angle_deg(roads, boundary)

    assert orientation is not None
    resolved, confidence, segment_count = orientation
    assert resolved == pytest.approx(30.0, abs=0.2)
    assert confidence > 0.95
    assert segment_count >= 5


def test_context_grid_orientation_rejects_directionally_ambiguous_streets():
    boundary = Polygon([(0, 0), (400, 0), (400, 250), (0, 250)])
    center = Point(200, 125)
    roads = []
    for angle_deg in (0.0, 22.5, 45.0, 67.5):
        angle = math.radians(angle_deg)
        roads.append(
            LineString(
                [
                    (center.x - math.cos(angle) * 250, center.y - math.sin(angle) * 250),
                    (center.x + math.cos(angle) * 250, center.y + math.sin(angle) * 250),
                ]
            )
        )

    assert _context_grid_angle_deg(roads, boundary) is None


def test_generated_network_records_contextual_grid_alignment():
    boundary = Polygon([(0, 0), (400, 0), (400, 250), (0, 250)])
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    angle = math.radians(25.0)
    roads = [
        LineString([(-50, 20), (450, 20 + math.tan(angle) * 500)]),
        LineString([(-50, 90), (450, 90 + math.tan(angle) * 500)]),
    ]

    network = generate_street_network(boundary, rules, [], context_road_lines=roads)

    assert network.grid_orientation_source == "surrounding_street_grid"
    assert network.grid_angle_deg == pytest.approx(25.0, abs=0.2)
    assert network.grid_orientation_confidence is not None
    assert any(note["code"] == "CONTEXT_GRID_ORIENTATION_APPLIED" for note in network.notes)


def test_road_context_entries_are_bounded_and_spaced_like_real_gateways():
    boundary = Polygon([(0, 0), (260, 0), (260, 160), (0, 160)])
    fragmented_crossings = [LineString([(x, -30), (x, 30)]) for x in (20, 48, 76, 104, 132, 160, 188, 216, 244)]

    entries = entry_points_from_roads(fragmented_crossings, boundary)

    assert len(entries) == 4
    assert all(first.distance(second) >= 50.0 for index, first in enumerate(entries) for second in entries[index + 1 :])


def test_park_access_points_prefer_paths_and_land_on_frontages():
    park = Polygon([(0, 0), (40, 0), (40, 30), (0, 30)])
    network = StreetNetwork(
        segments=[
            StreetSegment(LineString([(-10, -6), (50, -6)]), 12.0, "local"),
            StreetSegment(LineString([(47, -10), (47, 40)]), 14.0, "path"),
            StreetSegment(LineString([(-20, 80), (60, 80)]), 16.0, "spine"),
        ]
    )

    points = _park_access_points_m(park, network)

    assert len(points) == 2
    assert points[0].distance(Point(40, 15)) < 0.01
    assert points[1].distance(Point(20, 0)) < 0.01
    assert all(park.boundary.distance(point) < 0.01 for point in points)


def test_network_connects_every_feasible_context_anchor_exactly():
    boundary = Polygon([(0, 0), (500, 0), (500, 340), (0, 340)])
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    road_entries = [Point(0, 70), Point(500, 270)]
    path_entries = [Point(80, 0)]

    network = generate_street_network(
        boundary,
        rules,
        road_entries,
        path_entry_points=path_entries,
    )
    connected = unary_union(network.centerlines)

    assert network.entries_served == 2
    assert network.path_entries_served == 1
    assert all(point.distance(connected) < 0.01 for point in road_entries + path_entries)
    assert any(segment.role == "path" for segment in network.segments)
    assert any(note["code"] == "CONTEXT_CONNECTIONS_APPLIED" for note in network.notes)


def test_context_connector_tries_visible_network_line_on_concave_site():
    # The horizontal line is slightly nearer but lies across the missing
    # north-east notch. The vertical line remains visible through the site's
    # southern arm and must be used instead of abandoning the entrance.
    boundary = Polygon([(0, 0), (120, 0), (120, 40), (40, 40), (40, 120), (0, 120)])
    entry = Point(120, 30)
    centerlines = [
        LineString([(35, 0), (35, 120)]),
        LineString([(0, 50), (40, 50)]),
    ]
    segments = []

    added = _append_context_connectors(
        boundary_m=boundary,
        entries=[entry],
        role="local",
        width_m=14.0,
        centerlines=centerlines,
        segments=segments,
    )

    assert added == 1
    assert len(segments) == 1
    assert entry.distance(unary_union(centerlines)) < 0.01
    assert boundary.buffer(0.05).covers(segments[0].line)


def test_context_connector_uses_inward_route_instead_of_half_width_edge_route():
    boundary = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    entry = Point(20, 0)
    # The 10 m candidate is the shortest centreline connection, but it runs
    # along the parcel edge and only half of a 14 m ROW would survive clipping.
    # The 20 m inward candidate is the shortest truthful full-section route.
    centerlines = [
        LineString([(30, 0), (100, 0)]),
        LineString([(0, 20), (100, 20)]),
    ]
    segments = []

    added = _append_context_connectors(
        boundary_m=boundary,
        entries=[entry],
        role="local",
        width_m=14.0,
        centerlines=centerlines,
        segments=segments,
    )

    assert added == 1
    connector = segments[0].line
    assert Point(connector.coords[-1]).distance(Point(20, 20)) < 0.01
    corridor = connector.buffer(7.0, cap_style=2, join_style=2)
    assert corridor.intersection(boundary.buffer(0.05)).area / corridor.area >= 0.9


def test_vehicle_connector_prefers_grid_aligned_right_angle():
    boundary = Polygon([(0, 0), (200, 0), (200, 200), (0, 200)])
    entry = Point(0, 25)
    centerlines = [LineString([(60, 50), (60, 175)])]
    segments = []

    added = _append_context_connectors(
        boundary_m=boundary,
        entries=[entry],
        role="local",
        width_m=14.0,
        centerlines=centerlines,
        segments=segments,
        grid_angle_deg=0.0,
    )

    assert added == 1
    coords = list(segments[0].line.coords)
    assert len(coords) == 3
    first = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
    second = (coords[2][0] - coords[1][0], coords[2][1] - coords[1][1])
    assert abs(first[0] * second[0] + first[1] * second[1]) < 1e-6
    assert all(abs(value) < 1e-6 for value in (first[1], second[0]))


def test_roundabouts_require_an_explicit_network_option():
    boundary = Polygon([(0, 0), (500, 0), (500, 340), (0, 340)])
    rules, _ = resolve_rules("lap_compliant", PARAMS)

    ordinary = generate_street_network(boundary, rules, [])
    specialized = generate_street_network(boundary, rules, [], include_roundabouts=True)

    assert ordinary.roundabouts == []
    assert specialized.roundabouts


def test_context_connector_leaves_edge_only_half_width_route_unserved():
    boundary = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    centerlines = [LineString([(30, 0), (100, 0)])]
    segments = []

    added = _append_context_connectors(
        boundary_m=boundary,
        entries=[Point(20, 0)],
        role="local",
        width_m=14.0,
        centerlines=centerlines,
        segments=segments,
    )

    assert added == 0
    assert segments == []


def test_drivable_context_filter_rejects_limited_access_and_unbuilt_roads():
    residential = {"properties": {"ctp_class": "Residential Street", "built_status": "Built"}}
    skeletal = {"properties": {"ctp_class": "Skeletal Road", "built_status": "Built"}}
    motorway = {"properties": {"highway": "motorway_link"}}
    future = {"properties": {"road_class": "Collector", "status": "Proposed"}}

    assert _is_drivable_context_feature(residential)
    assert not _is_drivable_context_feature(skeletal)
    assert not _is_drivable_context_feature(motorway)
    assert not _is_drivable_context_feature(future)


def test_plan_emits_path_connectors_and_ignores_limited_access_roads():
    frontage_road = {
        "geometry": mapping(LineString([_offset(-20, -15), _offset(520, -15)])),
        "properties": {"road_type": "residential", "name": "Context Street"},
    }
    freeway = {
        "geometry": mapping(LineString([_offset(-20, 355), _offset(520, 355)])),
        "properties": {"road_type": "motorway", "name": "Do Not Connect"},
    }
    frontage_path = {
        "geometry": mapping(LineString([_offset(65, -12), _offset(95, -12)])),
        "properties": {"asset_type": "multi use pathway"},
    }

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="lap_compliant",
        scenario_label="Connected",
        parameters=PARAMS,
        road_features=[frontage_road, freeway],
        path_features=[frontage_path],
        district_features=[],
    )

    path_zones = [zone for zone in result.zones if zone["properties"].get("street_role") == "path"]
    assert path_zones
    assert all(zone["properties"].get("road_archetype_id") == "multi_use_trail" for zone in path_zones)
    assert all(zone["properties"].get("context_connection") is True for zone in path_zones)
    assert any(
        zone["properties"].get("context_connection") is True and zone["properties"].get("street_role") == "local"
        for zone in result.zones
    )
    context_note = next(note for note in result.notes if note["code"] == "CONTEXT_CONNECTIONS_APPLIED")
    assert "1 adjacent road" in context_note["message"]
    assert "1 pathway" in context_note["message"]
    assert result.geometry_inputs["context_road_anchors"] == 1
    assert result.geometry_inputs["context_road_connections"] == 1
    assert result.geometry_inputs["context_path_anchors"] == 1
    assert result.geometry_inputs["context_path_connections"] == 1
    assert any(note["code"] == "CONTEXT_CONNECTIVITY_OK" for note in result.notes)

    from app.services.plan_geometry.plan_evaluator import evaluate_plan

    report = evaluate_plan(result, PARAMS, units_estimate=None)
    assert report.scores["context_connectivity"].score == 1.0


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


def test_single_block_plan_draws_courtyard_and_unique_bar_names():
    # A ~1 ha site takes no internal streets — the plan degrades to one block
    # of perimeter bars. Regression (user trial 2026-07-07): all bars were
    # named "Block 1" and the enclosed courtyard was invisible, so the plan
    # read as one giant slab.
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(110, 100),
        scenario_id="climate_first",
        scenario_label="Climate First",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    assert result.block_count == 1
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert len(buildings) > 1
    names = [z["name"] for z in buildings]
    assert len(set(names)) == len(names)  # unique per bar
    assert all("Building" in n for n in names)

    courtyards = [z for z in result.zones if z["properties"].get("_plan_role") == "courtyard"]
    assert courtyards and all(z["zone_type"] == "green_space" for z in courtyards)
    assert all(z["properties"].get("green_space_archetype_id") == "urban_pocket_park" for z in courtyards)
    # Compact plans now preserve a measurable signature park even when no
    # internal street fits; the courtyard remains additional visual amenity.
    assert result.geometry_inputs["open_space_area_m2"] >= 900.0


def test_single_block_exact_count_contract_emits_four_buildings_and_two_parks_without_overlap():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(95, 78),
        scenario_id="custom_exact_counts",
        scenario_label="Four Buildings Two Parks",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        rule_hints={
            "building_count_target": 4.0,
            "park_count_target": 2.0,
            "open_space_share": 0.20,
        },
    )

    buildings = [zone for zone in result.zones if zone["properties"].get("_plan_role") == "building"]
    parks = [zone for zone in result.zones if zone["properties"].get("_plan_role") == "open_space"]
    assert len(buildings) == 4
    assert len(parks) == 2
    assert result.building_count == 4
    assert result.geometry_inputs["open_space_area_m2"] > 0

    authored = [(zone["zone_type"], Polygon(zone["coordinates"])) for zone in (*buildings, *parks)]
    for index, (kind, geometry) in enumerate(authored):
        for other_kind, other in authored[index + 1 :]:
            assert geometry.intersection(other).area == pytest.approx(0.0), (kind, other_kind)

    codes = {note["code"] for note in result.notes}
    assert "EXACT_BUILDING_COUNT_UNMET" not in codes
    assert "EXACT_PARK_COUNT_UNMET" not in codes
    assert "MASS_OPEN_SPACE_COLLISION" not in codes


def test_exact_count_native_module_packer_preserves_dimensions_and_clearance():
    cells = _pack_exact_target_cells(
        Polygon([(0, 0), (95, 0), (95, 58), (0, 58)]),
        4,
        TargetFootprint(width_m=20.0, depth_m=15.0, aspect=4 / 3, source="catalog"),
        setback_m=3.0,
    )

    assert cells is not None and len(cells) == 4
    for cell in cells:
        edges = sorted(
            math.dist(a, b)
            for a, b in zip(
                list(cell.minimum_rotated_rectangle.exterior.coords)[:-1],
                list(cell.minimum_rotated_rectangle.exterior.coords)[1:],
            )
        )
        assert edges == pytest.approx([15.0, 15.0, 20.0, 20.0])
    assert min(a.distance(b) for index, a in enumerate(cells) for b in cells[index + 1 :]) >= 4.0 - 1e-6


def test_tiny_site_degrades_to_single_block_plan():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(60, 45),
        scenario_id="as_of_right",
        scenario_label="AoR",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    codes = {n["code"] for n in result.notes}
    assert codes & {"SITE_TOO_SMALL", "NO_INTERNAL_STREETS"}
    assert result.block_count == 1
    assert any(z["zone_type"] == "building" for z in result.zones)  # still buildable


def test_locked_streets_are_reused_not_regenerated():
    site = _site()
    first = generate_plan_geometry(
        site_polygon_wgs84=site,
        scenario_id="lap_compliant",
        scenario_label="LAP",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    street_rings = [z["coordinates"] for z in first.zones if z["zone_type"] == "road"]
    assert street_rings
    from shapely.ops import unary_union

    locked = unary_union([Polygon(r) for r in street_rings])

    second = generate_plan_geometry(
        site_polygon_wgs84=site,
        scenario_id="lap_compliant",
        scenario_label="LAP",
        parameters={**PARAMS, "streets.row_width_m": {"value": 20.0}},  # would change streets if unlocked
        road_features=[],
        district_features=[],
        locked_street_area_wgs84=locked,
    )
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    locked_area = locked.area
    second_street_area = sum(Polygon(z["coordinates"]).area for z in second.zones if z["zone_type"] == "road")
    assert abs(second_street_area - locked_area) / locked_area < 0.02  # same network


def test_height_framework_zones_are_emitted_per_block():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="lap_compliant",
        scenario_label="LAP",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    framework = [z for z in result.zones if z["properties"].get("_plan_role") == "framework_height"]
    assert len(framework) == result.block_count  # one banded sub-area per block
    assert all(z["zone_type"] == "development_area" for z in framework)
    assert all(z["properties"]["max_floors"] > 0 for z in framework)
    assert all(z["properties"]["_imported_from"] == "Height framework — LAP" for z in framework)
    assert all("storeys" in z["name"] for z in framework)


def test_plan_sheet_builds_measurable_html():
    from app.services.plan_geometry.plan_sheet import build_plan_sheet

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="lap_compliant",
        scenario_label="LAP",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    plan_zones = [
        {
            "role": z["properties"]["_plan_role"],
            "coordinates": z["coordinates"],
            "floors": z["properties"].get("floors"),
        }
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    sheet = build_plan_sheet(
        scenario_label="LAP Aligned",
        scenario_id="lap_compliant",
        payload={
            "plan": {
                "status": "complete",
                "generated_at": "t",
                "final_score": 0.95,
                "iterations": [{"iteration": 1, "overall_score": 0.95, "scores": {}, "revisions": []}],
                "geometry_inputs": {
                    **result.geometry_inputs,
                    "context_road_anchors": 2,
                    "context_road_connections": 2,
                    "context_path_anchors": 1,
                    "context_path_connections": 1,
                },
                "rules": result.rules,
                "block_count": result.block_count,
                "parcel_count": result.parcel_count,
                "intersection_density_per_km2": 40.0,
                "notes": result.notes,
            },
            "metrics": {
                "metrics": {
                    "gfa_m2": {
                        "label": "Gross floor area",
                        "value": 100000,
                        "unit": "m2",
                        "derivation": "footprint × storeys",
                    }
                },
                "ceiling_reconciliation": [],
                "assumptions_used": {},
            },
            "trade_offs": [{"message": "narrow vs fire access"}],
        },
        boundary_wgs84=_site(),
        plan_zones=plan_zones,
        dna=None,
        snapshot_meta={"snapshot_id": "snap", "city_id": "calgary", "overall_confidence": 1.0},
    )
    assert "ILLUSTRATIVE — NOT AN APPROVED DESIGN" in sheet
    assert "<svg viewBox=" in sheet and "100 m" in sheet  # measurable drawing + scale bar
    assert "footprint × storeys" in sheet  # derivations on the sheet
    assert "narrow vs fire access" in sheet
    assert "context connections 3/3" in sheet
    assert sheet.count("<polygon") >= len(plan_zones)


def test_hearing_pack_pairs_renders_with_drawing_and_numbers():
    from app.services.plan_geometry.hearing_pack import build_hearing_pack
    from app.services.plan_geometry.plan_diagram import render_plan_diagram_png

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="climate_first",
        scenario_label="Climate First",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    plan_zones = [
        {
            "role": z["properties"]["_plan_role"],
            "coordinates": z["coordinates"],
            "floors": z["properties"].get("floors"),
        }
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    payload = {
        "plan": {
            "status": "complete",
            "final_score": 0.99,
            "geometry_inputs": result.geometry_inputs,
            "rules": result.rules,
            "block_count": result.block_count,
            "parcel_count": result.parcel_count,
        },
        "metrics": {"metrics": {"units": {"label": "Units", "value": 2100, "unit": "units"}}, "assumptions_used": {}},
        "trade_offs": [{"message": "canopy vs parking supply"}],
    }
    tiny_png = render_plan_diagram_png(_site(), plan_zones, size_px=64)
    pack = build_hearing_pack(
        scenario_label="Climate First",
        scenario_id="climate_first",
        payload=payload,
        boundary_wgs84=_site(),
        plan_zones=plan_zones,
        dna=None,
        snapshot_meta={"snapshot_id": "snap", "city_id": "calgary", "overall_confidence": 1.0},
        diagram_png=tiny_png,
        renders=[{"png": tiny_png, "style": "Gemini / photorealistic", "created_at": "2026-07-07T00:00:00"}],
        sibling_scenarios=[
            {"label": "As-of-Right", "scenario_id": "as_of_right", "payload": payload},
            {"label": "Climate First", "scenario_id": "climate_first", "payload": payload},
        ],
    )
    assert "ILLUSTRATIVE — NOT AN APPROVED DESIGN" in pack
    assert "<svg viewBox=" in pack  # to-scale drawing
    assert pack.count("data:image/png;base64,") >= 2  # diagram + render embedded
    assert "Scenario comparison" in pack and "Plan score" in pack
    assert "canopy vs parking supply" in pack
    assert "watermarked and provenance-tagged" in pack


def test_saved_render_watermark_and_provenance():
    from io import BytesIO

    from PIL import Image

    from app.api.v1.render import (
        SAVED_RENDER_WATERMARK_PREFIX,
        SaveRenderRequest,
        _watermark_and_provenance,
    )

    source = Image.new("RGB", (640, 360), (200, 200, 200))
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    req = SaveRenderRequest(
        image_base64="ignored", prompt="test prompt", style="photorealistic", seed=42, model="gemini"
    )
    out_bytes = _watermark_and_provenance(buffer.getvalue(), req)

    out = Image.open(BytesIO(out_bytes))
    assert out.size == (640, 360)
    assert SAVED_RENDER_WATERMARK_PREFIX.isascii()
    provenance = out.text.get("cityprompt:provenance")  # PNG tEXt chunk
    assert provenance and "NOT an approved design" not in provenance  # sanity: JSON not prose
    assert '"model": "gemini"' in provenance and '"seed": 42' in provenance
    # The banner darkens the bottom-left corner region.
    corner = out.convert("RGB").crop((0, 320, 200, 360))
    avg = sum(sum(px) / 3 for px in corner.getdata()) / (200 * 40)
    assert avg < 195  # plain source was uniform 200-grey


def test_courtyard_masses_decompose_into_hole_free_bars():
    # Zone coordinates are single-ring app-wide: a holed perimeter-ring mass
    # serialized by its exterior would draw as a SOLID slab (~2x the reported
    # footprint). The decomposition must yield simple bars whose summed area
    # still matches the reported footprint.
    from app.services.site_engine import iter_polygons

    rules, _ = resolve_rules("lap_compliant", PARAMS)
    block = Polygon([(0, 0), (200, 0), (200, 160), (0, 160)])  # big enough to ring
    mass, info = building_mass_for_block(block, rules)
    assert mass is not None
    polys = list(iter_polygons(mass))
    assert all(not p.interiors for p in polys)  # hole-free
    assert len(polys) >= 2  # actually decomposed
    total = sum(p.area for p in polys)
    assert abs(total - info["footprint_m2"]) / info["footprint_m2"] < 0.02
    assert total < 0.85 * block.area  # not a courtyard-less slab


def test_building_zone_exteriors_match_reported_footprint():
    # End-to-end version of the courtyard guarantee: the area a user SEES
    # (drawn zone exteriors) must equal the footprint the statistics report.
    from app.services.site_engine import (
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="lap_compliant",
        scenario_label="LAP Aligned",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(_site()))
    drawn = 0.0
    for zone in result.zones:
        if zone["zone_type"] != "building":
            continue
        poly = Polygon(zone["coordinates"])
        assert poly.is_valid and len(poly.interiors) == 0
        drawn += project_geometry(poly, tf).area
    gi = result.geometry_inputs
    assert gi["building_footprint_m2"] > 0
    assert abs(drawn - gi["building_footprint_m2"]) / gi["building_footprint_m2"] < 0.05


def test_plan_diagram_is_flat_palette_nadir_png():
    # Conditioning input rules (diagram research): flat colors only, no text,
    # no anti-aliasing artifacts — every pixel must belong to the palette.
    from io import BytesIO

    from PIL import Image

    from app.services.plan_geometry.plan_diagram import DIAGRAM_COLORS, render_plan_diagram_png

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="climate_first",
        scenario_label="Climate First",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    plan_zones = [
        {"role": z["properties"]["_plan_role"], "coordinates": z["coordinates"]}
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    png = render_plan_diagram_png(_site(), plan_zones, size_px=512)
    img = Image.open(BytesIO(png))
    assert img.size == (512, 512)
    colors = {color for _count, color in img.getcolors(maxcolors=1_000_000)}
    assert colors <= set(DIAGRAM_COLORS.values())
    assert DIAGRAM_COLORS["street"] in colors
    assert DIAGRAM_COLORS["building"] in colors
    assert DIAGRAM_COLORS["open_space"] in colors


def test_floors_clamped_by_district_ceiling():
    district = {
        "geometry": mapping(_site(1000, 1000)),  # covers everything
        "properties": {"lu_code": "CC-MH", "height": 19.2},  # 6 storeys at 3.2 m
    }
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="as_of_right",
        scenario_label="AoR",
        parameters={**PARAMS, "buildings.floors": {"value": 20}},
        road_features=[],
        district_features=[district],
    )
    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert buildings
    assert all(z["properties"]["floors"] <= 6.01 for z in buildings)
    assert any(n["code"] == "FLOORS_CLAMPED" for n in result.notes)
