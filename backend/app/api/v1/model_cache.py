"""
Admin endpoints for the archetype model cache — pre-warm generation and
ops visibility. The claim/complete lifecycle lives in the Celery task
(prewarm_archetype_model); these endpoints only enqueue and report.
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.models import ArchetypeModelCache, User
from app.services.archetype_model_cache import has_completed_entry

logger = logging.getLogger(__name__)
router = APIRouter()


class PrewarmRequest(BaseModel):
    archetype_id: str = Field(min_length=1, max_length=120)
    variant_id: str = Field(default="default", max_length=120)
    engine: str = Field(default="meshy", pattern="^(meshy|tripo)$")
    mode: str = Field(default="text", pattern="^(text|image|multi_image)$")
    # text mode: the text-to-3D prompt. multi_image mode: the Meshy
    # texture_prompt (client caps at 600 chars).
    prompt: str | None = None
    # base64 PNG/JPEG (with or without a data: prefix) for image mode.
    # Bounded: the payload rides through Redis as Celery task args.
    image_base64: str | None = Field(default=None, max_length=16_000_000)
    # multi_image mode: 1-4 images of the SAME building, street card first
    # (Meshy treats the first image as the primary view), then aerials.
    image_base64s: list[str] | None = Field(default=None, min_length=1, max_length=4)
    # None = per-mode default in the task (image -> True, multi_image -> False).
    isolate_images: bool | None = None
    # Gemini removal edit on inputs before submission (people/vehicles fuse
    # into mutant mesh geometry otherwise).
    clean_images: str | None = Field(default=None, pattern="^(entourage|building_only)$")
    target_polycount: int | None = Field(default=None, ge=100, le=300_000)
    # Re-generate over a COMPLETED cache row (flips it to failed so the
    # worker's claim takeover wins; the storage key is overwritten in place).
    force: bool = False

    @field_validator("image_base64s")
    @classmethod
    def _bound_image_payloads(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for i, item in enumerate(v):
            if len(item) > 8_000_000:
                raise ValueError(f"image_base64s[{i}] exceeds 8MB base64 limit")
        if sum(len(item) for item in v) > 24_000_000:
            raise ValueError("image_base64s total exceeds 24MB base64 limit")
        return v


@router.post("/prewarm")
async def prewarm(
    req: PrewarmRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Queue a cache-warming generation. Idempotent: an already-completed
    key returns immediately without spending credits (unless force)."""
    if req.mode == "text" and not req.prompt:
        raise HTTPException(status_code=422, detail="prompt is required for text mode")
    if req.mode == "image" and not req.image_base64:
        raise HTTPException(status_code=422, detail="image_base64 is required for image mode")
    if req.mode == "multi_image" and not req.image_base64s:
        raise HTTPException(status_code=422, detail="image_base64s is required for multi_image mode")

    if await has_completed_entry(db, req.archetype_id, req.variant_id, req.engine):
        if not req.force:
            return {"status": "completed", "archetype_id": req.archetype_id, "variant_id": req.variant_id}
        # Supersede: flip the completed row to failed so claim_entry's
        # failed-row takeover wins. Same row id -> same storage key, so the
        # new GLB overwrites the old asset in place and every Building
        # already referencing it gets the regenerated model.
        await db.execute(
            update(ArchetypeModelCache)
            .where(
                ArchetypeModelCache.archetype_id == req.archetype_id,
                ArchetypeModelCache.variant_id == req.variant_id,
                ArchetypeModelCache.engine == req.engine,
                ArchetypeModelCache.status == "completed",
            )
            .values(status="failed", error=f"superseded: {req.mode} regeneration")
        )
        await db.commit()
        logger.info(
            "Force prewarm: superseded completed row %s/%s/%s",
            req.archetype_id, req.variant_id, req.engine,
        )

    def _to_data_uri(b64: str, default_mime: str = "image/png") -> str:
        return b64 if b64.startswith("data:") else f"data:{default_mime};base64,{b64}"

    image_data_uri = _to_data_uri(req.image_base64) if req.image_base64 else None
    image_data_uris = (
        [_to_data_uri(item) for item in req.image_base64s] if req.image_base64s else None
    )

    from app.tasks.processing import prewarm_archetype_model

    task = await asyncio.to_thread(
        prewarm_archetype_model.apply_async,
        kwargs={
            "archetype_id": req.archetype_id,
            "variant_id": req.variant_id,
            "engine": req.engine,
            "mode": req.mode,
            "prompt": req.prompt,
            "image_data_uri": image_data_uri,
            "image_data_uris": image_data_uris,
            "isolate_images": req.isolate_images,
            "clean_images": req.clean_images,
            "target_polycount": req.target_polycount,
        },
    )
    return {
        "status": "queued",
        "task_id": getattr(task, "id", None),
        "archetype_id": req.archetype_id,
        "variant_id": req.variant_id,
        "engine": req.engine,
    }


@router.get("/entries")
async def list_entries(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    query = select(ArchetypeModelCache).order_by(ArchetypeModelCache.created_at.desc()).limit(500)
    if status:
        query = query.where(ArchetypeModelCache.status == status)
    rows = (await db.execute(query)).scalars().all()
    return {
        "entries": [
            {
                "id": str(e.id),
                "archetype_id": e.archetype_id,
                "variant_id": e.variant_id,
                "engine": e.engine,
                "status": e.status,
                "model_key": e.model_key,
                "size_bytes": e.size_bytes,
                "use_count": e.use_count,
                "generation_mode": e.generation_mode,
                "metadata": e.metadata_,
                "error": e.error,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "updated_at": e.updated_at.isoformat() if e.updated_at else None,
            }
            for e in rows
        ]
    }
