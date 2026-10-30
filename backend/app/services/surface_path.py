"""Source attestation for the finite, flat pathway adapters, not motor roads."""

import json
import math
from functools import lru_cache
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from app.services.site_engine import WGS84_CRS, build_transformer, local_metric_crs_for_polygon, project_geometry
from app.services.street_route_policy import native_street_max_length

SURFACE_PATH_WIDTHS = {
    "garden_gravel_path_v1": 1.5,
    "concrete_neighbourhood_walk_v1": 1.8,
    "brick_courtyard_path_v1": 2.0,
    "timber_garden_walk_v1": 2.0,
    "asphalt_shared_path_v1": 3.0,
    "standalone_narrow_sidewalk_v1": 1.5,
    "standalone_neighbourhood_sidewalk_v1": 2.0,
    "standalone_urban_sidewalk_v1": 3.0,
}


@lru_cache(maxsize=1)
def _path_sources():
    rows = json.loads(
        (Path(__file__).resolve().parents[1] / "data/nativeStreetPilots.json").read_text(encoding="utf-8")
    )
    return {row["id"]: row for row in rows if row["id"] in SURFACE_PATH_WIDTHS}


def surface_path_width(properties):
    variant = properties.get("road_selected_variant_id")
    if not isinstance(variant, str) or variant not in SURFACE_PATH_WIDTHS:
        return None
    row = _path_sources()[variant]
    width = properties.get("width")
    if (
        row.get("program", {}).get("adapter") != "narrow-pathway-v1"
        or properties.get("road_archetype_id") != row["sourceArchetypeId"]
        or isinstance(width, bool)
        or not isinstance(width, (int, float))
        or width != SURFACE_PATH_WIDTHS[variant]
        or width != row["widthM"]
        or properties.get("lane_count", 0) != 0
    ):
        raise ValueError("Pathway source must retain its exact design, clear width and zero motor lanes")
    return float(width)


def surface_path_centerline_metric(geometry_wgs84, properties):
    """Preserve bends, crossings and retraces, but prove their actual footprint.

    Zone coordinates retain an exterior plot ring; the route owns the walking
    surface and any enclosed lawn holes. Old paired miter footprints remain
    readable alongside new round joins. Neither format attests a different width.
    """
    width = surface_path_width(properties)
    if width is None:
        return None
    points = properties.get("plan_centerline")
    if not isinstance(points, (list, tuple)) or not 2 <= len(points) <= 4096:
        raise ValueError("Pathway needs a saved route with 2 to 4096 stations")
    if any(
        not isinstance(point, (list, tuple))
        or len(point) != 2
        or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in point)
        or not -180 <= point[0] <= 180
        or not -89 <= point[1] <= 89
        for point in points
    ):
        raise ValueError("Pathway route contains an invalid coordinate")
    if not isinstance(geometry_wgs84, Polygon) or geometry_wgs84.is_empty or not geometry_wgs84.is_valid:
        raise ValueError("Pathway needs a valid saved footprint")
    transformer = build_transformer(WGS84_CRS, local_metric_crs_for_polygon(geometry_wgs84))
    line = project_geometry(LineString(points), transformer)
    geometry = project_geometry(geometry_wgs84, transformer)
    if (
        not line.is_valid
        or not 0.05 < line.length <= native_street_max_length(properties["road_selected_variant_id"]) + 0.05
    ):
        raise ValueError("Pathway route has an unsupported length")
    # Local editor metres and UTM differ slightly; allow 15 cm, never an
    # arbitrary contained centreline in a much wider or unrelated plot.
    stations = list(line.coords)
    # Match the editor's union exactly: full interior discs can extend beyond
    # an endpoint when the first/last authored segment is shorter than half-width.
    corridors = [
        unary_union(
            [LineString([a, b]).buffer(width / 2, cap_style=2) for a, b in zip(stations, stations[1:])]
            + [Point(point).buffer(width / 2, quad_segs=6) for point in stations[1:-1]]
        ),
        # Existing saved routes may still use a bounded miter strip.
        line.buffer(width / 2, cap_style=2, join_style=2, mitre_limit=4, quad_segs=6),
    ]
    for corridor in corridors:
        if not isinstance(corridor, Polygon):
            continue
        for expected in (corridor, Polygon(corridor.exterior)):
            if expected.buffer(0.15).covers(geometry) and geometry.buffer(0.15).covers(expected):
                return line
    raise ValueError("Pathway footprint does not match its saved route and clear width")
