"""Add provider identity binding, revocable sessions and single-use reset state.

Existing users, passwords, roles and credits are preserved. Pre-upgrade bearer
and reset JWTs deliberately require sign-in/reset again because they have no
server-verifiable session version or single-use nonce. Provider subjects cannot
be inferred from legacy email addresses and remain NULL until securely bound.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "032_auth_sessions"
down_revision = "031_merge_legacy_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("oauth_subject", sa.String(255), nullable=True))
    op.add_column(
        "users",
        sa.Column("session_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("users", sa.Column("reset_nonce_hash", sa.String(64), nullable=True))
    op.create_unique_constraint("uq_users_oauth_identity", "users", ["oauth_provider", "oauth_subject"])
    op.create_table(
        "user_refresh_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_refresh_sessions_user_id", "user_refresh_sessions", ["user_id"])


def downgrade():
    op.drop_table("user_refresh_sessions")
    op.drop_constraint("uq_users_oauth_identity", "users", type_="unique")
    op.drop_column("users", "reset_nonce_hash")
    op.drop_column("users", "session_version")
    op.drop_column("users", "oauth_subject")
