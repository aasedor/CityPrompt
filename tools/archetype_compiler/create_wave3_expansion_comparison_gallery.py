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
            ("CANONICAL FRONT", "concert-hall-modern_preview.png"),
            ("ENTRANCE + SHELL DEPTH", "concert-hall-modern_facade_close.png"),
            ("WHOLE-BUILDING FORM", "concert-hall-modern_aerial.png"),
        ),
    },
    {
        "slug": "barcelona-mercat",
        "title": "MODERNISTA IRON MARKET",
        "identity": "A leaded-glass arched portal fronts an open iron arcade and five glazed aisles.",
        "views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("CANONICAL FRONT", "barcelona-mercat_preview.png"),
            ("CUSTOM GLASS + IRONWORK", "barcelona-mercat_facade_close.png"),
            ("FIVE-AISLE ROOF SYSTEM", "barcelona-mercat_aerial.png"),
        ),
    },
    {
        "slug": "historic-grand-station",
        "title": "BEAUX-ARTS GRAND STATION",
        "identity": "Three deep portals, a carved stone headhouse, and three independent train sheds.",
        "views": (
            ("REFERENCE GOALPOST", "textures/source/archetype-goalpost.png"),
            ("CANONICAL FRONT", "historic-grand-station_preview.png"),
            ("PORTAL CAVITY + FANLIGHT", "historic-grand-station_facade_close.png"),
            ("THREE-SHED SECTION", "historic-grand-station_aerial.png"),
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
        image = ImageOps.fit(
            source.convert("RGB"),
            (image_box[2] - image_box[0], image_box[3] - image_box[1]),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    canvas.paste(image, image_box[:2])


def build_sheet(spec: dict[str, object]) -> Path:
    slug = str(spec["slug"])
    family_root = FAMILIES_ROOT / slug
    output = family_root / f"{slug}_reference_match.jpg"
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
    views = spec["views"]
    assert isinstance(views, tuple)
    for index, ((label, relative_path), box) in enumerate(zip(views, cards)):
        accent = "#8a4b19" if index == 0 else "#226a48"
        place_card(
            canvas,
            draw,
            family_root / relative_path,
            box,
            label,
            accent,
        )

    canvas.save(output, quality=91, optimize=True, progressive=True)
    return output


if __name__ == "__main__":
    for family in FAMILIES:
        print(build_sheet(family))
