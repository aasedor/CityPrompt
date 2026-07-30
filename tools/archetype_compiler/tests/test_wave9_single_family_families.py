"""Regression contracts for the three Wave 9 detached-house families."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
FAMILY_ROOT = REPO / "frontend" / "public" / "families"
MEMORY_VERSION = "2026-07-30-detached-house-compositions-v104"
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
    "swiss-chalet-residence": {
        "parent": "mountain_alpine_chalet",
        "variant": "alpine_swiss_traditional",
        "glass": "chalet_warm_low_e",
        "floors": (1, 3, 3),
        "band": (0.86, 1.16, 1.14),
        "provenance_outputs": 5,
        "catalogue_thumbnail": (
            "/archetypes/buildings/mountain_alpine_chalet/hero.png"
        ),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "side",
            "interior",
            "stone",
            "timber",
            "carved",
            "roof",
            "metal",
            "flower",
        },
        "nodes": {
            "CHALET_FieldstoneStructuralCore",
            "CHALET_AgedTimberStructuralCore",
            "CHALET_RegisteredOccupiedDepth",
            "CHALET_RecessedArchedEntrance_DeepCarvedDoorLeaf",
            "CHALET_LeftCrossGable_SolidGableRoof",
            "CHALET_PrimaryCrossGable_SolidGableRoof",
            "CHALET_MasonryChimney_0",
            "CHALET_SideTimberReturn_-1",
        },
    },
    "timber-screen-lanehouse": {
        "parent": "japanese_contemporary_lanehouse",
        "variant": "japanese_lane_timber_screen",
        "glass": "lanehouse_screened_low_e",
        "floors": (1, 3, 3),
        "band": (0.82, 1.20, 1.18),
        "provenance_outputs": 3,
        "catalogue_thumbnail": (
            "/archetypes/buildings/japanese_contemporary_lanehouse/hero.png"
        ),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "side",
            "interior",
            "cedar",
            "metal",
            "concrete",
            "roof",
        },
        "nodes": {
            "LANE_GroundCedarStructuralCore",
            "LANE_ShadowedUpperStructuralCore",
            "LANE_UpperOccupiedGlassVolume",
            "LANE_RegisteredOccupiedDepth",
            "LANE_IntegratedBenchSeat",
            "LANE_RooftopClerestory_OccupiedClerestoryGlass",
        },
    },
    "spanish-colonial-villa": {
        "parent": "mediterranean_villa_estate",
        "variant": "med_villa_spanish_colonial",
        "glass": "villa_recessed_iron_glass",
        "floors": (1, 3, 3),
        "band": (0.84, 1.18, 1.16),
        "provenance_outputs": 6,
        "catalogue_thumbnail": (
            "/archetypes/buildings/mediterranean_villa_estate/hero.png"
        ),
        "zones": {
            "facade",
            "podium",
            "floor_a",
            "floor_b",
            "crown",
            "side",
            "interior",
            "stucco",
            "brick",
            "roof",
            "stone",
            "iron",
            "timber",
            "bronze",
        },
        "nodes": {
            "VILLA_AgedStuccoStructuralCore",
            "VILLA_RegisteredOccupiedDepth",
            "VILLA_DeepCentralStonePortal_DarkTimberDoor",
            "VILLA_CentralForgedIronBalcony_StoneSlab",
            "VILLA_LowTerracottaMainRoof",
            "VILLA_LeftBellTowerBody",
            "VILLA_PhysicalBronzeBell",
            "VILLA_ExposedBrickPatch_LeftLarge_ExposedBrick_0_1",
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
def test_manifest_binds_house_aliases_scale_band_and_flexible_stack(family: str):
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
    assert (
        manifest["min_floors"],
        manifest["max_floors"],
        manifest["native_floors"],
    ) == expected["floors"]
    assert manifest["assembled"]["stack"][0]["role"] == "assembled"
    assert manifest["massing_graph"]["type"] == "fixed_landmark"
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
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((root / module["filename"]).is_file() for module in modules)
    assert (root / manifest["assembled"]["filename"]).is_file()


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_fixed_glb_contains_house_geometry_and_reference_glazing(family: str):
    expected = FAMILIES[family]
    payload = glb_json(FAMILY_ROOT / family / f"{family}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert expected["nodes"] <= node_names

    if family == "swiss-chalet-residence":
        assert len(
            [
                name
                for name in node_names
                if name and name.endswith("_PhysicalPane")
                and name.startswith("CHALET_ResidentialSash_")
            ]
        ) >= 15
    if family == "timber-screen-lanehouse":
        assert len(
            [
                name
                for name in node_names
                if name and name.startswith(
                    "LANE_ContinuousPrivacyScreen_VerticalCedarBatten_"
                )
            ]
        ) >= 30
    if family == "spanish-colonial-villa":
        assert len(
            [
                name
                for name in node_names
                if name and name.startswith("VILLA_ExposedBrickPatch_")
            ]
        ) >= 100

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
    assert len(provenance["outputs"]) == expected["provenance_outputs"]
    assert {"elevation-source.png", "occupied-depth-source.png"} <= {
        item["file"] for item in provenance["outputs"]
    }
    assert provenance["elevation_prompt"]
    assert provenance["occupied_depth_prompt"]
    if expected["provenance_outputs"] > 2:
        assert provenance["material_prompts"]

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


def test_signatures_and_existing_catalogue_cards_resolve_to_house_assets():
    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    assert len(catalogue["archetypes"]) == 224
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
        assert entry["thumbnailUrl"] == expected["catalogue_thumbnail"]
        assert any(
            variant["id"] == expected["variant"]
            for variant in entry["variants"]
        )
        hero_path = (
            REPO
            / "frontend"
            / "public"
            / expected["catalogue_thumbnail"].removeprefix("/")
        )
        assert hero_path.is_file()


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_assessment_uses_current_quality_memory(family: str):
    assessment = load_json(FAMILY_ROOT / family / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
