"""Prepare source-faithful, scale-safe stickers for the V97 LEGO mill pilot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


OUT = Path(__file__).resolve().parent / "sticker_assets/functional_mill_v97"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entrance_square(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        edge = min(rgb.size)
        left = (rgb.width - edge) // 2
        top = (rgb.height - edge) // 2
        # Crop only: never non-uniformly resize a sticker to fit its carrier.
        rgb.crop((left, top, left + edge, top + edge)).save(target)


def _brick_return(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        # A masonry pier field between openings; tile it for tunnel, chimney,
        # soffit and other construction returns which must never expose clay.
        crop = rgb.crop((235, 515, 315, 675)).resize((256, 512), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (1024, 1024))
        for x in range(0, 1024, 256):
            for y in range(0, 1024, 512):
                canvas.paste(crop, (x, y))
        canvas.filter(ImageFilter.GaussianBlur(0.35)).save(target)


def _slate_roof(target: Path) -> None:
    image = Image.new("RGB", (1024, 1024), "#4b4c4c")
    draw = ImageDraw.Draw(image)
    course = 48
    for row, y in enumerate(range(0, 1024, course)):
        offset = 36 if row % 2 else 0
        tone = 67 + (row % 4) * 3
        draw.rectangle((0, y, 1024, min(1024, y + course)), fill=(tone, tone + 1, tone + 2))
        draw.line((0, y, 1024, y), fill="#2e3031", width=2)
        for x in range(-offset, 1024, 72):
            draw.line((x, y, x, min(1024, y + course)), fill="#383a3b", width=2)
    image.filter(ImageFilter.GaussianBlur(0.45)).save(target)


def _timber_service(target: Path) -> None:
    image = Image.new("RGB", (1024, 1024), "#716653")
    draw = ImageDraw.Draw(image)
    for x in range(0, 1024, 42):
        tone = 92 + (x // 42 % 5) * 5
        draw.rectangle((x, 0, min(1024, x + 39), 1024), fill=(tone + 10, tone + 4, tone - 7))
        draw.line((x, 0, x, 1024), fill="#3f3a31", width=3)
        draw.line((min(1023, x + 38), 0, min(1023, x + 38), 1024), fill="#8a7d66", width=2)
    image.filter(ImageFilter.GaussianBlur(0.35)).save(target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ordinary = OUT / "ordinary_five_bay_intrinsic.png"
    entrance = OUT / "entrance_bay_intrinsic.png"
    if not ordinary.is_file() or not entrance.is_file():
        raise FileNotFoundError("generated V97 master stickers are missing")
    _entrance_square(entrance, OUT / "entrance_bay_square.png")
    _brick_return(ordinary, OUT / "brick_return_intrinsic.png")
    _slate_roof(OUT / "slate_roof_intrinsic.png")
    _timber_service(OUT / "timber_service_intrinsic.png")
    with Image.open(ordinary) as image:
        if image.width != image.height:
            raise ValueError("five-bay/five-floor master must be square at 5 m x 5 m cells")
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "functionalist-brick-industrial--brick-multistory-mill",
        "method": "V97 rectified 5x5 cell master plus crop-only fixed entrance",
        "ordinary_sha256": _hash(ordinary),
        "entrance_sha256": _hash(entrance),
        "bay_module_m": 5.0,
        "floor_module_m": 5.0,
        "source_grid": [5, 5],
        "post_generation_nonuniform_scale_allowed": False,
        "approval_space": "rendered_on_all_three_locked_carriers",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "files": 7}, indent=2))


if __name__ == "__main__":
    main()
