"""Executable quality memory for catalogue-scale 3D building generation.

The memory is deliberately separate from Blender implementation details.  It
can assess an existing manifest/report pair, and the resume-safe batch runner
uses the same function to route each family to pass, review, or fail.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from visual_approval import validate_visual_approval


TOOL_DIR = Path(__file__).resolve().parent
DEFAULT_MEMORY_PATH = TOOL_DIR / "high_quality_building_memory.json"
SUPPORTED_SCHEMA = "high-quality-building-memory@1"


class QualityMemoryError(ValueError):
    """Raised when the persistent quality-memory contract is invalid."""


def load_quality_memory(path: Path | str = DEFAULT_MEMORY_PATH) -> dict[str, Any]:
    memory_path = Path(path)
    payload = json.loads(memory_path.read_text(encoding="utf-8"))
    if payload.get("schema") != SUPPORTED_SCHEMA:
        raise QualityMemoryError(
            f"unsupported quality memory schema {payload.get('schema')!r}; "
            f"expected {SUPPORTED_SCHEMA!r}"
        )
    if not payload.get("memory_version"):
        raise QualityMemoryError("quality memory requires memory_version")
    if not payload.get("non_negotiable_principles"):
        raise QualityMemoryError("quality memory requires non_negotiable_principles")
    if not payload.get("automated_quality_gates"):
        raise QualityMemoryError("quality memory requires automated_quality_gates")
    if not payload.get("calibration_set"):
        raise QualityMemoryError("quality memory requires calibration_set")
    return payload


def _gate(gate_id: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"id": gate_id, "passed": bool(passed), "detail": detail}


def _render_roles(manifest: dict[str, Any]) -> set[str]:
    roles: set[str] = set()
    known_roles = (
        "front_corner_oblique",
        "rear_corner_oblique",
        "facade_close",
        "archetype_match",
        "preview",
        "street",
        "aerial",
        "context",
    )
    for value in manifest.get("renders") or []:
        name = Path(str(value)).stem.lower()
        for role in known_roles:
            if role in name:
                roles.add(role)
    return roles


def _fixed_contract_tokens(manifest: dict[str, Any]) -> set[str]:
    facade = manifest.get("facade_sheet") or {}
    contract = facade.get("assembly_contract") or {}
    return {str(value).lower() for value in contract.get("fixed") or []}


def assess_family_quality(
    manifest: dict[str, Any],
    report: dict[str, Any],
    memory: dict[str, Any] | None = None,
    visual_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assess one generated family without requiring Blender or image APIs.

    Hard failures are structural and block import.  Review findings represent
    fidelity gaps or legacy manifests; they keep a large batch moving while
    placing only the affected family in the human review queue.
    """

    memory = memory or load_quality_memory()
    gates = memory["automated_quality_gates"]
    modules = list(manifest.get("modules") or [])
    fixed_modules = [item for item in modules if item.get("assembly_class") == "fixed_semantic"]
    repeatable_modules = [
        item for item in modules if item.get("assembly_class") == "repeatable_middle"
    ]
    assembled = manifest.get("assembled") or {}
    footprint = manifest.get("footprint_compatibility") or {}
    preferred_profiles = list(footprint.get("preferredProfiles") or [])
    render_roles = _render_roles(manifest)
    required_renders = set(gates.get("required_renders") or [])

    hard = [
        _gate(
            "validation_report_not_pass",
            report.get("status") == "pass",
            f"validation status is {report.get('status')!r}",
        ),
        _gate(
            "missing_assembled_glb",
            bool(assembled.get("filename")),
            "assembled filename is present" if assembled.get("filename") else "no assembled filename",
        ),
        _gate(
            "missing_fixed_semantic_module",
            bool(fixed_modules),
            f"{len(fixed_modules)} fixed semantic modules",
        ),
        _gate(
            "missing_repeatable_middle_module",
            bool(repeatable_modules),
            f"{len(repeatable_modules)} repeatable middle modules",
        ),
        _gate(
            "missing_footprint_compatibility",
            bool(footprint),
            f"{len(preferred_profiles)} preferred footprint profiles",
        ),
        _gate(
            "missing_required_render",
            required_renders <= render_roles,
            "missing: " + ", ".join(sorted(required_renders - render_roles))
            if required_renders - render_roles
            else "all required renders declared",
        ),
    ]

    facade = manifest.get("facade_sheet") or {}
    channels = set(facade.get("pbr_channels") or [])
    required_channels = set(
        memory.get("construction_memory", {}).get("facade_pbr", {}).get("required_channels") or []
    )
    shadow_neutral = facade.get("shadow_neutral") or {}
    bay_strategy = facade.get("bay_strategy") or {}
    variants = list(bay_strategy.get("middle_variants") or [])
    delivery = facade.get("delivery") or {}
    near_width = int(delivery.get("near_atlas_width_px") or 0)
    far_width = int(delivery.get("far_atlas_width_px") or 0)
    pbr_memory = memory.get("construction_memory", {}).get("facade_pbr", {})
    min_near = int(pbr_memory.get("near_atlas_min_width_px") or 2048)
    max_far = int(pbr_memory.get("far_atlas_max_width_px") or 1024)
    min_variants = int(
        memory.get("construction_memory", {}).get("variation", {}).get(
            "minimum_middle_bay_variants", 3
        )
    )
    min_profiles = int(gates.get("preferred_footprint_profile_count") or 3)
    fixed_tokens = _fixed_contract_tokens(manifest)
    required_fixed = {"podium/entrance", "corner returns", "crown", "roof"}
    side_wrap = str((facade.get("assembly_contract") or {}).get("side_elevations") or "")
    assembled_report = next(
        (item for item in report.get("modules") or [] if item.get("role") == "assembled"),
        {},
    )
    material_count = len(assembled_report.get("materials") or [])
    material_threshold = int(gates.get("material_count_review_threshold") or 20)
    visual_approved, visual_detail = validate_visual_approval(visual_approval)

    review = [
        _gate(
            "fewer_than_three_middle_variants",
            len(variants) >= min_variants,
            f"{len(variants)} middle variants; target is {min_variants}",
        ),
        _gate(
            "missing_full_pbr_channels",
            required_channels <= channels,
            "missing: " + ", ".join(sorted(required_channels - channels))
            if required_channels - channels
            else "full PBR channel set declared",
        ),
        _gate(
            "albedo_not_shadow_neutral",
            shadow_neutral.get("enabled") is True,
            "shadow-neutral albedo declared"
            if shadow_neutral.get("enabled") is True
            else "shadow-neutral albedo not declared",
        ),
        _gate(
            "near_atlas_below_2048",
            near_width >= min_near,
            f"near atlas width {near_width}px; minimum {min_near}px",
        ),
        _gate(
            "far_atlas_above_1024",
            0 < far_width <= max_far,
            f"far atlas width {far_width}px; maximum {max_far}px",
        ),
        _gate(
            "missing_fixed_assembly_contract",
            required_fixed <= fixed_tokens,
            "missing: " + ", ".join(sorted(required_fixed - fixed_tokens))
            if required_fixed - fixed_tokens
            else "fixed entrance, corner, crown and roof declared",
        ),
        _gate(
            "fewer_than_three_preferred_footprint_profiles",
            len(preferred_profiles) >= min_profiles,
            f"{len(preferred_profiles)} preferred profiles; target is {min_profiles}",
        ),
        _gate(
            "missing_side_elevation_wrap",
            bool(side_wrap),
            side_wrap if side_wrap else "side-elevation wrap not declared",
        ),
        _gate(
            "material_count_warning",
            material_count == 0 or material_count <= material_threshold,
            f"{material_count} assembled materials; review above {material_threshold}"
            if material_count
            else "assembled material inventory unavailable",
        ),
        _gate(
            "missing_visual_approval",
            visual_approved,
            visual_detail,
        ),
    ]

    triangles = int(assembled.get("triangle_count") or 0)
    budget = gates.get("triangle_budget") or {}
    triangle_budget = _gate(
        "city_triangle_budget",
        int(budget.get("city_min") or 0) <= triangles <= int(budget.get("city_max") or 10**9),
        f"{triangles} assembled triangles; budget {budget.get('city_min')}-{budget.get('city_max')}",
    )
    review.append(triangle_budget)

    hard_failures = [item for item in hard if not item["passed"]]
    review_findings = [item for item in review if not item["passed"]]
    status = "fail" if hard_failures else "review" if review_findings else "pass"
    return {
        "schema": "high-quality-building-assessment@1",
        "memory_version": memory["memory_version"],
        "archetype_id": manifest.get("archetype_id"),
        "family": manifest.get("family"),
        "status": status,
        "high_quality_ready": status == "pass",
        "hard_failures": hard_failures,
        "review_findings": review_findings,
        "gates": {"hard": hard, "review": review},
    }


def assess_paths(
    manifest_path: Path,
    report_path: Path | None = None,
    memory_path: Path = DEFAULT_MEMORY_PATH,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report_path = report_path or manifest_path.with_name("validation_report.json")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    approval_path = manifest_path.with_name("visual_approval.json")
    approval = (
        json.loads(approval_path.read_text(encoding="utf-8"))
        if approval_path.exists()
        else None
    )
    return assess_family_quality(
        manifest,
        report,
        load_quality_memory(memory_path),
        visual_approval=approval,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--memory", type=Path, default=DEFAULT_MEMORY_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    assessment = assess_paths(args.manifest, args.report, args.memory)
    rendered = json.dumps(assessment, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return {"pass": 0, "review": 2, "fail": 1}[assessment["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
