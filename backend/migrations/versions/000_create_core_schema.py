"""Create the core application schema.

Revision ID: 000_core_schema
Revises: None
Create Date: 2026-08-04

The original migration chain began with ``site_zones`` and assumed that the
core tables had already been created outside Alembic.  Keeping that assumption
made fresh development, CI, and review databases impossible to provision.  This
baseline records the schema that predates migration 001; all later migrations
continue to apply their historical changes in order.
"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "000_core_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    user_role = sa.Enum("viewer", "editor", "admin", name="user_role")
    project_status = sa.Enum("draft", "processing", "ready", "archived", name="project_status")
    share_permission = sa.Enum("viewer", "editor", name="share_permission")
    processing_status = sa.Enum("pending", "processing", "completed", "failed", name="processing_status")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("oauth_provider", sa.String(50), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="editor"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", geoalchemy2.Geography("POINT", srid=4326), nullable=True),
        sa.Column("site_boundary", geoalchemy2.Geography("POLYGON", srid=4326), nullable=True),
        sa.Column("status", project_status, nullable=False, server_default="draft"),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("construction_phases", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "buildings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("footprint", geoalchemy2.Geography("POLYGON", srid=4326), nullable=True),
        sa.Column("height_meters", sa.Numeric(10, 2), nullable=True),
        sa.Column("floor_count", sa.Integer(), nullable=True),
        sa.Column("floor_height_meters", sa.Numeric(5, 2), nullable=True),
        sa.Column("roof_type", sa.String(50), nullable=True),
        sa.Column("construction_phase", sa.Integer(), nullable=True),
        sa.Column("model_url", sa.String(500), nullable=True),
        sa.Column("lod_urls", JSONB, nullable=True),
        sa.Column("specifications", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_buildings_project_id", "buildings", ["project_id"])

    op.create_table(
        "project_shares",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("permission", share_permission, nullable=False, server_default="viewer"),
        sa.Column("invite_token", sa.String(64), nullable=True),
        sa.Column("is_public_link", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("invite_token", name="uq_project_shares_invite_token"),
    )
    op.create_index("ix_project_shares_project_id", "project_shares", ["project_id"])
    op.create_index("ix_project_shares_user_id", "project_shares", ["user_id"])
    op.create_index("ix_project_shares_email", "project_shares", ["email"])

    op.create_table(
        "annotations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "building_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buildings.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("position_x", sa.Numeric(10, 3), nullable=False),
        sa.Column("position_y", sa.Numeric(10, 3), nullable=False),
        sa.Column("position_z", sa.Numeric(10, 3), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_annotations_project_id", "annotations", ["project_id"])

    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_url", sa.String(500), nullable=False),
        sa.Column("processing_status", processing_status, nullable=False, server_default="pending"),
        sa.Column("extracted_data", JSONB, nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"])

    op.create_table(
        "activity_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_activity_logs_project_id", "activity_logs", ["project_id"])


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("documents")
    op.drop_table("annotations")
    op.drop_table("project_shares")
    op.drop_table("buildings")
    op.drop_table("projects")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS processing_status")
    op.execute("DROP TYPE IF EXISTS share_permission")
    op.execute("DROP TYPE IF EXISTS project_status")
    op.execute("DROP TYPE IF EXISTS user_role")
