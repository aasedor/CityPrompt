"""Build an evidence-backed coverage ledger for the LEGO building catalogue.

The catalogue has two independent deliverables: one parent archetype target and
every named architectural variant.  This tool never treats a parent fallback as
variant coverage.  It scans compiler manifests, their adjacent validation
reports, the render-lock review registry and (optionally) the live City Prompt
LEGO library, then writes JSON plus a short Markdown review queue.

Example::

    python tools/archetype_compiler/catalog_coverage.py \
      --catalog artifacts/catalog-current.json \
      --build-root build \
      --pilot tools/archetype_compiler/renderlock_variant_pilot_v1.json \
      --api-base http://localhost:8000 \
      --output artifacts/catalog-coverage.json \
      --markdown artifacts/catalog-coverage.md

``SITEFORGE_TOKEN`` is read from the environment when ``--api-base`` is used;
the token is never written to either report.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PBR_CHANNELS = {"albedo", "normal", "roughness", "ao", "depth", "emissive"}
LIVE_PREFIXES = ("keeper_live", "live_qa")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _validation_status(manifest_path: Path) -> str:
    report = manifest_path.parent / "validation_report.json"
    if not report.exists():
        return "missing"
    try:
        return str((_read_json(report) or {}).get("status") or "unknown").lower()
    except (OSError, ValueError, TypeError):
        return "invalid"


def _render_locked(manifest: dict[str, Any]) -> bool:
    sheet = manifest.get("facade_sheet") or {}
    channels = {str(value).lower() for value in sheet.get("pbr_channels") or []}
    return PBR_CHANNELS.issubset(channels) and bool(sheet.get("source_directory"))


@dataclass(frozen=True)
class Candidate:
    archetype_id: str
    variant_id: str | None
    family: str
    manifest_path: str
    validation: str
    render_locked: bool
    modified_at: float

    @property
    def rank(self) -> tuple[int, int, float]:
        return (self.validation == "pass", self.render_locked, self.modified_at)


def _scan_candidates(build_roots: Iterable[Path]) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[Path] = set()
    for root in build_roots:
        if not root.exists():
            continue
        for path in root.rglob("*_manifest.json"):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                payload = _read_json(path)
            except (OSError, ValueError, TypeError):
                continue
            if not isinstance(payload, dict) or not payload.get("modules"):
                continue
            archetype_id = str(payload.get("archetype_id") or "").strip()
            family = str(payload.get("family") or "").strip()
            if not archetype_id or not family:
                continue
            raw_variant = payload.get("variant_id")
            variant_id = str(raw_variant).strip() if raw_variant else None
            candidates.append(Candidate(
                archetype_id=archetype_id,
                variant_id=variant_id,
                family=family,
                manifest_path=str(resolved),
                validation=_validation_status(path),
                render_locked=_render_locked(payload),
                modified_at=path.stat().st_mtime,
            ))
    return candidates


def _pilot_states(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {}
    payload = _read_json(path)
    return {
        str(row.get("family_id")): str(row.get("review_state") or "unreviewed")
        for row in payload.get("families") or []
        if row.get("family_id")
    }


def _live_families(api_base: str | None) -> set[str]:
    if not api_base:
        return set()
    token = os.environ.get("SITEFORGE_TOKEN", "").strip()
    if not token:
        raise SystemExit("--api-base requires SITEFORGE_TOKEN in the environment")
    request = urllib.request.Request(
        api_base.rstrip("/") + "/api/v1/lego-assembly/modules",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return {
        str(module.get("family"))
        for module in payload.get("modules") or []
        if module.get("family")
    }


def _best_candidates(candidates: list[Candidate]) -> dict[tuple[str, str | None], Candidate]:
    grouped: dict[tuple[str, str | None], list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[(candidate.archetype_id, candidate.variant_id)].append(candidate)
    return {key: max(rows, key=lambda row: row.rank) for key, rows in grouped.items()}


def _target_rows(
    catalogue: list[dict[str, Any]],
    best: dict[tuple[str, str | None], Candidate],
    pilot: dict[str, str],
    imported: set[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for archetype in catalogue:
        archetype_id = str(archetype.get("archetypeId") or "").strip()
        if not archetype_id:
            continue
        targets: list[tuple[str, str | None, str]] = [
            ("base", None, str(archetype.get("archetypeLabel") or archetype_id)),
        ]
        targets.extend(
            ("variant", str(variant.get("id")), str(variant.get("label") or variant.get("id")))
            for variant in archetype.get("variants") or []
            if variant.get("id")
        )
        for kind, variant_id, target_label in targets:
            candidate = best.get((archetype_id, variant_id))
            family = candidate.family if candidate else None
            review_state = pilot.get(family or "")
            is_imported = bool(family and family in imported)
            live_qa = bool(review_state and review_state.lower().startswith(LIVE_PREFIXES))
            if live_qa:
                state = "live_qa"
            elif is_imported:
                state = "imported"
            elif candidate and candidate.validation == "pass":
                state = "validated"
            elif candidate:
                state = "generated_unvalidated"
            else:
                state = "missing"
            rows.append({
                "target_kind": kind,
                "archetype_id": archetype_id,
                "archetype_label": str(archetype.get("archetypeLabel") or archetype_id),
                "variant_id": variant_id,
                "target_label": target_label,
                "development_type": archetype.get("developmentType"),
                "family": family,
                "state": state,
                "validation": candidate.validation if candidate else None,
                "render_locked": candidate.render_locked if candidate else False,
                "imported": is_imported,
                "review_state": review_state,
                "manifest_path": candidate.manifest_path if candidate else None,
            })
    return rows


def _summary(rows: list[dict[str, Any]], candidate_count: int, imported_count: int) -> dict[str, Any]:
    by_kind: dict[str, dict[str, Any]] = {}
    for kind in ("base", "variant", "all"):
        subset = rows if kind == "all" else [row for row in rows if row["target_kind"] == kind]
        states = Counter(row["state"] for row in subset)
        by_kind[kind] = {
            "total": len(subset),
            "states": dict(sorted(states.items())),
            "validated_or_better": sum(
                1 for row in subset if row["state"] in {"validated", "imported", "live_qa"}
            ),
            "imported_or_better": sum(
                1 for row in subset if row["state"] in {"imported", "live_qa"}
            ),
            "live_qa": sum(1 for row in subset if row["state"] == "live_qa"),
            "render_locked": sum(1 for row in subset if row["render_locked"]),
        }
    return {
        "catalogue_archetypes": by_kind["base"]["total"],
        "catalogue_variants": by_kind["variant"]["total"],
        "compiler_manifests_scanned": candidate_count,
        "imported_families_observed": imported_count,
        "coverage": by_kind,
    }


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# City Prompt LEGO catalogue coverage",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "| Target | Total | Validated+ | Imported+ | Live QA | Render-locked |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, label in (("base", "Parent archetypes"), ("variant", "Named variants"), ("all", "All targets")):
        row = summary["coverage"][key]
        lines.append(
            f"| {label} | {row['total']} | {row['validated_or_better']} | "
            f"{row['imported_or_better']} | {row['live_qa']} | {row['render_locked']} |"
        )
    lines.extend(["", "## Next uncovered variant targets", ""])
    missing = [
        row for row in payload["targets"]
        if row["target_kind"] == "variant" and row["state"] == "missing"
    ]
    for row in missing[:60]:
        lines.append(
            f"- `{row['archetype_id']}::{row['variant_id']}` — "
            f"{row['archetype_label']} / {row['target_label']}"
        )
    if not missing:
        lines.append("- None")
    lines.extend(["", "## Pending live QA", ""])
    pending = [
        row for row in payload["targets"]
        if row["state"] in {"validated", "imported"}
    ]
    for row in pending[:60]:
        target = row["variant_id"] or "base"
        lines.append(f"- `{row['archetype_id']}::{target}` — {row['family']} ({row['state']})")
    if not pending:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, action="append", default=[])
    parser.add_argument("--pilot", type=Path)
    parser.add_argument("--api-base")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    catalogue = _read_json(args.catalog)
    if not isinstance(catalogue, list):
        raise SystemExit("catalogue export must be a JSON array")
    build_roots = args.build_root or [Path("build")]
    candidates = _scan_candidates(build_roots)
    imported = _live_families(args.api_base)
    rows = _target_rows(catalogue, _best_candidates(candidates), _pilot_states(args.pilot), imported)
    payload = {
        "schema": "lego-catalogue-coverage@1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalogue_source": str(args.catalog.resolve()),
        "build_roots": [str(path.resolve()) for path in build_roots],
        "summary": _summary(rows, len(candidates), len(imported)),
        "targets": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
