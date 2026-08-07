"""Render a mobile-friendly four-variant comparison for the Batch 15 pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULES = (
    Path(__file__).with_name("park_archetype_batch14_skin_sources.json"),
    Path(__file__).with_name("park_archetype_batch15_skin_sources.json"),
)
DEFAULT_OUT = REPO_ROOT / "docs/park_lego_batch15/park_lego_batch15_four_variant_sheet.jpg"
PARENTS = (
    "surface_parking_lot", "structured_parking_garage", "underground_parking_entry",
    "green_parking_lot", "airport_airfield", "equestrian_center", "golf_course_18_hole",
    "golf_driving_range", "multi_sport_complex", "suburban_retail_parking_lot",
)
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skin-root", type=Path, default=REPO_ROOT / "frontend/public/park-skins")
    args = parser.parse_args()
    source_to_slug: dict[str, str] = {}
    for schedule_path in SCHEDULES:
        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
        source_to_slug.update({item["source"]: slug for slug, item in schedule["archetypes"].items()})
    catalogue = json.loads((REPO_ROOT / "frontend/src/data/openSpaceArchetypes.json").read_text(encoding="utf-8"))
    archetypes = {item["id"]: item for item in catalogue["archetypes"]}
    width, row_height = 1800, 300
    canvas = Image.new("RGB", (width, 110 + row_height * len(PARENTS)), "#ebe6dc")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, width, 90), fill="#222a27")
    draw.text((32, 22), "PARK LEGO BATCH 15 - FOUR-VARIANT REFERENCE / SKIN CLOSURE", fill="white", font=font)
    draw.text((32, 48), "30 new exact-reference skins + 10 retained anchors | variant-aware geometry | no people, AI drape, or large buildings", fill="#c9d8c8", font=font)
    for row, parent_id in enumerate(PARENTS):
        top = 98 + row * row_height
        draw.rectangle((16, top, width - 16, top + row_height - 8), fill="#f8f5ee", outline="#c8c0b3", width=2)
        draw.text((28, top + 8), parent_id.replace("_", " ").upper(), fill="#29322e", font=font)
        for column, variant in enumerate(archetypes[parent_id]["variants"]):
            left = 28 + column * 438
            source = f"frontend/public{variant['thumbnailUrl']}"
            slug = source_to_slug[source]
            reference = cover(Image.open(REPO_ROOT / source).convert("RGB"), (405, 175))
            canvas.paste(reference, (left, top + 30))
            draw.rectangle((left, top + 190, left + 405, top + 207), fill="#222a27")
            draw.text((left + 6, top + 192), f"V{column}  {variant['label']}", fill="white", font=font)
            for role_index, role in enumerate(ROLES):
                swatch_path = args.skin_root / slug / "adaptive-v1" / role / "albedo.jpg"
                swatch = cover(Image.open(swatch_path).convert("RGB"), (58, 58))
                swatch_left = left + role_index * 67
                canvas.paste(swatch, (swatch_left, top + 216))
                draw.text((swatch_left, top + 276), role[:4].upper(), fill="#505852", font=font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, quality=90, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
