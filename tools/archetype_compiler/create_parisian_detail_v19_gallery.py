#!/usr/bin/env python3
"""Create the v19 Parisian detail-correction review board."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)


def _fit(path: Path, size: tuple[int, int], crop: tuple[int, int, int, int] | None = None) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if crop:
            image = image.crop(crop)
        return ImageOps.fit(image, size, Image.Resampling.LANCZOS)


def _panel(canvas: Image.Image, draw: ImageDraw.ImageDraw, path: Path,
           rect: tuple[int, int, int, int], title: str, color: str,
           crop: tuple[int, int, int, int] | None = None) -> None:
    x0, y0, x1, y1 = rect
    canvas.paste(_fit(path, (x1 - x0, y1 - y0), crop), (x0, y0))
    draw.rectangle(rect, outline="#c6bdae", width=3)
    draw.rectangle((x0, y0, x1, y0 + 52), fill=color)
    draw.text((x0 + 15, y0 + 13), title, font=_font(20, True), fill="white")


def _detail_card(canvas: Image.Image, draw: ImageDraw.ImageDraw,
                 rect: tuple[int, int, int, int], title: str,
                 before: Path, after: Path,
                 after_crop: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = rect
    draw.rounded_rectangle(rect, radius=16, fill="#ffffff", outline="#c6bdae", width=2)
    draw.text((x0 + 18, y0 + 16), title, font=_font(22, True), fill="#39751d")
    image_w, image_h = x1 - x0 - 36, 228
    before_y = y0 + 58
    canvas.paste(_fit(before, (image_w, image_h)), (x0 + 18, before_y))
    draw.rectangle((x0 + 18, before_y, x1 - 18, before_y + 34), fill="#596775")
    draw.text((x0 + 30, before_y + 8), "BEFORE", font=_font(16, True), fill="white")
    after_y = before_y + image_h + 18
    canvas.paste(_fit(after, (image_w, image_h), after_crop), (x0 + 18, after_y))
    draw.rectangle((x0 + 18, after_y, x1 - 18, after_y + 34), fill="#39751d")
    draw.text((x0 + 30, after_y + 8), "v19 CORRECTION", font=_font(16, True), fill="white")


def create(output: Path, repo: Path) -> None:
    build = repo / "build/codex-lego-parisian-detail-correction-v19e"
    family = "parisian-v19e-detail-correction"
    manifest = json.loads((build / f"{family}_manifest.json").read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    size_mb = (build / assembled["filename"]).stat().st_size / (1024 * 1024)

    aerial = build / f"{family}_aerial.png"
    street = build / f"{family}_street.png"
    baseline = repo / "build/codex-lego-geographic-shapes-v18/compact-rectangle/parisian-v18-compact-rectangle_aerial.png"
    archetype = repo / "frontend/public/archetypes/buildings/parisian_midrise_block/variant_0_angle_60.jpg"
    before_roof = Path("C:/Users/andre/AppData/Local/Temp/codex-clipboard-cf46c744-2ff9-4324-9fc0-774d984fa0e2.png")
    before_ground = Path("C:/Users/andre/AppData/Local/Temp/codex-clipboard-040c7800-31f8-4630-a54e-4341658a5927.png")
    before_corner = Path("C:/Users/andre/AppData/Local/Temp/codex-clipboard-e093672e-00e7-4dad-adb3-094bb62195b7.png")

    canvas = Image.new("RGB", (2400, 1720), "#f5f2eb")
    draw = ImageDraw.Draw(canvas)
    ink = "#142334"
    draw.text((48, 30), "PARISIAN LEGO v19 - ARCHITECTURAL DETAIL CORRECTION", font=_font(42, True), fill=ink)
    draw.text((48, 88), "Four reported defects rebuilt as reusable construction, checked against the multi-angle archetype", font=_font(24), fill="#526170")

    _panel(canvas, draw, archetype, (48, 145, 790, 745), "ARCHETYPE - MATERIAL / CORNER / ROOF TARGET", ink)
    _panel(canvas, draw, baseline, (829, 145, 1571, 745), "v18 - REVIEWED BASELINE", "#596775")
    _panel(canvas, draw, aerial, (1610, 145, 2352, 745), "v19 - CORRECTED MODULAR GLB", "#39751d")

    cards = [
        ("1  ZINC-INTEGRATED DORMERS", before_roof, aerial, (210, 10, 1430, 590)),
        ("2  RECESSED SHOPFRONTS + DOORS", before_ground, street, (235, 610, 1450, 1000)),
        ("3  NO SUSPENDED BLACK SLAB", before_ground, street, (235, 610, 1450, 1000)),
        ("4  SOFTENED CHAMFERED CORNER", before_corner, street, (120, 20, 520, 990)),
    ]
    gap = 24
    card_w = (2304 - gap * 3) // 4
    for index, (title, before, after, crop) in enumerate(cards):
        x0 = 48 + index * (card_w + gap)
        _detail_card(canvas, draw, (x0, 790, x0 + card_w, 1390), title, before, after, crop)

    draw.rounded_rectangle((48, 1440, 2352, 1665), radius=18, fill="#e7ede2", outline="#abc09e", width=2)
    draw.text((72, 1466), "DELIVERABLE", font=_font(24, True), fill="#39751d")
    draw.text((72, 1510), f"Validated city GLB: {int(assembled['triangle_count']):,} triangles / {size_mb:.1f} MB", font=_font(23, True), fill=ink)
    draw.text((72, 1554), "Standing-seam zinc + occupied dormers  |  dark-oak entry + bronze shopfronts  |  PBR limestone corner pavilions", font=_font(22), fill=ink)
    draw.text((72, 1596), "All details remain parametric end conditions; only the middle bays repeat when the user's polygon changes size or shape.", font=_font(22), fill=ink)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, compress_level=7)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    create(args.output.resolve(), args.repo.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
