"""Create catalog-archetype versus v6 modular-builder comparison boards."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = "#0c1116"
CARD = "#172028"
LINE = "#34434e"
TEXT = "#f5f1e8"
MUTED = "#aab7c1"
GREEN = "#9be875"
BLUE = "#71c9ef"
AMBER = "#e9b968"


@dataclass(frozen=True)
class Comparison:
    key: str
    title: str
    subtitle: str
    reference: str
    render_dir: str
    family: str
    score: int
    matched: str
    gap: str


COMPARISONS = (
    Comparison(
        "parisian",
        "Parisian limestone mansion block",
        "Catalog parent archetype · 5 floors · heritage_stone + mansard grammar",
        "frontend/public/archetypes/buildings/parisian_mid_rise/hero.png",
        "build/lego-archetype-comparisons-v6/parisian",
        "parisian-midrise-block",
        80,
        "Cream stone palette, vertical sash rhythm, rusticated base, continuous iron balconies, cornice, dormers, chimneys and zinc mansard silhouette.",
        "Target is a corner composition with a brasserie frontage, shallower roof pavilions and more sculpted corbels/cartouches.",
    ),
    Comparison(
        "nordic",
        "Nordic mass-timber mid-rise",
        "Catalog variant · 8 floors · timber_grid grammar",
        "frontend/public/archetypes/buildings/nordic_timber_midrise/variant_0.png",
        "build/lego-archetype-comparisons-v6/nordic",
        "nordic-timber-mass-timber",
        60,
        "Warm engineered-timber PBR, dark deep-set glazing, inhabited interiors, staggered balconies and a clear modular floor system.",
        "Target needs a dedicated exposed post-and-beam frame, recessed loggias, fewer wider bays, a roof pavilion and stronger upper setbacks.",
    ),
    Comparison(
        "industrial",
        "Victorian mill conversion",
        "Catalog variant · 5 floors · brick_bays grammar",
        "frontend/public/archetypes/buildings/industrial_brick_mixed_use/variant_0.png",
        "build/lego-archetype-comparisons-v6/industrial",
        "industrial-brick-original-mill",
        61,
        "Red-brick PBR, steel-framed glazing, retail base, projecting bay rhythm, strong floor bands and a legible industrial streetwall.",
        "Target needs repeated arched factory windows, pilaster bays, a pitched end wall, chimney and glazed rooftop addition instead of residential oriels.",
    ),
)


def font(size: int, bold: bool = False):
    root = Path("C:/Windows/Fonts")
    path = root / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def cover(path: Path, size: tuple[int, int], anchor_y: float = 0.5) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, round((image.height - size[1]) * anchor_y))
    return image.crop((left, top, left + size[0], top + size[1]))


def wrap(draw: ImageDraw.ImageDraw, value: str, x: int, y: int, width: int, face, fill: str, gap: int = 5) -> int:
    line = ""
    rows: list[str] = []
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            line = candidate
        else:
            rows.append(line)
            line = word
    if line:
        rows.append(line)
    for row in rows:
        draw.text((x, y), row, font=face, fill=fill)
        y += face.size + gap
    return y


def manifest_data(repo: Path, item: Comparison) -> tuple[int, float, int, float]:
    path = repo / item.render_dir / f"{item.family}_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    glb = repo / item.render_dir / assembled["filename"]
    return (
        int(assembled["triangle_count"]),
        glb.stat().st_size / (1024 * 1024),
        int(assembled["floors"]),
        float(assembled["height_m"]),
    )


def comparison_board(repo: Path, output: Path, item: Comparison) -> Path:
    reference = repo / item.reference
    render = repo / item.render_dir / f"{item.family}_preview.png"
    triangles, size_mb, floors, height = manifest_data(repo, item)

    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 26), item.title, font=font(38, True), fill=TEXT)
    draw.text((48, 78), item.subtitle, font=font(20), fill=MUTED)
    draw.rounded_rectangle((1640, 28, 1872, 91), radius=18, fill="#26352c", outline="#45634c", width=2)
    draw.text((1673, 43), f"FIDELITY {item.score}/100", font=font(21, True), fill=GREEN)

    board.paste(cover(reference, (894, 590), 0.47), (48, 122))
    board.paste(cover(render, (894, 590), 0.47), (978, 122))
    draw.rectangle((48, 122, 942, 712), outline=LINE, width=2)
    draw.rectangle((978, 122, 1872, 712), outline=LINE, width=2)
    draw.text((66, 672), "ARCHETYPE TARGET", font=font(18, True), fill=TEXT)
    draw.text((996, 672), "V6 MODULAR 3D MODEL", font=font(18, True), fill=GREEN)

    draw.text((48, 752), "MATCHED", font=font(21, True), fill=GREEN)
    wrap(draw, item.matched, 48, 791, 820, font(18), TEXT)
    draw.text((978, 752), "NEXT GRAMMAR GAP", font=font(21, True), fill=AMBER)
    wrap(draw, item.gap, 978, 791, 894, font(18), TEXT)
    draw.line((48, 998, 1872, 998), fill=LINE, width=2)
    draw.text((48, 1022), f"Validated model · {floors} floors · {height:.1f} m · {triangles:,} triangles · {size_mb:.1f} MB · six reusable GLB modules",
              font=font(17), fill=BLUE)
    draw.text((1385, 1049), "Feature fidelity, not pixel similarity", font=font(14), fill=MUTED)
    path = output / f"{item.key}_archetype_vs_v6.png"
    board.save(path, optimize=True)
    return path


def gallery_board(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 2140), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), "Archetype targets vs v6 modular 3D models", font=font(40, True), fill=TEXT)
    draw.text((48, 82), "Three catalog families rendered through the same quality-first Lego pipeline", font=font(21), fill=MUTED)
    draw.text((1505, 48), "CYCLES · 32 SAMPLES", font=font(18, True), fill=BLUE)

    for row, item in enumerate(COMPARISONS):
        y = 132 + row * 646
        reference = repo / item.reference
        render = repo / item.render_dir / f"{item.family}_preview.png"
        draw.rounded_rectangle((48, y, 1872, y + 610), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(cover(reference, (830, 470), 0.47), (66, y + 18))
        board.paste(cover(render, (830, 470), 0.47), (1024, y + 18))
        draw.text((66, y + 505), "TARGET", font=font(17, True), fill=TEXT)
        draw.text((1024, y + 505), "MODEL", font=font(17, True), fill=GREEN)
        draw.text((66, y + 547), item.title, font=font(23, True), fill=TEXT)
        draw.text((1024, y + 549), f"Feature fidelity {item.score}/100", font=font(21, True), fill=GREEN if item.score >= 75 else AMBER)

    draw.line((48, 2080, 1872, 2080), fill=LINE, width=2)
    draw.text((48, 2101), "Strongest transfer: heritage stone. Next dedicated kits: timber frame/loggia and industrial arch/chimney grammars.",
              font=font(18), fill=MUTED)
    path = output / "v6_archetype_comparison_gallery.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_archetype_comparisons_v6").resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = [comparison_board(repo, output, item) for item in COMPARISONS]
    paths.append(gallery_board(repo, output))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
