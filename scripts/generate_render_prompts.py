#!/usr/bin/env python3
"""Generate renderPrompt for building archetypes that are missing them,
replace vague styleProfile.materials with specific ones extracted from facadeDetail,
and trim verbose descriptions to <=120 chars.

Usage:
    python scripts/generate_render_prompts.py
    python scripts/generate_render_prompts.py --dry-run
"""

import json
import sys
from pathlib import Path

BUILDING_FILE = Path("frontend/src/data/buildingArchetypes.json")
OPEN_SPACE_FILE = Path("frontend/src/data/openSpaceArchetypes.json")

DRY_RUN = "--dry-run" in sys.argv

# Vague material patterns to replace
VAGUE_PATTERNS = [
    "material palette",
    "durable exterior",
    "high-quality glazing",
    "exterior materials",
    "premium glazing",
]

# Category-specific negative prompt additions
CATEGORY_NEGATIVES = {
    "classical": "modern glass, steel frame",
    "gothic": "modern glass, minimalist",
    "modernist": "ornate decoration, classical columns",
    "brutalism": "ornate decoration, warm materials, classical",
    "art_deco": "minimalist, brutalist",
    "industrial": "ornate decoration, classical columns",
    "victorian": "modern glass, minimalist, brutalist",
    "traditional": "modern glass, brutalist",
}

BASE_NEGATIVE = "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"


def first_clause(text: str, max_len: int = 60) -> str:
    """Extract first meaningful clause from a comma-separated description."""
    if not text:
        return ""
    parts = text.split(",")
    result = parts[0].strip()
    if len(result) > max_len:
        result = result[:max_len].rsplit(" ", 1)[0]
    return result


def generate_render_prompt(arch: dict) -> dict:
    """Generate a renderPrompt object from facadeDetail + roofDetail."""
    fd = arch.get("facadeDetail", {})
    rd = arch.get("roofDetail", {})
    title = arch.get("title", "building")
    min_f = arch.get("minFloors", 3)
    max_f = arch.get("maxFloors", 6)
    category = arch.get("aestheticCategory", arch.get("category", ""))

    # Build mapOverlay
    primary = fd.get("primaryMaterial", "")
    ground = fd.get("groundFloor", "")
    upper = fd.get("upperFloors", "")
    cornice = fd.get("cornice", "")
    color = fd.get("colorScheme", "")

    # Condense ground and upper floor to ~1 sentence each
    ground_short = first_clause(ground, 80)
    upper_short = first_clause(upper, 80)
    cornice_short = first_clause(cornice, 60)

    storeys = f"{min_f}-{max_f}" if min_f != max_f else str(min_f)

    parts = [
        f"Replace the colored building block with a photorealistic {title.lower()}.",
        f"Keep the exact same building footprint and height.",
        f"{first_clause(primary, 80)} facades",
    ]
    if ground_short:
        parts.append(f"with {ground_short}.")
    if upper_short:
        parts.append(f"{upper_short}.")
    if cornice_short:
        parts.append(f"{cornice_short}.")
    parts.append(f"{storeys} storey.")
    parts.append(
        "Maintain the surrounding satellite map context exactly as-is. "
        "Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k"
    )
    map_overlay = " ".join(parts)

    # Build roofView
    roof_form = rd.get("form", "flat roof")
    roof_mat = rd.get("material", "")
    roof_feat = rd.get("features", "")
    roof_parts = [
        f"Replace the colored block viewed from above with a {roof_form}",
    ]
    if roof_mat:
        roof_parts.append(f"with {first_clause(roof_mat, 60)}.")
    if roof_feat:
        roof_parts.append(f"{first_clause(roof_feat, 60)}.")
    roof_parts.append("Keep surrounding context exactly as-is.")
    roof_view = " ".join(roof_parts)

    # Build negative
    cat_neg = ""
    for key, neg in CATEGORY_NEGATIVES.items():
        if key in category.lower() or key in title.lower():
            cat_neg = neg
            break
    negative = f"{BASE_NEGATIVE}, {cat_neg}" if cat_neg else BASE_NEGATIVE

    return {
        "mapOverlay": map_overlay,
        "roofView": roof_view,
        "negative": negative,
    }


def extract_specific_materials(arch: dict) -> list[str]:
    """Extract specific material keywords from facadeDetail + roofDetail."""
    fd = arch.get("facadeDetail", {})
    rd = arch.get("roofDetail", {})

    materials = []
    for field in ["primaryMaterial", "secondaryMaterial", "accentMaterial"]:
        val = fd.get(field, "")
        if val:
            materials.append(first_clause(val, 50))

    roof_mat = rd.get("material", "")
    if roof_mat:
        materials.append(first_clause(roof_mat, 50))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for m in materials:
        m_lower = m.lower()
        if m_lower not in seen and m:
            seen.add(m_lower)
            unique.append(m)

    return unique[:5]


def is_vague_materials(materials: list) -> bool:
    """Check if materials array contains vague/generic entries."""
    if not materials:
        return True
    for mat in materials:
        for pattern in VAGUE_PATTERNS:
            if pattern in mat.lower():
                return True
    return False


def trim_description(desc: str, max_len: int = 120) -> str:
    """Trim description to max_len, preserving first sentence."""
    if not desc or len(desc) <= max_len:
        return desc
    # Try to cut at first sentence boundary
    for sep in [". ", "; ", " — ", " - "]:
        idx = desc.find(sep)
        if 0 < idx <= max_len:
            return desc[: idx + 1].rstrip()
    # Hard cut at word boundary
    trimmed = desc[:max_len].rsplit(" ", 1)[0]
    return trimmed


def process_buildings():
    """Process building archetypes."""
    with open(BUILDING_FILE, encoding="utf-8") as f:
        data = json.load(f)

    archetypes = data["archetypes"]
    prompts_added = 0
    materials_replaced = 0
    descriptions_trimmed = 0

    for arch in archetypes:
        aid = arch.get("id", "?")

        # Step 1: Generate missing renderPrompt
        if "renderPrompt" not in arch:
            prompt = generate_render_prompt(arch)
            arch["renderPrompt"] = prompt
            prompts_added += 1
            if DRY_RUN:
                print(f"\n[ADD renderPrompt] {aid}")
                print(f"  mapOverlay ({len(prompt['mapOverlay'])} chars): {prompt['mapOverlay'][:100]}...")
                print(f"  roofView ({len(prompt['roofView'])} chars): {prompt['roofView'][:80]}...")
                print(f"  negative: {prompt['negative'][:60]}...")

        # Step 2: Replace vague materials
        sp = arch.get("styleProfile", {})
        materials = sp.get("materials", [])
        if is_vague_materials(materials):
            new_materials = extract_specific_materials(arch)
            if new_materials:
                sp["materials"] = new_materials
                materials_replaced += 1
                if DRY_RUN:
                    print(f"\n[REPLACE materials] {aid}")
                    print(f"  OLD: {materials}")
                    print(f"  NEW: {new_materials}")

        # Step 4: Trim verbose descriptions
        desc = arch.get("description", "")
        if len(desc) > 120:
            trimmed = trim_description(desc)
            arch["description"] = trimmed
            descriptions_trimmed += 1
            if DRY_RUN:
                print(f"\n[TRIM description] {aid}")
                print(f"  {len(desc)} -> {len(trimmed)} chars")

    print(f"\n=== BUILDINGS SUMMARY ===")
    print(f"  renderPrompts added: {prompts_added}")
    print(f"  materials replaced:  {materials_replaced}")
    print(f"  descriptions trimmed: {descriptions_trimmed}")

    if not DRY_RUN:
        with open(BUILDING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {BUILDING_FILE}")

    return prompts_added, materials_replaced, descriptions_trimmed


def process_open_spaces():
    """Process open space archetypes — just community_garden_enhanced."""
    with open(OPEN_SPACE_FILE, encoding="utf-8") as f:
        data = json.load(f)

    archetypes = data["archetypes"]
    fixed = 0
    trimmed = 0

    for arch in archetypes:
        aid = arch.get("id", "?")

        if "renderPrompt" not in arch:
            sp = arch.get("styleProfile", {})
            lc = sp.get("landscapeCharacter", arch.get("description", ""))
            title = arch.get("title", "open space")

            prompt = {
                "mapOverlay": (
                    f"Replace the colored zone with a photorealistic {title.lower()}. "
                    f"Keep the exact same zone footprint. {first_clause(lc, 120)}. "
                    f"Maintain the surrounding satellite map context exactly as-is. "
                    f"Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k"
                ),
                "negative": BASE_NEGATIVE,
            }
            arch["renderPrompt"] = prompt
            fixed += 1
            if DRY_RUN:
                print(f"\n[ADD renderPrompt] {aid}")
                print(f"  mapOverlay: {prompt['mapOverlay'][:100]}...")

        desc = arch.get("description", "")
        if len(desc) > 120:
            arch["description"] = trim_description(desc)
            trimmed += 1

    print(f"\n=== OPEN SPACES SUMMARY ===")
    print(f"  renderPrompts added: {fixed}")
    print(f"  descriptions trimmed: {trimmed}")

    if not DRY_RUN:
        with open(OPEN_SPACE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {OPEN_SPACE_FILE}")


def process_streets():
    """Process street archetypes — just trim descriptions."""
    street_file = Path("frontend/src/data/streetPathArchetypes.json")
    with open(street_file, encoding="utf-8") as f:
        data = json.load(f)

    archetypes = data.get("archetypes", data.get("streetTypes", []))
    trimmed = 0

    for arch in archetypes:
        desc = arch.get("description", "")
        if len(desc) > 120:
            arch["description"] = trim_description(desc)
            trimmed += 1

    print(f"\n=== STREETS SUMMARY ===")
    print(f"  descriptions trimmed: {trimmed}")

    if not DRY_RUN:
        with open(street_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {street_file}")


if __name__ == "__main__":
    print(f"{'DRY RUN' if DRY_RUN else 'LIVE RUN'} — generate_render_prompts.py")
    print(f"{'=' * 50}")

    process_buildings()
    process_open_spaces()
    process_streets()

    print(f"\n{'=' * 50}")
    print("Done!")
