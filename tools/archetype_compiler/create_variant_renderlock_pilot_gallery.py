"""Create the review board for the July 2026 render-locked variant pilot."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "build" / "cityprompt-variant-pilot"
SHEET_ROOT = ROOT / "tools" / "archetype_compiler" / "facade_sheets_gpt_variant_pilot_v1"

ROWS = [
    {
        "name": "Contemporary Mid-Rise — Brick + Bronze",
        "status": "KEEPER",
        "status_color": "#397a2b",
        "goal": ROOT / "frontend/public/archetypes/buildings/contemporary_mid_rise_residential/variant_2.png",
        "sheet": SHEET_ROOT / "contemporary-midrise-brick-bronze/elevation_gpt_source.png",
        "family": "contemporary-midrise-brick-bronze-renderlocked-v1",
    },
    {
        "name": "Modern Glass Office — Terracotta Fins",
        "status": "KEEPER",
        "status_color": "#397a2b",
        "goal": ROOT / "frontend/public/archetypes/buildings/modern_glass_office_institutional/variant_1.png",
        "sheet": SHEET_ROOT / "glass-office-terracotta-fins/elevation_gpt_source.png",
        "family": "glass-office-terracotta-fins-renderlocked-v1",
    },
    {
        "name": "Victorian Heritage — Second Empire Mansard",
        "status": "KEEPER",
        "status_color": "#397a2b",
        "goal": ROOT / "frontend/public/archetypes/buildings/victorian_heritage_avenue/variant_3.png",
        "sheet": SHEET_ROOT / "victorian-second-empire/elevation_gpt_source.png",
        "family": "victorian-second-empire-renderlocked-v1",
    },
    {
        "name": "Collegiate Gothic — Perpendicular Chapel",
        "status": "REJECTED: NEEDS FIXED TOWER / NAVE MASSING",
        "status_color": "#a74135",
        "goal": ROOT / "frontend/public/archetypes/buildings/collegiate_gothic_education/variant_2.png",
        "sheet": SHEET_ROOT / "collegiate-gothic-perpendicular/elevation_gpt_source.png",
        "family": "collegiate-gothic-perpendicular-renderlocked-v1",
    },
]

COL_LABELS = ["CATALOGUE GOALPOST", "RECTIFIED GPT ELEVATION", "3D OBLIQUE", "CLOSE STREET", "AERIAL / ROOF"]
WIDTH = 1900
MARGIN = 34
GAP = 14
CELL_W = (WIDTH - MARGIN * 2 - GAP * 4) // 5
CELL_H = 250
ROW_HEADER = 64
TOP = 128
ROW_GAP = 26
HEIGHT = TOP + len(ROWS) * (ROW_HEADER + CELL_H + ROW_GAP) + 34


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def fit(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return ImageOps.fit(image, (CELL_W, CELL_H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def metadata(row: dict) -> str:
    manifest_path = OUT_ROOT / row["family"] / f"{row['family']}_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assembled = payload.get("assembled") or {}
    footprint = assembled.get("footprint_target") or {}
    return (
        f"{footprint.get('width_m', '?')} × {footprint.get('depth_m', '?')} m  ·  "
        f"{assembled.get('height_m', '?')} m high  ·  {assembled.get('triangle_count', 0):,} tris"
    )


def main() -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#f6f2ea")
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 26), "RENDER-LOCKED VARIANT PILOT", fill="#12243a", font=font(30, True))
    draw.text(
        (MARGIN, 68),
        "Catalogue views → shadow-neutral identity atlas → semantic PBR + fixed assemblies → close / aerial comparison",
        fill="#4d5c68",
        font=font(19),
    )
    for index, label in enumerate(COL_LABELS):
        x = MARGIN + index * (CELL_W + GAP)
        draw.text((x + 8, 105), label, fill="#51606d", font=font(14, True))

    y = TOP
    for row in ROWS:
        draw.rounded_rectangle((MARGIN, y, WIDTH - MARGIN, y + ROW_HEADER + CELL_H), 10, fill="#fffdf9", outline="#d2cabc", width=2)
        draw.text((MARGIN + 14, y + 10), row["name"], fill="#12243a", font=font(20, True))
        draw.text((MARGIN + 14, y + 38), metadata(row), fill="#61707c", font=font(14))
        status_font = font(14, True)
        status_width = draw.textbbox((0, 0), row["status"], font=status_font)[2]
        draw.text((WIDTH - MARGIN - status_width - 14, y + 18), row["status"], fill=row["status_color"], font=status_font)

        family_dir = OUT_ROOT / row["family"]
        images = [
            row["goal"],
            row["sheet"],
            family_dir / f"{row['family']}_preview.png",
            family_dir / f"{row['family']}_street.png",
            family_dir / f"{row['family']}_aerial.png",
        ]
        for col, path in enumerate(images):
            x = MARGIN + col * (CELL_W + GAP)
            cell_y = y + ROW_HEADER
            canvas.paste(fit(path), (x, cell_y))
        y += ROW_HEADER + CELL_H + ROW_GAP

    output = OUT_ROOT / "variant-renderlock-pilot-review.png"
    canvas.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
