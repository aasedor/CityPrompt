"""Export the backend trust index from authoritative frontend catalogues.

Run from any directory:
    python backend/scripts/export_public_realm_catalog_ids.py
    python backend/scripts/export_public_realm_catalog_ids.py --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "park": REPO_ROOT / "frontend" / "src" / "data" / "openSpaceArchetypes.json",
    "street": REPO_ROOT / "frontend" / "src" / "data" / "streetPathArchetypes.json",
}
TARGETS = {
    "park": REPO_ROOT / "backend" / "app" / "data" / "public_realm_park_variants.json",
    "street": REPO_ROOT / "backend" / "app" / "data" / "public_realm_street_variants.json",
}


def _payload(source: Path) -> dict[str, list[str]]:
    document = json.loads(source.read_text(encoding="utf-8"))
    archetypes = document.get("archetypes")
    if not isinstance(archetypes, list):
        raise RuntimeError(f"{source} has no archetypes array")
    payload: dict[str, list[str]] = {}
    for entry in archetypes:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise RuntimeError(f"{source} has an invalid archetype entry")
        archetype_id = entry["id"]
        variants = entry.get("variants") or []
        if not isinstance(variants, list) or not all(
            isinstance(variant, dict) and isinstance(variant.get("id"), str) for variant in variants
        ):
            raise RuntimeError(f"{source} has invalid variants for {archetype_id}")
        payload[archetype_id] = sorted(variant["id"] for variant in variants)
    return dict(sorted(payload.items()))


def export(*, check: bool) -> list[str]:
    drift: list[str] = []
    for kind in ("park", "street"):
        expected = _payload(SOURCES[kind])
        target = TARGETS[kind]
        if check:
            actual: Any = json.loads(target.read_text(encoding="utf-8")) if target.exists() else None
            if actual != expected:
                drift.append(kind)
            continue
        target.write_text(
            json.dumps(expected, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return drift


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated indexes differ")
    args = parser.parse_args()
    drift = export(check=args.check)
    if drift:
        print("Public-realm catalogue index drift: " + ", ".join(drift))
        return 1
    print("Public-realm catalogue indexes are current." if args.check else "Exported public-realm catalogue indexes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
