import unittest
from community_shapes import shape_vertex

class CommunityShapeTests(unittest.TestCase):
    def test_fitted_jacket_changes_waist_but_keeps_neckline(self):
        design = {'fit': .90, 'hem': .04, 'leg_fit': .95, 'face_width': 1.0}
        self.assertEqual(shape_vertex(design, 'Hip_length_overshirt', (.18, .15, 1.50)), (.18, .15, 1.50))
        self.assertLess(shape_vertex(design, 'Hip_length_overshirt', (.18, .15, 1.10))[0], .18)
        self.assertAlmostEqual(shape_vertex(design, 'Hip_length_overshirt', (.18, .15, .885))[2], .845)
    def test_trouser_taper_keeps_thigh_attachment(self):
        design = {'fit': 1, 'hem': 0, 'leg_fit': .8, 'face_width': 1}
        self.assertEqual(shape_vertex(design, 'Straight_trouser_l', (.16, .03, .92), .10), (.16, .03, .92))
        self.assertLess(shape_vertex(design, 'Straight_trouser_l', (.16, .03, .28), .10)[0], .16)
    def test_face_shape_preserves_feet_and_height(self):
        design = {'fit': 1, 'hem': 0, 'leg_fit': 1, 'face_width': 1.06}
        self.assertEqual(shape_vertex(design, 'Body', (.1, -.1, .04)), (.1, -.1, .04))
        self.assertAlmostEqual(shape_vertex(design, 'Body', (.1, -.1, 1.7))[0], .106)
        self.assertEqual(shape_vertex(design, 'Body', (.1, -.1, 1.7))[2], 1.7)

if __name__ == '__main__': unittest.main()
