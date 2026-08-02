"""Regression contracts for the ten reference-locked Wave 15 families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from wave15_mixed_specs import FAMILIES


REPO = Path(__file__).resolve().parents[3]
FAMILIES_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-08-01-wave15-program-topology-v114"
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
IDENTITY_NODES = {
    "copenhill-ski-slope-energy-plant": {
        "WTE_ContinuousSkiSlope",
        "WTE_FacetedStack",
    },
    "parametric-wave-natatorium": {
        "NAT_ContinuousWaveShell",
        "NAT_MainCableMast_Left",
    },
    "second-empire-clocktower-city-hall": {
        "CITY_ClockTower",
        "CITY_CopperDome",
    },
    "glass-greenhouse-vertical-farm": {
        "VF_GreenhouseCrown",
        "VF_ExteriorBrace_Front_0_0",
    },
    "steel-rib-intermodal-hub": {
        "HUB_PrimaryArch_Left_0",
        "HUB_ContinuousGlazedRoof",
    },
    "monumental-silo-cluster": {
        "SILO_BankA_0",
        "SILO_ConveyorHeadhouse",
    },
    "titanium-fold-art-museum": {
        "MUSEUM_RolledShell_Left",
        "MUSEUM_GalleryBridge",
    },
    "historic-iron-glass-market": {
        "MARKET_CentralBarrelGlass",
        "MARKET_FrontArch_Centre",
    },
    "bronze-curve-concert-hall": {
        "CONCERT_LeftBronzeShell",
        "CONCERT_CentralAuditorium",
    },
    "deconstructivist-concrete-fire-station": {
        "FIRE_LeaningHoseTower",
        "FIRE_ApparatusDoor_1",
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


def test_wave15_roster_expands_parent_coverage_without_losing_variant_depth():
    cohorts = [spec["cohort"] for spec in FAMILIES.values()]
    assert len(FAMILIES) == 10
    assert cohorts.count("uncovered_parent") == 7
    assert cohorts.count("sibling_variant") == 3
    assert len({spec["archetype_id"] for spec in FAMILIES.values()}) == 10
    assert len({spec["variant_id"] for spec in FAMILIES.values()}) == 10


@pytest.mark.parametrize("family", FAMILIES)
def test_wave15_manifest_is_reference_locked_and_size_flexible(family: str):
    spec = FAMILIES[family]
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")

    assert manifest["manifest_schema"] == 3
    assert manifest["grammar_schema_version"] == 3
    assert manifest["archetype_id"] == spec["archetype_id"]
    assert manifest["variant_id"] == spec["variant_id"]
    assert manifest["generation_archetype_id"] == spec["variant_id"]
    assert manifest["archetype_aliases"] == spec["aliases"]
    assert spec["variant_id"] in manifest["reuse_keys"]
    assert manifest["glass_profile"] == spec["glass_profile"]
    assert manifest["architectural_identity"] == spec["identity"]
    assert manifest["material_zones"] == spec["material_zones"]
    assert manifest["native_floors"] == spec["native_floors"]
    assert (manifest["min_floors"], manifest["max_floors"]) == (
        spec["min_floors"],
        spec["max_floors"],
    )
    assert manifest["coordinate_contract"]["origin"] == "bottom centre"
    assert manifest["coordinate_contract"]["gltf_up"] == "+Y (export_yup)"
    assert (
        manifest["coordinate_contract"]["front_facade"]
        == "-Y in Blender, +Z in glTF"
    )

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["scaleMin"] == 0.62
    assert compatibility["scaleMax"] == 1.4
    assert compatibility["maxAxisRatio"] == 1.3
    assert set(compatibility["profiles"]) == set(
        compatibility["preferredProfiles"]
    )
    assert compatibility["minimumPreferredProfiles"] == len(
        compatibility["preferredProfiles"]
    )
    for profile in compatibility["profiles"].values():
        assert profile["scaleMin"] == 0.62
        assert profile["scaleMax"] == 1.4
        assert profile["preferredBayMultiple_m"] > 0

    modules = manifest["modules"]
    assert len(modules) == 6
    assert {item["role"] for item in modules} == {
        "podium", "floor", "crown", "roof"
    }
    assert {
        item["variant_key"] for item in modules if item["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all((root / item["filename"]).is_file() for item in modules)
    assert all(
        item["repeatable_z"]
        and item["assembly_class"] == "repeatable_middle"
        for item in modules
        if item["role"] == "floor"
    )

    assembled = manifest["assembled"]
    assert assembled["assembly_class"] == "fixed_landmark"
    assert assembled["fixed_semantic"] is True
    assert assembled["repeatable_z"] is False
    assert assembled["source_variant_id"] == spec["variant_id"]
    assert assembled["generation_archetype_id"] == spec["variant_id"]
    assert assembled["triangle_count"] >= 1000
    assert assembled["material_count"] >= 6
    assert (root / assembled["filename"]).is_file()


@pytest.mark.parametrize("family", FAMILIES)
def test_wave15_custom_skin_and_generation_provenance_are_complete(family: str):
    spec = FAMILIES[family]
    root = FAMILIES_ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")
    assert skin["source_model"] == "gpt-image-2"
    registration = skin["reference_registration"]
    assert registration["mode"] == "archetype_specific"
    assert registration["source_archetype_id"] == spec["archetype_id"]
    assert registration["source_variant_id"] == spec["variant_id"]
    assert registration["generic_tiling_allowed"] is False
    assert set(registration["registered_elevations"]) == {
        "front", "left", "right", "rear", "roof"
    }
    assert "occupied-depth underlay" in registration["uv_strategy"]
    assert len(skin["zones"]) == 13
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
    assert provenance["archetype_id"] == spec["archetype_id"]
    assert provenance["variant_id"] == spec["variant_id"]
    assert provenance["design_lock"]["native_envelope_dimensions_m"] == list(
        spec["native"]
    )
    assert (
        provenance["design_lock"]["variant_specific_contract"]
        == spec["design_lock"]
    )
    assert all(item.get("source_id") for item in provenance["sources"])
    assert all((source_root / item["file"]).is_file() for item in provenance["sources"])
    generated = {
        item["file"]: item
        for item in provenance["sources"]
        if item["file"]
        in {"archetype-goalpost.png", "material-construction-source-v1.png"}
    }
    assert set(generated) == {
        "archetype-goalpost.png", "material-construction-source-v1.png"
    }
    assert all(item.get("prompt") for item in generated.values())


@pytest.mark.parametrize("family", FAMILIES)
def test_wave15_glb_keeps_identity_and_layered_materials(family: str):
    spec = FAMILIES[family]
    root = FAMILIES_ROOT / family
    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert IDENTITY_NODES[family] <= names
    material_extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == spec["glass_profile"]
        and item.get("reference_locked") is True
        for item in material_extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in material_extras)
    assert any(
        item.get("wave15_reference_locked_material") is True
        for item in material_extras
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_wave15_review_assets_signature_catalogue_and_assessment_bind(family: str):
    spec = FAMILIES[family]
    root = FAMILIES_ROOT / family
    for role in (
        "preview",
        "street",
        "aerial",
        "context",
        "front_corner_oblique",
        "rear_corner_oblique",
        "facade_close",
        "front_elevation",
    ):
        assert (root / f"{family}_{role}.png").is_file()
    assert (root / f"{family}_comparison.jpg").is_file()
    assert (FAMILIES_ROOT / f"wave15-{family}-comparison.jpg").is_file()
    assert (root / "elevation.jpg").is_file()

    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    signature = signatures[spec["variant_id"]]
    assert signature["archetypeId"] == spec["variant_id"]
    assert signature["glassProfile"] == spec["glass_profile"]
    assert signature["elevationUrl"] == f"/families/{family}/elevation.jpg"
    assert signature["identity"] == spec["identity"]
    assert signature["materialZones"] == spec["material_zones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    ids = [item["id"] for item in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))
    entry = next(
        item for item in catalogue["archetypes"]
        if item["id"] == spec["archetype_id"]
    )
    variant_ids = [item["id"] for item in entry["variants"]]
    assert len(variant_ids) == len(set(variant_ids))
    variant = next(
        item for item in entry["variants"]
        if item["id"] == spec["variant_id"]
    )
    assert variant["label"]
    assert variant["thumbnailUrl"] == (
        f"/archetypes/buildings/{spec['catalogue_slug']}/"
        f"variant_{spec['catalogue_variant_index']}.png"
    )
    thumbnail = (
        REPO / "frontend" / "public" / "archetypes" / "buildings"
        / spec["catalogue_slug"]
        / f"variant_{spec['catalogue_variant_index']}.png"
    )
    assert thumbnail.is_file()

    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
