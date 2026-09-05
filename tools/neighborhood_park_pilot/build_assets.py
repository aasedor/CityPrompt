"""Bounded neighbourhood-park candidate. Never overwrites the legacy kit.

Run with Blender --background --python this_file -- --source-root PATH
--output-dir PATH. The source root supplies the reviewed historical materials
and exact variant-0 references; generated output belongs in ignored artifacts.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import shutil
import sys

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--dry-run', action='store_true', help='Validate source inputs and list the finite batch without writing assets.')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root, output = args.source_root.resolve(), args.output_dir.resolve()
legacy_path = root / 'tools/public_realm_sticker_method/park/neighborhood_park_v0/build_objects.py'
required = [legacy_path, root / 'frontend/node_modules/@dgreenheck/ez-tree/src/lib/assets/leaves/oak_color.png',
            root / 'frontend/node_modules/@dgreenheck/ez-tree/LICENSE']
required += [root / 'frontend/public/archetypes/openspaces/neighborhood-park' / name
             for name in ['variant_0.png', 'variant_0_angle_60.jpg', 'variant_0_angle_90.jpg']]
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit('Missing pilot inputs: ' + ', '.join(missing))
if args.dry_run:
    print(json.dumps({'dryRun': True, 'assets': 9, 'output': str(output), 'sourceInputsPresent': len(required)}))
    raise SystemExit(0)
if output.exists() and any(output.iterdir()):
    raise SystemExit('Output already contains a candidate; choose a new revision directory.')
output.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('legacy_park_objects', legacy_path)
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def simple_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .88
    return mat

def pavilion(mats):
    legacy.build_pavilion(mats)
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('Pavilion roof plane'):
            obj.rotation_euler.y *= -1  # Ridge high, both eaves low.

def bench(mats):
    for y in (-.14, .14):
        legacy.box('Bench seat slat', (1.9, .22, .09), (0, y, .46), mats['timber'], 'park_bench', 'timber')
    for z in (.76, .99):
        legacy.box('Bench back slat', (1.9, .10, .17), (0, .26, z), mats['timber'], 'park_bench', 'timber')
    for x in (-.70, .70):
        legacy.box('Bench foot', (.11, .55, .09), (x, 0, .045), mats['metal'], 'park_bench', 'metal')
        legacy.box('Bench leg', (.10, .1, .46), (x, 0, .23), mats['metal'], 'park_bench', 'metal')
        legacy.box('Bench back support', (.08, .08, .8), (x, .26, .61), mats['metal'], 'park_bench', 'metal')

def tree(seed):
    """Branching deciduous canopy with leaf-twig cards, not crown billboards.

    Botanical silhouette is inferred from the exact aerial references. The
    reusable oak twig texture is MIT licensed; it is not photographic source
    projection or a replacement for the park's locked composition.
    """
    rng = random.Random(seed)
    wood = simple_material('Oak bark', (.20, .155, .105))
    leaves = simple_material('Oak leaf twigs', (.66, .80, .48))
    texture_path = root / 'frontend/node_modules/@dgreenheck/ez-tree/src/lib/assets/leaves/oak_color.png'
    nodes, links = leaves.node_tree.nodes, leaves.node_tree.links
    shader = nodes.get('Principled BSDF')
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(texture_path))
    links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    links.new(tex.outputs['Alpha'], shader.inputs['Alpha'])
    leaves.surface_render_method = 'DITHERED'
    # glTF exporter maps the clip extras below to MASK after export.
    leaf_vertices, leaf_faces = [], []
    top = rng.uniform(8.0, 9.4)

    def branch_mesh(name, points, radii, sides=7):
        """Continuous curved, tapered wood, with closed end faces."""
        verts, faces = [], []
        for i, (point, radius) in enumerate(zip(points, radii)):
            tangent = (points[min(i+1,len(points)-1)] - points[max(0,i-1)]).normalized()
            helper = Vector((0,1,0)) if abs(tangent.y) < .9 else Vector((1,0,0))
            u = tangent.cross(helper).normalized(); v = tangent.cross(u).normalized()
            for j in range(sides):
                angle = j * math.tau / sides
                verts.append(tuple(point + radius*(math.cos(angle)*u + math.sin(angle)*v)))
        faces.append(tuple(reversed(range(sides))))
        for i in range(len(points)-1):
            for j in range(sides):
                a=i*sides+j; b=i*sides+(j+1)%sides
                faces.append((a,b,b+sides,a+sides))
        faces.append(tuple((len(points)-1)*sides+j for j in range(sides)))
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
        obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(wood)
        for face in mesh.polygons: face.use_smooth=True

    trunk=[Vector((0,0,0)),Vector((.05,-.06,1.9)),Vector((-.10,.04,3.1)),
           Vector((.14,.08,top*.55)),Vector((.08,-.12,top*.77))]
    branch_mesh('Curved oak trunk',trunk,[.24,.21,.16,.10,.035],9)
    # Eight unequal leaders emerge at actual trunk nodes, then divide again.
    # This avoids the old 34-spoke fan and leaves clear trunk below the crown.
    for index in range(8):
        angle=index*2.39996+rng.uniform(-.42,.42)
        start=trunk[2 if index<5 else 3].copy()
        crown_z=top*rng.uniform(.57,.76) if index<5 else top*rng.uniform(.78,.91)
        reach=rng.uniform(1.65,2.15) if index<5 else rng.uniform(.65,1.35)
        end=Vector((math.cos(angle)*reach,math.sin(angle)*reach,crown_z))
        bend=start.lerp(end,.55)+Vector((-.1*math.sin(angle),.1*math.cos(angle),-.25))
        branch_mesh(f'Oak leader {index}',[start,bend,end],[.105,.065,.021])
        for twig in range(6):
            yaw=angle+rng.uniform(-.85,.85)
            origin=bend.lerp(end,rng.uniform(.28,.92))
            tip=end+Vector((math.cos(yaw)*rng.uniform(.05,.38),math.sin(yaw)*rng.uniform(.05,.38),rng.uniform(-.12,.48)))
            branch_mesh('Secondary curved branch',[origin,origin.lerp(tip,.58)+Vector((0,0,.08)),tip],[.025,.016,.006],5)
            for card in range(42):
                # Overlapping volumes along each outer branch form one crown,
                # rather than a separate clipped pom-pom at every twig tip.
                c=origin.lerp(tip,rng.uniform(.35,1.0))+Vector((rng.uniform(-.90,.90),rng.uniform(-.90,.90),rng.uniform(-.70,.95)))
                yaw,tilt=rng.uniform(0,math.tau),rng.uniform(-1.15,1.15)
                width,height=rng.uniform(.32,.49),rng.uniform(.29,.46)
                u=Vector((math.cos(yaw),math.sin(yaw),0))*width
                v=Vector((-math.sin(yaw)*math.sin(tilt),math.cos(yaw)*math.sin(tilt),math.cos(tilt)))*height
                quad=[c-u-v,c+u-v,c+u+v,c-u+v]
                # A bounded crown radius is also the live planting clearance.
                if max(math.hypot(p.x,p.y) for p in quad)>3.0: continue
                n=len(leaf_vertices);leaf_vertices.extend(tuple(p) for p in quad)
                leaf_faces.append((n,n+1,n+2,n+3))
    mesh = bpy.data.meshes.new('Leaf twigs')
    mesh.from_pydata(leaf_vertices, [], leaf_faces)
    mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        for index, uv in zip(polygon.loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            mesh.uv_layers.active.data[index].uv = uv
    obj = bpy.data.objects.new('Layered oak canopy', mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(leaves)

def export(name, builder, material_kit=True):
    legacy.reset_scene()
    builder(legacy.materials()) if material_kit else builder()
    bpy.context.view_layer.update()
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    # Evaluate bevels and measure real vertices before normalising the anchor.
    # Rotated bounding-box corners overestimated the boulders' lower bound,
    # leaving the old exported group 0.36 m above its declared ground plane.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH')
    objects=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    bpy.context.view_layer.update()
    if name == 'boulders':
        for obj in objects:
            obj.location.z -= min((obj.matrix_world @ vertex.co).z for vertex in obj.data.vertices)
        bpy.context.view_layer.update()
    world = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    minimum = Vector(tuple(min(v[i] for v in world) for i in range(3)))
    maximum = Vector(tuple(max(v[i] for v in world) for i in range(3)))
    offset = Vector(((minimum.x + maximum.x) / 2, (minimum.y + maximum.y) / 2, minimum.z))
    # Keep the live tree anchor at its trunk, rather than canopy bbox centre.
    if not material_kit: offset.x = offset.y = 0
    for obj in objects: obj.location -= offset
    # Join per material to bound draw calls without deleting physical detail.
    groups = {}
    for obj in objects: groups.setdefault(obj.data.materials[0].name, []).append(obj)
    for group in groups.values():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in group: obj.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='SELECT')
    path = output / f'{name}.glb'
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_apply=True, export_extras=True)
    # MASK avoids transparent-card sorting and keeps depth/occlusion correct.
    import struct
    raw = path.read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    data = json.loads(raw[20:20 + length])
    for mat in data.get('materials', []):
        if mat.get('name') == 'Oak leaf twigs':
            mat.update(alphaMode='MASK', alphaCutoff=.25, doubleSided=True)
            mat['pbrMetallicRoughness']['baseColorFactor'] = [.78, .86, .60, 1]
    encoded = json.dumps(data, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    tail = raw[20 + length:]
    path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20 + len(encoded) + len(tail)) + struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + tail)
    return {'url': f'/landscape-pilots/{output.name}/{name}.glb', 'sha256': digest(path), 'bytes': path.stat().st_size,
            'dimensionsM': list(maximum - minimum), 'bottomM': 0, 'nonuniformScalingAllowed': False,
            'meshCount': len(data.get('meshes', []))}

assets = {
    'pavilion': export('gable-pavilion', pavilion),
    'tower': export('timber-play-tower', legacy.build_tower_slide),
    'swing': export('timber-swing', legacy.build_swing),
    'fence': export('split-rail', legacy.build_fence),
    'boulders': export('boulders', legacy.build_boulders),
    'bench': export('timber-bench', bench),
}
for seed in range(3): assets[f'tree{seed}'] = export(f'oak-{seed}', lambda seed=seed: tree(917 + seed), False)
reference = root / 'frontend/public/archetypes/openspaces/neighborhood-park'
manifest = {'schemaVersion': 1, 'method': 'RLASM-v6.1-landscape-pilot', 'status': 'candidate-not-catalogue-approved',
            'archetypeId': 'neighborhood_park', 'variantId': 'neighborhood_park_v0', 'assets': assets,
            'sources': [{'path': str((reference / name).relative_to(root)).replace('\\', '/'), 'sha256': digest(reference / name), 'role': role}
                        for name, role in [('variant_0.png', 'material-and-human-scale'), ('variant_0_angle_60.jpg', 'primary-topology'), ('variant_0_angle_90.jpg', 'primary-topology')]],
            'inferences': ['Equipment dimensions are design assumptions, not a survey.', 'Repeated timber towers interpret the two aerial play pockets.',
                           'Oak branch topology and species are inferred; foliage texture is licensed supporting material.', 'Play clearances are pilot design allowances, not playground certification.'],
            'preserved': ['dominant lawn', 'continuous walking loop', 'two separate play pockets on full-size sites', 'one gabled pavilion', 'one swing', 'woodland/wildflower perimeter'],
            'legacyBuilderSha256': digest(legacy_path),
            'candidateBuilderSha256': digest(Path(__file__)),
            'foliageTextureSha256': digest(required[1]),
            'vegetationContract': {'maxNativeCrownRadiusM': 3.0, 'maxRuntimeUniformScale': 1.08,
                                   'treeBoundaryClearanceM': 3.3, 'drawCallsPerTreeVariant': 2,
                                   'branching': 'curved tapered trunk, unequal leaders and secondary branches'}}
(output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
shutil.copy2(root / 'frontend/node_modules/@dgreenheck/ez-tree/LICENSE', output / 'FOLIAGE_LICENSE.txt')
shutil.copy2(__file__, output / 'build_assets.py')
print(json.dumps({'output': str(output), 'totalBytes': sum(v['bytes'] for v in assets.values()), 'assets': len(assets)}))
