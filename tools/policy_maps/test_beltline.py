import hashlib, json, tempfile, unittest
from pathlib import Path
import fitz
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import transform, unary_union
from extract_beltline import extract
ROOT=Path(__file__).resolve().parents[2]
class BeltlinePolicyTests(unittest.TestCase):
    def test_changed_source_fails_closed_and_station_symbols_do_not_erase_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf=Path(directory)/'map.pdf'
            doc=fitz.open();page=doc.new_page(width=100,height=100)
            page.draw_rect(fitz.Rect(10,10,90,90),color=None,fill=(1,1,0))
            page.draw_line((10,50),(90,50),color=(1,1,1),width=3)
            page.draw_rect(fitz.Rect(20,20,30,30),color=(1,1,1),width=1)
            doc.save(pdf)
            inverse=Transformer.from_crs(26911,4326,always_xy=True)
            boundary=transform(inverse.transform,Polygon([(700000,5660000),(700100,5660000),(700100,5659900),(700000,5659900)]))
            config={'id':'test','source_url':'test','source_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
                    'pdf_page':1,'categories':{'#ffff00':'Policy'},'fill_indices':[0],'mask_colors':[],
                    'road_width':3,'matrix':[[1,0],[0,-1]],'translation':[700000,5660000],
                    'crs':'EPSG:26911','boundary':mapping(boundary)}
            data=extract(pdf,config)
            project=Transformer.from_crs(4326,26911,always_xy=True)
            union=unary_union([shape(feature['geometry']) for feature in data['features']])
            self.assertAlmostEqual(transform(project.transform,union).area,6160,delta=2)
            self.assertEqual(len(data['features']),2)
            config['source_sha256']='changed'
            with self.assertRaisesRegex(ValueError,'PDF changed'):
                extract(pdf,config)

    def test_source_geometry_topology_palette_and_independent_checks(self):
        configs=json.loads((Path(__file__).parent/'beltline_calibrations.json').read_text())
        for key,config in configs.items():
            with self.subTest(plan=key):
                data=json.loads((ROOT/'frontend/src/features/policyPlans/data'/f'{key}LandUseConcept.json').read_text())
                boundary=shape(data['boundary']); pieces=[shape(feature['geometry']) for feature in data['features']]
                self.assertTrue(boundary.is_valid)
                self.assertTrue(all(piece.is_valid and not piece.is_empty for piece in pieces))
                union=unary_union(pieces)
                self.assertLess(abs(sum(piece.area for piece in pieces)-union.area)*7.8e9,.01)
                self.assertLess(union.difference(boundary.buffer(1e-10)).area*7.8e9,.01)
                self.assertEqual({f['properties']['color'] for f in data['features']},set(config['categories']))
                self.assertGreater(len(pieces),20)
                self.assertEqual(data['boundary'],config['boundary'])
                self.assertEqual(config['boundary_status'],'Approved')
                matrix=np.array(config['matrix']);offset=np.array(config['translation'])
                project=Transformer.from_crs(4326,26911,always_xy=True)
                self.assertGreaterEqual(len(config['independent_checks']),2)
                for check in config['independent_checks']:
                    actual=np.array(check['pdf_point']) @ matrix.T+offset
                    self.assertLess(np.linalg.norm(actual-np.array(project.transform(*check['city_lon_lat']))),1,check['name'])
if __name__=='__main__':unittest.main()
