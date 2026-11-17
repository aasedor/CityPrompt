"""Deterministic checks on the clay generator. Run: pytest tools/catalogue_plus15_concrete_pilot"""
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
from clay_kit import Clay, cross, dot, earclip, inset_polygon, sub  # noqa: E402

IDENTITY = {'archetype_id': build.ARCHETYPE, 'variant_id': build.VARIANT}
CLAY = build.build()
DATA = CLAY.glb(build.PALETTE, IDENTITY)
DOCUMENT = json.loads(DATA[20:20 + struct.unpack('<I', DATA[12:16])[0]])


def test_build_is_deterministic_and_matches_the_recorded_candidate():
    assert build.build().glb(build.PALETTE, IDENTITY) == DATA
    record = json.loads((HERE / 'candidate.json').read_text(encoding='utf-8'))
    import hashlib
    assert hashlib.sha256(DATA).hexdigest() == record['model_sha256'], 'generator output no longer matches the reviewed candidate; build a new version'
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
        assert extras['archetype_id'] == 'calgary_15_connected_tower' and extras['variant_id'] == 'brutalist_concrete_slab'
        assert material['doubleSided'] is True and material['extras']['texture_free'] is True
        assert material['pbrMetallicRoughness']['metallicFactor'] == 0
    for mesh in DOCUMENT['meshes']:
        assert [sorted(primitive['attributes']) for primitive in mesh['primitives']] == [['NORMAL', 'POSITION']]
    glass = next(m for m in DOCUMENT['materials'] if m['name'] == 'CLAY_GLASS')       # the runtime swaps this material by name
    assert glass['alphaMode'] == 'BLEND' and 'KHR_materials_transmission' in glass['extensions']
    shop = next(m for m in DOCUMENT['materials'] if m['name'] == 'CLAY_SHOPGLASS')
    assert shop['alphaMode'] == 'BLEND' and 'extensions' not in shop
    assert DOCUMENT['extensionsUsed'] == ['KHR_materials_transmission', 'KHR_materials_ior']


def test_native_size_grade_and_budget():
    lo, hi = CLAY.bounds()
    assert lo[2] == 0.0, 'nothing may sit below grade'
    assert math.isclose(hi[0] - lo[0], build.W + build.BRIDGE_LENGTH, abs_tol=.01)       # the walkway adds to the east
    assert math.isclose(hi[1] - lo[1], build.D, abs_tol=.01)
    assert math.isclose(hi[2], build.PENT_TOP + .65, abs_tol=.01)                      # the unit on the penthouse roof is the highest point
    assert math.isclose(lo[0], -build.HX, abs_tol=.01) and math.isclose(lo[1], -build.HY, abs_tol=.01)
    assert 12_000 <= sum(CLAY.triangle_counts().values()) <= 180_000


def test_every_triangle_is_sound():
    for faces in CLAY.triangles.values():
        for a, b, c in faces:
            normal = cross(sub(b, a), sub(c, a))
            assert dot(normal, normal) > 1e-16 and all(math.isfinite(v) for p in (a, b, c) for v in p)


def test_five_storeys_with_four_ribbons_on_every_side():
    assert build.STOREYS == 5 == len(build.FLOORS)
    sills = {}
    for a, b, c in CLAY.triangles['glass']:
        zs = [p[2] for p in (a, b, c)]
        for side in build.SIDES:
            plane = side.p(0, build.GLASS, 0)
            axis = 1 if side.name in ('front', 'rear') else 0
            if all(abs(p[axis] - plane[axis]) < 1e-6 for p in (a, b, c)):
                sills.setdefault(side.name, set()).add(round(min(zs), 2))
    for side in build.SIDES:
        expected = {round(floor + build.SILL - .03 + build.RAIL, 2) for floor in build.FLOORS[1:]}
        assert expected <= sills[side.name], side.name


def test_bands_project_as_measured_and_face_outward():
    profile = build.spandrel_profile(4.10)
    assert min(d for d, _ in profile) == 0 and max(z for _, z in profile) == 4.10 + build.SPANDREL - .03
    assert (build.STEP, 4.10 + build.SPANDREL - build.CAP) in profile, 'main face must sit behind the cap strip'
    front = [face for face in CLAY.triangles['concrete'] if all(abs(p[1] + build.HY - build.STEP) < 1e-6 for p in face)]
    assert front and all(cross(sub(b, a), sub(c, a))[1] < 0 for a, b, c in front)


def test_walkway_sits_at_the_third_storey_on_the_east_flank():
    floor = build.FLOORS[build.BRIDGE_STOREY - 1]
    xs = [p[0] for face in CLAY.triangles['bridge'] for p in face]
    ys = [p[1] for face in CLAY.triangles['bridge'] for p in face]
    zs = [p[2] for face in CLAY.triangles['bridge'] for p in face]
    assert build.BRIDGE_STOREY == 3 and math.isclose(max(xs), build.HX + build.BRIDGE_LENGTH)
    assert floor - .65 < min(zs) < floor and floor + build.HEAD < max(zs) <= floor + build.HEAD + 1.5 + 1e-9
    centre = -build.HY + sum(build.BRIDGE_U) / 2
    assert math.isclose(min(ys), centre - build.BRIDGE_HALF) and math.isclose(max(ys), centre + build.BRIDGE_HALF)


def test_one_public_entrance_with_a_level_threshold():
    entrance = build.entrance()
    assert entrance['rise_m'] < .04 and entrance['clear_width_m'] > 1.8 and entrance['facade'] == 'front'
    a, b = build.bays(build.FRONT)[3]
    assert a < entrance['centre_xy_m'][0] + build.HX < b, 'second bay from the east corner'


def test_source_lock_matches_the_recorded_prework():
    recorded = json.loads((HERE / 'prework-manifest.json').read_text(encoding='utf-8'))
    assert build.source_lock() == recorded['sources']
    assert recorded['measurement_contract']['storeys'] == 5 and recorded['keeper_claimed'] is False


def test_kit_lofts_face_outward_whatever_the_ring_order():
    for order in (1, -1):
        clay = Clay()
        ring = [(0, 0), (2, 0), (2, 1), (0, 1)][::order]
        clay.loft('x', [[(x, y, 0) for x, y in ring], [(x, y, 3) for x, y in ring]])
        volume = sum(dot(a, cross(b, c)) for a, b, c in clay.triangles['x']) / 6
        assert math.isclose(volume, 6.0)


def test_kit_polygon_helpers():
    concave = [(0, 0), (4, 0), (4, 3), (2, 1), (0, 3)]
    area = sum(abs((concave[j][0] - concave[i][0]) * (concave[k][1] - concave[i][1]) - (concave[j][1] - concave[i][1]) * (concave[k][0] - concave[i][0]))
               for i, j, k in earclip(concave)) / 2
    assert math.isclose(area, 8.0)
    assert inset_polygon([(0, 0), (2, 0), (2, 2), (0, 2)], .5) == [(.5, .5), (1.5, .5), (1.5, 1.5), (.5, 1.5)]
