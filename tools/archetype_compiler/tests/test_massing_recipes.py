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
    assert len([
        item for item in graph["assemblies"]
        if item["kind"] == "pitched_roof_surface_detail" and item["tile_material"] == "stained_glass"
    ]) == 2
    assert graph["recipe_contract"]["front_open_bays"] == 8
    assert graph["recipe_contract"]["side_open_bays"] == 6
    assert graph["recipe_contract"]["footprint_projection_allowance_m"] == 5.2
