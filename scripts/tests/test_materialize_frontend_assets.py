"""Clean-checkout preparation must validate exact archive outputs and preserve files."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest


class FrontendArchiveMaterializationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('scripts.materialize_frontend_assets'),
                             'The clean-checkout asset materializer is missing')
        self.module = importlib.import_module('scripts.materialize_frontend_assets')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = b'glTF exact archive member'
        self.row = {'url': '/native-park-assets/example.glb', 'logicalBytes': len(self.payload),
                    'lfsOid': hashlib.sha256(self.payload).hexdigest()}
        self.calls = []
        def public(url, digest):
            self.calls.append((url, digest))
            return self.payload
        self.sources = SimpleNamespace(repo=self.root, tracked=set(), public=public, prefetch=lambda paths: None)
        self.target = self.root / 'frontend/public/native-park-assets/example.glb'

    def run_materializer(self):
        path = self.root / 'frontend/src/data/runtimeAssetManifest.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'schema': 'cityprompt.runtime-assets@1', 'explicitReferences': [self.row]}))
        return self.module.materialize(self.root, sources=self.sources)

    def test_materializes_the_exact_missing_archive_member(self):
        result = self.run_materializer()
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(result['archive_outputs'], 1)
        self.assertEqual(self.calls, [(self.row['url'], self.row['lfsOid'])])

    def test_preserves_existing_files_without_refetching_or_overwriting(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(b'existing local work')
        result = self.run_materializer()
        self.assertEqual(result['archive_outputs'], 0)
        self.assertEqual(self.target.read_bytes(), b'existing local work')
        self.assertEqual(self.calls, [])

    def test_rejects_changed_payload_before_writing(self):
        self.row['lfsOid'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.run_materializer()
        self.assertFalse(self.target.exists())

    def test_rejects_wrong_size_before_writing(self):
        self.row['logicalBytes'] += 1
        with self.assertRaisesRegex(ValueError, 'size'):
            self.run_materializer()
        self.assertFalse(self.target.exists())

    def test_rejects_traversal_before_calling_source_reader(self):
        self.row['url'] = '/../outside.glb'
        with self.assertRaisesRegex(ValueError, 'Unsafe|escaped'):
            self.run_materializer()
        self.assertEqual(self.calls, [])

    def startup_kit(self, **overrides):
        row = {'url': '/park-kits/neighborhood-park-rustic-v0/test.glb',
               'sha256': hashlib.sha256(self.payload).hexdigest(), 'bytes': len(self.payload), **overrides}
        path = self.root / 'frontend/src/data/neighborhoodParkV0StickerKit.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'assets': {'test': row}}))
        return row, self.root / ('frontend/public' + row['url'])

    def test_materializes_pinned_startup_preloads(self):
        row, target = self.startup_kit()
        result = self.run_materializer()
        self.assertEqual(target.read_bytes(), self.payload)
        self.assertEqual(result['startup_outputs'], 1)
        self.assertIn((row['url'], row['sha256']), self.calls)

    def test_replaces_only_a_matching_lfs_pointer(self):
        row, target = self.startup_kit()
        target.parent.mkdir(parents=True)
        target.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{row['sha256']}\nsize {row['bytes']}\n")
        self.run_materializer()
        self.assertEqual(target.read_bytes(), self.payload)

    def test_preserves_conflicting_startup_payload(self):
        _, target = self.startup_kit()
        target.parent.mkdir(parents=True)
        target.write_bytes(b'existing local work')
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.run_materializer()
        self.assertEqual(target.read_bytes(), b'existing local work')

    def test_rejects_mismatched_pointer_without_replacing_it(self):
        row, target = self.startup_kit()
        target.parent.mkdir(parents=True)
        pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{'0' * 64}\nsize {row['bytes']}\n".encode()
        target.write_bytes(pointer)
        with self.assertRaisesRegex(ValueError, 'pointer differs'):
            self.run_materializer()
        self.assertEqual(target.read_bytes(), pointer)

    def test_rejects_startup_size_mismatch_before_writing(self):
        _, target = self.startup_kit(bytes=len(self.payload) + 1)
        with self.assertRaisesRegex(ValueError, 'size'):
            self.run_materializer()
        self.assertFalse(target.exists())

    def test_rejects_startup_asset_outside_its_finite_kit(self):
        self.startup_kit(url='/unrelated/test.glb')
        with self.assertRaisesRegex(ValueError, 'startup kit'):
            self.run_materializer()
