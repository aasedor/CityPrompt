"""Create api_usage_logs table for tracking external API consumption

Revision ID: 014_create_api_usage_logs
Revises: 013_add_analytics_indexes
Create Date: 2026-02-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014_create_api_usage_logs"
down_revision: Union[str, None] = "013_add_analytics_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_usage_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("operation", sa.String(50), nullable=False),
        sa.Column("credits_used", sa.Numeric(10, 2), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("task_id", sa.String(100), nullable=True),
        sa.Column("building_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("document_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), server_default="success"),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_index("ix_api_usage_logs_provider_created_at", "api_usage_logs", ["provider", "created_at"])
    op.create_index("ix_api_usage_logs_user_id_created_at", "api_usage_logs", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_api_usage_logs_user_id_created_at", table_name="api_usage_logs")
    op.drop_index("ix_api_usage_logs_provider_created_at", table_name="api_usage_logs")
    op.drop_table("api_usage_logs")
