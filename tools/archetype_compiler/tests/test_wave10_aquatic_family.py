"""Regression contracts for the Wave 10 wave-shell aquatic-centre family."""
from __future__ import annotations

import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "parametric-wave-shell-aquatic-centre"
PARENT = "community_recreation_centre"
VARIANT = "rec_centre_aquatic"
ALIASES = {
    PARENT,
    VARIANT,
    "aquatic_natatorium_complex",
    "parametric_wave_shell",
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
    "roof_metal",
    "timber",
    "concrete",
    "polycarbonate",
    "cobalt_panel",
    "plinth",
    "pool_water",
    "wet_deck",
    "white_structure",
    "landscape",
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
    assert manifest["glass_profile"] == "aquatic_low_iron_pool_clear"
    assert (
        manifest["native_width_m"],
        manifest["native_depth_m"],
        manifest["native_floors"],
    ) == (80.0, 55.0, 1)
    assert (manifest["min_floors"], manifest["max_floors"]) == (1, 2)
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
    assert set(compatibility["profiles"]) == {"rectangle"}
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.78,
        "scaleMax": 1.22,
        "maxAxisRatio": 1.18,
    }
    assert compatibility["preferredBayMultiple_m"] == 5.0

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
    assert all(module["width_m"] == 80.0 for module in modules)
    assert all(module["depth_m"] == 55.0 for module in modules)
    assert all(
        module["repeatable_z"]
        and module["assembly_class"] == "repeatable_middle"
        for module in modules
        if module["role"] == "floor"
    )
    assert all(module["allow_inset_footprint"] for module in modules)
    assert all((ROOT / module["filename"]).is_file() for module in modules)

    assembled = manifest["assembled"]
    assert assembled["footprint_profile"] == "rectangle"
    assert [item["role"] for item in assembled["stack"]] == ["assembled"]
    graph = assembled["massing_graph"]
    assert graph["type"] == "fixed_landmark"
    assert graph["silhouette"] == "continuous_asymmetrical_double_wave_shell"
    assert graph["competition_crest"] == 1
    assert graph["leisure_crest"] == 1
    assert graph["glazed_saddle_valley"] is True
    assert graph["cable_stay_masts"] == 2
    assert graph["concrete_branch_support_assemblies"] == 8
    assert graph["recessed_public_entrance"] == 1
    assert graph["competition_pool_length_m"] == 50
    assert (ROOT / assembled["filename"]).is_file()


def test_glb_contains_real_shell_supports_entry_pool_and_service_envelope():
    payload = glb_json(ROOT / f"{FAMILY}_assembled.glb")
    node_names = {node.get("name") for node in payload.get("nodes", [])}
    assert {
        "AquaticContinuousDoubleWaveShell",
        "AquaticWarmTimberWaveSoffit",
        "AquaticCableStayMast_0",
        "AquaticCableStayMast_1",
        "AquaticConcreteIntegratedBranchSupport_00",
        "AquaticConcreteIntegratedBranchSupport_07",
        "AquaticEntryDarkPortalHeader",
        "AquaticEntryWarmLobbyBackdrop",
        "AquaticEntryDoorLeaf_00_PhysicalGlass",
        "AquaticEntryDoorLeaf_04_PhysicalGlass",
        "AquaticCompetitionPoolWater",
        "AquaticLeisurePoolWater",
        "AquaticDivingTowerColumn",
        "AquaticRearBay_00_RibbedPolycarbonate",
        "AquaticFrontCobaltBookendPanel_0",
        "AquaticFrontCobaltBookendPanel_1",
    } <= node_names
    assert sum(
        bool(name and name.startswith("AquaticCableStayMast_"))
        for name in node_names
    ) == 2
    assert sum(
        bool(name and "TensionRod" in name) for name in node_names
    ) == 12
    assert sum(
        bool(name and "IntegratedBranchSupport" in name) for name in node_names
    ) == 8
    assert sum(
        bool(name and "PhysicalLowIronPane" in name) for name in node_names
    ) == 16
    assert sum(
        bool(name and "AquaticStandingSeam_" in name) for name in node_names
    ) == 31
    assert sum(
        bool(name and "AquaticGlulamWaveRib_" in name) for name in node_names
    ) == 9

    material_extras = [
        item.get("extras", {}) for item in payload.get("materials", [])
    ]
    assert any(
        extras.get("glazing_profile") == "aquatic_low_iron_pool_clear"
        and extras.get("source_variant_id") == VARIANT
        and extras.get("reference_locked") is True
        for extras in material_extras
    )
    assert any(
        extras.get("glazing_profile") == "aquatic_pool_water"
        and extras.get("underlay_role") == "physical_pool_water_depth"
        for extras in material_extras
    )
    assert any(
        extras.get("underlay_role")
        == "occupied_depth_behind_physical_glazing"
        for extras in material_extras
    )
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
    assert len(provenance["research"]) >= 6
    outputs = {item["file"]: item for item in provenance["assets"]}
    assert {
        "archetype-goalpost.png",
        "front-elevation-source-v1.png",
        "aerial-roof-source-v1.png",
        "rear-service-source-v1.png",
        "material-construction-source-v1.png",
        "pbr-material-source-v1.png",
        "pool-occupied-depth-source-v1.png",
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
        "entry_close",
        "glazing_close",
        "pool_close",
        "roof_close",
        "side_close",
        "structure_close",
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
        assert signature["glassProfile"] == "aquatic_low_iron_pool_clear"
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
        "/archetypes/buildings/parametric-wave-shell-aquatic-centre/hero.png"
    )
    compatibility = entry["footprintCompatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle"]
    assert set(compatibility["profiles"]) == {"rectangle"}
    assert compatibility["fixedLandmarkScaleBand"] == {
        "scaleMin": 0.78,
        "scaleMax": 1.22,
        "maxAxisRatio": 1.18,
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
