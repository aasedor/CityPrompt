"""Render the mobile-friendly Batch 25 archetype-to-material review sheet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from compile_neighborhood_park_skins import REPO_ROOT

SCHEDULE = Path(__file__).with_name("park_archetype_batch25_skin_sources.json")
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")
GROUPS = (
    ("Vancouver Seawall", ("vancouver-seawall-promenade-v0", "vancouver-seawall-bench-v1", "vancouver-seawall-esplanade-v3")),
    ("Vancouver Beach Park", ("vancouver-beach-brick-pavilion-v1", "vancouver-beach-glazed-pavilion-v2", "vancouver-beach-waterfront-garden-v3")),
    ("Toronto Ravine", ("toronto-ravine-spring-trillium-v0", "toronto-ravine-autumn-maple-v2", "toronto-ravine-winter-creek-v3")),
    ("Toronto Urban Square", ("toronto-square-winter-rink-v0", "toronto-square-modernist-pool-v2", "toronto-square-rain-garden-v3")),
    ("Picturesque Olmsted Park", ("olmsted-wild-heath-v0", "olmsted-hillside-lookout-v1", "olmsted-meadow-ravine-lake-v2")),
    ("Reclaimed Industrial Park", ("reclaimed-gasworks-mound-v1", "reclaimed-colliery-headframe-v2", "reclaimed-steelworks-basin-v3")),
    ("Quarry Sunken Garden", ("quarry-sculpture-bowl-v0", "quarry-lake-beach-v1", "quarry-show-garden-v3")),
    ("Hilltop Topographic Park", ("hilltop-cypress-terraces-v0", "hilltop-urban-switchback-v1", "hilltop-rocky-folly-v2")),
    ("Estate Picnic Grove", ("estate-pine-creek-v0", "estate-meadow-pavilion-v2", "estate-regional-picnic-v3")),
    ("Reservoir Watershed Park", ("reservoir-stone-bank-v1", "reservoir-forested-upland-v2", "reservoir-earthen-dam-v3")),
)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    source = image.convert("RGB")
    scale = max(size[0] / source.width, size[1] / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left, top = (resized.width - size[0]) // 2, (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))["archetypes"]
    card_w, card_h, gap, margin = 510, 430, 18, 24
    header_h, group_h = 110, 42
    sheet = Image.new("RGB", (margin * 2 + card_w * 3 + gap * 2, header_h + margin + len(GROUPS) * (group_h + card_h + gap)), "#f2eee5")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 20), "PARK LEGO BATCH 25 · ARCHETYPE REFERENCE → MATERIAL FAMILY", fill="#27332c", font=font(26, True))
    draw.text((margin, 57), "30 exact landscape-system skins · parcel-aware depth kits · no people · no large buildings · no AI draping", fill="#59665e", font=font(18))
    y = header_h
    for group_name, slugs in GROUPS:
        draw.text((margin, y + 7), group_name.upper(), fill="#3f5948", font=font(19, True)); y += group_h
        for column, slug in enumerate(slugs):
            x = margin + column * (card_w + gap)
            draw.rounded_rectangle((x, y, x + card_w, y + card_h), 14, fill="#fffdf8", outline="#c9c2b5", width=2)
            sheet.paste(cover(Image.open(REPO_ROOT / schedule[slug]["source"]), (card_w - 24, 245)), (x + 12, y + 12))
            draw.rectangle((x + 12, y + 220, x + card_w - 12, y + 257), fill="#1d2521")
            draw.text((x + 22, y + 228), slug, fill="white", font=font(15, True))
            for role_index, role in enumerate(ROLES):
                swatch = cover(Image.open(REPO_ROOT / "frontend/public/park-skins" / slug / "adaptive-v1" / role / "albedo.jpg"), (70, 70))
                swatch_x = x + 12 + role_index * 81
                sheet.paste(swatch, (swatch_x, y + 276))
                draw.text((swatch_x, y + 352), role[:5].upper(), fill="#566159", font=font(11, True))
            draw.text((x + 12, y + 395), "Reference statistics + role-specific procedural structure", fill="#6b736d", font=font(13))
        y += card_h + gap
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=91, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
