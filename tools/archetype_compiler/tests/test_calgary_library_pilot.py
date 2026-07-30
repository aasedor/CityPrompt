"""Regression contracts for the Calgary Central Library pilot."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "calgary-central-library"
ROOT = REPO / "frontend" / "public" / "families" / FAMILY
MEMORY_VERSION = "2026-07-29-registered-source-construction-zones-v103"


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


def test_manifest_binds_parent_variant_and_flexible_landmark_fit():
    manifest = load_json(ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == "calgary_new_central_library"
    assert manifest["variant_id"] == "library_original_snohetta"
    assert manifest["generation_archetype_id"] == "library_original_snohetta"
    assert set(manifest["archetype_aliases"]) == {
        "calgary_new_central_library",
        "library_original_snohetta",
    }
    assert manifest["glass_profile"] == "calgary_library_low_iron_fritted"
    assert manifest["native_floors"] == 4
    assert manifest["assembled"]["stack"][0]["role"] == "assembled"
    assert manifest["massing_graph"]["type"] == "fixed_landmark"

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert compatibility["minimumPreferredProfiles"] == 1
    assert compatibility["profileRationale"]
    band = compatibility["fixedLandmarkScaleBand"]
    assert band == {
        "scaleMin": 0.84,
        "scaleMax": 1.16,
        "maxAxisRatio": 1.14,
    }

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
    assert all((ROOT / module["filename"]).is_file() for module in manifest["modules"])


def test_fixed_glb_contains_constructed_panel_arch_glass_and_transit_systems():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    nodes = {node.get("name"): node for node in payload.get("nodes", [])}
    assert {
        "CALGARY_UnitizedPanels_opaque",
        "CALGARY_UnitizedPanels_clear",
        "CALGARY_FiveFamilyUnitizedPanelJointSystem",
        "CALGARY_DoubleCurvedCedarSoffit",
        "CALGARY_IntegratedCedarArchReveal",
        "CALGARY_SurfaceFollowingCedarBattenSystem",
        "CALGARY_RenderLockedOccupiedDepthUnderlay_0",
        "CALGARY_CTrainPortalShadow",
        "CALGARY_FacetedRoofField",
        "CALGARY_CentralAtriumSkylight_Clear",
    } <= set(nodes)
    assert (
        nodes["CALGARY_UnitizedPanels_opaque"]["extras"]["panel_topology"]
        == "clipped_hexagonal_unitized"
    )
    assert (
        nodes["CALGARY_IntegratedCedarArchReveal"]["extras"][
            "subtractive_identity"
        ]
        == "thick cedar reveal continuous with soffit"
    )

    material_extras = [
        material.get("extras", {})
        for material in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "calgary_library_low_iron_fritted"
        and extras.get("pane_treatment") == "clear_low_iron_triple_glazed"
        for extras in material_extras
    )
    assert any(
        extras.get("glazing_profile") == "calgary_library_low_iron_fritted"
        and extras.get("pane_treatment") == "graduated_ceramic_frit"
        for extras in material_extras
    )
    assert any(
        extras.get("reference_locked") is True
        and extras.get("underlay_role")
        == "occupied_depth_behind_physical_glazing"
        for extras in material_extras
    )


def test_custom_skin_provenance_and_multiview_evidence_are_complete():
    skin = load_json(ROOT / "textures" / "skin_manifest.json")
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
        "cedar",
        "concrete",
        "metal",
        "interior",
        "roof",
    } == set(skin["zones"])
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
            assert all((ROOT / path).is_file() for path in zone[lod].values())

    provenance = load_json(
        ROOT / "textures" / "source" / "reference-generation.json"
    )
    assert provenance["tool"] == "OpenAI built-in ImageGen"
    assert provenance["model"] == "gpt-image-2"
    assert len(provenance["outputs"]) == 3
    research = load_json(ROOT / "textures" / "source" / "research-sources.json")
    assert len(research["primary_sources"]) >= 5

    for role in (
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "cedar_close",
        "context",
    ):
        assert (ROOT / f"{FAMILY}_{role}.png").is_file()
    assert (ROOT / f"{FAMILY}_comparison-sheet.png").is_file()
    assert (ROOT / "elevation.jpg").is_file()


def test_signatures_and_existing_catalogue_card_resolve_to_delivered_assets():
    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    for archetype_id in (
        "calgary_new_central_library",
        "library_original_snohetta",
    ):
        entry = signatures[archetype_id]
        assert entry["archetypeId"] == archetype_id
        assert entry["glassProfile"] == "calgary_library_low_iron_fritted"
        assert entry["elevationUrl"] == "/families/calgary-central-library/elevation.jpg"
        assert entry["identity"]
        assert entry["materialZones"]

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    matches = [
        entry
        for entry in catalogue["archetypes"]
        if entry["id"] == "calgary_new_central_library"
    ]
    assert len(matches) == 1
    entry = matches[0]
    paths = [entry["thumbnailUrl"], *[
        variant["thumbnailUrl"] for variant in entry["variants"]
    ]]
    assert len(paths) == 5
    assert len(set(paths)) == 5
    assert all(
        (REPO / "frontend" / "public" / path.removeprefix("/")).is_file()
        for path in paths
    )


def test_assessment_uses_current_quality_memory():
    assessment = load_json(ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == MEMORY_VERSION
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True
