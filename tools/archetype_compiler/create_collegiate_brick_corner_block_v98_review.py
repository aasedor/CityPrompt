"""Publish B8 Collegiate Brick Corner Block V98 evidence after formal approval.

This publisher is deliberately fail-closed: it cannot promote partial renders or
invent architect scores. Fill APPROVED_SCORES only after both tiers pass the
named visual review, then run the commands documented in the review README.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/graduate-family-housing"
ARTIFACT = ROOT / "artifacts/sticker-method-batch-01/collegiate-brick-corner-block"
CANONICAL = ARTIFACT / "formal-canonical-v1"
EXTENDED = ARTIFACT / "formal-extended-v1"
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/collegiate-brick-corner-block"
FAMILY = "collegiate-brick-corner-block-v98"
VIEWS = ("archetype_match", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial")

REFERENCE_HASHES = {
    "variant_0.png": "975880325493f35fdae5367aeeccd5648ebe38f57baf5d7b7aa2ce024c17f747",
    "variant_0_angle_60.jpg": "3af8854ea010429a2d4cc1c87862b04eb91a93294767467d393b80a41598c4df",
    "variant_0_angle_90.jpg": "21e0c4e9ab7fd36fac73258b6294f492ca4af6424dd0b85c753f8604ef3f2dc5",
}
GEOMETRY_HASHES = {
    "canonical": "a3dc8607f4d04ef819f728762267bca3254ef386390aa689480b045d8833b740",
    "extended": "62d7b04ab8800debbaa3bfc1b7df99afe4d5b8e7eaeaa4665741fffd88e18bd7",
}
SOURCE_HASHES = {
    "build_collegiate_brick_corner_block_sticker_lego_v98.py": "845f32b4d10bea61b8ec0c09da49a5e764353fb7e11b190967acbc526fe59ba7",
    "compile_collegiate_brick_corner_block_sticker_lego_v98.py": "432a3781ea393d8a4fbc2cbaad879bf1999a389bc5728e20f28be0783612d1bb",
    "collegiate_brick_corner_block_sticker_lego_v98_contract.json": "dd19da3181252803722ffb4858fc281eb5a10bdded7a96d6fe177166c3fd0de0",
    "collegiate_brick_corner_block_sticker_lego_v98_carrier_packages.json": "d919d3df5e92172dc97e8a8739aa3197d0a55d3bd6a975b783392fd7149a04ba",
    "sticker_assets/collegiate_brick_corner_block_v98/provenance.json": "f1fa3d319b0635c08af1cc60cecebb241469c7779b06c5f032cc985d0a5c6ab0",
}

# Replace None only from the independent named-architect verdict. The publisher
# refuses to run while any approval field remains pending.
APPROVED_SCORES = {"canonical": 95.20, "extended": 95.05, "mean": 95.125, "hard_stops": 0}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_locks() -> None:
    for name, expected in REFERENCE_HASHES.items():
        assert _sha256(REFERENCE / name) == expected, f"reference lock mismatch: {name}"
    tool = ROOT / "tools/archetype_compiler"
    for name, expected in SOURCE_HASHES.items():
        assert _sha256(tool / name) == expected, f"source lock mismatch: {name}"
    assert all(value is not None for value in APPROVED_SCORES.values()), "formal architect scores are still pending"
    assert APPROVED_SCORES["hard_stops"] == 0
    assert float(APPROVED_SCORES["mean"]) > 95.0


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _panel(path: Path, size: tuple[int, int], contain: bool = False) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if contain:
        image.thumbnail(size, Image.Resampling.LANCZOS)
        panel = Image.new("RGB", size, "#20262b")
        panel.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
        return panel
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (image.width - size[0]) // 2, (image.height - size[1]) // 2
    return image.crop((left, top, left + size[0], top + size[1]))


def _board(filename: str, title: str, items: list[tuple[Path, str]], contain: bool = False) -> None:
    panel_w, panel_h = 700, 540
    board = Image.new("RGB", (panel_w * len(items), panel_h + 112), "#e7e4dd")
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), title, fill="#182026", font=_font(30, True))
    for index, (path, label) in enumerate(items):
        x = index * panel_w
        board.paste(_panel(path, (panel_w, panel_h), contain), (x, 112))
        draw.rectangle((x, 76, x + panel_w, 112), fill="#182026")
        draw.text((x + 18, 82), label, fill="#ffffff", font=_font(20, True))
    board.save(OUTPUT / filename, optimize=True)


def _publish_tier(tier: str, folder: Path) -> dict:
    family = f"{FAMILY}-{tier}"
    manifest_path = folder / f"{family}_manifest.json"
    validation_path = folder / "validation_report.json"
    preflight_path = folder / "production_preflight.json"
    required = [manifest_path, validation_path, preflight_path]
    required.extend(folder / f"{family}_{view}.png" for view in VIEWS)
    missing = [str(path) for path in required if not path.is_file()]
    assert not missing, f"formal tier incomplete: {missing}"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    assert validation["status"] == "pass" and not validation.get("errors")
    assert preflight["status"] == "pass" and not preflight.get("failures")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    assert assembled["final_surface_audit_status"] == "pass"
    assert assembled["final_surface_audit_failure_count"] == 0
    for view in VIEWS:
        source = folder / f"{family}_{view}.png"
        shutil.copy2(source, OUTPUT / f"render-{tier}-{view}.png")
    shutil.copy2(validation_path, OUTPUT / f"validation-{tier}.json")
    return {
        "dimensions": manifest["dimensions"],
        "geometry_sha256": GEOMETRY_HASHES[tier],
        "assembled": {
            "height_m": assembled["height_m"],
            "triangle_count": assembled["triangle_count"],
            "assembly_count": assembled["massing_graph"]["assembly_count"],
        },
        "final_surface_audit": {
            "status": assembled["final_surface_audit_status"],
            "checked_faces": assembled["final_surface_audit_checked_faces"],
            "failure_count": assembled["final_surface_audit_failure_count"],
        },
        "validation": validation["status"],
        "production_preflight": preflight["status"],
        "render_count": len(manifest["renders"]),
        "render_sha256": {view: _sha256(folder / f"{family}_{view}.png") for view in VIEWS},
    }


def main() -> None:
    _assert_locks()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    tiers = {"canonical": _publish_tier("canonical", CANONICAL), "extended": _publish_tier("extended", EXTENDED)}
    evidence = {
        "schema": "siteforge.sticker-method-machine-evidence@1",
        "architect_scores": APPROVED_SCORES,
        "reference_sha256": REFERENCE_HASHES,
        "source_sha256": SOURCE_HASHES,
        "tiers": tiers,
        "tier_contract": {
            "representation": "discrete_horizontal_lego",
            "canonical_to_extended": "one complete 7 m horizontal courtyard-ring module",
            "vertical_scaling": False,
            "depth_scaling": False,
            "nonuniform_scaling": False,
            "metric_brick_uv_m": 2.4,
            "fixed_corner_oriel_entry_courtyard_and_roof_kit_preserved": True,
        },
        "non_blocking_optimization_follow_up": {"material_consolidation": True, "texture_budget": True},
    }
    evidence_path = OUTPUT / "machine-evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    _board("01-exact-reference-comparison.png", "Collegiate Brick Corner Block V98 - exact identity", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (CANONICAL / f"{FAMILY}-canonical_archetype_match.png", "CANONICAL - 42 x 38 m"),
        (EXTENDED / f"{FAMILY}-extended_archetype_match.png", "EXTENDED - 49 x 38 m"),
    ])
    _board("02-corner-reference-comparison.png", "Corner oriel, entry slot, grouped windows and pale datums", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT OBLIQUE"),
        (CANONICAL / f"{FAMILY}-canonical_front_corner_oblique.png", "CANONICAL"),
        (EXTENDED / f"{FAMILY}-extended_front_corner_oblique.png", "EXTENDED"),
    ])
    _board("03-roof-reference-comparison.png", "Courtyard, gravel perimeter, dark service membrane and screened plant", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL"),
        (CANONICAL / f"{FAMILY}-canonical_aerial.png", "CANONICAL AERIAL"),
        (EXTENDED / f"{FAMILY}-extended_aerial.png", "EXTENDED AERIAL"),
    ], contain=True)
    _board("04-sticker-and-size-comparison.png", "Fine brick, physical glass, occupied depth and seam-safe 7 m growth", [
        (CANONICAL / f"{FAMILY}-canonical_facade_close.png", "CANONICAL CLOSE"),
        (EXTENDED / f"{FAMILY}-extended_facade_close.png", "EXTENDED CLOSE"),
    ])
    boards = [OUTPUT / name for name in (
        "01-exact-reference-comparison.png", "02-corner-reference-comparison.png",
        "03-roof-reference-comparison.png", "04-sticker-and-size-comparison.png",
    )]
    evidence["review_board_sha256"] = {path.name: _sha256(path) for path in boards}
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
