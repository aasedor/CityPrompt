"""
Generate Elevated Rail Transit archetype images using Gemini 3 Pro.

Generates 4 variant images and saves to
frontend/public/archetypes/streets/elevated-rail-transit/
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
    / "streets"
    / "elevated-rail-transit"
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
        "label": "Parametric Flow Station",
        "filename": "variant_0.png",
        "prompt": (
            "Cinematic aerial photograph at 3/4 bird's-eye angle of a futuristic "
            "parametric elevated rail station inspired by Zaha Hadid's Napoli-Afragola, "
            "golden hour warm lighting. A sweeping 300-meter elevated transit concourse "
            "with a flowing double-curved white Corian-clad roof supported by 200 "
            "differently shaped steel ribs, creating an organic undulating form that "
            "serves as both station and pedestrian bridge spanning eight railway tracks. "
            "The parametric facade features geometric perforations in the white composite "
            "panels creating intricate dappled light patterns on the platforms below. "
            "Glass roof sections flood the interior with golden light. The station curves "
            "sinuously through a contemporary urban district of 6-10 story glass and stone "
            "buildings. Slender white concrete piers with tapered profiles support the "
            "elevated structure. A modern light rail train in silver with blue accent "
            "stripe approaches the station. Below the elevated concourse, a landscaped "
            "public plaza with geometric paving patterns, water features, and rows of "
            "ornamental trees connects the station to the surrounding streets. The white "
            "surfaces glow warmly in the golden hour light while deep shadows reveal the "
            "complex geometry of the perforated facade. Pedestrians visible on the elevated "
            "walkway and plaza below. Ultra-high quality architectural photography, 8K "
            "resolution, photorealistic."
        ),
    },
    {
        "label": "Structural Poetry",
        "filename": "variant_1.png",
        "prompt": (
            "Cinematic aerial photograph at 3/4 bird's-eye angle of a Santiago "
            "Calatrava-inspired elevated rail station with dramatic white structural "
            "expressionism, golden hour warm lighting. A soaring open-air station where "
            "tree-like branching white-painted steel columns rise 25 meters and split into "
            "interlocking curved canopy ribs, forming a transparent forest-like roof "
            "structure over the elevated platforms. The structural ribs create a "
            "cathedral-like volume with no traditional walls — the architecture is pure "
            "structure. Tempered glass panels fill between the steel ribs, creating a "
            "luminous canopy that shelters the platforms while remaining visually "
            "transparent. Cable-stayed elements connect the canopy to slender inclined "
            "masts. The elevated guideway approaches on a graceful white concrete viaduct "
            "with V-shaped piers. A sleek modern train in white sits at the platform. "
            "Below the station, the open ground plane features polished stone paving, "
            "reflecting pools, and a grove of tall palm trees whose natural branching "
            "echoes the structural columns above. The white steel catches the golden hour "
            "light creating warm amber highlights while the shadows between ribs create "
            "dramatic rhythmic patterns on the platform. 6-8 story contemporary buildings "
            "visible in the background. Ultra-high quality architectural photography, 8K "
            "resolution, photorealistic."
        ),
    },
    {
        "label": "Living Viaduct",
        "filename": "variant_2.png",
        "prompt": (
            "Cinematic aerial photograph at 3/4 bird's-eye angle of a futuristic green "
            "elevated rail transit line with split-track design and activated linear park "
            "beneath, golden hour warm lighting. Two separate slender concrete guideway "
            "beams are separated by a 4-meter gap allowing sunlight and rain to reach the "
            "vibrant park below. Sculptural white V-shaped tree-form concrete piers "
            "support the split beams, their organic branching forms echoing natural "
            "canopies. Mature trees grow in the gap between the split tracks, their green "
            "canopies reaching up toward the guideway. A flowing pod-shaped station with a "
            "parametrically curved roof of perforated bronze-toned anodized aluminum "
            "panels glows warmly, with building-integrated photovoltaic glass sections. "
            "Platform screen doors in curved glass. Below the split viaduct, a vibrant "
            "linear park contains multi-use sports courts in blue and terracotta rubber "
            "surfacing, an adventure playground, bioswale rain gardens with ornamental "
            "grasses and Purple Coneflower fed by viaduct stormwater runoff, a "
            "green-surfaced cycling path, and illuminated public art installations on the "
            "sculptural pier columns. Warm LED accent lighting along pier bases creates an "
            "inviting atmosphere. Modern 6-8 story residential buildings with planted "
            "balconies line both sides of the corridor. A sleek silver-and-green liveried "
            "train glides along the guideway. Ultra-high quality architectural photography, "
            "8K resolution, photorealistic."
        ),
    },
    {
        "label": "Floating Ribbon",
        "filename": "variant_3.png",
        "prompt": (
            "Cinematic aerial photograph at 3/4 bird's-eye angle of an ultra-lightweight "
            "elevated rail guideway appearing to float above a contemporary urban "
            "boulevard, golden hour transitioning to blue hour with station glowing as a "
            "civic lantern. An impossibly slender aerodynamic concrete guideway ribbon, "
            "just 1.2 meters deep, is supported by tapered white steel columns spaced 80 "
            "meters apart with cable-stay supports fanning from each column top, creating "
            "a harp-like structural pattern. The guideway appears to levitate — its minimal "
            "visual weight barely interrupts the sky. A glass-enclosed station glows warmly "
            "from within like a luminous jewel box — slender tubular white steel columns "
            "support a mass-timber roof deck visible through bird-friendly fritted glass "
            "panels that act as angled louvers. Stainless steel spider fittings connect the "
            "glass to the structure. Inside, warm wood ceiling and platform furniture are "
            "visible through the transparent walls. A sleek automated train in pearl white "
            "approaches the glowing station. Below, the wide boulevard is fully intact with "
            "mature London Plane trees, separated bike lanes, cafe terraces, and active "
            "street life completely unimpeded by the elevated structure. The thin guideway "
            "casts only a narrow shadow line. The sky transitions from golden amber at the "
            "horizon to deep blue overhead, and the station radiates warm amber light. "
            "Ultra-high quality architectural photography, 8K resolution, photorealistic."
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
            print(f"[{i}] {variant['label']} — already exists, skipping")
            continue

        print(f"[{i}] Generating {variant['label']}...")
        img_bytes = generate_image(variant["prompt"])

        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped)
            print(f"  OK Saved {filepath} ({len(cropped):,} bytes)")
        else:
            print(f"  X Failed to generate {variant['label']}")

        # Rate limit — 6 seconds between requests
        if i < len(VARIANTS) - 1:
            print("  .. Waiting 6s for rate limit...")
            time.sleep(6)

    # Copy variant_0 as hero.png
    v0 = _OUT_DIR / "variant_0.png"
    hero = _OUT_DIR / "hero.png"
    if v0.exists() and not hero.exists():
        shutil.copy2(v0, hero)
        print(f"\nOK Copied variant_0.png -> hero.png")

    print("\nDone! Images saved to:", _OUT_DIR)


if __name__ == "__main__":
    main()
