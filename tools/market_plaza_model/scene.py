"""Offline public-realm model evidence. No runtime or catalogue writes."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

MATS = {}
def material(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = .8
    MATS[name] = m

def init():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for n, c in dict(stone=(.58,.52,.42), pale=(.72,.69,.61), timber=(.32,.17,.075),
        metal=(.075,.09,.085), red=(.49,.16,.07), ochre=(.64,.42,.12),
        soil=(.16,.12,.07), grass=(.25,.29,.12), asphalt=(.13,.145,.14),
        marking=(.86,.86,.75), green=(.19,.33,.21)).items(): material(n,c)

def finish(obj, name, mat):
    obj.name=name; obj.data.materials.append(MATS[mat]); obj['public_realm_model']=True
    return obj

def box(name, xyz, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    o=bpy.context.object; o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat)

def beam(name, a, b, radius, mat):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=radius,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return finish(o,name,mat)

def mesh(name, verts, faces, mat):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
    return finish(o,name,mat)

def bench(x,y):
    for dx in (-.73,.73): box('Bench support',(x+dx,y,.22),(.09,.48,.44),'metal')
    for j in range(5): box('Bench seat slat',(x,y-.22+j*.11,.465),(1.8,.095,.05),'timber')
    for dx in (-.73,.73):box('Bench back support',(x+dx,y+.26,.66),(.055,.055,.58),'metal')
    for z in (.67,.82):box('Bench back slat',(x,y+.26,z),(1.8,.06,.12),'timber')

def grass(x,y,z,seed=0):
    # Small folded blades, not rounded broccoli crowns. Tree stands stay runtime-owned.
    for j in range(9):
        a=j*2.399+seed; r=.08+(j%3)*.10; h=.32+(j%4)*.09
        dx,dy=math.cos(a),math.sin(a)
        mesh('Prairie grass blade',[(x+r*dx-.03*dy,y+r*dy+.03*dx,z),
             (x+r*dx+.03*dy,y+r*dy-.03*dx,z),(x+(r+.14)*dx,y+(r+.14)*dy,z+h)],[(0,1,2)],'grass')

def lamp(x,y):
    box('Light base',(x,y,.06),(.28,.28,.12),'metal')
    beam('Light column',(x,y,.12),(x,y,4),.055,'metal')
    box('Light head',(x,y,4),(.48,.24,.12),'metal')

def save_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def export(path, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
    return dict(path=Path(path).name,bytes=Path(path).stat().st_size,
                sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())

def deliver(out, recipe, cameras, modules):
    out=Path(out); (out/'renders').mkdir()
    objects=[o for o in bpy.context.scene.objects if o.get('public_realm_model')]
    # Individual modules remain rigid; the assembled GLB is an inspection fixture.
    assets={}
    for name,obs in modules.items():assets[name]=export(out/(name+'.glb'),obs)
    recipe['assets']=assets
    preview=export(out/'assembly-preview.glb',objects)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(out/'assembly-preview.glb'))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
    bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
    triangles=sum(len(o.data.loop_triangles) for o in meshes)
    # Imported mesh triangles must be calculated, not inferred from source objects.
    for o in meshes:o.data.calc_loop_triangles()
    triangles=sum(len(o.data.loop_triangles) for o in meshes)
    scene=bpy.context.scene; scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.world.color=(.55,.55,.55)
    bpy.ops.object.light_add(type='SUN',location=(0,0,50));sun=bpy.context.object
    sun.rotation_euler=(.35,-.4,-.5);sun.data.energy=2
    bpy.ops.object.light_add(type='AREA',location=(0,-15,40));bpy.context.object.data.energy=4500;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=45
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
    for name,pos,target,scale in cameras:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.data.clip_end=1000
        scene.render.filepath=str(out/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
    recipe.update(preview=preview,bounds_m=bounds,triangles=triangles,render_source='reimported assembly-preview.glb',
                  runtime_approved=False,independent_review='not performed',builder_review='pending')
    save_json(out/'recipe.json',recipe)
    print('MODEL_COMPLETE',preview['sha256'],triangles,flush=True)
