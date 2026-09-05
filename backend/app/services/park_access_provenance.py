"""Bind a client route snapshot to every current project-zone revision."""

from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID

from fastapi import HTTPException

from app.schemas.park_access import ParkAccessSnapshot

PARK_ACCESS_EVIDENCE = "client_derived_routes_bound_to_server_revisions"


def _utc(value: Any) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def bind_park_access_snapshot(snapshot: ParkAccessSnapshot, zones: Iterable[Any]) -> dict:
    """Validate inventory/revisions only; hashes and route geometry are client claims."""
    current = {str(zone.id): zone for zone in zones}
    source_ids = [str(UUID(source.zoneId)) for source in snapshot.sources]
    if len(source_ids) != len(set(source_ids)) or set(source_ids) != set(current):
        raise HTTPException(status_code=409, detail="Park access source inventory changed; refresh the whole project and capture again.")
    for source in snapshot.sources:
        zone = current[str(UUID(source.zoneId))]
        try:
            matches = _utc(source.updatedAt) == _utc(zone.updated_at)
        except (TypeError, ValueError, AttributeError):
            matches = False
        if not matches:
            raise HTTPException(status_code=409, detail="A park access source zone changed; refresh and capture again.")
    park_ids = [str(park.parkZoneId) for park in snapshot.parks]
    eligible_streets = [str(value) for value in snapshot.eligibleStreetZoneIds]
    if len(eligible_streets) != len(set(eligible_streets)) or any(
        street_id not in current or current[street_id].zone_type != "road" for street_id in eligible_streets
    ):
        raise HTTPException(status_code=409, detail="Park access eligible streets changed; refresh and capture again.")
    if len(park_ids) != len(set(park_ids)) or any(
        park_id not in current or current[park_id].zone_type != "green_space" for park_id in park_ids
    ):
        raise HTTPException(status_code=409, detail="Park access references an unknown or changed park.")
    for park in snapshot.parks:
        connection_ids = [connection.id for connection in park.connections]
        if len(connection_ids) != len(set(connection_ids)) or any(
            str(connection.streetZoneId) not in eligible_streets for connection in park.connections
        ):
            raise HTTPException(status_code=409, detail="Park access references an unknown or duplicate street connection.")
    # Preserve optional-field presence and the submitted cache signatures. They
    # are recorded as evidence, never used to assert server geometric approval.
    return snapshot.model_dump(mode="json", exclude_unset=True)
