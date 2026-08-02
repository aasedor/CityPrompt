"""Regression contract for the multifamily Piece 1 timber-glass pilot."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from multifamily_piece1_specs import FAMILIES


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


def test_piece1_scope_is_one_reviewable_pilot() -> None:
    assert list(FAMILIES) == ["contemporary-timber-glass-midrise"]
    spec = next(iter(FAMILIES.values()))
    assert spec["archetype_id"] == "contemporary_midrise_residential"
    assert spec["variant_id"] == "contemporary_midrise_variant_timber_glass"
    assert spec["native_floors"] == 6


def test_pilot_manifest_is_reference_locked_and_size_flexible() -> None:
    family, spec = next(iter(FAMILIES.items()))
    root = FAMILIES_ROOT / family
    manifest = load_json(root / f"{family}_manifest.json")
    assert manifest["manifest_schema"] == 3
    assert manifest["grammar_schema_version"] == 3
    assert manifest["archetype_id"] == spec["archetype_id"]
    assert manifest["variant_id"] == spec["variant_id"]
    assert manifest["generation_archetype_id"] == spec["variant_id"]
    assert manifest["archetype_aliases"] == spec["aliases"]
    assert set(spec["aliases"]) <= set(manifest["reuse_keys"])
    assert manifest["native_floors"] == 6
    assert (manifest["min_floors"], manifest["max_floors"]) == (4, 8)
    assert manifest["architectural_identity"] == spec["identity"]
    assert manifest["material_zones"] == spec["material_zones"]
    assert manifest["glass_profile"] == spec["glass_profile"]
    assert manifest["coordinate_contract"]["origin"] == "bottom centre"
    assert manifest["coordinate_contract"]["gltf_up"] == "+Y (export_yup)"
    assert manifest["coordinate_contract"]["front_facade"] == "-Y in Blender, +Z in glTF"

    compatibility = manifest["footprint_compatibility"]
    assert compatibility["preferredProfiles"] == ["rectangle", "l_shape", "u_shape"]
    assert compatibility["minimumPreferredProfiles"] == 3
    assert set(compatibility["profiles"]) == {"rectangle", "l_shape", "u_shape"}
    assert compatibility["preferredBayMultiple_m"] == 4.8
    for profile in compatibility["profiles"].values():
        assert profile["scaleMin"] == 0.62
        assert profile["scaleMax"] == 1.4
        assert profile["maxAxisRatio"] == 1.3
        assert profile["preferredBayMultiple_m"] == 4.8

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
    assert assembled["source_variant_id"] == spec["variant_id"]
    assert assembled["generation_archetype_id"] == spec["variant_id"]
    assert assembled["triangle_count"] >= 15000
    assert assembled["material_count"] >= 10
    assert (root / assembled["filename"]).is_file()


def test_pilot_custom_skin_and_generation_provenance_are_complete() -> None:
    family, spec = next(iter(FAMILIES.items()))
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
    assert len(skin["zones"]) == 13
    for zone in skin["zones"].values():
        for lod in ("near", "far"):
            assert set(zone[lod]) == REQUIRED_CHANNELS
            assert all((root / path).is_file() for path in zone[lod].values())

    source_root = root / "textures" / "source"
    provenance = load_json(source_root / "reference-generation.json")
    assert provenance["provider"] == "OpenAI built-in image generation"
    assert provenance["model"] == "gpt-image-2"
    assert provenance["family"] == family
    assert provenance["archetype_id"] == spec["archetype_id"]
    assert provenance["variant_id"] == spec["variant_id"]
    assert provenance["design_lock"]["occupied_storeys"] == 6
    assert provenance["design_lock"]["variant_specific_contract"] == spec["design_lock"]
    assert all(item.get("source_id") for item in provenance["sources"])
    assert all((source_root / item["file"]).is_file() for item in provenance["sources"])
    generated = {
        item["file"]: item
        for item in provenance["sources"]
        if item["file"] in {
            "archetype-goalpost.png",
            "material-construction-source-v1.png",
        }
    }
    assert all(item.get("prompt") for item in generated.values())


def test_pilot_glb_keeps_physical_identity_and_optical_layers() -> None:
    family, spec = next(iter(FAMILIES.items()))
    root = FAMILIES_ROOT / family
    payload = glb_json(root / f"{family}_assembled.glb")
    names = {item.get("name", "") for item in payload.get("nodes", [])}
    assert {
        "LOBBY_DeepOccupiedVoid",
        "LOBBY_IntegratedCanopySoffit",
        "MF1_FrontGlulam_Column_0",
        "MF1_SetbackOccupiedVolume",
        "ROOF_PV_0_0_CellField",
        "MF1_Side1.0L1B0_LowIronPane",
    } <= names
    assert not any("Generic" in name for name in names)
    material_extras = [item.get("extras", {}) for item in payload.get("materials", [])]
    assert any(
        item.get("glazing_profile") == spec["glass_profile"]
        and item.get("reference_locked") is True
        for item in material_extras
    )
    assert any(item.get("occupied_depth_layer") is True for item in material_extras)
    assert any(
        item.get("multifamily_piece1_reference_locked_material") is True
        for item in material_extras
    )


def test_pilot_review_assets_signature_catalogue_and_assessment_bind() -> None:
    family, spec = next(iter(FAMILIES.items()))
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
    assert (
        FAMILIES_ROOT / f"multifamily-piece1-{family}-comparison.jpg"
    ).is_file()
    assert (root / "elevation.jpg").is_file()

    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )["families"]
    signature = signatures[spec["variant_id"]]
    assert signature == {
        "archetypeId": spec["variant_id"],
        "identity": spec["identity"],
        "materialZones": spec["material_zones"],
        "glassProfile": spec["glass_profile"],
        "elevationUrl": f"/families/{family}/elevation.jpg",
    }

    catalogue = load_json(
        REPO / "frontend" / "src" / "data" / "buildingArchetypes.json"
    )
    ids = [item["id"] for item in catalogue["archetypes"]]
    assert len(ids) == len(set(ids))
    entry = next(item for item in catalogue["archetypes"] if item["id"] == spec["archetype_id"])
    variant_ids = [item["id"] for item in entry["variants"]]
    assert len(variant_ids) == len(set(variant_ids))
    variant = next(item for item in entry["variants"] if item["id"] == spec["variant_id"])
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
