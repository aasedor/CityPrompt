"""Regression contracts for the Wave 10 Cedar & Black-Metal townhomes."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "rndsqr-cedar-black-townhomes"
PARENT = "rndsqr_missing_middle_townhomes"
VARIANT = "rndsqr_townhome_dark_wood_metal"
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
    "cedar",
    "metal",
    "concrete",
    "roof",
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


def test_manifest_binds_aliases_four_homes_and_flexible_lego_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == {PARENT, VARIANT}
    assert manifest["glass_profile"] == "residential_low_e"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (28.0, 14.0, 3)
    assert (manifest["min_floors"], manifest["max_floors"]) == (2, 4)
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
        "scaleMin": 0.72,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.24,
    }
    assert all(
        profile["preferredBayMultiple_m"] == 7.0
        for profile in compatibility["profiles"].values()
    )

    modules = manifest["modules"]
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
    assert all(module["width_m"] == 28.0 for module in modules)
    assert all(module["depth_m"] == 14.0 for module in modules)
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
    assert assembled["massing_graph"]["type"] == "four_attached_dwelling_row"
    assert assembled["massing_graph"]["dwelling_count"] == 4
    assert assembled["massing_graph"]["private_roof_terraces"] == 4
    assert assembled["massing_graph"]["rear_lane_service"] is True
    assert len(assembled["footprint_target"]["segments"]) == 4
    assert [item["role"] for item in assembled["stack"]] == [
        "podium",
        "floor",
        "floor",
        "crown",
        "roof",
    ]
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_entries_garages_windows_and_roof_terraces():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "podium_default_Unit1_Entry_LeftCedarJamb",
        "podium_default_Unit4_LaneGarage_InsulatedDoor",
        "floor_typical_a_Unit2_FrontWindow_0_PhysicalLowEPane",
        "floor_typical_b_RightWindow_1_PhysicalLowEPane",
        "Roof_Unit1_StairBulkhead",
        "Roof_Unit4_StairBulkhead",
        "Roof_PartyDivider_1_Top",
        "Roof_Unit3_TerraceMembrane",
    } <= node_names
    assert sum(
        bool(name and "PhysicalLowEPane" in name) for name in node_names
    ) >= 28
    assert sum(
        bool(name and "LaneGarage_InsulatedDoor" in name) for name in node_names
    ) == 4
    assert sum(bool(name and "_Entry_MatteBlackDoor" in name) for name in node_names) == 4
    assert sum(bool(name and "_StairBulkhead" in name) for name in node_names) == 4
    assert sum(bool(name and "CedarPrivacyFin" in name) for name in node_names) >= 32
    assert sum(bool(name and "JulietBar" in name) for name in node_names) >= 40

    material_extras = [
        material.get("extras", {}) for material in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "residential_low_e"
        and extras.get("source_variant_id") == VARIANT
        for extras in material_extras
    )
    assert any(
        extras.get("reference_locked") is True
        and extras.get("underlay_role")
        == "occupied_depth_behind_physical_glazing"
        for extras in material_extras
    )
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
    assert provenance["schema"] == "reference-generation@2"
    assert provenance["provider"] == "OpenAI built-in ImageGen"
    assert provenance["model"] == "gpt-image-2"
    assert provenance["generated_at"] == "2026-07-30"
    assert provenance["saved_output_path"] == "textures/source"
    assert provenance["output_role"] == "render_locked_source_package"
    assert {
        "front",
        "left",
        "right",
        "rear",
        "roof",
        "cedar",
        "charcoal_corrugated_metal",
        "glazing_occupied_depth",
    } <= set(provenance["registered_surfaces"])
    assert {
        "original_goalpost",
        "rectified_front_elevation",
        "roof_or_aerial",
        "secondary_elevation",
        "shadow_neutral_material_study",
        "occupied_depth_plate",
    } == set(provenance["prompt_fields"])
    assert len(provenance["outputs"]) == 7
    assert {
        "archetype-goalpost.png",
        "elevation-source-v1.png",
        "aerial-source-v1.png",
        "rear-elevation-source-v1.png",
        "cedar-material-source-v1.png",
        "charcoal-metal-material-source-v1.png",
        "occupied-depth-source-v1.png",
    } == {item["file"] for item in provenance["outputs"]}
    assert provenance["goalpost_prompt"]
    assert provenance["elevation_prompt"]
    assert provenance["aerial_prompt"]
    assert provenance["rear_elevation_prompt"]
    assert provenance["occupied_depth_prompt"]
    assert provenance["material_prompts"]["cedar"]
    assert provenance["material_prompts"]["charcoal_corrugated_metal"]


def test_render_set_signatures_and_existing_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "identity_close",
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
        assert signature["glassProfile"] == "residential_low_e"
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
        "/archetypes/buildings/rndsqr-cedar-black-townhomes/hero.png"
    )
    assert entry["footprintCompatibility"]["preferredProfiles"] == [
        "rectangle",
        "l_shape",
        "u_shape",
    ]
    selected = next(variant for variant in entry["variants"] if variant["id"] == VARIANT)
    assert selected["thumbnailUrl"] == entry["thumbnailUrl"]
    assert (
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / "rndsqr-cedar-black-townhomes"
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
