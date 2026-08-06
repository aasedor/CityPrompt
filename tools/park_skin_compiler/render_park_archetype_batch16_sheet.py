"""Render the ten-family, four-variant Batch 16 reference/skin sheet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = Path(__file__).with_name("park_archetype_batch16_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "docs/park_lego_batch16/park_lego_batch16_four_variant_sheet.jpg"
PARENTS = (
    "community_park", "regional_park", "dog_park", "skate_park",
    "sports_field_complex", "tennis_court_cluster", "botanical_garden",
    "japanese_garden", "memorial_garden", "urban_forest",
)
ANCHORS = {
    ("community_park", 0): "community-park-english-pastoral",
    ("regional_park", 0): "regional-park-english-landscape",
    ("dog_park", 0): "dog-park",
    ("skate_park", 0): "skate-park",
    ("sports_field_complex", 0): "sports-complex-tournament",
    ("tennis_court_cluster", 0): "tennis-court-professional",
    ("botanical_garden", 0): "botanical-collection-garden",
    ("botanical_garden", 3): "botanical-romantic-rose-garden-v3",
    ("japanese_garden", 0): "japanese-stroll-garden",
    ("memorial_garden", 0): "memorial-garden-classical-formal",
    ("urban_forest", 0): "urban-forest-native",
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
    draw.text((32, 22), "PARK LEGO BATCH 16 - FOUR-VARIANT REFERENCE / SKIN CLOSURE", fill="white", font=font)
    draw.text((32, 48), "29 new archetype-derived skins + 11 retained anchors | shared measured parcel grammar | no people, AI drape, or embedded buildings", fill="#c9d8c8", font=font)
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
                    # Historical anchor packs may be an unhydrated LFS pointer
                    # in an isolated worktree. The source card remains the
                    # authoritative visual reference for that retained anchor.
                    swatch_source = reference
                canvas.paste(cover(swatch_source, (58, 58)), (left + role_index * 67, top + 216))
                draw.text((left + role_index * 67, top + 276), role[:4].upper(), fill="#505852", font=font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, quality=90, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
