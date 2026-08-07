"""Publish deterministic Scottish Baronial v68 review boards."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs" / "reviews" / "scottish-baronial-v68"
REFERENCE = REPO / "frontend/public/archetypes/buildings/chateauesque-grand-railway-hotel"
BASELINE = REPO / "artifacts/pilot-v67/final/chateauesque-grand-railway-hotel"
FINAL = REPO / "artifacts/pilot-v68/final-v2/chateauesque-grand-railway-hotel"
FIDELITY = REPO / "artifacts/pilot-v68/final-v2/fidelity"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e6e3dc") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def labelled_panel(
    board: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    box: tuple[int, int, int, int],
    label: str,
) -> None:
    x0, y0, x1, y1 = box
    panel = contain(path, (x1 - x0, y1 - y0))
    board.paste(panel, (x0, y0))
    draw.rectangle(box, outline="#b8b1a5", width=2)
    label_width = max(160, int(draw.textlength(label, font=font(15, True))) + 28)
    draw.rectangle((x0, y0, x0 + label_width, y0 + 34), fill="#111c2b")
    draw.text((x0 + 12, y0 + 8), label, font=font(15, True), fill="white")


def street_board() -> None:
    board = Image.new("RGB", (1800, 760), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((42, 24), "Scottish Baronial railway hotel · v68 reconstruction", font=font(38, True), fill="#101b2b")
    draw.text(
        (44, 77),
        "Exact archetype vs. v67 inherited massing vs. v68 reference-derived quadrangle. Review result: improved, not yet catalogue gold.",
        font=font(19), fill="#536174",
    )
    draw.rectangle((42, 115, 1758, 123), fill="#91c83e")
    paths = (
        (REFERENCE / "variant_0.png", "ARCHETYPE PHOTO"),
        (BASELINE / "chateauesque-grand-railway-hotel_archetype_match.png", "V67 BASELINE"),
        (FINAL / "chateauesque-grand-railway-hotel_archetype_match.png", "V68 REBUILD"),
    )
    for index, (path, label) in enumerate(paths):
        x0 = 42 + index * 572
        labelled_panel(board, draw, path, (x0, 150, x0 + 540, 630), label)
    draw.text(
        (44, 662),
        "V68 fixes the centered gate tower, perimeter court, crow-stepped gables and four-turret roof hierarchy; gable/turret openings remain simplified.",
        font=font(19), fill="#273548",
    )
    draw.text(
        (44, 700),
        "OpenCV silhouette IoU: v67 0.901 · v68 0.891. The flat result proves why the automated gate remains regression-only.",
        font=font(18, True), fill="#8b5a19",
    )
    board.save(OUTPUT / "street-identity-comparison.png", optimize=True)


def roof_board() -> None:
    board = Image.new("RGB", (1800, 760), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((42, 24), "Roof-plan evidence · reference to constructed massing", font=font(38, True), fill="#101b2b")
    draw.text(
        (44, 77),
        "The high-angle reference is treated as a plan contract: open quadrangle, separate perimeter wings, centered gate tower and corner turrets.",
        font=font(19), fill="#536174",
    )
    draw.rectangle((42, 115, 1758, 123), fill="#91c83e")
    labelled_panel(board, draw, REFERENCE / "variant_0_angle_90.jpg", (42, 150, 872, 650), "ARCHETYPE ROOF VIEW")
    labelled_panel(
        board,
        draw,
        FINAL / "chateauesque-grand-railway-hotel_aerial.png",
        (928, 150, 1758, 650),
        "V68 BLENDER AERIAL",
    )
    draw.text(
        (44, 682),
        "Remaining review item: simplify the generic repeated facade cadence and author local opening schedules for the gables and turret drums.",
        font=font(19), fill="#273548",
    )
    board.save(OUTPUT / "roof-plan-comparison.png", optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    street_board()
    roof_board()
    contain(
        FINAL / "chateauesque-grand-railway-hotel_archetype_match.png",
        (1600, 1000),
    ).save(OUTPUT / "final-archetype-match.png", optimize=True)
    contain(
        FINAL / "chateauesque-grand-railway-hotel_aerial.png",
        (1600, 1000),
    ).save(OUTPUT / "final-aerial.png", optimize=True)
    Image.open(FIDELITY / "fidelity_overlay.png").save(
        OUTPUT / "fidelity-overlay.png", optimize=True
    )
    for path in sorted(OUTPUT.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()
