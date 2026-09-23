from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    build_public_realm_capability_catalog,
    plan_public_realm_recipe,
)


MANIFEST = Path(__file__).resolve().parents[2] / "frontend/src/data/nativeStreetPilots.json"


def test_native_street_candidates_compile_exact_locked_recipes_without_student_exposure():
    catalog = build_native_street_candidate_catalog(MANIFEST)
    rows = {row["id"]: row for row in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    assert len(catalog.capabilities) == 2
    assert catalog.prompt_vocabulary == ""
    active = build_public_realm_capability_catalog()
    for capability in catalog.capabilities:
        selection = capability.selections[0]
        pilot = rows[selection.variant_id]
        assert selection.archetype_id == pilot["sourceArchetypeId"]
        assert capability.family_id not in active.family_ids
        assert selection.variant_id not in active.variants_by_archetype.get(selection.archetype_id, ())
        recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id,
            variant_id=selection.variant_id,
            preferred_family_id=capability.family_id,
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=96),
        ), catalog=catalog)
        assert recipe.component_set_ids == selection.component_set_ids
        assert f"source_recipe:{pilot['sourceRecipeSha256']}" in recipe.component_set_ids
        assert len(recipe.component_set_ids) == len(pilot["modules"]) + 3
        assert recipe.recipe_hash == plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id,
            variant_id=selection.variant_id,
            preferred_family_id=capability.family_id,
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=96),
        ), catalog=catalog).recipe_hash


def test_candidate_contract_rejects_untrusted_parent_and_changed_module_hash(tmp_path: Path):
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows[0]["sourceArchetypeId"] = "invented_street"
    changed = tmp_path / "pilots.json"
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="trusted street parent"):
        build_native_street_candidate_catalog(changed)
    rows[0]["sourceArchetypeId"] = "neighborhood_main_street"
    first_module = next(iter(rows[0]["modules"].values()))
    original_sha = first_module["sha256"]
    first_module["sha256"] = "not-a-hash"
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="source or module hash"):
        build_native_street_candidate_catalog(changed)
    first_module["sha256"] = original_sha
    rows[0]["sections"][1]["x"] += 0.2
    changed.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(ValueError, match="metric section"):
        build_native_street_candidate_catalog(changed)
