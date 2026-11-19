"""Offline geometry checks for one built stormwater pond package.

Reads the exact assembly GLB the package holds, never the generator's memory of it,
and writes geometry-verification.json beside it. Usage:
  python3 tools/stormwater_pond_park/verify.py <package directory>
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stormwater_pond_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

WALK = {'paving', 'grass', 'deck'}
CLEARANCE = {'foliage': .35, 'wood': .35, 'fauna': .6}   # a plant or bird's own footprint, metres from its origin


def read_glb(data):
    magic, version, length = struct.unpack_from('<4sII', data)
    assert magic == b'glTF' and version == 2 and length == len(data)
    json_length = struct.unpack_from('<I', data, 12)[0]
    document = json.loads(data[20:20 + json_length])
    binary = data[28 + json_length:]
    return document, binary


def accessor(document, binary, index):
    a = document['accessors'][index]
    view = document['bufferViews'][a['bufferView']]
    dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2'}[a['componentType']]
    width = {'VEC3': 3, 'SCALAR': 1}[a['type']]
    out = np.frombuffer(binary, dtype=dtype, count=a['count'] * width, offset=view['byteOffset'] + a.get('byteOffset', 0))
    return out.reshape(-1, width) if width > 1 else out


def world_triangles(document, binary):
    """Every triangle in the authoring frame (x east, y north, z up), with its material name."""
    out = []
    names = [m['name'] for m in document['materials']]
    for node in document['nodes']:
        mesh = document['meshes'][node['mesh']]
        for prim in mesh['primitives']:
            p = accessor(document, binary, prim['attributes']['POSITION']).astype(float)
            idx = accessor(document, binary, prim['indices']).reshape(-1, 3)
            s = node.get('scale', [1, 1, 1])[0]
            q = node.get('rotation', [0, 0, 0, 1])
            yaw = 2 * math.atan2(q[1], q[3])
            t = node.get('translation', [0, 0, 0])
            x, y, z = p[:, 0] * s, -p[:, 2] * s, p[:, 1] * s
            c, sn = math.cos(yaw), math.sin(yaw)
            world = np.stack([x * c - y * sn + t[0], x * sn + y * c - t[2], z + t[1]], axis=1)
            out.append((names[prim['material']], world[idx], node['name'], (t[0], -t[2])))
    return out


def height_under(tris, x, y):
    """Highest surface among `tris` (n, 3, 3) above plan point (x, y), or None."""
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    d = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(d) > 1e-12
    u = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / np.where(ok, d, 1)
    v = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / np.where(ok, d, 1)
    inside = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
    if not inside.any():
        return None
    z = u * a[:, 2] + v * b[:, 2] + (1 - u - v) * c[:, 2]
    return float(z[inside].max())


def main(directory):
    directory = Path(directory)
    recipe = json.loads((directory / 'recipe.json').read_text(encoding='utf-8'))
    data = (directory / recipe['assembly']['path']).read_bytes()
    checks, failures = [], []

    def check(ok, label):
        (checks if ok else failures).append(label)

    check(hashlib.sha256(data).hexdigest() == recipe['assembly']['sha256'] and len(data) == recipe['assembly']['bytes'], 'delivered byte hashes')
    document, binary = read_glb(data)
    check(not any('uri' in item for item in document.get('buffers', []) + document.get('images', [])), 'self-contained GLB buffers')
    check('textures' not in document and 'images' not in document, 'no textures or images')
    names = {m['name'] for m in document['materials']}
    check({'paving', 'grass', 'deck', 'water'} <= names, 'runtime material names present')
    tris = world_triangles(document, binary)
    every = np.concatenate([t for _, t, _, _ in tris])
    lo, hi = every.reshape(-1, 3).min(axis=0), every.reshape(-1, 3).max(axis=0)
    check(np.isfinite(every).all(), 'finite metric bounds')
    hx, hy = build.SITE_W / 2, build.SITE_D / 2
    check(lo[0] >= -hx - 1e-3 and hi[0] <= hx + 1e-3 and lo[1] >= -hy - 1e-3 and hi[1] <= hy + 1e-3, f'inside the {build.SITE_W:g} x {build.SITE_D:g} m footprint')
    check(all(abs(a - b) < 2e-3 for a, b in zip(list(lo) + list(hi), recipe['bounds_m'][0] + recipe['bounds_m'][1])), 'recipe bounds match the GLB')
    check(lo[2] >= -1.0 and hi[2] < 20, 'below grade only where the pond is, and nothing towers')
    water = np.concatenate([t for n, t, _, _ in tris if n == 'water'])
    check(np.allclose(water[:, :, 2], build.WATER_Z, atol=1e-4), f'water is one plane {abs(build.WATER_Z):.2f} m below grade')
    walk = np.concatenate([t for n, t, _, _ in tris if n in WALK])
    # every clear route is walkable along its whole width, at a gentle height
    rays = 0
    for route in recipe['clear_routes']:
        (ax, ay), (bx, by), width = route['a'], route['b'], route['width']
        length = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / length, (by - ay) / length
        for k in range(int(length / .5) + 1):
            s = min(length, k * .5)
            for o in (-.45, 0, .45):
                x, y = ax + ux * s - uy * o * width, ay + uy * s + ux * o * width
                z = height_under(walk, x, y)
                rays += 1
                if z is None or not -.05 <= z <= .25:
                    failures.append(f'route gap at ({x:.2f}, {y:.2f}): {z}')
    check(True, f'{rays} material-aware route rays on paving, grass and deck')
    # no plant, bird or fixture stands on a clear route
    segments = [(r['a'], r['b'], r['width']) for r in recipe['clear_routes']]

    def distance_to_routes(x, y):
        best = math.inf
        for (ax, ay), (bx, by), width in segments:
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy) - width / 2)
        return best
    placed = {}
    for material, _, node, origin in tris:
        if material in CLEARANCE and node not in placed:
            placed[node] = (origin, CLEARANCE[material])
    blocked = [(node, round(distance_to_routes(*origin), 2)) for node, (origin, radius) in placed.items()
               if distance_to_routes(*origin) < radius]
    check(not blocked, f'{len(placed)} planted and wildlife instances clear of every route')
    failures.extend(f'on a route: {node} {gap}' for node, gap in blocked)
    entrance = height_under(walk, 0.0, -hy + .2)
    check(entrance is not None and abs(entrance - (build.PAVE_Z - .005)) < .01, 'entrance spur paved at the south edge')
    report = {'status': 'PASS_OFFLINE_GEOMETRY' if not failures else 'FAIL_OFFLINE_GEOMETRY', 'model_sha256': recipe['assembly']['sha256'],
              'checks': checks, 'failures': failures[:40], 'triangles_rendered': recipe['triangles'], 'mesh_instances': recipe['mesh_instances'],
              'runtime_tested': False}
    (directory / 'geometry-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'failures': len(failures)}))
    return report


if __name__ == '__main__':
    main(sys.argv[1])
