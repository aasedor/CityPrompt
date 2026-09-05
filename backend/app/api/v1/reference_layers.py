"""Permission-scoped, bounded reference datasets. Never creates proposal zones."""

import hashlib
import json
import uuid
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import Project, User
from app.models.reference_layers import ReferenceLayer
from app.schemas.reference_layers import ReferenceLayerListResponse, ReferenceLayerMetadata, ReferenceLayerResponse
from app.services.reference_import import MAX_UPLOAD_BYTES, ReferenceImportError, parse_reference_file

router = APIRouter()
MAX_PROJECT_LAYERS = 20
MAX_PROJECT_BYTES = 12 * 1024 * 1024


@router.get("/projects/{project_id}", response_model=ReferenceLayerListResponse)
async def list_reference_layers(
    project_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)
):
    permission = await check_project_permission(project_id, user, db)
    result = await db.execute(
        select(ReferenceLayer).where(ReferenceLayer.project_id == project_id).order_by(ReferenceLayer.created_at)
    )
    return {"layers": result.scalars().all(), "can_edit": permission in ("owner", "editor")}


@router.post("/projects/{project_id}/import", response_model=ReferenceLayerResponse, status_code=201)
async def import_reference_layer(
    project_id: uuid.UUID,
    response: Response,
    file: UploadFile = File(...),
    name: str | None = Form(None),
    kind: str = Form("reference"),
    source_url: str | None = Form(None),
    description: str | None = Form(None),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="editor")
    filename = PurePosixPath((file.filename or "reference.geojson").replace("\\", "/")).name[:255]
    try:
        metadata = ReferenceLayerMetadata(
            name=(name or PurePosixPath(filename).stem).strip(),
            kind=kind,
            source_url=source_url or None,
            description=description or None,
        )
    except ValidationError as exc:
        raise HTTPException(
            422, detail="Provide a name (1–160 characters), a reference/zoning type and an optional valid source URL."
        ) from exc
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, detail="Reference files must be 25 MB or smaller.")
    try:
        parsed = await run_in_threadpool(parse_reference_file, data, filename)
    except ReferenceImportError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    content_hash = hashlib.sha256(
        json.dumps(parsed.feature_collection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    # Serialize imports for this project so retries/parallel requests cannot
    # bypass per-project bounds or leave a half-imported collection.
    await db.execute(select(Project.id).where(Project.id == project_id).with_for_update())
    result = await db.execute(select(ReferenceLayer).where(ReferenceLayer.project_id == project_id))
    existing = result.scalars().all()
    duplicate = next((layer for layer in existing if layer.content_hash == content_hash), None)
    if duplicate:
        response.status_code = 200
        return duplicate
    if (
        len(existing) >= MAX_PROJECT_LAYERS
        or sum(layer.storage_bytes for layer in existing) + parsed.storage_bytes > MAX_PROJECT_BYTES
    ):
        raise HTTPException(
            409,
            detail="This project supports 20 reference layers and 12 MB of reference data. Remove a layer or import a smaller area.",
        )
    layer = ReferenceLayer(
        project_id=project_id,
        created_by=user.id,
        name=metadata.name,
        kind=metadata.kind,
        source_filename=filename,
        source_crs=parsed.source_crs[:255],
        source_url=str(metadata.source_url) if metadata.source_url else None,
        description=metadata.description,
        feature_collection=parsed.feature_collection,
        feature_count=parsed.feature_count,
        storage_bytes=parsed.storage_bytes,
        bounds=parsed.bounds,
        warnings=parsed.warnings,
        content_hash=content_hash,
        color=metadata.color,
        opacity=metadata.opacity,
    )
    db.add(layer)
    await db.flush()
    await db.refresh(layer)
    return layer


@router.put("/{layer_id}", response_model=ReferenceLayerResponse)
async def update_reference_layer(
    layer_id: uuid.UUID,
    metadata: ReferenceLayerMetadata,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    layer = await db.get(ReferenceLayer, layer_id)
    if layer is None:
        raise HTTPException(404, detail="Reference layer not found.")
    await check_project_permission(layer.project_id, user, db, required="editor")
    for key, value in metadata.model_dump().items():
        setattr(layer, key, str(value) if key == "source_url" and value is not None else value)
    await db.flush()
    await db.refresh(layer)
    return layer


@router.delete("/{layer_id}", status_code=204)
async def delete_reference_layer(
    layer_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)
):
    layer = await db.get(ReferenceLayer, layer_id)
    if layer is None:
        raise HTTPException(404, detail="Reference layer not found.")
    await check_project_permission(layer.project_id, user, db, required="editor")
    await db.delete(layer)
    return Response(status_code=204)
