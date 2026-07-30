"""Regression contracts for the three Wave 8 reference-locked families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILY_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-29-registered-source-construction-zones-v103"
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
FAMILIES = {
    "parametric-fluid-hub": {
        "parent": "parametric_future_hub",
        "variant": "parametric_fluid_organic",
        "glass": "fluid_hub_low_iron_curved",
        "floors": (4, 7, 5),
        "band": (0.86, 1.14, 1.12),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "shell",
            "side",
            "interior",
            "metal",
            "roof",
        },
        "nodes": {
            "FLUID_RegisteredDoubleCurvedFrontShell",
            "FLUID_WrappedSecondaryShell",
            "FLUID_ContinuousShellRoof",
            "FLUID_OrganicOpeningMullionSystem",
            "FLUID_OrganicOpeningTransomSystem",
        },
    },
    "timber-transit-station": {
        "parent": "transit_oriented_station_block",
        "variant": "transit_station_timber_sustainable",
        "glass": "timber_station_neutral_low_e",
        "floors": (4, 8, 5),
        "band": (0.84, 1.18, 1.15),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "timber",
            "louver",
            "canopy",
            "side",
            "interior",
            "glass",
            "green",
        },
        "nodes": {
            "STATION_PrimaryFrontPostSystem",
            "STATION_PhysicalLouverSystem",
            "STATION_ConcoursePane_0",
            "STATION_TreeColumnSystem",
            "STATION_TreeBranchSystem",
            "STATION_CanopyPrimaryBeamSystem",
            "STATION_TranslucentCanopyMembrane",
            "STATION_RoofGuardGlass_-1_0",
        },
    },
    "covered-souk-market": {
        "parent": "traditional_vernacular_market_street",
        "variant": "vernacular_market_souk_bazaar",
        "glass": "souk_recessed_amber_glass",
        "floors": (1, 3, 2),
        "band": (0.80, 1.25, 1.20),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "roof",
            "side",
            "interior",
            "stone",
            "dome",
            "timber",
            "bronze",
        },
        "nodes": {
            "SOUK_SevenDeepPointedArchSystem",
            "SOUK_VoussoirJointSystem",
            "SOUK_MashrabiyaFineLatticeSystem",
            "SOUK_RecessedShopGlazing_0",
            "SOUK_LanternBodySystem",
            "SOUK_SevenAlignedDomeSystem",
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
def test_manifest_binds_aliases_landmark_band_and_flexible_stack(family: str):
    expected = FAMILIES[family]
    root = FAMILY_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")

    assert manifest["archetype_id"] == expected["parent"]
    assert manifest["variant_id"] == expected["variant"]
    assert manifest["generation_archetype_id"] == expected["variant"]
    assert set(manifest["archetype_aliases"]) == {
        expected["parent"],
        expected["variant"],
    }
    assert manifest["glass_profile"] == expected["glass"]
    minimum, maximum, native = expected["floors"]
    assert (
        manifest["min_floors"],
        manifest["max_floors"],
        manifest["native_floors"],
    ) == (minimum, maximum, native)
    assert manifest["assembled"]["stack"][0]["role"] == "assembled"
    assert manifest["massing_graph"]["type"] == "fixed_landmark"

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert compatibility["minimumPreferredProfiles"] == 1
    assert compatibility["profileRationale"]
    scale_min, scale_max, max_axis_ratio = expected["band"]
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": scale_min,
        "scaleMax": scale_max,
        "maxAxisRatio": max_axis_ratio,
    }

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
    assert all(
        module["repeatable_z"] and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((root / module["filename"]).is_file() for module in modules)


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_fixed_glb_contains_family_geometry_glass_and_registered_depth(
    family: str,
):
    expected = FAMILIES[family]
    payload = glb_json(FAMILY_ROOT / family / f"{family}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert expected["nodes"] <= node_names
    if family == "parametric-fluid-hub":
        assert len(
            [name for name in node_names if name.startswith("FLUID_OrganicPane_")]
        ) == 6
        assert len(
            [
                name
                for name in node_names
                if name.startswith("FLUID_RenderLockedOccupiedDepth_")
            ]
        ) == 6
    if family == "covered-souk-market":
        assert len(
            [
                name
                for name in node_names
                if name.startswith("SOUK_RecessedShopGlazing_")
            ]
        ) == 7

    material_extras = [
        material.get("extras", {}) for material in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == expected["glass"]
        and extras.get("source_variant_id") == expected["variant"]
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


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_custom_skin_provenance_and_multiview_outputs_are_complete(family: str):
    expected = FAMILIES[family]
    root = FAMILY_ROOT / family
    skin = load_json(root / "textures" / "skin_manifest.json")

    assert skin["source_model"] == "gpt-image-2"
    registration = skin["reference_registration"]
    assert registration["source_archetype_id"] == expected["parent"]
    assert registration["source_variant_id"] == expected["variant"]
    assert registration["generic_tiling_allowed"] is False
    assert {"front", "left", "right", "rear", "roof"} <= set(
        registration["registered_elevations"]
    )
    assert "occupied-depth underlay" in registration["uv_strategy"]
    assert set(skin["zones"]) == expected["zones"]
    for zone in skin["zones"].values():
        for lod in ("near", "far"):
            assert set(zone[lod]) == REQUIRED_CHANNELS
            assert all((root / path).is_file() for path in zone[lod].values())

    provenance = load_json(
        root / "textures" / "source" / "reference-generation.json"
    )
    assert provenance["tool"] == "OpenAI built-in ImageGen"
    assert provenance["model"] == "gpt-image-2"
    assert len(provenance["outputs"]) == 2
    assert {item["file"] for item in provenance["outputs"]} == {
        "elevation-source.png",
        "occupied-depth-source.png",
    }

    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "identity_close",
        "context",
    ):
        assert (root / f"{family}_{role}.png").is_file()
    assert (root / f"{family}_comparison.jpg").is_file()
    assert (root / "elevation.jpg").is_file()


def test_signatures_and_existing_catalogue_cards_resolve_to_delivered_assets():
    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    catalogue_path = (
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    catalogue = load_json(catalogue_path)
    ids = [entry["id"] for entry in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))

    for family, expected in FAMILIES.items():
        for archetype_id in (expected["parent"], expected["variant"]):
            signature = signatures[archetype_id]
            assert signature["archetypeId"] == archetype_id
            assert signature["glassProfile"] == expected["glass"]
            assert signature["elevationUrl"] == f"/families/{family}/elevation.jpg"
            assert signature["identity"]
            assert signature["materialZones"]

        entry = next(
            item
            for item in catalogue["archetypes"]
            if item["id"] == expected["parent"]
        )
        assert any(
            variant["id"] == expected["variant"]
            for variant in entry["variants"]
        )
        paths = [
            entry["thumbnailUrl"],
            *(variant["thumbnailUrl"] for variant in entry["variants"]),
        ]
        assert len(paths) == len(set(paths))
        assert all(
            (REPO / "frontend" / "public" / path.removeprefix("/")).is_file()
            for path in paths
        )


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_assessment_uses_current_quality_memory(family: str):
    assessment = load_json(FAMILY_ROOT / family / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
