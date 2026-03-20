"""
AI Render endpoint — proxies Vertex AI Imagen 3 for architectural rendering.

The frontend sends a base64-encoded map screenshot with colored zone overlays
and a structured prompt. This endpoint forwards the request to the Vertex AI
Imagen 3 editing API and returns the rendered image as base64.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class RenderRequest(BaseModel):
    """Payload sent by the frontend useAIRender hook."""

    image_base64: str = Field(
        ...,
        description="Base64-encoded PNG screenshot of the map with colored zone overlays.",
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Structured prompt (3-block orchestration format).",
    )
    aspect_ratio: str = Field(
        default="4:3",
        description="Output aspect ratio (e.g. '4:3', '16:9', '1:1').",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility.",
    )


class RenderResponse(BaseModel):
    image_base64: str = Field(
        ...,
        description="Base64-encoded PNG of the rendered image.",
    )
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Vertex AI helpers
# ---------------------------------------------------------------------------

_VERTEX_AI_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _get_access_token() -> str:
    """Obtain an access token from Application Default Credentials.

    Reads from the GOOGLE_APPLICATION_CREDENTIALS env var (service-account JSON)
    or falls back to the gcloud CLI / metadata server.
    """
    import google.auth
    import google.auth.transport.requests

    credentials, _project = google.auth.default(scopes=_VERTEX_AI_SCOPES)
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


def _build_vertex_url(settings) -> str:
    """Build the Vertex AI prediction URL for the configured Imagen model."""
    return (
        f"https://{settings.vertex_ai_location}-aiplatform.googleapis.com/v1/"
        f"projects/{settings.vertex_ai_project}/"
        f"locations/{settings.vertex_ai_location}/"
        f"publishers/google/models/{settings.vertex_ai_imagen_model}:predict"
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=RenderResponse)
async def generate_render(req: RenderRequest):
    """Generate a photorealistic architectural render via Vertex AI Imagen 3.

    Accepts a base64 map screenshot with colored zone overlays and a structured
    prompt, sends it to Imagen 3 for inpaint-insertion editing, and returns the
    rendered image as base64.
    """
    settings = get_settings()

    if not settings.vertex_ai_project:
        raise HTTPException(
            status_code=503,
            detail="Vertex AI is not configured. Set VERTEX_AI_PROJECT in .env.",
        )

    # --- Build Vertex AI payload (matches the Imagen 3 editing API) ---
    payload = {
        "instances": [
            {
                "prompt": req.prompt,
                "image": {"bytesBase64Encoded": req.image_base64},
            }
        ],
        "parameters": {
            "editConfig": {
                "editMode": "EDIT_MODE_INPAINT_INSERTION",
            },
            "aspectRatio": req.aspect_ratio,
            "sampleCount": 1,
        },
    }

    if req.seed is not None:
        payload["parameters"]["seed"] = req.seed

    # --- Call Vertex AI ---
    try:
        access_token = _get_access_token()
    except Exception as exc:
        logger.error("Failed to obtain Google Cloud credentials: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not authenticate with Google Cloud. "
                "Ensure GOOGLE_APPLICATION_CREDENTIALS is set and valid."
            ),
        ) from exc

    url = _build_vertex_url(settings)
    logger.info(
        "Calling Vertex AI Imagen 3 — model=%s, location=%s, prompt_length=%d",
        settings.vertex_ai_imagen_model,
        settings.vertex_ai_location,
        len(req.prompt),
    )

    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code != 200:
        error_body = resp.text[:500]
        logger.error(
            "Vertex AI returned %d: %s", resp.status_code, error_body
        )
        raise HTTPException(
            status_code=502,
            detail=f"Vertex AI error ({resp.status_code}): {error_body}",
        )

    # --- Parse response ---
    try:
        body = resp.json()
        predictions = body.get("predictions", [])
        if not predictions:
            raise ValueError("No predictions in response")

        image_b64 = predictions[0].get("bytesBase64Encoded")
        if not image_b64:
            raise ValueError("No image data in prediction")

        return RenderResponse(
            image_base64=image_b64,
            seed=req.seed,
        )

    except (ValueError, KeyError, IndexError) as exc:
        logger.error("Failed to parse Vertex AI response: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Invalid Vertex AI response: {exc}",
        ) from exc
