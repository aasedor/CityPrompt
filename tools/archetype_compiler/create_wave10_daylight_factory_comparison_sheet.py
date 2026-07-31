"""Create a phone-readable reference/model comparison for the daylight factory."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
FAMILY = "historic-daylight-factory"
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


def panel(
    path: Path,
    label: str,
    *,
    centering: tuple[float, float] = (0.5, 0.5),
) -> Image.Image:
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
                "CANONICAL FOUR-VIEW FACTORY GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_preview.png",
                "MODEL - COMPLETE BRICK NORTHLIGHT HALL",
            ),
        ),
        (
            panel(
                source / "front-elevation-source-v1.png",
                "BRICK PIERS / STEEL-SASH / ENTRY GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_front_elevation.png",
                "MODEL - PHYSICAL OPENINGS / CORBEL COURSE",
            ),
        ),
        (
            panel(
                source / "aerial-roof-source-v1.png",
                "SEVEN NORTHLIGHT TEETH / DRAINAGE GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_aerial.png",
                "MODEL - SEVEN ZINC + GLASS ROOF ASSEMBLIES",
            ),
        ),
        (
            panel(
                source / "loading-court-source-v1.png",
                "THREE-DOCK WORKING REAR GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_rear_loading.png",
                "MODEL - RECESSES / PLATFORMS / REAL STAIRS",
            ),
        ),
        (
            panel(
                source / "occupied-workshop-source-v1.png",
                "THIN STEEL SASH / OCCUPIED DEPTH GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_window_close.png",
                "MODEL - LOW-E PANES / MULLIONS / PARALLAX",
            ),
        ),
        (
            panel(
                source / "street-hero-source-v1.png",
                "PROJECTING ADMINISTRATION ENTRY GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_entrance_close.png",
                "MODEL - RECESSED DOORS / CANOPY / HARDWARE",
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
        "Historic Daylight Factory - reference-locked LEGO family",
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
    combined = ROOT / "wave10-daylight-factory-comparison.jpg"
    sheet.save(combined, quality=91, optimize=True, progressive=True)
    print(f"[wave10-comparison] {destination.relative_to(REPO)}")
    print(f"[wave10-comparison] {combined.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
