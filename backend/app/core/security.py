"""
Security utilities: password hashing, JWT token creation and verification.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, role: str = "editor", *, session_version: int = 0) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "ver": session_version,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    user_id: str,
    *,
    session_version: int = 0,
    session_id: str | None = None,
    nonce: str | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "ver": session_version,
        "sid": session_id,
        "jti": nonce or secrets.token_urlsafe(32),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def token_digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def token_subject(payload: dict) -> uuid.UUID:
    """Reject malformed signed identities as credentials, rather than server errors."""
    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError, TypeError, AttributeError):
        raise HTTPException(401, "Invalid token payload")


def session_version(user) -> int:
    return getattr(user, "session_version", 0) or 0


def validate_session_version(payload: dict, user) -> None:
    # Missing versions intentionally invalidate sessions issued before the migration.
    if type(payload.get("ver")) is not int or payload["ver"] != session_version(user):
        raise HTTPException(401, "This session has expired. Please sign in again.")


def revoke_user_sessions(user) -> None:
    user.session_version = session_version(user) + 1
    user.reset_nonce_hash = None


async def issue_session_tokens(user, db: AsyncSession) -> tuple[str, str]:
    from app.models.models import UserRefreshSession

    nonce = secrets.token_urlsafe(32)
    version = session_version(user)
    session = UserRefreshSession(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=token_digest(nonce),
        session_version=version,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    db.add(session)
    await db.flush()
    return (
        create_access_token(str(user.id), user.role, session_version=version),
        create_refresh_token(
            str(user.id),
            session_version=version,
            session_id=str(session.id),
            nonce=nonce,
        ),
    )


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """FastAPI dependency that extracts and validates the current user from JWT.

    Returns None if no token provided (allows optional auth).
    Use `require_auth` for endpoints that must be authenticated.
    """
    if token is None:
        return None

    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = token_subject(payload)

    from app.models.models import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    validate_session_version(payload, user)

    return user


async def require_auth(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Strict auth dependency — raises 401 if not authenticated."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_current_user(token, db)


def require_role(required_role: str):
    """Factory for role-checking dependencies.

    Usage: Depends(require_role("admin"))
    """

    async def checker(user=Depends(require_auth)):
        role_hierarchy = {"viewer": 0, "editor": 1, "admin": 2, "cofounder": 3}
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role",
            )
        return user

    return checker


def is_admin_or_above(user) -> bool:
    """Return True if the user's role is admin or cofounder."""
    return user.role in ("admin", "cofounder")


require_admin = require_role("admin")
require_cofounder = require_role("cofounder")


def visible_project_ids(user):
    """A query usable by resource lists without first exposing other tenants' IDs."""
    from app.models.models import Project, ProjectShare

    query = select(Project.id)
    if is_admin_or_above(user):
        return query
    accepted = select(ProjectShare.project_id).where(ProjectShare.user_id == user.id)
    return query.where(or_(Project.owner_id == user.id, Project.id.in_(accepted)))


async def check_project_permission(
    project_id: uuid.UUID,
    user,
    db: AsyncSession,
    required: str = "viewer",
) -> str:
    """Check if a user has the required permission on a project.

    Returns the user's permission level: 'owner', 'editor', or 'viewer'.
    Raises HTTPException 403 if the user doesn't have the required permission.

    Permission hierarchy: owner > editor > viewer
    """
    from app.models.models import Project, ProjectShare

    if required not in {"viewer", "editor"}:
        raise ValueError("Project permission must be viewer or editor")

    # Load project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Project owner has full access
    if user and project.owner_id == user.id:
        return "owner"

    # Admin/cofounder users have full access
    if user and is_admin_or_above(user):
        return "owner"

    # Check project shares
    if user:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                ProjectShare.user_id == user.id,
            )
        )
        share = share_result.scalar_one_or_none()
        if share:
            permission_hierarchy = {"viewer": 0, "editor": 1}
            required_level = permission_hierarchy.get(required, 0)
            user_level = permission_hierarchy.get(share.permission, 0)
            if user_level >= required_level:
                return share.permission
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required} permission on this project",
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this project",
    )


async def check_project_read_access(
    project_id: uuid.UUID,
    user,
    db: AsyncSession,
    share_token: str | None = None,
) -> None:
    """A public link grants read access only to its own project while it exists."""
    from app.models.models import ProjectShare

    if share_token:
        result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                ProjectShare.invite_token == share_token,
                ProjectShare.is_public_link.is_(True),
            )
        )
        if result.scalar_one_or_none():
            return
        raise HTTPException(status_code=403, detail="Invalid or revoked public share link")
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    await check_project_permission(project_id, user, db, required="viewer")


def create_project_asset_ticket(project_id: uuid.UUID, user_id: uuid.UUID, *, session_version: int = 0) -> str:
    """Issue a short-lived read-only credential, never a login credential."""
    return jwt.encode(
        {
            "type": "project_asset",
            "sub": str(user_id),
            "project_id": str(project_id),
            "ver": session_version,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_file_asset_ticket(file_path: str, user_id: uuid.UUID, *, session_version: int = 0) -> str:
    """Limit URL authentication to one stored object for fifteen minutes."""
    return jwt.encode(
        {
            "type": "file_asset",
            "sub": str(user_id),
            "file_path": file_path,
            "ver": session_version,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def check_project_asset_access(
    project_id: uuid.UUID,
    user,
    db: AsyncSession,
    *,
    share_token: str | None = None,
    asset_ticket: str | None = None,
) -> None:
    """Recheck membership on every asset request so revocation stays effective."""
    from app.models.models import User

    if share_token or user is not None:
        await check_project_read_access(project_id, user, db, share_token)
        return
    if asset_ticket:
        payload = decode_token(asset_ticket)
        if payload.get("type") != "project_asset" or payload.get("project_id") != str(project_id):
            raise HTTPException(status_code=403, detail="Asset ticket does not cover this project")
        try:
            user_id = uuid.UUID(payload["sub"])
        except (KeyError, ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Invalid asset ticket") from None
        result = await db.execute(select(User).where(User.id == user_id))
        ticket_user = result.scalar_one_or_none()
        if not ticket_user or not ticket_user.is_active:
            raise HTTPException(status_code=401, detail="Asset ticket account is inactive")
        validate_session_version(payload, ticket_user)
        await check_project_permission(project_id, ticket_user, db, required="viewer")
        return
    raise HTTPException(status_code=401, detail="Authentication required")
