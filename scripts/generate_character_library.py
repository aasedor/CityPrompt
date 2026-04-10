#!/usr/bin/env python3
"""
Generate a library of 10 fictional character references for City Prompt.
These will be used as consistent entourage across all archetype card images.

Each character is generated as a full-body portrait with clear facial features,
clothing, and personality — designed to be reused via reference image injection.

Usage:
    python scripts/generate_character_library.py
"""

import base64
import io
import sys
import time
from pathlib import Path

import httpx
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / "backend" / ".env"
OUTPUT_DIR = PROJECT_ROOT / "frontend" / "public" / "entourage"

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


# 10 diverse fictional characters representing a cross-section of urban life
CHARACTERS = [
    {
        "id": "sarah_architect",
        "filename": "01_sarah_architect.png",
        "prompt": (
            "Full-body portrait photograph of a fictional female architect in her early 30s. "
            "She has shoulder-length dark brown wavy hair, warm olive skin tone, and brown eyes. "
            "Wearing a tailored charcoal blazer over a white crew-neck t-shirt, dark indigo slim jeans, "
            "and clean white sneakers. She carries a large black portfolio case under one arm and holds "
            "a takeaway coffee cup in the other hand. Confident, purposeful walking pose. "
            "Slight smile, looking ahead. "
        ),
    },
    {
        "id": "james_cyclist",
        "filename": "02_james_cyclist.png",
        "prompt": (
            "Full-body portrait photograph of a fictional male urban cyclist in his late 20s. "
            "He has short curly auburn hair, fair freckled skin, and blue-green eyes. "
            "Wearing a fitted olive green rain jacket (unzipped), a navy henley shirt underneath, "
            "slim dark grey chinos, and brown leather ankle boots. He is standing beside a single-speed "
            "bicycle with his right hand on the handlebar, wearing a messenger bag across his chest. "
            "Relaxed, casual stance. Looking slightly to the left with a friendly expression. "
        ),
    },
    {
        "id": "priya_student",
        "filename": "03_priya_student.png",
        "prompt": (
            "Full-body portrait photograph of a fictional South Asian female university student in her early 20s. "
            "She has long straight black hair pulled into a loose low ponytail, warm brown skin, and dark brown eyes. "
            "Wearing a rust-orange oversized knit cardigan over a cream camisole, high-waisted light wash jeans, "
            "and white canvas platform sneakers. She has a canvas tote bag on one shoulder with books visible inside, "
            "and is looking at her phone with a slight smile. Natural, candid pose. "
        ),
    },
    {
        "id": "marcus_dad",
        "filename": "04_marcus_dad.png",
        "prompt": (
            "Full-body portrait photograph of a fictional Black Canadian father in his late 30s. "
            "He has a short, well-groomed beard and close-cropped natural hair, dark brown skin, and warm brown eyes. "
            "Wearing a denim jacket over a burgundy crewneck sweater, khaki chinos, and clean white trainers. "
            "He is holding the hand of a young daughter (about 5 years old, similar features, wearing a yellow "
            "raincoat and small rain boots) who is looking up at him. He is smiling down at her. "
            "Warm, tender parental moment. "
        ),
    },
    {
        "id": "mei_professional",
        "filename": "05_mei_professional.png",
        "prompt": (
            "Full-body portrait photograph of a fictional East Asian professional woman in her mid-40s. "
            "She has a sleek black bob haircut with subtle highlights, light skin, and dark brown eyes behind "
            "thin gold-rimmed glasses. Wearing a camel wool coat (knee-length, belted), a cream silk blouse "
            "underneath, tailored navy trousers, and pointed black leather flats. She carries a structured "
            "leather handbag and is walking with composed, elegant posture. "
            "Poised, intelligent expression. "
        ),
    },
    {
        "id": "omar_elder",
        "filename": "06_omar_elder.png",
        "prompt": (
            "Full-body portrait photograph of a fictional Middle Eastern elderly gentleman in his early 70s. "
            "He has a neatly trimmed white beard and silver hair, tan weathered skin with laugh lines, "
            "and kind dark eyes. Wearing a well-fitted grey herringbone sport coat over a light blue "
            "button-down shirt (no tie), dark navy trousers, and polished brown oxford shoes. "
            "He is sitting on a park bench reading a newspaper, with a wooden walking cane leaning beside him. "
            "Dignified, peaceful, scholarly demeanor. "
        ),
    },
    {
        "id": "alex_runner",
        "filename": "07_alex_runner.png",
        "prompt": (
            "Full-body portrait photograph of a fictional non-binary jogger in their mid-20s. "
            "They have a short textured fade haircut dyed platinum blonde, medium brown skin, and hazel eyes. "
            "Wearing black running leggings, a bright teal technical running top, and grey running shoes. "
            "They have wireless earbuds in and are captured mid-stride in a natural running pose on a pathway. "
            "Athletic, energetic expression. Slight motion blur on feet to convey movement. "
        ),
    },
    {
        "id": "elena_dog_walker",
        "filename": "08_elena_dog_walker.png",
        "prompt": (
            "Full-body portrait photograph of a fictional Eastern European woman in her late 50s. "
            "She has chin-length silver-grey hair with a natural wave, fair skin with smile lines, and grey-blue eyes. "
            "Wearing a forest green quilted vest over a cream cable-knit sweater, dark jeans, and waterproof "
            "brown hiking boots. She is walking a large golden retriever on a leather leash, with the dog "
            "looking up at her happily. She has a warm, content smile. Outdoor, pathway setting. "
        ),
    },
    {
        "id": "raj_cafe",
        "filename": "09_raj_cafe.png",
        "prompt": (
            "Full-body portrait photograph of a fictional South Asian male cafe patron in his early 30s. "
            "He has thick dark hair styled in a modern side part, warm brown skin, and a neatly trimmed short beard. "
            "Wearing a fitted navy peacoat over a striped Breton shirt, slim dark jeans, and tan suede desert boots. "
            "He is seated at a small round outdoor cafe table with an espresso cup and a laptop open in front of him. "
            "Thoughtful expression, looking slightly away from the laptop. "
        ),
    },
    {
        "id": "linnea_skater",
        "filename": "10_linnea_skater.png",
        "prompt": (
            "Full-body portrait photograph of a fictional Scandinavian-Canadian teenage girl, about 16 years old. "
            "She has long straight strawberry blonde hair, pale skin with a few freckles, and light blue eyes. "
            "Wearing an oversized vintage band t-shirt tucked into high-waisted mom jeans, beat-up Converse "
            "high-tops, and a small backpack. She is standing with one foot on a skateboard, the other on the ground, "
            "casually looking at the camera with a relaxed half-smile. Youthful, confident energy. "
        ),
    },
]

# Shared style suffix — camera physics at the END per the paper's recommendation
STYLE_SUFFIX = (
    "The subject is standing/positioned on a neutral light grey concrete surface with a clean, "
    "slightly blurred urban background (out of focus buildings and trees). "
    "Emphasize realistic skin texture with visible pores, natural hair texture with individual strands "
    "catching the light, and authentic fabric textures on clothing. "
    "Natural subsurface scattering on skin from warm afternoon sunlight from the upper left. "
    "This is a fictional character created for architectural visualization — not a real person. "
    "Full body visible from head to feet with approximately 15% headroom above. "
    "Shot on a Canon EOS R5 with an 85mm f/1.8 portrait lens. Natural depth of field. "
    "35mm SLR photograph, Kodak Portra 400 film stock color science. "
    "8K resolution, photorealistic, editorial portrait photography quality."
)


def resize_portrait(image_bytes: bytes, width: int = 512, height: int = 768) -> bytes:
    """Resize to portrait format for character reference."""
    img = Image.open(io.BytesIO(image_bytes))
    img_ratio = img.width / img.height
    target_ratio = width / height
    if img_ratio > target_ratio:
        new_height = height
        new_width = int(img.width * (height / img.height))
    else:
        new_width = width
        new_height = int(img.height * (width / img.width))
    img = img.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    img = img.crop((left, top, left + width, top + height))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_character(prompt: str) -> bytes | None:
    full_prompt = prompt + "\n\n" + STYLE_SUFFIX
    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.5,
            "thinkingConfig": {"thinkingBudget": 8192},
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
        # Check for safety blocks
        for candidate in data.get("candidates", []):
            if candidate.get("finishReason") == "SAFETY":
                print("  SAFETY BLOCK - adjusting prompt...")
                return None
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    print(f"  Model text: {part['text'][:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating City Prompt Character Library")
    print(f"Model: {MODEL} (with thinking mode)")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Characters: {len(CHARACTERS)}")
    print(f"{'=' * 50}")
    print()

    success = 0
    failed = 0

    for i, char in enumerate(CHARACTERS):
        print(f"[{i+1}/{len(CHARACTERS)}] Generating {char['id']}...")
        output_path = OUTPUT_DIR / char["filename"]

        if output_path.exists():
            print(f"  SKIP - already exists")
            success += 1
            continue

        image_bytes = generate_character(char["prompt"])
        if not image_bytes:
            print(f"  FAILED - no image returned")
            failed += 1
            # Wait before retry/next
            time.sleep(3)
            continue

        portrait_bytes = resize_portrait(image_bytes)
        output_path.write_bytes(portrait_bytes)
        size_kb = len(portrait_bytes) / 1024
        print(f"  OK - {size_kb:.0f} KB -> {char['filename']}")
        success += 1

        # Rate limit between generations
        time.sleep(3)

    print(f"\n{'=' * 50}")
    print(f"Results: {success} success, {failed} failed")
    print(f"Character library: {OUTPUT_DIR}")
    print()
    print("Characters generated:")
    for char in CHARACTERS:
        path = OUTPUT_DIR / char["filename"]
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {char['id']}: {char['filename']}")


if __name__ == "__main__":
    main()
