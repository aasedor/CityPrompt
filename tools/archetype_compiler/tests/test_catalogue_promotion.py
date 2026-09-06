"""Promotion is additive, hash-bound and gated; no paid providers or live writes."""

import copy
import io
import shutil
from pathlib import Path

import pytest
import trimesh

from tools.catalogue_promotion import (
    LIBRARY,
    PICKER,
    TRIAL_CHECKS,
    check,
    digest,
    encoded,
    picker_source,
    prepare,
    read,
)
from tools.seed_model_library import remote_hash, select_candidates


@pytest.fixture
def package(tmp_path):
    root = tmp_path / "repo"
    source_root = Path(__file__).resolve().parents[3]
    for relative in ("frontend/src/features/calgaryCatalogue/guide.ts", "backend/app/services/lego_assembly.py"):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / relative, target)
    base = read(Path(__file__).resolve().parents[3] / LIBRARY)
    entry = copy.deepcopy(base["entries"][0])
    # Tiny real GLB makes the full validation path independent of repository LFS.
    model = tmp_path / "new.glb"
    model.write_bytes(trimesh.Scene(trimesh.creation.box((4, 6, 8))).export(file_type="glb"))
    from tools.rlasm_clay_library import _glb_counts

    counts = _glb_counts(model)
    entry["model"].update(
        bytes=model.stat().st_size,
        sha256=digest(model),
        native_dimensions_m={"width": 4.0, "height": 6.0, "depth": 8.0},
        mesh_count=counts["meshes"],
        material_count=counts["materials"],
    )
    target = root / LIBRARY.parent / entry["model"]["path"]
    target.parent.mkdir(parents=True)
    target.write_bytes(model.read_bytes())
    for ref in entry["references"]:
        path = root / ref["repo_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fixture source")
        ref.update(bytes=path.stat().st_size, sha256=digest(path))
    review = {
        "candidate": entry["candidate"],
        "model_sha256": digest(model),
        "reviewer": "independent fixture reviewer",
        "architectural_clay_pass": True,
        "holistic_review_performed": True,
        "unresolved_p0": 0,
        "unresolved_p1": 0,
        "inspected_files": [{"sha256": ref["sha256"]} for ref in entry["references"]],
    }
    path = root / entry["review"]["repo_path"]
    path.parent.mkdir(parents=True)
    path.write_text(encoded(review))
    entry["review"]["sha256"] = digest(path)
    base["entries"] = [entry]
    (root / LIBRARY).write_text(encoded(base))
    (root / PICKER).parent.mkdir(parents=True)
    (root / PICKER).write_text(picker_source(base))
    new = copy.deepcopy(entry)
    new.update(candidate="test-new-v001", family="test-new-family", variant_id="test_new_variant")
    new["picker"]["id"] = "test_new_asset"
    review["candidate"] = new["candidate"]
    (tmp_path / "review.json").write_text(encoded(review))
    spec = {
        "entry": new,
        "model_file": "new.glb",
        "review_file": "review.json",
        "approval": {
            "authorized_by": "human_user",
            "quote": "Fixture approval only",
            "date": "2026-09-06",
            "model_sha256": digest(model),
        },
        "trial": {
            "model_sha256": digest(model),
            "project_url": "http://localhost:5174/projects/test",
            "tested_by": "fixture",
            "tested_at": "2026-09-06",
            "evidence": ["external screenshot"],
            "checks": dict.fromkeys(TRIAL_CHECKS, True),
        },
    }
    package = tmp_path / "promotion.json"
    package.write_text(encoded(spec))
    return root, package


def test_dry_run_then_apply_and_duplicate_is_rejected(package):
    root, path = package
    before = (root / LIBRARY).read_bytes()
    prepare(root, path)
    assert (root / LIBRARY).read_bytes() == before
    assert not (root / LIBRARY.parent / "models/test-new-v001.glb").exists()
    prepare(root, path, apply=True)
    result = check(root)
    assert len(result["entries"]) == 2
    import json

    assert result["entries"][0] == json.loads(before)["entries"][0]
    with pytest.raises(ValueError, match="Already published"):
        prepare(root, path, apply=True)


def test_preserves_source_family_underscore_identity(package):
    root, path = package
    spec = read(path)
    spec['entry']['candidate'] = 'detached_contemporary_infill-clay-v003'
    review_path = path.parent / spec['review_file']
    review = read(review_path)
    review['candidate'] = spec['entry']['candidate']
    review_path.write_text(encoded(review))
    path.write_text(encoded(spec))
    prepare(root, path, apply=True)
    assert check(root)['entries'][-1]['candidate'] == review['candidate']


@pytest.mark.parametrize('candidate', ['../escape', 'family/escape', 'C:\\escape', 'family..v001'])
def test_candidate_paths_cannot_escape_package(package, candidate):
    root, path = package
    spec = read(path)
    spec['entry']['candidate'] = candidate
    path.write_text(encoded(spec))
    with pytest.raises(ValueError, match='lowercase identifier'):
        prepare(root, path, apply=True)


@pytest.mark.parametrize("failure", ["approval", "trial", "review", "model", "small_plot", "duplicate_id"])
def test_rejects_bad_packages_without_partial_writes(package, failure):
    root, path = package
    spec = read(path)
    if failure == "approval":
        spec["approval"]["model_sha256"] = "0" * 64
    if failure == "trial":
        spec["trial"]["checks"]["save_reload"] = False
    if failure == "review":
        review = read(path.parent / "review.json")
        review["unresolved_p1"] = 1
        (path.parent / "review.json").write_text(encoded(review))
    if failure == "model":
        (path.parent / "new.glb").write_bytes(b"changed model")
    if failure == "small_plot":
        spec["entry"]["picker"]["width"] = 1
    if failure == "duplicate_id":
        spec["entry"]["picker"]["id"] = "trial_postwar_bungalow"
    path.write_text(encoded(spec))
    before = (root / LIBRARY).read_bytes()
    with pytest.raises(ValueError):
        prepare(root, path, apply=True)
    assert (root / LIBRARY).read_bytes() == before
    assert not (root / LIBRARY.parent / "models/test-new-v001.glb").exists()


def test_detects_picker_and_review_drift(package):
    root, _ = package
    (root / PICKER).write_text("stale")
    with pytest.raises(ValueError, match="Picker drift"):
        check(root)
    (root / PICKER).write_text(picker_source(read(root / LIBRARY)))
    entry = read(root / LIBRARY)["entries"][0]
    (root / entry["review"]["repo_path"]).write_text("{}")
    with pytest.raises(ValueError, match="review bytes"):
        check(root)


def test_trial_can_be_tested_but_cannot_pass_publication_until_approved(package):
    root, path = package
    approved = read(path)
    unapproved = copy.deepcopy(approved)
    unapproved["approval"] = {}
    unapproved["trial"] = {}
    path.write_text(encoded(unapproved))
    prepare(root, path, trial_only=True, apply=True)
    assert check(root, allow_trials=True)["entries"][-1]["local_trial_only"]
    with pytest.raises(ValueError, match="Local trial cannot be published"):
        check(root)
    path.write_text(encoded(approved))
    prepare(root, path, apply=True)
    assert len(check(root)["entries"]) == 2
    assert check(root)["entries"][-1]["local_trial_only"] is False


def test_unknown_repeat_family_needs_backend_support(package):
    root, path = package
    spec = read(path)
    spec["entry"]["archetype_id"] = "unsupported_home"
    path.write_text(encoded(spec))
    with pytest.raises(ValueError, match="DETACHED_ARCHETYPE_IDS"):
        prepare(root, path)


def test_failed_write_restores_manifest_and_removes_only_new_deliveries(package, monkeypatch):
    root, path = package
    before = (root / LIBRARY).read_bytes()
    original_write = Path.write_text

    def fail_picker(target, *args, **kwargs):
        if target == root / PICKER:
            raise OSError("simulated disk failure")
        return original_write(target, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_picker)
    with pytest.raises(OSError, match="disk failure"):
        prepare(root, path, apply=True)
    assert (root / LIBRARY).read_bytes() == before
    assert not (root / LIBRARY.parent / "models/test-new-v001.glb").exists()
    assert not (root / LIBRARY.parent / "evidence/test-new-v001.json").exists()
    check(root)


def test_clay_dry_run_does_not_require_legacy_seed(package, monkeypatch):
    from types import SimpleNamespace
    from tools import seed_model_library as seed

    root, _ = package
    monkeypatch.setattr(seed, "ROWS_FILE", root / "missing-legacy.json")
    assert (
        seed.insert_rows(SimpleNamespace(rlasm_clay_only=True, owner_id=None, dry_run=True), read(root / LIBRARY)) == 0
    )


def test_select_install_scope_and_remote_hash():
    payload = {"entries": [{"candidate": "one"}, {"candidate": "two"}]}
    assert select_candidates(payload, ["two"])["entries"] == [{"candidate": "two"}]
    with pytest.raises(ValueError, match="Unknown"):
        select_candidates(payload, ["missing"])

    class S3:
        def get_object(self, **kwargs):
            return {"Body": io.BytesIO(b"actual remote bytes")}

    import hashlib

    assert remote_hash(S3(), "bucket", "key") == hashlib.sha256(b"actual remote bytes").hexdigest()
