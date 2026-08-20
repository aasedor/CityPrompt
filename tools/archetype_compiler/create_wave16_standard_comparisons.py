"""Create phone-readable catalogue/model comparisons for Wave 16."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from wave16_standard_specs import FAMILIES


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
PANEL_W = 820
PANEL_H = 540
LABEL_H = 54
GAP = 22


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ):
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def panel(path: Path, label: str) -> Image.Image:
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    fitted = ImageOps.fit(
        image,
        (PANEL_W, PANEL_H),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    result = Image.new("RGB", (PANEL_W, PANEL_H + LABEL_H), "#12181d")
    result.paste(fitted, (0, LABEL_H))
    ImageDraw.Draw(result).text((18, 12), label, fill="#f7f4ed", font=font(23))
    return result


def create_sheet(family: str) -> Path:
    spec = FAMILIES[family]
    root = ROOT / family
    source = root / "textures" / "source"
    rows = [
        (
            panel(source / "archetype-goalpost.png", "CATALOGUE GOALPOST"),
            panel(root / f"{family}_preview.png", "COMPLETE FIXED MODEL"),
        ),
        (
            panel(source / "elevation-source-v1.png", "REGISTERED BUILDING / MATERIAL CROP"),
            panel(root / f"{family}_front_elevation.png", "PHYSICAL FRONT ELEVATION"),
        ),
        (
            panel(root / f"{family}_aerial.png", "ROOF / PLAN / GROUNDING"),
            panel(root / f"{family}_rear_corner_oblique.png", "COMPLETE SIDE AND REAR"),
        ),
        (
            panel(root / f"{family}_street.png", "PEDESTRIAN STREET VIEW"),
            panel(root / f"{family}_facade_close.png", "PBR SKIN / PHYSICAL DEPTH"),
        ),
    ]
    title_h = 86
    row_h = PANEL_H + LABEL_H
    width = PANEL_W * 2 + GAP * 3
    height = title_h + row_h * len(rows) + GAP * (len(rows) + 1)
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text(
        (GAP, 20),
        f"{spec['label']} - commonplace catalogue LEGO family",
        fill="#111820",
        font=font(32),
    )
    y = title_h + GAP
    for left, right in rows:
        sheet.paste(left, (GAP, y))
        sheet.paste(right, (PANEL_W + GAP * 2, y))
        y += row_h + GAP
    destination = root / f"{family}_comparison.jpg"
    sheet.save(destination, quality=90, optimize=True, progressive=True)
    sheet.save(ROOT / f"wave16-{family}-comparison.jpg", quality=90, optimize=True, progressive=True)
    print(f"[wave16-comparison] {destination.relative_to(REPO)}")
    return destination


def create_overview(families: list[str]) -> Path:
    card_w, card_h, label_h = 680, 455, 64
    columns = 2
    rows = (len(families) + columns - 1) // columns
    title_h = 96
    width = columns * card_w + (columns + 1) * GAP
    height = title_h + rows * (card_h + label_h) + (rows + 1) * GAP
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text(
        (GAP, 22),
        "Catalogue Wave 3 - ten classic everyday buildings",
        fill="#111820",
        font=font(34),
    )
    for index, family in enumerate(families):
        column, row = index % columns, index // columns
        x = GAP + column * (card_w + GAP)
        y = title_h + GAP + row * (card_h + label_h + GAP)
        preview = ImageOps.fit(
            Image.open(ROOT / family / f"{family}_preview.png").convert("RGB"),
            (card_w, card_h),
            method=Image.Resampling.LANCZOS,
        )
        sheet.paste(preview, (x, y + label_h))
        ImageDraw.Draw(sheet).rectangle((x, y, x + card_w, y + label_h), fill="#12181d")
        ImageDraw.Draw(sheet).text((x + 15, y + 15), FAMILIES[family]["label"], fill="#f7f4ed", font=font(22))
    destination = ROOT / "wave16-classic-everyday-overview.jpg"
    sheet.save(destination, quality=90, optimize=True, progressive=True)
    print(f"[wave16-comparison] {destination.relative_to(REPO)}")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    args = parser.parse_args()
    families = args.family or list(FAMILIES)
    for family in families:
        create_sheet(family)
    if not args.family:
        create_overview(families)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
