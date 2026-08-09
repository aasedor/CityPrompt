"""Run the bounded three-new-archetype V85 pilot batch."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools/archetype_compiler"
ARTIFACTS = REPO / "artifacts/three-new-archetypes-v85"
TEXTURES = ARTIFACTS / "textures"
BLENDER = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")

PILOTS = {
    "brownstone": {
        "archetype": "classic_brownstone_streetwall",
        "variant": "classic_brownstone_traditional",
        "family": "classic-brownstone-traditional-v85",
        "width": 25.2,
        "depth": 19.0,
        "floors": 4,
        "facade": TOOLS / "facade_sheets_v8/classic-brownstone-streetwall",
    },
    "glass_office": {
        "archetype": "modern_glass_office_institutional",
        "variant": "glass_office_blue_curtainwall",
        "family": "blue-curtainwall-office-v85",
        "width": 30.0,
        "depth": 20.0,
        "floors": 10,
        "facade": TOOLS / "facade_sheets_v8/modern-glass-office-institutional",
    },
    "nordic_timber": {
        "archetype": "nordic_timber_midrise",
        "variant": "nordic_timber_mass_timber",
        "family": "nordic-mass-timber-midrise-v85",
        "width": 20.0,
        "depth": 16.0,
        "floors": 7,
        "facade": TOOLS / "facade_sheets_v8/nordic-timber-midrise",
    },
}


def run(command: list[str], *, allow_failure: bool = False) -> int:
    print("[v85] $", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=REPO, check=False)
    if result.returncode and not allow_failure:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.returncode


def derive_textures() -> None:
    run([
        sys.executable,
        str(TOOLS / "derive_surface_story_pbr.py"),
        "--source-root", str(TOOLS / "textures"),
        "--additional-source-root", str(TOOLS / "textures_worldclass_v7"),
        "--output-root", str(TEXTURES),
        "--size", "1024",
        "--pipeline-version", "v85",
    ])


def generate(pilot: dict, *, grammar_only: bool) -> Path:
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
    # A failed parity audit is a reviewed pilot outcome, not a reason to skip
    # the remaining new archetypes in this finite batch.
    run([
        sys.executable,
        str(TOOLS / "surface_finish_quality.py"),
        "--grammar", str(output / "grammar.json"),
        "--story-manifest", str(TEXTURES / "surface-story-manifest.json"),
        "--glb", str(glb),
        "--source-render", str(source_render),
        "--roundtrip-render", str(roundtrip_render),
        "--output", str(output / "surface_finish_report.json"),
    ], allow_failure=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", choices=("all", *PILOTS), default="all")
    parser.add_argument("--grammar-only", action="store_true")
    parser.add_argument("--skip-textures", action="store_true")
    parser.add_argument("--skip-neutral-audit", action="store_true")
    args = parser.parse_args()
    if not args.skip_textures:
        derive_textures()
    selected = PILOTS.items() if args.pilot == "all" else [(args.pilot, PILOTS[args.pilot])]
    for name, pilot in selected:
        print(f"[v85] starting {name}", flush=True)
        output = generate(pilot, grammar_only=args.grammar_only)
        if not args.grammar_only and not args.skip_neutral_audit:
            neutral_and_audit(pilot, output)


if __name__ == "__main__":
    main()
