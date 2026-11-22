"""Creekside Mini Golf: an original native park after the catalogue mini golf course's
"Nature Course" references (frontend/public/archetypes/openspaces/mini-golf-putting-course/variant_3*).

A nine-hole putting course laid out along a meandering creek: organic carpet greens with timber
edging, tee mats, cups and flags, boulder and log obstacles, a stone-dust path loop that crosses
the creek on two timber footbridges, a sod-roof starter hut by the entrance, and prairie planting
with aspen and spruce. No windmills, castles or other stock set pieces. Teaching values, not a
course design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, box

import leisurekit as lk
import parkkit as kit
import playkit as pk
from parkkit import Instances, Parts

PARK_ID = 'student_creekside_mini_golf_v1'
ARCHETYPE = 'mini_golf_course'
TITLE = 'Creekside Mini Golf'
GENERATOR = 'CityPrompt native park batch builder v1 (minigolf)'
REFERENCE = 'frontend/public/archetypes/openspaces/mini-golf-putting-course/variant_3'
KIT_SOURCES = ('playkit.py', 'leisurekit.py')

SITE_W, SITE_D = 48.0, 40.0
CREEK_LINE = LineString(kit.chaikin([(-24.5, 2.0), (-14.0, 4.2), (-6.0, .8), (2.0, 3.4), (10.0, -.2), (18.0, 2.2), (24.5, .4)], 4))
CREEK = CREEK_LINE.buffer(.9, cap_style='flat')
BANKS = CREEK_LINE.buffer(1.6, cap_style='flat').difference(CREEK)
WATER_Z = -.12
PATH_W = 1.8
NORTH_Y, SOUTH_Y = 8.0, -11.5
BRIDGES = (-12.0, 14.0)
ENTRANCE = dict(x=0.0, y=-20.0, widthM=1.8, arrivalY=-17.0)
HUT = (5.2, -16.4)
# each hole: green centre line, half-width, tee at the first point, cup near the last, obstacles
HOLES = [
    ([(-21.0, 14.0), (-17.0, 15.5), (-13.0, 13.8)], .8, [('boulder', -17.0, 15.3)]),
    ([(-9.0, 15.0), (-6.0, 17.0), (-3.0, 14.0), (0.0, 16.0)], .75, []),
    ([(4.0, 13.0), (9.0, 13.2), (11.0, 16.8)], .8, [('log', 7.0, 13.2)]),
    ([(15.0, 12.2), (18.5, 15.5), (21.5, 13.0)], .8, [('boulder', 18.4, 14.9)]),
    ([(22.0, -4.0), (19.5, -7.5), (16.6, -5.6)], .75, [('boulder', 19.6, -7.1)]),
    ([(10.0, -5.0), (6.0, -7.0), (2.0, -5.0)], .8, [('log', 6.0, -6.8)]),
    ([(-2.0, -6.5), (-5.8, -4.8), (-9.0, -7.0)], .75, []),
    ([(-21.0, -16.5), (-16.0, -15.0), (-11.0, -17.0)], .8, [('boulder', -16.0, -15.4)]),
    ([(10.5, -15.5), (15.5, -17.2), (20.5, -15.2)], .8, [('log', 15.5, -16.9)]),
]
FLAGS = ['#c8452f', '#2f7fc1', '#f2b632', '#3c9b57', '#8b4fb0', '#d9472b', '#2f9b9b', '#b0862f', '#e8e8e2']
SUNKEN, DEEPEST = CREEK, WATER_Z - .02


def crossing(x):
    """The rectangle a bridge and its ramps occupy: the creek corridor's full extent across the bridge width."""
    _, ya, _, yb = CREEK_LINE.buffer(2.4, cap_style='flat').intersection(box(x - 1.0, -12.0, x + 1.0, 12.0)).bounds
    return ya, yb


def greens():
    """Organic greens: a strip along each hole, swelling at the tee and widest round the cup."""
    out = []
    for pts, w, _ in HOLES:
        line = LineString(pts)
        cup = line.interpolate(line.length - .9).coords[0]
        shape = shapely.union_all([line.buffer(w, quad_segs=12), Point(pts[0]).buffer(w * 1.25, quad_segs=16),
                                   Point(cup).buffer(w * 1.75, quad_segs=16)])
        out.append(kit.smooth(shape, .4))
    return out


NORTH_PTS = [(-20.5, 9.4), (-16.0, 8.4), (-12.0, 8.0), (-6.0, 9.2), (0.0, 8.2), (6.0, 9.0), (10.0, 8.4), (14.0, 8.0), (18.0, 8.8), (21.0, 8.0)]
SOUTH_PTS = [(-20.5, -11.0), (-16.0, -11.6), (-12.0, -11.5), (-6.0, -10.7), (0.0, -11.5), (6.0, -12.0), (10.0, -11.6), (14.0, -11.5),
             (18.0, -10.9), (21.0, -11.6)]


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    lines = [LineString(kit.chaikin(NORTH_PTS, 3)), LineString(kit.chaikin(SOUTH_PTS, 3)),
             LineString([(BRIDGES[0], SOUTH_Y), (BRIDGES[0], NORTH_Y)]), LineString([(BRIDGES[1], SOUTH_Y), (BRIDGES[1], NORTH_Y)]),
             LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], SOUTH_Y)])]
    path = shapely.union_all([l.buffer(PATH_W / 2, cap_style='square') for l in lines]).intersection(site)
    crossings = shapely.union_all([box(x - 1.0, crossing(x)[0], x + 1.0, crossing(x)[1]) for x in BRIDGES])
    path = path.difference(crossings)
    gs = greens()
    edges = shapely.union_all([g.buffer(.12, quad_segs=12).difference(g) for g in gs])
    assert not path.intersects(shapely.union_all(gs).buffer(.3)), 'a green overlaps a path'
    beds = site.difference(path).difference(crossings).difference(CREEK).difference(BANKS).difference(shapely.union_all(gs).buffer(.12))
    hut = box(HUT[0] - 1.6, HUT[1] - 1.8, HUT[0] + 1.6, HUT[1] + 1.8)
    return dict(site=site, path=path, crossings=crossings, greens=gs, edges=edges, beds=beds.difference(hut.buffer(.9, join_style='mitre')), hut=hut)


def obstacles(parts, rng):
    rock, timber = parts['rock'], parts['timber']
    for k, (pts, w, obs) in enumerate(HOLES):
        for kind, x, y in obs:
            if kind == 'boulder':
                pk.boulder(rock, x, y, (.7, .5, .32), k * .7)
            else:
                a = math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0]) + math.pi / 2
                timber.cyl((x - math.cos(a) * .45, y - math.sin(a) * .45, .1), (x + math.cos(a) * .45, y + math.sin(a) * .45, .1), .1, '#6f5a43', sides=8)


def furniture(parts, layout, rng):
    furn, metal, timber = parts['furniture'], parts['metal'], parts['timber']
    for k, ((pts, w, _), g) in enumerate(zip(HOLES, layout['greens'])):
        lk.timber_edge(timber, g)
        (tx, ty), (nx, ny) = pts[0], pts[1]
        a = math.atan2(ny - ty, nx - tx)
        tee = shapely.affinity.rotate(box(tx - .1, ty - .45, tx + .8, ty + .45), a, origin=(tx, ty), use_radians=True)
        for tri in kit.triangulate(tee):
            kit._tri_up(furn, [(x, y, .015) for x, y in tri], '#2f3a2c')
        line = LineString(pts)
        cx, cy = line.interpolate(line.length - .9).coords[0]
        lk.cup_and_flag(furn, metal, cx, cy, flag=FLAGS[k])
    obstacles(parts, rng)
    for x in BRIDGES:
        ya, yb = crossing(x)
        lk.footbridge(timber, metal, (x, ya + .6), (x, yb - .6), width=2.0, deck=.25)
    rock = parts['rock']
    for d in np.arange(.5, CREEK_LINE.length, 1.5):                     # rock-lined banks, irregular, gaps at the bridges
        for side in (-1, 1):
            if rng.random() < .35:
                continue
            d = d + rng.uniform(-.4, .4)
            x, y = CREEK_LINE.interpolate(d).coords[0]
            nx_, ny_ = CREEK_LINE.interpolate(min(CREEK_LINE.length, d + .1)).coords[0]
            ang = math.atan2(ny_ - y, nx_ - x)
            off = rng.uniform(1.1, 1.45)
            bx, by = x - math.sin(ang) * side * off, y + math.cos(ang) * side * off
            if any(abs(bx - b) < 1.6 for b in BRIDGES) or not layout['site'].buffer(-.6).contains(Point(bx, by)):
                continue
            pk.boulder(rock, bx, by, (.6 + .25 * rng.random(), .45 + .2 * rng.random(), .3 + .15 * rng.random()), rng.uniform(0, math.tau))
    lk.sod_hut(timber, parts['grass'], HUT[0], HUT[1], math.pi, w=3.4, d=3.0)
    for x, y, yaw in ((-6.0, NORTH_Y + 1.6, -math.pi / 2), (6.0, NORTH_Y + 1.6, -math.pi / 2), (-4.5, SOUTH_Y - 1.6, math.pi / 2),
                      (9.0, SOUTH_Y + 1.5, -math.pi / 2)):
        kit.bench(furn, x, y, yaw)
    for x, y in ((2.2, -18.6), (-2.2, SOUTH_Y - 1.4), (22.0, NORTH_Y + 1.5)):
        kit.waste_bin(furn, x, y)
    kit.sign_board(furn, -2.0, -19.2, 0.0, colour='#4f6a3a')
    kit.bike_rack(metal, -4.2, -17.6, math.pi / 2)


def planting(inst, layout):
    rng = random.Random(12012)
    site = layout['site']
    keep_off = shapely.union_all([layout['path'], layout['crossings'], shapely.union_all(layout['greens']).buffer(.3), layout['hut']]).buffer(.45)
    mix = ['feather-reed-grass', 'rough-fescue-drift', 'blanketflower', 'wild-bergamot', 'shrubby-cinquefoil', 'snowberry', 'blue-grama',
           'prairie-crocus', 'feather-reed-grass']
    for x, y in kit.scatter(layout['beds'].buffer(-.3).intersection(site.buffer(-1.0)), 1.9, rng, keep_off.union(CREEK.buffer(1.4))):
        inst.plant(rng.choice(mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    trees = [('trembling-aspen', -22.0, 18.0), ('trembling-aspen', -18.5, 18.6), ('white-spruce', 21.8, 18.2), ('trembling-aspen', 22.0, -2.6),
             ('white-spruce', -22.0, -2.8), ('trembling-aspen', -22.0, -10.0), ('trembling-aspen', 22.0, -9.6), ('white-spruce', 2.0, 18.4),
             ('trembling-aspen', -7.5, 1.8)]
    radius = {}
    for slug, x, y in trees:
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{q}'][1].positions).reshape(-1, 3)
                                  for q in ('wood', 'foliage') if inst.meshes[f'{key}-{q}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        edge = min(SITE_W / 2 - abs(x), SITE_D / 2 - abs(y)) - .2
        scale = min(.8, edge / radius[slug])                          # canopies stay inside the site
        p = Point(x, y)
        if scale >= .5 and not keep_off.buffer(.8).contains(p) and not CREEK.buffer(.8).contains(p):
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)


def extra_checks(tris, recipe):
    """Course-specific: nine cups with flags on their greens, and the creek one water plane."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    metal, water = vertices({'metal'}), vertices({'water'})
    flags = metal[metal[:, 2] > 1.2]
    found = 0
    for (pts, w, _), g in zip(HOLES, greens()):
        line = LineString(pts)
        cx, cy = line.interpolate(line.length - .9).coords[0]
        found += bool((np.hypot(flags[:, 0] - cx, flags[:, 1] - cy) < .05).any()) and g.contains(Point(cx, cy))
    return [('nine cups with flagsticks, each on its own green', found == 9),
            ('the creek is one water plane 0.12 m below grade', bool(len(water)) and bool(np.allclose(water[:, 2], WATER_Z, atol=1e-4)))]


def build():
    parts = Parts(12100)
    layout = plan()
    rng = random.Random(1201)
    g, gr = parts['grass'].body, parts['gravel'].body
    kit.fill(g, 'lawn', layout['beds'], z=0.0, cell=2.0)
    for green in layout['greens']:
        kit.fill(g, 'putting', green, z=.02, cell=1.2)
    kit.fill(gr, 'stone_dust', layout['path'].union(layout['hut'].buffer(.9, join_style='mitre')), z=.01, cell=2.0)
    kit.fill(gr, 'creek_bed', BANKS.intersection(layout['site']).difference(layout['crossings']), z=-.02, cell=1.5)
    kit.fill(parts['water'].body, 'water', CREEK.intersection(layout['site']), z=WATER_Z, cell=1.5)
    for x in BRIDGES:                                                    # path ramps up to each bridge deck
        ya, yb = crossing(x)
        lk.ramp(parts['deck'].body, 'boards', (x, ya), (x, ya + .6), 2.0, .01, .25)
        lk.ramp(parts['deck'].body, 'boards', (x, yb - .6), (x, yb), 2.0, .25, .01)
        kit.fill(parts['deck'].body, 'boards', box(x - .9, ya + .6, x + .9, yb - .6), z=.245, cell=1.0)   # walk surface under the plank tops
    furniture(parts, layout, rng)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'minigolf')
    routes = kit.route_segments(LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], SOUTH_Y)]), 1.6)
    routes += kit.route_segments(LineString(kit.chaikin(SOUTH_PTS, 3)), 1.6)
    routes += kit.route_segments(LineString(kit.chaikin(NORTH_PTS, 3)), 1.6)
    for x in BRIDGES:
        routes += kit.route_segments(LineString([(x, SOUTH_Y), (x, NORTH_Y)]), 1.6)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['grass', 'gravel', 'deck'], reference=REFERENCE, routes=routes,
        programme='A nine-hole putting course along a meandering rock-lined creek: organic carpet greens with timber edging, tee '
                  'mats, cups and coloured flags, boulder and log obstacles; a stone-dust path loop crossing the creek on two '
                  'timber footbridges; a sod-roof starter hut by the entrance; benches, bins, a bike rack and prairie planting '
                  'with aspen and spruce.',
        design_basis='Original concept after the catalogue mini golf "Nature Course" references (variant 3): holes woven along '
                     'a creek with timber and stone details. No stock windmill, castle or ship set pieces.',
        limitations=['Prepared level ground only; the greens are flat carpet without designed breaks.',
                     'The creek is a shallow decorative channel; water supply, lining and safety are not designed.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='A nine-hole mini golf course along a rock-lined creek, with carpet greens, timber footbridges and a sod-roof '
                    'starter hut. Prepared level ground.')
    return meshes, nodes, meta
