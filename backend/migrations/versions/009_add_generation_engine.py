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


def upgrade() -> None:
    op.add_column("buildings", sa.Column("generation_engine", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("buildings", "generation_engine")
