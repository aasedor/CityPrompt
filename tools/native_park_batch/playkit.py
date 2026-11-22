"""Plaza and play pieces for park batch 3: shade sails, market stalls, a slotted wind screen,
glacial-erratic boulders, play structures, swings, a picnic shelter and a fieldhouse.

A separate file so that the kits already recorded in registered parks' source hashes
(parkkit.py, sportskit.py) never change. Everything is drawn in the park frame
(x east, y north, z up). Sizes are typical teaching values, not equipment designs.
"""
from __future__ import annotations

import math

import numpy as np

import parkkit as kit

kit.SURFACES.update({
    'sandstone': ('#c9b48f', '#d4c19d'), 'granite': ('#7d7a74', '#8a8780'), 'pavers': ('#bdb5a6', '#c9c1b2'),
    'fibar': ('#8a6a4a', '#987657'), 'play_rubber': ('#4a7a6a', '#558676'), 'stone_dust': ('#c2ab85', '#cdb791'),
})

CORTEN, CORTEN_DARK, SAIL, MAST = '#7d4a2a', '#6a3d22', '#f3f1ea', '#5b6266'
SANDSTONE = ['#c9b48f', '#bca582', '#d4c19d', '#b39a75']
ERRATIC = ['#8d8a83', '#9b978f', '#7f7b74', '#a6a197']


def shade_sail(metal, furn, corners, sag=.35, n=10):
    """A tensile shade sail: a triangular membrane between three mast tops, sagging toward its centre.
    `corners` are three (x, y, z) mast-top points; each mast leans outward with a back-stay to the ground."""
    a, b, c = (np.array(p, dtype=float) for p in corners)
    centre = (a + b + c) / 3
    for p in (a, b, c):
        out = np.array([p[0] - centre[0], p[1] - centre[1], 0.0])
        out /= max(np.linalg.norm(out), 1e-9)
        foot = (p[0] - out[0] * .6, p[1] - out[1] * .6, 0.0)
        metal.cyl(foot, tuple(p + np.array([0, 0, .15])), .09, MAST, r1=.07, sides=10)
        anchor = (p[0] + out[0] * 2.6, p[1] + out[1] * 2.6, 0.0)
        metal.cyl(tuple(p), anchor, .012, '#3a3f43', sides=4, cap0=False, cap1=False)
        metal.box(anchor, (.4, .4, .1), '#9a968d')

    def point(u, v):
        w = 1 - u - v
        q = a * w + b * u + c * v
        # sag: largest away from the corners, zero at them
        q = q - np.array([0, 0, sag * 6.75 * u * v * w * 1.0])
        return tuple(q)
    for i in range(n):
        for j in range(n - i):
            u0, v0, d = i / n, j / n, 1 / n
            furn.tri(point(u0, v0), point(u0 + d, v0), point(u0, v0 + d), SAIL)
            if i + j < n - 1:
                furn.tri(point(u0 + d, v0), point(u0 + d, v0 + d), point(u0, v0 + d), SAIL)


def market_stall(timber, furn, x, y, yaw, canopy='#2f5a3b', width=3.0, depth=2.2):
    """An open timber market stall facing local +x: four posts, a counter and a pitched canvas canopy."""
    with timber.at(x, y, 0, yaw):
        for px in (-depth / 2 + .1, depth / 2 - .1):
            for py in (-width / 2 + .1, width / 2 - .1):
                timber.box((px, py, 1.25), (.1, .1, 2.5), '#8a6844')
        timber.box((depth / 2 - .25, 0, .9), (.5, width - .1, .06), '#9a7752')
        timber.box((depth / 2 - .25, 0, .45), (.42, width - .3, .9), '#7a5b3c')
    with furn.at(x, y, 0, yaw):
        for s in (-1, 1):
            furn.quad((0, -width / 2 - .2, 3.0), (0, width / 2 + .2, 3.0), (s * (depth / 2 + .35), width / 2 + .2, 2.45),
                      (s * (depth / 2 + .35), -width / 2 - .2, 2.45), canopy)
        for s in (-1, 1):
            furn.tri((-depth / 2 - .35, s * (width / 2 + .2), 2.45), (depth / 2 + .35, s * (width / 2 + .2), 2.45),
                     (0, s * (width / 2 + .2), 3.0), canopy)


def wind_screen(metal, a, b, height=2.6, panel=2.0, view=None):
    """A weathering-steel wind screen from a to b: panels with vertical slots, and an optional
    framed view opening (start, end, sill, head) measured along the screen."""
    ax, ay = a
    bx, by = b
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    yaw = math.atan2(uy, ux)
    s = 0.0
    while s < length - 1e-6:
        e = min(length, s + panel)
        mid = (s + e) / 2
        cx, cy = ax + ux * mid, ay + uy * mid
        opening = view and view[0] < mid < view[1]
        if opening:
            for z0, z1 in ((0, view[2]), (view[3], height)):
                metal.box((cx, cy, (z0 + z1) / 2), (e - s - .03, .02, z1 - z0), CORTEN, yaw=yaw)
            metal.box((cx, cy, view[2]), (e - s, .14, .06), CORTEN_DARK, yaw=yaw)
            metal.box((cx, cy, view[3]), (e - s, .14, .06), CORTEN_DARK, yaw=yaw)
        else:
            # slotted panel: solid strips between narrow vertical slots
            strips = 7
            w = (e - s - .03) / strips
            for k in range(strips):
                off = s + .015 + (k + .5) * w
                px, py = ax + ux * off, ay + uy * off
                metal.box((px, py, height / 2), (w * .78, .02, height - .1), CORTEN, yaw=yaw)
            metal.box((cx, cy, .05), (e - s - .03, .03, .1), CORTEN_DARK, yaw=yaw)
            metal.box((cx, cy, height - .03), (e - s - .03, .03, .06), CORTEN_DARK, yaw=yaw)
        if not (view and view[0] < s < view[1]):                       # no posts inside the view opening
            metal.box((ax + ux * s, ay + uy * s, height / 2), (.08, .08, height), CORTEN_DARK, yaw=yaw)
        s = e
    metal.box((bx, by, height / 2), (.08, .08, height), CORTEN_DARK, yaw=yaw)


def boulder(rock, x, y, size, yaw, palette=None):
    """A glacial-erratic seating boulder: an angular block with a flat base."""
    rock.rock(size, 11, palette or ERRATIC, depth=(.62, .9), jitter=.04, origin=(x, y, 0), yaw=yaw)


def bench_plinth(conc, timber, x, y, yaw, length=4.0):
    """A long timber bench on a concrete plinth, sitting from both sides."""
    with conc.at(x, y, 0, yaw):
        conc.box((0, 0, .2), (length, .5, .4), '#b5b0a6')
    with timber.at(x, y, 0, yaw):
        for k in range(5):
            timber.box((0, -.2 + k * .1, .44), (length + .1, .085, .06), '#9a7752')


def paver_bands(furn, region, spacing=6.0, width=.25, colour='#a39b8d', origin=(0.0, 0.0)):
    """Darker paver bands on a square grid, laid flat just above a paved region."""
    import shapely
    from shapely.geometry import box
    minx, miny, maxx, maxy = region.bounds
    strips = []
    for x in np.arange(origin[0] + math.floor((minx - origin[0]) / spacing) * spacing, maxx + spacing, spacing):
        strips.append(box(x - width / 2, miny, x + width / 2, maxy))
    for y in np.arange(origin[1] + math.floor((miny - origin[1]) / spacing) * spacing, maxy + spacing, spacing):
        strips.append(box(minx, y - width / 2, maxx, y + width / 2))
    bands = shapely.union_all(strips).intersection(region.buffer(-.05))
    for poly in kit.polygons(bands):
        for tri in kit.triangulate(poly):
            kit._tri_up(furn, [(x, y, .003) for x, y in tri], colour)


def tree_grate(furn, x, y, size=1.5):
    """A cast-iron tree grate, flush with the paving."""
    furn.box((x, y, .006), (size, size, .012), '#3a3d3f')
    for k in range(-3, 4):
        furn.box((x + k * size / 8, y, .013), (.03, size - .1, .004), '#2a2c2e')


# ---- play ---------------------------------------------------------------------------------------
TIMBER, TIMBER_DARK, PLAY_GREEN, PLAY_ORANGE, PLAY_STEEL = '#9a7752', '#7a5b3c', '#4f7a4a', '#c8772f', '#6f777b'


def play_tower(timber, metal, x, y, deck=1.2, size=1.6, roof='#4f7a4a'):
    """A square timber play tower: four posts, a deck, low guard rails and a pitched roof."""
    h = size / 2
    for dx in (-h, h):
        for dy in (-h, h):
            timber.box((x + dx, y + dy, (deck + 2.4) / 2), (.12, .12, deck + 2.4), TIMBER)
    timber.box((x, y, deck - .04), (size + .1, size + .1, .08), TIMBER_DARK)
    for s in (-1, 1):
        timber.box((x + s * h, y, deck + .45), (.06, size, .1), TIMBER)
        timber.box((x, y + s * h, deck + .85), (size, .06, .08), TIMBER)
    r = deck + 2.4
    with metal.at(x, y, 0, 0.0):
        for s in (-1, 1):
            metal.quad((-h - .2, s * (h + .2), r), (h + .2, s * (h + .2), r), (h + .2, 0, r + .7), (-h - .2, 0, r + .7), roof)
        for s in (-1, 1):
            metal.tri((s * (h + .2), -h - .2, r), (s * (h + .2), h + .2, r), (s * (h + .2), 0, r + .7), roof)


def play_bridge(timber, metal, a, b, deck=1.2, width=.9):
    """A slatted timber bridge between two tower decks, with rope-net sides."""
    ax, ay = a
    bx, by = b
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    yaw = math.atan2(uy, ux)
    n = int(length / .22)
    for k in range(n):
        s = (k + .5) * length / n
        timber.box((ax + ux * s, ay + uy * s, deck - .03), (.16, width, .05), TIMBER, yaw=yaw)
    for side in (-1, 1):
        ox, oy = -uy * side * width / 2, ux * side * width / 2
        p0, p1 = (ax + ox, ay + oy), (bx + ox, by + oy)
        metal.net_quad((p0[0], p0[1], deck), (p1[0], p1[1], deck), (p1[0], p1[1], deck + .8), (p0[0], p0[1], deck + .8),
                       max(2, int(length / .25)), 4, .02, '#c9b07a')
        metal.cyl((p0[0], p0[1], deck + .8), (p1[0], p1[1], deck + .8), .03, '#c9b07a', sides=5)


def slide(metal, x, y, yaw, deck=1.2, length=3.2, colour=PLAY_ORANGE):
    """A straight plastic slide leaving a deck edge at (x, y), running out along local +x."""
    with metal.at(x, y, 0, yaw):
        steps = 10
        for k in range(steps):
            t0, t1 = k / steps, (k + 1) / steps
            def z(t):
                return deck * (1 - t) ** 1.6 + .28 * t
            x0, x1 = t0 * length, t1 * length
            metal.quad((x0, -.3, z(t0)), (x1, -.3, z(t1)), (x1, .3, z(t1)), (x0, .3, z(t0)), colour)
            for s in (-1, 1):
                metal.quad((x0, s * .32, z(t0)), (x1, s * .32, z(t1)), (x1, s * .32, z(t1) + .28), (x0, s * .32, z(t0) + .28), colour)


def climbing_net(metal, a, b, deck=1.2, colour='#c9b07a'):
    """A sloping rope net from the ground at a up to a deck edge at b."""
    (ax, ay), (bx, by) = a, b
    ux, uy = by - ay, -(bx - ax)
    length = math.hypot(ux, uy)
    ox, oy = ux / length * .6, uy / length * .6
    metal.net_quad((ax - ox, ay - oy, 0), (ax + ox, ay + oy, 0), (bx + ox, by + oy, deck), (bx - ox, by - oy, deck), 6, 8, .022, colour)


def swing_set(metal, x, y, yaw, bays=2, height=2.4, span=2.4):
    """A steel A-frame swing set with two seats per bay on chains."""
    with metal.at(x, y, 0, yaw):
        total = bays * span
        for sx in (-total / 2, total / 2):
            for sy in (-.9, .9):
                metal.cyl((sx, sy, 0), (sx, 0, height), .05, PLAY_STEEL, sides=8)
        metal.cyl((-total / 2, 0, height), (total / 2, 0, height), .055, PLAY_STEEL, sides=8)
        for b in range(bays):
            for k in (-.35, .35):
                cx = -total / 2 + (b + .5) * span + k * span / 1.2
                for dy in (-.2, .2):
                    metal.cyl((cx, dy, height), (cx, dy, .5), .008, '#3a3f43', sides=3, cap0=False, cap1=False)
                metal.box((cx, 0, .48), (.18, .45, .04), '#2f3438')


def split_rail_fence(timber, points, post_spacing=2.4, height=1.1):
    """A rustic split-rail fence: round posts with three rails between them."""
    pts = [tuple(p) for p in points]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        length = math.hypot(bx - ax, by - ay)
        n = max(1, math.ceil(length / post_spacing))
        for k in range(n + 1):
            t = k / n
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            timber.cyl((px, py, 0), (px, py, height + .1), .07, '#7d6a52', sides=7)
            if k < n:
                qx, qy = ax + (bx - ax) * (k + 1) / n, ay + (by - ay) * (k + 1) / n
                for z in (.35, .7, 1.0):
                    timber.cyl((px, py, z), (qx, qy, z), .045, '#8a7558', sides=5, cap0=False, cap1=False)


def picnic_table(timber, x, y, yaw):
    with timber.at(x, y, 0, yaw):
        timber.box((0, 0, .74), (1.9, .8, .05), TIMBER)
        for s in (-1, 1):
            timber.box((0, s * .7, .44), (1.9, .28, .04), TIMBER)
            for dx in (-.7, .7):
                timber.box((dx, s * .35, .37), (.08, .08, .74), TIMBER_DARK, yaw=0.0)


def fieldhouse(conc, timber, metal, x0, y0, x1, y1, height=3.6, front='y1'):
    """A single-storey fieldhouse (washrooms, concession, storage): block walls, a deep flat roof
    with fascia, a concession window and doors on the `front` side (a closed massing inside)."""
    from shapely.geometry import box
    kit.extrude(conc, '#c2bbae', box(x0, y0, x1, y1), 0, height, top_colour='#8c9196')
    kit.extrude(conc, '#8a8579', box(x0 - .02, y0 - .02, x1 + .02, y1 + .02), 0, .5)
    kit.extrude(metal, '#4f5a62', box(x0 - .8, y0 - .8, x1 + .8, y1 + .8).difference(box(x0 + .1, y0 + .1, x1 - .1, y1 - .1)),
                height, height + .45)
    cx = (x0 + x1) / 2
    fy = y1 if front == 'y1' else y0
    s = 1 if front == 'y1' else -1
    conc.box((cx, fy + s * .02, 1.6), (3.6, .04, 1.2), '#2c3a40', gloss=True)          # concession window
    timber.box((cx, fy + s * .25, 1.0), (3.9, .5, .06), '#8a6844')                     # counter
    for dx in (-(x1 - x0) / 2 + 1.2, (x1 - x0) / 2 - 1.2):
        conc.box((cx + dx, fy + s * .02, 1.05), (1.0, .04, 2.1), '#3b4f5e')            # doors
    for dx in (-(x1 - x0) / 2 + 2.6, (x1 - x0) / 2 - 2.6):
        conc.box((cx + dx, fy + s * .02, 2.6), (1.2, .04, .5), '#2c3a40', gloss=True)  # clerestory lights
