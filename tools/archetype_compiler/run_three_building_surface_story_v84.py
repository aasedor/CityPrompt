"""Run the bounded three-building V84 surface-story validation batch."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools/archetype_compiler"
ARTIFACTS = REPO / "artifacts/three-building-surface-story-v84"
TEXTURES = ARTIFACTS / "textures"
BLENDER = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")

PILOTS = {
    "courthouse": {
        "archetype": "monumental_courthouse_axis",
        "variant": "courthouse_neoclassical_temple",
        "family": "courthouse-neoclassical-surface-story-v84",
        "width": 60,
        "depth": 35,
        "floors": 3,
        "facade": TOOLS / "facade_sheets_v8/monumental-courthouse-axis",
    },
    "portici": {
        "archetype": "mediterranean_arcade_mixed_use",
        "variant": "med_arcade_italian_portici",
        "family": "mediterranean-portici-surface-story-v84",
        "width": 20,
        "depth": 16,
        "floors": 4,
        "facade": TOOLS / "facade_sheets_v8/mediterranean-arcade-mixed-use",
    },
    "warehouse": {
        "archetype": "romanesque_revival_warehouse",
        "variant": "warehouse_arch_window_brick",
        "family": "romanesque-warehouse-surface-story-v84",
        "width": 40,
        "depth": 40,
        "floors": 5,
        "facade": TOOLS / "facade_sheets_v8/romanesque-revival-warehouse",
    },
}


def run(command: list[str]) -> None:
    print("[v84] $", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO, check=True)


def derive_textures() -> None:
    run([
        sys.executable,
        str(TOOLS / "derive_surface_story_pbr.py"),
        "--source-root", str(TOOLS / "textures"),
        "--additional-source-root", str(TOOLS / "textures_worldclass_v7"),
        "--output-root", str(TEXTURES),
        "--size", "1024",
        "--pipeline-version", "v84",
    ])


def generate(pilot: dict, *, grammar_only: bool, assembled_only: bool) -> Path:
    output = ARTIFACTS / str(pilot["family"])
    command = [
        sys.executable,
        str(TOOLS / "generate_family.py"),
        "--archetype-id", str(pilot["archetype"]),
        "--variant-id", str(pilot["variant"]),
        "--family-id", str(pilot["family"]),
        "--output", str(output),
        "--width", str(pilot["width"]),
        "--depth", str(pilot["depth"]),
        "--floors", str(pilot["floors"]),
        "--textures", str(TEXTURES),
        "--facade-sheets", str(pilot["facade"]),
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
        if assembled_only:
            command.append("--assembled-only")
    run(command)
    return output


def neutral_and_audit(pilot: dict, output: Path) -> None:
    family = str(pilot["family"])
    source = output / f"{family}.blend"
    glb = output / f"{family}_assembled.glb"
    source_render = output / "neutral_source.png"
    roundtrip_render = output / "neutral_glb_roundtrip.png"
    for kind, input_path, render_path in (
        ("blend", source, source_render),
        ("glb", glb, roundtrip_render),
    ):
        run([
            str(BLENDER), "--background", "--factory-startup",
            "--python", str(TOOLS / "blender_render_neutral_parity.py"),
            "--", "--input", str(input_path), "--kind", kind,
            "--output", str(render_path),
        ])
    run([
        sys.executable,
        str(TOOLS / "surface_finish_quality.py"),
        "--grammar", str(output / "grammar.json"),
        "--story-manifest", str(TEXTURES / "surface-story-manifest.json"),
        "--glb", str(glb),
        "--source-render", str(source_render),
        "--roundtrip-render", str(roundtrip_render),
        "--output", str(output / "surface_finish_report.json"),
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", choices=("all", *PILOTS), default="all")
    parser.add_argument("--grammar-only", action="store_true")
    parser.add_argument("--assembled-only", action="store_true")
    parser.add_argument("--skip-textures", action="store_true")
    parser.add_argument("--skip-neutral-audit", action="store_true")
    args = parser.parse_args()
    if not args.skip_textures:
        derive_textures()
    selected = PILOTS.items() if args.pilot == "all" else [(args.pilot, PILOTS[args.pilot])]
    for name, pilot in selected:
        print(f"[v84] starting {name}", flush=True)
        output = generate(pilot, grammar_only=args.grammar_only, assembled_only=args.assembled_only)
        if not args.grammar_only and not args.skip_neutral_audit:
            neutral_and_audit(pilot, output)


if __name__ == "__main__":
    main()
