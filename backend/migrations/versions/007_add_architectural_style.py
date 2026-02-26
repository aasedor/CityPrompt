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


def upgrade() -> None:
    op.add_column("buildings", sa.Column("architectural_style", sa.String(50), nullable=True))
    op.add_column("projects", sa.Column("default_style", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("buildings", "architectural_style")
    op.drop_column("projects", "default_style")
