"""Source-based dimensional constraints before paying the native render cost."""
import unittest
from court_specs import COURTS, recipe

class CourtSpecsTest(unittest.TestCase):
    def test_finite_unique_candidates_keep_the_complete_fixed_reserve(self):
        self.assertEqual(len(COURTS),10)
        self.assertEqual(len({r['id'] for r in COURTS.values()}),10)
        for r in COURTS.values():
            for play,reserve,park in zip(r['playing_m'],r['module_m'],r['dimensions_m']):
                self.assertGreater(reserve,play)
                self.assertGreaterEqual(park-reserve+1e-6,20)

    def test_net_sport_runoffs_do_not_squeeze_the_playing_area(self):
        for kind,runoff in [('volleyball',(3,3)),('beach_volleyball',(3,3)),('tennis',(3.66,6.4)),('badminton',(2,2)),('netball',(3.05,3.05))]:
            r=COURTS[kind]
            for play,reserve,clear in zip(r['playing_m'],r['module_m'],runoff):
                self.assertGreaterEqual((reserve-play)/2+1e-6,clear,kind)

    def test_equipment_and_program_cannot_inherit_another_sport(self):
        self.assertEqual(COURTS['basketball']['hoops'],2)
        self.assertEqual(COURTS['three_x_three']['hoops'],1)
        self.assertEqual(COURTS['petanque']['lanes'],2)
        self.assertEqual(COURTS['tennis']['net_center_m'],.914)
        self.assertEqual(COURTS['padel']['net_center_m'],.88)
        self.assertEqual(COURTS['badminton']['net_center_m'],1.524)
        r=recipe('badminton');r['limitations'].append('fixture-only');r['playing_m'][0]=1
        self.assertEqual(COURTS['badminton']['playing_m'][0],6.1)
        self.assertNotIn('fixture-only',recipe('badminton')['limitations'])

if __name__=='__main__':unittest.main()
