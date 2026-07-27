"""Create the Gothic Collegiate semantic-geometry pilot comparison board."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROOT = REPO_ROOT / "build" / "gothic-collegiate-relief-v14"
FAMILY_ROOT = BUILD_ROOT / "collegiate-gothic-education"
OLD_ROOT = REPO_ROOT / "build" / "worldclass-v8" / "families" / "collegiate-gothic-education"
LARGE_ROOT = BUILD_ROOT / "size-tiers" / "collegiate-gothic-education-large"
OUTPUT = BUILD_ROOT / "gothic-collegiate-v14-board.png"


def font(size: int, *, bold: bool = False):
    candidate = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def panel(path: Path, label: str, colour: str, size: tuple[int, int], *, centering=(0.5, 0.5)) -> Image.Image:
    header = 50
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - header), Image.Resampling.LANCZOS, centering=centering)
    result = Image.new("RGB", size, "#ece8df")
    result.paste(image, (0, header))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, size[0], header), fill=colour)
    draw.text((14, 14), label, font=font(18, bold=True), fill="white")
    return result


def main() -> None:
    manifest = json.loads(
        (FAMILY_ROOT / "collegiate-gothic-education_manifest.json").read_text(encoding="utf-8")
    )
    assembled = manifest["assembled"]
    glb = FAMILY_ROOT / assembled["filename"]
    large_grammar = json.loads((LARGE_ROOT / "grammar.json").read_text(encoding="utf-8"))
    large_manifest = json.loads(
        (LARGE_ROOT / "collegiate-gothic-education-large_manifest.json").read_text(encoding="utf-8")
    )

    canvas = Image.new("RGB", (2160, 760), "#f7f4ec")
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 24), "Gothic Collegiate — semantic geometry stress test", font=font(40, bold=True), fill="#132333")
    draw.text(
        (42, 76),
        "Flat repeated streetwall → tower-and-wings massing with Gothic construction depth",
        font=font(22), fill="#536472",
    )
    draw.text(
        (42, 110),
        f"default: 60 × 25 m / 4 floors / {assembled['triangle_count']:,} tris / {glb.stat().st_size / 1048576:.1f} MB   |   "
        f"large LEGO tier: {large_grammar['dimensions']['width_m']:.0f} × {large_grammar['dimensions']['depth_m']:.0f} m / "
        f"{large_manifest['assembled']['floors']} floors / validation pass",
        font=font(18, bold=True), fill="#3f6d27",
    )

    paths = (
        REPO_ROOT / "frontend/public/archetypes/buildings/collegiate_gothic_education/variant_0.png",
        OLD_ROOT / "collegiate-gothic-education_preview.png",
        FAMILY_ROOT / "collegiate-gothic-education_archetype_match.png",
        FAMILY_ROOT / "collegiate-gothic-education_context.png",
    )
    labels = (
        ("ARCHETYPE GOALPOST", "#142536", (0.5, 0.5)),
        ("V8 FLAT BASELINE", "#5a6670", (0.5, 0.55)),
        ("V14 GOTHIC ASSEMBLY", "#347711", (0.5, 0.52)),
        ("CITY-SCALE CONTEXT", "#23677a", (0.5, 0.5)),
    )
    size = (500, 500)
    for x, path, (label, colour, centering) in zip((40, 565, 1090, 1615), paths, labels):
        if not path.exists():
            raise SystemExit(f"missing gallery input: {path}")
        canvas.paste(panel(path, label, colour, size, centering=centering), (x, 160))

    draw.rounded_rectangle((40, 686, 2115, 735), radius=12, fill="#e3eadf", outline="#bac8b5", width=2)
    draw.text(
        (60, 700),
        "Reusable kits: pointed portal · stepped buttresses · projecting oriels · battlements · pinnacles · steep gable roofs",
        font=font(19, bold=True), fill="#2d4e25",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
