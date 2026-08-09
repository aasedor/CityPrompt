"""Regression tests for compact exact-variant massing recipes."""
from __future__ import annotations


DIMENSIONS = {
    "width_m": 20.0,
    "depth_m": 16.0,
    "default_floors": 4,
    "podium_height_m": 4.5,
    "floor_height_m": 3.6,
    "roof_height_m": 2.4,
}


def test_front_opening_recipe_builds_five_depth_bearing_arches_and_clearances():
    from massing_recipes import compile_massing_recipe

    graph = compile_massing_recipe({
        "kind": "front_opening_landmark",
        "profile": "test_portici",
        "description": "five-bay portici",
        "frontage_depth_m": 3.2,
        "opening_shape": "round_arch",
        "opening_count": 5,
        "opening_width_m": 2.7,
        "opening_height_m": 4.0,
        "spring_height_m": 2.65,
        "void_id": "portici_arcade",
        "section_mode": "recessed",
        "roof_kind": "hipped",
    }, DIMENSIONS)

    opening = next(node for node in graph["nodes"] if node["id"] == "front_opening_block")
    skin = next(item for item in graph["assemblies"] if item["id"] == "front_podium_skin")
    void = next(item for item in graph["voids"] if item["id"] == "portici_arcade")
    assert opening["kind"] == "opening_block"
    assert opening["opening_count"] == 5
    assert opening["section_mode"] == "recessed"
    assert void["size"][1] == 3.2
    assert len(skin["opening_clearances"]) == 5


def test_courtyard_recipe_opens_passage_into_real_four_wing_court():
    from massing_recipes import compile_massing_recipe

    graph = compile_massing_recipe({
        "kind": "courtyard_passage",
        "profile": "test_scandi_court",
        "description": "perimeter court",
        "wing_depth_m": 4.2,
        "opening_width_m": 4.4,
        "opening_height_m": 4.0,
        "void_id": "court_passage",
    }, {**DIMENSIONS, "width_m": 24.0, "depth_m": 20.0, "default_floors": 6})

    front = next(node for node in graph["nodes"] if node["id"] == "front_passage_wing")
    assert front["section_mode"] == "through"
    assert {void["id"] for void in graph["voids"]} == {"open_courtyard", "court_passage"}
    assert len([node for node in graph["nodes"] if node["kind"] == "gable_roof"]) == 4


def test_signature_extensions_resolve_all_five_exact_variants():
    from signature_profiles import signature_for

    variants = {
        "historical_brick_arts_crafts",
        "courthouse_neoclassical_temple",
        "med_arcade_italian_portici",
        "warehouse_arch_window_brick",
        "scandi_urban_white_plaster",
    }
    for variant in variants:
        profile = signature_for(variant)
        assert profile["production_contract"]["quality_contract_version"] == 2
        assert profile["massing_recipe"]["reference_views"]


def test_step_gable_recipe_keeps_sparse_openings_and_capped_profile_explicit():
    from massing_recipes import compile_massing_recipe

    openings = [
        {"type": "door", "along_m": 0.0, "base_z_m": 0.3, "width_m": 0.9, "height_m": 2.6},
        {"type": "window", "along_m": -1.5, "base_z_m": 1.0, "width_m": 1.0, "height_m": 2.0},
    ]
    graph = compile_massing_recipe({
        "kind": "stepped_gable_house", "profile": "test_step_gable",
        "description": "measured canal house", "front_openings": openings,
        "side_openings": [], "rear_openings": [],
    }, {**DIMENSIONS, "width_m": 6.0, "depth_m": 12.0, "default_floors": 4})

    gable = next(item for item in graph["assemblies"] if item["id"] == "front_crow_step")
    schedule = next(item for item in graph["assemblies"] if item["id"] == "front_opening_schedule")
    assert gable["profile_style"] == "crow_step_flat"
    assert gable["profile_construction"] == "capped_masonry"
    assert schedule["openings"] == openings
    assert len([item for item in graph["assemblies"] if item["kind"] == "tie_grid"]) == 4
    assert graph["recipe_contract"]["front_opening_count"] == 2


def test_market_recipe_builds_cross_aisles_and_four_real_open_perimeters():
    from massing_recipes import compile_massing_recipe

    graph = compile_massing_recipe({
        "kind": "multi_aisle_market_hall", "profile": "test_market",
        "description": "measured market hall", "front_column_count": 9,
        "side_column_count": 7,
    }, {**DIMENSIONS, "width_m": 65.0, "depth_m": 45.0, "default_floors": 1})

    roof_ids = {
        node["id"] for node in graph["nodes"] if node["kind"] == "gable_roof"
    }
    assert roof_ids == {
        "central_glass_nave", "left_opaque_aisle", "right_opaque_aisle", "cross_glass_nave",
    }
    assert {
        node["material"] for node in graph["nodes"] if node["kind"] == "gable_roof"
    } == {"signature_roof"}
    assert len([void for void in graph["voids"] if void["shape"] == "open_perimeter_bays"]) == 4
    assert len([item for item in graph["assemblies"] if item["kind"] == "curtain_wall"]) == 4
    assert len([item for item in graph["assemblies"] if item["kind"] == "awning_schedule"]) == 4
    assert len([item for item in graph["assemblies"] if item["kind"] == "market_stall_schedule"]) == 4
    assert all(
        item["height_m"] == 5.98
        for item in graph["assemblies"] if item["kind"] == "column_array"
    )
    assert len([
        item for item in graph["assemblies"]
        if item["kind"] == "pitched_roof_surface_detail" and item["tile_material"] == "stained_glass"
    ]) == 2
    assert graph["recipe_contract"]["front_open_bays"] == 8
    assert graph["recipe_contract"]["side_open_bays"] == 6
    assert graph["recipe_contract"]["footprint_projection_allowance_m"] == 5.2


def test_terminal_recipe_separates_arcades_clock_and_unbacked_glass_vault():
    from massing_recipes import compile_massing_recipe

    graph = compile_massing_recipe({
        "kind": "beaux_arts_trainshed_terminal",
        "profile": "test_terminal",
        "description": "image-locked terminal",
        "headhouse_depth_m": 18.0,
        "headhouse_height_m": 20.0,
        "ground_arch_count": 9,
        "upper_arch_count": 5,
        "shed_width_m": 44.0,
        "shed_rise_m": 13.5,
        "glass_material": "terminal_window_glass",
        "roof_glass_material": "trainshed_glass",
    }, {**DIMENSIONS, "width_m": 70.0, "depth_m": 56.0, "default_floors": 3})

    ground = next(node for node in graph["nodes"] if node["id"] == "ground_arcade")
    upper = next(node for node in graph["nodes"] if node["id"] == "upper_arcade")
    vault = next(item for item in graph["assemblies"] if item["id"] == "trainshed_barrel_glazing")
    doors = next(item for item in graph["assemblies"] if item["id"] == "recessed_entry_doors")
    assert ground["section_mode"] == "through"
    assert ground["opening_count"] == 9
    assert upper["opening_count"] == 5
    assert upper["back_enabled"] is False
    assert upper["back_glass_material"] == "terminal_window_glass"
    assert vault["glass_material"] == "trainshed_glass"
    assert vault["glass_depth_fraction"] == 0.58
    assert len(doors["openings"]) == 9
    assert {void["id"] for void in graph["voids"]} == {
        "ground_arcade_tunnels", "open_trainshed_volume",
    }
    assert graph["recipe_contract"]["kind"] == "beaux_arts_trainshed_terminal"


def test_video_lessons_terminal_profile_is_selective_and_image_locked():
    from signature_profiles import signature_for

    profile = signature_for("beaux_arts_trainshed_terminal")
    assert profile["evidence_policy"]["metadata_mode"] == "selective"
    assert profile["glass_profile"] == "industrial_sash"
    assert profile["massing_recipe"]["kind"] == "beaux_arts_trainshed_terminal"
    assert profile["production_contract"]["image_lock"]["minimum_measurements"] == 10
