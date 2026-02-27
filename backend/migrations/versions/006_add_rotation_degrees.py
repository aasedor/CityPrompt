"""Add rotation_degrees column to buildings

Revision ID: 006_add_rotation_degrees
Revises: 005_add_building_ids
Create Date: 2026-02-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_add_rotation_degrees"
down_revision: Union[str, None] = "005_add_building_ids"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_name = :table AND column_name = :column)"
    ), {"table": table, "column": column})
    return result.scalar()


def upgrade() -> None:
    if not _column_exists("buildings", "rotation_degrees"):
        op.add_column("buildings", sa.Column("rotation_degrees", sa.Numeric(6, 2), nullable=True, server_default="0"))


def downgrade() -> None:
    if _column_exists("buildings", "rotation_degrees"):
        op.drop_column("buildings", "rotation_degrees")
