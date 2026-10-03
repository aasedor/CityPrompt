"""
Building management API endpoints.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    check_project_asset_access,
    check_project_permission,
    check_project_read_access,
    get_current_user,
    require_auth,
)
from app.tasks.worker import celery_app
from app.generation.styles import ARCHITECTURAL_STYLES, get_style
from app.models.models import Building, Project, ProjectShare, RenderPreview, User
from app.services.generation_queue import queue_ai_generation_task
from app.services.photo_building import (
    MAX_PHOTOS, MIN_REFERENCE_VIEWS, MAX_REFERENCE_VIEWS,
    PHOTO_MODEL_TOKEN_COST, PHOTO_REFERENCE_TOKEN_COST,
    photo_state, prepare_photo, refund_photo_tokens, reserve_photo_tokens,
)
from app.services.building_reference_search import (
    VIEW_TERMS, download_building_view, search_building_views, sign_candidate, verified_candidate,
)
from app.services.residual_landscape import (
    lock_residual_landscape_project,
    mark_linked_community_3d_stale,
)
from app.schemas.schemas import (
    ArchitecturalStyleResponse,
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
    GenerateRequest,
    GenerateFromImageRequest,
    GenerationStatusResponse,
    AITemplate,
    GenerationEngineInfo,
    RenderPreviewRequest,
    RenderPreviewResponse,
)

router = APIRouter()
settings = get_settings()


def _building_to_response(building: Building) -> dict:
    """Convert a Building ORM object to a response dict with footprint_coordinates."""
    footprint_coordinates: list[list[float]] | None = None
    if building.footprint is not None:
        try:
            shape = to_shape(building.footprint)
            footprint_coordinates = [[c[0], c[1]] for c in shape.exterior.coords[:-1]]
        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"Failed to convert footprint for building {building.id}: {e}")

    return {
        "id": building.id,
        "project_id": building.project_id,
        "name": building.name,
        "height_meters": building.height_meters,
        "floor_count": building.floor_count,
        "floor_height_meters": building.floor_height_meters,
        "roof_type": building.roof_type,
        "construction_phase": building.construction_phase,
        "model_url": building.model_url,
        "lod_urls": building.lod_urls,
        "specifications": building.specifications,
        "generation_status": building.generation_status,
        "generation_prompt": building.generation_prompt,
        "meshy_task_id": building.meshy_task_id,
        "footprint_coordinates": footprint_coordinates,
        "rotation_degrees": (
            float(building.rotation_degrees) if getattr(building, "rotation_degrees", None) is not None else 0
        ),
        "architectural_style": building.architectural_style,
        "preview_url": building.preview_url,
        "preview_status": building.preview_status,
        "generation_engine": building.generation_engine,
        "created_at": building.created_at,
    }


def _enrich_prompt_with_style(prompt: str, style_id: str | None) -> str:
    """Prepend/append style modifiers to a generation prompt."""
    style = get_style(style_id)
    parts = []
    if style.prompt_prefix:
        parts.append(style.prompt_prefix)
    parts.append(prompt)
    if style.prompt_suffix:
        parts.append(style.prompt_suffix)
    return " ".join(parts)


def _get_style_negative_prompt(style_id: str | None, user_negative: str | None) -> str:
    """Combine style's negative prompt with user-provided negative prompt."""
    style = get_style(style_id)
    parts = []
    base_negative = (
        "blurry, low quality, deformed, floating objects, ground plane, "
        "background, people, vehicles, cartoon, anime, stylized, miniature"
    )
    parts.append(base_negative)
    if style.negative_prompt:
        parts.append(style.negative_prompt)
    if user_negative:
        parts.append(user_negative)
    return ", ".join(parts)


def _resolve_engine(req_engine: str | None) -> str:
    """Resolve which generation engine to use."""
    if req_engine:
        return req_engine
    return settings.default_generation_engine


def _check_engine_available(engine: str) -> None:
    """Raise HTTPException if the requested engine is not configured."""
    if engine == "meshy" and not settings.meshy_api_key:
        raise HTTPException(
            status_code=400,
            detail="MESHY_API_KEY is not configured. Add your Meshy.ai API key to the .env file.",
        )
    elif engine == "tripo" and not settings.tripo_api_key:
        raise HTTPException(
            status_code=400,
            detail="TRIPO_API_KEY is not configured. Add your Tripo3D API key to the .env file.",
        )


@router.get("/projects/{project_id}/buildings", response_model=list[BuildingResponse])
async def list_buildings(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
    share_token: str | None = None,
):
    """List all buildings in a project."""
    await check_project_read_access(project_id, user, db, share_token)
    result = await db.execute(select(Building).where(Building.project_id == project_id).order_by(Building.created_at))
    return [_building_to_response(b) for b in result.scalars().all()]


@router.post(
    "/projects/{project_id}/buildings",
    response_model=BuildingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_building(
    project_id: uuid.UUID,
    building_in: BuildingCreate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Manually add a building to a project."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check editor permission
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to add buildings to this project",
            )

    building = Building(
        project_id=project_id,
        name=building_in.name,
        height_meters=building_in.height_meters,
        floor_count=building_in.floor_count,
        floor_height_meters=building_in.floor_height_meters,
        roof_type=building_in.roof_type,
        construction_phase=building_in.construction_phase,
        specifications=building_in.specifications,
        architectural_style=building_in.architectural_style,
    )

    if building_in.footprint_coordinates:
        from geoalchemy2.elements import WKTElement

        coords = building_in.footprint_coordinates
        # Close the polygon if not already closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        coords_str = ", ".join(f"{c[0]} {c[1]}" for c in coords)
        building.footprint = WKTElement(f"POLYGON(({coords_str}))", srid=4326)

    db.add(building)
    await db.flush()
    await db.refresh(building)

    # Log activity
    from app.api.v1.activity import log_activity

    await log_activity(
        db,
        project_id,
        "building_created",
        user_id=user.id,
        details={"name": building.name},
    )

    return _building_to_response(building)


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
    share_token: str | None = None,
):
    """Get building details."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_read_access(building.project_id, user, db, share_token)
    return _building_to_response(building)


@router.put("/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: uuid.UUID,
    building_in: BuildingUpdate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update building details."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check editor permission on parent project
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to edit buildings in this project",
            )

    update_data = building_in.model_dump(exclude_unset=True)
    representation_changed = bool(
        {
            "name",
            "height_meters",
            "floor_count",
            "floor_height_meters",
            "roof_type",
            "specifications",
            "footprint_coordinates",
            "rotation_degrees",
            "architectural_style",
            # Not currently exposed by BuildingUpdate, but keep the guard aligned
            # with the generated-model viewer if that schema is expanded later.
            "model_url",
            "lod_urls",
        }.intersection(update_data)
    )
    if representation_changed:
        await lock_residual_landscape_project(db, building.project_id)
        await db.refresh(building)

    # Handle footprint_coordinates to geometry conversion
    if "footprint_coordinates" in update_data:
        coords = update_data.pop("footprint_coordinates")
        if coords and len(coords) >= 3:
            from geoalchemy2.elements import WKTElement

            if coords[0] != coords[-1]:
                coords.append(coords[0])
            coords_str = ", ".join(f"{c[0]} {c[1]}" for c in coords)
            building.footprint = WKTElement(f"POLYGON(({coords_str}))", srid=4326)

    for field, value in update_data.items():
        setattr(building, field, value)

    if representation_changed:
        await mark_linked_community_3d_stale(
            db,
            project_id=building.project_id,
            building_id=building.id,
            reason="Linked building representation changed; rebuild Community 3D before Direct rendering.",
        )

    await db.flush()
    await db.refresh(building)
    return _building_to_response(building)


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a building."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check editor permission on parent project
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete buildings in this project",
            )

    # Serialize model deletion with Community compile and paid Direct
    # preflight. A request validated before this lock may finish against its
    # already captured pixels; a request arriving after deletion must observe
    # the missing model and fail before credits are reserved.
    await lock_residual_landscape_project(db, building.project_id)
    await db.refresh(building)
    await mark_linked_community_3d_stale(
        db,
        project_id=building.project_id,
        building_id=building.id,
        reason="Linked building deleted; rebuild Community 3D before Direct rendering.",
    )
    await db.delete(building)


@router.get("/{building_id}/model")
async def get_building_model(
    building_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
    share_token: str | None = None,
):
    """Get the 3D model URL for a building."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_read_access(building.project_id, user, db, share_token)
    if not building.model_url:
        raise HTTPException(status_code=404, detail="3D model not yet generated")
    return {"model_url": building.model_url}


@router.get("/{building_id}/model/file")
async def get_building_model_file(
    building_id: uuid.UUID,
    lod: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
    share_token: str | None = None,
    asset_ticket: str | None = None,
):
    """Proxy the GLB model file from MinIO storage.

    Query params:
        lod: LOD level (0=full detail, 1=simplified, 2=textured box, 3=simple box)
    """
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_asset_access(
        building.project_id,
        user,
        db,
        share_token=share_token,
        asset_ticket=asset_ticket,
    )
    if not building.model_url:
        raise HTTPException(status_code=404, detail="3D model not yet generated")

    # Pick the right URL based on LOD level
    model_url = building.model_url
    if lod > 0 and building.lod_urls:
        lod_url = building.lod_urls.get(str(lod))
        if lod_url:
            model_url = lod_url
        else:
            # Fall back to closest available LOD
            available = sorted(int(k) for k in building.lod_urls.keys())
            closest = min(available, key=lambda x: abs(x - lod))
            model_url = building.lod_urls[str(closest)]

    import boto3
    from botocore.config import Config

    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )

    # Extract the S3 key from the model URL. Modern URLs are API paths
    # (/api/v1/files/<key>, same key convention as files.get_file); legacy
    # URLs embed the bucket directly (http://minio:9000/<bucket>/<key>).
    files_prefix = "/api/v1/files/"
    if files_prefix in model_url:
        file_key = model_url.split(files_prefix, 1)[1]
    else:
        url_parts = model_url.split(f"/{settings.s3_bucket_name}/", 1)
        if len(url_parts) != 2:
            raise HTTPException(status_code=500, detail="Invalid model URL")
        file_key = url_parts[1]

    try:
        obj = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=file_key)
        file_data = obj["Body"].read()
    except Exception:
        raise HTTPException(status_code=404, detail="Model file not found in storage")

    return Response(
        content=file_data,
        media_type="model/gltf-binary",
        headers={
            "Content-Disposition": f'inline; filename="{building_id}_lod{lod}.glb"',
            "Cache-Control": "private, no-store",
            "Referrer-Policy": "no-referrer",
        },
    )


# =============================================================================
# Architectural Styles
# =============================================================================


@router.get("/ai/styles", response_model=list[ArchitecturalStyleResponse])
async def get_styles():
    """Get the list of available architectural styles."""
    return [
        ArchitecturalStyleResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            facade_material=s.facade_material,
            secondary_material=s.secondary_material,
            roof_material=s.roof_material,
            preferred_roof_types=s.preferred_roof_types,
            prompt_prefix=s.prompt_prefix,
            meshy_art_style=s.meshy_art_style,
            thumbnail_url=s.thumbnail_url,
            tags=s.tags,
        )
        for s in ARCHITECTURAL_STYLES.values()
    ]


# =============================================================================
# AI 3D Generation Endpoints
# =============================================================================

AI_TEMPLATES = [
    # Commercial
    AITemplate(
        id="com-office",
        name="Modern Glass Office Building",
        category="commercial",
        prompt="Modern glass office building, 10 stories, curtain wall facade, realistic architectural style",
    ),
    AITemplate(
        id="com-retail",
        name="Retail Storefront with Awning",
        category="commercial",
        prompt="Single-story retail storefront with fabric awning, large display windows, brick facade",
    ),
    AITemplate(
        id="com-mixed",
        name="Mixed-Use Building",
        category="commercial",
        prompt="Mixed-use building with ground-floor retail and upper residential units, modern facade, 5 stories",
    ),
    # Residential
    AITemplate(
        id="res-house",
        name="Two-Story Suburban House",
        category="residential",
        prompt="Two-story suburban house with attached garage, gabled roof, vinyl siding, front porch",
    ),
    AITemplate(
        id="res-apartment",
        name="Modern Apartment Building",
        category="residential",
        prompt="Modern apartment building, 8 stories, balconies on each floor, flat roof, contemporary design",
    ),
    AITemplate(
        id="res-townhouse",
        name="Townhouse Row",
        category="residential",
        prompt="Row of three attached townhouses, brick facade, bay windows, pitched roofs",
    ),
    # Infrastructure
    AITemplate(
        id="inf-parking",
        name="Parking Garage Structure",
        category="infrastructure",
        prompt="Multi-level parking garage structure, 4 levels, concrete, open-air design with ramps",
    ),
    AITemplate(
        id="inf-busstop",
        name="Bus Stop Shelter",
        category="infrastructure",
        prompt="Modern bus stop shelter with glass walls, metal roof, bench seating, LED lighting",
    ),
    AITemplate(
        id="inf-bridge",
        name="Pedestrian Bridge",
        category="infrastructure",
        prompt="Modern pedestrian bridge with steel cable stays, glass railings, covered walkway",
    ),
    # Landscaping
    AITemplate(
        id="land-gazebo",
        name="Park Gazebo",
        category="landscaping",
        prompt="Octagonal park gazebo with white painted wood, shingled roof, built-in benches",
    ),
    AITemplate(
        id="land-playground",
        name="Playground Equipment",
        category="landscaping",
        prompt="Children's playground set with slides, swings, climbing frame, colorful design",
    ),
    AITemplate(
        id="land-fountain",
        name="Garden Fountain",
        category="landscaping",
        prompt="Circular stone garden fountain with three tiers, water feature, classical style",
    ),
]


@router.post("/{building_id}/generate", response_model=GenerationStatusResponse)
async def generate_from_text(
    building_id: uuid.UUID,
    req: GenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Start AI 3D model generation from a text prompt."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # Resolve engine and check availability
    engine = _resolve_engine(req.engine)
    _check_engine_available(engine)

    # Resolve style: request > building > project default
    style_id = req.style or building.architectural_style or getattr(project, "default_style", None)
    style_changed = bool(style_id and style_id != building.architectural_style)
    if style_changed:
        await lock_residual_landscape_project(db, building.project_id)
        await db.refresh(building)

    # Enrich prompt with style
    enriched_prompt = _enrich_prompt_with_style(req.prompt, style_id)
    negative = _get_style_negative_prompt(style_id, req.negative_prompt)

    # Update building with generation info
    building.generation_status = "generating"
    building.generation_prompt = req.prompt
    if style_id:
        building.architectural_style = style_id
    building.generation_engine = engine
    if style_changed:
        await mark_linked_community_3d_stale(
            db,
            project_id=building.project_id,
            building_id=building.id,
            reason=("Linked building display style changed; rebuild Community 3D " "before Direct rendering."),
        )
    await db.flush()

    await queue_ai_generation_task(
        db,
        building,
        enriched_prompt,
        mode="text",
        engine=engine,
        style_id=style_id,
        negative_prompt=negative,
    )

    return GenerationStatusResponse(
        status="generating",
        progress=0,
        meshy_task_id=building.meshy_task_id,
    )


@router.post("/{building_id}/generate-from-image", response_model=GenerationStatusResponse)
async def generate_from_image(
    building_id: uuid.UUID,
    req: GenerateFromImageRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Start AI 3D model generation from an image."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # For image mode, default to meshy (tripo also supports image_to_3d)
    engine = _resolve_engine(None)
    _check_engine_available(engine)

    building.generation_status = "generating"
    # The source can be a multi-megabyte data URI or a signed private URL.
    # Keep it out of the DB, activity surfaces, and admin search results.
    building.generation_prompt = "[single-image reference]"
    building.generation_engine = engine
    await db.flush()

    await queue_ai_generation_task(
        db,
        building,
        "",
        mode="image",
        image_url=req.image_url,
        engine=engine,
    )

    return GenerationStatusResponse(
        status="generating",
        progress=0,
        meshy_task_id=building.meshy_task_id,
    )


async def _editable_building(building_id: uuid.UUID, user: User, db: AsyncSession) -> Building:
    building = await db.get(Building, building_id, with_for_update=True, populate_existing=True)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_permission(building.project_id, user, db, required="editor")
    return building


@router.get("/{building_id}/photo-references")
async def get_photo_references(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return the current private reference-view preparation status."""
    building = await db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_permission(building.project_id, user, db)
    state = photo_state(building.specifications)
    return {
        "status": state.get("status", "idle"),
        "brief": state.get("brief", ""),
        "reference_urls": [f"/api/v1/files/{key}" for key in state.get("reference_keys", [])],
        "error": state.get("error"),
        "source_count": len(state.get("source_keys", [])),
        "resume_available": bool(
            state.get("status") == "failed" and state.get("provider_task_id")
            and not state.get("reference_keys")
        ),
        "reference_token_cost": PHOTO_REFERENCE_TOKEN_COST,
        "model_token_cost": PHOTO_MODEL_TOKEN_COST,
        "source_provenance": state.get("source_provenance", []),
        "selected_reference_indices": state.get("selected_reference_indices", []),
    }


@router.post("/{building_id}/photo-reference-search")
async def find_photo_references(
    building_id: uuid.UUID,
    query: str = Body(..., min_length=3, max_length=160),
    view: str = Body("all"),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Find public landmark views and retain trusted candidates for this building."""
    building = await _editable_building(building_id, user, db)
    if view not in VIEW_TERMS or len(query.strip()) < 3:
        raise HTTPException(status_code=422, detail="Enter a building name and choose a viewing angle.")
    try:
        candidates = [sign_candidate(item, str(building_id)) for item in await search_building_views(query, view)]
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Image search is temporarily unavailable. Try again or upload your own photos.") from exc
    specs = dict(building.specifications or {})
    previous = specs.get("photo_reference_search", {}).get("candidates", [])
    current_ids = {item["id"] for item in candidates}
    specs["photo_reference_search"] = {
        "query": query.strip(), "searched_at": datetime.now(timezone.utc).isoformat(),
        "candidates": (candidates + [item for item in previous if item.get("id") not in current_ids])[:48],
    }
    building.specifications = specs
    await db.commit()
    return {"candidates": candidates, "query": query.strip(), "provider": "wikimedia_commons"}


@router.post("/{building_id}/photo-references")
async def create_photo_references(
    building_id: uuid.UUID,
    photos: list[UploadFile] = File(default=[]),
    brief: str = Form(""),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    web_reference_ids: str = Form("[]"),
):
    """Store bounded source photos and queue paid, reviewable reference views."""
    building = await _editable_building(building_id, user, db)
    if building.generation_status == "generating":
        raise HTTPException(status_code=409, detail="Wait for the current 3D generation to finish first.")
    if photo_state(building.specifications).get("status") == "synthesizing":
        raise HTTPException(status_code=409, detail="Reference views are already being prepared.")
    try:
        selected_ids = json.loads(web_reference_ids if isinstance(web_reference_ids, str) else "[]")
        if (not isinstance(selected_ids, list) or not all(isinstance(item, str) for item in selected_ids)
                or len(set(selected_ids)) != len(selected_ids)):
            raise ValueError("invalid selection")
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="Choose valid reference photos from your search results.") from exc
    if not 1 <= len(photos) + len(selected_ids) <= MAX_PHOTOS:
        raise HTTPException(status_code=422, detail="Choose 1 to 4 photos total, including uploads and search results.")
    candidates = {item["id"]: item for item in (building.specifications or {}).get("photo_reference_search", {}).get("candidates", [])}
    if any(item not in candidates or not verified_candidate(candidates[item], str(building_id)) for item in selected_ids):
        raise HTTPException(status_code=409, detail="A selected web photo is no longer available. Search again before preparing views.")
    if len(brief) > 500:
        raise HTTPException(status_code=422, detail="Description must be 500 characters or fewer.")
    _check_engine_available("meshy")

    prepared: list[tuple[bytes, str]] = []
    provenance: list[dict] = []
    for photo in photos:
        try:
            prepared.append(prepare_photo(await photo.read(5 * 1024 * 1024 + 1)))
            provenance.append({"provider": "student_upload", "sha256": prepared[-1][1]})
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    for reference_id in selected_ids:
        candidate = candidates[reference_id]
        try:
            prepared.append(await download_building_view(candidate))
        except Exception as exc:
            raise HTTPException(status_code=422, detail="A selected web photo could not be loaded. Choose another view; no tokens were charged.") from exc
        provenance.append({**candidate, "sha256": prepared[-1][1], "confirmed_same_building": True})

    from app.tasks.processing import _upload_to_storage, synthesize_building_photo_references

    batch_id = uuid.uuid4().hex
    source_keys: list[str] = []
    for index, (image_data, image_hash) in enumerate(prepared):
        key = f"projects/{building.project_id}/photo-buildings/{building.id}/{batch_id}/source-{index}-{image_hash[:12]}.jpg"
        await asyncio.to_thread(_upload_to_storage, key, image_data, "image/jpeg")
        source_keys.append(key)

    audit_id = await reserve_photo_tokens(
        db, user, building.project_id, cost=PHOTO_REFERENCE_TOKEN_COST,
        stage="references", brief=brief.strip(),
    )
    specs = dict(building.specifications or {})
    specs["photo_generation"] = {
        "version": 1,
        "batch_id": batch_id,
        "status": "synthesizing",
        "brief": brief.strip(),
        "source_keys": source_keys,
        "source_hashes": [digest for _, digest in prepared],
        "source_provenance": provenance,
        "reference_keys": [],
        "engine": "meshy",
        "quality_tier": "student_preview",
        "catalogue_eligible": False,
        "method": "photo_references_to_ai_mesh_v1",
        "reference_audit_id": str(audit_id),
    }
    building.specifications = specs
    await db.commit()
    try:
        task = await asyncio.to_thread(
            synthesize_building_photo_references.apply_async,
            args=[str(building.id), batch_id, str(audit_id)],
        )
    except Exception as exc:
        state = dict(photo_state(building.specifications))
        state.update(status="failed", error="Could not start reference preparation. Please try again.")
        building.specifications = {**(building.specifications or {}), "photo_generation": state}
        await db.commit()
        await refund_photo_tokens(db, str(audit_id))
        raise HTTPException(status_code=503, detail=state["error"]) from exc
    return {"status": "synthesizing", "task_id": getattr(task, "id", None)}


@router.post("/{building_id}/photo-references/resume")
async def resume_photo_references(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reuse an existing provider task after a transient storage/contract error."""
    building = await _editable_building(building_id, user, db)
    state = photo_state(building.specifications)
    if (
        state.get("status") != "failed" or not state.get("provider_task_id")
        or state.get("reference_keys") or not state.get("batch_id")
    ):
        raise HTTPException(status_code=409, detail="No prepared provider task is available to resume.")
    state = {**state, "status": "synthesizing", "error": None}
    building.specifications = {**(building.specifications or {}), "photo_generation": state}
    await db.commit()
    from app.tasks.processing import synthesize_building_photo_references

    try:
        task = await asyncio.to_thread(
            synthesize_building_photo_references.apply_async,
            args=[str(building.id), state["batch_id"], state.get("reference_audit_id")],
        )
    except Exception as exc:
        state = {**state, "status": "failed", "error": "Could not resume reference preparation."}
        building.specifications = {**(building.specifications or {}), "photo_generation": state}
        await db.commit()
        raise HTTPException(status_code=503, detail=state["error"]) from exc
    return {"status": "synthesizing", "task_id": getattr(task, "id", None)}


@router.post("/{building_id}/photo-model", response_model=GenerationStatusResponse)
async def generate_photo_model(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    selected_reference_indices: list[int] | None = Body(default=None, embed=True),
):
    """Turn reviewed reference views into a private AI mesh preview."""
    building = await _editable_building(building_id, user, db)
    state = photo_state(building.specifications)
    keys = state.get("reference_keys") or []
    expected_prefix = f"projects/{building.project_id}/photo-buildings/{building.id}/{state.get('batch_id', '')}/"
    if state.get("status") not in {"references_ready", "failed"} or not MIN_REFERENCE_VIEWS <= len(keys) <= MAX_REFERENCE_VIEWS or not all(
        isinstance(key, str) and key.startswith(expected_prefix + "reference-") for key in keys
    ):
        raise HTTPException(status_code=409, detail="Review the prepared views before generating a model.")
    selected = list(range(len(keys))) if selected_reference_indices is None else selected_reference_indices
    if not selected or len(set(selected)) != len(selected) or any(index < 0 or index >= len(keys) for index in selected):
        raise HTTPException(status_code=422, detail="Select at least one valid reference view.")
    selected_keys = [keys[index] for index in selected]
    if building.generation_status == "generating":
        raise HTTPException(status_code=409, detail="A 3D generation is already in progress.")
    _check_engine_available("meshy")

    # These are server-issued keys under this building, never client URLs.
    prompt = (
        "Architectural materials and colors exactly as shown in the reviewed reference views. "
        + str(state.get("brief", ""))[:500]
    )
    audit_id = await reserve_photo_tokens(
        db, user, building.project_id, cost=PHOTO_MODEL_TOKEN_COST,
        stage="model", brief=prompt,
    )
    state = {**state, "status": "model_generating", "error": None,
             "selected_reference_indices": selected, "model_audit_id": str(audit_id)}
    building.specifications = {**(building.specifications or {}), "photo_generation": state}
    building.generation_status = "generating"
    building.generation_prompt = f"[student photos] {str(state.get('brief', ''))[:500]}"
    await db.flush()
    try:
        await queue_ai_generation_task(
            db, building, prompt, mode="multi_image", engine="meshy",
            photo_reference_keys=selected_keys, photo_batch_id=state["batch_id"],
            photo_audit_id=str(audit_id),
        )
    except Exception as exc:
        await refund_photo_tokens(db, str(audit_id))
        raise HTTPException(status_code=503, detail="Could not start 3D generation. Your tokens were restored.") from exc
    return GenerationStatusResponse(status="generating", progress=0)


@router.get("/{building_id}/generation-status", response_model=GenerationStatusResponse)
async def get_generation_status(
    building_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Get the current AI generation status for a building."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_permission(building.project_id, user, db)

    # Try to get real progress from Celery task
    progress = None
    step = None
    if building.generation_status == "generating":
        celery_task_id = (building.specifications or {}).get("celery_task_id")
        if celery_task_id:
            result = celery_app.AsyncResult(celery_task_id)
            meta = result.info if isinstance(result.info, dict) else {}
            progress = int((meta.get("progress", 0) or 0) * 100)
            step = meta.get("step", "")

    # If still generating but model_url exists, it's the preview model
    preview_url = None
    if building.generation_status == "generating" and building.model_url:
        preview_url = building.model_url

    return GenerationStatusResponse(
        status=building.generation_status or "idle",
        progress=progress,
        step=step,
        model_url=building.model_url if building.generation_status == "completed" else None,
        preview_model_url=preview_url,
        meshy_task_id=building.meshy_task_id,
    )


@router.post("/{building_id}/cancel-generation")
async def cancel_generation(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an in-progress 3D model generation for a building."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_permission(building.project_id, user, db, required="editor")

    if building.generation_status != "generating":
        return {"status": "not_generating", "building_id": str(building_id)}

    # Revoke the Celery task
    celery_task_id = (building.specifications or {}).get("celery_task_id")
    if celery_task_id:
        celery_app.control.revoke(celery_task_id, terminate=True)

    # Reset building generation state
    building.generation_status = "idle"
    building.meshy_task_id = None
    await db.commit()

    return {"status": "cancelled", "building_id": str(building_id)}


@router.post("/batch-cancel-generation")
async def batch_cancel_generation(
    body: dict,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Cancel in-progress 3D generation for multiple buildings at once."""
    building_ids = body.get("building_ids", [])
    if not isinstance(building_ids, list) or len(building_ids) > 100:
        raise HTTPException(status_code=422, detail="Provide at most 100 building IDs")
    try:
        ids = list(dict.fromkeys(uuid.UUID(str(bid)) for bid in building_ids))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=422, detail="Invalid building ID") from None
    buildings = []
    # Authorize the whole batch before any task is revoked.
    for bid in ids:
        result = await db.execute(select(Building).where(Building.id == bid))
        building = result.scalar_one_or_none()
        if building is None:
            continue
        await check_project_permission(building.project_id, user, db, required="editor")
        buildings.append(building)

    cancelled = 0
    for building in buildings:
        if building.generation_status != "generating":
            continue
        celery_task_id = (building.specifications or {}).get("celery_task_id")
        if celery_task_id:
            celery_app.control.revoke(celery_task_id, terminate=True)
        building.generation_status = "idle"
        building.meshy_task_id = None
        cancelled += 1

    await db.commit()
    return {"status": "cancelled", "cancelled_count": cancelled}


@router.get("/ai/templates", response_model=list[AITemplate])
async def get_ai_templates():
    """Get the list of pre-built AI generation templates."""
    return AI_TEMPLATES


# =============================================================================
# Render Preview Endpoints
# =============================================================================


@router.post("/{building_id}/render-preview", response_model=RenderPreviewResponse)
async def generate_render_preview(
    building_id: uuid.UUID,
    req: RenderPreviewRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI render preview image for a building."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == building.project_id,
                ProjectShare.user_id == user.id,
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    if not settings.stability_api_key:
        raise HTTPException(
            status_code=400,
            detail="STABILITY_API_KEY is not configured. Add your Stability AI API key to the .env file.",
        )

    # Update building preview status
    building.preview_status = "generating"
    await db.flush()

    # Resolve style for prompt enrichment
    style_id = req.style or building.architectural_style or getattr(project, "default_style", None)

    # Queue Celery task
    from app.tasks.render_preview import generate_render_preview as render_task

    render_task.delay(
        str(building_id),
        req.prompt,
        req.source_type,
        req.source_image_url,
        style_id,
    )

    # Return a placeholder response
    return RenderPreviewResponse(
        id=uuid.uuid4(),
        building_id=building_id,
        image_url="",
        prompt=req.prompt,
        style=style_id,
        source_type=req.source_type,
        source_image_url=req.source_image_url,
        created_at=building.created_at,
    )


@router.get("/{building_id}/render-previews", response_model=list[RenderPreviewResponse])
async def get_render_previews(
    building_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
    share_token: str | None = None,
):
    """Get all render previews for a building."""
    building_result = await db.execute(select(Building).where(Building.id == building_id))
    building = building_result.scalar_one_or_none()
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await check_project_read_access(building.project_id, user, db, share_token)
    result = await db.execute(
        select(RenderPreview).where(RenderPreview.building_id == building_id).order_by(RenderPreview.created_at.desc())
    )
    return result.scalars().all()


# =============================================================================
# Generation Engines
# =============================================================================


@router.get("/ai/engines", response_model=list[GenerationEngineInfo])
async def get_engines():
    """Get the list of available 3D generation engines."""
    engines = [
        GenerationEngineInfo(
            id="procedural",
            name="Procedural",
            description="Local geometry generation from building data. Instant, no API key required.",
            available=True,
            features=["instant", "LOD variants", "PBR materials", "no API key"],
        ),
        GenerationEngineInfo(
            id="meshy",
            name="Meshy.ai",
            description="AI text/image-to-3D with PBR textures and refinement step.",
            available=bool(settings.meshy_api_key),
            features=["text-to-3D", "image-to-3D", "PBR textures", "refinement"],
        ),
        GenerationEngineInfo(
            id="tripo",
            name="Tripo3D",
            description="Fast AI 3D generation with smart low-poly optimization and mesh segmentation.",
            available=bool(settings.tripo_api_key),
            features=["text-to-3D", "image-to-3D", "smart low-poly", "mesh segmentation", "fast (~10-45s)"],
        ),
    ]
    return engines
