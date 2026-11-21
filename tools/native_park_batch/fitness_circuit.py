"""Parkour & Calisthenics Yard: an original native park after the catalogue outdoor fitness
circuit's "Parkour & Movement" references
(frontend/public/archetypes/openspaces/outdoor-fitness-circuit/variant_1*).

A red rubber movement floor with concrete vault walls and precision blocks, a climbing
wall, a pull-up rig with monkey bars, a hexagonal climbing frame, dip bars and balance
rails, set in lawn, a grass mound and dense planting with a winding asphalt loop.
Equipment sizes are typical teaching values, not a play or fitness equipment design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, box

import parkkit as kit
from parkkit import Instances, Parts

PARK_ID = 'student_parkour_calisthenics_yard_v1'
ARCHETYPE = 'outdoor_fitness_circuit'
TITLE = 'Parkour & Calisthenics Yard'
GENERATOR = 'CityPrompt native park batch builder v1 (fitness)'
REFERENCE = 'frontend/public/archetypes/openspaces/outdoor-fitness-circuit/variant_1'

SITE_W, SITE_D = 44.0, 36.0
ENTRANCE = dict(x=6, y=-18, widthM=2.0, arrivalY=-15)
CONCRETE, CONCRETE_DARK, STEEL, FRAME = '#bdb8ae', '#a8a399', '#5a6166', '#2f3438'
MOUND = ((12.0, 8.0), 3.6, 1.0)
SUNKEN, DEEPEST = None, 0.0

RUBBER = kit.smooth(shapely.union_all([kit.ellipse(-3, 1, 10, 6.5, math.radians(12)), Point(5, 4).buffer(4.5, quad_segs=24),
                                        Point(-9, -3).buffer(4.0, quad_segs=24), kit.ellipse(2.8, -2.4, 5.0, 3.3)]), 1.5)


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    kerb = RUBBER.buffer(.3, quad_segs=12).difference(RUBBER)
    ring = [(6, -14), (13, -12.2), (17.2, -5), (17.8, 4), (14.2, 11.4), (6, 14.2), (-4, 14.6), (-13, 12.2), (-18.2, 5), (-18.4, -5),
            (-14, -12), (-6, -14.4), (1, -14.6)]
    loop = LineString(kit.chaikin(ring + ring[:1], 4))
    spur = LineString([(6, -SITE_D / 2), (6, -14.6), (4.6, -11.6), (3.4, -8.4), (3.0, -5.4)])
    north = LineString([(-2.5, 14.5), (-2.3, 11.5), (-2.0, 8.6)])
    lines = [loop, spur, north]
    floor = shapely.union_all([RUBBER, kerb])
    paths = shapely.union_all([line.buffer(1.0, quad_segs=8) for line in lines]).difference(floor).intersection(site)
    pads = shapely.union_all([box(-14.9, -6.9, -13.3, -4.9), box(10.4, -2.0, 12.4, -.2)]).difference(paths)
    inside = shapely.geometry.Polygon(loop.coords).difference(floor).difference(paths).difference(pads)
    mound_area = Point(*MOUND[0]).buffer(MOUND[1], quad_segs=24).intersection(inside)
    beds_inner = inside.difference(mound_area).difference(floor.buffer(1.6)).difference(paths.buffer(.9))
    lawn = inside.difference(mound_area).difference(beds_inner)
    outer = site.difference(shapely.geometry.Polygon(loop.coords)).difference(paths).difference(pads)
    return dict(site=site, rubber=RUBBER, kerb=kerb, floor=floor, paths=paths, pads=pads, lawn=lawn, mound=mound_area, beds=beds_inner,
                outer=outer, loop=loop, spur=spur, north=north)


# ---- equipment ------------------------------------------------------------------------------------
def vault_blocks(conc):
    """An H of vault walls with a cross block, and precision blocks: board-formed concrete."""
    for x in (-7.6, -4.4):
        kit.extrude(conc, CONCRETE, box(x - .2, -1.3, x + .2, 1.3), 0, 1.15, top_colour='#c6c1b8')
    kit.extrude(conc, CONCRETE, box(-7.4, -.35, -4.6, .35), 0, .85, top_colour='#c6c1b8')
    for (x, y, h) in ((-9.4, 2.6, .5), (-10.4, .6, .7), (-9.2, -1.6, .45), (-6.0, 2.9, .6), (-2.6, -1.3, .9)):
        kit.extrude(conc, CONCRETE, box(x - .32, y - .32, x + .32, y + .32), 0, h, top_colour='#c6c1b8')
    kit.extrude(conc, CONCRETE_DARK, box(-12.0, -5.2, -11.6, -2.6), 0, 1.6, top_colour='#c6c1b8')   # a tic-tac wall


def climbing_wall(conc, metal, furn, rng):
    """A 3.6 m by 3 m bouldering wall facing south, on a steel frame, with coloured holds."""
    x0, x1, y, h = -.8, 2.8, 4.6, 3.0
    kit.extrude(conc, '#9e9a92', box(x0, y, x1, y + .25), 0, h, top_colour='#8f8b84')
    for x in (x0 + .1, x1 - .1):
        metal.box((x, y + .55, h / 2), (.1, .1, h), FRAME)
        metal.cyl((x, y + .25, h - .2), (x, y + .55, h - .5), .03, FRAME, sides=6)
    colours = ['#d9472b', '#2f7fc1', '#f2b632', '#3c9b57', '#8b4fb0']
    for _ in range(46):
        hx, hz = rng.uniform(x0 + .2, x1 - .2), rng.uniform(.25, h - .25)
        furn.box((hx, y - .04, hz), (rng.uniform(.08, .16), .08, rng.uniform(.07, .13)), rng.choice(colours))


def pull_up_rig(metal):
    """A 5 m rig: posts at three stations, pull-up bars at three heights and monkey bars across the top."""
    x0, y0 = 0.2, -2.4
    for dx in (0, 2.5, 5.0):
        for dy in (-.6, .6):
            metal.cyl((x0 + dx, y0 + dy, 0), (x0 + dx, y0 + dy, 2.5), .05, FRAME, sides=8)
    for dy in (-.6, .6):
        kit.tube(metal, [(x0, y0 + dy, 2.45), (x0 + 5.0, y0 + dy, 2.45)], .03, STEEL)
    for k in range(13):
        x = x0 + .2 + k * .38
        kit.tube(metal, [(x, y0 - .6, 2.45), (x, y0 + .6, 2.45)], .02, STEEL)
    for dx, z in ((1.25, 2.0), (3.75, 2.25)):
        kit.tube(metal, [(x0 + dx - 1.2, y0 - .6, z), (x0 + dx + 1.2, y0 - .6, z)], .02, STEEL)


def hex_frame(metal, cx=6.6, cy=5.4, r=1.6):
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(0, math.tau, 7)[:-1]]
    for x, y in pts:
        metal.cyl((x, y, 0), (x, y, 2.5), .05, FRAME, sides=8)
    for z in (1.2, 2.45):
        kit.tube(metal, [(x, y, z) for x, y in pts], .025, STEEL, closed=True)
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        kit.tube(metal, [(ax, ay, .6), ((ax + bx) / 2, (ay + by) / 2, 1.8), (bx, by, .6)], .018, STEEL)


def dip_and_balance(metal):
    for y in (-4.4, -3.9):
        kit.tube(metal, [(-1.8, y, 1.2), (.2, y, 1.2)], .025, STEEL)
        for x in (-1.7, .1):
            metal.cyl((x, y, 0), (x, y, 1.2), .04, FRAME, sides=8)
    rails = [((-12.4, -.6), (-10.8, -2.2), .4), ((-10.8, -2.2), (-9.4, -3.6), .6), ((-9.4, -3.6), (-7.6, -4.6), .45)]
    for (ax, ay), (bx, by), h in rails:
        kit.tube(metal, [(ax, ay, h), (bx, by, h)], .03, STEEL)
        for x, y in ((ax, ay), (bx, by)):
            metal.cyl((x, y, 0), (x, y, h), .035, FRAME, sides=8)


# ---- planting and furniture ------------------------------------------------------------------------
def planting(inst, layout):
    rng = random.Random(3044)
    keep_off = shapely.union_all([layout['paths'], layout['floor'], layout['pads']]).buffer(.55)
    mix = ['feather-reed-grass', 'feather-reed-grass', 'rough-fescue-drift', 'wild-bergamot', 'goldenrod', 'snowberry',
           'shrubby-cinquefoil', 'blanketflower', 'diabolo-ninebark', 'wolf-willow']
    for x, y in kit.scatter(layout['beds'].buffer(-.3), 1.35, rng, keep_off):
        inst.plant(rng.choice(mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    outer = layout['outer'].buffer(-1.7)
    for x, y in kit.scatter(outer, 1.7, rng, keep_off):
        inst.plant(rng.choice(mix + ['saskatoon', 'buffaloberry']), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    trees = [('green-ash', -19.0, 15.0), ('green-ash', -19.5, -2.0), ('littleleaf-linden', -16.0, -15.2), ('green-ash', 19.0, -15.0),
             ('littleleaf-linden', 19.2, 1.2), ('green-ash', 18.5, 15.2), ('littleleaf-linden', 6.0, 16.0), ('littleleaf-linden', -9.0, 16.0),
             ('littleleaf-linden', 12.5, -6.5), ('green-ash', -15.5, 7.0), ('littleleaf-linden', -13.0, 9.6),
             ('littleleaf-linden', 9.8, 10.6), ('green-ash', 14.6, 1.0), ('littleleaf-linden', -15.2, -8.6), ('littleleaf-linden', -1.0, -10.6)]
    for slug, x, y in trees:
        margin = {'green-ash': 4.4, 'littleleaf-linden': 4.0}[slug]
        if layout['site'].buffer(-margin).contains(Point(x, y)) and not keep_off.buffer(.8).contains(Point(x, y)):
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau))


def furniture(parts, layout):
    furn = parts['furniture']
    kit.bench(furn, -14.1, -5.9, 0.0)
    kit.bench(furn, 11.4, -1.1, math.pi)
    for x, y in ((4.4, -16.0), (-3.6, 15.9)):
        kit.waste_bin(furn, x, y)
    for x, y in ((14.8, -8.8), (-16.2, 8.4), (8.6, 12.1), (-8.4, -12.6)):
        kit.light_pole(furn, x, y, height=4.5)
    kit.bike_rack(parts['metal'], 8.6, -16.4, math.pi / 2)
    kit.drinking_fountain(furn, 3.6, -13.0, 0.0)
    kit.sign_board(furn, 7.9, -17.0, 0.0, colour='#8a3b2c')
    for x, y, yaw in ((-4.0, -3.2, 0.0), (1.4, -5.6, 0.0), (8.6, 2.2, math.pi / 2)):
        kit.sign_board(furn, x, y, yaw, colour='#3b5d7a')


def extra_checks(tris, recipe):
    """Fitness-specific: every climbing and swinging frame stands on the rubber, over its fall zone."""
    metal = np.concatenate([t for n, t, _, _ in tris if n == 'metal']).reshape(-1, 3)
    frames = metal[metal[:, 2] > .3]
    yard = RUBBER.buffer(1.0)
    on_rubber = shapely.contains_xy(RUBBER, frames[:, 0], frames[:, 1])
    racks = ~shapely.contains_xy(yard, frames[:, 0], frames[:, 1])           # the bike rack stands by the entrance
    return [('every equipment frame above 0.3 m stands over the rubber floor', bool((on_rubber | racks).all())),
            ('rubber floor at least 1.5 m beyond the rig and frame posts',
             bool(RUBBER.buffer(-1.5).contains(Point(2.7, -2.4)) and RUBBER.buffer(-1.5).contains(Point(6.6, 5.4))))]


def build():
    parts = Parts(4400)
    layout = plan()
    kit.fill(parts['rubber'].body, 'rubber_red', layout['rubber'], z=.02, cell=1.5)
    kit.fill(parts['paving'].body, 'deck', layout['kerb'], z=.02, cell=1.5)
    kit.fill(parts['paving'].body, 'deck', layout['pads'], z=.01, cell=1.5)
    kit.fill(parts['paving'].body, 'asphalt', layout['paths'], z=.01)
    kit.fill(parts['grass'].body, 'lawn', layout['lawn'])
    kit.fill(parts['grass'].body, 'bed', layout['beds'], z=.004, cell=1.8)
    kit.fill(parts['grass'].body, 'bed', layout['outer'], z=.004, cell=2.2)
    kit.heightfield(parts['grass'].body, 'lawn', layout['mound'], kit.mound(*MOUND), spacing=.5, rings=(.4, 1.0), ring_step=.5)
    rng = random.Random(44)
    conc, metal = parts['concrete'], parts['metal']
    vault_blocks(conc)
    climbing_wall(conc, metal, parts['furniture'], rng)
    pull_up_rig(metal)
    hex_frame(metal)
    dip_and_balance(metal)
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'fitness')
    routes = kit.route_segments(layout['spur'], 2.0) + kit.route_segments(layout['loop'], 2.0) + kit.route_segments(layout['north'], 2.0)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'rubber'], reference=REFERENCE, routes=routes,
        programme='A red rubber movement floor with concrete vault walls, a cross block, precision blocks and a tic-tac wall; a '
                  'bouldering wall; a pull-up rig with monkey bars; a hexagonal climbing frame; dip bars and zigzag balance rails; a '
                  'winding asphalt loop through lawn, a grass mound and dense planting; benches, lights, station signs, a bike rack and a '
                  'drinking fountain; green ash and littleleaf linden.',
        design_basis='Original concept after the catalogue outdoor fitness circuit "Parkour & Movement" references (variant 1). '
                     'Equipment sizes are typical teaching values, not a certified play or fitness equipment layout.',
        limitations=['Prepared level ground only.',
                     'Equipment, fall zones and surfacing are indicative; real installations follow the manufacturer and the '
                     'applicable play and fitness equipment standards.',
                     'Station signs are blank.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='A red rubber movement floor with vault walls, a climbing wall, a pull-up rig and a hex frame, in lawn and planting '
                    'with a path loop. Prepared level ground.')
    return meshes, nodes, meta
