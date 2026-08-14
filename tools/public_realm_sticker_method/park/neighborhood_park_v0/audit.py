"""Fail-closed evidence and runtime readiness audit for Neighborhood Park v0."""

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
COMPILED_KIT_PATH = HERE / "compiled-kit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_sha256(path: Path) -> str:
    """Hash source with LF normalization so the lock survives Git checkout policy."""
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def neighborhood_profile_block(source: str) -> str:
    start = source.index("  neighborhood_park: {")
    end = source.index("  urban_pocket_park: {", start)
    return source[start:end]


def audit(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    evidence = load_json(EVIDENCE_PATH)
    contract = load_json(CONTRACT_PATH)
    evidence_checks: list[dict[str, Any]] = []

    for reference in evidence["references"]:
        path = repo_root / reference["path"]
        dimensions = png_dimensions(path) if path.exists() else (None, None)
        actual_hash = sha256(path) if path.exists() else None
        passed = (
            path.exists()
            and actual_hash == reference["sha256"]
            and dimensions == (reference["width_px"], reference["height_px"])
        )
        evidence_checks.append(
            {
                "path": reference["path"],
                "passed": passed,
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
        actual_hash = source_sha256(path) if path.exists() else None
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

    profiles = source_text.get(
        "frontend/src/components/viewer/globe/parkGroundProfiles.ts", ""
    )
    recipes = source_text.get("frontend/src/data/parkKitRecipes.ts", "")
    families = source_text.get(
        "frontend/src/components/viewer/globe/parkLegoFamilies.ts", ""
    )
    profile = neighborhood_profile_block(profiles) if profiles else ""
    compiled_kit = load_json(COMPILED_KIT_PATH) if COMPILED_KIT_PATH.exists() else {}
    assembly = source_text.get(
        "frontend/src/components/viewer/globe/GlobeNeighborhoodParkV0StickerAssembly.tsx",
        "",
    )

    runtime_checks = [
        {
            "id": "canonical_profile_and_site_are_locked",
            "passed": (
                "id: 'neighborhood-park-v4'" in profile
                and "widthM: 100" in source_text.get("frontend/src/data/renderlockV1Parks.ts", "")
                and "depthM: 80" in source_text.get("frontend/src/data/renderlockV1Parks.ts", "")
            ),
        },
        {
            "id": "rustic_appearance_kit_exists",
            "passed": "rustic_timber_gravel_v1" in families,
        },
        {
            "id": "profile_owns_exact_rustic_identity",
            "passed": all(
                phrase in profiles.lower()
                for phrase in ("timber climbing tower with slide", "compacted-gravel", "split-rail", "wildflower")
            ),
        },
        {
            "id": "recipe_binds_observed_fixed_kit",
            "passed": all(
                phrase in recipes.lower()
                for phrase in ("timber_climbing_tower", "timber_swing_frame", "split_rail_fence")
            ),
        },
        {
            "id": "generic_contemporary_path_is_absent",
            "passed": (
                "neighborhood_park_v0_sticker_assembly" in profiles
                and "Never substitute a generic contemporary playground" in profiles
            ),
        },
        {
            "id": "compiled_exact_object_kit_is_complete",
            "passed": (
                compiled_kit.get("method") == "sticker_method_site_adaptive_whole_program"
                and compiled_kit.get("fixedProgramEnvelopeM") == [50.0, 38.0]
                and set(compiled_kit.get("assets", {})) == {
                    "timber_pavilion",
                    "timber_climbing_tower_with_slide",
                    "timber_swing_frame",
                    "split_rail_fence",
                    "natural_boulder_group",
                }
                and compiled_kit.get("surfaceOwnership", {}).get("exactOne") is True
                and compiled_kit.get("surfaceOwnership", {}).get("fallbackAllowed") is False
            ),
        },
        {
            "id": "runtime_mounts_whole_metric_sticker_assembly",
            "passed": all(
                phrase in assembly
                for phrase in (
                    "fitFixedParkProgram",
                    "fixedMetricObject: true",
                    "nonuniformScalingAllowed: false",
                    "sourcePixelsProjected: false",
                )
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
