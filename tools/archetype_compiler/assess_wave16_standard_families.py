"""Validate Wave 16 and route fresh models to human comparison review."""
from __future__ import annotations

import json
from pathlib import Path

from quality_memory import assess_family_quality, load_quality_memory
from validate_outputs import validate_family
from wave16_standard_specs import FAMILIES


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"


def main() -> int:
    memory = load_quality_memory()
    validation_failed = False
    for family in FAMILIES:
        root = ROOT / family
        report = validate_family(root, root / "grammar.json")
        (root / "validation_report.json").write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest = json.loads(
            (root / f"{family}_manifest.json").read_text(encoding="utf-8")
        )
        assessment = assess_family_quality(
            manifest,
            report,
            memory,
            family_dir=root,
        )
        (root / "quality_assessment.json").write_text(
            json.dumps(assessment, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"[wave16-assessor] {family}: validation={report['status']} "
            f"quality={assessment['status']} memory={assessment['memory_version']}"
        )
        validation_failed = validation_failed or report["status"] != "pass"
    # A quality status of review is the intended pre-approval state.
    return 1 if validation_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
