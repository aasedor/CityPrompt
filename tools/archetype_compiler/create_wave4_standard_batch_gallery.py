"""Build phone-safe reference and detail sheets for the Wave 4 batch."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
SHEET_SIZE = (1600, 1420)

FAMILIES = (
    {
        "slug": "brownstone-rowhouse-frontage",
        "title": "BROWNSTONE ROWHOUSE FRONTAGE",
        "identity": "Five red-brick bays, carved sandstone, a real raised stoop and shadowed garden level.",
        "detail": "The tall podium keeps garden level, stoop, landing and dark centre door as one fixed section.",
    },
    {
        "slug": "industrial-brick-mixed-use",
        "title": "INDUSTRIAL BRICK ORIGINAL MILL",
        "identity": "Six structural mill bays, segmental Crittall arches, corbelled eaves and a glazed roof monitor.",
        "detail": "Complete brick bays repeat while gables, chimney, corbelled crown and roof monitor remain fixed.",
    },
    {
        "slug": "contemporary-midrise-residential",
        "title": "CONTEMPORARY BRICK + BRONZE",
        "identity": "A limestone podium and deep central arch support a disciplined wide/narrow residential cadence.",
        "detail": "Physical brick piers, bronze frames and large podium glazing preserve the selected urban frontage.",
    },
    {
        "slug": "scandinavian-urban-residential",
        "title": "SCANDINAVIAN URBAN RESIDENTIAL",
        "identity": "White plaster, three timber balcony stacks, a through-passage and five standing-seam dormers.",
        "detail": "The passage is open through the podium; balconies are one physical slab/return/rail assembly.",
    },
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / filename), size)


def place_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    image_path: Path,
    box: tuple[int, int, int, int],
    label: str,
    accent: str,
    mode: str = "cover",
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=22,
        fill="#f7f6f2",
        outline="#c4c8ca",
        width=2,
    )
    draw.text((x0 + 22, y0 + 18), label, font=font(25, True), fill=accent)
    image_box = (x0 + 16, y0 + 60, x1 - 16, y1 - 16)
    with Image.open(image_path) as source:
        target = (image_box[2] - image_box[0], image_box[3] - image_box[1])
        if mode == "contain":
            image = ImageOps.contain(
                source.convert("RGB"),
                target,
                method=Image.Resampling.LANCZOS,
            )
            position = (
                image_box[0] + (target[0] - image.width) // 2,
                image_box[1] + (target[1] - image.height) // 2,
            )
        else:
            image = ImageOps.fit(
                source.convert("RGB"),
                target,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            position = image_box[:2]
    canvas.paste(image, position)


def build_sheet(spec: dict[str, str], *, detail: bool) -> Path:
    slug = spec["slug"]
    root = FAMILIES_ROOT / slug
    suffix = "detail_match" if detail else "reference_match"
    output = root / f"{slug}_{suffix}.jpg"
    canvas = Image.new("RGB", SHEET_SIZE, "#e6e8e7")
    draw = ImageDraw.Draw(canvas)
    draw.text((52, 34), spec["title"], font=font(42, True), fill="#172430")
    draw.text(
        (54, 94),
        spec["detail"] if detail else spec["identity"],
        font=font(23),
        fill="#4d5960",
    )
    draw.text(
        (54, 132),
        (
            "Custom PBR source and physical construction depth."
            if detail
            else "Reference images are the goalposts; model views use the selected variant."
        ),
        font=font(20),
        fill="#68737a",
    )
    if detail:
        cards = (
            ("AUTHORED ELEVATION", "elevation.jpg", "contain"),
            ("PHYSICAL FACADE DETAIL", f"{slug}_facade_close.png", "cover"),
            ("90° ROOF GOALPOST", "textures/source/angle-reference-90.jpg", "contain"),
            ("MODELED ROOF + REAR", f"{slug}_aerial.png", "cover"),
        )
    else:
        cards = (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png", "cover"),
            ("60° SHAPE GOALPOST", "textures/source/angle-reference-60.jpg", "cover"),
            ("ASSEMBLED STREET VIEW", f"{slug}_street.png", "cover"),
            ("ASSEMBLED CORNER", f"{slug}_front_corner_oblique.png", "cover"),
        )
    boxes = (
        (50, 188, 780, 780),
        (820, 188, 1550, 780),
        (50, 816, 780, 1368),
        (820, 816, 1550, 1368),
    )
    for index, ((label, relative, mode), box_bounds) in enumerate(zip(cards, boxes)):
        place_card(
            canvas,
            draw,
            root / relative,
            box_bounds,
            label,
            "#8a4b19" if index < 2 else "#226a48",
            mode,
        )
    canvas.save(output, quality=91, optimize=True, progressive=True)
    return output


if __name__ == "__main__":
    for family in FAMILIES:
        print(build_sheet(family, detail=False))
        print(build_sheet(family, detail=True))
