"""Blocks -> parcels -> building masses. All metric, all deterministic.

Massing dispatches on a typology chosen by the placement policy:
perimeter_block (bars around a courtyard — the historic default), point_towers
(freestanding pads, tower-in-park), row_bars (parallel townhouse rows), and
anchor_mass (one large civic/institutional footprint). Every typology respects
the coverage cap and returns hole-free polygons (zones are single-ring
app-wide)."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.validation import make_valid

from app.services.plan_geometry.archetypes import TargetFootprint
from app.services.plan_geometry.community_rules import FLOOR_HEIGHT_M, RuleProfile
from app.services.site_engine import iter_polygons

logger = logging.getLogger(__name__)

MIN_PARCEL_M2 = 120.0
MIN_BLOCK_M2 = 400.0

# Model-aware segmentation: party-wall seam between modules (thin enough to
# read as one streetwall, wide enough that iter_polygons keeps pieces apart),
# stretch tolerance vs the archetype module, and zone-count guards. Small
# modules (an 8m rowhouse) are batched up to MODULE_MIN_W_M so a superblock
# doesn't shatter into hundreds of zones — the emitted module_w_m reports the
# EFFECTIVE width so downstream stays truthful.
MODULE_SEAM_M = 0.2
MODULE_STRETCH_MAX = 1.5
# Finer frontage grain (2026-07-12 research): a townhouse/machiya plot is
# 6-12 m, so batch tiny modules only up to 12 m (was 16) — narrow-frontage
# archetypes read as several buildings, not one fat block.
MODULE_MIN_W_M = 12.0
MAX_MODULES_PER_BAR = 8
# Runtime LEGO plans persist one independently compiled recipe per polygon.
# Keep exact/native cells bounded, but never batch a narrow frontage into one
# stretched model simply to satisfy the older generic zone-count guard.
MAX_RUNTIME_LEGO_CELLS_PER_AXIS = 48
RUNTIME_LEGO_SCALE_MIN = 0.82

# Void-safety cap: a perimeter ring built at the archetype's REAL depth can
# still leave an oversized interior when a shallow archetype sits on a big
# block. Deepen the ring toward COURTYARD_MAX_DEPTH_M (never below the real
# depth) to hold the void under this share. Ratio 0.42 from the 2026-07-12
# morphology research (healthy closed block sits 20-45 % open).
COURTYARD_MAX_RATIO = 0.42
COURTYARD_MAX_DEPTH_M = 22.0
# Below this clear dimension the ring's interior is a lightwell, not a
# courtyard — the block is treated as SOLID and grid-segmented instead.
MIN_COURTYARD_M = 14.0

# FAITHFUL FOOTPRINTS (user decision 2026-07-12): building depth is driven by
# the archetype's real metadata depth (target.depth_m, already clamped to the
# catalog min/max_d), NOT by the scenario coverage cap. The old cap crushed
# rings into ~6 m slivers on fine blocks (25/25 Environmental buildings 6-7 m
# deep against a 15-38 m metadata depth). SEAL_CAP is now only a loose ceiling
# that preserves the street setback — a deep archetype on a tight block simply
# fills it as a solid block (little/no courtyard), which is the intended form.
SEAL_CAP_RATIO = 0.92


@dataclass(frozen=True)
class TypologyDims:
    """Coarse footprint envelope for a massing typology.

    Values mirror the catalog's minWidth_m/maxWidth_m/minDepth_m/maxDepth_m for
    the archetypes the placement palettes target — the backend never reads the
    catalog JSON (the frontend resolver picks the exact archetype); it only
    needs envelopes in the right family:
      point_towers: condo_podium_tower / calgary_beltline_mid_rise plates ~25-35 m
      row_bars:     brownstone_rowhouse_frontage bar depth 8-12 m
      anchor_mass:  university_academic_complex / hospital slabs up to ~60x45 m
    """
    unit_w_m: float
    unit_d_m: float
    gap_m: float


def _long_axis_angle(poly: BaseGeometry) -> float:
    """Orientation (degrees) of the longest edge of the minimum rotated rectangle."""
    rect = poly.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    best_len, angle = 0.0, 0.0
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if length > best_len:
            best_len, angle = length, math.degrees(math.atan2(y2 - y1, x2 - x1))
    return angle


def _centered_cell_intervals(
    lo: float,
    hi: float,
    cell_size: float,
    gap: float,
) -> list[tuple[float, float]]:
    """Place fixed-size cells symmetrically, leaving excess span unbuilt."""

    span = hi - lo
    if cell_size <= 0 or span + 1e-6 < cell_size:
        return []
    count = max(1, int((span + gap) // (cell_size + gap)))
    count = min(count, MAX_RUNTIME_LEGO_CELLS_PER_AXIS)
    used = count * cell_size + max(0, count - 1) * gap
    start = lo + max(0.0, span - used) / 2
    return [
        (
            start + index * (cell_size + gap),
            start + index * (cell_size + gap) + cell_size,
        )
        for index in range(count)
    ]


def _runtime_lego_mass(
    block_m: BaseGeometry,
    outer: BaseGeometry,
    *,
    typology: str,
    dims: "TypologyDims | None",
    target: TargetFootprint,
    max_footprint: float,
) -> tuple[BaseGeometry, dict[str, Any]]:
    """Carve clean, directly compilable cells for a runtime LEGO identity.

    Generic plan massing is allowed to deepen a perimeter, equal-distribute a
    grid, batch an 8 m rowhouse into a 12-15 m frontage, or enlarge an anchor.
    Each of those operations is useful for coloured massing but can leave the
    selected LEGO family outside its strict 0.8-1.2 scale envelope. Runtime
    plans instead place native cells (uniformly reduced only when a block is
    slightly smaller) and return all leftover land to the residual landscape.
    """

    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = make_valid(affinity.rotate(outer, -angle, origin=origin))
    minx, miny, maxx, maxy = work.bounds
    span_x = maxx - minx
    span_y = maxy - miny
    if span_x <= 0 or span_y <= 0:
        return Polygon(), {}

    # Prefer the authored frontage/depth orientation. A swapped orientation is
    # a deterministic fallback for a narrow block; the LEGO planner records a
    # 90-degree instance rotation so facade proportions remain unchanged.
    orientations = (
        (float(target.width_m), float(target.depth_m), 0.0),
        (float(target.depth_m), float(target.width_m), 90.0),
    )
    choices: list[tuple[float, float, float, float]] = []
    for native_x, native_y, rotation in orientations:
        area_scale = math.sqrt(max_footprint / max(native_x * native_y, 1e-6))
        scale = min(1.0, span_x / native_x, span_y / native_y, area_scale)
        if scale + 1e-9 >= RUNTIME_LEGO_SCALE_MIN:
            choices.append((scale, -rotation, native_x, native_y))
    if not choices:
        return Polygon(), {}

    scale, negative_rotation, native_x, native_y = max(choices)
    orientation_rotation = -negative_rotation
    cell_x = native_x * scale
    cell_y = native_y * scale

    if typology == "row_bars":
        gap_x = MODULE_SEAM_M
        gap_y = max(MODULE_SEAM_M, float(dims.gap_m) if dims else 0.0)
    elif typology == "point_towers":
        gap_x = gap_y = max(MODULE_SEAM_M, float(dims.gap_m) if dims else 0.0)
    elif typology == "anchor_mass":
        gap_x = gap_y = max(span_x, span_y)
    else:
        gap_x = gap_y = MODULE_SEAM_M

    x_intervals = _centered_cell_intervals(minx, maxx, cell_x, gap_x)
    y_intervals = _centered_cell_intervals(miny, maxy, cell_y, gap_y)
    if not x_intervals or not y_intervals:
        return Polygon(), {}

    buffered_work = work.buffer(0.05)
    indexed: list[tuple[int, int, Polygon]] = []
    for y_index, (y0, y1) in enumerate(y_intervals):
        for x_index, (x0, x1) in enumerate(x_intervals):
            cell = box(x0, y0, x1, y1)
            if buffered_work.covers(cell):
                indexed.append((x_index, y_index, cell))

    if typology == "perimeter_block" and len(indexed) > 1:
        last_x = len(x_intervals) - 1
        last_y = len(y_intervals) - 1
        indexed = [
            item
            for item in indexed
            if item[0] in (0, last_x) or item[1] in (0, last_y)
        ]

    # Concave/clipped blocks can miss every centered grid cell. Search a few
    # stable centres and shrink uniformly, never below the strict fit floor.
    if not indexed:
        centres = (
            work.centroid,
            work.representative_point(),
        )
        probe_scale = scale
        while probe_scale + 1e-9 >= RUNTIME_LEGO_SCALE_MIN and not indexed:
            probe_x = native_x * probe_scale
            probe_y = native_y * probe_scale
            for centre in centres:
                candidate = box(
                    centre.x - probe_x / 2,
                    centre.y - probe_y / 2,
                    centre.x + probe_x / 2,
                    centre.y + probe_y / 2,
                )
                if buffered_work.covers(candidate):
                    indexed.append((0, 0, candidate))
                    cell_x, cell_y, scale = probe_x, probe_y, probe_scale
                    break
            probe_scale = round(probe_scale - 0.025, 6)

    if not indexed:
        return Polygon(), {}

    # Honour the loose seal cap by dropping complete cells, never distorting
    # the selected building to consume the remainder.
    cell_area = cell_x * cell_y
    max_cells = max(1, int(max_footprint // max(cell_area, 1e-6)))
    selected = [item[2] for item in indexed[:max_cells]]
    mass = unary_union(selected)
    mass = make_valid(affinity.rotate(mass, angle, origin=origin))
    return mass, {
        "runtime_lego_native_cells": True,
        "runtime_lego_uniform_scale": round(scale, 4),
        "runtime_lego_cell_rotation": orientation_rotation,
        "module_w_m": round(target.width_m * scale, 1),
        "module_d_m": round(target.depth_m * scale, 1),
    }


def subdivide_block(block_m: Polygon, parcel_width_m: float) -> list[Polygon]:
    """Slice a block into street-fronting parcels perpendicular to its long axis."""
    block_m = make_valid(block_m)
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(block_m, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    parcels: list[Polygon] = []
    x = minx
    while x < maxx:
        strip = box(x, miny - 1, min(x + parcel_width_m, maxx + 1), maxy + 1)
        piece = work.intersection(strip)
        for poly in iter_polygons(make_valid(piece)):
            if poly.area >= 1.0:
                parcels.append(poly)
        x += parcel_width_m

    # Merge slivers into their neighbour so every parcel is buildable.
    merged: list[Polygon] = []
    for parcel in parcels:
        if parcel.area < MIN_PARCEL_M2 and merged:
            candidate = make_valid(merged[-1].union(parcel))
            polys = list(iter_polygons(candidate))
            if len(polys) == 1:
                merged[-1] = polys[0]
                continue
        merged.append(parcel)

    return [affinity.rotate(p, angle, origin=origin) for p in merged]


def _segment_span(
    lo: float, hi: float, module_w: float, min_w: float = MODULE_MIN_W_M
) -> list[tuple[float, float]]:
    """Split [lo, hi] into equal modules nearest module_w (seam-separated).

    Even distribution by construction — no crumb pieces. Module width is
    floored at min_w (default MODULE_MIN_W_M: tiny frontages are batched into
    party-wall groups; grid DEPTH rows pass a lower floor so a row stays at
    the archetype's true depth) and the count capped at MAX_MODULES_PER_BAR
    (zone-count guard; a capped bar stretches its modules rather than
    multiplying them).
    """
    span = hi - lo
    module_w = max(module_w, min_w)
    if span <= 0 or module_w <= 0:
        return []
    n = max(1, round(span / module_w))
    while span / n > module_w * MODULE_STRETCH_MAX and n < MAX_MODULES_PER_BAR:
        n += 1
    n = min(n, MAX_MODULES_PER_BAR)
    step = span / n
    return [
        (lo + k * step + (MODULE_SEAM_M / 2 if k > 0 else 0),
         lo + (k + 1) * step - (MODULE_SEAM_M / 2 if k < n - 1 else 0))
        for k in range(n)
    ]


def _segment_bar_axis(bar: BaseGeometry, module_w: float, axis: str) -> list[Polygon]:
    """Cut an axis-aligned bar (rotated work frame) into modules along x|y.

    Keep-floor scales with the actual module (35% of step x bar depth) so
    small-module archetypes aren't silently dropped; near-rectangular filter
    sheds corner stubs on oblique blocks (a dropped corner reads as a corner
    plaza, an L-stub reads as a broken model).
    """
    minx, miny, maxx, maxy = bar.bounds
    spans = _segment_span(minx, maxx, module_w) if axis == "x" else _segment_span(miny, maxy, module_w)
    if not spans:
        return []
    step = (spans[0][1] - spans[0][0]) + MODULE_SEAM_M / 2
    cross = (maxy - miny) if axis == "x" else (maxx - minx)
    min_keep = max(25.0, 0.35 * step * cross)
    pieces: list[Polygon] = []
    for lo, hi in spans:
        cutter = box(lo, miny - 1, hi, maxy + 1) if axis == "x" else box(minx - 1, lo, maxx + 1, hi)
        for poly in iter_polygons(make_valid(bar.intersection(cutter))):
            if poly.area < min_keep:
                continue
            rect = poly.minimum_rotated_rectangle
            if poly.area / max(rect.area, 0.01) < 0.65:
                continue
            pieces.append(poly)
    return pieces


def _cross_cut(mass: BaseGeometry, frame_poly: BaseGeometry, center) -> BaseGeometry:
    """Subtract a thin cross through `center`, aligned to the frame's axes."""
    angle = _long_axis_angle(frame_poly)
    diag = math.hypot(*(hi - lo for lo, hi in zip(frame_poly.bounds[:2], frame_poly.bounds[2:])))
    cutter = affinity.rotate(
        box(center.x - diag, center.y - 0.1, center.x + diag, center.y + 0.1).union(
            box(center.x - 0.1, center.y - diag, center.x + 0.1, center.y + diag)
        ),
        angle, origin=center,
    )
    cut = make_valid(mass.difference(cutter))
    return cut if not cut.is_empty else mass


def _largest_hole_centroid(geom: BaseGeometry):
    """Centroid of the largest interior ring; deterministic tiebreak by ring
    area descending, then centroid (x, y)."""
    best = None
    for poly in iter_polygons(geom):
        for ring in poly.interiors:
            hole = Polygon(ring)
            key = (-hole.area, hole.centroid.x, hole.centroid.y)
            if best is None or key < best[0]:
                best = (key, hole.centroid)
    return best[1] if best else None


def decompose_holed(mass: BaseGeometry, frame_poly: BaseGeometry) -> BaseGeometry:
    """Split any holed geometry into hole-free pieces.

    Zone coordinates are single-ring across the app (shapefile import drops
    holes too), so a holed polygon serialized by its exterior draws as a SOLID
    slab — visually contradicting the ring-based statistics by ~2x and
    rendering as a courtyard-less megablock.

    A single cross through the frame centroid clears the historic case (one
    centered courtyard). Curved (crescent) blocks and multi-hole masses can
    leave the centroid outside the polygon or holes off both cut axes, so the
    cut REPEATS — each pass re-cuts at the largest REMAINING hole's centroid
    (deterministic tiebreak) until hole-free, bounded at 6 passes. Tiny cut
    fragments (<25 m²) are dropped so a cross grazing a curved wall can't emit
    confetti buildings; on straight blocks the first cut already succeeds and
    behavior is unchanged.
    """
    holed = [p for p in iter_polygons(mass) if p.interiors]
    if not holed:
        return mass

    result = _cross_cut(mass, frame_poly, frame_poly.centroid)
    for _ in range(6):
        if not any(p.interiors for p in iter_polygons(result)):
            break
        center = _largest_hole_centroid(result)
        if center is None:
            break
        recut = _cross_cut(result, frame_poly, center)
        if recut is result:  # cut had no effect; stop rather than loop
            break
        result = recut

    pieces = [p for p in iter_polygons(result)]
    kept = [p for p in pieces if p.area >= 25.0]
    if kept and len(kept) < len(pieces):
        result = unary_union(kept)
    return result if not result.is_empty else mass


def _decompose_ring_mass(mass: BaseGeometry, block_m: Polygon) -> BaseGeometry:
    return decompose_holed(mass, block_m)


def _perimeter_ring_bars(
    ring: BaseGeometry, block_m: BaseGeometry, depth: float, module_w: float
) -> list[Polygon]:
    """Butt-jointed rectangular bars around a perimeter ring, module-cut.

    Replaces the cross-cut decomposition (whose corner pieces are the
    L-shapes no rectangular model fits): N/S bars run full width, E/W bars
    sit between them, every bar is segmented at the archetype module width.
    """
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = make_valid(affinity.rotate(ring, -angle, origin=origin))
    minx, miny, maxx, maxy = work.bounds
    if maxx - minx <= 0 or maxy - miny <= 0:
        return []

    seam = MODULE_SEAM_M
    n_band = box(minx, maxy - depth, maxx, maxy)
    s_band = box(minx, miny, maxx, miny + depth)
    w_band = box(minx, miny + depth + seam, minx + depth, maxy - depth - seam)
    e_band = box(maxx - depth, miny + depth + seam, maxx, maxy - depth - seam)

    pieces: list[Polygon] = []
    for band, axis in ((n_band, "x"), (s_band, "x"), (w_band, "y"), (e_band, "y")):
        strip = make_valid(work.intersection(band))
        if strip.is_empty:
            continue
        for bar in iter_polygons(strip):
            if bar.area < 25.0:
                continue
            pieces.extend(_segment_bar_axis(bar, module_w, axis))
    return [affinity.rotate(p, angle, origin=origin) for p in pieces]


def _grid_segment_mass(
    solid: BaseGeometry, block_m: BaseGeometry, module_w: float, module_d: float
) -> list[Polygon]:
    """Tile a (near-)solid mass into a grid of archetype-sized modules.

    The perimeter-bar cutter degenerates when the ring closes over the block
    interior (overlapping N/S/E/W bands fail the rectangularity filter), so a
    solid block used to fall through to decompose_holed and emit ONE slab — a
    5 m-frontage machiya drawn as a 39x66 m mass. Faithful footprints need the
    opposite: a solid block reads as MANY archetype-sized buildings. Frontage
    (x) modules batch at MODULE_MIN_W_M like bars do; depth (y) rows keep the
    archetype's true depth (8 m floor only)."""
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = make_valid(affinity.rotate(solid, -angle, origin=origin))
    minx, miny, maxx, maxy = work.bounds
    x_spans = _segment_span(minx, maxx, module_w)
    y_spans = _segment_span(miny, maxy, module_d, min_w=8.0)
    if not x_spans or not y_spans:
        return []

    step_x = (x_spans[0][1] - x_spans[0][0]) + MODULE_SEAM_M / 2
    step_y = (y_spans[0][1] - y_spans[0][0]) + MODULE_SEAM_M / 2
    min_keep = max(25.0, 0.35 * step_x * step_y)
    pieces: list[Polygon] = []
    for y0, y1 in y_spans:
        for x0, x1 in x_spans:
            cell = box(x0, y0, x1, y1)
            for poly in iter_polygons(make_valid(work.intersection(cell))):
                if poly.area < min_keep:
                    continue
                rect = poly.minimum_rotated_rectangle
                if poly.area / max(rect.area, 0.01) < 0.65:
                    continue
                # Boundary-clipped edge cells can survive area + rectangularity
                # while being a narrow strip — the very sliver this fixes.
                coords = list(rect.exterior.coords)
                short_edge = min(
                    math.hypot(x2 - x1, y2 - y1)
                    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:])
                )
                if short_edge < 8.0:
                    continue
                pieces.append(poly)
    return [affinity.rotate(p, angle, origin=origin) for p in pieces]


def _perimeter_mass(
    block_m: BaseGeometry,
    outer: BaseGeometry,
    rules: RuleProfile,
    max_footprint: float,
    target: TargetFootprint | None = None,
) -> tuple[BaseGeometry, dict[str, Any]]:
    # FAITHFUL depth: the ring is as deep as the archetype really is (metadata,
    # clamped to catalog min/max_d upstream). No coverage-crush — that made the
    # ~6 m slivers. A depth >= block_minor/2 empties the inner buffer, so a deep
    # archetype on a tight block becomes a SOLID block (no courtyard) by
    # construction — the intended faithful-footprint behavior.
    base_depth = target.depth_m if target else rules.building_depth_m
    depth = base_depth

    def _ring(d: float) -> tuple[BaseGeometry, BaseGeometry]:
        inner = outer.buffer(-d)
        mass = outer.difference(inner) if not inner.is_empty else outer
        return mass, inner

    mass, inner = _ring(depth)

    # Void safety: a SHALLOW archetype on a BIG block leaves an oversized void.
    # Deepen the ring toward COURTYARD_MAX_DEPTH_M until the interior is a
    # believable courtyard (<= COURTYARD_MAX_RATIO) — but NEVER below the
    # archetype's real depth, and never past the seal cap (keep the setback).
    block_area = float(block_m.area)
    grow_cap = max(base_depth, COURTYARD_MAX_DEPTH_M)
    for _ in range(6):
        court_ratio = float(inner.area) / block_area if (not inner.is_empty and block_area) else 0.0
        if court_ratio <= COURTYARD_MAX_RATIO or float(mass.area) >= max_footprint or depth >= grow_cap:
            break
        depth = min(grow_cap, depth + 2.5)
        mass, inner = _ring(depth)

    # Seal guard only: if even the real-depth ring would over-build the block
    # (a deep archetype whose ring exceeds the seal cap while still leaving a
    # sliver of interior), pull depth back toward the cap — but never below the
    # archetype's real depth, so buildings stay faithful (they just go solid).
    for _ in range(3):
        if mass.area <= max_footprint or mass.area <= 0 or depth <= base_depth:
            break
        depth = max(base_depth, depth * max_footprint / mass.area)
        mass, inner = _ring(depth)

    if target is not None:
        # A ring whose interior is below courtyard scale is really a SOLID
        # block: grid-segment the whole inset into archetype-sized modules
        # (the ring-bar cutter degenerates on solid masses and would emit one
        # giant slab). The pinhole interior is absorbed into the modules.
        if inner.is_empty or float(inner.area) < MIN_COURTYARD_M**2:
            grid = _grid_segment_mass(outer, block_m, target.width_m, target.depth_m)
            if grid:
                return (
                    make_valid(unary_union(grid)),
                    {
                        "bar_depth_m": round(target.depth_m, 1),
                        "module_w_m": round(max(target.width_m, MODULE_MIN_W_M), 1),
                        "solid_block": True,
                    },
                )
        segmented = _perimeter_ring_bars(mass, block_m, depth, target.width_m)
        if segmented:
            return (
                make_valid(unary_union(segmented)),
                {
                    "bar_depth_m": round(depth, 1),
                    "module_w_m": round(max(target.width_m, MODULE_MIN_W_M), 1),
                },
            )
        # Degenerate segmentation (tiny/odd blocks): legacy path below.

    mass = make_valid(decompose_holed(mass, block_m))
    return mass, {"bar_depth_m": round(depth, 1)}


def _point_towers(
    block_m: BaseGeometry, outer: BaseGeometry, dims: TypologyDims, max_footprint: float
) -> BaseGeometry:
    """Freestanding pads on a centered grid — reads as tower-in-park."""
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(outer, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    pitch_x = dims.unit_w_m + dims.gap_m
    pitch_y = dims.unit_d_m + dims.gap_m
    nx = max(1, int((maxx - minx + dims.gap_m) // pitch_x))
    ny = max(1, int((maxy - miny + dims.gap_m) // pitch_y))
    ox = (minx + maxx) / 2 - (nx * pitch_x - dims.gap_m) / 2
    oy = (miny + maxy) / 2 - (ny * pitch_y - dims.gap_m) / 2

    pads: list[Polygon] = []
    for j in range(ny):
        for i in range(nx):
            pad = box(ox + i * pitch_x, oy + j * pitch_y,
                      ox + i * pitch_x + dims.unit_w_m, oy + j * pitch_y + dims.unit_d_m)
            for poly in iter_polygons(make_valid(pad.intersection(work))):
                if poly.area >= 200.0:
                    pads.append(poly)
    # Trim in reverse row-major order until under the coverage cap.
    while len(pads) > 1 and sum(p.area for p in pads) > max_footprint:
        pads.pop()
    if not pads:
        return Polygon()
    return affinity.rotate(unary_union(pads), angle, origin=origin)


def _row_bars(
    block_m: BaseGeometry,
    outer: BaseGeometry,
    dims: TypologyDims,
    max_footprint: float,
    target: TargetFootprint | None = None,
) -> BaseGeometry:
    """Parallel bars along the long axis — townhouse/rowhouse fabric."""
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(outer, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    depth = target.depth_m if target else dims.unit_d_m
    span = maxy - miny
    if span <= depth:
        return affinity.rotate(work, angle, origin=origin)  # too shallow: fill the inset

    count = max(1, int((span + dims.gap_m) // (depth + dims.gap_m)))
    while count > 2 and (span - depth) / (count - 1) < depth + 4.0:
        count -= 1  # keep a real gap between bars

    def _build(bar_depth: float, n: int) -> list[BaseGeometry]:
        if n == 1:
            ys = [miny + (span - bar_depth) / 2]
        else:
            step = (span - bar_depth) / (n - 1)
            ys = [miny + k * step for k in range(n)]
        bars = []
        for y in ys:
            piece = make_valid(box(minx - 1, y, maxx + 1, y + bar_depth).intersection(work))
            bars.extend(p for p in iter_polygons(piece) if p.area >= 100.0)
        return bars

    bars = _build(depth, count)
    # Over the cap: drop innermost bars first (keep the street-fronting first
    # and last). Faithful footprints — bars keep the archetype's real depth, so
    # the depth-shrink floor is target.depth (dropping bars is the lever, not
    # thinning them into slivers).
    base_bar_depth = depth
    while count > 2 and sum(p.area for p in bars) > max_footprint:
        count -= 1
        bars = _build(depth, count)
    for _ in range(3):
        total = sum(p.area for p in bars)
        if total <= max_footprint or depth <= base_bar_depth or not bars:
            break
        depth = max(base_bar_depth, depth * max_footprint / total)
        bars = _build(depth, count)
    if not bars:
        return Polygon()
    if target is not None:
        # Each rowhouse bar becomes N party-wall modules of the archetype
        # width — the globe then places one model per module at true scale.
        segmented: list[Polygon] = []
        for bar in bars:
            segmented.extend(_segment_bar_axis(bar, target.width_m, "x"))
        if segmented:
            bars = segmented
    return affinity.rotate(unary_union(bars), angle, origin=origin)


def _anchor_mass(
    block_m: BaseGeometry,
    outer: BaseGeometry,
    dims: TypologyDims,
    max_footprint: float,
    target: TargetFootprint | None = None,
) -> BaseGeometry:
    """One large civic/institutional footprint.

    Legacy path carves a deterministic L-notch; with a model target the mass
    stays a clean rectangle at the model's aspect (an L-shape can never fit a
    rectangular GLB), scaled up toward the block within the coverage cap.
    """
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(outer, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    if target is not None:
        w, d = target.width_m, target.depth_m
        # Grow toward the block, preserving aspect, bounded by extent + cap.
        grow = min(
            (maxx - minx) / w if w else 1.0,
            (maxy - miny) / d if d else 1.0,
            math.sqrt(max_footprint / (w * d)) if w * d else 1.0,
            MODULE_STRETCH_MAX,
        )
        if grow > 1.0:
            w, d = w * grow, d * grow
        w, d = min(w, maxx - minx), min(d, maxy - miny)
    else:
        w = min(dims.unit_w_m, maxx - minx)
        d = min(dims.unit_d_m, maxy - miny)
    if w <= 0 or d <= 0:
        return Polygon()
    if w * d > max_footprint:
        scale = math.sqrt(max_footprint / (w * d))
        w, d = w * scale, d * scale
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    mass = make_valid(box(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2).intersection(work))

    if target is None:
        notch = box(cx + w / 2 - 0.4 * w, cy + d / 2 - 0.4 * d, cx + w / 2 + 1, cy + d / 2 + 1)
        cut = make_valid(mass.difference(notch))
        polys = list(iter_polygons(cut))
        if len(polys) == 1 and polys[0].area >= 200.0:
            mass = polys[0]
    return affinity.rotate(mass, angle, origin=origin)


def building_mass_for_block(
    block_m: BaseGeometry,
    rules: RuleProfile,
    *,
    typology: str = "perimeter_block",
    dims: TypologyDims | None = None,
    target: TargetFootprint | None = None,
) -> tuple[BaseGeometry | None, dict[str, Any] | None]:
    """Massing for one block, dispatched by typology (default: perimeter bars
    around a courtyard). Coverage-capped, decomposed into hole-free polygons
    (zone-format safe). Small blocks get a simple inset pad. Degenerate
    typology output falls back to the perimeter path; info["typology"] reports
    what was actually built (the generator gates courtyard zones on it)."""
    block_m = make_valid(block_m)
    if block_m.area < MIN_BLOCK_M2:
        return None, None

    outer = block_m.buffer(-rules.front_setback_m)
    if outer.is_empty or outer.area < MIN_BLOCK_M2 / 2:
        return None, None

    # Faithful footprints: the massing depth comes from the archetype metadata,
    # so this is a LOOSE seal ceiling (preserve the street setback), not the
    # old scenario-coverage budget that crushed rings into slivers. Density
    # differences between scenarios come from floors, open space, and grain.
    max_footprint = SEAL_CAP_RATIO * block_m.area
    typology_used = typology
    extra: dict[str, Any] = {}
    mass: BaseGeometry = Polygon()

    if target is not None and target.source == "runtime_lego":
        mass, extra = _runtime_lego_mass(
            block_m,
            outer,
            typology=typology,
            dims=dims,
            target=target,
            max_footprint=max_footprint,
        )
        if mass.is_empty:
            # The block cannot hold even an 80%-uniform version of this exact
            # selectable identity. Leaving it unbuilt is honest and lets the
            # residual landscape fill it; emitting a clipped generic polygon
            # would force an unrelated post-hoc family rebound.
            return None, None
        info = {
            "footprint_m2": round(float(mass.area), 1),
            "coverage_of_block": round(float(mass.area) / float(block_m.area), 3),
            "typology": typology_used,
            **extra,
        }
        return mass, info

    if typology == "point_towers" and dims:
        # Target overrides the pad envelope; the grid gap stays typological.
        tower_dims = (
            TypologyDims(unit_w_m=target.width_m, unit_d_m=target.depth_m, gap_m=dims.gap_m)
            if target
            else dims
        )
        mass = _point_towers(block_m, outer, tower_dims, max_footprint)
    elif typology == "row_bars" and dims:
        mass = _row_bars(block_m, outer, dims, max_footprint, target=target)
    elif typology == "anchor_mass" and dims:
        mass = _anchor_mass(block_m, outer, dims, max_footprint, target=target)

    if mass.is_empty or typology == "perimeter_block" or not dims:
        mass, extra = _perimeter_mass(block_m, outer, rules, max_footprint, target=target)
        typology_used = "perimeter_block"

    mass = make_valid(mass)
    if mass.is_empty:
        return None, None

    info = {
        "footprint_m2": round(float(mass.area), 1),
        "coverage_of_block": round(float(mass.area) / float(block_m.area), 3),
        "typology": typology_used,
        **extra,
    }
    if target is not None:
        # Effective module width (small modules batch up to the floor) —
        # tests and downstream consumers see what was actually carved.
        info.setdefault("module_w_m", round(max(target.width_m, MODULE_MIN_W_M), 1))
        info["module_d_m"] = round(target.depth_m, 1)
    return mass, info


def clamp_floors_to_ceiling(
    floors: float,
    block_m: Polygon,
    district_lookup: list[tuple[BaseGeometry, dict[str, Any]]],
) -> tuple[float, dict[str, Any] | None]:
    """Clamp working storeys to the numeric ceiling of the district under the
    block centroid, when one exists. Returns (floors, clamp_info|None)."""
    centroid = block_m.centroid
    for geom, props in district_lookup:
        try:
            if geom.contains(centroid):
                height = props.get("height_m") or props.get("height")
                if height:
                    ceiling = float(height) / FLOOR_HEIGHT_M
                    if floors > ceiling:
                        return ceiling, {
                            "district": props.get("code") or props.get("lu_code"),
                            "ceiling_floors": round(ceiling, 1),
                            "requested_floors": floors,
                        }
                return floors, None
        except SoftTimeLimitExceeded:
            raise
        except Exception:  # noqa: BLE001
            continue
    return floors, None
