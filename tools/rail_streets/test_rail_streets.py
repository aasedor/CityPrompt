"""Deterministic checks on the rail street generator. Run: pytest tools/rail_streets"""
import hashlib
import importlib.util
import json
import math
import struct
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('rail_streets_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

STREETS = sorted(build.STREETS)
BUILT = {name: build.build_all(name) for name in STREETS}


def glb_positions(payload):
    """Every vertex of a GLB, converted back to the authoring frame (x across, y along, z up)."""
    length = struct.unpack('<I', payload[12:16])[0]
    document = json.loads(payload[20:20 + length])
    blob = payload[20 + length + 8:]
    points = []
    for mesh in document['meshes']:
        for primitive in mesh['primitives']:
            accessor = document['accessors'][primitive['attributes']['POSITION']]
            view = document['bufferViews'][accessor['bufferView']]
            values = struct.unpack_from(f'<{accessor["count"] * 3}f', blob, view.get('byteOffset', 0) + accessor.get('byteOffset', 0))
            points += [(values[i], -values[i + 2], values[i + 1]) for i in range(0, len(values), 3)]
    return points


def placed(name, below=None):
    """Plan extents of every placed module, optionally only of its parts below a height."""
    _, row, modules, _, _, _ = BUILT[name]
    points = {kind: glb_positions(m['payload']) for kind, m in modules.items()}
    for p in row['placements']:
        pts = [q for q in points[p['kind']] if below is None or q[2] + p['z'] < below]
        if not pts:
            continue
        c, s = math.cos(p['yaw']), math.sin(p['yaw'])
        xs = [p['x'] + q[0] * c - q[1] * s for q in pts]
        ys = [p['y'] + q[0] * s + q[1] * c for q in pts]
        yield p, (min(xs), max(xs)), (min(ys), max(ys))


@pytest.mark.parametrize('name', STREETS)
def test_generator_is_deterministic(name):
    first, again = BUILT[name], build.build_all(name)
    assert first[1] == again[1]
    assert {k: v['sha256'] for k, v in first[2].items()} == {k: v['sha256'] for k, v in again[2].items()}
    assert hashlib.sha256(first[4]).hexdigest() == hashlib.sha256(again[4]).hexdigest()


@pytest.mark.parametrize('name', STREETS)
def test_sections_tile_the_width_and_name_their_zones(name):
    _, row, _, _, _, _ = BUILT[name]
    edge = -row['widthM'] / 2
    for band in row['sections']:
        assert abs(band['x'] - band['width'] / 2 - edge) < 1e-9
        edge += band['width']
        assert band['zoneType'] and band['surface']
    assert abs(edge - row['widthM'] / 2) < 1e-9
    assert sum(band['zoneType'] == 'rail_track' for band in row['sections']) == 1


@pytest.mark.parametrize('name', STREETS)
def test_every_module_fits_the_width_and_its_cycle(name):
    _, row, _, _, _, _ = BUILT[name]
    half, cycle = row['widthM'] / 2, row['fixtureLengthM']
    for p, (x0, x1), (y0, y1) in placed(name):
        assert -half - 1e-6 <= x0 and x1 <= half + 1e-6, (p['kind'], x0, x1)
        assert -cycle / 2 - 1e-6 <= y0 and y1 <= cycle / 2 + 1e-6, (p['kind'], y0, y1)


@pytest.mark.parametrize('name', STREETS)
def test_nothing_stands_in_a_train_envelope_or_on_a_clear_route(name):
    recipe, _, _, _, _, _ = BUILT[name]
    for p, (x0, x1), _ in placed(name, below=4.0):
        for envelope in recipe['track_envelopes']:
            centre, half = envelope['track_centre_x'], envelope['half_width_m']
            assert x1 <= centre - half or x0 >= centre + half, (p['kind'], x0, x1, centre)
    for p, (x0, x1), _ in placed(name, below=2.2):
        for route in recipe['clear_routes']:
            assert x1 <= route['x'] - route['width'] / 2 or x0 >= route['x'] + route['width'] / 2, (p['kind'], route['name'])


@pytest.mark.parametrize('name', STREETS)
def test_rails_are_standard_gauge_and_continuous(name):
    _, row, _, _, _, _ = BUILT[name]
    heads = sorted(d['x'] for d in row['program']['details'] if d['material'] == 'rail_head')
    assert len(heads) == 4
    for a, b in ((heads[0], heads[1]), (heads[2], heads[3])):
        assert abs((b - a) - build.HEAD - build.GAUGE) < 1e-3
    for d in row['program']['details']:
        if d['material'] in ('rail', 'rail_head'):
            assert d['depth'] == row['fixtureLengthM'] and d['y'] == 0


@pytest.mark.parametrize('name', STREETS)
def test_cantilevers_meet_the_contact_wires(name):
    recipe, row, modules, _, _, _ = BUILT[name]
    dims = recipe['dimensions']
    wires = {(d['x'], d['z']) for d in row['program']['details'] if d['material'] == 'wire' and d['depth'] == row['fixtureLengthM']}
    for track in (-dims['track'], dims['track']):
        assert (round(track, 4), round(dims['contact'], 4)) in wires
    kind = next(k for k in modules if k in ('centre_pole', 'side_mast', 'hsr_mast'))
    for p in row['placements']:
        if p['kind'] != kind:
            continue
        points = glb_positions(modules[kind]['payload'])
        c, s = math.cos(p['yaw']), math.sin(p['yaw'])
        ends = [(p['x'] + q[0] * c - q[1] * s, q[2] + p['z']) for q in points if abs(q[2] + p['z'] - dims['contact']) < .05]
        for track in (-dims['track'], dims['track']):
            if kind == 'centre_pole' or (track < 0) == (p['x'] < 0):
                assert any(abs(x - track) < .12 for x, _ in ends), (kind, p['x'], track)


def test_only_the_avenue_carries_traffic():
    lanes = {name: BUILT[name][5]['lane_count'] for name in STREETS}
    assert lanes == {'hsr': 0, 'lrt_row': 0, 'median_lrt': 4}
    for name in STREETS:
        asphalt = [b for b in BUILT[name][1]['sections'] if b['material'] == 'asphalt']
        assert (len(asphalt) == 2) == (name == 'median_lrt')


def test_high_speed_line_dimensions():
    recipe = BUILT['hsr'][0]
    dims = recipe['dimensions']
    assert abs(2 * dims['track'] - 4.8) < 1e-9
    rail_top = dims['contact'] - 5.3
    assert abs(dims['messenger'] - dims['contact'] - 1.6) < 1e-9
    assert abs(dims['mast_x'] - dims['track'] - 3.0) < 1e-9          # masts 3 m from the near track centre
    assert rail_top > dims['formation']


def test_module_bounds_and_urls_follow_the_pilot_convention():
    for name in STREETS:
        _, row, modules, bounds, _, _ = BUILT[name]
        assert set(bounds) == {m['sha256'] for m in modules.values()}
        for kind, module in row['modules'].items():
            assert module['url'] == f"/street-kits/pilots/{row['id']}/{kind}.glb"
            assert module['bytes'] < 1_100_000, (name, kind)
        assert row['thumbnailUrl'].startswith('/archetypes/streets/')


@pytest.mark.parametrize('name', STREETS)
def test_the_generator_reproduces_the_registered_row_and_module_bytes(name):
    row = BUILT[name][1]
    registered = next(r for r in json.loads((ROOT / 'frontend/src/data/nativeStreetPilots.json').read_text(encoding='utf-8')) if r['id'] == row['id'])
    card = ROOT / 'frontend/public' / registered['thumbnailUrl'].lstrip('/')
    assert hashlib.sha256(card.read_bytes()).hexdigest() == registered['referenceSha256'], 'the card image is the reference lock'
    assert {**row, 'referenceSha256': registered['referenceSha256']} == registered
    for kind, module in BUILT[name][2].items():
        assert (ROOT / 'frontend/public' / registered['modules'][kind]['url'].lstrip('/')).read_bytes() == module['payload'], kind
