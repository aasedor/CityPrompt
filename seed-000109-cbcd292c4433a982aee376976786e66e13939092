"""Canonical identity for the site boundary that authored a generated plan."""

from __future__ import annotations

import hashlib
from typing import Any

from shapely import normalize, set_precision, to_wkb
from shapely.errors import GEOSException
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


PLAN_BOUNDARY_FINGERPRINT_VERSION = 1
PLAN_BOUNDARY_PRECISION_DEG = 1e-9
PLAN_BOUNDARY_RESTORE_STATE_KEY = "_plan_boundary_restore_state"


def plan_boundary_fingerprint(value: BaseGeometry | dict[str, Any] | None) -> str | None:
    """Return a ring-order-independent fingerprint for one valid 2D boundary.

    A 1e-9 degree grid matches the API's material coordinate-change threshold,
    so harmless serialization noise cannot strand an undo while a real vertex
    move still produces a different identity.
    """

    if value is None:
        return None
    try:
        geometry = value if isinstance(value, BaseGeometry) else shape(value)
        if geometry.is_empty or not geometry.is_valid or geometry.area <= 0:
            return None
        canonical = normalize(set_precision(geometry, PLAN_BOUNDARY_PRECISION_DEG))
        if canonical.is_empty or canonical.area <= 0:
            return None
        payload = to_wkb(
            canonical,
            hex=False,
            byte_order=1,
            output_dimension=2,
            include_srid=False,
        )
    except (GEOSException, KeyError, TypeError, ValueError):
        return None
    return hashlib.sha256(
        f"plan-boundary-v{PLAN_BOUNDARY_FINGERPRINT_VERSION}:".encode("ascii")
        + payload
    ).hexdigest()


def stamp_plan_boundary_identity(
    properties: dict[str, Any] | None,
    *,
    fingerprint: str,
    boundary_zone_id: Any,
    snapshot_id: Any,
) -> dict[str, Any]:
    """Return generated-zone properties bound to one authoritative boundary."""

    stamped = dict(properties or {})
    stamped.update({
        "_plan_boundary_fingerprint": fingerprint,
        "_plan_boundary_zone_id": str(boundary_zone_id),
        "_plan_snapshot_id": str(snapshot_id),
    })
    stamped.pop("_plan_boundary_stale", None)
    stamped.pop("_plan_boundary_changed_at", None)
    return stamped
