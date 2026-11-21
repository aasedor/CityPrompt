"""Village Green Cricket Ground: an original native park after the catalogue cricket ground's
"Village Green" references (frontend/public/archetypes/openspaces/cricket-ground/variant_0*).

A rounded ground inside a white picket fence: a striped outfield, a boundary rope 42 to
46 m from the pitch centre, a square of prepared strips with the active 22-yard pitch,
creases and stumps, white sight screens at both ends, a timber-framed pavilion with a
veranda and a terrace of benches, a scoreboard, a roller, and shade trees outside the
fence. Teaching values, not a ground design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box

import parkkit as kit
import sportskit as sk
from parkkit import Instances, Parts

PARK_ID = 'student_village_green_cricket_v1'
ARCHETYPE = 'cricket_pitch_oval'
TITLE = 'Village Green Cricket Ground'
GENERATOR = 'CityPrompt native park batch builder v1 (cricket)'
REFERENCE = 'frontend/public/archetypes/openspaces/cricket-ground/variant_0'
KIT_SOURCES = ('sportskit.py',)

SITE_W = SITE_D = 120.0
STUMPS = 20.12 / 2               # 22 yards between the stumps, the pitch along x
POPPING = 1.22                   # popping crease in front of the stumps
PITCH_W = 3.05
ROPE = (46.0, 42.0, 20.0)        # boundary rope half-length, half-width and corner radius
FENCE = (51.0, 47.0, 10.0)       # picket fence
PAV = (-10.0, 10.0, -56.0, -49.0)  # pavilion body x0, x1, y0 (back), y1 (front wall)
VERANDA = -47.0
TERRACE = -44.6
GATES = ((16.0, 2.4, -1), (-20.0, 3.6, 1))      # (x, width, side): the south entrance gate and a north maintenance gate
ENTRANCE = dict(x=16.0, y=-60.0, widthM=2.4, arrivalY=-57.0)
SUNKEN, DEEPEST = None, 0.0
RENDER, FRAMING, ROOF_TILE, GLASS = '#ece6d8', '#4a3626', '#5b3a2a', '#2c3a40'


def rounded(hx, hy, r):
    return kit.smooth(box(-hx, -hy, hx, hy), r)


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    ground = rounded(*FENCE)
    rope = rounded(*ROPE)
    square = box(-13.0, -15.25, 13.0, 15.25)
    pitch = box(-STUMPS - POPPING - .6, -PITCH_W / 2, STUMPS + POPPING + .6, PITCH_W / 2)
    veranda = box(PAV[0] - .4, PAV[3], PAV[1] + .4, VERANDA)
    terrace = box(PAV[0] - 2.0, VERANDA, PAV[1] + 2.0, TERRACE)
    gx = GATES[0][0]
    spur = box(gx - 1.2, -SITE_D / 2, gx + 1.2, -FENCE[1] + .9)
    rear = box(-1.5, -SITE_D / 2, 1.5, PAV[2])                       # a service path to the pavilion's rear door
    link = box(PAV[1] + 2.0, -FENCE[1] - 3.4, gx + 1.2, -FENCE[1] - 1.0)   # a walk from the gate path to the pavilion side
    paving = shapely.union_all([veranda, terrace]).intersection(site)
    gravel = shapely.union_all([spur, rear, link]).difference(paving).difference(box(PAV[0], PAV[2], PAV[1], PAV[3]))
    field = ground.difference(square).difference(paving).difference(gravel)
    outside = site.difference(ground).difference(gravel).difference(box(PAV[0] - .4, PAV[2] - .4, PAV[1] + .4, VERANDA))
    beds = shapely.union_all([box(PAV[0] - 6.0, -SITE_D / 2 + .6, PAV[0] - .8, PAV[2] - .4), box(PAV[1] + .8, -SITE_D / 2 + .6, PAV[1] + 6.0, PAV[2] - .4),
                              kit.smooth(kit.ellipse(-48.0, -54.0, 9.0, 3.2, 0.0), 1.5), kit.smooth(kit.ellipse(48.0, 54.5, 9.0, 3.0, 0.0), 1.5)])
    beds = beds.intersection(outside.buffer(-.5)).difference(gravel.buffer(.8))
    lawn = outside.difference(beds)
    loop = LineString(list(rounded(FENCE[0] - 2.6, FENCE[1] - 2.6, FENCE[2] + 2.0).exterior.coords))
    return dict(site=site, ground=ground, rope=rope, square=square, pitch=pitch, veranda=veranda, terrace=terrace, spur=spur,
                paving=paving, gravel=gravel, field=field, outside=outside, beds=beds, lawn=lawn, loop=loop)


# ---- the pitch ---------------------------------------------------------------------------------
def pitch_markings(furn, timber):
    lines = []
    for e in (-1, 1):
        bowl = e * STUMPS
        pop = e * (STUMPS - POPPING)
        lines += [box(bowl - .025, -1.32, bowl + .025, 1.32),                 # bowling crease
                  box(pop - .025, -1.83, pop + .025, 1.83)]                   # popping crease
        for s in (-1, 1):                                                     # return creases
            lines.append(box(min(pop, e * (STUMPS + POPPING)), s * 1.32 - .025, max(pop, e * (STUMPS + POPPING)), s * 1.32 + .025))
    sk.chalk(furn, shapely.union_all(lines), z=.014)
    stump = '#e2d3b0'
    for e in (-1, 1):
        x = e * STUMPS
        for y in (-.1, 0.0, .1):
            furn.cyl((x, y, 0), (x, y, .711), .018, stump, sides=6)
        for y0, y1 in ((-.105, 0.0), (0.0, .105)):
            furn.box((x, (y0 + y1) / 2, .72), (.03, .1, .022), stump)


def boundary(furn):
    sk.chalk(furn, rounded(*ROPE).exterior.buffer(.045), z=.03, colour='#f4f3ee')
    for k, d in enumerate(np.arange(0, rounded(*ROPE).exterior.length, 18.0)):     # small boundary markers
        x, y = rounded(*ROPE).exterior.interpolate(d).coords[0]
        r = math.hypot(x, y)
        ox, oy = x / r * .6, y / r * .6
        furn.cyl((x + ox, y + oy, 0), (x + ox, y + oy, .32), .13, '#f4f3ee', r1=.02, sides=8)


def sight_screen(metal, x, facing):
    """A white wheeled sight screen, 7 m wide and 4 m tall, its face toward the pitch."""
    with metal.at(x, 0, 0, facing):
        metal.box((0, 0, 2.35), (.12, 7.0, 4.0), '#f6f5f0')
        for y in (-3.0, 0.0, 3.0):
            metal.cyl((-.06, y, .2), (-1.4, y, .2), .05, '#6f777b', sides=6)
            metal.cyl((-.06, y, 4.1), (-1.4, y, .2), .045, '#6f777b', sides=6)
            metal.cyl((-1.4, y - .25, .18), (-1.4, y + .25, .18), .18, '#2f3438', sides=10)


def roller(metal, x, y):
    with metal.at(x, y, 0, 0.0):
        metal.cyl((-.8, 0, .4), (.8, 0, .4), .4, '#3e4a3f', sides=16)
        metal.box((0, -.9, .7), (1.7, .6, .7), '#3e4a3f')
        kit.tube(metal, [(-.7, .2, .5), (0, 1.9, .95), (.7, .2, .5)], .03, '#2f3438')


# ---- the pavilion ------------------------------------------------------------------------------
def pavilion(conc, timber, furn):
    x0, x1, y0, y1 = PAV
    h, ridge = 3.2, 6.4
    kit.extrude(conc, RENDER, box(x0, y0, x1, y1), 0, h)
    kit.extrude(conc, '#8c8579', box(x0 - .05, y0 - .05, x1 + .05, y1 + .05), 0, .45)      # plinth
    mid = (y0 + y1) / 2
    for xe in (x0, x1):                                                            # gable ends
        conc.tri((xe, y0, h), (xe, y1, h), (xe, mid, ridge), RENDER)
    o = .5
    for ya, yb in ((y0 - o, mid), (y1 + o, mid)):
        za = h - o * (ridge - h) / (mid - y0)
        timber.quad((x0 - .4, ya, za), (x1 + .4, ya, za), (x1 + .4, yb, ridge), (x0 - .4, yb, ridge), ROOF_TILE)
        timber.quad((x0 - .4, ya, za + .08), (x0 - .4, yb, ridge + .08), (x1 + .4, yb, ridge + .08), (x1 + .4, ya, za + .08), ROOF_TILE)
    timber.box(((x0 + x1) / 2, mid, ridge + .08), (x1 - x0 + .9, .22, .16), '#4a2e22')
    # timber framing and windows on the front (north) face
    for x in np.arange(x0 + .15, x1, 1.25):
        timber.box((x, y1 + .04, h / 2 + .2), (.14, .06, h - .4), FRAMING)
    for z in (.95, 2.55, h - .1):
        timber.box(((x0 + x1) / 2, y1 + .04, z), (x1 - x0, .06, .14), FRAMING)
    for x in np.arange(x0 + .78, x1 - .5, 2.5):
        if abs(x) > 1.6:
            conc.box((x, y1 + .02, 1.75), (1.0, .04, 1.4), GLASS, gloss=True)
    conc.box((0, y1 + .03, 1.1), (2.2, .05, 2.2), '#3b2a1f')                       # double doors
    # a cross gable over the doors with a blank clock face
    gx0, gx1, gz = -2.6, 2.6, 5.6
    conc.quad((gx0, y1, h), (gx1, y1, h), (gx1, y1, h + .2), (gx0, y1, h + .2), RENDER)
    conc.tri((gx0, y1, h + .2), (gx1, y1, h + .2), (0, y1, gz), RENDER)
    for xs in (-1, 1):
        timber.quad((0, y1 + .3, gz + .1), (0, mid, gz + .1), (xs * 3.0, mid, h), (xs * 3.0, y1 + .3, h - .1), ROOF_TILE)
    conc.cyl((0, y1, 4.4), (0, y1 + .08, 4.4), .45, '#f4f1e6', sides=20)            # the clock face, blank
    # the veranda: posts, a lean-to roof and a low rail
    for x in np.arange(x0, x1 + .01, 2.5):
        timber.box((x, VERANDA + .15, 1.45), (.16, .16, 2.9), FRAMING)
    timber.quad((x0 - .4, y1, 3.05), (x1 + .4, y1, 3.05), (x1 + .4, VERANDA - .1, 2.75), (x0 - .4, VERANDA - .1, 2.75), ROOF_TILE)
    timber.quad((x0 - .4, y1, 3.12), (x0 - .4, VERANDA - .1, 2.82), (x1 + .4, VERANDA - .1, 2.82), (x1 + .4, y1, 3.12), ROOF_TILE)
    for xa, xb in ((x0, -1.4), (1.4, x1)):
        timber.box(((xa + xb) / 2, VERANDA + .15, .85), (xb - xa, .08, .08), FRAMING)
    for x in (-6.5, 6.5):
        kit.bench(furn, x, y1 + .5, math.pi / 2, length=2.2)


def picket(timber):
    ring = list(rounded(*FENCE).exterior.coords)
    pts = sk.polyline(LineString(ring), step=2.4)
    gaps = [box(x - w / 2, s * FENCE[1] - 3, x + w / 2, s * FENCE[1] + 3) for x, w, s in GATES]
    gaps.append(box(PAV[0] - .5, -FENCE[1] - 3, PAV[1] + .5, -FENCE[1] + 1))
    blocked = shapely.union_all(gaps)
    run = []
    for a, b in zip(pts, pts[1:]):
        if blocked.intersects(LineString([a, b])):
            seg = LineString([a, b]).difference(blocked)
            for part in getattr(seg, 'geoms', [seg]):
                if not part.is_empty and part.length > .05:
                    c = list(part.coords)
                    if run and math.dist(run[-1], c[0]) < 1e-6:
                        run.append(c[-1])
                    else:
                        if len(run) > 1:
                            sk.picket_fence(timber, run)
                        run = list(c)
            if len(run) > 1:
                sk.picket_fence(timber, run)
            run = []
        else:
            if not run:
                run = [a]
            run.append(b)
    if len(run) > 1:
        sk.picket_fence(timber, run)


def furniture(parts, layout):
    furn, metal, timber, conc = parts['furniture'], parts['metal'], parts['timber'], parts['concrete']
    pitch_markings(furn, timber)
    boundary(furn)
    for e in (-1, 1):
        sight_screen(metal, e * (ROPE[0] + 2.4), math.pi if e > 0 else 0.0)
    pavilion(conc, timber, furn)
    picket(timber)
    sk.scoreboard(furn, 24.0, FENCE[1] - 2.2, 0.0, width=4.0, height=2.0, base=1.0)
    roller(metal, -34.0, FENCE[1] - 2.0)
    for x in (-8.0, -3.0, 3.0, 8.0):
        kit.bench(furn, x, TERRACE + 1.0, math.pi / 2, length=2.0)
    ring = rounded(ROPE[0] + 2.4, ROPE[1] + 2.4, ROPE[2] + 2.0).exterior
    for d in np.arange(20.0, ring.length, 26.0):
        x, y = ring.interpolate(d).coords[0]
        if y > -40 and not (abs(y) < 6 and abs(x) > 40):            # clear of the pavilion side and the sight screens
            kit.bench(furn, x, y, math.atan2(-y, -x))
    for x, y in ((14.0, -58.4), (-3.0, -58.6), (-14.0, -45.6), (14.0, -45.6)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 12.8, -45.8, math.pi / 2)
    kit.bike_rack(metal, 19.8, -57.0, math.pi / 2)
    kit.sign_board(furn, 18.8, -59.2, 0.0, colour='#2f5a3b')


# ---- planting ----------------------------------------------------------------------------------
def planting(inst, layout):
    rng = random.Random(8080)
    site = layout['site']
    keep_off = shapely.union_all([layout['gravel'], layout['paving'], layout['ground'], box(PAV[0] - .5, PAV[2] - .5, PAV[1] + .5, PAV[3])]).buffer(.6)
    radius = {}

    def reach(slug):
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{p}'][1].positions).reshape(-1, 3)
                                  for p in ('wood', 'foliage') if inst.meshes[f'{key}-{p}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        return radius[slug]
    shrubs = ['common-lilac', 'snowberry', 'prickly-wild-rose', 'shrubby-cinquefoil', 'wild-bergamot', 'feather-reed-grass']
    for poly in kit.polygons(layout['beds']):
        for x, y in kit.scatter(poly.buffer(-.4), 1.8, rng, keep_off):
            inst.plant(rng.choice(shrubs), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.25))
    trees = []
    candidates = kit.scatter(layout['outside'], 4.0, rng)
    rng.shuffle(candidates)
    fence = rounded(*FENCE)
    for slug, count, gap in (('bur-oak', 14, 7.0), ('green-ash', 16, 7.0), ('trembling-aspen', 8, 4.5), ('white-spruce', 6, 5.5)):
        placed = 0
        for x, y in candidates:
            if placed >= count:
                break
            scale = rng.uniform(.8, 1.0)
            r = reach(slug) * scale
            p = Point(x, y)
            if not site.buffer(-(r + .3)).contains(p) or keep_off.buffer(1.0).contains(p) or fence.buffer(1.8).contains(p):
                continue
            if any(math.hypot(x - tx, y - ty) < gap * .5 + (r + tr) * .45 for tx, ty, tr in trees):
                continue
            trees.append((x, y, r))
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
            placed += 1
    return trees


def extra_checks(tris, recipe):
    """Cricket-specific: the 22-yard pitch, the boundary and a clear field of play."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    furn = vertices({'furniture'})
    tall = furn[furn[:, 2] > .68]
    stumps = all(bool((np.hypot(tall[:, 0] - e * STUMPS, tall[:, 1]) < .2).any()) for e in (-1, 1))
    rope_line = rounded(*ROPE).exterior
    near = [rope_line.interpolate(d).coords[0] for d in np.linspace(0, rope_line.length, 400, endpoint=False)]
    reach_min = min(math.hypot(x, y) for x, y in near)
    solid = vertices({'metal', 'concrete', 'furniture', 'wood', 'foliage', 'timber'})
    inside = shapely.contains_xy(rounded(*ROPE).buffer(-.3), solid[:, 0], solid[:, 1]) & (solid[:, 2] > .1)
    wickets = (np.abs(np.abs(solid[:, 0]) - STUMPS) < .2) & (np.abs(solid[:, 1]) < .2)
    return [('stumps 20.12 m (22 yards) apart on the pitch line', stumps),
            (f'boundary rope at least {reach_min:.1f} m from the pitch centre', reach_min >= 41.9),
            ('nothing stands inside the boundary but the stumps', not bool((inside & ~wickets).any()))]


def build():
    parts = Parts(8100)
    layout = plan()
    g, p = parts['grass'].body, parts['paving'].body
    sk.stripes(g, layout['field'], math.pi / 2, 6.0, z=0.0, cell=3.0)
    sk.stripes(g, layout['square'].difference(layout['pitch']), math.pi / 2, PITCH_W, surfaces=('square', 'turf_light'), cell=1.5)
    kit.fill(g, 'pitch', layout['pitch'], z=.003, cell=1.0)
    kit.fill(p, 'stone', layout['paving'], z=.02, cell=1.5)
    kit.fill(parts['gravel'].body, 'gravel', layout['gravel'], z=.01, cell=2.0)
    kit.fill(g, 'lawn', layout['lawn'], cell=3.0)
    kit.fill(g, 'bed', layout['beds'], z=.004, cell=2.0)
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'cricket')
    gx = GATES[0][0]
    routes = kit.route_segments(LineString([(gx, -SITE_D / 2), (gx, -FENCE[1] + 2.0)]), 2.0)
    routes += kit.route_segments(LineString([(PAV[0] - 1.0, (VERANDA + TERRACE) / 2), (PAV[1] + 1.0, (VERANDA + TERRACE) / 2)]), 1.6)
    routes += kit.route_segments(layout['loop'], 2.0)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'gravel'], reference=REFERENCE, routes=routes,
        programme='A village cricket ground inside a white picket fence: a striped outfield, a boundary rope 42 to 46 m from the '
                  'pitch centre with markers, a square of prepared strips with the active 22-yard pitch, creases and stumps, white '
                  'wheeled sight screens at both ends, a timber-framed pavilion with a veranda, a blank clock and a terrace of '
                  'benches, a scoreboard, a roller, benches round the boundary, and bur oak, green ash, aspen and spruce outside '
                  'the fence.',
        design_basis='Original concept after the catalogue cricket ground "Village Green" references (variant 0). A club-sized '
                     'ground as teaching values, not a ground or pitch design.',
        limitations=['Prepared level ground only; the square, drainage and outfield construction are not designed.',
                     'Club-sized boundaries (42 to 46 m); senior and international grounds are larger.',
                     'The pavilion is a closed massing with a veranda; its interior, services and access are not designed.',
                     'The scoreboard and clock are blank.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='A village cricket ground with a picket fence, boundary rope, square and pitch, sight screens, a timber pavilion '
                    'and shade trees. Prepared level ground.')
    return meshes, nodes, meta
