"""Build the Stephen Avenue pedestrian mall as a drawable native street, in pure Python.

The street only: no buildings, +15 skywalks or storefronts. A 20 m section of grey
granite promenade between dark granite borders and red brick frontage zones, with
littleleaf lindens in iron grates, heritage lamps with banners, cafe patios, benches
and litter bins. The shared native street engine repeats one 40 m fixture cycle of
these modules along any route a student draws, bending the surfaces with it.

    python3 tools/stephen_avenue_street/build.py --output <new directory>

Writes the five module GLBs, a 40 m preview assembly for review renders, the source
recipe, the registry row and the modules' occupied bounds. Never overwrites.
Frame: x across the street (east positive when the route runs north), y along it,
z up, metres. Module GLBs are Y-up, as glTF requires.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'detail_catalogue'))
import build_local_foliage as foliage
from calgary_kit import Solid

STREET_ID = 'student_stephen_avenue_mall_v1'
PARENT = 'stephen_avenue_pedestrian_mall'
TITLE = 'Stephen Avenue Pedestrian Mall'
GENERATOR = 'CityPrompt Stephen Avenue street builder v1'
REFERENCE = 'frontend/public/archetypes/streets/stephen-avenue-pedestrian-mall/variant_2.png'
THUMBNAIL = '/archetypes/streets/stephen-avenue-pedestrian-mall/variant_2.png'
REFERENCES = [f'frontend/public/archetypes/streets/stephen-avenue-pedestrian-mall/variant_{i}{s}' for i in range(4)
              for s in ('.png', '_angle_60.jpg', '_angle_90.jpg')]

# ---- section (metres) -------------------------------------------------------------
WIDTH, CYCLE = 20.0, 40.0
PROMENADE = 8.0                    # grey granite, flush, centred
BORDER = .40                       # dark granite band each side of it
FURNITURE_X = 5.20                 # the line of trees, lamps, benches and bins, each side
PATIO_X = 8.775                    # patio centres: the railing's outer face meets the building line at 10
PATIO = (2.4, 7.0)                 # depth across, length along
SECTIONS = [('west_walk', 4.0), ('west_furniture', 2.0), ('promenade', PROMENADE), ('east_furniture', 2.0), ('east_walk', 4.0)]

PALETTE_SRGB = {
    'paving': '#a6a39d',           # grey granite pavers
    'edge': '#7d7a74',             # their joints
    'granite_border': '#55534f',   # dark granite band
    'brick': '#7a4538',            # clay brick frontage zones
    'brick_soldier': '#5e3329',    # soldier course at each edge of the brick
    'brick_joint': '#96786b',      # mortar between courses
}
COURSE = .24                       # a mortar line across the brick zones every this far along the street

IRON, BLACK, BANNER, CANVAS, WOOD, GREEN = '#26292b', '#1d2023', '#a3262b', '#e6dcc4', '#8a6a48', '#2f5a3b'


def linear(hex_colour):
    return [round(v, 4) for v in foliage.srgb_to_linear(hex_colour)]


# ---- modules ----------------------------------------------------------------------
def linden_grate():
    """A littleleaf linden in a 1.5 m square cast-iron grate, crown lifted for walking."""
    s = Solid(41)
    half, frame = .75, .06
    for x0, x1, y0, y1 in ((-half, half, -half, -half + frame), (-half, half, half - frame, half),
                           (-half, -half + frame, -half + frame, half - frame), (half - frame, half, -half + frame, half - frame)):
        s.box(((x0 + x1) / 2, (y0 + y1) / 2, .012), (x1 - x0, y1 - y0, .024), IRON)
    for r in (.62, .48, .34):                       # three concentric square rings of bars
        for k in range(4):
            yaw = k * math.pi / 2
            with s.at(yaw=yaw):
                s.box((r, 0, .01), (.035, 2 * r, .02), IRON)
    for k in range(8):                              # radial ties
        with s.at(yaw=k * math.pi / 4):
            s.box((.48, 0, .009), (.28, .03, .018), IRON)
    s.box((0, 0, .004), (.40, .40, .008), '#3a2e25')  # soil in the trunk opening
    species = copy.deepcopy(next(sp for sp in foliage.SPECIES if sp['slug'] == 'littleleaf-linden'))
    species['params'].update(height=7.2, trunk_radius=.13, reach=2.2, crown_base=.38, lean=.04, leaves=3, twigs=4)
    plant = foliage.build(species)
    return [s.body, s.gloss, plant.wood, plant.foliage]


def heritage_lamp():
    """A black heritage lamp, 4.6 m to its finial, with a red banner on two arms
    reaching toward the promenade (local +x)."""
    s = Solid(42)
    s.cyl((0, 0, 0), (0, 0, .08), .22, BLACK, r1=.20, sides=8)
    s.cyl((0, 0, .08), (0, 0, .55), .16, BLACK, r1=.12, sides=8)
    s.cyl((0, 0, .55), (0, 0, .62), .14, BLACK, sides=8)
    s.cyl((0, 0, .62), (0, 0, 3.85), .075, BLACK, r1=.055, sides=8)
    for z in (2.62, 3.62):
        s.cyl((0, 0, z), (0, 0, z + .06), .085, BLACK, sides=8)
        s.box((.30, 0, z + .03), (.52, .035, .035), BLACK)
    s.box((.31, 0, 3.17), (.46, .012, .86), BANNER)           # banner between the two arms
    s.box((.31, 0, 3.17), (.47, .004, .10), '#e7d7a6')        # a pale band across it, no lettering
    s.cyl((0, 0, 3.85), (0, 0, 3.93), .10, BLACK, r1=.12, sides=8)
    lantern = .17
    for z0, z1 in ((3.93, 3.97), (4.47, 4.51)):
        s.box((0, 0, (z0 + z1) / 2), (2 * lantern + .04, 2 * lantern + .04, z1 - z0), BLACK)
    for dx in (-1, 1):
        for dy in (-1, 1):
            s.box((dx * lantern, dy * lantern, 4.22), (.025, .025, .54), BLACK)
    s.box((0, 0, 4.22), (2 * lantern - .01, 2 * lantern - .01, .50), '#f3e3b0', gloss=True)
    s.cyl((0, 0, 4.51), (0, 0, 4.68), lantern + .05, BLACK, r1=.02, sides=4)
    s.cyl((0, 0, 4.66), (0, 0, 4.76), .018, BLACK, sides=6)
    return [s.body, s.gloss]


def chair(s, x, y, yaw):
    """A wooden bistro chair facing local -x before `yaw`."""
    with s.at(x, y, 0, yaw):
        for dx in (-.19, .19):
            for dy in (-.19, .19):
                s.box((dx, dy, .225), (.03, .03, .45), BLACK)
        s.box((0, 0, .46), (.44, .44, .03), WOOD)
        for dy in (-.19, .19):
            s.box((.20, dy, .66), (.03, .03, .42), BLACK)
        s.box((.205, 0, .78), (.02, .42, .14), WOOD)


def umbrella(s, x, y, size=2.1):
    s.cyl((x, y, 0), (x, y, .04), .22, BLACK, sides=8)
    s.cyl((x, y, .04), (x, y, 2.78), .025, '#5a4636', sides=6)
    h = size / 2
    corners = [(x - h, y - h, 2.32), (x + h, y - h, 2.32), (x + h, y + h, 2.32), (x - h, y + h, 2.32)]
    apex = (x, y, 2.80)
    for a, b in zip(corners, corners[1:] + corners[:1]):
        s.tri(a, b, apex, CANVAS)
        s.tri(a, apex, b, '#d4c8ab')                # underside
        s.quad(a, b, (b[0], b[1], 2.20), (a[0], a[1], 2.20), CANVAS)   # valance
    s.cyl((x, y, 2.80), (x, y, 2.88), .05, CANVAS, r1=.01, sides=6)


def cafe_patio():
    """A cafe patio against the building line (local -x), 2.4 m deep and 7 m long, behind a
    black picket railing 1.0 m high with an entrance gap on its street side. Three
    umbrellas, three tables with four chairs each, and a planter at each street corner."""
    s = Solid(43)
    depth, length = PATIO
    x0, x1, y0, y1 = -depth / 2, depth / 2, -length / 2, length / 2
    gap = (2.0, 3.0)
    runs = [((x1, y0), (x1, gap[0])), ((x1, gap[1]), (x1, y1)), ((x0, y0), (x1, y0)), ((x0, y1), (x1, y1))]
    for (ax, ay), (bx, by) in runs:
        span = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / span, (by - ay) / span
        for z in (.10, .98):
            s.box(((ax + bx) / 2, (ay + by) / 2, z), (abs(bx - ax) + .04, abs(by - ay) + .04, .04), BLACK)
        posts = max(1, round(span / 1.2))
        for k in range(posts + 1):
            t = span * k / posts
            s.box((ax + ux * t, ay + uy * t, .50), (.05, .05, 1.0), BLACK)
        pickets = int(span / .13)
        for k in range(1, pickets):
            t = span * k / pickets
            s.box((ax + ux * t, ay + uy * t, .54), (.018, .018, .84), BLACK)
    for y in (-2.3, 0.0, 2.3):
        umbrella(s, -.05, y)
        s.cyl((-.05, y, 0), (-.05, y, .03), .24, BLACK, sides=8)          # table foot
        s.cyl((-.05, y, .03), (-.05, y, .72), .035, BLACK, sides=6)
        s.box((-.05, y, .735), (.72, .72, .03), '#2b2b2b')
        for dx, dy, yaw in ((.62, 0, 0), (-.62, 0, math.pi), (0, .62, math.pi / 2), (0, -.62, -math.pi / 2)):
            if abs(y + dy) < y1 - .3:
                chair(s, -.05 + dx, y + dy, yaw)
    for y in (y0 + .35, y1 - .35):
        s.box((x1 - .35, y, .25), (.56, .56, .50), '#3d4042')
        s.dome((x1 - .35, y, .50), (.30, .30, .34), '#4f7444', nu=10, nv=4)
    return [s.body, s.gloss]


def litter_bin():
    s = Solid(44)
    s.cyl((0, 0, 0), (0, 0, .05), .30, BLACK, sides=12)
    s.cyl((0, 0, .05), (0, 0, .88), .27, GREEN, sides=12)
    s.cyl((0, 0, .70), (0, 0, .76), .275, '#1f3b29', sides=12)
    s.dome((0, 0, .88), (.27, .27, .12), '#1f3b29', nu=12, nv=3)
    return [s.body, s.gloss]


def bench():
    """A 1.8 m backed bench on black cast ends, facing local +x."""
    s = Solid(45)
    for y in (-.82, .82):
        s.box((0, y, .22), (.50, .07, .44), BLACK)
        s.box((-.22, y, .62), (.06, .07, .40), BLACK)
        s.box((.05, y, .64), (.36, .06, .04), BLACK)                  # armrest
    for k in range(4):
        s.box((.18 - k * .12, 0, .45), (.10, 1.72, .035), WOOD)
    for k in range(3):
        s.box((-.25, 0, .55 + k * .12), (.035, 1.72, .09), WOOD)
    return [s.body, s.gloss]


MODULES = {'linden_grate': linden_grate, 'heritage_lamp': heritage_lamp, 'cafe_patio': cafe_patio,
           'litter_bin': litter_bin, 'bench': bench}


def placements():
    """One 40 m fixture cycle. West items face east, east items face west."""
    out = []

    def put(kind, x, y, yaw=0.0):
        out.append(dict(kind=kind, x=x, y=y, z=0, yaw=round(yaw, 6), scale=1))
    for side, yaw in ((-1, 0.0), (1, math.pi)):
        x = side * FURNITURE_X
        for y in (-15, -5, 5, 15):
            put('linden_grate', x, y)
        for y in (-10, 10):
            put('heritage_lamp', x, y, yaw)
        put('bench', x, 0, yaw)
        put('litter_bin', x, -8.8 if side < 0 else 11.2)
        for y in ((-12, 8) if side < 0 else (-2, 14)):
            put('cafe_patio', side * PATIO_X, y, yaw)
    return out


def program():
    half = PROMENADE / 2
    regions = [dict(x=0, y=0, width=PROMENADE, depth=CYCLE, material='paving')]
    brick = WIDTH / 2 - half - BORDER
    for side in (-1, 1):
        regions.append(dict(x=side * (half + BORDER / 2), y=0, width=BORDER, depth=CYCLE, material='granite_border'))
        regions.append(dict(x=side * (half + BORDER + brick / 2), y=0, width=brick, depth=CYCLE, material='brick'))
    details = []
    for side in (-1, 1):
        for k in range(1, int(CYCLE / COURSE)):
            details.append(dict(x=round(side * (half + BORDER + brick / 2), 4), y=round(-CYCLE / 2 + k * COURSE, 4), width=round(brick, 4),
                                depth=.012, z=.001, height=0, material='brick_joint'))
        for x in (half + BORDER + .10, WIDTH / 2 - .10):
            details.append(dict(x=round(side * x, 4), y=0, width=.2, depth=CYCLE, z=.002, height=0, material='brick_soldier'))
    return dict(schemaVersion=1, adapter='showcase-street-v1', surfaceRegions=regions, details=details, meshDetails=[],
                paving='stone', pavingModuleM=[1.2, .8], minLengthM=30, maxLengthM=300, preparedLevelOnly=True, baseLiftM=.025,
                palette={name: linear(colour) for name, colour in PALETTE_SRGB.items()})


def sections():
    out, cursor = [], -WIDTH / 2
    for name, width in SECTIONS:
        out.append(dict(name=name, x=round(cursor + width / 2, 4), width=width, material='paving'))
        cursor += width
    return out


# ---- GLB output ---------------------------------------------------------------------
def module_glb(kind):
    parts = MODULES[kind]()
    payload, lo, hi, triangles, meshes = foliage.write_glb(parts, kind, GENERATOR)
    # glTF bounds (Y up) back to the street frame: x across, y along, z up
    bounds = dict(plan=[[float(lo[0]), float(-hi[2])], [float(hi[0]), float(-lo[2])]], height=[float(lo[1]), float(hi[1])])
    return payload, bounds, triangles, meshes


def transform_parts(parts, x, y, yaw, scale=1.0):
    c, s = math.cos(yaw), math.sin(yaw)
    out = []
    for part in parts:
        moved = foliage.Part(part.name)
        moved.material = part.material
        p = np.array(part.positions, dtype=float).reshape(-1, 3) * scale
        n = np.array(part.normals, dtype=float).reshape(-1, 3)
        p[:, 0], p[:, 1] = p[:, 0] * c - p[:, 1] * s + x, p[:, 0] * s + p[:, 1] * c + y
        n[:, 0], n[:, 1] = n[:, 0] * c - n[:, 1] * s, n[:, 0] * s + n[:, 1] * c
        moved.positions, moved.normals, moved.colors = p.ravel().tolist(), n.ravel().tolist(), list(part.colors)
        out.append(moved)
    return out


def ground(prog):
    """The 40 m cycle's surfaces as the runtime draws them: regions, granite joints and details."""
    s = Solid(46)
    colour = PALETTE_SRGB

    def rect(material, x0, x1, y0, y1, z):
        s.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), colour[material])
    for r in prog['surfaceRegions']:
        rect(r['material'], r['x'] - r['width'] / 2, r['x'] + r['width'] / 2, r['y'] - r['depth'] / 2, r['y'] + r['depth'] / 2, prog['baseLiftM'])
    a, b = -PROMENADE / 2, PROMENADE / 2
    for j in range(1, int(CYCLE / .8)):
        y = -CYCLE / 2 + j * .8
        rect('edge', a, b, y - .0045, y + .0045, prog['baseLiftM'] + .002)
    for j in range(1, int(PROMENADE / 1.2)):
        x = a + j * 1.2
        rect('edge', x - .0045, x + .0045, -CYCLE / 2, CYCLE / 2, prog['baseLiftM'] + .002)
    for d in prog['details']:
        rect(d['material'], d['x'] - d['width'] / 2, d['x'] + d['width'] / 2, d['y'] - d['depth'] / 2, d['y'] + d['depth'] / 2,
             prog['baseLiftM'] + d['z'])
    return [s.body]


def assembly(prog, places):
    parts = ground(prog)
    built = {kind: MODULES[kind]() for kind in MODULES}
    for p in places:
        parts += transform_parts(built[p['kind']], p['x'], p['y'], p['yaw'], p['scale'])
    merged = {}
    for part in parts:
        key = (part.name if part.name in ('wood', 'foliage') else 'body') + (':gloss' if part.material else '')
        target = merged.setdefault(key, foliage.Part(key.replace(':', '_')))
        target.material = part.material
        target.positions += part.positions
        target.normals += part.normals
        target.colors += part.colors
    return foliage.write_glb(list(merged.values()), 'stephen_avenue_preview', GENERATOR)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build_all():
    prog = program()
    places = placements()
    modules, bounds, budget = {}, {}, []
    for kind in MODULES:
        payload, bound, triangles, meshes = module_glb(kind)
        sha = hashlib.sha256(payload).hexdigest()
        modules[kind] = dict(payload=payload, sha256=sha, bytes=len(payload))
        bounds[sha] = bound
        count = sum(p['kind'] == kind for p in places)
        budget.append(dict(kind=kind, countPer40M=count, moduleTriangles=triangles, moduleBytes=len(payload), meshes=meshes,
                           submittedTrianglesPer40M=count * triangles))
    preview, _, _, triangles, _ = assembly(prog, places)
    reference = (ROOT / REFERENCE).read_bytes()
    recipe = dict(id=STREET_ID, title=TITLE, sourceArchetypeId=PARENT, generator=GENERATOR,
                  dimensions_m=[WIDTH, CYCLE], fixed_width_m=WIDTH, fixture_length_m=CYCLE, motor_lanes=0, sections=sections(),
                  placements=places, program=prog, runtime_approved=False,
                  modules={k: dict(path=f'modules/{k}.glb', sha256=v['sha256'], bytes=v['bytes']) for k, v in modules.items()},
                  assembly=dict(path='assembly-preview.glb', sha256=hashlib.sha256(preview).hexdigest(), bytes=len(preview)),
                  triangles=triangles, budget=budget,
                  clear_routes=[dict(name='promenade', a=[0, -20], b=[0, 20], width=PROMENADE - .4)]
                  + [dict(name=f'{side}_frontage_walk', a=[sign * 6.775, -20], b=[sign * 6.775, 20], width=1.5)
                     for side, sign in (('west', -1), ('east', 1))],
                  source_notes=['The street only. Buildings, storefronts and +15 skywalks are left out; students add their own.',
                                'An original teaching section after the catalogue Stephen Avenue images, not a City of Calgary drawing.',
                                'Pedestrian mall: no motor lanes. The 8 m promenade stays clear for emergency and service access.'],
                  references=[dict(path=r, sha256=hashlib.sha256((ROOT / r).read_bytes()).hexdigest()) for r in REFERENCES])
    recipe_sha = digest({k: v for k, v in recipe.items() if k != 'assembly'})
    row = dict(id=STREET_ID, sourceArchetypeId=PARENT, title=TITLE, status='candidate',
               sourceRecipeSha256=recipe_sha, sourceAssemblySha256=recipe['assembly']['sha256'],
               referenceSha256=hashlib.sha256(reference).hexdigest(),
               widthM=WIDTH, fixtureLengthM=int(CYCLE), routeAxis='local_y', junctionSurface='pavers',
               sections=recipe['sections'], placements=places,
               modules={k: dict(sha256=v['sha256'], bytes=v['bytes'], url=f'/street-kits/pilots/{STREET_ID}/{k}.glb') for k, v in modules.items()},
               treeWells=[], thumbnailUrl=THUMBNAIL, program=prog, programSha256=digest(prog))
    return recipe, row, modules, bounds, preview


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f'{args.output} exists; a candidate is never overwritten')
    recipe, row, modules, bounds, preview = build_all()
    (args.output / 'modules').mkdir(parents=True)
    for kind, module in modules.items():
        (args.output / 'modules' / f'{kind}.glb').write_bytes(module['payload'])
    (args.output / 'assembly-preview.glb').write_bytes(preview)
    for name, value in (('recipe.json', recipe), ('row.json', row), ('module-bounds.json', bounds)):
        (args.output / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'id': STREET_ID, 'recipe': row['sourceRecipeSha256'], 'assembly': row['sourceAssemblySha256'],
                      'preview_triangles': recipe['triangles'], 'modules': {b['kind']: [b['moduleTriangles'], b['moduleBytes'], b['countPer40M']]
                                                                         for b in recipe['budget']}}))


if __name__ == '__main__':
    main()
