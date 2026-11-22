"""Prairie Sports Complex: an original native park after the catalogue sports field complex's
"Multi-Field Complex" references (frontend/public/archetypes/openspaces/sports-field-complex/variant_0*).

Two 90 x 60 m soccer pitches with goals, bleachers and lights to the south, and two Little
League diamonds (60 ft bases, 200 ft fences) to the north with their home plates turned toward
a central plaza and fieldhouse. An east-west promenade runs between the fields, an entrance
spine runs up from the south, and trees and prairie beds fill the margins. Dimensions are
teaching values, not a sports facility design.
"""
from __future__ import annotations

import math
import random

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box

import parkkit as kit
import playkit as pk
import sportskit as sk
from parkkit import Instances, Parts

PARK_ID = 'student_prairie_sports_complex_v1'
ARCHETYPE = 'sports_field_complex'
TITLE = 'Prairie Sports Complex'
GENERATOR = 'CityPrompt native park batch builder v1 (complex)'
REFERENCE = 'frontend/public/archetypes/openspaces/sports-field-complex/variant_0'
KIT_SOURCES = ('sportskit.py', 'playkit.py')

SITE_W, SITE_D = 216.0, 168.0
PITCH = (90.0, 60.0)
RUNOFF = 4.0
PITCHES = ((-55.0, -46.0), (55.0, -46.0))
BASE, PITCH_D, FENCE_R, FOUL, ARC_R, TRACK = 18.29, 14.02, 61.0, 7.62, 15.24, 3.0
JOIN = math.sqrt(FENCE_R ** 2 - FOUL ** 2)
DIAMONDS = (((18.0, 10.0), 0.0), ((-18.0, 10.0), 90.0))     # home plate and rotation: first-base line east, or north
GATE, DUGOUT = (3.6, 4.8), (4.8, 13.8)
PROMENADE = (-12.0, 2.38)                                    # y extent between the pitches and the diamond fences
FIELDHOUSE = (-6.0, 42.0, 6.0, 56.0)
ENTRANCE = dict(x=0.0, y=-84.0, widthM=4.0, arrivalY=-81.0)
SUNKEN, DEEPEST = None, 0.0


# ---- the local diamond frame: home plate at the origin, first-base line +x, third-base line +y ----------
def to_world(home, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def point(x, y):
        return (home[0] + x * c - y * s, home[1] + x * s + y * c)

    def geom(g):
        return affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), home[0], home[1])
    return point, geom


def enclosure_local():
    pts = sk.arc(0, 0, FOUL, math.pi, 1.5 * math.pi, step=2.0) + [(JOIN, -FOUL)]
    a0, a1 = -math.asin(FOUL / FENCE_R), math.pi / 2 + math.asin(FOUL / FENCE_R)
    pts += sk.arc(0, 0, FENCE_R, a0, a1, step=3.0)[1:] + [(-FOUL, 0.0)]
    return Polygon(pts)


def diamond_surfaces_local():
    p = (PITCH_D / math.sqrt(2), PITCH_D / math.sqrt(2))
    field = enclosure_local()
    home = Point(0, 0).buffer(3.4, quad_segs=24)
    behind = Point(0, 0).buffer(FOUL, quad_segs=32).intersection(box(-200, -200, .9, .9))
    mound = Point(*p).buffer(1.6, quad_segs=24)
    grass_in = box(.9, .9, BASE - .9, BASE - .9).difference(home).difference(mound.buffer(.01))
    arc = Point(*p).buffer(ARC_R, quad_segs=48).intersection(box(-1.0, -1.0, 200, 200))
    warning = field.difference(Point(0, 0).buffer(FENCE_R - TRACK, quad_segs=96))
    dugouts = shapely.union_all([box(-FOUL, DUGOUT[0], -FOUL + 2.1, DUGOUT[1]), box(DUGOUT[0], -FOUL, DUGOUT[1], -FOUL + 2.1)])
    dirt = shapely.union_all([arc, home, behind]).difference(grass_in).difference(mound).intersection(field).difference(dugouts)
    grass = field.difference(dirt).difference(warning).difference(mound).difference(dugouts)
    return dict(field=field, dirt=dirt, grass=grass, warning=warning, mound=mound, dugouts=dugouts, rubber=p)


def build_diamond(parts, home, rot):
    point, geom = to_world(home, rot)
    s = {k: (geom(v) if hasattr(v, 'geom_type') else point(*v)) for k, v in diamond_surfaces_local().items()}
    g, gr, pv = parts['grass'].body, parts['gravel'].body, parts['paving'].body
    sk.stripes(g, s['grass'], math.radians(rot + 135), 4.0, cell=3.0)
    kit.fill(gr, 'infield', s['dirt'], cell=1.5)
    kit.fill(gr, 'track_dirt', s['warning'], cell=2.5)
    px, py = s['rubber']
    kit.heightfield(gr, 'infield', s['mound'], kit.mound((px, py), 1.6, .15), spacing=.3, rings=(.3, .8), ring_step=.3)
    kit.fill(pv, 'concrete', s['dugouts'], z=.02, cell=1.5)
    furn, metal, conc = parts['furniture'], parts['metal'], parts['concrete']
    c = math.sqrt(.5)

    def frame(u, v):
        return point((u + v) * c, (u - v) * c)
    lines = [sk.line_band(point(0, 0), point(FENCE_R - .1, 0), .08), sk.line_band(point(0, 0), point(0, FENCE_R - .1), .08)]
    for side in (-1, 1):
        v0, v1 = side * .367, side * 1.281
        lines.append(Polygon([frame(u, v) for u, v in ((-.6, v0), (1.23, v0), (1.23, v1), (-.6, v1))]).exterior.buffer(.035))
    sk.chalk(furn, shapely.union_all(lines).difference(Point(*point(0, 0)).buffer(.35)))
    kit.extrude(furn, sk.WHITE, Polygon([frame(u, v) for u, v in ((0, 0), (-.215, .215), (-.43, .215), (-.43, -.215), (-.215, -.215))]), 0, .025)
    for bx, by in ((BASE - .19, .19), (BASE, BASE), (.19, BASE - .19)):
        x, y = point(bx, by)
        furn.box((x, y, .04), (.38, .38, .07), sk.WHITE, yaw=math.radians(rot))
    kit.extrude(furn, sk.WHITE, Polygon([frame(u, v) for u, v in ((PITCH_D, -.305), (PITCH_D + .152, -.305), (PITCH_D + .152, .305), (PITCH_D, .305))]), .14, .17)
    # fences: a 6 m backstop with a hood, 2.4 m side fences past the dugouts, then 1.5 m to the capped outfield fence
    back = [(-FOUL, GATE[0]), (-FOUL, 0.0)] + sk.arc(0, 0, FOUL, math.pi, 1.5 * math.pi, step=2.0)[1:-1] + [(0.0, -FOUL), (GATE[0], -FOUL)]
    sk.chain_link(metal, [point(*q) for q in back], [6.0] * len(back), post_spacing=2.0)
    arc = sk.arc(0, 0, FOUL, math.pi, 1.5 * math.pi, step=2.0)
    for (ax, ay), (bx, by) in zip(arc, arc[1:]):
        ia, ib = (-ax / FOUL * 1.4, -ay / FOUL * 1.4), (-bx / FOUL * 1.4, -by / FOUL * 1.4)
        wa, wb = point(ax, ay), point(bx, by)
        wia, wib = point(ax + ia[0], ay + ia[1]), point(bx + ib[0], by + ib[1])
        metal.diamond_mesh((wa[0], wa[1], 6.0), (wb[0] - wa[0], wb[1] - wa[1], 0.0),
                           (((wia[0] - wa[0]) + (wib[0] - wb[0])) / 2, ((wia[1] - wa[1]) + (wib[1] - wb[1])) / 2, .5), .16, .016, sk.GALV)
        metal.cyl((wia[0], wia[1], 6.5), (wib[0], wib[1], 6.5), .021, sk.POST, sides=6)
        metal.cyl((wa[0], wa[1], 6.0), (wia[0], wia[1], 6.5), .025, sk.POST, sides=6)
    for line in (lambda d: point(-FOUL, d), lambda d: point(d, -FOUL)):
        sk.chain_link(metal, [line(DUGOUT[1]), line(30.0)], [2.4, 2.4])
        sk.chain_link(metal, [line(30.0), line(JOIN)], [1.5, 1.5], cap=sk.YELLOW)
    a0, a1 = -math.asin(FOUL / FENCE_R), math.pi / 2 + math.asin(FOUL / FENCE_R)
    outfield = [point(*q) for q in sk.arc(0, 0, FENCE_R, a0, a1, step=3.0)]
    sk.chain_link(metal, outfield, [1.5] * len(outfield), cap=sk.YELLOW)
    mid = sum(DUGOUT) / 2
    x, y = point(-FOUL + 1.05, mid)
    sk.dugout(conc, metal, x, y, math.radians(rot), length=DUGOUT[1] - DUGOUT[0])
    x, y = point(mid, -FOUL + 1.05)
    sk.dugout(conc, metal, x, y, math.radians(rot) + math.pi / 2, length=DUGOUT[1] - DUGOUT[0])
    for q in ((FENCE_R, 0.0), (0.0, FENCE_R)):
        sk.foul_pole(metal, *point(*q))
    for d in (17.8, 24.6):
        x, y = point(-FOUL - .8 - 1.5, d)
        sk.bleacher(metal, x, y, math.radians(rot))
        x, y = point(d, -FOUL - .8 - 1.5)
        sk.bleacher(metal, x, y, math.radians(rot) + math.pi / 2)
    aim = point(24.0, 24.0)
    for ang in (8.0, 35.0, 55.0, 82.0):
        a = math.radians(ang)
        x, y = point(64.5 * math.cos(a), 64.5 * math.sin(a))
        sk.sports_light(metal, x, y, math.atan2(aim[1] - y, aim[0] - x))
    sk.scoreboard(furn, *point(63.0 * math.cos(math.pi / 4), 63.0 * math.sin(math.pi / 4)), math.radians(rot) - math.pi / 4,
                  width=4.0, height=2.0, base=2.2)
    return s['field']


# ---- soccer pitches ----------------------------------------------------------------------------
def pitch_lines(cx, cy):
    w, d = PITCH
    out = [box(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2).exterior.buffer(.06), box(cx - .06, cy - d / 2, cx + .06, cy + d / 2),
           Point(cx, cy).buffer(9.15, quad_segs=32).exterior.buffer(.06), Point(cx, cy).buffer(.2)]
    for s in (-1, 1):
        x0 = cx + s * w / 2
        out += [Polygon([(x0, cy - 20.16), (x0 - s * 16.5, cy - 20.16), (x0 - s * 16.5, cy + 20.16), (x0, cy + 20.16)]).exterior.buffer(.06),
                Polygon([(x0, cy - 9.16), (x0 - s * 5.5, cy - 9.16), (x0 - s * 5.5, cy + 9.16), (x0, cy + 9.16)]).exterior.buffer(.06),
                Point(x0 - s * 11, cy).buffer(.2),
                Point(x0 - s * 11, cy).buffer(9.15, quad_segs=32).exterior.buffer(.06).difference(
                    box(min(x0, x0 - s * 16.5), cy - 30, max(x0, x0 - s * 16.5), cy + 30))]
        for t in (-1, 1):
            out.append(Point(x0, cy + t * d / 2).buffer(1.0, quad_segs=8).exterior.buffer(.05).intersection(
                box(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2)))
    return shapely.union_all(out)


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    pitches = [box(cx - PITCH[0] / 2 - RUNOFF, cy - PITCH[1] / 2 - RUNOFF, cx + PITCH[0] / 2 + RUNOFF, cy + PITCH[1] / 2 + RUNOFF) for cx, cy in PITCHES]
    fields = [to_world(h, r)[1](enclosure_local()) for h, r in DIAMONDS]
    promenade = box(-SITE_W / 2 + 4.0, PROMENADE[0], SITE_W / 2 - 4.0, PROMENADE[1] - .01).difference(shapely.union_all(fields))
    spine_s = box(-2.5, -SITE_D / 2, 2.5, PROMENADE[0] + .01)
    plaza = box(-9.8, PROMENADE[1] - .02, 9.8, 62.0).difference(shapely.union_all(fields).buffer(.4))
    paving = shapely.union_all([promenade, spine_s, plaza]).intersection(site)
    house = box(*FIELDHOUSE)
    occupied = shapely.union_all(pitches + fields + [paving])
    grass = site.difference(occupied)
    beds = shapely.union_all([kit.smooth(kit.ellipse(-86.0, 64.0, 11.0, 6.0, math.radians(-20)), 2.0),
                              kit.smooth(kit.ellipse(86.0, 64.0, 11.0, 6.0, math.radians(20)), 2.0),
                              kit.smooth(kit.ellipse(0.0, 72.0, 8.0, 4.0, 0.0), 1.5)])
    beds = beds.intersection(grass.buffer(-1.0))
    return dict(site=site, pitches=pitches, fields=fields, promenade=promenade, paving=paving.difference(house), house=house,
                grass=grass.difference(beds), beds=beds)


def furniture(parts, layout):
    furn, metal, timber, conc = parts['furniture'], parts['metal'], parts['timber'], parts['concrete']
    for cx, cy in PITCHES:
        sk.chalk(furn, pitch_lines(cx, cy))
        for s in (-1, 1):
            sk.goal(metal, cx + s * PITCH[0] / 2, cy, math.pi if s > 0 else 0.0)
        for dx in (-8.0, 8.0):
            sk.bleacher(metal, cx + dx, PROMENADE[0] + 1.75, -math.pi / 2, length=6.8)
        for sx in (-1, 1):
            for y, face_y in ((PROMENADE[0] + 2.6, cy), (-SITE_D / 2 + 1.4, cy)):
                x = cx + sx * 30.0
                sk.sports_light(metal, x, y, math.atan2(face_y - y, cx - x))
    pk.fieldhouse(conc, timber, metal, *FIELDHOUSE, front='y0')
    for x in (-4.0, 4.0):
        kit.bench(furn, x, 38.0, -math.pi / 2)
    for x, y in ((-3.6, -80.0), (3.6, -80.0), (-12.0, -10.4), (12.0, -10.4), (-8.6, 40.0), (8.6, 40.0)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 3.8, 6.0, math.pi)
    kit.bike_rack(metal, -5.0, -78.0, math.pi / 2, loops=5)
    kit.bike_rack(metal, 5.0, -78.0, math.pi / 2, loops=5)
    kit.sign_board(furn, -4.0, -83.0, 0.0, colour='#2f5a3b')
    for x, y in ((0.0, -40.0), (0.0, -60.0), (-40.0, -5.0), (40.0, -5.0), (-80.0, -5.0), (80.0, -5.0)):
        kit.light_pole(furn, x + (3.6 if x == 0 else 0), y + (0 if x == 0 else 2.0), height=5.0)


def planting(inst, layout):
    rng = random.Random(11011)
    site = layout['site']
    keep_off = shapely.union_all(layout['pitches'] + layout['fields'] + [layout['paving'], layout['house']]).buffer(.6)
    meadow = ['rough-fescue-drift', 'feather-reed-grass', 'blanketflower', 'wild-bergamot', 'rough-fescue-drift', 'blue-grama']
    for x, y in kit.scatter(layout['beds'].buffer(-.4), 2.0, rng, keep_off):
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
    candidates = kit.scatter(layout['grass'].union(layout['beds']), 6.0, rng)
    rng.shuffle(candidates)
    play = shapely.union_all(layout['pitches'] + layout['fields'])
    for slug, count, gap in (('green-ash', 12, 9.0), ('bur-oak', 6, 10.0), ('white-spruce', 8, 7.0), ('trembling-aspen', 10, 5.0)):
        placed = 0
        for x, y in candidates:
            if placed >= count:
                break
            scale = rng.uniform(.8, 1.0)
            r = reach(slug) * scale
            p = Point(x, y)
            if not site.buffer(-(r + .3)).contains(p) or keep_off.buffer(1.2).contains(p) or play.buffer(r + 1.0).contains(p):
                continue
            if any(math.hypot(x - tx, y - ty) < gap * .5 + (r + tr) * .45 for tx, ty, tr in trees):
                continue
            trees.append((x, y, r))
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
            placed += 1
    return trees


def extra_checks(tris, recipe):
    """Complex-specific: diamond fences and bases where they belong, pitch lines at size, clear fields of play."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    metal, furn = vertices({'metal'}), vertices({'furniture'})
    checks = []
    for home, rot in DIAMONDS:
        point, _ = to_world(home, rot)
        ok = True
        for ang in (0.0, math.pi / 4, math.pi / 2):
            x, y = point(FENCE_R * math.cos(ang), FENCE_R * math.sin(ang))
            ok &= bool(((np.hypot(metal[:, 0] - x, metal[:, 1] - y) < .4) & (metal[:, 2] > .5) & (metal[:, 2] < 1.6)).any())
        x, y = point(BASE, BASE)
        ok &= bool(((np.hypot(furn[:, 0] - x, furn[:, 1] - y) < .3) & (np.abs(furn[:, 2] - .075) < .01)).any())
        checks.append(ok)
    lines_ok = True
    for cx, cy in PITCHES:
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = cx + sx * PITCH[0] / 2, cy + sy * PITCH[1] / 2
                lines_ok &= bool(((np.abs(furn[:, 0] - x) < .1) & (np.abs(furn[:, 1] - y) < .1) & (np.abs(furn[:, 2] - .012) < .002)).any())
    solid = vertices({'metal', 'concrete', 'furniture', 'wood', 'foliage', 'timber'})
    tall = solid[solid[:, 2] > .2]
    on_pitch = np.zeros(len(tall), dtype=bool)
    for cx, cy in PITCHES:
        inside = (np.abs(tall[:, 0] - cx) < PITCH[0] / 2 - .3) & (np.abs(tall[:, 1] - cy) < PITCH[1] / 2 - .3)
        goals = (np.abs(np.abs(tall[:, 0] - cx) - PITCH[0] / 2) < 2.3) & (np.abs(tall[:, 1] - cy) < 4.0)
        on_pitch |= inside & ~goals
    return [('both diamonds: outfield fences at 61 m on the foul lines and in centre field, second base at 60 ft', all(checks)),
            ('both pitches marked at 90 x 60 m', lines_ok),
            ('nothing stands on either pitch but its goals', not bool(on_pitch.any()))]


def build():
    parts = Parts(11100)
    layout = plan()
    g, p = parts['grass'].body, parts['paving'].body
    for (cx, cy), field in zip(PITCHES, layout['pitches']):
        sk.stripes(g, field, 0.0, 6.0, cell=3.0)
    for home, rot in DIAMONDS:
        build_diamond(parts, home, rot)
    kit.fill(p, 'concrete', layout['paving'], z=.01, cell=3.0)
    kit.fill(g, 'meadow', layout['grass'], cell=3.0)
    kit.fill(g, 'bed', layout['beds'], z=.004, cell=2.5)
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'complex')
    mid = (PROMENADE[0] + PROMENADE[1]) / 2 - 2.2
    routes = kit.route_segments(LineString([(0, -SITE_D / 2), (0, mid)]), 3.0)
    routes += kit.route_segments(LineString([(-SITE_W / 2 + 6.0, mid), (SITE_W / 2 - 6.0, mid)]), 3.0)
    routes += kit.route_segments(LineString([(0, mid), (0, FIELDHOUSE[1] - 1.0)]), 3.0)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'gravel'], reference=REFERENCE, routes=routes,
        programme='Two 90 x 60 m soccer pitches with full markings, goals, bleachers and field lights; two Little League '
                  'diamonds with backstops, dugouts, bleachers, lights and scoreboards, their home plates turned toward a '
                  'central plaza and fieldhouse with a concession window and washrooms; an east-west promenade between the '
                  'fields; an entrance spine with bike racks; prairie beds and groves of green ash, bur oak, spruce and aspen.',
        design_basis='Original concept after the catalogue sports field complex "Multi-Field Complex" references (variant 0). '
                     'Pitch and diamond sizes are teaching values, not a sports facility design.',
        limitations=['Prepared level ground only; field drainage, irrigation and turf construction are not designed.',
                     'Pitches are 90 x 60 m, the smallest adult size; diamonds use Little League dimensions.',
                     'The fieldhouse is a closed massing; its interior, services and parking are not designed.',
                     'Lights, fences and bleachers are indicative; the scoreboards are blank.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='Two soccer pitches and two ball diamonds round a central plaza and fieldhouse, with bleachers, field lights '
                    'and a promenade. Prepared level ground.')
    return meshes, nodes, meta
