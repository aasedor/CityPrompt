"""Finite local CC0 adult derivatives. Never modifies the three pilot assets.

Run Blender 5.2 --background --python build_community.py -- --only ID,
visually review it, then run with --remaining for the bounded remaining 19.
Preserved official source files are read through an external directory junction.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import build_characters as pilot
from community_shapes import shape_vertex

ROOT = Path('C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters')
DESIGNS = json.loads(Path(__file__).with_name('community_designs.json').read_text())
_clothing = pilot.clothing_shell
current = None


def community_clothing(body, rig, design, mats):
    result = _clothing(body, rig, design, mats)
    if design['gender'] == 'Male':
        # The male neck is offset behind the garment's origin. Its original
        # cut body boundary left visible gaps inside the jacket neckline.
        pilot.ring_mesh('Closed_neck_skin_underlay',
                        [(1.47, .095, .095), (1.535, .090, .085), (1.61, .063, .067)],
                        lambda v: {'neck_01': 1}, rig, [body.data.materials[0]],
                        center=(0, .025), segments=32)
        pilot.ring_mesh('Closed_neckline_collar',
                        [(1.48, .13, .12), (1.53, .105, .10), (1.56, .072, .075)],
                        lambda v: {'neck_01': 1}, rig, [mats['jacket']],
                        center=(0, .025), segments=32)
    # The source body's shoulder vertices are removed under the garment.
    # A small skinned yoke closes the neckline/sleeve intersection in oblique views.
    for side, sign in [('l', 1), ('r', -1)]:
        anchor = rig.data.bones['upperarm_' + side].head_local
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12,
                                           location=(anchor.x - sign * .02, anchor.y, anchor.z - .025))
        yoke = bpy.context.object
        yoke.name = 'Closed_shoulder_yoke_' + side
        yoke.scale = (.095, .087, .055)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        yoke.data.materials.append(mats['jacket'])
        group = yoke.vertex_groups.new(name='upperarm_' + side)
        group.add(list(range(len(yoke.data.vertices))), 1, 'REPLACE')
        yoke.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
    if design['collar'] == 'stand':
        pilot.ring_mesh('Ribbed_stand_collar', [(1.475, .065, .065), (1.535, .059, .059)],
                        lambda v: {'neck_01': 1}, rig, [mats['jacket']], segments=24)
    return result


def apply_community_shape():
    design = current
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        center = 0
        if 'Straight_trouser' in obj.name:
            center = sum(v.co.x for v in obj.data.vertices) / len(obj.data.vertices)
        for vertex in obj.data.vertices:
            vertex.co = shape_vertex(design, obj.name, tuple(vertex.co), center)
    parent = bpy.data.objects[design['id']]
    parent.scale.x *= design['body_width']
    parent.scale.y *= design['body_depth']
    parent['design'] = design['outfit']
    parent['license'] = 'CC0-1.0 derivative'
    bpy.context.view_layer.update()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--only')
    parser.add_argument('--remaining', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if not args.only and not args.remaining:
        parser.error('Choose one pilot --only ID or the finite --remaining batch')
    assert len(DESIGNS) == 20 and len({d['id'] for d in DESIGNS}) == 20
    assert all(d['id'].startswith('people-community-') for d in DESIGNS)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / 'qa').mkdir(exist_ok=True)
    assert (args.root / 'sources').exists(), 'Create read-only source junction first'
    pilot.clothing_shell = community_clothing
    for design in DESIGNS:
        if args.only and design['id'] != args.only:
            continue
        if args.remaining and (args.root / 'runtime' / (design['id'] + '.glb')).exists():
            continue
        current = design
        pilot.build(args.root, design, before_export=apply_community_shape)
