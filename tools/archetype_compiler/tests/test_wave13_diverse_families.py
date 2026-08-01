"""Regression contracts for the five reference-locked Wave 13 families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-08-01-wave13-optical-pv-refinement-v112"
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
    "art-deco-cream-terracotta-tower": {
        "parent": "art_deco_setback_tower",
        "variant": "art_deco_cream_terracotta",
        "aliases": {
            "art_deco_setback_tower",
            "art_deco_cream_terracotta",
            "cream_terracotta_art_deco_tower",
            "gilded_setback_tower",
        },
        "native": (31.62, 31.56, 72.85, 15),
        "source_native": (31.0, 29.0, 77.0),
        "floor_range": (10, 28),
        "profiles": ["rectangle"],
        "glass": "neutral_smoky_bronze_framed_occupied",
        "zone_count": 13,
        "hero_folder": "art_deco_setback_tower",
        "identity_nodes": {
            "DECO_LanternSmokyGlass",
            "DECO_FacetedGoldLanternCap",
            "DECO_FirstSetbackTerracottaBelt",
        },
    },
    "restored-kyoto-machiya": {
        "parent": "japanese_machiya_mixed_use",
        "variant": "machiya_traditional_restored",
        "aliases": {
            "japanese_machiya_mixed_use",
            "machiya_traditional_restored",
            "restored_kyoto_machiya",
            "traditional_koshi_lattice_shop_house",
        },
        "native": (19.77, 16.77, 11.57, 2),
        "source_native": (19.4, 15.4, 11.4),
        "floor_range": (2, 4),
        "profiles": ["rectangle", "l_shape"],
        "glass": "neutral_smoky_lattice_screened_occupied",
        "zone_count": 14,
        "hero_folder": "japanese_machiya_mixed_use",
        "identity_nodes": {
            "MACHIYA_KawaraRidgeCap",
            "MACHIYA_FrontWhiteClayGable",
            "MACHIYA_LowerStreetKawaraRoof",
            "MACHIYA_PlainIndigoNoren_0",
        },
    },
    "mid-century-glass-steel-pavilion": {
        "parent": "mid_century_modern_pavilion_block",
        "variant": "mid_century_pavilion_glass_steel",
        "aliases": {
            "mid_century_modern_pavilion_block",
            "mid_century_pavilion_glass_steel",
            "glass_steel_gallery_pavilion",
            "floating_roof_modern_pavilion",
        },
        "native": (29.28, 22.2, 11.63, 3),
        "source_native": (29.0, 22.0, 12.6),
        "floor_range": (1, 5),
        "profiles": ["rectangle", "l_shape"],
        "glass": "neutral_low_iron_gallery_occupied",
        "zone_count": 16,
        "refinement_source": "optical-construction-source-v2.png",
        "hero_folder": "mid_century_modern_pavilion_block",
        "identity_nodes": {
            "PAVILION_TravertineServiceCore",
            "PAVILION_RibbedSoffit",
            "PAVILION_KnifeEdgeRoof",
            "PAVILION_CeilingLightTrim_0_0_0",
        },
    },
    "timber-glass-transit-station-block": {
        "parent": "transit_oriented_station_block",
        "variant": "transit_station_modern_glass",
        "aliases": {
            "transit_oriented_station_block",
            "transit_station_modern_glass",
            "timber_glass_transit_station_block",
            "green_roof_station_concourse",
        },
        "native": (61.0, 40.54, 26.516, 6),
        "source_native": (62.0, 38.0, 29.5),
        "floor_range": (4, 10),
        "profiles": ["rectangle", "l_shape"],
        "glass": "high_transmission_transit_concourse_occupied",
        "zone_count": 14,
        "hero_folder": "transit_oriented_station_block",
        "identity_nodes": {
            "TRANSIT_EntranceCanopyGlass",
            "TRANSIT_EscalatorA_Step_0",
            "TRANSIT_ExtensiveGreenRoof",
            "TRANSIT_PVCanopy_0_0",
        },
    },
    "passive-house-timber-block": {
        "parent": "eco_urban_bioclimatic_block",
        "variant": "eco_bioclimatic_passive",
        "aliases": {
            "eco_urban_bioclimatic_block",
            "eco_bioclimatic_passive",
            "passive_house_timber_block",
            "larch_pv_sedum_urban_block",
        },
        "native": (37.2, 22.06, 17.8, 4),
        "source_native": (37.2, 21.0, 18.2),
        "floor_range": (3, 8),
        "profiles": ["rectangle", "l_shape"],
        "glass": "neutral_triple_glazed_deep_reveal_occupied",
        "zone_count": 15,
        "refinement_source": "optical-pv-construction-source-v2.png",
        "hero_folder": "eco_urban_bioclimatic_block",
        "identity_nodes": {
            "PASSIVE_CentralEntryRecess",
            "PASSIVE_RoofPVModule_0_0_CellLaminate",
            "PASSIVE_PVContinuousMountingRail_0",
            "PASSIVE_PublicSedumRoofBand",
            "PASSIVE_SedumRooflight_0",
        },
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
def test_wave13_manifest_binds_landmark_aliases_and_flexible_stack(family: str):
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
    assert compatibility["profileRationale"]
    assert compatibility["fixedLandmarkScaleBand"]["scaleMin"] <= 0.76
    assert compatibility["fixedLandmarkScaleBand"]["scaleMax"] >= 1.24

    modules = manifest["modules"]
    assert len(modules) == 6
    assert {item["role"] for item in modules} == {"podium", "floor", "crown", "roof"}
    assert {
        item["variant_key"] for item in modules if item["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
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
    assert assembled["triangle_count"] >= 12000
    assert (root / assembled["filename"]).is_file()


@pytest.mark.parametrize("family", SPECS)
def test_wave13_custom_skin_provenance_and_pbr_are_complete(family: str):
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
        "front", "left", "right", "rear", "roof"
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
    assert provenance["design_lock"]["native_envelope_dimensions_m"] == list(spec["source_native"])
    assert all(item.get("source_id") for item in provenance["sources"])
    assert all((source_root / item["file"]).is_file() for item in provenance["sources"])
    generated = {
        item["file"]: item
        for item in provenance["sources"]
        if item["file"] in {"archetype-goalpost.png", "material-construction-source-v1.png"}
    }
    assert set(generated) == {"archetype-goalpost.png", "material-construction-source-v1.png"}
    assert all(item.get("prompt") for item in generated.values())
    if refinement_source := spec.get("refinement_source"):
        refined = next(
            item for item in provenance["sources"]
            if item["file"] == refinement_source
        )
        assert provenance["status"] == "source-pack-refined"
        assert refined["role"] == "reviewed_optical_and_construction_refinement_plate"
        assert refined.get("prompt")
        assert (source_root / refinement_source).is_file()


@pytest.mark.parametrize("family", SPECS)
def test_wave13_glb_contains_family_identity_and_physical_optical_layers(family: str):
    spec = SPECS[family]
    root = FAMILIES_ROOT / family
    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert spec["identity_nodes"] <= names
    material_extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == spec["glass"]
        and item.get("reference_locked") is True
        for item in material_extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in material_extras)
    if family == "mid-century-glass-steel-pavilion":
        assert "PAVILION_FrontSlabFascia_0" in names
        assert not any(name.endswith("_OccupiedDepth") for name in names)
        assert sum(name.startswith("PAVILION_GalleryBench_") for name in names) >= 9
    if family == "passive-house-timber-block":
        assert sum(
            name.startswith("PASSIVE_RoofPVModule_")
            and name.endswith("_CellLaminate")
            for name in names
        ) == 90
        assert sum(name.startswith("PASSIVE_PVContinuousMountingRail_") for name in names) == 3
        assert any(item.get("photovoltaic_module") is True for item in material_extras)
        assert any(item.get("cell_topology") == "6_columns_x_10_rows" for item in material_extras)


@pytest.mark.parametrize("family", SPECS)
def test_wave13_render_signature_catalogue_and_assessment_bindings(family: str):
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
        "front_elevation",
        "identity_close",
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
        REPO / "frontend" / "public" / "archetypes" / "buildings"
        / spec["hero_folder"] / "hero.png"
    ).is_file()

    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
