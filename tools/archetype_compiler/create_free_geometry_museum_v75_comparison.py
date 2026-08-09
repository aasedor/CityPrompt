"""Publish the reviewed v75 free-geometry museum pilot."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "artifacts/archetype-geometry-pass-v75"
SAM_ROOT = REPO / "artifacts/sam3d-museum-ab-pilot"
OUTPUT = REPO / "docs/reviews/free-geometry-titanium-museum-v75"
REFERENCE = REPO / "frontend/public/archetypes/buildings/large-art-museum-gallery"
MODEL = ROOT / "model-v2"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def metrics(report: dict, role: str) -> dict:
    return next(view["metrics"] for view in report["views"] if view["role"] == role)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sam_report = json.loads((SAM_ROOT / "sam-informed-evidence.json").read_text(encoding="utf-8"))
    new_report = json.loads((ROOT / "v75-evidence.json").read_text(encoding="utf-8"))
    geometry = json.loads((ROOT / "evidence/architectural-geometry-evidence.json").read_text(encoding="utf-8"))

    board = Image.new("RGB", (2550, 2020), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "Titanium Museum v75 - bounded free-geometry pilot", font=font(44, True), fill="#101b2b")
    draw.text((57, 91), "MoGe-2 + Depth Anything 3 evidence translated into authored Blender geometry; proxy meshes are not shipped.", font=font(21), fill="#536174")
    draw.rectangle((55, 132, 2495, 141), fill="#2aa7a1")

    columns = [("ARCHETYPE", 55), ("SAM-INFORMED v74", 885), ("FREE GEOMETRY v75", 1715)]
    for title, left in columns:
        draw.rectangle((left, 166, left + 780, 210), fill="#111c2b")
        draw.text((left + 16, 177), title, font=font(17, True), fill="white")

    rows = [
        ("STREET IDENTITY", REFERENCE / "variant_0.png", SAM_ROOT / "sam-informed-model/titanium-museum-sam-informed-v74_archetype_match.png", MODEL / "titanium-museum-free-geometry-v75_archetype_match.png"),
        ("OBLIQUE MASSING", REFERENCE / "variant_0_angle_60.jpg", SAM_ROOT / "sam-informed-model/titanium-museum-sam-informed-v74_aerial.png", MODEL / "titanium-museum-free-geometry-v75_aerial.png"),
        ("ROOF / PLAN", REFERENCE / "variant_0_angle_90.jpg", SAM_ROOT / "sam-informed-model/titanium-museum-sam-informed-v74_roof_audit.png", MODEL / "titanium-museum-free-geometry-v75_roof_audit.png"),
    ]
    sam_street = metrics(sam_report, "street_identity")
    new_street = metrics(new_report, "street_identity")
    sam_roof = metrics(sam_report, "roof_plan")
    new_roof = metrics(new_report, "roof_plan")
    for row_index, (label, reference, sam, new) in enumerate(rows):
        top = 235 + row_index * 555
        draw.text((55, top - 21), label, font=font(16, True), fill="#273548")
        for left, path in zip((55, 885, 1715), (reference, sam, new)):
            board.paste(contain(path, (780, 470)), (left, top))
            draw.rectangle((left, top, left + 780, top + 470), outline="#b8b1a5", width=2)
        if row_index == 0:
            draw.text((885, top + 481), f"IoU {sam_street['silhouette_iou']:.3f} | aspect error {sam_street['aspect_ratio_error']:.3f}", font=font(17, True), fill="#273548")
            draw.text((1715, top + 481), f"IoU {new_street['silhouette_iou']:.3f} | aspect error {new_street['aspect_ratio_error']:.3f}", font=font(17, True), fill="#7c3b35")
        elif row_index == 1:
            draw.text((885, top + 481), "Opaque ribbon and shallow side relief", font=font(17, True), fill="#7c3b35")
            draw.text((1715, top + 481), "Open screen, curved shell and real soffit depth", font=font(17, True), fill="#17665e")
        else:
            draw.text((885, top + 481), f"Outer silhouette IoU {sam_roof['silhouette_iou']:.3f}", font=font(17, True), fill="#273548")
            draw.text((1715, top + 481), f"Outer silhouette IoU {new_roof['silhouette_iou']:.3f}", font=font(17, True), fill="#273548")

    draw.rectangle((55, 1900, 2495, 1980), fill="#e1ddd4")
    draw.text((75, 1917), "Result: side depth and cantilever construction improve, but the pilot remains review-only.", font=font(22, True), fill="#101b2b")
    draw.text((75, 1950), "Next bottleneck: replace isolated roof wells with connected curvilinear walls/courts, then calibrate bright titanium, glazing and occupied interiors.", font=font(19), fill="#455468")
    board.save(OUTPUT / "01-reference-comparison.png", optimize=True)

    shutil.copy2(ROOT / "evidence/geometry-evidence-board.png", OUTPUT / "02-geometry-evidence-board.png")
    shutil.copy2(ROOT / "v75-evidence.json", OUTPUT / "fidelity-evidence.json")
    shutil.copy2(ROOT / "evidence/architectural-geometry-evidence.json", OUTPUT / "geometry-evidence.json")
    summary = {
        "schema": "free-geometry-pilot-summary@1",
        "status": "review_only",
        "automatic_geometry_evidence": geometry["status"],
        "human_decision": "apply_shared_visible_constraints_only",
        "model": {"assembled_triangles": 21052, "api_cost_usd": 0.0},
        "metrics": {
            "sam_v74": {"street_iou": sam_street["silhouette_iou"], "street_aspect_error": sam_street["aspect_ratio_error"], "roof_iou": sam_roof["silhouette_iou"]},
            "free_v75": {"street_iou": new_street["silhouette_iou"], "street_aspect_error": new_street["aspect_ratio_error"], "roof_iou": new_roof["silhouette_iou"]},
        },
        "accepted": ["curved screen plan", "visible layer separation", "deep cantilever with soffit", "asymmetric curved inner masses", "multi-level roof evidence"],
        "withheld": ["raw learned mesh", "reflective veil depth", "glass depth", "vegetation", "hidden sides"],
        "next_priority": "connected curvilinear roof-wall topology, then titanium/glazing/interior material calibration",
    }
    (OUTPUT / "pilot-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
