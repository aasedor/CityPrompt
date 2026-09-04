"""
Model Library API endpoints.

Save, browse, and reuse AI-generated 3D models across buildings and projects.
"""

import uuid

import boto3
from botocore.config import Config
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    check_project_permission,
    require_auth,
    visible_project_ids,
)
from app.models.models import Building, ModelLibraryEntry, Project, User
from app.services.residual_landscape import (
    lock_residual_landscape_project,
    mark_linked_community_3d_stale,
)
from app.schemas.schemas import (
    ModelLibraryApplyRequest,
    ModelLibraryResponse,
    ModelLibrarySaveRequest,
)

router = APIRouter()
settings = get_settings()


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def _copy_s3_object(source_url: str, dest_key: str) -> str:
    """Copy an S3 object to a new key, return the new URL."""
    s3 = _get_s3_client()
    bucket = settings.s3_bucket_name

    # Extract source key from URL
    url_parts = source_url.split(f"/{bucket}/", 1)
    if len(url_parts) != 2:
        raise ValueError(f"Cannot parse S3 key from URL: {source_url}")
    source_key = url_parts[1]

    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": source_key},
        Key=dest_key,
        ContentType="model/gltf-binary",
    )
    return f"{settings.s3_endpoint_url}/{bucket}/{dest_key}"


@router.post("/buildings/{building_id}/save", response_model=ModelLibraryResponse)
async def save_to_library(
    building_id: uuid.UUID,
    req: ModelLibrarySaveRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save a building's AI-generated 3D model to the model library."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_permission(building.project_id, user, db)
    if not building.model_url:
        raise HTTPException(status_code=400, detail="Building has no 3D model to save")

    # Copy model file to library storage
    entry_id = uuid.uuid4()
    library_key = f"library/{user.id}/{entry_id}.glb"
    try:
        library_url = _copy_s3_object(building.model_url, library_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to copy model: {e}")

    # Copy LOD variants
    lod_urls = None
    if building.lod_urls:
        lod_urls = {}
        for lod_level, lod_source_url in building.lod_urls.items():
            lod_key = f"library/{user.id}/{entry_id}_lod{lod_level}.glb"
            try:
                lod_urls[lod_level] = _copy_s3_object(lod_source_url, lod_key)
            except Exception:
                pass  # Skip LODs that fail to copy

    entry = ModelLibraryEntry(
        id=entry_id,
        owner_id=user.id,
        source_building_id=building.id,
        source_project_id=building.project_id,
        name=req.name,
        description=req.description,
        category=req.category,
        tags=req.tags,
        model_url=library_url,
        lod_urls=lod_urls,
        generation_prompt=building.generation_prompt,
        generation_engine=building.generation_engine,
        architectural_style=building.architectural_style,
    )

    db.add(entry)
    await db.flush()
    await db.refresh(entry)

    return entry


@router.get("/items", response_model=list[ModelLibraryResponse])
async def list_library(
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search name, description, tags"),
    include_public: bool = Query(True, description="Include public models from other users"),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List models in the library. Shows own models + public models."""
    query = select(ModelLibraryEntry)

    if include_public:
        query = query.where(
            or_(
                ModelLibraryEntry.owner_id == user.id,
                ModelLibraryEntry.is_public == True,  # noqa: E712
            )
        )
    else:
        query = query.where(ModelLibraryEntry.owner_id == user.id)

    if category:
        query = query.where(ModelLibraryEntry.category == category)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                ModelLibraryEntry.name.ilike(pattern),
                ModelLibraryEntry.description.ilike(pattern),
                ModelLibraryEntry.generation_prompt.ilike(pattern),
            )
        )

    query = query.order_by(ModelLibraryEntry.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/items/{item_id}", response_model=ModelLibraryResponse)
async def get_library_item(
    item_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific model library entry."""
    result = await db.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Library item not found")
    if entry.owner_id != user.id and not entry.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to view this model")
    return entry


@router.post("/items/{item_id}/apply", response_model=dict)
async def apply_library_model(
    item_id: uuid.UUID,
    req: ModelLibraryApplyRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Apply a library model to a building (copies the model file)."""
    # Get library entry
    result = await db.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Library item not found")
    if entry.owner_id != user.id and not entry.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to use this model")

    # Get target building
    building_id = uuid.UUID(req.building_id)
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Target building not found")

    # Verify user has edit access to the target project
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        from app.models.models import ProjectShare

        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to edit this building")

    # Copy model to the building's project storage
    dest_key = f"projects/{building.project_id}/models/{building.id}_ai.glb"
    try:
        new_url = _copy_s3_object(entry.model_url, dest_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to copy model: {e}")

    # Copy LOD variants
    new_lod_urls = None
    if entry.lod_urls:
        new_lod_urls = {}
        for lod_level, lod_source_url in entry.lod_urls.items():
            lod_dest_key = f"projects/{building.project_id}/models/{building.id}_lod{lod_level}.glb"
            try:
                new_lod_urls[lod_level] = _copy_s3_object(lod_source_url, lod_dest_key)
            except Exception:
                pass

    # The object copies are external and can run without holding the project
    # row. Serialize only the viewer-authoritative DB swap with paid Direct
    # preflight, then invalidate any compiled zone that mounted the old model.
    await lock_residual_landscape_project(db, building.project_id)
    await db.refresh(building)
    building.model_url = new_url
    building.lod_urls = new_lod_urls
    building.generation_status = "completed"
    building.generation_engine = entry.generation_engine
    building.generation_prompt = entry.generation_prompt
    building.architectural_style = entry.architectural_style
    await mark_linked_community_3d_stale(
        db,
        project_id=building.project_id,
        building_id=building.id,
        reason=("Linked generated building model changed; rebuild Community 3D " "before Direct rendering."),
    )

    # Increment use count
    entry.use_count = (entry.use_count or 0) + 1

    await db.flush()

    return {
        "status": "applied",
        "building_id": str(building.id),
        "model_url": new_url,
        "library_item_id": str(entry.id),
    }


@router.put("/items/{item_id}", response_model=ModelLibraryResponse)
async def update_library_item(
    item_id: uuid.UUID,
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
    is_public: bool | None = None,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a library entry's metadata."""
    result = await db.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can edit this model")

    if name is not None:
        entry.name = name
    if description is not None:
        entry.description = description
    if category is not None:
        entry.category = category
    if tags is not None:
        entry.tags = tags
    if is_public is not None:
        entry.is_public = is_public

    await db.flush()
    await db.refresh(entry)
    return entry


@router.post("/bulk-import", response_model=dict)
async def bulk_import_to_library(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Import all existing AI-generated models into the library.

    Finds every building with a completed model_url that isn't already
    in the library and copies it in.
    """
    # Get all buildings with completed models
    result = await db.execute(
        select(Building).where(
            Building.project_id.in_(visible_project_ids(user)),
            Building.model_url.isnot(None),
            Building.generation_status == "completed",
        )
    )
    buildings = result.scalars().all()

    # Get existing library entries to avoid duplicates
    existing = await db.execute(
        select(ModelLibraryEntry.source_building_id).where(
            ModelLibraryEntry.owner_id == user.id,
        )
    )
    existing_ids = {row for row in existing.scalars().all() if row is not None}

    imported = 0
    skipped = 0

    for building in buildings:
        if building.id in existing_ids:
            skipped += 1
            continue

        entry_id = uuid.uuid4()
        library_key = f"library/{user.id}/{entry_id}.glb"

        try:
            library_url = _copy_s3_object(building.model_url, library_key)
        except Exception:
            skipped += 1
            continue

        # Copy LOD variants
        lod_urls = None
        if building.lod_urls:
            lod_urls = {}
            for lod_level, lod_source_url in building.lod_urls.items():
                lod_key = f"library/{user.id}/{entry_id}_lod{lod_level}.glb"
                try:
                    lod_urls[lod_level] = _copy_s3_object(lod_source_url, lod_key)
                except Exception:
                    pass

        name = building.name or building.generation_prompt or "Imported Model"
        if len(name) > 255:
            name = name[:252] + "..."

        entry = ModelLibraryEntry(
            id=entry_id,
            owner_id=user.id,
            source_building_id=building.id,
            source_project_id=building.project_id,
            name=name,
            description=building.generation_prompt,
            category="other",
            tags=[],
            model_url=library_url,
            lod_urls=lod_urls,
            generation_prompt=building.generation_prompt,
            generation_engine=building.generation_engine,
            architectural_style=building.architectural_style,
        )
        db.add(entry)
        imported += 1

    await db.flush()

    return {
        "status": "done",
        "imported": imported,
        "skipped": skipped,
        "total_buildings_with_models": len(buildings),
    }


@router.delete("/items/{item_id}", status_code=204)
async def delete_library_item(
    item_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a model from the library."""
    result = await db.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this model")

    # Delete S3 objects
    try:
        s3 = _get_s3_client()
        bucket = settings.s3_bucket_name
        url_parts = entry.model_url.split(f"/{bucket}/", 1)
        if len(url_parts) == 2:
            s3.delete_object(Bucket=bucket, Key=url_parts[1])
        if entry.lod_urls:
            for lod_url in entry.lod_urls.values():
                parts = lod_url.split(f"/{bucket}/", 1)
                if len(parts) == 2:
                    s3.delete_object(Bucket=bucket, Key=parts[1])
    except Exception:
        pass  # Don't fail deletion if S3 cleanup fails

    await db.delete(entry)


@router.get("/archetype-previews", response_model=dict)
async def archetype_previews(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return buildings with preview thumbnails grouped by archetype ID.

    Scans completed buildings that have both a preview_url and an archetype ID
    stored in their specifications. Returns a dict mapping archetype_id to a
    list of {id, name, preview_url, model_url} objects (max 4 per archetype).
    """

    result = await db.execute(
        select(Building)
        .where(
            Building.project_id.in_(visible_project_ids(user)),
            Building.preview_url.isnot(None),
            Building.model_url.isnot(None),
            Building.generation_status == "completed",
            Building.specifications.isnot(None),
        )
        .order_by(Building.created_at.desc())
    )
    buildings = result.scalars().all()

    archetype_map: dict[str, list[dict]] = {}
    for b in buildings:
        specs = b.specifications or {}
        # The archetype_id stored during zone creation follows the
        # format "{seed_id}_front_day" — extract the seed portion.
        raw_id = specs.get("development_archetype_id", "") or ""
        archetype_id = raw_id.replace("_front_day", "") if raw_id else ""
        if not archetype_id:
            # Try the subcategory as fallback
            archetype_id = specs.get("development_subcategory", "") or ""
        if not archetype_id:
            continue

        if archetype_id not in archetype_map:
            archetype_map[archetype_id] = []

        if len(archetype_map[archetype_id]) >= 4:
            continue

        archetype_map[archetype_id].append(
            {
                "id": str(b.id),
                "name": b.name,
                "preview_url": b.preview_url,
                "model_url": b.model_url,
                "project_id": str(b.project_id) if b.project_id else None,
            }
        )

    return archetype_map
