#!/usr/bin/env python3
"""Record an explicit human approval after locked-view family review.

Fresh generators deliberately leave the approval booleans false.  This command
verifies that the comparison sheet and every required locked view exist before
recording who approved the family.  It is a dry run unless ``--apply`` is used.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


REQUIRED_VIEWS = (
    "street",
    "context",
    "front_elevation",
    "front_corner_oblique",
    "rear_corner_oblique",
    "aerial",
    "facade_close",
)
EVIDENCE_FIELD = "quality_standard_evidence"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--reviewer", required=True, help="human reviewer name or handle"
    )
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--apply", action="store_true", help="write the approval to the manifest"
    )
    return parser.parse_args()


def standard_evidence(manifest: dict) -> dict:
    """Backfill deterministic evidence for manifests created before this gate."""
    family = str(manifest.get("family") or "").strip()
    graph = manifest.get("massing_graph") or {}
    existing = manifest.get(EVIDENCE_FIELD)
    evidence = dict(existing) if isinstance(existing, dict) else {}
    repeatable = [
        f"{module.get('role')}/{module.get('variant_key') or 'default'}"
        for module in manifest.get("modules") or []
        if module.get("assembly_class") == "repeatable_middle"
        or module.get("repeatable_z") is True
    ]
    defaults = {
        "standard_id": "haussmann-depth-shape-skin-scale@1",
        "distinctive_shape_features": list(graph.get("features") or []),
        "physical_depth_features": list(graph.get("physical_window_layers") or []),
        "photoreal_skin_approved": False,
        "fixed_identity_anchors": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
        ],
        "repeatable_middle_roles": repeatable,
        "comparison_views": list(REQUIRED_VIEWS),
        "comparison_sheet": f"{family}_comparison.jpg",
        "human_visual_approval": False,
    }
    for key, value in defaults.items():
        evidence.setdefault(key, value)
    return evidence


def review_errors(manifest_path: Path, manifest: dict) -> list[str]:
    family_dir = manifest_path.parent.resolve()
    family = str(manifest.get("family") or "").strip()
    evidence = manifest.get(EVIDENCE_FIELD)
    errors: list[str] = []
    if not family:
        errors.append("manifest family is missing")
    if not isinstance(evidence, dict):
        errors.append(f"manifest {EVIDENCE_FIELD} is missing")
        return errors

    declared_views = {str(value) for value in evidence.get("comparison_views") or []}
    for view in REQUIRED_VIEWS:
        if view not in declared_views:
            errors.append(f"comparison view is not declared: {view}")
        path = family_dir / f"{family}_{view}.png"
        if not path.is_file():
            errors.append(f"comparison view is missing: {path.name}")

    sheet_name = str(evidence.get("comparison_sheet") or "").strip()
    if not sheet_name:
        errors.append("comparison_sheet is not declared")
    else:
        sheet = (family_dir / sheet_name).resolve()
        try:
            sheet.relative_to(family_dir)
        except ValueError:
            errors.append("comparison_sheet must remain inside the family directory")
        else:
            if not sheet.is_file():
                errors.append(f"comparison sheet is missing: {sheet.name}")
            else:
                try:
                    with Image.open(sheet) as image:
                        image.verify()
                except OSError as exc:
                    errors.append(f"comparison sheet is unreadable: {exc}")
    return errors


def approve_manifest(
    manifest_path: Path,
    *,
    reviewer: str,
    notes: str = "",
    apply: bool = False,
) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[EVIDENCE_FIELD] = standard_evidence(manifest)
    errors = review_errors(manifest_path, manifest)
    if errors:
        raise ValueError("; ".join(errors))

    reviewer = reviewer.strip()
    if not reviewer:
        raise ValueError("reviewer must not be blank")
    evidence = dict(manifest[EVIDENCE_FIELD])
    evidence.update(
        {
            "photoreal_skin_approved": True,
            "human_visual_approval": True,
            "human_visual_reviewer": reviewer,
            "human_visual_reviewed_at": datetime.now(timezone.utc).isoformat(),
            "human_visual_review_notes": notes.strip(),
        }
    )
    manifest[EVIDENCE_FIELD] = evidence
    if apply:
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return manifest


def main() -> int:
    args = parse_args()
    try:
        manifest = approve_manifest(
            args.manifest,
            reviewer=args.reviewer,
            notes=args.notes,
            apply=args.apply,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"approval: BLOCKED ({exc})")
        return 1
    family = manifest["family"]
    action = "recorded" if args.apply else "ready (dry run; pass --apply to record)"
    print(f"approval: {action} for {family}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
