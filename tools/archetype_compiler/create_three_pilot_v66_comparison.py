"""Create the reference / v65 / v66 board for the bounded fidelity rerun."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def fit(path: Path, width: int, height: int) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "#d9dde1")
    canvas.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = (
        (
            "Parisian Corner Turret",
            REPO / "frontend/public/archetypes/buildings/parisian_boulevard_corner/variant_0.png",
            REPO / "artifacts/pilot-v65/families/parisian-boulevard-corner/parisian-boulevard-corner_preview.png",
            REPO / "artifacts/pilot-v66/pilot-paris-v4/parisian-boulevard-corner/parisian-boulevard-corner_preview.png",
            "Camera lock · clean floor bands · curved balcony datums",
        ),
        (
            "Cream Terra-Cotta Art Deco Tower",
            REPO / "frontend/public/archetypes/buildings/art_deco_setback_tower/variant_0.png",
            REPO / "artifacts/pilot-v65/families/art-deco-setback-tower/art-deco-setback-tower_preview.png",
            REPO / "artifacts/pilot-v66/final/art-deco-setback-tower/art-deco-setback-tower_preview.png",
            "Framed ceremonial portal · articulated eight-face lantern",
        ),
        (
            "Traditional Restored Machiya",
            REPO / "frontend/public/archetypes/buildings/japanese_machiya_mixed_use/variant_0.png",
            REPO / "artifacts/pilot-v65/families/japanese-machiya-mixed-use/japanese-machiya-mixed-use_preview.png",
            REPO / "artifacts/pilot-v66/machiya-v2/japanese-machiya-mixed-use/japanese-machiya-mixed-use_preview.png",
            "Corrected dark-timber hierarchy · complete orbit QA",
        ),
    )

    page = Image.new("RGB", (1900, 1620), "#eef0f2")
    draw = ImageDraw.Draw(page)
    draw.text((55, 28), "Three-Pilot Fidelity Refinement v66", font=font(42, True), fill="#171b20")
    draw.text(
        (55, 82),
        "Archetype reference → previous pilot → refined pipeline run · review-only",
        font=font(23),
        fill="#555d66",
    )
    headers = (("Archetype reference", 55), ("v65 pilot", 665), ("v66 refinement", 1275))
    for label, x in headers:
        draw.text((x + 150, 126), label, font=font(25, True), fill="#2d333a")

    cell_w, cell_h = 570, 350
    for row_index, (label, reference, old, new, note) in enumerate(rows):
        y = 172 + row_index * 474
        draw.rounded_rectangle((40, y, 1860, y + 446), radius=18, fill="#ffffff", outline="#c9ced4", width=2)
        draw.text((62, y + 18), label, font=font(27, True), fill="#20252b")
        draw.text((62, y + 54), note, font=font(19), fill="#a25c2a")
        for column, path in enumerate((reference, old, new)):
            image = fit(path, cell_w, cell_h)
            page.paste(image, (55 + column * 610, y + 86))

    page.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
