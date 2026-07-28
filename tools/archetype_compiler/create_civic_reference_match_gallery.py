"""Build phone-safe comparison sheets for the civic custom-skin pilot."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
ARCHETYPE = (
    REPO
    / "frontend"
    / "public"
    / "archetypes"
    / "buildings"
    / "civic_monumental_institution"
)
FAMILY = (
    REPO
    / "frontend"
    / "public"
    / "families"
    / "civic-monumental-neoclassical"
)
OUTPUT = FAMILY / "comparisons"
PREVIOUS_CONTROL = (
    REPO
    / "artifacts"
    / "civic-comparisons"
    / "d-reference"
    / "civic-monumental-neoclassical_preview.png"
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / filename), size)


def card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    source: Path | Image.Image,
    box: tuple[int, int, int, int],
    label: str,
    note: str,
    accent: str,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=24,
        fill="#f8f7f3",
        outline="#c7c5bf",
        width=2,
    )
    image_box = (x0 + 18, y0 + 62, x1 - 18, y1 - 96)
    image = (
        source.copy().convert("RGB")
        if isinstance(source, Image.Image)
        else Image.open(source).convert("RGB")
    )
    fitted = ImageOps.contain(
        image,
        (image_box[2] - image_box[0], image_box[3] - image_box[1]),
        Image.Resampling.LANCZOS,
    )
    px = image_box[0] + (image_box[2] - image_box[0] - fitted.width) // 2
    py = image_box[1] + (image_box[3] - image_box[1] - fitted.height) // 2
    canvas.paste(fitted, (px, py))
    draw.text((x0 + 22, y0 + 18), label, font=font(27, True), fill=accent)
    draw.text((x0 + 22, y1 - 70), note, font=font(21), fill="#343a40")


def build_front() -> None:
    canvas = Image.new("RGB", (1600, 1840), "#e8e6e0")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 36),
        "CIVIC MONUMENT — CUSTOM REGISTERED SKIN",
        font=font(42, True),
        fill="#172430",
    )
    draw.text(
        (62, 94),
        "Exact reference source above; previous generic skin and new canonical below.",
        font=font(25),
        fill="#4e5963",
    )
    cards = [
        (
            ARCHETYPE / "hero.png",
            (55, 160, 785, 950),
            "REFERENCE — ELEVATION",
            "Proportion, symmetry, dome, drum, order",
            "#8a4b19",
        ),
        (
            FAMILY / "textures" / "source" / "civic_reference_elevation_v2.png",
            (815, 160, 1545, 950),
            "CUSTOM RENDER-LOCKED SOURCE",
            "Exact archetype material and carving grammar",
            "#8a4b19",
        ),
        (
            PREVIOUS_CONTROL,
            (55, 980, 785, 1770),
            "BEFORE — GENERIC FOUR-ZONE SKIN",
            "PBR files existed, but the facade was not registered",
            "#42515e",
        ),
        (
            FAMILY / "civic-monumental-neoclassical_preview.png",
            (815, 980, 1545, 1770),
            "AFTER — CANONICAL CUSTOM SKIN",
            "Feature-registered facade plus physical depth",
            "#226a48",
        ),
    ]
    for item in cards:
        card(canvas, draw, *item)
    draw.text(
        (60, 1792),
        "Canonical assembled GLB now embeds the archetype-specific registered material.",
        font=font(22, True),
        fill="#4e5963",
    )
    canvas.save(OUTPUT / "civic-reference-match.jpg", quality=91, optimize=True)


def build_oblique() -> None:
    canvas = Image.new("RGB", (1600, 1080), "#e8e6e0")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 36),
        "CUSTOM SKIN + CONSTRUCTION DEPTH",
        font=font(40, True),
        fill="#172430",
    )
    draw.text(
        (62, 92),
        "The oblique check proves the registered skin remains attached to real geometry.",
        font=font(24),
        fill="#4e5963",
    )
    card(
        canvas,
        draw,
        ARCHETYPE / "variant_0.png",
        (55, 155, 785, 1005),
        "REFERENCE — STREET OBLIQUE",
        "Carved order, projecting portico, integrated stair",
        "#8a4b19",
    )
    card(
        canvas,
        draw,
        FAMILY / "civic-monumental-neoclassical_front_corner_oblique.png",
        (815, 155, 1545, 1005),
        "CANONICAL CUSTOM SKIN",
        "Registered facade on a deep portico and curved drum",
        "#226a48",
    )
    canvas.save(
        OUTPUT / "civic-reference-match-oblique.jpg",
        quality=91,
        optimize=True,
    )


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_front()
    build_oblique()
    print(f"Wrote civic custom-skin sheets to {OUTPUT}")
