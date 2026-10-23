"""Bounded final tailoring of four reviewed wardrobe variants.

Keeps the frozen shared generator immutable while finishing actual exported
garments. --all is exactly Leo/Owen/Rhea/Elena. Original derivative sources and
pre-finish GLBs are retained in the external checkpoint.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wardrobe as wardrobe

IDS = ('people-community-leo', 'people-community-owen', 'people-community-rhea', 'people-community-elena')


def finish(root, identity):
    assert identity in IDS
    source = root / (identity + '.blend')
    glb = root / 'runtime' / (identity + '.glb')
    record_path = root / (identity + '.source.json')
    checkpoint = root / 'checkpoints/pre-finish4'
    checkpoint.mkdir(parents=True, exist_ok=True)
    for path in [source, glb, record_path]:
        target = checkpoint / path.name
        if not target.exists():
            shutil.copy2(path, target)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    body = next(o for o in scene.objects if o.type == 'MESH' and o.name.lower().startswith('superhero'))
    top = bpy.data.objects['Anatomical_continuous_top']
    cloth = body.data.materials[1]
    if identity == 'people-community-leo':
        index = len(top.data.materials)
        top.data.materials.append(cloth)
        for polygon in top.data.polygons:
            if polygon.center.z > 1.40 and abs(polygon.center.x) < .35:
                polygon.material_index = index
        change = 'Continuous burgundy upper rugby yoke; broad cream/burgundy torso and sleeve stripes retained.'
    elif identity == 'people-community-owen':
        for uv in top.data.uv_layers.active.data:
            uv.uv *= 2.6
        change = 'Reference-scale small ochre/navy flannel plaid, using the embedded authored texture.'
    else:
        # A sleeveless bodice must follow the torso, independently of the bare
        # upper arms. Copying the source deltoid skin had left raised armhole
        # edges when its arm weights rotated downward.
        bpy.data.objects.remove(top, do_unlink=True)
        for polygon in body.data.polygons:
            if polygon.center.z > .98:
                polygon.material_index = 1 if polygon.center.z < 1.41 and abs(polygon.center.x) < .15 else 0
        neck = rig.data.bones['neck_01'].head_local.z
        def bodice_weights(v):
            return {'pelvis': 1} if v[2] < 1.08 else wardrobe.torso_weights(v)
        bodice = wardrobe.base.ring_mesh('Tailored_sleeveless_bodice',
                               [(.96, .20, .155), (1.10, .195, .155), (1.27, .20, .16),
                               (1.35, .20, .18), (1.415, .16, .14), (neck - .005, .07, .07)],
                               bodice_weights, rig, [cloth], center=(0, .025), segments=48)
        bodice.parent = bpy.data.objects[identity]
        change = 'Continuous torso-weighted sleeveless bodice; complete bare shoulders/arms preserved; no raised armhole flaps.'
    parent = bpy.data.objects[identity]
    parent['wardrobe_finish'] = 'picker-locked-finish-v1'
    bpy.ops.object.select_all(action='SELECT')
    rig.animation_data.action = None
    for track in rig.animation_data.nla_tracks:
        track.mute = False
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                             export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS',
                             export_nla_strips=True, export_frame_range=False, export_force_sampling=True,
                             export_skins=True, export_all_influences=False, export_materials='EXPORT', export_extras=True)
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    idle = bpy.data.actions['Idle']
    rig.animation_data.action = idle
    rig.animation_data.action_slot = idle.slots[0]
    scene.frame_set(0)
    editable = root / (identity + '.finished.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(editable))
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 8
    wardrobe.base.setup_render(root, identity)
    record = json.loads(record_path.read_text())
    record['glbSha256'] = wardrobe.sha(glb)
    record['postprocess'] = dict(generator='tools/people_pilot/finish_wardrobe.py', sha256=wardrobe.sha(__file__),
                                 change=change, editableSource=str(editable))
    record_path.write_text(json.dumps(record, indent=2))
    print('WARDROBE_FINISHED', identity, change)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=wardrobe.ROOT)
    parser.add_argument('--only', choices=IDS)
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if bool(args.only) == args.all:
        parser.error('Choose --only ID or the bounded --all four')
    for identity in [args.only] if args.only else IDS:
        finish(args.root, identity)
