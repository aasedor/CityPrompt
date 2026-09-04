"""Reference data is deliberately independent of authored SiteZone records."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReferenceLayer(Base):
    __tablename__ = "reference_layers"
    __table_args__ = (UniqueConstraint("project_id", "content_hash", name="uq_reference_layer_content"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(160))
    source_filename: Mapped[str] = mapped_column(String(255))
    source_crs: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(2048))
    description: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(24), default="reference")
    feature_collection: Mapped[dict] = mapped_column(JSONB)
    feature_count: Mapped[int] = mapped_column(Integer)
    storage_bytes: Mapped[int] = mapped_column(Integer)
    bounds: Mapped[list] = mapped_column(JSONB)
    warnings: Mapped[list] = mapped_column(JSONB, default=list)
    content_hash: Mapped[str] = mapped_column(String(64))
    color: Mapped[str] = mapped_column(String(7), default="#7c3aed")
    opacity: Mapped[float] = mapped_column(Float, default=0.8)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
