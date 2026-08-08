"""Publish deterministic Alpine chalet v70 roof-detail review boards."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/reviews/alpine-chalet-v70"
REFERENCE = REPO / "frontend/public/archetypes/buildings/mountain_alpine_chalet"
BASELINE = REPO / "artifacts/pilot-v69/final-v5/mountain-alpine-chalet"
FINAL = REPO / "artifacts/pilot-v70/final/mountain-alpine-chalet"
FIDELITY = REPO / "artifacts/pilot-v70/final/fidelity"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e6e3dc") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def panel(board: Image.Image, draw: ImageDraw.ImageDraw, path: Path,
          box: tuple[int, int, int, int], label: str) -> None:
    x0, y0, x1, y1 = box
    board.paste(contain(path, (x1 - x0, y1 - y0)), (x0, y0))
    draw.rectangle(box, outline="#b8b1a5", width=2)
    label_width = max(165, int(draw.textlength(label, font=font(15, True))) + 28)
    draw.rectangle((x0, y0, x0 + label_width, y0 + 34), fill="#111c2b")
    draw.text((x0 + 12, y0 + 8), label, font=font(15, True), fill="white")


def roof_board() -> None:
    board = Image.new("RGB", (1800, 760), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((42, 24), "Swiss Alpine chalet · v70 roof construction", font=font(38, True), fill="#101b2b")
    draw.text((44, 77), "Exact aerial reference vs. smooth v69 roof massing vs. course-modeled v70 roof.", font=font(19), fill="#536174")
    draw.rectangle((42, 115, 1758, 123), fill="#91c83e")
    paths = (
        (REFERENCE / "variant_0_angle_90.jpg", "ARCHETYPE ROOF"),
        (BASELINE / "mountain-alpine-chalet_aerial.png", "V69 SMOOTH ROOF"),
        (FINAL / "mountain-alpine-chalet_aerial.png", "V70 DETAILED ROOF"),
    )
    for index, (path, label) in enumerate(paths):
        x0 = 42 + index * 572
        panel(board, draw, path, (x0, 150, x0 + 540, 630), label)
    draw.text((44, 666), "V70 adds dark shingle and pale stone-slab fields, overlapping courses, ballast weights, metal ridges/gutters and timber verges.",
              font=font(18), fill="#273548")
    draw.text((44, 704), "The watertight gable prisms remain the massing base; detailed courses are a bounded hero-range layer.",
              font=font(18, True), fill="#8b5a19")
    board.save(OUTPUT / "roof-detail-comparison.png", optimize=True)


def identity_board(metrics: dict) -> None:
    board = Image.new("RGB", (1800, 780), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((42, 24), "Street identity · detailed roof retained", font=font(38, True), fill="#101b2b")
    draw.text((44, 77), "Roof construction is checked without changing the validated facade, frontage or overall massing.", font=font(19), fill="#536174")
    draw.rectangle((42, 115, 1758, 123), fill="#91c83e")
    panel(board, draw, REFERENCE / "variant_0.png", (42, 150, 872, 650), "ARCHETYPE PHOTO")
    panel(board, draw, FINAL / "mountain-alpine-chalet_front_corner_oblique.png", (928, 150, 1758, 650), "V70 BLENDER PILOT")
    draw.text((44, 678), "OpenCV remains a regression gate; detailed roof geometry must not destabilize the approved silhouette.", font=font(18), fill="#273548")
    draw.text((44, 716),
              f"IoU {metrics['silhouette_iou']:.5f} · roofline RMSE {metrics['roofline_rmse']:.5f} · aspect error {metrics['aspect_ratio_error']:.5f}.",
              font=font(18, True), fill="#8b5a19")
    board.save(OUTPUT / "street-identity-comparison.png", optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = json.loads((FIDELITY / "fidelity_report.json").read_text(encoding="utf-8"))
    roof_board()
    identity_board(report["metrics"])
    contain(FINAL / "mountain-alpine-chalet_aerial.png", (1600, 1000)).save(OUTPUT / "final-aerial.png", optimize=True)
    contain(FINAL / "mountain-alpine-chalet_front_corner_oblique.png", (1600, 1000)).save(OUTPUT / "final-front-corner.png", optimize=True)
    Image.open(FIDELITY / "fidelity_overlay.png").save(OUTPUT / "fidelity-overlay.png", optimize=True)
    for path in sorted(OUTPUT.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()
