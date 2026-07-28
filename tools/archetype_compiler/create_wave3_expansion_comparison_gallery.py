"""Build phone-safe reference-match sheets for the Wave 3 expansion families."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
SHEET_SIZE = (1600, 1420)

FAMILIES = (
    {
        "slug": "concert-hall-modern",
        "title": "SCULPTURAL CONCERT HALL",
        "identity": "Overlapping white acoustic shells wrap a deep, warm curtain-wall lobby.",
        "views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("ANGLE CONSTRAINTS", "textures/source/angle-reference-v2.png", "contain"),
            ("CANONICAL FRONT", "concert-hall-modern_preview.png"),
            ("WHOLE-BUILDING FORM", "concert-hall-modern_aerial.png"),
        ),
        "detail_views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("ENTRANCE + SHELL DEPTH", "concert-hall-modern_facade_close.png"),
            ("FRONT-CORNER CONTINUITY", "concert-hall-modern_front_corner_oblique.png"),
            ("REAR-CORNER CONTINUITY", "concert-hall-modern_rear_corner_oblique.png"),
        ),
    },
    {
        "slug": "barcelona-mercat",
        "title": "MODERNISTA IRON MARKET",
        "identity": "A leaded-glass arched portal fronts an open iron arcade and five zinc-and-glass aisles.",
        "views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("ANGLE CONSTRAINTS", "textures/source/angle-reference-v2.png", "contain"),
            ("CANONICAL FRONT", "barcelona-mercat_preview.png"),
            ("FIVE-AISLE ROOF SYSTEM", "barcelona-mercat_aerial.png"),
        ),
        "detail_views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("CUSTOM GLASS + IRONWORK", "barcelona-mercat_facade_close.png"),
            ("OCCUPIED SIDE ARCADE", "barcelona-mercat_front_corner_oblique.png"),
            ("REAR ROOF + GABLE", "barcelona-mercat_rear_corner_oblique.png"),
        ),
    },
    {
        "slug": "historic-grand-station",
        "title": "BEAUX-ARTS GRAND STATION",
        "identity": "Three deep portals, a carved stone headhouse, and three independent train sheds.",
        "views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("ANGLE CONSTRAINTS", "textures/source/angle-reference-v2.png", "contain"),
            ("CANONICAL FRONT", "historic-grand-station_preview.png"),
            ("THREE-SHED SECTION", "historic-grand-station_aerial.png"),
        ),
        "detail_views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("PORTAL CAVITY + FANLIGHT", "historic-grand-station_facade_close.png"),
            ("HEADHOUSE + SHED JUNCTION", "historic-grand-station_front_corner_oblique.png"),
            ("REAR TRAIN-SHED ENDS", "historic-grand-station_rear_corner_oblique.png"),
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
        target_size = (image_box[2] - image_box[0], image_box[3] - image_box[1])
        if mode == "contain":
            image = ImageOps.contain(
                source.convert("RGB"),
                target_size,
                method=Image.Resampling.LANCZOS,
            )
            image_position = (
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
            image_position = image_box[:2]
    canvas.paste(image, image_position)


def build_sheet(
    spec: dict[str, object],
    *,
    view_key: str = "views",
    suffix: str = "reference_match",
) -> Path:
    slug = str(spec["slug"])
    family_root = FAMILIES_ROOT / slug
    output = family_root / f"{slug}_{suffix}.jpg"
    canvas = Image.new("RGB", SHEET_SIZE, "#e6e8e7")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (52, 34),
        str(spec["title"]),
        font=font(42, True),
        fill="#172430",
    )
    draw.text(
        (54, 94),
        str(spec["identity"]),
        font=font(24),
        fill="#4d5960",
    )
    draw.text(
        (54, 130),
        "Reference shape is the goalpost; model views prove custom skin and sectional depth.",
        font=font(21),
        fill="#68737a",
    )

    cards = (
        (50, 188, 780, 780),
        (820, 188, 1550, 780),
        (50, 816, 780, 1368),
        (820, 816, 1550, 1368),
    )
    views = spec[view_key]
    assert isinstance(views, tuple)
    for index, (view, box) in enumerate(zip(views, cards)):
        label, relative_path, *options = view
        accent = "#8a4b19" if index == 0 else "#226a48"
        place_card(
            canvas,
            draw,
            family_root / relative_path,
            box,
            label,
            accent,
            options[0] if options else "cover",
        )

    canvas.save(output, quality=91, optimize=True, progressive=True)
    return output


if __name__ == "__main__":
    for family in FAMILIES:
        print(build_sheet(family))
        print(
            build_sheet(
                family,
                view_key="detail_views",
                suffix="detail_match",
            )
        )
