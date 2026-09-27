"""Finite source GLB versus actual frontend program comparisons. No asset writes."""
import argparse
import json
import sys
from pathlib import Path

def main():
    import bpy
    from mathutils import Vector, Matrix
    p=argparse.ArgumentParser()
    for name in ('source','modules','program','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Use a new evidence directory')
    a.output.mkdir(parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.source/'assembly-preview.glb'))
    original=[o for o in bpy.data.objects if o.type=='MESH']
    data=json.loads(a.program.read_text());center=data['length']/2;rebuilt=[]
    for item in data['geometry']:
        vertices=item['positions'];indices=item['indices']
        mesh=bpy.data.meshes.new('runtime_'+item['material'])
        mesh.from_pydata([(vertices[i],vertices[i+1]-center,vertices[i+2]) for i in range(0,len(vertices),3)],[],[indices[i:i+3] for i in range(0,len(indices),3)])
        mat=bpy.data.materials.new('runtime_'+item['material']);mat.diffuse_color=tuple(data['palette'][item['material']])+ (1,)
        mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=mat.diffuse_color;bsdf.inputs['Roughness'].default_value=.86
        mesh.materials.append(mat);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);rebuilt.append(obj)
    for kind in {f['kind'] for f in data['fixtures']}:
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(a.modules/(kind+'.glb')))
        imported=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
        for item in [f for f in data['fixtures'] if f['kind']==kind]:
            frame=Matrix.Translation((item['x'],item['y']-center,item['z']))@Matrix.Rotation(item['yaw'],4,'Z')@Matrix.Scale(item['scale'],4)
            for source in imported:
                obj=source.copy();bpy.context.collection.objects.link(obj);obj.matrix_world=frame@source.matrix_world;rebuilt.append(obj)
        for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('review_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.76,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=1500
    x=data['width']/2-1.25
    cameras=[('top',(0,0,90),(0,.001,0),data['length']*1.35),('oblique',(35,-40,58),(0,0,1),data['length']*1.45),('walk',(x,-center+3,1.75),(x,center-5,1.75),None)]
    for label,visible,hidden in [('original',original,rebuilt),('reconstructed',rebuilt,original)]:
        for obj in visible:obj.hide_render=False
        for obj in hidden:obj.hide_render=True
        for name,pos,target,scale in cameras:
            cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if scale else 'PERSP'
            if scale:cam.data.ortho_scale=scale
            else:cam.data.lens=32
            scene.render.filepath=str(a.output/f'{label}-{name}.png');bpy.ops.render.render(write_still=True)
    print('MATCHED_NATIVE_VIEWS',a.output)

if __name__=='__main__':main()
