"""Blocks -> parcels -> perimeter building masses. All metric, all deterministic."""

from __future__ import annotations

import logging
import math
from typing import Any

from celery.exceptions import SoftTimeLimitExceeded
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid

from app.services.plan_geometry.community_rules import FLOOR_HEIGHT_M, RuleProfile
from app.services.site_engine import iter_polygons

logger = logging.getLogger(__name__)

MIN_PARCEL_M2 = 120.0
MIN_BLOCK_M2 = 400.0


def subdivide_block(block_m: Polygon, parcel_width_m: float) -> list[Polygon]:
    """Slice a block into street-fronting parcels perpendicular to its long axis."""
    block_m = make_valid(block_m)
    rect = block_m.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    best_len, angle = 0.0, 0.0
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if length > best_len:
            best_len, angle = length, math.degrees(math.atan2(y2 - y1, x2 - x1))

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


def _decompose_ring_mass(mass: BaseGeometry, block_m: Polygon) -> BaseGeometry:
    """Split a courtyard-ring mass into hole-free bars.

    Zone coordinates are single-ring across the app (shapefile import drops
    holes too), so a holed polygon serialized by its exterior draws as a SOLID
    slab — visually contradicting the ring-based statistics by ~2x and
    rendering as a courtyard-less megablock. Cutting a thin cross through the
    courtyard centroid (aligned to the block's axes) yields 4 simple bars.
    """
    holed = [p for p in iter_polygons(mass) if p.interiors]
    if not holed:
        return mass

    rect = block_m.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    best_len, angle = 0.0, 0.0
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if length > best_len:
            best_len, angle = length, math.degrees(math.atan2(y2 - y1, x2 - x1))

    centroid = block_m.centroid
    diag = math.hypot(*(hi - lo for lo, hi in zip(block_m.bounds[:2], block_m.bounds[2:])))
    cutter = affinity.rotate(
        box(centroid.x - diag, centroid.y - 0.1, centroid.x + diag, centroid.y + 0.1).union(
            box(centroid.x - 0.1, centroid.y - diag, centroid.x + 0.1, centroid.y + diag)
        ),
        angle, origin=centroid,
    )
    cut = make_valid(mass.difference(cutter))
    return cut if not cut.is_empty else mass


def building_mass_for_block(
    block_m: Polygon, rules: RuleProfile
) -> tuple[BaseGeometry | None, dict[str, Any] | None]:
    """Perimeter-block massing: bars of building_depth around a courtyard,
    coverage-capped, decomposed into hole-free polygons (zone-format safe).
    Small blocks get a simple inset pad."""
    block_m = make_valid(block_m)
    if block_m.area < MIN_BLOCK_M2:
        return None, None

    outer = block_m.buffer(-rules.front_setback_m)
    if outer.is_empty or outer.area < MIN_BLOCK_M2 / 2:
        return None, None

    depth = rules.building_depth_m
    inner = outer.buffer(-depth)
    mass: BaseGeometry = outer.difference(inner) if not inner.is_empty else outer

    max_footprint = rules.coverage_ratio * block_m.area
    # Iterative shrink: one proportional step under-corrects on small blocks
    # (ring area is not linear in depth) — up to ~27% over the cap observed.
    for _ in range(3):
        if mass.area <= max_footprint or mass.area <= 0 or depth <= 6.0:
            break
        depth = max(6.0, depth * max_footprint / mass.area)
        inner = outer.buffer(-depth)
        mass = outer.difference(inner) if not inner.is_empty else outer

    mass = make_valid(_decompose_ring_mass(mass, block_m))
    if mass.is_empty:
        return None, None

    info = {
        "footprint_m2": round(float(mass.area), 1),
        "coverage_of_block": round(float(mass.area) / float(block_m.area), 3),
        "bar_depth_m": round(depth, 1),
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
