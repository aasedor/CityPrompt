"""Prairie Pollinator Meadow: an original native park after the catalogue pollinator meadow's
"Wildflower Walk" references (frontend/public/archetypes/openspaces/pollinator-meadow-wildflower-garden/variant_1*).

A native wildflower meadow for bees, butterflies and other pollinators: a winding stone-dust
walk from the entrance to a gathering circle, a mown grass loop through the meadow, dense beds of
prairie flowers and grasses, three bee hotels facing the morning sun, interpretive lecterns at
the junctions, benches, and saskatoon, chokecherry and aspen at the edges. Teaching values, not
a planting plan.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, box

import leisurekit as lk
import parkkit as kit
import playkit  # noqa: F401  (stone dust and the other batch 3 ground colours)
from parkkit import Instances, Parts

PARK_ID = 'student_prairie_pollinator_meadow_v1'
ARCHETYPE = 'pollinator_meadow'
TITLE = 'Prairie Pollinator Meadow'
GENERATOR = 'CityPrompt native park batch builder v1 (meadow)'
REFERENCE = 'frontend/public/archetypes/openspaces/pollinator-meadow-wildflower-garden/variant_1'
KIT_SOURCES = ('playkit.py', 'leisurekit.py')

SITE_W, SITE_D = 48.0, 36.0
MAIN = LineString(kit.chaikin([(0.0, -18.5), (0.0, -15.0), (-6.0, -9.0), (3.0, -2.0), (-3.5, 5.0), (0.0, 9.0)], 4))
CIRCLE = Point(0.0, 11.5).buffer(3.4, quad_segs=24)
LOOP = kit.ellipse(0.0, -.5, 17.0, 11.0, 0.0, n=96)
MAIN_W, LOOP_W = 1.8, 1.5
HOTELS = [((-5.2, 12.8), math.radians(-45)), ((13.2, -5.0), math.radians(-60)), ((-15.0, -2.0), math.radians(-30))]   # facing south-east


def lecterns():
    """Interpretive lecterns beside the main walk at set fractions of its length, alternating sides, facing it."""
    out = []
    for k, f in enumerate((.14, .38, .62, .84)):
        d = f * MAIN.length
        (x, y), (x2, y2) = MAIN.interpolate(d).coords[0], MAIN.interpolate(d + .2).coords[0]
        tx, ty = (x2 - x) / math.hypot(x2 - x, y2 - y), (y2 - y) / math.hypot(x2 - x, y2 - y)
        side = 1 if k % 2 else -1
        nx, ny = -ty * side, tx * side
        out.append(((x + nx * 1.45, y + ny * 1.45), math.atan2(-nx, ny)))
    return out


LECTERNS = lecterns()
FLOWERS = ['wild-bergamot', 'blanketflower', 'goldenrod', 'fireweed', 'wild-blue-flax', 'prairie-crocus', 'prairie-smoke',
           'pasture-sage', 'shrubby-cinquefoil', 'prickly-wild-rose']
GRASSES = ['rough-fescue-drift', 'blue-grama', 'feather-reed-grass', 'june-grass']
ENTRANCE = dict(x=0.0, y=-18.0, widthM=1.8, arrivalY=-15.0)
SUNKEN, DEEPEST = None, 0.0


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    main = MAIN.buffer(MAIN_W / 2, quad_segs=8).union(CIRCLE).intersection(site)
    loop_line = LineString(list(LOOP.exterior.coords))
    mown = loop_line.buffer(LOOP_W / 2, quad_segs=8).difference(main).intersection(site)
    beds = site.difference(main).difference(mown)
    return dict(site=site, main=main, mown=mown, beds=beds, loop=loop_line)


def furniture(parts, layout):
    furn, timber, metal = parts['furniture'], parts['timber'], parts['metal']
    for (x, y), yaw in HOTELS:
        lk.bee_hotel(timber, furn, x, y, yaw)
    for (x, y), yaw in LECTERNS:
        lk.lectern(furn, x, y, yaw, colour='#5a6a3a')
    for ang in (200.0, 270.0, 340.0):                                    # benches round the circle, facing in
        a = math.radians(ang)
        x, y = 2.6 * math.cos(a), 11.5 + 2.6 * math.sin(a)
        kit.bench(furn, x, y, a + math.pi)
    for x, y, yaw in ((-14.6, 9.8, math.radians(-120)), (15.8, 6.4, math.radians(-150))):
        kit.bench(furn, x, y, yaw)
    for x, y in ((-1.8, -17.0), (2.6, 13.6)):
        kit.waste_bin(furn, x, y)
    kit.sign_board(furn, -2.0, -17.6, 0.0, colour='#5a6a3a')
    kit.bike_rack(metal, 3.4, -17.0, 0.0)


def planting(inst, layout):
    rng = random.Random(14014)
    site = layout['site']
    keep_off = shapely.union_all([layout['main'], layout['mown']]).buffer(.35)
    hotels = shapely.union_all([Point(*p).buffer(.8) for p, _ in HOTELS] + [Point(*p).buffer(.8) for p, _ in LECTERNS])
    # drifts: flowers cluster in patches by species rather than an even salt-and-pepper mix
    centres = [(rng.uniform(-22, 22), rng.uniform(-16, 16), rng.choice(FLOWERS)) for _ in range(26)]
    for x, y in kit.scatter(layout['beds'].buffer(-.25).intersection(site.buffer(-1.3)), 2.05, rng, keep_off.union(hotels)):
        near = min(centres, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)
        slug = near[2] if rng.random() < .62 else rng.choice(GRASSES)
        inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.15, 1.5))
    for slug, x, y, s in (('saskatoon', -21.5, 15.4, 1.0), ('schubert-chokecherry', 21.0, 15.0, .55), ('trembling-aspen', -21.6, -15.2, .7),
                          ('saskatoon', 21.6, -15.6, 1.0), ('trembling-aspen', 21.4, -2.0, .7), ('schubert-chokecherry', -21.0, 2.0, .55)):
        if not keep_off.buffer(.5).contains(Point(x, y)):
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=s)


def extra_checks(tris, recipe):
    """Meadow-specific: many native flowering species, bee hotels facing the morning sun, lecterns on the walks."""
    species = {name.rsplit('-', 2)[0] for _, _, name, _ in tris if any(name.startswith(f + '-') for f in FLOWERS)}
    facing = all(-math.pi / 2 - .01 <= yaw <= .01 for _, yaw in HOTELS)
    walks = plan()
    lecterns = all(walks['main'].buffer(1.6).contains(Point(*p)) for p, _ in LECTERNS)
    return [(f'{len(species)} native flowering species in the beds', len(species) >= 9),
            ('every bee hotel faces between east and south', facing),
            ('every interpretive lectern stands beside the main walk', lecterns)]


def build():
    parts = Parts(14100)
    layout = plan()
    g = parts['grass'].body
    kit.fill(g, 'bed', layout['beds'], z=0.0, cell=2.0)
    kit.fill(g, 'lawn', layout['mown'], z=.005, cell=1.5)
    kit.fill(parts['gravel'].body, 'stone_dust', layout['main'], z=.01, cell=1.5)
    furniture(parts, layout)
    bloom_area = layout['beds'].buffer(-.3).intersection(layout['site'].buffer(-.4))
    lk.bloom_field(parts['foliage'], bloom_area, random.Random(1401), count=5200)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'meadow')
    routes = kit.route_segments(MAIN, 1.6) + kit.route_segments(layout['loop'], 1.3)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['gravel', 'grass'], reference=REFERENCE, routes=routes,
        programme='A native wildflower meadow: drifts of wild bergamot, blanketflower, goldenrod, fireweed, wild blue flax, prairie '
                  'crocus, prairie smoke, pasture sage, cinquefoil and wild rose among rough fescue, blue grama, feather reed '
                  'grass and june grass, with massed low blooms in drifts; a winding stone-dust walk to a gathering circle with benches; a mown grass loop; three '
                  'bee hotels facing the morning sun; four interpretive lecterns; saskatoon, chokecherry and aspen at the edges.',
        design_basis='Original concept after the catalogue pollinator meadow "Wildflower Walk" references (variant 1). Species '
                     'are prairie natives from the shared plant library; the mix is a teaching value, not a planting plan.',
        limitations=['Prepared level ground only; soil preparation, seeding rates and establishment care are not designed.',
                     'Meadows change through the seasons; the model shows midsummer bloom. Lectern panels are blank.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='nature',
        description='A native wildflower meadow with a winding walk, a mown loop, bee hotels and interpretive lecterns. Prepared '
                    'level ground.')
    return meshes, nodes, meta
