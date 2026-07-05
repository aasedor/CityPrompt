"""Spatial Intelligence Engine — pure Shapely-in-UTM geometry ops.

City-blind helpers the dataset transforms and DNA builder use for spatial
joins, nearest-neighbour, coverage, buffers, and clipping. Public API takes and
returns WGS84; all metric math happens in a site-local UTM frame built from the
existing site_engine helpers. No database, no HTTP — fully unit-testable.

Municipal geometries are routinely invalid (self-intersecting multipolygons);
every GeoJSON entering this module passes through ``make_valid`` so a
*successful* fetch can't crash downstream math.

Network distances are V1-estimated as straight-line x DETOUR_FACTOR and must be
labelled ``method="euclidean_estimate"`` wherever they surface.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from shapely.geometry import Point, Polygon, shape
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree
from shapely.validation import make_valid

from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)

logger = logging.getLogger(__name__)

DETOUR_FACTOR = 1.35  # straight-line -> street-network proxy; replace when real routing lands
DISTANCE_METHOD = "euclidean_estimate"

Feature = dict[str, Any]


def shape_of(feature: Feature) -> BaseGeometry | None:
    """GeoJSON feature -> valid Shapely geometry (WGS84), or None if unusable."""
    geometry = feature.get("geometry")
    if not geometry:
        return None
    try:
        geom = shape(geometry)
    except Exception:  # noqa: BLE001 — malformed municipal geometry
        return None
    if geom.is_empty:
        return None
    if not geom.is_valid:
        geom = make_valid(geom)
        if geom.is_empty:
            return None
    return geom


@dataclass
class SiteFrame:
    """Site-local metric frame: WGS84 boundary + its UTM projection, built once per site."""

    site_wgs84: Polygon
    site_m: BaseGeometry
    _to_metric: Any

    @classmethod
    def from_wgs84(cls, site_polygon: Polygon) -> "SiteFrame":
        if not site_polygon.is_valid:
            site_polygon = make_valid(site_polygon)
        crs = local_metric_crs_for_polygon(site_polygon)
        transformer = build_transformer("EPSG:4326", crs)
        site_m = project_geometry(site_polygon, transformer)
        return cls(site_wgs84=site_polygon, site_m=site_m, _to_metric=transformer)

    def to_metric(self, geom_wgs84: BaseGeometry) -> BaseGeometry:
        return project_geometry(geom_wgs84, self._to_metric)

    @property
    def area_m2(self) -> float:
        return float(self.site_m.area)

    @property
    def perimeter_m(self) -> float:
        return float(self.site_m.length)

    def centroid_wgs84(self) -> tuple[float, float]:
        c = self.site_wgs84.centroid
        return (c.x, c.y)


def _metric_geoms(frame: SiteFrame, features: list[Feature]) -> list[tuple[BaseGeometry, Feature]]:
    out: list[tuple[BaseGeometry, Feature]] = []
    for feature in features:
        geom = shape_of(feature)
        if geom is None:
            continue
        out.append((frame.to_metric(geom), feature))
    return out


def coverage_by(
    frame: SiteFrame,
    features: list[Feature],
    key_fn: Callable[[Feature], str | None],
    zone_m: BaseGeometry | None = None,
) -> dict[str, dict[str, float]]:
    """Area-weighted coverage of ``zone_m`` (default: the site) grouped by key.

    Returns {key: {"area_m2": ..., "pct": ...}} where pct is of the zone area.
    """
    zone = zone_m if zone_m is not None else frame.site_m
    zone_area = float(zone.area)
    if zone_area <= 0:
        return {}

    coverage: dict[str, dict[str, float]] = {}
    for geom_m, feature in _metric_geoms(frame, features):
        key = key_fn(feature)
        if key is None:
            continue
        overlap = geom_m.intersection(zone)
        if overlap.is_empty:
            continue
        entry = coverage.setdefault(key, {"area_m2": 0.0, "pct": 0.0})
        entry["area_m2"] += float(overlap.area)
    for entry in coverage.values():
        entry["pct"] = round(100.0 * entry["area_m2"] / zone_area, 2)
        entry["area_m2"] = round(entry["area_m2"], 1)
    return coverage


def ring_m(frame: SiteFrame, distance_m: float) -> BaseGeometry:
    """Metric ring around the site: buffer(distance) minus the site itself."""
    return frame.site_m.buffer(distance_m).difference(frame.site_m)


def intersecting(
    frame: SiteFrame,
    features: list[Feature],
    min_overlap_m2: float = 1.0,
) -> list[tuple[Feature, float]]:
    """Features whose geometry overlaps the site by at least ``min_overlap_m2``.

    Returns (feature, overlap_m2) pairs sorted by descending overlap. For point
    and line features the threshold is ignored (any intersection counts).
    """
    hits: list[tuple[Feature, float]] = []
    for geom_m, feature in _metric_geoms(frame, features):
        if geom_m.area > 0:
            overlap = geom_m.intersection(frame.site_m)
            if overlap.is_empty or overlap.area < min_overlap_m2:
                continue
            hits.append((feature, float(overlap.area)))
        elif geom_m.intersects(frame.site_m):
            hits.append((feature, 0.0))
    hits.sort(key=lambda pair: pair[1], reverse=True)
    return hits


def nearest(
    frame: SiteFrame,
    features: list[Feature],
    k: int = 5,
) -> list[tuple[float, Feature]]:
    """k nearest features to the site boundary, as (distance_m, feature)."""
    geoms = _metric_geoms(frame, features)
    if not geoms:
        return []
    tree = STRtree([g for g, _ in geoms])
    count = min(k, len(geoms))
    indices = tree.query_nearest(frame.site_m, max_distance=None, return_distance=False, all_matches=False)
    # STRtree.query_nearest returns only the closest; for k results rank all by distance.
    if count > 1 or len(indices) == 0:
        ranked = sorted(
            ((float(g.distance(frame.site_m)), f) for g, f in geoms),
            key=lambda pair: pair[0],
        )
        return ranked[:count]
    idx = int(indices[0])
    geom, feature = geoms[idx]
    return [(float(geom.distance(frame.site_m)), feature)]


def count_within(frame: SiteFrame, features: list[Feature], radius_m: float) -> int:
    """How many features fall within ``radius_m`` of the site boundary."""
    envelope = frame.site_m.buffer(radius_m)
    return sum(1 for geom_m, _ in _metric_geoms(frame, features) if geom_m.intersects(envelope))


def length_within_by(
    frame: SiteFrame,
    features: list[Feature],
    key_fn: Callable[[Feature], str | None],
    radius_m: float,
) -> dict[str, float]:
    """Total line length (m) within ``radius_m`` of the site, grouped by key."""
    envelope = frame.site_m.buffer(radius_m)
    totals: dict[str, float] = {}
    for geom_m, feature in _metric_geoms(frame, features):
        key = key_fn(feature)
        if key is None:
            continue
        clipped = geom_m.intersection(envelope)
        if clipped.is_empty:
            continue
        totals[key] = totals.get(key, 0.0) + float(clipped.length)
    return {key: round(value, 1) for key, value in totals.items()}


def frontage(
    frame: SiteFrame,
    features: list[Feature],
    tolerance_m: float = 25.0,
) -> list[tuple[Feature, float]]:
    """Line features fronting the site (within tolerance of its boundary).

    Returns (feature, shared_length_m) for each fronting line, longest first.
    """
    edge_zone = frame.site_m.boundary.buffer(tolerance_m)
    fronting: list[tuple[Feature, float]] = []
    for geom_m, feature in _metric_geoms(frame, features):
        shared = geom_m.intersection(edge_zone)
        if shared.is_empty or shared.length <= 0:
            continue
        fronting.append((feature, round(float(shared.length), 1)))
    fronting.sort(key=lambda pair: pair[1], reverse=True)
    return fronting


def network_distance_estimate_m(straight_line_m: float) -> float:
    """Street-network distance proxy. Callers must label output method="euclidean_estimate"."""
    return round(straight_line_m * DETOUR_FACTOR, 1)


def point_wgs84(lon: float, lat: float) -> Point:
    return Point(lon, lat)
