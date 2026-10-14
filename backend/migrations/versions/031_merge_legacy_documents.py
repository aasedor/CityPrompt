"""Join the old production document branch and the current release schema.

No data rewrite or version restamping: Alembic applies each missing branch first.
"""

revision = "031_merge_legacy_documents"
down_revision = ("030_render_attempts", "022_document_processing_task")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
