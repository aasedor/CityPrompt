"""Compile learned geometry evidence into a reviewed architectural graph patch.

The learned output never becomes catalogue geometry. This module joins visible
depth/normal evidence to the gold-set fixed-identity rules, validates every
operation's provenance, and applies only explicitly reviewed graph operations.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


SCHEMA = "architectural-interpretation@1"


def _merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _patch_named(items: list[dict], patches: dict[str, dict], collection: str) -> list[dict]:
    result: list[dict] = []
    found: set[str] = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id in patches:
            item = _merge(item, patches[item_id])
            found.add(item_id)
        result.append(item)
    missing = set(patches) - found
    if missing:
        raise KeyError(f"Architectural evidence patches missing {collection} ids: {sorted(missing)}")
    return result


def _scale_y(graph: dict, factor: float) -> None:
    if not 0.75 <= factor <= 1.75:
        raise ValueError(f"Refusing unsafe plan-axis scale factor {factor}")
    for collection in ("nodes", "voids"):
        for item in graph.get(collection, []):
            if "location" in item:
                item["location"][1] = round(float(item["location"][1]) * factor, 5)
            if "size" in item:
                item["size"][1] = round(float(item["size"][1]) * factor, 5)
    for item in graph.get("assemblies", []):
        if "centre" in item:
            item["centre"][1] = round(float(item["centre"][1]) * factor, 5)
        if "base_centre" in item:
            item["base_centre"][1] = round(float(item["base_centre"][1]) * factor, 5)
        if "centres" in item:
            for centre in item["centres"]:
                centre[1] = round(float(centre[1]) * factor, 5)
        if "recess_plane_y" in item:
            item["recess_plane_y"] = round(float(item["recess_plane_y"]) * factor, 5)
        if item.get("axis") in {"left", "right"} and "span_m" in item:
            item["span_m"] = round(float(item["span_m"]) * factor, 5)


def _gold_rules(memory: dict, requested: list[str]) -> list[dict[str, str]]:
    available = {rule["id"]: rule["rule"] for rule in memory.get("non_negotiable_principles", [])}
    missing = set(requested) - set(available)
    if missing:
        raise KeyError(f"Architectural profile references unknown gold-memory rules: {sorted(missing)}")
    return [{"id": rule_id, "rule": available[rule_id]} for rule_id in requested]


def compile_interpretation(
    grammar: dict,
    geometry_evidence: dict,
    profile: dict,
    quality_memory: dict,
    *,
    apply: bool = True,
) -> tuple[dict[str, Any], dict]:
    source = grammar.get("source", {})
    if source.get("archetype_id") != profile["archetype_id"]:
        raise ValueError("Architectural evidence archetype does not match the compiled grammar")
    if source.get("variant_id") != profile["variant_id"]:
        raise ValueError("Architectural evidence variant does not match the compiled grammar")
    graph = grammar.get("massing_graph") or {}
    if graph.get("profile") != profile["base_graph"]:
        raise ValueError(f"Expected base graph {profile['base_graph']!r}, got {graph.get('profile')!r}")
    if geometry_evidence.get("schema") != "archetype-geometry-evidence@1":
        raise ValueError("Learned geometry must use archetype-geometry-evidence@1")
    if geometry_evidence.get("scope") != "one_archetype_bounded_pilot":
        raise ValueError("Only bounded one-archetype evidence may drive this compiler")

    operations = profile.get("operations", [])
    for operation in operations:
        if not operation.get("evidence") or not operation.get("rationale"):
            raise ValueError(f"Operation {operation.get('id')} lacks traceable evidence or rationale")

    thresholds = profile.get("review_thresholds", {})
    coverage = float(geometry_evidence.get("street_geometry", {}).get("valid_coverage", 0.0))
    disagreement = float(
        geometry_evidence.get("street_geometry", {}).get("cross_model_disagreement", {}).get("median_ratio", 1.0)
    )
    roof_confidence = float(geometry_evidence.get("roof_geometry", {}).get("confidence", {}).get("median", 0.0))
    gate_results = {
        "valid_coverage": coverage >= float(thresholds.get("valid_coverage_min", 0.88)),
        "cross_model_median_disagreement": disagreement <= float(
            thresholds.get("cross_model_median_disagreement_max", 0.06)
        ),
        "roof_confidence_median": roof_confidence >= float(thresholds.get("roof_confidence_median_min", 1.25)),
    }
    safe_visible_evidence = all(gate_results.values())
    human_reviewed = profile.get("human_review_decision") == "apply_shared_visible_constraints_only"
    decision = "apply_reviewed_constraints" if safe_visible_evidence and human_reviewed else "withhold_patch"
    result_grammar = deepcopy(grammar)

    if apply and decision == "apply_reviewed_constraints":
        target = result_grammar["massing_graph"]
        for operation in operations:
            kind = operation["kind"]
            if kind == "scale_plan_axis":
                if operation.get("axis") != "y":
                    raise ValueError("v1 architectural evidence compiler supports only the plan Y axis")
                _scale_y(target, float(operation["factor"]))
            elif kind == "patch_graph_items":
                for collection, patches in operation.get("patches", {}).items():
                    if collection not in {"nodes", "voids", "assemblies"}:
                        raise ValueError(f"Unsupported graph patch collection {collection!r}")
                    target[collection] = _patch_named(target.get(collection, []), patches, collection)
            elif kind == "add_graph_assemblies":
                existing = {item.get("id") for item in target.get("assemblies", [])}
                additions = deepcopy(operation.get("assemblies", []))
                duplicate = existing & {item.get("id") for item in additions}
                if duplicate:
                    raise ValueError(f"Architectural evidence would duplicate assemblies: {sorted(duplicate)}")
                target.setdefault("assemblies", []).extend(additions)
            else:
                raise ValueError(f"Unsupported architectural evidence operation {kind!r}")

        dimensions = profile["target_dimensions_m"]
        result_grammar["dimensions"]["width_m"] = float(dimensions["width"])
        result_grammar["dimensions"]["depth_m"] = float(dimensions["depth"])
        target["height_m"] = float(dimensions["height"])
        target["reference_dimensions"]["width_m"] = float(dimensions["width"])
        target["reference_dimensions"]["depth_m"] = float(dimensions["depth"])
        target["profile"] = profile["output_graph"]
        target["description"] = (
            "Gold-set fixed-identity grammar refined by reviewed MoGe-2/DA3 visible constraints; "
            "learned proxy geometry is explicitly excluded from the catalogue asset."
        )

    interpretation: dict[str, Any] = {
        "schema": SCHEMA,
        "id": profile["output_graph"],
        "status": "review" if decision == "apply_reviewed_constraints" else "withheld",
        "decision": decision,
        "identity_mode": profile["identity_mode"],
        "source": {
            "archetype_id": profile["archetype_id"],
            "variant_id": profile["variant_id"],
            "base_graph": profile["base_graph"],
            "geometry_evidence_id": geometry_evidence.get("id"),
            "geometry_evidence_status": geometry_evidence.get("status"),
        },
        "fixed_identity": profile["fixed_identity"],
        "repeatable_capacity": profile["repeatable_capacity"],
        "gold_memory_rules": _gold_rules(quality_memory, profile["gold_memory_rules"]),
        "plan_measurements": profile["plan_measurements"],
        "target_dimensions_m": profile["target_dimensions_m"],
        "operations": deepcopy(operations),
        "uncertainty": geometry_evidence.get("uncertainty", {}),
        "policy": {
            "learned_mesh_delivery": "prohibited",
            "visible_constraints": "reviewed_before_application",
            "occluded_geometry": "authored_from_architectural_rules",
            "release": "review_only_until_multiscale_visual_approval",
        },
        "gates": {
            "safe_visible_evidence": safe_visible_evidence,
            "human_reviewed": human_reviewed,
            "every_operation_traceable": all(op.get("evidence") and op.get("rationale") for op in operations),
            "profile_thresholds": thresholds,
            "profile_gate_results": gate_results,
        },
    }
    return interpretation, result_grammar
