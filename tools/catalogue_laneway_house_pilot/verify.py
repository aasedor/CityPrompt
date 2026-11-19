"""Deterministic delivery checks for one built laneway-house candidate. Not a visual review.

    python3 tools/catalogue_laneway_house_pilot/verify.py <candidate directory>

Reads the GLB back from disk and checks the container, inventory, bounds, grade datum,
geometry, the locked sources, the generator scripts and the review files that exist.
Writes `delivery-verification.json` beside the model.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('laneway_build', HERE / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

KIT = HERE.parent / 'catalogue_plus15_concrete_pilot' / 'clay_kit.py'
SCRIPTS = {'clay_kit.py': KIT, **{name: HERE / name for name in ('build.py', 'cameras.json', 'review.html', 'render.cjs')}}
BOARDS = ('phone-street.png', 'phone-oblique.png', 'phone-roof.png', 'phone-construction.png')
WHOLE_VIEWS = ('front', 'front_corner', 'aerial', 'top', 'left_side', 'right_side', 'rear', 'rear_side', 'match_front', 'match_oblique')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_glb(path):
    data = Path(path).read_bytes()
    magic, version, length, json_length, json_type = struct.unpack('<4sIIII', data[:20])
    assert magic == b'glTF' and version == 2 and length == len(data) and json_type == 0x4E4F534A
    start = 20 + json_length
    blob_length, blob_type = struct.unpack('<II', data[start:start + 8])
    assert blob_type == 0x004E4942
    return json.loads(data[20:start]), data[start + 8:start + 8 + blob_length]


def accessor(document, blob, index):
    spec = document['accessors'][index]
    view = document['bufferViews'][spec['bufferView']]
    width = {'SCALAR': 1, 'VEC3': 3}[spec['type']]
    code = {5126: 'f', 5125: 'I'}[spec['componentType']]
    return struct.unpack_from(f'<{spec["count"] * width}{code}', blob, view.get('byteOffset', 0))


def outline_points():
    """The corners of everything a whole view must keep in frame: the paved apron and
    garden step at grade, the gutters at the eaves, and the ridge."""
    o = build.OVERHANG + .12
    ridge = build.FASCIA_TOP + (build.WIDTH + 2 * build.OVERHANG) / 2 * build.PITCH + .05
    points = [(x, y, 0.0) for x in (0.0, build.WIDTH) for y in (-build.PROJECT - build.APRON, build.DEPTH + .9)]
    points += [(x, y, build.FASCIA_TOP) for x in (-o, build.WIDTH + o) for y in (-o, build.DEPTH + o)]
    points += [((build.WIDTH) / 2, y, ridge) for y in (build.DEPTH / 2 - .35, build.DEPTH / 2 + .35)]
    return points


def view_extent(view):
    """Where the building falls in one camera's frame, as fractions of the half width and
    half height: (left, right, bottom, top). Beyond 1 it is out of frame."""
    def sub(a, c):
        return [a[i] - c[i] for i in range(3)]

    def cross(a, c):
        return [a[1] * c[2] - a[2] * c[1], a[2] * c[0] - a[0] * c[2], a[0] * c[1] - a[1] * c[0]]

    def dot(a, c):
        return sum(a[i] * c[i] for i in range(3))

    def unit(a):
        size = math.sqrt(dot(a, a))
        return [v / size for v in a]

    width, height = view.get('w', 1600), view.get('h', 1200)
    forward = unit(sub(view['target'], view['pos']))
    right = unit(cross(forward, view.get('up', [0, 0, 1])))
    up = cross(right, forward)
    xs, ys = [], []
    for point in outline_points():
        d = sub(point, view['pos'])
        x, y, z = dot(d, right), dot(d, up), dot(d, forward)
        if 'ortho' in view:
            xs.append(x / view['ortho'])
            ys.append(y / (view['ortho'] * height / width))
        else:
            t = math.tan(math.radians(view['fov']) / 2)
            xs.append(x / z / (t * width / height))
            ys.append(y / z / t - view.get('shift', 0))
    return min(xs), max(xs), min(ys), max(ys)


def main():
    directory = Path(sys.argv[1])
    report = json.loads((directory / 'build-report.json').read_text(encoding='utf-8'))
    model = directory / report['model']['file']
    document, blob = read_glb(model)
    checks = {f'source {lock["role"]}': build.source_lock_for(lock['role']) == lock for lock in report['sources']}
    checks.update({f'script {name}': path.is_file() for name, path in SCRIPTS.items()})
    checks['glb header'] = True
    checks['model hash'] = digest(model) == report['model']['sha256']
    checks['rebuilds to the same bytes'] = build.build().glb(build.PALETTE, {'archetype_id': build.ARCHETYPE, 'variant_id': build.VARIANT}) == model.read_bytes()
    checks['texture-free'] = not document.get('textures') and not document.get('images')
    checks['self-contained'] = len(document['buffers']) == 1 and 'uri' not in document['buffers'][0]
    checks['no QA camera or light'] = not document.get('cameras') and 'KHR_lights_punctual' not in document.get('extensionsUsed', [])
    checks['one node, mesh and material per role'] = len(document['nodes']) == len(document['meshes']) == len(document['materials'])
    checks['clay role names'] = all(node['name'].startswith('CLAY_') and node['extras']['representation_kind'] == 'architectural_clay'
                                    for node in document['nodes'])
    checks['no node transforms'] = not any(key in node for node in document['nodes'] for key in ('translation', 'rotation', 'scale', 'matrix'))
    lo, hi, triangles, finite, unit_normals = [math.inf] * 3, [-math.inf] * 3, 0, True, True
    for mesh in document['meshes']:
        for primitive in mesh['primitives']:
            positions = accessor(document, blob, primitive['attributes']['POSITION'])
            normals = accessor(document, blob, primitive['attributes']['NORMAL'])
            triangles += len(accessor(document, blob, primitive['indices'])) // 3
            finite = finite and all(math.isfinite(v) for v in positions)
            unit_normals = unit_normals and all(abs(math.sqrt(sum(c * c for c in normals[k:k + 3])) - 1) < 1e-3 for k in range(0, len(normals), 3))
            for k in range(0, len(positions), 3):
                for axis in range(3):
                    lo[axis] = min(lo[axis], positions[k + axis])
                    hi[axis] = max(hi[axis], positions[k + axis])
    native = report['native_dimensions_m']
    roster = json.loads((HERE / 'cameras.json').read_text(encoding='utf-8'))['views']
    checks['native grade zero'] = abs(lo[1]) < 1e-6        # glTF y is up
    checks['bounds roundtrip'] = all(abs(a - b) < 1e-3 for a, b in zip((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]),
                                                                       (native['width'], native['depth'], native['height'])))
    checks['finite geometry'] = finite
    checks['unit normals'] = unit_normals
    checks['nonzero triangles'] = triangles == report['model']['triangles'] > 0
    checks['triangle budget'] = 2000 <= triangles <= 180000
    checks['material count'] = len(document['materials']) <= 20
    checks['ridge under 8.5 m'] = native['height'] < 8.5
    doors = report['entrances']['doors']
    checks['one street door, one garden door, one garage door'] = sorted(d['kind'] for d in doors) == ['front door', 'garage door', 'garden door']
    checks['every door threshold at most one step above grade'] = all(d['rise_m'] <= .21 for d in doors)
    for name in WHOLE_VIEWS:
        checks[f'camera margin {name}'] = max(abs(v) for v in view_extent(roster[name])) <= .94
    for name in build.CAMERAS:
        checks[f'camera {name}'] = name in roster
        checks[f'render {name}'] = (directory / 'renders' / f'{name}.png').is_file()
    for name in BOARDS:
        checks[name] = (directory / 'boards' / name).is_file()
    result = {
        'status': 'PASS_DELIVERY_CHECKS' if all(checks.values()) else 'FAIL_DELIVERY_CHECKS', 'candidate': report['candidate'],
        'checks': checks, 'model_sha256': report['model']['sha256'], 'model_bytes': report['model']['bytes'],
        'delivered_bounds_gltf_m': [[round(v, 4) for v in lo], [round(v, 4) for v in hi]], 'triangles': triangles,
        'script_sha256': {name: digest(path) for name, path in SCRIPTS.items()}, 'runtime_approved': False, 'independent_visual_review': 'pending',
    }
    (directory / 'delivery-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    failed = [name for name, ok in checks.items() if not ok]
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'failed': failed}))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
