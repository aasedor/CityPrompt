"""Regression contracts for the Wave 10 mass-timber hospital family."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "biophilic-healthcare-mass-timber"
PARENT = "biophilic_healthcare"
VARIANT = "healthcare_mass_timber"
REGIONAL_ALIAS = "regional_hospital_biophilic_wellness"
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
    "atrium",
    "honey_timber",
    "glulam",
    "charred_timber",
    "concrete",
    "living_wall",
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


def test_manifest_binds_aliases_and_flexible_clinical_stack():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == PARENT
    assert manifest["variant_id"] == VARIANT
    assert manifest["generation_archetype_id"] == VARIANT
    assert set(manifest["archetype_aliases"]) == {
        PARENT,
        VARIANT,
        REGIONAL_ALIAS,
    }
    assert manifest["glass_profile"] == "timber_station_neutral_low_e"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (71.2, 51.2, 4)
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
        "u_shape",
        "courtyard",
        "rectangle",
        "l_shape",
    ]
    assert compatibility["minimumPreferredProfiles"] == 3
    assert set(compatibility["profiles"]) == {
        "u_shape",
        "courtyard",
        "rectangle",
        "l_shape",
    }
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.78,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.24,
    }
    assert compatibility["preferredBayMultiple_m"] == 4.25

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
    assert all(module["width_m"] == 71.2 for module in modules)
    assert all(module["depth_m"] == 51.2 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "u_shape"
    graph = assembled["massing_graph"]
    assert graph["type"] == "u_shaped_mass_timber_biophilic_hospital"
    assert graph["patient_wings"] == 2
    assert graph["open_healing_courtyard"] is True
    assert graph["integrated_public_atrium"] is True
    assert graph["ambulance_bays"] == 2
    assert graph["occupied_patient_room_rows"] == 3
    assert graph["screened_mechanical_penthouses"] == 2
    assert graph["photovoltaic_canopies"] == 1
    assert [item["role"] for item in assembled["stack"]] == [
        "podium",
        "floor",
        "floor",
        "floor",
        "crown",
        "roof",
    ]
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_atrium_patient_rooms_service_and_roof():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "HospitalAtriumGround_ContinuousLowIronCurtainWall",
        "HospitalIntegratedGlulamEntryCanopy",
        "HospitalEntryGlulamPost_-9.8",
        "Hospital_typical_a_LeftWingFront_Bay_00_PhysicalClinicalLowEPane",
        "Hospital_typical_b_RightCourtyard_Bay_05_RegisteredCareRoomDepth",
        "HospitalAmbulanceDoor_0_PhysicalGlass",
        "HospitalAmbulanceDoor_1_PhysicalGlass",
        "HospitalAmbulance_Cab",
        "HospitalCourtyardRainGardenWater",
        "HospitalLeftWingMeadowRoof",
        "HospitalLeftMechanicalPenthouse_Front_Louver_00",
        "HospitalPVPanel_00_00",
        "HospitalPVPanel_03_09",
    } <= node_names
    assert sum(
        bool(name and "PhysicalClinicalLowEPane" in name) for name in node_names
    ) >= 110
    assert sum(
        bool(name and "RegisteredCareRoomDepth" in name) for name in node_names
    ) >= 110
    assert sum(bool(name and "IntegratedPlanter" in name) for name in node_names) >= 110
    assert sum(
        bool(name and "LivingWallBacking" in name) for name in node_names
    ) >= 16
    assert sum(bool(name and "HospitalPVPanel" in name) for name in node_names) == 40
    assert sum(
        bool(name and "MechanicalPenthouse" in name and "Louver" in name)
        for name in node_names
    ) >= 100

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "timber_station_neutral_low_e"
        and extras.get("source_variant_id") == VARIANT
        for extras in material_extras
    )
    assert any(
        extras.get("glazing_profile") == "low_iron_clear"
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
    assert len(provenance["research"]) >= 5
    outputs = {item["file"]: item for item in provenance["assets"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "aerial-roof-source-v1.png",
        "rear-service-source-v1.png",
        "material-construction-source-v1.png",
        "glazing-occupied-depth-source-v1.png",
    } == set(outputs)
    assert all(item.get("prompt") for item in outputs.values())
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
        "atrium_close",
        "patient_window_close",
        "courtyard",
        "ambulance_close",
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
    for archetype_id in (PARENT, VARIANT, REGIONAL_ALIAS):
        assert signature_text.count(f'"{archetype_id}":') == 1
    signatures = load_json(signatures_path)["families"]
    for archetype_id in (PARENT, VARIANT, REGIONAL_ALIAS):
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
        "/archetypes/buildings/biophilic-healthcare-mass-timber/hero.png"
    )
    compatibility = entry["footprintCompatibility"]
    assert compatibility["preferredProfiles"] == [
        "u_shape",
        "courtyard",
        "rectangle",
        "l_shape",
    ]
    assert set(compatibility["profiles"]) == {
        "u_shape",
        "courtyard",
        "rectangle",
        "l_shape",
    }
    selected = next(
        variant for variant in entry["variants"] if variant["id"] == VARIANT
    )
    assert selected["thumbnailUrl"] == entry["thumbnailUrl"]
    regional = next(
        item
        for item in catalogue["archetypes"]
        if item["id"] == "regional_hospital_medical_center"
    )
    regional_variant = next(
        variant
        for variant in regional["variants"]
        if variant["id"] == REGIONAL_ALIAS
    )
    assert regional_variant["thumbnailUrl"] == entry["thumbnailUrl"]
    assert (
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / "biophilic-healthcare-mass-timber"
        / "hero.png"
    ).is_file()


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
