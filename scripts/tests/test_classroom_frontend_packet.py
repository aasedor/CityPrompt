import hashlib

import pytest
from scripts.classroom_frontend_packet import copy_verified


def test_exact_lfs_bytes_and_portable_text_are_copied(tmp_path):
    source, target = tmp_path / "public", tmp_path / "www"
    source.mkdir()
    source.joinpath("model.glb").write_bytes(b"glTF exact model")
    row = {"path": "frontend/public/model.glb", "logicalBytes": 16, "lfsOid": hashlib.sha256(b"glTF exact model").hexdigest()}
    report = copy_verified(row, source, target)
    assert report["sha256"] == row["lfsOid"]
    source.joinpath("model.json").write_bytes(b"{}\r\n")
    copy_verified({"path": "frontend/public/model.json", "logicalBytes": 3}, source, target)
    assert target.joinpath("model.json").read_bytes() == b"{}\n"


@pytest.mark.parametrize("path", ["../private", "frontend/public/../private", "frontend/public/C:/private", "/private"])
def test_packet_paths_cannot_escape_roots(tmp_path, path):
    with pytest.raises(ValueError, match="Unsafe"):
        copy_verified({"path": path}, tmp_path / "source", tmp_path / "target")


@pytest.mark.parametrize("data", [b"version https://git-lfs.github.com/spec/v1\n", b"corrupt"])
def test_pointer_or_wrong_bytes_cannot_become_a_qualified_packet(tmp_path, data):
    source = tmp_path / "source"
    source.mkdir()
    (source / "model.glb").write_bytes(data)
    with pytest.raises(ValueError, match="not hydrated|differs"):
        copy_verified({"path": "frontend/public/model.glb", "logicalBytes": 7, "lfsOid": "f" * 64}, source, tmp_path / "target")
