"""Regression contracts for the approved four-family Wave 4 batch."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILY_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-29-reference-specific-window-materiality-v99"
FAMILIES = {
    "brownstone-rowhouse-frontage": {
        "archetype": "brownstone_rowhouse_frontage",
        "variant": "brownstone_rowhouse_red_sandstone",
        "floors": (2, 3, 4),
        "bay": 1.60,
        "catalogue_dir": "brownstone_rowhouse_frontage",
        "identity_tag": "integrated_sandstone_stoop",
        "glass_profile": "heritage_sash_occupied",
        "glass_material": "glassheritagesash",
    },
    "industrial-brick-mixed-use": {
        "archetype": "industrial_brick_mixed_use",
        "variant": "industrial_brick_original_mill",
        "floors": (3, 4, 6),
        "bay": 5.00,
        "catalogue_dir": "industrial_brick_mixed_use",
        "identity_tag": "segmental_arch_crittall_windows",
        "glass_profile": "industrial_crittall_occupied",
        "glass_material": "glasscrittall",
    },
    "contemporary-midrise-residential": {
        "archetype": "contemporary_midrise_residential",
        "variant": "contemporary_midrise_variant_brick_bronze",
        "floors": (4, 6, 8),
        "bay": 4.15,
        "catalogue_dir": "contemporary_mid_rise_residential",
        "identity_tag": "subtractive_arched_entrance",
        "glass_profile": "bronze_recessed_occupied",
        "glass_material": "glassbronzelowe",
    },
    "scandinavian-urban-residential": {
        "archetype": "scandinavian_urban_residential",
        "variant": "scandi_urban_white_plaster",
        "floors": (4, 6, 7),
        "bay": 4.50,
        "catalogue_dir": "scandinavian_urban_residential",
        "identity_tag": "through_courtyard_passage",
        "glass_profile": "nordic_clear_occupied",
        "glass_material": "glassnordicclear",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_glb_json(path: Path) -> dict:
    payload = path.read_bytes()
    assert payload[:4] == b"glTF"
    json_chunk_length = struct.unpack_from("<I", payload, 12)[0]
    json_chunk = payload[20 : 20 + json_chunk_length]
    return json.loads(json_chunk.decode("utf-8").rstrip(" \x00"))


@pytest.mark.parametrize(("family", "expected"), FAMILIES.items())
def test_wave4_batch_manifest_is_reference_locked_and_resizable(
    family: str,
    expected: dict,
):
    root = FAMILY_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")

    assert manifest["archetype_id"] == expected["archetype"]
    assert manifest["variant_id"] == expected["variant"]
    assert {expected["archetype"], expected["variant"]} <= set(
        manifest["archetype_aliases"]
    )
    assert (
        manifest["min_floors"],
        manifest["native_floors"],
        manifest["max_floors"],
    ) == expected["floors"]
    assert manifest["massing_graph"]["type"] == "modular_streetwall"
    assert manifest["massing_graph"]["fixed"] == [
        "podium/entrance",
        "corner returns",
        "crown",
        "roof",
    ]
    assert expected["identity_tag"] in manifest["generation_tags"]

    modules = manifest["modules"]
    assert {module["role"] for module in modules} == {
        "podium",
        "floor",
        "setback",
        "crown",
        "roof",
    }
    assert {
        module["variant_key"]
        for module in modules
        if module["role"] == "floor"
    } == {"typical_a", "typical_b", "typical_c"}
    assert all((root / module["filename"]).is_file() for module in modules)
    assert (root / manifest["assembled"]["filename"]).is_file()

    compatibility = manifest["footprint_compatibility"]
    assert set(compatibility["preferredProfiles"]) == {
        "rectangle",
        "l_shape",
        "u_shape",
    }
    assert compatibility["preferredBayMultiple_m"] == expected["bay"]
    assert all(
        compatibility["profiles"][profile]["recommendedWidth_m"]
        for profile in compatibility["preferredProfiles"]
    )


@pytest.mark.parametrize(("family", "expected"), FAMILIES.items())
def test_wave4_batch_has_custom_skin_all_elevations_and_green_assessment(
    family: str,
    expected: dict,
):
    root = FAMILY_ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")
    registration = skin["reference_registration"]
    assert registration["mode"] == "archetype_specific"
    assert registration["source_archetype_id"] == expected["archetype"]
    assert registration["source_variant_id"] == expected["variant"]
    assert registration["generic_tiling_allowed"] is False
    assert registration["wall_band_aspect"] > 0
    assert set(registration["registered_elevations"]) == {
        "front",
        "left",
        "right",
        "rear",
        "roof",
    }
    assert {
        "facade",
        "podium",
        "floor_a",
        "floor_b",
        "floor_c",
        "crown",
        "side",
        "roof",
        "trim",
        "metal",
        "timber",
    } == set(skin["zones"])

    required = {
        "albedo",
        "normal",
        "roughness",
        "ao",
        "depth",
        "emissive",
        "glass_mask",
        "opaque_mask",
    }
    for zone in skin["zones"].values():
        for lod in ("near", "far"):
            assert set(zone[lod]) == required
            assert all((root / path).is_file() for path in zone[lod].values())

    assessment = load_json(root / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True


@pytest.mark.parametrize(("family", "expected"), FAMILIES.items())
def test_wave4_batch_catalogue_and_signature_assets_are_wired(
    family: str,
    expected: dict,
):
    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    cards = [
        item
        for item in catalogue["archetypes"]
        if item["id"] == expected["archetype"]
    ]
    assert len(cards) == 1
    assert (
        REPO
        / "frontend"
        / "public"
        / cards[0]["thumbnailUrl"].removeprefix("/")
    ).is_file()
    catalogue_dir = (
        REPO
        / "frontend"
        / "public"
        / "archetypes"
        / "buildings"
        / expected["catalogue_dir"]
    )
    assert (catalogue_dir / "hero.png").is_file()

    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    for identity in (expected["archetype"], expected["variant"]):
        signature = signatures[identity]
        assert signature["archetypeId"] == identity
        assert signature["elevationUrl"] == f"/families/{family}/elevation.jpg"
        assert signature["identity"]
        assert signature["materialZones"]
        assert signature["glassProfile"]


@pytest.mark.parametrize(("family", "expected"), FAMILIES.items())
def test_wave4_window_system_uses_registered_physical_glazing_profile(
    family: str,
    expected: dict,
):
    from glass_profiles import glass_profile

    manifest = load_json(FAMILY_ROOT / family / f"{family}_manifest.json")
    assert manifest["glass_profile"] == expected["glass_profile"]

    profile = glass_profile(manifest["glass_profile"])
    assert profile["label"]
    assert 0.15 <= profile["transmission"] <= 0.22
    assert profile["roughness"] <= 0.10
    assert profile["glass_emission_strength"] <= 0.01
    assert profile["interior_depth_m"] > profile["pane_recess_m"]


@pytest.mark.parametrize(("family", "expected"), FAMILIES.items())
def test_wave4_window_system_exports_physical_glazing_metadata(
    family: str,
    expected: dict,
):
    glb = load_glb_json(FAMILY_ROOT / family / f"{family}_assembled.glb")
    materials = [
        material
        for material in glb["materials"]
        if expected["glass_material"] in material.get("name", "").lower()
    ]

    assert len(materials) == 2
    assert {
        "KHR_materials_clearcoat",
        "KHR_materials_specular",
        "KHR_materials_transmission",
    } <= set(glb["extensionsUsed"])

    for material in materials:
        assert material["extras"]["glazing_profile"] == expected["glass_profile"]
        assert material["extras"]["glazing_lod"] == "always"
        assert material["extras"]["alpha_strategy"] == (
            "opaque_physical_transmission"
        )
        assert material["extras"]["interior_depth_m"] > (
            material["extras"]["pane_recess_m"]
        )
        assert material["extensions"]["KHR_materials_clearcoat"][
            "clearcoatFactor"
        ] >= 0.40
        assert 0.10 <= material["extensions"]["KHR_materials_transmission"][
            "transmissionFactor"
        ] <= 0.22
        assert material["pbrMetallicRoughness"]["metallicFactor"] == 0
