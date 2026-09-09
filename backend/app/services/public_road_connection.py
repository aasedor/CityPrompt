"""Bounded, explicit conceptual connections beyond a project's parcel."""

import math

from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon
from shapely.errors import GEOSException


def public_road_connection_fits(zone_type: str, properties: dict | None, candidate: Polygon, boundary: Polygon) -> bool:
    props = properties or {}
    if zone_type != "road" or props.get("connect_to_public_road") is not True:
        return False
    try:
        line = props.get("plan_centerline")
        if not isinstance(line, list) or len(line) < 2:
            return False
        lng, lat = boundary.centroid.x, boundary.centroid.y
        mx, my = 111320 * math.cos(math.radians(lat)), 111320
        transform = [mx, 0, 0, my, -lng * mx, -lat * my]
        parcel = affine_transform(boundary, transform).buffer(0.02)
        polygon = affine_transform(candidate, transform)
        route = affine_transform(LineString(line), transform)
        width = float(props.get("width", 0))
        if not 3 <= width <= 30 or not route.is_valid or not route.is_simple:
            return False
        ends = [parcel.covers(Point(p)) for p in [route.coords[0], route.coords[-1]]]
        outside = route.difference(parcel)
        return bool(
            sum(ends) == 1
            and outside.geom_type == "LineString"
            and outside.length <= 30
            and parcel.buffer(30).covers(polygon)
            and polygon.intersection(parcel).area >= polygon.area / 2
            # Apply the existing 15 cm tolerance at the end caps too. The
            # browser and server project around slightly different latitudes;
            # widening only the sides rejected valid, near-identical caps.
            and route.buffer(width / 2, cap_style=2, join_style=2).buffer(0.15).covers(polygon)
            and polygon.buffer(0.15).covers(route.buffer(width / 2, cap_style=2, join_style=2))
        )
    except (ValueError, TypeError, OverflowError, GEOSException):
        return False
