"""Create phone-readable reference/model comparison sheets for Wave 14."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from wave14_variant_specs import FAMILIES


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
PANEL_WIDTH = 860
PANEL_HEIGHT = 540
LABEL_HEIGHT = 52
GAP = 22


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    return parser.parse_args()


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
        (PANEL_WIDTH, PANEL_HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    result = Image.new("RGB", (PANEL_WIDTH, PANEL_HEIGHT + LABEL_HEIGHT), "#14191e")
    result.paste(fitted, (0, LABEL_HEIGHT))
    ImageDraw.Draw(result).text((18, 11), label, fill="#f7f4ed", font=font(24))
    return result


def create_sheet(family: str) -> Path:
    spec = FAMILIES[family]
    root = ROOT / family
    source = root / "textures" / "source"
    rows = [
        (
            panel(source / "street-hero-source-v1.png", "REFERENCE - HERO MASSING / VARIANT IDENTITY"),
            panel(root / f"{family}_preview.png", "MODEL - COMPLETE FIXED LANDMARK"),
        ),
        (
            panel(source / "front-elevation-source-v1.png", "REFERENCE - PUBLIC ELEVATION GOALPOST"),
            panel(root / f"{family}_front_elevation.png", "MODEL - PHYSICAL FRONT ELEVATION"),
        ),
        (
            panel(source / "aerial-roof-source-v1.png", "REFERENCE - ROOF / PLAN / LOAD PATH"),
            panel(root / f"{family}_aerial.png", "MODEL - COMPLETE METRIC ROOF AND PLAN"),
        ),
        (
            panel(source / "rear-corner-source-v1.png", "REFERENCE - SECONDARY SIDE / REAR"),
            panel(root / f"{family}_rear_corner_oblique.png", "MODEL - COMPLETE SECONDARY ELEVATIONS"),
        ),
        (
            panel(source / "material-construction-source-v1.png", "REFERENCE - CUSTOM MATERIAL / CONSTRUCTION LOCK"),
            panel(root / f"{family}_facade_close.png", "MODEL - CUSTOM PBR SKIN / PHYSICAL DETAIL"),
        ),
    ]
    title_height = 86
    row_height = PANEL_HEIGHT + LABEL_HEIGHT
    width = PANEL_WIDTH * 2 + GAP * 3
    height = title_height + row_height * len(rows) + GAP * (len(rows) + 1)
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    title = f"{spec['label']} - reference-locked sibling-variant LEGO family"
    ImageDraw.Draw(sheet).text((GAP, 19), title, fill="#111820", font=font(34))
    y = title_height + GAP
    for reference, model in rows:
        sheet.paste(reference, (GAP, y))
        sheet.paste(model, (PANEL_WIDTH + GAP * 2, y))
        y += row_height + GAP
    destination = root / f"{family}_comparison.jpg"
    sheet.save(destination, quality=91, optimize=True, progressive=True)
    root_copy = ROOT / f"wave14-{family}-comparison.jpg"
    sheet.save(root_copy, quality=91, optimize=True, progressive=True)
    print(f"[wave14-comparison] {destination.relative_to(REPO)}")
    return destination


def create_overview(families: list[str]) -> Path:
    """Create one compact two-column visual index for mobile review."""
    card_width = 700
    card_height = 470
    card_label = 58
    columns = 2
    rows = (len(families) + columns - 1) // columns
    title_height = 88
    width = columns * card_width + (columns + 1) * GAP
    height = title_height + rows * (card_height + card_label) + (rows + 1) * GAP
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text(
        (GAP, 20),
        "Wave 14 - ten independently modeled catalogue sibling variants",
        fill="#111820",
        font=font(34),
    )
    for index, family in enumerate(families):
        column = index % columns
        row = index // columns
        x = GAP + column * (card_width + GAP)
        y = title_height + GAP + row * (card_height + card_label + GAP)
        preview = ImageOps.fit(
            Image.open(ROOT / family / f"{family}_preview.png").convert("RGB"),
            (card_width, card_height),
            method=Image.Resampling.LANCZOS,
        )
        sheet.paste(preview, (x, y + card_label))
        ImageDraw.Draw(sheet).rectangle(
            (x, y, x + card_width, y + card_label),
            fill="#14191e",
        )
        ImageDraw.Draw(sheet).text(
            (x + 15, y + 13),
            FAMILIES[family]["label"],
            fill="#f7f4ed",
            font=font(23),
        )
    destination = ROOT / "wave14-variant-overview.jpg"
    sheet.save(destination, quality=91, optimize=True, progressive=True)
    print(f"[wave14-comparison] {destination.relative_to(REPO)}")
    return destination


def main() -> int:
    args = parse_args()
    families = args.family or list(FAMILIES)
    for family in families:
        create_sheet(family)
    if not args.family:
        create_overview(families)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
