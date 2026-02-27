"""Add pending_role_changes table for admin demotion confirmation

Revision ID: 010_add_pending_role_changes
Revises: 009_add_generation_engine
Create Date: 2026-02-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010_add_pending_role_changes"
down_revision: Union[str, None] = "009_add_generation_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_name = :table)"
    ), {"table": table})
    return result.scalar()


def upgrade() -> None:
    if not _table_exists("pending_role_changes"):
        op.create_table(
            "pending_role_changes",
            sa.Column("id", sa.UUID(), primary_key=True),
            sa.Column("token", sa.String(64), unique=True, nullable=False, index=True),
            sa.Column("target_user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("requested_by_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("new_role", sa.String(20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("pending_role_changes")
