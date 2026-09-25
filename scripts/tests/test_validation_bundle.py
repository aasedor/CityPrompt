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

if __name__=='__main__':unittest.main()
