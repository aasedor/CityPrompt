"""Publish the bounded v78 five-building material/void review set."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "five-building-v78"
OUTPUT = REPO / "docs" / "reviews" / "five-building-material-void-v78"

ROWS = [
    {
        "title": "Arts & Crafts Heritage",
        "reference": "frontend/public/archetypes/buildings/historical_brick_main_street/variant_2.png",
        "family": "historical-brick-arts-crafts-v78",
        "view": "archetype_match",
        "status": "PROVISIONAL",
        "finding": "Two-storey twin-gable mass, green tile skin and 1.8 m entry recess now follow the photo. Exact leaded glazing and half-timber infill still need a variant-native atlas.",
        "void_crop": [0.37, 0.43, 0.68, 0.91],
    },
    {
        "title": "Neoclassical Courthouse",
        "reference": "frontend/public/archetypes/buildings/monumental_courthouse_axis/variant_0.png",
        "family": "courthouse-neoclassical-v78",
        "view": "archetype_match",
        "status": "KEEPER",
        "finding": "Eight-column portico, broad stair, pediment, low green-copper roof and 4 m entry section replace the rejected Art Deco/classical atlas mismatch.",
        "void_crop": [0.54, 0.40, 0.78, 0.87],
    },
    {
        "title": "Italian Portici Block",
        "reference": "frontend/public/archetypes/buildings/mediterranean_arcade_mixed_use/variant_0.png",
        "family": "mediterranean-portici-v78",
        "view": "archetype_match",
        "status": "KEEPER",
        "finding": "Five construction-depth stone arches, framed set-back shop wall, ochre upper floors and a low textured hip roof reproduce the main hierarchy.",
        "void_crop": [0.28, 0.51, 0.76, 0.94],
    },
    {
        "title": "Romanesque Revival Warehouse",
        "reference": "frontend/public/archetypes/buildings/romanesque_revival_warehouse/variant_0.png",
        "family": "romanesque-warehouse-v78",
        "view": "archetype_match",
        "status": "KEEPER",
        "finding": "The existing exact-style atlas combines well with five 2.8 m loading recesses, a rusticated base and a textured membrane roof.",
        "void_crop": [0.22, 0.52, 0.84, 0.94],
    },
    {
        "title": "Scandinavian Courtyard Block",
        "reference": "frontend/public/archetypes/buildings/scandinavian_urban_residential/variant_0.png",
        "family": "scandinavian-passage-v78",
        "view": "archetype_match",
        "status": "PROVISIONAL",
        "finding": "The 4.2 m timber-lined through-passage opens into a real court and the zinc roof is corrected. Smooth plaster, dormers and projecting balconies need a variant-native atlas/kit.",
        "void_crop": [0.41, 0.52, 0.68, 0.94],
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, (image.height - size[1]) // 2)
    return image.crop((left, top, left + size[0], top + size[1]))


def contain(path: Path, size: tuple[int, int], background=(31, 35, 39)) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def crop_normalized(path: Path, bounds: list[float], size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    left, top, right, bottom = bounds
    crop = image.crop((
        round(image.width * left), round(image.height * top),
        round(image.width * right), round(image.height * bottom),
    ))
    scale = max(size[0] / crop.width, size[1] / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)
    left_px = max(0, (crop.width - size[0]) // 2)
    top_px = max(0, (crop.height - size[1]) // 2)
    return crop.crop((left_px, top_px, left_px + size[0], top_px + size[1]))


def generated_path(row: dict, suffix: str | None = None) -> Path:
    suffix = suffix or row["view"]
    return ARTIFACTS / row["family"] / f'{row["family"]}_{suffix}.png'


def publish_files() -> None:
    generated = OUTPUT / "generated"
    reports = OUTPUT / "reports"
    generated.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    for row in ROWS:
        shutil.copy2(generated_path(row), generated / f'{row["family"]}.png')
        for name in ("validation_report.json", "production_preflight.json"):
            source = ARTIFACTS / row["family"] / name
            if source.exists():
                shutil.copy2(source, reports / f'{row["family"]}-{name}')


def street_board() -> Path:
    width, row_height = 2400, 350
    header_height = 150
    board = Image.new("RGB", (width, header_height + row_height * len(ROWS)), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 28), "Five-building v78 — exact archetype vs generated model", font=font(42, True), fill="#f5f1e8")
    draw.text((55, 87), "Reference authority | construction-depth voids | material continuity | human visual status", font=font(24), fill="#aeb8c2")
    image_size = (650, 300)
    for index, row in enumerate(ROWS):
        y = header_height + index * row_height
        fill = "#192128" if index % 2 == 0 else "#151c22"
        draw.rectangle((0, y, width, y + row_height), fill=fill)
        ref = cover(REPO / row["reference"], image_size)
        model = cover(generated_path(row), image_size)
        board.paste(ref, (40, y + 25))
        board.paste(model, (725, y + 25))
        tx = 1410
        colour = "#72d39b" if row["status"] == "KEEPER" else "#f2bd69"
        draw.text((tx, y + 30), row["status"], font=font(22, True), fill=colour)
        draw.text((tx, y + 67), row["title"], font=font(30, True), fill="#f5f1e8")
        wrapped = textwrap.wrap(row["finding"], width=61)
        draw.multiline_text((tx, y + 116), "\n".join(wrapped), font=font(22), fill="#cad2d9", spacing=8)
        draw.text((55, y + 290), "EXACT ARCHETYPE", font=font(18, True), fill="#e8dcc6")
        draw.text((740, y + 290), "GENERATED v78", font=font(18, True), fill="#e8dcc6")
    path = OUTPUT / "five-building-comparison.png"
    board.save(path, optimize=True)
    return path


def audit_board() -> Path:
    tile = (440, 330)
    width, height = 2280, 820
    board = Image.new("RGB", (width, height), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((40, 25), "v78 roof and spatial-void audit", font=font(40, True), fill="#f5f1e8")
    draw.text((40, 79), "Aerial view verifies roof material/topology; close view verifies recess/through-passage construction.", font=font(22), fill="#aeb8c2")
    for index, row in enumerate(ROWS):
        x = 30 + index * 450
        board.paste(contain(generated_path(row, "aerial"), tile), (x, 130))
        board.paste(crop_normalized(generated_path(row), row["void_crop"], tile), (x, 470))
        draw.text((x + 10, 145), row["title"], font=font(18, True), fill="#ffffff")
    path = OUTPUT / "five-building-spatial-roof-audit.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    publish_files()
    street = street_board()
    audit = audit_board()
    summary = {
        "schema": "five-building-material-void-review@1",
        "pipeline_version": "v78",
        "buildings": [
            {
                "family": row["family"],
                "status": row["status"].lower(),
                "reference": row["reference"],
                "generated": f'generated/{row["family"]}.png',
                "finding": row["finding"],
            }
            for row in ROWS
        ],
    }
    (OUTPUT / "review-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(street)
    print(audit)


if __name__ == "__main__":
    main()
