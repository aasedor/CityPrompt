"""Walled Memorial Garden: an original native park after the catalogue memorial garden's
"Cottage Romantic" references (frontend/public/archetypes/openspaces/memorial-garden/variant_3*).

A brick-walled garden entered through a rose arbour: a long reflecting pool on the
axis, stone paths and terraces, a perimeter gravel walk, hedged beds of perennials and
roses, borders of columnar trees along the walls, and a back terrace with a wall of
blank plaques. Lawn and trees surround the walls.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, box

import parkkit as kit
from parkkit import Instances, Parts

PARK_ID = 'student_walled_memorial_garden_v1'
ARCHETYPE = 'memorial_garden'
TITLE = 'Walled Memorial Garden'
GENERATOR = 'CityPrompt native park batch builder v1 (memorial)'
REFERENCE = 'frontend/public/archetypes/openspaces/memorial-garden/variant_3'

SITE_W, SITE_D = 36.0, 50.0
ENTRANCE = dict(x=0, y=-25, widthM=3.0, arrivalY=-22)
WALL_X, WALL_FRONT, WALL_BACK, THICK = 13.0, -19.0, 21.0, .35
SIDE_H, FRONT_H, GATE = 2.6, 1.05, 1.6          # wall heights; half-width of the gate opening
BORDER, WALK = 2.4, 1.6                          # wall borders, then the perimeter walk
CROSS_Y = 3.0
WATER_Z = -.25
BRICK, BRICK_DARK, COPING, STONE = '#8d5b45', '#7a4c39', '#cfc6b4', '#c8bfae'
TIMBER = '#8c6a4a'

POOL = kit.smooth(box(-2.5, -5.5, 2.5, 11.5), 2.2)          # rounded ends, as in the reference
SUNKEN, DEEPEST = POOL, WATER_Z - .02


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    inner = box(-WALL_X + THICK / 2, WALL_FRONT + THICK / 2, WALL_X - THICK / 2, WALL_BACK - THICK / 2)
    walls_outline = box(-WALL_X - THICK / 2, WALL_FRONT - THICK / 2, WALL_X + THICK / 2, WALL_BACK + THICK / 2)
    walk_outer = inner.buffer(-BORDER, join_style='mitre')
    walk_inner = inner.buffer(-BORDER - WALK, join_style='mitre')
    walk = walk_outer.difference(walk_inner)
    coping = POOL.buffer(.4, quad_segs=16).difference(POOL)
    terrace = POOL.buffer(2.4, quad_segs=16).difference(POOL.buffer(.4, quad_segs=16))
    axis_front = box(-1.5, WALL_FRONT, 1.5, -5.5)
    axis_back = box(-1.5, 11.5, 1.5, 16.0)
    back_terrace = box(-6.0, 16.0, 6.0, WALL_BACK - THICK / 2)
    cross = box(-WALL_X + BORDER, CROSS_Y - 1.0, WALL_X - BORDER, CROSS_Y + 1.0)
    stone = shapely.union_all([terrace, axis_front, axis_back, back_terrace, cross]).intersection(inner).difference(POOL.buffer(.4))
    gravel = walk.difference(stone)
    central = walk_inner.difference(stone).difference(POOL.buffer(.4))
    beds = [b for b in kit.polygons(central) if b.area > 2]
    borders = inner.difference(walk_outer).difference(stone).difference(back_terrace.buffer(.01))
    entry = box(-1.5, -SITE_D / 2, 1.5, WALL_FRONT - THICK / 2).union(box(-GATE, WALL_FRONT - THICK / 2 - .01, GATE, WALL_FRONT + THICK / 2 + .01))
    outer_beds = shapely.union_all([box(-WALL_X, WALL_FRONT - 2.2, -2.6, WALL_FRONT - THICK / 2),
                                    box(2.6, WALL_FRONT - 2.2, WALL_X, WALL_FRONT - THICK / 2)])
    lawn = site.difference(walls_outline).difference(entry).difference(outer_beds)
    return dict(site=site, inner=inner, walk=gravel, stone=stone, coping=coping, beds=beds, borders=borders, entry=entry,
                outer_beds=outer_beds, lawn=lawn, back_terrace=back_terrace)


# ---- walls, gate and arbour --------------------------------------------------------------------
def wall_run(conc, x0, y0, x1, y1, height):
    """A brick wall with a stone coping and a dark plinth course."""
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    nx, ny = -uy * THICK / 2, ux * THICK / 2
    body = shapely.geometry.Polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
    kit.extrude(conc, BRICK, body, 0, height - .08)
    kit.extrude(conc, COPING, body.buffer(.04, join_style='mitre'), height - .08, height)
    kit.extrude(conc, BRICK_DARK, body.buffer(.01, join_style='mitre'), 0, .3)
    # brick courses: a slightly darker line every 0.3 m on both faces
    for z in np.arange(.6, height - .2, .3):
        for side in (1, -1):
            ox, oy = nx * (1 + .03 / (THICK / 2)) * side, ny * (1 + .03 / (THICK / 2)) * side
            conc.quad((x0 + ox, y0 + oy, z), (x1 + ox, y1 + oy, z), (x1 + ox, y1 + oy, z + .018), (x0 + ox, y0 + oy, z + .018), '#6f4434')


def walls(conc):
    wall_run(conc, -WALL_X, WALL_FRONT, -WALL_X, WALL_BACK, SIDE_H)
    wall_run(conc, WALL_X, WALL_FRONT, WALL_X, WALL_BACK, SIDE_H)
    wall_run(conc, -WALL_X - THICK / 2, WALL_BACK, WALL_X + THICK / 2, WALL_BACK, SIDE_H)
    wall_run(conc, -WALL_X - THICK / 2, WALL_FRONT, -GATE, WALL_FRONT, FRONT_H)
    wall_run(conc, GATE, WALL_FRONT, WALL_X + THICK / 2, WALL_FRONT, FRONT_H)
    for x in (-GATE - .25, GATE + .25):                          # gate piers with stone caps
        kit.extrude(conc, BRICK, box(x - .25, WALL_FRONT - .25, x + .25, WALL_FRONT + .25), 0, 1.6)
        kit.extrude(conc, COPING, box(x - .3, WALL_FRONT - .3, x + .3, WALL_FRONT + .3), 1.6, 1.72)
    # the plaque wall at the back: a stone panel with a grid of blank bronze-toned plaques
    kit.extrude(conc, STONE, box(-3.6, WALL_BACK - THICK / 2 - .12, 3.6, WALL_BACK - THICK / 2), 0, 2.2)
    for col in range(6):
        for row in range(3):
            x = -3.0 + col * 1.2
            z = .75 + row * .5
            conc.box((x, WALL_BACK - THICK / 2 - .13, z), (.9, .02, .36), '#8a7350')


def arbour(timber, metal):
    """A timber rose arbour over the gate, with an open picket gate swung back on each side."""
    for x in (-1.45, 1.45):
        for y in (WALL_FRONT - .45, WALL_FRONT + .45):
            timber.box((x, y, 1.25), (.12, .12, 2.5), TIMBER)
    for y in (WALL_FRONT - .45, WALL_FRONT + .45):
        arc = [(1.45 * math.cos(a), y, 2.5 + .55 * math.sin(a)) for a in np.linspace(0, math.pi, 13)]
        kit.tube(timber, arc, .05, TIMBER, sides=6)
    for k in range(9):
        a = math.pi * k / 8
        p = (1.45 * math.cos(a), WALL_FRONT - .5, 2.5 + .55 * math.sin(a))
        timber.cyl(p, (p[0], WALL_FRONT + .5, p[2]), .03, TIMBER, sides=5)
    for side in (-1, 1):                                        # gate leaves opened inward against the wall
        x0 = side * (GATE - .05)
        for k in range(9):
            y = WALL_FRONT + .1 + k * .14
            timber.box((x0, y, .55), (.03, .07, 1.0 - .1 * abs(k - 4) / 4), '#d9d2c2')
        for z in (.25, .85):
            timber.box((x0, WALL_FRONT + .66, z), (.04, 1.3, .06), '#d9d2c2')


def pool(parts):
    """A rounded reflecting pool: stone coping, inner walls down to the water and a still surface."""
    conc, pave = parts['concrete'], parts['paving']
    coping = POOL.buffer(.4, quad_segs=16).difference(POOL)
    kit.extrude(pave, COPING, coping, 0, .15)
    ring = kit.sample_ring(POOL.exterior, .4)
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        conc.quad((bx, by, WATER_Z), (ax, ay, WATER_Z), (ax, ay, .15), (bx, by, .15), '#9a958b')
    kit.fill(parts['water'].body, 'water', POOL, z=WATER_Z, cell=3.0)


def hedges(parts, layout):
    hedge = parts['foliage']
    for bed in layout['beds']:
        frame = bed.difference(bed.buffer(-.45, join_style='mitre'))
        kit.extrude(hedge, '#3f5a31', frame, 0, .55, top_colour='#4b6a38')


# ---- planting and furniture ----------------------------------------------------------------------------
def planting(inst, layout):
    rng = random.Random(5150)
    keep_off = shapely.union_all([layout['stone'], layout['walk'], layout['entry'], POOL.buffer(.5)]).buffer(.45)
    flowers = ['wild-bergamot', 'blanketflower', 'fireweed', 'goldenrod', 'prickly-wild-rose', 'prickly-wild-rose', 'shrubby-cinquefoil',
               'wild-blue-flax', 'feather-reed-grass', 'snowberry']
    for bed in layout['beds']:
        for x, y in kit.scatter(bed.buffer(-.75), 1.3, rng):
            inst.plant(rng.choice(flowers), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.25))
    borders = layout['borders']
    # columnar aspens in a steady rhythm along the side and back borders, flowers and shrubs between
    for y in np.arange(-14.5, 19.0, 4.2):
        for x in (-WALL_X + 1.2, WALL_X - 1.2):
            if borders.contains(Point(x, y)):
                inst.plant('swedish-columnar-aspen', x, y, yaw=rng.uniform(0, math.tau))
    for x in np.arange(-10.5, 11.0, 4.2):
        if borders.contains(Point(x, WALL_BACK - 1.4)) and abs(x) > 6.5:
            inst.plant('swedish-columnar-aspen', x, WALL_BACK - 1.4, yaw=rng.uniform(0, math.tau))
    for x, y in kit.scatter(borders.buffer(-.45), 1.5, rng, keep_off):
        if all(math.hypot(x - px, y - py) > .9 for px, py in ((-WALL_X + 1.2, yy) for yy in np.arange(-14.5, 19.0, 4.2))) and \
                all(math.hypot(x - px, y - py) > .9 for px, py in ((WALL_X - 1.2, yy) for yy in np.arange(-14.5, 19.0, 4.2))):
            inst.plant(rng.choice(flowers + ['common-lilac', 'saskatoon']), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(.95, 1.2))
    for x, y in kit.scatter(layout['outer_beds'].buffer(-.35), 1.0, rng):
        inst.plant(rng.choice(['wild-bergamot', 'prickly-wild-rose', 'blanketflower', 'fireweed']), x, y, yaw=rng.uniform(0, math.tau))
    for x in (-1.7, 1.7):                                         # roses climbing the arbour posts
        for y in (WALL_FRONT - .75, WALL_FRONT + .75):
            inst.plant('prickly-wild-rose', x, y, yaw=rng.uniform(0, math.tau), scale=1.3)
    trees = [('green-ash', -16.0 + 1.0, 17.5), ('green-ash', 16.0 - 1.0, 17.5), ('bur-oak', -15.0 + .4, -1.0), ('bur-oak', 15.0 - .4, -1.0)]
    for slug, x, y in trees:
        inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=.62)


def furniture(parts):
    furn = parts['furniture']
    for x, y, yaw in ((-3.9, -1.0, 0.0), (3.9, -1.0, math.pi), (-3.9, 8.0, 0.0), (3.9, 8.0, math.pi), (0.0, 18.6, -math.pi / 2)):
        kit.bench(furn, x, y, yaw)
    for x, y in ((-2.2, -23.0), (2.4, 17.8)):
        kit.waste_bin(furn, x, y)
    for x, y in ((-1.9, WALL_FRONT - 3.5), (1.9, WALL_FRONT - 3.5)):
        kit.light_pole(furn, x, y, height=3.6)
    kit.sign_board(furn, 2.4, -24.0, 0.0, colour='#2f4a3b')


def extra_checks(tris, recipe):
    """Memorial-specific: the pool is one still water plane, and the walls close the garden except at the gate."""
    water = np.concatenate([t for n, t, _, _ in tris if n == 'water']).reshape(-1, 3)
    conc = np.concatenate([t for n, t, _, _ in tris if n == 'concrete']).reshape(-1, 3)
    tall = conc[conc[:, 2] > 2.4]
    side = tall[(np.abs(np.abs(tall[:, 0]) - WALL_X) < .25)]
    return [(f'the pool is one water plane {abs(WATER_Z):.2f} m below the coping', bool(np.allclose(water[:, 2], WATER_Z, atol=1e-4))),
            ('both side walls stand 2.6 m along their full length',
             bool(len(side) and side[:, 1].min() <= WALL_FRONT + .3 and side[:, 1].max() >= WALL_BACK - .3))]


def build():
    parts = Parts(5100)
    layout = plan()
    kit.fill(parts['paving'].body, 'stone', layout['stone'], z=.01, cell=1.5)
    kit.fill(parts['paving'].body, 'stone', layout['entry'], z=.01, cell=1.5)
    kit.fill(parts['gravel'].body, 'gravel', layout['walk'], z=.005, cell=1.5)
    for bed in layout['beds']:
        kit.fill(parts['mud'].body, 'bed', bed, z=.004, cell=1.5)
    kit.fill(parts['mud'].body, 'bed', layout['borders'], z=.004, cell=1.5)
    kit.fill(parts['mud'].body, 'bed', layout['outer_beds'], z=.004, cell=1.5)
    kit.fill(parts['grass'].body, 'lawn', layout['lawn'], cell=2.5)
    pool(parts)
    walls(parts['concrete'])
    arbour(parts['timber'], parts['metal'])
    hedges(parts, layout)
    furniture(parts)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'memorial')
    axis = LineString([(0, -SITE_D / 2), (0, -7.4)])
    ring = LineString(POOL.buffer(1.65, quad_segs=16).exterior.coords)          # the middle of the stone pool terrace
    xm = WALL_X - THICK / 2 - BORDER - WALK / 2                   # the walk's centre line, measured from the inner wall faces
    yb, yf = WALL_BACK - THICK / 2 - BORDER - WALK / 2, WALL_FRONT + THICK / 2 + BORDER + WALK / 2
    perimeter = LineString([(-xm, yf), (-xm, yb), (xm, yb), (xm, yf), (-xm, yf)])
    cross = LineString([(-xm, CROSS_Y), (-4.8, CROSS_Y)])
    cross_e = LineString([(4.8, CROSS_Y), (xm, CROSS_Y)])
    back = LineString([(0, 13.8), (0, 18.6)])
    routes = (kit.route_segments(axis, 2.6) + kit.route_segments(ring, 1.4)
              + kit.route_segments(perimeter, 1.4) + kit.route_segments(cross, 1.6) + kit.route_segments(cross_e, 1.6)
              + kit.route_segments(back, 2.0))
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'gravel', 'grass'], reference=REFERENCE, routes=routes,
        programme='A brick-walled garden entered through a timber rose arbour: a 5 by 17 m reflecting pool with stone coping on the '
                  'axis, a stone pool terrace, cross and axis paths, a perimeter gravel walk, four hedged beds of perennials and roses, '
                  'borders of Swedish columnar aspen along the walls, and a back terrace with a bench before a wall of blank plaques; '
                  'lawn, flower beds along the front wall, and green ash and bur oak outside.',
        design_basis='Original concept after the catalogue memorial garden "Cottage Romantic" references (variant 3): a walled garden '
                     'with a long reflecting pool, flower borders and a rose-arched gate. Columnar aspen stand in for the reference\'s '
                     'cypress, which do not grow in Calgary.',
        limitations=['Prepared level ground only. The pool water sits 0.25 m below its coping; depth, filtration and safety are not designed.',
                     'The plaques are blank: the garden commemorates no real person or event.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='gardens',
        description='A brick-walled garden with a long reflecting pool, hedged flower beds, columnar trees, a rose arbour and a wall of '
                    'blank plaques. Prepared level ground.')
    return meshes, nodes, meta
