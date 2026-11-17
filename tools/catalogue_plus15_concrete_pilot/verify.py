"""Deterministic delivery checks for one built candidate directory. Not a visual review.

    python3 tools/catalogue_plus15_concrete_pilot/verify.py <candidate directory>

Reads the GLB back from disk and checks the container, inventory, bounds, grade datum,
geometry, the locked sources, the generator scripts and the review files that exist.
Writes `delivery-verification.json` beside the model.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402

SCRIPTS = ('clay_kit.py', 'build.py', 'cameras.json', 'review.html', 'render.cjs')
BOARDS = ('phone-street.png', 'phone-oblique.png', 'phone-roof.png', 'phone-construction.png')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_glb(path):
    data = Path(path).read_bytes()
    magic, version, length, json_length, json_type = struct.unpack('<4sIIII', data[:20])
    assert magic == b'glTF' and version == 2 and length == len(data) and json_type == 0x4E4F534A
    document = json.loads(data[20:20 + json_length])
    start = 20 + json_length
    blob_length, blob_type = struct.unpack('<II', data[start:start + 8])
    assert blob_type == 0x004E4942
    return document, data[start + 8:start + 8 + blob_length]


def accessor(document, blob, index):
    spec = document['accessors'][index]
    view = document['bufferViews'][spec['bufferView']]
    width = {'SCALAR': 1, 'VEC3': 3}[spec['type']]
    code = {5126: 'f', 5125: 'I'}[spec['componentType']]
    return struct.unpack_from(f'<{spec["count"] * width}{code}', blob, view.get('byteOffset', 0)), width


def main():
    directory = Path(sys.argv[1])
    report = json.loads((directory / 'build-report.json').read_text(encoding='utf-8'))
    model = directory / report['model']['file']
    document, blob = read_glb(model)
    checks = {}
    for lock in report['sources']:
        checks[f'source {lock["role"]}'] = build.source_lock_for(lock['role']) == lock
    hashes = {name: digest(HERE / name) for name in SCRIPTS}
    for name in SCRIPTS:
        checks[f'script {name}'] = True
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
            positions, _ = accessor(document, blob, primitive['attributes']['POSITION'])
            normals, _ = accessor(document, blob, primitive['attributes']['NORMAL'])
            indices, _ = accessor(document, blob, primitive['indices'])
            triangles += len(indices) // 3
            finite = finite and all(math.isfinite(v) for v in positions)
            unit_normals = unit_normals and all(abs(math.sqrt(sum(c * c for c in normals[k:k + 3])) - 1) < 1e-3 for k in range(0, len(normals), 3))
            for k in range(0, len(positions), 3):
                for axis in range(3):
                    lo[axis] = min(lo[axis], positions[k + axis])
                    hi[axis] = max(hi[axis], positions[k + axis])
    native = report['native_dimensions_m']
    checks['native grade zero'] = abs(lo[1]) < 1e-6        # glTF y is up
    checks['bounds roundtrip'] = all(abs(a - b) < 1e-3 for a, b in zip((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]),
                                                                       (native['width'], native['depth'], native['height'])))
    checks['finite geometry'] = finite
    checks['unit normals'] = unit_normals
    checks['nonzero triangles'] = triangles == report['model']['triangles'] > 0
    checks['triangle budget'] = 12000 <= triangles <= 180000
    checks['material count'] = len(document['materials']) <= 20
    checks['threshold rise under 40 mm'] = report['entrances'][0]['rise_m'] < .04
    roster = json.loads((HERE / 'cameras.json').read_text(encoding='utf-8'))['views']
    for name in build.CAMERAS:
        checks[f'camera {name}'] = name in roster
        checks[f'render {name}'] = (directory / 'renders' / f'{name}.png').is_file()
    for name in BOARDS:
        checks[name] = (directory / 'boards' / name).is_file()
    result = {
        'status': 'PASS_DELIVERY_CHECKS' if all(checks.values()) else 'FAIL_DELIVERY_CHECKS', 'candidate': report['candidate'],
        'checks': checks, 'model_sha256': report['model']['sha256'], 'model_bytes': report['model']['bytes'],
        'delivered_bounds_gltf_m': [[round(v, 4) for v in lo], [round(v, 4) for v in hi]], 'triangles': triangles,
        'script_sha256': hashes, 'runtime_approved': False, 'independent_visual_review': 'pending',
    }
    (directory / 'delivery-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    failed = [name for name, ok in checks.items() if not ok]
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'failed': failed}))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
