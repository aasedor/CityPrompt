"""
OAuth2 social login endpoints for Google and Microsoft.
"""

import base64
import json
import logging
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.models import User

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# =============================================================================
# Google OAuth2
# =============================================================================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def _allowed_frontend_origins() -> set[str]:
    allowed = {settings.frontend_url.rstrip("/")}
    allowed.update(origin.rstrip("/") for origin in settings.cors_origins if origin)
    return {origin for origin in allowed if origin}


def _is_allowed_frontend_origin(frontend_origin: str | None) -> bool:
    if not frontend_origin:
        return False
    normalized = frontend_origin.rstrip("/")
    return normalized in _allowed_frontend_origins()


def _build_oauth_state(frontend_origin: str | None) -> str:
    payload = {"csrf": secrets.token_urlsafe(32)}
    if _is_allowed_frontend_origin(frontend_origin):
        payload["frontend_origin"] = frontend_origin.rstrip("/")
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).decode("utf-8")


def _resolve_frontend_redirect_origin(state: str | None) -> str:
    fallback = settings.frontend_url.rstrip("/")
    if not state:
        return fallback

    try:
        padded = state + "=" * (-len(state) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        payload = json.loads(decoded)
    except Exception:
        return fallback

    frontend_origin = payload.get("frontend_origin")
    if isinstance(frontend_origin, str) and _is_allowed_frontend_origin(frontend_origin):
        return frontend_origin.rstrip("/")
    return fallback


def _oauth_error_redirect(frontend_origin: str, message: str) -> RedirectResponse:
    params = urlencode({"oauth_error": message})
    return RedirectResponse(url=f"{frontend_origin}/oauth/callback?{params}", status_code=302)


@router.get("/google")
async def google_login(frontend_origin: str | None = Query(default=None)):
    """Return the Google OAuth2 authorization URL for the client to redirect to."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": _build_oauth_state(frontend_origin),
    }
    authorization_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"authorization_url": authorization_url}


@router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle the Google OAuth2 callback: exchange code for tokens, find or create user, return JWT."""
    frontend_origin = _resolve_frontend_redirect_origin(state)

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
            logger.warning("Google token exchange failed (%s): %s", token_response.status_code, reason)
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
            logger.warning("Google userinfo fetch failed (%s): %s", userinfo_response.status_code, reason)
            return _oauth_error_redirect(frontend_origin, f"Failed to fetch Google user profile: {reason}")

        userinfo = userinfo_response.json()

    email = userinfo.get("email")
    if not email:
        return _oauth_error_redirect(frontend_origin, "Google account does not have an email address")

    full_name = userinfo.get("name")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            hashed_password=None,
            full_name=full_name,
            role="editor",
            oauth_provider="google",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # Update OAuth provider if not set (linking existing account)
        if not user.oauth_provider:
            user.oauth_provider = "google"
            await db.flush()

    if not user.is_active:
        return _oauth_error_redirect(frontend_origin, "Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # Generate JWT tokens
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

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
MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"


@router.get("/microsoft")
async def microsoft_login(frontend_origin: str | None = Query(default=None)):
    """Return the Microsoft OAuth2 authorization URL for the client to redirect to."""
    if not settings.microsoft_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Microsoft OAuth is not configured",
        )

    params = {
        "client_id": settings.microsoft_client_id,
        "redirect_uri": settings.microsoft_redirect_uri,
        "response_type": "code",
        "scope": "openid profile email User.Read",
        "response_mode": "query",
        "prompt": "select_account",
        "state": _build_oauth_state(frontend_origin),
    }
    authorization_url = f"{MICROSOFT_AUTH_URL}?{urlencode(params)}"
    return {"authorization_url": authorization_url}


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str,
    state: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle the Microsoft OAuth2 callback: exchange code for tokens, find or create user, return JWT."""
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

    # Microsoft Graph returns email in 'mail' or 'userPrincipalName'
    email = userinfo.get("mail") or userinfo.get("userPrincipalName")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft account does not have an email address",
        )

    full_name = userinfo.get("displayName")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            hashed_password=None,
            full_name=full_name,
            role="editor",
            oauth_provider="microsoft",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # Update OAuth provider if not set (linking existing account)
        if not user.oauth_provider:
            user.oauth_provider = "microsoft"
            await db.flush()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # Generate JWT tokens
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

    # Redirect to frontend with tokens as query params
    frontend_origin = _resolve_frontend_redirect_origin(state)
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
