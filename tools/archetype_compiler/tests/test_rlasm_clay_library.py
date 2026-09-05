"""Read-only verification of activated clay fixtures; no assets are promoted."""

import copy
import os
from pathlib import Path
import uuid

import pytest
import trimesh

from tools.rlasm_clay_library import _validate_payload, clay_seed_objects, clay_seed_rows, load_library


@pytest.fixture(scope="module")
def source_library():
    source = os.environ.get("CITYPROMPT_CLAY_FIXTURE_ROOT")
    if not source:
        pytest.skip("Set CITYPROMPT_CLAY_FIXTURE_ROOT to the reviewed read-only seed repository")
    root = Path(source).resolve()
    clay_root = root / "seed/model-library/rlasm-architectural-clay"
    return root, clay_root, load_library(clay_root / "library.json", repo_root=root)


def test_ten_activated_variants_keep_source_hashes_and_native_geometry(source_library):
    root, clay_root, payload = source_library
    rows = list(clay_seed_rows(payload))
    objects = list(clay_seed_objects(payload, clay_root=clay_root))
    assert len(rows) == len(objects) == len(payload["entries"]) == 10
    assert len({row["id"] for row in rows}) == 10
    for entry, row, item in zip(payload["entries"], rows, objects):
        assert uuid.UUID(row["id"]).version == 5
        assert item.source.parent == clay_root / "models"
        assert row["is_public"] is True
        assert row["thumbnail_url"] == next(ref["repo_path"] for ref in entry["references"] if ref["role"] == "front").removeprefix("frontend/public")
        assert all((root / ref["repo_path"]).is_file() for ref in entry["references"])
        assert row["metadata"]["rlasm"]["keeper_approved"] is False
        assert row["metadata"]["rlasm"]["design_dimensions_m"] == entry["design_dimensions_m"]
        lego = row["metadata"]["lego"]
        assert lego["source_variant_id"] == entry["variant_id"]
        assert lego["native_floors"] == lego["min_floors"] == lego["max_floors"] == entry["native_floors"]
        assert lego["repeatable_z"] is False
        assert lego["placement_contract"]["continuous_resize_allowed"] is False
        scene = trimesh.load(item.source, force="scene", process=False)
        assert [lego["width_m"], lego["height_m"], lego["depth_m"]] == pytest.approx(scene.extents, abs=1e-4)
        assert entry["model"]["image_count"] == entry["model"]["texture_count"] == 0


def test_design_dimensions_never_replace_larger_actual_model_envelope(source_library):
    _, _, payload = source_library
    special = payload["entries"][0]
    row = next(clay_seed_rows({**payload, "entries": [special]}))
    lego = row["metadata"]["lego"]
    assert lego["width_m"] == special["model"]["native_dimensions_m"]["width"]
    assert lego["depth_m"] > special["design_dimensions_m"]["depth"]


@pytest.mark.parametrize("axis,bad", [("width", 1.0), ("depth", float("nan")), ("height", 0.0)])
def test_loader_rejects_incorrect_native_bounds_before_producing_rows(source_library, axis, bad):
    root, clay_root, source = source_library
    payload = copy.deepcopy(source)
    payload["entries"][0]["model"]["native_dimensions_m"][axis] = bad
    with pytest.raises(ValueError, match="does not match delivered GLB bounds"):
        _validate_payload(payload, clay_root=clay_root, repo_root=root)


def test_loader_rejects_changed_delivered_model_hash(source_library):
    root, clay_root, source = source_library
    payload = copy.deepcopy(source)
    payload["entries"][0]["model"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Model hash mismatch"):
        _validate_payload(payload, clay_root=clay_root, repo_root=root)


def test_loader_rejects_disabled_unreviewed_entry(source_library):
    root, clay_root, source = source_library
    payload = copy.deepcopy(source)
    payload["entries"][0]["runtime_enabled"] = False
    with pytest.raises(ValueError, match="Disabled entry"):
        _validate_payload(payload, clay_root=clay_root, repo_root=root)
