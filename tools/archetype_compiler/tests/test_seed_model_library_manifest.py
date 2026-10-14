"""Explicit seed handoffs retain review gates, source containment and exact bytes."""
import copy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from tools import seed_model_library as seed


def fixture_manifest(tmp_path, paths=None):
    manifest = tmp_path / "seed/trial/library.json"
    manifest.parent.mkdir(parents=True)
    paths = paths or ["../model-library/objects/trial/models/one.glb"]
    payload = {"entries": [{"candidate": str(index), "model": {"path": path}}
                           for index, path in enumerate(paths)]}
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest, payload


def test_explicit_manifest_normalizes_without_mutating_source(tmp_path, monkeypatch):
    manifest, payload = fixture_manifest(tmp_path)
    original = manifest.read_bytes()
    validate = MagicMock()
    monkeypatch.setattr(seed, "_validate_payload", validate, raising=False)
    normalized, root = seed.load_seed_library(manifest, repo_root=tmp_path)
    assert root == tmp_path / "seed/model-library/objects/trial"
    assert normalized["entries"][0]["model"]["path"] == "models/one.glb"
    assert manifest.read_bytes() == original
    assert payload["entries"][0]["model"]["path"].startswith("../")
    validate.assert_called_once_with(normalized, clay_root=root, repo_root=tmp_path)
    assert next(seed.clay_seed_objects(normalized, clay_root=root)).source == root / "models/one.glb"


@pytest.mark.parametrize("paths", [
    ["../../outside/models/one.glb"], ["/absolute/models/one.glb"], ["C:/models/one.glb"],
    ["../objects/models/one.txt"], ["../objects/not-models/one.glb"],
    ["../a/models/one.glb", "../b/models/two.glb"],
])
def test_explicit_manifest_rejects_unsafe_or_mixed_sources(tmp_path, monkeypatch, paths):
    manifest, _ = fixture_manifest(tmp_path, paths)
    validate = MagicMock()
    monkeypatch.setattr(seed, "_validate_payload", validate, raising=False)
    with pytest.raises(ValueError):
        seed.load_seed_library(manifest, repo_root=tmp_path)
    validate.assert_not_called()


def test_explicit_manifest_cannot_bypass_existing_byte_validator(tmp_path, monkeypatch):
    manifest, _ = fixture_manifest(tmp_path)
    monkeypatch.setattr(seed, "_validate_payload", MagicMock(side_effect=ValueError("Model hash mismatch")), raising=False)
    with pytest.raises(ValueError, match="Model hash mismatch"):
        seed.load_seed_library(manifest, repo_root=tmp_path)


def test_default_seed_still_uses_canonical_loader(monkeypatch):
    payload = {"entries": []}
    loader = MagicMock(return_value=payload)
    monkeypatch.setattr(seed, "load_library", loader)
    result, root = seed.load_seed_library(None)
    assert result is payload
    assert root == seed.CLAY_ROOT
    loader.assert_called_once_with()


def test_explicit_upload_refuses_conflict_before_any_writes(tmp_path):
    from botocore.exceptions import ClientError

    first = tmp_path / "one.glb"
    second = tmp_path / "two.glb"
    first.write_bytes(b"new bytes")
    second.write_bytes(b"exact")
    storage = MagicMock()
    storage.head_object.side_effect = [ClientError({"Error": {"Code": "404"}}, "HeadObject"), {"ContentLength": 5}]
    storage.get_object.return_value = {"Body": io.BytesIO(b"wrong")}
    hashes = {"one": hashlib.sha256(b"new bytes").hexdigest(), "two": hashlib.sha256(b"exact").hexdigest()}
    with pytest.raises(ValueError, match="conflicting"):
        seed.upload_explicit_objects(storage, "bucket", [(first, "one"), (second, "two")], hashes)
    storage.upload_file.assert_not_called()


def test_explicit_upload_skips_exact_existing_bytes_and_refuses_access_errors(tmp_path):
    from botocore.exceptions import ClientError

    model = tmp_path / "one.glb"
    model.write_bytes(b"exact")
    storage = MagicMock()
    storage.head_object.return_value = {"ContentLength": 5}
    storage.get_object.return_value = {"Body": io.BytesIO(b"exact")}
    hashes = {"one": hashlib.sha256(b"exact").hexdigest()}
    assert seed.upload_explicit_objects(storage, "bucket", [(model, "one")], hashes) == 0
    storage.upload_file.assert_not_called()
    storage.head_object.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "HeadObject")
    with pytest.raises(ClientError):
        seed.upload_explicit_objects(storage, "bucket", [(model, "one")], hashes)
    storage.upload_file.assert_not_called()


def test_explicit_existing_row_requires_same_exact_runtime_binding():
    row = {"model_url": "/api/v1/files/library/one.glb", "is_public": True,
           "lod_urls": {"0": "/api/v1/files/library/one.glb"},
           "metadata": {"rlasm": {"candidate": "one", "model_sha256": "a" * 64},
                        "lego": {"width_m": 10}}}
    seed.verify_existing_row(row, copy.deepcopy(row))
    for key, value in [("model_url", "/other.glb"), ("is_public", False), ("metadata", {}),
                       ("lod_urls", {"0": "/other.glb"})]:
        with pytest.raises(ValueError, match="conflicting"):
            seed.verify_existing_row(row, {**row, key: value})


@pytest.mark.parametrize("field", [None, "native_dimensions_m", "native_floors", "repeatable_z", "lod_urls"])
@pytest.mark.parametrize("explicit", [True, False])
def test_verify_install_checks_full_explicit_runtime_binding(monkeypatch, field, explicit):
    import boto3
    import sqlalchemy

    row = {"id": "one", "model_url": "/one.glb", "is_public": True,
           "lod_urls": {"0": "/one.glb"},
           "metadata": {"rlasm": {"model_sha256": "a" * 64, "native_dimensions_m": {"width": 10}},
                        "lego": {"variant_key": "one", "native_floors": 5, "repeatable_z": False}}}
    stored = copy.deepcopy(row)
    if field == "native_dimensions_m":
        stored["metadata"]["rlasm"][field]["width"] = 20
    elif field == "native_floors":
        stored["metadata"]["lego"][field] = 6
    elif field == "repeatable_z":
        stored["metadata"]["lego"][field] = True
    elif field == "lod_urls":
        stored[field]["0"] = "/different.glb"
    engine = MagicMock()
    conn = engine.connect.return_value.__enter__.return_value
    conn.execute.return_value.mappings.return_value.first.return_value = stored
    monkeypatch.setattr(sqlalchemy, "create_engine", MagicMock(return_value=engine))
    monkeypatch.setattr(boto3, "client", MagicMock())
    monkeypatch.setattr(seed, "remote_hash", lambda *args: "a" * 64)
    monkeypatch.setattr(seed, "clay_seed_rows", lambda payload: iter([row]))
    args = SimpleNamespace(endpoint="local", access_key="test", secret_key="test", database_url="local",
                           bucket="test", clay_library=Path("seed/trial/library.json") if explicit else None)
    payload = {"entries": [{"candidate": "one", "variant_id": "one",
                            "model": {"path": "models/one.glb", "sha256": "a" * 64}}]}
    if explicit and field:
        with pytest.raises(ValueError, match="conflicting"):
            seed.verify_install(args, payload)
    else:
        assert seed.verify_install(args, payload) == 0
    engine.dispose.assert_called_once()
    if explicit:
        assert "lod_urls" in str(conn.execute.call_args.args[0])


def test_explicit_dry_run_never_constructs_storage_or_database_clients(tmp_path, monkeypatch):
    import boto3
    import sqlalchemy

    model = tmp_path / "models/one.glb"
    model.parent.mkdir()
    model.write_bytes(b"g" * 250)
    monkeypatch.setattr(seed, "clay_seed_rows", lambda payload: iter([{"id": "one"}]))
    storage = MagicMock(side_effect=AssertionError("storage client forbidden"))
    database = MagicMock(side_effect=AssertionError("database client forbidden"))
    monkeypatch.setattr(boto3, "client", storage)
    monkeypatch.setattr(sqlalchemy, "create_engine", database)
    args = SimpleNamespace(rlasm_clay_only=True, dry_run=True, owner_id=None, clay_library=Path("seed/trial/library.json"))
    payload = {"entries": [{"model": {"path": "models/one.glb"}}]}
    assert seed.upload_objects(args, payload, clay_root=tmp_path) == 0
    assert seed.insert_rows(args, payload) == 0
    storage.assert_not_called()
    database.assert_not_called()


def test_explicit_command_retains_remote_trial_and_independent_review_gates(monkeypatch):
    from tools import catalogue_promotion

    args = SimpleNamespace(candidate=["one"], verify=False, rlasm_clay_only=True, dry_run=True,
                           objects_only=False, rows_only=False, replace=False,
                           clay_library=Path("seed/trial/library.json"), local_trial=False,
                           endpoint="https://storage.example.invalid", database_url="postgresql://db.example.invalid/test")
    payload = {"entries": [{"candidate": "one", "local_trial_only": True}]}
    monkeypatch.setattr(seed, "parse_args", lambda: args)
    monkeypatch.setattr(seed, "load_seed_library", lambda manifest: (payload, Path("seed/trial")))
    upload = MagicMock(side_effect=AssertionError("No writes permitted"))
    monkeypatch.setattr(seed, "upload_objects", upload)
    with pytest.raises(ValueError, match="Unpublished pilot"):
        seed.main()
    args.local_trial = True
    with pytest.raises(ValueError, match="loopback"):
        seed.main()
    args.local_trial = False
    payload["entries"][0]["local_trial_only"] = False
    monkeypatch.setattr(catalogue_promotion, "validate_review", MagicMock(side_effect=ValueError("Review hash mismatch")))
    with pytest.raises(ValueError, match="Review hash mismatch"):
        seed.main()
    upload.assert_not_called()


@pytest.mark.parametrize("overrides", [{"candidate": None}, {"rlasm_clay_only": False}, {"replace": True}])
def test_explicit_manifest_requires_a_finite_nonreplacement_selection(monkeypatch, overrides):
    args = SimpleNamespace(candidate=["one"], verify=False, rlasm_clay_only=True, dry_run=True,
                           objects_only=False, rows_only=False, replace=False,
                           clay_library=Path("seed/trial/library.json"))
    for key, value in overrides.items():
        setattr(args, key, value)
    monkeypatch.setattr(seed, "parse_args", lambda: args)
    loader = MagicMock()
    monkeypatch.setattr(seed, "load_seed_library", loader)
    with pytest.raises(ValueError):
        seed.main()
    loader.assert_not_called()
