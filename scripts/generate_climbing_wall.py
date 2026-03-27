"""
Generate Climbing Wall Building archetype images using Gemini 3 Pro.

Generates 4 variant images and saves to
frontend/public/archetypes/buildings/climbing_wall_building/
"""

from __future__ import annotations

import base64
import io
import shutil
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
_OUT_DIR = (
    _PROJECT_ROOT
    / "frontend"
    / "public"
    / "archetypes"
    / "buildings"
    / "climbing_wall_building"
)

CARD_WIDTH = 1024
CARD_HEIGHT = 768


def _load_api_key() -> str:
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    print("ERROR: GEMINI_API_KEY not found")
    sys.exit(1)


API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

# ---------------------------------------------------------------------------
# Variant prompts
# ---------------------------------------------------------------------------

VARIANTS = [
    {
        "label": "The Crucible",
        "filename": "variant_0.png",
        "prompt": (
            "Photorealistic 8K architectural rendering, aerial three-quarter angle "
            "view, golden hour warm light. A massive asymmetric wedge-shaped "
            "industrial waste-to-energy building, 12 stories tall at the high end "
            "tapering to 3 stories. The entire western facade is a 75-degree sloped "
            "climbing wall clad in dark charcoal hexagonal fiberglass panels with "
            "amber LED route lines glowing between panels. The opposite facade is "
            "floor-to-ceiling industrial glass. Weathering Corten steel cladding in "
            "rust-orange on the building ends. A public running track with native "
            "grasses on the rooftop terrace. A tall smokestack emitting clean white "
            "steam at the south end, backlit by golden sunset light. Landscaped park "
            "with scattered boulders and black rubber fall zone at the base. Tiny "
            "climbers visible on the wall surface. Urban industrial waterfront "
            "setting. Dramatic long shadows, warm golden light, sharp architectural "
            "details, professional architectural photography style."
        ),
    },
    {
        "label": "The Overhang",
        "filename": "variant_1.png",
        "prompt": (
            "Photorealistic 8K architectural rendering, aerial three-quarter angle "
            "view, golden hour warm light. A modern recreation center with a clean "
            "white concrete and glass three-story horizontal base building along a "
            "city boulevard. From one end, a massive 25-meter-tall climbing wall "
            "structure in warm honey-toned Douglas fir cross-laminated timber leans "
            "dramatically outward over the street at a 30-degree overhang, "
            "cantilevered 12 meters beyond the building. The timber climbing surface "
            "has a faceted origami-like geometry of angled planes with earth-toned "
            "climbing holds. A public plaza sheltered beneath the overhang with grey "
            "granite pavers and ornamental grasses. A rooftop infinity pool on the "
            "main building catches golden light. Mature street trees casting long "
            "shadows. Small figures of climbers on the wall and pedestrians below "
            "looking up. Urban setting with adjacent buildings. Dramatic warm golden "
            "hour light, sharp shadows, professional architectural photography "
            "composition."
        ),
    },
    {
        "label": "The Spine",
        "filename": "variant_2.png",
        "prompt": (
            "Photorealistic 8K architectural rendering, aerial three-quarter angle "
            "view, golden hour warm light. A sleek 30-story mixed-use tower with "
            "dark bronze glass curtain wall. Running the full height of the south "
            "facade is a 6-meter-wide vertical climbing spine made of light warm "
            "grey sculpted precast concrete with deep rock-like relief texture. The "
            "glass curtain wall steps back 2 meters on each side of the spine "
            "creating a recessed canyon. Every 5th floor features an outdoor "
            "climbing terrace with stainless steel railings and wood decking "
            "protruding from the spine. Sculptural boulders on the rooftop garden. "
            "Ground level shows a double-height retail arcade with the spine "
            "beginning as a boulder garden. Tiny climbers visible on the spine at "
            "various heights. Golden sunset light reflecting off the glass, deep "
            "shadows in the concrete spine relief. Urban skyline context with other "
            "towers. Professional architectural photography, dramatic lighting, "
            "sharp detail."
        ),
    },
    {
        "label": "The Reef",
        "filename": "variant_3.png",
        "prompt": (
            "Photorealistic 8K architectural rendering, aerial three-quarter angle "
            "view, golden hour warm light. A low-slung organic community building "
            "whose entire exterior is a continuous sculptural bouldering surface "
            "with no straight lines. The building undulates like a coral reef, "
            "rising to 8 meters at the highest point and dipping to 2.5 meters at "
            "the lowest. The fiberglass shell has a gradient color from deep teal "
            "at the base through aquamarine to pale seafoam at the peaks, with an "
            "organic rock-like surface texture covered in bulges, pockets, and "
            "climbing features. Circular skylight domes puncture the shell like "
            "tidepools. Thick sand-colored rubber crash pad zones surround the "
            "entire building with organic curved edges. Set in a public park with "
            "scattered trees, native meadow grasses, and meandering crushed shell "
            "paths. Small figures of people climbing on every surface. Golden hour "
            "light casting warm shadows across the undulating form. Professional "
            "architectural photography, dreamlike quality, sharp details."
        ),
    },
]

# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------


def generate_image(prompt: str) -> bytes | None:
    """Call Gemini API and return PNG bytes."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }

    print(f"  -> Calling Gemini API ({len(prompt)} chars)...")
    resp = httpx.post(API_URL, json=body, timeout=120.0)

    if resp.status_code != 200:
        print(f"  X API error {resp.status_code}: {resp.text[:300]}")
        return None

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        print("  X No candidates in response")
        return None

    for part in candidates[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            b64 = part["inlineData"]["data"]
            return base64.b64decode(b64)

    print("  X No image in response")
    return None


def resize_and_crop(img_bytes: bytes, w: int, h: int) -> bytes:
    """Resize image to target dimensions, center-cropping if needed."""
    img = Image.open(io.BytesIO(img_bytes))
    ratio = max(w / img.width, h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    img = img.crop((left, top, left + w, top + h))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def main():
    _OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {_OUT_DIR}")
    print(f"Generating {len(VARIANTS)} variant images...\n")

    for i, variant in enumerate(VARIANTS):
        filename = variant["filename"]
        filepath = _OUT_DIR / filename

        if filepath.exists():
            print(f"[{i}] {variant['label']} -- already exists, skipping")
            continue

        print(f"[{i}] Generating {variant['label']}...")
        img_bytes = generate_image(variant["prompt"])

        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped)
            print(f"  OK Saved {filepath} ({len(cropped):,} bytes)")
        else:
            print(f"  X Failed to generate {variant['label']}")

        # Rate limit -- 8 seconds between requests
        if i < len(VARIANTS) - 1:
            print("  .. Waiting 8s for rate limit...")
            time.sleep(8)

    # Copy variant_0 as hero.png
    v0 = _OUT_DIR / "variant_0.png"
    hero = _OUT_DIR / "hero.png"
    if v0.exists() and not hero.exists():
        shutil.copy2(v0, hero)
        print(f"\nOK Copied variant_0.png -> hero.png")

    print("\nDone! Images saved to:", _OUT_DIR)


if __name__ == "__main__":
    main()
