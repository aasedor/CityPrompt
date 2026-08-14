"""Publish approved B10 Historic Iron-and-Glass Market Hall V98 evidence.

This publisher is fail-closed. It locks the three exact references, geometry,
compiler outputs, intrinsic-asset provenance, formal Cycles evidence, named
architect score, and catalogue orders 1-9 before promoting order 10.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/archetype_compiler"
REFERENCE = ROOT / "frontend/public/archetypes/buildings/food_hall_market_hall"
FORMAL = ROOT / "artifacts/sticker-method-batch-01/market-historic-iron-glass/formal-canonical-v1"
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/market-historic-iron-glass"
BATCH = TOOL / "sticker_method_batch_01.json"
FAMILY = "market-historic-iron-glass-v98-canonical"
VIEWS = (
    "archetype_match",
    "front_corner_oblique",
    "rear_corner_oblique",
    "facade_close",
    "roof_audit",
    "aerial",
)

REFERENCE_HASHES = {
    "variant_0.png": "0f04fa934c3b2883f82b3a27ba6883639aff8ab57a065e6b11fbe9c1afe13659",
    "variant_0_angle_60.jpg": "e504ab5a6c2af9141b0445d560a77d560d96b5e826949fec9be380f4d58d4c6a",
    "variant_0_angle_90.jpg": "af24f5150a12d417f07ae2fd5eab1c0037b984266b70ebb763fd60880dfa6be0",
}
GEOMETRY_SHA256 = "5b200136a81b1b6d75611072674b551ce9a9befcd28d6512f4a8000a36fa729a"
GEOMETRY_MESH_COUNT = 1177
SOURCE_HASHES = {
    "build_market_historic_iron_glass_sticker_lego_v98.py": "379fe0b92f906612ee10d36dccde4b41e5f31fe4d3fb8dde55590e2a1583da15",
    "compile_market_historic_iron_glass_sticker_landmark_v98.py": "0c63a8130c84e3403db82e4e4ecb084a31d36baba9015f144298a7baff3316cc",
    "market_historic_iron_glass_sticker_landmark_v98.json": "d836d9c91c014c82c2d61505aa87477257fdc211bed15a2fbbe229b01128091d",
    "architectural_signature_profiles.d/zzzzzzzzzzzzzzzzzz_market_historic_iron_glass_sticker_landmark_v98.json": "948e83d466b252cb4a2f638f275695efea500514815a787b8212b7c010988786",
    "market_historic_iron_glass_sticker_landmark_v98_carrier_packages.json": "ab4010efb938d5e35fa72286203aa9e6d45eefa0bf7fa9a8fdab925f25d6e528",
    "market_historic_iron_glass_sticker_landmark_v98_contract.json": "d0af59272f8bc44c987294ceb2330972a57155fecf486e8348f641577994f331",
    "sticker_assets/market_historic_iron_glass_v98/provenance.json": "4bf5852f1560d14d59b1d82b32cd11d1cae4e7c96eb4f0c7913a8eff82552001",
}
FORMAL_HASHES = {
    f"{FAMILY}_manifest.json": "90ac182ee6671e7f952c89d803015f3e8542d785dd003a3dec472f303e69d4b8",
    "production_preflight.json": "f002550be12cabb33a7015aa40d6fb008ed73d2532da9ed8fcb9e13cb74875ec",
    "validation_report.json": "cd8914d5abee327b2cdaf6cc4f7d925c0fcf792b7569c03380315cb4342332b5",
    f"{FAMILY}_aerial.png": "40e1077cf07171f72e303334e768c06dddd3d3a5882f5254af73f73b8c7ce01d",
    f"{FAMILY}_archetype_match.png": "8de839feda28620da943fbf38eaebf81b668a6776a65a017d21e053af20c2062",
    f"{FAMILY}_context.png": "47fdee7b6b18c6997c5de3f672e04dfc2ea820cbf91d37097b1e40f70206c975",
    f"{FAMILY}_facade_close.png": "fa176ec835d41c7ad12604a246a5bfbd759bb75c6e8d77b695e5ffcb5a638059",
    f"{FAMILY}_front_corner_oblique.png": "bf5b7a4027b14f8af4a0c4ab2460124ff2513b488cfd12a0282918e8e4c460ee",
    f"{FAMILY}_preview.png": "462007283a711fa111a6413e397315ba198ca1d167260d0708a15d3724872a50",
    f"{FAMILY}_rear_corner_oblique.png": "f9ce2fac88a92d9b2d3641beda5dcab8665286e232ab6e58af07d258d0166f7f",
    f"{FAMILY}_roof_audit.png": "6d7bab5c21a0541ac6ac4ad0bce5d2e74d558cff14968c19a312e21156b5fbc3",
    f"{FAMILY}_street.png": "a3e7c28499d0edde8ddb30bf6433632e344fc0043392dc2fc6de8e1d9fcef05b",
}
APPROVED_SCORES = {
    "canonical": 95.14,
    "components": {
        "archetype_identity": 28.20,
        "geometry_and_massing": 19.12,
        "sticker_and_material_fidelity": 19.06,
        "coverage_and_registration": 14.16,
        "release_and_landmark_readiness": 14.60,
    },
    "hard_stops": 0,
}
FIRST_NINE_SHA256 = "849105ccf40548fb21ec9f19ec66bddc668ad3d9135ddf885eb4fdeee355e7d1"

ORDER10_QUEUED = {
    "order": 10,
    "archetype_id": "food_hall_market_hall",
    "variant_id": "market_historic_iron_glass",
    "representation": "fixed_landmark",
    "status": "queued",
}
ORDER10_APPROVED = {
    "order": 10,
    "archetype_id": "food_hall_market_hall",
    "variant_id": "market_historic_iron_glass",
    "representation": "fixed_landmark",
    "status": "approved_95_plus",
    "architect_scores": {
        "canonical": 95.14,
        "components": [28.20, 19.12, 19.06, 14.16, 14.60],
        "hard_stops": 0,
    },
    "reference_authority": "three_exact_variant_0_images_override_generic_family_metadata",
    "identity_locks": [
        "one open public market hall under a physical heritage-green cast-iron frame",
        "continuous curved barrel glazing with front and rear fans and a fixed ridge lantern",
        "warm brick side aisles with pale stone quoins and true recessed arched openings",
        "fixed partial side galleries and recessed occupied timber market stalls",
        "asymmetric slate-left and standing-seam-zinc-right aisle roofs with bounded rooflights",
        "open cavernous nave and constrained closed rear service completion",
    ],
    "approved_tiers": {
        "canonical": {
            "width_m": 45.0,
            "depth_m": 60.0,
            "occupied_hall_levels": 1,
            "fixed_partial_galleries": 2,
        }
    },
    "lego_rule": "fixed 45x60 select-and-place landmark only; preserve one hall and two fixed partial galleries; continuous vertical depth and nonuniform scaling are forbidden and no alternate tier is approved",
    "review_path": "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/market-historic-iron-glass",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _assert_locks() -> None:
    for name, expected in REFERENCE_HASHES.items():
        assert _sha256(REFERENCE / name) == expected, f"reference lock mismatch: {name}"
    for name, expected in SOURCE_HASHES.items():
        assert _sha256(TOOL / name) == expected, f"source lock mismatch: {name}"
    for name, expected in FORMAL_HASHES.items():
        assert _sha256(FORMAL / name) == expected, f"formal evidence lock mismatch: {name}"
    profile = json.loads(
        (TOOL / "architectural_signature_profiles.d/zzzzzzzzzzzzzzzzzz_market_historic_iron_glass_sticker_landmark_v98.json").read_text(encoding="utf-8")
    )
    node = profile["profiles"]["market-historic-iron-glass-sticker-landmark-v98-canonical"]["massing_graph"]["nodes"][0]
    assert node["geometry_sha256"] == GEOMETRY_SHA256
    assert len(node["meshes"]) == GEOMETRY_MESH_COUNT
    components = APPROVED_SCORES["components"]
    assert round(sum(components.values()), 2) == APPROVED_SCORES["canonical"]
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


def _publish_canonical() -> dict:
    manifest = json.loads((FORMAL / f"{FAMILY}_manifest.json").read_text(encoding="utf-8"))
    validation = json.loads((FORMAL / "validation_report.json").read_text(encoding="utf-8"))
    preflight = json.loads((FORMAL / "production_preflight.json").read_text(encoding="utf-8"))
    assembled = manifest["assembled"]
    assert manifest["generator"]["render_engine"] == "CYCLES"
    assert validation["status"] == "pass" and not validation.get("errors")
    assert preflight["status"] == "pass" and not preflight.get("failures")
    assert assembled["final_surface_audit_status"] == "pass"
    assert assembled["final_surface_audit_checked_faces"] == 6409
    assert assembled["final_surface_audit_failure_count"] == 0
    assert manifest["placement_contract"]["mode"] == "fixed_landmark"
    assert manifest["dimensions"]["width_m"] == 45.0
    assert manifest["dimensions"]["depth_m"] == 60.0
    assert manifest["dimensions"]["default_floors"] == 2
    assert manifest["placement_contract"]["continuous_resize_allowed"] is False
    assert len(manifest["renders"]) == 9
    for view in VIEWS:
        shutil.copy2(FORMAL / f"{FAMILY}_{view}.png", OUTPUT / f"render-canonical-{view}.png")
    shutil.copy2(FORMAL / "validation_report.json", OUTPUT / "validation-canonical.json")
    shutil.copy2(FORMAL / "production_preflight.json", OUTPUT / "production-preflight-canonical.json")
    return {
        "dimensions": manifest["dimensions"],
        "geometry_sha256": GEOMETRY_SHA256,
        "geometry_mesh_count": GEOMETRY_MESH_COUNT,
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
        "validation_warnings": validation.get("warnings", []),
        "production_preflight": preflight["status"],
        "production_preflight_sha256": FORMAL_HASHES["production_preflight.json"],
        "manifest_sha256": FORMAL_HASHES[f"{FAMILY}_manifest.json"],
        "render_count": len(manifest["renders"]),
        "render_sha256": {view: FORMAL_HASHES[f"{FAMILY}_{view}.png"] for view in VIEWS},
    }


def _approval_payload() -> dict:
    return {
        "schema": "siteforge.named-architect-review@1",
        "pipeline_version": "v98",
        "building_id": "food_hall_market_hall--market_historic_iron_glass",
        "reviewer": "architect_design_reviewer",
        "status": "pass",
        "score_target_exclusive": 95.0,
        "hard_stop_status": "pass",
        "hard_stop_count": 0,
        "scores": {
            "canonical": {
                "total": APPROVED_SCORES["canonical"],
                "components": APPROVED_SCORES["components"],
            }
        },
        "approved_tiers": ORDER10_APPROVED["approved_tiers"],
        "approved_contract": {
            "representation": "fixed_landmark",
            "continuous_resize_allowed": False,
            "vertical_scaling_allowed": False,
            "depth_scaling_allowed": False,
            "nonuniform_scaling_allowed": False,
            "additional_tiers_allowed": False,
        },
        "machine_evidence": {
            "canonical_surface_faces": 6409,
            "surface_failures": 0,
            "production_preflight": "pass",
            "export_validation": "pass",
        },
        "residual_deductions": [
            "Rear and service elevations are constrained completions of limited exact evidence.",
            "The reviewed export has 1,247 materials and requires later consolidation.",
            "The assembled GLB is 8.1 MB, marginally above the 8 MB texture budget.",
        ],
        "verdict": "Approved only as the reviewed 45 x 60 m fixed select-and-place landmark; arbitrary resizing is not authorized.",
    }


def _release_payload() -> dict:
    return {
        "schema": "siteforge.sticker-method-release-scaffold@1",
        "status": "approved_95_plus",
        "building_id": "food_hall_market_hall--market_historic_iron_glass",
        "reference_sha256": REFERENCE_HASHES,
        "geometry_sha256": {"canonical": GEOMETRY_SHA256},
        "geometry_mesh_count": {"canonical": GEOMETRY_MESH_COUNT},
        "source_sha256": SOURCE_HASHES,
        "tier_contract": {
            "canonical": ORDER10_APPROVED["approved_tiers"]["canonical"],
            "continuous_resize_allowed": False,
            "vertical_scaling_allowed": False,
            "depth_scaling_allowed": False,
            "nonuniform_scaling_allowed": False,
            "additional_tiers_allowed": False,
        },
        "required_machine_gates": {
            "production_preflight": "pass",
            "validation": "pass",
            "surface_audit_failure_count": 0,
            "visible_face_ownership": "exactly_once",
            "generic_fallback_allowed": False,
            "minimum_render_views": 9,
        },
        "formal_release": {
            "architect_scores": APPROVED_SCORES,
            "render_sha256": "recorded_in_machine-evidence.json",
            "review_board_sha256": "recorded_in_machine-evidence.json",
            "visual_approval_status": "pass",
        },
    }


def _readme() -> str:
    return """# Historic Iron-and-Glass Market Hall - Sticker Method V98

Building 10 of Sticker Method Batch 01 is approved as one fixed landmark. The
45 x 60 m canonical tier scored 95.14 in independent architect review with
zero hard stops. No alternate size or arbitrary resizing is approved.

## Locked evidence

- Archetype: `food_hall_market_hall::market_historic_iron_glass`.
- Exact references: `variant_0.png`, `variant_0_angle_60.jpg`, and
  `variant_0_angle_90.jpg`; hashes are locked in `release-evidence-scaffold.json`.
- Final geometry: canonical `5b200136...fa729a`, 1,177 meshes.
- Approved tier: 45 x 60 m, one occupied hall plus two fixed partial galleries.
- Fixed identity: open cavernous nave, physical heritage-green cast-iron frame,
  barrel glazing and fans, ridge lantern, brick-and-stone side aisles, recessed
  timber stalls, and asymmetric slate-left/zinc-right aisle roofs.
- Sticker hard stops: every visible face exactly once; no fallback; physical
  glass separated from bounded occupied cards; roof and soffit faces disjoint;
  explicit terminal ownership; no card leak or arbitrary texture stretching.

## Formal score

- Archetype identity: 28.20
- Geometry and massing: 19.12
- Sticker and material fidelity: 19.06
- Coverage and registration: 14.16
- Release and landmark readiness: 14.60
- Total: **95.14**, with zero hard stops

## Evidence

- `01-exact-reference-comparison.png` - exact front identity and approved render.
- `02-oblique-and-detail-comparison.png` - iron frame, glass, masonry and stalls.
- `03-roof-reference-comparison.png` - barrel, lantern and asymmetric aisle roofs.
- `04-nave-and-rear-comparison.png` - cavernous nave, galleries and constrained rear.
- `visual-approval.json` - independent score and fixed-landmark approval.
- `machine-evidence.json` - locked sources, renders, face audit and validation.

## Reproduction commands

```powershell
pytest -q tools/archetype_compiler/tests/test_market_historic_iron_glass_geometry_v98.py tools/archetype_compiler/tests/test_market_historic_iron_glass_v98_assets.py tools/archetype_compiler/tests/test_market_historic_iron_glass_compiler_v98.py
python -m py_compile tools/archetype_compiler/create_market_historic_iron_glass_v98_review.py
python tools/archetype_compiler/create_market_historic_iron_glass_v98_review.py
git diff --check
```

The publisher refuses changed references, geometry, source packages, generated
outputs, provenance or formal evidence; failed preflight or validation; any
surface-audit failure; a score not strictly above 95; a nonzero hard-stop count;
or any semantic change to catalogue orders 1-9.

## Fixed-landmark contract

The user selects and places this 45 x 60 m landmark. Continuous, vertical,
depth and nonuniform scaling are forbidden. The one hall, two partial galleries,
open nave, barrel, lantern and roof identity kit remain indivisible. A new size
requires separately authored geometry and Sticker Method review.

## Known bounded limitations

Rear and service surfaces are constrained completions of the exact front,
oblique and aerial evidence. The assembled export has 1,247 materials and is
8.1 MB against an 8 MB texture budget; consolidation is a nonvisual follow-up.
"""


def _promote_order10() -> None:
    before = BATCH.read_bytes()
    batch = json.loads(before.decode("utf-8"))
    buildings = batch["buildings"]
    assert len(buildings) == 10 and [item["order"] for item in buildings] == list(range(1, 11))
    assert _json_sha256(buildings[:9]) == FIRST_NINE_SHA256, "catalogue orders 1-9 changed"
    assert all(item["status"] == "approved_95_plus" for item in buildings[:9])
    if buildings[9] == ORDER10_APPROVED:
        return
    assert buildings[9] == ORDER10_QUEUED, "order 10 is neither the locked queue entry nor approved payload"
    queued = json.dumps(ORDER10_QUEUED, indent=2).replace("\n", "\r\n")
    approved = json.dumps(ORDER10_APPROVED, indent=2).replace("\n", "\r\n")
    queued = "\r\n".join("    " + line if line else line for line in queued.split("\r\n"))
    approved = "\r\n".join("    " + line if line else line for line in approved.split("\r\n"))
    assert before.count(queued.encode("utf-8")) == 1, "locked order-10 source block not found exactly once"
    after = before.replace(queued.encode("utf-8"), approved.encode("utf-8"), 1)
    updated = json.loads(after.decode("utf-8"))
    assert _json_sha256(updated["buildings"][:9]) == FIRST_NINE_SHA256
    assert updated["buildings"][9] == ORDER10_APPROVED
    BATCH.write_bytes(after)


def main() -> None:
    _assert_locks()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    canonical = _publish_canonical()
    _write_json(OUTPUT / "visual-approval.json", _approval_payload())
    _write_json(OUTPUT / "release-evidence-scaffold.json", _release_payload())
    (OUTPUT / "README.md").write_text(_readme(), encoding="utf-8")
    evidence = {
        "schema": "siteforge.sticker-method-machine-evidence@1",
        "architect_scores": APPROVED_SCORES,
        "reference_sha256": REFERENCE_HASHES,
        "source_sha256": SOURCE_HASHES,
        "formal_input_sha256": FORMAL_HASHES,
        "tiers": {"canonical": canonical},
        "tier_contract": {
            "representation": "fixed_landmark",
            "approved_dimensions_m": ORDER10_APPROVED["approved_tiers"]["canonical"],
            "continuous_resize_allowed": False,
            "vertical_scaling_allowed": False,
            "depth_scaling_allowed": False,
            "nonuniform_scaling_allowed": False,
            "additional_tiers_allowed": False,
        },
        "non_blocking_optimization_follow_up": {"material_consolidation": True, "texture_budget": True},
    }
    evidence_path = OUTPUT / "machine-evidence.json"
    _write_json(evidence_path, evidence)
    _board("01-exact-reference-comparison.png", "Historic Iron-and-Glass Market Hall V98 - exact identity", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (FORMAL / f"{FAMILY}_archetype_match.png", "APPROVED CANONICAL - 45 x 60 m"),
    ])
    _board("02-oblique-and-detail-comparison.png", "Cast iron, curved glass, masonry and occupied stalls", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT OBLIQUE"),
        (FORMAL / f"{FAMILY}_front_corner_oblique.png", "APPROVED OBLIQUE"),
        (FORMAL / f"{FAMILY}_facade_close.png", "APPROVED NAVE CLOSE"),
    ])
    _board("03-roof-reference-comparison.png", "Barrel glazing, ridge lantern, slate and standing-seam zinc", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL"),
        (FORMAL / f"{FAMILY}_aerial.png", "APPROVED AERIAL"),
        (FORMAL / f"{FAMILY}_roof_audit.png", "APPROVED ROOF AUDIT"),
    ], contain=True)
    _board("04-nave-and-rear-comparison.png", "Open cavernous nave, fixed galleries and constrained rear", [
        (FORMAL / f"{FAMILY}_archetype_match.png", "OPEN PUBLIC NAVE"),
        (FORMAL / f"{FAMILY}_facade_close.png", "OCCUPIED GALLERY DEPTH"),
        (FORMAL / f"{FAMILY}_rear_corner_oblique.png", "CONSTRAINED REAR"),
    ])
    boards = [OUTPUT / name for name in (
        "01-exact-reference-comparison.png",
        "02-oblique-and-detail-comparison.png",
        "03-roof-reference-comparison.png",
        "04-nave-and-rear-comparison.png",
    )]
    evidence["review_board_sha256"] = {path.name: _sha256(path) for path in boards}
    _write_json(evidence_path, evidence)
    _promote_order10()


if __name__ == "__main__":
    main()
