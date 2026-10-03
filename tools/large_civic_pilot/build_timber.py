"""Original timber sanctuary, with a complete occupied hall and low annex."""
import argparse
import json
import math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import build_church as G
C=G.C;B=G.B
from walking import attach_church_walk

PALETTE=dict(G.PALETTE,wall=(.53,.34,.17),timber=(.49,.29,.12),trim=(.22,.15,.10),
    stone=(.57,.52,.41),roof=(.09,.115,.13),interior=(.63,.46,.28),floor=(.52,.51,.46),glass=(.50,.64,.67))
box=G.box

def window(face,owner,name,u,z,w,h,depth=.32):
    face.cut(owner,name,u,z,w,h,depth)
    face.window(name,u,z,w,h,1,2,'hardware',.14,.045,True,False,depth)

def boards(face,length,z0,z1,holes=()):
    # Bound each vertical timber batten to its own wall and opening schedule.
    for i in range(math.floor(length/.20)):
        u=.10+i*.20;segments=[(z0,z1)]
        for cu,cz,w,h in holes:
            if abs(u-cu)>w/2+.06:continue
            segments=[piece for lo,hi in segments for piece in ((lo,min(hi,cz)),(max(lo,cz+h),hi)) if piece[1]-piece[0]>.01]
        for lo,hi in segments:face.part('cedar board joint',u,-.007,(lo+hi)/2,.012,.018,hi-lo,'trim','cedar cladding',0)

def timber():
    box('sanctuary floor',(0,0,.02),(24,38,.04),'floor','foundation')
    # Sanctuary side walls and real slit windows; annex connection is a full opening.
    for side in (-1,1):
        f=C.Face((side*12,-19,0),(0,1,0),(-side,0,0),'sanctuary side '+str(side))
        wall=f.wall('timber side envelope',0,38,.04,8.1,.32,'interior')
        holes=[]
        for i in range(7):
            u=3.25+i*5.1
            # Rear-right annex covers the lower wall: high clerestory above it.
            z,h=(4.6,3.0) if side==1 and u>18 else (.80,6.80)
            window(f,wall,'tall side window',u,z,1.05,h);holes.append((u,z,1.05,h))
        if side==1:
            f.cut(wall,'open annex connection',28,.04,3.8,3.2,.32);holes.append((28,.04,3.8,3.2))
        boards(f,38,.67,8.1,holes)
        plinth=f.part('stone plinth',19,.01,.32,38,.40,.56,'stone','plinth',0)
        # Remove the plinth at the annex passage; the remaining base is outside.
        if side==1:
            f.cut(plinth,'plinth passage',28,0,3.8,.8,.5)
        C.beam('eaves gutter',(side*12.4,-20.3,8.16),(side*12.4,19.5,8.16),.14,.15,'roof','drainage')
    # Rear is a full gable and occupied altar backdrop, with a cut high slit.
    rear=C.Face((-12,19,0),(1,0,0),(0,-1,0),'rear')
    wall=rear.panel('rear timber gable',[(0,.04),(24,.04),(24,8.1),(12,17),(0,8.1)],0,.36,'interior');wall['rlasm_wall_carrier']=True
    window(rear,wall,'altar high slit',12,6,1,7,.36)
    for i in range(120):
        u=.1+.2*i;top=17-abs(u-12)*8.9/12
        ranges=[(.65,top)] if abs(u-12)>.56 else [(.65,6),(13,top)]
        for lo,hi in ranges:
            if hi>lo:rear.part('rear cedar joint',u,-.006,(lo+hi)/2,.012,.015,hi-lo,'trim','cedar cladding',0)
    rear.part('rear stone plinth',12,.01,.32,24,.42,.56,'stone','plinth',0)
    for side in (-1,1):
        C.solid_surface('standing seam roof',[(0,-20.4,17.45),(side*12.45,-20.4,8.11),(side*12.45,19.45,8.11),(0,19.45,17.45)],.22,'roof')
        C.solid_surface('timber roof soffit',[(0,-20.4,17.20),(side*12.45,-20.4,7.86),(side*12.45,19.45,7.86),(0,19.45,17.20)],.12,'interior','roof lining')
        for i in range(1,75):
            y=-20.4+i*39.85/75
            C.beam('raised metal seam',(0,y,17.47),(side*12.45,y,8.13),.026,.036,'roof','standing seams')
        C.beam('front rake timber',(0,-20.35,17.14),(side*12.3,-20.35,7.94),.40,.48,'timber','portal structure')
        for y in (-19.9,-13.9,-8.65,-3.4,1.85,7.1,12.35,18):
            C.beam('glulam rafter',(0,y,16.48),(side*11.5,y,7.85),.34,.60,'timber','portal structure')
            box('glulam column',(side*11.5,y,3.97),(.48,.42,7.86),'timber','portal structure')
            box('steel column shoe',(side*11.5,y,.18),(.58,.53,.28),'hardware','column shoes')
        for y in ((-19,18.5) if side==-1 else (-19,)):
            C.rod('downpipe',(side*12.32,y,.05),(side*12.32,y,8.0),.06,'roof','drainage',10)
    C.beam('ridge cap',(0,-20.4,17.49),(0,19.45,17.49),.16,.12,'roof','ridge')
    # Recessed glazed gable, with uninterrupted open entrance through its base.
    front=C.Face((-12,-18.8,0),(1,0,0),(0,1,0),'glazed front')
    divisions=[-11.22,-7.5,-3.75,-2,2,3.75,7.5,11.22]
    for l,r in zip(divisions,divisions[1:]):
        bottom=3.45 if l==-2 else .07
        tl=16.78-abs(l)*.75;tr=16.78-abs(r)*.75
        peak=[(12,16.72)] if l<0<r else []
        front.panel('recessed gable pane',[(12+l+.04,bottom),(12+r-.04,bottom),(12+r-.04,tr-.06),*peak,(12+l+.04,tl-.06)],.10,.112,'glass','glazed gable')
    for x in divisions:
        top=16.78-abs(x)*.75
        box('front glazing mullion',(x,-18.84,top/2),(.075,.13,top),'hardware','glazed gable')
    for side in (-1,1):
        C.beam('seated sloping glazing perimeter',(0,-18.85,16.94),(side*11.6,-18.85,8.24),.18,.55,'timber','glazed gable')
    for z in (3.45,8.0):
        length=min(22.44,(16.78-z)/.75*2)
        box('front glazing transom',(0,-18.84,z),(length,.13,.08),'hardware','glazed gable')
    # Deep timber portals at both edges frame the glass; parked door leaves.
    for x in (-11.7,11.7):box('deep front timber jamb',(x,-19.6,4),(.65,1.6,8),'timber','portal structure')
    for x in (-2.04,2.04):box('open front door leaf',(x,-19.75,1.68),(.10,1.85,3.28),'timber','entrance')
    box('door header',(0,-18.85,3.43),(4.25,.24,.20),'timber','entrance')
    C.mesh('shallow paved approach',[(-3,-24,0),(3,-24,0),(2.2,-18.8,.04),(-2.2,-18.8,.04),(-2.2,-18.8,0),(2.2,-18.8,0)],[(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2),(2,5,4,3)],'stone','access')
    # Low rear-right community annex with real windows and open hall connection.
    box('annex floor',(16,9,.02),(8,20,.04),'floor','foundation')
    for f,length in [(C.Face((12,-1,0),(1,0,0),(0,1,0),'annex front'),8),
                     (C.Face((20,-1,0),(0,1,0),(-1,0,0),'annex side'),20),
                     (C.Face((20,19,0),(-1,0,0),(0,-1,0),'annex rear'),8)]:
        owner=f.wall('annex envelope',0,length,.04,4.3,.32,'interior');holes=[]
        for i in range(1,round(length/4)):
            u=length*i/round(length/4);window(f,owner,'annex window',u,1.05,1.6,2.3);holes.append((u,1.05,1.6,2.3))
        boards(f,length,.65,4.3,holes);f.part('annex stone base',length/2,.02,.32,length,.40,.56,'stone','plinth',0)
    box('annex roof',(16,9,4.39),(8.6,20.6,.22),'roof','annex roof')
    box('annex ceiling',(16,9,4.24),(8,20,.08),'interior','ceiling lining')
    for y in (3,15):
        box('community table',(16,y,.79),(3.6,1.3,.12),'timber','annex furniture')
        for x in (14.4,17.6):
            for yy in (y-.5,y+.5):box('table leg',(x,yy,.4),(.10,.10,.76),'timber','annex furniture')
        for x in (14.8,16,17.2):
            for yy in (y-1.05,y+1.05):
                box('annex chair seat',(x,yy,.46),(.46,.46,.08),'timber','annex furniture')
                box('annex chair back',(x,yy+math.copysign(.21,yy-y),.72),(.46,.06,.54),'timber','annex furniture')
                for dx in (-.17,.17):
                    for dy in (-.17,.17):box('chair leg',(x+dx,yy+dy,.23),(.055,.055,.46),'hardware','annex furniture')
    # Occupied church programme, generous centre/side/transverse aisles.
    for side in (-1,1):
        for i in range(19):
            y=-14.4+i*1.4
            if -.8<y<1:continue
            x=side*5
            box('timber pew seat',(x,y,.48),(6,.45,.09),'timber','pews')
            box('timber pew back',(x,y-.21,.81),(6,.065,.64),'timber','pews')
            for dx in (-2.93,2.93):box('pew end support',(x+dx,y,.48),(.12,.56,.88),'timber','pews')
    box('altar table',(0,16.4,1.1),(3,1.2,.16),'timber','altar')
    for x in (-1.1,1.1):box('altar foot',(x,16.4,.55),(.3,.9,1.02),'timber','altar')
    G.cross(0,18.54,2.2,2.1)
    for x in (-6,6):
        for y in (-12,-3,6,14):
            ceiling=17.08-.75*abs(x)
            C.rod('pendant cord',(x,y,ceiling+.04),(x,y,6),.015,'hardware','lighting')
            C.rod('pendant cylinder',(x,y,5.55),(x,y,6),.11,'hardware','lighting',12)
            C.rod('pendant diffuser',(x,y,5.52),(x,y,5.55),.09,'white','lighting',12)

def cameras():
    target=(4,0,8)
    roster=[dict(name=n,location=p,target=target,ortho_scale=62) for n,p in [('front',(4,-88,8)),('left_side',(-88,0,8)),('right_side',(88,0,8)),('rear',(4,88,8))]]
    roster += [dict(name='front_corner',location=(60,-75,39),target=target),dict(name='aerial',location=(50,-65,70),target=target),
      dict(name='top',location=(4,0,110),target=(4,.001,0),ortho_scale=64),dict(name='rear_side',location=(63,73,38),target=target)]
    roster += [dict(name=n,location=p,target=t,whole=False,lens=l) for n,p,t,l in [
      ('facade_close',(18,-37,10),(0,-19,6),35),('architecture_close',(18,-31,18),(8,-20,12),40),
      ('glass_close',(17,-10,4),(12,-10,4),35),('program_interior',(0,-16,1.7),(0,16,6),20),
      ('vault_interior',(0,-8,2),(0,7,13),20),('walk',(0,-29,1.7),(0,-18,5),26),
      ('entrance_access',(5,-26,2),(0,-17,1.6),30),('annex_interior',(16,7,1.7),(16,17,2),24)]]
    return roster

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--lock',type=Path,required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');p.add_argument('--resolution',type=int,default=1200)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=json.loads(a.lock.read_text())['entries'][0]
    entry=dict(source,directory='.',_reference_root=str(Path(source['sources'][0]['path']).parent),sources=[dict(s,original_path=s['path'],path='sources/'+Path(s['path']).name) for s in source['sources']]);roster=cameras()
    manifest=dict(candidate=f'timber-sanctuary-church-clay-v{a.version:03d}',method=C.METHOD,archetype_id=source['archetype_id'],variant_id=source['variant_id'],representation_kind='architectural_clay',camera_roster=roster,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
      measurement_contract=dict(dimensions_m=dict(width=33,depth=44,height=18),floors=1,front='-Y',bottom_datum_m=0,measurement_basis='Original generated design board; conceptual dimensions, not surveyed'),
      identity_contract=['Single steep gable, glazed front, eight timber portal frames','Low flat-roof community annex at rear-right','Seven tall side window bays, rear slit, pews and altar'],
      hidden_view_assumptions=['Rear and annex window schedules interpreted from generated design; one occupied floor'],
      source_origin='Original generated design reference, not a photograph of a real church',limitations=['Architectural clay, no textured keeper claim','Fixed native dimensions','Browser access proof required'])
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE/'build_church.py',HERE/'walking.py',HERE.parent/'showcase_building_trio/build.py'])
    if out is None:return
    cams=C.setup(PALETTE,roster,a.resolution);C.fit=B.efficient_fit;C.bpy.context.scene.cycles.samples=20
    for y in (-12,0,12):C.qa_room_light('sanctuary',(0,y,10),1500,6)
    C.qa_room_light('annex',(16,9,3.7),650,4)
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.5,-.4,-.4);sun.data.energy=2;sun.data.angle=.16
    timber();attach_church_walk(C,'timber');C.deliver(out,manifest,cams)

if __name__=='__main__':main()
