"""
Custom Style API — LLM prompt expansion for user-defined ("Custom") zones.

The user describes their vision in a rough sentence or two and optionally
uploads PDFs (design briefs, mood boards). This endpoint expands that into a
single render-ready aerial description paragraph using Claude, folding in the
extracted PDF text and the zone's physical facts. The frontend caches the
result on the zone; renders fall back to the raw prompt if expansion fails.
"""

import logging
import uuid
from typing import Any, Optional

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.core.usage_logger import log_api_usage_sync
from app.models.models import Document, User

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

EXPANSION_MODEL = "claude-sonnet-5"
MAX_CHARS_PER_DOCUMENT = 8_000
MAX_CHARS_TOTAL = 24_000

DOMAIN_SUBJECT = {
    "building": "building",
    "open_space": "park or plaza",
    "street": "street",
}

SYSTEM_PROMPT = """You write visual descriptions that will be fed to an image-generation model rendering a photorealistic oblique aerial drone view (~60m altitude) of a masterplan.

Given a user's rough idea, optional excerpts from their documents, and the zone's dimensions, write ONE paragraph of 80-140 words describing exactly what this {subject} looks like from the air.

Requirements:
- Concrete materials, massing, roof form and roofscape detail (most visible from above), color palette, ground-plane treatment, landscape and paving.
- Present tense, simple natural language, no bullet points.
- No camera or style words (no "photorealistic", "render", "4k", "aerial view").
- No text or labels in the scene.
- Scale consistent with the stated dimensions.
- If the documents contradict the user's prompt, the user's prompt wins.

Output only the paragraph."""


class CustomStyleExpandRequest(BaseModel):
    project_id: uuid.UUID
    zone_id: Optional[uuid.UUID] = None
    user_prompt: str = Field(..., min_length=3, max_length=4000)
    document_ids: list[uuid.UUID] = Field(default_factory=list, max_length=10)
    zone_context: Optional[dict[str, Any]] = None
    domain: str = "building"


class UsedDocument(BaseModel):
    id: str
    filename: str
    status: str
    chars_used: int


class CustomStyleExpandResponse(BaseModel):
    expanded_prompt: str
    model: str
    used_documents: list[UsedDocument]
    truncated: bool


def _format_zone_facts(zone_context: Optional[dict[str, Any]]) -> str:
    if not zone_context:
        return ""

    def clip(value: Any) -> str:
        # Values are caller-supplied JSON — cap each so an oversized field
        # can't inflate the LLM prompt past the size limits enforced elsewhere.
        return str(value)[:80]

    parts: list[str] = []
    if zone_context.get("area_sqm"):
        parts.append(f"footprint area ~{clip(zone_context['area_sqm'])} m²")
    if zone_context.get("width_m") and zone_context.get("depth_m"):
        parts.append(f"~{clip(zone_context['width_m'])}m x {clip(zone_context['depth_m'])}m")
    if zone_context.get("floors"):
        parts.append(f"{clip(zone_context['floors'])} floors")
    if zone_context.get("height_m"):
        parts.append(f"~{clip(zone_context['height_m'])}m tall")
    if zone_context.get("zone_type"):
        parts.append(f"zone type: {clip(zone_context['zone_type'])}")
    return ", ".join(parts)


@router.post("/expand", response_model=CustomStyleExpandResponse)
async def expand_custom_style(
    req: CustomStyleExpandRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Expand a rough user prompt into a render-ready aerial description."""
    await check_project_permission(req.project_id, user, db, required="editor")

    # Collect extracted text from the referenced documents (PDFs)
    used_documents: list[UsedDocument] = []
    doc_excerpts: list[str] = []
    truncated = False
    total_chars = 0

    if req.document_ids:
        result = await db.execute(select(Document).where(Document.id.in_(req.document_ids)))
        documents = {doc.id: doc for doc in result.scalars().all()}

        for doc_id in req.document_ids:
            document = documents.get(doc_id)
            # Same message whether the document is missing or belongs to another
            # project — avoids a global document-existence oracle.
            if not document or document.project_id != req.project_id:
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found in this project")

            text = ""
            if document.processing_status == "completed" and isinstance(document.extracted_data, dict):
                extraction = document.extracted_data.get("extraction") or {}
                raw_text = extraction.get("text_content") or ""
                text = str(raw_text).strip()

            chars_used = 0
            if text:
                if len(text) > MAX_CHARS_PER_DOCUMENT:
                    text = text[:MAX_CHARS_PER_DOCUMENT]
                    truncated = True
                room = MAX_CHARS_TOTAL - total_chars
                if room <= 0:
                    text = ""
                    truncated = True
                elif len(text) > room:
                    text = text[:room]
                    truncated = True
                if text:
                    chars_used = len(text)
                    total_chars += chars_used
                    doc_excerpts.append(f'--- Excerpt from "{document.filename}" ---\n{text}')

            used_documents.append(
                UsedDocument(
                    id=str(document.id),
                    filename=document.filename,
                    status=document.processing_status or "pending",
                    chars_used=chars_used,
                )
            )

    subject = DOMAIN_SUBJECT.get(req.domain, "building")
    zone_facts = _format_zone_facts(req.zone_context)

    user_message_parts = [f"User's idea: {req.user_prompt.strip()}"]
    if zone_facts:
        user_message_parts.append(f"Zone dimensions: {zone_facts}")
    if doc_excerpts:
        user_message_parts.append(
            "Document excerpts (supporting reference only — the user's idea above wins on any conflict):\n\n"
            + "\n\n".join(doc_excerpts)
        )
    user_message = "\n\n".join(user_message_parts)

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        message = await client.messages.create(
            model=EXPANSION_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT.format(subject=subject),
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:
        logger.error(f"Custom style expansion failed: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Prompt expansion is unavailable right now — your raw description will be used.",
        )

    try:
        log_api_usage_sync(
            provider="anthropic",
            operation="custom_style_expand",
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
    except Exception as exc:
        logger.warning(f"Failed to log custom style expansion usage: {exc}")

    expanded = "".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    ).strip()
    if not expanded:
        raise HTTPException(
            status_code=502,
            detail="Prompt expansion returned no text — your raw description will be used.",
        )

    return CustomStyleExpandResponse(
        expanded_prompt=expanded,
        model=EXPANSION_MODEL,
        used_documents=used_documents,
        truncated=truncated,
    )
