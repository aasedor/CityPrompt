"""Deterministic checks on the concert-hall generator. Run: pytest tools/catalogue_concert_hall_pilot"""
import hashlib
import importlib.util
import json
import math
import struct
from itertools import pairwise
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('concert_hall_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
spec = importlib.util.spec_from_file_location('concert_hall_verify', HERE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

IDENTITY = {'archetype_id': build.ARCHETYPE, 'variant_id': build.VARIANT}
CLAY = build.build()
DATA = CLAY.glb(build.PALETTE, IDENTITY)
DOCUMENT = json.loads(DATA[20:20 + struct.unpack('<I', DATA[12:16])[0]])
RECORD = json.loads((HERE / 'candidate.json').read_text(encoding='utf-8'))


def test_build_is_deterministic_and_matches_the_recorded_candidate():
    assert build.build().glb(build.PALETTE, IDENTITY) == DATA
    assert hashlib.sha256(DATA).hexdigest() == RECORD['model_sha256'], 'generator output no longer matches the recorded candidate; build a new version'
    assert len(DATA) == RECORD['model_bytes']


def test_container_matches_the_clay_library_convention():
    assert 'textures' not in DOCUMENT and 'images' not in DOCUMENT
    assert len(DOCUMENT['nodes']) == len(DOCUMENT['meshes']) == len(DOCUMENT['materials']) <= 36
    for node in DOCUMENT['nodes']:
        assert node['name'].startswith('CLAY_') and node['extras']['representation_kind'] == 'architectural_clay'
        assert node['extras']['variant_id'] == build.VARIANT
    names = [m['name'] for m in DOCUMENT['materials']]
    for role in ('GLASS', 'OCULUS', 'SHELL', 'SEATS', 'FINS'):
        assert f'CLAY_{role}' in names


def test_nothing_below_grade_and_the_shells_under_25_m():
    lo, hi = CLAY.bounds()
    assert abs(lo[2]) < 1e-9
    assert hi[2] < 25.0
    native = RECORD['native_dimensions_m']
    assert abs(hi[0] - lo[0] - native['width']) < 1e-3 and abs(hi[1] - lo[1] - native['depth']) < 1e-3 and abs(hi[2] - native['height']) < 1e-3


def test_the_podium_is_the_measured_roof_view_outline():
    xs, ys = zip(*build.superellipse(build.PODIUM_A, build.PODIUM_B))
    assert abs(max(xs) - min(xs) - 88.0) < .01 and abs(max(ys) - min(ys) - 64.4) < .01, 'roof view: 888 by 650 px at 0.0991 m/px'
    assert build.GF_TOP < build.ROOF < build.COPING and build.COPING - build.GF_TOP < build.GF_TOP, 'the glazing is at least as tall as the band'


def test_the_shells_stand_on_the_roof_and_spiral_round_the_oculus():
    cx, cy = build.OCULUS_C
    rims = [p for control in (build.SHELL_A, build.SHELL_B) for p in verify.rim(control)]
    feet = MultiPoint([(cx + p[3] * math.cos(math.radians(p[4])), cy + p[3] * math.sin(math.radians(p[4]))) for p in rims])
    assert Polygon(build.podium_ring(1.0)).buffer(-3.0).contains(feet), 'every shell foot at least 3 m inside the roof guard'
    assert all(p[2] >= build.LIP_Z - 1e-9 for p in rims)
    assert max(p[2] for p in verify.rim(build.SHELL_A)) > max(p[2] for p in verify.rim(build.SHELL_B)), 'the west shell is the taller'
    assert build.SHELL_A[0][0] == build.SHELL_B[-1][0] == build.NOTCH
    assert build.catmull(build.SHELL_A, build.NOTCH)[1] > build.catmull(build.SHELL_B, build.NOTCH)[1], 'the west shell steps up over the east at the notch'
    assert build.SHELL_A[-1][0] - 360 < build.SHELL_B[0][0], 'a gap at the south-east lets the path reach the lip'
    assert build.ring_width(build.NOTCH) == build.RING[0] and build.ring_width(build.RING[1]) == 0.0


def test_the_doors_and_the_auditorium_are_recorded():
    doors = build.entrances()
    assert sorted(d['kind'] for d in doors) == ['east doors', 'main doors', 'service door']
    main = next(d for d in doors if d['kind'] == 'main doors')
    assert main['facing_deg'] == -90.0 and abs(main['centre_xy_m'][0]) < 1e-6 and main['leaves'] >= 4
    assert all(d['rise_m'] <= .15 for d in doors)
    hall = build.programme()
    assert hall['tiers'] == 11 and hall['stalls_seats_estimate'] > 200


def test_every_opening_starts_and_stops_on_a_shared_ring_vertex():
    angles = build.band_angles()
    edges = [build.RIBBON[0], build.RIBBON[1], *build.LOADING] + [e for zone in build.door_zones().values() for e in zone]
    for edge in edges:
        assert min(abs(((a - edge % 360 + 180) % 360) - 180) for a in angles) < 1e-9, edge
    widths = {}
    for kind, (lo, hi) in build.door_zones().items():
        inside = [build.polar_point(t, build.GLASS_SET) for t in angles if build.in_range(t, lo, hi)]
        widths[kind] = [math.dist(p, q) for p, q in pairwise(inside)]
    assert all(1.1 < w < 1.3 for kind in ('main doors', 'east doors') for w in widths[kind]), 'door leaves of about 1.2 m'


def test_the_foyer_stair_climbs_through_its_well_to_the_upper_storey():
    x0, x1, foot_y, head, rise, well = build.stair_geometry()
    assert rise < .19 and build.STAIR['run'] >= .28
    assert abs(build.FOYER + rise * build.STAIR['risers'] - build.UPPER) < 1e-9
    assert well.bounds == (x0, head, x1, head + build.STAIR['well'])
    headroom_from = foot_y - (build.GF_TOP - .1 - 2.1 - build.FOYER) / rise * build.STAIR['run']
    assert head + build.STAIR['well'] >= headroom_from, 'two metres of headroom where the stair passes under the ceiling'
    upper = Polygon(build.podium_ring(0.0)).difference(Polygon(build.podium_ring(build.UPPER_DEPTH)))
    assert upper.contains(well), 'the well opens into the upper storey'


def test_sources_are_locked_and_the_lego_preview_is_excluded():
    prework = build.prework(RECORD['candidate'])
    assert [lock['role'] for lock in prework['sources']] == ['oblique', 'top']
    assert prework['excluded_sources'][0]['role'] == 'front' and prework['gate_a']['front_oblique_top_coherent'] is False
    committed = json.loads((HERE / 'prework-manifest.json').read_text(encoding='utf-8'))
    assert committed == prework


def test_every_review_view_has_a_camera_and_whole_views_keep_the_building_in_frame():
    roster = json.loads((HERE / 'cameras.json').read_text(encoding='utf-8'))['views']
    assert set(build.CAMERAS) == set(roster)
    for name in verify.WHOLE_VIEWS:
        assert max(abs(v) for v in verify.view_extent(roster[name])) <= .94, name


def test_the_review_page_and_renderer_belong_to_this_pilot():
    assert 'catalogue_concert_hall_pilot/review.html' in (HERE / 'render.cjs').read_text(encoding='utf-8')
    assert (HERE / 'review.html').is_file()
