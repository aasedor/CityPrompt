"""Add performance indexes for analytics queries

Revision ID: 013_add_analytics_indexes
Revises: 012_add_last_login_at
Create Date: 2026-02-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013_add_analytics_indexes"
down_revision: Union[str, None] = "012_add_last_login_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_exists(name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = :name)"), {"name": name})
    return result.scalar()


def upgrade() -> None:
    if not _index_exists("ix_users_created_at"):
        op.create_index("ix_users_created_at", "users", ["created_at"])

    if not _index_exists("ix_buildings_generation_status"):
        op.create_index("ix_buildings_generation_status", "buildings", ["generation_status"])

    if not _index_exists("ix_buildings_generation_engine"):
        op.create_index("ix_buildings_generation_engine", "buildings", ["generation_engine"])

    if not _index_exists("ix_documents_uploaded_at"):
        op.create_index("ix_documents_uploaded_at", "documents", ["uploaded_at"])


def downgrade() -> None:
    op.drop_index("ix_documents_uploaded_at", table_name="documents")
    op.drop_index("ix_buildings_generation_engine", table_name="buildings")
    op.drop_index("ix_buildings_generation_status", table_name="buildings")
    op.drop_index("ix_users_created_at", table_name="users")
