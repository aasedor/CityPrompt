"""Prairie Bowl Skate Park: an original native park after the catalogue skate park's
"Naturalized Active" references (frontend/public/archetypes/openspaces/skate-park/variant_2*).

Concrete bowls and a snake run set into native prairie planting, with curved timber
terraces in a grass berm, a street-skating plaza, and a gravel path loop. Not a
skate-park design: bowl depths and transitions are typical teaching values.
"""
from __future__ import annotations

import math
import random

import numpy as np
import parkkit as kit
import shapely
from parkkit import Instances, Parts
from shapely.geometry import LineString, Point, Polygon, box

PARK_ID = 'student_prairie_bowl_skate_park_v1'
ARCHETYPE = 'skate_park'
TITLE = 'Prairie Bowl Skate Park'
GENERATOR = 'CityPrompt native park batch builder v1 (skate)'
REFERENCE = 'frontend/public/archetypes/openspaces/skate-park/variant_2'

SITE_W, SITE_D = 64.0, 52.0
ENTRANCE = dict(x=0, y=-26, widthM=2.2, arrivalY=-23)
DECK = 2.4                       # flat concrete deck around every bowl
TERRACE_CENTRE, TERRACE_R0, STEP, RISE, STEPS = (-12.0, -3.0), 7.6, .75, .40, 4
TERRACE_A = (math.radians(150), math.radians(246))
BERM_OUT = 14.0
PLAZA = (12.0, -13.0, 24.0, 9.0)
CONCRETE, CONCRETE_DARK, CORTEN = '#bcb8af', '#a7a39a', '#7b4a2e'


def chaikin(points, rounds=3):
    for _ in range(rounds):
        out = [points[0]]
        for a, b in zip(points, points[1:]):
            out += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        out.append(points[-1])
        points = out
    return points


# ---- the bowls: shapes and their depths ----------------------------------------------------
SHAPES = [
    ('kidney bowl', kit.smooth(Point(-12, -3).buffer(5.0, quad_segs=24).union(Point(-6.5, -7.5).buffer(3.6, quad_segs=24)), 2.0), 2.4),
    ('clover bowl', kit.smooth(Point(6, 2.5).buffer(4.0, quad_segs=24).union(Point(10.2, 6.8).buffer(3.0, quad_segs=24))
                               .union(Point(5, 8.6).buffer(2.6, quad_segs=24)), 1.4), 1.8),
    ('snake run', LineString(chaikin([(-12, 0.5), (-13.2, 5.5), (-9.5, 10.8), (-3.5, 13.2), (1.5, 12.3), (4.6, 9.2)])).buffer(1.7, quad_segs=16), 1.3),
]
BOWL = kit.smooth(shapely.union_all([s for _, s, _ in SHAPES]), .6)
SUNKEN, DEEPEST = BOWL, -max(r for _, _, r in SHAPES)   # verify.py: the only ground below grade, and how deep


def extra_checks(tris, recipe):
    """Skate-specific: the bowls reach their declared depths, and steel coping runs along every bowl edge."""
    concrete = np.concatenate([t for n, t, _, _ in tris if n == 'concrete']).reshape(-1, 3)
    metal = np.concatenate([t for n, t, _, _ in tris if n == 'metal']).reshape(-1, 3)
    out = []
    for name, shape, radius in SHAPES:
        others = shapely.union_all([o for n, o, _ in SHAPES if n != name]).buffer(2.0)
        core = shape.buffer(-.2).difference(others)          # away from the junctions, where depths blend
        inside = concrete[shapely.contains_xy(core, concrete[:, 0], concrete[:, 1])]
        out.append((f'{name} reaches {radius:.1f} m below the coping', abs(inside[:, 2].min() + radius) < .15))
    edge = np.array(kit.sample_ring(BOWL.exterior, 2.0) if hasattr(BOWL, 'exterior') else [])
    near = [np.min(np.hypot(metal[:, 0] - x, metal[:, 1] - y)) < .12 for x, y in edge]
    out.append((f'steel coping at {len(near)} sampled points along the bowl edge', bool(near) and all(near)))
    return out


def depth_radius(pts):
    """Transition radius, blended smoothly between the bowls so their junctions form hips."""
    p = shapely.points(pts)
    weights, radii = [], []
    for _, shape, radius in SHAPES:
        sd = shapely.distance(shape.boundary, p) * np.where(shapely.contains_xy(shape, pts[:, 0], pts[:, 1]), -1, 1)
        weights.append(np.exp(-sd / .6))
        radii.append(radius)
    w = np.array(weights)
    return (w * np.array(radii)[:, None]).sum(axis=0) / w.sum(axis=0)


def bowl_z(pts):
    """Quarter-circle transitions from a flat bottom to vertical at the coping."""
    w = shapely.distance(BOWL.boundary, shapely.points(pts))
    r = depth_radius(pts)
    w = np.minimum(w, r)
    return -np.sqrt(np.maximum(r * r - (r - w) ** 2, 0.0))


# ---- the ground plan --------------------------------------------------------------------------
def sector(r0, r1, a0, a1, centre=TERRACE_CENTRE, n=48):
    cx, cy = centre
    outer = [(cx + r1 * math.cos(a), cy + r1 * math.sin(a)) for a in np.linspace(a0, a1, n)]
    inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)) for a in np.linspace(a1, a0, n)]
    return Polygon(outer + inner)


def plan():
    site = box(-SITE_W / 2, -SITE_D / 2, SITE_W / 2, SITE_D / 2)
    deck_raw = kit.smooth(BOWL.buffer(DECK, quad_segs=16), 1.2)
    plaza = kit.smooth(box(*PLAZA), 1.5)
    floor_outline = Polygon(deck_raw.exterior) if isinstance(deck_raw, Polygon) else deck_raw
    islands = [Polygon(r) for r in deck_raw.interiors if Polygon(r).area > 4] if isinstance(deck_raw, Polygon) else []
    floor = shapely.union_all([floor_outline, plaza]).difference(BOWL)
    for island in islands:
        floor = floor.difference(island)
    steps = [sector(TERRACE_R0 + k * STEP, TERRACE_R0 + (k + 1) * STEP, *TERRACE_A) for k in range(STEPS)]
    terrace = shapely.union_all(steps)
    pad = math.radians(14)
    berm = sector(TERRACE_R0, BERM_OUT, TERRACE_A[0] - pad, TERRACE_A[1] + pad).difference(terrace).difference(floor).difference(BOWL)
    ring = [(0, -20.5), (14, -19.2), (26.8, -12), (28, 3), (24.5, 17), (10, 21.8), (-6, 21.6), (-20.5, 18.5), (-28.6, 6),
            (-28.6, -9), (-18, -19.4)]
    loop = LineString(chaikin(ring + ring[:1], 4))
    spur = LineString([(0, -SITE_D / 2), (0, -21.5), (.6, -17.0), (-.4, -13.6)])
    north = LineString([(-4.0, 21.6), (-4.4, 19.4), (-3.6, 17.0)])
    lines = [loop, spur, north]
    paths = shapely.union_all([line.buffer(1.1, quad_segs=8) for line in lines]).difference(floor).difference(berm).difference(BOWL)
    paths = paths.intersection(site)
    lawn = shapely.union_all([line.buffer(1.6) for line in lines]).difference(paths).difference(floor).difference(berm).intersection(site)
    band = floor_outline.buffer(4.2, quad_segs=12).difference(floor_outline).difference(plaza.buffer(.5)).difference(terrace).difference(berm)
    band = band.difference(shapely.union_all([line.buffer(2.6) for line in lines])).intersection(site)
    taken = shapely.union_all([floor, BOWL, terrace, berm, paths, lawn, band, *islands])
    meadow = site.difference(taken)
    return dict(site=site, floor=floor, deck=floor.difference(plaza), plaza=floor.intersection(plaza), islands=islands, steps=steps,
                terrace=terrace, berm=berm, paths=paths, lawn=lawn, meadow=meadow, loop=loop, spur=spur, north=north, band=band,
                deck_raw=deck_raw)


def berm_z(pts):
    cx, cy = TERRACE_CENTRE
    r = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
    a = np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx) % math.tau
    top = STEPS * RISE
    r1 = TERRACE_R0 + STEPS * STEP
    radial = np.where(r <= r1, top * np.clip((r - TERRACE_R0) / (r1 - TERRACE_R0), 0, 1) ** .7, top * np.clip((BERM_OUT - r) / (BERM_OUT - r1), 0, 1))
    pad = math.radians(14)
    along = np.clip(np.minimum(a - (TERRACE_A[0] - pad), (TERRACE_A[1] + pad) - a) / pad, 0, 1)
    return radial * (3 * along ** 2 - 2 * along ** 3)


# ---- built elements ------------------------------------------------------------------------------
def terraces(parts, layout):
    conc, timber = parts['concrete'], parts['timber']
    for k, step in enumerate(layout['steps']):
        top = (k + 1) * RISE
        kit.extrude(conc, CONCRETE_DARK, step, 0.0, top - .06)
        kit.extrude(timber, '#9b7652', step.buffer(-.02), top - .06, top, top_colour='#a98260')
        # board joints along each seat, every 0.15 m of the step's depth
        r0 = TERRACE_R0 + k * STEP
        for j in range(1, 5):
            joint = sector(r0 + j * STEP / 5 - .006, r0 + j * STEP / 5 + .006, TERRACE_A[0] + .004, TERRACE_A[1] - .004, n=40)
            for tri in kit.triangulate(joint):
                kit._tri_up(timber, [(x, y, top + .002) for x, y in tri], '#6d5238')


def coping(parts):
    metal = parts['metal']
    for poly in kit.polygons(BOWL):
        for ring in [poly.exterior, *poly.interiors]:
            pts = kit.sample_ring(ring, .55)
            kit.tube(metal, [(x, y, -.035) for x, y in pts], .035, '#8c9397', sides=5, closed=True)


def box_solid(solid, colour, x0, y0, x1, y1, z0, z1):
    kit.extrude(solid, colour, box(x0, y0, x1, y1), z0, z1)


def plaza_features(parts):
    conc, metal = parts['concrete'], parts['metal']
    # stair set: a 0.54 m platform with three steps down to the west, a handrail and a hubba ledge
    box_solid(conc, CONCRETE, 19.0, -13.0, 24.0, -8.0, 0, .54)
    for k in range(2):                       # nosings at x 19.0, 18.65 and 18.3: three 0.18 m risers
        box_solid(conc, CONCRETE, 19.0 - (k + 1) * .35, -12.6, 19.0 - k * .35, -8.4, 0, .54 - (k + 1) * .18)
    # a handrail 0.36 m above the nosing line, kinked flat at both ends
    rail = '#4c5357'
    kit.tube(metal, [(19.45, -10.5, .9), (19.0, -10.5, .9), (17.95, -10.5, .36), (17.45, -10.5, .36)], .03, rail)
    metal.cyl((19.4, -10.5, .54), (19.4, -10.5, .9), .03, rail, sides=6)
    metal.cyl((17.5, -10.5, 0), (17.5, -10.5, .36), .03, rail, sides=6)
    # a hubba ledge beside the steps, 0.4 m above the nosing line from foot to platform
    conc.quad((17.95, -8.4, .4), (19.0, -8.4, .94), (19.0, -8.0, .94), (17.95, -8.0, .4), CONCRETE)
    conc.quad((17.95, -8.4, 0), (19.0, -8.4, 0), (19.0, -8.4, .94), (17.95, -8.4, .4), CONCRETE_DARK)
    conc.quad((19.0, -8.0, 0), (17.95, -8.0, 0), (17.95, -8.0, .4), (19.0, -8.0, .94), CONCRETE_DARK)
    conc.quad((17.95, -8.0, 0), (17.95, -8.4, 0), (17.95, -8.4, .4), (17.95, -8.0, .4), CONCRETE_DARK)
    # two ledges with steel edges, a flat rail and a manual pad
    for (cx, cy, length, width, yaw) in ((15.0, -6.0, 4.0, .55, math.pi / 2), (16.5, 5.0, 4.0, .55, 0.0)):
        with conc.at(cx, cy, 0, yaw):
            conc.box((0, 0, .21), (length, width, .42), CONCRETE)
        with metal.at(cx, cy, 0, yaw):
            for side in (-1, 1):
                metal.box((0, side * (width / 2 - .015), .415), (length, .03, .03), '#5b6266')
    kit.tube(metal, [(19.5, -4.0, .36), (19.5, 1.0, .36)], .03, '#4c5357')
    for y in (-3.6, .6):
        metal.cyl((19.5, y, 0), (19.5, y, .36), .03, '#4c5357', sides=6)
    box_solid(conc, CONCRETE, 13.8, -.3, 16.3, 1.3, 0, .22)
    # a bank rising east to a 1.0 m deck along the plaza's edge
    x0, x1, x2, y0, y1, h = 21.0, 23.4, 24.0, 1.0, 8.0, 1.0
    conc.quad((x0, y0, 0), (x1, y0, h), (x1, y1, h), (x0, y1, 0), CONCRETE)
    conc.quad((x1, y0, h), (x2, y0, h), (x2, y1, h), (x1, y1, h), CONCRETE)
    conc.quad((x2, y0, 0), (x2, y1, 0), (x2, y1, h), (x2, y0, h), CONCRETE_DARK)
    for y, sign in ((y0, 1), (y1, -1)):
        pts = [(x0, y, 0), (x2, y, 0), (x2, y, h), (x1, y, h)]
        if sign < 0:
            pts = pts[::-1]
        conc.quad(*pts, CONCRETE_DARK)
    metal.box((x1, (y0 + y1) / 2, h + .01), (.06, y1 - y0, .03), '#5b6266')


def corten_edges(parts, layout):
    steel = parts['metal']
    for island in layout['islands']:
        pts = kit.sample_ring(island.exterior, .4)
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            steel.quad((ax, ay, 0), (bx, by, 0), (bx, by, .12), (ax, ay, .12), CORTEN)


# ---- planting and furniture --------------------------------------------------------------------
def scatter(region, spacing, rng, clearance=None):
    minx, miny, maxx, maxy = region.bounds
    out = []
    for x in np.arange(minx, maxx, spacing):
        for y in np.arange(miny, maxy, spacing):
            px, py = x + rng.uniform(-.4, .4) * spacing, y + rng.uniform(-.4, .4) * spacing
            if region.contains(Point(px, py)) and (clearance is None or not clearance.contains(Point(px, py))):
                out.append((px, py))
    return out


def planting(inst, layout):
    rng = random.Random(2026)
    site = layout['site']
    keep_off = shapely.union_all([layout['paths'], layout['floor'], BOWL, layout['terrace']]).buffer(.55)
    # the planted band hugging the deck: tall grasses, perennials and shrubs at close spacing
    band_mix = ['feather-reed-grass', 'feather-reed-grass', 'rough-fescue-drift', 'wild-bergamot', 'goldenrod', 'fireweed',
                'shrubby-cinquefoil', 'snowberry', 'blanketflower', 'wolf-willow']
    for x, y in scatter(layout['band'].buffer(-.35), 1.45, rng, keep_off):
        inst.plant(rng.choice(band_mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.35))
    for island in layout['islands']:
        for x, y in scatter(island.buffer(-.4), 1.15, rng):
            inst.plant(rng.choice(['feather-reed-grass', 'rough-fescue-drift', 'wild-bergamot', 'shrubby-cinquefoil']), x, y,
                       yaw=rng.uniform(0, math.tau), scale=rng.uniform(1.0, 1.3))
    # the wider prairie meadow, lower and looser
    meadow_mix = ['rough-fescue-drift', 'rough-fescue-drift', 'rough-fescue-drift', 'blue-grama', 'blue-grama', 'june-grass',
                  'blanketflower', 'wild-blue-flax', 'prairie-smoke']
    for x, y in scatter(layout['meadow'].buffer(-.9), 2.5, rng, keep_off):
        inst.plant(rng.choice(meadow_mix), x, y, yaw=rng.uniform(0, math.tau), scale=rng.uniform(.9, 1.25))
    # shrubs along the berm's crest
    cx, cy = TERRACE_CENTRE
    for a in np.linspace(TERRACE_A[0] + .04, TERRACE_A[1] - .04, 11):
        r = BERM_OUT - 1.3
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        if not keep_off.contains(Point(x, y)):
            inst.plant(rng.choice(['saskatoon', 'wolf-willow', 'snowberry', 'buffaloberry']), x, y,
                       z=float(berm_z(np.array([[x, y]]))[0]), yaw=rng.uniform(0, math.tau))
    # shade trees: aspen groves near the seating and in the corners, bur oaks on the open meadow
    trees = [('trembling-aspen', -24.0, 12.5), ('trembling-aspen', -22.0, 14.5), ('trembling-aspen', -25.0, 9.5),
             ('trembling-aspen', 17.0, 15.5), ('trembling-aspen', 19.5, 13.0), ('trembling-aspen', -10.0, 17.8),
             ('trembling-aspen', 6.5, -15.0), ('trembling-aspen', 9.5, -16.0), ('trembling-aspen', -23.0, -14.5),
             ('bur-oak', -20.5, 22.0 - 5.2), ('bur-oak', 21.5, -20.5), ('bur-oak', 25.5, 21.0 - 4.5), ('bur-oak', -26.5, -20.6)]
    margin = {'trembling-aspen': 3.2, 'bur-oak': 5.2}
    for slug, x, y in trees:
        inside = site.buffer(-margin[slug]).contains(Point(x, y))
        if inside and not keep_off.buffer(1.0).contains(Point(x, y)):
            inst.plant(slug, x, y, yaw=rng.uniform(0, math.tau))


def furniture(parts, layout):
    furn = parts['furniture']
    deck_edge = layout['deck_raw'].exterior
    benches = []
    for frac in (.08, .3, .52, .74):
        p = deck_edge.interpolate(frac, normalized=True)
        q = deck_edge.interpolate(frac + .002, normalized=True)
        tx, ty = q.x - p.x, q.y - p.y
        length = math.hypot(tx, ty)
        nx, ny = -ty / length, tx / length                       # left normal of the ring
        inward = Point(p.x + nx, p.y + ny)
        if not layout['deck_raw'].contains(inward):
            nx, ny = -nx, -ny
        x, y = p.x + nx * .7, p.y + ny * .7
        if layout['plaza'].buffer(.5).contains(Point(x, y)) or layout['terrace'].buffer(1.0).contains(Point(x, y)):
            continue
        benches.append((x, y, math.atan2(ny, nx)))
        kit.bench(furn, x, y, math.atan2(ny, nx))
    for x, y in ((2.2, -16.0), (-16.5, -12.0)):
        kit.waste_bin(furn, x, y)
    for frac in (0, .17, .34, .51, .68, .85):
        p = deck_edge.interpolate(frac, normalized=True)
        if not layout['plaza'].buffer(1).contains(p):
            kit.light_pole(parts['metal'], p.x, p.y)
    kit.bike_rack(parts['metal'], -2.6, -19.5, 0.0)
    kit.drinking_fountain(furn, 2.4, -20.0, math.pi)
    kit.sign_board(furn, -2.2, -23.6, 0.0)
    return benches


def build():
    parts = Parts(2600)
    layout = plan()
    floor_parts = parts['paving']
    kit.fill(floor_parts.body, 'deck', layout['deck'])
    kit.fill(floor_parts.body, 'plaza', layout['plaza'])
    for island in layout['islands']:
        kit.fill(parts['grass'].body, 'bed', island, z=.005, cell=1.5)
    kit.fill(parts['gravel'].body, 'gravel', layout['paths'], z=.0)
    kit.fill(parts['grass'].body, 'lawn', layout['lawn'])
    kit.fill(parts['grass'].body, 'bed', layout['band'], z=.004, cell=1.8)
    kit.fill(parts['grass'].body, 'meadow', layout['meadow'], cell=2.5)
    kit.heightfield(parts['grass'].body, 'berm', layout['berm'], berm_z, spacing=.6, rings=(.3,), ring_step=.6)
    bowl_tris = kit.heightfield(parts['concrete'].body, 'bowl', BOWL, bowl_z, spacing=.35,
                                rings=(.03, .08, .15, .25, .4, .6, .85, 1.1, 1.4, 1.75, 2.1, 2.5), ring_step=.25)
    terraces(parts, layout)
    coping(parts)
    plaza_features(parts)
    corten_edges(parts, layout)
    benches = furniture(parts, layout)
    inst = Instances()
    planting(inst, layout)
    meshes, nodes = kit.assemble(parts, inst, 'skate')
    routes = kit.route_segments(layout['spur'], 2.2) + kit.route_segments(layout['loop'], 2.2) + kit.route_segments(layout['north'], 2.2)
    meta = dict(
        id=PARK_ID, title=TITLE, archetype=ARCHETYPE, generator=GENERATOR, site=(SITE_W, SITE_D), entrance=ENTRANCE,
        walk_surface_materials=['paving', 'grass', 'gravel'], reference=REFERENCE, routes=routes, bowl_triangles=bowl_tris,
        benches=len(benches), hazards=[], deepest=-max(r for _, _, r in SHAPES),
        programme='Three linked concrete bowls (a 2.4 m kidney bowl, a 1.8 m clover bowl and a snake run) with steel coping, set into '
                  'native prairie planting; curved timber terrace seating in a grass berm; a street-skating plaza with a stair set, '
                  'handrail, hubba, ledges, flat rail, manual pad and bank; a gravel entrance spur and loop; benches, lights, bins, a '
                  'bike rack and a drinking fountain; aspen and bur oak.',
        design_basis='Original concept after the catalogue skate park "Naturalized Active" references (variant 2): bowls and a snake '
                     'run set into native planting with timber terraces. Depths and transitions are typical teaching values, not a '
                     'skate-park design.',
        limitations=['Prepared level ground only. The bowls go 2.4 m below grade inside the park; drainage is not modelled.',
                     'Bowl transitions are quarter circles from a flat bottom to vertical at the coping; real parks are designed and '
                     'built by specialist firms.',
                     'Skating surfaces are not walking routes: walkers use the deck, plaza, paths and grass.',
                     'The complete assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'],
        group='play_sport',
        description='Concrete bowls and a snake run set into prairie meadow, with timber terrace seating, a street plaza and a path loop. '
                    'Prepared level ground.')
    return meshes, nodes, meta
