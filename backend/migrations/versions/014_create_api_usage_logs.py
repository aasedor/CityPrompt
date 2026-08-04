"""Create api_usage_logs table for tracking external API consumption

Revision ID: 014_create_api_usage_logs
Revises: 013_add_analytics_indexes
Create Date: 2026-02-28
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014_create_api_usage_logs"
down_revision: Union[str, None] = "013_add_analytics_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL with IF NOT EXISTS to handle the case where the table
    # was already created by a previous create_all() call
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            provider VARCHAR(30) NOT NULL,
            operation VARCHAR(50) NOT NULL,
            credits_used NUMERIC(10, 2),
            input_tokens INTEGER,
            output_tokens INTEGER,
            task_id VARCHAR(100),
            building_id UUID,
            document_id UUID,
            user_id UUID,
            status VARCHAR(20) DEFAULT 'success',
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(building_id) REFERENCES buildings (id) ON DELETE SET NULL,
            FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE SET NULL,
            FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_api_usage_logs_provider_created_at
        ON api_usage_logs (provider, created_at)
    """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_api_usage_logs_user_id_created_at
        ON api_usage_logs (user_id, created_at)
    """
    )


def downgrade() -> None:
    op.drop_index("ix_api_usage_logs_user_id_created_at", table_name="api_usage_logs")
    op.drop_index("ix_api_usage_logs_provider_created_at", table_name="api_usage_logs")
    op.drop_table("api_usage_logs")
