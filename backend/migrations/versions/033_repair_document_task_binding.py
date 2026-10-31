"""Repair document task binding on legacy databases stamped past migration022.

Normal installations already have the column/index from022. Some preserved
deployments were stamped at the merge revision without that branch's schema.
This additive check preserves every existing document and task binding.
"""

from alembic import op
import sqlalchemy as sa

revision = "033_repair_document_task_binding"
down_revision = "032_auth_sessions"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "processing_task_id" not in {column["name"] for column in inspector.get_columns("documents")}:
        op.add_column("documents", sa.Column("processing_task_id", sa.String(100), nullable=True))
    if "ix_documents_processing_task_id" not in {index["name"] for index in inspector.get_indexes("documents")}:
        op.create_index("ix_documents_processing_task_id", "documents", ["processing_task_id"], unique=False)


def downgrade():
    # The column belongs to022 and must survive a downgrade of this repair.
    pass
