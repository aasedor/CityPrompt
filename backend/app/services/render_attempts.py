"""Bounded, at-most-once dispatch with durable request/result recovery.

The database is the outbox. Duplicate Redis deliveries can claim only a queued
row. A running row is NEVER queued again, including after a worker crash.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import logging
from threading import BoundedSemaphore
import uuid

from fastapi import HTTPException
from sqlalchemy import select, text, update

from app.core.config import get_settings
from app.core.image_models import image_provider_key
from app.core.security import check_project_permission, is_admin_or_above
from app.core.render_credits import effective_render_credit_balance
from app.models.models import RenderAuditLog, User
from app.models.render_attempt import RenderAttempt
from app.schemas.direct_3d_render import Direct3DRenderRequest, Direct3DRenderResponse
from app.schemas.video_appearance import VideoAppearanceRequest
from app.services.render_attempt_storage import read_evidence, write_evidence
from app.services.render_provenance import revision_sha256
from app.services.render_trial import reserve_image_trial_slot

logger = logging.getLogger(__name__)
ACTIVE = ("queued", "running")
QUEUE_LOCK = 23_140_785_570_740
# No event-loop-bound global semaphore: API tests and workers use different
# loops. The thread gate also bounds queued image payloads and survives cancel.
_ADMISSION_PREPARATION_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="image-admission")
# Permit a classroom burst to wait for the two CPU workers, while bounding the
# total retained requests. The actual image queue keeps its independent cap.
_ADMISSION_PREPARATION_SLOTS = BoundedSemaphore(64)


def now():
    return datetime.now(timezone.utc)


def describe_attempt(attempt):
    return {
        "id": str(attempt.id),
        "project_id": str(attempt.project_id),
        "idempotency_key": attempt.idempotency_key,
        "status": attempt.status,
        "model": attempt.model,
        "style": attempt.style,
        "created_at": attempt.created_at,
        "finished_at": attempt.finished_at,
        "error": attempt.error,
    }


def _estimate_admission_tokens(req):
    if isinstance(req, VideoAppearanceRequest):
        from app.services.video_appearance import GUIDE_CREDIT_COST

        return GUIDE_CREDIT_COST
    from app.services.direct_3d_render import (
        Direct3DValidationError,
        prepare_direct_3d_capture,
        estimate_direct_3d_token_cost,
    )

    try:
        capture = prepare_direct_3d_capture(req)
    except Direct3DValidationError as exc:
        raise HTTPException(400, str(exc)) from exc
    return estimate_direct_3d_token_cost(
        capture.normalized_beauty.width,
        capture.normalized_beauty.height,
        object_id_attached=capture.normalized_object_id is not None,
        instance_id_attached=capture.normalized_instance_id is not None,
        control_bundle_version=req.control_bundle_version,
        model=req.model,
    )


async def _prepare_admission_tokens(req):
    if isinstance(req, VideoAppearanceRequest):
        return _estimate_admission_tokens(req)
    if not _ADMISSION_PREPARATION_SLOTS.acquire(blocking=False):
        raise HTTPException(429, "Image validation is busy. No credits were charged. Try again shortly.")
    try:
        future = _ADMISSION_PREPARATION_POOL.submit(_estimate_admission_tokens, req)
    except BaseException:
        _ADMISSION_PREPARATION_SLOTS.release()
        raise
    # Release when the actual thread finishes, even if its HTTP caller cancels.
    future.add_done_callback(lambda _future: _ADMISSION_PREPARATION_SLOTS.release())
    return await asyncio.shield(asyncio.wrap_future(future))


def _check_credit_admission(user, token_cost):
    """Check the fresh balance under lock without charging or persisting reset.

    The worker still reserves credits atomically immediately before dispatch.
    """
    if is_admin_or_above(user):
        return
    balance = effective_render_credit_balance(user, at=now())
    if balance < token_cost:
        raise HTTPException(
            403,
            f"Not enough tokens. This image costs {token_cost} tokens " f"but you have {balance}. Tokens reset weekly.",
        )


async def submit_attempt(db, user, req: Direct3DRenderRequest | VideoAppearanceRequest, key: str):
    settings = get_settings()
    await check_project_permission(req.project_id, user, db, required="editor")
    user_id = user.id
    payload = req.model_dump(mode="json")
    fingerprint = revision_sha256(payload)
    # Recover existing jobs without capture work or waiting for global admission.
    existing = await db.scalar(
        select(RenderAttempt).where(
            RenderAttempt.user_id == user_id,
            RenderAttempt.idempotency_key == key,
        )
    )
    if existing:
        if existing.request_sha256 != fingerprint:
            raise HTTPException(
                409, "This request key already belongs to a different image. Recover the original attempt."
            )
        await db.commit()
        return existing
    if not settings.direct_3d_jobs_enabled or not settings.direct_3d_images_enabled:
        raise HTTPException(503, "AI image generation is paused. Exact 3D images remain available.")
    if not image_provider_key(settings, req.model):
        raise HTTPException(503, "Image generation is not configured")
    # Permission/identity lookups opened a read transaction. Return its pool
    # connection before waiting for CPU preparation. Rollback expires user
    # fields, so retain only the immutable ID and refresh under admission lock.
    await db.rollback()
    # Expensive decoding/control validation runs off-loop before QUEUE_LOCK.
    token_cost = await _prepare_admission_tokens(req)
    # Admission + idempotency are one global, short transaction. A duplicate
    # may have committed while this request prepared its capture; re-read it.
    await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": QUEUE_LOCK})
    await db.refresh(user, with_for_update=True)
    await check_project_permission(req.project_id, user, db, required="editor")
    existing = await db.scalar(
        select(RenderAttempt).where(
            RenderAttempt.user_id == user_id,
            RenderAttempt.idempotency_key == key,
        )
    )
    if existing:
        if existing.request_sha256 != fingerprint:
            raise HTTPException(
                409, "This request key already belongs to a different image. Recover the original attempt."
            )
        await db.commit()
        return existing
    active = list((await db.scalars(select(RenderAttempt).where(RenderAttempt.status.in_(ACTIVE)))).all())
    own = next((item for item in active if item.user_id == user.id), None)
    if own:
        raise HTTPException(
            409,
            {
                "code": "render_attempt_active",
                "attempt_id": str(own.id),
                "message": "An image is already queued or running. Recover that attempt first.",
            },
        )
    if (
        len(active) >= settings.direct_3d_queue_limit
        or sum(item.project_id == req.project_id for item in active) >= settings.direct_3d_project_queue_limit
    ):
        raise HTTPException(429, "The image queue is full. Your credits have not been charged. Try later.")
    _check_credit_admission(user, token_cost)
    attempt = RenderAttempt(
        id=uuid.uuid4(),
        user_id=user.id,
        project_id=req.project_id,
        idempotency_key=key,
        request_sha256=fingerprint,
        status="queued",
        model=req.model,
        style=req.style,
        created_at=now(),
    )
    await reserve_image_trial_slot(db, req.project_id, user.id, key, fingerprint)
    await write_evidence(attempt, "request", payload)
    db.add(attempt)
    await db.commit()
    # Broker outages do not lose the request or make the client submit anew.
    # Beat re-delivers committed queued rows after connectivity returns.
    await deliver_attempt(attempt.id)
    return attempt


async def deliver_attempt(attempt_id):
    import asyncio
    from app.tasks.direct_3d import render_direct_3d_attempt

    try:
        await asyncio.to_thread(
            render_direct_3d_attempt.apply_async, args=[str(attempt_id)], queue="direct3d", retry=False
        )
    except Exception:
        logger.warning("Image %s is saved; broker delivery will be retried by maintenance", attempt_id)


async def authorized_attempt(db, user, attempt_id):
    attempt = await db.get(RenderAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(404, "Image attempt not found")
    await check_project_permission(attempt.project_id, user, db, required="viewer")
    return attempt


def response_from_evidence(evidence):
    result = evidence["result"]
    return Direct3DRenderResponse(
        image_base64=result["image_base64"],
        model=evidence["model"],
        provider_image_base64=result.get("provider_image_base64"),
        outcome=result["outcome"],
        warnings=result["warnings"],
        capture_fingerprint=result["capture_fingerprint"],
        output_fingerprint=result["output_fingerprint"],
        diagnostics=result["diagnostics"],
    )


async def recover_result(attempt):
    stored = await read_evidence(attempt, "response")
    if stored:
        if stored.get("purpose") == "video_appearance":
            return stored
        return Direct3DRenderResponse.model_validate(stored)
    raw = await read_evidence(attempt, "provider-result")
    if raw:
        if raw.get("purpose") == "video_appearance":
            return raw
        return response_from_evidence(raw)
    return None


async def execute_attempt(db, attempt_id):
    from app.api.v1.direct_3d_render import run_direct_3d_render

    # Atomic one-way claim: even 60 duplicate deliveries dispatch at most once.
    attempt = (
        await db.execute(
            update(RenderAttempt)
            .where(
                RenderAttempt.id == attempt_id,
                RenderAttempt.status == "queued",
            )
            .values(status="running", started_at=now())
            .returning(RenderAttempt)
        )
    ).scalar_one_or_none()
    await db.commit()
    if attempt is None:
        return
    try:
        if (now() - attempt.created_at).total_seconds() > get_settings().direct_3d_queue_timeout_seconds:
            raise HTTPException(408, "The queue expired before generation. No credits were charged.")
        user = await db.get(User, attempt.user_id)
        if user is None or not user.is_active:
            raise HTTPException(403, "This account is no longer active. No image was generated.")
        payload = await read_evidence(attempt, "request")
        if payload is None or revision_sha256(payload) != attempt.request_sha256:
            raise HTTPException(409, "The saved image request could not be verified. No image was generated.")
        if payload.get("purpose") == "video_appearance":
            from app.services.video_appearance import run_appearance_render

            req = VideoAppearanceRequest.model_validate(payload)
            response = await run_appearance_render(req, user, db, attempt=attempt)
            await write_evidence(attempt, "response", response)
        else:
            req = Direct3DRenderRequest.model_validate(payload)
            response = await run_direct_3d_render(req, user, db, attempt=attempt)
            await write_evidence(attempt, "response", response.model_dump(mode="json"))
        await db.refresh(attempt, with_for_update=True)
        attempt.status, attempt.error, attempt.finished_at = "completed", None, now()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        logger.exception("Image attempt %s stopped; no provider retry", attempt_id)
        # A saved paid result wins over a gallery/response/connection failure.
        # Storage outages leave running state for maintenance to inspect later.
        try:
            await reconcile_attempt(db, attempt_id, error=exc)
        except Exception:
            await db.rollback()
            logger.exception("Image attempt %s awaits durable recovery", attempt_id)


async def reconcile_attempt(db, attempt_id, *, error=None):
    from app.api.v1.direct_3d_render import _refund_unknown_direct_render, _refund_unproduced_direct_render

    attempt = await db.scalar(select(RenderAttempt).where(RenderAttempt.id == attempt_id).with_for_update())
    if not attempt or attempt.status != "running":
        await db.commit()
        return
    result = await recover_result(attempt)
    if result:
        attempt.status, attempt.error, attempt.finished_at = "completed", None, now()
        await db.commit()
        return
    detail = error.detail if isinstance(error, HTTPException) else None
    reservation = await db.get(RenderAuditLog, attempt.audit_id) if attempt.audit_id else None
    if reservation and reservation.student_refunded_at is None:
        provider_error = await read_evidence(attempt, "provider-error")
        if provider_error and provider_error.get("billing_status") == "produced":
            detail = {
                "code": "direct_3d_billed_safety_rejection",
                "billed": True,
                "message": "An image was produced but rejected by safety checks. The attempt was charged; it will not retry.",
            }
        else:
            # A reservation means dispatch MAY have happened. Unknown costs
            # stay in the global cap. The refund and terminal transition commit
            # together below (the helper commits; reacquire the attempt lock).
            user = await db.get(User, attempt.user_id)
            refund = (
                _refund_unproduced_direct_render
                if provider_error and provider_error.get("billing_status") == "unproduced"
                else _refund_unknown_direct_render
            )
            await refund(
                db,
                user,
                reservation,
                token_cost=reservation.tokens_spent,
                detail="Worker stopped without a retained result",
            )
            await db.refresh(attempt, with_for_update=True)
            if attempt.status != "running":
                await db.commit()
                return
    refunded = reservation is not None and reservation.student_refunded_at is not None
    unknown = refunded and reservation.tokens_spent > 0
    attempt.status = "unknown" if unknown else "failed"
    attempt.error = (
        detail
        if isinstance(detail, dict)
        else {
            "code": "direct_3d_worker_stopped",
            "billed": bool(reservation and not refunded),
            "message": (
                str(detail)
                if detail
                else (
                    "The image did not finish. Your credits were restored; provider billing is uncertain. This attempt will not retry."
                    if unknown
                    else "The image did not finish. No credits were charged. This attempt will not retry."
                )
            ),
        }
    )
    attempt.finished_at = now()
    await db.commit()


async def maintain_attempts(db):
    settings = get_settings()
    if not settings.direct_3d_jobs_enabled:
        return
    await db.execute(
        update(RenderAttempt)
        .where(
            RenderAttempt.status == "queued",
            RenderAttempt.created_at < now() - timedelta(seconds=settings.direct_3d_queue_timeout_seconds),
        )
        .values(
            status="failed",
            finished_at=now(),
            error={
                "code": "render_queue_expired",
                "billed": False,
                "message": "The image queue expired before generation. No credits were charged.",
            },
        )
    )
    await db.commit()
    cutoff = now() - timedelta(seconds=settings.direct_3d_recovery_seconds)
    stale = list(
        (
            await db.scalars(
                select(RenderAttempt.id)
                .where(
                    RenderAttempt.status == "running",
                    RenderAttempt.started_at < cutoff,
                )
                .limit(64)
            )
        ).all()
    )
    await db.commit()
    for attempt_id in stale:
        try:
            await reconcile_attempt(db, attempt_id)
        except Exception:
            await db.rollback()
            logger.exception("Recovery pending for image %s", attempt_id)
    queued = list((await db.scalars(select(RenderAttempt.id).where(RenderAttempt.status == "queued").limit(64))).all())
    await db.commit()
    for attempt_id in queued:
        await deliver_attempt(attempt_id)
