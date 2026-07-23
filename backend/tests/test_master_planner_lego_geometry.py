from __future__ import annotations

import math
from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from app.services.master_planner.lego_catalog import build_lego_planning_catalog
from app.services.master_planner.lego_geometry import (
    LegoGeometryCompatibilityError,
    _frontend_footprint_analysis,
    bind_building_zones_to_lego,
)
from app.services.master_planner.spec import lego_fallback_spec, palette_from_spec
from app.services.plan_geometry.placement import BandSpec, Palette
from app.services.plan_geometry.refinement import run_refinement_loop

LAT = 51.04
LON = -114.08
M_LAT = 110_540.0
M_LON = 111_320.0 * math.cos(math.radians(LAT))


def _module(
    module_id: str,
    *,
    family: str,
    role: str,
    width_m: float,
    depth_m: float,
    archetype_id: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=module_id,
        name=module_id,
        model_url=f"/models/{module_id}.glb",
        metadata_={
            "lego": {
                "enabled": True,
                "family": family,
                "role": role,
                "width_m": width_m,
                "depth_m": depth_m,
                "height_m": 3.2 if role != "roof" else 1.0,
                "archetype_ids": [archetype_id],
                "reuse_keys": [],
                "repeatable_z": role == "floor",
                "min_floors": 1,
                "max_floors": 8,
                "variant_key": "default",
                "lod": 0,
            }
        },
    )


def _family(archetype_id: str, width_m: float, depth_m: float) -> list[SimpleNamespace]:
    family = f"{archetype_id}-family"
    return [
        _module(
            f"{family}-{role}",
            family=family,
            role=role,
            width_m=width_m,
            depth_m=depth_m,
            archetype_id=archetype_id,
        )
        for role in ("podium", "floor", "roof")
    ]


def _rectangle(width_m: float, depth_m: float) -> list[list[float]]:
    return [
        [LON, LAT],
        [LON + width_m / M_LON, LAT],
        [LON + width_m / M_LON, LAT + depth_m / M_LAT],
        [LON, LAT + depth_m / M_LAT],
    ]


def _geographic(points: list[tuple[float, float]]) -> list[list[float]]:
    return [[LON + x / M_LON, LAT + y / M_LAT] for x, y in points]


def _zone(width_m: float, depth_m: float) -> dict:
    return {
        "name": "AI building",
        "zone_type": "building",
        "coordinates": _rectangle(width_m, depth_m),
        "properties": {
            "_plan_role": "building",
            "floors": 3,
            "development_type": "mixed_use",
            "development_aesthetic": "industrial_brick",
            "development_archetype_id": "industrial_brick_mixed_use",
        },
    }


def _entries() -> list[SimpleNamespace]:
    return [
        *_family("industrial_brick_mixed_use", 30, 20),
        *_family("courtyard_family_housing", 14, 14),
    ]


def test_actual_footprint_binding_keeps_a_compatible_identity():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)

    zones, report = bind_building_zones_to_lego(
        [_zone(30, 20)],
        entries,
        catalog,
    )

    assert report.building_count == 1
    assert report.retained_count == 1
    assert report.unchanged_count == 1
    assert report.repaired_count == 0
    assert report.omitted_count == 0
    assert zones[0]["properties"]["development_archetype_id"] == (
        "industrial_brick_mixed_use"
    )
    assert zones[0]["properties"]["archetype_source"] == (
        "runtime_lego_actual_footprint"
    )


def test_actual_footprint_analysis_matches_browser_near_rectangle_rule():
    analysis = _frontend_footprint_analysis(_geographic([
        (-15, -10), (15, -10), (15, 10), (1, 10), (0, 9), (-1, 10),
        (-15, 10),
    ]))

    assert analysis is not None
    assert analysis[2] == "rectangle"


def test_actual_footprint_analysis_preserves_a_material_l_shape():
    analysis = _frontend_footprint_analysis(_geographic([
        (-18, -14), (18, -14), (18, -4), (-8, -4), (-8, 14), (-18, 14),
    ]))

    assert analysis is not None
    assert analysis[2] == "l_shape"


def test_actual_footprint_binding_rehomes_an_incompatible_identity_atomically():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)

    zones, report = bind_building_zones_to_lego(
        [_zone(14, 14)],
        entries,
        catalog,
    )

    properties = zones[0]["properties"]
    assert report.repaired_count == 1
    assert properties["development_archetype_id"] == "courtyard_family_housing"
    assert properties["_lego_runtime_repaired_from"] == "industrial_brick_mixed_use"
    assert properties["target_w_m"] == 14
    assert properties["target_d_m"] == 14


def test_actual_footprint_binding_rejects_a_cross_parent_selected_identity():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)
    zone = _zone(14, 14)
    zone["properties"]["development_selected_variant_id"] = (
        "courtyard_family_housing"
    )

    zones, report = bind_building_zones_to_lego([zone], entries, catalog)

    properties = zones[0]["properties"]
    assert report.unchanged_count == 0
    assert report.repaired_count == 1
    assert properties["development_archetype_id"] == "courtyard_family_housing"
    assert properties.get("development_selected_variant_id") is None


def test_actual_footprint_binding_fails_before_persistence_without_any_recipe():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)

    with pytest.raises(LegoGeometryCompatibilityError, match="no executable LEGO family"):
        bind_building_zones_to_lego(
            [_zone(100, 100)],
            entries,
            catalog,
        )


def test_actual_footprint_binding_returns_a_bounded_sliver_to_landscape():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)
    zones_in = [_zone(30, 20) for _ in range(9)] + [_zone(11.8, 5.1)]
    zones_in[-1]["name"] = "Clipped edge sliver"

    zones, report = bind_building_zones_to_lego(zones_in, entries, catalog)

    assert len(zones) == 9
    assert report.building_count == 10
    assert report.retained_count == 9
    assert report.omitted_count == 1
    assert report.omitted_building_indices == (9,)
    assert report.omissions == (("Clipped edge sliver", 11.8, 5.1, 3),)


def test_actual_footprint_binding_rejects_excessive_omissions_atomically():
    entries = _entries()
    catalog = build_lego_planning_catalog(entries)

    with pytest.raises(
        LegoGeometryCompatibilityError,
        match="bounded residual-landscape allowance",
    ):
        bind_building_zones_to_lego(
            [_zone(30, 20), _zone(11.8, 5.1), _zone(11.8, 5.1)],
            entries,
            catalog,
        )


def test_fallback_refinement_preserves_native_lego_identities_through_binding():
    rndsqr_parent = "rndsqr_terraced_mixed_use_midrise"
    brownstone_parent = "brownstone_rowhouse_frontage"
    brownstone_variant = "brownstone_rowhouse_red_sandstone"
    brownstone = _module(
        "brownstone-renderlocked",
        family="brownstone-renderlocked-family",
        role="assembled",
        width_m=8,
        depth_m=15,
        archetype_id=brownstone_parent,
    )
    brownstone.metadata_["lego"].update({
        "archetype_ids": [brownstone_parent, brownstone_variant],
        "native_floors": 3,
        "source_variant_id": brownstone_variant,
        "generation_archetype_id": brownstone_variant,
    })
    entries = [
        *_family(rndsqr_parent, 38, 30),
        brownstone,
    ]
    catalog = build_lego_planning_catalog(entries)
    fallback = lego_fallback_spec("city_policy", catalog)
    palette = palette_from_spec(
        fallback,
        "city_policy",
        lego_catalog=catalog,
    )
    site = Polygon(_geographic([
        (0, 0),
        (300, 0),
        (300, 240),
        (0, 240),
    ]))

    result, _, _ = run_refinement_loop(
        site_polygon_wgs84=site,
        scenario_id="city_policy",
        scenario_label="City policy",
        parameters={
            "streets.row_width_m": {"value": 16.0},
            "buildings.floors": {"value": 6},
            "landscape.tree_density": {"value": 0.6},
        },
        dna={},
        road_features=[],
        path_features=[],
        district_features=[],
        palette_override=palette,
    )
    building_zones = [
        zone
        for zone in result.zones
        if (zone.get("properties") or {}).get("_plan_role") == "building"
    ]
    identities_before = [
        (
            zone["properties"].get("development_archetype_id"),
            zone["properties"].get("development_selected_variant_id"),
        )
        for zone in building_zones
    ]

    assert (rndsqr_parent, None) in identities_before
    assert (brownstone_parent, brownstone_variant) in identities_before

    rebound_zones, report = bind_building_zones_to_lego(
        result.zones,
        entries,
        catalog,
    )
    rebound_buildings = [
        zone
        for zone in rebound_zones
        if (zone.get("properties") or {}).get("_plan_role") == "building"
    ]
    identities_after = [
        (
            zone["properties"].get("development_archetype_id"),
            zone["properties"].get("development_selected_variant_id"),
        )
        for zone in rebound_buildings
    ]

    assert report.building_count == len(building_zones)
    assert report.unchanged_count == len(building_zones)
    assert report.repaired_count == 0
    assert report.omitted_count == 0
    assert identities_after == identities_before
    assert all(
        "_lego_runtime_repaired_from" not in zone["properties"]
        for zone in rebound_buildings
    )

    for zone in rebound_buildings:
        properties = zone["properties"]
        selectable_id = (
            properties.get("development_selected_variant_id")
            or properties["development_archetype_id"]
        )
        native_width, native_depth = (
            catalog.target_dimensions_by_selectable_id[selectable_id]
        )
        analysis = _frontend_footprint_analysis(zone["coordinates"])
        assert analysis is not None
        actual_width, actual_depth, profile = analysis
        orientation_scales = (
            (actual_width / native_width, actual_depth / native_depth),
            (actual_depth / native_width, actual_width / native_depth),
        )
        assert profile == "rectangle"
        assert any(
            0.80 <= scale_x <= 1.20 and 0.80 <= scale_y <= 1.20
            for scale_x, scale_y in orientation_scales
        )


def test_runtime_cell_alternates_survive_final_binding_without_rebound():
    parent_id = "rndsqr_terraced_mixed_use_midrise"
    primary_variant = "rndsqr_midrise_courtyard"
    rotated_variant = "rndsqr_midrise_terraced_garden"
    incompatible_variant = "rndsqr_midrise_heritage_integrated"
    variant_dimensions = {
        primary_variant: (25.0, 18.0),
        rotated_variant: (18.0, 25.0),
        # Its nominal 0.833 x 0.818 fit is deliberately outside the guarded
        # runtime envelope and must never be stamped onto the primary cells.
        incompatible_variant: (30.0, 22.0),
    }
    entries: list[SimpleNamespace] = []
    for variant_id, (width_m, depth_m) in variant_dimensions.items():
        module = _module(
            variant_id,
            family=f"{variant_id}-family",
            role="assembled",
            width_m=width_m,
            depth_m=depth_m,
            archetype_id=parent_id,
        )
        module.metadata_["lego"].update({
            "archetype_ids": [parent_id, variant_id],
            "native_floors": 4,
            "source_variant_id": variant_id,
            "generation_archetype_id": variant_id,
        })
        entries.append(module)

    catalog = build_lego_planning_catalog(entries)
    band = BandSpec(
        development_type="mixed_use",
        aesthetic="contemporary_urban",
        floors_delta=None,
        floors_abs=4.0,
        typology="perimeter_block",
        archetype_id=parent_id,
        variant_id=primary_variant,
    )
    palette = Palette(
        bands={
            key: band
            for key in ("core", "frontage", "mid", "edge", "anchor")
        },
        allowed_archetype_ids=frozenset(catalog.parent_ids),
        allowed_variant_ids_by_archetype=dict(catalog.variants_by_parent),
        supported_floors_by_selectable_id=dict(
            catalog.supported_floors_by_selectable_id
        ),
        target_dimensions_by_selectable_id=dict(
            catalog.target_dimensions_by_selectable_id
        ),
    )
    site = Polygon(_geographic([
        (0, 0),
        (160, 0),
        (160, 120),
        (0, 120),
    ]))

    result, _, _ = run_refinement_loop(
        site_polygon_wgs84=site,
        scenario_id="economic",
        scenario_label="Economic",
        parameters={
            "streets.row_width_m": {"value": 16.0},
            "buildings.floors": {"value": 4},
            "landscape.tree_density": {"value": 0.6},
        },
        dna={},
        road_features=[],
        path_features=[],
        district_features=[],
        palette_override=palette,
    )
    buildings = [
        zone
        for zone in result.zones
        if (zone.get("properties") or {}).get("_plan_role") == "building"
    ]
    identities_before = [
        zone["properties"].get("development_selected_variant_id")
        for zone in buildings
    ]

    assert primary_variant in identities_before
    assert rotated_variant in identities_before
    assert incompatible_variant not in identities_before

    rebound_zones, report = bind_building_zones_to_lego(
        result.zones,
        entries,
        catalog,
    )
    identities_after = [
        zone["properties"].get("development_selected_variant_id")
        for zone in rebound_zones
        if (zone.get("properties") or {}).get("_plan_role") == "building"
    ]

    assert identities_after == identities_before
    assert report.building_count == len(buildings)
    assert report.unchanged_count == len(buildings)
    assert report.repaired_count == 0
    assert report.omitted_count == 0
