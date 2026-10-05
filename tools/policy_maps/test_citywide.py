"""Offline regression checks for the pinned municipal / transportation maps."""
import json
from pathlib import Path
import unittest

import numpy as np
from pyproj import Transformer
from tile_citywide import SPECS, geographic_grid, transparent_paper

HERE = Path(__file__).resolve().parent
CALIBRATION = json.loads((HERE / 'citywide_calibration.json').read_text())

class CitywideMapTests(unittest.TestCase):
    def test_complete_current_map_inventory(self):
        self.assertEqual(len(SPECS), 12)
        self.assertEqual(len({row[0] for row in SPECS}), 12)
        self.assertNotIn('ctp-4', {row[0] for row in SPECS})
        for _, name, page, crop, legend, _ in SPECS:
            self.assertIn(f'{name}-{page}', CALIBRATION['maps'])
            self.assertTrue(crop[2] > crop[0] and crop[3] > crop[1])
            self.assertTrue(legend[2] > legend[0] and legend[3] > legend[1])

    def test_transparency_preserves_published_colours(self):
        rgb = np.array([[[255,255,255], [255,250,207], [196,214,0], [191,59,87], [248,248,248]]], dtype='uint8')
        rgba = transparent_paper(rgb)
        np.testing.assert_array_equal(rgba[:, :, :3], rgb)
        self.assertEqual(rgba[0, :, 3].tolist(), [0,255,255,255,102])

    def test_tiles_share_exact_seams_and_stay_in_calgary(self):
        for _, name, page, crop, _, _ in SPECS:
            alignment = CALIBRATION['maps'][f'{name}-{page}']
            left = geographic_grid([0,0,.125,.125], crop, alignment['matrix'], alignment['translation'])
            right = geographic_grid([.125,0,.25,.125], crop, alignment['matrix'], alignment['translation'])
            self.assertEqual([left[i*5+4] for i in range(5)], [right[i*5] for i in range(5)])
            for lon, lat in left + right:
                self.assertTrue(-115 < lon < -113 and 50 < lat < 52)

    def test_independent_city_street_junctions_do_not_drift(self):
        project = Transformer.from_crs(4326,26911,always_xy=True)
        measured = 0
        for key, alignment in CALIBRATION['maps'].items():
            check = alignment['independentCheck']
            if 'pdfJunction' not in check:
                continue
            actual = np.array(alignment['matrix']) @ check['pdfJunction'] + alignment['translation']
            expected = np.array(project.transform(*check['cityStreetLonLat']))
            error = float(np.linalg.norm(actual-expected))
            self.assertLess(error, 35 if key == 'ctp-100' else 6)
            self.assertAlmostEqual(error, check['offsetMetres'], delta=.01)
            measured += 1
        self.assertEqual(measured, 8)

    def test_downtown_page_is_rotated_into_north_up_geography(self):
        alignment = CALIBRATION['maps']['ctp-102']
        # The published north arrow points left: decreasing PDF x must move north.
        delta = np.array(alignment['matrix']) @ np.array([-1,0])
        self.assertGreater(delta[1], 5)
        self.assertLess(abs(delta[0]), .3)

if __name__ == '__main__':
    unittest.main()
