"""Community Ball Diamond: an original native park after the catalogue baseball/softball
diamond's "Urban Community Diamond" references
(frontend/public/archetypes/openspaces/baseball-softball-diamond/variant_0*).

A Little League-sized diamond (60 ft bases, 46 ft pitching distance, a 200 ft outfield
fence) laid out from the south-west corner of the site: a grass infield inside a dirt arc,
a warning track, a 6 m chain-link backstop with a hood, dugouts, aluminium bleachers on a
concrete apron, field lights, a blank scoreboard and a path loop round the outfield
through lawn, trees and prairie beds. Dimensions are teaching values, not a field design.
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

PARK_ID = 'student_community_ball_diamond_v1'
ARCHETYPE = 'baseball_softball_diamond'
TITLE = 'Community Ball Diamond'
GENERATOR = 'CityPrompt native park batch builder v1 (baseball)'
REFERENCE = 'frontend/public/archetypes/openspaces/baseball-softball-diamond/variant_0'
KIT_SOURCES = ('sportskit.py',)

SITE_W = SITE_D = 88.0
HX, HY = -25.0, -25.0                    # home plate; the first-base line runs east, the third-base line north
BASE = 18.29                             # 60 ft between bases
PITCH = 14.02                            # 46 ft from home plate to the pitching rubber
FENCE_R = 61.0                           # 200 ft to the outfield fence
FOUL = 7.62                              # 25 ft from the foul lines (and home plate) to the side fences and backstop
ARC_R = 15.24                            # infield arc, 50 ft from the pitching rubber
TRACK = 3.0                              # warning track inside the outfield fence
APRON = 7.0                              # concrete apron outside the side fences, as far as 30 m along each line
PATH_C = 13.0                            # walk centre line: 13 m from home behind the backstop and from both foul lines
ENTRANCE = dict(x=-14.0, y=-44.0, widthM=3.0, arrivalY=-41.0)
PX, PY = HX + PITCH / math.sqrt(2), HY + PITCH / math.sqrt(2)
GATE = (3.6, 4.8)                        # gap in each side fence, metres along the line from home plate
DUGOUT = (4.8, 13.8)
SUNKEN, DEEPEST = None, 0.0
WEST, SOUTH = HX - FOUL, HY - FOUL       # side fence lines
JOIN = math.sqrt(FENCE_R ** 2 - FOUL ** 2)   # where each side fence meets the outfield arc, along its line


def along(x, y):
    return max(x - HX, y - HY)


def enclosure():
    pts = sk.arc(HX, HY, FOUL, math.pi, 1.5 * math.pi, step=2.0)
    pts += [(HX + JOIN, SOUTH)]
    a0, a1 = -math.asin(FOUL / FENCE_R), math.pi / 2 + math.asin(FOUL / FENCE_R)
    pts += sk.arc(HX, HY, FENCE_R, a0, a1, step=3.0)[1:]
    pts += [(WEST, HY)]
    return Polygon(pts)


def loop_line():
    """The walk: round the backstop on the apron, along both lines, and round the outfield."""
    c = PATH_C                                     # walk centre radius behind the backstop, and offset of both lines
    r = FENCE_R + 4.5                              # walk centre radius round the outfield
    a_s = -math.asin(c / r)
    pts = sk.arc(HX, HY, c, math.pi, 1.5 * math.pi, step=1.5)
    pts += [(HX + r * math.cos(a_s), HY - c)]
    pts += sk.arc(HX, HY, r, a_s, math.pi / 2 - a_s, step=2.0)[1:]
    pts += [(HX - c, HY)]
    pts = [p for i, p in enumerate(pts) if i == 0 or math.dist(p, pts[i - 1]) > .05]
    resampled = sk.polyline(LineString(pts + pts[:1]), step=4.0)
    return LineString(kit.chaikin(resampled, 4))


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    field = enclosure()
    near = box(-SITE_W, -SITE_D, HX + 30, HY + 30)
    apron = field.buffer(APRON, quad_segs=24).difference(field).intersection(near).intersection(site)
    loop = loop_line()
    entry = box(ENTRANCE['x'] - 1.5, -SITE_D / 2, ENTRANCE['x'] + 1.5, SOUTH - APRON + .3)
    path = loop.buffer(1.2, quad_segs=8).union(entry).difference(apron).difference(field).intersection(site)
    home_disc = Point(HX, HY).buffer(3.4, quad_segs=24)
    behind = Point(HX, HY).buffer(FOUL, quad_segs=32).intersection(box(HX - 200, HY - 200, HX + .9, HY + .9))   # home to backstop
    mound = Point(PX, PY).buffer(1.6, quad_segs=24)
    infield_grass = box(HX + .9, HY + .9, HX + BASE - .9, HY + BASE - .9).difference(home_disc).difference(mound.buffer(.01))
    arc_dirt = Point(PX, PY).buffer(ARC_R, quad_segs=48).intersection(box(HX - 1.0, HY - 1.0, HX + 200, HY + 200))
    warning = field.difference(Point(HX, HY).buffer(FENCE_R - TRACK, quad_segs=96))
    dugouts = [box(WEST, HY + DUGOUT[0], WEST + 2.1, HY + DUGOUT[1]), box(HX + DUGOUT[0], SOUTH, HX + DUGOUT[1], SOUTH + 2.1)]
    dirt = shapely.union_all([arc_dirt, home_disc, behind]).difference(infield_grass).difference(mound).intersection(field)
    dirt = dirt.difference(shapely.union_all(dugouts))
    grass = field.difference(dirt).difference(warning).difference(mound).difference(shapely.union_all(dugouts))
    outside = site.difference(field).difference(apron).difference(path)
    inner_lawn = outside.intersection(Point(HX, HY).buffer(FENCE_R + 3.2, quad_segs=96))
    outer = outside.difference(inner_lawn)
    beds = shapely.union_all([
        kit.smooth(kit.ellipse(30.0, 30.0, 11.0, 7.0, math.radians(-45)), 2.0),
        kit.smooth(kit.ellipse(39.0, 8.0, 3.0, 10.0, 0.0), 1.5),
        kit.smooth(kit.ellipse(8.0, 39.0, 10.0, 3.0, 0.0), 1.5),
        Polygon([(-44, -44), (-44, -39.6 + .01), (-41.0, -39.6), (-39.6, -41.0), (-39.6 + .01, -44)]).buffer(0),
        box(-44, -30, -41.2, 8), box(-30, -44, -16.4, -41.2), box(-11.6, -44, 8, -41.2),
    ]).intersection(outer.buffer(-.4)).difference(path.buffer(.8))
    lawn = outer.difference(beds)
    return dict(site=site, field=field, apron=apron, path=path, loop=loop, entry=entry, dirt=dirt, mound=mound, grass=grass,
                warning=warning, dugouts=dugouts, inner_lawn=inner_lawn, lawn=lawn, beds=beds)


# ---- markings ----------------------------------------------------------------------------------
def frame(u, v):
    """Field frame: u from home plate toward centre field, v toward first base's side."""
    c = math.sqrt(.5)
    return (HX + (u + v) * c, HY + (u - v) * c)


def markings(furn, metal):
    lines = [sk.line_band((HX, HY), (HX + FENCE_R - .1, HY), .08), sk.line_band((HX, HY), (HX, HY + FENCE_R - .1), .08)]
    for side in (-1, 1):                                          # batter's boxes, 3 by 6 ft, 6 in from the plate
        v0 = side * (.215 + .152)
        v1 = side * (.215 + .152 + .914)
        corners = [frame(u, v) for u, v in ((-.6, v0), (1.23, v0), (1.23, v1), (-.6, v1))]
        lines.append(Polygon(corners).exterior.buffer(.035))
    for x, y in ((HX - 4.2, HY + 3.0), (HX + 3.0, HY - 4.2)):      # on-deck circles
        lines.append(Point(x, y).buffer(.8).difference(Point(x, y).buffer(.72)))
    sk.chalk(furn, shapely.union_all(lines).difference(Point(HX, HY).buffer(.35)))
    plate = Polygon([frame(u, v) for u, v in ((0, 0), (-.215, .215), (-.43, .215), (-.43, -.215), (-.215, -.215))])
    kit.extrude(furn, sk.WHITE, Polygon([(HX + p[0] - frame(0, 0)[0], HY + p[1] - frame(0, 0)[1]) for p in plate.exterior.coords]),
                0, .025)
    s = .38
    for (x, y) in ((HX + BASE - s / 2, HY + s / 2), (HX + BASE, HY + BASE), (HX + s / 2, HY + BASE - s / 2)):
        furn.box((x, y, .04), (s, s, .07), sk.WHITE)
    rubber = Polygon([frame(u, v) for u, v in ((PITCH, -.305), (PITCH + .152, -.305), (PITCH + .152, .305), (PITCH, .305))])
    kit.extrude(furn, sk.WHITE, rubber, .14, .17)


# ---- fences and buildings ----------------------------------------------------------------------
def fences(metal, conc):
    six, side, low = 6.0, 2.4, 1.5
    back = [(WEST, HY + GATE[0]), (WEST, HY)] + sk.arc(HX, HY, FOUL, math.pi, 1.5 * math.pi, step=2.0)[1:-1] + \
           [(HX, SOUTH), (HX + GATE[0], SOUTH)]
    sk.chain_link(metal, back, [six] * len(back), post_spacing=2.0)
    arc_pts = sk.arc(HX, HY, FOUL, math.pi, 1.5 * math.pi, step=2.0)          # the hood leans toward home plate
    for (ax, ay), (bx, by) in zip(arc_pts, arc_pts[1:]):
        ia = ((HX - ax) / FOUL * 1.4, (HY - ay) / FOUL * 1.4)
        ib = ((HX - bx) / FOUL * 1.4, (HY - by) / FOUL * 1.4)
        metal.diamond_mesh((ax, ay, six), (bx - ax, by - ay, 0.0), ((ia[0] + ib[0]) / 2, (ia[1] + ib[1]) / 2, .5), .16, .016, sk.GALV)
        metal.cyl((ax + ia[0], ay + ia[1], six + .5), (bx + ib[0], by + ib[1], six + .5), .021, sk.POST, sides=6)
        metal.cyl((ax, ay, six), (ax + ia[0], ay + ia[1], six + .5), .025, sk.POST, sides=6)
    for line in (lambda d: (WEST, HY + d), lambda d: (HX + d, SOUTH)):
        sk.chain_link(metal, [line(DUGOUT[1]), line(30.0)], [side, side])
        sk.chain_link(metal, [line(30.0), line(JOIN)], [low, low], cap=sk.YELLOW)
        sk.chain_link(metal, [line(GATE[1]), line(DUGOUT[0])], [side, side], post_spacing=2.0)
    a0, a1 = -math.asin(FOUL / FENCE_R), math.pi / 2 + math.asin(FOUL / FENCE_R)
    outfield = sk.arc(HX, HY, FENCE_R, a0, a1, step=3.0)
    sk.chain_link(metal, outfield, [low] * len(outfield), cap=sk.YELLOW)
    sk.dugout(conc, metal, WEST + 1.05, HY + sum(DUGOUT) / 2, 0.0, length=DUGOUT[1] - DUGOUT[0])
    sk.dugout(conc, metal, HX + sum(DUGOUT) / 2, SOUTH + 1.05, math.pi / 2, length=DUGOUT[1] - DUGOUT[0])
    sk.foul_pole(metal, HX + FENCE_R, HY)
    sk.foul_pole(metal, HX, HY + FENCE_R)


def stands(furn, metal):
    for d in (17.8, 24.6):
        sk.bleacher(metal, WEST - .8 - 1.5, HY + d, 0.0)
        sk.bleacher(metal, HX + d, SOUTH - .8 - 1.5, math.pi / 2)
    for ang in (math.radians(200), math.radians(250)):
        x, y = HX + 10.2 * math.cos(ang), HY + 10.2 * math.sin(ang)
        kit.bench(furn, x, y, math.atan2(HY - y, HX - x))
    for ang in (15, 33, 57, 75):
        a = math.radians(ang)
        r = FENCE_R + 4.5 + 2.1
        x, y = HX + r * math.cos(a), HY + r * math.sin(a)
        kit.bench(furn, x, y, math.atan2(HY - y, HX - x))
    for x, y in ((-36.4, -36.4), (6.6, -40.0), (-40.0, 6.6), (HX + (FENCE_R + 6.6) * math.cos(.79), HY + (FENCE_R + 6.6) * math.sin(.79) + 3.0)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, -38.6, -32.0, 0.0)
    kit.bike_rack(metal, -9.6, -40.6, 0.0)
    kit.sign_board(furn, -16.6, -43.0, 0.0, colour='#2f5a3b')
    sk.scoreboard(furn, HX + 63.0 * math.cos(math.pi / 4), HY + 63.0 * math.sin(math.pi / 4), -math.pi / 4)
    aim = (HX + 24.0, HY + 24.0)
    for x, y in ((-41.4, 1.0), (1.0, -41.4), (HX + 63.2 * math.cos(math.radians(22)), HY + 63.2 * math.sin(math.radians(22))),
                 (HX + 63.2 * math.cos(math.radians(68)), HY + 63.2 * math.sin(math.radians(68)))):
        sk.sports_light(metal, x, y, math.atan2(aim[1] - y, aim[0] - x))


# ---- planting ----------------------------------------------------------------------------------
def planting(inst, layout):
    rng = random.Random(6060)
    keep_off = shapely.union_all([layout['path'], layout['apron'], layout['field']]).buffer(.6)
    site = layout['site']
    shrubs = ['snowberry', 'shrubby-cinquefoil', 'diabolo-ninebark', 'wolf-willow', 'saskatoon', 'feather-reed-grass']
    meadow = ['rough-fescue-drift', 'feather-reed-grass', 'blanketflower', 'wild-bergamot', 'goldenrod', 'wild-blue-flax',
              'june-grass', 'prairie-smoke']
    for poly in kit.polygons(layout['beds']):
        mix = meadow if poly.area > 60 else shrubs
        for x, y in kit.scatter(poly.buffer(-.3), 1.6 if mix is meadow else 1.5, rng, keep_off):
            inst.plant(rng.choice(mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    radius = {}

    def reach(slug):
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{p}'][1].positions).reshape(-1, 3)
                                  for p in ('wood', 'foliage') if inst.meshes[f'{key}-{p}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        return radius[slug]
    trees = []
    groves = [('trembling-aspen', 12, 5.0), ('green-ash', 12, 8.0), ('bur-oak', 7, 10.0), ('white-spruce', 8, 7.0)]
    candidates = kit.scatter(layout['lawn'].union(layout['beds']), 4.5, rng)
    rng.shuffle(candidates)
    for slug, count, gap in groves:
        placed = 0
        for x, y in candidates:
            if placed >= count:
                break
            scale = rng.uniform(.75, 1.0)
            r = reach(slug) * scale
            p = Point(x, y)
            if not site.buffer(-(r + .3)).contains(p) or keep_off.buffer(1.4).contains(p):
                continue
            d = Point(HX, HY).distance(p)
            if d < FENCE_R + 4.5 + 1.2 + 1.8 or d - r < FENCE_R + .8:  # trunks clear of the walk; canopies outside the fence
                continue
            if any(math.hypot(x - tx, y - ty) < gap * .5 + (r + tr) * .45 for tx, ty, tr in trees):
                continue
            trees.append((x, y, r))
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
            placed += 1
    corner = (-38.6, -38.6)                                     # one shade tree in the corner beyond the backstop
    trees.append((*corner, reach('green-ash') * .7))
    inst.plant('green-ash', *corner, yaw=1.1, scale=.7)
    # small flowering trees in the strips behind the aprons, between the walk and the site edge
    small = ['amur-cherry', 'schubert-chokecherry']           # two species keep the GLB small
    for k, d in enumerate(np.arange(-12.0, 38.0, 6.5)):
        for x, y in ((-41.9, HY + d), (HX + d, -41.9)):
            slug = small[(k + (x > -41)) % len(small)]
            scale = min(1.0, 1.85 / reach(slug))
            p = Point(x, y)
            if site.buffer(-(reach(slug) * scale + .2)).contains(p) and not keep_off.buffer(.2).contains(p) and \
                    Point(-14.0, -44.0).distance(p) > 4.0:
                inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
    return trees


def extra_checks(tris, recipe):
    """Diamond-specific: fence, base and backstop geometry, and a clear field of play."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    metal = vertices({'metal'})
    furn = vertices({'furniture'})
    d = np.hypot(metal[:, 0] - HX, metal[:, 1] - HY)

    def fence_at(angle):
        x, y = HX + FENCE_R * math.cos(angle), HY + FENCE_R * math.sin(angle)
        near = np.hypot(metal[:, 0] - x, metal[:, 1] - y) < .4
        return bool((near & (metal[:, 2] > .5) & (metal[:, 2] < 1.6)).any())
    bases = [(HX + BASE - .19, HY + .19), (HX + BASE, HY + BASE), (HX + .19, HY + BASE - .19)]
    base_ok = all(bool(((np.hypot(furn[:, 0] - x, furn[:, 1] - y) < .3) & (np.abs(furn[:, 2] - .075) < .01)).any()) for x, y in bases)
    rubber = ((np.hypot(furn[:, 0] - PX, furn[:, 1] - PY) < .4) & (np.abs(furn[:, 2] - .17) < .005)).any()
    behind = (metal[:, 0] < HX) & (metal[:, 1] < HY) & (np.abs(d - FOUL) < .3)
    solid = vertices({'metal', 'concrete', 'furniture', 'wood', 'foliage', 'timber'})
    ang = np.arctan2(solid[:, 1] - HY, solid[:, 0] - HX)
    ds = np.hypot(solid[:, 0] - HX, solid[:, 1] - HY)
    fair = (ang > .02) & (ang < math.pi / 2 - .02) & (ds < FENCE_R - .3) & (solid[:, 2] > .1)
    fair &= np.hypot(solid[:, 0] - PX, solid[:, 1] - PY) > .5
    fair &= np.hypot(solid[:, 0] - HX - BASE, solid[:, 1] - HY - BASE) > .4
    return [('outfield fence 61 m (200 ft) from home plate on both foul lines and in centre field',
             fence_at(0.0) and fence_at(math.pi / 2) and fence_at(math.pi / 4)),
            ('bases 18.29 m (60 ft) apart and the pitching rubber 14.02 m (46 ft) from home plate', base_ok and bool(rubber)),
            ('6 m backstop behind home plate', bool((behind & (metal[:, 2] > 5.9)).any())),
            ('nothing stands in fair territory but the bases and the pitching rubber', not bool(fair.any()))]


def build():
    parts = Parts(6100)
    layout = plan()
    g, p, gr = parts['grass'].body, parts['paving'].body, parts['gravel'].body
    sk.stripes(g, layout['grass'], math.radians(135), 4.0)
    kit.fill(gr, 'infield', layout['dirt'], cell=1.5)
    kit.fill(gr, 'track_dirt', layout['warning'], cell=2.0)
    kit.heightfield(gr, 'infield', layout['mound'], kit.mound((PX, PY), 1.6, .15), spacing=.3, rings=(.3, .8), ring_step=.3)
    for d in layout['dugouts']:
        kit.fill(p, 'concrete', d, z=.02, cell=1.5)
    kit.fill(p, 'concrete', layout['apron'], z=.01, cell=2.0)
    kit.fill(p, 'asphalt', layout['path'], z=.01, cell=2.0)
    kit.fill(g, 'lawn', layout['inner_lawn'], cell=2.5)
    kit.fill(g, 'lawn', layout['lawn'], cell=2.5)
    kit.fill(g, 'bed', layout['beds'], z=.004, cell=2.0)
    markings(parts['furniture'], parts['metal'])
    fences(parts['metal'], parts['concrete'])
    stands(parts['furniture'], parts['metal'])
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'diamond')
    entry_line = LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], SOUTH - APRON / 2 - 1.6)])
    walk = layout['loop']
    routes = kit.route_segments(entry_line, 2.4) + kit.route_segments(walk, 2.2)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'gravel'], reference=REFERENCE, routes=routes,
        programme='A Little League-sized ball diamond: 60 ft bases, a 46 ft pitching distance and a 200 ft outfield fence with a '
                  'yellow cap and foul poles; a grass infield inside a dirt arc, a raised mound, a warning track and chalked lines; '
                  'a 6 m chain-link backstop with a hood, side fences and two block dugouts; aluminium bleachers and benches on a '
                  'concrete apron; four field lights and a blank scoreboard; a path loop round the outfield with benches, through '
                  'lawn, prairie beds, flowering cherries and groves of aspen, green ash, bur oak and white spruce.',
        design_basis='Original concept after the catalogue baseball/softball diamond "Urban Community Diamond" references '
                     '(variant 0). Little League dimensions as teaching values, not a sports field design.',
        limitations=['Prepared level ground only; field drainage, irrigation and the infield mix are not designed.',
                     'Dimensions follow Little League baseball (60 ft bases, 46 ft pitching distance, 200 ft fences); fastpitch '
                     'softball uses 43 ft, and older age groups need larger fields.',
                     'Fences, backstop, lights and bleachers are indicative; real installations follow the governing body, the '
                     'manufacturer and the applicable building and lighting rules.',
                     'The scoreboard is blank.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='A Little League ball diamond with a dirt infield, backstop, dugouts, bleachers, field lights and a scoreboard, '
                    'ringed by a path loop and trees. Prepared level ground.')
    return meshes, nodes, meta
