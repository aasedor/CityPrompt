"""Validate and apply the executable quality memory to Wave 13."""
from __future__ import annotations

import json
from pathlib import Path

from quality_memory import assess_family_quality, load_quality_memory
from validate_outputs import validate_family


REPO = Path(__file__).resolve().parents[2]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
FAMILIES = (
    "art-deco-cream-terracotta-tower",
    "restored-kyoto-machiya",
    "mid-century-glass-steel-pavilion",
    "timber-glass-transit-station-block",
    "passive-house-timber-block",
)


def main() -> int:
    memory = load_quality_memory()
    failed = False
    for family in FAMILIES:
        root = FAMILIES_ROOT / family
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
            f"[wave13-assessor] {family}: validation={report['status']} "
            f"quality={assessment['status']} memory={assessment['memory_version']}"
        )
        failed = failed or report["status"] != "pass" or assessment["status"] != "pass"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
