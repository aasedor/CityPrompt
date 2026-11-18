"""Deterministic checks on the crescent generator. Run: pytest tools/catalogue_crescent_terrace_pilot"""
import hashlib
import importlib.util
import json
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('crescent_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
Clay = build.Clay

IDENTITY = {'archetype_id': build.ARCHETYPE, 'variant_id': build.VARIANT}
CLAY = build.build()
DATA = CLAY.glb(build.PALETTE, IDENTITY)
DOCUMENT = json.loads(DATA[20:20 + struct.unpack('<I', DATA[12:16])[0]])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def test_build_is_deterministic_and_matches_the_recorded_candidate():
    assert build.build().glb(build.PALETTE, IDENTITY) == DATA
    record = json.loads((HERE / 'candidate.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(DATA).hexdigest() == record['model_sha256'], 'generator output no longer matches the recorded candidate; build a new version'
    assert len(DATA) == record['model_bytes']


def test_container_matches_the_clay_library_convention():
    assert DATA[:4] == b'glTF' and struct.unpack('<I', DATA[8:12])[0] == len(DATA)
    assert 'textures' not in DOCUMENT and 'images' not in DOCUMENT and 'cameras' not in DOCUMENT
    assert len(DOCUMENT['nodes']) == len(DOCUMENT['meshes']) == len(DOCUMENT['materials']) == len(build.PALETTE) <= 20
    for node, material in zip(DOCUMENT['nodes'], DOCUMENT['materials']):
        assert node['name'] == material['name'] and node['name'].startswith('CLAY_')
        assert not {'translation', 'rotation', 'scale', 'matrix'} & set(node)
        extras = node['extras']
        assert extras['representation_kind'] == 'architectural_clay' and extras['rlasm_building_object'] is True
        assert extras['archetype_id'] == 'london_crescent_terrace' and extras['variant_id'] == 'london-crescent-terrace-bath-stone'
        assert material['doubleSided'] is True and material['extras']['texture_free'] is True
    glass = next(m for m in DOCUMENT['materials'] if m['name'] == 'CLAY_GLASS')       # the runtime swaps this material by name
    assert glass['alphaMode'] == 'BLEND' and 'KHR_materials_transmission' in glass['extensions']


def test_native_size_grade_and_budget():
    lo, hi = CLAY.bounds()
    assert lo[2] == 0.0, 'nothing may sit below grade'
    assert math.isclose(hi[0], -lo[0], abs_tol=1e-6), 'the crescent is centred on its axis of symmetry'
    assert 135 < hi[0] - lo[0] < 136 and 51 < hi[1] - lo[1] < 52
    assert math.isclose(hi[2], build.RIDGE + build.STACK + .71, abs_tol=1e-6), 'the chimney pots are the highest point'
    assert 12_000 <= sum(CLAY.triangle_counts().values()) <= 180_000


def test_every_triangle_is_sound():
    for faces in CLAY.triangles.values():
        for face in faces:
            a, b, c = face[:3]
            normal = cross(sub(b, a), sub(c, a))
            assert dot(normal, normal) > 1e-16 and all(math.isfinite(v) for p in face for v in p)
            for given in face[3:]:
                assert math.isclose(dot(given, given), 1, abs_tol=1e-9) and dot(given, normal) > 0


def test_every_loft_faces_outward():
    """Each swept piece that is closed, measured about its own centre, encloses a positive volume."""
    original, checked = Clay.loft, []

    def spy(self, role, rings, loop=False, caps=(True, True), smooth=None):
        before = len(self.triangles.get(role, []))
        original(self, role, rings, loop=loop, caps=caps, smooth=smooth)
        middle = [sum(p[k] for ring in rings for p in ring) / sum(len(ring) for ring in rings) for k in range(3)]
        checked.append(sum(dot(sub(f[0], middle), cross(sub(f[1], middle), sub(f[2], middle))) for f in self.triangles[role][before:]))

    Clay.loft = spy
    try:
        build.build()
    finally:
        Clay.loft = original
    assert len(checked) > 5000 and min(checked) > 0


def test_plan_is_a_symmetrical_half_ellipse_of_twenty_houses():
    assert build.HOUSES == 20 and build.BAYS == 3 and build.BAY_COUNT == 2 * 60 + 2 * build.END_BAYS == 132
    front = build.NODES[:build.FRONT_BAYS + 1]
    assert len(front) == 61, 'sixty-one columns stand on the concave front'
    for x, y in front:
        assert math.isclose((x / build.SEMI_MAJOR) ** 2 + (y / build.SEMI_MINOR) ** 2, 1, abs_tol=1e-6)
    for (ax, ay), (bx, by) in zip(front, front[::-1]):
        assert math.isclose(ax, -bx, abs_tol=1e-5) and math.isclose(ay, by, abs_tol=1e-5)
    lengths = [build.Bay(build.LOOP, k).length for k in range(build.FRONT_BAYS)]
    assert max(lengths) - min(lengths) < .01 and 2.2 < lengths[0] < 2.35, 'front bays are equal'
    assert math.isclose(build.FRONT_BAYS / build.HOUSES * lengths[0], 6.83, abs_tol=.05), 'each house is about 6.8 m wide'


def test_three_storeys_with_one_sash_to_a_bay():
    assert build.STOREYS == 3
    assert math.isclose(build.FIRST + build.COLUMN, build.ARCHITRAVE) and build.ARCHITRAVE < build.CORNICE < build.RAIL
    for lo, hi in (build.GROUND_WINDOW, build.FIRST_WINDOW, build.SECOND_WINDOW):
        assert hi - lo > 1.5
    assert build.GROUND_WINDOW[1] < build.BAND and build.FIRST < build.FIRST_WINDOW[0] and build.SECOND_WINDOW[1] < build.ARCHITRAVE
    assert 10.5 < build.COLUMN / (2 * build.RADIUS) < 11.5, 'slender Ionic columns, about eleven diameters tall'
    panes = len(CLAY.triangles['glass']) // 2
    dormers = sum(1 for face in CLAY.triangles['glass'][::2] if min(p[2] for p in face[:3]) > build.EAVES)
    doors = sum(1 for k in range(build.BAY_COUNT) if build.opening_kind(k) == 'door')
    assert panes - dormers == 3 * build.BAY_COUNT, 'a sash on each storey of every bay, with a fanlight where a door stands'
    assert doors == 42


def test_doors():
    report = build.entrances()
    kinds = [door['kind'] for door in report]
    assert kinds.count('front door') == 20 and kinds.count('garden door') == 20 and kinds.count('end door') == 2
    for door in report:
        assert door['rise_m'] < .04 and door['clear_width_m'] > .9
        bay = build.Bay(build.LOOP, door['bay'])
        x, y, _ = bay.p(bay.length / 2, .22, 0)
        assert math.isclose(x, door['centre_xy_m'][0], abs_tol=1e-3) and math.isclose(y, door['centre_xy_m'][1], abs_tol=1e-3)
    fronts = sorted(door['bay'] for door in report if door['kind'] == 'front door')
    assert fronts == list(range(0, 60, 3)), 'one front door to each house, in its first bay'


def test_roof_covers_the_whole_building():
    """Looking straight down, every point inside the walls meets slate or lead."""
    cover = [face[:3] for role in ('slate', 'lead') for face in CLAY.triangles[role]]

    def covered(x, y):
        for a, b, c in cover:
            d1 = (x - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (y - b[1])
            d2 = (x - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (y - c[1])
            d3 = (x - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (y - a[1])
            if not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0)):
                return True
        return False

    inset = build.WALL + build.THICK + .05
    for k in range(0, build.FRONT_BAYS, 4):
        back = (build.STARTS['east'] - k) % build.BAY_COUNT
        (fx, fy, _), (bx, by, _) = build.LOOP.node(k, inset), build.LOOP.node(back, inset)
        for t in (0, .2, .4, .5, .6, .8, 1):
            assert covered(fx + (bx - fx) * t, fy + (by - fy) * t), (k, t)


def test_gutter_starts_on_the_cornice():
    low = min(p[2] for face in CLAY.triangles['lead'] for p in face[:3])
    assert math.isclose(low, build.CORNICE), 'no slit is left under the gutter edge'


def test_source_lock_matches_the_recorded_prework():
    recorded = json.loads((HERE / 'prework-manifest.json').read_text(encoding='utf-8'))
    assert build.source_lock() == recorded['sources']
    assert recorded['measurement_contract']['houses'] == 20 and recorded['keeper_claimed'] is False


def test_rooms_stay_behind_the_walls():
    """No floor, ceiling or inner wall comes nearer an outside face than the wall's own
    inner face. A spine wall once ran out to the face of each end."""
    nodes = build.NODES

    def depth(x, y):
        best = math.inf
        for (ax, ay), (bx, by) in zip(nodes, nodes[1:] + nodes[:1]):
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best

    points = {(round(p[0], 3), round(p[1], 3), p[2] < build.BAND) for role in ('floor', 'interior') for face in CLAY.triangles[role] for p in face[:3]}
    for x, y, ground in points:
        assert depth(x, y) >= (.90 if ground else build.WALL + build.THICK) - 1e-3, (x, y)


def test_floors_meet_the_walls_in_every_bay():
    slabs = [face for face in CLAY.triangles['floor'] if abs(face[0][2] - build.FIRST) < 1e-9 and abs(face[1][2] - build.FIRST) < 1e-9 and abs(face[2][2] - build.FIRST) < 1e-9]
    corners = {(round(p[0], 3), round(p[1], 3)) for face in slabs for p in face[:3]}
    inset = build.WALL + build.THICK
    for k in list(range(build.FRONT_BAYS + 1)) + list(range(build.STARTS['back'], build.STARTS['east'] + 1)):
        x, y, _ = build.LOOP.node(k, inset)
        assert (round(x, 3), round(y, 3)) in corners, k


def test_no_floor_shares_a_plane_with_the_stone_above_or_below_it():
    """The band the columns stand on stops at the wall's inner face. It once ran 80 mm under
    the first floor at the same level, two colours in one plane."""
    inner = build.WALL + build.THICK
    nodes = build.NODES

    def depth(x, y):
        best = math.inf
        for (ax, ay), (bx, by) in zip(nodes, nodes[1:] + nodes[:1]):
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best

    level = [face for face in CLAY.triangles['dressed'] if all(abs(p[2] - build.FIRST) < 1e-9 for p in face[:3])]
    assert level, 'the band has a top'
    for x, y in {(round(p[0], 3), round(p[1], 3)) for face in level for p in face[:3]}:
        if all(math.hypot(x - nx, y - ny) > 3 for nx, ny in (nodes[k] for k in (0, 60, 66, 126))):     # mitres at the four corners reach further in
            assert depth(x, y) <= inner + .01, (x, y)                          # 80 mm was the fault; a mitre adds a millimetre or two


def test_each_column_is_one_unbroken_stack_from_band_to_architrave():
    """Plinth, base, shaft, necking, cushion and abacus follow one another with no slit.
    The cushion once started 20 mm above the necking."""
    spans = []
    lathe, block = build.lathe, build.block

    def spy_lathe(clay, role, x, y, profile, **options):
        spans.append((min(z for _, z in profile), max(z for _, z in profile)))
        return lathe(clay, role, x, y, profile, **options)

    def spy_block(clay, role, x, y, along, inward, half_u, half_n, z0, z1, **options):
        spans.append((z0, z1))
        return block(clay, role, x, y, along, inward, half_u, half_n, z0, z1, **options)

    build.lathe, build.block = spy_lathe, spy_block
    try:
        build.column(Clay(), 30)
    finally:
        build.lathe, build.block = lathe, block
    spans.sort()
    assert math.isclose(spans[0][0], build.FIRST) and math.isclose(max(hi for _, hi in spans), build.ARCHITRAVE)
    reach = spans[0][1]
    for lo, hi in spans[1:]:
        assert lo <= reach + 1e-9, f'slit between {reach:.3f} and {lo:.3f}'
        reach = max(reach, hi)


def test_ironwork_stands_on_something():
    iron = CLAY.triangles['iron']
    assert math.isclose(min(p[2] for face in iron for p in face[:3]), .02), 'the lowest railing bars stand on the paving'
    bay = build.Bay(build.LOOP, 31)                       # a window bay near the middle of the front
    here = [face for face in iron if all(p[2] > build.FIRST - 1e-9 for p in face[:3])
            and all(math.hypot(p[0] - bay.p(bay.length / 2, 0, 0)[0], p[1] - bay.p(bay.length / 2, 0, 0)[1]) < bay.length / 2 + .05 for p in face[:3])]
    assert here and math.isclose(min(p[2] for face in here for p in face[:3]), build.FIRST), 'each guard has posts standing on the band'
    along = [(p[0] - bay.origin[0]) * bay.along[0] + (p[1] - bay.origin[1]) * bay.along[1] for face in here for p in face[:3] if p[2] < build.FIRST + .095]
    assert min(along) < build.PLINTH and max(along) > bay.length - build.PLINTH, 'the bottom rail is let into both plinth blocks'


def test_sills_stand_proud_of_the_wall_beneath_them():
    tops = {round(max(p[2] for p in face[:3]), 3) for face in CLAY.triangles['dressed']}
    for lo, _ in (build.GROUND_WINDOW, build.FIRST_WINDOW, build.SECOND_WINDOW):
        assert round(lo + .012, 3) in tops and round(lo, 3) not in {round(p[2], 3) for face in CLAY.triangles['dressed'] for p in face[:3] if abs(p[2] - lo) < 1e-9}
