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
MODEL = "gemini-3.1-flash-image-preview"
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

# Style 6: Photorealistic Fictional People — camera physics suffix (constant)
# Key: camera physics, fictional characters, texture emphasis, mid-ground placement,
# critical constraints at END of prompt to avoid malformations
PEOPLE_CAMERA_SUFFIX = (
    "Emphasize natural hair texture, skin texture, and clothing fabric detail. "
    "The architecture and landscape is the hero of the image, not the people. "
    "Shot on 35mm SLR, Kodak Portra 400 film stock, f/5.6 aperture. "
    "CRITICAL: all human figures must be fictional characters with naturally "
    "proportioned bodies — no deformed hands, no distorted faces, no extra "
    "limbs, no uncanny valley."
)

# Activity-specific people for different archetype types
# Maps archetype ID keywords to contextual people descriptions
ACTIVITY_PEOPLE: dict[str, str] = {
    "basketball": "Include 5-8 fictional people — a few playing basketball on the court (one mid-jump shooting, others defending), a couple watching from a bench courtside, someone walking a dog past the fence. ",
    "pickleball": "Include 5-8 fictional people — two pairs actively playing pickleball on courts (mid-rally with paddles), spectators watching from covered seating, someone drinking water at a bench. ",
    "soccer": "Include 5-8 fictional people — players actively playing soccer on the pitch (one kicking the ball, others running), a couple watching from outside the cage, a person walking by with a dog. ",
    "running_track": "Include 5-8 fictional people — runners jogging on the track in athletic wear, someone stretching on the infield grass, a coach with a stopwatch at trackside, a walker on the outer lane. ",
    "fitness": "Include 5-8 fictional people — someone doing pull-ups on the bars, a person using the parallel dip bars, a couple jogging along the fitness trail, someone stretching on a mat. ",
    "baseball": "Include 5-8 fictional people — a batter at home plate, a pitcher on the mound, fielders in position, a few spectators on the bleachers behind the backstop. ",
    "cricket": "Include 5-8 fictional people — a batsman and bowler on the wicket, fielders positioned on the outfield, spectators seated at the pavilion with tea. ",
    "disc_golf": "Include 5-8 fictional people — a player mid-throw at the tee pad, others walking the fairway carrying disc bags, a couple on the path with a dog watching. ",
    "bocce": "Include 5-8 fictional people — players gathered around the court studying their throws, one mid-toss with a bocce ball, others seated with wine glasses at the pergola, a dog resting nearby. ",
    "climbing": "Include 5-8 fictional people — climbers on the bouldering wall reaching for holds, a spotter watching from below, friends sitting on benches cheering, someone chalking their hands. ",
    "nature_play": "Include 5-8 fictional people — children balancing on logs, a toddler playing in the sand area, a parent watching from a log bench, kids splashing in the water channel, someone exploring the willow tunnel. ",
    "inclusive": "Include 5-8 fictional people — a child in a wheelchair going up a ramp, kids on adaptive swings, a parent pushing a child on the merry-go-round, children playing together on the structure. ",
    "mini_golf": "Include 5-8 fictional people — a family putting on a green, a couple waiting at the next hole, a child excited about a shot, someone at the clubhouse kiosk. ",
    "pollinator": "Include 5-8 fictional people — a couple walking hand-in-hand through the wildflower meadow path, a nature photographer kneeling to photograph butterflies, someone reading on a clearing bench, a person walking a dog. ",
    "orchard": "Include 5-8 fictional people — someone picking fruit from a tree, a couple walking between rows with a basket, a family at the picnic table, a child reaching for an apple, a dog sniffing the ground. ",
    "bioswale": "Include 5-8 fictional people — a couple walking along the bioswale path, someone reading an interpretive sign, a jogger passing by, a person walking a dog, a child pointing at plants. ",
    "urban_beach": "Include 5-8 fictional people — sunbathers on loungers, a couple walking barefoot on the sand, someone at the bar kiosk, kids playing near the splash zone, a person under an umbrella reading. ",
    "sculpture": "Include 5-8 fictional people — a couple contemplating a large sculpture, someone sketching on a bench, a photographer framing a piece, visitors strolling the gravel paths, a person walking a dog. ",
    "labyrinth": "Include 3-5 fictional people — someone walking the labyrinth path meditatively, a person sitting in quiet contemplation on a bench, a couple approaching the garden entrance. Calm, unhurried energy. ",
    "festival": "Include 5-8 fictional people — someone jogging across the open lawn, a couple walking a dog, a family having a picnic on the grass, a cyclist on the perimeter path. The lawn is empty of events — showing its versatile everyday character. ",
    "pump_track": "Include 5-8 fictional people — a BMX rider pumping through the rollers, a kid on a scooter on the track, spectators watching from benches, someone waiting at the start mound with their bike. ",
    "ice_rink": "Include 5-8 fictional people — skaters gliding on the ice (a couple holding hands, a child learning), someone lacing up skates on a bench, a person at the hot drink kiosk. Winter clothing. ",
    "volleyball": "Include 5-8 fictional people — two teams actively playing beach volleyball (one player jumping to spike), spectators sitting on the sand watching, someone walking by with a towel. ",
    "kayak": "Include 5-8 fictional people — someone carrying a kayak to the dock, a pair paddling on the water, a person at the storage racks, a couple watching from the bench, a dog on the dock. ",
    "splash_pad": "Include 5-8 fictional people — children running through spray jets laughing, a toddler in the ground bubblers, parents watching from benches, a child under the dump bucket. Summer clothing. ",
    "amphitheater": "Include 5-8 fictional people — audience seated on the grass or terraces, a performer on stage, someone carrying a picnic blanket to find a spot, a couple arriving from the path. ",
    "skate_park": "Include 5-8 fictional people — skateboarders riding in the bowl and on ledges, someone sitting on the edge watching, a BMX rider on the ramp, friends hanging out on benches. ",
    "dog_park": "Include 5-8 fictional people — dog owners chatting while their dogs play off-leash, someone throwing a ball for a retriever, a person at the water station, dogs of various sizes running. Multiple dogs. ",
    "community_garden": "Include 5-8 fictional people — someone tending a raised bed, a couple carrying a harvest basket, a person watering plants, a child helping dig, someone resting on a bench with a dog. ",
    "playground": "Include 5-8 fictional people — children on swings and slides, a parent pushing a child on a swing, kids climbing on the structure, a family arriving at the entrance. ",
    "swimming": "Include 5-8 fictional people — swimmers in lap lanes, someone diving from the edge, people sunbathing on deck chairs, a lifeguard in the stand, children in the wading pool. ",
    "vehicular_bridge": "Include 5-8 fictional people — cars and a bus crossing the bridge deck, a couple walking on the sidewalk, a cyclist in the bike lane, someone leaning on the railing looking at the water below. ",
    "landmark": "Include 5-8 fictional people — pedestrians walking along the bridge promenade with the skyline behind them, a couple taking a photo, a cyclist crossing, vehicles on the roadway. Dramatic civic scale. ",
    "viaduct": "Include 3-5 fictional people — a train or tram crossing the elevated viaduct, pedestrians walking below between the piers, a cyclist on the path beneath. Show the impressive repetitive arch/pier rhythm. ",
    "transit_priority": "Include 5-8 fictional people — a tram or bus crossing the bridge, pedestrians on wide sidewalks, a cyclist in the bike lane, someone at a transit stop on the bridge approach. ",
    "footbridge": "Include 5-8 fictional people — pedestrians crossing the footbridge at different points, a couple stopping to look at the view, someone with a stroller, a jogger. The bridge structure is the hero. ",
    "landscape_park_pedestrian": "Include 5-8 fictional people — a couple crossing the bridge hand-in-hand, someone pausing to photograph the water below, a person with binoculars birdwatching, a child pointing at fish. Natural setting. ",
    "cycle_bridge": "Include 5-8 fictional people — cyclists riding across the bridge in both directions, a person on an e-scooter, someone stopping to enjoy the view, a jogger. Smooth flowing movement. ",
    "shared_cycle_pedestrian": "Include 5-8 fictional people — cyclists on the red/dedicated cycle lane, pedestrians on the separate walking path, a family with children, someone walking a dog on the pedestrian side. Clear mode separation. ",
}

# Default fallback for any archetype not matched above
DEFAULT_PEOPLE = (
    "Include 5-8 fictional human characters naturally placed in the mid-ground "
    "of the scene, 15-40 meters from camera — a couple walking together, someone "
    "sitting on a bench reading, a person walking a golden retriever, a cyclist "
    "passing through. Casual contemporary clothing in muted earth tones. "
    "Include at least one dog. "
)


def get_people_snippet(arch_id: str) -> str:
    """Return activity-specific people description for an archetype."""
    for keyword, snippet in ACTIVITY_PEOPLE.items():
        if keyword in arch_id:
            return snippet + PEOPLE_CAMERA_SUFFIX
    return DEFAULT_PEOPLE + PEOPLE_CAMERA_SUFFIX


# Keep backward-compatible constant for non-openspace code paths
PEOPLE_SNIPPET = DEFAULT_PEOPLE + PEOPLE_CAMERA_SUFFIX

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
    + STYLE_ANCHOR + " {people}"
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

        # Streets get photorealistic people (Style 6)
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

        # Also generate variant images if present
        variants = arch.get("variants", [])
        for vi, variant in enumerate(variants):
            v_title = variant.get("label", f"Variant {vi}")
            v_desc = variant.get("description", "")

            v_card_desc = f"{title} — {v_title} variant. {v_desc}"
            v_card_desc += " Surrounding context shows urban buildings or landscape."

            v_thumb_url = f"/archetypes/streets/{slug}/variant_{vi}.png"
            cards.append({
                "arch_id": f"{arch_id}__variant_{vi}",
                "title": f"{title} — {v_title}",
                "filename": f"variant_{vi}.png",
                "output_dir": out_dir,
                "thumbnail_url": v_thumb_url,
                "description": v_card_desc,
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

        # Also generate variant images if present
        variants = arch.get("variants", [])
        for vi, variant in enumerate(variants):
            v_title = variant.get("label", f"Variant {vi}")
            v_desc = variant.get("description", "")

            v_card_desc = f"{title} — {v_title} variant. {v_desc}"
            v_card_desc += " Surrounding context shows urban buildings in the background."

            v_thumb_url = f"/archetypes/openspaces/{slug}/variant_{vi}.png"
            cards.append({
                "arch_id": f"{arch_id}__variant_{vi}",
                "title": f"{title} — {v_title}",
                "filename": f"variant_{vi}.png",
                "output_dir": out_dir,
                "thumbnail_url": v_thumb_url,
                "description": v_card_desc,
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
            people = get_people_snippet(card["arch_id"])
            prompt = LANDSCAPE_STYLE.format(description=card["description"], people=people)
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
