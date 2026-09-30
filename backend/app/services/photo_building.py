"""Bounded, private photo inputs for the student custom-building pilot.

This workflow produces an AI mesh preview. It does not grant an RLASM keeper
status or add a model to the classroom catalogue.
"""

import hashlib
import io
import uuid
from datetime import datetime, timezone
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PHOTOS = 4
MIN_REFERENCE_VIEWS = 2
MAX_REFERENCE_VIEWS = 4
MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_EDGE = 2048
PHOTO_WORKFLOW_VERSION = 1
PHOTO_REFERENCE_TOKEN_COST = 50
PHOTO_MODEL_TOKEN_COST = 150


async def reserve_photo_tokens(db, user, project_id, *, cost: int, stage: str, brief: str) -> uuid.UUID:
    """Reserve a student's displayed City Prompt tokens before a paid stage."""
    from fastapi import HTTPException

    from app.core.security import is_admin_or_above
    from app.models.models import RenderAuditLog

    charge = 0 if is_admin_or_above(user) else cost
    if charge:
        await db.refresh(user, with_for_update=True)
        now = datetime.now(timezone.utc)
        if user.credits_reset_at is None or (now - user.credits_reset_at).days >= 7:
            user.render_credits = 1000
            user.credits_reset_at = now
        if user.render_credits < charge:
            raise HTTPException(
                status_code=403,
                detail=f"This step costs {charge} tokens; you have {user.render_credits}.",
            )
        user.render_credits -= charge
        db.add(user)
    audit = RenderAuditLog(
        id=uuid.uuid4(), user_id=user.id, user_email=user.email,
        project_id=project_id, model=f"meshy-photo-{stage}", tokens_spent=charge,
        prompt_preview=f"[Custom building {stage}] {brief[:400]}",
    )
    db.add(audit)
    await db.flush()
    return audit.id


async def refund_photo_tokens(db, audit_id: str | None) -> None:
    """Idempotently refund an unqueued or failed paid stage."""
    if not audit_id:
        return
    from app.models.models import RenderAuditLog, User

    audit = await db.get(RenderAuditLog, uuid.UUID(audit_id), with_for_update=True)
    if audit is None or audit.student_refunded_at is not None:
        return
    if audit.tokens_spent:
        user = await db.get(User, audit.user_id, with_for_update=True)
        if user is not None:
            user.render_credits += audit.tokens_spent
            db.add(user)
    audit.student_refunded_at = datetime.now(timezone.utc)
    audit.tokens_spent = 0
    audit.prompt_preview = "[Custom building refunded] Provider did not return a usable result"
    db.add(audit)
    await db.commit()


def refund_photo_tokens_sync(session, audit_id: str | None) -> None:
    """Worker-side equivalent, guarded by a row lock against double refunds."""
    if not audit_id:
        return
    from app.models.models import RenderAuditLog, User

    audit = session.query(RenderAuditLog).filter_by(id=uuid.UUID(audit_id)).with_for_update().first()
    if audit is None or audit.student_refunded_at is not None:
        return
    if audit.tokens_spent:
        user = session.query(User).filter_by(id=audit.user_id).with_for_update().first()
        if user is not None:
            user.render_credits += audit.tokens_spent
    audit.student_refunded_at = datetime.now(timezone.utc)
    audit.tokens_spent = 0
    audit.prompt_preview = "[Custom building refunded] Provider did not return a usable result"
    session.commit()


def prepare_photo(data: bytes, *, max_bytes: int = MAX_SOURCE_BYTES) -> tuple[bytes, str]:
    """Validate a source photo and make a bounded, oriented JPEG for storage."""
    if not data or len(data) > max_bytes:
        raise ValueError("The photo is empty or exceeds its size limit.")
    try:
        with Image.open(io.BytesIO(data)) as original:
            if original.format not in {"JPEG", "PNG"}:
                raise ValueError("Use JPG or PNG photos.")
            if original.width * original.height > 40_000_000:
                raise ValueError("The photo dimensions are too large.")
            oriented = ImageOps.exif_transpose(original)
            if oriented.mode == "RGBA":
                background = Image.new("RGB", oriented.size, "white")
                background.paste(oriented, mask=oriented.getchannel("A"))
                oriented = background
            else:
                oriented = oriented.convert("RGB")
            oriented.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            oriented.save(output, format="JPEG", quality=90, optimize=True)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The uploaded file is not a readable JPG or PNG photo.") from exc
    prepared = output.getvalue()
    return prepared, hashlib.sha256(prepared).hexdigest()


def reference_prompt(brief: str) -> str:
    """Ask for consistent architectural reference views, not presentation art."""
    description = brief.strip()[:500]
    return (
        "Create three mutually consistent views of the SAME building shown in the "
        "uploaded photos: front, rear, and side three-quarter. Preserve the roof "
        "form, storey count, facade rhythm, doors, windows, materials, and colors. "
        "Show the whole building at human scale on a neutral plain background. "
        "Remove people, cars, neighbouring buildings, signs, text, and logos. "
        "Do not invent extra wings or floors. "
        + (f"Student notes: {description}" if description else "")
    )


def photo_state(specifications: dict[str, Any] | None) -> dict[str, Any]:
    state = (specifications or {}).get("photo_generation")
    return state if isinstance(state, dict) and state.get("version") == PHOTO_WORKFLOW_VERSION else {}
