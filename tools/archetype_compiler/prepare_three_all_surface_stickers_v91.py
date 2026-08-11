"""Prepare generated V91 stickers for edge-to-edge UV registration.

Image generators intentionally return isolated orthographic assets on a pale
capture background.  Mapping that background onto a rectangular wall creates
the white shoulder/gable failures found by the first Blender pilot.  This
bounded pass preserves the generated masters and writes render-ready copies
cropped to the longest fully occupied architectural wall field.  Roof plans
are cropped to their complete foreground footprint.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "artifacts/three-all-surface-stickers-v91/surface-stickers"
OUTPUT = REPO / "artifacts/three-all-surface-stickers-v91/render-ready-stickers"

# The Tuscan generator framed roof silhouettes as part of each elevation.
# These image-measured wall rectangles remove the duplicate photographic roof
# while retaining the complete plaster/stone field beneath the physical hip.
CROP_OVERRIDES = {
    ("med_villa_tuscan", "front"): (38, 122, 1498, 956),
    ("med_villa_tuscan", "left"): (96, 118, 974, 915),
    ("med_villa_tuscan", "right"): (78, 120, 944, 982),
    ("med_villa_tuscan", "rear"): (76, 138, 1464, 968),
}


def longest_run(indices: np.ndarray) -> tuple[int, int]:
    if indices.size == 0:
        raise ValueError("sticker has no fully occupied architectural rows")
    splits = np.where(np.diff(indices) > 1)[0] + 1
    runs = np.split(indices, splits)
    best = max(runs, key=len)
    return int(best[0]), int(best[-1]) + 1


def exterior_background(image: np.ndarray) -> np.ndarray:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.int16)
    corners = np.concatenate((
        rgb[:12, :12].reshape(-1, 3), rgb[:12, -12:].reshape(-1, 3),
        rgb[-12:, :12].reshape(-1, 3), rgb[-12:, -12:].reshape(-1, 3),
    ))
    reference = np.median(corners, axis=0)
    distance = np.linalg.norm(rgb - reference, axis=2)
    brightness = rgb.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    # Generators often add a subtle grey vignette to the nominally white
    # capture field, so colour distance alone leaves a false full-width band.
    # The neutral-bright clause admits that vignette while connected-component
    # filtering prevents isolated pale limestone or glass highlights inside the
    # building from being treated as exterior background.
    candidate = (
        ((distance < 68.0) & (brightness > 182.0) & (chroma < 52))
        | ((brightness > 212.0) & (chroma < 30))
    ).astype(np.uint8)
    count, labels = cv2.connectedComponents(candidate, connectivity=8)
    border_labels = set(np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))))
    border_labels.discard(0)
    if count <= 1 or not border_labels:
        return np.zeros(labels.shape, dtype=bool)
    return np.isin(labels, list(border_labels))


def prepare(path: Path, destination: Path) -> dict[str, object]:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"could not read {path}")
    height, width = image.shape[:2]
    background = exterior_background(image)
    foreground = ~background
    ys, xs = np.where(foreground)
    if not len(xs):
        raise ValueError(f"no architectural foreground in {path}")
    x0, x1 = max(0, int(xs.min()) - 2), min(width, int(xs.max()) + 3)
    y0, y1 = max(0, int(ys.min()) - 2), min(height, int(ys.max()) + 3)

    override = CROP_OVERRIDES.get((path.parent.name, path.stem))
    if override:
        x0, y0, x1, y1 = override
    elif path.stem != "roof":
        local = foreground[y0:y1, x0:x1]
        occupancy = local.mean(axis=1)
        # The longest nearly full-width run is the true rectangular wall field;
        # it rejects isolated roof silhouettes and their white gable shoulders.
        valid = np.where(occupancy >= 0.94)[0]
        if valid.size:
            row0, row1 = longest_run(valid)
            if row1 - row0 >= max(48, int(local.shape[0] * 0.28)):
                y0, y1 = y0 + row0, y0 + row1

    crop = image[y0:y1, x0:x1]
    if crop.size == 0:
        raise ValueError(f"empty crop for {path}")
    ready = cv2.resize(crop, (width, height), interpolation=cv2.INTER_LANCZOS4)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), ready, [cv2.IMWRITE_PNG_COMPRESSION, 6]):
        raise ValueError(f"could not write {destination}")
    ready_background = exterior_background(ready)
    return {
        "source": str(path.relative_to(REPO)).replace("\\", "/"),
        "output": str(destination.relative_to(REPO)).replace("\\", "/"),
        "source_px": [width, height],
        "crop_xyxy": [x0, y0, x1, y1],
        "render_ready_px": [width, height],
        "border_background_fraction": round(float(ready_background.mean()), 5),
    }


def main() -> int:
    records = []
    for path in sorted(SOURCE.glob("*/*.png")):
        destination = OUTPUT / path.parent.name / path.name
        record = prepare(path, destination)
        records.append(record)
        print(f"[v91-prepare] {path.parent.name}/{path.name}: crop={record['crop_xyxy']}")
    if not records:
        raise SystemExit("no V91 source stickers found")
    manifest = {
        "schema": "all-surface-sticker-preparation@1",
        "method": "connected pale-border removal plus longest occupied wall-field crop",
        "records": records,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "preparation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
