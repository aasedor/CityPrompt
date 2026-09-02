from __future__ import annotations

from tools.archetype_compiler.architectural_clay_catalogue import load_catalogue, validate_catalogue


def test_saved_architectural_clay_catalogue_is_valid() -> None:
    catalogue = load_catalogue()
    assert validate_catalogue(catalogue) == []
    assert len(catalogue["assets"]) == 3


def test_clay_first_inglewood_asset_has_source_and_runtime_contracts() -> None:
    catalogue = load_catalogue()
    asset = next(
        item
        for item in catalogue["assets"]
        if item["candidate"] == "inglewood-victorian-brick-commercial-semantic-clay-v001"
    )
    assert asset["generation_mode"] == "clay_first"
    assert len(asset["source_lock"]) == 3
    assert asset["authoring"]["modular_by_bay"] is True
    assert asset["authoring"]["mesh_objects"] > asset["runtime"]["mesh_objects"]
    assert asset["runtime"]["mesh_objects"] == 8
    assert asset["runtime"]["images"] == 0
    assert asset["runtime"]["textures"] == 0
    assert asset["semantic_size_grammar"]["stretching_allowed"] is False


def test_no_saved_clay_candidate_is_implicitly_runtime_approved() -> None:
    catalogue = load_catalogue()
    for asset in catalogue["assets"]:
        assert asset["runtime_seed_allowed"] is False
        assert asset["independent_keeper_review"] == "pending"


def test_private_runtime_trials_are_exact_variant_and_compile_gated() -> None:
    catalogue = load_catalogue()
    trials = [asset for asset in catalogue["assets"] if asset.get("runtime_trial")]
    assert {asset["source_variant"] for asset in trials} == {
        "bell_gable_traditional_red",
        "inglewood_victorian_brick",
    }
    for asset in trials:
        trial = asset["runtime_trial"]
        assert trial["scope"] == "private_local"
        assert trial["planner_selectable"] is True
        assert trial["exact_variant_id"] == asset["source_variant"]
        assert trial["generated_only_after_compile"] is True
        assert len(asset["source_lock"]) == 3
