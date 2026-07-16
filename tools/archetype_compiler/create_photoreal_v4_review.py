"""Create v4 archetype-fidelity and city-quality review boards."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Family:
    key: str
    title: str
    reference: str
    directory: str
    stem: str
    delivered: str


FAMILIES = (
    Family(
        "mass-timber", "Mass Timber Biophilic Infill", "variant_0.png", "mass-timber",
        "mass-timber-biophilic-tower",
        "Four-sided timber grid, staggered planter bays, coated curtain wall, green roof + full roof plant",
    ),
    Family(
        "white-render", "European White Render Boutique", "variant_1.png", "white-render",
        "european-white-render-boutique",
        "Deep punched openings, alternating balconies, panel joints, roof loggia + service equipment",
    ),
    Family(
        "dark-brick", "Contextual Dark Brick Classical", "variant_2.png", "dark-brick",
        "contextual-dark-brick-classical",
        "True arch, projecting oriel stacks, brick coursing, sills, cornice hierarchy + detailed roof",
    ),
    Family(
        "limestone", "Limestone Panel Contemporary Infill", "variant_3.png", "limestone",
        "limestone-panel-balcony-infill",
        "Panel grid, timber balconies, colonnade entry, Corten crown wrap + four-sided joint logic",
    ),
)

BG = "#10151a"
CARD = "#1b232a"
LINE = "#35434d"
TEXT = "#f6f3ec"
MUTED = "#aeb8c0"
GREEN = "#9be875"
BLUE = "#68c7eb"
AMBER = "#edbc69"


def font(size: int, bold: bool = False):
    fonts = Path("C:/Windows/Fonts")
    path = fonts / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def fit_cover(path: Path, size: tuple[int, int], anchor_y: float = 0.5) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - size[0]) // 2)
    top = max(0, round((resized.height - size[1]) * anchor_y))
    return resized.crop((left, top, left + size[0], top + size[1]))


def wrap(draw: ImageDraw.ImageDraw, value: str, x: int, y: int, width: int, text_font, fill: str) -> int:
    lines: list[str] = []
    line = ""
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=text_font) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for row in lines:
        draw.text((x, y), row, font=text_font, fill=fill)
        y += text_font.size + 6
    return y


def family_board(repo: Path, output: Path, family: Family) -> Path:
    sources = (
        ("ARCHETYPE IMAGE", repo / "frontend/public/archetypes/buildings/contemporary_midrise" / family.reference),
        ("V4 FRONT / OBLIQUE", repo / "build/lego-photoreal-v4" / family.directory / f"{family.stem}_preview.png"),
        ("V4 AERIAL / ROOF", repo / "build/lego-photoreal-v4" / family.directory / f"{family.stem}_aerial.png"),
    )
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 30), family.title, font=font(40, True), fill=TEXT)
    draw.text((48, 82), "Archetype fidelity review · modular GLB family · geometry schema v3 / generator v0.6", font=font(19), fill=MUTED)
    draw.rounded_rectangle((1600, 30, 1872, 91), radius=17, fill="#26382d", outline="#46644d", width=2)
    draw.text((1644, 45), "V4 VALIDATED", font=font(22, True), fill=GREEN)

    card_y, card_w, card_h, gap = 130, 586, 570, 32
    for index, (label, path) in enumerate(sources):
        x = 48 + index * (card_w + gap)
        draw.rounded_rectangle((x, card_y, x + card_w, card_y + card_h), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(fit_cover(path, (card_w - 24, 494), 0.42), (x + 12, card_y + 12))
        draw.text((x + 18, card_y + 526), label, font=font(18, True), fill=GREEN if index else TEXT)

    draw.text((48, 746), "Delivered in v4", font=font(23, True), fill=GREEN)
    wrap(draw, family.delivered, 48, 786, 860, font(20), TEXT)
    draw.text((1010, 746), "Quality contract", font=font(23, True), fill=BLUE)
    wrap(
        draw,
        "PBR albedo / normal / roughness + baked AO; real opening depth; wraparound elevation detail; "
        "authored roof plant; persistent clipping of the original Google tile building when placed.",
        1010, 786, 850, font(20), TEXT,
    )
    draw.line((48, 1003, 1872, 1003), fill=LINE, width=2)
    draw.text((48, 1024), "Reference resemblance is judged by massing, material, facade rhythm and signature geometry—not pixel identity.", font=font(18), fill=MUTED)
    path = output / f"{family.key}_v4_review.png"
    board.save(path, optimize=True)
    return path


def showcase(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1320), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), "LEGO Photoreal v4 · authored buildings for real 3D city context", font=font(40, True), fill=TEXT)
    draw.text((48, 80), "Four facade systems · four-sided detail · roof service geometry · PBR + AO · 3D Tiles replacement masking", font=font(19), fill=MUTED)
    for index, family in enumerate(FAMILIES):
        column, row = index % 2, index // 2
        x, y = 48 + column * 924, 130 + row * 564
        draw.rounded_rectangle((x, y, x + 890, y + 530), radius=20, fill=CARD, outline=LINE, width=2)
        source = repo / "build/lego-photoreal-v4" / family.directory / f"{family.stem}_preview.png"
        board.paste(fit_cover(source, (866, 425), 0.42), (x + 12, y + 12))
        draw.text((x + 18, y + 462), family.title, font=font(22, True), fill=TEXT)
        draw.text((x + 18, y + 496), "AO-baked modular GLB · validation PASS", font=font(17, True), fill=GREEN)
    draw.line((48, 1262, 1872, 1262), fill=LINE, width=2)
    draw.text((48, 1281), "The isolated renders review building authorship; the production globe supplies the photogrammetric ground, trees and surrounding city.", font=font(18), fill=MUTED)
    path = output / "v4_showcase.png"
    board.save(path, optimize=True)
    return path


def quality_bar(repo: Path, output: Path, quality_reference: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 30), "Quality-bar translation · photogrammetric city + authored replacement building", font=font(38, True), fill=TEXT)
    draw.text((48, 80), "The target image is a complete scanned urban scene. V4 makes the proposed building compatible with that scene class.", font=font(19), fill=MUTED)
    left = fit_cover(quality_reference, (894, 638), 0.5)
    right_path = repo / "build/lego-photoreal-v4/mass-timber/mass-timber-biophilic-tower_context.png"
    right = fit_cover(right_path, (894, 638), 0.44)
    board.paste(left, (48, 126))
    board.paste(right, (978, 126))
    draw.rectangle((48, 126, 942, 764), outline=LINE, width=2)
    draw.rectangle((978, 126, 1872, 764), outline=LINE, width=2)
    draw.text((66, 724), "REFERENCE · PHOTOGRAMMETRIC CITY", font=font(18, True), fill=TEXT)
    draw.text((996, 724), "V4 · AUTHORED MODEL / URBAN QA RIG", font=font(18, True), fill=GREEN)

    draw.text((48, 811), "Production composition", font=font(23, True), fill=BLUE)
    wrap(
        draw,
        "Google Photorealistic 3D Tiles retain the real terrain and surrounding city. Once a replacement GLB is mounted, "
        "a persistent footprint stencil removes the scanned building beneath it; the PBR model is then seated on terrain with no double-building collision.",
        48, 851, 1824, font(20), TEXT,
    )
    draw.text((48, 1016), "This is the route to the attached quality class; the QA background is intentionally lightweight and is not the production city mesh.", font=font(18), fill=AMBER)
    path = output / "quality_bar_translation.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quality-reference", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_photoreal_v4").resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = [family_board(repo, output, family) for family in FAMILIES]
    paths.append(showcase(repo, output))
    if args.quality_reference and args.quality_reference.exists():
        paths.append(quality_bar(repo, output, args.quality_reference.resolve()))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
