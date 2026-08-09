"""Publish the Scottish Baronial v76 architectural-evidence review."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "artifacts/architectural-evidence-v76"
OUTPUT = REPO / "docs/reviews/scottish-baronial-v76"
REFERENCE = REPO / "frontend/public/archetypes/buildings/chateauesque-grand-railway-hotel"
V68 = REPO / "artifacts/pilot-v68/final-v2/chateauesque-grand-railway-hotel"
V76 = ROOT / "model-v2"
PREFIX = "scottish-baronial-architectural-evidence-v76"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = json.loads((ROOT / "v76-evidence.json").read_text(encoding="utf-8"))
    v68_report = json.loads((REPO / "artifacts/pilot-v68/final-v2/fidelity/fidelity_report.json").read_text(encoding="utf-8"))
    geometry = json.loads((ROOT / "evidence/architectural-geometry-evidence.json").read_text(encoding="utf-8"))
    interpretation = json.loads((ROOT / "architectural-interpretation.json").read_text(encoding="utf-8"))
    manifest = json.loads((V76 / f"{PREFIX}_manifest.json").read_text(encoding="utf-8"))
    metrics = {view["role"]: view["metrics"] for view in report["views"]}

    board = Image.new("RGB", (2550, 2020), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "Scottish Baronial v76 - architectural evidence pilot", font=font(44, True), fill="#101b2b")
    draw.text((57, 91), "Gold-set grammar plus reviewed MoGe-2 / DA3 constraints; learned proxy meshes are never shipped.", font=font(21), fill="#536174")
    draw.rectangle((55, 132, 2495, 141), fill="#2aa7a1")
    for title, left in (("ARCHETYPE", 55), ("V68 GOLD-SET BASE", 885), ("V76 EVIDENCE-INFORMED", 1715)):
        draw.rectangle((left, 166, left + 780, 210), fill="#111c2b")
        draw.text((left + 16, 177), title, font=font(17, True), fill="white")

    rows = [
        ("STREET IDENTITY", REFERENCE / "variant_0.png", V68 / "chateauesque-grand-railway-hotel_archetype_match.png", V76 / f"{PREFIX}_archetype_match.png"),
        ("OBLIQUE MASSING / SIDE DEPTH", REFERENCE / "variant_0_angle_60.jpg", V68 / "chateauesque-grand-railway-hotel_aerial.png", V76 / f"{PREFIX}_aerial.png"),
        ("ROOF PLAN / COURTYARD", REFERENCE / "variant_0_angle_90.jpg", V68 / "chateauesque-grand-railway-hotel_aerial.png", V76 / f"{PREFIX}_roof_audit.png"),
    ]
    for row_index, (label, reference, v68, v76) in enumerate(rows):
        top = 235 + row_index * 555
        draw.text((55, top - 21), label, font=font(16, True), fill="#273548")
        for left, path in zip((55, 885, 1715), (reference, v68, v76)):
            board.paste(contain(path, (780, 470)), (left, top))
            draw.rectangle((left, top, left + 780, top + 470), outline="#b8b1a5", width=2)
        if row_index == 0:
            draw.text((885, top + 481), f"IoU {v68_report['metrics']['silhouette_iou']:.3f} | inherited 55 x 36 m plan", font=font(17, True), fill="#273548")
            draw.text((1715, top + 481), f"IoU {metrics['street_identity']['silhouette_iou']:.3f} | reviewed 55 x 48 m plan", font=font(17, True), fill="#17665e")
        elif row_index == 1:
            draw.text((885, top + 481), "Shallow plan; four-turret hierarchy", font=font(17, True), fill="#7c3b35")
            draw.text((1715, top + 481), "Deeper wings; side turrets and court elevation", font=font(17, True), fill="#17665e")
        else:
            draw.text((885, top + 481), "Oversized 39 x 20 m court", font=font(17, True), fill="#7c3b35")
            draw.text((1715, top + 481), f"Compact 29 x 24 m court | outer IoU {metrics['roof_plan']['silhouette_iou']:.3f}", font=font(17, True), fill="#17665e")

    draw.rectangle((55, 1900, 2495, 1980), fill="#e1ddd4")
    draw.text((75, 1917), "Result: side depth and plan fidelity improve; this remains review-only, not catalogue gold.", font=font(22, True), fill="#101b2b")
    draw.text((75, 1950), "Next bottleneck: authored roof grammar - dormer arrays, intersecting cross-gables, slate response and the arched crenellated gate tower.", font=font(19), fill="#455468")
    board.save(OUTPUT / "01-v68-v76-reference-comparison.png", optimize=True)

    shutil.copy2(ROOT / "evidence/geometry-evidence-board.png", OUTPUT / "02-geometry-evidence-board.png")
    shutil.copy2(ROOT / "v76-evidence.json", OUTPUT / "fidelity-evidence.json")
    shutil.copy2(ROOT / "evidence/architectural-geometry-evidence.json", OUTPUT / "geometry-evidence.json")
    shutil.copy2(ROOT / "architectural-interpretation.json", OUTPUT / "architectural-interpretation.json")
    shutil.copy2(ROOT / "v76-overlays/street_identity.png", OUTPUT / "03-street-fidelity-overlay.png")
    shutil.copy2(ROOT / "v76-overlays/roof_plan.png", OUTPUT / "04-roof-fidelity-overlay.png")
    summary = {
        "schema": "architectural-evidence-pilot-summary@1",
        "status": "review_only",
        "automatic_geometry_evidence": geometry["status"],
        "human_decision": interpretation["decision"],
        "model": {"assembled_triangles": manifest["assembled"]["triangle_count"], "api_cost_usd": 0.0},
        "evidence": {
            "valid_coverage": geometry["street_geometry"]["valid_coverage"],
            "cross_model_median_disagreement": geometry["street_geometry"]["cross_model_disagreement"]["median_ratio"],
            "roof_confidence_median": geometry["roof_geometry"]["confidence"]["median"],
        },
        "metrics": {
            "v68_street_iou": v68_report["metrics"]["silhouette_iou"],
            "v76_street_iou": metrics["street_identity"]["silhouette_iou"],
            "v76_roof_iou": metrics["roof_plan"]["silhouette_iou"],
        },
        "accepted": ["55 x 48 m near-square plan", "29 x 24 m compact court", "deeper side wings", "side turret hierarchy", "central court gable", "audited gable and turret openings"],
        "withheld": ["raw learned mesh", "vegetation depth", "neighbouring roofs", "occluded rear opening schedule"],
        "next_priority": "authored Scottish Baronial roof and gate-tower topology",
    }
    (OUTPUT / "pilot-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
