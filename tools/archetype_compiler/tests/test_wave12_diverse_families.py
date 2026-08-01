"""Regression contracts for the three reference-locked Wave 12 families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-31-wave12-vegetation-loadpath-v110"
REQUIRED_CHANNELS = {
    "albedo",
    "normal",
    "roughness",
    "ao",
    "depth",
    "emissive",
    "glass_mask",
    "opaque_mask",
}
SPECS = {
    "vertical-forest-residential": {
        "parent": "vertical_forest_residential",
        "variant": "vertical_forest_bosco",
        "aliases": {
            "vertical_forest_residential",
            "vertical_forest_bosco",
            "bosco_verticale_residential",
            "planted_concrete_balcony_tower",
        },
        "native": (31.537, 31.514, 66.97, 18),
        "source_native": (31.0, 31.0, 69.0),
        "floor_range": (10, 30),
        "profiles": ["rectangle", "courtyard"],
        "glass": "neutral_low_iron_residential_occupied",
        "zone_count": 16,
        "hero_folder": "vertical_forest_residential",
    },
    "collegiate-gothic-gatehouse": {
        "parent": "collegiate_gothic_education",
        "variant": "collegiate_gothic_tudor",
        "aliases": {
            "collegiate_gothic_education",
            "collegiate_gothic_tudor",
            "tudor_gothic_quadrangle",
            "limestone_college_gatehouse",
        },
        "native": (61.767, 51.155, 31.22, 4),
        "source_native": (66.0, 49.0, 31.0),
        "floor_range": (2, 6),
        "profiles": ["rectangle", "u_shape", "courtyard"],
        "glass": "heritage_leaded_occupied",
        "zone_count": 14,
        "hero_folder": "collegiate_gothic_education",
    },
    "cable-stayed-airport-terminal": {
        "parent": "airport_terminal_building",
        "variant": "cable_stayed_steel_truss_terminal",
        "aliases": {
            "airport_terminal_building",
            "cable_stayed_steel_truss_terminal",
            "high_tech_airport_terminal",
            "branching_column_departure_hall",
        },
        "native": (88.32, 72.6, 27.275, 3),
        "source_native": (92.0, 70.0, 28.0),
        "floor_range": (2, 6),
        "profiles": ["rectangle", "l_shape"],
        "glass": "high_transmission_terminal_curtain_wall",
        "zone_count": 14,
        "hero_folder": "airport-terminal-building",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict:
    with path.open("rb") as stream:
        magic, version, _length = struct.unpack("<4sII", stream.read(12))
        assert magic == b"glTF"
        assert version == 2
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        assert chunk_type == 0x4E4F534A
        return json.loads(stream.read(chunk_length).decode("utf-8"))


@pytest.mark.parametrize("family", SPECS)
def test_wave12_manifest_binds_fixed_landmark_and_flexible_stack(family: str):
    spec = SPECS[family]
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")

    assert manifest["manifest_schema"] == 3
    assert manifest["grammar_schema_version"] == 3
    assert manifest["archetype_id"] == spec["parent"]
    assert manifest["variant_id"] == spec["variant"]
    assert manifest["generation_archetype_id"] == spec["variant"]
    assert set(manifest["archetype_aliases"]) == spec["aliases"]
    assert manifest["glass_profile"] == spec["glass"]
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_height_m"],
        manifest["native_floors"],
    ) == spec["native"]
    assert (manifest["min_floors"], manifest["max_floors"]) == spec["floor_range"]
    assert manifest["coordinate_contract"]["origin"] == "bottom centre"
    assert manifest["coordinate_contract"]["gltf_up"] == "+Y (export_yup)"
    assert manifest["coordinate_contract"]["front_facade"] == "-Y in Blender, +Z in glTF"

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == spec["profiles"]
    assert set(compatibility["profiles"]) == set(spec["profiles"])
    assert compatibility["fixedLandmarkScaleBand"]["scaleMin"] <= 0.74
    assert compatibility["fixedLandmarkScaleBand"]["scaleMax"] >= 1.28
    assert compatibility["fixedLandmarkScaleBand"]["maxAxisRatio"] <= 1.24

    modules = manifest["modules"]
    assert len(modules) == 6
    assert {item["role"] for item in modules} == {"podium", "floor", "crown", "roof"}
    assert {
        item["variant_key"] for item in modules if item["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all((root / item["filename"]).is_file() for item in modules)
    assert all(
        item["repeatable_z"] and item["assembly_class"] == "repeatable_middle"
        for item in modules
        if item["role"] == "floor"
    )

    assembled = manifest["assembled"]
    assert assembled["assembly_class"] == "fixed_landmark"
    assert assembled["fixed_semantic"] is True
    assert assembled["repeatable_z"] is False
    assert assembled["source_variant_id"] == spec["variant"]
    assert assembled["generation_archetype_id"] == spec["variant"]
    assert assembled["width_m"] == spec["native"][0]
    assert assembled["depth_m"] == spec["native"][1]
    assert assembled["floors"] == spec["native"][3]
    assert (root / assembled["filename"]).is_file()


@pytest.mark.parametrize("family", SPECS)
def test_wave12_custom_skin_and_generation_provenance_are_complete(family: str):
    spec = SPECS[family]
    root = FAMILIES_ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")

    assert skin["source_model"] == "gpt-image-2"
    registration = skin["reference_registration"]
    assert registration["mode"] == "archetype_specific"
    assert registration["source_archetype_id"] == spec["parent"]
    assert registration["source_variant_id"] == spec["variant"]
    assert registration["generic_tiling_allowed"] is False
    assert set(registration["registered_elevations"]) == {
        "front", "left", "right", "rear", "roof"
    }
    assert "occupied-depth underlay" in registration["uv_strategy"]
    assert len(skin["zones"]) == spec["zone_count"]
    for zone in skin["zones"].values():
        for lod in ("near", "far"):
            assert set(zone[lod]) == REQUIRED_CHANNELS
            assert all((root / path).is_file() for path in zone[lod].values())

    source_root = root / "textures" / "source"
    provenance = load_json(source_root / "reference-generation.json")
    assert provenance["schema"] == "reference-generation@1"
    assert provenance["provider"] == "OpenAI built-in image generation"
    assert provenance["model"] == "gpt-image-2"
    assert provenance["family"] == family
    assert provenance["archetype_id"] == spec["parent"]
    assert provenance["variant_id"] == spec["variant"]
    assert provenance["design_lock"]["native_envelope_dimensions_m"] == list(spec["source_native"])
    assert all(item.get("source_id") for item in provenance["sources"])
    assert all((source_root / item["file"]).is_file() for item in provenance["sources"])
    generated = {
        item["file"]: item
        for item in provenance["sources"]
        if item["file"] in {"archetype-goalpost.png", "material-construction-source-v1.png"}
    }
    assert set(generated) == {"archetype-goalpost.png", "material-construction-source-v1.png"}
    assert all(item.get("prompt") for item in generated.values())


def test_vertical_forest_glb_has_real_supported_planting_and_layered_windows():
    family = "vertical-forest-residential"
    payload = glb_json(FAMILIES_ROOT / family / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert "FOREST_BasePaving" in names
    assert "FOREST_RoofSlab" in names
    assert "FOREST_RoofCore" in names
    assert sum("_BalconyTray" in name for name in names) == 18
    assert sum("Planter" in name and name.endswith("_Soil") for name in names) >= 170
    assert sum("_Tree_Trunk" in name for name in names) >= 170
    assert sum("_Tree_Branch_" in name for name in names) >= 510
    assert sum("_Canopy_Vertical_" in name for name in names) >= 680
    assert not any("Horizontal" in name and "Canopy" in name for name in names)
    assert sum("Window" in name and name.endswith("_Glass") for name in names) >= 280

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "neutral_low_iron_residential_occupied"
        and item.get("reference_locked") is True
        for item in extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in extras)


def test_gothic_glb_has_a_real_gate_passage_court_and_carved_arch():
    family = "collegiate-gothic-gatehouse"
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    graph = manifest["assembled"]["massing_graph"]
    assert graph["open_quadrangle"] is True
    assert graph["real_through_passages"] == 1
    assert graph["pointed_traceried_window_bays"] == 38

    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert {
        "GOTHIC_QuadrangleLawn",
        "GOTHIC_GateTunnelLeftReturn",
        "GOTHIC_GateTunnelRightReturn",
        "GOTHIC_GateTunnelPaving",
        "GOTHIC_GateOakDoorLeft",
        "GOTHIC_GateOakDoorRight",
        "GOTHIC_TowerHeraldicPanel",
    } <= names
    assert sum("GOTHIC_GateSpandrel_" in name for name in names) == 12
    assert sum("GOTHIC_GateTunnelRib_" in name for name in names) == 60
    assert sum("GOTHIC_TowerTraceried_" in name for name in names) >= 75
    assert sum("GOTHIC_Chimney" in name for name in names) >= 24

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "heritage_leaded_occupied"
        and item.get("reference_locked") is True
        for item in extras
    )


def test_terminal_glb_has_one_coherent_roof_load_path_and_gate_system():
    family = "cable-stayed-airport-terminal"
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    graph = manifest["assembled"]["massing_graph"]
    assert graph["branching_tree_columns"] == 6
    assert graph["radiating_stay_cables"] == 10
    assert graph["complete_airside_gate_bridges"] == 3

    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert {
        "TERMINAL_SweepingRoofInfill",
        "TERMINAL_CentralMast",
        "TERMINAL_EntranceCanopyGlass",
        "TERMINAL_Mezzanine",
        "TERMINAL_UpperConcourse",
    } <= names
    assert sum("TERMINAL_RoofDiagonal" in name for name in names) == 192
    assert sum("TERMINAL_TreeColumn" in name for name in names) == 24
    assert sum("TERMINAL_StayCable_" in name for name in names) == 10
    assert sum(name.startswith("TERMINAL_GateBridge_") for name in names) == 3
    assert sum("TERMINAL_GateBridgeBrace" in name for name in names) == 24

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "high_transmission_terminal_curtain_wall"
        and item.get("reference_locked") is True
        for item in extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in extras)


@pytest.mark.parametrize("family", SPECS)
def test_wave12_render_signature_catalogue_and_assessment_bindings(family: str):
    spec = SPECS[family]
    root = FAMILIES_ROOT / family
    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "context",
        "front_elevation",
        "identity_close",
    ):
        assert (root / f"{family}_{role}.png").is_file()
    assert (root / f"{family}_comparison.jpg").is_file()
    assert (root / "elevation.jpg").is_file()

    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    for archetype_id in spec["aliases"]:
        signature = signatures[archetype_id]
        assert signature["archetypeId"] == archetype_id
        assert signature["glassProfile"] == spec["glass"]
        assert signature["elevationUrl"] == f"/families/{family}/elevation.jpg"
        assert signature["identity"]
        assert signature["materialZones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    ids = [item["id"] for item in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))
    entry = next(item for item in catalogue["archetypes"] if item["id"] == spec["parent"])
    assert entry["thumbnailUrl"] == f"/archetypes/buildings/{spec['hero_folder']}/hero.png"
    assert (
        REPO / "frontend" / "public" / "archetypes" / "buildings"
        / spec["hero_folder"] / "hero.png"
    ).is_file()

    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
