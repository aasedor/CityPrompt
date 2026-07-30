"""Create phone-readable Wave 8 catalogue/model comparison sheets."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
FAMILIES = {
    "parametric-fluid-hub": "Parametric Fluid Hub",
    "timber-transit-station": "Timber Transit Station",
    "covered-souk-market": "Covered Souk Market",
}
PANEL_WIDTH = 900
PANEL_HEIGHT = 560
LABEL_HEIGHT = 52


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
        centering=(0.5, 0.52),
    )
    result = Image.new(
        "RGB",
        (PANEL_WIDTH, PANEL_HEIGHT + LABEL_HEIGHT),
        "#14191e",
    )
    result.paste(fitted, (0, LABEL_HEIGHT))
    ImageDraw.Draw(result).text(
        (18, 11),
        label,
        fill="#f7f4ed",
        font=font(24),
    )
    return result


def family_sheet(slug: str, title: str) -> Image.Image:
    root = ROOT / slug
    items = [
        panel(
            root / "textures" / "source" / "archetype-goalpost.png",
            "CATALOGUE GOALPOST",
        ),
        panel(root / f"{slug}_street.png", "MODEL — PUBLIC FRONT"),
        panel(
            root / f"{slug}_front_corner_oblique.png",
            "MODEL — FRONT CORNER",
        ),
        panel(root / f"{slug}_aerial.png", "MODEL — AERIAL / ROOF PROOF"),
    ]
    gap = 22
    title_height = 76
    width = PANEL_WIDTH * 2 + gap * 3
    height = (PANEL_HEIGHT + LABEL_HEIGHT) * 2 + gap * 3 + title_height
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text(
        (gap, 18),
        f"{title} — reference-locked LEGO family",
        fill="#111820",
        font=font(34),
    )
    positions = [
        (gap, title_height + gap),
        (PANEL_WIDTH + gap * 2, title_height + gap),
        (gap, title_height + PANEL_HEIGHT + LABEL_HEIGHT + gap * 2),
        (
            PANEL_WIDTH + gap * 2,
            title_height + PANEL_HEIGHT + LABEL_HEIGHT + gap * 2,
        ),
    ]
    for image, position in zip(items, positions):
        sheet.paste(image, position)
    return sheet


def main() -> int:
    sheets: list[Image.Image] = []
    for slug, title in FAMILIES.items():
        sheet = family_sheet(slug, title)
        destination = ROOT / slug / f"{slug}_comparison.jpg"
        sheet.save(destination, quality=91, optimize=True, progressive=True)
        sheets.append(sheet)
        print(f"[wave8-comparison] {destination.relative_to(REPO)}")

    gap = 24
    width = max(sheet.width for sheet in sheets)
    height = sum(sheet.height for sheet in sheets) + gap * (len(sheets) - 1)
    combined = Image.new("RGB", (width, height), "#d8d8d5")
    y = 0
    for sheet in sheets:
        combined.paste(sheet, ((width - sheet.width) // 2, y))
        y += sheet.height + gap
    combined.save(
        ROOT / "wave8-reference-buildings-comparison.jpg",
        quality=89,
        optimize=True,
        progressive=True,
    )
    print(
        "[wave8-comparison] "
        "frontend/public/families/wave8-reference-buildings-comparison.jpg"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
