"""Five source-locked architectural-clay buildings; shared primitives, distinct designs."""
import argparse
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
import clay_core as C
sys.path.append(str(HERE.parent/'catalogue_coverage_five'))
import assemblies as A
from plan import SPECS,source_entry
import designs as D

PALETTE=dict(wall=(.28,.13,.095),trim=(.46,.44,.38),roof=(.17,.19,.20),foundation=(.42,.42,.39),
    glass=(.46,.51,.52),hardware=(.06,.075,.08),interior=(.69,.64,.52),floor=(.40,.32,.23),
    timber=(.40,.28,.16),joint=(.19,.105,.08),pale=(.77,.74,.64),blue=(.17,.26,.31),
    planting=(.19,.30,.12),produce=(.56,.24,.09))

def cameras(kind):
    roster=[('front',(0,-30,7),(0,0,3.7)),('front_corner',(23,-29,15),(0,0,3.7)),
        ('aerial',(22,-27,30),(0,0,3)),('top',(0,0,38),(0,.001,0)),
        ('left_side',(-31,0,8),(0,0,3.7)),('right_side',(31,0,8),(0,0,3.7)),
        ('rear',(0,31,8),(0,0,3.7)),('rear_side',(-24,28,15),(0,0,3.7))]
    details=[('facade_close',(10,-19,9),(1,-5.8,4)),('architecture_close',(9,-10,3),(4.8,-5.3,1.7)),
        ('glass_close',(1,-9,2.6),(1,-5.8,1.7)),('roof_contact',(10,-10,13),(4,-5,7.6)),
        ('side_projection',(12,4,7),(5.5,0,4)),('interior',(3.7,-4.7,1.8),(0,3,1.7)),
        ('stair_contact',(-1.8,-2.8,2),(-3.8,1,2.5)),('stair_arrival',(-1.5,4.6,5.7),(-3.8,2.7,4.2)),
        ('upper_room',(3.5,-4.5,5.7),(0,3,5.2))]
    if kind!='grocer':details=D.detail_cameras(kind)
    return [dict(name=n,location=l,target=t,**({'ortho_scale':18} if n=='top' else {})) for n,l,t in roster]+[
        dict(name=n,location=l,target=t,whole=False,lens=24 if n in ('interior','stair_contact','stair_arrival','upper_room','roof_half_landing','roof_stair') else 42) for n,l,t in details]

def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["title"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=s['parent'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=s['dimensions'],observed_storeys=s['floors'],source_measurements=s['measurements'],hidden_assumptions=s['assumptions']),
        roof_contract=dict(authority='locked top and oblique; complete closed envelope'),
        identity_contract=dict(owner='physical massing, openings, roof and construction; no bitmap facade'),
        material_contract=dict(profile='source-palette texture-free architectural clay; no textured-keeper claim'),
        programme_contract=dict(storeys=s['floors'],interiors=s['assumptions']),
        contact_contract=['Grade-zero complete foundations','Real full-depth openings','Supported stairs and explicit floor apertures'],
        runtime_contract=dict(scale='fixed_native_only',translation=True,rotation=True,resizing=False,terrain='not tested',installation='not installed',review='not tested'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def cleanup():
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()

def lettering(f,words,u,z,width,height,depth=-.127):
    C.bpy.ops.object.text_add()
    obj=C.bpy.context.object;obj.name=words;obj.data.body=words;obj.data.align_x='CENTER';obj.data.align_y='CENTER'
    obj.data.extrude=.006;obj.data.size=1
    C.bpy.context.view_layer.update();obj.scale=(width/max(obj.dimensions.x,.01),height/max(obj.dimensions.y,.01),1)
    # Text local X follows wall; local Y is world Z; its front normal faces outdoors.
    from mathutils import Matrix,Vector
    rot=Matrix((f.t,Vector((0,0,1)),-f.n)).transposed().to_4x4()
    obj.rotation_euler=rot.to_euler();obj.location=f.p(u,depth,z)
    C.bpy.ops.object.convert(target='MESH');C.tag(obj,'timber','signage');obj.data.materials.append(C.MATS['timber'])

def shelf(x,y,z=.16):
    for xx in (x-1.0,x+1.0):C.box('Shop shelf upright',(xx,y,z+.9),(.045,.50,1.8),'trim','grocery shelving')
    for level in range(4):
        zz=z+.17+level*.44
        C.box('Shop shelf',(x,y,zz),(2.1,.55,.035),'pale','grocery shelving')
        for j in range(9):
            C.box('Packaged groceries',(x-.88+j*.22,y,zz+.135),(.14,.25,.23),'produce' if (j+level)%3==0 else 'interior','grocery goods')

def grocer():
    w,d=11,12;lower=.16;upper=4.1;roof=7.5
    # Chamfer is confined to the street corner at the lower storey.
    outline=[(-5.5,-6),(4.05,-6),(5.5,-4.55),(5.5,6),(-5.5,6)]
    C.prism('Complete foundation',outline,'z',0,lower,'foundation','foundation')
    front,right,rear,left=A.faces(w,d)
    for f,span,holes in [
        (front,(-5.5,4.05),[A.hole('Front residence entrance',-4.65,lower,1.05,2.8),A.hole('Shop window west',-2.35,.65,2.6,2.5),A.hole('Shop window east',1.1,.65,3.1,2.5)]),
        (right,(-4.55,6),[A.hole('Shop side display',-2.65,.65,2.9,2.5),A.hole('Service side window',1.2,1.3,1.15,1.5),A.hole('Rear shop side window',4.0,1.3,1.15,1.5)]),
        (rear,(-5.5,5.5),[A.hole('Rear exit',0,lower,1.2,2.45),A.hole('Rear stock window',-3.1,1.1,1.5,1.8),A.hole('Stair rear window',3.8,1.1,1.1,1.8)]),
        (left,(-6,6),[A.hole('Stair daylight',-2.4,1.2,1.2,1.8),A.hole('Side retail daylight',2.5,1.0,1.5,2)])]:
        f.wall(f.label+' ground brick',*span,lower,upper-.18,depth=.28,holes=holes)
        for h in holes:
            door='entrance' in h['id'] or 'exit' in h['id']
            A.glazing(f,h,door=door,cols=1 if door else 3 if h['w']>2 else 1)
            if h['w']>2:
                f.part('Storefront transom',h['u'],.132,h['z']+h['h']-.45,h['w']-.12,.09,.055,'trim','storefront transoms')
        uppers=[A.hole(f.label+' upper sash '+str(i),u,4.8,1.05,2.0) for i,u in enumerate((-3.35,0,3.35))]
        f.wall(f.label+' upper brick',-w/2 if f in (front,rear) else -d/2,w/2 if f in (front,rear) else d/2,upper-.18,roof,depth=.28,holes=uppers)
        for h in uppers:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,rows=2,depth=.28,frame='timber')
        length=w if f in (front,rear) else d
        f.part('Parapet stringcourse',0,-.025,7.24,length,.055,.08,'trim','cornice')
        if f in (front,right):
            centre=1.575 if f==front else -3.4375;sw=8.05 if f==front else 5.325
            f.part('Shop sign fascia',centre,-.07,3.55,sw,.12,.61,'pale','signage')
            lettering(f,'DEPANNEUR LALONDE',centre,3.55,sw-.22,.33)
    C.prism('Supported corner sign soffit',[(4.05,-6),(5.5,-6),(5.5,-4.55)],'z',3.80,3.93,'pale','corner fascia support')
    # Source blade sign hangs from two real wall brackets above the right fascia.
    C.box('Corner blade sign',(5.97,-5.45,4.70),(.84,.085,1.08),'pale','corner sign')
    for z in (4.27,5.10):C.beam('Blade wall bracket',(5.45,-5.45,z),(6.32,-5.45,z),.045,.045,'hardware','corner sign')
    blade=C.Face((5.97,-5.40,0),(1,0,0),(0,1,0),'blade')
    lettering(blade,'LALONDE',0,4.70,.73,.19)
    diag=C.Face((4.775,-5.275,0),(math.sqrt(.5),math.sqrt(.5),0),(-math.sqrt(.5),math.sqrt(.5),0),'corner entry')
    hole=A.hole('Corner shop entrance',0,lower,1.48,2.95)
    diag.wall('Corner entry carrier',-1.025,1.025,lower,upper-.18,depth=.28,holes=[hole])
    A.glazing(diag,hole,door=True,cols=1)
    # Roof and floors; measured stair opening is kept clear through the slab.
    floor=C.box('Upper occupied floor',(0,0,upper-.09),(10.44,11.44,.18),'floor','floor',0)
    C.cut_box(floor,'Full stairwell aperture',(-3.8,.8,upper),(1.7,5.8,1))
    C.prism('Ground floor finish',outline,'z',lower,lower+.02,'floor','floor')
    C.prism('Corner threshold approach',[(4.05,-6),(5.5,-6),(5.5,-4.55)],'z',0,.08,'foundation','entry step')
    A.flat_roof('Flat membrane',0,0,11,12,roof,parapet=.29)
    stair=A.straight_stair('Residence stair',-3.8,-1.8,lower+.02,upper,width=1.35,run=.25,count=22)
    for xx in (-4.68,-2.92):A.seated_guard('Upper stairwell guard',(xx,-2.1,upper),(xx,3.85,upper))
    A.seated_guard('Stairwell lower end',(-4.68,-2.1,upper),(-2.92,-2.1,upper))
    # Retail: two short merchandising runs leave generous circulation from corner to rear.
    for x,y in [(-.3,-.6),(-.3,2.0),(2.8,3.5)]:shelf(x,y,lower+.02)
    C.box('Checkout counter',(2.75,-2.0,.64),(1.7,.75,.96),'timber','checkout')
    C.box('Checkout worktop',(2.75,-2,.1+1.02),(1.8,.82,.07),'pale','checkout')
    C.box('Till',(2.75,-2,1.32),(.38,.30,.35),'hardware','checkout')
    # Residential teaching layout upstairs, with clear central route and a rear stair arrival.
    A.sofa(1.8,-2.3,upper);A.bed(3.4,3.0,upper)
    C.box('Kitchen cabinets',(.8,5.22,upper+.44),(3.8,.70,.88),'timber','upper dwelling')
    C.box('Kitchen countertop',(.8,5.22,upper+.90),(3.85,.74,.06),'pale','upper dwelling')
    for z in (3.55,7.15):
        for x,y in ((0,-2),(1,3),(-3,2)):C.qa_room_light('occupied room',(x,y,z),140,3)
    C.CONTACTS.append(dict(name='Connected internal stair',**stair))
    C.CONTACTS.append(dict(name='Corner entrance',door_centre=[4.775,-5.275,lower],clear_width=1.48,entry_direction=[math.sqrt(.5),-math.sqrt(.5)],ground_floor=lower))

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True);p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=manifest(a.kind,a.version)
    out=C.prepare_candidate(a,source_entry(a.kind,a.source_root),m,__file__,extra_scripts=[HERE/'plan.py',HERE/'designs.py',HERE.parent/'catalogue_coverage_five/assemblies.py'])
    if out is None:return
    cams=C.setup(PALETTE if a.kind=='grocer' else D.palette(a.kind,PALETTE),m['camera_roster'],a.resolution);C.bevel=lambda *args,**kwargs:None
    {'grocer':grocer,'hall':D.hall,'cabin':D.cabin,'inglewood':lambda:D.inglewood(lettering,shelf),'shops':lambda:D.shops(lettering,shelf)}[a.kind]()
    cleanup();C.deliver(out,m,cams)

if __name__=='__main__':main()
