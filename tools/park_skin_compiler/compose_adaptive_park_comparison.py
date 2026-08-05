"""Compose the adaptive, non-photographic park pilot comparison sheet."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
ROOT = REPO_ROOT / "artifacts/neighborhood-park-adaptive-urban-v1"
SOURCE = REPO_ROOT / "frontend/public/archetypes/openspaces/neighborhood-park/variant_3_angle_90.jpg"
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")


def font(size: int, bold: bool = False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(image: Image.Image, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=centering)


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    source = image.convert("RGB")
    source.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#eceae4")
    result.paste(source, ((size[0] - source.width) // 2, (size[1] - source.height) // 2))
    return result


def rounded_paste(sheet: Image.Image, image: Image.Image, position, radius: int = 14) -> None:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    sheet.paste(image, position, mask)


def main() -> None:
    width, height, gap = 2000, 1490, 20
    sheet = Image.new("RGB", (width, height), "#f3f1ec")
    draw = ImageDraw.Draw(sheet)
    draw.text((28, 24), "ADAPTIVE PARK PILOT — NO STRETCHED PHOTOGRAPH", font=font(35, True), fill="#15251f")
    draw.text((28, 73), "The reference calibrates a reusable material kit; a metric grammar generates each parcel-specific layout.", font=font(20), fill="#46574f")
    draw.text((28, 108), "Reference statistics → stationary PBR materials → semantic program → clipped metric geometry", font=font(18, True), fill="#795431")

    top_y, top_h = 155, 330
    reference = fit(Image.open(SOURCE), (560, top_h), centering=(0.5, 0.48))
    rounded_paste(sheet, reference, (28, top_y))
    draw.rounded_rectangle((44, top_y + top_h - 44, 238, top_y + top_h - 10), radius=9, fill="#14241edb")
    draw.text((57, top_y + top_h - 37), "STYLE REFERENCE ONLY", font=font(14, True), fill="white")

    swatch_x = 608
    draw.text((swatch_x, top_y), "REFERENCE-DERIVED MATERIAL KIT", font=font(16, True), fill="#51615a")
    swatch_w, swatch_h = 205, 126
    for index, role in enumerate(ROLES):
        row, column = divmod(index, 3)
        x = swatch_x + column * (swatch_w + 12)
        y = top_y + 34 + row * (swatch_h + 10)
        swatch = fit(Image.open(ROOT / "materials" / role / "albedo.jpg"), (swatch_w, swatch_h))
        rounded_paste(sheet, swatch, (x, y), 10)
        draw.rounded_rectangle((x + 7, y + swatch_h - 28, x + 112, y + swatch_h - 6), radius=7, fill="#14241edb")
        draw.text((x + 14, y + swatch_h - 25), role.upper(), font=font(11, True), fill="white")

    method_x = 1282
    draw.rounded_rectangle((method_x, top_y, width - 28, top_y + top_h), radius=16, fill="#172820")
    draw.text((method_x + 28, top_y + 26), "WHAT CHANGED", font=font(18, True), fill="#c39162")
    lines = (
        "• no full-park photograph on the mesh",
        "• textures repeat at fixed metre scales",
        "• paths keep metric widths",
        "• rooms clip to the parcel boundary",
        "• tree spacing remains physical",
        "• same kit recomposes for each shape",
        "• zero image/model API calls",
    )
    for index, line in enumerate(lines):
        draw.text((method_x + 28, top_y + 72 + index * 34), line, font=font(17, index == 6), fill="#e7eee9" if index < 6 else "#d4a775")

    layouts = json.loads((ROOT / "layouts/adaptive_layouts.json").read_text(encoding="utf-8"))["layouts"]
    column_w = 634
    section_y = 520
    for index, name in enumerate(("square", "long", "irregular")):
        layout = layouts[name]
        x = 28 + index * (column_w + gap)
        draw.text((x, section_y), f"0{index + 1}  {layout['label'].upper()}", font=font(19, True), fill="#182820")
        draw.text((x, section_y + 29), f"{layout['widthM']:.0f} × {layout['heightM']:.0f} m · {layout['areaM2']:.0f} m²", font=font(15), fill="#59675f")
        plan = contain(Image.open(ROOT / "layouts" / f"{name}_plan.png"), (column_w, 330))
        render = fit(Image.open(ROOT / "renders" / f"{name}.png"), (column_w, 475), centering=(0.5, 0.54))
        rounded_paste(sheet, plan, (x, section_y + 62))
        rounded_paste(sheet, render, (x, section_y + 407))
        draw.rounded_rectangle((x + 12, section_y + 419, x + 166, section_y + 449), radius=8, fill="#14241edb")
        draw.text((x + 23, section_y + 425), "GENERATED 3D", font=font(13, True), fill="white")

    draw.text((28, height - 45), "Pilot gate: approve the adaptive grammar before replacing the full-atlas runtime surface or scaling to the other park skins.", font=font(17, True), fill="#485850")
    output = ROOT / "adaptive-urban-park-shape-matrix.png"
    sheet.save(output, optimize=True)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
