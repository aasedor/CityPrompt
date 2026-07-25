"""
Phase 3A — Per-variant scale on 5 priority archetypes.

Adds minFloors/maxFloors/suggestedFloorHeight/suggestedAreaSqm to specific
variants identified by id. Where a parent's range needs widening to envelope
the new variant scales, the parent is widened first.

Targets (all from docs/ARCHETYPE_SIZES_FIX_PLAN_2026_04_28.md §3.1):
  - art_deco_setback_tower       (parent 8-25  -> 8-55)
  - glass_tower_modern           (parent stays 12-50)
  - parametric_future_hub        (parent 5-30  -> 5-50)
  - autonomous_tech_campus       (parent 3-10  -> 1-10)
  - boutique_hotel               (parent 3-20  -> 3-22)

Uses TEXT-LEVEL splice (per CLAUDE.md). Validates JSON parses & confirms
each target variant gained the fields.
"""

from __future__ import annotations

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG = "frontend/src/data/buildingArchetypes.json"

# Parent floor-range widenings: archetype_id -> (new_minFloors, new_maxFloors).
# Only specify when widening — leave entries the same to preserve.
PARENT_WIDENS = {
    "art_deco_setback_tower":   (8,  55),
    "parametric_future_hub":    (5,  50),
    "autonomous_tech_campus":   (1,  10),
    "boutique_hotel":           (3,  22),
    # glass_tower_modern stays 12-50 (already widened in Phase 1.2)
}

# Per-variant scale specs, keyed by variant id.
VARIANT_SPECS = {
    # art_deco_setback_tower  (4 variants, all need scale)
    "art_deco_cream_terracotta":   {"minFloors": 35, "maxFloors": 55, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},  # Chrysler-class
    "art_deco_black_chrome":       {"minFloors": 20, "maxFloors": 35, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},
    "art_deco_polychrome":         {"minFloors": 30, "maxFloors": 45, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},  # Empire-State-ish
    "art_deco_streamline_moderne": {"minFloors":  8, "maxFloors": 15, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},  # low-rise sleek

    # glass_tower_modern  (4 placeholder variants — descriptions unchanged, just
    # giving them scale spans so the catalog gets some per-variant differentiation)
    "glass_tower_modern_variant_0": {"minFloors": 18, "maxFloors": 30, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},
    "glass_tower_modern_variant_1": {"minFloors": 30, "maxFloors": 50, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},
    "glass_tower_modern_variant_2": {"minFloors": 12, "maxFloors": 22, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},
    "glass_tower_modern_variant_3": {"minFloors": 35, "maxFloors": 50, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},

    # parametric_future_hub  (4 variants; diagrid_tower already has scale → skip)
    "parametric_fluid_organic":    {"minFloors":  5, "maxFloors": 15, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2500},
    "parametric_voronoi_lattice":  {"minFloors": 10, "maxFloors": 25, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2500},
    "parametric_kinetic_facade":   {"minFloors": 15, "maxFloors": 35, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2500},

    # autonomous_tech_campus  (4 variants; silicon_valley + data_center already have scale → skip)
    "tech_campus_biophilic":       {"minFloors":  4, "maxFloors":  7, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 10000},
    "tech_campus_research_lab":    {"minFloors":  5, "maxFloors": 10, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 12000},

    # boutique_hotel  (4 variants, all already have scale → no inserts)
}


def find_archetypes_array_start(text: str) -> int:
    m = re.search(r'"archetypes"\s*:\s*\[', text)
    if not m:
        raise ValueError("Could not find archetypes array")
    return m.end()


def widen_parent_floor_range(text: str, slug: str, new_min: int, new_max: int,
                              archetypes_start: int) -> str:
    """Replace the parent-level minFloors/maxFloors block for the given slug."""
    # Find the slug's archetype block (skip past data.categories)
    slug_pos = text.index(f'"id": "{slug}"', archetypes_start)
    # Find next archetype boundary
    next_arch = re.search(r'\n    \{', text[slug_pos:])
    block_end = slug_pos + next_arch.start() if next_arch else len(text)
    block = text[slug_pos:block_end]

    # The parent-level minFloors/maxFloors are at the OUTER scope, not inside
    # variants. Schema generations in this catalog vary indentation between
    # 6-space and 8-space; match either. We require both lines to share the
    # same indent (so we don't accidentally match a variant's fields).
    parent_pat = re.compile(
        r'^( {6,8})"minFloors":\s*\d+,\n\1"maxFloors":\s*\d+,',
        re.MULTILINE,
    )
    m = parent_pat.search(block)
    if not m:
        raise ValueError(f"Could not find parent minFloors/maxFloors block for {slug}")

    indent = m.group(1)
    new_lines = f'{indent}"minFloors": {new_min},\n{indent}"maxFloors": {new_max},'
    new_block = block[:m.start()] + new_lines + block[m.end():]
    return text[:slug_pos] + new_block + text[block_end:]


def insert_variant_scale(text: str, variant_id: str, specs: dict,
                         archetypes_start: int) -> tuple[str, str]:
    """Insert minFloors/maxFloors/suggestedFloorHeight/suggestedAreaSqm into the
    given variant. Returns (new_text, status) where status is 'applied', 'skipped', or 'not_found'."""
    needle = f'"id": "{variant_id}"'
    pos = text.find(needle, archetypes_start)
    if pos < 0:
        return text, "not_found"

    # Determine the variant block: from this variant's `"id":` line to the
    # next sibling variant's opening brace (or the variants array's `]`).
    # This is bounded enough to safely check for "minFloors" and find thumbnailUrl.
    nxt = re.search(r'\n( {8,12}\{)|(\n {6,8}\])', text[pos:pos+8000])
    end = pos + nxt.start() if nxt else min(pos + 8000, len(text))

    variant_block = text[pos:end]
    if '"minFloors"' in variant_block:
        return text, "skipped"

    # Find the variant's `"thumbnailUrl"` line — insert after it
    # (matches the existing apply_variant_specs.py convention)
    thumb_match = re.search(r'^( +)"thumbnailUrl":\s*"[^"]*"\s*,?\s*\n', variant_block, re.MULTILINE)
    if not thumb_match:
        return text, "not_found"
    indent = thumb_match.group(1)
    thumb_end = pos + thumb_match.end()

    # Ensure the thumbnailUrl line ends with a comma
    # (find the comma OR the position of newline)
    thumb_line_text = variant_block[thumb_match.start():thumb_match.end()]
    if not thumb_line_text.rstrip("\n").rstrip().endswith(","):
        # The thumbnail line lacks a trailing comma — add one
        # Insert the comma at the end of the thumbnailUrl line
        # Find position of the closing quote
        # Easier: rebuild by replacing the line
        new_thumb_line = thumb_line_text.rstrip("\n").rstrip() + ',\n'
        text = text[:pos + thumb_match.start()] + new_thumb_line + text[pos + thumb_match.end():]
        # Recompute thumb_end after insertion
        thumb_end = pos + thumb_match.start() + len(new_thumb_line)

    # Build the lines to insert
    inserts = (
        f'{indent}"minFloors": {specs["minFloors"]},\n'
        f'{indent}"maxFloors": {specs["maxFloors"]},\n'
        f'{indent}"suggestedFloorHeight": {specs["suggestedFloorHeight"]},\n'
        f'{indent}"suggestedAreaSqm": {specs["suggestedAreaSqm"]},\n'
    )
    return text[:thumb_end] + inserts + text[thumb_end:], "applied"


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        text = f.read()

    # baseline parse
    json.loads(text)
    archetypes_start = find_archetypes_array_start(text)

    print("== Widening parent floor ranges ==")
    for slug, (new_min, new_max) in PARENT_WIDENS.items():
        try:
            text = widen_parent_floor_range(text, slug, new_min, new_max, archetypes_start)
            print(f"  OK   {slug}: parent floors -> {new_min}-{new_max}")
        except Exception as e:
            print(f"  FAIL {slug}: {e}")

    # parse-check after parent edits
    json.loads(text)
    archetypes_start = find_archetypes_array_start(text)  # may have shifted

    print("\n== Inserting per-variant scale ==")
    applied = 0
    skipped = 0
    not_found = 0
    for variant_id, specs in VARIANT_SPECS.items():
        text, status = insert_variant_scale(text, variant_id, specs, archetypes_start)
        if status == "applied":
            print(f"  OK   {variant_id}: floors {specs['minFloors']}-{specs['maxFloors']}, fh={specs['suggestedFloorHeight']}, area={specs['suggestedAreaSqm']}")
            applied += 1
        elif status == "skipped":
            print(f"  SKIP {variant_id}: already has scale")
            skipped += 1
        else:
            print(f"  NOT FOUND: {variant_id}")
            not_found += 1
        # archetypes_start may have shifted; recompute on each iteration to be safe
        archetypes_start = find_archetypes_array_start(text)

    # Final parse + sanity
    data = json.loads(text)
    print()
    print(f"Result: {applied} variant scale inserts, {skipped} skipped, {not_found} not found")

    # Confirm targets all carry per-variant scale now
    archs_by_id = {a["id"]: a for a in data["archetypes"]}
    print()
    print("== Verification ==")
    for parent_id in ("art_deco_setback_tower", "glass_tower_modern", "parametric_future_hub",
                      "autonomous_tech_campus", "boutique_hotel"):
        a = archs_by_id[parent_id]
        n_with = sum(1 for v in a.get("variants", []) if "minFloors" in v)
        n_total = len(a.get("variants", []))
        print(f"  {parent_id}: parent {a['minFloors']}-{a['maxFloors']}, "
              f"{n_with}/{n_total} variants have scale")

    with open(CATALOG, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("\nWritten.")


if __name__ == "__main__":
    main()
