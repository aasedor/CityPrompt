"""
Beta feedback endpoints — any authenticated user can submit,
admin+ can view the inbox and manage status.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_auth, require_admin
from app.models.models import BetaFeedback, User

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    category: str = Field(default="suggestion", pattern="^(suggestion|bug|question)$")
    text: str = Field(..., min_length=1, max_length=5000)
    page_url: str | None = None


class FeedbackUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(open|reviewed|resolved|dismissed)$")
    admin_notes: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    author_id: str
    author_email: str | None = None
    author_name: str | None = None
    category: str
    text: str
    page_url: str | None
    status: str
    admin_notes: str | None
    created_at: str


# ---------------------------------------------------------------------------
# User endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    body: FeedbackCreate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Submit a feedback item (any authenticated user)."""
    fb = BetaFeedback(
        author_id=user.id,
        category=body.category,
        text=body.text,
        page_url=body.page_url,
    )
    db.add(fb)
    await db.flush()
    await db.refresh(fb)
    return _to_response(fb, user.email, user.full_name)


@router.get("/mine", response_model=list[FeedbackResponse])
async def list_my_feedback(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List feedback submitted by the current user."""
    result = await db.execute(
        select(BetaFeedback)
        .where(BetaFeedback.author_id == user.id)
        .order_by(BetaFeedback.created_at.desc())
    )
    return [_to_response(fb, user.email, user.full_name) for fb in result.scalars().all()]


# ---------------------------------------------------------------------------
# Admin inbox endpoints
# ---------------------------------------------------------------------------

@router.get("/inbox", response_model=list[FeedbackResponse])
async def list_feedback_inbox(
    status_filter: str | None = None,
    category: str | None = None,
    limit: int = 100,
    skip: int = 0,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin inbox — list all feedback with optional filters."""
    query = (
        select(BetaFeedback, User.email, User.full_name)
        .join(User, BetaFeedback.author_id == User.id)
        .order_by(BetaFeedback.created_at.desc())
    )
    if status_filter:
        query = query.where(BetaFeedback.status == status_filter)
    if category:
        query = query.where(BetaFeedback.category == category)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return [_to_response(fb, email, name) for fb, email, name in result.all()]


@router.get("/inbox/counts")
async def feedback_counts(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get counts by status for badge display."""
    result = await db.execute(
        select(BetaFeedback.status, func.count(BetaFeedback.id))
        .group_by(BetaFeedback.status)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return {
        "open": counts.get("open", 0),
        "reviewed": counts.get("reviewed", 0),
        "resolved": counts.get("resolved", 0),
        "dismissed": counts.get("dismissed", 0),
        "total": sum(counts.values()),
    }


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: uuid.UUID,
    body: FeedbackUpdate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: update feedback status or add notes."""
    result = await db.execute(
        select(BetaFeedback, User.email, User.full_name)
        .join(User, BetaFeedback.author_id == User.id)
        .where(BetaFeedback.id == feedback_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Feedback not found")

    fb, email, name = row
    if body.status is not None:
        fb.status = body.status
    if body.admin_notes is not None:
        fb.admin_notes = body.admin_notes
    await db.flush()
    await db.refresh(fb)
    return _to_response(fb, email, name)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: uuid.UUID,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: permanently delete a feedback item."""
    result = await db.execute(
        select(BetaFeedback).where(BetaFeedback.id == feedback_id)
    )
    fb = result.scalar_one_or_none()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    await db.delete(fb)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_response(fb: BetaFeedback, email: str | None = None, name: str | None = None) -> FeedbackResponse:
    return FeedbackResponse(
        id=str(fb.id),
        author_id=str(fb.author_id),
        author_email=email,
        author_name=name,
        category=fb.category,
        text=fb.text,
        page_url=fb.page_url,
        status=fb.status,
        admin_notes=fb.admin_notes,
        created_at=fb.created_at.isoformat(),
    )
