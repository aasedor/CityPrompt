"""Generate a reviewable site finish without rebuilding any authored object."""

from __future__ import annotations
import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated
import boto3
from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import SiteZone, User
from app.api.v1.lego_assembly import _get_zone_with_access
from app.api.v1.site_zones import _zone_to_response
from app.services.residual_landscape import (
    ResidualSourceZone,
    community_3d_kind_for_source,
    lock_residual_landscape_project,
)
from app.services.site_landscape import (
    build_site_landscape,
    context_hash,
    landscape_images,
    clip_custom_art,
    png_bytes,
    normalize_scene_reference,
    site_landscape_prompt,
    blend_site_edges,
)

router = APIRouter()
SITE_LANDSCAPE_MODEL = "gpt-image-2.5-flare"


class LandscapeEdgeSample(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    lng: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)
    color: tuple[
        Annotated[int, Field(ge=0, le=255)],
        Annotated[int, Field(ge=0, le=255)],
        Annotated[int, Field(ge=0, le=255)],
    ]


class LandscapePreviewRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    preset: str = Field(pattern="^(gardens|natural|urban)$")
    prompt: str = Field(default="", max_length=1600)
    corridors: list[list[tuple[float, float]]] = Field(default_factory=list, max_length=512)
    revisions: dict[str, str] = Field(max_length=2000)
    context_image_base64: str | None = Field(default=None, max_length=5_000_000)
    context_edge_samples: list[LandscapeEdgeSample] = Field(default_factory=list, max_length=256)


class LandscapeApplyRequest(BaseModel):
    preview: dict
    signature: str = Field(max_length=64)


def signature(payload):
    # Browser JSON drops .0 on integer-valued floats. Sign normalized numbers
    # so an untouched round-trip remains valid without reducing precision.
    def canonical(value):
        if type(value) in (int, float):
            return ["number", format(float(value) or 0.0, ".17g")]
        if isinstance(value, (list, tuple)):
            return ["array", [canonical(v) for v in value]]
        if isinstance(value, dict):
            return ["object", {k: canonical(v) for k, v in value.items()}]
        return [type(value).__name__, value]

    return hmac.new(
        get_settings().jwt_secret_key.encode(),
        json.dumps(canonical(payload), sort_keys=True, separators=(",", ":")).encode(),
        hashlib.sha256,
    ).hexdigest()


async def scene(db, boundary):
    rows = list(
        (
            await db.execute(
                select(SiteZone)
                .where(SiteZone.project_id == boundary.project_id)
                .execution_options(populate_existing=True)
            )
        )
        .scalars()
        .all()
    )
    boundary = next(z for z in rows if z.id == boundary.id)
    if boundary.zone_type != "site_boundary" or boundary.is_active_boundary is False:
        raise HTTPException(422, "Select the active site boundary")
    if (boundary.properties or {}).get("community_3d_mask_existing_tiles") is False:
        raise HTTPException(422, "Site landscape surfaces currently require a prepared site")
    zones = [
        z
        for z in rows
        if z.id != boundary.id
        and z.zone_type != "site_boundary"
        and (z.properties or {}).get("_plan_role") != "framework_height"
    ]
    return boundary, zones


@router.get("/options")
async def landscape_options(user: User = Depends(require_auth)):
    from app.api.v1.render import _MODEL_TOKEN_COST

    return {
        "tokens": _MODEL_TOKEN_COST[SITE_LANDSCAPE_MODEL],
        "model": SITE_LANDSCAPE_MODEL,
    }


@router.post("/{boundary_id}/preview")
async def preview_landscape(
    boundary_id: uuid.UUID,
    body: LandscapePreviewRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    boundary = await _get_zone_with_access(db, boundary_id, user, require_editor=True)
    boundary, zones = await scene(db, boundary)
    if not zones:
        raise HTTPException(422, "Place a building, street or park first")
    # Verify the browser's complete scene snapshot used to calculate keep-clear routes.
    from app.api.v1.lego_assembly import _same_source_revision

    try:
        valid = set(body.revisions) == {str(z.id) for z in [boundary, *zones]} and all(
            _same_source_revision(
                datetime.fromisoformat(body.revisions[str(z.id)].replace("Z", "+00:00")),
                z.updated_at,
            )
            for z in [boundary, *zones]
        )
    except (ValueError, KeyError):
        valid = False
    if not valid:
        raise HTTPException(409, "Your site changed. Refresh and generate the landscape again.")
    if any(len(ring) < 4 or len(ring) > 32 for ring in body.corridors):
        raise HTTPException(422, "Invalid access corridor")
    geometry = to_shape(boundary.geometry)
    sources = [
        ResidualSourceZone(
            str(z.id),
            community_3d_kind_for_source(z.zone_type, z.properties) or z.zone_type,
            to_shape(z.geometry),
            (z.properties or {}).get("_plan_role"),
        )
        for z in zones
    ]
    try:
        recipe = build_site_landscape(
            geometry,
            sources,
            body.corridors,
            body.preset,
            boundary_id=str(boundary.id),
            compiled_at=datetime.now(timezone.utc).isoformat(),
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if recipe["area_sqm"] < 4:
        raise HTTPException(422, "There is no usable landscape space left in this boundary")
    context = context_hash(boundary, zones)
    base, guide, mask = landscape_images(geometry, recipe, base_surface=bool(body.prompt.strip()))
    if body.prompt.strip():
        from app.api.v1.render import generate_render, RenderRequest

        if not body.context_image_base64:
            raise HTTPException(
                422,
                "Capture your development and surrounding Google tiles before generating custom landscape.",
            )
        try:
            scene_reference = normalize_scene_reference(body.context_image_base64)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        if len(body.context_edge_samples) < 8:
            raise HTTPException(
                422,
                "Capture the neighbouring tile colours to blend the landscape edges.",
            )
        generated = await generate_render(
            RenderRequest(
                project_id=boundary.project_id,
                image_base64=base64.b64encode(png_bytes(guide)).decode(),
                mask_base64=base64.b64encode(png_bytes(mask)).decode(),
                guide_image_kind="landscape_base",
                site_scene_reference_base64=scene_reference,
                prompt=site_landscape_prompt(geometry, zones, body.preset, body.prompt),
                aspect_ratio="1:1",
                image_size="1K",
                post_process=False,
                model=SITE_LANDSCAPE_MODEL,
                image_quality="high",
            ),
            user,
            db,
        )
        art = clip_custom_art(base64.b64decode(generated.image_base64), mask, feather=False)
        art = blend_site_edges(art, mask, geometry, [s.model_dump() for s in body.context_edge_samples])
        settings = get_settings()
        key = f"projects/{boundary.project_id}/landscape/{uuid.uuid4()}.png"
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=png_bytes(art),
            ContentType="image/png",
        )
        recipe["surface_image_url"] = f"/api/v1/files/{key}"
        recipe["surface_prompt"] = body.prompt.strip()
        recipe["surface_mode"] = "site_base"
        recipe["surface_model"] = SITE_LANDSCAPE_MODEL
        recipe["surface_edge_blend"] = {
            "width_m": 6,
            "sample_count": len(body.context_edge_samples),
            "source": "google_tiles_context",
        }
        recipe["surface_context"] = {
            "version": 1,
            "source": "development_with_google_tiles",
            "image_sha256": hashlib.sha256(base64.b64decode(scene_reference)).hexdigest(),
            "scene_hash": context,
        }
        guide.paste(art, mask=art.getchannel("A"))
    from PIL import ImageDraw

    drawing = ImageDraw.Draw(guide)
    west, south, east, north = geometry.bounds
    for tree in recipe["placements"]:
        x = (tree["lng"] - west) / (east - west) * guide.width
        y = (north - tree["lat"]) / (north - south) * guide.height
        drawing.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#496345")
    payload = {
        "boundary_id": str(boundary.id),
        "project_id": str(boundary.project_id),
        "context_hash": context,
        "expires_at": int(time.time()) + 86400,
        "recipe": recipe,
    }
    return {
        "preview": payload,
        "signature": signature(payload),
        "image_base64": base64.b64encode(png_bytes(guide)).decode(),
    }


@router.post("/{boundary_id}/apply")
async def apply_landscape(
    boundary_id: uuid.UUID,
    body: LandscapeApplyRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    payload = body.preview
    if not hmac.compare_digest(signature(payload), body.signature) or payload.get("expires_at", 0) < time.time():
        raise HTTPException(409, "This preview has expired. Generate a fresh landscape preview.")
    boundary = await _get_zone_with_access(db, boundary_id, user, require_editor=True)
    if payload.get("boundary_id") != str(boundary.id) or payload.get("project_id") != str(boundary.project_id):
        raise HTTPException(422, "The preview belongs to another site")
    await lock_residual_landscape_project(db, boundary.project_id)
    boundary, zones = await scene(db, boundary)
    if context_hash(boundary, zones) != payload["context_hash"]:
        raise HTTPException(
            409,
            "Your site changed after this preview. Generate a new landscape to keep access clear.",
        )
    boundary.properties = {
        **(boundary.properties or {}),
        "community_3d_landscape": payload["recipe"],
        "community_3d_landscape_mode": "generated",
    }
    flag_modified(boundary, "properties")
    await db.flush()
    await db.refresh(boundary)
    return _zone_to_response(boundary)
