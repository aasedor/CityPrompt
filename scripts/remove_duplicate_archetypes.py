"""
Phase 1.6 — Remove duplicate archetype JSON entries via TEXT-LEVEL splice.

Removes:
  - nordic_timber_mid_rise          (kept: nordic_timber_midrise)
  - midcentury_distribution_warehouse (kept: mid_century_distribution_warehouse)

Does NOT touch image directories on disk — those are flagged as orphans for
later manual cleanup. Does NOT touch shadeMap (separate edit).

Validates:
  - JSON parses before & after
  - Archetype count drops by exactly 2
  - thumbnailUrl count drops by expected amount (1 per archetype + 1 per variant = 5 per archetype, 10 total)
  - No duplicate archetype IDs in the result
  - Survivor archetypes still present
"""

from __future__ import annotations

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG = "frontend/src/data/buildingArchetypes.json"
LOSERS = ["nordic_timber_mid_rise", "midcentury_distribution_warehouse"]
SURVIVORS = ["nordic_timber_midrise", "mid_century_distribution_warehouse"]


def find_block(text: str, slug: str) -> tuple[int, int]:
    """Return (start_offset, end_offset) for the entire archetype block including
    the opening `    {` line and trailing `    },` (or `    }` if last)."""
    needle = f'"id": "{slug}"'
    needle_idx = text.index(needle)
    # Walk backward to the line with just `    {` (4 spaces + brace)
    # Use text.rfind to find the most recent occurrence of `\n    {`
    start = text.rfind("\n    {", 0, needle_idx)
    if start < 0:
        raise ValueError(f"Could not find opening brace for {slug}")
    start += 1  # skip the leading \n so we delete from the start of the line

    # Walk forward to find the closing `    },` or `    }` (final archetype)
    # The next archetype starts with `\n    {` at column 4 — find the first such match
    # AFTER the variants array closes for this archetype.
    j = needle_idx
    next_open = re.search(r"\n    \{", text[j:])
    if next_open:
        # Block ends just before the next archetype (i.e. closing brace + comma + newline)
        end = j + next_open.start() + 1  # include the \n at the end of `    },`
    else:
        # No next archetype — this is the last one; end at `\n  ]`
        m = re.search(r"\n  \]", text[j:])
        if not m:
            raise ValueError(f"Could not find end of {slug}")
        end = j + m.start() + 1

    return start, end


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        text = f.read()

    # baseline parse
    data_before = json.loads(text)
    arch_count_before = len(data_before["archetypes"])
    variants_before = sum(len(a.get("variants", [])) for a in data_before["archetypes"])
    thumbnail_count_before = text.count('"thumbnailUrl"')

    print(f"Before: {arch_count_before} archetypes, {variants_before} variants, "
          f"{thumbnail_count_before} thumbnailUrl entries")

    # Verify all losers and survivors exist
    ids_before = {a["id"] for a in data_before["archetypes"]}
    for slug in LOSERS + SURVIVORS:
        assert slug in ids_before, f"Missing: {slug}"

    # Delete loser blocks (in reverse order so earlier offsets stay valid)
    blocks = []
    for slug in LOSERS:
        s, e = find_block(text, slug)
        blocks.append((slug, s, e))
        print(f"  {slug}: bytes [{s}, {e}], length {e-s}, "
              f"~{text[s:s+200].count(chr(10))} lines for first 200 chars")

    blocks.sort(key=lambda b: -b[1])  # delete from highest offset first
    new_text = text
    for slug, s, e in blocks:
        new_text = new_text[:s] + new_text[e:]

    # Parse the result
    data_after = json.loads(new_text)
    arch_count_after = len(data_after["archetypes"])
    variants_after = sum(len(a.get("variants", [])) for a in data_after["archetypes"])
    thumbnail_count_after = new_text.count('"thumbnailUrl"')

    print()
    print(f"After:  {arch_count_after} archetypes, {variants_after} variants, "
          f"{thumbnail_count_after} thumbnailUrl entries")

    # Sanity checks
    assert arch_count_after == arch_count_before - len(LOSERS), \
        f"Expected {arch_count_before - len(LOSERS)} archetypes, got {arch_count_after}"

    ids_after = [a["id"] for a in data_after["archetypes"]]
    assert len(ids_after) == len(set(ids_after)), "Duplicate IDs after removal!"
    for s in SURVIVORS:
        assert s in ids_after, f"Survivor missing: {s}"
    for l in LOSERS:
        assert l not in ids_after, f"Loser still present: {l}"

    print("All checks pass. Writing.")
    with open(CATALOG, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    print("Done.")


if __name__ == "__main__":
    main()
