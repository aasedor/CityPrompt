import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("classroom_release", Path(__file__).parents[1] / "classroom_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def manifest():
    return json.loads((release.ROOT / release.SOURCE).read_text(encoding="utf-8"))


def test_committed_roster_and_generated_copies_agree():
    data = manifest()
    assert release.validate(data) == []
    assert release.check_copies(data, release.ROOT) == []
    assert all((release.ROOT / row["review"]["evidence"]).is_file() for row in data["entries"])


def test_unknown_or_unreferenced_dependency_is_not_silently_ignored():
    data = manifest()
    data["entries"][0]["dependencies"].append("missing")
    assert any("closure mismatch" in error for error in release.validate(data))


@pytest.mark.parametrize("path", ["../secret", "C:/secret", "/secret", "a/../../secret", "a\\secret"])
def test_manifest_cannot_escape_its_asset_root(path):
    data = manifest()
    data["dependencies"][0]["path"] = path
    assert any("unsafe" in error for error in release.validate(data))


def test_preflight_distinguishes_missing_pointer_corruption_and_exact_bytes(tmp_path):
    data = b"glTF exact reviewed bytes"
    dep = dict(id="test", location="public", path="test.glb", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    def inspect():
        return release.inspect_dependency(dep, root=tmp_path, public_root=tmp_path, artifact_root=None)["status"]
    assert inspect() == "missing"
    path = tmp_path / "test.glb"
    path.write_bytes(release.LFS + b"\noid sha256:test\nsize 42\n")
    assert inspect() == "unhydrated"
    path.write_bytes(data[:-1] + b"!")
    assert inspect() == "revision-mismatch"
    path.write_bytes(data)
    assert inspect() == "verified"
    dep["location"] = "artifact"
    assert inspect() == "unpackaged"


def test_text_byte_locks_are_portable_but_binary_bytes_are_exact(tmp_path):
    (tmp_path / "recipe.json").write_bytes(b"{}\r\n")
    dep = dict(id="recipe", location="repository", path="recipe.json", bytes=3,
               sha256=hashlib.sha256(b"{}\n").hexdigest(), normalizeText=True)
    assert release.inspect_dependency(dep, root=tmp_path, public_root=tmp_path, artifact_root=None)["status"] == "verified"
    dep.pop("normalizeText")
    assert release.inspect_dependency(dep, root=tmp_path, public_root=tmp_path, artifact_root=None)["status"] == "revision-mismatch"


def test_roster_does_not_implicitly_activate_candidates():
    rows = manifest()["entries"]
    assert len(rows) == 9
    native = [row for row in rows if row["representation"] == "native-modules"]
    assert len(native) == 2
    assert all(row["review"]["asset"] == "candidate" for row in native)
    # Bounded runtime acceptance never promotes a source asset to keeper status.
    bindings = json.loads((release.ROOT / "seed/classroom-release/model-bindings.json").read_text(encoding="utf-8"))
    assert all(row["metadata"]["rlasm"]["keeper_approved"] is False for row in bindings["entries"])
