"""Regression tests for the finite V86 catalogue campaign."""
from __future__ import annotations

import pytest

from plan_catalogue_rollout_v86 import DEFAULT_CAMPAIGN, build_plan
from run_catalogue_batch_v86 import validate_registry
from signature_profiles import inject_signature


def test_live_catalogue_is_fully_partitioned_into_finite_batches():
    plan = build_plan(DEFAULT_CAMPAIGN)

    assert plan["summary"]["parent_archetypes"] == 224
    assert plan["summary"]["named_variant_targets"] == 893
    assert plan["summary"]["representative_targets"] == 224
    assert plan["summary"]["remaining_variant_targets"] == 669
    assert all(1 <= batch["target_count"] <= 5 for batch in plan["batches"])
    assert all(row.get("batch_id") for row in plan["targets"] if row["state"] != "approved_existing")


def test_campaign_pilot_is_exact_variant_locked_and_authored():
    plan = build_plan(DEFAULT_CAMPAIGN)
    target = next(
        row for row in plan["targets"]
        if row["variant_id"] == "modernist_civic_concrete_brutalist"
    )

    assert target["state"] in {"ready_to_generate", "generated_human_review"}
    assert target["profile_key"] == target["variant_id"]
    assert target["reference_roles"] == ["oblique_massing", "roof_plan", "street_identity"]
    assert target["facade_sheet"].endswith("facade_sheets_v8/modernist-civic-block")


def test_modernist_pilot_owns_roof_membranes_as_real_geometry():
    grammar = inject_signature({
        "source": {
            "archetype_id": "modernist_civic_block",
            "variant_id": "modernist_civic_concrete_brutalist",
        },
        "dimensions": {},
        "materials": {"primary": {}, "secondary": {}, "accent": {}, "concrete": {}, "roof": {}},
    }, "modernist_civic_block", variant_id="modernist_civic_concrete_brutalist")
    graph = grammar["massing_graph"]
    nodes = {node["id"]: node for node in graph["nodes"]}
    contract = grammar["architectural_signature"]["production_contract"]

    assert graph["profile"] == "modernist_civic_concrete_image_lock_v86"
    assert nodes["roof_penthouse"]["size"][:2] == [24.0, 18.0]
    assert nodes["civic_roof_membrane"]["material"] == "roof"
    assert nodes["civic_penthouse_membrane"]["material"] == "roof"
    assert contract["surface_finish"]["required_baked_materials"] == ["concrete", "roof"]


def test_batch_runner_rejects_paid_or_unbounded_registries():
    base_entry = {
        "archetype_id": "a", "variant_id": "v", "family_id": "f",
        "width_m": 10, "depth_m": 10, "floors": 2,
        "facade_sheet": "tools/archetype_compiler/facade_sheets_v8/modernist-civic-block",
    }
    with pytest.raises(SystemExit, match="never performs paid"):
        validate_registry({
            "schema": "catalogue-rollout-batch@1", "paid_facade_calls": 1,
            "entries": [base_entry],
        })
    with pytest.raises(SystemExit, match="1-5"):
        validate_registry({
            "schema": "catalogue-rollout-batch@1", "paid_facade_calls": 0,
            "entries": [base_entry] * 6,
        })
