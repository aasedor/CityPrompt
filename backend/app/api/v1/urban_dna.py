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
from datetime import datetime, timedelta, timezone
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

    Runs dispatch independently (no chain): the as_of_right baseline starts
    immediately and the others start after a delay so the diff baseline usually
    lands first; a slow baseline degrades to a BASELINE_UNAVAILABLE info note.
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

    from app.tasks.urban_dna import run_urban_dna_scenario

    # Independent dispatch (NOT a celery chain): a killed baseline task must not
    # strand the other scenarios in 'pending' forever. Non-baseline runs start
    # after a delay so the as_of_right diff baseline usually lands first; if it
    # hasn't, the run proceeds with a BASELINE_UNAVAILABLE info warning.
    for index, row in enumerate(rows):
        countdown = 0 if row.scenario_id == BASELINE_SCENARIO_ID else 75 + index * 10
        run_urban_dna_scenario.apply_async(args=[str(row.id)], countdown=countdown)
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
    # Authorization comes BEFORE any status detail (existence-oracle hygiene):
    # the same 404 for missing, unauthorized-project, and not-yet-complete rows.
    if row is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    snapshot_result = await db.execute(
        select(UrbanDnaSnapshot).where(UrbanDnaSnapshot.id == row.snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        zone = await _load_zone_checked(snapshot.zone_id, user, db, required="editor")
    except HTTPException as exc:
        if exc.status_code in (403, 404):
            # Existence-oracle hygiene: a non-member must get the same 404 a
            # nonexistent scenario id gets, not a distinguishable 403.
            raise HTTPException(status_code=404, detail="Scenario not found")
        raise

    if row.status != "complete" or not row.payload:
        raise HTTPException(status_code=404, detail="Scenario not found")

    latest = await _latest_snapshot(zone, db)
    snapshot_superseded = latest is not None and latest.id != snapshot.id

    parameters: dict[str, Any] = {}
    rationales: dict[str, str] = {}
    for path, merged in (row.payload.get("plan_parameters") or {}).items():
        vocab = PARAMETER_VOCABULARY.get(path)
        if vocab is None:
            continue
        value = merged.get("value")
        # LLM-derived values are replayed into render prompts — cap every shape.
        # The runner's quirk-decode path can emit lists/dicts past the tool schema.
        if isinstance(value, str):
            value = value[:400]
        elif value is not None and not isinstance(value, (int, float, bool)):
            value = str(value)[:400]
        parameters[vocab["maps_to"]] = value
        rationales[vocab["maps_to"]] = str(merged.get("rationale", ""))[:200]

    explanation = row.payload.get("explanation") or {}
    properties = dict(zone.properties or {})
    properties["_urban_dna_directives"] = {
        "scenario_row_id": str(row.id),
        "scenario_id": row.scenario_id,
        "snapshot_id": str(row.snapshot_id),
        "snapshot_superseded": snapshot_superseded,
        "label": row.label,
        "applied_at": datetime.now().astimezone().isoformat(),
        "parameters": parameters,
        "rationales": rationales,
        "narrative": str(explanation.get("narrative", ""))[:600],
    }
    zone.properties = properties
    await db.commit()

    logger.info("Applied scenario %s to zone %s (%d parameters)", row.scenario_id, zone.id, len(parameters))
    return ApplyScenarioResponse(
        zone_id=str(zone.id),
        scenario_id=row.scenario_id,
        applied_parameters=parameters,
    )


class GeneratePlanRequest(BaseModel):
    locks: list[str] = Field(default_factory=list)  # ["streets"] keeps the drawn network


class GeneratePlanResponse(BaseModel):
    scenario_row_id: str
    status: str
    locks: list[str]


@router.post("/scenarios/{scenario_row_id}/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(
    scenario_row_id: uuid.UUID,
    req: GeneratePlanRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Draw the scenario's plan: streets, blocks, open space and building masses
    as real zones (a toggleable layer), with geometry-derived statistics
    superseding the parameter estimates. locks=["streets"] regenerates around
    the existing street network."""
    result = await db.execute(select(UrbanDnaScenario).where(UrbanDnaScenario.id == scenario_row_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    snapshot_result = await db.execute(
        select(UrbanDnaSnapshot).where(UrbanDnaSnapshot.id == row.snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        await _load_zone_checked(snapshot.zone_id, user, db, required="editor")
    except HTTPException as exc:
        if exc.status_code in (403, 404):
            raise HTTPException(status_code=404, detail="Scenario not found")
        raise

    if row.status != "complete" or not row.payload:
        raise HTTPException(status_code=409, detail="Run the scenario before drawing its plan")

    unknown_locks = [lock for lock in req.locks if lock not in ("streets",)]
    if unknown_locks:
        raise HTTPException(status_code=422, detail=f"Unknown locks: {unknown_locks}")

    existing_plan = row.payload.get("plan") or {}
    if existing_plan.get("status") in ("queued", "drawing"):
        # Concurrent plan tasks delete-and-insert the same zones — corruption.
        # Escape hatch: past the 600s Celery hard limit the worker is dead, not
        # busy — an untimestamped or >15-min-old busy state may be re-queued.
        queued_at = existing_plan.get("queued_at")
        stale = True
        if queued_at:
            try:
                age = datetime.now(timezone.utc) - datetime.fromisoformat(queued_at)
                stale = age > timedelta(minutes=15)
            except ValueError:
                pass
        if not stale:
            raise HTTPException(status_code=409, detail="A plan is already being drawn for this scenario")

    payload = dict(row.payload)
    plan = dict(payload.get("plan") or {})
    plan.update({
        "status": "queued",
        "locks": req.locks,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    })
    payload["plan"] = plan
    row.payload = payload
    await db.commit()

    from app.tasks.urban_dna import generate_scenario_plan

    generate_scenario_plan.delay(str(row.id), req.locks)
    logger.info("Queued plan drawing for scenario %s (locks=%s)", row.id, req.locks)
    return GeneratePlanResponse(scenario_row_id=str(row.id), status="queued", locks=req.locks)


async def _load_plan_context(
    scenario_row_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> tuple[UrbanDnaScenario, UrbanDnaSnapshot, Any, list[dict[str, Any]]]:
    """Shared loader for plan exports (sheet, diagram): scenario row +
    snapshot + authz-checked boundary + the drawn plan zones."""
    from geoalchemy2.shape import to_shape

    result = await db.execute(select(UrbanDnaScenario).where(UrbanDnaScenario.id == scenario_row_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    snapshot_result = await db.execute(
        select(UrbanDnaSnapshot).where(UrbanDnaSnapshot.id == row.snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    try:
        boundary_zone = await _load_zone_checked(snapshot.zone_id, user, db, required="viewer")
    except HTTPException as exc:
        if exc.status_code in (403, 404):
            raise HTTPException(status_code=404, detail="Scenario not found")
        raise
    if not row.payload or (row.payload.get("plan") or {}).get("status") != "complete":
        raise HTTPException(status_code=409, detail="Draw the plan before exporting it")

    zones_result = await db.execute(
        select(SiteZone).where(SiteZone.project_id == snapshot.project_id)
    )
    plan_zones = []
    for zone in zones_result.scalars().all():
        props = zone.properties or {}
        if props.get("_plan_scenario") != row.scenario_id:
            continue
        role = props.get("_plan_role")
        if role not in ("street", "open_space", "building"):
            continue
        shape = to_shape(zone.geometry)
        plan_zones.append({
            "role": role,
            "coordinates": [[float(x), float(y)] for x, y in shape.exterior.coords[:-1]],
            "floors": props.get("floors"),
        })
    return row, snapshot, to_shape(boundary_zone.geometry), plan_zones


@router.get("/scenarios/{scenario_row_id}/plan-sheet")
async def plan_sheet(
    scenario_row_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """The council-ready plan sheet: measurable SVG drawing, derived statistics,
    evaluation/refinement history, trade-offs, citations, assumptions and
    provenance — self-contained printable HTML."""
    from fastapi.responses import HTMLResponse

    from app.services.plan_geometry.plan_sheet import build_plan_sheet

    row, snapshot, boundary_shape, plan_zones = await _load_plan_context(scenario_row_id, user, db)
    sheet = build_plan_sheet(
        scenario_label=row.label,
        scenario_id=row.scenario_id,
        payload=row.payload,
        boundary_wgs84=boundary_shape,
        plan_zones=plan_zones,
        dna=snapshot.dna,
        snapshot_meta={
            "snapshot_id": str(snapshot.id),
            "city_id": snapshot.city_id,
            "overall_confidence": float(snapshot.overall_confidence)
            if snapshot.overall_confidence is not None else None,
        },
    )
    return HTMLResponse(content=sheet)


@router.get("/scenarios/{scenario_row_id}/plan-diagram")
async def plan_diagram(
    scenario_row_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """The drawn plan as an annotation-free flat-color nadir PNG — the
    authoritative-geometry conditioning input for renders, and the layout
    figure in the hearing pack."""
    from fastapi.responses import Response

    from app.services.plan_geometry.plan_diagram import render_plan_diagram_png

    row, _snapshot, boundary_shape, plan_zones = await _load_plan_context(scenario_row_id, user, db)
    png = render_plan_diagram_png(boundary_shape, plan_zones)
    return Response(
        content=png,
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="plan-diagram-{row.scenario_id}.png"'},
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
