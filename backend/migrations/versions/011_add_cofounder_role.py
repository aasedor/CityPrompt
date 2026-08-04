"""Add 'cofounder' value to user_role enum

Revision ID: 011_add_cofounder_role
Revises: 010_add_pending_role_changes
Create Date: 2026-02-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011_add_cofounder_role"
down_revision: Union[str, None] = "010_add_pending_role_changes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _enum_value_exists(enum_name: str, value: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM pg_enum "
            "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
            "WHERE pg_type.typname = :enum_name AND pg_enum.enumlabel = :value)"
        ),
        {"enum_name": enum_name, "value": value},
    )
    return result.scalar()


def upgrade() -> None:
    if not _enum_value_exists("user_role", "cofounder"):
        op.execute("ALTER TYPE user_role ADD VALUE 'cofounder'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly.
    # To downgrade, you would need to recreate the enum type without 'cofounder'.
    pass
