import hashlib
import json
from pathlib import Path

import pytest

from tools.public_realm_assets.stage_street_pilots import inspect_pilot, stage


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _package(root: Path) -> Path:
    root.mkdir()
    (root / "modules").mkdir()
    (root / "references").mkdir()
    assembly = b"preview-only"
    module = b"rigid-furniture"
    reference = b"source-image"
    (root / "assembly-preview.glb").write_bytes(assembly)
    (root / "modules" / "bench.glb").write_bytes(module)
    (root / "references" / "reference.png").write_bytes(reference)
    recipe = {
        "id": "student_main_street_v1", "title": "Pilot", "runtime_approved": False,
        "reference": "neighborhood-main-street/hero.png",
        "dimensions_m": [10, 48], "fixed_width_m": 10, "fixture_length_m": 48,
        "pattern": "stone", "sections": [
            {"name": "walk", "x": -3, "width": 4, "material": "paving"},
            {"name": "road", "x": 2, "width": 6, "material": "asphalt"},
        ],
        "placements": [{"kind": "bench", "x": -3, "y": 4, "yaw": 0}],
        "tree_wells": [],
        "assembly": {"path": "assembly-preview.glb", "bytes": len(assembly), "sha256": _sha(assembly)},
        "modules": {"bench": {"path": "bench.glb", "bytes": len(module), "sha256": _sha(module)}},
        "image_references": [{"path": "references/reference.png", "bytes": len(reference), "sha256": _sha(reference)}],
    }
    (root / "recipe.json").write_text(json.dumps(recipe), encoding="utf-8")
    return root


def test_staging_excludes_preview_and_locks_component_bytes(tmp_path):
    package = _package(tmp_path / "package")
    public = tmp_path / "public"
    manifest = tmp_path / "pilots.json"
    rows = stage([package], public, manifest, dry_run=True)
    assert rows[0]["status"] == "candidate"
    assert not public.exists() and not manifest.exists()
    rows = stage([package], public, manifest, dry_run=False)
    assert rows[0]["widthM"] == 10
    assert rows[0]["sourceArchetypeId"] == "neighborhood_main_street"
    staged = public / "street-kits" / "pilots" / rows[0]["id"]
    assert (staged / "bench.glb").read_bytes() == b"rigid-furniture"
    assert not (staged / "assembly-preview.glb").exists()
    assert json.loads(manifest.read_text())[0]["sourceAssemblySha256"] == _sha(b"preview-only")
    stage([package], public, manifest, dry_run=False)
    assert len(json.loads(manifest.read_text())) == 1


def test_staging_rejects_changed_bytes_and_misaligned_bands(tmp_path):
    package = _package(tmp_path / "package")
    (package / "modules" / "bench.glb").write_bytes(b"modified")
    with pytest.raises(ValueError, match="changed"):
        inspect_pilot(package)
    (package / "modules" / "bench.glb").write_bytes(b"rigid-furniture")
    recipe_path = package / "recipe.json"
    recipe = json.loads(recipe_path.read_text())
    recipe["sections"][1]["x"] = 2.2
    recipe_path.write_text(json.dumps(recipe))
    with pytest.raises(ValueError, match="tile the exact width"):
        inspect_pilot(package)


def test_staging_rejects_unreviewed_identity_and_unknown_tree_pair(tmp_path):
    package = _package(tmp_path / "package")
    recipe_path = package / "recipe.json"
    recipe = json.loads(recipe_path.read_text())
    recipe["id"] = "../unregistered_street"
    recipe_path.write_text(json.dumps(recipe))
    with pytest.raises(ValueError, match="student street pilot"):
        inspect_pilot(package)
    recipe["id"] = "student_main_street_v1"
    recipe["tree_wells"] = [{"x": -3, "y": 4, "width": 1, "depth": 1,
                             "style": "unknown", "tree_kind": "grove_tree"}]
    recipe_path.write_text(json.dumps(recipe))
    with pytest.raises(ValueError, match="native module|hardscape tree"):
        inspect_pilot(package)


def test_staging_requires_explicit_replacement_for_changed_candidate_metadata(tmp_path):
    package = _package(tmp_path / "package")
    public = tmp_path / "public"
    manifest = tmp_path / "pilots.json"
    stage([package], public, manifest, dry_run=False)
    recipe_path = package / "recipe.json"
    recipe = json.loads(recipe_path.read_text())
    recipe["title"] = "Revised candidate"
    recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
    with pytest.raises(ValueError, match="silently replace"):
        stage([package], public, manifest, dry_run=True)
    stage([package], public, manifest, dry_run=False, replace=True)
    assert json.loads(manifest.read_text())[0]["title"] == "Revised candidate"
