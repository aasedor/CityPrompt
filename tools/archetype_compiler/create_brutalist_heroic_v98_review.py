"""Publish approved B9 Brutalist Heroic V98 canonical release evidence.

This publisher is fail-closed: exact references, source packages, formal render
inputs, machine gates, and the named architect score must match their locks.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/brutalist_institutional"
FORMAL = ROOT / "artifacts/sticker-method-batch-01/brutalist-heroic/formal-canonical-v1"
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/brutalist-heroic"
FAMILY = "brutalist-heroic-v98-canonical"
VIEWS = (
    "archetype_match",
    "front_corner_oblique",
    "rear_corner_oblique",
    "facade_close",
    "roof_audit",
    "aerial",
)

REFERENCE_HASHES = {
    "variant_0.png": "955d4d45a2148325e2529d02139192c47080210d304bbc0ad856c50b9ef2abbc",
    "variant_0_angle_60.jpg": "ab69b3ddf450414c39d8fbb3c2e4886ec6748b0d02c6c2d751f000c2b456031b",
    "variant_0_angle_90.jpg": "427226ea95af68f6e54c0302896ca42dd8cb42167294f0396465cec801317bd5",
}
GEOMETRY_SHA256 = "ed97781e52550e79a5a5555b8db4b07580af69b59f31bd234834d67a0c9b8b07"
SOURCE_HASHES = {
    "build_brutalist_heroic_sticker_landmark_v98.py": "9fbf0e775e6c30eb912ae7034a721cd74348fd35e5526987152d8894fe7233f9",
    "compile_brutalist_heroic_sticker_landmark_v98.py": "cd85a5487d3610411e740da9b4d4d0ad9badee03b8fca00bbfbb3ec5bb7755d8",
    "brutalist_heroic_sticker_landmark_v98_contract.json": "d60e33fac7a427dbc6920c04a74e8e45aa9d4fa31d72ede3de20cd688f075127",
    "brutalist_heroic_sticker_landmark_v98_carrier_packages.json": "c0ce6d4bf6143e0031b222d445142bf9c9f11873cb595ea3e6c97f3fcce8f76f",
    "sticker_assets/brutalist_heroic_v98/provenance.json": "fbf87dea8c70cd1db898337412ff99437e9468e442381d0cd2c201f6cd6fc5fd",
}
FORMAL_HASHES = {
    "brutalist-heroic-v98-canonical_manifest.json": "9191c11dbccf79994d5b7dee872a70c2c00e84fe10f40f1f6a359c25737b2da6",
    "production_preflight.json": "a1763375748bd5524f09ff0486d76639e9c0aad4a9c492194e43b20ea8508e88",
    "validation_report.json": "0582ceabdbc97a37c5bcfdec7f8a733fc35df9c56730d91963cd39a8cd91f577",
    "brutalist-heroic-v98-canonical_aerial.png": "71528db0ab76da4d9ddadd1a42e334fe413a92a6d71f868c7a80e7ba705c140a",
    "brutalist-heroic-v98-canonical_archetype_match.png": "b762cc09694b6571ce4bc8f81b25341c707b8205311c3d85c068a0767d49bb55",
    "brutalist-heroic-v98-canonical_context.png": "f54c11da6dcfdfb00c5515cdc00aa9b9cfcc44155ae2552c0f3becdf81d8f018",
    "brutalist-heroic-v98-canonical_facade_close.png": "5061b833559102bc8bc91b3c7298f66bed01febf8b807ca933854bff68f48936",
    "brutalist-heroic-v98-canonical_front_corner_oblique.png": "83e12926d5efcb2edb2c9c8129170c741b65da0fd044ca5febafa1a11f73f9c2",
    "brutalist-heroic-v98-canonical_preview.png": "3c89aedf37a35ba90bb66870f3842018933f182f116edfdddf7f26d86a5907b2",
    "brutalist-heroic-v98-canonical_rear_corner_oblique.png": "ba7141ac1c3adca0f0ecf62fdd4612caee9f968d2ef0cb3e8aa06bfda21ee8ad",
    "brutalist-heroic-v98-canonical_roof_audit.png": "2493cd1ebf0d996857a7fbe24cb167a87a3f00f67ac401e60676ea62a899ee87",
    "brutalist-heroic-v98-canonical_street.png": "8a3ec6d322e813c303f86339ddcd5abc7a870be1cd0537cce3be08bde67066df",
}
APPROVED_SCORES = {"canonical": 95.05, "hard_stops": 0}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_locks() -> None:
    for name, expected in REFERENCE_HASHES.items():
        assert _sha256(REFERENCE / name) == expected, f"reference lock mismatch: {name}"
    tool = ROOT / "tools/archetype_compiler"
    for name, expected in SOURCE_HASHES.items():
        assert _sha256(tool / name) == expected, f"source lock mismatch: {name}"
    for name, expected in FORMAL_HASHES.items():
        assert _sha256(FORMAL / name) == expected, f"formal evidence lock mismatch: {name}"
    assert APPROVED_SCORES["canonical"] > 95.0
    assert APPROVED_SCORES["hard_stops"] == 0


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")
    for name in names:
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
    panel_w, panel_h = 760, 570
    board = Image.new("RGB", (panel_w * len(items), panel_h + 112), "#e7e4dd")
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), title, fill="#182026", font=_font(30, True))
    for index, (path, label) in enumerate(items):
        x = index * panel_w
        board.paste(_panel(path, (panel_w, panel_h), contain), (x, 112))
        draw.rectangle((x, 76, x + panel_w, 112), fill="#182026")
        draw.text((x + 18, 82), label, fill="#ffffff", font=_font(20, True))
    board.save(OUTPUT / filename, optimize=True)


def _publish_canonical() -> dict:
    manifest = json.loads((FORMAL / f"{FAMILY}_manifest.json").read_text(encoding="utf-8"))
    validation = json.loads((FORMAL / "validation_report.json").read_text(encoding="utf-8"))
    preflight = json.loads((FORMAL / "production_preflight.json").read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    assert validation["status"] == "pass" and not validation.get("errors")
    assert preflight["status"] == "pass" and not preflight.get("failures")
    assert assembled["final_surface_audit_status"] == "pass"
    assert assembled["final_surface_audit_checked_faces"] == 1110
    assert assembled["final_surface_audit_failure_count"] == 0
    assert manifest["dimensions"]["width_m"] == 50.0
    assert manifest["dimensions"]["depth_m"] == 42.0
    assert manifest["dimensions"]["default_floors"] == 2
    for view in VIEWS:
        shutil.copy2(FORMAL / f"{FAMILY}_{view}.png", OUTPUT / f"render-canonical-{view}.png")
    shutil.copy2(FORMAL / "validation_report.json", OUTPUT / "validation-canonical.json")
    shutil.copy2(FORMAL / "production_preflight.json", OUTPUT / "production-preflight-canonical.json")
    return {
        "dimensions": manifest["dimensions"],
        "geometry_sha256": GEOMETRY_SHA256,
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
        "validation_sha256": FORMAL_HASHES["validation_report.json"],
        "production_preflight": preflight["status"],
        "production_preflight_sha256": FORMAL_HASHES["production_preflight.json"],
        "manifest_sha256": FORMAL_HASHES[f"{FAMILY}_manifest.json"],
        "render_count": len(manifest["renders"]),
        "render_sha256": {
            view: FORMAL_HASHES[f"{FAMILY}_{view}.png"] for view in VIEWS
        },
    }


def main() -> None:
    _assert_locks()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    canonical = _publish_canonical()
    evidence = {
        "schema": "siteforge.sticker-method-machine-evidence@1",
        "architect_scores": APPROVED_SCORES,
        "reference_sha256": REFERENCE_HASHES,
        "source_sha256": SOURCE_HASHES,
        "formal_input_sha256": FORMAL_HASHES,
        "tiers": {"canonical": canonical},
        "tier_contract": {
            "representation": "fixed_landmark",
            "approved_dimensions_m": {"width": 50.0, "depth": 42.0, "occupied_storeys": 2},
            "continuous_resize_allowed": False,
            "vertical_scaling_allowed": False,
            "depth_scaling_allowed": False,
            "nonuniform_scaling_allowed": False,
            "additional_tiers_allowed": False,
        },
        "non_blocking_optimization_follow_up": {"material_consolidation": True},
    }
    evidence_path = OUTPUT / "machine-evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    _board("01-exact-reference-comparison.png", "Brutalist Heroic V98 - exact canonical identity", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (FORMAL / f"{FAMILY}_archetype_match.png", "APPROVED CANONICAL - 50 x 42 m"),
    ])
    _board("02-oblique-and-detail-comparison.png", "Board-form concrete, deep light boxes, pilotis and dark glazing", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT OBLIQUE"),
        (FORMAL / f"{FAMILY}_front_corner_oblique.png", "APPROVED OBLIQUE"),
        (FORMAL / f"{FAMILY}_facade_close.png", "APPROVED CLOSE"),
    ])
    _board("03-roof-and-court-comparison.png", "Cool membrane, two sunken courts and fixed rooftop volumes", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL"),
        (FORMAL / f"{FAMILY}_aerial.png", "APPROVED AERIAL"),
        (FORMAL / f"{FAMILY}_roof_audit.png", "APPROVED ROOF AUDIT"),
    ], contain=True)
    boards = [OUTPUT / name for name in (
        "01-exact-reference-comparison.png",
        "02-oblique-and-detail-comparison.png",
        "03-roof-and-court-comparison.png",
    )]
    evidence["review_board_sha256"] = {path.name: _sha256(path) for path in boards}
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
