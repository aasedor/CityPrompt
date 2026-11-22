"""Clover Neighbourhood Park: an original native park after the catalogue neighborhood park's
"Rustic Community Park" references (frontend/public/archetypes/openspaces/neighborhood-park/variant_0*).

A neighbourhood park around an open oval lawn for informal play, ringed by a stone-dust walk.
Three lobes open off the ring: a playground on wood-fibre surfacing with two timber towers,
a bridge, a slide, a climbing net and swings; a picnic shelter with tables; and a nature-play
corner of boulders and logs. A split-rail fence and wildflower meadow line the south edge,
and mature shade trees are scattered round the park. Teaching values, not a play design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, box

import parkkit as kit
import playkit as pk
import sportskit as sk
from parkkit import Instances, Parts

PARK_ID = 'student_clover_neighbourhood_park_v1'
ARCHETYPE = 'neighborhood_park'
TITLE = 'Clover Neighbourhood Park'
GENERATOR = 'CityPrompt native park batch builder v1 (neighbourhood)'
REFERENCE = 'frontend/public/archetypes/openspaces/neighborhood-park/variant_0'
KIT_SOURCES = ('sportskit.py', 'playkit.py')

SITE_W, SITE_D = 84.0, 68.0
LAWN = kit.ellipse(0.0, 3.0, 21.0, 14.0, 0.0, n=96)
RING_W = 2.4
PLAY = Point(29.5, -8.0).buffer(8.5, quad_segs=32)
PICNIC = Point(-24.5, 12.5).buffer(8.0, quad_segs=32)
NATURE = Point(-23.0, -14.0).buffer(7.0, quad_segs=32)
ENTRANCE = dict(x=4.0, y=-34.0, widthM=2.4, arrivalY=-31.0)
TOWERS = ((26.5, -5.5), (31.8, -4.0))
DECK = 1.2
SUNKEN, DEEPEST = None, 0.0


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    ring = LAWN.buffer(.2 + RING_W, quad_segs=24).difference(LAWN.buffer(.2, quad_segs=24))
    edge = LAWN.buffer(.2, quad_segs=24).difference(LAWN)                         # a mown edge strip
    spur = LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], -16.4)]).buffer(1.2, cap_style='flat')
    links = shapely.union_all([LineString([(-14.0, 11.5), (-17.5, 12.5)]).buffer(1.1), LineString([(-13.0, -7.0), (-17.5, -11.0)]).buffer(1.1),
                               LineString([(15.6, -7.2), (21.4, -8.0)]).buffer(1.1)])
    curb = PLAY.buffer(.25, quad_segs=32).difference(PLAY)
    gap = box(19.8, -9.2, 22.2, -6.8)                                           # a level, accessible entry
    curb = curb.difference(gap)
    stone = shapely.union_all([ring, spur, links, PICNIC, NATURE]).difference(PLAY.buffer(.25).difference(gap)).difference(PLAY).intersection(site)
    meadow = shapely.union_all([box(-SITE_W / 2, -SITE_D / 2, ENTRANCE['x'] - 2.0, -SITE_D / 2 + 4.5),
                                box(ENTRANCE['x'] + 2.0, -SITE_D / 2, SITE_W / 2, -SITE_D / 2 + 4.5),
                                kit.smooth(box(-SITE_W / 2, SITE_D / 2 - 6.0, -6.0, SITE_D / 2), 2.0),
                                kit.smooth(box(10.0, SITE_D / 2 - 6.5, SITE_W / 2, SITE_D / 2), 2.0)])
    meadow = meadow.intersection(site.buffer(-.01)).difference(stone.buffer(.8)).difference(PLAY.buffer(1.5))
    lawn_all = site.difference(LAWN).difference(edge).difference(stone).difference(PLAY.buffer(.25)).difference(meadow)
    return dict(site=site, lawn=LAWN, edge=edge, ring=ring, stone=stone, curb=curb, play=PLAY, meadow=meadow, grass=lawn_all, spur=spur)


def playground(timber, metal, furn, rock):
    (ax, ay), (bx, by) = TOWERS
    pk.play_tower(timber, metal, ax, ay, deck=DECK, roof='#4f7a4a')
    pk.play_tower(timber, metal, bx, by, deck=DECK + .3, roof='#b0862f')
    pk.play_bridge(timber, metal, (ax + .8, ay + .35), (bx - .8, by - .35), deck=DECK + .15)
    pk.slide(metal, bx + .8, by - .3, math.radians(-30), deck=DECK + .3, length=3.4)
    pk.climbing_net(metal, (ax - .2, ay - 3.0), (ax, ay - .8), deck=DECK)
    pk.swing_set(metal, 29.5, -13.0, 0.0, bays=2)
    for k, (x, y) in enumerate(((23.0, -10.5), (24.5, -13.0), (35.5, -9.0))):
        pk.boulder(rock, x, y, (1.1 + .2 * k, .8, .5), k * 1.3, palette=pk.ERRATIC)
    for k in range(5):                                                   # log steppers
        timber.cyl((32.5 + k * .7, -9.5 - k * .9, 0), (32.5 + k * .7, -9.5 - k * .9, .25 + .08 * (k % 3)), .2, '#7a5b3c', sides=9)


def furniture(parts, layout):
    furn, metal, timber, conc, rock = parts['furniture'], parts['metal'], parts['timber'], parts['concrete'], parts['rock']
    kit.extrude(conc, '#b5b0a6', layout['curb'], 0, .12)
    playground(timber, metal, furn, rock)
    sk.shelter(timber, metal, -27.0, 14.5, -math.pi / 4, length=7.5, depth=4.2)
    for x, y, yaw in ((-21.5, 9.6, .3), (-25.5, 8.8, -.2), (-20.0, 14.2, 1.3)):
        pk.picnic_table(timber, x, y, yaw)
    for k, (x, y) in enumerate(((-24.5, -12.0), (-20.5, -15.5), (-25.5, -16.5), (-21.0, -11.2))):
        pk.boulder(rock, x, y, (1.4 + .25 * (k % 2), 1.0, .55 + .1 * (k % 3)), k * .9, palette=pk.ERRATIC)
    for x0, y0, x1, y1 in ((-27.0, -14.0, -22.5, -18.6), (-19.0, -13.0, -18.4, -17.8)):            # fallen logs
        timber.cyl((x0, y0, .22), (x1, y1, .22), .22, '#6f5a43', sides=9)
    for s in (-1, 1):                                                    # small goals on the lawn
        sk.goal(metal, s * 17.0, 3.0, math.pi if s > 0 else 0.0, width=3.0, height=1.5, depth=1.0)
    for ang in (60, 120, 200, 250, 290, 340):                            # benches round the ring, facing the lawn
        a = math.radians(ang)
        x, y = 23.8 * math.cos(a), 3.0 + 16.8 * math.sin(a)
        if not PLAY.buffer(1.0).contains(Point(x, y)):
            kit.bench(furn, x, y, math.atan2(3.0 - y, -x))
    fence = [(-SITE_W / 2 + .5, -SITE_D / 2 + .6), (ENTRANCE['x'] - 2.2, -SITE_D / 2 + .6)]
    pk.split_rail_fence(timber, fence)
    pk.split_rail_fence(timber, [(ENTRANCE['x'] + 2.2, -SITE_D / 2 + .6), (SITE_W / 2 - .5, -SITE_D / 2 + .6)])
    for x, y in ((6.6, -31.5), (18.4, -5.6), (-17.5, 8.5), (-15.8, -12.5)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 1.6, -18.2, 0.0)
    kit.bike_rack(metal, 7.2, -29.0, math.pi / 2)
    kit.sign_board(furn, 1.0, -32.6, 0.0, colour='#2f5a3b')
    for x, y in ((ENTRANCE['x'] + 1.6, -20.0), (-23.5, 3.5), (23.5, 9.0), (-3.0, 19.6)):
        kit.light_pole(furn, x, y, height=4.5)


def planting(inst, layout):
    rng = random.Random(10010)
    site = layout['site']
    keep_off = shapely.union_all([layout['stone'], layout['ring'], PLAY.buffer(.3), LAWN.buffer(.3)]).buffer(.5)
    meadow = ['blanketflower', 'wild-bergamot', 'goldenrod', 'fireweed', 'rough-fescue-drift', 'feather-reed-grass', 'wild-blue-flax',
              'prickly-wild-rose', 'rough-fescue-drift']
    for x, y in kit.scatter(layout['meadow'].buffer(-.4).intersection(site.buffer(-1.0)), 1.8, rng, keep_off):
        inst.plant(rng.choice(meadow), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    radius = {}

    def reach(slug):
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{p}'][1].positions).reshape(-1, 3)
                                  for p in ('wood', 'foliage') if inst.meshes[f'{key}-{p}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        return radius[slug]
    trees = []
    candidates = kit.scatter(layout['grass'].union(layout['meadow']), 5.0, rng)
    rng.shuffle(candidates)
    for slug, count, gap in (('green-ash', 9, 8.0), ('bur-oak', 6, 9.0), ('littleleaf-linden', 4, 8.0), ('white-spruce', 4, 6.0),
                             ('trembling-aspen', 5, 4.5)):
        placed = 0
        for x, y in candidates:
            if placed >= count:
                break
            scale = rng.uniform(.8, 1.0)
            r = reach(slug) * scale
            p = Point(x, y)
            if not site.buffer(-(r + .3)).contains(p) or keep_off.buffer(1.5).contains(p) or LAWN.buffer(r * .5).contains(p):
                continue
            if PLAY.buffer(r * .6).contains(p) or Point(ENTRANCE['x'], -SITE_D / 2).buffer(4.0).contains(p):
                continue
            if any(math.hypot(x - tx, y - ty) < gap * .5 + (r + tr) * .45 for tx, ty, tr in trees):
                continue
            trees.append((x, y, r))
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
            placed += 1
    return trees


def extra_checks(tris, recipe):
    """Neighbourhood-specific: play equipment stands on the surfacing with a fall zone, and the lawn stays open."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    solid = vertices({'metal', 'timber', 'furniture', 'concrete', 'rock'})            # things that stand, not tree canopies
    play = solid[shapely.contains_xy(PLAY.buffer(2.5), solid[:, 0], solid[:, 1]) & (solid[:, 2] > .3)]
    equipment = play[shapely.contains_xy(PLAY.buffer(-.2), play[:, 0], play[:, 1])]
    inner = PLAY.buffer(-1.8)
    towers_ok = all(inner.contains(Point(x, y)) for x, y in TOWERS)
    lawn = solid[shapely.contains_xy(LAWN.buffer(-.5), solid[:, 0], solid[:, 1]) & (solid[:, 2] > .1)]
    goals = np.abs(np.abs(lawn[:, 0]) - 17.0) < 1.4
    return [('every tower stands at least 1.8 m inside the play surfacing', towers_ok and bool(len(equipment))),
            ('the open lawn holds only the two small goals', not bool((~goals).any()))]


def build():
    parts = Parts(10100)
    layout = plan()
    g, gr = parts['grass'].body, parts['gravel'].body
    kit.fill(g, 'lawn', layout['lawn'], cell=2.5)
    kit.fill(g, 'berm', layout['edge'], cell=2.0)
    kit.fill(g, 'meadow', layout['grass'], cell=2.5)
    kit.fill(g, 'bed', layout['meadow'], z=.004, cell=2.0)
    kit.fill(gr, 'stone_dust', layout['stone'], z=.01, cell=2.0)
    kit.fill(gr, 'fibar', PLAY, z=.03, cell=1.5)
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'neighbourhood')
    ring_line = LineString(list(LAWN.buffer(.2 + RING_W / 2, quad_segs=24).exterior.coords))
    routes = kit.route_segments(LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], -12.5)]), 2.0)
    routes += kit.route_segments(ring_line, 2.0)
    routes += kit.route_segments(LineString([(-14.0, 11.5), (-21.0, 12.5)]), 1.6)
    routes += kit.route_segments(LineString([(-13.0, -7.0), (-21.0, -13.0)]), 1.6)
    routes += kit.route_segments(LineString([(15.6, -7.2), (21.4, -8.0)]), 1.6)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['grass', 'gravel', 'paving'], reference=REFERENCE, routes=routes,
        programme='An open oval lawn for informal play with two small goals, ringed by a stone-dust walk with benches; a '
                  'playground on wood-fibre surfacing with two timber towers, a bridge, a slide, a climbing net, swings, '
                  'boulders and log steppers; a timber picnic shelter with tables; a nature-play corner of boulders and fallen '
                  'logs; a split-rail fence and wildflower meadow along the south edge; lights, bins, a bike rack and scattered '
                  'green ash, bur oak, linden, spruce and aspen.',
        design_basis='Original concept after the catalogue neighborhood park "Rustic Community Park" references (variant 0): '
                     'a central lawn ringed by a path with play and gathering lobes. Equipment sizes are teaching values, not a '
                     'certified play design.',
        limitations=['Prepared level ground only; drainage and irrigation are not designed.',
                     'Play equipment, fall zones and surfacing depths are indicative; real playgrounds follow CSA Z614 and the '
                     'manufacturer.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='neighbourhood',
        description='A neighbourhood park with an open play lawn, a ring walk, a timber playground, a picnic shelter, a nature-play '
                    'corner and shade trees. Prepared level ground.')
    return meshes, nodes, meta
