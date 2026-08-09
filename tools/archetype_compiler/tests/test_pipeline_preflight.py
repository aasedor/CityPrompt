"""Regression tests for the cheap production preflight."""
from __future__ import annotations

import json


def source_payload() -> dict:
    return {
        "archetypeId": "gold_archetype",
        "variants": [
            {"id": "gold_variant", "thumbnailUrl": "/archetypes/gold/variant_0.png"}
        ],
        "selectedVariant": {
            "id": "gold_variant",
            "thumbnailUrl": "/archetypes/gold/variant_0.png",
        },
        "generationStyleInput": {"archetypeId": "gold_archetype_variant_0"},
        "referenceViews": [
            {"role": "street_identity", "path": "/archetypes/gold/variant_0.png"},
            {"role": "oblique_massing", "path": "/archetypes/gold/variant_0_angle_60.jpg"},
            {"role": "roof_or_aerial", "path": "/archetypes/gold/variant_0_angle_90.jpg"},
        ],
    }


def semantic_grammar() -> dict:
    return {
        "family_id": "gold-family",
        "source": {"archetype_id": "gold_archetype", "variant_id": "gold_variant"},
        "dimensions": {"width_m": 24.0, "depth_m": 16.0, "default_floors": 5},
        "architectural_signature": {
            "production_contract": {
                "identity_mode": "semantic_stack",
                "fixed_identity": ["entrance", "corners", "roof"],
                "repeatable_capacity": ["middle bays"],
            }
        },
    }


def test_complete_semantic_stack_preflight_passes():
    from pipeline_preflight import assess_generation_preflight

    report = assess_generation_preflight(source_payload(), semantic_grammar())

    assert report["status"] == "pass"
    assert report["paid_generation_allowed"] is True
    assert report["identity_mode"] == "semantic_stack"


def test_multi_variant_parent_and_incomplete_references_block_paid_generation():
    from pipeline_preflight import assess_generation_preflight

    source = source_payload()
    source["selectedVariant"] = None
    source["referenceViews"] = source["referenceViews"][:1]
    report = assess_generation_preflight(source, semantic_grammar())

    assert report["status"] == "fail"
    assert report["paid_generation_allowed"] is False
    assert {item["id"] for item in report["failures"]} >= {
        "variant_not_selected",
        "incomplete_reference_set",
    }


def test_massing_graph_dimensions_are_executable_contract():
    from pipeline_preflight import assess_generation_preflight

    grammar = semantic_grammar()
    grammar["architectural_signature"]["production_contract"]["identity_mode"] = "massing_graph"
    grammar["massing_graph"] = {
        "profile": "gold_graph_v1",
        "reference_dimensions": {"width_m": 30.0, "depth_m": 16.0, "floors": 5},
    }
    report = assess_generation_preflight(source_payload(), grammar)

    assert report["status"] == "fail"
    assert {item["id"] for item in report["failures"]} == {
        "massing_reference_dimensions_mismatch"
    }


def test_unclassified_generic_stack_is_not_production_ready():
    from pipeline_preflight import assess_generation_preflight

    grammar = semantic_grammar()
    grammar["architectural_signature"].pop("production_contract")
    report = assess_generation_preflight(source_payload(), grammar)

    assert report["status"] == "fail"
    assert {item["id"] for item in report["failures"]} >= {
        "missing_production_contract",
        "unclassified_identity_mode",
    }


def test_selective_metadata_requires_image_confirmation_and_bounded_use():
    from pipeline_preflight import assess_generation_preflight

    source = source_payload()
    source["selectedVariant"]["roofDetail"] = {"form": "low green copper hip"}
    grammar = semantic_grammar()
    signature = grammar["architectural_signature"]
    signature["evidence_policy"] = {
        "authority": "reference_images",
        "metadata_mode": "selective",
        "selected_metadata": [{
            "path": "selectedVariant.roofDetail.form",
            "cue": "green copper",
            "purpose": "roof material family only",
            "image_consistent": True,
        }],
        "ignored_metadata": [{
            "path": "styleProfile",
            "reason": "generic parent prose is not visible evidence",
        }],
    }
    signature["production_contract"]["metadata_cues"] = ["green copper"]

    report = assess_generation_preflight(source, grammar)
    assert report["status"] == "pass"
    assert next(gate for gate in report["gates"] if gate["id"] == "unsafe_metadata_evidence")["passed"]

    signature["evidence_policy"]["selected_metadata"][0]["image_consistent"] = False
    report = assess_generation_preflight(source, grammar)
    assert "unsafe_metadata_evidence" in {item["id"] for item in report["failures"]}


def test_disabled_metadata_cannot_leak_into_contract_cues():
    from pipeline_preflight import assess_generation_preflight

    grammar = semantic_grammar()
    signature = grammar["architectural_signature"]
    signature["evidence_policy"] = {
        "authority": "reference_images", "metadata_mode": "disabled",
    }
    signature["production_contract"]["metadata_cues"] = ["generic roof prose"]
    report = assess_generation_preflight(source_payload(), grammar)
    assert "unsafe_metadata_evidence" in {item["id"] for item in report["failures"]}


def test_catalogue_import_gate_requires_human_visual_approval(tmp_path):
    from import_manifest import catalogue_release_gate

    (tmp_path / "production_preflight.json").write_text(
        json.dumps({"status": "pass"}), encoding="utf-8"
    )
    (tmp_path / "validation_report.json").write_text(
        json.dumps({"status": "pass"}), encoding="utf-8"
    )

    ready, detail = catalogue_release_gate(tmp_path)
    assert ready is False
    assert "visual_approval.json" in detail

    approval = {
        "schema": "building-visual-approval@1",
        "decision": "approved",
        "reviewer": "test-reviewer",
        "approved_at": "2026-08-07T00:00:00+00:00",
        "reference_set": "test-gold-set",
        "checks": {
            "block_scale": True,
            "building_scale": True,
            "facade_scale": True,
            "orbit_and_context": True,
        },
    }
    (tmp_path / "visual_approval.json").write_text(
        json.dumps(approval), encoding="utf-8"
    )

    ready, detail = catalogue_release_gate(tmp_path)
    assert ready is True
    assert "approved" in detail
