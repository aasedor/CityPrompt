"""Regression contracts for the Wave 10 historic daylight factory."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "historic-daylight-factory"
PARENT = "daylight_factory"
VARIANT = "factory_sawtooth_roof"
ALIASES = {
    PARENT,
    VARIANT,
    "historic_daylight_factory",
    "brick_northlight_factory",
}
ROOT = REPO / "frontend" / "public" / "families" / FAMILY
MEMORY_VERSION = "2026-07-30-reference-image-recipe-v108"
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
REQUIRED_ZONES = {
    "facade",
    "podium",
    "floor_a",
    "floor_b",
    "crown",
    "side",
    "interior",
    "red_brick",
    "zinc_roof",
    "black_steel",
    "industrial_glass",
    "limestone",
    "concrete",
    "loading_door",
    "asphalt",
    "timber",
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


def test_manifest_binds_aliases_fixed_landmark_and_flexible_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == ALIASES
    assert manifest["glass_profile"] == "industrial_low_iron_neutral"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (70.0, 50.0, 1)
    assert (manifest["min_floors"], manifest["max_floors"]) == (1, 3)
    assert manifest["coordinate_contract"] == {
        "units": "metres",
        "blender_up": "+Z",
        "gltf_up": "+Y (export_yup)",
        "origin": "bottom centre",
        "front_facade": "-Y in Blender, +Z in glTF",
        "transforms": "applied",
    }

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == [
        "rectangle",
        "l_shape",
        "u_shape",
    ]
    assert set(compatibility["profiles"]) == {
        "rectangle",
        "l_shape",
        "u_shape",
    }
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.70,
        "scaleMax": 1.36,
        "maxAxisRatio": 1.30,
    }
    assert abs(compatibility["preferredBayMultiple_m"] - 60 / 7) < 1e-9

    modules = manifest["modules"]
    assert len(modules) == 6
    assert {module["role"] for module in modules} == {
        "podium",
        "floor",
        "crown",
        "roof",
    }
    assert {
        module["variant_key"]
        for module in modules
        if module["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all(module["width_m"] == 70.0 for module in modules)
    assert all(module["depth_m"] == 50.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "rectangle"
    assert [item["role"] for item in assembled["stack"]] == ["assembled"]
    graph = assembled["massing_graph"]
    assert graph["type"] == "modular_northlight_factory_hall"
    assert graph["northlight_roof_teeth"] == 7
    assert graph["physical_clerestory_assemblies"] == 7
    assert graph["front_steel_sash_window_openings"] == 10
    assert graph["side_steel_sash_window_openings"] == 10
    assert graph["recessed_loading_docks"] == 3
    assert graph["integrated_loading_stair_runs"] == 2
    assert graph["roof_truss_frames"] == 7
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_roof_windows_entry_loading_and_structure():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name", "") for node in payload.get("nodes", [])}

    assert {
        "DAYLIGHT_AdministrationVestibuleLeftPier",
        "DAYLIGHT_AdministrationDoorLeftPane",
        "DAYLIGHT_AdministrationDoorTransomFrame",
        "DAYLIGHT_AdministrationCanopy",
        "DAYLIGHT_FrontWindowGlass_00",
        "DAYLIGHT_FrontWindowGlass_09",
        "DAYLIGHT_RecessedLoadingDoor_0",
        "DAYLIGHT_RecessedLoadingDoor_2",
        "DAYLIGHT_LoadingDockPlatform_1",
        "DAYLIGHT_RearPersonnelDoorBrickHead_-1",
        "DAYLIGHT_RearPersonnelDoorBrickHead_1",
        "DAYLIGHT_LoadingStairTread_-1_00",
        "DAYLIGHT_LoadingStairTread_1_06",
        "DAYLIGHT_RoofToothOpaque_0",
        "DAYLIGHT_RoofToothOpaque_6",
        "DAYLIGHT_RoofToothClerestoryGlass_0",
        "DAYLIGHT_RoofToothClerestoryGlass_6",
        "DAYLIGHT_FactoryExhaustStack",
    } <= node_names
    assert sum(
        bool(re.fullmatch(r"DAYLIGHT_RoofToothOpaque_\d", name))
        for name in node_names
    ) == 7
    assert sum(
        bool(re.fullmatch(r"DAYLIGHT_RoofToothClerestoryGlass_\d", name))
        for name in node_names
    ) == 7
    assert sum("DAYLIGHT_FrontWindowGlass_" in name for name in node_names) == 10
    assert sum("DAYLIGHT_SideWindowGlass_" in name for name in node_names) == 10
    assert sum(
        "DAYLIGHT_RecessedLoadingDoor_" in name for name in node_names
    ) == 3
    assert sum("DAYLIGHT_LoadingStairTread_" in name for name in node_names) == 14
    assert sum("DAYLIGHT_RoofTrussTop_" in name for name in node_names) == 49
    assert sum("Downpipe_" in name for name in node_names) == 10
    assert sum("CorbelBlock_" in name for name in node_names) == 164

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "industrial_low_iron_neutral"
        and extras.get("source_variant_id") == VARIANT
        and extras.get("reference_locked") is True
        and extras.get("pane_recess_m") == 0.23
        and extras.get("interior_depth_m") == 3.2
        for extras in material_extras
    )


def test_custom_skin_and_reference_provenance_are_complete():
    skin = load_json(ROOT / "textures" / "skin_manifest.json")

    assert skin["source_model"] == "gpt-image-2"
    registration = skin["reference_registration"]
    assert registration["source_archetype_id"] == PARENT
    assert registration["source_variant_id"] == VARIANT
    assert registration["generic_tiling_allowed"] is False
    assert {"front", "left", "right", "rear", "roof"} <= set(
        registration["registered_elevations"]
    )
    assert "occupied-depth underlay" in registration["uv_strategy"]
    assert set(skin["zones"]) == REQUIRED_ZONES
    for zone in skin["zones"].values():
        for lod in ("near", "far"):
            assert set(zone[lod]) == REQUIRED_CHANNELS
            assert all((ROOT / path).is_file() for path in zone[lod].values())

    provenance = load_json(
        ROOT / "textures" / "source" / "reference-generation.json"
    )
    assert provenance["schema"] == "reference-generation@1"
    assert provenance["family"] == FAMILY
    assert provenance["archetype_id"] == PARENT
    assert provenance["variant_id"] == VARIANT
    assert len(provenance["research"]) >= 3
    outputs = {item["file"]: item for item in provenance["sources"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "loading-court-source-v1.png",
        "aerial-roof-source-v1.png",
        "occupied-workshop-source-v1.png",
        "material-construction-source-v1.png",
    } == set(outputs)
    assert all(item.get("source_id") for item in outputs.values())
    assert all(item.get("prompt_summary") for item in outputs.values())


def test_render_set_signatures_and_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_elevation",
        "rear_loading",
        "aerial",
        "roof_close",
        "window_close",
        "entrance_close",
        "front_corner_oblique",
        "rear_corner_oblique",
        "facade_close",
        "context",
    ):
        assert (ROOT / f"{FAMILY}_{role}.png").is_file()
    assert (ROOT / f"{FAMILY}_comparison.jpg").is_file()
    assert (ROOT / "elevation.jpg").is_file()

    signatures_path = (
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )
    signature_text = signatures_path.read_text(encoding="utf-8")
    for archetype_id in ALIASES:
        assert signature_text.count(f'"{archetype_id}":') == 1
    signatures = load_json(signatures_path)["families"]
    for archetype_id in ALIASES:
        signature = signatures[archetype_id]
        assert signature["archetypeId"] == archetype_id
        assert signature["glassProfile"] == "industrial_low_iron_neutral"
        assert signature["elevationUrl"] == f"/families/{FAMILY}/elevation.jpg"
        assert signature["identity"]
        assert signature["materialZones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    ids = [entry["id"] for entry in catalogue["archetypes"]]
    assert ids.count(PARENT) == 1
    entry = next(item for item in catalogue["archetypes"] if item["id"] == PARENT)
    assert entry["thumbnailUrl"] == (
        "/archetypes/buildings/historic-daylight-factory/hero.png"
    )
    compatibility = entry["footprintCompatibility"]
    assert compatibility["preferredProfiles"] == [
        "rectangle",
        "l_shape",
        "u_shape",
    ]
    assert set(compatibility["profiles"]) == {
        "rectangle",
        "l_shape",
        "u_shape",
    }
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.70,
        "scaleMax": 1.36,
        "maxAxisRatio": 1.3,
    }
    selected = next(
        variant for variant in entry["variants"] if variant["id"] == VARIANT
    )
    assert selected["thumbnailUrl"] == entry["thumbnailUrl"]
    assert (
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / FAMILY
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
