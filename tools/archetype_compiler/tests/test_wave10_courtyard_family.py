"""Regression contracts for the Wave 10 Modern Brick Mews pilot."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "courtyard-family-brick-mews"
PARENT = "courtyard_family_housing"
VARIANT = "courtyard_family_brick_modern"
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
    "brick",
    "metal",
    "roof",
    "paving",
    "soffit",
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


def test_manifest_binds_aliases_open_court_and_flexible_lego_stack():
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
    ) == (28.0, 24.0, 3)
    assert (manifest["min_floors"], manifest["max_floors"]) == (2, 6)
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
        "courtyard",
        "u_shape",
        "rectangle",
    ]
    assert compatibility["minimumPreferredProfiles"] == 3
    assert set(compatibility["profiles"]) == {
        "courtyard",
        "u_shape",
        "rectangle",
    }
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.84,
        "scaleMax": 1.16,
        "maxAxisRatio": 1.15,
    }
    assert compatibility["profiles"]["courtyard"]["minimumCourtyard_m"] == 8.0
    assert compatibility["profiles"]["courtyard"]["wingDepth_m"] == [4.6, 7.0]

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
    assert all(module["depth_m"] == 5.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "courtyard"
    assert assembled["massing_graph"]["type"] == "open_courtyard_perimeter"
    assert assembled["massing_graph"]["roof_void_preserved"] is True
    assert (
        assembled["massing_graph"]["court_width_m"],
        assembled["massing_graph"]["court_depth_m"],
    ) == (18.0, 14.0)
    assert len(assembled["footprint_target"]["segments"]) == 4
    assert [item["role"] for item in assembled["stack"]] == [
        "podium",
        "floor",
        "floor",
        "crown",
        "roof",
    ]
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_courtyard_passage_roof_windows_and_bicycles():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "MEWS_OpenToSkyCourtyard_Paving",
        (
            "MEWS_PublicStreetWing_ThroughCarriagePassage_"
            "ContinuousSegmentalBrickBarrel"
        ),
        "MEWS_PublicStreetWing_ConnectedPitchedRoof",
        "MEWS_RearGardenWing_ConnectedPitchedRoof",
        "MEWS_LeftReturnWing_ConnectedPitchedRoof",
        "MEWS_RightReturnWing_ConnectedPitchedRoof",
        "MEWS_CornerRoof_-1_-1_FourPlaneHipRoof",
        "MEWS_CornerRoof_-1_-1_FrontRidgeContinuation",
        "MEWS_CornerRoof_-1_-1_ReturnRidgeContinuation",
        "MEWS_PublicStreetWing_RearGround_CourtyardBicycle_0_Wheel_0",
    } <= node_names
    assert sum(
        bool(name and "PhysicalLowEPane" in name) for name in node_names
    ) >= 100
    assert sum(
        bool(name and "IntegratedJuliet" in name) for name in node_names
    ) >= 200
    assert sum(bool(name and "StoredBicycle" in name) for name in node_names) >= 12

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
        "courtyard",
        "roof",
        "glazing_occupied_depth",
    } <= set(provenance["registered_surfaces"])
    assert {
        "rectified_front_elevation",
        "roof_or_aerial",
        "courtyard_or_secondary_elevation",
        "shadow_neutral_material_study",
        "occupied_depth_plate",
    } == set(provenance["prompt_fields"])
    assert len(provenance["outputs"]) == 5
    assert {
        "elevation-source-v1.png",
        "aerial-source-v1.png",
        "courtyard-source-v1.png",
        "buff-brick-material-source-v1.png",
        "occupied-depth-source-v1.png",
    } == {item["file"] for item in provenance["outputs"]}
    assert provenance["elevation_prompt"]
    assert provenance["aerial_prompt"]
    assert provenance["courtyard_prompt"]
    assert provenance["occupied_depth_prompt"]
    assert provenance["material_prompts"]["brick"]


def test_render_set_signatures_and_existing_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "identity_close",
        "courtyard_close",
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
        "/archetypes/buildings/courtyard_family_housing/hero.png"
    )
    assert entry["footprintCompatibility"]["preferredProfiles"] == [
        "courtyard",
        "u_shape",
        "rectangle",
    ]
    assert any(variant["id"] == VARIANT for variant in entry["variants"])
    assert (
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / "courtyard_family_housing"
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
