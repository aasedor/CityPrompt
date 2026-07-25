#!/usr/bin/env python3
"""
Generate 5 test card images with different people silhouette styles.
Uses Calgary Stephen Avenue as the test scene.

Usage:
    python scripts/test_people_styles.py
"""

import base64
import io
import json
import sys
import time
from pathlib import Path

import httpx
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / "backend" / ".env"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "people_style_tests"

# Load API key
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

# The base scene (same for all 5)
BASE_SCENE = (
    "A photorealistic architectural visualization of Calgary's Stephen Avenue pedestrian mall. "
    "Heritage sandstone buildings (buff/golden Paskapoo sandstone, Romanesque arches) line both sides. "
    "Plus-15 glass pedestrian bridges cross overhead between modern office towers. "
    "Granite pavers, street trees, cafe patios with umbrellas. "
    "Warm golden-hour afternoon sunlight from the left at 45 degrees. "
    "Sharp detail on sandstone texture, glass reflections, concrete grain. "
    "Rocky Mountain backdrop visible on the western horizon. "
    "Wide-angle street-level perspective, 4:3 aspect ratio, 8K detail."
)

STYLES = {
    "style1_flat_pastel": {
        "label": "Style 1: Flat Pastel Silhouettes",
        "people_prompt": (
            "The scene contains 8-12 human figures. "
            "Every human figure MUST be a flat-color semi-transparent silhouette in soft muted pastel tones "
            "(light cyan #8ED8D8, warm peach #F5B895, soft mint #A8D5BA, dusty rose #D4A0A0, lavender #B8A9C9). "
            "These are simple solid-color cutout shapes with NO facial features, NO skin texture, "
            "NO clothing detail, NO anatomical features. Just flat translucent colored shapes "
            "like architectural competition render silhouettes. "
            "Place them naturally: walking on sidewalks, sitting at cafe tables, standing in conversation pairs. "
            "Do NOT generate any realistic or semi-realistic human beings."
        ),
    },
    "style2_monochrome_ink": {
        "label": "Style 2: Monochrome Ink Silhouettes",
        "people_prompt": (
            "The scene contains 8-12 human figures. "
            "Every human figure MUST be a solid dark charcoal grey (#444444) silhouette. "
            "Slightly more detailed than flat shapes -- you can see posture, hair outline, and general clothing shape, "
            "but NO facial features, NO skin color, NO texture. Just dark grey solid shapes. "
            "All figures are the same dark charcoal color. Clean, minimal, professional. "
            "Place them naturally: walking, sitting at cafes, standing in pairs. "
            "Think Foster + Partners architectural diagram style. "
            "Do NOT generate any realistic human beings."
        ),
    },
    "style3_white_lineart": {
        "label": "Style 3: White Line-Art Figures",
        "people_prompt": (
            "The scene contains 8-12 human figures. "
            "Every human figure MUST be rendered as a simple line drawing -- thin black or dark grey outlines "
            "with NO fill color. Just clean architectural line-art of human figures showing posture and basic form. "
            "Like CAD block people or architectural section-cut figures. "
            "No shading, no color, no realistic detail -- just clean contour lines. "
            "Place them naturally: walking, sitting, standing. "
            "Think architectural drawing / pimpmydrawing.com style. "
            "Do NOT generate any realistic or filled-in human figures."
        ),
    },
    "style4_watercolor_wash": {
        "label": "Style 4: Watercolor Wash Figures",
        "people_prompt": (
            "The scene contains 8-12 human figures. "
            "Every human figure MUST be rendered as a loose watercolor wash -- soft, artistic splashes of color "
            "suggesting human form without precise detail. Soft edges, color bleeding, painterly quality. "
            "Use warm earth tones and muted colors (ochre, burnt sienna, indigo, sage green). "
            "Each figure is a small artistic splash of color suggesting a person walking or standing. "
            "NO photorealistic humans, NO precise facial features, NO sharp edges on figures. "
            "Think Alex Hogrefe / Visualizing Architecture render style. "
            "Place them naturally on sidewalks and at cafe tables."
        ),
    },
    "style5_posterized_cutout": {
        "label": "Style 5: Posterized Artistic Cutouts",
        "people_prompt": (
            "The scene contains 8-12 human figures. "
            "Every human figure should have natural human proportions and realistic poses, "
            "but rendered with a posterized/illustrated filter -- reduced to 4-5 flat color tones per figure, "
            "with slightly simplified features. Like a stylized editorial illustration of people. "
            "Visible clothing styles and diversity, but with an illustrated/graphic quality, NOT photorealistic. "
            "Slightly desaturated colors. Clean edges. "
            "Think MVRDV architectural presentation style -- real enough to read as people, "
            "stylized enough to not be uncanny. "
            "Place them naturally: walking, sitting at cafes, looking at shops."
        ),
    },
}


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


def generate_image(prompt: str) -> bytes | None:
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.7,
        },
    }
    try:
        resp = httpx.post(API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
    except Exception as e:
        print(f"  ERROR: {e}")
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating 5 people style test images...")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Model: {MODEL}")
    print()

    for style_id, style in STYLES.items():
        print(f"Generating {style['label']}...")
        prompt = f"{BASE_SCENE}\n\n{style['people_prompt']}"

        image_bytes = generate_image(prompt)
        if not image_bytes:
            print(f"  FAILED - no image returned")
            continue

        card_bytes = resize_to_card(image_bytes)
        output_path = OUTPUT_DIR / f"{style_id}.png"
        output_path.write_bytes(card_bytes)
        size_kb = len(card_bytes) / 1024
        print(f"  OK - {size_kb:.0f} KB -> {output_path.name}")

        # Rate limit
        time.sleep(2)

    print(f"\nDone! Check {OUTPUT_DIR} for the 5 test images.")
    print("Compare them side by side and pick your preferred style.")


if __name__ == "__main__":
    main()
