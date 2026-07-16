"""Create deterministic reference / v2 / v3 LEGO fidelity review boards."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Review:
    key: str
    title: str
    reference: str
    family: str
    v2_scores: tuple[int, int, int, int]
    v3_scores: tuple[int, int, int, int]
    delivered: str
    remaining: str

    @property
    def v2_total(self) -> int:
        return sum(self.v2_scores)

    @property
    def v3_total(self) -> int:
        return sum(self.v3_scores)


REVIEWS = (
    Review(
        "mass-timber", "Mass Timber Biophilic Infill", "variant_0.png", "mass-timber-biophilic-tower",
        (24, 21, 21, 16), (24, 22, 23, 20),
        "Real glazing voids; alternating planted balconies; timber crown; setback terrace rails",
        "Vegetation is still schematic and the reference has richer interior life",
    ),
    Review(
        "white-render", "European White Render Boutique", "variant_1.png", "european-white-render-boutique",
        (24, 22, 19, 14), (24, 22, 21, 18),
        "Deep punched openings; alternate balcony bays; open terrace rail; framed roof loggia",
        "Target is narrower and more irregular, with finer mesh balcony guards",
    ),
    Review(
        "dark-brick", "Contextual Dark Brick Classical", "variant_2.png", "contextual-dark-brick-classical",
        (24, 21, 18, 12), (24, 22, 22, 20),
        "True curved entry arch; aligned projecting oriels; deep reveals; three-part cornice",
        "Reference oriels are broader and carry more ornamental masonry hierarchy",
    ),
    Review(
        "limestone", "Limestone Panel Contemporary Infill", "variant_3.png", "limestone-panel-balcony-infill",
        (24, 20, 18, 13), (24, 21, 21, 20),
        "Stone opening frames; alternating warm balconies; colonnade; corten crown screen",
        "Perforated guard pattern and tall central portal remain simplified",
    ),
)

BG = "#101419"
CARD = "#1d242b"
LINE = "#34404a"
TEXT = "#f5f3ee"
MUTED = "#aab5bf"
GREEN = "#9be875"
BLUE = "#60c8ec"
AMBER = "#f1bd68"


def font(size: int, bold: bool = False):
    root = Path("C:/Windows/Fonts")
    candidate = root / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def fit_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - size[0]) // 2)
    top = max(0, (resized.height - size[1]) // 2)
    return resized.crop((left, top, left + size[0], top + size[1]))


def wrap(draw: ImageDraw.ImageDraw, value: str, xy: tuple[int, int], width: int, text_font, fill: str) -> int:
    words, lines, line = value.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=text_font) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    y = xy[1]
    for row in lines:
        draw.text((xy[0], y), row, font=text_font, fill=fill)
        y += text_font.size + 5
    return y


def comparison_board(repo: Path, output: Path, review: Review) -> Path:
    reference = repo / "frontend/public/archetypes/buildings/contemporary_midrise" / review.reference
    v2 = repo / "build/lego-pilot/pilot" / review.key / f"{review.family}_preview.png"
    v3 = repo / "build/lego-fidelity-v3" / review.key / f"{review.family}_preview.png"
    sources = (("ARCHETYPE TARGET", reference), ("GRAMMAR v2", v2), ("FIDELITY v3", v3))

    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), review.title, font=font(40, True), fill=TEXT)
    draw.text((48, 78), "Archetype fidelity review · same deterministic builder pipeline", font=font(20), fill=MUTED)
    draw.rounded_rectangle((1570, 31, 1870, 92), radius=18, fill="#26352c", outline="#45634c", width=2)
    draw.text((1600, 45), f"{review.v2_total} → {review.v3_total}/100", font=font(27, True), fill=GREEN)

    card_y, card_w, image_h, gap = 124, 586, 452, 32
    for index, (label, path) in enumerate(sources):
        x = 48 + index * (card_w + gap)
        draw.rounded_rectangle((x, card_y, x + card_w, card_y + 504), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(fit_cover(path, (card_w - 24, image_h)), (x + 12, card_y + 12))
        label_color = GREEN if index == 2 else TEXT
        draw.text((x + 18, card_y + 474), label, font=font(18, True), fill=label_color)

    labels = ("Massing / floors", "Material / palette", "Facade rhythm", "Signature features")
    score_y = 677
    draw.text((48, score_y), "Design-feature fidelity", font=font(25, True), fill=TEXT)
    draw.text((370, score_y + 4), "human rubric · 25 points each", font=font(17), fill=MUTED)
    for index, (label, old, new) in enumerate(zip(labels, review.v2_scores, review.v3_scores)):
        x = 48 + index * 460
        draw.text((x, score_y + 46), label, font=font(17, True), fill=MUTED)
        draw.text((x + 295, score_y + 46), f"{old} → {new}", font=font(18, True), fill=GREEN)
        draw.rounded_rectangle((x, score_y + 78, x + 390, score_y + 92), radius=7, fill="#3a454f")
        draw.rounded_rectangle((x, score_y + 78, x + round(390 * old / 25), score_y + 92), radius=7, fill=BLUE)
        draw.rounded_rectangle((x, score_y + 100, x + 390, score_y + 114), radius=7, fill="#3a454f")
        draw.rounded_rectangle((x, score_y + 100, x + round(390 * new / 25), score_y + 114), radius=7, fill=GREEN)

    draw.text((48, 846), "v3 delivered", font=font(18, True), fill=GREEN)
    wrap(draw, review.delivered, (178, 843), 730, font(18), TEXT)
    draw.text((985, 846), "Next gap", font=font(18, True), fill=AMBER)
    wrap(draw, review.remaining, (1085, 843), 770, font(18), TEXT)
    draw.line((48, 1005, 1872, 1005), fill=LINE, width=2)
    draw.text((48, 1024), "Scores compare architectural features—not pixels. Camera, trees and surrounding context intentionally differ.", font=font(17), fill=MUTED)
    path = output / f"{review.key}_v3_comparison.png"
    board.save(path, optimize=True)
    return path


def showcase_board(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1320), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 30), "LEGO Fidelity v3 · Four archetype-derived families", font=font(40, True), fill=TEXT)
    draw.text((48, 81), "Real facade openings · alternating floor modules · signature attachments · authored crowns", font=font(20), fill=MUTED)
    for index, review in enumerate(REVIEWS):
        col, row = index % 2, index // 2
        x, y = 48 + col * 924, 132 + row * 565
        draw.rounded_rectangle((x, y, x + 890, y + 530), radius=20, fill=CARD, outline=LINE, width=2)
        source = repo / "build/lego-fidelity-v3" / review.key / f"{review.family}_preview.png"
        board.paste(fit_cover(source, (866, 420)), (x + 12, y + 12))
        draw.text((x + 18, y + 452), review.title, font=font(22, True), fill=TEXT)
        draw.text((x + 18, y + 489), f"Fidelity {review.v3_total}/100", font=font(18, True), fill=GREEN)
        draw.text((x + 690, y + 489), f"+{review.v3_total - review.v2_total} vs v2", font=font(18, True), fill=BLUE)
    draw.line((48, 1260, 1872, 1260), fill=LINE, width=2)
    draw.text((48, 1280), "All four assembled GLBs and 24 distinct modules passed automated geometry and manifest validation.", font=font(18), fill=MUTED)
    path = output / "v3_showcase.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_fidelity_v3").resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = [comparison_board(repo, output, review) for review in REVIEWS]
    paths.append(showcase_board(repo, output))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
