import json
from pathlib import Path


TOOLS = Path(__file__).parents[1]


def load(name: str):
    return json.loads((TOOLS / name).read_text(encoding="utf-8"))


def test_round_has_ten_exact_variants_in_two_bounded_batches():
    batch_a = load("catalogue_round_v87_batch_a.json")
    batch_b = load("catalogue_round_v87_batch_b.json")
    entries = [*batch_a["entries"], *batch_b["entries"]]

    assert len(batch_a["entries"]) == 5
    assert len(batch_b["entries"]) == 5
    assert len({(item["archetype_id"], item["variant_id"]) for item in entries}) == 10
    assert all(batch["paid_facade_calls"] == 0 for batch in (batch_a, batch_b))


def test_round_profiles_preserve_roofs_wraps_and_void_depth():
    payload = load("architectural_signature_profiles.d/catalogue_round_v87.json")
    profiles = payload["profiles"]
    assert len(profiles) == 10

    for profile in profiles.values():
        graph = profile["massing_graph"]
        axes = {
            item["axis"]
            for item in graph["assemblies"]
            if item.get("kind") == "facade_skin"
        }
        assert axes == {"front", "rear", "left", "right"}
        assert any(node.get("material") == "roof" for node in graph["nodes"])

    moorish = profiles["med_arcade_moorish"]["massing_graph"]
    arcade = next(node for node in moorish["nodes"] if node["id"] == "ground_arcade")
    assert arcade["kind"] == "opening_block"
    assert arcade["opening_count"] == 3
    assert arcade["section_mode"] == "recessed"
    assert len(next(
        item["opening_clearances"]
        for item in moorish["assemblies"]
        if item["id"] == "skin_arcade_front"
    )) == 3


def test_large_modern_facades_use_lightweight_glass_and_repaired_dimensions():
    profiles = load("architectural_signature_profiles.d/catalogue_round_v87.json")["profiles"]
    for variant in (
        "modernist_civic_white_corbusian",
        "modernist_civic_precast_panel",
        "glass_office_terracotta_fins",
        "glass_office_dark_frame",
    ):
        overlays = [
            item for item in profiles[variant]["massing_graph"]["assemblies"]
            if item.get("kind") == "glazing_overlay"
        ]
        assert overlays
        assert {item["frame_mode"] for item in overlays} == {"mask_only"}

    terracotta = profiles["glass_office_terracotta_fins"]["massing_graph"]
    assert terracotta["reference_dimensions"] == {
        "width_m": 36.0,
        "depth_m": 25.0,
        "floors": 5,
    }
    assert len([node for node in terracotta["nodes"] if node["id"].startswith("terrace_edge_")]) == 5

    precast_identity = profiles["modernist_civic_precast_panel"]["production_contract"]["fixed_identity"]
    assert any("no arches" in item for item in precast_identity)


def test_round_surface_recipes_are_exact_variant_outputs():
    recipes = load("catalogue_round_v87_surface_recipes.json")
    assert recipes["schema"] == "surface-story-recipes@1"
    assert len(recipes["recipes"]) == 30
    assert len({item["output_key"] for item in recipes["recipes"]}) == 30
    assert all(item["output_key"].startswith("v87_") for item in recipes["recipes"])
