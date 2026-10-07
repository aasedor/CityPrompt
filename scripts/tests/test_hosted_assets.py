"""Exact, portable hosted-asset preparation; no provider or network calls."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.hosted_assets import ROOT, RepositoryAssets, checked_payload, safe_target, public_requirements, write_asset, browser_environment, stamp_service_worker, validate_packet


class HostedAssetsTests(unittest.TestCase):
    def test_packet_cannot_reuse_old_hero_or_publish_unlisted_files(self):
        sources = RepositoryAssets(ROOT)
        with tempfile.TemporaryDirectory(prefix="cityprompt-stale-test-") as directory:
            sources.repo = Path(directory) / "source"
            sources.repo.mkdir()
            source = sources.repo / "hero.png"
            source.write_bytes(b"old hero")
            sources.tracked = {"hero.png"}
            assets = Path(directory) / "packet"
            row = write_asset(assets / "public", "/hero.png", b"old hero")
            receipt = {"schema": "cityprompt.hosted-assets@1", "catalogue_activation": False,
                       "source_inputs": sources.fingerprint(sources.tracked), "assets": [row]}
            (assets / "assets.json").write_text(json.dumps(receipt))
            self.assertEqual(validate_packet(assets, sources), receipt)
            source.write_bytes(b"new approved hero at same URL")
            with self.assertRaisesRegex(ValueError, "stale"):
                validate_packet(assets, sources)
            source.write_bytes(b"old hero")
            (assets / "public/unlisted.env").write_text("unlisted")
            with self.assertRaisesRegex(ValueError, "unlisted"):
                validate_packet(assets, sources)

    def test_lfs_prefetch_downloads_only_exact_missing_inputs_in_batches(self):
        sources = RepositoryAssets(ROOT, fetch_lfs=True)
        with tempfile.TemporaryDirectory(prefix="cityprompt-lfs-test-") as directory:
            sources.repo = Path(directory).resolve()
            sources.lfs = sources.repo / "cache"
            sources.tracked = {"seed/a.glb", "seed/b.glb", "seed/c.glb", "seed/unrelated.glb"}
            for name, data in (("a", b"a"), ("b", b"b"), ("c", b"c")):
                digest = hashlib.sha256(data).hexdigest()
                path = sources.repo / f"seed/{name}.glb"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{digest}\nsize 1\n")
                if name == "c":
                    cached = sources.lfs / digest[:2] / digest[2:4] / digest
                    cached.parent.mkdir(parents=True)
                    cached.write_bytes(data)
            with patch("scripts.hosted_assets.subprocess.run") as run:
                sources.prefetch({"seed/a.glb", "seed/b.glb", "seed/c.glb"})
                run.assert_called_once_with(["git", "lfs", "fetch", "origin", "--include=seed/a.glb,seed/b.glb", "--exclude="], cwd=sources.repo, check=True)
            with self.assertRaises(ValueError):
                sources.prefetch({"seed/not-tracked.glb"})

    def test_release_changes_cannot_reuse_old_model_and_image_cache(self):
        source = "const CACHE_NAME = 'siteforge-v1';\nconst rest = 'unchanged';\n"
        one = stamp_service_worker(source, b"release-one")
        two = stamp_service_worker(source, b"release-two")
        self.assertNotEqual(one, two)
        self.assertNotIn("siteforge-v1", one)
        self.assertIn("const rest = 'unchanged';", one)
        self.assertEqual(one, stamp_service_worker(source, b"release-one"))
        with self.assertRaises(ValueError):
            stamp_service_worker("missing cache declaration", b"release")

    def test_rejects_unsafe_public_destinations(self):
        for url in ("/../secret", "/a/../../secret", "https://example.org/a", "/a\\b", "/a?query", "/a#fragment"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_target(Path("output"), url)
        self.assertEqual(safe_target(Path("output"), "/models/a.glb"), (Path("output") / "models/a.glb").resolve())

    def test_rejects_unhydrated_or_changed_assets(self):
        for data in (b"version https://git-lfs.github.com/spec/v1\n", b"<!doctype html><html>"):
            with self.assertRaises(ValueError):
                checked_payload(data, None)
        with self.assertRaises(ValueError):
            checked_payload(b"asset", "0" * 64)
        self.assertEqual(checked_payload(b"asset", hashlib.sha256(b"asset").hexdigest()), b"asset")

    def test_all_current_saved_and_rustic_dependencies_are_included(self):
        report = {"choices": [{"checks": [{"url": "/a.png", "kind": "image"}, {"sourcePath": "seed/private.glb", "kind": "glb"}]}],
                  "saved_layout_dependencies": [{"url": "/b.glb", "sha256": "b" * 64}],
                  "saved_model_revisions": [{"url": "/c.glb", "sha256": "c" * 64}],
                  "rustic_park_dependencies": [{"url": "/d.glb", "sha256": "d" * 64}]}
        self.assertEqual(set(public_requirements(report)), {"/a.png", "/b.glb", "/c.glb", "/d.glb"})
        report["saved_layout_dependencies"].append({"url": "/c.glb", "sha256": "f" * 64})
        with self.assertRaises(ValueError):
            public_requirements(report)

    def test_preserves_different_existing_files(self):
        with tempfile.TemporaryDirectory(prefix="cityprompt-hosted-test-") as directory:
            root = Path(directory).resolve()
            self.assertEqual(root.parent, Path(tempfile.gettempdir()).resolve())
            write_asset(root, "/a.png", b"one")
            write_asset(root, "/a.png", b"one")
            with self.assertRaises(ValueError):
                write_asset(root, "/a.png", b"two")
            self.assertEqual((root / "a.png").read_bytes(), b"one")

    def test_browser_build_requires_explicit_safe_origins_and_has_no_server_secrets(self):
        source = {"VITE_GOOGLE_MAPS_API_KEY": "restricted-browser-key", "VITE_API_URL": "https://api.example.org",
                  "VITE_FAL_KEY": "never-browser", "FAL_KEY": "server-only", "VITE_ENV_DIR": "developer-env"}
        env = browser_environment(source, Path("empty-env"), Path("prepared-public"))
        self.assertEqual(env["VITE_API_URL"], "https://api.example.org")
        self.assertNotIn("VITE_FAL_KEY", env)
        self.assertNotIn("FAL_KEY", env)
        self.assertNotEqual(env["VITE_ENV_DIR"], "developer-env")
        for bad in ("http://localhost:8011", "https://user:password@api.example.org", "https://api.example.org/api", ""):
            with self.subTest(origin=bad), self.assertRaises(ValueError):
                browser_environment({**source, "VITE_API_URL": bad}, Path("empty-env"), Path("prepared-public"))


if __name__ == "__main__":
    unittest.main()
