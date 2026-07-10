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

from app.services.plan_geometry.community_rules import FLOOR_HEIGHT_M, RuleProfile
from app.services.site_engine import iter_polygons

logger = logging.getLogger(__name__)

MIN_PARCEL_M2 = 120.0
MIN_BLOCK_M2 = 400.0


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


def decompose_holed(mass: BaseGeometry, frame_poly: BaseGeometry) -> BaseGeometry:
    """Split any holed geometry into hole-free pieces.

    Zone coordinates are single-ring across the app (shapefile import drops
    holes too), so a holed polygon serialized by its exterior draws as a SOLID
    slab — visually contradicting the ring-based statistics by ~2x and
    rendering as a courtyard-less megablock. Cutting a thin cross through the
    frame centroid (aligned to the frame's axes) yields simple pieces.
    """
    holed = [p for p in iter_polygons(mass) if p.interiors]
    if not holed:
        return mass

    angle = _long_axis_angle(frame_poly)
    centroid = frame_poly.centroid
    diag = math.hypot(*(hi - lo for lo, hi in zip(frame_poly.bounds[:2], frame_poly.bounds[2:])))
    cutter = affinity.rotate(
        box(centroid.x - diag, centroid.y - 0.1, centroid.x + diag, centroid.y + 0.1).union(
            box(centroid.x - 0.1, centroid.y - diag, centroid.x + 0.1, centroid.y + diag)
        ),
        angle, origin=centroid,
    )
    cut = make_valid(mass.difference(cutter))
    return cut if not cut.is_empty else mass


def _decompose_ring_mass(mass: BaseGeometry, block_m: Polygon) -> BaseGeometry:
    return decompose_holed(mass, block_m)


def _perimeter_mass(
    block_m: BaseGeometry, outer: BaseGeometry, rules: RuleProfile, max_footprint: float
) -> tuple[BaseGeometry, dict[str, Any]]:
    depth = rules.building_depth_m
    inner = outer.buffer(-depth)
    mass: BaseGeometry = outer.difference(inner) if not inner.is_empty else outer

    # Iterative shrink: one proportional step under-corrects on small blocks
    # (ring area is not linear in depth) — up to ~27% over the cap observed.
    for _ in range(3):
        if mass.area <= max_footprint or mass.area <= 0 or depth <= 6.0:
            break
        depth = max(6.0, depth * max_footprint / mass.area)
        inner = outer.buffer(-depth)
        mass = outer.difference(inner) if not inner.is_empty else outer

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
    block_m: BaseGeometry, outer: BaseGeometry, dims: TypologyDims, max_footprint: float
) -> BaseGeometry:
    """Parallel bars along the long axis — townhouse/rowhouse fabric."""
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(outer, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    depth = dims.unit_d_m
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
    # and last), then shrink depth as a final resort.
    while count > 2 and sum(p.area for p in bars) > max_footprint:
        count -= 1
        bars = _build(depth, count)
    for _ in range(3):
        total = sum(p.area for p in bars)
        if total <= max_footprint or depth <= 6.0 or not bars:
            break
        depth = max(6.0, depth * max_footprint / total)
        bars = _build(depth, count)
    if not bars:
        return Polygon()
    return affinity.rotate(unary_union(bars), angle, origin=origin)


def _anchor_mass(
    block_m: BaseGeometry, outer: BaseGeometry, dims: TypologyDims, max_footprint: float
) -> BaseGeometry:
    """One large civic/institutional footprint with a deterministic L-notch."""
    angle = _long_axis_angle(block_m)
    origin = block_m.centroid
    work = affinity.rotate(outer, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds

    w = min(dims.unit_w_m, maxx - minx)
    d = min(dims.unit_d_m, maxy - miny)
    if w <= 0 or d <= 0:
        return Polygon()
    if w * d > max_footprint:
        scale = math.sqrt(max_footprint / (w * d))
        w, d = w * scale, d * scale
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    mass = make_valid(box(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2).intersection(work))

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

    max_footprint = rules.coverage_ratio * block_m.area
    typology_used = typology
    extra: dict[str, Any] = {}
    mass: BaseGeometry = Polygon()

    if typology == "point_towers" and dims:
        mass = _point_towers(block_m, outer, dims, max_footprint)
    elif typology == "row_bars" and dims:
        mass = _row_bars(block_m, outer, dims, max_footprint)
    elif typology == "anchor_mass" and dims:
        mass = _anchor_mass(block_m, outer, dims, max_footprint)

    if mass.is_empty or typology == "perimeter_block" or not dims:
        mass, extra = _perimeter_mass(block_m, outer, rules, max_footprint)
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
