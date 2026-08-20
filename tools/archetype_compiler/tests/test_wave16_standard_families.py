"""Regression contracts for the ten commonplace Wave 16 families."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import pytest
from PIL import Image

from quality_memory import load_quality_memory
from wave16_standard_specs import FAMILIES


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = load_quality_memory()["memory_version"]
REQUIRED_CHANNELS = {
    "albedo", "normal", "roughness", "ao", "depth", "emissive",
    "glass_mask", "opaque_mask",
}
IDENTITY_NODES = {
    "craftsman-brick-bungalow": {"BUNGALOW_MainGableRoof", "BUNGALOW_FrontPorch"},
    "red-brick-edwardian-foursquare": {"FOURSQUARE_HippedRoof", "FOURSQUARE_FullWidthPorch_Deck"},
    "plateau-stone-montreal-duplex": {"DUPLEX_ExteriorStair_Step_0", "DUPLEX_CantedBay_-1"},
    "victorian-brick-rowhouse-terrace": {"ROWHOUSE_TerraceStreetwall", "ROWHOUSE_Dwelling_0"},
    "new-law-brick-walkup": {"TENEMENT_CastIronFireEscape_Platform_1", "TENEMENT_GroundStorefront_0_Glass"},
    "midcentury-balcony-apartment-slab": {"TOWER_ContinuousBalconySlab_0", "TOWER_BreezeBlockScreen_0_0_0"},
    "classic-neighbourhood-strip-mall": {"STRIP_ContinuousTenantCanopy", "STRIP_AnchorTower"},
    "classic-corner-bodega-mixed-use": {"BODEGA_WraparoundStorefront_Front_Glass", "BODEGA_CornerAwningFront"},
    "tilt-up-light-industrial-workshop": {"INDUSTRIAL_TiltUpPanelField", "INDUSTRIAL_LoadingDoor_0_Panel_0"},
    "provincial-brick-neighbourhood-school": {"SCHOOL_ClockTower", "SCHOOL_CourtyardBridge"},
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_wave16_roster_is_balanced_and_exact_variant_unique():
    assert len(FAMILIES) == 10
    assert len({spec["archetype_id"] for spec in FAMILIES.values()}) == 10
    assert len({spec["variant_id"] for spec in FAMILIES.values()}) == 10
    development = [spec["development_type"] for spec in FAMILIES.values()]
    assert development.count("residential_single_family") == 2
    assert sum(item.startswith("residential") for item in development) == 6
    assert set(development) >= {
        "retail_commercial", "mixed_use_neighbourhood", "industrial_light",
        "institutional_education",
    }
    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )["archetypes"]
    by_id = {item["id"]: item for item in catalogue}
    for spec in FAMILIES.values():
        parent = by_id[spec["archetype_id"]]
        variant = next(
            item for item in parent["variants"]
            if item["id"] == spec["variant_id"]
        )
        assert variant["thumbnailUrl"] == f"/{spec['source_path']}"


@pytest.mark.parametrize("family", FAMILIES)
def test_wave16_manifest_modules_and_grounding_contract(family: str):
    spec = FAMILIES[family]
    root = ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    assert manifest["manifest_schema"] == 3
    assert manifest["archetype_id"] == spec["archetype_id"]
    assert manifest["variant_id"] == spec["variant_id"]
    assert manifest["architectural_identity"] == spec["identity"]
    assert manifest["glass_profile"] == spec["glass_profile"]
    assert manifest["coordinate_contract"]["origin"] == "bottom centre"
    assert manifest["coordinate_contract"]["gltf_up"] == "+Y (export_yup)"
    assert manifest["source_provenance"]["catalogue_card_preserved"] is True
    assert len(manifest["modules"]) == 6
    assert {item["role"] for item in manifest["modules"]} == {
        "podium", "floor", "crown", "roof",
    }
    assert {
        item["variant_key"] for item in manifest["modules"]
        if item["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all((root / item["filename"]).is_file() for item in manifest["modules"])
    assembled = manifest["assembled"]
    assert assembled["assembly_class"] == "fixed_landmark"
    assert assembled["fixed_semantic"] is True
    assert assembled["repeatable_z"] is False
    assert assembled["triangle_count"] >= 1000
    assert assembled["material_count"] >= 6
    assert (root / assembled["filename"]).stat().st_size <= 9 * 1024 * 1024
    validation = load_json(root / "validation_report.json")
    assert validation["status"] == "pass"
    for item in validation["modules"]:
        assert abs(item["bottom_y"]) <= 0.002


@pytest.mark.parametrize("family", FAMILIES)
def test_wave16_skin_is_catalogue_registered_clean_and_compact(family: str):
    spec = FAMILIES[family]
    root = ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")
    assert skin["source_model"] == "pre-existing-catalogue-reference"
    assert skin["source_provider"] == "CityPrompt registered catalogue asset"
    registration = skin["reference_registration"]
    assert registration["source_archetype_id"] == spec["archetype_id"]
    assert registration["source_variant_id"] == spec["variant_id"]
    assert registration["generic_tiling_allowed"] is False
    assert len(skin["zones"]) == 13
    for zone in skin["zones"].values():
        for lod, maximum in (("near", 1024), ("far", 512)):
            assert set(zone[lod]) == REQUIRED_CHANNELS
            for relative in zone[lod].values():
                path = root / relative
                assert path.is_file()
                with Image.open(path) as image:
                    assert max(image.size) <= maximum
    source = REPO / "frontend" / "public" / spec["source_path"]
    copied = root / "textures" / "source" / "archetype-goalpost.png"
    assert digest(source) == digest(copied)
    provenance = load_json(root / "textures" / "source" / "reference-generation.json")
    assert provenance["provider"] == "CityPrompt registered catalogue asset"
    assert provenance["variant_id"] == spec["variant_id"]


@pytest.mark.parametrize("family", FAMILIES)
def test_wave16_glb_keeps_variant_identity_and_physical_layers(family: str):
    spec = FAMILIES[family]
    payload = glb_json(ROOT / family / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert IDENTITY_NODES[family] <= names
    extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == spec["glass_profile"]
        and item.get("reference_locked") is True
        for item in extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in extras)
    assert any(item.get("wave16_catalogue_registered_material") is True for item in extras)


@pytest.mark.parametrize("family", FAMILIES)
def test_wave16_review_assets_and_quality_memory_bind(family: str):
    root = ROOT / family
    spec = FAMILIES[family]
    for role in (
        "preview", "street", "context", "front_elevation",
        "front_corner_oblique", "rear_corner_oblique", "aerial", "facade_close",
    ):
        assert (root / f"{family}_{role}.png").is_file()
    assert (root / f"{family}_comparison.jpg").is_file()
    signature = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"][spec["variant_id"]]
    assert signature["archetypeId"] == spec["variant_id"]
    assert signature["identity"] == spec["identity"]
    assert signature["glassProfile"] == spec["glass_profile"]
    assert signature["elevationUrl"] == f"/families/{family}/elevation.jpg"
    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    evidence = load_json(root / f"{family}_manifest.json")["quality_standard_evidence"]
    assert evidence["human_visual_approval"] is False
    assert evidence["photoreal_skin_approved"] is False
    assert assessment["status"] == "review"
    assert assessment["high_quality_ready"] is False
