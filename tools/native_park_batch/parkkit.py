"""Shared drawing kit for native park assemblies, in pure Python.

The park runtime reads one self-contained GLB per park. Each material is one mesh
named for the runtime: `paving`, `grass` and `gravel` are walkable where a park
says so, `water` is a hazard, and plants never form walls. Repeated plants and
furniture are one mesh placed by many nodes.

Ground is laid as real polygons (shapely), cut into small cells so colour mottle
reads as patches, and triangulated with earcut. Sculpted ground such as skate
bowls is a dense Delaunay heightfield with smooth normals.
Adapted from tools/stormwater_pond_park/build.py.
"""
from __future__ import annotations

import json
import math
import random
import struct
import sys
from pathlib import Path

import mapbox_earcut
import numpy as np
import shapely
from scipy.spatial import Delaunay
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'detail_catalogue'))
import build_local_foliage as foliage  # noqa: E402
from calgary_kit import Solid  # noqa: E402

MATERIALS = {
    'grass': dict(roughness=.95), 'paving': dict(roughness=.9), 'gravel': dict(roughness=.97), 'mud': dict(roughness=.8),
    'water': dict(roughness=.55), 'deck': dict(roughness=.82), 'timber': dict(roughness=.82), 'concrete': dict(roughness=.85),
    'rock': dict(roughness=.95), 'metal': dict(roughness=.5, metallic=.3), 'furniture': dict(roughness=.7),
    'foliage': dict(roughness=.9), 'wood': dict(roughness=.92), 'rubber': dict(roughness=.95),
}

SURFACES = {   # (low, high) sRGB, blended per vertex by a smooth mottle
    'lawn': ('#5e7a37', '#6f8c41'), 'meadow': ('#5a6b34', '#71813f'), 'berm': ('#5d7537', '#6c8440'),
    'gravel': ('#a39a86', '#b5ac97'), 'deck': ('#bdb9b0', '#c9c5bc'), 'bowl': ('#a9aba8', '#b8b9b5'),
    'plaza': ('#b5b2ab', '#c3c0b8'), 'mulch': ('#5a4433', '#6c5240'), 'bed': ('#434f2b', '#556236'),
    'asphalt': ('#5d5f5e', '#6c6d6a'), 'rubber': ('#3f6f8a', '#4a7d98'), 'rubber_red': ('#8a4436', '#9b4e3f'),
    'stone': ('#b9b1a2', '#c7bfb0'), 'water': ('#3c5f6e', '#456c7c'), 'hedge_floor': ('#3e4a2c', '#485535'),
}


def linear(hex_colour):
    return foliage.srgb_to_linear(hex_colour)


def mottle(x, y, seed=0.0):
    """Smooth value in 0..1 from position: gentle patches, never stripes."""
    v = (math.sin(.37 * x + 1.3 + seed) * math.sin(.29 * y - .7 + seed) * .45 + math.sin(.11 * x - .13 * y + seed) * .3
         + math.sin(1.07 * x + .61 * y + 2 * seed) * .15 + math.sin(2.3 * x - 1.7 * y + seed) * .1)
    return .5 + .5 * max(-1.0, min(1.0, v))


def shade(surface, x, y):
    low, high = (linear(c) for c in SURFACES[surface])
    m = mottle(x, y, len(surface) * .7)
    return tuple(lo + (hi - lo) * m for lo, hi in zip(low, high))


class Parts:
    """A Solid per material, all drawn in the park frame (x east, y north, z up)."""

    def __init__(self, seed):
        self.solids = {name: Solid(seed + k) for k, name in enumerate(MATERIALS)}

    def __getitem__(self, name):
        return self.solids[name]


def ground_tri(part, a, b, c, colours, normals=None):
    """One triangle wound to face up, with a colour (and optionally a normal) at each corner."""
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    if nz < 0:
        b, c, colours = c, b, (colours[0], colours[2], colours[1])
        if normals:
            normals = (normals[0], normals[2], normals[1])
        nx, ny, nz = -nx, -ny, -nz
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-12:
        return
    part.positions.extend((*a, *b, *c))
    if normals:
        for n in normals:
            part.normals.extend(n)
    else:
        part.normals.extend((nx / length, ny / length, nz / length) * 3)
    for colour in colours:
        part.colors.extend(colour)


def polygons(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry]
    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)
    return [g for g in getattr(geometry, 'geoms', []) if isinstance(g, Polygon) and not g.is_empty]


def triangulate(polygon):
    """Earcut triangles of a polygon with holes, as lists of (x, y)."""
    rings = [list(polygon.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in polygon.interiors]
    rings = [r for r in rings if len(r) >= 3]
    if not rings:
        return []
    vertices = np.array([p for r in rings for p in r], dtype=np.float64)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    idx = mapbox_earcut.triangulate_float64(vertices, ends)
    return [tuple(tuple(vertices[i]) for i in idx[k:k + 3]) for k in range(0, len(idx), 3)]


def fill(part, surface, region, z=0.0, cell=2.0):
    """Lay a flat polygonal region at height z, cut into cells so its mottle reads as patches."""
    region = shapely.make_valid(region)
    if region.is_empty:
        return
    minx, miny, maxx, maxy = region.bounds
    boxes = [box(i * cell, j * cell, (i + 1) * cell, (j + 1) * cell)
             for i in range(math.floor(minx / cell), math.ceil(maxx / cell))
             for j in range(math.floor(miny / cell), math.ceil(maxy / cell))]
    for piece in shapely.intersection(region, np.array(boxes, dtype=object)):
        for poly in polygons(piece):
            if poly.area < 1e-6:
                continue
            for tri in triangulate(poly):
                pts = [(x, y, z) for x, y in tri]
                ground_tri(part, *pts, [shade(surface, x, y) for x, y, _ in pts])


def sample_ring(ring, step):
    coords = list(ring.coords)
    out = []
    for (ax, ay), (bx, by) in zip(coords, coords[1:]):
        n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
    return out


def heightfield(part, surface, region, zfun, spacing=.3, rings=(), ring_step=.25):
    """A sculpted surface over `region`: dense Delaunay points, height from zfun(points),
    smooth normals. Boundary and offset rings keep curves and transitions crisp."""
    pts = []
    for poly in polygons(region):
        for ring in [poly.exterior, *poly.interiors]:
            pts += sample_ring(ring, ring_step * .8)
    for d in rings:
        for poly in polygons(region.buffer(-d)):
            for ring in [poly.exterior, *poly.interiors]:
                pts += sample_ring(ring, ring_step)
    minx, miny, maxx, maxy = region.bounds
    xs, ys = np.meshgrid(np.arange(minx, maxx, spacing), np.arange(miny, maxy, spacing))
    grid = np.stack([xs.ravel(), ys.ravel()], axis=1)
    inner = region.buffer(-(max(rings) + .2) if rings else -.2)
    grid = grid[shapely.contains_xy(inner, grid[:, 0], grid[:, 1])]
    pts = np.unique(np.round(np.vstack([np.array(pts), grid]), 4), axis=0)
    tri = Delaunay(pts)
    simplices = tri.simplices
    centroids = pts[simplices].mean(axis=1)
    keep = shapely.contains_xy(region.buffer(1e-6), centroids[:, 0], centroids[:, 1])
    simplices = simplices[keep]
    z = zfun(pts)
    p3 = np.column_stack([pts, z])
    # smooth normals: area-weighted face normals summed at shared vertices
    a, b, c = p3[simplices[:, 0]], p3[simplices[:, 1]], p3[simplices[:, 2]]
    fn = np.cross(b - a, c - a)
    fn[fn[:, 2] < 0] *= -1
    vn = np.zeros_like(p3)
    for k in range(3):
        np.add.at(vn, simplices[:, k], fn)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
    for s in simplices:
        corners = [tuple(p3[i]) for i in s]
        ground_tri(part, *corners, [shade(surface, p[0], p[1]) for p in corners], [tuple(vn[i]) for i in s])
    return len(simplices)


def extrude(solid, colour, polygon, z0, z1, top_colour=None, gloss=False):
    """A vertical prism over a polygon (with holes): outward-facing walls and an earcut top."""
    for poly in polygons(polygon):
        poly = shapely.geometry.polygon.orient(poly, 1.0)
        for ring in [poly.exterior, *poly.interiors]:
            coords = list(ring.coords)
            for (ax, ay), (bx, by) in zip(coords, coords[1:]):
                solid.quad((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1), colour, gloss)
        for tri in triangulate(poly):
            _tri_up(solid, [(x, y, z1) for x, y in tri], top_colour or colour, gloss)


def _tri_up(solid, pts, colour, gloss=False):
    a, b, c = pts
    if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0:
        b, c = c, b
    solid.tri(a, b, c, colour, gloss)


def tube(solid, points, radius, colour, sides=6, closed=False):
    """A pipe through a sequence of 3D points."""
    seq = list(points) + ([points[0]] if closed else [])
    for a, b in zip(seq, seq[1:]):
        if math.dist(a, b) > 1e-6:
            solid.cyl(a, b, radius, colour, sides=sides, cap0=False, cap1=False)


class Instances:
    """Meshes drawn once and placed many times."""

    def __init__(self):
        self.meshes = {}
        self.places = []

    def add_plant(self, slug, **params):
        key = slug + ('' if not params else '-' + '-'.join(f'{k}{v}' for k, v in sorted(params.items())))
        if f'{key}-foliage' in self.meshes or f'{key}-wood' in self.meshes:
            return key
        import copy
        species = copy.deepcopy(next(s for s in foliage.SPECIES if s['slug'] == slug and not s.get('season')))
        species['params'].update(params)
        plant = foliage.build(species)
        self.meshes[f'{key}-wood'] = ('wood', plant.wood)
        self.meshes[f'{key}-foliage'] = ('foliage', plant.foliage)
        return key

    def plant(self, slug, x, y, z=0.0, yaw=0.0, scale=1.0, **params):
        key = self.add_plant(slug, **params)
        for part in ('wood', 'foliage'):
            if self.meshes[f'{key}-{part}'][1].positions:
                self.places.append((f'{key}-{part}', x, y, z, yaw, scale))

    def solid(self, name, solid, material):
        self.meshes[name] = (material, solid.body)

    def place(self, name, x, y, z=0.0, yaw=0.0, scale=1.0):
        self.places.append((name, x, y, z, yaw, scale))


def mesh_arrays(part):
    """Indexed positions, normals and colours, Y up. Corners that share all three are merged."""
    p = np.array(part.positions, dtype='<f4').reshape(-1, 3)
    n = np.array(part.normals, dtype='<f4').reshape(-1, 3)
    c = np.array(part.colors, dtype='<f4').reshape(-1, 3)
    p = np.stack([p[:, 0], p[:, 2], -p[:, 1]], axis=1).astype('<f4')
    n = np.stack([n[:, 0], n[:, 2], -n[:, 1]], axis=1).astype('<f4')
    key = np.concatenate([np.round(p, 4), np.round(n, 3), np.round(c, 4)], axis=1)
    unique, inverse = np.unique(key, axis=0, return_inverse=True)
    positions = np.ascontiguousarray(unique[:, :3].astype('<f4'))
    normals = unique[:, 3:6]
    normals = np.ascontiguousarray((normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)).astype('<f4'))
    colours = np.ascontiguousarray(unique[:, 6:].astype('<f4'))
    return positions, normals, colours, inverse.reshape(-1).astype('<u4')


def write_glb(meshes, nodes, generator, scene_name):
    """meshes: [(name, material, part)]; nodes: [(mesh index, translation, yaw, scale, name)]."""
    doc = {'asset': {'generator': generator, 'version': '2.0'}, 'scene': 0, 'scenes': [{'name': scene_name, 'nodes': []}],
           'nodes': [], 'meshes': [], 'materials': [], 'accessors': [], 'bufferViews': [], 'buffers': []}
    order = list(MATERIALS)
    for name in order:
        spec = MATERIALS[name]
        doc['materials'].append({'name': name, 'doubleSided': True,
                                 'pbrMetallicRoughness': {'metallicFactor': spec.get('metallic', 0.0), 'roughnessFactor': spec['roughness']}})
    binary = bytearray()

    def view(data, target):
        binary.extend(b'\0' * (-len(binary) % 4))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(data), 'target': target})
        binary.extend(data)
        return len(doc['bufferViews']) - 1

    mesh_triangles = []
    for name, material, part in meshes:
        positions, normals, colours, indices = mesh_arrays(part)
        first = len(doc['accessors'])
        doc['accessors'].append({'bufferView': view(positions.tobytes(), 34962), 'componentType': 5126, 'count': len(positions), 'type': 'VEC3',
                                 'min': [float(v) for v in positions.min(axis=0)], 'max': [float(v) for v in positions.max(axis=0)]})
        doc['accessors'].append({'bufferView': view(normals.tobytes(), 34962), 'componentType': 5126, 'count': len(normals), 'type': 'VEC3'})
        doc['accessors'].append({'bufferView': view(colours.tobytes(), 34962), 'componentType': 5126, 'count': len(colours), 'type': 'VEC3'})
        doc['accessors'].append({'bufferView': view(indices.tobytes(), 34963), 'componentType': 5125, 'count': len(indices), 'type': 'SCALAR'})
        doc['meshes'].append({'name': name, 'primitives': [{'attributes': {'POSITION': first, 'NORMAL': first + 1, 'COLOR_0': first + 2},
                                                            'indices': first + 3, 'material': order.index(material)}]})
        mesh_triangles.append(len(indices) // 3)
    rendered = 0
    for mesh, translation, yaw, scale, name in nodes:
        node = {'name': name, 'mesh': mesh}
        if any(translation):
            node['translation'] = [float(translation[0]), float(translation[2]), float(-translation[1])]
        if yaw:
            node['rotation'] = [0.0, math.sin(yaw / 2), 0.0, math.cos(yaw / 2)]
        if scale != 1:
            node['scale'] = [float(scale)] * 3
        doc['nodes'].append(node)
        doc['scenes'][0]['nodes'].append(len(doc['nodes']) - 1)
        rendered += mesh_triangles[mesh]
    binary.extend(b'\0' * (-len(binary) % 4))
    doc['buffers'].append({'byteLength': len(binary)})
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    payload = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary)) + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
               + struct.pack('<II', len(binary), 0x004E4942) + binary)
    return payload, rendered, len(doc['nodes'])


def assemble(parts, inst, prefix):
    meshes, nodes = [], []
    for name in MATERIALS:
        part = parts[name].body
        if part.positions:
            meshes.append((f'{prefix}_{name}', name, part))
            nodes.append((len(meshes) - 1, (0.0, 0.0, 0.0), 0.0, 1.0, f'{prefix}_{name}'))
        gloss = parts[name].gloss
        if gloss.positions:
            meshes.append((f'{prefix}_{name}_gloss', name, gloss))
            nodes.append((len(meshes) - 1, (0.0, 0.0, 0.0), 0.0, 1.0, f'{prefix}_{name}_gloss'))
    index = {}
    for name, (material, part) in inst.meshes.items():
        if part.positions:
            index[name] = len(meshes)
            meshes.append((name, material, part))
    for k, (name, x, y, z, yaw, scale) in enumerate(inst.places):
        nodes.append((index[name], (x, y, z), yaw, scale, f'{name}-{k}'))
    return meshes, nodes


def bounds(meshes, nodes):
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    cache = {}
    for mesh, (tx, ty, tz), yaw, scale, _ in nodes:
        if mesh not in cache:
            cache[mesh] = np.array(meshes[mesh][2].positions).reshape(-1, 3)
        p = cache[mesh] * scale
        c, s = math.cos(yaw), math.sin(yaw)
        x, y = p[:, 0] * c - p[:, 1] * s, p[:, 0] * s + p[:, 1] * c
        q = np.stack([x + tx, y + ty, p[:, 2] + tz], axis=1)
        lo, hi = np.minimum(lo, q.min(axis=0)), np.maximum(hi, q.max(axis=0))
    return lo, hi


def route_segments(line, width, tolerance=.04):
    """A path centre line as the longest straight chords that stay within `tolerance` of it."""
    fine = [line.interpolate(d).coords[0] for d in np.arange(0, line.length, .1)] + [line.coords[-1]]
    points, start = [fine[0]], 0
    for i in range(2, len(fine)):
        a, b = np.array(fine[start]), np.array(fine[i])
        length = np.linalg.norm(b - a)
        if length < 1e-9:
            continue
        mid = np.array(fine[start + 1:i])
        sag = np.abs((b[0] - a[0]) * (mid[:, 1] - a[1]) - (b[1] - a[1]) * (mid[:, 0] - a[0])) / length
        if sag.max() > tolerance:
            points.append(fine[i - 1])
            start = i - 1
    points.append(fine[-1])
    return [dict(a=[round(a[0], 3), round(a[1], 3)], b=[round(b[0], 3), round(b[1], 3)], width=width)
            for a, b in zip(points, points[1:]) if math.dist(a, b) > .05]


# ---- furniture ---------------------------------------------------------------------------------
BLACK, STEEL, GALV, WOOD = '#25282b', '#6f777b', '#9aa0a3', '#8a6a48'


def bench(solid, x, y, yaw, length=1.8):
    """A backed bench facing local +x before `yaw`."""
    with solid.at(x, y, 0, yaw):
        for dy in (-length / 2 + .08, length / 2 - .08):
            solid.box((0, dy, .22), (.5, .07, .44), BLACK)
            solid.box((-.22, dy, .62), (.06, .07, .4), BLACK)
        for k in range(4):
            solid.box((.18 - k * .12, 0, .45), (.1, length - .08, .035), WOOD)
        for k in range(3):
            solid.box((-.25, 0, .55 + k * .12), (.035, length - .08, .09), WOOD)


def waste_bin(solid, x, y):
    solid.cyl((x, y, 0), (x, y, .05), .3, BLACK, sides=12)
    solid.cyl((x, y, .05), (x, y, .9), .27, '#4f5a52', sides=12)
    solid.dome((x, y, .9), (.27, .27, .12), '#3a443d', nu=12, nv=3)


def light_pole(solid, x, y, height=5.5):
    solid.box((x, y, .1), (.32, .32, .2), '#b2aea6')
    solid.cyl((x, y, .2), (x, y, height), .07, '#3a3f43', r1=.05, sides=8)
    solid.box((x, y, height + .05), (.55, .22, .1), '#3a3f43')
    solid.box((x, y, height - .005), (.45, .16, .02), '#f2eedb', gloss=True)


def bike_rack(solid, x, y, yaw, loops=3):
    with solid.at(x, y, 0, yaw):
        for k in range(loops):
            dx = (k - (loops - 1) / 2) * .8
            pts = [(dx, -.35, 0), (dx, -.35, .72)] + [(dx, -.35 + .35 * (1 - math.cos(a)), .72 + .2 * math.sin(a)) for a in np.linspace(0, math.pi, 7)[1:]] + [(dx, .35, 0)]
            tube(solid, pts, .025, GALV, sides=6)


def drinking_fountain(solid, x, y, yaw):
    with solid.at(x, y, 0, yaw):
        solid.box((0, 0, .45), (.4, .4, .9), '#6b7377')
        solid.box((.05, 0, .93), (.5, .45, .06), '#8a9296')
        solid.cyl((.15, 0, .96), (.15, 0, 1.0), .05, GALV, sides=6)


def sign_board(solid, x, y, yaw, colour='#2f5a3b'):
    """A blank park sign on two posts, its face toward local -y."""
    with solid.at(x, y, 0, yaw):
        for dx in (-.55, .55):
            solid.box((dx, 0, .7), (.08, .08, 1.4), BLACK)
        solid.box((0, 0, 1.15), (1.3, .06, .6), colour)
        solid.box((0, -.032, 1.15), (1.1, .004, .42), '#e8e2cf')


def smooth(geometry, r):
    """Round convex and concave corners alike."""
    return geometry.buffer(r, quad_segs=12).buffer(-2 * r, quad_segs=12).buffer(r, quad_segs=12)


__all__ = ['LineString', 'Point', 'Polygon', 'box', 'shapely', 'Solid', 'foliage']


# ---- layout helpers shared by the batch ------------------------------------------------------
def chaikin(points, rounds=3):
    """Corner-cutting smoothing of an open polyline (repeat the first point to close it)."""
    for _ in range(rounds):
        out = [points[0]]
        for a, b in zip(points, points[1:]):
            out += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        out.append(points[-1])
        points = out
    return points


def scatter(region, spacing, rng, clearance=None):
    """Jittered grid points inside `region`, avoiding `clearance`."""
    minx, miny, maxx, maxy = region.bounds
    out = []
    for x in np.arange(minx, maxx, spacing):
        for y in np.arange(miny, maxy, spacing):
            px, py = x + rng.uniform(-.4, .4) * spacing, y + rng.uniform(-.4, .4) * spacing
            if region.contains(Point(px, py)) and (clearance is None or not clearance.contains(Point(px, py))):
                out.append((px, py))
    return out


def ellipse(cx, cy, a, b, angle=0.0, n=64):
    c, s = math.cos(angle), math.sin(angle)
    return Polygon([(cx + a * math.cos(t) * c - b * math.sin(t) * s, cy + a * math.cos(t) * s + b * math.sin(t) * c)
                    for t in np.linspace(0, math.tau, n, endpoint=False)])


def mound(centre, radius, height):
    """A smooth grassy mound: z(points) peaking at `height` in the middle, zero at `radius`."""
    cx, cy = centre

    def z(pts):
        r = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) / radius
        t = np.clip(1 - r, 0, 1)
        return height * (3 * t ** 2 - 2 * t ** 3)
    return z
