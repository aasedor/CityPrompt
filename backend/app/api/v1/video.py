"""Bounded Gemini Omni architectural-video pilot endpoints."""

from __future__ import annotations

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
from app.models.models import ApiUsageLog, Project, User
from app.services.omni_video import (
    MAX_ROUTE_IMAGE_BYTES,
    build_cinematic_prompt,
    build_omni_payload,
    decode_guide_image,
    decode_preview_video,
    request_omni_video_once,
)

logger = logging.getLogger(__name__)
router = APIRouter()

PILOT_MAX_PROVIDER_CALLS = 46
VIDEO_CREDIT_COST = 50
ESTIMATED_OMNI_COST_PER_SECOND_USD = Decimal("0.10")

CameraMotion = Literal["path_follow", "street_walkby"]
ControlMode = Literal["single_frame", "multi_keyframe", "preview_video"]


class RoutePoint(BaseModel):
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)


class VideoPilotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID
    guide_frame_base64: str = Field(..., min_length=100, max_length=20_000_000)
    control_mode: ControlMode = "single_frame"
    route_keyframes_base64: list[str] = Field(default_factory=list, max_length=6)
    preview_video_base64: str | None = Field(default=None, max_length=34_000_000)
    preview_video_mime_type: str | None = Field(default=None, max_length=100)
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
    attempts_used: int
    attempts_remaining: int
    estimated_cost_usd: float
    model: str
    reference_image_count: int


class VideoAttemptResponse(BaseModel):
    id: str
    request_id: str
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


class VideoGenerateResponse(BaseModel):
    attempt: VideoAttemptResponse
    attempts_used: int
    attempts_remaining: int
    provider_call_counted: bool


class VideoPilotStateResponse(BaseModel):
    attempts: list[VideoAttemptResponse]
    attempts_used: int
    attempts_remaining: int
    max_attempts: int = PILOT_MAX_PROVIDER_CALLS


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _count_provider_calls(attempts: list[dict]) -> int:
    return sum(1 for attempt in attempts if attempt.get("provider_call_started_at"))


def _public_attempt(entry: dict) -> VideoAttemptResponse:
    public = {key: entry[key] for key in VideoAttemptResponse.model_fields if key in entry}
    return VideoAttemptResponse(**public)


async def _locked_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id).with_for_update())
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


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
            if keyframes:
                raise ValueError("Preview-video mode sends the route video without route keyframe references.")
        prompt = build_cinematic_prompt(
            route_points=[point.model_dump() for point in req.route_points],
            camera_motion=req.camera_motion,
            scene_brief=req.scene_brief,
            duration_seconds=req.duration_seconds,
            control_mode=req.control_mode,
            keyframe_count=len(keyframes) or 1,
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
    """Validate the complete request without calling Gemini or consuming the pilot cap."""
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    guide, keyframes, _preview, prompt = _preflight_values(req)
    project = await db.get(Project, req.project_id)
    attempts = list((project.metadata_ or {}).get("video_pilot_attempts", [])) if project else []
    used = _count_provider_calls(attempts)
    if used >= PILOT_MAX_PROVIDER_CALLS:
        raise HTTPException(status_code=409, detail="This project has used all forty-six authorized pilot video submissions.")
    if not is_admin_or_above(user) and user.render_credits < VIDEO_CREDIT_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Video Render requires {VIDEO_CREDIT_COST} credits; you have {user.render_credits}.",
        )
    return VideoPreflightResponse(
        ready=True,
        width=guide.width,
        height=guide.height,
        mime_type=guide.mime_type,
        prompt_preview=prompt,
        attempts_used=used,
        attempts_remaining=PILOT_MAX_PROVIDER_CALLS - used,
        estimated_cost_usd=float(ESTIMATED_OMNI_COST_PER_SECOND_USD * req.duration_seconds),
        model=settings.omni_video_model,
        reference_image_count=len(keyframes),
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
    used = _count_provider_calls(attempts)
    return VideoPilotStateResponse(
        attempts=[_public_attempt(item) for item in reversed(attempts)],
        attempts_used=used,
        attempts_remaining=max(0, PILOT_MAX_PROVIDER_CALLS - used),
    )


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    req: VideoGenerateRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reserve a pilot slot, then make exactly one non-retrying Omni POST."""
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    guide, keyframes, preview, prompt = _preflight_values(req)

    # Idempotency and the hard cap are persisted before any provider contact.
    project = await _locked_project(db, req.project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    for existing in attempts:
        if existing.get("request_id") == str(req.request_id):
            used = _count_provider_calls(attempts)
            return VideoGenerateResponse(
                attempt=_public_attempt(existing),
                attempts_used=used,
                attempts_remaining=max(0, PILOT_MAX_PROVIDER_CALLS - used),
                provider_call_counted=bool(existing.get("provider_call_started_at")),
            )

    used = _count_provider_calls(attempts)
    active_reservations = sum(1 for attempt in attempts if attempt.get("status") == "reserved")
    if used + active_reservations >= PILOT_MAX_PROVIDER_CALLS:
        raise HTTPException(status_code=409, detail="This project has reserved all forty-six authorized pilot video submissions.")
    if not is_admin_or_above(user) and user.render_credits < VIDEO_CREDIT_COST:
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
    estimated_cost = float(ESTIMATED_OMNI_COST_PER_SECOND_USD * req.duration_seconds)
    entry = {
        "id": attempt_id,
        "request_id": str(req.request_id),
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
        "reference_image_count": len(keyframes),
    }
    attempts.append(entry)
    meta["video_pilot_attempts"] = attempts
    project.metadata_ = meta
    await db.commit()

    guide_extension = "png" if primary_guide.mime_type == "image/png" else "jpg"
    guide_key = f"projects/{req.project_id}/video-render/{attempt_id}/route-guide.{guide_extension}"
    video_key = f"projects/{req.project_id}/video-render/{attempt_id}/omni.mp4"
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
            preview_key = f"projects/{req.project_id}/video-render/{attempt_id}/controls/route-preview.{preview_extension}"
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
            error=f"Could not save the route guide; Gemini was not called: {str(exc)[:300]}",
        )
        raise HTTPException(status_code=503, detail=entry["error"]) from exc

    # From this committed timestamp onward the attempt consumes one pilot call,
    # even if the provider times out: the remote billing outcome is ambiguous.
    entry = await _update_attempt(
        db,
        req.project_id,
        attempt_id,
        status="generating",
        provider_call_started_at=_now(),
    )
    if not is_admin_or_above(user):
        user.render_credits = max(0, user.render_credits - VIDEO_CREDIT_COST)
        db.add(user)
        await db.commit()

    payload = build_omni_payload(
        model=settings.omni_video_model,
        guide_base64=req.guide_frame_base64,
        guide_mime_type=guide.mime_type,
        prompt=prompt,
        duration_seconds=req.duration_seconds,
        control_mode=req.control_mode,
        route_keyframes=[
            (value, frame.mime_type)
            for value, frame in zip(req.route_keyframes_base64, keyframes, strict=True)
        ],
        preview_video_base64=req.preview_video_base64,
        preview_video_mime_type=preview.mime_type if preview else None,
    )
    try:
        result = await request_omni_video_once(
            api_key=settings.gemini_api_key,
            payload=payload,
            timeout_seconds=settings.omni_video_timeout_seconds,
        )
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
            interaction_id=result.interaction_id,
            size_bytes=len(result.video_bytes),
        )
        db.add(
            ApiUsageLog(
                provider="gemini",
                operation="omni_video",
                credits_used=Decimal(VIDEO_CREDIT_COST),
                task_id=attempt_id,
                user_id=user.id,
                status="success",
                metadata_={
                    "project_id": str(req.project_id),
                    "duration_seconds": req.duration_seconds,
                    "model": settings.omni_video_model,
                    "control_mode": req.control_mode,
                    "interaction_id": result.interaction_id,
                    "estimated_provider_cost_usd": estimated_cost,
                },
            )
        )
        await db.commit()
    except Exception as exc:
        message = str(exc).replace(settings.gemini_api_key, "[redacted]")[:700]
        logger.exception("Gemini Omni pilot attempt %s failed", attempt_id)
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="failed",
            completed_at=_now(),
            error=message,
        )
        db.add(
            ApiUsageLog(
                provider="gemini",
                operation="omni_video",
                credits_used=Decimal(VIDEO_CREDIT_COST),
                task_id=attempt_id,
                user_id=user.id,
                status="failed",
                metadata_={
                    "project_id": str(req.project_id),
                    "model": settings.omni_video_model,
                    "control_mode": req.control_mode,
                    "estimated_provider_cost_usd": estimated_cost,
                },
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Omni submission failed and still counts toward the forty-six-run cap: {message}",
        ) from exc

    project = await db.get(Project, req.project_id)
    latest_attempts = list((project.metadata_ or {}).get("video_pilot_attempts", [])) if project else []
    used = _count_provider_calls(latest_attempts)
    return VideoGenerateResponse(
        attempt=_public_attempt(entry),
        attempts_used=used,
        attempts_remaining=max(0, PILOT_MAX_PROVIDER_CALLS - used),
        provider_call_counted=True,
    )
