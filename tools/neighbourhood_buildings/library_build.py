"""Reference-led neighbourhood buildings, immutable native GLB review packages."""
import argparse
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'catalogue_duplex_pilot'))
import clay_core as C
from mathutils import Vector
spec=importlib.util.spec_from_file_location('shared_building',HERE.parent/'showcase_building_trio/build.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

PALETTE=dict(B.PALETTE,wall=(.09,.095,.085),timber=(.43,.27,.125),trim=(.07,.075,.06),
             roof=(.20,.26,.08),glass=(.52,.57,.48),leaf=(.24,.31,.08),stem=(.33,.29,.12),
             book_red=(.30,.075,.045),book_blue=(.07,.13,.18),book_gold=(.43,.34,.13))

def box(name,xyz,size,role='wall',module='envelope'):
    return C.box(name,xyz,size,role,module,0)

def roof_z(y):return 9.4+2.6*(1-abs(y)/15)

def books(x,y,z,length=3):
    box('bookcase back',(x,y+.24,z+1.05),(length,.055,2.1),'timber','library stacks')
    for dx in (-length/2,length/2):box('bookcase end',(x+dx,y,z+1.05),(.07,.55,2.1),'timber','library stacks')
    rng=random.Random(round(x*13+y*37+z*19))
    for shelf in range(5):
        zz=z+.16+shelf*.4;box('book shelf',(x,y,zz),(length,.55,.045),'timber','library stacks')
        xx=x-length/2+.1
        while xx<x+length/2-.13:
            w=rng.uniform(.035,.085);h=rng.uniform(.21,.31)
            box('individual book',(xx,y-.05,zz+.025+h/2),(w,.22,h),rng.choice(['book_red','book_blue','book_gold','interior']),'library stacks');xx+=w+.012

def planted_roof(x0,x1,y0,y1,height,holes=()):
    # Small planted tufts are actual geometry; no image sheet or solid green box.
    rng=random.Random(int((x0+40)*37+(y0+40)*71));vs=[];fs=[]
    for i in range(int((x1-x0)/.28)):
        for j in range(int((y1-y0)/.28)):
            x=x0+(i+.5)*.28+rng.uniform(-.12,.12);y=y0+(j+.5)*.28+rng.uniform(-.12,.12)
            if any(a<=x<=b and c<=y<=d for a,b,c,d in holes):continue
            z=height(x,y);h=rng.uniform(.03,.09)
            for k in range(5):
                ang=k*math.tau/5+rng.random();rad=rng.uniform(.06,.14);dx=rad*math.cos(ang);dy=rad*math.sin(ang);n=len(vs)
                vs.extend([(x,y,z+.02),(x+dx*.5-dy*.38,y+dy*.5+dx*.38,z+h),(x+dx,y+dy,z+h*.65),(x+dx*.5+dy*.38,y+dy*.5-dx*.38,z+h)])
                fs.extend([(n,n+1,n+2),(n,n+2,n+3)])
    C.mesh('sedum meadow growth',vs,fs,'leaf','living roof')

def roof_tier(half,y0,y1,height,bottom,light_y,covered=(),step_front=False):
    # A partitioned roof skin with actual rooflight holes and interlocking tier cuts.
    xs=sorted(set([-half,half,-8,8,*[i*.5 for i in range(-int(half*2),int(half*2)+1)]]))
    ys=sorted(set([y0,y1,light_y-1.2,light_y+1.2,*[v for h in covered for v in h[2:]],*([y0+1.6] if step_front else []),*([0] if y0<0<y1 else [])]))
    def present(x,y):
        return not (step_front and y<y0+1.6 and abs(x)>9) and not any(a<x<b and c<y<d for a,b,c,d in covered)
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            if c<y0 or d>y1 or not present((a+b)/2,(c+d)/2):continue
            skylight=abs((a+b)/2)<8 and abs((c+d)/2-light_y)<1.2
            C.solid_surface('real rooflight pane' if skylight else 'planted curved tier',[(x,y,height(x,y)) for x,y in [(a,c),(b,c),(b,d),(a,d)]],.014 if skylight else .20,'glass' if skylight else 'roof','rooflight' if skylight else 'roof')
            if skylight:
                C.beam('rooflight glazing bar',(a,c,height(a,c)+.025),(a,d,height(a,d)+.025),.03,.045,'trim','rooflight')
            else:planted_roof(a+.01,b-.01,c+.01,d-.01,lambda x,y:height(x,y)+.01)
    outlines=[(-half,y0+1.6 if step_front else y0),(-9,y0+1.6),(-9,y0),(9,y0),(9,y0+1.6),(half,y0+1.6),(half,y1),(-half,y1)] if step_front else [(-half,y0),(half,y0),(half,y1),(-half,y1)]
    for a,b in zip(outlines,outlines[1:]+outlines[:1]):
        length=math.dist(a,b);n=max(1,math.ceil(length/.85))
        for i in range(n):
            p=tuple(a[k]+(b[k]-a[k])*i/n for k in range(2));q=tuple(a[k]+(b[k]-a[k])*(i+1)/n for k in range(2))
            mid=tuple((p[k]+q[k])/2 for k in range(2))
            if any(c<mid[0]<d and e<mid[1]<f for c,d,e,f in covered):continue
            lo0=bottom(*p);lo1=bottom(*q);hi0=height(*p)-.20;hi1=height(*q)-.20
            if min(hi0-lo0,hi1-lo1)<.035:continue
            C.solid_surface('curved clerestory return glazing',[(*p,lo0),(*q,lo1),(*q,hi1),(*p,hi0)],.018,'glass','clerestory glazing')
            C.beam('clerestory mullion',(*p,lo0),(*p,hi0),.05,.07,'trim','clerestory frame')
            C.beam('continuous curved glulam head',(*p,hi0+.08),(*q,hi1+.08),.18,.20,'timber','clerestory frame')
            C.beam('seated clerestory sill',(*p,lo0),(*q,lo1),.14,.16,'trim','clerestory frame')

def roof_system():
    lower=lambda x,y:roof_z(y)+.5+1.2*(1-(x/12)**2)
    upper=lambda x,y:13.0+1.45*(1-(x/11)**2)+1.0*(1-((y-4.5)/7.5)**2)
    xs=[-17,-12,-11,-9,9,11,12,17];ys=[-15,-12,-10.4,-3,0,10,12,15]
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            x,y=(a+b)/2,(c+d)/2
            if (abs(x)<12 and -10.4<y<10) or (abs(x)<9 and -12<y<-10.4) or (abs(x)<11 and -3<y<12):continue
            C.solid_surface('perimeter living roof',[(xx,yy,roof_z(yy)) for xx,yy in [(a,c),(b,c),(b,d),(a,d)]],.22,'roof')
            planted_roof(a+.01,b-.01,c+.01,d-.01,lambda x,y:roof_z(y)+.01)
    roof_tier(12,-12,10,lower,lambda x,y:roof_z(y),-7.5,[(-11,11,-3,12)],True)
    roof_tier(11,-3,12,upper,lambda x,y:lower(x,y) if y<=10 else roof_z(y),4.5)

def library():
    w,d=34,30
    box('ground-bearing slab',(0,0,.12),(w,d,.24),'foundation','foundation')
    front,right,rear,left=B.faces(w,d)
    for face in (front,rear):
        holes=[dict(id=f'{face.label} ground bay {i}',u=u,z=.24,w=4.4,h=3.4,cols=3) for i,u in enumerate((2.5,7.4,26.6,31.5))]
        # Central two-leaf entrance has a full-depth opening in the carrier.
        holes.append(dict(id=face.label+' entry',u=17,z=.24,w=8.8,h=3.8,cols=6,door=True))
        B.open_wall(face,w,.24,9.4,holes,depth=.30)
        for obj in C.objects():
            if obj.name.startswith(face.label+' entry'):obj.location+=face.n*1.4
        for i in range(170):
            u=(i+.5)*w/170;face.part('charred timber board',u,-.055,6.90,.18,.10,5.0,'wall','timber cladding',0)
        # Recessed timber entrance surround, including soffit and two returns.
        for s in (-1,1):
            face.part('entrance charcoal cheek',17+s*4.55,.2,2.10,.22,2.65,4.2,'wall','entrance',0)
            face.part('entrance timber return',17+s*4.40,.2,2.10,.075,2.65,4.2,'timber','entrance',0)
        face.part('entry canopy',17,.2,4.21,9.3,2.7,.22,'wall','entrance',0)
        face.part('warm timber porch soffit',17,.2,4.09,8.8,2.65,.045,'timber','entrance',0)
        face.part('continuous entrance threshold',17,.1,.10,8.8,2.8,.20,'foundation','entrance',0)
    for face in (left,right):
        # The whole gable is an enclosed physical curtain wall with visible timber structure.
        for i in range(20):
            u=i*1.5;v=u+1.5;y=-15+(u+v)/2
            top=roof_z(y)-.18
            face.panel('shaped gable pane',[(u,.24),(v,.24),(v,roof_z(-15+v)-.18),(u,roof_z(-15+u)-.18)],.14,.153,'glass','gable glazing')
            C.beam('gable mullion',face.p(u,.14,.24),face.p(u,.14,roof_z(-15+u)-.18),.055,.10,'trim','gable glazing')
            for z in (3.5,6.6,9.1):
                if z<top:C.beam('gable transom',face.p(u,.14,z),face.p(v,.14,z),.055,.08,'trim','gable glazing')
        for u in (0,30):face.part('glulam edge column',u,-.28,roof_z(-15+u)/2,.45,.60,roof_z(-15+u),'timber','gable structure',0)
        for i in range(4):
            u=i*7.5;u2=u+7.5;apex=(u+u2)/2;y=-15+u;yy=-15+u2
            face.part('Y support stone shoe',apex,-.28,.12,.65,.80,.24,'foundation','gable structure',0)
            C.beam('grounded Y timber stem',face.p(apex,-.28,.24),face.p(apex,-.28,4.3),.48,.64,'timber','gable structure')
            C.beam('glulam fork',face.p(apex,-.28,4.3),face.p(u,-.28,roof_z(y)-.2),.46,.60,'timber','gable structure')
            C.beam('glulam fork',face.p(apex,-.28,4.3),face.p(u2,-.28,roof_z(yy)-.2),.46,.60,'timber','gable structure')
            C.beam('gable rafter',face.p(u,-.28,roof_z(y)),face.p(u2,-.28,roof_z(yy)),.44,.64,'timber','gable structure')
    # Main roof is partitioned around both raised monitors; no opaque roof behind their glazing.
    roof_system()
    for y in (-15,15):box('eave coping',(0,y,roof_z(y)+.02),(34.5,.24,.25),'trim','roof edge')
    # Glulam cross frames continue through the reading hall, beyond the facade.
    for x in (-12,-6,0,6,12):
        for y in (-13.8,13.8):
            if x!=0:box('interior glulam column',(x,y,4.5),(.32,.32,9),'timber','structure')
            else:
                for xx in (-4.4,4.4):box('portal bearing column',(xx,y,4.5),(.32,.32,9),'timber','structure')
                C.beam('clear-span entry header',(-4.4,y,9),(4.4,y,9),.4,.6,'timber','structure')
            C.beam('interior glulam rafter',(x,y,9.1),(x,0,11.7),.28,.5,'timber','structure')
    # Low mezzanine surrounds a double-height reading room; clear central entrance.
    for x in (-10.5,10.5):
        box('mezzanine deck',(x,2,4.25),(10,22,.22),'floor','occupied floor')
        for y in (-8,2,12):box('mezzanine post',(x,y,2.15),(.25,.25,4.3),'timber','structure')
        for y in range(-9,14):
            C.rod('mezzanine guard',(x-math.copysign(5,x),y,4.36),(x-math.copysign(5,x),y,5.42),.025,'hardware','guard')
        C.beam('mezzanine handrail',(x-math.copysign(5,x),-9,5.42),(x-math.copysign(5,x),13,5.42),.05,.05,'timber','guard')
    # Straight enclosed stair at the rear connects actual floor datums.
    for i in range(24):
        h=(i+1)*4.25/24;box('library stair tread',(0,5+i*.29,h/2),(2.4,.30,h),'timber','circulation')
    box('stair landing',(0,12.3,4.25),(12,1.6,.22),'floor','circulation')
    for x in (-1.25,1.25):
        C.beam('stair handrail',(x,4.85,1.08),(x,11.95,5.4),.05,.05,'timber','circulation')
        for i in range(0,24,3):C.rod('stair baluster',(x,5+i*.29,(i+1)*4.25/24),(x,5+i*.29,(i+1)*4.25/24+1.05),.022,'hardware','circulation')
    for z in (.24,4.37):
        for x in (-12,-7,7,12):
            for y in (-4,2,8):books(x,y,z,3)
    for x in (-9,0,9):
        for y in (-10,-6):B.table(x,y,.24)
    B.label('LIBRARY',(0,-16.17,4.12),.24)

def roster():
    target=(0,0,7)
    views=[dict(name=n,location=p,target=target,ortho_scale=49) for n,p in [('front',(0,-70,7)),('left_side',(-70,0,7)),('right_side',(70,0,7)),('rear',(0,70,7))]]
    views += [dict(name='front_corner',location=(49,-55,30),target=target),dict(name='aerial',location=(43,-50,62),target=target),dict(name='top',location=(0,0,95),target=(0,.001,0),ortho_scale=49),dict(name='rear_side',location=(-48,53,30),target=target)]
    views += [dict(name=n,location=p,target=t,whole=False,lens=l) for n,p,t,l in [('facade_close',(8,-23,4),(0,-15,3),40),('architecture_close',(27,-20,17),(17,-4,8),36),('glass_close',(23,-8,3),(13,-3,3),40),('roof_contact',(21,-20,27),(0,0,13),40),('program_interior',(3,-11,2),(4,4,4),22),('walk',(22,-24,1.65),(12,-9,6),26)]]
    return views

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['library'],required=True);p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=next(s for s in json.loads(a.lock.read_text())['entries'] if s['kind']==a.kind)
    entry=dict(archetype_id=source['archetype_id'],variant_id=source['variant_id'],directory='.',_reference_root=str(Path(source['sources'][0]['path']).parent),sources=[dict(s,original_path=s['path'],path='sources/'+Path(s['path']).name) for s in source['sources']])
    views=roster();manifest=dict(candidate=f'neighbourhood-library-clay-v{a.version:03d}',method=C.METHOD,archetype_id=entry['archetype_id'],variant_id=entry['variant_id'],representation_kind='architectural_clay',camera_roster=views,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=34,depth=30,height=15.6),floors=2,front='-Y',bottom_datum_m=0,measurement_basis='Catalogue proportions and plausible metric timber/library modules; not surveyed'),
        identity_contract=['Charred vertical timber above glazed ground floor','Large glazed gable and exposed branching glulam','Planted roof with two raised curved clerestories and two rooflight strips','Recessed timber entry; book stacks, reading tables, actual mezzanine and stair'],
        hidden_view_assumptions=['Rear uses the same cladding and service-entry grammar; interior stacks, stair and mezzanine are inferred library programme','Source views disagree on precise clerestory extent; roof composition follows the oblique and top'],
        limitations=['Native fixed two-storey assembly; no mesh stretching','Architectural-clay delivery consistent with active local buildings; not a textured keeper','Runtime ground/access/edit/export acceptance pending'])
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE.parent/'showcase_building_trio/build.py'])
    if out is None:return
    cams=C.setup(PALETTE,views,1440);C.fit=B.efficient_fit;C.bpy.context.scene.cycles.samples=20
    bs=C.MATS['glass'].node_tree.nodes['Principled BSDF'];bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.08
    for x in (-10,0,10):
        for y in (-8,5):C.qa_room_light('reading hall',(x,y,8.8),700,5)
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    library();C.deliver(out,manifest,cams)

if __name__=='__main__':main()
