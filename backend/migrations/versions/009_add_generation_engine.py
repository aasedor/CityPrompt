"""Add generation_engine column to buildings

Revision ID: 009_add_generation_engine
Revises: 008_add_render_previews
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_add_generation_engine"
down_revision: Union[str, None] = "008_add_render_previews"
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
    if not _column_exists("buildings", "generation_engine"):
        op.add_column("buildings", sa.Column("generation_engine", sa.String(20), nullable=True))


def downgrade() -> None:
    if _column_exists("buildings", "generation_engine"):
        op.drop_column("buildings", "generation_engine")
