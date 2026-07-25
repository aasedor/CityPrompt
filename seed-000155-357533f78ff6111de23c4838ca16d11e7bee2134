"""Add building_id FK to site_zones table

Revision ID: 003_zone_building_link
Revises: 002_dev_area_generation
Create Date: 2026-02-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "003_zone_building_link"
down_revision: Union[str, None] = "002_dev_area_generation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_name = :table AND column_name = :column)"
    ), {"table": table, "column": column})
    return result.scalar()


def _constraint_exists(constraint: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.table_constraints "
        "WHERE constraint_name = :name)"
    ), {"name": constraint})
    return result.scalar()


def upgrade() -> None:
    if not _column_exists("site_zones", "building_id"):
        op.add_column(
            "site_zones",
            sa.Column("building_id", UUID(as_uuid=True), nullable=True),
        )
    if not _constraint_exists("fk_site_zones_building_id"):
        op.create_foreign_key(
            "fk_site_zones_building_id",
            "site_zones",
            "buildings",
            ["building_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    if _constraint_exists("fk_site_zones_building_id"):
        op.drop_constraint("fk_site_zones_building_id", "site_zones", type_="foreignkey")
    if _column_exists("site_zones", "building_id"):
        op.drop_column("site_zones", "building_id")
