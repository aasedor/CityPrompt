"""Build a mobile-friendly archetype-to-model comparison sheet for batch 2."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPOSITORY_ROOT / "docs/park-depth-kit-batch2/batch2_archetype_comparison.png"
ROWS = [
    (
        "Inclusive playground · v0",
        REPOSITORY_ROOT / "frontend/public/archetypes/openspaces/inclusive-accessible-playground/variant_0.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/inclusive_playground_overview.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/inclusive_playground_top.png",
    ),
    (
        "Community garden · v0",
        REPOSITORY_ROOT / "frontend/public/archetypes/openspaces/community-garden-allotments/variant_0.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/community_garden_overview.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/community_garden_top.png",
    ),
    (
        "Splash pad · v1",
        REPOSITORY_ROOT / "frontend/public/archetypes/openspaces/splash-pad-water-play/variant_1.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/splash_pad_area_overview.png",
        REPOSITORY_ROOT / "docs/park-depth-kit-batch2/splash_pad_area_top.png",
    ),
]


def font(size: int, *, bold: bool = False):
    filename = "arialbd.ttf" if bold else "arial.ttf"
    windows_font = Path("C:/Windows/Fonts") / filename
    if windows_font.is_file():
        return ImageFont.truetype(str(windows_font), size)
    return ImageFont.load_default()


def paste_contained(canvas: Image.Image, path: Path, box: tuple[int, int, int, int]) -> None:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        fitted = ImageOps.contain(image, (box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
        x = box[0] + (box[2] - box[0] - fitted.width) // 2
        y = box[1] + (box[3] - box[1] - fitted.height) // 2
        canvas.paste(fitted, (x, y))


def main() -> None:
    width = 2400
    header_height = 170
    column_header_height = 76
    row_height = 690
    margin = 36
    gutter = 24
    label_height = 62
    column_width = (width - margin * 2 - gutter * 2) // 3
    height = header_height + column_header_height + row_height * len(ROWS) + margin
    canvas = Image.new("RGB", (width, height), "#111820")
    draw = ImageDraw.Draw(canvas)

    draw.text((margin, 32), "Park depth kits · archetype comparison", fill="#F2F5F7", font=font(54, bold=True))
    draw.text(
        (margin, 100),
        "AI drape supplies the ground surface; staged GLBs supply the raised program elements.",
        fill="#A9B7C2",
        font=font(28),
    )

    headers = ("Catalogue archetype", "3D depth-kit overview", "Top / mask-fit view")
    header_y = header_height
    for column, label in enumerate(headers):
        x = margin + column * (column_width + gutter)
        draw.rounded_rectangle((x, header_y, x + column_width, header_y + 54), radius=12, fill="#23313D")
        draw.text((x + 20, header_y + 10), label, fill="#DDE6EC", font=font(27, bold=True))

    for row_index, (title, reference, overview, top) in enumerate(ROWS):
        row_y = header_height + column_header_height + row_index * row_height
        draw.text((margin, row_y + 4), title, fill="#F4C46A", font=font(34, bold=True))
        image_y = row_y + label_height
        for column, path in enumerate((reference, overview, top)):
            x = margin + column * (column_width + gutter)
            box = (x, image_y, x + column_width, image_y + row_height - label_height - 22)
            draw.rounded_rectangle(box, radius=16, fill="#1C2630", outline="#3B4C59", width=3)
            inner = (box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12)
            paste_contained(canvas, path, inner)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, format="PNG", optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
