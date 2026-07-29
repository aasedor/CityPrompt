"""Regression contract for the Wave 4 standard-building pilot."""
from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FAMILY = "historical-brick-main-street"
FAMILY_ROOT = REPO / "frontend" / "public" / "families" / FAMILY


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_historical_brick_manifest_is_a_resizable_reference_locked_family():
    manifest = load_json(FAMILY_ROOT / f"{FAMILY}_manifest.json")

    assert manifest["archetype_id"] == "historical_brick_main_street"
    assert manifest["variant_id"] == "historical_brick_victorian"
    assert set(manifest["archetype_aliases"]) == {
        "historical_brick_main_street",
        "historical_brick_victorian",
    }
    assert manifest["native_floors"] == 2
    assert (manifest["min_floors"], manifest["max_floors"]) == (2, 4)
    assert manifest["massing_graph"]["type"] != "fixed_landmark"

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
    assert all(
        (FAMILY_ROOT / module["filename"]).is_file()
        for module in modules
    )
    assert (FAMILY_ROOT / manifest["assembled"]["filename"]).is_file()

    compatibility = manifest["footprint_compatibility"]
    assert set(compatibility["preferredProfiles"]) == {
        "rectangle",
        "l_shape",
        "u_shape",
    }
    assert compatibility["preferredBayMultiple_m"] == 2.10
    assert compatibility["profiles"]["rectangle"]["recommendedWidth_m"] == [8, 30]


def test_historical_brick_skin_authors_every_orbit_visible_material_system():
    skin = load_json(FAMILY_ROOT / "textures" / "skin_manifest.json")
    assert skin["reference_registration"]["mode"] == "archetype_specific"
    assert skin["reference_registration"]["generic_tiling_allowed"] is False
    assert set(skin["reference_registration"]["registered_elevations"]) == {
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
        "side_crown",
        "deck",
        "roof",
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
            assert all((FAMILY_ROOT / path).is_file() for path in zone[lod].values())

    assessment = load_json(FAMILY_ROOT / "quality_assessment.json")
    assert assessment["memory_version"] == (
        "2026-07-29-reference-specific-window-materiality-v99"
    )
    assert assessment["status"] == "pass"
    assert assessment["high_quality_ready"] is True


def test_historical_brick_catalogue_card_and_signature_remain_wired():
    catalogue = load_json(REPO / "frontend" / "src" / "data" / "buildingArchetypes.json")
    cards = [
        item
        for item in catalogue["archetypes"]
        if item["id"] == "historical_brick_main_street"
    ]
    assert len(cards) == 1
    assert cards[0]["thumbnailUrl"].endswith(
        "/historical_brick_main_street/hero.png"
    )
    assert (
        REPO
        / "frontend"
        / "public"
        / cards[0]["thumbnailUrl"].removeprefix("/")
    ).is_file()

    signatures = load_json(
        REPO / "frontend" / "src" / "data" / "legoFamilySignatures.json"
    )
    signature = signatures["families"]["historical_brick_main_street"]
    assert signature["archetypeId"] == "historical_brick_main_street"
    assert signature["elevationUrl"] == (
        "/families/historical-brick-main-street/elevation.jpg"
    )
    assert signature["identity"]
    assert signature["materialZones"]
    assert signature["glassProfile"]
