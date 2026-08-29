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
    assert method["version"] == "6.0"
    assert method["canonical_human_method"] == "docs/RLASM_LATEST_METHOD.md"
    assert (ROOT / method["canonical_human_method"]).is_file()
    assert method["source_contract"]["minimum_compatible_roles"] == [
        "front",
        "oblique",
        "top",
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


def test_registry_preserves_supersession_evidence() -> None:
    registry = load_json("tools/archetype_compiler/rlasm_keeper_registry.json")
    entries = {entry["candidate"]: entry for entry in registry["entries"]}
    assert entries["10-second-empire-fire-station-rlasm-v20"]["status"] == "keeper_approved"
    older = entries["10-second-empire-fire-station-rlasm-v18"]
    assert older["status"] == "superseded"
    assert older["superseded_by"] == "10-second-empire-fire-station-rlasm-v20"
