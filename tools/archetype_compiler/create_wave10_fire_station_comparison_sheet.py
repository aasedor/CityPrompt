"""Create a phone-readable reference/model comparison for Wave 10 fire station."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
FAMILY = "modern-fire-station-mass-timber"
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
            panel(
                source / "archetype-goalpost.png",
                "ORIGINAL THREE-BAY IDENTITY GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_front_corner_oblique.png",
                "MODEL - MATCHED CIVIC STREET CORNER",
            ),
        ),
        (
            panel(
                source / "front-elevation-source-v1.png",
                "RECTIFIED PUBLIC ELEVATION",
            ),
            panel(
                root / f"{FAMILY}_street.png",
                "MODEL - THREE DRIVE-THROUGH BAYS",
            ),
        ),
        (
            panel(
                source / "aerial-roof-source-v1.png",
                "MEADOW / PHOTOVOLTAIC ROOF GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_aerial.png",
                "MODEL - PLANTED ROOF / TWO PV FIELDS",
            ),
        ),
        (
            panel(
                source / "rear-service-source-v1.png",
                "REAR DRIVE-THROUGH / SERVICE GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_rear_corner_oblique.png",
                "MODEL - COMPLETE REAR OPERATIONS",
            ),
        ),
        (
            panel(
                source / "glazing-occupied-depth-source-v1.png",
                "APPARATUS / CREW GLAZING GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_apparatus_close.png",
                "MODEL - PHYSICAL LOW-E / MODELED ENGINE",
                centering=(0.50, 0.56),
            ),
        ),
        (
            panel(
                source / "integrated-training-tower-source-v1.png",
                "INTEGRATED STAIR / TRAINING TOWER GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_tower_close.png",
                "MODEL - REAL STAIRS BEHIND CHANNEL GLASS",
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
        "Mass-Timber Fire Station - reference-locked LEGO family",
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
    combined = ROOT / "wave10-fire-station-comparison.jpg"
    sheet.save(combined, quality=91, optimize=True, progressive=True)
    print(f"[wave10-comparison] {destination.relative_to(REPO)}")
    print(f"[wave10-comparison] {combined.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
