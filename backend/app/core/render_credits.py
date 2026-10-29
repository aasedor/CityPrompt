"""Read-only credit policy shared by discovery, admission and reservation."""
from datetime import datetime, timezone

from app.core.security import is_admin_or_above

WEEKLY_TOKEN_ALLOWANCE = 1000


def effective_render_credit_balance(user, *, at: datetime | None = None) -> int:
    """Include a due weekly allowance without changing any account fields."""
    if not is_admin_or_above(user):
        current = at or datetime.now(timezone.utc)
        if user.credits_reset_at is None or (current - user.credits_reset_at).days >= 7:
            return WEEKLY_TOKEN_ALLOWANCE
    return user.render_credits
