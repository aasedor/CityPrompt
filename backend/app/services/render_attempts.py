"""Bounded, at-most-once dispatch with durable request/result recovery.

The database is the outbox. Duplicate Redis deliveries can claim only a queued
row. A running row is NEVER queued again, including after a worker crash.
"""

from datetime import datetime, timedelta, timezone
import logging
import uuid

from fastapi import HTTPException
from sqlalchemy import select, text, update

from app.core.config import get_settings
from app.core.security import check_project_permission
from app.models.models import RenderAuditLog, User
from app.models.render_attempt import RenderAttempt
from app.schemas.direct_3d_render import Direct3DRenderRequest, Direct3DRenderResponse
from app.services.render_attempt_storage import read_evidence, write_evidence
from app.services.render_provenance import revision_sha256
from app.services.render_trial import reserve_image_trial_slot

logger = logging.getLogger(__name__)
ACTIVE = ("queued", "running")
QUEUE_LOCK = 23_140_785_570_740


def now():
    return datetime.now(timezone.utc)


def describe_attempt(attempt):
    return {
        "id": str(attempt.id), "project_id": str(attempt.project_id),
        "idempotency_key": attempt.idempotency_key,
        "status": attempt.status, "model": attempt.model, "style": attempt.style,
        "created_at": attempt.created_at, "finished_at": attempt.finished_at,
        "error": attempt.error,
    }


async def submit_attempt(db, user, req: Direct3DRenderRequest, key: str):
    settings = get_settings()
    await check_project_permission(req.project_id, user, db, required="editor")
    payload = req.model_dump(mode="json")
    fingerprint = revision_sha256(payload)
    # Admission + idempotency are one global, short transaction. Only 16 active
    # jobs are allowed; image bodies live in private object storage, not rows.
    await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": QUEUE_LOCK})
    existing = await db.scalar(select(RenderAttempt).where(
        RenderAttempt.user_id == user.id, RenderAttempt.idempotency_key == key,
    ))
    if existing:
        if existing.request_sha256 != fingerprint:
            raise HTTPException(409, "This request key already belongs to a different image. Recover the original attempt.")
        await db.commit()
        return existing
    if not settings.direct_3d_jobs_enabled or not settings.direct_3d_images_enabled:
        raise HTTPException(503, "AI image generation is paused. Exact 3D images remain available.")
    if not settings.openai_api_key:
        raise HTTPException(503, "Image generation is not configured")
    active = list((await db.scalars(select(RenderAttempt).where(RenderAttempt.status.in_(ACTIVE)))).all())
    own = next((item for item in active if item.user_id == user.id), None)
    if own:
        raise HTTPException(409, {"code": "render_attempt_active", "attempt_id": str(own.id),
                                 "message": "An image is already queued or running. Recover that attempt first."})
    if len(active) >= settings.direct_3d_queue_limit or sum(item.project_id == req.project_id for item in active) >= settings.direct_3d_project_queue_limit:
        raise HTTPException(429, "The image queue is full. Your credits have not been charged. Try later.")
    attempt = RenderAttempt(
        id=uuid.uuid4(), user_id=user.id, project_id=req.project_id,
        idempotency_key=key, request_sha256=fingerprint, status="queued",
        model=req.model, style=req.style, created_at=now(),
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
        await asyncio.to_thread(render_direct_3d_attempt.apply_async, args=[str(attempt_id)], queue="direct3d", retry=False)
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
        image_base64=result["image_base64"], model=evidence["model"],
        outcome=result["outcome"], warnings=result["warnings"],
        capture_fingerprint=result["capture_fingerprint"], output_fingerprint=result["output_fingerprint"],
        diagnostics=result["diagnostics"],
    )


async def recover_result(attempt):
    stored = await read_evidence(attempt, "response")
    if stored:
        return Direct3DRenderResponse.model_validate(stored)
    raw = await read_evidence(attempt, "provider-result")
    if raw:
        return response_from_evidence(raw)
    return None


async def execute_attempt(db, attempt_id):
    from app.api.v1.direct_3d_render import run_direct_3d_render
    # Atomic one-way claim: even 60 duplicate deliveries dispatch at most once.
    attempt = (await db.execute(update(RenderAttempt).where(
        RenderAttempt.id == attempt_id, RenderAttempt.status == "queued",
    ).values(status="running", started_at=now()).returning(RenderAttempt))).scalar_one_or_none()
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
            detail = {"code": "direct_3d_billed_safety_rejection", "billed": True,
                      "message": "An image was produced but rejected by safety checks. The attempt was charged; it will not retry."}
        else:
            # A reservation means dispatch MAY have happened. Unknown costs
            # stay in the global cap. The refund and terminal transition commit
            # together below (the helper commits; reacquire the attempt lock).
            user = await db.get(User, attempt.user_id)
            refund = _refund_unproduced_direct_render if provider_error and provider_error.get("billing_status") == "unproduced" else _refund_unknown_direct_render
            await refund(db, user, reservation,
                token_cost=reservation.tokens_spent, detail="Worker stopped without a retained result")
            await db.refresh(attempt, with_for_update=True)
            if attempt.status != "running":
                await db.commit()
                return
    refunded = reservation is not None and reservation.student_refunded_at is not None
    unknown = refunded and reservation.tokens_spent > 0
    attempt.status = "unknown" if unknown else "failed"
    attempt.error = detail if isinstance(detail, dict) else {
        "code": "direct_3d_worker_stopped", "billed": bool(reservation and not refunded),
        "message": str(detail) if detail else (
            "The image did not finish. Your credits were restored; provider billing is uncertain. This attempt will not retry."
            if unknown else "The image did not finish. No credits were charged. This attempt will not retry."),
    }
    attempt.finished_at = now()
    await db.commit()


async def maintain_attempts(db):
    settings = get_settings()
    if not settings.direct_3d_jobs_enabled:
        return
    await db.execute(update(RenderAttempt).where(
        RenderAttempt.status == "queued",
        RenderAttempt.created_at < now() - timedelta(seconds=settings.direct_3d_queue_timeout_seconds),
    ).values(status="failed", finished_at=now(), error={
        "code": "render_queue_expired", "billed": False,
        "message": "The image queue expired before generation. No credits were charged.",
    }))
    await db.commit()
    cutoff = now() - timedelta(seconds=settings.direct_3d_recovery_seconds)
    stale = list((await db.scalars(select(RenderAttempt.id).where(
        RenderAttempt.status == "running", RenderAttempt.started_at < cutoff,
    ).limit(64))).all())
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
