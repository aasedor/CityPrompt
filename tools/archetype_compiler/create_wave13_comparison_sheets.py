"""Create phone-readable reference/model comparison sheets for Wave 13."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
PANEL_WIDTH = 860
PANEL_HEIGHT = 540
LABEL_HEIGHT = 52
GAP = 22

FAMILIES = {
    "art-deco-cream-terracotta-tower": {
        "title": "Cream Terracotta Art Deco Tower - reference-locked LEGO family",
        "detail_source": "terracotta-material-source-v1.png",
        "detail_render": "identity_close",
        "detail_label": "MODEL - PIERS / SPANDRELS / SETBACK CROWN / LANTERN",
    },
    "restored-kyoto-machiya": {
        "title": "Restored Kyoto Machiya - reference-locked LEGO family",
        "detail_source": "lattice-material-source-v1.png",
        "detail_render": "facade_close",
        "detail_label": "MODEL - KOSHI LATTICE / NORREN / EAVES / KAWARA TILES",
    },
    "mid-century-glass-steel-pavilion": {
        "title": "Mid-Century Glass and Steel Pavilion - reference-locked LEGO family",
        "detail_source": "vision-glass-material-source-v1.png",
        "detail_render": "facade_close",
        "detail_label": "MODEL - LOW-IRON GLASS / STEEL GRID / OCCUPIED DEPTH",
    },
    "timber-glass-transit-station-block": {
        "title": "Timber and Glass Transit Station - reference-locked LEGO family",
        "detail_source": "louver-material-source-v1.png",
        "detail_render": "identity_close",
        "detail_label": "MODEL - CONCOURSE / TIMBER LOUVERS / CANOPY / PV ROOF",
    },
    "passive-house-timber-block": {
        "title": "Passive-House Timber Block - reference-locked LEGO family",
        "detail_source": "blind-material-source-v1.png",
        "detail_render": "facade_close",
        "detail_label": "MODEL - DEEP REVEALS / TRIPLE GLASS / REAL BLINDS / LARCH",
    },
}


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
            panel(source / "street-hero-source-v1.png", "REFERENCE - HERO MASSING / IDENTITY"),
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
            panel(source / spec["detail_source"], "REFERENCE - MATERIAL / DETAIL LOCK"),
            panel(root / f"{family}_{spec['detail_render']}.png", spec["detail_label"]),
        ),
    ]
    title_height = 86
    row_height = PANEL_HEIGHT + LABEL_HEIGHT
    width = PANEL_WIDTH * 2 + GAP * 3
    height = title_height + row_height * len(rows) + GAP * (len(rows) + 1)
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text((GAP, 19), spec["title"], fill="#111820", font=font(36))
    y = title_height + GAP
    for reference, model in rows:
        sheet.paste(reference, (GAP, y))
        sheet.paste(model, (PANEL_WIDTH + GAP * 2, y))
        y += row_height + GAP
    destination = root / f"{family}_comparison.jpg"
    sheet.save(destination, quality=91, optimize=True, progressive=True)
    root_copy = ROOT / f"wave13-{family}-comparison.jpg"
    sheet.save(root_copy, quality=91, optimize=True, progressive=True)
    print(f"[wave13-comparison] {destination.relative_to(REPO)}")
    return destination


def main() -> int:
    args = parse_args()
    for family in args.family or list(FAMILIES):
        create_sheet(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
