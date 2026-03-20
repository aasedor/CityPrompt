"""
AI Render endpoint — proxies Vertex AI Imagen 3 for architectural rendering.

The frontend sends a base64-encoded map screenshot with colored zone overlays
and a structured prompt. This endpoint forwards the request to the Vertex AI
Imagen 3 editing API and returns the rendered image as base64.
"""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import Optional

import httpx
from PIL import Image, ImageEnhance
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
    mask_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded PNG binary mask (white=edit, black=keep).",
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Structured prompt (3-block orchestration format).",
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        max_length=10_000,
        description="Negative prompt — things to avoid in the render.",
    )
    aspect_ratio: str = Field(
        default="4:3",
        description="Output aspect ratio (e.g. '4:3', '16:9', '1:1').",
    )
    guidance_scale: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=30.0,
        description="Guidance scale for prompt adherence (1-30, higher = stricter).",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility.",
    )
    post_process: bool = Field(
        default=True,
        description="Apply post-processing (sharpening, contrast, color enhancement).",
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


def _describe_google_auth_failure(exc: Exception, settings) -> str:
    """Return a user-facing auth failure message with the most likely cause."""
    import os as _os

    credentials_path = (
        _os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or settings.google_application_credentials
        or ""
    )
    credentials_exists = bool(credentials_path) and Path(credentials_path).exists()
    exc_type_name = type(exc).__name__
    exc_text = str(exc).strip()
    exc_text_lower = exc_text.lower()

    if not credentials_path:
        detail = (
            "Google Cloud credentials are not configured. "
            "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file."
        )
    elif not credentials_exists:
        detail = (
            "Configured Google Cloud credentials file was not found: "
            f"{credentials_path}"
        )
    elif exc_type_name == "DefaultCredentialsError":
        detail = (
            "Google Cloud credentials file was found, but it could not be loaded "
            "as Application Default Credentials. Verify that it is a valid "
            "service-account JSON key."
        )
    elif exc_type_name == "TransportError":
        detail = (
            "Google Cloud credentials loaded, but the backend could not reach "
            "Google's token service. Check outbound HTTPS access to "
            "oauth2.googleapis.com and any firewall, proxy, VPN, or antivirus "
            "rules."
        )
    elif (
        "permission" in exc_text_lower
        or "forbidden" in exc_text_lower
        or "permission_denied" in exc_text_lower
        or "403" in exc_text_lower
    ):
        detail = (
            "Google Cloud credentials loaded, but Google rejected the token "
            "request. Check service-account permissions and confirm the Vertex AI "
            "and Service Usage APIs are enabled for the configured project."
        )
    else:
        detail = (
            "Could not authenticate with Google Cloud while requesting a Vertex AI "
            "access token."
        )

    if settings.app_debug or settings.app_env.lower() != "production":
        suffix = f" [{exc_type_name}"
        if exc_text:
            suffix += f": {exc_text}"
        suffix += "]"
        detail += suffix

    return detail


def _post_process(image_b64: str) -> str:
    """Apply subtle sharpening, contrast, and color enhancement to the rendered image."""
    raw = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img = ImageEnhance.Color(img).enhance(1.04)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


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

    # --- Build Vertex AI payload (Imagen 3 capability/editing API) ---
    reference_images = [
        {
            "referenceType": "REFERENCE_TYPE_RAW",
            "referenceId": 1,
            "referenceImage": {
                "bytesBase64Encoded": req.image_base64,
            },
        }
    ]

    # When a mask is provided, send it as REFERENCE_TYPE_MASK so Vertex AI
    # only paints inside the white pixels (strict inpainting).
    if req.mask_base64:
        reference_images.append(
            {
                "referenceType": "REFERENCE_TYPE_MASK",
                "referenceId": 2,
                "referenceImage": {
                    "bytesBase64Encoded": req.mask_base64,
                },
                "maskImageConfig": {
                    "maskMode": "MASK_MODE_USER_PROVIDED",
                    "dilation": 0.0,
                },
            }
        )

    payload = {
        "instances": [
            {
                "prompt": req.prompt,
                "referenceImages": reference_images,
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

    if req.negative_prompt:
        payload["parameters"]["negativePrompt"] = req.negative_prompt

    if req.guidance_scale is not None:
        payload["parameters"]["guidanceScale"] = req.guidance_scale

    # --- Observability logging ---
    logger.info(
        "Render request — prompt_length=%d, has_mask=%s, has_negative=%s, "
        "guidance_scale=%s, aspect_ratio=%s, seed=%s",
        len(req.prompt),
        bool(req.mask_base64),
        bool(req.negative_prompt),
        req.guidance_scale,
        req.aspect_ratio,
        req.seed,
    )
    logger.debug("Final prompt:\n%s", req.prompt)
    if req.negative_prompt:
        logger.debug("Negative prompt:\n%s", req.negative_prompt)

    # --- Call Vertex AI ---
    try:
        access_token = _get_access_token()
    except Exception as exc:
        logger.exception(
            "Failed to obtain Google Cloud credentials: %s (type: %s)",
            exc,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail=_describe_google_auth_failure(exc, settings),
        ) from exc

    url = _build_vertex_url(settings)
    logger.info(
        "Calling Vertex AI Imagen 3 — model=%s, location=%s",
        settings.vertex_ai_imagen_model,
        settings.vertex_ai_location,
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

        if req.post_process:
            image_b64 = _post_process(image_b64)

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
