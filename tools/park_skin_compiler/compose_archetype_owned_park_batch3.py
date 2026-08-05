"""Compose per-park and mobile comparison sheets for park LEGO batch 3."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PARKS = (
    (
        "Pickleball / Community Eight-Court Bank",
        "pickleball-courts",
        "variant_1.png",
        "pickleball-community-bank",
        "Two banks of four courts with a shaded social spine",
    ),
    (
        "Running Track / School Athletic Oval",
        "running-track-athletic-oval",
        "variant_2.png",
        "track-oval-school-athletic",
        "Eight lanes, regulation soccer infield, field events, and spectator edge",
    ),
    (
        "Baseball / Youth League Pinwheel",
        "baseball-softball-diamond",
        "variant_1.png",
        "baseball-youth-pinwheel",
        "Four outward-facing youth diamonds around one shared operations hub",
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
LABELS = ("ARCHETYPE", "LEGO OBLIQUE", "LEGO 60 DEG", "LEGO NADIR")


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
    images = [Image.open(source)] + [Image.open(render_dir / view) for view in VIEWS]
    for index, image in enumerate(images):
        x = margin + index * (cell_w + gap)
        sheet.paste(panel(image, (cell_w, cell_h)), (x, y))
        label_w = len(LABELS[index]) * 9 + 24
        draw.rounded_rectangle((x + 10, y + 10, x + 10 + label_w, y + 42), radius=8, fill="#17231f")
        draw.text((x + 20, y + 15), LABELS[index], font=font(14, True), fill="white")
    return y + cell_h


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    width, margin, gap = 1600, 34, 14
    cell_w, cell_h = 372, 280
    title_h, row_h, row_gap = 118, 62 + cell_h, 30
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
    draw.text((margin, 67), "Archetype reference -> LEGO oblique -> 60 degree -> near-nadir", font=font(20), fill="#52615b")
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
