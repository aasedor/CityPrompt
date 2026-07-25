#!/usr/bin/env python3
"""
Tag all archetypes with a districtKit field based on ID prefix.

Usage:
    python scripts/tag_district_kits.py --dry-run
    python scripts/tag_district_kits.py
"""

import json
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILES = [
    PROJECT_ROOT / "frontend/src/data/buildingArchetypes.json",
    PROJECT_ROOT / "frontend/src/data/streetPathArchetypes.json",
    PROJECT_ROOT / "frontend/src/data/openSpaceArchetypes.json",
]

# Prefix → kit mapping
KIT_PREFIXES = [
    ("parisian_", "paris"),
    ("amsterdam_", "amsterdam"),
    ("barcelona_", "barcelona"),
    ("london_", "london"),
    ("newyork_", "new_york"),
    ("montreal_", "montreal"),
    ("vancouver_", "vancouver"),
    ("toronto_", "toronto"),
    ("calgary_", "calgary"),
    ("halifax_", "halifax"),
    # Also catch existing archetypes with these patterns
    ("brownstone_", "new_york"),
    ("civic_classical", "classic"),
    ("modern_glass", "classic"),
    ("industrial_brick", "classic"),
    ("adaptive_reuse", "classic"),
    ("contemporary_", "classic"),
    ("scandinavian_", "copenhagen"),
    ("nordic_", "copenhagen"),
    ("mediterranean_", "mediterranean"),
    ("shophouse_", "singapore"),
]


def detect_kit(archetype_id: str) -> str | None:
    """Detect district kit from archetype ID prefix."""
    for prefix, kit in KIT_PREFIXES:
        if archetype_id.startswith(prefix):
            return kit
    return None


def process_file(filepath: Path):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    archetypes = data.get("archetypes", data.get("streetTypes", data.get("openSpaceTypes", [])))
    tagged = 0
    already = 0

    for arch in archetypes:
        aid = arch.get("id", "?")
        existing_kit = arch.get("districtKit")

        if existing_kit is not None:
            already += 1
            continue

        kit = detect_kit(aid)
        arch["districtKit"] = kit
        tagged += 1

        if DRY_RUN and kit:
            print(f"  {aid} -> {kit}")

    print(f"  {filepath.name}: {tagged} tagged, {already} already had kit")

    if not DRY_RUN:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main():
    print(f"{'DRY RUN' if DRY_RUN else 'LIVE RUN'} — tag_district_kits.py")
    print(f"{'=' * 50}")

    for filepath in FILES:
        print(f"\n{filepath.name}:")
        process_file(filepath)

    print(f"\n{'=' * 50}")
    print("Done!")


if __name__ == "__main__":
    main()
