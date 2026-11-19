"""Stormwater Pond & Pathway Loop: an original native park pilot for Calgary classrooms.

A small Calgary-style wet pond after the catalogue's stormwater retention pond
references (frontend/public/archetypes/openspaces/stormwater-retention-pond/),
scaled up from their garden-sized pond to a neighbourhood stormwater facility.

Pure Python with numpy; no Blender and no paid calls. Writes one self-contained
assembly GLB with the material names the park runtime reads: `paving`, `grass`
and `deck` are walkable, `water` is a hazard, plant materials never form walls.
Each repeated plant is one mesh placed by many nodes.

Usage:
  python3 tools/stormwater_pond_park/build.py --output <new directory>
  python3 tools/stormwater_pond_park/build.py --dry-run
The output directory must not exist: a candidate is never overwritten.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import struct
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KIT = ROOT / 'tools' / 'detail_catalogue'
sys.path.insert(0, str(KIT))
import build_local_foliage as foliage  # noqa: E402
from calgary_kit import Solid  # noqa: E402

_spec = importlib.util.spec_from_file_location('calgary_details_for_pond', KIT / 'build_calgary_details.py')
calgary = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calgary)

PARK_ID = 'student_stormwater_pond_v1'
TITLE = 'Stormwater Pond & Pathway Loop'
GENERATOR = 'CityPrompt stormwater pond park builder v1'

# ---- measured contract (metres; x east, y north, z up) ------------------------------
SITE_W, SITE_D = 86.0, 68.0
CENTRE = (0.0, 3.0)                  # middle of the pond
POND_A, POND_B = 23.0, 13.5          # half length and half width of the normal water level
SAMPLES = 180
WATER_Z = -.45                       # normal water level below the surrounding grade
MUD, BANK = .5, 3.2                  # wet margin, then a 1:7 grassed bank up to grade
SHELF = (-2.6, -.4)                  # planted shallow shelf, inside the water's edge
PATH_IN, PATH_OUT = 9.5, 12.5        # 3 m regional-style asphalt loop, as offsets from the water's edge
SHOULDER = .25
PAVE_Z = .02
DECK_Z = .17
ENTRANCE = dict(x=0, y=-34, widthM=3, arrivalY=-31)
INLET_T, OUTLET_T = 2.55, .15        # where the storm sewer comes in and the control structure lets water out
BENCH_T = (.8, 2.05, 3.85, 5.5)
DOCK_T = -math.pi / 2


# ---- the pond outline and its offsets ---------------------------------------------------
def wobble(t):
    return 1 + .05 * math.sin(3 * t + .4) + .03 * math.cos(5 * t)


def pond_point(t):
    f = wobble(t)
    return (CENTRE[0] + POND_A * math.cos(t) * f, CENTRE[1] + POND_B * math.sin(t) * f)


def outward(t):
    e = 1e-4
    (ax, ay), (bx, by) = pond_point(t - e), pond_point(t + e)
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    return (dy / length, -dx / length)


ANGLES = [math.tau * i / SAMPLES for i in range(SAMPLES)]


def offset_at(t, d):
    (x, y), (nx, ny) = pond_point(t), outward(t)
    return (x + nx * d, y + ny * d)


def ring(d):
    return [offset_at(t, d) for t in ANGLES]


def angle_gap(a, b):
    return abs((a - b + math.pi) % math.tau - math.pi)


# ---- parts: one named material each ------------------------------------------------------
MATERIALS = {
    'grass': dict(roughness=.95), 'paving': dict(roughness=.9), 'gravel': dict(roughness=.97), 'mud': dict(roughness=.8),
    'water': dict(roughness=.55), 'deck': dict(roughness=.82), 'timber': dict(roughness=.82), 'concrete': dict(roughness=.9),
    'rock': dict(roughness=.95), 'metal': dict(roughness=.5, metallic=.3), 'furniture': dict(roughness=.7),
    'foliage': dict(roughness=.9), 'wood': dict(roughness=.92), 'fauna': dict(roughness=.85),
}


class Parts:
    """A Solid per material, all drawn in the same frame."""

    def __init__(self, seed):
        self.solids = {name: Solid(seed + k) for k, name in enumerate(MATERIALS)}
        self.random = random.Random(seed).random

    def __getitem__(self, name):
        return self.solids[name]


def mottle(x, y, seed=0.0):
    """Smooth value in 0..1 from position: gentle patches, never stripes."""
    v = (math.sin(.37 * x + 1.3 + seed) * math.sin(.29 * y - .7 + seed) * .45 + math.sin(.11 * x - .13 * y + seed) * .3
         + math.sin(1.07 * x + .61 * y + 2 * seed) * .15 + math.sin(2.3 * x - 1.7 * y + seed) * .1)
    return .5 + .5 * max(-1.0, min(1.0, v))


def linear(hex_colour):
    return foliage.srgb_to_linear(hex_colour)


SURFACES = {   # (low, high) colours blended by mottle; each vertex gets its own, so faces never stripe
    'lawn': ('#5f8a3c', '#78a04b'), 'meadow': ('#7b8a44', '#929a52'), 'bank': ('#6f8143', '#829150'),
    'asphalt': ('#5d5f5e', '#6c6d6a'), 'gravel': ('#9a917f', '#aea592'), 'mud': ('#4f4030', '#62503b'),
}


def shade(surface, x, y):
    low, high = (linear(c) for c in SURFACES[surface])
    m = mottle(x, y, len(surface) * .7)
    return tuple(l + (h - l) * m for l, h in zip(low, high))


def ground_tri(part, a, b, c, colours):
    """One ground triangle with a colour at each corner, wound and lit to face up."""
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    if nz < 0:
        b, c, colours = c, b, (colours[0], colours[2], colours[1])
        nx, ny, nz = -nx, -ny, -nz
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-12:
        return
    part.positions.extend((*a, *b, *c))
    part.normals.extend((nx / length, ny / length, nz / length) * 3)
    for colour in colours:
        part.colors.extend(colour)


def tri_shaded(part, surface, a, b, c):
    """One ground triangle, coloured per vertex from its surface's mottle."""
    ground_tri(part, a, b, c, [shade(surface, p[0], p[1]) for p in (a, b, c)])


def strip(part, surface, inner, outer, z_in, z_out, steps=1):
    """A band between two rings of the same length, split into `steps` rings across."""
    n = len(inner)
    for k in range(steps):
        f0, f1 = k / steps, (k + 1) / steps
        za, zb = z_in + (z_out - z_in) * f0, z_in + (z_out - z_in) * f1
        for i in range(n):
            j = (i + 1) % n
            a = (inner[i][0] + (outer[i][0] - inner[i][0]) * f0, inner[i][1] + (outer[i][1] - inner[i][1]) * f0, za)
            b = (inner[j][0] + (outer[j][0] - inner[j][0]) * f0, inner[j][1] + (outer[j][1] - inner[j][1]) * f0, za)
            c = (inner[j][0] + (outer[j][0] - inner[j][0]) * f1, inner[j][1] + (outer[j][1] - inner[j][1]) * f1, zb)
            d = (inner[i][0] + (outer[i][0] - inner[i][0]) * f1, inner[i][1] + (outer[i][1] - inner[i][1]) * f1, zb)
            tri_shaded(part, surface, a, b, c)
            tri_shaded(part, surface, a, c, d)


def rectangle_projection(points):
    """Each ring point pushed out from the pond's middle to the site edge."""
    hx, hy = SITE_W / 2, SITE_D / 2
    out = []
    for x, y in points:
        dx, dy = x - CENTRE[0], y - CENTRE[1]
        scale = min((hx - CENTRE[0] * (dx > 0) + CENTRE[0] * (dx < 0)) / abs(dx) if dx else 1e9,
                    ((hy - CENTRE[1]) if dy > 0 else (hy + CENTRE[1])) / abs(dy) if dy else 1e9)
        out.append((CENTRE[0] + dx * scale, CENTRE[1] + dy * scale))
    return out


def edge_of(p):
    hx, hy = SITE_W / 2, SITE_D / 2
    x, y = p
    if abs(x - hx) < 1e-6:
        return 'e'
    if abs(x + hx) < 1e-6:
        return 'w'
    return 'n' if y > 0 else 's'


CORNER = {('e', 'n'): (1, 1), ('n', 'w'): (-1, 1), ('w', 's'): (-1, -1), ('s', 'e'): (1, -1)}


def water_surface(parts):
    """The water: one plane, darker toward the middle, in smooth rings. Nothing lies on anything else."""
    w = parts['water'].body
    deep, shallow = linear('#3b6668'), linear('#5f8e84')
    rings = [(.4, 1.0), (.62, .78), (.8, .5), (.92, .22), (1.0, 0.0)]     # fractions of the way out to the edge
    centre = (*CENTRE, WATER_Z)
    edge = ring(0)

    def toward(f):
        return [(CENTRE[0] + (x - CENTRE[0]) * f, CENTRE[1] + (y - CENTRE[1]) * f) for x, y in edge]

    def colour(depth_share, x, y):
        m = mottle(x, y, 3.1) * .12
        return tuple(s + (d - s) * min(1.0, depth_share + m) for d, s in zip(deep, shallow))

    first = toward(rings[0][0])
    for i in range(SAMPLES):
        j = (i + 1) % SAMPLES
        pts = [(centre, 1.0), ((*first[i], WATER_Z), rings[0][1]), ((*first[j], WATER_Z), rings[0][1])]
        ground_tri(w, *(p for p, _ in pts), [colour(share, p[0], p[1]) for p, share in pts])
    for (d0, s0), (d1, s1) in zip(rings, rings[1:]):
        inner, outer = toward(d0), toward(d1)
        for i in range(SAMPLES):
            j = (i + 1) % SAMPLES
            quad = [((*inner[i], WATER_Z), s0), ((*inner[j], WATER_Z), s0), ((*outer[j], WATER_Z), s1), ((*outer[i], WATER_Z), s1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                ground_tri(w, *(quad[k][0] for k in tri), [colour(quad[k][1], quad[k][0][0], quad[k][0][1]) for k in tri])


def site_ground(parts):
    body = {name: parts[name].body for name in ('mud', 'grass', 'gravel', 'paving')}
    strip(body['mud'], 'mud', ring(0), ring(MUD), WATER_Z, -.38)
    strip(body['grass'], 'bank', ring(MUD), ring(BANK), -.38, 0.0, steps=3)
    strip(body['grass'], 'meadow', ring(BANK), ring(PATH_IN - SHOULDER), 0.0, 0.0, steps=4)
    strip(body['gravel'], 'gravel', ring(PATH_IN - SHOULDER), ring(PATH_IN), 0.0, 0.0)
    strip(body['gravel'], 'gravel', ring(PATH_OUT), ring(PATH_OUT + SHOULDER), 0.0, 0.0)
    inner, outer = ring(PATH_IN), ring(PATH_OUT)
    strip(body['paving'], 'asphalt', inner, outer, PAVE_Z, PAVE_Z, steps=2)
    kerb = parts['paving']
    for ring_points in (inner, outer):
        n = len(ring_points)
        for i in range(n):
            (ax, ay), (bx, by) = ring_points[i], ring_points[(i + 1) % n]
            kerb.quad((ax, ay, 0.0), (bx, by, 0.0), (bx, by, PAVE_Z), (ax, ay, PAVE_Z), kerb.c('#626361'))
    # mown lawn out to the site edge in several rings, with the four corners filled
    edge = ring(PATH_OUT + SHOULDER)
    rect = rectangle_projection(edge)
    strip(body['grass'], 'lawn', edge, rect, 0.0, 0.0, steps=6)
    for i in range(SAMPLES):
        j = (i + 1) % SAMPLES
        e0, e1 = edge_of(rect[i]), edge_of(rect[j])
        if e0 != e1:
            sx, sy = CORNER[(e0, e1)]
            corner = (sx * SITE_W / 2, sy * SITE_D / 2, 0.0)
            tri_shaded(body['grass'], 'lawn', (*rect[i], 0.0), (*rect[j], 0.0), corner)
    water_surface(parts)


# ---- paths, dock and furniture -------------------------------------------------------------
def loop_south_y():
    return offset_at(DOCK_T, PATH_OUT)[1]


def spur(parts):
    """The entrance path from the site's south edge to the loop, 20 mm proud of the lawn."""
    s = parts['paving']
    # it runs 5 cm under the loop's edge, 5 mm lower, so no two paved faces share a plane
    y0, y1 = -SITE_D / 2, offset_at(DOCK_T, PATH_OUT)[1] + .05
    top = PAVE_Z - .005
    s.box((0, (y0 + y1) / 2, top / 2), (3.0, y1 - y0, top), '#666764')


def dock_span():
    start = offset_at(DOCK_T, PATH_IN)[1]
    shore = offset_at(DOCK_T, 0)[1]
    return start, shore, shore + 5.5


def dock(parts):
    """A railed timber viewing dock from the loop out over the water, with a wider end."""
    deck, frame = parts['deck'], parts['timber']
    start, shore, end = dock_span()
    ramp_end = start + 1.4
    deck.quad((-1.2, start, PAVE_Z), (1.2, start, PAVE_Z), (1.2, ramp_end, DECK_Z), (-1.2, ramp_end, DECK_Z), '#9a7a55')
    for sx in (-1, 1):                       # the ramp's side faces
        deck.tri((sx * 1.2, start, 0.0), (sx * 1.2, ramp_end, DECK_Z), (sx * 1.2, ramp_end, 0.0), '#7d6244')
    y = ramp_end
    colours = ['#9a7a55', '#a1805a', '#93744f', '#9c7c56']
    k = 0
    platform = end - 3.5
    # a filled layer under the boards, so the joints between them are never holes underfoot
    deck.box((0, (ramp_end + platform) / 2, DECK_Z - .027), (2.36, platform - ramp_end, .03), '#5c4632')
    deck.box((0, (platform + end) / 2, DECK_Z - .027), (3.96, end - platform, .03), '#5c4632')
    while y < end - 1e-6:
        step = min(.15, end - y)
        width = 2.4 if y < platform else 4.0
        deck.box((0, y + step / 2, DECK_Z - .02), (width, step - .012, .04), colours[k % 4])
        y += step
        k += 1
    for sx in (-1, 1):                       # stringers and posts down into the water
        frame.box((sx * 1.05, (ramp_end + platform) / 2, DECK_Z - .14), (.08, platform - ramp_end, .2), '#6c5339')
        yy = ramp_end + .6
        while yy < platform:
            z0 = -.9 if yy > shore - .3 else -.2
            frame.cyl((sx * 1.05, yy, z0), (sx * 1.05, yy, DECK_Z - .04), .07, '#5f4a34', sides=6)
            yy += 2.0
    for x in (-1.85, 1.85):
        for yy in (platform + .2, end - .2):
            frame.cyl((x, yy, -.9), (x, yy, DECK_Z - .04), .08, '#5f4a34', sides=6)
    frame.box((0, platform + 1.75, DECK_Z - .14), (3.8, .08, .2), '#6c5339')
    # railings: along both sides over the bank and water, and round the end platform
    rail_from = shore - 3.2
    runs = [((-1.2, rail_from), (-1.2, platform)), ((1.2, rail_from), (1.2, platform)), ((-2.0, platform), (-2.0, end)),
            ((2.0, platform), (2.0, end)), ((-2.0, end), (2.0, end)), ((-2.0, platform), (-1.2, platform)), ((1.2, platform), (2.0, platform))]
    for (ax, ay), (bx, by) in runs:
        length = math.hypot(bx - ax, by - ay)
        count = max(1, round(length / 1.5))
        for i in range(count + 1):
            x, y = ax + (bx - ax) * i / count, ay + (by - ay) * i / count
            frame.box((x, y, DECK_Z + .53), (.09, .09, 1.06), '#7a5d40')
        for z, size in ((DECK_Z + 1.05, .07), (DECK_Z + .55, .05)):
            frame.box(((ax + bx) / 2, (ay + by) / 2, z), (abs(bx - ax) + size, abs(by - ay) + size, size), '#8a6a49')


def bench(parts, x, y, facing):
    """A backed timber bench on a small concrete pad, facing the water."""
    yaw = math.atan2(facing[1], facing[0]) + math.pi / 2     # local -y, the sitter's view, turned to face the water
    pad, wood, metal = parts['paving'], parts['furniture'], parts['metal']
    with pad.at(x, y, 0, yaw=yaw):
        pad.box((0, -.05, PAVE_Z / 2), (2.4, 1.9, PAVE_Z), '#8e8a82')     # reaches back to the loop's edge
    with wood.at(x, y, 0, yaw=yaw):
        for k in range(4):
            wood.box((0, .08 + k * .1, .45), (1.8, .085, .04), '#8a6644')
        for k in range(3):
            wood.box((0, .46, .58 + k * .12), (1.8, .03, .085), '#8a6644')
    with metal.at(x, y, 0, yaw=yaw):
        for sx in (-.75, .75):
            metal.box((sx, .2, .22), (.06, .5, .44), '#2d3133')
            metal.box((sx, .47, .56), (.06, .04, .36), '#2d3133')


def sign(parts, x, y, yaw):
    """An interpretive panel on two posts; its face is left blank."""
    frame, panel = parts['metal'], parts['furniture']
    with frame.at(x, y, 0, yaw=yaw):
        for sx in (-.45, .45):
            frame.box((sx, 0, .5), (.08, .08, 1.0), '#2d3133')
    with panel.at(x, y, 0, yaw=yaw):
        with panel.at(0, 0, .95, pitch=-.55):
            panel.box((0, 0, 0), (1.2, .05, .7), '#2f4a46', top='#d8d2bd')


def waste_bin(parts, x, y):
    parts['metal'].cyl((x, y, 0), (x, y, .95), .3, '#2f4b35', sides=10)
    parts['metal'].cyl((x, y, .95), (x, y, 1.0), .33, '#263c2b', sides=10)


# ---- stormwater structures ------------------------------------------------------------------
def rip_rap(parts, t, d0, d1, half, count, seed):
    rng = random.Random(seed)
    s = parts['rock']
    (nx, ny) = outward(t)
    tx, ty = -ny, nx
    for _ in range(count):
        d = d0 + rng.random() * (d1 - d0)
        u = (rng.random() * 2 - 1) * half * (1 - .3 * rng.random())
        x, y = offset_at(t, d)
        x, y = x + tx * u, y + ty * u
        z = WATER_Z if d <= 0 else (WATER_Z + .07 + (d - MUD) * .38 / (BANK - MUD) if d > MUD else WATER_Z + d / MUD * .07)
        size = (.35 + rng.random() * .35, .3 + rng.random() * .3, .22 + rng.random() * .2)
        s.rock(size, 3, ['#8a8780', '#7b7972', '#95928a', '#6f6d67'], origin=(x, y, min(z, 0) - .06), yaw=rng.random() * math.tau)


def inlet(parts):
    """The storm sewer outfall: a concrete headwall in the bank with its pipe, over a rip-rap apron."""
    (nx, ny) = outward(INLET_T)
    yaw = math.atan2(ny, nx) - math.pi / 2
    x, y = offset_at(INLET_T, 1.6)
    with parts['concrete'].at(x, y, 0, yaw=yaw):
        parts['concrete'].box((0, 0, -.12), (4.2, .45, 1.0), '#b8b4aa')
        for sx in (-2.0, 2.0):
            parts['concrete'].box((sx, -.8, -.25), (.35, 1.6, .7), '#b3afa5')
    with parts['metal'].at(x, y, 0, yaw=yaw):
        with parts['metal'].at(0, -.23, -.15, pitch=math.pi / 2):
            parts['metal'].disc((0, 0, 0), .42, '#1f2123', sides=16)
    rip_rap(parts, INLET_T, -1.6, 1.3, 2.4, 26, 7)


def outlet(parts):
    """The outlet control structure: a concrete box at the water's edge with a steel grate."""
    (nx, ny) = outward(OUTLET_T)
    yaw = math.atan2(ny, nx) - math.pi / 2
    x, y = offset_at(OUTLET_T, .4)
    with parts['concrete'].at(x, y, 0, yaw=yaw):
        parts['concrete'].box((0, 0, -.15), (2.2, 2.2, 1.0), '#b8b4aa')
    with parts['metal'].at(x, y, 0, yaw=yaw):
        parts['metal'].box((0, 0, .36), (1.7, 1.7, .03), '#3a3e40')
        for k in range(-5, 6):
            parts['metal'].box((k * .15, 0, .385), (.025, 1.7, .02), '#2a2d2f')
    rip_rap(parts, OUTLET_T, -1.4, 1.2, 2.2, 18, 11)
    # a gravel maintenance access from the loop to the structure
    s = parts['gravel']
    a, b = offset_at(OUTLET_T, PATH_IN), offset_at(OUTLET_T, 1.6)
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    with s.at((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0, yaw=math.atan2(b[1] - a[1], b[0] - a[0])):
        s.box((0, 0, .008), (length, 3.0, .016), '#a59c8a')


# ---- planting -------------------------------------------------------------------------------
def cattail_clump(seed):
    """Cattails and bulrush: blades and brown spikes from the shallow shelf."""
    s = Solid(seed)
    rng = s.random
    blade = ['#6f8a3c', '#7c9645', '#667f36', '#86a04d', '#8c9a4c']
    for _ in range(34):
        a = rng() * math.tau
        r = rng() ** .7 * .6
        x, y = math.cos(a) * r, math.sin(a) * r
        h = 1.0 + rng() * .75
        lean = (rng() - .5) * .35
        w = .035 + rng() * .02
        top = (x + math.cos(a) * lean, y + math.sin(a) * lean, h)
        colour = blade[int(rng() * 4)]
        s.tri((x - w, y, -.6), (x + w, y, -.6), top, colour)
        s.tri((x, y - w, -.6), (x, y + w, -.6), top, colour)
    for _ in range(6):
        a = rng() * math.tau
        r = rng() * .4
        x, y = math.cos(a) * r, math.sin(a) * r
        h = 1.1 + rng() * .45
        s.cyl((x, y, -.6), (x, y, h + .32), .008, '#6d7f43', sides=3, cap0=False, cap1=False)
        s.cyl((x, y, h), (x, y, h + .22), .028, '#5b3f26', sides=6, cap0=True, cap1=True)
    return s


class Instances:
    """Meshes that are drawn once and placed many times."""

    def __init__(self):
        self.meshes = {}          # name -> (material, Part)
        self.places = []          # (mesh name, x, y, z, yaw, scale)

    def add_plant(self, slug):
        if f'{slug}-foliage' in self.meshes:
            return
        species = next(s for s in foliage.SPECIES if s['slug'] == slug and not s.get('season'))
        plant = foliage.build(species)
        self.meshes[f'{slug}-wood'] = ('wood', plant.wood)
        self.meshes[f'{slug}-foliage'] = ('foliage', plant.foliage)

    def plant(self, slug, x, y, z=0.0, yaw=0.0, scale=1.0):
        self.add_plant(slug)
        for part in ('wood', 'foliage'):
            if self.meshes[f'{slug}-{part}'][1].positions:
                self.places.append((f'{slug}-{part}', x, y, z, yaw, scale))

    def solid(self, name, solid, material):
        self.meshes[name] = (material, solid.body)

    def place(self, name, x, y, z=0.0, yaw=0.0, scale=1.0):
        self.places.append((name, x, y, z, yaw, scale))


def in_band_clear(t, d):
    """Planting keeps clear of the dock, the inlet, the outlet and each lookout."""
    if angle_gap(t, DOCK_T) < .2 and d < PATH_IN + .5:
        return False
    if angle_gap(t, INLET_T) < .28 or angle_gap(t, OUTLET_T) < .26:
        return False
    return all(angle_gap(t, b) > .12 or d < 3.5 for b in BENCH_T)


def planting(inst, parts):
    rng = random.Random(1907)
    for k, seed in enumerate((71, 72, 73)):
        inst.solid(f'cattail-{k}', cattail_clump(seed), 'foliage')
    # cattails on the shallow shelf, in drifts round most of the edge
    t = 0.0
    while t < math.tau:
        if in_band_clear(t, 0) and math.sin(4.0 * t + 1.2) + .45 * math.sin(9.0 * t) > -.15:
            for d in (-.7 - rng.random() * .4, -1.6 - rng.random() * .8):     # two staggered rows make a continuous marsh edge
                x, y = offset_at(t + rng.random() * .02, d)
                inst.place(f'cattail-{int(rng.random() * 3)}', x, y, 0, rng.random() * math.tau, .85 + rng.random() * .3)
        t += .028 + rng.random() * .018
    # laurel-leaf willows lean over the water, as in the references
    for t, d, scale in ((1.15, 4.6, 1.0), (2.05 + .35, 5.2, .9), (3.45, 4.8, 1.05), (4.25, 4.4, .95), (5.75, 4.9, .92)):
        x, y = offset_at(t, d)
        inst.plant('laurel-leaf-willow', x, y, 0, t * 2.1, scale)
    # meadow on the banks: grasses and wildflowers, kept off the paths and structures
    drifts = [('rough-fescue-drift', 'feather-reed-grass'), ('fireweed', 'rough-fescue-drift'), ('goldenrod', 'feather-reed-grass'),
              ('feather-reed-grass', 'rough-fescue-drift'), ('goldenrod', 'fireweed')]
    willows = [offset_at(tt, dd) for tt, dd in ((1.15, 4.6), (2.4, 5.2), (3.45, 4.8), (4.25, 4.4), (5.75, 4.9))]
    for k in range(34):
        t0 = k / 34 * math.tau + rng.random() * .08
        d0 = 4.4 + rng.random() * (PATH_IN - 6.2)
        mix = drifts[k % len(drifts)]
        for j in range(7):
            t, d = t0 + (rng.random() - .5) * .09, d0 + (rng.random() - .5) * 1.8
            x, y = offset_at(t, d)
            if not in_band_clear(t, d) or not 3.6 < d < PATH_IN - .5 or min(math.hypot(x - wx, y - wy) for wx, wy in willows) < 2.2:
                continue
            inst.plant(mix[j % 2 if j < 6 else 0], x, y, 0, rng.random() * math.tau, .85 + rng.random() * .35)
    # shrub groups in the meadow
    shrubs = ['wolf-willow', 'highbush-cranberry', 'snowberry']
    for k, t in enumerate((.45, 1.6, 2.95, 3.25, 4.9, 6.0)):
        for j in range(3):
            tt, d = t + (j - 1) * .07, 6.3 + (j % 2) * 1.1
            if in_band_clear(tt, d):
                x, y = offset_at(tt, d)
                inst.plant(shrubs[(k + j) % 3], x, y, 0, j * 2.3 + k, .95 + .1 * j)
    # aspen groves and white spruce on the lawn, clear of the loop
    for cx, cy in ((-36.5, 26.0), (36.0, 25.5), (37.0, -26.5)):
        for j in range(5):
            a = j * 2.4 + cx
            inst.plant('trembling-aspen', cx + math.cos(a) * (1.4 + j * .5), cy + math.sin(a) * (1.2 + j * .4), 0, a, .85 + (j % 3) * .1)
    for x, y in ((-24.0, 31.0), (-11.0, 31.5), (11.5, 31.0), (24.5, 30.5), (-37.5, -27.5), (-31.0, -30.0), (8.0, -30.5)):
        inst.plant('white-spruce', x, y, 0, x * .3, .8 + (abs(x) % 3) * .08)
    # a pair of Canada geese grazing on the bank
    geese = Solid(2503)
    calgary.canada_geese(geese)
    inst.solid('canada-geese', geese, 'fauna')
    x, y = offset_at(3.95, 3.9)
    inst.place('canada-geese', x, y, 0, 1.0, 1.0)


# ---- GLB --------------------------------------------------------------------------------------
def mesh_arrays(part):
    """Indexed positions, flat normals and colours, Y up. Corners that share all three are merged."""
    p = np.array(part.positions, dtype='<f4').reshape(-1, 3)
    n = np.array(part.normals, dtype='<f4').reshape(-1, 3)
    c = np.array(part.colors, dtype='<f4').reshape(-1, 3)
    p = np.stack([p[:, 0], p[:, 2], -p[:, 1]], axis=1).astype('<f4')
    n = np.stack([n[:, 0], n[:, 2], -n[:, 1]], axis=1).astype('<f4')
    key = np.concatenate([np.round(p, 4), np.round(n, 3), np.round(c, 4)], axis=1)
    unique, inverse = np.unique(key, axis=0, return_inverse=True)
    positions = np.ascontiguousarray(unique[:, :3].astype('<f4'))
    normals = unique[:, 3:6]
    normals = np.ascontiguousarray((normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)).astype('<f4'))
    colours = np.ascontiguousarray(unique[:, 6:].astype('<f4'))
    indices = inverse.reshape(-1).astype('<u4')
    return positions, normals, colours, indices


def write_glb(meshes, nodes):
    """meshes: [(name, material, part)]; nodes: [(mesh index, translation, yaw, scale, name)]."""
    doc = {'asset': {'generator': GENERATOR, 'version': '2.0'}, 'scene': 0, 'scenes': [{'name': PARK_ID, 'nodes': []}],
           'nodes': [], 'meshes': [], 'materials': [], 'accessors': [], 'bufferViews': [], 'buffers': []}
    order = list(MATERIALS)
    for name in order:
        spec = MATERIALS[name]
        doc['materials'].append({'name': name, 'doubleSided': True,
                                 'pbrMetallicRoughness': {'metallicFactor': spec.get('metallic', 0.0), 'roughnessFactor': spec['roughness']}})
    binary = bytearray()

    def view(data, target):
        binary.extend(b'\0' * (-len(binary) % 4))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(data), 'target': target})
        binary.extend(data)
        return len(doc['bufferViews']) - 1

    mesh_triangles = []
    for name, material, part in meshes:
        positions, normals, colours, indices = mesh_arrays(part)
        first = len(doc['accessors'])
        doc['accessors'].append({'bufferView': view(positions.tobytes(), 34962), 'componentType': 5126, 'count': len(positions), 'type': 'VEC3',
                                 'min': [float(v) for v in positions.min(axis=0)], 'max': [float(v) for v in positions.max(axis=0)]})
        doc['accessors'].append({'bufferView': view(normals.tobytes(), 34962), 'componentType': 5126, 'count': len(normals), 'type': 'VEC3'})
        doc['accessors'].append({'bufferView': view(colours.tobytes(), 34962), 'componentType': 5126, 'count': len(colours), 'type': 'VEC3'})
        doc['accessors'].append({'bufferView': view(indices.tobytes(), 34963), 'componentType': 5125, 'count': len(indices), 'type': 'SCALAR'})
        doc['meshes'].append({'name': name, 'primitives': [{'attributes': {'POSITION': first, 'NORMAL': first + 1, 'COLOR_0': first + 2},
                                                            'indices': first + 3, 'material': order.index(material)}]})
        mesh_triangles.append(len(indices) // 3)
    rendered = 0
    for mesh, translation, yaw, scale, name in nodes:
        node = {'name': name, 'mesh': mesh}
        if any(translation):
            node['translation'] = [float(translation[0]), float(translation[2]), float(-translation[1])]
        if yaw:
            node['rotation'] = [0.0, math.sin(yaw / 2), 0.0, math.cos(yaw / 2)]
        if scale != 1:
            node['scale'] = [float(scale)] * 3
        doc['nodes'].append(node)
        doc['scenes'][0]['nodes'].append(len(doc['nodes']) - 1)
        rendered += mesh_triangles[mesh]
    binary.extend(b'\0' * (-len(binary) % 4))
    doc['buffers'].append({'byteLength': len(binary)})
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    payload = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary)) + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
               + struct.pack('<II', len(binary), 0x004E4942) + binary)
    return payload, rendered, len(doc['nodes'])


def build():
    parts = Parts(1907)
    site_ground(parts)
    spur(parts)
    dock(parts)
    for t in BENCH_T:
        (nx, ny) = outward(t)
        x, y = offset_at(t, PATH_IN - .9)
        bench(parts, x, y, (-nx, -ny))
    start, shore, _ = dock_span()
    sign(parts, 2.3, start + .2, 0.0)
    waste_bin(parts, 2.4, -SITE_D / 2 + 3.2)
    x, y = offset_at(OUTLET_T + .3, PATH_OUT + 1.0)
    waste_bin(parts, x, y)
    inlet(parts)
    outlet(parts)
    inst = Instances()
    planting(inst, parts)
    meshes, nodes = [], []
    for name in MATERIALS:
        part = parts[name].body
        if part.positions:
            meshes.append((f'pond_{name}', name, part))
            nodes.append((len(meshes) - 1, (0.0, 0.0, 0.0), 0.0, 1.0, f'pond_{name}'))
    index = {}
    for name, (material, part) in inst.meshes.items():
        if part.positions:
            index[name] = len(meshes)
            meshes.append((name, material, part))
    for k, (name, x, y, z, yaw, scale) in enumerate(inst.places):
        nodes.append((index[name], (x, y, z), yaw, scale, f'{name}-{k}'))
    return meshes, nodes


def clear_routes():
    """The loop's centre line as straight segments, the entrance spur and the dock."""
    mid = (PATH_IN + PATH_OUT) / 2
    fine = [offset_at(math.tau * i / 1440, mid) for i in range(1440)]
    points, start = [fine[0]], 0
    for i in range(2, 1441):          # the longest chords that stay within 4 cm of the path's centre line

        def sag(k, a=start, b=i):
            (ax, ay), (bx, by), (px, py) = fine[a], fine[b % 1440], fine[k]
            length = math.hypot(bx - ax, by - ay)
            return abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) / length
        if max(sag(k) for k in range(start + 1, i)) > .04:
            points.append(fine[i - 1])
            start = i - 1
    routes = [dict(a=[round(a[0], 3), round(a[1], 3)], b=[round(b[0], 3), round(b[1], 3)], width=3.0)
              for a, b in zip(points, points[1:] + points[:1])]
    routes.append(dict(a=[0.0, -SITE_D / 2 + .1], b=[0.0, round(offset_at(DOCK_T, mid)[1], 3)], width=3.0))
    start, _, end = dock_span()
    routes.append(dict(a=[0.0, round(start, 3)], b=[0.0, round(end - .5, 3)], width=2.0))
    return routes


def recipe_for(payload, rendered, instances, lo, hi):
    return {
        'id': PARK_ID, 'title': TITLE, 'dimensions_m': [SITE_W, SITE_D],
        'programme': 'A wet stormwater pond with a planted shallow shelf, grassed 1:7 banks and native meadow; a 3 m asphalt pathway loop; '
                     'a railed timber viewing dock; an inlet headwall and outlet control structure with rip-rap; benches at four lookouts; '
                     'willows, aspen groves and white spruce.',
        'design_basis': 'Original concept after the catalogue stormwater retention pond references, enlarged from their garden-sized pond '
                        'toward a Calgary neighbourhood wet pond. Not a hydraulic or engineered design.',
        'generator': GENERATOR, 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'terrain_policy': 'prepared_level', 'native_scale_only': True,
        'limitations': ['Prepared level ground only. The water sits 0.45 m below grade inside the park; it does not connect to mapped water, '
                        'and nothing here sizes storage or models drainage.',
                        'Real Calgary stormwater ponds are often 1 to 5 ha. This 86 x 68 m park shows the type at a size the catalogue can place.',
                        'Safety signage, fencing decisions, ice safety and maintenance access need site design review.',
                        'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        'clear_routes': clear_routes(), 'tree_wells': [], 'placements': [], 'surface_regions': [],
        'surface_priority': 'Assembly owns its ground: asphalt loop, mown lawn, meadow banks, mud margin and water are one tiled surface.',
        'assembly': {'path': 'assembly-preview.glb', 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()},
        'modules': {}, 'bounds_m': [[round(float(v), 4) for v in lo], [round(float(v), 4) for v in hi]],
        'triangles': rendered, 'mesh_instances': instances, 'render_source': 'reimported GLB', 'runtime_approved': False,
        'axes': 'X east/across; Y north/along; Z up; metres (GLB standard Y-up conversion)',
        'runtime_contract': 'Native assembly at true size on prepared level ground. Walk on paving, grass and deck; the water is a hazard. '
                            'Never stretch the assembly to fit.',
    }


def bounds(meshes, nodes):
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    cache = {}
    for mesh, (tx, ty, tz), yaw, scale, _ in nodes:
        if mesh not in cache:
            cache[mesh] = np.array(meshes[mesh][2].positions).reshape(-1, 3)
        p = cache[mesh] * scale
        c, s = math.cos(yaw), math.sin(yaw)
        # a turn about GLB +Y by yaw is a counter-clockwise turn by yaw in plan
        x, y = p[:, 0] * c - p[:, 1] * s, p[:, 0] * s + p[:, 1] * c
        q = np.stack([x + tx, y + ty, p[:, 2] + tz], axis=1)
        lo, hi = np.minimum(lo, q.min(axis=0)), np.maximum(hi, q.max(axis=0))
    return lo, hi


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if args.dry_run:
        print(json.dumps({'id': PARK_ID, 'dimensions_m': [SITE_W, SITE_D], 'paid_calls': 0, 'blender': False}))
        return
    if not args.output:
        parser.error('--output is required')
    if args.output.exists():
        raise SystemExit(f'{args.output} exists; a candidate is never overwritten')
    meshes, nodes = build()
    payload, rendered, instances = write_glb(meshes, nodes)
    lo, hi = bounds(meshes, nodes)
    args.output.mkdir(parents=True)
    (args.output / 'assembly-preview.glb').write_bytes(payload)
    recipe = recipe_for(payload, rendered, instances, lo, hi)
    (args.output / 'recipe.json').write_text(json.dumps(recipe, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'id': PARK_ID, 'bytes': len(payload), 'sha256': recipe['assembly']['sha256'], 'triangles': rendered,
                      'unique_meshes': len(meshes), 'instances': instances, 'bounds_m': recipe['bounds_m']}))


if __name__ == '__main__':
    main(sys.argv[1:])
