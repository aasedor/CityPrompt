"""Build alpha-isolated, image-registered architectural sticker masks.

The rectified colour elevation and the depth guide share an aspect ratio.  A
sticker assembly already declares its canonical UV bounds; this tool extracts
only the locally projecting construction inside those bounds and writes a
full-resolution binary mask.  Because the output remains in the canonical
elevation frame, Blender can use the same UVs for colour and alpha without any
resampling or per-card scale drift.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--elevation", type=Path, required=True)
    parser.add_argument("--depth-guide", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _registered_crop(item: dict, width: int, height: int) -> tuple[int, int, int, int]:
    x0 = round(float(item.get("uv_u_min", 0.0)) * width)
    x1 = round(float(item.get("uv_u_max", 1.0)) * width)
    y0 = round((1.0 - float(item.get("uv_v_max", 1.0))) * height)
    y1 = round((1.0 - float(item.get("uv_v_min", 0.0))) * height)
    return max(0, x0), min(width, x1), max(0, y0), min(height, y1)


def _feature_mask(depth_crop: np.ndarray, item_id: str) -> np.ndarray:
    # The guide is a deliberately neutral depth/relief render.  Selecting its
    # nearer luminance cluster removes mosaic and window-field pixels while
    # retaining the carved stone silhouette. Oriel stacks use a slightly lower
    # cut because their deep vertical returns are identity-bearing.
    percentile = 60 if "oriel" in item_id else 65
    if "piano_nobile" in item_id:
        percentile = 64
    threshold = max(150.0, float(np.percentile(depth_crop, percentile)))
    mask = np.where(depth_crop >= threshold, 255, 0).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    count, labels, stats, _centres = cv2.connectedComponentsWithStats(mask)
    minimum_area = max(24, round(mask.size * 0.00045))
    cleaned = np.zeros_like(mask)
    candidates = [
        index for index in range(1, count)
        if int(stats[index, cv2.CC_STAT_AREA]) >= minimum_area
    ]
    if "balcony" in item_id and candidates:
        # Each audited balcony rail/slab is one continuous carved-stone
        # silhouette. Bright window jambs and mosaic fragments elsewhere in
        # the crop are disconnected false positives and must not travel
        # forward with it.
        candidates = [max(candidates, key=lambda index: int(stats[index, cv2.CC_STAT_AREA]))]
    for index in candidates:
        cleaned[labels == index] = 255
    if "balcony" in item_id and np.any(cleaned):
        # A balcony begins where its rail/slab establishes a broad horizontal
        # footprint. Connected narrow spikes above that datum are bright window
        # jambs touching the rail in the guide, not part of the projection.
        row_coverage = np.count_nonzero(cleaned, axis=1) / max(1, cleaned.shape[1])
        # The threshold is intentionally strict: a true balustrade/slab spans
        # most of its audited crop, while even several aligned jamb fragments
        # occupy less than two thirds. This removes the last wall/window strips
        # that remained attached to otherwise-correct balcony silhouettes.
        broad_rows = np.flatnonzero(row_coverage >= 0.65)
        if broad_rows.size:
            cleaned[: int(broad_rows[0]), :] = 0
    return cleaned


def main() -> None:
    args = parse_args()
    payload = json.loads(args.profile.read_text(encoding="utf-8"))
    profile = payload["profiles"][args.variant]
    assemblies = profile["massing_graph"]["assemblies"]
    registration = profile["production_contract"]["image_lock"]["surface_registration"]
    group = str(registration["group"])

    elevation = cv2.imread(str(args.elevation), cv2.IMREAD_COLOR)
    depth = cv2.imread(str(args.depth_guide), cv2.IMREAD_GRAYSCALE)
    if elevation is None or depth is None:
        raise FileNotFoundError("elevation and depth guide must both be readable images")
    height, width = elevation.shape[:2]
    depth = cv2.resize(depth, (width, height), interpolation=cv2.INTER_CUBIC)
    args.output.mkdir(parents=True, exist_ok=True)

    union = np.zeros((height, width), np.uint8)
    records: list[dict] = []
    registered = [item for item in assemblies if item.get("registration_group") == group]
    for item in registered:
        item_id = str(item["id"])
        if item_id == "catalan_front_image_lock":
            continue
        x0, x1, y0, y1 = _registered_crop(item, width, height)
        local = _feature_mask(depth[y0:y1, x0:x1], item_id)
        full = np.zeros((height, width), np.uint8)
        full[y0:y1, x0:x1] = local
        path = args.output / f"{item_id}_alpha.png"
        cv2.imwrite(str(path), full)
        union = cv2.max(union, full)
        records.append({
            "assembly_id": item_id,
            "mask": path.name,
            "pixel_bounds": [x0, y0, x1, y1],
            "selected_fraction": round(float(np.count_nonzero(local)) / max(1, local.size), 5),
        })

    # The base retains every nonprojecting pixel. Removing the projected union
    # prevents the source feature from appearing twice under grazing cameras.
    base_mask = cv2.bitwise_not(union)
    base_path = args.output / "catalan_front_image_lock_alpha.png"
    cv2.imwrite(str(base_path), base_mask)
    union_path = args.output / "catalan_projected_feature_union.png"
    cv2.imwrite(str(union_path), union)
    manifest = {
        "schema": "registered-architectural-stickers@1",
        "variant": args.variant,
        "registration_group": group,
        "canonical_size": [width, height],
        "elevation": str(args.elevation),
        "depth_guide": str(args.depth_guide),
        "base_mask": base_path.name,
        "union_mask": union_path.name,
        "stickers": records,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(args.output / "manifest.json")


if __name__ == "__main__":
    main()
