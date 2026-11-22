"""Calgary Prairie Urban Plaza: an original native park after the catalogue Calgary prairie
plaza's references (frontend/public/archetypes/openspaces/calgary-prairie-urban-plaza/variant_2*).

An open civic plaza under the prairie sky: a sandstone gathering circle inlaid with a granite
wind rose, a paved ring walk, crescents of native prairie grasses and flowers with glacial-
erratic boulders for seats, three white shade sails, a long reflecting pool, a market strip of
timber stalls, a slotted weathering-steel wind screen framing the view west toward the
mountains, and aspen groves. The reference's four-colour circle is not reproduced: the centre
is a neutral wind rose. Teaching values, not a plaza design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box

import parkkit as kit
import playkit as pk
from parkkit import Instances, Parts

PARK_ID = 'student_calgary_prairie_plaza_v1'
ARCHETYPE = 'calgary_prairie_plaza'
TITLE = 'Prairie Wind Plaza'
GENERATOR = 'CityPrompt native park batch builder v1 (plaza)'
REFERENCE = 'frontend/public/archetypes/openspaces/calgary-prairie-urban-plaza/variant_2'
KIT_SOURCES = ('playkit.py',)

SITE_W, SITE_D = 64.0, 52.0
CX, CY = 0.0, -1.0                 # gathering circle centre
CIRCLE, RING, BEDS = 9.0, 10.6, 15.5
AXIS = 2.0                          # half-width of the axis walks through the beds
POOL = box(-12.0, 11.4, 12.0, 16.6)
WATER_Z = -.1
MARKET = box(19.0, -20.0, 29.0, 16.0)
SCREEN_X = -28.6
ENTRANCE = dict(x=0.0, y=-26.0, widthM=4.0, arrivalY=-23.0)
FORECOURT = [(-13.5, -20.5), (-7.0, -20.5), (7.0, -20.5), (13.5, -20.5)]   # trees in grates on the south forecourt
SUNKEN, DEEPEST = POOL, WATER_Z - .02


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    c = Point(CX, CY)
    circle = c.buffer(CIRCLE, quad_segs=48)
    axes = shapely.union_all([box(CX - AXIS, -SITE_D / 2, CX + AXIS, POOL.bounds[1]), box(-SITE_W / 2, CY - AXIS, SITE_W / 2, CY + AXIS)])
    crescents = c.buffer(BEDS, quad_segs=48).difference(c.buffer(RING, quad_segs=48)).difference(axes)
    crescents = crescents.difference(box(-SITE_W, POOL.bounds[1] - 2.8, SITE_W, SITE_D))            # clear of the pool terrace
    coping = POOL.buffer(.4, join_style='mitre').difference(POOL)
    corners = shapely.union_all([kit.smooth(box(-32, 18.6, -12.5, 26), 2.0), kit.smooth(box(12.5, 18.6, 32, 26), 2.0),
                                 kit.smooth(box(-32, -26, -14.5, -19.0), 2.0), kit.smooth(box(14.5, -26, 32, -22.0), 1.5)])
    corners = corners.intersection(site).difference(MARKET.buffer(1.0)).difference(axes)
    screen_walk = box(SCREEN_X + .3, -17.0, SCREEN_X + 4.4, 17.0)
    strip = box(14.6, -12.0, 17.4, 8.0).difference(axes)                    # a planted strip before the market
    beds = shapely.union_all([crescents, corners, strip])
    paving = site.difference(circle).difference(beds).difference(POOL).difference(coping)
    market = MARKET.intersection(paving)
    pavers = paving.difference(market)
    return dict(site=site, circle=circle, crescents=crescents, corners=corners, strip=strip, beds=beds, coping=coping, pool=POOL,
                pavers=pavers, market=market, axes=axes, screen_walk=screen_walk)


def wind_rose(furn):
    """Granite inlays in the sandstone circle: two rings, eight rays and a centre stone, north up."""
    c = Point(CX, CY)
    parts = [c.buffer(CIRCLE, quad_segs=48).difference(c.buffer(CIRCLE - .4, quad_segs=48)),
             c.buffer(6.6, quad_segs=48).difference(c.buffer(6.35, quad_segs=48)), c.buffer(.9, quad_segs=24)]
    for k in range(8):
        a = math.pi / 2 - k * math.pi / 4
        reach = 8.4 if k % 2 == 0 else 6.0
        half = .5 if k % 2 == 0 else .32
        tip = (CX + reach * math.cos(a), CY + reach * math.sin(a))
        l = (CX + half * math.cos(a + math.pi / 2), CY + half * math.sin(a + math.pi / 2))
        r = (CX + half * math.cos(a - math.pi / 2), CY + half * math.sin(a - math.pi / 2))
        parts.append(Polygon([l, tip, r]))
    for poly in kit.polygons(shapely.union_all(parts)):
        for tri in kit.triangulate(poly):
            kit._tri_up(furn, [(x, y, .006) for x, y in tri], '#6f6c66')


def furniture(parts, layout):
    furn, metal, timber, conc = parts['furniture'], parts['metal'], parts['timber'], parts['concrete']
    wind_rose(furn)
    pk.paver_bands(furn, layout['pavers'], origin=(CX + 3.0, CY + 3.0))
    for x, y in FORECOURT:
        pk.tree_grate(furn, x, y)
    for ang in (135.0, 225.0, 315.0):                                     # three sails round the circle
        t = math.radians(ang)
        pts = []
        for r, da, z in ((12.4, -24, 4.4), (12.4, 24, 3.3), (6.8, 0, 3.9)):
            a = t + math.radians(da)
            pts.append((CX + r * math.cos(a), CY + r * math.sin(a), z))
        pk.shade_sail(metal, furn, pts)
    rock = parts['rock']
    for k, ang in enumerate(np.arange(22.5, 360.0, 45.0)):
        a = math.radians(ang)
        x, y = CX + (RING + 1.0) * math.cos(a), CY + (RING + 1.0) * math.sin(a)
        pk.boulder(rock, x, y, (1.6 + .3 * (k % 3), 1.0 + .2 * (k % 2), .5 + .06 * (k % 3)), a + math.pi / 2)
    pk.boulder(rock, -24.0, 22.0, (2.2, 1.5, .9), .4)
    pk.boulder(rock, 24.0, -24.0, (1.8, 1.2, .7), 1.2)
    for k, y in enumerate(np.arange(-15.0, 15.1, 7.5)):                   # the market strip
        pk.market_stall(timber, furn, 25.6, y, math.pi, canopy=['#5f7a5a', '#9a6a4a', '#5a7088', '#b39a5a', '#7a6a8a'][k % 5])
    pk.wind_screen(metal, (SCREEN_X, -16.0), (SCREEN_X, 16.0), height=2.6, panel=2.0, view=(12.0, 20.0, .9, 2.2))
    for ang in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(ang)
        kit.light_pole(furn, CX + (RING - .5) * math.cos(a), CY + (RING - .5) * math.sin(a), height=5.0)
    for x in (-8.0, 0.0, 8.0):                                           # benches facing the pool
        pk.bench_plinth(conc, timber, x, 9.9, 0.0, length=4.4)
    for y in (-11.0, -5.0, 5.0, 11.0):                                    # benches along the wind screen walk
        kit.bench(furn, SCREEN_X + 1.1, y, 0.0)
    for x, y in ((-3.4, -22.5), (3.4, -22.5), (17.4, 9.0), (-17.0, -9.0)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 3.6, -14.0, math.pi)
    kit.bike_rack(metal, -6.5, -23.0, 0.0, loops=4)
    kit.bike_rack(metal, 6.5, -23.0, 0.0, loops=4)
    kit.sign_board(furn, -3.2, -25.0, 0.0, colour='#7d4a2a')


def planting(inst, layout):
    rng = random.Random(9090)
    keep_off = shapely.union_all([layout['pavers'], layout['market'], layout['circle'], POOL.buffer(.5)]).buffer(.35)
    boulders = shapely.union_all([Point(CX + (RING + 1.0) * math.cos(math.radians(a)), CY + (RING + 1.0) * math.sin(math.radians(a))).buffer(1.4)
                                  for a in np.arange(22.5, 360.0, 45.0)])
    meadow = ['rough-fescue-drift', 'feather-reed-grass', 'blue-grama', 'june-grass', 'blanketflower', 'wild-bergamot', 'goldenrod',
              'prairie-crocus', 'rough-fescue-drift', 'feather-reed-grass']
    for x, y in kit.scatter(layout['crescents'].buffer(-.3), 1.4, rng, keep_off.union(boulders)):
        inst.plant(rng.choice(meadow), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    shrubs = ['wolf-willow', 'buffaloberry', 'saskatoon', 'snowberry', 'feather-reed-grass', 'rough-fescue-drift']
    for x, y in kit.scatter(layout['corners'].buffer(-.4).intersection(layout['site'].buffer(-1.4)), 1.7, rng, keep_off):
        inst.plant(rng.choice(shrubs), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.25))
    for x, y in kit.scatter(layout['strip'].buffer(-.35), 1.2, rng, keep_off):
        inst.plant(rng.choice(shrubs), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.25))
    radius = {}

    def reach(slug):
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{p}'][1].positions).reshape(-1, 3)
                                  for p in ('wood', 'foliage') if inst.meshes[f'{key}-{p}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        return radius[slug]
    site = layout['site']
    groves = [(-27.5, 22.6), (-23.0, 23.4), (-18.0, 22.6), (27.5, 22.6), (23.0, 23.4), (18.0, 22.6), (-28.0, -22.4), (-22.5, -23.2),
              (-17.5, -22.6), (27.6, -24.0), (22.4, -24.2)]
    for k, (x, y) in enumerate(groves):
        slug = 'trembling-aspen'
        scale = min(1.0, (SITE_D / 2 - abs(y) - .3) / reach(slug), (SITE_W / 2 - abs(x) - .3) / reach(slug))
        if scale >= .45 and site.contains(Point(x, y)):                   # smaller trees where the edge is close
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
    for x, y in FORECOURT:
        inst.plant('green-ash', x, y, yaw=rng.uniform(0, math.tau), scale=.72)
    for y in (-8.5, 5.5):
        inst.plant('trembling-aspen', 16.0, y, yaw=rng.uniform(0, math.tau), scale=.8)
    for ang in (45.0, 135.0, 225.0, 315.0):                              # an aspen in each crescent
        a = math.radians(ang)
        inst.plant('trembling-aspen', CX + 13.2 * math.cos(a), CY + 13.2 * math.sin(a), yaw=rng.uniform(0, math.tau), scale=.85)


def extra_checks(tris, recipe):
    """Plaza-specific: the pool is one water plane, the sails clear head height, the wind screen frames its view."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    water = vertices({'water'})
    furn = vertices({'furniture'})
    sails = furn[furn[:, 2] > 2.0]
    sail_ok = bool(len(sails)) and bool((sails[shapely.contains_xy(Point(CX, CY).buffer(RING + 2.5), sails[:, 0], sails[:, 1]), 2] > 2.4).all())
    metal = vertices({'metal'})
    screen = metal[np.abs(metal[:, 0] - SCREEN_X) < .2]
    opening = screen[(screen[:, 1] > -3.5) & (screen[:, 1] < 3.5) & (screen[:, 2] > 1.0) & (screen[:, 2] < 2.1)]
    return [('the reflecting pool is one water plane 0.1 m below the coping', bool(len(water)) and bool(np.allclose(water[:, 2], WATER_Z, atol=1e-4))),
            ('the sails stay above 2.4 m over the circle and ring walk', sail_ok),
            ('the wind screen leaves a clear view opening from 0.9 to 2.2 m high', bool(len(screen)) and not len(opening))]


def build():
    parts = Parts(9100)
    layout = plan()
    p, g = parts['paving'].body, parts['grass'].body
    kit.fill(p, 'sandstone', layout['circle'], z=0.0, cell=1.5)
    kit.fill(p, 'pavers', layout['pavers'], z=0.0, cell=2.0)
    kit.fill(p, 'deck', layout['market'], z=0.0, cell=2.0)
    kit.fill(p, 'stone', layout['coping'], z=.04, cell=1.5)
    kit.fill(parts['water'].body, 'water', POOL, z=WATER_Z, cell=2.0)
    ring = list(POOL.exterior.coords)                                    # the basin's inner walls, water to coping
    for (ax, ay), (bx, by) in zip(ring, ring[1:]):
        parts['concrete'].quad((ax, ay, WATER_Z - .02), (bx, by, WATER_Z - .02), (bx, by, .04), (ax, ay, .04), '#b9b1a2')
    kit.fill(g, 'bed', layout['beds'], z=.004, cell=1.8)
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'plaza')
    ring = LineString(list(Point(CX, CY).buffer(RING - .8, quad_segs=48).exterior.coords))
    routes = kit.route_segments(LineString([(0, -SITE_D / 2), (0, CY - RING + .8)]), 3.0)
    routes += kit.route_segments(ring, 1.4)
    routes += kit.route_segments(LineString([(0, CY + RING - .8), (0, 10.4)]), 3.0)
    routes += kit.route_segments(LineString([(-14.0, 10.4), (14.0, 10.4)]), 1.2)
    routes += kit.route_segments(LineString([(CX + RING - .8, CY), (MARKET.bounds[0] + 1.0, CY), (MARKET.bounds[0] + 1.0, 14.0)]), 2.0)
    routes += kit.route_segments(LineString([(CX - RING + .8, CY), (SCREEN_X + 3.2, CY)]), 3.0)
    routes += kit.route_segments(LineString([(SCREEN_X + 3.2, -16.0), (SCREEN_X + 3.2, 16.0)]), 1.6)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass'], reference=REFERENCE, routes=routes,
        programme='A sandstone gathering circle inlaid with a granite wind rose, a paved ring walk, crescents of rough fescue, '
                  'feather reed grass, blue grama and prairie flowers with glacial-erratic boulders for seats, three white shade '
                  'sails, a long reflecting pool with plinth benches, a market strip of five timber stalls, a slotted weathering-'
                  'steel wind screen framing the view west, lights, bike racks and aspen groves.',
        design_basis='Original concept after the catalogue Calgary prairie plaza references (variant 2): circular gathering '
                     'space, shade sails, reflecting pool and prairie planting. The reference\'s four-colour circle is not '
                     'reproduced; the centre is a neutral wind rose.',
        limitations=['Prepared level ground only; drainage, pool water treatment and winter operation are not designed.',
                     'Shade sails, the wind screen and market stalls are indicative structures that need engineering review.',
                     'The wind rose is decorative and points to grid north, not a surveyed true north.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='plazas',
        description='A civic plaza with a sandstone wind-rose circle, prairie grass crescents, shade sails, a reflecting pool, '
                    'market stalls and a wind screen framing the mountain view. Prepared level ground.')
    return meshes, nodes, meta
