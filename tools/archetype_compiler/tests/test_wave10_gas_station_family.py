"""Regression contracts for the Wave 10 prairie modern fuel-bar family."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "prairie-modern-fuel-bar"
PARENT = "rural_gas_station"
VARIANT = "gas_modern_fuel_bar"
ALIASES = {
    PARENT,
    VARIANT,
    "modern_fuel_bar",
    "prairie_fuel_bar",
}
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
    "buff_brick",
    "charcoal_metal",
    "canopy_aluminum",
    "timber_soffit",
    "storefront_glass",
    "forecourt_concrete",
    "burnt_orange",
    "pump_equipment",
    "stainless",
    "black_trim",
    "roof_membrane",
    "prairie_planting",
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
    assert manifest["glass_profile"] == "low_iron_clear"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (35.0, 30.0, 1)
    assert (manifest["min_floors"], manifest["max_floors"]) == (1, 1)
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
        "scaleMin": 0.78,
        "scaleMax": 1.22,
        "maxAxisRatio": 1.2,
    }
    assert compatibility["preferredBayMultiple_m"] == 4.0

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
    assert all(module["width_m"] == 35.0 for module in modules)
    assert all(module["depth_m"] == 30.0 for module in modules)
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
    assert graph["type"] == "fixed_landmark"
    assert graph["silhouette"] == "low_store_and_broad_detached_flat_canopy"
    assert graph["canopy_structural_columns"] == 6
    assert graph["pump_islands"] == 3
    assert graph["double_sided_pump_dispensers"] == 3
    assert graph["roadside_price_pylons"] == 1
    assert graph["rooftop_hvac_units"] == 2
    assert graph["propane_cages"] == 1
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_canopy_pumps_store_depth_and_service_equipment():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name", "") for node in payload.get("nodes", [])}

    assert {
        "FUELBAR_StorefrontPane_0",
        "FUELBAR_StorefrontPane_6",
        "FUELBAR_AutomaticDoorPane_0",
        "FUELBAR_AutomaticDoorPane_1",
        "FUELBAR_StorefrontHead",
        "FUELBAR_TrenchDrain_0",
        "FUELBAR_TrenchDrain_1",
        "FUELBAR_PumpDisplay_0_0",
        "FUELBAR_PumpReader_1_0",
        "FUELBAR_PumpKey_2_1_8",
        "FUELBAR_PylonTopBlank",
        "FUELBAR_PropaneCageBase",
        "FUELBAR_HVACUnit_0",
        "FUELBAR_HVACUnit_1",
    } <= node_names
    assert sum(
        bool(re.fullmatch(r"FUELBAR_CanopyColumn_\d{2}", name))
        for name in node_names
    ) == 6
    assert sum(
        bool(re.fullmatch(r"FUELBAR_PumpIsland_\d", name))
        for name in node_names
    ) == 3
    assert sum(
        bool(re.fullmatch(r"FUELBAR_PumpDispenser_\d", name))
        for name in node_names
    ) == 3
    assert sum("FUELBAR_CoolerProduct_" in name for name in node_names) == 200
    assert sum("FUELBAR_Hose_" in name for name in node_names) == 12
    assert sum("FUELBAR_NozzleBody_" in name for name in node_names) == 12

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "low_iron_clear"
        and extras.get("source_variant_id") == VARIANT
        and extras.get("reference_locked") is True
        and extras.get("pane_recess_m") == 0.16
        and extras.get("interior_depth_m") == 6.4
        for extras in material_extras
    )
    assert any(
        extras.get("skin_zone") == "pump_equipment"
        and extras.get("reference_locked") is True
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
    assert len(provenance["research"]) >= 6
    outputs = {item["file"]: item for item in provenance["assets"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "aerial-roof-source-v1.png",
        "rear-service-source-v1.png",
        "material-construction-source-v1.png",
        "storefront-pump-detail-source-v1.png",
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
        "storefront_close",
        "facade_close",
        "entry_close",
        "pump_close",
        "canopy_close",
        "service_close",
        "roof_close",
        "pylon_close",
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
        assert signature["glassProfile"] == "low_iron_clear"
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
        "/archetypes/buildings/prairie-modern-fuel-bar/hero.png"
    )
    compatibility = entry["footprintCompatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert set(compatibility["profiles"]) == {"rectangle"}
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.78,
        "scaleMax": 1.22,
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
