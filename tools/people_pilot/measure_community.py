"""Round-trip load and validate the finite20, then emit exact-byte provenance.

Blender 5.2 --background --python tools/people_pilot/measure_community.py
All outputs remain in external artifact storage; no original assets are written.
"""
import hashlib
import json
import math
from pathlib import Path
import struct

import bpy

ROOT = Path('C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters')
DESIGNS = json.loads(Path(__file__).with_name('community_designs.json').read_text())
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(design):
    path = ROOT / 'runtime' / (design['id'] + '.glb')
    raw = path.read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 8)[0] == len(raw)
    length = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20 + length])
    binary = raw[28 + length:]
    root_node = next(n for n in doc['nodes'] if n.get('name') == design['id'])
    assert root_node['extras'].get('design') == design['outfit'], 'Geometry callback was not applied'
    assert abs(root_node['scale'][0] / root_node['scale'][1] - design['body_width']) < .00001
    assert abs(root_node['scale'][2] / root_node['scale'][1] - design['body_depth']) < .00001

    def accessor(index):
        a = doc['accessors'][index]
        view = doc['bufferViews'][a['bufferView']]
        code, size = COMPONENTS[a['componentType']]
        width = WIDTHS[a['type']]
        offset = view.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = view.get('byteStride', size * width)
        return [struct.unpack_from('<' + code * width, binary, offset + i * stride) for i in range(a['count'])]

    for index in range(len(doc['accessors'])):
        assert all(math.isfinite(v) for row in accessor(index) for v in row)
    assert {a['name'] for a in doc['animations']} == {'Walk', 'Idle'}
    assert not any('uri' in b for b in doc['buffers']), 'GLB must be self-contained'
    for a in doc['animations']:
        for sampler in a['samplers']:
            times = [v[0] for v in accessor(sampler['input'])]
            assert times[0] == 0 and all(y > x for x, y in zip(times, times[1:]))
        assert all(c['target']['node'] < len(doc['nodes']) for c in a['channels'])
    bones = max(len(s['joints']) for s in doc['skins'])
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            assert {'POSITION', 'JOINTS_0', 'WEIGHTS_0'} <= p['attributes'].keys()
            assert all(abs(sum(w) - 1) < .0001 and min(w) >= 0 for w in accessor(p['attributes']['WEIGHTS_0']))
            assert all(max(j) < bones for j in accessor(p['attributes']['JOINTS_0']))
    textures = []
    for image in doc.get('images', []):
        assert 'bufferView' in image
        view = doc['bufferViews'][image['bufferView']]
        offset = view.get('byteOffset', 0)
        png = binary[offset:offset + view['byteLength']]
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack_from('>II', png, 16)
        assert max(width, height) <= 512
        textures.append({'width': width, 'height': height, 'bytes': len(png)})
    triangles = sum(doc['accessors'][p['indices']]['count'] // 3 for m in doc['meshes'] for p in m['primitives'])
    assert triangles < 20000 and len(raw) < 2 * 1024 * 1024
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 24
    bpy.ops.import_scene.gltf(filepath=str(path))
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    clips = []
    dimensions = None
    stride = None
    for action in bpy.data.actions:
        if action.name not in {'Walk', 'Idle'}:
            continue
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        samples = []
        for k in range(41):
            frame = action.frame_range[0] + (action.frame_range[1] - action.frame_range[0]) * k / 40
            scene.frame_set(int(frame), subframe=frame - int(frame))
            dg = bpy.context.evaluated_depsgraph_get()
            points, soles = [], []
            for obj in scene.objects:
                if obj.type != 'MESH' or not obj.vertex_groups:
                    continue
                evaluated = obj.evaluated_get(dg)
                mesh = evaluated.to_mesh()
                world = [evaluated.matrix_world @ v.co for v in mesh.vertices]
                points.extend(world)
                if 'sneaker' in obj.name:
                    soles.extend(world)
                evaluated.to_mesh_clear()
            low = [min(v[i] for v in points) for i in range(3)]
            high = [max(v[i] for v in points) for i in range(3)]
            samples.append({'t': frame / 24, 'min': low, 'max': high, 'soleZ': min(v.z for v in soles),
                            'ankles': {s: (rig.matrix_world @ rig.pose.bones['foot_' + s].head).y for s in ['l', 'r']}})
        assert min(s['soleZ'] for s in samples) >= -.0025
        assert max(s['soleZ'] for s in samples) <= .008
        if action.name == 'Idle':
            first = samples[0]
            dimensions = [first['max'][i] - first['min'][i] for i in range(3)]
            assert 1.58 < dimensions[2] < 1.96
        else:
            stride = sum(max(s['ankles'][side] for s in samples) - min(s['ankles'][side] for s in samples) for side in ['l', 'r'])
        clips.append({'name': action.name, 'duration': float(action.frame_range[1] / 24), 'sampleCount': 41,
                      'soleYMin': min(s['soleZ'] for s in samples), 'soleYMax': max(s['soleZ'] for s in samples), 'samples': samples})
    decoded = sum(a['count'] * WIDTHS[a['type']] * COMPONENTS[a['componentType']][1] for a in doc['accessors'])
    return {'id': design['id'], 'design': design, 'sha256': sha(path), 'bytes': len(raw), 'triangles': triangles,
            'bones': bones, 'meshPrimitives': sum(len(m['primitives']) for m in doc['meshes']), 'materials': len(doc['materials']),
            'textures': textures, 'decodedAccessorBytes': decoded,
            'estimatedDecodedBytes': decoded + sum(math.ceil(t['width'] * t['height'] * 4 * 4 / 3) for t in textures) + bones * 64,
            'dimensions': dimensions, 'walkStrideMeters': stride, 'clips': clips, 'thumbnailSha256': sha(ROOT / 'qa' / (design['id'] + '.png'))}


if __name__ == '__main__':
    assert {p.stem for p in (ROOT / 'runtime').glob('*.glb')} == {d['id'] for d in DESIGNS}
    actors = []
    for design in DESIGNS:
        actor = measure(design)
        actors.append(actor)
        print('PASS', actor['id'], actor['bytes'], actor['triangles'], actor['dimensions'], flush=True)
    source = json.loads(Path(__file__).with_name('character_provenance.json').read_text())
    for entry in source['sources']:
        assert sha(Path(entry['archiveFile'])) == entry['archiveSha256']
        assert sha(Path(entry['licenseFile'])) == entry['licenseSha256']
    originals = []
    for actor in source['actors']:
        assert sha(Path(actor['artifactFile'])) == actor['sha256']
        originals.append({'id': actor['id'], 'sha256': actor['sha256'], 'bytes': actor['byteSize']})
    scripts = ['build_characters.py', 'build_community.py', 'community_shapes.py', 'community_designs.json',
               'measure_community.py', 'render_community_views.py', 'promote_community.py']
    manifest = {'schemaVersion': 1, 'initiative': 'people-actions-2026-10-22', 'localOnly': True,
                'coordinates': {'unit': 'metre', 'up': '+Y', 'forward': '+Z', 'feetY': 0}, 'sources': source['sources'],
                'immutableOriginalsVerified': originals,
                'buildFiles': [{'path': 'tools/people_pilot/' + name, 'sha256': sha(Path(__file__).with_name(name))} for name in scripts],
                'authorship': 'CC0 Quaternius adult anatomy/hair/motion; derived garment topology, fitted/tapered silhouettes, shoulder closures, face-width variations, palette and measured foot grounding.',
                'limitations': ['Stylized low polygon faces; two source adult anatomical bases, not twenty independently sculpted anatomies.',
                                'Long sleeves and full trousers throughout; garments vary in fit, collar, hem and coat silhouette.',
                                'Approximate ankle-range walk calibration; no cloth simulation or pathfinding.',
                                'Decoded costs exclude renderer overhead, GPU allocator overhead and browser caches.',
                                'Walk/Idle grounding sampled at 41 times each. Procedural action pose QA is a separate runtime gate.'],
                'actors': actors}
    (ROOT / 'measurements.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('PASS finite20: 1,640 evaluated frame samples; original source archive/license hashes matched', flush=True)
