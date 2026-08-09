"""Create the finite, evidence-backed V86 LEGO catalogue rollout ledger."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from catalog_coverage import _normalise_catalogue
from signature_profiles import load_signature_profiles, signature_for


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
DEFAULT_CAMPAIGN = TOOL_DIR / "catalogue_rollout_v86.json"
DEFAULT_OUTPUT = REPO / "docs/reviews/catalogue-rollout-v86/rollout-plan.json"
DEFAULT_MARKDOWN = REPO / "docs/reviews/catalogue-rollout-v86/README.md"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def reference_path(value: str) -> Path:
    return REPO / "frontend/public" / value.lstrip("/")


def sheet_for(archetype_id: str, roots: list[Path]) -> Path | None:
    slug = archetype_id.replace("_", "-")
    for root in roots:
        candidate = root / slug
        if (candidate / "manifest.json").exists():
            return candidate
    return None


def scan_generated(roots: list[Path]) -> dict[tuple[str, str | None], dict[str, Any]]:
    generated: dict[tuple[str, str | None], dict[str, Any]] = {}
    for root in roots:
        if not root.exists():
            continue
        for manifest_path in root.rglob("*_manifest.json"):
            try:
                manifest = read_json(manifest_path)
            except (OSError, ValueError, TypeError):
                continue
            archetype_id = manifest.get("archetype_id")
            if not archetype_id:
                continue
            validation_path = manifest_path.parent / "validation_report.json"
            validation = read_json(validation_path).get("status") if validation_path.exists() else None
            key = (str(archetype_id), manifest.get("variant_id"))
            candidate = {
                "family": manifest.get("family"),
                "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
                "validation": validation,
                "modified_at": manifest_path.stat().st_mtime,
            }
            previous = generated.get(key)
            rank = (validation == "pass", candidate["modified_at"])
            previous_rank = (
                previous.get("validation") == "pass", previous.get("modified_at", 0.0)
            ) if previous else (False, 0.0)
            if not previous or rank > previous_rank:
                generated[key] = candidate
    return generated


def approved_targets(paths: list[Path]) -> dict[tuple[str, str | None], str]:
    approved: dict[tuple[str, str | None], str] = {}
    for path in paths:
        if not path.exists():
            continue
        payload = read_json(path)
        for row in payload.get("families") or []:
            state = str(row.get("review_state") or "")
            if payload.get("schema") == "building-generation-gold-set@1":
                state = "gold_set"
            if state == "gold_set" or state.startswith("keeper"):
                approved[(str(row["archetype_id"]), row.get("variant_id"))] = state
    return approved


def dimensions(archetype: dict[str, Any]) -> tuple[float, float, int]:
    width = float(archetype.get("suggestedWidth_m") or archetype.get("minWidth_m") or 24.0)
    depth = float(archetype.get("suggestedDepth_m") or archetype.get("minDepth_m") or 18.0)
    low = int(archetype.get("minFloors") or 1)
    high = int(archetype.get("maxFloors") or low)
    return width, depth, max(1, int(math.floor((low + high) / 2 + 0.5)))


def readiness(
    archetype_id: str,
    variant_id: str | None,
    raw_profiles: dict[str, dict],
    sheet: Path | None,
) -> tuple[str, list[str], dict[str, Any]]:
    profile_key = variant_id or archetype_id
    if profile_key not in raw_profiles:
        return "needs_variant_profile", ["exact variant signature profile"], {}
    profile = signature_for(profile_key)
    contract = profile.get("production_contract") or {}
    graph = profile.get("massing_graph") or {}
    references = graph.get("reference_views") or []
    roles = {str(item.get("role")) for item in references}
    required_roles = {"street_identity", "oblique_massing", "roof_plan"}
    missing: list[str] = []
    if not contract or contract.get("quality_contract_version") != 3:
        missing.append("quality-contract-v3 image lock")
    if contract.get("identity_mode") not in {"massing_graph", "semantic_stack"}:
        missing.append("classified identity mode")
    if not (contract.get("surface_finish") or {}).get("required_baked_materials"):
        missing.append("construction-role baked PBR contract")
    if required_roles - roles:
        missing.append("three role-labelled exact references")
    missing_files = [
        item.get("path") for item in references
        if item.get("path") and not reference_path(str(item["path"])).exists()
    ]
    if missing_files:
        missing.append("reference files present")
    if sheet is None:
        missing.append("audited facade sheet")
    if missing:
        state = "needs_facade_sheet" if missing == ["audited facade sheet"] else "needs_contract"
    else:
        state = "ready_to_generate"
    return state, missing, {
        "identity_mode": contract.get("identity_mode"),
        "reference_roles": sorted(roles),
        "profile_key": profile_key,
    }


def target_rows(
    catalogue: list[dict[str, Any]],
    raw_profiles: dict[str, dict],
    sheets: list[Path],
    generated: dict[tuple[str, str | None], dict[str, Any]],
    approved: dict[tuple[str, str | None], str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for catalogue_index, archetype in enumerate(catalogue):
        archetype_id = str(archetype["archetypeId"])
        variants = list(archetype.get("variants") or []) or [{"id": None, "label": "Base"}]
        width, depth, floors = dimensions(archetype)
        facade = sheet_for(archetype_id, sheets)
        for variant_index, variant in enumerate(variants):
            variant_id = variant.get("id")
            key = (archetype_id, variant_id)
            state, blockers, evidence = readiness(archetype_id, variant_id, raw_profiles, facade)
            candidate = generated.get(key)
            approval = approved.get(key)
            if approval:
                state, blockers = "approved_existing", []
            elif candidate and candidate.get("validation") == "pass":
                state, blockers = "generated_human_review", ["explicit keeper/provisional/reject decision"]
            rows.append({
                "target_key": f"{archetype_id}::{variant_id or 'base'}",
                "phase": "representative" if variant_index == 0 else "remaining_variant",
                "catalogue_index": catalogue_index,
                "variant_index": variant_index,
                "archetype_id": archetype_id,
                "archetype_label": archetype.get("archetypeLabel") or archetype_id,
                "variant_id": variant_id,
                "variant_label": variant.get("label") or variant_id or "Base",
                "development_type": archetype.get("developmentType"),
                "aesthetic_category": archetype.get("aestheticCategory"),
                "width_m": width,
                "depth_m": depth,
                "floors": floors,
                "state": state,
                "blockers": blockers,
                "facade_sheet": str(facade.relative_to(REPO)).replace("\\", "/") if facade else None,
                "generated": candidate,
                "approval": approval,
                **evidence,
            })
    return rows


def assign_batches(rows: list[dict[str, Any]], batch_size: int) -> list[dict[str, Any]]:
    batches: list[dict[str, Any]] = []
    for phase, prefix in (("representative", "REP"), ("remaining_variant", "VAR")):
        pending = [row for row in rows if row["phase"] == phase and row["state"] != "approved_existing"]
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in pending:
            groups[str(row.get("aesthetic_category") or row.get("development_type") or "uncategorized")].append(row)
        batch_number = 1
        for category in sorted(groups):
            group = sorted(groups[category], key=lambda item: (item["catalogue_index"], item["variant_index"]))
            for offset in range(0, len(group), batch_size):
                chunk = group[offset:offset + batch_size]
                batch_id = f"{prefix}-{batch_number:03d}"
                for row in chunk:
                    row["batch_id"] = batch_id
                batches.append({
                    "batch_id": batch_id,
                    "phase": phase,
                    "cluster": category,
                    "target_count": len(chunk),
                    "state_counts": dict(sorted(Counter(row["state"] for row in chunk).items())),
                    "targets": [row["target_key"] for row in chunk],
                    "checkpoint_required": True,
                })
                batch_number += 1
    return batches


def build_plan(campaign_path: Path) -> dict[str, Any]:
    campaign = read_json(campaign_path)
    catalogue_path = REPO / campaign["catalogue"]
    catalogue = _normalise_catalogue(read_json(catalogue_path))
    raw_profiles = load_signature_profiles()
    sheet_roots = [REPO / value for value in campaign["facade_sheet_roots"]]
    build_roots = [REPO / value for value in campaign["build_roots"]]
    approval_paths = [REPO / value for value in campaign["approval_sources"]]
    generated = scan_generated(build_roots)
    approved = approved_targets(approval_paths)
    rows = target_rows(catalogue, raw_profiles, sheet_roots, generated, approved)
    batches = assign_batches(rows, int(campaign["batch_size"]))
    by_phase = {
        phase: dict(sorted(Counter(row["state"] for row in rows if row["phase"] == phase).items()))
        for phase in ("representative", "remaining_variant")
    }
    facade_missing = sum(row["state"] in {"needs_facade_sheet", "needs_variant_profile", "needs_contract"} and not row["facade_sheet"] for row in rows)
    return {
        "schema": "catalogue-rollout-plan@1",
        "campaign_version": campaign["version"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalogue_source": campaign["catalogue"],
        "summary": {
            "parent_archetypes": len(catalogue),
            "named_variant_targets": len(rows),
            "representative_targets": sum(row["phase"] == "representative" for row in rows),
            "remaining_variant_targets": sum(row["phase"] == "remaining_variant" for row in rows),
            "exact_variant_profiles": sum((row.get("profile_key") == row.get("variant_id")) for row in rows),
            "audited_facade_sheet_archetypes": len({row["archetype_id"] for row in rows if row["facade_sheet"]}),
            "approved_existing": sum(row["state"] == "approved_existing" for row in rows),
            "generated_human_review": sum(row["state"] == "generated_human_review" for row in rows),
            "ready_to_generate": sum(row["state"] == "ready_to_generate" for row in rows),
            "estimated_blender_hours_representatives_at_8_min": round(sum(row["phase"] == "representative" and row["state"] != "approved_existing" for row in rows) * 8 / 60, 1),
            "estimated_blender_hours_all_variants_at_8_min": round(sum(row["state"] != "approved_existing" for row in rows) * 8 / 60, 1),
            "potential_paid_facade_image_calls_if_all_missing": facade_missing * 2,
            "state_counts_by_phase": by_phase,
            "batch_count": len(batches),
        },
        "policy": {
            "batch_size": campaign["batch_size"],
            "paid_facade_calls_default": campaign["default_paid_facade_calls_per_batch"],
            "quality_gates": campaign["quality_gates"],
            "checkpoints": campaign["checkpoints"],
            "artifact_retention": campaign["artifact_retention"],
        },
        "batches": batches,
        "targets": rows,
    }


def markdown(plan: dict[str, Any]) -> str:
    summary = plan["summary"]
    lines = [
        "# V86 catalogue rollout plan",
        "",
        "The catalogue is released in two finite waves: one exact representative variant per parent archetype, then every remaining named variant. No target enters Blender until its exact-variant image lock and audited inputs pass readiness checks.",
        "",
        "## Scope",
        "",
        f"- Parent archetypes: **{summary['parent_archetypes']}**",
        f"- Named variant delivery targets: **{summary['named_variant_targets']}**",
        f"- Representative wave: **{summary['representative_targets']}**",
        f"- Remaining-variant wave: **{summary['remaining_variant_targets']}**",
        f"- Existing explicit approvals: **{summary['approved_existing']}**",
        f"- Machine-generated targets awaiting human review: **{summary['generated_human_review']}**",
        f"- Targets immediately render-ready: **{summary['ready_to_generate']}**",
        f"- Finite five-building checkpoints: **{summary['batch_count']}**",
        "",
        "At the current measured cadence, the representative wave is roughly "
        f"{summary['estimated_blender_hours_representatives_at_8_min']} serial Blender hours and all variants roughly "
        f"{summary['estimated_blender_hours_all_variants_at_8_min']} hours. This is a campaign, not one unattended generation loop.",
        "",
        "## Mandatory release path",
        "",
        "1. Author the exact variant image-lock profile and role-specific material schedule.",
        "2. Approve or create the rectified facade source; paid calls remain zero unless a batch explicitly authorizes them.",
        "3. Run grammar-only production preflight.",
        "4. Render at most five targets sequentially, with geometry, PBR and GLB parity reports.",
        "5. Publish exact-reference comparison boards and assign keeper, provisional or reject.",
        "6. Start the next batch only after the checkpoint is recorded.",
        "",
        "## First campaign checkpoint",
        "",
        "`PILOT-001` is the Board-Formed Concrete Modernist Civic Block. It uses an existing massing graph and audited sheet, incurs no paid facade calls and tests the complete V86 resume/review path.",
        "",
        "## First ten planned batches",
        "",
        "| Batch | Wave | Cluster | Targets | Readiness |",
        "|---|---|---|---:|---|",
    ]
    for batch in plan["batches"][:10]:
        states = ", ".join(f"{key}: {value}" for key, value in batch["state_counts"].items())
        lines.append(f"| {batch['batch_id']} | {batch['phase']} | {batch['cluster']} | {batch['target_count']} | {states} |")
    lines.extend([
        "",
        "The complete target ledger, blockers, dimensions, batch assignments and estimates are in `rollout-plan.json`.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=DEFAULT_CAMPAIGN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    plan = build_plan(args.campaign.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(plan), encoding="utf-8")
    print(json.dumps(plan["summary"], indent=2))


if __name__ == "__main__":
    main()
