"""On-demand reports, with durable student reasoning and no design side effects."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import (
    Building,
    PolicyChunk,
    PolicyDocument,
    Project,
    SiteZone,
    UrbanDnaSnapshot,
    User,
)
from app.models.reference_layers import ReferenceLayer
from app.models.student_report import StudentPlanningReport
from app.schemas.student_report import StudentDecisionRequest, StudentReportRequest
from app.schemas.park_access import ParkAccessSnapshot
from app.services.park_access_provenance import bind_park_access_snapshot
from app.services.policy_intelligence.retrieval import ChunkRecord
from app.services.student_report import (
    analyze_snapshot,
    boundary_record,
    build_snapshot,
    digest,
    report_html,
    select_policy_sources,
)

router = APIRouter(prefix="/student-reports", tags=["student reports"])


async def _snapshot(db: AsyncSession, project_id: uuid.UUID, zone_ids: list[str] | None,
                    park_access: ParkAccessSnapshot | None = None) -> dict:
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalar_one_or_none()
    if project is None:
        raise HTTPException(404, "Project not found")
    zones = list((await db.execute(select(SiteZone).where(SiteZone.project_id == project_id))).scalars().all())
    buildings = list((await db.execute(select(Building).where(Building.project_id == project_id))).scalars().all())
    references = list(
        (await db.execute(select(ReferenceLayer).where(ReferenceLayer.project_id == project_id))).scalars().all()
    )
    snapshot = build_snapshot(project, zones, buildings, references, zone_ids)
    if park_access is not None:
        snapshot["park_access_snapshot"] = bind_park_access_snapshot(park_access, zones)
    return snapshot


async def _policy_sources(db: AsyncSession, project_id: uuid.UUID, snapshot: dict) -> list[dict]:
    boundary = boundary_record(snapshot)
    if not boundary or boundary["id"] == "project-boundary":
        return []
    dna_row = (
        await db.execute(
            select(UrbanDnaSnapshot)
            .where(
                UrbanDnaSnapshot.project_id == project_id,
                UrbanDnaSnapshot.zone_id == uuid.UUID(boundary["id"]),
                UrbanDnaSnapshot.status.in_(["complete", "partial"]),
            )
            .order_by(UrbanDnaSnapshot.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if dna_row is None or not dna_row.city_id or dna_row.city_id == "osm":
        return []
    # Stored documents only. No external research, generation, or inferred city.
    results = (
        await db.execute(
            select(PolicyChunk, PolicyDocument)
            .join(PolicyDocument, PolicyDocument.id == PolicyChunk.policy_document_id)
            .where(
                PolicyDocument.city == dna_row.city_id,
                PolicyDocument.status == "active",
                PolicyDocument.repealed_date.is_(None),
            )
            .order_by(PolicyDocument.id, PolicyChunk.page_start)
            .limit(3000)
        )
    ).all()
    records = [
        ChunkRecord(
            chunk_id=str(chunk.id),
            document_slug=document.slug,
            document_title=document.title,
            section_label=chunk.section_label,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            text=chunk.text,
            source_url=document.source_url,
        )
        for chunk, document in results
    ]
    land_use = ((dna_row.dna or {}).get("land_use") or {}).get("fields") or {}
    facts = {key: (land_use.get(key) or {}).get("value") for key in ("districts", "lap_name", "community_name")}
    sources = select_policy_sources(records, facts)
    for source in sources:
        source["context_snapshot_id"] = str(dna_row.id)
        source["context_created_at"] = dna_row.created_at.isoformat()
    return sources


def _plan_version(snapshot: dict) -> str:
    # Route evidence belongs to this report; freshness still compares the complete
    # saved design so later reads need no browser-derived geometry.
    return digest({key: value for key, value in snapshot.items() if key != "park_access_snapshot"})


def _view(row: StudentPlanningReport, current: dict) -> dict:
    return {
        "id": str(row.id),
        "project_id": str(row.project_id),
        "project_name": row.snapshot["project_name"],
        "requested_by_name": row.requested_by_name,
        "created_at": row.created_at.isoformat(),
        "plan_version": row.plan_version,
        "is_stale": _plan_version(current) != row.plan_version,
        "analysis": row.analysis,
        "decisions": row.decisions or {},
        "response_revision": row.response_revision,
        "scope_zone_ids": row.snapshot.get("scope_zone_ids"),
    }


async def _authorized_report(
    report_id: uuid.UUID, user: User, db: AsyncSession, *, editor: bool = False
) -> StudentPlanningReport:
    query = select(StudentPlanningReport).where(StudentPlanningReport.id == report_id)
    if editor:
        query = query.with_for_update()
    row = (await db.execute(query)).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "Report not found")
    await check_project_permission(row.project_id, user, db, required="editor" if editor else "viewer")
    return row


@router.get("/project/{project_id}")
async def latest_report(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    await check_project_permission(project_id, user, db, required="viewer")
    row = (
        await db.execute(
            select(StudentPlanningReport)
            .where(StudentPlanningReport.project_id == project_id)
            .order_by(StudentPlanningReport.created_at.desc(), StudentPlanningReport.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return _view(row, await _snapshot(db, project_id, row.snapshot.get("scope_zone_ids")))


@router.get("/project/{project_id}/history")
async def report_history(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    await check_project_permission(project_id, user, db, required="viewer")
    rows = (
        (
            await db.execute(
                select(StudentPlanningReport)
                .where(StudentPlanningReport.project_id == project_id)
                .order_by(
                    StudentPlanningReport.created_at.desc(),
                    StudentPlanningReport.id.desc(),
                )
                .limit(100)
            )
        )
        .scalars()
        .all()
    )
    return [
        {
            "id": str(row.id),
            "created_at": row.created_at.isoformat(),
            "plan_version": row.plan_version,
            "requested_by_name": row.requested_by_name,
        }
        for row in rows
    ]


@router.post("/project/{project_id}", status_code=201)
async def create_report(
    project_id: uuid.UUID,
    request: StudentReportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    await check_project_permission(project_id, user, db, required="editor")
    ids = [str(value) for value in request.zone_ids] if request.zone_ids is not None else None
    snapshot = await _snapshot(db, project_id, ids, request.park_access_snapshot)
    if ids is not None and set(ids) - {zone["id"] for zone in snapshot["zones"]}:
        raise HTTPException(
            409,
            "The selected proposal changed. Refresh the project before requesting a report.",
        )
    sources = await _policy_sources(db, project_id, snapshot)
    row = StudentPlanningReport(
        id=uuid.uuid4(),
        project_id=project_id,
        requested_by=user.id,
        requested_by_name=user.full_name or user.email,
        plan_version=_plan_version(snapshot),
        snapshot=snapshot,
        analysis=analyze_snapshot(snapshot, sources),
        decisions={},
        decision_history=[],
        response_revision=0,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    await db.flush()
    # A new analysis creates a new report. Previous reasoning remains attached
    # to its original snapshot; never silently copy it onto a changed design.
    return _view(row, snapshot)


@router.get("/{report_id}")
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    row = await _authorized_report(report_id, user, db)
    return _view(row, await _snapshot(db, row.project_id, row.snapshot.get("scope_zone_ids")))


@router.patch("/{report_id}/findings/{finding_id}")
async def respond_to_finding(
    report_id: uuid.UUID,
    finding_id: str,
    request: StudentDecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    row = await _authorized_report(report_id, user, db, editor=True)
    if finding_id not in {finding["id"] for finding in row.analysis["findings"]}:
        raise HTTPException(404, "Finding not found in this report")
    if request.expected_revision != row.response_revision:
        raise HTTPException(
            409,
            "A teammate updated this report. Refresh it before saving your response; keep your written reasoning.",
        )
    decision = {
        "choice": request.choice,
        "rationale": request.rationale,
        "follow_through": request.follow_through.strip(),
        "author_id": str(user.id),
        "author_name": user.full_name or user.email,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    row.decisions = {**(row.decisions or {}), finding_id: decision}
    row.decision_history = [
        *(row.decision_history or []),
        {"finding_id": finding_id, **decision},
    ]
    row.response_revision += 1
    await db.flush()
    return _view(row, await _snapshot(db, row.project_id, row.snapshot.get("scope_zone_ids")))


@router.get("/{report_id}/export", response_class=HTMLResponse)
async def export_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    row = await _authorized_report(report_id, user, db)
    current = await _snapshot(db, row.project_id, row.snapshot.get("scope_zone_ids"))
    return HTMLResponse(
        report_html(_view(row, current), row.snapshot, row.decision_history or []),
        headers={
            "Content-Disposition": f'attachment; filename="planning-report-{row.id}.html"',
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'",
        },
    )
