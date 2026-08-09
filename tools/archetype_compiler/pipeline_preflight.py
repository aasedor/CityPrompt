"""Cheap production preflight for reference-locked building generation.

The preflight runs after catalogue export and signature injection, but before
facade-image generation or Blender.  It prevents the expensive stages from
starting when a variant, reference set, identity strategy, or canonical
massing contract is still ambiguous.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generation_quality_contract import assess_generation_quality_contract


SUPPORTED_SCHEMA = "building-generation-preflight@1"
IDENTITY_MODES = {"massing_graph", "semantic_stack"}
REQUIRED_REFERENCE_ROLES = {"street_identity", "oblique_massing", "roof_or_aerial"}


def _gate(gate_id: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"id": gate_id, "passed": bool(passed), "detail": detail}


def _selected_variant_index(source: dict[str, Any]) -> int | None:
    selected = source.get("selectedVariant") or {}
    selected_id = selected.get("id")
    if not selected_id:
        return None
    for index, variant in enumerate(source.get("variants") or []):
        if variant.get("id") == selected_id:
            return index
    return None


def _reference_views(source: dict[str, Any], grammar: dict[str, Any]) -> list[dict[str, Any]]:
    views = list(source.get("referenceViews") or [])
    graph = grammar.get("massing_graph") or {}
    known_paths = {str(view.get("path")) for view in views}
    for view in graph.get("reference_views") or []:
        path = str(view.get("path"))
        if path not in known_paths:
            views.append(view)
            known_paths.add(path)
    return views


def assess_generation_preflight(
    source: dict[str, Any],
    grammar: dict[str, Any],
) -> dict[str, Any]:
    """Return a strict, API-free assessment of one compiled family."""

    variants = list(source.get("variants") or [])
    selected = source.get("selectedVariant") or {}
    selected_id = selected.get("id")
    selected_index = _selected_variant_index(source)
    generation = (source.get("generationStyleInput") or {}).get("archetypeId")
    expected_generation = (
        f"{source.get('archetypeId')}_variant_{selected_index}"
        if selected_index is not None
        else None
    )
    grammar_source = grammar.get("source") or {}
    references = _reference_views(source, grammar)
    reference_roles = {str(view.get("role")) for view in references}
    signature = grammar.get("architectural_signature") or {}
    contract = signature.get("production_contract") or {}
    identity_mode = contract.get("identity_mode")
    fixed_identity = list(contract.get("fixed_identity") or [])
    repeatable_capacity = list(contract.get("repeatable_capacity") or [])
    graph = grammar.get("massing_graph") or {}
    graph_reference = graph.get("reference_dimensions") or {}
    dimensions = grammar.get("dimensions") or {}

    hard = [
        _gate(
            "variant_not_selected",
            not variants or bool(selected_id),
            f"selected variant {selected_id!r}"
            if selected_id
            else f"catalogue exposes {len(variants)} variants but none is selected",
        ),
        _gate(
            "variant_generation_provenance_mismatch",
            not selected_id or generation == expected_generation,
            f"generation id {generation!r}; expected {expected_generation!r}",
        ),
        _gate(
            "grammar_variant_mismatch",
            not selected_id or grammar_source.get("variant_id") == selected_id,
            f"grammar variant {grammar_source.get('variant_id')!r}; selected {selected_id!r}",
        ),
        _gate(
            "incomplete_reference_set",
            REQUIRED_REFERENCE_ROLES <= reference_roles,
            "missing roles: " + ", ".join(sorted(REQUIRED_REFERENCE_ROLES - reference_roles))
            if REQUIRED_REFERENCE_ROLES - reference_roles
            else f"{len(references)} compatible reference views",
        ),
        _gate(
            "missing_production_contract",
            bool(contract),
            "architectural signature declares a production contract"
            if contract
            else "no production_contract on the resolved architectural signature",
        ),
        _gate(
            "unclassified_identity_mode",
            identity_mode in IDENTITY_MODES,
            f"identity mode {identity_mode!r}; expected one of {sorted(IDENTITY_MODES)}",
        ),
        _gate(
            "missing_fixed_identity",
            len(fixed_identity) >= 3,
            f"{len(fixed_identity)} fixed identity assemblies; minimum 3",
        ),
        _gate(
            "missing_repeatable_capacity",
            bool(repeatable_capacity),
            f"{len(repeatable_capacity)} repeatable capacity assemblies",
        ),
        _gate(
            "missing_required_massing_graph",
            identity_mode != "massing_graph" or bool(graph.get("profile")),
            f"massing profile {graph.get('profile')!r}"
            if graph.get("profile")
            else "massing_graph identity selected without a graph profile",
        ),
    ]

    if identity_mode == "massing_graph" and graph_reference:
        mismatches: list[str] = []
        for graph_key, grammar_key in (
            ("width_m", "width_m"),
            ("depth_m", "depth_m"),
            ("floors", "default_floors"),
        ):
            expected = graph_reference.get(graph_key)
            actual = dimensions.get(grammar_key)
            if expected is not None and actual != expected:
                mismatches.append(f"{grammar_key}={actual!r} expected {expected!r}")
        hard.append(
            _gate(
                "massing_reference_dimensions_mismatch",
                not mismatches,
                "; ".join(mismatches) if mismatches else "canonical graph dimensions activate exactly",
            )
        )

    quality = assess_generation_quality_contract(grammar, source=source)
    hard.extend(quality["gates"])

    failures = [gate for gate in hard if not gate["passed"]]
    status = "fail" if failures else "pass"
    return {
        "schema": SUPPORTED_SCHEMA,
        "archetype_id": source.get("archetypeId"),
        "variant_id": selected_id,
        "family": grammar.get("family_id"),
        "status": status,
        "paid_generation_allowed": status == "pass",
        "reference_views": references,
        "identity_mode": identity_mode,
        "generation_quality": quality,
        "failures": failures,
        "gates": hard,
    }


def assess_paths(source_path: Path, grammar_path: Path) -> dict[str, Any]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    return assess_generation_preflight(source, grammar)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--grammar", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = assess_paths(args.source, args.grammar)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
