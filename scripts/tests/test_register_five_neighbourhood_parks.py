"""Exact-evidence registration gates must fail before catalogue mutation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).parents[1]
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('five_parks',SCRIPTS/'register_five_neighbourhood_parks.py')
registrar=importlib.util.module_from_spec(spec)
spec.loader.exec_module(registrar)


def sha(data):return hashlib.sha256(data).hexdigest()


class ExactParkReviewTests(unittest.TestCase):
    def fixture(self,root):
        package=root/'candidate';package.mkdir()
        hero=b'original photographic source';evidence=b'exact offline aerial'
        (package/'variant_0.png').write_bytes(hero);(package/'aerial.png').write_bytes(evidence)
        recipe={'id':'new_park','source_references':[{'role':'front','path':'source/variant_0.png','sha256':sha(hero)}]}
        review={'status':'PASS_OFFLINE_NATIVE_REVIEW','unresolved_p0':0,'unresolved_p1':0,'model_sha256':'locked-model','inspected_files':[{'path':'aerial.png','sha256':sha(evidence)}]}
        (package/'recipe.json').write_text(json.dumps(recipe));(package/'independent-review.json').write_text(json.dumps(review))
        (package/'assembly-preview.glb').write_bytes(b'glTF fixture')
        (package/'geometry-verification.json').write_text('{}')
        for name in ('recipe.json','assembly-preview.glb','geometry-verification.json'):
            review['inspected_files'].append({'path':name,'sha256':sha((package/name).read_bytes())})
        (package/'independent-review.json').write_text(json.dumps(review))
        return package,review,{'new_park':{'key':'new-park','sha256':'locked-model'}}

    def test_changed_reviewed_view_blocks_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package,_,specs=self.fixture(root)
            (package/'aerial.png').write_bytes(b'changed render')
            with patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'Reviewed evidence changed'):registrar.main(package)
                install.assert_not_called()
            self.assertFalse((package/'before-registration').exists())

    def test_unresolved_blocker_prevents_all_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            package,review,specs=self.fixture(Path(directory));review['unresolved_p1']=1
            (package/'independent-review.json').write_text(json.dumps(review))
            with patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'Exact independent holistic pass required'):registrar.main(package)
                install.assert_not_called()

    def test_review_for_different_model_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            package,review,specs=self.fixture(Path(directory));review['model_sha256']='different-model'
            (package/'independent-review.json').write_text(json.dumps(review))
            with patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'Exact independent holistic pass required'):registrar.main(package)
                install.assert_not_called()

    def test_source_thumbnail_must_be_exact_original(self):
        with tempfile.TemporaryDirectory() as directory:
            package,_,specs=self.fixture(Path(directory));(package/'variant_0.png').write_bytes(b'replaced source')
            with patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'Thumbnail must be the exact front reference'):registrar.main(package)
                install.assert_not_called()

    def test_staging_preserves_changed_user_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);asset=root/'seed/source.glb';asset.parent.mkdir();asset.write_bytes(b'glTF native bytes')
            public=root/'public';target=public/'native/a.glb';target.parent.mkdir(parents=True);target.write_bytes(b'user asset')
            registry=root/'frontend/src/data/nativeParks.json';registry.parent.mkdir(parents=True)
            item={'sha256':sha(asset.read_bytes()),'archivePath':'seed/source.glb','url':'/native/a.glb'}
            registry.write_text(json.dumps({'layouts':[{'variantId':'new_park','assets':{'assembly':item},'thumbnail':item}]}))
            with patch.object(registrar,'ROOT',root),patch.object(registrar,'SPECS',{'new_park':{}}):
                with self.assertRaisesRegex(ValueError,'Preserved existing asset'):registrar.stage(public)
            self.assertEqual(target.read_bytes(),b'user asset')

    def test_empty_review_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package,review,specs=self.fixture(Path(directory));review['inspected_files']=[]
            (package/'independent-review.json').write_text(json.dumps(review))
            with patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'nonempty exact recipe'):registrar.main(package)
                install.assert_not_called()

    def test_mirror_conflict_is_preserved_before_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package,_,specs=self.fixture(root)
            for path,data in [('frontend/src/data/nativeParks.json',b'{"layouts":[]}'),('backend/app/data/nativeParks.json',b'{"layouts":[],"user":true}')]:
                target=root/path;target.parent.mkdir(parents=True);target.write_bytes(data)
            before=(root/'backend/app/data/nativeParks.json').read_bytes()
            with patch.object(registrar,'ROOT',root),patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'mirrors differ'):registrar.main(package)
                install.assert_not_called()
            self.assertEqual((root/'backend/app/data/nativeParks.json').read_bytes(),before)
            self.assertFalse((package/'before-registration').exists())

    def test_orphan_same_variant_card_is_not_silently_kept(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package,_,specs=self.fixture(root)
            for path in ('frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json'):
                target=root/path;target.parent.mkdir(parents=True);target.write_text('{"layouts":[]}')
            target=root/'frontend/src/data/classroomExpansion.json'
            target.write_text(json.dumps({'entries':[],'assets':[{'model':{'variantId':'new_park'},'label':'User changed card'}]}));before=target.read_bytes()
            with patch.object(registrar,'ROOT',root),patch.object(registrar,'SPECS',specs),patch.object(registrar,'register') as install:
                with self.assertRaisesRegex(ValueError,'same-variant records'):registrar.main(package)
                install.assert_not_called()
            self.assertEqual(target.read_bytes(),before)

    def test_changed_same_variant_card_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);recipe={'id':'new_park','title':'Intended park','dimensions_m':[20,30],'bounds_m':[[-10,-15,0],[10,15,5]]}
            raw=json.dumps(recipe).encode();spec={'archetype':'new_parent','sha256':'locked','group':'gardens'}
            layout={'id':'new_park--native-v1','variantId':'new_park','archetypeId':'new_parent','sourceRecipeSha256':sha(raw),'assets':{'assembly':{'sha256':'locked'}},'contentRevision':'revision','thumbnail':{'url':'/source.png'}}
            entry={'variant_id':'new_park','sha256':'locked','archetype_id':'new_parent','placement_id':'native-park:new_park--native-v1'}
            asset={'id':entry['placement_id'],'label':'User changed title','model':{'variantId':'new_park','revision':'revision','method':'native_park_v2'},'width':20,'depth':30,'calgaryGuide':{'groupId':'gardens'},'properties':{'green_space_native_layout_id':layout['id']},'thumbnail':'/source.png'}
            for path in ('frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json'):
                target=root/path;target.parent.mkdir(parents=True);target.write_text(json.dumps({'layouts':[layout]}))
            target=root/'frontend/src/data/classroomExpansion.json';target.write_text(json.dumps({'entries':[entry],'assets':[asset]}));before=target.read_bytes()
            with patch.object(registrar,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'same-variant card/assets'):registrar.preflight_registry(recipe,raw,spec)
            self.assertEqual(target.read_bytes(),before)


if __name__=='__main__':unittest.main()
