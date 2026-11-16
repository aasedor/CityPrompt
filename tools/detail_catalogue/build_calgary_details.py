#!/usr/bin/env python3
"""Calgary site details for Add details: winter city, lanes and yards, foothills
materials, pathway and transit furniture, and local wildlife.

Blender-free and deterministic like the prairie foliage builder, and written in
the same kit convention (linear vertex colours, flat normals, no textures, one
matte mesh plus an optional smoother glass/ice mesh). Objects are authored in
metres, Z-up, about a ground origin that is the placement anchor.

These are generic concept models for site visualization. They carry no City of
Calgary or Calgary Transit branding, reproduce no specific landmark or artwork,
and are not construction, electrical, traffic or play-safety designs.

    python tools/detail_catalogue/build_calgary_details.py --dry-run
    python tools/detail_catalogue/build_calgary_details.py --output <fresh-directory> [--id <slug> ...]
    node tools/detail_catalogue/render_detail_thumbnails.cjs <directory> utility-pole-lines:3.2,lrt-catenary-pole:4.2
    python tools/detail_catalogue/build_calgary_details.py --output <directory> --attach-thumbnails
    python tools/detail_catalogue/build_calgary_details.py --output <directory> --register
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_local_foliage as foliage  # noqa: E402
from calgary_kit import Solid, add, mix, mul, norm, rounded_rect, sub  # noqa: E402

KIT = 'calgary-details-v1'
# YYC is Calgary's airport code and common local shorthand. The plainer
# detail-calgary- prefix already belongs to the traffic-safety concept family
# (calgarySafetyCatalogue.json), and IDs are saved in student projects, so the
# two families must never be confusable by prefix.
PREFIX = 'detail-yyc-'
URL_ROOT = f'/park-kits/{KIT}'
GENERATOR = 'CityPrompt Calgary details builder v1'

# sRGB palette; converted to linear vertex colours by the kit.
WHITE = '#eef0f1'
SNOW = ['#f4f7fa', '#e9eff5', '#fbfcfd', '#dfe8f0']
ICE = '#c6dbec'
RED = '#c23b33'
BLUE = '#2f5fa8'
YELLOW = '#e0b63a'
ORANGE = '#e2742b'
STEEL = '#3d4348'
GALV = '#9aa3a7'
BLACK = '#1e2124'
CONCRETE = '#b5b2aa'
GRAVEL = ['#a39b8c', '#b0a898', '#968e80', '#bab2a2']
TIMBER = '#8a6a4a'
CEDAR = ['#9a6b45', '#a87750', '#8c5f3c', '#b2835a']
WEATHERED = ['#8a7d6c', '#978a78', '#7c7061', '#a39684']
GLASS = '#a9c6cf'
GLASS_DARK = '#4c6470'
SANDSTONE = ['#c9ad84', '#bfa078', '#d4ba93', '#b3936b']
RUNDLE = ['#4a4a4c', '#5a5754', '#3f4144', '#6b5f55', '#544a44']
QUARTZITE = ['#b7b0a6', '#a9a39a', '#c4bdb2', '#9c958c', '#b9a99c']
STRAW = ['#c9a857', '#bf9d4c', '#d6b566', '#b08e42']


# ---------------------------------------------------------------------------
# Shared sub-assemblies
# ---------------------------------------------------------------------------
def split_outline(outline, longest):
    """Subdivide a closed outline so no edge is longer than `longest`."""
    out = []
    for i, a in enumerate(outline):
        b = outline[(i + 1) % len(outline)]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = max(1, math.ceil(length / longest))
        for k in range(steps):
            out.append((a[0] + (b[0] - a[0]) * k / steps, a[1] + (b[1] - a[1]) * k / steps))
    return out


def board_run(s, a, b, height=1.07, thick=.06, kick=.2, cap=BLUE):
    """One rink board panel from a to b on a counter-clockwise outline: ice side is the left."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ox, oy = dy / length * thick, -dx / length * thick
    s.quad((a[0], a[1], 0), (b[0], b[1], 0), (b[0], b[1], kick), (a[0], a[1], kick), YELLOW)
    s.quad((a[0], a[1], kick), (b[0], b[1], kick), (b[0], b[1], height), (a[0], a[1], height), WHITE)
    s.quad((a[0] + ox, a[1] + oy, 0), (b[0] + ox, b[1] + oy, 0), (b[0] + ox, b[1] + oy, height), (a[0] + ox, a[1] + oy, height), '#d9dcde')
    lip = thick * .35
    ix, iy = -dy / length * lip, dx / length * lip
    top = [(a[0] + ix, a[1] + iy), (b[0] + ix, b[1] + iy), (b[0] + ox * 1.35, b[1] + oy * 1.35), (a[0] + ox * 1.35, a[1] + oy * 1.35)]
    s.prism(top, height, height + .045, cap)


def board_brace(s, p, outward, height=1.07):
    """Timber post and kicker behind a board joint."""
    x, y = p[0] + outward[0] * .11, p[1] + outward[1] * .11
    s.box((x, y, height / 2), (.09, .09, height), TIMBER, jitter=.08, yaw=math.atan2(outward[1], outward[0]))
    foot = (p[0] + outward[0] * .75, p[1] + outward[1] * .75, .03)
    s.cyl((x, y, height * .8), foot, .035, TIMBER, sides=4)


def hockey_net(s, width=1.83, height=1.22, depth=1.1, shelf=.5, frame=RED, pipe=.03, net='#f2f4f5', mesh=.13):
    """Opening faces -y from the goal line at y = 0."""
    w = width / 2
    back = w * .86
    s.cyl((-w, 0, 0), (-w, 0, height), pipe, frame, sides=8)
    s.cyl((w, 0, 0), (w, 0, height), pipe, frame, sides=8)
    s.cyl((-w, 0, height), (w, 0, height), pipe, frame, sides=8)
    for sx in (-1, 1):
        s.cyl((sx * w, 0, height), (sx * w, shelf, height), pipe * .7, WHITE, sides=6)
        s.cyl((sx * w, shelf, height), (sx * back, depth, pipe), pipe * .7, WHITE, sides=6)
        s.cyl((sx * w, 0, pipe), (sx * back, depth, pipe), pipe * .7, WHITE, sides=6)
    s.cyl((-w, shelf, height), (w, shelf, height), pipe * .7, WHITE, sides=6)
    s.cyl((-back, depth, pipe), (back, depth, pipe), pipe * .7, WHITE, sides=6)
    nu = max(3, round(width / mesh))
    s.net_quad((-w, 0, height), (w, 0, height), (w, shelf, height), (-w, shelf, height), nu, max(2, round(shelf / mesh)), .012, net)
    s.net_quad((-w, shelf, height), (w, shelf, height), (back, depth, pipe), (-back, depth, pipe), nu, max(3, round(height / mesh)), .012, net)
    for sx in (-1, 1):
        s.net_quad((sx * w, 0, pipe), (sx * w, 0, height), (sx * w, shelf, height), (sx * back, depth, pipe), max(3, round(height / mesh)),
                   max(3, round(depth / mesh)), .012, net)


def roof_slab(s, a, b, c, d, thick, colour, courses=1, underside='#5a5048', jitter=.05):
    """Sloped slab on quad a-b (eave) to c-d (ridge); the top is drawn in shingle or panel courses."""
    up = (0, 0, thick)
    for i in range(courses):
        t0, t1 = i / courses, (i + 1) / courses
        s.quad(add(mix(a, d, t0), up), add(mix(b, c, t0), up), add(mix(b, c, t1), up), add(mix(a, d, t1), up), s.c(colour, jitter))
    s.quad(a, b, c, d, underside)
    s.quad(a, b, add(b, up), add(a, up), colour)
    s.quad(a, d, add(d, up), add(a, up), colour)
    s.quad(b, c, add(c, up), add(b, up), colour)


def gable_house(s, length, width, wall, ridge, siding, bands, roof, overhang=.25, courses=6, seams=0, trim=None, base=0.0):
    """Simple building with the ridge along x: banded walls, gable ends and a two-slab roof."""
    s.banded_box((0, 0, base), (length, width, wall), bands, siding, jitter=.07)
    for sx in (-1, 1):
        x = sx * length / 2
        s.tri((x, -width / 2, base + wall), (x, width / 2, base + wall), (x, 0, base + ridge), s.c(siding, .05))
    slope = (ridge - wall) / (width / 2)
    eave_y, eave_z = width / 2 + overhang, base + wall - slope * overhang
    x0, x1 = -length / 2 - overhang, length / 2 + overhang
    for sy in (-1, 1):
        a, b, c, d = (x0, sy * eave_y, eave_z), (x1, sy * eave_y, eave_z), (x1, 0, base + ridge), (x0, 0, base + ridge)
        roof_slab(s, a, b, c, d, .07, roof, courses)
        for k in range(seams):
            x = x0 + (x1 - x0) * (k + .5) / seams
            s.quad((x - .02, sy * eave_y, eave_z + .075), (x + .02, sy * eave_y, eave_z + .075), (x + .02, 0, base + ridge + .075), (x - .02, 0, base + ridge + .075),
                   s.c(roof, .0))
            s.quad((x - .02, sy * eave_y, eave_z + .075), (x - .02, 0, base + ridge + .075), (x - .02, 0, base + ridge + .11), (x - .02, sy * eave_y, eave_z + .11), roof)
            s.quad((x + .02, sy * eave_y, eave_z + .075), (x + .02, 0, base + ridge + .075), (x + .02, 0, base + ridge + .11), (x + .02, sy * eave_y, eave_z + .11), roof)
            s.quad((x - .02, sy * eave_y, eave_z + .11), (x + .02, sy * eave_y, eave_z + .11), (x + .02, 0, base + ridge + .11), (x - .02, 0, base + ridge + .11), roof)
    s.box((0, 0, base + ridge + .09), (x1 - x0, .14, .05), roof)
    if trim:
        for sx in (-1, 1):
            for sy in (-1, 1):
                s.box((sx * (length / 2 + .005), sy * (width / 2 + .005), base + wall / 2), (.1, .1, wall), trim)


def wall_panel(s, face, length, width, along, z, w, h, colour, proud=.02, gloss=False):
    """Thin panel on a wall of a length x width building: door leaf, window pane, sign."""
    if face in ('S', 'N'):
        sy = -1 if face == 'S' else 1
        s.box((along, sy * (width / 2 + proud / 2), z + h / 2), (w, proud, h), colour, gloss=gloss)
    else:
        sx = -1 if face == 'W' else 1
        s.box((sx * (length / 2 + proud / 2), along, z + h / 2), (proud, w, h), colour, gloss=gloss)


def framed_opening(s, face, length, width, along, z, w, h, fill, trim=WHITE, gloss=False, bar=.07, mullion=False):
    wall_panel(s, face, length, width, along, z, w, h, fill, proud=.015, gloss=gloss)
    for dz, hh in ((-bar / 2, bar), (h - bar / 2, bar)):
        wall_panel(s, face, length, width, along, z + dz, w + bar * 2, hh, trim, proud=.035)
    for da in (-w / 2 - bar / 2, w / 2 + bar / 2):
        wall_panel(s, face, length, width, along + da, z, bar, h, trim, proud=.035)
    if mullion:
        wall_panel(s, face, length, width, along, z, bar * .6, h, trim, proud=.03)
        wall_panel(s, face, length, width, along, z + h / 2 - bar * .3, w, bar * .6, trim, proud=.03)


def timber_bench(s, length=1.8, seat=.45, height=.45, colour=TIMBER, back=False):
    """Slatted bench centred on the origin, long axis x, sitter faces -y."""
    for k in range(4):
        s.box((0, -seat / 2 + seat * (k + .5) / 4, height), (length, seat / 4 - .012, .045), colour, jitter=.08)
    for sx in (-1, 1):
        s.box((sx * (length / 2 - .2), 0, height / 2 - .02), (.07, seat * .85, height - .04), STEEL)
    if back:
        for k in range(3):
            s.box((0, seat / 2 + .03, height + .16 + k * .13), (length, .035, .1), colour, jitter=.08)
        for sx in (-1, 1):
            s.box((sx * (length / 2 - .2), seat / 2 + .06, height + .22), (.06, .04, .5), STEEL)


def log(s, a, b, radius, bark='#6a5443', cut='#c9a977', sides=8):
    s.cyl(a, b, radius, s.c(bark, .1), sides=sides, cap0=False, cap1=False)
    axis = norm(sub(b, a))
    for end, sign in ((a, -1), (b, 1)):
        s.cyl(end, add(end, mul(axis, sign * .004)), radius * .96, s.c(cut, .06), sides=sides)


# ---------------------------------------------------------------------------
# Winter city
# ---------------------------------------------------------------------------
def outdoor_rink(s):
    length, width, radius = 30.0, 15.0, 4.5
    outline = rounded_rect(length, width, radius, 6)
    s.prism(outline, 0, .04, ICE, gloss=True)
    z = .042
    s.box((0, 0, z), (.3, width - .16, .004), RED)
    for x in (-4.5, 4.5):
        s.box((x, 0, z), (.3, width - .16, .004), BLUE)
    for x in (-11.6, 11.6):
        s.box((x, 0, z), (.06, 14.3, .004), RED)
    s.annulus((0, 0, z + .003), 2.92, 3.04, BLUE, 40)
    s.disc((0, 0, z + .003), .15, BLUE, 12)
    for sx in (-1, 1):
        crease = [(sx * 11.6, 0, z + .001)] + [(sx * (11.6 - math.cos(a) * 1.8), math.sin(a) * 1.8, z + .001)
                                              for a in (-math.pi / 2 + math.pi * i / 12 for i in range(13))]
        s.poly(crease, '#a9cfe8')
        for sy in (-1, 1):
            s.disc((sx * 8.2, sy * 4.0, z + .003), .3, RED, 12)
    panels = split_outline(outline, 2.45)
    count = len(panels)
    for i, a in enumerate(panels):
        b = panels[(i + 1) % count]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        size = math.hypot(dx, dy)
        outward = (dy / size, -dx / size)
        gate = mid[1] < -width / 2 + .01 and abs(mid[0]) < 1.3
        if not gate:
            board_run(s, a, b)
        if i % 2 == 0 or gate:
            board_brace(s, a, outward)
    # players' gate swung open on the south side
    hinge = (-1.3, -width / 2)
    with s.at(hinge[0], hinge[1], 0, yaw=math.radians(-112)):
        board_run(s, (0, 0), (2.4, 0))
    for sx, yaw in ((1, -math.pi / 2), (-1, math.pi / 2)):
        with s.at(sx * 11.6, 0, .04, yaw=yaw):
            hockey_net(s)
    for x in (-5.5, 5.5):
        with s.at(x, width / 2 + 1.0, 0, yaw=math.pi):
            timber_bench(s, 3.0)


def rink_board_section(s):
    board_run(s, (2.0, 0), (-2.0, 0))
    for x in (-2.0, 0, 2.0):
        board_brace(s, (x, 0), (0, 1))


def regulation_hockey_net(s):
    hockey_net(s)


def warming_hut(s):
    length, width, wall, ridge = 4.2, 3.0, 2.3, 3.25
    s.box((0, 0, .06), (length + .5, width + 1.5, .12), '#8f8a80')
    gable_house(s, length, width, wall, ridge, CEDAR[0], 12, '#39443f', overhang=.35, courses=1, seams=9, base=.12)
    framed_opening(s, 'S', length, width, -1.0, .12, 1.0, 2.05, '#2a2420', trim='#3a2f27')
    wall_panel(s, 'S', length, width, -1.62, .12, .1, 2.05, CEDAR[2], proud=.05)
    with s.at(-1.5, -width / 2 - .02, .12, yaw=math.radians(-108)):
        s.box((.5, 0, 1.02), (1.0, .05, 2.04), '#7a5234')
        s.box((.86, -.04, 1.0), (.05, .05, .14), GALV)
    framed_opening(s, 'S', length, width, .95, 1.1, 1.1, .85, GLASS_DARK, trim=WHITE, gloss=True, mullion=True)
    framed_opening(s, 'E', length, width, 0, 1.2, .9, .8, GLASS_DARK, trim=WHITE, gloss=True, mullion=True)
    with s.at(.95, -width / 2 - .32, .12):
        timber_bench(s, 1.7, .4, .45, CEDAR[1])
    # stove pipe
    s.cyl((1.3, .5, 2.7), (1.3, .5, 3.75), .08, BLACK, sides=10)
    s.cyl((1.3, .5, 3.75), (1.3, .5, 3.82), .13, BLACK, sides=10)
    # firewood against the west wall
    for row in range(4):
        for k in range(7 - row % 2):
            y = -.85 + k * .26 + (row % 2) * .13
            log(s, (-length / 2 - .5, y, .25 + row * .22), (-length / 2 - .06, y, .25 + row * .22), .11)
    # skate-change mat at the door
    s.box((-1.0, -width / 2 - .55, .125), (1.4, .9, .012), '#2b2f33')


def fire_pit_circle(s):
    for i in range(24):
        a0, a1 = i * math.tau / 24, (i + 1) * math.tau / 24
        s.tri((0, 0, .03), (math.cos(a0) * 2.7, math.sin(a0) * 2.7, .03), (math.cos(a1) * 2.7, math.sin(a1) * 2.7, .03), s.c(GRAVEL[0], .025))
        s.quad((math.cos(a0) * 2.7, math.sin(a0) * 2.7, 0), (math.cos(a1) * 2.7, math.sin(a1) * 2.7, 0), (math.cos(a1) * 2.7, math.sin(a1) * 2.7, .03),
               (math.cos(a0) * 2.7, math.sin(a0) * 2.7, .03), GRAVEL[2])
    rust = '#5b4035'
    s.cyl((0, 0, .03), (0, 0, .43), .56, rust, sides=20, cap0=False, cap1=False)
    s.cyl((0, 0, .03), (0, 0, .43), .52, '#2b2422', sides=20, cap0=False, cap1=False)
    s.annulus((0, 0, .43), .52, .58, '#6a4b3d', 20)
    s.disc((0, 0, .12), .52, '#3a3634', 20)
    for k in range(4):
        a = k * math.pi / 4 + .3
        log(s, (math.cos(a) * .38, math.sin(a) * .38, .16 + (k % 2) * .09), (-math.cos(a) * .38, -math.sin(a) * .38, .2 + (k % 2) * .09), .06, bark='#2c2623', cut='#4a3a30')
    for k in range(5):
        a = k * 1.3
        base = (math.cos(a) * .12, math.sin(a) * .12, .28)
        tip = (math.cos(a) * .04, math.sin(a) * .04, .5 + (k % 3) * .09)
        side = (math.cos(a + 1.6) * .07, math.sin(a + 1.6) * .07, 0)
        s.tri(sub(base, side), add(base, side), tip, ORANGE if k % 2 else '#f0b23a')
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        with s.at(math.cos(a) * 1.95, math.sin(a) * 1.95, .03, yaw=a + math.pi / 2):
            s.box((0, 0, .41), (1.9, .38, .1), s.c(TIMBER, .08), top=s.c('#a98862', .05))
            for x in (-.65, .65):
                s.cyl((x, 0, 0), (x, 0, .36), .15, s.c('#6a5443', .1), sides=9)
    with s.at(2.15, 0, .03):
        for row in range(3):
            for k in range(4 - row):
                y = -.36 + k * .24 + row * .12
                log(s, (-.25, y, .11 + row * .2), (.25, y, .11 + row * .2), .1)


def snow_fence(s):
    length, height = 4.8, 1.22
    for x in (-2.4, 0, 2.4):
        s.box((x, .03, .75), (.035, .035, 1.5), '#3f5a3a')
        s.box((x, .03, 1.44), (.04, .04, .12), WHITE)
    count = 54
    for k in range(count):
        x = -length / 2 + length * (k + .5) / count
        lean = (s.random() - .5) * .012
        tone = s.pick(['#b85a34', '#a94f2d', '#c2663d', '#9c4a2c'], .08)
        s.quad((x - .019, 0, .05), (x + .019, 0, .05), (x + .019 + lean, 0, .05 + height), (x - .019 + lean, 0, .05 + height), tone)
    for k in range(5):
        z = .16 + k * .25
        s.box((0, -.004, z), (length, .006, .012), '#6f7578')
        s.box((0, .004, z), (length, .006, .012), '#6f7578')


def snow_windrow(s):
    length, rings, around = 6.4, 13, 9
    profile = []
    for i in range(rings):
        t = i / (rings - 1)
        x = -length / 2 + length * t
        taper = math.sin(math.pi * min(1.0, max(0.0, t))) ** .55
        w, h = .95 * taper * (.85 + s.random() * .3) + .02, .95 * taper * (.75 + s.random() * .45) + .01
        shift = (s.random() - .5) * .25
        profile.append([(x + (s.random() - .5) * .12, shift + math.cos(math.pi * k / (around - 1)) * w * (.9 + s.random() * .2),
                         math.sin(math.pi * k / (around - 1)) * h * (.85 + s.random() * .3)) for k in range(around)])

    def tone(r, i):
        if i == 0 or i >= around - 2:
            return s.pick(['#c3c9cc', '#b3b8b8', '#cdd2d6'], .04)  # gritty base
        # ploughed snow is broken and blue in its shaded facets, which also keeps it legible on a pale card
        return s.pick(['#f1f5f9', '#dbe5ef', '#c8d6e4', '#e6edf4', '#bccbdb'], .02)

    s.loft(profile, tone, cap_start=True, cap_end=True)
    for _ in range(9):
        x, y = (s.random() - .5) * length * .8, (.75 + s.random() * .45) * (1 if s.random() < .5 else -1)
        s.rock((.25 + s.random() * .3, .2 + s.random() * .25, .12 + s.random() * .18), 4, ['#e6edf4', '#cfdbe8', '#f1f5f9'], jitter=.02, origin=(x, y, 0), yaw=s.random() * 3)


def grit_box(s):
    s.box((-.42, 0, .04), (.1, .8, .08), TIMBER)
    s.box((.42, 0, .04), (.1, .8, .08), TIMBER)
    s.box((0, 0, .08 + .32), (1.2, .76, .64), YELLOW)
    lid = '#3b4046'
    front, back = -.43, .43
    profile = [(front, .72), (back, .98), (back, 1.02), (front - .04, .76)]
    for x0, x1 in ((-.63, .63),):
        pts0 = [(x0, y, z) for y, z in profile]
        pts1 = [(x1, y, z) for y, z in profile]
        s.loft([pts0, pts1], lid)
    s.quad((-.6, front, .72), (.6, front, .72), (.6, back, .72), (-.6, back, .72), YELLOW)
    for sx in (-1, 1):
        s.tri((sx * .6, front, .72), (sx * .6, back, .72), (sx * .6, back, .98), YELLOW)
    s.box((0, front - .06, .78), (.3, .03, .03), GALV)
    s.box((0, -.385, .42), (.62, .012, .3), WHITE)
    s.box((0, -.392, .5), (.5, .006, .05), BLACK)
    s.box((0, -.392, .38), (.34, .006, .035), BLACK)
    s.box((0, -.392, .3), (.34, .006, .035), BLACK)


def plug_in_posts(s):
    for x in (-2.7, 0, 2.7):
        s.box((x, 0, .58), (.09, .09, 1.16), GALV)
        s.box((x, 0, 1.17), (.11, .11, .02), GALV)
        s.box((x, -.075, 1.02), (.16, .07, .22), '#7f888c')
        for dz in (-.05, .05):
            s.box((x, -.115, 1.02 + dz), (.1, .012, .075), YELLOW)
        s.box((x, 0, .01), (.2, .2, .02), CONCRETE)
    s.box((0, .03, .72), (5.4, .045, .14), s.c(TIMBER, .05))
    s.box((0, .03, .38), (5.4, .045, .14), s.c(TIMBER, .05))
    for x in (-1.35, 1.35):
        profile = [(-.11, 0), (.11, 0), (.07, .13), (-.07, .13)]
        s.loft([[(x - .9, -1.0 + y, z) for y, z in profile], [(x + .9, -1.0 + y, z) for y, z in profile]], CONCRETE)
        for dx in (-.7, .7):
            s.box((x + dx, -1.0, .134), (.18, .15, .006), YELLOW)
    # one cord left plugged in
    s.wire((-2.7, -.12, .97), (-2.2, -.9, .32), .28, .011, ORANGE, 8)


# ---------------------------------------------------------------------------
# Lanes and yards
# ---------------------------------------------------------------------------
def waste_cart(s, colour):
    lid = s.c(colour)
    lid = tuple(min(1.0, v * 1.18 + .004) for v in lid)
    bottom = [(x, y + .06, .03) for x, y in rounded_rect(.46, .54, .07, 3)]
    top = [(x, y, 1.0) for x, y in rounded_rect(.58, .72, .08, 3)]
    s.loft([bottom, top], colour, cap_start=True, cap_end=False)
    s.loft([[(x, y, .97) for x, y in rounded_rect(.62, .76, .09, 3)], [(x, y, 1.03) for x, y in rounded_rect(.62, .76, .09, 3)]], colour, cap_start=True, cap_end=False)
    s.prism(rounded_rect(.64, .79, .09, 3), 1.03, 1.065, lid)
    s.prism(rounded_rect(.5, .6, .08, 3), 1.065, 1.09, lid)
    s.box((0, -.41, 1.045), (.3, .05, .03), lid)
    s.cyl((-.25, .44, .99), (.25, .44, .99), .016, BLACK, sides=6)
    for sx in (-1, 1):
        s.box((sx * .25, .4, .99), (.035, .1, .04), colour)
        s.cyl((sx * .26, .34, .1), (sx * .33, .34, .1), .1, '#15171a', sides=12)
        s.cyl((sx * .33, .34, .1), (sx * .335, .34, .1), .045, GALV, sides=8)
    s.cyl((-.27, .34, .1), (.27, .34, .1), .012, GALV, sides=5)


CART_BLACK, CART_BLUE, CART_GREEN = '#272b2f', '#1f5fa8', '#3f7d3a'


def waste_cart_black(s):
    waste_cart(s, CART_BLACK)


def waste_cart_blue(s):
    waste_cart(s, CART_BLUE)


def waste_cart_green(s):
    waste_cart(s, CART_GREEN)


def waste_cart_trio(s):
    for x, colour, yaw in ((-.72, CART_BLACK, .04), (0, CART_BLUE, -.03), (.72, CART_GREEN, .05)):
        with s.at(x, 0, 0, yaw=yaw):
            waste_cart(s, colour)


def half_span(s, start, direction, span, sag, radius, colour, segments=6):
    """Conductor from a pole attachment to the low point at mid-span, `span` metres along +-x."""
    points = [(start[0] + direction * span * t, start[1], start[2] - sag * t * t) for t in (i / segments for i in range(segments + 1))]
    for a, b in zip(points, points[1:]):
        s.cyl(a, b, radius, colour, sides=3, cap0=False, cap1=False)


def utility_pole(s, wires=False):
    wood, height = '#6e5a48', 10.4
    for i in range(4):
        z0, z1 = height * i / 4, height * (i + 1) / 4
        s.cyl((0, 0, z0), (0, 0, z1), .15 - .05 * i / 4, s.c(wood, .07), r1=.15 - .05 * (i + 1) / 4, sides=10, cap0=i == 0, cap1=i == 3)
    s.box((0, 0, 9.9), (.1, 2.4, .12), s.c(wood, .05))
    for sy in (-1, 1):
        s.cyl((.05, sy * .7, 9.86), (.05, 0, 9.2), .012, GALV, sides=4)
    primaries = (-1.05, .38, 1.05)
    porcelain = '#7a5a4a'
    for y in primaries:
        s.cyl((0, y, 9.96), (0, y, 10.06), .018, GALV, sides=6)
        s.cyl((0, y, 10.06), (0, y, 10.2), .05, porcelain, r1=.035, sides=8)
        s.cyl((0, y, 10.1), (0, y, 10.13), .068, porcelain, sides=8)
    s.cyl((0, .14, 8.9), (0, .25, 8.9), .032, '#d9d6cc', sides=8)
    # pole-mounted transformer with its hangers, bushings and drop lead
    s.cyl((0, -.45, 7.5), (0, -.45, 8.4), .27, '#8b9196', sides=14)
    s.cyl((0, -.45, 8.4), (0, -.45, 8.45), .29, '#7b8186', sides=14)
    for k in range(8):
        a = k * math.tau / 8
        s.box((math.cos(a) * .29, -.45 + math.sin(a) * .29, 7.9), (.035, .035, .6), '#7b8186', yaw=a)
    for dx in (-.12, .12):
        s.cyl((dx, -.45, 8.45), (dx, -.45, 8.72), .035, '#c9c2b3', r1=.02, sides=8)
    for z in (7.7, 8.2):
        s.box((0, -.2, z), (.12, .22, .06), GALV)
    s.wire((0, -1.05, 10.2), (-.12, -.45, 8.72), .12, .008, BLACK, 5)
    for k in range(3):
        s.cyl((0, .14, 6.9 + k * .2), (0, .22, 6.9 + k * .2), .035, '#d9d6cc', sides=8)
    s.box((0, .17, 5.6), (.05, .1, .05), GALV)
    # lane light on a curved arm
    arm = [(0, .12, 8.25), (0, .9, 8.72), (0, 1.9, 8.82)]
    s.tube(arm, .028, GALV, sides=6)
    s.box((0, 2.15, 8.8), (.24, .6, .1), '#7f888c')
    s.box((0, 2.2, 8.745), (.16, .36, .012), '#f3ecd0', gloss=True)
    s.box((.152, 0, 1.9), (.004, .09, .13), '#c9cdd0')
    if wires:
        for direction in (-1, 1):
            for y in primaries:
                half_span(s, (0, y, 10.2), direction, 15.0, .45, .011, '#3a3d40')
            half_span(s, (0, .25, 8.9), direction, 15.0, .42, .011, '#3a3d40')
            half_span(s, (0, .22, 7.1), direction, 15.0, .4, .02, '#25282b')
            half_span(s, (0, .22, 5.6), direction, 15.0, .35, .026, '#1b1d1f')


def utility_pole_plain(s):
    utility_pole(s, False)


def utility_pole_lines(s):
    utility_pole(s, True)


def privacy_fence(s):
    width, height = 2.44, 1.83
    for x in (-width / 2, width / 2):
        s.box((x, .03, .98), (.089, .089, 1.96), s.c(CEDAR[2], .06))
        s.box((x, .03, 1.975), (.12, .12, .03), s.c(CEDAR[2], .06))
    for z in (.28, .95, 1.6):
        s.box((0, .035, z), (width - .09, .038, .089), s.c(CEDAR[0], .06))
    boards = 17
    pitch = (width - .1) / boards
    for k in range(boards):
        x = -width / 2 + .05 + pitch * (k + .5)
        top = height + (s.random() - .5) * .012
        s.box((x, 0, .04 + top / 2), (pitch - .006, .019, top), s.c(CEDAR[k % 2], .07))


def chain_link_fence(s):
    width, height = 3.0, 1.22
    for x in (-width / 2, width / 2):
        s.cyl((x, 0, 0), (x, 0, height + .08), .03, GALV, sides=10)
        s.cyl((x, 0, height + .08), (x, 0, height + .12), .036, GALV, r1=.012, sides=10)
    s.cyl((-width / 2, 0, height), (width / 2, 0, height), .021, GALV, sides=8)
    s.cyl((-width / 2, 0, .06), (width / 2, 0, .06), .006, GALV, sides=4)
    s.diamond_mesh((-width / 2 + .03, 0, .06), (width - .06, 0, 0), (0, 0, height - .08), .1, .009, '#aab1b4')
    for x in (-width / 2 + .045, width / 2 - .045):
        s.box((x, 0, height / 2 + .03), (.012, .012, height - .1), GALV)


def garden_shed(s):
    length, width, wall, ridge = 3.0, 2.4, 1.95, 2.75
    for y in (-.8, .8):
        s.box((0, y, .06), (length + .1, .14, .12), s.c(TIMBER, .05))
    gable_house(s, length, width, wall, ridge, '#7d8f96', 11, '#4a4d50', overhang=.2, courses=7, trim=WHITE, base=.12)
    # double doors with Z bracing on the south side
    for sx in (-1, 1):
        cx = sx * .39
        wall_panel(s, 'S', length, width, cx, .14, .74, 1.74, '#6c7d84', proud=.03)
        for dz in (.02, .82, 1.62):
            wall_panel(s, 'S', length, width, cx, .14 + dz, .74, .1, WHITE, proud=.045)
        with s.at(cx, -width / 2 - .04, .14 + .87):
            s.box((0, 0, 0), (.07, .012, 1.04), WHITE, yaw=0)
        a = (cx - sx * .32, -width / 2 - .04, .26)
        b = (cx + sx * .32, -width / 2 - .04, .96)
        s.ribbon(a, b, .08, WHITE, normal=(0, 1, 0))
        s.box((sx * .06, -width / 2 - .06, 1.05), (.03, .03, .12), BLACK)
    for dz, hh in ((-.05, .09), (1.78, .09)):
        wall_panel(s, 'S', length, width, 0, .14 + dz, 1.68, hh, WHITE, proud=.05)
    for da in (-.82, .82):
        wall_panel(s, 'S', length, width, da, .14, .09, 1.83, WHITE, proud=.05)
    framed_opening(s, 'E', length, width, 0, 1.15, .7, .6, GLASS_DARK, trim=WHITE, gloss=True, mullion=True)
    # ramp to the doors
    ramp = [(-.8, -width / 2 - .7, 0), (.8, -width / 2 - .7, 0), (.8, -width / 2, .12), (-.8, -width / 2, .12)]
    s.quad(*ramp, s.c(TIMBER, .05))
    for sx in (-1, 1):
        s.tri((sx * .8, -width / 2 - .7, 0), (sx * .8, -width / 2, .12), (sx * .8, -width / 2, 0), TIMBER)


def trampoline(s):
    radius, deck = 2.13, .9
    frame = '#565d63'
    s.torus((0, 0, deck), radius, .026, frame, nu=28, nv=5)
    s.disc((0, 0, deck), 1.78, '#1c1e21', 28)
    s.annulus((0, 0, deck + .03), 1.74, radius + .1, '#2f66b5', 28)
    s.cyl((0, 0, deck - .02), (0, 0, deck + .03), radius + .1, '#285a9f', sides=28, cap0=False, cap1=False)
    for k in range(6):
        a = k * math.tau / 6
        b = a + math.tau / 12
        p, q = (math.cos(a - .12) * radius, math.sin(a - .12) * radius), (math.cos(a + .12) * radius, math.sin(a + .12) * radius)
        s.cyl((p[0], p[1], deck), (p[0] * 1.02, p[1] * 1.02, .03), .022, frame, sides=6)
        s.cyl((q[0], q[1], deck), (q[0] * 1.02, q[1] * 1.02, .03), .022, frame, sides=6)
        s.cyl((p[0] * 1.02, p[1] * 1.02, .03), (q[0] * 1.02, q[1] * 1.02, .03), .022, frame, sides=6)
        del b
    poles, top = 8, 2.7
    for k in range(poles):
        a = k * math.tau / poles + .2
        x, y = math.cos(a) * (radius + .02), math.sin(a) * (radius + .02)
        s.cyl((x, y, .5), (x, y, deck + .05), .02, frame, sides=6)
        s.cyl((x, y, deck + .05), (x, y, top), .036, '#3f8f5a', sides=8)
        s.cyl((x, y, top), (x * .97, y * .97, top + .05), .04, '#3f8f5a', r1=.01, sides=8)
    net, ring_r, segments = '#3b4046', radius - .12, 40
    for k in range(segments):
        a0, a1 = k * math.tau / segments, (k + 1) * math.tau / segments
        p0, p1 = (math.cos(a0) * ring_r, math.sin(a0) * ring_r), (math.cos(a1) * ring_r, math.sin(a1) * ring_r)
        normal = (math.cos(a0), math.sin(a0), 0)
        s.ribbon((p0[0], p0[1], deck + .04), (p0[0], p0[1], top), .012, net, normal=normal)
        for j in range(7):
            z = deck + .04 + (top - deck - .04) * (j + 1) / 7
            s.ribbon((p0[0], p0[1], z), (p1[0], p1[1], z), .012, net, normal=normal)
    s.torus((0, 0, top), ring_r, .014, frame, nu=segments, nv=4)
    # zipped entry flap and a short ladder
    s.box((0, -radius - .28, .45), (.5, .04, .04), frame)
    s.box((0, -radius - .2, .25), (.5, .04, .04), frame)
    for sx in (-1, 1):
        s.cyl((sx * .25, -radius - .32, 0), (sx * .25, -radius - .12, deck), .018, frame, sides=6)


def little_free_library(s):
    post = '#6b523c'
    s.box((0, 0, .58), (.09, .09, 1.16), post)
    s.box((0, 0, .02), (.3, .3, .04), CONCRETE)
    for sx in (-1, 1):
        s.cyl((sx * .04, 0, .78), (sx * .2, 0, 1.14), .022, post, sides=4)
    teal, roof = '#2f8f8a', '#b5443a'
    w, d, h, z = .5, .36, .46, 1.16
    s.box((0, 0, z + .015), (w + .04, d + .04, .03), post)
    s.box((0, d / 2 - .01, z + .03 + h / 2), (w, .02, h), teal)
    for sx in (-1, 1):
        s.box((sx * (w / 2 - .01), 0, z + .03 + h / 2), (.02, d, h), teal)
    s.box((0, 0, z + .035), (w, d, .012), teal)
    s.box((0, 0, z + .03 + h * .5), (w - .04, d - .04, .012), '#d8c9a8')
    books = ['#b5443a', '#e0b63a', '#2f5fa8', '#3f7d3a', '#7a4b8f', '#e2742b', '#d9d2c2', '#5b4035']
    for shelf_z in (z + .045, z + .03 + h * .5 + .008):
        x = -w / 2 + .04
        while x < w / 2 - .06:
            thick, tall = .022 + s.random() * .022, .13 + s.random() * .07
            s.box((x + thick / 2, -d / 2 + .1, shelf_z + tall / 2), (thick, .14, tall), s.pick(books, .05))
            x += thick + .003
    # door frame, left open-glazed so the books show
    for dz in (0, h - .04):
        s.box((0, -d / 2 - .005, z + .05 + dz), (w, .02, .04), WHITE)
    for sx in (-1, 1):
        s.box((sx * (w / 2 - .02), -d / 2 - .005, z + .03 + h / 2), (.04, .02, h), WHITE)
    s.box((w / 2 - .06, -d / 2 - .02, z + .03 + h / 2), (.02, .02, .02), GALV)
    # little gable roof, ridge front to back
    rz, peak, over = z + .03 + h, z + .03 + h + .2, .06
    for sx in (-1, 1):
        a, b = (sx * (w / 2 + over), -d / 2 - over, rz - .02), (sx * (w / 2 + over), d / 2 + over, rz - .02)
        c, e = (0, d / 2 + over, peak), (0, -d / 2 - over, peak)
        roof_slab(s, a, b, c, e, .02, roof, 3, underside='#7a2f29')
    for sy in (-1, 1):
        s.tri((-w / 2, sy * d / 2, rz), (w / 2, sy * d / 2, rz), (0, sy * d / 2, peak - .03), teal)


def street_hockey_net(s):
    hockey_net(s, width=1.37, height=1.12, depth=.6, shelf=.25, frame=WHITE, pipe=.022, mesh=.11)
    for sx in (-1, 1):
        s.cyl((sx * .685, 0, .3), (sx * .685, 0, .55), .0235, RED, sides=8)
    shaft, blade = '#d9c9a3', '#2a2d31'
    for x, y, yaw, colour in ((.55, -.75, .35, shaft), (-.5, -1.0, 2.6, '#b8442a')):
        with s.at(x, y, .012, yaw=yaw):
            s.box((0, 0, .015), (1.4, .03, .02), colour)
            s.box((.76, .1, .03), (.06, .26, .06), blade, yaw=.3)
    s.dome((.1, -.6, .035), (.035, .035, .035), ORANGE, nu=8, nv=4, full=True)


# ---------------------------------------------------------------------------
# Foothills landscape and ranch heritage
# ---------------------------------------------------------------------------
def sandstone_blocks(s):
    s.rock((1.55, .72, .56), 5, SANDSTONE, depth=(.88, .98), origin=(-.55, .1, 0), yaw=.12)
    s.rock((1.15, .68, .5), 5, SANDSTONE, depth=(.88, .98), origin=(1.0, -.35, 0), yaw=-.5)
    s.rock((.95, .6, .42), 5, SANDSTONE, depth=(.86, .97), origin=(.75, .75, 0), yaw=1.1)
    s.rock((.8, .5, .34), 5, SANDSTONE, depth=(.86, .97), origin=(-.5, .12, .56), yaw=.3)


def sandstone_seat_wall(s):
    length, depth = 3.6, .5
    x = -length / 2
    while x < length / 2 - .2:
        size = min(length / 2 - x, .75 + s.random() * .4)
        if length / 2 - x - size < .35:
            size = length / 2 - x
        s.rock((size - .015, depth - s.random() * .03, .32), 4, SANDSTONE, depth=(.9, .99), origin=(x + size / 2, (s.random() - .5) * .02, 0), jitter=.04)
        x += size
    x = -length / 2 - .02
    while x < length / 2 - .2:
        size = min(length / 2 + .02 - x, 1.0 + s.random() * .4)
        if length / 2 + .02 - x - size < .5:
            size = length / 2 + .02 - x
        s.rock((size - .012, depth + .06, .15), 3, SANDSTONE, depth=(.93, .995), origin=(x + size / 2, 0, .32), jitter=.035, top_light=1.1)
        x += size


def rundle_rock_wall(s):
    length, depth, height = 3.0, .45, .84
    s.box((0, 0, (height - .02) / 2), (length - .06, depth - .08, height - .02), '#26272a')
    z = 0.0
    while z < height - .03:
        course = min(height - z, .055 + s.random() * .06)
        x = -length / 2 + (s.random() * .15)
        first = True
        while x < length / 2 - .02:
            size = .18 + s.random() * .36
            if first:
                x0, first = -length / 2, False
                size = x + size + length / 2
            else:
                x0 = x
            size = min(size, length / 2 - x0)
            if length / 2 - (x0 + size) < .1:
                size = length / 2 - x0
            proud = s.random() * .03
            s.box((x0 + size / 2, 0, z + course / 2), (size - .008, depth + proud, course - .007), s.pick(RUNDLE, .08))
            x = x0 + size
        z += course
    x = -length / 2 - .03
    while x < length / 2:
        size = min(length / 2 + .03 - x, .5 + s.random() * .35)
        if length / 2 + .03 - x - size < .25:
            size = length / 2 + .03 - x
        s.box((x + size / 2, 0, height + .028), (size - .01, depth + .1, .056), s.pick(RUNDLE[:3], .06))
        x += size


def glacial_erratic(s):
    s.rock((3.5, 2.7, 2.3), 16, QUARTZITE, depth=(.6, .9), jitter=.045, yaw=.3)
    s.rock((1.3, 1.0, .8), 9, QUARTZITE, depth=(.62, .9), origin=(2.1, -1.2, 0), yaw=1.2)
    s.rock((.7, .55, .4), 7, QUARTZITE, depth=(.65, .9), origin=(-1.9, 1.5, 0), yaw=2.0)
    # lichen and rub marks kept to a few low faces
    for _ in range(7):
        a = s.random() * math.tau
        r = 1.2 + s.random() * .5
        p = (math.cos(a) * r, math.sin(a) * r * .75, .25 + s.random() * .5)
        s.dome(p, (.16 + s.random() * .1, .16 + s.random() * .1, .03), s.pick(['#8f9a6e', '#a8a06a', '#b88a4a'], .08), nu=6, nv=2)


def round_hay_bale(s):
    radius, width, sides = .76, 1.2, 22
    lift = radius * .93
    rings = []
    for x in (-width / 2, -.36, -.26, .26, .36, width / 2):
        rings.append([(x, math.cos(i * math.tau / sides) * radius, lift + max(-radius * .93, math.sin(i * math.tau / sides) * radius)) for i in range(sides)])

    courses = [s.c(STRAW[k % len(STRAW)], .03) for k in range(sides)]

    def tone(r, i):
        base = courses[i]
        return tuple(min(1.0, v * 1.16) for v in base) if r in (1, 3) else base  # net-wrap bands catch the light

    s.loft(rings, tone, cap_start=False, cap_end=False)
    for sx in (-1, 1):
        x = sx * width / 2
        steps = 4
        for k in range(steps):
            r0, r1 = radius * k / steps, radius * (k + 1) / steps
            colour = s.c(STRAW[(k + (sx > 0)) % len(STRAW)], .04)
            for i in range(sides):
                a0, a1 = i * math.tau / sides, (i + 1) * math.tau / sides
                pts = [(x, math.cos(a) * r, lift + max(-radius * .93, math.sin(a) * r)) for a, r in ((a0, r0), (a0, r1), (a1, r1), (a1, r0))]
                s.quad(pts[0], pts[1], pts[2], pts[3], colour)


def ranch_rail_fence(s):
    for x in (-2.4, 0, 2.4):
        s.cyl((x, 0, 0), (x, 0, 1.38), .08, s.pick(WEATHERED, .06), r1=.07, sides=9)
        s.cyl((x, 0, 1.38), (x, 0, 1.43), .07, s.pick(WEATHERED, .06), r1=.03, sides=9)
    for bay in (-1.2, 1.2):
        for z in (.42, .82, 1.2):
            s.box((bay, -.085, z + (s.random() - .5) * .02), (2.52, .04, .14), s.pick(WEATHERED, .07))


def ranch_gate(s):
    post = WEATHERED[2]
    for x in (-2.7, 2.7):
        s.cyl((x, 0, 0), (x, 0, 4.7), .16, s.c(post, .06), r1=.13, sides=10)
        s.cyl((x - .0, 0, 3.3), (x * .62, 0, 4.42), .07, s.c(post, .06), sides=7)
    s.cyl((-3.25, 0, 4.5), (3.25, 0, 4.5), .13, s.c(post, .06), sides=10)
    for x in (-.8, .8):
        s.cyl((x, 0, 4.38), (x, 0, 3.95), .008, GALV, sides=4)
    s.box((0, 0, 3.7), (2.0, .05, .5), s.c('#5d4a3a', .05))
    for dz in (-.21, .21):
        s.box((0, -.03, 3.7 + dz), (1.9, .012, .03), '#c9b48a')
    for sx in (-1, 1):
        s.box((sx * .93, -.03, 3.7), (.03, .012, .42), '#c9b48a')
    steel = '#7f8a8c'

    def leaf(length):
        for z in (.2, .48, .76, 1.04, 1.32):
            s.cyl((0, 0, z), (length, 0, z), .02, steel, sides=6)
        for x in (0, length / 2, length):
            s.cyl((x, 0, .2), (x, 0, 1.32), .022, steel, sides=6)
        s.cyl((0, 0, .2), (length / 2, 0, 1.32), .016, steel, sides=5)
        s.cyl((length, 0, .2), (length / 2, 0, 1.32), .016, steel, sides=5)

    with s.at(-2.52, 0, 0):
        leaf(2.48)
    with s.at(2.52, 0, 0, yaw=math.pi - .55):
        leaf(2.48)


# ---------------------------------------------------------------------------
# Pathway and transit
# ---------------------------------------------------------------------------
def pathway_marker(s):
    body, band = '#3a4046', '#1f8a8a'
    s.cyl((0, 0, 0), (0, 0, .012), .22, CONCRETE, sides=16, cap0=False)
    s.box((0, 0, .68), (.16, .16, 1.34), body)
    for sx in (-1, 1):
        s.tri((sx * .08, -.08, 1.35), (sx * .08, .08, 1.35), (0, 0, 1.43), body)
    for sy in (-1, 1):
        s.tri((-.08, sy * .08, 1.35), (.08, sy * .08, 1.35), (0, 0, 1.43), '#4a5158')
    s.box((0, 0, 1.16), (.172, .172, .13), band)
    s.box((0, 0, .3), (.168, .168, .05), YELLOW)
    ink = '#1d3f6b'
    for sy, kind in ((-1, 'bike'), (1, 'walk')):
        y = sy * .0815
        s.box((0, y, .86), (.13, .006, .15), WHITE)
        face = sy * .086
        if kind == 'bike':
            for x in (-.034, .034):
                with s.at(x, face, .835, roll=math.pi / 2):
                    s.annulus((0, 0, 0), .017, .024, ink, 12)
            for a, b in (((-.034, .835), (-.004, .875)), ((-.004, .875), (.022, .875)), ((.022, .875), (.034, .835)), ((-.034, .835), (.006, .835)),
                         ((.006, .835), (.022, .875)), ((-.004, .875), (-.008, .888)), ((.022, .875), (.03, .893))):
                s.ribbon((a[0], face, a[1]), (b[0], face, b[1]), .006, ink, normal=(0, 1, 0))
        else:
            with s.at(0, face, .905, roll=math.pi / 2):
                s.disc((0, 0, 0), .012, ink, 10)
            for a, b in (((0, .89), (0, .845)), ((0, .845), (-.018, .805)), ((0, .845), (.02, .808)), ((0, .88), (-.02, .855)), ((0, .88), (.022, .862))):
                s.ribbon((a[0], face, a[1]), (b[0], face, b[1]), .007, ink, normal=(0, 1, 0))
    for k in range(3):
        z = .5 + k * .09
        for sx in (-1, 1):
            x = sx * .0815
            s.tri((x, -.04, z), (x, 0, z + .04), (x, 0, z + .015), YELLOW)
            s.tri((x, .04, z), (x, 0, z + .04), (x, 0, z + .015), YELLOW)


def river_safety_station(s):
    s.box((0, 0, .02), (.34, .34, .04), CONCRETE)
    s.box((0, 0, 1.02), (.1, .1, 2.0), YELLOW)
    s.box((0, -.07, 1.42), (.62, .04, .86), RED)
    s.box((0, -.092, 1.42), (.56, .006, .8), '#d94a3f')

    def ring_tone(i):
        return WHITE if (i // 3) % 2 else ORANGE

    s.torus((0, -.15, 1.5), .26, .055, ring_tone, nu=24, nv=8, axis='y')
    for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4):
        s.box((math.cos(a) * .26, -.115, 1.5 + math.sin(a) * .26), (.05, .05, .05), GALV)
    s.torus((0, -.11, 1.12), .09, .014, WHITE, nu=14, nv=5, axis='y')
    s.torus((0, -.13, 1.12), .075, .014, '#e6e2d6', nu=14, nv=5, axis='y')
    s.box((0, -.1, 1.23), (.03, .04, .05), GALV)
    s.box((0, -.06, 1.94), (.34, .012, .24), WHITE)
    with s.at(0, -.068, 1.94, roll=math.pi / 2):
        s.annulus((0, 0, 0), .05, .078, RED, 16)
    for z in (.5, .62):
        s.box((0, 0, z), (.104, .104, .05), BLACK)


def lrt_platform_shelter(s):
    length, steel, roof = 10.0, STEEL, '#cdd4d7'
    s.box((0, -2.3, .004), (length, .6, .008), YELLOW)
    columns = (-3.8, 0, 3.8)
    front, back, gutter = -1.0, 1.2, .1
    for x in columns:
        s.box((x, front, 1.5), (.14, .14, 3.0), steel)
        s.box((x, back, 1.55), (.14, .14, 3.1), steel)
        s.box((x, front, .01), (.3, .3, .02), GALV)
        s.box((x, back, .01), (.3, .3, .02), GALV)
        s.cyl((x, front, 2.98), (x, gutter, 2.84), .05, steel, sides=6)
        s.cyl((x, back, 3.08), (x, gutter, 2.84), .05, steel, sides=6)
    s.box((0, front, 3.0), (length - .8, .12, .2), steel)
    s.box((0, back, 3.1), (length - .8, .12, .2), steel)
    x0, x1 = -length / 2, length / 2
    roof_slab(s, (x0, -1.95, 3.24), (x1, -1.95, 3.24), (x1, gutter, 2.92), (x0, gutter, 2.92), .06, roof, 1, underside='#e3e7e9')
    roof_slab(s, (x1, 1.6, 3.2), (x0, 1.6, 3.2), (x0, gutter, 2.92), (x1, gutter, 2.92), .06, roof, 1, underside='#e3e7e9')
    s.box((0, -1.97, 3.27), (length + .04, .05, .16), RED)
    s.box((0, 1.62, 3.23), (length + .04, .05, .12), steel)
    s.box((0, gutter, 2.9), (length, .16, .06), steel)
    s.box((0, gutter - .5, 2.93), (length - 1.0, .08, .02), '#f5f1dc', gloss=True)
    # glazed wind screens along the back and both ends
    for a, b in ((columns[0], columns[1]), (columns[1], columns[2])):
        mid, span = (a + b) / 2, b - a - .14
        s.box((mid, back, 1.3), (span, .02, 2.05), GLASS, gloss=True)
        s.box((mid, back - .012, 1.05), (span, .006, .1), WHITE)
        for z in (.26, 2.34):
            s.box((mid, back, z), (span, .05, .05), steel)
    for x in (columns[0], columns[2]):
        s.box((x, .65, 1.3), (.02, 1.0, 2.05), GLASS, gloss=True)
        s.box((x, .65, 2.34), (.05, 1.0, .05), steel)
        s.box((x, .65, .26), (.05, 1.0, .05), steel)
    for x in (-1.9, 1.9):
        with s.at(x, .72, 0):
            timber_bench(s, 2.0, .45, .46, '#9a7650', back=True)
    s.cyl((-3.6, -.3, .95), (-1.2, -.3, .95), .03, GALV, sides=6)
    for x in (-3.5, -1.3):
        s.cyl((x, -.3, 0), (x, -.3, .95), .025, GALV, sides=6)
    # information pylon and fare validator, both blank
    s.box((-4.6, .5, 1.15), (.14, .62, 2.3), '#2c3136')
    s.box((-4.6, .5, 2.18), (.146, .626, .24), RED)
    for sx in (-1, 1):
        s.box((-4.6 + sx * .072, .5, 1.3), (.004, .5, 1.1), '#e7e3d6')
        s.box((-4.6 + sx * .075, .5, 1.62), (.004, .4, .03), BLUE)
        s.box((-4.6 + sx * .075, .42, 1.3), (.004, .03, .5), RED)
        s.box((-4.6 + sx * .075, .58, 1.05), (.004, .2, .03), '#3f7d3a')
    s.box((4.5, .4, .62), (.26, .22, 1.24), '#6f777c')
    s.box((4.5, .285, 1.02), (.2, .012, .16), '#1d2b36', gloss=True)
    s.box((4.5, .285, .8), (.12, .012, .1), YELLOW)


def lrt_catenary_pole(s):
    steel, reach = '#8e969a', -2.75
    s.box((0, 0, .015), (.5, .5, .03), '#7b8387')
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.cyl((sx * .19, sy * .19, .03), (sx * .19, sy * .19, .07), .022, '#5e666a', sides=6)
    s.cyl((0, 0, .03), (0, 0, 7.7), .16, steel, r1=.1, sides=8)
    s.cyl((0, 0, 7.7), (0, 0, 7.76), .11, steel, r1=.04, sides=8)
    arm_z, stay_z = 6.3, 7.35
    s.cyl((0, -.1, arm_z), (0, reach - .15, arm_z), .035, steel, sides=7)
    s.cyl((0, -.1, stay_z), (0, reach + .1, arm_z + .04), .022, steel, sides=6)
    porcelain = '#7a5a4a'
    for y, z in ((-.45, arm_z), (-.5, stay_z - .16)):
        for k in range(4):
            s.cyl((0, y - k * .07, z if z == arm_z else z - k * .026), (0, y - k * .07 - .025, z if z == arm_z else z - k * .026 - .009), .075, porcelain, sides=9)
    messenger, contact = arm_z + .12, 5.5
    s.cyl((0, reach, arm_z), (0, reach, messenger), .02, steel, sides=5)
    s.cyl((0, reach + .9, arm_z - .02), (0, reach, contact + .04), .018, steel, sides=5)
    s.box((0, reach, contact + .03), (.2, .04, .05), '#5e666a')
    wire = '#3a3d40'
    for direction in (-1, 1):
        half_span(s, (0, reach, messenger), direction, 20.0, .5, .012, wire, 8)
        s.cyl((0, reach, contact), (direction * 20.0, reach, contact), .013, wire, sides=3, cap0=False, cap1=False)
        for k in range(1, 5):
            x = direction * k * 4.6
            t = abs(x) / 20.0
            s.cyl((x, reach, messenger - .5 * t * t), (x, reach, contact), .005, wire, sides=3, cap0=False, cap1=False)


def heated_bus_shelter(s):
    length, depth, height, steel = 4.8, 1.9, 2.5, STEEL
    s.box((0, 0, .012), (length + .5, depth + .7, .024), '#c2bfb7')
    xs = (-length / 2, 0, length / 2)
    for x in xs:
        for y in (-depth / 2, depth / 2):
            s.box((x, y, height / 2 + .02), (.07, .07, height), steel)
    s.box((0, 0, height + .08), (length + .3, depth + .4, .12), '#454c52')
    s.box((0, -depth / 2 - .2, height + .1), (length + .32, .04, .16), RED)
    s.box((0, 0, height + .145), (length - .4, depth - .3, .02), '#252a2e')

    def pane(centre, size, frit_axis):
        s.box(centre, size, GLASS, gloss=True)
        band = (size[0] if frit_axis == 'x' else .008, .008 if frit_axis == 'x' else size[1], .1)
        offset = (0, -.012, 0) if frit_axis == 'x' else (-.012, 0, 0)
        s.box((centre[0] + offset[0], centre[1] + offset[1], 1.05), band, WHITE)

    for a, b in ((xs[0], xs[1]), (xs[1], xs[2])):
        pane(((a + b) / 2, depth / 2, 1.3), (b - a - .07, .02, 2.2), 'x')
    for x in (xs[0], xs[2]):
        pane((x, 0, 1.3), (.02, depth - .07, 2.2), 'y')
    # front: two fixed panes either side of a 1.3 m doorway
    for sx in (-1, 1):
        cx = sx * (length / 2 + .65) / 2
        pane((cx, -depth / 2, 1.3), (length / 2 - .65 - .07, .02, 2.2), 'x')
        s.box((sx * .65, -depth / 2, height / 2 + .02), (.06, .06, height), steel)
    s.box((0, -depth / 2, 2.32), (1.3, .05, .12), steel)
    for y in (-depth / 2, depth / 2):
        s.box((0, y, .16), (length, .05, .08), steel) if y > 0 else None
    for sx in (-1, 1):
        s.box((sx * (length / 2 + .65) / 2, -depth / 2, .16), (length / 2 - .65, .05, .08), steel)
    with s.at(0, depth / 2 - .32, 0):
        timber_bench(s, 3.2, .42, .46, '#9a7650')
    # two radiant heaters under the roof and a push button by the door
    for x in (-1.2, 1.2):
        s.box((x, .2, height - .04), (1.0, .2, .07), '#2c3136')
        s.box((x, .2, height - .08), (.9, .12, .012), '#ef6a2e')
    s.box((.78, -depth / 2 + .08, 1.1), (.08, .05, .12), '#6f777c')
    s.box((.78, -depth / 2 + .05, 1.1), (.04, .012, .04), '#3fae5a')
    # blank advertising panel and stop flag
    s.box((length / 2 + .75, .3, 1.15), (1.25, .14, 1.9), '#2c3136')
    for sy in (-1, 1):
        s.box((length / 2 + .75, .3 + sy * .072, 1.2), (1.1, .004, 1.6), '#e9e5d8')
        s.box((length / 2 + .75, .3 + sy * .075, 1.55), (.9, .004, .5), '#8fb7c9')
        s.box((length / 2 + .75, .3 + sy * .075, .85), (.9, .004, .35), '#d8a657')
    s.cyl((-length / 2 - .7, -depth / 2 - .1, 0), (-length / 2 - .7, -depth / 2 - .1, 2.7), .03, GALV, sides=8)
    s.box((-length / 2 - .7, -depth / 2 - .1, 2.45), (.46, .02, .46), WHITE)
    s.box((-length / 2 - .7, -depth / 2 - .1, 2.56), (.47, .024, .23), RED)


def scooter(s, colour):
    dark = '#2a2d31'
    s.box((0, 0, .13), (.15, .52, .035), dark)
    s.box((0, 0, .15), (.13, .44, .006), '#43474c')
    for y in (-.36, .36):
        s.cyl((-.022, y, .1), (.022, y, .1), .1, BLACK, sides=12)
        s.cyl((-.026, y, .1), (.026, y, .1), .04, GALV, sides=8)
    s.box((0, .36, .215), (.06, .22, .012), colour)
    s.box((0, -.3, .16), (.05, .16, .06), colour)
    s.cyl((0, -.36, .12), (0, -.27, 1.05), .022, colour, sides=8)
    s.cyl((-.24, -.27, 1.05), (.24, -.27, 1.05), .015, BLACK, sides=6)
    s.box((0, -.27, 1.085), (.07, .035, .04), dark)
    s.cyl((.03, .1, .12), (.14, .12, .0), .008, GALV, sides=4)


def scooter_corral(s):
    length, depth = 3.4, 1.6
    s.box((0, 0, .003), (length, depth, .006), '#5f9d74')
    for y in (-depth / 2, depth / 2):
        s.box((0, y, .005), (length + .1, .1, .01), WHITE)
    for x in (-length / 2, length / 2):
        s.box((x, 0, .005), (.1, depth, .01), WHITE)
    s.cyl((-1.45, .55, .5), (1.45, .55, .5), .025, GALV, sides=7)
    for x in (-1.45, 0, 1.45):
        s.cyl((x, .55, 0), (x, .55, .5), .025, GALV, sides=7)
    for k, colour in enumerate(('#17a2a2', '#17a2a2', '#7a4b8f', '#17a2a2', '#7a4b8f')):
        if k == 3:
            continue
        with s.at(-1.2 + k * .6, -.05, .003, yaw=.08 * (k % 2) - .04, pitch=-.1):
            scooter(s, colour)
    # sign: blue plate with a plain scooter pictogram, no wording
    px = length / 2 + .25
    s.cyl((px, .55, 0), (px, .55, 2.3), .03, GALV, sides=8)
    s.box((px, .52, 2.02), (.5, .02, .5), BLUE)
    y = .505
    for a, b in (((-.14, 1.9), (.1, 1.9)), ((.1, 1.9), (.13, 2.16)), ((.07, 2.16), (.17, 2.16))):
        s.ribbon((px + a[0], y, a[1]), (px + b[0], y, b[1]), .028, WHITE, normal=(0, 1, 0))
    for x in (-.14, .1):
        with s.at(px + x, y, 1.885, roll=math.pi / 2):
            s.disc((0, 0, 0), .035, WHITE, 10)


# ---------------------------------------------------------------------------
# Everyday streets, lanes and yards: the humble objects that make a place read
# as lived in. Same rules as above: generic, unbranded, no wording.
# ---------------------------------------------------------------------------
def wheel(s, centre, radius, width, axis=(1.0, 0.0, 0.0), tyre='#15171a', hub=GALV, sides=12):
    half = mul(axis, width / 2)
    s.cyl(sub(centre, half), add(centre, half), radius, tyre, sides=sides)
    cap = mul(axis, width / 2 + .004)
    s.cyl(sub(centre, cap), add(centre, cap), radius * .45, hub, sides=8)


def arch_prism(s, width, y0, y1, base_z, rise, colour, steps=8, gloss=False):
    """Barrel top: a half-ellipse in XZ extruded along y."""
    def ring(y):
        return [(math.cos(math.pi * k / steps) * width / 2, y, base_z + math.sin(math.pi * k / steps) * rise) for k in range(steps + 1)]
    s.loft([ring(y0), ring(y1)], colour, gloss=gloss)


def rest_on_ground(s, draw):
    """Run draw(), then shift what it added so its lowest vertex sits on z = 0."""
    parts = (s.body, s.gloss)
    marks = [len(part.positions) for part in parts]
    draw()
    low = min(z for part, mark in zip(parts, marks) for z in part.positions[mark + 2::3])
    for part, mark in zip(parts, marks):
        for k in range(mark + 2, len(part.positions), 3):
            part.positions[k] -= low


def spoked_wheel(s, hub, radius, spokes=8, rim=GALV):
    """Bicycle wheel in the YZ plane: tyre, rim, spokes and a short axle."""
    s.torus(hub, radius - .02, .02, '#1b1d1f', nu=20, nv=5, axis='x')
    s.torus(hub, radius - .048, .008, rim, nu=20, nv=4, axis='x')
    for k in range(spokes):
        a = k * math.tau / spokes
        s.cyl(hub, (hub[0], hub[1] + math.cos(a) * (radius - .05), hub[2] + math.sin(a) * (radius - .05)), .0028, rim, sides=3, cap0=False, cap1=False)
    s.cyl((hub[0] - .035, hub[1], hub[2]), (hub[0] + .035, hub[1], hub[2]), .02, rim, sides=6)


def wedge_body(s, width, profile, colour):
    """Extrude a (y, z) side profile across the width, closing both ends."""
    s.loft([[(-width / 2, y, z) for y, z in profile], [(width / 2, y, z) for y, z in profile]], colour)


def dumpster(s):
    green, lid = '#2f5d3a', '#1d1f22'
    w, d = 1.83, 1.7
    wedge_body(s, w, [(-d / 2, .12), (d / 2, .12), (d / 2, 1.5), (-d / 2, 1.08)], green)
    for sx in (-1, 1):
        x0, x1 = (.02, w / 2 + .02) if sx > 0 else (-w / 2 - .02, -.02)
        roof_slab(s, (x0, -d / 2 - .04, 1.085), (x1, -d / 2 - .04, 1.085), (x1, d / 2, 1.505), (x0, d / 2, 1.505), .04, lid, 1, underside=lid, jitter=.0)
        s.box((sx * (w / 2 + .07), 0, .82), (.14, 1.5, .22), '#264d30')
        s.box((sx * (w / 2 + .07), -.752, .82), (.1, .006, .16), '#111315')
        for y in (-.5, 0, .5):
            top = 1.08 + (y + d / 2) / d * .42 - .08
            s.box((sx * (w / 2 + .012), y, (.14 + top) / 2), (.024, .07, top - .14), '#264d30')
        for y in (-.7, .7):
            s.box((sx * .75, y, .06), (.14, .14, .12), '#2b2e31')
    s.box((0, -d / 2 - .01, 1.07), (w + .06, .07, .07), '#264d30')
    s.box((0, d / 2, 1.5), (w + .06, .06, .06), '#264d30')
    s.box((0, -d / 2 - .006, .68), (.55, .012, .32), WHITE)
    s.box((0, -d / 2 - .013, .68), (.45, .006, .05), '#264d30')


def deep_collection_bins(s):
    def one(x, lid):
        with s.at(x, 0, 0):
            r, h, n = .64, 1.12, 20
            for k in range(n):
                a0, a1 = k * math.tau / n, (k + 1) * math.tau / n
                tone = s.c(WEATHERED[(k * 2) % len(WEATHERED)], .06)
                s.quad((math.cos(a0) * r, math.sin(a0) * r, .08), (math.cos(a1) * r, math.sin(a1) * r, .08), (math.cos(a1) * r, math.sin(a1) * r, h),
                       (math.cos(a0) * r, math.sin(a0) * r, h), tone)
            s.cyl((0, 0, 0), (0, 0, .08), r + .05, '#5a5e61', sides=n)
            for z in (.32, .86):
                s.cyl((0, 0, z), (0, 0, z + .035), r + .008, STEEL, sides=n, cap0=False, cap1=False)
            s.cyl((0, 0, h), (0, 0, h + .07), r + .035, '#2b2e31', sides=n)
            s.dome((0, 0, h + .07), (r + .02, r + .02, .2), lid, nu=n, nv=4)
            s.box((0, -.3, h + .2), (.42, .3, .07), tuple(min(1.0, v * 1.25 + .01) for v in s.c(lid)))
            s.cyl((-.12, -.44, h + .22), (.12, -.44, h + .22), .014, GALV, sides=6)
    one(-.78, '#24272a')
    one(.78, '#1f5fa8')


def wildlife_proof_bin(s):
    brown, dark = '#5b4636', '#33271f'
    s.box((0, 0, .04), (1.55, .95, .08), CONCRETE)
    w, d = 1.3, .7
    wedge_body(s, w, [(-d / 2, .22), (d / 2, .22), (d / 2, 1.22), (-d / 2, 1.02)], brown)
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * (w / 2 - .06), sy * (d / 2 - .06), .15), (.08, .08, .14), dark)
        s.box((sx * .32, -d / 2 - .008, .78), (.46, .016, .3), dark)
        s.box((sx * .32, -d / 2 - .045, .96), (.36, .07, .06), '#6f5746')
        s.box((sx * .32, -d / 2 - .018, .78), (.1, .012, .05), GALV)
    s.box((-.32, -d / 2 - .01, .5), (.12, .01, .12), '#3f7d3a')
    s.box((.32, -d / 2 - .01, .5), (.12, .01, .12), '#1f5fa8')
    s.box((0, -d / 2 - .006, .62), (.02, .012, .8), dark)
    s.box((0, 0, 1.13), (w + .04, d + .06, .03), '#4a392c', yaw=0)


def yard_waste_bags(s):
    kraft = '#b08a5a'

    def bag(x, y, yaw, height):
        with s.at(x, y, 0, yaw=yaw):
            rings = [[(px * f, py * f, z) for px, py in rounded_rect(.42, .3, .05, 2)] for z, f in ((0, .93), (height * .35, 1.07), (height * .75, 1.0), (height, .9))]
            tones = [s.c(kraft, .05) for _ in rings[0]]
            s.loft(rings, lambda r, i: tones[i], cap_start=True, cap_end=False)
            s.loft([[(px * .92, py * .92, height - .012) for px, py in rounded_rect(.42, .3, .05, 2)], [(px * .9, py * .9, height) for px, py in rounded_rect(.42, .3, .05, 2)]],
                   '#8f6f47', cap_start=False, cap_end=False)
            s.dome((0, 0, height - .05), (.17, .11, .11), s.c('#6f6a3a', .1), nu=8, nv=3, noise=.25)
            for _ in range(9):
                a = s.random() * math.tau
                base = (math.cos(a) * .1, math.sin(a) * .07, height)
                tip = (math.cos(a) * .22, math.sin(a) * .16, height + .05 + s.random() * .12)
                side = (-math.sin(a) * .04, math.cos(a) * .04, 0)
                s.tri(sub(base, side), add(base, side), tip, s.pick(['#8a7a3c', '#a8742c', '#6f7a3c', '#b89a3a'], .08))

    bag(-.42, 0, .1, .86)
    bag(.03, .06, -.15, .9)
    bag(.47, -.03, .22, .82)


def donation_box(s):
    teal, dark = '#1f7a8c', '#175c69'
    w, d, h = 1.2, 1.1, 1.85
    s.box((0, 0, .03), (w + .1, d + .1, .06), '#2b2e31')
    s.box((0, 0, .06 + h / 2), (w, d, h), teal)
    roof_slab(s, (-w / 2 - .05, -d / 2 - .1, h + .07), (w / 2 + .05, -d / 2 - .1, h + .07), (w / 2 + .05, d / 2 + .05, h + .3), (-w / 2 - .05, d / 2 + .05, h + .3), .04, dark, 1,
              underside=dark, jitter=.0)
    for sx in (-1, 1):
        s.tri((sx * w / 2, -d / 2, h + .06), (sx * w / 2, d / 2, h + .06), (sx * w / 2, d / 2, h + .3), teal)
    s.quad((-w / 2, d / 2, h + .06), (w / 2, d / 2, h + .06), (w / 2, d / 2, h + .3), (-w / 2, d / 2, h + .3), teal)
    s.box((0, -d / 2 - .006, .95), (w, .012, .38), WHITE)
    s.box((0, -d / 2 - .012, .95), (.5, .008, .12), '#f0b23a')
    s.box((0, -d / 2 - .008, 1.5), (.78, .016, .34), '#0f2f36')
    with s.at(0, -d / 2 - .01, 1.34, roll=.5):
        s.box((0, 0, .15), (.74, .03, .3), dark)
        s.cyl((-.22, -.04, .24), (.22, -.04, .24), .014, GALV, sides=6)
    for z in (.4, 1.2):
        s.box((w / 2 - .12, d / 2 + .008, z), (.06, .016, .14), GALV)


def padmount_transformer(s):
    green, dark = '#3c6b4a', '#2c5239'
    s.box((0, 0, .05), (1.45, 1.3, .1), CONCRETE)
    w, d = 1.05, .95
    wedge_body(s, w, [(-d / 2, .1), (d / 2, .1), (d / 2, 1.0), (-d / 2 + .14, 1.0), (-d / 2, .84)], green)
    s.box((0, -d / 2 - .004, .47), (.012, .008, .7), dark)
    s.box((.1, -d / 2 - .01, .5), (.1, .02, .05), '#1b1d1f')
    s.box((.1, -d / 2 - .022, .46), (.04, .02, .05), '#c9a13a')
    tri = [(.28, -d / 2 - .006, .28), (.44, -d / 2 - .006, .28), (.36, -d / 2 - .006, .42)]
    s.tri(tri[0], tri[1], tri[2], YELLOW)
    s.tri((.315, -d / 2 - .009, .3), (.405, -d / 2 - .009, .3), (.36, -d / 2 - .009, .385), BLACK)
    for k in range(7):
        s.box((-.42 + k * .14, d / 2 + .04, .55), (.02, .08, .7), dark)
    for sx in (-1, 1):
        s.box((sx * .4, 0, 1.02), (.08, .08, .04), dark)
    s.box((0, 0, 1.005), (w + .03, d + .03, .012), dark)


def signal_cabinet(s):
    alu, line = '#aeb5b9', '#7f878b'
    s.box((0, 0, .1), (.95, .7, .2), CONCRETE)
    s.box((0, 0, .9), (.78, .52, 1.4), alu)
    s.box((0, 0, 1.62), (.86, .62, .04), '#9aa1a5')
    for dz, hh in ((.3, .012), (1.52, .012)):
        s.box((0, -.262, dz), (.7, .006, hh), line)
    for dx in (-.35, .35):
        s.box((dx, -.262, .91), (.012, .006, 1.22), line)
    s.box((.26, -.27, .95), (.04, .02, .16), '#3a3d40')
    for k in range(5):
        s.box((0, -.264, 1.34 + k * .03), (.4, .006, .012), '#3a3d40')
        s.box((0, -.264, .38 + k * .03), (.4, .006, .012), '#3a3d40')
    s.box((.392, .05, 1.2), (.006, .22, .28), line)
    s.box((.398, .05, 1.2), (.006, .03, .05), '#3a3d40')


def street_letter_box(s):
    red, dark = '#c2332b', '#8f231d'
    w, d = .56, .5
    s.box((0, 0, .02), (w + .08, d + .08, .04), CONCRETE)
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * (w / 2 - .05), sy * (d / 2 - .05), .16), (.06, .06, .24), dark)
    s.box((0, 0, .28 + .41), (w, d, .82), red)
    arch_prism(s, w, -d / 2, d / 2, 1.1, .2, red, steps=8)
    s.box((0, -d / 2 - .03, 1.07), (.46, .07, .035), dark)
    s.box((0, -d / 2 - .005, 1.0), (.42, .012, .07), '#1b1d1f')
    s.box((0, -d / 2 - .006, .68), (.3, .012, .18), WHITE)
    s.box((0, -d / 2 - .012, .72), (.22, .006, .02), dark)
    s.box((0, -d / 2 - .012, .66), (.22, .006, .02), dark)
    s.box((0, -d / 2 - .008, .4), (.44, .012, .012), dark)


def newspaper_boxes(s):
    def one(x, colour, yaw, tall):
        with s.at(x, 0, 0, yaw=yaw):
            dark = '#2b2e31'
            s.box((0, 0, .02), (.42, .38, .04), dark)
            s.box((0, 0, .29), (.1, .1, .5), dark)
            s.box((0, 0, .54 + tall / 2), (.46, .4, tall), colour)
            s.box((0, -.205, .54 + tall * .6), (.36, .012, tall * .5), '#1d2b36', gloss=True)
            s.box((0, -.212, .54 + tall * .29), (.3, .012, .04), GALV)
            s.box((.17, -.207, .54 + tall * .12), (.07, .014, .09), '#8a9195')
            wedge_body(s, .46, [(-.2, .54 + tall), (.2, .54 + tall), (.2, .54 + tall + .09)], colour)
    one(-.55, BLUE, .06, .6)
    one(0, YELLOW, -.04, .66)
    one(.55, RED, .03, .6)


def parking_pay_station(s):
    body, blue = STEEL, '#2f5fa8'
    s.box((0, 0, .02), (.42, .36, .04), CONCRETE)
    s.box((0, 0, .64), (.3, .26, 1.2), body)
    s.box((0, 0, 1.44), (.36, .3, .4), blue)
    s.box((0, -.152, 1.5), (.22, .008, .14), '#101820', gloss=True)
    for row in range(4):
        for col in range(3):
            s.box((-.05 + col * .05, -.152, 1.38 - row * .035), (.035, .008, .025), '#d9dde0')
    s.box((.11, -.152, 1.34), (.05, .008, .012), BLACK)
    s.box((0, -.132, 1.02), (.2, .012, .1), '#1b1d1f')
    s.box((0, -.132, .8), (.22, .008, .16), YELLOW)
    s.cyl((0, .06, 1.64), (0, .06, 2.1), .022, GALV, sides=8)
    with s.at(0, .06, 2.1, roll=.6):
        s.box((0, 0, .02), (.5, .36, .03), '#1b2a44', gloss=True)
        s.box((0, 0, .0), (.54, .4, .02), GALV)
    s.box((0, -.02, 1.86), (.36, .02, .36), blue)
    s.box((0, -.032, 1.86), (.2, .008, .2), WHITE)


def bus_bench(s):
    for sx in (-1, 1):
        s.box((sx * .85, 0, .22), (.14, .56, .44), CONCRETE)
        s.box((sx * .85, .23, .72), (.14, .1, .58), CONCRETE)
    for k in range(4):
        s.box((0, -.2 + k * .13, .465), (1.9, .11, .045), s.c(TIMBER, .07))
    s.box((0, .2, .76), (1.86, .035, .5), '#e9e5d8')
    s.box((0, .18, .86), (1.5, .008, .22), '#8fb7c9')
    s.box((0, .18, .64), (1.5, .008, .12), '#d8a657')
    s.box((0, .218, .76), (1.86, .008, .5), '#c9c5b8')


def sandwich_board(s):
    for sy in (-1, 1):
        with s.at(0, sy * .23, 0, roll=sy * .24):
            s.box((0, 0, .475), (.62, .03, .95), s.c(TIMBER, .06))
            s.box((0, sy * .017, .52), (.52, .008, .74), '#24282b')
            for k, (z, width) in enumerate(((.78, .34), (.66, .26), (.52, .38), (.4, .2))):
                s.box((-.02 + (k % 2) * .04, sy * .022, z), (width, .004, .028 if k else .05), '#e9e6da' if k else '#f0d98a')
    s.cyl((-.3, 0, .93), (.3, 0, .93), .012, GALV, sides=6)
    for sx in (-1, 1):
        s.wire((sx * .29, -.12, .5), (sx * .29, .12, .5), .05, .004, GALV, 5)


def shopping_cart(s):
    steel = '#b9c0c4'
    a, b, c, d = (-.17, -.4, .47), (.17, -.4, .47), (.21, .33, .45), (-.21, .33, .45)
    e, f, g, h = (-.24, -.5, .98), (.24, -.5, .98), (.27, .42, 1.0), (-.27, .42, 1.0)
    s.net_quad(a, b, f, e, 6, 7, .008, steel)
    s.net_quad(b, c, g, f, 9, 7, .008, steel)
    s.net_quad(a, d, h, e, 9, 7, .008, steel)
    s.net_quad(d, c, g, h, 7, 7, .008, steel)
    s.net_quad(a, b, c, d, 6, 9, .008, steel)
    for p, q in ((e, f), (f, g), (g, h), (h, e)):
        s.cyl(p, q, .011, steel, sides=5)
    wheels = [(-.19, -.36), (.19, -.36), (-.25, .4), (.25, .4)]
    for x, y in wheels:
        wheel(s, (x, y, .06), .06, .03, tyre='#2b2e31', hub=steel, sides=10)
        s.cyl((x, y, .06), (x, y, .2), .012, steel, sides=5)
    s.tube([(-.19, -.36, .2), (.19, -.36, .2), (.25, .4, .2), (-.25, .4, .2), (-.19, -.36, .2)], .012, steel, sides=5)
    for sx in (-1, 1):
        s.cyl((sx * .25, .4, .2), (sx * .27, .42, 1.0), .012, steel, sides=5)
        s.cyl((sx * .21, .33, .45), (sx * .25, .4, .2), .01, steel, sides=5)
        s.cyl((sx * .27, .42, 1.0), (sx * .27, .55, 1.04), .012, steel, sides=5)
    s.cyl((-.27, .55, 1.04), (.27, .55, 1.04), .016, RED, sides=8)
    s.net_quad((-.2, .3, .62), (.2, .3, .62), (.24, .4, .98), (-.24, .4, .98), 5, 4, .008, steel)


def barbecue(s):
    black, steel = '#1f2124', '#8f979b'
    for sy in (-1, 1):
        s.box((-.36, sy * .2, .425), (.04, .04, .67), black)
        s.box((.36, sy * .2, .38), (.04, .04, .76), black)
    s.box((0, 0, .16), (.78, .46, .03), black)
    for sy in (-1, 1):
        wheel(s, (-.38, sy * .2, .09), .09, .04, axis=(0.0, 1.0, 0.0), sides=10)
    s.box((0, 0, .86), (.82, .5, .22), black)
    with s.at(0, 0, 0, yaw=math.pi / 2):
        arch_prism(s, .5, -.41, .41, .97, .27, '#2a2d31', steps=7)
    s.cyl((-.3, -.3, 1.1), (.3, -.3, 1.1), .016, steel, sides=6)
    for sx in (-1, 1):
        s.cyl((sx * .3, -.3, 1.1), (sx * .3, -.24, 1.08), .012, steel, sides=5)
        s.box((sx * .57, 0, .94), (.3, .42, .03), steel)
        s.box((sx * .43, 0, .9), (.03, .36, .06), black)
    s.box((0, -.26, .82), (.82, .03, .12), steel)
    for x in (-.24, 0, .24):
        s.cyl((x, -.275, .82), (x, -.31, .82), .03, black, sides=10)
    s.cyl((.08, 0, .19), (.08, 0, .5), .15, '#e6e8ea', sides=12)
    s.cyl((.08, 0, .5), (.08, 0, .56), .1, '#e6e8ea', r1=.06, sides=12)
    s.cyl((0, -.255, 1.12), (0, -.262, 1.12), .035, '#d9dde0', sides=10)


def adirondack_chair(s, colour):
    for k in range(5):
        t = (k + .5) / 5
        with s.at(0, -.36 + .6 * t, .39 - .14 * t, roll=-.23):
            s.box((0, 0, 0), (.56, .112, .022), s.c(colour, .05))
    for k in range(5):
        offset = k - 2
        with s.at(offset * .113, .26, .24, roll=-.4):
            height = .86 - .09 * abs(offset)
            s.box((0, 0, height / 2), (.105, .02, height), s.c(colour, .05))
    with s.at(0, .26, .24, roll=-.4):
        s.box((0, .016, .3), (.56, .02, .07), colour)
        s.box((0, .016, .58), (.5, .02, .07), colour)
    for sx in (-1, 1):
        s.box((sx * .34, -.06, .585), (.13, .76, .025), s.c(colour, .04))
        s.box((sx * .33, -.38, .29), (.09, .025, .58), colour)
        s.cyl((sx * .31, .46, .03), (sx * .31, .12, .32), .035, colour, sides=4)
        s.box((sx * .31, .14, .46), (.025, .09, .26), colour)
    s.box((0, -.37, .3), (.6, .025, .09), colour)


def adirondack_chairs(s):
    with s.at(-.62, 0, 0, yaw=-.3):
        adirondack_chair(s, '#b23a34')
    with s.at(.62, 0, 0, yaw=.3):
        adirondack_chair(s, '#2f6f8f')
    for k in range(4):
        s.box((0, -.32 + k * .1, .42), (.36, .09, .022), s.c(TIMBER, .06))
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * .15, -.17 + sy * .15, .205), (.04, .04, .41), TIMBER)


def rotary_clothesline(s):
    s.cyl((0, 0, 0), (0, 0, .06), .07, CONCRETE, sides=10)
    s.cyl((0, 0, 0), (0, 0, 1.95), .022, GALV, sides=8)
    arms = []
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        tip = (math.cos(a) * 1.3, math.sin(a) * 1.3, 2.08)
        arms.append(tip)
        s.cyl((0, 0, 1.78), tip, .012, GALV, sides=5)
        s.cyl((0, 0, 1.4), mix((0, 0, 1.78), tip, .55), .008, GALV, sides=4)
    hub = (0, 0, 1.78)
    cloths = ['#d9dde0', '#c2332b', '#2f5fa8', '#e0b63a', '#7fb7a4', '#f1ede3']
    for ring, f in enumerate((.4, .6, .8, .98)):
        for k in range(4):
            p, q = mix(hub, arms[k], f), mix(hub, arms[(k + 1) % 4], f)
            s.ribbon(p, q, .008, WHITE)
            if ring >= 2 and (k + ring) % 2 == 0:
                # a towel or shirt pegged along this run of line
                for j in range(2 if ring == 3 else 1):
                    t0 = .12 + j * .45 + s.random() * .05
                    t1 = t0 + .22 + s.random() * .1
                    a0, a1 = mix(p, q, t0), mix(p, q, min(.95, t1))
                    drop = .45 + s.random() * .35
                    sway = (s.random() - .5) * .08
                    s.quad(a0, a1, (a1[0] + sway, a1[1] + sway, a1[2] - drop), (a0[0] + sway, a0[1] + sway, a0[2] - drop), s.pick(cloths, .04))


BIKE_LEAN = -.13  # radians toward the kickstand side


def bicycle(s, colour, saddle='#1d1f22', kickstand=True):
    radius = .34
    rear, front = (0, .52, radius), (0, -.52, radius)
    for hub in (rear, front):
        spoked_wheel(s, hub, radius)
    bracket, seat, head_top, head_bottom = (0, .1, .27), (0, .22, .82), (0, -.36, .86), (0, -.39, .7)
    for a, b, r in ((bracket, seat, .016), (seat, head_top, .015), (bracket, head_bottom, .017), (head_bottom, head_top, .02)):
        s.cyl(a, b, r, colour, sides=6)
    for sx in (-1, 1):
        s.cyl((sx * .03, bracket[1], bracket[2]), (sx * .04, rear[1], rear[2]), .009, colour, sides=5)
        s.cyl((sx * .02, seat[1], seat[2]), (sx * .04, rear[1], rear[2]), .008, colour, sides=5)
        s.cyl((sx * .03, head_bottom[1], head_bottom[2]), (sx * .04, front[1], front[2]), .011, colour, sides=5)
    s.cyl(head_top, (0, -.38, .99), .013, GALV, sides=6)
    s.cyl((-.28, -.4, .99), (.28, -.4, .99), .012, GALV, sides=6)
    for sx in (-1, 1):
        s.cyl((sx * .2, -.4, .99), (sx * .29, -.4, .99), .017, '#1b1d1f', sides=6)
    s.cyl(seat, (0, .25, .9), .012, GALV, sides=6)
    s.box((0, .27, .92), (.13, .26, .045), saddle)
    s.cyl((.045, bracket[1], bracket[2]), (.052, bracket[1], bracket[2]), .09, GALV, sides=14)
    for sx, a in ((1, .9), (-1, .9 + math.pi)):
        pedal = (sx * .09, bracket[1] + math.cos(a) * .17, bracket[2] + math.sin(a) * .17)
        s.cyl((sx * .06, bracket[1], bracket[2]), pedal, .008, GALV, sides=4)
        s.box(pedal, (.09, .06, .02), '#1b1d1f')
    if kickstand:
        # Short enough that, leaned BIKE_LEAN onto it, the foot and both tyres touch down together.
        s.cyl((-.04, .28, .3), (-.2, .34, .034), .008, GALV, sides=4)
    # rear mudguard over the top of the wheel only
    s.tube([(0, rear[1] + math.cos(a) * (radius + .022), rear[2] + math.sin(a) * (radius + .022)) for a in (.1, .5, .95, 1.4, 1.85, 2.3, 2.65)], .009, colour, sides=4)


def leaned_bicycle(s, colour, y=0.0):
    with s.at(0, y, .003, pitch=BIKE_LEAN):
        bicycle(s, colour)


def parked_bicycle(s):
    leaned_bicycle(s, '#1f7a8c')


def bike_with_trailer(s):
    leaned_bicycle(s, '#2f5fa8', y=-.78)
    blue, yellow, frame = '#2f5fa8', '#e7b93a', GALV
    # two-wheel child trailer: tub, canopy, clear front, mesh sides, hitch arm and flag
    for sx in (-1, 1):
        spoked_wheel(s, (sx * .4, .98, .25), .25, spokes=6)
        s.box((sx * .316, 1.02, .72), (.006, .46, .2), '#22313c', gloss=True)
        s.cyl((sx * .31, 1.4, .84), (sx * .31, 1.62, .96), .012, frame, sides=5)
    s.cyl((-.4, .98, .25), (.4, .98, .25), .012, frame, sides=5)
    s.cyl((-.31, 1.62, .96), (.31, 1.62, .96), .014, '#1b1d1f', sides=6)
    wedge_body(s, .62, [(.46, .22), (1.44, .22), (1.44, .56), (.46, .56)], blue)
    wedge_body(s, .62, [(.46, .56), (1.44, .56), (1.44, .82), (1.16, .98), (.82, .98)], yellow)
    s.quad((-.25, .508, .625), (.25, .508, .625), (.25, .771, .948), (-.25, .771, .948), '#cfe0ea', gloss=True)
    s.box((0, 1.446, .5), (.5, .008, .4), '#24476f')
    s.tube([(-.28, .47, .26), (-.3, .2, .3), (-.1, -.26, .335)], .012, frame, sides=5)
    s.cyl((.29, 1.42, .82), (.29, 1.5, 1.72), .004, WHITE, sides=3)
    s.tri((.29, 1.5, 1.72), (.29, 1.485, 1.56), (.29, 1.72, 1.64), ORANGE)


def kids_bikes(s):
    def dropped(colour, x, y, yaw, side, scale, saddle='#1d1f22'):
        def draw():
            with s.at(x, y, .4, yaw=yaw, pitch=side * 1.36, scale=scale):
                bicycle(s, colour, saddle=saddle, kickstand=False)
        rest_on_ground(s, draw)

    dropped('#c2332b', -.45, 0, .5, 1, .62)
    dropped('#e0b63a', .55, .25, -2.2, -1, .56, saddle='#2f5fa8')
    s.dome((.05, -.55, 0), (.11, .14, .1), '#2f5fa8', nu=10, nv=4)
    s.box((.05, -.55, .012), (.06, .2, .02), '#1b1d1f')


def wheelbarrow(s):
    green = '#3f7d3a'
    bottom = [(-.2, -.28, .34), (.2, -.28, .34), (.22, .3, .34), (-.22, .3, .34)]
    top = [(-.33, -.56, .6), (.33, -.56, .6), (.31, .42, .58), (-.31, .42, .58)]
    s.loft([bottom, top], green, cap_start=True, cap_end=False)
    s.dome((0, -.04, .5), (.25, .4, .16), s.c('#4a3a2c', .08), nu=10, nv=3, noise=.12)
    wheel(s, (0, -.66, .19), .19, .08, sides=14)
    for sx in (-1, 1):
        s.cyl((sx * .06, -.66, .19), (sx * .2, -.26, .34), .014, STEEL, sides=5)
        s.cyl((sx * .2, -.3, .34), (sx * .3, 1.0, .62), .02, s.c(TIMBER, .05), sides=6)
        s.cyl((sx * .24, .36, .36), (sx * .27, .42, 0), .014, STEEL, sides=5)
    s.cyl((-.27, .42, .02), (.27, .42, .02), .012, STEEL, sides=5)
    s.cyl((.08, .1, .5), (.2, .42, 1.28), .016, s.c(TIMBER, .05), sides=6)
    s.cyl((.14, .4, 1.28), (.26, .44, 1.28), .014, s.c(TIMBER, .05), sides=5)


def barrel_planter(s):
    n = 16
    oak = [s.c(c, .05) for c in ('#7a5a3c', '#8a6846', '#6c4f34')]
    rings = [[(math.cos(i * math.tau / n) * r, math.sin(i * math.tau / n) * r, z) for i in range(n)] for z, r in ((0, .27), (.12, .31), (.28, .335), (.42, .32))]
    s.loft(rings, lambda r, i: oak[i % 3], cap_start=True, cap_end=False)
    for z, r in ((.06, .297), (.3, .338)):
        s.cyl((0, 0, z), (0, 0, z + .03), r, '#3a3d40', sides=n, cap0=False, cap1=False)
    s.disc((0, 0, .39), .31, '#3d3027', n)
    for k in range(22):
        a, r = k * 2.399963, .26 * math.sqrt((k + .5) / 22)
        x, y = math.cos(a) * r, math.sin(a) * r
        top = .5 + s.random() * .2
        s.cyl((x * .6, y * .6, .39), (x, y, top), .005, '#5a7a45', sides=3, cap0=False, cap1=False)
        s.dome((x, y, top - .06), (.07, .07, .03), s.pick(['#5a7a45', '#6c8a52', '#4a6a3c'], .08), nu=6, nv=2)
        if k % 2 == 0:
            s.dome((x, y, top), (.045, .045, .04), s.pick(['#c2332b', '#d4493f', '#b02a3a'], .06), nu=6, nv=3, full=True)
    for k in range(7):
        a = k * .9 + .3
        p = (math.cos(a) * .3, math.sin(a) * .3, .42)
        q = (math.cos(a) * .37, math.sin(a) * .37, .22 + s.random() * .1)
        s.cyl(p, q, .005, '#5a7a45', sides=3, cap0=False, cap1=False)
        s.dome(q, (.04, .04, .03), '#6c8a52', nu=5, nv=2)


def portable_hoop(s):
    black, grey = '#1d1f22', '#6f777c'
    s.prism(rounded_rect(.85, 1.15, .1, 3), 0, .24, black)
    s.cyl((.2, .3, .24), (.2, .3, .27), .05, grey, sides=8)
    for sx in (-1, 1):
        wheel(s, (sx * .3, -.6, .06), .06, .05, tyre=black, hub=grey, sides=8)
    s.cyl((0, .35, .2), (0, -.1, 2.95), .045, grey, sides=4)
    for sx in (-1, 1):
        s.cyl((sx * .3, -.35, .24), (0, .16, 1.25), .016, grey, sides=4)
    board_y = -.62
    s.box((0, board_y, 3.25), (1.12, .035, .76), '#e3e9ee', gloss=True)
    for dz in (-.38, .38):
        s.box((0, board_y, 3.25 + dz), (1.14, .045, .03), black)
    for dx in (-.56, .56):
        s.box((dx, board_y, 3.25), (.03, .045, .76), black)
    for dz, hh, ww in ((3.05, .02, .46), (3.39, .02, .46)):
        s.box((0, board_y - .02, dz), (ww, .006, hh), RED)
    for dx in (-.23, .23):
        s.box((dx, board_y - .02, 3.22), (.02, .006, .34), RED)
    for sx in (-1, 1):
        s.cyl((sx * .04, -.1, 2.95), (sx * .2, board_y + .03, 3.12), .014, grey, sides=4)
        s.cyl((sx * .04, -.14, 2.7), (sx * .2, board_y + .03, 3.38), .014, grey, sides=4)
    rim_centre = (0, board_y - .27, 3.05)
    s.torus(rim_centre, .225, .011, ORANGE, nu=18, nv=4)
    s.box((0, board_y - .03, 3.05), (.12, .05, .01), ORANGE)
    for k in range(12):
        a = k * math.tau / 12
        p = (rim_centre[0] + math.cos(a) * .225, rim_centre[1] + math.sin(a) * .225, 3.04)
        q = (rim_centre[0] + math.cos(a + .26) * .13, rim_centre[1] + math.sin(a + .26) * .13, 2.64)
        s.ribbon(p, q, .01, '#f2f4f5', normal=(math.cos(a), math.sin(a), 0))
    for z, r in ((2.9, .19), (2.76, .155), (2.64, .13)):
        s.torus((rim_centre[0], rim_centre[1], z), r, .004, '#f2f4f5', nu=12, nv=3)


def sandbox(s):
    size, wood = 1.8, TIMBER
    half = size / 2
    for sy in (-1, 1):
        s.box((0, sy * (half - .045), .12), (size, .09, .24), s.c(wood, .06))
    for sx in (-1, 1):
        s.box((sx * (half - .045), 0, .12), (.09, size - .18, .24), s.c(wood, .06))
        for sy in (-1, 1):
            corner = [(sx * half, sy * half), (sx * (half - .45), sy * half), (sx * half, sy * (half - .45))]
            if sx * sy < 0:
                corner = [corner[0], corner[2], corner[1]]
            s.prism(corner, .24, .27, s.c('#a98862', .05), bottom=True)
    s.box((0, 0, .085), (size - .18, size - .18, .17), '#d9c79a')
    s.dome((.3, .28, .17), (.42, .36, .14), '#d3c092', nu=10, nv=3, noise=.08)
    s.cyl((-.38, -.3, .17), (-.38, -.3, .34), .085, RED, r1=.11, sides=10, cap1=False)
    s.torus((-.38, -.3, .36), .1, .006, WHITE, nu=10, nv=3, axis='y')
    s.box((-.1, -.5, .185), (.07, .2, .012), YELLOW, yaw=.5)
    s.box((-.02, -.38, .19), (.03, .16, .03), YELLOW, yaw=.5)
    with s.at(.2, -.45, .17, yaw=-.4):
        s.box((0, 0, .06), (.14, .3, .06), YELLOW)
        s.box((0, -.09, .12), (.13, .1, .08), YELLOW)
        with s.at(0, .06, .1, roll=-.35):
            s.box((0, 0, .03), (.14, .18, .06), ORANGE)
        for sx in (-1, 1):
            for y in (-.09, .09):
                wheel(s, (sx * .075, y, .035), .035, .025, sides=8)
    s.dome((-.5, .42, .28), (.1, .1, .1), BLUE, nu=10, nv=5, full=True)


def snowman(s):
    tones = ['#f4f7fa', '#e3ebf2', '#d3dfea', '#eef3f8']
    for centre, radii in (((0, 0, .43), (.48, .48, .43)), ((0, 0, 1.0), (.36, .36, .33)), ((0, 0, 1.47), (.25, .25, .24))):
        s.dome(centre, radii, lambda j, i: s.pick(tones, .015), nu=12, nv=7, noise=.035, full=True)
    coal = '#1f2124'
    for sx in (-1, 1):
        s.dome((sx * .085, -.215, 1.54), (.028, .028, .028), coal, nu=6, nv=3, full=True)
        shoulder, hand = (sx * .32, 0, 1.08), (sx * .78, -.08, 1.36)
        s.cyl(shoulder, hand, .016, '#5a4636', r1=.009, sides=5)
        for twig in (-.5, .6):
            s.cyl(mix(shoulder, hand, .82), (hand[0] + sx * .04, hand[1] + twig * .18, hand[2] + .12), .007, '#5a4636', sides=4)
    s.cyl((0, -.24, 1.47), (0, -.46, 1.45), .034, ORANGE, r1=.002, sides=8)
    for k in range(5):
        a = -.6 + k * .3
        s.dome((math.sin(a) * .12, -.225 - (1 - abs(a)) * .012, 1.4 - math.cos(a) * .035), (.016, .016, .016), coal, nu=5, nv=3, full=True)
    for z, y in ((.88, -.345), (1.0, -.36), (1.12, -.335)):
        s.dome((0, y, z), (.03, .03, .03), coal, nu=6, nv=3, full=True)
    s.torus((0, 0, 1.285), .25, .05, RED, nu=16, nv=6)
    s.box((.14, -.27, 1.1), (.1, .04, .34), RED)
    s.box((.14, -.275, .95), (.1, .03, .04), '#f0d98a')
    toque = '#2f5fa8'
    s.dome((0, 0, 1.6), (.225, .225, .2), toque, nu=12, nv=5)
    s.cyl((0, 0, 1.56), (0, 0, 1.64), .235, '#f0d98a', sides=12, cap0=False, cap1=False)
    s.dome((0, 0, 1.83), (.06, .06, .06), '#f4f7fa', nu=8, nv=4, full=True)


def toboggan_and_sled(s):
    profile = [(.9, .03), (-.5, .03), (-.72, .08), (-.86, .2), (-.88, .36), (-.8, .46), (-.68, .48)]
    for k in range(6):
        x = -.17 + k * .068
        tone = s.c(('#b8894f', '#a87a44', '#c49a60')[k % 3], .05)
        for (y0, z0), (y1, z1) in zip(profile, profile[1:]):
            s.quad((x - .03, y0, z0), (x + .03, y0, z0), (x + .03, y1, z1), (x - .03, y1, z1), tone)
    for y in (.75, .35, -.05, -.42):
        s.box((0, y, .05), (.44, .05, .025), '#8a6a44')
    for sx in (-1, 1):
        s.wire((sx * .2, -.68, .48), (sx * .2, .7, .07), .12, .006, YELLOW, 6)
    with s.at(.85, -.2, 0, yaw=.4):
        s.cyl((0, 0, 0), (0, 0, .05), .3, RED, r1=.36, sides=18, cap1=False)
        s.torus((0, 0, .05), .36, .014, '#a82a23', nu=18, nv=4)
        for sx in (-1, 1):
            s.torus((sx * .3, 0, .07), .05, .008, '#f2f4f5', nu=8, nv=3, axis='y')


def camping_trailer(s):
    length, width, floor = 4.3, 2.1, .55
    white, trim, dark = '#eceef0', '#1f7a8c', '#2b2e31'
    section = rounded_rect(width, 2.0, .26, 4)
    stations = [(-length / 2, .8, .84), (-length / 2 + .16, .93, .95), (-length / 2 + .5, 1.0, 1.0), (length / 2 - .5, 1.0, 1.0), (length / 2 - .16, .95, .97), (length / 2, .85, .9)]
    rings = [[(x * ws, y, floor + (z + 1.0) * hs) for x, z in section] for y, ws, hs in stations]
    s.loft(rings, white)
    for sx in (-1, 1):
        x = sx * (width / 2 + .004)
        s.box((x, .05, 1.36), (.012, length - 1.1, .2), trim)
        s.box((x, .05, 1.2), (.012, length - 1.1, .05), ORANGE)
        wheel(s, (sx * (width / 2 - .1), .4, .33), .33, .2, sides=14)
        s.box((sx * (width / 2 - .02), .4, .74), (.26, .92, .05), dark)
        for y in (-length / 2 + .35, length / 2 - .3):
            s.cyl((sx * .8, y, floor), (sx * .8, y, .02), .022, GALV, sides=5)
            s.box((sx * .8, y, .012), (.14, .14, .024), GALV)
    s.box((0, 0, floor - .06), (width - .3, length - .1, .12), dark)

    def window(side, y, z, w, h):
        x = side * (width / 2 + .006)
        s.box((x, y, z), (.012, w + .08, h + .08), '#d3d7da')
        s.box((x + side * .004, y, z), (.012, w, h), '#22313c', gloss=True)

    window(-1, -.9, 1.82, 1.0, .58)
    window(-1, .95, 1.82, .8, .58)
    window(1, -1.0, 1.82, .9, .58)
    x = width / 2 + .006
    s.box((x, .75, floor + .92), (.012, .66, 1.8), '#d3d7da')
    s.box((x + .004, .75, floor + .92), (.012, .58, 1.72), '#f4f5f6')
    s.box((x + .008, .75, floor + 1.4), (.012, .36, .4), '#22313c', gloss=True)
    s.box((x + .012, .51, floor + .85), (.02, .04, .1), GALV)
    s.box((x + .18, .75, .3), (.3, .62, .04), dark)
    s.box((0, -length / 2 - .004, 1.85), (1.2, .012, .5), '#22313c', gloss=True)
    s.box((0, length / 2 + .004, 1.85), (1.0, .012, .45), '#22313c', gloss=True)
    for sx in (-1, 1):
        s.box((sx * .8, length / 2 + .01, 1.0), (.18, .02, .1), RED)
        s.cyl((sx * .55, -length / 2 + .1, floor - .06), (0, -length / 2 - 1.15, .5), .04, dark, sides=4)
        s.cyl((sx * .2, -length / 2 - .42, .56), (sx * .2, -length / 2 - .42, 1.0), .15, '#e6e8ea', sides=12)
        s.cyl((sx * .2, -length / 2 - .42, 1.0), (sx * .2, -length / 2 - .42, 1.06), .1, '#e6e8ea', r1=.05, sides=12)
    s.box((0, length / 2 + .012, .78), (.3, .012, .15), WHITE)
    s.box((0, -length / 2 - 1.18, .5), (.12, .16, .1), GALV)
    s.cyl((0, -length / 2 - .8, .02), (0, -length / 2 - .8, .78), .03, GALV, sides=8)
    s.box((0, -length / 2 - .8, .012), (.18, .18, .024), GALV)
    s.box((0, -length / 2 - .42, .5), (.6, .34, .06), dark)
    s.box((0, .3, floor + 2.0 + .1), (.7, .9, .2), WHITE)
    s.box((0, -1.2, floor + 2.0 + .05), (.36, .36, .1), '#d3d7da')
    s.cyl((width / 2 + .07, -1.5, 2.42), (width / 2 + .07, 1.5, 2.42), .06, '#d9dde0', sides=10)
    for y in (-1.5, 1.5):
        s.cyl((width / 2 + .07, y - .02, 2.42), (width / 2 + .07, y + .02, 2.42), .07, dark, sides=10)


def patio_heater(s):
    steel = '#b4bbbf'
    s.cyl((0, 0, 0), (0, 0, .05), .25, '#2b2e31', sides=16)
    s.cyl((0, 0, .05), (0, 0, .8), .2, steel, r1=.17, sides=16)
    s.cyl((0, 0, .8), (0, 0, .87), .17, steel, r1=.04, sides=16)
    s.cyl((0, 0, .87), (0, 0, 1.82), .03, steel, sides=8)
    s.box((0, -.2, .45), (.12, .012, .2), '#8f979b')
    s.cyl((0, 0, 1.82), (0, 0, 1.88), .06, '#3a3d40', r1=.1, sides=12)
    s.cyl((0, 0, 1.88), (0, 0, 2.06), .1, '#e8743a', sides=12, cap0=False, cap1=False)
    for k in range(12):
        a = k * math.tau / 12
        s.cyl((math.cos(a) * .104, math.sin(a) * .104, 1.88), (math.cos(a) * .104, math.sin(a) * .104, 2.06), .005, '#3a3d40', sides=3, cap0=False, cap1=False)
    s.cyl((0, 0, 2.06), (0, 0, 2.09), .11, '#3a3d40', sides=12)
    s.cyl((0, 0, 2.09), (0, 0, 2.2), .43, steel, r1=.07, sides=20)
    s.torus((0, 0, 2.09), .43, .01, '#8f979b', nu=20, nv=4)
    s.box((.03, 0, 1.8), (.05, .03, .05), BLACK)
    for sy in (-1, 1):
        wheel(s, (-.22, sy * .1, .05), .05, .03, axis=(0.0, 1.0, 0.0), sides=8)


def park_grill(s):
    black = '#1f2124'
    s.box((0, 0, .04), (1.0, 1.0, .08), CONCRETE)
    s.cyl((0, 0, .08), (0, 0, .86), .045, black, sides=8)
    w, d, h, z = .52, .4, .2, .86
    s.box((0, 0, z + .01), (w, d, .02), black)
    for sy in (-1, 1):
        s.box((0, sy * (d / 2 - .008), z + h / 2), (w, .016, h), black)
    for sx in (-1, 1):
        s.box((sx * (w / 2 - .008), 0, z + h / 2), (.016, d, h), black)
    s.box((0, 0, z + .035), (w - .04, d - .04, .01), '#6f7275')
    s.net_quad((-w / 2 + .02, -d / 2 + .02, z + .15), (w / 2 - .02, -d / 2 + .02, z + .15), (w / 2 - .02, d / 2 - .02, z + .15), (-w / 2 + .02, d / 2 - .02, z + .15), 12, 2, .01, '#4a4d50')
    s.cyl((0, -d / 2, z + .15), (0, -d / 2 - .22, z + .17), .012, black, sides=5)
    s.cyl((0, -d / 2 - .18, z + .17), (0, -d / 2 - .3, z + .17), .02, s.c(TIMBER, .05), sides=6)
    s.box((w / 2 + .14, 0, z + .14), (.26, .3, .02), '#3a3d40')


def disc_golf_basket(s):
    s.cyl((0, 0, 0), (0, 0, .04), .1, GALV, sides=10)
    s.cyl((0, 0, 0), (0, 0, 1.44), .022, GALV, sides=8)
    tray, wall, n = .62, .8, 18
    s.torus((0, 0, tray), .33, .008, GALV, nu=n, nv=4)
    s.torus((0, 0, wall), .33, .008, GALV, nu=n, nv=4)
    for k in range(n):
        a = k * math.tau / n
        x, y = math.cos(a) * .33, math.sin(a) * .33
        s.cyl((x, y, tray), (x, y, wall), .004, GALV, sides=3, cap0=False, cap1=False)
        if k % 2 == 0:
            s.cyl((0, 0, tray - .04), (x, y, tray), .004, GALV, sides=3, cap0=False, cap1=False)
    top = 1.32
    s.cyl((0, 0, top - .02), (0, 0, top + .08), .285, YELLOW, sides=n, cap0=False, cap1=False)
    s.disc((0, 0, top + .08), .285, YELLOW, n)
    for k in range(12):
        a = k * math.tau / 12
        points = [(math.cos(a) * .27, math.sin(a) * .27, top - .02), (math.cos(a) * .21, math.sin(a) * .21, 1.05), (math.cos(a) * .05, math.sin(a) * .05, .8)]
        s.tube(points, .004, '#c9cdd0', sides=3)
        if k % 2 == 0:
            b = a + .26
            inner = [(math.cos(b) * .15, math.sin(b) * .15, top - .02), (math.cos(b) * .11, math.sin(b) * .11, 1.05), (math.cos(b) * .04, math.sin(b) * .04, .84)]
            s.tube(inner, .004, '#c9cdd0', sides=3)
    s.box((0, 0, top + .16), (.2, .012, .14), WHITE)


def traffic_barrel(s):
    s.cyl((0, 0, 0), (0, 0, .07), .34, '#1b1d1f', sides=16)
    bands = [(.07, .3, ORANGE), (.3, .42, WHITE), (.42, .6, ORANGE), (.6, .72, WHITE), (.72, .96, ORANGE)]
    for z0, z1, colour in bands:
        r0, r1 = .275 - .055 * (z0 - .07) / .89, .275 - .055 * (z1 - .07) / .89
        s.cyl((0, 0, z0), (0, 0, z1), r0, colour, r1=r1, sides=16, cap0=False, cap1=z1 > .9)
    for sx in (-1, 1):
        s.box((sx * .1, 0, .99), (.03, .05, .06), ORANGE)
    s.box((0, 0, 1.03), (.26, .05, .03), ORANGE)


def construction_fence(s):
    w, h = 2.9, 1.85
    for sx in (-1, 1):
        s.cyl((sx * w / 2, 0, .1), (sx * w / 2, 0, h), .02, GALV, sides=6)
        s.box((sx * w / 2, 0, .07), (.24, .72, .14), '#8a8f92')
        s.box((sx * w / 2, 0, .145), (.2, .2, .012), ORANGE)
    for z in (.26, h):
        s.cyl((-w / 2, 0, z), (w / 2, 0, z), .016, GALV, sides=5)
    s.cyl((0, 0, .26), (0, 0, h), .012, GALV, sides=5)
    s.net_quad((-w / 2, 0, .26), (w / 2, 0, .26), (w / 2, 0, h), (-w / 2, 0, h), 26, 7, .006, '#aab1b4')


def portable_toilet(s):
    blue, dark, light = '#2a66a8', '#1f4f85', '#3b7cc2'
    w, d, h = 1.12, 1.2, 2.2
    s.box((0, 0, .06), (w + .08, d + .08, .12), '#2b2e31')
    s.box((0, 0, .12 + h / 2), (w, d, h), blue)
    arch_prism(s, w + .08, -d / 2 - .04, d / 2 + .04, .12 + h, .13, '#e9eef2', steps=6, gloss=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * w / 2, sy * d / 2, .12 + h / 2), (.07, .07, h), dark)
        for k in range(3):
            s.box((sx * (w / 2 + .004), 0, 2.02 + k * .06), (.008, .7, .025), '#14181c')
    s.box((0, -d / 2 - .008, .12 + .96), (.86, .016, 1.88), light)
    for dx in (-.43, .43):
        s.box((dx, -d / 2 - .014, .12 + .96), (.03, .012, 1.9), dark)
    s.box((0, -d / 2 - .014, .12 + 1.9), (.89, .012, .03), dark)
    s.box((.3, -d / 2 - .02, 1.15), (.1, .02, .14), '#d9dde0')
    s.box((.3, -d / 2 - .032, 1.19), (.05, .008, .03), '#3fae5a')
    for z in (.5, 1.75):
        s.box((-.42, -d / 2 - .02, z), (.04, .02, .1), GALV)
    for k in range(3):
        s.box((0, -d / 2 - .016, 2.02 + k * .06 - .03), (.5, .01, .025), '#14181c')
    s.cyl((w / 2 - .12, d / 2 - .12, 1.7), (w / 2 - .12, d / 2 - .12, 2.6), .045, '#2b2e31', sides=8)


def chickadee(s):
    """Small perched songbird facing +x, about 13 cm long."""
    grey, buff, black, white = '#7d8187', '#dccbae', '#1b1c1e', '#f2f0ea'
    s.dome((0, 0, .04), (.06, .036, .036), buff, nu=8, nv=4, full=True)
    s.dome((-.004, 0, .042), (.062, .038, .037), grey, nu=8, nv=2)
    s.dome((.046, 0, .078), (.028, .027, .027), white, nu=8, nv=4, full=True)
    s.dome((.044, 0, .08), (.031, .029, .028), black, nu=8, nv=2)
    s.box((.066, 0, .062), (.014, .026, .016), black)
    s.cyl((.07, 0, .08), (.09, 0, .078), .006, black, r1=.001, sides=4)
    with s.at(-.05, 0, .045, pitch=-.25):
        s.box((-.05, 0, 0), (.09, .02, .008), '#5d6166')


def bird_feeder(s):
    dark, cedar = '#2b2e31', CEDAR
    s.cyl((0, 0, 0), (0, 0, 1.76), .02, dark, sides=8)
    s.cyl((0, 0, 1.02), (0, 0, 1.16), .19, dark, r1=.03, sides=14, cap0=False, cap1=False)
    s.box((0, 0, 1.77), (.4, .3, .02), s.pick(cedar, .04))
    for sy in (-1, 1):
        s.box((0, sy * .14, 1.79), (.4, .02, .03), s.pick(cedar, .04))
    for sx in (-1, 1):
        s.box((sx * .19, 0, 1.79), (.02, .26, .03), s.pick(cedar, .04))
        s.box((sx * .1, 0, 1.9), (.016, .16, .24), s.pick(cedar, .04))
        s.tri((sx * .1, -.08, 2.02), (sx * .1, .08, 2.02), (sx * .1, 0, 2.1), s.pick(cedar, .04))
    s.box((0, 0, 1.86), (.19, .12, .15), '#b08a4a')
    for sy in (-1, 1):
        s.box((0, sy * .066, 1.9), (.19, .006, .22), '#d8e4ea', gloss=True)
    green = '#3f5d4a'
    roof_slab(s, (-.22, -.2, 1.98), (.22, -.2, 1.98), (.22, 0, 2.1), (-.22, 0, 2.1), .016, green, 1, underside=green, jitter=.0)
    roof_slab(s, (.22, .2, 1.98), (-.22, .2, 1.98), (-.22, 0, 2.1), (.22, 0, 2.1), .016, green, 1, underside=green, jitter=.0)
    s.tube([(0, 0, 1.4), (.26, 0, 1.62), (.44, 0, 1.58)], .008, dark, sides=5)
    s.cyl((.44, 0, 1.58), (.44, 0, 1.5), .003, dark, sides=3)
    s.cyl((.44, 0, 1.5), (.44, 0, 1.46), .012, dark, r1=.05, sides=10)
    s.cyl((.44, 0, 1.18), (.44, 0, 1.46), .045, '#8a7448', sides=10)
    s.cyl((.44, 0, 1.15), (.44, 0, 1.18), .085, dark, sides=10)
    s.cyl((.44, -.045, 1.25), (.44, -.13, 1.25), .005, dark, sides=4)
    with s.at(.05, -.13, 1.805, yaw=-1.1, scale=.82):
        chickadee(s)
    with s.at(.44, -.115, 1.255, yaw=math.pi / 2, scale=.82):
        chickadee(s)


def telecom_pedestals(s):
    sage, sage_dark, green = '#8f9a8c', '#778273', '#4f7a5a'
    with s.at(-.27, 0, 0):
        s.box((0, 0, .02), (.38, .38, .04), CONCRETE)
        s.box((0, 0, .44), (.28, .28, .8), sage)
        s.box((0, 0, .86), (.31, .31, .04), sage_dark)
        s.box((0, -.143, .5), (.21, .006, .52), sage_dark)
        s.box((.07, -.148, .5), (.02, .008, .05), '#3a3d40')
        for k in range(4):
            s.box((0, -.143, .79 + k * .014), (.16, .006, .006), '#3a3d40')
    with s.at(.26, .06, 0):
        s.cyl((0, 0, 0), (0, 0, .72), .1, green, sides=12, cap1=False)
        s.dome((0, 0, .72), (.1, .1, .07), '#456c50', nu=12, nv=3)
        s.cyl((0, 0, .34), (0, 0, .36), .104, '#3d6047', sides=12, cap0=False, cap1=False)
        s.box((0, -.1, .52), (.05, .012, .07), '#3a3d40')


def firewood_stack(s):
    length, depth = 1.9, .42
    for sx in (-1, 1):
        s.box((sx * (length / 2 + .04), 0, .62), (.08, .08, 1.24), s.c(WEATHERED[0], .05))
    for sy in (-1, 1):
        s.box((0, sy * .13, .05), (length + .16, .07, .08), s.c(WEATHERED[1], .05))
    bark, cut = ['#6b5a48', '#7a6652', '#5c4c3c', '#857059'], ['#d8b98a', '#c9a877', '#e0c497']
    z = .09
    while z < 1.02:
        x, tallest = -length / 2 + .01, 0.0
        while True:
            r = .058 + s.random() * .03
            if x + 2 * r > length / 2 - .01:
                break
            shift = (s.random() - .5) * .05
            centre_z = z + r
            s.cyl((x + r, -depth / 2 + shift, centre_z), (x + r, depth / 2 + shift, centre_z), r, s.pick(bark, .05), sides=5, cap0=False, cap1=False)
            for y in (-depth / 2 + shift - .001, depth / 2 + shift + .001):
                with s.at(x + r, y, centre_z, roll=math.pi / 2):
                    s.disc((0, 0, 0), r * .98, s.pick(cut, .04), sides=5)
            x += 2 * r
            tallest = max(tallest, 2 * r)
        z += tallest * .9
    # chopping block with an axe left in it
    with s.at(length / 2 + .62, -.05, 0):
        s.cyl((0, 0, 0), (0, 0, .42), .21, s.c('#6b5a48', .04), r1=.19, sides=10, cap1=False)
        s.disc((0, 0, .42), .19, '#d3b382', sides=10)
        with s.at(.02, 0, .4, pitch=.5):
            s.box((0, 0, .08), (.03, .07, .17), '#5a5f63')
            s.box((0, 0, .15), (.034, .045, .05), '#3a3d40')
        with s.at(.09, 0, .53, pitch=.5 - math.pi / 2):
            s.cyl((0, 0, -.06), (0, 0, .62), .016, s.c(TIMBER, .04), sides=6)
        for x, y, yaw in ((.42, -.3, .4), (.36, .3, 1.9), (-.2, -.46, 2.7)):
            with s.at(x, y, .05, yaw=yaw):
                s.cyl((-.17, 0, 0), (.17, 0, 0), .055, s.pick(bark, .05), sides=5, cap0=False, cap1=False)
                for end in (-.171, .171):
                    with s.at(end, 0, 0, pitch=math.pi / 2):
                        s.disc((0, 0, 0), .054, s.pick(cut, .04), sides=5)


def snow_shovel(s):
    snow = ['#eaf1f8', '#d6e3ef', '#c6d7e8', '#dfe9f3']
    s.dome((0, 0, 0), (.8, .58, .44), lambda j, i: s.pick(snow, .015), nu=12, nv=4, noise=.1)
    s.dome((.55, .3, 0), (.5, .42, .24), lambda j, i: s.pick(snow, .015), nu=10, nv=3, noise=.1)
    with s.at(-.42, -.2, .44, yaw=.35, pitch=-.14, roll=.2):
        s.box((0, 0, -.16), (.44, .025, .36), RED)
        for dx in (-.15, 0, .15):
            s.box((dx, -.016, -.16), (.02, .012, .34), '#a82a23')
        s.box((0, 0, .03), (.46, .04, .03), '#a82a23')
        s.cyl((0, 0, .02), (0, 0, 1.0), .016, s.c(TIMBER, .04), sides=6)
        s.torus((0, 0, 1.06), .058, .013, RED, nu=10, nv=4, axis='y')
        s.cyl((0, 0, .98), (0, 0, 1.01), .022, RED, sides=6)
    with s.at(.82, -.4, 0):
        s.cyl((0, 0, 0), (0, 0, .27), .115, '#eceae0', r1=.14, sides=12)
        s.cyl((0, 0, .27), (0, 0, .295), .147, BLUE, sides=12)
        s.box((0, -.128, .15), (.12, .006, .1), BLUE)


def lawn_mower(s):
    red, black, grey = '#c2332b', '#1d1f22', '#8f979b'
    s.prism(rounded_rect(.52, .62, .1, 3), .06, .2, red)
    s.box((0, -.02, .29), (.26, .28, .18), black)
    s.cyl((0, -.02, .38), (0, -.02, .43), .11, grey, sides=12)
    s.cyl((.07, .08, .38), (.07, .08, .42), .03, black, sides=8)
    s.box((0, .04, .215), (.4, .3, .03), '#a82a23')
    for sx in (-1, 1):
        wheel(s, (sx * .29, -.22, .09), .09, .04, tyre=black, hub=grey, sides=10)
        wheel(s, (sx * .29, .24, .1), .1, .04, tyre=black, hub=grey, sides=10)
        s.tube([(sx * .23, .28, .2), (sx * .23, .82, .86), (sx * .23, 1.0, .98)], .012, grey, sides=5)
    s.cyl((-.23, 1.0, .98), (.23, 1.0, .98), .014, black, sides=6)
    s.cyl((-.23, .93, .935), (.23, .93, .935), .006, RED, sides=4)
    wedge_body(s, .4, [(.3, .14), (.74, .2), (.74, .42), (.3, .46)], '#3a3d40')
    s.box((0, .3, .47), (.36, .03, .03), grey)


def propane_cage(s):
    white, bar, w, d, h, base = '#cfd5d9', '#9aa3a8', 1.5, .72, 1.74, .12
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * (w / 2 - .04), sy * (d / 2 - .04), base / 2), (.06, .06, base), '#8f979b')
        s.box((sx * (w / 2 - .01), 0, base + h / 2), (.02, d, h), white)
        s.box((sx * (w / 2 - .02), -d / 2 + .02, base + h / 2), (.04, .04, h), bar)
    s.box((0, d / 2 - .01, base + h / 2), (w, .02, h), white)
    for k in range(4):
        s.box((0, 0, base + k * h / 3), (w, d, .03), bar)
    s.box((0, -d / 2 + .02, base + h / 2), (.05, .04, h), bar)
    for row in range(3):
        z = base + row * h / 3 + .015
        for col in range(4):
            x = -w / 2 + .2 + col * (w - .4) / 3
            s.cyl((x, .04, z), (x, .04, z + .3), .15, '#f1f2f3', sides=10, cap1=False)
            s.dome((x, .04, z + .3), (.15, .15, .07), '#f1f2f3', nu=10, nv=2)
            s.cyl((x, .04, z + .36), (x, .04, z + .44), .09, '#d9dde0', sides=8, cap0=False, cap1=False)
    for sx in (-1, 1):
        x0, x1 = (.025, w / 2 - .04) if sx > 0 else (-w / 2 + .04, -.025)
        s.net_quad((x0, -d / 2 + .005, base + .02), (x1, -d / 2 + .005, base + .02), (x1, -d / 2 + .005, base + h - .02), (x0, -d / 2 + .005, base + h - .02), 7, 14, .008, bar)
        s.box((sx * .09, -d / 2 - .01, base + h * .5), (.04, .02, .12), '#3a3d40')
    s.box((0, -d / 2 + .01, base + h + .11), (w, .02, .22), '#2f5fa8')
    s.box((0, -d / 2 - .002, base + h + .11), (w - .3, .006, .08), WHITE)


# ---------------------------------------------------------------------------
# Wildlife: static low-poly animals, lofted along a spine in the XZ plane
# ---------------------------------------------------------------------------
def spine_loft(s, stations, tone, n=8, cap_start=True, cap_end=True):
    """stations are (x, z, half_width, half_height). Ring index 0 is the +y flank,
    n/4 the back, n/2 the -y flank and 3n/4 the belly."""
    rings = []
    for i, (x, z, hw, hh) in enumerate(stations):
        a, b = stations[max(0, i - 1)], stations[min(len(stations) - 1, i + 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        size = math.hypot(tx, tz) or 1.0
        tx, tz = tx / size, tz / size
        rings.append([(x - tz * math.sin(k * math.tau / n) * hh, math.cos(k * math.tau / n) * hw, z + tx * math.sin(k * math.tau / n) * hh) for k in range(n)])
    s.loft(rings, tone, cap_start, cap_end)


def limb(s, points, radii, colour, sides=6):
    for (a, b), (r0, r1) in zip(zip(points, points[1:]), zip(radii, radii[1:])):
        s.cyl(a, b, r0, colour, r1=r1, sides=sides)


def mule_deer(s):
    coat, belly, rump, dark, pale, leg = '#8a7460', '#b5a48c', '#ece7db', '#2f2925', '#cdbfa9', '#7b6654'
    with s.at(yaw=-math.pi / 2, scale=.87):
        body = [(-.76, 1.0, .03, .04), (-.71, 1.0, .13, .16), (-.52, .97, .19, .22), (-.2, .93, .2, .23), (.12, .93, .19, .23),
                (.38, .97, .17, .22), (.52, 1.03, .12, .17), (.6, 1.07, .05, .08)]

        def body_tone(r, i):
            if r == 0 or (r == 1 and i not in (1, 2)):
                return rump
            return belly if i in (5, 6) else coat

        spine_loft(s, body, body_tone, n=8)
        neck = [(.44, 1.03, .11, .16), (.57, 1.2, .085, .115), (.67, 1.36, .07, .09), (.73, 1.5, .062, .078)]
        spine_loft(s, neck, lambda r, i: pale if i in (5, 6) else coat, n=8, cap_start=False)
        head = [(.67, 1.57, .03, .04), (.73, 1.58, .075, .085), (.82, 1.56, .066, .07), (.92, 1.52, .042, .046), (.99, 1.495, .03, .032)]
        spine_loft(s, head, lambda r, i: pale if r >= 2 and i not in (1, 2) else (dark if r == 1 and i in (1, 2) else coat), n=8)
        s.dome((1.0, 0, 1.495), (.022, .028, .022), dark, nu=6, nv=3, full=True)
        for sy in (-1, 1):
            s.dome((.8, sy * .064, 1.59), (.016, .01, .016), dark, nu=6, nv=3, full=True)
            # big mule ears, set wide and tilted out
            with s.at(.69, sy * .07, 1.63, pitch=-.25, roll=-sy * .75):
                s.dome((0, 0, .12), (.03, .06, .125), coat, nu=8, nv=4, full=True)
                s.dome((.02, 0, .12), (.014, .042, .095), pale, nu=6, nv=3, full=True)
            for hip, knee, fetlock in (((.42, .1, .84), (.44, .09, .46), (.42, .09, .1)), ((-.56, .11, .88), (-.68, .1, .5), (-.6, .1, .1))):
                points = [(hip[0], sy * hip[1], hip[2]), (knee[0], sy * knee[1], knee[2]), (fetlock[0], sy * fetlock[1], fetlock[2])]
                limb(s, points, [.085, .045, .03], leg)
                s.cyl((fetlock[0], sy * fetlock[1], .1), (fetlock[0] + .02, sy * fetlock[1], 0), .03, dark, r1=.036, sides=6)
            # haunch and shoulder masses blend the legs into the body
            s.dome((-.52, sy * .12, .93), (.19, .09, .2), coat, nu=8, nv=4, full=True)
            s.dome((.38, sy * .11, .95), (.14, .08, .19), coat, nu=8, nv=4, full=True)
        limb(s, [(-.75, 0, 1.03), (-.8, 0, .9), (-.81, 0, .8)], [.03, .024, .012], rump, sides=6)
        s.dome((-.81, 0, .79), (.02, .02, .03), dark, nu=6, nv=3, full=True)


def jackrabbit(s):
    coat, belly, white, dark = '#8f8474', '#cfc8b8', '#efece4', '#2a2623'
    with s.at(yaw=-math.pi / 2, scale=.95):
        body = [(-.2, .1, .02, .02), (-.17, .13, .085, .1), (-.07, .17, .11, .14), (.04, .2, .1, .125), (.13, .25, .075, .095), (.19, .31, .055, .065), (.22, .36, .04, .045)]
        spine_loft(s, body, lambda r, i: belly if i in (5, 6) else coat)
        head = [(.19, .4, .02, .025), (.235, .41, .052, .055), (.3, .4, .046, .048), (.35, .385, .03, .03), (.378, .378, .014, .015)]
        spine_loft(s, head, lambda r, i: belly if r >= 2 and i in (5, 6) else coat)
        s.dome((.38, 0, .378), (.012, .016, .011), dark, nu=6, nv=3, full=True)
        for sy in (-1, 1):
            s.dome((.29, sy * .045, .423), (.012, .008, .012), dark, nu=6, nv=3, full=True)
            with s.at(.225, sy * .03, .445, pitch=-.3, roll=-sy * .16):
                s.dome((0, 0, .075), (.015, .027, .08), coat, nu=6, nv=4, full=True)
                s.dome((.008, 0, .075), (.007, .018, .062), '#c9a99a', nu=6, nv=3, full=True)
                s.dome((0, 0, .143), (.011, .019, .018), dark, nu=6, nv=3, full=True)
            s.dome((-.08, sy * .088, .11), (.105, .046, .1), coat, nu=8, nv=4, full=True)
            s.box((-.01, sy * .092, .018), (.18, .042, .036), coat)
            limb(s, [(.13, sy * .042, .2), (.15, sy * .042, .0)], [.022, .015], coat)
        s.dome((-.21, 0, .12), (.036, .042, .042), white, nu=7, nv=4, full=True)


def magpie(s):
    black, white, blue, teal = '#1c1d21', '#f1f1ec', '#22478a', '#1d6b63'
    body = [(-.1, .13, .012, .014), (-.08, .135, .035, .035), (-.02, .14, .05, .052), (.05, .15, .048, .05), (.1, .165, .036, .04), (.128, .18, .022, .024)]
    spine_loft(s, body, lambda r, i: white if r in (1, 2) and i in (4, 5, 6, 7) else black)
    s.dome((.14, 0, .2), (.034, .029, .03), black, nu=8, nv=4, full=True)
    s.cyl((.165, 0, .2), (.215, 0, .193), .012, black, r1=.002, sides=6)
    for sy in (-1, 1):
        s.dome((.035, sy * .046, .162), (.04, .01, .02), white, nu=6, nv=3, full=True)
        s.dome((-.03, sy * .047, .148), (.07, .01, .028), blue, nu=6, nv=3, full=True)
        limb(s, [(.02, sy * .02, .1), (.03, sy * .024, .0)], [.006, .005], black, sides=4)
        for toe in (-.5, 0, .5):
            s.ribbon((.03, sy * .024, .003), (.03 + math.cos(toe) * .035, sy * .024 + math.sin(toe) * .035, .003), .006, black)
        s.ribbon((.03, sy * .024, .003), (0, sy * .024, .003), .006, black)
    # long graduated tail: a shallow ridge from rump to tip
    root, middle, tip = (-.09, .14), (-.25, .17), (-.37, .185)
    for sy in (-1, 1):
        s.quad((root[0], 0, root[1] + .008), (root[0], sy * .022, root[1]), (middle[0], sy * .03, middle[1]), (middle[0], 0, middle[1] + .008), teal)
        s.quad((middle[0], 0, middle[1] + .008), (middle[0], sy * .03, middle[1]), (tip[0], sy * .006, tip[1]), (tip[0], 0, tip[1] + .004), '#16302f')


def magpies(s):
    with s.at(-.22, -.05, 0, yaw=-math.pi / 2 + .35):
        magpie(s)
    with s.at(.3, .18, 0, yaw=math.pi * .6):
        magpie(s)


def goose(s, grazing=False):
    brown, flank, black, white, foot = '#77685a', '#b3a795', '#1d1d1f', '#f1f0ea', '#2c2a28'
    body = [(-.43, .37, .012, .014), (-.39, .36, .07, .06), (-.25, .36, .14, .13), (-.05, .35, .17, .16), (.14, .37, .15, .15), (.26, .41, .1, .11), (.32, .45, .055, .065)]

    def body_tone(r, i):
        if r == 0:
            return black if i in (0, 1, 2, 3) else white
        if r == 1:
            return brown if i in (1, 2) else white
        return brown if i in (0, 1, 2, 3) else flank

    spine_loft(s, body, body_tone)
    if grazing:
        neck = [(.27, .46, .05, .055), (.4, .5, .04, .042), (.5, .42, .034, .036), (.56, .27, .03, .032)]
        head, bill = (.575, .17), ((.58, .13), (.585, .06))
    else:
        neck = [(.27, .46, .05, .055), (.33, .62, .038, .042), (.34, .76, .032, .034), (.36, .87, .03, .032)]
        head, bill = (.4, .9), ((.445, .895), (.52, .885))
    spine_loft(s, neck, black, n=6, cap_start=False)
    s.dome((head[0], 0, head[1]), (.055, .036, .04) if not grazing else (.04, .036, .055), black, nu=8, nv=4, full=True)
    for sy in (-1, 1):
        s.dome((head[0] - .008, sy * .031, head[1] - .014), (.028, .012, .026), white, nu=6, nv=3, full=True)
        limb(s, [(0, sy * .07, .23), (.012, sy * .07, .0)], [.016, .012], foot)
        s.tri((.012, sy * .07, .004), (.1, sy * .11, .004), (.1, sy * .03, .004), foot)
    s.cyl((bill[0][0], 0, bill[0][1]), (bill[1][0], 0, bill[1][1]), .019, black, r1=.008, sides=6)


def canada_geese(s):
    with s.at(-.35, .1, 0, yaw=-math.pi / 2 - .3):
        goose(s)
    with s.at(.5, -.25, 0, yaw=math.pi + .5):
        goose(s, grazing=True)


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
def spec(slug, label, category, description, builder, seed, color='#8b8f8a'):
    return dict(slug=slug, label=label, category=category, description=description, builder=builder, seed=seed, color=color, kind='object')


WINTER = 'Winter city'
WILDLIFE = 'Wildlife'
SPECS = [
    spec('outdoor-rink', 'Community outdoor rink', WINTER, 'Boarded 30 x 15 m neighbourhood ice rink with lines, two nets, a gate and players\' benches.', outdoor_rink, 2101, '#d9e7f1'),
    spec('rink-board-section', 'Rink board section', WINTER, 'Repeatable 4 m length of braced rink boards for building a custom ice surface.', rink_board_section, 2102, '#eef0f1'),
    spec('hockey-net', 'Hockey net', WINTER, 'Regulation red steel hockey net with white mesh for rinks and ponds.', regulation_hockey_net, 2103, '#c23b33'),
    spec('warming-hut', 'Skaters\' warming hut', WINTER, 'Small cedar skate-change hut with a stove pipe, bench and firewood beside the rink.', warming_hut, 2104, '#9a6b45'),
    spec('fire-pit-circle', 'Fire pit circle', WINTER, 'Steel fire ring on a gravel pad with four log benches and stacked firewood.', fire_pit_circle, 2105, '#8a6a4a'),
    spec('snow-fence', 'Snow fence', WINTER, 'Repeatable 4.8 m run of wood-slat snow fence on steel posts to hold drifts off paths.', snow_fence, 2106, '#b85a34'),
    spec('snow-windrow', 'Snow windrow', WINTER, 'Ploughed 6 m snow bank with broken chunks; repeat along winter streets and lots.', snow_windrow, 2107, '#f4f7fa'),
    spec('grit-box', 'Sanding grit box', WINTER, 'Roadside box of traction grit for icy hills, steps and pathway slopes.', grit_box, 2108, '#e0b63a'),
    spec('plug-in-posts', 'Parking plug-in posts', WINTER, 'Block-heater outlet posts with rail and wheel stops for two winter parking stalls.', plug_in_posts, 2109, '#9aa3a7'),
    # --- lanes and yards ---
    spec('waste-cart-black', 'Black garbage cart', 'Street furniture', 'Wheeled black cart for back lanes, side yards and collection day.', waste_cart_black, 2201, '#272b2f'),
    spec('waste-cart-blue', 'Blue recycling cart', 'Street furniture', 'Wheeled blue recycling cart for back lanes and collection day.', waste_cart_blue, 2202, '#1f5fa8'),
    spec('waste-cart-green', 'Green compost cart', 'Street furniture', 'Wheeled green food and yard waste cart for back lanes and collection day.', waste_cart_green, 2203, '#3f7d3a'),
    spec('waste-cart-trio', 'Three-cart set', 'Street furniture', 'Black, blue and green carts lined up at the lane, as on a Calgary collection day.', waste_cart_trio, 2204, '#1f5fa8'),
    spec('utility-pole', 'Wooden utility pole', 'Street furniture', 'Back-lane power pole with crossarm, transformer and lane light. Use alone or to end a line.', utility_pole_plain, 2205, '#6e5a48'),
    spec('utility-pole-lines', 'Utility pole with lines', 'Street furniture', 'Power pole carrying overhead lines 15 m each way. Place one every 30 m along a lane.', utility_pole_lines, 2206, '#6e5a48'),
    spec('privacy-fence', 'Wood privacy fence', 'Edges & gates', 'Repeatable 2.4 m panel of 1.8 m cedar board fence for yards and lanes.', privacy_fence, 2207, '#9a6b45'),
    spec('chain-link-fence', 'Chain-link fence', 'Edges & gates', 'Repeatable 3 m panel of 1.2 m galvanized chain-link for yards, schools and parks.', chain_link_fence, 2208, '#9aa3a7'),
    spec('garden-shed', 'Garden shed', 'Garden & growing', 'Backyard 3 x 2.4 m gable shed with double doors, window and a small ramp.', garden_shed, 2209, '#7d8f96'),
    spec('trampoline', 'Backyard trampoline', 'Play', 'Round 4.3 m trampoline with safety net enclosure; a familiar backyard sight.', trampoline, 2210, '#2f66b5'),
    spec('little-free-library', 'Little free library', 'Street furniture', 'Neighbourhood book-exchange box on a post for front yards and park entries.', little_free_library, 2211, '#2f8f8a'),
    spec('street-hockey-net', 'Driveway hockey net', 'Play', 'Street hockey net with two sticks and a ball for driveways, lanes and cul-de-sacs.', street_hockey_net, 2212, '#eef0f1'),
    # --- foothills landscape and ranch heritage ---
    spec('sandstone-blocks', 'Sandstone block group', 'Landscape', 'Quarried buff sandstone blocks, the stone of Calgary\'s early buildings, as informal seating.', sandstone_blocks, 2301, '#c9ad84'),
    spec('sandstone-seat-wall', 'Sandstone seat wall', 'Seating', 'Repeatable 3.6 m seat wall of rough sandstone blocks with thick cap stones.', sandstone_seat_wall, 2302, '#c9ad84'),
    spec('rundle-rock-wall', 'Rundle rock wall', 'Edges & gates', 'Repeatable 3 m wall of dark ledge-laid Rundle stone from the Bow valley.', rundle_rock_wall, 2303, '#4a4a4c'),
    spec('glacial-erratic', 'Glacial erratic', 'Landscape', 'House-sized quartzite boulder left by the ice, like those of the foothills erratics train.', glacial_erratic, 2304, '#b7b0a6'),
    spec('round-hay-bale', 'Round hay bale', 'Landscape', 'Large round straw bale for field edges, event seating and harvest scenes.', round_hay_bale, 2305, '#c9a857'),
    spec('ranch-rail-fence', 'Ranch rail fence', 'Edges & gates', 'Repeatable 4.8 m run of weathered three-rail post fence.', ranch_rail_fence, 2306, '#8a7d6c'),
    spec('ranch-gate', 'Ranch entry gate', 'Edges & gates', 'Tall log gateway with a blank hanging sign and a pair of steel farm gates.', ranch_gate, 2307, '#8a7d6c'),
    # --- pathway and transit ---
    spec('pathway-marker', 'River pathway marker', 'Street furniture', 'Shared pathway post with walking and cycling symbols and a coloured route band.', pathway_marker, 2401, '#1f8a8a'),
    spec('river-safety-station', 'River safety ring station', 'Street furniture', 'Life ring and throw rope on a marked post for river banks, ponds and boat launches.', river_safety_station, 2402, '#c23b33'),
    spec('lrt-platform-shelter', 'Light-rail platform shelter', 'Shelters & markets', 'Ten metre station canopy with wind screens, benches, blank pylon and platform edge strip.', lrt_platform_shelter, 2403, '#3d4348'),
    spec('lrt-catenary-pole', 'Light-rail catenary pole', 'Street furniture', 'Overhead line pole with cantilever and wires 20 m each way. Place one every 40 m.', lrt_catenary_pole, 2404, '#8e969a'),
    spec('heated-bus-shelter', 'Heated bus shelter', 'Shelters & markets', 'Enclosed glazed shelter with radiant heaters, bench, blank ad panel and stop flag.', heated_bus_shelter, 2405, '#454c52'),
    spec('scooter-corral', 'E-scooter parking corral', 'Street furniture', 'Marked on-street bay with a rail, sign and four shared scooters.', scooter_corral, 2406, '#17a2a2'),
    # --- wildlife ---
    spec('white-tailed-jackrabbit', 'White-tailed jackrabbit', WILDLIFE, 'Lepus townsendii · Calgary\'s big prairie hare sitting alert on a lawn. Static model.', jackrabbit, 2501, '#8f8474'),
    spec('magpies', 'Black-billed magpies', WILDLIFE, 'Pica hudsonia · a pair of long-tailed black, white and blue magpies on the ground. Static model.', magpies, 2502, '#22478a'),
    spec('canada-geese', 'Canada geese', WILDLIFE, 'Branta canadensis · a pair of geese, one alert and one grazing, for river banks and ponds. Static model.', canada_geese, 2503, '#77685a'),
    spec('mule-deer', 'Mule deer', WILDLIFE, 'Odocoileus hemionus · a doe standing alert with big ears and white rump. Static model.', mule_deer, 2504, '#8a7460'),
    # --- everyday streets, lanes and yards ---
    spec('dumpster', 'Lane dumpster', 'Street furniture', 'Green front-load bin with black lids for the lane behind shops and apartments.', dumpster, 2601, '#2f5d3a'),
    spec('deep-collection-bins', 'Deep-collection bins', 'Street furniture', 'Pair of slat-clad semi-underground garbage and recycling bins for parks and townhouse sites.', deep_collection_bins, 2602, '#8a7d6c'),
    spec('wildlife-proof-bin', 'Wildlife-proof park bin', 'Street furniture', 'Brown steel twin bin with latched chutes, as used along river parks and foothills trails.', wildlife_proof_bin, 2603, '#5b4636'),
    spec('yard-waste-bags', 'Yard waste paper bags', 'Street furniture', 'Three tall kraft bags of leaves set out at the curb in autumn.', yard_waste_bags, 2604, '#b08a5a'),
    spec('donation-box', 'Donation drop box', 'Street furniture', 'Steel clothing donation bin with a pull-down chute for plaza and community hall lots.', donation_box, 2605, '#1f7a8c'),
    spec('padmount-transformer', 'Green utility box', 'Street furniture', 'Pad-mounted power transformer, the green box found on boulevards and front lawns.', padmount_transformer, 2606, '#3c6b4a'),
    spec('signal-cabinet', 'Signal control cabinet', 'Street furniture', 'Grey controller cabinet that stands at the corner of a signalled intersection.', signal_cabinet, 2607, '#aeb5b9'),
    spec('street-letter-box', 'Street letter box', 'Street furniture', 'Red barrel-topped post box for mailing letters on a neighbourhood main street.', street_letter_box, 2608, '#c2332b'),
    spec('newspaper-boxes', 'Newspaper boxes', 'Street furniture', 'Row of three coin-box newspaper stands for a transit stop or main street corner.', newspaper_boxes, 2609, '#2f5fa8'),
    spec('parking-pay-station', 'Parking pay station', 'Street furniture', 'Solar pay machine with a screen and keypad for on-street and lot parking.', parking_pay_station, 2610, '#2f5fa8'),
    spec('bus-bench', 'Bus stop bench', 'Seating', 'Slatted bench on concrete ends with a blank poster back, for an unsheltered stop.', bus_bench, 2611, '#8a6a4a'),
    spec('sandwich-board', 'Sandwich board sign', 'Street furniture', 'Folding chalkboard sign for a cafe door or market stall. No wording.', sandwich_board, 2612, '#8a6a4a'),
    spec('shopping-cart', 'Shopping cart', 'Street furniture', 'Wire grocery cart, for a store entrance or left behind at a bus stop.', shopping_cart, 2613, '#b9c0c4'),
    spec('portable-toilet', 'Portable toilet', 'Street furniture', 'Blue job-site and festival toilet cabin with vent stack.', portable_toilet, 2614, '#2a66a8'),
    spec('patio-heater', 'Patio heater', 'Street furniture', 'Propane mushroom heater that stretches patio season into the shoulder months.', patio_heater, 2615, '#b4bbbf'),
    spec('park-grill', 'Park charcoal grill', 'Street furniture', 'Pedestal barbecue with an adjustable grate on a concrete pad at a picnic site.', park_grill, 2616, '#1f2124'),
    spec('backyard-barbecue', 'Backyard barbecue', 'Garden & growing', 'Gas grill on a cart with side shelves and a propane tank, for decks and patios.', barbecue, 2617, '#1f2124'),
    spec('adirondack-chairs', 'Adirondack chairs', 'Seating', 'Pair of slatted lawn chairs with a small table between them.', adirondack_chairs, 2618, '#b23a34'),
    spec('rotary-clothesline', 'Rotary clothesline', 'Garden & growing', 'Umbrella clothesline with laundry out to dry in a prairie backyard.', rotary_clothesline, 2619, '#9aa3a7'),
    spec('wheelbarrow', 'Wheelbarrow', 'Garden & growing', 'Garden wheelbarrow loaded with soil and a spade.', wheelbarrow, 2620, '#3f7d3a'),
    spec('barrel-planter', 'Half-barrel planter', 'Garden & growing', 'Oak half barrel planted with red geraniums and trailing greens.', barrel_planter, 2621, '#7a5a3c'),
    spec('parked-bicycle', 'Parked bicycle', 'Vehicles', 'Adult bicycle leaning on its kickstand.', parked_bicycle, 2622, '#1f7a8c'),
    spec('kids-bikes', 'Kids\' bikes on the lawn', 'Play', 'Two small bikes dropped on the grass with a helmet beside them.', kids_bikes, 2623, '#c2332b'),
    spec('portable-hoop', 'Driveway basketball hoop', 'Play', 'Portable hoop on a weighted wheeled base, set at regulation rim height.', portable_hoop, 2624, '#e2742b'),
    spec('sandbox', 'Backyard sandbox', 'Play', 'Timber sandbox with corner seats, a pail, a spade, a toy truck and a ball.', sandbox, 2625, '#d9c79a'),
    spec('camping-trailer', 'Camping trailer', 'Vehicles', 'Small travel trailer parked on its jack with twin propane tanks, as seen beside many garages.', camping_trailer, 2626, '#eceef0'),
    spec('disc-golf-basket', 'Disc golf basket', 'Sport & exercise', 'Chain basket target for a park disc golf course.', disc_golf_basket, 2627, '#e0b63a'),
    spec('traffic-barrel', 'Construction barrel', 'Traffic & safety', 'Orange and white striped drum for road and infill construction zones.', traffic_barrel, 2628, '#e2742b'),
    spec('construction-fence', 'Construction fence panel', 'Traffic & safety', 'Repeatable 2.9 m temporary mesh panel on block feet around a building site.', construction_fence, 2629, '#9aa3a7'),
    spec('snowman', 'Snowman', WINTER, 'Front-yard snowman with a carrot nose, stick arms, scarf and toque.', snowman, 2630, '#f4f7fa'),
    spec('toboggan-and-sled', 'Toboggan and saucer', WINTER, 'Wooden toboggan and a red saucer sled left at the bottom of the hill.', toboggan_and_sled, 2631, '#b8894f'),
    spec('bike-with-trailer', 'Bicycle with child trailer', 'Vehicles', 'Parked bicycle towing a two-wheel child trailer with a safety flag.', bike_with_trailer, 2632, '#e7b93a'),
    spec('bird-feeder', 'Bird feeder with chickadees', 'Garden & growing', 'Pole-mounted seed feeders with two black-capped chickadees, year-round Calgary residents. Static model.', bird_feeder, 2633, '#3f5d4a'),
    spec('telecom-pedestals', 'Telecom pedestals', 'Street furniture', 'Pair of small phone and cable boxes, one square and one round, found along lot lines.', telecom_pedestals, 2634, '#8f9a8c'),
    spec('firewood-stack', 'Firewood stack', 'Garden & growing', 'Split logs racked between posts, with a chopping block and axe.', firewood_stack, 2635, '#7a6652'),
    spec('snow-shovel', 'Snow shovel in a snowbank', WINTER, 'Shovel stuck in a shovelled pile beside a pail of ice melt.', snow_shovel, 2636, '#c2332b'),
    spec('lawn-mower', 'Lawn mower', 'Garden & growing', 'Gas push mower with a rear grass bag.', lawn_mower, 2637, '#c2332b'),
    spec('propane-cage', 'Propane exchange cage', 'Street furniture', 'Locked mesh cabinet of white barbecue tanks, as found outside gas stations and hardware stores.', propane_cage, 2638, '#e6e8ea'),
]


# ---------------------------------------------------------------------------
# Export and registry
# ---------------------------------------------------------------------------
def build(item):
    solid = Solid(item['seed'])
    item['builder'](solid)
    return solid


def row(item, payload, lo, hi, triangles, meshes):
    size = hi - lo
    return {
        'id': PREFIX + item['slug'],
        'label': item['label'],
        'category': item['category'],
        'description': item['description'],
        'dimensions': [round(float(size[0]), 3), round(float(size[2]), 3), round(float(size[1]), 3)],
        'url': f'{URL_ROOT}/{item["slug"]}.glb',
        'color': item['color'],
        'kind': item['kind'],
        'offset': [0.0, round(-float(lo[1]), 6) + 0.0, 0.0],
        'sourceKit': KIT,
        'sourceBuilder': f'calgary:{item["builder"].__name__}',
        'sha256': hashlib.sha256(payload).hexdigest(),
        'triangles': triangles,
        'meshes': meshes,
        'bytes': len(payload),
    }


def compile_item(item):
    solid = build(item)
    payload, lo, hi, triangles, meshes = foliage.write_glb([solid.body, solid.gloss], item['slug'], GENERATOR)
    if triangles > 14000 or meshes > 2:
        raise ValueError(f'{item["slug"]} exceeds its budget: {triangles} triangles, {meshes} meshes')
    return row(item, payload, lo, hi, triangles, meshes), payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--id', action='append')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--register', action='store_true', help='Splice finished rows into the frontend extras catalogue and backend allowlist.')
    parser.add_argument('--attach-thumbnails', action='store_true', help='Record the reviewed <slug>.webp card images found beside the GLBs.')
    args = parser.parse_args(argv)
    chosen = [s for s in SPECS if not args.id or s['slug'] in args.id]
    unknown = set(args.id or []) - {s['slug'] for s in SPECS}
    if unknown:
        raise SystemExit(f'Unknown item: {sorted(unknown)}')
    if args.dry_run:
        print(json.dumps({'count': len(chosen), 'kit': KIT, 'items': [s['slug'] for s in chosen], 'paid_calls': 0, 'blender': False}))
        return
    if not args.output:
        parser.error('--output is required unless --dry-run')
    if args.attach_thumbnails:
        rows = json.loads((args.output / 'catalogue.json').read_text(encoding='utf-8'))
        attached = foliage.attach_thumbnails(rows, args.output)
        (args.output / 'catalogue.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'thumbnails': attached, 'rows': len(rows)}))
        return
    if args.register:
        rows = json.loads((args.output / 'catalogue.json').read_text(encoding='utf-8'))
        foliage.register(rows)
        print(json.dumps({'registered': len(rows)}))
        return
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for item in chosen:
        record, payload = compile_item(item)
        (args.output / f'{item["slug"]}.glb').write_bytes(payload)
        rows.append(record)
    (args.output / 'catalogue.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'count': len(rows), 'triangles': sum(r['triangles'] for r in rows), 'bytes': sum(r['bytes'] for r in rows), 'paid_calls': 0}))


if __name__ == '__main__':
    main(sys.argv[1:])
