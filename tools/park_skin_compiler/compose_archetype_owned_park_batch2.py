"""Compose a mobile-review sheet for archetype-owned park LEGO batch 2."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PARKS = (
    ("Tennis Court Cluster / Professional Grade", "tennis-court-cluster", "tennis-court-professional"),
    ("Nature Play Area / Forest Adventure", "nature-play-area", "nature-play-forest-adventure"),
    ("Pump Track / Asphalt Competition", "pump-track", "pump-track-asphalt-competition"),
    ("Outdoor Fitness / Urban Calisthenics", "outdoor-fitness-circuit", "outdoor-fitness-calisthenics"),
    ("Memorial Garden / Classical Formal", "memorial-garden", "memorial-garden-classical-formal"),
)
VIEWS = ("generated_base.png", "generated_angle_60.png", "generated_angle_90.png")


def font(size: int, bold: bool = False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    fitted = ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (size[0] + 4, size[1] + 4), "#c5cbc7")
    framed.paste(fitted, (2, 2))
    return framed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    width, margin, gap = 1600, 34, 14
    cell_w, cell_h = 372, 280
    title_h, row_label_h, row_gap = 118, 48, 30
    height = title_h + len(PARKS) * (row_label_h + cell_h + row_gap) + 24
    sheet = Image.new("RGB", (width, height), "#f3f2ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 22), "ARCHETYPE-OWNED PARK LEGO — BATCH 2", font=font(34, True), fill="#1e2c27")
    draw.text((margin, 67), "Exact catalogue render → authored oblique → 60° → near-nadir", font=font(20), fill="#52615b")

    y = title_h
    labels = ("ARCHETYPE", "AUTHORED OBLIQUE", "AUTHORED 60°", "AUTHORED NADIR")
    for title, source_slug, render_slug in PARKS:
        draw.text((margin, y), title, font=font(24, True), fill="#24342d")
        y += row_label_h
        source = args.repo_root / "frontend/public/archetypes/openspaces" / source_slug / "variant_0.png"
        images = [Image.open(source)] + [Image.open(args.render_root / render_slug / view) for view in VIEWS]
        for index, image in enumerate(images):
            x = margin + index * (cell_w + gap)
            sheet.paste(panel(image, (cell_w, cell_h)), (x, y))
            draw.rounded_rectangle((x + 10, y + 10, x + 10 + len(labels[index]) * 10 + 24, y + 42), radius=8, fill="#17231f")
            draw.text((x + 20, y + 15), labels[index], font=font(14, True), fill="white")
        y += cell_h + row_gap

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, optimize=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
