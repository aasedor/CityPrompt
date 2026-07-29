"""Build phone-safe review sheets for the Wave 4 standard-building pilot."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
FAMILY = "historical-brick-main-street"
ROOT = REPO / "frontend" / "public" / "families" / FAMILY
SHEET_SIZE = (1600, 1420)

SHEETS = (
    {
        "suffix": "reference_match",
        "subtitle": (
            "Goalpost geometry compared with the assembled two-storey LEGO "
            "building from matching street and corner views."
        ),
        "cards": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png", "cover"),
            ("60° SHAPE + SIDE GOALPOST", "textures/source/angle-reference-60.jpg", "cover"),
            ("ASSEMBLED FRONT", f"{FAMILY}_preview.png", "cover"),
            ("ASSEMBLED CORNER", f"{FAMILY}_front_corner_oblique.png", "cover"),
        ),
    },
    {
        "suffix": "detail_match",
        "subtitle": (
            "Render-locked facade and roof sources compared with physical "
            "recesses, custom PBR masonry, glazing and service-roof geometry."
        ),
        "cards": (
            ("AUTHORED ELEVATION SOURCE", "elevation.jpg", "cover"),
            ("PHYSICAL FACADE DETAIL", f"{FAMILY}_facade_close.png", "cover"),
            ("90° ROOF GOALPOST", "textures/source/angle-reference-90.jpg", "contain"),
            ("RECESSED SERVICE ROOF", f"{FAMILY}_aerial.png", "cover"),
        ),
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
    mode: str,
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
        target_size = (image_box[2] - image_box[0], image_box[3] - image_box[1])
        if mode == "contain":
            image = ImageOps.contain(
                source.convert("RGB"),
                target_size,
                method=Image.Resampling.LANCZOS,
            )
            position = (
                image_box[0] + (target_size[0] - image.width) // 2,
                image_box[1] + (target_size[1] - image.height) // 2,
            )
        else:
            image = ImageOps.fit(
                source.convert("RGB"),
                target_size,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            position = image_box[:2]
    canvas.paste(image, position)


def build_sheet(spec: dict[str, object]) -> Path:
    output = ROOT / f"{FAMILY}_{spec['suffix']}.jpg"
    canvas = Image.new("RGB", SHEET_SIZE, "#e6e8e7")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (52, 34),
        "HISTORICAL BRICK MAIN STREET",
        font=font(42, True),
        fill="#172430",
    )
    draw.text(
        (54, 94),
        "Wave 4 standard-building pilot · Victorian Polychrome",
        font=font(24),
        fill="#8a4b19",
    )
    draw.text(
        (54, 132),
        str(spec["subtitle"]),
        font=font(20),
        fill="#68737a",
    )

    boxes = (
        (50, 188, 780, 780),
        (820, 188, 1550, 780),
        (50, 816, 780, 1368),
        (820, 816, 1550, 1368),
    )
    cards = spec["cards"]
    assert isinstance(cards, tuple)
    for index, ((label, relative_path, mode), box) in enumerate(zip(cards, boxes)):
        place_card(
            canvas,
            draw,
            ROOT / relative_path,
            box,
            label,
            "#8a4b19" if index < 2 else "#226a48",
            mode,
        )
    canvas.save(output, quality=91, optimize=True, progressive=True)
    return output


if __name__ == "__main__":
    for sheet in SHEETS:
        print(build_sheet(sheet))
