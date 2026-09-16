from __future__ import annotations

from types import SimpleNamespace

import pytest
from pyproj import CRS
from shapely.geometry import Polygon, box, shape
from shapely.ops import transform, unary_union

from app.services.residual_landscape import (
    ResidualSourceZone,
    build_residual_landscape_recipe,
    community_3d_representation_hash,
    community_3d_source_hash,
    derive_site_boundary_from_authored_zones,
    mark_community_3d_stale,
    mark_residual_landscape_stale,
)
from app.services.site_engine import WGS84_CRS, build_transformer, project_geometry


METRIC_CRS = CRS.from_epsg(32612)
TO_WGS84 = build_transformer(METRIC_CRS, WGS84_CRS)
TO_METRIC = build_transformer(WGS84_CRS, METRIC_CRS)
ORIGIN_E = 707_000.0
ORIGIN_N = 5_655_000.0


def wgs_box(min_x: float, min_y: float, max_x: float, max_y: float):
    return transform(
        TO_WGS84.transform,
        box(
            ORIGIN_E + min_x,
            ORIGIN_N + min_y,
            ORIGIN_E + max_x,
            ORIGIN_N + max_y,
        ),
    )


def source(zone_id: str, kind: str, geometry, role: str | None = None):
    return ResidualSourceZone(zone_id=zone_id, kind=kind, geometry=geometry, role=role)


def build(boundary, zones, compiled_at: str = "2026-07-20T00:00:00Z"):
    return build_residual_landscape_recipe(
        boundary,
        zones,
        boundary_id="boundary-1",
        compiled_at=compiled_at,
    )


def metric_geometry(payload):
    return project_geometry(shape(payload), TO_METRIC)


def source_fingerprint(zone_type: str, properties: dict, geometry=None) -> str:
    return community_3d_source_hash(
        zone_type,
        geometry if geometry is not None else wgs_box(0, 0, 30, 20),
        properties,
    )


def test_skate_seating_changes_scene_identity_without_invalidating_legacy_default():
    props = {"green_space_archetype_id": "skate_park", "green_space_selected_variant_id": "skate_park_v0"}
    original = source_fingerprint("green_space", props)
    assert source_fingerprint("green_space", {**props, "skate_spectator_edge": "north"}) == original
    assert source_fingerprint("green_space", {**props, "skate_spectator_edge": "south"}) != original


def test_community_representation_fingerprint_tracks_exact_generator_content():
    source_hash = "a" * 64
    building = SimpleNamespace(
        id="building-1",
        name="Original massing color",
        architectural_style=None,
        footprint=wgs_box(0, 0, 30, 20),
        height_meters=18,
        floor_count=6,
        floor_height_meters=3,
        rotation_degrees=0,
        specifications={
            "legoAssembly": {
                "module_family": "industrial-brick",
                "instances": [{"model_url": "/podium.glb", "position": [0, 0, 0]}],
            },
        },
    )

    original = community_3d_representation_hash(
        kind="building",
        generator="lego_assembly",
        source_hash=source_hash,
        building=building,
    )
    assert original is not None
    assert (
        community_3d_representation_hash(
            kind="building",
            generator="lego_assembly",
            source_hash=source_hash,
            building=building,
        )
        == original
    )

    changed_recipe = SimpleNamespace(**building.__dict__)
    changed_recipe.specifications = {
        "legoAssembly": {
            "module_family": "industrial-brick",
            "instances": [{"model_url": "/podium-v2.glb", "position": [0, 0, 0]}],
        },
    }
    assert (
        community_3d_representation_hash(
            kind="building",
            generator="lego_assembly",
            source_hash=source_hash,
            building=changed_recipe,
        )
        != original
    )

    changed_placement = SimpleNamespace(**building.__dict__)
    changed_placement.rotation_degrees = 15
    assert (
        community_3d_representation_hash(
            kind="building",
            generator="lego_assembly",
            source_hash=source_hash,
            building=changed_placement,
        )
        != original
    )

    changed_display_seed = SimpleNamespace(**building.__dict__)
    changed_display_seed.name = "Different massing color"
    assert (
        community_3d_representation_hash(
            kind="building",
            generator="lego_assembly",
            source_hash=source_hash,
            building=changed_display_seed,
        )
        != original
    )

    assert community_3d_representation_hash(
        kind="park",
        generator="park_kit",
        source_hash=source_hash,
    ) == community_3d_representation_hash(
        kind="park",
        generator="park_kit",
        source_hash=source_hash,
    )
    assert (
        community_3d_representation_hash(
            kind="building",
            generator="lego_assembly",
            source_hash=source_hash,
            building=SimpleNamespace(id="incomplete", footprint=wgs_box(0, 0, 1, 1), specifications={}),
        )
        is None
    )


def test_community_representation_fingerprint_binds_family_pending_public_realm_marker():
    source_hash = "b" * 64
    marker = {
        "schema_version": 1,
        "state": "family_pending",
        "kind": "park",
        "generator": "park_kit",
        "archetype_id": "academic_courtyard",
        "variant_id": None,
        "target_source": "zone_geometry",
    }

    original = community_3d_representation_hash(
        kind="park",
        generator="park_kit",
        source_hash=source_hash,
        public_realm_fallback=marker,
    )

    assert original is not None
    changed = {**marker, "archetype_id": "amsterdam_hofje_garden"}
    assert (
        community_3d_representation_hash(
            kind="park",
            generator="park_kit",
            source_hash=source_hash,
            public_realm_fallback=changed,
        )
        != original
    )
    assert (
        community_3d_representation_hash(
            kind="street",
            generator="street_section",
            source_hash=source_hash,
            public_realm_fallback=marker,
        )
        is None
    )


def test_community_source_fingerprint_tracks_building_design_not_operational_metadata():
    properties = {
        "_plan_role": "building",
        "floors": 10,
        "floor_height": 3.2,
        "height": 32,
        "development_archetype_id": "industrial_brick_mixed_use",
        "development_selected_variant_id": "industrial_brick_variant_1",
        "facade_material": "brick",
        "roof_style": "flat",
        "generation_style_input": {
            "archetypeId": "industrial_brick_mixed_use",
            "generationTags": ["Brick", "Setback"],
            "styleProfile": {"massing": "podium and upper floors"},
            "downstreamHints": {"reuseKeys": ["brick", "corner"], "allowSetback": True},
        },
    }
    original = source_fingerprint("building", properties)
    for key, value in (
        ("floors", 12),
        ("height", 38),
        ("floor_height", 3.5),
        ("development_archetype_id", "london_heritage_mansion"),
        ("development_selected_variant_id", "industrial_brick_variant_2"),
        ("facade_material", "limestone"),
        ("roof_style", "mansard"),
        ("roof_material", "slate"),
        ("development_style_profile", {"massing": "courtyard", "roofForm": "pitched"}),
    ):
        assert source_fingerprint("building", {**properties, key: value}) != original

    changed_generation = {
        **properties,
        "generation_style_input": {
            **properties["generation_style_input"],
            "styleProfile": {"massing": "tower on podium"},
        },
    }
    assert source_fingerprint("building", changed_generation) != original

    for key, value in (
        ("community_3d", {"state": "stale", "stale_at": "later"}),
        ("community_3d_landscape", {"source_hash": "generated"}),
        ("park_ground_texture", {"image_url": "new.png"}),
        ("_preview_history", [{"image_url": "preview.png"}]),
        ("_osm_context", {"fetched_at": "later", "buildings": []}),
        ("terrain_elevation", 1042.1),
        ("community_3d_mask_existing_tiles", True),
        ("development_archetype_image", "https://example.test/new.png"),
        ("reference_images", ["https://example.test/reference.png"]),
    ):
        assert source_fingerprint("building", {**properties, key: value}) == original

    reordered = {
        **properties,
        "floors": 10.0,
        "generation_style_input": {
            **properties["generation_style_input"],
            "generationTags": ["setback", "brick", "brick"],
            "downstreamHints": {
                "reuseKeys": ["corner", "brick", "corner"],
                "allowSetback": True,
            },
        },
    }
    assert source_fingerprint("building", reordered) == original


def test_community_source_fingerprint_canonicalizes_polygon_ring_representation():
    coordinates = [(0, 0), (3, 0), (3, 2), (0, 2), (0, 0)]
    properties = {"_plan_role": "building", "floors": 4}
    original = source_fingerprint("building", properties, Polygon(coordinates))
    rotated = Polygon([(3, 2), (0, 2), (0, 0), (3, 0), (3, 2)])
    reversed_ring = Polygon(list(reversed(coordinates)))

    assert source_fingerprint("building", properties, rotated) == original
    assert source_fingerprint("building", properties, reversed_ring) == original
    assert (
        source_fingerprint(
            "building",
            properties,
            Polygon([(0, 0), (3.01, 0), (3, 2), (0, 2), (0, 0)]),
        )
        != original
    )


def test_community_source_fingerprint_tracks_park_and_street_semantics():
    park = {
        "_plan_role": "open_space",
        "green_space_archetype_id": "neighborhood_park",
        "green_space_selected_variant_id": "neighborhood_park_variant_1",
        "planting_structure": "perimeter grove",
        "tree_density": 0.4,
        "park_access_points": [[-114.08, 51.04]],
    }
    park_hash = source_fingerprint("green_space", park)
    for key, value in (
        ("green_space_archetype_id", "botanical_garden"),
        ("green_space_selected_variant_id", "variant_2"),
        ("planting_structure", "formal allee"),
        ("tree_density", 0.8),
        ("neighborhood_park_layout", "adaptive_rustic_v1"),
        ("park_access_points", [[-114.079, 51.041]]),
    ):
        assert source_fingerprint("green_space", {**park, key: value}) != park_hash

    street = {
        "_plan_role": "street",
        "road_archetype_id": "main_street_complete",
        "road_selected_variant_id": "main_street_variant_1",
        "street_role": "spine",
        "width": 18,
        "lane_count": 2,
        "road_surface": "asphalt",
        "plan_centerline": [[-114.08, 51.04], [-114.079, 51.041]],
    }
    street_hash = source_fingerprint("road", street)
    for key, value in (
        ("road_archetype_id", "yield_street"),
        ("road_selected_variant_id", "variant_2"),
        ("street_role", "local"),
        ("width", 14),
        ("lane_count", 1),
        ("road_surface", "unit pavers"),
        ("plan_centerline", [[-114.08, 51.04], [-114.078, 51.042]]),
    ):
        assert source_fingerprint("road", {**street, key: value}) != street_hash


def test_residual_is_boundary_minus_union_of_overlapping_authored_zones():
    boundary = wgs_box(0, 0, 100, 100)
    building = wgs_box(10, 10, 50, 50)
    overlapping_park = wgs_box(35, 35, 75, 70)
    recipe = build(
        boundary,
        [
            source("building", "building", building, "building"),
            source("park", "park", overlapping_park, "open_space"),
        ],
    )

    boundary_metric = project_geometry(boundary, TO_METRIC)
    occupied_metric = unary_union(
        [
            project_geometry(building, TO_METRIC),
            project_geometry(overlapping_park, TO_METRIC),
        ]
    )
    expected = boundary_metric.difference(occupied_metric)
    residual = metric_geometry(recipe["geometry"])

    assert recipe["area_sqm"] == pytest.approx(expected.area, abs=0.1)
    assert residual.symmetric_difference(expected).area < 0.05
    assert sum(region["area_sqm"] for region in recipe["regions"]) == pytest.approx(recipe["area_sqm"], abs=0.15)


def test_outside_polygons_are_clipped_and_framework_overlays_do_not_subtract():
    boundary = wgs_box(0, 0, 50, 50)
    crossing_street = wgs_box(-20, 20, 25, 30)
    framework = wgs_box(0, 0, 50, 50)
    recipe = build(
        boundary,
        [
            source("street", "street", crossing_street, "street"),
            source("framework", "building", framework, "framework_height"),
        ],
    )

    assert recipe["occupied_area_sqm"] == pytest.approx(250.0, abs=0.2)
    assert recipe["area_sqm"] == pytest.approx(2_250.0, abs=0.2)


def test_residual_preserves_multipolygons_and_holes():
    boundary = wgs_box(0, 0, 100, 100)
    splitter = wgs_box(45, 0, 55, 100)
    split_recipe = build(boundary, [source("street", "street", splitter, "street")])
    assert split_recipe["geometry"]["type"] == "MultiPolygon"

    island = wgs_box(35, 35, 65, 65)
    hole_recipe = build(boundary, [source("building", "building", island, "building")])
    assert hole_recipe["geometry"]["type"] == "Polygon"
    assert len(hole_recipe["geometry"]["coordinates"]) == 2


def test_narrow_residual_is_covered_but_receives_no_tree_canopy():
    boundary = wgs_box(0, 0, 20, 100)
    occupied = wgs_box(0, 0, 18, 100)
    recipe = build(boundary, [source("building", "building", occupied, "building")])

    assert recipe["area_sqm"] == pytest.approx(200.0, abs=0.2)
    assert recipe["regions"]
    assert recipe["placements"] == []


def test_recipe_hash_regions_and_placements_are_deterministic_across_rebuilds():
    boundary = wgs_box(0, 0, 120, 100)
    zones = [
        source("building", "building", wgs_box(20, 20, 55, 60), "building"),
        source("street", "street", wgs_box(0, 78, 120, 88), "street"),
    ]
    first = build(boundary, zones, "2026-07-20T00:00:00Z")
    second = build(boundary, list(reversed(zones)), "2026-07-21T00:00:00Z")

    assert first["source_hash"] == second["source_hash"]
    assert first["regions"] == second["regions"]
    assert first["placements"] == second["placements"]
    assert first["compiled_at"] != second["compiled_at"]


def test_tree_placements_stay_in_residual_and_clear_buildings_and_streets():
    boundary = wgs_box(0, 0, 160, 120)
    building = wgs_box(55, 35, 100, 85)
    street = wgs_box(0, 98, 160, 110)
    recipe = build(
        boundary,
        [
            source("building", "building", building, "building"),
            source("street", "street", street, "street"),
        ],
    )
    residual = metric_geometry(recipe["geometry"])
    building_metric = project_geometry(building, TO_METRIC)
    street_metric = project_geometry(street, TO_METRIC)

    assert recipe["placements"]
    for placement in recipe["placements"]:
        point_metric = project_geometry(
            shape({"type": "Point", "coordinates": [placement["lng"], placement["lat"]]}),
            TO_METRIC,
        )
        assert residual.covers(point_metric)
        # The largest yawed overhead crown plane reaches 5.05 m from its trunk.
        # The whole canopy, not just its centre, stays residual.
        assert residual.buffer(0.05).covers(point_metric.buffer(5.05))
        assert point_metric.distance(building_metric) >= 5.05
        assert point_metric.distance(street_metric) >= 5.05


def test_invalid_bow_tie_polygon_is_repaired_without_losing_the_recipe():
    boundary = wgs_box(0, 0, 80, 80)
    coordinates = [
        (ORIGIN_E + 10, ORIGIN_N + 10),
        (ORIGIN_E + 60, ORIGIN_N + 60),
        (ORIGIN_E + 10, ORIGIN_N + 60),
        (ORIGIN_E + 60, ORIGIN_N + 10),
        (ORIGIN_E + 10, ORIGIN_N + 10),
    ]
    bow_tie = transform(TO_WGS84.transform, Polygon(coordinates))
    recipe = build(boundary, [source("invalid", "building", bow_tie, "building")])

    assert recipe["area_sqm"] > 0
    # GEOS MakeValid preserves both 625 m² lobes. The older buffer(0) repair
    # kept only one and allowed generated landscape to overlap the other.
    assert recipe["occupied_area_sqm"] == pytest.approx(1_250.0, abs=0.2)
    assert shape(recipe["geometry"]).is_valid


def test_boundaryless_legacy_plan_gets_metric_convex_hull_without_extra_buffer():
    southwest = wgs_box(0, 0, 30, 30)
    northeast = wgs_box(70, 70, 100, 100)
    boundary = derive_site_boundary_from_authored_zones([southwest, northeast])
    metric = project_geometry(boundary, TO_METRIC)

    assert metric.area == pytest.approx(5_100.0, abs=0.5)
    assert metric.buffer(0.01).covers(project_geometry(southwest, TO_METRIC))
    assert metric.buffer(0.01).covers(project_geometry(northeast, TO_METRIC))


def test_shared_stale_transition_is_idempotent_and_preserves_diagnostics():
    boundary = SimpleNamespace(
        properties={
            "site_name": "Pilot",
            "community_3d_landscape": {
                "state": "compiled",
                "source_hash": "authoritative-hash",
                "area_sqm": 123.4,
            },
        }
    )

    assert mark_residual_landscape_stale(
        boundary,
        changed_zone_id="zone-1",
        reason="Plan changed",
        stale_at="2026-07-20T12:00:00Z",
    )
    recipe = boundary.properties["community_3d_landscape"]
    assert recipe == {
        "state": "stale",
        "source_hash": "authoritative-hash",
        "area_sqm": 123.4,
        "stale_at": "2026-07-20T12:00:00Z",
        "stale_reason": "Plan changed",
        "changed_zone_id": "zone-1",
    }
    assert boundary.properties["site_name"] == "Pilot"
    assert not mark_residual_landscape_stale(
        boundary,
        changed_zone_id="zone-2",
        reason="Repeated change",
    )

    zone = SimpleNamespace(
        properties={
            "community_3d": {
                "state": "compiled",
                "kind": "building",
                "source_hash": "zone-hash",
            },
        }
    )
    assert mark_community_3d_stale(
        zone,
        reason="Floors changed",
        stale_at="2026-07-20T12:00:00Z",
    )
    assert zone.properties["community_3d"] == {
        "state": "stale",
        "kind": "building",
        "source_hash": "zone-hash",
        "stale_at": "2026-07-20T12:00:00Z",
        "stale_reason": "Floors changed",
    }
    assert not mark_community_3d_stale(zone, reason="Repeated change")
