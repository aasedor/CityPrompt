"""Publish the bounded V91 all-surface Sticker Method review package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs/reviews/catalogue-rollout-v91/three-all-surface-sticker-pilot"
ARTIFACT = REPO / "artifacts/three-all-surface-stickers-v91"
PREPARED = ARTIFACT / "render-ready-stickers"

BUILDINGS = (
    {
        "slug": "tuscan-farmhouse",
        "title": "Tuscan Farmhouse",
        "source": REPO / "frontend/public/archetypes/buildings/mediterranean_villa_estate",
        "variant_index": 0,
        "variant": "med_villa_tuscan",
        "family": "tuscan-farmhouse-v91",
        "run": ARTIFACT / "run-v2/three-all-surface-stickers-v91-pilot/tuscan-farmhouse-v91",
        "faces": ("front", "left", "rear", "right", "roof"),
        "human_status": "pilot_candidate",
        "known_limit": "The roof is fully skinned but close aerial views retain mild pantile moire.",
    },
    {
        "slug": "egyptian-revival-theater",
        "title": "Egyptian Revival Theater",
        "source": REPO / "frontend/public/archetypes/buildings/deco_theater_mainstreet",
        "variant_index": 2,
        "variant": "deco_theater_egyptian_revival",
        "family": "egyptian-revival-theater-v91",
        "run": ARTIFACT / "run-v7/three-all-surface-stickers-v91-theater-alignment-repair/egyptian-revival-theater-v91",
        "faces": ("front", "left", "rear", "right", "roof"),
        "human_status": "pilot_candidate",
        "known_limit": "Slim physical lotus columns remain deliberately subordinate to the registered facade image.",
    },
    {
        "slug": "belle-epoque-grand-magasin",
        "title": "Belle Epoque Grand Magasin",
        "source": REPO / "frontend/public/archetypes/buildings/grand-magasin",
        "variant_index": 0,
        "variant": "grand-magasin-belle-epoque",
        "family": "belle-epoque-grand-magasin-v91",
        "run": ARTIFACT / "run-v6/three-all-surface-stickers-v91-remaining/belle-epoque-grand-magasin-v91",
        "faces": (
            "front", "front_right", "right", "rear_right", "rear",
            "rear_left", "left", "front_left", "roof",
        ),
        "human_status": "provisional_pilot_candidate",
        "known_limit": "Pale exposed edge strips remain visible at several zinc-roof returns, and the three front entrance backs still read too shallow in the head-on view.",
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


def comparison_board(name: str, reference_role: str, render_roles: tuple[str, str]) -> None:
    cell = (640, 480)
    canvas = Image.new("RGB", (cell[0] * 3, cell[1] * len(BUILDINGS)), (30, 32, 35))
    for row, item in enumerate(BUILDINGS):
        index = item["variant_index"]
        reference_name = f"variant_{index}.png" if reference_role == "street" else f"variant_{index}_{reference_role}.jpg"
        paths = (
            (item["source"] / reference_name, f"{item['title']} - exact {reference_role}"),
            (item["run"] / f"{item['family']}_{render_roles[0]}.png", render_roles[0].replace("_", " ")),
            (item["run"] / f"{item['family']}_{render_roles[1]}.png", render_roles[1].replace("_", " ")),
        )
        for column, (path, label) in enumerate(paths):
            canvas.paste(panel(path, cell, label), (column * cell[0], row * cell[1]))
    canvas.save(OUT / name, optimize=True)


def sticker_atlas(item: dict) -> None:
    cell = (480, 320)
    columns = 3
    rows = (len(item["faces"]) + columns - 1) // columns
    canvas = Image.new("RGB", (cell[0] * columns, cell[1] * rows), (30, 32, 35))
    for offset, face in enumerate(item["faces"]):
        image = panel(PREPARED / item["variant"] / f"{face}.png", cell, f"registered {face} sticker")
        canvas.paste(image, ((offset % columns) * cell[0], (offset // columns) * cell[1]))
    canvas.save(OUT / item["slug"] / "all-surface-sticker-atlas.png", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for item in BUILDINGS:
        target = OUT / item["slug"]
        target.mkdir(parents=True, exist_ok=True)
        index = item["variant_index"]
        copies = {
            "archetype-street.png": item["source"] / f"variant_{index}.png",
            "archetype-oblique.jpg": item["source"] / f"variant_{index}_angle_60.jpg",
            "archetype-roof.jpg": item["source"] / f"variant_{index}_angle_90.jpg",
        }
        for face in item["faces"]:
            copies[f"sticker-{face.replace('_', '-')}.png"] = PREPARED / item["variant"] / f"{face}.png"
        for role in (
            "archetype_match", "street", "front_corner_oblique", "rear_corner_oblique",
            "facade_close", "roof_audit",
        ):
            copies[f"generated-{role.replace('_', '-')}.png"] = item["run"] / f"{item['family']}_{role}.png"
        copies["validation-report.json"] = item["run"] / "validation_report.json"
        copies["surface-finish-report.json"] = item["run"] / "surface_finish_report.json"
        for destination, source in copies.items():
            if not source.exists():
                raise FileNotFoundError(source)
            shutil.copy2(source, target / destination)
        sticker_atlas(item)
        validation = read_json(item["run"] / "validation_report.json")
        finish = read_json(item["run"] / "surface_finish_report.json")
        results.append({
            "building": item["title"],
            "slug": item["slug"],
            "machine_validation": validation.get("status"),
            "surface_finish": finish.get("status"),
            "registered_surface_count": len(item["faces"]),
            "registered_surfaces": list(item["faces"]),
            "human_status": item["human_status"],
            "known_limit": item["known_limit"],
            "architect_review": "pending",
        })

    comparison_board("01-exact-archetype-comparison.png", "street", ("archetype_match", "facade_close"))
    comparison_board("02-oblique-all-elevation-comparison.png", "angle_60", ("front_corner_oblique", "rear_corner_oblique"))
    comparison_board("03-roof-comparison.png", "angle_90", ("roof_audit", "archetype_match"))

    summary = {
        "schema": "three-all-surface-sticker-review@1",
        "pipeline": "v91-all-surface-registered-sticker-landmark",
        "batch_scope": "three never-before-attempted fixed select-and-place landmarks",
        "image_generation": {
            "gpt_image_api_calls": 15,
            "built_in_image_fallbacks": 4,
            "total_authored_surface_stickers": 19,
            "metadata_mode": "disabled",
            "authority": "exact three-view archetype evidence plus selective architectural research",
        },
        "results": results,
    }
    (OUT / "review-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Three All-Surface Sticker Landmarks - V91\n\n"
        "This finite pilot applies the Sticker Method to three catalogue variants that had not previously been built. "
        "Each is a fixed select-and-place landmark: geometry owns silhouette, roof section, projection and true recessed voids; "
        "registered image stickers own visible windows, ornament, material variation and every exposed wall and roof field.\n\n"
        "## Review boards\n\n"
        "- `01-exact-archetype-comparison.png`: exact street reference, image-match render and facade close-up.\n"
        "- `02-oblique-all-elevation-comparison.png`: exact oblique evidence, front corner and rear corner.\n"
        "- `03-roof-comparison.png`: exact aerial evidence, roof audit and image-match render.\n"
        "- Each building folder includes all exact references, every registered surface sticker, a sticker atlas, six render views and machine reports.\n\n"
        "## Bounded generation\n\n"
        "Fifteen bounded GPT Image API calls authored surface-specific stickers. Four missing Grand Magasin surfaces were completed "
        "with the built-in image generator after the external connection failed. Metadata was disabled; exact reference views and "
        "selective primary architectural sources were authoritative.\n\n"
        "## Remaining visible limits\n\n"
        "The batch is a review pilot, not an automatic catalogue release. Tuscan roof texture has mild aerial moire; the Grand Magasin "
        "retains pale seams on several roof construction returns and its front entrance still reads too shallow. These are "
        "disclosed in `review-summary.json` for the architect gate.\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
