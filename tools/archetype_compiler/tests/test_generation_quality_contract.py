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


def test_material_assembly_bindings_can_target_named_subsets_of_one_kind():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    contract = grammar["architectural_signature"]["production_contract"]["material_continuity"]
    contract["assembly_bindings"] = [
        {
            "kind": "striped_turret_array", "ids": ["stone_turrets"],
            "slots": {"body_material": "signature_stone", "roof_material": "roof"},
        },
        {
            "kind": "striped_turret_array", "ids": ["brick_turrets"],
            "slots": {"body_material": "primary", "roof_material": "roof"},
        },
    ]
    grammar["massing_graph"]["assemblies"][0]["id"] = "stone_turrets"
    grammar["massing_graph"]["assemblies"].append({
        "id": "brick_turrets", "kind": "striped_turret_array",
        "body_material": "primary", "roof_material": "roof",
    })
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert report["status"] == "pass"

    grammar["massing_graph"]["assemblies"][-1]["body_material"] = "signature_stone"
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert any(not gate["passed"] and "brick_turrets" in gate["detail"] for gate in report["gates"])


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


def test_image_lock_requires_measured_reference_roles_and_named_graph_topology():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    production = grammar["architectural_signature"]["production_contract"]
    production["image_lock"] = {
        "required_reference_roles": ["street_identity", "roof_plan"],
        "minimum_measurements": 2,
        "measurements": [
            {"feature": "front bay count", "role": "street_identity", "value": 5, "unit": "count", "drives": "opening schedule"},
            {"feature": "ridge axis", "role": "roof_plan", "value": 90, "unit": "degrees", "drives": "roof node"},
        ],
        "required_node_ids": ["gate_tower"],
        "required_assembly_ids": ["gate_portal"],
        "required_node_kinds": {"pointed_passage_block": 1},
        "required_assembly_kinds": {"pointed_portal": 1},
    }
    grammar["massing_graph"]["reference_views"] = [
        {"role": "street_identity", "path": "street.png"},
        {"role": "roof_plan", "path": "roof.png"},
    ]
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert report["status"] == "pass"

    grammar["massing_graph"]["assemblies"][1]["id"] = "wrong_portal"
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "image_lock_assembly_topology" in {item["id"] for item in report["failures"]}


def test_image_lock_rejects_untraceable_measurement():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    grammar["architectural_signature"]["production_contract"]["image_lock"] = {
        "required_reference_roles": ["street_identity"],
        "minimum_measurements": 1,
        "measurements": [{
            "feature": "gable height", "role": "missing_view", "value": 5.2,
            "unit": "metres", "drives": "front gable",
        }],
        "required_node_ids": ["gate_tower"],
    }
    grammar["massing_graph"]["reference_views"] = [
        {"role": "street_identity", "path": "street.png"},
    ]
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "image_lock_measurements" in {item["id"] for item in report["failures"]}


def test_surface_finish_requires_baked_pbr_metric_uvs_and_parity_renders():
    from generation_quality_contract import assess_generation_quality_contract

    grammar = quality_grammar()
    grammar["materials"]["primary"].update({
        "baked_pbr": True,
        "texture_tile_metres": 4.0,
    })
    production = grammar["architectural_signature"]["production_contract"]
    production["quality_contract_version"] = 3
    production["surface_finish"] = {
        "required_baked_materials": ["primary"],
        "material_roles": {"primary": "coursed_wall_stone"},
        "required_channels": ["albedo", "roughness", "normal"],
        "uv_contract": {"minimum_tile_metres": 3.0, "maximum_tile_metres": 8.0},
        "semantic_weathering": ["grade patina", "roof oxidation", "protected cornice"],
        "qa_renders": ["neutral_source", "neutral_glb_roundtrip", "archetype_match"],
    }

    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert report["status"] == "pass"
    assert any(gate["id"] == "surface_uv_scale:primary" and gate["passed"] for gate in report["gates"])

    production["surface_finish"]["material_roles"] = {}
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    assert "surface_material_roles" in {item["id"] for item in report["failures"]}

    production["surface_finish"]["material_roles"] = {"primary": "coursed_wall_stone"}
    grammar["materials"]["primary"]["baked_pbr"] = False
    grammar["materials"]["primary"]["texture_tile_metres"] = 18.0
    production["surface_finish"]["qa_renders"] = ["archetype_match"]
    report = assess_generation_quality_contract(grammar, source=source_metadata())
    failures = {item["id"] for item in report["failures"]}
    assert "surface_baked_pbr:primary" in failures
    assert "surface_uv_scale:primary" in failures
    assert "surface_qa_renders" in failures
