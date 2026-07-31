"""Regression contracts for the Wave 10 corten-arch university library."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "corten-arch-university-library"
PARENT = "university_library"
VARIANT = "contemporary_corten_arch"
ALIASES = {
    PARENT,
    VARIANT,
    "corten_arch_university_library",
    "sculptural_campus_library",
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
    "corten",
    "board_concrete",
    "bronze_steel",
    "low_iron_glass",
    "oak",
    "precast",
    "roof_membrane",
    "vegetation",
    "asphalt",
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
    assert manifest["glass_profile"] == "library_neutral_low_iron_clear"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_height_m"],
        manifest["native_floors"],
    ) == (70.0, 56.0, 25.0, 4)
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
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert set(compatibility["profiles"]) == {"rectangle"}
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.76,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.2,
    }
    assert compatibility["recommendedWidth_m"] == [44.0, 90.0]
    assert compatibility["recommendedDepth_m"] == [34.0, 70.0]

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
    assert all(module["depth_m"] == 56.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["assembly_class"] == "fixed_landmark"
    assert assembled["source_variant_id"] == VARIANT
    assert assembled["generation_archetype_id"] == VARIANT
    assert assembled["footprint_profile"] == "rectangle"
    assert [item["role"] for item in assembled["stack"]] == ["assembled"]
    graph = assembled["massing_graph"]
    assert graph["type"] == "fixed_landmark"
    assert graph["continuous_barrel_arch_shells"] == 1
    assert graph["occupied_reading_storeys"] == 4
    assert graph["front_triangular_lattice"] is True
    assert graph["public_entry_doors"] == 5
    assert graph["ceremonial_stair_risers"] == 12
    assert graph["accessible_side_ramps"] == 2
    assert graph["linear_crown_skylights"] == 1
    assert graph["side_reading_window_panes"] == 20
    assert graph["shell_drainage_downpipes"] == 4
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_constructed_shell_glass_entry_and_occupied_depth():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name", "") for node in payload.get("nodes", [])}

    assert {
        "LIBRARY_FrontArchGlass",
        "LIBRARY_RearArchGlass",
        "LIBRARY_FrontCortenPortalRing_00",
        "LIBRARY_FrontCortenPortalRing_39",
        "LIBRARY_RearCortenPortalRing_00",
        "LIBRARY_RearCortenPortalRing_39",
        "LIBRARY_CeremonialStairTread_00",
        "LIBRARY_CeremonialStairTread_11",
        "LIBRARY_AccessibleEntryRamp_-1",
        "LIBRARY_AccessibleEntryRamp_1",
        "LIBRARY_EntranceDoorGlass_0",
        "LIBRARY_EntranceDoorGlass_4",
        "LIBRARY_CrownSkylightGlass",
        "LIBRARY_SideWindowConcretePlinth_-1",
        "LIBRARY_SideWindowConcretePlinth_1",
        "LIBRARY_Downpipe_-1_0",
        "LIBRARY_Downpipe_1_1",
    } <= node_names
    assert sum("CortenShellPanel_" in name for name in node_names) == 250
    assert sum("FrontCortenPortalRing_" in name for name in node_names) == 40
    assert sum("RearCortenPortalRing_" in name for name in node_names) == 40
    assert sum("InnerArchRib_" in name for name in node_names) == 320
    assert sum("SideReadingGlass_" in name for name in node_names) == 20
    assert sum("CeremonialStairTread_" in name for name in node_names) == 12
    assert sum(
        bool(re.fullmatch(r"LIBRARY_EntranceDoorGlass_\d", name))
        for name in node_names
    ) == 5
    assert sum("ReadingFloorPlate_" in name for name in node_names) == 8
    assert sum("BookStackCase_" in name for name in node_names) == 32
    assert sum("Downpipe_" in name for name in node_names) == 4

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "library_neutral_low_iron_clear"
        and extras.get("source_variant_id") == VARIANT
        and extras.get("generation_archetype_id") == VARIANT
        and extras.get("reference_locked") is True
        and extras.get("pane_recess_m") == 2.15
        and extras.get("interior_depth_m") == 6.4
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
    assert "true-scale material zones" in registration["uv_strategy"]
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
    assert len(provenance["research"]) >= 5
    outputs = {item["file"]: item for item in provenance["sources"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "rear-corner-source-v1.png",
        "aerial-roof-source-v1.png",
        "occupied-library-source-v1.png",
        "material-construction-source-v1.png",
    } == set(outputs)
    assert all(item.get("source_id") for item in outputs.values())
    assert all(item.get("prompt_summary") for item in outputs.values())


def test_render_set_signatures_and_catalogue_card_are_bound():
    for role in (
        "preview",
        "street",
        "front_elevation",
        "rear_corner",
        "aerial",
        "shell_close",
        "curtainwall_close",
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
        assert signature["glassProfile"] == "library_neutral_low_iron_clear"
        assert signature["elevationUrl"] == f"/families/{FAMILY}/elevation.jpg"
        assert signature["identity"]
        assert signature["materialZones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    ids = [entry["id"] for entry in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))
    assert ids.count(PARENT) == 1
    entry = next(item for item in catalogue["archetypes"] if item["id"] == PARENT)
    assert entry["thumbnailUrl"] == (
        "/archetypes/buildings/corten-arch-university-library/hero.png"
    )
    compatibility = entry["footprintCompatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert set(compatibility["profiles"]) == {"rectangle"}
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.76,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.2,
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
