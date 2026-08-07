"""Render the ten-family, four-variant Batch 20 reference/skin sheet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = Path(__file__).with_name("park_archetype_batch20_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "docs/park_lego_batch20/park_lego_batch20_four_variant_sheet.jpg"
PARENTS = (
    "riparian_buffer", "wetland_rain_garden", "playground_adventure",
    "amphitheater_lawn", "beer_garden", "city_hall_government_plaza",
    "sunken_plaza", "cathedral_religious_forecourt",
    "cultural_institution_forecourt", "stepped_terraced_plaza",
)
ANCHORS = {
    ("riparian_buffer", 0): "riparian-buffer-native",
    ("wetland_rain_garden", 0): "wetland-rain-garden-native",
    ("playground_adventure", 0): "playground-adventure-timber",
    ("amphitheater_lawn", 0): "amphitheater-lawn-terraced",
    ("beer_garden", 0): "beer-garden-munich-chestnut",
    ("city_hall_government_plaza", 2): "city-hall-modernist-fountain-v2",
    ("sunken_plaza", 0): "sunken-plaza-intimate-courtyard",
    ("cathedral_religious_forecourt", 3): "cathedral-mosque-courtyard-v3",
    ("cultural_institution_forecourt", 0): "cultural-museum-terrace-v0",
    ("stepped_terraced_plaza", 3): "stepped-plaza-modernist-cascade",
}
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skin-root", type=Path, default=REPO_ROOT / "frontend/public/park-skins")
    args = parser.parse_args()
    schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    source_to_slug = {item["source"]: slug for slug, item in schedule["archetypes"].items()}
    catalogue = json.loads((REPO_ROOT / "frontend/src/data/openSpaceArchetypes.json").read_text(encoding="utf-8"))
    archetypes = {item["id"]: item for item in catalogue["archetypes"]}
    width, row_height = 1800, 300
    canvas = Image.new("RGB", (width, 110 + row_height * len(PARENTS)), "#ebe6dc")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, width, 90), fill="#222a27")
    draw.text((32, 22), "PARK LEGO BATCH 20 - ECOLOGY / CIVIC REFERENCE-SKIN CLOSURE", fill="white", font=font)
    draw.text((32, 48), "30 new exact-reference skins + 10 retained anchors | parcel-adaptive LEGO grammar | no people, AI drape, or embedded buildings", fill="#c9d8c8", font=font)
    for row, parent_id in enumerate(PARENTS):
        top = 98 + row * row_height
        draw.rectangle((16, top, width - 16, top + row_height - 8), fill="#f8f5ee", outline="#c8c0b3", width=2)
        draw.text((28, top + 8), parent_id.replace("_", " ").upper(), fill="#29322e", font=font)
        for column, variant in enumerate(archetypes[parent_id]["variants"]):
            left = 28 + column * 438
            source = f"frontend/public{variant['thumbnailUrl']}"
            slug = source_to_slug.get(source) or ANCHORS[(parent_id, column)]
            reference = Image.open(REPO_ROOT / source).convert("RGB")
            canvas.paste(cover(reference, (405, 175)), (left, top + 30))
            draw.rectangle((left, top + 190, left + 405, top + 207), fill="#222a27")
            draw.text((left + 6, top + 192), f"V{column}  {variant['label']}", fill="white", font=font)
            for role_index, role in enumerate(ROLES):
                swatch_path = args.skin_root / slug / "adaptive-v1" / role / "albedo.jpg"
                try:
                    swatch_source = Image.open(swatch_path).convert("RGB")
                except (OSError, ValueError):
                    swatch_source = reference
                canvas.paste(cover(swatch_source, (58, 58)), (left + role_index * 67, top + 216))
                draw.text((left + role_index * 67, top + 276), role[:4].upper(), fill="#505852", font=font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, quality=90, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
