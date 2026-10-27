"""Render finite exact GLB storey comparisons in neutral light (Blender only)."""
import json
import hashlib
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def occupied_interiors(root):
    """Supplemental source-datum cameras; never replace models or prior renders."""
    program=json.loads((root/'program.json').read_text())
    is_plus=program['source']['variant_id']=='plus15_contemporary_glass'
    for path in sorted(root.glob('*-storeys.glb')):
        count=int(path.stem.split('-')[-2])
        native=count==program['source']['native_storeys']
        floor=(43.2 if is_plus else 22.3) if native else program['height_contract']['podium_height_m']+2*program['height_contract']['repeatable_storey_height_m']
        destination=root/'renders'/path.stem/'interior_occupied_program_v001.png'
        if destination.exists():
            raise ValueError('Preserve existing supplementary evidence: '+str(destination))
        model_hash=hashlib.sha256(path.read_bytes()).hexdigest()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path))
        scene=bpy.context.scene
        scene.render.engine='CYCLES'
        scene.cycles.samples=32
        scene.cycles.use_denoising=True
        scene.cycles.max_bounces=8
        scene.cycles.transparent_max_bounces=8
        scene.render.threads_mode='FIXED'
        scene.render.threads=6
        try:
            preferences=bpy.context.preferences.addons['cycles'].preferences
            preferences.compute_device_type='OPTIX'; preferences.get_devices()
            for device in preferences.devices: device.use=device.type!='CPU'
            if any(d.use for d in preferences.devices): scene.cycles.device='GPU'
        except Exception: pass
        scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG'
        scene.view_settings.view_transform='AgX'
        world=bpy.data.worlds.new('Neutral interior QA world');world.use_nodes=True
        world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;scene.world=world
        camera_position=(-12,3,floor+1.6) if is_plus else (-7,-3,floor+1.55)
        target=(-10,-17,floor+1.1) if is_plus else (-8,-11.5,floor+1.0)
        lights=[((-11,-10,floor+3.0),(-10,-12,floor+.5),450,5),((-12,1,floor+2.6),(-10,-10,floor+1),250,4)] if is_plus else [((-7,-5,floor+2.7),(-7,-8,floor+.6),250,4)]
        for location,look,power,size in lights:
            bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object
            light.data.energy=power;light.data.size=size;aim(light,look)
        bpy.ops.object.camera_add(location=camera_position);camera=bpy.context.object
        camera.data.lens=36 if is_plus else 28;camera.data.clip_start=.03;camera.data.clip_end=500
        aim(camera,target);scene.camera=camera;scene.render.filepath=str(destination)
        bpy.ops.render.render(write_still=True)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==model_hash
        destination.with_suffix('.json').write_text(json.dumps(dict(source_glb=str(path),sha256=model_hash,
            model_and_material_bytes_unchanged=True,source_floor_datum_m=floor,location=camera_position,target=target,
            qa_only='Inside perspective and neutral room lights; no mesh/material replacement'),indent=2)+'\n')


def main():
    root = Path(sys.argv[sys.argv.index('--')+1])
    program = json.loads((root/'program.json').read_text())
    variant = program['source']['variant_id']
    is_plus = variant == 'plus15_contemporary_glass'
    is_slab = variant == 'midcentury_concrete_slab'
    face_y = -18 if is_plus else -11 if is_slab else -12
    podium_height = program['height_contract']['podium_height_m']
    paths = sorted(root.glob('*-storeys.glb'))
    for path in paths:
        destination = root / 'renders' / path.stem
        if destination.exists():
            raise ValueError('Preserve existing renders: '+str(destination))
        destination.mkdir(parents=True)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path))
        points = [o.matrix_world @ Vector(v) for o in bpy.context.scene.objects if o.type == 'MESH' for v in o.bound_box]
        lo = Vector([min(p[i] for p in points) for i in range(3)])
        hi = Vector([max(p[i] for p in points) for i in range(3)])
        center = (lo+hi)*.5
        width, depth, height = hi-lo
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 16
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 7
        scene.cycles.transparent_max_bounces = 8
        scene.render.threads_mode = 'FIXED'
        scene.render.threads = 6
        try:
            preferences = bpy.context.preferences.addons['cycles'].preferences
            preferences.compute_device_type = 'OPTIX'
            preferences.get_devices()
            for device in preferences.devices:
                device.use = device.type != 'CPU'
            if any(device.use for device in preferences.devices):
                scene.cycles.device = 'GPU'
        except Exception:
            pass
        scene.render.resolution_x = 1440
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.view_settings.view_transform = 'AgX'
        world = bpy.data.worlds.new('Neutral QA world')
        world.use_nodes = True
        world.node_tree.nodes['Background'].inputs['Color'].default_value = (.65,.68,.72,1)
        world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
        scene.world = world
        bpy.ops.mesh.primitive_plane_add(size=max(height,width,depth)*8, location=(0,0,-.025))
        ground = bpy.context.object
        ground.name = 'QA ground only'
        material = bpy.data.materials.new('QA ground')
        material.diffuse_color = (.55,.56,.54,1)
        ground.data.materials.append(material)
        for location, strength in [((-1,-2,3),2.2), ((2,-1,2),1.2), ((-1,2,2),1.6)]:
            bpy.ops.object.light_add(type='AREA', location=Vector(location)*max(height,width,depth))
            light = bpy.context.object
            light.data.energy = max(height,width,depth)**2 * strength * 20
            light.data.shape = 'DISK'
            light.data.size = max(height,width,depth)*1.4
            aim(light, center)
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        camera.data.type = 'ORTHO'
        camera.data.clip_end = 5000
        scene.camera = camera
        directions = dict(front=(0,-1,0), front_corner=(-1,-1,.45), aerial=(-1,-1,1.5), top=(0,-.001,1),
            left_side=(-1,0,0),right_side=(1,0,0),rear=(0,1,0),rear_side=(1,1,.45))
        roster = [(name, center, direction, True, None) for name,direction in directions.items()]
        roster += [('facade_close',Vector((0,face_y,height*.48)),(-.4,-1,.1),False,23),
            ('architecture_close',Vector((0,face_y,6)),(.5,-1,.25),False,34),
            ('glass_close',Vector((4,face_y,height*.48)),(.15,-1,.08),False,12),
            ('roof_contact',Vector((0,0,height-5)),(.6,-1,.65),False,43),
            ('lobby_contact',Vector((0,face_y,4)),(-.4,-1,.15),False,29),
            ('repeat_seam',Vector((0,face_y,podium_height)),(.4,-1,.12),False,15)]
        if is_plus:
            roster += [('plus15_bridge',Vector((-2.6,-32,6)),(-1,-1,.35),False,43),
                ('roof_terrace',Vector((-6,2,height-9)),(-1,-1,1.2),False,45),
                ('crown_penthouse',Vector((0,2,height-5)),(1,-1,.6),False,38),
                ('interior',Vector((-9,face_y,height*.5)),(-.15,-1,.08),False,11)]
        if is_slab:
            roster += [('balcony_close',Vector((7.5,-12,height*.5)),(.5,-1,.3),False,16),
                ('fin_contact',Vector((-3.4,-11,5)),(-1,-1,.3),False,19),
                ('roof_penthouse',Vector((0,3,height-3.5)),(-1,-1,.7),False,32),
                ('interior',Vector((-7,face_y,height*.5)),(-.15,-1,.08),False,10)]
        records = []
        for name, target, direction, whole, scale in roster:
            camera.location = target + Vector(direction).normalized()*max(height,width,depth)*4
            aim(camera,target)
            camera.data.ortho_scale = scale or (max(width,depth)*1.25 if name == 'top' else max(height,width,depth))
            bpy.context.view_layer.update()
            if whole:
                for _ in range(80):
                    projected = [world_to_camera_view(scene,camera,p) for p in points]
                    if all(.085<=p.x<=.915 and .085<=p.y<=.915 for p in projected):
                        break
                    camera.data.ortho_scale *= 1.045
                else:
                    raise ValueError('Camera fit failed: '+name)
            scene.render.filepath = str(destination / (name+'.png'))
            bpy.ops.render.render(write_still=True)
            records.append(dict(view=name, whole=whole, location=list(camera.location),target=list(target),ortho_scale=camera.data.ortho_scale))
        (destination/'render-manifest.json').write_text(json.dumps(dict(source_glb=str(path),no_geometry_or_material_replacement=True,
            bounds=[list(lo),list(hi)],resolution=[1440,1080],views=records),indent=2)+'\n')


if __name__ == '__main__':
    if '--interiors' in sys.argv:
        occupied_interiors(Path(sys.argv[sys.argv.index('--')+1]))
    else:
        main()
