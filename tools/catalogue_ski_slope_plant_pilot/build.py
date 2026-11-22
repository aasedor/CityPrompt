"""Build the Ski Slope waste-to-energy plant as an RLASM 6.1 architectural-clay GLB.

Exact variant: `waste_to_energy_plant` / `wte_ski_slope` (variant 0). The locked oblique and roof views
show a long block clad in aluminium bricks whose roof is one green turf slope, stepped paths
down both sides and a terraced summit with a pavilion. The east face has tall slot windows and a
climbing wall on a pier; lower green-roofed wings wrap the south half; a twin-flue stack rises from
the west wing. The catalogue's street view of this variant is a grey render of the old LEGO model,
not a picture of the building, so it is recorded as a source conflict and not used.

    python3 tools/catalogue_ski_slope_plant_pilot/build.py --output <new directory> --version <n>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, renders and
boards are review material and stay outside Git until a person activates them.

Geometry is authored in the roof view's plan frame (x east, y north, z up, metres, grade z = 0,
the main block centred on the origin) and turned a quarter turn at the end, so that in the
delivered authoring frame the east face, with the visitor entrance and the climbing wall, is
the street front facing -y and the slope descends toward -x.
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
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'catalogue_plus15_concrete_pilot'))
from clay_kit import METHOD, Clay

SLUG = 'wte-ski-slope'
ARCHETYPE, VARIANT, INDEX = 'waste_to_energy_plant', 'wte_ski_slope', 0
TITLE = 'Ski Slope WtE'
SOURCE_DIR = 'frontend/public/archetypes/buildings/waste_to_energy_plant'
SOURCES = {'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}
EXCLUDED = {'front': f'variant_{INDEX}.png'}     # a grey render of the old LEGO model; see source_conflicts

# ---- measured contract (plan frame, metres) -------------------------------------------------------
PX = .204                                         # roof view scale: the main block is 294 by 780 px for 60 by 159 m
HALF_W, HALF_L, CORNER = 30.0, 79.5, 6.5          # main block half-width (x), half-length (y) and plan corner radius
HS, H0, HP = 80.2, 39.5, 29.8                     # summit parapet, low-end parapet and wing roof heights (camera fit)
Y_LOW = -HALF_L + CORNER                          # the parapet starts to climb where the low end's corners end
SLOPE = (HS - H0) / (HALF_L - Y_LOW)              # one straight parapet line from the low end to the summit
WALK = .3                                         # walking surfaces sit this far below the parapet's coping
GUARD = 1.1                                       # glass guard on the coping beside the slope
TURF_X, STAIR_X, INNER = 24.4, 28.8, 29.4         # half-widths: the turf, the stepped paths, and the parapet's inside face
STAIR_Y = (-66.0, 31.0)                           # the stepped paths beside the turf
RISE = .18                                        # riser of every stair
TERRACE_Y = (31.0, 46.9)                          # lower summit terrace; the upper terrace runs from its north edge to the summit wall
BAR = (-17.1, 18.6, 6.0)                          # glazed bar under the upper terrace: x range and depth
UPPER_STEP = 4.1                                  # the upper terrace stands this far above the lower one
PAVILION = (-24.7, 18.2, 60.5, 76.3, 5.0)         # rooftop pavilion on the upper terrace: x range, y range, height
PLANT = (18.2, 27.1, 61.0, 71.4, 3.5)             # plant enclosure beside it
PIER = (30.0, 35.3, 16.3, 45.3, 2.5)              # climbing-wall pier on the east face: x, y, and its rise above the parapet line
ENTRANCE = (65.0, 71.0, 5.0)                      # visitor entrance in the east face: y range and height
LOADING = [(-16.0, -9.0), (-4.0, 3.0)]            # roller doors in the north face (x ranges), 9 m high
SERVICE = [(-15.6, -11.8), (-6.4, -2.6)]          # service doors from the wing roof into the low end (x ranges), 4.4 m high
WINGS = [(-47.7, -95.5, -HALF_W, -.6), (-47.7, -95.5, 55.3, -HALF_L), (HALF_W, -95.5, 55.3, -19.0),   # x0, y0, x1, y1
         (-41.8, -.6, -HALF_W, 47.3)]          # the west wing narrows to a strip running north beside the block
WING_CORNER = 5.0
STACK = ((-38.2, -46.5), 100.0, (3.6, 2.8), (1.9, 1.1), 100.0, (3.0, 2.2))  # main flue centre, top, radii; second flue offset, top, radii
TWIST = 110.0                                     # the second flue winds this far round the first, in degrees, base to top
SLOT = (1.4, 3.7, 1.6)                            # slot windows: width, column spacing, gap between stacked slots
COURSE = 1.25                                     # aluminium brick courses
SLOT_ROOM = 1.4                                   # lit room face behind each slot window, from the outer face
UNDER_FLOOR = 1.2                                 # slot windows stop this far below the roof's walking surface above them
PAD = (35.3, 43.3, 16.3, 45.3)                    # turf pad at the foot of the climbing wall: x and y range
APRON = 4.0

PALETTE = {  # role -> flat colour (sRGB), in node order
    'apron': {'colour': '#a8a59c', 'module': 'site'},
    'cladding': {'colour': '#b7babd', 'module': 'aluminium brick facade', 'roughness': .55},
    'joint': {'colour': '#8d9195', 'module': 'aluminium brick facade', 'roughness': .6},
    'coping': {'colour': '#e4e4df', 'module': 'roof edges', 'roughness': .5},
    'reveal': {'colour': '#7a7e83', 'module': 'slot windows'},
    'mullion': {'colour': '#55595e', 'module': 'slot windows', 'roughness': .5},
    'light': {'colour': '#f0c26a', 'module': 'interior glow'},
    'interior': {'colour': '#c8a87c', 'module': 'interiors'},
    'door': {'colour': '#4a4f55', 'module': 'doors'},
    'turf': {'colour': '#3d8a2b', 'module': 'ski slope'},
    'turf_light': {'colour': '#48962f', 'module': 'ski slope'},
    'stair': {'colour': '#9fa3a6', 'module': 'stepped paths'},
    'gravel': {'colour': '#a49f94', 'module': 'roof edges'},
    'terrace': {'colour': '#c9c4b8', 'module': 'summit terraces'},
    'furniture': {'colour': '#4b4540', 'module': 'summit terraces'},
    'pavilion': {'colour': '#d2d3d0', 'module': 'summit pavilion'},
    'grille': {'colour': '#3c4045', 'module': 'plant'},
    'roof_dark': {'colour': '#5d6267', 'module': 'summit pavilion'},
    'roofgreen': {'colour': '#6c7b42', 'module': 'wing roofs'},
    'planting': {'colour': '#7a8a46', 'module': 'wing roofs'},
    'meadow': {'colour': '#a39a5f', 'module': 'wing roofs'},
    'blossom': {'colour': '#dcd6c4', 'module': 'wing roofs'},
    'climb': {'colour': '#d9d7cf', 'module': 'climbing wall'},
    'hold_blue': {'colour': '#2f6fc4', 'module': 'climbing wall'},
    'hold_red': {'colour': '#c8402e', 'module': 'climbing wall'},
    'hold_yellow': {'colour': '#e3c234', 'module': 'climbing wall'},
    'hold_green': {'colour': '#3f9a4a', 'module': 'climbing wall'},
    'stack': {'colour': '#cbccc8', 'module': 'stack', 'roughness': .6},
    'flue': {'colour': '#2c2b29', 'module': 'stack'},
    'glass': {'colour': '#2a2620', 'module': 'glazing', 'alpha': .32, 'roughness': .2, 'transmission': .3},
    'guard': {'colour': '#d0dade', 'module': 'glass guards', 'alpha': .25, 'roughness': .15},
}


# ---- heights ---------------------------------------------------------------------------------------
def parapet(y):
    """Top of the coping along the long faces: flat over the low end, then one straight climb to the summit."""
    return min(HS, H0 + SLOPE * max(0.0, y - Y_LOW))


def walk(y):
    """The slope's walking surface: the turf, the stepped paths and the edge strips."""
    return parapet(y) - WALK


Z_LOWER = walk(TERRACE_Y[0])
Z_UPPER = Z_LOWER + UPPER_STEP


def floor_at(y):
    """The roof's walking surface at plan y: the slope, then the lower and upper summit terraces."""
    if y >= TERRACE_Y[1]:
        return Z_UPPER
    if y >= TERRACE_Y[0]:
        return Z_LOWER
    return walk(y)


def under_roof(y, half=1.0):
    """Highest a slot window may reach at plan y: below the lowest walking surface within `half` metres."""
    return min(floor_at(y - half), floor_at(y), floor_at(y + half)) - UNDER_FLOOR


# ---- helpers ---------------------------------------------------------------------------------------
def plan_normal(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy) or 1.0
    return dy / length, -dx / length


def wall(clay, role, p, q, z0, z1, facing):
    """A vertical quad on the plan segment p-q from z0 to z1; `facing` may be a plan vector."""
    if z1 - z0 > 1e-4:
        clay.quad(role, (p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1), (p[0], p[1], z1), facing=(*facing[:2], 0))


def obox(clay, role, cx, cy, ux, uy, half_u, half_v, z0, z1):
    """A vertical box whose plan is a rectangle with axis u = (ux, uy) and its perpendicular."""
    vx, vy = -uy, ux
    corners = [(cx + su * half_u * ux + sv * half_v * vx, cy + su * half_u * uy + sv * half_v * vy) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    clay.prism(role, corners, z0, z1)


def flat_region(clay, role, geometry, z, up=True):
    """Triangulate a shapely polygon (holes allowed) as a horizontal surface at height z."""
    surface(clay, role, geometry, lambda x, y: z, up)


def surface(clay, role, geometry, height, up=True):
    """Triangulate a shapely polygon and lift each vertex to height(x, y); planar when height is linear."""
    for poly in getattr(geometry, 'geoms', [geometry]):
        if poly.is_empty or poly.geom_type != 'Polygon' or poly.area < 1e-6:
            continue
        rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
        verts = np.array([p for r in rings for p in r], dtype=np.float64)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        idx = mapbox_earcut.triangulate_float64(verts, ends)
        for k in range(0, len(idx), 3):
            a, b, c = (tuple(verts[i]) + (height(*verts[i]),) for i in idx[k:k + 3])
            clay.tri(role, a, b, c, facing=(0, 0, 1 if up else -1))


def rounded(x0, y0, x1, y1, r):
    return orient(box(x0, y0, x1, y1).buffer(-r, quad_segs=8).buffer(r, quad_segs=8), 1.0)


def main_block():
    return rounded(-HALF_W, -HALF_L, HALF_W, HALF_L, CORNER)


def footprint():
    """The whole building at grade: the main block and its wings, convex corners rounded."""
    parts = [box(-HALF_W, -HALF_L, HALF_W, HALF_L)] + [box(*w) for w in WINGS]
    whole = shapely.union_all(parts).buffer(-WING_CORNER, quad_segs=8).buffer(WING_CORNER, quad_segs=8)
    slivers = box(-HALF_W, 0.0, HALF_W, HALF_L).difference(main_block())     # the block's own corner radius where it meets the ground
    return orient(whole.difference(slivers), 1.0)


# ---- facades with real openings --------------------------------------------------------------------
class Face:
    """A planar vertical facade: origin (x, y), unit plan direction u, outward plan normal n, and an outline in (u, z)."""

    def __init__(self, origin, u, outline):
        self.o, self.u, self.outline = origin, u, outline
        self.n = (u[1], -u[0])

    def at(self, s, z, depth=0.0):
        return (self.o[0] + s * self.u[0] - depth * self.n[0], self.o[1] + s * self.u[1] - depth * self.n[1], z)


def build_face(clay, face, openings, role='cladding', courses=True):
    """The wall with every opening cut, each opening's reveals, its glass or door, and what lies behind it."""
    outline = Polygon(face.outline)
    holes = [box(o['u'][0], o['z'][0], o['u'][1], o['z'][1]) for o in openings]
    solid = outline.difference(shapely.union_all(holes)) if holes else outline
    normal = (*face.n, 0)
    for poly in getattr(solid, 'geoms', [solid]):
        rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
        verts = np.array([p for r in rings for p in r], dtype=np.float64)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        idx = mapbox_earcut.triangulate_float64(verts, ends)
        for k in range(0, len(idx), 3):
            a, b, c = (face.at(*verts[i]) for i in idx[k:k + 3])
            clay.tri(role, a, b, c, facing=normal)
    for o in openings:
        (u0, u1), (z0, z1) = o['u'], o['z']
        kind = o.get('kind', 'slot')
        depth = o.get('depth', SLOT_ROOM if kind == 'slot' else .35)
        reveal = 'reveal'
        corners = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
        for (ua, za), (ub, zb) in pairwise(corners + corners[:1]):          # reveals, facing into the opening
            inward = ((ua + ub) / 2 - (u0 + u1) / 2, (za + zb) / 2 - (z0 + z1) / 2)
            d = (-(face.u[0] * inward[0]), -(face.u[1] * inward[0]), -inward[1])
            clay.quad(reveal, face.at(ua, za), face.at(ub, zb), face.at(ub, zb, depth), face.at(ua, za, depth), facing=d)
        back = 'light' if kind in ('slot', 'entrance') else 'door'
        clay.quad(back, face.at(u0, z0, depth), face.at(u1, z0, depth), face.at(u1, z1, depth), face.at(u0, z1, depth), facing=normal)
        if kind == 'slot':
            clay.quad('glass', face.at(u0, z0, .25), face.at(u1, z0, .25), face.at(u1, z1, .25), face.at(u0, z1, .25), facing=normal)
            z = z0 + 2.6
            while z < z1 - .8:                                                 # glazing bars about every 2.6 m
                bar_box(clay, face, (u0, u1), (z - .05, z + .05), .2, .3)
                z += 2.6
        elif kind == 'entrance':
            clay.quad('door', face.at(u0, z0, .3), face.at(u1, z0, .3), face.at(u1, z0 + 2.9, .3), face.at(u0, z0 + 2.9, .3), facing=normal)
            clay.quad('glass', face.at(u0, z0 + 3.05, .3), face.at(u1, z0 + 3.05, .3), face.at(u1, z1, .3), face.at(u0, z1, .3), facing=normal)
            bar_box(clay, face, (u0, u1), (z0 + 2.9, z0 + 3.05), .25, .35)
            s = u0
            while s <= u1 + 1e-6:
                bar_box(clay, face, (s - .05, s + .05), (z0, z1), .25, .35)
                s += (u1 - u0) / 4
    if courses:
        course_lines(clay, face, solid)


def bar_box(clay, face, us, zs, d0, d1):
    """A thin member between depths d0 and d1 behind the face plane."""
    (u0, u1), (z0, z1) = us, zs
    ring = [face.at(u0, 0, d0)[:2], face.at(u1, 0, d0)[:2], face.at(u1, 0, d1)[:2], face.at(u0, 0, d1)[:2]]
    clay.prism('mullion', ring, z0, z1)


def course_lines(clay, face, solid):
    """Aluminium brick courses: thin proud strips every COURSE metres, stopping at each opening."""
    lo, hi = solid.bounds[1], solid.bounds[3]
    z = lo + COURSE
    normal = (*face.n, 0)
    while z < hi - .1:
        line = LineString([(solid.bounds[0] - 1, z), (solid.bounds[2] + 1, z)]).intersection(solid.buffer(-.05))
        for seg in getattr(line, 'geoms', [line]):
            if seg.is_empty or seg.length < .3 or seg.geom_type != 'LineString':
                continue
            (ua, _), (ub, _) = seg.coords[0], seg.coords[-1]
            clay.quad('joint', face.at(ua, z - .03, -.012), face.at(ub, z - .03, -.012), face.at(ub, z + .03, -.012), face.at(ua, z + .03, -.012),
                      facing=normal)
        z += COURSE


def slot_columns(u_range, base, top, skip=(), seed=0, limit=None):
    """Tall slot windows in staggered columns: each column a stack of slots of varied height."""
    width, spacing, gap = SLOT
    out = []
    u = u_range[0]
    k = seed
    while u <= u_range[1]:
        if not any(a - width <= u <= b + width for a, b in skip):
            z_lo, z_hi = base(u) + (8.0 if base(u) < 1 else 2.0), top(u) - (4.5 if base(u) < 1 else 2.2)
            if limit is not None:
                z_hi = min(z_hi, limit(u))
            z = z_lo + (k * 2.3) % 4.0
            j = k
            while z + 2.4 < z_hi:
                h = min((8.0, 5.5, 10.5)[j % 3], z_hi - z)
                if h >= 2.4:
                    out.append({'u': (u - width / 2, u + width / 2), 'z': (z, z + h)})
                z += h + gap
                j += 1
        u += spacing
        k += 1
    return out


# ---- the main block --------------------------------------------------------------------------------
def east_base(y):
    return HP if y < WINGS[2][3] else 0.0


def west_base(y):
    return HP if y < WINGS[3][3] else 0.0


def main_facades(clay):
    s0, s1 = -HALF_L + CORNER, HALF_L - CORNER                         # straight run of the long faces
    w0, w1 = -HALF_W + CORNER, HALF_W - CORNER
    # east face (u = y, northward): the street front
    east = Face((HALF_W, 0.0), (0.0, 1.0), [(s0, HP), (WINGS[2][3], HP), (WINGS[2][3], 0.0), (s1, 0.0), (s1, parapet(s1)), (s0, parapet(s0))])
    openings = slot_columns((s0 + 3.0, s1 - 3.0), east_base, parapet, skip=[(PIER[2] - 1.0, PIER[3] + 1.0), (ENTRANCE[0] - 1.5, ENTRANCE[1] + 1.5),
                                                                           (WINGS[2][3] - 2.0, WINGS[2][3] + 2.0)], seed=1, limit=under_roof)
    openings.append({'u': ENTRANCE[:2], 'z': (0.0, ENTRANCE[2]), 'kind': 'entrance', 'depth': 4.0})
    build_face(clay, east, openings)
    # west face (u = -y, southward)
    west = Face((-HALF_W, 0.0), (0.0, -1.0), [(-s1, 0.0), (-WINGS[3][3], 0.0), (-WINGS[3][3], HP), (-s0, HP), (-s0, parapet(s0)), (-s1, parapet(s1))])
    build_face(clay, west, slot_columns((-s1 + 3.0, -s0 - 3.0), lambda u: west_base(-u), lambda u: parapet(-u),
                                        skip=[(-WINGS[3][3] - 2.0, -WINGS[3][3] + 2.0)], seed=4, limit=lambda u: under_roof(-u)))
    # north face (u = -x, westward): roller doors at grade, slots above
    north = Face((0.0, HALF_L), (-1.0, 0.0), [(-w1, 0.0), (-w0, 0.0), (-w0, HS), (-w1, HS)])
    doors = [{'u': (-b, -a), 'z': (0.0, 9.0), 'kind': 'door', 'depth': .4} for a, b in LOADING]
    for a, b in LOADING:                                                   # slats of the roller doors
        z = .45
        while z < 9.0:
            bar_box(clay, north, (-b, -a), (z - .03, z + .03), .34, .4)
            z += .45
    slots = [s for s in slot_columns((-w1 + 2.5, -w0 - 2.5), lambda u: 0.0, lambda u: HS, seed=2, limit=lambda u: Z_UPPER - UNDER_FLOOR)
             if s['z'][0] > 12.0]
    build_face(clay, north, doors + slots)
    # south face (u = x, eastward): the low end above the wing roof, with two service doors
    south = Face((0.0, -HALF_L), (1.0, 0.0), [(w0, HP), (w1, HP), (w1, H0), (w0, H0)])
    build_face(clay, south, [{'u': d, 'z': (HP, HP + 4.4), 'kind': 'door', 'depth': .35} for d in SERVICE])
    # the four rounded corners, faceted
    for (cx, cy), a0, base, in (((w1, s1), 0, 0.0), ((w0, s1), 90, 0.0), ((w0, s0), 180, HP), ((w1, s0), 270, HP)):
        ts = np.linspace(math.radians(a0), math.radians(a0 + 90), 9)
        pts = [(cx + CORNER * math.cos(t), cy + CORNER * math.sin(t)) for t in ts]
        for p, q in pairwise(pts):
            n = plan_normal(p, q)
            top_p, top_q = parapet(p[1]), parapet(q[1])
            if cy > 0:
                top_p, top_q = min(top_p, HS), min(top_q, HS)
            else:
                top_p = top_q = H0
            clay.quad('cladding', (*p, base), (*q, base), (*q, top_q), (*p, top_p), facing=(*n, 0))
            z = base + COURSE
            while z < min(top_p, top_q) - .1:
                o = (n[0] * .012, n[1] * .012)
                clay.quad('joint', (p[0] + o[0], p[1] + o[1], z - .03), (q[0] + o[0], q[1] + o[1], z - .03),
                          (q[0] + o[0], q[1] + o[1], z + .03), (p[0] + o[0], p[1] + o[1], z + .03), facing=(*n, 0))
                z += COURSE
    # the visitor entrance's canopy and lit sign
    obox(clay, 'coping', HALF_W + 1.25, sum(ENTRANCE[:2]) / 2, 0.0, 1.0, (ENTRANCE[1] - ENTRANCE[0]) / 2 + 1.0, 1.25, ENTRANCE[2] + .2, ENTRANCE[2] + .45)
    obox(clay, 'light', HALF_W + .06, sum(ENTRANCE[:2]) / 2, 0.0, 1.0, 2.2, .04, ENTRANCE[2] + 1.0, ENTRANCE[2] + 2.0)
    return openings


def pier(clay):
    """The climbing-wall pier: a solid fin standing proud of the east face, its top following the parapet."""
    x0, x1, y0, y1, rise = PIER

    def top(y):
        return parapet(y) + rise
    face = Face((x1, 0.0), (0.0, 1.0), [(y0, 0.0), (y1, 0.0), (y1, top(y1)), (y0, top(y0))])
    build_face(clay, face, [], role='climb', courses=False)
    for y, sign in ((y0, -1), (y1, 1)):
        side = Face((0.0, y), (-sign * 1.0, 0.0), [(-sign * x0 if sign < 0 else -x1, 0.0), (-sign * x1 if sign < 0 else -x0, 0.0),
                                                     (-sign * x1 if sign < 0 else -x0, top(y)), (-sign * x0 if sign < 0 else -x1, top(y))])
        build_face(clay, side, [])
    clay.quad('coping', (x0, y0, top(y0)), (x1, y0, top(y0)), (x1, y1, top(y1)), (x0, y1, top(y1)), facing=(0, 0, 1))
    clay.quad('cladding', (x0, y0, parapet(y0)), (x0, y1, parapet(y1)), (x0, y1, top(y1)), (x0, y0, top(y0)), facing=(-1, 0, 0))   # back, above the parapet
    flat_region(clay, 'turf', box(PAD[0], PAD[2], PAD[1], PAD[3]), .04)
    rng = np.random.default_rng(1601)
    colours = ['hold_blue', 'hold_red', 'hold_yellow', 'hold_green']
    for _ in range(26):                                                    # large volumes
        y, z = rng.uniform(y0 + 2, y1 - 2), rng.uniform(1.5, top(y0) - 4)
        size = rng.uniform(1.0, 2.6)
        sides = int(rng.integers(3, 6))
        ring = [(x1 + .03, y + size * math.cos(2 * math.pi * k / sides + .4), z + size * 1.3 * math.sin(2 * math.pi * k / sides + .4)) for k in range(sides)]
        apex = (x1 + size * .35, y, z)
        role = 'hold_blue' if rng.random() < .55 else 'hold_yellow'
        for a, b in pairwise(ring + ring[:1]):
            clay.tri(role, a, b, apex, facing=(1, 0, 0))
    for _ in range(240):                                                   # holds
        y, z = rng.uniform(y0 + .6, y1 - .6), rng.uniform(.4, top(y0) - 1.0)
        s = rng.uniform(.15, .35)
        clay.box(colours[int(rng.integers(0, 4))], x1 + .03, x1 + .03 + s * .8, y - s, y + s, z - s, z + s)


# ---- the roof: turf, stepped paths, terraces and summit --------------------------------------------
def stair_flight(clay, x0, x1, y0, y1, z0, z1, floor=None, sides=None):
    """A straight flight between plan y0 and y1 from z0 to z1, as solid steps standing on the plane between;
    with `floor`, the flight stands on a level floor and its sides are closed down to it."""
    count = max(1, round((z1 - z0) / RISE))
    run, rise = (y1 - y0) / count, (z1 - z0) / count
    for k in range(count):
        ya, yb = y0 + run * k, y0 + run * (k + 1)
        za, zb = z0 + rise * k, z0 + rise * (k + 1)
        clay.quad('stair', (x0, ya, za), (x1, ya, za), (x1, ya, zb), (x0, ya, zb), facing=(0, -1, 0))
        clay.quad('stair', (x0, ya, zb), (x1, ya, zb), (x1, yb, zb), (x0, yb, zb), facing=(0, 0, 1))
        for x in sides or (x0, x1):                                        # step sides above the sloping plane
            clay.tri('stair', (x, ya, za), (x, ya, zb), (x, yb, zb), facing=(1 if x == max(x0, x1) else -1, 0, 0))
    if floor is not None:
        for x in sides or (x0, x1):
            clay.tri('stair', (x, y0, floor), (x, y1, floor), (x, y1, z1), facing=(1 if x == max(x0, x1) else -1, 0, 0))


def roof(clay):
    inner = orient(main_block().buffer(-(HALF_W - INNER), quad_segs=8), 1.0)   # inside face of the parapet
    slope_zone = inner.intersection(box(-50, -100, 50, TERRACE_Y[0]))
    stairs = [box(TURF_X, STAIR_Y[0], STAIR_X, STAIR_Y[1]), box(-STAIR_X, STAIR_Y[0], -TURF_X, STAIR_Y[1])]
    edges = [box(STAIR_X, STAIR_Y[0], INNER + 1, TERRACE_Y[1]), box(-INNER - 1, STAIR_Y[0], -STAIR_X, TERRACE_Y[1])]
    turf = slope_zone.difference(shapely.union_all(stairs + edges))
    flat = turf.intersection(box(-50, -100, 50, Y_LOW))
    bands = [box(-TURF_X + 6.1 * k, -100, -TURF_X + 6.1 * (k + 1), 100) for k in range(8)]
    for k, band in enumerate(bands):                                       # groomed stripes down the slope
        role = 'turf' if k % 2 == 0 else 'turf_light'
        surface(clay, role, flat.intersection(band), lambda x, y: walk(Y_LOW))
        surface(clay, role, turf.difference(flat).intersection(band), lambda x, y: walk(y))
    rest = turf.difference(shapely.union_all(bands))
    surface(clay, 'turf', rest.intersection(flat), lambda x, y: walk(Y_LOW))
    surface(clay, 'turf', rest.difference(flat), lambda x, y: walk(y))
    for side in (1, -1):                                                   # the stepped paths, and their edge strips
        xa, xb = sorted((side * TURF_X, side * STAIR_X))
        stair_flight(clay, xa, xb, STAIR_Y[0], STAIR_Y[1], walk(STAIR_Y[0]), walk(STAIR_Y[1]))
        strip = inner.intersection(box(min(side * STAIR_X, side * (INNER + 1)), STAIR_Y[0], max(side * STAIR_X, side * (INNER + 1)), TERRACE_Y[0]))
        surface(clay, 'gravel', strip, lambda x, y: walk(y))
        xa, xb = sorted((side * TURF_X, side * STAIR_X))
        xa, xb = sorted((side * TURF_X, side * INNER))                     # summit flights run to the parapet; guarded on the open side
        stair_flight(clay, xa, xb, TERRACE_Y[0], TERRACE_Y[1], Z_LOWER, Z_UPPER, floor=Z_LOWER, sides=(side * TURF_X,))
        x = side * TURF_X
        clay.quad('guard', (x, TERRACE_Y[0], Z_LOWER), (x, TERRACE_Y[1], Z_UPPER), (x, TERRACE_Y[1], Z_UPPER + GUARD),
                  (x, TERRACE_Y[0], Z_LOWER + GUARD), facing=(-side, 0, 0))
        clay.quad('mullion', (x, TERRACE_Y[0], Z_LOWER + GUARD), (x, TERRACE_Y[1], Z_UPPER + GUARD), (x, TERRACE_Y[1], Z_UPPER + GUARD + .05),
                  (x, TERRACE_Y[0], Z_LOWER + GUARD + .05), facing=(-side, 0, 0))
    # lower terrace between the flights, the bar under the upper terrace, and the upper terrace
    flat_region(clay, 'terrace', box(-TURF_X, TERRACE_Y[0], TURF_X, TERRACE_Y[1]), Z_LOWER)
    bx0, bx1, depth = BAR
    yf = TERRACE_Y[1]
    for (a, b) in ((-TURF_X, bx0), (bx1, TURF_X)):
        wall(clay, 'cladding', (a, yf), (b, yf), Z_LOWER, Z_UPPER, (0, -1))
    clay.quad('glass', (bx0, yf, Z_LOWER), (bx1, yf, Z_LOWER), (bx1, yf, Z_UPPER - .3), (bx0, yf, Z_UPPER - .3), facing=(0, -1, 0))
    wall(clay, 'cladding', (bx0, yf), (bx1, yf), Z_UPPER - .3, Z_UPPER, (0, -1))
    x = bx0
    while x <= bx1 + 1e-6:
        obox(clay, 'mullion', x, yf - .05, 1.0, 0.0, .05, .08, Z_LOWER, Z_UPPER - .3)
        x += (bx1 - bx0) / 12
    flat_region(clay, 'interior', box(bx0, yf, bx1, yf + depth), Z_LOWER + .01)
    flat_region(clay, 'light', box(bx0, yf, bx1, yf + depth), Z_UPPER - .3, up=False)
    wall(clay, 'interior', (bx0, yf + depth), (bx1, yf + depth), Z_LOWER, Z_UPPER - .3, (0, -1))
    for xx, s in ((bx0, 1), (bx1, -1)):
        wall(clay, 'interior', (xx, yf), (xx, yf + depth), Z_LOWER, Z_UPPER - .3, (s, 0))
    clay.box('furniture', bx0 + 3, bx1 - 3, yf + depth - 2.2, yf + depth - 1.2, Z_LOWER, Z_LOWER + 1.1)
    upper = inner.intersection(box(-50, yf, 50, 100))
    flat_region(clay, 'terrace', upper.difference(box(PAVILION[0], PAVILION[2], PAVILION[1], PAVILION[3])).difference(
        box(PLANT[0], PLANT[2], PLANT[1], PLANT[3])), Z_UPPER)
    for a, b in ((-TURF_X, TURF_X),):                                     # glass guard on the upper terrace's front
        wall(clay, 'guard', (a, yf - .02), (b, yf - .02), Z_UPPER, Z_UPPER + GUARD, (0, -1))
    # the parapets: inside faces from the walking surfaces, coping, and glass guards beside the slope
    ring = list(inner.exterior.coords)
    outer = list(main_block().exterior.coords)

    for p, q in pairwise(ring):                                            # inside faces, in short pieces, look inward
        n = plan_normal(q, p)
        cuts = sorted({0.0, 1.0} | {(c - p[1]) / (q[1] - p[1]) for c in (TERRACE_Y[0], yf) if (p[1] - c) * (q[1] - c) < 0})
        pieces = []
        for t0, t1 in pairwise(cuts):
            k = max(1, math.ceil(math.dist(p, q) * (t1 - t0) / 1.0))
            pieces += [(t0 + (t1 - t0) * j / k, t0 + (t1 - t0) * (j + 1) / k) for j in range(k)]
        for t0, t1 in pieces:
            a = (p[0] + (q[0] - p[0]) * t0, p[1] + (q[1] - p[1]) * t0)
            b = (p[0] + (q[0] - p[0]) * t1, p[1] + (q[1] - p[1]) * t1)
            mid = (a[1] + b[1]) / 2
            zone = Z_UPPER if mid >= yf else Z_LOWER if mid >= TERRACE_Y[0] else None
            za, zb = (zone, zone) if zone is not None else (walk(a[1]), walk(b[1]))
            ta, tb = parapet(a[1]), parapet(b[1])
            if a[1] > 0 and b[1] > 0 and abs(a[0]) < HALF_W - CORNER + 1e-6 and abs(b[0]) < HALF_W - CORNER + 1e-6:
                ta = tb = HS
            if ta - za > 1e-4 or tb - zb > 1e-4:
                clay.quad('cladding', (*a, min(za, ta)), (*b, min(zb, tb)), (*b, tb), (*a, ta), facing=(*n, 0))
    for (p, q), (pi, qi) in zip(pairwise(outer), pairwise(_matching(outer, ring))):
        tp, tq = _top(p), _top(q)
        clay.quad('coping', (*p, tp), (*q, tq), (*qi, tq), (*pi, tp), facing=(0, 0, 1))
        if min(p[1], q[1]) < TERRACE_Y[0] + 6:
            mid = ((p[0] + pi[0]) / 2, (p[1] + pi[1]) / 2)
            midq = ((q[0] + qi[0]) / 2, (q[1] + qi[1]) / 2)
            clay.quad('guard', (*mid, tp), (*midq, tq), (*midq, tq + GUARD), (*mid, tp + GUARD), facing=(*plan_normal(p, q), 0))
    # pavilion, plant enclosure and terrace furniture
    x0, x1, y0, y1, h = PAVILION
    pav = Face(((x0 + x1) / 2, y0), (1.0, 0.0), [((x0 - x1) / 2, Z_UPPER), ((x1 - x0) / 2, Z_UPPER), ((x1 - x0) / 2, Z_UPPER + h), ((x0 - x1) / 2, Z_UPPER + h)])
    pav.n = (0.0, -1.0)
    glazing = [{'u': ((x0 - x1) / 2 + 1.0 + 4.1 * k, (x0 - x1) / 2 + 4.6 + 4.1 * k), 'z': (Z_UPPER + .1, Z_UPPER + h - .6), 'depth': 4.5} for k in range(9)]
    build_face(clay, pav, glazing, role='pavilion', courses=False)
    for (a, b), n in ((((x1, y0), (x1, y1)), (1, 0)), (((x1, y1), (x0, y1)), (0, 1)), (((x0, y1), (x0, y0)), (-1, 0))):
        wall(clay, 'pavilion', a, b, Z_UPPER, Z_UPPER + h, n)
    flat_region(clay, 'roof_dark', box(x0, y0, x1, y1), Z_UPPER + h)
    for cx in (x0 + 8, x0 + 14):
        clay.box('grille', cx, cx + 2.6, y0 + 4, y0 + 6.4, Z_UPPER + h, Z_UPPER + h + 1.5)
    px0, px1, py0, py1, ph = PLANT
    clay.box('grille', px0 + .2, px1, py0, py1, Z_UPPER, Z_UPPER + ph)
    x = px0 + .6
    while x < px1 - .2:                                                    # louvres on the plant enclosure's south face
        clay.box('pavilion', x - .04, x + .04, py0 - .12, py0, Z_UPPER + .2, Z_UPPER + ph - .2)
        x += .45
    y = py0 + .5
    while y < py1 - .2:                                                    # and on its west face
        clay.box('pavilion', px0 + .08, px0 + .2, y - .04, y + .04, Z_UPPER + .2, Z_UPPER + ph - .2)
        y += .45
    rng = np.random.default_rng(77)
    for _ in range(14):
        x, y = rng.uniform(-20, 16), rng.uniform(yf + 2, y0 - 2)
        clay.cylinder('furniture', x, y, Z_UPPER, Z_UPPER + .75, .45, steps=10)
    for _ in range(9):
        x, y = rng.uniform(-20, 20), rng.uniform(TERRACE_Y[0] + 2, yf - 2)
        clay.cylinder('furniture', x, y, Z_LOWER, Z_LOWER + .75, .45, steps=10)


def _top(p):
    """Coping height at a point of the main block's outline."""
    if p[1] > HALF_L - CORNER - 1e-6 and abs(p[0]) <= HALF_W - CORNER + 1e-6:
        return HS
    return parapet(p[1]) if p[1] > 0 else (H0 if p[1] <= Y_LOW + 1e-6 else parapet(p[1]))


def _matching(outer, inner):
    """For each outline point, the nearest point of the parapet's inside face (the same ring, inset)."""
    ring = LineString(inner)
    return [ring.interpolate(ring.project(Point(p))).coords[0] for p in outer]


# ---- the wings, the stack and the site --------------------------------------------------------------
def wings(clay):
    whole = footprint()
    mb = main_block()
    roof_zone = whole.difference(mb)
    flat_region(clay, 'apron', whole.buffer(APRON, quad_segs=8).difference(whole), .02)
    exterior = whole.exterior.difference(mb.buffer(.001))
    seed = 7
    for seg in getattr(exterior, 'geoms', [exterior]):
        for p, q in pairwise(list(seg.coords)):
            length = math.dist(p, q)
            if length >= 8.0:                                              # straight runs carry slot windows
                u = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
                face = Face(p, u, [(0.0, 0.0), (length, 0.0), (length, HP + .6), (0.0, HP + .6)])
                slots = [o for o in slot_columns((3.5, length - 3.5), lambda _: 0.0, lambda _: HP + 2.0, seed=seed) if o['z'][1] < HP - 2.0]
                build_face(clay, face, slots[::2])
                seed += 3
                continue
            n = plan_normal(p, q)
            wall(clay, 'cladding', p, q, 0.0, HP + .6, n)
            z = COURSE
            while z < HP:
                o = (n[0] * .012, n[1] * .012)
                clay.quad('joint', (p[0] + o[0], p[1] + o[1], z - .03), (q[0] + o[0], q[1] + o[1], z - .03),
                          (q[0] + o[0], q[1] + o[1], z + .03), (p[0] + o[0], p[1] + o[1], z + .03), facing=(*n, 0))
                z += COURSE
    inset = orient(whole.buffer(-.5, quad_segs=8), 1.0)
    coping = roof_zone.difference(inset)
    flat_region(clay, 'coping', coping, HP + .6)
    upstand = inset.exterior.difference(mb.buffer(.001))
    for seg in getattr(upstand, 'geoms', [upstand]):
        for p, q in pairwise(list(seg.coords)):
            wall(clay, 'cladding', p, q, HP, HP + .6, plan_normal(q, p))
    deck = roof_zone.intersection(inset)
    gravel = deck.intersection(mb.buffer(1.6, quad_segs=8))
    (sx, sy), *_ = STACK
    gravel = gravel.union(Point(sx, sy).buffer(6.0, quad_segs=8).intersection(deck))
    hatches = [(-41.0, -20.0), (-41.0, -70.0), (-20.0, -88.0), (10.0, -88.0), (40.0, -60.0), (44.0, -35.0), (46.0, -84.0), (-40.0, -86.0)]
    flat_region(clay, 'gravel', gravel, HP + .01)
    green = deck.difference(gravel)
    flat_region(clay, 'roofgreen', green, HP)
    for x, y in hatches:
        if green.contains(Point(x, y)):
            clay.box('coping', x - .9, x + .9, y - .9, y + .9, HP, HP + .6)
    rng = np.random.default_rng(2903)
    keep = prep(green.buffer(-.8))
    blocked = [Point(x, y).buffer(1.6) for x, y in hatches]
    placed = 0
    for _ in range(9000):
        x, y = rng.uniform(-50, 56), rng.uniform(-96, 48)
        if not keep.contains(Point(x, y)) or any(b.contains(Point(x, y)) for b in blocked):
            continue
        role = 'planting' if rng.random() < .55 else 'meadow'
        mound(clay, role, x, y, rng.uniform(.5, 1.1), rng.uniform(.25, .55), 6, HP)
        if rng.random() < .3:
            mound(clay, 'blossom', x + rng.uniform(-.5, .5), y + rng.uniform(-.5, .5), rng.uniform(.25, .4), rng.uniform(.4, .6), 5, HP)
        placed += 1
        if placed >= 1500:
            break


def mound(clay, role, x, y, radius, height, sides, z0):
    """A low dome: a base ring, a shoulder ring turned half a step at 60 % height, and a crown."""
    base = [(x + radius * math.cos(2 * math.pi * k / sides), y + radius * math.sin(2 * math.pi * k / sides), z0 + .01) for k in range(sides)]
    shoulder = [(x + .72 * radius * math.cos(2 * math.pi * (k + .5) / sides), y + .72 * radius * math.sin(2 * math.pi * (k + .5) / sides),
                 z0 + .6 * height) for k in range(sides)]
    crown = (x, y, z0 + height)
    for k in range(sides):
        a, b, c, d = base[k], base[(k + 1) % sides], shoulder[k], shoulder[(k + 1) % sides]
        clay.tri(role, a, b, c, facing=(c[0] - x, c[1] - y, .6))
        clay.tri(role, b, d, c, facing=(b[0] - x, b[1] - y, .6))
        clay.tri(role, c, d, crown, facing=(c[0] - x, c[1] - y, 2.0))


def stack(clay):
    """Twin flues merged into one tapering stack, the second winding round the first, rising from the west wing roof."""
    (cx, cy), top, (r0, r1), (dx, dy), _, (q0, q1) = STACK
    steps = 14
    for twist, (a, b) in ((False, (r0, r1)), (True, (q0, q1))):
        rings = []
        for k in range(steps + 1):
            f = k / steps
            z, r = HP + (top - HP) * f, a + (b - a) * f
            ang = math.radians(TWIST * f) if twist else 0.0
            ox, oy = (dx * math.cos(ang) - dy * math.sin(ang), dx * math.sin(ang) + dy * math.cos(ang)) if twist else (0.0, 0.0)
            rings.append([(cx + ox + r * math.cos(2 * math.pi * j / 28), cy + oy + r * math.sin(2 * math.pi * j / 28), z) for j in range(28)])
        clay.loft('stack', rings, caps=(False, False), smooth=40)
    ang = math.radians(TWIST)
    tx, ty = cx + dx * math.cos(ang) - dy * math.sin(ang), cy + dx * math.sin(ang) + dy * math.cos(ang)
    outer = Point(cx, cy).buffer(r1, quad_segs=7).union(Point(tx, ty).buffer(q1, quad_segs=7))
    flues = Point(cx, cy).buffer(r1 - .35, quad_segs=7).union(Point(tx, ty).buffer(q1 - .35, quad_segs=7))
    flat_region(clay, 'stack', outer.difference(flues), top)
    flat_region(clay, 'flue', flues, top - .6)


def rotate(clay):
    """Turn the plan frame a quarter turn: plan east becomes authoring -y (the street front), plan north becomes +x."""
    turned = {}
    for role, faces in clay.triangles.items():
        out = []
        for face in faces:
            out.append(tuple((p[1], -p[0], p[2]) for p in face))
        turned[role] = out
    clay.triangles = turned


def build():
    clay = Clay()
    main_facades(clay)
    pier(clay)
    roof(clay)
    wings(clay)
    stack(clay)
    rotate(clay)
    return clay


# ---- records -----------------------------------------------------------------------------------------
def to_auth(x, y):
    return y, -x


def entrances():
    """Every door, from the model's own numbers, in the authoring frame."""
    mid = sum(ENTRANCE[:2]) / 2
    doors = [{'kind': 'visitor entrance', 'centre_xy_m': [round(v, 3) for v in to_auth(HALF_W, mid)], 'facing': 'street front (-y)',
              'clear_width_m': ENTRANCE[1] - ENTRANCE[0], 'door_height_m': 2.9, 'threshold_top_m': 0.0, 'rise_m': 0.0}]
    for a, b in LOADING:
        doors.append({'kind': 'loading door', 'centre_xy_m': [round(v, 3) for v in to_auth((a + b) / 2, HALF_L)], 'facing': '+x (plan north)',
                      'clear_width_m': b - a, 'door_height_m': 9.0, 'threshold_top_m': 0.0, 'rise_m': 0.0})
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
           'glass_close', 'climbing_wall', 'summit', 'slope', 'low_end_contact', 'stack_contact', 'match_oblique', 'match_top')


def prework(candidate):
    return {
        'candidate': candidate, 'method': METHOD, 'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'title': TITLE,
        'sources': [source_lock_for(r) for r in SOURCES],
        'excluded_sources': [source_lock_for('front', EXCLUDED) | {'reason': 'grey render of the old LEGO model'}],
        'gate_a': {'front_oblique_top_coherent': False,
                   'note': ('The variant has no usable street view: variant_0.png is a grey render of the old LEGO model. The oblique '
                            'and roof views agree and are the authority. A person must rule on this before activation, as for the '
                            'concert hall, the crescent and the laneway.')},
        'measurement_contract': {
            'scale_basis': ('No image carries a scale. The main block in the roof view (294 by 780 px) is set to 60 by 159 m '
                            '(0.204 m/px), matching the catalogue\'s suggested 160 m length. Heights come from a pinhole camera '
                            'fitted to eight points of the block in the oblique (8.2 px RMS) with the plan held fixed: summit '
                            'parapet 80.2 m, low-end parapet 39.5 m, wing roof 29.8 m. A wing roof below 20 m fits clearly worse '
                            '(12.5 px RMS at 20 m, 26 px at 5 m). The east parapet is one straight line from the low end to the summit.'),
            'source_measurements': {
                'oblique': ['High view from the south-east over the wings toward the harbour.',
                            ('Long block in light aluminium bricks; its whole roof is one green turf slope rising north, with a '
                             'stepped path and a glass guard down each side and a rounded low end.'),
                            ('East face: tall slot windows glowing warm in staggered columns, and a climbing wall with large '
                             'blue and yellow volumes on a pier standing proud of the face.'),
                            ('Summit: a lower terrace with tables in front of a glazed bar, an upper terrace with a glass guard, '
                             'a pavilion and plant behind; the side walls rise to the summit corner.'),
                            ('Lower green-roofed wings in aluminium brick in front of and beside the low end; a tall twin-flue '
                             'stack to the west.')],
                'top': ['Near-nadir view, north up.',
                        'Main block 294 by 780 px with rounded corners; turf 234 px wide between two stepped paths.',
                        ('Summit at the north: an upper terrace with string lights, a pavilion 210 px wide and a plant enclosure; '
                         'a lower terrace with tables; short flights at each side between them.'),
                        'A pier 26 by 140 px on the east face 230 to 372 px from the top.',
                        ('Green-roofed wings west and south-east of the block, with hatches; the west wing narrows to a strip '
                         '58 px wide that runs north to 220 px from the top; the stack in the west wing.')]},
            'source_conflicts': [('variant_0.png, the street view, is a grey render of the old LEGO model, not a picture of this '
                                  'building. It is excluded; the oblique and roof views govern. Needs a ruling by a person.'),
                                 ('The roof view draws the stack leaning, its flue about 30 m north-west of its base; the oblique '
                                  'shows it upright and further east. The base position from the roof view governs; the height, '
                                  'about 100 m, comes from the oblique camera.'),
                                 ('The catalogue suggests a 160 by 70 m footprint. The images show the 60 by 159 m block with wings '
                                  'that make the whole 103 m wide; the images govern.')],
            'hidden_assumptions': [('The west and north faces are not seen; they carry the same slot windows, and the north face two '
                                    'roller doors for the plant\'s deliveries (inferred).'),
                                   ('The wings\' southern end lies outside both images; they are drawn ending 16 m south of the block.'),
                                   ('Interiors are schematic: each slot window has a lit room face 0.9 m behind its outer face; the bar and '
                                    'pavilion have shallow lit interiors; the plant itself is not modelled.'),
                                   'The harbour, ships, cranes, neighbouring sheds, roads, vehicles and people belong to the site and are not modelled.']},
        'roof_contract': {'form': ('one straight turf slope from the low end to the summit terraces, stepped paths beside it, a '
                                   'parapet with a glass guard; terraces, pavilion and plant at the summit'),
                          'weathering': 'the slope, paths, terraces and parapets close the roof completely'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()}},
        'identity_contract': ['a long aluminium-brick block whose whole roof is one green ski slope with stepped paths',
                              'tall warm slot windows in staggered columns', 'a climbing wall on a pier of the east face',
                              'terraced summit with bar and pavilion', 'lower green-roofed wings and a tall twin-flue stack'],
        'programme_contract': {'ski_slope': 1, 'summit_terraces': 2, 'climbing_wall': 1, 'visitor_entrance': 1},
        'contact_contract': {'base_datum_m': 0.0, 'ground': 'a 4 m apron round the whole footprint; nothing below grade'},
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
        'heights_m': {'summit_parapet': HS, 'low_end_parapet': H0, 'wing_roof': HP, 'lower_terrace': round(Z_LOWER, 3),
                      'upper_terrace': round(Z_UPPER, 3), 'stack': STACK[1]},
        'entrances': {'doors': entrances()},
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
