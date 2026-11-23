"""Build the Silo Cluster as an RLASM 6.1 architectural-clay GLB.

Exact variant: `machine_aesthetic_heavy_industrial` / `heavy_silo_cluster` (variant 2). The locked
oblique and roof views show two rows of eight poured-concrete silos with ribbed conical caps and
ring railings, a concrete elevator shaft standing proud of the front row between its two halves,
a corrugated head house on the shaft, a corrugated conveyor gallery running the length of the
cluster over the caps on steel frames, walkways along the front row, and two loading sheds with
truck bays at the foot of the shaft. The catalogue's street view of this variant is a grey render
of the old LEGO model, not a picture of the building, so it is recorded as a source conflict.

    python3 tools/catalogue_silo_cluster_pilot/build.py --output <new directory> --version <n>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, renders and
boards are review material and stay outside Git until a person activates them.

Frame: x along the rows (east), y north, z up, metres, grade z = 0; the loading front faces -y and
the cluster is centred on the line between the two rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from itertools import pairwise
from pathlib import Path

import mapbox_earcut
import numpy as np
import shapely
from shapely.geometry import Point, box

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'catalogue_plus15_concrete_pilot'))
from clay_kit import METHOD, Clay

SLUG = 'silo-cluster'
ARCHETYPE, VARIANT, INDEX = 'machine_aesthetic_heavy_industrial', 'heavy_silo_cluster', 2
TITLE = 'Silo Cluster'
SOURCE_DIR = 'frontend/public/archetypes/buildings/machine_aesthetic_heavy_industrial'
SOURCES = {'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}
EXCLUDED = {'front': f'variant_{INDEX}.png'}     # a grey render of the old LEGO model; see source_conflicts

# ---- measured contract (metres) -------------------------------------------------------------------
PX = .0756                                        # roof view scale: the back row's eight caps span 1010 px for 76.4 m
R = 4.6                                           # silo radius
PITCH = 9.6                                       # centre spacing along a row and between the rows
ROW_Y = (-PITCH / 2, PITCH / 2)                   # front and back row centre lines
BACK_X = [(k - 3.5) * PITCH for k in range(8)]    # the back row runs straight through
SHAFT = (3.6, -11.7, .2, 36.0)                    # elevator shaft: half-width, front and back y, top
FRONT_X = sorted([s * (SHAFT[0] + .3 + R + PITCH * k) for s in (-1, 1) for k in range(4)])   # the front row parts round the shaft
CYL, CONE = 26.0, 3.0                             # silo wall height and cap rise
POUR = 2.4                                        # pour lines on the silo walls
GALLERY = (43.0, 2.3, 31.0, 34.4, 35.0)           # conveyor gallery: half-length, half-width, floor, eaves, ridge
HEAD = (4.7, -12.0, .2, 36.0, 47.0, 49.5)         # head house, seated on the shaft for its whole depth: half-width, front and back y, foot, eaves, ridge
VENTS = [(-2.4, -6.0), (2.4, -6.0)]               # roof ventilators on the head house
SHEDS = [(-22.7, -SHAFT[0]), (SHAFT[0], 22.7)]    # loading sheds either side of the shaft, each under two front silos (x ranges)
SHED = (-15.4, -9.4, 5.8, 8.0)                    # shed front and back y, eave heights at front and back
BAYS = [-17.0, -10.0, 10.0, 17.0]                 # truck bay centres, 3.8 m wide and 4.6 m high
WALKWAY = (10.0, -10.8, -9.6)                     # walkways along the front row: deck height, outer and inner y
APRON = 4.0

PALETTE = {  # role -> flat colour (sRGB), in node order
    'apron': {'colour': '#a6a39b', 'module': 'yard'},
    'pad': {'colour': '#bdb9b0', 'module': 'yard'},
    'concrete': {'colour': '#bab5ab', 'module': 'silos and shaft', 'roughness': .9},
    'pour': {'colour': '#a29d93', 'module': 'silos and shaft', 'roughness': .9},
    'cap': {'colour': '#9fa2a1', 'module': 'silo caps', 'roughness': .6},
    'rib': {'colour': '#6c7072', 'module': 'silo caps', 'roughness': .5},
    'steel': {'colour': '#c3c6c7', 'module': 'corrugated cladding', 'roughness': .5},
    'corrugation': {'colour': '#a3a8ab', 'module': 'corrugated cladding', 'roughness': .5},
    'roof': {'colour': '#8f9498', 'module': 'roofs', 'roughness': .5},
    'frame': {'colour': '#5c6165', 'module': 'steelwork', 'roughness': .45},
    'spout': {'colour': '#7a7f84', 'module': 'discharge spouts'},
    'door': {'colour': '#4b5056', 'module': 'doors'},
    'interior': {'colour': '#3e3c38', 'module': 'bays'},
    'louvre': {'colour': '#4f5458', 'module': 'louvres'},
    'glass': {'colour': '#2a2a28', 'module': 'windows', 'alpha': .55, 'roughness': .2},
}


# ---- helpers ---------------------------------------------------------------------------------------
def flat_region(clay, role, geometry, z, up=True):
    for poly in getattr(geometry, 'geoms', [geometry]):
        if poly.is_empty or poly.geom_type != 'Polygon' or poly.area < 1e-6:
            continue
        rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
        verts = np.array([p for r in rings for p in r], dtype=np.float64)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        idx = mapbox_earcut.triangulate_float64(verts, ends)
        for k in range(0, len(idx), 3):
            a, b, c = (tuple(verts[i]) + (z,) for i in idx[k:k + 3])
            clay.tri(role, a, b, c, facing=(0, 0, 1 if up else -1))


def circle(x, y, r, n=32, phase=0.0):
    return [(x + r * math.cos(2 * math.pi * (k + phase) / n), y + r * math.sin(2 * math.pi * (k + phase) / n)) for k in range(n)]


def beam(clay, role, a, b, size=.18):
    """A square member between two 3D points."""
    d = np.subtract(b, a)
    length = float(np.linalg.norm(d))
    if length < 1e-6:
        return
    d = d / length
    up = np.array([0, 0, 1.0]) if abs(d[2]) < .9 else np.array([1.0, 0, 0])
    u = np.cross(d, up)
    u /= np.linalg.norm(u)
    v = np.cross(d, u)
    h = size / 2
    ring = [np.array(a) + h * (su * u + sv * v) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    clay.loft(role, [[tuple(p) for p in ring], [tuple(p + d * length) for p in ring]])


def wall(clay, role, p, q, z0, z1, facing):
    if z1 - z0 > 1e-4:
        clay.quad(role, (p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1), (p[0], p[1], z1), facing=(*facing[:2], 0))


def niche(clay, origin, u, n, u0, u1, z0, z1, depth, back, glass=False):
    """An opening in a planar wall: four reveals going `depth` in, and a back face (and glass)."""
    def at(s, z, d=0.0):
        return (origin[0] + s * u[0] - d * n[0], origin[1] + s * u[1] - d * n[1], z)
    corners = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    for (sa, za), (sb, zb) in pairwise(corners + corners[:1]):
        mid_s, mid_z = (sa + sb) / 2 - (u0 + u1) / 2, (za + zb) / 2 - (z0 + z1) / 2
        clay.quad('concrete' if back != 'interior' else 'steel', at(sa, za), at(sb, zb), at(sb, zb, depth), at(sa, za, depth),
                  facing=(-u[0] * mid_s, -u[1] * mid_s, -mid_z))
    clay.quad(back, at(u0, z0, depth), at(u1, z0, depth), at(u1, z1, depth), at(u0, z1, depth), facing=(n[0], n[1], 0))
    if glass:
        clay.quad('glass', at(u0, z0, .12), at(u1, z0, .12), at(u1, z1, .12), at(u0, z1, .12), facing=(n[0], n[1], 0))


def holed_wall(clay, role, origin, u, n, outline, holes):
    """A planar wall polygon in (s, z) with rectangular holes, triangulated."""
    poly = shapely.geometry.Polygon(outline)
    if holes:
        poly = poly.difference(shapely.union_all([box(a, c, b, d) for a, b, c, d in holes]))
    for part in getattr(poly, 'geoms', [poly]):
        rings = [list(part.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in part.interiors]
        verts = np.array([p for r in rings for p in r], dtype=np.float64)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        idx = mapbox_earcut.triangulate_float64(verts, ends)
        for k in range(0, len(idx), 3):
            a, b, c = ((origin[0] + verts[i][0] * u[0], origin[1] + verts[i][0] * u[1], verts[i][1]) for i in idx[k:k + 3])
            clay.tri(role, a, b, c, facing=(n[0], n[1], 0))


# ---- silos ----------------------------------------------------------------------------------------
def silos():
    return [(x, ROW_Y[0]) for x in FRONT_X] + [(x, ROW_Y[1]) for x in BACK_X]


def cap_height(x, y, cx, cy):
    """Height of a silo's conical cap above plan point (x, y)."""
    d = math.hypot(x - cx, y - cy)
    return CYL + CONE * max(0.0, 1 - d / R)


def silo(clay, cx, cy, front):
    ring0 = [(*p, 0.0) for p in circle(cx, cy, R)]
    ring1 = [(*p, CYL) for p in circle(cx, cy, R)]
    clay.loft('concrete', [ring0, ring1], caps=(False, False), smooth=30)
    z = POUR
    while z < CYL - .5:                                                    # pour lines
        lo = [(*p, z - .05) for p in circle(cx, cy, R + .02)]
        hi = [(*p, z + .05) for p in circle(cx, cy, R + .02)]
        clay.loft('pour', [lo, hi], caps=(False, False), smooth=30)
        z += POUR
    rim = [(*p, CYL) for p in circle(cx, cy, R + .08)]
    top = [(*p, CYL + CONE - .1) for p in circle(cx, cy, .45)]
    clay.loft('cap', [rim, top], caps=(False, True), smooth=30)
    flat_region(clay, 'cap', Point(cx, cy).buffer(R + .08, quad_segs=8).difference(Point(cx, cy).buffer(R - .02, quad_segs=8)), CYL)
    for k in range(16):                                                    # radial ribs on the cap
        t = 2 * math.pi * (k + .5) / 16
        a = (cx + (R + .05) * math.cos(t), cy + (R + .05) * math.sin(t), CYL + .05)
        b = (cx + .5 * math.cos(t), cy + .5 * math.sin(t), CYL + CONE - .1)
        beam(clay, 'rib', a, b, .1)
    clay.box('cap', cx - .5, cx + .5, cy - .5, cy + .5, CYL + CONE - .1, CYL + CONE + .25)   # hatch at the apex
    posts = circle(cx, cy, R - .15, 24)                                    # ring railing round the cap's edge
    for x, y in posts:
        clay.box('frame', x - .03, x + .03, y - .03, y + .03, cap_height(x, y, cx, cy), cap_height(x, y, cx, cy) + 1.1)
    for p, q in pairwise(posts + posts[:1]):
        zp, zq = cap_height(*p, cx, cy) + 1.1, cap_height(*q, cx, cy) + 1.1
        clay.quad('frame', (*p, zp - .04), (*q, zq - .04), (*q, zq + .04), (*p, zp + .04))
    side = -1 if front else 1                                              # a discharge spout on the outer side
    if not (front and any(a - R <= cx <= b + R for a, b in SHEDS)):
        y0 = cy + side * (R - .1)
        clay.box('spout', cx - .5, cx + .5, min(y0, y0 + side * .9), max(y0, y0 + side * .9), 0.0, 2.6)
        clay.box('spout', cx - .25, cx + .25, min(y0, y0 + side * .9), max(y0, y0 + side * .9), 2.6, 4.6)


# ---- shaft, head house, gallery ------------------------------------------------------------------
def shaft(clay):
    hw, yf, yb, top = SHAFT
    front = ((-hw, yf), (1.0, 0.0), (0.0, -1.0))
    windows = [(-.45, .45, z, z + 1.3) for z in (8.0, 13.0, 18.0, 23.0, 28.0, 32.5)]
    door = [(-.7, .7, 0.0, 2.5)]
    holed_wall(clay, 'concrete', (-hw, yf), (1.0, 0.0), (0.0, -1.0), [(0, 0), (2 * hw, 0), (2 * hw, top), (0, top)],
               [(hw + a, hw + b, c, d) for a, b, c, d in windows + door])
    for a, b, c, d in windows:
        niche(clay, front[0], front[1], front[2], hw + a, hw + b, c, d, 1.2, 'interior', glass=True)
    a, b, c, d = door[0]
    niche(clay, front[0], front[1], front[2], hw + a, hw + b, c, d, .25, 'door')
    for x, n in ((-hw, (-1.0, 0.0)), (hw, (1.0, 0.0))):                    # side faces, with a door onto each walkway
        u = (0.0, 1.0) if n[0] < 0 else (0.0, -1.0)
        origin = (x, yf) if n[0] < 0 else (x, yb)
        length = yb - yf
        s_door = (WALKWAY[1] + WALKWAY[2]) / 2 - yf if n[0] < 0 else yb - (WALKWAY[1] + WALKWAY[2]) / 2
        holes = [(s_door - .5, s_door + .5, WALKWAY[0], WALKWAY[0] + 2.2)]
        holed_wall(clay, 'concrete', origin, u, n, [(0, 0), (length, 0), (length, top), (0, top)], holes)
        niche(clay, origin, u, n, s_door - .5, s_door + .5, WALKWAY[0], WALKWAY[0] + 2.2, .25, 'door')
    wall(clay, 'concrete', (hw, yb), (-hw, yb), 0.0, top, (0, 1))
    z = POUR
    while z < top - .5:                                                    # pour lines on the shaft's front, broken at each opening
        cuts = sorted((a - .1, b + .1) for a, b, c, d in windows + door if c - .1 <= z <= d + .1)
        xs, x = [], -hw
        for a, b in cuts:
            xs.append((x, a))
            x = b
        xs.append((x, hw))
        for a, b in xs:
            if b - a > .05:
                clay.quad('pour', (a, yf - .02, z - .05), (b, yf - .02, z - .05), (b, yf - .02, z + .05), (a, yf - .02, z + .05), facing=(0, -1, 0))
        z += POUR


def head_house(clay):
    hw, yf, yb, foot, eave, ridge = HEAD
    for (p, q), n in ((((-hw, yf), (hw, yf)), (0, -1)), (((hw, yb), (-hw, yb)), (0, 1))):   # gable ends
        clay.polygon('steel', [(*p, foot), (*q, foot), (*q, eave), ((p[0] + q[0]) / 2, p[1], ridge), (*p, eave)], (*n, 0))
    for (p, q), n in ((((hw, yf), (hw, yb)), (1, 0)), (((-hw, yb), (-hw, yf)), (-1, 0))):  # long sides
        wall(clay, 'steel', p, q, foot, eave, n)
    flat_region(clay, 'steel', box(-hw, yf, hw, yb), foot, up=False)
    for side in (-1, 1):                                                   # roof slopes with a small overhang
        edge = eave - (ridge - eave) * .35 / hw                            # the roof plane passes through the wall tops
        clay.quad('roof', (side * (hw + .35), yf - .35, edge), (side * (hw + .35), yb + .35, edge), (0, yb + .35, ridge),
                  (0, yf - .35, ridge), facing=(side, 0, 2))
    x = -hw + .3
    while x < hw - .1:                                                     # corrugation on the gable ends
        for y, d in ((yf - .03, -1), (yb + .03, 1)):
            zt = eave + (ridge - eave) * (1 - abs(x) / hw)
            clay.quad('corrugation', (x - .04, y, foot + .1), (x + .04, y, foot + .1), (x + .04, y, zt - .15), (x - .04, y, zt - .15), facing=(0, d, 0))
        x += .5
    y = yf + .3
    while y < yb - .1:                                                     # and on the long sides
        for xx, d in ((hw + .03, 1), (-hw - .03, -1)):
            clay.quad('corrugation', (xx, y - .04, foot + .1), (xx, y + .04, foot + .1), (xx, y + .04, eave - .15), (xx, y - .04, eave - .15), facing=(d, 0, 0))
        y += .5
    clay.box('louvre', 1.0, 3.4, yf - .02, yf + .2, foot + 1.2, foot + 4.2)    # louvre panel on the front gable, 2 cm proud
    for vx, vy in VENTS:                                                   # ridge ventilators
        seat = eave + (ridge - eave) * (1 - (abs(vx) + .7) / hw) - .1       # down through the roof slope at its low side
        clay.cylinder('steel', vx, vy, seat, ridge + 1.4, .7, steps=16)
        clay.cylinder('roof', vx, vy, ridge + 1.4, ridge + 1.6, .85, steps=16)


def gallery(clay):
    """The conveyor gallery, in two segments that run into the shaft's side faces."""
    hl, hw, floor, eave, ridge = GALLERY
    sh, yb = SHAFT[0], SHAFT[2]

    def roof_z(y):
        return eave + (ridge - eave) * (1 - abs(y) / hw)
    for side in (-1, 1):
        x_in, x_out = side * sh, side * hl
        lo, hi = sorted((x_in, x_out))
        for (p, q), n in ((((lo, -hw), (hi, -hw)), (0, -1)), (((hi, hw), (lo, hw)), (0, 1))):
            wall(clay, 'steel', p, q, floor, eave, n)
        clay.polygon('steel', [(x_out, -hw, floor), (x_out, hw, floor), (x_out, hw, eave), (x_out, 0, ridge), (x_out, -hw, eave)], (side, 0, 0))
        clay.polygon('steel', [(x_in, yb, floor), (x_in, hw, floor), (x_in, hw, eave), (x_in, yb, roof_z(yb))], (-side, 0, 0))   # beyond the shaft's back
        flat_region(clay, 'steel', box(lo, -hw, hi, hw), floor, up=False)
        lo_r, hi_r = (lo - .2, hi) if side < 0 else (lo, hi + .2)
        for s2 in (-1, 1):
            edge = eave - (ridge - eave) * .2 / hw
            clay.quad('roof', (lo_r, s2 * (hw + .2), edge), (hi_r, s2 * (hw + .2), edge), (hi_r, 0, ridge), (lo_r, 0, ridge), facing=(0, s2, 3))
    x = -hl + .25
    while x < hl:
        if abs(x) > sh + .1:
            for y, d in ((-hw - .03, -1), (hw + .03, 1)):
                clay.quad('corrugation', (x - .04, y, floor + .08), (x + .04, y, floor + .08), (x + .04, y, eave - .1), (x - .04, y, eave - .1),
                          facing=(0, d, 0))
        x += .5
    for x in sorted(set(BACK_X + FRONT_X)):                                # steel frames from the caps up to the gallery
        if abs(x) < HEAD[0] + .5:
            continue
        for y in (-hw + .2, hw - .2):
            cx, cy = min(silos(), key=lambda s: math.hypot(s[0] - x, s[1] - y))
            z0 = cap_height(x, y, cx, cy)
            beam(clay, 'frame', (x, y, z0), (x, y, floor), .22)
        beam(clay, 'frame', (x, -hw + .2, floor - .11), (x, hw - .2, floor - .11), .18)       # cross beam under the floor
        cx, cy = min(silos(), key=lambda s: math.hypot(s[0] - x, s[1] + hw))
        beam(clay, 'frame', (x, -hw + .2, cap_height(x, -hw + .2, cx, cy) + .2), (x, hw - .2, floor - .35), .12)


# ---- sheds, walkways, yard -------------------------------------------------------------------------
def sheds(clay):
    yf, yb, ef, eb = SHED
    for x0, x1 in SHEDS:
        holes = [(b - 1.9 - x0, b + 1.9 - x0, 0.0, 4.6) for b in BAYS if x0 < b < x1]
        holed_wall(clay, 'steel', (x0, yf), (1.0, 0.0), (0.0, -1.0), [(0, 0), (x1 - x0, 0), (x1 - x0, ef), (0, ef)], holes)
        for a, b, c, d in holes:
            niche(clay, (x0, yf), (1.0, 0.0), (0.0, -1.0), a, b, c, d, 5.4, 'interior')
            mid = x0 + (a + b) / 2                                         # loading spout over the truck's place
            clay.box('spout', mid - .8, mid + .8, yf + 2.2, yf + 3.8, 3.7, d)
            clay.box('spout', mid - .3, mid + .3, yf + 2.7, yf + 3.3, 3.0, 3.7)
            flat_region(clay, 'pad', box(x0 + a - .4, yf - 6.0, x0 + b + .4, yf), .04)
        for x in (x0, x1):
            n = (-1, 0) if x == x0 else (1, 0)
            if abs(abs(x) - SHAFT[0]) < 1e-6:                              # beside the shaft: close the part in front of it, facing the recess
                ys = SHAFT[1]
                zs = ef + (eb - ef) * (ys - yf) / (yb - yf)
                clay.polygon('steel', [(x, yf, 0.0), (x, ys, 0.0), (x, ys, zs), (x, yf, ef)], (*n, 0))
                continue
            clay.polygon('steel', [(x, yf, 0.0), (x, yb, 0.0), (x, yb, eb), (x, yf, ef)], (*n, 0))
        lo = x0 if abs(abs(x0) - SHAFT[0]) < 1e-6 else x0 - .2                # no overhang into the shaft
        hi = x1 if abs(abs(x1) - SHAFT[0]) < 1e-6 else x1 + .2
        clay.quad('roof', (lo, yf - .4, ef - .05), (hi, yf - .4, ef - .05), (hi, yb, eb), (lo, yb, eb), facing=(0, -.3, 1))
        wall(clay, 'steel', (x1, yb), (x0, yb), 0.0, eb, (0, 1))
        x = x0 + .3
        while x < x1 - .1:                                                 # corrugation over the bays
            clay.quad('corrugation', (x - .04, yf - .03, 4.8), (x + .04, yf - .03, 4.8), (x + .04, yf - .03, ef - .1), (x - .04, yf - .03, ef - .1),
                      facing=(0, -1, 0))
            x += .5


def walkways(clay):
    z, yo, yi = WALKWAY
    for x0, x1 in ((-GALLERY[0] + 1.0, -SHAFT[0]), (SHAFT[0], GALLERY[0] - 1.0)):
        clay.box('frame', x0, x1, yo, yi, z - .15, z)
        for y in (yo, yi - .05):                                           # guard rails on both sides, and at the outer end
            clay.box('frame', x0, x1, y, y + .05, z + 1.05, z + 1.1)
            clay.box('frame', x0, x1, y, y + .05, z + .5, z + .54)
        xe = x0 if x0 < 0 else x1
        clay.box('frame', xe - .025, xe + .025, yo, yi, z + 1.05, z + 1.1)
        x = x0
        while x <= x1 + 1e-6:                                              # posts, and brackets back to the silo walls
            clay.box('frame', x - .03, x + .03, yo, yo + .06, z, z + 1.1)
            x += 1.6
        for sx in FRONT_X:
            if x0 < sx < x1:
                beam(clay, 'frame', (sx, yi, z - .15), (sx, ROW_Y[0] - R + .02, z - 2.2), .14)


def yard(clay):
    hw = SHAFT[0]
    parts = [Point(x, y).buffer(R, quad_segs=8) for x, y in silos()] + [box(-hw, SHAFT[1], hw, SHAFT[2])]
    parts += [box(x0, SHED[0], x1, SHED[1]) for x0, x1 in SHEDS]
    whole = shapely.union_all(parts)
    yard_area = box(-GALLERY[0] - APRON, SHED[0] - 6.0 - APRON, GALLERY[0] + APRON, ROW_Y[1] + R + APRON)
    pads = shapely.union_all([box(b - 2.3, SHED[0] - 6.0, b + 2.3, SHED[0]) for b in BAYS])
    flat_region(clay, 'apron', yard_area.difference(whole).difference(pads), .02)


def build():
    clay = Clay()
    for x, y in silos():
        silo(clay, x, y, front=y < 0)
    shaft(clay)
    head_house(clay)
    gallery(clay)
    sheds(clay)
    walkways(clay)
    yard(clay)
    return clay


# ---- records -----------------------------------------------------------------------------------------
def entrances():
    doors = [{'kind': 'truck bay', 'centre_xy_m': [b, SHED[0]], 'facing': 'street front (-y)', 'clear_width_m': 3.8, 'door_height_m': 4.6,
              'threshold_top_m': 0.0, 'rise_m': 0.0} for b in BAYS]
    doors.append({'kind': 'shaft door', 'centre_xy_m': [0.0, SHAFT[1]], 'facing': 'street front (-y)', 'clear_width_m': 1.4, 'door_height_m': 2.5,
                  'threshold_top_m': 0.0, 'rise_m': 0.0})
    return doors


def source_lock_for(role, files=SOURCES):
    path = ROOT / SOURCE_DIR / files[role]
    data = path.read_bytes()
    lock = {'role': role, 'repo_path': f'{SOURCE_DIR}/{files[role]}', 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        fields = dict(line.split(' ', 1) for line in data.decode('ascii').splitlines() if ' ' in line)
        lock.update(bytes=int(fields['size']), sha256=fields['oid'].removeprefix('sha256:'))
    return lock


CAMERAS = ('front', 'front_corner', 'aerial', 'top', 'left_side', 'right_side', 'rear', 'rear_side', 'facade_close', 'architecture_close',
           'glass_close', 'caps_close', 'gallery_close', 'bays_contact', 'base_contact', 'match_oblique', 'match_top')


def prework(candidate):
    return {
        'candidate': candidate, 'method': METHOD, 'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'title': TITLE,
        'sources': [source_lock_for(r) for r in SOURCES],
        'excluded_sources': [source_lock_for('front', EXCLUDED) | {'reason': 'grey render of the old LEGO model'}],
        'gate_a': {'front_oblique_top_coherent': False,
                   'note': ('The variant has no usable street view: variant_2.png is a grey render of the old LEGO model. The oblique '
                            'and roof views agree and are the authority. A person must rule on this before activation, as for the '
                            'concert hall and the ski-slope plant.')},
        'measurement_contract': {
            'scale_basis': ('No image carries a scale. The back row\'s eight caps span 1010 px in the roof view; with the front row '
                            '(1095 px) parted round the shaft, that is set to 76.4 m, matching the catalogue\'s suggested 80 m length, '
                            'so the silos are 9.2 m across at a 9.6 m pitch (0.0756 m/px). Heights are proportioned in the oblique: '
                            'the walls about 2.8 silo diameters (26 m) with 3 m caps, the gallery just over the cap tips, the shaft '
                            'to 36 m and the head house to a 47 m eave. A pinhole fit to nine points gave 29 m walls and a 47 m '
                            'eave at 32 px RMS, too loose to govern.'),
            'source_measurements': {
                'oblique': ['High view from the south-west toward rail yards and sheds.',
                            ('Two rows of eight poured-concrete silos with pour lines, ribbed conical caps with ring railings and '
                             'discharge spouts at their feet.'),
                            ('A concrete elevator shaft with a column of small windows stands proud of the front row between its two '
                             'halves; a corrugated head house with a gable roof, a louvre and two ridge ventilators sits on it.'),
                            'A corrugated conveyor gallery runs the length of the cluster over the caps on steel frames.',
                            ('Walkways along the front row at about mid-height; two loading sheds, each as wide as two silos, with '
                             'two truck bays each either side of the foot of the shaft, and concrete pads in front.')],
                'top': ['View from above and a little south of overhead, north up.',
                        'Back row of eight caps 1010 px long; front row 1095 px, parted round the shaft.',
                        ('Gallery 1110 px long and 60 px wide along the middle of the cluster; head house 124 px wide, its ridge '
                         'running north-south, with two ventilators.'),
                        'Sheds and pads at the foot of the shaft; tall parts lean north by about 2 px per metre of height.']},
            'source_conflicts': [('variant_2.png, the street view, is a grey render of the old LEGO model, not a picture of this '
                                  'building. It is excluded; the oblique and roof views govern. Needs a ruling by a person.'),
                                 ('The roof view is not overhead: tall parts lean north. Plan positions come from features at one '
                                  'height (the caps) and from the feet of the shaft and sheds.'),
                                 ('The catalogue suggests an 80 by 50 m footprint; the images show a long cluster about 86 by 25 m '
                                  'with its yard; the images govern.')],
            'hidden_assumptions': [('The back row\'s north side, the ends and the shaft\'s back are not seen; the back row carries '
                                    'discharge spouts like the front (inferred).'),
                                   ('The walkways are reached from the shaft through doors at their level; their stairs are not '
                                    'modelled.'),
                                   'The bays are shallow lit-less interiors 5.4 m deep; the plant inside the head house is not modelled.',
                                   'Rail tracks, wagons, roads, trucks and neighbouring sheds belong to the site and are not modelled.']},
        'roof_contract': {'form': 'ribbed conical silo caps with ring railings, a gabled gallery and head house, shed roofs over the bays',
                          'weathering': 'every roof closes its volume; the gallery and head house stand on steel frames and the shaft'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()}},
        'identity_contract': ['two rows of eight concrete silos with ribbed conical caps', 'a concrete elevator shaft proud of the front row',
                              'a corrugated head house with ventilators', 'a conveyor gallery over the caps on steel frames',
                              'loading sheds with truck bays at the foot of the shaft'],
        'programme_contract': {'silos': 16, 'truck_bays': 4, 'walkways': 2},
        'contact_contract': {'base_datum_m': 0.0, 'ground': 'a concrete yard round the cluster with pads in front of the bays; nothing below grade'},
        'camera_roster': list(CAMERAS),
        'mandatory_review_views': [f'{name}.png' for name in CAMERAS if not name.startswith('match_')],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--output', required=True, help='new candidate directory; must not exist')
    parser.add_argument('--version', type=int, default=1)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise SystemExit(f'{out} exists. RLASM never overwrites a candidate; choose a new directory.')
    candidate = f'{SLUG}-clay-v{args.version:03d}'
    clay = build()
    data = clay.glb(PALETTE, {'archetype_id': ARCHETYPE, 'variant_id': VARIANT})
    out.mkdir(parents=True)
    model = out / f'{candidate}.glb'
    model.write_bytes(data)
    lo, hi = clay.bounds()
    counts = clay.triangle_counts()
    report = {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'state': 'build_valid', 'keeper_claimed': False, 'runtime_seed_allowed': False,
        'sources': [source_lock_for(r) for r in SOURCES],
        'model': {'file': model.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'meshes': len(counts), 'materials': len(counts), 'textures': 0, 'images': 0,
                  'triangles': sum(counts.values()), 'triangles_by_role': counts},
        'native_dimensions_m': {'width': round(hi[0] - lo[0], 4), 'depth': round(hi[1] - lo[1], 4), 'height': round(hi[2] - lo[2], 4)},
        'authoring_bounds_m': {'min': [round(v, 4) for v in lo], 'max': [round(v, 4) for v in hi]},
        'heights_m': {'silo_wall': CYL, 'cap_tip': CYL + CONE, 'gallery_ridge': GALLERY[4], 'shaft': SHAFT[3], 'head_house_eave': HEAD[4],
                      'head_house_ridge': HEAD[5]},
        'silos': len(silos()),
        'entrances': {'doors': entrances()},
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
