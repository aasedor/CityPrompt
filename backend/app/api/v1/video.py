"""
Video generation endpoint — uses Google Veo for architectural flythrough videos.

The frontend sends a base64-encoded aerial render (first frame) and optionally
a second render (last frame) with a camera motion prompt. This endpoint submits
the request to Veo 3.1 Fast asynchronously and provides a polling endpoint.
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import require_auth, is_admin_or_above
from app.models.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Camera motion prompt templates
# ---------------------------------------------------------------------------

CAMERA_MOTION_PROMPTS: dict[str, str] = {
    "tracking_forward": (
        "Slow cinematic tracking shot moving forward, camera gradually descending "
        "toward the architectural site, smooth dolly movement, professional drone footage"
    ),
    "tracking_backward": (
        "Camera slowly pulling back and rising to reveal the full architectural site plan "
        "from above, smooth ascending dolly-out movement, professional drone footage"
    ),
    "orbit_left": (
        "Smooth orbital camera movement rotating counter-clockwise around the site center, "
        "maintaining consistent altitude and distance, cinematic aerial rotation"
    ),
    "orbit_right": (
        "Smooth orbital camera movement rotating clockwise around the site center, "
        "maintaining consistent altitude and distance, cinematic aerial rotation"
    ),
    "crane_up": (
        "Camera rising vertically upward from close aerial view, gradually revealing "
        "more of the surrounding urban context, smooth vertical crane movement"
    ),
    "static_life": (
        "Static aerial camera position, gentle wind rustling through trees, "
        "moving clouds casting soft shadows, pedestrians walking on sidewalks, "
        "cars moving slowly on streets, subtle life and activity throughout the scene"
    ),
}

# Token cost for video generation
_VIDEO_TOKEN_COST = 50

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class VideoRequest(BaseModel):
    """Payload for video generation."""
    first_frame_base64: str = Field(
        ...,
        description="Base64-encoded PNG/JPEG of the first frame (existing aerial render).",
    )
    last_frame_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded PNG/JPEG of the last frame (shifted camera render).",
    )
    prompt: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="Custom prompt override. If omitted, camera_motion template is used.",
    )
    camera_motion: str = Field(
        default="tracking_forward",
        description="Camera motion preset: tracking_forward, tracking_backward, orbit_left, orbit_right, crane_up, static_life",
    )
    duration_seconds: int = Field(
        default=8,
        description="Video duration in seconds (4, 6, or 8).",
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Project ID for audit logging.",
    )


class VideoStartResponse(BaseModel):
    """Returned when video generation starts."""
    operation_name: str = Field(..., description="Async operation name for polling.")
    estimated_seconds: int = Field(default=60, description="Estimated generation time.")


class VideoStatusResponse(BaseModel):
    """Returned when polling video status."""
    status: str = Field(..., description="'processing', 'complete', or 'failed'.")
    video_base64: Optional[str] = Field(default=None, description="Base64-encoded MP4 when complete.")
    error: Optional[str] = Field(default=None, description="Error message if failed.")


# ---------------------------------------------------------------------------
# In-memory operation store (local prototype — no DB persistence)
# ---------------------------------------------------------------------------

# Maps operation_name → { "genai_op": <operation>, "user_id": int, "started_at": float }
_operations: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=VideoStartResponse)
async def generate_video(
    req: VideoRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Start async video generation from aerial render frame(s)."""
    settings = get_settings()

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY not configured — video generation unavailable.",
        )

    # Check token balance
    if not is_admin_or_above(user) and user.render_credits < _VIDEO_TOKEN_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. Video costs {_VIDEO_TOKEN_COST} tokens, you have {user.render_credits}.",
        )

    # Validate duration
    if req.duration_seconds not in (4, 6, 8):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="duration_seconds must be 4, 6, or 8.",
        )

    # Build the prompt
    base_prompt = req.prompt or CAMERA_MOTION_PROMPTS.get(
        req.camera_motion, CAMERA_MOTION_PROMPTS["tracking_forward"]
    )
    full_prompt = (
        f"{base_prompt}. Photorealistic architectural visualization, "
        f"8K quality, golden hour lighting, smooth camera movement."
    )

    logger.info(
        "[Video] Starting generation for %s — motion: %s, duration: %ds, prompt: %d chars",
        user.email, req.camera_motion, req.duration_seconds, len(full_prompt),
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        # Decode first frame
        first_frame_bytes = base64.b64decode(req.first_frame_base64)
        first_frame_image = types.Image(image_bytes=first_frame_bytes, mime_type="image/png")

        # Build config
        video_config = types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=req.duration_seconds,
            aspect_ratio="16:9",
        )

        # Build generate_videos kwargs
        gen_kwargs: dict = {
            "model": settings.veo_model,
            "prompt": full_prompt,
            "image": first_frame_image,
            "config": video_config,
        }

        # Add last frame if provided (Veo 3.1 first/last frame conditioning)
        if req.last_frame_base64:
            last_frame_bytes = base64.b64decode(req.last_frame_base64)
            last_frame_image = types.Image(image_bytes=last_frame_bytes, mime_type="image/png")
            gen_kwargs["end_image"] = last_frame_image
            logger.info("[Video] Using first + last frame conditioning")

        # Start async generation
        operation = client.models.generate_videos(**gen_kwargs)

        op_name = operation.name or f"video-op-{int(time.time())}"
        _operations[op_name] = {
            "genai_op": operation,
            "client": client,
            "user_id": user.id,
            "started_at": time.time(),
        }

        logger.info("[Video] Operation started: %s", op_name)

        return VideoStartResponse(
            operation_name=op_name,
            estimated_seconds=60 if req.duration_seconds == 8 else 40,
        )

    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="google-genai SDK not installed. Run: pip install google-genai",
        )
    except Exception as exc:
        logger.error("[Video] Failed to start generation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Veo API error: {exc}",
        )


@router.get("/status/{operation_name:path}", response_model=VideoStatusResponse)
async def check_video_status(
    operation_name: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Poll video generation status."""
    op_data = _operations.get(operation_name)
    if not op_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {operation_name} not found. It may have expired.",
        )

    # Security: only the user who started it can poll
    if op_data["user_id"] != user.id and not is_admin_or_above(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your operation.")

    try:
        client = op_data["client"]
        operation = client.operations.get(op_data["genai_op"])
        op_data["genai_op"] = operation  # update cached state

        elapsed = int(time.time() - op_data["started_at"])
        logger.info("[Video] Polling %s — done: %s, elapsed: %ds", operation_name, operation.done, elapsed)

        if not operation.done:
            return VideoStatusResponse(status="processing")

        # Generation complete — extract video
        if operation.response and operation.response.generated_videos:
            video = operation.response.generated_videos[0].video
            if hasattr(video, 'video_bytes') and video.video_bytes:
                video_b64 = base64.b64encode(video.video_bytes).decode()
            else:
                # Try to read from the video object
                video_b64 = base64.b64encode(video.read()).decode() if hasattr(video, 'read') else None

            if not video_b64:
                logger.error("[Video] Operation complete but no video bytes returned")
                _operations.pop(operation_name, None)
                return VideoStatusResponse(status="failed", error="No video data in response.")

            # Deduct tokens
            if not is_admin_or_above(user):
                user.render_credits = max(0, user.render_credits - _VIDEO_TOKEN_COST)
                db.add(user)
                await db.commit()
                logger.info(
                    "[Video] User %s: %d tokens deducted — %d remaining",
                    user.email, _VIDEO_TOKEN_COST, user.render_credits,
                )

            logger.info("[Video] Complete: %s — video size: %d chars base64", operation_name, len(video_b64))

            # Cleanup
            _operations.pop(operation_name, None)

            return VideoStatusResponse(status="complete", video_base64=video_b64)
        else:
            logger.error("[Video] Operation done but no generated_videos in response")
            _operations.pop(operation_name, None)
            return VideoStatusResponse(status="failed", error="Veo returned no video. Safety filter may have blocked generation.")

    except Exception as exc:
        logger.error("[Video] Status check failed: %s", exc)
        _operations.pop(operation_name, None)
        return VideoStatusResponse(status="failed", error=str(exc))
