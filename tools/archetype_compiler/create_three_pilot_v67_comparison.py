"""Create the v67 archetype-versus-render pilot review board."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "artifacts" / "pilot-v67" / "three-pilot-archetype-comparison.png"
PILOTS = (
    (
        "CIVIC CLASSICAL · LIMESTONE IONIC",
        "frontend/public/archetypes/buildings/civic_classical_building/variant_0.png",
        "artifacts/pilot-v67/final/civic-classical-building/civic-classical-building_archetype_match.png",
        "STRONG PILOT",
        "A- · Portico, low civic proportion, limestone and arched wing openings survive.",
        "#2f7d45",
    ),
    (
        "COLLEGIATE GOTHIC · JACOBETHAN",
        "frontend/public/archetypes/buildings/collegiate_gothic_education/variant_1.png",
        "artifacts/pilot-v67/final/collegiate-gothic-education/collegiate-gothic-education_archetype_match.png",
        "KEEP WITH REVISION",
        "B · Brick/stone rhythm, shaped gables and quadrangle roof read; centre bay needs cleanup.",
        "#a36a18",
    ),
    (
        "RAILWAY HOTEL · SCOTTISH BARONIAL GRANITE",
        "frontend/public/archetypes/buildings/chateauesque-grand-railway-hotel/variant_0.png",
        "artifacts/pilot-v67/final/chateauesque-grand-railway-hotel/chateauesque-grand-railway-hotel_archetype_match.png",
        "PIPELINE FAILURE",
        "C- · Correct granite/storey identity, but tower hierarchy and oblique side construction fail.",
        "#a33a2d",
    ),
)


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#e7e5df")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    width, row_h = 1760, 560
    board = Image.new("RGB", (width, 150 + row_h * len(PILOTS) + 30), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((40, 24), "Three new building pilots · v67 fidelity review", font=font(38, True), fill="#101b2b")
    draw.text(
        (42, 78),
        "Authoritative archetype photo vs. the same-camera modular LEGO render. Technical validation is separate from visual acceptance.",
        font=font(19), fill="#5f6c7d",
    )
    draw.rectangle((40, 119, width - 40, 127), fill="#91c83e")

    for index, (title, reference, render, status, note, colour) in enumerate(PILOTS):
        y = 150 + index * row_h
        draw.rounded_rectangle((28, y + 10, width - 28, y + row_h - 12), radius=14, fill="#fffdf8", outline="#d8d0c2", width=2)
        draw.text((52, y + 28), title, font=font(25, True), fill="#101b2b")
        draw.text((width - 350, y + 30), status, font=font(18, True), fill=colour)
        left = contain(REPO / reference, (800, 410))
        right = contain(REPO / render, (800, 410))
        board.paste(left, (52, y + 78))
        board.paste(right, (908, y + 78))
        draw.rectangle((52, y + 78, 852, y + 488), outline="#c9c3b8", width=2)
        draw.rectangle((908, y + 78, 1708, y + 488), outline="#c9c3b8", width=2)
        draw.rectangle((52, y + 78, 196, y + 110), fill="#101b2b")
        draw.text((64, y + 85), "ARCHETYPE", font=font(14, True), fill="white")
        draw.rectangle((908, y + 78, 1088, y + 110), fill="#101b2b")
        draw.text((920, y + 85), "LEGO MODEL v67", font=font(14, True), fill="white")
        draw.text((52, y + 505), note, font=font(17), fill="#273548")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    board.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
