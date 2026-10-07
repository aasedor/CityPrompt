"""Read-only assessment calculation, scoped to the saved active boundary."""

import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field, FiniteFloat
from shapely.geometry import Polygon
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import SiteZone, User
from app.services.site_assessment import AssessmentError, get_site_assessment

router = APIRouter()


class AssessmentRequest(BaseModel):
    coordinates: list[tuple[FiniteFloat, FiniteFloat]] = Field(min_length=3, max_length=1024)


@router.post("/zones/{zone_id}")
async def calculate_site_assessment(
    zone_id: uuid.UUID, request: AssessmentRequest,
    user: User = Depends(require_auth), db: AsyncSession = Depends(get_db),
):
    boundary = (await db.execute(select(SiteZone).where(SiteZone.id == zone_id))).scalar_one_or_none()
    if boundary is None:
        raise HTTPException(404, "Site boundary not found.")
    await check_project_permission(boundary.project_id, user, db, required="viewer")
    if boundary.zone_type != "site_boundary" or not boundary.is_active_boundary:
        raise HTTPException(422, "Select the active site boundary to calculate assessments.")
    site = to_shape(boundary.geometry)
    submitted = Polygon(request.coordinates)
    # Different ring starting vertices are allowed; a pending/outdated save is not.
    if not submitted.is_valid or not site.equals(submitted):
        raise HTTPException(409, "Wait for the boundary to finish saving, then calculate again.")
    try:
        result = await get_site_assessment(site)
    except AssessmentError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (httpx.HTTPError, TimeoutError, ValueError) as exc:
        raise HTTPException(502, "Calgary assessments could not load. Please retry.") from exc
    return {**result, "boundary_id": str(boundary.id)}
