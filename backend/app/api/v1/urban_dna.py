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
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import SiteZone, UrbanDnaScenario, UrbanDnaSnapshot, User
from app.services.city_connector import detect_city, get_connector
from app.services.planning_agents.scenarios import (
    BASELINE_SCENARIO_ID,
    DEFAULT_SCENARIO_IDS,
    SCENARIO_PRESETS,
)
from app.services.planning_agents.schemas import PARAMETER_VOCABULARY
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


class CreateScenariosRequest(BaseModel):
    scenario_ids: list[str] = Field(default_factory=lambda: list(DEFAULT_SCENARIO_IDS))


class ScenarioRowResponse(BaseModel):
    id: str
    snapshot_id: str
    scenario_id: str
    label: str
    status: str
    payload: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ScenarioListResponse(BaseModel):
    snapshot_id: Optional[str] = None
    scenarios: list[ScenarioRowResponse] = Field(default_factory=list)
    available_presets: list[dict[str, str]] = Field(default_factory=list)


def _scenario_row_response(row: UrbanDnaScenario) -> ScenarioRowResponse:
    return ScenarioRowResponse(
        id=str(row.id),
        snapshot_id=str(row.snapshot_id),
        scenario_id=row.scenario_id,
        label=row.label,
        status=row.status,
        payload=row.payload,
        error=row.error,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _latest_snapshot(zone: SiteZone, db: AsyncSession) -> UrbanDnaSnapshot | None:
    result = await db.execute(
        select(UrbanDnaSnapshot)
        .where(UrbanDnaSnapshot.zone_id == zone.id)
        .order_by(UrbanDnaSnapshot.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post("/zones/{zone_id}/scenarios", response_model=ScenarioListResponse)
async def create_scenarios(
    zone_id: uuid.UUID,
    req: CreateScenariosRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Queue planning-agent scenario runs against the zone's latest DNA snapshot.

    Runs are chained so the as_of_right baseline completes before the scenarios
    that diff against it.
    """
    zone = await _load_zone_checked(zone_id, user, db, required="editor")
    snapshot = await _latest_snapshot(zone, db)
    if snapshot is None or snapshot.status not in ("complete", "partial") or not snapshot.dna:
        raise HTTPException(status_code=409, detail="Generate the Urban DNA for this zone first")

    unknown = [s for s in req.scenario_ids if s not in SCENARIO_PRESETS]
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unknown scenario presets: {unknown}")

    # Baseline first so diffs have something to diff against.
    ordered = sorted(set(req.scenario_ids), key=lambda s: (s != BASELINE_SCENARIO_ID, s))
    rows: list[UrbanDnaScenario] = []
    for scenario_id in ordered:
        preset = SCENARIO_PRESETS[scenario_id]
        row = UrbanDnaScenario(
            id=uuid.uuid4(),
            snapshot_id=snapshot.id,
            scenario_id=scenario_id,
            label=preset.label,
            status="pending",
        )
        db.add(row)
        rows.append(row)
    await db.commit()

    from celery import chain

    from app.tasks.urban_dna import run_urban_dna_scenario

    chain(*(run_urban_dna_scenario.si(str(row.id)) for row in rows)).apply_async()
    logger.info("Queued %d scenario runs for zone %s (snapshot %s)", len(rows), zone_id, snapshot.id)

    return ScenarioListResponse(
        snapshot_id=str(snapshot.id),
        scenarios=[_scenario_row_response(row) for row in rows],
        available_presets=[
            {"scenario_id": s.scenario_id, "label": s.label, "description": s.description}
            for s in SCENARIO_PRESETS.values()
        ],
    )


@router.get("/zones/{zone_id}/scenarios", response_model=ScenarioListResponse)
async def list_scenarios(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Scenario runs for the zone's latest snapshot (any status)."""
    zone = await _load_zone_checked(zone_id, user, db, required="viewer")
    snapshot = await _latest_snapshot(zone, db)
    presets = [
        {"scenario_id": s.scenario_id, "label": s.label, "description": s.description}
        for s in SCENARIO_PRESETS.values()
    ]
    if snapshot is None:
        return ScenarioListResponse(available_presets=presets)

    result = await db.execute(
        select(UrbanDnaScenario)
        .where(UrbanDnaScenario.snapshot_id == snapshot.id)
        .order_by(UrbanDnaScenario.created_at.asc())
    )
    rows = result.scalars().all()
    return ScenarioListResponse(
        snapshot_id=str(snapshot.id),
        scenarios=[_scenario_row_response(row) for row in rows],
        available_presets=presets,
    )


class ApplyScenarioResponse(BaseModel):
    zone_id: str
    scenario_id: str
    applied_parameters: dict[str, Any]


@router.post("/scenarios/{scenario_row_id}/apply", response_model=ApplyScenarioResponse)
async def apply_scenario(
    scenario_row_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Write the scenario's PlanParameters onto the boundary zone as planning directives.

    Non-destructive: user-set zone properties are untouched; the directives land
    under properties._urban_dna_directives, which the layout prompts read as a
    PLANNING DIRECTIVES block. Re-applying (or applying another scenario)
    replaces them; deleting the key reverts entirely.
    """
    result = await db.execute(select(UrbanDnaScenario).where(UrbanDnaScenario.id == scenario_row_id))
    row = result.scalar_one_or_none()
    if row is None or row.status != "complete" or not row.payload:
        raise HTTPException(status_code=404, detail="Completed scenario not found")

    snapshot_result = await db.execute(
        select(UrbanDnaSnapshot).where(UrbanDnaSnapshot.id == row.snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot for scenario not found")

    zone = await _load_zone_checked(snapshot.zone_id, user, db, required="editor")

    parameters: dict[str, Any] = {}
    rationales: dict[str, str] = {}
    for path, merged in (row.payload.get("plan_parameters") or {}).items():
        vocab = PARAMETER_VOCABULARY.get(path)
        if vocab is None:
            continue
        parameters[vocab["maps_to"]] = merged.get("value")
        rationales[vocab["maps_to"]] = str(merged.get("rationale", ""))[:200]

    explanation = row.payload.get("explanation") or {}
    properties = dict(zone.properties or {})
    properties["_urban_dna_directives"] = {
        "scenario_row_id": str(row.id),
        "scenario_id": row.scenario_id,
        "label": row.label,
        "applied_at": datetime.utcnow().isoformat() + "Z",
        "parameters": parameters,
        "rationales": rationales,
        "narrative": explanation.get("narrative", ""),
    }
    zone.properties = properties
    await db.commit()

    logger.info("Applied scenario %s to zone %s (%d parameters)", row.scenario_id, zone.id, len(parameters))
    return ApplyScenarioResponse(
        zone_id=str(zone.id),
        scenario_id=row.scenario_id,
        applied_parameters=parameters,
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
