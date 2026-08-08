"""Publish controlled baseline/SAM comparison boards for the v74 museum pilot."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "artifacts/sam3d-museum-ab-pilot"
OUTPUT = REPO / "docs/reviews/sam-ab-titanium-museum-v74"
REFERENCE = REPO / "frontend/public/archetypes/buildings/large-art-museum-gallery"
BASELINE = ROOT / "baseline-model"
INFORMED = ROOT / "sam-informed-model"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def metric(report: dict, role: str) -> dict:
    return next(view["metrics"] for view in report["views"] if view["role"] == role)


def comparison_board(baseline_report: dict, informed_report: dict) -> None:
    board = Image.new("RGB", (2550, 2020), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "Titanium Museum v74 — controlled SAM 3D A/B", font=font(44, True), fill="#101b2b")
    draw.text(
        (57, 91),
        "Same archetype, compiler, cameras and renderer. Only SAM-derived plan/section evidence changes.",
        font=font(21), fill="#536174",
    )
    draw.rectangle((55, 132, 2495, 141), fill="#2aa7a1")

    columns = [("ARCHETYPE", 55), ("BASELINE — NO SAM", 885), ("SAM-INFORMED", 1715)]
    for title, left in columns:
        draw.rectangle((left, 166, left + 780, 210), fill="#111c2b")
        draw.text((left + 16, 177), title, font=font(17, True), fill="white")

    rows = [
        (
            "STREET IDENTITY",
            REFERENCE / "variant_0.png",
            BASELINE / "titanium-museum-baseline-v74_archetype_match.png",
            INFORMED / "titanium-museum-sam-informed-v74_archetype_match.png",
        ),
        (
            "OBLIQUE MASSING",
            REFERENCE / "variant_0_angle_60.jpg",
            BASELINE / "titanium-museum-baseline-v74_aerial.png",
            INFORMED / "titanium-museum-sam-informed-v74_aerial.png",
        ),
        (
            "ROOF / PLAN",
            REFERENCE / "variant_0_angle_90.jpg",
            BASELINE / "titanium-museum-baseline-v74_roof_audit.png",
            INFORMED / "titanium-museum-sam-informed-v74_roof_audit.png",
        ),
    ]
    for row_index, (label, reference, baseline, informed) in enumerate(rows):
        top = 235 + row_index * 555
        draw.text((55, top - 21), label, font=font(16, True), fill="#273548")
        for left, path in zip((55, 885, 1715), (reference, baseline, informed)):
            board.paste(contain(path, (780, 470)), (left, top))
            draw.rectangle((left, top, left + 780, top + 470), outline="#b8b1a5", width=2)

        if row_index == 0:
            base = metric(baseline_report, "street_identity")
            sam = metric(informed_report, "street_identity")
            draw.text(
                (885, top + 481),
                f"IoU {base['silhouette_iou']:.3f}  •  aspect error {base['aspect_ratio_error']:.3f}",
                font=font(17, True), fill="#7c3b35",
            )
            draw.text(
                (1715, top + 481),
                f"IoU {sam['silhouette_iou']:.3f}  •  aspect error {sam['aspect_ratio_error']:.3f}",
                font=font(17, True), fill="#17665e",
            )
        elif row_index == 1:
            draw.text((885, top + 481), "5 broad, regular pods; shallow cantilever", font=font(17, True), fill="#7c3b35")
            draw.text((1715, top + 481), "7 varied pods; stronger lean and cantilever", font=font(17, True), fill="#17665e")
        else:
            base = metric(baseline_report, "roof_plan")
            sam = metric(informed_report, "roof_plan")
            draw.text((885, top + 481), f"Outer silhouette IoU {base['silhouette_iou']:.3f}", font=font(17, True), fill="#273548")
            draw.text((1715, top + 481), f"Outer silhouette IoU {sam['silhouette_iou']:.3f}", font=font(17, True), fill="#273548")

    draw.rectangle((55, 1900, 2495, 1980), fill="#e1ddd4")
    draw.text((75, 1917), "Result: SAM improves gross massing and street proportions, but it does not solve the dominant realism gap.", font=font(22, True), fill="#101b2b")
    draw.text((75, 1950), "Largest weakness: the reference's luminous perforated metal veil and interlocking curved roof/wall topology are rendered as opaque dark shells and capped drums.", font=font(19), fill="#455468")
    board.save(OUTPUT / "01-sam-ab-reference-comparison.png", optimize=True)


def diagnosis_board(baseline_report: dict, informed_report: dict) -> None:
    board = Image.new("RGB", (2200, 1390), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "What the SAM pass changed — and what it could not", font=font(42, True), fill="#101b2b")
    draw.text((57, 91), "SAM is useful as plan/section evidence; envelope optics and architectural assembly still require authored geometry.", font=font(21), fill="#536174")
    draw.rectangle((55, 132, 2145, 141), fill="#2aa7a1")

    panels = [
        ("SAM PROJECTION — RADIAL POD EVIDENCE", ROOT / "sam-results/pilot-01/preview-pca-front.png"),
        ("SAM-INFORMED ROOF", INFORMED / "titanium-museum-sam-informed-v74_roof_audit.png"),
        ("ARCHETYPE ENVELOPE", REFERENCE / "variant_0.png"),
        ("CURRENT ENVELOPE", INFORMED / "titanium-museum-sam-informed-v74_archetype_match.png"),
    ]
    for index, (title, path) in enumerate(panels):
        left = 55 + (index % 2) * 1060
        top = 185 + (index // 2) * 515
        board.paste(contain(path, (1005, 425)), (left, top))
        draw.rectangle((left, top, left + 1005, top + 425), outline="#b8b1a5", width=2)
        draw.rectangle((left, top, left + 500, top + 40), fill="#111c2b")
        draw.text((left + 14, top + 10), title, font=font(15, True), fill="white")

    street_base = metric(baseline_report, "street_identity")
    street_sam = metric(informed_report, "street_identity")
    gain = street_sam["silhouette_iou"] - street_base["silhouette_iou"]
    draw.text((58, 1240), f"Measured street silhouette gain: +{gain:.3f} IoU; baseline contract FAIL → SAM-informed PASS.", font=font(20, True), fill="#17665e")
    draw.text((58, 1278), "Priority 1: replace opaque ribbon with a double-layer perforated veil, visible pod separation and patterned shadow transmission.", font=font(19, True), fill="#7c3b35")
    draw.text((58, 1315), "Priority 2: replace capped pods with open/interlocking curved walls, roof courts, skylights and non-planar metal caps.", font=font(19, True), fill="#7c3b35")
    board.save(OUTPUT / "02-sam-methodology-diagnosis.png", optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    baseline_report = json.loads((ROOT / "baseline-evidence.json").read_text(encoding="utf-8"))
    informed_report = json.loads((ROOT / "sam-informed-evidence.json").read_text(encoding="utf-8"))
    comparison_board(baseline_report, informed_report)
    diagnosis_board(baseline_report, informed_report)
    (OUTPUT / "baseline-evidence.json").write_text(json.dumps(baseline_report, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "sam-informed-evidence.json").write_text(json.dumps(informed_report, indent=2) + "\n", encoding="utf-8")
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
