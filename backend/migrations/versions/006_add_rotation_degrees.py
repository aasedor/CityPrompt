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


def upgrade() -> None:
    op.add_column("buildings", sa.Column("rotation_degrees", sa.Numeric(6, 2), nullable=True, server_default="0"))


def downgrade() -> None:
    op.drop_column("buildings", "rotation_degrees")
