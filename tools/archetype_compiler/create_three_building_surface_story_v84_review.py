"""Build the bounded V78-versus-V84 three-building review package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "artifacts/five-building-v78"
PILOT = REPO / "artifacts/three-building-surface-story-v84"
REFERENCE = REPO / "frontend/public/archetypes/buildings"
OUTPUT = REPO / "docs/reviews/three-building-surface-story-v84"

BUILDINGS = [
    {
        "label": "Neoclassical Courthouse",
        "reference": "monumental_courthouse_axis",
        "baseline_dir": "courthouse-neoclassical-v78",
        "baseline_family": "courthouse-neoclassical-v78",
        "pilot_dir": "courthouse-neoclassical-surface-story-v84",
        "pilot_family": "courthouse-neoclassical-surface-story-v84",
        "status": "surface keeper; archetype provisional",
        "finding": "Granite and standing-seam copper now read as separate construction systems; sculpted pediment and capital identity remain simplified.",
    },
    {
        "label": "Italian Portici",
        "reference": "mediterranean_arcade_mixed_use",
        "baseline_dir": "mediterranean-portici-v78",
        "baseline_family": "mediterranean-portici-v78",
        "pilot_dir": "mediterranean-portici-surface-story-v84",
        "pilot_family": "mediterranean-portici-surface-story-v84",
        "status": "keeper candidate",
        "finding": "The pantile roof, ochre wall and stone arcade are construction-role congruent; deeper occupied shops and eave detail are the main remaining gains.",
    },
    {
        "label": "Romanesque Warehouse",
        "reference": "romanesque_revival_warehouse",
        "baseline_dir": "romanesque-warehouse-v78",
        "baseline_family": "romanesque-warehouse-v78",
        "pilot_dir": "romanesque-warehouse-surface-story-v84",
        "pilot_family": "romanesque-warehouse-surface-story-v84",
        "status": "visual provisional; export parity fail",
        "finding": "Darker wall brick, brownstone and roof membrane improve material truth, but export parity fails and the loading-arcade cadence still needs a fixed identity pass.",
    },
]


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE = font(34, bold=True)
ROW = font(25, bold=True)
LABEL = font(21, bold=True)
BODY = font(17)


def card(path: Path, size: tuple[int, int], label: str, note: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image = ImageOps.fit(image, (size[0], size[1] - 72), method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#15191d")
    result.paste(image, (0, 72))
    draw = ImageDraw.Draw(result)
    draw.text((14, 8), label, font=LABEL, fill="#f1eee7")
    draw.text((14, 40), note, font=BODY, fill="#adb8c2")
    return result


def grid_board(title: str, rows: list[tuple[str, list[Image.Image]]], destination: Path) -> None:
    gap = 14
    margin = 22
    header = 70
    row_label_width = 260
    row_gap = 24
    card_width = rows[0][1][0].width
    card_height = rows[0][1][0].height
    column_count = len(rows[0][1])
    width = margin * 2 + row_label_width + column_count * card_width + (column_count - 1) * gap
    height = header + margin + len(rows) * card_height + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), "#0d1013")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 17), title, font=TITLE, fill="#f6f2e9")
    y = header
    for row_label, cards in rows:
        draw.multiline_text((margin, y + 18), row_label, font=ROW, fill="#f6f2e9", spacing=7)
        x = margin + row_label_width
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
    temp = OUTPUT / "_difference.png"
    image.save(temp)
    result = card(temp, size, "Absolute difference", f"{similarity * 100:.2f}% building-foreground similarity")
    temp.unlink()
    return result


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    comparison_size = (455, 400)
    archetype_rows = []
    roof_rows = []
    parity_rows = []
    summary_buildings = []

    for building in BUILDINGS:
        reference_dir = REFERENCE / building["reference"]
        baseline_dir = BASELINE / building["baseline_dir"]
        pilot_dir = PILOT / building["pilot_dir"]
        baseline_family = building["baseline_family"]
        pilot_family = building["pilot_family"]
        report = json.loads((pilot_dir / "surface_finish_report.json").read_text(encoding="utf-8"))
        similarity = float(report["render_parity"]["similarity"])

        archetype_rows.append((building["label"], [
            card(reference_dir / "variant_0.png", comparison_size, "Exact archetype", "selected catalogue identity view"),
            card(baseline_dir / f"{baseline_family}_archetype_match.png", comparison_size, "V78 baseline", "same massing and camera"),
            card(pilot_dir / f"{pilot_family}_archetype_match.png", comparison_size, "V84 surface story", building["status"]),
        ]))
        roof_rows.append((building["label"], [
            card(reference_dir / "variant_0_angle_90.jpg", comparison_size, "Exact roof evidence", "construction-role authority"),
            card(baseline_dir / f"{baseline_family}_roof_audit.png", comparison_size, "V78 roof audit", "generic or weak surface role"),
            card(pilot_dir / f"{pilot_family}_roof_audit.png", comparison_size, "V84 roof audit", "role-locked baked PBR"),
        ]))
        parity_rows.append((building["label"], [
            card(pilot_dir / "neutral_source.png", comparison_size, "Source .blend", "neutral studio render"),
            card(pilot_dir / "neutral_glb_roundtrip.png", comparison_size, "Re-imported GLB", "catalogue export round trip"),
            difference_card(pilot_dir / "neutral_source.png", pilot_dir / "neutral_glb_roundtrip.png", comparison_size, similarity),
        ]))

        for view in ("archetype_match", "aerial", "facade_close"):
            shutil.copy2(pilot_dir / f"{pilot_family}_{view}.png", OUTPUT / f"{pilot_family}_{view}.png")
        shutil.copy2(pilot_dir / "surface_finish_report.json", OUTPUT / f"{pilot_family}_surface_finish_report.json")
        summary_buildings.append({
            "label": building["label"],
            "status": building["status"],
            "surface_audit": report["status"],
            "glb_roundtrip_similarity": similarity,
            "finding": building["finding"],
        })

    grid_board("V84 surface-story generalization - exact archetype vs controlled baseline", archetype_rows, OUTPUT / "01-archetype-baseline-v84.png")
    grid_board("V84 construction-role roof check - exact evidence vs pipeline", roof_rows, OUTPUT / "02-roof-baseline-v84.png")
    grid_board("V84 neutral export QA - Blender source vs re-imported GLB", parity_rows, OUTPUT / "03-neutral-glb-parity-v84.png")
    (OUTPUT / "review-summary.json").write_text(json.dumps({
        "schema": "three-building-surface-story-review@1",
        "pipeline_version": "v84",
        "batch_status": "bounded_generalization_mixed",
        "texture_resolution_px": 1024,
        "buildings": summary_buildings,
        "methodology_lessons": [
            "A surface source must match the construction role and pattern, not merely the material family or colour.",
            "1024 px baked PBR sets preserved visible quality while keeping all three assembled GLBs below the 8 MB delivery target.",
            "Surface approval and archetype-identity approval remain separate; missing fixed geometry cannot be replaced by stronger texture noise.",
        ],
    }, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
