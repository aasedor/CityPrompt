"""Source-locked twin-gable childcare pilot. Run with Blender, output externally.

The dedicated envelope and programme are authored here. Shared modules provide
mesh primitives, furniture components, and exact-GLB evidence utilities only.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'neighborhood_refinement'))
import geometry_core as C
import build_neighborhood as B
import refinements as R
import walking as W

FLOOR = .14
OBSTACLES = []
PALETTE = dict(B.PALETTE, wall=(.72,.61,.44), trim=(.24,.31,.23),
               timber=(.53,.36,.19), roof=(.42,.46,.46), interior=(.82,.79,.67),
               floor=(.62,.51,.35), furniture=(.42,.53,.34), sand=(.65,.53,.34),
               leaf=(.20,.30,.10), flower=(.67,.58,.30), ceiling=(.82,.81,.75),
               lamp=(.94,.85,.68))


def cameras():
    result=[]
    for name,loc in [('front',(1,-48,8)),('front_corner',(35,-40,23)),
                     ('aerial',(33,-36,46)),('left_side',(-47,0,11)),
                     ('right_side',(47,0,11)),('rear',(0,48,13)),
                     ('rear_side',(-36,38,25))]:
        result.append(dict(name=name,location=loc,target=(1,0,2),whole=True,lens=52))
    for name,loc,target,lens in [
        ('facade_close',(-14,-23,6),(-8,-10,2.8),48),
        ('architecture_close',(5,-20,5),(0,-8.5,1.8),38),
        ('glass_close',(-10,-14,2.1),(-8,-8,1.4),38),
        ('roof_contact',(8,-15,12),(2,-5,5.1),40),
        ('lobby',(1.8,-7.1,1.75),(-1.8,-3.7,1.3),22),
        ('classroom_left',(-4.7,-7.8,1.7),(-9,-3,1.2),24),
        ('classroom_right',(4.6,-7.8,1.7),(9,-3,1.1),24),
        ('washroom',(8.7,2.2,2.1),(9.9,3.8,.85),14),
        ('washroom_toilets',(9.05,2.85,1.75),(9.1,4.6,.6),24),
        ('washroom_sinks',(10.3,3.4,1.6),(11.9,2.5,.85),28),
        ('nap_room',(-6.6,2,1.6),(-10.5,6.4,.8),24),
        ('garden_connection',(.6,-1.5,1.7),(0,6.5,1.1),30),
        ('play_garden',(18,-6,3.5),(16,4,1),30),
        ('staff_room',(6.6,6,1.7),(11.4,8.8,1.2),22),
        ('stroller_bay',(6,-15,2.3),(3.4,-10.65,1.2),30),
    ]:
        result.append(dict(name=name,location=loc,target=target,whole=False,lens=lens))
    return result


def hole(name,u,w,z=FLOOR,h=2.4,door=False):
    return dict(id=name,u=u,w=w,z=z,h=h,door=door)


def wall(face,lo,hi,holes=(),height=4.5,role='wall',depth=.30):
    face.wall(face.label,lo,hi,0,height,depth,role,holes)
    cuts=sorted([h for h in holes if h.get('door')],key=lambda h:h['u'])
    edges=[lo]
    for h in cuts:edges.extend([h['u']-h['w']/2,h['u']+h['w']/2])
    edges.append(hi)
    for a,b in zip(edges[::2],edges[1::2]):
        pts=[face.p(u,d,0) for u in (a,b) for d in (0,depth)]
        OBSTACLES.append([min(p[0] for p in pts),max(p[0] for p in pts),
                          min(p[1] for p in pts),max(p[1] for p in pts),0,height])
    for h in holes:
        if h.get('door'):
            if h['id'] in ('entrance door','garden exit door'):
                u,z,w,ht=h['u'],h['z'],h['w'],h['h']
                for side in (-1,1):face.part(h['id']+' jamb',u+side*(w/2-.025),.07,z+ht/2,.05,.14,ht,'trim')
                face.part(h['id']+' lintel',u,.07,z+ht,w,.14,.06,'trim')
                leaf=C.Face(face.p(u-w/2+.06,.10,0),face.n,face.t,h['id']+' open leaf')
                leaf.window(h['id']+' open leaf glazing',(w-.12)/2,z,w-.12,ht-.04,1,1,'trim',.03,sill=False,depth=.1,kind='open glazed leaf')
            else:R.open_door(face,h['id'],h['u'],h['z'],h['w'],h['h'])
        else:
            face.window(h['id'],h['u'],h['z'],h['w'],h['h'],3 if h['w']>3 else 2,1,
                        'trim',.16,.045,True,False,depth)
            if 'classroom picture' in h['id']:
                face.part(h['id']+' high transom',h['u'],.145,h['z']+h['h']*.80,h['w']-.10,.10,.05,'trim')


def light(name,x,y,power=260):
    o=C.qa_room_light(name,(x,y,4.05),power,3)
    if hasattr(o.data,'specular_factor'):o.data.specular_factor=0
    R.lamp(x,y,4.22,1.2)


def shelf(name,x,y,w=2):
    for z in (.22,.6,.98):C.box(name+' shelf',(x,y,z),(w,.36,.05),'timber','furniture')
    for xx in (x-w/2,x+w/2):C.box(name+' side',(xx,y,.60),(.06,.38,.85),'timber','furniture')
    for i in range(8):
        C.box(name+' book',(x-w*.43+i*w*.11,y,.79),(.09,.22,.28+.03*(i%3)),'furniture','furniture')


def child_table(x,y):
    C.box('child table top',(x,y,.66),(1.4,.8,.06),'timber','furniture')
    for dx in (-.56,.56):
        for dy in (-.28,.28):C.box('child table leg',(x+dx,y+dy,.38),(.045,.045,.48),'timber','furniture')
    for dx in (-.42,.42):
        for dy in (-.85,.85):
            C.box('child chair seat',(x+dx,y+dy,.43),(.34,.34,.04),'furniture','furniture')
            C.box('child chair back',(x+dx,y+dy+(.14 if dy>0 else -.14),.60),(.34,.035,.33),'furniture','furniture')
            for lx in (-.13,.13):
                for ly in (-.13,.13):C.box('child chair leg',(x+dx+lx,y+dy+ly,.275),(.025,.025,.27),'timber','furniture',0)


def wing(cx):
    x0,x1=cx-5,cx+5
    front=C.Face((cx,-10,0),(1,0,0),(0,1,0),f'{cx} front')
    wall(front,-5,5,[hole(f'{cx} classroom picture window',0,5.6,.62,3.0)])
    back=C.Face((cx,10,0),(-1,0,0),(0,-1,0),f'{cx} rear')
    wall(back,-5,5,[hole(f'{cx} rear window',0,4,1,1.8)])
    # Gable infill and closed pitched roof share the same eave/ridge graph.
    for ya,yb in [(-10,-9.7),(9.7,10)]:
        C.prism('brick gable',[(x0,4.5),(cx,7.2),(x1,4.5)],'y',ya,yb,'wall')
    outer=x0 if cx<0 else x1
    side=C.Face((outer,0,0),(0,1,0),(1 if cx<0 else -1,0,0),f'{cx} outer side')
    hs=[hole(f'{cx} side window {i}',y,3.3,.75,2.15) for i,y in enumerate((-6.7,-1,7.1))]
    if cx>0:hs.append(hole('secure play garden doorway',-3.5,1.4,door=True))
    wall(side,-9.7,9.7,hs)
    inner=x1 if cx<0 else x0
    inside=C.Face((inner,0,0),(0,1,0),(-1 if cx<0 else 1,0,0),f'{cx} garden side')
    wall(inside,-9.7,9.7,[hole(f'{cx} lobby connection',-5.5,1.7,door=True),
                           hole(f'{cx} garden window',3,3,.85,2),
                           hole(f'{cx} garden rear window',7.3,2,.85,2)])
    C.box('wing floor',(cx,0,.09),(10,20,.10),'floor','floors',0)
    C.box('wing ceiling',(cx,0,4.38),(9.4,19.4,.12),'ceiling','ceiling',0)
    for sign in (-1,1):
        xe=cx+sign*5.35;ze=7.2-5.35*.54
        # No low inner overhang at connector: it meets the higher joining roof.
        inner_slope=(cx<0 and sign>0) or (cx>0 and sign<0)
        for ya,yb in [(-10.35,-8.25),(-8.25,-2.85),(-2.85,10.35)]:
            joint=inner_slope and ya==-8.25
            enda=cx+sign*5 if joint else xe
            endb=cx+sign*((7.2-5.8)/.54) if joint else xe
            outline=[(cx,ya,7.2),(enda,ya,7.2-abs(enda-cx)*.54),
                     (endb,yb,7.2-abs(endb-cx)*.54),(cx,yb,7.2)]
            C.solid_surface('standing seam roof slope',outline,.10)
        for i in range(39):
            yy=-10.3+i*.535
            joinz=4.5+(yy+8.25)/5.4*1.3
            end=cx+sign*((7.2-joinz)/.54) if inner_slope and -8.25<yy<-2.85 else xe
            C.beam('roof standing seam',(cx,yy,7.225),(end,yy,7.225-abs(end-cx)*.54),.018,.025,'roof','roof')
        for yy in (-10.36,10.36):
            C.beam('timber gable fascia',(cx,yy,7.13),(xe,yy,ze-.07),.14,.14,'timber','roof')
    C.rod('ridge cap',(cx,-10.37,7.205),(cx,10.37,7.205),.065,'roof','roof')


def build():
    C.box('site base',(2,0,.02),(38,30,.04),'paving','site',0)
    wing(-8);wing(8)
    # Pitched connector and wing planes share solved diagonal intersections.
    C.box('lobby floor',(0,-5.5,.09),(6,5,.10),'floor','floors',0)
    for y,t,n,label in [(-8,(1,0,0),(0,1,0),'entrance'),(-3,(-1,0,0),(0,-1,0),'garden exit')]:
        face=C.Face((0,y,0),t,n,label)
        wall(face,-3,3,[hole(label+' door',0,1.6,door=True),hole(label+' transom',0,1.6,2.65,1.15),hole(label+' left light',-1.95,1.5,.22,3.58),hole(label+' right light',1.95,1.5,.22,3.58)],4.4)
    C.box('connector ceiling',(0,-5.5,4.22),(6,5,.12),'ceiling','ceiling',0)
    rear=8-(7.2-5.8)/.54
    C.solid_surface('pitched connector roof',[(-3,-8.25,4.5),(3,-8.25,4.5),(rear,-2.85,5.8),(-rear,-2.85,5.8)],.12)
    C.prism('connector rear infill',[(-rear,5.78),(-3,4.35),(3,4.35),(rear,5.78)],'y',-3.02,-2.87,'wall')
    for sign in (-1,1):C.beam('diagonal roof joint flashing',(sign*3,-8.25,4.53),(sign*rear,-2.85,5.83),.09,.04,'roof','roof')
    for i in range(-10,11):
        x=i*.5;ya=-8.25+max(0,abs(x)-3)/(rear-3)*5.4;za=4.5+(ya+8.25)/5.4*1.3
        C.beam('connector standing seam',(x,ya,za+.025),(x,-2.85,5.825),.018,.025,'roof','roof')
    C.box('porch canopy',(0,-9.15,4.16),(7.5,2.3,.20),'timber','structure')
    C.box('porch metal weather cap',(0,-9.15,4.28),(7.6,2.4,.045),'roof','roof')
    for x in (-2.5,2.5):C.box('porch column',(x,-10.1,2.07),(.14,.14,4.14),'hardware','structure')
    C.box('entrance apron',(0,-11.2,.09),(5.2,6.4,.10),'paving','site',0)
    C.box('rear garden path',(0,3.6,.09),(2.4,13.2,.10),'paving','site',0)
    C.box('side play path',(16,-3.5,.09),(6,2,.10),'paving','site',0)
    # Rooms flank clear inner corridors; physical partitions stop at door apertures.
    for cx in (-8,8):
        f=C.Face((cx,1,0),(1,0,0),(0,1,0),'classroom rear partition '+str(cx))
        wall(f,-4.7,4.7,[hole('classroom rear door '+str(cx),3.4 if cx<0 else -3.4,1.4,door=True)],4.4,'interior',.12)
        child_table(cx,-6.6);child_table(cx,-2.5)
        shelf('classroom reading shelf',cx-2.8 if cx<0 else cx+2.8,-.05,2.4)
        C.box('reading mat',(cx,-.5,.16),(2.1,1.1,.04),'furniture','furniture')
        for dx in (-.65,.65):C.box('reading cushion',(cx+dx,-.5,.30),(.55,.55,.24),'furniture','furniture')
        light('classroom light',cx,-5,380);light('classroom rear light',cx,-.1,240)
    # Left rear sleeping room, separated from a wide circulation strip.
    f=C.Face((-5.8,5.4,0),(0,1,0),(-1,0,0),'nap room wall')
    wall(f,-4.28,4.28,[hole('nap room doorway',-2,1.3,door=True)],4.4,'interior',.12)
    for x in (-11.2,-8.5):
        for y in (3.6,6.5,8.7):
            C.box('nap cot frame',(x,y,.29),(1.5,.75,.30),'timber','furniture')
            C.box('nap cot mattress',(x,y,.49),(1.46,.71,.10),'interior','furniture')
            C.box('nap pillow',(x-.46,y,.56),(.36,.59,.09),'furniture','furniture')
    light('nap room',-9,5.5,200)
    # Right rear washroom and staff/kitchen room with independent corridor doors.
    f=C.Face((5.8,5.4,0),(0,1,0),(1,0,0),'service corridor wall')
    wall(f,-4.28,4.28,[hole('washroom doorway',-2.5,1.3,door=True),hole('staff doorway',2.1,1.3,door=True)],4.4,'interior',.12)
    f=C.Face((9.23,5.3,0),(1,0,0),(0,1,0),'staff washroom divider')
    wall(f,-3.31,3.31,[],4.4,'interior',.12)
    for x in (8.2,10):
        C.box('child toilet base',(x,4.6,.32),(.40,.58,.36),'interior','furniture')
        C.box('child toilet seat',(x,4.5,.53),(.46,.62,.07),'ceiling','furniture')
        C.box('toilet seat recess',(x,4.48,.57),(.24,.34,.018),'hardware','furniture')
        C.box('toilet cistern',(x,4.87,.66),(.40,.18,.58),'interior','furniture')
    C.box('toilet privacy divider',(9.1,4.3,.88),(.06,1.5,1.45),'timber','furniture')
    C.box('child sink cabinet',(11.95,2.5,.44),(.7,1.65,.60),'timber','furniture')
    C.box('child sink rim',(11.95,2.5,.77),(.74,1.7,.07),'ceiling','furniture')
    for y in (2.08,2.92):
        C.box('recessed sink bowl',(11.84,y,.813),(.40,.50,.013),'hardware','furniture')
        C.rod('tap',(12.1,y,.82),(12.1,y,1),.025,'hardware','furniture')
        C.rod('tap spout',(12.1,y,1),(11.94,y,1),.025,'hardware','furniture')
    C.box('changing table',(7.2,1.7,.72),(1.3,.75,1.16),'timber','furniture')
    C.box('changing cushion',(7.2,1.7,1.34),(1.2,.65,.10),'interior','furniture')
    light('washroom',9,3,220)
    C.box('staff kitchen base',(11.95,7.5,.61),(.9,3.6,.94),'timber','furniture')
    C.box('staff worktop',(11.95,7.5,1.10),(.98,3.65,.05),'stone','furniture')
    C.box('staff inset sink',(11.85,7,1.13),(.55,.7,.015),'hardware','furniture')
    C.rod('staff tap',(12.25,7,1.1),(12.25,7,1.4),.025,'hardware','furniture')
    C.box('fridge',(10.2,9.1,1.05),(1,.85,1.82),'ceiling','furniture')
    B.desk(8.5,7.7,.14,False);shelf('staff supplies',7,9.3,1.5);light('staff room',9,7.5,230)
    # Reception hugs lobby side, keeping entry/garden axis and both wing doors clear.
    C.box('reception desk',(-1.95,-4.3,.66),(1.35,.70,1.04),'timber','furniture')
    shelf('lobby cubbies',1.9,-3.7,1.5);light('lobby',0,-5.5,300)
    # Source cedar bay sits in front of the right classroom wall, not behind it.
    C.box('stroller shelter canopy',(3.45,-10.7,3.50),(2.4,1.55,.18),'timber','structure')
    C.box('stroller shelter weather cap',(3.45,-10.7,3.61),(2.48,1.62,.035),'roof','roof')
    for y in (-11.4,-10.0):C.box('stroller shelter post',(4.55,y,1.77),(.10,.10,3.46),'timber','structure')
    for i in range(13):C.box('stroller side screen',(4.55,-11.4+i*.115,1.75),(.055,.05,3.38),'timber','site')
    for i in range(5):C.box('stroller front screen',(4.05+i*.115,-11.4,1.75),(.05,.055,3.38),'timber','site')
    for x in (2.85,3.65):
        y=-10.75
        for dx in (-.27,.27):
            for dy in (-.32,.32):C.rod('stroller wheel',(x+dx-.035,y+dy,.24),(x+dx+.035,y+dy,.24),.13,'hardware','site',12)
        for dx in (-.27,.27):
            C.beam('stroller chassis',(x+dx,y-.32,.24),(x+dx,y+.36,.82),.035,role='hardware',module='site')
            C.beam('stroller handle',(x+dx,y-.32,.24),(x+dx,y-.46,1.1),.035,role='hardware',module='site')
        C.beam('stroller pushbar',(x-.27,y-.46,1.1),(x+.27,y-.46,1.1),.035,role='hardware',module='site')
        C.box('stroller fabric seat',(x,y,.60),(.48,.46,.07),'furniture','site')
        C.solid_surface('stroller reclined back',[(x-.24,y-.18,.60),(x+.24,y-.18,.60),(x+.24,y-.36,.96),(x-.24,y-.36,.96)],.025,'furniture','site')
        C.solid_surface('stroller hood',[(x-.28,y-.40,1.01),(x+.28,y-.40,1.01),(x+.28,y+.08,1.11),(x-.28,y+.08,1.11)],.025,'furniture','site')
    # Side garden enclosing fence, gated frontage, low planting and supported play.
    for a,b in [((13,-8,.04),(14,-8,.04)),((15.5,-8,.04),(20,-8,.04)),
                ((20,-8,.04),(20,11,.04)),((20,11,.04),(13,11,.04)),((13,11,.04),(13,10,.04))]:
        C.railing('secure play fence',a,b,height=1.35,spacing=.12,role='timber')
        OBSTACLES.append([min(a[0],b[0])-.045,max(a[0],b[0])+.045,min(a[1],b[1])-.045,max(a[1],b[1])+.045,0,1.4])
    C.railing('open play gate',(15.5,-8,.04),(15.5,-6.5,.04),height=1.35,spacing=.12,role='timber')
    for a,b in [((-3,9.9,.04),(-3,10.8,.04)),((-3,10.8,.04),(-.7,10.8,.04)),
                ((.7,10.8,.04),(3,10.8,.04)),((3,10.8,.04),(3,9.9,.04))]:
        C.railing('rear learning garden fence',a,b,height=1.35,spacing=.12,role='timber')
    C.railing('rear garden gate',(-.7,10.8,.04),(.7,10.8,.04),height=1.35,spacing=.12,role='timber')
    C.box('play garden sand',(16.5,7,.075),(4,4,.07),'sand','site',0)
    for x in (14.45,18.55):C.box('sand box timber edge',(x,7,.13),(.1,4.2,.18),'timber','site')
    for y in (4.95,9.05):C.box('sand box timber edge',(16.5,y,.13),(4.2,.1,.18),'timber','site')
    for x in (15.1,16.3):
        for y in (6.2,7.4):C.rod('low climber post',(x,y,.11),(x,y,1.65),.065,'timber','site')
    C.box('low climbing deck',(15.7,6.8,.78),(1.32,1.32,.10),'timber','site')
    for x in (15.1,16.3):C.railing('climber side guard',(x,6.2,.83),(x,7.4,.83),height=.78,spacing=.13,role='timber')
    for i in range(3):C.box('low climbing steps',(15.7,5.5+i*.26,.11+(i+1)*.22/2),(.78,.27,(i+1)*.22),'timber','site')
    C.solid_surface('low slide bed',[(15.3,7.4,.84),(16.1,7.4,.84),(16.1,8.75,.18),(15.3,8.75,.18)],.06,'trim','site')
    for x in (15.3,16.1):C.beam('slide edge',(x,7.4,.93),(x,8.75,.27),.07,.14,'trim','site')
    for x in (15,18):
        for y in (-.5,2):C.rod('shade pergola post',(x,y,.04),(x,y,2.8),.065,'timber','site')
    for x in (15,18):C.beam('pergola beam',(x,-.65,2.8),(x,2.15,2.8),.14,role='timber',module='site')
    for i in range(8):C.beam('pergola shade slat',(14.8,-.55+i*.37,2.91),(18.2,-.55+i*.37,2.91),.11,role='timber',module='site')
    B.bench(16.5,1.5)
    for x in (-8,8):R.plantbed(x,-11.7,7,1.4)
    for x in (-2,2):R.plantbed(x,5,1.3,5)
    for x,y in [(-14,7),(18,10),(16,-5)]:R.tree(x,y,int(x*3+y))
    for x in (-1.8,1.8):B.bench(x,8.5)


def walking():
    triangles=[]
    def rect(x0,y0,x1,y1,z):
        a=[x0,y0,z];b=[x1,y0,z];c=[x1,y1,z];d=[x0,y1,z]
        triangles.extend([[a,b,c],[a,c,d]])
    for cx in (-8,8):rect(cx-4.85,-9.9,cx+4.85,9.85,FLOOR)
    rect(-3.4,-8.1,3.4,-2.9,FLOOR)
    rect(-2.55,-14.4,2.55,-8,FLOOR);rect(-1.15,-3.1,1.15,10,FLOOR)
    rect(12.6,-4.45,19,-2.55,FLOOR)
    # The surrounding site is physically level at .04. Routes stay on real paths.
    rect(13.4,-7.9,19.9,10.9,.04)
    for o in C.objects():
        module=o.get('cityprompt_lego_module','')
        role=o.get('cityprompt_semantic_role','')
        solid_site=(module in ('site','structure') or 'gate' in o.name or 'fence' in o.name or (module=='landscape' and role=='timber'))
        if role in ('paving','sand','soil','leaf','plant','flower','roof'):solid_site=False
        if module not in ('furniture','interior') and 'open leaf' not in o.name and not solid_site:continue
        if any(k in o.name for k in ('lamp','ceiling','diffuser')):continue
        lo,hi=C.bounds([o])
        if hi[2]-lo[2]>.015:OBSTACLES.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    routes=[]
    def route(name,xy):routes.append(dict(name=name,points=[[x,y,FLOOR] for x,y in xy]))
    route('Approach to supervised lobby',[(0,-14),(0,-6)])
    route('Left classroom',[(0,-6),(0,-5.5),(-4.5,-5.5),(-4.5,-3),(-6,-3)])
    route('Right classroom',[(0,-6),(0,-5.5),(4.5,-5.5),(4.5,-3),(6,-3)])
    route('Left classroom to nap room',[(-4.6,-3),(-4.6,3.4),(-6.5,3.4),(-6.7,5)])
    route('Right classroom to child washroom',[(4.6,-3),(4.6,2.9),(6.7,2.9),(9,2.9)])
    route('Staff kitchen',[(4.6,-3),(4.6,7.5),(6.7,7.5),(7.3,6.5)])
    route('Lobby to rear learning garden',[(0,-6),(0,9.5)])
    route('Right classroom to secured play garden',[(4.6,-4.3),(11.2,-4.3),(11.2,-3.5),(18.8,-3.5)])
    return dict(version=2,footprint=[38,30],entrance=[0,-14,FLOOR],maxStepM=.18,
                triangles=triangles,obstacles=OBSTACLES,portals=[[-2.5,2.5,-15,-13.5]],routes=routes,
                gardenExclusionProbes=[dict(name='pergola post',point=[15,-.5,.04]),
                    dict(name='climbing platform',point=[15.7,6.8,.04]),
                    dict(name='garden bench',point=[16.5,1.5,.04]),
                    dict(name='open gate leaf',point=[15.5,-7.2,.04])])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--version',default='v001');parser.add_argument('--resolution',type=int,default=1280)
    parser.add_argument('--dry-run',action='store_true');a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root=a.output_root.resolve();candidate='childcare-garden-'+a.version;out=root/candidate
    spec=json.loads((HERE/'pilot-prework.json').read_text(encoding='utf-8'))
    for s in spec['sources']:
        p=Path(s['path']);assert p.stat().st_size==s['bytes'] and C.digest(p)==s['sha256']
    camspec=cameras()
    if a.dry_run:
        print(json.dumps(dict(candidate=candidate,sources=3,cameras=len(camspec),geometry_written=False)));return
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','textures','renders','review','evidence','boards'):(out/name).mkdir()
    locked_sources=[]
    for s in spec['sources']:
        shutil.copy2(s['path'],out/'sources'/Path(s['path']).name)
        locked_sources.append(dict(s,original_path=s['path'],path='sources/'+Path(s['path']).name))
    for f in (Path(__file__),HERE/'pilot-prework.json',Path(C.__file__),Path(B.__file__),Path(R.__file__),Path(W.__file__)):
        shutil.copy2(f,out/'scripts'/f.name)
    texture=root/'materials/childcare-buff-brick.png';shutil.copy2(texture,out/'textures'/texture.name)
    shutil.copy2(root/'materials/childcare-material-provenance.json',out/'textures/material-provenance.json')
    manifest=dict(spec,candidate=candidate,state='building',camera_roster=camspec,
                  mandatory_review_views=[s['name'] for s in camspec],
                  source_contract=dict(sources=locked_sources,front_is_primary=True),
                  provenance=dict(scripts=[dict(path='scripts/'+p.name,sha256=C.digest(p)) for p in (out/'scripts').iterdir()],blender_version=bpy.app.version_string),
                  measurement_contract=dict(dimensions_m=dict(width=26,depth=20,height=7.2),
                    brick_tile_m=[1.25,2.2],brick_scale_note='Generated tile shows about5.25 bricks across and28 courses; mapping uses observed cadence, not requested2.4m square.'),
                  material_scope='Source-conditioned masonry albedo; remaining semantic physical materials, no full keeper PBR claim.')
    B.write(out/'prework-manifest.json',manifest)
    cams=C.setup(PALETTE,camspec,a.resolution);bpy.context.scene.cycles.samples=24
    bs=C.MATS['glass'].node_tree.nodes['Principled BSDF'];bs.inputs['Alpha'].default_value=1
    bs.inputs['Transmission Weight'].default_value=1;bs.inputs['Roughness'].default_value=.06;bs.inputs['IOR'].default_value=1.45
    bs=C.MATS['lamp'].node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.85,.62,1);bs.inputs['Emission Strength'].default_value=2
    mat=C.MATS['wall'];mat['texture_free']=False;mat['source_conditioned']=True
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(texture));node.image.pack()
    mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    build();bpy.context.view_layer.update();network=walking();B.write(out/'evidence/walking-network.json',network)
    B.uv_all()
    for o in C.objects():
        if o.get('cityprompt_semantic_role')=='wall':
            for uv in o.data.uv_layers.active.data:uv.uv.x*=2.4/1.25;uv.uv.y*=2.4/2.2
        o['archetype_id']=spec['archetype_id'];o['variant_id']=spec['variant_id']
    original=C.bounds(C.objects());assert abs(original[0][2])<.001,original
    aperture=C.aperture_audit();B.write(out/'evidence/carrier-aperture-audit.json',aperture)
    for s in camspec:
        if s['whole']:C.fit(cams[s['name']],s['target'])
    bpy.context.scene.camera=cams['front_corner'];bpy.ops.wm.save_as_mainfile(filepath=str(out/(candidate+'.blend')))
    for role in C.MATS:
        group=[o for o in C.objects() if o.get('cityprompt_semantic_role')==role]
        if not group:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        bpy.context.object.name=role
    W.embed(network);glb=out/(candidate+'.glb');bpy.ops.object.select_all(action='DESELECT')
    for o in C.objects():o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
    payload=C.glb_json(glb)
    for o in list(C.objects()):bpy.data.objects.remove(o,do_unlink=True)
    old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=[o for o in bpy.context.scene.objects if o not in old and o.type=='MESH']
    for o in imported:o['rlasm_building_object']=True
    bpy.context.view_layer.update();actual=C.bounds(imported)
    delta=max(abs(actual[i][j]-original[i][j]) for i in range(2) for j in range(3));assert delta<.001
    for s in camspec:
        bpy.context.scene.camera=cams[s['name']]
        bpy.context.scene.render.filepath=str(out/'renders'/(s['name']+'.png'))
        bpy.ops.render.render(write_still=True);print('RENDER_COMPLETE '+s['name'],flush=True)
    report=dict(candidate=candidate,status='build_valid',keeper_claimed=False,runtime_activated=False,generic_fallback_count=0,
        generic_fallback_scope='No substitute library building or material assets. Palette-only prototype finishes remain declared keeper limitations.',
        glb=dict(path=glb.name,bytes=glb.stat().st_size,sha256=C.digest(glb),meshes=len(payload['meshes']),textures=len(payload.get('textures',[])),**C.metrics(imported)),
        native_bounds_m=actual,max_roundtrip_delta_m=delta,carrier_aperture_audit=aperture['status'],
        opening_count=len(C.OPENINGS),render_source='exact exported GLB reimport, no substitutions',independent_review='pending')
    B.write(out/'build-report.json',report);B.write(out/'evidence/builder-evidence.json',report)
    print('BUILD_COMPLETE '+json.dumps(report),flush=True)


if __name__=='__main__':main()
