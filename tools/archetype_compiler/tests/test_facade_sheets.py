"""Facade-sheet processing and world-class library contract tests."""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import pytest


def test_worldclass_registry_has_twenty_unique_real_archetypes():
    registry = json.loads(
        (Path(__file__).parents[1] / "worldclass_v7_library.json").read_text(encoding="utf-8")
    )
    entries = registry["entries"]
    ids = [entry["archetype_id"] for entry in entries]
    assert len(entries) == 20
    assert len(set(ids)) == 20
    assert all(entry.get("floors", 0) >= 3 for entry in entries)
    assert registry["generation_profile"]["geometry_detail"] == "city"


def test_v8_signature_registry_covers_every_worldclass_family():
    tool_dir = Path(__file__).parents[1]
    registry = json.loads((tool_dir / "worldclass_v8_library.json").read_text(encoding="utf-8"))
    signatures = json.loads(
        (tool_dir / "architectural_signature_profiles.json").read_text(encoding="utf-8")
    )["profiles"]
    ids = {entry["archetype_id"] for entry in registry["entries"]}
    assert len(ids) == 20
    # Variant-specific profiles may extend the parent registry, but every
    # world-class parent family must remain covered.
    assert ids <= set(signatures)
    assert all(len(signatures[archetype_id]["kits"]) >= 4 for archetype_id in ids)
    assert all(len(profile["identity"]) >= 80 for profile in signatures.values())


def test_v8_cached_facade_sheets_have_four_role_bands():
    root = Path(__file__).parents[1] / "facade_sheets_v8"
    manifests = sorted(root.glob("*/manifest.json"))
    assert len(manifests) == 20
    for path in manifests:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema"] in {"facade-sheet@3", "facade-sheet@4"}
        assert set(payload["bands"]) == {"podium", "floor", "floor_alt", "crown"}


def test_signature_injection_is_renderer_agnostic_dict_extension():
    from signature_profiles import inject_signature

    grammar = {"source": {"archetype_id": "nordic_timber_midrise"}}
    result = inject_signature(grammar)
    assert result is grammar
    assert "timber_picture_frames" in result["architectural_signature"]["kits"]
    assert "mass-timber" in result["architectural_signature"]["identity"]

    chateau = {"source": {"archetype_id": "chateauesque_grand_railway_hotel"},
               "materials": {"roof": {"base_color": "#c9c2b4"}, "accent": {}}}
    inject_signature(chateau)
    assert chateau["materials"]["roof"]["base_color"] == "#6f9a8b"
    assert chateau["materials"]["roof"]["texture_key"] == "verdigris_copper"


def test_signature_injection_prefers_an_explicit_variant_profile():
    from signature_profiles import inject_signature

    grammar = {
        "source": {"archetype_id": "modern_glass_office_institutional"},
        "materials": {
            "primary": {}, "secondary": {}, "accent": {}, "glass": {},
        },
    }
    result = inject_signature(
        grammar,
        "modern_glass_office_institutional",
        variant_id="glass_office_terracotta_fins",
    )

    assert "terracotta fins" in result["architectural_signature"]["identity"]
    assert "curtainwall_fins" in result["architectural_signature"]["kits"]
    assert result["materials"]["primary"]["base_color"] == "#a75f43"
    assert "massing_graph" not in result


def test_modernist_civic_signature_injects_semantic_massing_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {"archetype_id": "modernist_civic_block"},
        "materials": {},
    }
    result = inject_signature(grammar)
    graph = result["massing_graph"]

    assert graph["schema"] == "massing-graph@1"
    assert graph["profile"] == "landmark_hero"
    assert graph["height_m"] > 0
    assert {node["id"] for node in graph["nodes"]} >= {
        "west_floating_volume", "east_service_core", "cantilevered_roof",
    }
    assert {item["kind"] for item in graph["assemblies"]} >= {
        "column_array", "curtain_wall", "ribbon_window", "steps",
    }
    assert {void["id"] for void in graph["voids"]} >= {
        "pilotis_forecourt", "entrance_cleft",
    }
    # Geometry recipes are not facade-prompt hints.
    assert "massing_graph" not in result["architectural_signature"]


@pytest.mark.parametrize(
    ("archetype_id", "required_skin_kind", "glass_profile_name"),
    [
        ("nordic_timber_midrise", "facade_skin", "residential_low_e"),
        ("modern_glass_office_institutional", "facade_skin", "reflective_curtain_wall"),
    ],
)
def test_gemini_skin_pilots_inject_depth_backed_elevations(
    archetype_id, required_skin_kind, glass_profile_name,
):
    from signature_profiles import inject_signature

    grammar = {"source": {"archetype_id": archetype_id}, "materials": {}}
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    kinds = {assembly["kind"] for assembly in graph["assemblies"]}

    assert graph["profile"] == "gemini_skin_hero"
    assert injected["architectural_signature"]["glass_profile"] == glass_profile_name
    assert required_skin_kind in kinds
    assert "glazing_overlay" in kinds
    assert graph["height_m"] >= 26.0
    assert any(node["id"].endswith("shadow_core") for node in graph["nodes"])
    assert "massing_graph" not in grammar["architectural_signature"]


def test_original_mill_variant_explicitly_inherits_parent_massing_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "industrial_brick_mixed_use",
            "variant_id": "industrial_brick_original_mill",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]

    assert graph["profile"] == "victorian_textile_mill_monitor_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 30.0,
        "depth_m": 20.0,
        "floors": 4,
        "floor_height_m": 4.0,
    }
    assert injected["footprint_compatibility"]["preferredProfiles"] == [
        "rectangle", "l_shape", "u_shape",
    ]
    assert "massing_graph_from" not in injected["architectural_signature"]
    assert "massing_graph" not in injected["architectural_signature"]


def test_original_mill_graph_is_not_implicitly_shared_with_sibling_variants():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "industrial_brick_mixed_use",
            "variant_id": "industrial_brick_brewery",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    injected = inject_signature(grammar)

    assert "massing_graph" not in injected
    assert "brewery warehouse" in injected["architectural_signature"]["identity"]


def test_cast_iron_warehouse_variant_injects_fixed_corner_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "adaptive_reuse_warehouse_lofts",
            "variant_id": "warehouse_loft_cast_iron",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]

    assert graph["profile"] == "soho_cast_iron_corner_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 30.0,
        "depth_m": 26.0,
        "floors": 4,
        "floor_height_m": 4.2,
    }
    assert sum(
        assembly["kind"] == "fire_escape_stack"
        for assembly in graph["assemblies"]
    ) == 2
    assert any(
        assembly["kind"] == "classical_balustrade_perimeter"
        for assembly in graph["assemblies"]
    )
    assert "massing_graph" not in injected["architectural_signature"]


def test_arch_window_warehouse_variant_injects_ten_bay_romanesque_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "romanesque_revival_warehouse",
            "variant_id": "warehouse_arch_window_brick",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]

    assert graph["profile"] == "richardsonian_ten_bay_warehouse_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 44.0,
        "depth_m": 36.0,
        "floors": 3,
        "floor_height_m": 5.4,
    }
    front_piers = next(
        assembly for assembly in graph["assemblies"]
        if assembly["id"] == "romanesque_front_piers"
    )
    assert front_piers["columns"] == 10
    assert len(front_piers["active_vertical_indices"]) == 11
    loading = next(
        assembly for assembly in graph["assemblies"]
        if assembly["id"] == "romanesque_front_loading_portals"
    )
    assert len(loading["positions_m"]) == 5
    side_skins = [
        assembly for assembly in graph["assemblies"]
        if assembly["id"].startswith("romanesque_left_elevation_")
    ]
    assert len(side_skins) == 5
    assert [skin["uv_u_min"] for skin in side_skins] == [0.1, 0.2, 0.3, 0.4, 0.5]
    assert all(skin["span_m"] == 7.1 for skin in side_skins)


def test_cream_terracotta_art_deco_variant_injects_fixed_setback_lantern_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "art_deco_setback_tower",
            "variant_id": "art_deco_cream_terracotta",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    graph = inject_signature(grammar)["massing_graph"]

    assert graph["profile"] == "cream_terracotta_four_stage_lantern_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 30.0,
        "depth_m": 28.0,
        "floors": 15,
        "floor_height_m": 3.6,
    }
    node_ids = {node["id"] for node in graph["nodes"]}
    assert {"deco_main_shaft", "deco_stage_one", "deco_stage_two", "deco_crown_stage"} <= node_ids
    assert len([node_id for node_id in node_ids if node_id.startswith("deco_lantern_post_")]) == 8
    front_stack = next(
        assembly for assembly in graph["assemblies"]
        if assembly["id"] == "deco_front_main_skin"
    )
    assert front_stack["repeat_count"] == 2
    assert len(front_stack["levels"]) == 9
    assert "deco_front_main_glazing" in graph["disabled_assembly_ids"]
    assert "deco_front_podium_glazing" in graph["disabled_assembly_ids"]


def test_nordic_mass_timber_variant_injects_open_pavilion_and_planted_roof_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "nordic_timber_midrise",
            "variant_id": "nordic_timber_mass_timber",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    graph = inject_signature(grammar)["massing_graph"]

    assert graph["profile"] == "gemini_skin_hero"
    assert graph["reference_dimensions"] == {
        "width_m": 20.0,
        "depth_m": 16.0,
        "floors": 7,
        "floor_height_m": 3.2,
    }
    nodes = {node["id"]: node for node in graph["nodes"]}
    assemblies = {assembly["id"]: assembly for assembly in graph["assemblies"]}
    assert "pavilion_shadow" not in nodes
    assert nodes["pavilion_service_wall"]["size"][0] < nodes["pavilion_roof"]["size"][0]
    pavilion_posts = [
        node_id
        for node_id in nodes
        if node_id.startswith("pavilion_") and node_id.endswith("_post")
    ]
    assert len(pavilion_posts) == 4
    assert assemblies["timber_roof_guard"]["kind"] == "classical_balustrade_perimeter"
    assert not any(
        assembly_id.startswith("pavilion_") and assembly["kind"] == "curtain_wall"
        for assembly_id, assembly in assemblies.items()
    )


def test_scandi_white_plaster_variant_injects_fixed_dormer_passage_graph():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "scandinavian_urban_residential",
            "variant_id": "scandi_urban_white_plaster",
        },
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "roof": {}},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]

    assert graph["profile"] == "white_plaster_five_dormer_perimeter_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 38.0,
        "depth_m": 22.0,
        "floors": 6,
        "floor_height_m": 3.2,
    }
    nodes = {node["id"]: node for node in graph["nodes"]}
    assemblies = {assembly["id"]: assembly for assembly in graph["assemblies"]}
    dormer_bodies = [
        node_id
        for node_id in nodes
        if node_id.startswith("scandi_front_dormer_")
        and "cap" not in node_id
    ]
    assert len(dormer_bodies) == 5
    assert len([key for key in assemblies if key.endswith("_guard")]) == 5
    assert assemblies["scandi_passage_atlas"]["band"] == "entrance"
    passage_y = assemblies["scandi_passage_atlas"]["centre"][1]
    wall_y = assemblies["scandi_front_skin"]["base_centre"][1]
    assert passage_y < wall_y
    assert injected["materials"]["roof"]["texture_key"] == "standing_seam"
    assert injected["footprint_compatibility"]["preferredProfiles"] == [
        "rectangle",
        "l_shape",
        "u_shape",
    ]


def test_parametric_relief_pilots_keep_landmark_reference_contracts():
    profiles = json.loads(
        (Path(__file__).parents[1] / "architectural_signature_profiles.json").read_text(
            encoding="utf-8"
        )
    )["profiles"]
    nordic = profiles["nordic_timber_midrise"]["massing_graph"]
    glass = profiles["modern_glass_office_institutional"]["massing_graph"]

    assert nordic["reference_dimensions"] == {
        "width_m": 20.0,
        "depth_m": 16.0,
        "floors": 7,
        "floor_height_m": 3.2,
    }
    assert any(item["kind"] == "bay_frame_array" for item in nordic["assemblies"])
    assert sum(item["kind"] == "frame_grid" for item in glass["assemblies"]) == 4
    assert glass["reference_dimensions"]["floors"] == 10
    overlays = [item for item in glass["assemblies"] if item["kind"] == "glazing_overlay"]
    assert overlays and all(item.get("interior_cards") is False for item in overlays)


def test_collegiate_gothic_injects_variable_silhouette_geometry():
    from signature_profiles import inject_signature

    grammar = {"source": {"archetype_id": "collegiate_gothic_education"}, "materials": {}}
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    kinds = {assembly["kind"] for assembly in graph["assemblies"]}
    node_ids = {node["id"] for node in graph["nodes"]}
    assemblies = {assembly["id"]: assembly for assembly in graph["assemblies"]}

    assert graph["profile"] == "gothic_gatehouse_hero"
    assert graph["reference_dimensions"] == {
        "width_m": 60.0,
        "depth_m": 25.0,
        "floors": 4,
        "floor_height_m": 4.0,
    }
    assert {
        "gothic_left_wing_core", "gothic_right_wing_core", "gothic_gate_tower_core",
        "gothic_left_return_core", "gothic_right_return_core", "gothic_rear_wing_core",
    } <= node_ids
    assert {
        "pointed_portal", "buttress_array", "crenellation_array",
        "pinnacle_array", "oriel_array", "facade_skin_stack",
    } <= kinds
    assert {view["role"] for view in graph["reference_views"]} == {
        "street_identity", "oblique_massing", "roof_plan",
    }
    assert any(void["id"] == "quadrangle_courtyard" for void in graph["voids"])
    # Generated facade windows are the source of truth for the wing rhythm;
    # only tower-edge buttresses are fixed geometry, avoiding window overlap.
    assert "gothic_left_buttresses" not in assemblies
    assert "gothic_right_buttresses" not in assemblies
    assert assemblies["gothic_tower_buttresses"]["positions_m"] == [-6.55, 6.55]


def test_classical_civic_injects_courtyard_roof_ring_and_four_column_portico():
    from signature_profiles import inject_signature

    grammar = {"source": {"archetype_id": "civic_classical_building"}, "materials": {}}
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "classical_civic_courtyard_v2"
    assert graph["reference_dimensions"] == {
        "width_m": 42.0,
        "depth_m": 34.0,
        "floors": 2,
        "floor_height_m": 5.6,
    }
    assert {view["role"] for view in graph["reference_views"]} == {
        "street_identity", "oblique_massing", "roof_plan",
    }
    portico = assemblies["civic_giant_portico"]
    assert portico["kind"] == "classical_portico"
    assert portico["count"] == 4
    assert portico["door_count"] == 3
    assert portico["depth_m"] == 3.4
    assert any(
        void["id"] == "civic_open_court" and void["size"][:2] == [23.0, 15.0]
        for void in graph["voids"]
    )
    assert assemblies["civic_copper_roof_ring"]["kind"] == "courtyard_hip_roof"
    assert assemblies["civic_roof_balustrade"]["kind"] == "classical_balustrade_perimeter"
    front_windows = assemblies["civic_front_lower_windows"]
    assert front_windows["kind"] == "classical_window_array"
    assert front_windows["arched"] is True
    assert graph["final_bevel_m"] == 0.0


def test_neoclassical_courthouse_injects_eight_column_temple_and_seamed_hip():
    from signature_profiles import inject_signature

    grammar = {"source": {"archetype_id": "monumental_courthouse_axis"}, "materials": {}}
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}
    nodes = {item["id"]: item for item in graph["nodes"]}

    assert graph["profile"] == "neoclassical_courthouse_temple_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 60.0,
        "depth_m": 45.0,
        "floors": 4,
        "floor_height_m": 5.0,
    }
    portico = assemblies["courthouse_giant_portico"]
    assert portico["count"] == 8
    assert portico["flutes"] == 20
    assert portico["capital_style"] == "corinthian"
    assert portico["door_count"] == 3
    assert assemblies["courthouse_judicial_steps"]["width_m"] == 60.0
    assert assemblies["courthouse_main_roof_seams"]["kind"] == "hip_roof_seam_array"
    assert nodes["courthouse_main_copper_hip"]["kind"] == "hipped_roof"
    assert all("dome" not in node["id"] for node in graph["nodes"])
    assert graph["final_bevel_m"] == 0.0
    assert injected["footprint_compatibility"]["preferredProfiles"] == [
        "rectangle", "u_shape", "courtyard",
    ]


def test_classic_brownstone_injects_paired_streetwall_stoops_and_panelled_entries():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "classic_brownstone_streetwall",
            "variant_id": "classic_brownstone_traditional",
        },
        "materials": {},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "paired_brownstone_streetwall_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 30.0,
        "depth_m": 22.0,
        "floors": 4,
        "floor_height_m": 3.2,
    }
    assert {
        "brownstone_stoop_left",
        "brownstone_stoop_centre",
        "brownstone_stoop_right",
    } <= assemblies.keys()
    entries = assemblies["brownstone_arched_entries"]
    assert entries["positions_m"] == [-11.0, 0.5, 11.0]
    assert entries["arched"] is True
    assert entries["panelled_door"] is True
    assert assemblies["brownstone_upper_windows"]["pedimented"] is True
    assert len(assemblies["brownstone_upper_windows"]["positions_m"]) == 10
    assert {
        "brownstone_left_cornice_brackets",
        "brownstone_right_cornice_brackets",
    } <= assemblies.keys()
    assert injected["footprint_compatibility"]["preferredProfiles"] == [
        "rectangle", "l_shape", "u_shape",
    ]


def test_victorian_main_street_injects_six_arches_segmented_bands_and_seamed_roof():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "historical_brick_main_street",
            "variant_id": "historical_brick_victorian",
        },
        "materials": {},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    nodes = {item["id"]: item for item in graph["nodes"]}
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "victorian_polychrome_main_street_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 15.0,
        "depth_m": 22.0,
        "floors": 2,
        "floor_height_m": 3.6,
    }
    assert len(assemblies["victorian_upper_arches"]["positions_m"]) == 6
    assert assemblies["victorian_storefront_entries"]["positions_m"] == [-3.25, 3.25]
    bands = assemblies["victorian_front_polychrome_bands"]
    assert bands["kind"] == "band_segments"
    assert len(bands["levels_z"]) == 4
    assert len(bands["segments_m"]) == 7
    assert nodes["victorian_low_hip_roof"]["ridge_axis"] == "x"
    assert assemblies["victorian_roof_seams"]["kind"] == "hip_roof_seam_array"
    assert "victorian_skylight_front_curb" in nodes
    assert "victorian_skylight_rear_curb" in nodes
    assert injected["footprint_compatibility"]["preferredProfiles"] == [
        "rectangle", "l_shape", "u_shape",
    ]


def test_v21_expansion_graphs_preserve_family_specific_construction():
    """The methodology batch must not regress to one generic textured box."""
    from signature_profiles import inject_signature

    def graph_for(archetype_id: str) -> dict:
        grammar = {"source": {"archetype_id": archetype_id}, "materials": {}}
        return inject_signature(grammar)["massing_graph"]

    industrial = graph_for("industrial_brick_mixed_use")
    industrial_assemblies = industrial["assemblies"]
    assert industrial["reference_dimensions"]["floors"] == 4
    assert sum(item["kind"] == "corbel_array" for item in industrial_assemblies) == 4
    overlays = [item for item in industrial_assemblies if item["kind"] == "glazing_overlay"]
    assert overlays and all(item.get("frame_mode") == "mask_only" for item in overlays)

    eixample = graph_for("eixample_apartment_block")
    assert eixample["profile"] == "cerda_chamfer_courtyard_v24"
    assert sum(node["kind"] == "chamfered_box" for node in eixample["nodes"]) >= 2
    assert sum(item["kind"] == "balcony_array" for item in eixample["assemblies"]) == 4
    corner_skins = [
        item for item in eixample["assemblies"]
        if item["id"].startswith("eixample_") and item["id"].endswith("corner_elevation")
    ]
    assert len(corner_skins) == 4
    assert all(item["axis"] == "angle" for item in corner_skins)
    assert {item["rotation_z_deg"] for item in corner_skins} == {-45.0, 45.0}

    chateau = graph_for("chateauesque_grand_railway_hotel")
    assert chateau["profile"] == "chateauesque_landmark_v21"
    node_kinds = {node["kind"] for node in chateau["nodes"]}
    assert {"cylinder", "cone", "gable_roof"} <= node_kinds
    assembly_ids = {item["id"] for item in chateau["assemblies"]}
    assert {
        "hotel_centre_elevation",
        "hotel_left_tower_elevation",
        "hotel_left_pavilion_elevation",
        "hotel_right_pavilion_elevation",
    } <= assembly_ids


def test_corner_archetype_compiles_corner_condition():
    from compiler import compile_archetype
    from test_compiler import payload_mixed_use_midrise

    grammar = compile_archetype(payload_mixed_use_midrise(
        archetypeId="parisian_boulevard_corner",
        archetypeLabel="Parisian Boulevard Corner",
    ))
    assert grammar.massing.corner_condition == "corner"


def test_facade_prompts_pin_texture_map_and_forbid_scene_completion():
    pytest.importorskip("PIL")
    pytest.importorskip("numpy")
    from generate_facade_sheets import PROMPT_TEMPLATES

    for prompt in PROMPT_TEMPLATES:
        lowered = prompt.lower()
        assert "texture" in lowered
        assert "orthographic" in lowered or "zero perspective" in lowered
        assert "no sky" in lowered
        assert "no people" in lowered
        assert "identity" in lowered


def test_rooftop_pavilion_crown_crop_excludes_the_brick_middle_floors():
    from generate_facade_sheets import select_crown_bottom

    crop = select_crown_bottom(
        {"massing": {"rooftop_pavilion": True}},
        floor_top=0.368,
        floor_bottom=0.561,
        period=0.193,
        podium_top=0.753,
        layout={"parapet_f": 0.05, "floor_f": 0.16},
    )

    assert crop == pytest.approx(0.175)


def test_conventional_three_storey_crown_contains_only_the_top_storey():
    from generate_facade_sheets import select_crown_bottom

    crop = select_crown_bottom(
        {"massing": {"rooftop_pavilion": False}},
        floor_top=0.431,
        floor_bottom=0.669,
        period=0.238,
        podium_top=0.732,
        layout={"parapet_f": 0.06, "floor_f": 0.22},
    )

    assert crop == pytest.approx(0.431)


def test_conventional_two_storey_crown_keeps_the_detected_upper_storey():
    from generate_facade_sheets import select_crown_bottom

    crop = select_crown_bottom(
        {"massing": {"rooftop_pavilion": False}},
        floor_top=0.280,
        floor_bottom=0.506,
        period=0.226,
        podium_top=0.731,
        layout={"parapet_f": 0.08, "floor_f": 0.20},
    )

    assert crop == pytest.approx(0.506)


def test_secondary_elevation_crop_uses_a_clean_rightmost_glazed_bay():
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    from generate_facade_sheets import select_repeatable_side_bay

    facade = Image.new("RGB", (1000, 240), (150, 80, 55))
    mask = Image.new("L", facade.size, 0)
    draw = ImageDraw.Draw(mask)
    for left in (100, 390, 680):
        draw.rectangle((left, 35, left + 170, 205), fill=255)

    side, side_mask, crop = select_repeatable_side_bay(facade, mask)

    assert crop[0] > 0.60
    assert crop[1] < 0.95
    assert side.size == side_mask.size
    assert side.width < facade.width * 0.35


def test_gpt_image_provider_uses_high_quality_reference_edit(monkeypatch):
    pytest.importorskip("requests")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import OPENAI_MODEL_ID, generate_elevation_openai

    encoded = io.BytesIO()
    Image.new("RGB", (32, 48), (100, 120, 140)).save(encoded, format="PNG")
    response_payload = {"data": [{"b64_json": base64.b64encode(encoded.getvalue()).decode()}]}
    captured = {}

    class Response:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return response_payload

    def fake_post(url, *, headers, data, files, timeout):
        captured.update(url=url, headers=headers, data=data, files=files, timeout=timeout)
        return Response()

    monkeypatch.setattr("requests.post", fake_post)
    reference = Image.new("RGB", (64, 96), (200, 195, 185))
    result = generate_elevation_openai("test-secret", "RECTIFIED FACADE", reference)

    assert result.size == (32, 48)
    assert captured["data"]["model"] == OPENAI_MODEL_ID
    assert captured["data"]["quality"] == "high"
    assert captured["data"]["size"] == "1024x1536"
    assert "hard design reference" in captured["data"]["prompt"].lower()
    assert captured["files"][0][0] == "image[]"
    assert captured["headers"]["Authorization"] == "Bearer test-secret"


def test_openai_key_loader_accepts_environment_without_logging_value(monkeypatch):
    from generate_facade_sheets import load_openai_api_key

    monkeypatch.setenv("OPENAI_API_KEY", "test-environment-key")
    assert load_openai_api_key(None) == "test-environment-key"


def test_horizontal_blend_wraps_without_vertical_tiling():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import make_horizontally_tileable

    array = np.zeros((64, 96, 3), dtype=np.uint8)
    array[:, :, 0] = np.linspace(10, 240, 96, dtype=np.uint8)[None, :]
    array[:16, :, 1] = 220
    result = np.asarray(make_horizontally_tileable(Image.fromarray(array)))
    horizontal_seam = abs(result[:, 0].astype(float) - result[:, -1].astype(float)).mean()
    assert horizontal_seam < 2.0
    assert result[:16, :, 1].mean() > result[-16:, :, 1].mean() + 100


def test_emissive_mask_prefers_warm_lit_pixels():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import derive_emissive_mask

    array = np.zeros((64, 64, 3), dtype=np.uint8)
    array[:, :32] = (188, 132, 62)
    array[:, 32:] = (84, 132, 188)
    mask = np.asarray(derive_emissive_mask(Image.fromarray(array)))
    assert mask[:, :28].mean() > mask[:, 36:].mean() + 100


def test_semantic_glass_mask_normalization_is_binary_and_registered():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import normalize_semantic_glass_mask

    source = np.zeros((40, 20), dtype=np.uint8)
    source[8:32, 5:15] = 230
    result = normalize_semantic_glass_mask(Image.fromarray(source), (40, 80))
    values = set(np.unique(np.asarray(result)).tolist())
    assert result.size == (40, 80)
    assert values <= {0, 255}
    assert np.asarray(result).mean() > 0


def test_fallback_mask_recognizes_cool_curtain_wall_without_selecting_aluminium():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import derive_glass_mask_fallback

    image = Image.new("RGB", (120, 80), (190, 192, 194))
    pixels = image.load()
    for y in range(8, 72):
        for x in range(8, 112):
            if x % 26 not in (0, 1, 2) and y % 24 not in (0, 1, 2):
                pixels[x, y] = (105, 132, 148)
    mask = derive_glass_mask_fallback(image)
    coverage = float(np.asarray(mask, dtype=np.float32).mean() / 255.0)
    assert 0.45 < coverage < 0.80


def test_glass_regions_merge_adjacent_panes_but_keep_separate_window_bays():
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    from generate_facade_sheets import extract_glass_regions

    mask = Image.new("L", (400, 240), 0)
    draw = ImageDraw.Draw(mask)
    for bay_x in (35, 235):
        for row in range(2):
            for column in range(2):
                x0 = bay_x + column * 48
                y0 = 40 + row * 64
                draw.rectangle((x0, y0, x0 + 42, y0 + 60), fill=255)
    regions = extract_glass_regions(mask)
    assert len(regions) == 2
    assert regions[0][2] < regions[1][0]


def test_glass_regions_merge_sash_rows_across_a_heavier_meeting_rail():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    from generate_facade_sheets import extract_glass_regions

    mask = Image.new("L", (400, 240), 0)
    draw = ImageDraw.Draw(mask)
    # A five-pixel horizontal meeting rail is deliberately wider than the
    # slim vertical glazing bars, matching the live industrial-window mask.
    for bay_x in (35, 235):
        for row, row_y in enumerate((40, 105)):
            for column in range(2):
                x0 = bay_x + column * 48
                draw.rectangle((x0, row_y, x0 + 42, row_y + 59), fill=255)

    regions = extract_glass_regions(mask)

    assert len(regions) == 2
    assert all(region[3] - region[1] > 0.48 for region in regions)


def test_reusable_glass_profiles_are_physically_plausible():
    from glass_profiles import GLASS_PROFILES, glass_profile

    assert set(GLASS_PROFILES) == {
        "low_iron_clear",
        "office_clear_occupied",
        "reflective_curtain_wall",
        "industrial_sash",
        "residential_low_e",
        "heritage_leaded_occupied",
    }
    for name in GLASS_PROFILES:
        profile = glass_profile(name)
        assert 0.0 < profile["transmission"] <= 1.0
        assert 1.0 < profile["ior"] < 2.0
        assert 0.0 <= profile["roughness"] < 0.3
        assert profile["interior_depth_m"] > profile["pane_recess_m"]


def test_perpendicular_lantern_has_physical_lancets_on_every_elevation():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "collegiate_gothic_education",
            "variant_id": "collegiate_gothic_perpendicular",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    lancets = [
        item for item in graph["assemblies"]
        if item["kind"] == "pointed_window_array"
    ]
    octagonal_lantern = next(
        node for node in graph["nodes"]
        if node["id"] == "perp_octagonal_lantern"
    )
    low_roof = next(
        node for node in graph["nodes"]
        if node["id"] == "perp_low_lead_roof"
    )

    assert len(lancets) == 8
    assert {item["axis"] for item in lancets} == {"front", "rear", "left", "right", "angle"}
    assert all(item["count"] == 2 for item in lancets)
    assert all(item["recess_m"] >= 0.2 for item in lancets)
    assert {
        item["rotation_z_deg"] for item in lancets if item["axis"] == "angle"
    } == {-135.0, -45.0, 45.0, 135.0}
    assert octagonal_lantern["kind"] == "cylinder"
    assert octagonal_lantern["vertices"] == 8
    assert octagonal_lantern["rotation_z_deg"] == 22.5
    assert low_roof["kind"] == "hipped_roof"
    assert not any(node["id"] == "perp_square_lantern" for node in graph["nodes"])


def test_ruskinian_turret_windows_are_owned_by_fixed_corner_assembly():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "collegiate_gothic_education",
            "variant_id": "collegiate_gothic_ruskinian",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    turret = next(
        item for item in graph["assemblies"]
        if item["id"] == "ruskinian_corner_turrets"
    )

    assert turret["kind"] == "striped_turret_array"
    assert turret["window_levels_m"] == [3.75, 7.95, 12.15]
    assert turret["window_style"] == "rectangular"
    assert turret["window_recess_m"] >= 0.1
    assert 0.08 <= turret["window_surround_depth_m"] <= 0.12
    assert turret["window_surround_m"] <= 0.05
    assert len(turret["centres"]) * 2 * len(turret["window_levels_m"]) == 24
    assert not any(
        item["id"].startswith((
            "ruskinian_left_turret_window",
            "ruskinian_right_turret_window",
        ))
        for item in graph["assemblies"]
    )


def test_ruskinian_facade_period_matches_registered_source_span():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "collegiate_gothic_education",
            "variant_id": "collegiate_gothic_ruskinian",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}
    front_skin = assemblies["ruskinian_front_elevation"]
    left_skin = assemblies["ruskinian_left_elevation"]
    rear_skin = assemblies["ruskinian_rear_elevation"]
    front_glass = assemblies["ruskinian_front_glazing"]
    left_glass = assemblies["ruskinian_left_glazing"]

    assert graph["profile"] == "ruskinian_polychrome_hall_v68"
    assert {level["repeat_count"] for level in front_skin["levels"][1:]} == {7}
    assert left_skin["repeat_count"] == 6
    assert rear_skin["repeat_count"] == 7
    assert {level["band"] for level in left_skin["levels"]} == {"side"}
    assert {level["band"] for level in rear_skin["levels"]} == {"side"}
    assert front_glass["columns"] == 7
    assert left_glass["columns"] == 6
    assert front_glass["repeat_span_m"] == pytest.approx(30.0 / 7, abs=0.001)
    assert left_glass["repeat_span_m"] == pytest.approx(25.0 / 6, abs=0.001)
    assert abs(front_glass["repeat_span_m"] - 4.4) / 4.4 < 0.10
    assert abs(left_glass["repeat_span_m"] - 3.91) / 3.91 < 0.10

    gable_axes = {
        item["axis"] for item in graph["assemblies"]
        if item["id"].startswith("ruskinian_main_") and item["id"].endswith("_gable")
    }
    assert gable_axes == {"front", "rear", "left", "right"}


def test_red_sandstone_rowhouse_preserves_reference_five_bay_rhythm():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "brownstone_rowhouse_frontage",
            "variant_id": "brownstone_rowhouse_red_sandstone",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "red_brick_sandstone_rowhouse_v61"
    assert assemblies["rowhouse_front_glazing"]["columns"] == 5
    assert assemblies["rowhouse_stoop"]["base_centre"][0] == 0.0
    assert "rowhouse_door_pediment" not in assemblies
    assert "rowhouse_left_front_side_skin" in graph["disabled_assembly_ids"]
    assert "rowhouse_rear_left_glazing" in graph["disabled_assembly_ids"]
    for level in ("low", "mid", "high"):
        assert assemblies[f"rowhouse_rear_left_{level}"]["span_m"] == 0.92
        assert assemblies[f"rowhouse_rear_right_{level}"]["span_m"] == 0.92


def test_dark_frame_office_preserves_compact_reference_proportions():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "modern_glass_office_institutional",
            "variant_id": "glass_office_dark_frame",
        },
        "materials": {},
    }
    injected = inject_signature(grammar)
    graph = injected["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "dark_frame_clear_glass_renderlock_v3"
    assert graph["reference_dimensions"] == {
        "width_m": 30.0,
        "depth_m": 20.0,
        "floors": 8,
        "floor_height_m": 3.6,
    }
    assert assemblies["dark_glass_front_structure"]["columns"] == 4
    assert assemblies["dark_glass_front_structure"]["rows"] == 8
    assert len(assemblies["dark_glass_front_skin"]["levels"]) == 7


def test_classic_eixample_preserves_four_storeys_and_real_light_court():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "eixample_apartment_block",
            "variant_id": "eixample-apartment-block-classic",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    nodes = {item["id"]: item for item in graph["nodes"]}
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "cerda_chamfer_courtyard_v24"
    assert graph["reference_dimensions"] == {
        "width_m": 23.0,
        "depth_m": 23.0,
        "floors": 4,
        "floor_height_m": 5.0,
    }
    assert "eixample_shadow_core" in graph["disabled_node_ids"]
    assert "eixample_roof_deck" in graph["disabled_node_ids"]
    assert nodes["eixample_courtyard_floor"]["size"][:2] == [8.8, 8.8]
    assert assemblies["eixample_front_glazing"]["rows"] == 4
    assert assemblies["eixample_front_balconies"]["levels_z"] == [6.1, 10.0, 13.7]


def test_london_mansion_uses_registered_wall_and_canonical_mansard_kit():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "london_heritage_mansion_block",
            "variant_id": "london-heritage-mansion-portland-stone",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    nodes = {item["id"]: item for item in graph["nodes"]}
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "portland_stone_mansion_v3"
    assert graph["reference_dimensions"]["floors"] == 5
    assert nodes["london_mansard_kit"]["kind"] == "canonical_roof"
    assert nodes["london_centre_roof_cap"]["kind"] == "hipped_roof"
    assert assemblies["london_centre_pavilion_sash"]["kind"] == "curtain_wall"
    assert assemblies["london_front_glazing"]["frame_mode"] == "mask_only"
    assert not any(item["kind"] == "balcony_array" for item in graph["assemblies"])


def test_classic_haussmann_preserves_twin_courts_and_fixed_entrance():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "parisian_midrise_block",
            "variant_id": "parisian_haussmann_classic",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "haussmann_twin_court_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 42.0,
        "depth_m": 38.0,
        "floors": 6,
        "floor_height_m": 3.4,
    }
    assert len(graph["voids"]) == 2
    assert assemblies["haussmann_twin_court_mansard"]["kind"] == "mansard_perimeter"
    assert assemblies["haussmann_twin_court_mansard"]["court_count"] == 2
    assert assemblies["haussmann_front_entrance"]["band"] == "entrance"
    assert assemblies["haussmann_front_podium_left"]["levels"][0]["repeat_count"] == 2
    assert assemblies["haussmann_front_balconies"]["levels_z"] == [4.65, 14.85]
    assert assemblies["haussmann_front_balconies"]["rail_profile_m"] == 0.028
    assert graph["final_bevel_m"] == 0.0


def test_boulevard_corner_preserves_curved_landmark_and_open_court():
    from signature_profiles import inject_signature

    grammar = {
        "source": {
            "archetype_id": "parisian_boulevard_corner",
            "variant_id": "parisian_corner_haussmann_turret",
        },
        "materials": {},
    }
    graph = inject_signature(grammar)["massing_graph"]
    assemblies = {item["id"]: item for item in graph["assemblies"]}

    assert graph["profile"] == "haussmann_rounded_corner_court_v1"
    assert graph["reference_dimensions"] == {
        "width_m": 42.0,
        "depth_m": 40.0,
        "floors": 7,
        "floor_height_m": 3.4,
    }
    assert len(graph["voids"]) == 1
    assert graph["voids"][0]["purpose"].startswith("real open interior court")
    assert assemblies["corner_landmark_pavilion"]["kind"] == "rounded_corner_pavilion"
    assert assemblies["corner_landmark_pavilion"]["radius_m"] == 9.5
    assert assemblies["corner_landmark_pavilion"]["balcony_levels_z"] == [4.65, 11.45, 18.25]
    assert assemblies["corner_perimeter_mansard"]["rounded_corner"] == "front_left"
    assert assemblies["corner_right_front_return_glazing"]["span_m"] == 9.5
    assert graph["final_bevel_m"] == 0.0


def test_blender_facade_loader_and_all_view_set_match_quality_contract():
    source = (Path(__file__).parents[1] / "blender_generate.py").read_text(encoding="utf-8")

    role_filter = source.split(
        'for role, band in FACADE_SHEET["manifest"].get("bands", {}).items():', 1
    )[1].split("continue", 1)[0]
    assert '"side"' in role_filter
    for role in ("front_corner_oblique", "rear_corner_oblique", "facade_close"):
        assert f'("{role}"' in source
    assert "+ outward * profile_outward_offset" in source
    assert "base_z + height * 0.10, depth + 0.018, brick" in source
    assert "near_tree_offset = max(width * 0.72, 12.0)" in source
    assert "foreground_tree_x = -max(width * 1.10, 18.0)" in source
    assert "disabled_assembly_ids" in source
    assert "disabled_node_ids" in source
    assert 'kind == "canonical_roof"' in source
    assert 'kind == "mansard_perimeter"' in source
    assert 'kind == "rounded_corner_pavilion"' in source
    assert 'kind == "courtyard_hip_roof"' in source
    assert 'kind == "hip_roof_seam_array"' in source
    assert 'kind == "classical_balustrade_perimeter"' in source
    assert 'kind == "classical_window_array"' in source
    assert "focus_height * 2.75" in source
    assert "focus_height * 2.05" in source


def test_pbr_upgrade_preserves_fixed_end_bays_while_swapping_middle_bays():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from upgrade_facade_pbr import reorder_bays

    source = np.zeros((12, 40, 3), dtype=np.uint8)
    for bay, value in enumerate((30, 80, 150, 220)):
        source[:, bay * 10:(bay + 1) * 10] = value
    result = np.asarray(reorder_bays(Image.fromarray(source), [0, 2, 1, 3]))

    assert result[:, :10].mean() == 30
    assert result[:, 10:20].mean() == 150
    assert result[:, 20:30].mean() == 80
    assert result[:, 30:].mean() == 220


def test_pbr_upgrade_uses_manifest_local_construction_datums(tmp_path):
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from upgrade_facade_pbr import upgrade

    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    elevation = source / "render_locked.png"
    Image.new("RGB", (120, 240), (210, 200, 180)).save(elevation)
    layout = {
        "crops": {
            "crown": [0.0, 0.2],
            "floor": [0.2, 0.4],
            "floor_alt": [0.4, 0.6],
            "podium": [0.6, 1.0],
        },
        "glass_regions": {
            role: [[0.15, 0.2, 0.30, 0.8], [0.65, 0.2, 0.80, 0.8]]
            for role in ("crown", "floor", "floor_alt", "podium")
        },
        "podium_outer_slices": [[0.0, 0.35], [0.65, 1.0]],
        "podium_repeat_glass_regions": [[0.15, 0.2, 0.30, 0.8], [0.65, 0.2, 0.80, 0.8]],
        "entrance_x_bounds": [0.35, 0.65],
        "entrance_glass_regions": [[0.25, 0.2, 0.75, 0.85]],
    }
    manifest = {
        "schema": "facade-sheet@3",
        "family": "render-locked-chateau",
        "archetype_id": "chateauesque_grand_railway_hotel",
        "span_m": 9.0,
        "requested_span_m": 9.6,
        "audited_band_layout": layout,
        "bands": {
            role: {"albedo": f"{role}.png", "height_m": 4.5 if role == "podium" else 3.6}
            for role in ("floor", "floor_alt", "crown", "podium")
        },
    }
    (source / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    path = upgrade(source, output, near_width=96, far_width=48, elevation_override=elevation)
    upgraded = json.loads(path.read_text(encoding="utf-8"))

    assert upgraded["audited_layout_source"] == "manifest"
    assert upgraded["span_m"] == 9.6
    assert upgraded["bands"]["floor"]["source_crop_normalized"] == [0.2, 0.4]
    assert upgraded["bands"]["entrance"]["source_x_bounds_normalized"] == [0.35, 0.65]
    assert (output / "far" / "entrance_albedo.png").exists()


def test_pbr_upgrade_preserves_registered_source_band_glass_masks(tmp_path):
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    from upgrade_facade_pbr import upgrade

    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    elevation = Image.new("RGB", (160, 320), (150, 110, 85))
    elevation.save(source / "elevation_raw.jpg")
    bands = {}
    for role in ("floor", "floor_alt", "side", "crown", "podium"):
        Image.new("RGB", (160, 80), (150, 110, 85)).save(source / f"{role}.png")
        mask = Image.new("L", (160, 80), 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((20, 15, 55, 65), fill=255)
        draw.rectangle((100, 15, 135, 65), fill=255)
        mask.save(source / f"{role}_glass.png")
        bands[role] = {
            "albedo": f"{role}.png",
            "glass_mask": f"{role}_glass.png",
            "height_m": 3.6,
            **({"span_m": 2.5} if role == "side" else {}),
        }
    (source / "manifest.json").write_text(json.dumps({
        "schema": "facade-sheet@4",
        "family": "registered-mask",
        "archetype_id": "test_registered_mask",
        "span_m": 10.0,
        "bands": bands,
    }), encoding="utf-8")

    path = upgrade(source, output, near_width=160, far_width=80)
    upgraded = json.loads(path.read_text(encoding="utf-8"))

    assert upgraded["bands"]["floor"]["audited_openings"] is True
    assert len(upgraded["bands"]["floor"]["glass_regions"]) == 2
    assert upgraded["bands"]["floor_c"]["audited_openings"] is True
    assert len(upgraded["bands"]["floor_c"]["glass_regions"]) >= 2
    assert upgraded["bands"]["side"]["audited_openings"] is True
    assert upgraded["bands"]["side"]["span_m"] == 2.5
    assert (output / "near" / "side_albedo.png").exists()
    assert (output / "near" / "side_glass.png").exists()
    assert all(region[3] - region[1] > 0.5 for region in upgraded["bands"]["floor_c"]["glass_regions"])
    saved = np.asarray(Image.open(output / "near" / "floor_glass.png").convert("L"))
    assert saved[15:66, 20:55].mean() > 245
    assert saved[:, 65:90].mean() < 10


def test_chateauesque_audited_bands_are_single_storeys_with_bounded_openings():
    from upgrade_facade_pbr import (
        CHATEAUESQUE_BAND_CROPS,
        CHATEAUESQUE_GLASS_REGIONS,
    )

    assert set(CHATEAUESQUE_BAND_CROPS) == {"crown", "floor", "floor_alt", "podium"}
    # Repeatable/crown strips must contain one construction storey, never the
    # two-to-four storeys compressed by the legacy automatic slicing.
    for role in ("crown", "floor", "floor_alt"):
        top, bottom = CHATEAUESQUE_BAND_CROPS[role]
        assert 0.075 < bottom - top < 0.12
    assert CHATEAUESQUE_BAND_CROPS["podium"][1] == 1.0

    for role, regions in CHATEAUESQUE_GLASS_REGIONS.items():
        assert 4 <= len(regions) <= 6
        for x0, y0, x1, y1 in regions:
            assert 0.03 <= x1 - x0 <= 0.16
            assert 0.12 <= y1 - y0 <= 0.68
            assert 0.0 < x0 < x1 < 1.0
            assert 0.0 < y0 < y1 < 1.0


def test_pbr_upgrade_emits_registered_material_channels_and_recessed_glass():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    from upgrade_facade_pbr import PBR_KEYS, build_pbr_set

    source = Image.new("RGB", (96, 128), (194, 186, 171))
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle((24, 30, 70, 104), fill=255)
    maps = build_pbr_set(source, mask)

    assert set(maps) == set(PBR_KEYS)
    assert {image.size for image in maps.values()} == {source.size}
    depth = np.asarray(maps["depth"], dtype=np.float32)
    assert depth[60, 45] < depth[10, 10] * 0.5
    assert np.asarray(maps["emissive"])[60, 45].mean() > 40
    assert np.asarray(maps["roughness"])[60, 45] < np.asarray(maps["roughness"])[10, 10]


def test_registered_opening_mask_preserves_rectangles_and_arch_heads(tmp_path):
    from create_registered_opening_mask import build_mask
    from PIL import Image

    source = tmp_path / "elevation.png"
    Image.new("RGB", (100, 100), "white").save(source)
    mask = build_mask(source, {
        "openings": [
            {"shape": "rect", "bbox": [0.1, 0.1, 0.3, 0.4]},
            {"shape": "segmental_arch", "bbox": [0.5, 0.2, 0.9, 0.8], "rise": 0.1},
            {"shape": "pointed_arch", "bbox": [0.35, 0.45, 0.48, 0.9], "rise": 0.15},
        ],
    })

    assert mask.size == (100, 100)
    assert mask.getpixel((20, 20)) == 255
    assert mask.getpixel((70, 20)) == 255
    assert mask.getpixel((50, 20)) == 0
    assert mask.getpixel((70, 70)) == 255
    assert mask.getpixel((32, 50)) == 0
    assert mask.getpixel((42, 45)) == 255
    assert mask.getpixel((35, 45)) == 0
    assert mask.getpixel((36, 61)) == 255


def test_parisian_pbr_manifest_declares_lods_and_semantic_assembly_contract():
    from upgrade_facade_pbr import PBR_KEYS

    path = (
        Path(__file__).parents[1]
        / "facade_sheets_pbr_v15"
        / "parisian-midrise-block"
        / "manifest.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema"] == "facade-sheet@5"
    assert set(payload["pbr_lods"]) == {"near", "far"}
    assert payload["pbr_lods"]["near"]["px"][0] >= 2048
    assert payload["pbr_lods"]["far"]["px"][0] <= 1024
    assert payload["bay_strategy"]["fixed_end_bays"] == [0, 3]
    assert payload["bay_strategy"]["middle_variants"] == ["floor", "floor_alt", "floor_c"]
    for band in payload["bands"].values():
        for lod in ("near", "far"):
            assert set(PBR_KEYS) <= set(band["lods"][lod])


def test_ktx2_packaged_manifest_preserves_modules_and_declares_runtime_delivery():
    from package_ktx2 import TRANSCODER_PATH, packaged_manifest

    source = {
        "family": "pilot",
        "modules": [{"filename": "pilot_floor.glb"}],
        "assembled": {"filename": "pilot_assembled.glb"},
    }
    result = packaged_manifest(source)

    assert result["modules"][0]["filename"] == "pilot_floor.glb"
    assert result["modules"][0]["texture_container"] == "KTX2/UASTC"
    assert result["assembled"]["texture_container"] == "KTX2/UASTC"
    assert result["texture_delivery"]["runtime_transcoder_path"] == TRANSCODER_PATH
    assert result["texture_delivery"]["mipmaps"] is True
    assert result["package_profile"] == "full_family"


def test_ktx2_glb_detection_supports_resumable_packaging(tmp_path):
    import json as json_module
    import struct
    from package_ktx2 import has_ktx2_texture

    payload = json_module.dumps({"extensionsRequired": ["KHR_texture_basisu"]}).encode("utf-8")
    payload += b" " * ((4 - len(payload) % 4) % 4)
    total_length = 20 + len(payload)
    path = tmp_path / "module.glb"
    path.write_bytes(
        b"glTF" + struct.pack("<II", 2, total_length)
        + struct.pack("<II", len(payload), 0x4E4F534A) + payload
    )

    assert has_ktx2_texture(path) is True
