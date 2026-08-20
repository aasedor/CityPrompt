#!/usr/bin/env python3
"""Prepare older family manifests for locked-view human review.

This command backfills deterministic quality-standard evidence and verifies the
declared comparison assets.  It never records human approval.  It is a dry run
unless ``--apply`` is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from approve_family_review import EVIDENCE_FIELD, review_errors, standard_evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, nargs="+")
    parser.add_argument(
        "--apply", action="store_true", help="write prepared evidence to each manifest"
    )
    return parser.parse_args()


def prepare_manifest(manifest_path: Path, *, apply: bool = False) -> dict:
    """Backfill deterministic evidence without granting visual approval."""
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[EVIDENCE_FIELD] = standard_evidence(manifest)
    errors = review_errors(manifest_path, manifest)
    if errors:
        raise ValueError("; ".join(errors))

    if apply:
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return manifest


def main() -> int:
    args = parse_args()
    action = "prepared" if args.apply else "ready (dry run; pass --apply to write)"
    for manifest_path in args.manifest:
        try:
            manifest = prepare_manifest(manifest_path, apply=args.apply)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"preparation: BLOCKED for {manifest_path} ({exc})")
            return 1
        print(f"preparation: {action} for {manifest['family']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
