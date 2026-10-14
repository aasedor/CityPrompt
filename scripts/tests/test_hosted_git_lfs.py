import hashlib
import io
from pathlib import Path
import subprocess
import tarfile
from unittest.mock import patch

import pytest

from scripts import hosted_git_lfs as lfs


def archive():
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tar:
        member = tarfile.TarInfo("git-lfs-3.7.1/git-lfs")
        payload = b"fixture executable"
        member.size = len(payload)
        tar.addfile(member, io.BytesIO(payload))
    return output.getvalue()


def test_existing_lfs_does_not_download():
    with patch.object(lfs.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)), patch.object(
        lfs, "urlopen"
    ) as download:
        lfs.ensure_git_lfs()
        download.assert_not_called()


def test_missing_linux_lfs_is_verified_and_added_to_child_path(tmp_path, monkeypatch):
    payload = archive()
    monkeypatch.setattr(lfs, "SHA256", hashlib.sha256(payload).hexdigest())
    monkeypatch.setenv("PATH", "original-path")
    with patch.object(
        lfs.subprocess, "run", side_effect=[subprocess.CompletedProcess([], 1), subprocess.CompletedProcess([], 0)]
    ), patch.object(lfs.platform, "system", return_value="Linux"), patch.object(
        lfs.platform, "machine", return_value="x86_64"
    ), patch.object(
        lfs.tempfile, "mkdtemp", return_value=str(tmp_path)
    ), patch.object(
        lfs, "urlopen", return_value=io.BytesIO(payload)
    ):
        lfs.ensure_git_lfs()
    assert (tmp_path / "git-lfs").read_bytes() == b"fixture executable"
    assert lfs.os.environ["PATH"].startswith(str(tmp_path) + lfs.os.pathsep)


def test_bad_checksum_never_installs_or_runs_download(tmp_path):
    with patch.object(lfs.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run, patch.object(
        lfs.platform, "system", return_value="Linux"
    ), patch.object(lfs.platform, "machine", return_value="x86_64"), patch.object(
        lfs.tempfile, "mkdtemp", return_value=str(tmp_path)
    ), patch.object(
        lfs, "urlopen", return_value=io.BytesIO(archive())
    ):
        with pytest.raises(ValueError, match="checksum"):
            lfs.ensure_git_lfs()
        assert run.call_count == 1
    assert not (tmp_path / "git-lfs").exists()
