"""
Ensure admin users exist on every startup.

- Creates admin@example.com with a default password if it doesn't exist.
- Promotes wbeshry@gmail.com to admin if the account exists.

Run:  python -m scripts.ensure_admins
"""

import asyncio
import os

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.models import User

# Default admin account
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123!")

# Accounts to always promote to admin when they exist
PROMOTE_EMAILS = [
    "wbeshry@gmail.com",
]


async def ensure_admins() -> None:
    async with async_session_factory() as db:
        # 1. Ensure default admin account exists
        result = await db.execute(select(User).where(User.email == DEFAULT_ADMIN_EMAIL))
        admin_user = result.scalar_one_or_none()

        if admin_user is None:
            admin_user = User(
                email=DEFAULT_ADMIN_EMAIL,
                hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
                full_name="Platform Admin",
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            await db.flush()
            print(f"[ensure_admins] Created admin user: {DEFAULT_ADMIN_EMAIL}")
        elif admin_user.role != "admin":
            admin_user.role = "admin"
            print(f"[ensure_admins] Promoted {DEFAULT_ADMIN_EMAIL} to admin")
        else:
            print(f"[ensure_admins] {DEFAULT_ADMIN_EMAIL} already admin — OK")

        # 2. Promote configured emails to cofounder
        for email in PROMOTE_EMAILS:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if user is None:
                print(f"[ensure_admins] {email} not registered yet — skipping")
            elif user.role != "cofounder":
                user.role = "cofounder"
                print(f"[ensure_admins] Promoted {email} to cofounder")
            else:
                print(f"[ensure_admins] {email} already cofounder — OK")

        await db.commit()
        print("[ensure_admins] Done.")


if __name__ == "__main__":
    asyncio.run(ensure_admins())
