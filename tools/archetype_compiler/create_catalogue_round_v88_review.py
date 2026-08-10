"""Build mandatory V88 archetype, six-view, roof, and release-gate evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
DEFAULT_BUILDS = REPO / "artifacts/catalogue-rollout-v88/round-001/builds"
DEFAULT_OUTPUT = REPO / "docs/reviews/catalogue-rollout-v88/round-001"
BATCHES = ("round-001-v88-a", "round-001-v88-b")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


TITLE, ROW, LABEL, BODY = font(34, bold=True), font(22, bold=True), font(19, bold=True), font(15)


def card(path: Path, size: tuple[int, int], label: str, note: str) -> Image.Image:
    source = Image.open(path).convert("RGB")
    image = ImageOps.fit(source, (size[0], size[1] - 68), method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, "#15191d")
    result.paste(image, (0, 68))
    draw = ImageDraw.Draw(result)
    draw.text((12, 7), label, font=LABEL, fill="#f1eee7")
    draw.text((12, 37), note, font=BODY, fill="#adb8c2")
    return result


def board(title: str, rows: list[tuple[str, list[Image.Image]]], path: Path) -> None:
    gap, margin, header, label_width, row_gap = 12, 20, 66, 245, 18
    card_width, card_height = rows[0][1][0].size
    columns = max(len(cards) for _label, cards in rows)
    width = margin * 2 + label_width + columns * card_width + (columns - 1) * gap
    height = header + len(rows) * card_height + (len(rows) - 1) * row_gap
    canvas = Image.new("RGB", (width, height), "#0d1013")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), title, font=TITLE, fill="#f6f2e9")
    y = header
    for row_label, cards in rows:
        draw.multiline_text((margin, y + 16), row_label, font=ROW, fill="#f6f2e9", spacing=6)
        x = margin + label_width
        for item in cards:
            canvas.paste(item, (x, y))
            x += card_width + gap
        y += card_height + row_gap
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=94)


def reference(grammar: dict[str, Any], role: str) -> Path:
    item = next(value for value in (grammar.get("massing_graph") or {}).get("reference_views") or [] if value.get("role") == role)
    return REPO / "frontend/public" / str(item["path"]).lstrip("/")


def check_report(family_dir: Path, grammar: dict[str, Any], machine: dict[str, Any]) -> dict[str, Any]:
    validation_path = family_dir / "validation_report.json"
    finish_path = family_dir / "surface_finish_report.json"
    validation = read_json(validation_path) if validation_path.exists() else {"status": "missing"}
    finish = read_json(finish_path) if finish_path.exists() else {"status": "missing"}
    references = [reference(grammar, role) for role in ("street_identity", "oblique_massing", "roof_plan")]
    views = {
        name: family_dir / f"{family_dir.name}_{name}.png"
        for name in ("street", "front_corner_oblique", "roof_audit", "rear_corner_oblique", "facade_close", "archetype_match")
    }
    workflow = (grammar.get("architectural_signature") or {}).get("production_contract", {}).get("stage_workflow", {})
    required = workflow.get("required_stages") or {}
    stages = {
        "reference_sufficiency": {"passed": all(path.exists() for path in references), "evidence": [str(path.relative_to(REPO)).replace("\\", "/") for path in references]},
        "representation_selection": {"passed": workflow.get("representation") in {"massing_graph", "curve_native"}, "evidence": workflow.get("representation")},
        "clay_massing": {"passed": (family_dir / "neutral_source.png").exists(), "evidence": "neutral_source.png"},
        "roof_and_voids": {"passed": views["roof_audit"].exists() and views["facade_close"].exists(), "evidence": [views["roof_audit"].name, views["facade_close"].name]},
        "medium_detail": {"passed": views["facade_close"].exists(), "evidence": views["facade_close"].name},
        "retopology": {"passed": validation.get("status") == "pass", "evidence": validation_path.name},
        "manual_uv_audit": {"passed": finish.get("status") == "pass", "evidence": finish_path.name},
        "material_bake": {"passed": finish.get("status") == "pass", "evidence": finish_path.name},
        "export_parity": {"passed": bool((finish.get("render_parity") or {}).get("passed")), "evidence": ["neutral_source.png", "neutral_glb_roundtrip.png"]},
        "architect_review": {"passed": False, "evidence": "architect-review.json"},
    }
    missing_declarations = sorted(set(stages) - set(required))
    hard_stops = [name for name, result in stages.items() if name != "architect_review" and not result["passed"]]
    return {
        "schema": "catalogue-v88-stage-gate@1",
        "family_id": family_dir.name,
        "machine_status": machine.get("machine_status", "missing"),
        "architect_threshold": int(workflow.get("architect_release_score", 85)),
        "mandatory_stage_declarations_complete": not missing_declarations,
        "missing_stage_declarations": missing_declarations,
        "hard_stops": hard_stops,
        "stages": stages,
        "release_status": "blocked_pending_architect_review" if not hard_stops else "blocked_repair_required",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--builds", type=Path, default=DEFAULT_BUILDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    builds, output = args.builds.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    all_summaries: list[dict[str, Any]] = []
    size = (430, 380)

    for batch_name in BATCHES:
        batch = builds / batch_name
        index = read_json(batch / "batch-index.json")
        identity_rows: list[tuple[str, list[Image.Image]]] = []
        roof_rows: list[tuple[str, list[Image.Image]]] = []
        for machine in index["results"]:
            family = str(machine["family_id"])
            family_dir = batch / family
            grammar = read_json(family_dir / "grammar.json")
            label = str((grammar.get("source") or {}).get("variant_label") or family).replace(" ", "\n", 1)
            identity_rows.append((label, [
                card(reference(grammar, "street_identity"), size, "Exact archetype", "identity-authoritative image"),
                card(family_dir / f"{family}_archetype_match.png", size, "V88 generated", "clean identity camera"),
                card(family_dir / f"{family}_facade_close.png", size, "Facade close", "glass, depth, UV and detail"),
            ]))
            roof_rows.append((label, [
                card(reference(grammar, "roof_plan"), size, "Exact roof evidence", "image-authoritative roof angle"),
                card(family_dir / f"{family}_roof_audit.png", size, "V88 roof audit", "isolated construction view"),
                card(family_dir / f"{family}_rear_corner_oblique.png", size, "Rear/side", "non-hero-face depth audit"),
            ]))
            six_views = [
                ("Street", "street"), ("Oblique", "front_corner_oblique"), ("Roof", "roof_audit"),
                ("Identity", "archetype_match"), ("Rear", "rear_corner_oblique"), ("Close-up", "facade_close"),
            ]
            view_rows = []
            for row in range(2):
                cards = [card(family_dir / f"{family}_{view}.png", size, label_text, "mandatory architect view") for label_text, view in six_views[row * 3:(row + 1) * 3]]
                view_rows.append((family if row == 0 else "", cards))
            board(f"V88 mandatory six-view review - {family}", view_rows, output / f"{family}-six-view.png")
            report = check_report(family_dir, grammar, machine)
            (output / f"{family}-stage-gates.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            all_summaries.append(report)
        suffix = "a" if batch_name.endswith("-a") else "b"
        board(f"V88 batch {suffix.upper()} - exact archetype, generated identity and facade", identity_rows, output / f"01-archetype-comparison-v88-{suffix}.png")
        board(f"V88 batch {suffix.upper()} - exact roof, roof audit and rear depth", roof_rows, output / f"02-roof-depth-comparison-v88-{suffix}.png")

    (output / "stage-gate-summary.json").write_text(json.dumps({
        "schema": "catalogue-v88-stage-gate-summary@1",
        "release_threshold": 85,
        "release_status": "blocked_pending_architect_review",
        "buildings": all_summaries,
    }, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
