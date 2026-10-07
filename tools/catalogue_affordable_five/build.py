"""Original affordable housing: measured envelopes, occupied rooms and seated contacts."""
import argparse
import math
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
import clay_core as C
from plan import SPECS,source_entry
from assemblies import hole,faces,steps,sofa,bed,straight_stair,seated_guard,bathroom,shrub,garden_chair,rotate_new
from geometry import gable,kitchen
from housing_wave import juniper,stackyard,aspen,switchback,DETAILS as WAVE_DETAILS

PALETTE=dict(wall=(.73,.71,.65),trim=(.09,.105,.115),roof=(.16,.18,.20),
 foundation=(.42,.43,.41),glass=(.34,.40,.40),hardware=(.065,.075,.08),
 interior=(.78,.75,.68),floor=(.54,.42,.30),timber=(.57,.37,.20),
 pale=(.66,.64,.57),planting=(.25,.32,.14),blue=(.16,.25,.28),
 brick=(.54,.29,.20),joint=(.32,.33,.30))

def pane(f,h):
    if 'door' in h['id'].lower():
        f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=1)
    else:
        f.window(h['id'],h['u'],h['z'],h['w'],h['h'],
                 cols=2 if h['w']>1.6 else 1,rows=1,frame='trim',depth=.23)

def partition(f,name,a,b,z,top,doors):
    f.wall(name,a,b,z,top,depth=.12,role='interior',holes=doors)
    for h in doors: f.door(h['id'],h['u'],z,h['w'],h['h'],role='timber',panels=1)

def porchlight_unit(i):
    before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
    x=(i-1.5)*5.5;low=.15;upper=3.15;top=6.10
    ff=faces(5.5,9,label=f'Porchlight home {i+1} ')
    front=[hole('Living window',-1.05,.75,2.4,1.85),hole('Front door',1.65,low,1.04,2.23)]
    front += [hole('Bedroom front window '+str(j),u,4.0,1.2,1.55) for j,u in enumerate((-1.32,.82))]
    rear=[hole('Kitchen window',1.3,1.1,1.35,1.4),hole('Garden door',-1.65,low,1.0,2.23)]
    rear += [hole('Bedroom rear window '+str(j),u,4.0,1.2,1.55) for j,u in enumerate((-1.3,1.3))]
    for j,(f,span) in enumerate(zip(ff,[5.5,9,5.5,9])):
        hs=front if j==0 else rear if j==2 else (
            [hole('End sash '+str(k),-2.15,z,1.0,1.5) for k,z in enumerate((1.0,4.0))]
            if (j==1 and i==3) or (j==3 and i==0) else [])
        # Long facades own the corner; returns stop at their interior faces.
        span2=span if j in (0,2) else span-.46
        if j in (1,3) and not hs:
            if j==3 and i>0:continue
            # Shared party wall is one solid owner, no double coplanar surface.
        f.wall('Complete residential envelope',-span2/2,span2/2,low,top,depth=.23,holes=hs)
        for h in hs:pane(f,h)
    # Accent belongs to the door bay, physically terminated around its aperture.
    f=ff[0]
    f.wall('Terracotta door-bay cladding',1.60,2.42,low,top,depth=.035,role='brick',
           holes=front)
    # Move accent outward from the carrier, with slight buried overlap.
    accent=next(o for o in C.objects() if o.name.startswith('Terracotta door-bay cladding') and o not in before)
    accent.location.y-=.027
    floor_x=-.115 if i>0 else 0
    floor_w=5.29 if i>0 else 5.06
    slab=C.box('Upper occupied floor',(floor_x,0,upper-.11),(floor_w,8.56,.22),'floor','floor')
    sx=1.63;start=-2.70;length=18*.26
    C.cut_box(slab,'Open stair headroom',(sx,start+length/2,upper-.11),(1.08,length,.6))
    stair=straight_stair('Private household stair',sx,start,low,upper,width=1,run=.26,count=18)
    for dx in (-.63,.63):seated_guard('Floor seated stair guard',(sx+dx,start-.09,upper),(sx+dx,start+length,upper))
    seated_guard('Floor seated stair end',(sx-.63,start-.09,upper),(sx+.63,start-.09,upper),end_anchors=False)
    C.box('Continuous upper ceiling',(floor_x,0,6.04),(floor_w,8.54,.12),'interior','ceiling')
    hall=C.Face((.15,0,0),(0,1,0),(-1,0,0),'Bedroom passage')
    partition(hall,'Bedroom partition',-4.27,4.27,upper,5.99,[
        hole('Front bedroom door',-.8,upper,.82,2.1),
        hole('Rear bedroom door',2.15,upper,.82,2.1)])
    C.box('Bedroom separating wall',(-1.18,.15,4.57),(2.6,.12,2.84),'interior','partitions')
    bed(-1.25,-2.0,upper);bed(-1.25,2.35,upper)
    bath=C.Face((0,2.8,0),(1,0,0),(0,1,0),'Bath entrance')
    partition(bath,'Enclosed sanitary room',.20,2.52,upper,5.99,[hole('Bathroom door',1.55,upper,.82,2.1)])
    bathroom(1.25,3.85,upper)
    sofa(-1.17,-1.15,low);kitchen(-.30,3.72,low,2.65)
    # Four complete porches, grounded posts, finite weathering joints.
    dx=1.60
    C.box('Entrance pad',(dx,-5.08,.075),(2.25,1.45,.15),'foundation','entry')
    C.box('Porch timber soffit',(dx,-5.00,2.72),(2.30,1.32,.14),'timber','porch')
    C.box('Porch weathering cap',(dx,-5.00,2.82),(2.39,1.40,.08),'roof','porch')
    for px in (dx-1.04,dx+1.04):
        C.box('Porch foot',(px,-5.55,.17),(.23,.23,.04),'hardware','porch')
        C.box('Porch grounded timber post',(px,-5.55,1.42),(.17,.17,2.48),'timber','porch')
    steps('Low front step ',dx,-5.80,1.55,.15,n=1,run=.35,role='foundation')
    C.box('Front path',(dx,-6.16,.025),(1.55,.72,.05),'pale','paths')
    C.box('Rear private patio',(0,5.75,.05),(3.1,2.50,.1),'pale','patios')
    garden_chair(-.70,5.6,.10)
    # Garden exit at source-inferred rear; arrival pad has actual grade contact.
    C.box('Garden door landing',(1.65,4.75,.075),(1.30,.5,.15),'foundation','garden entry')
    for y in (-2.5,2.9):
        C.qa_room_light('Home lower',(0,y,2.86),100,1.7)
        C.qa_room_light('Home upper',(-1.15,y,5.80),90,1.4)
    C.qa_room_light('Stair daylight',(1.60,1.1,5.8),90,1.5)
    C.qa_room_light('Sanitary room inspection',(1.4,3.5,5.8),55,1.0)
    rotate_new(before,opening_start,x,0,0)
    C.CONTACTS.append(dict(name=f'Porchlight dwelling {i+1}',storeys=2,bedrooms=2,stair=stair,
        assumptions='Original teaching floor plan; no permit/accessibility/structural certification.'))

def porchlight():
    C.box('Grounded row foundation',(0,0,.075),(22,9,.15),'foundation','foundation')
    # Garden edges are separate geometry from the body and lie below the floor.
    C.box('Front grounded garden',(0,-5.40,.035),(22.5,2.5,.07),'foundation','landscape')
    C.box('Rear garden base',(0,5.85,.035),(22.5,2.7,.07),'foundation','landscape')
    for i in range(4):porchlight_unit(i)
    gable('Porchlight continuous gable',0,0,22,9,6.25,7.65,seams=True,over=.23,flush_gable=True)
    for i in range(4):
        x=(i-1.5)*5.5
        C.box('Rear lawn',(x,6.5,.078),(5.26,1.1,.016),'planting','garden')
        for xx in (x-2.05,x-1.35,x-.60):
            shrub(xx,-5.30,.07,.47)
        for xx in (x-1.9,x-.5,x+1.1):shrub(xx,7.0,.07,.46)
    for x in (-11.1,-5.5,0,5.5,11.1):
        C.box('Rear garden divider',(x,5.90,.47),(.10,2.70,.80),'timber','garden partitions')

DETAILS={'porchlight':[
 ('facade_close',(4,-18,7),(2.75,-4.5,3.25)),
 ('architecture_close',(4.8,-9,2.7),(4.35,-5.35,1.7)),
 ('glass_close',(0,-8,2.2),(1.70,-4.4,1.65)),
 ('roof_contact',(14,-12,11),(10.8,-3.5,6.6)),
 ('side_projection',(17,-8,6),(10.8,-1.2,3.4)),
 ('interior',(4.65,-4.0,2.0),(1.45,-1.0,1.15)),
 ('bedroom',(2.58,-3.95,5.8),(1.50,-1.9,3.65)),
 ('stairs',(3.58,-3.8,1.9),(4.40,.8,3.2)),
 ('upper_landing',(5.10,2.5,5.4),(4.0,.70,3.3)),
 ('stair_contact',(3.3,2.5,3.6),(3.75,1.1,3.18)),
 ('rear_entry',(7.6,9,2.9),(4.4,4.7,1.2)),
 ('bathroom',(4.90,3.16,5.60),(3.90,3.85,3.6))]}
DETAILS.update(WAVE_DETAILS)

def cameras(kind):
    d=SPECS[kind]['dimensions_m'];scale=max(d['width'],d['depth'])/34
    basic=[('front',(0,-64,12)),('front_corner',(46,-58,32)),('aerial',(39,-49,69)),('top',(0,0,90)),('left_side',(-64,0,12)),('right_side',(64,0,12)),('rear',(0,64,12)),('rear_side',(-46,58,32))]
    out=[dict(name=n,location=tuple(v*scale for v in loc),target=(0,.001 if n=='top' else 0,0 if n=='top' else d['height']*.4),**({'ortho_scale':max(d['width'],d['depth'])*1.25} if n=='top' else {})) for n,loc in basic]
    wide={'interior','stairs','upper_landing','bathroom'}
    return out+[dict(name=n,location=loc,target=t,whole=False,lens=18 if n in ('bedroom','bathroom','lift') else 24 if n in wide else 42) for n,loc,t in DETAILS[kind]]

def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["slug"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',archetype_id=s['id'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
      measurement_contract=dict(dimensions_m=s['dimensions_m'],observed_storeys=s['storeys'],reference_reconciliation=s.get('reference_reconciliation','Original reference topology; front owns bay counts, high top view owns the roof graph. Right end reference has one window per floor; hidden rear and interiors inferred.'),source_measurements=s.get('source_measurements',['Four equal 5.5m bays and two front occupied levels in Porchlight.']),hidden_assumptions=['Metric dimensions are authored, not surveyed.','Hidden interiors and rear construction are inferred.','Top reference is high oblique, not a georeferenced orthophoto.']),
      roof_contract=dict(authority='Locked original pixels; closed supported weathering envelope.'),identity_contract=dict(owner='Source-specific physical geometry',bitmap_stickers='None in architectural clay.'),material_contract=dict(profile='Source-palette untextured clay',limitations='Final textured keeper stage remains separate.'),programme_contract=dict(storeys=s['storeys'],description=s['program'],uses=s['uses'],legal_approval=False),contact_contract=['Grade-zero support.','Through-carrier apertures.','Floor-seated guards.','Complete supported roofs and access.'],runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='NOT TESTED'),camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def prepare(a,entry,m):
    out=Path(a.output).resolve()
    if not out.is_relative_to(Path('C:/dev-artifacts/CityPrompt').resolve()):raise ValueError('Output must be external')
    if a.dry_run:print('DRY_RUN_PASS '+m['candidate']);return None
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'):(out/name).mkdir()
    for s in entry['sources']:
        shutil.copy2(s['original_path'],out/s['path']);assert C.digest(out/s['path'])==s['sha256']
    shutil.copy2(Path(entry['_reference_root'])/'generation-provenance.json',out/'sources/generation-provenance.json')
    scripts=[Path(C.__file__),Path(__file__),HERE/'assemblies.py',HERE/'geometry.py',HERE/'housing_wave.py',HERE/'plan.py',HERE/'designs.json']
    for p in scripts:shutil.copy2(p,out/'scripts'/p.name)
    C.write_json(out/'source-entry.json',{k:v for k,v in entry.items() if not k.startswith('_')})
    m['source_contract']=dict(sources=entry['sources'],exact_variant_only=True,origin='original_generated_design',generated_references_explicitly_requested=True,not_surveyed=True)
    m['provenance']=dict(scripts=[dict(path='scripts/'+p.name,sha256=C.digest(out/'scripts'/p.name)) for p in scripts],blender_version=C.bpy.app.version_string,python_version=sys.version,build_started_utc=C.utc(),generation_api_calls_during_build=0,reference_generation='built-in image_gen; prompts in source provenance',render_source='actual optimized GLB reimport only')
    C.write_json(out/'prework-manifest.json',m);return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=manifest(a.kind,a.version);out=prepare(a,source_entry(a.kind,a.source_root),m)
    if out is None:return
    palette=PALETTE.copy()
    if a.kind=='juniper':palette.update(wall=(.43,.46,.36),joint=(.31,.34,.27))
    if a.kind=='stackyard':palette.update(wall=(.28,.31,.24),joint=(.20,.22,.18))
    if a.kind=='aspen':palette.update(wall=(.74,.67,.53),joint=(.52,.45,.33))
    if a.kind=='switchback':palette.update(wall=(.73,.72,.68),olive=(.39,.43,.27),ochre=(.68,.39,.13),joint=(.38,.36,.29))
    cams=C.setup(palette,m['camera_roster'],a.resolution);C.bevel=lambda *args,**kwargs:None
    for obj in C.bpy.context.scene.objects:
        if obj.type=='LIGHT':obj.location*=2;obj.data.energy*=4;obj.data.size*=2
        if obj.name=='QA ground - excluded':obj.scale*=6
    globals()[a.kind]()
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces));C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)

if __name__=='__main__':main()
