"""Executable image-lock, material-continuity and spatial-void contracts.

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
    image_lock = production.get("image_lock") or {}
    if image_lock:
        reference_roles = {
            str(view.get("role")) for view in graph.get("reference_views") or []
        }
        required_roles = {str(role) for role in image_lock.get("required_reference_roles") or []}
        missing_roles = sorted(required_roles - reference_roles)
        gates.append(_gate(
            "image_lock_reference_roles",
            bool(required_roles) and not missing_roles,
            "missing reference roles: " + ", ".join(missing_roles)
            if missing_roles else f"{len(required_roles)} image-authoritative roles declared",
        ))
        measurements = list(image_lock.get("measurements") or [])
        minimum_measurements = int(image_lock.get("minimum_measurements", 1))
        invalid_measurements = []
        for index, measurement in enumerate(measurements):
            valid = (
                isinstance(measurement, dict)
                and bool(measurement.get("feature"))
                and str(measurement.get("role")) in reference_roles
                and isinstance(measurement.get("value"), (int, float))
                and bool(measurement.get("unit"))
                and bool(measurement.get("drives"))
            )
            if not valid:
                invalid_measurements.append(index)
        gates.append(_gate(
            "image_lock_measurements",
            len(measurements) >= minimum_measurements and not invalid_measurements,
            f"{len(measurements)} measurements; minimum {minimum_measurements}; "
            f"invalid indices: {invalid_measurements or 'none'}",
        ))
        for noun, collection in (
            ("node", nodes), ("assembly", assemblies), ("void", voids),
        ):
            if f"required_{noun}_ids" not in image_lock:
                continue
            required_ids = {str(value) for value in image_lock.get(f"required_{noun}_ids") or []}
            missing_ids = sorted(required_ids - set(collection))
            gates.append(_gate(
                f"image_lock_{noun}_topology",
                bool(required_ids) and not missing_ids,
                f"missing {noun} ids: {', '.join(missing_ids)}"
                if missing_ids else f"{len(required_ids)} required {noun} ids resolved",
            ))
        for noun, items in (("node", nodes.values()), ("assembly", assemblies.values())):
            if f"required_{noun}_kinds" not in image_lock:
                continue
            counts: dict[str, int] = {}
            for item in items:
                kind = str(item.get("kind"))
                counts[kind] = counts.get(kind, 0) + 1
            required_counts = {
                str(kind): int(count)
                for kind, count in (image_lock.get(f"required_{noun}_kinds") or {}).items()
            }
            deficits = {
                kind: [counts.get(kind, 0), minimum]
                for kind, minimum in required_counts.items()
                if counts.get(kind, 0) < minimum
            }
            gates.append(_gate(
                f"image_lock_{noun}_kind_counts",
                bool(required_counts) and not deficits,
                f"kind deficits (actual, minimum): {deficits}"
                if deficits else f"{len(required_counts)} {noun} kind counts satisfied",
            ))
    for binding in material_contract.get("assembly_bindings") or []:
        kind = str(binding["kind"])
        limited_ids = {str(value) for value in binding.get("ids") or []}
        matching = [
            item for item in assemblies.values()
            if item.get("kind") == kind
            and (not limited_ids or str(item.get("id")) in limited_ids)
        ]
        expected = dict(binding.get("slots") or {})
        incorrect = [
            str(item.get("id"))
            for item in matching
            if any(item.get(slot) != material_id for slot, material_id in expected.items())
        ]
        gates.append(_gate(
            f"material_assembly_binding:{kind}"
            + (f":{','.join(sorted(limited_ids))}" if limited_ids else ""),
            bool(matching) and not incorrect,
            f"{len(matching)} assemblies checked; incorrect: {', '.join(incorrect) if incorrect else 'none'}",
        ))
    for binding in material_contract.get("node_bindings") or []:
        kind = str(binding["kind"])
        limited_ids = {str(value) for value in binding.get("ids") or []}
        matching = [
            item for item in nodes.values()
            if item.get("kind") == kind
            and (not limited_ids or str(item.get("id")) in limited_ids)
        ]
        expected = dict(binding.get("slots") or {})
        incorrect = [
            str(item.get("id"))
            for item in matching
            if any(item.get(slot) != material_id for slot, material_id in expected.items())
        ]
        gates.append(_gate(
            f"material_node_binding:{kind}",
            bool(matching) and not incorrect,
            f"{len(matching)} nodes checked; incorrect: {', '.join(incorrect) if incorrect else 'none'}",
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
        expected_target_kind = str(passage.get("target_node_kind", "pointed_passage_block"))
        expected_section_mode = str(passage.get("section_mode", "through"))
        minimum_openings = int(passage.get("minimum_opening_count", 1))
        target_openings = int(target.get("opening_count", 1))
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
                target.get("kind") == expected_target_kind
                and str(target.get("section_mode", "through")) == expected_section_mode
                and target_openings >= minimum_openings,
                f"target node kind {target.get('kind')!r}; mode {target.get('section_mode', 'through')!r}; openings {target_openings}",
            ),
            _gate(
                f"passage_skin_clearance:{passage_id}",
                len(clearances) >= int(passage.get("minimum_clearance_count", minimum_openings)),
                f"{len(clearances)} facade-skin clearances reference the passage",
            ),
        ])
        if passage.get("portal_assembly_id"):
            gates.append(_gate(
                f"passage_portal:{passage_id}",
                portal.get("kind") == "pointed_portal"
                and portal.get("opening_mode") == "through_passage"
                and portal.get("passage_void_id") == passage_id,
                f"portal {portal.get('id')!r} mode {portal.get('opening_mode')!r}",
            ))

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
