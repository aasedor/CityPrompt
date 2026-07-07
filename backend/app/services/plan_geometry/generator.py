"""Plan generator — orchestrates rules -> streets -> blocks -> parcels -> masses.

Input: WGS84 site boundary, scenario id, PlanParameters, and raw features
(road centrelines + land-use districts) already fetched by the connector.
Output: WGS84 zone dicts ready to insert as SiteZones, plus geometry-mode
inputs for plan_metrics and ValidationNotes. Deterministic; never raises for
data reasons — a degenerate site yields a single-block plan with notes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely.geometry import LineString, Polygon, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.community_rules import (
    FLOOR_HEIGHT_M,
    RuleProfile,
    resolve_rules,
)
from app.services.plan_geometry.layout_validation import validate_plan
from app.services.plan_geometry.parceling import (
    building_mass_for_block,
    clamp_floors_to_ceiling,
    subdivide_block,
)
from app.services.plan_geometry.street_graph import (
    StreetNetwork,
    entry_points_from_roads,
    generate_street_network,
)
from app.services.site_engine import (
    build_transformer,
    cleanup_developable_blocks,
    iter_polygons,
    local_metric_crs_for_polygon,
    project_geometry,
)

logger = logging.getLogger(__name__)

PLAN_COLORS = {"road": "#8a8f98", "green_space": "#5fae5f", "building": "#8b5cf6"}

# Height framework bands (amber -> deep red), aligned to LAP building-scale steps.
HEIGHT_BANDS = [(3, "#fde68a"), (6, "#fbbf24"), (12, "#f97316"), (26, "#dc2626"), (999, "#7c2d12")]


def _height_band(floors: float) -> tuple[int, str]:
    for ceiling, color in HEIGHT_BANDS:
        if floors <= ceiling:
            return ceiling, color
    return 999, HEIGHT_BANDS[-1][1]


@dataclass
class PlanGeometryResult:
    zones: list[dict[str, Any]] = field(default_factory=list)
    geometry_inputs: dict[str, float] = field(default_factory=dict)
    intersection_density_per_km2: float = 0.0
    block_count: int = 0
    parcel_count: int = 0
    building_count: int = 0
    notes: list[dict[str, Any]] = field(default_factory=list)
    rules: dict[str, Any] = field(default_factory=dict)
    # Metric internals for the evaluator (in-memory only, never serialized).
    blocks_m: list[BaseGeometry] = field(default_factory=list)
    masses_m: list[BaseGeometry] = field(default_factory=list)
    green_m: list[BaseGeometry] = field(default_factory=list)
    mass_floors: list[float] = field(default_factory=list)


def _ring(poly_wgs84: Polygon) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in poly_wgs84.exterior.coords[:-1]]


def _feature_lines_m(features: list[dict[str, Any]], to_metric) -> list[LineString]:
    lines: list[LineString] = []
    for feature in features or []:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        try:
            geom = make_valid(shape(geometry))
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001
            continue
        metric = project_geometry(geom, to_metric)
        if isinstance(metric, LineString):
            lines.append(metric)
        else:
            lines.extend(g for g in getattr(metric, "geoms", []) if isinstance(g, LineString))
    return lines


def _district_lookup_m(features: list[dict[str, Any]], to_metric) -> list[tuple[BaseGeometry, dict[str, Any]]]:
    lookup = []
    for feature in features or []:
        geometry = feature.get("geometry")
        props = feature.get("properties") or {}
        if not geometry:
            continue
        try:
            geom = project_geometry(make_valid(shape(geometry)), to_metric)
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001
            continue
        height = props.get("height")
        lookup.append((geom, {"code": props.get("lu_code"), "height_m": float(height) if height else None}))
    return lookup


def generate_plan_geometry(
    *,
    site_polygon_wgs84: Polygon,
    scenario_id: str,
    scenario_label: str,
    parameters: dict[str, Any],
    road_features: list[dict[str, Any]] | None = None,
    district_features: list[dict[str, Any]] | None = None,
    locked_street_area_wgs84: Polygon | None = None,
    rule_overrides: dict[str, float] | None = None,
) -> PlanGeometryResult:
    result = PlanGeometryResult()
    layer_name = f"Plan — {scenario_label}"

    site = make_valid(site_polygon_wgs84)
    crs = local_metric_crs_for_polygon(site)
    to_metric = build_transformer("EPSG:4326", crs)
    to_wgs84 = build_transformer(crs, "EPSG:4326")
    boundary_m = make_valid(project_geometry(site, to_metric))
    gross = float(boundary_m.area)

    rules, rule_notes = resolve_rules(scenario_id, parameters)
    if rule_overrides:
        # The refinement loop revises rule inputs; each override is recorded by
        # the loop itself as {parameter, from, to, reason}.
        from dataclasses import replace as dc_replace
        valid_overrides = {k: v for k, v in rule_overrides.items()
                           if hasattr(rules, k) and isinstance(v, (int, float))}
        rules = dc_replace(rules, **valid_overrides)
    result.notes.extend(rule_notes)
    result.rules = {
        "block_target_m": rules.block_target_m, "row_width_m": rules.row_width_m,
        "clear_width_m": rules.clear_width_m, "open_space_share": rules.open_space_share,
        "coverage_ratio": rules.coverage_ratio, "floors": rules.floors,
        "floors_note": rules.floors_note,
    }

    # --- streets (or the locked network) --------------------------------------
    if locked_street_area_wgs84 is not None and not locked_street_area_wgs84.is_empty:
        network = StreetNetwork()
        network.street_area = make_valid(project_geometry(make_valid(locked_street_area_wgs84), to_metric))
        result.notes.append({
            "code": "STREETS_LOCKED", "severity": "info",
            "message": "Street network locked by the user — regenerated blocks/massing only.",
            "source_phase": "street_graph",
        })
    else:
        entries = entry_points_from_roads(_feature_lines_m(road_features or [], to_metric), boundary_m)
        network = generate_street_network(boundary_m, rules, entries)
    result.notes.extend(network.notes)
    street_area = network.street_area if network.street_area is not None else Polygon()

    # --- blocks -----------------------------------------------------------------
    developable = boundary_m.difference(street_area) if not street_area.is_empty else boundary_m
    # Morphological opening (erode 5 cm, dilate back): the difference can leave
    # hairline bridges at street crossings that keep blocks topologically
    # connected — the part count then depends on floating-point noise. Opening
    # severs the bridges deterministically at negligible geometric cost.
    developable = make_valid(developable.buffer(-0.05).buffer(0.05))
    blocks = cleanup_developable_blocks(developable, sliver_area_threshold=400.0)
    if not blocks:
        blocks = [boundary_m]

    # --- open space: whole blocks nearest the site centroid until the share is met
    open_target = rules.open_space_share * gross
    centroid = boundary_m.centroid
    by_proximity = sorted(range(len(blocks)), key=lambda i: blocks[i].centroid.distance(centroid))
    green_indices: set[int] = set()
    open_area = 0.0
    for index in by_proximity:
        if open_area >= open_target or len(green_indices) >= max(1, len(blocks) - 1):
            break
        if open_area + blocks[index].area <= open_target * 1.6:
            green_indices.add(index)
            open_area += blocks[index].area
    if open_area < open_target * 0.5 and len(blocks) > 1:
        result.notes.append({
            "code": "OPEN_SPACE_SHORTFALL", "severity": "warning",
            "message": f"Open space {open_area:,.0f} m² is under half the "
                       f"{open_target:,.0f} m² target — block sizes don't divide cleanly.",
            "source_phase": "civic_distribution",
        })

    # --- parcels + masses on the developable blocks ------------------------------
    district_lookup = _district_lookup_m(district_features or [], to_metric)
    parcels_by_block: list[list[Polygon]] = []
    masses: list[Polygon] = []
    developable_blocks: list[Polygon] = []
    gfa = 0.0
    footprint = 0.0
    clamp_notes = 0

    zone_sort = 500  # after user zones
    for index, block in enumerate(blocks):
        if index in green_indices:
            result.green_m.append(block)
            for poly in iter_polygons(project_geometry(block, to_wgs84)):
                result.zones.append({
                    "zone_type": "green_space",
                    "name": f"{scenario_label} · Park",
                    "coordinates": _ring(poly),
                    "color": PLAN_COLORS["green_space"],
                    "sort_order": zone_sort,
                    "properties": {
                        "_plan_scenario": scenario_id, "_imported_from": layer_name,
                        "_plan_role": "open_space", "tree_density": 0.8,
                    },
                })
                zone_sort += 1
            continue

        developable_blocks.append(block)
        parcels = subdivide_block(block, rules.parcel_width_m)
        parcels_by_block.append(parcels)

        floors, clamp = clamp_floors_to_ceiling(rules.floors, block, district_lookup)
        if clamp:
            clamp_notes += 1

        # Height framework: the block's storey envelope as a MAPPED sub-area
        # (replaces "6-16 storeys" prose with geometry, banded like LAP maps).
        band_ceiling, band_color = _height_band(floors)
        for wpoly in iter_polygons(project_geometry(block, to_wgs84)):
            result.zones.append({
                "zone_type": "development_area",
                "name": f"≤{band_ceiling if band_ceiling != 999 else '27+'} storeys",
                "coordinates": _ring(wpoly),
                "color": band_color,
                "sort_order": 480,
                "properties": {
                    "_plan_scenario": scenario_id,
                    "_imported_from": f"Height framework — {scenario_label}",
                    "_plan_role": "framework_height",
                    "max_floors": round(floors, 1),
                },
            })
        mass, info = building_mass_for_block(block, rules)
        if mass is None:
            continue
        for poly in iter_polygons(mass):
            masses.append(poly)
            result.mass_floors.append(floors)
            footprint += float(poly.area)
            gfa += float(poly.area) * floors
            wgs = project_geometry(poly, to_wgs84)
            for wpoly in iter_polygons(wgs):
                result.zones.append({
                    "zone_type": "building",
                    "name": f"{scenario_label} · Block {index + 1}",
                    "coordinates": _ring(wpoly),
                    "color": PLAN_COLORS["building"],
                    "sort_order": zone_sort,
                    "properties": {
                        "_plan_scenario": scenario_id, "_imported_from": layer_name,
                        "_plan_role": "building", "floors": round(floors, 1),
                        "height": round(floors * FLOOR_HEIGHT_M, 1),
                        **(info or {}),
                        **({"floors_clamped_by": clamp} if clamp else {}),
                    },
                })
                zone_sort += 1

    if clamp_notes:
        result.notes.append({
            "code": "FLOORS_CLAMPED", "severity": "info",
            "message": f"{clamp_notes} blocks clamped to their district height ceiling.",
            "source_phase": "building_placement",
        })

    # --- street zones -------------------------------------------------------------
    for poly in iter_polygons(street_area):
        wgs = project_geometry(poly, to_wgs84)
        for wpoly in iter_polygons(wgs):
            result.zones.append({
                "zone_type": "road",
                "name": f"{scenario_label} · Street",
                "coordinates": _ring(wpoly),
                "color": PLAN_COLORS["road"],
                "sort_order": 490,
                "properties": {
                    "_plan_scenario": scenario_id, "_imported_from": layer_name,
                    "_plan_role": "street", "width": rules.row_width_m,
                    "clear_width_m": rules.clear_width_m,
                },
            })

    # --- validation + metrics inputs -----------------------------------------------
    result.notes.extend(validate_plan(
        rules=rules, network=network, blocks_m=developable_blocks,
        parcels_by_block=parcels_by_block, masses_m=masses,
    ))

    net_block_area = sum(b.area for b in developable_blocks)
    result.geometry_inputs = {
        "site_area_m2": gross,
        "row_area_m2": float(street_area.area) if not street_area.is_empty else 0.0,
        "open_space_area_m2": open_area,
        "net_block_area_m2": float(net_block_area),
        "building_footprint_m2": footprint,
        "gfa_m2": gfa,
    }
    result.intersection_density_per_km2 = (
        len(network.intersections) / (gross / 1_000_000) if gross else 0.0
    )
    result.block_count = len(developable_blocks)
    result.parcel_count = sum(len(p) for p in parcels_by_block)
    result.building_count = sum(1 for z in result.zones if z["zone_type"] == "building")
    result.blocks_m = developable_blocks
    result.masses_m = masses
    return result
