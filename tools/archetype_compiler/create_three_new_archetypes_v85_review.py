"""Build the bounded exact-reference review package for the three new V85 pilots."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "artifacts/three-new-archetypes-v85"
REFERENCE = REPO / "frontend/public/archetypes/buildings"
OUTPUT = REPO / "docs/reviews/three-new-archetypes-v85"

BUILDINGS = [
    {
        "label": "Classic Brownstone\nStreetwall",
        "reference": "classic_brownstone_streetwall",
        "directory": "classic-brownstone-traditional-v85",
        "family": "classic-brownstone-traditional-v85",
        "status": "keeper candidate",
        "finding": "Three physical stoops, party-wall roof divisions, chimneys and carved trim preserve the attached-house identity; the pale roof correction now matches the aerial evidence.",
    },
    {
        "label": "Blue Curtain-Wall\nOffice",
        "reference": "modern_glass_office_institutional",
        "directory": "blue-curtainwall-office-v85",
        "family": "blue-curtainwall-office-v85",
        "status": "conditional pilot",
        "finding": "Layered glazing, occupied interior depth and a screened mechanical roof avoid plastic glass, but the inherited façade sheet overstates the opaque metal-panel zone relative to the exact photo.",
    },
    {
        "label": "Nordic Mass-Timber\nMid-Rise",
        "reference": "nordic_timber_midrise",
        "directory": "nordic-mass-timber-midrise-v85",
        "family": "nordic-mass-timber-midrise-v85",
        "status": "keeper candidate",
        "finding": "The corrected pass removes redundant projecting frames and keeps the expressed glulam grid, recessed loggia read, larch infill, sedum terrace and roof pavilion.",
    },
]


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


TITLE = font(34, bold=True)
ROW = font(24, bold=True)
LABEL = font(20, bold=True)
BODY = font(16)


def card(path: Path, size: tuple[int, int], label: str, note: str) -> Image.Image:
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - 72), method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#15191d")
    result.paste(image, (0, 72))
    draw = ImageDraw.Draw(result)
    draw.text((14, 8), label, font=LABEL, fill="#f1eee7")
    draw.text((14, 40), note, font=BODY, fill="#adb8c2")
    return result


def board(title: str, rows: list[tuple[str, list[Image.Image]]], destination: Path) -> None:
    gap, margin, header, label_width, row_gap = 14, 22, 70, 280, 24
    card_width, card_height = rows[0][1][0].size
    columns = len(rows[0][1])
    width = margin * 2 + label_width + columns * card_width + (columns - 1) * gap
    height = header + len(rows) * card_height + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), "#0d1013")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 17), title, font=TITLE, fill="#f6f2e9")
    y = header
    for label, cards in rows:
        draw.multiline_text((margin, y + 18), label, font=ROW, fill="#f6f2e9", spacing=8)
        x = margin + label_width
        for item in cards:
            canvas.paste(item, (x, y))
            x += card_width + gap
        y += card_height + row_gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=95)


def difference_card(source: Path, roundtrip: Path, size: tuple[int, int], similarity: float) -> Image.Image:
    left = Image.open(source).convert("RGB")
    right = Image.open(roundtrip).convert("RGB").resize(left.size, Image.Resampling.LANCZOS)
    delta = np.abs(np.asarray(left, dtype=np.int16) - np.asarray(right, dtype=np.int16)).mean(axis=2)
    heat = np.zeros((*delta.shape, 3), dtype=np.uint8)
    strength = np.clip(delta * 7.0, 0, 255).astype(np.uint8)
    heat[..., 0] = strength
    heat[..., 1] = (strength * 0.35).astype(np.uint8)
    heat[..., 2] = (255 - strength) // 8
    image = ImageEnhance.Contrast(Image.fromarray(heat, "RGB")).enhance(1.15)
    temporary = OUTPUT / "_difference.png"
    image.save(temporary)
    result = card(temporary, size, "Absolute difference", f"{similarity * 100:.2f}% foreground similarity")
    temporary.unlink()
    return result


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    size = (455, 400)
    identity_rows: list[tuple[str, list[Image.Image]]] = []
    roof_rows: list[tuple[str, list[Image.Image]]] = []
    parity_rows: list[tuple[str, list[Image.Image]]] = []
    summary: list[dict] = []

    for building in BUILDINGS:
        reference = REFERENCE / building["reference"]
        pilot = PILOT / building["directory"]
        family = building["family"]
        finish = json.loads((pilot / "surface_finish_report.json").read_text(encoding="utf-8"))
        validation = json.loads((pilot / "validation_report.json").read_text(encoding="utf-8"))
        similarity = float(finish["render_parity"]["similarity"])
        assembled = next(item for item in validation["modules"] if item.get("role") == "assembled")

        identity_rows.append((building["label"], [
            card(reference / "variant_0.png", size, "Exact archetype", "catalogue identity image"),
            card(pilot / f"{family}_archetype_match.png", size, "V85 generated", building["status"]),
            card(pilot / f"{family}_facade_close.png", size, "V85 façade close", "material and depth audit"),
        ]))
        roof_rows.append((building["label"], [
            card(reference / "variant_0_angle_90.jpg", size, "Exact roof evidence", "catalogue angle-90 image"),
            card(pilot / f"{family}_roof_audit.png", size, "V85 roof audit", "top-down construction check"),
            card(pilot / f"{family}_aerial.png", size, "V85 aerial", "roof plus silhouette read"),
        ]))
        parity_rows.append((building["label"], [
            card(pilot / "neutral_source.png", size, "Source .blend", "neutral studio render"),
            card(pilot / "neutral_glb_roundtrip.png", size, "Re-imported GLB", "catalogue export round trip"),
            difference_card(pilot / "neutral_source.png", pilot / "neutral_glb_roundtrip.png", size, similarity),
        ]))

        for view in ("archetype_match", "facade_close", "roof_audit", "aerial"):
            shutil.copy2(pilot / f"{family}_{view}.png", OUTPUT / f"{family}_{view}.png")
        shutil.copy2(pilot / "surface_finish_report.json", OUTPUT / f"{family}_surface_finish_report.json")
        summary.append({
            "label": building["label"].replace("\n", " "),
            "status": building["status"],
            "validation": validation["status"],
            "validation_warning_count": len(validation["warnings"]),
            "surface_audit": finish["status"],
            "glb_roundtrip_similarity": similarity,
            "assembled_triangles": assembled["triangles"],
            "assembled_size_bytes": assembled["size_bytes"],
            "finding": building["finding"],
        })

    board("V85 new archetypes - exact image, generated identity and façade detail", identity_rows, OUTPUT / "01-archetype-comparison-v85.png")
    board("V85 roof fidelity - exact aerial evidence, roof audit and generated aerial", roof_rows, OUTPUT / "02-roof-comparison-v85.png")
    board("V85 neutral export QA - Blender source vs re-imported GLB", parity_rows, OUTPUT / "03-neutral-glb-parity-v85.png")
    payload = {
        "schema": "three-new-archetypes-review@1",
        "pipeline_version": "v85",
        "batch_status": "two_keeper_candidates_one_conditional",
        "buildings": summary,
        "methodology_lessons": [
            "Baked albedo is authoritative: a declared material base colour does not repair a roof texture whose actual pixels have the wrong value.",
            "One architectural feature needs one owning representation; duplicating loggias in both the façade sheet and projecting geometry creates floating cages.",
            "Automated geometry, PBR and export checks are necessary but cannot detect an archetype-specific façade-sheet composition mismatch.",
        ],
    }
    (OUTPUT / "review-summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
