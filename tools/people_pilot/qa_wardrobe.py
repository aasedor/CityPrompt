"""Round-trip finite wardrobe GLBs, measure motion, render review evidence.

This is structural/contact QA, not automatic approval of visual fidelity.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wardrobe as wardrobe
from wardrobe_rules import PILOT_IDS, WARDROBES


def evaluated_points(obj, dg):
    ev = obj.evaluated_get(dg)
    mesh = ev.to_mesh()
    coordinates = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', coordinates)
    matrix = np.asarray(ev.matrix_world, dtype=np.float64)
    points = coordinates.reshape((-1, 3)) @ matrix[:3, :3].T + matrix[:3, 3]
    ev.to_mesh_clear()
    return points


def measure(root, identity, render=False):
    path = root / 'runtime' / (identity + '.glb')
    raw = path.read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20 + length])
    binary = raw[28 + length:]
    widths = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
    components = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
    def values(index):
        a = doc['accessors'][index]
        view = doc['bufferViews'][a['bufferView']]
        code, size = components[a['componentType']]
        width = widths[a['type']]
        offset = view.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = view.get('byteStride', width * size)
        return [struct.unpack_from('<' + code * width, binary, offset + stride * i) for i in range(a['count'])]
    for index in range(len(doc['accessors'])):
        assert all(math.isfinite(v) for row in values(index) for v in row)
    assert {a['name'] for a in doc['animations']} == {'Walk', 'Idle'}
    bones = max(len(s['joints']) for s in doc['skins'])
    assert bones == 65
    names = {n.get('name', '') for n in doc['nodes']}
    assert {'Low_top_sneaker_l', 'Low_top_sneaker_r'} <= names
    assert not any(any(bad in n for bad in ['Hip_length_overshirt', 'Relaxed_sleeve', 'Closed_shoulder_yoke']) for n in names)
    assert all('uri' not in b for b in doc['buffers'])
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            assert {'POSITION', 'JOINTS_0', 'WEIGHTS_0'} <= primitive['attributes'].keys()
            assert all(abs(sum(w) - 1) < .0001 and min(w) >= 0 for w in values(primitive['attributes']['WEIGHTS_0']))
            assert all(max(j) < bones for j in values(primitive['attributes']['JOINTS_0']))
    textures = []
    for image in doc.get('images', []):
        assert 'bufferView' in image
        view = doc['bufferViews'][image['bufferView']]
        offset = view.get('byteOffset', 0)
        data = binary[offset:offset + view['byteLength']]
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack_from('>II', data, 16)
        assert max(width, height) <= 512
        textures.append(dict(width=width, height=height, bytes=len(data)))
    triangles = sum(doc['accessors'][p['indices']]['count'] // 3 for m in doc['meshes'] for p in m['primitives'])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 8
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    # Blender creates an unweighted Icosphere as an armature display shape on
    # import; it is not a GLB node and must never enter actor bounds or renders.
    meshes = [o for o in scene.objects if o.type == 'MESH' and o.vertex_groups]
    for obj in list(scene.objects):
        if obj.type == 'MESH' and not obj.vertex_groups:
            bpy.data.objects.remove(obj, do_unlink=True)
    actions = {}
    for action in bpy.data.actions:
        for name in ['Idle', 'Walk']:
            if action.name == name or action.name.startswith(name + '_'):
                actions[name] = action
    assert actions.keys() >= {'Walk', 'Idle'}, str(list(bpy.data.actions.keys()))
    clips = []
    for name, action in actions.items():
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        samples = []
        for k in range(41):
            frame = action.frame_range[0] + (action.frame_range[1] - action.frame_range[0]) * k / 40
            scene.frame_set(math.floor(frame), subframe=frame % 1)
            dg = bpy.context.evaluated_depsgraph_get()
            by_object = {obj.name: evaluated_points(obj, dg) for obj in meshes}
            points = np.concatenate(list(by_object.values()))
            soles = np.concatenate([by_object[name] for name in ['Low_top_sneaker_l', 'Low_top_sneaker_r']])
            assert np.isfinite(points).all()
            samples.append(dict(frame=frame, min=points.min(axis=0).tolist(),
                                max=points.max(axis=0).tolist(), soleZ=float(soles[:, 2].min()),
                                ankles={side: (rig.matrix_world @ rig.pose.bones['foot_' + side].head).y for side in ['l', 'r']}))
        low, high = min(s['soleZ'] for s in samples), max(s['soleZ'] for s in samples)
        assert low >= -.0025 and high <= .008, (identity, name, low, high)
        clips.append(dict(name=name, duration=(action.frame_range[1] - action.frame_range[0]) / 24,
                          framesMeasured=41, soleZMin=low, soleZMax=high, samples=samples))
    result = dict(id=identity, sha256=wardrobe.sha(path), bytes=len(raw), triangles=triangles,
                  bones=bones, materials=len(doc['materials']), meshPrimitives=sum(len(m['primitives']) for m in doc['meshes']),
                  geometries=len(doc['meshes']), textures=textures,
                  vertices=sum(doc['accessors'][p['attributes']['POSITION']]['count'] for m in doc['meshes'] for p in m['primitives']),
                  topology='original continuous skin retained beneath clothing; original weighted shoulder topology', clips=clips)
    idle0 = next(c for c in clips if c['name'] == 'Idle')['samples'][0]
    result['idle0Bounds'] = dict(min=idle0['min'], max=idle0['max'])
    result['dimensions'] = [b - a for a, b in zip(idle0['min'], idle0['max'])]
    walk = next(c for c in clips if c['name'] == 'Walk')['samples']
    result['walkStrideMeters'] = sum(max(s['ankles'][side] for s in walk) - min(s['ankles'][side] for s in walk) for side in ['l', 'r'])
    result['decodedAccessorBytes'] = sum(a['count'] * widths[a['type']] * components[a['componentType']][1] for a in doc['accessors'])
    result['estimatedDecodedBytes'] = result['decodedAccessorBytes'] + sum(math.ceil(t['width'] * t['height'] * 4 * 4 / 3) for t in textures) + bones * 64
    if render:
        rig.animation_data.action = actions['Idle']
        rig.animation_data.action_slot = actions['Idle'].slots[0]
        scene.frame_set(0)
        wardrobe.base.setup_render(root, identity + '-roundtrip')
        camera = scene.camera
        for view, loc, name, fraction in [
                ('front', (0, -6, 2.1), 'Idle', 0),
                ('side', (6, -.2, 2.1), 'Idle', 0),
                ('walk-a', (3.8, -6, 2.5), 'Walk', .25),
                ('walk-b', (3.8, -6, 2.5), 'Walk', .75)]:
            action = actions[name]
            rig.animation_data.action = action
            rig.animation_data.action_slot = action.slots[0]
            scene.frame_set(int(action.frame_range[1] * fraction))
            camera.location = loc
            camera.rotation_euler = (Vector((0, 0, .92)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
            scene.render.filepath = str(root / 'qa' / (identity + '-' + view + '.png'))
            scene.cycles.samples = 16
            bpy.ops.render.render(write_still=True)
    (root / (identity + '.qa.json')).write_text(json.dumps(result, indent=2))
    print('WARDROBE_QA', identity, triangles, len(raw), [(c['name'], c['soleZMin'], c['soleZMax']) for c in clips])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=wardrobe.ROOT)
    parser.add_argument('--only')
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if sum([bool(args.only), args.pilot, args.all]) != 1:
        parser.error('Choose one --only, --pilot or finite --all')
    ids = [args.only] if args.only else PILOT_IDS if args.pilot else list(WARDROBES)
    results = [measure(args.root, identity, args.render) for identity in ids]
    (args.root / ('pilot-qa.json' if args.pilot else 'wardrobe-qa.json')).write_text(json.dumps(results, indent=2))
