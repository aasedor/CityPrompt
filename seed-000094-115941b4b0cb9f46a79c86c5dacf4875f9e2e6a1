"""Ownership helpers for derived Community 3D building artifacts.

Buildings created by Community 3D carry an explicit source-zone marker.  The
marker is the ownership boundary that lets plan regeneration remove obsolete
derived artifacts without guessing from names, LEGO metadata, or model URLs.
Unmarked and malformed rows are deliberately treated as user-owned.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from app.models.models import Building

COMMUNITY_REPRESENTATION_SPEC_KEY = "community3DRepresentation"
COMMUNITY_BUILDING_GENERATORS = frozenset({
    "lego_assembly",
    "planned_massing",
    "meshy",
})


def community_3d_source_zone_id(building: Building) -> uuid.UUID | None:
    """Return the owned source zone for a valid derived-building marker.

    Being conservative here is intentional: a row is safe to remove only when
    it has the exact marker written by the Community 3D compiler.  Anything
    unmarked or partially marked survives redraw and compile cleanup.
    """

    specifications = building.specifications
    if not isinstance(specifications, dict):
        return None
    marker = specifications.get(COMMUNITY_REPRESENTATION_SPEC_KEY)
    if not isinstance(marker, dict):
        return None
    if marker.get("schema_version") != 1:
        return None
    if marker.get("generator") not in COMMUNITY_BUILDING_GENERATORS:
        return None
    compiled_at = marker.get("compiled_at")
    if not isinstance(compiled_at, str) or not compiled_at.strip():
        return None
    representation_hash = marker.get("representation_hash")
    if not isinstance(representation_hash, str) or len(representation_hash) != 64:
        return None
    try:
        int(representation_hash, 16)
    except ValueError:
        return None
    raw_zone_id = marker.get("zone_id")
    if not isinstance(raw_zone_id, str):
        return None
    try:
        return uuid.UUID(raw_zone_id)
    except ValueError:
        return None


def community_3d_buildings_for_zones(
    buildings: Iterable[Building],
    zone_ids: Iterable[uuid.UUID],
) -> list[Building]:
    """Select only derived buildings owned by one of ``zone_ids``."""

    owned_zone_ids = set(zone_ids)
    return [
        building
        for building in buildings
        if community_3d_source_zone_id(building) in owned_zone_ids
    ]


def stale_community_3d_buildings(
    buildings: Iterable[Building],
    current_building_zone_ids: Iterable[uuid.UUID],
) -> list[Building]:
    """Select derived buildings whose source is no longer a building zone.

    Master-plan redraws can delete a source polygon or reuse its UUID for a
    park/street polygon.  Both cases retire the previously derived Building.
    Callers must therefore pass only zones that still classify as buildings,
    rather than every current zone ID.

    The complete ownership marker validated by
    :func:`community_3d_source_zone_id` remains the deletion boundary.  An
    unmarked or malformed Building is never returned, even when its linked
    source polygon changes kind.
    """

    valid_zone_ids = set(current_building_zone_ids)
    stale: list[Building] = []
    for building in buildings:
        source_zone_id = community_3d_source_zone_id(building)
        if source_zone_id is not None and source_zone_id not in valid_zone_ids:
            stale.append(building)
    return stale
