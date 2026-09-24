"""Reconnectable Direct 3D image jobs. Reads require current project access."""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import User
from app.models.render_attempt import RenderAttempt
from app.schemas.direct_3d_render import Direct3DRenderRequest
from app.services.render_attempt_storage import read_evidence
from app.services.render_attempts import authorized_attempt, describe_attempt, recover_result, submit_attempt

async def private_response(response: Response):
    response.headers["Cache-Control"] = "private, no-store"


router = APIRouter(dependencies=[Depends(private_response)])


@router.get("/direct-3d-attempts/capabilities")
async def capabilities(user: User = Depends(require_auth)):
    settings = get_settings()
    return {"enabled": settings.direct_3d_jobs_enabled, "images_enabled": settings.direct_3d_images_enabled}


@router.post("/direct-3d-attempts", status_code=202)
async def submit(req: Direct3DRenderRequest,
                 idempotency_key: Annotated[UUID, Header()],
                 user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return describe_attempt(await submit_attempt(db, user, req, str(idempotency_key)))


@router.get("/direct-3d-attempts")
async def recent(project_id: UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    await check_project_permission(project_id, user, db, required="viewer")
    attempts = (await db.scalars(select(RenderAttempt).where(
        RenderAttempt.user_id == user.id, RenderAttempt.project_id == project_id,
    ).order_by(RenderAttempt.created_at.desc()).limit(10))).all()
    return [describe_attempt(attempt) for attempt in attempts]


@router.get("/direct-3d-attempts/{attempt_id}")
async def status(attempt_id: UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return describe_attempt(await authorized_attempt(db, user, attempt_id))


@router.get("/direct-3d-attempts/{attempt_id}/result")
async def result(attempt_id: UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    attempt = await authorized_attempt(db, user, attempt_id)
    if attempt.status != "completed":
        raise HTTPException(409, "This image is not ready yet. Check the saved attempt again.")
    response = await recover_result(attempt)
    request = await read_evidence(attempt, "request")
    if response is None or request is None:
        raise HTTPException(503, "Saved image storage is unavailable. Try recovery later; do not generate again.")
    return {"response": response, "source_image_base64": request["beauty_image_base64"],
            "style": request["style"], "fidelity_policy": request["fidelity_policy"],
            "attempt": describe_attempt(attempt)}
