"""Bounded tied-arch correction; preserve the pinned failed candidates intact."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.claude_bridge_corrections.tied_arch_plan import trapezoid_plan
from tools.claude_bridge_corrections.geometry_contract import approach_stair_treads
import family_tiedarch as F
import clay_core as C
import geometry as G

PALETTE = dict(F.PALETTE)
LIGHT_RIG = F.LIGHT_RIG
STAIRS = approach_stair_treads(26, F.ZQ)
OUTER = STAIRS[-1][1]


def point(x, y, z):
    return trapezoid_plan(x, y) + (z,)


def manifest(version):
    m = F.manifest(version)
    # Source-matched observer directions are authored in the local bridge frame.
    details = [
        ('facade_close', (0, -21, 5), (0, 0, 7), 28),
        ('architecture_close', (-7, -17, 16), (0, -4, 12), 35),
        ('glass_close', (-8, -3.6, 4.9), (-3.5, -6.2, 4.1), 40),
        ('arch_springing', (-29, -13, 5.7), (-23, -6.15, 4.5), 40),
        ('hangers', (-15, -3.2, 5), (10, -6.3, 7.8), 35),
        ('planter_divider', (-15, 3.6, 5.1), (-4, 1.4, 3.8), 40),
        ('cycle_lane', (-21, 4.2, 4.9), (10, 4, 3.8), 35),
        ('deck_edge', (-9, -14, 2.9), (-2, -6.3, 2.8), 35),
        ('quay_under', (-11, -15, 1.3), (-20, 0, 1.4), 35),
        ('rear_north', (0, 58, 22), (0, 0, 6), 35),
        ('west_approach', (-39, -13, 8), (-27, -2.6, 2.7), 35),
        ('east_approach', (39, 13, 8), (27, -2.6, 2.7), 35),
    ]
    details = [(name, point(*loc), point(*target), lens) for name, loc, target, lens in details]
    cams = G.camera_roster(68, 33, 14.5, details)
    for camera in cams:
        if camera['name'] == 'front':
            camera.update(location=point(-31, 2.6, 5), target=point(0, -1.2, 6.7), lens=24, whole=False)
        elif camera['name'] == 'front_corner':
            camera.update(location=point(-43, -47, 32), target=point(0, 0, 6), lens=35, whole=False)
    m.update(camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])
    m['measurement_contract'].update(
        dimensions_m=dict(width=68, depth=33, height=14.5),
        plan='46 m centre span, 13-degree heading; opposite six-degree end skews, south tie about six percent longer; one transform governs all bridge, bearing and quay geometry',
        inferred='Metric scale, compact quays, bearing shelves and grade-to-quay pedestrian stairs are teaching assumptions. External city blocks omitted. Cycle lane ends on raised quays; stairs imply dismount, not an accessible cycle approach.')
    m['contact_contract'] = ['All bridge, bearing and quay contacts share the same trapezoidal plan transform',
        'Arch springings seat on quay plinths', 'Deck end bearings seat on quay shelves',
        'Two inferred pedestrian stairs physically connect raised quays to grade']
    m['runtime_contract'].update(scale='fixed_native_only', installation='not installed', review='NOT TESTED',
        ground='prepared level grade only; bounded canal scene, pedestrian stairs at ends',
        unsupported=['stretching', 'bending', 'automatic intersections', 'sloped ground', 'engineering or accessibility certification'])
    return m


def compact_quays():
    b = F.RBatch()
    b.box('water', 0, 0, .01, 2 * F.CW, 18, .02)
    for side in (-1, 1):
        b.box('quay', side * 23, 0, (F.ZQ - .06) / 2, 6, 16, F.ZQ - .06)
        b.box('paving', side * 23, 0, F.ZQ - .03, 6, 16, .06)
        for y in (-7.4, 7.4):
            b.box('stone', side * 20.25, y, F.ZQ + .02, .7, 1.2, .14)
        b.box('concrete', side * 19.72, 0, F.ZQ - 1.05, .6, 13.5, .6)
        b.box('concrete', side * 19.95, 0, F.ZQ - .55, .12, 13.5, .5)
        # Walkway continuation across the compact brick quay to inferred stairs.
        for lo, hi, top in STAIRS:
            b.box('paving', side * (lo + hi) / 2, -2.65, top / 2, hi - lo, 4, top)
        for edge in (-1, 1):
            y = -2.65 + edge * 2.08
            b.beam('rail', (side * 26, y, F.ZQ + 1.05), (side * OUTER, y, 1.05), .055)
            for index, (lo, hi, top) in enumerate(STAIRS):
                if index % 3 == 0:
                    x = (lo + hi) / 2
                    rail = F.ZQ * (OUTER - x) / (OUTER - 26) + 1.05
                    b.beam('rail', (side * x, y, top), (side * x, y, rail), .055)
        # Full end landings stay bounded; outer guards do not close the stair exit.
        for y in (-7.85, 7.85):
            F.railing(b, y, side * 23 - 2.9, side * 23 + 2.9, F.ZQ)
    b.flush('bounded canal and raised quays')


def build():
    original_skew, original_angle = F.skew, F.SKEW
    try:
        F.skew = trapezoid_plan
        F.SKEW = 0  # old cosine compensation is replaced by the common plan map
        compact_quays()
        F.deck()
        F.arches()
        F.planter()
    finally:
        F.skew, F.SKEW = original_skew, original_angle
    C.CONTACTS.append(dict(name='Compact trapezoidal tied-arch bridge, raised quays and connected pedestrian approaches',
                           box=[-34, 34, -16.5, 16.5]))
