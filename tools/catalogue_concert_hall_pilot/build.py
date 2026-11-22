"""Build the Timber Acoustic concert hall as an RLASM 6.1 architectural-clay GLB.

Exact variant: `concert_hall_modern` / `concert_timber_acoustic` (variant 2). The locked oblique and
roof views show a rounded-rectangle podium wrapped in vertical bronze fins over a glazed ground
floor, a planted roof garden with winding paths, and two opposing curved shells clad in bronze
battens that spiral round an oval oculus, through which the auditorium is seen: raked seating
facing a stage. The catalogue's street view of this variant is the grey preview of an old LEGO
model, not a picture of the building, so it is recorded as a source conflict and not used.

    python3 tools/catalogue_concert_hall_pilot/build.py --output <new directory> --version <n>

The output directory must not exist: RLASM never overwrites a candidate. The GLB, renders and
boards are review material and stay outside Git until a person activates them.

Frame: x east, y north (the oblique looks north from the south), z up, metres, grade z = 0.
The podium is centred on the origin.
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
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'catalogue_plus15_concrete_pilot'))
from clay_kit import METHOD, Clay

SLUG = 'concert-timber-acoustic'
ARCHETYPE, VARIANT, INDEX = 'concert_hall_modern', 'concert_timber_acoustic', 2
TITLE = 'Timber Acoustic'
SOURCE_DIR = 'frontend/public/archetypes/buildings/concert_hall_modern'
SOURCES = {'oblique': f'variant_{INDEX}_angle_60.jpg', 'top': f'variant_{INDEX}_angle_90.jpg'}
EXCLUDED = {'front': f'variant_{INDEX}.png'}     # the grey preview of the old LEGO model; see source_conflicts

# ---- measured contract (metres) ------------------------------------------------------------------
PODIUM_A, PODIUM_B, PODIUM_N = 44.0, 32.2, 3.3   # superellipse half-width, half-depth and exponent of the podium's outer face
GLASS_SET = 1.0                                   # the ground-floor glazing stands this far inside the band above
GF_TOP = 6.0                                      # ground floor: foyer floor at FOYER, band soffit at GF_TOP
FOYER = .15
UPPER = 6.4                                       # upper floor level (offices and rehearsal rooms behind the band)
TRANSOM = 3.4                                     # transom of the ground-floor curtain wall, over the door heads
ROOF = 10.6                                       # roof garden surface
COPING = 11.2                                     # top of the band and its parapet
GUARD = 1.1                                       # glass guard above the roof surface, set back from the coping
FIN = (.9, .07, .22)                              # fin spacing along the band, thickness and depth
RIBBON = (162.0, 214.0, 7.4, 9.5)                 # ribbon window in the band: podium polar angles from-to (deg) and sill/head
OCULUS_C = (11.4, -1.7)                           # oculus centre
OCULUS_AB = (11.9, 9.4)                           # oculus half-axes
LIP_W, LIP_Z = 1.2, 12.4                          # the dark lip round the oculus: width and top
HALL_FLOOR = 1.0
NOTCH = 115.0                                     # polar angle (about the oculus) where the two shells meet at the north
# shell outer rims as (polar angle about the oculus in degrees, outer radius, rim height): spiral sheets rising outward
SHELL_A = [(115, 27.7, 19.6), (135, 34.0, 23.0), (155, 39.0, 23.6), (175, 42.0, 22.2), (195, 38.5, 19.8), (217, 27.6, 16.6),
           (240, 21.0, 14.6), (265, 17.0, 13.4), (285, 15.0, 12.9), (300, 13.8, 12.6)]
SHELL_B = [(-50, 13.0, 12.6), (-40, 14.8, 13.1), (-20, 18.0, 14.4), (0, 20.9, 16.2), (20, 23.5, 18.4), (42, 25.0, 20.4),
           (65, 26.0, 21.6), (90, 26.8, 21.2), (115, 27.7, 18.2)]
RING = (4.5, 260.0, .6, 1.2)                      # the east sheet runs on under the west one as a ring round the oculus: width at the
                                                  # notch, polar angle where it dies out, its rise, and the step up to the west sheet's edge
LEAN = .28                                        # the shells' outer walls lean in: feet this far out per metre of rise
SAG = 1.7                                         # shell section profile: z = lip + rise * s**SAG, concave like a bowl
ENTRANCE = {'angle': -90.0, 'width': 7.2}          # main doors: south, on the podium's front
EAST_DOOR = {'angle': -8.0, 'width': 4.8}
LOADING = (18.0, 52.0)                            # back-of-house: opaque ground floor with a loading door (podium polar angles)
ROOF_DOOR = 203.0                                  # roof-garden entrance in the foot of the west shell: polar angle about the oculus
APRON = 6.0

PALETTE = {  # role -> flat colour (sRGB), in node order
    'apron': {'colour': '#9c978d', 'module': 'plaza'},
    'plinth': {'colour': '#5f5a52', 'module': 'podium base'},
    'cladding': {'colour': '#4f3a29', 'module': 'band wall'},
    'fins': {'colour': '#9a6a44', 'module': 'bronze fins', 'roughness': .6},
    'soffit': {'colour': '#7b5a3e', 'module': 'band soffit'},
    'coping': {'colour': '#3a2f26', 'module': 'roof edge', 'roughness': .55},
    'mullion': {'colour': '#3a3532', 'module': 'curtain wall', 'roughness': .5},
    'door': {'colour': '#1d272d', 'module': 'doors', 'alpha': .62, 'roughness': .25},
    'service': {'colour': '#45423d', 'module': 'doors'},
    'floor': {'colour': '#8a8378', 'module': 'floors'},
    'interior': {'colour': '#b8875a', 'module': 'foyer timber'},
    'ceiling': {'colour': '#d9c4a2', 'module': 'foyer ceiling'},
    'structure': {'colour': '#6f6a62', 'module': 'columns'},
    'furniture': {'colour': '#4a4038', 'module': 'foyer furniture'},
    'roofdeck': {'colour': '#5c6838', 'module': 'roof garden'},
    'planting': {'colour': '#6f8a3e', 'module': 'roof garden'},
    'meadow': {'colour': '#a89c5c', 'module': 'roof garden'},
    'shrub': {'colour': '#4c6a30', 'module': 'roof garden'},
    'blossom': {'colour': '#dcd6c4', 'module': 'roof garden'},
    'path': {'colour': '#b4ada0', 'module': 'roof paths'},
    'shell': {'colour': '#8f6440', 'module': 'acoustic shells', 'roughness': .6},
    'seam': {'colour': '#6a482d', 'module': 'acoustic shells', 'roughness': .6},
    'shellwall': {'colour': '#7a5638', 'module': 'acoustic shells', 'roughness': .6},
    'lip': {'colour': '#3f342b', 'module': 'oculus lip', 'roughness': .55},
    'hall': {'colour': '#b0703a', 'module': 'auditorium'},
    'seats': {'colour': '#8c3a2a', 'module': 'auditorium'},
    'stage': {'colour': '#2a2724', 'module': 'auditorium'},
    'panel': {'colour': '#c98a4b', 'module': 'auditorium'},
    'light': {'colour': '#f6e6c8', 'module': 'interior lights'},
    'glass': {'colour': '#2b2622', 'module': 'ground floor glazing', 'alpha': .52, 'roughness': .2, 'transmission': .3},
    'oculus': {'colour': '#eef2f3', 'module': 'oculus glazing', 'alpha': .05, 'roughness': .1},
    'guard': {'colour': '#c9d3d6', 'module': 'roof guard', 'alpha': .22, 'roughness': .15},
    'ribbon': {'colour': '#2a2018', 'module': 'band windows', 'alpha': .45, 'roughness': .24, 'transmission': .28},
}


# ---- plan geometry ---------------------------------------------------------------------------------
def superellipse(a, b, n=PODIUM_N, steps=360):
    """Points of |x/a|^n + |y/b|^n = 1, counter-clockwise from +x."""
    pts = []
    for k in range(steps):
        t = 2 * math.pi * k / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s)))
    return pts


def resample(ring, step):
    """A closed ring resampled at near-equal spacing, starting at its first point."""
    line = LineString(ring + ring[:1])
    n = max(8, round(line.length / step))
    return [line.interpolate(line.length * k / n).coords[0] for k in range(n)]


def podium_ring(inset=0.0, step=1.2):
    return resample(superellipse(PODIUM_A - inset, PODIUM_B - inset), step)


def polar_deg(x, y):
    return math.degrees(math.atan2(y, x)) % 360


def in_range(angle, lo, hi):
    angle, lo, hi = angle % 360, lo % 360, hi % 360
    return lo <= angle <= hi if lo <= hi else angle >= lo or angle <= hi


def outward(ring, i):
    """Unit outward normal (in plan) at ring point i of a counter-clockwise ring."""
    (x0, y0), (x1, y1) = ring[i - 1], ring[(i + 1) % len(ring)]
    tx, ty = x1 - x0, y1 - y0
    length = math.hypot(tx, ty) or 1.0
    return ty / length, -tx / length


def ellipse_r(theta_deg, a, b):
    t = math.radians(theta_deg)
    return 1 / math.sqrt((math.cos(t) / a) ** 2 + (math.sin(t) / b) ** 2)


def catmull(points, t):
    """Catmull-Rom through (t_i, values...) control rows, clamped at the ends."""
    ts = [p[0] for p in points]
    k = max(0, min(len(points) - 2, next((i for i in range(len(ts) - 1) if ts[i] <= t <= ts[i + 1]), len(ts) - 2)))
    p0, p1, p2, p3 = points[max(k - 1, 0)], points[k], points[k + 1], points[min(k + 2, len(points) - 1)]
    u = (t - p1[0]) / (p2[0] - p1[0])
    out = []
    for j in range(1, len(p1)):
        a, b, c, d = p0[j], p1[j], p2[j], p3[j]
        out.append(.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3))
    return out


def flat_region(clay, role, geometry, z, up=True):
    """Triangulate a shapely polygon (holes allowed) as a horizontal surface at height z."""
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


def obox(clay, role, cx, cy, ux, uy, half_u, half_v, z0, z1):
    """A vertical box whose plan is a rectangle with axis u = (ux, uy) and its perpendicular."""
    vx, vy = -uy, ux
    corners = [(cx + su * half_u * ux + sv * half_v * vx, cy + su * half_u * uy + sv * half_v * vy) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    clay.prism(role, corners, z0, z1)


def band_wall(clay, role, ring, z0, z1, skip=None, facing_out=True):
    """A closed vertical wall along a ring; `skip(angle, za, zb)` returns height spans to leave open."""
    n = len(ring)
    for i in range(n):
        (x0, y0), (x1, y1) = ring[i], ring[(i + 1) % n]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = outward(ring, i)
        face = (nx, ny, 0) if facing_out else (-nx, -ny, 0)
        spans = [(z0, z1)] if skip is None else skip(polar_deg(mx, my), z0, z1)
        for za, zb in spans:
            if zb - za > 1e-4:
                clay.quad(role, (x0, y0, za), (x1, y1, za), (x1, y1, zb), (x0, y0, zb), facing=face)


# ---- the podium ----------------------------------------------------------------------------------
def podium(clay):
    outer = podium_ring(0.0)
    glass = podium_ring(GLASS_SET)
    inner = podium_ring(.6)
    site = Polygon(superellipse(PODIUM_A + APRON, PODIUM_B + APRON))
    foot = Polygon(superellipse(PODIUM_A, PODIUM_B))
    flat_region(clay, 'apron', site.difference(foot), .02)
    # ground floor: glazing set back under the band, opaque back-of-house to the north-east
    gfoot = Polygon(glass)
    flat_region(clay, 'floor', gfoot, FOYER)
    flat_region(clay, 'plinth', foot.difference(gfoot), .03)

    def gf_spans(angle, z0, z1):
        return [] if in_range(angle, *LOADING) else [(z0, z1)]
    band_wall(clay, 'glass', glass, FOYER, GF_TOP, skip=gf_spans)
    band_wall(clay, 'cladding', glass, 0.0, GF_TOP, skip=lambda a, z0, z1: [(z0, z1)] if in_range(a, *LOADING) else [])
    for i, (x, y) in enumerate(glass):                                   # mullions every fourth ring point (about 4.8 m)
        if i % 4 or in_range(polar_deg(x, y), *LOADING):
            continue
        nx, ny = outward(glass, i)
        obox(clay, 'mullion', x + nx * .04, y + ny * .04, ny, -nx, .035, .09, FOYER, GF_TOP)
    for d in (ENTRANCE, EAST_DOOR):                                      # door leaves in the curtain wall
        for i, (x, y) in enumerate(glass):
            a = polar_deg(x, y)
            if abs(((a - d['angle'] + 180) % 360) - 180) < math.degrees(d['width'] / 2 / math.hypot(x, y)):
                nx, ny = outward(glass, i)
                ux, uy = ny, -nx                                         # glazed leaf in a frame, with a head over it
                obox(clay, 'door', x + nx * .06, y + ny * .06, ux, uy, .58, .02, FOYER, 2.7)
                for side in (-1, 1):
                    obox(clay, 'mullion', x + nx * .06 + side * .6 * ux, y + ny * .06 + side * .6 * uy, ux, uy, .03, .05, FOYER, 2.75)
                obox(clay, 'mullion', x + nx * .06, y + ny * .06, ux, uy, .63, .05, 2.7, 2.85)
    open_glass = lambda a, z0, z1: [] if in_range(a, *LOADING) else [(z0, z1)]
    band_wall(clay, 'mullion', podium_ring(GLASS_SET - .05), TRANSOM - .06, TRANSOM + .06, skip=open_glass)
    band_wall(clay, 'mullion', podium_ring(GLASS_SET - .05), FOYER, FOYER + .12, skip=open_glass)
    load_a = sum(LOADING) / 2
    lx, ly = next((p for p in glass if abs(polar_deg(*p) - load_a) < 1.5), glass[0])
    nx, ny = lx / math.hypot(lx, ly), ly / math.hypot(lx, ly)
    obox(clay, 'service', lx + nx * .05, ly + ny * .05, ny, -nx, 2.4, .04, 0.0, 4.2)
    # the band: soffit, outer wall with a ribbon window, coping and parapet
    band_soffit = foot.difference(gfoot)
    flat_region(clay, 'soffit', band_soffit, GF_TOP, up=False)

    def band_spans(angle, z0, z1):
        return [(z0, RIBBON[2]), (RIBBON[3], z1)] if in_range(angle, RIBBON[0], RIBBON[1]) else [(z0, z1)]
    band_wall(clay, 'cladding', outer, GF_TOP, COPING, skip=band_spans)
    ribbon_back = podium_ring(.35)                                       # window glass in a 0.35 m reveal
    band_wall(clay, 'ribbon', ribbon_back, RIBBON[2], RIBBON[3],
              skip=lambda a, z0, z1: [(z0, z1)] if in_range(a, RIBBON[0], RIBBON[1]) else [])
    n = len(outer)
    for i in range(n):                                                   # reveal returns at sill and head
        (x0, y0), (x1, y1) = outer[i], outer[(i + 1) % n]
        if not in_range(polar_deg((x0 + x1) / 2, (y0 + y1) / 2), RIBBON[0], RIBBON[1]):
            continue
        (bx0, by0), (bx1, by1) = ribbon_back[i % len(ribbon_back)], ribbon_back[(i + 1) % len(ribbon_back)]
        for z, up in ((RIBBON[2], 1), (RIBBON[3], -1)):
            clay.quad('cladding', (x0, y0, z), (x1, y1, z), (bx1, by1, z), (bx0, by0, z), facing=(0, 0, up))
    flat_region(clay, 'coping', Polygon(outer).difference(Polygon(inner)), COPING)
    band_wall(clay, 'cladding', inner, ROOF, COPING, facing_out=False)
    # fins: vertical bronze fins standing proud of the band, none across the ribbon window
    fins = podium_ring(-FIN[2] / 2, step=FIN[0])
    for i, (x, y) in enumerate(fins):
        if in_range(polar_deg(x, y), RIBBON[0] + .6, RIBBON[1] - .6):
            continue
        nx, ny = outward(fins, i)
        obox(clay, 'fins', x, y, ny, -nx, FIN[1] / 2, FIN[2] / 2, GF_TOP, COPING - .02)
    # guard on the roof garden edge
    guard = podium_ring(1.0)
    band_wall(clay, 'guard', guard, ROOF, ROOF + GUARD)
    band_wall(clay, 'coping', guard, ROOF + GUARD - .04, ROOF + GUARD)


def interiors(clay):
    """The foyer seen through the curtain wall, and the rooms behind the ribbon window."""
    cx, cy = OCULUS_C
    hall_a, hall_b = 24.0, 18.0
    ring = [(cx + hall_a * math.cos(t), cy + hall_b * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    band_wall(clay, 'interior', ring, FOYER, GF_TOP - .1)
    glass = Polygon(podium_ring(GLASS_SET + .05))
    flat_region(clay, 'ceiling', glass.difference(Polygon(ring)), GF_TOP - .1, up=False)
    for t in np.linspace(0, 2 * math.pi, 14, endpoint=False):           # foyer columns
        x, y = cx + (hall_a + 4.2) * math.cos(t), cy + (hall_b + 4.2) * math.sin(t)
        if glass.buffer(-1.0).contains(Point(x, y)):
            clay.cylinder('structure', x, y, FOYER, GF_TOP - .1, .28, steps=12)
    for k, t in enumerate(np.linspace(math.radians(200), math.radians(330), 22)):   # cafe tables along the south foyer
        for row in (0, 1):
            r = 1.0 + .2 * row
            x, y = (PODIUM_A - GLASS_SET - 3.2 - 2.0 * row) * math.cos(t) * r ** 0, (PODIUM_B - GLASS_SET - 3.2 - 2.0 * row) * math.sin(t)
            if not glass.buffer(-1.5).contains(Point(x, y)) or Point(x, y).distance(Point(0, -PODIUM_B)) < 5.5:
                continue
            clay.cylinder('furniture', x, y, FOYER, FOYER + .72, .05, steps=6)
            clay.cylinder('furniture', x, y, FOYER + .72, FOYER + .76, .42, steps=12)
    clay.box('interior', -6.0, -1.5, -22.0, -20.6, FOYER, FOYER + 1.1)    # box office and bar counters
    clay.box('interior', 3.0, 9.0, -22.5, -21.1, FOYER, FOYER + 1.1)
    for k in range(18):                                                  # grand stair to the upper floor, west foyer
        z = FOYER + (UPPER - FOYER) * (k + 1) / 18
        clay.box('floor', -30.0 + k * .3, -29.7 + k * .3, -8.0, -5.6, z - .18, z)
    flat_region(clay, 'light', glass.difference(Polygon(ring)).buffer(-2.0), GF_TOP - .12, up=False)
    # upper floor rooms behind the ribbon window: floor, ceiling and a back wall 3 m in
    room = podium_ring(3.4)
    span = Polygon(podium_ring(.35)).difference(Polygon(room))
    sector = Polygon([(0, 0)] + [(80 * math.cos(math.radians(a)), 80 * math.sin(math.radians(a))) for a in np.linspace(RIBBON[0], RIBBON[1], 24)])
    flat_region(clay, 'floor', span.intersection(sector), UPPER)
    flat_region(clay, 'ceiling', span.intersection(sector), RIBBON[3] + .6, up=False)
    band_wall(clay, 'interior', room, UPPER, RIBBON[3] + .6,
              skip=lambda a, z0, z1: [(z0, z1)] if in_range(a, RIBBON[0], RIBBON[1]) else [])


# ---- shells, lip and auditorium ----------------------------------------------------------------------
def lip_r(theta):
    return ellipse_r(theta, OCULUS_AB[0] + LIP_W, OCULUS_AB[1] + LIP_W)


def ring_width(t):
    """Width of the ring by which the east sheet runs on under the west one, at polar angle t (degrees)."""
    width, end = RING[0], RING[1]
    return 0.0 if t >= end else width * (end - t) / (end - NOTCH) if t >= NOTCH else 0.0


def ring_top(t):
    return LIP_Z + RING[2] * ring_width(t) / RING[0]


def west_inner(t):
    """The west sheet's inner edge: on the lip where the ring has died out, stepped up over the ring elsewhere."""
    w = ring_width(t)
    return lip_r(t) + w, ring_top(t) + RING[3] * w / RING[0]


def shell(clay, control, step=2.5, sections=7, inner=None, start=0.0):
    """One spiral sheet: sections from its inner edge to the outer rim, an outer wall down to the roof, and end walls."""
    cx, cy = OCULUS_C
    t0, t1 = control[0][0] + start, control[-1][0]
    thetas = list(np.arange(t0, t1, step)) + [t1]
    rows = []
    for t in thetas:
        r_foot, z_out = catmull(control, t)
        r_out = r_foot - LEAN * (z_out - ROOF)                           # the control radius is the wall's foot; the rim leans in
        r_in, z_in = inner(t) if inner else (lip_r(t), LIP_Z)
        u = (math.cos(math.radians(t)), math.sin(math.radians(t)))
        row = []
        for k in range(sections):
            s = k / (sections - 1)
            r = r_in + (r_out - r_in) * s
            row.append((cx + u[0] * r, cy + u[1] * r, z_in + (z_out - z_in) * s ** SAG))
        rows.append(row)
    for a, b in pairwise(rows):
        for k in range(sections - 1):
            clay.quad('shell', a[k], a[k + 1], b[k + 1], b[k], facing=(0, 0, 1))
    def foot(p):                                                         # where the leaning outer wall meets the roof
        dx, dy = p[0] - cx, p[1] - cy
        length = math.hypot(dx, dy)
        return (p[0] + dx / length * LEAN * (p[2] - ROOF), p[1] + dy / length * LEAN * (p[2] - ROOF), ROOF)
    for a, b in pairwise(rows):                                     # outer wall from the rim down to the roof
        pa, pb = a[-1], b[-1]
        out = (pa[0] - cx, pa[1] - cy, LEAN * math.hypot(pa[0] - cx, pa[1] - cy) / 10)
        clay.quad('shellwall', foot(pa), foot(pb), pb, pa, facing=out)
    for a, b in pairwise(rows):                                     # a dark cap along the rim
        pa, pb = a[-1], b[-1]
        if pa[2] - ROOF < .6:
            continue
        ua, ub = [(p[0] - cx, p[1] - cy) for p in (pa, pb)]
        ua, ub = [(v[0] / math.hypot(*v) * .06, v[1] / math.hypot(*v) * .06) for v in (ua, ub)]
        clay.quad('lip', (pa[0] + ua[0], pa[1] + ua[1], pa[2] - .32), (pb[0] + ub[0], pb[1] + ub[1], pb[2] - .32),
                  (pb[0] + ub[0], pb[1] + ub[1], pb[2] + .06), (pa[0] + ua[0], pa[1] + ua[1], pa[2] + .06), facing=(ua[0], ua[1], 0))
    for row, sign in ((rows[0], -1), (rows[-1], 1)):                     # end walls in the section planes
        ring = list(row) + [foot(row[-1]), (row[0][0], row[0][1], ROOF)]
        t = thetas[0] if sign < 0 else thetas[-1]
        tangent = (-math.sin(math.radians(t)) * sign, math.cos(math.radians(t)) * sign, 0)
        clay.polygon('shellwall', ring, tangent)
    for j in range(0, len(rows), 2):                                     # standing seams up each section
        row = rows[j]
        for p, q in pairwise(row):
            lift = .05
            dx, dy = q[0] - p[0], q[1] - p[1]
            length = math.hypot(dx, dy) or 1.0
            sx, sy = -dy / length * .07, dx / length * .07
            clay.quad('seam', (p[0] - sx, p[1] - sy, p[2] + lift), (q[0] - sx, q[1] - sy, q[2] + lift),
                      (q[0] + sx, q[1] + sy, q[2] + lift), (p[0] + sx, p[1] + sy, p[2] + lift), facing=(0, 0, 1))
    for j in range(len(rows) - 1):                                       # battens on the outer wall
        pa = rows[j][-1]
        fa = foot(pa)
        out = (pa[0] - cx, pa[1] - cy)
        length = math.hypot(*out)
        ox, oy = out[0] / length * .05, out[1] / length * .05
        tx, ty = -oy / .05 * .06, ox / .05 * .06
        clay.quad('seam', (fa[0] + ox - tx, fa[1] + oy - ty, ROOF), (fa[0] + ox + tx, fa[1] + oy + ty, ROOF),
                  (pa[0] + ox + tx, pa[1] + oy + ty, pa[2] - .05), (pa[0] + ox - tx, pa[1] + oy - ty, pa[2] - .05), facing=(out[0], out[1], .3))
    footprint = Polygon([foot(row[-1])[:2] for row in rows] + [(p[0], p[1]) for p in (row[0] for row in reversed(rows))])
    return footprint.buffer(0)


def under_ring(clay, step=2.5):
    """The east sheet's continuation under the west sheet: a narrow sloping ring on the lip, and the fascia of the west sheet's stepped edge."""
    cx, cy = OCULUS_C
    thetas = list(np.arange(NOTCH, RING[1], step)) + [RING[1]]
    rows = []
    for t in thetas:
        u = (math.cos(math.radians(t)), math.sin(math.radians(t)))
        r0, w = lip_r(t), ring_width(t)
        r1, z1 = west_inner(t)
        rows.append([(cx + u[0] * r0, cy + u[1] * r0, LIP_Z), (cx + u[0] * (r0 + w), cy + u[1] * (r0 + w), ring_top(t)),
                     (cx + u[0] * r1, cy + u[1] * r1, z1)])
    for a, b in pairwise(rows):
        clay.quad('shell', a[0], a[1], b[1], b[0], facing=(0, 0, 1))
        clay.quad('shellwall', a[1], b[1], b[2], a[2], facing=(cx - a[1][0], cy - a[1][1], 0))
    for j in range(0, len(rows), 2):                                     # seams carry on across the ring
        p, q = rows[j][0], rows[j][1]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < .2:
            continue
        sx, sy = -dy / length * .07, dx / length * .07
        clay.quad('seam', (p[0] - sx, p[1] - sy, p[2] + .05), (q[0] - sx, q[1] - sy, q[2] + .05),
                  (q[0] + sx, q[1] + sy, q[2] + .05), (p[0] + sx, p[1] + sy, p[2] + .05), facing=(0, 0, 1))


def oculus_and_hall(clay):
    cx, cy = OCULUS_C
    a, b = OCULUS_AB
    inner = [(cx + a * math.cos(t), cy + b * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    outer = [(cx + (a + LIP_W) * math.cos(t), cy + (b + LIP_W) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    flat_region(clay, 'lip', Polygon(outer).difference(Polygon(inner)), LIP_Z)
    band_wall(clay, 'shellwall', outer, ROOF, LIP_Z - .3)
    band_wall(clay, 'lip', outer, LIP_Z - .3, LIP_Z)
    band_wall(clay, 'hall', inner, HALL_FLOOR, LIP_Z, facing_out=False)
    flat_region(clay, 'oculus', Polygon(inner), LIP_Z - .06)
    hall = Polygon(inner).buffer(-.05)
    stage_x = cx + 5.0
    stage = hall.intersection(shapely.geometry.box(stage_x - 1.0, -100, 100, 100))
    flat_region(clay, 'stage', stage, 2.1)
    for k, (x0, height) in enumerate(((cx + 8.0, 2.6), (cx + 9.4, 3.1), (cx + 10.6, 3.6))):   # choir terraces behind the stage
        flat_region(clay, 'hall', hall.intersection(shapely.geometry.box(x0, -100, 100, 100)), height)
    flat_region(clay, 'hall', hall, HALL_FLOOR)
    for t in np.arange(0, 360, 4.0):                                     # vertical acoustic panels round the hall wall
        x, y = cx + (a - .12) * math.cos(math.radians(t)), cy + (b - .12) * math.sin(math.radians(t))
        nx, ny = math.cos(math.radians(t)) / a, math.sin(math.radians(t)) / b
        length = math.hypot(nx, ny)
        obox(clay, 'panel', x, y, -ny / length, nx / length, .32, .1, 3.0 if in_range(t, -70, 70) else 7.2, LIP_Z - .8)
    for z in (7.2, 9.6):                                                 # two balcony rings round the back and sides, open to the stage
        back = Polygon(inner).difference(Polygon(inner).buffer(-1.7))
        wedge = Polygon([(cx, cy)] + [(cx + 60 * math.cos(math.radians(t)), cy + 60 * math.sin(math.radians(t))) for t in np.linspace(75, 285, 30)])
        ledge = back.intersection(wedge)
        flat_region(clay, 'hall', ledge, z)
        front = [(cx + (a - 1.7) * math.cos(math.radians(t)), cy + (b - 1.7) * math.sin(math.radians(t))) for t in np.linspace(75, 285, 44)]
        for p, q in pairwise(front):
            clay.quad('panel', (p[0], p[1], z - .5), (q[0], q[1], z - .5), (q[0], q[1], z + 1.0), (p[0], p[1], z + 1.0), facing=(cx - p[0], cy - p[1], 0))
    sx, sy = stage_x, cy
    for k in range(11):                                                  # raked seating facing the stage
        r0, r1 = 4.6 + .95 * k, 4.6 + .95 * (k + 1)
        z = HALL_FLOOR + .4 + .42 * k
        sector = Polygon([(sx + r0 * math.cos(t), sy + r0 * math.sin(t)) for t in np.linspace(math.radians(118), math.radians(242), 40)] +
                         [(sx + r1 * math.cos(t), sy + r1 * math.sin(t)) for t in np.linspace(math.radians(242), math.radians(118), 40)])
        tier = sector.intersection(hall)
        if tier.is_empty:
            continue
        flat_region(clay, 'hall', tier, z)
        seats = Polygon([(sx + (r1 - .55) * math.cos(t), sy + (r1 - .55) * math.sin(t)) for t in np.linspace(math.radians(122), math.radians(238), 40)] +
                        [(sx + (r1 - .1) * math.cos(t), sy + (r1 - .1) * math.sin(t)) for t in np.linspace(math.radians(238), math.radians(122), 40)]).intersection(hall)
        flat_region(clay, 'seats', seats, z + .45)
        for poly in getattr(tier, 'geoms', [tier]):
            if poly.geom_type == 'Polygon':
                ring = list(poly.exterior.coords)[:-1]
                for p, q in zip(ring, ring[1:] + ring[:1]):
                    if math.hypot((p[0] + q[0]) / 2 - sx, (p[1] + q[1]) / 2 - sy) < r0 + .05:
                        clay.quad('hall', (p[0], p[1], z - .42), (q[0], q[1], z - .42), (q[0], q[1], z), (p[0], p[1], z), facing=(sx - p[0], sy - p[1], 0))


# ---- the roof garden ---------------------------------------------------------------------------------
def meander(line, amplitude, waves, closed=True, step=.5):
    """A line displaced sideways by a sine wave of `waves` periods along its length."""
    n = max(16, round(line.length / step))
    pts = []
    for k in range(n + (0 if closed else 1)):
        d = line.length * k / n
        (x, y) = line.interpolate(d).coords[0]
        (x2, y2) = line.interpolate(min(d + .3, line.length) if not closed else (d + .3) % line.length).coords[0]
        if (x2, y2) == (x, y):
            (x2, y2), (x, y) = (x, y), line.interpolate(d - .3).coords[0]
        length = math.hypot(x2 - x, y2 - y) or 1.0
        nx, ny = (y2 - y) / length, -(x2 - x) / length
        off = amplitude * math.sin(2 * math.pi * waves * k / n) * (1 if closed else math.sin(math.pi * k / n))
        pts.append((line.interpolate(d).coords[0][0] + nx * off, line.interpolate(d).coords[0][1] + ny * off))
    return LineString(pts + pts[:1] if closed else pts)


def roof_garden(clay, shells, stair):
    deck = Polygon(podium_ring(.6)).buffer(0)
    cx, cy = OCULUS_C
    oculus = Polygon([(cx + (OCULUS_AB[0] + LIP_W) * math.cos(t), cy + (OCULUS_AB[1] + LIP_W) * math.sin(t))
                      for t in np.linspace(0, 2 * math.pi, 96, endpoint=False)])
    blocked = shapely.union_all(shells + [oculus, stair])
    inner_bound = shapely.union_all(shells + [oculus]).buffer(2.4)
    outer_bound = Polygon(podium_ring(3.4))
    loop_pts = []
    for k, t in enumerate(np.arange(0.0, 360.0, 1.5)):                   # rays from the oculus: the loop runs midway, winding
        u = (math.cos(math.radians(t)), math.sin(math.radians(t)))
        ray = LineString([(cx, cy), (cx + 90 * u[0], cy + 90 * u[1])])
        hit = ray.intersection(inner_bound)
        r1 = max((math.hypot(x - cx, y - cy) for g in getattr(hit, 'geoms', [hit]) for x, y in g.coords), default=lip_r(t))
        r2 = ray.intersection(outer_bound).length
        amp = max(0.0, min(3.4, (r2 - r1) / 2 - 1.3))
        r = (r1 + r2) / 2 + amp * math.sin(math.radians(t) * 8 + .6)
        loop_pts.append((cx + r * u[0], cy + r * u[1]))
    loop = LineString(loop_pts + loop_pts[:1]).simplify(.05)
    paths = [loop.buffer(1.0, quad_segs=6)]
    # an outer walk along the south-west edge, from the roof-garden entrance round to the front
    edge = podium_ring(5.2, step=.8)
    arc = LineString([p for p in edge if in_range(polar_deg(*p), 196, 292)])
    walk = meander(arc, 1.3, 4, closed=False)
    paths.append(walk.buffer(.8, quad_segs=6))
    for end in (walk.coords[0], walk.coords[-1]):
        near = loop.interpolate(loop.project(Point(end)))
        paths.append(LineString([end, near.coords[0]]).buffer(.8, quad_segs=6))
    # spurs to the viewing ledge at the oculus' south-east and to the roof-garden entrance
    gap_t = math.radians(305)
    ledge = (cx + (lip_r(305) + .4) * math.cos(gap_t), cy + (lip_r(305) + .4) * math.sin(gap_t))
    near = loop.interpolate(loop.project(Point(ledge)))
    paths.append(LineString([ledge, near.coords[0]]).buffer(1.0, quad_segs=6))
    sc = stair.centroid
    near = loop.interpolate(loop.project(sc))
    paths.append(LineString([sc.coords[0], near.coords[0]]).buffer(1.0, quad_segs=6))
    path = shapely.union_all(paths).intersection(deck.buffer(-1.6)).difference(blocked)
    ground = deck.difference(blocked).difference(path)
    flat_region(clay, 'roofdeck', ground, ROOF)
    flat_region(clay, 'path', path, ROOF + .03)
    # planting: drifts of grasses, perennials and low shrubs, kept off the paths and back from the guard
    rng = np.random.default_rng(2402)
    keep = prep(ground.buffer(-.6))
    clear = prep(path.buffer(.5))

    def mound(role, x, y, radius, height, sides):
        ring = [(x + radius * math.cos(2 * math.pi * k / sides), y + radius * math.sin(2 * math.pi * k / sides), ROOF) for k in range(sides)]
        for k in range(sides):
            clay.tri(role, ring[k], ring[(k + 1) % sides], (x, y, ROOF + height), facing=(ring[k][0] - x, ring[k][1] - y, 1))
    placed = {'mounds': 0, 'blooms': 0}
    drifts = [(rng.uniform(-PODIUM_A, PODIUM_A), rng.uniform(-PODIUM_B, PODIUM_B), 'meadow' if rng.random() < .5 else 'planting') for _ in range(40)]
    for _ in range(20000):
        x, y = rng.uniform(-PODIUM_A, PODIUM_A), rng.uniform(-PODIUM_B, PODIUM_B)
        if not keep.contains(Point(x, y)) or clear.contains(Point(x, y)):
            continue
        drift = drifts[min(range(len(drifts)), key=lambda i: (drifts[i][0] - x) ** 2 + (drifts[i][1] - y) ** 2)][2]
        if placed['mounds'] < 2600:
            pick = rng.random()
            role = drift if pick < .7 else 'planting' if pick < .9 else 'shrub'
            mound(role, x, y, rng.uniform(.45, 1.0), rng.uniform(.25, .6) * (1.6 if role == 'shrub' else 1), 7)
            placed['mounds'] += 1
            if drift == 'meadow' and rng.random() < .45 and placed['blooms'] < 900:
                mound('blossom', x + rng.uniform(-.6, .6), y + rng.uniform(-.6, .6), rng.uniform(.3, .45), rng.uniform(.45, .65), 6)
                placed['blooms'] += 1
        else:
            break
    return path


def shell_entrance(clay):
    """Roof-garden entrance: a vestibule in the foot of the west shell, leading to a lift and stair inside it."""
    cx, cy = OCULUS_C
    t = math.radians(ROOF_DOOR)
    r_foot = catmull(SHELL_A, ROOF_DOOR)[0]
    nx, ny = math.cos(t), math.sin(t)
    ux, uy = -ny, nx
    x, y = cx + (r_foot + .2) * nx, cy + (r_foot + .2) * ny
    obox(clay, 'shellwall', x, y, ux, uy, 2.0, 1.4, ROOF, ROOF + 3.2)
    obox(clay, 'lip', x + nx * .15, y + ny * .15, ux, uy, 2.2, 1.6, ROOF + 3.2, ROOF + 3.45)
    obox(clay, 'door', x + nx * 1.42, y + ny * 1.42, ux, uy, 1.3, .03, ROOF, ROOF + 2.7)
    corners = [(x + su * 2.0 * ux + sv * 1.4 * nx, y + su * 2.0 * uy + sv * 1.4 * ny) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Polygon(corners).buffer(.3)


def build():
    clay = Clay()
    podium(clay)
    interiors(clay)
    shells = [shell(clay, SHELL_A, inner=west_inner, start=.3), shell(clay, SHELL_B)]
    under_ring(clay)
    oculus_and_hall(clay)
    stair = shell_entrance(clay)
    roof_garden(clay, shells, stair)
    return clay


# ---- records -----------------------------------------------------------------------------------------
def door_point(angle):
    """Where a podium polar angle meets the ground-floor glazing (authoring frame)."""
    glass = podium_ring(GLASS_SET)
    return min(glass, key=lambda p: abs(((polar_deg(*p) - angle + 180) % 360) - 180))


def entrances():
    """Every door, from the model's own numbers. The foyer floor is FOYER above the 0.02 m apron."""
    doors = []
    for kind, d in (('main doors', ENTRANCE), ('east doors', EAST_DOOR)):
        x, y = door_point(d['angle'])
        doors.append({'kind': kind, 'centre_xy_m': [round(x, 3), round(y, 3)], 'facing_deg': d['angle'], 'leaves': None,
                      'clear_width_m': d['width'], 'door_height_m': round(2.7 - FOYER, 2), 'threshold_top_m': FOYER, 'rise_m': round(FOYER - .02, 3)})
    glass = podium_ring(GLASS_SET)
    for door in doors:
        angle = ENTRANCE['angle'] if door['kind'] == 'main doors' else EAST_DOOR['angle']
        door['leaves'] = sum(1 for p in glass if abs(((polar_deg(*p) - angle + 180) % 360) - 180) <
                             math.degrees((ENTRANCE if door['kind'] == 'main doors' else EAST_DOOR)['width'] / 2 / math.hypot(*p)))
    x, y = door_point(sum(LOADING) / 2)
    doors.append({'kind': 'service door', 'centre_xy_m': [round(x, 3), round(y, 3)], 'facing_deg': sum(LOADING) / 2, 'leaves': 1,
                  'clear_width_m': 4.8, 'door_height_m': 4.2, 'threshold_top_m': 0.0, 'rise_m': 0.0})
    return doors


def programme():
    """Seat and tier counts of the auditorium, measured from the seat strips."""
    clay = Clay()
    oculus_and_hall(clay)
    length = 0.0
    for a, b, c in (t[:3] for t in clay.triangles.get('seats', [])):
        area = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
        length += area / .45
    return {'tiers': 11, 'balcony_rings': 2, 'stalls_seats_estimate': int(length / .55), 'stage_floor_m': 2.1,
            'note': 'Schematic: a seat every 0.55 m along 0.45 m strips. Balcony seating is not drawn.'}



def source_lock_for(role, files=SOURCES):
    path = ROOT / SOURCE_DIR / files[role]
    data = path.read_bytes()
    lock = {'role': role, 'repo_path': f'{SOURCE_DIR}/{files[role]}', 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        fields = dict(line.split(' ', 1) for line in data.decode('ascii').splitlines() if ' ' in line)
        lock.update(bytes=int(fields['size']), sha256=fields['oid'].removeprefix('sha256:'))
    return lock


CAMERAS = ('front', 'front_corner', 'aerial', 'top', 'left_side', 'right_side', 'rear', 'rear_side', 'facade_close', 'architecture_close',
           'glass_close', 'oculus_program', 'roof_garden', 'notch_contact', 'lip_contact', 'match_oblique', 'match_top')


def prework(candidate):
    return {
        'candidate': candidate, 'method': METHOD, 'archetype_id': ARCHETYPE, 'variant_id': VARIANT, 'title': TITLE,
        'sources': [source_lock_for(r) for r in SOURCES], 'excluded_sources': [source_lock_for('front', EXCLUDED) | {'reason': 'grey preview of the old LEGO model'}],
        'gate_a': {'front_oblique_top_coherent': False,
                   'note': ('The variant has no usable street view: variant_2.png has the same bytes as the old LEGO family preview '
                            '(hash prefix b33e3a3378be). The oblique and roof views agree and are the authority. A person must rule '
                            'on this before activation, as for the crescent and the laneway.')},
        'measurement_contract': {
            'scale_basis': ('No image carries a scale. The podium outline in the roof view (888 by 650 px) is set to 88 by 64.4 m, '
                            "matching the archetype's suggested 90 by 65 m footprint and 1.4:1 aspect. Plan positions are measured "
                            'in the roof view at 0.0991 m/px. Heights: a pinhole camera fitted to 39 traced podium points in the '
                            'oblique (31 px RMS) barely changes between an 11 m and a 21 m podium, so the podium takes the '
                            "catalogue's two 5 m floors (glazed ground floor to 6.0 m, finned band to 11.2 m). The shell rims are "
                            'set from the same fit, peaking near 23.6 m (west) and 21.6 m (east).'),
            'source_measurements': {
                'oblique': ['High view from the south over the front plaza toward the water and mountains.',
                            ('Rounded podium wrapped in close vertical bronze fins above a glazed ground floor with cafe tables '
                             'inside; the glazing is about as tall as the band; a horizontal window slot in the band at the west end.'),
                            'Planted roof garden with winding pale paths and a thin dark edge.',
                            ('Two opposing curved shells clad in bronze battens, their outer walls leaning in: the west shell rises '
                             'highest at the north-west, the east shell at the north-east; their rims meet in a V at the back.'),
                            ('Inside the west shell a narrow sloping ring runs round the oculus below its stepped inner edge: the '
                             'east sheet continuing underneath.'),
                            'An oval oculus between them shows the auditorium: timber walls, raked seating, balcony fronts and a stage.'],
                'top': ['Near-nadir view, north up, the pier to the west and south.',
                        'Podium a rounded rectangle about 888 by 650 px; roof garden with a winding path loop and planting.',
                        ('Shells spiral round an oval oculus about 235 by 185 px, centred 114 px east of the podium centre: the '
                         'west shell wraps west and south, the east shell north-east and east; a radial notch at the north.'),
                        'Inside the oculus, seating rows on the west half facing a dark stage on the east.']},
            'source_conflicts': [('variant_2.png, the street view, is the grey preview of the old LEGO model, not a picture of this '
                                  'building. It is excluded; the oblique and roof views govern. Needs a ruling by a person.'),
                                 ('The oblique puts the oculus about 3.5 m east of the podium centre, the roof view 11.3 m. The roof '
                                  'view governs plan positions; the oblique governs heights.'),
                                 ('The catalogue text says "two opposing curved planes in weathered bronze-tone metal with landscaped '
                                  'rooftop terrace". The images agree; the title "Timber Acoustic" refers to the interior and battens.')],
            'hidden_assumptions': [('The north and east elevations are seen only obliquely or from above; their ground floor continues '
                                    'the glazing, with an opaque back-of-house and a service door at the north-east (inferred).'),
                                   'The oculus is glazed (clear) so the hall is closed; the images show its interior without glass reflections.',
                                   ('Roof access is a lift and stair inside the west shell, entered from the roof garden through a '
                                    'vestibule at its south-west foot (inferred; no access is visible in the images).'),
                                   ('Interiors are schematic: a foyer with cafe tables, counters, a stair and columns round the hall '
                                    'drum; upper rooms behind the ribbon window; the auditorium, only as large as the oculus, with 11 '
                                    'raked tiers (about 340 stalls seats), two balcony rings, a stage and choir terraces.'),
                                   ('The pier, the stepped terrace to the west, the water, boats, cars and people belong to the site '
                                    'and are not modelled.')]},
        'roof_contract': {'form': ('two spiral sheets about an oval oculus, rising from its lip to high outer rims, with outer walls '
                                   'leaning in to the roof garden; the east sheet runs on under the west as a ring on the lip, and the '
                                   'west sheet steps up over it at the north notch'),
                          'weathering': 'each sheet is one closed surface with standing seams; the lip and oculus glazing close the centre'},
        'material_contract': {'profile': 'texture-free source-palette architectural clay', 'generic_texture_fallback': False,
                              'roles': {role: settings['colour'] for role, settings in PALETTE.items()}},
        'identity_contract': ['rounded-rectangle podium, about 1.37:1, wrapped in close vertical bronze fins over a recessed glazed ground floor',
                              'planted roof garden with a winding path loop', 'two opposing spiral shells clad in bronze battens',
                              'a stepped notch where the shells meet at the north', 'an oval oculus revealing raked seating and a stage'],
        'programme_contract': {'auditorium': 1, 'foyer': 1, 'roof_garden': 1},
        'contact_contract': {'base_datum_m': 0.0, 'ground': 'a 6 m plaza apron round the podium; nothing below grade'},
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
        'storeys': 2,
        'entrances': {'doors': entrances(), 'roof_garden_entrance_deg': ROOF_DOOR},
        'auditorium': programme(),
    }
    (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'prework-manifest.json').write_text(json.dumps(prework(candidate), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate': candidate, 'native_dimensions_m': report['native_dimensions_m'], 'triangles': report['model']['triangles'],
                      'bytes': len(data), 'sha256': report['model']['sha256']}))


if __name__ == '__main__':
    main()
