"""Codegen the backend's open-space dims table from the frontend catalogue.

Mirrors the buildings table (app/data/archetype_plan_dims.json). The backend
had no open-space metadata at all, so park archetype choice was a hardcoded
two-way threshold against a 130-entry catalogue — and the thresholds had
drifted from the catalogue's real area bands.

Run from the repo root:
    python backend/scripts/export_open_space_plan_dims.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "frontend" / "src" / "data" / "openSpaceArchetypes.json"
DEST = ROOT / "backend" / "app" / "data" / "open_space_plan_dims.json"


def _usable(entry: dict) -> bool:
    """Same predicate as the frontend resolver: something must be renderable."""
    if entry.get("thumbnailUrl"):
        return True
    return any(variant.get("thumbnailUrl") for variant in entry.get("variants") or [])


def _float(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = payload.get("archetypes") if isinstance(payload, dict) else payload

    rows = []
    for entry in entries or []:
        variants = [v.get("id") for v in entry.get("variants") or [] if v.get("id")]
        rows.append(
            {
                "id": entry["id"],
                "title": entry.get("title", ""),
                "space_type": entry.get("spaceType", ""),
                "aesthetic_category": entry.get("aestheticCategory", ""),
                "min_area_sqm": _float(entry.get("minAreaSqm")),
                "max_area_sqm": _float(entry.get("maxAreaSqm")),
                "suggested_area_sqm": _float(entry.get("suggestedAreaSqm")),
                "min_w_m": _float(entry.get("minWidth_m")),
                "max_w_m": _float(entry.get("maxWidth_m")),
                "min_d_m": _float(entry.get("minDepth_m")),
                "max_d_m": _float(entry.get("maxDepth_m")),
                "usable": _usable(entry),
                "has_variants": bool(variants),
                "variant_ids": variants,
            }
        )
    rows.sort(key=lambda row: row["id"])

    DEST.write_text(
        json.dumps(
            {"source": "openSpaceArchetypes.json", "count": len(rows), "archetypes": rows},
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    usable = sum(1 for row in rows if row["usable"])
    print(f"wrote {DEST.relative_to(ROOT)} — {len(rows)} entries, {usable} usable")


if __name__ == "__main__":
    main()
