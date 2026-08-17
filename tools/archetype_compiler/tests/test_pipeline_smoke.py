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
from PIL import Image, ImageStat

TOOL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_DIR.parents[1]
FRONTEND = REPO_ROOT / "frontend"

sys.path.insert(0, str(TOOL_DIR))

from blender_locator import BlenderNotFoundError, find_blender  # noqa: E402
from compiler import compile_archetype  # noqa: E402

NPX = shutil.which("npx") or shutil.which("npx.cmd")
HAS_NODE_DEPS = NPX is not None and (FRONTEND / "node_modules" / ".bin").exists()
MACHIYA_DELIVERY = (
    REPO_ROOT
    / "seed"
    / "model-library"
    / "objects"
    / "lego"
    / "651daf60-b797-4f95-b1e7-6364d6dc0665"
    / "restored-kyoto-machiya"
    / "assembled--default--lod0.glb"
)
HAS_MACHIYA_DELIVERY = MACHIYA_DELIVERY.is_file() and MACHIYA_DELIVERY.stat().st_size >= 200

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


@pytest.mark.skipif(
    not (BLENDER and HAS_MACHIYA_DELIVERY),
    reason="needs Blender and the hydrated restored Machiya delivery GLB",
)
def test_delivery_glb_renders_grounded_locked_camera_evidence(tmp_path: Path):
    review_dir = tmp_path / "delivery-review"
    result = subprocess.run(
        [
            BLENDER,
            "--background",
            "--factory-startup",
            "--python",
            str(TOOL_DIR / "render_delivery_glb.py"),
            "--",
            "--input",
            str(MACHIYA_DELIVERY),
            "--output-dir",
            str(review_dir),
            "--family",
            "restored-kyoto-machiya",
            "--resolution-x",
            "320",
            "--resolution-y",
            "240",
            "--samples",
            "1",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-2000:]

    review = json.loads((review_dir / "delivery-review.json").read_text(encoding="utf-8"))
    assert review["schema"] == "cityprompt-delivery-glb-review@1"
    assert review["family"] == "restored-kyoto-machiya"
    assert review["blender_version"]
    assert review["mesh_objects"] > 0
    assert review["ground_delta_m"] == pytest.approx(0.0, abs=0.02)
    assert review["bounds"]["dimensions"] == pytest.approx(
        [19.77, 16.77, 11.57],
        abs=0.02,
    )
    assert {item["role"] for item in review["views"]} == {
        "front",
        "front_corner",
        "rear_corner",
        "aerial",
    }

    for item in review["views"]:
        image_path = review_dir / item["path"]
        with Image.open(image_path) as rendered:
            assert rendered.size == (320, 240)
            assert ImageStat.Stat(rendered.convert("L")).stddev[0] > 5
