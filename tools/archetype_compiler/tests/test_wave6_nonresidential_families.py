"""Regression contracts for the three Wave 6 non-residential families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILY_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-29-nonresidential-glazing-enclosure-v100"
FAMILIES = {
    "deconstructivist-museum": {
        "archetype": "monumental_museum_axis",
        "variant": "museum_contemporary_deconstructivist",
        "glass": "museum_atrium_low_iron",
        "identity_objects": {
            "MUSEUM_MainLeftGalleryMass",
            "MUSEUM_Atrium_Pane_0_0",
            "MUSEUM_EntryStructuralWedge",
            "MUSEUM_MainParapetTooth_0",
        },
    },
    "terracotta-fin-office": {
        "archetype": "modern_glass_office_institutional",
        "variant": "glass_office_terracotta_fins",
        "glass": "terracotta_office_low_e",
        "identity_objects": {
            "OFFICE_Lobby_Pane_0_0",
            "OFFICE_TerracottaFin_0_0",
            "OFFICE_LowerTerraceSlab",
            "OFFICE_RoofTreeCrownA_-17.6",
        },
    },
    "brutalist-civic-block": {
        "archetype": "modernist_civic_block",
        "variant": "modernist_civic_concrete_brutalist",
        "glass": "civic_recessed_smoked",
        "identity_objects": {
            "CIVIC_MonumentalPilotis_0",
            "CIVIC_LeftGallery_RecessedSlit_Pane_0_0",
            "CIVIC_BroadRoofPlane",
            "CIVIC_RecessedLobby_Pane_0_0",
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


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_wave6_manifest_preserves_variant_identity_and_flexible_landmark_fit(
    family: str,
):
    expected = FAMILIES[family]
    root = FAMILY_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")

    assert manifest["archetype_id"] == expected["archetype"]
    assert manifest["variant_id"] == expected["variant"]
    assert manifest["generation_archetype_id"] == expected["variant"]
    assert set(manifest["archetype_aliases"]) == {
        expected["archetype"],
        expected["variant"],
    }
    assert manifest["glass_profile"] == expected["glass"]
    assert manifest["assembled"]["stack"][0]["role"] == "assembled"
    assert manifest["massing_graph"]["type"] == "fixed_landmark"

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert compatibility["minimumPreferredProfiles"] == 1
    assert compatibility["profileRationale"]
    band = compatibility["fixedLandmarkScaleBand"]
    assert band["scaleMin"] <= 0.82
    assert band["scaleMax"] >= 1.18
    assert band["maxAxisRatio"] >= 1.16

    floor_variants = {
        module["variant_key"]
        for module in manifest["modules"]
        if module["role"] == "floor"
    }
    assert floor_variants == {"typical_a", "typical_b", "typical_c"}
    assert {module["role"] for module in manifest["modules"]} == {
        "podium",
        "floor",
        "crown",
        "roof",
    }
    assert all((root / module["filename"]).is_file() for module in manifest["modules"])


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_wave6_delivers_custom_pbr_multiview_evidence_and_geometry(family: str):
    expected = FAMILIES[family]
    root = FAMILY_ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")

    assert skin["source_model"] == "gpt-image-2"
    assert skin["reference_registration"]["generic_tiling_allowed"] is False
    assert {"front", "left", "right", "rear", "roof"} <= set(
        skin["reference_registration"]["registered_elevations"]
    )
    assert {
        "facade",
        "podium",
        "floor_a",
        "floor_b",
        "floor_c",
        "crown",
        "shell",
        "side",
        "roof",
        "trim",
        "metal",
        "interior",
        "planting",
    } <= set(skin["zones"])
    required_channels = {
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
            assert set(zone[lod]) == required_channels
            assert all((root / path).is_file() for path in zone[lod].values())

    provenance = load_json(root / "textures" / "source" / "reference-generation.json")
    assert provenance["mode"] == "generate from hard catalogue reference"
    assert len(provenance["outputs"]) == 4
    for name in (
        "archetype-goalpost.png",
        "angle-reference-60.png",
        "angle-reference-90.png",
        "elevation-source.png",
        "material-source.png",
    ):
        assert (root / "textures" / "source" / name).is_file()

    payload = glb_json(root / f"{family}_assembled.glb")
    names = {node.get("name") for node in payload.get("nodes", [])}
    assert expected["identity_objects"] <= names
    material_extras = [
        value.get("extras", {})
        for value in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == expected["glass"]
        for extras in material_extras
    )

    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "context",
    ):
        assert (root / f"{family}_{role}.png").is_file()
    assert (root / "elevation.jpg").is_file()


def test_wave6_signatures_bind_parent_and_variant_to_render_locked_elevations():
    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    expected = {
        "monumental_museum_axis": (
            "museum_atrium_low_iron",
            "/families/deconstructivist-museum/elevation.jpg",
        ),
        "museum_contemporary_deconstructivist": (
            "museum_atrium_low_iron",
            "/families/deconstructivist-museum/elevation.jpg",
        ),
        "modern_glass_office_institutional": (
            "terracotta_office_low_e",
            "/families/terracotta-fin-office/elevation.jpg",
        ),
        "glass_office_terracotta_fins": (
            "terracotta_office_low_e",
            "/families/terracotta-fin-office/elevation.jpg",
        ),
        "modernist_civic_block": (
            "civic_recessed_smoked",
            "/families/brutalist-civic-block/elevation.jpg",
        ),
        "modernist_civic_concrete_brutalist": (
            "civic_recessed_smoked",
            "/families/brutalist-civic-block/elevation.jpg",
        ),
    }
    for archetype_id, (glass, elevation) in expected.items():
        entry = signatures[archetype_id]
        assert entry["archetypeId"] == archetype_id
        assert entry["glassProfile"] == glass
        assert entry["elevationUrl"] == elevation
        assert entry["identity"]
        assert entry["materialZones"]


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_wave6_assessment_uses_current_quality_memory(family: str):
    assessment = load_json(FAMILY_ROOT / family / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
