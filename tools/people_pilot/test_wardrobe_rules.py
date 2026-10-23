import unittest
from wardrobe_rules import WARDROBES, PILOT_IDS, coverage


class WardrobeRulesTests(unittest.TestCase):
    def test_finite_catalogue_and_pilots(self):
        self.assertEqual(len(WARDROBES), 23)
        self.assertEqual(len(PILOT_IDS), 3)
        self.assertTrue(set(PILOT_IDS) <= WARDROBES.keys())

    def test_shorts_keep_bare_knees_and_crew_socks(self):
        kai = WARDROBES['people-community-kai']
        self.assertEqual(coverage(kai, (0.12, 0, .52)), 'skin')
        self.assertEqual(coverage(kai, (0.12, 0, .23)), 'socks')
        self.assertEqual(coverage(kai, (0.12, 0, .8)), 'trousers')

    def test_dress_has_no_trousers_and_exposed_forearms(self):
        sofia = WARDROBES['people-pilot-creative']
        self.assertEqual(coverage(sofia, (.12, 0, .4)), 'skin')
        self.assertEqual(coverage(sofia, (.55, 0, 1.4)), 'skin')
        self.assertEqual(coverage(sofia, (0, -.12, 1.3)), 'jacket')

    def test_crewneck_has_no_white_front_panel(self):
        eli = WARDROBES['people-pilot-neighbour']
        self.assertEqual(coverage(eli, (0, -.13, 1.3)), 'jacket')

    def test_t_pose_shoulders_above_neckline_stay_clothed(self):
        kai = WARDROBES['people-community-kai']
        self.assertEqual(coverage(kai, (.26, .06, 1.55)), 'jacket')
        self.assertEqual(coverage(kai, (.6, .06, 1.46)), 'skin')


if __name__ == '__main__':
    unittest.main()
