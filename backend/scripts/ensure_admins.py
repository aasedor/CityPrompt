"""Explicit one-time administrator creation; never change existing privileges."""

import asyncio
import os

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.models import User


def bootstrap_credentials():
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
    if not email and not password:
        return None
    if "@" not in email or len(password) < 16:
        raise ValueError("Set BOOTSTRAP_ADMIN_EMAIL and a unique BOOTSTRAP_ADMIN_PASSWORD of at least 16 characters")
    return email, password


async def ensure_admins():
    credentials = bootstrap_credentials()
    if credentials is None:
        return
    email, password = credentials
    async with async_session_factory() as db:
        user = await db.scalar(select(User).where(User.email == email))
        if user is not None:
            if user.role not in {"admin", "cofounder"}:
                raise RuntimeError("Bootstrap email belongs to an existing non-administrator; review account ownership manually")
            return  # Never reset an existing administrator's password or role.
        db.add(User(email=email, hashed_password=hash_password(password), full_name="Classroom administrator", role="admin", is_active=True))
        await db.commit()


if __name__ == "__main__":
    asyncio.run(ensure_admins())
