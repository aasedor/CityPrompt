"""Street graph — an oriented internal grid connected to the real frontage streets.

All math in the site-local metric CRS. The grid orientation follows the site's
minimum rotated rectangle; the grid phase is shifted so a line passes through
the first street entry point (where the surrounding network meets the boundary),
and remaining entries are checked in validation rather than silently ignored.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.community_rules import RuleProfile

logger = logging.getLogger(__name__)

MIN_SEGMENT_M = 40.0     # drop grid stubs shorter than this
ENTRY_SNAP_MAX_M = 60.0  # an entry further than this from any gridline is "unserved"


@dataclass
class StreetNetwork:
    centerlines: list[LineString] = field(default_factory=list)
    street_area: BaseGeometry | None = None       # unioned ROW polygons (metric)
    intersections: list[Point] = field(default_factory=list)
    entries_served: int = 0
    entries_total: int = 0
    notes: list[dict[str, Any]] = field(default_factory=list)


def _grid_angle_deg(boundary_m: Polygon) -> float:
    """Orientation of the longest edge of the minimum rotated rectangle."""
    rect = boundary_m.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    best_len, best_angle = 0.0, 0.0
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if length > best_len:
            best_len = length
            best_angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return best_angle


def entry_points_from_roads(
    road_lines_m: list[LineString], boundary_m: Polygon, limit: int = 8
) -> list[Point]:
    """Where surrounding street centrelines cross the site boundary."""
    entries: list[Point] = []
    exterior = boundary_m.exterior
    for line in road_lines_m:
        try:
            crossing = line.intersection(exterior)
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001 — municipal geometry
            continue
        if crossing.is_empty:
            continue
        points = [crossing] if isinstance(crossing, Point) else list(getattr(crossing, "geoms", []))
        for point in points:
            if isinstance(point, Point):
                entries.append(point)
    # De-duplicate near-coincident entries (parallel carriageways etc.)
    deduped: list[Point] = []
    for point in entries:
        if all(point.distance(existing) > 20.0 for existing in deduped):
            deduped.append(point)
        if len(deduped) >= limit:
            break
    return deduped


def generate_street_network(
    boundary_m: Polygon,
    rules: RuleProfile,
    entry_points: list[Point] | None = None,
) -> StreetNetwork:
    network = StreetNetwork(entries_total=len(entry_points or []))
    boundary_m = make_valid(boundary_m)
    inset = boundary_m.buffer(-rules.perimeter_inset_m)
    if inset.is_empty:
        network.notes.append({
            "code": "SITE_TOO_SMALL", "severity": "warning",
            "message": "Site too small for an internal street grid — single-block plan.",
            "source_phase": "street_graph",
        })
        network.street_area = Polygon()
        return network

    angle = _grid_angle_deg(boundary_m)
    origin = boundary_m.centroid
    # Work in a rotated frame where the grid is axis-aligned.
    work = affinity.rotate(inset, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds
    spacing = rules.block_target_m + rules.row_width_m

    # Distribute lines EVENLY across each span (n = floor(span/spacing)):
    # edge-anchored spacing leaves an oversized orphan block whenever the span
    # isn't a clean multiple of the spacing (observed: a 501 m block on a
    # 340 m-deep site). Then shift the nearest line onto the first entry point
    # per axis so the internal grid meets the surrounding network.
    xs = _even_positions(minx, maxx, spacing)
    ys = _even_positions(miny, maxy, spacing)

    entries_work = [affinity.rotate(p, -angle, origin=origin) for p in (entry_points or [])]
    if entries_work:
        first = entries_work[0]
        xs = _snap_nearest(xs, first.x, spacing / 3)
        ys = _snap_nearest(ys, first.y, spacing / 3)

    lines_work: list[LineString] = []
    for x in xs:
        lines_work.append(LineString([(x, miny - spacing), (x, maxy + spacing)]))
    for y in ys:
        lines_work.append(LineString([(minx - spacing, y), (maxx + spacing, y)]))

    served = 0
    for entry in entries_work:
        near_x = any(abs(entry.x - x) <= ENTRY_SNAP_MAX_M for x in xs)
        near_y = any(abs(entry.y - y) <= ENTRY_SNAP_MAX_M for y in ys)
        if near_x or near_y:
            served += 1
    network.entries_served = served
    if network.entries_total and served < network.entries_total:
        network.notes.append({
            "code": "ENTRIES_UNSERVED", "severity": "info",
            "message": f"{network.entries_total - served} of {network.entries_total} street entry "
                       "points are more than 60 m from an internal street.",
            "source_phase": "street_graph",
        })

    # Record in-boundary centerlines (stub-filtered) but buffer the FULL-SPAN
    # lines: a street clipped short of the boundary leaves a land strip at its
    # end and the blocks never sever (observed: one connected block with slits).
    boundary_work = affinity.rotate(boundary_m, -angle, origin=origin)
    full_span_kept: list[LineString] = []
    for line in lines_work:
        clipped = line.intersection(boundary_work)
        pieces = [clipped] if isinstance(clipped, LineString) else list(getattr(clipped, "geoms", []))
        kept_any = False
        for piece in pieces:
            if isinstance(piece, LineString) and piece.length >= MIN_SEGMENT_M:
                network.centerlines.append(affinity.rotate(piece, angle, origin=origin))
                kept_any = True
        if kept_any:
            full_span_kept.append(affinity.rotate(line, angle, origin=origin))

    if not network.centerlines:
        network.notes.append({
            "code": "NO_INTERNAL_STREETS", "severity": "info",
            "message": "Block spacing exceeds site dimensions — no internal streets generated.",
            "source_phase": "street_graph",
        })
        network.street_area = Polygon()
        return network

    # Buffer per line THEN union: buffering a merged multiline leaves hairline
    # bridges at the crossings (zero-area slivers) that keep the blocks
    # topologically CONNECTED after the difference — observed as "one block
    # with slits". Per-line bands unioned sever cleanly.
    bands = [
        line.buffer(rules.row_width_m / 2, cap_style=2, join_style=2)
        for line in full_span_kept
    ]
    network.street_area = make_valid(unary_union(bands)).intersection(boundary_m)

    # Intersections: pairwise centerline crossings (grid nodes).
    seen: list[Point] = []
    for i, a in enumerate(network.centerlines):
        for b in network.centerlines[i + 1:]:
            crossing = a.intersection(b)
            if isinstance(crossing, Point) and all(crossing.distance(s) > 1.0 for s in seen):
                seen.append(crossing)
    network.intersections = seen
    return network


def _even_positions(low: float, high: float, spacing: float) -> list[float]:
    span = high - low
    count = int(span // spacing)
    if count < 1:
        return []
    return [low + span * (i + 1) / (count + 1) for i in range(count)]


def _snap_nearest(positions: list[float], target: float, max_shift: float) -> list[float]:
    if not positions:
        return positions
    index = min(range(len(positions)), key=lambda i: abs(positions[i] - target))
    if abs(positions[index] - target) <= max_shift:
        shifted = list(positions)
        shifted[index] = target
        return shifted
    return positions
