"""Add architectural_style column to buildings and default_style to projects

Revision ID: 007_add_architectural_style
Revises: 006_add_rotation_degrees
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_add_architectural_style"
down_revision: Union[str, None] = "006_add_rotation_degrees"
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
    if not _column_exists("buildings", "architectural_style"):
        op.add_column("buildings", sa.Column("architectural_style", sa.String(50), nullable=True))
    if not _column_exists("projects", "default_style"):
        op.add_column("projects", sa.Column("default_style", sa.String(50), nullable=True))


def downgrade() -> None:
    if _column_exists("buildings", "architectural_style"):
        op.drop_column("buildings", "architectural_style")
    if _column_exists("projects", "default_style"):
        op.drop_column("projects", "default_style")
