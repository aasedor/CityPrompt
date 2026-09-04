"""Persist plan-bound student reports and attributed decision history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "029_student_reports"
down_revision = "028_reference_layers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_planning_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "requested_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("requested_by_name", sa.String(255), nullable=False),
        sa.Column("plan_version", sa.String(64), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("analysis", postgresql.JSONB(), nullable=False),
        sa.Column("decisions", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "decision_history", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "response_revision", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_student_planning_reports_project_id",
        "student_planning_reports",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_table("student_planning_reports")
