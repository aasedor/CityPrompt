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
from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely import affinity, set_precision
from shapely.geometry import LineString, Point, Polygon, box, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import nearest_points, unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.archetypes import (
    TargetFootprint,
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
from app.services.public_realm_lego import (
    build_public_realm_capability_catalog,
    plan_public_realm_metric_street_recipe,
    public_realm_park_archetype_supports_metric_geometry,
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
    "road": "#8a8f98",
    "green_space": "#5fae5f",
    "building": "#8b5cf6",
    "water": "#4a90c2",
}

# Height framework bands (amber -> deep red), aligned to LAP building-scale steps.
HEIGHT_BANDS = [(3, "#fde68a"), (6, "#fbbf24"), (12, "#f97316"), (26, "#dc2626"), (999, "#7c2d12")]


def _height_band(floors: float) -> tuple[int, str]:
    for ceiling, color in HEIGHT_BANDS:
        if floors <= ceiling:
            return ceiling, color
    return 999, HEIGHT_BANDS[-1][1]


def _split_building_cell(cell: Polygon, clearance_m: float) -> list[Polygon] | None:
    """Split one cell into two footprints with a real metric gap."""

    rectangle = cell.minimum_rotated_rectangle
    coordinates = list(rectangle.exterior.coords)
    if len(coordinates) < 4:
        return None
    edges = [
        (
            math.hypot(
                coordinates[index + 1][0] - coordinates[index][0],
                coordinates[index + 1][1] - coordinates[index][1],
            ),
            math.degrees(
                math.atan2(
                    coordinates[index + 1][1] - coordinates[index][1],
                    coordinates[index + 1][0] - coordinates[index][0],
                )
            ),
        )
        for index in range(2)
    ]
    longest, angle = max(edges, key=lambda item: item[0])
    if longest < 12.0 + clearance_m:
        return None
    origin = cell.centroid
    work = affinity.rotate(cell, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds
    cut_x = (minx + maxx) / 2.0
    cut = box(cut_x - clearance_m / 2.0, miny - 1.0, cut_x + clearance_m / 2.0, maxy + 1.0)
    pieces = [
        piece
        for piece in iter_polygons(make_valid(work.difference(cut)))
        if piece.area >= 80.0
    ]
    if len(pieces) != 2:
        return None
    return [affinity.rotate(piece, angle, origin=origin) for piece in pieces]


def _exact_building_cells(
    cells: list[Polygon],
    target_count: int,
    *,
    clearance_m: float = 4.0,
) -> list[Polygon]:
    """Return an exact bounded count when the existing mass can support it.

    The normal massing remains the design authority. Extra cells are obtained
    only by splitting its largest viable footprint and removing a true gap;
    no geometry is allowed outside the already validated building mass.
    """

    target_count = max(1, min(20, int(target_count)))
    selected = list(cells)
    while len(selected) < target_count:
        split_index = None
        split_pieces = None
        for index in sorted(range(len(selected)), key=lambda value: (-selected[value].area, value)):
            candidate = _split_building_cell(selected[index], clearance_m)
            if candidate is not None:
                split_index = index
                split_pieces = candidate
                break
        if split_index is None or split_pieces is None:
            break
        selected[split_index : split_index + 1] = split_pieces
    if len(selected) > target_count:
        keep = sorted(range(len(selected)), key=lambda value: (-selected[value].area, value))[:target_count]
        selected = [selected[index] for index in sorted(keep)]
    return selected


def _pack_exact_target_cells(
    block: BaseGeometry,
    target_count: int,
    target: TargetFootprint,
    *,
    setback_m: float,
    clearance_m: float = 4.0,
) -> list[Polygon] | None:
    """Pack native-footprint LEGO cells on a compact developable block.

    A count contract must not be satisfied by shrinking a reviewed 20 x 15 m
    module into four incompatible slivers. The primary family owns frontage
    and depth; this bounded grid keeps both unchanged and returns ``None``
    when the site genuinely cannot fit them.
    """

    target_count = max(1, min(20, int(target_count)))
    rectangle = block.minimum_rotated_rectangle
    coordinates = list(rectangle.exterior.coords)
    if len(coordinates) < 4:
        return None
    edges = [
        (
            math.hypot(
                coordinates[index + 1][0] - coordinates[index][0],
                coordinates[index + 1][1] - coordinates[index][1],
            ),
            math.degrees(
                math.atan2(
                    coordinates[index + 1][1] - coordinates[index][1],
                    coordinates[index + 1][0] - coordinates[index][0],
                )
            ),
        )
        for index in range(2)
    ]
    _longest, angle = max(edges, key=lambda item: item[0])
    origin = block.centroid
    safe = make_valid(block.buffer(-max(0.0, setback_m)))
    if safe.is_empty:
        return None
    work = make_valid(affinity.rotate(safe, -angle, origin=origin))
    columns = max(1, math.ceil(math.sqrt(target_count)))
    rows = math.ceil(target_count / columns)
    total_width = columns * target.width_m + (columns - 1) * clearance_m
    total_depth = rows * target.depth_m + (rows - 1) * clearance_m
    center_x, center_y = work.centroid.x, work.centroid.y
    start_x = center_x - total_width / 2.0
    start_y = center_y - total_depth / 2.0
    cells: list[Polygon] = []
    for index in range(target_count):
        row, column = divmod(index, columns)
        x0 = start_x + column * (target.width_m + clearance_m)
        y0 = start_y + row * (target.depth_m + clearance_m)
        cell = box(x0, y0, x0 + target.width_m, y0 + target.depth_m)
        if not work.buffer(0.05).covers(cell):
            return None
        cells.append(affinity.rotate(cell, angle, origin=origin))
    return cells


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


def _line_parts(geometry: BaseGeometry) -> list[LineString]:
    if isinstance(geometry, LineString):
        return [geometry] if geometry.length > 0 and len(geometry.coords) >= 2 else []
    return [
        part
        for part in getattr(geometry, "geoms", ())
        if isinstance(part, LineString) and part.length > 0 and len(part.coords) >= 2
    ]


def _principal_street_centerline_m(geometry_m: BaseGeometry) -> LineString | None:
    """Recover a deterministic centreline for an attestable locked street band."""

    rectangle = geometry_m.minimum_rotated_rectangle
    exterior = getattr(rectangle, "exterior", None)
    if exterior is None:
        return None
    coordinates = list(exterior.coords)
    if len(coordinates) < 5:
        return None
    edges = sorted(
        (
            math.dist(coordinates[index], coordinates[index + 1]),
            index,
        )
        for index in range(4)
    )
    if edges[-1][0] < edges[0][0] * 1.5:
        return None
    short_edges = edges[:2]
    midpoints = [
        (
            (coordinates[index][0] + coordinates[index + 1][0]) / 2,
            (coordinates[index][1] + coordinates[index + 1][1]) / 2,
        )
        for _length, index in short_edges
    ]
    candidates = _line_parts(LineString(midpoints).intersection(geometry_m.buffer(1e-6)))
    if not candidates:
        return None
    candidate = max(candidates, key=lambda line: line.length)
    # A bent or crescent street can intersect its bounding-box axis only in a
    # short chord. Refuse that false straight line and leave the legacy curved
    # reconstruction in control instead of persisting bad metadata.
    return candidate if candidate.length >= edges[-1][0] * 0.72 else None


def _plan_centerline_coordinates(
    centerline_m: BaseGeometry | None,
    zone_wgs84: Polygon,
    *,
    to_wgs84,
) -> list[list[float]] | None:
    """Clip the authored metric line to one emitted zone and serialize lng/lat."""

    if centerline_m is None or centerline_m.is_empty:
        return None
    centerline_wgs84 = project_geometry(centerline_m, to_wgs84)
    candidates = _line_parts(centerline_wgs84.intersection(zone_wgs84))
    if not candidates:
        # Projection can put an endpoint a few floating-point units outside
        # the polygon.  This is roughly a centimetre, far below a street band.
        candidates = _line_parts(centerline_wgs84.intersection(zone_wgs84.buffer(1e-10)))
    if not candidates:
        return None
    line = max(candidates, key=lambda candidate: candidate.length)
    return [[float(x), float(y)] for x, y in line.coords]


def recover_street_plan_centerline_wgs84(
    zone_wgs84: BaseGeometry,
) -> list[list[float]] | None:
    """Safely recover straight-street metadata for a locked legacy polygon."""

    if not isinstance(zone_wgs84, Polygon) or zone_wgs84.is_empty:
        return None
    metric_crs = local_metric_crs_for_polygon(zone_wgs84)
    to_metric = build_transformer("EPSG:4326", metric_crs)
    to_wgs84 = build_transformer(metric_crs, "EPSG:4326")
    centerline_m = _principal_street_centerline_m(project_geometry(zone_wgs84, to_metric))
    return _plan_centerline_coordinates(
        centerline_m,
        zone_wgs84,
        to_wgs84=to_wgs84,
    )


def validate_street_plan_centerline_wgs84(
    zone_wgs84: BaseGeometry,
    value: Any,
) -> bool:
    """Whether saved centreline metadata still describes this street polygon.

    ``plan_centerline`` is authored JSON, so validate both its wire shape and
    its metric relationship to the current polygon.  Containment alone is not
    enough: a stale short/crosswise line can remain inside a reshaped zone but
    no longer represent the street's longitudinal axis.
    """

    if (
        not isinstance(zone_wgs84, Polygon)
        or zone_wgs84.is_empty
        or not zone_wgs84.is_valid
        or not isinstance(value, (list, tuple))
        or len(value) < 2
    ):
        return False

    coordinates: list[tuple[float, float]] = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        try:
            longitude = float(point[0])
            latitude = float(point[1])
        except (TypeError, ValueError):
            return False
        if (
            isinstance(point[0], bool)
            or isinstance(point[1], bool)
            or not math.isfinite(longitude)
            or not math.isfinite(latitude)
            or not -180 <= longitude <= 180
            or not -90 <= latitude <= 90
        ):
            return False
        coordinates.append((longitude, latitude))

    try:
        centerline_wgs84 = LineString(coordinates)
    except (TypeError, ValueError):
        return False
    if (
        centerline_wgs84.is_empty
        or not centerline_wgs84.is_valid
        or not centerline_wgs84.is_simple
        or centerline_wgs84.length <= 0
    ):
        return False

    metric_crs = local_metric_crs_for_polygon(zone_wgs84)
    to_metric = build_transformer("EPSG:4326", metric_crs)
    zone_m = project_geometry(zone_wgs84, to_metric)
    centerline_m = project_geometry(centerline_wgs84, to_metric)

    # Generated endpoints lie on the boundary.  A 25 cm tolerance absorbs
    # WGS84/UTM round-trip drift without accepting a line from another zone.
    if not centerline_m.difference(zone_m.buffer(0.25)).is_empty:
        return False

    rectangle = zone_m.minimum_rotated_rectangle
    exterior = getattr(rectangle, "exterior", None)
    if exterior is None:
        return False
    rectangle_coordinates = list(exterior.coords)
    if len(rectangle_coordinates) < 5:
        return False
    longest_edge = max(
        (
            math.dist(rectangle_coordinates[index], rectangle_coordinates[index + 1]),
            rectangle_coordinates[index],
            rectangle_coordinates[index + 1],
        )
        for index in range(4)
    )
    long_axis, axis_start, axis_end = longest_edge
    if long_axis <= 0:
        return False
    axis_x = (axis_end[0] - axis_start[0]) / long_axis
    axis_y = (axis_end[1] - axis_start[1]) / long_axis
    projections = [coordinate[0] * axis_x + coordinate[1] * axis_y for coordinate in centerline_m.coords]
    if max(projections) - min(projections) < long_axis * 0.55:
        return False

    recovered_axis = _principal_street_centerline_m(zone_m)
    if recovered_axis is not None:
        short_axis = min(
            math.dist(rectangle_coordinates[index], rectangle_coordinates[index + 1]) for index in range(4)
        )
        alignment_tolerance_m = max(0.5, short_axis * 0.35)
        if not centerline_m.difference(recovered_axis.buffer(alignment_tolerance_m)).is_empty:
            return False

    return True


def _safe_plan_centerline_coordinates(
    zone_wgs84: Polygon,
    value: list[list[float]] | None,
) -> list[list[float]] | None:
    """Keep authored centreline metadata only when it describes this polygon.

    Ordered street subtraction can leave a valid road surface as a clipped
    wedge or short connector.  The source segment can still intersect that
    surface while no longer representing its longitudinal axis.  Persisting
    that stale chord poisons the otherwise-valid public-realm compile because
    the compiler correctly treats present metadata as authoritative.

    Prefer a conservative polygon-derived replacement when possible.  If the
    shape is not safely recoverable (roundabouts and tiny wedges commonly are
    not), omit the optional hint so the executable polygon recipe remains the
    source of truth.
    """

    if value is None or validate_street_plan_centerline_wgs84(zone_wgs84, value):
        return value
    recovered = recover_street_plan_centerline_wgs84(zone_wgs84)
    if recovered and validate_street_plan_centerline_wgs84(zone_wgs84, recovered):
        return recovered
    return None


def _stable_public_realm_polygons_wgs84(
    geometry_m: BaseGeometry,
    *,
    to_wgs84,
    to_metric,
    min_area_m2: float,
) -> list[Polygon]:
    """Project material metric pieces without creating degree-scale slivers.

    ``make_valid`` in WGS84 can split a shared 20 cm courtyard seam into one
    real polygon plus many numerically valid zero-area fragments.  Precision
    repair belongs in the local metric CRS where one millimetre has a stable
    meaning.  A bounded round-trip repair catches the rare projection that is
    valid in degrees but self-intersects after the assembly service measures
    it back in UTM.
    """

    def _metric_parts(value: BaseGeometry) -> list[Polygon]:
        repaired = make_valid(value)
        parts: list[Polygon] = []
        for polygon in iter_polygons(repaired):
            snapped = make_valid(set_precision(polygon, 1e-3))
            parts.extend(candidate for candidate in iter_polygons(snapped) if candidate.area >= min_area_m2)
        return parts

    projected: list[Polygon] = []
    for metric_polygon in _metric_parts(geometry_m):
        candidate_wgs84 = project_geometry(metric_polygon, to_wgs84)
        round_trip = project_geometry(candidate_wgs84, to_metric)
        if candidate_wgs84.is_valid and round_trip.is_valid:
            projected.append(candidate_wgs84)
            continue

        # Repair the round-trip in metres, then project each material part
        # once more.  Never run an unconditional degree-space make_valid here.
        for repaired_metric in _metric_parts(round_trip):
            repaired_wgs84 = project_geometry(repaired_metric, to_wgs84)
            verification = project_geometry(repaired_wgs84, to_metric)
            if repaired_wgs84.is_valid and verification.is_valid:
                projected.append(repaired_wgs84)
    return projected


def _lego_park_identity_for_metric_polygon(
    *,
    kind: str,
    archetype_id: str | None,
    geometry_m: BaseGeometry,
) -> tuple[str, str] | None:
    """Preserve the selected park identity regardless of kit availability.

    Geometry compatibility decides exact-kit versus family-pending fallback
    during Community 3D compilation. Re-homing here would silently replace
    the AI/user's catalogue choice before that truthful decision can occur.
    """

    return (kind, archetype_id) if archetype_id else None


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
                pieces.extend(geom for geom in getattr(hit, "geoms", []) if isinstance(geom, LineString))
        usable = [piece for piece in pieces if piece.length > 0.5]
        if usable:
            longest = max(
                usable,
                key=lambda piece: (piece.length, -piece.bounds[0], -piece.bounds[1]),
            )
            park_point = longest.interpolate(0.5, normalized=True)
        else:
            park_point, _street_point = nearest_points(boundary, segment.line)
        candidates.append(
            (
                role_priority.get(segment.role, 3),
                distance,
                park_point.x,
                park_point.y,
                park_point,
            )
        )

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
    "footway",
    "path",
    "pathway",
    "trail",
    "cycleway",
    "bikeway",
    "pedestrian",
    "multi-use",
    "multi use",
    "shared use",
)
_EXCLUDED_ROAD_CONTEXT_TERMS = (
    "railway",
    "rail line",
    "motorway",
    "freeway",
    "expressway",
    "controlled access",
    "skeletal road",
    "trunk",
    "off ramp",
    "on ramp",
    "slip road",
)


def _context_feature_text(feature: dict[str, Any]) -> str:
    props = feature.get("properties") or {}
    return " ".join(
        str(value).lower()
        for key, value in props.items()
        if value is not None
        and key
        in {
            "road_type",
            "highway",
            "centerline_type",
            "functional_class_code",
            "road_segment_type_description",
            "street_type",
            "asset_type",
            "asset_class",
            "bicycle_class",
            "type",
            "status",
            "built_status",
            # Calgary calls its limited-access freeway network "Skeletal Road".
            # Other municipal feeds expose the same distinction through one of
            # these generic classification fields.
            "ctp_class",
            "road_class",
            "classification",
            "functional_class",
            "transportation_class",
            "access",
            "junction",
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
    lifecycle = " ".join(str(props.get(key) or "").strip().lower() for key in ("built_status", "status", "plan_status"))
    if any(
        term in lifecycle
        for term in (
            "proposed",
            "planned",
            "future",
            "closed",
            "abandoned",
            "demolished",
        )
    ):
        return False
    if str(props.get("access") or "").strip().lower() in {
        "no",
        "private",
        "emergency",
        "permit",
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


def _derive_blocks(boundary_m: BaseGeometry, street_area: BaseGeometry | None) -> tuple[list[Polygon], float]:
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
        return "BLOCKS_FRAGMENTED"  # curve shattered buildable blocks into pocket-park chum
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
    building_count_target = (
        max(1, min(20, int(rule_hints["building_count_target"])))
        if isinstance((rule_hints or {}).get("building_count_target"), (int, float))
        and not isinstance((rule_hints or {}).get("building_count_target"), bool)
        else None
    )
    park_count_target = (
        max(1, min(8, int(rule_hints["park_count_target"])))
        if isinstance((rule_hints or {}).get("park_count_target"), (int, float))
        and not isinstance((rule_hints or {}).get("park_count_target"), bool)
        else None
    )
    if rule_overrides:
        # The refinement loop revises rule inputs; each override is recorded by
        # the loop itself as {parameter, from, to, reason}.
        valid_overrides = {k: v for k, v in rule_overrides.items() if hasattr(rules, k) and isinstance(v, (int, float))}
        rules = dataclass_replace(rules, **valid_overrides)
    result.notes.extend(rule_notes)

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

    # Executable street families own their native metric cross-sections. The
    # broad/Classic planner continues to honor expert ROW parameters exactly;
    # only a LEGO-authored palette normalizes its graph before subdivision.
    public_realm_variants = getattr(palette, "public_realm_variants", None) or {}
    public_realm_occurrences: dict[str, int] = {}
    if public_realm_variants:
        capability_catalog = build_public_realm_capability_catalog()
        spine_archetype_id = getattr(palette, "spine_archetype_id", None)
        local_archetype_id = getattr(palette, "local_archetype_id", None)
        spine_variant_id = public_realm_variants.get("spine")
        local_variant_id = public_realm_variants.get("local")
        spine_exact = spine_variant_id in capability_catalog.variants_by_archetype.get(
            spine_archetype_id or "",
            (),
        )
        local_exact = local_variant_id in capability_catalog.variants_by_archetype.get(
            local_archetype_id or "",
            (),
        )
        local_native_row_m = {
            "yield_street": 10.0,
            "narrow_residential_street": 14.0,
            "woonerf_shared_street": 10.0,
            "calgary_local": 16.0,
        }.get(local_archetype_id, 14.0)
        native_updates: dict[str, float] = {}
        if spine_exact:
            native_updates["spine_row_width_m"] = 18.0
        if local_exact:
            native_updates["local_row_width_m"] = local_native_row_m
        if native_updates:
            rules = dataclass_replace(rules, **native_updates)
            result.notes.append(
                {
                    "code": "PUBLIC_REALM_LEGO_NATIVE_STREET_WIDTHS",
                    "severity": "info",
                    "message": "Executable street roles set their reviewed native widths before graph generation.",
                    "source_phase": "street_graph",
                }
            )

    result.rules = {
        "block_target_m": rules.block_target_m,
        "row_width_m": rules.row_width_m,
        "clear_width_m": rules.clear_width_m,
        "open_space_share": rules.open_space_share,
        "coverage_ratio": rules.coverage_ratio,
        "floors": rules.floors,
        "floors_note": rules.floors_note,
        "spine_row_width_m": rules.spine_row_width_m,
        "local_row_width_m": rules.local_row_width_m,
        **({"building_count_target": building_count_target} if building_count_target else {}),
        **({"park_count_target": park_count_target} if park_count_target else {}),
    }
    seed = site_hash(boundary_m)

    # --- streets (or the locked network) --------------------------------------
    if locked_street_area_wgs84 is not None and not locked_street_area_wgs84.is_empty:
        network = StreetNetwork()
        network.street_area = make_valid(project_geometry(make_valid(locked_street_area_wgs84), to_metric))
        result.notes.append(
            {
                "code": "STREETS_LOCKED",
                "severity": "info",
                "message": "Street network locked by the user — regenerated blocks/massing only.",
                "source_phase": "street_graph",
            }
        )
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
        raw_paths = list(path_features or []) + [feature for feature in raw_roads if _is_path_context_feature(feature)]
        path_lines = _feature_lines_m(raw_paths, to_metric)
        entries = entry_points_from_roads(road_lines, boundary_m)
        path_entries = entry_points_from_paths(path_lines, boundary_m)
        # Straight baseline always generated — it is the fallback AND the
        # yardstick the curved candidates are judged against.
        network = generate_street_network(
            boundary_m,
            rules,
            entries,
            path_entry_points=path_entries,
            context_road_lines=road_lines,
            include_roundabouts=palette.automatic_roundabouts,
        )
        blocks, sliver_straight = _derive_blocks(boundary_m, network.street_area)
        if palette.curvilinear and network.segments:
            straight_network, straight_blocks = network, blocks
            n_straight_large = sum(1 for b in straight_blocks if b.area >= 2000.0)
            rejections: list[tuple[str, str]] = []
            applied = False
            for mode in ("all", "spine"):  # graduated: full vision, then bow, then straight
                candidate = generate_street_network(
                    boundary_m,
                    rules,
                    entries,
                    path_entry_points=path_entries,
                    context_road_lines=road_lines,
                    include_roundabouts=palette.automatic_roundabouts,
                    curve_mode=mode,
                    seed=seed,
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
                    rejected_suffix = "; rejected " + ", ".join(f"{m}:{r}" for m, r in rejections) if rejections else ""
                    network.notes.append(
                        {
                            "code": "CURVILINEAR_APPLIED",
                            "severity": "info",
                            "message": f"Streets follow a gentle curve toward the site's heart "
                            f"(mode={mode}{rejected_suffix}).",
                            "source_phase": "street_graph",
                        }
                    )
                    applied = True
                    break
                rejections.append((mode, reason))
            if not applied:
                # The guard is the SOLE curvature-note authority: exactly one
                # outcome note for a curvilinear palette on a viable site.
                guard_rejected = [r for r in rejections if r[1] not in ("AMPLITUDE_BELOW_MIN", "NO_LONG_AXIS_ROWS")]
                network, blocks = straight_network, straight_blocks
                if guard_rejected:
                    network.notes.append(
                        {
                            "code": "CURVILINEAR_FALLBACK",
                            "severity": "info",
                            "message": "Curved grid rejected ("
                            + "; ".join(f"{m}:{r}" for m, r in rejections)
                            + "); straight grid kept.",
                            "source_phase": "street_graph",
                        }
                    )
                elif rejections:
                    network.notes.append(
                        {
                            "code": "CURVILINEAR_SKIPPED",
                            "severity": "info",
                            "message": "Site too tight to curve the grid ("
                            + "; ".join(f"{m}:{r}" for m, r in rejections)
                            + ") — straight grid kept.",
                            "source_phase": "street_graph",
                        }
                    )
    result.notes.extend(network.notes)
    street_area = network.street_area if network.street_area is not None else Polygon()

    # --- open space + placement policy ------------------------------------------
    open_target = rules.open_space_share * gross
    open_plan = select_open_space(
        blocks=blocks,
        boundary_m=boundary_m,
        rules=rules,
        palette=palette,
        network=network,
        seed=seed,
        target_count=park_count_target,
    )
    open_spaces_m = [spec.geom_m for spec in open_plan.specs]
    open_area = open_plan.open_area_m2
    if open_area < open_target * 0.5 and len(blocks) > 1:
        result.notes.append(
            {
                "code": "OPEN_SPACE_SHORTFALL",
                "severity": "warning",
                "message": f"Open space {open_area:,.0f} m² is under half the "
                f"{open_target:,.0f} m² target — block sizes don't divide cleanly.",
                "source_phase": "civic_distribution",
            }
        )

    # Landscape structure per green kind (mirrored by the globe's parkScatter):
    # ponds are water, everything else plants to the palette's design intent.
    _LANDSCAPE_KEY = {"central": "park", "pocket": "pocket", "greenway": "greenway", "plaza": "plaza"}
    _PUBLIC_REALM_KEY = {
        "central": "central",
        "pocket": "pocket",
        "greenway": "greenway",
        "plaza": "plaza",
        "pond": "pond",
    }
    public_realm_variants = getattr(palette, "public_realm_variants", None) or {}
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
        for poly_m in iter_polygons(spec.geom_m):
            kind = spec.kind
            archetype_id = (
                (getattr(palette, "central_archetype_id", None) if kind == "central" else spec.archetype_id)
                or spec.archetype_id
                or _PARK_ARCHETYPE_FALLBACK.get(kind)
            )
            if public_realm_variants:
                identity = _lego_park_identity_for_metric_polygon(
                    kind=kind,
                    archetype_id=archetype_id,
                    geometry_m=poly_m,
                )
                if identity is None:
                    continue
                kind, archetype_id = identity
            color = PLAN_COLORS["water"] if kind == "pond" else PLAN_COLORS["green_space"]
            planting = palette.landscape.get(_LANDSCAPE_KEY.get(kind, ""))
            public_realm_role = _PUBLIC_REALM_KEY.get(kind, "")
            occurrence = public_realm_occurrences.get(public_realm_role, 0)
            variant_id = _public_realm_variant_for(palette, public_realm_role, occurrence)
            public_realm_occurrences[public_realm_role] = occurrence + 1
            poly = project_geometry(poly_m, to_wgs84)
            access_points = [project_geometry(point, to_wgs84) for point in _park_access_points_m(poly_m, network)]
            result.zones.append(
                {
                    "zone_type": "green_space",
                    "name": f"{scenario_label} · {spec.name_suffix}",
                    "coordinates": _ring(poly),
                    "color": color,
                    "sort_order": zone_sort,
                    "properties": {
                        "_plan_scenario": scenario_id,
                        "_imported_from": layer_name,
                        "_plan_role": "open_space",
                        "tree_density": tree_density,
                        "green_kind": kind,
                        **({"green_space_archetype_id": archetype_id} if archetype_id else {}),
                        **({"green_space_selected_variant_id": variant_id} if variant_id else {}),
                        **({"ground_texture": ground_texture} if ground_texture else {}),
                        **({"planting_structure": planting} if planting else {}),
                        **(
                            {
                                "park_access_points": [[float(point.x), float(point.y)] for point in access_points],
                            }
                            if access_points
                            else {}
                        ),
                    },
                }
            )
            zone_sort += 1

    emitted_park_count = sum(
        1
        for zone in result.zones
        if zone["zone_type"] == "green_space" and zone["properties"].get("_plan_role") == "open_space"
    )
    if park_count_target is not None and emitted_park_count != park_count_target:
        result.notes.append(
            {
                "code": "EXACT_PARK_COUNT_UNMET",
                "severity": "error",
                "message": (
                    f"The brief required exactly {park_count_target} public park polygons; "
                    f"the safe geometry could emit {emitted_park_count}."
                ),
                "source_phase": "civic_distribution",
            }
        )

    # --- parcels + masses on the developable blocks ------------------------------
    loop_blocks = [
        (index, open_plan.carved_blocks.get(index, block))
        for index, block in enumerate(blocks)
        if index not in open_plan.consumed_indices
    ]
    contexts = compute_block_contexts(
        blocks=loop_blocks,
        boundary_m=boundary_m,
        network=network,
        district_lookup=district_lookup,
        signature_green_m=open_plan.central_geom_m,
    )
    block_plans = plan_blocks(
        contexts=contexts,
        palette=palette,
        rules=rules,
        base_type=base_development_type,
        base_aesthetic=base_aesthetic,
        dna=dna,
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
        if (
            clamp
            and round(floors, 1) != plan.floors_target
            and plan_archetype_id not in palette.family_pending_archetype_ids
        ):
            ceiling_floors = max(1, int(float(floors)))
            supported_by_parent = None
            if palette.allowed_archetype_ids is not None:
                supported_by_parent = {
                    parent_id: tuple(
                        sorted(
                            {
                                supported_floor
                                for selectable_id in (
                                    parent_id,
                                    *palette.allowed_variant_ids_by_archetype.get(parent_id, ()),
                                )
                                for supported_floor in palette.supported_floors_by_selectable_id.get(selectable_id, ())
                                if supported_floor <= ceiling_floors
                            }
                        )
                    )
                    for parent_id in palette.allowed_archetype_ids
                }
                supported_by_parent = {parent_id: values for parent_id, values in supported_by_parent.items() if values}
            entry = resolve_building_archetype(
                plan.development_type,
                plan.aesthetic,
                ceiling_floors,
                prefer_family=palette.style_family,
                allowed_archetype_ids=(supported_by_parent.keys() if supported_by_parent is not None else None),
                supported_floors_by_archetype=supported_by_parent,
            )
            plan_archetype_id = entry["id"] if entry else None
            measured_entry = (measured_model_dims or {}).get(plan_archetype_id) if entry else None
            plan_variant_id = measured_entry.variant_id if measured_entry else None
            if entry and palette.allowed_archetype_ids is not None:
                preferred_selectable_id = (
                    plan.variant_id if entry["id"] == plan.archetype_id and plan.variant_id else entry["id"]
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
                    for supported_floor in palette.supported_floors_by_selectable_id.get(selectable_id, ())
                    if supported_floor <= ceiling_floors
                ]
                if candidates:
                    _, _, selectable_id, selected_floors = min(candidates)
                    floors = float(selected_floors)
                    plan_variant_id = selectable_id if selectable_id != entry["id"] else None
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
            result.zones.append(
                {
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
                }
            )
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
            mass_block,
            rules,
            typology=plan.typology,
            dims=TYPOLOGY_DIMS.get(plan.typology),
            target=target,
        )
        if mass is None:
            continue
        typology_used = (info or {}).get("typology", "perimeter_block")

        if lane is not None:
            lane_area_total += float(lane.area)
            projected_lanes = (
                _stable_public_realm_polygons_wgs84(
                    lane,
                    to_wgs84=to_wgs84,
                    to_metric=to_metric,
                    min_area_m2=1.0,
                )
                if public_realm_variants.get("lane")
                else list(iter_polygons(project_geometry(lane, to_wgs84)))
            )
            lane_centerline = _principal_street_centerline_m(lane)
            for wpoly in projected_lanes:
                plan_centerline = _plan_centerline_coordinates(
                    lane_centerline,
                    wpoly,
                    to_wgs84=to_wgs84,
                )
                result.zones.append(
                    {
                        "zone_type": "road",
                        "name": f"{scenario_label} · Block {index + 1} Lane",
                        "coordinates": _ring(wpoly),
                        "color": PLAN_COLORS["road"],
                        "sort_order": 490,
                        "properties": {
                            "_plan_scenario": scenario_id,
                            "_imported_from": layer_name,
                            "_plan_role": "street",
                            "width": LANE_ROW_M,
                            "street_role": "lane",
                            "road_archetype_id": "toronto_laneway",
                            **({"plan_centerline": plan_centerline} if plan_centerline else {}),
                            **(
                                {
                                    "road_selected_variant_id": public_realm_variants["lane"],
                                }
                                if public_realm_variants.get("lane")
                                else {}
                            ),
                        },
                    }
                )

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
                (o.development_type, o.aesthetic, o.archetype_id, o.variant_id) for o in plan.bar_options
            )

        mass_polys = list(iter_polygons(mass))
        if building_count_target is not None and len(loop_blocks) == 1:
            native_cells = (
                _pack_exact_target_cells(
                    mass_block,
                    building_count_target,
                    target,
                    setback_m=rules.front_setback_m,
                )
                if target is not None
                else None
            )
            mass_polys = native_cells or _exact_building_cells(mass_polys, building_count_target)
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
                if palette.allowed_archetype_ids is not None and target is not None and target.source == "runtime_lego":
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
                result.zones.append(
                    {
                        "zone_type": "building",
                        "name": f"{scenario_label} · Block {index + 1}{suffix}",
                        "coordinates": _ring(wpoly),
                        "color": PLAN_COLORS["building"],
                        "sort_order": zone_sort,
                        "properties": {
                            "_plan_scenario": scenario_id,
                            "_imported_from": layer_name,
                            "_plan_role": "building",
                            "floors": round(floors, 1),
                            "height": round(floors * FLOOR_HEIGHT_M, 1),
                            "development_type": dev_out,
                            "development_aesthetic": aes_out,
                            "_plan_band": plan.band,
                            **archetype_props,
                            **(info or {}),
                            **({"floors_clamped_by": clamp} if clamp else {}),
                        },
                    }
                )
                zone_sort += 1

        # The perimeter bars enclose a courtyard the mass ring left unbuilt —
        # draw it, or a single-block plan reads as one solid slab with no
        # visible open space. Visual zone only: NOT counted in open-space
        # metrics and NOT part of the frozen evaluator loop. Perimeter blocks
        # only: tower pads and row bars leave open ground, not a courtyard.
        if typology_used == "perimeter_block" and len(mass_polys) > 1:
            courtyard = make_valid(block.buffer(-rules.front_setback_m).difference(unary_union(mass_polys)))
            # Hole-free before drawing: a courtyard that wraps an interior bar
            # is a donut, and zone rings are exterior-only app-wide — drawn raw
            # it would fill the hole and paint green UNDER the buildings.
            courtyard = decompose_holed(courtyard, block)
            for cpoly in iter_polygons(courtyard):
                if cpoly.area < 150.0:
                    continue
                open_spaces_m.append(cpoly)
                if public_realm_variants:
                    projected_courtyards = _stable_public_realm_polygons_wgs84(
                        cpoly,
                        to_wgs84=to_wgs84,
                        to_metric=to_metric,
                        min_area_m2=64.0,
                    )
                else:
                    # Keep the established Classic serialization path inert.
                    projected_courtyards = list(iter_polygons(make_valid(project_geometry(cpoly, to_wgs84))))
                for wpoly in projected_courtyards:
                    metric_courtyard = project_geometry(wpoly, to_metric)
                    if public_realm_variants and not (
                        public_realm_park_archetype_supports_metric_geometry(
                            "urban_pocket_park",
                            metric_courtyard,
                        )
                    ):
                        # A sub-family ribbon is unprogrammed ground, not a
                        # fake park.  The residual landscape pass owns it.
                        continue
                    result.zones.append(
                        {
                            "zone_type": "green_space",
                            "name": f"{scenario_label} · Block {index + 1} courtyard",
                            "coordinates": _ring(wpoly),
                            "color": PLAN_COLORS["green_space"],
                            "sort_order": zone_sort,
                            "properties": {
                                "_plan_scenario": scenario_id,
                                "_imported_from": layer_name,
                                "_plan_role": "courtyard",
                                "tree_density": tree_density,
                                "green_space_archetype_id": "urban_pocket_park",
                                **(
                                    {
                                        "green_space_selected_variant_id": _public_realm_variant_for(
                                            palette,
                                            "courtyard",
                                            public_realm_occurrences.get("courtyard", 0),
                                        ),
                                    }
                                    if _public_realm_variant_for(
                                        palette,
                                        "courtyard",
                                        public_realm_occurrences.get("courtyard", 0),
                                    )
                                    else {}
                                ),
                                **(
                                    {"planting_structure": palette.landscape["courtyard"]}
                                    if palette.landscape.get("courtyard")
                                    else {}
                                ),
                            },
                        }
                    )
                    public_realm_occurrences["courtyard"] = public_realm_occurrences.get("courtyard", 0) + 1
                    zone_sort += 1

    if clamp_notes:
        result.notes.append(
            {
                "code": "FLOORS_CLAMPED",
                "severity": "info",
                "message": f"{clamp_notes} blocks clamped to their district height ceiling.",
                "source_phase": "building_placement",
            }
        )

    # --- street zones -------------------------------------------------------------
    _emit_street_zones(
        result=result,
        network=network,
        street_area=street_area,
        rules=rules,
        palette=palette,
        scenario_id=scenario_id,
        scenario_label=scenario_label,
        layer_name=layer_name,
        to_wgs84=to_wgs84,
        to_metric=to_metric,
    )

    # --- validation + metrics inputs -----------------------------------------------
    result.notes.extend(
        validate_plan(
            rules=rules,
            network=network,
            blocks_m=developable_blocks,
            parcels_by_block=parcels_by_block,
            masses_m=masses,
            open_spaces_m=open_spaces_m,
        )
    )

    # Lanes count as ROW: +lane on the street side, −lane on the block side is
    # an exact identity, so the land budget still closes.
    net_block_area = sum(b.area for b in developable_blocks) - lane_area_total
    result.geometry_inputs = {
        "site_area_m2": gross,
        "row_area_m2": (float(street_area.area) if not street_area.is_empty else 0.0) + lane_area_total,
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
    result.intersection_density_per_km2 = len(network.intersections) / (gross / 1_000_000) if gross else 0.0
    result.block_count = len(developable_blocks)
    result.parcel_count = sum(len(p) for p in parcels_by_block)
    result.building_count = sum(1 for z in result.zones if z["zone_type"] == "building")
    if building_count_target is not None and result.building_count != building_count_target:
        result.notes.append(
            {
                "code": "EXACT_BUILDING_COUNT_UNMET",
                "severity": "error",
                "message": (
                    f"The brief required exactly {building_count_target} building footprints; "
                    f"the safe geometry could emit {result.building_count}."
                ),
                "source_phase": "building_placement",
            }
        )
    result.blocks_m = developable_blocks
    result.masses_m = masses
    return result


def _public_realm_variant_for(palette, role: str, occurrence: int = 0) -> str | None:
    """Select a deterministic compatible appearance for one repeated role."""

    cycles = getattr(palette, "public_realm_variant_cycles", None) or {}
    cycle = tuple(cycles.get(role) or ())
    if cycle:
        return cycle[max(0, int(occurrence)) % len(cycle)]
    variants = getattr(palette, "public_realm_variants", None) or {}
    return variants.get(role)


def _default_road_archetype_id(role: str, width: float) -> str:
    """Persist the same measured street identity the frontend would infer.

    This covers locked networks and precision residue that have no source
    segment from which to inherit an explicit catalog identity.
    """

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
    poly_m,
    *,
    name: str,
    width: float,
    role: str,
    rules: RuleProfile,
    scenario_id: str,
    layer_name: str,
    to_wgs84,
    to_metric,
    archetype_id: str | None = None,
    variant_id: str | None = None,
    centerline_m: BaseGeometry | None = None,
    context_connection: bool = False,
    geometry_source: str | None = None,
) -> list[dict[str, Any]]:
    resolved_archetype_id = archetype_id or _default_road_archetype_id(role, width)
    zones = []
    resolved_archetype_id = archetype_id or _default_road_archetype_id(role, width)
    projected_polygons = (
        _stable_public_realm_polygons_wgs84(
            poly_m,
            to_wgs84=to_wgs84,
            to_metric=to_metric,
            min_area_m2=1.0,
        )
        if variant_id
        else list(iter_polygons(project_geometry(poly_m, to_wgs84)))
    )
    for wpoly in projected_polygons:
        plan_centerline = _safe_plan_centerline_coordinates(
            wpoly,
            _plan_centerline_coordinates(
                centerline_m,
                wpoly,
                to_wgs84=to_wgs84,
            ),
        )
        zones.append(
            {
                "zone_type": "road",
                "name": name,
                "coordinates": _ring(wpoly),
                "color": PLAN_COLORS["road"],
                "sort_order": 490,
                "properties": {
                    "_plan_scenario": scenario_id,
                    "_imported_from": layer_name,
                    "_plan_role": "street",
                    "width": width,
                    "clear_width_m": width if role == "path" else rules.clear_width_m,
                    "street_role": role,
                    **({"plan_centerline": plan_centerline} if plan_centerline else {}),
                    **({"_plan_street_geometry_source": geometry_source} if geometry_source else {}),
                    **({"context_connection": True} if context_connection else {}),
                    "road_archetype_id": resolved_archetype_id,
                    **({"road_selected_variant_id": variant_id} if variant_id else {}),
                },
            }
        )
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
    to_metric,
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

    public_realm_variants = getattr(palette, "public_realm_variants", None) or {}

    if street_area.is_empty:
        return
    if not network.segments:
        public_realm_catalog = build_public_realm_capability_catalog() if public_realm_variants else None
        locked_occurrence = 0
        for poly in iter_polygons(street_area):
            pieces = iter_polygons(decompose_holed(poly, poly)) if poly.interiors else [poly]
            for piece in pieces:
                if public_realm_variants:
                    candidates = (
                        (
                            "local",
                            getattr(palette, "local_archetype_id", None),
                            _public_realm_variant_for(palette, "local", locked_occurrence),
                            rules.local_row_width_m,
                        ),
                        (
                            "spine",
                            getattr(palette, "spine_archetype_id", None),
                            _public_realm_variant_for(palette, "spine", locked_occurrence),
                            rules.spine_row_width_m,
                        ),
                    )
                    compatible_identities = []
                    for role, archetype_id, variant_id, native_width in candidates:
                        if not archetype_id or not variant_id:
                            continue
                        recipe = plan_public_realm_metric_street_recipe(
                            archetype_id,
                            piece,
                            variant_id=variant_id,
                            declared_width_m=native_width,
                            catalog=public_realm_catalog,
                        )
                        if recipe is not None:
                            compatible_identities.append(
                                (
                                    role,
                                    archetype_id,
                                    variant_id,
                                    float(recipe.target.row_width_m),
                                    abs(float(recipe.target.row_width_m) - float(native_width)),
                                )
                            )
                    if not compatible_identities:
                        # Preserve the authored local character as a truthful
                        # family-pending section when no exact kit fits.
                        role = "local"
                        archetype_id = getattr(palette, "local_archetype_id", None)
                        variant_id = _public_realm_variant_for(palette, "local", locked_occurrence)
                        emitted_width = rules.local_row_width_m
                    # Compatibility envelopes may overlap (the Calgary local
                    # section reaches the exact 18 m main-street width).  Pick
                    # the role whose native section best matches the measured
                    # polygon instead of allowing tuple order to reclassify it.
                    else:
                        (
                            role,
                            archetype_id,
                            variant_id,
                            emitted_width,
                            _native_width_delta,
                        ) = min(
                            compatible_identities,
                            key=lambda identity: (
                                identity[4],
                                0 if identity[0] == "spine" else 1,
                            ),
                        )
                else:
                    role = "local"
                    archetype_id = None
                    variant_id = None
                    emitted_width = rules.row_width_m
                result.zones.extend(
                    _street_zone(
                        piece,
                        name=f"{scenario_label} · Street",
                        width=emitted_width,
                        role=role,
                        rules=rules,
                        scenario_id=scenario_id,
                        layer_name=layer_name,
                        to_wgs84=to_wgs84,
                        to_metric=to_metric,
                        archetype_id=archetype_id,
                        variant_id=variant_id,
                        centerline_m=_principal_street_centerline_m(piece),
                        geometry_source=("locked_area" if public_realm_variants else None),
                    )
                )
                locked_occurrence += 1
        return

    remaining = _snap(street_area)
    for n, (point, radius) in enumerate(network.roundabouts, start=1):
        piece = make_valid(_snap(point.buffer(radius, quad_segs=8)).intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        result.zones.extend(
            _street_zone(
                piece,
                name=f"{scenario_label} · Roundabout {n}",
                width=rules.spine_row_width_m,
                role="roundabout",
                rules=rules,
                scenario_id=scenario_id,
                layer_name=layer_name,
                to_wgs84=to_wgs84,
                to_metric=to_metric,
                archetype_id="roundabout",
                variant_id=public_realm_variants.get("roundabout"),
            )
        )

    spine_segments = [s for s in network.segments if s.role == "spine"]
    for spine_index, segment in enumerate(spine_segments):
        band = _snap(segment.line.buffer(segment.row_width_m / 2, cap_style=2, join_style=2))
        piece = make_valid(band.intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        result.zones.extend(
            _street_zone(
                piece,
                name=f"{scenario_label} · Main Street",
                width=segment.row_width_m,
                role="spine",
                rules=rules,
                scenario_id=scenario_id,
                layer_name=layer_name,
                to_wgs84=to_wgs84,
                to_metric=to_metric,
                archetype_id=getattr(palette, "spine_archetype_id", None),
                variant_id=_public_realm_variant_for(palette, "spine", spine_index),
                centerline_m=segment.line,
            )
        )

    path_counter = 0
    for segment in (s for s in network.segments if s.role == "path"):
        band = _snap(segment.line.buffer(segment.row_width_m / 2, cap_style=2, join_style=2))
        piece = make_valid(band.intersection(remaining))
        if piece.is_empty:
            continue
        remaining = make_valid(remaining.difference(piece))
        path_counter += 1
        result.zones.extend(
            _street_zone(
                piece,
                name=f"{scenario_label} · Path Connection {path_counter}",
                width=segment.row_width_m,
                role="path",
                rules=rules,
                scenario_id=scenario_id,
                layer_name=layer_name,
                to_wgs84=to_wgs84,
                to_metric=to_metric,
                archetype_id="multi_use_trail",
                context_connection=True,
                variant_id=_public_realm_variant_for(palette, "path", path_counter - 1),
                centerline_m=segment.line,
            )
        )

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
            if segment.context_connection
            else f"{scenario_label} · Street {counter}"
        )
        result.zones.extend(
            _street_zone(
                piece,
                name=segment_name,
                width=segment.row_width_m,
                role="local",
                rules=rules,
                scenario_id=scenario_id,
                layer_name=layer_name,
                to_wgs84=to_wgs84,
                to_metric=to_metric,
                archetype_id=archetype,
                context_connection=segment.context_connection,
                variant_id=_public_realm_variant_for(palette, "local", counter - 1),
                centerline_m=segment.line,
            )
        )

    # Numerical crumbs from the subtractions (shouldn't happen, but never
    # silently drop street land — the budget is measured against street_area).
    # Residue inherits the palette's local archetype so scenario street
    # invariants (e.g. environmental all-woonerf) hold on every road zone.
    for poly in iter_polygons(make_valid(remaining)):
        if poly.area < 1.0:
            continue
        counter += 1
        result.zones.extend(
            _street_zone(
                poly,
                name=f"{scenario_label} · Street {counter}",
                width=rules.local_row_width_m,
                role="local",
                rules=rules,
                scenario_id=scenario_id,
                layer_name=layer_name,
                to_wgs84=to_wgs84,
                to_metric=to_metric,
                archetype_id=local_archetype,
                variant_id=_public_realm_variant_for(palette, "local", counter - 1),
            )
        )
