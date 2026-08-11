"""Executable high-quality building memory contract tests."""
from __future__ import annotations

import json


def production_manifest() -> dict:
    return {
        "family": "quality-pilot",
        "archetype_id": "quality_pilot",
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
            "quality-pilot_archetype_match.png",
            "quality-pilot_street.png",
            "quality-pilot_aerial.png",
            "quality-pilot_context.png",
            "quality-pilot_front_corner_oblique.png",
            "quality-pilot_rear_corner_oblique.png",
            "quality-pilot_facade_close.png",
        ],
    }


def approved_visual_review() -> dict:
    return {
        "schema": "building-visual-approval@1",
        "family": "quality-pilot",
        "decision": "approved",
        "reviewer": "test-reviewer",
        "approved_at": "2026-08-07T00:00:00+00:00",
        "reference_set": "test-gold-set",
        "checks": {
            "block_scale": True,
            "building_scale": True,
            "facade_scale": True,
            "orbit_and_context": True,
        },
    }


def test_quality_memory_is_versioned_and_preserves_core_lessons():
    from quality_memory import load_quality_memory

    memory = load_quality_memory()
    principle_ids = {item["id"] for item in memory["non_negotiable_principles"]}

    assert memory["schema"] == "high-quality-building-memory@1"
    assert memory["memory_version"]
    assert memory["calibration_set"]["version"] == "2026-08-07-four-family-v1"
    assert len(memory["calibration_set"]["families"]) == 4
    assert {
        "reference_is_goalpost",
        "geometry_carries_identity",
        "fixed_ends_repeat_middle",
        "materials_are_pbr",
        "glass_is_layered",
        "validate_shapes_not_one_box",
        "identity_mode_is_explicit",
        "preflight_precedes_paid_generation",
        "human_approval_controls_release",
        "variant_atlas_matches_selected_reference",
        "silhouette_gate_is_regression_not_approval",
        "reference_plan_voids_are_geometry",
        "landmark_materials_are_executable_contracts",
        "declared_passages_execute_through_massing",
        "large_span_shells_are_closed_and_panelised",
        "audit_views_are_context_free",
        "large_span_clear_height_is_catalogue_truth",
        "all_exposed_landmark_surfaces_have_registered_owners",
        "stickers_are_approved_in_exact_final_carrier_space",
        "floor_ownership_follows_carrier_construction_domain",
        "identity_landmark_glass_persists_across_review_lods",
        "thin_returns_use_shared_texels_or_explicit_joints",
    } <= principle_ids


def test_complete_family_passes_executable_quality_memory():
    from quality_memory import assess_family_quality

    assessment = assess_family_quality(
        production_manifest(),
        {"status": "pass", "warnings": []},
        visual_approval=approved_visual_review(),
    )

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


def test_structural_pass_requires_explicit_visual_approval():
    from quality_memory import assess_family_quality

    assessment = assess_family_quality(
        production_manifest(),
        {"status": "pass", "warnings": []},
    )

    assert assessment["status"] == "review"
    assert assessment["high_quality_ready"] is False
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_visual_approval"
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
    assessment = assess_family_quality(
        production_manifest(),
        report,
        visual_approval=approved_visual_review(),
    )

    assert assessment["status"] == "review"
    assert assessment["hard_failures"] == []
    assert {item["id"] for item in assessment["review_findings"]} == {
        "material_count_warning"
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
    (family_dir / "visual_approval.json").write_text(
        json.dumps(approved_visual_review()), encoding="utf-8"
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
