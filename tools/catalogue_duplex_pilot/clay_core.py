"""RLASM clay-only construction, actual-GLB rendering and evidence utilities.

Low-level box/prism/normals, camera-fit and role-merge patterns adapted from
London Mews v005's clay_utilities.py (SHA recorded in batch provenance).
No building composition, dimensions or opening schedule is inherited.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import time

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
METHOD='RLASM v6.1 clay-first'
MATS={}
CONTACTS=[]
OPENINGS=[]
MODULES={}

def utc(): return datetime.now(timezone.utc).isoformat()
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
def read_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def entry_for(archetype_id):
    """Replay a preserved package from its own exact copied sources."""
    if (ROOT/'source-entry.json').is_file():
        entry=read_json(ROOT/'source-entry.json')
        assert entry['archetype_id']==archetype_id
        entry['_reference_root']=str(ROOT/'sources')
        return entry
    return next(e for e in read_json(ROOT/'batch-progress.json')['candidates'] if e['archetype_id']==archetype_id)

def remove_cutter(cutter):
    name=cutter.name
    bpy.data.objects.remove(cutter,do_unlink=True)
    MODULES['construction cutter'].remove(name)
    if not MODULES['construction cutter']:del MODULES['construction cutter']

def tag(obj,role,module):
    obj['rlasm_building_object']=True
    obj['rlasm_method']=METHOD
    obj['cityprompt_semantic_role']=role
    obj['cityprompt_lego_module']=module
    obj['representation_kind']='architectural_clay'
    obj['native_geometry_only']=True
    MODULES.setdefault(module,[]).append(obj.name)
    return obj

def normalise(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()

def bevel(obj,width=.012,segments=1):
    if width<=0:return
    bpy.context.view_layer.objects.active=obj
    m=obj.modifiers.new('Construction edge chamfer','BEVEL');m.width=width;m.segments=segments;m.limit_method='ANGLE'
    bpy.ops.object.modifier_apply(modifier=m.name)

def mesh(name,vs,fs,role='wall',module='envelope',soft=0):
    data=bpy.data.meshes.new(name+' mesh');data.from_pydata(vs,[],fs);normalise(data)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(MATS[role]);tag(obj,role,module)
    bevel(obj,soft)
    return obj

BOX_FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,loc,size,role='wall',module='envelope',soft=.008):
    x,y,z=loc;a,b,c=[s/2 for s in size]
    assert min(size)>0,(name,size)
    vs=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
        (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    return mesh(name,vs,BOX_FACES,role,module,soft)

def prism(name,points,axis,low,high,role='wall',module='envelope',soft=0):
    # Explicit two-dimensional polygon, extruded along one named global axis.
    def point(p,a):
        return (a,p[0],p[1]) if axis=='x' else (p[0],a,p[1]) if axis=='y' else (p[0],p[1],a)
    n=len(points);vs=[point(p,a) for a in (low,high) for p in points]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,role,module,soft)

def solid_surface(name,outline,thickness,role='roof',module='roof'):
    vs=list(outline)+[(x,y,z-thickness) for x,y,z in outline];n=len(outline)
    fs=[tuple(range(n)),tuple(range(n*2-1,n-1,-1))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    return mesh(name,vs,fs,role,module)

def rod(name,a,b,r=.025,role='hardware',module='hardware',sides=12):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized()
    side=axis.cross(Vector((0,0,1)))
    if side.length<1e-6:side=axis.cross(Vector((0,1,0)))
    side.normalize();up=axis.cross(side).normalized()
    vs=[tuple(p+r*(math.cos(i*math.tau/sides)*side+math.sin(i*math.tau/sides)*up)) for p in (a,b) for i in range(sides)]
    fs=[tuple(range(sides-1,-1,-1)),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    obj=mesh(name,vs,fs,role,module)
    for f in obj.data.polygons[2:]: f.use_smooth=True
    return obj

def beam(name,a,b,width=.05,depth=None,role='hardware',module='structure',soft=0):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();depth=depth or width
    side=axis.cross(Vector((0,0,1)))
    if side.length<1e-6:side=axis.cross(Vector((0,1,0)))
    side.normalize();up=axis.cross(side).normalized()
    vs=[tuple(p+side*u*width/2+up*v*depth/2) for p in (a,b) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,vs,BOX_FACES,role,module,soft)

def cut_box(owner,name,loc,size):
    cutter=box(name,loc,size,'wall','construction cutter',0)
    cutter.data.materials.clear();cutter.data.materials.append(owner.data.materials[0])
    bpy.context.view_layer.objects.active=owner
    m=owner.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name)
    remove_cutter(cutter)
    normalise(owner.data)

class Face:
    """Metric face coordinates: u along wall, d inward, z vertical."""
    def __init__(self,origin,tangent,inward,label):
        self.o=Vector(origin);self.t=Vector(tangent);self.n=Vector(inward);self.label=label
    def p(self,u,d,z): return tuple(self.o+self.t*u+self.n*d+Vector((0,0,z)))
    def part(self,name,u,d,z,w,t,h,role='trim',module='openings',soft=.005):
        vs=[self.p(u+du*w/2,d+dd*t/2,z+dz*h/2) for dz in (-1,1) for du,dd in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        return mesh(name,vs,BOX_FACES,role,module,soft)
    def panel(self,name,poly,d0,d1,role='wall',module='envelope'):
        n=len(poly);vs=[self.p(u,d,z) for d in (d0,d1) for u,z in poly]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        return mesh(name,vs,fs,role,module)
    def cut(self,owner,name,u,z,w,h,depth=.5):
        cutter=self.part(name,u,depth/2,z+h/2,w,depth+1,h,'wall','construction cutter',0)
        cutter.data.materials.clear();cutter.data.materials.append(owner.data.materials[0])
        bpy.context.view_layer.objects.active=owner
        m=owner.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
        bpy.ops.object.modifier_apply(modifier=m.name);remove_cutter(cutter);normalise(owner.data)
    def wall(self,name,u0,u1,z0,z1,depth=.27,role='wall',holes=()):
        obj=self.part(name,(u0+u1)/2,depth/2,(z0+z1)/2,u1-u0,depth,z1-z0,role,'envelope',0)
        obj['rlasm_wall_carrier']=True
        for h in holes:
            if h['u']+h['w']/2>u0 and h['u']-h['w']/2<u1 and h['z']<z1 and h['z']+h['h']>z0:
                self.cut(obj,h['id']+' full carrier cut',h['u'],h['z'],h['w'],h['h'],depth)
        return obj
    def window(self,ident,u,z,w,h,cols=2,rows=1,frame='trim',inset=.14,bar=.045,sill=True,curtain=False,depth=.27,kind='window'):
        # Clear hole dimensions are w x h. All frames and glazing sit INSIDE it.
        module=f'{self.label}.{ident}'
        per=.065
        for side in (-1,1):
            self.part(ident+' recessed jamb',u+side*(w/2-per/2),inset,z+h/2,per,.11,h,frame,module)
        for vz in (z+per/2,z+h-per/2):
            self.part(ident+' recessed head or sill',u,inset,vz,w-per,.11,per,frame,module)
        for i in range(1,cols):
            self.part(ident+f' mullion {i}',u-w/2+w*i/cols,inset-.008,z+h/2,bar,.09,h-per*2,frame,module,.003)
        for i in range(1,rows):
            self.part(ident+f' transom {i}',u,inset-.012,z+h*i/rows,w-per*2,.085,bar,frame,module,.003)
        for c in range(cols):
            for r in range(rows):
                cw=w/cols;ch=h/rows
                self.part(ident+f' optical pane {c}-{r}',u-w/2+cw*(c+.5),inset+.037,z+ch*(r+.5),cw-.065,.009,ch-.065,'glass',module,0)
        if sill:
            self.part(ident+' bearing sill',u,.015,z-.035,w+.14,.39,.07,frame,module,.006)
        if curtain:
            # Selective actual curtain panels, well inside the common room.
            for s in (-1,1):
                self.part(ident+' inset curtain',u+s*w*.37,.48,z+h*.49,w*.16,.018,h*.91,'interior',module,0)
        OPENINGS.append(dict(id=ident,face=self.label,u=u,z=z,width=w,height=h,kind=kind,
            clear_wall_cut=True,carrier_depth_m=depth,frame_inset_m=inset,pane_inset_m=inset+.037,
            face_origin=list(self.o),face_tangent=list(self.t),face_inward=list(self.n),
            occupied_space='common enclosed room behind carrier; no texture cards',cols=cols,rows=rows))
    def door(self,ident,u,z,w,h,role='timber',inset=.19,panels=4,glazed=False,panel_cols=1):
        module=f'{self.label}.{ident}'
        if glazed:
            self.window(ident,u,z,w,h,1,2,role,inset,sill=False,kind='glazed door');return
        for side in (-1,1): self.part(ident+' jamb',u+side*(w/2-.035),inset,z+h/2,.07,.13,h,'trim',module)
        self.part(ident+' head',u,inset,z+h-.035,w,.13,.07,'trim',module)
        self.part(ident+' recessed leaf',u,inset+.035,z+h/2-.02,w-.13,.055,h-.05,role,module,.004)
        for i in range(panels):
            ph=(h-.25)/panels;pw=(w-.28)/panel_cols
            for col in range(panel_cols):
                self.part(ident+f' door panel {col}-{i}',u-(w-.28)/2+pw*(col+.5),inset-.008,z+.12+ph*(i+.5),pw-.045,.025,ph-.11,role,module,.005)
        self.part(ident+' threshold',u,.07,z-.020,w+.06,.38,.055,'trim',module,0)
        pa=self.p(u+w*.30,inset-.065,z+h*.45)
        rod(ident+' handle',(pa[0],pa[1],pa[2]-.075),(pa[0],pa[1],pa[2]+.075),.015,'hardware',module,10)
        OPENINGS.append(dict(id=ident,face=self.label,u=u,z=z,width=w,height=h,kind='opaque operable door',clear_wall_cut=True,carrier_depth_m=.29,frame_inset_m=inset,pane_inset_m=None,
            face_origin=list(self.o),face_tangent=list(self.t),face_inward=list(self.n),occupied_space='enclosed room beyond door'))

def railing(name,a,b,height=1.02,spacing=.105,role='trim',bottom=.07,end_posts=True):
    a,b=Vector(a),Vector(b);length=(b-a).length;count=max(1,round(length/spacing))
    beam(name+' top rail',a+Vector((0,0,height)),b+Vector((0,0,height)),.042,.038,role,name,.004)
    beam(name+' bottom rail',a+Vector((0,0,bottom)),b+Vector((0,0,bottom)),.028,.025,role,name,.002)
    for i in range(count+1):
        if not end_posts and i in (0,count):continue
        p=a.lerp(b,i/count)
        w=.039 if i in (0,count) else .018
        beam(name+f' picket {i}',p+Vector((0,0,bottom)),p+Vector((0,0,height)),w,w,role,name,.001)

def look_at(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def qa_room_light(name,location,power=100,size=2.4):
    """Neutral inspection illumination, never a delivered emissive surface."""
    bpy.ops.object.light_add(type='AREA',location=location)
    obj=bpy.context.object;obj.name='QA interior '+name
    obj.data.energy=power;obj.data.shape='DISK';obj.data.size=size
    look_at(obj,(location[0],location[1],location[2]-1))
    return obj

def setup(palette,cameras,resolution=1440):
    global MATS,CONTACTS,OPENINGS,MODULES
    CONTACTS=[];OPENINGS=[];MODULES={}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.cycles.max_bounces=7;scene.cycles.transparent_max_bounces=8
    # Use the available local GPU without saving application preferences. CPU fallback.
    try:
        cp=bpy.context.preferences.addons['cycles'].preferences
        cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        if any(d.use for d in cp.devices):scene.cycles.device='GPU'
    except Exception as error:
        print('Local GPU unavailable; using CPU: '+str(error),flush=True)
    scene.render.threads_mode='FIXED';scene.render.threads=6
    scene.render.resolution_x=resolution;scene.render.resolution_y=round(resolution*.75);scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    world=bpy.data.worlds.new('Neutral architectural review world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.59,.63,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55;scene.world=world
    MATS={}
    for role,value in palette.items():
        mat=bpy.data.materials.new('CLAY_'+role.upper());mat.use_nodes=True
        mat['cityprompt_semantic_role']=role;mat['texture_free']=True
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*value[:3],1)
        bs.inputs['Roughness'].default_value=.78 if role not in ('glass','hardware') else .24 if role=='glass' else .52
        mat.diffuse_color=(*value[:3],1)
        if role=='glass':
            bs.inputs['Alpha'].default_value=.32;bs.inputs['Transmission Weight'].default_value=.28;bs.inputs['IOR'].default_value=1.45
            mat.surface_render_method='DITHERED'
        MATS[role]=mat
    groundmat=bpy.data.materials.new('Review ground not exported');groundmat.diffuse_color=(.56,.57,.55,1)
    groundmat.use_nodes=True;groundmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.56,.57,.55,1)
    groundmat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));g=bpy.context.object;g.name='QA ground - excluded';g.data.materials.append(groundmat)
    for label,loc,power,size in [('key',(-9,-13,18),1800,10),('fill',(13,-5,14),1350,9),('rear',(-6,14,16),1800,10)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='QA '+label;o.data.energy=power;o.data.shape='DISK';o.data.size=size;look_at(o,(0,0,3.5))
    cams={}
    for spec in cameras:
        bpy.ops.object.camera_add(location=spec['location']);o=bpy.context.object;o.name='QA '+spec['name'];o.data.lens=spec.get('lens',52);o.data.clip_end=500
        if spec.get('ortho_scale'):o.data.type='ORTHO';o.data.ortho_scale=spec['ortho_scale']
        look_at(o,spec['target']);cams[spec['name']]=o
    return cams

def objects():return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('rlasm_building_object')]
def bounds(items):
    pts=[o.matrix_world@v.co for o in items for v in o.data.vertices]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def metrics(items):
    for o in items:o.data.calc_loop_triangles()
    return dict(mesh_objects=len(items),vertices=sum(len(o.data.vertices) for o in items),polygons=sum(len(o.data.polygons) for o in items),triangles=sum(len(o.data.loop_triangles) for o in items))
def fit(camera,target,margin=.075):
    scene=bpy.context.scene;bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in objects() for v in o.data.vertices]
    # Finite camera search is framing, not a geometry-generation correction loop.
    for _ in range(80):
        bpy.context.view_layer.update();q=[world_to_camera_view(scene,camera,p) for p in pts]
        if all(p.z>0 and margin<=p.x<=1-margin and margin<=p.y<=1-margin for p in q):break
        if camera.data.type=='ORTHO':camera.data.ortho_scale*=1.045
        else:camera.location=Vector(target)+(camera.location-Vector(target))*1.045
    else:raise RuntimeError('Unable to fit '+camera.name)
    return dict(xmin=min(p.x for p in q),xmax=max(p.x for p in q),ymin=min(p.y for p in q),ymax=max(p.y for p in q))
def glb_json(p):
    data=Path(p).read_bytes();magic,v,total=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and v==2 and total==len(data)
    n,kind=struct.unpack_from('<II',data,12);assert kind==0x4E4F534A
    return json.loads(data[20:20+n])

def aperture_audit():
    """Nine through-carrier rays per opening; frames/glass excluded on purpose."""
    carriers=[o for o in objects() if o.get('rlasm_wall_carrier')]
    vertices=[];faces=[]
    for o in carriers:
        offset=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in o.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
    checks=[]
    for op in OPENINGS:
        o=Vector(op['face_origin']);t=Vector(op['face_tangent']);n=Vector(op['face_inward'])
        failures=[]
        for fu in (-.27,0,.27):
            for fz in (.22,.5,.78):
                start=o+t*(op['u']+fu*op['width'])+Vector((0,0,op['z']+fz*op['height']))-n*.06
                loc,normal,index,distance=tree.ray_cast(start,n,op['carrier_depth_m']+.14)
                if loc is not None:failures.append(dict(sample=[fu,fz],distance_m=distance,point=list(loc)))
        checks.append(dict(opening=op['id'],face=op['face'],ray_count=9,blocked_samples=failures))
    return dict(status='PASS_CARRIER_APERTURES' if all(not x['blocked_samples'] for x in checks) else 'FAIL_CARRIER_APERTURES',
        scope='Opaque facade carriers only. Does not prove room access, structural adequacy or visual glass depth.',checks=checks)

def prepare_candidate(a,entry,manifest,build_script,extra_scripts=()):
    out=Path(a.output).resolve();assert str(out).startswith('C:\\dev-artifacts\\CityPrompt\\') or str(out).startswith('C:/dev-artifacts/CityPrompt/')
    if a.dry_run:
        for s in entry['sources']:
            f=Path(entry['_reference_root'])/Path(s['original_path']).name if entry.get('_reference_root') else Path(s['original_path'])
            assert f.stat().st_size==s['bytes'] and digest(f)==s['sha256']
        print(json.dumps(dict(dry_run=True,no_geometry_written=True,sources=len(entry['sources']),cameras=len(manifest['camera_roster']),candidate=manifest['candidate'])),flush=True)
        return None
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'): (out/name).mkdir()
    for s in entry['sources']:
        f=(Path(entry['_reference_root']) if entry.get('_reference_root') else ROOT/entry['directory']/'references')/Path(s['original_path']).name
        if not f.is_file():f=Path(s['original_path'])
        dest=out/s['path'];shutil.copy2(f,dest)
        assert dest.stat().st_size==s['bytes'] and digest(dest)==s['sha256']
    for p in [Path(__file__),Path(build_script),*map(Path,extra_scripts)]:shutil.copy2(p,out/'scripts'/p.name)
    write_json(out/'source-entry.json',{k:v for k,v in entry.items() if k not in ('_reference_root','versions','runtime')})
    manifest['source_contract']={'sources':entry['sources'],'exact_variant_only':True,'no_generated_substitute_references':True}
    manifest['provenance']={'scripts':[dict(path='scripts/'+p.name,sha256=digest(out/'scripts'/p.name)) for p in [Path(__file__),Path(build_script),*map(Path,extra_scripts)]],
        'blender_version':bpy.app.version_string,'python_version':sys.version,'generation_api_calls':0,'build_started_utc':utc(),'render_source':'actual optimized GLB reimport only'}
    write_json(out/'prework-manifest.json',manifest)
    # Snapshot prior progress before every significant checkpoint; completed candidates immutable.
    progress_path=ROOT/'batch-progress.json'
    if progress_path.is_file():
        progress=read_json(progress_path);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        write_json(ROOT/'checkpoints'/f'{stamp}-before-{manifest["candidate"]}.json',progress)
        for c in progress['candidates']:
            if c['archetype_id']==entry['archetype_id']:
                c['status']='building';c.setdefault('started_utc',utc());c['current_candidate']=manifest['candidate'];c['current_directory']=str(out)
                c['versions'].append(dict(candidate=manifest['candidate'],path=str(out),started_utc=utc(),status='building'))
        progress['updated_utc']=utc();progress['status']='building'
        with progress_path.open('w',encoding='utf-8') as f:json.dump(progress,f,indent=2,ensure_ascii=False)
    return out

def deliver(out,manifest,cameras):
    started=time.monotonic();scene=bpy.context.scene;bpy.context.view_layer.update()
    authored=objects();original=bounds(authored);author_metrics=metrics(authored)
    assert abs(original[0][2])<.0001,original
    for o in authored:o['archetype_id']=manifest['archetype_id'];o['variant_id']=manifest['variant_id']
    camera_report={}
    for spec in manifest['camera_roster']:
        if spec.get('whole',True):camera_report[spec['name']]=fit(cameras[spec['name']],spec['target'])
    detail_report={}
    for spec in manifest['camera_roster']:
        if spec.get('proof_points'):
            cam=cameras[spec['name']];bpy.context.view_layer.update()
            q=[world_to_camera_view(scene,cam,Vector(p)) for p in spec['proof_points']]
            assert all(p.z>0 and .05<p.x<.95 and .05<p.y<.95 for p in q),'Contact landmarks clipped in '+spec['name']
            detail_report[spec['name']]=dict(world_points=spec['proof_points'],projected=[list(p) for p in q],minimum_margin=.05,passed=True,
                limitation='Framing proof only; independent pixel review must still check occlusion and illumination')
    scene.camera=cameras['front_corner']
    blend=out/(manifest['candidate']+'-authoring.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    aperture_report=aperture_audit();write_json(out/'evidence/carrier-aperture-audit.json',aperture_report)
    # Editable component source is now preserved. Delivery changes only this in-memory copy.
    groups={}
    for role in MATS:
        items=[o for o in objects() if o.get('cityprompt_semantic_role')==role]
        if not items:continue
        groups[role]=len(items);bpy.ops.object.select_all(action='DESELECT')
        for o in items:o.select_set(True)
        bpy.context.view_layer.objects.active=items[0]
        if len(items)>1:bpy.ops.object.join()
        o=bpy.context.object;o.name='CLAY_'+role.upper();o['source_component_count']=len(items)
    bpy.context.view_layer.update();delivery_metrics=metrics(objects())
    glb=out/(manifest['candidate']+'.glb');bpy.ops.object.select_all(action='DESELECT')
    for o in objects():o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_materials='EXPORT',
        export_extras=True,export_cameras=False,export_lights=False,export_yup=True,export_texcoords=False,export_normals=True)
    payload=glb_json(glb);assert not payload.get('textures') and not payload.get('images')
    for o in list(objects()):bpy.data.objects.remove(o,do_unlink=True)
    before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=[o for o in scene.objects if o not in before and o.type=='MESH']
    for o in imported:o['rlasm_building_object']=True
    bpy.context.view_layer.update();actual=bounds(imported)
    delta=max(abs(original[a][b]-actual[a][b]) for a in range(2) for b in range(3));assert delta<.0001,delta
    # No material override is permitted after export: all QA shows delivered geometry AND material.
    for spec in manifest['camera_roster']:
        name=spec['name'];scene.camera=cameras[name]
        if spec.get('whole',True):camera_report[name]=fit(scene.camera,spec['target'])
        path=out/'renders'/(name+'.png');assert not path.exists()
        scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        print('RENDER_COMPLETE '+name,flush=True)
    report=dict(candidate=manifest['candidate'],status='build_valid',representation_kind='architectural_clay',
        authoring=dict(author_metrics,path=blend.name,bytes=blend.stat().st_size,sha256=digest(blend)),
        runtime=dict(path=glb.name,bytes=glb.stat().st_size,sha256=digest(glb),meshes=len(payload.get('meshes',[])),
            materials=len(payload.get('materials',[])),textures=len(payload.get('textures',[])),images=len(payload.get('images',[])),**delivery_metrics),
        original_bounds_m=original,delivered_bounds_m=actual,max_roundtrip_delta_m=delta,
        design_dimensions_m=manifest['measurement_contract']['dimensions_m'],
        native_dimensions_m=dict(width=actual[1][0]-actual[0][0],depth=actual[1][1]-actual[0][1],height=actual[1][2]-actual[0][2]),
        native_bottom_center_m=[(actual[0][0]+actual[1][0])/2,(actual[0][1]+actual[1][1])/2,actual[0][2]],source_components_by_role=groups,
        render_source='actual optimized GLB reimport; no geometry/material replacement',renders=[f'renders/{s["name"]}.png' for s in manifest['camera_roster']],
        render_resolution=[scene.render.resolution_x,scene.render.resolution_y],render_engine=scene.render.engine,render_device=scene.cycles.device,camera_safety_margin=camera_report,detail_camera_landmarks=detail_report,
        contacts=CONTACTS,opening_sections=OPENINGS,authoring_modules=MODULES,
        carrier_aperture_audit=aperture_report['status'],
        finished_utc=utc(),delivery_and_render_seconds=time.monotonic()-started,
        keeper_claimed=False,runtime_seed_allowed=False,runtime_imported=False,scaling_verified=False,
        independent_review='pending',builder_visual_review='pending')
    write_json(out/'build-report.json',report)
    write_json(out/'evidence/builder-evidence.json',dict(report,generic_fallback_count=0,
        material_scope='Intentionally untextured source-palette semantic clay; source-specific PBR and final textures omitted by design'))
    print('BUILD_COMPLETE '+json.dumps(dict(candidate=manifest['candidate'],runtime=report['runtime'],bounds=actual,delta=delta)),flush=True)
    return report

def args():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1)
    p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    return p.parse_args(argv)
