#!/usr/bin/env python3
"""Local prairie foliage for Add details: Calgary and Alberta trees, shrubs and grasses.

Blender-free and deterministic. Every plant is authored in metres, Z-up, with
the trunk or clump centre at the origin and the ground at z = 0, then written
as a Y-up GLB 2.0 in the public-realm kit convention: POSITION/NORMAL/COLOR_0
linear vertex colours, one double-sided roughness-0.9 material, flat normals
and one untransformed node per wood/foliage mesh. The recipe follows the
accepted meadow kit: visible tapered limbs, attached leafy sprays and small
folded leaf tufts with gaps through the crown, never a solid crown shell.

Species are visual types for site visualization at hardiness zone 3-4, not
botanical specimens, growth models or planting advice.

    python tools/detail_catalogue/build_local_foliage.py --dry-run
    python tools/detail_catalogue/build_local_foliage.py --output <fresh-directory> [--id <slug> ...]
    node tools/detail_catalogue/render_detail_thumbnails.cjs <directory>
    python tools/detail_catalogue/build_local_foliage.py --output <directory> --attach-thumbnails
    python tools/detail_catalogue/build_local_foliage.py --output <directory> --register

--register splices the finished rows into the frontend extras catalogue and the
backend allowlist by text-level insertion after writing .bak-detail-register
backups. It refuses IDs that already exist.
"""
import argparse
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
KIT = 'prairie-foliage-v1'
PREFIX = 'detail-prairie-'
URL_ROOT = f'/park-kits/{KIT}'
GOLDEN = 2.399963
TREE_NOTE = 'Keep the trunk clear of paths; canopies can overlap.'
SHRUB_NOTE = 'Place in beds and soft landscape edges.'

# Muted, linear-converted palettes shared with the meadow kit; species shift them.
GREENS = ['#657951', '#829368', '#506945', '#94a176', '#718758']
LIGHT_GREENS = ['#7f9a5a', '#95ad66', '#6a8a4d', '#a7b875', '#8aa060']
DARK_GREENS = ['#4f6a44', '#5e7a4d', '#3f5a3a', '#6a8656']
SILVER = ['#879484', '#a6b09b', '#71846e', '#94a18d', '#b0b8a7']
PURPLE_LEAF = ['#4a2f3f', '#5c3a4a', '#6d4756', '#3d2633', '#7a5262']
SPRUCE = ['#4a6652', '#577560', '#3d5847', '#62806a']
BLUE_SPRUCE = ['#7b8e98', '#8c9ea6', '#6a7d88', '#9fb0b5']
LARCH = ['#93ad6a', '#a7bf78', '#7e9a5b', '#b3c88a']
JUNIPER = ['#6e8a7a', '#5f7a6c', '#7f9a8c', '#8ea89a']
GRASS_GREENS = ['#788452', '#99a06c', '#b0ab78', '#617344']
FESCUE = ['#8c9a7a', '#a4ad84', '#7a8a6c', '#b7b78e']
AUTUMN_GOLD = ['#d9b23c', '#e6c24d', '#c99a2e', '#edd070', '#b8872a']
LARCH_GOLD = ['#d6a93a', '#e3bb4f', '#c4932c', '#eccc6c']
SNOW = ['#f4f7fa', '#e6edf3', '#fbfcfd', '#dde6ee']
PINE_BLUE = ['#5d7a6a', '#6b8a78', '#4f6b5c', '#7a9a88']
FIR = ['#465f45', '#547052', '#3a5139', '#627f5c']
LIMBER = ['#4d6a55', '#5a7a62', '#405a49', '#688a70']
SAGE_SILVER = ['#97a391', '#a8b2a0', '#869482', '#b3bbab']
BEARBERRY = ['#3e5b3a', '#4b6b45', '#345032', '#587a50']
GRAMA = ['#8a9468', '#a1a878', '#77825a', '#b3b488']
JUNE = ['#7f9068', '#93a37a', '#6d7f5a', '#a6b38b']


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4)
    return tuple(out)


GLOSS_MATERIAL = {'name': 'kit_linear_vertex_colour_gloss', 'doubleSided': True,
                  'pbrMetallicRoughness': {'metallicFactor': 0, 'roughnessFactor': 0.35}}


class Part:
    """Flat-shaded triangle soup with a linear colour per vertex."""

    material = 0  # 1 selects the smoother glass/ice material used by hard-surface kits

    def __init__(self, name):
        self.name = name
        self.positions = []
        self.normals = []
        self.colors = []

    def triangle(self, a, b, c, colour):
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length < 1e-12:
            return
        normal = (nx / length, ny / length, nz / length)
        self.positions.extend((*a, *b, *c))
        self.normals.extend(normal * 3)
        self.colors.extend(colour * 3)

    @property
    def triangles(self):
        return len(self.positions) // 9


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def rotate(p, rx, ry, rz):
    x, y, z = p
    cy, sy = math.cos(rx), math.sin(rx)
    y, z = y * cy - z * sy, y * sy + z * cy
    cy, sy = math.cos(ry), math.sin(ry)
    x, z = x * cy + z * sy, -x * sy + z * cy
    cy, sy = math.cos(rz), math.sin(rz)
    x, y = x * cy - y * sy, x * sy + y * cy
    return (x, y, z)


class Plant:
    """season None is the leafy summer plant. 'winter' keeps the identical
    skeleton and random sequence but drops leaves to twiglets and needles to
    spurs; 'snow' swaps a share of needle tufts for snow. Seasonal choices draw
    from a second random stream so the summer bytes never change."""

    def __init__(self, seed, season=None):
        self.random = random.Random(seed).random
        self.extra = random.Random(seed + 7919).random
        self.season = season
        self.twig_colour = '#5d5148'
        self.persist = None
        self.snow_rate = .5
        self.wood = Part('wood')
        self.foliage = Part('foliage')
        self._linear = {}

    def colour(self, hex_colour):
        if hex_colour not in self._linear:
            self._linear[hex_colour] = srgb_to_linear(hex_colour)
        return self._linear[hex_colour]

    def pick(self, palette, index=None):
        return self.colour(palette[int(self.random() * len(palette)) if index is None else index % len(palette)])

    # --- woody primitives -------------------------------------------------
    def stem(self, a, b, base, tip, bark, sides=5):
        axis = np.array(b, dtype=float) - np.array(a, dtype=float)
        length = float(np.linalg.norm(axis))
        if length < 1e-9:
            return
        axis /= length
        up = np.array([1.0, 0.0, 0.0]) if abs(axis[2]) > .95 else np.array([0.0, 0.0, 1.0])
        u = np.cross(up, axis)
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)
        colour = self.colour(bark)

        def ring(p, r, angle):
            return (p[0] + r * (u[0] * math.cos(angle) + v[0] * math.sin(angle)),
                    p[1] + r * (u[1] * math.cos(angle) + v[1] * math.sin(angle)),
                    p[2] + r * (u[2] * math.cos(angle) + v[2] * math.sin(angle)))

        for i in range(sides):
            a0, a1 = i * math.tau / sides, (i + 1) * math.tau / sides
            p, q, r, s = ring(a, base, a0), ring(a, base, a1), ring(b, tip, a1), ring(b, tip, a0)
            self.wood.triangle(p, q, r, colour)
            self.wood.triangle(p, r, s, colour)
            self.wood.triangle(b, s, r, colour)

    def path(self, points, radii, bark, sides=6):
        for (a, b), (r0, r1) in zip(zip(points, points[1:]), zip(radii, radii[1:])):
            self.stem(a, b, r0, r1, bark, sides)

    def bark_mark(self, centre, u, v, width, height, colour):
        """Thin surface patch tangent to a trunk: lenticels, knots, bark plates."""
        c = self.colour(colour)
        corners = [(centre[0] + sx * u[0] * width + sz * v[0] * height,
                    centre[1] + sx * u[1] * width + sz * v[1] * height,
                    centre[2] + sx * u[2] * width + sz * v[2] * height) for sx, sz in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
        self.wood.triangle(corners[0], corners[1], corners[2], c)
        self.wood.triangle(corners[0], corners[2], corners[3], c)

    # --- leafy primitives -------------------------------------------------
    def twiglet(self, p, angle, length, lift):
        """Winter stand-in for a leaf: one fine sliver, turned about its own axis."""
        dx, dy = math.cos(angle), math.sin(angle)
        tip = (p[0] + dx * length * 1.15, p[1] + dy * length * 1.15, p[2] + lift * .5 + length * .4)
        turn = self.extra() * math.pi
        w = .012
        sx, sy, sz = -dy * math.cos(turn) * w, dx * math.cos(turn) * w, math.sin(turn) * w
        self.wood.triangle((p[0] - sx, p[1] - sy, p[2] - sz), (p[0] + sx, p[1] + sy, p[2] + sz), tip, self.colour(self.twig_colour))

    def leaf(self, p, angle, length, width, lift, colour, part=None):
        if self.season == 'winter' and part is None:
            self.twiglet(p, angle, length, lift)
            return
        part = part or self.foliage
        dx, dy = math.cos(angle), math.sin(angle)
        tip = (p[0] + dx * length, p[1] + dy * length, p[2] + lift)
        left = (p[0] + dx * length * .48 - dy * width, p[1] + dy * length * .48 + dx * width, p[2] + lift * .6 + width * .25)
        right = (p[0] + dx * length * .48 + dy * width, p[1] + dy * length * .48 - dx * width, p[2] + lift * .6 - width * .25)
        part.triangle(p, left, tip, colour)
        part.triangle(p, tip, right, colour)

    def tuft(self, centre, size, colour, stretch=1.0, rotation=None):
        """Six-point folded tuft, four triangles; the kit's needle/leaf cluster."""
        rx, ry, rz = rotation or (self.random() * math.pi, self.random() * math.pi, self.random() * math.tau)
        if self.season == 'winter':
            if self.persist is None:
                # Needles and petals are gone; a short spur keeps the branch from reading as wire.
                d = rotate((size * stretch * .5, 0, 0), rx, ry, rz)
                w = .008
                self.wood.triangle((centre[0], centre[1], centre[2] - w), (centre[0], centre[1], centre[2] + w),
                                   (centre[0] + d[0], centre[1] + d[1], centre[2] + abs(d[2])), self.colour(self.twig_colour))
                return
            colour = self.colour(self.persist)
        elif self.season == 'snow' and self.extra() < self.snow_rate:
            # Snow settles as flat slabs on the upper side of the branch.
            colour = self.colour(SNOW[int(self.extra() * len(SNOW))])
            rx, ry = (self.extra() - .5) * 1.5, (self.extra() - .5) * 1.5
            centre = (centre[0], centre[1], centre[2] + size * .22)
            size, stretch = size * 1.2, min(stretch, 1.6)
        base = [(-.5, 0, 0), (-.24, -.34, 0), (.28, -.28, 0), (.5, 0, 0), (.24, .34, 0), (-.28, .28, .12)]
        points = []
        for x, y, z in base:
            p = rotate((x * size * stretch, y * size, z * size), rx, ry, rz)
            points.append((centre[0] + p[0], centre[1] + p[1], centre[2] + p[2]))
        for i in (1, 2, 3, 4):
            self.foliage.triangle(points[0], points[i], points[i + 1], colour)

    def spray(self, base, radius, height, twigs, leaf_size, greens, bark, width_ratio=.3, leaves=6, twig_radius=.009, accent=None, pairs=2):
        """Twigs with leaves fanned around each node; several per limb create gaps."""
        for j in range(twigs):
            angle = j * GOLDEN + self.random() * .5
            distance = radius * (.4 + self.random() * .6)
            tip = (base[0] + math.cos(angle) * distance, base[1] + math.sin(angle) * distance, base[2] + height * (.1 + self.random() * .9))
            self.stem(base, tip, twig_radius, twig_radius * .22, self.twig_colour if self.season == 'winter' else bark, 4)
            for n in range(1, leaves + 1):
                p = mix(base, tip, n / (leaves + 1))
                for k in range(pairs):
                    side = -1 if k % 2 else 1
                    a = angle + side * (.7 + self.random() * .8) + (k // 2) * 1.1
                    self.leaf(p, a, leaf_size * (.75 + self.random() * .5), leaf_size * width_ratio, (self.random() - .2 + (k // 2) * .35) * leaf_size, self.pick(greens, j + n + k))
            if accent and self.random() < accent.get('rate', 0):
                self.accent(tip, accent)

    def accent(self, p, accent):
        self.persist = accent.get('winter')
        try:
            self._accent(p, accent)
        finally:
            self.persist = None

    def _accent(self, p, accent):
        kind, colour, size = accent['kind'], accent['colour'], accent.get('size', .05)
        if kind == 'blossom':
            alt = accent.get('alt', colour)
            for k in range(accent.get('count', 4)):
                a = k * GOLDEN + self.random() * math.tau
                r = size * (.4 + self.random() * 1.6)
                self.tuft((p[0] + math.cos(a) * r, p[1] + math.sin(a) * r, p[2] + (self.random() - .6) * size * 2.2), size * (.8 + self.random() * .5),
                          self.colour(alt if k % 2 else colour))
        elif kind == 'berry':
            for k in range(accent.get('count', 4)):
                a = k * GOLDEN
                self.tuft((p[0] + math.cos(a) * size * .8, p[1] + math.sin(a) * size * .8, p[2] - size * .5 - k * size * .25), size * .55, self.colour(colour))
        elif kind == 'flower':
            centre = self.colour(accent.get('centre', '#e6d27a'))
            for k in range(5):
                self.leaf(p, k * math.tau / 5 + self.random(), size, size * .5, size * .2, self.colour(colour))
            self.tuft((p[0], p[1], p[2] + size * .1), size * .35, centre, rotation=(0, 0, self.random() * math.tau))
        elif kind == 'panicle':
            rows = accent.get('count', 7)
            for k in range(rows):
                t = k / rows
                r = size * (1.2 - t) * .9
                for m in range(3):
                    a = m * math.tau / 3 + k * .9
                    self.tuft((p[0] + math.cos(a) * r * .5, p[1] + math.sin(a) * r * .5, p[2] + k * size * .75), size * (.9 - t * .4), self.colour(colour))
        elif kind == 'catkin':
            self.stem(p, (p[0], p[1], p[2] - size * 2.2), size * .18, size * .1, colour, 4)
        elif kind == 'plume':
            for k in range(accent.get('count', 9)):
                self.tuft((p[0] + (self.random() - .5) * size * .4, p[1] + (self.random() - .5) * size * .4, p[2] + k * size * .55), size * (.55 + .1 * (k % 3)), self.colour(colour), stretch=1.8)


# ---------------------------------------------------------------------------
# Deciduous trees
# ---------------------------------------------------------------------------
PROFILES = {
    'round': lambda t: math.sin((.18 + .75 * t) * math.pi),
    'oval': lambda t: math.sin(math.pi * (.08 + .84 * t)) ** .7,
    'columnar': lambda t: .95 - .35 * t,
    'spreading': lambda t: .55 + .45 * math.sin(math.pi * (.15 + .7 * t)),
    'vase': lambda t: .45 + .55 * t,
    'weeping': lambda t: .5 + .5 * math.sin(math.pi * (.2 + .7 * t)),
}


def deciduous(plant, p):
    height = p['height']
    scale = height / 7
    plant.twig_colour = p.get('twig', plant.twig_colour)
    trunks = p.get('trunks', 1)
    spread = p.get('trunk_spread', 0)
    profile = PROFILES[p.get('profile', 'round')]
    rise = p.get('rise', .34)
    for t_index in range(trunks):
        angle = t_index * math.tau / trunks + .4
        lean = p.get('lean', .34) * (1 if trunks == 1 else 1.6)
        base_x, base_y = (math.cos(angle) * spread, math.sin(angle) * spread) if trunks > 1 else (0, 0)
        sway = p.get('sway', 0)

        def trunk(z, _angle=angle, _lean=lean, _bx=base_x, _by=base_y):
            f = z / height
            return (_bx + math.cos(_angle) * _lean * f ** 1.3 + sway * math.sin(f * math.pi * 2) * .25,
                    _by + math.sin(_angle) * _lean * f, z)

        radius = p['trunk_radius'] * (1 if trunks == 1 else .72)
        segments = 8
        points = [trunk(height * i / segments) for i in range(segments + 1)]
        radii = [radius * (1 - .9 * (i / segments) ** 1.1) for i in range(segments + 1)]
        plant.path(points, radii, p['bark'], p.get('trunk_sides', 7))
        marks = p.get('bark_marks')
        if marks:
            for k in range(int(28 * scale * (1 if trunks == 1 else .6))):
                z = height * (.08 + .62 * plant.random())
                a = plant.random() * math.tau
                centre = trunk(z)
                r = radius * (1 - .9 * (z / height) ** 1.1) + .004
                normal = (math.cos(a), math.sin(a), 0)
                u = (-math.sin(a), math.cos(a), 0)
                c = (centre[0] + normal[0] * r, centre[1] + normal[1] * r, centre[2])
                if marks == 'birch':
                    plant.bark_mark(c, u, (0, 0, 1), .05 + plant.random() * .11, .012 + plant.random() * .012, '#3b3a35')
                elif marks == 'furrow':
                    plant.bark_mark(c, u, (0, 0, 1), .025 + r * .12 * plant.random(), .3 + plant.random() * .5, p.get('mark_colour', '#3f3a34'))
                elif marks == 'lenticel':
                    plant.bark_mark(c, u, (0, 0, 1), .04 + plant.random() * .07, .01 + plant.random() * .006, p.get('mark_colour', '#d6b48c'))
                else:
                    plant.bark_mark(c, u, (0, 0, 1), .05 + plant.random() * .05, .09 + plant.random() * .09, '#4d4a42')
        branches = p['branches'] if trunks == 1 else max(5, p['branches'] // trunks)
        crown_base, crown_top = p.get('crown_base', .3), p.get('crown_top', .96)
        reach_max = p['reach'] * (1 if trunks == 1 else .8)
        for i in range(branches):
            f = i / branches
            z = height * (crown_base + (crown_top - crown_base) * f)
            a = trunk(z)
            direction = i * GOLDEN + t_index * 1.7 + plant.random() * .35
            reach = reach_max * profile(f) * (.8 + plant.random() * .2)
            tip_z = z + rise * reach + plant.random() * .25 * scale
            b = (a[0] + math.cos(direction) * reach * .56, a[1] + math.sin(direction) * reach * .56, z + (tip_z - z) * .55 + p.get('droop', 0) * reach * .3)
            c = (a[0] + math.cos(direction) * reach, a[1] + math.sin(direction) * reach, tip_z - p.get('droop', 0) * reach)
            limb = p.get('limb_radius', .065) * scale
            plant.stem(a, b, limb, limb * .36, p['bark'])
            plant.stem(b, c, limb * .36, limb * .12, p['bark'])
            sprays = p.get('sprays', 3)
            for s in range(sprays):
                start = mix(b, c, .15 + s * (.85 / max(1, sprays - 1)) if sprays > 1 else 1)
                plant.spray(start, p['spray_radius'], p['spray_height'], p.get('twigs', 6), p['leaf_size'], p['greens'], p['bark'],
                            p.get('leaf_width', .3), p.get('leaves', 6), .009 * max(1, scale * .8), p.get('accent'), p.get('pairs', 3))
        if p.get('top_spray', True):
            plant.spray(trunk(height), p['spray_radius'] * .7, p['spray_height'] * .75, p.get('twigs', 6) * 2, p['leaf_size'] * .9, p['greens'], p['bark'],
                        p.get('leaf_width', .3), p.get('leaves', 6), .009 * max(1, scale * .8), p.get('accent'), p.get('pairs', 3))


# ---------------------------------------------------------------------------
# Conifers
# ---------------------------------------------------------------------------
def conifer(plant, p):
    height = p['height']
    crown_base = p.get('crown_base', .08) * height
    spacing = p['whorl_spacing']
    bark = p['bark']
    radius = p['trunk_radius']
    segments = 10
    points = [(0, 0, height * i / segments) for i in range(segments + 1)]
    radii = [radius * (1 - .96 * (i / segments) ** .9) for i in range(segments + 1)]
    if p.get('upper_bark'):
        # Scots pine: plated grey-brown below, flaking orange above.
        for i in range(segments):
            plant.stem(points[i], points[i + 1], radii[i], radii[i + 1], bark if i < segments * p.get('upper_from', .45) else p['upper_bark'], 7)
    else:
        plant.path(points, radii, bark, 7)
    plant.twig_colour = p.get('twig', bark)
    kind = p.get('kind', 'spruce')
    needles = p['needles']
    tuft_size = p['tuft_size']
    whorl = 0
    z = crown_base
    while z < height - spacing * .9:
        t = (z - crown_base) / (height - crown_base)
        if kind == 'pine':
            reach = p['reach'] * (.35 + .65 * math.sin(math.pi * t) ** .6) * (.85 + plant.random() * .3)
        elif kind == 'larch':
            reach = p['reach'] * ((1 - t) ** .85 * .9 + .1) * (.85 + plant.random() * .3)
        else:
            reach = p['reach'] * ((1 - t) ** .9 + .06) * (.88 + plant.random() * .24)
        count = max(3, round(p['branches'] * (1 - .45 * t)))
        for i in range(count):
            a = i * math.tau / count + whorl * .9 + plant.random() * .3
            start = (0, 0, z + plant.random() * spacing * .3)
            droop = p.get('droop', -.2)
            mid = (math.cos(a) * reach * .6, math.sin(a) * reach * .6, start[2] + droop * reach * .7)
            tip = (math.cos(a) * reach, math.sin(a) * reach, start[2] + droop * reach * .55 + p.get('upturn', .08) * reach)
            limb = radius * .34 * (1 - t * .6)
            limb_bark = p.get('limb_bark', bark)
            plant.stem(start, mid, limb, limb * .5, limb_bark)
            plant.stem(mid, tip, limb * .5, limb * .15, limb_bark)
            if kind == 'pine':
                # Needle bundles brush outward from the end of each limb.
                for cluster in range(p.get('clusters', 3)):
                    centre = mix(mid, tip, .3 + cluster * .35)
                    for n in range(p.get('bundle', 6)):
                        b = a + (n - 2.5) * .35 + plant.random() * .3
                        length = tuft_size * (1.4 + plant.random() * .5)
                        c = (centre[0] + math.cos(b) * length * .5, centre[1] + math.sin(b) * length * .5, centre[2] + (plant.random() - .3) * length * .5)
                        plant.tuft(c, tuft_size, plant.pick(needles), stretch=2.6, rotation=(plant.random() * .8 - .4, plant.random() * .8 - .4, b))
            else:
                # Side branchlets with needle tufts along branch and branchlets.
                steps = p.get('tufts', 5)
                for n in range(1, steps + 1):
                    f = n / (steps + 1)
                    point = mix(start, mid, f * 2) if f < .5 else mix(mid, tip, (f - .5) * 2)
                    for _ in range(p.get('density', 2)):
                        plant.tuft((point[0] + (plant.random() - .5) * tuft_size * .9, point[1] + (plant.random() - .5) * tuft_size * .9, point[2] + (plant.random() - .45) * tuft_size * .7),
                                   tuft_size * (.8 + plant.random() * .5), plant.pick(needles), stretch=p.get('stretch', 1.3))
                    if n % 2 == 0 and f > .15:
                        for side in (-1, 1):
                            b = a + side * (1.0 + plant.random() * .5)
                            length = reach * p.get('branchlet', .32) * (1 - f * .5)
                            end = (point[0] + math.cos(b) * length, point[1] + math.sin(b) * length, point[2] + droop * length * .6)
                            plant.stem(point, end, limb * .25, limb * .08, bark, 3)
                            for m in range(1, 4):
                                q = mix(point, end, m / 3.5)
                                plant.tuft(q, tuft_size * (.7 + plant.random() * .5), plant.pick(needles), stretch=p.get('stretch', 1.3))
            if kind != 'pine':
                plant.tuft(tip, tuft_size * .9, plant.pick(needles), stretch=p.get('stretch', 1.3))
        whorl += 1
        z += spacing
    # Leader: a short spike of foliage at the very top.
    plant.stem((0, 0, height - spacing * .9), (0, 0, height + spacing * .25), radius * .08, radius * .02, bark, 4)
    for n in range(p.get('leader', 6)):
        f = n / p.get('leader', 6)
        plant.tuft((0, 0, height - spacing * .8 + f * spacing * 1.05), tuft_size * (.9 - f * .4), plant.pick(needles), stretch=1.2 if kind != 'pine' else 2.4)


# ---------------------------------------------------------------------------
# Shrubs, hedges, ground cover and grasses
# ---------------------------------------------------------------------------
def shrub(plant, p, origin=(0, 0), scale=1.0):
    height = p['height'] * scale
    spread = p['spread'] * scale
    arch = p.get('arch', .4)
    bark = p['bark']
    greens = p['greens']
    accent = p.get('accent')
    for i in range(p['stems']):
        a = i * GOLDEN + plant.random() * .4
        base = (origin[0] + math.cos(a) * spread * .12, origin[1] + math.sin(a) * spread * .12, .01)
        reach = spread * (.5 + plant.random() * .5)
        top = height * (.62 + plant.random() * .38)
        tip = (origin[0] + math.cos(a) * reach, origin[1] + math.sin(a) * reach, top * (1 - arch * .35))
        mid = (origin[0] + math.cos(a) * reach * (.45 - arch * .15), origin[1] + math.sin(a) * reach * (.45 - arch * .15), top * (.55 + arch * .35))
        radius = p.get('stem_radius', .018) * scale
        plant.stem(base, mid, radius, radius * .6, bark)
        plant.stem(mid, tip, radius * .6, radius * .2, bark)
        leaf_size = p['leaf_size'] * scale
        for n in range(1, p.get('leaves', 5) + 1):
            f = n / (p.get('leaves', 5) + 1)
            q = mix(base, mid, f * 2) if f < .5 else mix(mid, tip, (f - .5) * 2)
            if f < p.get('bare', .25):
                continue
            for k in range(p.get('pairs', 3)):
                side = -1 if k % 2 else 1
                plant.leaf(q, a + side * (.8 + plant.random() * .7) + (k // 2) * 1.2, leaf_size * (.8 + plant.random() * .5), leaf_size * p.get('leaf_width', .35), (plant.random() - .3 + (k // 2) * .4) * leaf_size, plant.pick(greens, i + n + k))
        plant.spray(tip, p.get('spray_radius', .24) * scale, p.get('spray_height', .3) * scale, p.get('twigs', 5), leaf_size, greens, bark,
                    p.get('leaf_width', .35), p.get('spray_leaves', 5), .006 * scale, accent, p.get('pairs', 3))
        if accent and p.get('stem_accent', 0) > plant.random():
            plant.accent(mix(mid, tip, .5 + plant.random() * .5), accent)


def hedge_row(plant, p):
    """Informal hedge: a row of overlapping clumps along x."""
    for k in range(p['clumps']):
        x = (k - (p['clumps'] - 1) / 2) * p['pitch']
        shrub(plant, p, origin=(x, (plant.random() - .5) * .12), scale=.92 + plant.random() * .16)


def clipped_hedge(plant, p):
    """Formal clipped hedge: dense leaf tufts on a slightly irregular box, a
    dark core so it never reads see-through, and bare stems at the base."""
    length, depth, height = p['length'], p['depth'], p['height']
    foot = p.get('foot', .18)
    core = plant.colour(p['core'])
    hx, hy = length / 2 - .04, depth / 2 - .04
    corners = [(sx * hx, sy * hy, zz) for zz in (foot + .02, height - .05) for sy in (-1, 1) for sx in (-1, 1)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    for i0, i1, i2, i3 in faces:
        plant.foliage.triangle(corners[i0], corners[i1], corners[i2], core)
        plant.foliage.triangle(corners[i0], corners[i2], corners[i3], core)
    for k in range(int(length / .28)):
        x = -length / 2 + .14 + k * .28 + (plant.random() - .5) * .08
        plant.stem((x, (plant.random() - .5) * depth * .5, 0), (x * .96, (plant.random() - .5) * depth * .4, foot + .12), .022, .012, p['bark'], 5)
    pitch = p.get('pitch', .1)
    size = p['tuft_size']
    greens = p['greens']

    def skin(point):
        plant.tuft(point, size * (.8 + plant.random() * .5), plant.pick(greens), stretch=1.2)

    nx, ny, nz = int(length / pitch), int(depth / pitch), int((height - foot) / pitch)
    for i in range(nx + 1):
        x = -length / 2 + i * length / nx
        for j in range(nz + 1):
            z = foot + j * (height - foot) / nz
            for sy in (-1, 1):
                skin((x + (plant.random() - .5) * pitch * .5, sy * (depth / 2 + plant.random() * .04), z + (plant.random() - .5) * pitch * .5))
        for j in range(ny + 1):
            y = -depth / 2 + j * depth / ny
            skin((x + (plant.random() - .5) * pitch * .5, y + (plant.random() - .5) * pitch * .5, height + plant.random() * .04))
    for j in range(ny + 1):
        y = -depth / 2 + j * depth / ny
        for k in range(nz + 1):
            z = foot + k * (height - foot) / nz
            for sx in (-1, 1):
                skin((sx * (length / 2 + plant.random() * .04), y + (plant.random() - .5) * pitch * .5, z + (plant.random() - .5) * pitch * .5))
    if p.get('accent'):
        for _ in range(p.get('accent_count', 20)):
            plant.accent((((plant.random() - .5) * length), (plant.random() - .5) * depth, height + .03), p['accent'])


def ground_cover(plant, p):
    """Spreading evergreen: radiating ground-hugging limbs clothed in scale tufts."""
    bark = p['bark']
    for i in range(p['stems']):
        a = i * GOLDEN + plant.random() * .3
        reach = p['spread'] * (.6 + plant.random() * .4)
        start = (0, 0, .03)
        mid = (math.cos(a) * reach * .5, math.sin(a) * reach * .5, p['height'] * (.55 + plant.random() * .3))
        tip = (math.cos(a) * reach, math.sin(a) * reach, p['height'] * (.25 + plant.random() * .3))
        plant.stem(start, mid, .02, .012, bark, 4)
        plant.stem(mid, tip, .012, .005, bark, 4)
        for n in range(1, 10):
            f = n / 10
            q = mix(start, mid, f * 2) if f < .5 else mix(mid, tip, (f - .5) * 2)
            for _ in range(2):
                plant.tuft((q[0] + (plant.random() - .5) * .08, q[1] + (plant.random() - .5) * .08, q[2] + plant.random() * .04), p['tuft_size'] * (.8 + plant.random() * .5), plant.pick(p['needles']), stretch=1.6)
            if n % 2 == 1 and f > .2:
                for side in (-1, 1):
                    b = a + side * (.9 + plant.random() * .5)
                    length = reach * .28 * (1 - f * .4)
                    end = (q[0] + math.cos(b) * length, q[1] + math.sin(b) * length, q[2] - .02 + plant.random() * .06)
                    plant.stem(q, end, .008, .003, bark, 3)
                    for m in range(1, 4):
                        plant.tuft(mix(q, end, m / 3.2), p['tuft_size'] * (.7 + plant.random() * .5), plant.pick(p['needles']), stretch=1.4)


def mound_conifer(plant, p):
    """Mounding pine: candelabra stems ending in brushes of needle bundles."""
    bark = p['bark']
    for i in range(p['stems']):
        a = i * GOLDEN + plant.random() * .4
        reach = p['spread'] * (.35 + plant.random() * .65)
        top = p['height'] * (.5 + .5 * (1 - reach / p['spread'])) * (.85 + plant.random() * .3)
        start = (math.cos(a) * .06, math.sin(a) * .06, .02)
        mid = (math.cos(a) * reach * .5, math.sin(a) * reach * .5, top * .55)
        tip = (math.cos(a) * reach, math.sin(a) * reach, top)
        plant.stem(start, mid, .03, .018, bark, 5)
        plant.stem(mid, tip, .018, .008, bark, 4)
        for cluster in range(p.get('clusters', 4)):
            centre = mix(mid, tip, .2 + cluster * (.8 / max(1, p.get('clusters', 4) - 1)))
            for n in range(p.get('bundle', 10)):
                b = plant.random() * math.tau
                length = p['tuft_size'] * (1.6 + plant.random() * .8)
                c = (centre[0] + math.cos(b) * length * .4, centre[1] + math.sin(b) * length * .4, centre[2] + plant.random() * length * .5)
                plant.tuft(c, p['tuft_size'], plant.pick(p['needles']), stretch=p.get('stretch', 4.0), rotation=(plant.random() * 1.4 - .7, plant.random() * 1.4 - .7, b))


def grass(plant, p):
    greens = p['greens']
    base_radius = p['radius']
    for i in range(p['blades']):
        a = i * GOLDEN
        r = base_radius * math.sqrt(plant.random())
        base = (math.cos(a) * r, math.sin(a) * r, 0)
        height = p['height'] * (.55 + plant.random() * .45)
        reach = p['reach'] * (.6 + plant.random() * .6)
        middle = (base[0] + math.cos(a) * reach * .32, base[1] + math.sin(a) * reach * .32, height * .77)
        tip = (base[0] + math.cos(a) * reach, base[1] + math.sin(a) * reach, height)
        w = p.get('blade_width', .009)

        def edge(q, width):
            return (q[0] - math.sin(a) * width, q[1] + math.cos(a) * width, q[2])

        left, right = edge(base, w), edge(base, -w)
        mid_left, mid_right = edge(middle, w * .75), edge(middle, -w * .75)
        colour = plant.pick(greens, i)
        plant.foliage.triangle(left, right, mid_right, colour)
        plant.foliage.triangle(left, mid_right, mid_left, colour)
        plant.foliage.triangle(mid_left, mid_right, tip, colour)
    for i in range(p.get('plumes', 0)):
        a = i * GOLDEN + .7
        r = base_radius * .6 * math.sqrt(plant.random())
        base = (math.cos(a) * r, math.sin(a) * r, 0)
        top = p['plume_height'] * (.85 + plant.random() * .15)
        lean = p.get('plume_lean', .18)
        head = (base[0] + math.cos(a) * lean, base[1] + math.sin(a) * lean, top)
        if p.get('head') == 'eyelash':
            # Blue grama: one or two combs held sideways like eyelashes.
            plant.stem(base, head, .003, .002, p['stem'], 3)
            for k in range(1 + (i % 2)):
                q = mix(base, head, 1 - k * .16)
                b = a + 1.3 + k * 2.2
                dx, dy, length = math.cos(b), math.sin(b), .034 + plant.random() * .014
                colour = plant.colour(p['plume'])
                plant.foliage.triangle(q, (q[0] + dx * length, q[1] + dy * length, q[2] + .006), (q[0] + dx * length, q[1] + dy * length, q[2] - .011), colour)
                plant.foliage.triangle(q, (q[0] + dx * length, q[1] + dy * length, q[2] - .011), (q[0], q[1], q[2] - .009), colour)
            continue
        if p.get('head') == 'spike':
            # June grass: a narrow dense spike at the top of the stem.
            plant.stem(base, head, .003, .002, p['stem'], 3)
            for k in range(6):
                q = mix(base, head, .74 + .26 * k / 5)
                plant.tuft(q, .022 * (1.1 - k * .08), plant.colour(p['plume']), stretch=1.2)
            continue
        plant.stem(base, mix(base, head, .72), .005, .003, p['stem'], 3)
        plant.accent(mix(base, head, .72), {'kind': 'plume', 'colour': p['plume'], 'size': p.get('plume_size', .05), 'count': p.get('plume_rows', 9)})


def scatter(plant, builder, params, placements):
    """Run a builder once per placement (x, y, yaw, scale) and merge the copies."""
    for x, y, yaw, scale in placements:
        wood, foliage = plant.wood, plant.foliage
        plant.wood, plant.foliage = Part('wood'), Part('foliage')
        builder(plant, params)
        c, sn = math.cos(yaw), math.sin(yaw)
        for src, dst in ((plant.wood, wood), (plant.foliage, foliage)):
            pos, nor = src.positions, src.normals
            for i in range(0, len(pos), 3):
                px, py = pos[i] * scale, pos[i + 1] * scale
                dst.positions.extend((x + px * c - py * sn, y + px * sn + py * c, pos[i + 2] * scale))
                dst.normals.extend((nor[i] * c - nor[i + 1] * sn, nor[i] * sn + nor[i + 1] * c, nor[i + 2]))
            dst.colors.extend(src.colors)
        plant.wood, plant.foliage = wood, foliage


def grass_drift(plant, p):
    """Several small bunchgrass clumps so one placement reads at site scale."""
    placements = []
    for i in range(p['clumps']):
        a = i * GOLDEN + plant.random() * .5
        r = p['drift_radius'] * math.sqrt((i + .35) / p['clumps'])
        placements.append((math.cos(a) * r, math.sin(a) * r, plant.random() * math.tau, .8 + plant.random() * .4))
    scatter(plant, grass, p, placements)


def gnarled_pine(plant, p):
    """Limber pine: short twisting trunks and long supple limbs swept leeward."""
    height, bark, wind = p['height'], p['bark'], p.get('wind', 0.0)
    for t in range(p['trunks']):
        angle = t * math.tau / p['trunks'] + .9
        top = height * (1 if t == 0 else .7 + plant.random() * .2)
        lean = p['lean'] * (.5 if t == 0 else 1)
        segs = 7
        pts = []
        for i in range(segs + 1):
            f = i / segs
            out = (.1 if t else 0) + lean * top * f ** 1.2
            pts.append((math.cos(angle) * out + math.sin(f * 5 + t * 2) * .06 * top * f,
                        math.sin(angle) * out + math.cos(f * 4 + t) * .06 * top * f, top * f))
        r0 = p['trunk_radius'] * (1 if t == 0 else .7)
        plant.path(pts, [r0 * (1 - .85 * (i / segs) ** .9) for i in range(segs + 1)], bark, 6)
        limbs = p['limbs']
        for i in range(limbs):
            f = .3 + .7 * i / limbs
            k = min(segs - 1, int(f * segs))
            start = mix(pts[k], pts[k + 1], f * segs - k)
            direction = i * GOLDEN + t * 1.3 + plant.random() * .5
            reach = p['reach'] * (.55 + plant.random() * .45) * (1.15 - f * .5) * (1 + .45 * math.cos(direction - wind))
            mid = (start[0] + math.cos(direction) * reach * .5, start[1] + math.sin(direction) * reach * .5, start[2] + reach * (.05 + plant.random() * .2))
            tip = (start[0] + math.cos(direction) * reach, start[1] + math.sin(direction) * reach, start[2] + reach * (.2 + plant.random() * .35))
            limb = r0 * .3 * (1.1 - f * .6)
            plant.stem(start, mid, limb, limb * .6, bark)
            plant.stem(mid, tip, limb * .6, limb * .22, bark)
            clusters = p.get('clusters', 4)
            for cluster in range(clusters):
                centre = mix(mid, tip, .15 + cluster * (.95 / clusters))
                for n in range(p.get('bundle', 8)):
                    b = plant.random() * math.tau
                    length = p['tuft_size'] * (1.5 + plant.random() * .7)
                    c = (centre[0] + math.cos(b) * length * .4, centre[1] + math.sin(b) * length * .4, centre[2] + (plant.random() - .2) * length * .5)
                    plant.tuft(c, p['tuft_size'], plant.pick(p['needles']), stretch=3.0, rotation=(plant.random() * 1.2 - .6, plant.random() * 1.2 - .6, b))
        for n in range(p.get('bundle', 8) * 2):
            b = plant.random() * math.tau
            plant.tuft((pts[-1][0] + math.cos(b) * .2, pts[-1][1] + math.sin(b) * .2, top + plant.random() * .25), p['tuft_size'], plant.pick(p['needles']),
                       stretch=3.0, rotation=(plant.random() * 1.2 - .6, plant.random() * 1.2 - .6, b))


def mat(plant, p):
    """Bearberry: trailing woody stems clothed in small evergreen leaves."""
    segs = 5
    for i in range(p['stems']):
        a = i * GOLDEN + plant.random() * .4
        reach = p['spread'] * (.25 + plant.random() * .75)
        wander = plant.random() * 2.4 - 1.2
        pts = [(0, 0, .02)]
        for k in range(1, segs + 1):
            f = k / segs
            ang = a + wander * f
            pts.append((math.cos(ang) * reach * f, math.sin(ang) * reach * f, p['height'] * (.25 + .5 * math.sin(f * math.pi)) * (.6 + plant.random() * .5)))
        plant.path(pts, [.006 * (1 - .7 * k / segs) for k in range(segs + 1)], p['bark'], 3)
        for k in range(segs):
            count = p.get('leaves', 3)
            for n in range(count):
                q = mix(pts[k], pts[k + 1], (n + .5) / count)
                for side in (-1, 1):
                    plant.leaf(q, a + side * (1.0 + plant.random() * .6), p['leaf_size'] * (.8 + plant.random() * .4), p['leaf_size'] * .45,
                               p['leaf_size'] * (.2 + plant.random() * .5), plant.pick(p['greens'], k + n))
            if plant.random() < p.get('berry_rate', .3):
                q = mix(pts[k], pts[k + 1], plant.random())
                for _ in range(3):
                    plant.tuft((q[0] + (plant.random() - .5) * .03, q[1] + (plant.random() - .5) * .03, q[2] + .012), .016, plant.colour(p['berry']))


def forb_head(plant, p, base, top, bearing, s):
    kind, size = p['head'], p.get('flower_size', .03) * s
    petals = p.get('petals', [])
    if kind == 'crocus':
        for j in range(6):
            plant.leaf(top, j * math.tau / 6 + bearing, size, size * .4, size * .95, plant.pick(petals, j))
        plant.tuft((top[0], top[1], top[2] + size * .35), size * .4, plant.colour(p['centre']))
    elif kind == 'daisy':
        rays = p.get('rays', 9)
        for j in range(rays):
            a = j * math.tau / rays + bearing
            plant.leaf(top, a, size, size * .3, size * .08, plant.colour(petals[0]))
            plant.leaf((top[0], top[1], top[2] + size * .04), a + .12, size * .58, size * .3, size * .1, plant.colour(petals[1]))
        plant.tuft((top[0], top[1], top[2] + size * .14), size * .5, plant.colour(p['centre']))
        plant.tuft((top[0], top[1], top[2] + size * .1), size * .5, plant.colour(p['centre']), rotation=(0, 0, bearing))
    elif kind == 'pom':
        for j in range(8):
            plant.leaf(top, j * math.tau / 8 + bearing, size, size * .2, size * (.15 + .6 * plant.random()), plant.pick(petals, j))
        for j in range(3):
            plant.tuft((top[0], top[1], top[2] + size * (.2 + j * .12)), size * .7, plant.pick(petals, j))
    elif kind == 'spire':
        rows = p.get('rows', 10)
        for j in range(rows):
            f = j / rows
            q = mix(base, top, .52 + .48 * f)
            bud = f > .75
            for side in range(3 if not bud else 2):
                a = j * GOLDEN + side * math.tau / 3
                plant.leaf(q, a, size * (1 - .55 * f), size * (.5 if not bud else .25), size * .25, plant.colour(p['bud']) if bud else plant.pick(petals, j + side))
    elif kind == 'plume':
        for branch, spread in ((0, 1), (.95, .7), (-.95, .7)):
            direction = bearing + branch
            for j in range(p.get('rows', 7)):
                f = j / p.get('rows', 7)
                q = (top[0] + math.cos(direction) * f * size * 4.2 * spread, top[1] + math.sin(direction) * f * size * 4.2 * spread,
                     top[2] + size * (.6 - 2.6 * f * f) * spread)
                plant.tuft(q, size * (1 - .5 * f), plant.pick(petals), stretch=1.6)
    elif kind == 'smoke':
        for j in range(3):
            a = bearing + j * math.tau / 3
            bud = (top[0] + math.cos(a) * size * 1.3, top[1] + math.sin(a) * size * 1.3, top[2] - size * .5)
            plant.stem(top, bud, .002, .0015, p['stem'], 3)
            plant.tuft(bud, size * .8, plant.pick(petals, j))
            if plant.random() < .55:
                for w in range(5):
                    plant.leaf(bud, a + w * 1.26, size * 1.5, size * .05, size * (.8 + plant.random() * .8), plant.colour(p['wisp']))
    elif kind == 'flax':
        fork = mix(base, top, .8)
        for j in range(3):
            a = bearing + j * math.tau / 3
            end = (top[0] + math.cos(a) * size * 2.2, top[1] + math.sin(a) * size * 2.2, top[2] + (plant.random() - .3) * size * 2)
            plant.stem(fork, end, .0018, .0012, p['stem'], 3)
            for k in range(5):
                plant.leaf(end, k * math.tau / 5 + a, size, size * .5, size * .18, plant.pick(petals, j + k))
            plant.tuft((end[0], end[1], end[2] + size * .08), size * .3, plant.colour(p['centre']))
    elif kind == 'sage':
        for j in range(7):
            q = mix(base, top, .45 + .55 * j / 6)
            plant.tuft(q, size * (1 - j * .07), plant.colour(p['centre']))
    else:
        raise ValueError(kind)


def forb_drift(plant, p):
    """A drift of small flowering plants: basal leaves, leafy stems and a flower head each."""
    count, radius = p['plants'], p['radius']
    for i in range(count):
        a = i * GOLDEN + plant.random() * .6
        r = radius * math.sqrt((i + .5) / count) * (.85 + plant.random() * .3)
        ox, oy = math.cos(a) * r, math.sin(a) * r
        s = .75 + plant.random() * .5
        for k in range(p.get('basal', 6)):
            b = k * GOLDEN + plant.random()
            length = p['basal_length'] * s * (.7 + plant.random() * .6)
            plant.leaf((ox, oy, .004), b, length, length * p.get('basal_width', .22), length * p.get('basal_lift', .45), plant.pick(p['greens'], i + k))
        for k in range(p.get('stems', 2)):
            b = k * 2.1 + plant.random() * math.tau
            h = p['height'] * s * (.75 + plant.random() * .35)
            lean = p.get('lean', .15) * h
            base = (ox + math.cos(b) * .012, oy + math.sin(b) * .012, 0)
            top = (ox + math.cos(b) * lean, oy + math.sin(b) * lean, h)
            radius_stem = p.get('stem_radius', .004)
            plant.stem(base, top, radius_stem, radius_stem * .5, p['stem'], 3)
            leaves = p.get('stem_leaves', 0)
            for m in range(1, leaves + 1):
                q = mix(base, top, m / (leaves + 1.5))
                for side in (0, math.pi):
                    plant.leaf(q, b + m * 1.9 + side, p['leaf_size'] * s, p['leaf_size'] * s * p.get('leaf_width', .25), p['leaf_size'] * s * .25, plant.pick(p['greens'], m))
            forb_head(plant, p, base, top, b, s)


# ---------------------------------------------------------------------------
# Species catalogue
# ---------------------------------------------------------------------------
TREE = {'category': 'Trees', 'kind': 'tree', 'color': '#76a65c'}
PLANT = {'category': 'Planting', 'kind': 'object', 'color': '#6c8072'}

SPECIES = [
    # --- deciduous trees ---------------------------------------------------
    dict(slug='trembling-aspen', label='Trembling aspen', **TREE, seed=1101, builder=deciduous,
         description=f'Populus tremuloides · Alberta native with pale bark and a light, open crown. {TREE_NOTE}',
         params=dict(height=11, trunk_radius=.17, lean=.3, bark='#b9bcae', bark_marks='aspen', branches=14, reach=2.2, crown_base=.4, profile='oval', rise=.5,
                     spray_radius=.7, spray_height=.65, twigs=5, leaf_size=.21, leaf_width=.6, greens=LIGHT_GREENS, limb_radius=.05, leaves=6)),
    dict(slug='swedish-columnar-aspen', label='Swedish columnar aspen', **TREE, seed=1102, builder=deciduous,
         description=f'Populus tremula Erecta · narrow upright screen tree planted across Calgary. {TREE_NOTE}',
         params=dict(height=10, trunk_radius=.15, lean=.12, bark='#b4b6a9', bark_marks='aspen', branches=22, reach=.95, crown_base=.16, crown_top=.97, profile='columnar', rise=1.3,
                     spray_radius=.45, spray_height=.6, twigs=4, leaf_size=.19, leaf_width=.6, greens=LIGHT_GREENS, limb_radius=.04, sprays=2, leaves=6)),
    dict(slug='balsam-poplar', label='Balsam poplar', **TREE, seed=1103, builder=deciduous,
         description=f'Populus balsamifera · tall river-valley native with coarse ascending limbs. {TREE_NOTE}',
         params=dict(height=16, trunk_radius=.32, lean=.4, bark='#6f655a', branches=16, reach=3.8, crown_base=.36, profile='oval', rise=.7,
                     spray_radius=1.1, spray_height=1.0, twigs=6, leaf_size=.36, leaf_width=.5, greens=GREENS, limb_radius=.075, leaves=5)),
    dict(slug='paper-birch', label='Paper birch', **TREE, seed=1104, builder=deciduous,
         description=f'Betula papyrifera · white-barked native, often multi-stem, with fine drooping twigs. {TREE_NOTE}',
         params=dict(height=10, trunk_radius=.14, trunks=3, trunk_spread=.16, lean=.25, sway=.08, bark='#e3e1d6', bark_marks='birch', branches=18, reach=2.3, crown_base=.4,
                     profile='oval', rise=.35, droop=.3, spray_radius=.75, spray_height=.5, twigs=5, leaf_size=.21, leaf_width=.5, greens=LIGHT_GREENS, limb_radius=.045, leaves=5)),
    dict(slug='green-ash', label='Green ash', **TREE, seed=1105, builder=deciduous,
         description=f'Fraxinus pennsylvanica · hardy boulevard shade tree with a rounded crown. {TREE_NOTE}',
         params=dict(height=12, trunk_radius=.26, lean=.3, bark='#7a7268', branches=16, reach=3.6, crown_base=.34, profile='round', rise=.45,
                     spray_radius=1.05, spray_height=.85, twigs=6, leaf_size=.34, leaf_width=.35, greens=GREENS, limb_radius=.07, leaves=5)),
    dict(slug='bur-oak', label='Bur oak', **TREE, seed=1106, builder=deciduous,
         description=f'Quercus macrocarpa · slow, broad prairie oak with heavy spreading limbs. {TREE_NOTE}',
         params=dict(height=9.5, trunk_radius=.3, lean=.25, bark='#55493f', branches=15, reach=4.2, crown_base=.3, profile='spreading', rise=.38,
                     spray_radius=1.15, spray_height=.9, twigs=6, leaf_size=.35, leaf_width=.45, greens=DARK_GREENS, limb_radius=.095, leaves=5)),
    dict(slug='manitoba-maple', label='Manitoba maple', **TREE, seed=1107, builder=deciduous,
         description=f'Acer negundo · fast, wide, often multi-stem shelterbelt maple. {TREE_NOTE}',
         params=dict(height=10, trunk_radius=.2, trunks=2, trunk_spread=.22, lean=.45, bark='#6c655b', branches=16, reach=3.8, crown_base=.28, profile='spreading', rise=.4,
                     spray_radius=1.05, spray_height=.85, twigs=6, leaf_size=.34, leaf_width=.42, greens=GREENS, limb_radius=.07, leaves=5)),
    dict(slug='laurel-leaf-willow', label='Laurel leaf willow', **TREE, seed=1108, builder=deciduous,
         description=f'Salix pentandra · dense glossy rounded crown common in older Calgary neighbourhoods. {TREE_NOTE}',
         params=dict(height=12, trunk_radius=.34, lean=.3, bark='#6b6358', branches=16, reach=4.6, crown_base=.22, crown_top=.9, profile='round', rise=.3, droop=.25,
                     spray_radius=1.2, spray_height=1.0, twigs=6, leaf_size=.36, leaf_width=.24, greens=['#5f7a4a', '#73905a', '#4e6a40', '#86a068'], limb_radius=.085, leaves=5)),
    dict(slug='schubert-chokecherry', label='Schubert chokecherry', **TREE, seed=1109, builder=deciduous,
         description=f'Prunus virginiana Schubert · small tree whose leaves turn deep purple by summer. {TREE_NOTE}',
         params=dict(height=6, trunk_radius=.12, lean=.25, bark='#4c413b', branches=13, reach=1.9, crown_base=.36, profile='round', rise=.45,
                     spray_radius=.65, spray_height=.6, twigs=5, leaf_size=.21, leaf_width=.45, greens=PURPLE_LEAF, limb_radius=.05, top_spray=True, leaves=6)),
    dict(slug='showy-mountain-ash', label='Showy mountain ash', **TREE, seed=1110, builder=deciduous,
         description=f'Sorbus decora · compact ornamental with orange-red berry clusters. {TREE_NOTE}',
         params=dict(height=6.5, trunk_radius=.12, lean=.2, bark='#776d62', branches=13, reach=1.9, crown_base=.38, profile='oval', rise=.55,
                     spray_radius=.62, spray_height=.65, twigs=5, leaf_size=.21, leaf_width=.28, greens=GREENS, limb_radius=.045, leaves=6,
                     accent=dict(kind='berry', colour='#d4552c', size=.075, count=5, rate=.45, winter='#b8442a'))),
    dict(slug='amur-cherry', label='Amur cherry', **TREE, seed=1111, builder=deciduous,
         description=f'Prunus maackii · multi-stem ornamental with glossy copper-amber bark. {TREE_NOTE}',
         params=dict(height=6.5, trunk_radius=.11, trunks=3, trunk_spread=.14, lean=.22, bark='#a26b3c', branches=15, reach=2.0, crown_base=.4, profile='round', rise=.5,
                     spray_radius=.65, spray_height=.6, twigs=5, leaf_size=.21, leaf_width=.45, greens=GREENS, limb_radius=.045, leaves=6)),
    dict(slug='plains-cottonwood', label='Plains cottonwood', **TREE, seed=1112, builder=deciduous,
         description=f'Populus deltoides · massive river-flat native with furrowed bark and a broad crown. {TREE_NOTE}',
         params=dict(height=18, trunk_radius=.5, lean=.5, bark='#6a6257', bark_marks='furrow', branches=15, reach=6.0, crown_base=.3, profile='spreading', rise=.55,
                     spray_radius=1.5, spray_height=1.2, twigs=6, leaf_size=.44, leaf_width=.55, greens=['#6f8a52', '#84a060', '#5c7745', '#97b06e'], limb_radius=.085, leaves=5)),
    dict(slug='brandon-elm', label='Brandon elm', **TREE, seed=1113, builder=deciduous,
         description=f'Ulmus americana Brandon · vase-shaped prairie elm that arches over Calgary boulevards. {TREE_NOTE}',
         params=dict(height=12, trunk_radius=.3, lean=.2, bark='#5f574e', bark_marks='furrow', branches=15, reach=5.4, crown_base=.36, crown_top=.7, profile='vase', rise=1.35,
                     droop=.5, spray_radius=1.2, spray_height=.9, twigs=6, leaf_size=.33, leaf_width=.4, greens=GREENS, limb_radius=.075, leaves=5)),
    dict(slug='littleleaf-linden', label='Littleleaf linden', **TREE, seed=1114, builder=deciduous,
         description=f'Tilia cordata · dense, neatly pyramidal street tree with small heart-shaped leaves. {TREE_NOTE}',
         params=dict(height=11, trunk_radius=.24, lean=.12, bark='#6b665d', branches=17, reach=3.3, crown_base=.26, profile='oval', rise=.4,
                     spray_radius=.95, spray_height=.8, twigs=5, leaf_size=.29, leaf_width=.55, greens=['#4f6e45', '#5f7f52', '#436239', '#6f8f5f'], limb_radius=.065, leaves=5)),
    dict(slug='flowering-crabapple', label='Flowering crabapple', **TREE, seed=1115, builder=deciduous,
         description=f'Malus · small rounded yard tree covered in pink spring blossom. {TREE_NOTE}',
         params=dict(height=5.5, trunk_radius=.13, lean=.2, bark='#5b4c43', branches=13, reach=2.3, crown_base=.32, profile='round', rise=.35,
                     spray_radius=.62, spray_height=.5, twigs=5, leaf_size=.19, leaf_width=.45, greens=['#566f47', '#6a8457', '#48613d', '#7b9566'], limb_radius=.05, leaves=5,
                     accent=dict(kind='blossom', colour='#e58fae', alt='#f3c1d2', size=.13, count=5, rate=.9, winter='#7a2a26'))),
    dict(slug='japanese-tree-lilac', label='Japanese tree lilac', **TREE, seed=1116, builder=deciduous,
         description=f'Syringa reticulata · compact street tree with cherry-like bark and creamy June bloom. {TREE_NOTE}',
         params=dict(height=7.5, trunk_radius=.15, lean=.2, bark='#6a4a3c', bark_marks='lenticel', branches=13, reach=2.4, crown_base=.34, profile='oval', rise=.5,
                     spray_radius=.7, spray_height=.6, twigs=5, leaf_size=.23, leaf_width=.5, greens=DARK_GREENS, limb_radius=.05, leaves=5,
                     accent=dict(kind='panicle', colour='#f4f0dc', size=.14, count=4, rate=.3, winter='#8a7355'))),
    # --- conifers -----------------------------------------------------------
    dict(slug='white-spruce', label='White spruce', **TREE, seed=1201, builder=conifer,
         description=f'Picea glauca · Alberta native evergreen with soft drooping tiers. {TREE_NOTE}',
         params=dict(kind='spruce', height=14, trunk_radius=.26, crown_base=.07, whorl_spacing=.7, branches=6, reach=2.6, droop=-.22, upturn=.1,
                     tuft_size=.27, tufts=4, branchlet=.34, needles=SPRUCE, bark='#5b5048', stretch=1.5, density=2)),
    dict(slug='colorado-blue-spruce', label='Colorado blue spruce', **TREE, seed=1202, builder=conifer,
         description=f'Picea pungens · stiff silver-blue tiers; the classic Calgary yard evergreen. {TREE_NOTE}',
         params=dict(kind='spruce', height=10.5, trunk_radius=.22, crown_base=.06, whorl_spacing=.6, branches=6, reach=2.4, droop=-.06, upturn=.03,
                     tuft_size=.26, tufts=4, branchlet=.36, needles=BLUE_SPRUCE, bark='#5a4f47', stretch=1.5, density=2)),
    dict(slug='lodgepole-pine', label='Lodgepole pine', **TREE, seed=1203, builder=conifer,
         description=f'Pinus contorta · Alberta\'s provincial tree: tall clean trunk, narrow high crown. {TREE_NOTE}',
         params=dict(kind='pine', height=15, trunk_radius=.22, crown_base=.42, whorl_spacing=.75, branches=6, reach=1.8, droop=.22, upturn=.1,
                     tuft_size=.2, clusters=5, bundle=9, needles=DARK_GREENS, bark='#8a5d3f', leader=5)),
    dict(slug='siberian-larch', label='Siberian larch', **TREE, seed=1204, builder=conifer,
         description=f'Larix sibirica · soft open conifer, bright green in spring and gold in autumn. {TREE_NOTE}',
         params=dict(kind='larch', height=13, trunk_radius=.22, crown_base=.12, whorl_spacing=.66, branches=5, reach=2.4, droop=-.12, upturn=.06,
                     tuft_size=.2, tufts=5, branchlet=.3, needles=LARCH, bark='#6d6052', stretch=1.2, density=2)),
    dict(slug='scots-pine', label='Scots pine', **TREE, seed=1205, builder=conifer,
         description=f'Pinus sylvestris · orange-barked pine with an irregular blue-green crown held high. {TREE_NOTE}',
         params=dict(kind='pine', height=12, trunk_radius=.24, crown_base=.5, whorl_spacing=.7, branches=6, reach=2.7, droop=.3, upturn=.12,
                     tuft_size=.23, clusters=5, bundle=12, needles=PINE_BLUE, bark='#6b5648', upper_bark='#b9774a', limb_bark='#8f6a4e', leader=6)),
    dict(slug='douglas-fir', label='Douglas fir', **TREE, seed=1206, builder=conifer,
         description=f'Pseudotsuga menziesii · tall dark native of Bow valley slopes with furrowed bark. {TREE_NOTE}',
         params=dict(kind='spruce', height=18, trunk_radius=.38, crown_base=.22, whorl_spacing=.85, branches=6, reach=3.4, droop=-.3, upturn=.16,
                     tuft_size=.3, tufts=4, branchlet=.36, needles=FIR, bark='#4f443b', stretch=1.5, density=2)),
    dict(slug='limber-pine', label='Limber pine', **TREE, seed=1207, builder=gnarled_pine,
         description=f'Pinus flexilis · gnarled, wind-shaped foothills pine of dry ridges and escarpments. {TREE_NOTE}',
         params=dict(height=6.5, trunks=2, lean=.22, trunk_radius=.26, limbs=13, reach=2.6, clusters=6, bundle=14, tuft_size=.13, needles=LIMBER, bark='#5d554c', wind=.6)),
    # --- shrubs and hedges --------------------------------------------------
    dict(slug='saskatoon', label='Saskatoon berry', **PLANT, seed=1301, builder=shrub,
         description=f'Amelanchier alnifolia · upright native shrub with round leaves and purple berries. {SHRUB_NOTE}',
         params=dict(height=2.6, spread=1.1, stems=12, arch=.3, stem_radius=.02, leaf_size=.13, leaf_width=.6, leaves=8, greens=GREENS, bark='#6b6058',
                     spray_radius=.3, spray_height=.32, twigs=4, accent=dict(kind='berry', colour='#4a2a52', size=.045, count=5, rate=.5))),
    dict(slug='wolf-willow', label='Wolf willow', **PLANT, seed=1302, builder=shrub,
         description=f'Elaeagnus commutata · silverberry; suckering prairie native with silver-grey leaves. {SHRUB_NOTE}',
         params=dict(height=2.0, spread=.9, stems=15, arch=.15, stem_radius=.014, leaf_size=.13, leaf_width=.24, leaves=9, greens=SILVER, bark='#7c7462',
                     spray_radius=.22, spray_height=.3, twigs=4, bare=.15)),
    dict(slug='common-lilac', label='Common lilac', **PLANT, seed=1303, builder=shrub,
         description=f'Syringa vulgaris · heart-leaved hedge shrub with fragrant purple panicles in June. {SHRUB_NOTE}',
         params=dict(height=3.0, spread=1.3, stems=12, arch=.3, stem_radius=.024, leaf_size=.16, leaf_width=.6, leaves=7, greens=GREENS, bark='#6b6358',
                     spray_radius=.32, spray_height=.34, twigs=5, accent=dict(kind='panicle', colour='#9a7cb5', size=.075, count=6, rate=.6))),
    dict(slug='caragana-hedge', label='Caragana hedge', **PLANT, seed=1304, builder=hedge_row,
         description='Caragana arborescens · 2 m section of informal shelterbelt hedge with yellow pea flowers. Repeat along an edge.',
         params=dict(clumps=5, pitch=.42, height=1.9, spread=.5, stems=5, arch=.25, stem_radius=.012, leaf_size=.095, leaf_width=.45, leaves=7, greens=LIGHT_GREENS, bark='#7a7556',
                     spray_radius=.22, spray_height=.26, twigs=3, spray_leaves=4, bare=.08, accent=dict(kind='flower', colour='#e2c640', centre='#c9a52c', size=.035, rate=.35))),
    dict(slug='cotoneaster-hedge', label='Cotoneaster hedge', **PLANT, seed=1305, builder=clipped_hedge,
         description='Cotoneaster lucidus · 2 m section of clipped Calgary boulevard hedge, 1.1 m tall. Repeat along an edge.',
         params=dict(length=2.0, depth=.65, height=1.1, foot=.16, core='#2f4330', tuft_size=.09, pitch=.1, greens=['#3f5a3c', '#4e6c47', '#5c7a52', '#36503a'], bark='#5f574c')),
    dict(slug='prickly-wild-rose', label='Prickly wild rose', **PLANT, seed=1306, builder=shrub,
         description=f'Rosa acicularis · Alberta\'s provincial flower; low arching native with pink blooms. {SHRUB_NOTE}',
         params=dict(height=1.2, spread=.7, stems=16, arch=.6, stem_radius=.009, leaf_size=.085, leaf_width=.5, leaves=8, greens=GREENS, bark='#6d5a4a',
                     spray_radius=.18, spray_height=.14, twigs=3, bare=.05, stem_accent=.5, accent=dict(kind='flower', colour='#d58aa0', centre='#e9d17a', size=.045, rate=.5))),
    dict(slug='snowberry', label='Common snowberry', **PLANT, seed=1307, builder=shrub,
         description=f'Symphoricarpos albus · twiggy native thicket shrub with white berries into winter. {SHRUB_NOTE}',
         params=dict(height=1.1, spread=.75, stems=18, arch=.45, stem_radius=.008, leaf_size=.07, leaf_width=.6, leaves=9, greens=['#6f8560', '#86997a', '#5c7350', '#98a98a'], bark='#6b6256',
                     spray_radius=.17, spray_height=.16, twigs=3, bare=.05, stem_accent=.5, accent=dict(kind='berry', colour='#ece9df', size=.03, count=4, rate=.6))),
    dict(slug='shrubby-cinquefoil', label='Shrubby cinquefoil', **PLANT, seed=1308, builder=shrub,
         description=f'Dasiphora fruticosa · potentilla; tough mounding native with yellow summer flowers. {SHRUB_NOTE}',
         params=dict(height=.85, spread=.6, stems=22, arch=.5, stem_radius=.007, leaf_size=.065, leaf_width=.35, leaves=8, greens=['#6b7f52', '#80945f', '#5a6e46', '#93a56e'], bark='#6c5b48',
                     spray_radius=.15, spray_height=.12, twigs=3, bare=.02, stem_accent=.4, accent=dict(kind='flower', colour='#e0c344', centre='#c99a2c', size=.03, rate=.6))),
    dict(slug='buffaloberry', label='Canada buffaloberry', **PLANT, seed=1309, builder=shrub,
         description=f'Shepherdia canadensis · grey-green native shrub with bright red berries. {SHRUB_NOTE}',
         params=dict(height=1.7, spread=.95, stems=13, arch=.3, stem_radius=.014, leaf_size=.1, leaf_width=.5, leaves=9, greens=['#7d8c6c', '#93a082', '#6a7a5c', '#a3ad8f'], bark='#6f6354',
                     spray_radius=.24, spray_height=.26, twigs=4, bare=.1, stem_accent=.6, accent=dict(kind='berry', colour='#c1392b', size=.032, count=5, rate=.5))),
    dict(slug='highbush-cranberry', label='Highbush cranberry', **PLANT, seed=1310, builder=shrub,
         description=f'Viburnum trilobum · tall native with lobed leaves and red berry clusters. {SHRUB_NOTE}',
         params=dict(height=2.9, spread=1.3, stems=12, arch=.35, stem_radius=.022, leaf_size=.16, leaf_width=.6, leaves=8, greens=GREENS, bark='#6b6058',
                     spray_radius=.32, spray_height=.34, twigs=5, accent=dict(kind='berry', colour='#b8332a', size=.05, count=6, rate=.5))),
    dict(slug='diabolo-ninebark', label='Diabolo ninebark', **PLANT, seed=1311, builder=shrub,
         description=f'Physocarpus opulifolius Diabolo · arching shrub with dark purple foliage and pale flower heads. {SHRUB_NOTE}',
         params=dict(height=2.1, spread=1.2, stems=14, arch=.6, stem_radius=.016, leaf_size=.13, leaf_width=.6, leaves=9, greens=PURPLE_LEAF, bark='#5a4238',
                     spray_radius=.28, spray_height=.24, twigs=4, accent=dict(kind='berry', colour='#e5d9d2', size=.04, count=5, rate=.35))),
    dict(slug='mugo-pine', label='Mugo pine', **PLANT, seed=1312, builder=mound_conifer,
         description=f'Pinus mugo · mounding dwarf pine; evergreen mass for beds and slopes. {SHRUB_NOTE}',
         params=dict(height=1.3, spread=1.1, stems=16, tuft_size=.075, bundle=10, clusters=4, stretch=4.2, needles=['#3f5a3a', '#4a6842', '#33503a', '#587a4b'], bark='#6b5444')),
    dict(slug='creeping-juniper', label='Creeping juniper', **PLANT, seed=1313, builder=ground_cover,
         description=f'Juniperus horizontalis · low spreading native evergreen ground cover. {SHRUB_NOTE}',
         params=dict(height=.42, spread=1.1, stems=12, tuft_size=.09, needles=JUNIPER, bark='#6a5a4c')),
    dict(slug='bearberry', label='Bearberry', **PLANT, seed=1314, builder=mat,
         description='Arctostaphylos uva-ursi · kinnikinnick; native evergreen mat with red berries for dry sunny slopes.',
         params=dict(stems=34, spread=.75, height=.13, leaf_size=.044, leaves=4, greens=BEARBERRY, bark='#7a4f3e', berry='#c0322b', berry_rate=.3)),
    # --- native wildflowers -------------------------------------------------
    dict(slug='prairie-crocus', label='Prairie crocus', **PLANT, seed=1501, builder=forb_drift,
         description='Pulsatilla nuttalliana · first flower of a Calgary spring; a drift of low mauve cups on fuzzy stems.',
         params=dict(plants=14, radius=.45, height=.14, stems=2, lean=.12, basal=5, basal_length=.07, basal_width=.14, basal_lift=.6, greens=['#8f9d84', '#a2ae96', '#7f8e76'],
                     stem='#98a48e', stem_radius=.004, head='crocus', flower_size=.052, petals=['#b9a6d6', '#a892cc', '#cbbbe2'], centre='#e2c648')),
    dict(slug='blanketflower', label='Blanketflower', **PLANT, seed=1502, builder=forb_drift,
         description='Gaillardia aristata · native summer daisy; red-centred yellow flowers for dry sunny beds.',
         params=dict(plants=9, radius=.55, height=.5, stems=3, lean=.2, basal=7, basal_length=.16, basal_width=.2, greens=['#72865a', '#869a68', '#62764d'],
                     stem='#7d8c5e', stem_leaves=2, leaf_size=.09, leaf_width=.22, head='daisy', flower_size=.05, rays=9, petals=['#e8b930', '#b8382a'], centre='#6e2a22')),
    dict(slug='wild-bergamot', label='Wild bergamot', **PLANT, seed=1503, builder=forb_drift,
         description='Monarda fistulosa · native bee balm; lavender pom-pom flowers that draw pollinators.',
         params=dict(plants=8, radius=.55, height=.8, stems=3, lean=.14, basal=4, basal_length=.1, basal_width=.3, greens=['#6f8560', '#82976f', '#5f7552'],
                     stem='#6f7f5c', stem_leaves=4, leaf_size=.085, leaf_width=.32, head='pom', flower_size=.058, petals=['#b79ad6', '#a586c8', '#c9b2e2'])),
    dict(slug='fireweed', label='Fireweed', **PLANT, seed=1504, builder=forb_drift,
         description='Chamaenerion angustifolium · tall magenta spires of late summer along paths and clearings.',
         params=dict(plants=8, radius=.55, height=1.3, stems=2, lean=.08, basal=0, basal_length=.1, greens=['#6c8458', '#7f9767', '#5b724a'],
                     stem='#8a5a5c', stem_radius=.006, stem_leaves=7, leaf_size=.1, leaf_width=.15, head='spire', flower_size=.045, rows=10,
                     petals=['#c84a9c', '#d766ad', '#b53a8a'], bud='#8e2f6d')),
    dict(slug='goldenrod', label='Canada goldenrod', **PLANT, seed=1505, builder=forb_drift,
         description='Solidago canadensis · arching golden plumes of early autumn; a native meadow staple.',
         params=dict(plants=8, radius=.55, height=.9, stems=2, lean=.12, basal=3, basal_length=.12, basal_width=.2, greens=['#6f8556', '#829865', '#5e7448'],
                     stem='#77875a', stem_radius=.005, stem_leaves=6, leaf_size=.09, leaf_width=.17, head='plume', flower_size=.036, rows=7,
                     petals=['#e3c132', '#d4ae26', '#eed256'])),
    dict(slug='prairie-smoke', label='Prairie smoke', **PLANT, seed=1506, builder=forb_drift,
         description='Geum triflorum · three-flowered avens; nodding rose buds that open into feathery pink plumes.',
         params=dict(plants=11, radius=.45, height=.28, stems=2, lean=.18, basal=8, basal_length=.11, basal_width=.2, basal_lift=.3, greens=['#6f8560', '#819670', '#5f7552'],
                     stem='#9a5f62', stem_radius=.003, head='smoke', flower_size=.03, petals=['#b0566b', '#c06a7d'], wisp='#dbb0bf')),
    dict(slug='wild-blue-flax', label='Wild blue flax', **PLANT, seed=1507, builder=forb_drift,
         description='Linum lewisii · airy sky-blue flowers on wiry stems; a native of dry prairie slopes.',
         params=dict(plants=8, radius=.5, height=.55, stems=4, lean=.3, basal=0, basal_length=.05, greens=['#7c8d6e', '#8e9e7e', '#6c7d60'],
                     stem='#7c8d6e', stem_radius=.0025, stem_leaves=6, leaf_size=.032, leaf_width=.14, head='flax', flower_size=.024,
                     petals=['#7fa6dc', '#6c95d2', '#93b6e4'], centre='#e8d470')),
    dict(slug='pasture-sage', label='Pasture sage', **PLANT, seed=1508, builder=forb_drift,
         description='Artemisia frigida · prairie sagewort; low silver feathery mats with slender flower stalks.',
         params=dict(plants=15, radius=.42, height=.3, stems=3, lean=.2, basal=20, basal_length=.075, basal_width=.16, basal_lift=.75, greens=SAGE_SILVER,
                     stem='#a5ab98', stem_radius=.003, stem_leaves=4, leaf_size=.032, leaf_width=.16, head='sage', flower_size=.016, centre='#b9b58a')),
    # --- grasses --------------------------------------------------------------
    dict(slug='feather-reed-grass', label='Feather reed grass', **PLANT, seed=1401, builder=grass,
         description='Calamagrostis Karl Foerster · upright ornamental grass with tan plumes; Calgary\'s go-to clump grass.',
         params=dict(blades=120, radius=.22, height=.95, reach=.3, greens=GRASS_GREENS, plumes=26, plume_height=1.6, plume_lean=.14, plume='#c9b58a', stem='#a89a74', plume_size=.05, plume_rows=9)),
    dict(slug='rough-fescue-drift', label='Rough fescue drift', **PLANT, seed=1402, builder=grass,
         description='Festuca hallii · native foothills fescue; a low blue-green drift for naturalized edges.',
         params=dict(blades=170, radius=.45, height=.5, reach=.32, blade_width=.007, greens=FESCUE, plumes=14, plume_height=.8, plume_lean=.22, plume='#c6bd9c', stem='#a39b7e', plume_size=.03, plume_rows=6)),
    dict(slug='blue-grama', label='Blue grama', **PLANT, seed=1403, builder=grass_drift,
         description='Bouteloua gracilis · low native shortgrass with eyelash seed heads; a drift for dry prairie.',
         params=dict(clumps=7, drift_radius=.45, blades=42, radius=.07, height=.22, reach=.17, blade_width=.005, greens=GRAMA, plumes=6, plume_height=.42, plume_lean=.1,
                     head='eyelash', plume='#7d6a78', stem='#a39b7e')),
    dict(slug='june-grass', label='June grass', **PLANT, seed=1404, builder=grass_drift,
         description='Koeleria macrantha · fine native bunchgrass with pale narrow spikes in early summer.',
         params=dict(clumps=7, drift_radius=.45, blades=46, radius=.06, height=.28, reach=.13, blade_width=.006, greens=JUNE, plumes=7, plume_height=.5, plume_lean=.05,
                     head='spike', plume='#cfcdb0', stem='#a8a684')),
]


def _variant(base_slug, suffix, label_suffix, note, season=None, **overrides):
    """A seasonal form shares its base species' seed, so the skeleton is the same tree."""
    base = next(s for s in SPECIES if s['slug'] == base_slug)
    latin = base['description'].split(' · ')[0]
    return dict(slug=f'{base_slug}-{suffix}', label=f'{base["label"]} · {label_suffix}', category=base['category'], kind=base['kind'], color=base['color'],
                seed=base['seed'], builder=base['builder'], season=season, params={**base['params'], **overrides},
                description=f'{latin} · {note} {TREE_NOTE}')


WINTER_BASES = ['trembling-aspen', 'swedish-columnar-aspen', 'balsam-poplar', 'paper-birch', 'green-ash', 'bur-oak', 'manitoba-maple', 'laurel-leaf-willow',
                'schubert-chokecherry', 'showy-mountain-ash', 'amur-cherry', 'plains-cottonwood', 'brandon-elm', 'littleleaf-linden', 'flowering-crabapple',
                'japanese-tree-lilac', 'siberian-larch']
SEASONAL = [
    _variant('trembling-aspen', 'autumn', 'autumn', 'the same tree in gold September leaf.', greens=AUTUMN_GOLD),
    _variant('siberian-larch', 'autumn', 'autumn', 'the same tree with needles turned gold.', needles=LARCH_GOLD),
    _variant('white-spruce', 'snow', 'snow', 'the same tree carrying fresh snow.', season='snow'),
    _variant('colorado-blue-spruce', 'snow', 'snow', 'the same tree carrying fresh snow.', season='snow'),
    *[_variant(slug, 'winter', 'winter', 'the same tree bare, for winter scenes.', season='winter') for slug in WINTER_BASES],
]
_anchor = next(i for i, s in enumerate(SPECIES) if s['slug'] == 'limber-pine') + 1
SPECIES[_anchor:_anchor] = SEASONAL


# ---------------------------------------------------------------------------
# GLB writer and registry
# ---------------------------------------------------------------------------
def to_y_up(array):
    """Z-up authoring to glTF Y-up: (x, y, z) -> (x, z, -y)."""
    out = np.empty_like(array)
    out[:, 0] = array[:, 0]
    out[:, 1] = array[:, 2]
    out[:, 2] = -array[:, 1]
    return out


def write_glb(parts, slug, generator='CityPrompt prairie foliage builder v1'):
    doc = {
        'asset': {'generator': generator, 'version': '2.0'},
        'scene': 0, 'scenes': [{'name': 'Scene', 'nodes': []}], 'nodes': [], 'meshes': [],
        'materials': [{'name': 'kit_linear_vertex_colour', 'doubleSided': True,
                       'pbrMetallicRoughness': {'metallicFactor': 0, 'roughnessFactor': 0.9}}],
        'accessors': [], 'bufferViews': [], 'buffers': [],
    }
    binary = bytearray()

    def view(data, target):
        binary.extend(b'\0' * (-len(binary) % 4))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(data), 'target': target})
        binary.extend(data)
        return len(doc['bufferViews']) - 1

    bounds_min = np.array([math.inf] * 3)
    bounds_max = np.array([-math.inf] * 3)
    triangles = 0
    if any(part.material and part.positions for part in parts):
        doc['materials'].append(GLOSS_MATERIAL)
    for part in parts:
        if not part.positions:
            continue
        positions = to_y_up(np.array(part.positions, dtype='<f4').reshape(-1, 3))
        normals = to_y_up(np.array(part.normals, dtype='<f4').reshape(-1, 3))
        colors = np.array(part.colors, dtype='<f4').reshape(-1, 3)
        count = len(positions)
        index_type, index_dtype = (5123, '<u2') if count <= 65535 else (5125, '<u4')
        indices = np.arange(count, dtype=index_dtype)
        lo, hi = positions.min(axis=0), positions.max(axis=0)
        bounds_min = np.minimum(bounds_min, lo)
        bounds_max = np.maximum(bounds_max, hi)
        first = len(doc['accessors'])
        for data, kind in ((positions, 'VEC3'), (normals, 'VEC3'), (colors, 'VEC3')):
            accessor = {'bufferView': view(data.tobytes(), 34962), 'componentType': 5126, 'count': count, 'type': kind}
            if data is positions:
                accessor['min'] = [float(v) for v in lo]
                accessor['max'] = [float(v) for v in hi]
            doc['accessors'].append(accessor)
        doc['accessors'].append({'bufferView': view(indices.tobytes(), 34963), 'componentType': index_type, 'count': count, 'type': 'SCALAR'})
        name = f'{slug.replace("-", "_")}_{part.name}'
        doc['meshes'].append({'name': name, 'primitives': [{
            'attributes': {'POSITION': first, 'NORMAL': first + 1, 'COLOR_0': first + 2}, 'indices': first + 3, 'material': part.material}]})
        doc['nodes'].append({'mesh': len(doc['meshes']) - 1, 'name': name})
        doc['scenes'][0]['nodes'].append(len(doc['nodes']) - 1)
        triangles += count // 3
    binary.extend(b'\0' * (-len(binary) % 4))
    doc['buffers'].append({'byteLength': len(binary)})
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    payload = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary))
               + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
               + struct.pack('<II', len(binary), 0x004E4942) + binary)
    return payload, bounds_min, bounds_max, triangles, len(doc['meshes'])


def build(species):
    plant = Plant(species['seed'], species.get('season'))
    species['builder'](plant, species['params'])
    return plant


def row(species, payload, lo, hi, triangles, meshes):
    size = hi - lo
    return {
        'id': PREFIX + species['slug'],
        'label': species['label'],
        'category': species['category'],
        'description': species['description'],
        'dimensions': [round(float(size[0]), 3), round(float(size[2]), 3), round(float(size[1]), 3)],
        'url': f'{URL_ROOT}/{species["slug"]}.glb',
        'color': species['color'],
        'kind': species['kind'],
        # The authored origin (trunk or clump centre) is the placement anchor; only ground the model.
        'offset': [0.0, round(-float(lo[1]), 6) + 0.0, 0.0],
        'sourceKit': KIT,
        'sourceBuilder': f'prairie:{species["builder"].__name__}' + (f':{species["season"]}' if species.get('season') else ''),
        'sha256': hashlib.sha256(payload).hexdigest(),
        'triangles': triangles,
        'meshes': meshes,
        'bytes': len(payload),
    }


def budget(species, triangles, meshes):
    limit = 14000 if species['kind'] == 'tree' else 6000
    if triangles > limit:
        raise ValueError(f'{species["slug"]} exceeds its triangle budget: {triangles} > {limit}')
    if meshes > 3:
        raise ValueError(f'{species["slug"]} uses more than three meshes')


def export(species, output):
    plant = build(species)
    payload, lo, hi, triangles, meshes = write_glb([plant.wood, plant.foliage], species['slug'])
    budget(species, triangles, meshes)
    (output / f'{species["slug"]}.glb').write_bytes(payload)
    return row(species, payload, lo, hi, triangles, meshes)


def attach_thumbnails(rows, directory):
    """Lock each reviewed card image rendered beside its GLB (render_detail_thumbnails.cjs).

    Static cards spare the panel from downloading a megabyte-size model per
    tile just to draw a preview. They are reviewed renders, never rebuilt here."""
    attached = 0
    for record in rows:
        image = Path(directory) / (Path(record['url']).stem + '.webp')
        record.pop('thumbnailUrl', None)
        record.pop('thumbnailSha256', None)
        if image.is_file():
            data = image.read_bytes()
            if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
                raise ValueError(f'{image.name} is not a WebP image')
            record['thumbnailUrl'] = record['url'][:-len('.glb')] + '.webp'
            record['thumbnailSha256'] = hashlib.sha256(data).hexdigest()
            attached += 1
    return attached


def register(rows, frontend=ROOT / 'frontend/src/features/parks/detailCatalogueExtras.json',
             backend=ROOT / 'backend/app/data/project_detail_models.json'):
    """Text-level insertion before the closing bracket; never parse-modify-dump the extras."""
    text = frontend.read_text(encoding='utf-8')
    existing = {entry['id'] for entry in json.loads(text)}
    clashes = existing & {r['id'] for r in rows}
    if clashes:
        raise ValueError(f'Catalogue already contains {sorted(clashes)}')
    allow = json.loads(backend.read_text(encoding='utf-8'))
    if {r['id'] for r in rows} & (set(allow['trees']) | set(allow['props'])):
        raise ValueError('Backend allowlist already contains one of these IDs')
    frontend.with_name(frontend.name + '.bak-detail-register').write_text(text, encoding='utf-8')
    backend.with_name(backend.name + '.bak-detail-register').write_text(json.dumps(allow, indent=2) + '\n', encoding='utf-8')
    head, bracket, tail = text.rstrip().rpartition(']')
    if not bracket or tail.strip():
        raise ValueError('Unexpected extras catalogue layout')
    body = ',\n'.join('  ' + json.dumps(r, indent=2).replace('\n', '\n  ') for r in rows)
    frontend.write_text(head.rstrip() + ',\n' + body + '\n]\n', encoding='utf-8')
    json.loads(frontend.read_text(encoding='utf-8'))
    for r in rows:
        allow['trees' if r['kind'] == 'tree' else 'props'].append(r['id'])
    backend.write_text(json.dumps(allow, indent=2) + '\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--id', action='append')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--register', action='store_true', help='Splice finished rows into the frontend extras catalogue and backend allowlist.')
    parser.add_argument('--attach-thumbnails', action='store_true', help='Record the reviewed <slug>.webp card images found beside the GLBs.')
    args = parser.parse_args(argv)
    chosen = [s for s in SPECIES if not args.id or s['slug'] in args.id]
    unknown = set(args.id or []) - {s['slug'] for s in SPECIES}
    if unknown:
        raise SystemExit(f'Unknown species: {sorted(unknown)}')
    if args.dry_run:
        print(json.dumps({'count': len(chosen), 'kit': KIT, 'species': [s['slug'] for s in chosen], 'paid_calls': 0, 'blender': False}))
        return
    if not args.output:
        parser.error('--output is required unless --dry-run')
    if args.attach_thumbnails:
        rows = json.loads((args.output / 'catalogue.json').read_text(encoding='utf-8'))
        attached = attach_thumbnails(rows, args.output)
        (args.output / 'catalogue.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'thumbnails': attached, 'rows': len(rows)}))
        return
    if args.register:
        rows = json.loads((args.output / 'catalogue.json').read_text(encoding='utf-8'))
        register(rows)
        print(json.dumps({'registered': len(rows)}))
        return
    args.output.mkdir(parents=True, exist_ok=False)
    rows = [export(species, args.output) for species in chosen]
    (args.output / 'catalogue.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'count': len(rows), 'triangles': sum(r['triangles'] for r in rows), 'bytes': sum(r['bytes'] for r in rows), 'paid_calls': 0}))


if __name__ == '__main__':
    main(sys.argv[1:])
