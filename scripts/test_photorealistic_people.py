#!/usr/bin/env python3
"""
Generate a test card image using photorealistic fictional people
with Gemini 3.1 Flash best practices from the Nano Banana 2 research paper.

Usage:
    python scripts/test_photorealistic_people.py
"""

import base64
import io
import sys
from pathlib import Path

import httpx
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / "backend" / ".env"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "people_style_tests"

def load_api_key() -> str:
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    print("ERROR: GEMINI_API_KEY not found")
    sys.exit(1)

API_KEY = load_api_key()
MODEL = "gemini-3.1-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

CARD_WIDTH = 1024
CARD_HEIGHT = 768

# Following the paper's "Taxonomy of Architectural Prompting":
# 1. Context first
# 2. Anchoring the query
# 3. Role definition & stylistic constraints
# 4. Spatial & anatomical directives (PRECISE, not vague)
# 5. Camera physics at the END (forces real-world rendering)

PROMPT = """Generate a photorealistic architectural visualization of Calgary's Stephen Avenue pedestrian mall.

SCENE CONTEXT:
Heritage sandstone buildings (buff/golden Paskapoo sandstone, Richardsonian Romanesque arches with heavy voussoirs) line both sides of the pedestrian-only street. A glass-enclosed Plus-15 pedestrian bridge crosses overhead between modern office towers. Granite pavers on the ground. Young deciduous street trees. Cafe patios with umbrellas. Warm golden-hour afternoon sunlight from the left at 45 degrees casting long, natural shadows. Rocky Mountain silhouette visible on the western horizon through the street canyon.

STYLISTIC CONSTRAINTS:
Render as a high-end professional architectural visualization photograph. Emphasize material textures throughout — visible sandstone grain, glass reflections, concrete texture, fabric folds on clothing, individual hair strands catching light. Natural color grading with warm tones. Slightly hazy atmospheric perspective increasing with distance.

HUMAN FIGURES — CRITICAL INSTRUCTIONS:
Include exactly 8 fictional human characters naturally inhabiting the scene. These are diverse, contemporary fictional people — NOT real individuals. Place all figures in the mid-ground and background (15-40 meters from camera), never extreme close-up foreground. Each figure must have:
- Anatomically correct proportions and natural posture
- Detailed, realistic facial features with proper eye symmetry
- Visible hair texture and natural skin tones with subsurface scattering from the warm sunlight
- Contemporary Canadian urban clothing appropriate for a warm summer evening
- Natural activities: a couple walking together, a person sitting at a cafe reading, two friends in conversation, a woman walking a golden retriever on a leash, a cyclist pushing their bike

Ensure each figure's lighting matches the scene — warm directional sunlight from the left creating natural facial shadows, bounce light from the sandstone buildings providing fill.

Include one golden retriever dog on a leash, rendered with the same photorealistic fidelity as the human figures — visible fur texture, natural pose, proper anatomical proportions.

PROHIBITIONS:
No deformed hands, no extra fingers, no floating figures, no figures intersecting with architecture, no uncanny valley plastic skin, no identical faces on different characters.

Shot on a Canon EOS R5 with a 35mm f/1.8 lens at golden hour. Natural depth of field with slight background bokeh. 35mm SLR photograph, Kodak Portra 400 film stock color science."""


def resize_to_card(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    img_ratio = img.width / img.height
    card_ratio = CARD_WIDTH / CARD_HEIGHT
    if img_ratio > card_ratio:
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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating Style 6: Photorealistic Fictional People (paper techniques)...")
    print(f"Model: {MODEL}")
    print(f"Using: camera physics, texture emphasis, fictional characters, mid-ground placement")
    print(f"Thinking mode: enabled via thinkingConfig")
    print()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.6,
            "thinkingConfig": {"thinkingBudget": 8192},
        },
    }

    try:
        print("Sending request (with thinking mode — may take 30-60s)...")
        resp = httpx.post(API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        image_bytes = None
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    image_bytes = base64.b64decode(part["inlineData"]["data"])
                    break

        if not image_bytes:
            print("ERROR: No image returned")
            # Print any text response for debugging
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "text" in part:
                        print(f"Model said: {part['text'][:500]}")
            return

        card_bytes = resize_to_card(image_bytes)
        output_path = OUTPUT_DIR / "style6_photorealistic_fictional.png"
        output_path.write_bytes(card_bytes)
        size_kb = len(card_bytes) / 1024
        print(f"OK - {size_kb:.0f} KB -> {output_path}")
        print(f"\nCompare with the watercolor wash version side by side!")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
