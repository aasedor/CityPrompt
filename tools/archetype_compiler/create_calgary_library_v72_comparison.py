"""Publish the exact-reference and methodology boards for the v72 civic pilot."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/reviews/calgary-library-v72"
FAMILY = REPO / "artifacts/calgary-library-v72/families/calgary-library-original"
FIDELITY = REPO / "artifacts/calgary-library-v72/fidelity"
REFERENCE = REPO / "frontend/public/archetypes/buildings/calgary-new-central-library"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def reference_board(report: dict) -> None:
    board = Image.new("RGB", (2000, 1840), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((54, 32), "Calgary catalogue library v72 - exact-reference pilot", font=font(42, True), fill="#101b2b")
    draw.text((56, 90), "Catalogue evidence on the left; deterministic Blender construction on the right.", font=font(21), fill="#536174")
    draw.rectangle((54, 132, 1946, 141), fill="#91c83e")
    metrics = {item["role"]: item["metrics"] for item in report["views"]}
    rows = [
        ("Street identity", REFERENCE / "variant_0.png", FAMILY / "calgary-library-original_archetype_match.png", metrics["street_identity"]),
        ("Oblique massing", REFERENCE / "variant_0_angle_60.jpg", FAMILY / "calgary-library-original_aerial.png", None),
        ("Roof / court plan", REFERENCE / "variant_0_angle_90.jpg", FAMILY / "calgary-library-original_roof_audit.png", metrics["roof_plan"]),
    ]
    for index, (label, reference, render, metric) in enumerate(rows):
        top = 178 + index * 535
        board.paste(contain(reference, (900, 430)), (54, top))
        board.paste(contain(render, (900, 430)), (1046, top))
        draw.rectangle((54, top, 954, top + 430), outline="#b8b1a5", width=2)
        draw.rectangle((1046, top, 1946, top + 430), outline="#b8b1a5", width=2)
        draw.rectangle((54, top, 430, top + 40), fill="#111c2b")
        draw.text((70, top + 9), f"{label.upper()} - REFERENCE", font=font(16, True), fill="white")
        draw.rectangle((1046, top, 1390, top + 40), fill="#111c2b")
        draw.text((1062, top + 9), f"{label.upper()} - V72", font=font(16, True), fill="white")
        if metric:
            text = (
                f"OpenCV: IoU {metric['silhouette_iou']:.3f} | "
                f"roofline RMSE {metric['roofline_rmse']:.3f} | "
                f"aspect error {metric['aspect_ratio_error']:.3f}"
            )
        else:
            text = "Human visual role: portal projection, perimeter wings, rear shell and roof pavilion."
        draw.text((58, top + 450), text, font=font(18, True), fill="#273548")
    board.save(OUTPUT / "01-reference-comparison.png", optimize=True)


def methodology_board(report: dict) -> None:
    board = Image.new("RGB", (2000, 1260), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((54, 32), "V72 methodology evidence", font=font(42, True), fill="#101b2b")
    draw.text((56, 90), "Orthographic identity source, constructed section, isolated plan audit and measured overlap.", font=font(21), fill="#536174")
    draw.rectangle((54, 132, 1946, 141), fill="#91c83e")
    panels = [
        ("ORTHOGRAPHIC FACADE SOURCE", REPO / "tools/archetype_compiler/facade_sources_v72/library_original_snohetta.png"),
        ("FLARED TIMBER SECTION", FAMILY / "calgary-library-original_facade_close.png"),
        ("CONTEXT-FREE ROOF AUDIT", FAMILY / "calgary-library-original_roof_audit.png"),
        ("ROOF COURT OVERLAP", FIDELITY / "overlays/roof_plan.png"),
    ]
    for index, (label, path) in enumerate(panels):
        left = 54 + (index % 2) * 992
        top = 176 + (index // 2) * 500
        board.paste(contain(path, (900, 410), "#d9d5cc"), (left, top))
        draw.rectangle((left, top, left + 900, top + 410), outline="#b8b1a5", width=2)
        draw.rectangle((left, top, left + 410, top + 38), fill="#111c2b")
        draw.text((left + 14, top + 8), label, font=font(15, True), fill="white")
    roof = next(view for view in report["views"] if view["role"] == "roof_plan")
    draw.text(
        (56, 1190),
        f"Paired evidence gate: {report['status'].upper()} | roof-court IoU {roof['metrics']['silhouette_iou']:.3f} | roof-court aspect error {roof['metrics']['aspect_ratio_error']:.3f}",
        font=font(20, True), fill="#273548",
    )
    board.save(OUTPUT / "02-methodology-evidence.png", optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = json.loads((FIDELITY / "evidence_report.json").read_text(encoding="utf-8"))
    reference_board(report)
    methodology_board(report)
    (OUTPUT / "evidence-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
