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
    if version >= 4:
        workflow = production.get("stage_workflow") or {}
        required_stages = [
            "reference_sufficiency",
            "representation_selection",
            "clay_massing",
            "roof_and_voids",
            "medium_detail",
            "retopology",
            "manual_uv_audit",
            "material_bake",
            "export_parity",
            "architect_review",
        ]
        declared = workflow.get("required_stages") or {}
        missing = [
            stage for stage in required_stages
            if not isinstance(declared.get(stage), dict)
            or not declared[stage].get("deliverable")
            or not declared[stage].get("approval_required")
        ]
        gates.append(_gate(
            "mandatory_stage_workflow",
            not missing,
            "missing mandatory stage declarations: " + ", ".join(missing)
            if missing else f"{len(required_stages)} mandatory production stages declared",
        ))
        views = {str(value) for value in workflow.get("architect_review_views") or []}
        required_views = {"street", "oblique", "roof", "side", "rear", "close_up"}
        gates.append(_gate(
            "architect_review_view_set",
            required_views.issubset(views),
            "missing architect views: " + ", ".join(sorted(required_views - views))
            if required_views - views else "complete six-view architect review declared",
        ))
        threshold = int(workflow.get("architect_release_score", 0))
        gates.append(_gate(
            "architect_release_threshold",
            threshold >= 85,
            f"architect release threshold is {threshold}/100; minimum 85",
        ))
        gates.append(_gate(
            "architect_hard_stops",
            bool(workflow.get("hard_stops_block_release")),
            "architectural hard stops block release"
            if workflow.get("hard_stops_block_release") else
                "architectural hard stops do not block release",
        ))
        representation = str(workflow.get("representation") or "")
        if representation in {"skin_driven_2_5d", "registered_sticker_landmark"}:
            placement = production.get("placement_contract") or {}
            footprint = placement.get("footprint_m") or {}
            fixed_landmark = (
                placement.get("mode") == "fixed_landmark"
                and placement.get("ui_interaction") == "select_and_place"
                and float(footprint.get("width", 0.0)) > 0.0
                and float(footprint.get("depth", 0.0)) > 0.0
                and placement.get("non_uniform_scale") == "forbidden"
                and placement.get("floor_count_change") == "forbidden"
                and placement.get("polygon_fit") is False
            )
            gates.append(_gate(
                "registered_sticker_fixed_placement",
                fixed_landmark,
                (
                    f"fixed {float(footprint.get('width', 0.0)):.2f} x "
                    f"{float(footprint.get('depth', 0.0)):.2f} m select-and-place landmark; "
                    "polygon fitting, floor changes and non-uniform scaling forbidden"
                    if fixed_landmark else
                    "registered sticker building lacks a safe fixed-landmark placement contract"
                ),
            ))
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

    surface_finish = production.get("surface_finish") or {}
    if surface_finish:
        required_baked_materials = [
            str(value) for value in surface_finish.get("required_baked_materials") or []
        ]
        material_roles = {
            str(key): str(value).strip()
            for key, value in (surface_finish.get("material_roles") or {}).items()
        }
        missing_material_roles = [
            material_id for material_id in required_baked_materials
            if not material_roles.get(material_id)
        ]
        gates.append(_gate(
            "surface_material_roles",
            bool(required_baked_materials) and not missing_material_roles,
            "missing construction roles: " + ", ".join(missing_material_roles)
            if missing_material_roles else
            "declared construction roles: " + ", ".join(
                f"{material_id}={material_roles[material_id]}"
                for material_id in required_baked_materials
            ),
        ))
        uv_contract = surface_finish.get("uv_contract") or {}
        minimum_tile = float(uv_contract.get("minimum_tile_metres", 0.01))
        maximum_tile = float(uv_contract.get("maximum_tile_metres", float("inf")))
        for material_id in required_baked_materials:
            spec = material_spec(grammar, str(material_id))
            tile_metres = float(spec.get("texture_tile_metres", 0.0))
            gates.extend([
                _gate(
                    f"surface_baked_pbr:{material_id}",
                    spec.get("baked_pbr") is True,
                    f"{material_id} baked_pbr is {spec.get('baked_pbr')!r}",
                ),
                _gate(
                    f"surface_uv_scale:{material_id}",
                    minimum_tile <= tile_metres <= maximum_tile,
                    f"{material_id} tiles every {tile_metres:.2f} m; required {minimum_tile:.2f}-{maximum_tile:.2f} m",
                ),
            ])
        channels = {str(value) for value in surface_finish.get("required_channels") or []}
        expected_channels = {"albedo", "roughness", "normal"}
        gates.append(_gate(
            "surface_finish_channels",
            expected_channels.issubset(channels),
            f"declared channels: {', '.join(sorted(channels)) or 'none'}",
        ))
        weathering = list(surface_finish.get("semantic_weathering") or [])
        gates.append(_gate(
            "surface_semantic_weathering",
            len(weathering) >= 3,
            f"{len(weathering)} location-specific weathering rules declared",
        ))
        qa_renders = {str(value) for value in surface_finish.get("qa_renders") or []}
        required_qa = {"neutral_source", "neutral_glb_roundtrip", "archetype_match"}
        gates.append(_gate(
            "surface_qa_renders",
            required_qa.issubset(qa_renders),
            f"declared QA renders: {', '.join(sorted(qa_renders)) or 'none'}",
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
        registration = image_lock.get("surface_registration") or {}
        if registration:
            group = str(registration.get("group") or "")
            frame = registration.get("frame") or {}
            tolerance = float(registration.get("tolerance_uv", 1e-6))
            frame_width = float(frame.get("width_m", 0.0))
            frame_height = float(frame.get("height_m", 0.0))
            frame_centre_x = float(frame.get("centre_x_m", 0.0))
            frame_base_z = float(frame.get("base_z_m", 0.0))
            frame_u_min = float(frame.get("uv_u_min", 0.0))
            frame_u_max = float(frame.get("uv_u_max", 1.0))
            frame_v_min = float(frame.get("uv_v_min", 0.0))
            frame_v_max = float(frame.get("uv_v_max", 1.0))
            registered = [
                item for item in assemblies.values()
                if str(item.get("registration_group") or "") == group
            ]
            misregistered: list[str] = []
            valid_frame = bool(group) and frame_width > 0.0 and frame_height > 0.0
            if valid_frame:
                frame_left = frame_centre_x - frame_width / 2
                for item in registered:
                    cx, _cy, cz = (float(value) for value in item.get("centre", [0, 0, 0]))
                    span = float(item.get("span_m", 0.0))
                    height = float(item.get("height_m", 0.0))
                    expected = (
                        frame_u_min + ((cx - span / 2) - frame_left) / frame_width * (frame_u_max - frame_u_min),
                        frame_u_min + ((cx + span / 2) - frame_left) / frame_width * (frame_u_max - frame_u_min),
                        frame_v_min + ((cz - height / 2) - frame_base_z) / frame_height * (frame_v_max - frame_v_min),
                        frame_v_min + ((cz + height / 2) - frame_base_z) / frame_height * (frame_v_max - frame_v_min),
                    )
                    actual = (
                        float(item.get("uv_u_min", 0.0)),
                        float(item.get("uv_u_max", 1.0)),
                        float(item.get("uv_v_min", 0.0)),
                        float(item.get("uv_v_max", 1.0)),
                    )
                    if any(abs(left - right) > tolerance for left, right in zip(actual, expected)):
                        misregistered.append(str(item.get("id")))
            anchors = {str(value) for value in registration.get("anchor_types") or []}
            required_anchors = {"window_centres", "column_centres", "floor_datums"}
            passed = (
                valid_frame
                and len(registered) >= 2
                and not misregistered
                and required_anchors.issubset(anchors)
            )
            gates.append(_gate(
                "image_lock_surface_registration",
                passed,
                f"{len(registered)} surfaces share {group!r}; "
                f"misregistered: {', '.join(misregistered) if misregistered else 'none'}; "
                f"anchors: {', '.join(sorted(anchors)) or 'none'}",
            ))
            missing_masks = [
                str(item.get("id")) for item in registered
                if (
                    item.get("mask_semantics") == "alpha_isolated_projected_feature"
                    and not item.get("alpha_mask_path")
                )
                or item.get("mask_semantics") not in {
                    "continuous_registration_base",
                    "alpha_isolated_projected_feature",
                }
            ]
            base_masks = [
                item for item in registered
                if item.get("mask_semantics") == "continuous_registration_base"
            ]
            gates.append(_gate(
                "image_lock_semantic_sticker_masks",
                len(base_masks) == 1 and not missing_masks,
                f"{len(registered)} registered surfaces; {len(base_masks)} continuous base; "
                f"missing semantic masks: {', '.join(missing_masks) if missing_masks else 'none'}",
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
