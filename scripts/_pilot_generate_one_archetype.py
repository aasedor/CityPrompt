"""One-off pilot runner: generate variant_N.png for a single archetype id
using the Style 6 'Photorealistic Fictional People' pipeline (matches the
quality of the original outdoor-ice-rink/festival/etc. cards).

Imports prompt machinery from scripts/generate_card_images.py so we get:
  - Gemini 3.1 Flash Image (preview) at temperature 0.7 (proven recipe)
  - PEOPLE_CAMERA_SUFFIX with Kodak Portra 400 film stock + 35mm SLR f/5.6
  - LANDSCAPE_STYLE template with {description} + {people} interpolation
  - ACTIVITY_PEOPLE per-archetype activity descriptions

Does NOT walk the whole catalog and does NOT write the JSON back — strictly
pilot scope, one archetype id at a time.

Usage:
    python scripts/_pilot_generate_one_archetype.py --domain=openspaces --id=beer_garden

Add the archetype to PILOT_ACTIVITY_PEOPLE below if it's not already in the
shared ACTIVITY_PEOPLE map in generate_card_images.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from generate_card_images import (  # type: ignore
    LANDSCAPE_STYLE,
    PEOPLE_CAMERA_SUFFIX,
    ACTIVITY_PEOPLE,
    generate_image,
    resize_to_card,
    _slugify,
    _DATA_DIR,
    _PUBLIC_DIR,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Per-archetype activity people for new pilots not yet in ACTIVITY_PEOPLE.
# Add entries here as we author new archetypes; merge into the canonical
# generate_card_images.py ACTIVITY_PEOPLE when we land the batch.
PILOT_ACTIVITY_PEOPLE: dict[str, str] = {
    "beer_garden": (
        "Include 5-8 fictional people — friends seated at long trestle tables "
        "clinking beer steins, a server walking with a tray of full glasses, a "
        "couple standing near the kiosk reading the menu, two people at a high "
        "bar counter laughing, a small dog under one of the tables, a child "
        "with a pretzel sitting next to parents at the end of a row. Casual "
        "contemporary clothing, warm relaxed atmosphere. "
    ),
    # --- Civic Plazas ---
    "city_hall_government_plaza": (
        "Include 5-8 fictional people — a small group of three students sitting "
        "on a stone bench reading, a couple walking diagonally across the plaza, "
        "someone reading a bronze plaque near the monument, a person with a "
        "coffee on the building steps, a tourist taking a photo of the building, "
        "a delivery cyclist crossing the corner. Casual contemporary clothing, "
        "weekday-civic atmosphere. "
    ),
    "sunken_plaza": (
        "Include 5-8 fictional people — diners at a café terrace on the lower "
        "court, two friends seated on the stepped tiers chatting, a couple "
        "descending the broad steps with shopping bags, someone with a takeaway "
        "coffee crossing the lower floor, a person photographing the central "
        "feature, an office-worker on a phone call by a rim planter. Casual "
        "urban contemporary clothing. "
    ),
    "cathedral_religious_forecourt": (
        "Include 4-6 fictional people — a couple standing reverently near the "
        "building portal, a tour group of three listening to a guide pointing "
        "up at the facade, a single contemplative figure on a stone bench, a "
        "person taking a photograph of the religious building, an elderly local "
        "crossing the square with a small market bag. Modest respectful "
        "clothing appropriate to the cultural setting. Calm, unhurried "
        "atmosphere. "
    ),
    "cultural_institution_forecourt": (
        "Include 5-8 fictional people — a couple ascending the grand staircase "
        "to the entry, two students sitting on the steps reading, someone "
        "photographing the building facade, a parent and child arriving at the "
        "curb, a person with a museum tote descending the steps, a small tour "
        "group near the central feature with a guide. Casual smart-casual "
        "contemporary clothing. "
    ),
    "stepped_terraced_plaza": (
        "Include 5-8 fictional people — a couple sitting on the stepped tiers "
        "eating gelato, a small group of four friends gathered on a tier "
        "chatting, someone descending the central stair-aisle with a guidebook, "
        "a person reading on a tier with a takeaway coffee, a tourist "
        "photographing the cascade from below. Casual relaxed clothing, late-"
        "afternoon golden hour light. "
    ),
    # --- Landscape Parks ---
    "picturesque_olmsted_park": (
        "Include 5-8 fictional people — a couple walking hand-in-hand on a "
        "serpentine path, a jogger with a golden retriever along the lake "
        "shore, a family with a stroller crossing a stone arch bridge, two "
        "friends reading on a bench by the lake, a child running across a "
        "meadow, a cyclist on the carriage drive. Casual contemporary "
        "clothing, soft late-afternoon golden hour atmosphere. "
    ),
    "reclaimed_industrial_park": (
        "Include 5-8 fictional people — climbers ascending a preserved blast-"
        "furnace stair, a couple exploring a converted gasometer, a "
        "photographer with a tripod near an industrial relic, two kids "
        "clambering on a sculptural conveyor, a group of three on the "
        "elevated catwalk, a person walking a dog past a pioneer-birch grove. "
        "Casual urban clothing, contemporary post-industrial atmosphere. "
    ),
    "quarry_sunken_garden_park": (
        "Include 4-6 fictional people — a couple descending the switchback "
        "stair to the bowl floor, a person sitting on a stone bench among "
        "the flower beds, a small group of three friends near the central "
        "pond, a tourist photographing the cascading water feature, a child "
        "running across the bowl-floor lawn. Calm, contemplative garden "
        "atmosphere. "
    ),
    "hilltop_topographic_park": (
        "Include 5-8 fictional people — a couple at the summit belvedere "
        "taking in the view, a runner ascending a switchback, a child "
        "pointing out a city landmark from the parapet, a group of three "
        "friends on a terrace bench, a hiker with a small backpack on a "
        "mid-slope switchback, a person photographing the view. Casual "
        "outdoor clothing. "
    ),
    "estate_picnic_grove": (
        "Include 5-8 fictional people — a family of four at a picnic table "
        "eating, a person tending a charcoal grill, two children playing "
        "frisbee on the central lawn, a couple unfolding a picnic blanket, "
        "an elderly couple seated under a pavilion, a teenager throwing a "
        "ball for a labrador. Family-day-out atmosphere, summer light. "
    ),
    "reservoir_watershed_park": (
        "Include 4-6 fictional people — a runner on the perimeter trail, a "
        "cyclist passing on the same trail, a person fishing from a timber "
        "pier with a rod, a couple walking a dog around the lake, two "
        "friends on a bench overlooking the water. Calm regional-recreation "
        "atmosphere. "
    ),
    "greenbelt_buffer_park": (
        "Include 5-8 fictional people — a cyclist on the spine path, a "
        "runner with a small dog, a parent with a stroller on a branch path, "
        "two friends walking and chatting, a small playground scene with "
        "two children climbing, a person with a coffee on a bench. Suburban-"
        "recreational atmosphere. "
    ),
    "foothill_trail_park": (
        "Include 3-5 fictional people — a hiker with a small daypack on a "
        "ridge trail, a couple at a viewpoint outcrop pointing at distant "
        "peaks, a trail runner with a hydration vest, a person photographing "
        "wildflowers, a single hiker resting on a log bench. Outdoor "
        "wilderness clothing, regional-conservation atmosphere. "
    ),
    # --- Social / Event Spaces ---
    "concert_pavilion_lawn": (
        "Include 5-8 fictional people — concertgoers seated on the lawn "
        "with picnic blankets, a couple at the edge of the audience field, "
        "a small group on folding chairs near the front, two people walking "
        "toward the stage shell with concession cups, a person with a small "
        "dog on a path. Casual summer-evening clothing, golden-hour pre-"
        "show atmosphere. "
    ),
    "food_truck_plaza": (
        "Include 5-8 fictional people — diners seated at communal picnic "
        "tables eating from food-truck plates, two friends standing in line "
        "at a truck window, a couple sharing a bar-height counter table "
        "with drinks, a small group of four laughing at the centre table, a "
        "child sitting on a parent's lap, a server at one of the trucks. "
        "Casual contemporary clothing, evening string-light atmosphere. "
    ),
    "outdoor_cinema_lawn": (
        "Include 5-8 fictional people — couples and small groups seated on "
        "picnic blankets and low folding chairs across the lawn watching "
        "the screen, a person walking back from the concession kiosk with "
        "popcorn, a small child propped against a parent. Casual summer-"
        "evening clothing, dusk light, warm projection glow on faces. "
    ),
    "night_market": (
        "Include 5-8 fictional people — diners seated at the central "
        "communal aisle tables eating from market plates, a couple walking "
        "between stall rows with takeaway cups, two friends at a hawker "
        "kiosk picking up an order, a small child holding a paper lantern, "
        "a server at one of the food kiosks plating up. Casual contemporary "
        "clothing matching the cultural setting, lantern-glow atmosphere. "
    ),
    "parade_ground": (
        "Include 4-6 fictional people — a couple walking down the central "
        "axis at a leisurely pace, a tourist photographing the monumental "
        "termination, a small group of three on a perimeter bench, a "
        "jogger crossing the cross-axis, a person with a small dog on a "
        "side path. Casual everyday clothing, midday clear-sky atmosphere "
        "(no parade in progress — showing everyday character). "
    ),
    # --- Waterfront Spaces ---
    "marina_yacht_harbor": (
        "Include 4-6 fictional people — a couple walking the perimeter "
        "promenade, a sailor adjusting lines on a moored yacht, two "
        "friends on a bench overlooking the slips, a person with a coffee "
        "exiting the dockmaster building, a fisherman casting from the "
        "quay edge. Casual coastal clothing. "
    ),
    "working_pier_wharf_conversion": (
        "Include 5-8 fictional people — a runner along the perimeter "
        "promenade, two children climbing on a sculptural shipping crate, "
        "a couple on the lawn panel with a picnic blanket, a person with "
        "a coffee on a kiosk patio, a small group of three by an "
        "interpretive panel reading. Casual urban clothing, post-"
        "industrial-cool atmosphere. "
    ),
    "floating_park_pool": (
        "Include 4-6 fictional people — swimmers in the pool basin (if "
        "applicable), a couple on the deck looking at the water, a person "
        "lounging on a built-in deck bench, a child crossing the gangway "
        "with a parent, a friend group of three on the viewing deck. "
        "Casual swim or summer clothing as appropriate. "
    ),
    "lighthouse_point_park": (
        "Include 3-5 fictional people — a couple at a cliff-edge viewing "
        "platform looking out to sea, a single hiker with a small "
        "backpack on the headland path, a parent with a child near the "
        "lighthouse base, a tourist photographing the lighthouse. Casual "
        "windswept-coastal clothing. "
    ),
    "tidal_marsh_boardwalk": (
        "Include 3-5 fictional people — a birdwatcher with binoculars on "
        "a viewing platform, a couple walking the boardwalk hand-in-hand, "
        "a parent with a child pointing at a marsh creature, a person with "
        "a camera at the bird-blind. Quiet, contemplative atmosphere. "
        "Casual outdoor clothing. "
    ),
    "lake_edge_plaza": (
        "Include 5-8 fictional people — a couple walking the esplanade "
        "hand-in-hand, a runner passing on the promenade, two friends on "
        "a perimeter bench facing the lake, a parent with a stroller, a "
        "tourist photographing the water, a cyclist on the landside path. "
        "Casual contemporary clothing, late-afternoon golden hour. "
    ),
}


def get_people_snippet_pilot(arch_id: str) -> str:
    """Resolve activity-specific people description for an archetype.
    Checks the pilot-local map first, then the canonical ACTIVITY_PEOPLE."""
    if arch_id in PILOT_ACTIVITY_PEOPLE:
        return PILOT_ACTIVITY_PEOPLE[arch_id] + PEOPLE_CAMERA_SUFFIX
    for keyword, snippet in ACTIVITY_PEOPLE.items():
        if keyword in arch_id:
            return snippet + PEOPLE_CAMERA_SUFFIX
    # Fallback handled by LANDSCAPE_STYLE if needed
    return (
        "Include 5-8 fictional human characters naturally placed in the "
        "mid-ground of the scene, 15-40 meters from camera. Casual "
        "contemporary clothing in muted earth tones. Include at least one "
        "dog. " + PEOPLE_CAMERA_SUFFIX
    )


def build_pilot_card_description(arch: dict, variant: dict | None) -> str:
    """Build a rich card description matching generate_card_images.py
    load_openspace_archetypes() conventions."""
    title = arch.get("title", arch.get("id", ""))
    desc = arch.get("description", "")
    landscape = arch.get("landscapeDetail", {})

    if variant is None:
        out = f"{title}. {desc}"
    else:
        v_title = variant.get("label", "Variant")
        v_desc = variant.get("description", "")
        out = f"{title} — {v_title} variant. {v_desc}"

    if landscape.get("vegetation"):
        out += f" Vegetation: {landscape['vegetation']}."
    if landscape.get("hardscape"):
        out += f" Hardscape: {landscape['hardscape']}."
    if landscape.get("waterFeature"):
        out += f" Water: {landscape['waterFeature']}."
    if landscape.get("furniture"):
        out += f" Furniture: {landscape['furniture']}."

    out += " Surrounding context shows urban buildings in the background."
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=["openspaces", "streets"], default="openspaces")
    parser.add_argument("--id", required=True, help="archetype id (e.g. beer_garden)")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    json_name = "openSpaceArchetypes.json" if args.domain == "openspaces" else "streetPathArchetypes.json"
    catalog = json.loads((_DATA_DIR / json_name).read_text(encoding="utf-8"))

    arch = next((a for a in catalog["archetypes"] if a.get("id") == args.id), None)
    if arch is None:
        print(f"ERROR: archetype id={args.id!r} not found in {json_name}")
        return 1

    arch_title = arch.get("title", args.id)
    slug = _slugify(arch_title)
    out_dir = _PUBLIC_DIR / args.domain / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    people = get_people_snippet_pilot(args.id)
    variants = arch.get("variants", [])
    print(f"Pilot (Style 6 + people): {arch_title} -> {out_dir}")
    print(f"  {len(variants)} variants, slug={slug}")

    generated = failed = skipped = 0
    for vi, v in enumerate(variants):
        img_path = out_dir / f"variant_{vi}.png"
        if args.skip_existing and img_path.exists():
            print(f"  [{vi}] SKIP (exists): {img_path.name}")
            skipped += 1
            continue

        description = build_pilot_card_description(arch, v)
        prompt = LANDSCAPE_STYLE.format(description=description, people=people)

        print(f"\n  [{vi}] Generating: {v.get('label','?')}")
        print(f"      Prompt: {len(prompt)} chars")
        img_bytes = generate_image(prompt)
        if img_bytes is None:
            print(f"      FAILED")
            failed += 1
            continue

        resized = resize_to_card(img_bytes)
        img_path.write_bytes(resized)
        kb = img_path.stat().st_size / 1024
        print(f"      Saved {img_path.name} ({kb:.1f} KB)")
        generated += 1
        time.sleep(2)

    # No hero.png — UI only exposes the 4 variant slots, arch.thumbnailUrl
    # references variant_0.png directly. (See feedback_no_hero_image.md.)

    print(f"\nDone: generated={generated} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
