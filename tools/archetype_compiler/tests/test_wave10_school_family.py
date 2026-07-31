"""Regression contracts for the Wave 10 Third Republic school family."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "ecole-republicaine-third-republic"
PARENT = "ecole_republicaine"
VARIANT = "ecole-republicaine-third-republic-original"
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
    "limestone",
    "meuliere",
    "slate",
    "zinc",
    "green_wood",
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


def test_manifest_binds_school_aliases_and_flexible_lego_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == {PARENT, VARIANT}
    assert manifest["glass_profile"] == "heritage_sash_occupied"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (40.0, 15.0, 2)
    assert (manifest["min_floors"], manifest["max_floors"]) == (2, 3)
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
        "scaleMin": 0.75,
        "scaleMax": 1.32,
        "maxAxisRatio": 1.35,
    }
    assert compatibility["preferredBayMultiple_m"] == 4.4

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
    assert all(module["width_m"] == 40.0 for module in modules)
    assert all(module["depth_m"] == 15.0 for module in modules)
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
    assert assembled["massing_graph"]["type"] == (
        "symmetrical_third_republic_school_bar"
    )
    assert assembled["massing_graph"]["public_entrances"] == 3
    assert assembled["massing_graph"]["clock_pavilion"] is True
    assert len(assembled["footprint_target"]["segments"]) == 3
    assert [item["role"] for item in assembled["stack"]] == [
        "podium",
        "floor",
        "crown",
        "roof",
    ]
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_portals_sashes_clock_and_roof_construction():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "SchoolFrontCivicEntry_1_LeftTimberDoor",
        "SchoolEcoleCommunaleRelief",
        "SchoolPodiumFrontClassroom_00_PhysicalLowEPane",
        "SchoolFloorRearClassroom_05_PhysicalLowEPane",
        "SchoolGroundRearStairFanlight_PhysicalLowEPane",
        "SchoolRearServiceDoor_0_ZincCanopy",
        "SchoolFrontClock_CreamClockFace",
        "SchoolClockPavilionSlateCap",
        "SchoolFrontZincDormer_0_PhysicalGlass",
        "SchoolLeftChimneys_BrickStack_0",
    } <= node_names
    assert sum(
        bool(name and "PhysicalLowEPane" in name) for name in node_names
    ) >= 36
    assert sum(
        bool(name and "FrontCivicEntry" in name and "TimberDoor" in name)
        for name in node_names
    ) == 6
    assert sum(bool(name and "ZincDormer" in name) for name in node_names) >= 20
    assert sum(bool(name and "BrickStack" in name) for name in node_names) == 4
    assert sum(bool(name and "ClockTick" in name) for name in node_names) == 24

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "heritage_sash_occupied"
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


def test_custom_school_skin_and_reference_provenance_are_complete():
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
    assert len(provenance["research"]) >= 5
    outputs = {item["file"]: item for item in provenance["assets"]}
    assert {
        "archetype-goalpost.png",
        "elevation-source-v1.png",
        "aerial-source-v1.png",
        "rear-elevation-source-v1.png",
        "masonry-material-source-v1.png",
        "occupied-depth-source-v1.png",
        "classroom-interior-depth-source-v1.png",
        "clock-cornice-detail-source-v1.png",
    } == set(outputs)
    assert all(item["prompt"] for item in outputs.values())
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
        assert signature["glassProfile"] == "heritage_sash_occupied"
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
        "/archetypes/buildings/ecole-republicaine-third-republic/hero.png"
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
        / "ecole-republicaine-third-republic"
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
