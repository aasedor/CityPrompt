"""Build drawable rail streets for the native street engine, in pure Python.

Three original teaching sections, each a fixed cross-section that students draw
like any other native street: pick the card, click a route with bends or
curves, and the engine repeats one fixture cycle along it.

  median_lrt   Median light-rail avenue, 34 m: ballasted double track in a fenced
               centre median, centre catenary poles, two traffic lanes each way,
               tree boulevards and sidewalks.
  lrt_row      Light-rail right-of-way, 20 m: ballasted double track on its own
               fenced corridor, side masts, a regional pathway and a drainage swale.
  hsr          High-speed line at grade, 30 m: double slab track on a low
               embankment, overhead-line masts, security fences, ditches and a
               gravel maintenance road.

    python3 tools/rail_streets/build.py --street median_lrt --output <new directory>

Writes the module GLBs, a three-cycle preview assembly for review renders, the
source recipe, the registry row, the card text and the modules' occupied bounds.
Never overwrites.

Frame: x across the street (east positive when the route runs north), y along
it, z up, metres. Module GLBs are Y-up, as glTF requires. Rails, sleepers, slabs,
wires, curbs and markings are program details, which the engine bends with the
route; poles, masts, fences, lights and trees are rigid modules, which the
engine drops near junctions and sharp bends.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'detail_catalogue'))
import build_local_foliage as foliage
from calgary_kit import Solid

GENERATOR = 'CityPrompt rail street builder v1'
BASE_LIFT = .025

# ---- track (metres) --------------------------------------------------------------------
GAUGE = 1.435                      # standard gauge, between the rail heads' inner faces
HEAD = .072                        # rail head width
RAIL_OFFSET = GAUGE / 2 + HEAD / 2  # track centre to rail centre
FOOT, FOOT_H, WEB_H = .150, .012, .160

PALETTE_SRGB = {
    'asphalt': '#4b4d50', 'path': '#57595b', 'paint': '#e6e3d8', 'paint_yellow': '#d6a62c',
    'paving': '#b8b4ab', 'edge': '#8f8b84', 'curb': '#c4bfb4', 'gutter': '#aaa69d',
    'grass': '#6e8a48', 'grass_dark': '#5b7840', 'soil': '#6b5644', 'gravel': '#9b9283',
    'ballast': '#8c8781', 'formation': '#a29a8b', 'sleeper': '#a4a19b', 'rail': '#5e534b',
    'rail_head': '#c3c6c8', 'rail_pad': '#2f3134', 'wire': '#2b2e31', 'slab': '#bdb9b1',
    'base_layer': '#a7a39a', 'trough': '#9e9b94', 'riprap': '#8b867d',
}

STEEL, GALV, BLACK, CONCRETE, PORCELAIN = '#7f878b', '#9aa0a3', '#1f2326', '#b2aea6', '#7a5a4a'
FENCE_GREEN = '#3b4a41'


def linear(hex_colour):
    return [round(v, 4) for v in foliage.srgb_to_linear(hex_colour)]


def r4(v):
    return round(float(v), 4)


# ---- program pieces ------------------------------------------------------------------------
def detail(material, x, y, width, depth, z, height=0.0):
    """A box the engine sweeps along the route. z is the box's centre height."""
    return dict(x=r4(x), y=r4(y), width=r4(width), depth=r4(depth), z=r4(z), height=r4(height), material=material)


def region(material, x0, x1, cycle, y=0.0, depth=None):
    return dict(x=r4((x0 + x1) / 2), y=r4(y), width=r4(x1 - x0), depth=r4(cycle if depth is None else depth), material=material)


class Mesh:
    """Triangles in the cycle frame, swept by the engine along the route."""

    def __init__(self):
        self.groups = {}

    def tri(self, material, a, b, c):
        group = self.groups.setdefault(material, ([], []))
        first = len(group[0]) // 3
        for p in (a, b, c):
            group[0].extend(r4(v) for v in p)
        group[1].extend((first, first + 1, first + 2))

    def quad(self, material, a, b, c, d):
        """Counter-clockwise seen from outside."""
        self.tri(material, a, b, c)
        self.tri(material, a, c, d)

    def strip(self, material, profile, cycle, end_caps=False):
        """Extrude an open cross-section profile [(x, z), ...] (left to right, upper side
        facing up) over the whole cycle."""
        y0, y1 = -cycle / 2, cycle / 2
        for (xa, za), (xb, zb) in itertools.pairwise(profile):
            self.quad(material, (xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za))
        if end_caps:
            for y, sign in ((y0, 1), (y1, -1)):
                for (xa, za), (xb, zb) in itertools.pairwise(profile):
                    corners = [(xa, y, 0.0), (xb, y, 0.0), (xb, y, zb), (xa, y, za)]
                    corners = [c for i, c in enumerate(corners) if not (i == 2 and zb < 1e-9) and not (i == 3 and za < 1e-9)]
                    if len(corners) < 3:
                        continue
                    if sign < 0:
                        corners = corners[::-1]
                    for i in range(1, len(corners) - 1):
                        self.tri(material, corners[0], corners[i], corners[i + 1])

    def program(self):
        return [dict(material=m, positions=p, indices=i) for m, (p, i) in sorted(self.groups.items())]


def ballasted_double_track(details, mesh, centres, ballast_top, cycle, sleeper_spacing=.625, sleeper_length=2.6, floor=0.0):
    """Concrete sleepers half-buried in a ballast bed, with flat-bottom rails on them."""
    half = max(abs(c) for c in centres) + sleeper_length / 2 + .15
    slope = 1.5
    toe = half + (ballast_top - floor) * slope
    mesh.strip('ballast', [(-toe, floor), (-half, ballast_top), (half, ballast_top), (toe, floor)], cycle, end_caps=True)
    sleeper_bottom, sleeper_top = ballast_top - .10, ballast_top + .06
    count = round(cycle / sleeper_spacing)
    for c in centres:
        for k in range(count):
            y = -cycle / 2 + (k + .5) * cycle / count
            details.append(detail('sleeper', c, y, sleeper_length, .24, (sleeper_bottom + sleeper_top) / 2, sleeper_top - sleeper_bottom))
        rails(details, c, sleeper_top, cycle)
    return toe, sleeper_top + FOOT_H + WEB_H


def rails(details, centre, seat, cycle):
    for side in (-1, 1):
        x = centre + side * RAIL_OFFSET
        details.append(detail('rail', x, 0, FOOT, cycle, seat + FOOT_H / 2, FOOT_H))
        details.append(detail('rail', x, 0, HEAD, cycle, seat + FOOT_H + WEB_H / 2, WEB_H))
        details.append(detail('rail_head', x, 0, HEAD - .008, cycle, seat + FOOT_H + WEB_H + .0008))


def catenary(details, centres, contact, system, cycle, dropper_ys):
    """Contact and messenger wires over each track, with droppers between them."""
    for c in centres:
        details.append(detail('wire', c, 0, .014, cycle, contact, .014))
        details.append(detail('wire', c, 0, .014, cycle, contact + system, .014))
        for y in dropper_ys:
            details.append(detail('wire', c, y, .008, .008, contact + system / 2, system))


def dashes(details, material, x, cycle, period, length, width=.10, z=.004):
    for k in range(round(cycle / period)):
        y = -cycle / 2 + (k + .5) * period
        details.append(detail(material, x, y, width, length, z))


# ---- modules -----------------------------------------------------------------------------------
def insulator(s, a, b, discs=4):
    """A short string of porcelain discs from a toward b."""
    for k in range(discs):
        t0, t1 = k / discs, (k + .55) / discs
        p0 = tuple(a[i] + (b[i] - a[i]) * t0 for i in range(3))
        p1 = tuple(a[i] + (b[i] - a[i]) * t1 for i in range(3))
        s.cyl(p0, p1, .06, PORCELAIN, sides=9)


def lrt_cantilever(s, reach, contact, messenger, mast_r):
    """Messenger support, stay and registration arm reaching toward local +x."""
    sign = 1 if reach > 0 else -1
    x0 = sign * mast_r
    s.cyl((x0, 0, messenger + .02), (reach + sign * .08, 0, messenger + .02), .032, STEEL, sides=7)
    s.cyl((x0, 0, messenger + .55), (reach * .85, 0, messenger + .06), .02, STEEL, sides=6)
    s.cyl((x0, 0, contact + .30), (reach - sign * .25, 0, contact + .12), .024, STEEL, sides=6)
    s.cyl((reach - sign * .25, 0, contact + .12), (reach, 0, contact + .02), .014, STEEL, sides=5)   # steady arm
    insulator(s, (x0 + sign * .12, 0, messenger + .02), (x0 + sign * .55, 0, messenger + .02))
    insulator(s, (x0 + sign * .12, 0, contact + .29), (x0 + sign * .5, 0, contact + .27), 3)
    s.box((reach, 0, messenger + .01), (.16, .05, .06), '#5e666a')
    s.box((reach, 0, contact + .03), (.18, .04, .04), '#5e666a')
    s.cyl((reach, 0, contact + .03), (reach, 0, messenger), .006, '#2b2e31', sides=4, cap0=False, cap1=False)


def centre_pole(median):
    """Tubular centre pole between the median tracks, twin cantilevers to both contact wires."""
    def make():
        s = Solid(61)
        s.box((0, 0, median['ballast_top'] - .02), (.7, .7, .16), CONCRETE)
        s.box((0, 0, median['ballast_top'] + .08), (.42, .42, .04), '#6d7579')
        top = median['messenger'] + .75
        s.cyl((0, 0, median['ballast_top'] + .06), (0, 0, top), .15, STEEL, r1=.10, sides=10)
        s.cyl((0, 0, top), (0, 0, top + .06), .11, STEEL, r1=.04, sides=8)
        for reach in (-median['track'], median['track']):
            lrt_cantilever(s, reach, median['contact'], median['messenger'], .12)
        return [s.body, s.gloss]
    return make


def side_mast(row):
    """Tubular side mast on the formation, its cantilever reaching over the near track (local +x)."""
    def make():
        s = Solid(62)
        s.box((0, 0, .08), (.6, .6, .16), CONCRETE)
        top = row['messenger'] + .7
        s.cyl((0, 0, .16), (0, 0, top), .15, STEEL, r1=.10, sides=10)
        s.cyl((0, 0, top), (0, 0, top + .06), .11, STEEL, r1=.04, sides=8)
        lrt_cantilever(s, row['reach'], row['contact'], row['messenger'], .12)
        return [s.body, s.gloss]
    return make


def hsr_mast(line):
    """H-section steel mast on a concrete foundation at the formation edge. Cantilever to the
    near track (local +x), a feeder wire bracket behind (local -x)."""
    def make():
        s = Solid(63)
        crest = line['formation']
        s.box((0, 0, crest - .15), (1.0, 1.0, .5), CONCRETE)
        s.box((0, 0, crest + .12), (.5, .4, .04), '#6d7579')
        top = line['feeder'] + .45
        z0, z1 = crest + .14, top
        for y in (-.13, .13):
            s.box((0, y, (z0 + z1) / 2), (.28, .022, z1 - z0), STEEL)           # flanges
        s.box((0, 0, (z0 + z1) / 2), (.016, .24, z1 - z0), STEEL)               # web
        s.box((0, 0, top + .02), (.32, .3, .04), STEEL)
        reach, contact, messenger = line['reach'], line['contact'], line['messenger']
        s.cyl((.15, 0, messenger + .75), (reach + .1, 0, messenger + .1), .035, STEEL, sides=7)    # top tube
        s.cyl((.15, 0, contact + .65), (reach + .05, 0, messenger - .02), .035, STEEL, sides=7)    # cantilever tube
        s.cyl((reach * .55, 0, messenger + .4), (reach * .55, 0, contact + .62 + (messenger - contact) * .55), .015, STEEL, sides=5)
        s.cyl((.15, 0, contact + .42), (reach - .45, 0, contact + .30), .026, STEEL, sides=6)      # registration tube
        s.cyl((reach - .45, 0, contact + .30), (reach, 0, contact + .02), .016, STEEL, sides=5)    # steady arm
        insulator(s, (.25, 0, messenger + .73), (.7, 0, messenger + .65))
        insulator(s, (.25, 0, contact + .64), (.65, 0, contact + .74))
        insulator(s, (.25, 0, contact + .42), (.62, 0, contact + .40), 3)
        s.box((reach, 0, messenger + .02), (.18, .06, .07), '#5e666a')
        s.box((reach, 0, contact + .03), (.2, .05, .05), '#5e666a')
        s.cyl((reach, 0, contact + .03), (reach, 0, messenger), .006, '#2b2e31', sides=4, cap0=False, cap1=False)
        feeder_x = -line['feeder_offset']
        s.cyl((-.15, 0, line['feeder'] + .25), (feeder_x - .05, 0, line['feeder'] + .25), .03, STEEL, sides=6)
        insulator(s, (feeder_x, 0, line['feeder'] + .22), (feeder_x, 0, line['feeder'] + .02), 3)
        s.box((0, -.2, crest + 1.6), (.2, .02, .28), '#eef0e8')                 # blank mast number plate
        return [s.body, s.gloss]
    return make


def fence_panel(height, colour, verticals, horizontals, post=.06, rails=(), seed=64, wire=.008):
    """One 2.5 m fence panel running along y, with its post at local y = -1.25."""
    def make():
        s = Solid(seed)
        length = 2.5
        foot = -length / 2 + .13                   # the post and its footing stay inside the panel's 2.5 m
        s.box((0, foot, .1), (.26, .26, .2), CONCRETE)
        s.box((0, foot, height / 2 + .02), (post, post, height + .04), colour)
        for z in rails:
            s.box((0, (foot + length / 2) / 2, z), (.04, length / 2 - foot, .04), colour)
        for k in range(1, verticals):
            y = foot + k * (length / 2 - foot) / verticals
            s.box((0, y, height / 2 + .02), (wire, wire, height - .04), colour)
        for k in range(horizontals):
            z = .08 + k * (height - .12) / max(1, horizontals - 1)
            s.box((0, (foot + length / 2) / 2, z), (wire, length / 2 - foot, wire), colour)
        return [s.body, s.gloss]
    return make


def street_light(height=9.5, reach=2.2):
    """Davit street light facing local +x, over the road."""
    def make():
        s = Solid(65)
        s.box((0, 0, .15), (.4, .4, .3), CONCRETE)
        s.cyl((0, 0, .3), (0, 0, height - .5), .11, '#5c6266', r1=.07, sides=10)
        steps = 8
        points = [(reach * math.sin(t * math.pi / 2) ** 1.6,
                   0, height - .5 + .5 * math.sin(t * math.pi)) for t in (i / steps for i in range(steps + 1))]
        for a, b in itertools.pairwise(points):
            s.cyl(a, b, .055, '#5c6266', sides=8, cap0=False, cap1=False)
        hx, hz = points[-1][0], points[-1][2]
        s.box((hx + .25, 0, hz - .03), (.7, .3, .1), '#4c5256')
        s.box((hx + .25, 0, hz - .085), (.56, .22, .012), '#f3efd9', gloss=True)
        return [s.body, s.gloss]
    return make


def pathway_light():
    def make():
        s = Solid(66)
        s.box((0, 0, .1), (.3, .3, .2), CONCRETE)
        s.cyl((0, 0, .2), (0, 0, 4.6), .06, '#3a3f43', sides=8)
        s.cyl((0, 0, 4.6), (0, 0, 4.66), .2, '#3a3f43', sides=10)
        s.cyl((0, 0, 4.66), (0, 0, 4.92), .16, '#f2eedb', sides=10, gloss=True)
        s.cyl((0, 0, 4.92), (0, 0, 5.02), .22, '#3a3f43', r1=.05, sides=10)
        return [s.body, s.gloss]
    return make


def bench():
    """A 1.8 m backed bench facing local +x."""
    def make():
        s = Solid(67)
        for y in (-.82, .82):
            s.box((0, y, .22), (.5, .07, .44), BLACK)
            s.box((-.22, y, .62), (.06, .07, .4), BLACK)
        for k in range(4):
            s.box((.18 - k * .12, 0, .45), (.1, 1.72, .035), '#8a6a48')
        for k in range(3):
            s.box((-.25, 0, .55 + k * .12), (.035, 1.72, .09), '#8a6a48')
        return [s.body, s.gloss]
    return make


def litter_bin():
    def make():
        s = Solid(68)
        s.cyl((0, 0, 0), (0, 0, .05), .3, BLACK, sides=12)
        s.cyl((0, 0, .05), (0, 0, .9), .27, '#4f5a52', sides=12)
        s.dome((0, 0, .9), (.27, .27, .12), '#3a443d', nu=12, nv=3)
        return [s.body, s.gloss]
    return make


def cabinet(width, depth, height, seed):
    """A grey trackside equipment cabinet on a concrete pad, its doors facing local +x."""
    def make():
        s = Solid(seed)
        s.box((0, 0, .06), (width + .3, depth + .3, .12), CONCRETE)
        s.box((0, 0, .12 + height / 2), (width, depth, height), '#a9aeae')
        s.box((0, 0, .12 + height + .03), (width + .08, depth + .08, .06), '#8f9595')
        for y in (-depth / 4, depth / 4):
            s.box((width / 2 + .004, y, .12 + height / 2), (.008, depth / 2 - .04, height - .12), '#9da2a2')
            for k in range(5):
                s.box((width / 2 + .01, y, .12 + height * .62 + k * .07), (.008, depth / 2 - .14, .025), '#7d8383')
        return [s.body, s.gloss]
    return make


def etcs_marker(board_z=1.6):
    """A blank blue marker board with a yellow arrow, facing local -y (approaching trains)."""
    def make():
        s = Solid(69)
        s.box((0, 0, .1), (.3, .3, .2), CONCRETE)
        s.box((0, 0, (board_z + .2) / 2 + .1), (.07, .07, board_z + .2), GALV)
        s.box((0, -.05, board_z), (.5, .03, .5), '#1d4f9a')
        s.tri((-.17, -.068, board_z - .12), (.17, -.068, board_z - .12), (0, -.068, board_z + .15), '#f2c418')
        return [s.body, s.gloss]
    return make


def tree(slug, height, reach, seed, leaves=4, twigs=4, offsets=((0.0, 0.0),)):
    def make():
        parts = []
        for k, (dx, dy) in enumerate(offsets):
            species = copy.deepcopy(next(sp for sp in foliage.SPECIES if sp['slug'] == slug))
            species['seed'] = seed + k
            species['params'].update(height=height * (1 - .08 * k), reach=reach, leaves=leaves, twigs=twigs)
            plant = foliage.build(species)
            parts += transform_parts([plant.wood, plant.foliage], dx, dy, 0.0)
        return parts
    return make


# ---- streets ---------------------------------------------------------------------------------
def median_lrt():
    width, cycle = 34.0, 40.0
    track, ballast_top = 2.3, .25                 # track centres 4.6 m, room for centre poles
    m = dict(track=track, ballast_top=ballast_top)
    sections = [('west_walk', 2.5, 'paving', 'sidewalk', 'concrete sidewalk'),
                ('west_boulevard', 2.5, 'grass', 'boulevard', 'grass boulevard with street trees'),
                ('west_road', 7.0, 'asphalt', 'travel_lane', 'asphalt, two lanes'),
                ('lrt_median', 10.0, 'ballast', 'rail_track', 'raised median with fenced ballasted double light-rail track'),
                ('east_road', 7.0, 'asphalt', 'travel_lane', 'asphalt, two lanes'),
                ('east_boulevard', 2.5, 'grass', 'boulevard', 'grass boulevard with street trees'),
                ('east_walk', 2.5, 'paving', 'sidewalk', 'concrete sidewalk')]
    regions = [region('paving', -17, -14.5, cycle), region('grass', -14.5, -12, cycle), region('asphalt', -12, -5, cycle),
               region('ballast', -5, 5, cycle), region('asphalt', 5, 12, cycle), region('grass', 12, 14.5, cycle),
               region('paving', 14.5, 17, cycle)]
    details, mesh = [], Mesh()
    _, rail_top = ballasted_double_track(details, mesh, (-track, track), ballast_top, cycle)
    m['contact'] = rail_top + 5.6                 # contact wire above the rail head
    m['messenger'] = m['contact'] + 1.0
    catenary(details, (-track, track), m['contact'], 1.0, cycle, [-17.5, -12.5, -7.5, -2.5, 2.5, 7.5, 12.5, 17.5])
    for side in (-1, 1):
        details.append(detail('curb', side * 4.875, 0, .25, cycle, .075, .15))           # median curb
        details.append(detail('gutter', side * 5.2, 0, .4, cycle, .003))
        details.append(detail('curb', side * 11.9, 0, .2, cycle, .075, .15))             # outer curb
        details.append(detail('gutter', side * 11.6, 0, .4, cycle, .003))
        dashes(details, 'paint', side * 8.5, cycle, 10.0, 3.0)                          # lane line between the two lanes
        for k in range(1, round(cycle / 1.5)):                                           # sidewalk control joints
            details.append(detail('edge', side * 15.75, -cycle / 2 + k * cycle / round(cycle / 1.5), 2.5, .012, .002))
    modules = {'centre_pole': centre_pole(m),
               'median_fence': fence_panel(1.2, BLACK, 20, 0, post=.06, rails=(.12, 1.16), seed=71, wire=.018),
               'street_light': street_light(),
               'boulevard_tree': tree('green-ash', 9.0, 2.7, 701)}
    places = []
    for y in (-10.0, 10.0):
        places.append(dict(kind='centre_pole', x=0.0, y=y, yaw=0.0))
    for side in (-1, 1):
        for k in range(16):
            places.append(dict(kind='median_fence', x=side * 4.45, y=-cycle / 2 + 1.25 + k * 2.5, yaw=0.0 if side < 0 else math.pi))
        for y in (-15, -5, 5, 15):
            places.append(dict(kind='boulevard_tree', x=side * 13.25, y=float(y), yaw=0.0))
        places.append(dict(kind='street_light', x=side * 12.6, y=0.0, yaw=0.0 if side < 0 else math.pi))
    return dict(
        id='student_median_lrt_avenue_v1', parent='light_rail_tram_avenue', title='Median LRT Avenue', width=width, cycle=cycle,
        sections=sections, regions=regions, details=details, mesh=mesh, modules=modules, placements=places,
        lane_count=4, group='transit', min_length=40, slug='light-rail-tram-avenue',
        card='An arterial with light rail in its centre median: fenced ballasted double track and catenary between two traffic lanes each way.',
        asset_description='34 m arterial: fenced ballasted double light-rail track in the median, two lanes each way, boulevards and sidewalks.',
        search=['street_pathway', 'lrt', 'light rail', 'median', 'transit', 'ctrain', 'catenary', 'arterial'],
        clear=[('west_lanes', -8.5, 6.6), ('east_lanes', 8.5, 6.6), ('west_walk', -15.75, 2.3), ('east_walk', 15.75, 2.3)],
        envelopes=[(-track, 1.65), (track, 1.65)],
        dims=m, notes=[
            'An original teaching section after the catalogue Light Rail Tram Avenue description: tracks in the centre median flanked by traffic lanes.',
            'Track centres 4.6 m, so a centre pole clears each light-rail vehicle; the contact wire is 5.6 m above the rail head.',
            'Not a City of Calgary drawing. Stations, crossings and turning lanes are not modelled; students add them.'],
    )


def lrt_row():
    width, cycle = 20.0, 40.0
    track, ballast_top = 2.0, .35
    r = dict(track=track, ballast_top=ballast_top)
    sections = [('west_verge', 1.0, 'grass', 'boulevard', 'grass verge'),
                ('regional_pathway', 3.0, 'paving', 'multi_use_pathway', 'asphalt pathway with a yellow centre line'),
                ('west_buffer', 1.5, 'grass', 'boulevard', 'grass buffer with right-of-way fence'),
                ('lrt_track_bed', 9.0, 'ballast', 'rail_track', 'ballasted double light-rail track on its own right-of-way'),
                ('east_buffer', 1.5, 'grass', 'boulevard', 'grass buffer with right-of-way fence'),
                ('east_swale', 4.0, 'grass', 'boulevard', 'grassed drainage swale with aspens')]
    regions = [region('grass', -10, -9, cycle), region('path', -9, -6, cycle), region('grass', -6, -4.5, cycle),
               region('formation', -4.5, 4.5, cycle), region('grass', 4.5, 6, cycle), region('grass', 6, 7, cycle),
               region('grass_dark', 7, 9, cycle), region('grass', 9, 10, cycle)]
    details, mesh = [], Mesh()
    _, rail_top = ballasted_double_track(details, mesh, (-track, track), ballast_top, cycle)
    r['contact'] = rail_top + 5.2
    r['messenger'] = r['contact'] + 1.1
    r['mast_x'] = 4.2
    r['reach'] = r['mast_x'] - track
    catenary(details, (-track, track), r['contact'], 1.1, cycle, [-17.5, -12.5, -7.5, -2.5, 2.5, 7.5, 12.5, 17.5])
    dashes(details, 'paint_yellow', -7.5, cycle, 10.0, 3.0)
    modules = {'side_mast': side_mast(r),
               'row_fence': fence_panel(1.8, GALV, 16, 7, post=.06, rails=(1.78,), seed=72, wire=.007),
               'pathway_light': pathway_light(), 'bench': bench(), 'litter_bin': litter_bin(),
               'aspen_clump': tree('trembling-aspen', 9.5, 1.6, 702, leaves=3, twigs=3, offsets=((0.0, 0.0), (.9, 1.1))),
               'relay_case': cabinet(.9, 1.4, 1.5, 73)}
    places = [dict(kind='side_mast', x=-r['mast_x'], y=0.0, yaw=0.0), dict(kind='side_mast', x=r['mast_x'], y=0.0, yaw=math.pi)]
    for side in (-1, 1):
        for k in range(16):
            places.append(dict(kind='row_fence', x=side * 4.75, y=-cycle / 2 + 1.25 + k * 2.5, yaw=0.0 if side < 0 else math.pi))
    places += [dict(kind='pathway_light', x=-9.5, y=-5.0, yaw=0.0), dict(kind='bench', x=-9.45, y=10.0, yaw=0.0),
               dict(kind='litter_bin', x=-9.5, y=12.4, yaw=0.0), dict(kind='aspen_clump', x=7.0, y=-13.0, yaw=0.0),
               dict(kind='aspen_clump', x=7.6, y=7.0, yaw=2.1), dict(kind='relay_case', x=5.45, y=16.0, yaw=0.0)]
    return dict(
        id='student_lrt_right_of_way_v1', parent='light_rail_tram_avenue', title='LRT Right-of-Way', width=width, cycle=cycle,
        sections=sections, regions=regions, details=details, mesh=mesh, modules=modules, placements=places,
        lane_count=0, group='transit', min_length=40, slug='light-rail-tram-avenue',
        card='Light rail on its own fenced corridor: ballasted double track, side masts and catenary, with a regional pathway alongside.',
        asset_description='20 m light-rail corridor: fenced ballasted double track, side masts, a regional pathway and a drainage swale.',
        search=['street_pathway', 'lrt', 'light rail', 'right-of-way', 'transit', 'ctrain', 'pathway', 'catenary'],
        clear=[('regional_pathway', -7.5, 2.8)],
        envelopes=[(-track, 1.65), (track, 1.65)],
        dims=r, notes=[
            'An original teaching section of light rail on its own right-of-way, as it runs beside major roads and rail corridors.',
            'Track centres 4.0 m with side masts; the contact wire is 5.2 m above the rail head.',
            'Not a City of Calgary drawing. Stations, crossings and signals beyond one relay case are not modelled.'],
    )


def hsr():
    width, cycle = 30.0, 50.0
    track = 2.4                                   # track centres 4.8 m
    crest, toe, formation = 6.5, 8.5, .8          # embankment crest and toe half-widths, height
    line = dict(track=track, formation=formation)
    sections = [('west_margin', 1.0, 'grass', 'boulevard', 'grass margin with security fence'),
                ('service_road', 3.5, 'gravel', 'shoulder', 'gravel maintenance road'),
                ('west_ditch', 2.0, 'grass', 'ditch', 'grassed drainage ditch'),
                ('hsr_track_formation', 17.0, 'slab_track', 'rail_track', 'low embankment carrying double high-speed slab track'),
                ('east_ditch', 2.0, 'grass', 'ditch', 'grassed drainage ditch'),
                ('east_margin', 4.5, 'grass', 'boulevard', 'grass margin with security fence')]
    regions = [region('grass', -15, -14, cycle), region('gravel', -14, -10.5, cycle), region('grass_dark', -10.5, -8.5, cycle),
               region('grass', -8.5, 8.5, cycle), region('grass_dark', 8.5, 10.5, cycle), region('grass', 10.5, 15, cycle)]
    details, mesh = [], Mesh()
    mesh.strip('grass', [(-toe, 0.0), (-crest, formation)], cycle, end_caps=True)
    mesh.strip('grass', [(crest, formation), (toe, 0.0)], cycle, end_caps=True)
    mesh.strip('formation', [(-crest, formation), (crest, formation)], cycle, end_caps=True)
    for side in (-1, 1):
        details.append(detail('riprap', side * 9.5, 0, .6, cycle, .004))
    base_top, slab_top = formation + .3, formation + .5
    slab_count = 8
    for c in (-track, track):
        details.append(detail('base_layer', c, 0, 3.2, cycle, (formation + base_top) / 2, base_top - formation))
        for k in range(slab_count):
            y = -cycle / 2 + (k + .5) * cycle / slab_count
            details.append(detail('slab', c, y, 2.55, cycle / slab_count - .05, (base_top + slab_top) / 2, slab_top - base_top))
        for side in (-1, 1):
            details.append(detail('rail_pad', c + side * RAIL_OFFSET, 0, .18, cycle, slab_top + .0075, .015))
        rails(details, c, slab_top + .015, cycle)
        details.append(detail('trough', (abs(c) + 2.1) * (1 if c > 0 else -1), 0, .6, cycle, formation + .1, .2))
    rail_top = slab_top + .015 + FOOT_H + WEB_H
    line.update(contact=rail_top + 5.3, messenger=rail_top + 5.3 + 1.6, mast_x=5.4, feeder_offset=.5)
    line['reach'] = line['mast_x'] - track
    line['feeder'] = line['messenger'] + 1.2
    catenary(details, (-track, track), line['contact'], 1.6, cycle, [-cycle / 2 + (k + .5) * cycle / 8 for k in range(8)])
    for side in (-1, 1):
        details.append(detail('wire', side * (line['mast_x'] + line['feeder_offset']), 0, .02, cycle, line['feeder'], .02))
    modules = {'hsr_mast': hsr_mast(line),
               'security_fence': fence_panel(2.4, FENCE_GREEN, 12, 8, post=.07, rails=(2.36,), seed=74, wire=.008),
               'trackside_cabinet': cabinet(.6, 1.0, 1.3, 75),
               'etcs_marker': etcs_marker()}
    places = [dict(kind='hsr_mast', x=-line['mast_x'], y=0.0, yaw=0.0), dict(kind='hsr_mast', x=line['mast_x'], y=0.0, yaw=math.pi)]
    for side in (-1, 1):
        for k in range(20):
            places.append(dict(kind='security_fence', x=side * 14.5, y=-cycle / 2 + 1.25 + k * 2.5, yaw=0.0 if side < 0 else math.pi))
    places += [dict(kind='trackside_cabinet', x=-5.95, y=20.0, yaw=0.0, z=formation),
               dict(kind='etcs_marker', x=-5.95, y=-15.0, yaw=0.0, z=formation),
               dict(kind='etcs_marker', x=5.95, y=15.0, yaw=math.pi, z=formation)]
    return dict(
        id='student_high_speed_rail_line_v1', parent='high_speed_rail_corridor', title='High-Speed Rail Line', width=width, cycle=cycle,
        sections=sections, regions=regions, details=details, mesh=mesh, modules=modules, placements=places,
        lane_count=0, group='transit', min_length=50, slug='high-speed-rail-corridor',
        card='A high-speed line at grade: double slab track on a low embankment, overhead-line masts, security fences and a maintenance road.',
        asset_description='30 m high-speed rail corridor: double slab track on an embankment, overhead line, fences, ditches and a service road.',
        search=['street_pathway', 'high-speed rail', 'hsr', 'rail', 'train', 'intercity', 'catenary', 'transit'],
        clear=[('service_road', -12.25, 3.3)],
        envelopes=[(-track, 2.0), (track, 2.0)],
        dims=line, notes=[
            'An original teaching section of a 300 km/h class line at grade: track centres 4.8 m, slab track, contact wire 5.3 m above the rail head and a 1.6 m system height.',
            'No level crossings exist on such lines; where students cross it with a street, a bridge or underpass is implied.',
            'Its curves are not checked against the very large radii real high-speed lines need.'],
    )


STREETS = {'median_lrt': median_lrt, 'lrt_row': lrt_row, 'hsr': hsr}


# ---- outputs ---------------------------------------------------------------------------------------
def transform_parts(parts, x, y, yaw, scale=1.0, z=0.0):
    c, s = math.cos(yaw), math.sin(yaw)
    out = []
    for part in parts:
        moved = foliage.Part(part.name)
        moved.material = part.material
        p = np.array(part.positions, dtype=float).reshape(-1, 3) * scale
        n = np.array(part.normals, dtype=float).reshape(-1, 3)
        p[:, 0], p[:, 1] = p[:, 0] * c - p[:, 1] * s + x, p[:, 0] * s + p[:, 1] * c + y
        p[:, 2] += z
        n[:, 0], n[:, 1] = n[:, 0] * c - n[:, 1] * s, n[:, 0] * s + n[:, 1] * c
        moved.positions, moved.normals, moved.colors = p.ravel().tolist(), n.ravel().tolist(), list(part.colors)
        out.append(moved)
    return out


def program(spec):
    used = {r['material'] for r in spec['regions']} | {d['material'] for d in spec['details']} | set(spec['mesh'].groups)
    return dict(schemaVersion=1, adapter='showcase-street-v1', surfaceRegions=spec['regions'], details=spec['details'],
                meshDetails=spec['mesh'].program(), paving='concrete', pavingModuleM=[1.2, .8], minLengthM=spec['min_length'],
                maxLengthM=2000, preparedLevelOnly=True, baseLiftM=BASE_LIFT,
                palette={name: linear(PALETTE_SRGB[name]) for name in sorted(used)})


def sections(spec):
    out, cursor = [], -spec['width'] / 2
    for name, width, material, zone, surface in spec['sections']:
        out.append(dict(name=name, x=r4(cursor + width / 2), width=width, material=material, zoneType=zone, surface=surface))
        cursor += width
    assert abs(cursor - spec['width'] / 2) < 1e-9, 'sections must tile the width'
    return out


def placements(spec):
    return [dict(kind=p['kind'], x=r4(p['x']), y=r4(p['y']), z=r4(p.get('z', 0.0)), yaw=round(p['yaw'], 6), scale=1) for p in spec['placements']]


def module_glb(spec, kind):
    parts = spec['modules'][kind]()
    payload, lo, hi, triangles, meshes = foliage.write_glb(parts, kind, GENERATOR)
    bounds = dict(plan=[[float(lo[0]), float(-hi[2])], [float(hi[0]), float(-lo[2])]], height=[float(lo[1]), float(hi[1])])
    return payload, bounds, triangles, meshes


def ground(prog, cycles):
    """The program surfaces as the runtime draws them on a straight route, for `cycles` consecutive cycles."""
    s = Solid(80)
    colour, lift = PALETTE_SRGB, prog['baseLiftM']
    for centre in cycles:
        for r in prog['surfaceRegions']:
            x0, x1 = r['x'] - r['width'] / 2, r['x'] + r['width'] / 2
            y0, y1 = centre + r['y'] - r['depth'] / 2, centre + r['y'] + r['depth'] / 2
            s.quad((x0, y0, lift), (x1, y0, lift), (x1, y1, lift), (x0, y1, lift), colour[r['material']])
        for d in prog['details']:
            x0, x1 = d['x'] - d['width'] / 2, d['x'] + d['width'] / 2
            y0, y1 = centre + d['y'] - d['depth'] / 2, centre + d['y'] + d['depth'] / 2
            top = lift + d['z'] + d['height'] / 2
            if d['height'] > 0:
                s.box(((x0 + x1) / 2, (y0 + y1) / 2, lift + d['z']), (x1 - x0, y1 - y0, d['height']), colour[d['material']])
            else:
                s.quad((x0, y0, top), (x1, y0, top), (x1, y1, top), (x0, y1, top), colour[d['material']])
        for m in prog['meshDetails']:
            p, idx = m['positions'], m['indices']
            for i in range(0, len(idx), 3):
                a, b, c = ((p[3 * j], centre + p[3 * j + 1], lift + p[3 * j + 2]) for j in idx[i:i + 3])
                s.tri(a, b, c, colour[m['material']])
    return [s.body]


def assembly(spec, prog, places, cycles):
    parts = ground(prog, cycles)
    built = {kind: spec['modules'][kind]() for kind in spec['modules']}
    for centre in cycles:
        for p in places:
            parts += transform_parts(built[p['kind']], p['x'], centre + p['y'], p['yaw'], p['scale'], prog['baseLiftM'] + p['z'])
    merged = {}
    for part in parts:
        key = (part.name if part.name in ('wood', 'foliage') else 'body') + (':gloss' if part.material else '')
        target = merged.setdefault(key, foliage.Part(key.replace(':', '_')))
        target.material = part.material
        target.positions += part.positions
        target.normals += part.normals
        target.colors += part.colors
    return foliage.write_glb(list(merged.values()), f"{spec['id']}_preview", GENERATOR)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build_all(name, reference=None):
    spec = STREETS[name]()
    prog = program(spec)
    places = placements(spec)
    cycle = spec['cycle']
    modules, bounds, budget = {}, {}, []
    for kind in spec['modules']:
        payload, bound, triangles, meshes = module_glb(spec, kind)
        sha = hashlib.sha256(payload).hexdigest()
        modules[kind] = dict(payload=payload, sha256=sha, bytes=len(payload))
        bounds[sha] = bound
        count = sum(p['kind'] == kind for p in places)
        budget.append(dict(kind=kind, countPerCycle=count, moduleTriangles=triangles, moduleBytes=len(payload), meshes=meshes,
                           submittedTrianglesPerCycle=count * triangles))
    preview, _, _, triangles, _ = assembly(spec, prog, places, [-cycle, 0.0, cycle])
    thumbnail = f"/archetypes/streets/{spec['slug']}/{spec['id']}.png"
    recipe = dict(id=spec['id'], title=spec['title'], sourceArchetypeId=spec['parent'], generator=GENERATOR,
                  dimensions_m=[spec['width'], cycle], fixed_width_m=spec['width'], fixture_length_m=cycle, motor_lanes=spec['lane_count'],
                  sections=sections(spec), placements=places, program=prog, runtime_approved=False,
                  modules={k: dict(path=f'modules/{k}.glb', sha256=v['sha256'], bytes=v['bytes']) for k, v in modules.items()},
                  assembly=dict(path='assembly-preview.glb', sha256=hashlib.sha256(preview).hexdigest(), bytes=len(preview), cycles=3),
                  preview_triangles=triangles, budget=budget,
                  ground_triangles_per_cycle=sum(len(m['indices']) // 3 for m in prog['meshDetails'])
                  + 2 * len(prog['surfaceRegions']) + sum(10 if d['height'] > 0 else 2 for d in prog['details']),
                  dimensions=spec['dims'], clear_routes=[dict(name=n, x=x, width=w) for n, x, w in spec['clear']],
                  track_envelopes=[dict(track_centre_x=x, half_width_m=h) for x, h in spec['envelopes']],
                  source_notes=spec['notes'])
    recipe_sha = digest({k: v for k, v in recipe.items() if k != 'assembly'})
    row = dict(id=spec['id'], sourceArchetypeId=spec['parent'], title=spec['title'], status='candidate',
               sourceRecipeSha256=recipe_sha, sourceAssemblySha256=recipe['assembly']['sha256'],
               referenceSha256=hashlib.sha256(Path(reference).read_bytes()).hexdigest() if reference else None, widthM=spec['width'], fixtureLengthM=int(cycle), routeAxis='local_y', junctionSurface='pavers',
               sections=recipe['sections'], placements=places,
               modules={k: dict(sha256=v['sha256'], bytes=v['bytes'], url=f"/street-kits/pilots/{spec['id']}/{k}.glb") for k, v in modules.items()},
               treeWells=[], thumbnailUrl=thumbnail, program=prog, programSha256=digest(prog))
    card = dict(label=spec['title'], description=spec['card'], asset_description=spec['asset_description'], search=spec['search'],
                lane_count=spec['lane_count'], group=spec['group'])
    return recipe, row, modules, bounds, preview, card


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--street', required=True, choices=sorted(STREETS))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reference', type=Path, help='the card image rendered from an earlier build; its hash becomes the reference lock')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f'{args.output} exists; a candidate is never overwritten')
    recipe, row, modules, bounds, preview, card = build_all(args.street, args.reference)
    (args.output / 'modules').mkdir(parents=True)
    for kind, module in modules.items():
        (args.output / 'modules' / f'{kind}.glb').write_bytes(module['payload'])
    (args.output / 'assembly-preview.glb').write_bytes(preview)
    if args.reference:
        (args.output / 'card.png').write_bytes(args.reference.read_bytes())
    for name, value in (('recipe.json', recipe), ('row.json', row), ('module-bounds.json', bounds), ('card.json', card)):
        (args.output / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'id': row['id'], 'preview_triangles': recipe['preview_triangles'], 'ground_per_cycle': recipe['ground_triangles_per_cycle'],
                      'modules': {b['kind']: [b['moduleTriangles'], b['moduleBytes'], b['countPerCycle']] for b in recipe['budget']}}))


if __name__ == '__main__':
    main()
