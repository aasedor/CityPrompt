"""Blender-free checks for the authored walking-surface contract."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import struct
import unittest


class SiteDetailsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name('build_site_details.py')
        spec = importlib.util.spec_from_file_location('site_details', path)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_bounded_unique_twenty(self):
        specs = self.module.SPECS
        self.assertEqual(len(specs), 20)
        self.assertEqual(len({s[0] for s in specs}), 20)

    def test_ramp_has_ground_entry_landing_and_one_in_twelve_slope(self):
        surface = self.module.walk_surface('accessible-ramp')
        stations = surface['stations']
        self.assertEqual(stations[0]['height'], 0)
        self.assertEqual(stations[-1]['height'], .6)
        for a, b in zip(stations, stations[1:]):
            self.assertLessEqual(abs(b['height']-a['height'])/(b['z']-a['z']), 1/12 + 1e-8)

    def test_stairs_use_discrete_treads(self):
        surface = self.module.walk_surface('outdoor-stairs')
        self.assertEqual(surface['interpolation'], 'step')
        self.assertEqual(max(s['height'] for s in surface['stations']), .9)
        self.assertGreaterEqual(surface['width'], 1.5)

    def test_curb_surface_and_nonwalking_objects(self):
        self.assertEqual(self.module.walk_surface('tactile-curb-ramp')['stations'][0]['height'], 0)
        self.assertIsNone(self.module.walk_surface('food-truck'))

    @unittest.skipUnless(os.environ.get('SITE_DETAILS_OUTPUT'), 'Set SITE_DETAILS_OUTPUT to validate actual GLBs')
    def test_exported_geometry_and_walk_profiles(self):
        output = Path(os.environ['SITE_DETAILS_OUTPUT'])
        records = json.loads((output/'catalogue.json').read_text())
        self.assertEqual(len(records), 20)
        for record in records:
            slug = record['id'].removeprefix('detail-site-')
            payload = (output/(slug+'.glb')).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), record['sha256'])
            self.assertEqual(len(payload), record['bytes'])
            length = struct.unpack_from('<I', payload, 12)[0]
            gltf = json.loads(payload[20:20+length])
            binary = memoryview(payload)[28+length:]
            self.assertLessEqual(len(gltf['meshes']), 10)
            self.assertEqual(len(gltf['meshes']), record['meshes'])
            vertices = []
            triangles = 0
            for mesh in gltf['meshes']:
                for primitive in mesh['primitives']:
                    triangles += gltf['accessors'][primitive['indices']]['count']//3
                    accessor = gltf['accessors'][primitive['attributes']['POSITION']]
                    self.assertEqual(accessor['componentType'], 5126)
                    view = gltf['bufferViews'][accessor['bufferView']]
                    start = view.get('byteOffset', 0)+accessor.get('byteOffset', 0)
                    stride = view.get('byteStride', 12)
                    vertices.extend(struct.unpack_from('<3f', binary, start+i*stride) for i in range(accessor['count']))
            self.assertEqual(triangles, record['triangles'], slug)
            # Static exporter bakes world transforms into every material mesh.
            for node in gltf['nodes']:
                self.assertFalse(any(key in node for key in ('matrix','rotation','translation','scale')), slug)
            actual = [max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in (0,2,1)]
            for a,b in zip(actual,record['dimensions']):self.assertAlmostEqual(a,b,places=3,msg=slug)
            if record.get('walkSurface'):
                half = .75 if slug=='tactile-curb-ramp' else 1.025
                for station in record['walkSurface']['stations']:
                    self.assertTrue(any(abs(abs(x)-half)<.0001 and abs(y-station['height'])<.0001 and abs(z-station['z'])<.0001 for x,y,z in vertices), (slug,station))


if __name__ == '__main__':
    unittest.main()
