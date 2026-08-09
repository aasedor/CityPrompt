"""Regression tests for the three genuinely new V85 pilot contracts."""
from __future__ import annotations


def _grammar(archetype: str, variant: str) -> dict:
    from signature_profiles import inject_signature

    return inject_signature({
        "source": {"archetype_id": archetype, "variant_id": variant},
        "dimensions": {},
        "materials": {
            "primary": {}, "secondary": {}, "accent": {}, "roof": {},
        },
    }, archetype, variant_id=variant)


def test_v85_profiles_are_exact_variant_image_locked_and_role_complete():
    cases = (
        ("classic_brownstone_streetwall", "classic_brownstone_traditional", "classic_brownstone_three_house_v85"),
        ("modern_glass_office_institutional", "glass_office_blue_curtainwall", "blue_curtainwall_roof_screen_v85"),
        ("nordic_timber_midrise", "nordic_timber_mass_timber", "nordic_mass_timber_terrace_v85"),
    )
    for archetype, variant, graph_profile in cases:
        grammar = _grammar(archetype, variant)
        graph = grammar["massing_graph"]
        production = grammar["architectural_signature"]["production_contract"]
        finish = production["surface_finish"]
        assert graph["profile"] == graph_profile
        assert {view["role"] for view in graph["reference_views"]} == {
            "street_identity", "oblique_massing", "roof_plan",
        }
        assert production["quality_contract_version"] == 3
        assert set(finish["required_baked_materials"]) == set(finish["material_roles"])


def test_v85_fixed_medium_detail_is_not_a_facade_only_swap():
    brownstone = _grammar("classic_brownstone_streetwall", "classic_brownstone_traditional")["massing_graph"]
    glass = _grammar("modern_glass_office_institutional", "glass_office_blue_curtainwall")["massing_graph"]
    timber = _grammar("nordic_timber_midrise", "nordic_timber_mass_timber")["massing_graph"]

    assert sum(item["kind"] == "rowhouse_stoop" for item in brownstone["assemblies"]) == 3
    assert any(item["id"] == "brownstone_cornice_brackets" for item in brownstone["assemblies"])
    assert any(node["id"] == "glass_mechanical_penthouse" for node in glass["nodes"])
    assert sum(item["id"].startswith("glass_mechanical_") for item in glass["assemblies"]) == 3
    assert not any(item["id"] == "timber_front_picture_frames" for item in timber["assemblies"])
    assert sum(item["id"].startswith("timber_roof_guard_") for item in timber["assemblies"]) == 4
