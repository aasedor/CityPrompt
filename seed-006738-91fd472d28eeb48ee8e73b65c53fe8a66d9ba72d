"""
Generate Collegiate Gothic archetype card images using Gemini API.

Generates 4 variant images (Tudor Gothic, Jacobethan, Perpendicular Revival, Ruskinian Gothic)
at 1024x768 and saves to frontend/public/archetypes/buildings/collegiate_gothic_education/
"""

from __future__ import annotations

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
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"

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
MODEL = "gemini-2.5-flash-image"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

STYLE_ANCHOR = (
    "Style: photorealistic architectural visualization, high-end 3D rendering "
    "quality like a professional archviz studio. Warm golden-hour afternoon "
    "sunlight from the left at roughly 45 degrees, casting soft natural shadows. "
    "Slightly hazy atmospheric perspective in the background. Natural color "
    "grading with warm tones. Sharp detail on materials and textures — visible "
    "stone courses, glass reflections, carved ornament detail, metal patina. "
    "Photorealistic, 8K detail, architectural photography composition."
)

NO_PEOPLE = (
    "Absolutely no people, no human figures, no pedestrians, no silhouettes, "
    "no crowds anywhere in the scene. The scene is completely empty of humans."
)

# ---------------------------------------------------------------------------
# Variant definitions
# ---------------------------------------------------------------------------

VARIANTS = [
    {
        "id": "collegiate_gothic_tudor",
        "label": "Tudor Gothic",
        "filename": "variant_0.png",
        "description": (
            "Tudor Gothic university building. A grand collegiate quadrangle entrance "
            "with a square gatehouse tower topped with crenellated battlements. "
            "Facade of honey-colored limestone ashlar with four-centred (flat pointed) Tudor arches "
            "over the main entrance and windows. Tall mullioned and transomed windows with "
            "leaded diamond-pane glass. Projecting oriel windows on upper floors supported by "
            "carved stone corbels. Crenellated parapets along the roofline giving a castle-like "
            "silhouette. Heraldic shields carved above the main archway. Steeply pitched slate "
            "roof with ornate clustered chimney stacks. Dark slate roofing. "
            "Surrounding context: enclosed grass quadrangle with gravel paths, mature oak trees. "
            "Inspired by Magdalen College Oxford and Yale's Memorial Quadrangle."
        ),
        "facadeDetail": {
            "primaryMaterial": "honey-colored limestone ashlar, Cotswold stone",
            "secondaryMaterial": "carved limestone door surrounds with Tudor rose motifs",
            "accentMaterial": "leaded diamond-pane windows in iron frames",
            "groundFloor": "four-centred Tudor arch gatehouse entrance with carved heraldic shields, heavy oak doors with iron studs",
            "upperFloors": "tall mullioned and transomed windows with hood mouldings, projecting oriel windows on corbels",
            "cornice": "crenellated battlemented parapet with corner turrets",
            "colorScheme": "warm honey limestone, dark slate roof, dark oak doors, lead-grey window frames"
        },
        "roofDetail": {
            "form": "steeply pitched gable behind crenellated parapet",
            "material": "dark Welsh slate",
            "features": "clustered octagonal chimney stacks, corner pinnacles, gargoyle downspouts",
            "aerialAppearance": "dark slate with prominent chimney clusters and stone battlemented parapets"
        },
        "palette": {"primary": "#C4A55A"}
    },
    {
        "id": "collegiate_gothic_jacobethan",
        "label": "Jacobethan",
        "filename": "variant_1.png",
        "description": (
            "Jacobethan university building. A grand symmetrical facade in rich red brick "
            "with contrasting pale limestone dressings. The roofline is defined by elaborate "
            "shaped Dutch gables with curved S-scroll profiles topped with stone obelisk finials. "
            "Very large mullioned and transomed windows in grids of rectangular lights filling "
            "most of the wall surface, with leaded diamond-lattice glazing. A central entrance "
            "porch with classical Renaissance columns and a round arch, mixing Gothic and "
            "classical elements. Decorative strapwork carved panels on gable ends and parapets — "
            "interlaced ornamental bands in pale stone against red brick. Ornate stone balustrades "
            "along the roofline between the gables. Tall ornamental chimney stacks with "
            "diagonally-set brick flues. Steeply pitched roof with slate tiles. "
            "Surrounding context: formal gardens with geometric hedges and a paved courtyard. "
            "Inspired by Royal Holloway College and Hobart College."
        ),
        "facadeDetail": {
            "primaryMaterial": "rich warm red brick in Flemish bond",
            "secondaryMaterial": "pale Portland stone window surrounds, quoins, and strapwork panels",
            "accentMaterial": "stone obelisk finials, carved balustrades",
            "groundFloor": "central entrance porch with classical columns and round arch, stone steps",
            "upperFloors": "very large mullioned and transomed window grids with diamond-lattice leaded glass, strapwork panels between floors",
            "cornice": "stone balustrade parapet with shaped Dutch gables and obelisk finials",
            "colorScheme": "rich red brick, pale cream stone dressings, dark slate roof"
        },
        "roofDetail": {
            "form": "steeply pitched with multiple shaped Dutch gables",
            "material": "dark slate tiles",
            "features": "ornamental chimney stacks with diagonally-set flues, stone obelisk finials on gable peaks",
            "aerialAppearance": "dark slate with prominent shaped gable profiles and tall decorative chimneys"
        },
        "palette": {"primary": "#8B3A3A"}
    },
    {
        "id": "collegiate_gothic_perpendicular",
        "label": "Perpendicular Revival",
        "filename": "variant_2.png",
        "description": (
            "Perpendicular Gothic Revival university building. A tall, soaring facade of pale "
            "cream limestone ashlar dominated by extreme verticality. Unbroken vertical mullions "
            "run from base to parapet, subdividing the wall into tall narrow panels. Enormous "
            "windows with rectilinear panel tracery — a strict grid of vertical and horizontal "
            "stone bars with no flowing curves. The windows are so large they dissolve the wall "
            "into luminous screens of glass. Four-centred arches over the largest windows. "
            "Blind paneling on solid wall sections matching the window tracery pattern. "
            "A tall square tower with clasping buttresses, subdivided by vertical panel shafts, "
            "topped with an octagonal lantern and pinnacles. Crenellated parapets with "
            "miniature battlements. Grotesques and gargoyles at corners. "
            "Flat-pitched roof hidden behind the parapet. "
            "Surrounding context: formal lawn with stone paths. "
            "Inspired by King's College Chapel Cambridge and Wills Memorial Building Bristol."
        ),
        "facadeDetail": {
            "primaryMaterial": "pale cream limestone ashlar, Bath stone or Clipsham stone",
            "secondaryMaterial": "slender stone mullions and transoms forming rectilinear panel tracery",
            "accentMaterial": "carved grotesques, heraldic shields, stone pinnacles",
            "groundFloor": "tall four-centred arch entrance with blind panel tracery surrounds, heavy oak doors",
            "upperFloors": "enormous panel tracery windows filling entire wall bays, blind paneling on solid walls, vertical emphasis throughout",
            "cornice": "crenellated parapet with pinnacles and miniature battlements on transoms",
            "colorScheme": "pale cream limestone throughout, dark leaded glass, grey lead roof"
        },
        "roofDetail": {
            "form": "relatively flat, hidden behind tall crenellated parapet",
            "material": "lead sheeting or dark slate",
            "features": "pinnacles at corners and along parapet, octagonal lantern tower, gargoyle downspouts",
            "aerialAppearance": "dark lead or slate surface hidden behind pale stone parapets with pinnacles"
        },
        "palette": {"primary": "#E8DCC8"}
    },
    {
        "id": "collegiate_gothic_ruskinian",
        "label": "Ruskinian Gothic",
        "filename": "variant_3.png",
        "description": (
            "Ruskinian Gothic (High Victorian Gothic) university building. A bold, muscular "
            "asymmetrical facade with dramatic constructional polychromy — horizontal bands of "
            "contrasting materials running across the entire facade. Red brick walls with "
            "alternating bands of cream/buff brick and blue-black brick creating striking "
            "striped patterns. Pointed lancet arch windows with polychrome voussoirs "
            "(alternating red and cream arch stones). Venetian-inspired plate tracery with "
            "trefoil and quatrefoil openings. Carved naturalistic capitals on stone columns "
            "depicting leaves, flowers, and birds — ornament drawn from nature per Ruskin's "
            "principles. Polished granite colonnettes flanking windows. A steep polychrome "
            "slate roof with patterns of different colored slates (red, grey, purple). "
            "Round turrets with conical roofs at corners. Iron cresting on ridgelines. "
            "Diaper patterns (diamond shapes) in contrasting brick on wall surfaces. "
            "Surrounding context: landscaped grounds with specimen trees. "
            "Inspired by Keble College Oxford and Memorial Hall Harvard."
        ),
        "facadeDetail": {
            "primaryMaterial": "red brick with horizontal bands of cream and blue-black brick",
            "secondaryMaterial": "carved sandstone window surrounds with naturalistic leaf capitals",
            "accentMaterial": "polished granite colonnettes, polychrome voussoirs, iron cresting",
            "groundFloor": "pointed lancet arch entrance with alternating red and cream voussoirs, carved naturalistic tympanum",
            "upperFloors": "lancet windows with plate tracery and quatrefoil medallions, polychrome brick banding and diaper patterns throughout",
            "cornice": "corbelled brick course with carved stone string course, iron ridge cresting",
            "colorScheme": "red brick body with cream, blue-black, and buff brick banding, sandstone details, polychrome slate roof"
        },
        "roofDetail": {
            "form": "steep pitch with cross gables and round corner turrets with conical caps",
            "material": "polychrome slate in patterned layout — red, grey, and purple slates",
            "features": "iron ridge cresting, conical turret roofs, prominent dormers with carved bargeboards",
            "aerialAppearance": "patterned polychrome slate in geometric designs, visible turret caps and iron cresting"
        },
        "palette": {"primary": "#A0522D"}
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
    # Resize to cover target, then center crop
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
    out_dir = _PUBLIC_DIR / "buildings" / "collegiate_gothic_education"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {out_dir}")
    print(f"Generating {len(VARIANTS)} variant images...\n")

    for i, variant in enumerate(VARIANTS):
        filename = variant["filename"]
        filepath = out_dir / filename

        if filepath.exists():
            print(f"[{i}] {variant['label']} — already exists, skipping")
            continue

        prompt = (
            f"Photorealistic architectural visualization. "
            f"Street-level perspective from across the street, approximately 25 meters away, "
            f"at a 3/4 angle showing two facades. The full building is visible from ground "
            f"to roofline with some sky above and street/sidewalk below. "
            f"{variant['description']} "
            f"{NO_PEOPLE} {STYLE_ANCHOR}"
        )

        print(f"[{i}] Generating {variant['label']}...")
        img_bytes = generate_image(prompt)

        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped)
            print(f"  OK Saved {filepath} ({len(cropped):,} bytes)")
        else:
            print(f"  X Failed to generate {variant['label']}")

        # Rate limit
        if i < len(VARIANTS) - 1:
            print("  .. Waiting 5s for rate limit...")
            time.sleep(5)

    # Also copy variant_0 as hero.png
    v0 = out_dir / "variant_0.png"
    hero = out_dir / "hero.png"
    if v0.exists() and not hero.exists():
        hero.write_bytes(v0.read_bytes())
        print(f"\nOK Copied variant_0.png -> hero.png")

    print("\nOK Done! Images saved to:", out_dir)


if __name__ == "__main__":
    main()
