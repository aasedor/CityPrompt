"""Deterministic checks on the silo-cluster generator. Run: pytest tools/catalogue_silo_cluster_pilot"""
import hashlib
import importlib.util
import json
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('silo_cluster_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
spec = importlib.util.spec_from_file_location('silo_cluster_verify', HERE / 'verify.py')
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
    for role in ('CONCRETE', 'CAP', 'STEEL', 'FRAME', 'INTERIOR'):
        assert f'CLAY_{role}' in names


def test_nothing_below_grade_and_the_ventilators_are_the_top():
    lo, hi = CLAY.bounds()
    assert abs(lo[2]) < 1e-9 and abs(hi[2] - (build.HEAD[5] + 1.6)) < 1e-9
    native = RECORD['native_dimensions_m']
    assert abs(hi[0] - lo[0] - native['width']) < 1e-3 and abs(hi[1] - lo[1] - native['depth']) < 1e-3


def test_two_rows_of_eight_measured_from_the_roof_view():
    back = [x for x, y in build.silos() if y > 0]
    front = [x for x, y in build.silos() if y < 0]
    assert len(back) == len(front) == 8
    assert abs((max(back) - min(back) + 2 * build.R) - 1010 * build.PX) < .2, 'back row: 1010 px'
    assert abs((max(front) - min(front) + 2 * build.R) - 1095 * build.PX) < 1.2, 'front row: 1095 px, parted round the shaft'
    centres = build.silos()
    assert all(math.dist(a, b) >= 2 * build.R - 1e-9 for i, a in enumerate(centres) for b in centres[i + 1:])


def test_the_stack_of_parts_is_coherent():
    assert build.CYL + build.CONE < build.GALLERY[2] < build.GALLERY[3] < build.SHAFT[3] == build.HEAD[3] < build.HEAD[4] < build.HEAD[5]
    hw, yf, yb, _ = build.SHAFT
    assert all(math.hypot(max(abs(x) - hw, 0), max(yf - y, y - yb, 0)) >= build.R - 1e-9 for x, y in build.silos())
    assert yf < build.ROW_Y[0] - build.R, 'the shaft stands proud of the front row'
    assert build.WALKWAY[0] < build.CYL and build.SHED[3] < build.WALKWAY[0]


def test_the_loading_front_has_four_bays_and_a_door():
    doors = build.entrances()
    assert sorted(d['kind'] for d in doors) == ['shaft door'] + ['truck bay'] * 4
    for x0, x1 in build.SHEDS:
        assert sum(1 for b in build.BAYS if x0 < b < x1) == 2
    assert all(d['rise_m'] == 0.0 for d in doors)


def test_sources_are_locked_and_the_lego_render_is_excluded():
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
    assert 'catalogue_silo_cluster_pilot/review.html' in (HERE / 'render.cjs').read_text(encoding='utf-8')
    assert (HERE / 'review.html').is_file()
