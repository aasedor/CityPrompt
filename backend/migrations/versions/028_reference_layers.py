"""Separate reference datasets from authored community geometry.

Revision ID: 028_reference_layers
Revises: 027_add_active_site_boundary
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "028_reference_layers"
down_revision = "027_add_active_site_boundary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reference_layers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("source_filename", sa.String(255), nullable=False),
        sa.Column("source_crs", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(2048)),
        sa.Column("description", sa.Text()),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("feature_collection", postgresql.JSONB(), nullable=False),
        sa.Column("feature_count", sa.Integer(), nullable=False),
        sa.Column("storage_bytes", sa.Integer(), nullable=False),
        sa.Column("bounds", postgresql.JSONB(), nullable=False),
        sa.Column("warnings", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("opacity", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "content_hash", name="uq_reference_layer_content"),
    )
    op.create_index("ix_reference_layers_project_id", "reference_layers", ["project_id"])


def downgrade() -> None:
    op.drop_table("reference_layers")
