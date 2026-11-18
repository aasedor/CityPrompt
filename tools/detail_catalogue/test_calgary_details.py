"""Blender-free checks: the committed Calgary detail registry matches the builder."""
import hashlib
import importlib.util
import json
import math
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

    def test_one_hundred_and_sixty_five_unique_items(self):
        specs = self.module.SPECS
        self.assertEqual(len(specs), 165)
        self.assertEqual(len({s['slug'] for s in specs}), 165)
        self.assertEqual(len({s['label'] for s in specs}), 165)
        self.assertEqual({s['kind'] for s in specs}, {'object'})
        counts = {}
        for s in specs:
            counts[s['category']] = counts.get(s['category'], 0) + 1
        self.assertEqual(counts['Winter city'], 12)
        self.assertEqual(counts['Wildlife'], 9)
        self.assertEqual(counts['Vehicles'], 7)
        self.assertEqual(counts['Shared micromobility'], 11)
        self.assertEqual(sum(counts.values()), 165)
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
                # the row ships the hash, as the released catalogue does; the lock file must agree
                self.assertEqual(row['thumbnailSha256'], locks[row['id']])
                data = (kit / Path(row['thumbnailUrl']).name).read_bytes()
                self.assertEqual((data[:4], data[8:12]), (b'RIFF', b'WEBP'))
                self.assertEqual(hashlib.sha256(data).hexdigest(), locks[row['id']])
                self.assertLess(len(data), 40_000)

    def test_geometry_budgets_and_kit_convention(self):
        total = 0
        for slug, (_item, row, payload) in self.built.items():
            with self.subTest(slug=slug):
                # one item is allowed more: the pink ghost barrier is a sculpture plus eighteen line drawings
                triangles, size = {'city-ghost-barrier-pink': (4_800, 540_000)}.get(slug, (3_500, 400_000))
                self.assertLess(row['triangles'], triangles)
                self.assertLessEqual(row['meshes'], 2)
                self.assertLess(row['bytes'], size)
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
        self.assertLess(total, 20_500_000)

    def test_line_carriers_are_centred_on_their_pole_for_chaining(self):
        for slug, span in (('utility-pole-lines', 30.0), ('lrt-catenary-pole', 40.0)):
            row = self.by_slug[slug]
            self.assertAlmostEqual(row['dimensions'][0], span, places=2)
            self.assertIn(f'{int(span)} m', row['description'])

    def test_boardwalk_modules_in_feet_are_exact_with_steel_railings(self):
        foot, tube = self.module.FOOT, self.module.RAIL_TUBE
        sizes = (('boardwalk-module-nine-foot', 9), ('boardwalk-module-twelve-foot', 12), ('boardwalk-corner', 6), ('boardwalk-corner-approach', 6),
                 ('boardwalk-module-nine-foot-road-rail', 9), ('boardwalk-module-twelve-foot-road-rail', 12))
        # every piece also comes with black railings: the same model in another colour
        for slug, length_ft in (*sizes, *((f'{slug}-black', length_ft) for slug, length_ft in sizes)):
            row = self.by_slug[slug]
            # nothing overhangs the deck, so the footprint is the exact conversion and a run does not drift
            self.assertEqual(row['dimensions'][:2], [round(length_ft * foot, 3), round(6 * foot, 3)], slug)
            # deck at 150 mm plus a 1.0 m railing: under the 1.2 m limit above the street
            self.assertEqual(row['dimensions'][2], 1.15, slug)
        for length_ft in (6, 9, 12):
            stiles = self.module.steel_rail_bays(length_ft * foot)
            self.assertAlmostEqual(stiles[0], tube / 2)
            self.assertAlmostEqual(stiles[-1], length_ft * foot - tube / 2)
            self.assertLessEqual(max(stiles[k + 1] - stiles[k] for k in range(len(stiles) - 1)), 6 * foot)
        # a road-side-only module carries one railing where the standard module carries two
        for length in ('nine', 'twelve'):
            self.assertLess(self.by_slug[f'boardwalk-module-{length}-foot-road-rail']['triangles'], self.by_slug[f'boardwalk-module-{length}-foot']['triangles'])
        for slug, _ in sizes:
            red, black = self.by_slug[slug], self.by_slug[f'{slug}-black']
            self.assertEqual((black['dimensions'], black['triangles']), (red['dimensions'], red['triangles']), slug)
            self.assertNotEqual(black['sha256'], red['sha256'], slug)
            self.assertIn('black steel', black['description'].lower())
            self.assertIn('red steel', red['description'].lower())

    def test_low_profile_barriers_and_planters_for_the_road_edge_of_a_patio(self):
        plain = self.by_slug['low-profile-barrier']
        self.assertEqual(plain['dimensions'], [3.0, 0.62, 0.5])
        designs = ('foothills', 'chinook', 'river', 'mosaic', 'chevron', 'quilt', 'aspen', 'confetti')
        for design in designs:
            low, tall = self.by_slug[f'low-profile-mural-{design}'], self.by_slug[f'mural-barrier-{design}']
            # painted and plain sections share a footprint, so they mix in one row
            self.assertEqual(low['dimensions'], plain['dimensions'], design)
            self.assertIn('Original design.', low['description'])
            # each low-profile mural carries the same design as the tall barrier of that name
            self.assertEqual(low['label'].split(' · ')[1], tall['label'].split(' · ')[1])
            self.assertEqual(low['color'], tall['color'])
        # the sloped face is half the height of the tall barrier's painted face, so murals fit at half scale
        self.assertAlmostEqual(self.module.LOW_FACE, self.module.MURAL_HEIGHT / 2)
        self.assertAlmostEqual(math.hypot(self.module.LOW_RUN, self.module.LOW_RISE), self.module.LOW_FACE)
        for slug, length in (('barrier-planter-pink', 1.22), ('barrier-planter-purple', 1.22), ('long-planter', 1.83)):
            row = self.by_slug[slug]
            # planter and plants together stay under 1.2 m above the street
            self.assertLess(row['dimensions'][2], 1.2, slug)
            self.assertGreater(row['dimensions'][2], .85, slug)
            # the plants spill a little past the box, never by more than 10 cm at either end
            self.assertTrue(length <= row['dimensions'][0] < length + .2, slug)
            self.assertEqual(row['category'], 'Planting')

    def test_scooter_corrals_follow_the_city_drawing_and_wrap_each_panel_exactly_once(self):
        """Drawing P2023-589-0001A: 96 by 48 in between post centres, 36 in tall, rails 28 in
        apart, four 40 by 26 in panels. Every panel face is covered by its artwork once."""
        module, inch = self.module, .0254
        designs = ('foothills', 'chinook', 'river', 'mosaic', 'chevron', 'quilt', 'aspen', 'confetti')
        slugs = ['scooter-corral-plain'] + [f'scooter-corral-{design}' for design in designs]
        plain = self.by_slug['scooter-corral-plain']
        width, depth, height = plain['dimensions']
        self.assertAlmostEqual(width, 96 * inch + .17, places=3)       # post centres plus a flange at each end
        self.assertAlmostEqual(depth, 48 * inch + .1, places=3)
        self.assertTrue(35.5 * inch < height < 36.5 * inch)
        self.assertAlmostEqual(module.CORRAL_RAILS[1] - module.CORRAL_RAILS[0], 28 * inch)
        self.assertEqual(module.CORRAL_PANEL[:2], (40 * inch, 26 * inch))
        self.assertEqual(len(module.corral_posts()), 5)
        panel_w, panel_h, thick = module.CORRAL_PANEL
        middle = sum(module.CORRAL_RAILS) / 2
        for slug in slugs:
            row = self.by_slug[slug]
            self.assertEqual(row['dimensions'], plain['dimensions'], slug)
            self.assertEqual(row['category'], 'Shared micromobility')
            if slug != 'scooter-corral-plain':
                design = slug.removeprefix('scooter-corral-')
                barrier = self.by_slug[f'mural-barrier-{design}']
                # the same eight original designs as the painted road barriers
                self.assertEqual(row['label'].split(' · ')[1], barrier['label'].split(' · ')[1])
                self.assertEqual(row['color'], barrier['color'])
                self.assertIn('Original design.', row['description'])
            item = next(spec for spec in module.SPECS if spec['slug'] == slug)
            body = module.build(item).body
            covered, stray = {}, 0
            for k in range(0, len(body.positions), 9):
                corners = [body.positions[k + 3 * i:k + 3 * i + 3] for i in range(3)]
                normal = body.normals[k:k + 3]
                on_a_face = placed = False
                for index, ((cx, cy), (ax, ay), (nx, ny)) in enumerate(module.corral_panel_frames()):
                    for side in (1, -1):
                        depths = [((x - cx) * nx + (y - cy) * ny) * side for x, y, _ in corners]
                        if all(abs(d - thick / 2) < 1e-6 for d in depths) and normal[0] * nx * side + normal[1] * ny * side > .99:
                            on_a_face = True
                            along = [(x - cx) * ax + (y - cy) * ay for x, y, _ in corners]
                            if not all(abs(u) <= panel_w / 2 + 1e-6 for u in along):
                                continue            # the other panel in the same plane
                            self.assertTrue(all(abs(z - middle) <= panel_h / 2 + 1e-6 for _, _, z in corners), slug)
                            placed = True
                            a, b, c = corners
                            cross = [(b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
                                     (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
                                     (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])]
                            covered[index, side] = covered.get((index, side), 0.0) + math.sqrt(sum(v * v for v in cross)) / 2
                stray += on_a_face and not placed
            # no artwork spills past a panel's edge
            self.assertEqual(stray, 0, slug)
            # four panels, both faces, each covered once: no gap, nothing lying on anything else
            self.assertEqual(len(covered), 8, slug)
            for face, area in covered.items():
                self.assertAlmostEqual(area, panel_w * panel_h, places=5, msg=f'{slug} {face}')
        # one mural window per panel at true proportions, so a 3 m design runs round all four
        self.assertAlmostEqual(module.CORRAL_WINDOW / module.MURAL_HEIGHT, panel_w / panel_h)

    def test_bird_and_lime_corral_parks_its_fleet_inside_the_frame(self):
        module = self.module
        row, mosaic = self.by_slug['scooter-corral-bird-lime'], self.by_slug['scooter-corral-mosaic']
        self.assertEqual(row['category'], 'Shared micromobility')
        # fleet colours only: the names and logos belong to their companies
        self.assertIn('No logos', row['description'])
        self.assertEqual(set(module.FLEETS), {'bird', 'lime'})
        # the same corral, so the same width; the e-bikes stand out of its open side
        self.assertEqual(row['dimensions'][0], mosaic['dimensions'][0])
        self.assertGreater(row['dimensions'][1], mosaic['dimensions'][1])
        fleet = module.Solid(1)
        module.corral_fleet(fleet)
        xs, ys, zs = fleet.body.positions[0::3], fleet.body.positions[1::3], fleet.body.positions[2::3]
        self.assertAlmostEqual(min(zs), 0.0, places=6)       # every vehicle stands on the ground
        self.assertLess(max(abs(x) for x in xs), module.CORRAL_BAY - module.CORRAL_FIT)     # clear of both returns
        self.assertGreater(min(ys), -module.CORRAL_BAY / 2 + module.CORRAL_PANEL[2])       # short of the long side's panel
        self.assertLess(max(zs), 1.1)

    def test_district_barriers_carry_baked_logo_artwork_that_tiles_the_face(self):
        baked = json.loads((ROOT / 'tools/detail_catalogue/district_logo_shapes.json').read_text(encoding='utf-8'))
        face = baked['face']
        self.assertAlmostEqual(face['length'], self.module.MURAL_LENGTH)
        self.assertAlmostEqual(face['bend'], self.module.MURAL_LOWER, places=5)
        self.assertAlmostEqual(face['height'], self.module.MURAL_HEIGHT, places=5)
        # every source file is recorded by hash, since the files themselves are not kept here
        self.assertEqual(len(baked['sources']), 4)
        for digest in baked['sources'].values():
            self.assertRegex(digest, r'^[0-9a-f]{64}$')
        plain = self.by_slug['concrete-barrier']
        for district, slug in (('kensington', 'district-barrier-kensington'), ('inglewood', 'district-barrier-inglewood'),
                               ('fourth-street-purple', 'district-barrier-fourth-street-purple'), ('fourth-street-green', 'district-barrier-fourth-street-green'),
                               ('seventeenth-ave', 'district-barrier-seventeenth-ave'), ('seventeenth-ave-single', 'district-barrier-seventeenth-ave-single')):
            art, row = baked['districts'][district], self.by_slug[slug]
            area = 0.0
            for a, b, c, tone in art['triangles']:
                (ax, ay), (bx, by), (cx, cy) = (art['vertices'][i] for i in (a, b, c))
                area += abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
                self.assertLess(tone, len(art['colours']))
                # no triangle straddles the bend, so each folds onto one slope
                self.assertFalse(min(ay, by, cy) < face['bend'] - 1e-4 and max(ay, by, cy) > face['bend'] + 1e-4)
            # the triangles cover the painted face exactly once: no gaps and nothing on top of anything else
            self.assertAlmostEqual(area, face['length'] * face['height'], places=3, msg=district)
            for u, v in art['vertices']:
                self.assertTrue(-1e-6 <= u <= face['length'] + 1e-6 and -1e-6 <= v <= face['height'] + 1e-6)
            # two painted faces, plus the bare barrier
            self.assertGreater(row['triangles'], 2 * len(art['triangles']))
            self.assertEqual(row['dimensions'], plain['dimensions'], slug)
            self.assertIn('belongs to its business association', row['description'])
            # paintable for real: a ground coat and at most two stencilled colours, flat, no gradients
            self.assertLessEqual(len(art['colours']), 3, district)
            painted = [art['vertices'][i] for a, b, c, tone in art['triangles'] if tone != len(art['colours']) - 1 for i in (a, b, c)]
            length = (max(u for u, _ in painted) - min(u for u, _ in painted)) / face['length']
            height = (max(v for _, v in painted) - min(v for _, v in painted)) / face['height']
            if district == 'seventeenth-ave-single':
                # asked for as one logo alone at the centre: it fills the height, not the length
                self.assertGreater(height, .85, district)
                self.assertAlmostEqual((max(u for u, _ in painted) + min(u for u, _ in painted)) / 2, face['length'] / 2, places=3)
                self.assertEqual(len(art['colours']), 2)
                continue
            # the artwork runs most of the length, so the ends are not left bare
            self.assertGreater(length, .85, district)
            if district != 'inglewood':
                # and most of the height: little bare ground is left for anyone to write on
                self.assertGreater(length, .9, district)
                self.assertGreater(height, .75, district)

    def test_city_ghost_sits_astride_a_barrier_at_just_under_two_metres(self):
        module = self.module
        plain = self.by_slug['concrete-barrier']
        ghost, pink = self.by_slug['city-ghost-barrier'], self.by_slug['city-ghost-barrier-pink']
        # the same sculpture on two barriers
        self.assertEqual(ghost['dimensions'], pink['dimensions'])
        self.assertNotEqual(ghost['sha256'], pink['sha256'])
        for row in (ghost, pink):
            # the barrier underneath is the standard 3 m section
            self.assertEqual(row['dimensions'][0], plain['dimensions'][0])
            self.assertEqual(row['category'], 'Water & landmarks')
            self.assertIn('belongs to its artist', row['description'])
            # the head tops out just under 2 m; the hat adds a little
            self.assertTrue(2.0 < row['dimensions'][2] < 2.12)
        self.assertTrue(1.9 < module.GHOST_TOP < 2.0)
        # the skirt hangs below the top of the barrier on both sides, so the ghost sits astride it
        self.assertLess(module.GHOST_SKIRT - module.GHOST_DROP, .81 - .25)
        self.assertGreater(module.GHOST_B, .2)
        # every cusp between two lobes of the skirt falls on a column of the skin
        self.assertEqual(module.GHOST_COLUMNS % module.GHOST_LOBES, 0)
        section = module.ghost_section(module.GHOST_COLUMNS)
        self.assertEqual(section[0], (0.0, -1.0))
        for i in range(1, module.GHOST_COLUMNS // 2):
            self.assertEqual(section[module.GHOST_COLUMNS - i], (-section[i][0], section[i][1]))
        # each eye lies on the front of the head, clear of its middle and of its edge
        eye_x, eye_z, eye_rx, eye_rz = module.GHOST_EYE
        self.assertGreater(eye_x - eye_rx, .02)
        self.assertLess(eye_x + eye_rx, module.GHOST_A * .7)
        self.assertLess(eye_z + eye_rz, module.GHOST_TOP)
        # each pupil lies wholly on the white of its eye, looking a little inward and down
        toward_nose, up, pupil_rx, pupil_rz = module.GHOST_LOOK
        self.assertGreater(toward_nose, 0)
        self.assertLess(up, 0)
        for dx, dz in ((pupil_rx, 0), (-pupil_rx, 0), (0, pupil_rz), (0, -pupil_rz)):
            self.assertLess(math.hypot((toward_nose + dx) / eye_rx, (up + dz) / eye_rz), .9)
        for row in (ghost, pink):
            self.assertIn('white eyes', row['description'])
        # the pink barrier carries eighteen line characters: the same nine either side of the ghost
        for side in (0, 1):
            self.assertEqual(sorted(name for row in module.DOODLE_ROWS for name in row[side]), sorted(module.DOODLES))
        # they stand clear of the ghost, one row sits on the lower slope, and the plain barrier has none
        self.assertLess(max(module.DOODLE_COLUMNS[0]) + module.DOODLE_SIZE * .6, module.MURAL_LENGTH / 2 - module.GHOST_A)
        self.assertGreater(min(module.DOODLE_COLUMNS[1]) - module.DOODLE_SIZE * .6, module.MURAL_LENGTH / 2 + module.GHOST_A)
        self.assertEqual([height > module.MURAL_LOWER for height in module.DOODLE_HEIGHTS], [True, True, False])
        self.assertGreater(pink['triangles'], ghost['triangles'] + 1000)
        self.assertIn('white doodles', pink['description'])
        self.assertNotIn('doodles', ghost['description'])

    def test_backend_allowlist_and_category_tiles(self):
        allow = json.loads(ALLOWLIST.read_text(encoding='utf-8'))
        for row in self.registry:
            self.assertIn(row['id'], allow['props'])
            self.assertNotIn(row['id'], allow['trees'])
        tiles = TILES.read_text(encoding='utf-8')
        self.assertIn("'Winter city': () =>", tiles)
        self.assertIn('Wildlife: () =>', tiles)
        self.assertIn("'Shared micromobility': () =>", tiles)
        # every scooter item, old and new, sits in its own category
        scooters = [row for row in self.registry if 'scooter' in row['id']]
        self.assertEqual(len(scooters), 11)
        self.assertTrue(all(row['category'] == 'Shared micromobility' for row in scooters))

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
