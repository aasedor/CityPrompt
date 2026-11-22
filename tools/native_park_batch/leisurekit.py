"""Leisure pieces for park batch 4: mini golf cups, flags, edging and a starter hut, timber
footbridges, faceted climbing boulders with holds, bee hotels and interpretive lecterns.

A separate file so that the kits recorded in registered parks' source hashes (parkkit.py,
sportskit.py, playkit.py) never change. Everything is drawn in the park frame (x east,
y north, z up). Sizes are typical teaching values, not equipment designs.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

import parkkit as kit

kit.SURFACES.update({
    'putting': ('#3f8a3a', '#47943f'), 'tee_mat': ('#2f3a2c', '#35412f'), 'safety_black': ('#2b2d2e', '#333536'),
    'creek_bed': ('#6d6a5f', '#7a776b'), 'boards': ('#8a6844', '#9a7752'),
})

TIMBER, TIMBER_DARK, SOD = '#8a6844', '#6f5236', '#5c7a3a'


def cup_and_flag(furn, metal, x, y, flag='#c8452f'):
    """A putting cup (a dark disc) with a white flagstick and a small pennant."""
    furn.cyl((x, y, .004), (x, y, .012), .054, '#1c1d1e', sides=12)
    metal.cyl((x, y, 0), (x, y, 1.25), .012, '#f1f0ea', sides=6)
    metal.tri((x, y, 1.25), (x, y, 1.03), (x + .32, y, 1.14), flag)


def timber_edge(timber, region, height=.12, width=.12):
    """A low timber kerb round a putting green or bed (the ring just outside `region`)."""
    ring = region.buffer(width, quad_segs=12).difference(region)
    kit.extrude(timber, TIMBER, ring, 0, height, top_colour='#9a7752')


def footbridge(timber, metal, a, b, width=2.0, deck=.25):
    """A level timber footbridge from a to b, with short ramps at both ends and railings."""
    (ax, ay), (bx, by) = a, b
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    yaw = math.atan2(uy, ux)
    n = int(length / .16)
    for k in range(n):
        s = (k + .5) * length / n
        timber.box((ax + ux * s, ay + uy * s, deck - .03), (.14, width, .06), TIMBER, yaw=yaw)
    for side in (-1, 1):
        ox, oy = -uy * side * (width / 2 - .05), ux * side * (width / 2 - .05)
        timber.box(((ax + bx) / 2 + ox, (ay + by) / 2 + oy, deck - .12), (length, .1, .18), TIMBER_DARK, yaw=yaw)
        for t in np.linspace(.6, length - .6, max(2, int(length / 1.2) + 1)):
            px, py = ax + ux * t + ox, ay + uy * t + oy
            timber.box((px, py, deck + .5), (.09, .09, 1.0), TIMBER_DARK)
        timber.box(((ax + bx) / 2 + ox, (ay + by) / 2 + oy, deck + 1.0), (length - .8, .09, .07), TIMBER, yaw=yaw)


def ramp(part, surface, a, b, width, z0, z1, steps=6):
    """A short sloping walk surface from height z0 at a to z1 at b."""
    (ax, ay), (bx, by) = a, b
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    nx, ny = -uy * width / 2, ux * width / 2
    for k in range(steps):
        t0, t1 = k / steps, (k + 1) / steps
        p0, p1 = (ax + ux * length * t0, ay + uy * length * t0), (ax + ux * length * t1, ay + uy * length * t1)
        za, zb = z0 + (z1 - z0) * t0, z0 + (z1 - z0) * t1
        pts = [(p0[0] - nx, p0[1] - ny, za), (p1[0] - nx, p1[1] - ny, zb), (p1[0] + nx, p1[1] + ny, zb), (p0[0] + nx, p0[1] + ny, za)]
        cols = [kit.shade(surface, p[0], p[1]) for p in pts]
        kit.ground_tri(part, pts[0], pts[1], pts[2], cols[:3])
        kit.ground_tri(part, pts[0], pts[2], pts[3], [cols[0], cols[2], cols[3]])


def sod_hut(timber, grass_solid, x, y, yaw, w=3.4, d=3.0, h=2.5):
    """A small timber starter hut with a counter window and a planted sod roof, facing local +x."""
    with timber.at(x, y, 0, yaw):
        timber.box((0, 0, h / 2), (d, w, h), '#7d5d3f')
        for k in np.arange(.25, h, .3):
            timber.box((d / 2 + .01, 0, k), (.02, w - .1, .04), '#6a4e34')
        timber.box((d / 2 + .02, 0, 1.45), (.03, 1.6, .8), '#2c3a40', gloss=True)
        timber.box((d / 2 + .25, 0, 1.0), (.5, 1.8, .06), TIMBER)
        timber.box((0, 0, h + .08), (d + .6, w + .6, .16), TIMBER_DARK)
    with grass_solid.at(x, y, 0, yaw):
        grass_solid.dome((0, 0, h + .16), ((d + .5) / 2, (w + .5) / 2, .28), SOD, nu=14, nv=4)


# ---- climbing --------------------------------------------------------------------------------------
HOLD_COLOURS = ['#d9472b', '#2f7fc1', '#f2b632', '#3c9b57', '#8b4fb0', '#e8e8e2']


def faceted_boulder(conc, furn, rng, footprint, height, lean=.35, holds=60, shell='#d9d3c6', facet='#c9c2b3'):
    """A faceted concrete bouldering block: its plan polygon rises to a smaller, offset, tilted top,
    so every face leans out or back like a natural boulder; coloured holds dot the faces."""
    poly = shapely.geometry.polygon.orient(footprint, 1.0)
    base = list(poly.exterior.coords)[:-1]
    cx, cy = poly.centroid.x, poly.centroid.y
    top = []
    for i, (x, y) in enumerate(base):
        s = .55 + .15 * math.sin(i * 1.7)
        ox, oy = math.cos(i * 2.3) * lean, math.sin(i * 2.3) * lean
        z = height * (.88 + .12 * math.cos(i * 1.3))
        top.append((cx + (x - cx) * s + ox, cy + (y - cy) * s + oy, z))
    mid = []
    for i, (x, y) in enumerate(base):
        s = 1.08 + .08 * math.cos(i * 2.1)
        mid.append((cx + (x - cx) * s, cy + (y - cy) * s, height * (.45 + .1 * math.sin(i * 1.1))))
    faces = []
    n = len(base)
    for i in range(n):
        j = (i + 1) % n
        b0, b1 = (*base[i], 0.0), (*base[j], 0.0)
        faces.append((b0, b1, mid[j], mid[i]))
        faces.append((mid[i], mid[j], top[j], top[i]))
    for k, f in enumerate(faces):
        colour = shell if k % 3 else facet
        conc.tri(f[0], f[1], f[2], colour)
        conc.tri(f[0], f[2], f[3], colour)
    tc = (sum(p[0] for p in top) / n, sum(p[1] for p in top) / n, max(p[2] for p in top) + .05)
    for i in range(n):
        conc.tri(top[i], top[(i + 1) % n], tc, facet)
    # holds: small blocks scattered over the side faces, never above the top edge
    for _ in range(holds):
        f = faces[rng.randrange(len(faces))]
        u, v = rng.uniform(.1, .9), rng.uniform(.1, .9)
        p = [f[0][i] * (1 - u) * (1 - v) + f[1][i] * u * (1 - v) + f[2][i] * u * v + f[3][i] * (1 - u) * v for i in range(3)]
        if p[2] < .25:
            continue
        nx, ny = p[0] - cx, p[1] - cy
        r = math.hypot(nx, ny) or 1.0
        size = rng.uniform(.08, .2)
        furn.box((p[0] + nx / r * .05, p[1] + ny / r * .05, p[2]), (size, size, size * .7), rng.choice(HOLD_COLOURS), yaw=math.atan2(ny, nx))
    return faces


# ---- pollinator garden -----------------------------------------------------------------------------
def bee_hotel(timber, furn, x, y, yaw, height=1.9):
    """A timber bee hotel on a post: a roofed box packed with hollow stems and drilled logs."""
    with timber.at(x, y, 0, yaw):
        timber.box((0, 0, height / 2 - .3), (.12, .12, height - .6), TIMBER_DARK)
        timber.box((0, 0, height - .25), (.32, .7, .6), '#7d5d3f')
        for s in (-1, 1):
            timber.quad((-.24, s * .02, height + .14), (.24, s * .02, height + .14), (.24, s * .45, height - .02), (-.24, s * .45, height - .02), TIMBER)
    with furn.at(x, y, 0, yaw):
        for i in range(5):
            for j in range(4):
                furn.cyl((.17, -.27 + i * .135, height - .48 + j * .14), (.12, -.27 + i * .135, height - .48 + j * .14), .05,
                         '#c9b48a' if (i + j) % 3 else '#6f5236', sides=6)


def lectern(furn, x, y, yaw, colour='#3b5d3a'):
    """An interpretive lectern: a sloped panel on a post, its blank face toward local -y."""
    with furn.at(x, y, 0, yaw):
        furn.box((0, 0, .45), (.1, .1, .9), '#3a3f43')
        furn.quad((-.4, -.25, .85), (.4, -.25, .85), (.4, .15, 1.1), (-.4, .15, 1.1), colour)
        furn.quad((-.35, -.24, .87), (.35, -.24, .87), (.35, .12, 1.095), (-.35, .12, 1.095), '#e8e2cf')


def prism_block(conc, furn, rng, centre, radius, height, rot, lean=(.3, .1), tilt=(.06, -.04), holds=40,
                bulge=.45, panels=('#a9a8a2', '#c9a878'), sides=6):
    """An angular bouldering block like the cast and timber-panel blocks of outdoor bouldering parks: an
    irregular hexagon footprint, a mid-height ring pushed out on alternate faces so every wall folds,
    and a top ring shifted by `lean` (overhanging one side) under a flat cap tilted by `tilt`. Faces
    alternate grey and plywood-toned panels; coloured holds dot the walls."""
    cx, cy = centre
    base, mid, top = [], [], []
    for k in range(sides):
        a = math.radians(rot) + math.tau * k / sides
        r = radius * (1.0 + .1 * math.sin(k * 2.9 + radius))
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        base.append((x, y, 0.0))
        out = bulge if k % 2 == 0 else -.15
        mid.append((cx + (x - cx) * (1 + out / r), cy + (y - cy) * (1 + out / r), height * (.42 + .08 * math.sin(k * 1.7))))
        tx, ty = cx + (x - cx) * .9 + lean[0], cy + (y - cy) * .9 + lean[1]
        top.append((tx, ty, height + tilt[0] * (tx - cx) + tilt[1] * (ty - cy)))
    walls = []
    for i in range(sides):
        j = (i + 1) % sides
        for lo, hi, band in ((base, mid, 0), (mid, top, 1)):
            quad = (lo[i], lo[j], hi[j], hi[i])
            walls.append(quad)
            colour = panels[(i + band) % 2]
            conc.tri(quad[0], quad[1], quad[2], colour)
            conc.tri(quad[0], quad[2], quad[3], colour)
    centre_top = (sum(p[0] for p in top) / sides, sum(p[1] for p in top) / sides, sum(p[2] for p in top) / sides)
    for i in range(sides):
        conc.tri(top[i], top[(i + 1) % sides], centre_top, '#b9b6ae')
    for _ in range(holds):
        q = walls[rng.randrange(len(walls))]
        u, v = rng.uniform(.08, .92), rng.uniform(.06, .94)
        p = [q[0][k] * (1 - u) * (1 - v) + q[1][k] * u * (1 - v) + q[2][k] * u * v + q[3][k] * (1 - u) * v for k in range(3)]
        nx, ny = q[1][1] - q[0][1], -(q[1][0] - q[0][0])
        n = math.hypot(nx, ny) or 1.0
        size = rng.uniform(.1, .26)
        furn.box((p[0] + nx / n * .06, p[1] + ny / n * .06, p[2]), (size, size * 1.3, size * .7), rng.choice(HOLD_COLOURS),
                 yaw=math.atan2(ny, nx))
    return shapely.geometry.Polygon([(x, y) for x, y, _ in base])


BLOOM_COLOURS = ['#8a5fb0', '#e6b62f', '#d27aa8', '#ecebe3', '#d9772f', '#6f8fd0']


def bloom_field(foliage_solid, region, rng, count, drifts=24, heights=(.3, .85)):
    """Cheap massed flowers for meadow beds: each a thin green stem and a small coloured head (four
    triangles), coloured by the nearest drift so blooms read in patches. Drawn as foliage, so the
    runtime never treats the stems as walls."""
    minx, miny, maxx, maxy = region.bounds
    centres = [(rng.uniform(minx, maxx), rng.uniform(miny, maxy), rng.choice(BLOOM_COLOURS)) for _ in range(drifts)]
    placed = 0
    tries = 0
    while placed < count and tries < count * 6:
        tries += 1
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if not region.contains(shapely.geometry.Point(x, y)):
            continue
        near = min(centres, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)
        colour = near[2] if rng.random() < .8 else rng.choice(BLOOM_COLOURS)
        h = rng.uniform(*heights)
        a = rng.uniform(0, math.tau)
        lean = rng.uniform(-.06, .06)
        tx, ty = x + math.cos(a) * lean, y + math.sin(a) * lean
        w = .012
        foliage_solid.tri((x - math.sin(a) * w, y + math.cos(a) * w, 0.0), (x + math.sin(a) * w, y - math.cos(a) * w, 0.0), (tx, ty, h), '#5d7a3a')
        s = rng.uniform(.045, .09)
        p = [(tx + s * math.cos(a + k * math.pi / 2), ty + s * math.sin(a + k * math.pi / 2), h + (.02 if k % 2 else -.01)) for k in range(4)]
        foliage_solid.tri(p[0], p[1], p[2], colour)
        foliage_solid.tri(p[0], p[2], p[3], colour)
        placed += 1
    return placed
