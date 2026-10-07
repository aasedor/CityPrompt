import json
import unittest
from pathlib import Path

import fitz
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

from extract_riley import path_geometry, extract, CATEGORIES


class RileyExtractionTests(unittest.TestCase):
    def test_even_odd_holes_and_disconnected_islands(self):
        result = path_geometry({'even_odd': True, 'items': [
            ('re', fitz.Rect(0, 0, 10, 10), 1), ('re', fitz.Rect(2, 2, 8, 8), 1),
            ('re', fitz.Rect(3, 3, 4, 4), 1), ('re', fitz.Rect(20, 0, 21, 1), 1),
        ]})
        self.assertAlmostEqual(result.area, 66)
        self.assertTrue(result.is_valid)

    def test_changed_source_fails_before_using_calibration(self):
        with self.assertRaisesRegex(ValueError, 'PDF changed'):
            extract(Path(__file__), {'source_sha256': 'wrong'})

    def test_committed_geometry_and_street_alignment(self):
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / 'frontend/src/features/policyPlans/data/rileyUrbanForm.json').read_text())
        calibration = json.loads((Path(__file__).parent / 'riley_calibration.json').read_text())
        project = Transformer.from_crs(4326, 26911, always_xy=True)
        boundary = transform(project.transform, shape(data['boundary']))
        shapes = [transform(project.transform, shape(feature['geometry'])) for feature in data['features']]
        self.assertEqual(len(shapes), 362)
        self.assertTrue(all(p.is_valid and not p.is_empty for p in shapes))
        self.assertEqual({f['properties']['color'] for f in data['features']}, set(CATEGORIES))
        union = unary_union(shapes)
        self.assertLess(sum(p.area for p in shapes) - union.area, 1)  # No overlapping categories.
        self.assertLess(union.difference(boundary.buffer(.02)).area, .01)
        matrix, offset = np.array(calibration['matrix']), np.array(calibration['translation'])
        self.assertEqual(len(calibration['independent_checks']), 5)
        for check in calibration['independent_checks']:
            actual = np.array(check['pdf_point']) @ matrix.T + offset
            expected = np.array(project.transform(*check['city_lon_lat']))
            self.assertLess(np.linalg.norm(actual - expected), 4.1, check['name'])


if __name__ == '__main__':
    unittest.main()
