"""Regression contracts for the Wave 10 prairie courtyard motor inn."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "prairie-courtyard-motor-inn"
PARENT = "highway_motor_hotel"
VARIANT = "hotel_two_storey_motor_inn"
ALIASES = {
    PARENT,
    VARIANT,
    "prairie_courtyard_motor_inn",
    "two_storey_exterior_corridor_motel",
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
    "ivory_stucco",
    "russet_brick",
    "charcoal_shingles",
    "cedar_soffit",
    "kelp_door",
    "black_steel",
    "low_e_glass",
    "pale_concrete",
    "pool_water",
    "asphalt",
    "room_curtain",
    "service_metal",
    "landscape_gravel",
    "prairie_planting",
    "interior_wood",
    "warm_light",
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


def test_manifest_binds_aliases_landmark_and_flexible_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == ALIASES
    assert manifest["glass_profile"] == "low_iron_neutral"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (64.0, 36.0, 2)
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
        "scaleMin": 0.72,
        "scaleMax": 1.34,
        "maxAxisRatio": 1.3,
    }
    assert compatibility["preferredBayMultiple_m"] == 4.2

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
    assert all(module["width_m"] == 64.0 for module in modules)
    assert all(module["depth_m"] == 36.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "l_shape"
    assert [item["role"] for item in assembled["stack"]] == ["assembled"]
    graph = assembled["massing_graph"]
    assert graph["type"] == "modular_exterior_corridor_motor_inn"
    assert graph["main_guest_wing_bays"] == 10
    assert graph["return_guest_wing_bays"] == 4
    assert graph["occupied_guest_room_modules"] == 28
    assert graph["integrated_stair_assemblies"] == 2
    assert graph["inside_corner_glazed_lobby"] == 1
    assert graph["pool_basins"] == 1
    assert graph["rear_condenser_units"] == 5
    assert graph["screened_refuse_bins"] == 2
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_constructed_rooms_stairs_lobby_pool_and_service():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name", "") for node in payload.get("nodes", [])}

    assert {
        "ROOM_south_0_00_Door",
        "ROOM_south_0_00_Mullion",
        "ROOM_west_1_03_Door",
        "STAIR_MainWing_Tread_00",
        "STAIR_ReturnWing_Tread_17",
        "LOBBY_ProjectingSouthGlass_0_0",
        "LOBBY_ProjectingVestibuleDoor_0",
        "LOBBY_PorteCochereRoof",
        "POOL_Water",
        "POOL_CabanaRoof",
        "SERVICE_RefuseBin_0",
        "SERVICE_RefuseBin_1",
    } <= node_names
    assert sum(
        bool(re.fullmatch(r"STAIR_(MainWing|ReturnWing)_Tread_\d\d", name))
        for name in node_names
    ) == 36
    assert sum(
        "LOBBY_ProjectingSouthGlass_" in name for name in node_names
    ) == 8
    assert sum(
        "POOL_FencePicket_" in name for name in node_names
    ) >= 100
    assert sum(
        "SITE_PrairieGrass_" in name and "_Blade_" in name
        for name in node_names
    ) == 152

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "low_iron_neutral"
        and extras.get("source_variant_id") == VARIANT
        and extras.get("reference_locked") is True
        and extras.get("pane_recess_m") == 0.18
        and extras.get("interior_depth_m") == 3.2
        for extras in material_extras
    )
    assert any(
        extras.get("glazing_profile") == "low_iron_neutral"
        and extras.get("interior_depth_m") == 8.0
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
    assert len(provenance["research"]) >= 4
    outputs = {item["file"]: item for item in provenance["sources"]}
    assert {
        "archetype-goalpost.png",
        "aerial-roof-source-v1.png",
        "courtyard-elevation-source-v1.png",
        "integrated-stair-source-v1.png",
        "lobby-entry-source-v1.png",
        "rear-service-source-v1.png",
        "guest-window-source-v1.png",
        "material-construction-source-v1.png",
    } == set(outputs)
    assert all(item.get("source_id") for item in outputs.values())
    assert all(item.get("prompt_summary") for item in outputs.values())


def test_render_set_signatures_and_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "stair_close",
        "window_close",
        "lobby_close",
        "service_close",
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
        assert signature["glassProfile"] == "low_iron_neutral"
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
        "/archetypes/buildings/prairie-courtyard-motor-inn/hero.png"
    )
    assert entry["footprintCompatibility"]["preferredProfiles"] == [
        "rectangle",
        "l_shape",
        "u_shape",
    ]
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
