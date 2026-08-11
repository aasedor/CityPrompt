"""Create de-lit intrinsic roof-feature stickers for the V95 carrier meshes."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "tools/archetype_compiler/sticker_assets/belle_epoque_v95"


def _stained_glass(seed: int, *, cooler: bool = False) -> np.ndarray:
    """Return a clean equirectangular dome material with no photographed roof."""

    height, width = 1024, 2048
    rng = np.random.default_rng(seed)
    y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None, None]
    top = np.array([154, 158, 140] if cooler else [169, 151, 112], dtype=np.float32)[None, None, :]
    base = np.array([65, 86, 76] if cooler else [91, 78, 51], dtype=np.float32)[None, None, :]
    image = top * (1.0 - y) + base * y
    image = np.repeat(image, width, axis=1)
    noise = rng.normal(0.0, 1.0, (height // 8, width // 8)).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    noise = cv2.GaussianBlur(noise, (0, 0), 10.0)
    image += noise[:, :, None] * 10.0

    # Restrained translucent Art Nouveau band close to the dome spring. The
    # physical Blender ribs own the heavy structure; these marks are glass
    # colour only and contain no directional highlight or cast shadow.
    band_y = int(height * 0.70)
    band_h = int(height * 0.17)
    overlay = np.zeros((height, width, 3), dtype=np.uint8)
    palette = (
        (72, 105, 96), (152, 113, 60), (120, 66, 54), (176, 146, 78), (74, 91, 102)
    )
    for index in range(40):
        cx = int((index + 0.5) * width / 40)
        cy = band_y + int(np.sin(index * 0.85) * band_h * 0.13)
        colour = palette[index % len(palette)]
        cv2.ellipse(overlay, (cx, cy), (42, 62), (index % 4) * 18, 0, 360, colour, -1, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), 13, (205, 177, 112), -1, cv2.LINE_AA)
    mask = np.any(overlay > 0, axis=2)
    image[mask] = image[mask] * 0.42 + overlay[mask].astype(np.float32) * 0.58
    cv2.line(image, (0, band_y - band_h // 2), (width, band_y - band_h // 2), (105, 102, 82), 4, cv2.LINE_AA)
    cv2.line(image, (0, band_y + band_h // 2), (width, band_y + band_h // 2), (105, 102, 82), 4, cv2.LINE_AA)
    # A de-lit leaded-cell field keeps the dome visibly polychrome from an
    # oblique aerial camera. Physical meridians still own the major structure;
    # these are only the smaller glass lights between them.
    cell_palette = (
        np.array((92, 117, 111), dtype=np.float32),
        np.array((168, 134, 72), dtype=np.float32),
        np.array((132, 81, 64), dtype=np.float32),
        np.array((99, 105, 124), dtype=np.float32),
    )
    for row in range(0, height, 48):
        offset = 24 if (row // 48) % 2 else 0
        for column in range(-offset, width, 52):
            if rng.random() < 0.38:
                colour = cell_palette[int(rng.integers(0, len(cell_palette)))]
                y0, y1 = row + 3, min(height - 1, row + 44)
                x0, x1 = max(0, column + 3), min(width - 1, column + 48)
                image[y0:y1, x0:x1] = image[y0:y1, x0:x1] * 0.52 + colour * 0.48
            cv2.line(image, (max(0, column), row), (min(width - 1, column + 52), row), (81, 82, 72), 2, cv2.LINE_AA)
        cv2.line(image, (0, row), (width - 1, row), (81, 82, 72), 2, cv2.LINE_AA)
    return cv2.cvtColor(np.clip(image, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


def _dormer_zinc(seed: int) -> np.ndarray:
    """A de-lit, construction-role-correct zinc sticker for every dormer face."""
    height = width = 1024
    rng = np.random.default_rng(seed)
    base = np.full((height, width, 3), (157, 166, 169), dtype=np.float32)
    noise = rng.normal(0.0, 1.0, (height // 12, width // 12)).astype(np.float32)
    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
    noise = cv2.GaussianBlur(noise, (0, 0), 6.0)
    base += noise[:, :, None] * 7.0
    # Standing seams and restrained weather streaks are intrinsic material
    # variation, not a photographed directional-light gradient.
    for x in range(40, width, 128):
        cv2.line(base, (x, 0), (x, height), (107, 119, 124), 5, cv2.LINE_AA)
        cv2.line(base, (x + 7, 0), (x + 7, height), (193, 198, 199), 2, cv2.LINE_AA)
    for x in range(83, width, 211):
        cv2.line(base, (x, 0), (x + 16, height), (136, 143, 142), 2, cv2.LINE_AA)
    return cv2.cvtColor(np.clip(base, 55, 220).astype(np.uint8), cv2.COLOR_RGB2BGR)


def _entrance_sign() -> np.ndarray:
    # OpenCV writes BGR. These values intentionally produce the reference's
    # warm brown plaque with aged gold lettering, not a teal diagnostic bar.
    image = np.full((256, 2048, 3), (27, 39, 54), dtype=np.uint8)
    cv2.rectangle(image, (12, 12), (2035, 243), (59, 115, 151), 9, cv2.LINE_AA)
    label = "GALERIES LAFAYETTE"
    font = cv2.FONT_HERSHEY_TRIPLEX
    scale, thickness = 3.55, 7
    size = cv2.getTextSize(label, font, scale, thickness)[0]
    origin = ((image.shape[1] - size[0]) // 2, (image.shape[0] + size[1]) // 2 - 4)
    cv2.putText(image, label, origin, font, scale, (126, 190, 218), thickness, cv2.LINE_AA)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUT / "central_dome_intrinsic.png": _stained_glass(9501),
        OUT / "corner_dome_intrinsic.png": _stained_glass(9502, cooler=True),
        OUT / "dormer_zinc_intrinsic.png": _dormer_zinc(9503),
        OUT / "entrance_sign_intrinsic.png": _entrance_sign(),
    }
    for path, image in outputs.items():
        if not cv2.imwrite(str(path), image, [cv2.IMWRITE_PNG_COMPRESSION, 7]):
            raise RuntimeError(f"could not write {path}")
        print(f"wrote {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
