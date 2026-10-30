"""
OAuth2 social login endpoints for Google and Microsoft.
"""

import logging
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import issue_session_tokens, revoke_user_sessions
from app.models.models import User
from app.services.oauth_state import issue_state, bind_browser, consume_state

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# =============================================================================
# Google OAuth2
# =============================================================================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def _allowed_frontend_origins() -> set[str]:
    allowed = {settings.frontend_url.rstrip("/")}
    allowed.update(origin.rstrip("/") for origin in settings.cors_origins if origin)
    return {origin for origin in allowed if origin}


def _is_allowed_frontend_origin(frontend_origin: str | None) -> bool:
    if not frontend_origin:
        return False
    normalized = frontend_origin.rstrip("/")
    if normalized in _allowed_frontend_origins():
        return True

    # Linked worktrees deliberately run Vite on the IPv4 loopback so Windows
    # does not route the proxy through a stale IPv6/WSL listener. Older shared
    # .env files often list localhost only, however, which made OAuth discard
    # the initiating 127.0.0.1 origin and fall back to the obsolete port 5175.
    # Accept a syntactically pure loopback *origin* in development only.
    if settings.is_production:
        return False
    try:
        parsed = urlparse(normalized)
        _ = parsed.port  # Validate malformed port values.
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        and parsed.username is None
        and parsed.password is None
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    )


def _oauth_error_redirect(frontend_origin: str, message: str) -> RedirectResponse:
    params = urlencode({"oauth_error": message})
    return RedirectResponse(url=f"{frontend_origin}/oauth/callback?{params}", status_code=302)


async def _resolve_oauth_user(db: AsyncSession, provider: str, profile: dict) -> User:
    """Bind identities by the provider's immutable OIDC subject, never by mutable mail."""
    subject = profile.get("sub")
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 255:
        raise HTTPException(400, "The sign-in provider did not return a valid account identity.")

    result = await db.execute(
        select(User)
        .where(User.oauth_provider == provider, User.oauth_subject == subject)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    user = result.scalar_one_or_none()
    if user:
        if not user.is_active:
            raise HTTPException(403, "Account is disabled")
        return user

    try:
        email = str(TypeAdapter(EmailStr).validate_python(profile.get("email"))).strip().lower()
        if len(email) > 255:
            raise ValueError("Email too long")
    except (ValidationError, ValueError):
        raise HTTPException(400, "The sign-in provider did not return a valid email address.")

    # Google is authoritative for Gmail and verified Workspace addresses only.
    # Microsoft email/preferred_username/UPN are display hints, not proof of mail ownership.
    verified = provider == "google" and profile.get("email_verified") is True
    authoritative = verified and (email.endswith("@gmail.com") or bool(profile.get("hd")))
    if provider == "google" and not verified:
        raise HTTPException(400, "Google has not verified this email address.")

    result = await db.execute(
        select(User).where(func.lower(User.email) == email).with_for_update().execution_options(populate_existing=True)
    )
    matches = result.scalars().all()
    if len(matches) > 1:
        raise HTTPException(409, "Multiple existing accounts use this email. Contact an administrator.")
    user = matches[0] if matches else None
    if user:
        if not user.is_active:
            raise HTTPException(403, "Account is disabled")
        if user.oauth_subject or user.oauth_provider not in (None, provider) or not authoritative:
            raise HTTPException(
                409,
                "An account already uses this email. Use its existing sign-in method or password recovery.",
            )
        # Local registrations never proved email ownership. Authoritative first
        # social sign-in must remove the pre-existing credential and every session.
        user.hashed_password = None
        revoke_user_sessions(user)
        user.oauth_provider = provider
        user.oauth_subject = subject
    else:
        user = User(
            email=email,
            hashed_password=None,
            full_name=profile.get("name"),
            role="editor",
            oauth_provider=provider,
            oauth_subject=subject,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    return user


@router.get("/google")
async def google_login(frontend_origin: str | None = Query(default=None)):
    """Return the Google OAuth2 authorization URL for the client to redirect to."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    origin = frontend_origin if _is_allowed_frontend_origin(frontend_origin) else settings.frontend_url
    return {
        "authorization_url": settings.google_redirect_uri.removesuffix("/callback")
        + "/start?"
        + urlencode({"frontend_origin": origin})
    }


@router.get("/google/start")
async def google_start(frontend_origin: str | None = Query(default=None)):
    if not settings.google_client_id:
        raise HTTPException(501, "Google OAuth is not configured")
    origin = (
        frontend_origin.rstrip("/")
        if _is_allowed_frontend_origin(frontend_origin)
        else settings.frontend_url.rstrip("/")
    )
    state, binding = await issue_state("google", origin)
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state,
    }
    authorization_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return bind_browser(RedirectResponse(authorization_url, status_code=302), "google", binding)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle the Google OAuth2 callback: exchange code for tokens, find or create user, return JWT."""
    # Verify before error handling, provider exchange or database lookup. The
    # redirect origin comes from the issued record, never callback JSON.
    frontend_origin = await consume_state(request, "google", state)

    if error:
        reason = error_description or error
        logger.warning("Google OAuth callback returned provider error: %s", reason)
        return _oauth_error_redirect(frontend_origin, f"Google OAuth error: {reason}")

    if not code:
        logger.warning("Google OAuth callback missing authorization code")
        return _oauth_error_redirect(frontend_origin, "Google OAuth callback missing authorization code")

    if not settings.google_client_id or not settings.google_client_secret:
        return _oauth_error_redirect(frontend_origin, "Google OAuth is not configured on the backend")

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            provider_reason = None
            try:
                token_error = token_response.json()
                if isinstance(token_error, dict):
                    provider_reason = token_error.get("error_description") or token_error.get("error")
            except Exception:
                provider_reason = None
            reason = provider_reason or token_response.text[:220] or f"HTTP {token_response.status_code}"
            logger.warning(
                "Google token exchange failed (%s): %s",
                token_response.status_code,
                reason,
            )
            return _oauth_error_redirect(frontend_origin, f"Google token exchange failed: {reason}")

        token_data = token_response.json()
        google_access_token = token_data.get("access_token")

        if not google_access_token:
            logger.warning("Google token exchange returned no access_token")
            return _oauth_error_redirect(frontend_origin, "No access token received from Google")

        # Fetch user info from Google
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
        )

        if userinfo_response.status_code != 200:
            provider_reason = None
            try:
                userinfo_error = userinfo_response.json()
                if isinstance(userinfo_error, dict):
                    error_obj = userinfo_error.get("error")
                    if isinstance(error_obj, dict):
                        provider_reason = error_obj.get("message")
            except Exception:
                provider_reason = None
            reason = provider_reason or userinfo_response.text[:220] or f"HTTP {userinfo_response.status_code}"
            logger.warning(
                "Google userinfo fetch failed (%s): %s",
                userinfo_response.status_code,
                reason,
            )
            return _oauth_error_redirect(frontend_origin, f"Failed to fetch Google user profile: {reason}")

        userinfo = userinfo_response.json()

    try:
        user = await _resolve_oauth_user(db, "google", userinfo)
    except HTTPException as exc:
        return _oauth_error_redirect(frontend_origin, str(exc.detail))

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # Generate JWT tokens
    access_token, refresh_token = await issue_session_tokens(user, db)

    # Redirect to frontend with tokens as query params
    redirect_params = urlencode(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    return RedirectResponse(
        url=f"{frontend_origin}/oauth/callback?{redirect_params}",
        status_code=302,
    )


# =============================================================================
# Microsoft OAuth2
# =============================================================================

MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/oidc/userinfo"


@router.get("/microsoft")
async def microsoft_login(frontend_origin: str | None = Query(default=None)):
    """Return the Microsoft OAuth2 authorization URL for the client to redirect to."""
    if not settings.microsoft_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Microsoft OAuth is not configured",
        )

    origin = frontend_origin if _is_allowed_frontend_origin(frontend_origin) else settings.frontend_url
    return {
        "authorization_url": settings.microsoft_redirect_uri.removesuffix("/callback")
        + "/start?"
        + urlencode({"frontend_origin": origin})
    }


@router.get("/microsoft/start")
async def microsoft_start(frontend_origin: str | None = Query(default=None)):
    if not settings.microsoft_client_id:
        raise HTTPException(501, "Microsoft OAuth is not configured")
    origin = (
        frontend_origin.rstrip("/")
        if _is_allowed_frontend_origin(frontend_origin)
        else settings.frontend_url.rstrip("/")
    )
    state, binding = await issue_state("microsoft", origin)
    params = {
        "client_id": settings.microsoft_client_id,
        "redirect_uri": settings.microsoft_redirect_uri,
        "response_type": "code",
        "scope": "openid profile email User.Read",
        "response_mode": "query",
        "prompt": "select_account",
        "state": state,
    }
    authorization_url = f"{MICROSOFT_AUTH_URL}?{urlencode(params)}"
    return bind_browser(RedirectResponse(authorization_url, status_code=302), "microsoft", binding)


@router.get("/microsoft/callback")
async def microsoft_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle the Microsoft OAuth2 callback: exchange code for tokens, find or create user, return JWT."""
    frontend_origin = await consume_state(request, "microsoft", state)
    if error or not code:
        return _oauth_error_redirect(
            frontend_origin,
            "Microsoft sign-in was cancelled or did not return a code. Start sign-in again.",
        )
    if not settings.microsoft_client_id or not settings.microsoft_client_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Microsoft OAuth is not configured",
        )

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            MICROSOFT_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.microsoft_client_id,
                "client_secret": settings.microsoft_client_secret,
                "redirect_uri": settings.microsoft_redirect_uri,
                "grant_type": "authorization_code",
                "scope": "openid profile email User.Read",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code with Microsoft",
            )

        token_data = token_response.json()
        ms_access_token = token_data.get("access_token")

        if not ms_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Microsoft",
            )

        # Fetch user info from Microsoft Graph
        userinfo_response = await client.get(
            MICROSOFT_USERINFO_URL,
            headers={"Authorization": f"Bearer {ms_access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Microsoft",
            )

        userinfo = userinfo_response.json()

    try:
        user = await _resolve_oauth_user(db, "microsoft", userinfo)
    except HTTPException as exc:
        return _oauth_error_redirect(frontend_origin, str(exc.detail))

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # Generate JWT tokens
    access_token, refresh_token = await issue_session_tokens(user, db)

    # Redirect to frontend with tokens as query params
    redirect_params = urlencode(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    return RedirectResponse(
        url=f"{frontend_origin}/oauth/callback?{redirect_params}",
        status_code=302,
    )
