import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('bundle',Path(__file__).parents[1]/'validation_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)

class ValidationPacketTests(unittest.TestCase):
    def packet(self,root,name='public/test.glb'):
        data=b'exact native test bytes'
        with zipfile.ZipFile(root/'runtime-assets.zip','w') as z:z.writestr(name,data)
        (root/'manifest.json').write_text(json.dumps({'archive_sha256':bundle.digest((root/'runtime-assets.zip').read_bytes()),'files':[{'path':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}]}))
        return data

    def test_exact_repeated_unpack_and_changed_file_preservation(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);data=self.packet(root);dest=root/'out'
            with patch.object(bundle,'PACKET',root):
                bundle.unpack(dest);bundle.unpack(dest)
                self.assertEqual((dest/'public/test.glb').read_bytes(),data)
                (dest/'public/test.glb').write_bytes(b'user modification')
                with self.assertRaisesRegex(ValueError,'Preserved changed file'):bundle.unpack(dest)
                self.assertEqual((dest/'public/test.glb').read_bytes(),b'user modification')

    def test_wrong_archive_fails_before_extraction(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.packet(root)
            (root/'runtime-assets.zip').write_bytes(b'wrong archive')
            with patch.object(bundle,'PACKET',root),self.assertRaisesRegex(ValueError,'Missing/wrong'):bundle.unpack(root/'out')
            self.assertFalse((root/'out').exists())

    def test_path_traversal_fails_before_extraction(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.packet(root,'../outside.glb')
            with patch.object(bundle,'PACKET',root),self.assertRaisesRegex(ValueError,'Unsafe packet path'):bundle.unpack(root/'out')
            self.assertFalse((root/'outside.glb').exists())

    def test_picker_heroes_stage_exactly_and_preserve_changed_copy(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'source';dest=root/'out'
            for domain,count in [('buildings',1),('openspaces',9),('streets',2)]:
                folder=source/'archetypes'/domain/'classroom-heroes';folder.mkdir(parents=True)
                for index in range(count):(folder/f'{index}.webp').write_bytes(b'RIFFxxxxWEBPtest')
            bundle.sync_picker_heroes(dest,source)
            bundle.sync_picker_heroes(dest,source)
            staged=list((dest/'public'/'archetypes').rglob('*.webp'))
            self.assertEqual(len(staged),12)
            staged[0].write_bytes(b'user edit')
            with self.assertRaisesRegex(ValueError,'Preserved changed picker hero'):
                bundle.sync_picker_heroes(dest,source)
            self.assertEqual(staged[0].read_bytes(),b'user edit')

    def test_unhydrated_picker_hero_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'source';dest=root/'out'
            for domain,count in [('buildings',1),('openspaces',9),('streets',2)]:
                folder=source/'archetypes'/domain/'classroom-heroes';folder.mkdir(parents=True)
                for index in range(count):(folder/f'{index}.webp').write_bytes(b'RIFFxxxxWEBPtest')
            (source/'archetypes/streets/classroom-heroes/0.webp').write_bytes(b'version https://git-lfs.github.com/spec/v1')
            with self.assertRaisesRegex(ValueError,'Unhydrated picker hero'):
                bundle.sync_picker_heroes(dest,source)

if __name__=='__main__':unittest.main()
