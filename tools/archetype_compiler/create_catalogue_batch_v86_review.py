"""Create exact-reference and export-parity boards for one V86 batch checkpoint."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
DEFAULT_BATCH = REPO / "artifacts/catalogue-rollout-v86/pilot-001"
DEFAULT_OUTPUT = REPO / "docs/reviews/catalogue-rollout-v86/pilot-001"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


TITLE, ROW, LABEL, BODY = font(34, bold=True), font(23, bold=True), font(20, bold=True), font(16)


def card(path: Path, size: tuple[int, int], label: str, note: str) -> Image.Image:
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - 72), method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#15191d")
    result.paste(image, (0, 72))
    draw = ImageDraw.Draw(result)
    draw.text((14, 8), label, font=LABEL, fill="#f1eee7")
    draw.text((14, 40), note, font=BODY, fill="#adb8c2")
    return result


def board(title: str, rows: list[tuple[str, list[Image.Image]]], path: Path) -> None:
    gap, margin, header, label_width, row_gap = 14, 22, 70, 285, 24
    card_width, card_height = rows[0][1][0].size
    width = margin * 2 + label_width + 3 * card_width + 2 * gap
    height = header + len(rows) * card_height + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), "#0d1013")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 17), title, font=TITLE, fill="#f6f2e9")
    y = header
    for row_label, cards in rows:
        draw.multiline_text((margin, y + 18), row_label, font=ROW, fill="#f6f2e9", spacing=7)
        x = margin + label_width
        for item in cards:
            canvas.paste(item, (x, y))
            x += card_width + gap
        y += card_height + row_gap
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=95)


def difference(source: Path, roundtrip: Path, size: tuple[int, int], similarity: float, temp: Path) -> Image.Image:
    left = Image.open(source).convert("RGB")
    right = Image.open(roundtrip).convert("RGB").resize(left.size, Image.Resampling.LANCZOS)
    delta = np.abs(np.asarray(left, dtype=np.int16) - np.asarray(right, dtype=np.int16)).mean(axis=2)
    heat = np.zeros((*delta.shape, 3), dtype=np.uint8)
    strength = np.clip(delta * 7.0, 0, 255).astype(np.uint8)
    heat[..., 0] = strength
    heat[..., 1] = (strength * 0.35).astype(np.uint8)
    heat[..., 2] = (255 - strength) // 8
    ImageEnhance.Contrast(Image.fromarray(heat, "RGB")).enhance(1.15).save(temp)
    result = card(temp, size, "Absolute difference", f"{similarity * 100:.2f}% foreground similarity")
    temp.unlink()
    return result


def reference_by_role(grammar: dict, role: str) -> Path:
    references = (grammar.get("massing_graph") or {}).get("reference_views") or []
    item = next(value for value in references if value.get("role") == role)
    return REPO / "frontend/public" / str(item["path"]).lstrip("/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    batch = args.batch.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    index = read_json(batch / "batch-index.json")
    size = (455, 400)
    identity_rows: list[tuple[str, list[Image.Image]]] = []
    roof_rows: list[tuple[str, list[Image.Image]]] = []
    parity_rows: list[tuple[str, list[Image.Image]]] = []
    summaries: list[dict] = []

    for result in index["results"]:
        family = result["family_id"]
        family_dir = batch / family
        grammar = read_json(family_dir / "grammar.json")
        finish = read_json(family_dir / "surface_finish_report.json")
        validation = read_json(family_dir / "validation_report.json")
        similarity = float((finish.get("render_parity") or {}).get("similarity") or 0.0)
        label = str((grammar.get("source") or {}).get("variant_label") or family).replace(" ", "\n", 1)
        identity_rows.append((label, [
            card(reference_by_role(grammar, "street_identity"), size, "Exact archetype", "selected variant identity"),
            card(family_dir / f"{family}_archetype_match.png", size, "V86 generated", "machine pass; human unreviewed"),
            card(family_dir / f"{family}_facade_close.png", size, "V86 façade close", "material, opening and depth audit"),
        ]))
        roof_rows.append((label, [
            card(reference_by_role(grammar, "roof_plan"), size, "Exact roof evidence", "selected variant angle-90"),
            card(family_dir / f"{family}_roof_audit.png", size, "V86 roof audit", "construction and material check"),
            card(family_dir / f"{family}_aerial.png", size, "V86 aerial", "roof plus silhouette read"),
        ]))
        parity_rows.append((label, [
            card(family_dir / "neutral_source.png", size, "Source .blend", "neutral studio render"),
            card(family_dir / "neutral_glb_roundtrip.png", size, "Re-imported GLB", "delivery round trip"),
            difference(family_dir / "neutral_source.png", family_dir / "neutral_glb_roundtrip.png", size, similarity, output / "_difference.png"),
        ]))
        for view in ("archetype_match", "facade_close", "roof_audit", "aerial"):
            shutil.copy2(family_dir / f"{family}_{view}.png", output / f"{family}_{view}.png")
        for report in ("validation_report.json", "surface_finish_report.json", "quality_assessment.json"):
            shutil.copy2(family_dir / report, output / f"{family}_{report}")
        assembled = next(item for item in validation.get("modules") or [] if item.get("role") == "assembled")
        summaries.append({
            "archetype_id": result["archetype_id"],
            "variant_id": result["variant_id"],
            "family_id": family,
            "machine_status": result["machine_status"],
            "human_status": "unreviewed",
            "validation": validation.get("status"),
            "surface_finish": finish.get("status"),
            "foreground_similarity": similarity,
            "assembled_triangles": assembled.get("triangles"),
            "assembled_size_bytes": assembled.get("size_bytes"),
        })

    board("V86 catalogue checkpoint - exact archetype, generated identity and façade", identity_rows, output / "01-archetype-comparison-v86.png")
    board("V86 catalogue checkpoint - exact roof evidence and generated roof", roof_rows, output / "02-roof-comparison-v86.png")
    board("V86 catalogue checkpoint - Blender source vs re-imported GLB", parity_rows, output / "03-neutral-glb-parity-v86.png")
    (output / "review-summary.json").write_text(json.dumps({
        "schema": "catalogue-rollout-review@1",
        "batch_id": index["batch_id"],
        "checkpoint_state": "human_review_required",
        "buildings": summaries,
    }, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
