"""Create the review board for the five-family v21 methodology expansion."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "build" / "codex-lego-five-family-v21"
REFINED = ROOT / "build" / "codex-lego-five-family-v21r"
REFERENCES = ROOT / "frontend" / "public" / "archetypes" / "buildings"
OUTPUT = REFINED / "five-family-v21-comparison-board.png"

ROWS = [
    {
        "name": "London Heritage Mansion Block",
        "archetype": "london_heritage_mansion_block",
        "reference": REFERENCES / "london-heritage-mansion-block" / "hero.png",
        "slug": "london-heritage-mansion-block",
        "family": BASELINE / "london-heritage-mansion-block",
        "method": "fixed ends + carved stone bays + occupied sash glazing",
    },
    {
        "name": "Industrial Brick Mixed Use",
        "archetype": "industrial_brick_mixed_use",
        "reference": REFERENCES / "industrial_brick_mixed_use" / "variant_0.png",
        "slug": "industrial-brick-mixed-use",
        "family": REFINED / "industrial-brick-mixed-use",
        "method": "shadow-neutral brick PBR + masonry corbels + roof monitor",
    },
    {
        "name": "Eixample Apartment Block",
        "archetype": "eixample_apartment_block",
        "reference": REFERENCES / "eixample-apartment-block" / "variant_0.png",
        "slug": "eixample-apartment-block",
        "family": REFINED / "eixample-apartment-block",
        "method": "true Cerda chamfer + oriented corner skin + open iron balconies",
    },
    {
        "name": "Modernist Civic Block",
        "archetype": "modernist_civic_block",
        "reference": REFERENCES / "modernist_civic_block" / "variant_0.png",
        "slug": "modernist-civic-block",
        "family": BASELINE / "modernist-civic-block",
        "method": "floating mass + pilotis + cantilevered roof + deep brise-soleil",
    },
    {
        "name": "Chateauesque Grand Railway Hotel",
        "archetype": "chateauesque_grand_railway_hotel",
        "reference": REFERENCES / "chateauesque-grand-railway-hotel" / "variant_0.png",
        "slug": "chateauesque-grand-railway-hotel",
        "family": REFINED / "chateauesque-grand-railway-hotel",
        "method": "steep roof family + fixed pavilions + towers + porte cochere",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def fitted(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def main() -> None:
    width, margin, gutter = 1920, 42, 20
    header_h, row_h, image_h = 170, 500, 350
    card_w = (width - margin * 2 - gutter * 2) // 3
    canvas = Image.new("RGB", (width, header_h + len(ROWS) * row_h + margin), "#f4f1e9")
    draw = ImageDraw.Draw(canvas)

    draw.text((margin, 30), "CITY PROMPT LEGO V21", font=font(25, True), fill="#2f6940")
    draw.text((margin, 66), "Five new families built with the reusable methodology", font=font(42, True), fill="#132234")
    draw.text(
        (margin, 123),
        "Archetype goalpost, street model, and aerial massing - PBR facades, physical depth, fixed identity, repeatable capacity",
        font=font(20), fill="#536170",
    )

    headings = ("ARCHETYPE GOALPOST", "V21 STREET MODEL", "V21 AERIAL / ROOF")
    for row_index, item in enumerate(ROWS):
        y = header_h + row_index * row_h
        family = item["family"]
        manifest = json.loads((family / f"{item['slug']}_manifest.json").read_text(encoding="utf-8"))
        assessment_path = family / "quality_assessment.json"
        status = "VALIDATED"
        if assessment_path.exists():
            status = json.loads(assessment_path.read_text(encoding="utf-8"))["status"].upper()
        assembled = manifest["assembled"]

        draw.rounded_rectangle(
            (margin - 16, y + 8, width - margin + 16, y + row_h - 18),
            radius=18, fill="#fffdf8", outline="#d9d2c4", width=2,
        )
        draw.text((margin, y + 25), item["name"], font=font(29, True), fill="#17283b")
        details = (
            f"{assembled['footprint_target']['width_m']:.0f} x "
            f"{assembled['footprint_target']['depth_m']:.0f} m  |  "
            f"{assembled['floors']} floors  |  {assembled['triangle_count']:,} tris  |  {status}"
        )
        draw.text((margin + 540, y + 32), details, font=font(17, True), fill="#2f6940")

        paths = (
            item["reference"],
            family / f"{item['slug']}_street.png",
            family / f"{item['slug']}_aerial.png",
        )
        for column, (heading, path) in enumerate(zip(headings, paths)):
            x, image_y = margin + column * (card_w + gutter), y + 90
            draw.rectangle((x, image_y - 30, x + card_w, image_y), fill="#17283b" if column == 0 else "#2f6940")
            draw.text((x + 12, image_y - 25), heading, font=font(15, True), fill="white")
            canvas.paste(fitted(path, (card_w, image_h)), (x, image_y))
            draw.rectangle((x, image_y, x + card_w, image_y + image_h), outline="#c8c0b2", width=2)

        draw.text((margin, y + 450), item["method"], font=font(17), fill="#687382")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
