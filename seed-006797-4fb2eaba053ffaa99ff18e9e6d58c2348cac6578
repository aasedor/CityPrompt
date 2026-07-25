#!/usr/bin/env python3
"""Create the Kinnaird quality-gate board for the reference-guided v17 pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/Arial.ttf")]
        if bold
        else [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/Arial.ttf")]
    )
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    return ImageFont.truetype(str(path), size) if path else ImageFont.load_default(size=size)


def _fit(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.fit(source.convert("RGB"), size, Image.Resampling.LANCZOS)


def _panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    rect: tuple[int, int, int, int],
    label: str,
    label_color: str,
) -> None:
    x0, y0, x1, y1 = rect
    canvas.paste(_fit(path, (x1 - x0, y1 - y0)), (x0, y0))
    draw.rectangle(rect, outline="#bfb7a9", width=3)
    draw.rectangle((x0, y0, x1, y0 + 48), fill=label_color)
    draw.text((x0 + 15, y0 + 11), label, font=_font(19, True), fill="white")


def create(output: Path, repo: Path, family: str) -> None:
    build = repo / "build" / family
    manifest_path = build / f"{family}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hero_tris = int(manifest["assembled"]["triangle_count"])
    hero_mb = (build / manifest["assembled"]["filename"]).stat().st_size / (1024 * 1024)

    canvas = Image.new("RGB", (2400, 1600), "#f4f1e9")
    draw = ImageDraw.Draw(canvas)
    ink, green, blue = "#142334", "#39751d", "#17687a"
    draw.text((48, 34), "KINNAIRD QUALITY GATE - REFERENCE-GUIDED PARISIAN LEGO v17b", font=_font(41, True), fill=ink)
    draw.text(
        (48, 91),
        "Bespoke-model material richness translated into a resizable City Prompt assembly",
        font=_font(24),
        fill="#526170",
    )

    _panel(
        canvas,
        draw,
        repo / "build/lego-kinnaird-v6/reference/kinnaird-house.jpg",
        (48, 156, 790, 748),
        "KINNAIRD - DETAIL / MATERIAL BENCHMARK",
        ink,
    )
    _panel(
        canvas,
        draw,
        repo / "frontend/public/archetypes/buildings/parisian_midrise_block/variant_0_angle_60.jpg",
        (829, 156, 1571, 748),
        "PARISIAN ARCHETYPE - SHAPE / STYLE TARGET",
        ink,
    )
    _panel(
        canvas,
        draw,
        build / f"{family}_preview.png",
        (1610, 156, 2352, 748),
        "v17b HERO - MODULAR PHYSICAL ASSEMBLY",
        green,
    )

    _panel(
        canvas,
        draw,
        repo / "build/lego-archetype-comparisons-v6/parisian/parisian-midrise-block_preview.png",
        (48, 824, 790, 1354),
        "v6 BASELINE - PROCEDURAL / FLAT / REPETITIVE",
        "#64717d",
    )
    _panel(
        canvas,
        draw,
        build / f"{family}_street.png",
        (829, 824, 1571, 1354),
        "v17b STREET - RECESSES / CORNICES / VARIANT BAYS",
        green,
    )

    pbr = repo / "tools/archetype_compiler/facade_sheets_pbr_v16/parisian-midrise-block/near"
    maps = [
        (pbr / "floor_albedo.png", "4K ALBEDO"),
        (pbr / "floor_normal.png", "NORMAL"),
        (pbr / "floor_emissive.png", "EMISSIVE"),
    ]
    tile_w, tile_h, gap = 235, 530, 19
    for index, (path, label) in enumerate(maps):
        x0 = 1610 + index * (tile_w + gap)
        _panel(canvas, draw, path, (x0, 824, x0 + tile_w, 1354), label, blue)

    draw.rounded_rectangle((48, 1414, 2352, 1546), radius=18, fill="#e4eddf", outline="#a8c29b", width=2)
    draw.text(
        (72, 1437),
        f"HERO: {hero_tris:,} tris / {hero_mb:.1f} MB  |  4K registered PBR  |  physical glazing on four elevations",
        font=_font(25, True),
        fill=green,
    )
    draw.text(
        (72, 1482),
        "Fixed entrance + corners + crown + roof  |  only three middle bay variants repeat  |  separate 1K/KTX2 city LOD",
        font=_font(23),
        fill=ink,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, compress_level=7)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--family", default="codex-lego-kinnaird-quality-v17b")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    create(args.output.resolve(), args.repo.resolve(), args.family)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
