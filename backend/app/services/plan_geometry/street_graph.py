"""Street graph — an oriented internal grid connected to the real frontage streets.

All math in the site-local metric CRS. The grid orientation follows the site's
minimum rotated rectangle; the grid phase is shifted so a line passes through
the first street entry point (where the surrounding network meets the boundary),
then explicit connector stubs join every other feasible road or pathway anchor.
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
from shapely.ops import nearest_points, unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.community_rules import RuleProfile

logger = logging.getLogger(__name__)

MIN_SEGMENT_M = 40.0     # drop grid stubs shorter than this
ENTRY_CONNECTOR_MAX_M = 90.0
CONNECTION_EPSILON_M = 0.05
ROAD_FRONTAGE_PROXIMITY_M = 32.0
PATH_FRONTAGE_PROXIMITY_M = 24.0
PATH_CONNECTOR_WIDTH_M = 4.0

# --- curvilinear grid ---------------------------------------------------------
CURVE_STEP_M = 8.0                 # densification step along a bowed line
CURVE_AMPLITUDE_MIN_M = 8.0        # below this the curve isn't worth drawing
CURVE_AMPLITUDE_ABS_MAX_M = 45.0
CRESCENT_SAGITTA_MIN_M = 6.0       # emission-side crescent qualification
CURVE_MARGIN_MIN_M = 24.0          # minimum edge-band depth before curving at all
BLOCK_EDGE_MAX_M = 220.0           # frozen evaluator block_scale bound (plan_evaluator)

# Closed-form maximum of |sin(pi t) + 0.15 sin(2 pi t)| on [0,1]: stationary
# cos(pi t) = c solves 0.6 c^2 + c - 0.3 = 0. Normalizing by this makes the
# bow's sagitta EXACTLY the requested amplitude (both harmonic signs share the
# same max by the t -> 1-t symmetry).
_BOW_C = (math.sqrt(1.72) - 1.0) / 1.2
BOW_PROFILE_MAX = math.sqrt(1.0 - _BOW_C * _BOW_C) * (1.0 + 0.3 * _BOW_C)


@dataclass
class StreetSegment:
    """One full-span grid line with its own ROW width (spine vs local)."""
    line: LineString              # metric, full-span (unclipped, like full_span_kept)
    row_width_m: float
    role: str                     # "spine" | "local" | "path"
    sagitta_m: float = 0.0        # max chord deviation of the full-span line
    context_connection: bool = False


@dataclass
class StreetNetwork:
    centerlines: list[LineString] = field(default_factory=list)
    street_area: BaseGeometry | None = None       # unioned ROW polygons (metric)
    intersections: list[Point] = field(default_factory=list)
    segments: list[StreetSegment] = field(default_factory=list)
    roundabouts: list[tuple[Point, float]] = field(default_factory=list)  # (center, radius)
    entries_served: int = 0
    entries_total: int = 0
    path_entries_served: int = 0
    path_entries_total: int = 0
    notes: list[dict[str, Any]] = field(default_factory=list)
    curve_mode: str = "none"           # "none" | "spine" | "all" ACTUALLY applied
    curve_skip_reason: str | None = None  # set when a requested curve self-skipped


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


def _entry_points_from_context_lines(
    lines_m: list[LineString],
    boundary_m: Polygon,
    *,
    proximity_m: float,
    limit: int,
    dedupe_m: float,
) -> list[Point]:
    """Return deterministic boundary anchors for crossing or fronting lines.

    A parcel boundary normally stops at the curb, so the real street/path
    centreline often runs parallel 8-20 m outside it and never intersects the
    boundary.  For those lines, intersect a metric proximity band with the
    boundary and use the midpoint of the longest shared frontage.  Exact
    crossings are ranked first, followed by the nearest frontages.
    """
    candidates: list[tuple[int, float, float, float, Point]] = []
    exterior = boundary_m.exterior
    for line in lines_m:
        try:
            crossing = line.intersection(exterior)
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001 — municipal geometry
            continue
        points = [crossing] if isinstance(crossing, Point) else [
            geom for geom in getattr(crossing, "geoms", []) if isinstance(geom, Point)
        ]
        for point in points:
            candidates.append((0, 0.0, point.x, point.y, point))

        if points or line.distance(exterior) > proximity_m:
            continue
        try:
            proximity_band = line.buffer(proximity_m, cap_style=2, join_style=2)
            # Intersect individual boundary edges so a shared frontage that
            # turns a corner cannot become one L-shaped LineString whose
            # midpoint is biased toward the side leg.
            edge_frontages: list[LineString] = []
            boundary_coords = list(exterior.coords)
            for start, end in zip(boundary_coords[:-1], boundary_coords[1:]):
                edge_hit = LineString([start, end]).intersection(proximity_band)
                if isinstance(edge_hit, LineString):
                    edge_frontages.append(edge_hit)
                else:
                    edge_frontages.extend(
                        geom for geom in getattr(edge_hit, "geoms", [])
                        if isinstance(geom, LineString)
                    )
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001 — municipal geometry
            continue
        pieces = [piece for piece in edge_frontages if piece.length > 0.1]
        if not pieces:
            # A near-tangent may collapse the band intersection to a point.
            boundary_point, _line_point = nearest_points(exterior, line)
            candidates.append((1, line.distance(exterior), boundary_point.x,
                               boundary_point.y, boundary_point))
            continue
        longest = max(pieces, key=lambda piece: (piece.length, -piece.bounds[0], -piece.bounds[1]))
        point = longest.interpolate(0.5, normalized=True)
        candidates.append((1, line.distance(exterior), point.x, point.y, point))

    # Exact crossings before nearby frontages; stable coordinate tie-breaks
    # make cached redraws byte-identical even when source feature order changes.
    candidates.sort(key=lambda item: item[:4])
    deduped: list[Point] = []
    for _kind, _distance, _x, _y, point in candidates:
        if all(point.distance(existing) > dedupe_m for existing in deduped):
            deduped.append(point)
        if len(deduped) >= limit:
            break
    return deduped


def entry_points_from_roads(
    road_lines_m: list[LineString], boundary_m: Polygon, limit: int = 8
) -> list[Point]:
    """Road access anchors at crossings and adjacent street frontages."""
    return _entry_points_from_context_lines(
        road_lines_m, boundary_m,
        proximity_m=ROAD_FRONTAGE_PROXIMITY_M, limit=limit, dedupe_m=20.0,
    )


def entry_points_from_paths(
    path_lines_m: list[LineString], boundary_m: Polygon, limit: int = 8
) -> list[Point]:
    """Pedestrian/cycle anchors at crossings and adjacent pathway frontages."""
    return _entry_points_from_context_lines(
        path_lines_m, boundary_m,
        proximity_m=PATH_FRONTAGE_PROXIMITY_M, limit=limit, dedupe_m=12.0,
    )


def generate_street_network(
    boundary_m: Polygon,
    rules: RuleProfile,
    entry_points: list[Point] | None = None,
    *,
    path_entry_points: list[Point] | None = None,
    curve_mode: str = "none",
    seed: int = 0,
) -> StreetNetwork:
    """curve_mode="none" is byte-identical to the historic straight grid. "spine"
    bows only the main street; "all" translates the same bow to every long-axis
    row (exact spacing between interior rows). A requested curve that fails its
    feasibility caps returns a cheap sentinel network (curve_mode="none" +
    curve_skip_reason) WITHOUT paying for generation — the generator's guard
    owns all curvature notes."""
    network = StreetNetwork(
        entries_total=len(entry_points or []),
        path_entries_total=len(path_entry_points or []),
    )
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
    spacing = rules.block_target_m + rules.local_row_width_m
    max_block = getattr(rules, "max_block_edge_m", 0.0) or 0.0

    # Distribute lines EVENLY across each span, choosing the block count from
    # the preferred spacing but then raising it until no resulting block edge
    # exceeds max_block_edge_m. This is what makes a site SMALLER than one
    # target block still subdivide (the historic single-megablock bug: a
    # 156 m site with a 200 m target produced zero internal streets and one
    # giant perimeter ring). Then shift the nearest line onto the first entry
    # point per axis so the internal grid meets the surrounding network.
    xs = _axis_positions(minx, maxx, spacing, max_block)
    ys = _axis_positions(miny, maxy, spacing, max_block)

    entries_work = [affinity.rotate(p, -angle, origin=origin) for p in (entry_points or [])]
    snapped_y: float | None = None
    if entries_work:
        first = entries_work[0]
        xs, _ = _snap_nearest(xs, first.x, spacing / 3)
        ys, snapped_y = _snap_nearest(ys, first.y, spacing / 3)

    # --- curve feasibility (cheap, BEFORE any heavy geometry) -----------------
    requested_mode = curve_mode if curve_mode in ("spine", "all") else "none"
    amplitude = 0.0
    if requested_mode != "none":
        if not ys:
            # Skinny site: the long axis has no interior rows to bow.
            network.curve_skip_reason = "NO_LONG_AXIS_ROWS"
            requested_mode = "none"
        else:
            amplitude = _curve_amplitude(requested_mode, ys, work.bounds, spacing)
            if amplitude <= 0.0:
                network.curve_skip_reason = "AMPLITUDE_BELOW_MIN"
                requested_mode = "none"
        if requested_mode == "none" and curve_mode in ("spine", "all"):
            # Sentinel: the guard discards this candidate; don't pay for
            # clipping/buffering/intersections it will never use.
            return network
    direction = 1.0 if (seed >> 1) & 1 else -1.0
    w2_sign = 1.0 if (seed >> 3) & 1 else -1.0

    # Entry-snap exemption: the row that was snapped onto the first entry stays
    # straight when the entry sits mid-span — a bow would carry the street up to
    # the full amplitude away from the very road it was snapped to meet.
    exempt_ys: set[float] = set()
    if requested_mode != "none" and snapped_y is not None and entries_work:
        t_entry = (entries_work[0].x - minx) / max(maxx - minx, 1e-9)
        if 0.05 < t_entry < 0.95:
            exempt_ys.add(snapped_y)

    # Exactly one spine: the long-axis line nearest the site centroid (the
    # rotation origin maps to itself in the work frame). Long-axis lines are
    # the horizontals (grid angle follows the longest MRR edge = x axis), so
    # prefer a y-position; skinny sites with no interior y fall back to x.
    spine_y = min(ys, key=lambda y: (abs(y - origin.y), y)) if ys else None
    spine_x = None
    if spine_y is None and xs:
        spine_x = min(xs, key=lambda x: (abs(x - origin.x), x))

    lines_work: list[tuple[LineString, str, bool]] = []
    for x in xs:
        role = "spine" if spine_x is not None and x == spine_x else "local"
        lines_work.append((LineString([(x, miny - spacing), (x, maxy + spacing)]), role, False))
    for y in ys:
        role = "spine" if spine_y is not None and y == spine_y else "local"
        bow = (
            requested_mode == "all"
            or (requested_mode == "spine" and spine_y is not None and y == spine_y)
        ) and y not in exempt_ys
        if bow:
            line = _bow_curve(y, minx - spacing, maxx + spacing, minx, maxx,
                              amplitude, direction, w2_sign)
        else:
            line = LineString([(minx - spacing, y), (maxx + spacing, y)])
        lines_work.append((line, role, bow))

    # Record in-boundary centerlines (stub-filtered) but buffer the FULL-SPAN
    # lines: a street clipped short of the boundary leaves a land strip at its
    # end and the blocks never sever (observed: one connected block with slits).
    boundary_work = affinity.rotate(boundary_m, -angle, origin=origin)
    full_span_kept: list[StreetSegment] = []
    bowed_kept = False
    for line, role, bow in lines_work:
        clipped = line.intersection(boundary_work)
        pieces = [clipped] if isinstance(clipped, LineString) else list(getattr(clipped, "geoms", []))
        kept_any = False
        for piece in pieces:
            if isinstance(piece, LineString) and piece.length >= MIN_SEGMENT_M:
                network.centerlines.append(affinity.rotate(piece, angle, origin=origin))
                kept_any = True
        if kept_any:
            bowed_kept = bowed_kept or bow
            width = rules.spine_row_width_m if role == "spine" else rules.local_row_width_m
            # The full-span line is stored VERBATIM — emission re-buffers this
            # exact object and roundabout candidacy measures distance to it.
            # Never simplify or re-densify between here and emission.
            full_span_kept.append(StreetSegment(
                line=affinity.rotate(line, angle, origin=origin),
                row_width_m=width, role=role,
                sagitta_m=_line_sagitta(line) if bow else 0.0,
            ))
    road_connectors = 0
    path_connectors = 0
    if network.centerlines:
        road_connectors = _append_context_connectors(
            boundary_m=boundary_m,
            entries=entry_points or [],
            role="local",
            width_m=rules.local_row_width_m,
            centerlines=network.centerlines,
            segments=full_span_kept,
        )
        path_connectors = _append_context_connectors(
            boundary_m=boundary_m,
            entries=path_entry_points or [],
            role="path",
            width_m=PATH_CONNECTOR_WIDTH_M,
            centerlines=network.centerlines,
            segments=full_span_kept,
        )
    network.segments = full_span_kept
    if bowed_kept:
        network.curve_mode = requested_mode

    if not network.centerlines:
        network.notes.append({
            "code": "NO_INTERNAL_STREETS", "severity": "info",
            "message": "Block spacing exceeds site dimensions — no internal streets generated.",
            "source_phase": "street_graph",
        })
        network.street_area = Polygon()
        return network

    connected_lines = unary_union(network.centerlines)
    network.entries_served = sum(
        1 for entry in (entry_points or [])
        if entry.distance(connected_lines) <= CONNECTION_EPSILON_M
    )
    network.path_entries_served = sum(
        1 for entry in (path_entry_points or [])
        if entry.distance(connected_lines) <= CONNECTION_EPSILON_M
    )
    unserved_roads = network.entries_total - network.entries_served
    unserved_paths = network.path_entries_total - network.path_entries_served
    if unserved_roads or unserved_paths:
        network.notes.append({
            "code": "CONTEXT_ENTRIES_UNSERVED", "severity": "info",
            "message": f"Could not safely reach {unserved_roads} road and {unserved_paths} pathway "
                       "context anchor(s) from the internal network.",
            "source_phase": "street_graph",
        })
    if network.entries_served or network.path_entries_served:
        network.notes.append({
            "code": "CONTEXT_CONNECTIONS_APPLIED", "severity": "info",
            "message": f"Connected the plan to {network.entries_served} adjacent road and "
                       f"{network.path_entries_served} pathway anchor(s) "
                       f"({road_connectors + path_connectors} connector stub(s) added).",
            "source_phase": "street_graph",
        })

    # Buffer per line THEN union: buffering a merged multiline leaves hairline
    # bridges at the crossings (zero-area slivers) that keep the blocks
    # topologically CONNECTED after the difference — observed as "one block
    # with slits". Per-line bands unioned sever cleanly.
    bands = [
        seg.line.buffer(seg.row_width_m / 2, cap_style=2, join_style=2)
        for seg in full_span_kept
    ]

    # Intersections: pairwise centerline crossings (grid nodes). Single-Point
    # crossings are guaranteed by construction (horizontals are functions of x,
    # verticals are straight; translated horizontals never meet) — the geoms
    # filter is a defensive net for concave-boundary clip artifacts, not a
    # crutch. Byte-identical results on straight grids.
    seen: list[Point] = []
    for i, a in enumerate(network.centerlines):
        for b in network.centerlines[i + 1:]:
            crossing = a.intersection(b)
            points = [crossing] if isinstance(crossing, Point) else [
                g for g in getattr(crossing, "geoms", []) if isinstance(g, Point)
            ]
            for point in points:
                if all(point.distance(s) > 1.0 for s in seen):
                    seen.append(point)
    network.intersections = seen

    # Roundabouts at 1-2 major spine intersections. Unioned into street_area
    # BEFORE the generator differences the blocks, so block corners are trimmed
    # cleanly (an overlay after the fact would double-count land).
    spine_segs = [s for s in full_span_kept if s.role == "spine"]
    circles: list[BaseGeometry] = []
    if spine_segs and seen:
        spine_line = spine_segs[0].line
        candidates = sorted(
            (p for p in seen if p.distance(spine_line) < 0.5),
            key=lambda p: (p.distance(origin), p.x, p.y),
        )
        radius = (rules.spine_row_width_m + 6.0) / 2
        for point in candidates[: 2 if len(candidates) >= 6 else 1]:
            circles.append(point.buffer(radius, quad_segs=8))
            network.roundabouts.append((point, radius))

    network.street_area = make_valid(unary_union(bands + circles)).intersection(boundary_m)
    return network


def _append_context_connectors(
    *,
    boundary_m: Polygon,
    entries: list[Point],
    role: str,
    width_m: float,
    centerlines: list[LineString],
    segments: list[StreetSegment],
) -> int:
    """Join boundary anchors exactly to the nearest generated centreline.

    The historic phase shift aligned only the first anchor and merely checked
    whether the remainder were within 60 m.  These short, clipped stubs make
    every feasible connection topological: their ROW/path band participates in
    block carving and is emitted as real proposal geometry.
    """
    added = 0
    for entry in entries:
        if not centerlines:
            break
        connected = unary_union(centerlines)
        if entry.distance(connected) <= CONNECTION_EPSILON_M:
            continue
        anchor = nearest_points(entry, boundary_m.exterior)[1]
        raw = _shortest_visible_connector(anchor, centerlines, boundary_m)
        if raw is None:
            continue
        try:
            clipped = raw.intersection(boundary_m)
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001 — defensive against invalid municipal boundaries
            continue
        pieces = [clipped] if isinstance(clipped, LineString) else [
            geom for geom in getattr(clipped, "geoms", []) if isinstance(geom, LineString)
        ]
        if not pieces:
            continue
        inside_length = sum(piece.length for piece in pieces)
        if inside_length <= CONNECTION_EPSILON_M or inside_length < raw.length * 0.8:
            continue
        # Store the exact anchor-to-network line. Street-area emission clips
        # its buffer back to the site, while retaining the boundary endpoint
        # here makes connectivity topological rather than merely visual.
        centerlines.append(raw)
        segments.append(StreetSegment(
            line=raw, row_width_m=width_m, role=role, context_connection=True,
        ))
        added += 1
    return added


def _shortest_visible_connector(
    anchor: Point,
    centerlines: list[LineString],
    boundary_m: Polygon,
) -> LineString | None:
    """Return the shortest direct connection that remains inside the parcel.

    On a concave site, the nearest network point may sit across a notch. The
    one-shot nearest-point approach rejected that unsafe shortcut and stopped,
    even when another centreline was fully visible from the same entrance.
    Evaluate each line's nearest point and endpoints, then choose the shortest
    deterministic candidate covered by the valid site.
    """
    candidates: list[tuple[float, float, float, LineString]] = []
    seen: set[tuple[float, float]] = set()
    for line in centerlines:
        targets = [
            nearest_points(anchor, line)[1],
            Point(line.coords[0]),
            Point(line.coords[-1]),
        ]
        for target in targets:
            key = (round(target.x, 6), round(target.y, 6))
            if key in seen:
                continue
            seen.add(key)
            raw = LineString([anchor.coords[0], target.coords[0]])
            if raw.length <= CONNECTION_EPSILON_M or raw.length > ENTRY_CONNECTOR_MAX_M:
                continue
            candidates.append((raw.length, target.x, target.y, raw))

    safe_site = boundary_m.buffer(CONNECTION_EPSILON_M)
    for _length, _x, _y, raw in sorted(candidates, key=lambda item: item[:3]):
        try:
            if not safe_site.covers(raw):
                continue
            clipped = raw.intersection(boundary_m)
            pieces = [clipped] if isinstance(clipped, LineString) else [
                geom for geom in getattr(clipped, "geoms", [])
                if isinstance(geom, LineString)
            ]
            inside_length = sum(piece.length for piece in pieces)
            # A tolerance buffer absorbs projection noise, but must never turn
            # a line running just outside the parcel edge into a valid route.
            if inside_length >= raw.length * 0.98:
                return raw
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001 - invalid municipal boundaries
            continue
    return None


MAX_BLOCKS_PER_AXIS = 12   # runaway guard on very large greenfield sites


def _axis_positions(
    low: float, high: float, spacing: float, max_block_m: float = 0.0
) -> list[float]:
    """Interior gridline positions along [low, high].

    n_blocks starts from the preferred spacing (round, not floor — a span 1.4x
    the spacing should read as two blocks, not one oversized orphan) and is
    then raised until every resulting block edge is <= max_block_m. A span at
    least 1.3x the spacing takes ceil() so it can never round DOWN to a single
    block (the medium-site collapse: a 156 m span at 114 m spacing rounds to 1
    without this). Returns the n_blocks-1 evenly-spaced interior lines (empty
    for a single block)."""
    span = high - low
    if span <= 0:
        return []
    n_blocks = math.ceil(span / spacing) if span >= 1.3 * spacing else max(1, round(span / spacing))
    if max_block_m and max_block_m > 0:
        n_blocks = max(n_blocks, math.ceil(span / max_block_m))
    n_blocks = min(n_blocks, MAX_BLOCKS_PER_AXIS)
    if n_blocks <= 1:
        return []
    return [low + span * i / n_blocks for i in range(1, n_blocks)]


def _snap_nearest(
    positions: list[float], target: float, max_shift: float
) -> tuple[list[float], float | None]:
    """Shift the nearest position onto target; returns (positions, snapped value)."""
    if not positions:
        return positions, None
    index = min(range(len(positions)), key=lambda i: abs(positions[i] - target))
    if abs(positions[index] - target) <= max_shift:
        shifted = list(positions)
        shifted[index] = target
        return shifted, target
    return positions, None


def _line_sagitta(line: LineString) -> float:
    """Max distance of interior vertices to the first-last chord; 0 for 2-pt lines."""
    coords = list(line.coords)
    if len(coords) <= 2:
        return 0.0
    chord = LineString([coords[0], coords[-1]])
    return max(chord.distance(Point(c)) for c in coords[1:-1])


def _bow_offset(t: float, w2_sign: float) -> float:
    """Normalized bow profile: peak magnitude exactly 1, vanishes at t=0 and t=1."""
    t = min(1.0, max(0.0, t))
    return (math.sin(math.pi * t) + w2_sign * 0.15 * math.sin(2 * math.pi * t)) / BOW_PROFILE_MAX


def _bow_curve(
    base_y: float, x_lo: float, x_hi: float, span_lo: float, span_hi: float,
    amplitude: float, direction: float, w2_sign: float,
    step_m: float = CURVE_STEP_M,
) -> LineString:
    """Full-span horizontal bowed by amplitude·direction. t is measured over the
    INSET span and clamped, so the extension beyond the inset stays straight at
    base_y (entry snapping and edge behavior preserved by construction)."""
    span = max(span_hi - span_lo, 1e-9)
    count = max(16, int(math.ceil((x_hi - x_lo) / step_m)))
    points = []
    for k in range(count + 1):
        x = x_lo + (x_hi - x_lo) * k / count
        t = (x - span_lo) / span
        points.append((x, base_y + amplitude * direction * _bow_offset(t, w2_sign)))
    return LineString(points)


def _curve_amplitude(
    mode: str, ys: list[float], work_bounds: tuple[float, float, float, float], spacing: float
) -> float:
    """Closed-form amplitude with every safety cap; 0.0 means stay straight.

    Caps: slope (mitre joins stay benign at the 1.3π endpoint derivative of the
    normalized profile — 0.11·L keeps deflection ≈24°), edge margin (never pinch
    the boundary band below ~12 m of usable depth), absolute, mode-relative
    spacing (spine must not graze parallel straight locals; in all-mode the
    translation keeps spacing exact so only edge strips vary), and block-scale
    headroom (frozen evaluator counts MRR long edges ≤220 m — the bow must not
    push the deepest block row over it)."""
    if not ys:
        return 0.0
    minx, miny, maxx, maxy = work_bounds
    length = maxx - minx
    margin = min(min(ys) - miny, maxy - max(ys))
    if margin < CURVE_MARGIN_MIN_M:
        return 0.0
    ys_sorted = sorted(ys)
    gaps = [ys_sorted[0] - miny]
    gaps += [b - a for a, b in zip(ys_sorted, ys_sorted[1:])]
    gaps.append(maxy - ys_sorted[-1])
    headroom = max(0.0, BLOCK_EDGE_MAX_M - max(gaps))
    amplitude = min(
        0.11 * length,
        margin - 12.0,
        CURVE_AMPLITUDE_ABS_MAX_M,
        headroom,
        (0.30 if mode == "spine" else 0.35) * spacing,
    )
    return amplitude if amplitude >= CURVE_AMPLITUDE_MIN_M else 0.0
