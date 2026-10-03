"""Durable idempotent image attempts and once-only student refunds."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "030_render_attempts"
down_revision = "029_student_reports"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("render_audit_logs", sa.Column("student_refunded_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("""UPDATE render_audit_logs SET student_refunded_at = created_at
        WHERE prompt_preview LIKE '[Direct 3D student refunded; provider cost unknown]%'
           OR prompt_preview LIKE '[Direct 3D unbilled failure]%'""")
    op.create_table(
        "render_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("request_sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("style", sa.String(100), nullable=False),
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("render_audit_logs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("error", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_render_attempt_user_key"),
    )
    for column in ("user_id", "project_id", "status"):
        op.create_index(f"ix_render_attempts_{column}", "render_attempts", [column])


def downgrade():
    op.drop_table("render_attempts")
    op.drop_column("render_audit_logs", "student_refunded_at")
