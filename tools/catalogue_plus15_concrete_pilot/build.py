"""Build the Brutalist Concrete Office Slab as an RLASM 6.1 architectural-clay GLB.

Exact variant: `calgary_15_connected_tower` / `brutalist_concrete_slab` (variant 0). The
model is plain constructive geometry written by `clay_kit`; nothing here needs Blender.

    python3 tools/catalogue_plus15_concrete_pilot/build.py --output <new directory>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, its
renders and boards are review material and stay outside Git until a human activates them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clay_kit import METHOD, Clay, arc, inset_polygon  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'plus15-brutalist-concrete-office'
ARCHETYPE, VARIANT, INDEX = 'calgary_15_connected_tower', 'brutalist_concrete_slab', 0
TITLE = 'Brutalist Concrete Office Slab'
SOURCE_DIR = 'frontend/public/archetypes/buildings/calgary-15-connected-tower'
SOURCES = {'front': f'variant_{INDEX}.png', 'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}

# ---- measured contract (metres) ------------------------------------------------
W, D = 45.0, 40.5                 # five 9 m bays across the front, four and a half deep
HX, HY = W / 2, D / 2
BAY, MODULE = 9.0, 1.5            # structural bay and window module
STOREYS = 5
FLOORS = (0.0, 5.2, 9.1, 13.0, 16.9)   # finished floor of storeys 1 to 5
ROOF, PARAPET = 20.8, 21.8
SILL, HEAD, SPANDREL = .80, 2.85, 1.85  # above a floor: window sill, window head; band height
CEILING = 2.90
FRAME_OUT, GLASS, FRAME_IN, RAIL = .24, .30, .36, .07   # ribbon glazing, inset from the cap strip's face
CAP = .52                         # height of the cap strip at the top of each band
REVEAL = (.10, .16)               # depth and height of the recess under each cap strip
STEP = .15                        # each band's main face sits this far behind its projecting cap strip
JOINT = .03
BASE, GROUND_FLOOR, SOFFIT, GROUND_CEILING = .02, .04, 4.15, 4.05
PIER, PIER_FACE = 1.3, .20        # granite pier size and its setback from the precast face
SHOP_OUT, SHOP_GLASS, SHOP_IN, TRANSOM = .90, .96, 1.02, 2.45
WALL_FACE, WALL_THICK = .75, .30  # granite infill walls of the service sides
PENT, PENT_TOP, PENT_WALL = 11.25, 27.6, .30   # penthouse half-size, top, wall thickness
WELL = 8.0                        # open mechanical well in the penthouse's rear east corner
BRIDGE_STOREY = 3                 # both references show the walkway at the third storey
BRIDGE_U, BRIDGE_HALF, BRIDGE_LENGTH = (9.0, 13.5), 2.23, 9.0   # opening along the east side from the front corner; the tube sits 20 mm clear of it each side

PALETTE = {  # role -> flat colour (sRGB), in node order
    'foundation': {'colour': '#5f5a52', 'module': 'apron'},
    'granite': {'colour': '#948e85', 'module': 'ground floor'},
    'concrete': {'colour': '#c8b89e', 'module': 'precast bands'},
    'joint': {'colour': '#75695a', 'module': 'panel joints'},
    'boardconcrete': {'colour': '#b8b1a2', 'module': 'penthouse'},
    'bridge': {'colour': '#b5afa3', 'module': 'plus 15 bridge'},
    'frame': {'colour': '#5d4833', 'module': 'glazing frames', 'roughness': .52},
    'coping': {'colour': '#5c4a38', 'module': 'roof edge', 'roughness': .52},
    'gravel': {'colour': '#8d867a', 'module': 'roof'},
    'membrane': {'colour': '#a8a297', 'module': 'roof'},
    'hardware': {'colour': '#565859', 'module': 'doors and plant', 'roughness': .52},
    'floor': {'colour': '#6f6a61', 'module': 'occupied floors'},
    'interior': {'colour': '#a8a092', 'module': 'occupied floors'},
    'structure': {'colour': '#7b756b', 'module': 'columns'},
    'light': {'colour': '#f6f0dd', 'module': 'occupied floors'},
    'timber': {'colour': '#a8662f', 'module': 'lobby'},
    'furniture': {'colour': '#5a564f', 'module': 'office furniture'},
    'shopglass': {'colour': '#b9c4c2', 'module': 'ground floor glazing', 'alpha': .14, 'roughness': .24},
    'glass': {'colour': '#2a2018', 'module': 'ribbon glazing', 'alpha': .45, 'roughness': .24, 'transmission': .28},
}


class Side:
    """One facade of a rectangle. `u` runs left to right seen from outside, `n` is the
    setback from the outer face, and `p` maps (u, n, z) to world coordinates."""

    OUT = {'front': (0, -1, 0), 'east': (1, 0, 0), 'rear': (0, 1, 0), 'west': (-1, 0, 0)}

    def __init__(self, name, hx=HX, hy=HY):
        self.name, self.hx, self.hy = name, hx, hy
        self.length = 2 * hx if name in ('front', 'rear') else 2 * hy
        self.out = self.OUT[name]

    def p(self, u, n, z):
        hx, hy = self.hx, self.hy
        return {'front': (-hx + u, -hy + n, z), 'east': (hx - n, -hy + u, z),
                'rear': (hx - u, hy - n, z), 'west': (-hx + n, hy - u, z)}[self.name]

    def box(self, clay, role, u0, u1, n0, n1, z0, z1):
        a, b = self.p(u0, n0, z0), self.p(u1, n1, z1)
        clay.box(role, a[0], b[0], a[1], b[1], a[2], b[2])

    def quad(self, clay, role, u0, u1, n, z0, z1):
        clay.quad(role, self.p(u0, n, z0), self.p(u1, n, z0), self.p(u1, n, z1), self.p(u0, n, z1), facing=self.out)

    def cross_quad(self, clay, role, u, n0, n1, z0, z1):
        """A quad standing square to the facade at `u`."""
        clay.quad(role, self.p(u, n0, z0), self.p(u, n1, z0), self.p(u, n1, z1), self.p(u, n0, z1))


FRONT, EAST, REAR, WEST = (Side(name) for name in ('front', 'east', 'rear', 'west'))
SIDES = (FRONT, EAST, REAR, WEST)


def bay_lines(side):
    """Structural lines along a facade. The half bay is at the rear of both flanks."""
    if side.name in ('front', 'rear'):
        return [BAY * k for k in range(1, 5)]
    lines = [BAY * k for k in range(1, 5)]
    return lines if side.name == 'east' else [D - u for u in reversed(lines)]


def bays(side):
    """Clear openings between the ground-floor piers, left to right."""
    edges = [PIER_FACE + PIER] + [v for u in bay_lines(side) for v in (u - PIER / 2, u + PIER / 2)] + [side.length - PIER_FACE - PIER]
    return list(zip(edges[::2], edges[1::2]))


# ---- precast bands ---------------------------------------------------------------
def spandrel_profile(bottom, soffit=FRAME_IN, lip=False):
    """Section of one precast band as (setback, height): the main face, a recessed reveal,
    a cap strip that projects beyond the face and throws a shadow line, then a sill
    running back to the window frame, as both references show at the corner. `soffit`
    deepens the underside; `lip` adds the lower moulding the first band carries."""
    top = bottom + SPANDREL
    foot = ([(soffit, bottom), (.06, bottom), (.04, bottom + .02), (.04, bottom + .26), (STEP, bottom + .30)] if lip
            else [(soffit, bottom), (STEP + .02, bottom), (STEP, bottom + .02)])
    deep, tall = REVEAL
    ring = foot + [(STEP, top - CAP - tall), (STEP + deep, top - CAP - tall), (STEP + deep, top - CAP), (.015, top - CAP),
                   (0, top - CAP + .015), (0, top - .075), (.02, top - .06), (FRAME_OUT, top - .03), (FRAME_IN, top - .03)]
    return ring + ([(FRAME_IN, bottom + .30), (soffit, bottom + .30)] if soffit > FRAME_IN else [])


def parapet_profile(bottom):
    """The top band: main face, reveal, then the same projecting cap strip, up to a concrete top."""
    deep, tall = REVEAL
    return [(FRAME_IN, bottom), (STEP + .02, bottom), (STEP, bottom + .02), (STEP, PARAPET - CAP - tall), (STEP + deep, PARAPET - CAP - tall),
            (STEP + deep, PARAPET - CAP), (.015, PARAPET - CAP), (0, PARAPET - CAP + .015), (0, PARAPET - .02), (.02, PARAPET),
            (.45, PARAPET), (.45, ROOF - .10), (FRAME_IN, ROOF - .10)]


def band(clay, side, profile, joints=(), openings=(), role='concrete'):
    """One band along one facade: mitred at both corners, split by a sealant joint at
    each structural line, and left open across `openings`."""
    joints = [u for u in joints if not any(a - JOINT <= u <= b + JOINT for a, b in openings)]   # an opening edge replaces a joint there
    marks = sorted([(u - JOINT / 2, u + JOINT / 2) for u in joints] + list(openings))
    start, pieces = ('mitre', 0.0), []
    for a, b in marks:
        pieces.append((start, ('cut', a)))
        start = ('cut', b)
    pieces.append((start, ('mitre', side.length)))
    for (kind_a, ua), (kind_b, ub) in pieces:
        first = [side.p(d if kind_a == 'mitre' else ua, d, z) for d, z in profile]
        last = [side.p(side.length - d if kind_b == 'mitre' else ub, d, z) for d, z in profile]
        clay.loft(role, [first, last], caps=(kind_a == 'cut', kind_b == 'cut'))
    sealant = inset_polygon(profile, .02)
    for u in joints:
        clay.loft('joint', [[side.p(u - JOINT, d, z) for d, z in sealant], [side.p(u + JOINT, d, z) for d, z in sealant]], caps=(False, False))


def ring(clay, role, profile, hx=HX, hy=HY):
    """A continuous mitred band right round a rectangle."""
    clay.loft(role, [[(sx * (hx - d), sy * (hy - d), z) for d, z in profile] for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], loop=True)


def spans(a, b, openings):
    """The parts of [a, b] outside the open intervals."""
    out, at = [], a
    for lo, hi in sorted(openings):
        if lo > at:
            out.append((at, min(lo, b)))
        at = max(at, hi)
    if at < b:
        out.append((at, b))
    return out


def ribbon(clay, side, floor, openings=()):
    """One storey's ribbon window on one facade: bronze frame, recessed bronze glass."""
    z0, z1, length = floor + SILL - .03, floor + HEAD, side.length
    for a, b in spans(FRAME_IN, length - FRAME_IN, openings):
        side.box(clay, 'frame', a, b, FRAME_OUT, FRAME_IN, z0, z0 + RAIL)
        side.box(clay, 'frame', a, b, FRAME_OUT, FRAME_IN, z1 - RAIL, z1)
    for a, b in spans(GLASS, length - GLASS, openings):
        side.quad(clay, 'glass', a, b, GLASS, z0 + RAIL, z1 - RAIL)
    side.box(clay, 'frame', FRAME_OUT, FRAME_IN, FRAME_OUT, FRAME_IN, z0, z1)   # corner post
    for k in range(1, round(length / MODULE)):
        u = k * MODULE
        if not any(lo < u < hi for lo, hi in openings):
            post = any(u in edge for edge in openings)      # the rails stop at an opening, so its edge posts run full height
            side.box(clay, 'frame', u - .03, u + .03, FRAME_OUT, FRAME_IN, z0 if post else z0 + RAIL, z1 if post else z1 - RAIL)


def envelope(clay):
    bridge_floor = FLOORS[BRIDGE_STOREY - 1]
    for storey in range(2, STOREYS + 1):
        floor = FLOORS[storey - 1]
        bottom = floor + SILL - SPANDREL
        for side in SIDES:
            at_bridge = side is EAST and storey == BRIDGE_STOREY
            band(clay, side, spandrel_profile(bottom, 1.6 if storey == 2 else FRAME_IN, lip=storey == 2), bay_lines(side), [BRIDGE_U] if at_bridge else [])
            ribbon(clay, side, floor, [BRIDGE_U] if at_bridge else [])
    # under the walkway the band's face carries on below the bridge and becomes its threshold
    bottom = bridge_floor + SILL - SPANDREL
    sill = [(FRAME_IN, bottom), (STEP + .02, bottom), (STEP, bottom + .02), (STEP, bridge_floor), (FRAME_IN, bridge_floor)]
    clay.loft('concrete', [[EAST.p(u, d, z) for d, z in sill] for u in BRIDGE_U], caps=(False, False))
    top = FLOORS[-1] + HEAD
    for side in SIDES:
        band(clay, side, parapet_profile(top), bay_lines(side))
    # bronze flashing wraps the inner edge of the parapet, as the roof plan shows
    ring(clay, 'coping', [(.32, PARAPET), (.32, PARAPET + .025), (.475, PARAPET + .025), (.475, PARAPET - .30), (.45, PARAPET - .30), (.45, PARAPET)])
    clay.box('gravel', -HX + .45, HX - .45, -HY + .45, HY - .45, ROOF - .20, ROOF)


# ---- ground floor ----------------------------------------------------------------
def pier(clay, cx, cy):
    """A granite-clad pier with chamfered corners, a base course and a shadow gap at the soffit."""
    h, c = PIER / 2, .04
    outline = [(cx + sx * (h - (c if k else 0)), cy + sy * (h - (0 if k else c)))
               for (sx, sy), order in (((-1, -1), (0, 1)), ((1, -1), (1, 0)), ((1, 1), (0, 1)), ((-1, 1), (1, 0))) for k in order]
    clay.prism('granite', outline, BASE + .14, SOFFIT - .08)
    clay.box('foundation', cx - h - .015, cx + h + .015, cy - h - .015, cy + h + .015, BASE, BASE + .14)
    clay.box('joint', cx - h + .07, cx + h - .07, cy - h + .07, cy + h - .07, SOFFIT - .08, SOFFIT)


def piers(clay):
    centre = PIER_FACE + PIER / 2
    for side in SIDES:
        for u in bay_lines(side):
            x, y, _ = side.p(u, centre, 0)
            pier(clay, x, y)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pier(clay, sx * (HX - centre), sy * (HY - centre))


def door_leaf(clay, side, a, b, handle):
    """A glazed bronze door leaf in a storefront. `handle` is the pull's position along the facade."""
    lo, hi, n0, n1 = BASE + .015, TRANSOM, SHOP_GLASS - .03, SHOP_GLASS + .03
    side.box(clay, 'frame', a, a + .09, n0, n1, lo, hi)
    side.box(clay, 'frame', b - .09, b, n0, n1, lo, hi)
    side.box(clay, 'frame', a + .09, b - .09, n0, n1, lo, lo + .22)
    side.box(clay, 'frame', a + .09, b - .09, n0, n1, hi - .09, hi)
    side.quad(clay, 'shopglass', a + .09, b - .09, SHOP_GLASS, lo + .22, hi - .09)
    side.box(clay, 'hardware', handle - .018, handle + .018, n0 - .10, n0 - .065, .95, 1.85)
    for z in (1.02, 1.78):
        side.box(clay, 'hardware', handle - .012, handle + .012, n0 - .065, n0, z - .012, z + .012)


def storefront(clay, side, u0, u1, panes, doors=()):
    """A glazed bay between two piers: bronze frame, transom at door-head height."""
    top = SOFFIT - .10
    side.box(clay, 'frame', u0, u1, SHOP_OUT, SHOP_IN, top, SOFFIT)
    side.box(clay, 'frame', u0, u1, SHOP_OUT, SHOP_IN, TRANSOM, TRANSOM + .08)
    width = (u1 - u0) / panes
    for k in range(panes + 1):
        u = min(max(u0 + k * width, u0 + .03), u1 - .03)
        meeting = k in doors and k - 1 in doors        # two leaves meet here: no post below the transom
        side.box(clay, 'frame', u - .03, u + .03, SHOP_OUT, SHOP_IN, TRANSOM + .08 if meeting else BASE, top)
    for k in range(panes):
        a, b = u0 + k * width + (.06 if k == 0 else .03), u0 + (k + 1) * width - (.06 if k == panes - 1 else .03)
        if k in doors:
            pair_left = k + 1 in doors
            door_leaf(clay, side, a - (0 if pair_left or k - 1 not in doors else .03), b + (.03 if pair_left else 0), b - .06 if pair_left else a + .06)
        else:
            side.box(clay, 'frame', a, b, SHOP_OUT, SHOP_IN, BASE, BASE + .12)
            side.quad(clay, 'shopglass', a, b, SHOP_GLASS, BASE + .12, TRANSOM)
        side.quad(clay, 'shopglass', a, b, SHOP_GLASS, TRANSOM + .08, top)
    if doors:
        a, b = u0 + min(doors) * width, u0 + (max(doors) + 1) * width
        side.box(clay, 'hardware', a, b, SHOP_OUT - .04, SHOP_IN + .04, BASE, BASE + .015)   # threshold plate


def panel_wall(clay, side, us, zs, face, thick, role, openings=(), proud=.03, gap=.03, trim=0.0):
    """A clad wall: a structural leaf, a dark joint layer, and panels on the grid `us` by `zs`.

    Openings are (u0, u1, z0, z1) holes cut right through, so each keeps true jamb, head
    and sill returns of the wall's own thickness. `trim` shortens the leaf at both ends,
    for walls that meet another at a corner."""
    def void(u, z):
        return any(a < u < b and c < z < d for a, b, c, d in openings)

    cut_u = sorted({us[0] + trim, us[-1] - trim, *[v for o in openings for v in o[:2]]})
    cut_z = sorted({zs[0], zs[-1], *[v for o in openings for v in o[2:]]})
    for a, b in zip(cut_u, cut_u[1:]):
        for c, d in zip(cut_z, cut_z[1:]):
            if not void((a + b) / 2, (c + d) / 2):
                side.box(clay, role, a, b, face + proud + .012, face + thick, c, d)
                side.box(clay, 'joint', a, b, face + proud, face + proud + .012, c, d)
    for a, b in zip(us, us[1:]):
        for c, d in zip(zs, zs[1:]):
            part_u = sorted({a + gap / 2, b - gap / 2, *[v for o in openings for v in o[:2] if a < v < b]})
            part_z = sorted({c + gap / 2, d - gap / 2, *[v for o in openings for v in o[2:] if c < v < d]})
            for e, f in zip(part_u, part_u[1:]):
                for g, h in zip(part_z, part_z[1:]):
                    if not void((e + f) / 2, (g + h) / 2):
                        side.box(clay, role, e, f, face, face + proud + .001, g, h)


def grid(a, b, count):
    return [a + (b - a) * k / count for k in range(count + 1)]


def louvre(clay, side, u0, u1, z0, z1, face):
    """Horizontal blades in a frame, set into a wall opening."""
    for a, b, c, d in ((u0, u1, z0, z0 + .06), (u0, u1, z1 - .06, z1), (u0, u0 + .06, z0, z1), (u1 - .06, u1, z0, z1)):
        side.box(clay, 'hardware', a, b, face + .06, face + .18, c, d)
    side.quad(clay, 'hardware', u0, u1, face + .20, z0, z1)
    z = z0 + .10
    while z < z1 - .12:
        clay.quad('membrane', side.p(u0 + .06, face + .07, z), side.p(u1 - .06, face + .07, z),
                  side.p(u1 - .06, face + .16, z + .09), side.p(u0 + .06, face + .16, z + .09), facing=(side.out[0], side.out[1], 1))
        z += .13


def service_door(clay, side, u0, u1, z0, z1, face):
    """A flat steel door in a pressed frame, with a pull."""
    for a, b, c, d in ((u0, u1, z1 - .05, z1), (u0, u0 + .05, z0, z1), (u1 - .05, u1, z0, z1)):
        side.box(clay, 'hardware', a, b, face + .05, face + .17, c, d)
    side.box(clay, 'frame', u0 + .05, u1 - .05, face + .10, face + .15, z0, z1 - .05)
    side.box(clay, 'hardware', u1 - .22, u1 - .18, face + .06, face + .10, z0 + .95, z0 + 1.15)


def rollup(clay, side, u0, u1, z0, z1, face):
    """A sectional overhead door, recessed, with its ribs and guides."""
    side.box(clay, 'hardware', u0, u1, face + .20, face + .24, z0, z1)
    z = z0 + .30
    while z < z1 - .05:
        side.box(clay, 'frame', u0 + .08, u1 - .08, face + .185, face + .20, z - .012, z + .012)
        z += .30
    for a, b in ((u0, u0 + .08), (u1 - .08, u1)):
        side.box(clay, 'frame', a, b, face + .14, face + .24, z0, z1)


def window(clay, side, u0, u1, z0, z1, face, panes):
    """A fixed window set back in a wall opening: bronze frame, bronze glass."""
    n0, n1 = face + .10, face + .19
    for a, b, c, d in ((u0, u1, z0, z0 + .05), (u0, u1, z1 - .05, z1)):
        side.box(clay, 'frame', a, b, n0, n1, c, d)
    for u in grid(u0, u1, panes):
        u = min(max(u, u0 + .025), u1 - .025)
        side.box(clay, 'frame', u - .025, u + .025, n0, n1, z0 + .05, z1 - .05)
    side.quad(clay, 'glass', u0 + .05, u1 - .05, face + .145, z0 + .05, z1 - .05)


def granite_bay(clay, side, u0, u1, openings=()):
    columns = max(2, round((u1 - u0) / 1.34))
    panel_wall(clay, side, grid(u0, u1, columns), [BASE, 1.40, 2.75, SOFFIT], WALL_FACE, WALL_THICK, 'granite', openings)


def ground_floor(clay):
    clay.box('foundation', -HX, HX, -HY, HY, 0, BASE)
    piers(clay)
    # street front: five glazed bays, the entrance in the second bay from the east corner
    for index, (a, b) in enumerate(bays(FRONT)):
        storefront(clay, FRONT, a, b, 6, doors=(2, 3) if index == 3 else ())
    # east flank: the lobby glazing returns round the corner, then blank granite and a service door
    east = bays(EAST)
    storefront(clay, EAST, east[0][0], east[0][0] + 2.4, 2)
    granite_bay(clay, EAST, east[0][0] + 2.4, east[0][1])
    for a, b in east[1:4]:
        granite_bay(clay, EAST, a, b)
    a, b = east[4]
    door = (a + .2, b - .2, BASE, 3.2)
    panel_wall(clay, EAST, [a, b], [BASE, SOFFIT], WALL_FACE, WALL_THICK, 'granite', [door])
    rollup(clay, EAST, *door, WALL_FACE)
    # west flank, unseen in the references: the mirror of the east, with plant louvres and an exit
    west = bays(WEST)
    a, b = west[0]
    door = (a + .9, a + 1.9, BASE, 2.25)
    panel_wall(clay, WEST, [a, b], [BASE, SOFFIT], WALL_FACE, WALL_THICK, 'granite', [door])
    service_door(clay, WEST, *door, WALL_FACE)
    granite_bay(clay, WEST, *west[1])
    a, b = west[2]
    vents = [(a + 1.34, a + 3.9, 1.40, 2.75), (b - 3.9, b - 1.34, 1.40, 2.75)]
    granite_bay(clay, WEST, a, b, vents)
    for vent in vents:
        louvre(clay, WEST, *vent, WALL_FACE)
    granite_bay(clay, WEST, *west[3])
    granite_bay(clay, WEST, west[4][0], west[4][1] - 2.4)
    storefront(clay, WEST, west[4][1] - 2.4, west[4][1], 2)
    # rear, unseen in the references: service side with high windows, a loading door and a staff exit
    for index, (a, b) in enumerate(bays(REAR)):
        step = (b - a) / 6
        if index == 1:
            dock = (a + step, b - step, BASE, 3.60)
            granite_bay(clay, REAR, a, b, [dock])
            rollup(clay, REAR, *dock, WALL_FACE)
            continue
        high = (a + step, b - step, 2.75, 3.65)
        holes = [high] + ([(a + .25, a + 1.25, BASE, 2.25)] if index == 3 else [])
        granite_bay(clay, REAR, a, b, holes)
        window(clay, REAR, *high, WALL_FACE, 4)
        if index == 3:
            service_door(clay, REAR, *holes[1], WALL_FACE)


# ---- interiors ---------------------------------------------------------------------
CORE = (-9.0, 9.0, -4.5, 9.0)            # lifts, stairs and risers at street level
ROOMS = (-16.0, 16.0, -13.75, 13.75)     # core and enclosed rooms on the office floors


def within(block, x, y, margin=0.0):
    return block[0] - margin < x < block[1] + margin and block[2] - margin < y < block[3] + margin


def ceiling_lights(clay, z, block, y_range=(-18.0, 18.0)):
    x = -19.5
    while x <= 19.5:
        y = y_range[0]
        while y <= y_range[1]:
            if not within(block, x, y, .4):
                clay.box('light', x - .6, x + .6, y - .3, y + .3, z, z + .04)
            y += 3.0
        x += 3.0


def workstation(clay, side, u, floor):
    side.box(clay, 'furniture', u - .8, u + .8, 2.40, 3.15, floor + .70, floor + .74)
    for end in (u - .78, u + .74):
        side.box(clay, 'furniture', end, end + .04, 2.42, 3.13, floor, floor + .70)
    side.box(clay, 'furniture', u - .24, u + .24, 3.35, 3.83, floor + .40, floor + .48)
    side.box(clay, 'furniture', u - .24, u + .24, 3.79, 3.85, floor + .48, floor + .95)


def columns(clay):
    lines_x, lines_y = [-13.5, -4.5, 4.5, 13.5], [-11.25, -2.25, 6.75, 15.75]
    for x in lines_x:                       # interior columns
        for y in lines_y:
            if not within(CORE, x, y):
                clay.box('structure', x - .3, x + .3, y - .3, y + .3, GROUND_FLOOR, GROUND_CEILING)
            if not within(ROOMS, x, y):
                clay.box('structure', x - .3, x + .3, y - .3, y + .3, FLOORS[1], ROOF - .2)
    back = 1.5                              # perimeter columns stand well behind the glass and clear of the light fittings
    edge = [(x, sy * (HY - back)) for x in lines_x for sy in (-1, 1)] + [(sx * (HX - back), y) for y in lines_y for sx in (-1, 1)]
    edge += [(sx * (HX - back), sy * (HY - back)) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in edge:
        clay.box('structure', x - .3, x + .3, y - .3, y + .3, FLOORS[1], ROOF - .2)


def offices(clay):
    x0, x1, y0, y1 = -HX + FRAME_IN, HX - FRAME_IN, -HY + FRAME_IN, HY - FRAME_IN
    for storey in range(2, STOREYS + 1):
        floor = FLOORS[storey - 1]
        above = FLOORS[storey] if storey < STOREYS else ROOF + .15
        clay.box('floor', x0, x1, y0, y1, floor - .35, floor)
        clay.box('interior', x0, x1, y0, y1, floor + CEILING, above - .35)
        ceiling_lights(clay, floor + CEILING - .04, ROOMS)
        for side in SIDES:
            for wall, a, b in ((4.5, FRAME_IN + .02, 4.45), (side.length - 4.5, side.length - 4.45, side.length - FRAME_IN - .02)):
                # corner rooms with their blinds drawn, so no sight line runs clean through a corner
                side.box(clay, 'interior', wall - .05, wall + .05, FRAME_IN + .02, HY + ROOMS[2], floor, floor + CEILING)
                side.box(clay, 'furniture', a, b, FRAME_IN + .07, FRAME_IN + .09, floor + SILL + .05, floor + HEAD - .08)
            u = 7.5
            while u <= side.length - 7.5:
                at_bridge = side is EAST and storey == BRIDGE_STOREY and BRIDGE_U[0] - 1.2 < u < BRIDGE_U[1] + 1.2
                if not at_bridge:
                    workstation(clay, side, u, floor)
                u += 3.0
    clay.box('interior', CORE[0], CORE[1], CORE[2], CORE[3], GROUND_FLOOR, GROUND_CEILING)
    clay.box('interior', ROOMS[0], ROOMS[1], ROOMS[2], ROOMS[3], FLOORS[1], ROOF - .2)
    columns(clay)


def lobby(clay):
    inside_x, inside_y = HX - SHOP_IN, HY - SHOP_IN
    clay.box('floor', -inside_x, inside_x, -inside_y, inside_y, BASE, GROUND_FLOOR)
    clay.box('interior', -inside_x, inside_x, -inside_y, inside_y, GROUND_CEILING, FLOORS[1] - .35)
    ceiling_lights(clay, GROUND_CEILING - .04, CORE, (-17.5, -14.5))
    # shop units behind the three western bays, the office lobby behind the two eastern ones
    for x in (-13.5, -4.5, 4.5):
        clay.box('interior', x - .1, x + .1, -HY + PIER_FACE + PIER, -11.0, GROUND_FLOOR, GROUND_CEILING)
    clay.box('interior', -inside_x, 4.5, -11.2, -11.0, GROUND_FLOOR, GROUND_CEILING)
    for x in (-18.0, -9.0, 0.0):
        clay.box('timber', x - 1.6, x + 1.6, -12.6, -11.9, GROUND_FLOOR, GROUND_FLOOR + .95)
        clay.box('light', x - 1.65, x + 1.65, -12.65, -11.85, GROUND_FLOOR + .95, GROUND_FLOOR + .99)
        for dx in (-1.7, 1.7):
            clay.box('furniture', x + dx - .7, x + dx + .7, -16.4, -15.6, GROUND_FLOOR, GROUND_FLOOR + .78)
    back = -13.0
    clay.box('interior', 4.5, inside_x, back, back + .2, GROUND_FLOOR, GROUND_CEILING)
    x = 11.0                                # timber panelling, as seen through the corner bay
    while x < 19.4:
        clay.box('timber', x + .012, x + 1.2 - .012, back - .05, back, GROUND_FLOOR + .10, 3.60)
        x += 1.2
    for x in (5.6, 7.6):                    # lift doors
        clay.box('hardware', x, x + 1.2, back - .03, back, GROUND_FLOOR, 2.30)
        clay.box('frame', x + .59, x + .61, back - .035, back - .03, GROUND_FLOOR, 2.30)
    clay.box('timber', 14.0, 17.4, -15.9, -15.1, GROUND_FLOOR, 1.10)        # reception desk
    clay.box('light', 13.95, 17.45, -15.95, -15.05, 1.10, 1.14)
    # glazed draught lobby inside the entrance doors
    a, b = bays(FRONT)[3]
    width = (b - a) / 6
    u0, u1, depth, top = a + 2 * width - .03, a + 4 * width + .03, 3.3, 2.60
    for u in (u0, u1):
        FRONT.cross_quad(clay, 'shopglass', u, SHOP_IN, depth, GROUND_FLOOR, top)
        FRONT.box(clay, 'frame', u - .03, u + .03, depth - .06, depth, GROUND_FLOOR, top)
    FRONT.box(clay, 'frame', u0 - .03, u1 + .03, SHOP_IN, depth, top, top + .08)
    FRONT.quad(clay, 'shopglass', u0 + .03, u1 - .03, depth - .03, GROUND_FLOOR, top)
    FRONT.box(clay, 'frame', (u0 + u1) / 2 - .03, (u0 + u1) / 2 + .03, depth - .06, depth, GROUND_FLOOR, top)


# ---- roof ----------------------------------------------------------------------------
def penthouse(clay):
    sides = [Side(name, PENT, PENT) for name in ('front', 'east', 'rear', 'west')]
    us, mid = grid(0, 2 * PENT, 8), ROOF + 3.70
    door, vent = (7.0, 8.0, ROOF + .10, ROOF + 2.25), (9.0, 13.5, ROOF + 1.00, mid)
    for side in sides:
        holes = [door, vent] if side.name == 'east' else []
        panel_wall(clay, side, us, [ROOF, mid, PENT_TOP], 0.0, PENT_WALL, 'boardconcrete', holes, trim=.042)
        if holes:
            service_door(clay, side, *door, 0.0)
            louvre(clay, side, *vent, 0.0)
            side.box(clay, 'boardconcrete', door[0] - .2, door[1] + .2, -1.0, 0.0, ROOF, ROOF + .10)   # door landing
    ring(clay, 'boardconcrete', [(-.015, PENT_TOP), (-.015, PENT_TOP + .06), (PENT_WALL + .015, PENT_TOP + .06), (PENT_WALL + .015, PENT_TOP)], PENT, PENT)
    inner, well = PENT - PENT_WALL, PENT - WELL
    clay.box('membrane', -inner, well - .25, -inner, inner, PENT_TOP - .40, PENT_TOP - .25)
    clay.box('membrane', well - .25, inner, -inner, well - .25, PENT_TOP - .40, PENT_TOP - .25)
    clay.box('boardconcrete', well - .25, well, well - .25, inner, ROOF, PENT_TOP)   # walls of the open well
    clay.box('boardconcrete', well, inner, well - .25, well, ROOF, PENT_TOP)
    # plant in the well: one cooling unit, as the top view shows
    cx = cy = PENT - PENT_WALL - (WELL - PENT_WALL) / 2
    clay.box('hardware', cx - 1.6, cx + 1.6, cy - 1.6, cy + 1.6, ROOF + .25, ROOF + 2.45)
    for dx in (-1.4, 1.4):
        for dy in (-1.4, 1.4):
            clay.box('hardware', cx + dx - .08, cx + dx + .08, cy + dy - .08, cy + dy + .08, ROOF, ROOF + .25)
    clay.box('membrane', cx - 1.68, cx + 1.68, cy - 1.68, cy + 1.68, ROOF + 2.45, ROOF + 2.55)
    for a, b, c, d in ((-1.68, 1.68, -1.68, -1.30), (-1.68, 1.68, 1.30, 1.68), (-1.68, -1.30, -1.30, 1.30), (1.30, 1.68, -1.30, 1.30)):
        clay.box('membrane', cx + a, cx + b, cy + c, cy + d, ROOF + 2.55, ROOF + 2.70)        # raised rim of the outlet
    clay.box('hardware', cx - 1.30, cx + 1.30, cy - 1.30, cy + 1.30, ROOF + 2.55, ROOF + 2.60)       # outlet grille
    for k in range(1, 6):
        clay.box('frame', cx - 1.30 + k * .433 - .02, cx - 1.30 + k * .433 + .02, cy - 1.30, cy + 1.30, ROOF + 2.60, ROOF + 2.64)
    # the few roof items the references show: a hatch, a vent, one unit and two conduit runs
    clay.box('membrane', .7, 1.9, -13.5, -12.3, ROOF, ROOF + .40)
    clay.box('hardware', .65, 1.95, -13.55, -12.25, ROOF + .40, ROOF + .46)
    clay.cylinder('hardware', 14.1, -2.8, ROOF, ROOF + .45, .22, 12)
    clay.cylinder('hardware', 14.1, -2.8, ROOF + .45, ROOF + .50, .32, 12)
    top = PENT_TOP - .25
    clay.box('hardware', 5.75, 7.05, -.25, .85, top + .10, top + .90)
    for dx in (5.85, 6.95):
        clay.box('hardware', dx - .05, dx + .05, -.2, .8, top, top + .10)
    for y in (7.2, 3.3):
        clay.box('hardware', -8.7, -5.2, y - .04, y + .04, top + .06, top + .14)
        for x in (-8.5, -6.95, -5.4):
            clay.box('hardware', x - .05, x + .05, y - .07, y + .07, top, top + .06)


# ---- the walkway -----------------------------------------------------------------------
def bridge(clay):
    """The +15 walkway: a concrete tube with eased edges and ribbon glazing, built as a
    length that stops short of a neighbour and is closed by a glazed end. Its glazed band
    is a little taller than the office ribbons, as the street view shows."""
    floor = FLOORS[BRIDGE_STOREY - 1]
    sill, head, half, wall, ease = floor + .65, floor + HEAD, BRIDGE_HALF, .30, .35
    bottom, top = sill - 1.25, head + 1.15
    yc = -HY + sum(BRIDGE_U) / 2
    x0, x1 = HX - STEP, HX + BRIDGE_LENGTH
    belly = ([(-half, sill), (-half, bottom + ease)] + arc(-half + ease, bottom + ease, ease, 180, 270, 10)[1:]
             + arc(half - ease, bottom + ease, ease, 270, 360, 10)
             + [(half, sill), (half - wall, sill), (half - wall, floor), (-half + wall, floor), (-half + wall, sill)])
    crown = ([(-half, head), (half, head), (half, top - ease)] + arc(half - ease, top - ease, ease, 0, 90, 10)[1:]
             + arc(-half + ease, top - ease, ease, 90, 180, 10))
    for section in (belly, crown):
        clay.loft('bridge', [[(x, yc + y, z) for y, z in section] for x in (x0, x1)], caps=(False, True), smooth=40)
    # solid jambs close the mouth between the band face and the building's own glass line
    for a, b in ((BRIDGE_U[0] + .03, BRIDGE_U[0] + .31), (BRIDGE_U[1] - .31, BRIDGE_U[1] - .03)):
        EAST.box(clay, 'bridge', a, b, STEP, FRAME_IN, floor, head)
    for a, b in ((BRIDGE_U[0], BRIDGE_U[0] + .03), (BRIDGE_U[1] - .03, BRIDGE_U[1])):      # under the edge posts of the office ribbon
        EAST.box(clay, 'bridge', a, b, STEP, FRAME_IN, floor, floor + SILL - .03)
    clay.box('bridge', x1 - wall, x1, yc - half + wall, yc + half - wall, floor, sill)      # end upstand
    clay.box('floor', HX - FRAME_IN, x1 - wall, yc - half + wall, yc + half - wall, floor, floor + .02)
    clay.box('light', x0 + .5, x1 - .9, yc - .25, yc + .25, head - .04, head)
    n0, n1, g = .06, .16, .11
    for sign in (-1, 1):                    # ribbon glazing down both sides, close to the face
        y0, y1, yg = yc + sign * (half - n0), yc + sign * (half - n1), yc + sign * (half - g)
        clay.box('frame', x0, x1 - n1, y0, y1, sill, sill + RAIL)
        clay.box('frame', x0, x1 - n1, y0, y1, head - RAIL, head)
        clay.quad('glass', (x0, yg, sill + RAIL), (x1 - g, yg, sill + RAIL), (x1 - g, yg, head - RAIL), (x0, yg, head - RAIL), facing=(0, sign, 0))
        clay.box('frame', x0, x0 + .06, y0, y1, sill + RAIL, head - RAIL)
        for k in range(1, round(BRIDGE_LENGTH / MODULE)):
            x = HX + k * MODULE
            clay.box('frame', x - .03, x + .03, y0, y1, sill + RAIL, head - RAIL)
        clay.box('frame', x1 - n1, x1 - n0, y0, y1, sill, head)                               # corner post
    ya, yb = yc - half + n1, yc + half - n1                                                    # glazed end
    clay.box('frame', x1 - n1, x1 - n0, ya, yb, sill, sill + RAIL)
    clay.box('frame', x1 - n1, x1 - n0, ya, yb, head - RAIL, head)
    clay.quad('glass', (x1 - g, ya, sill + RAIL), (x1 - g, yb, sill + RAIL), (x1 - g, yb, head - RAIL), (x1 - g, ya, head - RAIL), facing=(1, 0, 0))
    for y in (yc - .65, yc + .65):
        clay.box('frame', x1 - n1, x1 - n0, y - .03, y + .03, sill + RAIL, head - RAIL)


def build():
    clay = Clay()
    ground_floor(clay)
    envelope(clay)
    offices(clay)
    lobby(clay)
    penthouse(clay)
    bridge(clay)
    return clay


# ---- records -------------------------------------------------------------------------------
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


CAMERAS = ('front', 'front_corner', 'aerial', 'top', 'left_side', 'right_side', 'rear', 'rear_side', 'facade_close',
           'architecture_close', 'glass_close', 'roof_contact', 'bridge_contact', 'entrance_contact', 'rear_ground', 'west_ground',
           'bridge_junction', 'bridge_end', 'corner_close', 'service_close', 'match_front', 'match_oblique', 'match_top')


def prework(candidate):
    """The measured contract this candidate is built to. Written before the first review."""
    return {
        'candidate': candidate, 'title': TITLE, 'method': METHOD, 'representation_kind': 'architectural_clay',
        'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'state': 'prework', 'keeper_claimed': False, 'runtime_seed_allowed': False,
        'sources': source_lock(),
        'measurement_contract': {
            'dimensions_m': {'width': W, 'depth': D, 'parapet': PARAPET, 'penthouse_top': PENT_TOP, 'walkway_projection': BRIDGE_LENGTH},
            'storeys': STOREYS, 'storey_policy': 'fixed_authored_assembly',
            'source_measurements': {
                'front': [
                    'A two-point street view from the south-east corner with upright verticals. A fitted camera (2.4 m eye height, 40 degree lens, vertical shift) puts six measured corners within 10 px on the 1024 px image.',
                    'Down the south-east corner edge: 230 px of clear ground storey, four pairs of 108 px ribbon and 107 px band, and a 115 px top band. At the variant\'s 3.9 m storey this gives a clear ground storey of about 4.1 m, ribbons and bands that each read 1.95 m, and a top band of about 2.0 to 2.1 m. The parapet is built at 21.8 m.',
                    'From the street each sill hides about 0.1 m of its window, and from above each band hides more. Both views agree when the openings are 2.05 m tall in 1.85 m bands with the glass 0.3 m behind the cap strip, so that is what is built.',
                    'Ground storey plus four office storeys: five. The catalogue text says six; the selected-variant images govern.',
                    'Five structural bays across the street front, marked by band joints and granite piers about 1.3 m wide, with six window modules to a bay.',
                    'Each band carries a cap strip about 0.5 m tall that projects beyond the main face over a dark line about 0.2 m deep. Built as a 0.15 m projection over a recessed reveal 0.16 m tall. The first band also carries a lower moulding.',
                    'One pair of glazed entrance doors in the second bay from the east corner, with a transom at door-head height. Timber panelling shows through the corner bay.',
                    'East flank at street level: the glazing returns a short way, then blank granite between piers, with a service door at the far end.',
                    'The walkway leaves the east flank at the third storey. Its glazed band is a little taller than the office ribbons and close to half the height of the tube, between a concrete crown and belly with rounded edges.'],
                'oblique': [
                    'A fitted camera (37 m up to the south-east, 48 degree lens) puts eight measured points, including the corner pier\'s foot, within 18 px on the 1195 px image. It is a looser fit than the street view, and worst at the west end of the street front, where the model\'s lowest ribbon sits about 35 px high. This image settles the roof layout and not facade heights.',
                    'Four ribbon storeys over the ground storey on both visible sides, with band joints at the structural lines.',
                    'Penthouse about 6.8 m tall in board-formed panels, eight to a face, with one horizontal joint; a door and a louvre on its east face; an open well in its rear east corner.',
                    'Flat gravel roof inside a concrete parapet with a bronze flashing on its inner edge.'],
                'top': [
                    'Footprint 670 px by 615 px, a ratio of 1.09. Built 45.0 m by 40.5 m, a ratio of 1.11.',
                    'Penthouse 337 px by 343 px, centred, about 9 m from every parapet. Built 22.5 m square, centred.',
                    'Open well about 8 m square in the penthouse\'s rear east corner holding one square unit.',
                    'Walkway 4.4 m wide on the east flank, centred about 29 percent of the depth back from the street corner. Built 4.5 m wide on the window module, centred 11.25 m back.',
                    'Roof items: one hatch south of the penthouse, one vent to its east, one unit and two conduit runs on its roof.'],
            },
            'source_conflicts': [
                'Walkway level. The archetype text places +15 walkways at the second storey; both perspective sources show this one at the third. Built as drawn, floor 9.1 m above grade.',
                'Penthouse from the street. The street view shows about 6 m of penthouse above the parapet line, so its skyline is stepped. The roof plan and the oblique cannot produce that from the fitted street camera; under 1 m shows and the skyline is nearly flat. Roof plan and oblique govern.',
                'Penthouse size in the oblique. Fitted to the building\'s corners, the oblique shows the penthouse about 7 percent narrower than the roof plan does, and the model\'s penthouse renders somewhat larger than the reference there. The roof plan governs the plan, 22.5 m square; the height, 6.8 m, comes from the penthouse\'s own corner edge in the oblique.',
                'Walkway roof. The street view shows a rounded crown; the oblique shows a flat roof with eased edges. Built flat with 0.35 m eased edges, which is consistent with both.',
                'Storey count. The catalogue description says six storeys; both perspective sources show five.'],
            'hidden_assumptions': [
                'The west flank and the rear are not shown. The west flank mirrors the east at street level, with plant louvres and an exit door. The rear is a service side with high windows, a loading door and a staff exit. The ribbon bands repeat on all four sides above.',
                'Interior layout, floor levels behind the bands and the structural grid are inferred from the facade rhythm.',
                'The walkway runs on to a neighbouring building in the sources. It is delivered as a 9 m length with a glazed end, no neighbour and no support at the free end.',
                'The penthouse\'s rear and west faces are plain board-formed panels.',
                'The penthouse well is taken to be open down to the main roof deck, holding one cooling unit.',
                'Corner rooms with dark blinds drawn stand in each corner of every office storey. No reference shows them; they stop sight lines running clean through the corner panes.'],
        },
        'roof_contract': {'form': 'flat ballasted roof inside a 1.0 m parapet', 'penthouse': 'centred concrete plant room with an open well',
                          'weathering': 'closed deck, parapet and penthouse walls; no floating plant'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()}},
        'identity_contract': ['five storeys', 'four ribbon and band pairs on every side', 'projecting cap strip on every band', 'granite piers at 9 m',
                              'one street entrance in the second bay from the east corner', 'third-storey walkway on the east flank',
                              'centred penthouse with a rear east well'],
        'programme_contract': {'ground': 'three shop units and an office lobby to the street; service rooms to the flank and rear',
                               'upper': 'open office around a core of enclosed rooms, four storeys', 'public_entrances': 1},
        'contact_contract': {'base_datum_m': 0.0, 'lowest_geometry_m': 0.0, 'threshold_rise_m': round(BASE + .015, 3),
                             'ground': 'a 20 mm apron inside the footprint only; no display slab, street or planting in the model'},
        'camera_roster': list(CAMERAS),
        'mandatory_review_views': ['front.png', 'front_corner.png', 'aerial.png', 'left_side.png', 'right_side.png', 'rear.png', 'rear_side.png',
                                   'facade_close.png', 'architecture_close.png', 'glass_close.png', 'roof_contact.png', 'bridge_contact.png',
                                   'entrance_contact.png'],
    }


def entrance():
    """The one public entrance, measured from the model's own numbers (authoring frame)."""
    a, b = bays(FRONT)[3]
    width = (b - a) / 6
    x0, _, _ = FRONT.p(a + 2 * width, 0, 0)
    x1, y, _ = FRONT.p(a + 4 * width, SHOP_GLASS, 0)
    return {'kind': 'public', 'storey': 1, 'facade': 'front', 'centre_xy_m': [round((x0 + x1) / 2, 3), round(y, 3)],
            'clear_width_m': round(x1 - x0 - .24, 3), 'door_height_m': round(TRANSOM - BASE, 3), 'threshold_top_m': round(BASE + .015, 3),
            'outer_step_foot_m': 0.0, 'rise_m': round(BASE + .015, 3), 'route_direction': [0, -1],
            'frame': 'authoring Z-up, x east, front faces -y, grade z = 0, building body centred on the origin'}


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
        'sources': source_lock(),
        'model': {'file': model.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'meshes': len(counts), 'materials': len(counts), 'textures': 0, 'images': 0,
                  'triangles': sum(counts.values()), 'triangles_by_role': counts},
        'native_dimensions_m': {'width': round(hi[0] - lo[0], 4), 'depth': round(hi[1] - lo[1], 4), 'height': round(hi[2] - lo[2], 4)},
        'authoring_bounds_m': {'min': [round(v, 4) for v in lo], 'max': [round(v, 4) for v in hi]},
        'design_dimensions_m': {'width': W, 'depth': D, 'height': PENT_TOP},
        'storeys': STOREYS, 'floor_levels_m': list(FLOORS), 'roof_m': ROOF, 'parapet_m': PARAPET, 'penthouse_top_m': PENT_TOP,
        'bridge': {'storey': BRIDGE_STOREY, 'floor_m': FLOORS[BRIDGE_STOREY - 1], 'projection_m': BRIDGE_LENGTH, 'width_m': 2 * BRIDGE_HALF},
        'entrances': [entrance()],
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('candidate', 'native_dimensions_m')} | {'triangles': report['model']['triangles'],
                                                                                    'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
