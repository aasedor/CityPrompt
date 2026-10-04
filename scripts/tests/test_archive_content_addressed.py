"""Exercise archive safety with disposable directories and real file copies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "archive_content_addressed.ps1"
PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell is required for archive integration tests")
class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.allowed = self.root / "evidence"
        self.source = self.allowed / "pilot"
        self.source.mkdir(parents=True)
        (self.source / "photo.txt").write_bytes(b"exact reference evidence\n")
        self.store = self.root / "archive"

    def tearDown(self):
        self.temp.cleanup()

    def archive(self, source=None, store=None, remove=False):
        args = [PWSH, "-NoProfile", "-File", str(SCRIPT),
                "-AllowedSourceRoot", str(self.allowed),
                "-SourcePath", str(source or self.source),
                "-StoreRoot", str(store or self.store)]
        if remove:
            args.append("-RemoveSource")
        return subprocess.run(args, capture_output=True, text=True, timeout=30)

    def test_copies_and_verifies_exact_evidence(self):
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        payload = Path(receipt["object"]) / "payload" / "photo.txt"
        self.assertEqual(hashlib.sha256(payload.read_bytes()).digest(),
                         hashlib.sha256((self.source / "photo.txt").read_bytes()).digest())
        self.assertTrue(self.source.exists())

    def test_rejects_store_inside_source_before_copy_or_removal(self):
        result = self.archive(store=self.source / "nested-archive", remove=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.source / "photo.txt").exists())
        self.assertFalse((self.source / "nested-archive").exists())

    def test_rejects_source_outside_allowed_root(self):
        outside = self.root / "outside"
        outside.mkdir()
        result = self.archive(source=outside, remove=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(outside.exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction safety")
    def test_rejects_junction_without_touching_its_target(self):
        target = self.root / "outside-target"
        target.mkdir()
        sentinel = target / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        link = self.source / "linked"
        def quote(p):
            return "'" + str(p).replace("'", "''") + "'"
        subprocess.run([PWSH, "-NoProfile", "-Command",
                        f"New-Item -ItemType Junction -Path {quote(link)} -Target {quote(target)} | Out-Null"],
                       check=True, capture_output=True)
        try:
            result = self.archive(remove=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertTrue(self.source.exists())
        finally:
            link.rmdir()


if __name__ == "__main__":
    unittest.main()
