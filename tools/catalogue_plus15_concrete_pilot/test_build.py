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
        for face in faces:
            a, b, c = face[:3]
            normal = cross(sub(b, a), sub(c, a))
            assert dot(normal, normal) > 1e-16 and all(math.isfinite(v) for p in face for v in p)
            for given in face[3:]:                          # rounded surfaces carry their own normals
                assert math.isclose(dot(given, given), 1, abs_tol=1e-9) and dot(given, normal) > 0


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
    profile = build.spandrel_profile(4.15)
    top = 4.15 + build.SPANDREL
    assert min(d for d, _ in profile) == 0 and math.isclose(max(z for _, z in profile), top - .03)
    assert (build.STEP, top - build.CAP - .10) in profile and (build.STEP + .08, top - build.CAP) in profile, 'main face and reveal sit behind the cap strip'
    assert math.isclose(build.SPANDREL + build.HEAD - build.SILL, 3.9) and math.isclose(build.FLOORS[1] + build.SILL - build.SPANDREL, build.SOFFIT)
    for side in build.SIDES:                                    # every band's main face, on all four sides
        axis = 1 if side.name in ('front', 'rear') else 0
        plane = side.p(0, build.STEP, 0)[axis]
        faces = [face for face in CLAY.triangles['concrete'] if all(abs(p[axis] - plane) < 1e-6 for p in face)]
        assert len(faces) >= 40, side.name
        assert all(dot(cross(sub(b, a), sub(c, a)), side.out) > 0 for a, b, c in faces), side.name


def test_walkway_sits_at_the_third_storey_on_the_east_flank():
    floor = build.FLOORS[build.BRIDGE_STOREY - 1]
    points = [p for face in CLAY.triangles['bridge'] for p in face[:3]]
    xs, ys, zs = ([p[k] for p in points] for k in range(3))
    assert build.BRIDGE_STOREY == 3 and math.isclose(max(xs), build.HX + build.BRIDGE_LENGTH)
    assert floor - .65 < min(zs) < floor and floor + build.HEAD < max(zs) <= floor + build.HEAD + 1.5 + 1e-9
    centre = -build.HY + sum(build.BRIDGE_U) / 2
    assert math.isclose(min(ys), centre - build.BRIDGE_HALF) and math.isclose(max(ys), centre + build.BRIDGE_HALF)
    panes = [p[2] for face in CLAY.triangles['glass'] for p in face[:3] if all(q[0] > build.HX - build.STEP - 1e-6 for q in face[:3])]
    assert .42 < (max(panes) - min(panes)) / (max(zs) - min(zs)) < .50, 'the glazed band is close to half the tube, as the street view shows'


def test_walkway_mouth_is_closed_against_the_building():
    """A solid jamb fills the gap between the band face and the building's own glass line."""
    floor = build.FLOORS[build.BRIDGE_STOREY - 1]
    for u in (build.BRIDGE_U[0] + .17, build.BRIDGE_U[1] - .17):
        _, y, _ = build.EAST.p(u, 0, 0)
        for setback in (build.STEP, build.FRAME_IN):            # the jamb's outer and inner faces
            x = build.HX - setback
            face = [f for f in CLAY.triangles['bridge'] if all(abs(p[0] - x) < 1e-9 for p in f[:3])
                    and min(p[1] for p in f[:3]) <= y <= max(p[1] for p in f[:3])]
            assert face, 'nothing stands in the walkway mouth'
            assert min(p[2] for f in face for p in f[:3]) <= floor and max(p[2] for f in face for p in f[:3]) >= floor + build.HEAD


def test_band_pieces_never_overlap_an_opening():
    marks = []
    original = build.Clay.loft

    def spy(self, role, rings, **options):
        if role == 'concrete':
            marks.append(sorted(p[1] for ring in rings for p in ring))
        return original(self, role, rings, **options)

    build.Clay.loft = spy
    try:
        build.band(build.Clay(), build.EAST, build.spandrel_profile(8.05), build.bay_lines(build.EAST), [build.BRIDGE_U])
    finally:
        build.Clay.loft = original
    spans = sorted((ys[0] + build.HY, ys[-1] + build.HY) for ys in marks)
    assert all(a < b for a, b in spans), 'no inverted sliver'
    assert all(b <= build.BRIDGE_U[0] + 1e-9 or a >= build.BRIDGE_U[1] - 1e-9 for a, b in spans)


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


def test_kit_lofts_face_outward_far_from_the_origin_and_when_concave():
    """A band piece is a long concave section a long way from the origin. The kit once
    judged its facing from the origin and turned some pieces inside out."""
    section = build.spandrel_profile(4.15, 1.6, lip=True)
    area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(section, section[1:] + section[:1]))) / 2
    for order in (1, -1):
        for a, b in ((9.015, 17.985), (17.985, 9.015)):
            clay = Clay()
            clay.loft('x', [[build.FRONT.p(u, d, z) for d, z in section[::order]] for u in (a, b)], smooth=40 if order < 0 else None)
            volume = sum(dot(f[0], cross(f[1], f[2])) for f in clay.triangles['x']) / 6
            assert math.isclose(volume, area * 8.97, rel_tol=1e-9)


def signed_areas(outline):
    return [((outline[j][0] - outline[i][0]) * (outline[k][1] - outline[i][1]) - (outline[j][1] - outline[i][1]) * (outline[k][0] - outline[i][0])) / 2
            for i, j, k in earclip(outline)]


def test_kit_polygon_helpers():
    concave = [(0, 0), (4, 0), (4, 3), (2, 1), (0, 3)]
    assert math.isclose(sum(signed_areas(concave)), 8.0) and min(signed_areas(concave)) > 0


def test_every_section_the_building_uses_triangulates_cleanly():
    """No triangle of a cap may be wound backwards. An earlier ear clipper cut one corner
    of the first band across its own outline, which left that cap wrong."""
    sections = [build.spandrel_profile(4.15, 1.6, lip=True), build.spandrel_profile(8.05), build.parapet_profile(19.75)]
    for outline in sections + [section[::-1] for section in sections]:
        outline = [(d, z) for d, z in outline]
        areas = signed_areas(outline)
        shoelace = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))) / 2
        assert min(areas) > 0 and math.isclose(sum(areas), shoelace, rel_tol=1e-9)
    assert inset_polygon([(0, 0), (2, 0), (2, 2), (0, 2)], .5) == [(.5, .5), (1.5, .5), (1.5, 1.5), (.5, 1.5)]


def test_every_loft_in_the_building_faces_outward():
    """Each swept piece, measured about its own centre, must enclose a positive volume."""
    original, checked = Clay.loft, []

    def spy(self, role, rings, **options):
        before = len(self.triangles.get(role, []))
        original(self, role, rings, **options)
        middle = [sum(p[k] for ring in rings for p in ring) / sum(len(ring) for ring in rings) for k in range(3)]
        added = self.triangles[role][before:]
        checked.append(sum(dot(sub(f[0], middle), cross(sub(f[1], middle), sub(f[2], middle))) for f in added))

    Clay.loft = spy
    try:
        build.build()
    finally:
        Clay.loft = original
    assert len(checked) > 150 and min(checked) > 0
