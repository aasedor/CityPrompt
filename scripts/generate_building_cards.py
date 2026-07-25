"""
Generate card images for new building archetypes (Rec Centre, Sports Arena, Hotel).

Creates front_day.png + 4 variant images per archetype using Gemini API.
Also generates _thumb.jpg thumbnails for each.

Usage:
    python scripts/generate_building_cards.py [--skip-existing]
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
from pathlib import Path

import httpx
from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_DATA_FILE = _PROJECT_ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes" / "buildings"


def _load_api_key() -> str:
    if not _ENV_FILE.exists():
        print(f"ERROR: .env file not found at {_ENV_FILE}")
        sys.exit(1)
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    print("ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)


API_KEY = _load_api_key()
MODEL = "gemini-2.5-flash-image"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

CARD_WIDTH = 1024
CARD_HEIGHT = 1024

# Target archetype IDs
TARGET_IDS = [
    "community_recreation_centre",
    "modern_sports_arena",
    "boutique_hotel_tower",
]

# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

STYLE_ANCHOR = (
    "Style: photorealistic architectural visualization, high-end 3D rendering "
    "quality like a professional archviz studio. Warm golden-hour afternoon "
    "sunlight from the left at roughly 45 degrees, casting soft natural shadows. "
    "Slightly hazy atmospheric perspective in the background. Natural color "
    "grading with warm tones. Sharp detail on materials and textures. "
    "Photorealistic, 8K detail, architectural photography composition."
)

NO_PEOPLE = (
    "Absolutely no people, no human figures, no pedestrians, no silhouettes, "
    "no crowds anywhere in the scene. The scene is completely empty of humans."
)


def build_main_prompt(archetype: dict) -> str:
    """Build prompt for the main front_day card image."""
    title = archetype["title"]
    desc = archetype["description"]
    facade = archetype.get("facadeDetail", {})
    roof = archetype.get("roofDetail", {})

    materials = []
    if facade.get("primaryMaterial"):
        materials.append(facade["primaryMaterial"])
    if facade.get("secondaryMaterial"):
        materials.append(facade["secondaryMaterial"])
    if facade.get("groundFloor"):
        materials.append(f"Ground floor: {facade['groundFloor']}")

    prompt = (
        f"Front-facing photorealistic architectural rendering of a {title}. "
        f"{desc}. "
        f"Materials: {', '.join(materials)}. "
        f"Roof: {roof.get('form', 'flat roof')} with {roof.get('material', 'standard roofing')}. "
        f"Color scheme: {facade.get('colorScheme', 'neutral tones')}. "
        f"Centered composition, slightly elevated eye level, showing the full building facade. "
        f"Urban context with sidewalk, street trees, and sky. "
        f"{NO_PEOPLE} {STYLE_ANCHOR}"
    )
    return prompt


def build_variant_prompt(archetype: dict, variant: dict) -> str:
    """Build prompt for a variant card image."""
    title = archetype["title"]
    label = variant["label"]
    desc = variant["description"]
    facade = variant.get("facadeDetail", {})
    roof = variant.get("roofDetail", {})

    prompt = (
        f"Front-facing photorealistic architectural rendering of a {title} - {label} variant. "
        f"{desc} "
        f"Primary material: {facade.get('primaryMaterial', 'premium materials')}. "
        f"Ground floor: {facade.get('groundFloor', 'active street frontage')}. "
        f"Color scheme: {facade.get('colorScheme', 'refined palette')}. "
        f"Roof form: {roof.get('form', 'articulated roof')}. "
        f"Centered composition, slightly elevated eye level, showing the full building facade. "
        f"Urban context with sidewalk, street trees, and sky. "
        f"{NO_PEOPLE} {STYLE_ANCHOR}"
    )
    return prompt


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(prompt: str, retries: int = 5) -> bytes | None:
    """Call Gemini API to generate an image."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 1.0,
        },
    }

    for attempt in range(retries):
        try:
            resp = httpx.post(API_URL, json=payload, timeout=120.0)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  RATE LIMITED - waiting {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()

            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        return base64.b64decode(part["inlineData"]["data"])

            print(f"  WARNING: No image in response (attempt {attempt + 1})")
            time.sleep(5)

        except Exception as e:
            print(f"  ERROR: {e} (attempt {attempt + 1})")
            time.sleep(10)

    return None


def save_image(image_bytes: bytes, output_path: Path, size: tuple[int, int] = (CARD_WIDTH, CARD_HEIGHT)) -> None:
    """Resize and save image as PNG."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize(size, Image.LANCZOS)
    img.save(str(output_path), "PNG", optimize=True)


def save_thumbnail(image_bytes: bytes, output_path: Path, size: tuple[int, int] = (256, 256)) -> None:
    """Resize and save thumbnail as JPEG."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize(size, Image.LANCZOS)
    img.save(str(output_path), "JPEG", quality=80, optimize=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    # Load archetypes
    data = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    archetypes = data.get("archetypes", [])

    targets = [a for a in archetypes if a["id"] in TARGET_IDS]
    print(f"Found {len(targets)} target archetypes to generate images for")

    total_generated = 0
    total_failed = 0

    for arch in targets:
        arch_id = arch["id"]
        arch_title = arch["title"]
        out_dir = _PUBLIC_DIR / arch_id
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Archetype: {arch_title} ({arch_id})")
        print(f"Output: {out_dir}")
        print(f"{'='*60}")

        # --- Main card image (front_day) ---
        main_path = out_dir / "front_day.png"
        main_thumb = out_dir / "front_day_thumb.jpg"

        if args.skip_existing and main_path.exists():
            print(f"  SKIP: front_day.png already exists")
        else:
            print(f"  Generating main card image...")
            prompt = build_main_prompt(arch)
            img_bytes = generate_image(prompt)
            if img_bytes:
                save_image(img_bytes, main_path)
                save_thumbnail(img_bytes, main_thumb)
                total_generated += 1
                print(f"  OK: front_day.png ({main_path.stat().st_size // 1024}KB)")
            else:
                total_failed += 1
                print(f"  FAILED: front_day.png")

        # --- Variant images ---
        variants = arch.get("variants", [])
        for vi, variant in enumerate(variants):
            var_path = out_dir / f"variant_{vi}.png"
            var_thumb = out_dir / f"variant_{vi}_thumb.jpg"

            if args.skip_existing and var_path.exists():
                print(f"  SKIP: variant_{vi}.png already exists")
                continue

            print(f"  Generating variant {vi}: {variant['label']}...")
            prompt = build_variant_prompt(arch, variant)
            img_bytes = generate_image(prompt)
            if img_bytes:
                save_image(img_bytes, var_path)
                save_thumbnail(img_bytes, var_thumb)
                total_generated += 1
                print(f"  OK: variant_{vi}.png ({var_path.stat().st_size // 1024}KB)")
            else:
                total_failed += 1
                print(f"  FAILED: variant_{vi}.png")

            # Small delay between variants to avoid rate limiting
            time.sleep(2)

        # Delay between archetypes
        time.sleep(3)

    print(f"\n{'='*60}")
    print(f"DONE: {total_generated} generated, {total_failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
