"""Exact, portable hosted-asset preparation; no provider or network calls."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from scripts.hosted_assets import ROOT, RepositoryAssets, checked_payload, safe_target, public_requirements, write_asset, browser_environment, stamp_service_worker, validate_packet
from scripts.hosted_assets import detail_requirements, hydrate_source_media
from scripts.hosted_assets import DETAIL_MANIFESTS


class HostedAssetsTests(unittest.TestCase):
    def test_people_models_and_thumbnails_have_exact_hosted_payloads(self):
        name = 'frontend/src/features/people/peopleCatalogue.json'
        self.assertIn(name, DETAIL_MANIFESTS)
        rows = json.loads((ROOT / name).read_text())
        self.assertEqual(len(rows), 23)
        requirements = detail_requirements(rows)
        self.assertEqual(len(requirements), 46)
        for row in rows:
            self.assertEqual(row['sha256'], row['people']['sha256'])
            for url in (row['url'], row['thumbnailUrl']):
                payload = (ROOT / 'frontend/public' / url.lstrip('/')).read_bytes()
                # CI deliberately retains LFS pointers. Match their locked OID;
                # runtime preparation verifies the downloaded bytes separately.
                if payload.startswith(b'version https://git-lfs.github.com/spec/v1'):
                    digest = payload.decode().split('oid sha256:', 1)[1].splitlines()[0]
                else:
                    digest = hashlib.sha256(payload).hexdigest()
                self.assertEqual(digest, requirements[url]['sha256'])

    def test_inclusive_people_and_realistic_picker_images_are_in_the_hosted_closure(self):
        for filename, count, file_count in [
            ('inclusivePeopleCatalogue.json', 8, 16),
            ('peopleAppearancePreviews.json', 31, 31),
        ]:
            name = 'frontend/src/features/people/' + filename
            self.assertIn(name, DETAIL_MANIFESTS)
            rows = json.loads((ROOT / name).read_text())
            self.assertEqual(len(rows), count)
            requirements = detail_requirements(rows)
            self.assertEqual(len(requirements), file_count)
            for url, lock in requirements.items():
                payload = (ROOT / 'frontend/public' / url.lstrip('/')).read_bytes()
                digest = (payload.decode().split('oid sha256:', 1)[1].splitlines()[0]
                          if payload.startswith(b'version https://git-lfs.github.com/spec/v1')
                          else hashlib.sha256(payload).hexdigest())
                self.assertEqual(digest, lock['sha256'])

    def test_reviewed_calgary_concepts_are_in_hosted_asset_closure(self):
        name = 'frontend/src/features/parks/calgarySafetyCatalogue.json'
        self.assertIn(name, DETAIL_MANIFESTS)
        rows = json.loads((ROOT / name).read_text())
        self.assertEqual(len(rows), 10)
        requirements = detail_requirements(rows)
        for row in rows:
            self.assertEqual(requirements[row['url']]['sha256'], row['sha256'])

    def test_safety_catalogue_is_part_of_the_hosted_asset_closure(self):
        name = 'frontend/src/features/parks/trafficSafetyCatalogue.json'
        self.assertIn(name, DETAIL_MANIFESTS)
        rows = json.loads((ROOT / name).read_text())
        self.assertEqual(len(rows), 56)
        requirements = detail_requirements(rows)
        for row in rows:
            self.assertEqual(requirements[row['url']]['sha256'], row['sha256'])
            self.assertEqual(requirements[row['url']]['bytes'], row['bytes'])

    def test_imported_source_media_hydrates_only_exact_tracked_lfs_bytes(self):
        sources = RepositoryAssets(ROOT)
        with tempfile.TemporaryDirectory(prefix="cityprompt-source-media-") as directory:
            sources.repo = Path(directory) / "source"
            sources.lfs = Path(directory) / "lfs"
            relative = "frontend/src/features/landing/media/test.png"
            sources.tracked = {relative, "frontend/src/features/landing/media/README.md", "frontend/src/unrelated.png"}
            payload = b"verified media payload"
            digest = hashlib.sha256(payload).hexdigest()
            source = sources.repo / relative
            source.parent.mkdir(parents=True)
            pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{digest}\nsize {len(payload)}\n".encode()
            source.write_bytes(pointer)
            cached = sources.lfs / digest[:2] / digest[2:4] / digest
            cached.parent.mkdir(parents=True)
            cached.write_bytes(payload)
            receipt = hydrate_source_media(sources)
            self.assertEqual(source.read_bytes(), payload)
            self.assertEqual(receipt, {relative: {"sha256": digest, "bytes": len(payload)}})
            self.assertEqual(hydrate_source_media(sources), receipt)
            source.write_bytes(pointer)
            cached.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                hydrate_source_media(sources)
            self.assertEqual(source.read_bytes(), pointer)

    def test_recovered_archive_serves_only_exact_locked_bytes(self):
        sources = RepositoryAssets(ROOT)
        url = "/park-kits/recovered-details-v1/test.glb"
        payload = b"reviewed model"
        digest = hashlib.sha256(payload).hexdigest()
        sources.recovered_sources = {url: {"path": "public" + url, "sha256": digest, "bytes": len(payload)}}

        def install_archive(data=payload, extra=False):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, "w") as archive:
                archive.writestr("public" + url, data)
                if extra:
                    archive.writestr("public/unapproved.glb", b"unapproved")
            packed = stream.getvalue()
            sources.recovered = {"archive_path": "seed/model-library/objects/test.zip",
                                 "archive_sha256": hashlib.sha256(packed).hexdigest(), "archive_bytes": len(packed)}
            sources.recovered_archive = None
            return packed

        packed = install_archive()
        with patch.object(sources, "read", return_value=packed) as read:
            self.assertEqual(sources.public(url, digest), payload)
            read.assert_called_once_with("seed/model-library/objects/test.zip")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                sources.public(url, "0" * 64)
        packed = install_archive(b"changed model")
        with patch.object(sources, "read", return_value=packed), self.assertRaisesRegex(ValueError, "SHA-256"):
            sources.public(url, digest)
        packed = install_archive(extra=True)
        with patch.object(sources, "read", return_value=packed), self.assertRaisesRegex(ValueError, "unlisted"):
            sources.public(url, digest)
        packed = install_archive()
        sources.recovered["archive_sha256"] = "0" * 64
        with patch.object(sources, "read", return_value=packed), self.assertRaisesRegex(ValueError, "SHA-256"):
            sources.public(url, digest)

    def test_add_details_carries_every_locked_model_and_thumbnail(self):
        rows = []
        for name in ("detailCatalogueExtras.json", "recoveredDetails.json"):
            rows.extend(json.loads((ROOT / "frontend/src/features/parks" / name).read_text()))
        requirements = detail_requirements(rows)
        self.assertEqual(len(requirements), 525)
        for row in rows:
            self.assertEqual(requirements[row["url"]]["sha256"], row["sha256"])
            self.assertEqual(requirements[row["url"]]["bytes"], row["bytes"])
            if row.get("thumbnailUrl"):
                self.assertEqual(requirements[row["thumbnailUrl"]]["sha256"], row["thumbnailSha256"])
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            detail_requirements([rows[0], {**rows[0], "sha256": "0" * 64}])

    def test_explicit_catalogue_profile_survives_sanitized_build_environment(self):
        source = {"VITE_GOOGLE_MAPS_API_KEY": "browser-key", "VITE_API_URL": "https://api.example.org",
                  "VITE_CLAUDE_FIVE_TRIAL": "true"}
        env = browser_environment(source, Path("empty-env"), Path("prepared-public"))
        self.assertEqual(env.get("VITE_CLAUDE_FIVE_TRIAL"), "true")
        self.assertEqual(env["NODE_ENV"], "production")
        with self.assertRaisesRegex(ValueError, "true or false"):
            browser_environment({**source, "VITE_CLAUDE_FIVE_TRIAL": "yes"}, Path("env"), Path("public"))

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
            with self.assertRaisesRegex(ValueError, "profile"):
                validate_packet(assets, sources, {"claude_five": True})
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
