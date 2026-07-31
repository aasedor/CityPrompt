"""Regression contracts for the Wave 10 mass-timber fire-station family."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "modern-fire-station-mass-timber"
PARENT = "modern_fire_station"
VARIANT = "fire_mass_timber"
ROOT = REPO / "frontend" / "public" / "families" / FAMILY
MEMORY_VERSION = "2026-07-30-reference-image-recipe-v107"
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
    "apparatus",
    "honey_timber",
    "glulam",
    "charred_timber",
    "concrete",
    "green_roof",
    "solar_metal",
    "paving",
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


def test_manifest_binds_aliases_and_flexible_operational_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == {PARENT, VARIANT}
    assert manifest["glass_profile"] == "timber_station_neutral_low_e"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (40.0, 35.0, 2)
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
    assert compatibility["minimumPreferredProfiles"] == 3
    assert set(compatibility["profiles"]) == {
        "rectangle",
        "l_shape",
        "u_shape",
    }
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.7,
        "scaleMax": 1.35,
        "maxAxisRatio": 1.34,
    }
    assert compatibility["preferredBayMultiple_m"] == 7.5

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
    assert all(module["width_m"] == 40.0 for module in modules)
    assert all(module["depth_m"] == 35.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "rectangle"
    graph = assembled["massing_graph"]
    assert graph["type"] == "three_lane_mass_timber_fire_station"
    assert graph["apparatus_lanes"] == 3
    assert graph["drive_through"] is True
    assert graph["integrated_training_tower"] is True
    assert graph["occupied_crew_gallery"] is True
    assert graph["photovoltaic_arrays"] == 2
    assert [item["role"] for item in assembled["stack"]] == [
        "podium",
        "floor",
        "crown",
        "roof",
    ]
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_bays_engines_stairs_windows_and_roof():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "FireFrontApparatusDoor_1_PhysicalFourFoldGlass",
        "FireFrontApparatusDoor_2_PhysicalFourFoldGlass",
        "FireFrontApparatusDoor_3_PhysicalFourFoldGlass",
        "FireRearApparatusDoor_1_PhysicalFourFoldGlass",
        "FireRearApparatusDoor_2_PhysicalFourFoldGlass",
        "FireRearApparatusDoor_3_PhysicalFourFoldGlass",
        "FireEngine1_Cab",
        "FireEngine2_Cab",
        "FireEngine3_Cab",
        "FirePublicEntryOccupiedLobbyDepth",
        "FirePodiumIntegratedTrainingTower_RealMidLanding",
        "FireRoofMeadowBuildUp",
        "FireRoofSouthPV_PhotovoltaicPanel_0_0",
        "FireRoofNorthPV_PhotovoltaicPanel_1_6",
    } <= node_names
    assert sum(
        bool(name and "PhysicalFourFoldGlass" in name) for name in node_names
    ) == 6
    assert sum(bool(name and "PhysicalLowEPane" in name) for name in node_names) >= 20
    assert sum(bool(name and "RealTread" in name) for name in node_names) >= 60
    assert sum(
        bool(name and "PhotovoltaicPanel" in name) for name in node_names
    ) == 30
    assert sum(bool(name and "FireEngine" in name) for name in node_names) >= 50
    assert sum(
        bool(name and "FireUpperGalleryPlanter" in name) for name in node_names
    ) == 4

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "timber_station_neutral_low_e"
        and extras.get("source_variant_id") == VARIANT
        for extras in material_extras
    )
    assert any(
        extras.get("channel_glass") is True
        and extras.get("reference_locked") is True
        for extras in material_extras
    )
    assert sum(
        extras.get("underlay_role")
        == "occupied_depth_behind_physical_glazing"
        for extras in material_extras
    ) >= 2
    assert any(
        "normal" in str(extras.get("pbr_channels", ""))
        and "depth" in str(extras.get("pbr_channels", ""))
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
    assert provenance["schema"] == "reference-generation-provenance@2"
    assert provenance["family"] == FAMILY
    assert provenance["archetype_id"] == PARENT
    assert provenance["variant_id"] == VARIANT
    assert len(provenance["research"]) >= 7
    outputs = {item["file"]: item for item in provenance["assets"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "aerial-roof-source-v1.png",
        "rear-service-source-v1.png",
        "material-construction-source-v1.png",
        "glazing-occupied-depth-source-v1.png",
        "integrated-training-tower-source-v1.png",
    } == set(outputs)
    assert all(
        item.get("prompt") or item.get("prompt_chain")
        for item in outputs.values()
    )
    assert all(
        (ROOT / "textures" / "source" / filename).is_file()
        for filename in outputs
    )


def test_render_set_signatures_and_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "apparatus_close",
        "tower_close",
        "roof_close",
        "side_close",
        "context",
    ):
        assert (ROOT / f"{FAMILY}_{role}.png").is_file()
    assert (ROOT / f"{FAMILY}_comparison.jpg").is_file()
    assert (ROOT / "elevation.jpg").is_file()

    signatures_path = (
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )
    signature_text = signatures_path.read_text(encoding="utf-8")
    assert signature_text.count(f'"{PARENT}":') == 1
    assert signature_text.count(f'"{VARIANT}":') == 1
    signatures = load_json(signatures_path)["families"]
    for archetype_id in (PARENT, VARIANT):
        signature = signatures[archetype_id]
        assert signature["archetypeId"] == archetype_id
        assert signature["glassProfile"] == "timber_station_neutral_low_e"
        assert signature["elevationUrl"] == f"/families/{FAMILY}/elevation.jpg"
        assert signature["identity"]
        assert signature["materialZones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    assert len(catalogue["archetypes"]) == 224
    ids = [entry["id"] for entry in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))
    entry = next(item for item in catalogue["archetypes"] if item["id"] == PARENT)
    assert entry["thumbnailUrl"] == (
        "/archetypes/buildings/modern-fire-station-mass-timber/hero.png"
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
        / "modern-fire-station-mass-timber"
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
