"""Boulder Block Park: an original native park after the catalogue outdoor climbing and bouldering
wall's "Faceted Boulders" references (frontend/public/archetypes/openspaces/outdoor-climbing-bouldering-wall/variant_0*).

A chain of three joined, angular concrete bouldering blocks (3.2 to 3.6 m) and a separate 2.0 m
children's block, their folded walls leaning and overhanging and dotted with coloured holds, set in one
continuous black rubber fall zone at least 2.5 m wide round every block. A timber seat edge wraps part of the fall zone for spectators; paving, prairie beds and
aspens frame the park. Teaching values, not a climbing-wall design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box

import leisurekit as lk
import parkkit as kit
import playkit as pk
from parkkit import Instances, Parts

PARK_ID = 'student_boulder_block_park_v1'
ARCHETYPE = 'climbing_bouldering_wall'
TITLE = 'Boulder Block Park'
GENERATOR = 'CityPrompt native park batch builder v1 (bouldering)'
REFERENCE = 'frontend/public/archetypes/openspaces/outdoor-climbing-bouldering-wall/variant_0'
KIT_SOURCES = ('playkit.py', 'leisurekit.py')

SITE_W, SITE_D = 40.0, 32.0
FALL = 2.5
REACH = 1.0                      # how far a block's walls can lean or bulge beyond its footprint
BLOCKS = [   # centre, radius, rotation, height, lean, tilt, holds: a joined chain of three, and a children's block
    ((-7.4, 1.0), 2.8, 10.0, 3.55, (.8, .2), (.04, -.05), 70),
    ((-2.9, 3.3), 2.6, 35.0, 3.2, (-.3, .7), (-.05, .03), 60),
    ((1.9, 2.0), 2.8, 5.0, 3.6, (.6, -.5), (.04, .04), 70),
    ((7.6, -5.6), 1.7, 20.0, 2.0, (.3, .15), (.04, 0.0), 35),
]
ENTRANCE = dict(x=0.0, y=-16.0, widthM=3.0, arrivalY=-13.0)
SUNKEN, DEEPEST = None, 0.0


def footprint(centre, radius, rot, sides=6):
    """The same irregular hexagon leisurekit.prism_block stands on."""
    cx, cy = centre
    pts = []
    for k in range(sides):
        a = math.radians(rot) + math.tau * k / sides
        r = radius * (1.0 + .1 * math.sin(k * 2.9 + radius))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    feet = [footprint(c, r, rot) for c, r, rot, *_ in BLOCKS]
    reach = [f.buffer(REACH) for f in feet]                            # the blocks' widest point: bulge and lean
    fall = kit.smooth(shapely.union_all([r.buffer(FALL, quad_segs=16) for r in reach]), 1.0)
    seat = fall.buffer(.55, quad_segs=16).difference(fall).intersection(box(-SITE_W, 4.0, SITE_W, SITE_D))   # the north arc
    beds = shapely.union_all([kit.smooth(box(-20, 9.5, -11.0, 16), 1.5), kit.smooth(box(11.0, 9.5, 20, 16), 1.5),
                              kit.smooth(box(-20, -16, -12.0, -9.5), 1.5), kit.smooth(box(12.0, -16, 20, -9.5), 1.5),
                              kit.smooth(box(-4.5, 11.5, 4.5, 16), 1.2)])
    beds = beds.intersection(site).difference(fall.buffer(1.4)).difference(seat.buffer(.6))
    paving = site.difference(fall).difference(seat).difference(beds)
    return dict(site=site, feet=feet, fall=fall, seat=seat, beds=beds, paving=paving)


def furniture(parts, layout, rng):
    conc, furn, timber, metal = parts['concrete'], parts['furniture'], parts['timber'], parts['metal']
    for c, r, rot, h, lean, tilt, holds in BLOCKS:
        lk.prism_block(conc, furn, rng, c, r, h, rot, lean=lean, tilt=tilt, holds=holds)
    kit.extrude(timber, '#8a6844', layout['seat'], 0, .45, top_colour='#9a7752')
    for x, y in ((-9.0, -12.6), (9.0, -12.6)):
        kit.bench(furn, x, y, math.pi / 2)
    for x, y in ((-3.2, -14.0), (16.0, 6.0)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 3.4, -14.2, 0.0)
    kit.bike_rack(metal, -7.0, -14.6, 0.0, loops=4)
    kit.sign_board(furn, 5.6, -15.0, 0.0, colour='#c8772f')
    for x, y in ((-16.0, 0.0), (16.0, 0.0), (0.0, 12.0)):
        kit.light_pole(furn, x, y, height=4.5)
    furn.box((14.8, -4.0, .45), (1.4, .8, .9), '#4a5a6a')                # a lockable gear box for brushes and pads


def planting(inst, layout):
    rng = random.Random(13013)
    site = layout['site']
    keep_off = shapely.union_all([layout['paving'], layout['fall'], layout['seat']]).buffer(.35)
    mix = ['feather-reed-grass', 'rough-fescue-drift', 'blue-grama', 'blanketflower', 'shrubby-cinquefoil', 'wolf-willow', 'snowberry']
    for x, y in kit.scatter(layout['beds'].buffer(-.35).intersection(site.buffer(-1.0)), 1.6, rng, keep_off):
        inst.plant(rng.choice(mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    for x, y in ((-16.5, 13.2), (-13.2, 13.0), (16.5, 13.2), (13.2, 13.0), (-16.0, -13.0), (16.0, -13.0), (0.0, 14.2)):
        edge = min(SITE_W / 2 - abs(x), SITE_D / 2 - abs(y)) - .2
        inst.plant('trembling-aspen', x, y, yaw=rng.uniform(0, math.tau), scale=min(.85, edge / 2.76))


def extra_checks(tris, recipe):
    """Bouldering-specific: every block stands in at least 2.5 m of fall surfacing and stays under 4 m."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    conc = vertices({'concrete'})
    layout = plan()
    rubber = vertices({'rubber'})
    ok_zone = all(layout['fall'].buffer(-FALL + .05).contains(f.buffer(REACH)) for f in layout['feet'])
    blocks = conc[shapely.contains_xy(shapely.union_all(layout['feet']).buffer(REACH + .1), conc[:, 0], conc[:, 1])]
    reach_ok = bool(shapely.contains_xy(shapely.union_all(layout['feet']).buffer(REACH), blocks[:, 0], blocks[:, 1]).all())
    return [('every block has at least 2.5 m of rubber fall surfacing beyond its widest point', ok_zone and reach_ok and bool(len(rubber))),
            ('every block is under 4 m tall', bool(len(blocks)) and float(blocks[:, 2].max()) < 4.0)]


def build():
    parts = Parts(13100)
    layout = plan()
    rng = random.Random(1301)
    kit.fill(parts['rubber'].body, 'safety_black', layout['fall'], z=.04, cell=1.5)
    kit.fill(parts['paving'].body, 'pavers', layout['paving'], z=0.0, cell=2.0)
    kit.fill(parts['grass'].body, 'bed', layout['beds'], z=.004, cell=1.8)
    pk.paver_bands(parts['furniture'], layout['paving'], spacing=4.0, origin=(0.0, 0.0))
    furniture(parts, layout, rng)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'bouldering')
    ring = LineString(list(layout['fall'].buffer(1.2).exterior.coords))
    routes = kit.route_segments(LineString([(0, -SITE_D / 2), (0, layout['fall'].bounds[1] - .6)]), 2.4)
    routes += kit.route_segments(ring, 1.4)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'rubber', 'grass'], reference=REFERENCE, routes=routes,
        programme='A chain of three joined, angular concrete bouldering blocks (3.2 to 3.6 m) and a 2.0 m children\'s block '
                  'with leaning and overhanging walls and coloured holds, set in one continuous black rubber fall zone at least 2.5 m wide; a timber seat edge for '
                  'spectators; banded paving, benches, a drinking fountain, a gear box, bike racks, lights, prairie beds and aspens.',
        design_basis='Original concept after the catalogue bouldering "Faceted Boulders" references (variant 0). Heights, fall '
                     'zones and holds are teaching values, not a climbing-wall design.',
        limitations=['Prepared level ground only.',
                     'Block structure, hold layout, route grades and fall surfacing depth follow the manufacturer and the '
                     'applicable climbing-wall and play standards (for example EN 12572-2), not this model.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='Angular concrete bouldering blocks with coloured holds in a black rubber fall zone, with a timber seat edge and '
                    'prairie planting. Prepared level ground.')
    return meshes, nodes, meta
