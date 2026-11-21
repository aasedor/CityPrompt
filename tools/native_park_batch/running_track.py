"""Community Track & Field: an original native park after the catalogue running track and
athletic oval's "Community Park Track" references
(frontend/public/archetypes/openspaces/running-track-athletic-oval/variant_1*).

A six-lane 400 m track on the standard geometry (36.5 m bends, 84.39 m straights, 1.22 m
lanes) round a grass infield with a full soccer pitch and goals; a long jump runway and
sand pit beside the home straight; a shot put circle in the west D; stagger starts and the
finish line; a concrete walk ringing the track with lights and benches; bleachers, a timber
shelter, a hurdle stack and a timber fitness station; groves and flowering trees. Teaching
values, not a competition facility design.
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

PARK_ID = 'student_community_track_field_v1'
ARCHETYPE = 'running_track_oval'
TITLE = 'Community Track & Field'
GENERATOR = 'CityPrompt native park batch builder v1 (track)'
REFERENCE = 'frontend/public/archetypes/openspaces/running-track-athletic-oval/variant_1'
KIT_SOURCES = ('sportskit.py',)

SITE_W, SITE_D = 200.0, 112.0
A = 84.39 / 2                    # half the straight
R0 = 36.5                        # inner kerb radius
LANE, LANES = 1.22, 6
R1 = R0 + LANE * LANES           # outer edge of lane six
WALK_OFF, WALK_W = 6.2, 3.0      # walk centre line outside the track edge, and its width
PITCH = (100.0, 64.0)
ENTRANCE = dict(x=0.0, y=-56.0, widthM=3.0, arrivalY=-53.0)
RUNWAY_Y, RUNWAY = -45.6, (-45.0, -6.0)        # long jump runway centre line and its x extent; take-off board at its end
PIT = (-5.0, 4.0, 2.75)                        # sand pit x extent and width
SHOT = (-A - 22.0, 0.0)                        # shot put circle in the west D, throwing west
SUNKEN, DEEPEST = None, 0.0


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    infield = sk.stadium(A, R0)
    track = sk.stadium(A, R1).difference(infield)
    outer = sk.stadium(A, R1 + .5)
    walk_line = LineString(list(sk.stadium(A, R1 + WALK_OFF).exterior.coords))
    walk = sk.stadium(A, R1 + WALK_OFF + WALK_W / 2).difference(sk.stadium(A, R1 + WALK_OFF - WALK_W / 2))
    entry = box(ENTRANCE['x'] - 1.5, -SITE_D / 2, ENTRANCE['x'] + 1.5, -(R1 + WALK_OFF))
    paving = walk.union(entry).intersection(site)
    runway = box(RUNWAY[0], RUNWAY_Y - LANE / 2, PIT[0], RUNWAY_Y + LANE / 2)
    pit = box(PIT[0], RUNWAY_Y - PIT[2] / 2, PIT[1], RUNWAY_Y + PIT[2] / 2)
    pit_edge = pit.buffer(.18, join_style='mitre').difference(pit)
    shot_pad = Point(*SHOT).buffer(1.0675 + .6, quad_segs=24)
    aprons = shapely.union_all([box(A + R1 - 1.0, -6.5, A + R1 + WALK_OFF - WALK_W / 2 + .01, 6.5),     # shelter pad, east end
                                box(-A - R1 - WALK_OFF + WALK_W / 2 - .01, -4.5, -A - R1 - 1.0, 4.5),  # fitness pad, west end
                                box(14.4, -R1 - WALK_OFF + WALK_W / 2 - .01, 30.2, -R1 - .6)])      # bleacher pad
    band = sk.stadium(A, R1 + WALK_OFF - WALK_W / 2).difference(outer).difference(aprons).difference(runway).difference(pit_edge.union(pit))
    infield_grass = infield.difference(shot_pad)
    outside = site.difference(sk.stadium(A, R1 + WALK_OFF + WALK_W / 2)).difference(entry)
    beds = shapely.union_all([
        kit.smooth(kit.ellipse(84.0, 46.0, 6.5, 3.2, math.radians(-28)), 1.2), kit.smooth(kit.ellipse(-84.0, 46.0, 6.5, 3.2, math.radians(28)), 1.2),
        kit.smooth(kit.ellipse(84.0, -46.0, 6.5, 3.2, math.radians(28)), 1.2), kit.smooth(kit.ellipse(-84.0, -46.0, 6.5, 3.2, math.radians(-28)), 1.2),
    ]).intersection(outside.buffer(-.5)).difference(entry.buffer(1.0))
    lawn = outside.difference(beds)
    edge = outer.difference(sk.stadium(A, R1)).difference(runway)          # a concrete edge strip outside lane six
    return dict(site=site, infield=infield, infield_grass=infield_grass, track=track, outer=outer, edge=edge, walk=walk, walk_line=walk_line,
                entry=entry, paving=paving, runway=runway, pit=pit, pit_edge=pit_edge, shot_pad=shot_pad, aprons=aprons, band=band,
                beds=beds, lawn=lawn, outside=outside)


# ---- markings ----------------------------------------------------------------------------------
def markings(furn, metal):
    lines = [sk.stadium(A, R0 + LANE * k).exterior.buffer(.025) for k in range(1, LANES + 1)]
    lines.append(box(A - .025, -R1, A + .025, -R0))                                 # finish line, end of the home straight
    for n in range(2, LANES + 1):                                                    # 400 m stagger starts on the east bend
        run_n, run_1 = R0 + LANE * (n - 1) + .20, R0 + .30
        theta = -math.pi / 2 + 2 * math.pi * (run_n - run_1) / run_n
        r_in, r_out = R0 + LANE * (n - 1), R0 + LANE * n
        c, s = math.cos(theta), math.sin(theta)
        lines.append(LineString([(A + r_in * c, r_in * s), (A + r_out * c, r_out * s)]).buffer(.025, cap_style='flat'))
    w, d = PITCH
    pitch_lines = [box(-w / 2, -d / 2, w / 2, d / 2).exterior.buffer(.06), box(-.06, -d / 2, .06, d / 2),
                   Point(0, 0).buffer(9.15, quad_segs=32).exterior.buffer(.06), Point(0, 0).buffer(.2)]
    for s in (-1, 1):
        x0 = s * w / 2
        pitch_lines += [Polygon([(x0, -20.16), (x0 - s * 16.5, -20.16), (x0 - s * 16.5, 20.16), (x0, 20.16)]).exterior.buffer(.06),
                        Polygon([(x0, -9.16), (x0 - s * 5.5, -9.16), (x0 - s * 5.5, 9.16), (x0, 9.16)]).exterior.buffer(.06),
                        Point(x0 - s * 11, 0).buffer(.2),
                        Point(x0 - s * 11, 0).buffer(9.15, quad_segs=32).exterior.buffer(.06).difference(
                            box(min(x0, x0 - s * 16.5), -30, max(x0, x0 - s * 16.5), 30))]
    sk.chalk(furn, shapely.union_all(lines + pitch_lines))
    # shot put: a 2.135 m concrete circle, a white stop board and the 34.92 degree landing sector
    cx, cy = SHOT
    sector = []
    for s in (-1, 1):
        a = math.pi + s * math.radians(34.92 / 2)
        sector.append(LineString([(cx + 1.07 * math.cos(a), cy + 1.07 * math.sin(a)), (cx + 20 * math.cos(a), cy + 20 * math.sin(a))]).buffer(.03))
    sk.chalk(furn, shapely.union_all(sector))
    board = Point(cx, cy).buffer(1.0675 + .11, quad_segs=24).difference(Point(cx, cy).buffer(1.0675, quad_segs=24)).intersection(
        box(cx - 3, cy - .6, cx - .5, cy + .6))
    kit.extrude(furn, sk.WHITE, board, 0, .1)
    kit.extrude(metal, '#6f777b', Point(cx, cy).buffer(1.0675 + .02, quad_segs=24).difference(Point(cx, cy).buffer(1.0675, quad_segs=24)), 0, .02)
    # long jump take-off board and runway edge lines
    kit.extrude(furn, sk.WHITE, box(RUNWAY[1] - .2, RUNWAY_Y - LANE / 2, RUNWAY[1], RUNWAY_Y + LANE / 2), 0, .016)
    sk.chalk(furn, box(RUNWAY[0], RUNWAY_Y - LANE / 2, PIT[0], RUNWAY_Y + LANE / 2).exterior.buffer(.025), z=.02)
    # the inner kerb: a low white aluminium kerb round the infield
    ring = sk.stadium(A, R0).buffer(-.0).exterior
    for (ax, ay), (bx, by) in zip(ring.coords, list(ring.coords)[1:]):
        length = math.hypot(bx - ax, by - ay)
        if length > 1e-6:
            furn.box(((ax + bx) / 2, (ay + by) / 2, .03), (length + .01, .05, .06), '#e9eae6', yaw=math.atan2(by - ay, bx - ax))


# ---- buildings and furniture -------------------------------------------------------------------
def fitness_station(timber, metal, x, y):
    """Timber posts of stepped heights with pull-up and dip bars, in a row along y."""
    heights = [1.0, 1.4, 1.9, 2.3, 2.3, 1.9, 1.4]
    for k, h in enumerate(heights):
        timber.box((x, y - 4.2 + k * 1.4, h / 2), (.22, .22, h), '#8a6844')
    for k in range(len(heights) - 1):
        h = min(heights[k], heights[k + 1]) - .1
        kit.tube(metal, [(x, y - 4.2 + k * 1.4, h), (x, y - 4.2 + (k + 1) * 1.4, h)], .025, sk.POST)


def furniture(parts, layout):
    furn, metal, timber, conc = parts['furniture'], parts['metal'], parts['timber'], parts['concrete']
    for s in (-1, 1):
        sk.goal(metal, s * PITCH[0] / 2, 0.0, math.pi if s > 0 else 0.0)
    for x in (18.6, 26.0):
        sk.bleacher(metal, x, -R1 - .6 - 1.6, math.pi / 2, length=6.8)
    sk.shelter(timber, metal, A + R1 + 2.9, 0.0, math.pi, length=10.0, depth=4.2)
    for k in range(6):
        sk.hurdle(furn, A + R1 + 1.2, -4.8 - k * .12, math.pi, height=.84)
    fitness_station(timber, metal, -A - R1 - 2.8, 0.0)
    walk_r = R1 + WALK_OFF
    edge = sk.stadium(A, walk_r + WALK_W / 2 + .5).exterior
    for k, d in enumerate(np.arange(8.0, edge.length, 26.0)):
        x, y = edge.interpolate(d).coords[0]
        if abs(x - ENTRANCE['x']) > 4 or y > 0:
            kit.light_pole(furn, x, y, height=4.5)
    bench_edge = sk.stadium(A, walk_r - WALK_W / 2 - .45).exterior
    for d in np.arange(30.0, bench_edge.length, 42.0):
        x, y = bench_edge.interpolate(d).coords[0]
        nx, ny = bench_edge.interpolate(d + .5).coords[0]
        if layout['band'].buffer(-.3).contains(Point(x, y)):
            kit.bench(furn, x, y, math.atan2(ny - y, nx - x) + math.pi / 2)
    for x, y in ((4.0, -53.6), (-4.0, -53.6), (A + R1 + 5.0, 8.0), (-A - R1 - 5.0, -6.5)):
        kit.waste_bin(furn, x, y)
    kit.drinking_fountain(furn, 4.2, -48.6, math.pi / 2)
    kit.bike_rack(metal, -7.0, -53.4, 0.0, loops=4)
    kit.sign_board(furn, -2.8, -55.0, 0.0, colour='#2f5a3b')


# ---- planting ----------------------------------------------------------------------------------
def planting(inst, layout):
    rng = random.Random(7070)
    site = layout['site']
    keep_off = shapely.union_all([layout['paving'], layout['outer'], layout['aprons']]).buffer(.6)
    radius = {}

    def reach(slug):
        if slug not in radius:
            key = inst.add_plant(slug)
            pts = np.concatenate([np.array(inst.meshes[f'{key}-{p}'][1].positions).reshape(-1, 3)
                                  for p in ('wood', 'foliage') if inst.meshes[f'{key}-{p}'][1].positions])
            radius[slug] = float(np.hypot(pts[:, 0], pts[:, 1]).max())
        return radius[slug]
    shrubs = ['snowberry', 'shrubby-cinquefoil', 'feather-reed-grass', 'feather-reed-grass', 'blanketflower', 'wild-bergamot']
    for poly in kit.polygons(layout['beds']):
        spacing = 2.1
        for x, y in kit.scatter(poly.buffer(-.4), spacing, rng, keep_off):
            inst.plant(rng.choice(shrubs), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    trees = []
    corners = layout['outside'].difference(box(-A, -SITE_D, A, SITE_D))
    candidates = kit.scatter(corners, 5.0, rng)
    rng.shuffle(candidates)
    walk_outer = sk.stadium(A, R1 + WALK_OFF + WALK_W / 2)
    for slug, count, gap in (('trembling-aspen', 12, 4.5), ('green-ash', 10, 7.5), ('bur-oak', 6, 9.0), ('white-spruce', 9, 6.0)):
        placed = 0
        for x, y in candidates:
            if placed >= count:
                break
            scale = rng.uniform(.75, 1.0)
            r = reach(slug) * scale
            p = Point(x, y)
            if not site.buffer(-(r + .3)).contains(p) or walk_outer.buffer(1.8).contains(p) or keep_off.buffer(1.2).contains(p):
                continue
            if any(math.hypot(x - tx, y - ty) < gap * .5 + (r + tr) * .45 for tx, ty, tr in trees):
                continue
            trees.append((x, y, r))
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
            placed += 1
    small = ['amur-cherry', 'schubert-chokecherry']
    spots = [(x, y) for x in np.arange(-A + 2.0, A - 1.0, 16.0) for y in (-SITE_D / 2 + 2.05, SITE_D / 2 - 2.05)]
    spots += [(x, y) for y in (-16.0, 0.0, 16.0) for x in (-SITE_W / 2 + 2.6, SITE_W / 2 - 2.6)]
    for k, (x, y) in enumerate(spots):
        slug = small[k % 2]
        scale = min(1.0, 1.85 / reach(slug))
        p = Point(x, y)
        if site.buffer(-(reach(slug) * scale + .15)).contains(p) and not keep_off.buffer(.2).contains(p):
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau), scale=scale)
    return trees


def extra_checks(tris, recipe):
    """Track-specific: lane geometry, the 400 m lap, the pitch and a clear track and infield."""
    def vertices(names):
        return np.concatenate([t for n, t, _, _ in tris if n in names]).reshape(-1, 3)
    rubber = vertices({'rubber'})
    bend = rubber[rubber[:, 0] > A + .5]
    rb = np.hypot(bend[:, 0] - A, bend[:, 1])
    furn = vertices({'furniture'})
    chalk = furn[(np.abs(furn[:, 2] - .012) < .002) & (np.abs(furn[:, 1]) < .3) & (furn[:, 0] > A)]
    lines_ok = all(bool((np.abs(chalk[:, 0] - A - (R0 + LANE * k)) < .04).any()) for k in range(1, LANES + 1))
    lap = 2 * 84.39 + 2 * math.pi * (R0 + .30)
    solid = vertices({'metal', 'concrete', 'furniture', 'wood', 'foliage', 'timber'})
    inside = shapely.contains_xy(sk.stadium(A, R1), solid[:, 0], solid[:, 1]) & (solid[:, 2] > .11)
    goals = (np.abs(np.abs(solid[:, 0]) - PITCH[0] / 2) < 2.2) & (np.abs(solid[:, 1]) < 3.8)
    return [('track inner edge 36.5 m and outer edge 43.82 m from the bend centre (six 1.22 m lanes)',
             bool(abs(rb.min() - R0) < .02 and abs(rb.max() - R1) < .02)),
            ('six lane lines 1.22 m apart on the east bend', lines_ok),
            (f'lane one measures {lap:.2f} m, 0.30 m from the kerb', abs(lap - 400.0) < .05),
            ('the 100 x 64 m pitch fits inside the kerb', bool(sk.stadium(A, R0 - 2.0).contains(box(-50, -32, 50, 32)))),
            ('nothing stands on the track or infield but the goals', not bool((inside & ~goals).any()))]


def build():
    parts = Parts(7100)
    layout = plan()
    g, p = parts['grass'].body, parts['paving'].body
    sk.stripes(g, layout['infield_grass'], 0.0, 5.0, z=0.0, cell=3.0)
    kit.fill(parts['rubber'].body, 'track_red', layout['track'], z=.01, cell=2.5)
    kit.fill(parts['rubber'].body, 'track_red', layout['runway'], z=.01, cell=2.0)
    kit.fill(parts['gravel'].body, 'sand', layout['pit'], z=-.02, cell=1.5)
    kit.fill(p, 'concrete', layout['pit_edge'], z=.03, cell=1.5)
    kit.fill(p, 'concrete', layout['shot_pad'].difference(Point(*SHOT).buffer(1.0675 + .02, quad_segs=24)), z=.01, cell=1.5)
    kit.fill(p, 'concrete', Point(*SHOT).buffer(1.0675, quad_segs=24), z=.005, cell=1.5)
    kit.fill(p, 'concrete', layout['paving'], z=.01, cell=2.5)
    kit.fill(p, 'concrete', layout['aprons'], z=.01, cell=2.0)
    kit.fill(p, 'concrete', layout['edge'], z=.012, cell=2.5)
    kit.fill(g, 'lawn', layout['band'], cell=3.0)
    kit.fill(g, 'lawn', layout['lawn'], cell=3.0)
    kit.fill(g, 'bed', layout['beds'], z=.004, cell=2.5)
    markings(parts['furniture'], parts['metal'])
    furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'track')
    routes = kit.route_segments(LineString([(ENTRANCE['x'], -SITE_D / 2), (ENTRANCE['x'], -(R1 + WALK_OFF))]), 2.4)
    routes += kit.route_segments(layout['walk_line'], 2.6)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'rubber', 'gravel'], reference=REFERENCE, routes=routes,
        programme='A six-lane 400 m track (36.5 m bends, 84.39 m straights, 1.22 m lanes) with an inner kerb, lane lines, stagger '
                  'starts and a finish line; a grass infield with a 100 x 64 m soccer pitch and goals; a long jump runway and sand '
                  'pit beside the home straight; a shot put circle and sector in the west D; a concrete walk ringing the track '
                  'with lights and benches; bleachers, a timber shelter, a hurdle stack and a timber fitness station; prairie '
                  'shrub beds, flowering cherries and groves of aspen, green ash, bur oak and white spruce.',
        design_basis='Original concept after the catalogue running track "Community Park Track" references (variant 1). '
                     'Standard 400 m track geometry as teaching values, not a certified competition facility.',
        limitations=['Prepared level ground only; drainage, base courses and the track surface build-up are not designed.',
                     'Six lanes, as at many schools and community tracks; competition tracks have eight and more field events.',
                     'Markings show lane lines, 400 m stagger starts and the finish line only.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='A six-lane 400 m running track round a soccer pitch, with long jump and shot put, bleachers, a shelter and a '
                    'walking loop through trees. Prepared level ground.')
    return meshes, nodes, meta
