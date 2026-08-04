"""Add render_credits and credits_reset_at columns to users table

Revision ID: 018_add_render_credits
Revises: 017_create_beta_feedback
Create Date: 2026-03-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_add_render_credits"
down_revision: Union[str, None] = "017_create_beta_feedback"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column)"
        ),
        {"table": table, "column": column},
    )
    return result.scalar()


def upgrade() -> None:
    if not _column_exists("users", "render_credits"):
        op.add_column("users", sa.Column("render_credits", sa.Integer(), nullable=False, server_default="1000"))
    # Update existing users from 10 to 1000
    op.execute(sa.text("UPDATE users SET render_credits = 1000 WHERE render_credits <= 10"))
    if not _column_exists("users", "credits_reset_at"):
        op.add_column("users", sa.Column("credits_reset_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "credits_reset_at")
    op.drop_column("users", "render_credits")
