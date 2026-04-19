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
import os
import uuid as _uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from PIL import Image, ImageEnhance
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import require_auth, check_project_permission, is_admin_or_above
from app.models.models import User
from app.models.models import Project, User

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Gemini model for render pipeline — must support image generation
# (responseModalities: ["TEXT", "IMAGE"])
_GEMINI_RENDER_MODEL = "gemini-3.1-flash-image-preview"


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ArchetypeImage(BaseModel):
    """An archetype reference image to include in the multi-image payload."""
    image_base64: str = Field(..., description="Base64-encoded JPEG/PNG of the archetype card.")
    label: str = Field(..., description="Label for this archetype (e.g., 'Glass Office Tower').")
    zone_color: Optional[str] = Field(default=None, description="Color identifier in the layout (e.g., 'red').")


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
    model: Optional[str] = Field(
        default=None,
        description="Gemini model ID to use. Defaults to gemini-2.5-flash-image.",
    )
    archetype_images: Optional[list[ArchetypeImage]] = Field(
        default=None,
        description="Archetype card photos for multi-image composition routing.",
    )
    previous_render_base64: Optional[str] = Field(
        default=None,
        description="Previous render for dual anchoring (iterative refinement).",
    )
    thinking_budget: Optional[int] = Field(
        default=None,
        ge=0,
        le=32768,
        description="Gemini thinking budget tokens for complex spatial reasoning",
    )
    image_size: Optional[str] = Field(
        default=None,
        pattern=r"^(512|1K|2K|4K)$",
        description="Output image resolution: 512, 1K, 2K, or 4K. Model-dependent.",
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


def _describe_google_auth_failure(exc: Exception, settings) -> str:
    """Return a human-readable description of a Google auth / Vertex AI failure."""
    from google.auth.exceptions import DefaultCredentialsError, TransportError

    suffix = ""
    if getattr(settings, "app_debug", False):
        suffix = f" [{type(exc).__name__}: {exc}]"

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

    if isinstance(exc, DefaultCredentialsError):
        if not creds_path:
            return (
                "Google credentials are not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file."
                + suffix
            )
        if not Path(creds_path).exists():
            return (
                f"Credentials file was not found at {creds_path}. "
                "Check that the path is correct and the file exists."
                + suffix
            )
        return (
            f"Credentials file at {creds_path} could not be loaded. "
            "Ensure it contains valid service-account JSON."
            + suffix
        )

    if isinstance(exc, TransportError):
        return (
            "The server could not reach Google's token service "
            "(oauth2.googleapis.com). Check network / firewall settings."
            + suffix
        )

    if isinstance(exc, RuntimeError) and "403" in str(exc):
        return (
            "Google rejected the token request (403). "
            "Verify that the Vertex AI API is enabled on the project "
            "and the service account has the correct IAM roles."
            + suffix
        )

    return f"Google auth failed: {exc}" + suffix


async def _save_render_audit(
    db: AsyncSession,
    user,
    render_model: str,
    token_cost: int,
    input_b64: str | None,
    output_b64: str | None,
    prompt_preview: str | None = None,
):
    """Save input/output images to S3 and create an audit log row."""
    import boto3
    from botocore.config import Config as BotoConfig

    settings = get_settings()
    audit_id = _uuid.uuid4()

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=BotoConfig(signature_version="s3v4"),
    )

    bucket = settings.s3_bucket_name
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)

    input_key = None
    output_key = None

    if input_b64:
        input_key = f"render-audit/{audit_id}/input.png"
        s3.put_object(Bucket=bucket, Key=input_key, Body=base64.b64decode(input_b64), ContentType="image/png")

    if output_b64:
        output_key = f"render-audit/{audit_id}/output.png"
        s3.put_object(Bucket=bucket, Key=output_key, Body=base64.b64decode(output_b64), ContentType="image/png")

    from app.models.models import RenderAuditLog
    log = RenderAuditLog(
        id=audit_id,
        user_id=user.id,
        user_email=user.email,
        model=render_model,
        tokens_spent=token_cost,
        input_image_key=input_key,
        output_image_key=output_key,
        prompt_preview=prompt_preview,
    )
    db.add(log)
    await db.commit()
    logger.info("Render audit saved: %s for %s", audit_id, user.email)


_ALLOWED_MODELS = {
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
}

# Token cost per render by model ($5 = 1000 tokens, 1 token = $0.005)
_MODEL_TOKEN_COST: dict[str, int] = {
    "gemini-2.5-flash-image": 8,        # ~$0.039
    "gemini-3.1-flash-image-preview": 13, # ~$0.067
    "gemini-3-pro-image-preview": 27,     # ~$0.134
}
_DEFAULT_TOKEN_COST = 13  # fallback
_WEEKLY_TOKEN_ALLOWANCE = 99999


def _build_gemini_url(settings, model: str | None = None) -> str:
    """Build the Gemini API URL.

    If GEMINI_API_KEY is set, use the public generativelanguage.googleapis.com
    endpoint (simpler, no Vertex AI setup needed).
    Otherwise fall back to Vertex AI endpoint.
    """
    render_model = model if model and model in _ALLOWED_MODELS else _GEMINI_RENDER_MODEL
    if settings.gemini_api_key:
        return (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{render_model}:generateContent"
            f"?key={settings.gemini_api_key}"
        )
    else:
        # Vertex AI path — requires Generative AI API enabled on project
        location = "us-central1"
        return (
            f"https://{location}-aiplatform.googleapis.com/v1/"
            f"projects/{settings.vertex_ai_project}/"
            f"locations/{location}/"
            f"publishers/google/models/{render_model}:generateContent"
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
async def generate_render(
    req: RenderRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate a photorealistic architectural render via Gemini.

    Sends the map screenshot + prompt to Gemini's generateContent API
    with responseModalities: ["TEXT", "IMAGE"] to get an edited image back.
    Requires authentication. Non-admin users must have render tokens.
    """
    # Weekly token reset for non-admin users
    if not is_admin_or_above(user):
        now = datetime.now(timezone.utc)
        if user.credits_reset_at is None or (now - user.credits_reset_at).days >= 7:
            user.render_credits = _WEEKLY_TOKEN_ALLOWANCE
            user.credits_reset_at = now
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info("Weekly token reset for %s — %d tokens", user.email, user.render_credits)

    # Calculate cost for this render
    render_model = req.model if req.model and req.model in _ALLOWED_MODELS else _GEMINI_RENDER_MODEL
    token_cost = _MODEL_TOKEN_COST.get(render_model, _DEFAULT_TOKEN_COST)

    # Check render tokens for non-admin users
    if not is_admin_or_above(user) and user.render_credits < token_cost:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough tokens. This render costs {token_cost} tokens but you have {user.render_credits}. Tokens reset weekly.",
        )

    settings = get_settings()

    if not settings.gemini_api_key and not settings.vertex_ai_project:
        raise HTTPException(
            status_code=503,
            detail="Gemini is not configured. Set GEMINI_API_KEY in .env "
            "(get one free at https://aistudio.google.com/apikey).",
        )

    # --- Build payload ---
    parts: list[dict] = []

    # For dual anchoring: previous render goes first as structural anchor
    if req.previous_render_base64:
        parts.append({
            "text": "Image 1 (STRUCTURAL ANCHOR): This is a previously generated render. "
                    "Preserve its EXACT spatial layout, geometric volumes, camera angle, and "
                    "proportions. Only modify the specific elements described in the prompt."
        })
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": req.previous_render_base64,
            }
        })

    # Add the primary layout image (clay render or screenshot)
    if req.image_base64:
        img_index = 2 if req.previous_render_base64 else 1
        parts.append({
            "text": f"Image {img_index} (SPATIAL LAYOUT): This is a 3D clay massing model "
                    f"showing the exact spatial arrangement of all structures from the camera's "
                    f"perspective. Use this as the definitive spatial reference."
        })
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": req.image_base64,
            }
        })

    # Add archetype reference images for multi-image composition.
    # Cap raised from 6 → 48 to support multi-view refs (street-level +
    # 30°/60°/90° aerials per zone). Each ref is ~30-50KB compressed JPEG,
    # so 48 at ~40KB = ~2MB, well within Gemini's ~20MB request limit.
    # The prompt's "ARCHETYPE REFERENCE IMAGES" section now explains which
    # angle each ref is taken from, so the label already carries the angle.
    if req.archetype_images:
        base_index = 3 if req.previous_render_base64 else 2
        for i, arch_img in enumerate(req.archetype_images[:48]):  # Max 48 archetype refs
            img_idx = base_index + i
            color_ref = f" Located in the {arch_img.zone_color} zone." if arch_img.zone_color else ""
            parts.append({
                "text": f"Image {img_idx} (ARCHETYPE REFERENCE — {arch_img.label}): "
                        f"Apply the exact architectural style, materials, and textures from "
                        f"this reference image to the corresponding zone.{color_ref}"
            })
            # Detect mime type from base64 header or default to jpeg
            mime = "image/jpeg"
            if arch_img.image_base64[:4] == "iVBO":
                mime = "image/png"
            parts.append({
                "inlineData": {
                    "mimeType": mime,
                    "data": arch_img.image_base64,
                }
            })

    # If a mask is provided, send it as an additional image with explanation
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

    gen_config = {
        "responseModalities": ["TEXT", "IMAGE"],
        "temperature": temperature,
    }

    # Add image size for models that support higher resolution
    _HIRES_MODELS = {"gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview"}
    image_size = req.image_size
    if image_size is None and render_model in _HIRES_MODELS:
        image_size = "2K"  # Default to 2K for supported models
    if image_size and render_model in _HIRES_MODELS:
        gen_config["imageConfig"] = {"imageSize": image_size}

    # Add thinking budget for complex scenes (only models that support it)
    _THINKING_MODELS = {"gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview"}
    if render_model in _THINKING_MODELS:
        thinking = req.thinking_budget
        if thinking is None and len(req.prompt) > 1000:
            thinking = 8192
        if thinking is not None and thinking > 0:
            gen_config["thinkingConfig"] = {"thinkingBudget": thinking}

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": gen_config,
    }

    # --- Logging ---
    auth_mode = "API key" if settings.gemini_api_key else "Vertex AI"
    logger.info(
        "Render request — model=%s, auth=%s, prompt_length=%d, has_mask=%s, "
        "temperature=%.2f, imageSize=%s",
        req.model or _GEMINI_RENDER_MODEL,
        auth_mode,
        len(req.prompt),
        bool(req.mask_base64),
        temperature,
        gen_config.get("imageConfig", {}).get("imageSize", "default"),
    )
    logger.debug("Final prompt:\n%s", prompt_text)

    # --- Call Gemini ---
    try:
        url = _build_gemini_url(settings, model=req.model)
        headers = _get_auth_headers(settings)
    except Exception as exc:
        logger.exception("Failed to prepare Gemini request: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Auth error: {exc}",
        ) from exc

    logger.info("Calling Gemini — %s", auth_mode)

    async with httpx.AsyncClient(timeout=300.0) as client:
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

        # Deduct tokens for non-admin users
        if not is_admin_or_above(user):
            user.render_credits = max(0, user.render_credits - token_cost)
            db.add(user)
            await db.commit()
            logger.info("User %s: %d tokens deducted (%s) — %d remaining", user.email, token_cost, render_model, user.render_credits)

        # Save audit log with input/output images to S3
        try:
            await _save_render_audit(
                db=db,
                user=user,
                render_model=render_model,
                token_cost=token_cost if not is_admin_or_above(user) else 0,
                input_b64=req.image_base64,
                output_b64=image_b64,
                prompt_preview=req.prompt[:500] if req.prompt else None,
            )
        except Exception as audit_exc:
            logger.warning("Failed to save render audit log: %s", audit_exc)

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


# ---------------------------------------------------------------------------
# Saved renders (gallery)
# ---------------------------------------------------------------------------

class SaveRenderRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded PNG of the render.")
    prompt: str = Field(..., description="Prompt used for the render.")
    style: Optional[str] = Field(default=None, description="Style preset name.")
    seed: Optional[int] = Field(default=None, description="Seed used for generation.")


class SavedRenderResponse(BaseModel):
    id: str
    image_url: str
    prompt: str
    style: Optional[str] = None
    seed: Optional[int] = None
    created_at: str


@router.post("/projects/{project_id}/save", response_model=SavedRenderResponse, status_code=status.HTTP_201_CREATED)
async def save_render(
    project_id: _uuid.UUID,
    req: SaveRenderRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save an AI render image to the project's gallery in S3."""
    await check_project_permission(project_id, user, db, required="editor")

    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        image_bytes = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    render_id = str(_uuid.uuid4())
    file_key = f"projects/{project_id}/renders/{render_id}.png"

    from app.api.v1.documents import _upload_to_storage
    await _upload_to_storage(file_key, image_bytes, "image/png")

    image_url = f"/api/v1/files/{file_key}"
    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "id": render_id,
        "image_url": image_url,
        "prompt": req.prompt,
        "style": req.style,
        "seed": req.seed,
        "created_at": now,
    }

    meta = dict(project.metadata_) if project.metadata_ else {}
    renders = list(meta.get("saved_renders", []))
    renders.insert(0, entry)
    meta["saved_renders"] = renders
    project.metadata_ = meta

    await db.commit()
    logger.info("Saved render %s for project %s", render_id, project_id)

    return SavedRenderResponse(**entry)


@router.get("/projects/{project_id}/renders", response_model=list[SavedRenderResponse])
async def list_renders(
    project_id: _uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all saved renders for a project."""
    await check_project_permission(project_id, user, db, required="viewer")

    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_ or {}
    renders = meta.get("saved_renders", [])
    return [SavedRenderResponse(**r) for r in renders]


@router.delete("/projects/{project_id}/renders/{render_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_render(
    project_id: _uuid.UUID,
    render_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved render from the project."""
    await check_project_permission(project_id, user, db, required="editor")

    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = dict(project.metadata_) if project.metadata_ else {}
    renders = list(meta.get("saved_renders", []))
    meta["saved_renders"] = [r for r in renders if r.get("id") != render_id]
    project.metadata_ = meta

    await db.commit()
