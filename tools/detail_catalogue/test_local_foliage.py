"""Blender-free checks: the committed prairie foliage registry matches the generator."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXTRAS = ROOT / 'frontend/src/features/parks/detailCatalogueExtras.json'
ALLOWLIST = ROOT / 'backend/app/data/project_detail_models.json'


def load_module():
    path = Path(__file__).with_name('build_local_foliage.py')
    spec = importlib.util.spec_from_file_location('local_foliage', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_glb(payload):
    magic, version, size = struct.unpack_from('<4sII', payload)
    assert (magic, version, size) == (b'glTF', 2, len(payload))
    length = struct.unpack_from('<I', payload, 12)[0]
    return json.loads(payload[20:20 + length]), memoryview(payload)[28 + length:]


class PrairieFoliageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.registry = [row for row in json.loads(EXTRAS.read_text(encoding='utf-8')) if row.get('sourceKit') == cls.module.KIT]
        cls.by_slug = {row['id'].removeprefix(cls.module.PREFIX): row for row in cls.registry}
        cls.built = {}
        for species in cls.module.SPECIES:
            plant = cls.module.build(species)
            payload, lo, hi, triangles, meshes = cls.module.write_glb([plant.wood, plant.foliage], species['slug'])
            cls.built[species['slug']] = (species, cls.module.row(species, payload, lo, hi, triangles, meshes), payload)

    def test_thirty_unique_local_species_split_between_trees_and_planting(self):
        species = self.module.SPECIES
        self.assertEqual(len(species), 30)
        self.assertEqual(len({s['slug'] for s in species}), 30)
        kinds = {s['kind'] for s in species}
        self.assertEqual(kinds, {'tree', 'object'})
        self.assertEqual({s['category'] for s in species if s['kind'] == 'tree'}, {'Trees'})
        self.assertEqual({s['category'] for s in species if s['kind'] == 'object'}, {'Planting'})
        self.assertEqual(sum(1 for s in species if s['kind'] == 'tree'), 15)

    def test_registry_rows_are_exactly_the_deterministic_generator_output(self):
        self.assertEqual(set(self.by_slug), set(self.built))
        for slug, (_species, row, payload) in self.built.items():
            with self.subTest(slug=slug):
                self.assertEqual(self.by_slug[slug], row)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row['sha256'])
                self.assertEqual(len(payload), row['bytes'])
                self.assertEqual(row['url'], f'{self.module.URL_ROOT}/{slug}.glb')

    def test_geometry_budgets_and_kit_convention(self):
        total = 0
        for slug, (species, row, payload) in self.built.items():
            with self.subTest(slug=slug):
                self.assertLessEqual(row['triangles'], 14000 if species['kind'] == 'tree' else 6000)
                self.assertLessEqual(row['meshes'], 3)
                self.assertLess(row['bytes'], 1_700_000)
                gltf, binary = parse_glb(payload)
                self.assertEqual(len(gltf['meshes']), row['meshes'])
                self.assertEqual(gltf['materials'], [{'name': 'kit_linear_vertex_colour', 'doubleSided': True,
                                                      'pbrMetallicRoughness': {'metallicFactor': 0, 'roughnessFactor': 0.9}}])
                self.assertNotIn('extensionsRequired', gltf)
                for node in gltf['nodes']:
                    self.assertFalse(any(key in node for key in ('matrix', 'rotation', 'translation', 'scale')))
                triangles = 0
                lo = [float('inf')] * 3
                hi = [float('-inf')] * 3
                for mesh in gltf['meshes']:
                    for primitive in mesh['primitives']:
                        self.assertEqual(set(primitive['attributes']), {'POSITION', 'NORMAL', 'COLOR_0'})
                        triangles += gltf['accessors'][primitive['indices']]['count'] // 3
                        accessor = gltf['accessors'][primitive['attributes']['POSITION']]
                        lo = [min(a, b) for a, b in zip(lo, accessor['min'])]
                        hi = [max(a, b) for a, b in zip(hi, accessor['max'])]
                        colours = gltf['accessors'][primitive['attributes']['COLOR_0']]
                        view = gltf['bufferViews'][colours['bufferView']]
                        sample = struct.unpack_from('<3f', binary, view['byteOffset'])
                        self.assertTrue(all(0 <= c <= 1 for c in sample))
                self.assertEqual(triangles, row['triangles'])
                # width x depth x height from Y-up bounds; grounded at y = 0 with the trunk at the origin.
                for actual, declared in zip((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]), row['dimensions']):
                    self.assertLessEqual(abs(actual - declared), .00051)
                # Leaf tips may dip a few millimetres below the datum; the offset lifts them.
                self.assertTrue(-.05 <= lo[1] <= .02, lo[1])
                self.assertAlmostEqual(row['offset'][1], -lo[1], places=5)
                self.assertLess(abs(row['offset'][0]), 1.2)
                self.assertLess(abs(row['offset'][2]), 1.2)
            total += row['bytes']
        self.assertLess(total, 30_000_000)

    def test_backend_allowlist_mirrors_every_row_by_kind(self):
        allow = json.loads(ALLOWLIST.read_text(encoding='utf-8'))
        for row in self.registry:
            self.assertIn(row['id'], allow['trees' if row['kind'] == 'tree' else 'props'])
            self.assertNotIn(row['id'], allow['props' if row['kind'] == 'tree' else 'trees'])

    def test_searchable_local_descriptions(self):
        text = ' '.join(f"{row['label']} {row['description']}" for row in self.registry).lower()
        for term in ('alberta', 'calgary', 'native', 'hedge', 'evergreen', 'berries', 'aspen', 'spruce', 'lilac'):
            self.assertIn(term, text)
        for row in self.registry:
            self.assertLess(len(row['description']), 140, row['id'])

    def test_register_refuses_duplicate_ids(self):
        before = EXTRAS.read_bytes(), ALLOWLIST.read_bytes()
        with self.assertRaises(ValueError):
            self.module.register(self.registry[:1], EXTRAS, ALLOWLIST)
        self.assertEqual((EXTRAS.read_bytes(), ALLOWLIST.read_bytes()), before)


if __name__ == '__main__':
    unittest.main()
