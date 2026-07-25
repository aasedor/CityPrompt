"""Build the archetype -> GPT facade -> 3D model comparison board."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROOT = REPO_ROOT / "build" / "gpt-image-brick-pilot-v12"
FAMILY_ROOT = BUILD_ROOT / "industrial-brick-mixed-use"
SHEET_ROOT = (
    REPO_ROOT / "tools" / "archetype_compiler" / "facade_sheets_openai"
    / "industrial-brick-mixed-use"
)
OUTPUT = BUILD_ROOT / "gpt-image-brick-pilot-board.png"


def font(size: int, *, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def panel(path: Path, label: str, colour: str, size: tuple[int, int]) -> Image.Image:
    header = 48
    source = Image.open(path).convert("RGB")
    framed = ImageOps.fit(source, (size[0], size[1] - header), Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#ece8df")
    result.paste(framed, (0, header))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], header), fill=colour)
    draw.text((14, 13), label, font=font(18, bold=True), fill="white")
    return result


def main() -> None:
    canvas = Image.new("RGB", (2160, 720), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((38, 26), "GPT Image facade -> real LEGO GLB", font=font(38, bold=True), fill="#132333")
    draw.text(
        (40, 76),
        "Industrial Brick Loft pilot | exact catalogue card | 7,008 triangles | 3.22 MB | validation pass",
        font=font(20),
        fill="#536472",
    )
    paths = (
        REPO_ROOT / "frontend/public/archetypes/buildings/industrial_brick_mixed_use/variant_0.png",
        SHEET_ROOT / "elevation_raw.png",
        FAMILY_ROOT / "industrial-brick-mixed-use_street.png",
        FAMILY_ROOT / "industrial-brick-mixed-use_context.png",
    )
    labels = (
        ("ARCHETYPE GOALPOST", "#142536"),
        ("GPT IMAGE FACADE", "#764d2c"),
        ("3D MODEL - STREET", "#347711"),
        ("3D MODEL - CITY CONTEXT", "#23677a"),
    )
    panel_size = (500, 550)
    for x, path, (label, colour) in zip((40, 565, 1090, 1615), paths, labels):
        if not path.exists():
            raise SystemExit(f"missing gallery input: {path}")
        canvas.paste(panel(path, label, colour, panel_size), (x, 130))
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
