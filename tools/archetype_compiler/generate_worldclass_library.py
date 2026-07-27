"""Resume-safe facade-sheet + GLB batch pipeline for the v7 LEGO library.

The script prepares the real catalogue grammar first, generates/caches one
Gemini elevation per family, then invokes the normal single-family generator
with the sheet attached. Failures are recorded and the remaining families
continue, making the overnight run safe to resume.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(TOOL_DIR))

from compiler import compile_archetype  # noqa: E402
from generate_family import export_archetype  # noqa: E402
from quality_memory import (  # noqa: E402
    DEFAULT_MEMORY_PATH,
    assess_family_quality,
    load_quality_memory,
)
from signature_profiles import inject_signature  # noqa: E402


def log(message: str) -> None:
    print(f"[worldclass_library] {message}", flush=True)


def run(command: list[str], log_path: Path) -> None:
    log(f"$ {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        (result.stdout or "") + "\n--- stderr ---\n" + (result.stderr or ""),
        encoding="utf-8",
    )
    if result.returncode:
        tail = "\n".join(((result.stdout or "") + "\n" + (result.stderr or "")).splitlines()[-24:])
        raise RuntimeError(f"exit {result.returncode}; see {log_path}\n{tail}")


def prepare_grammar(entry: dict, family_dir: Path) -> dict:
    family_dir.mkdir(parents=True, exist_ok=True)
    source_path = family_dir / "archetype-source.json"
    payload = export_archetype(entry["archetype_id"], entry.get("variant_id"), source_path)
    grammar = compile_archetype(
        payload,
        floors=entry.get("floors"),
        width_m=entry.get("width_m"),
        depth_m=entry.get("depth_m"),
    ).to_dict()
    inject_signature(grammar, entry["archetype_id"])
    (family_dir / "grammar.json").write_text(json.dumps(grammar, indent=2), encoding="utf-8")
    return grammar


def family_result(entry: dict, family_dir: Path, sheet_dir: Path, quality_memory: dict) -> dict:
    reports = list(family_dir.glob("validation_report.json"))
    manifests = [path for path in family_dir.glob("*_manifest.json") if path.name != "manifest.json"]
    manifest = json.loads(manifests[0].read_text(encoding="utf-8")) if manifests else {}
    report = json.loads(reports[0].read_text(encoding="utf-8")) if reports else {}
    preview_name = manifest.get("thumbnail")
    quality_assessment = (
        assess_family_quality(manifest, report, quality_memory, family_dir=family_dir)
        if manifest and report
        else {
            "schema": "high-quality-building-assessment@1",
            "memory_version": quality_memory["memory_version"],
            "status": "pending",
            "high_quality_ready": False,
            "hard_failures": [],
            "review_findings": [],
        }
    )
    (family_dir / "quality_assessment.json").write_text(
        json.dumps(quality_assessment, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        **entry,
        "family": manifest.get("family"),
        "output_directory": str(family_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "facade_sheet_directory": str(sheet_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "manifest": manifests[0].name if manifests else None,
        "preview": preview_name,
        "validation": report.get("status"),
        "assembled": (manifest.get("assembled") or {}).get("filename"),
        "triangle_count": (manifest.get("assembled") or {}).get("triangle_count"),
        "module_count": len(manifest.get("modules") or []),
        "city_prompt_ready": report.get("status") == "pass" and bool(manifests),
        "high_quality_ready": quality_assessment["high_quality_ready"],
        "quality_assessment": quality_assessment,
        "import_command": f"python tools/archetype_compiler/import_manifest.py {family_dir.relative_to(REPO_ROOT).as_posix()}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=TOOL_DIR / "worldclass_v7_library.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "build" / "worldclass-v7" / "families")
    parser.add_argument("--only", action="append", default=[], help="archetype id; repeat to select several")
    parser.add_argument("--force-facades", action="store_true")
    parser.add_argument("--skip-facades", action="store_true", help="require an existing sheet manifest")
    parser.add_argument("--skip-models", action="store_true", help="prepare grammars/sheets only")
    parser.add_argument("--presentation-view-set", choices=("all", "preview"), default=None)
    parser.add_argument("--facade-sheet-detail", choices=("hero", "city"), default=None)
    parser.add_argument(
        "--quality-memory",
        type=Path,
        default=DEFAULT_MEMORY_PATH,
        help="versioned executable quality rules used to route pass/review/fail outputs",
    )
    args = parser.parse_args()

    registry_path = args.registry.resolve()
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    quality_memory = load_quality_memory(args.quality_memory.resolve())
    profile = registry.get("generation_profile") or {}
    entries = list(registry["entries"])
    if args.only:
        selected = set(args.only)
        entries = [entry for entry in entries if entry["archetype_id"] in selected]
        missing = selected - {entry["archetype_id"] for entry in entries}
        if missing:
            raise SystemExit(f"unknown --only ids: {', '.join(sorted(missing))}")
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    view_set = args.presentation_view_set or profile.get("presentation_view_set", "preview")
    detail = args.facade_sheet_detail or profile.get("geometry_detail", "city")
    results: list[dict] = []
    failures: list[dict] = []

    for index, entry in enumerate(entries, 1):
        archetype_id = entry["archetype_id"]
        family_dir = output_root / archetype_id.replace("_", "-")
        log(f"[{index}/{len(entries)}] {archetype_id}")
        try:
            grammar_path = family_dir / "grammar.json"
            if args.skip_models and grammar_path.exists():
                grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
            else:
                grammar = prepare_grammar(entry, family_dir)
            family = grammar["family_id"]
            sheet_root = REPO_ROOT / profile.get("facade_sheet_root", "tools/archetype_compiler/facade_sheets")
            sheet_dir = sheet_root / family
            sheet_manifest = sheet_dir / "manifest.json"
            if not args.skip_facades:
                facade_command = [
                    sys.executable,
                    str(TOOL_DIR / "generate_facade_sheets.py"),
                    "--family", str(family_dir),
                    "--out", str(sheet_dir),
                ]
                if args.force_facades:
                    facade_command.append("--force")
                run(facade_command, family_dir / "logs" / "facade-sheet.log")
            elif not args.skip_models and not sheet_manifest.exists():
                raise RuntimeError(f"--skip-facades but {sheet_manifest} does not exist")

            if not args.skip_models:
                model_command = [
                    sys.executable,
                    str(TOOL_DIR / "generate_family.py"),
                    "--archetype-id", archetype_id,
                    "--output", str(family_dir),
                    "--facade-sheets", str(sheet_dir),
                    "--facade-sheet-detail", detail,
                    "--textures", str(REPO_ROOT / profile.get(
                        "texture_library", "tools/archetype_compiler/textures"
                    )),
                    "--no-ao",
                    "--presentation-engine", "eevee",
                    "--presentation-samples", "48",
                    "--presentation-view-set", view_set,
                ]
                if entry.get("variant_id"):
                    model_command += ["--variant-id", entry["variant_id"]]
                if entry.get("floors"):
                    model_command += ["--floors", str(entry["floors"])]
                if entry.get("width_m"):
                    model_command += ["--width", str(entry["width_m"])]
                if entry.get("depth_m"):
                    model_command += ["--depth", str(entry["depth_m"])]
                run(model_command, family_dir / "logs" / "family-batch.log")
            results.append(family_result(entry, family_dir, sheet_dir, quality_memory))
            log(f"completed {archetype_id}")
        except Exception as exc:
            failure = {"archetype_id": archetype_id, "error": str(exc)}
            failures.append(failure)
            log(f"FAILED {archetype_id}: {exc}")

        index_payload = {
            "schema": "worldclass-lego-build-index@1",
            "library": registry.get("name"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "registry": str(registry_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "generation_profile": {
                **profile,
                "geometry_detail": detail,
                "presentation_view_set": view_set,
                "quality_memory_version": quality_memory["memory_version"],
            },
            "families": results,
            "failures": failures,
            "summary": {
                "requested": len(entries),
                "completed": len(results),
                "city_prompt_ready": sum(bool(item.get("city_prompt_ready")) for item in results),
                "high_quality_ready": sum(bool(item.get("high_quality_ready")) for item in results),
                "quality_review": sum(
                    item.get("quality_assessment", {}).get("status") == "review" for item in results
                ),
                "quality_failed": sum(
                    item.get("quality_assessment", {}).get("status") == "fail" for item in results
                ),
                "quality_pending": sum(
                    item.get("quality_assessment", {}).get("status") == "pending" for item in results
                ),
                "failed": len(failures),
            },
        }
        (output_root.parent / "worldclass-library-index.json").write_text(
            json.dumps(index_payload, indent=2), encoding="utf-8"
        )

    log(f"done: {len(results)} completed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
