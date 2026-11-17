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
# Transit and service vehicles. Long axis along y with the front at -y, like the
# existing vehicle details; the curb side for right-hand traffic is therefore -x.
# Liveries are generic and carry no agency colours, numbers or wording.
# ---------------------------------------------------------------------------
def shell(s, stations, width, height, floor, colour, radius=.25, steps=3):
    """Vehicle or cabin body: a rounded cross-section lofted along y. stations are
    (y, width scale, height scale). The floor line stays level and the roof follows."""
    section = rounded_rect(width, height, radius, steps)
    s.loft([[(x * ws, y, floor + (z + height / 2) * hs) for x, z in section] for y, ws, hs in stations], colour)


def glazing(s, width, y0, y1, z0, z1, pillars=(), frame='#1b1d1f', sides=(-1, 1), proud=.006):
    """Dark window band on the flat part of a body side, split by pillars."""
    for sx in sides:
        x = sx * (width / 2 + proud)
        s.box((x, (y0 + y1) / 2, (z0 + z1) / 2), (.012, y1 - y0, z1 - z0), GLASS_DARK, gloss=True)
        for y in pillars:
            s.box((x + sx * .004, y, (z0 + z1) / 2), (.012, .06, z1 - z0), frame)


def road_wheels(s, y, track, radius, width, arch=None, body_width=None, hub='#8f979b'):
    """One axle. With arch set, a dark wheel-well panel sits behind each tyre face."""
    for sx in (-1, 1):
        wheel(s, (sx * track / 2, y, radius), radius, width, sides=16, hub=hub)
        if arch:
            s.box((sx * (body_width / 2 + .004), y, arch / 2 + .16), (.012, radius * 2 + .3, arch), '#141618')


def beam_yz(s, a, b, width, depth, colour, gloss=False):
    """Box beam from a to b, which share an x. depth is measured in the yz-plane."""
    dy, dz = b[1] - a[1], b[2] - a[2]
    length = math.hypot(dy, dz)
    with s.at(a[0], a[1], a[2], roll=math.atan2(-dy, dz)):
        s.box((0, 0, length / 2), (width, depth, length), colour, gloss=gloss)


def city_bus(s):
    length, width, floor, height = 12.2, 2.55, .32, 2.72
    white, skirt, dark = '#eef0f1', '#1f4f85', '#1b1d1f'
    front, rear, roof = -length / 2, length / 2, floor + height
    shell(s, [(front, .93, .97), (front + .35, 1, 1), (rear - .25, 1, 1), (rear, .96, .98)], width, height, floor, white, radius=.22)
    for sx in (-1, 1):
        x = sx * (width / 2 + .002)
        s.box((x, 0, floor + .4), (.012, length - .8, .6), skirt)
        s.box((x, 0, floor + .74), (.012, length - .8, .05), ORANGE)
    glazing(s, width, front + .95, rear - .6, 1.42, 2.42, pillars=[front + .95 + k * 1.52 for k in range(1, 7)])
    s.box((0, front - .004, 1.9), (width - .32, .012, 1.25), GLASS_DARK, gloss=True)
    s.box((0, front - .008, 2.74), (width - .5, .012, .26), dark)
    s.box((0, front - .014, 2.74), (1.5, .008, .13), '#e0a23a')
    s.box((0, rear + .004, 2.1), (1.7, .012, .7), GLASS_DARK, gloss=True)
    s.box((0, rear + .008, 1.1), (1.9, .012, .9), '#d9dde0')
    for y, w in ((front + 1.5, 1.15), (.95, 1.3)):
        x = -(width / 2 + .012)
        s.box((x, y, floor + 1.12), (.012, w, 2.08), '#2a3640', gloss=True)
        s.box((x - .006, y, floor + 1.12), (.008, .04, 2.08), dark)
        s.box((x - .006, y, floor + 2.2), (.008, w + .08, .06), dark)
    for y in (front + 2.75, rear - 3.3):
        road_wheels(s, y, width - .26, .5, .3, arch=.92, body_width=width)
    for y, sign in ((front - .06, -1), (rear + .06, 1)):
        s.box((0, y, .47), (width - .08, .14, .28), dark)
        for sx in (-1, 1):
            s.box((sx * .95, y + sign * .075, .85 if sign < 0 else 1.0), (.3, .012, .14), '#f4f1e4' if sign < 0 else RED)
    for sx in (-1, 1):
        s.cyl((sx * (width / 2 - .05), front + .12, 2.45), (sx * (width / 2 + .22), front - .05, 2.3), .02, dark, sides=5)
        s.box((sx * (width / 2 + .24), front - .06, 2.1), (.06, .16, .4), dark)
    s.box((0, 1.4, roof + .11), (1.9, 2.6, .22), '#d9dde0')
    s.box((0, -3.3, roof + .08), (1.6, 1.5, .16), '#d9dde0')
    # folded bicycle rack on the front
    s.tube([(-.95, front - .2, .62), (.95, front - .2, .62), (.95, front - .16, 1.3), (-.95, front - .16, 1.3), (-.95, front - .2, .62)], .02, dark, sides=5)
    for x in (-.5, 0, .5):
        s.cyl((x, front - .2, .62), (x, front - .16, 1.3), .012, dark, sides=4)


def light_rail_car(s):
    width, floor, height, half, gap = 2.65, .3, 3.15, 12.5, .45
    white, teal, dark, roof = '#e6ebef', '#1f7a8c', '#1b1d1f', .3 + 3.15
    for sign in (-1, 1):
        cab = [(sign * half, .78, .9), (sign * (half - .4), .9, .97), (sign * (half - 1.3), 1, 1), (sign * gap, 1, 1)]
        shell(s, cab if sign < 0 else list(reversed(cab)), width, height, floor, white, radius=.3)
        y0, y1 = sorted((sign * (gap + .5), sign * (half - 1.5)))
        glazing(s, width, y0, y1, 1.3, 2.5)
        for sx in (-1, 1):
            x = sx * (width / 2 + .002)
            s.box((x, (y0 + y1) / 2, floor + .36), (.012, y1 - y0 + .6, .58), teal)
            s.box((x, (y0 + y1) / 2, 2.72), (.012, y1 - y0 + .6, .1), teal)
            for door in (sign * 3.4, sign * 8.2):
                s.box((x + sx * .012, door, floor + 1.1), (.012, 1.36, 2.12), teal)
                s.box((x + sx * .02, door, floor + 1.28), (.012, 1.1, 1.6), '#2a3640', gloss=True)
                s.box((x + sx * .026, door, floor + 1.28), (.008, .03, 1.6), teal)
        # sloped cab front: windshield, lights and coupler
        s.box((0, sign * (half + .004), 2.05), (width * .78 - .25, .012, 1.25), GLASS_DARK, gloss=True)
        for sx in (-1, 1):
            s.box((sx * .7, sign * (half + .006), 1.0), (.3, .012, .12), '#f4f1e4')
            s.box((sx * .7, sign * (half + .006), .84), (.3, .012, .08), RED)
        s.box((0, sign * (half + .12), .5), (.3, .3, .18), dark)
        s.box((0, sign * 6.4, roof + .14), (1.9, 3.6, .28), '#cfd5d9')
        s.box((0, sign * 10.2, roof + .1), (1.6, 1.4, .2), '#cfd5d9')
    # articulation bellows
    s.box((0, 0, floor + height / 2 - .03), (width - .22, gap * 2 + .02, height - .2), '#3a3d40')
    for k in range(5):
        y = -gap + .09 + k * (gap * 2 - .18) / 4
        s.box((0, y, floor + height / 2 - .03), (width - .14, .04, height - .14), '#2b2e31')
    for y in (-8.7, 0, 8.7):
        s.box((0, y, .3), (2.25, 2.3, .34), dark)
        for dy in (-.85, .85):
            s.cyl((-.8, y + dy, .33), (.8, y + dy, .33), .33, '#2b2e31', sides=12)
    # pantograph reaching the 5.5 m contact wire
    base = roof + .3
    s.box((0, -3.6, base), (1.3, 1.7, .08), '#5e666a')
    for sx in (-1, 1):
        s.cyl((sx * .45, -4.3, base + .04), (sx * .3, -3.1, 4.55), .03, '#5e666a', sides=5)
        s.cyl((sx * .3, -3.1, 4.55), (sx * .5, -4.1, 5.44), .025, '#5e666a', sides=5)
    s.cyl((-.3, -3.1, 4.55), (.3, -3.1, 4.55), .025, '#5e666a', sides=5)
    s.box((0, -4.1, 5.47), (1.5, .28, .06), '#3a3d40')


def school_bus(s):
    yellow, black, width = '#f2b01e', '#1b1d1f', 2.44
    front, cab, rear, floor, height = -5.5, -3.7, 5.5, .8, 2.25
    shell(s, [(cab, .97, .97), (cab + .3, 1, 1), (rear - .2, 1, 1), (rear, .97, .98)], width, height, floor, yellow, radius=.28)
    s.box((0, (cab + rear) / 2 + .1, .62), (width - .1, rear - cab - .5, .4), yellow)
    shell(s, [(front, .76, .8), (front + .3, .86, .96), (cab, .9, 1)], width, 1.0, .75, yellow, radius=.2)
    s.box((0, front - .004, 1.2), (1.25, .012, .55), black)
    for y in (front - .1, rear + .1):
        s.box((0, y, .6), (width, .2, .26), black)
    s.box((0, cab - .006, 2.3), (width - .36, .012, .95), GLASS_DARK, gloss=True)
    glazing(s, width, cab + 1.15, rear - .45, 1.95, 2.62, pillars=[cab + 1.15 + k * .78 for k in range(1, 10)], frame=yellow)
    for sx in (-1, 1):
        for z in (1.02, 1.42, 1.8):
            s.box((sx * (width / 2 + .004), (cab + rear) / 2 + .3, z), (.012, rear - cab - .8, .05), black)
        s.box((sx * .8, front - .012, 1.05), (.26, .012, .16), '#f4f1e4')
        s.box((sx * .95, rear + .006, 1.3), (.2, .012, .2), RED)
        for y, tone in ((cab - .01, '#e0a23a'), (rear + .01, RED)):
            s.box((sx * .78, y, 2.92), (.2, .02, .2), tone)
        s.cyl((sx * .95, front + .3, 1.6), (sx * 1.28, front - .1, 2.15), .015, black, sides=4)
        s.dome((sx * 1.28, front - .1, 2.15), (.1, .05, .12), black, nu=8, nv=3, full=True)
    s.box((-(width / 2 + .012), cab + .55, 1.78), (.012, .78, 1.75), '#2a3640', gloss=True)
    s.box((-(width / 2 + .018), cab + .55, 1.78), (.008, .035, 1.75), black)
    s.box((0, rear + .006, 2.2), (1.5, .012, .6), GLASS_DARK, gloss=True)
    s.box((0, rear + .008, 1.45), (.75, .012, .85), '#e0a218')
    s.box((0, (cab + rear) / 2 + .2, floor + height + .012), (width - .6, rear - cab - 1.0, .03), '#f4f1e4')
    road_wheels(s, cab - .55, width - .3, .5, .3, hub=yellow)
    road_wheels(s, 3.0, width - .5, .5, .55, hub=yellow)
    for sx in (-1, 1):
        s.box((sx * (width / 2 - .12), cab - .55, 1.08), (.36, 1.3, .1), black)
        s.box((sx * (width / 2 + .004), 3.0, .86), (.012, 1.3, .5), '#141618')
    # folded stop arm on the driver side
    s.box((width / 2 + .03, cab + 1.0, 1.6), (.03, .46, .46), RED)
    s.box((width / 2 + .05, cab + 1.0, 1.6), (.008, .3, .08), WHITE)


def plow_truck(s):
    cab_c, box_c, dark, width = '#f2c230', '#6f777c', '#1b1d1f', 2.5
    s.box((0, .6, .98), (1.0, 8.2, .3), dark)
    shell(s, [(-3.9, .86, .86), (-3.6, .93, 1), (-2.4, 1, 1)], 2.3, 1.0, 1.08, cab_c, radius=.15)
    shell(s, [(-2.4, .98, .96), (-2.2, 1, 1), (-.75, 1, 1)], 2.45, 1.75, 1.15, cab_c, radius=.18)
    s.box((0, -2.406, 2.32), (2.05, .012, .85), GLASS_DARK, gloss=True)
    for sx in (-1, 1):
        s.box((sx * 1.231, -1.55, 2.3), (.012, 1.0, .75), GLASS_DARK, gloss=True)
        s.box((sx * .78, -3.906, 1.9), (.26, .012, .14), '#f4f1e4')
        s.cyl((sx * 1.2, -2.3, 2.5), (sx * 1.5, -2.5, 2.55), .02, dark, sides=4)
        s.box((sx * 1.52, -2.52, 2.4), (.05, .14, .36), dark)
        s.box((sx * 1.05, -3.0, 1.12), (.42, 1.25, .1), dark)
    s.box((0, -3.906, 1.5), (1.4, .012, .66), dark)
    s.box((0, -4.0, 1.0), (2.4, .26, .3), dark)
    s.box((0, -1.5, 2.96), (1.3, .22, .1), ORANGE)
    s.cyl((1.16, -.62, 1.2), (1.16, -.62, 3.3), .07, GALV, sides=8)
    # dump box with a load of sanding grit, cab shield and rear spreader
    wedge_body(s, width, [(-.55, 1.25), (5.0, 1.25), (5.15, 2.75), (-.55, 2.75)], box_c)
    for sx in (-1, 1):
        for y in (.4, 1.6, 2.8, 4.0):
            s.box((sx * (width / 2 + .03), y, 2.0), (.06, .09, 1.5), '#5e666a')
        s.box((sx * (width / 2 + .03), 2.25, 2.72), (.08, 5.6, .1), '#5e666a')
    s.box((0, -1.2, 2.98), (width, 1.4, .08), box_c)
    s.dome((0, 2.2, 2.74), (1.05, 2.5, .34), lambda j, i: s.pick(['#b5a58a', '#a8987c', '#c2b396'], .03), nu=10, nv=3, noise=.08)
    s.box((0, 5.32, 1.25), (1.7, .4, .55), ORANGE)
    s.cyl((0, 5.45, .55), (0, 5.45, .6), .32, dark, sides=12)
    s.cyl((0, 5.45, .6), (0, 5.4, 1.0), .05, dark, sides=5)
    for sx in (-1, 1):
        s.box((sx * .95, 5.16, 1.5), (.2, .012, .3), RED)
    road_wheels(s, -3.0, width - .32, .52, .32, hub=cab_c)
    for y in (2.9, 4.2):
        road_wheels(s, y, width - .56, .52, .56, hub=cab_c)
    # angled front plow on a push frame
    for sx in (-1, 1):
        s.cyl((sx * .5, -4.1, .95), (sx * .7, -5.0, .55), .05, dark, sides=5)
    s.cyl((0, -4.1, 1.5), (0, -5.0, 1.0), .04, GALV, sides=5)
    profile = [(0, .05), (.14, .3), (.2, .58), (.16, .85), (.04, 1.05), (-.1, 1.15)]
    with s.at(0, -5.25, 0, yaw=.4):
        half = 1.8
        for (y0, z0), (y1, z1) in zip(profile, profile[1:]):
            s.quad((-half, y0, z0), (half, y0, z0), (half, y1, z1), (-half, y1, z1), s.c(ORANGE, .05))
        s.box((0, .0, .08), (half * 2, .03, .16), '#3a3d40')
        for x in (-1.2, 0, 1.2):
            s.box((x, .28, .6), (.08, .18, .9), dark)
        s.box((0, .34, .55), (2.9, .08, .1), dark)
        for sx in (-1, 1):
            s.cyl((sx * (half - .03), 0, 1.1), (sx * (half - .03), -.04, 1.95), .012, ORANGE, sides=4)
            s.box((sx * (half - .03), -.04, 1.9), (.04, .012, .12), '#f4f1e4')


# ---------------------------------------------------------------------------
# Construction site kit, to go with the fence panel, barrel and portable toilet.
# ---------------------------------------------------------------------------
def roll_off_bin(s):
    blue, dark, length, width = '#2f6f8f', '#245a75', 6.6, 2.4
    x0, x1 = -length / 2, length / 2
    s.loft([[(x0 + .35, -width / 2, .22), (x1, -width / 2, .22), (x1, width / 2, .22), (x0 + .35, width / 2, .22)],
            [(x0, -width / 2, .75), (x1, -width / 2, .75), (x1, width / 2, .75), (x0, width / 2, .75)],
            [(x0, -width / 2, 1.85), (x1, -width / 2, 1.85), (x1, width / 2, 1.85), (x0, width / 2, 1.85)]], blue, cap_end=False)
    for sy in (-1, 1):
        for k in range(10):
            s.box((x0 + .5 + k * .62, sy * (width / 2 + .03), 1.3), (.07, .06, 1.1), dark)
        s.box((0, sy * (width / 2 + .03), 1.88), (length, .1, .1), dark)
        s.box((.15, sy * .75, .11), (length - .7, .14, .22), '#2b2e31')
        for x in (x0 + .9, x1 - .5):
            s.cyl((x, sy * .75 - .1, .13), (x, sy * .75 + .1, .13), .13, '#2b2e31', sides=10)
    for x in (x0 - .03, x1 + .03):
        s.box((x, 0, 1.88), (.1, width + .16, .1), dark)
    # hook plate on the sloped front and latch bars on the rear doors
    s.box((x0 + .1, 0, .62), (.1, .5, .5), dark)
    s.cyl((x0 - .02, -.22, .78), (x0 - .02, .22, .78), .035, GALV, sides=6)
    s.box((x1 + .03, 0, 1.3), (.04, .05, 1.1), dark)
    for sy in (-1, 1):
        s.cyl((x1 + .06, sy * .55, .35), (x1 + .06, sy * .55, 1.8), .025, GALV, sides=5)
        s.box((x1 + .06, sy * .55, 1.0), (.03, .3, .05), GALV)
    # a load of broken drywall, timber and soil showing over the rim
    s.box((0, 0, 1.6), (length - .1, width - .1, .04), '#4a4338')
    s.dome((-.6, .1, 1.6), (2.4, 1.0, .42), lambda j, i: s.pick(['#8a7d6c', '#a39683', '#6f6557', '#c9c2b4'], .04), nu=10, nv=3, noise=.14)
    for x, y, yaw, pitch, length_m in ((1.6, -.4, .3, .5, 1.9), (2.2, .5, -.6, .7, 1.5), (-2.3, -.5, 1.1, .35, 2.1), (.8, .6, 2.0, .45, 1.4)):
        with s.at(x, y, 1.62, yaw=yaw, pitch=pitch):
            s.box((length_m / 2 - .3, 0, 0), (length_m, .09, .04), s.pick(WEATHERED, .06))


def site_office_trailer(s):
    length, width, wall, base = 7.3, 3.0, 2.55, .62
    beige, trim, dark = '#d8d2c2', '#8f979b', '#2b2e31'
    for x in (-2.9, -1.0, 1.0, 2.9):
        for sy in (-1, 1):
            s.box((x, sy * 1.1, base / 2 - .04), (.4, .4, base - .08), CONCRETE)
    s.box((0, 0, base - .06), (length, width - .2, .12), dark)
    s.banded_box((0, 0, base), (length, width, wall), 8, beige, jitter=.03, top='#c9cdd0')
    s.box((0, 0, base + wall + .03), (length + .1, width + .1, .06), trim)
    for along in (-2.3, 2.3):
        framed_opening(s, 'S', length, width, along, base + 1.05, 1.1, .85, GLASS_DARK, trim=trim, gloss=True, mullion=True)
    framed_opening(s, 'N', length, width, -1.5, base + 1.05, 1.1, .85, GLASS_DARK, trim=trim, gloss=True, mullion=True)
    framed_opening(s, 'S', length, width, .2, base + .02, .9, 2.03, '#aeb5b9', trim=trim)
    wall_panel(s, 'S', length, width, .2, base + 1.3, .5, .5, GLASS_DARK, proud=.03, gloss=True)
    wall_panel(s, 'S', length, width, .52, base + .95, .05, .16, dark, proud=.05)
    wall_panel(s, 'S', length, width, 1.35, base + 1.5, .8, .5, WHITE, proud=.03)
    # landing, steps and rail
    y = -width / 2
    s.box((.2, y - .6, base - .05), (1.5, 1.2, .1), s.c(TIMBER, .05))
    for k in range(3):
        s.box((-.69 - k * .28, y - .6, base - (k + 1) * .155 - .025), (.28, 1.1, .05), s.c(TIMBER, .05))
    for x in (-.55, .95):
        for dy in (-.08, -1.15):
            s.box((x, y + dy, base / 2 + .5), (.08, .08, base + 1.0), s.c(TIMBER, .05))
    s.box((.2, y - 1.15, base + .95), (1.58, .06, .08), s.c(TIMBER, .05))
    s.box((.95, y - .62, base + .95), (.06, 1.1, .08), s.c(TIMBER, .05))
    # air conditioner on the end wall and a tow hitch at the other
    s.box((length / 2 + .2, .3, base + 1.7), (.4, .7, .45), '#c9cdd0')
    for k in range(4):
        s.box((length / 2 + .405, .3, base + 1.56 + k * .09), (.01, .6, .03), dark)
    for sy in (-1, 1):
        s.cyl((-length / 2, sy * .8, base - .06), (-length / 2 - 1.1, 0, base - .1), .05, dark, sides=5)
    s.cyl((-length / 2 - 1.0, 0, 0), (-length / 2 - 1.0, 0, base), .04, GALV, sides=6)
    s.box((-length / 2 - 1.0, 0, .012), (.2, .2, .024), GALV)
    s.cyl((2.6, .6, base + wall + .06), (2.6, .6, base + wall + .5), .06, GALV, sides=6)


def excavator(s):
    yellow, dark, glass = '#f0b323', '#2b2e31', GLASS_DARK
    stadium = [(-2.05, .28), (-1.75, 0), (1.75, 0), (2.05, .28), (2.05, .58), (1.75, .86), (-1.75, .86), (-2.05, .58)]
    for sx in (-1, 1):
        with s.at(sx * 1.15, 0, 0):
            wedge_body(s, .6, stadium, dark)
            for y in (-1.75, 1.75):
                s.cyl((0, y, .44), (sx * .32, y, .44), .26, '#8f979b', sides=10)
            s.box((sx * .31, 0, .44), (.02, 3.0, .3), '#3a3d40')
    s.box((0, 0, .6), (1.75, 2.4, .46), dark)
    s.cyl((0, 0, .83), (0, 0, 1.05), .85, '#3a3d40', sides=14)
    with s.at(0, 0, 1.05, yaw=.38):
        wedge_body(s, 2.7, [(-1.0, 0), (2.15, 0), (2.15, .95), (1.75, 1.28), (-1.0, 1.28)], yellow)
        s.box((0, 2.0, .55), (2.74, .36, .9), '#d39a1c')
        for k in range(4):
            s.box((1.356, .6 + k * .32, .78), (.012, .2, .5), dark)
        # cab on the left
        s.box((-.78, -.55, .28), (1.0, 1.5, .56), yellow)
        s.box((-.78, -.55, 1.1), (.98, 1.48, 1.08), glass, gloss=True)
        for dx in (-.49, .49):
            for dy in (-.74, .74):
                s.box((-.78 + dx, -.55 + dy, 1.1), (.07, .07, 1.1), dark)
        s.box((-.78, -.55, 1.68), (1.06, 1.56, .08), dark)
        # two-piece boom, stick and bucket reaching forward
        x = .3
        foot, knee, tip, toe = (x, -.9, .75), (x, -2.6, 2.6), (x, -4.6, 3.1), (x, -6.2, -.1)
        beam_yz(s, foot, knee, .42, .5, yellow)
        beam_yz(s, knee, tip, .42, .46, yellow)
        beam_yz(s, tip, toe, .36, .4, yellow)
        s.cyl((x - .28, knee[1], knee[2]), (x + .28, knee[1], knee[2]), .2, yellow, sides=8)
        for a, b in (((x, -1.45, .7), (x, -2.3, 2.0)), ((x, -2.9, 3.0), (x, -4.4, 3.75)), ((x, -4.8, 3.2), (x, -5.75, 1.3))):
            s.cyl(a, b, .075, '#5e666a', sides=6)
            s.cyl(mix(a, b, .45), b, .045, '#d9dde0', sides=6)
        beam_yz(s, (x, -4.4, 3.75), (x, -4.62, 3.15), .2, .2, yellow)
        # bucket resting on the ground, one turntable height below this frame
        with s.at(x, 0, 0):
            wedge_body(s, 1.05, [(-5.9, .13), (-6.55, -.12), (-6.8, -.67), (-6.4, -1.0), (-6.05, -.67), (-6.1, -.27)], '#3a3d40')
        for k in range(4):
            s.box((x - .36 + k * .24, -6.47, -.99), (.08, .16, .1), '#8f979b')

def skid_steer(s):
    orange, dark = '#e2742b', '#1b1d1f'
    for sx in (-1, 1):
        for y in (-.62, .62):
            wheel(s, (sx * .72, y, .42), .42, .3, sides=12, hub=orange)
        s.box((sx * .72, 0, .82), (.34, 2.0, .06), dark)
    wedge_body(s, 1.08, [(-1.0, .3), (1.25, .3), (1.25, 1.25), (.9, 1.35), (-1.0, 1.0)], orange)
    s.box((0, 1.1, .85), (1.0, .34, .8), '#c9621f')
    # cab cage
    for sx in (-1, 1):
        for y in (-.85, .55):
            s.box((sx * .5, y, 1.5), (.07, .07, 1.0), dark)
        s.box((sx * .5, -.15, 1.52), (.012, 1.3, .86), GLASS_DARK, gloss=True)
    s.box((0, -.15, 2.02), (1.12, 1.55, .08), dark)
    s.box((0, .56, 1.5), (.94, .012, .9), GLASS_DARK, gloss=True)
    # lift arms from the rear towers to a bucket on the ground
    for sx in (-1, 1):
        s.box((sx * .66, 1.0, 1.25), (.14, .3, 1.2), orange)
        beam_yz(s, (sx * .66, 1.0, 1.78), (sx * .66, -.95, 1.2), .12, .16, orange)
        beam_yz(s, (sx * .66, -.95, 1.2), (sx * .66, -1.55, .3), .12, .16, orange)
        s.cyl((sx * .66, .9, 1.0), (sx * .66, -.5, 1.35), .04, '#d9dde0', sides=5)
    wedge_body(s, 1.78, [(-1.5, .04), (-2.2, .04), (-2.28, .12), (-1.75, .62), (-1.5, .62)], '#3a3d40')
    s.box((0, 1.3, .55), (.5, .06, .3), '#f4f1e4')


def lumber_stacks(s):
    wood = ['#d9b98a', '#cfae7c', '#e2c597', '#c9a672']

    def bundle(x, y, yaw, width, length, layers, per):
        with s.at(x, y, 0, yaw=yaw):
            for dy in (-length * .32, 0, length * .32):
                s.box((0, dy, .045), (width + .1, .09, .09), s.pick(WEATHERED, .05))
            board, thick = width / per, .084
            for layer in range(layers):
                z = .09 + layer * (thick + .002) + thick / 2
                for k in range(per):
                    if layer % 4 == 3 and k % 2:
                        continue
                    s.box((-width / 2 + board * (k + .5), (s.random() - .5) * .04, z), (board - .006, length, thick), s.pick(wood, .04))
            top = .09 + layers * (thick + .002)
            for dy in (-length * .3, length * .3):
                s.box((0, dy, top / 2 + .05), (width + .02, .03, top - .08), '#2b2e31')
                s.box((0, dy, top + .004), (width + .02, .03, .008), '#2b2e31')

    bundle(-.9, 0, 0, 1.15, 4.8, 14, 8)
    bundle(.55, -.6, .05, 1.15, 3.6, 9, 8)
    # sheet goods on a pallet
    with s.at(.6, 1.9, 0, yaw=-.08):
        for dx in (-.5, 0, .5):
            s.box((dx, 0, .06), (.1, 2.3, .12), s.pick(WEATHERED, .05))
        for k in range(9):
            s.box(((s.random() - .5) * .02, (s.random() - .5) * .02, .13 + k * .05 + .025), (1.22, 2.44, .048), s.pick(['#c9a877', '#bf9c68', '#d3b382'], .03))
        s.box((0, 0, .59), (1.26, 2.48, .012), '#3f6f8f')


def concrete_barrier(s):
    profile = [(-.305, 0), (.305, 0), (.305, .08), (.2, .33), (.125, .81), (-.125, .81), (-.2, .33), (-.305, .08)]
    wedge_body(s, 3.0, profile, '#b9b6ae')
    for x in (-.9, .9):
        s.box((x, 0, .05), (.3, .63, .1), '#55524c')
    for sx in (-1, 1):
        s.box((sx * 1.502, 0, .45), (.008, .1, .5), '#8f8c84')


# ---------------------------------------------------------------------------
# Painted road barriers. The same 3 m precast section as the plain concrete
# barrier, with an original mural on both long faces. The designs are our own
# flat-colour compositions on local themes; none reproduces a real mural or
# carries a program name, logo or wording.
#
# A mural is drawn in (u, v) metres: u runs 0 to 3 along the barrier and v runs
# up the face from the top of the unpainted toe. Shapes are convex polygons that
# tile the face without overlapping, then are folded over the bend in the
# barrier's profile, so no painted surface ever lies on top of another.
# ---------------------------------------------------------------------------
MURAL_LENGTH = 3.0
MURAL_LOWER = math.hypot(.305 - .2, .33 - .08)
MURAL_UPPER = math.hypot(.2 - .125, .81 - .33)
MURAL_HEIGHT = MURAL_LOWER + MURAL_UPPER
BARRIER_CONCRETE = '#b9b6ae'


def clip(polygon, a, b, c):
    """The part of a convex (u, v) polygon where a*u + b*v >= c."""
    out = []
    for i, p in enumerate(polygon):
        q = polygon[(i + 1) % len(polygon)]
        dp, dq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if dp >= 0:
            out.append(p)
        if (dp > 0 > dq) or (dp < 0 < dq):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def polygon_area(polygon):
    return abs(sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def mural_point(u, v, side, upper, proud):
    """Map mural coordinates onto one long face. Each side reads left to right when faced."""
    x = (MURAL_LENGTH / 2 - u) * side
    if upper:
        t = (v - MURAL_LOWER) / MURAL_UPPER
        y, z, ny, nz = .2 - .075 * t, .33 + .48 * t, .48 / MURAL_UPPER, .075 / MURAL_UPPER
    else:
        t = v / MURAL_LOWER
        y, z, ny, nz = .305 - .105 * t, .08 + .25 * t, .25 / MURAL_LOWER, .105 / MURAL_LOWER
    return (x, side * (y + ny * proud), z + nz * proud)


def paint(s, polygon, colour, proud=0.0):
    """One convex mural shape on both faces. Only a few accents sit proud, above the tiled field."""
    polygon = clip(clip(polygon, 1, 0, 0), -1, 0, -MURAL_LENGTH)
    repeats = getattr(s, 'low_profile', 0)
    if repeats:
        piece = clip(clip(polygon, 0, 1, 0.0), 0, -1, -MURAL_HEIGHT)
        if len(piece) >= 3 and polygon_area(piece) >= 2e-6:
            for k in range(repeats):
                for side in (-1, 1):
                    s.poly([low_profile_point((u + k * MURAL_LENGTH) / repeats, v / 2, side, proud) for u, v in piece], colour)
        return
    for upper, low, high in ((False, 0.0, MURAL_LOWER), (True, MURAL_LOWER, MURAL_HEIGHT)):
        piece = clip(clip(polygon, 0, 1, low), 0, -1, -high)
        if len(piece) < 3 or polygon_area(piece) < 2e-6:
            continue
        for side in (-1, 1):
            s.poly([mural_point(u, v, side, upper, proud) for u, v in piece], colour)


def paint_bands(s, curves, colours, columns=36):
    """Stacked colour bands split by curves v = f(u), bottom to top. One more colour than curves."""
    assert len(colours) == len(curves) + 1

    def levels(u):
        out, floor = [-.1], -.1
        for curve in curves:
            floor = max(floor, curve(u))
            out.append(floor)
        return out + [MURAL_HEIGHT + .1]

    for k in range(columns):
        u0, u1 = MURAL_LENGTH * k / columns, MURAL_LENGTH * (k + 1) / columns
        a, b = levels(u0), levels(u1)
        for i, colour in enumerate(colours):
            paint(s, [(u0, a[i]), (u1, b[i]), (u1, b[i + 1]), (u0, a[i + 1])], colour)


def paint_above(s, polygon, colour, curve, columns=36, proud=.004):
    """An accent shown only above a band curve, such as a sun rising behind a skyline."""
    for k in range(columns):
        u0, u1 = MURAL_LENGTH * k / columns, MURAL_LENGTH * (k + 1) / columns
        v0, v1 = curve(u0), curve(u1)
        piece = clip(clip(polygon, 1, 0, u0), -1, 0, -u1)
        # keep the side of the line through (u0, v0) and (u1, v1) that lies above it
        piece = clip(piece, -(v1 - v0), u1 - u0, -(v1 - v0) * u0 + (u1 - u0) * v0)
        if len(piece) >= 3:
            paint(s, piece, colour, proud)


def disc(u, v, radius, sides=16):
    return [(u + math.cos(k * math.tau / sides) * radius, v + math.sin(k * math.tau / sides) * radius) for k in range(sides)]


def zigzag(x):
    """Triangle wave between 0 and 1 with period 1."""
    return 2 * abs(x - math.floor(x) - .5)


def wave(u, cycles, phase=0.0):
    """Sine that repeats every barrier length, so adjoining sections join cleanly."""
    return math.sin(math.tau * (u / MURAL_LENGTH * cycles) + phase)


def mural_barrier(s, top):
    """The barrier without its two painted faces: ends, toe, top, underside and lifting slots."""
    if getattr(s, 'low_profile', 0):
        low_profile_body(s, faces=False)
        return
    half = MURAL_LENGTH / 2
    for sx in (-1, 1):
        x = sx * half
        s.poly([(x, y, z) for y, z in ((-.305, 0), (.305, 0), (.305, .08), (.2, .33), (-.2, .33), (-.305, .08))], BARRIER_CONCRETE)
        s.poly([(x, y, z) for y, z in ((-.2, .33), (.2, .33), (.125, .81), (-.125, .81))], BARRIER_CONCRETE)
        s.box((sx * (half + .002), 0, .45), (.008, .1, .5), '#8f8c84')
    for sy in (-1, 1):
        s.quad((-half, sy * .305, 0), (half, sy * .305, 0), (half, sy * .305, .08), (-half, sy * .305, .08), '#a5a29a')
    s.quad((-half, -.125, .81), (half, -.125, .81), (half, .125, .81), (-half, .125, .81), top)
    s.quad((-half, -.305, 0), (half, -.305, 0), (half, .305, 0), (-half, .305, 0), BARRIER_CONCRETE)
    for x in (-.9, .9):
        s.box((x, 0, .05), (.3, .63, .1), '#55524c')


def mural_foothills(s):
    mural_barrier(s, '#3a4a6b')
    def prairie(u):
        return .09 + .02 * wave(u, 2)
    def foothills(u):
        return .24 + .045 * wave(u, 2, 1.0) + .025 * wave(u, 5, .5)
    def peaks(u):
        return .39 + .17 * zigzag(u / MURAL_LENGTH * 3 + .1) + .07 * zigzag(u / MURAL_LENGTH * 7 + .4)
    def snow(u):
        return min(peaks(u), max(peaks(u) - .055, .5))
    paint_bands(s, [prairie, foothills, snow, peaks, lambda u: .655, lambda u: .71],
                ['#d8b24a', '#4f7a5a', '#3a4a6b', '#f1f0ea', '#f6c15b', '#f08a5d', '#7a5a9a'], columns=42)
    paint_above(s, disc(2.32, .56, .1), '#fff1b8', peaks, columns=42)


def mural_chinook(s):
    mural_barrier(s, '#5b3a78')
    def horizon(u):
        return .085 + .012 * wave(u, 3)
    def range_line(u):
        return .15 + .035 * zigzag(u / MURAL_LENGTH * 4 + .3) + .02 * zigzag(u / MURAL_LENGTH * 9)
    def arch(u):
        return .3 + .3 * math.sin(math.pi * u / MURAL_LENGTH) ** .8
    paint_bands(s, [horizon, range_line, lambda u: arch(u) - .11, arch, lambda u: arch(u) + .07, lambda u: arch(u) + .15],
                ['#c99a3c', '#2f3a4f', '#fbd27a', '#f7e3a1', '#e7733c', '#b8456b', '#5b3a78'], columns=36)
    paint_above(s, disc(1.5, .16, .1), '#fff7d6', range_line)


def mural_river(s):
    mural_barrier(s, '#0f4c75')
    count = 7
    curves = [(lambda u, i=i: MURAL_HEIGHT * i / count + .035 * wave(u, 2, i * .9) + .018 * wave(u, 3, i * 1.7)) for i in range(1, count)]
    paint_bands(s, curves, ['#0f4c75', '#1b6ca8', '#3fa7d6', '#9bd4e4', '#f1f0ea', '#59c3a3', '#1f7a6c'], columns=30)


def mural_mosaic(s):
    mural_barrier(s, '#073b4c')
    palette = ['#ef476f', '#ffd166', '#06d6a0', '#118ab2', '#073b4c', '#f78c6b', '#f1f0ea']
    cols, rows = 12, 5
    grid = {}
    for i in range(cols + 1):
        for j in range(rows + 1):
            du = 0 if i in (0, cols) else (s.random() - .5) * .11
            dv = 0 if j in (0, rows) else (s.random() - .5) * .07
            grid[i, j] = (MURAL_LENGTH * i / cols + du, MURAL_HEIGHT * j / rows + dv)
    for i in range(cols):
        for j in range(rows):
            a, b, c, d = grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]
            first, second = ((a, b, c), (a, c, d)) if (i + j) % 2 else ((a, b, d), (b, c, d))
            last = None
            for triangle in (first, second):
                tone = palette[int(s.random() * len(palette))]
                while tone == last:
                    tone = palette[int(s.random() * len(palette))]
                last = tone
                paint(s, list(triangle), tone)


def mural_chevron(s):
    mural_barrier(s, '#111827')
    pitch, tones = .15, ['#111827', '#f1f0ea', '#ef476f', '#ffd166']
    curves = [(lambda u, i=i: i * pitch - .2 + .22 * zigzag(u / MURAL_LENGTH * 6)) for i in range(1, 8)]
    paint_bands(s, curves, [tones[i % len(tones)] for i in range(8)], columns=12)


def mural_quilt(s):
    mural_barrier(s, '#2f4b6e')
    palette = ['#9b2d30', '#d9a441', '#f1e9d2', '#2f4b6e', '#7a8f6a']
    cols, rows = 12, 3
    w, h = MURAL_LENGTH / cols, MURAL_HEIGHT / rows
    for i in range(cols):
        for j in range(rows):
            u, v = i * w, j * h
            a, b, c, d, m = (u, v), (u + w, v), (u + w, v + h), (u, v + h), (u + w / 2, v + h / 2)
            first = palette[int(s.random() * len(palette))]
            second = palette[(palette.index(first) + 1 + int(s.random() * (len(palette) - 1))) % len(palette)]
            kind = int(s.random() * 3)
            if kind == 0:
                pieces = [((a, b, c), first), ((a, c, d), second)]
            elif kind == 1:
                pieces = [((a, b, d), first), ((b, c, d), second)]
            else:
                pieces = [((a, b, m), first), ((b, c, m), second), ((c, d, m), first), ((d, a, m), second)]
            for points, tone in pieces:
                paint(s, list(points), tone)


def mural_aspen(s):
    mural_barrier(s, '#e6b93a')
    trunks = [(.16, .1), (.47, .13), (.83, .09), (1.12, .12), (1.5, .14), (1.86, .1), (2.14, .12), (2.52, .13), (2.82, .09)]
    edges = [0.0] + [e for centre, width in trunks for e in (centre - width / 2, centre + width / 2)] + [MURAL_LENGTH]
    def canopy(u):
        return .47 + .05 * wave(u, 4) + .03 * wave(u, 9, 1.0)
    def ground(u):
        return .085 + .018 * wave(u, 3, .5)
    for k, (u0, u1) in enumerate(zip(edges, edges[1:])):
        if k % 2:
            paint(s, [(u0, -.1), (u1, -.1), (u1, MURAL_HEIGHT + .1), (u0, MURAL_HEIGHT + .1)], '#f1eee4')
            centre = (u0 + u1) / 2
            for _ in range(4):
                v = .06 + s.random() * (MURAL_HEIGHT - .12)
                half = (u1 - u0) * (.18 + s.random() * .2)
                side = -1 if s.random() < .5 else 1
                paint(s, [(centre + side * (u1 - u0) * .12 - half, v), (centre + side * (u1 - u0) * .12 + half, v + .006), (centre + side * (u1 - u0) * .12, v + .03)], '#2a2623', proud=.004)
            continue
        steps = max(1, round((u1 - u0) / .09))
        for n in range(steps):
            a, b = u0 + (u1 - u0) * n / steps, u0 + (u1 - u0) * (n + 1) / steps
            levels = [(-.1, -.1), (ground(a), ground(b)), (canopy(a), canopy(b)), (MURAL_HEIGHT + .1, MURAL_HEIGHT + .1)]
            for (low, high), tone in zip(zip(levels, levels[1:]), ('#6f8a3c', '#8ec3d6', '#e6b93a')):
                paint(s, [(a, low[0]), (b, low[1]), (b, high[1]), (a, high[0])], tone)


def mural_confetti(s):
    mural_barrier(s, '#1f5f6b')
    paint(s, [(0, -.1), (MURAL_LENGTH, -.1), (MURAL_LENGTH, MURAL_HEIGHT + .1), (0, MURAL_HEIGHT + .1)], '#1f5f6b')
    tones, placed = ['#ffd166', '#ef476f', '#f1f0ea', '#06d6a0', '#f78c6b'], []
    for _ in range(400):
        radius = .035 + s.random() * .075
        u, v = radius + s.random() * (MURAL_LENGTH - 2 * radius), radius + .01 + s.random() * (MURAL_HEIGHT - 2 * radius - .02)
        if all(math.hypot(u - pu, v - pv) > radius + pr + .02 for pu, pv, pr in placed):
            placed.append((u, v, radius))
            paint(s, disc(u, v, radius, 14), tones[len(placed) % len(tones)], proud=.004)
        if len(placed) >= 46:
            break


# ---------------------------------------------------------------------------
# District barriers: the 3 m road barrier in the colours of a business district,
# carrying its logo on both long faces. The artwork is baked from each district's
# own logo files by bake_district_logos.py into triangles that tile the face in
# (u, v) metres, already split at the bend, so nothing here lies on top of
# anything else. The logos belong to their business improvement areas.
# ---------------------------------------------------------------------------
DISTRICT_SHAPES = Path(__file__).with_name('district_logo_shapes.json')
_district_art = {}


def district_art(district):
    if not _district_art:
        baked = json.loads(DISTRICT_SHAPES.read_text(encoding='utf-8'))
        face = baked['face']
        assert abs(face['length'] - MURAL_LENGTH) < 1e-6 and abs(face['bend'] - MURAL_LOWER) < 1e-5 and abs(face['height'] - MURAL_HEIGHT) < 1e-5
        _district_art.update(baked['districts'])
    return _district_art[district]


def district_barrier(s, district):
    art = district_art(district)
    mural_barrier(s, art['top'])
    tones = [s.c(colour) for colour in art['colours']]
    for a, b, c, tone in art['triangles']:
        corners = [art['vertices'][index] for index in (a, b, c)]
        upper = sum(v for _, v in corners) / 3 > MURAL_LOWER
        for side in (-1, 1):
            p, q, r = (mural_point(u, MURAL_LOWER if abs(v - MURAL_LOWER) < 1e-4 else v, side, upper, 0.0) for u, v in corners)
            # keep each face's triangles wound to face outward
            outward = ((q[2] - p[2]) * (r[0] - p[0]) - (q[0] - p[0]) * (r[2] - p[2])) * side > 0
            s.tri(p, q, r, tones[tone]) if outward else s.tri(p, r, q, tones[tone])


def district_barrier_kensington(s):
    district_barrier(s, 'kensington')


def district_barrier_inglewood(s):
    district_barrier(s, 'inglewood')


def district_barrier_fourth_street_purple(s):
    district_barrier(s, 'fourth-street-purple')


def district_barrier_fourth_street_green(s):
    district_barrier(s, 'fourth-street-green')


def district_barrier_seventeenth_ave(s):
    district_barrier(s, 'seventeenth-ave')


def district_barrier_seventeenth_ave_single(s):
    district_barrier(s, 'seventeenth-ave-single')


# ---------------------------------------------------------------------------
# City Ghost: a public sculpture made to sit astride these barriers, modelled
# from photographs and its concept sheet. A blue ghost just under 2 m tall with
# two tall white eyes, a small smile, stubby arms and a cowboy hat. The
# sculpture is its artist's work; see docs/CITY_GHOST_BARRIER_2026-11-17.md.
#
# The ghost faces -y. Its body is one skin over rings of a rounded section: a
# scalloped skirt that hangs either side of the barrier, straight sides and a
# rounded head. Each eye is a block of that skin rebuilt around an oval, so the
# socket has a clean edge and the white of the eye truly sits in it.
# ---------------------------------------------------------------------------
GHOST_BLUE, GHOST_CUP, GHOST_UNDER = '#27a8d2', '#1b8db6', '#187a9f'
GHOST_WHITE, GHOST_PUPIL, GHOST_GLINT = '#f5f5f2', '#16161a', '#ffffff'
GHOST_HAT, GHOST_HAT_BAND = '#b98f52', '#8a683a'
GHOST_A, GHOST_B = .435, .33              # half width and half depth of the body
GHOST_SKIRT, GHOST_SHOULDER, GHOST_TOP = .585, 1.44, 1.94
GHOST_COLUMNS, GHOST_LOBES, GHOST_DROP = 48, 8, .125   # six columns to a lobe, so every cusp falls on one
GHOST_EYE = (.155, 1.52, .118, .32)       # centre x, centre z, half width and half height of an eye
GHOST_LOOK = (.014, -.03, .056, .13)      # a pupil: how far toward the nose and how far up from the eye's centre, half width, half height


def ghost_scale(z):
    """Width of the body at height z as a share of its full width: a slight flare toward
    the skirt, and a rounded head above the shoulder."""
    if z <= GHOST_SHOULDER:
        return 1 + .035 * (GHOST_SHOULDER - z) / (GHOST_SHOULDER - GHOST_SKIRT)
    t = min(1.0, (z - GHOST_SHOULDER) / (GHOST_TOP - GHOST_SHOULDER))
    return max(0.0, 1 - t ** 3.2) ** (1 / 3.2)


def ghost_front(x, z):
    """y of the front of the body at (x, z)."""
    scale = ghost_scale(z)
    return -GHOST_B * scale * max(0.0, 1 - abs(x / (GHOST_A * scale)) ** 2.6) ** (1 / 2.6)


def ghost_section(count):
    """count points round the body's section, evenly spaced along it, from the middle of
    the front toward +x, in units of the half width and half depth."""
    fine = 1440
    points = []
    for k in range(fine + 1):
        angle = -math.pi / 2 + math.tau * k / fine
        c, w = math.cos(angle), math.sin(angle)
        points.append((math.copysign(abs(c) ** (2 / 2.6), c), math.copysign(abs(w) ** (2 / 2.6), w)))
    lengths = [0.0]
    for k in range(fine):
        lengths.append(lengths[-1] + math.hypot((points[k + 1][0] - points[k][0]) * GHOST_A, (points[k + 1][1] - points[k][1]) * GHOST_B))
    out, k = [(0.0, -1.0)], 0
    for i in range(1, count):
        target = lengths[-1] * i / count
        while lengths[k + 1] < target:
            k += 1
        t = (target - lengths[k]) / (lengths[k + 1] - lengths[k])
        out.append((points[k][0] + (points[k + 1][0] - points[k][0]) * t, points[k][1] + (points[k + 1][1] - points[k][1]) * t))
    # the body is the same left and right: mirror the first half exactly
    for i in range(1, count // 2):
        out[count - i] = (-out[i][0], out[i][1])
    return out


def ghost_eye(s, grid, columns, rows, side):
    """Rebuild a block of the skin around one eye: a rim from the block's edge to the oval,
    a shallow step down into the socket, then the white of the eye, which swells gently
    back out. The black pupil and its glint are painted just proud of the white. columns
    and rows are the first and last grid lines of the block; side is +1 for the eye at +x."""
    ex, ez, rx, rz = side * GHOST_EYE[0], GHOST_EYE[1], GHOST_EYE[2], GHOST_EYE[3]
    count = len(grid[0])
    (i0, i1), (j0, j1) = columns, rows
    border = [(j0, i) for i in range(i0, i1)] + [(j, i1) for j in range(j0, j1)] + [(j1, i) for i in range(i1, i0, -1)] + [(j, i0) for j in range(j1, j0, -1)]
    edge, oval = [], []
    for j, i in border:
        x, y, z = grid[j][i % count]
        reach = math.hypot((x - ex) / rx, (z - ez) / rz)
        assert reach > 1.04, 'the eye must sit inside its block'
        edge.append((x, y, z))
        oval.append((ex + (x - ex) / reach, ez + (z - ez) / reach))

    def white(x, z, proud=0.0):
        """A point on the white of the eye: 12 mm inside the skin at the socket's edge,
        swelling to 8 mm outside it in the middle."""
        share = min(1.0, math.hypot((x - ex) / rx, (z - ez) / rz))
        return (x, ghost_front(x, z) + .012 * share * share - .008 * (1 - share * share) - proud, z)

    def ring(share):
        return [white(ex + (x - ex) * share, ez + (z - ez) * share) for x, z in oval]

    rings = [edge, [(x, ghost_front(x, z), z) for x, z in oval], ring(1.0), ring(.72), ring(.4)]
    tones = (GHOST_BLUE, GHOST_CUP, GHOST_WHITE, GHOST_WHITE)
    total = len(border)
    for r, tone in enumerate(tones):
        for k in range(total):
            n = (k + 1) % total
            s.quad(rings[r][k], rings[r][n], rings[r + 1][n], rings[r + 1][k], tone)
    for k in range(total):
        s.tri(rings[-1][k], rings[-1][(k + 1) % total], white(ex, ez), GHOST_WHITE)

    def patch(cx, cz, hx, hz, colour, proud, segments, shares):
        """An oval painted on the white of the eye, following its curve."""
        loops = [[white(cx + hx * share * math.cos(math.tau * k / segments), cz + hz * share * math.sin(math.tau * k / segments), proud) for k in range(segments)] for share in shares]
        for r in range(len(loops) - 1):
            for k in range(segments):
                n = (k + 1) % segments
                s.quad(loops[r][k], loops[r][n], loops[r + 1][n], loops[r + 1][k], colour)
        for k in range(segments):
            s.tri(loops[-1][k], loops[-1][(k + 1) % segments], white(cx, cz, proud), colour)

    px, pz = ex - side * GHOST_LOOK[0], ez + GHOST_LOOK[1]
    patch(px, pz, GHOST_LOOK[2], GHOST_LOOK[3], GHOST_PUPIL, .004, 18, (1.0, .55))
    patch(px - .02, pz + .056, .017, .019, GHOST_GLINT, .007, 10, (1.0,))


def ghost_blob(s, radii, taper, rings=7, sides=10):
    """An egg: an ellipsoid whose rings narrow toward the top by the taper."""
    loops = []
    for r in range(1, rings):
        latitude = -math.pi / 2 + math.pi * r / rings
        shrink = math.cos(latitude) * (1 - taper * (math.sin(latitude) + 1) / 2)
        loops.append([(radii[0] * shrink * math.cos(math.tau * k / sides), radii[1] * shrink * math.sin(math.tau * k / sides), radii[2] * math.sin(latitude)) for k in range(sides)])
    s.loft(loops, GHOST_BLUE, cap_start=False, cap_end=False)
    for k in range(sides):
        s.tri((0, 0, -radii[2]), loops[0][(k + 1) % sides], loops[0][k], GHOST_BLUE)
        s.tri((0, 0, radii[2] * (1 - taper * .2)), loops[-1][k], loops[-1][(k + 1) % sides], GHOST_BLUE)


def ghost_hat(s):
    """Cowboy hat: a creased crown with a band, and a brim that curls up at both sides."""
    sides = 20

    def oval(rx, ry, z, lift=0.0):
        return [(rx * math.cos(math.tau * k / sides), ry * math.sin(math.tau * k / sides), z + lift * math.cos(math.tau * k / sides) ** 2) for k in range(sides)]
    s.loft([oval(.118, .098, 0), oval(.19, .14, .004, .014), oval(.255, .178, .0, .05), oval(.295, .2, .012, .085)], GHOST_HAT, cap_start=False, cap_end=False)
    s.loft([oval(.12, .1, .0), oval(.121, .101, .03)], GHOST_HAT_BAND, cap_start=False, cap_end=False)
    crown = [oval(.118, .098, .03), oval(.112, .092, .085), oval(.098, .078, .118), oval(.06, .045, .104)]
    s.loft(crown, GHOST_HAT, cap_start=False, cap_end=False)
    for k in range(sides):
        s.tri((0, 0, .094), crown[-1][k], crown[-1][(k + 1) % sides], GHOST_HAT)


def city_ghost(s):
    """The ghost astride a barrier that runs along x, centred on it."""
    count = GHOST_COLUMNS
    section = ghost_section(count)
    # rings: few on the straight sides below the eyes, closer where the eyes and the head need them
    heights = [GHOST_SKIRT + (1.15 - GHOST_SKIRT) * k / 4 for k in range(4)] + [1.15 + (GHOST_SHOULDER - 1.15) * k / 5 for k in range(6)]
    heights.append(GHOST_SHOULDER + .08)
    for k in range(1, 10):
        heights.append(GHOST_SHOULDER + (GHOST_TOP - GHOST_SHOULDER) * math.sin(math.pi / 2 * k / 10) ** (2 / 3.2))
    grid = [[(x * GHOST_A * ghost_scale(z), y * GHOST_B * ghost_scale(z), z) for x, y in section] for z in heights]

    # the two eye blocks, each a run of whole grid cells from the middle of the face outward
    eye_x, eye_z, eye_rx, eye_rz = GHOST_EYE
    reach = next(i for i in range(1, count // 4) if section[i][0] * GHOST_A >= eye_x + eye_rx + .025)
    low = max(j for j, z in enumerate(heights) if z <= eye_z - eye_rz - .035)
    high = min(j for j, z in enumerate(heights) if z >= eye_z + eye_rz + .018)
    for j in range(len(heights) - 1):
        for i in range(count):
            if low <= j < high and (i < reach or i >= count - reach):
                continue
            n = (i + 1) % count
            s.quad(grid[j][i], grid[j][n], grid[j + 1][n], grid[j + 1][i], GHOST_BLUE)
    ghost_eye(s, grid, (0, reach), (low, high), 1)
    ghost_eye(s, grid, (count - reach, count), (low, high), -1)
    for i in range(count):
        s.tri(grid[-1][i], grid[-1][(i + 1) % count], (0, 0, GHOST_TOP), GHOST_BLUE)

    # the skirt: eight rounded lobes that hang below the body, tucked under at their tips
    def lobes(share, tuck):
        ring = []
        for i, (x, y) in enumerate(section):
            across = 2 * ((i / count * GHOST_LOBES + .5) % 1) - 1
            drop = GHOST_DROP * math.sqrt(max(0.0, 1 - across * across))
            scale = ghost_scale(GHOST_SKIRT) * (1 - tuck * drop / GHOST_DROP)
            ring.append((x * GHOST_A * scale, y * GHOST_B * scale, GHOST_SKIRT - drop * share))
        return ring
    hem = [grid[0], lobes(.7, .0), lobes(1.0, .16)]
    s.loft(hem, GHOST_BLUE, cap_start=False, cap_end=False)
    for i in range(count):
        s.tri(hem[2][(i + 1) % count], hem[2][i], (0, 0, GHOST_SKIRT - .03), GHOST_UNDER)

    # a small smile, painted a shade darker just proud of the skin
    steps, half = 10, .12

    def lip(k, lower):
        x = -half + 2 * half * k / steps
        z = 1.095 + .016 * (x / half) ** 2 - (.034 * (1 - (x / half) ** 2) if lower else 0.0)
        return (x, ghost_front(x, z) - .004, z)
    for k in range(steps):
        s.quad(lip(k, True), lip(k + 1, True), lip(k + 1, False), lip(k, False), GHOST_CUP)

    for side in (-1, 1):
        with s.at(side * (GHOST_A * ghost_scale(1.08) - .012), -.02, 1.08, pitch=-side * .2):
            ghost_blob(s, (.088, .115, .185), .45)
    with s.at(.015, .01, GHOST_TOP + .006, yaw=.2, pitch=.045, roll=-.03):
        ghost_hat(s)


GHOST_PINK = '#ee8f8c'


def city_ghost_barrier(s):
    concrete_barrier(s)
    city_ghost(s)


# White line characters for the pink barrier under the ghost. The real barrier carries
# its artist's hand-drawn characters. These are simple ones of our own in the same
# spirit, not tracings: marker strokes 4 mm proud of the paint, three rows of three
# either side of the ghost. Each character is drawn in a unit square, x right and y up,
# as open or closed strokes plus dots for eyes.
GHOST_INK = '#fbf7f3'
DOODLE_SIZE, DOODLE_STROKE, DOODLE_DOT = .2, .011, .014


def doodle_arc(cx, cy, rx, ry, start, finish, steps):
    """Points along an arc of an oval, in degrees. A full turn leaves off its last point, ready to be closed."""
    count = steps if finish - start >= 360 else steps + 1
    return [(cx + rx * math.cos(math.radians(start + (finish - start) * k / steps)), cy + ry * math.sin(math.radians(start + (finish - start) * k / steps))) for k in range(count)]


def doodle(closed=(), lines=(), dots=()):
    return {'closed': list(closed), 'lines': list(lines), 'dots': list(dots)}


DOODLES = {
    'ghost': doodle(closed=[[(.14, .06), *doodle_arc(.5, .56, .36, .38, 180, 0, 6), (.86, .06), (.68, .17), (.5, .06), (.32, .17)]],
                    lines=[[(.4, .42), (.5, .37), (.6, .42)]], dots=[(.37, .6), (.63, .6)]),
    'robot': doodle(closed=[[(.2, .1), (.8, .1), (.88, .18), (.88, .66), (.8, .74), (.2, .74), (.12, .66), (.12, .18)]],
                    lines=[[(.36, .74), (.3, .93)], [(.64, .74), (.7, .93)], [(.3, .32), (.4, .22), (.5, .32), (.6, .22), (.7, .32)]],
                    dots=[(.36, .54), (.64, .54), (.3, .95), (.7, .95)]),
    'slice': doodle(closed=[[(.5, .92), (.92, .1), (.08, .1)]],
                    lines=[[(.34, .8), (.5, 1.0), (.66, .8)], [(.44, .28), (.51, .23), (.58, .28)], [(.3, .1), (.26, 0)], [(.7, .1), (.74, 0)]],
                    dots=[(.42, .44), (.6, .44)]),
    'blob': doodle(closed=[doodle_arc(.5, .5, .4, .4, 0, 360, 10), doodle_arc(.36, .58, .11, .13, 0, 360, 6), doodle_arc(.64, .58, .11, .13, 0, 360, 6)],
                   lines=[[(.42, .29), (.5, .25), (.58, .29)]], dots=[(.38, .56), (.62, .56)]),
    'mound': doodle(closed=[doodle_arc(.5, .1, .42, .72, 180, 0, 7)],
                    lines=[[(.34, .31), (.42, .25), (.5, .31), (.58, .25), (.66, .31)]], dots=[(.38, .5), (.62, .5)]),
    'berry': doodle(closed=[[(.14, .66), (.5, .78), (.86, .66), (.8, .38), (.5, .06), (.2, .38)]],
                    lines=[[(.3, .78), (.4, .96), (.5, .8), (.6, .96), (.7, .78)], [(.43, .4), (.5, .36), (.57, .4)]], dots=[(.4, .54), (.6, .54)]),
    'capsule': doodle(closed=[[(.3, .08), (.7, .08), (.78, .18), (.78, .7), (.66, .86), (.34, .86), (.22, .7), (.22, .18)]],
                      lines=[[(.2, .72), (.96, .72)], [(.42, .36), (.58, .36)], [(.38, .08), (.36, 0)], [(.62, .08), (.64, 0)]], dots=[(.4, .54), (.6, .54)]),
    'king': doodle(closed=[[(.2, .06), (.8, .06), (.74, .6), (.26, .6)]],
                   lines=[[(.26, .6), (.22, .92), (.38, .74), (.5, .96), (.62, .74), (.78, .92), (.74, .6)], [(.42, .27), (.5, .21), (.58, .27)]], dots=[(.4, .42), (.6, .42)]),
    'fish': doodle(closed=[doodle_arc(.44, .5, .34, .26, 0, 360, 8), [(.78, .5), (.98, .72), (.98, .28)]],
                   lines=[[(.14, .44), (.24, .42)], [(.44, .76), (.52, .9), (.6, .74)]], dots=[(.3, .56)]),
}
# rows from the top of the barrier down, left of the ghost and then right of it; the right-hand ones face the other way
DOODLE_ROWS = ((('king', 'robot', 'blob'), ('robot', 'ghost', 'mound')),
               (('berry', 'ghost', 'mound'), ('blob', 'slice', 'capsule')),
               (('slice', 'fish', 'capsule'), ('fish', 'king', 'berry')))
DOODLE_COLUMNS = ((.19, .47, .75), (2.25, 2.53, 2.81))
DOODLE_HEIGHTS = (.633, .397, .137)        # centre of each row up the painted face; the lowest row sits on the lower slope


def doodle_quad(s, corners, upper):
    """One flat piece of a stroke on both long faces, in (u, v) metres."""
    ink = s.c(GHOST_INK)
    for side in (-1, 1):
        p, q, r, t = (mural_point(u, v, side, upper, .004) for u, v in corners)
        if ((q[2] - p[2]) * (r[0] - p[0]) - (q[0] - p[0]) * (r[2] - p[2])) * side > 0:
            s.tri(p, q, r, ink)
            s.tri(p, r, t, ink)
        else:
            s.tri(p, r, q, ink)
            s.tri(p, t, r, ink)


def doodle_character(s, name, u, v, upper, mirror):
    """Draw one character centred at (u, v), with the small wobble, turn and change of size of a hand at work."""
    turn, size = (s.random() - .5) * .2, DOODLE_SIZE * (.92 + s.random() * .12)
    low, high = (MURAL_LOWER, MURAL_HEIGHT) if upper else (0.0, MURAL_LOWER)

    def place(point):
        x, y = point[0] + (s.random() - .5) * .024 - .5, point[1] + (s.random() - .5) * .024 - .5
        if mirror:
            x = -x
        pu, pv = u + (x * math.cos(turn) - y * math.sin(turn)) * size, v + (x * math.sin(turn) + y * math.cos(turn)) * size
        assert low + .012 < pv < high - .012, f'{name} must stay on one slope of the barrier'
        return (pu, pv)

    def stroke(a, b):
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if length < 1e-6:
            return
        du, dv = (b[0] - a[0]) / length * DOODLE_STROKE / 2, (b[1] - a[1]) / length * DOODLE_STROKE / 2
        # square ends, half a stroke long, so that strokes close up where they meet
        doodle_quad(s, [(a[0] - du - dv, a[1] - dv + du), (b[0] + du - dv, b[1] + dv + du), (b[0] + du + dv, b[1] + dv - du), (a[0] - du + dv, a[1] - dv - du)], upper)

    shape = DOODLES[name]
    for points, closed in [(points, True) for points in shape['closed']] + [(points, False) for points in shape['lines']]:
        placed = [place(point) for point in points]
        for k in range(len(placed) if closed else len(placed) - 1):
            stroke(placed[k], placed[(k + 1) % len(placed)])
    for point in shape['dots']:
        cu, cv = place(point)
        doodle_quad(s, [(cu - DOODLE_DOT, cv), (cu, cv - DOODLE_DOT), (cu + DOODLE_DOT, cv), (cu, cv + DOODLE_DOT)], upper)


def city_ghost_barrier_pink(s):
    mural_barrier(s, GHOST_PINK)
    paint(s, [(0, 0), (MURAL_LENGTH, 0), (MURAL_LENGTH, MURAL_HEIGHT), (0, MURAL_HEIGHT)], GHOST_PINK)
    city_ghost(s)
    for (left, right), v in zip(DOODLE_ROWS, DOODLE_HEIGHTS):
        for names, columns, mirror in ((left, DOODLE_COLUMNS[0], False), (right, DOODLE_COLUMNS[1], True)):
            for name, u in zip(names, columns):
                doodle_character(s, name, u, v, v > MURAL_LOWER, mirror)


# ---------------------------------------------------------------------------
# Seasonal patios: boardwalk sections, on-street patios, parklets and a sidewalk
# patio. Dimensions follow the City of Calgary's published "Guidelines for
# Seasonal Patios located on public property": a platform level with the
# sidewalk, a guard 1.0 m high and never more than 1.2 m above the street, a
# cane-detectable rail within 100 mm of the walking surface, at least 2 m of
# clear walkway, umbrella canopies at least 2.1 m up, nothing fixed to the road,
# and a hazard marker on the corner facing approaching traffic. These are
# concept models for site visualization, not permit drawings.
#
# x runs along the curb. The road is at -y and the sidewalk at +y. For
# right-hand traffic in the lane beside the curb, vehicles approach from +x.
# ---------------------------------------------------------------------------
DECK = .15
GUARD = 1.0
DECK_TONES = ['#b99a6b', '#ad8f61', '#c2a374', '#a98a5c']
GUARD_TIMBER = '#8a6a4a'


def deck(s, x0, x1, y0, y1, top=DECK, plank=.143):
    """Timber platform at sidewalk grade: skirt boards, and planks laid across the path of travel."""
    skirt = '#806848'
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        s.quad((a[0], a[1], 0), (b[0], b[1], 0), (b[0], b[1], top), (a[0], a[1], top), skirt)
    count = max(1, round((x1 - x0) / plank))
    for k in range(count):
        xa, xb = x0 + (x1 - x0) * k / count, x0 + (x1 - x0) * (k + 1) / count
        s.quad((xa, y0, top), (xb, y0, top), (xb, y1, top), (xa, y1, top), s.pick(DECK_TONES, .03))


def guard_run(s, a, b, base=DECK, road=0, feet=0, colour=GUARD_TIMBER):
    """Patio guard from a to b: posts about every metre and never at the ends, so runs butt
    together; a handrail, two boards and a cane-detection rail. road is +1 or -1 for the
    side of the run, left or right of a to b, that carries reflective tape. feet is +1 or
    -1 for the side the weighted feet reach toward, which must be the patio side: supports
    may not project into the walkway."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < .05:
        return
    with s.at(a[0], a[1], base, yaw=math.atan2(b[1] - a[1], b[0] - a[0])):
        count = max(1, round(length / 1.0))
        for k in range(count):
            x = length * (k + .5) / count
            s.box((x, 0, GUARD / 2), (.09, .09, GUARD), s.c(colour, .04))
            if feet:
                s.box((x, feet * .19, .012), (.34, .48, .024), '#5e666a')
        s.box((length / 2, 0, GUARD + .019), (length, .11, .038), s.c(colour, .04))
        for z in (.72, .44):
            s.box((length / 2, 0, z), (length, .03, .14), s.c(colour, .05))
        s.box((length / 2, 0, .085), (length, .04, .09), s.c(colour, .05))
        if road:
            s.box((length / 2, road * .018, .72), (length, .004, .05), '#f2c230')


def corner_post(s, x, y, base=DECK):
    s.box((x, y, base + GUARD / 2 + .02), (.1, .1, GUARD + .04), GUARD_TIMBER)


def object_marker(s, x, y, facing, low, base=DECK):
    """Yellow and black hazard marker on the corner, facing approaching traffic. Its
    stripes fall toward the side that vehicles pass on; low is that side's y sign."""
    slope = low * (1 if facing > 0 else -1)
    with s.at(x, y, base, yaw=0.0 if facing > 0 else math.pi):
        # mounted below the handrail, so the corner stays under 1.2 m above the street
        s.box((.03, 0, .5), (.05, .05, 1.0), '#5e666a')
        s.box((.062, 0, .53), (.012, .3, .92), '#f2c230')
        for k in range(4):
            centre = .24 + k * .17
            s.quad((.07, -.15, centre + slope * .15), (.07, .15, centre - slope * .15), (.07, .15, centre - slope * .15 + .085), (.07, -.15, centre + slope * .15 + .085), '#16181a')


def cafe_chair(s, colour, legs='#2b2e31'):
    """Chair facing local +x."""
    s.box((0, 0, .44), (.4, .4, .03), colour)
    s.box((-.19, 0, .66), (.03, .38, .34), colour)
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * .17, sy * .17, .215), (.03, .03, .43), legs)


def patio_umbrella(s, x, y, base, tones, radius=.95):
    """Free-standing on a weighted base; the canopy edge clears 2.1 m above the walking surface."""
    s.cyl((x, y, base), (x, y, base + .09), .25, '#3a3d40', sides=10)
    s.cyl((x, y, base + .09), (x, y, base + 2.58), .022, GALV, sides=6)
    rim, peak, sides = base + 2.13, base + 2.6, 8
    for k in range(sides):
        a0, a1 = k * math.tau / sides, (k + 1) * math.tau / sides
        s.tri((x, y, peak), (x + math.cos(a0) * radius, y + math.sin(a0) * radius, rim), (x + math.cos(a1) * radius, y + math.sin(a1) * radius, rim), tones[k % len(tones)])


def bistro_set(s, x, y, base, yaw=0.0, seats=4, chair='#2f6f8f', umbrella=None):
    with s.at(x, y, base, yaw=yaw):
        s.box((0, 0, .735), (.75, .75, .03), '#d9dde0')
        if not umbrella:
            s.cyl((0, 0, .02), (0, 0, .72), .03, '#2b2e31', sides=6)
            s.box((0, 0, .012), (.42, .42, .024), '#2b2e31')
        for k in range(seats):
            a = k * math.tau / seats
            with s.at(math.cos(a) * .62, math.sin(a) * .62, 0, yaw=a + math.pi):
                cafe_chair(s, chair)
    if umbrella:
        patio_umbrella(s, x, y, base, umbrella)


def box_planter(s, x, y, base, size=(.55, .55, .5), plant='shrub', colour='#3f4347'):
    w, d, h = size
    s.box((x, y, base + h / 2), (w, d, h), colour)
    s.box((x, y, base + h + .004), (w - .08, d - .08, .008), '#3d3027')
    greens = ['#4f7a3f', '#5d8a4a', '#456c38']
    if plant == 'conifer':
        s.cyl((x, y, base + h), (x, y, base + h + .45), min(w, d) * .36, s.pick(greens, .05), r1=.03, sides=8)
    elif plant == 'grass':
        for k in range(9):
            a, r = k * 2.399963, min(w, d) * .3 * math.sqrt((k + .5) / 9)
            foot = (x + math.cos(a) * r, y + math.sin(a) * r, base + h)
            tip = (foot[0] + math.cos(a) * .12, foot[1] + math.sin(a) * .12, base + h + .32 + s.random() * .12)
            s.tri((foot[0] - .03, foot[1], foot[2]), (foot[0] + .03, foot[1], foot[2]), tip, s.pick(['#8a9a52', '#a3ab5e', '#768a48'], .05))
            s.tri((foot[0], foot[1] - .03, foot[2]), (foot[0], foot[1] + .03, foot[2]), tip, s.pick(['#8a9a52', '#a3ab5e', '#768a48'], .05))
    else:
        s.dome((x, y, base + h), (w * .46, d * .46, .4), lambda j, i: s.pick(greens, .05), nu=8, nv=3, noise=.1)
        for k in range(6):
            a = k * 1.047 + .4
            s.dome((x + math.cos(a) * w * .3, y + math.sin(a) * d * .3, base + h + .26), (.05, .05, .04), s.pick(['#d4493f', '#e86aa0', '#f2c230'], .05), nu=6, nv=3, full=True)


def curbside_deck(s, length, returns=(False, False), marker=False, width=2.5, strip=True):
    """Platform in the parking lane with a guard on the road side. returns closes the -x and +x ends."""
    half, front, back = length / 2, -width / 2, width / 2
    deck(s, -half, half, front, back)
    if strip:
        s.box((0, back - .04, DECK + .003), (length, .08, .006), '#aab1b6')
    line = front + .07
    guard_run(s, (-half, line), (half, line), road=-1)
    for sign, closed in zip((-1, 1), returns):
        if not closed:
            continue
        x = sign * (half - .07)
        guard_run(s, (x, line), (x, back - .07), road=-sign)
        corner_post(s, x, line)
        corner_post(s, x, back - .07)
    if marker:
        object_marker(s, half - .09, line + .09, 1, -1)


def boardwalk_section(s):
    curbside_deck(s, 3.0)


# Boardwalk modules in feet: 6 ft wide, 9 ft or 12 ft long, with a guard on both long
# sides and open ends so they run on, and a 6 ft square corner for turning a run toward
# the sidewalk. The handrail's outer face sits on the deck edge, which keeps the footprint
# exact and the walkway as wide as the module allows.
FOOT = .3048
RAIL_RED = '#cf1f2b'
RAIL_BLACK = '#232527'
RAIL_TUBE = .05
DECK_GREY = ['#84817d', '#7c7975', '#8a8782', '#807d79']
DECK_METAL = '#b3b8bc'


def composite_deck(s, x0, x1, y0, y1, top=DECK, board=.14, trim=.03):
    """Grey decking on a metal frame at sidewalk grade. Boards run along the path of
    travel and stop at a metal edge strip at each end, which shows as a seam where two
    modules meet."""
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        s.quad((a[0], a[1], 0), (b[0], b[1], 0), (b[0], b[1], top), (a[0], a[1], top), DECK_METAL)
    for xa, xb in ((x0, x0 + trim), (x1 - trim, x1)):
        s.quad((xa, y0, top), (xb, y0, top), (xb, y1, top), (xa, y1, top), DECK_METAL)
    count = max(1, round((y1 - y0) / board))
    for k in range(count):
        ya, yb = y0 + (y1 - y0) * k / count, y0 + (y1 - y0) * (k + 1) / count
        s.quad((x0 + trim, ya, top), (x1 - trim, ya, top), (x1 - trim, yb, top), (x0 + trim, yb, top), s.pick(DECK_GREY, .02))


def steel_rail_bays(length):
    """Stile stations of a welded railing panel: one just inside each end, and enough
    between them that no bay is longer than six feet."""
    first, last = RAIL_TUBE / 2, length - RAIL_TUBE / 2
    bays = max(1, math.ceil((last - first) / (6 * FOOT) - 1e-6))
    return [first + (last - first) * k / bays for k in range(bays + 1)]


def steel_rail(s, a, b, base=DECK, colour=RAIL_RED):
    """Welded steel railing from a to b, red unless told otherwise: a square top rail, a square stile at each end
    and at most six feet apart, thin upright bars about a foot apart, and a solid kick
    band along the bottom that a cane can find. The top is 1.0 m above the deck."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    with s.at(a[0], a[1], base, yaw=math.atan2(b[1] - a[1], b[0] - a[0])):
        s.box((length / 2, 0, GUARD - RAIL_TUBE / 2), (length, RAIL_TUBE, RAIL_TUBE), colour)
        s.box((length / 2, 0, .08), (length, .02, .12), colour)
        stations = steel_rail_bays(length)
        for x in stations:
            s.box((x, 0, (GUARD - RAIL_TUBE) / 2), (RAIL_TUBE, RAIL_TUBE, GUARD - RAIL_TUBE), colour)
        for k in range(len(stations) - 1):
            x0, x1 = stations[k], stations[k + 1]
            gaps = max(1, round((x1 - x0) / FOOT))
            for j in range(1, gaps):
                s.box((x0 + (x1 - x0) * j / gaps, 0, (.14 + GUARD - RAIL_TUBE) / 2), (.016, .016, GUARD - RAIL_TUBE - .14), colour)


def curb_strip(s, x0, x1, y):
    """Metal threshold along the open sidewalk edge of a deck."""
    s.box(((x0 + x1) / 2, y - .05, DECK + .003), (x1 - x0, .1, .006), '#c3c8cc')


def rail_marker(s, x, y):
    """Yellow and black hazard marker on the outside of an end railing, facing vehicles
    that approach from +x. Its stripes fall toward the road at -y."""
    s.box((x - .005, y, .55), (.008, .3, .78), '#f2c230')
    for k in range(4):
        low = .2 + k * .19
        s.quad((x, y + .15, low + .15), (x, y - .15, low), (x, y - .15, low + .09), (x, y + .15, low + .24), '#16181a')


def boardwalk_module(s, length_ft, width_ft=6, both_sides=True, colour=RAIL_RED):
    """Road at -y. Open at both ends; a railing on the road side, and on the sidewalk side too
    unless that side is left open to the curb."""
    half, edge = length_ft * FOOT / 2, width_ft * FOOT / 2
    line = edge - RAIL_TUBE / 2
    composite_deck(s, -half, half, -edge, edge)
    steel_rail(s, (-half, -line), (half, -line), colour=colour)
    if both_sides:
        steel_rail(s, (-half, line), (half, line), colour=colour)
    else:
        curb_strip(s, -half + .03, half - .03, edge)


def boardwalk_module_nine_foot(s):
    boardwalk_module(s, 9)


def boardwalk_module_twelve_foot(s):
    boardwalk_module(s, 12)


def boardwalk_module_nine_foot_road_rail(s):
    boardwalk_module(s, 9, both_sides=False)


def boardwalk_module_twelve_foot_road_rail(s):
    boardwalk_module(s, 12, both_sides=False)


def boardwalk_corner_piece(s, marker=False, size_ft=6, colour=RAIL_RED):
    """Railings on the road side (-y) and across the outer end (+x); open toward the run (-x) and the sidewalk (+y)."""
    edge = size_ft * FOOT / 2
    line = edge - RAIL_TUBE / 2
    composite_deck(s, -edge, edge, -edge, edge)
    curb_strip(s, -edge + .03, edge - RAIL_TUBE - .01, edge)
    steel_rail(s, (-edge, -line), (edge, -line), colour=colour)
    steel_rail(s, (line, -edge + RAIL_TUBE), (line, edge), colour=colour)
    if marker:
        rail_marker(s, edge, -edge + .3)


def boardwalk_corner(s):
    boardwalk_corner_piece(s)


def boardwalk_corner_approach(s):
    boardwalk_corner_piece(s, marker=True)


def boardwalk_module_nine_foot_black(s):
    boardwalk_module(s, 9, colour=RAIL_BLACK)


def boardwalk_module_twelve_foot_black(s):
    boardwalk_module(s, 12, colour=RAIL_BLACK)


def boardwalk_corner_black(s):
    boardwalk_corner_piece(s, colour=RAIL_BLACK)


def boardwalk_corner_approach_black(s):
    boardwalk_corner_piece(s, marker=True, colour=RAIL_BLACK)


def boardwalk_module_nine_foot_road_rail_black(s):
    boardwalk_module(s, 9, both_sides=False, colour=RAIL_BLACK)


def boardwalk_module_twelve_foot_road_rail_black(s):
    boardwalk_module(s, 12, both_sides=False, colour=RAIL_BLACK)


def boardwalk_section_short(s):
    curbside_deck(s, 1.5)


def boardwalk_end_approach(s):
    curbside_deck(s, 3.0, returns=(False, True), marker=True)


def boardwalk_end_far(s):
    curbside_deck(s, 3.0, returns=(True, False))


def street_patio(s, length, tables, width=2.5):
    half, back = length / 2, width / 2
    curbside_deck(s, length, returns=(True, True), marker=True, width=width)
    # sidewalk side: a guard with a 2 m barrier-free opening in the middle
    line = back - .07
    guard_run(s, (-(half - .07), line), (-1.0, line))
    guard_run(s, (1.0, line), (half - .07, line))
    for sign in (-1, 1):
        corner_post(s, sign * 1.0, line)
        box_planter(s, sign * 1.38, back - .5, DECK, size=(.5, .5, .5), plant='conifer' if sign < 0 else 'shrub')
    stripes = (['#b5432a', '#f1e9d2'], ['#2f6f8f', '#f1e9d2'])
    for k, x in enumerate(tables):
        bistro_set(s, x, -.22, DECK, yaw=.785, umbrella=stripes[k % 2], chair='#2f6f8f' if k % 2 else '#b5432a')


def street_patio_one_stall(s):
    street_patio(s, 6.0, (-1.95, 1.95))


def street_patio_two_stall(s):
    street_patio(s, 11.0, (-4.3, -2.25, 2.25, 4.3))


def bench_run(s, x0, x1, y, base, facing=1, colour=None):
    """Built-in slatted bench along a guard; facing is the y direction the sitter looks."""
    colour = colour or TIMBER
    length = x1 - x0
    for k in range(4):
        s.box(((x0 + x1) / 2, y + facing * (.06 + k * .105), base + .45), (length, .09, .04), s.c(colour, .06))
    s.box(((x0 + x1) / 2, y + facing * .22, base + .21), (length - .1, .34, .42), '#6f5a44')
    for k in range(3):
        s.box(((x0 + x1) / 2, y - facing * .01, base + .62 + k * .13), (length, .03, .1), s.c(colour, .06))


def stool_table(s, x, y, base, stools=2, tone='#e0b63a'):
    s.cyl((x, y, base), (x, y, base + .02), .2, '#2b2e31', sides=10)
    s.cyl((x, y, base + .02), (x, y, base + .7), .025, '#2b2e31', sides=6)
    s.cyl((x, y, base + .7), (x, y, base + .73), .3, '#d9dde0', sides=12)
    for k in range(stools):
        a = k * math.tau / stools + .5
        sx, sy = x + math.cos(a) * .55, y + math.sin(a) * .55
        s.cyl((sx, sy, base), (sx, sy, base + .43), .16, tone, r1=.18, sides=10)


def parklet_one_stall(s):
    length, width = 6.0, 2.5
    half, front = length / 2, -width / 2
    curbside_deck(s, length, returns=(True, True), marker=True, width=width)
    inner = front + .14
    bench_run(s, -1.9, 1.9, inner, DECK)
    for sign in (-1, 1):
        box_planter(s, sign * 2.42, inner + .3, DECK, size=(.9, .6, .5), plant='grass' if sign < 0 else 'shrub')
    stool_table(s, -1.1, .25, DECK, tone='#e0b63a')
    stool_table(s, 1.2, .35, DECK, tone='#1f7a8c')
    patio_umbrella(s, 0, -.15, DECK, ['#e0b63a', '#f1e9d2'], radius=1.0)
    # a short bench along the far end
    with s.at(-(half - .16), .35, 0, yaw=math.pi / 2):
        bench_run(s, -.75, .75, 0, DECK, facing=-1)


def parklet_two_stall(s):
    length, width = 11.0, 2.5
    front = -width / 2
    curbside_deck(s, length, returns=(True, True), marker=True, width=width)
    inner = front + .14
    for x0, x1 in ((-4.6, -1.1), (1.1, 4.6)):
        bench_run(s, x0, x1, inner, DECK)
    for x, plant in ((-5.05, 'grass'), (0, 'shrub'), (5.05, 'conifer')):
        box_planter(s, x, inner + .3, DECK, size=(.8 if x else 1.6, .6, .5), plant=plant)
    # long shared table with two benches, across from the first bay
    s.box((-2.9, .35, DECK + .74), (2.4, .8, .05), s.c(TIMBER, .05))
    for x in (-3.9, -1.9):
        s.box((x, .35, DECK + .36), (.08, .7, .72), '#2b2e31')
    for sy in (-1, 1):
        s.box((-2.9, .35 + sy * .68, DECK + .44), (2.3, .3, .05), s.c(TIMBER, .06))
        for x in (-3.8, -2.0):
            s.box((x, .35 + sy * .68, DECK + .21), (.06, .26, .42), '#2b2e31')
    stool_table(s, 2.2, .3, DECK, stools=3, tone='#b5432a')
    stool_table(s, 3.9, .45, DECK, stools=2, tone='#1f7a8c')
    patio_umbrella(s, -2.9, .35, DECK, ['#1f7a8c', '#f1e9d2'], radius=.9)
    patio_umbrella(s, 3.0, .2, DECK, ['#b5432a', '#f1e9d2'], radius=1.0)


def sidewalk_patio(s):
    """On the sidewalk itself, open to the building at +y, with free-standing guards on weighted feet."""
    length, depth = 6.0, 2.2
    half, front = length / 2, -depth / 2
    gate = 1.5
    guard_run(s, (-half, front), (half - gate, front), base=0, feet=1)
    for sign in (-1, 1):
        guard_run(s, (sign * half, front), (sign * half, depth / 2), base=0, feet=sign)
        corner_post(s, sign * half, front, base=0)
    corner_post(s, half - gate, front, base=0)
    box_planter(s, half - gate - .45, front + .45, 0, size=(.5, .5, .5), plant='conifer')
    box_planter(s, half - .4, front + .45, 0, size=(.5, .5, .5), plant='shrub')
    stripes = (['#b5432a', '#f1e9d2'], ['#2f6f8f', '#f1e9d2'])
    for k, x in enumerate((-2.05, -.05)):
        bistro_set(s, x, .1, 0, yaw=.785, umbrella=stripes[k], chair='#b5432a' if k == 0 else '#2f6f8f')
    bistro_set(s, 1.9, .45, 0, yaw=0, seats=2, chair='#2f6f8f')


def patio_fence_panel(s):
    guard_run(s, (-1.2, 0), (1.2, 0), base=0, feet=1)


# The low-profile barrier is 3.0 m long, 0.6 m wide and 0.5 m tall: a short vertical toe, a
# sloped face on each side and a narrow rounded top. The sloped face is exactly half the
# height of a road barrier's painted face, so the same murals fit it at half scale.
LOW_HALF, LOW_TOE, LOW_RUN = .3, .09, .165
LOW_FACE = MURAL_HEIGHT / 2
LOW_RISE = math.sqrt(LOW_FACE ** 2 - LOW_RUN ** 2)
LOW_SHOULDER = (LOW_HALF - LOW_RUN, LOW_TOE + LOW_RISE)
LOW_TOP = (.09, .5)


def low_profile_point(u, v, side, proud):
    """Map (u, v) metres onto one sloped face. Each side reads left to right when faced."""
    t = v / LOW_FACE
    return ((MURAL_LENGTH / 2 - u) * side, side * (LOW_HALF - LOW_RUN * t + LOW_RISE / LOW_FACE * proud), LOW_TOE + LOW_RISE * t + LOW_RUN / LOW_FACE * proud)


def low_profile_body(s, faces=True):
    """Ends, toe, shoulders, top, underside and lifting slots; the two sloped faces too unless a mural replaces them."""
    half = MURAL_LENGTH / 2
    (sy, sz), (ty, tz) = LOW_SHOULDER, LOW_TOP
    profile = [(-LOW_HALF, 0), (LOW_HALF, 0), (LOW_HALF, LOW_TOE), (sy, sz), (ty, tz), (-ty, tz), (-sy, sz), (-LOW_HALF, LOW_TOE)]
    for sx in (-1, 1):
        s.poly([(sx * half, y, z) for y, z in profile], BARRIER_CONCRETE)
    for side in (-1, 1):
        s.quad((-half, side * LOW_HALF, 0), (half, side * LOW_HALF, 0), (half, side * LOW_HALF, LOW_TOE), (-half, side * LOW_HALF, LOW_TOE), '#a5a29a')
        s.quad((-half, side * sy, sz), (half, side * sy, sz), (half, side * ty, tz), (-half, side * ty, tz), '#c4c1b9')
        if faces:
            s.quad((-half, side * LOW_HALF, LOW_TOE), (half, side * LOW_HALF, LOW_TOE), (half, side * sy, sz), (-half, side * sy, sz), BARRIER_CONCRETE)
    s.quad((-half, -ty, tz), (half, -ty, tz), (half, ty, tz), (-half, ty, tz), '#c9c6be')
    s.quad((-half, -LOW_HALF, 0), (half, -LOW_HALF, 0), (half, LOW_HALF, 0), (-half, LOW_HALF, 0), BARRIER_CONCRETE)
    for x in (-.9, .9):
        s.box((x, 0, .035), (.3, .62, .07), '#55524c')


def low_profile_barrier(s):
    low_profile_body(s)


def low_profile_mural(s, design, repeats):
    """A road-barrier mural on the low-profile barrier's sloped faces. repeats is 1 to stretch
    one scene along the 3 m, or 2 to show a pattern twice at true proportions."""
    s.low_profile = repeats
    design(s)


def low_profile_mural_foothills(s):
    low_profile_mural(s, mural_foothills, 1)


def low_profile_mural_chinook(s):
    low_profile_mural(s, mural_chinook, 1)


def low_profile_mural_river(s):
    low_profile_mural(s, mural_river, 1)


def low_profile_mural_mosaic(s):
    low_profile_mural(s, mural_mosaic, 2)


def low_profile_mural_chevron(s):
    low_profile_mural(s, mural_chevron, 2)


def low_profile_mural_quilt(s):
    low_profile_mural(s, mural_quilt, 2)


def low_profile_mural_aspen(s):
    low_profile_mural(s, mural_aspen, 2)


def low_profile_mural_confetti(s):
    low_profile_mural(s, mural_confetti, 2)


# ---------------------------------------------------------------------------
# Planters that stand between a patio and the road. Black planters filled with
# summer annuals; with their plants they stay under 1.2 m above the street.
# ---------------------------------------------------------------------------
PLANTER_BLACK = '#1f2123'
PLANTER_TRIM = '#2c2f32'
BLOOMS_PINK = ['#e8559a', '#f07ab0', '#d93d87', '#c22a9a', '#f4a3c4', '#d4303a']
BLOOMS_PURPLE = ['#7b3fc4', '#9a5cd6', '#5e2ea6', '#f1eef5', '#c9a6ea', '#e8559a']
BLOOMS_MIXED = ['#c22a9a', '#d4303a', '#e8559a', '#7b3fc4', '#f07ab0', '#d93d87']
VINE_LIME = ['#b9d63a', '#a6c930', '#c8e04e']
ANNUAL_GREENS = ['#4f7a3f', '#5d8a4a', '#456c38']


def halton(index, base):
    value, fraction = 0.0, 1.0
    while index > 0:
        fraction /= base
        value += fraction * (index % base)
        index //= base
    return value


def annuals(s, length, width, z, blooms, count, trailing):
    """A planter overflowing with summer annuals above soil at height z: leafy mounds that
    spread a little past the rim, a dense scatter of blooms lying on them, and lime vine
    trailing down the sides at the listed (x, side) spots."""
    mounds = []
    for k in range(max(2, round(length / .4))):
        span = length / max(2, round(length / .4))
        mound = (-length / 2 + span * (k + .5), (s.random() - .5) * .05, span * .74, width * .6, .27 + s.random() * .07)
        mounds.append(mound)
        s.dome((mound[0], mound[1], z - .02), mound[2:], lambda j, i: s.pick(ANNUAL_GREENS, .06), nu=9, nv=3, noise=.1)

    def surface(x, y):
        return max(rz * math.sqrt(max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2)) for cx, cy, rx, ry, rz in mounds)

    for k in range(count):
        x = (halton(k + 1, 2) - .5) * (length + .04)
        y = (halton(k + 1, 3) - .5) * width * 1.02
        lift = surface(x, y)
        if lift < .05:
            continue
        size = .05 + s.random() * .022
        s.dome((x, y, z - .012 + lift), (size, size, size * .62), s.pick(blooms, .05), nu=5, nv=2, full=True)
    for x, side in trailing:
        y = side * width / 2
        s.dome((x, y - side * .02, z - .02), (.15, .11, .1), lambda j, i: s.pick(VINE_LIME, .06), nu=7, nv=2, noise=.14)
        for n in range(4):
            s.dome((x + (s.random() - .5) * .13, y + side * (.05 + .01 * n), z - .06 - .075 * n), (.12 - .02 * n, .045, .08 - .01 * n),
                   s.pick(VINE_LIME, .07), nu=6, nv=2, noise=.2, full=True)


def barrier_planter(s, blooms):
    """Black moulded planter, 4 ft by 2 ft, wider at the rim than the base. It stands on three
    feet a side, which leaves forklift pockets, and carries red and white reflective tape on
    each end."""
    length, width, height, foot = 1.22, .61, .62, .1
    base_l, base_w, rim = length - .1, width - .1, .05

    def ring(z, l, w):
        return [(-l / 2, -w / 2, z), (l / 2, -w / 2, z), (l / 2, w / 2, z), (-l / 2, w / 2, z)]

    s.loft([ring(foot, base_l, base_w), ring(height - rim, length - .02, width - .02)], PLANTER_BLACK, cap_start=True, cap_end=False)
    s.box((0, 0, height - rim / 2), (length, width, rim), PLANTER_TRIM)
    for x in (-(base_l / 2 - .09), 0, base_l / 2 - .09):
        s.box((x, 0, foot / 2), (.18, base_w, foot), PLANTER_BLACK)
    s.quad((-length / 2 + .04, -width / 2 + .04, height + .002), (length / 2 - .04, -width / 2 + .04, height + .002),
           (length / 2 - .04, width / 2 - .04, height + .002), (-length / 2 + .04, width / 2 - .04, height + .002), '#3d3027')

    def end(sx, across, z):
        """A point on a tapered end face, 3 mm proud; across runs -1 to 1 over its width."""
        t = (z - foot) / (height - rim - foot)
        return (sx * (base_l / 2 + (length - .02 - base_l) / 2 * t + .003), across * (base_w / 2 + (width - .02 - base_w) / 2 * t), z)

    for sx in (-1, 1):
        for a0, a1, z0, z1, tone in ((-.92, -.3, .43, .5, '#f1f0ea'), (-.3, .3, .43, .5, '#c8202c'), (.3, .92, .43, .5, '#f1f0ea'), (-.92, .92, .27, .33, '#c8202c')):
            s.quad(end(sx, a0, z0), end(sx, a1, z0), end(sx, a1, z1), end(sx, a0, z1), tone)
    annuals(s, length - .1, width - .08, height, blooms, 110, [(-.36, -1), (.3, -1), (.42, 1), (-.22, 1)])


def barrier_planter_pink(s):
    barrier_planter(s, BLOOMS_PINK)


def barrier_planter_purple(s):
    barrier_planter(s, BLOOMS_PURPLE)


def long_planter(s):
    """Black panelled planter box, 6 ft by 2 ft, on four low feet."""
    length, width, height, gap = 1.83, .61, .6, .04
    body_l, body_w = length - .03, width - .03
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * (length / 2 - .13), sy * (width / 2 - .1), gap / 2), (.14, .1, gap), '#0f1011')
    s.box((0, 0, gap + (height - gap) / 2), (body_l, body_w, height - gap), PLANTER_BLACK)
    s.box((0, 0, height - .03), (length, width, .06), PLANTER_TRIM)
    low, high = gap + .03, height - .09
    for sy in (-1, 1):
        y = sy * body_w / 2
        for z in (low + .035, high - .035):
            s.box((0, y, z), (body_l - .04, .014, .07), PLANTER_TRIM)
        for sx in (-1, 1):
            s.box((sx * (body_l / 2 - .065), y, (low + high) / 2), (.09, .014, high - low), PLANTER_TRIM)
        s.box((0, y, (low + high) / 2), (body_l - .5, .009, high - low - .28), PLANTER_TRIM)
    for sx in (-1, 1):
        x = sx * body_l / 2
        for z in (low + .035, high - .035):
            s.box((x, 0, z), (.014, body_w - .04, .07), PLANTER_TRIM)
        for sy in (-1, 1):
            s.box((x, sy * (body_w / 2 - .065), (low + high) / 2), (.014, .09, high - low), PLANTER_TRIM)
    s.quad((-length / 2 + .05, -width / 2 + .05, height + .002), (length / 2 - .05, -width / 2 + .05, height + .002),
           (length / 2 - .05, width / 2 - .05, height + .002), (-length / 2 + .05, width / 2 - .05, height + .002), '#3d3027')
    annuals(s, length - .12, width - .08, height, BLOOMS_MIXED, 160, [(-.62, -1), (-.1, -1), (.55, -1), (.2, 1), (-.45, 1), (.72, 1)])


# ---------------------------------------------------------------------------
# River and city edge.
# ---------------------------------------------------------------------------
def open_hull(s, rings, tones, split):
    """Loft closed thin-shell sections so a boat stays open on top. Each ring lists the
    outer skin, then the inner skin back again; `split` is the outer point count."""
    outer, inner, trim = tones

    def tone(r, i):
        if i == split - 1 or i == 2 * split - 1:
            return trim
        return outer if i < split else inner

    s.loft(rings, tone, cap_start=False, cap_end=False)


def paddle(s, a, b, blade='#e0b63a', shaft='#2b2e31'):
    s.cyl(a, b, .016, shaft, sides=5)
    tip = add(b, mul(norm(sub(b, a)), .42))
    s.ribbon(b, tip, .17, blade, normal=(0.0, 0.0, 1.0))
    s.cyl(sub(a, (0, 0, .0)), add(a, mul(norm(sub(a, b)), .001)), .03, shaft, sides=5)


def canoe(s):
    red, tan, wood, half = '#b23a34', '#d8c39a', '#8a6a4a', 2.45

    def draw():
        rings = []
        for k in range(11):
            t = -1 + 2 * k / 10
            beam = .44 * (1 - abs(t) ** 2.4) ** .55 + .012
            keel, sheer, skin = .16 * abs(t) ** 3.5, .34 + .2 * abs(t) ** 3, .022
            outer = [(beam * math.cos(math.pi + math.pi * j / 6), t * half, sheer + (sheer - keel) * math.sin(math.pi + math.pi * j / 6)) for j in range(7)]
            inner = [((beam - skin) * math.cos(math.pi + math.pi * j / 6) if beam > skin * 1.5 else outer[j][0] * .5, t * half,
                      sheer + (sheer - keel - skin) * math.sin(math.pi + math.pi * j / 6)) for j in range(7)]
            rings.append(outer + list(reversed(inner)))
        with s.at(pitch=.2):
            open_hull(s, rings, (red, tan, wood), 7)
            s.box((0, 0, .33), (.84, .07, .03), wood)
            for y, w in ((-1.45, .56), (1.6, .42)):
                s.box((0, y, .25), (w, .26, .03), '#d9c79a')
                s.box((0, y - .14, .26), (w + .08, .03, .03), wood)
                s.box((0, y + .14, .26), (w + .08, .03, .03), wood)
            paddle(s, (-.12, -.9, .16), (.1, .35, .14))

    rest_on_ground(s, draw)


def inflatable_raft(s):
    blue, grey = '#2a66a8', '#7b8387'
    ring = [(x, y, .2475 + .24 * max(0.0, (abs(y) - 1.15) / .75) ** 2) for x, y in rounded_rect(1.42, 3.75, .62, 4)]
    s.tube(ring + [ring[0]], .25, blue, sides=8)
    for x, y, z in ring[::2]:
        s.dome((x, y, z), (.25, .25, .25), blue, nu=8, nv=4, full=True)
    s.prism(rounded_rect(1.3, 3.5, .55, 4), .05, .09, grey)
    for y in (-.78, .78):
        s.cyl((-.62, y, .3), (.62, y, .3), .19, grey, sides=8)
    for sy in (-1, 1):
        for sx in (-1, 1):
            s.box((sx * .96, sy * .9, .34), (.03, .16, .05), ORANGE)
    s.box((0, 0, .3), (.46, .68, .4), '#f4f1e4')
    s.box((0, 0, .52), (.48, .7, .05), RED)
    paddle(s, (-.5, -1.55, .5), (.45, -.4, .5))
    paddle(s, (.5, 1.5, .5), (-.4, .35, .5), blade='#e0b63a')
    paddle(s, (.3, -1.2, .52), (.55, .2, .5), blade=ORANGE)


def drift_boat(s):
    teal, tan, wood = '#2f6f8f', '#c9a877', '#8a6a4a'
    rings, skin = [], .03
    for k in range(11):
        t = -1 + 2 * k / 10
        shape = (1 - abs(t) ** 2.2) ** .6
        top = .95 * shape + .02 if t < 0 else .34 + .61 * shape
        y = t * (2.45 if t < 0 else 2.25)
        keel = (.36 if t < 0 else .3) * abs(t) ** 2.2
        sheer = keel + .56 + .16 * t * t
        bottom = top * .62
        rings.append([(-top, y, sheer), (-bottom, y, keel), (bottom, y, keel), (top, y, sheer),
                      (max(top - skin, .004), y, sheer), (max(bottom - skin, .004), y, keel + skin), (-max(bottom - skin, .004), y, keel + skin), (-max(top - skin, .004), y, sheer)])
    open_hull(s, rings, (teal, tan, wood), 4)
    stern = rings[-1]
    s.quad(stern[0], stern[1], stern[2], stern[3], teal)
    for y, w, z in ((.1, 1.2, .4), (-1.15, .9, .52), (1.45, .74, .56)):
        s.box((0, y, z), (w, .28, .04), wood)
        s.box((0, y, z / 2 + .02), (.3, .2, z - .06), tan)
    for sx in (-1, 1):
        lock = (sx * .95, .2, .64)
        s.cyl(lock, (lock[0], lock[1], lock[2] + .1), .02, GALV, sides=5)
        handle, blade = (sx * .22, .32, .78), (sx * 2.15, .95, .36)
        s.cyl(handle, blade, .022, s.c(wood, .05), sides=5)
        s.ribbon(mix(handle, blade, .8), blade, .15, '#e9e6da', normal=(0.0, 1.0, 0.0))


def pumpjack(s):
    green, dark = '#3f6b55', '#2b2e31'
    for sx in (-1, 1):
        s.box((sx * .55, .6, .14), (.22, 8.4, .28), dark)
    for y in (-3.2, -1.2, .8, 2.8, 4.5):
        s.box((0, y, .2), (1.6, .18, .16), dark)
    # Samson post and saddle bearing
    for sx in (-1, 1):
        for y in (-1.9, .7):
            s.cyl((sx * .65, y, .28), (sx * .12, -.6, 4.3), .09, green, sides=6)
        s.cyl((sx * .5, -1.4, 1.2), (sx * .5, .3, 1.2), .04, green, sides=4)
    s.box((0, -.6, 4.38), (.6, .5, .28), dark)
    # walking beam, horsehead and bridle down to the wellhead
    front, rear = (0, -3.55, 4.02), (0, 2.45, 5.09)
    beam_yz(s, front, rear, .3, .5, green)
    wedge_body(s, .34, [(-3.45, 4.45), (-4.1, 4.72), (-4.48, 4.2), (-4.55, 3.4), (-4.3, 2.75), (-3.75, 3.0), (-3.45, 3.6)], green)
    s.box((0, -4.56, 3.7), (.36, .02, 1.5), YELLOW)
    for sx in (-1, 1):
        s.cyl((sx * .09, -4.56, 3.1), (sx * .09, -4.56, 1.75), .012, GALV, sides=3)
    s.box((0, -4.56, 1.72), (.3, .08, .08), dark)
    s.cyl((0, -4.56, 1.7), (0, -4.56, 1.0), .018, '#d9dde0', sides=5)
    s.cyl((0, -4.56, 0), (0, -4.56, .5), .14, dark, sides=10)
    s.cyl((0, -4.56, .5), (0, -4.56, 1.0), .08, '#c2332b', sides=8)
    s.cyl((0, -4.56, .62), (.9, -4.56, .62), .06, dark, sides=6)
    s.box((.5, -4.56, .62), (.16, .16, .22), '#c2332b')
    # gearbox, cranks with counterweights, pitman arms and motor
    centre_y, centre_z = 2.3, 1.55
    s.box((0, centre_y, 1.2), (1.0, 1.25, 1.1), green)
    s.cyl((-.82, centre_y, centre_z), (.82, centre_y, centre_z), .09, dark, sides=8)
    s.cyl((-.78, 2.42, 5.08), (.78, 2.42, 5.08), .07, dark, sides=6)
    for sx in (-1, 1):
        x = sx * .78
        beam_yz(s, (x, centre_y - .12, centre_z + .16), (x, centre_y + .78, centre_z - 1.04), .14, .42, dark)
        s.box((x, centre_y + .72, centre_z - .96), (.22, .86, .6), '#5e666a', yaw=0)
        pin = (x, centre_y + .42, centre_z - .56)
        s.cyl(pin, (x, 2.42, 5.08), .05, green, sides=5)
    s.box((0, 4.2, .58), (.5, .75, .5), dark)
    s.box((.72, 3.3, 1.0), (.12, 2.0, .9), YELLOW)


def grain_bin(s, x, y, radius, wall, sides=20):
    steel, seam = '#b9c0c4', '#98a1a6'
    with s.at(x, y, 0):
        s.cyl((0, 0, 0), (0, 0, .15), radius + .3, CONCRETE, sides=sides)
        bands = round(wall / .7)
        for k in range(bands):
            z0, z1 = .15 + wall * k / bands, .15 + wall * (k + 1) / bands
            s.cyl((0, 0, z0), (0, 0, z1), radius, s.c(steel, .03), sides=sides, cap0=False, cap1=False)
            s.cyl((0, 0, z1 - .04), (0, 0, z1), radius + .02, seam, sides=sides, cap0=False, cap1=False)
        eave = .15 + wall
        s.cyl((0, 0, eave), (0, 0, eave + radius * .5), radius + .1, '#c9cfd3', r1=.4, sides=sides, cap0=False, cap1=False)
        s.cyl((0, 0, eave + radius * .5), (0, 0, eave + radius * .5 + .3), .4, seam, r1=.28, sides=10)
        s.box((0, -radius - .012, 1.15), (.72, .04, 1.4), seam)
        s.box((.22, -radius - .04, 1.15), (.06, .03, .16), '#3a3d40')
        # caged ladder up the wall and across the roof
        for dx in (-.2, .2):
            s.cyl((radius * .82 + dx * .55, -radius * .6 + dx * .75, .3), (radius * .82 + dx * .55, -radius * .6 + dx * .75, eave + .2), .02, seam, sides=4)
        for k in range(int((eave - .3) / .35)):
            z = .5 + k * .35
            s.cyl((radius * .82 - .11, -radius * .6 - .15, z), (radius * .82 + .11, -radius * .6 + .15, z), .012, seam, sides=3)
        s.ribbon((radius * .8, -radius * .58, eave + .06), (.3, -.22, eave + radius * .5 + .05), .34, seam)
        for a in (1.2, 3.4):
            s.box((math.cos(a) * radius * .55, math.sin(a) * radius * .55, eave + radius * .26), (.3, .3, .2), seam)


def grain_bins(s):
    grain_bin(s, -3.2, .3, 2.75, 5.6)
    grain_bin(s, 2.9, -.2, 2.2, 4.2, sides=18)


def wind_turbine(s):
    white, grey, hub = '#d3dadf', '#aab3b9', 60.0  # a shade off white so it reads on the pale picker card
    s.cyl((0, 0, 0), (0, 0, .5), 5.0, CONCRETE, sides=16)
    for z0, z1, r0, r1 in ((.5, 20, 2.0, 1.72), (20, 40, 1.72, 1.44), (40, hub - 1.5, 1.44, 1.18)):
        s.cyl((0, 0, z0), (0, 0, z1), r0, s.c(white, .015), r1=r1, sides=14, cap0=False, cap1=False)
        s.cyl((0, 0, z1 - .12), (0, 0, z1), r1 + .05, grey, sides=14, cap0=False, cap1=False)
    s.box((0, -1.99, 1.6), (.9, .08, 2.1), grey)
    s.box((0, -2.5, .56), (1.4, 1.0, .12), '#8f979b')
    shell(s, [(-2.9, .68, .8), (-2.1, 1, 1), (4.6, 1, 1), (6.1, .8, .86)], 3.4, 3.4, hub - 1.7, white, radius=.9)
    s.box((0, 4.2, hub + 1.85), (.6, 1.2, .3), grey)
    with s.at(0, -2.9, hub, roll=math.pi / 2):
        s.dome((0, 0, 0), (1.55, 1.55, 2.3), white, nu=12, nv=4)
    for angle in (20, 140, 260):
        with s.at(0, -3.9, hub, pitch=math.radians(angle)):
            rings = []
            for z, chord, thick in ((.9, 1.5, 1.3), (5.0, 2.9, .75), (14.0, 1.75, .4), (22.0, 1.0, .2), (26.0, .32, .08)):
                rings.append([(-.3 * chord, 0, z), (0, thick / 2, z), (.7 * chord, 0, z), (0, -thick / 2, z)])
            s.loft(rings, white)


# ---------------------------------------------------------------------------
# Street and yard basics.
# ---------------------------------------------------------------------------
def street_light(s):
    steel, dark = '#9aa3a8', '#7b8387'
    s.cyl((0, 0, 0), (0, 0, .12), .28, CONCRETE, sides=12)
    s.cyl((0, 0, .12), (0, 0, .18), .2, dark, sides=8)
    s.cyl((0, 0, .18), (0, 0, 8.4), .11, steel, r1=.065, sides=8)
    s.box((0, -.107, .9), (.1, .012, .22), dark)
    s.tube([(0, 0, 8.4), (0, -.12, 8.75), (0, -.5, 9.0), (0, -1.2, 9.1), (0, -2.0, 9.08)], .05, steel, sides=6)
    s.box((0, -2.32, 9.06), (.32, .78, .09), dark)
    s.box((0, -2.32, 9.008), (.26, .62, .012), '#f4f1e4', gloss=True)


def basket_lamp_post(s):
    black = '#1d1f22'
    s.cyl((0, 0, 0), (0, 0, .1), .26, black, sides=10)
    s.cyl((0, 0, .1), (0, 0, .75), .16, black, r1=.1, sides=10)
    s.cyl((0, 0, .75), (0, 0, .82), .13, black, sides=10)
    s.cyl((0, 0, .82), (0, 0, 3.6), .07, black, r1=.055, sides=8)
    s.cyl((0, 0, 3.6), (0, 0, 3.72), .11, black, sides=8)
    s.dome((0, 0, 3.98), (.2, .2, .3), '#f4ecd2', nu=10, nv=5, full=True)
    s.cyl((0, 0, 4.24), (0, 0, 4.42), .13, black, r1=.02, sides=8)
    blooms = ['#d4493f', '#e86aa0', '#8a4fc2', '#f2c230', '#f4f1e4']
    for sx in (-1, 1):
        s.tube([(0, 0, 2.75), (sx * .3, 0, 2.95), (sx * .62, 0, 2.98), (sx * .72, 0, 2.9)], .018, black, sides=5)
        s.tube([(0, 0, 2.55), (sx * .35, 0, 2.6), (sx * .6, 0, 2.8)], .012, black, sides=4)
        cx, rim = sx * .72, 2.5
        for k in range(3):
            a = k * math.tau / 3 + .3
            s.cyl((cx, 0, 2.9), (cx + math.cos(a) * .2, math.sin(a) * .2, rim), .004, black, sides=3, cap0=False, cap1=False)
        with s.at(cx, 0, rim, pitch=math.pi):
            s.dome((0, 0, 0), (.21, .21, .18), '#5a4636', nu=10, nv=3)
        s.dome((cx, 0, rim), (.27, .27, .2), lambda j, i: s.pick(['#4f7a3f', '#5d8a4a', '#456c38'], .05), nu=10, nv=3, noise=.12)
        for k in range(18):
            a, r = k * 2.399963, .08 + .22 * ((k * 7) % 10) / 10
            trailing = .26 if k % 3 == 0 else 0.0
            s.dome((cx + math.cos(a) * r, math.sin(a) * r, rim + .17 - r * .45 - trailing), (.055, .055, .045), s.pick(blooms, .06), nu=6, nv=3, full=True)


def flagpole(s):
    alu, cloth = '#c9cdd0', '#1f7a8c'
    s.box((0, 0, .04), (.9, .9, .08), CONCRETE)
    s.cyl((0, 0, .08), (0, 0, .3), .12, alu, sides=10)
    s.cyl((0, 0, .3), (0, 0, 9.0), .075, alu, r1=.04, sides=10)
    s.dome((0, 0, 9.06), (.07, .07, .07), '#d6b24a', nu=8, nv=4, full=True)
    s.cyl((.085, 0, 1.2), (.05, 0, 8.9), .004, WHITE, sides=3)
    s.box((.09, 0, 1.2), (.03, .02, .1), alu)
    steps, top = 8, 8.86
    for k in range(steps):
        x0, x1 = .05 + 1.8 * k / steps, .05 + 1.8 * (k + 1) / steps
        y0, y1 = .13 * math.sin(k * 1.05) * k / steps, .13 * math.sin((k + 1) * 1.05) * (k + 1) / steps
        d0, d1 = .28 * (k / steps) ** 2, .28 * ((k + 1) / steps) ** 2
        s.quad((x0, y0, top - d0 - .9), (x1, y1, top - d1 - .9), (x1, y1, top - d1), (x0, y0, top - d0), s.c(cloth, .05))


def lane_garage(s):
    length, width, wall, ridge, base = 6.7, 6.7, 2.6, 4.25, .1
    s.box((0, 0, base / 2), (length + .2, width + .2, base), CONCRETE)
    s.box((0, -width / 2 - .9, .04), (5.5, 1.7, .08), '#b9b6ae')
    gable_house(s, length, width, wall, ridge, '#b8b2a4', 12, '#4a4d50', overhang=.4, courses=8, trim=WHITE, base=base)
    framed_opening(s, 'S', length, width, 0, base + .02, 4.9, 2.15, '#eceae0', trim=WHITE, bar=.1)
    for k in range(1, 4):
        wall_panel(s, 'S', length, width, 0, base + .02 + k * .54, 4.9, .02, '#b9b6ae', proud=.022)
    for k in range(4):
        wall_panel(s, 'S', length, width, -1.8 + k * 1.2, base + 1.74, .8, .3, GLASS_DARK, proud=.024, gloss=True)
    wall_panel(s, 'S', length, width, 0, base + 2.32, .22, .12, '#2b2e31', proud=.08)
    framed_opening(s, 'E', length, width, -1.9, base + .02, .9, 2.03, '#6f7a80', trim=WHITE)
    wall_panel(s, 'E', length, width, -1.58, base + 1.0, .05, .14, '#2b2e31', proud=.05)
    framed_opening(s, 'W', length, width, .3, base + 1.25, 1.2, .9, GLASS_DARK, trim=WHITE, gloss=True, mullion=True)
    s.box((0, -width / 2 - .42, base + wall - .14), (length + .7, .1, .1), WHITE)
    s.cyl((length / 2 + .08, -width / 2 - .08, base + wall - .2), (length / 2 + .08, -width / 2 - .08, .2), .04, WHITE, sides=5)


def carport(s):
    length, depth, steel = 6.0, 5.2, '#3a3d40'
    s.box((0, 0, .02), (length + .3, depth + .6, .04), '#b9b6ae')
    for x in (-length / 2 + .1, 0, length / 2 - .1):
        for y, h in ((-depth / 2, 2.72), (depth / 2, 2.42)):
            s.box((x, y, .05), (.3, .3, .1), CONCRETE)
            s.box((x, y, h / 2), (.13, .13, h), steel)
    for y, z in ((-depth / 2, 2.66), (depth / 2, 2.36)):
        s.box((0, y, z), (length, .1, .2), steel)
    for k in range(7):
        x = -length / 2 + .1 + k * (length - .2) / 6
        s.cyl((x, -depth / 2 - .35, 2.84), (x, depth / 2 + .35, 2.5), .045, steel, sides=4)
    roof_slab(s, (-length / 2 - .2, -depth / 2 - .5, 2.9), (length / 2 + .2, -depth / 2 - .5, 2.9), (length / 2 + .2, depth / 2 + .5, 2.55),
              (-length / 2 - .2, depth / 2 + .5, 2.55), .05, '#8f979b', 7, underside='#d3d7da', jitter=.03)
    for k in range(9):
        s.box((0, depth / 2, .28 + k * .17), (length - .2, .03, .12), s.pick(CEDAR, .05))


def solar_array(s):
    cols, rows, panel_w, panel_h, gap, low, tilt = 8, 2, 1.05, 1.75, .025, .8, math.radians(30)
    width, slope = cols * (panel_w + gap), rows * (panel_h + gap)
    y0 = -slope * math.cos(tilt) / 2
    alu, cell = '#c9cdd0', '#1c2f4a'
    with s.at(0, y0, low, roll=tilt):
        s.box((0, slope / 2, 0), (width + .04, slope + .04, .03), alu)
        for c in range(cols):
            for r in range(rows):
                x, y = -width / 2 + (c + .5) * (panel_w + gap), (r + .5) * (panel_h + gap)
                s.box((x, y, .035), (panel_w, panel_h, .04), cell, gloss=True)
                s.box((x, y, .058), (panel_w, .012, .008), '#4a5f7d')
        for d in (slope * .2, slope * .8):
            s.box((0, d, -.06), (width, .08, .1), '#8f979b')
    for k in range(4):
        x = -width / 2 + width * (k + .5) / 4
        front = (x, y0 + slope * .2 * math.cos(tilt), low + slope * .2 * math.sin(tilt) - .1)
        back = (x, y0 + slope * .8 * math.cos(tilt), low + slope * .8 * math.sin(tilt) - .1)
        for foot in (front, back):
            s.box((foot[0], foot[1], foot[2] / 2), (.1, .1, foot[2]), '#8f979b')
            s.box((foot[0], foot[1], .03), (.28, .28, .06), CONCRETE)
        s.cyl((x, front[1], .2), back, .025, '#8f979b', sides=4)


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
# Wildlife and ranch animals, round two. Same method as the first four: forms
# lofted along a spine, modelled nose toward +x, then turned to face -y.
# ---------------------------------------------------------------------------
def crest_points(stations):
    """Top-of-back point of each spine station, where a mane or ridge sits."""
    out = []
    for i, (x, z, _hw, hh) in enumerate(stations):
        a, b = stations[max(0, i - 1)], stations[min(len(stations) - 1, i + 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        size = math.hypot(tx, tz) or 1.0
        out.append((x - tz / size * hh, 0.0, z + tx / size * hh))
    return out


def four_legs(s, front, hind, radii, colour, hoof, hoof_radius, lower=None):
    """front and hind are (hip, knee, fetlock) triples of (x, half-width, z), mirrored left and right."""
    for sy in (-1, 1):
        for hip, knee, fetlock in (front, hind):
            points = [(q[0], sy * q[1], q[2]) for q in (hip, knee, fetlock)]
            limb(s, points[:2], radii[:2], colour)
            limb(s, points[1:], radii[1:], lower or colour)
            s.cyl(points[2], (fetlock[0], sy * fetlock[1], 0), hoof_radius * .85, hoof, r1=hoof_radius, sides=6)


def horse(s, coat, points, grazing=False, blaze=False):
    body = [(-1.02, 1.3, .04, .05), (-.95, 1.3, .2, .24), (-.7, 1.28, .3, .33), (-.25, 1.2, .31, .34), (.25, 1.2, .3, .35), (.6, 1.25, .27, .33),
            (.8, 1.32, .2, .27), (.9, 1.38, .1, .15)]
    spine_loft(s, body, coat)
    if grazing:
        neck = [(.74, 1.36, .17, .25), (1.02, 1.2, .12, .17), (1.25, .88, .1, .13), (1.38, .58, .09, .11)]
        head = [(1.36, .56, .05, .06), (1.4, .48, .1, .11), (1.47, .32, .085, .1), (1.52, .16, .065, .075), (1.54, .07, .05, .05)]
    else:
        neck = [(.72, 1.4, .17, .26), (.93, 1.62, .13, .2), (1.07, 1.8, .105, .155), (1.15, 1.93, .09, .12)]
        head = [(1.07, 2.0, .05, .06), (1.15, 2.02, .1, .12), (1.31, 1.95, .09, .11), (1.49, 1.84, .07, .085), (1.62, 1.75, .055, .065), (1.68, 1.71, .04, .045)]
    spine_loft(s, neck, coat, cap_start=False)
    spine_loft(s, head, (lambda r, i: '#f1ede4' if blaze and r >= 1 and i in (1, 2) else coat))
    for x, _y, z in crest_points(neck):
        s.dome((x - .02, 0, z - .02), (.11, .035, .09), points, nu=6, nv=3, full=True)
    top = crest_points(head)[1]
    for sy in (-1, 1):
        s.dome((top[0] - .03, sy * .06, top[2] + .05), (.025, .03, .075), coat, nu=6, nv=3, full=True)
        s.dome((-.72, sy * .2, 1.25), (.28, .13, .3), coat, nu=8, nv=4, full=True)
        s.dome((.6, sy * .17, 1.2), (.2, .12, .28), coat, nu=8, nv=4, full=True)
    s.dome((head[-1][0], 0, head[-1][1]), (.045, .05, .04), points, nu=6, nv=3, full=True)
    limb(s, [(-1.0, 0, 1.36), (-1.13, 0, 1.12), (-1.15, 0, .55)], [.05, .075, .03], points)
    four_legs(s, ((.62, .16, 1.05), (.66, .14, .58), (.64, .14, .12)), ((-.8, .17, 1.1), (-.95, .15, .6), (-.86, .15, .12)), [.11, .055, .04], coat, '#211a16', .052, lower=points)


def horses(s):
    with s.at(-.75, .1, 0, yaw=-math.pi / 2 - .25, scale=.97):
        horse(s, '#7a4a2c', '#241c18', blaze=True)
    with s.at(.85, -.5, 0, yaw=math.pi * .62, scale=.93):
        horse(s, '#b79f7c', '#241c18', grazing=True)


def cow(s, coat, face, grazing=False):
    belly = face if face != coat else coat
    body = [(-1.0, 1.12, .05, .08), (-.94, 1.12, .24, .3), (-.65, 1.08, .34, .38), (-.15, 1.02, .37, .42), (.35, 1.02, .35, .42), (.68, 1.08, .3, .38),
            (.86, 1.12, .2, .3), (.94, 1.14, .1, .16)]
    spine_loft(s, body, (lambda r, i: belly if i in (5, 6) and 2 <= r <= 5 else coat))
    if grazing:
        neck = [(.8, 1.1, .2, .3), (1.02, .9, .15, .2), (1.16, .62, .13, .16)]
        head = [(1.14, .6, .06, .07), (1.18, .52, .14, .15), (1.24, .36, .12, .13), (1.3, .2, .1, .1), (1.32, .1, .085, .075)]
    else:
        neck = [(.8, 1.14, .2, .3), (1.0, 1.2, .15, .22), (1.12, 1.24, .13, .17)]
        head = [(1.06, 1.3, .06, .07), (1.14, 1.3, .14, .15), (1.3, 1.22, .12, .13), (1.46, 1.12, .1, .1), (1.54, 1.07, .085, .075)]
    spine_loft(s, neck, (lambda r, i: belly if i in (5, 6) else coat), cap_start=False)
    spine_loft(s, head, face)
    s.dome((head[-1][0], 0, head[-1][1]), (.07, .085, .06), '#d9a9a0', nu=6, nv=3, full=True)
    top = crest_points(head)[1]
    for sy in (-1, 1):
        s.dome((top[0] - .04, sy * .17, top[2] - .05), (.04, .09, .035), coat, nu=6, nv=3, full=True)
        s.dome((-.7, sy * .24, 1.05), (.3, .13, .32), coat, nu=8, nv=4, full=True)
        s.dome((.62, sy * .22, 1.0), (.22, .12, .3), coat, nu=8, nv=4, full=True)
    limb(s, [(-.98, 0, 1.3), (-1.07, 0, .9), (-1.06, 0, .5)], [.03, .025, .02], coat)
    s.dome((-1.06, 0, .42), (.04, .04, .1), '#2a211c', nu=6, nv=3, full=True)
    four_legs(s, ((.62, .2, .8), (.63, .18, .42), (.62, .18, .1)), ((-.78, .21, .82), (-.9, .19, .45), (-.84, .19, .1)), [.12, .07, .055], coat, '#211a16', .065,
              lower=face if face != coat else None)


def cattle(s):
    with s.at(-.9, .2, 0, yaw=-math.pi / 2 + .3):
        cow(s, '#7a3b22', '#f1ede4')
    with s.at(.95, -.45, 0, yaw=math.pi * .55, scale=.96):
        cow(s, '#1f1d1c', '#1f1d1c', grazing=True)


def coyote(s):
    coat, back, belly, legs, dark = '#9a8a72', '#6f6658', '#d9cdb8', '#a57a52', '#221d1a'
    with s.at(yaw=-math.pi / 2):
        body = [(-.42, .56, .02, .03), (-.38, .56, .08, .1), (-.25, .55, .11, .13), (0, .54, .115, .135), (.22, .56, .11, .14), (.34, .6, .085, .12), (.4, .64, .05, .08)]
        spine_loft(s, body, lambda r, i: back if i in (1, 2) else (belly if i in (5, 6) else coat))
        neck = [(.3, .62, .075, .1), (.4, .74, .06, .075), (.46, .84, .055, .06)]
        spine_loft(s, neck, lambda r, i: belly if i in (5, 6) else coat, cap_start=False)
        head = [(.42, .88, .03, .035), (.47, .89, .065, .06), (.55, .87, .055, .05), (.63, .845, .032, .03), (.69, .83, .02, .02)]
        spine_loft(s, head, lambda r, i: belly if r >= 2 and i in (5, 6) else coat)
        s.dome((.695, 0, .83), (.014, .016, .013), dark, nu=6, nv=3, full=True)
        for sy in (-1, 1):
            s.dome((.56, sy * .045, .9), (.011, .008, .011), dark, nu=6, nv=3, full=True)
            with s.at(.44, sy * .045, .93, roll=-sy * .2):
                s.dome((0, 0, .055), (.018, .032, .07), legs, nu=6, nv=4, full=True)
                s.dome((.008, 0, .05), (.008, .02, .05), belly, nu=6, nv=3, full=True)
            s.dome((-.28, sy * .08, .52), (.13, .05, .13), coat, nu=8, nv=4, full=True)
            s.dome((.26, sy * .075, .54), (.09, .05, .13), coat, nu=8, nv=4, full=True)
        limb(s, [(-.4, 0, .56), (-.53, 0, .38), (-.6, 0, .2)], [.04, .065, .03], coat)
        s.dome((-.61, 0, .17), (.03, .03, .05), dark, nu=6, nv=3, full=True)
        four_legs(s, ((.26, .07, .5), (.28, .06, .26), (.27, .06, .045)), ((-.3, .075, .5), (-.4, .07, .27), (-.34, .07, .045)), [.05, .028, .022], legs, legs, .026)


def ground_squirrel(s, upright):
    tan, pale, dark = '#b39a6b', '#d9c9a2', '#2a211c'
    if upright:
        s.dome((0, 0, .1), (.045, .045, .1), tan, nu=8, nv=5, full=True)
        s.dome((.012, 0, .105), (.04, .035, .085), pale, nu=8, nv=4, full=True)
        s.dome((.012, 0, .215), (.033, .03, .03), tan, nu=8, nv=4, full=True)
        s.dome((.042, 0, .21), (.012, .012, .01), dark, nu=5, nv=3, full=True)
        for sy in (-1, 1):
            s.dome((.022, sy * .026, .222), (.007, .005, .007), dark, nu=5, nv=3, full=True)
            s.dome((-.006, sy * .026, .24), (.008, .006, .008), tan, nu=5, nv=3, full=True)
            s.cyl((.03, sy * .022, .15), (.05, sy * .012, .13), .008, tan, sides=4)
            s.box((.02, sy * .03, .008), (.06, .022, .016), tan)
        s.ribbon((-.03, 0, .01), (-.12, .02, .006), .022, tan)
    else:
        body = [(-.1, .04, .008, .008), (-.085, .045, .03, .03), (-.03, .05, .04, .042), (.04, .052, .038, .04), (.085, .058, .028, .03), (.11, .064, .016, .018)]
        spine_loft(s, body, lambda r, i: pale if i in (5, 6) else tan)
        s.dome((.125, 0, .075), (.03, .026, .025), tan, nu=8, nv=4, full=True)
        s.dome((.153, 0, .07), (.01, .011, .009), dark, nu=5, nv=3, full=True)
        for sy in (-1, 1):
            s.dome((.135, sy * .022, .083), (.006, .005, .006), dark, nu=5, nv=3, full=True)
            s.box((.06, sy * .03, .012), (.03, .016, .024), tan)
            s.box((-.05, sy * .034, .012), (.045, .018, .024), tan)
        s.ribbon((-.1, 0, .03), (-.18, -.02, .012), .02, tan)


def ground_squirrels(s):
    soil = ['#8a7558', '#7b684d', '#96815f']
    s.dome((.05, .1, 0), (.42, .36, .08), lambda j, i: s.pick(soil, .04), nu=12, nv=3, noise=.12)
    s.dome((.12, .02, .062), (.075, .065, .02), '#241c15', nu=8, nv=2)
    with s.at(-.02, .22, .06, yaw=-1.9):
        ground_squirrel(s, True)
    with s.at(-.38, -.3, 0, yaw=-1.0):
        ground_squirrel(s, True)
    with s.at(.42, -.34, 0, yaw=2.6):
        ground_squirrel(s, False)


def duck(s, drake):
    foot = '#e2742b'
    if drake:
        body_c, breast, head_c, bill, rump = '#b9b6ae', '#6b3f2c', '#1f5a3a', '#d9c23a', '#1d1d1f'
    else:
        body_c, breast, head_c, bill, rump = '#8a6f52', '#9a7d5c', '#7a6046', '#c9772c', '#6f5a44'
    body = [(-.21, .17, .01, .012), (-.18, .165, .045, .04), (-.08, .15, .075, .07), (.03, .15, .08, .075), (.11, .17, .065, .065), (.15, .2, .04, .045)]
    spine_loft(s, body, lambda r, i: rump if r == 0 else (breast if r >= 3 else body_c))
    neck = [(.12, .21, .035, .04), (.15, .27, .028, .03), (.16, .32, .026, .027)]
    spine_loft(s, neck, head_c if not drake else (lambda r, i: breast if r == 0 else head_c), n=6, cap_start=False)
    if drake:
        s.cyl((.15, 0, .262), (.152, 0, .274), .031, '#f1f0ea', sides=8, cap0=False, cap1=False)
        s.ribbon((-.19, 0, .2), (-.24, 0, .23), .05, '#f1f0ea')
    s.dome((.175, 0, .34), (.038, .03, .03), head_c, nu=8, nv=4, full=True)
    s.box((.228, 0, .332), (.06, .03, .014), bill)
    for sy in (-1, 1):
        s.dome((.19, sy * .026, .348), (.006, .004, .006), '#1d1d1f', nu=5, nv=3, full=True)
        s.dome((-.03, sy * .07, .17), (.1, .012, .04), '#5a4a3c' if not drake else '#8f8c84', nu=6, nv=3, full=True)
        limb(s, [(.01, sy * .035, .1), (.015, sy * .035, .0)], [.008, .007], foot, sides=4)
        s.tri((.015, sy * .035, .003), (.065, sy * .06, .003), (.065, sy * .01, .003), foot)


def mallards(s):
    with s.at(-.2, .05, 0, yaw=-math.pi / 2 - .3):
        duck(s, True)
    with s.at(.22, -.12, 0, yaw=-math.pi / 2 + .5):
        duck(s, False)


def pelican(s, tucked=False):
    white, black, bill, pouch, foot = '#f4f3ee', '#1d1d1f', '#f2a23a', '#f0b84a', '#e88a2c'
    body = [(-.44, .44, .02, .02), (-.4, .43, .1, .09), (-.2, .42, .19, .17), (.02, .42, .21, .2), (.2, .46, .17, .18), (.3, .52, .1, .12)]
    spine_loft(s, body, lambda r, i: black if r == 0 and i in (0, 3, 4, 7) else white)
    if tucked:
        neck = [(.26, .55, .07, .08), (.24, .72, .055, .06), (.2, .84, .05, .05)]
        head, tip = (.24, .88), (.42, .5)
    else:
        neck = [(.26, .55, .07, .08), (.3, .72, .05, .055), (.25, .88, .045, .048), (.27, 1.0, .045, .046)]
        head, tip = (.32, 1.03), (.72, .84)
    spine_loft(s, neck, white, n=6, cap_start=False)
    s.dome((head[0], 0, head[1]), (.07, .05, .052), white, nu=8, nv=4, full=True)
    s.cyl((head[0] + .04, 0, head[1]), (tip[0], 0, tip[1]), .032, bill, r1=.012, sides=6)
    middle = mix((head[0] + .04, 0, head[1] - .03), (tip[0], 0, tip[1]), .45)
    s.tri((head[0] + .05, 0, head[1] - .03), (tip[0], 0, tip[1] - .01), (middle[0] - .04, 0, middle[2] - .11), pouch)
    for sy in (-1, 1):
        s.dome((head[0] + .03, sy * .04, head[1] + .012), (.008, .005, .008), black, nu=5, nv=3, full=True)
        s.dome((-.22, sy * .19, .46), (.2, .02, .09), black, nu=6, nv=3, full=True)
        limb(s, [(0, sy * .08, .27), (.012, sy * .08, .0)], [.022, .016], foot)
        s.tri((.012, sy * .08, .004), (.13, sy * .14, .004), (.13, sy * .02, .004), foot)


def pelicans(s):
    with s.at(-.42, .12, 0, yaw=-math.pi / 2 - .25):
        pelican(s)
    with s.at(.5, -.2, 0, yaw=-math.pi / 2 + .55, scale=.95):
        pelican(s, tucked=True)


def osprey_platform(s):
    wood, top = '#6e5a48', 11.4
    for i in range(4):
        z0, z1 = top * i / 4, top * (i + 1) / 4
        s.cyl((0, 0, z0), (0, 0, z1), .17 - .02 * i, s.c(wood, .05), r1=.17 - .02 * (i + 1), sides=8, cap0=i == 0, cap1=i == 3)
    s.box((0, 0, top + .04), (1.3, 1.3, .08), s.c(TIMBER, .05))
    for sx in (-1, 1):
        s.box((sx * .62, 0, top + .16), (.06, 1.3, .16), s.c(TIMBER, .05))
        s.box((0, sx * .62, top + .16), (1.3, .06, .16), s.c(TIMBER, .05))
        s.cyl((sx * .12, 0, top - .9), (sx * .6, 0, top), .04, wood, sides=5)
        s.cyl((0, sx * .12, top - .9), (0, sx * .6, top), .04, wood, sides=5)
    sticks = ['#6b5a48', '#857059', '#5c4c3c', '#9a856a']
    s.dome((0, 0, top + .08), (.62, .62, .34), lambda j, i: s.pick(sticks, .05), nu=12, nv=3, noise=.14)
    for k in range(26):
        a, r = k * 2.399963, .15 + .5 * ((k * 5) % 9) / 9
        centre = (math.cos(a) * r, math.sin(a) * r, top + .2 + .22 * (1 - r / .7))
        b = a + 1.3 + (k % 5) * .4
        half = (math.cos(b) * .32, math.sin(b) * .32, ((k % 3) - 1) * .06)
        s.cyl(sub(centre, half), add(centre, half), .013, s.pick(sticks, .05), sides=3)
    # osprey standing on the nest rim
    brown, white, dark = '#4a3b30', '#f1efe8', '#1d1d1f'
    with s.at(.3, -.25, top + .36, yaw=-.9):
        s.dome((0, 0, .17), (.085, .075, .17), white, nu=8, nv=5, full=True)
        s.dome((-.025, 0, .17), (.08, .085, .175), brown, nu=8, nv=5, full=True)
        s.dome((.02, 0, .37), (.05, .045, .045), white, nu=8, nv=4, full=True)
        s.cyl((.055, 0, .365), (.095, 0, .345), .014, dark, r1=.002, sides=5)
        for sy in (-1, 1):
            s.box((.03, sy * .042, .375), (.06, .008, .018), brown)
            limb(s, [(.02, sy * .03, .06), (.03, sy * .03, .0)], [.012, .01], '#c9c2b4', sides=4)
        s.ribbon((-.07, 0, .1), (-.2, 0, .02), .09, brown)


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
    # --- transit and service vehicles ---
    spec('city-bus', 'City bus', 'Vehicles', 'Twelve-metre low-floor transit bus with two curb-side doors and a folded front bike rack.', city_bus, 2701, '#1f4f85'),
    spec('light-rail-car', 'Light-rail car', 'Vehicles', 'Low-floor articulated light-rail vehicle, 25 m long, with a pantograph for a 5.5 m contact wire.', light_rail_car, 2702, '#1f7a8c'),
    spec('school-bus', 'School bus', 'Vehicles', 'Yellow conventional school bus with a folded stop arm, for school sites and pick-up loops.', school_bus, 2703, '#f2b01e'),
    spec('plow-truck', 'Snow plow truck', 'Vehicles', 'Tandem sanding truck with an angled front plow and rear spreader, for winter street scenes.', plow_truck, 2704, '#f2c230'),
    # --- construction site kit ---
    spec('roll-off-bin', 'Roll-off construction bin', 'Traffic & safety', 'Thirty-yard steel bin loaded with demolition debris, as parked beside infill sites.', roll_off_bin, 2711, '#2f6f8f'),
    spec('site-office-trailer', 'Site office trailer', 'Traffic & safety', 'Portable job-site office on blocks with timber steps and a blank sign panel.', site_office_trailer, 2712, '#d8d2c2'),
    spec('excavator', 'Excavator', 'Traffic & safety', 'Tracked hydraulic excavator with its boom reaching forward to the ground.', excavator, 2713, '#f0b323'),
    spec('skid-steer', 'Skid-steer loader', 'Traffic & safety', 'Compact wheeled loader with its bucket resting on the ground.', skid_steer, 2714, '#e2742b'),
    spec('lumber-stacks', 'Lumber and sheet goods', 'Traffic & safety', 'Two strapped bundles of framing lumber and a pallet of plywood on a building site.', lumber_stacks, 2715, '#d9b98a'),
    spec('concrete-barrier', 'Concrete barrier', 'Traffic & safety', 'Repeatable 3 m precast safety-shape barrier section for work zones and road edges.', concrete_barrier, 2716, '#b9b6ae'),
    # --- river and city edge ---
    spec('inflatable-raft', 'Inflatable raft', 'Landscape', 'Blue river raft pulled up on shore with paddles and a cooler, for a float down the Bow.', inflatable_raft, 2721, '#2a66a8'),
    spec('canoe', 'Canoe', 'Landscape', 'Red canoe resting on its side on the bank with a paddle inside.', canoe, 2722, '#b23a34'),
    spec('drift-boat', 'Drift boat', 'Landscape', 'High-ended river fishing boat with oars shipped, as used by anglers on the Bow.', drift_boat, 2723, '#2f6f8f'),
    spec('pumpjack', 'Pumpjack', 'Landscape', 'Beam pumping unit over an oil well, a familiar sight in fields at the edge of Alberta towns.', pumpjack, 2724, '#3f6b55'),
    spec('grain-bins', 'Grain bins', 'Landscape', 'Pair of corrugated steel farm bins with conical roofs and ladders.', grain_bins, 2725, '#b9c0c4'),
    spec('wind-turbine', 'Wind turbine', 'Landscape', 'Utility-scale three-blade turbine with a 60 m hub, as seen across southern Alberta.', wind_turbine, 2726, '#e9ecee'),
    # --- street and yard basics ---
    spec('street-light', 'Roadway street light', 'Lighting', 'Nine-metre davit pole with a flat roadway luminaire reaching over the curb.', street_light, 2731, '#9aa3a8'),
    spec('basket-lamp-post', 'Lamp post with flower baskets', 'Lighting', 'Black heritage-style post with a globe and two hanging summer flower baskets, for main streets.', basket_lamp_post, 2732, '#1d1f22'),
    spec('flagpole', 'Flagpole', 'Street furniture', 'Nine-metre aluminium pole flying a plain flag with no emblem.', flagpole, 2733, '#1f7a8c'),
    spec('lane-garage', 'Lane garage', 'Garden & growing', 'Detached double garage with a sectional overhead door facing the back lane.', lane_garage, 2734, '#b8b2a4'),
    spec('carport', 'Carport', 'Shelters & markets', 'Two-stall steel carport with a low-slope roof and a slatted back screen.', carport, 2735, '#8f979b'),
    spec('solar-array', 'Ground solar array', 'Street furniture', 'Sixteen-panel ground-mounted solar table tilted south on steel posts.', solar_array, 2736, '#1c2f4a'),
    # --- wildlife and ranch animals, round two ---
    spec('ground-squirrels', "Richardson's ground squirrels", WILDLIFE, 'Urocitellus richardsonii · prairie gophers standing watch beside a burrow mound. Static model.', ground_squirrels, 2741, '#b39a6b'),
    spec('coyote', 'Coyote', WILDLIFE, 'Canis latrans · alert and standing, as seen in river valleys and on park edges. Static model.', coyote, 2742, '#9a8a72'),
    spec('mallards', 'Mallards', WILDLIFE, 'Anas platyrhynchos · a drake and a hen on the bank of a pond or storm pond. Static model.', mallards, 2743, '#1f5a3a'),
    spec('pelicans', 'American white pelicans', WILDLIFE, 'Pelecanus erythrorhynchos · two summer visitors to the Bow, one with its bill tucked. Static model.', pelicans, 2744, '#f2a23a'),
    spec('osprey-platform', 'Osprey nesting platform', WILDLIFE, 'Pandion haliaetus · tall pole with a stick nest and a perched osprey, as raised along the rivers. Static model.', osprey_platform, 2745, '#6e5a48'),
    spec('horses', 'Horses', 'Landscape', 'Two ranch horses, a bay standing and a buckskin grazing, for acreages at the city edge. Static model.', horses, 2746, '#7a4a2c'),
    spec('cattle', 'Cattle', 'Landscape', 'Two beef cattle, a white-faced red cow and a black cow grazing, for foothills ranchland. Static model.', cattle, 2747, '#7a3b22'),
    # --- painted road barriers: original murals on the 3 m concrete barrier ---
    spec('mural-barrier-foothills', 'Mural barrier · Foothills sunrise', 'Traffic & safety', 'Repeatable 3 m road barrier painted with a sunrise over peaks, foothills and prairie. Original design.', mural_foothills, 2801, '#f08a5d'),
    spec('mural-barrier-chinook', 'Mural barrier · Chinook arch', 'Traffic & safety', 'Repeatable 3 m road barrier painted with a chinook arch of sunset cloud over the range. Original design.', mural_chinook, 2802, '#b8456b'),
    spec('mural-barrier-river', 'Mural barrier · River ribbons', 'Traffic & safety', 'Repeatable 3 m road barrier painted with flowing bands of river blue and green. Original design.', mural_river, 2803, '#1b6ca8'),
    spec('mural-barrier-mosaic', 'Mural barrier · Triangle mosaic', 'Traffic & safety', 'Repeatable 3 m road barrier painted with a bright mosaic of irregular triangles. Original design.', mural_mosaic, 2804, '#06d6a0'),
    spec('mural-barrier-chevron', 'Mural barrier · Chevrons', 'Traffic & safety', 'Repeatable 3 m road barrier painted with bold zigzag chevrons. Original design.', mural_chevron, 2805, '#ef476f'),
    spec('mural-barrier-quilt', 'Mural barrier · Prairie quilt', 'Traffic & safety', 'Repeatable 3 m road barrier painted as patchwork quilt blocks in barn red, mustard and denim. Original design.', mural_quilt, 2806, '#9b2d30'),
    spec('mural-barrier-aspen', 'Mural barrier · Aspen grove', 'Traffic & safety', 'Repeatable 3 m road barrier painted with white aspen trunks under a gold canopy. Original design.', mural_aspen, 2807, '#e6b93a'),
    spec('mural-barrier-confetti', 'Mural barrier · Confetti', 'Traffic & safety', 'Repeatable 3 m road barrier painted with bright dots on deep teal. Original design.', mural_confetti, 2808, '#1f5f6b'),
    # --- seasonal patios: boardwalk sections, on-street patios, parklets ---
    spec('boardwalk-section', 'Boardwalk section', 'Access & levels', 'Repeatable 3 m timber walkway for the parking lane, level with the sidewalk, 2.3 m clear, with a guard on the road side.', boardwalk_section, 2901, '#b99a6b'),
    spec('boardwalk-section-short', 'Boardwalk section · 1.5 m', 'Access & levels', 'Half-length boardwalk section for fitting a run to a frontage. Level with the sidewalk, guard on the road side.', boardwalk_section_short, 2902, '#b99a6b'),
    spec('boardwalk-end-approach', 'Boardwalk end · approach', 'Access & levels', 'Boardwalk end closed by a guard return, with a yellow and black hazard marker facing approaching traffic.', boardwalk_end_approach, 2903, '#f2c230'),
    spec('boardwalk-end-far', 'Boardwalk end · far', 'Access & levels', 'Boardwalk end closed by a guard return, for the end that traffic leaves behind.', boardwalk_end_far, 2904, '#b99a6b'),
    spec('street-patio-one-stall', 'On-street patio · one stall', 'Seating', 'Fenced dining platform in one parking stall, level with the sidewalk: two tables, eight seats, umbrellas and a 2 m entrance.', street_patio_one_stall, 2905, '#b5432a'),
    spec('street-patio-two-stall', 'On-street patio · two stalls', 'Seating', 'Fenced dining platform 11 m long in two parking stalls: four tables, sixteen seats, umbrellas and a 2 m entrance.', street_patio_two_stall, 2906, '#2f6f8f'),
    spec('parklet-one-stall', 'Parklet · one stall', 'Seating', 'Public seating platform in one parking stall, open to the sidewalk, with built-in benches, planters and two small tables.', parklet_one_stall, 2907, '#e0b63a'),
    spec('parklet-two-stall', 'Parklet · two stalls', 'Seating', 'Public seating platform 11 m long in two parking stalls, with benches, a long shared table, planters and umbrellas.', parklet_two_stall, 2908, '#1f7a8c'),
    spec('sidewalk-patio', 'Sidewalk patio', 'Seating', 'Fenced dining area on a wide sidewalk, 6 m by 2.2 m, with tables, umbrellas and planters. Keep 2 m of walkway clear beside it.', sidewalk_patio, 2909, '#8a6a4a'),
    spec('patio-fence-panel', 'Patio guard panel', 'Edges & gates', 'Repeatable 2.4 m free-standing timber patio guard with a cane-detection rail. Its weighted feet go on the patio side.', patio_fence_panel, 2910, '#8a6a4a'),
    spec('low-profile-barrier', 'Low-profile barrier', 'Traffic & safety', 'Repeatable 3 m low concrete traffic barrier, half a metre tall, for the road end of a patio or boardwalk.', low_profile_barrier, 2911, '#b9b6ae'),
    # --- boardwalk modules in feet, with guards on both long sides and open ends ---
    spec('boardwalk-module-nine-foot', 'Boardwalk module · 6 × 9 ft', 'Access & levels', 'Repeatable 6 ft by 9 ft boardwalk module with grey decking, level with the sidewalk. Red steel railings on both long sides, open ends.', boardwalk_module_nine_foot, 2921, '#cf1f2b'),
    spec('boardwalk-module-twelve-foot', 'Boardwalk module · 6 × 12 ft', 'Access & levels', 'Repeatable 6 ft by 12 ft boardwalk module with grey decking, level with the sidewalk. Red steel railings on both long sides, open ends.', boardwalk_module_twelve_foot, 2922, '#cf1f2b'),
    spec('boardwalk-corner', 'Boardwalk corner · 6 × 6 ft', 'Access & levels', 'Six-foot-square boardwalk corner with red steel railings on its two outer sides, for turning a run toward the sidewalk. Rotate to suit.', boardwalk_corner, 2923, '#cf1f2b'),
    spec('boardwalk-corner-approach', 'Boardwalk corner · approach', 'Access & levels', 'Six-foot-square boardwalk corner with red steel railings on two outer sides and a hazard marker facing approaching traffic.', boardwalk_corner_approach, 2924, '#f2c230'),
    spec('boardwalk-module-nine-foot-road-rail', 'Boardwalk module · 6 × 9 ft · road-side rail', 'Access & levels', 'Repeatable 6 ft by 9 ft boardwalk module with grey decking and a red steel railing on the road side only. Open to the sidewalk.', boardwalk_module_nine_foot_road_rail, 2925, '#cf1f2b'),
    spec('boardwalk-module-twelve-foot-road-rail', 'Boardwalk module · 6 × 12 ft · road-side rail', 'Access & levels', 'Repeatable 6 ft by 12 ft boardwalk module with grey decking and a red steel railing on the road side only. Open to the sidewalk.', boardwalk_module_twelve_foot_road_rail, 2926, '#cf1f2b'),
    spec('boardwalk-module-nine-foot-black', 'Boardwalk module · 6 × 9 ft · black', 'Access & levels', 'Repeatable 6 ft by 9 ft boardwalk module with grey decking, level with the sidewalk. Black steel railings on both long sides, open ends.', boardwalk_module_nine_foot_black, 2927, '#232527'),
    spec('boardwalk-module-twelve-foot-black', 'Boardwalk module · 6 × 12 ft · black', 'Access & levels', 'Repeatable 6 ft by 12 ft boardwalk module with grey decking, level with the sidewalk. Black steel railings on both long sides, open ends.', boardwalk_module_twelve_foot_black, 2928, '#232527'),
    spec('boardwalk-corner-black', 'Boardwalk corner · 6 × 6 ft · black', 'Access & levels', 'Six-foot-square boardwalk corner with black steel railings on its two outer sides, for turning a run toward the sidewalk. Rotate to suit.', boardwalk_corner_black, 2929, '#232527'),
    spec('boardwalk-corner-approach-black', 'Boardwalk corner · approach · black', 'Access & levels', 'Six-foot-square boardwalk corner with black steel railings on two outer sides and a hazard marker facing approaching traffic.', boardwalk_corner_approach_black, 2930, '#f2c230'),
    spec('boardwalk-module-nine-foot-road-rail-black', 'Boardwalk module · 6 × 9 ft · road-side rail · black', 'Access & levels', 'Repeatable 6 ft by 9 ft boardwalk module with grey decking and a black steel railing on the road side only. Open to the sidewalk.', boardwalk_module_nine_foot_road_rail_black, 2931, '#232527'),
    spec('boardwalk-module-twelve-foot-road-rail-black', 'Boardwalk module · 6 × 12 ft · road-side rail · black', 'Access & levels', 'Repeatable 6 ft by 12 ft boardwalk module with grey decking and a black steel railing on the road side only. Open to the sidewalk.', boardwalk_module_twelve_foot_road_rail_black, 2932, '#232527'),
    spec('low-profile-mural-foothills', 'Low-profile mural barrier · Foothills sunrise', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with a sunrise over peaks, foothills and prairie. Original design.', low_profile_mural_foothills, 2941, '#f08a5d'),
    spec('low-profile-mural-chinook', 'Low-profile mural barrier · Chinook arch', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with a chinook arch of sunset cloud over the range. Original design.', low_profile_mural_chinook, 2942, '#b8456b'),
    spec('low-profile-mural-river', 'Low-profile mural barrier · River ribbons', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with flowing bands of river blue and green. Original design.', low_profile_mural_river, 2943, '#1b6ca8'),
    spec('low-profile-mural-mosaic', 'Low-profile mural barrier · Triangle mosaic', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with a bright mosaic of irregular triangles. Original design.', low_profile_mural_mosaic, 2944, '#06d6a0'),
    spec('low-profile-mural-chevron', 'Low-profile mural barrier · Chevrons', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with bold zigzag chevrons. Original design.', low_profile_mural_chevron, 2945, '#ef476f'),
    spec('low-profile-mural-quilt', 'Low-profile mural barrier · Prairie quilt', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted as patchwork quilt blocks in barn red, mustard and denim. Original design.', low_profile_mural_quilt, 2946, '#9b2d30'),
    spec('low-profile-mural-aspen', 'Low-profile mural barrier · Aspen grove', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with white aspen trunks under a gold canopy. Original design.', low_profile_mural_aspen, 2947, '#e6b93a'),
    spec('low-profile-mural-confetti', 'Low-profile mural barrier · Confetti', 'Traffic & safety', 'Repeatable 3 m low-profile barrier painted with bright dots on deep teal. Original design.', low_profile_mural_confetti, 2948, '#1f5f6b'),
    spec('barrier-planter-pink', 'Barrier planter · pink petunias', 'Planting', 'Black moulded 4 ft planter with forklift pockets and reflective tape on its ends, full of pink petunias and trailing lime vine.', barrier_planter_pink, 2951, '#e8559a'),
    spec('barrier-planter-purple', 'Barrier planter · purple petunias', 'Planting', 'Black moulded 4 ft planter with forklift pockets and reflective tape on its ends, full of purple petunias and trailing lime vine.', barrier_planter_purple, 2952, '#7b3fc4'),
    spec('long-planter', 'Long black planter', 'Planting', 'Black panelled 6 ft planter box on low feet, full of mixed summer annuals and trailing lime vine, for the road edge of a patio.', long_planter, 2953, '#c22a9a'),
    spec('district-barrier-kensington', 'District barrier · Kensington', 'Traffic & safety', 'Burgundy 3 m road barrier with the Kensington wordmark in off-white and roundel in orange. The logo belongs to its business association.', district_barrier_kensington, 2961, '#42031a'),
    spec('district-barrier-inglewood', 'District barrier · Inglewood', 'Traffic & safety', 'Repeatable 3 m road barrier with the Inglewood district wordmark in yellow on red. The logo belongs to its business association.', district_barrier_inglewood, 2962, '#d84d2c'),
    spec('district-barrier-fourth-street-purple', 'District barrier · Fourth Street · purple', 'Traffic & safety', 'Purple 3 m road barrier with the Fourth Street name between two 4s, in white and pink. The logo belongs to its business association.', district_barrier_fourth_street_purple, 2963, '#6c3991'),
    spec('district-barrier-fourth-street-green', 'District barrier · Fourth Street · green', 'Traffic & safety', 'Teal 3 m road barrier with the Fourth Street name between two 4s, in white and green. The logo belongs to its business association.', district_barrier_fourth_street_green, 2964, '#23997c'),
    spec('district-barrier-seventeenth-ave', 'District barrier · 17th Ave', 'Traffic & safety', 'Red 3 m road barrier with the 17th Ave logo four times in white. The logo belongs to its business association.', district_barrier_seventeenth_ave, 2965, '#e21a2d'),
    spec('district-barrier-seventeenth-ave-single', 'District barrier · 17th Ave · single logo', 'Traffic & safety', 'Red 3 m road barrier with one large 17th Ave logo in white at its centre. The logo belongs to its business association.', district_barrier_seventeenth_ave_single, 2966, '#e21a2d'),
    spec('city-ghost-barrier', 'City Ghost on a barrier', 'Water & landmarks', 'Blue ghost sculpture with big white eyes and a cowboy hat, just under 2 m tall, astride a 3 m barrier. The artwork belongs to its artist.', city_ghost_barrier, 2971, '#27a8d2'),
    spec('city-ghost-barrier-pink', 'City Ghost on a pink barrier', 'Water & landmarks', 'Blue ghost sculpture with big white eyes and a cowboy hat, astride a pink barrier of white doodles. The artwork belongs to its artist.', city_ghost_barrier_pink, 2972, '#ee8f8c'),
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
