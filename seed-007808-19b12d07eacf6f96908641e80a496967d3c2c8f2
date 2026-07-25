"""Plan generator — orchestrates rules -> streets -> blocks -> parcels -> masses.

Input: WGS84 site boundary, scenario id, PlanParameters, and raw features
(road centrelines + land-use districts) already fetched by the connector.
Output: WGS84 zone dicts ready to insert as SiteZones, plus geometry-mode
inputs for plan_metrics and ValidationNotes. Deterministic; never raises for
data reasons — a degenerate site yields a single-block plan with notes.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import nearest_points, unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.archetypes import (
    resolve_building_archetype,
)
from app.services.plan_geometry.community_rules import (
    FLOOR_HEIGHT_M,
    LANE_ROW_M,
    RuleProfile,
    resolve_rules,
)
from app.services.plan_geometry.layout_validation import validate_plan
from app.services.plan_geometry.parceling import (
    building_mass_for_block,
    clamp_floors_to_ceiling,
    decompose_holed,
    subdivide_block,
)
from app.services.plan_geometry.placement import (
    TYPOLOGY_DIMS,
    Palette,
    carve_lane,
    compute_block_contexts,
    effective_palette,
    plan_blocks,
    resolve_layout_strategy,
    runtime_lego_rectangle_fit,
    selected_target_footprint,
    select_open_space,
    site_hash,
)
from app.services.plan_geometry.street_graph import (
    CRESCENT_SAGITTA_MIN_M,
    StreetNetwork,
    entry_points_from_paths,
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

PLAN_COLORS = {
    "road": "#8a8f98", "green_space": "#5fae5f", "building": "#8b5cf6",
    "water": "#4a90c2",
}

# Height framework bands (amber -> deep red), aligned to LAP building-scale steps.
HEIGHT_BANDS = [(3, "#fde68a"), (6, "#fbbf24"), (12, "#f97316"), (26, "#dc2626"), (999, "#7c2d12")]


def _height_band(floors: float) -> tuple[int, str]:
    for ceiling, color in HEIGHT_BANDS:
        if floors <= ceiling:
            return ceiling, color
    return 999, HEIGHT_BANDS[-1][1]


def _runtime_lego_identities_for_cell(
    identities: list[tuple[str, str, str | None, str | None]],
    *,
    cell: Polygon,
    floors: float,
    palette: Palette,
) -> list[tuple[str, str, str | None, str | None]]:
    """Filter a runtime character cycle against the actual emitted cell."""

    rectangle = cell.minimum_rotated_rectangle
    coordinates = list(rectangle.exterior.coords)
    if len(coordinates) < 4:
        return []
    edges = [
        math.hypot(
            coordinates[index + 1][0] - coordinates[index][0],
            coordinates[index + 1][1] - coordinates[index][1],
        )
        for index in range(2)
    ]
    cell_width_m = max(edges)
    cell_depth_m = min(edges)
    floors_int = max(1, int(round(float(floors))))
    compatible: list[tuple[str, str, str | None, str | None]] = []
    for identity in identities:
        _, _, archetype_id, variant_id = identity
        selectable_id = variant_id or archetype_id
        if selectable_id is None:
            continue
        if floors_int not in palette.supported_floors_by_selectable_id.get(
            selectable_id,
            (),
        ):
            continue
        dimensions = palette.target_dimensions_by_selectable_id.get(selectable_id)
        if dimensions is None:
            continue
        if runtime_lego_rectangle_fit(
            cell_width_m,
            cell_depth_m,
            dimensions[0],
            dimensions[1],
        ):
            compatible.append(identity)
    return compatible


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


def _normalize_site_polygon(
    site_geometry: BaseGeometry,
    *,
    max_discarded_share: float = 0.02,
) -> tuple[Polygon, dict[str, Any] | None]:
    """Repair a negligible invalid-ring sliver or fail with a useful error.

    Older projects may contain the near-closing-vertex bug fixed at the zone
    API. ``make_valid`` represents that as one real site polygon plus a tiny
    fragment. Keeping the dominant component is safe when the discarded share
    is negligible; a material bow-tie or genuinely disjoint site is rejected
    rather than silently losing land.
    """
    was_valid_polygon = isinstance(site_geometry, Polygon) and site_geometry.is_valid
    repaired = make_valid(site_geometry)
    polygons = sorted(iter_polygons(repaired), key=lambda part: part.area, reverse=True)
    if not polygons:
        raise ValueError("Site boundary does not contain a usable polygon")
    total_area = sum(part.area for part in polygons)
    primary = polygons[0]
    discarded_share = max(0.0, total_area - primary.area) / max(total_area, 1e-12)
    if discarded_share > max_discarded_share:
        raise ValueError(
            "Site boundary self-intersects into multiple material areas; redraw the boundary "
            "before generating a master plan"
        )
    if was_valid_polygon and len(polygons) == 1:
        return primary, None
    return primary, {
        "code": "SITE_BOUNDARY_REPAIRED",
        "severity": "warning",
        "message": (
            "A negligible self-intersection at the site-boundary closure was repaired "
            f"({discarded_share:.3%} sliver removed)."
        ),
        "source_phase": "site_boundary",
    }


def _park_access_points_m(
    park_m: Polygon,
    network: StreetNetwork,
    *,
    limit: int = 6,
    dedupe_m: float = 12.0,
) -> list[Point]:
    """Return deterministic gateways where a park fronts the plan network.

    Open-space polygons are carved from blocks, so their frontage sits roughly
    half a ROW-width from a street centreline. Persisting those boundary points
    gives the ground-texture generator exact entrances: its paths can meet the
    same network that already meets the real urban context.
    """
    if park_m.is_empty:
        return []
    boundary = park_m.boundary
    candidates: list[tuple[int, float, float, float, Point]] = []
    role_priority = {"path": 0, "local": 1, "spine": 2}
    for segment in network.segments:
        threshold = segment.row_width_m / 2.0 + 3.0
        distance = boundary.distance(segment.line)
        if distance > threshold:
            continue
        band = segment.line.buffer(threshold, cap_style=2, join_style=2)
        # Intersect one park edge at a time. A band wrapping a corner otherwise
        # returns an L-shaped LineString whose normalized midpoint is pulled
        # away from the centre of the true street-facing edge.
        pieces: list[LineString] = []
        coords = list(park_m.exterior.coords)
        for start, end in zip(coords[:-1], coords[1:]):
            hit = LineString([start, end]).intersection(band)
            if isinstance(hit, LineString):
                pieces.append(hit)
            else:
                pieces.extend(
                    geom for geom in getattr(hit, "geoms", [])
                    if isinstance(geom, LineString)
                )
        usable = [piece for piece in pieces if piece.length > 0.5]
        if usable:
            longest = max(
                usable,
                key=lambda piece: (piece.length, -piece.bounds[0], -piece.bounds[1]),
            )
            park_point = longest.interpolate(0.5, normalized=True)
        else:
            park_point, _street_point = nearest_points(boundary, segment.line)
        candidates.append((
            role_priority.get(segment.role, 3),
            distance,
            park_point.x,
            park_point.y,
            park_point,
        ))

    candidates.sort(key=lambda item: item[:4])
    gateways: list[Point] = []
    for _priority, _distance, _x, _y, point in candidates:
        if all(point.distance(existing) > dedupe_m for existing in gateways):
            gateways.append(point)
        if len(gateways) >= limit:
            break
    return gateways


def _letter(index: int) -> str:
    """1 -> A, 26 -> Z, 27 -> AA … (module segmentation exceeds 26 pieces)."""
    label = ""
    while index > 0:
        index, rem = divmod(index - 1, 26)
        label = chr(65 + rem) + label
    return label


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


_PATH_CONTEXT_TERMS = (
    "footway", "path", "pathway", "trail", "cycleway", "bikeway",
    "pedestrian", "multi-use", "multi use", "shared use",
)
_EXCLUDED_ROAD_CONTEXT_TERMS = (
    "railway", "rail line", "motorway", "freeway", "expressway",
    "controlled access", "skeletal road", "trunk", "off ramp", "on ramp",
    "slip road",
)


def _context_feature_text(feature: dict[str, Any]) -> str:
    props = feature.get("properties") or {}
    return " ".join(
        str(value).lower()
        for key, value in props.items()
        if value is not None and key in {
            "road_type", "highway", "centerline_type", "functional_class_code",
            "road_segment_type_description", "street_type", "asset_type",
            "asset_class", "bicycle_class", "type", "status", "built_status",
            # Calgary calls its limited-access freeway network "Skeletal Road".
            # Other municipal feeds expose the same distinction through one of
            # these generic classification fields.
            "ctp_class", "road_class", "classification", "functional_class",
            "transportation_class", "access", "junction",
        }
    )


def _is_path_context_feature(feature: dict[str, Any]) -> bool:
    text = _context_feature_text(feature)
    return any(term in text for term in _PATH_CONTEXT_TERMS)


def _is_drivable_context_feature(feature: dict[str, Any]) -> bool:
    text = _context_feature_text(feature)
    if _is_path_context_feature(feature):
        return False
    if any(term in text for term in _EXCLUDED_ROAD_CONTEXT_TERMS):
        return False
    props = feature.get("properties") or {}
    lifecycle = " ".join(
        str(props.get(key) or "").strip().lower()
        for key in ("built_status", "status", "plan_status")
    )
    if any(term in lifecycle for term in (
        "proposed", "planned", "future", "closed", "abandoned", "demolished",
    )):
        return False
    if str(props.get("access") or "").strip().lower() in {
        "no", "private", "emergency", "permit",
    }:
        return False
    return True


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


def _param_value(parameters: dict[str, Any], path: str) -> Any:
    merged = parameters.get(path)
    if isinstance(merged, dict) and "value" in merged:
        return merged["value"]
    return merged


def _derive_blocks(
    boundary_m: BaseGeometry, street_area: BaseGeometry | None
) -> tuple[list[Polygon], float]:
    """Streets -> developable blocks, plus the sliver share of gross.

    Morphological opening (erode 5 cm, dilate back): the difference can leave
    hairline bridges at street crossings that keep blocks topologically
    connected — the part count then depends on floating-point noise. Opening
    severs the bridges deterministically at negligible geometric cost.
    Sliver share is measured against the PRE-opening developable area so both
    the opening loss and the sub-threshold discards count."""
    if street_area is not None and not street_area.is_empty:
        developable = boundary_m.difference(street_area)
    else:
        developable = boundary_m
    opened = make_valid(developable.buffer(-0.05).buffer(0.05))
    blocks = cleanup_developable_blocks(opened, sliver_area_threshold=400.0)
    if not blocks:
        return [boundary_m], 0.0
    discarded = max(0.0, float(developable.area) - sum(b.area for b in blocks))
    return blocks, discarded / max(float(boundary_m.area), 1.0)


def _curvilinear_fallback_reason(
    *,
    n_curved: int,
    n_straight: int,
    n_curved_large: int,
    n_straight_large: int,
    sliver_curved: float,
    sliver_straight: float,
) -> str | None:
    """Why a curved candidate must be rejected in favor of the straight grid.

    Pure and unit-testable. Ordering matters: the relative sliver clause runs
    BEFORE the absolute backstop so it is actually reachable (a curved run 2pp
    of gross worse than its straight twin is a curve problem even under 4%)."""
    if n_curved < 2:
        return "BLOCKS_COLLAPSED"
    if n_curved < n_straight:
        return "BLOCKS_MERGED"
    if n_curved_large < min(n_straight_large, 2):
        return "BLOCKS_FRAGMENTED"       # curve shattered buildable blocks into pocket-park chum
    if sliver_curved > sliver_straight + 0.02:
        return "SLIVER_EXCESS_REL"
    if sliver_curved > 0.04:
        return "SLIVER_EXCESS_ABS"
    return None


def generate_plan_geometry(
    *,
    site_polygon_wgs84: Polygon,
    scenario_id: str,
    scenario_label: str,
    parameters: dict[str, Any],
    road_features: list[dict[str, Any]] | None = None,
    path_features: list[dict[str, Any]] | None = None,
    district_features: list[dict[str, Any]] | None = None,
    locked_street_area_wgs84: Polygon | None = None,
    rule_overrides: dict[str, float] | None = None,
    rule_hints: dict[str, float] | None = None,
    dna: dict[str, Any] | None = None,
    palette_hint: str | None = None,
    measured_model_dims: dict | None = None,
    palette_override: "Palette | None" = None,
) -> PlanGeometryResult:
    result = PlanGeometryResult()
    layer_name = f"Plan — {scenario_label}"

    # Semantic hints for the render pipeline: the frontend resolves archetype
    # references from these (development_type/aesthetic -> building archetype,
    # tree_density/ground_texture -> park character). Strings only, clipped.
    # Expert-emitted values override the placement palette's MID band only;
    # the transect bands (edge/core/frontage/anchor) keep their strategic
    # roles — see placement.plan_blocks.
    raw_type = _param_value(parameters, "buildings.development_type")
    base_development_type = str(raw_type)[:60] if raw_type else None
    development_aesthetic = _param_value(parameters, "buildings.development_aesthetic")
    base_aesthetic = str(development_aesthetic)[:60] if development_aesthetic else None
    tree_density_param = _param_value(parameters, "landscape.tree_density")
    tree_density = float(tree_density_param) if isinstance(tree_density_param, (int, float)) else 0.8
    ground_texture = _param_value(parameters, "landscape.ground_texture")
    ground_texture = str(ground_texture)[:60] if ground_texture else None

    site, boundary_repair_note = _normalize_site_polygon(site_polygon_wgs84)
    if boundary_repair_note is not None:
        result.notes.append(boundary_repair_note)
    crs = local_metric_crs_for_polygon(site)
    to_metric = build_transformer("EPSG:4326", crs)
    to_wgs84 = build_transformer(crs, "EPSG:4326")
    boundary_m = make_valid(project_geometry(site, to_metric))
    gross = float(boundary_m.area)

    rules, rule_notes = resolve_rules(scenario_id, parameters, rule_hints=rule_hints)
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
        "spine_row_width_m": rules.spine_row_width_m,
        "local_row_width_m": rules.local_row_width_m,
    }

    # Placement policy resolves BEFORE streets: the palette now gates street
    # geometry (curvilinear grids) as well as archetype character. A master-
    # plan palette arrives fully authored — the layout-strategy collapse and
    # the experts' mid-band override would both undo its deliberate variety,
    # so it bypasses them (the planner already read the expert parameters).
    district_lookup = _district_lookup_m(district_features or [], to_metric)
    if palette_override is not None:
        palette = palette_override
        base_development_type = None
        base_aesthetic = None
    else:
        strategy = resolve_layout_strategy(_param_value(parameters, "layout.strategy"))
        palette = effective_palette(scenario_id, strategy, palette_hint)
    seed = site_hash(boundary_m)

    # --- streets (or the locked network) --------------------------------------
    if locked_street_area_wgs84 is not None and not locked_street_area_wgs84.is_empty:
        network = StreetNetwork()
        network.street_area = make_valid(project_geometry(make_valid(locked_street_area_wgs84), to_metric))
        result.notes.append({
            "code": "STREETS_LOCKED", "severity": "info",
            "message": "Street network locked by the user — regenerated blocks/massing only.",
            "source_phase": "street_graph",
        })
        blocks, _ = _derive_blocks(boundary_m, network.street_area)
    else:
        raw_roads = road_features or []
        road_lines = _feature_lines_m(
            [feature for feature in raw_roads if _is_drivable_context_feature(feature)],
            to_metric,
        )
        # Generic OSM's road feed also contains footways/cycleways. Promote
        # those to pedestrian context, alongside explicit city pathway and
        # bikeway datasets supplied by the plan task.
        raw_paths = list(path_features or []) + [
            feature for feature in raw_roads if _is_path_context_feature(feature)
        ]
        path_lines = _feature_lines_m(raw_paths, to_metric)
        entries = entry_points_from_roads(road_lines, boundary_m)
        path_entries = entry_points_from_paths(path_lines, boundary_m)
        # Straight baseline always generated — it is the fallback AND the
        # yardstick the curved candidates are judged against.
        network = generate_street_network(
            boundary_m, rules, entries, path_entry_points=path_entries,
        )
        blocks, sliver_straight = _derive_blocks(boundary_m, network.street_area)
        if palette.curvilinear and network.segments:
            straight_network, straight_blocks = network, blocks
            n_straight_large = sum(1 for b in straight_blocks if b.area >= 2000.0)
            rejections: list[tuple[str, str]] = []
            applied = False
            for mode in ("all", "spine"):     # graduated: full vision, then bow, then straight
                candidate = generate_street_network(
                    boundary_m, rules, entries, path_entry_points=path_entries,
                    curve_mode=mode, seed=seed,
                )
                if candidate.curve_mode == "none":
                    rejections.append((mode, candidate.curve_skip_reason or "AMPLITUDE_BELOW_MIN"))
                    continue
                c_blocks, sliver_curved = _derive_blocks(boundary_m, candidate.street_area)
                reason = _curvilinear_fallback_reason(
                    n_curved=len(c_blocks),
                    n_straight=len(straight_blocks),
                    n_curved_large=sum(1 for b in c_blocks if b.area >= 2000.0),
                    n_straight_large=n_straight_large,
                    sliver_curved=sliver_curved,
                    sliver_straight=sliver_straight,
                )
                if reason is None:
                    network, blocks = candidate, c_blocks
                    rejected_suffix = (
                        "; rejected " + ", ".join(f"{m}:{r}" for m, r in rejections)
                        if rejections else ""
                    )
                    network.notes.append({
                        "code": "CURVILINEAR_APPLIED", "severity": "info",
                        "message": f"Streets follow a gentle curve toward the site's heart "
                                   f"(mode={mode}{rejected_suffix}).",
                        "source_phase": "street_graph",
                    })
                    applied = True
                    break
                rejections.append((mode, reason))
            if not applied:
                # The guard is the SOLE curvature-note authority: exactly one
                # outcome note for a curvilinear palette on a viable site.
                guard_rejected = [r for r in rejections
                                  if r[1] not in ("AMPLITUDE_BELOW_MIN", "NO_LONG_AXIS_ROWS")]
                network, blocks = straight_network, straight_blocks
                if guard_rejected:
                    network.notes.append({
                        "code": "CURVILINEAR_FALLBACK", "severity": "info",
                        "message": "Curved grid rejected ("
                                   + "; ".join(f"{m}:{r}" for m, r in rejections)
                                   + "); straight grid kept.",
                        "source_phase": "street_graph",
                    })
                elif rejections:
                    network.notes.append({
                        "code": "CURVILINEAR_SKIPPED", "severity": "info",
                        "message": "Site too tight to curve the grid ("
                                   + "; ".join(f"{m}:{r}" for m, r in rejections)
                                   + ") — straight grid kept.",
                        "source_phase": "street_graph",
                    })
    result.notes.extend(network.notes)
    street_area = network.street_area if network.street_area is not None else Polygon()

    # --- open space + placement policy ------------------------------------------
    open_target = rules.open_space_share * gross
    open_plan = select_open_space(
        blocks=blocks, boundary_m=boundary_m, rules=rules, palette=palette,
        network=network, seed=seed,
    )
    open_spaces_m = [spec.geom_m for spec in open_plan.specs]
    open_area = open_plan.open_area_m2
    if open_area < open_target * 0.5 and len(blocks) > 1:
        result.notes.append({
            "code": "OPEN_SPACE_SHORTFALL", "severity": "warning",
            "message": f"Open space {open_area:,.0f} m² is under half the "
                       f"{open_target:,.0f} m² target — block sizes don't divide cleanly.",
            "source_phase": "civic_distribution",
        })

    # Landscape structure per green kind (mirrored by the globe's parkScatter):
    # ponds are water, everything else plants to the palette's design intent.
    _LANDSCAPE_KEY = {"central": "park", "pocket": "pocket",
                      "greenway": "greenway", "plaza": "plaza"}
    # Parks without a palette/LLM archetype get a catalog fallback so the
    # globe park kit resolves a real furniture recipe (playgrounds/pavilions
    # gate on planting_structure + area downstream, not here). Ponds keep
    # their water ids; enclosed courtyards are stamped when emitted below.
    _PARK_ARCHETYPE_FALLBACK = {
        "central": "neighborhood_park",
        "pocket": "urban_pocket_park",
        "greenway": "linear_park_greenway",
        "plaza": "formal_civic_plaza",
        # Formal palettes provide their own fountain id. An otherwise
        # unspecified pond is operational green infrastructure, so it must use
        # the authored stormwater profile rather than generic open space.
        "pond": "stormwater_retention_pond",
    }

    zone_sort = 500  # after user zones
    for spec in open_plan.specs:
        result.green_m.append(spec.geom_m)
        color = PLAN_COLORS["water"] if spec.kind == "pond" else PLAN_COLORS["green_space"]
        planting = palette.landscape.get(_LANDSCAPE_KEY.get(spec.kind, ""))
        archetype_id = spec.archetype_id or _PARK_ARCHETYPE_FALLBACK.get(spec.kind)
        for poly_m in iter_polygons(spec.geom_m):
            poly = project_geometry(poly_m, to_wgs84)
            access_points = [
                project_geometry(point, to_wgs84)
                for point in _park_access_points_m(poly_m, network)
            ]
            result.zones.append({
                "zone_type": "green_space",
                "name": f"{scenario_label} · {spec.name_suffix}",
                "coordinates": _ring(poly),
                "color": color,
                "sort_order": zone_sort,
                "properties": {
                    "_plan_scenario": scenario_id, "_imported_from": layer_name,
                    "_plan_role": "open_space", "tree_density": tree_density,
                    "green_kind": spec.kind,
                    **({"green_space_archetype_id": archetype_id}
                       if archetype_id else {}),
                    **({"ground_texture": ground_texture} if ground_texture else {}),
                    **({"planting_structure": planting} if planting else {}),
                    **({
                        "park_access_points": [
                            [float(point.x), float(point.y)] for point in access_points
                        ],
                    } if access_points else {}),
                },
            })
            zone_sort += 1

    # --- parcels + masses on the developable blocks ------------------------------
    loop_blocks = [
        (index, open_plan.carved_blocks.get(index, block))
        for index, block in enumerate(blocks)
        if index not in open_plan.consumed_indices
    ]
    contexts = compute_block_contexts(
        blocks=loop_blocks, boundary_m=boundary_m, network=network,
        district_lookup=district_lookup, signature_green_m=open_plan.central_geom_m,
    )
    block_plans = plan_blocks(
        contexts=contexts, palette=palette, rules=rules,
        base_type=base_development_type, base_aesthetic=base_aesthetic, dna=dna,
        measured_dims=measured_model_dims,
    )

    parcels_by_block: list[list[Polygon]] = []
    masses: list[Polygon] = []
    developable_blocks: list[Polygon] = []
    gfa = 0.0
    footprint = 0.0
    lane_area_total = 0.0
    clamp_notes = 0

    for index, block in loop_blocks:
        plan = block_plans[index]
        developable_blocks.append(block)
        parcels = subdivide_block(block, rules.parcel_width_m)
        parcels_by_block.append(parcels)

        floors, clamp = clamp_floors_to_ceiling(plan.floors_target, block, district_lookup)
        if clamp:
            clamp_notes += 1

        # The district clamp can move floors outside the resolved archetype's
        # range — re-resolve so the emitted archetype always matches the
        # emitted storeys (and the target scales with the real height).
        plan_archetype_id = plan.archetype_id
        plan_variant_id = plan.variant_id
        plan_development_type = plan.development_type
        plan_aesthetic = plan.aesthetic
        target = plan.target
        if clamp and round(floors, 1) != plan.floors_target:
            ceiling_floors = max(1, int(float(floors)))
            supported_by_parent = None
            if palette.allowed_archetype_ids is not None:
                supported_by_parent = {
                    parent_id: tuple(sorted({
                        supported_floor
                        for selectable_id in (
                            parent_id,
                            *palette.allowed_variant_ids_by_archetype.get(parent_id, ()),
                        )
                        for supported_floor in palette.supported_floors_by_selectable_id.get(
                            selectable_id, ()
                        )
                        if supported_floor <= ceiling_floors
                    }))
                    for parent_id in palette.allowed_archetype_ids
                }
                supported_by_parent = {
                    parent_id: values
                    for parent_id, values in supported_by_parent.items()
                    if values
                }
            entry = resolve_building_archetype(
                plan.development_type,
                plan.aesthetic,
                ceiling_floors,
                prefer_family=palette.style_family,
                allowed_archetype_ids=(
                    supported_by_parent.keys()
                    if supported_by_parent is not None
                    else None
                ),
                supported_floors_by_archetype=supported_by_parent,
            )
            plan_archetype_id = entry["id"] if entry else None
            measured_entry = (measured_model_dims or {}).get(plan_archetype_id) if entry else None
            plan_variant_id = measured_entry.variant_id if measured_entry else None
            if entry and palette.allowed_archetype_ids is not None:
                preferred_selectable_id = (
                    plan.variant_id
                    if entry["id"] == plan.archetype_id and plan.variant_id
                    else entry["id"]
                )
                candidates = [
                    (
                        ceiling_floors - supported_floor,
                        0 if selectable_id == preferred_selectable_id else 1,
                        selectable_id,
                        supported_floor,
                    )
                    for selectable_id in (
                        entry["id"],
                        *palette.allowed_variant_ids_by_archetype.get(entry["id"], ()),
                    )
                    for supported_floor in palette.supported_floors_by_selectable_id.get(
                        selectable_id, ()
                    )
                    if supported_floor <= ceiling_floors
                ]
                if candidates:
                    _, _, selectable_id, selected_floors = min(candidates)
                    floors = float(selected_floors)
                    plan_variant_id = (
                        selectable_id if selectable_id != entry["id"] else None
                    )
                    plan_development_type = entry["development_type"]
                    plan_aesthetic = entry["aesthetic_category"]
            target = selected_target_footprint(
                entry,
                max(1, int(round(floors))),
                measured_model_dims,
                palette,
                plan_variant_id or plan_archetype_id,
            )

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
        # Rear laneway: split large row-bar blocks with a mid-block lane so
        # townhouse rows front the street and back onto a lane (masses are
        # built on block − lane; the ORIGINAL block stays in blocks_m so the
        # evaluator's block_scale and the height framework are unchanged).
        # Only when this run generated the streets — a locked network means
        # the user froze circulation, lanes included.
        lane = None
        if palette.laneways and plan.typology == "row_bars" and network.segments:
            lane = carve_lane(block, LANE_ROW_M)
        mass_block = make_valid(block.difference(lane)) if lane is not None else block

        mass, info = building_mass_for_block(
            mass_block, rules,
            typology=plan.typology, dims=TYPOLOGY_DIMS.get(plan.typology),
            target=target,
        )
        if mass is None:
            continue
        typology_used = (info or {}).get("typology", "perimeter_block")

        if lane is not None:
            lane_area_total += float(lane.area)
            for wpoly in iter_polygons(project_geometry(lane, to_wgs84)):
                result.zones.append({
                    "zone_type": "road",
                    "name": f"{scenario_label} · Block {index + 1} Lane",
                    "coordinates": _ring(wpoly),
                    "color": PLAN_COLORS["road"],
                    "sort_order": 490,
                    "properties": {
                        "_plan_scenario": scenario_id, "_imported_from": layer_name,
                        "_plan_role": "street", "width": LANE_ROW_M,
                        "street_role": "lane", "road_archetype_id": "toronto_laneway",
                    },
                })

        # Model-aware identity: emitting the resolved archetype id makes the
        # frontend resolver keep it (user-override precedence), threads it
        # into Building.specifications -> model-cache hits, and lets the
        # globe place the exact GLB these parcels were carved for. The
        # variant id is emitted ONLY when it names the measured cache row
        # (a synthesized variant would normalize to a different cache key).
        # Bars rotate through the band's width-compatible characters so a
        # perimeter ring reads as several buildings, not one model stamped N
        # times — suppressed when a district clamp moved the floors (the
        # options were resolved at the unclamped height).
        bar_identities: list[tuple[str, str, str | None, str | None]] = [
            (plan_development_type, plan_aesthetic, plan_archetype_id, plan_variant_id)
        ]
        if not clamp:
            bar_identities.extend(
                (o.development_type, o.aesthetic, o.archetype_id, o.variant_id)
                for o in plan.bar_options
            )

        mass_polys = list(iter_polygons(mass))
        bar_index = 0
        for poly in mass_polys:
            masses.append(poly)
            result.mass_floors.append(floors)
            footprint += float(poly.area)
            gfa += float(poly.area) * floors
            wgs = project_geometry(poly, to_wgs84)
            for wpoly in iter_polygons(wgs):
                # Mass decomposition yields several pieces per block —
                # unique names, or every label on the globe reads "Block 1".
                bar_index += 1
                suffix = f" · Building {_letter(bar_index)}" if len(mass_polys) > 1 else ""
                compatible_identities = bar_identities
                if (
                    palette.allowed_archetype_ids is not None
                    and target is not None
                    and target.source == "runtime_lego"
                ):
                    compatible_identities = _runtime_lego_identities_for_cell(
                        bar_identities,
                        cell=poly,
                        floors=floors,
                        palette=palette,
                    )
                    # The mass itself was carved for the primary runtime target
                    # with the same guarded envelope, so this is defensive only.
                    if not compatible_identities:
                        compatible_identities = [bar_identities[0]]
                dev_out, aes_out, arch_out, variant_out = compatible_identities[
                    (bar_index - 1) % len(compatible_identities)
                ]
                archetype_props: dict[str, Any] = {}
                if arch_out:
                    archetype_props["development_archetype_id"] = arch_out
                    if variant_out and variant_out != "default":
                        archetype_props["development_selected_variant_id"] = variant_out
                    if target is not None:
                        # Carve dims stay the primary's: they describe the
                        # parcel grid, not the bar's model.
                        archetype_props["target_w_m"] = round(target.width_m, 1)
                        archetype_props["target_d_m"] = round(target.depth_m, 1)
                        archetype_props["archetype_source"] = target.source
                result.zones.append({
                    "zone_type": "building",
                    "name": f"{scenario_label} · Block {index + 1}{suffix}",
                    "coordinates": _ring(wpoly),
                    "color": PLAN_COLORS["building"],
                    "sort_order": zone_sort,
                    "properties": {
                        "_plan_scenario": scenario_id, "_imported_from": layer_name,
                        "_plan_role": "building", "floors": round(floors, 1),
                        "height": round(floors * FLOOR_HEIGHT_M, 1),
                        "development_type": dev_out,
                        "development_aesthetic": aes_out,
                        "_plan_band": plan.band,
                        **archetype_props,
                        **(info or {}),
                        **({"floors_clamped_by": clamp} if clamp else {}),
                    },
                })
                zone_sort += 1

        # The perimeter bars enclose a courtyard the mass ring left unbuilt —
        # draw it, or a single-block plan reads as one solid slab with no
        # visible open space. Visual zone only: NOT counted in open-space
        # metrics and NOT part of the frozen evaluator loop. Perimeter blocks
        # only: tower pads and row bars leave open ground, not a courtyard.
        if typology_used == "perimeter_block" and len(mass_polys) > 1:
            courtyard = make_valid(
                block.buffer(-rules.front_setback_m).difference(unary_union(mass_polys))
            )
            # Hole-free before drawing: a courtyard that wraps an interior bar
            # is a donut, and zone rings are exterior-only app-wide — drawn raw
            # it would fill the hole and paint green UNDER the buildings.
            courtyard = decompose_holed(courtyard, block)
            for cpoly in iter_polygons(courtyard):
                if cpoly.area < 150.0:
                    continue
                open_spaces_m.append(cpoly)
                # Projection can turn a metric-space cut that shares a seam
                # into a microscopic WGS84 self-intersection. Repair after
                # projection as the final serialization boundary; otherwise
                # PostGIS accepts the ring but the globe receives an invalid
                # courtyard polygon.
                projected_courtyard = make_valid(project_geometry(cpoly, to_wgs84))
                for wpoly in iter_polygons(projected_courtyard):
                    result.zones.append({
                        "zone_type": "green_space",
                        "name": f"{scenario_label} · Block {index + 1} courtyard",
                        "coordinates": _ring(wpoly),
                        "color": PLAN_COLORS["green_space"],
                        "sort_order": zone_sort,
                        "properties": {
                            "_plan_scenario": scenario_id, "_imported_from": layer_name,
                            "_plan_role": "courtyard", "tree_density": tree_density,
                            "green_space_archetype_id": "urban_pocket_park",
                            **({"planting_structure": palette.landscape["courtyard"]}
                               if palette.landscape.get("courtyard") else {}),
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
    _emit_street_zones(
        result=result, network=network, street_area=street_area, rules=rules,
        palette=palette, scenario_id=scenario_id, scenario_label=scenario_label,
        layer_name=layer_name, to_wgs84=to_wgs84,
    )

    # --- validation + metrics inputs -----------------------------------------------
    result.notes.extend(validate_plan(
        rules=rules, network=network, blocks_m=developable_blocks,
        parcels_by_block=parcels_by_block, masses_m=masses,
        open_spaces_m=open_spaces_m,
    ))

    # Lanes count as ROW: +lane on the street side, −lane on the block side is
    # an exact identity, so the land budget still closes.
    net_block_area = sum(b.area for b in developable_blocks) - lane_area_total
    result.geometry_inputs = {
        "site_area_m2": gross,
        "row_area_m2": (float(street_area.area) if not street_area.is_empty else 0.0)
                       + lane_area_total,
        "open_space_area_m2": open_area,
        "net_block_area_m2": float(net_block_area),
        "building_footprint_m2": footprint,
        "gfa_m2": gfa,
        # First-class context metrics let the evaluator, plan sheet and future
        # UI report real network continuity without parsing prose notes.
        "context_road_anchors": float(network.entries_total),
        "context_road_connections": float(network.entries_served),
        "context_path_anchors": float(network.path_entries_total),
        "context_path_connections": float(network.path_entries_served),
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


def _default_road_archetype_id(role: str, width: float) -> str:
    """Persist the same measured street identity the frontend would infer."""

    if role == "path":
        return "multi_use_trail"
    if role == "lane":
        return "toronto_laneway"
    if role == "roundabout":
        return "roundabout"
    if width < 10:
        return "yield_street"
    if width < 15:
        return "narrow_residential_street"
    if width < 22:
        return "collector_road"
    return "main_street_complete"


def _street_zone(
    poly_m, *, name: str, width: float, role: str, rules: RuleProfile,
    scenario_id: str, layer_name: str, to_wgs84,
    archetype_id: str | None = None,
    context_connection: bool = False,
) -> list[dict[str, Any]]:
    zones = []
    resolved_archetype_id = archetype_id or _default_road_archetype_id(role, width)
    for wpoly in iter_polygons(project_geometry(poly_m, to_wgs84)):
        zones.append({
            "zone_type": "road",
            "name": name,
            "coordinates": _ring(wpoly),
            "color": PLAN_COLORS["road"],
            "sort_order": 490,
            "properties": {
                "_plan_scenario": scenario_id, "_imported_from": layer_name,
                "_plan_role": "street", "width": width,
                "clear_width_m": width if role == "path" else rules.clear_width_m,
                "street_role": role,
                **({"context_connection": True} if context_connection else {}),
                "road_archetype_id": resolved_archetype_id,
            },
        })
    return zones


def _emit_street_zones(
    *,
    result: PlanGeometryResult,
    network: StreetNetwork,
    street_area,
    rules: RuleProfile,
    palette,
    scenario_id: str,
    scenario_label: str,
    layer_name: str,
    to_wgs84,
) -> None:
    """Partition the merged street area into per-role zones (roundabouts, then
    the spine, then locals) via ordered subtraction — the pieces sum exactly
    to street_area, so the land budget is unchanged. A network without
    segments (locked streets / degenerate sites) emits the legacy single-width
    zones.

    Two robustness rules for curved geometry:
    - every subtraction operand is precision-snapped to a 1 mm grid (bowed
      bands crossing straights at near-tangents otherwise trip GEOS
      "non-noded intersection" — observed at refinement iteration 2 when
      block_target shrinks and the bow regenerates);
    - a HOLED street polygon (a locked curved network unions into one
      connected ring whose holes are the blocks) is decomposed before
      emission — zone rings are exterior-only app-wide, so emitting it raw
      would draw the whole site as asphalt."""
    from shapely import set_precision

    from app.services.plan_geometry.parceling import decompose_holed

    def _snap(geom):
        return make_valid(set_precision(geom, 1e-3))

    if street_area.is_empty:
        return
    if not network.segments:
        for poly in iter_polygons(street_area):
            pieces = iter_polygons(decompose_holed(poly, poly)) if poly.interiors else [poly]
            for piece in pieces:
                result.zones.extend(_street_zone(
                    piece, name=f"{scenario_label} · Street", width=rules.row_width_m,
                    role="local", rules=rules, scenario_id=scenario_id,
                    layer_name=layer_name, to_wgs84=to_wgs84,
                ))
        return

    remaining = _snap(street_area)
    for n, (point, radius) in enumerate(network.roundabouts, start=1):
        piece = make_valid(_snap(point.buffer(radius, quad_segs=8)).intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        result.zones.extend(_street_zone(
            piece, name=f"{scenario_label} · Roundabout {n}",
            width=rules.spine_row_width_m, role="roundabout", rules=rules,
            scenario_id=scenario_id, layer_name=layer_name, to_wgs84=to_wgs84,
            archetype_id="roundabout",
        ))

    spine_segments = [s for s in network.segments if s.role == "spine"]
    for segment in spine_segments:
        band = _snap(segment.line.buffer(segment.row_width_m / 2, cap_style=2, join_style=2))
        piece = make_valid(band.intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        result.zones.extend(_street_zone(
            piece, name=f"{scenario_label} · Main Street",
            width=segment.row_width_m, role="spine", rules=rules,
            scenario_id=scenario_id, layer_name=layer_name, to_wgs84=to_wgs84,
            archetype_id=getattr(palette, "spine_archetype_id", None),
        ))

    path_counter = 0
    for segment in (s for s in network.segments if s.role == "path"):
        band = _snap(segment.line.buffer(segment.row_width_m / 2, cap_style=2, join_style=2))
        piece = make_valid(band.intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        path_counter += 1
        result.zones.extend(_street_zone(
            piece, name=f"{scenario_label} · Path Connection {path_counter}",
            width=segment.row_width_m, role="path", rules=rules,
            scenario_id=scenario_id, layer_name=layer_name, to_wgs84=to_wgs84,
            archetype_id="multi_use_trail", context_connection=True,
        ))

    local_archetype = getattr(palette, "local_archetype_id", None)
    crescent_archetype = getattr(palette, "crescent_archetype_id", None)
    counter = 0
    for segment in (s for s in network.segments if s.role not in ("spine", "path")):
        band = _snap(segment.line.buffer(segment.row_width_m / 2, cap_style=2, join_style=2))
        piece = make_valid(band.intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        counter += 1
        # Crescent precedence: a genuinely bowed local resolves to the crescent
        # street archetype when the palette provides one. Environmental keeps
        # crescent_archetype_id=None so woonerf wins on every local, bowed or not.
        archetype = local_archetype
        if crescent_archetype and segment.sagitta_m >= CRESCENT_SAGITTA_MIN_M:
            archetype = crescent_archetype
        segment_name = (
            f"{scenario_label} · Access Connection {counter}"
            if segment.context_connection else f"{scenario_label} · Street {counter}"
        )
        result.zones.extend(_street_zone(
            piece, name=segment_name,
            width=segment.row_width_m, role="local", rules=rules,
            scenario_id=scenario_id, layer_name=layer_name, to_wgs84=to_wgs84,
            archetype_id=archetype, context_connection=segment.context_connection,
        ))

    # Numerical crumbs from the subtractions (shouldn't happen, but never
    # silently drop street land — the budget is measured against street_area).
    # Residue inherits the palette's local archetype so scenario street
    # invariants (e.g. environmental all-woonerf) hold on every road zone.
    for poly in iter_polygons(make_valid(remaining)):
        if poly.area < 1.0:
            continue
        counter += 1
        result.zones.extend(_street_zone(
            poly, name=f"{scenario_label} · Street {counter}",
            width=rules.local_row_width_m, role="local", rules=rules,
            scenario_id=scenario_id, layer_name=layer_name, to_wgs84=to_wgs84,
            archetype_id=local_archetype,
        ))
