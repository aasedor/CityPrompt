"""Bind terrain evidence to the current retained boundary before provider spend."""

from datetime import datetime, timezone
from math import isclose
from typing import Any, Iterable

from fastapi import HTTPException
from geoalchemy2.shape import to_shape

from app.schemas.shared_ground import SharedGroundSnapshot

SHARED_GROUND_EVIDENCE = "client_measured_google_mesh_bound_to_server_boundary_revision"


def _utc(value: Any) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def _open_ring(points) -> list[tuple[float, float]]:
    ring = [tuple(point[:2]) for point in points]
    return ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring


def _same_ring(left, right) -> bool:
    # PostGIS/GeoJSON/JavaScript round-trips can differ in the last binary
    # digit. One trillionth of a degree is sub-micrometre noise, not a site
    # edit. Never use relative tolerance on longitude-sized numbers.
    a, b = _open_ring(left), _open_ring(right)
    return len(a) == len(b) and all(
        isclose(x, y, rel_tol=0, abs_tol=1e-12)
        for p, q in zip(a, b) for x, y in zip(p, q)
    )


def bind_shared_ground_snapshot(snapshot: SharedGroundSnapshot, zones: Iterable[Any]) -> dict:
    """Validate boundary identity/geometry/revision. Heights, quality and cache
    signatures remain client measurements; the server does not resample tiles."""
    active = [zone for zone in zones if zone.zone_type == "site_boundary" and bool(getattr(zone, "is_active_boundary", False))]
    valid = len(active) == 1 and str(active[0].id) == str(snapshot.boundaryId)
    if valid:
        boundary = active[0]
        try:
            geometry = boundary.geometry if hasattr(boundary.geometry, "geom_type") else to_shape(boundary.geometry)
            valid = (
                (boundary.properties or {}).get("community_3d_mask_existing_tiles") is False
                and _utc(boundary.updated_at) == _utc(snapshot.boundaryUpdatedAt)
                and geometry.geom_type == "Polygon"
                and not len(geometry.interiors)
                and _same_ring(geometry.exterior.coords, snapshot.boundaryCoordinates)
            )
        except (TypeError, ValueError, AttributeError):
            valid = False
    if not valid:
        raise HTTPException(status_code=409, detail="The retained site boundary changed; refresh the project and capture its ground alignment again.")
    return snapshot.model_dump(mode="json", exclude_unset=True)
