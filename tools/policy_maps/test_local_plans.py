import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import fitz
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

from extract_local_plans import extract

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'frontend/src/features/policyPlans/data'


class LocalPlanTests(unittest.TestCase):
    def test_reviewed_geometry_palette_and_independent_junctions(self):
        configs = json.loads((Path(__file__).parent / 'local_plan_calibrations.json').read_text())
        project = Transformer.from_crs(4326, 26911, always_xy=True)
        self.assertEqual(len(configs), 7)
        for key, config in configs.items():
            with self.subTest(plan=key):
                data = json.loads((DATA / f'{key}UrbanForm.json').read_text())
                # Validate in the stored CRS. Reprojecting sparse, straight WGS84
                # edges independently can introduce artificial slivers where
                # neighbouring edges have different intermediate vertices.
                boundary = shape(data['boundary'])
                shapes = [shape(f['geometry']) for f in data['features']]
                self.assertTrue(all(p.is_valid and not p.is_empty for p in shapes))
                colors = {f['properties']['color'] for f in data['features']}
                self.assertEqual(colors, set(config['categories']))
                union = unary_union(shapes)
                square_degrees_to_m2_at_calgary = 7.8e9
                self.assertLess(abs(sum(p.area for p in shapes) - union.area) * square_degrees_to_m2_at_calgary, .01)
                self.assertLess(union.difference(boundary.buffer(3e-7)).area * square_degrees_to_m2_at_calgary, .02)
                self.assertGreaterEqual(len(config['independent_checks']), 2)
                matrix, offset = np.array(config['matrix']), np.array(config['translation'])
                for check in config['independent_checks']:
                    actual = np.array(check['pdf_point']) @ matrix.T + offset
                    expected = np.array(project.transform(*check['city_lon_lat']))
                    self.assertLess(np.linalg.norm(actual-expected), 2.5, check['name'])

    def test_invisible_pdf_edits_do_not_erase_designations(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / 'map.pdf'
            doc = fitz.open()
            page = doc.new_page(width=100, height=100)
            page.draw_rect(fitz.Rect(10,10,90,90), color=None, fill=(1,1,0))
            page.draw_rect(fitz.Rect(20,20,80,80), color=None, fill=(1,1,1), fill_opacity=0)
            page.draw_rect(fitz.Rect(40,40,60,60), color=None, fill=(1,1,1))
            doc.save(pdf)
            config = {'id':'test', 'source_url':'test', 'source_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
                      'pdf_page':1, 'boundary_index':0, 'pdf_bounds':[10,10,90,90], 'crs':'EPSG:26911',
                      'matrix':[[1,0],[0,-1]], 'translation':[700000,5660000],
                      'categories':{'#ffff00':'Test'}, 'mask_colors':['#ffffff'], 'road_color':'#999999'}
            data = extract(pdf, config)
            project = Transformer.from_crs(4326,26911,always_xy=True)
            area = sum(transform(project.transform, shape(f['geometry'])).area for f in data['features'])
            self.assertAlmostEqual(area, 6000, delta=2)
            self.assertEqual(len(data['features'][0]['geometry']['coordinates']), 2)
            config['source_sha256']='changed'
            with self.assertRaisesRegex(ValueError, 'PDF changed'):
                extract(pdf, config)


if __name__ == '__main__':
    unittest.main()
