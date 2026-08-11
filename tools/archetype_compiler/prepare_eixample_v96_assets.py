"""Prepare intrinsic Sticker Method assets for the Eixample V96 transfer pilot.

The source elevation was produced and approved during the local V24 render-lock
work.  This script removes the white isolation field, normalizes the exact
carrier aspect, and writes only shadow-neutral surface masters.  The generated
files are committed, so later builds do not depend on the local artifact cache.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/eixample_v96"
ARTIFACT = Path(r"C:\dev-artifacts\3D-Maps\families\eixample-classic-v1")


def _occupied_crop(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    white = Image.new("RGB", rgb.size, "white")
    difference = ImageChops.difference(rgb, white).convert("L")
    difference = difference.point(lambda value: 255 if value > 14 else 0)
    bounds = difference.getbbox()
    if not bounds:
        raise ValueError("source elevation contains no occupied pixels")
    left, top, right, bottom = bounds
    # Keep a small amount of the real masonry edge, but never isolation white.
    inset = max(2, round((right - left) * 0.004))
    return rgb.crop((left + inset, top + inset, right - inset, bottom - inset))


def _save_square(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        occupied = _occupied_crop(image)
        occupied = ImageEnhance.Contrast(occupied).enhance(0.96)
        occupied = ImageEnhance.Color(occupied).enhance(0.94)
        occupied.resize((2048, 2048), Image.Resampling.LANCZOS).save(target)


def _roof_intrinsic(target: Path) -> None:
    size = 1024
    image = Image.new("RGB", (size, size), "#918f87")
    draw = ImageDraw.Draw(image)
    for y in range(0, size, 96):
        tone = 137 + ((y // 96) % 3) * 3
        draw.rectangle((0, y, size, min(size, y + 95)), fill=(tone + 5, tone + 4, tone))
        draw.line((0, y, size, y), fill="#74746f", width=2)
    for x in range(0, size, 128):
        draw.line((x, 0, x, size), fill="#7d7c76", width=2)
    for index in range(14):
        x = (index * 173 + 47) % size
        y = (index * 97 + 83) % size
        draw.line((x - 30, y, x + 40, y + 8), fill="#85837c", width=5)
    image.filter(ImageFilter.GaussianBlur(1.2)).save(target)


def _terracotta_cap(target: Path) -> None:
    image = Image.new("RGB", (512, 512), "#a55f3c")
    draw = ImageDraw.Draw(image)
    for y in range(0, 512, 64):
        draw.line((0, y, 512, y), fill="#72442f", width=3)
    for x in range(0, 512, 96):
        draw.line((x, 0, x, 512), fill="#8b5035", width=2)
    image.filter(ImageFilter.GaussianBlur(0.8)).save(target)


def _courtyard_floor(target: Path) -> None:
    image = Image.new("RGB", (1024, 1024), "#69675f")
    draw = ImageDraw.Draw(image)
    for y in range(0, 1024, 42):
        for x in range(0, 1024, 42):
            tone = 92 + ((x // 42 + y // 42) % 5) * 3
            draw.rectangle((x, y, x + 40, y + 40), fill=(tone + 4, tone + 3, tone))
    image.filter(ImageFilter.GaussianBlur(0.7)).save(target)


def _ordinary_elevation(principal: Path, target: Path) -> None:
    """Build a portal-free, repeatable ordinary-bay master.

    The hero entrance belongs only to the broad street chamfer.  Repeating its
    full elevation on every side and court face creates painted false doors.
    This master repeats a clean left-hand residential/shop bay strip while
    retaining the approved colour, window, shutter and balcony language.
    """
    with Image.open(principal) as image:
        rgb = image.convert("RGB")
        # One complete ordinary bay, bounded by stone piers on both sides.
        strip = rgb.crop((90, 0, 545, rgb.height)).resize(
            (rgb.width // 4, rgb.height), Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGB", rgb.size)
        x = 0
        while x < canvas.width:
            width = min(strip.width, canvas.width - x)
            canvas.paste(strip.crop((0, 0, width, strip.height)), (x, 0))
            x += strip.width
        canvas.save(target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    primary = ARTIFACT / "facade-source/imagegen-elevation-source.png"
    side = ARTIFACT / "facade-pbr-v1/near/side_albedo.png"
    if not primary.is_file():
        primary = REPO / "tools/archetype_compiler/facade_sheets_v8/eixample-apartment-block/elevation_raw.jpg"
    if not side.is_file():
        side = primary
    principal = OUT / "principal_elevation_intrinsic.png"
    _save_square(primary, principal)
    _ordinary_elevation(principal, OUT / "ordinary_elevation_intrinsic.png")
    _save_square(side, OUT / "secondary_elevation_intrinsic.png")
    _roof_intrinsic(OUT / "terrace_roof_intrinsic.png")
    _terracotta_cap(OUT / "terracotta_cap_intrinsic.png")
    _courtyard_floor(OUT / "courtyard_floor_intrinsic.png")
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "eixample-apartment-block-classic",
        "method": "occupied-crop, de-isolation, restrained intrinsic normalization",
        "principal_source": str(primary),
        "secondary_source": str(side),
        "post_generation_nonuniform_scale_allowed": False,
        "ordinary_source_rule": "portal-free approved-bay repeat; hero portal is unique",
        "approval_space": "rendered_on_locked_carrier",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "files": 7}, indent=2))


if __name__ == "__main__":
    main()
