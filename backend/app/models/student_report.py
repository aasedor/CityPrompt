"""Versioned advisory reports; students' decisions never mutate the design."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudentPlanningReport(Base):
    __tablename__ = "student_planning_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    requested_by_name: Mapped[str] = mapped_column(String(255))
    plan_version: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict] = mapped_column(JSONB)
    analysis: Mapped[dict] = mapped_column(JSONB)
    decisions: Mapped[dict] = mapped_column(JSONB, default=dict)
    decision_history: Mapped[list] = mapped_column(JSONB, default=list)
    response_revision: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
