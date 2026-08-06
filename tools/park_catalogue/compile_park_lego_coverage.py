#!/usr/bin/env python3
"""Compile deterministic park LEGO coverage from the catalogue and backend registry."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOGUE_PATH = ROOT / "frontend" / "src" / "data" / "openSpaceArchetypes.json"
DEFAULT_OUTPUT = ROOT / "docs" / "park_lego_catalogue" / "coverage.json"


def build_coverage() -> dict[str, object]:
    sys.path.insert(0, str(ROOT / "backend"))
    from app.services.public_realm_lego import _CAPABILITIES  # noqa: PLC0415

    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    park_capabilities = [capability for capability in _CAPABILITIES if capability.kind == "park"]

    mapped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for capability in park_capabilities:
        for selection in capability.selections:
            mapped.setdefault((selection.archetype_id, selection.variant_id), []).append(
                {
                    "familyId": capability.family_id,
                    "profileId": selection.profile_id,
                    "appearanceKitId": selection.appearance_kit_id,
                    "componentSetIds": list(selection.component_set_ids),
                    "oneSelectionFamily": len(capability.selections) == 1,
                }
            )

    parents: list[dict[str, object]] = []
    category_summary: Counter[str] = Counter()
    totals = Counter()
    for archetype in catalogue["archetypes"]:
        variants: list[dict[str, object]] = []
        for variant in archetype.get("variants", []):
            mappings = mapped.get((archetype["id"], variant["id"]), [])
            exact = any(mapping["oneSelectionFamily"] for mapping in mappings)
            status = "exact_family" if exact else "mapped_shared_family" if mappings else "unmapped"
            totals[status] += 1
            variants.append(
                {
                    "id": variant["id"],
                    "label": variant.get("label"),
                    "thumbnailUrl": variant.get("thumbnailUrl"),
                    "status": status,
                    "mappings": mappings,
                }
            )

        mapped_count = sum(variant["status"] != "unmapped" for variant in variants)
        exact_count = sum(variant["status"] == "exact_family" for variant in variants)
        parent_status = (
            "complete_exact"
            if exact_count == len(variants)
            else "complete_mapped"
            if mapped_count == len(variants)
            else "partial"
            if mapped_count
            else "uncovered"
        )
        category_summary[f"{archetype.get('aestheticCategory', 'uncategorized')}:{parent_status}"] += 1
        parents.append(
            {
                "id": archetype["id"],
                "title": archetype.get("title"),
                "spaceType": archetype.get("spaceType"),
                "aestheticCategory": archetype.get("aestheticCategory"),
                "parentStatus": parent_status,
                "variantCount": len(variants),
                "mappedVariantCount": mapped_count,
                "exactVariantCount": exact_count,
                "variants": variants,
            }
        )

    return {
        "schemaVersion": 1,
        "definitionOfDone": {
            "parent": "Every variant has an explicit exact or reviewed shared-family mapping.",
            "variant": "The mapping has archetype-derived materials, parcel logic, a 3D kit decision, and a verified Generate-to-3D path.",
        },
        "summary": {
            "catalogueParents": len(parents),
            "catalogueVariants": sum(parent["variantCount"] for parent in parents),
            "completeExactParents": sum(parent["parentStatus"] == "complete_exact" for parent in parents),
            "completeMappedParents": sum(parent["parentStatus"] in {"complete_exact", "complete_mapped"} for parent in parents),
            "partialParents": sum(parent["parentStatus"] == "partial" for parent in parents),
            "uncoveredParents": sum(parent["parentStatus"] == "uncovered" for parent in parents),
            "exactVariants": totals["exact_family"],
            "sharedMappedVariants": totals["mapped_shared_family"],
            "unmappedVariants": totals["unmapped"],
            "parkCapabilities": len(park_capabilities),
        },
        "categorySummary": dict(sorted(category_summary.items())),
        "parents": parents,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the existing output differs.")
    args = parser.parse_args()
    payload = json.dumps(build_coverage(), indent=2, ensure_ascii=False) + "\n"
    output = args.out if args.out.is_absolute() else ROOT / args.out

    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != payload:
            raise SystemExit(f"coverage is stale: {output}")
        print(f"coverage current: {output}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    summary = json.loads(payload)["summary"]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
