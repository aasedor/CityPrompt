#!/usr/bin/env python3
"""
Test generating a Stephen Avenue card image using character reference
images from the City Prompt persona library.

Uses Gemini 3.1 Flash's Subject Consistency engine with up to 14
interleaved reference images.

Usage:
    python scripts/test_personas_in_scene.py
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
ENTOURAGE_DIR = PROJECT_ROOT / "frontend" / "public" / "entourage"
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

# Select 5 personas to include (Flash 3.1 tracks up to 5 human identities)
PERSONAS = [
    ("01_sarah_architect.png", "Sarah (the architect with coffee and portfolio)"),
    ("02_james_cyclist.png", "James (the cyclist with messenger bag and bicycle)"),
    ("04_marcus_dad.png", "Marcus and his young daughter in yellow raincoat"),
    ("08_elena_dog_walker.png", "Elena (the silver-haired woman walking a golden retriever)"),
    ("09_raj_cafe.png", "Raj (the man at the cafe with espresso and laptop)"),
]

SCENE_PROMPT = """Generate a photorealistic architectural visualization photograph of Calgary's Stephen Avenue pedestrian mall.

SCENE CONTEXT:
Heritage sandstone buildings (buff/golden Paskapoo sandstone, Richardsonian Romanesque arches with heavy stone voussoirs) line both sides of the pedestrian-only street. A glass-enclosed Plus-15 pedestrian bridge crosses overhead between modern office towers. Granite pavers on the ground. Young deciduous street trees. Cafe patios with umbrellas. Warm golden-hour afternoon sunlight from the left at 45 degrees casting long natural shadows. Rocky Mountain silhouette visible on the western horizon.

CHARACTER PLACEMENT — CRITICAL:
The reference images (Images 1-5) show specific fictional characters. You MUST include these EXACT characters in the scene, maintaining their precise facial features, hair, clothing, and accessories from the reference images:

- Image 1 (Sarah): Place her walking on the left side of the street in the mid-ground (~20m away), carrying her portfolio and coffee, walking toward the camera.
- Image 2 (James): Place him on the right side standing beside his bicycle near a street tree, in the mid-ground (~25m away), looking at his phone.
- Image 3 (Marcus + daughter): Place them walking together hand-in-hand in the center of the street, slightly closer to camera (~15m away). The daughter in yellow raincoat looking up at her father.
- Image 4 (Elena + golden retriever): Place her in the background (~35m away), walking the golden retriever along the right sidewalk near cafe patios.
- Image 5 (Raj): Place him seated at an outdoor cafe table on the left side, with his espresso and laptop, in the mid-ground (~20m away).

Keep the EXACT facial features, proportions, clothing, and accessories from each reference image. Adapt only the lighting to match the golden-hour scene conditions — warm directional sunlight from the left creating natural shadows on faces, with warm bounce light from sandstone buildings.

STYLISTIC CONSTRAINTS:
Photorealistic architectural visualization. Emphasize material textures — sandstone grain, glass reflections, fabric folds, hair catching light, dog fur texture. Natural color grading with warm tones.

PROHIBITIONS:
No deformed hands, no extra fingers, no floating figures, no figures intersecting architecture, no duplicate characters, no characters not from the reference images.

Shot on Canon EOS R5 with 35mm f/1.8 lens at golden hour. Natural depth of field. Kodak Portra 400 film stock color science. 8K resolution."""


def load_persona_image(filename: str) -> str:
    """Load a persona image and return base64-encoded data."""
    path = ENTOURAGE_DIR / filename
    if not path.exists():
        print(f"  WARNING: {filename} not found!")
        return ""
    img_bytes = path.read_bytes()
    return base64.b64encode(img_bytes).decode("utf-8")


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
    print("Testing Character Reference Library in Scene")
    print(f"Model: {MODEL} (with thinking mode)")
    print(f"Scene: Calgary Stephen Avenue")
    print(f"Personas: {len(PERSONAS)}")
    print()

    # Build the multimodal prompt with interleaved reference images
    parts = []

    # Add reference images first (as the paper recommends — context at the beginning)
    for i, (filename, description) in enumerate(PERSONAS):
        print(f"Loading persona {i+1}: {description}")
        img_b64 = load_persona_image(filename)
        if not img_b64:
            continue
        # Add image
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": img_b64,
            }
        })
        # Add label
        parts.append({
            "text": f"Image {i+1}: This is {description}. Maintain this exact character's facial features, hair, clothing, and accessories in the scene."
        })

    # Add the scene prompt at the end
    parts.append({"text": SCENE_PROMPT})

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.5,
            "thinkingConfig": {"thinkingBudget": 16384},  # Higher thinking for complex multi-character scene
        },
    }

    print(f"\nSending request with {len(PERSONAS)} reference images + scene prompt...")
    print("(This may take 60-90s with thinking mode on a complex multi-character scene)")

    try:
        resp = httpx.post(API_URL, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()

        image_bytes = None
        model_text = None
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    image_bytes = base64.b64decode(part["inlineData"]["data"])
                elif "text" in part:
                    model_text = part["text"]

        if not image_bytes:
            print("ERROR: No image returned")
            if model_text:
                print(f"Model said: {model_text[:500]}")
            # Check for safety blocks
            for candidate in data.get("candidates", []):
                fr = candidate.get("finishReason", "")
                if fr:
                    print(f"Finish reason: {fr}")
            return

        card_bytes = resize_to_card(image_bytes)
        output_path = OUTPUT_DIR / "style7_personas_in_scene.png"
        output_path.write_bytes(card_bytes)
        size_kb = len(card_bytes) / 1024
        print(f"\nOK - {size_kb:.0f} KB -> {output_path}")
        if model_text:
            print(f"Model notes: {model_text[:300]}")
        print("\nCompare with style6 (random fictional people) to see if personas are maintained!")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
