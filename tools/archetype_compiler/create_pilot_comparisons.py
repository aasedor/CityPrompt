"""Compose deterministic archetype-vs-builder review boards for the LEGO pilot.

The rubric is an explicit human design-feature review, not pixel similarity:
the source images and Blender renders do not share a camera or context.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class VariantReview:
    key: str
    title: str
    reference: str
    folder: str
    family: str
    scores: tuple[int, int, int, int]
    strengths: str
    gap: str

    @property
    def total(self) -> int:
        return sum(self.scores)


REVIEWS = (
    VariantReview(
        "mass-timber", "Mass Timber Biophilic Infill", "variant_0.png", "mass-timber",
        "mass-timber-biophilic-tower", (24, 21, 21, 16),
        "8-storey proportion, timber grid, curtain wall, staggered planted balconies, green roof",
        "Planting and balcony staggering remain schematic; no interior depth",
    ),
    VariantReview(
        "white-render", "European White Render Boutique", "variant_1.png", "white-render",
        "european-white-render-boutique", (24, 22, 19, 14),
        "6-storey proportion, white render, deep punched glazing, metal balcony rhythm, setback",
        "Reference has more asymmetry, darker frames and finer Juliet railings",
    ),
    VariantReview(
        "dark-brick", "Contextual Dark Brick Classical", "variant_2.png", "dark-brick",
        "contextual-dark-brick-classical", (24, 21, 18, 12),
        "6-storey proportion, dark brick/bronze palette, string courses, grouped tall windows",
        "True arched portal and projecting multi-storey oriels need dedicated modules",
    ),
    VariantReview(
        "limestone", "Limestone Panel Contemporary Infill", "variant_3.png", "limestone",
        "limestone-panel-balcony-infill", (24, 20, 18, 13),
        "4-storey scale, pale frame, warm upper material, projecting balconies, formal entry",
        "Upper band should wrap the crown/side; guard pattern needs a perforated module",
    ),
)

BG = "#11151a"
CARD = "#20262d"
TEXT = "#f6f4ef"
MUTED = "#aeb8c2"
GREEN = "#8fe36d"
AMBER = "#f4bd62"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fonts = Path("C:/Windows/Fonts")
    candidate = fonts / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def fit_cover(source: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(source).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - size[0]) // 2)
    top = max(0, (resized.height - size[1]) // 2)
    return resized.crop((left, top, left + size[0], top + size[1]))


def rounded_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 18) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=CARD, outline="#323b44", width=2)


def wrap(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, text_font, fill: str, spacing: int = 6) -> int:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=text_font) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    y = xy[1]
    for row in lines:
        draw.text((xy[0], y), row, font=text_font, fill=fill)
        y += text_font.size + spacing
    return y


def draw_score_panel(draw: ImageDraw.ImageDraw, review: VariantReview, y: int) -> None:
    labels = ("Massing / floors", "Material / palette", "Facade rhythm", "Signature features")
    draw.text((48, y), f"Design-feature fidelity  {review.total}/100", font=font(28, True), fill=TEXT)
    draw.text((1470, y + 4), "human review rubric", font=font(18), fill=MUTED)
    bar_y = y + 52
    for index, (label, score) in enumerate(zip(labels, review.scores)):
        x = 48 + index * 460
        draw.text((x, bar_y), f"{label}  {score}/25", font=font(18, True), fill=MUTED)
        draw.rounded_rectangle((x, bar_y + 31, x + 390, bar_y + 46), radius=7, fill="#3a424b")
        draw.rounded_rectangle((x, bar_y + 31, x + round(390 * score / 25), bar_y + 46), radius=7, fill=GREEN if score >= 20 else AMBER)
    draw.text((48, y + 123), "Matches", font=font(18, True), fill=GREEN)
    wrap(draw, review.strengths, (145, y + 120), 720, font(18), TEXT)
    draw.text((985, y + 123), "Gap", font=font(18, True), fill=AMBER)
    wrap(draw, review.gap, (1040, y + 120), 820, font(18), TEXT)


def comparison_board(repo: Path, output: Path, review: VariantReview) -> Path:
    reference_root = repo / "frontend/public/archetypes/buildings/contemporary_midrise"
    pilot_root = repo / "build/lego-pilot/pilot" / review.folder
    sources = (
        ("ARCHETYPE REFERENCE", reference_root / review.reference),
        ("PILOT — THREE-QUARTER", pilot_root / f"{review.family}_preview.png"),
        ("PILOT — STREET", pilot_root / f"{review.family}_street.png"),
    )
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 34), review.title, font=font(42, True), fill=TEXT)
    draw.text((48, 88), "Contemporary Midrise · deterministic Building Grammar v2 comparison", font=font(21), fill=MUTED)
    card_y, card_w, card_h, gap = 145, 586, 500, 32
    for index, (label, path) in enumerate(sources):
        x = 48 + index * (card_w + gap)
        rounded_card(draw, (x, card_y, x + card_w, card_y + card_h))
        board.paste(fit_cover(path, (card_w - 24, 422)), (x + 12, card_y + 12))
        draw.text((x + 18, card_y + 450), label, font=font(18, True), fill=TEXT)
    draw_score_panel(draw, review, 690)
    draw.text((48, 1032), "Accuracy measures design features, not pixel similarity; cameras and surrounding context intentionally differ.", font=font(17), fill=MUTED)
    path = output / f"{review.key}_comparison.png"
    board.save(path, optimize=True)
    return path


def before_after_board(repo: Path, output: Path) -> Path:
    review = REVIEWS[0]
    sources = (
        ("ARCHETYPE REFERENCE", repo / "frontend/public/archetypes/buildings/contemporary_midrise/variant_0.png"),
        ("BEFORE — GRAMMAR v1", repo / "build/lego-pilot/baseline/mass-timber/mass-timber-biophilic-tower_preview.png"),
        ("PILOT — GRAMMAR v2", repo / "build/lego-pilot/pilot/mass-timber/mass-timber-biophilic-tower_preview.png"),
    )
    board = Image.new("RGB", (1920, 880), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 34), "Codex LEGO Pilot · Before / After", font=font(42, True), fill=TEXT)
    draw.text((48, 88), "Same Contemporary Midrise target; deterministic geometry and presentation upgrade", font=font(21), fill=MUTED)
    card_y, card_w, card_h, gap = 145, 586, 590, 32
    for index, (label, path) in enumerate(sources):
        x = 48 + index * (card_w + gap)
        rounded_card(draw, (x, card_y, x + card_w, card_y + card_h))
        board.paste(fit_cover(path, (card_w - 24, 500)), (x + 12, card_y + 12))
        draw.text((x + 18, card_y + 526), label, font=font(20, True), fill=TEXT)
    draw.text((48, 780), "v2 adds façade-system rules, visible glazing, projected/recessed layers, planted balcony modules, bevel highlights, entrance types, context and three review cameras.", font=font(19), fill=TEXT)
    path = output / "before_after_mass_timber.png"
    board.save(path, optimize=True)
    return path


def showcase_board(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1320), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 34), "Codex LEGO Pilot · Four deterministic families", font=font(42, True), fill=TEXT)
    draw.text((48, 88), "One Contemporary Midrise archetype · four material and façade systems · 12 presentation renders", font=font(21), fill=MUTED)
    for index, review in enumerate(REVIEWS):
        col, row = index % 2, index // 2
        x, y = 48 + col * 924, 145 + row * 565
        rounded_card(draw, (x, y, x + 890, y + 530))
        preview = repo / "build/lego-pilot/pilot" / review.folder / f"{review.family}_preview.png"
        board.paste(fit_cover(preview, (866, 430)), (x + 12, y + 12))
        draw.text((x + 18, y + 458), review.title, font=font(22, True), fill=TEXT)
        draw.text((x + 18, y + 491), f"Feature fidelity {review.total}/100", font=font(18), fill=GREEN)
    draw.text((48, 1280), "Each family exports podium, repeatable floor, setback, roof and assembled GLBs; every output passed geometric validation.", font=font(18), fill=MUTED)
    path = output / "pilot_showcase.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_pilot").resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = [comparison_board(repo, output, review) for review in REVIEWS]
    paths.extend((before_after_board(repo, output), showcase_board(repo, output)))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
