"""Urban Intelligence DNA API.

POST /urban-dna/zones/{zone_id}/generate  -> create a snapshot + queue the build
GET  /urban-dna/zones/{zone_id}           -> latest snapshot (any status)
GET  /urban-dna/capabilities/{zone_id}    -> which datasets/DNA fields this site's city can produce

All endpoints require auth + project permission (these trigger external API
spend — do NOT follow the unauthenticated boundary-analysis precedent).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import SiteZone, UrbanDnaSnapshot, User
from app.services.city_connector import detect_city, get_connector
from app.services.urban_dna.schema import DNA_SCHEMA_VERSION

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateDnaResponse(BaseModel):
    snapshot_id: str
    zone_id: str
    status: str
    city_id: str


class DnaSnapshotResponse(BaseModel):
    snapshot_id: str
    zone_id: str
    project_id: str
    city_id: str
    status: str  # pending | partial | complete | failed
    dna_schema_version: str
    dna: Optional[dict[str, Any]] = None
    overall_confidence: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CapabilitiesResponse(BaseModel):
    city_id: str
    display_name: str
    datasets: list[dict[str, Any]]
    dna_fields: list[str]


async def _load_zone_checked(
    zone_id: uuid.UUID, user: User, db: AsyncSession, required: str
) -> SiteZone:
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    await check_project_permission(zone.project_id, user, db, required=required)
    return zone


@router.post("/zones/{zone_id}/generate", response_model=GenerateDnaResponse)
async def generate_dna(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Queue Urban DNA generation for a zone (site boundaries give the fullest picture)."""
    zone = await _load_zone_checked(zone_id, user, db, required="editor")

    centroid = to_shape(zone.geometry).centroid
    city_id = detect_city(centroid.x, centroid.y)

    snapshot = UrbanDnaSnapshot(
        id=uuid.uuid4(),  # set explicitly so the id exists before flush
        project_id=zone.project_id,
        zone_id=zone.id,
        city_id=city_id,
        dna_schema_version=DNA_SCHEMA_VERSION,
        status="pending",
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    from app.tasks.urban_dna import generate_urban_dna

    generate_urban_dna.delay(str(snapshot.id))
    logger.info("Queued urban DNA build %s for zone %s (city=%s)", snapshot.id, zone_id, city_id)

    return GenerateDnaResponse(
        snapshot_id=str(snapshot.id),
        zone_id=str(zone.id),
        status=snapshot.status,
        city_id=city_id,
    )


@router.get("/zones/{zone_id}", response_model=DnaSnapshotResponse)
async def get_latest_dna(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Latest DNA snapshot for a zone, whatever its status (pending/partial/complete/failed)."""
    zone = await _load_zone_checked(zone_id, user, db, required="viewer")

    result = await db.execute(
        select(UrbanDnaSnapshot)
        .where(UrbanDnaSnapshot.zone_id == zone.id)
        .order_by(UrbanDnaSnapshot.created_at.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No DNA snapshot for this zone yet")

    return DnaSnapshotResponse(
        snapshot_id=str(snapshot.id),
        zone_id=str(snapshot.zone_id),
        project_id=str(snapshot.project_id),
        city_id=snapshot.city_id,
        status=snapshot.status,
        dna_schema_version=snapshot.dna_schema_version,
        dna=snapshot.dna,
        overall_confidence=float(snapshot.overall_confidence) if snapshot.overall_confidence is not None else None,
        error=snapshot.error,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
    )


@router.get("/capabilities/{zone_id}", response_model=CapabilitiesResponse)
async def get_capabilities(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Which datasets and DNA fields the detected city can produce for this zone."""
    zone = await _load_zone_checked(zone_id, user, db, required="viewer")

    centroid = to_shape(zone.geometry).centroid
    connector = get_connector(detect_city(centroid.x, centroid.y))

    datasets = [
        {
            "id": spec.id,
            "name": spec.name,
            "priority": spec.priority,
            "geometry_type": spec.geometry_type,
            "source_url": spec.source_url,
            "dna_fields": list(spec.dna_fields),
        }
        for spec in sorted(connector.datasets.values(), key=lambda s: s.priority)
    ]
    return CapabilitiesResponse(
        city_id=connector.city_id,
        display_name=connector.display_name,
        datasets=datasets,
        dna_fields=sorted(connector.capabilities()),
    )
