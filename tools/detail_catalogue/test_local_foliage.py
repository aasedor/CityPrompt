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

# The first batch shipped these exact bytes. Seasonal support, new builders and
# new species must never change them, whatever happens to the registry rows.
FIRST_BATCH_SHA256 = {
    'trembling-aspen': 'e4758a42376944bebcc8d09fa4be9c16187e6e3bb1d3a6ce24201103df935cc6',
    'swedish-columnar-aspen': 'a09ee5e199e867702907e807bf4499ff75ed59b5e7699ef05406c0ef4514ddc1',
    'balsam-poplar': 'dc9e1de6bb85a1f04d74307ebe86278b1075e7059a84ae989e75e50b63e2881f',
    'paper-birch': '0eb04366360a3870e5903e776f9ffbf3a01cba9dca5186fbcc7116542e1b7387',
    'green-ash': '27f2d0724f5c83180dfa3fe01959eb4614e2e4c2d53920913f3b403fe3b12abe',
    'bur-oak': '2ccdad063f50cea83a4d1fc7036cac5488423d5cad93331402d6a5d6fe050663',
    'manitoba-maple': '894b33ce41f79c74753c9c9bc24ec1436e56785ebcccf7ec541fd2a87ed057f9',
    'laurel-leaf-willow': 'db19177329607978d2deaf6711e037791f7c54a777255f048dd5b38292e9e0de',
    'schubert-chokecherry': 'f665a32f5945c588398b3f154a3c3064cc13180c09023c7a896dc4317f971b1a',
    'showy-mountain-ash': '41fb3874bdddee746b130ae8a19b549fa9f3439838b1bf98731b5c0338197053',
    'amur-cherry': '4d5a66a73827d5744e5145f8fc9785f657a22482ff2b4f04def7e8322490b4a6',
    'white-spruce': '3d83701d9ee87a0a7969f8d113187692476bff81df706c717d99ae5f835ff4f9',
    'colorado-blue-spruce': 'a8d5e91945c654ac2ca1613d95fe54953d9ae1ac0df03bf8377a463144009f80',
    'lodgepole-pine': '33dd6af3cdfe9b7fe2277a717cc3c6e047060c6f2b5dfa72475d44a355a58716',
    'siberian-larch': '2cc624898382e3c205b2f1b8dfe8a5ab65c0de59d6d13179e0a82871446b676c',
    'saskatoon': '08f09457021f3fb055a94a164f47e0e367d6953c87e2d2baae59c1f6218be559',
    'wolf-willow': '2d3735eef77217a42acabc75eb4352420362cf5df1f22de9e3c58b29f25cfddf',
    'common-lilac': 'ed807491ada9ce15902fb504fd751c06bad0f264e52f81aae1de0ec8b52c838a',
    'caragana-hedge': '615e9e391d034bfdc887916cefdf6bd71ec11d609a0f141d2d92ce8ce70dc038',
    'cotoneaster-hedge': '6b050c1be830686fa3df2d797194c2491c12322fd1e0a32f4261b04dbe281628',
    'prickly-wild-rose': 'e3855fdf88876b6fd2001ef1ad491b44d1122bab6c34a054cf5097db28acdd48',
    'snowberry': '312babfb897777a116b5667d16334caab65a4940e69cc5f56a33c7ba0010dd7e',
    'shrubby-cinquefoil': 'cbdad927de0c9e8df2f819aae2fce47cafbb17f777d43f034ab682407aecc897',
    'buffaloberry': '5564b98060a59358cd8959f8f909dea91c51081b38890f5797aa048471e20b85',
    'highbush-cranberry': 'd2e3d29c753913fbdee9e0c57d28d71696a2f68e50b77ccd4a4011a4e1f71173',
    'diabolo-ninebark': '489410b87b1deb28cce62b06296c4cd1ea70822d548e9eb34ef137f541078965',
    'mugo-pine': 'acaf1b099cb37bfd2c57a7685d7320c7a261470160d8bbb743d18169ef801de0',
    'creeping-juniper': 'c20c840b8034b2f06e748ecabb94e41d80f6e0602bc2bdaf86ef76f784ce873c',
    'feather-reed-grass': 'ee76c55ac8a7bfda4ce21f536d498608703f29f62fbbd1f947f8d412ce975400',
    'rough-fescue-drift': '02a1ad7de8eb74a48335840437d8f67b933b8eac239aec48685f5b33133a4398',
}


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
            cls.built[species['slug']] = (species, cls.module.row(species, payload, lo, hi, triangles, meshes), payload, plant)

    def test_seventy_unique_local_plants_split_between_trees_and_planting(self):
        species = self.module.SPECIES
        self.assertEqual(len(species), 70)
        self.assertEqual(len({s['slug'] for s in species}), 70)
        self.assertEqual(len({s['label'] for s in species}), 70)
        self.assertEqual({s['kind'] for s in species}, {'tree', 'object'})
        self.assertEqual({s['category'] for s in species if s['kind'] == 'tree'}, {'Trees'})
        self.assertEqual({s['category'] for s in species if s['kind'] == 'object'}, {'Planting'})
        self.assertEqual(sum(1 for s in species if s['kind'] == 'tree'), 44)
        seasons = [s.get('season') for s in species]
        self.assertEqual((seasons.count('winter'), seasons.count('snow')), (17, 2))
        self.assertEqual(sum(1 for s in species if s['slug'].endswith('-autumn')), 2)

    def test_registry_rows_are_exactly_the_deterministic_generator_output(self):
        self.assertEqual(list(self.by_slug), [s['slug'] for s in self.module.SPECIES])
        for slug, (_species, row, payload, _plant) in self.built.items():
            with self.subTest(slug=slug):
                self.assertEqual(self.by_slug[slug], row)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row['sha256'])
                self.assertEqual(len(payload), row['bytes'])
                self.assertEqual(row['url'], f'{self.module.URL_ROOT}/{slug}.glb')

    def test_first_batch_models_are_byte_identical(self):
        self.assertEqual(len(FIRST_BATCH_SHA256), 30)
        for slug, digest in FIRST_BATCH_SHA256.items():
            with self.subTest(slug=slug):
                self.assertEqual(self.built[slug][1]['sha256'], digest)

    def test_seasonal_forms_keep_the_summer_skeleton(self):
        """A winter or snow tree is the same tree: same seed, same random sequence, same trunk and limbs."""
        for slug, (species, row, _payload, plant) in self.built.items():
            season = species.get('season')
            if not season and not slug.endswith('-autumn'):
                continue
            base_slug = slug.rsplit('-', 1)[0]
            base_species, base_row, _base_payload, base_plant = self.built[base_slug]
            with self.subTest(slug=slug):
                self.assertEqual(species['seed'], base_species['seed'])
                self.assertIs(species['builder'], base_species['builder'])
                if season == 'winter':
                    # every summer wood triangle is still there, in order, among the twiglets
                    summer = [tuple(base_plant.wood.positions[i:i + 9]) for i in range(0, len(base_plant.wood.positions), 9)]
                    winter = iter(tuple(plant.wood.positions[i:i + 9]) for i in range(0, len(plant.wood.positions), 9))
                    self.assertTrue(all(any(tri == candidate for candidate in winter) for tri in summer))
                    self.assertLess(plant.foliage.triangles, base_plant.foliage.triangles * .4)
                    self.assertTrue(row['sourceBuilder'].endswith(':winter'))
                else:
                    self.assertEqual(plant.wood.positions, base_plant.wood.positions)
                    self.assertEqual(plant.foliage.triangles, base_plant.foliage.triangles)
                    self.assertNotEqual(plant.foliage.colors, base_plant.foliage.colors)
                for actual, base in zip(row['dimensions'], base_row['dimensions']):
                    self.assertLess(abs(actual - base), .35)

    def test_geometry_budgets_and_kit_convention(self):
        total = 0
        for slug, (species, row, payload, _plant) in self.built.items():
            with self.subTest(slug=slug):
                self.assertLessEqual(row['triangles'], 14000 if species['kind'] == 'tree' else 6000)
                self.assertLessEqual(row['meshes'], 2)
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
                # width x depth x height from Y-up bounds
                for actual, declared in zip((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]), row['dimensions']):
                    self.assertLessEqual(abs(actual - declared), .00051)
                # Leaf tips may dip a few millimetres below the datum; the offset lifts them.
                self.assertTrue(-.05 <= lo[1] <= .02, lo[1])
                self.assertAlmostEqual(row['offset'][1], -lo[1], places=5)
                # The trunk or clump centre is the placement anchor, so the model is never re-centred.
                self.assertEqual((row['offset'][0], row['offset'][2]), (0.0, 0.0))
                self.assertTrue(lo[0] < 0 < hi[0] and lo[2] < 0 < hi[2])
            total += row['bytes']
        self.assertLess(total, 66_000_000)

    def test_trunks_stand_on_the_placement_anchor(self):
        for slug, (species, _row, _payload, plant) in self.built.items():
            if species['kind'] != 'tree':
                continue
            with self.subTest(slug=slug):
                # the first wood triangles are the trunk base ring; it must surround the origin
                base = [plant.wood.positions[i:i + 3] for i in range(0, 9 * 14, 3)]
                near = [p for p in base if p[2] < .05]
                self.assertTrue(near)
                self.assertLess(max(math_hypot(p[0], p[1]) for p in near), .75)

    def test_backend_allowlist_mirrors_every_row_by_kind(self):
        allow = json.loads(ALLOWLIST.read_text(encoding='utf-8'))
        for row in self.registry:
            self.assertIn(row['id'], allow['trees' if row['kind'] == 'tree' else 'props'])
            self.assertNotIn(row['id'], allow['props' if row['kind'] == 'tree' else 'trees'])

    def test_searchable_local_descriptions(self):
        text = ' '.join(f"{row['label']} {row['description']}" for row in self.registry).lower()
        for term in ('alberta', 'calgary', 'native', 'hedge', 'evergreen', 'berries', 'aspen', 'spruce', 'lilac', 'winter', 'autumn', 'snow',
                     'crocus', 'fireweed', 'cottonwood', 'elm'):
            self.assertIn(term, text)
        for row in self.registry:
            self.assertLess(len(row['description']), 140, row['id'])

    def test_register_refuses_duplicate_ids(self):
        before = EXTRAS.read_bytes(), ALLOWLIST.read_bytes()
        with self.assertRaises(ValueError):
            self.module.register(self.registry[:1], EXTRAS, ALLOWLIST)
        self.assertEqual((EXTRAS.read_bytes(), ALLOWLIST.read_bytes()), before)


def math_hypot(x, y):
    return (x * x + y * y) ** .5


if __name__ == '__main__':
    unittest.main()
