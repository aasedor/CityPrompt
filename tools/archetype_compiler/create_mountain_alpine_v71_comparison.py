"""Publish deterministic comparison boards for the complete Alpine category v71."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/reviews/mountain-alpine-v71"
FAMILIES = REPO / "artifacts/mountain-alpine-v71/families"
FIDELITY = REPO / "artifacts/mountain-alpine-v71/fidelity"

ITEMS = [
    ("Swiss traditional", "mountain_alpine_chalet", 0, "alpine-swiss-traditional", "archetype_match"),
    ("Austrian contemporary", "mountain_alpine_chalet", 1, "alpine-austrian-contemporary", "archetype_match"),
    ("Bavarian painted", "mountain_alpine_chalet", 2, "alpine-bavarian-painted", "archetype_match"),
    ("Stone Berghaus", "mountain_alpine_chalet", 3, "alpine-stone-berghaus", "archetype_match"),
    ("Ski-resort glulam", "alpine_mixed_use_lodge", 0, "alpine-lodge-ski-resort", "archetype_match"),
    ("Tyrolean mixed-use", "alpine_mixed_use_lodge", 1, "alpine-lodge-tyrolean", "archetype_match"),
    ("Stone and timber lodge", "alpine_mixed_use_lodge", 2, "alpine-lodge-stone-timber", "archetype_match"),
    ("Eco-passive lodge", "alpine_mixed_use_lodge", 3, "alpine-lodge-eco-passive", "street"),
]


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def identity_board(title: str, items: list[tuple[str, str, int, str, str]], filename: str) -> None:
    board = Image.new("RGB", (2000, 2260), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((54, 34), title, font=font(42, True), fill="#101b2b")
    draw.text((56, 91), "Exact catalogue archetype on the left; camera-locked Blender result on the right.", font=font(21), fill="#536174")
    draw.rectangle((54, 132, 1946, 141), fill="#91c83e")
    for row, (label, archetype, variant, family, render_view) in enumerate(items):
        top = 176 + row * 510
        reference = REPO / f"frontend/public/archetypes/buildings/{archetype}/variant_{variant}.png"
        render = FAMILIES / family / f"{family}_{render_view}.png"
        report = json.loads((FIDELITY / family / "fidelity_report.json").read_text(encoding="utf-8"))
        metrics = report["metrics"]
        board.paste(contain(reference, (900, 420)), (54, top))
        board.paste(contain(render, (900, 420)), (1046, top))
        draw.rectangle((54, top, 954, top + 420), outline="#b8b1a5", width=2)
        draw.rectangle((1046, top, 1946, top + 420), outline="#b8b1a5", width=2)
        draw.rectangle((54, top, 520, top + 40), fill="#111c2b")
        draw.text((70, top + 9), f"{label.upper()} - ARCHETYPE", font=font(16, True), fill="white")
        draw.rectangle((1046, top, 1510, top + 40), fill="#111c2b")
        draw.text((1062, top + 9), f"{label.upper()} - V71", font=font(16, True), fill="white")
        metric_text = (
            f"OpenCV silhouette: IoU {metrics['silhouette_iou']:.3f} | "
            f"roof RMSE {metrics['roofline_rmse']:.3f} | aspect error {metrics['aspect_ratio_error']:.3f}"
        )
        draw.text((58, top + 438), metric_text, font=font(18, True), fill="#273548")
    board.save(OUTPUT / filename, optimize=True)


def roof_board() -> None:
    board = Image.new("RGB", (2000, 2240), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((54, 34), "Mountain / Alpine v71 - roof-plan audit", font=font(42, True), fill="#101b2b")
    draw.text((56, 91), "Exact 90-degree catalogue evidence on the left; generated aerial construction on the right.", font=font(21), fill="#536174")
    draw.rectangle((54, 132, 1946, 141), fill="#91c83e")
    for row, (label, archetype, variant, family, _render_view) in enumerate(ITEMS):
        top = 170 + row * 252
        reference = REPO / f"frontend/public/archetypes/buildings/{archetype}/variant_{variant}_angle_90.jpg"
        render = FAMILIES / family / f"{family}_aerial.png"
        board.paste(contain(reference, (900, 205)), (54, top))
        board.paste(contain(render, (900, 205)), (1046, top))
        draw.rectangle((54, top, 954, top + 205), outline="#b8b1a5", width=2)
        draw.rectangle((1046, top, 1946, top + 205), outline="#b8b1a5", width=2)
        draw.rectangle((54, top, 420, top + 34), fill="#111c2b")
        draw.text((68, top + 7), f"{label.upper()} - REFERENCE", font=font(14, True), fill="white")
        draw.rectangle((1046, top, 1390, top + 34), fill="#111c2b")
        draw.text((1060, top + 7), f"{label.upper()} - V71", font=font(14, True), fill="white")
    board.save(OUTPUT / "03-roof-plan-comparison.png", optimize=True)


def metrics_summary() -> None:
    rows = []
    for label, _archetype, _variant, family, render_view in ITEMS:
        report = json.loads((FIDELITY / family / "fidelity_report.json").read_text(encoding="utf-8"))
        rows.append({"label": label, "family_id": family, "comparison_view": render_view, **report})
    (OUTPUT / "fidelity-summary.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    identity_board("Mountain / Alpine v71 - complete chalet family", ITEMS[:4], "01-chalet-reference-comparison.png")
    identity_board("Mountain / Alpine v71 - complete mixed-use lodge family", ITEMS[4:], "02-lodge-reference-comparison.png")
    roof_board()
    metrics_summary()
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
