"""Render a mobile-friendly source-to-skin review sheet for Batch 23."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from compile_neighborhood_park_skins import REPO_ROOT

SCHEDULE = Path(__file__).with_name("park_archetype_batch23_skin_sources.json")
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")
GROUPS = (
    ("Community garden", ("community-garden-classic-allotment-v0", "community-garden-permaculture-farm-v1", "community-garden-intercultural-social-v3")),
    ("Paris place", ("paris-place-quiet-cobble-v0", "paris-place-statue-axis-v1", "paris-place-cafe-paved-v3")),
    ("Paris square", ("paris-square-linear-edge-v0", "paris-square-corner-cafe-v1", "paris-square-compact-cobble-v2")),
    ("Paris jardin", ("paris-jardin-clipped-parterre-v0", "paris-jardin-rill-garden-v2", "paris-jardin-paved-forecourt-v3")),
    ("Amsterdam Vondelpark", ("amsterdam-vondelpark-neighbourhood-edge-v0", "amsterdam-vondelpark-cafe-edge-v1", "amsterdam-vondelpark-planted-corner-v2")),
    ("Amsterdam hofje", ("amsterdam-hofje-lush-communal-v1", "amsterdam-hofje-pocket-garden-v2", "amsterdam-hofje-historic-lawn-v3")),
    ("Amsterdam plein", ("amsterdam-plein-glass-canopy-v1", "amsterdam-plein-cafe-threshold-v2", "amsterdam-plein-open-brick-v3")),
    ("Barcelona pati", ("barcelona-pati-lawn-court-v1", "barcelona-pati-social-paved-v2", "barcelona-pati-shade-paved-v3")),
    ("Barcelona xamfra", ("barcelona-xamfra-cafe-corner-v0", "barcelona-xamfra-clear-corner-v1", "barcelona-xamfra-active-corner-v3")),
    ("Barcelona superilla", ("barcelona-superilla-plaza-planters-v0", "barcelona-superilla-green-corridor-v2", "barcelona-superilla-social-garden-v3")),
)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/arialbd.ttf") if bold else Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    source = image.convert("RGB")
    scale = max(size[0] / source.width, size[1] / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))["archetypes"]
    card_w, card_h, gap, margin = 510, 430, 18, 24
    header_h, group_h = 110, 42
    width = margin * 2 + card_w * 3 + gap * 2
    height = header_h + margin + len(GROUPS) * (group_h + card_h + gap)
    sheet = Image.new("RGB", (width, height), "#f2eee5")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 20), "PARK LEGO BATCH 23 · ARCHETYPE REFERENCE → MATERIAL FAMILY", fill="#27332c", font=font(26, True))
    draw.text((margin, 57), "30 exact local-reference skins · variant-aware parcel recipes · no people · no embedded large buildings · no AI draping", fill="#59665e", font=font(18))
    y = header_h
    for group_name, slugs in GROUPS:
        draw.text((margin, y + 7), group_name.upper(), fill="#3f5948", font=font(19, True))
        y += group_h
        for column, slug in enumerate(slugs):
            x = margin + column * (card_w + gap)
            draw.rounded_rectangle((x, y, x + card_w, y + card_h), 14, fill="#fffdf8", outline="#c9c2b5", width=2)
            source_path = REPO_ROOT / schedule[slug]["source"]
            reference = cover(Image.open(source_path), (card_w - 24, 245))
            sheet.paste(reference, (x + 12, y + 12))
            draw.rectangle((x + 12, y + 220, x + card_w - 12, y + 257), fill="#1d2521")
            draw.text((x + 22, y + 228), slug, fill="white", font=font(15, True))
            swatch_y = y + 276
            for role_index, role in enumerate(ROLES):
                swatch_path = REPO_ROOT / "frontend/public/park-skins" / slug / "adaptive-v1" / role / "albedo.jpg"
                swatch = cover(Image.open(swatch_path), (70, 70))
                swatch_x = x + 12 + role_index * 81
                sheet.paste(swatch, (swatch_x, swatch_y))
                draw.text((swatch_x, swatch_y + 76), role[:5].upper(), fill="#566159", font=font(11, True))
            draw.text((x + 12, y + 395), "Reference statistics + role-specific procedural structure", fill="#6b736d", font=font(13))
        y += card_h + gap
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=91, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
