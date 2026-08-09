"""Regression tests for landmark skins and executable passage contracts."""
from __future__ import annotations

from copy import deepcopy


def quality_grammar() -> dict:
    return {
        "materials": {
            "primary": {"texture_key": "granite"},
            "secondary": {"texture_key": "granite"},
            "roof": {"texture_key": "welsh_slate"},
        },
        "architectural_signature": {
            "signature_material_overrides": {"signature_stone": {"texture_key": "granite"}},
            "production_contract": {
                "quality_contract_version": 2,
                "metadata_cues": ["pink-grey granite", "natural slate", "deeply recessed"],
                "material_continuity": {
                    "required_textured_materials": ["primary", "secondary", "signature_stone", "roof"],
                    "required_material_matches": {"signature_stone": "primary"},
                    "assembly_bindings": [{
                        "kind": "striped_turret_array",
                        "slots": {"body_material": "signature_stone", "roof_material": "roof"},
                    }],
                },
                "spatial_voids": {
                    "required_passages": [{
                        "void_id": "gate_passage",
                        "target_node_id": "gate_tower",
                        "portal_assembly_id": "gate_portal",
                        "shape": "pointed_arch_passage",
                        "minimum_depth_m": 6.0,
                    }],
                },
            },
        },
        "massing_graph": {
            "nodes": [{"id": "gate_tower", "kind": "pointed_passage_block"}],
            "voids": [{
                "id": "gate_passage", "shape": "pointed_arch_passage", "axis": "front",
                "size": [4.8, 8.8, 8.0],
            }],
            "assemblies": [
                {
                    "id": "corner_turrets", "kind": "striped_turret_array",
                    "body_material": "signature_stone", "roof_material": "roof",
                },
                {
                    "id": "gate_portal", "kind": "pointed_portal",
                    "opening_mode": "through_passage", "passage_void_id": "gate_passage",
                },
                {
                    "id": "gate_skin", "kind": "facade_skin",
                    "opening_clearances": [{"void_id": "gate_passage"}],
                },
            ],
        },
    }


def source_metadata() -> dict:
    return {
        "description": "Pink-grey granite tower with a deeply recessed porte-cochere.",
        "roofDetail": {"material": "Dark grey natural slate."},
    }


def test_material_and_spatial_contract_passes_when_every_surface_and_void_is_executable():
    from generation_quality_contract import assess_generation_quality_contract

    report = assess_generation_quality_contract(
        quality_grammar(), source=source_metadata(), texture_available=lambda key: key in {"granite", "welsh_slate"},
    )
    assert report["status"] == "pass"
    assert all(gate["passed"] for gate in report["gates"])


def test_flat_landmark_material_and_missing_runtime_skin_fail():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    grammar["architectural_signature"]["signature_material_overrides"]["signature_stone"]["texture_key"] = None
    report = assess_generation_quality_contract(
        grammar, source=source_metadata(), texture_available=lambda key: key != "welsh_slate",
    )
    failures = {item["id"] for item in report["failures"]}
    assert "material_texture_key:signature_stone" in failures
    assert "material_texture_available:roof" in failures


def test_decorative_portal_cannot_satisfy_a_declared_passage():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = deepcopy(quality_grammar())
    portal = grammar["massing_graph"]["assemblies"][1]
    portal["opening_mode"] = "recessed_back_plane"
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "passage_portal:gate_passage" in {item["id"] for item in report["failures"]}


def test_unpunched_facade_skin_cannot_cover_a_declared_passage():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = deepcopy(quality_grammar())
    grammar["massing_graph"]["assemblies"][2].pop("opening_clearances")
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "passage_skin_clearance:gate_passage" in {item["id"] for item in report["failures"]}


def test_multi_arch_recess_requires_every_opening_and_skin_clearance():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    passage = grammar["architectural_signature"]["production_contract"]["spatial_voids"]["required_passages"][0]
    passage.update({
        "target_node_kind": "opening_block",
        "shape": "round_arch_passage",
        "section_mode": "recessed",
        "minimum_opening_count": 5,
        "minimum_clearance_count": 5,
        "minimum_depth_m": 2.5,
    })
    passage.pop("portal_assembly_id")
    graph = grammar["massing_graph"]
    graph["nodes"][0].update({
        "kind": "opening_block", "section_mode": "recessed", "opening_count": 5,
    })
    graph["voids"][0].update({"shape": "round_arch_passage", "size": [18.0, 2.8, 4.8]})
    graph["assemblies"] = [
        graph["assemblies"][0],
        {
            "id": "arcade_skin", "kind": "facade_skin",
            "opening_clearances": [{"void_id": "gate_passage"} for _ in range(5)],
        },
    ]

    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert report["status"] == "pass"

    graph["assemblies"][1]["opening_clearances"] = graph["assemblies"][1]["opening_clearances"][:4]
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "passage_skin_clearance:gate_passage" in {item["id"] for item in report["failures"]}
