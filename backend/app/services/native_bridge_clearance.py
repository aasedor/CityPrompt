"""Measured modular bridge reservations, separate from at-grade street joins."""

import math

from shapely.geometry import Polygon

from app.services.native_modular_bridge import is_modular_bridge, modular_bridge_profile
from app.services.native_specialist_streets import validate_specialist_properties
from app.services.surface_path import surface_path_width


# Source 0dbeb273… retains complete end piers 5/3 m beyond each nominal
# end module. The five public bridge programme dimensions remain unchanged.
_SUPPORT_OVERLAP_M = {"timber_covered_bridge_route_v1": 5 / 3}
_AREA_TOLERANCE_M2 = 1e-6


def validate_modular_bridge_footprint(geometry, properties):
    """Match a source bridge to its authored axis, even when width > span.

    Generic road principal-axis recovery is not valid for these wide stair and
    approach reservations. Retain the same 10 cm corridor tolerance as clearance.
    """
    validate_specialist_properties(properties)
    if not isinstance(geometry, Polygon) or geometry.is_empty or not geometry.is_valid or geometry.interiors:
        raise ValueError("Keep a complete valid modular bridge footprint.")
    profile = modular_bridge_profile(properties["road_selected_variant_id"])
    route = properties["plan_centerline"]
    if not isinstance(route, list):
        raise ValueError("Modular bridge clearance requires its explicit saved two-endpoint coordinate array.")
    origin = route[0]
    sx = 111320 * math.cos(math.radians(origin[1]))

    def local(point):
        return ((point[0] - origin[0]) * sx, (point[1] - origin[1]) * 111320)

    dx, dy = local(route[-1])
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    half = profile["widthM"] / 2
    occupied = Polygon(
        [
            (ux * along - uy * across, uy * along + ux * across)
            for along, across in ((0, -half), (length, -half), (length, half), (0, half))
        ]
    )
    footprint = Polygon([local(point) for point in geometry.exterior.coords])
    if not occupied.buffer(0.1).covers(footprint) or not footprint.buffer(0.1).covers(occupied):
        raise ValueError("Keep the modular bridge footprint aligned with its current saved two-endpoint route.")


def _validate_bridge_pair(bridge_coordinates, bridge_properties, other_coordinates, other_properties):
    validate_modular_bridge_footprint(Polygon(bridge_coordinates), bridge_properties)
    profile = modular_bridge_profile(bridge_properties["road_selected_variant_id"])
    route = bridge_properties["plan_centerline"]
    if not isinstance(route, list):
        raise ValueError("Modular bridge clearance requires its explicit saved two-endpoint coordinate array.")
    origin = route[0]
    sx = 111320 * math.cos(math.radians(origin[1]))

    def local(point):
        return ((point[0] - origin[0]) * sx, (point[1] - origin[1]) * 111320)

    dx, dy = local(route[-1])
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    half = profile["widthM"] / 2

    def corridor(start, end):
        return Polygon(
            [
                (ux * along - uy * across, uy * along + ux * across)
                for along, across in ((start, -half), (start, half), (end, half), (end, -half))
            ]
        )

    occupied = corridor(0, length)
    other = Polygon([local(point) for point in other_coordinates])
    overlap = occupied.intersection(other)
    if overlap.area <= _AREA_TOLERANCE_M2:
        return  # Shared ground endpoints and touching footprint edges stay usable.
    if profile["program"]["adapter"] == "source-span-bridge-v1":
        raise ValueError("Keep other objects clear of this bridge structure. Routes may meet at its endpoints.")
    if (
        isinstance(other_properties.get("lane_count"), bool)
        or other_properties.get("lane_count") != 0
        or surface_path_width(other_properties) is None
    ):
        raise ValueError(
            "Keep other bridge structures and motor roads outside this modular bridge; ground endpoints may touch."
        )
    bridge = profile["program"]["bridge"]
    reserve = bridge["approachM"] + bridge["endM"] + _SUPPORT_OVERLAP_M[profile["id"]]
    clear_span = corridor(reserve, length - reserve)
    if not clear_span.buffer(1e-6).covers(overlap):
        raise ValueError(
            "Keep paths outside the modular bridge stairs, end structures and support piers; use its clear central opening."
        )


def validate_modular_bridge_overlap(candidate_coordinates, candidate_properties, neighbours):
    """Check either edit direction using full width polygon footprints."""
    candidate_bridge = is_modular_bridge(candidate_properties)
    for coordinates, properties in neighbours:
        if candidate_bridge:
            _validate_bridge_pair(candidate_coordinates, candidate_properties, coordinates, properties)
        elif is_modular_bridge(properties):
            _validate_bridge_pair(coordinates, properties, candidate_coordinates, candidate_properties)
