"""Publish the Scottish Baronial v77 material/void contract review."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/reviews/scottish-baronial-v77"
REFERENCE = REPO / "frontend/public/archetypes/buildings/chateauesque-grand-railway-hotel"
V76 = REPO / "artifacts/architectural-evidence-v76/model-v2"
V77_ROOT = REPO / "artifacts/material-void-v77"
V77 = V77_ROOT / "model-v2"
P76 = "scottish-baronial-architectural-evidence-v76"
P77 = "scottish-baronial-material-void-v77"


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
    manifest = json.loads((V77 / f"{P77}_manifest.json").read_text(encoding="utf-8"))
    runtime = manifest["generation_quality"]
    board = Image.new("RGB", (2550, 1530), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "Scottish Baronial v77 - material continuity + executable passage", font=font(42, True), fill="#101b2b")
    draw.text((57, 88), "Catalogue metadata now becomes a checked Blender contract; no image API or new installation required.", font=font(21), fill="#536174")
    draw.rectangle((55, 128, 2495, 137), fill="#2aa7a1")
    for title, left in (("ARCHETYPE", 55), ("V76 BEFORE", 885), ("V77 CONTRACT", 1715)):
        draw.rectangle((left, 160, left + 780, 204), fill="#111c2b")
        draw.text((left + 16, 171), title, font=font(17, True), fill="white")

    rows = [
        (
            "STREET MATERIAL + PASSAGE",
            REFERENCE / "variant_0.png",
            V76 / f"{P76}_archetype_match.png",
            V77 / f"{P77}_archetype_match.png",
            "Flat gate infill; colour-only fixed masses",
            "Open 11.73 m passage; granite/slate bindings",
        ),
        (
            "AERIAL ROOF + TURRET CONTINUITY",
            REFERENCE / "variant_0_angle_60.jpg",
            V76 / f"{P76}_aerial.png",
            V77 / f"{P77}_aerial.png",
            "Smooth dark roof; pale mono-colour battlements",
            "Welsh-slate surface; granite signature assemblies",
        ),
    ]
    for row_index, (label, reference, before, after, before_note, after_note) in enumerate(rows):
        top = 228 + row_index * 595
        draw.text((55, top - 21), label, font=font(16, True), fill="#273548")
        for left, path in zip((55, 885, 1715), (reference, before, after)):
            board.paste(contain(path, (780, 500)), (left, top))
            draw.rectangle((left, top, left + 780, top + 500), outline="#b8b1a5", width=2)
        draw.text((885, top + 511), before_note, font=font(17, True), fill="#7c3b35")
        draw.text((1715, top + 511), after_note, font=font(17, True), fill="#17665e")

    passed = sum(1 for gate in runtime["gates"] if gate["passed"])
    draw.rectangle((55, 1410, 2495, 1490), fill="#e1ddd4")
    draw.text((75, 1425), f"Runtime result: {passed}/{len(runtime['gates'])} declared gates pass; 149,730 assembled triangles; $0 API cost.", font=font(22, True), fill="#101b2b")
    draw.text((75, 1458), "Review-only: passage/material regressions are fixed; turret articulation and archetype-specific roof topology remain the largest gaps.", font=font(18), fill="#455468")
    board.save(OUTPUT / "01-v76-v77-material-void-comparison.png", optimize=True)

    shutil.copy2(V77_ROOT / "generation-quality.json", OUTPUT / "generation-quality-preflight.json")
    (OUTPUT / "generation-quality-runtime.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")
    summary = {
        "schema": "material-void-pilot-summary@1",
        "status": "review_only",
        "api_cost_usd": 0.0,
        "assembled_triangles": manifest["assembled"]["triangle_count"],
        "runtime_quality": runtime["status"],
        "passed_runtime_gates": passed,
        "total_runtime_gates": len(runtime["gates"]),
        "metadata_cues": [
            "rusticated pink-grey granite ashlar",
            "dark grey natural slate",
            "deeply recessed",
        ],
        "accepted": [
            "Welsh-slate texture resolves on main and turret roofs",
            "granite texture family binds to turrets, shaped gables and crenellations",
            "pointed entrance is a full-depth 11.73 m passage",
            "facade skin clears the passage and portal has no back plane",
        ],
        "remaining": [
            "stronger per-turret stone course registration and window returns",
            "reference-accurate dormer arrays and gate-tower hierarchy",
            "intersecting cross-gables, ridge caps, valleys and chimney clusters",
        ],
    }
    (OUTPUT / "pilot-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for path in sorted(OUTPUT.iterdir()):
        print(path)


if __name__ == "__main__":
    main()
