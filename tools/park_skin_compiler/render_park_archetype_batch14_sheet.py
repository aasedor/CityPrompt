"""Render the mobile-friendly Batch 14 reference/skin comparison sheet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = Path(__file__).with_name("park_archetype_batch14_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "docs/park_lego_batch14/park_lego_batch14_reference_skin_sheet.jpg"
ROLE_COLORS = {"paver": "#d9cfbc", "lawn": "#78935f", "asphalt": "#555754", "planting": "#57704c", "safety": "#b78355", "timber": "#8a6646"}


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skin-root", type=Path, default=REPO_ROOT / "frontend/public/park-skins")
    args = parser.parse_args()
    items = list(json.loads(SCHEDULE.read_text(encoding="utf-8"))["archetypes"].items())
    width, row_height = 1500, 245
    canvas = Image.new("RGB", (width, 110 + row_height * len(items)), "#eee9df")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, width, 90), fill="#252b29")
    draw.text((34, 24), "PARK LEGO BATCH 14 - EXACT REFERENCE + ADAPTIVE 3D FAMILY", fill="white", font=font)
    draw.text((34, 50), "10 parking, transport and field parents - no people/large buildings - zero API calls", fill="#c8d7c6", font=font)
    roles = ["paver", "lawn", "asphalt", "planting", "safety", "timber"]
    for index, (slug, item) in enumerate(items):
        top = 100 + index * row_height
        draw.rectangle((20, top, width - 20, top + row_height - 10), fill="#f8f5ee", outline="#c8c1b5", width=2)
        reference_path = REPO_ROOT / item["source"]
        reference = cover(Image.open(reference_path).convert("RGB"), (420, 190))
        canvas.paste(reference, (50, top + 24))
        draw.text((50, top + 7), slug, fill="#28302d", font=font)
        for role_index, role in enumerate(roles):
            left = 495 + role_index * 158
            image_path = args.skin_root / slug / "adaptive-v1" / role / "albedo.jpg"
            swatch = cover(Image.open(image_path).convert("RGB"), (142, 142)) if image_path.exists() else Image.new("RGB", (142, 142), ROLE_COLORS[role])
            canvas.paste(swatch, (left, top + 40))
            draw.text((left, top + 190), role.upper(), fill="#4a514d", font=font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, quality=90, optimize=True)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
