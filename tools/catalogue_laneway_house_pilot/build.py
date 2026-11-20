"""Build the Garden Studio laneway house as an RLASM 6.1 architectural-clay GLB.

Exact variant: `vancouver_laneway_house` / `laneway_garden_studio` (variant 3). The three
locked images show a two-storey laneway house: a brick garage block with a glass-railed
balcony on its roof, a recessed corner porch under a flat canopy, a cedar upper storey
with sliding doors and a boxed corner window, a dark panel band on the lane side, and a
low hipped standing-seam roof. The model is plain constructive geometry written with
the shared `clay_kit`; nothing here needs Blender.

    python3 tools/catalogue_laneway_house_pilot/build.py --output <new directory> --version <n>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, its
renders and boards are review material and stay outside Git until a human activates them.

Frame: x east along the street front, y north from the street toward the garden, z up,
metres. The lane runs along the east side (x = WIDTH). Grade is z = 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'catalogue_plus15_concrete_pilot'))
from clay_kit import METHOD, Clay, cross, sub, unit

SLUG = 'laneway-garden-studio'
ARCHETYPE, VARIANT, INDEX = 'vancouver_laneway_house', 'laneway_garden_studio', 3
TITLE = 'Garage Suite'
SOURCE_DIR = 'frontend/public/archetypes/buildings/vancouver-laneway-house'
SOURCES = {'front': f'variant_{INDEX}.png', 'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}

# ---- measured contract (metres) ------------------------------------------------
WIDTH, DEPTH = 7.90, 8.60        # main two-storey volume: street front to garden back
PROJECT = 1.50                   # the garage block, balcony and porch canopy stand this far in front of it
GARAGE_X = 5.55                  # the brick garage block and balcony run from x = 0 to here; the porch from here to the lane
WALL = .30                       # outer face to inner face
SLAB, DECK = 2.85, 3.13          # underside of the first floor and canopy; top of the balcony deck and canopy
FLOOR2 = 3.15                    # upper floor level
BAND = (2.85, 3.25, .03, .05)    # floor band: bottom, top, how far it stands proud, how far it runs into the wall
PLATE = 5.78                     # top of the upper walls, the soffit and the ceiling
OVERHANG, FASCIA_TOP = .45, 6.00
PITCH = 5 / 12                   # 5 in 12 on the side faces; the front and back faces are steeper
RIDGE = 2.00                     # ridge length, front to back
PLINTH = .30                     # exposed concrete under the cedar
HALL = .34                       # floor of the entry hall and back room, two steps above grade
STEP = .16                       # the lower step of the stoop and of the garden step
GARAGE_DOOR = (.45, 4.70, 2.42)  # left, right, head: a 14 by 8 ft door; it opens at the slab, 0.02
PANEL_BAND = (3.00, 5.80, .05)   # the dark panel band on the lane face: from, to (along y) and how proud
PANEL_JOINTS = (3.70, 4.40, 5.10)   # vertical joints between its four panels
CORNER = (5.80, .95, .08, .05)   # corner window: street pane from x, lane pane to y, frame width, how far the box stands proud
RAIL_TOP = 4.22
APRON = 1.20                     # pavers in front of the garage door and the stoop
STAIR = (6.60, 7.55, 1.45, 16)   # stair: x from, x to, foot (y), risers
POST = 7.67                      # porch post, centre x; the canopy runs on past it to the lane face
TREAD = .25
BOARD = .15                      # cedar board exposure; a shadow line marks each board
COURSE = .076                    # brick course; a mortar bed joint 10 mm high marks each one

PALETTE = {  # role -> flat colour (sRGB), in node order
    'pavers': {'colour': '#9a9894', 'module': 'site paving'},
    'concrete': {'colour': '#b8b3aa', 'module': 'foundation and stoop'},
    'brick': {'colour': '#7d5040', 'module': 'garage block'},
    'cedar': {'colour': '#bb8458', 'module': 'cedar cladding'},
    'cedar_joint': {'colour': '#7e5434', 'module': 'cedar cladding'},
    'mortar': {'colour': '#957a6c', 'module': 'garage block'},
    'panel': {'colour': '#45484a', 'module': 'panel band'},
    'panel_joint': {'colour': '#2b2e31', 'module': 'panel band'},
    'trim': {'colour': '#25282b', 'module': 'frames, band, gutters and rails', 'roughness': .55},
    'garage_door': {'colour': '#232a29', 'module': 'garage door', 'roughness': .6},
    'deck': {'colour': '#a5a29b', 'module': 'balcony'},
    'roofing': {'colour': '#3a3d40', 'module': 'canopy'},
    'metal_roof': {'colour': '#7d8085', 'module': 'roof', 'roughness': .5},
    'seam': {'colour': '#888b90', 'module': 'roof', 'roughness': .45},
    'floor': {'colour': '#8a7258', 'module': 'rooms'},
    'interior': {'colour': '#d9d3c7', 'module': 'rooms'},
    'glass': {'colour': '#3d464f', 'module': 'glazing', 'alpha': .45, 'roughness': .24, 'transmission': .28},
}


def r6(v):
    return round(v, 6)


class Face:
    """A vertical wall plane seen from outside. `origin` is its left end, `along` the unit
    direction to the right; the outward normal is along turned clockwise. A point is
    p(u, n, z): u along the face, n outward from it (negative is into the wall)."""

    def __init__(self, origin, along):
        self.o, self.a = origin, along
        self.out = (along[1], -along[0])

    def p(self, u, n, z):
        return (r6(self.o[0] + self.a[0] * u + self.out[0] * n), r6(self.o[1] + self.a[1] * u + self.out[1] * n), r6(z))

    def quad(self, clay, role, u0, u1, n, z0, z1, sign=1):
        clay.quad(role, self.p(u0, n, z0), self.p(u1, n, z0), self.p(u1, n, z1), self.p(u0, n, z1),
                  facing=(self.out[0] * sign, self.out[1] * sign, 0.0))

    def side(self, clay, role, u, n0, n1, z0, z1, sign):
        """A face square to the wall at u, facing along +a (sign 1) or -a."""
        clay.quad(role, self.p(u, n0, z0), self.p(u, n1, z0), self.p(u, n1, z1), self.p(u, n0, z1),
                  facing=(self.a[0] * sign, self.a[1] * sign, 0.0))

    def flat(self, clay, role, u0, u1, n0, n1, z, sign):
        clay.quad(role, self.p(u0, n0, z), self.p(u1, n0, z), self.p(u1, n1, z), self.p(u0, n1, z), facing=(0.0, 0.0, float(sign)))

    def box(self, clay, role, u0, u1, n0, n1, z0, z1):
        a, b = self.p(u0, n0, z0), self.p(u1, n1, z1)
        clay.box(role, a[0], b[0], a[1], b[1], z0, z1)


# The four faces of the main volume, and the three of the projecting garage block.
STREET_UPPER = Face((0.0, 0.0), (1.0, 0.0))
GARAGE_FRONT = Face((0.0, -PROJECT), (1.0, 0.0))
PORCH_RETURN = Face((GARAGE_X, -PROJECT), (0.0, 1.0))      # the brick pier's side, facing the porch
ENTRY = Face((GARAGE_X, 0.0), (1.0, 0.0))
LANE = Face((WIDTH, 0.0), (0.0, 1.0))
BACK = Face((WIDTH, DEPTH), (-1.0, 0.0))
WEST = Face((0.0, DEPTH), (0.0, -1.0))


# ---- openings -------------------------------------------------------------------
def opening(u0, u1, z0, z1, kind, **extra):
    return {'u': (u0, u1), 'z': (z0, z1), 'kind': kind, **extra}


OPENINGS = {
    'garage_front': [opening(GARAGE_DOOR[0], GARAGE_DOOR[1], .02, GARAGE_DOOR[2], 'garage')],
    'entry': [opening(.20, 1.70, HALL, 2.65, 'entry', mullions=(1.28,))],
    'street_upper': [opening(1.50, 4.90, FLOOR2, 5.45, 'slider', mullions=(2.35, 3.20, 4.05)),
                     opening(CORNER[0], WIDTH - CORNER[2], 3.75, 5.35, 'corner', mullions=(7.05,), transoms=((4.60, 7.05, WIDTH),), reveal='trim',
                             skip='b')],
    'lane': [opening(CORNER[2], CORNER[1], .95, 2.45, 'window'), opening(5.22, 5.72, .95, 2.10, 'window'),
             opening(CORNER[2], CORNER[1], 3.75, 5.35, 'corner', reveal='trim', skip='a'), opening(5.22, 5.72, 3.95, 5.25, 'window')],
    'back': [opening(.65, 1.60, HALL, 2.55, 'door'), opening(4.80, 6.00, 1.00, 2.30, 'window', mullions=(5.40,)),
             opening(1.90, 2.90, 4.35, 5.25, 'window'), opening(5.30, 6.70, 3.85, 5.25, 'window', mullions=(6.00,))],
    'west': [opening(.70, 1.70, 1.60, 2.30, 'window'), opening(1.80, 3.00, 3.95, 5.25, 'window', mullions=(2.40,))],
}


def inside(o, u, z):
    (a, b), (c, d) = o['u'], o['z']
    return a - 1e-9 <= u <= b + 1e-9 and c - 1e-9 <= z <= d + 1e-9


def skin(clay, face, u0, u1, z0, z1, openings, material, cuts=((), ()), inner=(None, None), thick=WALL, inner_u=None):
    """One wall as a grid of faces. `material(u, z)` gives (role, proud) for the outer face
    of each cell, or (None, 0) where something else owns the surface. Every cell edge is
    shared with its neighbour, so no hairline shows. Openings get reveals of the wall's
    own thickness, cut through every layer; `inner` limits the interior face in z."""
    iu0, iu1 = inner_u or (u0, u1)
    us = sorted({u0, u1, *(v for o in openings for v in o['u']), *(v for v in (*cuts[0], iu0, iu1) if u0 < v < u1)})
    zs = sorted({z0, z1, *(v for o in openings for v in o['z']), *(v for v in cuts[1] if z0 < v < z1)})
    zi0, zi1 = inner[0] if inner[0] is not None else z0, inner[1] if inner[1] is not None else z1
    cells = {}
    for i, (ua, ub) in enumerate(pairwise(us)):
        for j, (za, zb) in enumerate(pairwise(zs)):
            um, zm = (ua + ub) / 2, (za + zb) / 2
            if any(inside(o, um, zm) for o in openings):
                continue
            role, proud = material(um, zm)
            cells[i, j] = (role, proud)
            if role is not None:
                face.quad(clay, role, ua, ub, proud, za, zb)
                if role == 'cedar':
                    shadow_lines(clay, face, ua, ub, za, zb, proud)
                elif role == 'brick':
                    bed_joints(clay, face, ua, ub, za, zb, proud)
            if zi0 - 1e-9 <= za and zb <= zi1 + 1e-9 and iu0 - 1e-9 <= ua and ub <= iu1 + 1e-9:
                face.quad(clay, 'interior', ua, ub, -thick, za, zb, sign=-1)
    # where a proud surface meets a flush one, close the step; an opening's reveal closes its own edge
    last_i, last_j = len(us) - 2, len(zs) - 2
    for (i, j), (role, proud) in cells.items():
        if role is None or proud <= 1e-9:
            continue
        for k, sign, u in ((i - 1, -1, us[i]), (i + 1, 1, us[i + 1])):
            if 0 <= k <= last_i and (k, j) not in cells:
                continue
            other = cells.get((k, j))
            lower = other[1] if other and other[0] is not None else 0.0
            if proud > lower + 1e-9:
                face.side(clay, role, u, lower, proud, zs[j], zs[j + 1], sign)
        for k, sign, z in ((j - 1, -1, zs[j]), (j + 1, 1, zs[j + 1])):
            if not 0 <= k <= last_j or (i, k) not in cells:
                continue
            other = cells[i, k]
            lower = other[1] if other[0] is not None else 0.0
            if proud > lower + 1e-9:
                face.flat(clay, role, us[i], us[i + 1], lower, proud, z, sign)
    for o in openings:
        reveal(clay, face, o, us, zs, material, thick)


def reveal(clay, face, o, us, zs, material, thick):
    (a, b), (c, d) = o['u'], o['z']
    role, proud = material((a + b) / 2, d + .01)
    role = o.get('reveal') or role or 'cedar'
    floor = 'concrete' if o['kind'] in ('garage', 'door', 'entry') else role
    for za, zb in pairwise(zs):
        if c - 1e-9 <= za and zb <= d + 1e-9:
            if o.get('skip') != 'a':
                face.side(clay, role, a, -thick, proud, za, zb, 1)
            if o.get('skip') != 'b':
                face.side(clay, role, b, -thick, proud, za, zb, -1)
    for ua, ub in pairwise(us):
        if a - 1e-9 <= ua and ub <= b + 1e-9:
            face.flat(clay, role, ua, ub, -thick, proud, d, -1)
            face.flat(clay, floor, ua, ub, -thick, proud, c, 1)


def courses(clay, face, role, ua, ub, za, zb, n, start, pitch, height):
    """A strip `height` tall every `pitch` from `start`, clipped to this cell, so a course
    that crosses a cell edge continues on the next cell rather than vanishing."""
    k = math.floor((za - start) / pitch)
    while True:
        z = round(start + k * pitch, 6)
        if z >= zb - 1e-6:
            break
        lo, hi = max(z, za), min(z + height, zb)
        if hi - lo > 1e-4 and z > start - 1e-9:
            face.quad(clay, role, ua, ub, n, lo, hi)
        k += 1


def shadow_lines(clay, face, ua, ub, za, zb, proud):
    """One shadow line at the foot of each cedar board, standing 6 mm proud."""
    courses(clay, face, 'cedar_joint', ua, ub, za, zb, proud + .006, PLINTH + BOARD, BOARD, .014)


def bed_joints(clay, face, ua, ub, za, zb, proud):
    """A mortar bed joint at the top of each brick course, standing 3 mm proud."""
    courses(clay, face, 'mortar', ua, ub, za, zb, proud + .003, COURSE, COURSE, .010)


# ---- frames, glass and doors ---------------------------------------------------
def frame(clay, face, o, proud=0.0, inset=.10, width=.06, depth=.07):
    """A dark frame set back in the reveal, with mullions, transoms and glass."""
    (a, b), (c, d) = o['u'], o['z']
    a, b, c, d = a + .003, b - .003, c + .003, d - .003
    n1, n0 = proud - inset, proud - inset - depth
    face.box(clay, 'trim', a, a + width, n0, n1, c, d)
    face.box(clay, 'trim', b - width, b, n0, n1, c, d)
    face.box(clay, 'trim', a + width, b - width, n0, n1, c, c + width)
    face.box(clay, 'trim', a + width, b - width, n0, n1, d - width, d)
    edges = [a + width, *o.get('mullions', ()), b - width]
    for m in o.get('mullions', ()):
        face.box(clay, 'trim', m - .03, m + .03, n0, n1, c + width, d - width)
    for z, t0, t1 in o.get('transoms', ()):
        face.box(clay, 'trim', max(t0, a + width) + (.03 if t0 > a + width else 0), min(t1, b - width) - (.03 if t1 < b - width else 0),
                 n0 + .005, n1 - .005, z - .03, z + .03)
    face.quad(clay, 'glass', edges[0], edges[-1], (n0 + n1) / 2, c + width, d - width)


def sill(clay, face, o, proud=0.0):
    (a, b), (c, _) = o['u'], o['z']
    face.box(clay, 'trim', a - .03, b + .03, proud - .10, proud + .05, c - .02, c + .012)


def glass_door(clay, face, o, leaf, proud=0.0):
    """A frame with a glass door leaf in it, a pull handle and a threshold."""
    (a, b), (c, d) = o['u'], o['z']
    frame(clay, face, o, proud)
    l0, l1 = leaf
    n = proud - .10 - .035
    for u0, u1 in ((l0, l0 + .07), (l1 - .07, l1)):
        face.box(clay, 'trim', u0, u1, n - .02, n + .02, c + .06, d - .06)
    face.box(clay, 'trim', l0 + .07, l1 - .07, n - .02, n + .02, c + .063, c + .18)
    face.box(clay, 'trim', l0 + .07, l1 - .07, n - .02, n + .02, d - .13, d - .063)
    pull = l1 - .16
    face.box(clay, 'trim', pull - .015, pull + .015, n + .02, n + .07, c + .75, c + 1.65)
    face.box(clay, 'concrete', a - .05, b + .05, proud - .30, proud + .02, c - .02, c + .005)


def garage_door(clay, face, o):
    """Four sectional panels in the reveal, the top one glazed with four lites."""
    (a, b), (c, d) = o['u'], o['z']
    n0, n1 = -.16, -.12
    rise = (d - c) / 4
    for k in range(3):
        face.box(clay, 'garage_door', a + .01, b - .01, n0, n1, c + rise * k + .006, c + rise * (k + 1) - .006)
    s0, s1 = c + rise * 3 + .006, d - .006
    face.box(clay, 'garage_door', a + .01, b - .01, n0, n1, s0, s0 + .13)
    face.box(clay, 'garage_door', a + .01, b - .01, n0, n1, s1 - .13, s1)
    stile = .12
    lite = ((b - a - .02) - 5 * stile) / 4
    for k in range(5):
        u = a + .01 + k * (lite + stile)
        face.box(clay, 'garage_door', u, u + stile, n0, n1, s0 + .13, s1 - .13)
    face.quad(clay, 'glass', a + .01, b - .01, (n0 + n1) / 2, s0 + .13, s1 - .13)
    face.box(clay, 'trim', (a + b) / 2 - .25, (a + b) / 2 + .25, n1, n1 + .03, c + .10, c + .14)   # lift handle on the bottom panel


# ---- walls -----------------------------------------------------------------------
def cedar_with_plinth(u, z):
    if z < PLINTH:
        return 'concrete', 0.0
    return 'cedar', 0.0


def lane_material(u, z):
    if PANEL_BAND[0] < u < PANEL_BAND[1]:
        return 'panel', PANEL_BAND[2]
    if BAND[0] < z < BAND[1]:
        return None, 0.0
    return cedar_with_plinth(u, z)


def back_material(u, z):
    if BAND[0] < z < BAND[1]:
        return None, 0.0
    if z < BAND[0] and u > WIDTH - GARAGE_X:
        return 'brick', 0.0
    return cedar_with_plinth(u, z)


def west_material(u, z):
    if BAND[0] < z < BAND[1]:
        return None, 0.0
    return ('brick', 0.0) if z < BAND[0] else ('cedar', 0.0)


def walls(clay):
    garage = OPENINGS['garage_front']
    skin(clay, GARAGE_FRONT, 0.0, GARAGE_X, 0.0, SLAB, garage, lambda u, z: ('brick', 0.0), inner_u=(WALL, GARAGE_X - WALL))
    garage_door(clay, GARAGE_FRONT, garage[0])
    skin(clay, PORCH_RETURN, 0.0, PROJECT, 0.0, SLAB, [], lambda u, z: ('brick', 0.0), inner_u=(WALL, PROJECT))
    entry = OPENINGS['entry']
    skin(clay, ENTRY, 0.0, WIDTH - GARAGE_X, 0.0, SLAB, entry, cedar_with_plinth, cuts=((), (PLINTH,)), inner=(HALL, None),
         inner_u=(0.0, WIDTH - GARAGE_X - WALL))
    glass_door(clay, ENTRY, entry[0], (.20 + .063, 1.28 - .03))
    upper = OPENINGS['street_upper']
    skin(clay, STREET_UPPER, 0.0, WIDTH, DECK, PLATE, upper, lambda u, z: ('cedar', 0.0), inner=(FLOOR2, None), inner_u=(WALL, WIDTH - WALL))
    slider, corner = upper
    frame(clay, STREET_UPPER, slider, inset=.12)
    frame(clay, STREET_UPPER, corner, inset=.01)
    lane = OPENINGS['lane']
    skin(clay, LANE, 0.0, DEPTH, 0.0, PLATE, lane, lane_material, cuts=((PANEL_BAND[0], PANEL_BAND[1]), (PLINTH, BAND[0], BAND[1])),
         inner=(HALL, None), inner_u=(WALL, DEPTH - WALL))
    frame(clay, LANE, lane[2], inset=.01)
    corner_box(clay, corner, lane[2])
    for o in (lane[0], lane[1], lane[3]):
        proud = PANEL_BAND[2] if PANEL_BAND[0] < (o['u'][0] + o['u'][1]) / 2 < PANEL_BAND[1] else 0.0
        frame(clay, LANE, o, proud, inset=.01)    # seen along the lane at a low angle: glass about 45 mm behind the face
        sill(clay, LANE, o, proud)
    panel_joints(clay)
    back = OPENINGS['back']
    skin(clay, BACK, 0.0, WIDTH, 0.0, PLATE, back, back_material, cuts=((WIDTH - GARAGE_X,), (PLINTH, BAND[0], BAND[1])), inner=(HALL, None),
         inner_u=(WALL, WIDTH - WALL))
    glass_door(clay, BACK, back[0], (.65 + .003 + .06, 1.60 - .003 - .06))
    for o in back[1:]:
        frame(clay, BACK, o)
        sill(clay, BACK, o)
    west = OPENINGS['west']
    skin(clay, WEST, 0.0, DEPTH, 0.0, PLATE, west, west_material, cuts=((), (BAND[0], BAND[1])), inner_u=(WALL, DEPTH - WALL))
    clay.quad('interior', (WALL, WALL, .02), (WALL, 0.0, .02), (WALL, 0.0, SLAB), (WALL, WALL, SLAB), facing=(1, 0, 0))   # garage lining, garage level only
    projection_west = Face((0.0, 0.0), (0.0, -1.0))
    skin(clay, projection_west, 0.0, PROJECT, 0.0, SLAB, [], lambda u, z: ('brick', 0.0), inner_u=(0.0, PROJECT - WALL))
    for o in west:
        frame(clay, WEST, o)
        sill(clay, WEST, o)
    fixtures(clay)


def corner_box(clay, street, lane):
    """The dark box that frames the corner window, standing proud of the cedar on both faces
    and wrapping the corner, with a square post at the corner between the two panes."""
    (a, _), (c, d) = street['u'], street['z']
    (_, b), _ = lane['u'], lane['z']
    _, _, t, out = CORNER
    for z0, z1 in ((c - t, c), (d, d + t)):
        clay.box('trim', a - t, WIDTH + out, -out, 0.0, z0, z1)                 # sill and head across the street face and round the corner
        clay.box('trim', WIDTH, WIDTH + out, 0.0, b + t, z0, z1)                # and along the lane face
    clay.box('trim', a - t, a, -out, 0.0, c, d)                                  # street jamb
    clay.box('trim', WIDTH, WIDTH + out, b, b + t, c, d)                        # lane jamb
    clay.box('trim', WIDTH - t, WIDTH + out, -out, t, c, d)                      # corner post
    clay.box('trim', WIDTH - t - .063, WIDTH, 0.0, t + .063, c + .003, d - .003)    # behind the post, out to both frames: no seam


def panel_joints(clay):
    """Vertical joints between the band's four panels, and one horizontal joint at the floor line."""
    u0, u1, proud = PANEL_BAND
    n = proud + .006
    for u in PANEL_JOINTS:
        LANE.quad(clay, 'panel_joint', u - .006, u + .006, n, 0.0, PLATE)
    for a, b in zip((u0, *PANEL_JOINTS), (*PANEL_JOINTS, u1)):
        LANE.quad(clay, 'panel_joint', a + .006 if a in PANEL_JOINTS else a, b - .006 if b in PANEL_JOINTS else b, n, 3.04, 3.052)


def fixtures(clay):
    """Wall lamps either side of the garage door and a mailbox on the pier by the porch."""
    for u in (.22, 4.95):
        GARAGE_FRONT.box(clay, 'trim', u - .07, u + .07, 0.0, .12, 1.95, 2.22)
        GARAGE_FRONT.quad(clay, 'interior', u - .045, u + .045, .121, 2.0, 2.17)
    GARAGE_FRONT.box(clay, 'trim', 5.20, 5.42, 0.0, .10, 1.25, 1.55)


# ---- the projecting block: balcony, canopy, porch -------------------------------------
def projection(clay):
    bottom, top, proud, into = BAND
    # one floor band round the whole house, at the first floor
    clay.box('trim', -proud, into, -PROJECT - proud, DEPTH + proud, bottom, top)                         # west
    clay.box('trim', WIDTH - into, WIDTH + proud, -PROJECT - proud, DEPTH + proud, bottom, top)           # lane, under the panel band
    clay.box('trim', into, WIDTH - into, -PROJECT - proud, -PROJECT + into, bottom, top)                 # front of balcony and canopy
    clay.box('trim', into, WIDTH - into, DEPTH - into, DEPTH + proud, bottom, top)                       # back
    # balcony deck and canopy, inside the band
    clay.quad('deck', (into, -PROJECT + into, DECK), (GARAGE_X, -PROJECT + into, DECK), (GARAGE_X, 0.0, DECK), (into, 0.0, DECK), facing=(0, 0, 1))
    clay.quad('roofing', (GARAGE_X, -PROJECT + into, DECK), (WIDTH - into, -PROJECT + into, DECK), (WIDTH - into, 0.0, DECK), (GARAGE_X, 0.0, DECK),
              facing=(0, 0, 1))
    clay.quad('cedar', (GARAGE_X, -PROJECT + into, SLAB), (WIDTH - into, -PROJECT + into, SLAB), (WIDTH - into, 0.0, SLAB), (GARAGE_X, 0.0, SLAB),
              facing=(0, 0, -1))
    # stoop, porch post and the paved apron
    clay.box('concrete', GARAGE_X, WIDTH, -PROJECT, 0.0, 0.0, HALL - .02)                              # stoop landing
    clay.box('concrete', GARAGE_X, WIDTH, -PROJECT - .35, -PROJECT, 0.0, STEP)                           # its lower step, in front of the post
    clay.box('cedar', POST - .07, POST + .07, -PROJECT + .06, -PROJECT + .20, HALL - .02, SLAB)
    clay.box('pavers', 0.0, WIDTH, -PROJECT - APRON, -PROJECT, 0.0, .02)
    clay.box('concrete', 6.10, 7.45, DEPTH, DEPTH + .60, 0.0, HALL - .02)                                 # garden landing at the back door
    clay.box('concrete', 6.10, 7.45, DEPTH + .60, DEPTH + .95, 0.0, STEP)                                 # and its lower step
    balcony(clay)


END = .20                          # the balcony's solid cedar west end reaches this far in from the west face


def balcony(clay):
    """Glass guard on dark posts along the front and the porch end; a cedar-clad solid
    end at the west, standing on the band to the height of the guard."""
    top = BAND[1]
    y = -PROJECT + .10
    for x in (1.55, 2.85, 4.15, GARAGE_X - .08):
        clay.box('trim', x - .025, x + .025, y - .025, y + .025, DECK, RAIL_TOP - .03)
    for yy in (-.85, -.08):
        clay.box('trim', GARAGE_X - .105, GARAGE_X - .055, yy - .025, yy + .025, DECK, RAIL_TOP - .03)
    clay.box('trim', END, GARAGE_X - .05, y - .045, y + .045, RAIL_TOP - .03, RAIL_TOP)
    clay.box('trim', GARAGE_X - .125, GARAGE_X - .035, y + .045, -.002, RAIL_TOP - .03, RAIL_TOP)
    posts = [END - .03, 1.55, 2.85, 4.15, GARAGE_X - .08]
    for x0, x1 in pairwise(posts):
        clay.quad('glass', (x0 + .03, y, top + .05), (x1 - .03, y, top + .05), (x1 - .03, y, RAIL_TOP - .06), (x0 + .03, y, RAIL_TOP - .06),
                  facing=(0, -1, 0))
    x = GARAGE_X - .08
    for y0, y1 in ((y + .03, -.88), (-.82, -.11)):
        clay.quad('glass', (x, y0, DECK + .05), (x, y1, DECK + .05), (x, y1, RAIL_TOP - .06), (x, y0, RAIL_TOP - .06), facing=(1, 0, 0))
    screen = Face((-BAND[2], 0.0), (0.0, -1.0))
    screen.box(clay, 'cedar', 0.0, PROJECT + BAND[2], -(END + BAND[2]), 0.0, top, RAIL_TOP)
    screen.box(clay, 'trim', 0.0, PROJECT + BAND[2] + .02, -(END + BAND[2]) - .02, .02, RAIL_TOP, RAIL_TOP + .04)     # dark coping
    for side, n in ((1, .006), (-1, -(END + BAND[2]) - .006)):
        z = top + BOARD
        while z < RAIL_TOP - .05:
            screen.quad(clay, 'cedar_joint', 0.0, PROJECT + BAND[2], n, z, z + .014, sign=side)
            z = round(z + BOARD, 6)


# ---- roof ------------------------------------------------------------------------
def roof(clay):
    """A hipped standing-seam roof over the upper storey, its eaves 0.6 m out on every side,
    with a fascia, a gutter round the eaves, a cedar soffit, hip and ridge caps and a
    downpipe at each back corner."""
    x0, x1, y0, y1 = -OVERHANG, WIDTH + OVERHANG, -OVERHANG, DEPTH + OVERHANG
    half = (x1 - x0) / 2
    ridge_z = FASCIA_TOP + half * PITCH
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r0, r1 = (cx, cy - RIDGE / 2, ridge_z), (cx, cy + RIDGE / 2, ridge_z)
    c = [(x0, y0, FASCIA_TOP), (x1, y0, FASCIA_TOP), (x1, y1, FASCIA_TOP), (x0, y1, FASCIA_TOP)]
    clay.tri('metal_roof', c[0], c[1], r0, facing=(0, -1, 2))
    clay.tri('metal_roof', c[2], c[3], r1, facing=(0, 1, 2))
    clay.polygon('metal_roof', [c[1], c[2], r1, r0], facing=(1, 0, 3))
    clay.polygon('metal_roof', [c[3], c[0], r0, r1], facing=(-1, 0, 3))
    # fascia, soffit and the ceiling inside
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        mid = ((ax + bx) / 2 - cx, (ay + by) / 2 - (y0 + y1) / 2, 0)
        clay.quad('trim', (ax, ay, PLATE), (bx, by, PLATE), (bx, by, FASCIA_TOP), (ax, ay, FASCIA_TOP), facing=mid)
    walls_ring = [(0.0, 0.0), (WIDTH, 0.0), (WIDTH, DEPTH), (0.0, DEPTH)]
    for k in range(4):
        a, b, p, q = walls_ring[k], walls_ring[(k + 1) % 4], ring[(k + 1) % 4], ring[k]
        clay.quad('cedar', (*a, PLATE), (*b, PLATE), (*p, PLATE), (*q, PLATE), facing=(0, 0, -1))
    gutters(clay, x0, x1, y0, y1)
    caps(clay, c, r0, r1)
    seams(clay, x0, x1, y0, y1, half, r0[1] - y0)


def gutters(clay, x0, x1, y0, y1):
    w, lo, hi = .12, 5.86, 5.99
    clay.box('trim', x0 - w, x1 + w, y0 - w, y0, lo, hi)
    clay.box('trim', x0 - w, x1 + w, y1, y1 + w, lo, hi)
    clay.box('trim', x0 - w, x0, y0, y1, lo, hi)
    clay.box('trim', x1, x1 + w, y0, y1, lo, hi)
    y = DEPTH - .25                                  # a downpipe on each side face at the back corner, with a gooseneck under the soffit
    for wall, gutter in ((WIDTH + .01, x1 + w / 2), (-.09, x0 - w / 2)):
        clay.box('trim', wall, wall + .08, y - .04, y + .04, .05, 5.62)
        near, far = sorted((wall + (.08 if wall > 0 else 0.0), gutter + (.04 if wall > 0 else -.04)))
        clay.box('trim', near, far, y - .04, y + .04, 5.54, 5.62)
        clay.box('trim', gutter - .04, gutter + .04, y - .04, y + .04, 5.62, lo)


def along_box(clay, role, a, b, width, below, above):
    """A box whose long axis runs from a to b, `width` across, from `below` under the line
    to `above` over it, square to the line."""
    axis = unit(sub(b, a))
    across = unit(cross(axis, (0.0, 0.0, 1.0)))
    up = cross(across, axis)
    corners = []
    for p in (a, b):
        for s in (-1, 1):
            for t in (-below, above):
                corners.append(tuple(r6(p[i] + across[i] * s * width / 2 + up[i] * t) for i in range(3)))
    (a0, a1, a2, a3, b0, b1, b2, b3) = corners
    middle = tuple((a[i] + b[i]) / 2 for i in range(3))
    for quad in ((a0, a1, a3, a2), (b0, b2, b3, b1), (a0, b0, b1, a1), (a2, a3, b3, b2), (a1, b1, b3, a3), (a0, a2, b2, b0)):
        facing = sub(tuple(sum(p[i] for p in quad) / 4 for i in range(3)), middle)
        clay.quad(role, *quad, facing=facing)


def caps(clay, corners, r0, r1):
    for corner, ridge_end in zip(corners, (r0, r0, r1, r1)):
        span = math.dist(corner, ridge_end)
        start = tuple(corner[i] + (ridge_end[i] - corner[i]) * .12 / span for i in range(3))   # stops short of the eave corner
        along_box(clay, 'seam', start, ridge_end, .16, .03, .045)
    along_box(clay, 'seam', r0, r1, .20, .03, .045)


def roof_height(x, y):
    """The roof sheet's height over a plan point: the lowest of its four face planes."""
    x0, x1, y0, y1 = -OVERHANG, WIDTH + OVERHANG, -OVERHANG, DEPTH + OVERHANG
    half = (x1 - x0) / 2
    run = (y1 - y0) / 2 - RIDGE / 2                 # the front and back faces' run, eave to ridge end
    rise = half * PITCH
    return FASCIA_TOP + min(min(x - x0, x1 - x) * PITCH, min(y - y0, y1 - y) * rise / run)


def seams(clay, x0, x1, y0, y1, half, run):
    """Standing seams square to each eave, 0.43 m apart, each running up to the hip or ridge
    it meets. The side faces rise at PITCH; the front and back faces are steeper, so they
    reach the same ridge height over their shorter run."""
    spacing, w, h = .43, .015, .03
    steep = half * PITCH / run
    faces = [((x0, y0), (1, 0), (0, 1), x1 - x0, steep), ((x1, y1), (-1, 0), (0, -1), x1 - x0, steep),
             ((x1, y0), (0, 1), (-1, 0), y1 - y0, PITCH), ((x0, y1), (0, -1), (1, 0), y1 - y0, PITCH)]
    for (ox, oy), (ex, ey), (wx, wy), length, slope in faces:
        count = int((length - .40) / spacing)
        start = (length - count * spacing) / 2
        for k in range(count + 1):
            s = start + k * spacing
            if slope is steep:                      # hips run from the eave corners to the ridge ends
                reach = min(s, length - s) * run / half - .07
            else:
                reach = min(s * half / run, (length - s) * half / run, half) - .07
            if reach < .12:
                continue

            def at(du, d, lift, ox=ox, oy=oy, ex=ex, ey=ey, wx=wx, wy=wy, s=s, slope=slope):
                return (r6(ox + ex * (s + du) + wx * d), r6(oy + ey * (s + du) + wy * d), r6(FASCIA_TOP + d * slope + lift))
            clay.quad('seam', at(-w, 0, h), at(w, 0, h), at(w, reach, h), at(-w, reach, h), facing=(-wx * slope, -wy * slope, 1))
            clay.quad('seam', at(-w, 0, 0), at(-w, reach, 0), at(-w, reach, h), at(-w, 0, h), facing=(-ex, -ey, 0))
            clay.quad('seam', at(w, 0, 0), at(w, 0, h), at(w, reach, h), at(w, reach, 0), facing=(ex, ey, 0))
            clay.quad('seam', at(-w, 0, 0), at(-w, 0, h), at(w, 0, h), at(w, 0, 0), facing=(-wx, -wy, 0))


# ---- rooms -----------------------------------------------------------------------
def rooms(clay):
    """Floors, ceilings, the stair and partitions, so every opening has a room behind it.
    Nothing here comes nearer an outside face than the inner face of the wall."""
    i0, i1, j0, j1 = WALL, WIDTH - WALL, WALL, DEPTH - WALL
    g1 = GARAGE_X - WALL
    sx0, _, sy, risers = STAIR
    top = sy + (risers - 1) * TREAD
    # garage
    clay.quad('floor', (i0, -PROJECT + WALL, .02), (g1, -PROJECT + WALL, .02), (g1, 5.70, .02), (i0, 5.70, .02), facing=(0, 0, 1))
    clay.quad('interior', (i0, -PROJECT + WALL, SLAB), (g1, -PROJECT + WALL, SLAB), (g1, j0, SLAB), (i0, j0, SLAB), facing=(0, 0, -1))
    clay.box('interior', i0, g1, 5.70, 5.85, .02, SLAB)                                       # garage back wall
    clay.box('interior', g1, GARAGE_X - .05, 0.0, j1, .02, SLAB)                               # garage side wall to the hall
    clay.quad('floor', (i0, 5.85, HALL), (g1, 5.85, HALL), (g1, j1, HALL), (i0, j1, HALL), facing=(0, 0, 1))           # back room
    clay.quad('floor', (GARAGE_X - .05, j0, HALL), (i1, j0, HALL), (i1, j1, HALL), (GARAGE_X - .05, j1, HALL), facing=(0, 0, 1))   # hall
    # the first floor slab, with the stair well cut out of it
    outline = [(i0, j0), (i1, j0), (i1, sy), (sx0, sy), (sx0, top), (i1, top), (i1, j1), (i0, j1)]
    clay.polygon('interior', [(x, y, SLAB) for x, y in outline], facing=(0, 0, -1))
    clay.polygon('floor', [(x, y, FLOOR2) for x, y in outline], facing=(0, 0, 1))
    for (ax, ay), (bx, by) in ((outline[2], outline[3]), (outline[3], outline[4]), (outline[4], outline[5])):
        mx, my = (ax + bx) / 2, (ay + by) / 2
        clay.quad('interior', (ax, ay, SLAB), (bx, by, SLAB), (bx, by, FLOOR2), (ax, ay, FLOOR2), facing=((sx0 + i1) / 2 - mx, (sy + top) / 2 - my, 0))
    rise = (FLOOR2 - HALL) / risers
    for k in range(risers - 1):
        clay.box('interior', sx0 + .02, i1, sy + k * TREAD, sy + (k + 1) * TREAD, HALL, HALL + rise * (k + 1))
    clay.box('interior', sx0 - .10, sx0, sy, top, FLOOR2, FLOOR2 + 1.0)                           # guard wall round the well
    clay.box('interior', sx0 - .10, i1, sy - .10, sy, FLOOR2, FLOOR2 + 1.0)
    clay.polygon('interior', [(x, y, PLATE) for x, y in ((i0, j0), (i1, j0), (i1, j1), (i0, j1))], facing=(0, 0, -1))
    # upper partitions: living room at the front, bedroom and bath behind
    clay.box('interior', i0 + .02, 4.60, 5.00, 5.10, FLOOR2, PLATE)
    clay.box('interior', 4.50, 4.60, 5.10, j1 - .02, FLOOR2, PLATE)
    clay.box('interior', 4.60, sx0 - .10, 6.30, 6.40, FLOOR2, PLATE)


def build():
    clay = Clay()
    walls(clay)
    projection(clay)
    roof(clay)
    rooms(clay)
    return clay


# ---- records -------------------------------------------------------------------------------
def source_lock_for(role):
    """Path, size and SHA-256 of one locked reference. An unhydrated Git LFS pointer
    already states both, so the lock is the same with or without the image bytes."""
    path = ROOT / SOURCE_DIR / SOURCES[role]
    data = path.read_bytes()
    lock = {'role': role, 'repo_path': f'{SOURCE_DIR}/{SOURCES[role]}', 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        fields = dict(line.split(' ', 1) for line in data.decode('ascii').splitlines() if ' ' in line)
        lock.update(bytes=int(fields['size']), sha256=fields['oid'].removeprefix('sha256:'))
    return lock


def source_lock():
    return [source_lock_for(role) for role in SOURCES]


CAMERAS = ('front', 'front_corner', 'aerial', 'top', 'left_side', 'right_side', 'rear', 'rear_side', 'facade_close', 'architecture_close',
           'glass_close', 'entrance_contact', 'roof_contact', 'band_contact', 'balcony_contact', 'match_front', 'match_oblique', 'match_top')


def entrances():
    """Every door, measured from the model's own numbers (authoring frame)."""
    entry = OPENINGS['entry'][0]
    back = OPENINGS['back'][0]
    garage = OPENINGS['garage_front'][0]
    l0, l1 = entry['u'][0] + .063, entry['mullions'][0] - .03
    return [
        {'kind': 'front door', 'facade': 'street', 'centre_xy_m': [round(GARAGE_X + (l0 + l1) / 2, 3), 0.0], 'route_direction': [0, -1],
         'clear_width_m': round(l1 - l0 - .14, 3), 'door_height_m': round(entry['z'][1] - HALL - .126, 2),
         'threshold_top_m': round(HALL + .005, 3), 'outer_step_foot_m': 0.0, 'rise_m': round(HALL + .005, 3),
         'note': 'two steps from grade: a 0.16 m step in front of the post, then the stoop landing, level with the door'},
        {'kind': 'garden door', 'facade': 'back', 'centre_xy_m': [round(WIDTH - (back['u'][0] + back['u'][1]) / 2, 3), round(DEPTH + .15, 3)],
         'route_direction': [0, 1], 'clear_width_m': round(back['u'][1] - back['u'][0] - .26, 3), 'door_height_m': round(back['z'][1] - HALL - .13, 2),
         'threshold_top_m': round(HALL + .005, 3), 'outer_step_foot_m': 0.0, 'rise_m': round(HALL + .005, 3), 'note': 'two steps: a 0.6 m landing and a 0.35 m lower step'},
        {'kind': 'garage door', 'facade': 'street', 'centre_xy_m': [round((garage['u'][0] + garage['u'][1]) / 2, 3), round(-PROJECT, 3)],
         'route_direction': [0, -1], 'clear_width_m': round(garage['u'][1] - garage['u'][0], 2), 'door_height_m': round(garage['z'][1] - .02, 2),
         'threshold_top_m': .02, 'outer_step_foot_m': .02, 'rise_m': 0.0, 'note': 'vehicle door onto the paved apron'},
    ]


def prework(candidate):
    """The measured contract this candidate is built to."""
    ridge = FASCIA_TOP + (WIDTH + 2 * OVERHANG) / 2 * PITCH
    return {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'variant_index': INDEX, 'state': 'prework', 'keeper_claimed': False,
        'runtime_seed_allowed': False, 'sources': source_lock(),
        'measurement_contract': {
            'dimensions_m': {'main_width': WIDTH, 'main_depth': DEPTH, 'projection': PROJECT, 'garage_block_width': GARAGE_X,
                             'first_floor': FLOOR2, 'wall_plate': PLATE, 'eaves': FASCIA_TOP, 'ridge': round(ridge, 3), 'overhang': OVERHANG},
            'storeys': 2, 'storey_policy': 'fixed_authored_assembly', 'dwellings': 1,
            'scale_basis': 'No image carries a scale. Scale is set by the garage door, taken as a 14 by 8 ft door (4.25 by 2.4 m). The other dimensions were then adjusted until one pinhole camera per image fitted 16 to 18 matched points of the model; see camera_note.',
            'source_measurements': {
                'front': [
                    'Street view from across the street at the corner with the lane, at eye level. The street face recedes gently to the left; the lane face recedes steeply to the right.',
                    'Garage door: four lites in its top section, flush sections below. Built 4.25 m wide and 2.4 m tall.',
                    'Brick from grade to about 0.45 m above the door, then a dark floor band about 0.4 m deep across the whole front, round the porch canopy and on along the lane side.',
                    'Brick piers: about 0.45 m left of the door and 0.85 m right of it, with a wall lamp on each and a mailbox on the right pier.',
                    'Porch at the lane corner, under a flat canopy: a glass door and sidelight in a cedar wall set back about 1.5 m, a cedar post just short of the canopy corner, a concrete stoop of two risers: a lower step in front of the post and a landing level with the door.',
                    'Upper storey: cedar with a shadow line at each board. Sliding glass doors of four panels behind a glass-railed balcony, and to the right a corner window in a dark box frame that wraps onto the lane face: a wide pane and a narrow pane with a transom on the street, one tall pane on the lane.',
                    'Balcony: glass panels between dark posts with a dark top rail, about 1.07 m high, on the roof of the garage block; a cedar-clad solid end at the west, the height of the guard.',
                    'Roof: hip, about 5 in 12 on the side faces and steeper front and back, standing-seam metal, eaves about 0.45 m out over a cedar soffit and dark fascia.',
                    'Lane face: the corner window upstairs and, directly below it, a ground-floor window as wide as its lane pane, then a dark band of four vertical panels from grade to the eaves, about 2.8 m wide, with a slot window about 0.5 m wide on each storey near its back edge; a downpipe at the back corner.'],
                'oblique': [
                    'High view from over the street at the lane corner.',
                    'The garage block, balcony and canopy project in front of the upper storey; the eave covers part of the balcony.',
                    'Hipped roof with all four faces visible as hips; standing seams square to each eave.',
                    'The west end of the balcony is cedar-clad and solid, the height of the glass guard.',
                    'The porch post, stoop with two risers, recessed door and brick pier all read clearly.',
                    'The panel band on the lane face stands slightly proud and carries narrow windows.'],
                'top': [
                    'Near-nadir view, street at the bottom, lane on the right.',
                    'Roof plan about 419 by 434 px, very slightly deeper than wide, hips meeting a ridge about 96 px (about 2 m) long that runs front to back.',
                    'In front of the street eave a lighter strip, the balcony deck, over the west two thirds, and a dark strip, the canopy, at the lane end. Both stand about 0.9 m past the eave.'],
            },
            'source_conflicts': [
                'Catalogue text. The variant was named Garden Studio and described as a single storey with no garage, a dark fibre-cement skin and a green roof. All three images show a two-storey laneway house over a garage, in brick and cedar under a hipped metal roof. The images govern. Ruled by a person on 2026-11-19: the variant is renamed Garage Suite and its text rewritten to match the images.',
                'Ridge length. The roof plan and the oblique both show a ridge about 2 m long; equal pitches on this outline would give about 0.4 m. Built 2.0 m, with the side faces at 5 in 12 and the front and back faces steeper, as an independent review of v004 measured.'],
            'hidden_assumptions': [
                'The back face and the west face are not shown. The back has a glazed garden door with a step, a garage-side window and two upper windows; the west face has one window on each storey. Inferred.',
                'Brick wraps the whole garage block, including the west side and the garage part of the back. The images show it on the street face and the west end of the projection only.',
                'Interiors are schematic: a garage, a back room and an entry hall with a straight stair along the lane wall, lit by the slot windows; upstairs a living room across the front and a bedroom and bath behind.',
                'A downpipe stands at the back corner of each side face. The street view shows the one on the lane face; the west one is inferred.',
                'People, cars, planting, the lane, the street and neighbours belong to the site and are not in the model.'],
        },
        'roof_contract': {'form': 'hip roof with a 2 m ridge front to back: side faces 5 in 12, front and back faces steeper; standing seams square to each eave',
                          'weathering': 'a single closed sheet; seams stop under the hip caps; a gutter round all four eaves drains to downpipes at the back corners'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()},
                              'note': 'board lines on the cedar, mortar bed joints on the brick and joints in the panel band are thin geometry strips; brick head joints are left out as surface texture'},
        'identity_contract': ['two storeys on a near-square plan', 'brick garage block projecting toward the street with a balcony on its roof',
                              'glass guard and cedar-clad solid end on the balcony', 'recessed corner porch with a flat canopy, cedar post and stoop',
                              'cedar upper storey with four-panel sliding doors and a dark-boxed corner window that wraps onto the lane face',
                              'dark floor band round the house',
                              'dark panel band with slot windows on the lane face', 'low hipped standing-seam roof with cedar soffits'],
        'programme_contract': {'dwellings': 1, 'garage': 1, 'street_doors': 1, 'garden_doors': 1},
        'contact_contract': {'base_datum_m': 0.0, 'lowest_geometry_m': 0.0, 'threshold_rise_m': HALL + .005,
                             'ground': 'a 20 mm paver apron 1.2 m deep in front of the garage and porch, a concrete stoop and a garden step; nothing below grade'},
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
    doors = entrances()
    report = {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'state': 'build_valid', 'keeper_claimed': False, 'runtime_seed_allowed': False,
        'sources': source_lock(),
        'model': {'file': model.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'meshes': len(counts), 'materials': len(counts), 'textures': 0, 'images': 0,
                  'triangles': sum(counts.values()), 'triangles_by_role': counts},
        'native_dimensions_m': {'width': round(hi[0] - lo[0], 4), 'depth': round(hi[1] - lo[1], 4), 'height': round(hi[2] - lo[2], 4)},
        'authoring_bounds_m': {'min': [round(v, 4) for v in lo], 'max': [round(v, 4) for v in hi]},
        'storeys': 2, 'dwellings': 1,
        'entrances': {'street doors': 1, 'garden doors': 1, 'garage doors': 1, 'doors': doors},
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
