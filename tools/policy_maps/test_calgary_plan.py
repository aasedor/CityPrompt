"""Offline checks for the additional proposed-map packet."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from pyproj import Transformer
from PIL import Image
from tile_calgary_plan import SPECS, build

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAL=json.loads((HERE/'calgary_plan_calibration.json').read_text())


class ProposedMapTests(unittest.TestCase):
    def test_pinned_eight_maps_exclude_deleted_regional_maps(self):
        self.assertEqual([s[0] for s in SPECS],list(range(1,9)))
        self.assertEqual([s[1] for s in SPECS],[25,26,51,59,61,63,65,83])
        self.assertEqual(set(CAL['excludedPages']),{'93','94'})
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'other.pdf';source.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError,'PDF changed'):
                build(source,Path(folder)/'output')
            self.assertFalse((Path(folder)/'output').exists())

    def test_promoted_assets_are_complete_and_bound_to_source(self):
        for number,page,_ in SPECS:
            folder=ROOT/f'frontend/public/policy-maps/citywide-2026-v1/calgary-plan-{number}'
            meta=json.loads((folder/'map.json').read_text())
            self.assertEqual(meta['sourcePage'],page)
            self.assertEqual(meta['sourceSha256'],CAL['sha256'])
            self.assertEqual(meta['gridSize'],4)
            self.assertGreater(len(meta['tiles']),40)
            for name in ['overview','legend']:
                with Image.open(folder/f'{name}.webp') as im:
                    self.assertGreater(im.width,500)
                    im.verify()
            for tile in meta['tiles']:
                self.assertEqual(len(tile['grid']),25)
                self.assertTrue((folder/f"{tile['id']}.webp").is_file())
                self.assertTrue(all(-115<lon<-113 and 50<lat<52 for lon,lat in tile['grid']))

    def test_independent_road_control_stays_within_policy_map_tolerance(self):
        project=Transformer.from_crs(4326,26911,always_xy=True)
        measured=0
        for page,alignment in CAL['maps'].items():
            check=alignment['independentCheck']
            if 'pdfJunction' not in check:
                self.assertEqual(page,'59')  # Wheeling map omits road background.
                continue
            actual=np.array(alignment['matrix'])@check['pdfJunction']+alignment['translation']
            error=float(np.linalg.norm(actual-project.transform(*check['cityStreetLonLat'])))
            self.assertLess(error,15 if page=='26' else 7)
            self.assertAlmostEqual(error,check['offsetMetres'],delta=.01)
            measured+=1
        self.assertEqual(measured,7)


if __name__=='__main__':
    unittest.main()
