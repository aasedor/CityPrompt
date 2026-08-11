"""Prepare deterministic V94 sticker assets from the approved V91/V92 sheets."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


REPO = Path(__file__).resolve().parents[2]
SOURCE = (
    REPO
    / "docs/reviews/catalogue-rollout-v91/three-all-surface-sticker-pilot"
    / "belle-epoque-grand-magasin/sticker-roof.png"
)
OUTPUT = REPO / "tools/archetype_compiler/sticker_assets/belle_epoque_v94/roof_edge_extended.png"


def connected_border_white_mask(image: np.ndarray) -> np.ndarray:
    """Return only near-white pixels connected to an outer image edge."""

    near_white = np.all(image[:, :, :3] >= 238, axis=2).astype(np.uint8)
    count, labels = cv2.connectedComponents(near_white, connectivity=8)
    if count <= 1:
        return np.zeros(near_white.shape, dtype=np.uint8)
    border_labels = np.unique(
        np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))
    )
    border_labels = border_labels[border_labels != 0]
    return np.isin(labels, border_labels).astype(np.uint8) * 255


def main() -> None:
    image = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(SOURCE)
    mask = connected_border_white_mask(image)
    # Telea propagates the adjacent zinc/cornice pixels through only the exterior
    # white field. Architectural detail inside the roof sheet is untouched.
    cleaned = cv2.inpaint(image, mask, 5.0, cv2.INPAINT_TELEA)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT), cleaned):
        raise RuntimeError(f"Could not write {OUTPUT}")
    print(f"wrote {OUTPUT.relative_to(REPO)} ({int(np.count_nonzero(mask))} pixels extended)")


if __name__ == "__main__":
    main()
