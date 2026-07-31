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
            "reference_registration": {
                "mode": "archetype_specific",
                "source_archetype_id": "quality_pilot",
                "registered_elevations": ["front", "left", "right", "rear"],
                "registered_surfaces": ["podium", "typical", "crown", "roof"],
                "uv_strategy": "feature_registered_shared_coordinates",
                "depth_binding": "shader_bump",
                "generic_tiling_allowed": False,
            },
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
    assert (
        memory["memory_version"]
        == "2026-07-31-wave11-optical-curve-v109"
    )
    memory_doc = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "HIGH_QUALITY_3D_BUILDING_MEMORY.md"
    ).read_text(encoding="utf-8")
    assert memory["memory_version"] in memory_doc
    assert any(
        "arena, dome or inhabited-arch landmark" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "camera-locked archetype" in item["symptom"].lower()
        and "screen-space offsets" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "entrance staircase" in item["symptom"].lower()
        and "tacked onto the facade" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "flat orange window" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "checkerboard-like" in item["symptom"].lower()
        and "family optical profile" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "generic roof shell" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "stacked ribbons" in item["symptom"].lower()
        and "black canopy" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "exports below ground" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "secondary elevations" in item["symptom"].lower()
        and "enlarged brick mosaics" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "courtyard ring roof" in item["symptom"].lower()
        and "internal gable end caps" in item["correction"].lower()
        and "true-scale roof uvs" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "impossible vertical extent" in item["symptom"].lower()
        and "dependency graph" in item["correction"].lower()
        and "on-disk glb bounds" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "flat service zone" in item["symptom"].lower()
        and "floating above the corrugation" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "stoop entrance or courtyard passage" in item["symptom"].lower()
        and "tacked onto the facade" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "balcony stack" in item["symptom"].lower()
        and "ghost balconies" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "slightly imperfect footprint" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "monumental atrium" in item["symptom"].lower()
        and "closed transparent section" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "custom elevation" in item["symptom"].lower()
        and "no exported material consumed it" in item["cause"].lower()
        and "occupied-depth underlay" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "triangular quilt" in item["symptom"].lower()
        and "unitized panel topology" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "screen fuses into a pale solid wall" in item["symptom"].lower()
        and "shadowed mortar bed" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert {
        "reference_is_goalpost",
        "geometry_carries_identity",
        "freeform_envelopes_are_continuous_and_sectional",
        "fixed_ends_repeat_middle",
        "entrances_and_passages_are_subtractive",
        "balcony_stacks_are_constructed_once",
        "fixed_landmarks_accept_bounded_drawing_variation",
        "materials_are_pbr",
        "glazing_materiality_matches_reference",
        "pbr_assets_are_verified",
        "skins_are_archetype_specific",
        "image_generation_recipe_is_reproducible",
        "render_locked_sources_are_geometry_bound",
        "registered_reference_and_tile_safe_zones_are_separate",
        "construction_skins_are_projection_clean",
        "visually_open_assemblies_are_open_geometry",
        "semantic_materials_deduplicate_images",
        "proof_glass_does_not_redefine_delivery_glass",
        "unitized_enclosures_are_panel_topologies",
        "glass_is_layered",
        "validate_shapes_not_one_box",
        "shape_matrices_are_honest",
        "archetype_envelope_not_parcel_fill",
        "identity_aliases_are_explicit",
        "monumental_glazing_has_sectional_depth",
        "multi_aisle_roofs_are_complete_systems",
        "detached_houses_are_complete_compositions",
    } <= principle_ids
    image_generation = memory["construction_memory"]["image_generation"]
    assert {
        "labelled_archetype_goalpost",
        "rectified_front_elevation",
        "shadow_neutral_material_study",
        "occupied_depth_plate",
    } <= set(image_generation["required_source_roles"])
    assert {
        "provider",
        "model",
        "generated_at",
        "input_paths",
        "saved_output_path",
        "output_role",
        "registered_surfaces",
        "prompt_fields",
    } <= set(image_generation["provenance_contract"]["required_fields"])
    assert (
        "complete, unmodified exact prompt"
        in image_generation["provenance_contract"]["prompt_storage_rule"]
    )
    assert image_generation["provenance_contract"]["canonical_path"].endswith(
        "textures/source/reference-generation.json"
    )
    assert any(
        "generic skins" in item["symptom"].lower()
        and "chat history" in item["cause"].lower()
        and "locked-camera comparison sheet" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "curved shell, long timber member or deep stone arcade"
        in item["symptom"].lower()
        and "tile-safe shadow-neutral" in item["correction"].lower()
        and "occupied-depth plate" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "warped buildings, reflections or furniture printed" in item["symptom"].lower()
        and "orthographic shadow-neutral construction plate"
        in item["correction"].lower()
        and "real members" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "too large for reliable mobile loading" in item["symptom"].lower()
        and "same approved construction-image paths"
        in item["correction"].lower()
        and "far lods" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "visible head reads as a staircase" in item["symptom"].lower()
        and "one continuous ribbon" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "one dark repeated image" in item["symptom"].lower()
        and "wash its base colour" in item["correction"].lower()
        and "occupied-depth source" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "mast, roof lantern, photovoltaic rack or screen" in item["symptom"].lower()
        and "complete assembled bounds" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "context-dependent blender operators" in item["cause"].lower()
        and "metric vertices" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "reject perspective" in rule.lower()
        for rule in image_generation["pbr_derivation"]
    )
    glazing = memory["construction_memory"]["glazing"]
    assert {
        "bronze_recessed_occupied",
        "heritage_sash_occupied",
        "industrial_crittall_occupied",
        "nordic_clear_occupied",
        "museum_atrium_low_iron",
        "terracotta_office_low_e",
        "civic_recessed_smoked",
        "chalet_warm_low_e",
        "lanehouse_screened_low_e",
        "villa_recessed_iron_glass",
    } <= set(glazing["profiles"])
    assert any(
        "detached house" in item["symptom"].lower()
        and "fixed whole-house landmark" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert "nearly non-emissive" in glazing["materiality_rule"]
    assert "glTF extras" in glazing["export_contract"]
    assert "KHR clearcoat" in glazing["export_contract"]
    assert "proof renderer" in glazing["export_contract"]
    assert "must restore" in glazing["export_contract"]


def test_complete_family_passes_executable_quality_memory():
    from quality_memory import assess_family_quality

    assessment = assess_family_quality(production_manifest(), {"status": "pass", "warnings": []})

    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
    assert assessment["hard_failures"] == []
    assert assessment["review_findings"] == []


def test_filesystem_assessor_rejects_declared_channels_without_real_assets(tmp_path):
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["facade_sheet"]["assets"] = {
        "skin_manifest": "textures/skin_manifest.json",
        "source": "textures/source.png",
        "near": {
            channel: f"textures/near_{channel}.png"
            for channel in ("albedo", "normal", "roughness", "ao", "depth", "emissive")
        },
        "far": {
            channel: f"textures/far_{channel}.png"
            for channel in ("albedo", "normal", "roughness", "ao", "depth", "emissive")
        },
    }
    assessment = assess_family_quality(
        manifest,
        {"status": "pass", "warnings": []},
        family_dir=tmp_path,
    )

    assert assessment["status"] == "review"
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_or_invalid_pbr_assets"
    }


def write_verified_assets(manifest: dict, family_dir: Path) -> None:
    from PIL import Image

    textures = family_dir / "textures"
    textures.mkdir(exist_ok=True)
    (textures / "skin_manifest.json").write_text("{}\n", encoding="utf-8")
    Image.new("RGB", (8, 8)).save(textures / "source.png")
    near = {}
    far = {}
    for channel in (
        "albedo",
        "normal",
        "roughness",
        "ao",
        "depth",
        "emissive",
        "glass_mask",
        "opaque_mask",
    ):
        near_path = textures / f"near_{channel}.png"
        far_path = textures / f"far_{channel}.png"
        Image.new("RGB", (4096, 8)).save(near_path)
        Image.new("RGB", (1024, 8)).save(far_path)
        near[channel] = near_path.relative_to(family_dir).as_posix()
        far[channel] = far_path.relative_to(family_dir).as_posix()
    manifest["facade_sheet"]["assets"] = {
        "skin_manifest": "textures/skin_manifest.json",
        "source": "textures/source.png",
        "near": near,
        "far": far,
    }


def test_filesystem_assessor_verifies_atlas_files_and_declared_widths(tmp_path):
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    write_verified_assets(manifest, tmp_path)
    assessment = assess_family_quality(
        manifest,
        {"status": "pass", "warnings": []},
        family_dir=tmp_path,
    )

    assert assessment["status"] == "pass"
    asset_gate = next(
        gate
        for gate in assessment["gates"]["review"]
        if gate["id"] == "missing_or_invalid_pbr_assets"
    )
    assert asset_gate["passed"] is True


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
        "generic_or_unregistered_skin",
        "albedo_not_shadow_neutral",
        "missing_fixed_assembly_contract",
    }


def test_generic_tiled_skin_routes_to_review():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["facade_sheet"]["reference_registration"] = {
        "mode": "generic_style_atlas",
        "source_archetype_id": "quality_pilot",
        "registered_elevations": [],
        "registered_surfaces": [],
        "uv_strategy": "box_projection_repeat",
        "depth_binding": "declared_file_only",
        "generic_tiling_allowed": True,
    }

    assessment = assess_family_quality(
        manifest,
        {"status": "pass", "warnings": []},
    )

    assert assessment["status"] == "review"
    assert {
        item["id"] for item in assessment["review_findings"]
    } == {"generic_or_unregistered_skin"}


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


def test_fixed_landmark_requires_a_bounded_near_native_scale_contract():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["massing_graph"] = {"type": "fixed_landmark"}
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "review"
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_or_unsafe_fixed_landmark_scale_band"
    }

    manifest["footprint_compatibility"]["fixedLandmarkScaleBand"] = {
        "scaleMin": 0.80,
        "scaleMax": 1.20,
        "maxAxisRatio": 1.18,
    }
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})
    assert assessment["status"] == "pass"

    manifest["footprint_compatibility"]["fixedLandmarkScaleBand"][
        "maxAxisRatio"
    ] = 1.40
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})
    assert assessment["status"] == "review"
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_or_unsafe_fixed_landmark_scale_band"
    }


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
    write_verified_assets(manifest, family_dir)
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
