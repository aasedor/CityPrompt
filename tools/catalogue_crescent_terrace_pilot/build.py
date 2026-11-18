"""Build the Bath Stone Grand crescent as an RLASM 6.1 architectural-clay GLB.

Exact variant: `london_crescent_terrace` / `london-crescent-terrace-bath-stone` (variant 0).
Eighteen houses stand on a half ellipse behind a giant Ionic order. The model is plain
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
HOUSES, BAYS = 18, 3              # houses round the sweep, window bays to a house
SEMI_MAJOR, SEMI_MINOR = 47.5, 31.0   # half ellipse of the concave front's face line
DEPTH, END_BAYS = 13.8, 6         # front face to back face; window bays across each end
COUPLED = .95                     # at every corner a second column stands this far along each face, with blind wall between
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
    """Node positions round the building, and where each run of bays starts. Every face
    begins and ends with a narrow blind bay between the corner column and its partner."""
    samples = 20000
    points, total = [(SEMI_MAJOR, 0.0)], [0.0]
    for i in range(1, samples + 1):
        t = math.pi * i / samples
        point = (SEMI_MAJOR * math.cos(t), SEMI_MINOR * math.sin(t))
        total.append(total[-1] + math.hypot(point[0] - points[-1][0], point[1] - points[-1][1]))
        points.append(point)
    windows = HOUSES * BAYS
    pitch = (total[-1] - 2 * COUPLED) / windows
    stations = [0.0] + [COUPLED + pitch * j for j in range(windows + 1)] + [total[-1]]
    inner, at = [], 0
    for index, target in enumerate(stations):
        while at < samples and total[at + 1] < target:
            at += 1
        if index == 0:
            x, y = points[0]
        elif index == len(stations) - 1:
            x, y = points[-1]
        else:
            f = (target - total[at]) / (total[at + 1] - total[at])
            (ax, ay), (bx, by) = points[at], points[min(at + 1, samples)]
            x, y = ax + (bx - ax) * f, ay + (by - ay) * f
        nx, ny = unit2(x / SEMI_MAJOR ** 2, y / SEMI_MINOR ** 2) if y > 1e-9 else ((1.0, 0.0) if x > 0 else (-1.0, 0.0))
        inner.append(((round(x, 6), round(y, 6)), (nx, ny)))
    front = [point for point, _ in inner]
    outer = [(round(x + DEPTH * nx, 6), round(y + DEPTH * ny, 6)) for (x, y), (nx, ny) in inner]

    # Party walls stand square to the front, so the convex side is longer. Its nodes are
    # respaced house by house: the partner column 0.95 m from each corner, then equal bays.
    reach = [0.0]
    for a, b in zip(outer, outer[1:]):
        reach.append(reach[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

    def at_reach(distance):
        k = max(i for i in range(len(reach) - 1) if reach[i] <= distance + 1e-12)
        f = (distance - reach[k]) / (reach[k + 1] - reach[k])
        return (round(outer[k][0] + (outer[k + 1][0] - outer[k][0]) * f, 6), round(outer[k][1] + (outer[k + 1][1] - outer[k][1]) * f, 6))

    party = [0] + [1 + BAYS * h for h in range(1, HOUSES)] + [len(outer) - 1]
    respaced = list(outer)
    for h, (first, last) in enumerate(zip(party, party[1:])):
        start = reach[first] + (COUPLED if h == 0 else 0)
        end = reach[last] - (COUPLED if h == HOUSES - 1 else 0)
        if h == 0:
            respaced[1] = at_reach(start)
        if h == HOUSES - 1:
            respaced[-2] = at_reach(end)
        base = first + (1 if h == 0 else 0)
        for j in (1, 2):
            respaced[base + j] = at_reach(start + (end - start) * j / BAYS)
    outer = respaced

    def across(a, b):
        """The nodes strictly between two corners of an end, in travelling order."""
        way = 1 if b[0] > a[0] else -1
        step = (DEPTH - 2 * COUPLED) / END_BAYS
        return [(round(a[0] + way * (COUPLED + step * j), 6), 0.0) for j in range(END_BAYS + 1)]

    nodes = front + across(front[-1], outer[-1]) + outer[::-1] + across(outer[0], front[0])
    long_bays, end_bays = windows + 2, END_BAYS + 2
    starts = {'front': 0, 'west': long_bays, 'back': long_bays + end_bays, 'east': 2 * long_bays + end_bays}
    return nodes, starts


NODES, STARTS = outline()
LOOP = Loop(NODES)
BAY_COUNT = len(NODES)
FRONT_BAYS = HOUSES * BAYS + 2          # bays along each long face, counting the blind one at each end
END_FACE_BAYS = END_BAYS + 2
CORNERS = tuple(STARTS.values())


def side_of(k):
    if k < STARTS['west']:
        return 'front'
    if k < STARTS['back']:
        return 'west'
    return 'back' if k < STARTS['east'] else 'east'


def opening_kind(k):
    """'blind' for the narrow bay beside each corner. Otherwise what stands in the ground
    storey: a 'door' or a 'window'. The layout mirrors about the middle of the crescent."""
    side = side_of(k)
    j = k - STARTS[side]
    long_face = side in ('front', 'back')
    if j in (0, (FRONT_BAYS if long_face else END_FACE_BAYS) - 1):
        return 'blind'
    window = j - 1
    if long_face:
        house, place = divmod(window, BAYS)
        if place != 1 or (side == 'front' and house in (0, HOUSES - 1)):     # the two end houses are entered from their ends
            return 'window'
        return 'door'
    from_front = window if side == 'west' else END_BAYS - 1 - window
    return 'door' if from_front == 2 else 'window'


def frame_at(k):
    """The two directions a block at node k is squared to: its mitre line on a curve, the
    face itself at a corner."""
    k %= BAY_COUNT
    return (LOOP.along[k], LOOP.inward[k]) if k in CORNERS else (LOOP.tangent(k), LOOP.bisector[k])


def depth_inside(x, y):
    """How far a point lies behind the nearest outside face."""
    best = math.inf
    for (ax, ay), (bx, by) in zip(NODES, NODES[1:] + NODES[:1]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


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
    bay.box(clay, 'dressed', a - .06, b + .06, face - .06, face + .14, z0 - .10, z0 + .012)   # stone sill, weathered 12 mm above the wall it sits on


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


def block(clay, role, x, y, along, inward, half_u, half_n, z0, z1, caps=(True, True)):
    """A box square to a node's own tangent and mitre line. `caps` says whether to build
    its bottom and top; a face buried in its neighbour is left off."""
    ring = [(x + su * half_u * along[0] + sn * half_n * inward[0], y + su * half_u * along[1] + sn * half_n * inward[1]) for su, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    clay.prism(role, ring, z0, z1, caps=caps)


def column(clay, k):
    """One engaged Ionic column on its plinth block at node k. Every radial size is a
    multiple of the lower radius, so the order keeps its proportions if that changes."""
    x, y, _ = LOOP.node(k, AXIS)
    (along, inward), z, r = frame_at(k), FIRST, RADIUS
    block(clay, 'dressed', x, y, along, inward, PLINTH, PLINTH, z, z + .16, caps=(False, True))
    lathe(clay, 'dressed', x, y, [(1.24 * r, z + .16), (1.29 * r, z + .22), (1.10 * r, z + .30), (1.16 * r, z + .36), (r, z + .42)], steps=12, caps=(False, False))
    top = z + COLUMN - .52
    lathe(clay, 'dressed', x, y, [(r, z + .42), (r, z + 2.50), (.94 * r, z + 4.70), (.855 * r, top)], steps=12, caps=(False, False))
    lathe(clay, 'dressed', x, y, [(.855 * r, top), (.92 * r, top + .05), (.87 * r, top + .09), (1.05 * r, top + .22)], steps=12, caps=(False, True))
    centre = top + .27                       # the capital: a cushion between two scrolls that run front to back
    block(clay, 'dressed', x, y, along, inward, .90 * r, 1.05 * r, centre - .05, centre + .15)
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
    inner = WALL + THICK                      # the band stops at the wall's inner face, where the first floor begins
    LOOP.sweep(clay, 'dressed', [(inner, BAND), (-.07, BAND), (-.07, FIRST - .06), (-.04, FIRST), (inner, FIRST)])
    LOOP.sweep(clay, 'dressed', ENTABLATURE)
    LOOP.sweep(clay, 'dressed', [(.10, CORNICE), (.10, CORNICE + .22), (.60, CORNICE + .22), (.60, CORNICE)])           # blocking course
    LOOP.sweep(clay, 'dressed', [(.11, RAIL - .18), (.11, RAIL - .04), (.14, RAIL), (.56, RAIL), (.59, RAIL - .04), (.59, RAIL - .18)])   # top rail
    base = CORNICE + .22
    for k in range(BAY_COUNT):
        column(clay, k)
        x, y, _ = LOOP.node(k, .35)
        along, inward = frame_at(k)
        half = (.27, .27) if k in CORNERS else (.30, .24)      # a pedestal over each column, as deep as the rail it carries
        block(clay, 'dressed', x, y, along, inward, *half, base, RAIL - .18, caps=(False, False))
        bay = Bay(LOOP, k)
        if opening_kind(k) == 'blind':       # between a corner column and its partner the balustrade is a solid panel
            bay.box(clay, 'dressed', .27, bay.length - .27, .14, .56, base, RAIL - .18, ends=False)
        else:
            count = max(4, round((bay.length - .6) / .28))
            turn = math.atan2(bay.along[1], bay.along[0]) + math.pi / 4
            for j in range(count):
                u = .30 + (bay.length - .60) * (j + .5) / count
                bx, by, _ = bay.p(u, .35, 0)
                profile = [(.085, base), (.115, base + .20), (.055, base + .46), (.085, RAIL - .18)]
                clay.loft('dressed', [[(bx + r * math.cos(turn + math.pi / 2 * s), by + r * math.sin(turn + math.pi / 2 * s), z) for s in range(4)] for r, z in profile],
                          caps=(False, False))
        count = max(2, round(bay.length / .455))
        for j in range(count):               # modillions under the corona: front, underside and two cheeks
            u, z0, z1 = bay.length * (j + .5) / count, ARCHITRAVE + .99, ARCHITRAVE + 1.09
            a, b = u - .07, u + .07
            clay.quad('dressed', bay.p(a, -.34, z0), bay.p(b, -.34, z0), bay.p(b, -.34, z1), bay.p(a, -.34, z1), facing=bay.out)
            clay.quad('dressed', bay.p(a, -.34, z0), bay.p(b, -.34, z0), bay.p(b, .04, z0), bay.p(a, .04, z0), facing=(0, 0, -1))
            for end, side in ((a, -1), (b, 1)):
                clay.quad('dressed', bay.p(end, -.34, z0), bay.p(end, .04, z0), bay.p(end, .04, z1), bay.p(end, -.34, z1),
                          facing=(side * bay.along[0], side * bay.along[1], 0))


# ---- walls ---------------------------------------------------------------------------
GROUND_CUTS = (.02, GROUND_WINDOW[0], DOOR[2], GROUND_WINDOW[1], BAND)
UPPER_CUTS = (FIRST, FIRST_WINDOW[0], FIRST_WINDOW[1], SECOND_WINDOW[0], SECOND_WINDOW[1], CORNICE - .05)   # the wall stops inside the entablature


def panel(clay, bay, n0, n1, cuts, span=None, openings=()):
    """One bay of wall as a grid of faces. Every bay uses the same heights, so each corner
    of each face is shared with its neighbour and no hairline shows where pieces meet.
    `span` is the width the openings take and `openings` the (low, high) heights left
    open in it. Each opening gets jambs and a head of the wall's own thickness, and a
    sill unless it starts at the floor."""
    us = [0.0, bay.length] if span is None else [0.0, span[0], span[1], bay.length]
    rows = list(zip(cuts, cuts[1:]))

    def open_at(lo, hi):
        return any(low - 1e-9 <= lo and hi <= high + 1e-9 for low, high in openings)

    back = (-bay.out[0], -bay.out[1], 0.0)
    for column, (u0, u1) in enumerate(zip(us, us[1:])):
        for lo, hi in rows:
            if span is not None and column == 1 and open_at(lo, hi):
                continue
            for n, facing in ((n0, bay.out), (n1, back)):
                clay.quad('stone', bay.p(u0, n, lo), bay.p(u1, n, lo), bay.p(u1, n, hi), bay.p(u0, n, hi), facing=facing)
    if span is None:
        return
    a, b = span
    for low, high in openings:
        for lo, hi in rows:
            if low - 1e-9 <= lo and hi <= high + 1e-9:
                for u, side in ((a, 1), (b, -1)):
                    clay.quad('stone', bay.p(u, n0, lo), bay.p(u, n1, lo), bay.p(u, n1, hi), bay.p(u, n0, hi), facing=(side * bay.along[0], side * bay.along[1], 0.0))
        clay.quad('stone', bay.p(a, n0, high), bay.p(b, n0, high), bay.p(b, n1, high), bay.p(a, n1, high), facing=(0, 0, -1))
        if low > cuts[0] + 1e-9:
            clay.quad('stone', bay.p(a, n0, low), bay.p(b, n0, low), bay.p(b, n1, low), bay.p(a, n1, low), facing=(0, 0, 1))


def walls(clay):
    for k in range(BAY_COUNT):
        bay = Bay(LOOP, k)
        kind = opening_kind(k)
        if kind == 'blind':                  # solid wall between a corner column and its partner
            panel(clay, bay, 0, .90, GROUND_CUTS)
            panel(clay, bay, WALL, WALL + THICK, UPPER_CUTS)
            continue
        length, uc = bay.length, bay.length / 2
        a, b = uc - OPENING / 2, uc + OPENING / 2
        if kind == 'door':
            panel(clay, bay, 0, .90, GROUND_CUTS, (uc - DOOR[0] / 2, uc + DOOR[0] / 2), [(GROUND_CUTS[0], DOOR[2])])
            door(clay, bay, uc, 0)
        else:
            panel(clay, bay, 0, .90, GROUND_CUTS, (a, b), [GROUND_WINDOW])
            sash(clay, bay, uc, *GROUND_WINDOW, 0)
        # behind the columns: one wall with the tall first-floor sash and the second-floor sash
        (f0, f1), (s0, s1) = FIRST_WINDOW, SECOND_WINDOW
        panel(clay, bay, WALL, WALL + THICK, UPPER_CUTS, (a, b), [FIRST_WINDOW, SECOND_WINDOW])
        sash(clay, bay, uc, f0, f1, WALL)
        sash(clay, bay, uc, s0, s1, WALL)
        for u0, u1, lo, hi in ((a - .13, a, s0 - .10, s1 + .13), (b, b + .13, s0 - .10, s1 + .13), (a, b, s1, s1 + .13)):
            bay.box(clay, 'dressed', u0, u1, WALL - .035, WALL, lo, hi)
        # iron guard between the column plinths at the tall window
        clear = PLINTH + .02                 # the bottom rail is let into the plinth blocks; an end post stands on the band at each end
        bay.box(clay, 'iron', clear, length - clear, -.03, .00, FIRST + .86, FIRST + .90)
        bay.box(clay, 'iron', PLINTH - .02, length - PLINTH + .02, -.03, .00, FIRST + .06, FIRST + .09, ends=False)
        count = max(4, round((length - 2 * clear) / .18))
        for j in range(count + 1):
            post = j in (0, count)
            bay.cross(clay, 'iron', clear + (length - 2 * clear) * j / count, -.015, FIRST if post else FIRST + .09, FIRST + .86, width=.03 if post else .018)


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
                bay.cross(clay, 'iron', u, n0 + (n1 - n0) * j / count, .02, 1.22)
        bay.box(clay, 'dressed', uc - half, uc + half, -AREA - .10, -.05, .02, .035)         # flagged path over the area


# ---- roof --------------------------------------------------------------------------------
def party_lines():
    """Front and back node indices of each line between two houses, east to west. The
    first and last are the two ends."""
    fronts = [0] + [1 + BAYS * h for h in range(1, HOUSES)] + [FRONT_BAYS]
    return [(front, STARTS['east'] - front) for front in fronts]


def contour(depth, z):
    """The outline moved in by `depth`, as (bay, point) pairs in order: each point is where
    the moved-in lines of two bays meet, numbered by the bay that leaves it. A bay whose
    moved-in length has shrunk to nothing is dropped and its neighbours meet instead.
    That is what turns each corner into a hip, and what lets the short blind bays vanish."""
    def meet(i, j):
        (px, py, _), (qx, qy, _) = LOOP.node(i, 0), LOOP.node(j, 0)
        (ax, ay), (bx, by) = LOOP.along[i], LOOP.along[j]
        px, py = px + LOOP.inward[i][0] * depth, py + LOOP.inward[i][1] * depth
        qx, qy = qx + LOOP.inward[j][0] * depth, qy + LOOP.inward[j][1] * depth
        cross = ax * by - ay * bx
        if abs(cross) < 1e-9:                # the two bays lie in one line
            return (qx, qy)
        s = ((qx - px) * by - (qy - py) * bx) / cross
        return (px + ax * s, py + ay * s)

    bays = list(range(BAY_COUNT))
    while True:
        points = [meet(bays[m - 1], bays[m]) for m in range(len(bays))]
        runs = []
        for m, k in enumerate(bays):
            (x0, y0), (x1, y1) = points[m], points[(m + 1) % len(bays)]
            runs.append((x1 - x0) * LOOP.along[k][0] + (y1 - y0) * LOOP.along[k][1])
        worst = min(range(len(bays)), key=runs.__getitem__)
        if runs[worst] > 1e-6:
            return [(k, (round(x, 6), round(y, 6), z)) for k, (x, y) in zip(bays, points)]
        del bays[worst]


def strip(clay, role, outer, inner):
    """Skin between two contours, walking both in step. At each step the shorter of the
    two possible diagonals is taken, which runs the hips straight from corner to corner
    and never lets one face cross another."""
    def gap(p, q):
        return math.hypot(p[1][0] - q[1][0], p[1][1] - q[1][1])

    i = j = 0
    n, m = len(outer), len(inner)
    while i < n or j < m:
        a, b = outer[i % n], inner[j % m]
        a_next, b_next = outer[(i + 1) % n], inner[(j + 1) % m]
        if j >= m or (i < n and gap(a_next, b) <= gap(a, b_next)):
            clay.tri(role, a[1], a_next[1], b[1], facing=(0, 0, 1))
            i += 1
        else:
            clay.tri(role, a[1], b_next[1], b[1], facing=(0, 0, 1))
            j += 1


def roof(clay):
    """Two slate ranges with a lead flat between them, behind lead gutters. The roof's
    height depends only on the distance in from the nearest face, so it turns each of
    the four corners as a true hip."""
    gutter, eaves, ridge, valley = (contour(depth, z) for depth, z in ((WALL + THICK, CORNICE), (EAVES_SET, EAVES), (RIDGE_SET, RIDGE), (VALLEY_SET, VALLEY)))
    strip(clay, 'lead', gutter, eaves)
    strip(clay, 'slate', eaves, ridge)
    strip(clay, 'slate', ridge, valley)
    clay.polygon('lead', [point for _, point in valley], facing=(0, 0, 1))
    for front, back in party_lines()[1:-1]:
        party_wall(clay, front, back)
    for k in range(BAY_COUNT):
        if has_dormer(k):
            dormer(clay, Bay(LOOP, k))


DORMER = (2.05, 3.30, .56)        # nearest and farthest setback of a dormer, and half its width over the cap


def has_dormer(k):
    """Two dormers to a house on each long slope and two on each end, wherever the whole
    dormer stands on its own face's slope and clear of a hip."""
    side = side_of(k)
    window = k - STARTS[side] - 1
    if opening_kind(k) == 'blind':
        return False
    if side in ('front', 'back'):
        if window % BAYS == 1:
            return False
    elif (window if side == 'west' else END_BAYS - 1 - window) not in (2, 3):
        return False
    bay = Bay(LOOP, k)
    near, far, half = DORMER
    for u in (bay.length / 2 - half - .2, bay.length / 2 + half + .2):
        x, y, _ = bay.p(u, far + .1, 0)
        if depth_inside(x, y) < far + .1 - 1e-3:
            return False
    return True


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
        # each stack starts below the lowest roof it stands over, so no part of its base hangs in the air
        block(clay, 'stone', x, y, (tx, ty), (ux, uy), .45, 1.30, VALLEY - .10, RIDGE + STACK, caps=(False, True))
        block(clay, 'dressed', x, y, (tx, ty), (ux, uy), .52, 1.37, RIDGE + STACK, RIDGE + STACK + .18)
        for j in range(7):
            px, py = x + (-1.05 + .35 * j) * ux, y + (-1.05 + .35 * j) * uy
            lathe(clay, 'pot', px, py, [(.12, RIDGE + STACK + .18), (.10, RIDGE + STACK + .65), (.115, RIDGE + STACK + .71)], steps=6, caps=(False, True))


def dormer(clay, bay):
    """A small lead-topped dormer on the outer slope, with one sash and a blind drawn
    behind it. It is a roof feature only: there is no attic room."""
    near, far, half = DORMER
    uc, n0, n1 = bay.length / 2, near, far
    slope = (RIDGE - EAVES) / (RIDGE_SET - EAVES_SET)
    base, top = EAVES + (n0 - EAVES_SET) * slope, EAVES + (n0 - EAVES_SET) * slope + 1.05
    for u0, u1 in ((uc - .50, uc - .42), (uc + .42, uc + .50)):
        bay.box(clay, 'lead', u0, u1, n0, n1, base - .1, top)
    bay.box(clay, 'lead', uc - half, uc + half, n0 - .08, n1 + .1, top, top + .07)
    bay.box(clay, 'joinery', uc - .42, uc + .42, n0, n0 + .06, base + .02, base + .09)
    bay.box(clay, 'joinery', uc - .42, uc + .42, n0, n0 + .06, top - .07, top)
    bay.box(clay, 'joinery', uc - .02, uc + .02, n0, n0 + .05, base + .09, top - .07)
    bay.quad(clay, 'glass', uc - .42, uc + .42, n0 + .04, base + .09, top - .07)
    bay.quad(clay, 'interior', uc - .42, uc + .42, n0 + .10, base + .09, top - .07)       # the blind
    bay.quad(clay, 'lead', uc - .42, uc + .42, n1, base, top)


# ---- rooms ---------------------------------------------------------------------------------
def rooms(clay):
    """Floors, a spine wall and party walls, so every sash has a room behind it. Nothing
    here comes nearer an outside face than the inner face of the wall."""
    inset = WALL + THICK

    def middle(front, back):
        (ax, ay, _), (bx, by, _) = LOOP.node(front, inset), LOOP.node(back, inset)
        return ((ax + bx) / 2, (ay + by) / 2)

    for level, thick, role, edge in ((.02, .03, 'floor', .90), (FIRST - .12, .12, 'floor', inset), (SECOND - .12, .12, 'floor', inset),
                                     (EAVES - .30, .12, 'interior', inset)):
        # each floor is the outline moved in to the wall's inner face, so it meets every wall and enters none
        ring = [point for _, point in contour(edge, level)]
        clay.polygon(role, [(x, y, z + thick) for x, y, z in ring], facing=(0, 0, 1))
        clay.polygon(role, ring, facing=(0, 0, -1))
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
           'glass_close', 'entrance_contact', 'end_contact', 'end_roof', 'roof_contact', 'street', 'rear_ground', 'corner_close', 'match_front', 'match_oblique',
           'match_top')


def prework(candidate):
    """The measured contract this candidate is built to."""
    span = 2 * (SEMI_MAJOR + DEPTH)
    front_columns = FRONT_BAYS + 1
    return {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'state': 'prework', 'keeper_claimed': False, 'runtime_seed_allowed': False,
        'sources': source_lock(),
        'measurement_contract': {
            'dimensions_m': {'width': round(span, 1), 'depth': round(SEMI_MINOR + DEPTH, 1), 'range_depth': DEPTH, 'cornice': CORNICE, 'balustrade': RAIL,
                             'ridge': RIDGE, 'stack_top': round(RIDGE + STACK + .71, 2)},
            'storeys': STOREYS, 'storey_policy': 'fixed_authored_assembly', 'houses': HOUSES, 'window_bays_per_house': BAYS,
            'columns': {'all': BAY_COUNT, 'concave_front': front_columns, 'each_end': END_FACE_BAYS + 1},
            'source_measurements': {
                'front': [
                    'An eye-level view along the concave front from inside the crescent. It carries no scale. Scale is set by the column: 7.2 m, about 280 px at the right edge.',
                    'At the right-hand column: ground storey about 175 px of wall below the band, columns 270 to 280 px, entablature about 55 px, balustrade about 45 px. Built 4.4 m, 7.2 m, 1.4 m and 1.1 m.',
                    'Ground storey: plain ashlar with one tall window to a bay, about 2.0 m tall with its sill at railing height. Built 1.95 m tall with the sill at 1.15 m.',
                    'Behind the columns: a first-floor sash about 2.05 m tall with its sill 0.65 m above the column bases, and a second-floor sash about 1.75 m tall whose head is 0.8 m below the capitals.',
                    'Columns are slender, about eleven lower diameters tall, three-quarters engaged, Ionic, with the scrolls of each capital side by side as seen from the front.',
                    'At the far end two columns stand close together at the corner, with blind wall between them.',
                    'An iron guard stands between the column plinths at every first-floor window.',
                    'A continuous entablature with a modillion cornice, then a balustrade with a pedestal over every column and about six balusters to a bay.',
                    'Stone chimney stacks with a row of pots rise behind the balustrade at each party wall. Slate shows above the balustrade toward the far end.',
                    'Spear-headed iron railings run along the pavement edge.'],
                'oblique': [
                    'A view from high outside one end, looking along the convex side and across to the concave front.',
                    'Plan: close to half an ellipse. The far end faces back toward the camera.',
                    'House count. Front doors are three bays apart. The builder counted about forty columns on the visible two thirds of the concave front and estimated sixty bays. The independent reviewer counted 39 columns and 38 bays visible, estimated about sixteen hidden, and gave 54 bays and 18 houses, in a range of 50 to 58 bays. Built 18 houses of 3 window bays.',
                    'The near end has nine columns: a corner column and a partner close beside it at each corner, with blind wall between, and six window bays across the rest.',
                    'The end house has no door among its three front bays. It is entered from its end.',
                    'The giant order runs along the convex side as well as the concave front and the ends.',
                    'Each house: a white door and two windows at street level; a first-floor sash about 2.4 m tall and a second-floor sash about 1.6 m tall, each six panes over six.',
                    'Roof: slate ranges behind the balustrade, a stone upstand and broad stacks with about seven pots at each party wall, small dormers just behind the balustrade, a hipped roof over each end.',
                    'A sunken area with railings and a bridge to each door lies between the pavement and the front.'],
                'top': [
                    'A roof plan of a short block of about ten houses, concave on both long sides, with flared hipped ends. It is not the building the other two images show.',
                    'Used only for the character of the roof: two slate ranges with a lead flat and lead-covered additions between them, a stack on each party wall, dormers behind the parapet, hipped ends.'],
            },
            'source_conflicts': [
                'Plan and length. The roof plan shows about ten houses in a shallow block. The street view and the oblique, which agree with each other, show a long sweep on half an ellipse. Street view and oblique govern.',
                'House count. Part of the front is hidden in the oblique, so the count is an estimate: about twenty by the builder, about eighteen by the independent reviewer. Built eighteen.',
                f'Catalogue text. It gives 114 columns, thirty or more houses and a rusticated base. The images show about 54 bays on the front and plain ashlar. Built {front_columns} columns on the concave front, {BAY_COUNT} in all, {HOUSES} houses and a plain base.',
                'Catalogue plot. The catalogue lists a 6 m by 12 m plot, the size of one house. All three images show a complete crescent. Built as the complete crescent; each house is 6.8 m wide and 13.8 m deep.',
                'Window bars. The street view shows sashes with one large pane above another. The oblique shows six panes over six. Built six over six.',
                'First-floor sash height. About 2.05 m in the street view and about 2.4 m in the oblique. Built 2.35 m.',
                'Columns on the convex side. The oblique shows the giant order on the convex side. A real crescent of this kind has a plain back. Built as drawn.'],
            'camera_note': 'The three comparison cameras are approximate. No camera can register this model exactly against the oblique or the roof plan, because the images do not agree on the plan. The street camera matches the far end of the sweep; the near end renders somewhat larger than the reference.',
            'hidden_assumptions': [
                'The far end, and most of the convex side, are not shown in detail. Both ends are built alike, and the convex side repeats the front.',
                'Garden doors. One door to each house on the convex side is an invention; no image shows that side at street level.',
                'End doors. Each end has one door, in the third window bay from the concave front. The oblique shows a door on the near end; its exact bay is a reading of a small image.',
                'Interiors are inferred: three floors, a spine wall and party walls to each house, so that every window has a room behind it. They are schematic.',
                'Dormers are roof features only. Each has a sash with a blind drawn behind it; there is no attic room.',
                'The roof between the two slate ranges is a plain lead flat. The lead-covered additions in the roof plan are left out.',
                'The sunken areas, their steps and the bridges to the doors are left out, because nothing may lie below grade. Railings stand at grade and each door has a level stone path through them.',
                'Ashlar coursing and joints are left out, as surface texture.',
                'The crescent is taken to be symmetrical about its middle, in its plan, its doors and its dormers.',
                'Party walls stand square to the concave front, so bays on the convex side widen from 2.7 m at the middle to 4.0 m in the end houses.'],
        },
        'roof_contract': {'form': 'two slate ranges with a lead flat between, behind lead gutters and a stone balustrade; a true hip at each of the four corners',
                          'weathering': 'the roof height depends only on the distance in from the nearest face, so no plane crosses another; a stack stands through each ridge at every party wall'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()},
                              'note': 'every material is double-sided; the glass blends and carries the transmission extension, as the clay library does'},
        'identity_contract': ['half-ellipse crescent', 'eighteen houses of three window bays', 'three storeys', 'giant Ionic order on a plain ground storey',
                              'coupled columns and blind wall at every corner', 'nine columns across each end', 'one sash to a window bay on each storey',
                              'continuous entablature and balustrade', 'a stack with pots at every party wall', 'slate roof with dormers behind the balustrade, hipped at both ends',
                              'iron railings at the pavement'],
        'programme_contract': {'houses': HOUSES, 'street_doors': HOUSES, 'front_doors': HOUSES - 2, 'end_doors': 2, 'garden_doors': HOUSES},
        'contact_contract': {'base_datum_m': 0.0, 'lowest_geometry_m': 0.0, 'threshold_rise_m': .035,
                             'ground': 'a 20 mm paved strip 1.8 m wide round the building; no lawn, street or sunken area in the model'},
        'camera_roster': list(CAMERAS),
        'mandatory_review_views': ['front.png', 'front_corner.png', 'aerial.png', 'left_side.png', 'right_side.png', 'rear.png', 'rear_side.png',
                                   'facade_close.png', 'architecture_close.png', 'glass_close.png', 'entrance_contact.png', 'end_contact.png', 'end_roof.png',
                                   'roof_contact.png'],
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
        'storeys': STOREYS, 'houses': HOUSES, 'bays': BAY_COUNT, 'columns': BAY_COUNT, 'front_columns': FRONT_BAYS + 1,
        'entrances': {'front doors': sum(1 for d in doors if d['kind'] == 'front door'), 'garden doors': sum(1 for d in doors if d['kind'] == 'garden door'),
                      'end doors': sum(1 for d in doors if d['kind'] == 'end door'),
                      'street doors': sum(1 for d in doors if d['kind'] in ('front door', 'end door')), 'doors': doors},
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
