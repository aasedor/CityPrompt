"""Optional saved-still animation, isolated from the eight-second route API."""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import uuid
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Literal
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, require_auth, is_admin_or_above
from app.models.models import ApiUsageLog, User
from app.services.render_provenance import revision_sha256
from app.services.render_trial import check_trial_available, reserve_trial_slot
from app.services.kling_video import (
    ANIMATION_SECONDS,
    ANIMATION_PROMPT,
    ANIMATION_NEGATIVE_PROMPT,
    ANIMATION_SETTINGS,
    KlingGenerationFailed,
    build_kling_arguments,
    estimate_kling_cost,
    validate_endpoint,
    validate_source_image,
    upload_kling_source,
    submit_kling_once,
    poll_kling_request,
    download_kling_video,
)
from app.api.v1.video import (
    VideoAttemptResponse,
    _locked_project,
    _update_attempt,
    _public_attempt,
    _visible_usage,
    _now,
    PILOT_MAX_PROVIDER_CALLS,
)

router = APIRouter()
POLL_LEASE_SECONDS = 240


class RenderAnimationPreflightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: uuid.UUID
    source_render_id: uuid.UUID


class RenderAnimationRequest(RenderAnimationPreflightRequest):
    request_id: uuid.UUID
    confirm_paid_submission: Literal[True]


class RenderAnimationPreflightResponse(BaseModel):
    ready: Literal[True] = True
    provider_called: Literal[False] = False
    source_render_id: str
    width: int
    height: int
    duration_seconds: Literal[5] = 5
    generate_audio: Literal[False] = False
    estimated_cost_usd: float
    credit_cost: int
    model: str
    attempts_remaining: int


def _configured(settings):
    if not settings.kling_animation_enabled:
        raise HTTPException(
            503, "Saved-render animation is not enabled on this server."
        )
    if not settings.fal_key:
        raise HTTPException(503, "FAL_KEY is not configured on the server.")
    try:
        validate_endpoint(settings.kling_animation_endpoint)
    except ValueError as exc:
        raise HTTPException(503, str(exc)) from exc


def _source_render(project, render_id: uuid.UUID, *, require_finished: bool = True) -> tuple[dict, str]:
    render = next(
        (
            item
            for item in (project.metadata_ or {}).get("saved_renders", [])
            if item.get("id") == str(render_id)
        ),
        None,
    )
    if not render:
        raise HTTPException(404, "Finished render not found in this project.")
    strategy = (
        render.get("presentation_strategy")
        or str(render.get("outcome") or "").partition("·")[2].strip()
    )
    if (
        require_finished
        and render.get("variant") != "provider_original"
        and (strategy == "authoritative_source" or render.get("model") == "3d-capture")
    ):
        raise HTTPException(
            400,
            "This gallery item is the 3D source. Select the finished AI render to animate.",
        )
    url = urlsplit(render.get("image_url") or "")
    prefix = f"/api/v1/files/projects/{project.id}/renders/{render_id}."
    if (
        url.query
        or url.fragment
        or not url.path.startswith(prefix)
        or url.path[len(prefix) :] not in {"png", "jpg", "jpeg", "webp"}
    ):
        raise HTTPException(
            400, "The full-resolution finished render is not stored in this project."
        )
    return render, url.path.removeprefix("/api/v1/files/")


def _read_source(key: str) -> bytes:
    from app.api.v1.files import _s3_client

    settings = get_settings()
    return (
        _s3_client().get_object(Bucket=settings.s3_bucket_name, Key=key)["Body"].read()
    )


async def _load_source(key):
    try:
        data = await asyncio.to_thread(_read_source, key)
        return await asyncio.to_thread(validate_source_image, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            503,
            "Could not read the saved full-resolution render. No generation was submitted.",
        ) from exc


def _check_budget(project, user, settings):
    check_trial_available(project, user.id, "video")
    attempts = (project.metadata_ or {}).get("video_pilot_attempts", [])
    # Include pending reservations so simultaneous distinct submissions cannot
    # overrun the same bounded per-project allowance used by route videos.
    reserved = sum(item.get("provider") == "kling" for item in attempts)
    if reserved >= PILOT_MAX_PROVIDER_CALLS:
        raise HTTPException(
            409, "This project has reached its saved-render animation allowance."
        )
    if (
        not is_admin_or_above(user)
        and user.render_credits < settings.kling_animation_credit_cost
    ):
        raise HTTPException(
            402, f"Animation requires {settings.kling_animation_credit_cost} credits."
        )
    return _visible_usage(project, attempts, "kling")


def _safe_error(exc, key):
    return str(exc).replace(key, "[redacted]")[:500] if key else str(exc)[:500]


@router.post("/animate/preflight", response_model=RenderAnimationPreflightResponse)
async def preflight_animation(
    req: RenderAnimationPreflightRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    _configured(settings)
    project = await _locked_project(db, req.project_id)
    _, key = _source_render(project, req.source_render_id)
    usage = _check_budget(project, user, settings)
    await db.commit()  # Release the row lock before object storage I/O.
    source = await _load_source(key)
    return RenderAnimationPreflightResponse(
        source_render_id=str(req.source_render_id),
        width=source.width,
        height=source.height,
        estimated_cost_usd=estimate_kling_cost(
            settings.kling_animation_cost_per_second_usd
        ),
        credit_cost=(
            0 if is_admin_or_above(user) else settings.kling_animation_credit_cost
        ),
        model=settings.kling_animation_endpoint,
        attempts_remaining=usage.attempts_remaining,
    )


@router.post("/animate", response_model=VideoAttemptResponse, status_code=202)
async def animate_render(
    req: RenderAnimationRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await check_project_permission(req.project_id, user, db, required="editor")
    project = await _locked_project(db, req.project_id)
    fingerprint = revision_sha256(req.model_dump(mode="json"))
    attempts = [
        dict(item) for item in (project.metadata_ or {}).get("video_pilot_attempts", [])
    ]
    existing = next(
        (item for item in attempts if item.get("request_id") == str(req.request_id)),
        None,
    )
    if existing:
        if existing.get("request_sha256") != fingerprint or existing.get(
            "requested_by"
        ) != str(user.id):
            raise HTTPException(
                409, "This request ID already belongs to another video request."
            )
        await db.commit()
        return _public_attempt(
            existing
        )  # Never submit again, including an unknown outcome.

    settings = get_settings()
    _configured(settings)
    render, source_key = _source_render(project, req.source_render_id)
    _check_budget(project, user, settings)
    attempt_id = str(uuid.uuid4())
    entry = {
        "id": attempt_id,
        "request_id": str(req.request_id),
        "request_sha256": fingerprint,
        "requested_by": str(user.id),
        "project_id": str(req.project_id),
        "provider": "kling",
        "mode": "saved_render_animation",
        "source_render_id": str(req.source_render_id),
        "source_image_url": render["image_url"],
        "guide_image_url": render["image_url"],
        "model": settings.kling_animation_endpoint,
        "prompt": ANIMATION_PROMPT,
        "negative_prompt": ANIMATION_NEGATIVE_PROMPT,
        "generation_settings": dict(ANIMATION_SETTINGS),
        "status": "reserved",
        "style": "architectural_film",
        "camera_motion": "slow_push_in",
        "duration_seconds": ANIMATION_SECONDS,
        "created_at": _now(),
        "estimated_cost_usd": estimate_kling_cost(
            settings.kling_animation_cost_per_second_usd
        ),
        "credit_cost": settings.kling_animation_credit_cost,
        "source_storage_key": source_key,
    }
    reserve_trial_slot(project, user.id, "video", str(req.request_id), fingerprint)
    meta = dict(project.metadata_ or {})
    meta["video_pilot_attempts"] = [*attempts, entry]
    project.metadata_ = meta
    await db.commit()

    # Upload only these stored bytes; there is no image URL/base64 input in this API.
    try:
        source = await _load_source(source_key)
        start_image_url = await upload_kling_source(settings.fal_key, source)
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            source_sha256=hashlib.sha256(source.data).hexdigest(),
            source_width=source.width,
            source_height=source.height,
            provider_source_url=start_image_url,
        )
    except Exception:
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="preflight_failed",
            error="Could not prepare the finished render; no paid generation was submitted.",
            completed_at=_now(),
        )
        return _public_attempt(entry)

    # Credit debit and submission marker share the row-lock transaction. A lost
    # receipt is an unknown outcome, never permission to retry the paid POST.
    project = await _locked_project(db, req.project_id)
    if not is_admin_or_above(user):
        remaining = (
            await db.execute(
                update(User)
                .where(
                    User.id == user.id,
                    User.render_credits >= entry["credit_cost"],
                )
                .values(render_credits=User.render_credits - entry["credit_cost"])
                .returning(User.render_credits)
            )
        ).scalar_one_or_none()
        if remaining is None:
            await db.rollback()
            entry = await _update_attempt(
                db,
                req.project_id,
                attempt_id,
                status="preflight_failed",
                error="Insufficient animation credits. No paid generation was submitted.",
            )
            return _public_attempt(entry)
    usage_log = ApiUsageLog(
        provider="fal",
        operation="kling_render_animation",
        task_id=attempt_id,
        user_id=user.id,
        credits_used=Decimal(0 if is_admin_or_above(user) else entry["credit_cost"]),
        status="submitting",
        metadata_={
            "project_id": str(req.project_id),
            "source_render_id": str(req.source_render_id),
            "model": entry["model"],
            "estimated_provider_cost_usd": entry["estimated_cost_usd"],
            "generation_settings": entry["generation_settings"],
        },
    )
    db.add(usage_log)
    entry = await _update_attempt(
        db,
        req.project_id,
        attempt_id,
        status="submitting",
        provider_call_started_at=_now(),
    )
    usage_log_id = usage_log.id
    request_id = None
    try:
        request_id = await submit_kling_once(
            settings.fal_key, entry["model"], build_kling_arguments(start_image_url)
        )
        # FIRST operation after the receipt: durable provider identity, before polling.
        entry = await _update_attempt(
            db, req.project_id, attempt_id, status="queued", interaction_id=request_id
        )
    except Exception as exc:
        await db.rollback()
        entry = await _update_attempt(
            db,
            req.project_id,
            attempt_id,
            status="queued" if request_id else "submission_unknown",
            interaction_id=request_id,
            error=(
                "Receipt recovery needed. "
                if request_id
                else "Submission outcome is unknown. "
            )
            + _safe_error(exc, settings.fal_key)
            + " No new generation will be submitted automatically.",
        )
    # The charge/log already survived before submission. Recovery never logs or
    # debits a second time, even if the server stops before this receipt update.
    usage_log = await db.get(ApiUsageLog, usage_log_id, populate_existing=True)
    usage_log.status = "submitted" if request_id else "unknown"
    usage_log.metadata_ = {**usage_log.metadata_, "interaction_id": request_id}
    await db.commit()
    return _public_attempt(entry)


async def _recovery_update(
    db, project_id, attempt_id, lease_id, *, release=False, **changes
):
    project = await _locked_project(db, project_id)
    meta = dict(project.metadata_ or {})
    attempts = [dict(item) for item in meta.get("video_pilot_attempts", [])]
    for index, entry in enumerate(attempts):
        if entry.get("id") != str(attempt_id):
            continue
        # A restarted worker may have acquired an expired lease. A stale poll
        # must not clear that lease or overwrite its completed result.
        if entry.get("poll_lease_id") == lease_id and not entry.get("video_url"):
            entry.update(changes)
            if changes.get("status") in {"complete", "failed"}:
                await db.execute(
                    update(ApiUsageLog)
                    .where(
                        ApiUsageLog.task_id == str(attempt_id),
                        ApiUsageLog.operation == "kling_render_animation",
                    )
                    .values(
                        status=(
                            "success" if changes["status"] == "complete" else "failed"
                        )
                    )
                )
            if release:
                entry.update(poll_lease_id=None, poll_lease_until=None)
            attempts[index] = entry
            meta["video_pilot_attempts"] = attempts
            project.metadata_ = meta
        await db.commit()
        return entry
    raise HTTPException(404, "Saved-render animation not found.")


@router.post(
    "/projects/{project_id}/animations/{attempt_id}/recover",
    response_model=VideoAttemptResponse,
)
async def recover_animation(
    project_id: uuid.UUID,
    attempt_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Read the original fal request and retain its output. NEVER submits a job."""
    await check_project_permission(project_id, user, db, required="editor")
    project = await _locked_project(db, project_id)
    entry = next(
        (
            dict(item)
            for item in (project.metadata_ or {}).get("video_pilot_attempts", [])
            if item.get("id") == str(attempt_id)
            and item.get("mode") == "saved_render_animation"
        ),
        None,
    )
    if not entry:
        raise HTTPException(404, "Saved-render animation not found.")
    if entry.get("requested_by") != str(user.id):
        raise HTTPException(403, "Only the requester can recover this animation job.")
    if (
        entry.get("video_url")
        or entry.get("status") == "failed"
        or not entry.get("interaction_id")
    ):
        await db.commit()
        return _public_attempt(entry)
    settings = get_settings()
    # Recovery stays available if optional new submissions have been disabled.
    if not settings.fal_key:
        raise HTTPException(503, "FAL_KEY is required to recover the saved request.")
    lease = entry.get("poll_lease_until")
    if lease and datetime.fromisoformat(lease) > datetime.now(timezone.utc):
        await db.commit()
        return _public_attempt(entry)
    lease_id = str(uuid.uuid4())
    entry = await _update_attempt(
        db,
        project_id,
        str(attempt_id),
        poll_lease_id=lease_id,
        poll_lease_until=(
            datetime.now(timezone.utc) + timedelta(seconds=POLL_LEASE_SECONDS)
        ).isoformat(),
    )
    changes = {}
    try:
        status, url = await poll_kling_request(
            settings.fal_key, entry["model"], entry["interaction_id"]
        )
        changes = {"status": status, "error": None}
        if url:
            # Keep the completed remote address before download/storage can fail.
            entry = await _recovery_update(
                db,
                project_id,
                attempt_id,
                lease_id,
                provider_video_url=url,
                status="saving",
            )
            if entry.get("poll_lease_id") != lease_id or entry.get("video_url"):
                return _public_attempt(entry)
            video_bytes = await download_kling_video(url)
            from app.api.v1.documents import _upload_to_storage

            key = f"projects/{project_id}/video-render/{attempt_id}/kling-animation.mp4"
            await _upload_to_storage(key, video_bytes, "video/mp4")
            changes.update(
                status="complete",
                video_url=f"/api/v1/files/{key}",
                completed_at=_now(),
                size_bytes=len(video_bytes),
            )
    except KlingGenerationFailed as exc:
        changes = {
            "status": "failed",
            "error": _safe_error(exc, settings.fal_key),
            "completed_at": _now(),
        }
    except Exception as exc:
        await db.rollback()
        changes = {
            "error": "Recovery paused: "
            + _safe_error(exc, settings.fal_key)
            + " Try checking this saved request again; no new generation will be submitted."
        }
    entry = await _recovery_update(
        db, project_id, attempt_id, lease_id, release=True, **changes
    )
    return _public_attempt(entry)
