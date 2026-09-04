"""
Annotation/comment API endpoints for 3D scene objects.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import Annotation, Building, User
from app.schemas.schemas import AnnotationCreate, AnnotationResponse, AnnotationUpdate

router = APIRouter()


@router.get("/projects/{project_id}/annotations", response_model=list[AnnotationResponse])
async def list_annotations(
    project_id: uuid.UUID,
    resolved: bool | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """List all annotations for a project."""
    await check_project_permission(project_id, user, db)
    query = select(Annotation).where(Annotation.project_id == project_id)
    if resolved is not None:
        query = query.where(Annotation.resolved == resolved)
    query = query.order_by(Annotation.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/projects/{project_id}/annotations",
    response_model=AnnotationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_annotation(
    project_id: uuid.UUID,
    annotation_in: AnnotationCreate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a new annotation at a 3D position."""
    await check_project_permission(project_id, user, db, required="editor")
    if annotation_in.building_id:
        result = await db.execute(
            select(Building).where(
                Building.id == annotation_in.building_id,
                Building.project_id == project_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=400, detail="Building does not belong to this project")

    annotation = Annotation(
        project_id=project_id,
        building_id=annotation_in.building_id,
        author_id=user.id,
        text=annotation_in.text,
        position_x=annotation_in.position_x,
        position_y=annotation_in.position_y,
        position_z=annotation_in.position_z,
    )
    db.add(annotation)
    await db.flush()
    await db.refresh(annotation)
    return annotation


@router.put("/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation_id: uuid.UUID,
    annotation_in: AnnotationUpdate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update an annotation (edit text or resolve)."""
    result = await db.execute(select(Annotation).where(Annotation.id == annotation_id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    await check_project_permission(annotation.project_id, user, db, required="editor")

    for field, value in annotation_in.model_dump(exclude_unset=True).items():
        setattr(annotation, field, value)

    await db.flush()
    await db.refresh(annotation)
    return annotation


@router.delete("/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete an annotation."""
    result = await db.execute(select(Annotation).where(Annotation.id == annotation_id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    await check_project_permission(annotation.project_id, user, db, required="editor")

    await db.delete(annotation)
