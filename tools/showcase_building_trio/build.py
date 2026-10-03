"""Exact-reference native showcase buildings; offline architectural-clay delivery."""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'catalogue_duplex_pilot')]
import clay_core as C
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

SPECS = {
    'market': dict(width=34, depth=48, height=20, floors=2, title='Grand Iron & Glass Market',
        signature='Open axial market nave, two occupied shop galleries, iron barrel vault, raised ridge monitor and brick side aisles.'),
    'tower': dict(width=32, depth=28, height=68, floors=17, title='Gilded Terracotta Tower',
        signature='Cream terracotta piers, nested occupied setbacks, sunburst relief, dark retail plinth and octagonal gilded lantern.'),
    'aquatic': dict(width=38, depth=56, height=17, floors=1, title='Living-Roof Aquatic Centre',
        signature='Arched glulam pool hall, glazed entry gable, planted vault, photovoltaic strips, ridge light and side ventilation towers.'),
}
PALETTE = dict(wall=(.48,.19,.105), stone=(.62,.58,.48), roof=(.20,.23,.20), trim=(.035,.11,.08),
               glass=(.38,.46,.42), timber=(.41,.25,.12), bronze=(.49,.34,.12), hardware=(.055,.075,.065),
               interior=(.64,.59,.48), floor=(.36,.26,.17), foundation=(.48,.46,.40), water=(.06,.31,.34),
               leaf=(.19,.28,.09), soil=(.105,.075,.045), solar=(.05,.085,.105), white=(.77,.75,.65))

def box(name, loc, size, role='wall', module='envelope'):
    return C.box(name, loc, size, role, module, 0)

def faces(w,d):
    return [C.Face((-w/2,-d/2,0),(1,0,0),(0,1,0),'front'),
            C.Face((w/2,-d/2,0),(0,1,0),(-1,0,0),'right'),
            C.Face((w/2,d/2,0),(-1,0,0),(0,-1,0),'rear'),
            C.Face((-w/2,d/2,0),(0,-1,0),(1,0,0),'left')]

def open_wall(face, length, z0, z1, holes, role='wall', depth=.32):
    """Partition a carrier around holes; reveals are real solid wall sections."""
    us=sorted({0,length,*[v for h in holes for v in (h['u']-h['w']/2,h['u']+h['w']/2)]})
    zs=sorted({z0,z1,*[v for h in holes for v in (h['z'],h['z']+h['h'])]})
    verts=[];polys=[]
    for u,v in zip(us,us[1:]):
        for z,t in zip(zs,zs[1:]):
            if any(abs((u+v)/2-h['u']) < h['w']/2 and h['z'] < (z+t)/2 < h['z']+h['h'] for h in holes):continue
            n=len(verts)
            verts.extend(face.p(uu,dd,zz) for zz in (z,t) for uu,dd in [(u,0),(v,0),(v,depth),(u,depth)])
            polys.extend(tuple(n+i for i in p) for p in C.BOX_FACES)
    o=C.mesh(face.label+' open carrier',verts,polys,role,'envelope');o['rlasm_wall_carrier']=True
    for h in holes:
        C.Face.window(face,h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',2),rows=h.get('rows',1),
                      frame=h.get('frame','trim'),inset=.16,sill=not h.get('door',False),depth=depth)
    return o

def curve_beam(name, points, width, depth, role='trim', module='structure'):
    for a,b in zip(points,points[1:]):C.beam(name,a,b,width,depth,role,module)

def chair(x,y,z=0,yaw=0):
    # Whole furniture at human scale, with back and four connected legs.
    def b(n,loc,size):
        xx,yy,zz=loc;co=math.cos(yaw);si=math.sin(yaw)
        o=box(n,(0,0,0),size,'timber','furniture');o.location=(x+co*xx-si*yy,y+si*xx+co*yy,z+zz);o.rotation_euler.z=yaw
    b('chair seat',(0,0,.46),(.46,.46,.07));b('chair back',(0,.21,.73),(.46,.06,.46))
    for xx in (-.17,.17):
        for yy in (-.17,.17):b('chair leg',(xx,yy,.22),(.045,.045,.44))

def table(x,y,z=0):
    box('cafe tabletop',(x,y,z+.76),(1.35,.8,.065),'timber','furniture')
    for dx in (-.52,.52):
        for dy in (-.29,.29):box('table leg',(x+dx,y+dy,z+.365),(.045,.045,.73),'hardware','furniture')
    chair(x,y-.7,z);chair(x,y+.7,z,math.pi)

def label(text, xyz, size=.32, role='bronze'):
    C.bpy.ops.object.text_add(location=xyz,rotation=(math.pi/2,0,0));o=C.bpy.context.object
    o.data.body=text;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.006
    C.bpy.ops.object.convert(target='MESH');o=C.bpy.context.object;o.data.materials.append(C.MATS[role]);C.tag(o,role,'signage')

def camera_roster(kind):
    s=SPECS[kind];w,d,h=s['width'],s['depth'],s['height'];target=(0,0,h*.43);r=max(w,d,h)*1.55
    result=[dict(name=n,location=p,target=target,ortho_scale=max(w,d,h)*1.3) for n,p in
            [('front',(0,-r,h*.43)),('left_side',(-r,0,h*.43)),('right_side',(r,0,h*.43)),('rear',(0,r,h*.43))]]
    result += [dict(name='front_corner',location=(w*1.6,-d*1.6,h*1.15),target=target),
               dict(name='aerial',location=(w*1.5,-d*1.5,max(w,d,h)*1.55),target=target),
               dict(name='top',location=(0,0,h+180),target=(0,.001,0),ortho_scale=max(w,d)*1.4),
               dict(name='rear_side',location=(-w*1.6,d*1.6,h*.9),target=target)]
    if kind=='market':
        close=[('facade_close',(23,-33,9),(12,-23,5)),('architecture_close',(18,-32,18),(7,-16,13)),
               ('glass_close',(3,-31,16),(0,-23,14)),('program_interior',(0,-20,2.2),(0,12,5)),
               ('walk',(2,-36,1.65),(0,-14,5)),('gallery_stair',(0,12,8.7),(8.2,20,3.5)),
               ('gallery_landing',(3,18,7),(8.8,22,4.8))]
    elif kind=='aquatic':
        close=[('facade_close',(25,-40,9),(10,-26,5)),('architecture_close',(-22,-39,18),(-7,-22,13)),
               ('glass_close',(0,-35,6),(0,-24,5)),('program_interior',(11,-16,2),(0,13,5)),
               ('walk',(4,-42,1.65),(0,-22,6)),('roof_contact',(27,-26,25),(9,-8,12))]
    else:
        close=[('facade_close',(25,-34,24),(10,-13,22)),('architecture_close',(21,-25,72),(0,0,61)),
               ('glass_close',(2,-23,5),(0,-13,3)),('walk',(22,-43,1.65),(0,0,25)),
               ('crown_contact',(20,-25,78),(0,0,62)),
               ('entrance_access',(5,-23,2.1),(0,-13.8,2.1))]
    result += [dict(name=n,location=p,target=t,whole=False,lens=34 if n in ('walk','program_interior') else 48) for n,p,t in close]
    return result

def efficient_fit(camera,target,margin=.075):
    scene=C.bpy.context.scene;C.bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(p) for o in C.objects() for p in o.bound_box]
    for _ in range(80):
        C.bpy.context.view_layer.update();q=[world_to_camera_view(scene,camera,p) for p in pts]
        if all(p.z>0 and margin<=p.x<=1-margin and margin<=p.y<=1-margin for p in q):break
        if camera.data.type=='ORTHO':camera.data.ortho_scale*=1.045
        else:camera.location=Vector(target)+(camera.location-Vector(target))*1.045
    else:raise RuntimeError('Could not frame '+camera.name)
    return dict(xmin=min(p.x for p in q),xmax=max(p.x for p in q),ymin=min(p.y for p in q),ymax=max(p.y for p in q))

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=SPECS[a.kind]
    source=next(e for e in json.loads(a.lock.read_text())['entries'] if e['kind']==a.kind)
    entry=dict(archetype_id=source['archetype_id'],variant_id=source['variant_id'],directory='.',
               _reference_root=str(Path(source['sources'][0]['path']).parent),
               sources=[dict(v,original_path=v['path'],path='sources/'+Path(v['path']).name) for v in source['sources']])
    roster=camera_roster(a.kind);manifest=dict(candidate=f"showcase-{a.kind}-clay-v{a.version:03d}",method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=entry['archetype_id'],variant_id=entry['variant_id'],
        camera_roster=roster,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m={k:s[k] for k in ('width','depth','height')},floors=s['floors'],front='-Y',bottom_datum_m=0,
                                  measurement_basis='Exact catalogue image ratios and plausible metric modules; conceptual, not surveyed.'),
        identity_contract=[s['signature']],hidden_view_assumptions=['Unshown rear and interior details inferred from the depicted building program.'],
        cohesion_contract='Shared neutral stone, real opening depth, complete construction and human-scale detailing; exact reference morphology takes priority.',
        limitations=['Fixed native scale. Browser placement, ground, editing and render capture NOT TESTED at user request.',
                     'Architectural-clay tier, not a textured RLASM keeper or construction model.'])
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE/(a.kind+'.py')])
    if out is None:return
    palette=dict(PALETTE)
    if a.kind=='tower':palette.update(wall=(.66,.57,.40),stone=(.72,.64,.49),trim=(.30,.24,.12),foundation=(.08,.09,.08),roof=(.34,.34,.29))
    if a.kind=='aquatic':palette.update(wall=(.38,.25,.14),trim=(.40,.27,.13),roof=(.21,.29,.10),floor=(.60,.57,.48),cladding=(.07,.085,.075))
    cams=C.setup(palette,roster,1440);C.fit=efficient_fit
    C.bpy.context.scene.cycles.samples=24
    # Tall towers have hundreds of chamfered window parts. Apply those same
    # modifiers in one selected-object conversion, avoiding a dependency-graph
    # rebuild for every jamb. Geometry and audits still receive real meshes.
    chamfers=[]
    if a.kind=='tower':
        def queue_chamfer(obj,width=.012,segments=1):
            if width<=0:return
            m=obj.modifiers.new('Construction edge chamfer','BEVEL');m.width=width;m.segments=segments;m.limit_method='ANGLE'
            chamfers.append(obj)
        C.bevel=queue_chamfer
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    importlib.import_module(a.kind).build(sys.modules[__name__])
    if chamfers:
        C.bpy.ops.object.select_all(action='DESELECT')
        for obj in chamfers:obj.select_set(True)
        C.bpy.context.view_layer.objects.active=chamfers[0]
        C.bpy.ops.object.convert(target='MESH')
    C.deliver(out,manifest,cams)

if __name__=='__main__':main()
