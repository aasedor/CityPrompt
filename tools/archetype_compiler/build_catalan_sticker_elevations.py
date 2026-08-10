"""Prepare rectified secondary-elevation stickers for the bounded Catalan pilot.

The generated long-side reference is already an orthographic design sheet.  This
script crops only its wall field: the front identity strip, roof and white studio
background remain geometry/reference responsibilities rather than texture pixels.
"""
from __future__ import annotations

from pathlib import Path

import cv2


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "artifacts/catalogue-rollout-v88/round-001/multiview-references/med_arcade_catalan_modernista/left-elevation-long-v1.png"
REAR_SOURCE = SOURCE.with_name("rear-elevation-v1.png")
OUTPUT = SOURCE.with_name("left-elevation-wall-sticker-v1.png")
REAR_OUTPUT = SOURCE.with_name("rear-elevation-wall-sticker-v1.png")


def main() -> None:
    image = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(SOURCE)
    # Pixel bounds were audited against the 1607x979 orthographic sheet.  They
    # isolate a 1.84:1 wall field, matching the fixed 31m x 17m side elevation.
    x0, y0, x1, y1 = 318, 300, 1500, 942
    if image.shape[:2] != (979, 1607):
        raise ValueError(f"unexpected side reference size {image.shape[1]}x{image.shape[0]}")
    crop = image[y0:y1, x0:x1]
    crop = cv2.resize(crop, (2048, 1123), interpolation=cv2.INTER_LANCZOS4)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT), crop, [cv2.IMWRITE_PNG_COMPRESSION, 4]):
        raise OSError(f"could not write {OUTPUT}")
    print(OUTPUT)

    rear = cv2.imread(str(REAR_SOURCE), cv2.IMREAD_COLOR)
    if rear is None:
        raise FileNotFoundError(REAR_SOURCE)
    if rear.shape[:2] != (1677, 938):
        raise ValueError(f"unexpected rear reference size {rear.shape[1]}x{rear.shape[0]}")
    # Keep the complete generated wall schedule but exclude the studio margin
    # and roof.  Rectification compresses its uncertain storey spacing to the
    # exact front-controlled 14m x 17m envelope.
    rear_crop = rear[382:1632, 70:868]
    rear_crop = cv2.resize(rear_crop, (1400, 1700), interpolation=cv2.INTER_LANCZOS4)
    if not cv2.imwrite(str(REAR_OUTPUT), rear_crop, [cv2.IMWRITE_PNG_COMPRESSION, 4]):
        raise OSError(f"could not write {REAR_OUTPUT}")
    print(REAR_OUTPUT)


if __name__ == "__main__":
    main()
