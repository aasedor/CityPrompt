"""
Authentication API endpoints.
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import enforce_rate_limit
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    issue_session_tokens,
    require_auth,
    revoke_user_sessions,
    session_version,
    token_digest,
    token_subject,
    validate_session_version,
    verify_password,
)
from app.models.models import User, UserRefreshSession
from app.schemas.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Register a new user account. Returns the created user profile. Raises 409 if email is already taken."""
    # Check if email already exists
    email = user_in.email.strip().lower()
    await enforce_rate_limit(request, 300, 3600, bucket="auth-register-ip")
    await enforce_rate_limit(request, 3, 3600, bucket="auth-register-email", identity=email)
    result = await db.execute(select(User).where(func.lower(User.email) == email).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role="editor",
        render_credits=1000,  # matches the column default; set explicitly so it exists pre-flush
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Authenticate with email/password and receive JWT access + refresh tokens."""
    email = credentials.email.strip().lower()
    await enforce_rate_limit(request, 120, 60, bucket="auth-login-ip")
    await enforce_rate_limit(request, 10, 60, bucket="auth-login-email", identity=email)
    result = await db.execute(
        select(User).where(func.lower(User.email) == email).with_for_update().execution_options(populate_existing=True)
    )
    try:
        user = result.scalar_one_or_none()
    except MultipleResultsFound:
        raise HTTPException(409, "Multiple existing accounts use this email. Contact an administrator.")

    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    access_token, refresh_token = await issue_session_tokens(user, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Exchange a refresh token for a new access/refresh token pair. Use when the access token expires."""
    await enforce_rate_limit(request, 240, 60, bucket="auth-refresh-ip")
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type — expected refresh token")

    user_id = token_subject(payload)
    await enforce_rate_limit(request, 60, 60, bucket="auth-refresh-user", identity=str(user_id))
    result = await db.execute(
        select(User).where(User.id == user_id).with_for_update().execution_options(populate_existing=True)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    validate_session_version(payload, user)
    try:
        session_id = uuid.UUID(payload["sid"])
        nonce = payload["jti"]
        if not isinstance(nonce, str) or not nonce or len(nonce) > 200:
            raise ValueError("Invalid nonce")
    except (KeyError, ValueError, TypeError, AttributeError):
        raise HTTPException(401, "Invalid refresh session")

    result = await db.execute(
        select(UserRefreshSession)
        .where(UserRefreshSession.id == session_id, UserRefreshSession.user_id == user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    session = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if (
        not session
        or session.session_version != session_version(user)
        or session.expires_at.replace(tzinfo=timezone.utc) <= now
        or not secrets.compare_digest(session.token_hash, token_digest(nonce))
    ):
        raise HTTPException(401, "Invalid or already used refresh token")

    new_nonce = secrets.token_urlsafe(32)
    session.token_hash = token_digest(new_nonce)
    session.expires_at = now + timedelta(days=get_settings().jwt_refresh_token_expire_days)
    await db.flush()
    access_token = create_access_token(str(user.id), user.role, session_version=session_version(user))
    new_refresh_token = create_refresh_token(
        str(user.id),
        session_version=session_version(user),
        session_id=str(session.id),
        nonce=new_nonce,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(require_auth),
):
    """Get the profile of the currently authenticated user. Requires a valid access token."""
    return user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Change password for the currently authenticated user. Requires current password."""
    await enforce_rate_limit(request, 120, 60, bucket="auth-change-password-ip")
    await enforce_rate_limit(request, 10, 900, bucket="auth-change-password-user", identity=str(user.id))
    result = await db.execute(
        select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    if not user.hashed_password or not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.hashed_password = hash_password(body.new_password)
    revoke_user_sessions(user)
    await db.flush()
    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Request a password reset email. Always returns success to avoid leaking email existence."""
    settings = get_settings()
    email = body.email.strip().lower()
    await enforce_rate_limit(request, 120, 900, bucket="auth-forgot-password-ip")
    await enforce_rate_limit(request, 3, 900, bucket="auth-forgot-password-email", identity=email)

    result = await db.execute(
        select(User).where(func.lower(User.email) == email).with_for_update().execution_options(populate_existing=True)
    )
    try:
        user = result.scalar_one_or_none()
    except MultipleResultsFound:
        user = None  # Do not reset an arbitrary legacy case-duplicate account.

    if user and user.is_active:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        nonce = secrets.token_urlsafe(32)
        user.reset_nonce_hash = token_digest(nonce)
        await db.flush()
        reset_token = jwt.encode(
            {
                "sub": str(user.id),
                "type": "reset",
                "exp": expire,
                "ver": session_version(user),
                "jti": nonce,
            },
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
        try:
            from app.core.email import send_password_reset_email

            await send_password_reset_email(user.email, reset_link)
        except Exception:
            logger.warning("Failed to send reset email for %s", body.email)

    return MessageResponse(message="If that email is registered, a reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    *,
    request: Request,
):
    """Reset password using a token from a password reset email."""
    await enforce_rate_limit(request, 30, 900, bucket="auth-reset-password-ip")
    payload = decode_token(body.token)

    if payload.get("type") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    user_id = token_subject(payload)
    result = await db.execute(
        select(User).where(User.id == user_id).with_for_update().execution_options(populate_existing=True)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    validate_session_version(payload, user)
    nonce = payload.get("jti")
    if (
        not isinstance(nonce, str)
        or not nonce
        or len(nonce) > 200
        or not user.reset_nonce_hash
        or not secrets.compare_digest(user.reset_nonce_hash, token_digest(nonce))
    ):
        raise HTTPException(400, "Invalid or already used reset token")

    user.hashed_password = hash_password(body.new_password)
    revoke_user_sessions(user)
    # Mailbox recovery must also remove an old provider's route back into the
    # account. A stored provider subject carries no persisted proof that its
    # original email claim was authoritative (Microsoft/third-party Google).
    user.oauth_provider = None
    user.oauth_subject = None
    await db.flush()
    return MessageResponse(message="Password has been reset successfully")
