"""
Project sharing API endpoints — invite by email and public links.
"""

import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import (
    check_project_permission,
    create_project_asset_ticket,
    require_auth,
)
from app.models.models import Project, ProjectShare, User
from app.schemas.schemas import (
    ProjectResponse,
    PublicLinkResponse,
    ShareProjectRequest,
    ShareResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_project_as_owner(
    project_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> Project:
    """Load a project and verify the user is the owner."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can manage sharing")
    return project


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/projects/{project_id}/shares",
    response_model=ShareResponse,
    status_code=status.HTTP_201_CREATED,
)
async def share_project(
    project_id: uuid.UUID,
    body: ShareProjectRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Share a project with another user by email."""
    await _get_project_as_owner(project_id, user, db)

    # Check if already shared with this email
    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.project_id == project_id,
            ProjectShare.email == body.email,
            ProjectShare.is_public_link.is_(False),
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        # Update permission instead of duplicating
        existing.permission = body.permission
        await db.flush()
        await db.refresh(existing)
        return existing

    share = ProjectShare(
        project_id=project_id,
        email=body.email,
        # Email labels the intended recipient; possession of the invitation
        # secret, not an unverified registration email, redeems membership.
        user_id=None,
        permission=body.permission,
        invite_token=secrets.token_urlsafe(32),
    )
    db.add(share)
    await db.flush()
    await db.refresh(share)
    return share


@router.get("/projects/{project_id}/shares", response_model=list[ShareResponse])
async def list_shares(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all shares for a project (owner only)."""
    await _get_project_as_owner(project_id, user, db)

    result = await db.execute(
        select(ProjectShare).where(ProjectShare.project_id == project_id).order_by(ProjectShare.created_at)
    )
    return result.scalars().all()


@router.delete("/projects/{project_id}/shares/{share_id:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(
    project_id: uuid.UUID,
    share_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a project share."""
    await _get_project_as_owner(project_id, user, db)

    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.id == share_id,
            ProjectShare.project_id == project_id,
        )
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    await db.delete(share)


@router.post(
    "/projects/{project_id}/shares/public-link",
    response_model=PublicLinkResponse,
)
async def create_public_link(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate a public share link for the project."""
    await _get_project_as_owner(project_id, user, db)

    # Check if a public link already exists
    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.project_id == project_id,
            ProjectShare.is_public_link.is_(True),
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return PublicLinkResponse(
            token=existing.invite_token,
            url=f"/shared/{existing.invite_token}",
        )

    token = secrets.token_urlsafe(32)
    share = ProjectShare(
        project_id=project_id,
        permission="viewer",
        is_public_link=True,
        invite_token=token,
    )
    db.add(share)
    await db.flush()

    return PublicLinkResponse(token=token, url=f"/shared/{token}")


@router.delete("/projects/{project_id}/shares/public-link", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_public_link(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Revoke the public share link."""
    await _get_project_as_owner(project_id, user, db)

    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.project_id == project_id,
            ProjectShare.is_public_link.is_(True),
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)


@router.get("/shared/{token}", response_model=ProjectResponse)
async def get_shared_project(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Read a project through an explicitly public, revocable share link."""
    result = await db.execute(
        select(ProjectShare).where(
            ProjectShare.invite_token == token,
            ProjectShare.is_public_link.is_(True),
        )
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Invalid or expired share link")

    result = await db.execute(
        select(Project)
        .options(selectinload(Project.buildings), selectinload(Project.documents))
        .where(Project.id == share.project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from app.api.v1.projects import _project_to_dict

    data = _project_to_dict(project, include_relations=True)
    data["documents"] = []
    for building in data["buildings"]:
        building["generation_prompt"] = None
        building["meshy_task_id"] = None
    return data


@router.get("/invitations/{token}")
async def invitation_details(token: str, db: AsyncSession = Depends(get_db)):
    """Show enough invitation context to sign in; never reveal project contents."""
    result = await db.execute(
        select(ProjectShare, Project.name)
        .join(Project, Project.id == ProjectShare.project_id)
        .where(ProjectShare.invite_token == token, ProjectShare.is_public_link.is_(False))
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Invalid or revoked invitation")
    share, project_name = row
    return {
        "project_name": project_name,
        "email": share.email,
        "permission": share.permission,
        "accepted": share.user_id is not None,
    }


@router.post("/invitations/{token}/accept", response_model=ShareResponse)
async def accept_invitation(
    token: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Bind a secret invitation to its intended account exactly once."""
    result = await db.execute(
        select(ProjectShare)
        .where(ProjectShare.invite_token == token, ProjectShare.is_public_link.is_(False))
        .with_for_update()
    )
    share = result.scalar_one_or_none()
    if share is None:
        raise HTTPException(status_code=404, detail="Invalid or revoked invitation")
    if not share.email or share.email.casefold() != user.email.casefold():
        raise HTTPException(
            status_code=403,
            detail="Sign in with the email address invited to this project",
        )
    if share.user_id is not None and share.user_id != user.id:
        raise HTTPException(status_code=409, detail="This invitation has already been accepted")
    share.user_id = user.id
    await db.flush()
    await db.refresh(share)
    return share


@router.post("/projects/{project_id}/asset-ticket")
async def issue_asset_ticket(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="viewer")
    return {
        "asset_ticket": create_project_asset_ticket(project_id, user.id),
        "expires_in": 900,
    }


@router.get("/shared-with-me", response_model=list[ShareResponse])
async def list_shared_with_me(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all projects shared with the current user."""
    result = await db.execute(
        select(ProjectShare).where(ProjectShare.user_id == user.id).order_by(ProjectShare.created_at.desc())
    )
    return result.scalars().all()
