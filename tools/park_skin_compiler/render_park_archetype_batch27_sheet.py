"""Render the mobile-friendly final-catalogue Batch 27 review sheet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from compile_neighborhood_park_skins import REPO_ROOT

SCHEDULE = Path(__file__).with_name("park_archetype_batch27_skin_sources.json")
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")
GROUPS = (
    ("Academic Courtyard", ("academic-corten-hardscape-v1", "academic-glass-canopy-v2", "academic-timber-screen-v3")),
    ("Campus Pedestrian Spine", ("campus-urban-paved-spine-v1", "campus-pavilion-spine-v2", "campus-pergola-spine-v3")),
    ("Constructed Wetland", ("wetland-tidal-treatment-v1", "wetland-wildlife-v2", "wetland-nature-center-v3")),
    ("Research Garden", ("research-greenhouse-garden-v1", "research-teaching-pavilion-v2", "research-demonstration-plots-v3")),
    ("Rewilding & Restoration", ("rewilding-urban-prairie-v0", "rewilding-interpretive-v2", "rewilding-riparian-v3")),
    ("Naturalized Drainage", ("drainage-urban-daylit-v1", "drainage-seasonal-planted-v2", "drainage-stream-shelter-v3")),
    ("Stormwater Resilience", ("stormwater-urban-bioswale-v0", "stormwater-naturalistic-detention-v1", "stormwater-engineered-plaza-v2")),
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
    draw.text((margin, 20), "PARK LEGO BATCH 27 - FINAL CATALOGUE CLOSURE", fill="#27332c", font=font(26, True))
    draw.text((margin, 57), "21 exact skins - 520/520 catalogue variants - no people - no large buildings - no AI draping", fill="#59665e", font=font(18))
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
            draw.text((x + 12, y + 395), "Exact reference statistics + parcel-adaptive LEGO structure", fill="#6b736d", font=font(13))
        y += card_h + gap
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=91, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
