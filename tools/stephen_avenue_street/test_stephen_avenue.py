"""The generator still reproduces the registered Stephen Avenue street. Run: pytest tools/stephen_avenue_street"""
import hashlib
import importlib.util
import json
import math
from itertools import pairwise
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('stephen_avenue_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

RECIPE, ROW, MODULES, BOUNDS, PREVIEW = build.build_all()


def registered(name, root='frontend/src/data'):
    rows = json.loads((ROOT / root / name).read_text(encoding='utf-8'))
    return next(r for r in rows if r['id'] == build.STREET_ID)


def test_registry_rows_are_exactly_what_the_generator_writes():
    assert registered('nativeStreetPilots.json') == ROW
    assert registered('nativeStreetPilots.json', 'backend/app/data') == ROW


def test_public_modules_are_the_generated_bytes_and_their_bounds_are_recorded():
    bounds = json.loads((ROOT / 'frontend/src/data/nativeStreetModuleBounds.json').read_text(encoding='utf-8'))
    for kind, module in MODULES.items():
        path = ROOT / 'frontend/public/street-kits/pilots' / build.STREET_ID / f'{kind}.glb'
        data = path.read_bytes()
        if data.startswith(b'version https://git-lfs'):
            assert hashlib.sha256(module['payload']).hexdigest() in data.decode()      # unhydrated checkout: the pointer names the bytes
        else:
            assert data == module['payload'], kind
        assert bounds[module['sha256']] == BOUNDS[module['sha256']]


def test_roster_card_and_presentation_bind_the_exact_revision():
    for root in ('frontend/src/data', 'backend/app/data'):
        roster = json.loads((ROOT / root / 'classroomStarter.json').read_text(encoding='utf-8'))['entries']
        release = [e for e in roster if e.get('variantId') == build.STREET_ID]
        assert release == [dict(domain='street', representation='native-modules', archetypeId=build.PARENT, variantId=build.STREET_ID,
                                revision=ROW['sourceRecipeSha256'], status='local-pilot-runtime-pending')]
    cards = json.loads((ROOT / 'frontend/src/data/classroomExpansion.json').read_text(encoding='utf-8'))
    asset = next(a for a in cards['assets'] if a['id'] == build.STREET_ID)
    assert asset['model']['revision'] == ROW['sourceRecipeSha256'] and asset['properties']['lane_count'] == 0
    assert asset['sectionWidth'] == build.WIDTH and asset['reshapeMode'] == 'fixed_section_route'
    heroes = json.loads((ROOT / 'frontend/src/data/catalogueHeroImages.json').read_text(encoding='utf-8'))
    assert heroes[build.STREET_ID] == ROW['thumbnailUrl']


def test_section_bands_tile_the_full_width():
    edge = -build.WIDTH / 2
    for band in ROW['sections']:
        assert abs(band['x'] - band['width'] / 2 - edge) < 1e-9
        edge += band['width']
    assert abs(edge - build.WIDTH / 2) < 1e-9
    covered = sorted((r['x'] - r['width'] / 2, r['x'] + r['width'] / 2) for r in ROW['program']['surfaceRegions'])
    assert covered[0][0] == -build.WIDTH / 2 and covered[-1][1] == build.WIDTH / 2
    assert all(abs(a[1] - b[0]) < 1e-9 for a, b in pairwise(covered))


def ground_box(item):
    """The placement's footprint on the ground; a linden occupies its 1.5 m grate."""
    if item['kind'] == 'linden_grate':
        plan = [[-.75, -.75], [.75, .75]]
    else:
        plan = BOUNDS[MODULES[item['kind']]['sha256']]['plan']
    c, s = math.cos(item['yaw']), math.sin(item['yaw'])
    xs, ys = [], []
    for x in (plan[0][0], plan[1][0]):
        for y in (plan[0][1], plan[1][1]):
            xs.append(item['x'] + x * c - y * s)
            ys.append(item['y'] + x * s + y * c)
    return min(xs), max(xs), min(ys), max(ys)


def test_clear_routes_stay_clear_of_every_ground_footprint():
    boxes = [ground_box(p) for p in ROW['placements']]
    for route in RECIPE['clear_routes']:
        half = route['width'] / 2
        x0, x1 = route['a'][0] - half, route['a'][0] + half
        for (bx0, bx1, by0, by1), item in zip(boxes, ROW['placements']):
            assert bx1 <= x0 + 1e-6 or bx0 >= x1 - 1e-6, (route['name'], item)


def test_every_item_fits_inside_one_cycle_and_its_own_zone():
    for item, (x0, x1, y0, y1) in zip(ROW['placements'], (ground_box(p) for p in ROW['placements'])):
        assert -build.CYCLE / 2 <= y0 and y1 <= build.CYCLE / 2, item
        assert -build.WIDTH / 2 - 1e-5 <= x0 and x1 <= build.WIDTH / 2 + 1e-5, item      # float32 bounds
        if item['kind'] == 'cafe_patio':
            assert abs(x0) > 7.5 - 1e-6 or abs(x1) > 7.5, 'patios stand against the frontage'


def test_no_motor_lanes_and_a_wide_clear_promenade():
    assert RECIPE['motor_lanes'] == 0
    promenade = next(r for r in RECIPE['clear_routes'] if r['name'] == 'promenade')
    assert promenade['width'] >= 6.0, 'fire and service access needs 6 m clear'
