"""Create the three-family parametric facade-relief pilot review board."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROOT = REPO_ROOT / "build" / "parametric-relief-v13"
SHEET_ROOT = REPO_ROOT / "tools" / "archetype_compiler" / "facade_sheets_v8"
OUTPUT = BUILD_ROOT / "parametric-relief-v13-board.png"

FAMILIES = (
    {
        "title": "Nordic Timber Mid-Rise",
        "archetype": "nordic_timber_midrise",
        "family": "nordic-timber-midrise",
        "close": "nordic-timber-midrise_archetype_match.png",
        "size_test": "nordic-timber-midrise-28x20x7",
        "depth": "timber frames + deep loggias + balcony guards + roof pavilion",
    },
    {
        "title": "Modern Glass Office / Institutional",
        "archetype": "modern_glass_office_institutional",
        "family": "modern-glass-office-institutional",
        "close": "modern-glass-office-institutional_archetype_match.png",
        "size_test": "modern-glass-office-institutional-42x26x16",
        "depth": "recessed panes + alternating fins + slab bands + entrance canopy",
    },
    {
        "title": "Parisian Mid-Rise",
        "archetype": "parisian_midrise_block",
        "family": "parisian-midrise-block",
        "close": "parisian-midrise-block_preview.png",
        "size_test": "parisian-midrise-block-42x24x8",
        "depth": "window surrounds + sills + balconies + cornice + mansard dormers",
    },
)


def font(size: int, *, bold: bool = False):
    candidate = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def card(path: Path, label: str, colour: str, size: tuple[int, int], *, centering=(0.5, 0.5)) -> Image.Image:
    header = 46
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - header), Image.Resampling.LANCZOS, centering=centering)
    result = Image.new("RGB", size, "#eeeae2")
    result.paste(image, (0, header))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], header), fill=colour)
    draw.text((14, 12), label, font=font(17, bold=True), fill="white")
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    canvas = Image.new("RGB", (2160, 1900), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((42, 26), "Parametric facade relief — three LEGO pilots", font=font(42, bold=True), fill="#132333")
    draw.text(
        (44, 82),
        "Archetype goalpost → Gemini facade → multi-depth 3D construction → City Prompt context",
        font=font(22), fill="#536472",
    )

    panel_size = (490, 392)
    x_positions = (42, 562, 1082, 1602)
    for row, item in enumerate(FAMILIES):
        family = item["family"]
        family_root = BUILD_ROOT / family
        manifest = read_json(family_root / f"{family}_manifest.json")
        assembled = manifest["assembled"]
        glb = family_root / assembled["filename"]
        size_root = BUILD_ROOT / "size-tests" / item["size_test"]
        size_grammar = read_json(size_root / "grammar.json")
        size_manifest = read_json(size_root / f"{family}_manifest.json")
        size_assembled = size_manifest["assembled"]
        dimensions = size_grammar["dimensions"]
        y = 130 + row * 560

        draw.text((42, y), item["title"], font=font(29, bold=True), fill="#132333")
        draw.text(
            (42, y + 38),
            f"{item['depth']}  |  default: {assembled['triangle_count']:,} tris / {glb.stat().st_size / 1048576:.1f} MB",
            font=font(17), fill="#61717d",
        )
        draw.text(
            (42, y + 64),
            f"resize proof: {dimensions['width_m']:.0f} × {dimensions['depth_m']:.0f} m / "
            f"{size_assembled['floors']} floors / validation pass / six reusable modules",
            font=font(17, bold=True), fill="#3f6d27",
        )

        paths = (
            REPO_ROOT / "frontend" / "public" / "archetypes" / "buildings" / item["archetype"] / "variant_0.png",
            SHEET_ROOT / family / "elevation_raw.jpg",
            family_root / item["close"],
            family_root / f"{family}_context.png",
        )
        labels = (
            ("ARCHETYPE GOALPOST", "#142536", (0.5, 0.5)),
            ("GEMINI FACADE SHEET", "#69522f", (0.5, 0.48)),
            ("3D RELIEF ASSEMBLY", "#347711", (0.5, 0.52)),
            ("CITY-SCALE CONTEXT", "#23677a", (0.5, 0.5)),
        )
        for x, path, (label, colour, centering) in zip(x_positions, paths, labels):
            if not path.exists():
                raise SystemExit(f"missing gallery input: {path}")
            canvas.paste(card(path, label, colour, panel_size, centering=centering), (x, y + 94))

    footer = 1814
    draw.rounded_rectangle((42, footer, 2118, 1870), radius=12, fill="#e3eadf", outline="#bac8b5", width=2)
    draw.text(
        (62, footer + 17),
        "Depth is bay- and floor-relative: resizing adds modules and bays; it does not stretch a fixed hero mesh.",
        font=font(20, bold=True), fill="#2d4e25",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
