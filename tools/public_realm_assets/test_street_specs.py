"""Fast recipe invariants; actual native geometry is separately reimported/raycast."""
import unittest
from street_specs import STREETS,recipe,validate


class StreetSpecsTest(unittest.TestCase):
    def test_finite_unique_batch(self):
        self.assertEqual(len(STREETS),10)
        rows=[validate(recipe(k)) for k in STREETS]
        self.assertEqual(len({r['id'] for r in rows}),10)
        self.assertEqual(len({r['reference'] for r in rows}),10)

    def test_sections_cover_footprint_without_gaps_or_overlap(self):
        for kind in STREETS:
            r=recipe(kind);cursor=-r['dimensions_m'][0]/2
            for section in r['sections']:
                self.assertAlmostEqual(section['x']-section['width']/2,cursor)
                cursor=section['x']+section['width']/2
            self.assertAlmostEqual(cursor,r['dimensions_m'][0]/2)

    def test_recipes_do_not_share_mutable_geometry(self):
        a=recipe('main_street');a['sections'][0]['width']=99
        self.assertEqual(recipe('main_street')['sections'][0]['width'],3)

    def test_bad_width_is_rejected(self):
        r=recipe('cycle_avenue');r['dimensions_m'][0]+=1
        with self.assertRaises(AssertionError):validate(r)


if __name__=='__main__':unittest.main()
