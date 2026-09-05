import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import is_admin_or_above, require_auth
from app.models.models import Building, MasterPlan2DOption, Project, ProjectShare, SiteZone, User
from app.schemas.schemas import (
    MasterPlan2DExportResponse,
    MasterPlan2DGenerateRequest,
    MasterPlan2DGenerateResponse,
    MasterPlan2DOptionResponse,
    MasterPlan2DSelectResponse,
    MasterPlan3DGenerateRequest,
    MasterPlan3DGenerateResponse,
)
from app.services.master_plan_2d import MasterPlan2DService, STYLE_LABELS

router = APIRouter()
logger = logging.getLogger(__name__)


async def _get_project(project_id: uuid.UUID, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _require_project_access(project: Project, user: User, db: AsyncSession, editor: bool) -> None:
    if project.owner_id == user.id or is_admin_or_above(user):
        return
    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.project_id == project.id,
            ProjectShare.user_id == user.id,
        )
    )
    share = result.scalar_one_or_none()
    if share is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    if editor and share.permission != "editor":
        raise HTTPException(status_code=403, detail="Editor access required")


async def _load_project_geometry(project_id: uuid.UUID, db: AsyncSession) -> tuple[list[SiteZone], list[Building]]:
    zones_result = await db.execute(
        select(SiteZone).where(SiteZone.project_id == project_id).order_by(SiteZone.sort_order, SiteZone.created_at)
    )
    buildings_result = await db.execute(select(Building).where(Building.project_id == project_id))
    return list(zones_result.scalars().all()), list(buildings_result.scalars().all())


def _asset_urls(option: MasterPlan2DOption) -> dict[str, str | None]:
    metadata = option.metadata_ or {}
    assets = metadata.get("assets") or {}
    return {
        "preview_png_url": assets.get("preview_png_url") or option.preview_url,
        "full_png_url": assets.get("full_png_url"),
        "svg_url": assets.get("svg_url"),
        "plan_preview_png_url": assets.get("plan_preview_png_url"),
        "plan_full_png_url": assets.get("plan_full_png_url"),
        "plan_svg_url": assets.get("plan_svg_url"),
        "debug_png_url": assets.get("debug_png_url"),
    }


def _option_response(option: MasterPlan2DOption) -> MasterPlan2DOptionResponse:
    assets = _asset_urls(option)
    return MasterPlan2DOptionResponse(
        id=option.id,
        project_id=option.project_id,
        label=option.label,
        style_preset=option.style_preset,
        style_name=STYLE_LABELS.get(option.style_preset, option.style_preset.replace("_", " ").title()),
        variant_index=option.variant_index,
        preview_url=option.preview_url,
        preview_png_url=assets["preview_png_url"] or option.preview_url,
        full_png_url=assets["full_png_url"],
        svg_url=assets["svg_url"],
        plan_preview_png_url=assets["plan_preview_png_url"],
        plan_full_png_url=assets["plan_full_png_url"],
        plan_svg_url=assets["plan_svg_url"],
        debug_png_url=assets["debug_png_url"],
        is_selected=option.is_selected,
        metadata=option.metadata_,
        created_at=option.created_at,
    )


@router.get("/projects/{project_id}/options", response_model=list[MasterPlan2DOptionResponse])
async def list_options(project_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    await _require_project_access(project, user, db, editor=False)
    options = await MasterPlan2DService.list_options(db, project_id)
    return [_option_response(option) for option in options]


@router.post("/projects/{project_id}/generate", response_model=MasterPlan2DGenerateResponse)
async def generate_options(
    project_id: uuid.UUID,
    request: MasterPlan2DGenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project(project_id, db)
    await _require_project_access(project, user, db, editor=True)
    zones, buildings = await _load_project_geometry(project_id, db)
    try:
        options = await MasterPlan2DService.generate_options(db, project, zones, buildings, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MasterPlan2DGenerateResponse(
        project_id=str(project_id), options=[_option_response(option) for option in options]
    )


@router.post("/projects/{project_id}/regenerate", response_model=MasterPlan2DGenerateResponse)
async def regenerate_options(
    project_id: uuid.UUID,
    request: MasterPlan2DGenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await generate_options(project_id, request, user, db)


@router.post("/options/{option_id}/select", response_model=MasterPlan2DSelectResponse)
async def select_option(option_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MasterPlan2DOption).where(MasterPlan2DOption.id == option_id))
    option = result.scalar_one_or_none()
    if option is None:
        raise HTTPException(status_code=404, detail="2D master plan option not found")
    project = await _get_project(option.project_id, db)
    await _require_project_access(project, user, db, editor=True)
    try:
        selected = await MasterPlan2DService.select_option(db, option.project_id, option_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MasterPlan2DSelectResponse(
        status="selected", project_id=str(selected.project_id), selected_option_id=str(selected.id)
    )


@router.post("/options/{option_id}/generate-3d", response_model=MasterPlan3DGenerateResponse)
async def generate_option_3d_packages(
    option_id: uuid.UUID,
    request: MasterPlan3DGenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MasterPlan2DOption).where(MasterPlan2DOption.id == option_id))
    option = result.scalar_one_or_none()
    if option is None:
        raise HTTPException(status_code=404, detail="2D master plan option not found")
    project = await _get_project(option.project_id, db)
    await _require_project_access(project, user, db, editor=False)
    zones, buildings = await _load_project_geometry(option.project_id, db)
    try:
        payload = await MasterPlan2DService.generate_3d_render_packages(
            db, project, option_id, zones, buildings, request
        )
        return MasterPlan3DGenerateResponse(**payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("3D package generation failed for option %s", option_id)
        raise HTTPException(
            status_code=422, detail="Failed to prepare 3D render packages due to invalid geometry or metadata payload."
        ) from exc


@router.get("/options/{option_id}/export", response_model=MasterPlan2DExportResponse)
async def export_option(
    option_id: uuid.UUID,
    width: int = Query(4200, ge=3000, le=5000),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MasterPlan2DOption).where(MasterPlan2DOption.id == option_id))
    option = result.scalar_one_or_none()
    if option is None:
        raise HTTPException(status_code=404, detail="2D master plan option not found")
    project = await _get_project(option.project_id, db)
    await _require_project_access(project, user, db, editor=False)
    try:
        export = await MasterPlan2DService.export_option(db, option_id, width)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    selected_option = export["option"]
    return MasterPlan2DExportResponse(
        option_id=str(selected_option.id),
        project_id=str(selected_option.project_id),
        label=selected_option.label,
        style_preset=selected_option.style_preset,
        style_name=export["style_name"],
        width=export["width"],
        height=export["height"],
        svg=export["svg"],
        preview_png_url=export.get("preview_png_url"),
        full_png_url=export.get("full_png_url"),
        svg_url=export.get("svg_url"),
        plan_preview_png_url=export.get("plan_preview_png_url"),
        plan_full_png_url=export.get("plan_full_png_url"),
        plan_svg_url=export.get("plan_svg_url"),
        debug_png_url=export.get("debug_png_url"),
    )
