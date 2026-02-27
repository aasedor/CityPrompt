"""
Admin API endpoints for platform management.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_admin
from app.models.models import Building, Document, Project, User
from app.schemas.schemas import (
    AdminDashboardStats,
    AdminProjectListResponse,
    AdminUserListResponse,
    AdminUserUpdate,
)

router = APIRouter()


@router.get("/stats", response_model=AdminDashboardStats)
async def get_admin_stats(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get platform-wide statistics."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (
        await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))
    ).scalar() or 0
    total_projects = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    total_buildings = (await db.execute(select(func.count(Building.id)))).scalar() or 0
    total_documents = (await db.execute(select(func.count(Document.id)))).scalar() or 0

    # Users by role
    role_rows = (
        await db.execute(select(User.role, func.count(User.id)).group_by(User.role))
    ).all()
    users_by_role = {row[0]: row[1] for row in role_rows}

    # Projects by status
    status_rows = (
        await db.execute(
            select(Project.status, func.count(Project.id)).group_by(Project.status)
        )
    ).all()
    projects_by_status = {row[0]: row[1] for row in status_rows}

    return AdminDashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_projects=total_projects,
        total_buildings=total_buildings,
        total_documents=total_documents,
        users_by_role=users_by_role,
        projects_by_status=projects_by_status,
    )


@router.get("/users", response_model=list[AdminUserListResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None, pattern="^(viewer|editor|admin)$"),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users with optional search and role filter."""
    query = select(
        User,
        func.count(Project.id).label("project_count"),
    ).outerjoin(Project, Project.owner_id == User.id).group_by(User.id)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(User.email.ilike(pattern), User.full_name.ilike(pattern))
        )
    if role:
        query = query.where(User.role == role)

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    rows = (await db.execute(query)).all()

    return [
        AdminUserListResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
            project_count=count,
        )
        for u, count in rows
    ]


@router.put("/users/{user_id}", response_model=AdminUserListResponse)
async def update_user(
    user_id: uuid.UUID,
    update: AdminUserUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's role, active status, or name."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion and self-deactivation
    if target.id == user.id:
        if update.role is not None and update.role != user.role:
            raise HTTPException(
                status_code=400, detail="Cannot change your own role"
            )
        if update.is_active is not None and not update.is_active:
            raise HTTPException(
                status_code=400, detail="Cannot deactivate your own account"
            )

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)

    await db.flush()
    await db.refresh(target)

    # Get project count
    count_result = await db.execute(
        select(func.count(Project.id)).where(Project.owner_id == target.id)
    )
    project_count = count_result.scalar() or 0

    return AdminUserListResponse(
        id=target.id,
        email=target.email,
        full_name=target.full_name,
        role=target.role,
        is_active=target.is_active,
        created_at=target.created_at,
        project_count=project_count,
    )


@router.get("/projects", response_model=list[AdminProjectListResponse])
async def list_all_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    project_status: Optional[str] = Query(
        None, alias="status", pattern="^(draft|processing|ready|archived)$"
    ),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all projects with owner info and optional filters."""
    query = (
        select(
            Project,
            User.email.label("owner_email"),
            User.full_name.label("owner_name"),
            func.count(Building.id).label("building_count"),
        )
        .join(User, User.id == Project.owner_id)
        .outerjoin(Building, Building.project_id == Project.id)
        .group_by(Project.id, User.email, User.full_name)
    )

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(Project.name.ilike(pattern), User.email.ilike(pattern))
        )
    if project_status:
        query = query.where(Project.status == project_status)

    query = query.order_by(Project.updated_at.desc()).offset(skip).limit(limit)
    rows = (await db.execute(query)).all()

    return [
        AdminProjectListResponse(
            id=proj.id,
            name=proj.name,
            description=proj.description,
            status=proj.status,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
            owner_id=proj.owner_id,
            owner_email=email,
            owner_name=name,
            building_count=bcount,
        )
        for proj, email, name, bcount in rows
    ]
