"""Matched original/reconstruction cameras using actual runtime geometry JSON.

Blender --python this_file -- --source DIR --derived DIR --program JSON
--output NEW_DIR --delivery canal-v005|bridge-v003. Evidence only.
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    import bpy
    from mathutils import Vector,Matrix
    p=argparse.ArgumentParser()
    for name in ('source','derived','program','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--delivery',choices=['canal-v005','bridge-v003'],required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Choose a new evidence directory')
    args.output.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.source/'editable.blend'))
    original=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='water inspection context']
    for o in bpy.context.scene.objects:
        if o.name=='water inspection context':o.hide_render=True
    program=json.loads(args.program.read_text());center=program['length']/2;rebuilt=[]
    for item in program['geometry']:
        positions=item['positions'];indices=item['indices']
        mesh=bpy.data.meshes.new('runtime_'+item['material'])
        mesh.from_pydata([(positions[i],positions[i+1]-center,positions[i+2]) for i in range(0,len(positions),3)],[],
                         [tuple(indices[i:i+3]) for i in range(0,len(indices),3)])
        mesh.materials.append(bpy.data.materials[item['material']]);mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);rebuilt.append(obj)
    for kind in {f['kind'] for f in program['fixtures']}:
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(args.derived/(kind+'.glb')))
        imported=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
        for item in [f for f in program['fixtures'] if f['kind']==kind]:
            transform=Matrix.Translation((item['x'],item['y']-center,item['z']))@Matrix.Rotation(item['yaw'],4,'Z')@Matrix.Scale(item['scale'],4)
            for source in imported:
                obj=source.copy();bpy.context.collection.objects.link(obj);obj.matrix_world=transform@source.matrix_world;rebuilt.append(obj)
        for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    if not scene.world:scene.world=bpy.data.worlds.new('review_world')
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.76,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    for obj in list(scene.objects):
        if obj.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=1500
    cameras=[('aerial',(51,-49,75),(0,0,0),110),('walk',(15,-25,3),(10,-11,.5),None)] if args.delivery=='canal-v005' else [('aerial',(65,-65,85),(0,0,7),135),('walk',(-9,-57,7),(0,-5,12),None)]
    for label,visible,hidden in [('original',original,rebuilt),('reconstructed',rebuilt,original)]:
        for o in visible:o.hide_render=False
        for o in hidden:o.hide_render=True
        for name,pos,target,scale in cameras:
            cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if scale else 'PERSP'
            if scale:cam.data.ortho_scale=scale
            else:cam.data.lens=35
            scene.render.filepath=str(args.output/f'{label}-{name}.png');bpy.ops.render.render(write_still=True)
    print('MATCHED_SPECIALIST_VIEWS',args.output)


if __name__=='__main__':main()
