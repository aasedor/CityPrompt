"""
AI Render endpoint — proxies Google Gemini for architectural rendering.

The frontend sends a base64-encoded map screenshot with colored zone overlays
and a natural-language prompt. This endpoint forwards the request to Gemini's
generateContent API (with image generation) and returns the rendered image.

Supports two auth modes:
  1. GEMINI_API_KEY — calls generativelanguage.googleapis.com directly (preferred)
  2. Vertex AI service account — calls Vertex AI endpoint (fallback)
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
# Config
# ---------------------------------------------------------------------------

# Gemini model for render pipeline — must support image generation
# (responseModalities: ["TEXT", "IMAGE"])
_GEMINI_RENDER_MODEL = "gemini-2.5-flash-image"


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class RenderRequest(BaseModel):
    """Payload sent by the frontend useAIRender hook."""

    image_base64: Optional[str] = Field(
        default=None,
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
        description="Natural-language prompt describing what to render.",
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        max_length=10_000,
        description="Negative prompt — things to avoid in the render.",
    )
    aspect_ratio: str = Field(
        default="4:3",
        description="Output aspect ratio (kept for compat).",
    )
    guidance_scale: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=30.0,
        description="Mapped to Gemini temperature (higher guidance = lower temp).",
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
# Helpers
# ---------------------------------------------------------------------------


def _post_process(image_b64: str) -> str:
    """Apply subtle sharpening, contrast, and color enhancement."""
    raw = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img = ImageEnhance.Color(img).enhance(1.04)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _build_gemini_url(settings) -> str:
    """Build the Gemini API URL.

    If GEMINI_API_KEY is set, use the public generativelanguage.googleapis.com
    endpoint (simpler, no Vertex AI setup needed).
    Otherwise fall back to Vertex AI endpoint.
    """
    if settings.gemini_api_key:
        return (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{_GEMINI_RENDER_MODEL}:generateContent"
            f"?key={settings.gemini_api_key}"
        )
    else:
        # Vertex AI path — requires Generative AI API enabled on project
        location = "us-central1"
        return (
            f"https://{location}-aiplatform.googleapis.com/v1/"
            f"projects/{settings.vertex_ai_project}/"
            f"locations/{location}/"
            f"publishers/google/models/{_GEMINI_RENDER_MODEL}:generateContent"
        )


def _get_auth_headers(settings) -> dict[str, str]:
    """Return authorization headers for the Gemini API call.

    If using API key (in URL), no auth header needed.
    If using Vertex AI, get a Bearer token from service account.
    """
    headers = {"Content-Type": "application/json"}

    if not settings.gemini_api_key:
        # Vertex AI — need Bearer token
        import google.auth
        import google.auth.transport.requests

        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        headers["Authorization"] = f"Bearer {credentials.token}"

    return headers


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=RenderResponse)
async def generate_render(req: RenderRequest):
    """Generate a photorealistic architectural render via Gemini.

    Sends the map screenshot + prompt to Gemini's generateContent API
    with responseModalities: ["TEXT", "IMAGE"] to get an edited image back.
    """
    settings = get_settings()

    if not settings.gemini_api_key and not settings.vertex_ai_project:
        raise HTTPException(
            status_code=503,
            detail="Gemini is not configured. Set GEMINI_API_KEY in .env "
            "(get one free at https://aistudio.google.com/apikey).",
        )

    # --- Build payload ---
    parts: list[dict] = []

    # Add the screenshot as inline image (if provided)
    if req.image_base64:
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": req.image_base64,
            }
        })

    # If a mask is provided, send it as a second image with explanation
    if req.image_base64 and req.mask_base64:
        parts.append({
            "text": "The following black-and-white mask shows the exact area to edit "
                    "(white = edit, black = keep unchanged):"
        })
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": req.mask_base64,
            }
        })

    # Build the final prompt text
    prompt_text = req.prompt
    if req.negative_prompt:
        prompt_text += f"\n\nDo NOT include: {req.negative_prompt}"

    parts.append({"text": prompt_text})

    # Map guidance_scale to temperature: high guidance = low temperature (strict)
    # For architectural editing, low temperature preserves unedited areas faithfully
    temperature = 0.0  # Default to 0 for maximum consistency in editing
    if req.guidance_scale is not None:
        temperature = max(0.0, min(1.5, 1.5 - (req.guidance_scale / 30) * 1.5))

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": temperature,
        },
    }

    # --- Logging ---
    auth_mode = "API key" if settings.gemini_api_key else "Vertex AI"
    logger.info(
        "Render request — model=%s, auth=%s, prompt_length=%d, has_mask=%s, "
        "temperature=%.2f",
        _GEMINI_RENDER_MODEL,
        auth_mode,
        len(req.prompt),
        bool(req.mask_base64),
        temperature,
    )
    logger.debug("Final prompt:\n%s", prompt_text)

    # --- Call Gemini ---
    try:
        url = _build_gemini_url(settings)
        headers = _get_auth_headers(settings)
    except Exception as exc:
        logger.exception("Failed to prepare Gemini request: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Auth error: {exc}",
        ) from exc

    logger.info("Calling Gemini — %s", auth_mode)

    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        error_body = resp.text[:500]
        logger.error("Gemini returned %d: %s", resp.status_code, error_body)
        raise HTTPException(
            status_code=502,
            detail=f"Gemini error ({resp.status_code}): {error_body}",
        )

    # --- Parse response ---
    try:
        body = resp.json()
        candidates = body.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates in Gemini response")

        content_parts = candidates[0].get("content", {}).get("parts", [])
        if not content_parts:
            raise ValueError("No parts in Gemini response")

        # Find the image part
        image_b64 = None
        text_response = None
        for part in content_parts:
            if "inlineData" in part:
                inline = part["inlineData"]
                if inline.get("mimeType", "").startswith("image/"):
                    image_b64 = inline["data"]
            elif "text" in part:
                text_response = part["text"]

        if not image_b64:
            logger.error(
                "No image in Gemini response. Text: %s, Parts: %d",
                text_response or "(none)",
                len(content_parts),
            )
            raise ValueError(
                f"No image in Gemini response. Model said: {text_response or '(no text)'}"
            )

        logger.info(
            "Gemini success — image size: %d chars, text: %s",
            len(image_b64),
            (text_response or "")[:100],
        )

        # Log dimensions
        try:
            if req.image_base64:
                input_img = Image.open(io.BytesIO(base64.b64decode(req.image_base64)))
                output_img = Image.open(io.BytesIO(base64.b64decode(image_b64)))
                logger.info(
                    "Dimensions — input: %s, output: %s, match: %s",
                    input_img.size,
                    output_img.size,
                    input_img.size == output_img.size,
                )
        except Exception as dim_exc:
            logger.warning("Could not compare dimensions: %s", dim_exc)

        if req.post_process:
            image_b64 = _post_process(image_b64)

        return RenderResponse(
            image_base64=image_b64,
            seed=req.seed,
        )

    except (ValueError, KeyError, IndexError) as exc:
        logger.error("Failed to parse Gemini response: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Invalid Gemini response: {exc}",
        ) from exc
