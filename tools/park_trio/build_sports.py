"""Finite metric sports batch. Blender --background --python ... -- --sport basketball --output-dir ...

No image API calls. Dimensions shared with the runtime; separate mesh materials
carry markings, so generated paint cannot move a goal or alter a playing area.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SPECS = json.loads((ROOT / 'frontend/src/data/sportsParkDimensions.json').read_text())
PALETTE = {'asphalt': (.065,.09,.105), 'blue': (.075,.29,.43), 'teal': (.045,.23,.20),
           'red': (.43,.17,.105), 'grass': (.20,.34,.105), 'stripe': (.25,.39,.14),
           'white': (.92,.93,.86), 'steel': (.065,.08,.085), 'net': (.30,.34,.32),
           'orange': (.9,.23,.035), 'glass': (.37,.55,.59)}
GEOMETRY = {}


def mesh_piece(material, vertices, faces):
    vv, ff = GEOMETRY.setdefault(material, ([], []))
    offset = len(vv)
    vv.extend(vertices)
    ff.extend(tuple(i+offset for i in face) for face in faces)


def box(material, x, y, z, w, d, h):
    mesh_piece(material, [(x+sx*w/2,y+sy*d/2,z+sz*h/2) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)],
               [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])


def beam(material, a, b, radius=.025, sides=6):
    a,b=Vector(a),Vector(b); rotation=(b-a).to_track_quat('Z','Y')
    vertices=[tuple(p+rotation@Vector((radius*math.cos(i*math.tau/sides),radius*math.sin(i*math.tau/sides),0))) for p in (a,b) for i in range(sides)]
    mesh_piece(material,vertices,[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]+[tuple(reversed(range(sides))),tuple(range(sides,2*sides))])


def line(a,b,width=.05,z=.014):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length<1e-8:return
    nx,ny=-dy/length*width/2,dx/length*width/2
    mesh_piece('white',[(a[0]+nx,a[1]+ny,z),(a[0]-nx,a[1]-ny,z),(b[0]-nx,b[1]-ny,z),(b[0]+nx,b[1]+ny,z)],[(0,1,2,3)])


def rectangle(x,y,w,d,width=.05):
    points=[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)]
    for a,b in zip(points,points[1:]+points[:1]):line(a,b,width)


def arc(x,y,r,start=0,end=math.tau,width=.05):
    n=max(12,int(abs(end-start)*22));p=[(x+r*math.cos(start+(end-start)*i/n),y+r*math.sin(start+(end-start)*i/n)) for i in range(n+1)]
    for a,b in zip(p,p[1:]):line(a,b,width)


def fence(w,d,height=3):
    # South-side gate is deliberately open, with no wire or rail across it.
    segments=[((-w/2,-d/2),(-1.1,-d/2)),((1.1,-d/2),(w/2,-d/2)),((w/2,-d/2),(w/2,d/2)),((w/2,d/2),(-w/2,d/2)),((-w/2,d/2),(-w/2,-d/2))]
    for a,b in segments:
        length=math.dist(a,b); n=math.ceil(length/2.5)
        for i in range(n+1):
            t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            beam('steel',(x,y,0),(x,y,height),.047)
        for z in (.12,height):beam('steel',(*a,z),(*b,z),.025)
        n=math.ceil(length/.20)
        for i in range(n+1):
            t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            beam('net',(x,y,.15),(x,y,height-.03),.007,4)
        for i in range(1,int(height/.2)):
            beam('net',(*a,i*.2),(*b,i*.2),.007,4)


def basketball():
    box('teal',0,0,-.02,36,23,.04);box('blue',0,0,.002,28,15,.004)
    # Boundary dimensions are measured to their inside edges for basketball.
    rectangle(0,0,28.05,15.05);line((0,-7.5),(0,7.5));arc(0,0,1.8)
    for s in (-1,1):
        box('red',s*11.1,0,.006,5.8,4.9,.005)
        rectangle(s*11.1,0,5.8,4.9);arc(s*8.2,0,1.8)
        # Three-point arc meets the parallel corner lines 0.9 m from sidelines.
        theta=math.asin(6.6/6.75);center=s*12.425;delta=math.sqrt(6.75**2-6.6**2)
        if s<0:arc(center,0,6.75,-theta,theta)
        else:arc(center,0,6.75,math.pi-theta,math.pi+theta)
        for y in (-6.6,6.6):line((s*14,y),(center-s*delta,y))
        beam('steel',(s*16.4,0,0),(s*16.4,0,3.6),.13,10)
        beam('steel',(s*16.4,0,3.6),(s*12.8,0,3.6),.095,8)
        beam('steel',(s*16.4,0,2.2),(s*13.7,0,3.6),.055,8)
        box('glass',s*12.8,0,3.425,.065,1.8,1.05)
        # Rim top is 3.05 m. Ring and hanging net retain true physical scale.
        cx=s*12.425
        for i in range(48):
            a=i*math.tau/48;b=(i+1)*math.tau/48
            beam('orange',(cx+.225*math.cos(a),.225*math.sin(a),3.04),(cx+.225*math.cos(b),.225*math.sin(b),3.04),.01)
        for i in range(12):
            a=i*math.tau/12
            beam('white',(cx+.225*math.cos(a),.225*math.sin(a),3.03),(cx+.14*math.cos(a+.2),.14*math.sin(a+.2),2.62),.006,4)
        for y in (-.9,.9):box('white',s*12.84,y,3.425,.03,.025,1.05)
        for z in (2.9,3.95):box('white',s*12.84,0,z,.03,1.8,.025)
    fence(35.6,22.6)


def tennis():
    box('teal',0,0,-.02,38,20,.04);box('blue',0,0,.002,23.77,10.97,.004)
    # Tennis dimensions include the outside of the boundary lines.
    rectangle(0,0,23.72,10.92)
    for y in (-4.115,4.115):line((-11.885,y),(11.885,y))
    for x in (-6.4,6.4):line((x,-4.115),(x,4.115))
    line((-6.4,0),(6.4,0))
    for x in (-11.86,11.86):line((x,0),(x-math.copysign(.10,x),0))
    for y in (-6.399,6.399):beam('steel',(0,y,0),(0,y,1.07),.045,10)
    for i in range(129):
        y=-6.399+12.798*i/128;top=.914+.156*(abs(y)/6.399)**2
        beam('net',(0,y,.04),(0,y,top),.006,4)
        if i<128:
            y2=y+12.798/128;top2=.914+.156*(abs(y2)/6.399)**2
            beam('white',(0,y,top),(0,y2,top2),.021,6)
    for z in (.15,.3,.45,.6,.75,.9):beam('net',(0,-6.399,z),(0,6.399,z),.006,4)
    box('white',0,0,.457,.035,.05,.914)
    fence(37.6,19.6)


def soccer():
    box('grass',0,0,-.02,117,80,.04)
    for i in range(14):
        box('stripe' if i%2 else 'grass',-52.5+(i+.5)*7.5,0,.002,7.5,68,.004)
    rectangle(0,0,104.88,67.88,.12);line((0,-34),(0,34),.12);arc(0,0,9.15,width=.12);arc(0,0,.12,width=.12)
    for s in (-1,1):
        for reach,span in ((16.5,40.32),(5.5,18.32)):
            x=s*(52.5-reach)
            line((s*52.5,-span/2),(x,-span/2),.12);line((x,-span/2),(x,span/2),.12);line((x,span/2),(s*52.5,span/2),.12)
        arc(s*41.5,0,.12,width=.12)
        theta=math.acos(5.5/9.15)
        arc(s*41.5,0,9.15,(-theta if s<0 else math.pi-theta),(theta if s<0 else math.pi+theta),.12)
        # Inside clear goal opening 7.32 × 2.44 m; posts are 0.12 m thick.
        x=s*52.5;rear=x+s*2.2
        for y in (-3.72,3.72):
            beam('white',(x,y,.06),(x,y,2.5),.06,10)
            beam('white',(x,y,2.5),(rear,y,.12),.025)
        beam('white',(x,-3.72,2.5),(x,3.72,2.5),.06,10)
        for i in range(39):
            y=-3.66+i*7.32/38
            beam('net',(x,y,2.44),(rear,y,.12),.008,4)
        for j in range(14):
            t=j/13;beam('net',(x+s*2.2*t,-3.66,2.44-2.32*t),(x+s*2.2*t,3.66,2.44-2.32*t),.008,4)
        for y in (-3.66,3.66):
            for j in range(1,12):
                z=j*.2;end=s*(52.5+2.2*(2.44-z)/2.32)
                beam('net',(x,y,z),(end,y,z),.008,4)
        for y in (-34,34):
            beam('white',(s*52.5,y,0),(s*52.5,y,1.5),.015)
            box('orange',s*52.5+.15,y,1.37,.30,.015,.24)
            start=0 if s<0 and y<0 else math.pi/2 if s>0 and y<0 else math.pi if s>0 else math.pi*1.5
            arc(s*52.5,y,1,start,start+math.pi/2,.12)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sport',choices=SPECS,required=True)
    parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);spec=SPECS[args.sport]
    if args.dry_run:print(json.dumps({'sport':args.sport,**spec,'paidCalls':0}));return
    out=args.output_dir
    if out.exists() and any(out.iterdir()):raise RuntimeError('Use a new revision directory; existing outputs are preserved.')
    out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    globals()[args.sport]()
    for name,(vertices,faces) in GEOMETRY.items():
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
        mat=bpy.data.materials.new(name);mat.diffuse_color=(*PALETTE[name],1);mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*PALETTE[name],1)
        shader.inputs['Roughness'].default_value=.87 if name not in ('steel','glass') else .35
        shader.inputs['Metallic'].default_value=.6 if name=='steel' else 0
        mesh.materials.append(mat)
        # Every module seats at its lowest physical vertex.
        obj.location.z=.04
    bpy.ops.object.select_all(action='SELECT')
    glb=out/'court.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True)
    # Re-import actual delivered bytes before reporting bounds and rendering.
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
    # glTF importer restores Blender Z-up.
    assert abs(low[2])<.001,low
    assert high[0]-low[0]<=spec['module'][0]+.001
    assert high[1]-low[1]<=spec['module'][1]+.001
    (out/'manifest.json').write_text(json.dumps({'sport':args.sport,**spec,'sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'bytes':glb.stat().st_size,'reimportBounds':[low,high],'meshes':len(objs),'triangles':sum(len(p.vertices)-2 for o in objs for p in o.data.polygons),'paidCalls':0},indent=2))
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.world.color=(.45,.45,.45)
    bpy.ops.object.light_add(type='AREA',location=(0,-20,60));bpy.context.object.data.energy=60000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=40
    bpy.ops.object.light_add(type='SUN',location=(0,0,30));bpy.context.object.rotation_euler=(.3,-.4,-.5);bpy.context.object.data.energy=2
    w,d=spec['module'];bpy.ops.object.camera_add(location=(w*.65,-d*1.0,max(w,d)*.85));camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=max(w,d)*1.32;scene.camera=camera
    scene.render.resolution_x=1000;scene.render.resolution_y=750;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'preview.png');bpy.ops.render.render(write_still=True)
    print(json.dumps({'complete':args.sport,'output':str(out)}))


if __name__=='__main__':main()
