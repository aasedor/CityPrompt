"""Create a phone-readable reference/model comparison for the Wave 10 motor inn."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "frontend" / "public" / "families"
FAMILY = "prairie-courtyard-motor-inn"
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
                "CANONICAL PRAIRIE MOTOR-INN GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_preview.png",
                "MODEL - L WINGS / LOBBY / POOL COURT",
            ),
        ),
        (
            panel(
                source / "courtyard-elevation-source-v1.png",
                "ROOM-BAY / GALLERY / ROOF DATUM GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_street.png",
                "MODEL - FOURTEEN BAYS / TWO LEVELS",
            ),
        ),
        (
            panel(
                source / "aerial-roof-source-v1.png",
                "L PLAN / HIP ROOFS / SITE GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_aerial.png",
                "MODEL - CLEAN ROOF JOINTS / FENCED POOL",
            ),
        ),
        (
            panel(
                source / "integrated-stair-source-v1.png",
                "STRUCTURAL STAIR / LANDING GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_stair_close.png",
                "MODEL - 18 TREADS / STRINGERS / RAILS",
            ),
        ),
        (
            panel(
                source / "guest-window-source-v1.png",
                "LOW-E WINDOW / OCCUPIED ROOM GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_window_close.png",
                "MODEL - PHYSICAL PANES / CURTAINS / DEPTH",
            ),
        ),
        (
            panel(
                source / "lobby-entry-source-v1.png",
                "PROJECTING GLAZED ARRIVAL GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_lobby_close.png",
                "MODEL - VESTIBULE / CANOPY / WARM SOFFIT",
            ),
        ),
        (
            panel(
                source / "rear-service-source-v1.png",
                "QUIET OPERATIONAL REAR GOALPOST",
            ),
            panel(
                root / f"{FAMILY}_service_close.png",
                "MODEL - CONDENSERS / METERS / REFUSE",
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
        "Prairie Courtyard Motor Inn - reference-locked LEGO family",
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
    combined = ROOT / "wave10-motor-inn-comparison.jpg"
    sheet.save(combined, quality=91, optimize=True, progressive=True)
    print(f"[wave10-comparison] {destination.relative_to(REPO)}")
    print(f"[wave10-comparison] {combined.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
