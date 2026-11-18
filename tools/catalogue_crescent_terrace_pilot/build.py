"""Build the Bath Stone Grand crescent as an RLASM 6.1 architectural-clay GLB.

Exact variant: `london_crescent_terrace` / `london-crescent-terrace-bath-stone` (variant 0).
Twenty houses stand on a half ellipse behind a giant Ionic order. The model is plain
constructive geometry written with the shared `clay_kit`; nothing here needs Blender.

    python3 tools/catalogue_crescent_terrace_pilot/build.py --output <new directory>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, its
renders and boards are review material and stay outside Git until a human activates them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'catalogue_plus15_concrete_pilot'))
from clay_kit import METHOD, Clay  # noqa: E402

SLUG = 'crescent-terrace-bath-stone'
ARCHETYPE, VARIANT, INDEX = 'london_crescent_terrace', 'london-crescent-terrace-bath-stone', 0
TITLE = 'Bath Stone Grand'
SOURCE_DIR = 'frontend/public/archetypes/buildings/london-crescent-terrace'
SOURCES = {'front': f'variant_{INDEX}.png', 'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}

# ---- measured contract (metres) ------------------------------------------------
HOUSES, BAYS = 20, 3              # houses round the sweep, window bays to a house
SEMI_MAJOR, SEMI_MINOR = 52.0, 34.0   # half ellipse of the concave front's face line
DEPTH, END_BAYS = 13.8, 6         # front face to back face; bays across each end
STOREYS = 3
FIRST, SECOND = 4.40, 8.70        # floor levels above the ground storey
BAND = 4.05                       # underside of the band the columns stand on
COLUMN, RADIUS, AXIS = 7.20, .33, .40   # column height, lower radius, axis setback from the face line
WALL, THICK = .62, .30            # setback and thickness of the wall behind the columns
ARCHITRAVE = 11.60                # top of the capitals: FIRST + COLUMN
CORNICE = 13.00                   # top of the cornice, 1.4 m above the capitals
RAIL = 14.10                      # top of the balustrade
EAVES, RIDGE, VALLEY = 13.10, 15.90, 14.00
EAVES_SET, RIDGE_SET, VALLEY_SET = 1.10, 4.20, 5.80   # setbacks of the roof's lines from each face
AREA = 1.70                       # paved strip between each face and its railings
PLINTH = 1.24 * RADIUS             # half-width of the block each column stands on
STACK = 2.55                      # height of each chimney stack above its ridge; the pots add 0.7 m
OPENING = 1.05                    # sash window width
GROUND_WINDOW, FIRST_WINDOW, SECOND_WINDOW = (1.15, 3.10), (FIRST + .55, FIRST + 2.90), (FIRST + 4.65, FIRST + 6.35)
DOOR = (1.15, 2.25, 3.05)         # width, leaf height, head of the fanlight

PALETTE = {  # role -> flat colour (sRGB), in node order
    'paving': {'colour': '#a8a08e', 'module': 'area paving'},
    'stone': {'colour': '#cbb385', 'module': 'ashlar walls'},
    'dressed': {'colour': '#d3bd90', 'module': 'giant order'},
    'slate': {'colour': '#5d636b', 'module': 'roof'},
    'lead': {'colour': '#9aa1a6', 'module': 'roof'},
    'pot': {'colour': '#b98a63', 'module': 'chimneys'},
    'iron': {'colour': '#2b2d30', 'module': 'railings', 'roughness': .52},
    'joinery': {'colour': '#ece7da', 'module': 'sashes and doors'},
    'door': {'colour': '#d6d0c0', 'module': 'sashes and doors'},
    'floor': {'colour': '#7b6a55', 'module': 'rooms'},
    'interior': {'colour': '#b9b09d', 'module': 'rooms'},
    'glass': {'colour': '#3d464f', 'module': 'sash glazing', 'alpha': .45, 'roughness': .24, 'transmission': .28},
}


def unit2(x, y):
    size = math.hypot(x, y)
    return (x / size, y / size)


class Loop:
    """The building's outline as a closed run of straight bays. Travelling round it the
    building is on the right, so `inward` points into the building and a viewer outside
    sees each bay run from right to left."""

    def __init__(self, nodes):
        self.nodes = nodes
        count = len(nodes)
        self.inward, self.length, self.along = [], [], []
        for k in range(count):
            (ax, ay), (bx, by) = nodes[k], nodes[(k + 1) % count]
            ux, uy = unit2(bx - ax, by - ay)
            self.along.append((ux, uy))
            self.inward.append((uy, -ux))
            self.length.append(math.hypot(bx - ax, by - ay))
        self.bisector, self.scale = [], []
        for k in range(count):
            (ax, ay), (bx, by) = self.inward[k - 1], self.inward[k]
            mx, my = unit2(ax + bx, ay + by)
            self.bisector.append((mx, my))
            self.scale.append(1 / (mx * bx + my * by))

    def node(self, k, n, z=0.0):
        """The point `n` behind both bays that meet at node k: their mitre line."""
        k %= len(self.nodes)
        (x, y), (mx, my), s = self.nodes[k], self.bisector[k], self.scale[k]
        return (x + n * s * mx, y + n * s * my, z)

    def tangent(self, k):
        mx, my = self.bisector[k % len(self.nodes)]
        return (-my, mx)

    def sweep(self, clay, role, profile):
        """A moulding of constant section right round the building, mitred at every node."""
        clay.loft(role, [[self.node(k, n, z) for n, z in profile] for k in range(len(self.nodes))], loop=True)

    def ring(self, n, z):
        return [self.node(k, n, z) for k in range(len(self.nodes))]


class Bay:
    """One straight bay. `u` runs along it, `n` is the setback behind its face line
    (negative in front of it) and `p` maps (u, n, z) to world coordinates."""

    def __init__(self, loop, k):
        self.loop, self.k = loop, k
        self.origin, self.along, self.inward, self.length = loop.nodes[k], loop.along[k], loop.inward[k], loop.length[k]
        self.out = (-self.inward[0], -self.inward[1], 0.0)

    def p(self, u, n, z):
        if u <= 1e-9:                        # at either end the bay stops on the mitre line it shares
            return self.loop.node(self.k, n, z)
        if u >= self.length - 1e-9:
            return self.loop.node(self.k + 1, n, z)
        (x, y), (ux, uy), (mx, my) = self.origin, self.along, self.inward
        return (x + u * ux + n * mx, y + u * uy + n * my, z)

    def box(self, clay, role, u0, u1, n0, n1, z0, z1, ends=True):
        """A box along the bay. `ends=False` leaves off the two end faces, for a piece
        whose ends are buried in its neighbours."""
        clay.loft(role, [[self.p(u, n0, z0), self.p(u, n1, z0), self.p(u, n1, z1), self.p(u, n0, z1)] for u in (u0, u1)], caps=(ends, ends))

    def quad(self, clay, role, u0, u1, n, z0, z1):
        clay.quad(role, self.p(u0, n, z0), self.p(u1, n, z0), self.p(u1, n, z1), self.p(u0, n, z1), facing=self.out)

    def cross(self, clay, role, u, n, z0, z1, width=.022):
        """A slender bar drawn as two crossed blades."""
        h = width / 2
        u = min(max(u, .03), self.length - .03)
        clay.quad(role, self.p(u - h, n, z0), self.p(u + h, n, z0), self.p(u + h, n, z1), self.p(u - h, n, z1))
        clay.quad(role, self.p(u, n - h, z0), self.p(u, n + h, z0), self.p(u, n + h, z1), self.p(u, n - h, z1))


def outline():
    """Node positions round the building, and where each run of bays starts."""
    samples = 20000
    points, total = [(SEMI_MAJOR, 0.0)], [0.0]
    for i in range(1, samples + 1):
        t = math.pi * i / samples
        point = (SEMI_MAJOR * math.cos(t), SEMI_MINOR * math.sin(t))
        total.append(total[-1] + math.hypot(point[0] - points[-1][0], point[1] - points[-1][1]))
        points.append(point)
    bays = HOUSES * BAYS
    inner, at = [], 0
    for k in range(bays + 1):
        target = total[-1] * k / bays
        while at < samples and total[at + 1] < target:
            at += 1
        f = 0.0 if k in (0, bays) else (target - total[at]) / (total[at + 1] - total[at])
        (ax, ay), (bx, by) = points[at], points[min(at + 1, samples)]
        x, y = (points[0] if k == 0 else points[-1] if k == bays else (ax + (bx - ax) * f, ay + (by - ay) * f))
        nx, ny = unit2(x / SEMI_MAJOR ** 2, y / SEMI_MINOR ** 2) if y > 1e-9 else ((1.0, 0.0) if x > 0 else (-1.0, 0.0))
        inner.append(((round(x, 6), round(y, 6)), (nx, ny)))
    outer = [((round(x + DEPTH * nx, 6), round(y + DEPTH * ny, 6))) for (x, y), (nx, ny) in inner]
    front = [point for point, _ in inner]

    def between(a, b):
        return [(round(a[0] + (b[0] - a[0]) * k / END_BAYS, 6), 0.0) for k in range(1, END_BAYS)]

    nodes = front + between(front[-1], outer[-1]) + outer[::-1] + between(outer[0], front[0])
    starts = {'front': 0, 'west': bays, 'back': bays + END_BAYS, 'east': 2 * bays + END_BAYS}
    return nodes, starts


NODES, STARTS = outline()
LOOP = Loop(NODES)
BAY_COUNT = len(NODES)
FRONT_BAYS = HOUSES * BAYS


def side_of(k):
    if k < STARTS['west']:
        return 'front'
    if k < STARTS['back']:
        return 'west'
    return 'back' if k < STARTS['east'] else 'east'


def opening_kind(k):
    """What stands in the ground storey of bay k: a front door, a garden door or a window."""
    side = side_of(k)
    j = k - STARTS[side]
    if side == 'front':
        return 'door' if j % BAYS == 0 else 'window'
    if side == 'back':
        return 'door' if j % BAYS == 1 else 'window'
    return 'door' if j == 2 else 'window'


# ---- joinery -----------------------------------------------------------------------
def sash(clay, bay, uc, z0, z1, face, bars=(2, 1)):
    """A sash window in a wall opening: box frame set back in the reveal, meeting rail,
    glazing bars and glass. `face` is the setback of the wall's outer face."""
    a, b, n0, n1 = uc - OPENING / 2, uc + OPENING / 2, face + .14, face + .22
    for u0, u1 in ((a, a + .06), (b - .06, b)):
        bay.box(clay, 'joinery', u0, u1, n0, n1, z0, z1)
    middle = (z0 + z1) / 2
    for c, d, back in ((z0, z0 + .07, n1), (z1 - .07, z1, n1), (middle - .025, middle + .025, n1 - .02)):
        bay.box(clay, 'joinery', a + .06, b - .06, n0, back, c, d, ends=False)
    glass = face + .19
    bay.quad(clay, 'glass', a + .06, b - .06, glass, z0 + .07, z1 - .07)
    upright, level = bars
    for k in range(1, upright + 1):
        u = a + .06 + (OPENING - .12) * k / (upright + 1)
        bay.quad(clay, 'joinery', u - .012, u + .012, glass - .012, z0 + .07, z1 - .07)
    for lo, hi in ((z0 + .07, middle - .025), (middle + .025, z1 - .07)):
        for k in range(1, level + 1):
            z = lo + (hi - lo) * k / (level + 1)
            bay.quad(clay, 'joinery', a + .06, b - .06, glass - .012, z - .012, z + .012)
    bay.box(clay, 'dressed', a - .06, b + .06, face - .06, face + .14, z0 - .10, z0)      # stone sill


def door(clay, bay, uc, face):
    """A six-panel door under a fanlight, in a reveal of the wall's own thickness."""
    width, leaf, head = DOOR
    a, b, n0, n1 = uc - width / 2, uc + width / 2, face + .22, face + .30
    for u0, u1, c, d in ((a, a + .07, .02, head), (b - .07, b, .02, head), (a + .07, b - .07, leaf, leaf + .07), (a + .07, b - .07, head - .06, head)):
        bay.box(clay, 'joinery', u0, u1, n0, n1, c, d)
    bay.box(clay, 'door', a + .07, b - .07, n0 + .02, n1, .035, leaf)
    panel = (width - .14 - .30) / 2
    for column in range(2):
        u = a + .07 + .10 + column * (panel + .10)
        for lo, hi in ((.20, .70), (.82, 1.42), (1.54, 2.06)):
            bay.quad(clay, 'joinery', u, u + panel, n0 + .012, lo, hi)
    bay.quad(clay, 'glass', a + .07, b - .07, n0 + .05, leaf + .07, head - .06)
    for k in (1, 2):
        u = a + .07 + (width - .14) * k / 3
        bay.quad(clay, 'joinery', u - .012, u + .012, n0 + .04, leaf + .07, head - .06)
    bay.box(clay, 'iron', b - .22, b - .17, n0 - .03, n0 + .02, 1.02, 1.07)                # knob
    bay.box(clay, 'dressed', a - .10, b + .10, face - .30, face + .30, .02, .035)           # threshold stone


# ---- the order -----------------------------------------------------------------------
def lathe(clay, role, x, y, profile, steps=12, caps=(True, True)):
    """Turn a (radius, height) profile about a vertical axis."""
    rings = [[(x + r * math.cos(2 * math.pi * k / steps), y + r * math.sin(2 * math.pi * k / steps), z) for k in range(steps)] for r, z in profile]
    clay.loft(role, rings, caps=caps, smooth=50)


def block(clay, role, x, y, along, inward, half_u, half_n, z0, z1):
    """A box square to a node's own tangent and mitre line."""
    ring = [(x + su * half_u * along[0] + sn * half_n * inward[0], y + su * half_u * along[1] + sn * half_n * inward[1]) for su, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    clay.prism(role, ring, z0, z1)


def column(clay, k):
    """One engaged Ionic column on its plinth block at node k. Every radial size is a
    multiple of the lower radius, so the order keeps its proportions if that changes."""
    x, y, _ = LOOP.node(k, AXIS)
    along, inward, z, r = LOOP.tangent(k), LOOP.bisector[k % BAY_COUNT], FIRST, RADIUS
    block(clay, 'dressed', x, y, along, inward, PLINTH, PLINTH, z, z + .16)
    lathe(clay, 'dressed', x, y, [(1.24 * r, z + .16), (1.29 * r, z + .22), (1.10 * r, z + .30), (1.16 * r, z + .36), (r, z + .42)], steps=10, caps=(False, False))
    top = z + COLUMN - .52
    lathe(clay, 'dressed', x, y, [(r, z + .42), (r, z + 2.50), (.94 * r, z + 4.70), (.855 * r, top)], steps=10, caps=(False, False))
    lathe(clay, 'dressed', x, y, [(.855 * r, top), (.92 * r, top + .05), (.87 * r, top + .09), (1.05 * r, top + .22)], steps=10, caps=(False, True))
    centre = top + .27                       # the capital: a cushion between two scrolls that run front to back
    block(clay, 'dressed', x, y, along, inward, .90 * r, 1.05 * r, centre - .03, centre + .13)
    for side in (-1, 1):
        cx, cy = x + side * .90 * r * along[0], y + side * .90 * r * along[1]
        rings = []
        for n in (-1.13 * r, 1.13 * r):
            rings.append([(cx + n * inward[0] + .40 * r * math.cos(a) * along[0], cy + n * inward[1] + .40 * r * math.cos(a) * along[1], centre + .40 * r * math.sin(a))
                          for a in (2 * math.pi * s / 12 for s in range(12))])
        clay.loft('dressed', rings, smooth=50)
    block(clay, 'dressed', x, y, along, inward, 1.32 * r, 1.32 * r, z + COLUMN - .12, z + COLUMN)


ENTABLATURE = [(.95, ARCHITRAVE), (.12, ARCHITRAVE), (.12, ARCHITRAVE + .22), (.09, ARCHITRAVE + .22), (.09, ARCHITRAVE + .40), (.05, ARCHITRAVE + .45),
               (.12, ARCHITRAVE + .48), (.12, ARCHITRAVE + .95), (.04, ARCHITRAVE + 1.00), (.04, ARCHITRAVE + 1.09), (-.40, ARCHITRAVE + 1.09),
               (-.40, ARCHITRAVE + 1.26), (-.48, ARCHITRAVE + 1.32), (-.48, CORNICE), (.95, CORNICE)]


def order(clay):
    """Band, columns, entablature and balustrade, right round the building."""
    LOOP.sweep(clay, 'dressed', [(1.00, BAND), (-.07, BAND), (-.07, FIRST - .06), (-.04, FIRST), (1.00, FIRST)])
    LOOP.sweep(clay, 'dressed', ENTABLATURE)
    LOOP.sweep(clay, 'dressed', [(.10, CORNICE), (.10, CORNICE + .22), (.60, CORNICE + .22), (.60, CORNICE)])           # blocking course
    LOOP.sweep(clay, 'dressed', [(.11, RAIL - .18), (.11, RAIL - .04), (.14, RAIL), (.56, RAIL), (.59, RAIL - .04), (.59, RAIL - .18)])   # top rail
    for k in range(BAY_COUNT):
        column(clay, k)
        x, y, _ = LOOP.node(k, .35)
        block(clay, 'dressed', x, y, LOOP.tangent(k), LOOP.bisector[k], .30, .25, CORNICE + .22, RAIL - .18)             # pedestal over the column
        bay = Bay(LOOP, k)
        count = max(4, round((bay.length - .6) / .28))
        turn = math.atan2(bay.along[1], bay.along[0]) + math.pi / 4
        for j in range(count):
            u = .30 + (bay.length - .60) * (j + .5) / count
            bx, by, _ = bay.p(u, .35, 0)
            base = CORNICE + .22
            profile = [(.085, base), (.115, base + .20), (.055, base + .46), (.085, RAIL - .18)]
            clay.loft('dressed', [[(bx + r * math.cos(turn + math.pi / 2 * s), by + r * math.sin(turn + math.pi / 2 * s), z) for s in range(4)] for r, z in profile],
                      caps=(False, False))
        for j in range(5):                   # modillions under the corona
            u = bay.length * (j + .5) / 5
            bay.box(clay, 'dressed', u - .07, u + .07, -.34, .04, ARCHITRAVE + .99, ARCHITRAVE + 1.09)


# ---- walls ---------------------------------------------------------------------------
def walls(clay):
    for k in range(BAY_COUNT):
        bay = Bay(LOOP, k)
        length, uc = bay.length, bay.length / 2
        a, b = uc - OPENING / 2, uc + OPENING / 2
        kind = opening_kind(k)
        # ground storey: a 0.9 m wall with one opening
        if kind == 'door':
            width, leaf, head = DOOR
            a0, b0, lo, hi = uc - width / 2, uc + width / 2, .02, head
        else:
            a0, b0, (lo, hi) = a, b, GROUND_WINDOW
        bay.box(clay, 'stone', 0, a0, 0, .90, .02, BAND)
        bay.box(clay, 'stone', b0, length, 0, .90, .02, BAND)
        bay.box(clay, 'stone', a0, b0, 0, .90, hi, BAND, ends=False)
        if kind == 'door':
            door(clay, bay, uc, 0)
        else:
            bay.box(clay, 'stone', a0, b0, 0, .90, .02, lo, ends=False)
            sash(clay, bay, uc, lo, hi, 0, bars=(2, 2))
        # behind the columns: one wall with the tall first-floor sash and the second-floor sash
        (f0, f1), (s0, s1) = FIRST_WINDOW, SECOND_WINDOW
        bay.box(clay, 'stone', 0, a, WALL, WALL + THICK, FIRST, CORNICE)
        bay.box(clay, 'stone', b, length, WALL, WALL + THICK, FIRST, CORNICE)
        for lo, hi in ((FIRST, f0), (f1, s0), (s1, CORNICE)):
            bay.box(clay, 'stone', a, b, WALL, WALL + THICK, lo, hi, ends=False)
        sash(clay, bay, uc, f0, f1, WALL, bars=(2, 2))
        sash(clay, bay, uc, s0, s1, WALL, bars=(2, 1))
        for u0, u1, lo, hi in ((a - .13, a, s0 - .10, s1 + .13), (b, b + .13, s0 - .10, s1 + .13), (a, b, s1, s1 + .13)):
            bay.box(clay, 'dressed', u0, u1, WALL - .035, WALL, lo, hi)
        # iron guard between the column plinths at the tall window
        clear = PLINTH + .02
        bay.box(clay, 'iron', clear, length - clear, -.03, .00, FIRST + .86, FIRST + .90, ends=False)
        bay.box(clay, 'iron', clear, length - clear, -.03, .00, FIRST + .06, FIRST + .09, ends=False)
        count = max(4, round((length - 2 * clear) / .18))
        for j in range(count + 1):
            bay.cross(clay, 'iron', clear + (length - 2 * clear) * j / count, -.015, FIRST + .09, FIRST + .86, width=.018)


# ---- area railings and paving -------------------------------------------------------------
def railing(clay, bay, u0, u1):
    """Spear-headed iron railings on a stone kerb along the edge of the area."""
    n = -AREA + .08
    bay.box(clay, 'dressed', u0, u1, -AREA, -AREA + .16, .02, .14)
    bay.box(clay, 'iron', u0, u1, n - .015, n + .015, 1.04, 1.07)
    bay.box(clay, 'iron', u0, u1, n - .015, n + .015, .22, .25)
    count = max(1, round((u1 - u0) / .16))
    for j in range(count + 1):
        bay.cross(clay, 'iron', u0 + (u1 - u0) * j / count, n, .14, 1.22)


def areas(clay):
    LOOP.sweep(clay, 'paving', [(-AREA - .10, 0), (-AREA - .10, .02), (.30, .02), (.30, 0)])
    for k in range(BAY_COUNT):
        bay = Bay(LOOP, k)
        if opening_kind(k) != 'door':
            railing(clay, bay, 0, bay.length)
            continue
        uc, half = bay.length / 2, DOOR[0] / 2 + .25
        railing(clay, bay, 0, uc - half)
        railing(clay, bay, uc + half, bay.length)
        for u in (uc - half, uc + half):     # returns either side of the path to the door
            n0, n1 = -AREA + .16, -.06
            bay.box(clay, 'iron', u - .015, u + .015, n0, n1, 1.04, 1.07)
            bay.box(clay, 'iron', u - .015, u + .015, n0, n1, .22, .25)
            count = round((n1 - n0) / .14)
            for j in range(count + 1):
                bay.cross(clay, 'iron', u, n0 + (n1 - n0) * j / count, .04, 1.22)
        bay.box(clay, 'dressed', uc - half, uc + half, -AREA - .10, -.05, .02, .035)         # flagged path over the area


# ---- roof --------------------------------------------------------------------------------
def party_lines():
    """Front and back node indices of each line between two houses, east to west."""
    return [(BAYS * h, STARTS['east'] - BAYS * h) for h in range(HOUSES + 1)]


def roof(clay):
    """Two slate ridges over each range of rooms with a lead flat between them, behind
    lead gutters, turning the corners as hips."""
    rings = {name: LOOP.ring(n, z) for name, n, z in (('gutter', WALL + THICK, CORNICE), ('eaves', EAVES_SET, EAVES), ('ridge', RIDGE_SET, RIDGE), ('valley', VALLEY_SET, VALLEY))}
    for k in range(BAY_COUNT):
        j = (k + 1) % BAY_COUNT
        for low, high, role in (('gutter', 'eaves', 'lead'), ('eaves', 'ridge', 'slate'), ('ridge', 'valley', 'slate')):
            clay.quad(role, rings[low][k], rings[low][j], rings[high][j], rings[high][k], facing=(0, 0, 1))
    for front in range(FRONT_BAYS):          # the lead flat down the middle, bay by bay
        back = (STARTS['east'] - front) % BAY_COUNT
        clay.quad('lead', rings['valley'][front], rings['valley'][front + 1], rings['valley'][back - 1], rings['valley'][back], facing=(0, 0, 1))
    for front, back in party_lines()[1:-1]:
        party_wall(clay, front, back)
    corners = {(STARTS[side] + offset) % BAY_COUNT for side in STARTS for offset in (-1, 0)}
    for h in range(HOUSES):
        for first in (BAYS * h, STARTS['back'] + BAYS * h):
            for k in {first if first not in corners else first + 1, first + BAYS - 1 if first + BAYS - 1 not in corners else first + BAYS - 2}:
                dormer(clay, Bay(LOOP, k))
    for side in ('west', 'east'):
        for j in (2, END_BAYS - 3):
            dormer(clay, Bay(LOOP, STARTS[side] + j))


def party_wall(clay, front, back):
    """The stone upstand between two houses, following the roof, with a stack on each ridge."""
    (fx, fy, _), (bx, by, _) = LOOP.node(front, 0), LOOP.node(back, 0)
    ux, uy = unit2(bx - fx, by - fy)
    tx, ty = -uy, ux
    span = math.hypot(bx - fx, by - fy)
    section = [(EAVES_SET - .1, EAVES), (RIDGE_SET, RIDGE + .30), (VALLEY_SET, VALLEY + .30), (span - VALLEY_SET, VALLEY + .30), (span - RIDGE_SET, RIDGE + .30),
               (span - EAVES_SET + .1, EAVES), (span - EAVES_SET + .1, EAVES - .3), (EAVES_SET - .1, EAVES - .3)]
    clay.loft('stone', [[(fx + d * ux + s * tx, fy + d * uy + s * ty, z) for d, z in section] for s in (-.14, .14)])
    for d in (RIDGE_SET, span - RIDGE_SET):
        x, y = fx + d * ux, fy + d * uy
        block(clay, 'stone', x, y, (tx, ty), (ux, uy), .45, 1.30, RIDGE - .6, RIDGE + STACK)
        block(clay, 'dressed', x, y, (tx, ty), (ux, uy), .52, 1.37, RIDGE + STACK, RIDGE + STACK + .18)
        for j in range(7):
            px, py = x + (-1.05 + .35 * j) * ux, y + (-1.05 + .35 * j) * uy
            lathe(clay, 'pot', px, py, [(.12, RIDGE + STACK + .18), (.10, RIDGE + STACK + .65), (.115, RIDGE + STACK + .71)], steps=6, caps=(False, True))


def dormer(clay, bay):
    """A small lead-topped dormer on the outer slope, with one sash."""
    uc, n0, n1 = bay.length / 2, 2.05, 3.30
    slope = (RIDGE - EAVES) / (RIDGE_SET - EAVES_SET)
    base, top = EAVES + (n0 - EAVES_SET) * slope, EAVES + (n0 - EAVES_SET) * slope + 1.05
    for u0, u1 in ((uc - .50, uc - .42), (uc + .42, uc + .50)):
        bay.box(clay, 'lead', u0, u1, n0, n1, base - .1, top)
    bay.box(clay, 'lead', uc - .56, uc + .56, n0 - .08, n1 + .1, top, top + .07)
    bay.box(clay, 'joinery', uc - .42, uc + .42, n0, n0 + .06, base + .02, base + .09)
    bay.box(clay, 'joinery', uc - .42, uc + .42, n0, n0 + .06, top - .07, top)
    bay.box(clay, 'joinery', uc - .02, uc + .02, n0, n0 + .05, base + .09, top - .07)
    bay.quad(clay, 'glass', uc - .42, uc + .42, n0 + .04, base + .09, top - .07)
    bay.quad(clay, 'lead', uc - .42, uc + .42, n1, base, top)


# ---- rooms ---------------------------------------------------------------------------------
def rooms(clay):
    """Floors, a spine wall and party walls, so every sash has a room behind it. Nothing
    here comes nearer an outside face than the inner face of the wall."""
    inset = WALL + THICK

    def middle(front, back):
        (ax, ay, _), (bx, by, _) = LOOP.node(front, inset), LOOP.node(back, inset)
        return ((ax + bx) / 2, (ay + by) / 2)

    for front in range(FRONT_BAYS):          # floors and ceiling bay by bay, so each meets both walls
        back = (STARTS['east'] - front) % BAY_COUNT
        for level, thick, role, edge in ((.02, .03, 'floor', .90), (FIRST - .12, .12, 'floor', inset), (SECOND - .12, .12, 'floor', inset),
                                         (EAVES - .30, .12, 'interior', inset)):
            lower = [LOOP.node(front, edge, level), LOOP.node(front + 1, edge, level), LOOP.node(back - 1, edge, level), LOOP.node(back, edge, level)]
            clay.loft(role, [lower, [(x, y, z + thick) for x, y, z in lower]])
    lines = party_lines()
    for (f0, b0), (f1, b1) in zip(lines, lines[1:]):       # the spine wall of each house
        first, second = middle(f0, b0), middle(f1, b1)
        clay.quad('interior', (*first, .05), (*second, .05), (*second, EAVES - .30), (*first, EAVES - .30))
    for front, back in lines[1:-1]:                         # party walls
        (ax, ay, _), (bx, by, _) = LOOP.node(front, inset), LOOP.node(back, inset)
        clay.quad('interior', (ax, ay, .05), (bx, by, .05), (bx, by, EAVES - .30), (ax, ay, EAVES - .30))


def build():
    clay = Clay()
    areas(clay)
    walls(clay)
    order(clay)
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
           'glass_close', 'entrance_contact', 'end_contact', 'roof_contact', 'street', 'rear_ground', 'corner_close', 'match_front', 'match_oblique', 'match_top')


def prework(candidate):
    """The measured contract this candidate is built to."""
    span = 2 * (SEMI_MAJOR + DEPTH)
    return {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'state': 'prework', 'keeper_claimed': False, 'runtime_seed_allowed': False,
        'sources': source_lock(),
        'measurement_contract': {
            'dimensions_m': {'width': round(span, 1), 'depth': round(SEMI_MINOR + DEPTH, 1), 'range_depth': DEPTH, 'cornice': CORNICE, 'balustrade': RAIL,
                             'ridge': RIDGE, 'stack_top': round(RIDGE + STACK + .71, 2)},
            'storeys': STOREYS, 'storey_policy': 'fixed_authored_assembly', 'houses': HOUSES, 'bays_per_house': BAYS, 'columns': BAY_COUNT,
            'source_measurements': {
                'front': [
                    'An eye-level view along the concave front from inside the crescent. It carries no scale. Scale is set by the column: 7.2 m, about 280 px at the right edge.',
                    'At the right-hand column: ground storey about 175 px of wall below the band, columns 270 to 280 px, entablature about 55 px, balustrade about 45 px. Built 4.4 m, 7.2 m, 1.4 m and 1.1 m.',
                    'Ground storey: plain ashlar with one tall window to a bay, about 2.0 m tall with its sill at railing height. Built 1.95 m tall with the sill at 1.15 m.',
                    'Behind the columns: a first-floor sash about 2.05 m tall with its sill 0.65 m above the column bases, and a second-floor sash about 1.75 m tall whose head is 0.8 m below the capitals.',
                    'Columns are slender, about eleven lower diameters tall, three-quarters engaged, Ionic, with the scrolls of each capital side by side as seen from the front.',
                    'An iron guard stands between the column plinths at every first-floor window.',
                    'A continuous entablature with a modillion cornice, then a balustrade with a pedestal over every column and about six balusters to a bay.',
                    'Stone chimney stacks with a row of pots rise behind the balustrade at each party wall. Slate shows above the balustrade toward the far end.',
                    'Spear-headed iron railings run along the pavement edge.'],
                'oblique': [
                    'A view from high outside one end, looking along the convex side and across to the concave front.',
                    'Plan: close to half an ellipse. The far end faces back toward the camera.',
                    'House count: front doors are three bays apart, and about forty columns show on the visible two thirds of the concave front, so about sixty bays and twenty houses. Built 20 houses of 3 bays, 61 columns on the front.',
                    'The giant order runs along the convex side and across the six-bay end as well as the concave front.',
                    'Each house: a white door and two windows at street level; a first-floor sash about 2.4 m tall and a second-floor sash about 1.6 m tall, both with glazing bars.',
                    'Roof: slate ranges behind the balustrade, a stone upstand and broad stacks with about seven pots at each party wall, small dormers just behind the balustrade, a hipped roof over each end.',
                    'A sunken area with railings and a bridge to each door lies between the pavement and the front.'],
                'top': [
                    'A roof plan of a short block of about ten houses, concave on both long sides, with flared hipped ends. It is not the building the other two images show.',
                    'Used only for the character of the roof: two slate ranges with a lead flat and lead-covered additions between them, a stack on each party wall, dormers behind the parapet, hipped ends.'],
            },
            'source_conflicts': [
                'Plan and length. The roof plan shows about ten houses in a shallow block. The street view and the oblique, which agree with each other, show a long sweep of about twenty houses on half an ellipse. Street view and oblique govern.',
                'Column count. The catalogue text gives 114 columns. Counted on the oblique, the concave front has about sixty bays. Built 61 columns on the concave front and 132 in all.',
                'Catalogue plot. The catalogue lists a 6 m by 12 m plot, the size of one house. All three images show a complete crescent. Built as the complete crescent; each house is 6.85 m wide and 13.8 m deep.',
                'Window bars. The street view shows sashes with one large pane above another. The oblique shows small panes with glazing bars. Built with glazing bars.',
                'First-floor sash height. About 2.05 m in the street view and about 2.4 m in the oblique. Built 2.35 m.',
                'Columns on the convex side. The oblique shows the giant order on the convex side. A real crescent of this kind has a plain back. Built as drawn.'],
            'camera_note': 'The three fitted cameras are approximate. No camera can register this model exactly against the oblique or the roof plan, because the images do not agree on the plan. The street camera matches the far end of the sweep; the near end renders about 15 percent larger than the reference.',
            'hidden_assumptions': [
                'The far end, and most of the convex side, are not shown in detail. Both ends are built alike, and the convex side repeats the front with a garden door to each house.',
                'Interiors are inferred: three floors, a spine wall and party walls to each house, so that every window has a room behind it.',
                'The roof between the two slate ranges is a plain lead flat. The lead-covered additions in the roof plan are left out.',
                'The sunken areas, their steps and the bridges to the doors are left out, because nothing may lie below grade. Railings stand at grade and each door has a level stone path through them.',
                'Ashlar coursing and joints are left out, as surface texture.',
                'The crescent is taken to be symmetrical about its middle.',
                'Party walls stand square to the concave front, so bays on the convex side widen from 2.7 m at the middle to 3.7 m toward the ends.'],
        },
        'roof_contract': {'form': 'two slate ranges with a lead flat between, behind lead gutters and a stone balustrade; hipped at both ends',
                          'weathering': 'closed gutter, slopes, flat and party upstands; a stack on each ridge at every party wall'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()}},
        'identity_contract': ['half-ellipse crescent', 'twenty houses of three bays', 'three storeys', 'giant Ionic order on a plain ground storey',
                              'one sash to a bay on each storey', 'continuous entablature and balustrade', 'a stack with pots at every party wall',
                              'slate roof with dormers behind the balustrade', 'iron railings at the pavement'],
        'programme_contract': {'houses': HOUSES, 'front_doors': HOUSES, 'garden_doors': HOUSES, 'end_doors': 2},
        'contact_contract': {'base_datum_m': 0.0, 'lowest_geometry_m': 0.0, 'threshold_rise_m': .035,
                             'ground': 'a 20 mm paved strip 1.8 m wide round the building; no lawn, street or sunken area in the model'},
        'camera_roster': list(CAMERAS),
        'mandatory_review_views': ['front.png', 'front_corner.png', 'aerial.png', 'left_side.png', 'right_side.png', 'rear.png', 'rear_side.png',
                                   'facade_close.png', 'architecture_close.png', 'glass_close.png', 'entrance_contact.png', 'end_contact.png', 'roof_contact.png'],
    }


def entrances():
    """Every door, measured from the model's own numbers (authoring frame)."""
    out = []
    for k in range(BAY_COUNT):
        if opening_kind(k) != 'door':
            continue
        bay = Bay(LOOP, k)
        x, y, _ = bay.p(bay.length / 2, .22, 0)
        side = side_of(k)
        out.append({'kind': 'front door' if side == 'front' else 'garden door' if side == 'back' else 'end door', 'facade': side, 'bay': k,
                    'centre_xy_m': [round(x, 3), round(y, 3)], 'route_direction': [round(bay.out[0], 4), round(bay.out[1], 4)],
                    'clear_width_m': round(DOOR[0] - .14, 3), 'door_height_m': DOOR[1], 'threshold_top_m': .035, 'outer_step_foot_m': 0.0, 'rise_m': .035})
    return out


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
        'storeys': STOREYS, 'houses': HOUSES, 'bays': BAY_COUNT, 'columns': BAY_COUNT,
        'entrances': {'front doors': sum(1 for d in doors if d['kind'] == 'front door'), 'garden doors': sum(1 for d in doors if d['kind'] == 'garden door'),
                      'end doors': sum(1 for d in doors if d['kind'] == 'end door'), 'doors': doors},
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
