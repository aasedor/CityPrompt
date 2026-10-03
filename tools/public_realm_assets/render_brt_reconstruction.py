"""Render source and reconstructed BRT programs from identical cameras.

Blender CLI --source original --derived recovered --program JSON --output PATH.
The JSON must be exported by the actual frontend brtStreetLayout implementation.
No source saves; evidence only. Not a substitute for student browser testing.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def main():
    import bpy
    from mathutils import Vector
    p=argparse.ArgumentParser()
    for name in ('source','derived','program','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Use a new immutable evidence directory')
    args.output.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.source/'editable.blend'))
    original=[o for o in bpy.context.scene.objects if o.type=='MESH']
    program=json.loads(args.program.read_text())
    groups={}
    for item in program['primitives']:
        vertices,faces=groups.setdefault(item['material'],([],[]));n=len(vertices)
        if item['kind']=='face':
            vertices.extend([(x,y-50,z) for x,y,z in item['points']]);faces.append(tuple(range(n,len(vertices))))
        else:
            x,y,z,w,d,h=(item[k] for k in ('x','y','z','width','depth','height'));y-=50
            top=[(x-w/2,y-d/2,z+h/2),(x+w/2,y-d/2,z+h/2),(x+w/2,y+d/2,z+h/2),(x-w/2,y+d/2,z+h/2)]
            vertices.extend(top);faces.append(tuple(range(n,n+4)))
            if h>0:
                vertices.extend([(x,y,z-h) for x,y,z in top])
                faces.extend((n+i,n+i+4,n+(i+1)%4+4,n+(i+1)%4) for i in range(4))
    rebuilt=[]
    for material,(vertices,faces) in groups.items():
        mesh=bpy.data.meshes.new('runtime_'+material);mesh.from_pydata(vertices,[],faces);mesh.materials.append(bpy.data.materials[material]);mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);rebuilt.append(obj)
    for kind in {f['kind'] for f in program['fixtures']}:
        path=(args.derived if kind in ('station_program','bus_symbol') else args.source/'modules')/(kind+'.glb')
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
        imported=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
        for item in [f for f in program['fixtures'] if f['kind']==kind]:
            from mathutils import Matrix
            transform=Matrix.Translation((item['x'],item['y']-50,item['z'])) @ Matrix.Rotation(item['yaw'],4,'Z') @ Matrix.Scale(item['scale'],4)
            for source in imported:
                obj=source.copy();obj.data=source.data;bpy.context.collection.objects.link(obj)
                obj.matrix_world=transform@source.matrix_world;rebuilt.append(obj)
        for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    if scene.world is None:scene.world=bpy.data.worlds.new('review_world')
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.76,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    for obj in list(scene.objects):
        if obj.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=1500
    cameras=[('aerial',(65,-63,87),(0,0,2),136),('walk',(5.4,-31,2.05),(4.6,5,2.4),None)]
    for label,visible,hidden in [('original',original,rebuilt),('reconstructed',rebuilt,original)]:
        for o in visible:o.hide_render=False
        for o in hidden:o.hide_render=True
        for name,pos,target,scale in cameras:
            cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
            cam.data.type='ORTHO' if scale else 'PERSP'
            if scale:cam.data.ortho_scale=scale
            else:cam.data.lens=32
            scene.render.filepath=str(args.output/f'{label}-{name}.png');bpy.ops.render.render(write_still=True)
    print('MATCHED_BRT_VIEWS',args.output)


if __name__=='__main__':main()
