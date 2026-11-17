"""Blender-free checks: the committed Calgary detail registry matches the builder."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXTRAS = ROOT / 'frontend/src/features/parks/detailCatalogueExtras.json'
ALLOWLIST = ROOT / 'backend/app/data/project_detail_models.json'
TILES = ROOT / 'frontend/src/features/parks/DetailCategoryTiles.tsx'


def load_module():
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    spec = importlib.util.spec_from_file_location('calgary_details', here / 'build_calgary_details.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_glb(payload):
    magic, version, size = struct.unpack_from('<4sII', payload)
    assert (magic, version, size) == (b'glTF', 2, len(payload))
    length = struct.unpack_from('<I', payload, 12)[0]
    return json.loads(payload[20:20 + length])

# SHA-256 over the 38 first-batch model hashes in catalogue order.
FIRST_BATCH_DIGEST = '5f33a018c6467c550a18bf7c1c0a4bed06823fbfc2a276cc7638a81ff43edb59'

class CalgaryDetailsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.registry = [row for row in json.loads(EXTRAS.read_text(encoding='utf-8')) if row.get('sourceKit') == cls.module.KIT]
        cls.by_slug = {row['id'].removeprefix(cls.module.PREFIX): row for row in cls.registry}
        cls.built = {item['slug']: (item, *cls.module.compile_item(item)) for item in cls.module.SPECS}

    def test_one_hundred_and_twenty_four_unique_items(self):
        specs = self.module.SPECS
        self.assertEqual(len(specs), 124)
        self.assertEqual(len({s['slug'] for s in specs}), 124)
        self.assertEqual(len({s['label'] for s in specs}), 124)
        self.assertEqual({s['kind'] for s in specs}, {'object'})
        counts = {}
        for s in specs:
            counts[s['category']] = counts.get(s['category'], 0) + 1
        self.assertEqual(counts['Winter city'], 12)
        self.assertEqual(counts['Wildlife'], 9)
        self.assertEqual(counts['Vehicles'], 7)
        self.assertEqual(sum(counts.values()), 124)
        # each batch was appended, so earlier items keep their catalogue order
        self.assertEqual((specs[75]['slug'], specs[76]['slug']), ('propane-cage', 'city-bus'))

    def test_first_batch_models_are_pinned(self):
        # The first 38 shipped before the everyday batch shared new helpers with them.
        first = [self.built[item['slug']][1]['sha256'] for item in self.module.SPECS[:38]]
        self.assertEqual(self.module.SPECS[37]['slug'], 'mule-deer')
        self.assertEqual(hashlib.sha256(''.join(first).encode()).hexdigest(), FIRST_BATCH_DIGEST)

    def test_registry_rows_are_exactly_the_deterministic_builder_output(self):
        self.assertEqual(list(self.by_slug), [s['slug'] for s in self.module.SPECS])
        for slug, (_item, row, payload) in self.built.items():
            with self.subTest(slug=slug):
                self.assertEqual({k: v for k, v in self.by_slug[slug].items() if not k.startswith('thumbnail')}, row)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row['sha256'])
                self.assertEqual(len(payload), row['bytes'])
                self.assertEqual(row['url'], f'{self.module.URL_ROOT}/{slug}.glb')

    def test_every_row_locks_a_reviewed_card_image(self):
        """Static cards keep the panel from downloading each model just to draw its tile."""
        kit = ROOT / 'frontend/public/park-kits/calgary-details-v1'
        locks = json.loads(Path(__file__).with_name('detail_card_images.lock.json').read_text(encoding='utf-8'))
        for row in self.registry:
            with self.subTest(id=row['id']):
                self.assertEqual(row['thumbnailUrl'], row['url'][:-len('.glb')] + '.webp')
                # the hash is locked beside the builder, not in the row that ships in the bundle
                self.assertNotIn('thumbnailSha256', row)
                data = (kit / Path(row['thumbnailUrl']).name).read_bytes()
                self.assertEqual((data[:4], data[8:12]), (b'RIFF', b'WEBP'))
                self.assertEqual(hashlib.sha256(data).hexdigest(), locks[row['id']])
                self.assertLess(len(data), 40_000)

    def test_geometry_budgets_and_kit_convention(self):
        total = 0
        for slug, (_item, row, payload) in self.built.items():
            with self.subTest(slug=slug):
                self.assertLess(row['triangles'], 3500)
                self.assertLessEqual(row['meshes'], 2)
                self.assertLess(row['bytes'], 400_000)
                gltf = parse_glb(payload)
                self.assertEqual(gltf['asset']['generator'], self.module.GENERATOR)
                self.assertEqual(gltf['materials'][0]['name'], 'kit_linear_vertex_colour')
                self.assertLessEqual(len(gltf['materials']), 2)
                if len(gltf['materials']) == 2:
                    self.assertEqual(gltf['materials'][1]['name'], 'kit_linear_vertex_colour_gloss')
                    self.assertNotIn('alphaMode', gltf['materials'][1])
                self.assertNotIn('images', gltf)
                self.assertNotIn('textures', gltf)
                self.assertNotIn('extensionsRequired', gltf)
                for node in gltf['nodes']:
                    self.assertFalse(any(key in node for key in ('matrix', 'rotation', 'translation', 'scale')))
                lo = [float('inf')] * 3
                hi = [float('-inf')] * 3
                for mesh in gltf['meshes']:
                    for primitive in mesh['primitives']:
                        self.assertEqual(set(primitive['attributes']), {'POSITION', 'NORMAL', 'COLOR_0'})
                        accessor = gltf['accessors'][primitive['attributes']['POSITION']]
                        lo = [min(a, b) for a, b in zip(lo, accessor['min'])]
                        hi = [max(a, b) for a, b in zip(hi, accessor['max'])]
                for actual, declared in zip((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]), row['dimensions']):
                    self.assertLessEqual(abs(actual - declared), .00051)
                # authored on the ground about a placement anchor that the footprint surrounds;
                # the offset only settles the last few millimetres of feet, wheels and tube ends
                self.assertLess(abs(lo[1]), .008)
                self.assertAlmostEqual(row['offset'][1], -lo[1], places=5)
                self.assertEqual((row['offset'][0], row['offset'][2]), (0.0, 0.0))
                self.assertTrue(lo[0] < 0 < hi[0] and lo[2] < 0 < hi[2])
            total += row['bytes']
        self.assertLess(total, 13_500_000)

    def test_line_carriers_are_centred_on_their_pole_for_chaining(self):
        for slug, span in (('utility-pole-lines', 30.0), ('lrt-catenary-pole', 40.0)):
            row = self.by_slug[slug]
            self.assertAlmostEqual(row['dimensions'][0], span, places=2)
            self.assertIn(f'{int(span)} m', row['description'])

    def test_backend_allowlist_and_category_tiles(self):
        allow = json.loads(ALLOWLIST.read_text(encoding='utf-8'))
        for row in self.registry:
            self.assertIn(row['id'], allow['props'])
            self.assertNotIn(row['id'], allow['trees'])
        tiles = TILES.read_text(encoding='utf-8')
        self.assertIn("'Winter city': () =>", tiles)
        self.assertIn('Wildlife: () =>', tiles)

    def test_ids_never_share_the_traffic_safety_family_prefix(self):
        """IDs are saved in student projects. detail-calgary- belongs to the safety concepts."""
        safety = json.loads((ROOT / 'frontend/src/features/parks/calgarySafetyCatalogue.json').read_text(encoding='utf-8'))
        self.assertTrue(safety and all(row['id'].startswith('detail-calgary-') for row in safety))
        self.assertEqual(self.module.PREFIX, 'detail-yyc-')
        for row in self.registry:
            self.assertTrue(row['id'].startswith('detail-yyc-'), row['id'])
        every = [row['id'] for row in json.loads(EXTRAS.read_text(encoding='utf-8'))]
        self.assertFalse([i for i in every if i.startswith('detail-calgary-')])

    def test_generic_wording_without_branding(self):
        for row in self.registry:
            text = f"{row['label']} {row['description']}".lower()
            self.assertLess(len(row['description']), 140, row['id'])
            for banned in ('calgary transit', 'ctrain', 'city of calgary', 'peace bridge', 'stampede'):
                self.assertNotIn(banned, text, row['id'])
        for slug in ('white-tailed-jackrabbit', 'magpies', 'canada-geese', 'mule-deer', 'bird-feeder', 'ground-squirrels', 'coyote', 'mallards', 'pelicans',
                     'osprey-platform', 'horses', 'cattle'):
            self.assertIn('static model', self.by_slug[slug]['description'].lower())


if __name__ == '__main__':
    unittest.main()
