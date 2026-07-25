#!/usr/bin/env python3
"""
Add true-orphan archetype folders (on disk but not in the JSON catalog) to
buildingArchetypes.json / openSpaceArchetypes.json.

Uses TEXT-LEVEL INSERTION ONLY — never json.dump the whole catalog (corrupts
thumbnailUrl paths per CLAUDE.md). Each new archetype stub is serialized via
json.dumps on a single dict, then spliced into the file before the closing
`]` of the archetypes array.

Usage:
    python scripts/add_orphans_to_catalog.py --dry-run      # print stubs only
    python scripts/add_orphans_to_catalog.py                # perform insertion
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "frontend" / "public" / "archetypes"
DATA_DIR = ROOT / "frontend" / "src" / "data"

CATALOGS = {
    "buildings": DATA_DIR / "buildingArchetypes.json",
    "openspaces": DATA_DIR / "openSpaceArchetypes.json",
}


# -----------------------------------------------------------------------------
# Subcategory / aestheticCategory inference from folder-name keywords
# -----------------------------------------------------------------------------

BUILDING_SUBCATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Office / Institutional", ["office", "faculty", "administrative", "corporate"]),
    ("Health Care", ["hospital", "medical", "healthcare", "natatorium"]),
    ("Educational / Institutional", ["university", "academic", "student", "graduate", "campus", "library", "research", "laboratory", "science"]),
    ("Transit / Aviation", ["airport", "terminal", "vertiport", "station", "transit"]),
    ("Industrial", ["brewery", "distillery", "industrial", "factory", "warehouse", "data center", "fulfillment"]),
    ("Mixed-Use Residential", ["coastal", "eco", "mixed-use", "mixed_use"]),
    ("Townhouse / Rowhouse", ["rowhouse", "row-house", "terrace", "streetwall", "brownstone"]),
    ("Detached Residential", ["mansion", "bungalow", "lanehouse", "infill", "foursquare", "chalet", "cottage", "villa"]),
    ("High-Rise Office / Commercial", ["tower", "high-rise", "office-cluster", "skyline"]),
    ("Hospitality / Hotel", ["hotel", "resort", "lodge", "hospitality"]),
    ("Civic / Institutional", ["museum", "courthouse", "civic", "cultural", "institutional", "monument", "neoclassical"]),
    ("Sports / Arena", ["arena", "stadium", "aquatic", "climbing", "athletics"]),
    ("Recreation / Community", ["rec-centre", "recreation", "community", "community-centre"]),
    ("Convention / Exhibition", ["convention", "exhibition"]),
    ("Infrastructure", ["energy-centre", "utilities", "waste-to-energy", "ev-charging", "fire-station", "solar"]),
    ("Market Hall / Commercial", ["market", "food-hall", "shophouse", "d�panneur"]),
    ("Condo Podium Tower", ["podium", "condo"]),
    ("Senior Living / Assisted Living", ["senior", "assisted"]),
    ("Custom", []),
]


OS_CATEGORY_KEYWORDS: list[tuple[tuple[str, str], list[str]]] = [
    # ((spaceType, aestheticCategory), keywords)
    (("park", "sports_recreation"), ["athletic", "multi-sport", "velodrome", "bike-park", "driving-range", "golf", "playground", "splash-pad", "equestrian"]),
    (("park", "specialty_gardens"), ["garden", "community-garden", "teaching-arboretum", "research-garden"]),
    (("park", "ecological_resilience"), ["wetland", "stormwater", "rewilding", "riparian", "restoration"]),
    (("park", "social_event_spaces"), ["amphitheater", "performance"]),
    (("plaza", "civic_plazas"), ["quad", "academic-courtyard", "courtyard-plaza", "campus-pedestrian-spine", "campus-central"]),
    (("plaza", "parking_areas"), ["parking", "airfield", "underground-parking"]),
    (("park", "landscape_parks"), ["fountain"]),
    (("park", "neighborhood_public_realm"), []),
]


def infer_building_subcategory(slug: str) -> str:
    s = slug.lower()
    for cat, kws in BUILDING_SUBCATEGORY_KEYWORDS:
        for kw in kws:
            if kw in s:
                return cat
    return "Custom"


def infer_os_category(slug: str) -> tuple[str, str]:
    s = slug.lower()
    for (space_type, aesth), kws in OS_CATEGORY_KEYWORDS:
        for kw in kws:
            if kw in s:
                return space_type, aesth
    return "park", "neighborhood_public_realm"


def slug_to_title(slug: str) -> str:
    words = slug.replace("_", " ").replace("-", " ").split()
    # Title-case each word; keep small joining words lowercase unless first
    small = {"a", "an", "and", "of", "the", "for", "with", "to", "on", "in"}
    out = []
    for i, w in enumerate(words):
        if i > 0 and w.lower() in small:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def slug_to_id(slug: str) -> str:
    # Use underscore form for the id (most common convention in existing catalog)
    return slug.replace("-", "_")


def build_building_stub(folder: Path) -> dict:
    slug = folder.name
    variants = sorted(folder.glob("variant_*.png"))
    arch_id = slug_to_id(slug)
    title = slug_to_title(slug)
    subcat = infer_building_subcategory(slug)

    variant_entries = []
    for i, v in enumerate(variants):
        vid = v.stem  # e.g., variant_0
        variant_entries.append({
            "id": f"{arch_id}_{vid}",
            "label": f"Style Variant {i + 1}",
            "description": f"{title} — style variant {i + 1}.",
            "thumbnailUrl": f"/archetypes/buildings/{slug}/{v.name}",
            "color": ["#4A6B8A", "#8A6B4A", "#5B7065", "#6B4A8A"][i % 4],
        })

    return {
        "id": arch_id,
        "title": title,
        "buildingSubcategory": subcat,
        "description": f"A {title} archetype.",
        "suggestedWidth_m": 30,
        "suggestedDepth_m": 20,
        "minFloors": 2,
        "maxFloors": 6,
        "thumbnailUrl": f"/archetypes/buildings/{slug}/hero.png",
        "variants": variant_entries,
    }


def build_openspace_stub(folder: Path) -> dict:
    slug = folder.name
    variants = sorted(folder.glob("variant_*.png"))
    arch_id = slug_to_id(slug)
    title = slug_to_title(slug)
    space_type, aesth = infer_os_category(slug)

    variant_entries = []
    for i, v in enumerate(variants):
        vid = v.stem
        variant_entries.append({
            "id": f"{arch_id}_{vid}",
            "label": f"Style Variant {i + 1}",
            "color": ["#8B6914", "#5B7065", "#6B8A4A", "#8A6B4A"][i % 4],
            "description": f"{title} — style variant {i + 1}.",
            "thumbnailUrl": f"/archetypes/openspaces/{slug}/{v.name}",
        })

    return {
        "id": arch_id,
        "title": title,
        "spaceType": space_type,
        "aestheticCategory": aesth,
        "description": f"A {title}.",
        "suggestedWidth_m": 40,
        "suggestedDepth_m": 30,
        "suggestedAreaSqm": 1200,
        "thumbnailUrl": f"/archetypes/openspaces/{slug}/hero.png",
        "shape": "rectangular",
        "generationTags": [aesth.replace("_", "-")],
        "variants": variant_entries,
    }


def find_true_orphans(kind: str) -> list[Path]:
    """Return folder paths for orphans (on disk but not in catalog), excluding
    naming twins. When BOTH the hyphenated and underscored version of a slug
    exist as orphans, pick the one with more PNG content (tiebreak: underscored).

    Also filters out any orphan whose generated id would collide with an
    existing archetype id in the catalog (e.g., an orphan folder
    `amphitheater-lawn` whose slug_to_id=`amphitheater_lawn` collides with an
    existing catalog entry with that id but a different folder path).
    """
    catalog_path = CATALOGS[kind]
    d = json.loads(catalog_path.read_text(encoding="utf-8"))
    archs = d.get("archetypes", d)
    catalog_slugs: set[str] = set()
    catalog_ids: set[str] = set()
    for a in archs:
        aid = a.get("id")
        if aid:
            catalog_ids.add(aid)
        for v in a.get("variants", []):
            t = v.get("thumbnailUrl", "")
            if t.startswith("/archetypes/"):
                parts = t.strip("/").split("/")
                if len(parts) >= 3 and parts[1] == kind:
                    catalog_slugs.add(parts[2])

    fs_dir = PUBLIC / kind
    on_disk = {p.name for p in fs_dir.iterdir() if p.is_dir()}
    orphans = on_disk - catalog_slugs
    # Exclude naming twins of CATALOG entries (handled separately via cleanup)
    orphans = {
        o for o in orphans
        if o.replace("-", "_") not in catalog_slugs
        and o.replace("_", "-") not in catalog_slugs
    }
    # Dedupe hyphen/underscore pairs among orphans themselves.
    # Key each orphan by its underscored normal form; pick winner with more
    # PNG content (tiebreak: the underscored version wins).
    groups: dict[str, list[str]] = {}
    for o in orphans:
        key = o.replace("-", "_")
        groups.setdefault(key, []).append(o)

    chosen: list[str] = []
    for key, names in groups.items():
        if len(names) == 1:
            chosen.append(names[0])
        else:
            def rank(n: str) -> tuple[int, int]:
                folder = fs_dir / n
                pngs = len(list(folder.glob("*.png")))
                is_underscored = 1 if "-" not in n else 0
                return (pngs, is_underscored)
            names.sort(key=rank, reverse=True)
            chosen.append(names[0])

    chosen.sort()
    # Drop orphans whose generated id would collide with an existing catalog
    # archetype id. These are typically catalog entries whose folder path
    # differs from the id (e.g., id=amphitheater_lawn, folder=amphitheater-
    # performance-lawn, AND a separate orphan folder amphitheater-lawn).
    chosen = [o for o in chosen if slug_to_id(o) not in catalog_ids]
    # Only include orphans that have actual PNG content
    return [fs_dir / o for o in chosen if (fs_dir / o / "hero.png").exists() or list((fs_dir / o).glob("variant_*.png"))]


def splice_stubs_into_catalog(catalog_path: Path, stubs: list[dict]) -> None:
    """Append new archetype stubs into the `archetypes` array via text-level insertion.

    Never json.dump the whole catalog (corrupts thumbnailUrl paths per
    CLAUDE.md). Instead: serialize each stub individually with json.dumps,
    then splice raw text before the closing `]` of the archetypes array.
    """
    text = catalog_path.read_text(encoding="utf-8")

    # Find the insertion point: the closing `]` of the archetypes array.
    # This is the LAST `]` in the file (the file ends with `]\n}\n`).
    close_bracket = text.rfind("]")
    if close_bracket < 0:
        raise RuntimeError(f"No closing `]` found in {catalog_path}")

    # Walk backward from the `]` to skip whitespace and find where the last
    # archetype entry ends (should be a `}`).
    insertion_point = close_bracket
    while insertion_point > 0 and text[insertion_point - 1] in " \t\r\n":
        insertion_point -= 1
    # insertion_point now sits right after the last `}` of the last archetype
    # (or right after the `[` if the array was empty).

    # Build the new text
    new_entries_text = ""
    for stub in stubs:
        new_entries_text += ",\n    " + json.dumps(stub, ensure_ascii=False, indent=4).replace("\n", "\n    ")

    new_text = text[:insertion_point] + new_entries_text + "\n  " + text[close_bracket:]

    # Validate by parsing
    try:
        parsed = json.loads(new_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Resulting JSON does not parse: {e}") from e

    # Sanity-check: number of archetypes grew by expected amount
    new_archs = parsed.get("archetypes", [])
    print(f"  Catalog now has {len(new_archs)} archetypes (inserted {len(stubs)}).")

    # Backup + write
    backup = catalog_path.with_suffix(catalog_path.suffix + ".bak")
    backup.write_bytes(catalog_path.read_bytes())
    catalog_path.write_text(new_text, encoding="utf-8")
    print(f"  Backup saved to {backup.name}")


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    all_stubs: dict[str, list[dict]] = {}
    for kind in ("buildings", "openspaces"):
        orphans = find_true_orphans(kind)
        print(f"\n=== {kind.upper()}: {len(orphans)} true orphans ===")
        stubs = []
        for folder in orphans:
            if kind == "buildings":
                stub = build_building_stub(folder)
            else:
                stub = build_openspace_stub(folder)
            stubs.append(stub)
            detail = stub.get("buildingSubcategory") or f'{stub["spaceType"]}/{stub["aestheticCategory"]}'
            print(f"  - {stub['id']}  [{detail}]  (variants: {len(stub['variants'])})")
        all_stubs[kind] = stubs

    if dry_run:
        print("\n[DRY RUN] No files modified.")
        return 0

    # Perform splicing
    for kind, stubs in all_stubs.items():
        if not stubs:
            continue
        print(f"\nSplicing {len(stubs)} stubs into {CATALOGS[kind].name}...")
        splice_stubs_into_catalog(CATALOGS[kind], stubs)

    print("\nDone. Verify:")
    print("  1. App loads without catalog errors")
    print("  2. New archetypes appear in the UI picker")
    print("  3. Backups are at buildingArchetypes.json.bak / openSpaceArchetypes.json.bak")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
