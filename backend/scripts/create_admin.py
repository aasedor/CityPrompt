"""
CLI script to create or promote an admin user.

Usage:
    # Create a new admin user
    python -m scripts.create_admin --email admin@test.com --password testpass123

    # Promote an existing user to admin
    python -m scripts.create_admin --email user@test.com --promote
"""

import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.models import User


async def create_admin(email: str, password: str) -> None:
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"User {email} already exists (role: {existing.role}).")
            print("Use --promote to change their role to admin.")
            sys.exit(1)

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        print(f"Admin user created: {email}")


async def promote_to_admin(email: str) -> None:
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"User {email} not found.")
            sys.exit(1)

        if user.role == "admin":
            print(f"User {email} is already an admin.")
            return

        old_role = user.role
        user.role = "admin"
        await db.commit()
        print(f"User {email} promoted from {old_role} to admin.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--password", help="Password for new user (required without --promote)")
    parser.add_argument("--promote", action="store_true", help="Promote existing user to admin")

    args = parser.parse_args()

    if args.promote:
        asyncio.run(promote_to_admin(args.email))
    elif args.password:
        asyncio.run(create_admin(args.email, args.password))
    else:
        parser.error("--password is required when creating a new admin user (without --promote)")


if __name__ == "__main__":
    main()
