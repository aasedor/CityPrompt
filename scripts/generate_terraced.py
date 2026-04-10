"""
Generate 4 terraced/stepped building variant images using Gemini 3 Pro.
Creates variant_0..3.png + hero.png (copy of variant_0) in the archetype folder.
"""

import base64, json, os, shutil, sys, time
from pathlib import Path

import httpx

# ── paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / "backend" / ".env"
OUT_DIR = ROOT / "frontend" / "public" / "archetypes" / "buildings" / "terraced_stepped_building"

# ── load API key from .env ─────────────────────────────────────────────
def load_env(path: Path) -> dict[str, str]:
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env

env = load_env(ENV_FILE)
API_KEY = env["GEMINI_API_KEY"]

# ── Gemini endpoint ───────────────────────────────────────────────────
MODEL = "gemini-3-pro-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# ── prompts ───────────────────────────────────────────────────────────
PROMPTS = [
    # variant_0 — "The Ridgeline"
    (
        "Photorealistic architectural photograph, aerial 3/4 view, golden hour warm light, 8K resolution. "
        "A bold geometric stepped residential building approximately 10 stories tall with an asymmetric mountain-like profile. "
        "The north face is a sheer wall of dark charcoal brick, the south face cascades down in wide terraced steps from 12 stories to 4 stories. "
        "Each terrace step is 4-5 meters deep with light oak timber decking, ornamental grasses in Corten steel planters, silver birch trees, and modern outdoor furniture. "
        "Pale concrete terrace floors. Black steel mesh railings. Central courtyard at base with birch grove visible from above. "
        "Rooftop solar panels on highest terrace. Surrounding urban context with lower buildings. Long golden shadows cast across the terraces. "
        "Professional architectural photography style, sharp detail, Scandinavian-inspired minimalism."
    ),
    # variant_1 — "The Canopy Tower"
    (
        "Photorealistic architectural photograph, aerial 3/4 view, golden hour warm light, 8K resolution. "
        "A 20-story residential tower covered in lush vegetation creating a vertical forest effect. "
        "White precast concrete structure with staggered asymmetric balconies projecting 3.5 meters outward, each overflowing with mature trees, shrubs, and cascading vines. "
        "Japanese maples with red foliage, stone pines, holm oaks, cascading wisteria and Boston ivy draping between levels. "
        "Slightly rounded organic building footprint with two indented sky-gardens at mid-height creating sheltered micro-gardens. "
        "Top three floors step back with larger mature trees silhouetted against golden sky. Ground level colonnade opening to public garden. "
        "Deep green foliage contrasting with white concrete. Surrounding urban context with glass and steel buildings. "
        "Warm directional golden hour light catching the canopy tops, deep shadows within the foliage. "
        "Professional architectural photography, biophilic architecture."
    ),
    # variant_2 — "The Hillside Quarter"
    (
        "Photorealistic architectural photograph, aerial 3/4 view, golden hour warm light, 8K resolution. "
        "A low-rise Mediterranean-inspired terraced housing complex of 3-5 stories stepping down an artificial hillside. "
        "White-washed cubic volumes with lime-rendered walls, each offset from its neighbor creating private courtyards and planted terraces. "
        "Terracotta roof tiles in warm ochre and sienna tones. Vivid magenta and purple bougainvillea cascading over courtyard walls. "
        "Olive trees and Italian cypress trees punctuating the composition. "
        "Narrow limestone-paved pedestrian lanes winding between buildings, opening into small communal plazas with water features. "
        "Blue-painted wooden shutters and doors. Potted lemon trees and geraniums on terraces. Jasmine climbing over timber pergolas. "
        "Communal swimming pool on the lowest terrace reflecting golden sky. "
        "Warm Mediterranean light with deep shadows in the narrow lanes. "
        "Professional architectural photography, warm color palette, human-scale village atmosphere."
    ),
    # variant_3 — "The Cascade Podium"
    (
        "Photorealistic architectural photograph, aerial 3/4 view, golden hour warm light, 8K resolution. "
        "A 6-story mixed-use terraced building with transparent glass commercial base of 2 stories and 4 residential floors stepping back progressively on all sides. "
        "Each setback creates deep planted rooftop garden terraces 6-8 meters wide. "
        "Dark bronze anodized aluminum frames and vertical Western red cedar timber screens on upper residential floors. "
        "Third floor communal terrace visible with urban farming plots, play area, and yoga deck. "
        "Higher private terraces with structured planting: formal box hedging at edges, wild meadow flowers purple salvia, yellow achillea, echinops and small ornamental trees amelanchier, dogwood in centers. "
        "Sedum green roof on topmost level. Perforated Corten steel public staircase climbing one corner from ground to roof. "
        "Ground floor food hall activity visible through full-height glass. "
        "Large grey porcelain paver terrace surfaces with timber boardwalk sections. "
        "Warm golden hour light creating long shadows across terraced levels. Surrounding mid-rise urban context. "
        "Professional architectural photography, sophisticated material palette."
    ),
]

VARIANT_NAMES = ["The Ridgeline", "The Canopy Tower", "The Hillside Quarter", "The Cascade Podium"]

# ── generate ──────────────────────────────────────────────────────────
def generate_image(prompt: str, out_path: Path, label: str, client: httpx.Client) -> bool:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }
    print(f"\n{'='*60}")
    print(f"Generating: {label}")
    print(f"  -> {out_path.name}")

    try:
        resp = client.post(URL, json=body, timeout=120)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"  ERROR {exc.response.status_code}: {exc.response.text[:300]}")
        return False
    except httpx.RequestError as exc:
        print(f"  REQUEST ERROR: {exc}")
        return False

    data = resp.json()

    # find inlineData part
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                out_path.write_bytes(img_bytes)
                print(f"  OK  ({len(img_bytes):,} bytes)")
                return True

    print(f"  WARNING: no inlineData found in response")
    # dump keys for debugging
    print(f"  response keys: {list(data.keys())}")
    if "candidates" in data:
        for ci, c in enumerate(data["candidates"]):
            parts = c.get("content", {}).get("parts", [])
            print(f"  candidate[{ci}] parts: {[list(p.keys()) for p in parts]}")
    return False


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUT_DIR}")

    ok_count = 0
    with httpx.Client() as client:
        for i, (prompt, label) in enumerate(zip(PROMPTS, VARIANT_NAMES)):
            out_path = OUT_DIR / f"variant_{i}.png"
            success = generate_image(prompt, out_path, label, client)
            if success:
                ok_count += 1
            if i < len(PROMPTS) - 1:
                print(f"  Waiting 8 seconds...")
                time.sleep(8)

    # hero.png = copy of variant_0
    v0 = OUT_DIR / "variant_0.png"
    hero = OUT_DIR / "hero.png"
    if v0.exists():
        shutil.copy2(v0, hero)
        print(f"\nCopied variant_0.png -> hero.png")

    print(f"\nDone: {ok_count}/{len(PROMPTS)} images generated successfully.")
    if ok_count < len(PROMPTS):
        sys.exit(1)


if __name__ == "__main__":
    main()
