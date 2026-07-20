"""Create the review board for the Modernist Civic Block massing pilot."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHETYPE = REPO_ROOT / "frontend/public/archetypes/buildings/modernist_civic_block/variant_0.png"
V8 = REPO_ROOT / "build/worldclass-v8/families/modernist-civic-block/modernist-civic-block_preview.png"
PILOT = REPO_ROOT / "build/modernist-civic-massing-pilot"
OUTPUT = PILOT / "modernist-civic-massing-comparison.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def panel(image_path: Path, size: tuple[int, int], label: str, accent: str) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    body_h = size[1] - 54
    fitted = ImageOps.fit(image, (size[0], body_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.52))
    result = Image.new("RGB", size, "#f4f1e9")
    result.paste(fitted, (0, 54))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], 54), fill=accent)
    draw.text((18, 14), label, font=font(23, bold=True), fill="white")
    return result


def main() -> None:
    required = [
        ARCHETYPE,
        V8,
        PILOT / "modernist-civic-block_archetype_match.png",
        PILOT / "modernist-civic-block_street.png",
        PILOT / "modernist-civic-block_aerial.png",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing gallery inputs:\n" + "\n".join(missing))

    canvas = Image.new("RGB", (1800, 1570), "#f6f3eb")
    draw = ImageDraw.Draw(canvas)
    draw.text((48, 34), "Modernist Civic Block — massing-graph pilot", font=font(44, bold=True), fill="#14202b")
    draw.text(
        (50, 94),
        "The change is structural: V8 facade repetition is replaced by asymmetric solids, real voids and construction assemblies.",
        font=font(22), fill="#53616e",
    )

    card_size = (540, 530)
    for index, (path, label, accent) in enumerate((
        (ARCHETYPE, "ARCHETYPE", "#14202b"),
        (V8, "V8 REPEATED STACK", "#6c7379"),
        (PILOT / "modernist-civic-block_archetype_match.png", "MASSING GRAPH @1", "#39730b"),
    )):
        card = panel(path, card_size, label, accent)
        canvas.paste(card, (48 + index * 578, 148))

    draw.text((48, 718), "Pilot geometry from two review angles", font=font(31, bold=True), fill="#14202b")
    street = panel(PILOT / "modernist-civic-block_street.png", (834, 570), "STREET / CONSTRUCTION DEPTH", "#39730b")
    aerial = panel(PILOT / "modernist-civic-block_aerial.png", (834, 570), "AERIAL / WHOLE-BUILDING COHERENCE", "#39730b")
    canvas.paste(street, (48, 768))
    canvas.paste(aerial, (918, 768))

    draw.rounded_rectangle((48, 1380, 1752, 1526), radius=18, fill="#e8ece4", outline="#b9c5ae", width=2)
    draw.text((76, 1404), "WHAT IS NOW REAL GEOMETRY", font=font(21, bold=True), fill="#39730b")
    draw.text(
        (76, 1444),
        "floating concrete rooms  •  recessed civic lobby  •  pilotis  •  entrance cleft  •  ribbon-window reveals",
        font=font(21), fill="#28343c",
    )
    draw.text(
        (76, 1480),
        "clerestory bands  •  cantilevered roof/soffit  •  panel form ties  •  ceremony steps  •  service core",
        font=font(21), fill="#28343c",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=94)
    print(OUTPUT)


if __name__ == "__main__":
    main()
