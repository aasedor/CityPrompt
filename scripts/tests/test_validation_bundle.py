import base64
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
            with patch.object(bundle,'PACKET',root), patch.object(bundle,'sync_picker_heroes'):
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

    def heroes(self, root, count=17):
        source=root/'source';manifest={}
        data=base64.b64decode('UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAUAmJaQAA3AA/vz0AAA=')
        for index in range(count):
            domain=bundle.PICKER_HERO_DOMAINS[index%3]
            url=f'/archetypes/{domain}/classroom-heroes/{index}.webp'
            target=source/url.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            manifest[f'placement-{index}']=url
        path=root/'heroes.json';path.write_text(json.dumps(manifest))
        return source,path,manifest,data

    def test_picker_heroes_stage_manifest_and_legacy_views_and_preserve_changed_copy(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source,manifest,_,data=self.heroes(root);dest=root/'out'
            legacy=source/'archetypes/buildings/classroom-heroes/inactive-legacy.webp'
            legacy.write_bytes(data)
            bundle.sync_picker_heroes(dest,source,manifest)
            bundle.sync_picker_heroes(dest,source,manifest)
            staged=list((dest/'public'/'archetypes').rglob('*.webp'))
            self.assertEqual(len(staged),18)
            self.assertEqual((dest/'public'/legacy.relative_to(source)).read_bytes(),data)
            staged[0].write_bytes(b'user edit')
            with self.assertRaisesRegex(ValueError,'Preserved changed picker hero'):
                bundle.sync_picker_heroes(dest,source,manifest)
            self.assertEqual(staged[0].read_bytes(),b'user edit')

    def test_unhydrated_picker_hero_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source,manifest,_,_=self.heroes(root);dest=root/'out'
            (source/'archetypes/streets/classroom-heroes/2.webp').write_bytes(b'version https://git-lfs.github.com/spec/v1')
            with self.assertRaisesRegex(ValueError,'Unhydrated picker hero'):
                bundle.sync_picker_heroes(dest,source,manifest)
            self.assertFalse(dest.exists())

    def test_missing_referenced_hero_fails_before_copying(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source,manifest,entries,_=self.heroes(root);dest=root/'out'
            entries['missing']='/archetypes/buildings/classroom-heroes/missing.webp'
            manifest.write_text(json.dumps(entries))
            with self.assertRaisesRegex(ValueError,'Missing required picker hero'):
                bundle.sync_picker_heroes(dest,source,manifest)
            self.assertFalse(dest.exists())

    def test_mixed_manifest_keeps_other_reference_delivery_outside_this_supplement(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source,manifest,entries,_=self.heroes(root,2);dest=root/'out'
            entries.update({'existing-png':'/archetypes/buildings/example/variant_0.png',
                            'existing-jpg':'/archetypes/openspaces/example/photo.jpg',
                            'packet-photo':'/validation-assets/parks/reference.png'})
            manifest.write_text(json.dumps(entries))
            bundle.sync_picker_heroes(dest,source,manifest)
            self.assertEqual(len(list((dest/'public').rglob('*.webp'))),2)
            self.assertFalse((dest/'public/validation-assets').exists())

    def test_unsafe_manifest_urls_fail_before_copying(self):
        invalid=['/archetypes/buildings/classroom-heroes/../escape.webp',
                 '/archetypes/buildings/classroom-heroes/%2e%2e.webp',
                 '/archetypes/legacy/classroom-heroes/0.webp',
                 '/archetypes/buildings/classroom-heroes/0.png',
                 'https://example.com/classroom-heroes/hero.webp',
                 '/archetypes/buildings/classroom-heroes/0.webp?query',
                 '/archetypes//buildings/classroom-heroes/0.webp', 4]
        for url in invalid:
            with self.subTest(url=url), tempfile.TemporaryDirectory() as t:
                root=Path(t);source,manifest,_,_=self.heroes(root);dest=root/'out'
                manifest.write_text(json.dumps({'bad':url}))
                with self.assertRaisesRegex(ValueError,'Unsafe picker hero path'):
                    bundle.sync_picker_heroes(dest,source,manifest)
                self.assertFalse(dest.exists())

    def test_invalid_or_truncated_webp_fails_before_copying(self):
        for data in [b'RIFFxxxxWEBPtest', b'not an image',
                     b'RIFF'+(12).to_bytes(4,'little')+b'WEBPJUNK'+b'\x00'*4]:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as t:
                root=Path(t);source,manifest,_,_=self.heroes(root);dest=root/'out'
                (source/'archetypes/buildings/classroom-heroes/0.webp').write_bytes(data)
                with self.assertRaisesRegex(ValueError,'Invalid WebP picker hero'):
                    bundle.sync_picker_heroes(dest,source,manifest)
                self.assertFalse(dest.exists())

if __name__=='__main__':unittest.main()
