"""Normalize successful Meshy park GLBs and render four-view QA previews.

This performs no paid API calls. Rejected asset IDs can be excluded before any
runtime file is produced; raw Meshy outputs remain untouched for audit.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True)
    parser.add_argument(
        "--batch",
        default=str(Path(__file__).with_name("meshy_park_object_batch_v1.json")),
    )
    parser.add_argument("--blender")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--target-faces", type=int, default=12_000)
    parser.add_argument("--texture-max", type=int, default=512)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def blender_path(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).resolve()
        if path.is_file():
            return path
        raise FileNotFoundError(path)
    discovered = shutil.which("blender")
    if discovered:
        return Path(discovered)
    candidates = sorted(
        Path("C:/Program Files/Blender Foundation").glob("Blender */blender.exe"),
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError("Blender executable not found; pass --blender")
    return candidates[0]


def material_prefix(family: str) -> str:
    return {
        "nature-play-area": "meshy_nature_play",
        "rewilding-ecological-restoration-zone": "meshy_rewilding_deadwood",
        "pollinator-meadow-wildflower-garden": "meshy_pollinator_habitat",
        "urban-orchard-food-forest": "meshy_productive_garden",
        "memorial-garden": "meshy_memorial_garden",
        "mini-golf-putting-course": "meshy_mini_golf",
        "sculpture-garden-art-park": "meshy_sculpture_garden",
    }.get(family, "meshy_park_object")


def run(args: argparse.Namespace) -> None:
    root = Path(args.artifact_root).resolve()
    batch = json.loads(Path(args.batch).resolve().read_text(encoding="utf-8"))
    excluded = set(args.exclude)
    only = set(args.only)
    blender = blender_path(args.blender)
    normalizer = Path(__file__).with_name("normalize_and_render_meshy_park_asset.py")
    results: list[dict[str, Any]] = []

    for item in batch["objects"]:
        asset_id = item["assetId"]
        if asset_id in excluded or (only and asset_id not in only):
            continue
        asset_dir = root / asset_id
        raw = asset_dir / f"{asset_id}-raw.glb"
        cleaned = asset_dir / f"{asset_id}-clean.glb"
        previews = asset_dir / "previews"
        if not raw.is_file():
            results.append({"assetId": asset_id, "outcome": "missing-raw"})
            continue
        if cleaned.is_file() and not args.force:
            results.append({"assetId": asset_id, "outcome": "already-normalized"})
            continue
        dimensions = item["dimensionsM"]
        command = [
            str(blender),
            "--background",
            "--factory-startup",
            "--python",
            str(normalizer),
            "--",
            "--input",
            str(raw),
            "--output",
            str(cleaned),
            "--preview-dir",
            str(previews),
            "--asset-id",
            asset_id,
            "--size-x",
            str(dimensions[0]),
            "--size-y",
            str(dimensions[1]),
            "--size-z",
            str(dimensions[2]),
            "--orientation",
            item["orientation"],
            "--placement-role",
            item["placementRole"],
            "--material-prefix",
            material_prefix(item["family"]),
            "--target-faces",
            str(args.target_faces),
            "--texture-max",
            str(args.texture_max),
        ]
        completed = subprocess.run(command, check=False)
        results.append(
            {
                "assetId": asset_id,
                "outcome": "normalized" if completed.returncode == 0 else "failed",
                "returnCode": completed.returncode,
                "output": str(cleaned),
            }
        )

    report = {
        "batchId": batch["batchId"],
        "artifactRoot": str(root),
        "excluded": sorted(excluded),
        "targetFaces": args.target_faces,
        "textureMax": args.texture_max,
        "objects": results,
    }
    (root / "normalization-batch-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    if any(item["outcome"] == "failed" for item in results):
        sys.exit(1)


if __name__ == "__main__":
    run(parse_args())
