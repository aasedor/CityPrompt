import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('stage_parks', Path(__file__).parents[1] / 'stage_native_parks.py')
stage_parks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage_parks)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class NativeParkStagingTests(unittest.TestCase):
    def fixture(self, root):
        document = json.dumps({'asset': {'version': '2.0'}, 'buffers': []}).encode()
        document += b' ' * (-len(document) % 4)
        model = b'glTF' + struct.pack('<II', 2, 20 + len(document)) + struct.pack('<I', len(document)) + b'JSON' + document
        recipe = b'{"reviewed":true}'
        source = root / 'seed/classroom-parks/test'
        source.mkdir(parents=True)
        (source / 'assembly.glb').write_bytes(model)
        (source / 'recipe.json').write_bytes(recipe)
        archive = root / 'original.zip'
        with ZipFile(archive, 'w') as z:
            z.writestr('evidence/validation_old/recipe.json', recipe)
            z.writestr('old.glb', model)
        layout = {'id':'new', 'variantId':'new', 'sourceStorage':'repository',
                  'sourceRecipePath':'seed/classroom-parks/test/recipe.json', 'sourceRecipeSha256':sha(recipe),
                  'assets':{'assembly':{'sha256':sha(model),'archivePath':'seed/classroom-parks/test/assembly.glb','url':'/native/new.glb'}}}
        layout['contentRevision'] = sha(json.dumps(layout, sort_keys=True, separators=(',', ':')).encode())
        registry = root / 'registry.json'
        registry.write_text(json.dumps({'layouts':[layout]}))
        return archive, registry, source, model

    def test_repository_package_stages_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, registry, source, model = self.fixture(root)
            with patch.object(stage_parks, 'ROOT', root), patch.object(stage_parks, 'REGISTRY', registry):
                stage_parks.stage(archive, root / 'public')
                stage_parks.stage(archive, root / 'public')
            self.assertEqual((root / 'public/native/new.glb').read_bytes(), model)

    def test_corruption_fails_before_public_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, registry, source, _ = self.fixture(root)
            (source / 'assembly.glb').write_bytes(b'corrupt')
            with patch.object(stage_parks, 'ROOT', root), patch.object(stage_parks, 'REGISTRY', registry):
                with self.assertRaisesRegex(ValueError, 'Invalid native park asset'):
                    stage_parks.stage(archive, root / 'public')
            self.assertFalse((root / 'public').exists())

    def test_changed_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, registry, _, _ = self.fixture(root)
            dest = root / 'public/native/new.glb'
            dest.parent.mkdir(parents=True)
            dest.write_bytes(b'user work')
            with patch.object(stage_parks, 'ROOT', root), patch.object(stage_parks, 'REGISTRY', registry):
                with self.assertRaisesRegex(ValueError, 'conflicting destination'):
                    stage_parks.stage(archive, root / 'public')
            self.assertEqual(dest.read_bytes(), b'user work')

    def test_source_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(stage_parks, 'ROOT', Path(directory)):
            with self.assertRaisesRegex(ValueError, 'Unsafe classroom park source'):
                stage_parks.repository_bytes('seed/classroom-parks/../../private.json')


if __name__ == '__main__':
    unittest.main()
