"""
Generate archetype card images for SiteForge using Gemini API.

Reads all archetype JSON files, generates 1024x768 card thumbnails
for each archetype, and updates the JSON with thumbnailUrl paths.

Usage:
    python scripts/generate_card_images.py [--only buildings|streets|openspaces]
    python scripts/generate_card_images.py --skip-existing
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
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
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"


def _load_api_key() -> str:
    """Read GEMINI_API_KEY from backend/.env file."""
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
CARD_HEIGHT = 768

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

STYLE_ANCHOR = (
    "Style: photorealistic architectural visualization, high-end 3D rendering "
    "quality like a professional archviz studio. Warm golden-hour afternoon "
    "sunlight from the left at roughly 45 degrees, casting soft natural shadows. "
    "Slightly hazy atmospheric perspective in the background. Natural color "
    "grading with warm tones. Sharp detail on materials and textures — visible "
    "brick courses, glass reflections, concrete grain, metal patina. "
    "Photorealistic, 8K detail, architectural photography composition."
)

# For parks/streets/plazas — ONLY abstract silhouettes, NO real people
PEOPLE_SNIPPET = (
    "The ONLY human figures in this image must be flat-color semi-transparent "
    "silhouettes in soft muted pastel tones (light cyan, warm peach, soft mint, "
    "dusty rose). These are simple solid-color cutout shapes — NO realistic "
    "people, NO photorealistic humans, NO rendered faces, NO skin texture, "
    "NO clothing detail, NO anatomical features. Just flat translucent colored "
    "shapes like architectural competition render silhouettes. Place 5-8 of "
    "these abstract figures naturally on walkways, at benches, or standing in "
    "pairs. Do NOT generate any realistic or semi-realistic human beings."
)

NO_PEOPLE = (
    "Absolutely no people, no human figures, no pedestrians, no silhouettes, "
    "no crowds anywhere in the scene. The scene is completely empty of humans."
)

BUILDING_STYLE = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from across the street, approximately 25 meters away, "
    "at a 3/4 angle showing two facades. The full building is visible from ground "
    "to roofline with some sky above and street/sidewalk below. "
    "{description} "
    + NO_PEOPLE + " " + STYLE_ANCHOR
)

LANDSCAPE_STYLE = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from a pedestrian viewpoint, approximately 20 meters away, "
    "at a 3/4 angle showing the full scene. "
    "{description} "
    + STYLE_ANCHOR + " " + PEOPLE_SNIPPET
)

LANDSCAPE_NO_PEOPLE_STYLE = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from a pedestrian viewpoint, approximately 20 meters away, "
    "at a 3/4 angle showing the full scene. "
    "{description} "
    + NO_PEOPLE + " " + STYLE_ANCHOR
)

# ---------------------------------------------------------------------------
# Archetype JSON loaders
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert title to filesystem-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def load_building_archetypes() -> list[dict]:
    """Load building archetypes and build card entries."""
    path = _DATA_DIR / "buildingArchetypes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    archetypes = data if isinstance(data, list) else data.get("archetypes", data)

    cards = []
    for arch in archetypes:
        arch_id = arch.get("id", "")
        title = arch.get("title", arch_id)
        desc = arch.get("description", "")
        slug = _slugify(title)

        # Build a rich description from facade/roof metadata
        facade = arch.get("facadeDetail", {})
        roof = arch.get("roofDetail", {})

        card_desc = f"{title}. {desc}"
        if facade.get("primaryMaterial"):
            card_desc += f" Primary facade material: {facade['primaryMaterial']}."
        if facade.get("secondaryMaterial"):
            card_desc += f" Secondary material: {facade['secondaryMaterial']}."
        if facade.get("groundFloor"):
            card_desc += f" Ground floor: {facade['groundFloor']}."
        if facade.get("colorScheme"):
            card_desc += f" Color scheme: {facade['colorScheme']}."
        if roof.get("form"):
            card_desc += f" Roof: {roof['form']}."

        # Add surrounding context
        card_desc += (
            " Surrounding context shows a typical urban street with mature "
            "trees and neighboring buildings."
        )

        out_dir = _PUBLIC_DIR / "buildings" / slug
        thumb_url = f"/archetypes/buildings/{slug}/hero.png"

        cards.append({
            "arch_id": arch_id,
            "title": title,
            "filename": "hero.png",
            "output_dir": out_dir,
            "thumbnail_url": thumb_url,
            "description": card_desc,
            "include_people": False,
            "category": "building",
        })

        # Also generate variant images if present
        variants = arch.get("variants", [])
        for vi, variant in enumerate(variants):
            v_title = variant.get("label", f"Variant {vi}")
            v_desc = variant.get("description", "")
            v_facade = variant.get("facadeDetail", {})
            v_roof = variant.get("roofDetail", {})

            v_card_desc = f"{title} — {v_title} variant. {v_desc}"
            if v_facade.get("primaryMaterial"):
                v_card_desc += f" Primary facade: {v_facade['primaryMaterial']}."
            if v_facade.get("secondaryMaterial"):
                v_card_desc += f" Secondary material: {v_facade['secondaryMaterial']}."
            if v_facade.get("groundFloor"):
                v_card_desc += f" Ground floor: {v_facade['groundFloor']}."
            if v_roof.get("form"):
                v_card_desc += f" Roof: {v_roof['form']}."
            v_card_desc += (
                " Surrounding context shows a typical urban street with mature "
                "trees and neighboring buildings."
            )

            v_thumb_url = f"/archetypes/buildings/{slug}/variant_{vi}.png"
            cards.append({
                "arch_id": f"{arch_id}__variant_{vi}",
                "title": f"{title} — {v_title}",
                "filename": f"variant_{vi}.png",
                "output_dir": out_dir,
                "thumbnail_url": v_thumb_url,
                "description": v_card_desc,
                "include_people": False,
                "category": "building",
            })

    return cards


def load_street_archetypes() -> list[dict]:
    """Load street/path archetypes and build card entries."""
    path = _DATA_DIR / "streetPathArchetypes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    archetypes = data if isinstance(data, list) else data.get("archetypes", data)

    cards = []
    for arch in archetypes:
        arch_id = arch.get("id", "")
        title = arch.get("title", arch_id)
        desc = arch.get("description", "")
        slug = _slugify(title)

        # Build description from render prompt or description
        render_prompt = arch.get("renderPrompt", {})
        card_desc = f"{title}. {desc}"
        if render_prompt.get("mapOverlay"):
            # Extract useful visual details from the render prompt
            overlay = render_prompt["mapOverlay"]
            # Take first 300 chars of overlay for visual detail
            card_desc += f" Visual details: {overlay[:300]}"

        # Street detail metadata
        street_detail = arch.get("streetDetail", {})
        if street_detail.get("surfaceMaterial"):
            card_desc += f" Surface: {street_detail['surfaceMaterial']}."
        if street_detail.get("laneConfiguration"):
            card_desc += f" Lanes: {street_detail['laneConfiguration']}."
        if street_detail.get("streetFurniture"):
            card_desc += f" Furniture: {street_detail['streetFurniture']}."

        out_dir = _PUBLIC_DIR / "streets" / slug
        thumb_url = f"/archetypes/streets/{slug}/hero.png"

        # Streets get abstract people silhouettes
        cards.append({
            "arch_id": arch_id,
            "title": title,
            "filename": "hero.png",
            "output_dir": out_dir,
            "thumbnail_url": thumb_url,
            "description": card_desc,
            "include_people": True,
            "category": "street",
        })

    return cards


def load_openspace_archetypes() -> list[dict]:
    """Load open space archetypes and build card entries."""
    path = _DATA_DIR / "openSpaceArchetypes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    archetypes = data if isinstance(data, list) else data.get("archetypes", data)

    # These categories should NOT have people (infrastructure, water, parking)
    NO_PEOPLE_CATEGORIES = {
        "parking_areas", "water_features",
    }

    cards = []
    for arch in archetypes:
        arch_id = arch.get("id", "")
        title = arch.get("title", arch_id)
        desc = arch.get("description", "")
        category = arch.get("aestheticCategory", "")
        slug = _slugify(title)

        card_desc = f"{title}. {desc}"

        # Landscape detail
        landscape = arch.get("landscapeDetail", {})
        if landscape.get("vegetation"):
            card_desc += f" Vegetation: {landscape['vegetation']}."
        if landscape.get("hardscape"):
            card_desc += f" Hardscape: {landscape['hardscape']}."
        if landscape.get("waterFeature"):
            card_desc += f" Water: {landscape['waterFeature']}."
        if landscape.get("furniture"):
            card_desc += f" Furniture: {landscape['furniture']}."

        card_desc += " Surrounding context shows urban buildings in the background."

        include_people = category not in NO_PEOPLE_CATEGORIES
        out_dir = _PUBLIC_DIR / "openspaces" / slug
        thumb_url = f"/archetypes/openspaces/{slug}/hero.png"

        cards.append({
            "arch_id": arch_id,
            "title": title,
            "filename": "hero.png",
            "output_dir": out_dir,
            "thumbnail_url": thumb_url,
            "description": card_desc,
            "include_people": include_people,
            "category": "openspace",
        })

    return cards


# ---------------------------------------------------------------------------
# Gemini API call
# ---------------------------------------------------------------------------

def generate_image(prompt: str, retries: int = 2) -> bytes | None:
    """Call Gemini API to generate an image. Retries on failure."""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.7,
        },
    }

    for attempt in range(retries + 1):
        try:
            resp = httpx.post(
                API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120.0,
            )
        except httpx.TimeoutException:
            print(f"  ERROR: Request timed out (attempt {attempt + 1})")
            if attempt < retries:
                time.sleep(5)
                continue
            return None
        except httpx.RequestError as exc:
            print(f"  ERROR: Network error — {exc}")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        if resp.status_code == 429:
            print(f"  RATE LIMITED — waiting 30s (attempt {attempt + 1})")
            time.sleep(30)
            continue

        if resp.status_code != 200:
            print(f"  ERROR: Gemini returned HTTP {resp.status_code}")
            print(f"  Response: {resp.text[:300]}")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        # Parse response
        try:
            body = resp.json()
            candidates = body.get("candidates", [])
            if not candidates:
                print("  ERROR: No candidates in response")
                if attempt < retries:
                    time.sleep(3)
                    continue
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    inline = part["inlineData"]
                    if inline.get("mimeType", "").startswith("image/"):
                        return base64.b64decode(inline["data"])

            for part in parts:
                if "text" in part:
                    print(f"  Model said: {part['text'][:200]}")

            print("  ERROR: No image part in response")
            if attempt < retries:
                time.sleep(3)
                continue
            return None

        except (ValueError, KeyError, IndexError) as exc:
            print(f"  ERROR: Failed to parse response — {exc}")
            if attempt < retries:
                time.sleep(3)
                continue
            return None

    return None


def resize_to_card(image_bytes: bytes) -> bytes:
    """Resize and crop image to card dimensions."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    target_ratio = CARD_WIDTH / CARD_HEIGHT
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        new_height = CARD_HEIGHT
        new_width = int(img.width * (CARD_HEIGHT / img.height))
    else:
        new_width = CARD_WIDTH
        new_height = int(img.height * (CARD_WIDTH / img.width))

    img = img.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - CARD_WIDTH) // 2
    top = (new_height - CARD_HEIGHT) // 2
    img = img.crop((left, top, left + CARD_WIDTH, top + CARD_HEIGHT))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# JSON updater — set thumbnailUrl on each archetype
# ---------------------------------------------------------------------------

def update_json_thumbnails(json_path: Path, url_map: dict[str, str]):
    """Update thumbnailUrl fields in the archetype JSON file."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    archetypes = data if isinstance(data, list) else data.get("archetypes", data)

    changed = False
    for arch in archetypes:
        arch_id = arch.get("id", "")
        if arch_id in url_map:
            arch["thumbnailUrl"] = url_map[arch_id]
            changed = True

        # Update variant thumbnails too
        for vi, variant in enumerate(arch.get("variants", [])):
            v_key = f"{arch_id}__variant_{vi}"
            if v_key in url_map:
                variant["thumbnailUrl"] = url_map[v_key]
                changed = True

    if changed:
        json_path.write_text(
            json.dumps(data if not isinstance(data, list) else archetypes,
                       indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Updated {json_path.name} with {len(url_map)} thumbnail URLs")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate archetype card images")
    parser.add_argument("--only", choices=["buildings", "streets", "openspaces"],
                        help="Only generate for one category")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip images that already exist on disk")
    args = parser.parse_args()

    # Load all cards
    all_cards = []
    if args.only is None or args.only == "buildings":
        all_cards.extend(load_building_archetypes())
    if args.only is None or args.only == "streets":
        all_cards.extend(load_street_archetypes())
    if args.only is None or args.only == "openspaces":
        all_cards.extend(load_openspace_archetypes())

    print(f"SiteForge Archetype Card Image Generator")
    print(f"Model: {MODEL}")
    print(f"Resolution: {CARD_WIDTH}x{CARD_HEIGHT}")
    print(f"Total cards to generate: {len(all_cards)}")
    print("-" * 60)

    # Track URLs for JSON update
    building_urls: dict[str, str] = {}
    street_urls: dict[str, str] = {}
    openspace_urls: dict[str, str] = {}

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, card in enumerate(all_cards, 1):
        out_dir: Path = card["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / card["filename"]

        # Skip existing if requested
        if args.skip_existing and output_path.exists():
            print(f"[{i}/{len(all_cards)}] SKIP (exists): {card['title']}")
            skip_count += 1
            # Still record URL
            url_map = {"building": building_urls, "street": street_urls,
                       "openspace": openspace_urls}[card["category"]]
            url_map[card["arch_id"]] = card["thumbnail_url"]
            continue

        print(f"\n[{i}/{len(all_cards)}] Generating: {card['title']}")

        # Build prompt
        if card["category"] == "building":
            prompt = BUILDING_STYLE.format(description=card["description"])
        elif card["include_people"]:
            prompt = LANDSCAPE_STYLE.format(description=card["description"])
        else:
            prompt = LANDSCAPE_NO_PEOPLE_STYLE.format(description=card["description"])

        print(f"  Category: {card['category']} | People: {card['include_people']}")
        print(f"  Prompt length: {len(prompt)} chars")
        print(f"  Calling Gemini API...")

        image_bytes = generate_image(prompt)

        if image_bytes is None:
            print(f"  FAILED — skipping {card['title']}")
            fail_count += 1
            continue

        # Resize to card dimensions
        print(f"  Resizing to {CARD_WIDTH}x{CARD_HEIGHT}...")
        card_bytes = resize_to_card(image_bytes)

        # Save
        output_path.write_bytes(card_bytes)
        file_size_kb = len(card_bytes) / 1024
        print(f"  Saved: {output_path} ({file_size_kb:.1f} KB)")
        success_count += 1

        # Record URL for JSON update
        url_map = {"building": building_urls, "street": street_urls,
                   "openspace": openspace_urls}[card["category"]]
        url_map[card["arch_id"]] = card["thumbnail_url"]

        # Rate limit pause
        if i < len(all_cards):
            time.sleep(2)

    # Update JSON files with thumbnailUrls
    print("\n" + "=" * 60)
    print("Updating JSON files with thumbnailUrl paths...")

    if building_urls:
        update_json_thumbnails(_DATA_DIR / "buildingArchetypes.json", building_urls)
    if street_urls:
        update_json_thumbnails(_DATA_DIR / "streetPathArchetypes.json", street_urls)
    if openspace_urls:
        update_json_thumbnails(_DATA_DIR / "openSpaceArchetypes.json", openspace_urls)

    print(f"\nDone! {success_count} generated, {fail_count} failed, {skip_count} skipped")


if __name__ == "__main__":
    main()
