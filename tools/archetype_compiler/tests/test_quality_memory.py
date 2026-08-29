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
        "quality_standard_evidence": {
            "standard_id": "haussmann-depth-shape-skin-scale@1",
            "distinctive_shape_features": [
                "chamfered occupied corner",
                "open courtyard massing",
            ],
            "physical_depth_features": [
                "open projecting balcony railings",
                "recessed layered window assemblies",
            ],
            "photoreal_skin_approved": True,
            "fixed_identity_anchors": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
            ],
            "repeatable_middle_roles": ["typical_a", "typical_b", "typical_c"],
            "comparison_views": [
                "street",
                "front_corner_oblique",
                "rear_corner_oblique",
                "aerial",
                "facade_close",
                "context",
            ],
            "comparison_sheet": "quality-pilot_comparison.jpg",
            "human_visual_approval": True,
        },
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
            {
                "role": "podium",
                "assembly_class": "fixed_semantic",
                "allow_inset_footprint": True,
            },
            {
                "role": "floor",
                "assembly_class": "repeatable_middle",
                "allow_inset_footprint": True,
            },
            {
                "role": "roof",
                "assembly_class": "fixed_semantic",
                "allow_inset_footprint": True,
            },
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
        == "2026-08-29-rlasm-v6-integrated-method-v129"
    )
    memory_doc = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "HIGH_QUALITY_3D_BUILDING_MEMORY.md"
    ).read_text(encoding="utf-8")
    assert memory["memory_version"] in memory_doc
    minimum_standard = memory["minimum_standard"]
    assert minimum_standard["id"] == "haussmann-depth-shape-skin-scale@1"
    assert minimum_standard["reference_archetype_id"] == "parisian_haussmann_classic"
    goalpost_path = Path(__file__).resolve().parents[3] / minimum_standard[
        "reference_goalpost_path"
    ]
    assert goalpost_path.is_file()
    assert {
        "archetype_shape",
        "physical_depth",
        "photoreal_skin",
        "lego_scalability",
    } == set(minimum_standard["pillars"])
    assert "registered_identity_and_supporting_specimens_are_distinct" in principle_ids
    assert "identity_features_have_one_visual_owner" in principle_ids
    assert "visible_relationships_are_proof" in principle_ids
    assert "scoped_reviews_cannot_promote_keepers" in principle_ids
    assert "keeper_status_is_revisable_by_new_visual_evidence" in principle_ids
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
        "pier bisects occupied windows" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "eaves rise away" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "floating pale ridge rods" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "generic member of the style" in item["symptom"].lower()
        and "orthographic identity source" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "doubled chimneys" in item["symptom"].lower()
        and "one visual owner" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "black carrier voids" in item["symptom"].lower()
        and "glass-close" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "zero generic material fallbacks" in item["symptom"].lower()
        and "source-derived specimens" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "fieldstone, brick or paving changes scale" in item["symptom"].lower()
        and "tile size in metres" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "previously recorded builder pass" in item["symptom"].lower()
        and "rescind" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "flat orange window" in item["symptom"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert {
        "structural_grammar_is_family_specific",
        "roof_orientation_and_fields_are_goalpost_locked",
        "screens_preserve_real_cavities",
        "environmental_systems_are_architecture",
        "transparent_interiors_are_coherent_volumes",
        "passive_windows_are_sectional_envelopes",
        "photovoltaic_fields_are_discrete_modules",
        "sibling_variants_are_independent_design_contracts",
        "program_systems_are_connected_topology",
        "haussmann_depth_shape_skin_scale_is_minimum",
        "archetype_envelope_not_parcel_fill",
    } <= principle_ids
    assert any(
        "civic or industrial landmark" in item["symptom"].lower()
        and "trace the complete route or load path" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "haussmann minimum standard" in item["symptom"].lower()
        and "all four pillars" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "four-vertex user polygon" in item["symptom"].lower()
        and "uniform horizontal contain scale" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "stack of cubicles" in item["symptom"].lower()
        and "per-pane occupation cards" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "same bright living-room photograph" in item["symptom"].lower()
        and "blind blades" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "one stretched blue sheet" in item["symptom"].lower()
        and "countable cell topology" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "same generic box" in item["symptom"].lower()
        and "structural grammar" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "sibling variants" in item["symptom"].lower()
        and "independent family" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "ridge runs the wrong direction" in item["symptom"].lower()
        and "export quantisation" in item["correction"].lower()
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
        "all_placed_families_remain_authored_geometry",
        "authored_buildings_hide_planning_volumes",
        "identity_aliases_are_explicit",
        "monumental_glazing_has_sectional_depth",
        "multi_aisle_roofs_are_complete_systems",
        "detached_houses_are_complete_compositions",
    } <= principle_ids
    assert any(
        "grey massing polygons" in item["symptom"]
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "surrounded by pale blue" in item["symptom"]
        for item in memory["known_failure_patterns"]
    )
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
        "dark rectangular cards" in item["symptom"].lower()
        and "explicit alpha mix shader" in item["correction"].lower()
        and "crossed vertical crown planes" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "cannot show the court beyond" in item["symptom"].lower()
        and "split every intersecting mass" in item["correction"].lower()
        and "uninterrupted sightline" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "decorative lines floating near a glass box" in item["symptom"].lower()
        and "one load-path function" in item["correction"].lower()
        and "outside the glazing" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert any(
        "giant masonry blocks" in item["symptom"].lower()
        and "physical-scale coordinates" in item["correction"].lower()
        for item in memory["known_failure_patterns"]
    )
    assert "optical_wall_sections_follow_exterior_to_interior_order" in principle_ids
    assert any(
        "projecting box" in item["symptom"].lower()
        and "exterior to interior" in item["correction"].lower()
        and "oblique glass-close" in item["correction"].lower()
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


def test_missing_haussmann_minimum_standard_evidence_routes_to_review():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest.pop("quality_standard_evidence")
    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "review"
    assert assessment["high_quality_ready"] is False
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_haussmann_minimum_standard_evidence"
    }


def test_filesystem_assessor_rejects_declared_channels_without_real_assets(tmp_path):
    from quality_memory import assess_family_quality
    from PIL import Image

    manifest = production_manifest()
    Image.new("RGB", (16, 16)).save(tmp_path / "quality-pilot_comparison.jpg")
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
    Image.new("RGB", (16, 16)).save(family_dir / "quality-pilot_comparison.jpg")
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


def test_missing_archetype_contain_contract_routes_family_to_review():
    from quality_memory import assess_family_quality

    manifest = production_manifest()
    manifest["modules"][1]["allow_inset_footprint"] = False

    assessment = assess_family_quality(manifest, {"status": "pass", "warnings": []})

    assert assessment["status"] == "review"
    assert {item["id"] for item in assessment["review_findings"]} == {
        "missing_archetype_contain_contract"
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
