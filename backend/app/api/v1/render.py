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
import hashlib
import io
import logging
import os
import uuid as _uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

import httpx
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, PngImagePlugin
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.render_media import SavedRenderResponse
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    require_auth,
    check_project_permission,
    check_project_read_access,
    get_current_user,
    is_admin_or_above,
)
from app.models.models import Project, RenderAuditLog, User
from app.services.render_audit_images import put_image_with_thumbnail
from app.services.render_fidelity import append_render_preservation_lock

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Gemini model for render pipeline — must support image generation
# (responseModalities: ["TEXT", "IMAGE"])
# GA id since 2026-05-28; the -preview alias is deprecated (shutdown announced
# ~2026-06-25, still on a grace alias as of 2026-07-12).
_GEMINI_RENDER_MODEL = "gemini-3.1-flash-image"
_OPENAI_RENDER_MODEL = "gpt-image-2"


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ArchetypeImage(BaseModel):
    """An archetype reference image to include in the multi-image payload."""

    image_base64: str = Field(..., description="Base64-encoded JPEG/PNG of the archetype card.")
    label: str = Field(..., description="Label for this archetype (e.g., 'Glass Office Tower').")
    zone_color: Optional[str] = Field(default=None, description="Color identifier in the layout (e.g., 'red').")


class SiteContextAnchor(BaseModel):
    """Geodetic anchor for fetching real-world context (Street View / Places / satellite)."""

    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    heading: Optional[float] = Field(
        default=None,
        description="Camera compass heading in degrees (0=N, clockwise; any value, normalised "
        "server-side). When set, a forward-facing Street View plate at this heading "
        "is added as the distant-background reference.",
    )


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
        description="DEPRECATED — accepted for back-compat, ignored (was mapped to temperature).",
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
    image_quality: Optional[str] = Field(
        default="auto",
        pattern=r"^(auto|low|medium|high)$",
        description="OpenAI GPT Image quality: auto, low, medium, or high.",
    )
    project_id: Optional[_uuid.UUID] = Field(
        default=None,
        description="Project associated with this render for admin audit log linking.",
    )
    site_context: Optional[SiteContextAnchor] = Field(
        default=None,
        description=(
            "When set, real Street View photos, a satellite tile, and the current Places "
            "tenant list for this location are fetched server-side and appended to the "
            "reference images + prompt (Gemini path), grounding the render in the real "
            "surroundings. Validated 2026-06-10, artifacts/sv-context-pilot/."
        ),
    )
    guide_image_kind: Optional[Literal["clay", "context_3d", "model_3d"]] = Field(
        default=None,
        description=(
            "What image_base64 actually depicts, so the provider-facing description "
            "matches the pixels. 'clay' (default): synthetic color-coded massing model. "
            "'context_3d': photorealistic 3D-tiles capture of the EXISTING site with "
            "zone overlays marking intervention areas. 'model_3d': street-level capture "
            "of the authored 3D development model standing in real 3D-tiles context — "
            "the modelled buildings are the design and must be preserved."
        ),
    )
    semantic_guide_base64: Optional[str] = Field(
        default=None,
        description=(
            "Optional flat-color semantic zone map rendered from the same camera as "
            "image_base64 (Direct 3D class-ID pass: one color per zone class, real "
            "context transparent/dark). Anchors depth ordering and zone containment — "
            "sent to providers as an additional reference image."
        ),
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
                "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file." + suffix
            )
        if not Path(creds_path).exists():
            return (
                f"Credentials file was not found at {creds_path}. "
                "Check that the path is correct and the file exists." + suffix
            )
        return (
            f"Credentials file at {creds_path} could not be loaded. "
            "Ensure it contains valid service-account JSON." + suffix
        )

    if isinstance(exc, TransportError):
        return (
            "The server could not reach Google's token service "
            "(oauth2.googleapis.com). Check network / firewall settings." + suffix
        )

    if isinstance(exc, RuntimeError) and "403" in str(exc):
        return (
            "Google rejected the token request (403). "
            "Verify that the Vertex AI API is enabled on the project "
            "and the service account has the correct IAM roles." + suffix
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
    project_id: _uuid.UUID | None = None,
    reservation: RenderAuditLog | None = None,
):
    """Save input/output images to S3 and create an audit log row."""
    import boto3
    from botocore.config import Config as BotoConfig

    settings = get_settings()
    audit_id = reservation.id if reservation is not None else _uuid.uuid4()

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
        put_image_with_thumbnail(s3, bucket, input_key, base64.b64decode(input_b64))

    if output_b64:
        output_key = f"render-audit/{audit_id}/output.png"
        put_image_with_thumbnail(s3, bucket, output_key, base64.b64decode(output_b64))

    log = reservation or RenderAuditLog(
        id=audit_id,
        user_id=user.id,
        user_email=user.email,
        model=render_model,
        tokens_spent=token_cost,
        project_id=project_id,
    )
    log.input_image_key = input_key
    log.output_image_key = output_key
    log.prompt_preview = prompt_preview
    db.add(log)
    await db.commit()
    logger.info("Render audit saved: %s for %s", audit_id, user.email)


_ALLOWED_MODELS = {
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gpt-image-2",
    "gpt-image-2-2026-04-21",
}
_OPENAI_MODELS = {"gpt-image-2", "gpt-image-2-2026-04-21"}

# Token cost per render by model ($5 = 1000 tokens, 1 token = $0.005)
_MODEL_TOKEN_COST: dict[str, int] = {
    "gemini-2.5-flash-image": 8,  # ~$0.039
    "gemini-3.1-flash-image": 13,  # ~$0.067 (GA id)
    "gemini-3.1-flash-image-preview": 13,  # ~$0.067 (deprecated alias)
    "gemini-3-pro-image-preview": 27,  # ~$0.134
    "gpt-image-2": 13,
    "gpt-image-2-2026-04-21": 13,
}
_DEFAULT_TOKEN_COST = 13  # fallback
_WEEKLY_TOKEN_ALLOWANCE = 1000


def _utc_day_start(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


async def _get_tokens_spent_today(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(RenderAuditLog.tokens_spent), 0)).where(
            RenderAuditLog.created_at >= _utc_day_start()
        )
    )
    return int(result.scalar() or 0)


async def _enforce_global_daily_render_cap(
    db: AsyncSession,
    token_cost: int,
    daily_cap: int,
) -> None:
    if daily_cap <= 0:
        return

    tokens_spent_today = await _get_tokens_spent_today(db)
    if tokens_spent_today + token_cost <= daily_cap:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            "Daily render token cap reached. "
            f"Today has used {tokens_spent_today} of {daily_cap} tokens, "
            f"and this render costs {token_cost} tokens."
        ),
    )


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
        # Vertex AI path â€” requires Generative AI API enabled on project
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
        # Vertex AI â€” need Bearer token
        import google.auth
        import google.auth.transport.requests

        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(google.auth.transport.requests.Request())
        headers["Authorization"] = f"Bearer {credentials.token}"

    return headers


def _is_openai_model(model: str) -> bool:
    return model in _OPENAI_MODELS


def _prompt_with_negative(req: RenderRequest) -> str:
    prompt_text = req.prompt
    if req.negative_prompt:
        prompt_text += f"\n\nDo NOT include: {req.negative_prompt}"
    return prompt_text


def _decode_base64_payload(image_b64: str) -> bytes:
    """Decode a raw base64 image string, tolerating data URL prefixes."""
    payload = image_b64.split(",", 1)[1] if "," in image_b64[:64] else image_b64
    return base64.b64decode(payload)


def _guess_image_mime(image_b64: str) -> str:
    if image_b64.startswith("/9j/"):
        return "image/jpeg"
    if image_b64.startswith("iVBOR"):
        return "image/png"
    if image_b64.startswith("UklGR"):
        return "image/webp"
    return "image/png"


def _extension_for_mime(mime: str) -> str:
    if mime == "image/jpeg":
        return "jpg"
    if mime == "image/webp":
        return "webp"
    return "png"


def _openai_mask_png_bytes(mask_b64: str) -> bytes:
    """Convert the existing white-edit/black-keep mask to alpha-edit PNG."""
    raw = _decode_base64_payload(mask_b64)
    try:
        mask = Image.open(io.BytesIO(raw)).convert("L")
        alpha = mask.point(lambda pixel: 0 if pixel > 127 else 255)
        rgba = Image.new("RGBA", mask.size, (0, 0, 0, 255))
        rgba.putalpha(alpha)
        buf = io.BytesIO()
        rgba.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as exc:
        logger.warning("Could not convert OpenAI edit mask to alpha PNG: %s", exc)
        return raw


def _gemini_guide_image_text(kind: Optional[str], img_index: int) -> str:
    """Describe the primary guide image (image_base64) to Gemini.

    The description must match what the pixels actually show — a mismatched
    label (e.g. calling a photorealistic 3D capture a "clay massing model")
    makes the model distrust or reinterpret the guide.
    """
    if kind == "model_3d":
        return (
            f"Image {img_index} (DEVELOPMENT MODEL IN REAL CONTEXT): This is a "
            f"street-level capture of the site's detailed 3D development model "
            f"standing inside real photographic 3D context. The modelled buildings "
            f"ARE the proposed design: their positions, silhouettes, storey counts, "
            f"facade rhythm, and materials are authored ground truth — preserve them "
            f"exactly and resolve them into photorealistic built reality. The "
            f"surrounding real terrain, streets, and existing buildings are the real "
            f"site — keep them consistent with the capture."
        )
    if kind == "context_3d":
        return (
            f"Image {img_index} (REAL SITE CAPTURE): This is a photorealistic "
            f"street-level capture of the EXISTING site (3D photogrammetry). Colored "
            f"semi-transparent overlays mark where new interventions are planned. "
            f"Preserve the real context exactly; add the described new architecture "
            f"only within the marked areas."
        )
    return (
        f"Image {img_index} (SPATIAL LAYOUT): This is a 3D clay massing model "
        f"showing the exact spatial arrangement of all structures from the camera's "
        f"perspective. Use this as the definitive spatial reference."
    )


def _openai_source_framing(kind: Optional[str]) -> str:
    """First-paragraph framing of the source image for the OpenAI edit path."""
    if kind == "model_3d":
        return (
            "Use the first attached image as the source scene. It is a street-level "
            "capture of the site's authored 3D development model standing in real "
            "photographic context. The modelled buildings ARE the proposed design: "
            "preserve their positions, silhouettes, storey counts, facade rhythm, "
            "and materials exactly while resolving them into photorealistic built "
            "reality. Preserve the camera angle, lighting, terrain, and surrounding "
            "real context. Additional attached images are archetype references for "
            "the proposed zones. If a previous render is attached, use it as a "
            "visual continuity reference while keeping the source scene and prompt "
            "instructions authoritative.\n\n"
        )
    if kind == "context_3d":
        return (
            "Use the first attached image as the source city/site context. It is a "
            "photorealistic capture of the existing site; colored overlays mark "
            "where new interventions are planned. Preserve the camera angle, "
            "lighting, terrain, surrounding buildings, and all unedited context. "
            "Additional attached images are archetype references for the proposed "
            "zones. If a previous render is attached, use it as a visual continuity "
            "reference while keeping the source context and prompt instructions "
            "authoritative.\n\n"
        )
    return (
        "Use the first attached image as the source city/site context. "
        "Preserve the camera angle, lighting, terrain, surrounding buildings, "
        "and all unedited context. If an edit mask is attached, edit only the "
        "masked site areas. Additional attached images are archetype references "
        "for the proposed zones. If a previous render is attached, use it as a "
        "visual continuity reference while keeping the source context and prompt "
        "instructions authoritative.\n\n"
    )


def _build_openai_files(
    req: RenderRequest,
    include_mask: bool,
    site_pack: dict | None = None,
) -> list[tuple[str, tuple[str, bytes, str]]]:
    """Build multipart image files for OpenAI image editing."""
    if not req.image_base64:
        raise HTTPException(status_code=400, detail="OpenAI image editing requires image_base64.")

    input_mime = _guess_image_mime(req.image_base64)
    input_ext = _extension_for_mime(input_mime)
    files: list[tuple[str, tuple[str, bytes, str]]] = [
        ("image[]", (f"site-context.{input_ext}", _decode_base64_payload(req.image_base64), input_mime)),
    ]

    # Semantic zone map rides directly behind the source so the prompt can
    # reference it as "the second attached image".
    if req.semantic_guide_base64:
        files.append(
            (
                "image[]",
                ("semantic-zone-map.png", _decode_base64_payload(req.semantic_guide_base64), "image/png"),
            )
        )

    if req.previous_render_base64:
        previous_mime = _guess_image_mime(req.previous_render_base64)
        previous_ext = _extension_for_mime(previous_mime)
        files.append(
            (
                "image[]",
                (
                    f"previous-street-view-render.{previous_ext}",
                    _decode_base64_payload(req.previous_render_base64),
                    previous_mime,
                ),
            )
        )

    # GPT image edit models support up to 16 input images. Keep slots for the
    # site screenshot, optional previous render, and any real-context photos,
    # then use the rest for archetype refs.
    context_images = (site_pack or {}).get("images", [])
    max_refs = 16 - 1 - (1 if req.previous_render_base64 else 0) - len(context_images)
    for idx, arch_img in enumerate((req.archetype_images or [])[:max_refs], start=1):
        mime = _guess_image_mime(arch_img.image_base64)
        ext = _extension_for_mime(mime)
        safe_idx = str(idx).zfill(2)
        files.append(
            (
                "image[]",
                (f"archetype-reference-{safe_idx}.{ext}", _decode_base64_payload(arch_img.image_base64), mime),
            )
        )

    # Real-context photos (Street View + satellite) go last so the prompt can
    # reference them positionally as "the final N attached images".
    import base64 as _b64

    for idx, (_label, mime, b64) in enumerate(context_images, start=1):
        ext = _extension_for_mime(mime)
        files.append(
            (
                "image[]",
                (f"real-context-{str(idx).zfill(2)}.{ext}", _b64.b64decode(b64), mime),
            )
        )

    if include_mask and req.mask_base64:
        files.append(("mask", ("edit-mask.png", _openai_mask_png_bytes(req.mask_base64), "image/png")))

    return files


async def _call_openai_image_edit(
    req: RenderRequest,
    settings,
    render_model: str,
    *,
    include_mask: bool,
    site_pack: dict | None = None,
) -> httpx.Response:
    prompt_text = _prompt_with_negative(req)
    semantic_framing = (
        "The second attached image is a SEMANTIC ZONE MAP of the exact same view: "
        "each proposed zone painted one flat color, real context dark. Use it only "
        "to resolve volume identity, silhouettes, and depth ordering (nearer volumes "
        "occlude farther ones exactly as shown) — never copy its flat colors.\n\n"
        if req.semantic_guide_base64
        else ""
    )
    prompt_text = _openai_source_framing(req.guide_image_kind) + semantic_framing + prompt_text
    if site_pack:
        n_ctx = len(site_pack.get("images", []))
        prompt_text += (
            f"\n\nThe final {n_ctx} attached images are REAL Street View photographs of "
            "this exact site's surroundings, in compass order (north, east, south, west). "
            "Use them ONLY for the appearance of the surroundings - buildings, materials, "
            "signage, vegetation. The camera position, angle and framing must come from "
            "Image 1 EXACTLY; do not adopt the viewpoint of any context photograph.\n" + site_pack["prompt_block"]
        )
    prompt_text = append_render_preservation_lock(prompt_text)

    image_quality = req.image_quality or "auto"
    data = {
        "model": render_model,
        "prompt": prompt_text,
        "n": "1",
        "size": "auto",
        "quality": image_quality,
        "output_format": "png",
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

    async with httpx.AsyncClient(timeout=300.0) as client:
        return await client.post(
            "https://api.openai.com/v1/images/edits",
            data=data,
            files=_build_openai_files(req, include_mask=include_mask, site_pack=site_pack),
            headers=headers,
        )


async def _generate_openai_render(req: RenderRequest, settings, render_model: str) -> str:
    """Generate one render through OpenAI's image edit endpoint."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI is not configured. Set OPENAI_API_KEY in .env, or use the temporary OPENAI alias.",
        )

    logger.info(
        "Calling OpenAI image edit — model=%s, quality=%s, size=auto, prompt_length=%d, has_mask=%s, refs=%d",
        render_model,
        req.image_quality or "auto",
        len(req.prompt),
        bool(req.mask_base64),
        len(req.archetype_images or []),
    )

    # Real-world site context (same cached pack the Gemini path uses, so
    # compare-mode dual renders only fetch once).
    site_pack = None
    if req.site_context:
        from app.services.site_context import build_site_context_pack

        site_pack = await build_site_context_pack(req.site_context.lat, req.site_context.lng, req.site_context.heading)
        if site_pack:
            # GPT's edit endpoint weights every input image as a quasi-source —
            # a top-down satellite in the stack drags the output camera skyward
            # (observed 2026-06-10). Street View photos only for OpenAI; the
            # satellite stays on the Gemini path where role labels contain it.
            site_pack = {
                **site_pack,
                "images": [im for im in site_pack["images"] if "AERIAL" not in im[0]],
            }
            logger.info(
                "Site context attached to OpenAI edit: %d images for %.5f,%.5f",
                len(site_pack["images"]),
                req.site_context.lat,
                req.site_context.lng,
            )

    resp = await _call_openai_image_edit(
        req,
        settings,
        render_model,
        include_mask=bool(req.mask_base64),
        site_pack=site_pack,
    )
    if resp.status_code == 400 and req.mask_base64 and "mask" in resp.text.lower():
        logger.warning("OpenAI rejected the edit mask; retrying without mask for comparison render.")
        resp = await _call_openai_image_edit(
            req,
            settings,
            render_model,
            include_mask=False,
            site_pack=site_pack,
        )

    if resp.status_code != 200:
        error_body = resp.text[:500]
        logger.error("OpenAI image edit returned %d: %s", resp.status_code, error_body)
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI image error ({resp.status_code}): {error_body}",
        )

    body = resp.json()
    data = body.get("data") or []
    if not data:
        raise HTTPException(status_code=502, detail="OpenAI image response did not include image data.")

    image_b64 = data[0].get("b64_json")
    if image_b64:
        logger.info("OpenAI success — image size: %d chars", len(image_b64))
        return image_b64

    image_url = data[0].get("url")
    if image_url:
        async with httpx.AsyncClient(timeout=120.0) as client:
            image_resp = await client.get(image_url)
            image_resp.raise_for_status()
            return base64.b64encode(image_resp.content).decode()

    raise HTTPException(status_code=502, detail="OpenAI image response did not include b64_json or url.")


# Shared advisory lock value with Direct 3D. Every reservation is committed
# before provider work, making it visible to both pipelines' daily-cap checks.
_RENDER_CAP_LOCK = 23_140_785_570_739


async def _reserve_render(db, user, req, render_model, token_cost, daily_cap):
    try:
        if daily_cap > 0:
            await db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": _RENDER_CAP_LOCK},
            )
            await _enforce_global_daily_render_cap(db, token_cost, daily_cap)
        if not is_admin_or_above(user):
            await db.refresh(user, with_for_update=True)
            now = datetime.now(timezone.utc)
            if user.credits_reset_at is None or (now - user.credits_reset_at).days >= 7:
                user.render_credits = _WEEKLY_TOKEN_ALLOWANCE
                user.credits_reset_at = now
            if user.render_credits < token_cost:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough render tokens. Tokens reset weekly.",
                )
            user.render_credits -= token_cost
            db.add(user)
        reservation = RenderAuditLog(
            id=_uuid.uuid4(),
            user_id=user.id,
            user_email=user.email,
            model=render_model,
            tokens_spent=token_cost,
            project_id=req.project_id,
            prompt_preview=f"[Classic reserved] {req.prompt[:470]}",
        )
        db.add(reservation)
        await db.commit()
        return reservation
    except Exception:
        await db.rollback()
        raise


async def _refund_render(db, user, reservation):
    """Refund once when no image was produced, including concurrent retry safety."""
    try:
        await db.refresh(reservation, with_for_update=True)
        amount = reservation.tokens_spent
        if amount <= 0:
            await db.commit()
            return
        if not is_admin_or_above(user):
            await db.refresh(user, with_for_update=True)
            user.render_credits += amount
            db.add(user)
        reservation.tokens_spent = 0
        reservation.prompt_preview = "[Classic unbilled failure] Provider produced no image"
        db.add(reservation)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to refund render reservation %s", reservation.id)
        raise


@router.post("/generate", response_model=RenderResponse)
async def generate_render(
    req: RenderRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reserve budget atomically, release the transaction, then call the provider."""
    if req.project_id:
        await check_project_permission(req.project_id, user, db, required="editor")
    settings = get_settings()
    render_model = req.model if req.model in _ALLOWED_MODELS else _GEMINI_RENDER_MODEL
    token_cost = _MODEL_TOKEN_COST.get(render_model, _DEFAULT_TOKEN_COST)
    reservation = await _reserve_render(db, user, req, render_model, token_cost, settings.render_global_daily_token_cap)
    try:
        image_b64 = await _generate_render_image(req, settings, render_model)
    except Exception:
        await _refund_render(db, user, reservation)
        raise
    # An image exists: optional image polish or audit storage failure must not
    # trigger a refund or another paid generation.
    if req.post_process:
        try:
            image_b64 = _post_process(image_b64)
        except Exception:
            logger.exception("Render post-processing failed; returning provider image")
    try:
        reservation.prompt_preview = f"[Classic completed] {req.prompt[:470]}"
        db.add(reservation)
        await db.commit()
        await _save_render_audit(
            db,
            user,
            render_model,
            token_cost,
            req.image_base64,
            image_b64,
            prompt_preview=reservation.prompt_preview,
            project_id=req.project_id,
            reservation=reservation,
        )
    except Exception:
        await db.rollback()
        logger.exception("Render image produced but audit image storage failed: %s", reservation.id)
    return RenderResponse(image_base64=image_b64, seed=req.seed)


async def _generate_render_image(req: RenderRequest, settings, render_model: str) -> str:
    if _is_openai_model(render_model):
        return await _generate_openai_render(req, settings, render_model)
    if not settings.gemini_api_key and not settings.vertex_ai_project:
        raise HTTPException(status_code=503, detail="Image generation is not configured.")

    # --- Build payload ---
    parts: list[dict] = []

    # For dual anchoring: previous render goes first as structural anchor
    if req.previous_render_base64:
        parts.append(
            {
                "text": "Image 1 (STRUCTURAL ANCHOR): This is a previously generated render. "
                "Preserve its EXACT spatial layout, geometric volumes, camera angle, and "
                "proportions. Only modify the specific elements described in the prompt."
            }
        )
        parts.append(
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": req.previous_render_base64,
                }
            }
        )

    # Add the primary layout image (clay render, 3D capture, or screenshot)
    if req.image_base64:
        img_index = 2 if req.previous_render_base64 else 1
        parts.append({"text": _gemini_guide_image_text(req.guide_image_kind, img_index)})
        parts.append(
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": req.image_base64,
                }
            }
        )

    # Semantic zone map — same camera as the primary guide, one flat color per
    # proposal zone class. It pins depth ordering (nearer volumes occlude
    # farther ones) and zone containment without competing as a style source.
    if req.image_base64 and req.semantic_guide_base64:
        sem_index = 3 if req.previous_render_base64 else 2
        parts.append(
            {
                "text": f"Image {sem_index} (SEMANTIC ZONE MAP): The same camera view as the "
                f"previous image with each proposed zone painted one flat color and "
                f"the real context left dark. Use it ONLY to resolve which volume is "
                f"which, their exact silhouettes, and their depth ordering — nearer "
                f"volumes occlude farther ones exactly as shown. Never copy its flat "
                f"colors into the output."
            }
        )
        parts.append(
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": req.semantic_guide_base64,
                }
            }
        )

    # Add archetype reference images for multi-image composition.
    # Cap raised from 6 → 48 to support multi-view refs (street-level +
    # 30°/60°/90° aerials per zone). Each ref is ~30-50KB compressed JPEG,
    # so 48 at ~40KB = ~2MB, well within Gemini's ~20MB request limit.
    # The prompt's "ARCHETYPE REFERENCE IMAGES" section now explains which
    # angle each ref is taken from, so the label already carries the angle.
    if req.archetype_images:
        base_index = 3 if req.previous_render_base64 else 2
        if req.image_base64 and req.semantic_guide_base64:
            base_index += 1
        for i, arch_img in enumerate(req.archetype_images[:48]):  # Max 48 archetype refs
            img_idx = base_index + i
            color_ref = f" Located in the {arch_img.zone_color} zone." if arch_img.zone_color else ""
            parts.append(
                {
                    "text": f"Image {img_idx} (ARCHETYPE REFERENCE — {arch_img.label}): "
                    f"Apply the exact architectural style, materials, and textures from "
                    f"this reference image to the corresponding zone.{color_ref}"
                }
            )
            # Detect mime type from base64 header or default to jpeg
            mime = "image/jpeg"
            if arch_img.image_base64[:4] == "iVBO":
                mime = "image/png"
            parts.append(
                {
                    "inlineData": {
                        "mimeType": mime,
                        "data": arch_img.image_base64,
                    }
                }
            )

    # Real-world site context: Street View photos + satellite + tenant list.
    # Fetched server-side (keys stay in backend/.env); failure degrades silently.
    site_pack = None
    if req.site_context:
        from app.services.site_context import build_site_context_pack

        site_pack = await build_site_context_pack(req.site_context.lat, req.site_context.lng, req.site_context.heading)
        if site_pack:
            logger.info(
                "Site context attached: %d images for %.5f,%.5f",
                len(site_pack["images"]),
                req.site_context.lat,
                req.site_context.lng,
            )
            # A top-down satellite ("AERIAL") in the reference stack drags the output
            # camera skyward and washes out eye-level street-view renders. This was
            # observed + fixed for the OpenAI path on 2026-06-10; the satellite was
            # left on the Gemini path on the assumption role labels would contain it,
            # but it degrades Gemini the same way (confirmed 2026-06-15). Feed Gemini
            # the Street View photos only — keep the satellite out of the stack.
            for label, mime, b64 in site_pack["images"]:
                # Also drop the FORWARD STREET VIEW plate on the GEMINI path only: GPT
                # integrates it cleanly (kept on the OpenAI path), but Gemini over-leans on
                # the flat, offset plate — it degrades quality AND pulls the output camera off
                # the user's requested angle. Gemini grounds on the cardinal MATERIALS plates
                # only; prompt_block's forward clause is conditional ("if attached") so it goes
                # inert here. GPT untouched. (2026-06-16)
                if "AERIAL" in label or "FORWARD STREET VIEW" in label:
                    continue
                parts.append({"text": label})
                parts.append({"inlineData": {"mimeType": mime, "data": b64}})

    # If a mask is provided, send it as an additional image with explanation
    if req.image_base64 and req.mask_base64:
        parts.append(
            {
                "text": "The following black-and-white mask shows the exact area to edit "
                "(white = edit, black = keep unchanged):"
            }
        )
        parts.append(
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": req.mask_base64,
                }
            }
        )

    # Build the final prompt text
    prompt_text = _prompt_with_negative(req)

    # Site context follows custom art direction; the final shared lock keeps
    # source geometry authoritative across every supplied instruction.
    if site_pack:
        prompt_text = prompt_text + "\n\n" + site_pack["prompt_block"]

    prompt_text = append_render_preservation_lock(prompt_text)
    parts.append({"text": prompt_text})

    # No temperature: Gemini 3 image docs list no temperature parameter, and the
    # old guidance_scale->temperature mapping silently overrode the intended 0.0
    # to 0.75 on every render (guidance_scale is an undocumented Imagen-era
    # field). req.guidance_scale is accepted for back-compat but ignored.
    gen_config = {
        "responseModalities": ["TEXT", "IMAGE"],
    }

    # Add image size for models that support higher resolution
    _HIRES_MODELS = {
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
    }
    image_size = req.image_size
    if image_size is None and render_model in _HIRES_MODELS:
        image_size = "2K"  # Default to 2K for supported models
    if image_size and render_model in _HIRES_MODELS:
        gen_config["imageConfig"] = {"imageSize": image_size}

    # Thread the requested aspect ratio through to Gemini. Unset, the LAST
    # image in the payload governs the output frame — a silent geometry
    # distorter for zone polygons.
    _SUPPORTED_RATIOS = {
        "1:1",
        "2:3",
        "3:2",
        "3:4",
        "4:3",
        "4:5",
        "5:4",
        "9:16",
        "16:9",
        "21:9",
    }
    if req.aspect_ratio in _SUPPORTED_RATIOS and render_model in _HIRES_MODELS:
        gen_config.setdefault("imageConfig", {})["aspectRatio"] = req.aspect_ratio

    # Add thinking budget for complex scenes (only models that support it)
    _THINKING_MODELS = {
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
    }
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
        "Render request — model=%s, auth=%s, prompt_length=%d, has_mask=%s, " "imageSize=%s, aspectRatio=%s",
        req.model or _GEMINI_RENDER_MODEL,
        auth_mode,
        len(req.prompt),
        bool(req.mask_base64),
        gen_config.get("imageConfig", {}).get("imageSize", "default"),
        gen_config.get("imageConfig", {}).get("aspectRatio", "unset"),
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
            raise ValueError(f"No image in Gemini response. Model said: {text_response or '(no text)'}")

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

        return image_b64

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
    model: Optional[str] = Field(default=None, description="Model used for generation.")
    image_quality: Optional[str] = Field(
        default=None, pattern=r"^(auto|low|medium|high)$", description="Image quality used for generation."
    )


def _watermark_and_provenance(
    image_bytes: bytes,
    req: "SaveRenderRequest",
    *,
    server_provenance: dict | None = None,
) -> bytes:
    """Burn the ILLUSTRATIVE banner onto a saved render and embed provenance
    as a PNG tEXt chunk. Saved renders are the shareable artifact — the
    watermark/provenance pair is the designed safeguard for AI-generated
    planning imagery (visible label + machine-readable audit trail).
    Never fails the save: on any error the original bytes are kept."""
    import json

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")
        text = "ILLUSTRATIVE — NOT AN APPROVED DESIGN · City Prompt · " + datetime.now(timezone.utc).strftime(
            "%Y-%m-%d"
        )
        font_size = max(12, img.width // 90)
        try:
            font = ImageFont.load_default(size=font_size)
        except TypeError:  # very old Pillow
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = max(6, font_size // 2)
        x, y = pad, img.height - text_h - 2 * pad
        draw.rectangle(
            [x - pad // 2, y - pad // 2, x + text_w + pad // 2, y + text_h + pad],
            fill=(21, 21, 21, 150),
        )
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 235))

        provenance = {
            "generator": "City Prompt AI render — illustrative concept, not an approved design",
            "model": req.model,
            "style": req.style,
            "seed": req.seed,
            "prompt_sha256": hashlib.sha256((req.prompt or "").encode("utf-8")).hexdigest(),
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "source": server_provenance,
        }
        png_info = PngImagePlugin.PngInfo()
        png_info.add_text("cityprompt:provenance", json.dumps(provenance))

        out = io.BytesIO()
        img.save(out, format="PNG", pnginfo=png_info)
        return out.getvalue()
    except Exception as exc:  # noqa: BLE001 — watermark must never block a save
        logger.warning("Watermark/provenance failed, saving original image: %s", exc)
        return image_bytes


async def persist_render_to_gallery(
    db: AsyncSession,
    project_id: _uuid.UUID,
    req: SaveRenderRequest,
    *,
    variant: Optional[str] = None,
    outcome: Optional[str] = None,
    presentation_strategy: Optional[str] = None,
    scene_revision_sha256: Optional[str] = None,
    source_snapshot: dict | None = None,
    capture_fingerprint: str | None = None,
    output_fingerprint: str | None = None,
) -> SavedRenderResponse:
    """Core gallery save: watermark, dedupe, upload, append to project metadata.

    Shared by the manual Accept & Save endpoint and the Direct 3D auto-save
    path (which persists every paid result, including the untouched provider
    image when a safety fallback replaced it).
    """
    project_result = await db.execute(select(Project).where(Project.id == project_id).with_for_update())
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        image_bytes = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    # Dedupe on the ORIGINAL bytes: the watermark embeds a save timestamp, so
    # hashing afterwards would defeat same-image dedupe.
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    meta = dict(project.metadata_) if project.metadata_ else {}
    renders = list(meta.get("saved_renders", []))
    # Equal pixels do not imply an equal result: a provider rejection can return
    # the same clean source as a previous pass. Preserve the treatment and all
    # authoritative revision claims instead of reusing a misleading gallery row.
    dedup_identity = {
        "image_hash": image_hash,
        "variant": variant,
        "outcome": outcome,
        "presentation_strategy": presentation_strategy,
        "capture_fingerprint": capture_fingerprint,
        "output_fingerprint": output_fingerprint,
        "scene_revision_sha256": scene_revision_sha256,
        "plan_revision_sha256": (source_snapshot or {}).get("plan_revision_sha256"),
        "camera_revision_sha256": (source_snapshot or {}).get("camera_revision_sha256"),
        "prompt": req.prompt,
        "style": req.style,
        "seed": req.seed,
        "model": req.model,
        "image_quality": req.image_quality,
    }
    for existing in renders:
        if all(existing.get(key) == value for key, value in dedup_identity.items()):
            return SavedRenderResponse(**existing)

    render_id = str(_uuid.uuid4())
    file_key = f"projects/{project_id}/renders/{render_id}.png"

    from app.api.v1.documents import _upload_to_storage

    # These are server-only function arguments. SaveRenderRequest deliberately
    # offers no way to attach an authoritative snapshot or acceptance outcome.
    provenance_key = f"projects/{project_id}/renders/{render_id}.provenance.json"
    source_identity = {
        "scene_revision_sha256": scene_revision_sha256,
        "plan_revision_sha256": (source_snapshot or {}).get("plan_revision_sha256"),
        "camera_revision_sha256": (source_snapshot or {}).get("camera_revision_sha256"),
        "capture_fingerprint": capture_fingerprint,
        "output_fingerprint": output_fingerprint,
        "provenance_url": f"/api/v1/files/{provenance_key}" if source_snapshot else None,
    }
    if source_snapshot is not None:
        from app.services.render_provenance import canonical_json

        await _upload_to_storage(
            provenance_key,
            canonical_json(
                {
                    **source_identity,
                    "source_snapshot": source_snapshot,
                    "variant": variant,
                    "outcome": outcome,
                    "presentation_strategy": presentation_strategy,
                    "original_output_sha256": image_hash,
                    "prompt_sha256": hashlib.sha256(req.prompt.encode("utf-8")).hexdigest(),
                    "image_note": "Gallery PNG includes a visible illustrative label; output fingerprint identifies the original pixels.",
                }
            ).encode("utf-8"),
            "application/json",
        )
    image_bytes = _watermark_and_provenance(
        image_bytes,
        req,
        server_provenance=(
            {
                **source_identity,
                "variant": variant,
                "outcome": outcome,
                "presentation_strategy": presentation_strategy,
            }
            if source_snapshot
            else None
        ),
    )
    await _upload_to_storage(file_key, image_bytes, "image/png")

    image_url = f"/api/v1/files/{file_key}"
    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "id": render_id,
        "image_url": image_url,
        "prompt": req.prompt,
        "style": req.style,
        "seed": req.seed,
        "model": req.model,
        "image_quality": req.image_quality,
        "image_hash": image_hash,
        "created_at": now,
        "variant": variant,
        "outcome": outcome,
        "presentation_strategy": presentation_strategy,
        **source_identity,
    }

    renders.insert(0, entry)
    meta["saved_renders"] = renders
    project.metadata_ = meta

    await db.commit()
    logger.info(
        "Saved render %s for project %s (model=%s, quality=%s, variant=%s)",
        render_id,
        project_id,
        req.model or "unknown",
        req.image_quality or "unknown",
        variant or "manual",
    )

    return SavedRenderResponse(**entry)


@router.post("/projects/{project_id}/save", response_model=SavedRenderResponse, status_code=status.HTTP_201_CREATED)
async def save_render(
    project_id: _uuid.UUID,
    req: SaveRenderRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save an AI render image to the project's gallery in S3."""
    await check_project_permission(project_id, user, db, required="editor")
    return await persist_render_to_gallery(db, project_id, req)


@router.get("/projects/{project_id}/renders", response_model=list[SavedRenderResponse])
async def list_renders(
    project_id: _uuid.UUID,
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    share_token: str | None = None,
):
    """List all saved renders for a project."""
    await check_project_read_access(project_id, user, db, share_token)

    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_ or {}
    renders = meta.get("saved_renders", [])
    return [
        SavedRenderResponse(**({**r, "prompt": ""} if share_token else r))
        for r in renders
        if not share_token or r.get("variant") != "provider_original"
    ]


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
