from __future__ import annotations

import json
from pathlib import Path

from app.services.public_realm_catalog import (
    public_realm_catalog_variants,
    resolve_public_realm_catalog_identity,
)
from app.services.public_realm_lego import public_realm_fallback_marker


def _frontend_variants(filename: str) -> dict[str, tuple[str, ...]]:
    source = Path(__file__).resolve().parents[2] / "frontend" / "src" / "data" / filename
    document = json.loads(source.read_text(encoding="utf-8"))
    return {
        entry["id"]: tuple(sorted(variant["id"] for variant in entry.get("variants") or []))
        for entry in document["archetypes"]
    }


def test_backend_public_realm_trust_index_matches_all_frontend_parents_and_variants():
    generated = public_realm_catalog_variants()
    parks = _frontend_variants("openSpaceArchetypes.json")
    streets = _frontend_variants("streetPathArchetypes.json")
    native = Path(__file__).resolve().parents[2] / "frontend/src/data/nativeStreetPilots.json"
    for row in json.loads(native.read_text(encoding="utf-8")):
        streets[row["sourceArchetypeId"]] = tuple(sorted((*streets[row["sourceArchetypeId"]], row["id"])))
    validation = Path(__file__).resolve().parents[2] / "frontend/src/data/validationCatalogue.json"
    local_entries = json.loads(validation.read_text(encoding="utf-8"))["entries"]
    for entry in local_entries:
        if entry["domain"] not in ("park", "street"):
            continue
        expected = parks if entry["domain"] == "park" else streets
        parent, variant = entry["archetype_id"], entry["variant_id"]
        expected[parent] = tuple(sorted(set((*expected.get(parent, ()), variant))))
    assert generated["park"] == parks
    assert generated["street"] == streets
    assert len(generated["park"]) == 132
    assert sum(map(len, generated["park"].values())) == 522
    assert len(generated["street"]) == 117
    assert sum(map(len, generated["street"].values())) == 359


def test_local_validation_public_realm_ids_have_exact_fallback_identity():
    for archetype_id in ("student_neighbourhood_orchard_v1", "student_garden_square_v1"):
        marker = public_realm_fallback_marker(
            "green_space",
            {
                "green_space_archetype_id": archetype_id,
                "green_space_selected_variant_id": archetype_id,
            },
        )
        assert marker is not None
        assert marker["archetype_id"] == archetype_id
        assert marker["variant_id"] == archetype_id
    for archetype_id in ("student_planted_shared_lane_v1", "student_quiet_residential_street_v1"):
        marker = public_realm_fallback_marker(
            "road",
            {"road_archetype_id": archetype_id, "road_selected_variant_id": archetype_id},
        )
        assert marker is not None
        assert marker["archetype_id"] == archetype_id
        assert marker["variant_id"] == archetype_id
    assert resolve_public_realm_catalog_identity(
        "park", "student_garden_square_v1", "student_garden_square_v2"
    ) is None


def test_family_pending_identity_accepts_known_unbuilt_catalogue_ids_and_exact_variants():
    assert (
        resolve_public_realm_catalog_identity(
            "park",
            "academic_courtyard",
            "academic_courtyard_variant_2",
        )
        is not None
    )
    marker = public_realm_fallback_marker(
        "road",
        {
            "road_archetype_id": "scenic_parkway",
            "road_selected_variant_id": "scenic_parkway_v3",
        },
    )
    assert marker is not None
    assert marker["archetype_id"] == "scenic_parkway"
    assert marker["variant_id"] == "scenic_parkway_v3"


def test_family_pending_identity_rejects_unknown_and_nonexistent_prompt_like_ids():
    assert (
        resolve_public_realm_catalog_identity(
            "street",
            "ignore_previous_instructions",
        )
        is None
    )
    assert (
        resolve_public_realm_catalog_identity(
            "street",
            "scenic_parkway",
            "scenic_parkway_v99",
        )
        is None
    )
    assert (
        public_realm_fallback_marker(
            "road",
            {"road_archetype_id": "ignore_previous_instructions"},
        )
        is None
    )
