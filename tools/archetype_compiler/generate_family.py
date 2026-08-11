"""One-command archetype -> modular GLB family pipeline.

    python tools/archetype_compiler/generate_family.py --archetype-id nordic_timber_midrise

Steps: export the real catalogue entry (vite-node) -> compile Building Grammar ->
discover Blender -> generate GLB modules + assembled preview + thumbnail headlessly ->
validate outputs -> print the output folder. Exits non-zero on any failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252 and crash/garble on the catalogue's unicode dashes
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"

sys.path.insert(0, str(TOOL_DIR))

from blender_locator import BlenderNotFoundError, find_blender  # noqa: E402
from compiler import compile_archetype  # noqa: E402
from pipeline_preflight import assess_generation_preflight  # noqa: E402
from signature_profiles import inject_signature  # noqa: E402


class StepFailed(SystemExit):
    def __init__(self, step: str, detail: str):
        super().__init__(f"\n[generate_family] FAILED at step '{step}':\n{detail}")


def log(message: str) -> None:
    print(f"[generate_family] {message}", flush=True)


def run(cmd: list[str], *, cwd: Path, step: str, log_file: Path | None = None) -> subprocess.CompletedProcess:
    log(f"$ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")
    combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text((result.stdout or "") + "\n--- stderr ---\n" + (result.stderr or ""), encoding="utf-8")
    # Blender may return process code zero even when its Python entry point
    # raises. Treat the embedded traceback/argparse failure as authoritative;
    # otherwise a stale GLB and manifest can make validation report a false
    # pass after the renderer has actually failed.
    blender_python_failed = step == "blender" and (
        "Traceback (most recent call last)" in combined_output
        or "blender_generate.py: error:" in combined_output
    )
    if result.returncode != 0 or blender_python_failed:
        tail = "\n".join(combined_output.strip().splitlines()[-25:])
        where = f" (full log: {log_file})" if log_file else ""
        reason = f"exit code {result.returncode}" if result.returncode != 0 else "embedded Python failure"
        raise StepFailed(step, f"{reason}{where}\n{tail}")
    return result


def export_archetype(archetype_id: str, variant_id: str | None, out_file: Path) -> dict:
    if not FRONTEND_DIR.joinpath("node_modules", ".bin").exists():
        raise StepFailed(
            "export",
            f"frontend dependencies are not installed ({FRONTEND_DIR / 'node_modules'} missing).\n"
            f"Run:  cd {FRONTEND_DIR} && npm install\n"
            f"(or use scripts/generate-archetype-family.ps1 which does this for you)",
        )
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise StepFailed("export", "npx not found — install Node.js 18+ from https://nodejs.org")

    cmd = [npx, "vite-node", str(TOOL_DIR / "export_catalog.ts"), "--",
           "--archetype-id", archetype_id, "--output", str(out_file)]
    if variant_id:
        cmd += ["--variant-id", variant_id]
    run(cmd, cwd=FRONTEND_DIR, step="export")
    if not out_file.exists():
        raise StepFailed("export", f"exporter reported success but {out_file} does not exist")
    return json.loads(out_file.read_text(encoding="utf-8"))


def ensure_validation_deps(auto_install: bool) -> bool:
    if importlib.util.find_spec("trimesh") is not None:
        return True
    if not auto_install:
        return False
    log(f"installing validation dependencies (trimesh, numpy) into {sys.executable}")
    log("(pass --no-auto-install to manage packages yourself)")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        log(f"WARNING: pip install failed:\n{result.stderr[-800:]}")
        return False
    importlib.invalidate_caches()
    return importlib.util.find_spec("trimesh") is not None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a modular GLB family from a real catalogue archetype")
    parser.add_argument("--archetype-id", required=True, help="catalogue id, e.g. nordic_timber_midrise (see export_catalog.ts --list)")
    parser.add_argument("--variant-id", default=None)
    parser.add_argument(
        "--family-id",
        default=None,
        help=(
            "override the generated kebab-case LEGO family id; use this for "
            "coexisting footprint tiers such as nordic-timber-midrise-large"
        ),
    )
    parser.add_argument("--output", type=Path, default=None, help="default: build/archetypes/<archetype-id>")
    parser.add_argument("--floors", type=int, default=None, help="assembled preview floor count (default: catalogue midpoint)")
    parser.add_argument("--width", type=float, default=None)
    parser.add_argument("--depth", type=float, default=None)
    parser.add_argument(
        "--allow-outside-bounds",
        action="store_true",
        help="author an explicit footprint tier outside catalogue recommendations",
    )
    parser.add_argument("--footprint-profile", choices=("rectangle", "l_shape", "u_shape", "courtyard"), default="rectangle",
                        help="assembled-preview geographic footprint profile")
    parser.add_argument("--footprint-width", type=float, default=None,
                        help="overall assembled footprint width; module width still comes from --width")
    parser.add_argument("--footprint-depth", type=float, default=None,
                        help="overall assembled footprint depth; module depth still comes from --depth")
    parser.add_argument("--wing-depth", type=float, default=None,
                        help="occupied wing thickness for non-rectangular profiles")
    parser.add_argument("--blender-path", default=None)
    parser.add_argument("--skip-thumbnail", action="store_true")
    parser.add_argument(
        "--assembled-only", action="store_true",
        help="reuse existing module files/metadata and rebuild only the assembled model and review images",
    )
    parser.add_argument("--keep-blend", action="store_true")
    parser.add_argument("--no-ao", action="store_true", help="skip the Cycles AO bake (fast runs)")
    parser.add_argument("--facade-sheets", type=Path, default=None,
                        help="facade-sheet directory created by generate_facade_sheets.py")
    parser.add_argument("--facade-sheet-detail", choices=("hero", "city"), default="hero")
    parser.add_argument("--textures", type=Path, default=None,
                        help="texture library root (default: tools/archetype_compiler/textures)")
    parser.add_argument("--presentation-engine", choices=("eevee", "cycles"), default="eevee",
                        help="review-image renderer; use cycles for final archviz QA")
    parser.add_argument("--presentation-samples", type=int, default=48)
    parser.add_argument("--presentation-view-set", choices=("all", "preview"), default="all")
    parser.add_argument("--clay-mode", action="store_true",
                        help="render the massing graph without sticker assemblies for geometry approval")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--no-auto-install", action="store_true", help="don't pip-install validation deps automatically")
    parser.add_argument(
        "--grammar-only",
        action="store_true",
        help="export the catalogue entry and write grammar.json, then stop before Blender generation",
    )
    parser.add_argument(
        "--prototype",
        action="store_true",
        help=(
            "write production_preflight.json but continue after failed production gates; "
            "never use for catalogue release"
        ),
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    default_dirname = f"{args.archetype_id}--{args.variant_id}" if args.variant_id else args.archetype_id
    output = (args.output or REPO_ROOT / "build" / "archetypes" / default_dirname).resolve()
    output.mkdir(parents=True, exist_ok=True)
    logs_dir = output / "logs"

    # 1. export the real catalogue entry ------------------------------------
    log(f"step 1/5: exporting archetype '{args.archetype_id}' from the catalogue")
    source_file = output / "archetype-source.json"
    payload = export_archetype(args.archetype_id, args.variant_id, source_file)
    log(f"exported: {payload.get('archetypeLabel')} ({payload.get('developmentType')}, "
        f"{payload.get('aestheticCategoryId')})")

    # 2. compile grammar ------------------------------------------------------
    log("step 2/5: compiling Building Grammar")
    try:
        grammar = compile_archetype(
            payload,
            floors=args.floors,
            width_m=args.width,
            depth_m=args.depth,
            allow_outside_bounds=args.allow_outside_bounds,
        )
    except Exception as exc:
        raise StepFailed("compile", str(exc))
    if args.family_id:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.family_id):
            raise StepFailed("compile", f"--family-id must be a kebab-case slug, got {args.family_id!r}")
        grammar.family_id = args.family_id
        grammar.validate()
    grammar_file = output / "grammar.json"
    grammar_payload = inject_signature(
        grammar.to_dict(), args.archetype_id, variant_id=args.variant_id,
    )
    if payload.get("footprintCompatibility"):
        grammar_payload["footprint_compatibility"] = payload["footprintCompatibility"]
    else:
        placement = (
            (grammar_payload.get("architectural_signature") or {})
            .get("production_contract", {})
            .get("placement_contract") or {}
        )
        if placement.get("mode") == "fixed_landmark":
            fixed = placement.get("footprint_m") or {}
            grammar_payload["footprint_compatibility"] = {
                "preferredProfiles": ["fixed_landmark"],
                "placementMode": "select_and_place",
                "fixedDimensions": {
                    "width": float(fixed.get("width", grammar_payload["dimensions"]["width_m"])),
                    "depth": float(fixed.get("depth", grammar_payload["dimensions"]["depth_m"])),
                },
                "polygonFit": False,
            }
    grammar_file.write_text(json.dumps(grammar_payload, indent=2), encoding="utf-8")
    preflight = assess_generation_preflight(payload, grammar_payload)
    preflight_file = output / "production_preflight.json"
    preflight_file.write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
    if preflight["status"] != "pass":
        details = "\n".join(
            f"- {finding['id']}: {finding['detail']}" for finding in preflight["failures"]
        )
        if not args.prototype:
            raise StepFailed(
                "production-preflight",
                f"paid generation is blocked; see {preflight_file}\n{details}",
            )
        log(f"PROTOTYPE ONLY — production preflight failed:\n{details}")
    else:
        log(f"production preflight: PASS ({preflight['identity_mode']})")
    dims = grammar.dimensions
    log(f"grammar: {grammar.family_id} — {dims.width_m}x{dims.depth_m} m, "
        f"{dims.default_floors} floors, roof={grammar.roof.type}, retail={grammar.massing.has_podium_retail}")
    if args.verbose:
        for note in grammar.notes:
            log(f"  note: {note}")

    if args.grammar_only:
        log("")
        log("SUCCESS — catalogue source and Building Grammar prepared (--grammar-only)")
        log(f"  family:        {grammar.family_id}")
        log(f"  archetype:     {args.archetype_id}")
        log(f"  grammar:       {grammar_file}")
        log(f"  output folder: {output}")
        print(str(output))
        return

    # 3. locate Blender -------------------------------------------------------
    log("step 3/5: locating Blender")
    try:
        blender = find_blender(args.blender_path)
    except BlenderNotFoundError as exc:
        raise StepFailed("blender-discovery", str(exc))
    log(f"blender: {blender}")

    # 4. run Blender headless -------------------------------------------------
    log("step 4/5: generating GLB modules in Blender (headless)")
    blender_cmd = [
        blender, "--background", "--factory-startup",
        "--python", str(TOOL_DIR / "blender_generate.py"), "--",
        "--grammar", str(grammar_file), "--output", str(output),
    ]
    if args.floors:
        blender_cmd += ["--floors", str(args.floors)]
    if args.keep_blend:
        blender_cmd += ["--keep-blend"]
    if args.skip_thumbnail:
        blender_cmd += ["--no-thumbnail"]
    if args.assembled_only:
        blender_cmd += ["--assembled-only"]
    if args.no_ao:
        blender_cmd += ["--no-ao"]
    if args.clay_mode:
        blender_cmd += ["--clay-mode"]
    if args.facade_sheets:
        blender_cmd += ["--facade-sheets", str(args.facade_sheets.resolve()),
                        "--facade-sheet-detail", args.facade_sheet_detail]
    if args.textures:
        blender_cmd += ["--textures", str(args.textures.resolve())]
    blender_cmd += ["--presentation-engine", args.presentation_engine,
                    "--presentation-samples", str(args.presentation_samples),
                    "--presentation-view-set", args.presentation_view_set,
                    "--footprint-profile", args.footprint_profile]
    if args.footprint_width is not None:
        blender_cmd += ["--footprint-width", str(args.footprint_width)]
    if args.footprint_depth is not None:
        blender_cmd += ["--footprint-depth", str(args.footprint_depth)]
    if args.wing_depth is not None:
        blender_cmd += ["--wing-depth", str(args.wing_depth)]
    result = run(blender_cmd, cwd=REPO_ROOT, step="blender", log_file=logs_dir / "blender.log")
    for line in (result.stdout or "").splitlines():
        if "[blender_generate]" in line:
            log(f"  {line.strip()}")

    manifest_file = output / f"{grammar.family_id}_manifest.json"
    if not manifest_file.exists():
        raise StepFailed("blender", f"Blender exited 0 but manifest {manifest_file.name} was not written "
                                    f"(see {logs_dir / 'blender.log'})")

    # 5. validate --------------------------------------------------------------
    if args.skip_validation:
        log("step 5/5: validation SKIPPED (--skip-validation)")
    else:
        log("step 5/5: validating outputs")
        if not ensure_validation_deps(auto_install=not args.no_auto_install):
            raise StepFailed(
                "validate",
                "trimesh is not installed and auto-install failed/disabled.\n"
                f"Install with: {sys.executable} -m pip install -r {TOOL_DIR / 'requirements.txt'}\n"
                "Or re-run with --skip-validation (not recommended).",
            )
        validate_cmd = [sys.executable, str(TOOL_DIR / "validate_outputs.py"), str(output), "--grammar", str(grammar_file)]
        result = subprocess.run(validate_cmd, text=True)
        if result.returncode != 0:
            raise StepFailed("validate", f"validation failed — see {output / 'validation_report.json'}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    log("")
    log("SUCCESS — family generated and validated")
    log(f"  family:        {manifest['family']}")
    log(f"  archetype:     {manifest['archetype_id']} ({manifest.get('archetype_label')})")
    log(f"  reuse keys:    {manifest.get('reuse_keys')}")
    log(f"  modules:       {[m['filename'] for m in manifest['modules']]}")
    if manifest.get("assembled"):
        log(f"  assembled:     {manifest['assembled']['filename']} "
            f"({manifest['assembled']['floors']} floors, {manifest['assembled']['height_m']} m)")
    if manifest.get("thumbnail"):
        log(f"  preview image: {output / manifest['thumbnail']}")
    log(f"  output folder: {output}")
    print(str(output))


if __name__ == "__main__":
    main()
