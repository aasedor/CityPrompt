"""Finite twelve extra actual-model QA views: studio, portrait, walk-back."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
import build_characters as pilot

ROOT = Path('C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters')
for slug in ['ava', 'noah', 'zara', 'jules']:
    name = 'people-community-' + slug
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / (name + '.blend')))
    scene = bpy.context.scene
    pilot.setup_render(ROOT, name + '-review-base')
    scene.camera.location = (1.5, -3.3, 1.95)
    scene.camera.rotation_euler = (Vector((0, 0, 1.45)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera.data.ortho_scale = 1.0
    scene.render.filepath = str(ROOT / 'qa' / (name + '-portrait.png'))
    bpy.ops.render.render(write_still=True)
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    action = bpy.data.actions['Walk']
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    scene.frame_set(12)
    scene.camera.location = (-4, 1.5, 2.0)
    scene.camera.rotation_euler = (Vector((0, 0, .95)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera.data.ortho_scale = 2.35
    scene.render.filepath = str(ROOT / 'qa' / (name + '-walk-back.png'))
    bpy.ops.render.render(write_still=True)
