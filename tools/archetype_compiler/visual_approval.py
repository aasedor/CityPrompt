"""Validate or explicitly record human visual approval for one building family.

Approval is intentionally separate from geometry validation.  This command is
only run after a reviewer compares the generated board with the authoritative
archetype views at block, building, facade, and live-context scales.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "building-visual-approval@1"
REQUIRED_CHECKS = {
    "block_scale",
    "building_scale",
    "facade_scale",
    "orbit_and_context",
}


def validate_visual_approval(approval: dict[str, Any] | None) -> tuple[bool, str]:
    if not approval:
        return False, "visual_approval.json is missing"
    if approval.get("schema") != SCHEMA:
        return False, f"visual approval schema is {approval.get('schema')!r}"
    if approval.get("decision") != "approved":
        return False, f"visual decision is {approval.get('decision')!r}"
    if not approval.get("reviewer") or not approval.get("approved_at"):
        return False, "reviewer and approved_at are required"
    if not approval.get("reference_set"):
        return False, "reference_set is required"
    checks = approval.get("checks") or {}
    missing = sorted(check for check in REQUIRED_CHECKS if checks.get(check) is not True)
    if missing:
        return False, "unapproved checks: " + ", ".join(missing)
    return True, "all multiscale visual checks explicitly approved"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--family", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reference-set", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="confirm that all four required visual scales were reviewed and approved",
    )
    args = parser.parse_args()
    if not args.approve:
        parser.error("--approve is required; approval cannot be inferred from generated files")

    payload = {
        "schema": SCHEMA,
        "family": args.family,
        "decision": "approved",
        "reviewer": args.reviewer,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "reference_set": args.reference_set,
        "checks": {check: True for check in sorted(REQUIRED_CHECKS)},
        "notes": args.notes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
