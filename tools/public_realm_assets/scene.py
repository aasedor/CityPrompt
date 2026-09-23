"""Deterministic metre/Z-up public-realm assets. No catalogue or provider writes."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector

MATS={}; KIT={}; PLACEMENTS=[]; RIGID={}; SURFACES=[]; GROUND_SIZE=[]
def init(kit):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    PLACEMENTS.clear(); KIT.clear(); MATS.clear(); RIGID.clear(); SURFACES.clear(); GROUND_SIZE.clear()
    palette={'paving':(.53,.50,.43),'edge':(.35,.34,.29),'grass':(.21,.28,.105),
      'soil':(.105,.073,.045),'metal':(.035,.049,.045),'timber':(.32,.235,.15),
      'court':(.085,.235,.245),'runoff':(.19,.28,.255),'kitchen':(.28,.39,.34),
      'paint':(.86,.86,.77),'net':(.075,.09,.08),'cycle':(.33,.145,.085),
      'asphalt':(.10,.115,.11),'flower':(.35,.23,.38)}
    for n,c in palette.items():
        m=bpy.data.materials.new(n); m.diffuse_color=(*c,1);m.use_nodes=True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
        m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.86
        MATS[n]=m
    m=bpy.data.materials.new('kit_linear_vertex_colour'); m.use_nodes=True
    attr=m.node_tree.nodes.new('ShaderNodeVertexColor'); attr.layer_name='Color'
    m.node_tree.links.new(attr.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
    m.use_backface_culling=False;MATS['kit']=m
    for kind,parts in json.loads(Path(kit).read_text()).items():
        KIT[kind]=[]
        for part,g in parts.items():
            verts=list(zip(*[iter(g['position'])]*3)); ids=g['index'] or list(range(len(verts)))
            data=bpy.data.meshes.new(kind+'_'+part);data.from_pydata(verts,[],list(zip(*[iter(ids)]*3)));data.update()
            colors=data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
            rgba=[v for rgb in zip(*[iter(g['color'])]*3) for v in (*rgb,1)]
            colors.data.foreach_set('color',rgba);data.materials.append(m); KIT[kind].append(data)

def mesh(name,verts,faces,mat):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();m.materials.append(MATS[mat])
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o
def box(name,xyz,size,mat):
    x,y,z=xyz;w,d,h=[a/2 for a in size]
    return mesh(name,[(x+a*w,y+b*d,z+c*h) for c in (-1,1) for b in (-1,1) for a in (-1,1)],
      [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)
def beam(name,a,b,r,mat,sides=6):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();ref=Vector((0,0,1)) if abs(d.z)<.9 else Vector((1,0,0))
    u=d.cross(ref).normalized();v=d.cross(u);verts=[tuple(p+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v)) for p in (a,b) for i in range(sides)]
    return mesh(name,verts,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],mat)
def kit(kind,x=0,y=0,z=0,yaw=0,scale=1):
    result=[]
    for data in KIT[kind]:
        o=bpy.data.objects.new(kind,data);bpy.context.collection.objects.link(o);o.location=(x,y,z);o.rotation_euler.z=yaw;o.scale=(scale,)*3;result.append(o)
    PLACEMENTS.append(dict(kind=kind,x=x,y=y,z=z,yaw=yaw,scale=scale));return result
def line(a,b,width=.05,mat='paint',z=.012):
    dx,dy=b[0]-a[0],b[1]-a[1];r=math.hypot(dx,dy)
    if r<1e-8:return
    nx,ny=-dy/r*width/2,dx/r*width/2
    mesh('marking',[(a[0]+nx,a[1]+ny,z),(a[0]-nx,a[1]-ny,z),(b[0]-nx,b[1]-ny,z),(b[0]+nx,b[1]+ny,z)],[(0,1,2,3)],mat)
def arc(x,y,r,start=0,end=math.tau,width=.08):
    count=max(8,round(abs(end-start)*r*3))
    for i in range(count):
        a=start+(end-start)*i/count;b=start+(end-start)*(i+1)/count
        line((x+r*math.cos(a),y+r*math.sin(a)),(x+r*math.cos(b),y+r*math.sin(b)),width)
def rectline(x,y,w,d,width=.05):
    p=[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)]
    for a,b in zip(p,p[1:]+p[:1]):line(a,b,width)
def paving(x,y,w,d):
    box('paving',(x,y,-.06),(w,d,.12),'paving')
    # Fine joints in world metres; no outsized outlines.
    for i in range(1,int(d/.8)):
        yy=y-d/2+i*.8;line((x-w/2,yy),(x+w/2,yy),.009,'edge',.002)
    for i in range(1,int(w/1.2)):
        xx=x-w/2+i*1.2;line((xx,y-d/2),(xx,y+d/2),.009,'edge',.002)
def bed(x,y,w,d,trees=False,surface=True):
    if surface:box('planting soil',(x,y,-.055),(w,d,.11),'soil')
    for xx in (x-w/2,x+w/2):box('slender steel edging',(xx,y,.025),(.035,d,.05),'metal')
    for yy in (y-d/2,y+d/2):box('slender steel edging',(x,yy,.025),(w,.035,.05),'metal')
    for i in range(max(1,int(w/1.1))):
        for j in range(max(1,int(d/1.25))):
            xx=x-w/2+.6+i*1.1; yy=y-d/2+.65+j*1.25
            if trees and math.hypot(xx-x,yy-y)<.7:continue
            kind=['meadow_grass','flowering_perennial','silver_shrub'][(i+2*j)%3]
            kit(kind,xx,yy,0,(i+j)*2.4,.55 if kind=='silver_shrub' else .65)
def pergola(x,y,w=6,d=4):
    before=set(bpy.context.scene.objects)
    for dx in (-w/2+.15,w/2-.15):
        for dy in (-d/2+.15,d/2-.15):
            box('pergola base shoe',(x+dx,y+dy,.08),(.24,.24,.16),'metal')
            box('pergola post',(x+dx,y+dy,1.45),(.16,.16,2.9),'timber')
    for dy in (-d/2+.15,d/2-.15):box('pergola carrier',(x,y+dy,2.85),(w,.15,.28),'timber')
    for i in range(int(w/.32)+1):box('pergola louvre',(x-w/2+i*.32,y,3.06),(.07,d+.25,.20),'timber')
    kind=f'pergola-{w:g}x{d:g}'
    if kind not in RIGID:RIGID[kind]=(list(set(bpy.context.scene.objects)-before),x,y)
    PLACEMENTS.append(dict(kind=kind,x=x,y=y,z=0,yaw=0,scale=1))
def fence_segment(a,b,h=2.8):
    n=max(1,math.ceil(math.dist(a,b)/2.5))
    for i in range(n+1):
        x=a[0]+(b[0]-a[0])*i/n;y=a[1]+(b[1]-a[1])*i/n
        beam('fence post',(x,y,0),(x,y,h),.035,'metal',8)
    for z in (.12,h-.05):beam('fence rail',(*a,z),(*b,z),.024,'metal')
    # Light welded mesh, deliberately open rather than a dark solid wall.
    n=max(1,round(math.dist(a,b)/.2))
    for i in range(n+1):
        x=a[0]+(b[0]-a[0])*i/n;y=a[1]+(b[1]-a[1])*i/n
        beam('fence wire',(x,y,.1),(x,y,h-.1),.005,'net',4)
    for j in range(1,int(h/.25)):beam('fence wire',(*a,j*.25),(*b,j*.25),.005,'net',4)
def enclosure(w,d,h=2.8,gate_x=0):
    # South entrance is an actual two-metre opening, not a painted gate.
    for a,b in [((-w/2,-d/2),(gate_x-1,-d/2)),((gate_x+1,-d/2),(w/2,-d/2)),((w/2,-d/2),(w/2,d/2)),((w/2,d/2),(-w/2,d/2)),((-w/2,d/2),(-w/2,-d/2))]:fence_segment(a,b,h)
def ground(w,d,regions):
    """Partition rectangles so every ground cell has exactly one surface owner.

    Regions: (x,y,width,depth,material); last wins, None leaves a module opening.
    """
    SURFACES.extend([dict(x=x,y=y,width=rw,depth=rd,material=m) for x,y,rw,rd,m in regions])
    GROUND_SIZE[:] = [w,d]

def build_ground():
    w,d=GROUND_SIZE
    regions=[(r['x'],r['y'],r['width'],r['depth'],r['material']) for r in SURFACES]
    xs=sorted({-w/2,w/2,*[x+s*rw/2 for x,y,rw,rd,m in regions for s in (-1,1)]})
    ys=sorted({-d/2,d/2,*[y+s*rd/2 for x,y,rw,rd,m in regions for s in (-1,1)]})
    assert xs[0]>=-w/2 and xs[-1]<=w/2 and ys[0]>=-d/2 and ys[-1]<=d/2
    for a,b in zip(xs,xs[1:]):
        for c,e in zip(ys,ys[1:]):
            x,y=(a+b)/2,(c+e)/2;mat='grass'
            for rx,ry,rw,rd,rm in regions:
                if abs(x-rx)<rw/2 and abs(y-ry)<rd/2:mat=rm
            if mat=='paving':paving(x,y,b-a,e-c)
            elif mat:box(mat,(x,y,-.06),(b-a,e-c,.12),mat)

def surface_at(x,y):
    material='grass'
    for r in SURFACES:
        if abs(x-r['x'])<=r['width']/2 and abs(y-r['y'])<=r['depth']/2:material=r['material']
    return material

def prepare_tree_wells():
    """Every authored hardscape tree gets a root opening; existing soft beds win.

    Ground is emitted afterwards, so paving/joints never span these openings.
    Use the actual exported runtime kit, with independent metre-scale wells.
    """
    wells=[];w,d=GROUND_SIZE
    for tree in list(PLACEMENTS):
        if tree['kind'] not in ('shade_tree','grove_tree','ornamental_tree'):continue
        x,y=tree['x'],tree['y']
        support=[surface_at(x+dx,y+dy) for dx in (-.45,0,.45) for dy in (-.45,0,.45)]
        if all(m in ('grass','soil') for m in support):continue
        assert all(m in ('paving','grass','soil') for m in support),(tree,'tree intersects a protected surface')
        style='planted' if tree['kind']=='ornamental_tree' else 'grate'
        size=2.4 if style=='planted' else 1.8
        assert abs(x)+size/2<=w/2 and abs(y)+size/2<=d/2,(tree,'well outside plot')
        # Check complete rectangle, including internal surface region boundaries.
        xs={x-size/2,x+size/2,*[r['x']+sign*r['width']/2 for r in SURFACES for sign in (-1,1) if abs(r['x']+sign*r['width']/2-x)<size/2]}
        ys={y-size/2,y+size/2,*[r['y']+sign*r['depth']/2 for r in SURFACES for sign in (-1,1) if abs(r['y']+sign*r['depth']/2-y)<size/2]}
        xs=sorted(xs);ys=sorted(ys)
        assert all(surface_at((a+b)/2,(c+e)/2) in ('paving','soil','grass') for a,b in zip(xs,xs[1:]) for c,e in zip(ys,ys[1:])),(tree,'well overlaps protected surface')
        SURFACES.append(dict(x=x,y=y,width=size,depth=size,material='soil'))
        # Keep vertical dimensions unchanged when widening an ornamental well.
        objects=kit('tree_well_'+style,x,y,0,0,1)
        for o in objects:o.scale=(size/1.8,size/1.8,1)
        PLACEMENTS[-1]['scale_xy']=size/1.8
        wells.append(dict(x=x,y=y,width=size,depth=size,style=style,tree_kind=tree['kind']))
    return wells

def export(path,objects):
    # Consolidate small static wires, paint and slabs by material. Preserve the
    # shared kit mesh datablocks so repeating plants/furniture stay instanced.
    groups={};selected=[];temporary=[]
    for o in objects:
        mat=o.data.materials[0]
        if mat==MATS['kit']:selected.append(o)
        else:groups.setdefault(mat.name,[]).append(o)
    for mat,group in groups.items():
        bpy.ops.object.select_all(action='DESELECT');copies=[]
        for original in group:
            c=original.copy();c.data=original.data.copy();bpy.context.collection.objects.link(c);c.select_set(True);copies.append(c)
        bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name=mat
        selected.append(joined);temporary.append(joined)
    bpy.ops.object.select_all(action='DESELECT')
    for o in selected:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
    for o in temporary:bpy.data.objects.remove(o,do_unlink=True)
    return dict(path=Path(path).name,bytes=Path(path).stat().st_size,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
def deliver(out,recipe,cameras):
    recipe['tree_wells']=prepare_tree_wells()
    build_ground()
    out=Path(out);objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    recipe['placements']=list(PLACEMENTS)
    recipe['surface_regions']=list(SURFACES)
    recipe['surface_priority']='Last containing region owns ground cell; grass default; null means rigid module owns surface.'
    recipe['assembly']=export(out/'assembly-preview.glb',objects)
    # Reusable kit modules at native origin, with identical vertex colours.
    (out/'modules').mkdir();recipe['modules']={}
    for kind in sorted({p['kind'] for p in PLACEMENTS}):
        obs=[]
        if kind in KIT:
            for data in KIT[kind]:
                o=bpy.data.objects.new('module_'+kind,data);bpy.context.collection.objects.link(o);obs.append(o)
        else:
            originals,x,y=RIGID[kind]
            for original in originals:
                o=original.copy();o.data=original.data.copy();bpy.context.collection.objects.link(o);o.location.x-=x;o.location.y-=y;obs.append(o)
        recipe['modules'][kind]=export(out/'modules'/(kind+'.glb'),obs)
        for o in obs:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(out/'assembly-preview.glb'))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    assert all(math.isfinite(v) for p in pts for v in p)
    bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
    w,d=recipe['dimensions_m'];assert bounds[0][0]>=-w/2-.05 and bounds[1][0]<=w/2+.05,bounds
    assert bounds[0][1]>=-d/2-.05 and bounds[1][1]<=d/2+.05,bounds
    for o in objects:o.data.calc_loop_triangles()
    recipe.update(bounds_m=bounds,triangles=sum(len(o.data.loop_triangles) for o in objects),mesh_instances=len(objects),
      render_source='reimported GLB',runtime_approved=False,axes='X east/across; Y north/along; Z up; metres (GLB standard Y-up conversion)',
      runtime_contract='Preview assembly is a level inspection fixture. Reconstruct surfaces with shared ground; place rigid modules at native size. Never stretch assembly to fit.')
    assert recipe['triangles']<900000,recipe['triangles']
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
    scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.76,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=1500
    (out/'renders').mkdir()
    for name,pos,target,scale in cameras:
        if name=='top':scale=max(w,d*scene.render.resolution_x/scene.render.resolution_y)*1.1
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
        scene.render.filepath=str(out/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print('DELIVERED',recipe['id'],recipe['triangles'],flush=True)
