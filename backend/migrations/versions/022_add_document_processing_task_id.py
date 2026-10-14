"""Track the Celery task authorized for each document.

Revision ID: 022_document_processing_task
Revises: 021_add_previous_snapshot
Create Date: 2026-08-30

Preserved from the previous production repository (807e323). Keep this branch
identity so its deployed database can upgrade without changing its version stamp.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022_document_processing_task"
down_revision: Union[str, None] = "021_add_previous_snapshot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("processing_task_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_documents_processing_task_id",
        "documents",
        ["processing_task_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_documents_processing_task_id", table_name="documents")
    op.drop_column("documents", "processing_task_id")
