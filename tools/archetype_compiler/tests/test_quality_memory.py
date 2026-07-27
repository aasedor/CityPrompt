"""Executable high-quality building memory contract tests."""
from __future__ import annotations

import json
from pathlib import Path


def production_manifest() -> dict:
    return {
        "family": "quality-pilot",
        "archetype_id": "quality_pilot",
        "variant_id": "quality_pilot_selected",
        "archetype_aliases": ["quality_pilot", "quality_pilot_selected"],
        "footprint_compatibility": {
            "preferredProfiles": ["rectangle", "l_shape", "courtyard"],
        },
        "facade_sheet": {
            "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
            "shadow_neutral": {"enabled": True},
            "bay_strategy": {
                "middle_variants": ["floor", "floor_alt", "floor_c"],
            },
            "delivery": {
                "near_atlas_width_px": 4096,
                "far_atlas_width_px": 1024,
            },
            "assembly_contract": {
                "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
                "repeatable": ["typical_a", "typical_b", "typical_c"],
                "side_elevations": "wrapped PBR atlas with recessed glazing",
            },
        },
        "modules": [
            {"role": "podium", "assembly_class": "fixed_semantic"},
            {"role": "floor", "assembly_class": "repeatable_middle"},
            {"role": "roof", "assembly_class": "fixed_semantic"},
        ],
        "assembled": {"filename": "quality-pilot.glb", "triangle_count": 60000},
        "renders": [
            "quality-pilot_preview.png",
            "quality-pilot_street.png",
            "quality-pilot_aerial.png",
            "quality-pilot_context.png",
            "quality-pilot_front_corner_oblique.png",
            "quality-pilot_rear_corner_oblique.png",
            "quality-pilot_facade_close.png",
        ],
    }


def test_quality_memory_is_versioned_and_preserves_core_lessons():
    from quality_memory import load_quality_memory

    memory = load_quality_memory()
    principle_ids = {item["id"] for item in memory["non_negotiable_principles"]}

    assert memory["schema"] == "high-quality-building-memory@1"
    assert memory["memory_version"] == "2026-07-26-wave3-civic-identity-v86"
    memory_doc = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "HIGH_QUALITY_3D_BUILDING_MEMORY.md"
    ).read_text(encoding="utf-8")
    assert memory["memory_version"] in memory_doc
    assert {
        "reference_is_goalpost",
        "geometry_carries_identity",
        "fixed_ends_repeat_middle",
        "materials_are_pbr",
        "glass_is_layered",
        "validate_shapes_not_one_box",
        "shape_matrices_are_honest",
        "identity_aliases_are_explicit",
    } <= principle_ids


def test_complete_family_passes_executable_quality_memory():
    from quality_memory import assess_family_quality

    assessment = assess_family_quality(production_manifest(), {"status": "pass", "warnings": []})

    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
    assert assessment["hard_failures"] == []
    assert assessment["review_findings"] == []


def test_legacy_family_routes_to_review_without_stopping_batch():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["facade_sheet"] = {}
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "review"
    assert assessment["high_quality_ready"] is False
    assert assessment["hard_failures"] == []
    assert {item["id"] for item in assessment["review_findings"]} >= {
        "missing_full_pbr_channels",
        "albedo_not_shadow_neutral",
        "missing_fixed_assembly_contract",
    }


def test_structurally_invalid_family_fails_import_gate():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["assembled"] = {}
    assessment = assess_family_quality(manifest, {"status": "fail", "warnings": []})

    assert assessment["status"] == "fail"
    assert assessment["high_quality_ready"] is False
    assert {item["id"] for item in assessment["hard_failures"]} >= {
        "validation_report_not_pass",
        "missing_assembled_glb",
    }


def test_excess_materials_route_to_review_without_structural_failure():
    from quality_memory import assess_family_quality

    report = {
        "status": "pass",
        "warnings": ["quality-pilot.glb: many materials"],
        "modules": [{"role": "assembled", "materials": [f"MAT_{i}" for i in range(24)]}],
    }
    assessment = assess_family_quality(production_manifest(), report)

    assert assessment["status"] == "review"
    assert assessment["hard_failures"] == []
    assert {item["id"] for item in assessment["review_findings"]} == {
        "material_count_warning"
    }


def test_registered_pbr_material_budget_waiver_passes_with_bounded_rationale():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["material_budget"] = {
        "max_assembled_materials": 36,
        "rationale": "Separate registered PBR bands wrap four elevations.",
    }
    report = {
        "status": "pass",
        "warnings": [],
        "modules": [{"role": "assembled", "materials": [f"MAT_{i}" for i in range(32)]}],
    }
    assessment = assess_family_quality(manifest, report)

    assert assessment["status"] == "pass"
    material_gate = next(
        gate
        for gate in assessment["gates"]["review"]
        if gate["id"] == "material_count_warning"
    )
    assert material_gate["passed"] is True


def test_honest_single_profile_exception_passes_with_rationale():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["footprint_compatibility"] = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": "One fixed public frontage; other profiles duplicate the entrance.",
    }
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "pass"
    profile_gate = next(
        gate
        for gate in assessment["gates"]["review"]
        if gate["id"] == "fewer_than_three_preferred_footprint_profiles"
    )
    assert profile_gate["passed"] is True


def test_selected_variant_without_parent_alias_routes_to_review():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["archetype_aliases"] = ["quality_pilot_selected"]
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "review"
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_variant_alias_contract"
    }


def test_resume_safe_batch_writes_per_family_quality_assessment(tmp_path, monkeypatch):
    import generate_worldclass_library as batch
    from quality_memory import load_quality_memory

    monkeypatch.setattr(batch, "REPO_ROOT", tmp_path)
    family_dir = tmp_path / "families" / "quality-pilot"
    sheet_dir = tmp_path / "facade-sheets" / "quality-pilot"
    family_dir.mkdir(parents=True)
    sheet_dir.mkdir(parents=True)
    manifest = production_manifest()
    (family_dir / "quality-pilot_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (family_dir / "validation_report.json").write_text(
        json.dumps({"status": "pass", "warnings": []}), encoding="utf-8"
    )

    result = batch.family_result(
        {"archetype_id": "quality_pilot"},
        family_dir,
        sheet_dir,
        load_quality_memory(),
    )
    assessment = json.loads(
        (family_dir / "quality_assessment.json").read_text(encoding="utf-8")
    )

    assert result["high_quality_ready"] is True
    assert result["quality_assessment"]["status"] == "pass"
    assert assessment["memory_version"] == result["quality_assessment"]["memory_version"]
