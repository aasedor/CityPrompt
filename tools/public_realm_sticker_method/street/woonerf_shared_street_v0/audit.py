"""Fail-closed evidence and runtime readiness audit for Woonerf v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_PATH = HERE / "evidence-lock.json"
CONTRACT_PATH = HERE / "contract.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] != b"\xff\xd8":
        raise ValueError(f"unsupported image: {path}")
    index = 2
    while index < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        length = int.from_bytes(data[index:index + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += length
    raise ValueError(f"JPEG dimensions not found: {path}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def between(source: str, start_text: str, end_text: str) -> str:
    start = source.index(start_text)
    end = source.index(end_text, start)
    return source[start:end]


def audit(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    evidence = load_json(EVIDENCE_PATH)
    contract = load_json(CONTRACT_PATH)
    evidence_checks: list[dict[str, Any]] = []

    for reference in evidence["references"]:
        path = repo_root / reference["path"]
        dimensions = image_dimensions(path) if path.exists() else (None, None)
        actual_hash = sha256(path) if path.exists() else None
        evidence_checks.append(
            {
                "path": reference["path"],
                "passed": (
                    path.exists()
                    and actual_hash == reference["sha256"]
                    and dimensions == (reference["width_px"], reference["height_px"])
                ),
                "expected_sha256": reference["sha256"],
                "actual_sha256": actual_hash,
                "expected_dimensions": [reference["width_px"], reference["height_px"]],
                "actual_dimensions": list(dimensions),
            }
        )

    source_checks: list[dict[str, Any]] = []
    source_text: dict[str, str] = {}
    for source in contract["runtime_sources"]:
        path = repo_root / source["path"]
        actual_hash = sha256(path) if path.exists() else None
        source_checks.append(
            {
                "path": source["path"],
                "passed": path.exists() and actual_hash == source["sha256"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual_hash,
            }
        )
        if path.exists():
            source_text[source["path"]] = path.read_text(encoding="utf-8")

    visual_source = source_text.get(
        "frontend/src/components/viewer/globe/streetVisualContracts.ts", ""
    )
    section_source = source_text.get(
        "frontend/src/components/viewer/globe/streetSectionProfiles.ts", ""
    )
    furniture_source = source_text.get(
        "frontend/src/components/viewer/globe/streetFamilyFurniture.ts", ""
    )
    detail_source = source_text.get(
        "frontend/src/components/viewer/globe/GlobeStreetDetailLayer.tsx", ""
    )
    visual_block = between(
        visual_source,
        "contractId: 'woonerf_shared_street/woonerf_shared_street_v0'",
        "contractId: 'yield_street/yield_street_v0'",
    ) if visual_source else ""
    section_block = between(
        section_source,
        "  woonerf_shared_street: {",
        "  yield_street: {",
    ) if section_source else ""
    combined_runtime = "\n".join((visual_block, section_block, furniture_source, detail_source)).lower()

    runtime_checks = [
        {
            "id": "ten_metre_flush_curb_free_section_is_locked",
            "passed": (
                "rowm: 10" in section_block.lower()
                and "rendercurbs: false" in section_block.lower()
                and "standard_lane_markings" in visual_block
            ),
        },
        {
            "id": "three_exact_reference_views_are_bound",
            "passed": "referenceViews: threeViews('woonerf-shared-street')" in visual_block,
        },
        {
            "id": "exact_authority_overrides_dutch_vehicle_chicane",
            "passed": all(
                forbidden not in visual_block.lower()
                for forbidden in ("chicane_delineation", "raised_tables", "play_elements", "informal_pockets")
            ),
        },
        {
            "id": "complete_pergola_module_is_bound",
            "passed": all(
                token in combined_runtime
                for token in ("timber_pergola", "flowering_vine", "pergola_citrus_social_bay")
            ),
        },
        {
            "id": "full_width_pedestrian_paving_is_bound",
            "passed": (
                "shared_lane', width_m: 10" in section_block.lower()
                and "alternating planter edge" not in section_block.lower()
            ),
        },
        {
            "id": "botanical_furnishing_kit_is_bound",
            "passed": all(
                token in combined_runtime
                for token in ("terracotta_citrus", "wrought_iron_bench", "mosaic_square_inlay")
            ),
        },
    ]

    evidence_integrity = all(item["passed"] for item in evidence_checks)
    source_integrity = all(item["passed"] for item in source_checks)
    runtime_ready = all(item["passed"] for item in runtime_checks)
    status = "ready" if evidence_integrity and source_integrity and runtime_ready else "hold"
    if not evidence_integrity or not source_integrity:
        status = "invalid"

    return {
        "schema_version": "sticker_method_public_realm_audit_v1",
        "initiative": contract["initiative"],
        "status": status,
        "evidence_integrity": evidence_integrity,
        "source_integrity": source_integrity,
        "runtime_ready": runtime_ready,
        "evidence_checks": evidence_checks,
        "source_checks": source_checks,
        "runtime_checks": runtime_checks,
        "known_runtime_gaps": contract["known_runtime_gaps"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    result = audit(args.repo.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "invalid":
        return 2
    if args.require_ready and result["status"] != "ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
