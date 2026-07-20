"""Create one review board for the physical-glazing / baked-facade LOD pilot."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROOT = REPO_ROOT / "build/glass-lod-v11"
SHEET_ROOT = REPO_ROOT / "tools/archetype_compiler/facade_sheets_v8"
OUTPUT = BUILD_ROOT / "glass-lod-pilot-board.png"

FAMILIES = (
    ("Modern Glass Office", "modern_glass_office_institutional", "modern-glass-office-institutional", "reflective_curtain_wall"),
    ("Industrial Brick Loft", "industrial_brick_mixed_use", "industrial-brick-mixed-use", "industrial_sash"),
    ("Nordic Timber Residential", "nordic_timber_midrise", "nordic-timber-midrise", "residential_low_e"),
)


def font(size: int, bold: bool = False):
    candidate = Path(f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def card(path: Path, label: str, colour: str, size: tuple[int, int], *, centering=(0.5, 0.5)) -> Image.Image:
    header = 48
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - header), Image.Resampling.LANCZOS, centering=centering)
    result = Image.new("RGB", size, "#eeeae2")
    result.paste(image, (0, header))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], header), fill=colour)
    draw.text((14, 13), label, font=font(18, True), fill="white")
    return result


def main() -> None:
    canvas = Image.new("RGB", (2160, 1900), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((42, 28), "Archetype-matched LEGO v11", font=font(42, True), fill="#132333")
    draw.text(
        (44, 82),
        "Archetype intent → rectified facade → close physical glazing → city-scale assembled context",
        font=font(22), fill="#536472",
    )
    panel_size = (490, 405)
    x_positions = (42, 562, 1082, 1602)

    for row, (title, archetype_id, family, profile) in enumerate(FAMILIES):
        y = 132 + row * 560
        manifest = json.loads((SHEET_ROOT / family / "manifest.json").read_text(encoding="utf-8"))
        model_manifest = json.loads(
            (BUILD_ROOT / family / f"{family}_manifest.json").read_text(encoding="utf-8")
        )
        semantic = manifest.get("semantic_glass") or {}
        coverage = float(semantic.get("coverage", 0.0))
        source = str(semantic.get("source", "unknown"))
        assembled = model_manifest.get("assembled") or {}
        triangles = int(assembled.get("triangle_count", 0))
        assembled_path = BUILD_ROOT / family / str(assembled.get("filename", ""))
        size_mb = assembled_path.stat().st_size / (1024 * 1024)
        draw.text((42, y), title, font=font(28, True), fill="#132333")
        draw.text(
            (42, y + 36),
            f"profile: {profile}   mask: {source}   glass: {coverage:.1%}   "
            f"{triangles:,} tris   {size_mb:.2f} MB",
            font=font(17), fill="#61717d",
        )
        paths = (
            REPO_ROOT / f"frontend/public/archetypes/buildings/{archetype_id}/variant_0.png",
            SHEET_ROOT / family / "elevation_raw.jpg",
            BUILD_ROOT / family / f"{family}_archetype_match.png",
            BUILD_ROOT / family / f"{family}_context.png",
        )
        labels = (
            ("ARCHETYPE", "#142536", (0.5, 0.5)),
            ("RECTIFIED GEMINI FACADE", "#69522f", (0.5, 0.48)),
            ("NEAR: PHYSICAL GLASS", "#347711", (0.5, 0.48)),
            ("CITY-SCALE CONTEXT", "#23677a", (0.5, 0.5)),
        )
        for x, path, (label, colour, centering) in zip(x_positions, paths, labels):
            if not path.exists():
                raise SystemExit(f"missing gallery input: {path}")
            canvas.paste(card(path, label, colour, panel_size, centering=centering), (x, y + 72))

    footer = 1818
    draw.rounded_rectangle((42, footer, 2118, 1870), radius=12, fill="#e3eadf", outline="#bac8b5", width=2)
    draw.text(
        (62, footer + 15),
        "Exact archetype card + softened semantic massing + physical near glass <180 m + baked city facade >230 m.",
        font=font(19, True), fill="#2d4e25",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
