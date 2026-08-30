from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_repository_blob_policy.py"
SPEC = importlib.util.spec_from_file_location("blob_policy", SCRIPT)
assert SPEC and SPEC.loader
blob_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(blob_policy)


def run(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def commit_file(repo: Path, relative: str, content: bytes) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    run(repo, "add", relative)
    run(repo, "commit", "-m", f"add {relative}")


def stage_blob_direct(repo: Path, relative: str, content: bytes) -> None:
    blob_id = (
        subprocess.run(
            ["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
            input=content,
            check=True,
            capture_output=True,
        )
        .stdout.decode("ascii")
        .strip()
    )
    run(repo, "update-index", "--add", "--cacheinfo", "100644", blob_id, relative)


class BlobPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        run(self.repo, "init")
        run(self.repo, "config", "user.name", "Repository Policy Test")
        run(self.repo, "config", "user.email", "repo-policy@example.invalid")
        commit_file(self.repo, "baseline.txt", b"baseline\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_rejects_oversized_ordinary_blob(self) -> None:
        commit_file(self.repo, "large.bin", b"x" * 65)
        failures = blob_policy.audit_paths(self.repo, ["large.bin"], max_bytes=64)
        self.assertEqual(
            failures,
            [
                "large.bin: ordinary Git blob is 65 bytes; limit is 64 bytes "
                "(use Git LFS, artifact storage, or split it)"
            ],
        )

    def test_accepts_valid_lfs_pointer(self) -> None:
        (self.repo / ".gitattributes").write_text(
            "*.bin filter=lfs diff=lfs merge=lfs -text\n", encoding="utf-8"
        )
        pointer = (
            b"version https://git-lfs.github.com/spec/v1\n"
            b"oid sha256:" + b"a" * 64 + b"\n"
            b"size 5000000\n"
        )
        run(self.repo, "add", ".gitattributes")
        stage_blob_direct(self.repo, "asset.bin", pointer)
        run(self.repo, "commit", "-m", "track binaries with lfs")
        self.assertEqual(
            blob_policy.audit_paths(self.repo, ["asset.bin"], max_bytes=64), []
        )

    def test_rejects_lfs_attribute_with_raw_blob(self) -> None:
        (self.repo / ".gitattributes").write_text(
            "*.bin filter=lfs diff=lfs merge=lfs -text\n", encoding="utf-8"
        )
        run(self.repo, "add", ".gitattributes")
        stage_blob_direct(self.repo, "raw.bin", b"raw-binary")
        run(self.repo, "commit", "-m", "add malformed lfs entry")
        failures = blob_policy.audit_paths(self.repo, ["raw.bin"], max_bytes=64)
        self.assertEqual(
            failures,
            ["raw.bin: filter=lfs but committed blob is not a valid LFS pointer"],
        )

    def test_changed_paths_only_returns_new_commit_delta(self) -> None:
        base = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit_file(self.repo, "new.txt", b"new\n")
        self.assertEqual(blob_policy.changed_paths(self.repo, base), ["new.txt"])


if __name__ == "__main__":
    unittest.main()
