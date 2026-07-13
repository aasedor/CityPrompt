"""Experimental archetype-driven modular building assembly endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import ModelLibraryEntry, User
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)

router = APIRouter()


class LegoAssemblyPlanRequest(BaseModel):
    target_width_m: float = Field(gt=0)
    target_depth_m: float = Field(gt=0)
    target_floors: int = Field(ge=1, le=100)
    archetype_id: str | None = None
    reuse_keys: list[str] = Field(default_factory=list)
    preferred_family: str | None = None


class LegoModuleMetadataRequest(BaseModel):
    role: str = Field(pattern="^(podium|floor|setback|roof|attachment)$")
    family: str = Field(min_length=1, max_length=100)
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    repeatable_z: bool = False
    archetype_ids: list[str] = Field(default_factory=list)
    reuse_keys: list[str] = Field(default_factory=list)
    min_floors: int | None = Field(default=None, ge=1)
    max_floors: int | None = Field(default=None, ge=1)


async def _accessible_entries(db: AsyncSession, user: User) -> list[ModelLibraryEntry]:
    result = await db.execute(
        select(ModelLibraryEntry)
        .where(
            or_(
                ModelLibraryEntry.owner_id == user.id,
                ModelLibraryEntry.is_public.is_(True),
            )
        )
        .order_by(ModelLibraryEntry.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/modules")
async def list_lego_modules(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List model-library items currently configured as LEGO modules."""
    descriptors = []
    for entry in await _accessible_entries(db, user):
        descriptor = descriptor_from_library_entry(entry)
        if descriptor:
            descriptors.append(
                {
                    "id": descriptor.id,
                    "name": descriptor.name,
                    "model_url": descriptor.model_url,
                    "family": descriptor.family,
                    "role": descriptor.role,
                    "width_m": descriptor.width_m,
                    "depth_m": descriptor.depth_m,
                    "height_m": descriptor.height_m,
                    "archetype_ids": list(descriptor.archetype_ids),
                    "reuse_keys": list(descriptor.reuse_keys),
                    "min_floors": descriptor.min_floors,
                    "max_floors": descriptor.max_floors,
                    "repeatable_z": descriptor.repeatable_z,
                }
            )
    return {"modules": descriptors, "count": len(descriptors)}


@router.put("/modules/{item_id}")
async def configure_lego_module(
    item_id: str,
    body: LegoModuleMetadataRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Mark an existing model-library item as a modular building component."""
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Model-library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the asset owner can configure it")

    if body.min_floors and body.max_floors and body.min_floors > body.max_floors:
        raise HTTPException(status_code=400, detail="min_floors cannot exceed max_floors")

    metadata = dict(entry.metadata_ or {})
    metadata["lego"] = {
        "enabled": True,
        "role": body.role,
        "family": body.family,
        "width_m": body.width_m,
        "depth_m": body.depth_m,
        "height_m": body.height_m,
        "repeatable_z": body.repeatable_z or body.role == "floor",
        "archetype_ids": body.archetype_ids,
        "reuse_keys": body.reuse_keys,
        "min_floors": body.min_floors,
        "max_floors": body.max_floors,
    }
    entry.metadata_ = metadata
    await db.flush()

    return {
        "status": "configured",
        "item_id": str(entry.id),
        "lego": metadata["lego"],
    }


@router.delete("/modules/{item_id}")
async def remove_lego_module_configuration(
    item_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Remove LEGO metadata without deleting the underlying library asset."""
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Model-library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the asset owner can configure it")

    metadata = dict(entry.metadata_ or {})
    metadata.pop("lego", None)
    entry.metadata_ = metadata or None
    await db.flush()
    return {"status": "removed", "item_id": str(entry.id)}


@router.post("/plan")
async def create_lego_assembly_plan(
    body: LegoAssemblyPlanRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a renderer-neutral vertical assembly recipe.

    ``archetype_id`` and ``reuse_keys`` are designed to be passed directly from
    the existing Urban Intelligence DNA ``generation_style_input`` object.
    """
    descriptors = [
        descriptor
        for entry in await _accessible_entries(db, user)
        if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]

    try:
        return plan_vertical_assembly(
            descriptors,
            AssemblyRequest(
                target_width_m=body.target_width_m,
                target_depth_m=body.target_depth_m,
                target_floors=body.target_floors,
                archetype_id=body.archetype_id,
                reuse_keys=tuple(body.reuse_keys),
                preferred_family=body.preferred_family,
            ),
        )
    except AssemblyPlanningError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
