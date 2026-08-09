"""Publish the bounded v80 exact-image-lock review set."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "two-building-v80"
OUTPUT = REPO / "docs" / "reviews" / "two-building-image-lock-v80"

ROWS = [
    {
        "slug": "amsterdam",
        "title": "Amsterdam Step-Gable House",
        "reference": "frontend/public/archetypes/buildings/amsterdam-step-gable-house/variant_0.png",
        "roof_reference": "frontend/public/archetypes/buildings/amsterdam-step-gable-house/variant_0_angle_90.jpg",
        "family": "amsterdam-step-gable-gothic-v80",
        "view": "front_corner_oblique",
        "status": "KEEPER",
        "finding": "Three occupied levels, exact sash schedules and the capped crow-step remain image-locked. Round two adds a paneled oak door, glazed diamond fanlight and black masonry anchors instead of flat dark placeholders.",
    },
    {
        "slug": "mercat",
        "title": "Barcelona Mercat",
        "reference": "frontend/public/archetypes/buildings/barcelona-mercat/variant_0.png",
        "roof_reference": "frontend/public/archetypes/buildings/barcelona-mercat/variant_0_angle_90.jpg",
        "family": "barcelona-mercat-modernista-v80",
        "view": "archetype_match",
        "status": "PROVISIONAL",
        "finding": "The image-locked roof and real open bays now gain continuous brick piers plus counters, crates, produce and warm task lights on all four frontages. Fine iron ornament and photographic entourage remain provisional.",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, (image.height - size[1]) // 2)
    return image.crop((left, top, left + size[0], top + size[1]))


def contain(path: Path, size: tuple[int, int], background: str = "#20272d") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def generated_path(row: dict, suffix: str) -> Path:
    return ARTIFACTS / row["slug"] / f'{row["family"]}_{suffix}.png'


def publish_files() -> None:
    generated = OUTPUT / "generated"
    reports = OUTPUT / "reports"
    generated.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    for row in ROWS:
        for suffix in (row["view"], "aerial", "roof_audit"):
            shutil.copy2(
                generated_path(row, suffix),
                generated / f'{row["family"]}_{suffix}.png',
            )
        for name in ("validation_report.json", "production_preflight.json"):
            source = ARTIFACTS / row["slug"] / name
            if source.exists():
                shutil.copy2(source, reports / f'{row["family"]}-{name}')


def comparison_board() -> Path:
    width, row_height, header_height = 2400, 570, 150
    board = Image.new("RGB", (width, header_height + row_height * len(ROWS)), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 28), "v81 refinement — exact archetype vs generated geometry", font=font(42, True), fill="#f5f1e8")
    draw.text((55, 88), "Image-lock topology | real void depth | occupied opening kits | material continuity", font=font(24), fill="#aeb8c2")
    tile = (880, 470)
    for index, row in enumerate(ROWS):
        y = header_height + index * row_height
        draw.rectangle((0, y, width, y + row_height), fill="#192128" if index % 2 == 0 else "#151c22")
        board.paste(cover(REPO / row["reference"], tile), (35, y + 25))
        board.paste(contain(generated_path(row, row["view"]), tile), (950, y + 25))
        colour = "#72d39b" if row["status"] == "KEEPER" else "#f2bd69"
        draw.text((1865, y + 35), row["status"], font=font(23, True), fill=colour)
        draw.text((1865, y + 78), row["title"], font=font(28, True), fill="#f5f1e8")
        wrapped = textwrap.wrap(row["finding"], width=38)
        draw.multiline_text((1865, y + 132), "\n".join(wrapped), font=font(21), fill="#cad2d9", spacing=8)
        draw.text((50, y + 515), "EXACT ARCHETYPE", font=font(19, True), fill="#e8dcc6")
        draw.text((965, y + 515), "GENERATED v80", font=font(19, True), fill="#e8dcc6")
    path = OUTPUT / "two-building-comparison.png"
    board.save(path, optimize=True)
    return path


def roof_board() -> Path:
    width, row_height, header_height = 2400, 500, 140
    board = Image.new("RGB", (width, header_height + row_height * len(ROWS)), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 26), "v81 refinement — roof-plan and material audit", font=font(42, True), fill="#f5f1e8")
    draw.text((55, 83), "Exact aerial evidence beside the generated aerial and independent roof-audit camera", font=font(23), fill="#aeb8c2")
    tile = (730, 410)
    for index, row in enumerate(ROWS):
        y = header_height + index * row_height
        draw.rectangle((0, y, width, y + row_height), fill="#192128" if index % 2 == 0 else "#151c22")
        board.paste(cover(REPO / row["roof_reference"], tile), (35, y + 25))
        board.paste(cover(generated_path(row, "aerial"), tile), (800, y + 25))
        board.paste(cover(generated_path(row, "roof_audit"), tile), (1565, y + 25))
        draw.text((50, y + 450), f'{row["title"]} — REFERENCE', font=font(18, True), fill="#e8dcc6")
        draw.text((815, y + 450), "GENERATED AERIAL", font=font(18, True), fill="#e8dcc6")
        draw.text((1580, y + 450), "GENERATED ROOF AUDIT", font=font(18, True), fill="#e8dcc6")
    path = OUTPUT / "two-building-roof-audit.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    publish_files()
    comparison = comparison_board()
    roof = roof_board()
    summary = {
        "schema": "two-building-image-lock-review@1",
        "pipeline_version": "v81 refinement on v80 image-lock pilots",
        "method": [
            "exact reference roles become numeric feature schedules",
            "required graph nodes, assemblies and voids are production gates",
            "metadata is disabled or selectively admitted only when image-consistent",
            "human comparison remains the final keeper decision",
            "occupied opening kits add bounded public-edge detail without changing validated topology",
        ],
        "buildings": [
            {
                "family": row["family"],
                "status": row["status"].lower(),
                "reference": row["reference"],
                "generated": f'generated/{row["family"]}_{row["view"]}.png',
                "finding": row["finding"],
            }
            for row in ROWS
        ],
    }
    (OUTPUT / "review-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(comparison)
    print(roof)


if __name__ == "__main__":
    main()
