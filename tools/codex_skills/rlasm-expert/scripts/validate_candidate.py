#!/usr/bin/env python3
"""Deterministic RLASM candidate preflight; never substitutes for pixel review."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASELINE = {
    "front.png",
    "front_corner.png",
    "aerial.png",
    "left_side.png",
    "right_side.png",
    "rear.png",
    "rear_side.png",
    "facade_close.png",
    "architecture_close.png",
    "glass_close.png",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def resolve(candidate: Path, relative: str) -> Path:
    path = Path(relative)
    return path if path.is_absolute() else candidate / path


def resolve_candidate_or_batch(candidate: Path, relative: str) -> Path | None:
    """Resolve files stored either inside the candidate or its finite batch."""
    path = Path(relative)
    options = [path] if path.is_absolute() else [candidate / path, candidate.parent / path]
    return next((option for option in options if option.is_file()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--keeper", action="store_true")
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    failures: list[str] = []
    warnings: list[str] = []

    manifest_path = candidate / "prework-manifest.json"
    if not manifest_path.is_file():
        failures.append("missing prework-manifest.json")
        manifest: dict[str, Any] = {}
    else:
        manifest = read_json(manifest_path)

    sources = manifest.get("source_contract", {}).get("sources", [])
    source_roles = {str(item.get("role", "")).lower() for item in sources}
    role_groups = [
        {"front", "facade"},
        {"oblique", "angle_60", "front_corner"},
        {"top", "topology", "angle_90", "aerial"},
    ]
    if not sources or any(not (source_roles & group) for group in role_groups):
        failures.append(
            "source contract lacks compatible front/facade, oblique, or top/topology roles"
        )
    for item in sources:
        path = resolve(candidate, str(item.get("path", "")))
        if not path.is_file():
            failures.append(f"missing source: {path}")
            continue
        if item.get("bytes") != path.stat().st_size:
            failures.append(f"source byte mismatch: {path}")
        if item.get("sha256") != digest(path):
            failures.append(f"source SHA-256 mismatch: {path}")

    render_dir = candidate / "renders"
    render_names = (
        {path.name for path in render_dir.glob("*.png")}
        if render_dir.is_dir()
        else set()
    )
    missing_views = sorted(BASELINE - render_names)
    if missing_views:
        failures.append("missing baseline renders: " + ", ".join(missing_views))

    required_roles = manifest.get("mandatory_review_views", [])
    missing_declared = sorted(
        f"{role}.png"
        for role in required_roles
        if f"{role}.png" not in render_names
    )
    if missing_declared:
        failures.append("missing declared renders: " + ", ".join(missing_declared))

    evidence_path = candidate / "evidence" / "builder-evidence.json"
    if not evidence_path.is_file():
        failures.append("missing evidence/builder-evidence.json")
    else:
        evidence = read_json(evidence_path)
        fallback_count = evidence.get("generic_fallback_count")
        if fallback_count is None:
            fallback_count = evidence.get("material_compliance", {}).get(
                "generic_fallback_count"
            )
        if fallback_count != 0:
            failures.append(
                f"generic_fallback_count is {fallback_count!r}, expected 0"
            )

    if args.keeper:
        review_paths = [
            candidate / "review" / "independent-visual-review.json",
            candidate / "review" / "independent-review.json",
        ]
        review_path = next((path for path in review_paths if path.is_file()), None)
        if review_path is None:
            failures.append(
                "keeper check requires an independent visual review record"
            )
        else:
            review = read_json(review_path)
            status = str(review.get("status", "")).upper()
            blockers = review.get(
                "unresolved_blockers", review.get("p0_blockers", [])
            )
            scope_text = " ".join(
                str(item) for item in review.get("review_scope", [])
            ).lower()
            if "PASS" not in status or blockers:
                failures.append("independent review is not a zero-blocker pass")
            if "every mandatory" not in scope_text or "phone" not in scope_text:
                failures.append(
                    "independent review does not declare holistic mandatory-view and phone-board scope"
                )

        builder_review_path = candidate / "review" / "builder-visual-review.json"
        phone_boards: list[str] = []
        if builder_review_path.is_file():
            phone_boards = read_json(builder_review_path).get("phone_boards", [])
        if not phone_boards:
            failures.append("keeper check requires declared phone comparison boards")
        else:
            missing_boards = [
                relative
                for relative in phone_boards
                if resolve_candidate_or_batch(candidate, relative) is None
            ]
            if missing_boards:
                failures.append(
                    "missing phone comparison boards: " + ", ".join(missing_boards)
                )

    warnings.append(
        "Deterministic preflight cannot prove pixel fidelity, camera framing, contacts, optics, or holistic approval."
    )
    result = {
        "schema": "cityprompt.rlasm.preflight@1",
        "candidate": str(candidate),
        "keeper_check_requested": args.keeper,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
