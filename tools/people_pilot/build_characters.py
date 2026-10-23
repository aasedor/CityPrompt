"""Bounded CC0 character derivatives. Run with Blender 5.2 --background --python.

Inputs are preserved official Quaternius Standard downloads, never paid Source kits.
The adult anatomy, hairstyles and motion are CC0 derivatives. Outer-garment,
trouser and sneaker topology, palettes and measured grounding are authored here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


DEFAULT_ROOT = Path('C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/characters')
DESIGNS = [
    dict(id='people-pilot-commuter', gender='Female', hair='Hair_Buns', height=1.72,
         jacket='#95482f', shirt='#e9dfd0', trousers='#242d39', shoes='#ece6da', hair_color='#291c17', skin='#805139', coat=False),
    dict(id='people-pilot-neighbour', gender='Male', hair='Hair_SimpleParted', height=1.82,
         jacket='#263d58', shirt='#d8d9cc', trousers='#b5a88a', shoes='#382e29', hair_color='#392921', skin='#bb8760', coat=False),
    dict(id='people-pilot-creative', gender='Female', hair='Hair_Long', height=1.68,
         jacket='#87937b', shirt='#eee5d1', trousers='#353637', shoes='#d7c8af', hair_color='#34251d', skin='#bb8a65', coat=True),
]


def color(value):
    rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return (*[v / 12.92 if v < .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb], 1)


def material(name, value, roughness=.8):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color(value)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = color(value)
    p.inputs['Roughness'].default_value = roughness
    return mat


def curves(action):
    return [f for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for f in bag.fcurves]


def remove_obj(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def weighted_mesh(name, verts, faces, weights, rig, mats, mat_indices=None):
    mesh = bpy.data.meshes.new(name); mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj)
    for mat in mats: mesh.materials.append(mat)
    for i, p in enumerate(mesh.polygons):
        p.use_smooth = True
        if mat_indices: p.material_index = mat_indices[i]
    groups = {key: obj.vertex_groups.new(name=key) for key in sorted({key for row in weights for key in row})}
    for i, row in enumerate(weights):
        total = sum(row.values())
        for key, value in row.items(): groups[key].add([i], value / total, 'REPLACE')
    obj.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
    return obj


def ring_mesh(name, rings, weight_fn, rig, mats, center=(0, 0), material_fn=None, segments=32):
    verts, faces, weights, indices = [], [], [], []
    for z, rx, ry in rings:
        for i in range(segments):
            a = 2 * math.pi * i / segments
            v = (center[0] + rx * math.cos(a), center[1] + ry * math.sin(a), z)
            verts.append(v); weights.append(weight_fn(v))
    for row in range(len(rings) - 1):
        for i in range(segments):
            faces.append((row * segments + i, row * segments + (i + 1) % segments,
                          (row + 1) * segments + (i + 1) % segments, (row + 1) * segments + i))
            indices.append(material_fn((i + .5) * 2 * math.pi / segments) if material_fn else 0)
    return weighted_mesh(name, verts, faces, weights, rig, mats, indices)


def clothing_shell(body, rig, design, mats):
    # Remove covered body skin; garments have independent clean boundaries and topology.
    import bmesh
    bm = bmesh.new(); bm.from_mesh(body.data)
    covered = []
    for face in bm.faces:
        c = face.calc_center_median()
        neck_z = rig.data.bones['neck_01'].head_local.z
        arm_z = rig.data.bones['upperarm_l'].head_local.z
        wrist_x = rig.data.bones['lowerarm_l'].tail_local.x
        keep_neck = abs(c.x) < .075 and c.z > neck_z - .055
        torso = .83 < c.z < neck_z + .018 and abs(c.x) < .315 and not keep_neck
        sleeves = arm_z - .165 < c.z < arm_z + .165 and .18 < abs(c.x) < wrist_x - .025
        if torso or sleeves or c.z < .97: covered.append(face)
    bmesh.ops.delete(bm, geom=covered, context='FACES'); bm.to_mesh(body.data); bm.free()
    def torso_weights(v):
        z = v[2]
        anchors = [(.91, 'pelvis'), (1.07, 'spine_01'), (1.23, 'spine_02'), (1.39, 'spine_03')]
        for (lo, low), (hi, high) in zip(anchors, anchors[1:]):
            if z < hi:
                t = max(0, min(1, (z - lo) / (hi - lo)))
                return {low: 1 - t, high: t}
        return {'spine_03': 1}
    # Distinct garment silhouette; a clean continuous ivory front rather than source body triangles.
    rings = [(.885, .185, .151), (.98, .184, .151), (1.12, .183, .15),
             (1.28, .208, .167), (1.39, .237, .155), (1.435, .213, .127), (1.495, .052, .054)]
    if design['gender'] == 'Male':
        rings = [(z + max(0, z - 1.0) * .073, rx * 1.12, ry * 1.16) for z, rx, ry in rings]
    ring_mesh('Hip_length_overshirt', rings, torso_weights, rig, [mats['jacket'], mats['shirt']],
              material_fn=lambda a: 1 if abs(a - 1.5 * math.pi) < .39 else 0)
    # Collar is visibly separate, thin, following neckline.
    ring_mesh('Folded_jacket_collar', [(1.474, .067, .066), (1.508, .054, .057)], torso_weights,
              rig, [mats['jacket']], segments=24)
    for side, sign in [('l', 1), ('r', -1)]:
        upper, lower = rig.data.bones['upperarm_' + side], rig.data.bones['lowerarm_' + side]
        points = [upper.head_local.copy(), upper.tail_local.copy(), lower.tail_local.copy()]
        points[0].x -= sign * .045; points[-1].x -= sign * .025
        verts, faces, weights = [], [], []
        sleeve_radii = [.103, .080, .059] if design['gender'] == 'Male' else [.084, .068, .054]
        for j, (point, radius) in enumerate(zip(points, sleeve_radii)):
            for i in range(24):
                a = 2 * math.pi * i / 24
                verts.append((point.x, point.y + radius * math.cos(a), point.z + radius * math.sin(a)))
                weights.append({'upperarm_' + side: 1} if j == 0 else
                               {'upperarm_' + side: .45, 'lowerarm_' + side: .55} if j == 1 else {'lowerarm_' + side: 1})
        for j in range(2):
            for i in range(24): faces.append((j * 24 + i, j * 24 + (i + 1) % 24, (j + 1) * 24 + (i + 1) % 24, (j + 1) * 24 + i))
        faces.append(tuple(range(23, -1, -1)))
        weighted_mesh('Relaxed_sleeve_' + side, verts, faces, weights, rig, [mats['jacket']])
        # Straight trousers retain knee articulation, with enough fabric volume to hide the base.
        thigh, calf = rig.data.bones['thigh_' + side], rig.data.bones['calf_' + side]
        tx, ty = thigh.head_local.x, thigh.head_local.y
        def leg_weights(v):
            z = v[2]; t = max(0, min(1, (z - .44) / .10))
            return {'thigh_' + side: t, 'calf_' + side: 1 - t}
        ring_mesh('Straight_trouser_' + side,
                  [(.105, .061, .070), (.28, .065, .074), (.48, .073, .081), (.68, .094, .108), (.92, .101, .128)],
                  leg_weights, rig, [mats['trousers']], center=(tx, .025))
        # Closed low-top sneaker, sole rests at zero in the source rest coordinates.
        foot = rig.data.bones['foot_' + side]
        shoe = ring_mesh('Low_top_sneaker_' + side,
                       [(-.009, .062, .151), (.012, .069, .159), (.045, .069, .154), (.085, .058, .137), (.117, .043, .073)],
                       lambda v: {'foot_' + side: 1}, rig, [mats['shoes']], center=(foot.head_local.x, -.055), segments=32)
        # Add bottom cap so nothing disappears in low camera angles.
        m = shoe.data; bm2 = bmesh.new(); bm2.from_mesh(m); edges = [e for e in bm2.edges if e.is_boundary]
        bmesh.ops.holes_fill(bm2, edges=edges); bm2.to_mesh(m); bm2.free()
    # Fill trouser hip region as a single waistband; covered by jacket lower edge.
    ring_mesh('Trouser_waistband', [(.84, .194, .148), (.95, .187, .148)], lambda v: {'pelvis': 1}, rig, [mats['trousers']])


def coat_skirt(rig, mat):
    """Open-front short coat hem, independently weighted to pelvis and thighs."""
    verts, faces = [], []
    # Opening points toward -Y. Ring is elliptical and falls above knees.
    seg = 28
    for z, rx, ry in [(1.00, .185, .145), (.82, .215, .158), (.67, .235, .170)]:
        for i in range(seg + 1):
            a = -.5 * math.pi + .20 + (2 * math.pi - .40) * i / seg
            verts.append((rx * math.cos(a), ry * math.sin(a), z))
    for row in range(2):
        for i in range(seg):
            a = row * (seg + 1) + i
            faces.append((a, a + 1, a + seg + 2, a + seg + 1))
    mesh = bpy.data.meshes.new('Open_front_coat_hem'); mesh.from_pydata(verts, [], faces); mesh.materials.append(mat)
    obj = bpy.data.objects.new('Sage_open_front_coat', mesh); bpy.context.collection.objects.link(obj)
    groups = {n: obj.vertex_groups.new(name=n) for n in ['pelvis', 'thigh_l', 'thigh_r']}
    for i, v in enumerate(verts):
        leg = 'thigh_l' if v[0] > 0 else 'thigh_r'
        influence = min(.55, (1 - v[2]) * 1.2)
        groups['pelvis'].add([i], 1 - influence, 'REPLACE'); groups[leg].add([i], influence, 'REPLACE')
    for p in mesh.polygons: p.use_smooth = True
    mesh.materials[0].use_backface_culling = False
    obj.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
    return obj


def setup_render(root, name):
    from mathutils import Quaternion
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.004))
    floor = bpy.context.object; floor.name = 'QA_floor'; floor.data.materials.append(material('QA_studio_floor', '#aeb4b1'))
    bpy.ops.object.camera_add(location=(3.8, -6.0, 2.8)); camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, .92)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'; camera.data.ortho_scale = 2.18
    scene = bpy.context.scene; scene.camera = camera
    for loc, power, size in [((2, -4, 5), 800, 4), ((-3, -2, 3), 450, 3), ((1, 3, 4), 650, 3)]:
        bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.data.energy = power; l.data.shape = 'DISK'; l.data.size = size
        l.rotation_euler = (Vector((0, 0, 1)) - l.location).to_track_quat('-Z', 'Y').to_euler()
    if scene.world is None: scene.world = bpy.data.worlds.new('QA_world')
    scene.world.color = (.25, .25, .25); scene.render.engine = 'CYCLES'; scene.cycles.samples = 24
    scene.render.resolution_x = 640; scene.render.resolution_y = 720; scene.render.resolution_percentage = 100
    scene.render.filepath = str(root / 'qa' / (name + '.png'))
    bpy.ops.render.render(write_still=True)


def build(root, design, before_export=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene; scene.render.fps = 24
    anim_file = next((root / 'sources/universal-animation-library').rglob('UAL1_Standard.glb'))
    bpy.ops.import_scene.gltf(filepath=str(anim_file))
    actions = {}
    for source, target in [('Walk_Loop', 'Walk'), ('Idle_Loop', 'Idle')]:
        a = bpy.data.actions[source].copy(); a.name = target
        # Source action locations are pose-relative, shared humanoid skeleton. Root is in-place.
        actions[target] = a
    for o in list(scene.objects): remove_obj(o)
    for a in list(bpy.data.actions):
        if a not in actions.values(): bpy.data.actions.remove(a)
    base = next((root / 'sources/universal-base-characters').rglob('Superhero_' + design['gender'] + '_FullBody.gltf'))
    bpy.ops.import_scene.gltf(filepath=str(base))
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    body = max((o for o in scene.objects if o.type == 'MESH' and o.vertex_groups), key=lambda o: len(o.data.vertices))
    for o in list(scene.objects):
        if o.type == 'MESH' and not o.vertex_groups: remove_obj(o)
    mats = {key: material(design['id'] + '_' + key, design[key], .68 if key == 'shoes' else .84) for key in ['jacket', 'shirt', 'trousers', 'shoes']}
    # Material skin is deliberately simple: source facial geometry/UVs remain, skin palette is original.
    skin = material(design['id'] + '_skin', design['skin'], .72)
    body.data.materials.clear(); body.data.materials.append(skin)
    for obj in scene.objects:
        if obj.type == 'MESH' and obj != body and any('Hair' in m.name for m in obj.data.materials):
            obj.data.materials.clear(); obj.data.materials.append(material(design['id'] + '_brows', design['hair_color'], .92))
    shell = clothing_shell(body, rig, design, mats)
    if design['coat']: coat_skirt(rig, mats['jacket'])
    # Free hairstyle meshes are supplied in absolute base coordinates; attach rigidly to head.
    candidates = list((root / 'sources/universal-base-characters').rglob(design['hair'] + '.gltf'))
    hair_file = next((p for p in candidates if 'Godot' in str(p)), candidates[0])
    before = set(scene.objects); bpy.ops.import_scene.gltf(filepath=str(hair_file))
    for o in set(scene.objects) - before:
        if o.type == 'MESH' and o.name != 'Icosphere':
            o.name = design['hair']; o.data.materials.clear(); o.data.materials.append(material(design['id'] + '_hair', design['hair_color'], .92))
            # Use an armature modifier and full Head weights (preserves source placement).
            for mod in list(o.modifiers): o.modifiers.remove(mod)
            o.vertex_groups.clear(); group = o.vertex_groups.new(name='Head'); group.add(list(range(len(o.data.vertices))), 1, 'REPLACE')
            o.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
            o.parent = None
        else: remove_obj(o)
    for o in scene.objects:
        if o.type == 'MESH':
            for poly in o.data.polygons: poly.use_smooth = True
            for m in o.data.materials:
                if m and m.use_nodes:
                    # Export only <=512 textures: eyes still use the creator's texture.
                    for node in m.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            if node.image.source == 'FILE' and not Path(bpy.path.abspath(node.image.filepath)).exists():
                                fallback = next((root / 'sources/universal-base-characters').rglob('T_Eye_Normal.png'), None)
                                if fallback: node.image.filepath = str(fallback); node.image.reload()
                            if max(node.image.size) > 512: node.image.scale(512, 512)
    rig.animation_data_create()
    for name, action in actions.items():
        track = rig.animation_data.nla_tracks.new(); track.name = name
        strip = track.strips.new(name, 0, action); strip.action_slot = action.slots[0]
    rig.animation_data.action = actions['Idle']; rig.animation_data.action_slot = actions['Idle'].slots[0]
    scene.frame_set(0); bpy.context.view_layer.update()
    meshes = [o for o in scene.objects if o.type == 'MESH']
    # Normalize all authored geometry and skeleton together, keeping animation metres coherent.
    top = max(v.co.z for o in meshes for v in o.data.vertices)
    bottom = min(v.co.z for o in meshes for v in o.data.vertices)
    scale = design['height'] / (top - bottom)
    parent = bpy.data.objects.new(design['id'], None); scene.collection.objects.link(parent)
    for o in list(scene.objects):
        if o != parent and o.parent is None: o.parent = parent
    parent.scale = (scale,) * 3; parent.location.z = -bottom * scale
    parent['source'] = 'Quaternius CC0 Universal Base Characters Standard + Universal Animation Library Standard'
    parent['forward'] = '+Z glTF; -Y Blender'; parent['meters'] = True
    # Retargeted shoe volumes differ from the bare-foot source. Bake a bounded
    # vertical correction on the root bone, measured against the actual
    # skinned sneaker vertices at every exported frame, to retain ground contact.
    for track in rig.animation_data.nla_tracks: track.mute = True
    for name, action in actions.items():
        rig.animation_data.action = action; rig.animation_data.action_slot = action.slots[0]
        root_bone = rig.pose.bones['root']
        original_locations = []
        for frame in range(int(action.frame_range[1]) + 1):
            scene.frame_set(frame); original_locations.append(root_bone.location.copy())
        for frame, original_location in enumerate(original_locations):
            scene.frame_set(frame); root_bone.location = original_location; bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get(); lowest = math.inf
            for obj in meshes:
                if 'sneaker' not in obj.name: continue
                ev = obj.evaluated_get(dg); mesh = ev.to_mesh()
                lowest = min(lowest, min((ev.matrix_world @ v.co).z for v in mesh.vertices)); ev.to_mesh_clear()
            delta = rig.data.bones['root'].matrix_local.inverted().to_3x3() @ Vector((0, 0, -lowest / scale))
            root_bone.location = original_location + delta
            root_bone.keyframe_insert(data_path='location', frame=frame, group='Measured_foot_contact')
        for curve in curves(action):
            if curve.data_path == 'pose.bones["root"].location':
                for key in curve.keyframe_points: key.interpolation = 'LINEAR'
    # Select actors only, no accidental QA floor/cameras or source mannequin.
    bpy.ops.object.select_all(action='SELECT')
    rig.animation_data.action = None
    for track in rig.animation_data.nla_tracks: track.mute = False
    if before_export is not None:
        before_export()
    runtime = root / 'runtime'; runtime.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(runtime / (design['id'] + '.glb')), export_format='GLB', use_selection=True,
        export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_nla_strips=True,
        export_frame_range=False, export_force_sampling=True, export_skins=True, export_all_influences=False,
        export_materials='EXPORT', export_extras=True)
    # Keep editable source in artifact storage and a truthful fixed-pose render for review.
    for track in rig.animation_data.nla_tracks: track.mute = True
    rig.animation_data.action = actions['Idle']; rig.animation_data.action_slot = actions['Idle'].slots[0]
    scene.frame_set(0)
    bpy.ops.wm.save_as_mainfile(filepath=str(root / (design['id'] + '.blend')))
    setup_render(root, design['id'])
    print('CHARACTER_EXPORTED', design['id'], 'normalization_scale', scale, 'source_bottom', bottom)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(); parser.add_argument('--root', type=Path, default=DEFAULT_ROOT); parser.add_argument('--only')
    options = parser.parse_args(args)
    (options.root / 'qa').mkdir(exist_ok=True)
    for d in DESIGNS:
        if not options.only or d['id'] == options.only: build(options.root, d)
