"""
Phase 3.5 — Backfill archetype-level `suggestedFloorHeight` on all 218 archetypes
based on typology classification, AND flag variant-level overrides that
contradict their new parent default.

Uses TEXT-LEVEL splice (per CLAUDE.md). Inserts the field right after the
`suggestedDepth_m` line if absent. Skips archetypes that already have one.

Validates:
  - JSON parses before & after
  - All 218 archetypes have a parent suggestedFloorHeight after the run
  - No duplicate IDs
  - Reports list of variants whose existing fh is more than 50% off from the
    new parent default — these are candidates for manual review
"""

from __future__ import annotations

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Reuse the classifier
sys.path.insert(0, "scripts")
from classify_archetype_floor_heights import classify, TYPOLOGY_RULES  # noqa: E402

CATALOG = "frontend/src/data/buildingArchetypes.json"


def find_archetypes_array_start(text: str) -> int:
    m = re.search(r'"archetypes"\s*:\s*\[', text)
    if not m:
        raise ValueError("Could not find archetypes array")
    return m.end()


def find_arch_block(text: str, slug: str, search_start: int) -> tuple[int, int]:
    needle = f'"id": "{slug}"'
    needle_idx = text.index(needle, search_start)
    start = text.rfind("\n    {", search_start, needle_idx)
    if start < 0:
        raise ValueError(f"No opening brace for {slug}")
    start += 1
    nxt = re.search(r"\n    \{", text[needle_idx:])
    if nxt:
        end = needle_idx + nxt.start() + 1
    else:
        m = re.search(r"\n  \]", text[needle_idx:])
        end = needle_idx + m.start() + 1
    return start, end


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        text = f.read()

    data_before = json.loads(text)
    arches = data_before["archetypes"]
    print(f"Loaded {len(arches)} archetypes")

    # Classify each
    classifications = []
    for a in arches:
        label, h = classify(a)
        classifications.append((a["id"], label, h))

    # Compute outlier flags BEFORE applying parent backfill (since variant fh is
    # what's currently in the data; the parent default is what we're proposing).
    outliers = []  # (arch_id, variant_id, variant_label, variant_fh, parent_typology, parent_fh, ratio)
    for a in arches:
        label, parent_fh = classify(a)
        for v in a.get("variants", []) or []:
            vfh = v.get("suggestedFloorHeight")
            if vfh is None:
                continue
            ratio = vfh / parent_fh
            if ratio < 0.5 or ratio > 1.6:
                outliers.append((a["id"], v.get("id", "?"), v.get("label", "?"),
                                 vfh, label, parent_fh, ratio))

    # Apply backfill (TEXT-LEVEL): for each archetype that doesn't already have
    # `suggestedFloorHeight` at parent level, insert it after suggestedDepth_m.
    archetypes_start = find_archetypes_array_start(text)
    edits = []
    skipped_present = 0
    not_found = 0
    applied = 0

    for slug, label, h in classifications:
        a = next(x for x in arches if x["id"] == slug)
        if "suggestedFloorHeight" in a:
            skipped_present += 1
            continue

        try:
            block_start, block_end = find_arch_block(text, slug, archetypes_start)
        except Exception as e:
            print(f"  NOT FOUND in text: {slug}: {e}")
            not_found += 1
            continue

        block = text[block_start:block_end]
        # Insert right after the first parent-level line that contains
        # "suggestedDepth_m" (matching its indent).
        m = re.search(r'^([ \t]*)"suggestedDepth_m":\s*[\d\.]+\s*,?\s*\n',
                      block, re.MULTILINE)
        if not m:
            print(f"  NO suggestedDepth_m line: {slug}")
            not_found += 1
            continue
        indent = m.group(1)
        # Format: integer (8) -> "8.0", float (3.15) -> "3.15"
        h_str = f"{h:g}"
        if "." not in h_str:
            h_str += ".0"
        insert_text = f'{indent}"suggestedFloorHeight": {h_str},\n'
        offset = block_start + m.end()
        edits.append((offset, insert_text))
        applied += 1

    # Apply edits highest-offset-first so earlier offsets stay valid
    edits.sort(key=lambda e: -e[0])
    new_text = text
    for off, txt in edits:
        new_text = new_text[:off] + txt + new_text[off:]

    # Validate parse
    data_after = json.loads(new_text)
    archs_after = data_after["archetypes"]
    n_with_fh = sum(1 for a in archs_after if "suggestedFloorHeight" in a)

    print()
    print(f"Backfill: applied {applied}, skipped {skipped_present} (already had), not found {not_found}")
    print(f"Result: {n_with_fh}/{len(archs_after)} archetypes have suggestedFloorHeight at parent level")

    assert n_with_fh == len(archs_after), \
        f"Expected all {len(archs_after)} to have suggestedFloorHeight; got {n_with_fh}"

    ids = [a["id"] for a in archs_after]
    assert len(ids) == len(set(ids)), "Duplicate IDs after backfill"

    # Write
    with open(CATALOG, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)

    # Print outliers
    print()
    print("=" * 78)
    print(f"VARIANT FLOOR-HEIGHT OUTLIERS — {len(outliers)} variants where existing fh")
    print("differs from new parent typology default by >60%/<50% (review candidates):")
    print("=" * 78)
    by_arch = {}
    for o in outliers:
        by_arch.setdefault(o[0], []).append(o)
    for arch_id in sorted(by_arch):
        items = by_arch[arch_id]
        # show parent typology once
        _, _, _, _, label, parent_fh, _ = items[0]
        print(f"\n  {arch_id} (typology={label}, new parent fh={parent_fh}m)")
        for o in items:
            _, vid, vlbl, vfh, _, _, ratio = o
            arrow = "↓" if ratio < 1 else "↑"
            print(f"    {arrow} {vid:45} '{vlbl[:35]:35}' fh={vfh:5.1f}m (ratio {ratio:.2f}x)")


if __name__ == "__main__":
    main()
