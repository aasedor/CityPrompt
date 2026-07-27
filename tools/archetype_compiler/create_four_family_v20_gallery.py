"""Create the archetype-versus-GLB review board for the v20 pilot."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build" / "codex-lego-four-family-v20"
FAMILIES = BUILD / "families"
REFERENCES = ROOT / "frontend" / "public" / "archetypes" / "buildings"
OUTPUT = BUILD / "four-family-v20-comparison-board.png"

ROWS = [
    {
        "name": "Collegiate Gothic",
        "slug": "collegiate-gothic-education",
        "reference": REFERENCES / "collegiate_gothic_education" / "variant_0.png",
        "provider": "cached facade + semantic Gothic geometry",
    },
    {
        "name": "Modern Glass Office",
        "slug": "modern-glass-office-institutional",
        "reference": REFERENCES / "modern_glass_office_institutional" / "variant_0.png",
        "provider": "new Gemini elevation + physical curtain wall",
    },
    {
        "name": "Nordic Residential",
        "slug": "nordic-timber-midrise",
        "reference": REFERENCES / "nordic_timber_midrise" / "variant_0.png",
        "provider": "cached facade + timber picture-frame kit",
    },
    {
        "name": "Classical Civic Building",
        "slug": "civic-classical-building",
        "reference": REFERENCES / "civic_classical_building" / "variant_0.png",
        "provider": "GPT elevation + fixed four-column portico",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def fitted(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def main() -> None:
    width = 1920
    margin = 42
    header_h = 170
    row_h = 500
    gutter = 20
    card_w = (width - margin * 2 - gutter * 2) // 3
    image_h = 350
    height = header_h + len(ROWS) * row_h + margin
    canvas = Image.new("RGB", (width, height), "#f4f1e9")
    draw = ImageDraw.Draw(canvas)

    draw.text((margin, 32), "CITY PROMPT LEGO V20", font=font(25, True), fill="#2f6940")
    draw.text(
        (margin, 68), "Four archetypes → four validated, resizable 3D families",
        font=font(42, True), fill="#132234",
    )
    draw.text(
        (margin, 124),
        "Goalpost, street-level physical model, and aerial massing — full PBR@5, fixed semantic ends, repeatable middle bays",
        font=font(20), fill="#536170",
    )

    headings = ("ARCHETYPE GOALPOST", "V20 STREET MODEL", "V20 AERIAL / ROOF")
    for row_index, item in enumerate(ROWS):
        y = header_h + row_index * row_h
        family = FAMILIES / item["slug"]
        manifest = json.loads((family / f"{item['slug']}_manifest.json").read_text(encoding="utf-8"))
        assessment = json.loads((family / "quality_assessment.json").read_text(encoding="utf-8"))
        assembled = manifest["assembled"]

        draw.rounded_rectangle(
            (margin - 16, y + 8, width - margin + 16, y + row_h - 18),
            radius=18, fill="#fffdf8", outline="#d9d2c4", width=2,
        )
        draw.text((margin, y + 26), item["name"], font=font(29, True), fill="#17283b")
        details = (
            f"{assembled['footprint_target']['width_m']:.0f} × "
            f"{assembled['footprint_target']['depth_m']:.0f} m · "
            f"{assembled['floors']} floors · {assembled['triangle_count']:,} tris · "
            f"QUALITY MEMORY: {assessment['status'].upper()}"
        )
        draw.text((margin + 360, y + 32), details, font=font(17, True), fill="#2f6940")

        paths = (
            item["reference"],
            family / f"{item['slug']}_street.png",
            family / f"{item['slug']}_aerial.png",
        )
        for column, (heading, path) in enumerate(zip(headings, paths)):
            x = margin + column * (card_w + gutter)
            image_y = y + 90
            draw.rectangle((x, image_y - 30, x + card_w, image_y), fill="#17283b" if column == 0 else "#2f6940")
            draw.text((x + 12, image_y - 25), heading, font=font(15, True), fill="white")
            canvas.paste(fitted(path, (card_w, image_h)), (x, image_y))
            draw.rectangle((x, image_y, x + card_w, image_y + image_h), outline="#c8c0b2", width=2)

        draw.text((margin, y + 450), item["provider"], font=font(17), fill="#687382")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
