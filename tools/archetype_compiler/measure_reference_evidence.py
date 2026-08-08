"""Measure a finite set of camera-locked renders against a multi-view contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from reference_fidelity import assess_evidence_contract, load_contract


def render_mapping(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"--render must be KEY=PATH, got {value!r}")
        key, raw_path = value.split("=", 1)
        result[key] = Path(raw_path).resolve()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--render", action="append", default=[], metavar="KEY=PATH")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path)
    args = parser.parse_args()

    report, overlays = assess_evidence_contract(
        load_contract(args.contract.resolve()), render_mapping(args.render),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.overlay_dir:
        args.overlay_dir.mkdir(parents=True, exist_ok=True)
        for view_id, overlay in overlays.items():
            cv2.imwrite(str(args.overlay_dir / f"{view_id}.png"), overlay)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
