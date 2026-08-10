"""Run one finite, resume-safe V86 catalogue batch with machine QA."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quality_memory import assess_family_quality, load_quality_memory


REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools/archetype_compiler"
DEFAULT_REGISTRY = TOOLS / "catalogue_rollout_v86_pilot.json"
DEFAULT_OUTPUT = REPO / "artifacts/catalogue-rollout-v86"
BLENDER = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
MAX_BATCH = 5


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run(command: list[str], log_path: Path | None = None, *, allow_failure: bool = False) -> int:
    print("[catalogue-v86] $", " ".join(command), flush=True)
    result = subprocess.run(
        command,
        cwd=REPO,
        capture_output=log_path is not None,
        text=log_path is not None,
        encoding="utf-8" if log_path is not None else None,
        errors="replace" if log_path is not None else None,
        check=False,
    )
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            (result.stdout or "") + "\n--- stderr ---\n" + (result.stderr or ""),
            encoding="utf-8",
        )
        if result.returncode:
            tail = "\n".join(((result.stdout or "") + "\n" + (result.stderr or "")).splitlines()[-24:])
            print(tail, flush=True)
    if result.returncode and not allow_failure:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.returncode


def validate_registry(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "catalogue-rollout-batch@1":
        raise SystemExit("unsupported batch registry schema")
    entries = payload.get("entries") or []
    if not 1 <= len(entries) <= MAX_BATCH:
        raise SystemExit(f"a catalogue batch must contain 1-{MAX_BATCH} entries")
    if int(payload.get("paid_facade_calls") or 0) != 0:
        raise SystemExit("this runner never performs paid facade calls; authorize and prepare them separately")
    for entry in entries:
        required = {"archetype_id", "variant_id", "family_id", "width_m", "depth_m", "floors", "facade_sheet"}
        missing = required - set(entry)
        if missing:
            raise SystemExit(f"entry missing required fields: {', '.join(sorted(missing))}")
        facade = REPO / str(entry["facade_sheet"])
        if not (facade / "manifest.json").exists():
            raise SystemExit(f"audited facade sheet missing: {facade}")


def require_capacity(output_root: Path, minimum_free_gb: float) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    free_gb = shutil.disk_usage(output_root).free / 1024**3
    if free_gb < minimum_free_gb:
        raise SystemExit(f"only {free_gb:.1f} GB free; campaign requires {minimum_free_gb:.1f} GB")


def derive_textures(textures: Path, recipe_manifest: Path | None = None, pipeline_version: str = "v86") -> None:
    command = [
        sys.executable,
        str(TOOLS / "derive_surface_story_pbr.py"),
        "--source-root", str(TOOLS / "textures"),
        "--additional-source-root", str(TOOLS / "textures_worldclass_v7"),
        "--output-root", str(textures),
        "--size", "1024",
        "--pipeline-version", pipeline_version,
    ]
    if recipe_manifest is not None:
        command.extend(["--recipe-manifest", str(recipe_manifest)])
    run(command)


def generate(entry: dict[str, Any], family_dir: Path, textures: Path, grammar_only: bool) -> None:
    command = [
        sys.executable,
        str(TOOLS / "generate_family.py"),
        "--archetype-id", str(entry["archetype_id"]),
        "--variant-id", str(entry["variant_id"]),
        "--family-id", str(entry["family_id"]),
        "--output", str(family_dir),
        "--width", str(entry["width_m"]),
        "--depth", str(entry["depth_m"]),
        "--floors", str(entry["floors"]),
        "--textures", str(textures),
        "--facade-sheets", str(REPO / str(entry["facade_sheet"])),
        "--facade-sheet-detail", "hero",
    ]
    if grammar_only:
        command.append("--grammar-only")
    else:
        command.extend([
            "--keep-blend", "--no-ao",
            "--presentation-engine", "eevee",
            "--presentation-samples", "48",
            "--presentation-view-set", "all",
        ])
    if bool(entry.get("allow_outside_bounds", False)):
        command.append("--allow-outside-bounds")
    run(command, family_dir / "logs/generate.log")


def neutral_audit(entry: dict[str, Any], family_dir: Path, textures: Path) -> dict[str, Any]:
    family = str(entry["family_id"])
    source_render = family_dir / "neutral_source.png"
    roundtrip_render = family_dir / "neutral_glb_roundtrip.png"
    glb = family_dir / f"{family}_assembled.glb"
    for kind, source, destination in (
        ("blend", family_dir / f"{family}.blend", source_render),
        ("glb", glb, roundtrip_render),
    ):
        run([
            str(BLENDER), "--background", "--factory-startup",
            "--python", str(TOOLS / "blender_render_neutral_parity.py"),
            "--", "--input", str(source), "--kind", kind, "--output", str(destination),
        ], family_dir / f"logs/neutral-{kind}.log")
    audit_path = family_dir / "surface_finish_report.json"
    run([
        sys.executable,
        str(TOOLS / "surface_finish_quality.py"),
        "--grammar", str(family_dir / "grammar.json"),
        "--story-manifest", str(textures / "surface-story-manifest.json"),
        "--glb", str(glb),
        "--source-render", str(source_render),
        "--roundtrip-render", str(roundtrip_render),
        "--output", str(audit_path),
    ], family_dir / "logs/surface-finish.log", allow_failure=True)
    return read_json(audit_path)


def assess_quality(family_dir: Path) -> dict[str, Any]:
    manifests = [path for path in family_dir.glob("*_manifest.json") if path.name != "manifest.json"]
    if not manifests:
        raise RuntimeError("family manifest missing after generation")
    manifest = read_json(manifests[0])
    validation = read_json(family_dir / "validation_report.json")
    approval_path = family_dir / "visual_approval.json"
    visual_approval = read_json(approval_path) if approval_path.exists() else None
    assessment = assess_family_quality(
        manifest,
        validation,
        load_quality_memory(),
        visual_approval=visual_approval,
    )
    (family_dir / "quality_assessment.json").write_text(
        json.dumps(assessment, indent=2) + "\n", encoding="utf-8"
    )
    return assessment


def write_index(path: Path, registry: dict[str, Any], results: list[dict[str, Any]]) -> None:
    summary = Counter(item["machine_status"] for item in results)
    payload = {
        "schema": "catalogue-rollout-batch-index@1",
        "batch_id": registry["batch_id"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "requested": len(registry["entries"]),
        "results": results,
        "summary": dict(sorted(summary.items())),
        "checkpoint_state": "human_review_required" if results and not summary.get("failed") else "repair_required",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--grammar-only", action="store_true")
    parser.add_argument("--skip-textures", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--minimum-free-gb", type=float, default=15.0)
    args = parser.parse_args()

    registry = read_json(args.registry.resolve())
    validate_registry(registry)
    output_root = args.output.resolve()
    require_capacity(output_root, args.minimum_free_gb)
    textures = output_root / "textures"
    if not args.skip_textures and not args.grammar_only:
        recipe_manifest = registry.get("surface_recipe_manifest")
        derive_textures(
            textures,
            (REPO / str(recipe_manifest)).resolve() if recipe_manifest else None,
            str(registry.get("pipeline_version") or "v86"),
        )
    elif not args.grammar_only and not (textures / "surface-story-manifest.json").exists():
        raise SystemExit("--skip-textures requires an existing V86 surface-story manifest")

    batch_root = output_root / str(registry["batch_id"]).lower()
    batch_root.mkdir(parents=True, exist_ok=True)
    index_path = batch_root / "batch-index.json"
    previous = read_json(index_path) if index_path.exists() else {"results": []}
    previous_by_family = {item["family_id"]: item for item in previous.get("results") or []}
    results: list[dict[str, Any]] = []

    for number, entry in enumerate(registry["entries"], 1):
        family = str(entry["family_id"])
        family_dir = batch_root / family
        prior = previous_by_family.get(family)
        if prior and prior.get("machine_status") == "pass" and not args.force and not args.grammar_only:
            print(f"[catalogue-v86] [{number}/{len(registry['entries'])}] resume skip {family}")
            results.append(prior)
            continue
        print(f"[catalogue-v86] [{number}/{len(registry['entries'])}] {family}", flush=True)
        result = {
            "archetype_id": entry["archetype_id"],
            "variant_id": entry["variant_id"],
            "family_id": family,
            "output_directory": str(family_dir.relative_to(REPO)).replace("\\", "/"),
            "machine_status": "pending",
            "human_status": "unreviewed",
        }
        try:
            generate(entry, family_dir, textures, args.grammar_only)
            if args.grammar_only:
                preflight = read_json(family_dir / "production_preflight.json")
                result.update({"machine_status": "preflight_pass", "production_preflight": preflight["status"]})
            else:
                finish = neutral_audit(entry, family_dir, textures)
                validation = read_json(family_dir / "validation_report.json")
                quality = assess_quality(family_dir)
                machine_pass = validation.get("status") == "pass" and finish.get("status") == "pass"
                result.update({
                    "machine_status": "pass" if machine_pass else "failed",
                    "validation": validation.get("status"),
                    "surface_finish": finish.get("status"),
                    "foreground_similarity": (finish.get("render_parity") or {}).get("similarity"),
                    "quality_memory_status": quality.get("status"),
                })
        except Exception as exc:
            result.update({"machine_status": "failed", "error": str(exc)})
        results.append(result)
        write_index(index_path, registry, results)

    write_index(index_path, registry, results)
    return 1 if any(item["machine_status"] == "failed" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
