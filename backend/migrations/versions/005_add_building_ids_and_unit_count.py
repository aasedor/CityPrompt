"""Add building_ids JSONB column to site_zones

Revision ID: 005_add_building_ids
Revises: 004_add_site_boundary
Create Date: 2026-02-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "005_add_building_ids"
down_revision: Union[str, None] = "004_add_site_boundary"
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
    if not _column_exists("site_zones", "building_ids"):
        op.add_column("site_zones", sa.Column("building_ids", JSONB, nullable=True))


def downgrade() -> None:
    if _column_exists("site_zones", "building_ids"):
        op.drop_column("site_zones", "building_ids")
