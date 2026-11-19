"""Deterministic checks on the laneway-house generator. Run: pytest tools/catalogue_laneway_house_pilot"""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('laneway_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

IDENTITY = {'archetype_id': build.ARCHETYPE, 'variant_id': build.VARIANT}
CLAY = build.build()
DATA = CLAY.glb(build.PALETTE, IDENTITY)
DOCUMENT = json.loads(DATA[20:20 + struct.unpack('<I', DATA[12:16])[0]])
FACES = {'garage_front': build.GARAGE_FRONT, 'entry': build.ENTRY, 'street_upper': build.STREET_UPPER, 'lane': build.LANE,
         'back': build.BACK, 'west': build.WEST}


def tris(role):
    return [face[:3] for face in CLAY.triangles.get(role, [])]


def local(face, p):
    """A point in a face's own frame: (u along, n outward, z)."""
    dx, dy = p[0] - face.o[0], p[1] - face.o[1]
    return dx * face.a[0] + dy * face.a[1], dx * face.out[0] + dy * face.out[1], p[2]


def centroid(t):
    return tuple(sum(p[i] for p in t) / 3 for i in range(3))


def test_build_is_deterministic_and_matches_the_recorded_candidate():
    assert build.build().glb(build.PALETTE, IDENTITY) == DATA
    record = json.loads((HERE / 'candidate.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(DATA).hexdigest() == record['model_sha256'], 'generator output no longer matches the recorded candidate; build a new version'
    assert len(DATA) == record['model_bytes']


def test_container_matches_the_clay_library_convention():
    assert 'textures' not in DOCUMENT and 'images' not in DOCUMENT
    assert len(DOCUMENT['nodes']) == len(DOCUMENT['meshes']) == len(DOCUMENT['materials']) <= 20
    for node in DOCUMENT['nodes']:
        assert node['name'].startswith('CLAY_') and node['extras']['representation_kind'] == 'architectural_clay'
        assert node['extras']['variant_id'] == build.VARIANT
    assert 'CLAY_GLASS' in [m['name'] for m in DOCUMENT['materials']]


def test_nothing_below_grade_and_the_ridge_under_the_laneway_limit():
    lo, hi = CLAY.bounds()
    assert abs(lo[2]) < 1e-9
    assert hi[2] < 8.5, 'the catalogue gives 8.5 m as the laneway-house height limit'
    record = json.loads((HERE / 'candidate.json').read_text(encoding='utf-8'))
    native = record['native_dimensions_m']
    assert abs(hi[0] - lo[0] - native['width']) < 1e-3 and abs(hi[1] - lo[1] - native['depth']) < 1e-3 and abs(hi[2] - native['height']) < 1e-3


def test_the_roof_is_one_hipped_sheet_at_the_right_pitch():
    x0, x1 = -build.OVERHANG, build.WIDTH + build.OVERHANG
    y0, y1 = -build.OVERHANG, build.DEPTH + build.OVERHANG
    sheet = tris('metal_roof')
    for i in range(1, 30):
        for j in range(1, 30):
            x, y = x0 + (x1 - x0) * (i + .37) / 30.7, y0 + (y1 - y0) * (j + .41) / 30.7
            over = []
            for a, b, c in sheet:
                d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
                u = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / d
                v = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / d
                if u >= -1e-9 and v >= -1e-9 and u + v <= 1 + 1e-9:
                    over.append(u * a[2] + v * b[2] + (1 - u - v) * c[2])
            assert len(over) == 1, (x, y, over)
            inward = min(x - x0, x1 - x, y - y0, y1 - y)
            assert abs(over[0] - (build.FASCIA_TOP + inward * build.PITCH)) < 1e-6


def test_every_seam_stands_on_the_roof_and_under_the_caps_at_its_inner_end():
    x0, x1 = -build.OVERHANG, build.WIDTH + build.OVERHANG
    y0, y1 = -build.OVERHANG, build.DEPTH + build.OVERHANG
    for t in tris('seam'):
        for x, y, z in t:
            assert x0 - .2 <= x <= x1 + .2 and y0 - .2 <= y <= y1 + .2
            inward = min(x - x0, x1 - x, y - y0, y1 - y)
            if inward > -1e-6:
                assert z >= build.FASCIA_TOP + inward * build.PITCH - .035, (x, y, z)


def test_the_corner_window_box_wraps_the_corner_and_stops_at_its_lane_pane():
    """Regression for v003, whose box ran on along the lane face to the panel band."""
    reach = build.CORNER[1] + build.CORNER[2]
    for t in tris('trim'):
        if all(p[0] >= build.WIDTH - 1e-6 for p in t) and all(3.5 < p[2] < 5.6 for p in t) and all(p[1] < build.PANEL_BAND[0] for p in t):
            assert max(p[1] for p in t) <= reach + 1e-6, t
    street, lane = build.OPENINGS['street_upper'][1], build.OPENINGS['lane'][2]
    assert street['kind'] == lane['kind'] == 'corner' and street['z'] == lane['z']
    assert street['u'][1] == build.WIDTH - build.CORNER[2] and lane['u'][0] == build.CORNER[2]


def test_no_room_surface_stands_inside_a_window_or_door_opening():
    for key, face in FACES.items():
        for o in build.OPENINGS[key]:
            (a, b), (c, d) = o['u'], o['z']
            for t in tris('interior') + tris('floor'):
                u, n, z = local(face, centroid(t))
                assert not (a + 1e-6 < u < b - 1e-6 and c + 1e-6 < z < d - 1e-6 and -build.WALL + 1e-6 < n < 1e-6), (key, o['kind'], t)


def test_board_lines_and_mortar_joints_never_cross_an_opening():
    for role in ('cedar_joint', 'mortar'):
        assert tris(role), role
        for t in tris(role):
            for key, face in FACES.items():
                for o in build.OPENINGS[key]:
                    (a, b), (c, d) = o['u'], o['z']
                    u, n, z = local(face, centroid(t))
                    assert not (a < u < b and c < z < d and abs(n) < .02), (role, key, o['kind'])


def test_every_opening_has_glass_set_back_in_its_reveal():
    for key, face in FACES.items():
        for o in build.OPENINGS[key]:
            (a, b), (c, d) = o['u'], o['z']
            found = [t for t in tris('glass') if all(a - 1e-6 <= local(face, p)[0] <= b + 1e-6 and c - 1e-6 <= p[2] <= d + 1e-6
                                                     and -build.WALL < local(face, p)[1] < -.05 for p in t)]
            assert found, (key, o['kind'])


def test_balcony_guard_height_and_its_solid_cedar_end():
    assert build.RAIL_TOP - build.DECK >= 1.07
    rails = [t for t in tris('trim') if all(abs(p[2] - build.RAIL_TOP) < 1e-6 for p in t)]
    assert rails, 'top rail'
    end = [t for t in tris('cedar') if all(p[0] <= .1 and p[1] < 0 for p in t)]
    assert max(p[2] for t in end for p in t) == build.RAIL_TOP


def test_stair_risers_are_equal_and_rise_to_the_upper_floor():
    risers = build.STAIR[3]
    rise = (build.FLOOR2 - build.HALL) / risers
    assert .17 <= rise <= .19 and build.TREAD >= .25
    top = build.STAIR[2] + (risers - 1) * build.TREAD
    slot = build.OPENINGS['lane'][1]
    assert slot['u'][0] > top, 'the ground slot window looks past the top of the stair, not into its side'


def test_downpipes_reach_their_gutters_and_the_ground():
    pipes = [t for t in tris('trim') if any(abs(p[1] - (build.DEPTH - .25)) < .05 for p in t)]
    tops = max(p[2] for t in pipes for p in t)
    bottoms = min(p[2] for t in pipes for p in t)
    assert abs(tops - 5.86) < 1e-6 and bottoms <= .05


def test_entrances_are_one_front_door_one_garden_door_and_the_garage():
    doors = {door['kind']: door for door in build.entrances()}
    assert set(doors) == {'front door', 'garden door', 'garage door'}
    assert doors['front door']['clear_width_m'] >= .8 and doors['garden door']['clear_width_m'] >= .65
    assert doors['garage door']['clear_width_m'] >= 4.2
    assert all(door['rise_m'] <= .21 for door in doors.values())
