#!/usr/bin/env python3
"""
Insert `developmentType` into archetypes that are missing it (typically the
52 orphan stubs I added). The UI picker filters by `developmentType`, so
without this field the stubs fall into a default bucket and appear under
wrong categories (e.g., "Single Family" when they're mid-rise or industrial).

Text-level regex insertion — never json.dump (per CLAUDE.md).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"


# Map the 19 new buildingSubcategory labels to valid developmentType values
# that the UI dropdown already recognizes.
SUBCAT_TO_DEVTYPE = {
    "Residential — Detached / Single-Family": "residential_single_family",
    "Residential — Rowhouse / Townhouse / Terrace": "residential_duplex",
    "Residential — Mid-Rise Apartment": "residential_multifamily",
    "Residential — High-Rise / Tower": "residential_highrise",
    "Commercial — Main Street / Heritage Retail": "commercial_retail",
    "Commercial — Office / Office Tower": "commercial_office",
    "Commercial — Mixed-Use Mid-Rise": "mixed_use",
    "Commercial — Market / Specialty Retail": "commercial_retail",
    "Industrial": "industrial_light",
    "Civic / Institutional": "institutional",
    "Education": "institutional_education",
    "Transportation": "transit_station",
    "Entertainment / Culture": "sports_arena",
    "Recreation": "recreational",
    "Hospitality": "hotel",
    "Healthcare": "institutional_health",
    "Energy / Infrastructure": "energy_infrastructure",
    "Agriculture": "other",
    "Custom / Other": "other",
}


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    d = json.loads(CATALOG.read_text(encoding="utf-8"))
    archs = d.get("archetypes", [])

    # Find archetypes missing developmentType
    missing = [a for a in archs if not a.get("developmentType")]
    print(f"{len(missing)} archetypes missing developmentType (of {len(archs)} total)")

    if not missing:
        print("All archetypes already have developmentType. Nothing to do.")
        return 0

    text = CATALOG.read_text(encoding="utf-8")
    inserted = 0
    skipped = []

    for a in missing:
        aid = a.get("id") or ""
        subcat = a.get("buildingSubcategory") or ""
        devtype = SUBCAT_TO_DEVTYPE.get(subcat)
        if not devtype:
            skipped.append(f"{aid} (subcat={subcat!r} not in map)")
            continue

        # Insert `"developmentType": "<val>",` right after the buildingSubcategory line.
        # The field format in orphan stubs is:
        #     "buildingSubcategory": "<value>",
        # We append a new line with matching indent.
        pattern = re.compile(
            r'("id"\s*:\s*"' + re.escape(aid) + r'"\s*,[^}]*?"buildingSubcategory"\s*:\s*"[^"]*",)(\s*\n)(\s+)',
            re.DOTALL
        )
        replacement = r'\g<1>\g<2>\g<3>"developmentType": "' + devtype + r'",\n\g<3>'
        new_text, n = pattern.subn(replacement, text, count=1)
        if n == 0:
            skipped.append(f"{aid} (regex didn't match)")
            continue
        text = new_text
        inserted += 1

    # Validate
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ABORT: resulting JSON does not parse: {e}")
        return 1

    # Verify thumbnailUrl count unchanged
    old_thumbs = sum(1 for a in archs for v in a.get("variants", []) if v.get("thumbnailUrl"))
    new_thumbs = sum(1 for a in parsed.get("archetypes", []) for v in a.get("variants", []) if v.get("thumbnailUrl"))
    if old_thumbs != new_thumbs:
        print(f"ABORT: thumbnailUrl count changed {old_thumbs} -> {new_thumbs}")
        return 1

    # Verify developmentType is now present
    still_missing = sum(1 for a in parsed.get("archetypes", []) if not a.get("developmentType"))
    print(f"Inserted developmentType for {inserted} archetypes")
    print(f"Still missing after pass: {still_missing}")
    if skipped:
        print(f"Skipped {len(skipped)}:")
        for s in skipped[:10]:
            print(f"  ! {s}")

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return 0

    backup = CATALOG.with_suffix(CATALOG.suffix + ".bak-devtype")
    backup.write_bytes(CATALOG.read_bytes())
    CATALOG.write_text(text, encoding="utf-8")
    print(f"Backup saved to {backup.name}")
    print(f"Catalog updated at {CATALOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
