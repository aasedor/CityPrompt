"""Bounded architectural-video pilot endpoints."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    check_project_permission,
    check_project_read_access,
    get_current_user,
    is_admin_or_above,
    require_auth,
)
from app.models.models import ApiUsageLog, Building, Project, SiteZone, User
from app.schemas.direct_3d_render import (
    Direct3DCameraManifest,
    Direct3DCommunityZoneClaim,
    Direct3DInstanceDescriptor,
    Direct3DMaterialDescriptor,
    Direct3DResidualLandscapeClaim,
    Direct3DSemanticClass,
)
from app.services.grok_video import (
    GrokRequestError,
    build_grok_video_prompt,
    estimate_grok_video_cost,
    grok_model_for,
    grok_runtime_error,
    request_grok_video_once,
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
    GuideImage,
    PreviewVideo,
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
from app.services.vace_video import (
    VaceRequestError,
    estimate_vace_depth_cost,
    request_vace_depth_video_once,
    vace_runtime_error,
)
from app.services.video_controls import (
    ControlVideo,
    ControlVideoEncoding,
    ControlVideoRole,
    DepthWindow,
    decode_control_video,
    inspect_control_video,
    normalize_control_video,
)
from app.services.video_fidelity import FidelityStatus, score_video_fidelity
from app.services.video_prompts import (
    DEFAULT_LOOK_STYLE,
    STUDENT_NOTE_MAX_CHARS,
    LookStyle,
    PromptProfile,
    build_look_sheet,
    build_omni_look_prompt,
    build_vace_depth_prompt,
)
from app.services.video_providers import (
    VIDEO_PROVIDER_IDS,
    VIDEO_PROVIDERS,
    provider_setting_error,
    video_provider,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pilot policy lives in the provider registry; these names remain for callers.
PILOT_MAX_PROVIDER_CALLS = VIDEO_PROVIDERS["omni"].max_calls
SEEDANCE_PILOT_MAX_PROVIDER_CALLS = VIDEO_PROVIDERS["seedance_mini"].max_calls
INTERNAL_ENHANCE_MAX_RUNS: None = None
VACE_PILOT_MAX_PROVIDER_CALLS = VIDEO_PROVIDERS["vace_depth"].max_calls
GROK_PILOT_MAX_PROVIDER_CALLS = VIDEO_PROVIDERS["grok_video"].max_calls
VIDEO_CREDIT_COST = VIDEO_PROVIDERS["omni"].credit_cost
SEEDANCE_VIDEO_CREDIT_COST = VIDEO_PROVIDERS["seedance_mini"].credit_cost
VACE_VIDEO_CREDIT_COST = VIDEO_PROVIDERS["vace_depth"].credit_cost
GROK_VIDEO_CREDIT_COST = VIDEO_PROVIDERS["grok_video"].credit_cost
ESTIMATED_OMNI_COST_PER_SECOND_USD = Decimal("0.10")
# Structure Lock works at fal's 720p ceiling; High sources are downsampled.
VACE_CONTROL_SIZE = (1280, 720)

CameraMotion = Literal["path_follow", "street_walkby", "detail_flythrough"]
ControlMode = Literal["single_frame", "multi_keyframe", "preview_video"]
VideoProvider = Literal["omni", "seedance_mini", "internal_enhance", "vace_depth", "grok_video"]
SeedanceReferenceMode = Literal["preview_only", "preview_plus_keyframes"]
InternalEnhanceQuality = Literal["fast", "gpu_detail"]
RenderQuality = Literal["draft", "high"]
CaptureEncoder = Literal["webcodecs_h264", "media_recorder_webm"]
MAX_GEOMETRY_CONTROL_BYTES = 96 * 1024 * 1024


class RoutePoint(BaseModel):
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)


class VideoDepthWindowClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    near_meters: float = Field(..., gt=0)
    far_meters: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_order(self) -> "VideoDepthWindowClaim":
        if self.far_meters <= self.near_meters:
            raise ValueError("The depth window's far distance must exceed its near distance.")
        return self


class VideoControlVideo(BaseModel):
    """A per-frame geometry track rendered from the same camera poses as the preview."""

    model_config = ConfigDict(extra="forbid")

    role: ControlVideoRole
    video_base64: str = Field(..., min_length=100, max_length=16_000_000)
    mime_type: str = Field(..., max_length=100)
    width: int = Field(..., ge=640, le=1920)
    height: int = Field(..., ge=360, le=1080)
    frame_count: Literal[192]
    fps: Literal[24]
    encoding: ControlVideoEncoding
    depth_window: VideoDepthWindowClaim | None = None


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
    material_checkpoint_count: int = Field(default=0, ge=0, le=6)
    motion_frame_count: int = Field(default=0, ge=0, le=192)
    control_video_roles: list[ControlVideoRole] = Field(default_factory=list, max_length=2)


class VideoGeometryCheckpoint(BaseModel):
    """Same-camera renderer facts persisted for temporal geometry review."""

    model_config = ConfigDict(extra="forbid")

    progress: float = Field(..., ge=0, le=1)
    beauty_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    object_id_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    object_id_manifest: dict[str, Direct3DSemanticClass]
    instance_id_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    instance_id_manifest: dict[str, Direct3DInstanceDescriptor]
    depth_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    normal_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    material_id_image_base64: str = Field(..., min_length=32, max_length=20_000_000)
    material_id_manifest: dict[str, Direct3DMaterialDescriptor]
    camera: Direct3DCameraManifest

    @model_validator(mode="after")
    def validate_manifests(self) -> "VideoGeometryCheckpoint":
        for label, manifest in (
            ("object_id_manifest", self.object_id_manifest),
            ("instance_id_manifest", self.instance_id_manifest),
            ("material_id_manifest", self.material_id_manifest),
        ):
            if not 1 <= len(manifest) <= 2048:
                raise ValueError(f"{label} must contain between 1 and 2048 colors")
            if any(not re.fullmatch(r"#[0-9a-fA-F]{6}", color) for color in manifest):
                raise ValueError(f"{label} colors must use #RRGGBB")
            if any(color.upper() == "#000000" for color in manifest):
                raise ValueError(f"{label} reserves #000000 for context")
        return self


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
    geometry_checkpoints: list[VideoGeometryCheckpoint] = Field(default_factory=list, max_length=6)
    capture_profile: VideoCaptureProfile | None = None
    control_videos: list[VideoControlVideo] = Field(default_factory=list, max_length=2)
    # Optional appearance authority: frame 0 of this route, finished by the
    # Direct 3D image pipeline in the same look. Engines that accept a
    # reference image (Omni, Structure Lock) match its materials and light.
    anchor_image_base64: str | None = Field(default=None, max_length=20_000_000)
    route_points: list[RoutePoint] = Field(..., min_length=2, max_length=24)
    camera_motion: CameraMotion = "path_follow"
    duration_seconds: Literal[8] = 8
    # Look sheet: the short, structured description of the finished footage.
    # Geometry, camera and timing travel as data (preview and control videos),
    # so the prompt never restates the plan.
    look_style: LookStyle = DEFAULT_LOOK_STYLE
    add_people: bool = False
    add_vehicles: bool = False
    student_note: str = Field(default="", max_length=STUDENT_NOTE_MAX_CHARS)
    prompt_profile: PromptProfile = "look_sheet"
    # Legacy per-zone lock prose; only the legacy profile (and Seedance) reads it.
    scene_brief: str | None = Field(default=None, min_length=20, max_length=12_000)
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
    geometry_checkpoint_count: int = 0
    scene_revision_sha256: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")
    prompt_chars: int = 0
    negative_prompt_preview: str | None = None
    look_style: str | None = None
    prompt_profile: PromptProfile = "look_sheet"
    control_video_roles: list[str] = Field(default_factory=list)
    anchor_attached: bool = False


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
    protected_instance_min_score: float | None = None
    temporal_consistency_score: float | None = None
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
    look_style: str | None = None
    add_people: bool | None = None
    add_vehicles: bool | None = None
    student_note: str | None = None
    prompt_profile: str | None = None
    negative_prompt: str | None = None
    prompt_chars: int | None = None
    control_video_roles: list[str] = Field(default_factory=list)
    geometry_score: float | None = None
    geometry_min_score: float | None = None
    geometry_status: FidelityStatus | None = None
    geometry_samples: list[dict[str, float]] = Field(default_factory=list)
    geometry_source: str | None = None
    grok_reference_mode: str | None = None
    provider_cost_usd: float | None = None
    anchor_attached: bool | None = None
    anchor_image_url: str | None = None


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
    if provider in VIDEO_PROVIDERS:
        return provider
    return "omni"


def _provider_cap(provider: VideoProvider) -> int | None:
    return video_provider(provider).max_calls


def _provider_credit_cost(provider: VideoProvider) -> int:
    return video_provider(provider).credit_cost


def _estimated_cost_usd(req: VideoPilotRequest, settings) -> float:
    if req.provider == "seedance_mini":
        return estimate_seedance_mini_cost(
            input_video_seconds=req.duration_seconds,
            output_video_seconds=req.duration_seconds,
        )
    if req.provider == "vace_depth":
        return estimate_vace_depth_cost(output_video_seconds=req.duration_seconds)
    if req.provider == "grok_video":
        return estimate_grok_video_cost(
            model=grok_model_for(
                req.control_mode,
                generation_model=settings.grok_video_model,
                edit_model=settings.grok_video_edit_model,
            ),
            output_video_seconds=req.duration_seconds,
        )
    if req.provider == "internal_enhance":
        return 0.0
    return float(ESTIMATED_OMNI_COST_PER_SECOND_USD * req.duration_seconds)


def _provider_runtime_error(req: VideoPilotRequest, preview: PreviewVideo | None) -> str | None:
    if req.provider == "seedance_mini" and preview:
        return seedance_runtime_error(preview.mime_type)
    if req.provider == "internal_enhance":
        return internal_video_runtime_error(require_upscaler=req.internal_enhance_quality == "gpu_detail")
    if req.provider == "vace_depth":
        return vace_runtime_error()
    if req.provider == "grok_video":
        return grok_runtime_error(req.control_mode, preview.mime_type if preview else None)
    return None


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
    control_mode: str = "preview_video",
) -> str:
    if provider == "seedance_mini":
        return SEEDANCE_MINI_ENDPOINT
    if provider == "internal_enhance":
        runtime = internal_video_runtime()
        return runtime.model if internal_quality == "gpu_detail" else INTERNAL_VIDEO_MODEL
    if provider == "vace_depth":
        return settings.vace_depth_endpoint
    if provider == "grok_video":
        return grok_model_for(
            control_mode,
            generation_model=settings.grok_video_model,
            edit_model=settings.grok_video_edit_model,
        )
    return settings.omni_video_model


def _provider_label(provider: VideoProvider) -> str:
    return video_provider(provider).label


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
    checkpoint_controls = list(attempt.get("geometry_checkpoint_controls") or [])
    instance_map_urls = [
        str(control.get("images", {}).get("instance_id") or "")
        for control in checkpoint_controls
        if control.get("images", {}).get("instance_id")
    ]
    instance_map_bytes = (
        await asyncio.gather(*(asyncio.to_thread(_read_storage_file, url, project_id) for url in instance_map_urls))
        if instance_map_urls
        else []
    )
    depth_url = dict(attempt.get("control_video_urls") or {}).get("depth")
    depth_bytes = await asyncio.to_thread(_read_storage_file, depth_url, project_id) if depth_url else None
    report = await asyncio.to_thread(
        score_video_fidelity,
        generated_video=video_bytes,
        duration_seconds=int(attempt.get("duration_seconds") or 8),
        preview_video=preview_bytes,
        preview_mime_type="video/webm" if str(preview_url).endswith(".webm") else "video/mp4",
        route_keyframes=keyframe_bytes,
        instance_id_maps=instance_map_bytes,
        depth_video=depth_bytes,
        depth_mime_type="video/webm" if str(depth_url).endswith(".webm") else "video/mp4",
    )
    return report.metadata()


def _decode_geometry_checkpoints(req: VideoPilotRequest) -> list[dict[str, Any]]:
    decoded: list[dict[str, Any]] = []
    total_bytes = 0
    previous_progress = -1.0
    for index, checkpoint in enumerate(req.geometry_checkpoints, start=1):
        if checkpoint.progress <= previous_progress:
            raise ValueError("Geometry checkpoint progress values must be strictly increasing.")
        previous_progress = checkpoint.progress
        images = {
            "beauty": decode_guide_image(checkpoint.beauty_image_base64),
            "object_id": decode_guide_image(checkpoint.object_id_image_base64),
            "instance_id": decode_guide_image(checkpoint.instance_id_image_base64),
            "depth": decode_guide_image(checkpoint.depth_image_base64),
            "normal": decode_guide_image(checkpoint.normal_image_base64),
            "material_id": decode_guide_image(checkpoint.material_id_image_base64),
        }
        dimensions = {(image.width, image.height) for image in images.values()}
        if len(dimensions) != 1:
            raise ValueError(f"Geometry checkpoint {index} images must have identical dimensions.")
        metadata_keys = {"object_id", "instance_id", "depth", "normal", "material_id"}
        if any(images[key].mime_type != "image/png" for key in metadata_keys):
            raise ValueError(f"Geometry checkpoint {index} metadata passes must be PNG.")
        total_bytes += sum(len(image.data) for image in images.values())
        decoded.append({"progress": checkpoint.progress, "images": images, "claim": checkpoint})
    if total_bytes > MAX_GEOMETRY_CONTROL_BYTES:
        raise ValueError("Geometry checkpoints exceed the 96 MB pilot limit.")
    if req.capture_profile:
        claimed = req.capture_profile.geometry_checkpoint_count
        if claimed != len(decoded):
            raise ValueError("The geometry checkpoint count does not match the capture profile.")
        expected_counts = (
            req.capture_profile.semantic_checkpoint_count,
            req.capture_profile.instance_checkpoint_count,
            req.capture_profile.depth_checkpoint_count,
            req.capture_profile.normal_checkpoint_count,
            req.capture_profile.material_checkpoint_count,
        )
        if any(count != len(decoded) for count in expected_counts):
            raise ValueError("The geometry pass counts do not match the supplied checkpoints.")
    return decoded


def _require_provider_setting(provider: VideoProvider, settings) -> None:
    required_setting = video_provider(provider).required_setting
    if required_setting and not getattr(settings, required_setting, ""):
        raise HTTPException(status_code=503, detail=provider_setting_error(provider))


def _decode_control_videos(req: VideoPilotRequest, preview: PreviewVideo | None) -> list[ControlVideo]:
    """Validate the geometry tracks against the preview they were rendered with."""
    if not req.control_videos:
        if req.capture_profile and req.capture_profile.control_video_roles:
            raise ValueError("The capture profile claims control videos that were not supplied.")
        return []
    if req.control_mode != "preview_video" or preview is None:
        raise ValueError("Control videos ride with the deterministic preview video.")
    roles = [claim.role for claim in req.control_videos]
    if len(set(roles)) != len(roles):
        raise ValueError("Each control video role may be supplied once.")
    if req.capture_profile and sorted(req.capture_profile.control_video_roles) != sorted(roles):
        raise ValueError("The capture profile's control video roles do not match the supplied tracks.")
    decoded: list[ControlVideo] = []
    for claim in req.control_videos:
        control = decode_control_video(
            role=claim.role,
            video_base64=claim.video_base64,
            mime_type=claim.mime_type,
            width=claim.width,
            height=claim.height,
            frame_count=claim.frame_count,
            fps=claim.fps,
            encoding=claim.encoding,
            depth_window=(
                DepthWindow(claim.depth_window.near_meters, claim.depth_window.far_meters)
                if claim.depth_window
                else None
            ),
        )
        inspect_control_video(
            control,
            expected_width=req.capture_profile.width if req.capture_profile else claim.width,
            expected_height=req.capture_profile.height if req.capture_profile else claim.height,
        )
        decoded.append(control)
    return decoded


INTERNAL_ENHANCE_DEFAULT_BRIEF = (
    "Preserve every authored building, open space, and surrounding context exactly as depicted in the route preview."
)


def _effective_prompt_profile(req: VideoPilotRequest) -> PromptProfile:
    """Seedance and the local cleanup still read the legacy prose; look-sheet engines never do."""
    if video_provider(req.provider).prompt_policy != "look_sheet":
        return "legacy"
    return req.prompt_profile


ANCHOR_PROVIDERS: frozenset[str] = frozenset({"omni", "vace_depth"})


def _decode_anchor_image(req: VideoPilotRequest) -> GuideImage | None:
    """Validate the optional anchor frame; only the preview edit of a look-sheet engine can use one."""
    if not req.anchor_image_base64:
        return None
    if req.control_mode != "preview_video":
        raise ValueError("An anchor frame only applies when finishing the route preview.")
    if req.provider not in ANCHOR_PROVIDERS or _effective_prompt_profile(req) != "look_sheet":
        raise ValueError(
            f"{_provider_label(req.provider)} does not take an anchor frame; remove it or choose Omni or Structure Lock."
        )
    try:
        return decode_guide_image(req.anchor_image_base64)
    except ValueError as exc:
        raise ValueError(f"Anchor frame: {exc}") from exc


def _build_provider_prompt(
    req: VideoPilotRequest,
    *,
    keyframe_count: int,
    anchor_attached: bool = False,
) -> tuple[str, str | None]:
    """Return (prompt, negative_prompt) for the provider and prompt profile."""
    if req.provider == "internal_enhance":
        return build_internal_video_contract(req.scene_brief or INTERNAL_ENHANCE_DEFAULT_BRIEF), None
    if _effective_prompt_profile(req) == "legacy":
        if not req.scene_brief:
            raise ValueError("The legacy prompt profile requires a scene brief.")
        return (
            build_cinematic_prompt(
                route_points=[point.model_dump() for point in req.route_points],
                camera_motion=req.camera_motion,
                scene_brief=req.scene_brief,
                duration_seconds=req.duration_seconds,
                control_mode=req.control_mode,
                keyframe_count=keyframe_count if req.control_mode == "preview_video" else keyframe_count or 1,
                provider=req.provider,
            ),
            None,
        )
    sheet = build_look_sheet(
        look_style=req.look_style,
        add_people=req.add_people,
        add_vehicles=req.add_vehicles,
        student_note=req.student_note,
        anchor_attached=anchor_attached,
    )
    if req.provider == "vace_depth":
        return build_vace_depth_prompt(sheet)
    if req.provider == "grok_video":
        return build_grok_video_prompt(camera_motion=req.camera_motion, control_mode=req.control_mode, sheet=sheet), None
    return build_omni_look_prompt(sheet), None


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
        geometry_checkpoints = _decode_geometry_checkpoints(req)
        control_videos = _decode_control_videos(req, preview)
        anchor = _decode_anchor_image(req)
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
            if req.provider in {"omni", "internal_enhance", "vace_depth", "grok_video"} and keyframes:
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
        spec = video_provider(req.provider)
        if req.control_mode not in spec.control_modes:
            raise ValueError(f"{spec.label} requires the deterministic preview-video mode.")
        missing_roles = sorted(spec.required_control_videos - {control.role for control in control_videos})
        if missing_roles:
            raise ValueError(
                f"{spec.label} needs the {', '.join(missing_roles)} control track. "
                "Prepare the preview in a browser with WebCodecs (Chrome or Edge), then check again."
            )
        prompt, negative_prompt = _build_provider_prompt(
            req,
            keyframe_count=len(keyframes),
            anchor_attached=anchor is not None,
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:  # Missing OpenCV/ffmpeg on the Video Render server.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return guide, keyframes, preview, geometry_checkpoints, control_videos, anchor, prompt, negative_prompt


@router.post("/preflight", response_model=VideoPreflightResponse)
async def preflight_video(
    req: VideoPilotRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Validate the complete request without calling a provider or consuming a pilot slot."""
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    _require_provider_setting(req.provider, settings)
    guide, keyframes, preview, geometry_checkpoints, control_videos, anchor, prompt, negative_prompt = _preflight_values(
        req
    )
    runtime_error = _provider_runtime_error(req, preview)
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
    estimated_cost = _estimated_cost_usd(req, settings)
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
        model=_provider_model(req.provider, settings, req.internal_enhance_quality, req.control_mode),
        reference_image_count=len(keyframes),
        geometry_checkpoint_count=len(geometry_checkpoints),
        scene_revision_sha256=scene_revision_sha256,
        prompt_chars=len(prompt),
        negative_prompt_preview=negative_prompt,
        look_style=req.look_style if _effective_prompt_profile(req) == "look_sheet" else None,
        prompt_profile=_effective_prompt_profile(req),
        control_video_roles=[control.role for control in control_videos],
        anchor_attached=anchor is not None,
    )


@router.get("/projects/{project_id}", response_model=VideoPilotStateResponse)
async def list_video_attempts(
    project_id: uuid.UUID,
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    share_token: str | None = None,
):
    await check_project_read_access(project_id, user, db, share_token)
    project = await db.get(Project, project_id)
    attempts = [dict(item) for item in (project.metadata_ or {}).get("video_pilot_attempts", [])] if project else []
    if share_token:
        # Public presentations contain completed videos, not failed attempts,
        # provider prompts, capture inputs, or interaction identifiers.
        attempts = [
            {
                **item,
                "prompt": None,
                "error": None,
                "guide_image_url": None,
                "anchor_image_url": None,
                "interaction_id": None,
                "request_id": "",
            }
            for item in attempts
            if item.get("status") == "complete" and item.get("video_url")
        ]
    omni_usage = _provider_usage(attempts, "omni")
    return VideoPilotStateResponse(
        attempts=[_public_attempt(item) for item in reversed(attempts)],
        attempts_used=omni_usage.attempts_used,
        attempts_remaining=omni_usage.attempts_remaining,
        provider_usage={provider_id: _provider_usage(attempts, provider_id) for provider_id in VIDEO_PROVIDER_IDS},
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
    _require_provider_setting(req.provider, settings)
    guide, keyframes, preview, geometry_checkpoints, control_videos, anchor, prompt, negative_prompt = _preflight_values(
        req
    )
    prompt_profile = _effective_prompt_profile(req)
    depth_control = next((control for control in control_videos if control.role == "depth"), None)
    runtime_error = _provider_runtime_error(req, preview)
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
    for control in control_videos:
        control_hash.update(control.data)
    if anchor:
        control_hash.update(anchor.data)
    for checkpoint in geometry_checkpoints:
        for image in checkpoint["images"].values():
            control_hash.update(image.data)
        control_hash.update(
            json.dumps(
                checkpoint["claim"].model_dump(
                    mode="json",
                    exclude={
                        "beauty_image_base64",
                        "object_id_image_base64",
                        "instance_id_image_base64",
                        "depth_image_base64",
                        "normal_image_base64",
                        "material_id_image_base64",
                    },
                ),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    guide_hash = control_hash.hexdigest()
    estimated_cost = _estimated_cost_usd(req, settings)
    resource_updates = (
        await _project_internal_resources(db, req.project_id) if req.provider == "internal_enhance" else {}
    )
    entry = {
        "id": attempt_id,
        "request_id": str(req.request_id),
        "provider": req.provider,
        "model": _provider_model(req.provider, settings, req.internal_enhance_quality, req.control_mode),
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
        "negative_prompt": negative_prompt,
        "prompt_chars": len(prompt),
        "prompt_profile": prompt_profile,
        "look_style": req.look_style if prompt_profile == "look_sheet" else None,
        "add_people": req.add_people if prompt_profile == "look_sheet" else None,
        "add_vehicles": req.add_vehicles if prompt_profile == "look_sheet" else None,
        "student_note": (req.student_note or None) if prompt_profile == "look_sheet" else None,
        "estimated_cost_usd": estimated_cost,
        "guide_sha256": guide_hash,
        "scene_revision_sha256": scene_revision_sha256,
        "reference_image_count": len(keyframes),
        "geometry_checkpoint_count": len(geometry_checkpoints),
        "control_video_roles": [control.role for control in control_videos],
        "anchor_attached": anchor is not None,
        "anchor_image_url": None,
        "fidelity_status": "pending" if preview or len(keyframes) >= 2 else None,
        **resource_updates,
    }
    attempts.append(entry)
    meta["video_pilot_attempts"] = attempts
    project.metadata_ = meta
    await db.commit()

    guide_extension = "png" if primary_guide.mime_type == "image/png" else "jpg"
    guide_key = f"projects/{req.project_id}/video-render/{attempt_id}/route-guide.{guide_extension}"
    video_name = video_provider(req.provider).output_name
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
        anchor_image_url = None
        if anchor:
            anchor_extension = "png" if anchor.mime_type == "image/png" else "jpg"
            anchor_key = f"projects/{req.project_id}/video-render/{attempt_id}/controls/anchor.{anchor_extension}"
            await _upload_to_storage(anchor_key, anchor.data, anchor.mime_type)
            anchor_image_url = f"/api/v1/files/{anchor_key}"
        control_video_urls: dict[str, str] = {}
        control_video_profile: list[dict[str, Any]] = []
        for control in control_videos:
            control_key = (
                f"projects/{req.project_id}/video-render/{attempt_id}/controls/{control.role}-control{control.suffix}"
            )
            await _upload_to_storage(control_key, control.data, control.mime_type)
            control_video_urls[control.role] = f"/api/v1/files/{control_key}"
            control_video_profile.append(
                {
                    "role": control.role,
                    "width": control.width,
                    "height": control.height,
                    "frame_count": control.frame_count,
                    "fps": control.fps,
                    "encoding": control.encoding,
                    "depth_window": (
                        {"near_meters": control.depth_window.near_meters, "far_meters": control.depth_window.far_meters}
                        if control.depth_window
                        else None
                    ),
                }
            )
        geometry_checkpoint_controls: list[dict[str, Any]] = []
        for index, checkpoint in enumerate(geometry_checkpoints, start=1):
            base_key = f"projects/{req.project_id}/video-render/{attempt_id}/controls/geometry-{index:02d}"
            image_urls: dict[str, str] = {}
            for role, image in checkpoint["images"].items():
                image_key = f"{base_key}/{role}.png"
                await _upload_to_storage(image_key, image.data, "image/png")
                image_urls[role] = f"/api/v1/files/{image_key}"
            manifest_key = f"{base_key}/control.json"
            manifest_payload = json.dumps(
                checkpoint["claim"].model_dump(
                    mode="json",
                    exclude={
                        "beauty_image_base64",
                        "object_id_image_base64",
                        "instance_id_image_base64",
                        "depth_image_base64",
                        "normal_image_base64",
                        "material_id_image_base64",
                    },
                ),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            await _upload_to_storage(manifest_key, manifest_payload, "application/json")
            geometry_checkpoint_controls.append(
                {
                    "progress": checkpoint["progress"],
                    "images": image_urls,
                    "manifest_url": f"/api/v1/files/{manifest_key}",
                }
            )
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            guide_image_url=guide_url,
            route_keyframe_urls=route_keyframe_urls,
            preview_video_url=preview_video_url,
            anchor_image_url=anchor_image_url,
            control_video_urls=control_video_urls,
            control_video_profile=control_video_profile,
            geometry_checkpoint_controls=geometry_checkpoint_controls,
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

    provider_spec = video_provider(req.provider)
    provider_name = provider_spec.vendor
    operation = provider_spec.operation
    model = _provider_model(req.provider, settings, req.internal_enhance_quality, req.control_mode)
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
        elif req.provider == "vace_depth":
            if preview is None or depth_control is None:  # Defense in depth after request validation.
                raise ValueError("Structure Lock requires the deterministic preview and its depth track.")
            control_mp4 = await normalize_control_video(
                depth_control,
                width=VACE_CONTROL_SIZE[0],
                height=VACE_CONTROL_SIZE[1],
            )
            result = await request_vace_depth_video_once(
                api_key=settings.fal_key,
                endpoint=settings.vace_depth_endpoint,
                control_video_mp4=control_mp4,
                # The anchor is frame 0 from the same camera, so it is both
                # the identity reference and the literal first frame.
                references=[anchor] if anchor else [],
                first_frame=anchor,
                prompt=prompt,
                negative_prompt=negative_prompt or "",
                timeout_seconds=settings.vace_video_timeout_seconds,
            )
            interaction_id = result.request_id
            output_seed = result.seed
        elif req.provider == "grok_video":
            result = await request_grok_video_once(
                api_key=settings.xai_api_key,
                prompt=prompt,
                control_mode=req.control_mode,
                guide=guide,
                route_keyframes=keyframes,
                preview=preview,
                duration_seconds=req.duration_seconds,
                generation_model=settings.grok_video_model,
                edit_model=settings.grok_video_edit_model,
                timeout_seconds=settings.grok_video_timeout_seconds,
            )
            interaction_id = result.request_id
            model = result.model
            enhancement_updates = {
                "model": result.model,
                "grok_reference_mode": result.reference_mode,
                "provider_cost_usd": result.provider_cost_usd,
            }
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
                anchor_image=(req.anchor_image_base64, anchor.mime_type) if anchor and req.anchor_image_base64 else None,
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
                    instance_id_maps=[checkpoint["images"]["instance_id"].data for checkpoint in geometry_checkpoints],
                    depth_video=depth_control.data if depth_control else None,
                    depth_mime_type=depth_control.mime_type if depth_control else None,
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
                    "prompt_profile": prompt_profile,
                    "look_style": req.look_style if prompt_profile == "look_sheet" else None,
                    "prompt_chars": len(prompt),
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
        secret = str(getattr(settings, provider_spec.required_setting or "", "") or "")
        message = str(exc).replace(secret, "[redacted]")[:700] if secret else str(exc)[:700]
        if isinstance(exc, (SeedanceRequestError, VaceRequestError, GrokRequestError)) and exc.request_id:
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
                    "prompt_profile": prompt_profile,
                    "look_style": req.look_style if prompt_profile == "look_sheet" else None,
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
