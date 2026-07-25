"""
Generate 4 design variants for every park/plaza and street/pathway archetype.

For each archetype, creates 4 material/design variants with:
  - Unique label, description, color palette
  - Card image generated via Gemini API

Usage:
    python scripts/generate_park_street_variants.py [--skip-existing] [--json-only]
                                                     [--parks-only] [--streets-only]
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
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"


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
CARD_HEIGHT = 768

# ---------------------------------------------------------------------------
# Variant theme definitions by category
# ---------------------------------------------------------------------------
# Each category maps to 4 variant themes. Each theme has:
#   label, color, style, details (used to build the prompt)

PARK_VARIANT_THEMES: dict[str, list[dict]] = {
    # --- Landscape Parks ---
    "landscape_parks": [
        {
            "label": "English Pastoral",
            "color": "#4A7C59",
            "style": "classic English landscape garden style",
            "details": "rolling lawns with scattered specimen trees, serpentine gravel paths, naturalistic pond edges, ornamental iron benches, and romantic bridge features",
        },
        {
            "label": "Modern Minimalist",
            "color": "#7D8491",
            "style": "contemporary minimalist landscape design",
            "details": "clean geometric lawn panels, poured concrete paths with corten steel edges, architectural grasses in linear beds, minimalist timber benches, and subtle LED path lighting",
        },
        {
            "label": "Mediterranean Xeriscape",
            "color": "#C4A35A",
            "style": "Mediterranean drought-tolerant xeriscape",
            "details": "gravel and decomposed granite groundcover, native drought-tolerant plantings including lavender and rosemary, terracotta-edged paths, olive and citrus trees, and stone retaining walls",
        },
        {
            "label": "Tropical Lush",
            "color": "#2D6A4F",
            "style": "lush tropical landscape design",
            "details": "dense tropical plantings with palms and ferns, winding boardwalk paths, water features with lotus plants, thatched shade pavilions, and volcanic rock accents",
        },
    ],
    # --- Neighborhood Public Realm ---
    "neighborhood_public_realm": [
        {
            "label": "Rustic Timber & Gravel",
            "color": "#8B6914",
            "style": "rustic timber and natural materials design",
            "details": "rough-hewn timber structures, compacted gravel paths, split-rail fences, wildflower meadow borders, and natural boulder seating",
        },
        {
            "label": "Modern Steel & Turf",
            "color": "#5B7065",
            "style": "modern steel and synthetic turf design",
            "details": "powder-coated steel structures, synthetic turf play areas, rubber safety surfacing, LED-lit stainless bollards, and clean concrete edges",
        },
        {
            "label": "Natural Meadow",
            "color": "#6B8E23",
            "style": "naturalized meadow and prairie planting",
            "details": "native prairie grasses and wildflowers, mown paths through tall meadow, log seating circles, bird boxes on timber posts, and rain garden bioswales",
        },
        {
            "label": "Urban Contemporary",
            "color": "#4A6670",
            "style": "urban contemporary landscape with mixed hardscape",
            "details": "permeable pavers in geometric patterns, raised planters with ornamental grasses, powder-coated metal furniture, integrated water play jets, and colored concrete accents",
        },
    ],
    # --- Sports & Recreation ---
    "sports_recreation": [
        {
            "label": "Professional Grade",
            "color": "#1B5E20",
            "style": "professional-grade sports facility",
            "details": "regulation markings on manicured turf, aluminum bleacher seating, chain-link and windscreen fencing, professional LED floodlights, and paved service roads",
        },
        {
            "label": "Community Recreation",
            "color": "#E65100",
            "style": "community recreation center style",
            "details": "multi-use fields with painted lines, covered picnic pavilions, rubber track surface, colorful equipment and signage, and family-friendly gathering areas",
        },
        {
            "label": "Naturalized Active",
            "color": "#558B2F",
            "style": "naturalized active recreation landscape",
            "details": "fields integrated into natural terrain, timber spectator terraces, native grass borders, gravel parking areas, and wildlife-friendly perimeter planting",
        },
        {
            "label": "Urban Athletic",
            "color": "#37474F",
            "style": "urban athletic facility with industrial materials",
            "details": "concrete and steel structures, rubber and asphalt surfaces, corten steel retaining walls, bold graphic markings, and integrated skateable landscape elements",
        },
    ],
    # --- Specialty Gardens ---
    "specialty_gardens": [
        {
            "label": "Classical Formal",
            "color": "#5D4037",
            "style": "classical formal garden design",
            "details": "symmetrical parterre beds, clipped boxwood hedges, gravel allees, stone urns and balustrades, and a central ornamental fountain",
        },
        {
            "label": "Woodland Naturalistic",
            "color": "#33691E",
            "style": "woodland naturalistic garden",
            "details": "shade-loving understory plantings, bark mulch paths winding through dappled light, moss-covered stones, fern grottos, and rustic timber bridges",
        },
        {
            "label": "Contemporary Sculptural",
            "color": "#546E7A",
            "style": "contemporary sculptural garden",
            "details": "abstract sculptural elements, architectural plant specimens, polished concrete and corten steel features, minimalist water rills, and dramatic night lighting",
        },
        {
            "label": "Cottage Romantic",
            "color": "#AD1457",
            "style": "romantic cottage garden style",
            "details": "overflowing perennial borders, climbing roses on arbors, brick and stone paths, weathered wooden gates, and antique-style garden furniture",
        },
    ],
    # --- Ecological Resilience ---
    "ecological_resilience": [
        {
            "label": "Native Restoration",
            "color": "#2E7D32",
            "style": "native habitat restoration landscape",
            "details": "native grassland and woodland edge plantings, naturalized stream channels, wildlife corridors, educational interpretive signs, and minimal-impact boardwalk trails",
        },
        {
            "label": "Bioengineered Infrastructure",
            "color": "#00695C",
            "style": "bioengineered green infrastructure",
            "details": "constructed wetland cells, gabion basket retaining walls, bioswale channels with native sedges, permeable paving systems, and rain harvesting cisterns",
        },
        {
            "label": "Rewilded Urban",
            "color": "#4E342E",
            "style": "rewilded urban landscape",
            "details": "successional forest plantings, deadwood habitat piles, wildflower meadows on former pavement, reclaimed material paths, and insect hotels",
        },
        {
            "label": "Resilient Coastal",
            "color": "#0277BD",
            "style": "resilient coastal landscape design",
            "details": "salt-tolerant native plantings, living shoreline with oyster reef structures, elevated boardwalks, dune grass restoration, and tidal marsh buffers",
        },
    ],
    # --- Civic Plazas ---
    "civic_plazas": [
        {
            "label": "Neoclassical Stone",
            "color": "#795548",
            "style": "neoclassical stone civic plaza",
            "details": "cut stone paving in radiating patterns, classical balustrades and columns, symmetrical tree plantings, ornamental lamp posts, and a central monument or fountain",
        },
        {
            "label": "Contemporary Urban",
            "color": "#455A64",
            "style": "contemporary urban civic plaza",
            "details": "large-format granite pavers, linear water channels, architectural concrete seating walls, stainless steel bollards, and specimen trees in flush grates",
        },
        {
            "label": "Green Civic",
            "color": "#388E3C",
            "style": "green civic plaza with integrated landscape",
            "details": "permeable paving with grass joints, raised planter terraces, shade tree canopy, rain gardens at edges, and timber-and-steel hybrid furniture",
        },
        {
            "label": "Festival & Market",
            "color": "#D84315",
            "style": "flexible festival and market plaza",
            "details": "flat open hardscape with utility hookups, moveable planters, retractable bollards, festoon lighting infrastructure, and modular stage platform area",
        },
    ],
    # --- Social / Event Spaces ---
    "social_event_spaces": [
        {
            "label": "Terraced Performance",
            "color": "#4527A0",
            "style": "terraced performance venue landscape",
            "details": "stone-clad terraced seating into hillside, permanent stage platform with acoustic wall, theatrical lighting columns, and landscaped wings with mature trees",
        },
        {
            "label": "Open Festival Ground",
            "color": "#F57F17",
            "style": "open festival ground design",
            "details": "large flat lawn for events, portable infrastructure connections, gravel service paths, shade sail anchor points, and perimeter food vendor pads",
        },
        {
            "label": "Intimate Garden Venue",
            "color": "#1B5E20",
            "style": "intimate garden event venue",
            "details": "formal garden rooms with hedge walls, pergola-covered gathering areas, string light canopy, stone patio spaces, and ornamental flower beds",
        },
        {
            "label": "Industrial Adaptive",
            "color": "#424242",
            "style": "industrial adaptive reuse event space",
            "details": "reclaimed brick and steel structures, polished concrete surfaces, industrial pendant lighting, exposed steel trusses for hanging decor, and container gardens",
        },
    ],
    # --- Waterfront Spaces ---
    "waterfront_spaces": [
        {
            "label": "Maritime Heritage",
            "color": "#1565C0",
            "style": "maritime heritage waterfront",
            "details": "timber boardwalk with rope railings, nautical lighting fixtures, weathered timber bollards, mooring cleats as seating, and coastal native plantings",
        },
        {
            "label": "Modern Esplanade",
            "color": "#78909C",
            "style": "modern waterfront esplanade",
            "details": "polished concrete promenade, glass and steel balustrades, integrated LED strip lighting, cantilevered viewing platforms, and architectural shade structures",
        },
        {
            "label": "Tropical Resort",
            "color": "#00897B",
            "style": "tropical resort waterfront",
            "details": "palm-lined walkways, white sand accents, thatched shade cabanas, coral stone retaining walls, and overwater timber decking",
        },
        {
            "label": "Naturalized Riparian",
            "color": "#33691E",
            "style": "naturalized riparian waterfront",
            "details": "natural stone bank armoring, native riparian plantings, timber fishing platforms, gravel access paths, and wildlife observation blinds",
        },
    ],
    # --- Parking Areas ---
    "parking_areas": [
        {
            "label": "Standard Asphalt",
            "color": "#616161",
            "style": "standard asphalt parking facility",
            "details": "smooth asphalt surface with painted striping, concrete curbs, standard pole-mounted lighting, simple landscaped islands, and chain-link perimeter",
        },
        {
            "label": "Green Infrastructure",
            "color": "#43A047",
            "style": "green infrastructure parking design",
            "details": "permeable paver parking stalls, bioswale drainage channels, shade tree canopy over every row, rain gardens at lot edges, and solar panel canopies",
        },
        {
            "label": "Urban Structured",
            "color": "#546E7A",
            "style": "urban structured parking design",
            "details": "concrete and steel multi-level structure, perforated metal screen facade, integrated EV charging stations, LED wayfinding, and ground-level retail wrap",
        },
        {
            "label": "Landscape-Screened",
            "color": "#689F38",
            "style": "landscape-screened parking facility",
            "details": "dense hedge and tree screening, decorative perimeter fencing, brick paver entry drives, ornamental lighting, and generous landscape medians",
        },
    ],
    # --- Water Features ---
    "water_features": [
        {
            "label": "Naturalistic Pond",
            "color": "#1B5E20",
            "style": "naturalistic pond and water garden",
            "details": "irregular organic shoreline, native aquatic plantings, natural stone edge, timber fishing dock, and overhanging willow trees",
        },
        {
            "label": "Formal Reflecting",
            "color": "#37474F",
            "style": "formal reflecting pool and fountain",
            "details": "geometric stone-edged reflecting pool, symmetrical jet fountains, polished granite coping, clipped hedges framing the water, and classical urns",
        },
        {
            "label": "Contemporary Interactive",
            "color": "#0097A7",
            "style": "contemporary interactive water feature",
            "details": "flush-grade splash jets in granite paving, LED-lit water curtains, misting arches, stainless steel nozzles, and rubberized play surfacing",
        },
        {
            "label": "Ecological Wetland",
            "color": "#558B2F",
            "style": "ecological wetland water system",
            "details": "constructed wetland cells with native sedges, gravel filter beds, wooden boardwalk crossings, bird observation platforms, and interpretive ecology signage",
        },
    ],
    # --- Custom ---
    "custom": [
        {
            "label": "Eclectic Mixed-Use",
            "color": "#6D4C41",
            "style": "eclectic mixed-use open space",
            "details": "combination of hardscape and softscape zones, moveable furniture, pop-up garden beds, flexible paving areas, and art installation platforms",
        },
        {
            "label": "Biophilic Urban",
            "color": "#2E7D32",
            "style": "biophilic urban oasis",
            "details": "dense vertical gardens, moss walls, cascading water features, natural stone and timber materials, and sensory planting beds",
        },
        {
            "label": "Tech-Enabled Smart",
            "color": "#1565C0",
            "style": "tech-enabled smart park",
            "details": "solar-powered charging stations, interactive digital displays, smart irrigation zones, sensor-equipped furniture, and programmable LED landscape lighting",
        },
        {
            "label": "Heritage Adaptive",
            "color": "#8D6E63",
            "style": "heritage adaptive reuse landscape",
            "details": "preserved historic elements integrated with new plantings, reclaimed materials for paths and walls, interpretive heritage markers, and restored original features",
        },
    ],
}

STREET_VARIANT_THEMES: dict[str, list[dict]] = {
    "auto_oriented": [
        {
            "label": "Classic Tree-Lined",
            "color": "#4A7C59",
            "style": "classic tree-lined streetscape",
            "details": "mature deciduous street trees with broad canopies, traditional concrete sidewalks, ornamental iron lamp posts, granite curbs, and manicured grass planting strips",
        },
        {
            "label": "Modern Minimalist",
            "color": "#607D8B",
            "style": "modern minimalist streetscape",
            "details": "clean concrete paving, flush curbs, columnar trees in steel grates, LED pole lights, and minimal street furniture in brushed stainless steel",
        },
        {
            "label": "European Cobblestone",
            "color": "#8D6E63",
            "style": "European cobblestone streetscape",
            "details": "natural stone sett paving, granite curbs, pollarded plane trees, vintage-style cast iron lamp posts, and stone bollards with iron chains",
        },
        {
            "label": "Tropical Boulevard",
            "color": "#2E7D32",
            "style": "tropical boulevard streetscape",
            "details": "palm-lined median and verges, coral stone curbs, lush tropical understory plantings, warm-toned concrete walks, and decorative tile accents",
        },
    ],
    "pedestrian_oriented": [
        {
            "label": "Mediterranean Paseo",
            "color": "#D4A574",
            "style": "Mediterranean paseo streetscape",
            "details": "terracotta-toned pavers, shade pergolas with climbing bougainvillea, ceramic tile accents, wrought-iron benches, and citrus trees in decorative planters",
        },
        {
            "label": "Nordic Timber Walk",
            "color": "#5D4037",
            "style": "Nordic timber pedestrian streetscape",
            "details": "wide timber boardwalk surface, birch tree plantings, warm-toned timber bollards, integrated timber bench seating, and native ground cover plantings",
        },
        {
            "label": "Contemporary Urban",
            "color": "#455A64",
            "style": "contemporary urban pedestrian street",
            "details": "large-format natural stone pavers, corten steel planters, architectural concrete seating walls, linear water features, and specimen trees in flush grates",
        },
        {
            "label": "Festival Street",
            "color": "#E65100",
            "style": "vibrant festival street design",
            "details": "colorful permeable pavers in patterns, festoon string lighting overhead, moveable planter boxes, public art installations, and bright-colored street furniture",
        },
    ],
    "cycling_oriented": [
        {
            "label": "Dutch Cycle Infrastructure",
            "color": "#E53935",
            "style": "Dutch-style separated cycle infrastructure",
            "details": "red-tinted asphalt cycle track, raised concrete separator from traffic, dedicated signal poles, cycle parking racks, and green verge with low hedging",
        },
        {
            "label": "Green Corridor",
            "color": "#43A047",
            "style": "green corridor cycle and pedestrian path",
            "details": "smooth asphalt path through linear park, native wildflower meadow edges, timber rest stops with bike repair stations, and wildlife crossing bridges",
        },
        {
            "label": "Urban Protected Lane",
            "color": "#1565C0",
            "style": "urban protected cycle lane",
            "details": "green-painted cycle lane with concrete barriers, flex-post delineators, dedicated signal phases, bike box at intersections, and raised crossings",
        },
        {
            "label": "Scenic Greenway",
            "color": "#2E7D32",
            "style": "scenic greenway trail",
            "details": "winding paved path through natural landscape, interpretive nature signs, rest areas with shade pavilions, native tree canopy, and creek crossings on timber bridges",
        },
    ],
    "transit_oriented": [
        {
            "label": "Modern Transit Mall",
            "color": "#1565C0",
            "style": "modern transit mall design",
            "details": "dedicated bus and rail lanes in colored pavement, glass-canopy shelters, digital real-time displays, raised platform stops, and street trees in structural soil",
        },
        {
            "label": "Heritage Tram Avenue",
            "color": "#795548",
            "style": "heritage tram avenue streetscape",
            "details": "embedded rail tracks in cobblestone paving, ornamental catenary poles, heritage-style waiting shelters, gas-lamp-style lighting, and mature tree-lined median",
        },
        {
            "label": "Green Transit Corridor",
            "color": "#388E3C",
            "style": "green transit corridor",
            "details": "grass-track transit lanes, bioswale median strips, solar-powered shelters with green roofs, native plantings along alignment, and permeable platform surfaces",
        },
        {
            "label": "High-Tech Transit Hub",
            "color": "#37474F",
            "style": "high-tech transit hub streetscape",
            "details": "sleek aluminum and glass shelters, integrated EV charging, smart pavement sensors, dynamic LED wayfinding, and polished concrete platforms",
        },
    ],
}


# ---------------------------------------------------------------------------
# Variant generation from themes
# ---------------------------------------------------------------------------

def _id_to_hyphen(arch_id: str) -> str:
    """Convert underscore-based ID to hyphenated directory name."""
    return arch_id.replace("_", "-")


def generate_variants_for_archetype(
    arch_id: str,
    arch_title: str,
    arch_description: str,
    category: str,
    domain: str,  # "openspaces" or "streets"
    themes: dict[str, list[dict]],
) -> list[dict]:
    """Generate 4 variant dicts for a given archetype using category themes."""
    category_themes = themes.get(category, themes.get("custom", []))
    if not category_themes:
        # Fallback: use the first available category
        category_themes = next(iter(themes.values()))

    dir_name = _id_to_hyphen(arch_id)
    variants = []

    for vi, theme in enumerate(category_themes):
        variant_id = f"{arch_id}_v{vi}"
        thumb_url = f"/archetypes/{domain}/{dir_name}/variant_{vi}.png"
        variants.append({
            "id": variant_id,
            "label": theme["label"],
            "color": theme["color"],
            "description": f"{arch_title} in {theme['style']}. {theme['details'].capitalize()}.",
            "thumbnailUrl": thumb_url,
            "style": theme["style"],
            "details": theme["details"],
        })

    return variants


# ---------------------------------------------------------------------------
# Image generation
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


def build_variant_prompt(arch_title: str, arch_description: str, variant: dict) -> str:
    """Build a card image prompt for a park/street variant."""
    style = variant.get('style', variant.get('label', ''))
    details = variant.get('details', variant.get('description', ''))
    prompt = (
        f"Photorealistic architectural visualization of {arch_title} "
        f"in {style} style. "
        f"Street-level perspective showing {details}. "
        f"{arch_description}. "
        f"{NO_PEOPLE} {STYLE_ANCHOR}"
    )
    return prompt


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


def save_image(image_bytes: bytes, output_path: Path) -> None:
    """Resize and save image."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
    img.save(str(output_path), "PNG", optimize=True)


# ---------------------------------------------------------------------------
# Processing logic
# ---------------------------------------------------------------------------

def process_domain(
    json_path: Path,
    domain: str,       # "openspaces" or "streets"
    themes: dict[str, list[dict]],
    category_key: str,  # "aestheticCategory" for both
    skip_existing: bool,
    json_only: bool,
) -> tuple[int, int, int, int]:
    """Process all archetypes in a domain. Returns (updated, generated, failed, skipped)."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    archetypes = data["archetypes"]

    updated_count = 0
    image_tasks: list[dict] = []

    for arch in archetypes:
        arch_id = arch["id"]
        arch_title = arch.get("title", arch_id)
        arch_description = arch.get("description", "")
        category = arch.get(category_key, "custom")
        dir_name = _id_to_hyphen(arch_id)

        # Skip if already has 4 variants
        if arch.get("variants") and len(arch["variants"]) >= 4:
            print(f"SKIP (has variants): {arch_title}")
            # Still queue image tasks for missing images
            for vi, v in enumerate(arch["variants"]):
                out_dir = _PUBLIC_DIR / domain / dir_name
                img_path = out_dir / f"variant_{vi}.png"
                if not img_path.exists() and not skip_existing:
                    image_tasks.append({
                        "arch_title": arch_title,
                        "arch_description": arch_description,
                        "variant": v,
                        "output_dir": out_dir,
                        "filename": f"variant_{vi}.png",
                    })
            continue

        # Generate variant definitions
        variants = generate_variants_for_archetype(
            arch_id, arch_title, arch_description, category, domain, themes
        )

        # Add variants to archetype JSON
        arch["variants"] = []
        for vi, v in enumerate(variants):
            arch_variant = {
                "id": v["id"],
                "label": v["label"],
                "color": v["color"],
                "description": v["description"],
                "thumbnailUrl": v["thumbnailUrl"],
            }
            arch["variants"].append(arch_variant)

            out_dir = _PUBLIC_DIR / domain / dir_name
            img_path = out_dir / f"variant_{vi}.png"
            if not skip_existing or not img_path.exists():
                image_tasks.append({
                    "arch_title": arch_title,
                    "arch_description": arch_description,
                    "variant": v,
                    "output_dir": out_dir,
                    "filename": f"variant_{vi}.png",
                })

        updated_count += 1
        print(f"ADDED variants: {arch_title} ({len(variants)} variants)")

    # Save updated JSON
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nUpdated {updated_count} archetypes with variants in {json_path.name}")
    print(f"Image generation tasks: {len(image_tasks)}")

    if json_only:
        print("--json-only: skipping image generation")
        return updated_count, 0, 0, 0

    # Generate images
    generated = 0
    failed = 0
    skipped = 0

    for i, task in enumerate(image_tasks):
        out_dir = task["output_dir"]
        img_path = out_dir / task["filename"]

        if skip_existing and img_path.exists():
            skipped += 1
            continue

        label = task["variant"].get("label", task["filename"])
        print(
            f"\n[{i+1}/{len(image_tasks)}] Generating: "
            f"{task['arch_title']} - {label}"
        )
        prompt = build_variant_prompt(
            task["arch_title"], task["arch_description"], task["variant"]
        )
        print(f"  Prompt length: {len(prompt)} chars")
        print(f"  Calling Gemini API...")

        image_bytes = generate_image(prompt)
        if image_bytes:
            out_dir.mkdir(parents=True, exist_ok=True)
            save_image(image_bytes, img_path)
            size_kb = img_path.stat().st_size / 1024
            print(f"  Saved: {img_path} ({size_kb:.1f} KB)")
            generated += 1
        else:
            print(f"  FAILED - skipping {label}")
            failed += 1

        # Small delay between requests
        time.sleep(2)

    return updated_count, generated, failed, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate 4 design variants for park/street archetypes"
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip images that already exist on disk",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Only update JSON files, don't generate images",
    )
    parser.add_argument(
        "--parks-only", action="store_true",
        help="Only process park/plaza archetypes",
    )
    parser.add_argument(
        "--streets-only", action="store_true",
        help="Only process street/pathway archetypes",
    )
    args = parser.parse_args()

    if args.parks_only and args.streets_only:
        print("ERROR: Cannot specify both --parks-only and --streets-only")
        sys.exit(1)

    do_parks = not args.streets_only
    do_streets = not args.parks_only

    total_updated = 0
    total_generated = 0
    total_failed = 0
    total_skipped = 0

    if do_parks:
        print("=" * 60)
        print("PARKS & PLAZAS")
        print("=" * 60)
        parks_json = _DATA_DIR / "openSpaceArchetypes.json"
        u, g, f, s = process_domain(
            parks_json,
            "openspaces",
            PARK_VARIANT_THEMES,
            "aestheticCategory",
            args.skip_existing,
            args.json_only,
        )
        total_updated += u
        total_generated += g
        total_failed += f
        total_skipped += s

    if do_streets:
        print("\n" + "=" * 60)
        print("STREETS & PATHWAYS")
        print("=" * 60)
        streets_json = _DATA_DIR / "streetPathArchetypes.json"
        u, g, f, s = process_domain(
            streets_json,
            "streets",
            STREET_VARIANT_THEMES,
            "aestheticCategory",
            args.skip_existing,
            args.json_only,
        )
        total_updated += u
        total_generated += g
        total_failed += f
        total_skipped += s

    print(f"\n{'=' * 60}")
    print(
        f"Done! {total_updated} archetypes updated, "
        f"{total_generated} images generated, "
        f"{total_failed} failed, {total_skipped} skipped"
    )


if __name__ == "__main__":
    main()
