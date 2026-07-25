"""Add site_boundary to zone_type enum

Revision ID: 004_add_site_boundary
Revises: 003_zone_building_link
Create Date: 2026-02-18
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_add_site_boundary"
down_revision: Union[str, None] = "003_zone_building_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE zone_type ADD VALUE IF NOT EXISTS 'site_boundary'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    # A full migration would need to recreate the enum, which is out of scope.
    pass
