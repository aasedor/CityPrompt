#!/usr/bin/env python3
"""Create the size and geographic-footprint comparison board for LEGO v18."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    path = next((Path("C:/Windows/Fonts") / name for name in names if (Path("C:/Windows/Fonts") / name).exists()), None)
    return ImageFont.truetype(str(path), size) if path else ImageFont.load_default(size=size)


def _fit(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.fit(source.convert("RGB"), size, Image.Resampling.LANCZOS)


def _panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    rect: tuple[int, int, int, int],
    title: str,
    subtitle: str,
) -> None:
    x0, y0, x1, y1 = rect
    canvas.paste(_fit(path, (x1 - x0, y1 - y0)), (x0, y0))
    draw.rectangle(rect, outline="#c8c0b2", width=3)
    draw.rectangle((x0, y0, x1, y0 + 78), fill="#173045")
    draw.text((x0 + 18, y0 + 10), title, font=_font(23, True), fill="white")
    draw.text((x0 + 18, y0 + 43), subtitle, font=_font(18), fill="#d8e4ec")


def _manifest_metrics(build: Path, family: str) -> tuple[int, float]:
    manifest = json.loads((build / f"{family}_manifest.json").read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    return int(assembled["triangle_count"]), (build / assembled["filename"]).stat().st_size / (1024 * 1024)


def create(output: Path, repo: Path) -> None:
    root = repo / "build/codex-lego-geographic-shapes-v18"
    items = [
        ("compact-rectangle", "parisian-v18-compact-rectangle", "COMPACT RECTANGLE", "24 x 16 m  |  5 floors"),
        ("wide-rectangle", "parisian-v18-wide-rectangle", "WIDE RECTANGLE", "42 x 24 m  |  7 floors"),
        ("l-shape", "parisian-v18-l-shape", "L SHAPE", "36 x 28 m  |  6 floors  |  10 m wing"),
        ("u-shape", "parisian-v18-u-shape", "U SHAPE", "40 x 30 m  |  7 floors  |  11 m wings"),
        ("courtyard", "parisian-v18-courtyard", "COURTYARD BLOCK", "40 x 36 m  |  7 floors  |  10 m ring"),
    ]

    canvas = Image.new("RGB", (2400, 1780), "#f5f2eb")
    draw = ImageDraw.Draw(canvas)
    ink, green = "#142334", "#39751d"
    draw.text((48, 32), "PARISIAN LEGO v18 - SIZE + GEOGRAPHIC FOOTPRINT PILOT", font=_font(41, True), fill=ink)
    draw.text(
        (48, 88),
        "One architectural kit, assembled from the user's polygon - not five bespoke rectangular models",
        font=_font(24),
        fill="#526170",
    )

    positions = [
        (48, 150, 800, 770),
        (824, 150, 1576, 770),
        (1600, 150, 2352, 770),
        (48, 800, 800, 1420),
        (824, 800, 1576, 1420),
    ]
    metrics: list[str] = []
    for (folder, family, title, subtitle), rect in zip(items, positions):
        build = root / folder
        tris, size = _manifest_metrics(build, family)
        metrics.append(f"{title.lower()}: {tris:,} tris / {size:.1f} MB")
        _panel(canvas, draw, build / f"{family}_aerial.png", rect, title, subtitle)

    x0, y0, x1, y1 = 1600, 800, 2352, 1420
    draw.rounded_rectangle((x0, y0, x1, y1), radius=18, fill="#e7ede2", outline="#abc09e", width=3)
    draw.text((x0 + 26, y0 + 24), "ARCHETYPE FIT METADATA", font=_font(27, True), fill=green)
    rows = [
        ("RECTANGLE", "24-42 x 16-24 m", "5-7 floors"),
        ("L SHAPE", "32-40 x 24-30 m", "8-12 m wings"),
        ("U SHAPE", "36-42 x 26-32 m", "9-13 m wings"),
        ("COURTYARD", "36-42 x 32-38 m", "9-12 m ring"),
    ]
    y = y0 + 88
    for name, dimensions, note in rows:
        draw.line((x0 + 26, y - 10, x1 - 26, y - 10), fill="#c1cdbb", width=2)
        draw.text((x0 + 26, y + 2), name, font=_font(21, True), fill=ink)
        draw.text((x0 + 232, y + 2), dimensions, font=_font(21), fill=ink)
        draw.text((x0 + 232, y + 36), note, font=_font(18), fill="#526170")
        y += 104
    draw.text((x0 + 26, y + 2), "BEST FACADE RHYTHM", font=_font(20, True), fill=green)
    draw.text((x0 + 26, y + 38), "Width near a 3 m bay multiple", font=_font(20), fill=ink)

    draw.rounded_rectangle((48, 1470, 2352, 1716), radius=18, fill="#ffffff", outline="#c8c0b2", width=2)
    draw.text((72, 1495), "WHAT THE CITY PROMPT PIPELINE NOW DOES", font=_font(25, True), fill=green)
    draw.text((72, 1540), "1  Measure and orient the drawn geographic polygon", font=_font(22), fill=ink)
    draw.text((72, 1580), "2  Detect rectangle / L / U / courtyard from concave corners", font=_font(22), fill=ink)
    draw.text((72, 1620), "3  Place, rotate and scale reusable streetwall segments; keep authored podium, middle bays, crown and roof", font=_font(22), fill=ink)
    draw.text((72, 1660), "4  Warn when the polygon is outside the archetype's preferred architectural envelope", font=_font(22), fill=ink)

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
