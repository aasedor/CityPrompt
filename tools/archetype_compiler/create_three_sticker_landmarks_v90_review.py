"""Publish the reviewed V90 three-landmark comparison package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs/reviews/catalogue-rollout-v90/three-sticker-landmarks-pilot"
RUN = REPO / "artifacts/three-sticker-landmarks-v90/run"
FACADE = REPO / "artifacts/three-sticker-landmarks-v90/facade-sheets"

BUILDINGS = (
    {
        "slug": "amsterdam-neck-gable",
        "title": "Amsterdam Neck-Gable Merchant",
        "source": REPO / "frontend/public/archetypes/buildings/amsterdam-neck-gable-house",
        "variant": 1,
        "run": RUN / "three-sticker-landmarks-v90-pilot/amsterdam-neck-gable-merchant-v90",
        "family": "amsterdam-neck-gable-merchant-v90",
        "sheet": FACADE / "neck_gable_merchant/elevation_raw.jpg",
    },
    {
        "slug": "paris-zinc-dome-corner",
        "title": "Parisian Zinc-Dome Corner",
        "source": REPO / "frontend/public/archetypes/buildings/parisian-corner-with-dome",
        "variant": 0,
        "run": RUN / "three-sticker-landmarks-v90-paris-repair/paris-zinc-dome-corner-v90",
        "family": "paris-zinc-dome-corner-v90",
        "sheet": FACADE / "parisian-corner-with-dome-zinc-mansard/elevation_raw.jpg",
    },
    {
        "slug": "toronto-yellow-bay-gable",
        "title": "Toronto Yellow-Brick Bay-and-Gable",
        "source": REPO / "frontend/public/archetypes/buildings/toronto-bay-and-gable-house",
        "variant": 0,
        "run": RUN / "three-sticker-landmarks-v90-remaining/toronto-yellow-bay-gable-v90",
        "family": "toronto-yellow-bay-gable-v90",
        "sheet": FACADE / "toronto_bay_gable_yellow_brick/elevation_raw.jpg",
    },
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def panel(path: Path, size: tuple[int, int], label: str) -> Image.Image:
    with Image.open(path) as source:
        image = ImageOps.fit(source.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=20)
    box = draw.textbbox((0, 0), label, font=font)
    draw.rectangle((0, 0, box[2] + 20, box[3] + 18), fill=(15, 18, 20))
    draw.text((10, 8), label, fill=(255, 255, 255), font=font)
    return image


def board(name: str, source_role: str, render_role: str, third_role: str) -> None:
    cell = (640, 480)
    canvas = Image.new("RGB", (cell[0] * 3, cell[1] * len(BUILDINGS)), (30, 32, 35))
    for row, item in enumerate(BUILDINGS):
        variant = item["variant"]
        source_name = f"variant_{variant}.png" if source_role == "street" else f"variant_{variant}_{source_role}.jpg"
        paths = (
            (item["source"] / source_name, f"{item['title']} — exact {source_role}"),
            (item["run"] / f"{item['family']}_{render_role}.png", render_role.replace("_", " ")),
            (item["run"] / f"{item['family']}_{third_role}.png", third_role.replace("_", " ")),
        )
        for column, (path, label) in enumerate(paths):
            canvas.paste(panel(path, cell, label), (column * cell[0], row * cell[1]))
    canvas.save(OUT / name, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for item in BUILDINGS:
        target = OUT / item["slug"]
        target.mkdir(parents=True, exist_ok=True)
        variant = item["variant"]
        copies = {
            "archetype-street.png": item["source"] / f"variant_{variant}.png",
            "archetype-oblique.jpg": item["source"] / f"variant_{variant}_angle_60.jpg",
            "archetype-roof.jpg": item["source"] / f"variant_{variant}_angle_90.jpg",
            "sticker-sheet.jpg": item["sheet"],
        }
        for role in ("archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit"):
            copies[f"generated-{role.replace('_', '-')}.png"] = item["run"] / f"{item['family']}_{role}.png"
        for destination, source in copies.items():
            shutil.copy2(source, target / destination)
        validation = read_json(item["run"] / "validation_report.json")
        finish = read_json(item["run"] / "surface_finish_report.json")
        results.append({
            "building": item["title"],
            "slug": item["slug"],
            "machine_validation": validation.get("status"),
            "surface_finish": finish.get("status"),
            "foreground_similarity": (finish.get("render_parity") or {}).get("similarity"),
            "human_status": "architect_review_pending",
        })
    board("01-exact-archetype-comparison.png", "street", "archetype_match", "facade_close")
    board("02-oblique-side-comparison.png", "angle_60", "front_corner_oblique", "rear_corner_oblique")
    board("03-roof-comparison.png", "angle_90", "roof_audit", "archetype_match")
    (OUT / "review-summary.json").write_text(json.dumps({
        "schema": "three-sticker-landmarks-review@1",
        "pipeline": "v90-continuous-sticker-landmark",
        "paid_image_calls": 5,
        "api_budget_state": "bounded_complete_no_more_calls",
        "results": results,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Three Sticker Landmarks — V90\n\n"
        "This finite batch tests three previously unattempted exact catalogue variants. "
        "Each fixed select-and-place landmark uses one continuous registered facade per elevation; "
        "roof, silhouette, bay, porch, balcony, dome and construction returns remain physical geometry.\n\n"
        "- `01-exact-archetype-comparison.png` compares exact street evidence, the image-match render and facade close-up.\n"
        "- `02-oblique-side-comparison.png` compares exact oblique evidence with front and rear Blender views.\n"
        "- `03-roof-comparison.png` compares exact aerial evidence with the roof audit.\n"
        "- Each building folder includes the three exact references, the rectified sticker sheet and all six architect-review views.\n\n"
        "Five bounded GPT Image calls were used: three first-pass sheets and selective retries for Amsterdam and Toronto. "
        "No semantic-mask calls or unbounded retries were made. Blender, OpenCV-derived masks, PBR baking and QA were local.\n\n"
        "The decisive method correction was to forbid generic punched-window geometry from covering already accurate photographic openings. "
        "The sticker owns visible sash, glazing and facade ornament; physical geometry owns only silhouette and depth-bearing construction.\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
