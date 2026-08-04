"""Shared adapter geometry — metric-buffered, vertex-bounded site envelopes.

Every HTTP adapter (Socrata, Opendatasoft, ArcGIS) queries "features
intersecting the buffered site boundary". The buffer is metric-accurate (UTM)
— degree-averaged buffering undercounts east-west by ~18% at Calgary
latitudes, silently shrinking walksheds. The ring is simplified to
``max_vertices`` so query URLs and POST bodies stay bounded.
"""

from __future__ import annotations

from shapely.geometry import Polygon

from app.services.spatial_engine import buffer_wgs84

MAX_VERTICES = 120


def buffered_boundary(boundary_wgs84: Polygon, buffer_m: float, max_vertices: int = MAX_VERTICES) -> Polygon:
    """Buffered site boundary with a bounded exterior ring (WGS84)."""
    buffered = buffer_wgs84(boundary_wgs84, buffer_m)
    # Keep doubling tolerance until the ring is genuinely bounded.
    tolerance = 0.0001
    for _ in range(6):
        if len(buffered.exterior.coords) <= max_vertices:
            break
        buffered = buffered.simplify(tolerance, preserve_topology=True)
        tolerance *= 2
    return buffered


def boundary_wkt(boundary_wgs84: Polygon, buffer_m: float) -> str:
    """Buffered site boundary as WKT (lon lat order, exterior ring only)."""
    ring = buffered_boundary(boundary_wgs84, buffer_m)
    coords = ", ".join(f"{lon:.6f} {lat:.6f}" for lon, lat in ring.exterior.coords)
    return f"POLYGON(({coords}))"
