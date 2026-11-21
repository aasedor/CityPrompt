"""Sports-ground pieces for the native park batch: fences, stands, dugouts, lights and markings.

Kept apart from parkkit.py so the parks already registered keep the source hash they
were built with. Everything is drawn in the park frame (x east, y north, z up).
Dimensions are typical teaching values, not a sports facility design.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box

import parkkit as kit

# extra ground colours (low, high) for sports surfaces; parkkit's own entries are untouched
kit.SURFACES.update({
    'infield': ('#a8774f', '#b5835a'), 'track_dirt': ('#9a6c48', '#a77752'),
    'turf_light': ('#5f8a3a', '#6a9642'), 'turf_dark': ('#4f7631', '#5a8238'),
    'track_red': ('#9c4a3a', '#a85443'), 'pitch': ('#a59a6e', '#b4a87a'), 'square': ('#6f8a45', '#7b974c'),
    'concrete': ('#b7b3ab', '#c2beb6'), 'sand': ('#d6c49a', '#e0cfa6'),
})

GALV, POST, YELLOW, WHITE = '#b8bdc0', '#878f93', '#e5c22e', '#f1f0ea'
ALUMINIUM, ALU_DARK, BLOCK, ROOF = '#c3c7c9', '#9ea4a7', '#b9b4aa', '#5d6a72'


def stripes(part, region, direction, width, surfaces=('turf_light', 'turf_dark'), z=0.0, cell=2.5):
    """Mowing stripes: alternate bands across `direction` (radians), each laid with kit.fill."""
    ux, uy = math.cos(direction), math.sin(direction)
    minx, miny, maxx, maxy = region.bounds
    corners = [(minx, miny), (minx, maxy), (maxx, miny), (maxx, maxy)]
    proj = [x * ux + y * uy for x, y in corners]
    reach = max(maxx - minx, maxy - miny) * 2
    k0, k1 = math.floor(min(proj) / width), math.ceil(max(proj) / width)
    for k in range(k0, k1):
        a, b = k * width, (k + 1) * width
        band = Polygon([(a * ux - reach * uy, a * uy + reach * ux), (b * ux - reach * uy, b * uy + reach * ux),
                        (b * ux + reach * uy, b * uy - reach * ux), (a * ux + reach * uy, a * uy - reach * ux)])
        kit.fill(part, surfaces[k % 2], region.intersection(band), z=z, cell=cell)


def chalk(solid, region, z=.012, colour=WHITE):
    """Flat white markings over a polygonal region."""
    for poly in kit.polygons(shapely.make_valid(region)):
        for tri in kit.triangulate(poly):
            kit._tri_up(solid, [(x, y, z) for x, y in tri], colour)


def line_band(a, b, width):
    return LineString([a, b]).buffer(width / 2, cap_style='flat')


def chain_link(metal, points, heights, post_spacing=3.0, top_rail=True, mesh_spacing=.16, wire=.016, cap=None):
    """A chain-link fence along a polyline. `heights` is one height per point (a callable of
    the point is also accepted). Posts at every vertex and at most `post_spacing` apart."""
    pts = [tuple(p) for p in points]
    hs = [heights(p) for p in pts] if callable(heights) else list(heights)
    for (ax, ay), (bx, by), ha, hb in zip(pts, pts[1:], hs, hs[1:]):
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            continue
        n = max(1, math.ceil(length / post_spacing))
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            p0 = (ax + (bx - ax) * t0, ay + (by - ay) * t0)
            p1 = (ax + (bx - ax) * t1, ay + (by - ay) * t1)
            h = min(ha + (hb - ha) * t0, ha + (hb - ha) * t1)
            metal.diamond_mesh((p0[0], p0[1], .03), (p1[0] - p0[0], p1[1] - p0[1], 0.0), (0.0, 0.0, h - .06), mesh_spacing, wire, GALV)
            if top_rail:
                metal.cyl((p0[0], p0[1], h), (p1[0], p1[1], h), .021, POST, sides=6, cap0=False, cap1=False)
            metal.cyl((p0[0], p0[1], .05), (p1[0], p1[1], .05), .012, POST, sides=4, cap0=False, cap1=False)
            if cap:
                metal.cyl((p0[0], p0[1], h + .03), (p1[0], p1[1], h + .03), .045, cap, sides=6, cap0=False, cap1=False)
    for (x, y), h in zip(_posts(pts, post_spacing), _post_heights(pts, hs, post_spacing)):
        metal.cyl((x, y, 0), (x, y, h + .05), .035, POST, sides=8)


def _posts(pts, spacing):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / spacing))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
    return out + [pts[-1]]


def _post_heights(pts, hs, spacing):
    out = []
    for (ax, ay), (bx, by), ha, hb in zip(pts, pts[1:], hs, hs[1:]):
        n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / spacing))
        out += [ha + (hb - ha) * k / n for k in range(n)]
    return out + [hs[-1]]


def bleacher(solid, x, y, yaw, length=6.4, rows=5, rise=.3, tread=.6):
    """Aluminium bleachers facing local +x before `yaw`: seat and foot planks per row,
    a frame every 1.8 m and a back guardrail. Depth rows * tread, height rows * rise."""
    depth = rows * tread
    with solid.at(x, y, 0, yaw):
        frames = np.linspace(-length / 2 + .15, length / 2 - .15, max(2, math.ceil(length / 1.8) + 1))
        for fy in frames:
            solid.cyl((depth / 2, fy, 0), (-depth / 2, fy, rows * rise), .04, ALU_DARK, sides=4)
            solid.cyl((-depth / 2, fy, 0), (-depth / 2, fy, rows * rise + 1.0), .035, ALU_DARK, sides=4)
            solid.cyl((depth / 2 - .05, fy, 0), (depth / 2 - .05, fy, .2), .035, ALU_DARK, sides=4)
        for r in range(rows):
            xr = depth / 2 - (r + .5) * tread
            solid.box((xr + .1, 0, (r + .45) * rise - .1), (.4, length, .04), ALUMINIUM)          # foot planks
            solid.box((xr - .1, 0, (r + 1) * rise + .12), (.28, length, .05), ALUMINIUM)        # seat plank
        for z in (rows * rise + .55, rows * rise + 1.0):
            solid.cyl((-depth / 2, -length / 2, z), (-depth / 2, length / 2, z), .025, ALU_DARK, sides=6)


def dugout(solid, metal, x, y, yaw, length=9.0, depth=2.1, height=2.3):
    """A players' dugout facing local +x: block back and end walls, a sloping metal roof,
    a bench, a concrete floor drawn separately by the park, and a screen across its front."""
    with solid.at(x, y, 0, yaw):
        solid.box((-depth / 2 + .1, 0, height / 2), (.2, length, height), BLOCK)
        for s in (-1, 1):
            solid.box((0, s * (length / 2 - .1), height / 2), (depth, .2, height), BLOCK)
        solid.box((0, 0, height + .12), (depth + .5, length + .3, .1), ROOF)
        solid.box((-depth / 2 + .45, 0, .45), (.4, length - .8, .06), kit.WOOD)
        for k in np.linspace(-length / 2 + .6, length / 2 - .6, 5):
            solid.box((-depth / 2 + .45, k, .22), (.06, .06, .44), kit.BLACK)
    c, s = math.cos(yaw), math.sin(yaw)

    def world(px, py):
        return (x + px * c - py * s, y + px * s + py * c)
    a, b = world(depth / 2, -length / 2 + 1.0), world(depth / 2, length / 2 - 1.0)
    chain_link(metal, [a, b], [height - .05, height - .05], post_spacing=2.4)


def sports_light(solid, x, y, face, height=18.0, lamps=6):
    """A field light: a tapered steel pole, a cross-arm frame and lamps aimed toward `face` (radians)."""
    solid.box((x, y, .3), (.9, .9, .6), '#b2aea6')
    solid.cyl((x, y, .6), (x, y, height), .2, '#8c9396', r1=.12, sides=10)
    c, s = math.cos(face), math.sin(face)
    with solid.at(x, y, height, face):
        solid.box((.1, 0, .25), (.12, 2.6, .12), '#6f777b')
        solid.box((.1, 0, 1.05), (.12, 2.6, .12), '#6f777b')
        for k in range(lamps):
            ly = -1.05 + (k % 3) * 1.05
            lz = .45 + (k // 3) * .8
            solid.box((.35, ly, lz), (.42, .62, .5), '#3c4246')
            solid.box((.57, ly, lz), (.02, .52, .42), '#f4f1e2', gloss=True)
    return c, s


def scoreboard(solid, x, y, yaw, width=4.8, height=2.4, base=2.4):
    """A blank scoreboard on two posts, its face toward local -y."""
    with solid.at(x, y, 0, yaw):
        for dx in (-width / 2 + .4, width / 2 - .4):
            solid.box((dx, .15, (base + height) / 2), (.2, .2, base + height), '#4a5156')
        solid.box((0, 0, base + height / 2), (width, .25, height), '#24452f')
        for col in range(9):
            for row in range(2):
                solid.box((-width / 2 + .55 + col * .47, -.13, base + .55 + row * .9), (.36, .02, .5), '#16241a')
        solid.box((0, -.13, base + height - .22), (width - .6, .02, .22), '#e8e2cf')


def foul_pole(solid, x, y, height=6.0):
    solid.cyl((x, y, 0), (x, y, height), .075, YELLOW, sides=8)
    solid.box((x, y, height - 1.6), (.04, .6, 2.6), YELLOW)


def polyline(geometry, step=1.5):
    """Points along a line or ring, resampled no further than `step` apart."""
    coords = list(geometry.coords)
    out = [coords[0]]
    for (ax, ay), (bx, by) in zip(coords, coords[1:]):
        n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(1, n + 1)]
    return out


def arc(cx, cy, r, a0, a1, step=1.5):
    n = max(2, math.ceil(abs(a1 - a0) * r / step))
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(a0, a1, n + 1)]


def stadium(a, r, quad_segs=64):
    """A running-track shape: straights of length 2a along x joined by half circles of radius r."""
    return shapely.union_all([Point(-a, 0).buffer(r, quad_segs=quad_segs), Point(a, 0).buffer(r, quad_segs=quad_segs), box(-a, -r, a, r)])


def goal(metal, x, y, facing, width=7.32, height=2.44, depth=2.0):
    """A full-size soccer goal on the line at (x, y); the net runs back away from `facing` (radians, toward the pitch)."""
    with metal.at(x, y, 0, facing):
        for s in (-1, 1):
            metal.cyl((0, s * width / 2, 0), (0, s * width / 2, height), .06, WHITE, sides=8)
            metal.cyl((0, s * width / 2, height), (-depth * .5, s * width / 2, height), .03, POST, sides=6)
            metal.cyl((-depth * .5, s * width / 2, height), (-depth, s * width / 2, 0), .03, POST, sides=6)
            metal.cyl((0, s * width / 2, .02), (-depth, s * width / 2, .02), .03, POST, sides=6)
        metal.cyl((0, -width / 2, height), (0, width / 2, height), .06, WHITE, sides=8)
        metal.cyl((-depth, -width / 2, .02), (-depth, width / 2, .02), .03, POST, sides=6)
        metal.net_quad((-depth * .5, -width / 2, height), (-depth * .5, width / 2, height), (-depth, width / 2, 0), (-depth, -width / 2, 0),
                       24, 10, .012, '#e9eae6')
        metal.net_quad((0, -width / 2, height), (0, width / 2, height), (-depth * .5, width / 2, height), (-depth * .5, -width / 2, height),
                       24, 4, .012, '#e9eae6')


def shelter(timber, roof_solid, x, y, yaw, length=10.0, depth=4.4, low=2.6, high=3.4, bays=4):
    """An open timber shelter facing local +x before `yaw`: posts, beams and a single-slope metal roof,
    with a slatted back wall and a bench along it."""
    with timber.at(x, y, 0, yaw):
        for k in range(bays + 1):
            py = -length / 2 + k * length / bays
            for px, h in ((depth / 2 - .2, high), (-depth / 2 + .2, low)):
                timber.box((px, py, h / 2), (.2, .2, h), '#8a6844')
            timber.box((0, py, (high + low) / 2 + .05), (depth, .1, .22), '#7a5b3c')
        for px, h in ((depth / 2 - .2, high), (-depth / 2 + .2, low)):
            timber.box((px, 0, h + .02), (.24, length + .2, .26), '#7a5b3c')
        for z in np.arange(.35, low - .2, .22):
            timber.box((-depth / 2 + .2, 0, z), (.05, length, .14), '#9a7752')
        timber.box((-depth / 2 + .65, 0, .45), (.45, length - .6, .06), '#9a7752')
    with roof_solid.at(x, y, 0, yaw):
        lift = .22
        a, b = (depth / 2 + .35, high + lift + (high - low) * .35 / (depth - .4)), (-depth / 2 - .35, low + lift - (high - low) * .35 / (depth - .4))
        roof_solid.quad((a[0], -length / 2 - .4, a[1]), (a[0], length / 2 + .4, a[1]), (b[0], length / 2 + .4, b[1]), (b[0], -length / 2 - .4, b[1]), ROOF)
        roof_solid.quad((a[0], -length / 2 - .4, a[1] + .06), (b[0], -length / 2 - .4, b[1] + .06), (b[0], length / 2 + .4, b[1] + .06),
                        (a[0], length / 2 + .4, a[1] + .06), '#6b7880')


def hurdle(solid, x, y, yaw, height=.84):
    """A training hurdle: L-shaped feet, two uprights and a striped top bar."""
    with solid.at(x, y, 0, yaw):
        for s in (-.55, .55):
            solid.box((.3, s, .02), (.7, .04, .04), '#3a3f43')
            solid.box((0, s, height / 2), (.035, .035, height), '#c9cdd0')
        solid.box((0, 0, height - .035), (.02, 1.18, .07), WHITE)
        for k in (-.35, 0, .35):
            solid.box((-.005, k, height - .035), (.022, .18, .072), '#1f2326')


def picket_fence(timber, points, height=1.0, post_spacing=2.4, picket_gap=.14, colour='#f0eee6'):
    """A white picket fence along a polyline: square posts, two rails and pointed pickets,
    each picket one flat pentagon (the materials are double-sided)."""
    pts = [tuple(p) for p in points]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        for z in (.28, height - .22):
            timber.box(((ax + bx) / 2, (ay + by) / 2, z), (length, .035, .08), colour, yaw=math.atan2(uy, ux))
        n = max(1, int(length / picket_gap))
        for k in range(n):
            s = (k + .5) * length / n
            cx, cy = ax + ux * s, ay + uy * s
            w = .07
            x0, y0, x1, y1 = cx - ux * w / 2, cy - uy * w / 2, cx + ux * w / 2, cy + uy * w / 2
            ox, oy = -uy * .03, ux * .03
            top = height - .07
            timber.poly([(x0 + ox, y0 + oy, .04), (x1 + ox, y1 + oy, .04), (x1 + ox, y1 + oy, top), (cx + ox, cy + oy, height),
                         (x0 + ox, y0 + oy, top)], colour)
    for (x, y) in _posts(pts, post_spacing):
        timber.box((x, y, (height + .08) / 2), (.1, .1, height + .08), colour)
