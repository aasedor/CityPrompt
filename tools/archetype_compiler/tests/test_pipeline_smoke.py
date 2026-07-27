"""End-to-end smoke tests: real catalogue export -> grammar -> (optional) Blender.

The export stage needs Node + frontend/node_modules; the generation stage needs
Blender. Each stage is skipped (not failed) when its tool is unavailable, so the
unit-test suite stays green on CI boxes without those tools.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_DIR.parents[1]
FRONTEND = REPO_ROOT / "frontend"

sys.path.insert(0, str(TOOL_DIR))

from blender_locator import BlenderNotFoundError, find_blender  # noqa: E402
from compiler import compile_archetype  # noqa: E402

NPX = shutil.which("npx") or shutil.which("npx.cmd")
HAS_NODE_DEPS = NPX is not None and (FRONTEND / "node_modules" / ".bin").exists()

try:
    BLENDER = find_blender()
except BlenderNotFoundError:
    BLENDER = None


@pytest.mark.skipif(not HAS_NODE_DEPS, reason="needs npx + frontend/node_modules for the catalogue exporter")
def test_export_real_archetype_and_compile(tmp_path: Path):
    out = tmp_path / "source.json"
    result = subprocess.run(
        [NPX, "vite-node", str(TOOL_DIR / "export_catalog.ts"), "--",
         "--archetype-id", "nordic_timber_midrise", "--output", str(out)],
        cwd=str(FRONTEND), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr[-800:]
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["archetypeId"] == "nordic_timber_midrise"
    assert payload["generationStyleInput"]["downstreamHints"]["reuseKeys"]

    grammar = compile_archetype(payload)
    assert grammar.source.archetype_id == "nordic_timber_midrise"
    assert "nordic_timber_midrise" in grammar.source.reuse_keys
    assert grammar.dimensions.width_m == 20
    assert grammar.roof.green_roof is True
    # charred timber primary derived from real facadeDetail prose
    assert grammar.materials.primary.base_color == "#2e2a26"


@pytest.mark.skipif(
    not (HAS_NODE_DEPS and BLENDER), reason="needs Blender + node deps for the full pipeline"
)
def test_full_pipeline_generates_validated_family(tmp_path: Path):
    out_dir = tmp_path / "family"
    result = subprocess.run(
        [sys.executable, str(TOOL_DIR / "generate_family.py"),
         "--archetype-id", "nordic_timber_midrise", "--output", str(out_dir),
         "--floors", "6", "--skip-thumbnail"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-1500:]

    manifest = json.loads(next(out_dir.glob("*_manifest.json")).read_text(encoding="utf-8"))
    roles = {m["role"] for m in manifest["modules"]}
    assert {"podium", "floor", "setback", "roof"} <= roles
    assert manifest["archetype_id"] == "nordic_timber_midrise"
    assert manifest["reuse_keys"]
    assert manifest["assembled"]["floors"] == 6
    assert (out_dir / manifest["assembled"]["filename"]).exists()

    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "pass", report["errors"]
