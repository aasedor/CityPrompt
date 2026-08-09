"""Executable material-continuity and spatial-void quality contracts.

Catalogue prose supplies the architectural evidence, while a resolved
signature profile maps that evidence to named graph materials and passages.
The same contract is checked before generation and again against the texture
library selected by Blender.
"""
from __future__ import annotations

from typing import Any, Callable


def _gate(gate_id: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"id": gate_id, "passed": bool(passed), "detail": detail}


def _source_text(source: dict[str, Any] | None) -> str:
    if not source:
        return ""
    values: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    for key in ("description", "facadeDetail", "roofDetail", "styleProfile", "prompt"):
        collect(source.get(key))
    return " ".join(values).lower()


def material_spec(grammar: dict[str, Any], material_id: str) -> dict[str, Any]:
    materials = grammar.get("materials") or {}
    if material_id in materials:
        return dict(materials[material_id] or {})
    signature = grammar.get("architectural_signature") or {}
    overrides = signature.get("signature_material_overrides") or {}
    return dict(overrides.get(material_id) or {})


def assess_generation_quality_contract(
    grammar: dict[str, Any],
    *,
    source: dict[str, Any] | None = None,
    texture_available: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    signature = grammar.get("architectural_signature") or {}
    production = signature.get("production_contract") or {}
    version = int(production.get("quality_contract_version") or 0)
    if version < 2:
        return {"schema": "building-generation-quality@1", "status": "not_declared", "gates": []}

    gates: list[dict[str, Any]] = []
    material_contract = production.get("material_continuity") or {}
    required_materials = list(material_contract.get("required_textured_materials") or [])
    for material_id in required_materials:
        spec = material_spec(grammar, str(material_id))
        texture_key = spec.get("texture_key")
        gates.append(_gate(
            f"material_texture_key:{material_id}",
            bool(texture_key),
            f"{material_id} resolves to texture {texture_key!r}",
        ))
        if texture_key and texture_available is not None:
            gates.append(_gate(
                f"material_texture_available:{material_id}",
                texture_available(str(texture_key)),
                f"texture set {texture_key!r} is available to the selected Blender library",
            ))
    for landmark_id, reference_id in (material_contract.get("required_material_matches") or {}).items():
        landmark_key = material_spec(grammar, str(landmark_id)).get("texture_key")
        reference_key = material_spec(grammar, str(reference_id)).get("texture_key")
        gates.append(_gate(
            f"material_family_match:{landmark_id}",
            bool(landmark_key) and landmark_key == reference_key,
            f"{landmark_id} texture {landmark_key!r}; {reference_id} texture {reference_key!r}",
        ))

    graph = grammar.get("massing_graph") or {}
    nodes = {str(item.get("id")): item for item in graph.get("nodes") or []}
    voids = {str(item.get("id")): item for item in graph.get("voids") or []}
    assemblies = {str(item.get("id")): item for item in graph.get("assemblies") or []}
    for binding in material_contract.get("assembly_bindings") or []:
        kind = str(binding["kind"])
        matching = [item for item in assemblies.values() if item.get("kind") == kind]
        expected = dict(binding.get("slots") or {})
        incorrect = [
            str(item.get("id"))
            for item in matching
            if any(item.get(slot) != material_id for slot, material_id in expected.items())
        ]
        gates.append(_gate(
            f"material_assembly_binding:{kind}",
            bool(matching) and not incorrect,
            f"{len(matching)} assemblies checked; incorrect: {', '.join(incorrect) if incorrect else 'none'}",
        ))
    for passage in (production.get("spatial_voids") or {}).get("required_passages") or []:
        passage_id = str(passage["void_id"])
        void = voids.get(passage_id) or {}
        target = nodes.get(str(passage.get("target_node_id"))) or {}
        portal = assemblies.get(str(passage.get("portal_assembly_id"))) or {}
        minimum_depth = float(passage.get("minimum_depth_m", 1.5))
        axis = str(void.get("axis", "front"))
        size = list(void.get("size") or [0.0, 0.0, 0.0])
        depth_index = 1 if axis in {"front", "rear"} else 0
        actual_depth = float(size[depth_index]) if len(size) > depth_index else 0.0
        clearances = [
            clearance
            for assembly in assemblies.values()
            if assembly.get("kind") == "facade_skin"
            for clearance in assembly.get("opening_clearances") or []
            if clearance.get("void_id") == passage_id
        ]
        gates.extend([
            _gate(
                f"passage_void:{passage_id}",
                bool(void) and void.get("shape") == passage.get("shape", "pointed_arch_passage"),
                f"declared void shape {void.get('shape')!r}",
            ),
            _gate(
                f"passage_depth:{passage_id}",
                actual_depth >= minimum_depth,
                f"passage depth {actual_depth:.2f} m; minimum {minimum_depth:.2f} m",
            ),
            _gate(
                f"passage_target:{passage_id}",
                target.get("kind") == "pointed_passage_block",
                f"target node kind {target.get('kind')!r}",
            ),
            _gate(
                f"passage_portal:{passage_id}",
                portal.get("kind") == "pointed_portal"
                and portal.get("opening_mode") == "through_passage"
                and portal.get("passage_void_id") == passage_id,
                f"portal {portal.get('id')!r} mode {portal.get('opening_mode')!r}",
            ),
            _gate(
                f"passage_skin_clearance:{passage_id}",
                bool(clearances),
                f"{len(clearances)} facade-skin clearances reference the passage",
            ),
        ])

    metadata_cues = [str(cue).lower() for cue in production.get("metadata_cues") or []]
    if source is not None and metadata_cues:
        text = _source_text(source)
        missing = [cue for cue in metadata_cues if cue not in text]
        gates.append(_gate(
            "metadata_traceability",
            not missing,
            "missing catalogue cues: " + ", ".join(missing) if missing else "quality contract is traceable to catalogue metadata",
        ))

    failures = [gate for gate in gates if not gate["passed"]]
    return {
        "schema": "building-generation-quality@1",
        "status": "fail" if failures else "pass",
        "quality_contract_version": version,
        "failures": failures,
        "gates": gates,
    }
