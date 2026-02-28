"""
Platform settings endpoints for cofounder-level configuration.
"""

import redis as redis_lib
from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.core.security import require_cofounder
from app.models.models import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
settings = get_settings()


class PlatformSettingsResponse(BaseModel):
    """Current platform settings for the cofounder dashboard."""
    layout_ai_provider: str
    claude_configured: bool
    gemini_configured: bool


class PlatformSettingsUpdate(BaseModel):
    """Update platform settings."""
    layout_ai_provider: Optional[str] = None


@router.get("/platform-settings", response_model=PlatformSettingsResponse)
async def get_platform_settings(
    user: User = Depends(require_cofounder),
):
    """Get current platform settings (cofounder only)."""
    # Check Redis for runtime override
    current_provider = settings.layout_ai_provider
    try:
        r = redis_lib.from_url(settings.redis_url, decode_responses=True)
        override = r.get("layout_ai_provider")
        if override:
            current_provider = override
    except Exception:
        pass

    return PlatformSettingsResponse(
        layout_ai_provider=current_provider,
        claude_configured=bool(settings.anthropic_api_key),
        gemini_configured=bool(settings.gemini_api_key),
    )


@router.put("/platform-settings", response_model=PlatformSettingsResponse)
async def update_platform_settings(
    update: PlatformSettingsUpdate,
    user: User = Depends(require_cofounder),
):
    """Update platform settings at runtime (cofounder only).

    Uses Redis for runtime toggle so no restart is needed.
    """
    current_provider = settings.layout_ai_provider

    if update.layout_ai_provider:
        if update.layout_ai_provider not in ("claude", "gemini", "algorithmic"):
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="layout_ai_provider must be 'claude', 'gemini', or 'algorithmic'",
            )
        try:
            r = redis_lib.from_url(settings.redis_url, decode_responses=True)
            r.set("layout_ai_provider", update.layout_ai_provider)
            current_provider = update.layout_ai_provider
        except Exception:
            # If Redis is unavailable, the setting won't persist across requests
            current_provider = update.layout_ai_provider

    return PlatformSettingsResponse(
        layout_ai_provider=current_provider,
        claude_configured=bool(settings.anthropic_api_key),
        gemini_configured=bool(settings.gemini_api_key),
    )
