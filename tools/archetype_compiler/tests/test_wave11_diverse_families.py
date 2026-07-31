"""Regression contracts for the three reference-locked Wave 11 families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-31-wave11-optical-curve-v109"
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
    "coastal-mediterranean-resort": {
        "parent": "coastal_resort_terrace_block",
        "variant": "coastal_resort_white_mediterranean",
        "aliases": {
            "coastal_resort_terrace_block",
            "coastal_resort_white_mediterranean",
            "coastal_mediterranean_resort",
            "white_mediterranean_resort_block",
        },
        "native": (40.0, 28.0, 13.4, 3),
        "floor_range": (3, 8),
        "profiles": ["rectangle"],
        "glass": "coastal_residential_low_iron",
        "zone_count": 17,
        "hero_folder": "coastal_resort_terrace_block",
    },
    "skyline-glass-office-cluster": {
        "parent": "skyline_glass_office_cluster",
        "variant": "skyline_cluster_staggered",
        "aliases": {
            "skyline_glass_office_cluster",
            "skyline_cluster_staggered",
            "staggered_glass_office_cluster",
            "three_tower_skybridge_cluster",
        },
        "native": (70.0, 40.0, 76.1, 17),
        "floor_range": (8, 30),
        "profiles": ["rectangle"],
        "glass": "neutral_low_e_office_curtain_wall",
        "zone_count": 14,
        "hero_folder": "skyline_glass_office_cluster",
    },
    "autonomous-tech-campus-silicon-valley": {
        "parent": "autonomous_tech_campus",
        "variant": "tech_campus_silicon_valley",
        "aliases": {
            "autonomous_tech_campus",
            "tech_campus_silicon_valley",
            "silicon_valley_research_campus",
            "white_steel_technology_pavilions",
        },
        "native": (74.0, 54.0, 13.4, 3),
        "floor_range": (2, 7),
        "profiles": ["rectangle", "l_shape", "u_shape"],
        "glass": "low_iron_research_pavilion",
        "zone_count": 14,
        "hero_folder": "autonomous_tech_campus",
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
def test_wave11_manifest_binds_landmark_aliases_and_flexible_stack(family: str):
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
    assert compatibility["fixedLandmarkScaleBand"]["scaleMin"] < 1.0
    assert compatibility["fixedLandmarkScaleBand"]["scaleMax"] > 1.0
    assert compatibility["fixedLandmarkScaleBand"]["maxAxisRatio"] <= 1.20

    modules = manifest["modules"]
    assert len(modules) == 6
    assert {item["role"] for item in modules} == {"podium", "floor", "crown", "roof"}
    assert {
        item["variant_key"] for item in modules if item["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all(item["width_m"] == spec["native"][0] for item in modules)
    assert all(item["depth_m"] == spec["native"][1] for item in modules)
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
def test_wave11_custom_skin_and_generation_provenance_are_complete(family: str):
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
        "front",
        "left",
        "right",
        "rear",
        "roof",
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
    assert provenance["design_lock"]["native_envelope_dimensions_m"] == list(spec["native"][:3])
    assert all(item.get("source_id") for item in provenance["sources"])
    assert all((source_root / item["file"]).is_file() for item in provenance["sources"])
    generated = {
        item["file"]: item
        for item in provenance["sources"]
        if item["file"] in {"archetype-goalpost.png", "material-construction-source-v1.png"}
    }
    assert set(generated) == {"archetype-goalpost.png", "material-construction-source-v1.png"}
    assert all(item.get("prompt") for item in generated.values())


def test_coastal_glb_constructs_curves_pool_stair_and_open_pergolas():
    family = "coastal-mediterranean-resort"
    payload = glb_json(FAMILIES_ROOT / family / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert {
        "COASTAL_PoolWater",
        "COASTAL_EntryStair_00",
        "COASTAL_EntryStair_04",
        "COASTAL_MainRoofDeck",
        "COASTAL_Second_Opening00_ArchSpandrel",
        "COASTAL_RoofPergola_Rafter_13",
    } <= names
    assert sum("ArchSpandrel" in name for name in names) == 3
    assert sum("CurvedHead" in name for name in names) == 12
    assert sum("EntryStair" in name for name in names) == 5

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "coastal_residential_low_iron"
        and item.get("reference_locked") is True
        and "normal" in str(item.get("pbr_channels", ""))
        for item in extras
    )


def test_skyline_glb_keeps_three_towers_two_bridges_and_layered_glass():
    family = "skyline-glass-office-cluster"
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    graph = manifest["assembled"]["massing_graph"]
    assert graph["tower_count"] == 3
    assert graph["enclosed_skybridges"] == 2
    assert graph["stepped_glazed_crowns"] == 3

    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert sum("LeftLowerBridge" in name for name in names) == 15
    assert sum("RightUpperBridge" in name for name in names) == 15
    assert sum("Crown_RoofDeck" in name for name in names) == 3
    assert "SKYLINE_Centre_Crown_CentreMast" in names

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "neutral_low_e_office_curtain_wall"
        and item.get("reference_locked") is True
        for item in extras
    )
    assert any(
        item.get("occupied_depth_layer") is True
        and item.get("warmth_reference_locked") is True
        for item in extras
    )


def test_campus_glb_keeps_u_court_pv_canopy_and_occupied_labs():
    family = "autonomous-tech-campus-silicon-valley"
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    graph = manifest["assembled"]["massing_graph"]
    assert graph["pavilion_wings"] == 3
    assert graph["open_landscaped_courtyard"] is True
    assert graph["glazed_connectors"] == 2
    assert graph["photovoltaic_fields"] == 3

    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert "CAMPUS_ArrivalCanopy" in names
    assert sum("ArrivalCanopyPost" in name for name in names) == 4
    assert sum("WestPV_Panel" in name for name in names) == 56
    assert sum("EastPV_Panel" in name for name in names) == 56
    assert sum("RearPV_Panel" in name for name in names) == 18
    assert sum("MechanicalLouver" in name for name in names) == 30
    assert {"CAMPUS_WestConnectorGlass", "CAMPUS_EastConnectorGlass"} <= names

    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == "low_iron_research_pavilion"
        and item.get("reference_locked") is True
        for item in extras
    )
    assert any(
        item.get("occupied_depth_layer") is True
        and item.get("warmth_reference_locked") is True
        for item in extras
    )


@pytest.mark.parametrize("family", SPECS)
def test_wave11_render_signature_catalogue_and_assessment_bindings(family: str):
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
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / spec["hero_folder"]
        / "hero.png"
    ).is_file()

    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
