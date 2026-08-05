"""Compose per-park and mobile comparison sheets for park LEGO batch 3."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PARKS = (
    (
        "Pickleball / Community Five-Court Hub",
        "pickleball-courts",
        "variant_1.png",
        "pickleball-community-bank",
        "One 2x2 bank plus a separate court, playground, and shaded social edge",
    ),
    (
        "Running Track / School Athletic Oval",
        "running-track-athletic-oval",
        "variant_2.png",
        "track-oval-school-athletic",
        "Eight lanes, regulation soccer infield, field events, and spectator edge",
    ),
    (
        "Baseball / Three-Field Club Hub",
        "baseball-softball-diamond",
        "variant_1.png",
        "baseball-youth-pinwheel",
        "Three youth diamonds around a shared club forecourt, cages, and reserved building pad",
    ),
    (
        "Cricket / Traditional Village Green",
        "cricket-ground",
        "variant_0.png",
        "cricket-village-green",
        "One central wicket, open oval, sight screens, practice nets, and pavilion pad",
    ),
    (
        "Sports Complex / Mixed Tournament Campus",
        "sports-field-complex",
        "variant_0.png",
        "sports-complex-tournament",
        "Two soccer fields and two softball diamonds organized by crossing spines",
    ),
)
VIEWS = ("generated_base.png", "generated_angle_60.png", "generated_angle_90.png")
LABELS = (
    "REFERENCE HERO", "REFERENCE 60 DEG", "REFERENCE NADIR",
    "LEGO OBLIQUE", "LEGO 60 DEG", "LEGO NADIR",
)


def font(size: int, bold: bool = False):
    candidates = (
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    fitted = ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (size[0] + 4, size[1] + 4), "#c5cbc7")
    framed.paste(fitted, (2, 2))
    return framed


def draw_park_row(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    *,
    y: int,
    title: str,
    note: str,
    source: Path,
    render_dir: Path,
    margin: int,
    gap: int,
    cell_w: int,
    cell_h: int,
) -> int:
    draw.text((margin, y), title, font=font(24, True), fill="#24342d")
    draw.text((margin, y + 31), note, font=font(16), fill="#596760")
    y += 62
    source_stem = source.with_suffix("")
    images = [
        Image.open(source),
        Image.open(source_stem.with_name(f"{source_stem.name}_angle_60.jpg")),
        Image.open(source_stem.with_name(f"{source_stem.name}_angle_90.jpg")),
        *[Image.open(render_dir / view) for view in VIEWS],
    ]
    for index, image in enumerate(images):
        column, row = index % 3, index // 3
        x = margin + column * (cell_w + gap)
        image_y = y + row * (cell_h + gap)
        sheet.paste(panel(image, (cell_w, cell_h)), (x, image_y))
        label_w = len(LABELS[index]) * 9 + 24
        draw.rounded_rectangle((x + 10, image_y + 10, x + 10 + label_w, image_y + 42), radius=8, fill="#17231f")
        draw.text((x + 20, image_y + 15), LABELS[index], font=font(14, True), fill="white")
    return y + 2 * cell_h + gap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    width, margin, gap = 1600, 34, 14
    cell_w, cell_h = 500, 300
    title_h, row_h, row_gap = 118, 62 + 2 * cell_h + gap, 30
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for title, source_slug, source_name, render_slug, note in PARKS:
        height = title_h + row_h + 30
        sheet = Image.new("RGB", (width, height), "#f3f2ed")
        draw = ImageDraw.Draw(sheet)
        draw.text((margin, 22), "ARCHETYPE-OWNED PARK LEGO - BATCH 3", font=font(34, True), fill="#1e2c27")
        draw.text((margin, 67), "Reference composition translated into deterministic metric geometry", font=font(20), fill="#52615b")
        source = args.reference_root / "frontend/public/archetypes/openspaces" / source_slug / source_name
        draw_park_row(
            sheet,
            draw,
            y=title_h,
            title=title,
            note=note,
            source=source,
            render_dir=args.render_root / render_slug,
            margin=margin,
            gap=gap,
            cell_w=cell_w,
            cell_h=cell_h,
        )
        output = args.output_dir / f"{render_slug}-comparison.png"
        sheet.save(output, optimize=True)
        print(f"wrote {output}")

    height = title_h + len(PARKS) * (row_h + row_gap) + 24
    sheet = Image.new("RGB", (width, height), "#f3f2ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 22), "ARCHETYPE-OWNED PARK LEGO - BATCH 3", font=font(34, True), fill="#1e2c27")
    draw.text((margin, 67), "Hero + 60 degree + nadir references -> matching LEGO views", font=font(20), fill="#52615b")
    y = title_h
    for title, source_slug, source_name, render_slug, note in PARKS:
        source = args.reference_root / "frontend/public/archetypes/openspaces" / source_slug / source_name
        y = draw_park_row(
            sheet,
            draw,
            y=y,
            title=title,
            note=note,
            source=source,
            render_dir=args.render_root / render_slug,
            margin=margin,
            gap=gap,
            cell_w=cell_w,
            cell_h=cell_h,
        ) + row_gap
    output = args.output_dir / "comparison-mobile.png"
    sheet.save(output, optimize=True)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
