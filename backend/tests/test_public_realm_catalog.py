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
    assert generated["park"] == _frontend_variants("openSpaceArchetypes.json")
    assert generated["street"] == _frontend_variants("streetPathArchetypes.json")
    assert len(generated["park"]) == 130
    assert sum(map(len, generated["park"].values())) == 520
    assert len(generated["street"]) == 115
    assert sum(map(len, generated["street"].values())) == 355


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
