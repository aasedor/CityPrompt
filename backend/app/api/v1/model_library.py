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
from app.core.security import require_auth
from app.models.models import Building, ModelLibraryEntry, Project, User
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
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
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
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
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
                or_(ProjectShare.user_id == user.id, ProjectShare.email == user.email),
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

    # Update building
    building.model_url = new_url
    building.lod_urls = new_lod_urls
    building.generation_status = "completed"
    building.generation_engine = entry.generation_engine
    building.generation_prompt = entry.generation_prompt
    building.architectural_style = entry.architectural_style

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
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
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


@router.delete("/items/{item_id}", status_code=204)
async def delete_library_item(
    item_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a model from the library."""
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
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
