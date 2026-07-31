"""Create a phone-readable reference/model comparison for the Wave 10 school."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
FAMILY = "ecole-republicaine-third-republic"
PANEL_WIDTH = 860
PANEL_HEIGHT = 540
LABEL_HEIGHT = 52
GAP = 22


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ):
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def panel(path: Path, label: str, *, centering=(0.5, 0.5)) -> Image.Image:
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    fitted = ImageOps.fit(
        image,
        (PANEL_WIDTH, PANEL_HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=centering,
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


def main() -> int:
    root = ROOT / FAMILY
    source = root / "textures" / "source"
    rows = [
        (
            panel(source / "archetype-goalpost.png", "ORIGINAL IDENTITY GOALPOST"),
            panel(
                root / f"{FAMILY}_front_corner_oblique.png",
                "MODEL - MATCHED CIVIC STREET CORNER",
            ),
        ),
        (
            panel(source / "elevation-source-v1.png", "RECTIFIED PUBLIC ELEVATION"),
            panel(root / f"{FAMILY}_street.png", "MODEL - RECTIFIED PUBLIC FRONT"),
        ),
        (
            panel(source / "aerial-source-v1.png", "SLATE ROOF / MASSING GOALPOST"),
            panel(root / f"{FAMILY}_aerial.png", "MODEL - ROOF TOPOLOGY PROOF"),
        ),
        (
            panel(source / "rear-elevation-source-v1.png", "SCHOOLYARD REAR GOALPOST"),
            panel(
                root / f"{FAMILY}_rear_corner_oblique.png",
                "MODEL - REAR STAIR / SERVICE PROOF",
            ),
        ),
        (
            panel(
                source / "occupied-depth-source-v1.png",
                "WINDOW / ENTRY CONSTRUCTION GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_identity_close.png",
                "MODEL - PHYSICAL ARCHES / HERITAGE LOW-E",
                centering=(0.50, 0.56),
            ),
        ),
        (
            panel(
                source / "clock-cornice-detail-source-v1.png",
                "CLOCK / CORNICE / CHIMNEY GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_roof_close.png",
                "MODEL - INTEGRATED CLOCK / SLATE DETAIL",
                centering=(0.50, 0.50),
            ),
        ),
    ]
    title_height = 86
    width = PANEL_WIDTH * 2 + GAP * 3
    row_height = PANEL_HEIGHT + LABEL_HEIGHT
    height = title_height + row_height * len(rows) + GAP * (len(rows) + 1)
    sheet = Image.new("RGB", (width, height), "#e6e5e1")
    ImageDraw.Draw(sheet).text(
        (GAP, 19),
        "Third Republic School - reference-locked LEGO family",
        fill="#111820",
        font=font(36),
    )
    y = title_height + GAP
    for reference, model in rows:
        sheet.paste(reference, (GAP, y))
        sheet.paste(model, (PANEL_WIDTH + GAP * 2, y))
        y += row_height + GAP
    destination = root / f"{FAMILY}_comparison.jpg"
    sheet.save(destination, quality=91, optimize=True, progressive=True)
    combined = ROOT / "wave10-school-comparison.jpg"
    sheet.save(combined, quality=91, optimize=True, progressive=True)
    print(f"[wave10-comparison] {destination.relative_to(REPO)}")
    print(f"[wave10-comparison] {combined.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
