"""Contract tests for the canonical RLASM method and keeper registry."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_rlasm_v6_is_single_executable_authority() -> None:
    method = load_json("tools/archetype_compiler/rlasm_method.json")
    assert method["schema"] == "cityprompt.rlasm.method@6"
    assert method["version"] == "6.1"
    assert method["canonical_human_method"] == "docs/RLASM_LATEST_METHOD.md"
    assert (ROOT / method["canonical_human_method"]).is_file()
    assert method["source_contract"]["minimum_compatible_roles"] == [
        "front",
        "oblique",
        "top",
    ]
    assert method["reference_keeper_examples"] == [
        "07-barcelona-modernist-printing-house-rlasm-v7",
        "10-amsterdam-bell-gable-house-rlasm-v10",
        "rlasm-amsterdam-hofje-medieval-v023",
    ]


def test_keeper_requires_holistic_independent_review() -> None:
    method = load_json("tools/archetype_compiler/rlasm_method.json")
    principles = method["principles"]
    assert principles["general_high_quality_ready_is_keeper_approval"] is False
    assert principles["builder_may_self_approve_keeper"] is False
    assert principles["scoped_review_may_promote_keeper"] is False
    assert "holistic_adversarial_regression" in method["review_contract"][
        "keeper_promotion_requires"
    ]


def test_required_camera_contract_is_complete() -> None:
    method = load_json("tools/archetype_compiler/rlasm_method.json")
    assert set(method["required_baseline_views"]) == {
        "front.png",
        "front_corner.png",
        "aerial.png",
        "left_side.png",
        "right_side.png",
        "rear.png",
        "rear_side.png",
        "facade_close.png",
        "architecture_close.png",
        "glass_close.png",
    }


def test_forward_pilot_registration_and_alpha_contract() -> None:
    method = load_json("tools/archetype_compiler/rlasm_method.json")
    registration = method["identity_registration_contract"]
    assert registration["register_to_carrier_exterior_face_not_center"] is True
    assert registration["carrier_thickness_in_datum"] is True
    assert registration["actual_alpha_channel_inspection_required"] is True
    assert registration["checkerboard_preview_is_alpha_proof"] is False


def test_forward_pilot_transparent_roof_and_program_contract() -> None:
    method = load_json("tools/archetype_compiler/rlasm_method.json")
    roof = method["transparent_roof_contract"]
    assert roof["multi_wing_roof_uses_one_union_outline"] is True
    assert roof["single_continuous_curb_and_flashing_owner"] is True
    assert roof["single_source_conditioned_optical_family_across_all_facets"] is True
    assert roof["stark_unexplained_facet_family_switches_allowed"] is False
    assert roof["overlapping_transparent_roof_primitives_allowed"] is False
    roof_edge = method["roof_edge_identity_contract"]
    assert roof_edge["ironwork_section_and_cadence_match_locked_source"] is True
    assert roof_edge["supports_have_positive_contact"] is True
    assert roof_edge["generic_repeated_perimeter_template_allowed"] is False
    assert method["program_contract"][
        "source_specific_workflow_visibly_identifiable"
    ] is True
    assert method["unskinned_gate"][
        "orientation_specific_openings_visible_in_front_side_and_rear_roles"
    ] is True
    assert method["evidence_contract"][
        "revalidate_camera_targets_and_occlusion_after_geometry_change"
    ] is True
    assert method["evidence_contract"][
        "whole_envelope_views_require_visible_neutral_safety_margin"
    ] is True


def test_registry_preserves_supersession_evidence() -> None:
    registry = load_json("tools/archetype_compiler/rlasm_keeper_registry.json")
    entries = {entry["candidate"]: entry for entry in registry["entries"]}
    assert entries["10-second-empire-fire-station-rlasm-v20"]["status"] == "keeper_approved"
    older = entries["10-second-empire-fire-station-rlasm-v18"]
    assert older["status"] == "superseded"
    assert older["superseded_by"] == "10-second-empire-fire-station-rlasm-v20"
    pilot = entries["07-barcelona-modernist-printing-house-rlasm-v7"]
    assert pilot["status"] == "keeper_approved"
    assert pilot["source_mode"] == "exact_catalogue_photos_only"
    amsterdam = entries["10-amsterdam-bell-gable-house-rlasm-v10"]
    assert amsterdam["status"] == "keeper_approved"
    assert amsterdam["review_scope"] == "holistic_independent"
    assert amsterdam["source_mode"] == "exact_catalogue_photos_only"
    assert amsterdam["standard_role"] == "raw_photo_forward_standard"
    hofje = entries["rlasm-amsterdam-hofje-medieval-v023"]
    assert hofje["status"] == "keeper_approved"
    assert hofje["review_scope"] == "holistic_independent"
    assert hofje["source_mode"] == "exact_catalogue_photos_only"
    assert hofje["standard_role"] == (
        "formal_courtyard_and_pantile_forward_standard"
    )
    assert (ROOT / hofje["package"] / "keeper-manifest.json").is_file()
