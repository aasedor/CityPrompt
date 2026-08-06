"""Bounded architectural-video pilot endpoints."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, is_admin_or_above, require_auth
from app.models.models import ApiUsageLog, Building, Project, SiteZone, User
from app.schemas.direct_3d_render import (
    Direct3DCommunityZoneClaim,
    Direct3DResidualLandscapeClaim,
)
from app.services.internal_video import (
    INTERNAL_VIDEO_MODEL,
    build_internal_video_contract,
    enhance_video_locally,
    internal_video_runtime,
    internal_video_runtime_error,
)
from app.services.omni_video import (
    MAX_ROUTE_IMAGE_BYTES,
    build_cinematic_prompt,
    build_omni_payload,
    decode_guide_image,
    decode_preview_video,
    request_omni_video_once,
)
from app.services.seedance_video import (
    SEEDANCE_MINI_ENDPOINT,
    SeedanceRequestError,
    estimate_seedance_mini_cost,
    request_seedance_video_once,
    seedance_runtime_error,
)
from app.services.scene_revision import compiled_scene_revision_sha256
from app.services.video_fidelity import FidelityStatus, score_video_fidelity

logger = logging.getLogger(__name__)
router = APIRouter()

PILOT_MAX_PROVIDER_CALLS = 49
SEEDANCE_PILOT_MAX_PROVIDER_CALLS = 4
INTERNAL_ENHANCE_MAX_RUNS: None = None
VIDEO_CREDIT_COST = 50
SEEDANCE_VIDEO_CREDIT_COST = 125
ESTIMATED_OMNI_COST_PER_SECOND_USD = Decimal("0.10")

CameraMotion = Literal["path_follow", "street_walkby", "detail_flythrough"]
ControlMode = Literal["single_frame", "multi_keyframe", "preview_video"]
VideoProvider = Literal["omni", "seedance_mini", "internal_enhance"]
SeedanceReferenceMode = Literal["preview_only", "preview_plus_keyframes"]
InternalEnhanceQuality = Literal["fast", "gpu_detail"]
RenderQuality = Literal["draft", "high"]
CaptureEncoder = Literal["webcodecs_h264", "media_recorder_webm"]


class RoutePoint(BaseModel):
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)


class VideoCaptureProfile(BaseModel):
    """Auditable facts about the deterministic browser source render."""

    model_config = ConfigDict(extra="forbid")

    encoder: CaptureEncoder
    fixed_timestep: Literal[True]
    frame_count: Literal[192]
    fps: Literal[24]
    width: int = Field(..., ge=640, le=1920)
    height: int = Field(..., ge=360, le=1080)
    render_width: int = Field(..., ge=640, le=4096)
    render_height: int = Field(..., ge=360, le=4096)
    tile_warmup_frame_count: int = Field(..., ge=0, le=192)
    tile_set_held: bool
    geometry_checkpoint_count: int = Field(default=0, ge=0, le=6)
    semantic_checkpoint_count: int = Field(default=0, ge=0, le=6)
    instance_checkpoint_count: int = Field(default=0, ge=0, le=6)
    depth_checkpoint_count: int = Field(default=0, ge=0, le=6)
    normal_checkpoint_count: int = Field(default=0, ge=0, le=6)
    motion_frame_count: int = Field(default=0, ge=0, le=192)


class VideoPilotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID
    provider: VideoProvider = "omni"
    seedance_reference_mode: SeedanceReferenceMode = "preview_only"
    internal_enhance_quality: InternalEnhanceQuality = "fast"
    render_quality: RenderQuality = "high"
    guide_frame_base64: str = Field(..., min_length=100, max_length=20_000_000)
    control_mode: ControlMode = "single_frame"
    route_keyframes_base64: list[str] = Field(default_factory=list, max_length=6)
    preview_video_base64: str | None = Field(default=None, max_length=34_000_000)
    preview_video_mime_type: str | None = Field(default=None, max_length=100)
    capture_profile: VideoCaptureProfile | None = None
    route_points: list[RoutePoint] = Field(..., min_length=2, max_length=24)
    camera_motion: CameraMotion = "path_follow"
    duration_seconds: Literal[8] = 8
    scene_brief: str = Field(
        default=(
            "Preserve every authored building, open space, and surrounding context exactly as depicted in Image1."
        ),
        min_length=20,
        max_length=12_000,
    )
    community_3d_claims: list[Direct3DCommunityZoneClaim] = Field(
        default_factory=list,
        max_length=2000,
    )
    residual_landscape_claim: Direct3DResidualLandscapeClaim | None = None


class VideoGenerateRequest(VideoPilotRequest):
    request_id: uuid.UUID
    confirm_paid_submission: Literal[True]


class VideoPreflightResponse(BaseModel):
    ready: bool
    provider_called: Literal[False] = False
    width: int
    height: int
    mime_type: str
    prompt_preview: str
    provider: VideoProvider
    attempts_used: int
    attempts_remaining: int | None
    max_attempts: int | None
    estimated_cost_usd: float
    model: str
    reference_image_count: int
    scene_revision_sha256: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")


class VideoAttemptResponse(BaseModel):
    id: str
    request_id: str
    provider: VideoProvider = "omni"
    model: str | None = None
    seedance_reference_mode: SeedanceReferenceMode | None = None
    internal_enhance_quality: InternalEnhanceQuality | None = None
    render_quality: RenderQuality = "draft"
    capture_profile: VideoCaptureProfile | None = None
    status: str
    style: str
    control_mode: ControlMode = "single_frame"
    camera_motion: str
    duration_seconds: int
    created_at: str
    video_url: str | None = None
    guide_image_url: str | None = None
    error: str | None = None
    interaction_id: str | None = None
    prompt: str | None = None
    estimated_cost_usd: float
    fidelity_score: float | None = None
    fidelity_min_score: float | None = None
    fidelity_status: FidelityStatus | Literal["pending"] | None = None
    fidelity_samples: list[dict[str, float]] = Field(default_factory=list)
    is_benchmark: bool = False
    benchmark_source: Literal["automatic", "user"] | None = None
    enhancement_engine: str | None = None
    resource_count: int = 0
    resource_asset_count: int = 0
    resource_families: list[str] = Field(default_factory=list)
    resource_strategy: str | None = None
    processing_seconds: float | None = None
    enhancement_warning: str | None = None
    scene_revision_sha256: str | None = Field(
        default=None,
        pattern=r"^[a-fA-F0-9]{64}$",
    )


class VideoGenerateResponse(BaseModel):
    attempt: VideoAttemptResponse
    attempts_used: int
    attempts_remaining: int | None
    provider_call_counted: bool


class VideoProviderUsage(BaseModel):
    attempts_used: int
    attempts_remaining: int | None
    max_attempts: int | None


class VideoPilotStateResponse(BaseModel):
    attempts: list[VideoAttemptResponse]
    attempts_used: int
    attempts_remaining: int
    max_attempts: int = PILOT_MAX_PROVIDER_CALLS
    provider_usage: dict[VideoProvider, VideoProviderUsage]


class VideoFidelityBackfillRequest(BaseModel):
    project_id: uuid.UUID


class VideoFidelityBackfillResponse(BaseModel):
    attempts_scored: int
    attempts_skipped: int
    benchmark_attempt_id: str | None = None


class VideoBenchmarkRequest(BaseModel):
    project_id: uuid.UUID
    attempt_id: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attempt_provider(attempt: dict) -> VideoProvider:
    provider = attempt.get("provider")
    if provider in {"omni", "seedance_mini", "internal_enhance"}:
        return provider
    return "omni"


def _provider_cap(provider: VideoProvider) -> int | None:
    if provider == "seedance_mini":
        return SEEDANCE_PILOT_MAX_PROVIDER_CALLS
    if provider == "internal_enhance":
        return INTERNAL_ENHANCE_MAX_RUNS
    return PILOT_MAX_PROVIDER_CALLS


def _provider_credit_cost(provider: VideoProvider) -> int:
    if provider == "seedance_mini":
        return SEEDANCE_VIDEO_CREDIT_COST
    if provider == "internal_enhance":
        return 0
    return VIDEO_CREDIT_COST


def _count_provider_calls(attempts: list[dict], provider: VideoProvider | None = None) -> int:
    return sum(
        1
        for attempt in attempts
        if (attempt.get("provider_call_started_at") or attempt.get("local_run_started_at"))
        and (provider is None or _attempt_provider(attempt) == provider)
    )


def _provider_usage(attempts: list[dict], provider: VideoProvider) -> VideoProviderUsage:
    used = _count_provider_calls(attempts, provider)
    maximum = _provider_cap(provider)
    return VideoProviderUsage(
        attempts_used=used,
        attempts_remaining=None if maximum is None else max(0, maximum - used),
        max_attempts=maximum,
    )


def _public_attempt(entry: dict) -> VideoAttemptResponse:
    public = {key: entry[key] for key in VideoAttemptResponse.model_fields if key in entry}
    return VideoAttemptResponse(**public)


def _provider_model(
    provider: VideoProvider,
    settings,
    internal_quality: InternalEnhanceQuality = "fast",
) -> str:
    if provider == "seedance_mini":
        return SEEDANCE_MINI_ENDPOINT
    if provider == "internal_enhance":
        runtime = internal_video_runtime()
        return runtime.model if internal_quality == "gpu_detail" else INTERNAL_VIDEO_MODEL
    return settings.omni_video_model


def _provider_label(provider: VideoProvider) -> str:
    if provider == "seedance_mini":
        return "Seedance Mini"
    if provider == "internal_enhance":
        return "Internal Enhance"
    return "Omni"


async def _project_internal_resources(db: AsyncSession, project_id: uuid.UUID) -> dict:
    """Record the exact render-locked families already baked into the route video."""
    building_result = await db.execute(select(Building).where(Building.project_id == project_id))
    zone_result = await db.execute(select(SiteZone).where(SiteZone.project_id == project_id))
    families: set[str] = set()
    asset_ids: set[str] = set()
    for building in building_result.scalars():
        assembly = (building.specifications or {}).get("legoAssembly") or {}
        family = assembly.get("module_family")
        if isinstance(family, str) and family.strip():
            families.add(family.strip())
        for instance in assembly.get("instances") or []:
            if not isinstance(instance, dict):
                continue
            instance_family = instance.get("family")
            asset_id = instance.get("asset_id")
            if isinstance(instance_family, str) and instance_family.strip():
                families.add(instance_family.strip())
            if isinstance(asset_id, str) and asset_id.strip():
                asset_ids.add(asset_id.strip())
    open_space_resources: set[str] = set()
    for zone in zone_result.scalars():
        if zone.zone_type not in {"green_space", "park", "plaza"}:
            continue
        properties = zone.properties or {}
        archetype = (
            properties.get("plaza_archetype_id") or properties.get("green_space_archetype_id") or "authored-open-space"
        )
        variant = properties.get("plaza_selected_variant_id") or properties.get("green_space_selected_variant_id")
        open_space_resources.add(f"open-space:{archetype}{f':{variant}' if variant else ''}")
    resource_families = sorted(families | open_space_resources)
    return {
        "resource_count": len(resource_families),
        "resource_families": resource_families,
        "resource_asset_count": len(asset_ids),
        "resource_strategy": "captured_render_locked_glb_and_open_space_assets",
    }


async def _locked_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id).with_for_update())
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _video_scene_conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "video_project_state_changed",
            "billed": False,
            "message": message,
        },
    )


async def _validate_video_scene_revision(
    req: VideoPilotRequest,
    db: AsyncSession,
) -> str:
    """Bind a video route to the same current compiled scene as Direct image render.

    This runs again while the project row is locked immediately before a run
    is reserved, so a changed plan cannot spend against an older browser
    capture. The returned digest is persisted with the durable attempt.
    """

    if not req.community_3d_claims:
        raise _video_scene_conflict("Generate the current site in 3D again before Video Render.")

    zones_result = await db.execute(select(SiteZone).where(SiteZone.project_id == req.project_id))
    zones = list(zones_result.scalars().all())
    buildings_result = await db.execute(select(Building).where(Building.project_id == req.project_id))
    buildings = {str(building.id): building for building in buildings_result.scalars().all()}

    # Import locally to keep the video module's schema/service dependencies
    # independent from the image-render router at import time.
    from app.api.v1.direct_3d_render import _validate_direct_3d_project_zones

    try:
        _validate_direct_3d_project_zones(
            req,  # Shared Community 3D and residual-landscape claim contract.
            zones,
            buildings,
            bind_capture_instances=False,
        )
    except HTTPException as exc:
        if exc.status_code != status.HTTP_409_CONFLICT:
            raise
        detail = exc.detail
        message = detail.get("message") if isinstance(detail, dict) else str(detail)
        raise _video_scene_conflict(message) from exc

    return compiled_scene_revision_sha256(
        req.community_3d_claims,
        req.residual_landscape_claim,
    )


async def _update_attempt(db: AsyncSession, project_id: uuid.UUID, attempt_id: str, **updates) -> dict:
    project = await _locked_project(db, project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    for index, entry in enumerate(attempts):
        if entry.get("id") == attempt_id:
            entry.update(updates)
            attempts[index] = entry
            meta["video_pilot_attempts"] = attempts
            project.metadata_ = meta
            await db.commit()
            return entry
    raise HTTPException(status_code=404, detail="Video attempt not found")


def _best_automatic_benchmark_index(attempts: list[dict]) -> int | None:
    eligible: list[tuple[int, dict]] = [
        (index, attempt)
        for index, attempt in enumerate(attempts)
        if _attempt_provider(attempt) == "omni"
        and attempt.get("status") == "complete"
        and attempt.get("style") == "source_fidelity"
        and isinstance(attempt.get("fidelity_score"), (int, float))
    ]
    if not eligible:
        return None
    # Prefer the highest mean, then the strongest worst frame. When both are
    # equal, keep the earlier result so the benchmark does not churn.
    return max(
        eligible,
        key=lambda item: (
            float(item[1]["fidelity_score"]),
            float(item[1].get("fidelity_min_score") or 0),
            -item[0],
        ),
    )[0]


async def _refresh_automatic_benchmark(db: AsyncSession, project_id: uuid.UUID) -> str | None:
    project = await _locked_project(db, project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    user_benchmark = next(
        (attempt for attempt in attempts if attempt.get("is_benchmark") and attempt.get("benchmark_source") == "user"),
        None,
    )
    if user_benchmark:
        return str(user_benchmark.get("id"))
    best_index = _best_automatic_benchmark_index(attempts)
    if best_index is None:
        return None
    for index, attempt in enumerate(attempts):
        if _attempt_provider(attempt) != "omni":
            continue
        attempt["is_benchmark"] = index == best_index
        attempt["benchmark_source"] = "automatic" if index == best_index else None
    meta["video_pilot_attempts"] = attempts
    project.metadata_ = meta
    await db.commit()
    return str(attempts[best_index].get("id"))


def _storage_key_from_file_url(url: str | None, project_id: uuid.UUID) -> str | None:
    if not url or "/api/v1/files/" not in url:
        return None
    key = url.split("/api/v1/files/", 1)[1].split("?", 1)[0]
    expected_prefix = f"projects/{project_id}/video-render/"
    return key if key.startswith(expected_prefix) else None


def _read_storage_file(url: str | None, project_id: uuid.UUID) -> bytes:
    key = _storage_key_from_file_url(url, project_id)
    if not key:
        raise ValueError("A saved fidelity-control URL is missing or outside this project.")
    from app.api.v1.files import _s3_client

    settings = get_settings()
    obj = _s3_client().get_object(Bucket=settings.s3_bucket_name, Key=key)
    return obj["Body"].read()


async def _score_saved_attempt(attempt: dict, project_id: uuid.UUID) -> dict:
    video_bytes = await asyncio.to_thread(_read_storage_file, attempt.get("video_url"), project_id)
    preview_url = attempt.get("preview_video_url")
    keyframe_urls = list(attempt.get("route_keyframe_urls") or [])
    preview_bytes = await asyncio.to_thread(_read_storage_file, preview_url, project_id) if preview_url else None
    keyframe_bytes = (
        await asyncio.gather(*(asyncio.to_thread(_read_storage_file, url, project_id) for url in keyframe_urls))
        if keyframe_urls
        else []
    )
    report = await asyncio.to_thread(
        score_video_fidelity,
        generated_video=video_bytes,
        duration_seconds=int(attempt.get("duration_seconds") or 8),
        preview_video=preview_bytes,
        preview_mime_type="video/webm" if str(preview_url).endswith(".webm") else "video/mp4",
        route_keyframes=keyframe_bytes,
    )
    return report.metadata()


def _preflight_values(req: VideoPilotRequest):
    try:
        guide = decode_guide_image(req.guide_frame_base64)
        keyframes = [decode_guide_image(value) for value in req.route_keyframes_base64]
        if sum(len(frame.data) for frame in keyframes) > MAX_ROUTE_IMAGE_BYTES:
            raise ValueError("The route keyframes exceed the 36 MB pilot limit.")
        preview = (
            decode_preview_video(req.preview_video_base64, req.preview_video_mime_type or "")
            if req.preview_video_base64
            else None
        )
        if req.control_mode == "single_frame" and (keyframes or preview):
            raise ValueError("Single-frame mode cannot include route keyframes or a preview video.")
        if req.control_mode == "multi_keyframe":
            if len(keyframes) < 2:
                raise ValueError("Multi-keyframe mode requires at least two route images.")
            if preview is not None:
                raise ValueError("Multi-keyframe mode cannot include a preview video.")
        if req.control_mode == "preview_video":
            if preview is None:
                raise ValueError("Preview-video mode requires the deterministic route preview.")
            if req.provider in {"omni", "internal_enhance"} and keyframes:
                raise ValueError("This preview-video mode sends the route video without route keyframe references.")
            if req.provider == "seedance_mini":
                expected_keyframes = 3 if req.seedance_reference_mode == "preview_plus_keyframes" else 0
                if len(keyframes) != expected_keyframes:
                    raise ValueError(
                        f"Seedance {req.seedance_reference_mode.replace('_', ' ')} requires exactly "
                        f"{expected_keyframes} route keyframes."
                    )
        if req.provider == "seedance_mini" and req.control_mode != "preview_video":
            raise ValueError("The bounded Seedance pilot requires preview-video mode.")
        if req.provider == "internal_enhance" and req.control_mode != "preview_video":
            raise ValueError("Internal Enhance requires the deterministic preview-video mode.")
        prompt = (
            build_internal_video_contract(req.scene_brief)
            if req.provider == "internal_enhance"
            else build_cinematic_prompt(
                route_points=[point.model_dump() for point in req.route_points],
                camera_motion=req.camera_motion,
                scene_brief=req.scene_brief,
                duration_seconds=req.duration_seconds,
                control_mode=req.control_mode,
                keyframe_count=len(keyframes) if req.control_mode == "preview_video" else len(keyframes) or 1,
                provider=req.provider,
            )
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return guide, keyframes, preview, prompt


@router.post("/preflight", response_model=VideoPreflightResponse)
async def preflight_video(
    req: VideoPilotRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Validate the complete request without calling a provider or consuming a pilot slot."""
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    if req.provider == "omni" and not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    if req.provider == "seedance_mini" and not settings.fal_key:
        raise HTTPException(status_code=503, detail="FAL_KEY is not configured.")
    guide, keyframes, preview, prompt = _preflight_values(req)
    if req.provider == "seedance_mini" and preview:
        runtime_error = seedance_runtime_error(preview.mime_type)
        if runtime_error:
            raise HTTPException(status_code=503, detail=runtime_error)
    if req.provider == "internal_enhance":
        runtime_error = internal_video_runtime_error(require_upscaler=req.internal_enhance_quality == "gpu_detail")
        if runtime_error:
            raise HTTPException(status_code=503, detail=runtime_error)
    scene_revision_sha256 = await _validate_video_scene_revision(req, db)
    project = await db.get(Project, req.project_id)
    attempts = list((project.metadata_ or {}).get("video_pilot_attempts", [])) if project else []
    usage = _provider_usage(attempts, req.provider)
    if usage.attempts_remaining is not None and usage.attempts_remaining <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"This project has used all {usage.max_attempts} authorized {req.provider.replace('_', ' ')} submissions.",
        )
    credit_cost = _provider_credit_cost(req.provider)
    if not is_admin_or_above(user) and user.render_credits < credit_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Video Render requires {credit_cost} credits; you have {user.render_credits}.",
        )
    if req.provider == "seedance_mini":
        estimated_cost = estimate_seedance_mini_cost(
            input_video_seconds=req.duration_seconds,
            output_video_seconds=req.duration_seconds,
        )
    elif req.provider == "internal_enhance":
        estimated_cost = 0.0
    else:
        estimated_cost = float(ESTIMATED_OMNI_COST_PER_SECOND_USD * req.duration_seconds)
    return VideoPreflightResponse(
        ready=True,
        width=guide.width,
        height=guide.height,
        mime_type=guide.mime_type,
        prompt_preview=prompt,
        provider=req.provider,
        attempts_used=usage.attempts_used,
        attempts_remaining=usage.attempts_remaining,
        max_attempts=usage.max_attempts,
        estimated_cost_usd=estimated_cost,
        model=_provider_model(req.provider, settings, req.internal_enhance_quality),
        reference_image_count=len(keyframes),
        scene_revision_sha256=scene_revision_sha256,
    )


@router.get("/projects/{project_id}", response_model=VideoPilotStateResponse)
async def list_video_attempts(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="viewer")
    project = await db.get(Project, project_id)
    attempts = [dict(item) for item in (project.metadata_ or {}).get("video_pilot_attempts", [])] if project else []
    omni_usage = _provider_usage(attempts, "omni")
    return VideoPilotStateResponse(
        attempts=[_public_attempt(item) for item in reversed(attempts)],
        attempts_used=omni_usage.attempts_used,
        attempts_remaining=omni_usage.attempts_remaining,
        provider_usage={
            "omni": omni_usage,
            "seedance_mini": _provider_usage(attempts, "seedance_mini"),
            "internal_enhance": _provider_usage(attempts, "internal_enhance"),
        },
    )


@router.post("/fidelity/backfill", response_model=VideoFidelityBackfillResponse)
async def backfill_video_fidelity(
    req: VideoFidelityBackfillRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Score existing source-fidelity videos without making provider calls."""
    await check_project_permission(req.project_id, user, db, required="editor")
    project = await db.get(Project, req.project_id)
    attempts = [dict(item) for item in (project.metadata_ or {}).get("video_pilot_attempts", [])] if project else []
    candidates = [
        attempt
        for attempt in attempts
        if attempt.get("status") == "complete"
        and attempt.get("video_url")
        and attempt.get("style") == "source_fidelity"
        and not isinstance(attempt.get("fidelity_score"), (int, float))
        and (attempt.get("preview_video_url") or len(attempt.get("route_keyframe_urls") or []) >= 2)
    ][:12]
    scored = 0
    for attempt in candidates:
        try:
            fidelity = await _score_saved_attempt(attempt, req.project_id)
            await _update_attempt(db, req.project_id, str(attempt["id"]), **fidelity)
            scored += 1
        except Exception as exc:  # Scoring is advisory and must never hide a saved render.
            logger.warning("Video fidelity backfill failed for %s: %s", attempt.get("id"), exc)
            await _update_attempt(
                db,
                req.project_id,
                str(attempt["id"]),
                fidelity_status="unavailable",
                fidelity_error=str(exc)[:300],
            )
    benchmark_id = await _refresh_automatic_benchmark(db, req.project_id)
    return VideoFidelityBackfillResponse(
        attempts_scored=scored,
        attempts_skipped=max(0, len(attempts) - len(candidates)),
        benchmark_attempt_id=benchmark_id,
    )


@router.post("/benchmark", response_model=VideoAttemptResponse)
async def set_video_benchmark(
    req: VideoBenchmarkRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Pin a completed Omni result as the user-approved fidelity benchmark."""
    await check_project_permission(req.project_id, user, db, required="editor")
    project = await _locked_project(db, req.project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    selected: dict | None = None
    for attempt in attempts:
        is_selected = attempt.get("id") == req.attempt_id
        if is_selected:
            if (
                _attempt_provider(attempt) != "omni"
                or attempt.get("status") != "complete"
                or not attempt.get("video_url")
            ):
                raise HTTPException(status_code=400, detail="Only a completed Omni video can be the benchmark.")
            selected = attempt
        if _attempt_provider(attempt) == "omni":
            attempt["is_benchmark"] = is_selected
            attempt["benchmark_source"] = "user" if is_selected else None
    if selected is None:
        raise HTTPException(status_code=404, detail="Video attempt not found")
    meta["video_pilot_attempts"] = attempts
    project.metadata_ = meta
    await db.commit()
    return _public_attempt(selected)


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    req: VideoGenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reserve a provider-specific pilot slot, then submit exactly one generation."""
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    if req.provider == "omni" and not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    if req.provider == "seedance_mini" and not settings.fal_key:
        raise HTTPException(status_code=503, detail="FAL_KEY is not configured.")
    guide, keyframes, preview, prompt = _preflight_values(req)
    if req.provider == "seedance_mini" and preview:
        runtime_error = seedance_runtime_error(preview.mime_type)
        if runtime_error:
            raise HTTPException(status_code=503, detail=runtime_error)
    if req.provider == "internal_enhance":
        runtime_error = internal_video_runtime_error(require_upscaler=req.internal_enhance_quality == "gpu_detail")
        if runtime_error:
            raise HTTPException(status_code=503, detail=runtime_error)

    # Idempotency and the hard cap are persisted before any provider contact.
    project = await _locked_project(db, req.project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    for existing in attempts:
        if existing.get("request_id") == str(req.request_id):
            provider = _attempt_provider(existing)
            usage = _provider_usage(attempts, provider)
            return VideoGenerateResponse(
                attempt=_public_attempt(existing),
                attempts_used=usage.attempts_used,
                attempts_remaining=usage.attempts_remaining,
                provider_call_counted=bool(
                    existing.get("provider_call_started_at") or existing.get("local_run_started_at")
                ),
            )

    scene_revision_sha256 = await _validate_video_scene_revision(req, db)

    usage = _provider_usage(attempts, req.provider)
    active_reservations = sum(
        1 for attempt in attempts if attempt.get("status") == "reserved" and _attempt_provider(attempt) == req.provider
    )
    if usage.max_attempts is not None and usage.attempts_used + active_reservations >= usage.max_attempts:
        raise HTTPException(
            status_code=409,
            detail=f"This project has reserved all {usage.max_attempts} authorized {req.provider.replace('_', ' ')} submissions.",
        )
    credit_cost = _provider_credit_cost(req.provider)
    if not is_admin_or_above(user) and user.render_credits < credit_cost:
        raise HTTPException(status_code=402, detail="Insufficient Video Render credits.")

    attempt_id = str(uuid.uuid4())
    primary_guide = keyframes[0] if keyframes else guide
    control_hash = hashlib.sha256()
    control_hash.update(guide.data)
    for frame in keyframes:
        control_hash.update(frame.data)
    if preview:
        control_hash.update(preview.data)
    guide_hash = control_hash.hexdigest()
    if req.provider == "seedance_mini":
        estimated_cost = estimate_seedance_mini_cost(
            input_video_seconds=req.duration_seconds,
            output_video_seconds=req.duration_seconds,
        )
    elif req.provider == "internal_enhance":
        estimated_cost = 0.0
    else:
        estimated_cost = float(ESTIMATED_OMNI_COST_PER_SECOND_USD * req.duration_seconds)
    resource_updates = (
        await _project_internal_resources(db, req.project_id) if req.provider == "internal_enhance" else {}
    )
    entry = {
        "id": attempt_id,
        "request_id": str(req.request_id),
        "provider": req.provider,
        "model": _provider_model(req.provider, settings, req.internal_enhance_quality),
        "seedance_reference_mode": req.seedance_reference_mode if req.provider == "seedance_mini" else None,
        "internal_enhance_quality": (req.internal_enhance_quality if req.provider == "internal_enhance" else None),
        "render_quality": req.render_quality,
        "capture_profile": req.capture_profile.model_dump() if req.capture_profile else None,
        "status": "reserved",
        "style": "source_fidelity",
        "control_mode": req.control_mode,
        "camera_motion": req.camera_motion,
        "duration_seconds": req.duration_seconds,
        "created_at": _now(),
        "video_url": None,
        "guide_image_url": None,
        "error": None,
        "interaction_id": None,
        "prompt": prompt,
        "estimated_cost_usd": estimated_cost,
        "guide_sha256": guide_hash,
        "scene_revision_sha256": scene_revision_sha256,
        "reference_image_count": len(keyframes),
        "fidelity_status": "pending" if preview or len(keyframes) >= 2 else None,
        **resource_updates,
    }
    attempts.append(entry)
    meta["video_pilot_attempts"] = attempts
    project.metadata_ = meta
    await db.commit()

    guide_extension = "png" if primary_guide.mime_type == "image/png" else "jpg"
    guide_key = f"projects/{req.project_id}/video-render/{attempt_id}/route-guide.{guide_extension}"
    video_name = {
        "seedance_mini": "seedance-mini.mp4",
        "internal_enhance": "internal-enhance.mp4",
        "omni": "omni.mp4",
    }[req.provider]
    video_key = f"projects/{req.project_id}/video-render/{attempt_id}/{video_name}"
    try:
        from app.api.v1.documents import _upload_to_storage

        await _upload_to_storage(guide_key, primary_guide.data, primary_guide.mime_type)
        guide_url = f"/api/v1/files/{guide_key}"
        route_keyframe_urls: list[str] = []
        for index, frame in enumerate(keyframes, start=1):
            extension = "png" if frame.mime_type == "image/png" else "jpg"
            frame_key = f"projects/{req.project_id}/video-render/{attempt_id}/controls/keyframe-{index:02d}.{extension}"
            await _upload_to_storage(frame_key, frame.data, frame.mime_type)
            route_keyframe_urls.append(f"/api/v1/files/{frame_key}")
        preview_video_url = None
        if preview:
            preview_extension = "mp4" if preview.mime_type == "video/mp4" else "webm"
            preview_key = (
                f"projects/{req.project_id}/video-render/{attempt_id}/controls/route-preview.{preview_extension}"
            )
            await _upload_to_storage(preview_key, preview.data, preview.mime_type)
            preview_video_url = f"/api/v1/files/{preview_key}"
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            guide_image_url=guide_url,
            route_keyframe_urls=route_keyframe_urls,
            preview_video_url=preview_video_url,
        )
    except Exception as exc:
        logger.exception("Video guide persistence failed before provider call")
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="preflight_failed",
            error=f"Could not save the route guide; the provider was not called: {str(exc)[:300]}",
        )
        raise HTTPException(status_code=503, detail=entry["error"]) from exc

    # From this committed timestamp onward the attempt consumes one bounded run.
    # Remote calls may incur billing; local runs remain free but are capped while
    # the pilot is being evaluated.
    run_marker = (
        {"local_run_started_at": _now()} if req.provider == "internal_enhance" else {"provider_call_started_at": _now()}
    )
    entry = await _update_attempt(
        db,
        req.project_id,
        attempt_id,
        status="generating",
        **run_marker,
    )
    if credit_cost and not is_admin_or_above(user):
        user.render_credits = max(0, user.render_credits - credit_cost)
        db.add(user)
        await db.commit()

    provider_name = {
        "seedance_mini": "fal",
        "internal_enhance": "local",
        "omni": "gemini",
    }[req.provider]
    operation = {
        "seedance_mini": "seedance_video",
        "internal_enhance": "internal_video_enhance",
        "omni": "omni_video",
    }[req.provider]
    model = _provider_model(req.provider, settings, req.internal_enhance_quality)
    interaction_id: str | None = None
    output_seed: int | None = None
    enhancement_updates: dict = {}
    try:
        if req.provider == "internal_enhance":
            if preview is None:  # Defense in depth after request validation.
                raise ValueError("Internal Enhance requires the deterministic route preview.")
            result = await enhance_video_locally(
                preview=preview,
                duration_seconds=req.duration_seconds,
                allow_upscaler=req.internal_enhance_quality == "gpu_detail",
                render_quality=req.render_quality,
            )
            model = result.model
            enhancement_updates = {
                "model": result.model,
                "enhancement_engine": result.engine,
                "processing_seconds": result.processing_seconds,
                "enhancement_warning": result.fallback_reason,
            }
        elif req.provider == "seedance_mini":
            if preview is None:  # Kept explicit for static type checking and defense in depth.
                raise ValueError("Seedance requires the deterministic route preview.")
            result = await request_seedance_video_once(
                api_key=settings.fal_key,
                preview=preview,
                keyframes=keyframes,
                prompt=prompt,
                duration_seconds=req.duration_seconds,
                timeout_seconds=settings.seedance_video_timeout_seconds,
            )
            interaction_id = result.request_id
            output_seed = result.seed
        else:
            payload = build_omni_payload(
                model=settings.omni_video_model,
                guide_base64=req.guide_frame_base64,
                guide_mime_type=guide.mime_type,
                prompt=prompt,
                duration_seconds=req.duration_seconds,
                control_mode=req.control_mode,
                route_keyframes=[
                    (value, frame.mime_type) for value, frame in zip(req.route_keyframes_base64, keyframes, strict=True)
                ],
                preview_video_base64=req.preview_video_base64,
                preview_video_mime_type=preview.mime_type if preview else None,
            )
            result = await request_omni_video_once(
                api_key=settings.gemini_api_key,
                payload=payload,
                timeout_seconds=settings.omni_video_timeout_seconds,
            )
            interaction_id = result.interaction_id
        fidelity_updates: dict = {}
        if preview or len(keyframes) >= 2:
            try:
                fidelity_report = await asyncio.to_thread(
                    score_video_fidelity,
                    generated_video=result.video_bytes,
                    duration_seconds=req.duration_seconds,
                    preview_video=preview.data if preview else None,
                    preview_mime_type=preview.mime_type if preview else None,
                    route_keyframes=[frame.data for frame in keyframes],
                )
                fidelity_updates = fidelity_report.metadata()
            except Exception as fidelity_exc:
                logger.warning("Video fidelity scoring failed for %s: %s", attempt_id, fidelity_exc)
                fidelity_updates = {
                    "fidelity_status": "unavailable",
                    "fidelity_error": str(fidelity_exc)[:300],
                }
        from app.api.v1.documents import _upload_to_storage

        await _upload_to_storage(video_key, result.video_bytes, result.mime_type)
        video_url = f"/api/v1/files/{video_key}"
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="complete",
            completed_at=_now(),
            video_url=video_url,
            interaction_id=interaction_id,
            seed=output_seed,
            size_bytes=len(result.video_bytes),
            **enhancement_updates,
            **fidelity_updates,
        )
        db.add(
            ApiUsageLog(
                provider=provider_name,
                operation=operation,
                credits_used=Decimal(credit_cost),
                task_id=attempt_id,
                user_id=user.id,
                status="success",
                metadata_={
                    "project_id": str(req.project_id),
                    "duration_seconds": req.duration_seconds,
                    "model": model,
                    "control_mode": req.control_mode,
                    "seedance_reference_mode": req.seedance_reference_mode if req.provider == "seedance_mini" else None,
                    "interaction_id": interaction_id,
                    "seed": output_seed,
                    "estimated_provider_cost_usd": estimated_cost,
                    "enhancement_engine": enhancement_updates.get("enhancement_engine"),
                    "internal_enhance_quality": (
                        req.internal_enhance_quality if req.provider == "internal_enhance" else None
                    ),
                    "render_quality": req.render_quality,
                    "capture_profile": req.capture_profile.model_dump() if req.capture_profile else None,
                    "resource_count": resource_updates.get("resource_count", 0),
                    "resource_families": resource_updates.get("resource_families", []),
                },
            )
        )
        await db.commit()
        await _refresh_automatic_benchmark(db, req.project_id)
    except Exception as exc:
        secret = (
            settings.fal_key
            if req.provider == "seedance_mini"
            else settings.gemini_api_key if req.provider == "omni" else ""
        )
        message = str(exc).replace(secret, "[redacted]")[:700] if secret else str(exc)[:700]
        if isinstance(exc, SeedanceRequestError) and exc.request_id:
            interaction_id = exc.request_id
        logger.exception("%s pilot attempt %s failed", req.provider, attempt_id)
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="failed",
            completed_at=_now(),
            error=message,
            interaction_id=interaction_id,
        )
        db.add(
            ApiUsageLog(
                provider=provider_name,
                operation=operation,
                credits_used=Decimal(credit_cost),
                task_id=attempt_id,
                user_id=user.id,
                status="failed",
                metadata_={
                    "project_id": str(req.project_id),
                    "model": model,
                    "control_mode": req.control_mode,
                    "seedance_reference_mode": req.seedance_reference_mode if req.provider == "seedance_mini" else None,
                    "interaction_id": interaction_id,
                    "estimated_provider_cost_usd": estimated_cost,
                    "resource_count": resource_updates.get("resource_count", 0),
                    "resource_families": resource_updates.get("resource_families", []),
                },
            )
        )
        await db.commit()
        cap = _provider_cap(req.provider)
        provider_label = _provider_label(req.provider)
        failure_detail = (
            f"{provider_label} run failed: {message}"
            if cap is None
            else f"{provider_label} submission failed and still counts toward the {cap}-run cap: {message}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=failure_detail,
        ) from exc

    project = await db.get(Project, req.project_id, populate_existing=True)
    latest_attempts = list((project.metadata_ or {}).get("video_pilot_attempts", [])) if project else []
    entry = next((dict(item) for item in latest_attempts if item.get("id") == attempt_id), entry)
    usage = _provider_usage(latest_attempts, req.provider)
    return VideoGenerateResponse(
        attempt=_public_attempt(entry),
        attempts_used=usage.attempts_used,
        attempts_remaining=usage.attempts_remaining,
        provider_call_counted=True,
    )
