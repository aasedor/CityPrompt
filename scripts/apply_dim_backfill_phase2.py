"""
Phase 2.1 — Backfill min/maxWidth_m, min/maxDepth_m, aspectRatio on the 51
archetypes that already carry suggestedWidth_m/suggestedDepth_m but lack the
min/max envelopes.

Uses TEXT-LEVEL splice (per CLAUDE.md): inserts the missing fields right after
the existing `"suggestedDepth_m":` line. Skips any archetype that already has
`minWidth_m` defined.

Default ranges chosen by:
  min = 0.55 * suggested  (rounded to nice integer)
  max = 1.7  * suggested  (rounded to nice integer)
  aspectRatio derived from the W:D ratio of the suggested values.

Manual overrides for archetypes whose typology demands a wider/tighter range
than the formula suggests (e.g. boutique_hotel, outdoor_sports_stadium).

Validates JSON parses before & after. Confirms each target's fields landed.
"""

from __future__ import annotations

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG = "frontend/src/data/buildingArchetypes.json"

# id -> (minW, maxW, minD, maxD, aspectRatio)
# Manually tuned for each archetype's typology — formula default is min=0.55x,
# max=1.7x of suggested, with overrides where the typology range is wider or
# tighter than the formula gives.
DIMS = {
    "administrative_faculty_office_building": (18, 50, 12, 35, "3:2"),
    "airport_terminal_building":              (50, 200, 35, 150, "4:3"),   # wide
    "annex_mansion":                          (11, 25, 12, 28, "1:1.1"),
    "aquatic_natatorium_complex":             (50, 120, 35, 80, "16:11"),
    "bay_and_gable_house":                    (6, 12, 10, 18, "1:1.5"),
    "biophilic_modern_healthcare":            (25, 60, 18, 45, "4:3"),
    "boutique_hotel":                         (12, 60, 10, 50, "1.1:1"),    # wide span (3-storey courtyard to 22-storey tower)
    "brick_rowhouse_terrace":                 (10, 30, 8, 18, "3:2"),
    "calgary_15_connected_tower":             (30, 65, 28, 60, "9:8"),
    "campus_dining_hall_food_court":          (25, 60, 18, 42, "10:7"),
    "campus_lecture_hall_complex":            (30, 80, 25, 60, "5:4"),
    "campus_parking_structure":               (35, 90, 25, 60, "11:7"),
    "campus_recreation_athletics_centre":     (40, 100, 30, 70, "4:3"),
    "central_utilities_plant_energy_centre":  (22, 55, 18, 45, "5:4"),
    "chateauesque_grand_railway_hotel":       (50, 130, 35, 95, "4:3"),     # wide for grand railway hotels
    "collegiate_gothic":                      (25, 70, 18, 40, "8:5"),
    "condo_podium_tower":                     (25, 60, 18, 45, "4:3"),
    "contemporary_midrise":                   (14, 35, 12, 30, "11:10"),
    "convention_exhibition_center":           (50, 200, 35, 150, "4:3"),    # very wide
    "corner_dépanneur":                       (8, 18, 9, 20, "1:1.2"),
    "corporate_office_campus_headquarters":   (25, 80, 20, 60, "9:7"),
    "cruise_ferry_terminal":                  (70, 200, 35, 100, "2:1"),
    "e_commerce_fulfillment_center":          (70, 250, 50, 180, "3:2"),    # very wide
    "early_20th_century_megastructure":       (50, 150, 40, 110, "4:3"),
    "edwardian_foursquare":                   (8, 16, 10, 18, "1:1.2"),
    "ev_charging_hub_mobility_station":       (20, 55, 16, 45, "5:4"),
    "glass_tower_modern":                     (20, 50, 14, 35, "3:2"),
    "graduate_family_housing":                (25, 65, 16, 40, "8:5"),
    "high_tech_structural_arena":             (80, 200, 70, 180, "6:5"),
    "intermodal_transit_hub":                 (50, 150, 35, 100, "4:3"),
    "junction_converted_industrial_loft":     (22, 60, 18, 50, "9:7"),
    "large_art_museum_gallery":               (50, 130, 35, 100, "4:3"),
    "mid_century_distribution_warehouse":     (30, 80, 22, 60, "9:7"),
    "modern_big_box_logistics":               (50, 200, 40, 150, "4:3"),    # very wide
    "outdoor_sports_stadium":                 (80, 350, 60, 300, "10:9"),   # very wide span
    "parisian_mid_rise":                      (22, 55, 14, 35, "8:5"),
    "parkitecture":                           (14, 35, 10, 25, "11:8"),
    "postmodern_community_rec_centre":        (25, 65, 18, 50, "4:3"),
    "regional_hospital_medical_center":       (40, 120, 28, 90, "3:2"),
    "research_laboratory":                    (25, 65, 18, 50, "4:3"),
    "research_laboratory_innovation_hub":     (25, 65, 18, 50, "4:3"),
    "residential_superblock":                 (50, 150, 35, 100, "4:3"),
    "science_engineering_lab_complex":        (30, 80, 25, 65, "5:4"),
    "second_empire_civic_building":           (28, 70, 22, 55, "9:7"),
    "student_residence_tower":                (18, 50, 16, 40, "6:5"),
    "student_union_campus_centre":            (35, 100, 25, 70, "4:3"),
    "ttc_streetcar_platform_stop":            (2, 4, 12, 35, "1:6.7"),       # narrow & long
    "university_academic_complex":            (28, 75, 18, 50, "3:2"),
    "university_library":                     (35, 90, 25, 65, "11:8"),
    "vertical_farm_indoor_agriculture":       (25, 65, 18, 50, "4:3"),
    "vertiport_evtol_facility":               (28, 75, 22, 60, "9:7"),
}


def find_archetypes_array_start(text: str) -> int:
    """Return offset where data.archetypes opens, so we don't accidentally
    splice into data.categories (which can contain a misplaced archetype-like
    entry with the same id — see glass_tower_modern)."""
    m = re.search(r'"archetypes"\s*:\s*\[', text)
    if not m:
        raise ValueError("Could not find archetypes array")
    return m.end()


def find_arch_block_text(text: str, slug: str, search_start: int) -> tuple[int, int]:
    """Return (block_start, block_end) byte offsets for the entire archetype block.
    Only searches text[search_start:] so we skip past data.categories."""
    needle = f'"id": "{slug}"'
    needle_idx = text.index(needle, search_start)
    start = text.rfind("\n    {", search_start, needle_idx)
    if start < 0:
        raise ValueError(f"No opening brace for {slug}")
    start += 1
    next_open = re.search(r"\n    \{", text[needle_idx:])
    if next_open:
        end = needle_idx + next_open.start() + 1
    else:
        m = re.search(r"\n  \]", text[needle_idx:])
        end = needle_idx + m.start() + 1
    return start, end


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        text = f.read()

    # Baseline parse
    data_before = json.loads(text)
    arch_count = len(data_before["archetypes"])
    archs_by_id = {a["id"]: a for a in data_before["archetypes"]}

    print(f"Catalog: {arch_count} archetypes")

    archetypes_start = find_archetypes_array_start(text)
    print(f"data.archetypes opens at byte {archetypes_start}")

    applied = 0
    skipped_present = 0
    not_found = 0
    skipped_already_has = 0

    # Apply edits highest-offset-first so earlier offsets stay valid
    edits = []  # (offset, new_lines_text)

    for slug, (mnW, mxW, mnD, mxD, ar) in DIMS.items():
        a = archs_by_id.get(slug)
        if a is None:
            print(f"  NOT FOUND: {slug}")
            not_found += 1
            continue
        if "minWidth_m" in a:
            print(f"  SKIP (already has minWidth_m): {slug}")
            skipped_already_has += 1
            continue

        # Find the suggestedDepth_m line in this archetype's block, then insert after.
        # Search only inside data.archetypes to skip the misplaced glass_tower_modern
        # entry that lives inside data.categories.
        block_start, block_end = find_arch_block_text(text, slug, archetypes_start)
        block = text[block_start:block_end]
        # Match the line containing suggestedDepth_m (with surrounding whitespace).
        # The catalog has heterogeneous indentation (4-space and 6-space variants
        # of the schema). Match the line as a whole.
        m = re.search(r'^([ \t]*)"suggestedDepth_m":\s*[\d\.]+\s*,?\s*\n', block, re.MULTILINE)
        if not m:
            print(f"  NO suggestedDepth_m line: {slug}")
            not_found += 1
            continue

        indent = m.group(1)
        # Build the lines to insert (indent matches existing line)
        lines_to_insert = (
            f'{indent}"minWidth_m": {mnW},\n'
            f'{indent}"maxWidth_m": {mxW},\n'
            f'{indent}"minDepth_m": {mnD},\n'
            f'{indent}"maxDepth_m": {mxD},\n'
            f'{indent}"aspectRatio": "{ar}",\n'
        )
        insert_offset = block_start + m.end()
        edits.append((insert_offset, lines_to_insert))
        applied += 1

    # Apply edits in reverse-offset order
    edits.sort(key=lambda e: -e[0])
    new_text = text
    for off, txt in edits:
        new_text = new_text[:off] + txt + new_text[off:]

    # Validate
    data_after = json.loads(new_text)
    archs_after_by_id = {a["id"]: a for a in data_after["archetypes"]}

    # Confirm all target archetypes now have minWidth_m
    missing = []
    for slug in DIMS:
        a = archs_after_by_id.get(slug)
        if a and ("minWidth_m" not in a or "maxWidth_m" not in a or "minDepth_m" not in a or "maxDepth_m" not in a):
            missing.append(slug)
    if missing:
        print(f"ERROR: {len(missing)} archetypes still missing fields after edit:")
        for s in missing[:10]:
            print(f"  - {s}")
        sys.exit(1)

    # Write
    with open(CATALOG, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)

    print()
    print(f"Applied {applied} dim sets, skipped {skipped_already_has} (already had), not found {not_found}")
    print(f"After: {len(data_after['archetypes'])} archetypes")
    # Confirm new presence stats
    total_with_minW = sum(1 for a in data_after["archetypes"] if "minWidth_m" in a)
    total_with_minD = sum(1 for a in data_after["archetypes"] if "minDepth_m" in a)
    print(f"  minWidth_m presence:  {total_with_minW}/{len(data_after['archetypes'])}")
    print(f"  minDepth_m presence:  {total_with_minD}/{len(data_after['archetypes'])}")


if __name__ == "__main__":
    main()
