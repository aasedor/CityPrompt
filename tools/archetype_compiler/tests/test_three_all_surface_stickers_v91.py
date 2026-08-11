from collections import Counter
from copy import deepcopy
from pathlib import Path

from compile_catalogue_round_v87 import build_profile
from compile_three_all_surface_stickers_v91 import (
    TARGETS,
    customize,
    grand_magasin_draft,
    theater_draft,
    tuscan_draft,
)


def _profiles():
    drafts = (tuscan_draft(), theater_draft(), grand_magasin_draft())
    for target, draft in zip(TARGETS, drafts):
        parent, variant, index, _family, width, depth, floors = target
        profile, _recipes = build_profile(parent, variant, index, width, depth, floors, deepcopy(draft))
        profile.pop("extends", None)
        customize(variant, profile)
        yield variant, profile


def test_targets_are_three_distinct_exact_variants_not_in_previous_review_evidence():
    variants = {target[1] for target in TARGETS}
    assert variants == {
        "med_villa_tuscan",
        "deco_theater_egyptian_revival",
        "grand-magasin-belle-epoque",
    }
    repo = Path(__file__).parents[3]
    prior_review_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (repo / "docs/reviews").rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
        and path.name != "rollout-plan.json"
        and "catalogue-rollout-v91" not in path.as_posix()
    )
    assert all(variant not in prior_review_text for variant in variants)


def test_every_building_has_unique_front_left_right_rear_and_registered_roof_stickers():
    for _variant, profile in _profiles():
        assemblies = profile["massing_graph"]["assemblies"]
        facade = [item for item in assemblies if item["kind"] == "facade_skin"]
        roofs = [item for item in assemblies if item["kind"] == "roof_skin"]
        roles = Counter(item["surface_role"] for item in facade)
        assert {"front", "left", "right", "rear"}.issubset(roles)
        assert roofs
        assert all(item["surface_role"] == "roof" for item in roofs)
        assert all(item.get("source_image_path", "").endswith(".png") for item in [*facade, *roofs])
        coverage = profile["production_contract"]["sticker_method"]["all_surface_coverage"]
        assert coverage["unskinned_exposed_wall_fields_allowed"] is False
        assert coverage["unskinned_roof_fields_allowed"] is False


def test_grand_magasin_owns_all_eight_external_faces_and_uses_one_plan_frame_for_six_roof_fields():
    variant, profile = list(_profiles())[2]
    assert variant == "grand-magasin-belle-epoque"
    assemblies = profile["massing_graph"]["assemblies"]
    facade_roles = {item["surface_role"] for item in assemblies if item["kind"] == "facade_skin"}
    assert {
        "front", "front_right", "right", "rear_right",
        "rear", "rear_left", "left", "front_left",
    }.issubset(facade_roles)
    roofs = [item for item in assemblies if item["kind"] == "roof_skin"]
    assert Counter(item["shape"] for item in roofs) == {"mono_pitch": 4, "dome": 2}
    assert len({tuple(item["plan_bounds"]) for item in roofs}) == 1


def test_massing_gate_precedes_stickers_and_no_generic_glazing_overlay_survives():
    for _variant, profile in _profiles():
        production = profile["production_contract"]
        gate = production["sticker_method"]["pre_sticker_massing_gate"]
        assert gate["status"] == "pass_for_bounded_pilot"
        assert gate["blank_side_or_rear"] == "hard_stop"
        assert gate["generic_roof_substitution"] == "hard_stop"
        assemblies = profile["massing_graph"]["assemblies"]
        assert not any(item["kind"] == "glazing_overlay" for item in assemblies)


def test_public_entrances_are_real_recessed_sections():
    expected = {
        "med_villa_tuscan": ("tuscan_loggia", 3.0),
        "deco_theater_egyptian_revival": ("theater_entrance_vestibule", 4.0),
        "grand-magasin-belle-epoque": ("grand_magasin_entrance", 4.2),
    }
    for variant, profile in _profiles():
        node_id, minimum_depth = expected[variant]
        node = next(item for item in profile["massing_graph"]["nodes"] if item["id"] == node_id)
        assert node["kind"] == "opening_block"
        assert node["section_mode"] == "recessed"
        assert float(node["size"][1]) >= minimum_depth
        assert int(node["opening_count"]) == 3
        if variant != "med_villa_tuscan":
            assert node["back_material"] == "interior"
            assert node["back_glass_material"] == "glass"


def test_front_opening_blocks_align_their_outer_face_to_the_sticker_plane():
    for _variant, profile in _profiles():
        graph = profile["massing_graph"]
        front = next(item for item in graph["assemblies"] if item.get("surface_role") == "front")
        opening = next(item for item in graph["nodes"] if item.get("kind") == "opening_block")
        outer_face_y = float(opening["location"][1]) - float(opening["size"][1]) / 2.0
        assert abs(outer_face_y - float(front["centre"][1])) <= 0.15


def test_theater_auditorium_does_not_fill_the_recessed_vestibule():
    _variant, profile = list(_profiles())[1]
    graph = profile["massing_graph"]
    auditorium = next(item for item in graph["nodes"] if item["id"] == "theater_auditorium")
    vestibule = next(item for item in graph["nodes"] if item["id"] == "theater_entrance_vestibule")
    auditorium_front = auditorium["location"][1] - auditorium["size"][1] / 2.0
    vestibule_back = vestibule["location"][1] + vestibule["size"][1] / 2.0
    assert auditorium_front >= vestibule_back


def test_render_ready_stickers_are_edge_to_edge_inputs_and_roof_keeps_pbr_role():
    for _variant, profile in _profiles():
        for item in profile["massing_graph"]["assemblies"]:
            if item.get("kind") in {"facade_skin", "roof_skin"}:
                assert "render-ready-stickers" in item["source_image_path"]
        roof = profile["material_overrides"]["roof"]
        assert roof["baked_pbr"] is True
        assert roof["texture_key"].endswith("_roof")
