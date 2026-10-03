"""Reference details preserve the fixed sports program and exact source identity."""
import tempfile, unittest
from pathlib import Path
from court_specs import COURTS, recipe
from court_reference_profiles import REFERENCE_PROFILES, apply_profile

class ReferenceProfileTest(unittest.TestCase):
    def test_reference_revision_does_not_change_native_sports_reserve(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for profile in REFERENCE_PROFILES.values():
                for name in profile['images']:
                    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'reference-fixture')
            ids=set()
            for kind in COURTS:
                before=recipe(kind);after=apply_profile(recipe(kind),root)
                ids.add(after['id'])
                for key in ('playing_m','module_m','dimensions_m'):self.assertEqual(before[key],after[key])
                self.assertNotEqual(before['id'],after['id'])
                self.assertTrue(before['id'].endswith('_v1'))
                self.assertTrue(after['image_references'])
                self.assertTrue(after['reference_profile']['adaptation'])
            self.assertEqual(len(ids),10)

    def test_reference_lock_detects_changed_bytes_and_missing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in REFERENCE_PROFILES['basketball']['images']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'first')
            first=apply_profile(recipe('basketball'),root)
            target=root/first['image_references'][0]['path'];target.write_bytes(b'changed')
            second=apply_profile(recipe('basketball'),root)
            self.assertNotEqual(first['image_references'][0]['sha256'],second['image_references'][0]['sha256'])
            target.unlink()
            with self.assertRaises(AssertionError):apply_profile(recipe('basketball'),root)

if __name__=='__main__':unittest.main()
