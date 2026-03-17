"""First-phase real-world site engine.

This module keeps the live OSM fetch isolated from the geometry pipeline so the
projection, right-of-way derivation, and block cleanup logic can be tested
offline.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Iterable
from typing import Any, Protocol

from pyproj import CRS, Transformer
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon
from shapely.ops import transform, unary_union

from app.services.osm_context import OSMContextFetcher

logger = logging.getLogger(__name__)

WGS84_CRS = CRS.from_epsg(4326)
DEFAULT_SLIVER_AREA_THRESHOLD_SQM = 50.0


class OSMStreetContextFetcher(Protocol):
    """Protocol for OSM fetchers used by the site engine."""

    async def fetch(
        self,
        polygon: Polygon,
        buffer_m: float = 50,
    ) -> dict[str, Any]:
        """Fetch OSM context for a WGS84 site polygon."""


def local_metric_crs_for_polygon(site_polygon: Polygon) -> CRS:
    """Choose a local UTM CRS based on the polygon centroid."""
    centroid = site_polygon.centroid
    lon = centroid.x
    lat = centroid.y
    zone = int(math.floor((lon + 180.0) / 6.0) + 1)
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)


def build_transformer(source_crs: CRS | str, target_crs: CRS | str) -> Transformer:
    """Create a Shapely-friendly transformer."""
    return Transformer.from_crs(source_crs, target_crs, always_xy=True)


def project_geometry(
    geometry: Polygon | LineString | MultiPolygon | GeometryCollection,
    transformer: Transformer,
):
    """Project any Shapely geometry using the supplied transformer."""
    return transform(transformer.transform, geometry)


def derive_right_of_way_polygons(
    roads: Iterable[dict[str, Any]],
    *,
    to_metric: Transformer,
    site_metric: Polygon | MultiPolygon | None = None,
) -> list[dict[str, Any]]:
    """Buffer road centerlines into metric ROW polygons, clipped to the site."""
    row_features: list[dict[str, Any]] = []

    for road in roads:
        coords = road.get("coordinates") or []
        if len(coords) < 2:
            continue

        try:
            centerline = LineString(coords)
        except Exception:
            logger.debug("Skipping invalid road geometry for OSM id=%s", road.get("osm_id"))
            continue

        if centerline.is_empty or centerline.length == 0:
            continue

        width_m = max(float(road.get("width_m") or 0.0), 1.0)
        centerline_metric = project_geometry(centerline, to_metric)
        row_polygon = centerline_metric.buffer(
            width_m / 2.0,
            cap_style=2,
            join_style=2,
        )

        if site_metric is not None:
            row_polygon = row_polygon.intersection(site_metric)

        if row_polygon.is_empty:
            continue

        for clipped in iter_polygons(row_polygon):
            row_features.append(
                {
                    "osm_id": road.get("osm_id"),
                    "name": road.get("name"),
                    "road_type": road.get("road_type", "residential"),
                    "width_m": width_m,
                    "geometry": clipped,
                }
            )

    return row_features


def cleanup_developable_blocks(
    geometry,
    *,
    sliver_area_threshold: float = DEFAULT_SLIVER_AREA_THRESHOLD_SQM,
) -> list[Polygon]:
    """Normalize difference geometry and discard unusable slivers."""
    cleaned: list[Polygon] = []

    for polygon in iter_polygons(geometry):
        normalized = polygon.buffer(0)
        for candidate in iter_polygons(normalized):
            without_tiny_holes = _remove_small_holes(candidate, sliver_area_threshold)
            if without_tiny_holes.is_empty:
                continue
            if without_tiny_holes.area < sliver_area_threshold:
                continue
            cleaned.append(without_tiny_holes)

    cleaned.sort(key=lambda poly: poly.area, reverse=True)
    return cleaned


def iter_polygons(geometry) -> Iterable[Polygon]:
    """Yield polygonal members from a geometry of any supported type."""
    if geometry is None or geometry.is_empty:
        return

    if isinstance(geometry, Polygon):
        yield geometry
        return

    if isinstance(geometry, MultiPolygon):
        for polygon in geometry.geoms:
            if not polygon.is_empty:
                yield polygon
        return

    if isinstance(geometry, GeometryCollection):
        for member in geometry.geoms:
            yield from iter_polygons(member)


def _remove_small_holes(polygon: Polygon, threshold: float) -> Polygon:
    """Strip tiny interior holes that do not materially affect buildability."""
    retained_holes = []
    for ring in polygon.interiors:
        hole = Polygon(ring.coords)
        if hole.area >= threshold:
            retained_holes.append(ring.coords)
    return Polygon(polygon.exterior.coords, retained_holes)


def _crs_label(crs: CRS) -> str:
    authority = crs.to_authority()
    if authority:
        return f"{authority[0]}:{authority[1]}"
    return crs.to_string()


def _polygon_to_wgs84_coordinates(polygon: Polygon, to_wgs84: Transformer) -> list[list[float]]:
    polygon_wgs84 = project_geometry(polygon, to_wgs84)
    coords = [[float(x), float(y)] for x, y in polygon_wgs84.exterior.coords]
    if coords and coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


class RealWorldSiteEngine:
    """Fetch street context and derive developable blocks from a site boundary."""

    def __init__(self, context_fetcher: OSMStreetContextFetcher | None = None):
        self.context_fetcher = context_fetcher or OSMContextFetcher()

    async def extract_developable_blocks(
        self,
        site_polygon: Polygon,
        *,
        osm_context: dict[str, Any] | None = None,
        buffer_m: float = 50,
        sliver_area_threshold: float = DEFAULT_SLIVER_AREA_THRESHOLD_SQM,
    ) -> dict[str, Any]:
        """Return developable blocks after subtracting road ROW polygons."""
        fetched_context = False
        if osm_context is None:
            osm_context = await self.context_fetcher.fetch(site_polygon, buffer_m=buffer_m)
            fetched_context = True

        metric_crs = local_metric_crs_for_polygon(site_polygon)
        to_metric = build_transformer(WGS84_CRS, metric_crs)
        to_wgs84 = build_transformer(metric_crs, WGS84_CRS)
        site_metric = project_geometry(site_polygon, to_metric)
        roads = list(osm_context.get("roads", []))

        row_features = derive_right_of_way_polygons(
            roads,
            to_metric=to_metric,
        )
        clipped_row_features: list[dict[str, Any]] = []
        for feature in row_features:
            clipped_geometry = feature["geometry"].intersection(site_metric)
            if clipped_geometry.is_empty:
                continue
            for clipped in iter_polygons(clipped_geometry):
                clipped_feature = dict(feature)
                clipped_feature["geometry"] = clipped
                clipped_row_features.append(clipped_feature)

        row_union = unary_union([feature["geometry"] for feature in row_features]) if row_features else None

        developable_geometry = site_metric
        if row_union is not None and not row_union.is_empty:
            developable_geometry = site_metric.difference(row_union)

        blocks = cleanup_developable_blocks(
            developable_geometry,
            sliver_area_threshold=sliver_area_threshold,
        )

        clipped_row_union = unary_union([feature["geometry"] for feature in clipped_row_features]) if clipped_row_features else None
        right_of_way_area_sqm = float(clipped_row_union.area) if clipped_row_union is not None else 0.0
        developable_area_sqm = float(sum(block.area for block in blocks))
        site_area_sqm = float(site_metric.area)
        roads_considered = len({feature.get("osm_id") for feature in clipped_row_features if feature.get("osm_id") is not None}) or len(clipped_row_features)

        logger.info(
            "Derived %d developable blocks from %d roads for site area %.1f sqm",
            len(blocks),
            roads_considered,
            site_area_sqm,
        )

        return {
            "metric_crs": _crs_label(metric_crs),
            "fetched_context": fetched_context,
            "buffer_m": buffer_m,
            "sliver_area_threshold_sqm": float(sliver_area_threshold),
            "site_area_sqm": site_area_sqm,
            "right_of_way_area_sqm": right_of_way_area_sqm,
            "developable_area_sqm": developable_area_sqm,
            "roads_considered": roads_considered,
            "right_of_way_polygons": [
                {
                    "osm_id": feature.get("osm_id"),
                    "name": feature.get("name"),
                    "road_type": feature.get("road_type"),
                    "width_m": float(feature.get("width_m") or 0.0),
                    "coordinates": _polygon_to_wgs84_coordinates(feature["geometry"], to_wgs84),
                    "area_sqm": float(feature["geometry"].area),
                }
                for feature in clipped_row_features
            ],
            "developable_blocks": [
                {
                    "block_index": index,
                    "coordinates": _polygon_to_wgs84_coordinates(block, to_wgs84),
                    "area_sqm": float(block.area),
                }
                for index, block in enumerate(blocks)
            ],
        }

