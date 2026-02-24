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


def upgrade() -> None:
    op.add_column(
        "site_zones",
        sa.Column("building_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_site_zones_building_id",
        "site_zones",
        "buildings",
        ["building_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_site_zones_building_id", "site_zones", type_="foreignkey")
    op.drop_column("site_zones", "building_id")
