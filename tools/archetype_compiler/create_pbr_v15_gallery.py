#!/usr/bin/env python3
"""Build a compact archetype/model/PBR comparison board for the v15 pilot."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/Arial.ttf")]
        if bold else
        [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/Arial.ttf")]
    )
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    return ImageFont.truetype(str(path), size) if path else ImageFont.load_default(size=size)


def _fit(path: Path, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), size, Image.Resampling.LANCZOS)


def create(output: Path, repo: Path) -> None:
    canvas = Image.new("RGB", (2200, 1440), "#f3f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, green, border = "#152231", "#39731d", "#c9c2b4"
    draw.text((48, 34), "PARISIAN LEGO PBR v15 — ARCHETYPE TO CITY PROMPT", font=_font(40, True), fill=ink)
    draw.text(
        (48, 88),
        "Fixed entrance/corners/crown/roof · three repeatable middle floors · wrapped side elevations · physical glass",
        font=_font(23), fill="#526170",
    )

    reference = repo / "frontend/public/archetypes/buildings/parisian_midrise_block/variant_0_angle_60.jpg"
    model = repo / "build/codex-lego-pbr-parisian-v15b/codex-lego-pbr-parisian-v15_preview.png"
    panels = [
        (reference, (48, 160, 1050, 820), "ARCHETYPE — OBLIQUE MASSING / MATERIAL GOAL"),
        (model, (1120, 160, 2152, 820), "PBR LEGO ASSEMBLY — 30 × 20 m / 6 FLOORS"),
    ]
    for path, (x0, y0, x1, y1), label in panels:
        canvas.paste(_fit(path, (x1 - x0, y1 - y0)), (x0, y0))
        draw.rectangle((x0, y0, x1, y1), outline=border, width=3)
        draw.rectangle((x0, y0, x0 + 570, y0 + 48), fill=ink)
        draw.text((x0 + 16, y0 + 11), label, font=_font(18, True), fill="white")

    pbr_root = repo / "tools/archetype_compiler/facade_sheets_pbr_v15/parisian-midrise-block/near"
    maps = [
        (pbr_root / "floor_albedo.png", "SHADOW-NEUTRAL ALBEDO"),
        (pbr_root / "floor_normal.png", "NORMAL"),
        (pbr_root / "floor_roughness.png", "ROUGHNESS"),
        (pbr_root / "floor_emissive.png", "ALWAYS-OCCUPIED EMISSIVE"),
    ]
    tile_w, tile_h, gap, y = 510, 360, 24, 900
    for index, (path, label) in enumerate(maps):
        x = 48 + index * (tile_w + gap)
        canvas.paste(_fit(path, (tile_w, tile_h)), (x, y))
        draw.rectangle((x, y, x + tile_w, y + tile_h), outline=border, width=3)
        draw.rectangle((x, y, x + tile_w, y + 42), fill="#ffffff")
        draw.text((x + 13, y + 10), label, font=_font(17, True), fill=ink)

    draw.rounded_rectangle((48, 1300, 2152, 1388), radius=18, fill="#e5eddf", outline="#aac39a", width=2)
    draw.text(
        (70, 1320),
        "CITY PROMPT READY  ·  source masters: 2K PNG PBR  ·  delivery: KTX2/UASTC  ·  city LOD: 1K baked facade",
        font=_font(24, True), fill=green,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, compress_level=7)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    create(args.output.resolve(), args.repo.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
