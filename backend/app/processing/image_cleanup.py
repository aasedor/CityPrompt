"""
Gemini-based reference-image cleanup for image-to-3D inputs.

Meshy fuses everything visible in the reference views into mesh geometry —
people become melty low-poly figures, patio furniture becomes lumps, and
neighbouring buildings weld onto the podium (calgary_plus_15 pilot,
2026-07-11). rembg cannot help: people in front of the building ARE
foreground, so matting keeps them.

This module does instruction-driven removal with Gemini image editing
instead. Levels:
  "entourage"     — remove people, vehicles, street furniture, and legible
                    signage text; KEEP trees (they read well on the globe).
  "building_only" — also remove trees, planting, and neighbouring buildings.

Fail-open like image_isolation: any error returns the original bytes, so a
Gemini outage degrades to the old behaviour instead of failing the task.
"""

import base64
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_CLEANUP_MODEL = "gemini-3.1-flash-image"
_TIMEOUT_S = 120.0

_REMOVE_BY_LEVEL = {
    "entourage": (
        "every person and human figure, all vehicles (cars, bicycles, buses), "
        "all street furniture (patio tables, chairs, umbrellas, benches, "
        "planters, bollards, light poles), and all legible signage text"
    ),
    "building_only": (
        "every person and human figure, all vehicles, all street furniture, "
        "all legible signage text, all trees and planting, and any "
        "neighbouring or background buildings that are not the main subject"
    ),
}


def cleanup_levels() -> tuple[str, ...]:
    return tuple(_REMOVE_BY_LEVEL)


def clean_reference_image(image_bytes: bytes, level: str = "entourage") -> bytes:
    """Remove distracting elements from a reference image via Gemini editing.

    Returns edited PNG/JPEG bytes, or the ORIGINAL bytes on any failure
    (fail-open). The instruction pins identity preservation, and the hard
    constraint sits at the END of the prompt — Gemini weights later
    instructions more heavily (CLAUDE.md render rule).
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.warning("Image cleanup skipped: GEMINI_API_KEY not set")
        return image_bytes
    remove_list = _REMOVE_BY_LEVEL.get(level)
    if remove_list is None:
        logger.warning("Image cleanup skipped: unknown level %r", level)
        return image_bytes

    mime = "image/png" if image_bytes[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
    prompt = (
        f"Edit this architectural photograph: remove {remove_list}. "
        "Fill the areas they occupied with a natural continuation of the "
        "existing pavement, ground, or sky. "
        "CRITICAL: the building itself must remain EXACTLY as shown — same "
        "geometry, same window pattern and mullion spacing, same materials, "
        "same colors, same camera angle and framing. Do not redraw, "
        "beautify, or alter the building in any way."
    )
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{_CLEANUP_MODEL}:generateContent"
            f"?key={settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime, "data": base64.b64encode(image_bytes).decode()}},
                        {"text": prompt},
                    ],
                }
            ],
            # Temperature 0 for maximum edit fidelity — this is surgical
            # removal, not generation.
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": 0.0},
        }
        resp = httpx.post(url, json=payload, timeout=_TIMEOUT_S)
        if resp.status_code != 200:
            logger.warning(
                "Image cleanup failed (non-fatal): HTTP %d %s",
                resp.status_code,
                resp.text[:200],
            )
            return image_bytes
        for candidate in resp.json().get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data") or {}
                if inline.get("data"):
                    cleaned = base64.b64decode(inline["data"])
                    logger.info(
                        "Image cleanup (%s): %dKB -> %dKB",
                        level,
                        len(image_bytes) // 1024,
                        len(cleaned) // 1024,
                    )
                    return cleaned
        logger.warning("Image cleanup returned no image part (non-fatal)")
        return image_bytes
    except Exception as exc:
        logger.warning("Image cleanup failed (non-fatal): %s", exc)
        return image_bytes
