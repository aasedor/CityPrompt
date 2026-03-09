"""
Admin API endpoints for platform management.
"""

import asyncio
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.email import send_admin_welcome_email, send_cofounder_welcome_email
from app.core.security import is_admin_or_above, require_admin
from app.models.models import Building, Document, Project, User

logger = logging.getLogger(__name__)
from app.schemas.schemas import (
    AdminBuildingListResponse,
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

    role_rows = (
        await db.execute(select(User.role, func.count(User.id)).group_by(User.role))
    ).all()
    users_by_role = {row[0]: row[1] for row in role_rows}

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
    role: Optional[str] = Query(None, pattern="^(viewer|editor|admin|cofounder)$"),
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
            last_login_at=u.last_login_at,
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

    if target.id == user.id:
        if update.role is not None and update.role != user.role:
            raise HTTPException(
                status_code=400, detail="Cannot change your own role"
            )
        if update.is_active is not None and not update.is_active:
            raise HTTPException(
                status_code=400, detail="Cannot deactivate your own account"
            )

    # Cofounder-only guards for role changes
    if update.role is not None:
        # Only cofounders can set role to admin or cofounder
        if update.role in ("admin", "cofounder") and user.role != "cofounder":
            raise HTTPException(
                status_code=403, detail="Requires cofounder role"
            )
        # Only cofounders can change an admin's or cofounder's role
        if target.role in ("admin", "cofounder") and user.role != "cofounder":
            raise HTTPException(
                status_code=403, detail="Requires cofounder role"
            )

    was_promoted_to_admin = (
        update.role == "admin" and target.role not in ("admin", "cofounder")
    )
    was_promoted_to_cofounder = (
        update.role == "cofounder" and target.role != "cofounder"
    )

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)

    await db.flush()
    await db.refresh(target)

    # Send welcome email to newly promoted admin or cofounder
    email_sent = False
    if was_promoted_to_cofounder:
        settings = get_settings()
        try:
            await send_cofounder_welcome_email(
                to_email=target.email,
                promoted_by_email=user.email,
                login_link=f"{settings.frontend_url}/admin",
            )
            email_sent = True
        except Exception:
            logger.exception("Failed to send cofounder welcome email to %s", target.email)
    elif was_promoted_to_admin:
        settings = get_settings()
        try:
            await send_admin_welcome_email(
                to_email=target.email,
                promoted_by_email=user.email,
                login_link=f"{settings.frontend_url}/admin",
            )
            email_sent = True
        except Exception:
            logger.exception("Failed to send admin welcome email to %s", target.email)

    count_result = await db.execute(
        select(func.count(Project.id)).where(Project.owner_id == target.id)
    )
    project_count = count_result.scalar() or 0

    result_data = AdminUserListResponse(
        id=target.id,
        email=target.email,
        full_name=target.full_name,
        role=target.role,
        is_active=target.is_active,
        created_at=target.created_at,
        last_login_at=target.last_login_at,
        project_count=project_count,
    )

    if (was_promoted_to_admin or was_promoted_to_cofounder) and not email_sent:
        from fastapi.responses import JSONResponse
        data = result_data.model_dump(mode="json")
        data["_email_failed"] = True
        return JSONResponse(content=data)

    return result_data


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user account. Cannot delete yourself."""
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Nobody can delete cofounders
    if target.role == "cofounder":
        raise HTTPException(status_code=403, detail="Cofounders cannot be deleted")

    # Only cofounders can delete admins
    if target.role == "admin" and user.role != "cofounder":
        raise HTTPException(status_code=403, detail="Requires cofounder role")

    await db.delete(target)
    await db.flush()


@router.get("/buildings", response_model=list[AdminBuildingListResponse])
async def list_all_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(
        None, pattern="^(idle|generating|completed|failed)$"
    ),
    engine: Optional[str] = Query(None),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all buildings across all projects with owner info and optional filters."""
    query = (
        select(
            Building,
            Project.name.label("project_name"),
            User.email.label("owner_email"),
        )
        .join(Project, Project.id == Building.project_id)
        .join(User, User.id == Project.owner_id)
    )

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Building.name.ilike(pattern),
                Building.generation_prompt.ilike(pattern),
                Project.name.ilike(pattern),
            )
        )
    if status:
        query = query.where(Building.generation_status == status)
    if engine:
        query = query.where(Building.generation_engine == engine)

    query = query.order_by(Building.created_at.desc()).offset(skip).limit(limit)
    rows = (await db.execute(query)).all()

    return [
        AdminBuildingListResponse(
            id=b.id,
            name=b.name,
            project_id=b.project_id,
            project_name=proj_name,
            owner_email=email,
            generation_status=b.generation_status,
            generation_engine=b.generation_engine,
            architectural_style=b.architectural_style,
            model_url=b.model_url,
            preview_url=b.preview_url,
            generation_prompt=b.generation_prompt,
            created_at=b.created_at,
        )
        for b, proj_name, email in rows
    ]


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


@router.get("/buildings/thumbnail-debug")
async def thumbnail_debug(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Debug endpoint: show thumbnail status for all completed buildings."""
    import httpx

    settings = get_settings()
    result = await db.execute(
        select(
            Building.id,
            Building.name,
            Building.meshy_task_id,
            Building.generation_engine,
            Building.preview_url,
            Building.model_url,
        ).where(Building.generation_status == "completed").order_by(Building.created_at.desc())
    )
    rows = result.all()

    buildings = []
    for bid, name, meshy_id, engine, preview_url, model_url in rows:
        status = "ok" if preview_url and preview_url.startswith("/api/") else "missing"
        if preview_url and not preview_url.startswith("/api/"):
            status = f"stale_url ({preview_url[:60]}...)"

        buildings.append({
            "id": str(bid),
            "name": name,
            "engine": engine,
            "meshy_task_id": meshy_id,
            "preview_url": preview_url,
            "has_model": bool(model_url),
            "thumbnail_status": status,
        })

    ok = sum(1 for b in buildings if b["thumbnail_status"] == "ok")
    missing = sum(1 for b in buildings if b["thumbnail_status"] == "missing")
    stale = sum(1 for b in buildings if b["thumbnail_status"].startswith("stale"))
    with_meshy_id = sum(1 for b in buildings if b["meshy_task_id"] and b["thumbnail_status"] != "ok")

    return {
        "summary": {
            "total": len(buildings),
            "ok": ok,
            "missing": missing,
            "stale": stale,
            "fetchable_from_meshy": with_meshy_id,
        },
        "buildings": buildings,
    }


@router.post("/buildings/backfill-thumbnail-test/{building_id}")
async def backfill_single_thumbnail(
    building_id: uuid.UUID,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Test endpoint: try to fetch thumbnail for ONE building and return detailed results."""
    import httpx

    settings = get_settings()
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    info = {
        "building_id": str(building_id),
        "name": building.name,
        "engine": building.generation_engine,
        "meshy_task_id": building.meshy_task_id,
        "current_preview_url": building.preview_url,
        "model_url": building.model_url[:80] if building.model_url else None,
        "steps": [],
    }

    if not building.meshy_task_id:
        # Try sibling approach
        info["steps"].append("No meshy_task_id — trying sibling lookup")
        if building.model_url:
            sibling_result = await db.execute(
                select(Building.id, Building.preview_url).where(
                    Building.model_url == building.model_url,
                    Building.preview_url.like("/api/%"),
                    Building.id != building_id,
                )
            )
            sibling = sibling_result.first()
            if sibling:
                building.preview_url = sibling.preview_url
                building.preview_status = "completed"
                info["steps"].append(f"Copied from sibling {sibling.id}: {sibling.preview_url}")
                info["result"] = "success_from_sibling"
                return info
            else:
                info["steps"].append("No sibling with valid thumbnail found")

                # Check what siblings exist
                all_siblings = await db.execute(
                    select(Building.id, Building.preview_url, Building.meshy_task_id).where(
                        Building.model_url == building.model_url,
                    )
                )
                info["siblings"] = [
                    {"id": str(s.id), "preview_url": s.preview_url, "meshy_task_id": s.meshy_task_id}
                    for s in all_siblings.all()
                ]
        info["result"] = "no_source_available"
        return info

    # Has meshy_task_id — try fetching from Meshy API
    info["steps"].append(f"Querying Meshy API for task {building.meshy_task_id}")
    headers = {"Authorization": f"Bearer {settings.meshy_api_key}"}
    base = settings.meshy_api_base.rstrip("/")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{base}/openapi/v2/text-to-3d/{building.meshy_task_id}",
            headers=headers,
        )
        info["steps"].append(f"text-to-3d response: {resp.status_code}")

        if resp.status_code == 404:
            resp = await client.get(
                f"{base}/openapi/v2/image-to-3d/{building.meshy_task_id}",
                headers=headers,
            )
            info["steps"].append(f"image-to-3d response: {resp.status_code}")

        if resp.status_code != 200:
            info["result"] = f"meshy_api_error_{resp.status_code}"
            info["response_body"] = resp.text[:500]
            return info

        data = resp.json()
        info["meshy_status"] = data.get("status")
        info["meshy_thumbnail_url"] = data.get("thumbnail_url")
        info["meshy_model_urls"] = list((data.get("model_urls") or {}).keys())

        thumbnail_url = data.get("thumbnail_url")
        if not thumbnail_url:
            info["result"] = "no_thumbnail_in_meshy_response"
            return info

        info["steps"].append(f"Downloading thumbnail from {thumbnail_url[:80]}")
        thumb_resp = await client.get(thumbnail_url)
        info["steps"].append(f"Thumbnail download: {thumb_resp.status_code}, {len(thumb_resp.content)} bytes")

        if thumb_resp.status_code != 200 or len(thumb_resp.content) < 100:
            info["result"] = "thumbnail_download_failed"
            return info

        # Upload to S3
        from app.tasks.processing import _upload_to_storage
        thumb_key = f"projects/{building.project_id}/thumbnails/{building_id}.png"
        _upload_to_storage(thumb_key, thumb_resp.content, "image/png")
        proxy_url = f"/api/v1/files/{thumb_key}"

        building.preview_url = proxy_url
        building.preview_status = "completed"
        info["steps"].append(f"Saved as {proxy_url}")
        info["result"] = "success"

    return info


@router.post("/buildings/{building_id}/upload-thumbnail")
async def upload_building_thumbnail(
    building_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload a rendered thumbnail image for a building (from client-side 3D render)."""
    from app.tasks.processing import _upload_to_storage

    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    contents = await file.read()
    if len(contents) < 100:
        raise HTTPException(status_code=400, detail="Image too small")

    thumb_key = f"projects/{building.project_id}/thumbnails/{building_id}.png"
    _upload_to_storage(thumb_key, contents, "image/png")
    proxy_url = f"/api/v1/files/{thumb_key}"

    building.preview_url = proxy_url
    building.preview_status = "completed"

    return {"status": "ok", "preview_url": proxy_url}


@router.post("/buildings/backfill-thumbnails")
async def backfill_thumbnails(
    background_tasks: BackgroundTasks,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Backfill thumbnails for completed buildings missing preview_url.

    Fetches from Meshy API for buildings with a task ID, then propagates
    thumbnails to sibling buildings that share the same model_url.
    Runs in the background — returns immediately.
    """
    # Find buildings with meshy_task_id that need thumbnails fetched
    result = await db.execute(
        select(Building).where(
            Building.generation_status == "completed",
            Building.meshy_task_id.isnot(None),
            (Building.preview_url.is_(None))
            | (Building.preview_url == "")
            | (~Building.preview_url.like("/api/%")),
        )
    )
    buildings = result.scalars().all()

    # Count all completed buildings without a valid /api/ preview_url
    # (includes siblings with NULL, empty, or stale S3 URLs)
    all_missing_result = await db.execute(
        select(func.count(Building.id)).where(
            Building.generation_status == "completed",
            Building.model_url.isnot(None),
            (Building.preview_url.is_(None))
            | (Building.preview_url == "")
            | (~Building.preview_url.like("/api/%")),
        )
    )
    total_missing = all_missing_result.scalar() or 0

    if not buildings and total_missing == 0:
        return {"status": "nothing_to_do", "queued": 0}

    # Collect IDs to process in background (only buildings with meshy_task_id)
    building_ids = [(str(b.id), b.meshy_task_id, str(b.project_id), b.generation_engine) for b in buildings]

    # Always run — even with 0 Meshy entries, the sibling propagation pass is needed
    background_tasks.add_task(_backfill_thumbnails_task, building_ids)

    return {"status": "started", "queued": total_missing}


def _backfill_thumbnails_task(building_entries: list[tuple[str, str, str, str | None]]):
    """Background task that fetches thumbnails from Meshy/Tripo for existing buildings."""
    import time
    import httpx
    from app.tasks.processing import _get_sync_session, _upload_to_storage

    settings = get_settings()
    session = _get_sync_session()
    success = 0
    failed = 0
    retries_left = 3  # Global retry budget for rate-limit backoff

    # Use a persistent client with connection pooling
    client = httpx.Client(timeout=30.0)
    headers = {"Authorization": f"Bearer {settings.meshy_api_key}"}
    base = settings.meshy_api_base.rstrip("/")

    for i, (building_id, meshy_task_id, project_id, engine) in enumerate(building_entries):
        try:
            if engine == "tripo":
                logger.info(f"Skipping Tripo building {building_id} (no thumbnail API)")
                continue

            # Rate-limit: pause between Meshy API calls
            if i > 0:
                time.sleep(1.0)

            # Try text-to-3D first, fall back to image-to-3D
            resp = client.get(
                f"{base}/openapi/v2/text-to-3d/{meshy_task_id}",
                headers=headers,
            )
            if resp.status_code == 404:
                resp = client.get(
                    f"{base}/openapi/v2/image-to-3d/{meshy_task_id}",
                    headers=headers,
                )

            # Handle rate limiting with backoff
            if resp.status_code == 429 and retries_left > 0:
                retry_after = int(resp.headers.get("Retry-After", "10"))
                logger.warning(f"Rate limited by Meshy, sleeping {retry_after}s ({retries_left} retries left)")
                time.sleep(retry_after)
                retries_left -= 1
                # Retry this one
                resp = client.get(
                    f"{base}/openapi/v2/text-to-3d/{meshy_task_id}",
                    headers=headers,
                )

            if resp.status_code != 200:
                logger.warning(f"Meshy task lookup failed for {meshy_task_id}: {resp.status_code}")
                failed += 1
                continue

            data = resp.json()
            thumbnail_url = data.get("thumbnail_url")
            if not thumbnail_url:
                logger.info(f"No thumbnail_url in Meshy response for task {meshy_task_id}")
                failed += 1
                continue

            # Download thumbnail
            thumb_resp = client.get(thumbnail_url)
            if thumb_resp.status_code != 200:
                logger.warning(f"Failed to download thumbnail for {building_id}: {thumb_resp.status_code}")
                failed += 1
                continue

            thumb_key = f"projects/{project_id}/thumbnails/{building_id}.png"
            _upload_to_storage(thumb_key, thumb_resp.content, "image/png")

            proxy_url = f"/api/v1/files/{thumb_key}"

            building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
            if building:
                building.preview_url = proxy_url
                building.preview_status = "completed"
                session.commit()
                success += 1
                logger.info(f"Backfilled thumbnail for building {building_id} ({success}/{len(building_entries)})")

        except Exception as e:
            logger.warning(f"Failed to backfill thumbnail for building {building_id}: {e}")
            try:
                session.rollback()
            except Exception:
                # Session is broken, create a new one
                try:
                    session.close()
                except Exception:
                    pass
                session = _get_sync_session()
            failed += 1

    client.close()

    # Second pass: propagate thumbnails to sibling buildings that share the same
    # model_url but have no valid preview_url (created via zone propagation).
    # Catches: NULL, empty string, and stale S3 URLs that don't start with /api/
    propagated = 0
    try:
        siblings = session.query(Building).filter(
            Building.generation_status == "completed",
            Building.model_url.isnot(None),
            ~Building.preview_url.like("/api/%") if Building.preview_url.isnot(None) else True,
        ).all()

        # Filter in Python to handle NULL/empty/stale URLs cleanly
        siblings = [
            s for s in siblings
            if not s.preview_url or not s.preview_url.startswith("/api/")
        ]

        logger.info(f"Sibling propagation pass: {len(siblings)} buildings need thumbnails")

        # Build a lookup: model_url -> valid preview_url (from buildings that have one)
        if siblings:
            model_urls = {s.model_url for s in siblings if s.model_url}
            sources = session.query(Building).filter(
                Building.model_url.in_(model_urls),
                Building.preview_url.like("/api/%"),
            ).all()
            preview_map = {s.model_url: s.preview_url for s in sources}

            for sibling in siblings:
                preview = preview_map.get(sibling.model_url)
                if preview:
                    sibling.preview_url = preview
                    sibling.preview_status = "completed"
                    propagated += 1

            if propagated > 0:
                session.commit()
                logger.info(f"Propagated thumbnails to {propagated} sibling buildings")
    except Exception as e:
        logger.warning(f"Sibling thumbnail propagation failed: {e}")
        session.rollback()

    session.close()
    logger.info(f"Thumbnail backfill complete: {success} fetched, {propagated} propagated to siblings, {failed} failed")
