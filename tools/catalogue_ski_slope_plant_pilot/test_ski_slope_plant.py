"""Deterministic checks on the ski-slope plant generator. Run: pytest tools/catalogue_ski_slope_plant_pilot"""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from shapely.geometry import Point

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ski_slope_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
spec = importlib.util.spec_from_file_location('ski_slope_verify', HERE / 'verify.py')
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
    for role in ('TURF', 'STAIR', 'GLASS', 'CLIMB', 'STACK'):
        assert f'CLAY_{role}' in names


def test_nothing_below_grade_and_the_stack_is_the_top():
    lo, hi = CLAY.bounds()
    assert abs(lo[2]) < 1e-9 and abs(hi[2] - build.STACK[1]) < 1e-9
    native = RECORD['native_dimensions_m']
    assert abs(hi[0] - lo[0] - native['width']) < 1e-3 and abs(hi[1] - lo[1] - native['depth']) < 1e-3


def test_the_block_is_the_measured_roof_view_outline():
    assert abs(294 * build.PX - 2 * build.HALF_W) < .1 and abs(780 * build.PX - 2 * build.HALF_L) < .2
    assert build.footprint().contains(build.main_block())


def test_one_straight_parapet_and_a_walkable_slope():
    assert abs(build.parapet(build.Y_LOW) - build.H0) < 1e-9 and abs(build.parapet(build.HALF_L) - build.HS) < 1e-9
    assert build.parapet(build.Y_LOW - 5) == build.H0, 'the low end is level'
    assert build.SLOPE < .3
    rise = build.walk(build.STAIR_Y[1]) - build.walk(build.STAIR_Y[0])
    assert rise / round(rise / build.RISE) < .19
    assert abs(build.Z_LOWER - build.walk(build.TERRACE_Y[0])) < 1e-9 and abs(build.Z_UPPER - build.Z_LOWER - build.UPPER_STEP) < 1e-9
    assert build.PAVILION[3] < build.HALF_L - (build.HALF_W - build.INNER), 'the pavilion stands inside the parapet'


def test_the_east_face_is_the_street_front_with_the_entrance_and_climbing_wall():
    doors = build.entrances()
    visitor = next(d for d in doors if d['kind'] == 'visitor entrance')
    assert visitor['centre_xy_m'][1] == -build.HALF_W and visitor['rise_m'] == 0.0
    assert build.to_auth(build.PIER[1], 0)[1] < -build.HALF_W, 'the climbing wall stands proud of the street front'
    lo, hi = CLAY.bounds()
    assert lo[1] < -build.HALF_W - 4 and hi[0] > build.HALF_L, 'plan east is authoring -y, plan north is +x'


def test_the_wings_hold_the_low_end_and_the_stack():
    whole = build.footprint()
    (sx, sy), *_ = build.STACK
    assert whole.contains(Point(sx, sy).buffer(4.0)) and not build.main_block().contains(Point(sx, sy))
    assert build.HP < build.H0 and build.east_base(-30) == build.HP and build.east_base(0) == 0.0


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
    assert 'catalogue_ski_slope_plant_pilot/review.html' in (HERE / 'render.cjs').read_text(encoding='utf-8')
    assert (HERE / 'review.html').is_file()
