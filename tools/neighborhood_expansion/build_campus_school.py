"""Shared campus: two classroom wings, a double-height commons and rear gym."""
from pathlib import Path
import sys
import math
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy
import build_corner_fourplex as P
import build_library_pavilion as L

Z=.14
RISE=3.8
PALETTE=dict(B.PALETTE,wall=(.69,.61,.47),trim=(.28,.33,.34),roof=(.42,.46,.48),
 panel=(.25,.32,.38),timber=(.58,.38,.19),interior=(.83,.82,.76),floor=(.57,.53,.43),
 furniture=(.26,.39,.43),ceiling=(.85,.85,.79),lamp=(.98,.90,.75),leaf=(.23,.33,.13),
 flower=(.66,.61,.35),grass=(.29,.39,.18),mirror=(.82,.84,.85))
ROOMS=[(-31.7,-23),(-23,-11.3),(-11.3,-5),(5,17.9),(17.9,23.7)]

def wall(face,a,b,z0,z1,holes=(),role='wall',depth=.30):
    P.wall(face,a,b,z0,z1,holes,role,depth,glazed=role=='wall',flat_door=role=='interior')

def partition(y,a,b,z,door=None):
    holes=[] if door is None else [P.h('room door '+str((a,y,z)),door,z,1.25,2.35,True)]
    if y==-9:
        # Classroom leaves swing inward, clear of teaching boards and corridor.
        P.wall(C.Face((0,y,0),(1,0,0),(0,-1,0),'classroom rear'),a,b,z,z+3.60,holes,'interior',.14)
    else:wall(C.Face((0,y,0),(1,0,0),(0,1,0),'room front'),a,b,z,z+3.60,holes,'interior',.14)

def lamp(x,y,z,ceiling=3.58):
    R.lamp(x,y,z+ceiling-.035,.85)
    C.qa_room_light('school',(x,y,z+ceiling-.23),330,2.8)

def classroom(a,b,z,index):
    # The clear door aisle is kept beside the east wall of each classroom.
    def desk(x,y):
        before=set(C.objects());B.desk(x,y,z)
        for obj in set(C.objects())-before:
            obj.location.x=2*x-obj.location.x;obj.location.y=2*y-obj.location.y;obj.rotation_euler.z+=math.pi
    columns=[a+1.2,a+2.8]+([a+4.4] if b-a>6.1 else [])
    for x in columns:
        for y in (-17.9,-15.9,-13.9):desk(x,y)
    desk(a+2,-19.7)
    board_width=min(3.3,b-a-3.4)
    # The reversed rear carrier ends at y=-9.14 on the classroom side.
    C.box('teaching whiteboard',(a+2.5,-9.1655,z+1.75),(board_width,.055,1.15),'ceiling','furniture')
    C.box('whiteboard tray',(a+2.5,-9.20,z+1.16),(board_width,.13,.035),'trim','furniture')
    for j in range(5):
        x=a+.5+j*.68
        C.box('classroom low cubby',(x,-9.48,z+.48),(.60,.55,.96),'timber','furniture')
        C.box('cubby open recess',(x,-9.775,z+.54),(.48,.035,.65),'panel','decor')
    for y in (-17.4,-12):lamp((a+b)/2,y,z)

def stair():
    x=0;y=-7.5;z=Z;w=1.25
    R.stair(x,y,z,RISE,w)
    for obj in list(C.objects()):
        if obj.name.startswith(('outer stair rail','outer guard post','half landing rear guard')):bpy.data.objects.remove(obj,do_unlink=True)
    C.railing('half landing rear guard',(-1.3125,y+3.65,z+RISE/2),(1.3125,y+3.65,z+RISE/2),spacing=.10,bottom=0)
    for side in (-1,1):
        pts=[]
        for j in range(11):
            zz=z+(j+1)*RISE/22 if side<0 else z+RISE-j*RISE/22
            pts.append((side*.0625,y-.125+j*.25,zz))
        pts.append((side*.0625,y+2.625,pts[-1][2]))
        for p in pts:C.rod('inner stair guard post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
        for a,b in zip(pts,pts[1:]):
            C.beam('inner stair guard rail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.04,.04,'trim','stair guard')
        outer=[(side*1.27,p[1]+.02,p[2]) for p in pts[:-1]]
        for p in outer:C.rod('seated outer stair post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
        for a,b in zip(outer,outer[1:]):C.beam('outer stair guard rail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.04,.04,'trim','stair guard')
        # Landing pickets bear on its slab; the short rail transition joins
        # the last flight post without duplicating it or blocking the turn.
        foot=(side*1.27,-4.855,Z+RISE/2)
        end=(side*1.27,-3.85,Z+RISE/2)
        C.rod('landing side start post',foot,(foot[0],foot[1],foot[2]+1.02),.018,'trim','stair guard')
        C.railing('landing side guard',foot,end,spacing=.10,bottom=0,end_posts=False)
        last=outer[-1]
        C.beam('landing flight rail connection',(last[0],last[1],last[2]+1.02),(foot[0],foot[1],foot[2]+1.02),.042,.038,'trim','stair guard')
        C.beam('landing rear rail connection',(end[0],end[1],end[2]+1.02),(side*1.3125,end[1],end[2]+1.02),.042,.038,'trim','stair guard')
    for x in (-1.50,1.50):C.railing('upper stair edge',(x,-7.63,Z+RISE),(x,-3.70,Z+RISE),bottom=0)
    C.railing('upper rear stair edge',(-1.5,-3.70,Z+RISE),(1.5,-3.70,Z+RISE),bottom=0)
    C.railing('upper lower-flight lip',(-1.5,-7.64,Z+RISE),(0,-7.64,Z+RISE),bottom=0)
    C.railing('commons gallery front',(-5,-9,Z+RISE),(5,-9,Z+RISE),bottom=0)

def roof(a,b,c,d,z,role='wall'):
    B.parapet(a,b,c,d,z,role)
    # Roof joints have finite height and never share a coplanar carrier face.
    for y in range(int(c)+2,int(d)-1,3):C.box('membrane joint',((a+b)/2,y,z-.367),(b-a-.8,.018,.008),'roof','roof',0)
    for x in (a+.34,b-.34):C.box('parapet base flashing',(x,(c+d)/2,z-.25),(.08,d-c-.7,.25),'roof','roof',0)

def build():
    mirror=C.MATS['mirror'].node_tree.nodes['Principled BSDF']
    mirror.inputs['Metallic'].default_value=1;mirror.inputs['Roughness'].default_value=.055
    C.box('site soil base',(0,1,.0125),(80,76,.025),'soil','site',0)
    C.box('rear shared playing field',(-4,31,.0325),(70,14,.015),'grass','landscape',0)
    C.box('rear school lawn',(-9,10.5,.0325),(46,27,.015),'grass','landscape',0)
    for x in (-37,37):C.box('side landscape',(x,0,.0325),(6,61,.015),'grass','landscape',0)
    C.box('public sidewalk',(0,-34,.02),(80,3,.04),'paving','site',0)
    C.box('school forecourt',(-2,-26.25,.07),(68,9.5,.14),'paving','site',0)
    for x,w in [(-19.5,33),(17.5,29)]:C.box('forecourt ramp side',(x,-31.75,.07),(w,1.5,.14),'paving','site',0)
    C.box('right pedestrian connection',(28,-14,.07),(8,16,.14),'paving','site',0)
    C.box('right service drive',(35,2,.035),(5,68,.03),'roof','site',0)
    C.prism('solid public entry ramp',[(-32.5,0),(-32.5,.04),(-31,.14),(-31,0)],'x',-3,3,'paving','site')
    C.box('school entrance threshold slab',(0,-21.2,Z-.07),(3,1.5,.14),'paving','floors',0)
    C.box('school gym threshold slab',(20,-3,Z-.07),(2.1,.85,.14),'floor','floors',0)
    C.box('vestibule gym threshold slab',(28,-3,Z-.07),(2.1,.85,.14),'floor','floors',0)
    # Two-storey bar: front classrooms, rear corridor and services.
    for level in range(2):
        z=Z+level*RISE
        slab=C.box('classroom occupied slab',(-4,-12,z-.07),(55.4,17.4,.14),'floor','floors',0)
        if level:
            C.cut_box(slab,'double-height commons void',(0,-15,z),(10,12,.7))
            C.cut_box(slab,'stair opening',(0,-5.665,z),(3.0,3.93,.7))
        ceiling=C.box('classroom ceiling',(-4,-12,z+3.63),(55.4,17.4,.10),'ceiling','ceiling',0)
        C.cut_box(ceiling,'commons open height',(0,-12,z+3.63),(10,18,.6))
        front=C.Face((0,-21,0),(1,0,0),(0,1,0),'school front '+str(level))
        left=[(-28,5.6),(-22,1.2),(-15,5.6),(-7.7,2.7)]
        right=[(7.5,2.7),(12.4,2.7),(15.4,2.7),(21,3.2)]
        for a,b,bays in [(-32,-5,left),(5,24,right)]:
            holes=[P.h('front classroom '+str((level,j,a)),x,z+.75,w,2.12) for j,(x,w) in enumerate(bays)]
            wall(front,a,b,z if level else 0,z+RISE,holes)
            # Source bands bridge the inter-storey zone; upper headers stay brick.
            if level==0:
                bands=bays if a<0 else [(7.5,2.7),(16.825,11.55)]
                for x,w in bands:front.part('fibre cement spandrel',x,-.018,3.84,w,.035,1.65,'panel','envelope',0)
            if a>0:front.part('grouped-bay fibre cement panel',18.075,-.018,z+1.81,2.65,.035,2.12,'panel','envelope',0)
        for side in (-32,24):
            face=C.Face((side,0,0),(0,1,0),(1 if side<0 else -1,0,0),'classroom flank')
            wall(face,-21,-3,z if level else 0,z+RISE,[P.h('flank window '+str((side,level,y)),y,z+.85,2.1,2.0) for y in (-18,-13.5,-4.8)])
        rear=C.Face((0,-3,0),(1,0,0),(0,-1,0),'classroom rear')
        hs=[P.h('rear light '+str((level,x)),x,z+1.15,2,1.6) for x in (-28,-19.5,-10.5,8,12)]
        hs += [P.h('school gym connection',20,z,1.8,2.5,True)] if level==0 else [P.h('upper rear light',20,z+1.15,2.0,1.6)]
        # The gym meets the rear-right classroom wall. Upper connection is opaque.
        wall(rear,-32,24,z if level else 0,z+RISE,hs)
        for i,(a,b) in enumerate(ROOMS):
            partition(-9,a,b,z,b-1.15)
            for x in ((a,b) if i in (2,4) else (a,)):
                if x not in (-31.7,23.7):wall(C.Face((x,0,0),(0,1,0),(1,0,0),'classroom divider'),-20.7,-9,z,z+3.60,role='interior',depth=.14)
            classroom(a,b,z,i)
        # Rear support rooms; wide corridor remains between y=-9 and y=-6.
        for a,b in [(-31.7,-24),(-22,-17),(-15,-7)]:
            partition(-6,a,b,z,a+1.1)
            for x in (a,b):
                if x!=-31.7:wall(C.Face((x,0,0),(0,1,0),(1,0,0),'support room side'),-6,-3.3,z,z+3.6,role='interior',depth=.13)
            lamp((a+b)/2,-4.7,z)
        B.desk(-28,-4.5,z,False);B.desk(-25.6,-4.5,z,False)
        L.Z=z;L.basin(-20.9,-3.85);L.toilet(-18.15,-3.95)
        C.box('washroom mirror',(-21.1,-3.315,z+1.7),(.9,.03,.65),'mirror','furniture')
        for x in (-13.2,-10.4):
            C.box('resource storage cabinet',(x,-3.65,z+.48),(2.0,.60,.96),'timber','furniture')
        for x in (-28,-19,-10,9,18):lamp(x,-7.5,z)
    # Front commons is full height; the upper gallery is connected to both wings.
    face=C.Face((0,-21,0),(1,0,0),(0,1,0),'glazed commons front')
    hs=[P.h('main entrance',0,Z,2.2,2.55,True),P.h('commons transom',0,2.89,2.2,4.91),P.h('commons left screen',-3.0,Z,3.4,7.66),P.h('commons right screen',3.0,Z,3.4,7.66)]
    wall(face,-5,5,0,8.3,hs)
    for x in (-3.0,0,3.0):face.part('commons horizontal mullion',x,.16,4.02,3.35 if x else 2.2,.07,.07,'trim')
    for x in (-5,5):
        wall(C.Face((x,0,0),(0,1,0),(1 if x<0 else -1,0,0),'commons raised cheek'),-21,-3,7.74,8.65,role='panel')
    C.box('commons high ceiling',(0,-12,8.16),(9.4,17.4,.13),'ceiling','ceiling')
    # Roof over the rear commons does not leave a clerestory opening to outdoors.
    wall(C.Face((0,-3,0),(1,0,0),(0,-1,0),'commons upper rear'),-5,5,7.74,8.65)
    stair()
    C.box('reception counter',(-3.2,-14.8,Z+.50),(2.8,.85,1.0),'timber','furniture')
    C.box('reception countertop',(-3.2,-14.8,Z+1.03),(2.9,.94,.07),'stone','furniture')
    B.sofa(3,-17,Z);B.sofa(-3,-18.2,Z)
    for x in (-4.65,4.65):
        C.box('timber portico foot',(x,-22.2,.18),(.58,.58,.36),'stone','structure')
        C.box('timber portico column',(x,-22.2,4.25),(.24,.24,8.15),'timber','structure')
    for y in (-22.2,-20.9):C.box('portico cross beam',(0,y,8.20),(10.3,.28,.4),'timber','structure')
    C.box('portico timber soffit',(0,-21.8,8.40),(10.6,2.8,.12),'timber','roof')
    C.box('portico metal cap',(0,-21.8,8.49),(10.7,2.9,.06),'roof','roof')
    C.box('entrance rain canopy',(0,-21.75,2.85),(3.0,1.5,.10),'roof','structure')
    for x in (-1.25,1.25):
        C.box('canopy anchor plate',(x,-21.025,3.6),(.10,.06,.20),'hardware','structure')
        C.rod('canopy hanger',(x,-22.35,2.9),(x,-21.035,3.6),.02,'hardware','structure')
    for y in (-18,-12,-6):lamp(0,y,Z,7.955)
    # Gym and community vestibule, independent after-hours entrance.
    C.box('gym slab',(23,9,Z-.07),(17.4,23.4,.14),'sport','floors',0)
    C.box('gym ceiling',(23,9,9.72),(17.4,23.4,.16),'ceiling','ceiling')
    for side in (14,32):
        f=C.Face((side,0,0),(0,1,0),(1 if side==14 else -1,0,0),'gym side')
        wall(f,-3,21,0,6.0,[P.h('gym side daylight '+str((side,y)),y,3.8,3.0,1.6) for y in (2,8,14,18)])
        wall(f,-3,21,6.0,10.3,role='panel')
    rear=C.Face((0,21,0),(1,0,0),(0,-1,0),'gym rear')
    wall(rear,14,32,0,6,[P.h('gym field exit',28,Z,1.8,2.5,True)])
    wall(rear,14,32,6,10.3,role='panel')
    gf=C.Face((0,-3,0),(1,0,0),(0,1,0),'gym front')
    # Main bar already owns x14..24; only exposed annex connector receives wall.
    wall(gf,24,32,0,6,[P.h('gym vestibule door',28,Z,1.8,2.5,True)])
    wall(gf,14,32,7.74,10.3,role='panel')
    wall(gf,24,32,6,7.74,role='panel')
    C.box('community vestibule slab',(28,-5,Z-.07),(8,4,.14),'floor','floors',0)
    wall(C.Face((0,-7,0),(1,0,0),(0,1,0),'community entrance front'),24,32,0,4.0,[P.h('community entrance',28,Z,1.8,2.5,True),P.h('community sidelight',25.3,Z+.55,1.3,2.4)])
    wall(C.Face((32,0,0),(0,1,0),(-1,0,0),'vestibule end'),-7,-3,0,4.0,[P.h('community side light',-5,Z+.8,2,2)])
    C.box('vestibule ceiling',(28,-5,3.70),(7.4,3.4,.1),'ceiling','ceiling')
    for y in (0,18):
        direction=1 if y==0 else -1
        C.box('gym wall padding',(23,-2.62 if y==0 else 20.62,Z+1.0),(3.2,.20,2.0),'furniture','furniture')
        # Backboard and ring supported by a real cantilever from the side wall.
        C.box('basketball backboard',(23,y+direction*.24,3.5),(1.8,.09,1.05),'ceiling','sport')
        anchor=-2.7 if y==0 else 20.7
        C.beam('basketball support',(23,anchor,4.0),(23,y+direction*.24,3.6),.10,.10,'hardware','structure')
        C.rod('basket ring bracket',(23,y+direction*.24,3.05),(23,y+direction*.43,3.05),.028,'hardware','sport')
        for i in range(24):
            a=i*math.tau/24;b=(i+1)*math.tau/24
            C.rod('basket ring',(23+.23*math.cos(a),y+direction*.65+.23*math.sin(a),3.05),(23+.23*math.cos(b),y+direction*.65+.23*math.sin(b),3.05),.018,'hardware','sport',6)
    for x in (16,30):C.box('court sideline',(x,9,Z+.003),(.045,18,.006),'ceiling','sport',0)
    for y in (0,9,18):C.box('court cross line',(23,y,Z+.003),(14,.045,.006),'ceiling','sport',0)
    for y in (4,9,14):
        B.bench(15.2,y)
        for x in (19,27):lamp(x,y,Z,9.50)
    lamp(28,-5,Z,3.51)
    roof(-32,-5,-21,-3,8.15);roof(5,24,-21,-3,8.15);roof(-5,5,-21,-3,8.75)
    roof(14,32,-3,21,10.35,'panel');roof(24,32,-7,-3,4.2)
    for i in range(5):
        for j in range(3):
            x=-20+i*1.2;y=-14+j*2
            C.box('solar ballast',(x,y,7.87),(.9,1.5,.18),'stone','roof_equipment')
            C.box('bounded solar module',(x,y,7.995),(1.12,1.85,.07),'panel','roof_equipment')
            for xx in (-.53,.53):C.box('solar frame',(x+xx,y,8.0475),(.025,1.87,.035),'trim','roof_equipment')
    R.roof_unit(24,12,9.985,2.7,2)
    # Covered bicycles, benches and planted forecourt islands.
    for x in (-23,-13):
        for y in (-30,-26):C.box('bike shelter column',(x,y,1.52),(.12,.12,2.9),'trim','structure')
    C.box('bike shelter cap',(-18,-28,3.03),(10.7,4.7,.16),'roof','structure')
    for x in (-21,-19,-17,-15):B.bikehoop(x,-28)
    for x in (7,13):B.bench(x,-28.5)
    for x,y,w,d in [(-28,-23,5,1),(-18,-23,5,1),(-9,-23,4,1),(10,-23,6,1),(20,-23,5,1),(18,-30,8,2),(-29,-29,5,3)]:R.plantbed(x,y,w,d)
    for x,y,seed in [(-36,-27,801),(-36,20,802),(37,23,803),(28,-30,804)]:R.tree(x,y,seed)
    C.box('gym rear landing',(28,22.1,.07),(3.0,2.8,.14),'paving','site',0)
    L.Z=Z
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    tris=[];routes=[];obs=P.OBS
    def rect(a,b,c,d,z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    def route(name,xy,z=Z):routes.append(dict(name=name,points=[[x,y,z] for x,y in xy]))
    for level in range(2):
        z=Z+level*RISE
        rect(-31.68,-20.68,-5,-3.32,z);rect(5,-20.68,23.68,-3.32,z)
        if level==0:rect(-5,-20.68,5,-7.625,z)
        else:rect(-5,-9,5,-7.625,z)
        rect(-5,-7.625,-1.5,-3.32,z);rect(1.5,-7.625,5,-3.32,z);rect(-1.5,-3.70,1.5,-3.32,z)
        for i,(a,b) in enumerate(ROOMS):route('Classroom '+str(i+1)+' floor '+str(level+1),[(2 if a>0 else -2,-7.95),(b-1.15,-7.95),(b-1.15,-11.2),(b-1.15,-18.8)],z)
        for a,label in [(-31.7,'Staff room'),(-22,'Washroom'),(-15,'Resources')]:route(label+' floor '+str(level+1),[(-2,-7.95),(a+1.1,-7.95),(a+1.1,-4.9)],z)
    for j in range(11):
        rect(-1.3125,-7.625+j*.25,-.0625,-7.375+j*.25,Z+(j+1)*RISE/22)
        rect(.0625,-7.625+j*.25,1.3125,-7.375+j*.25,Z+RISE-j*RISE/22)
    rect(-1.3125,-4.875,1.3125,-3.825,Z+RISE/2)
    pts=[[-.6875,-8.0,Z],[-.6875,-4.3,Z+RISE/2],[.6875,-4.3,Z+RISE/2],[.6875,-8.0,Z+RISE]]
    routes += [dict(name='Commons stair ascent',points=pts),dict(name='Commons stair descent',points=list(reversed(pts)))]
    rect(-36,-31,32,-21,Z);rect(-3,-32.8,3,-32.5,.04)
    a=[-3,-32.5,.04];b=[3,-32.5,.04];c=[3,-31,Z];d=[-3,-31,Z];tris.extend([[a,b,c],[a,c,d]])
    rect(-2,-22,2,-20,Z);rect(24,-22,32,-3,Z);rect(14.32,-3,31.68,20.68,Z)
    rect(27,20,29,23.3,Z);rect(19,-4,21,-2,Z)
    routes.append(dict(name='Public school entrance',points=[[0,-32.7,.04],[0,-32.5,.04],[0,-31,Z],[0,-23,Z],[0,-19,Z],[0,-8.0,Z]]))
    route('Reception',[(0,-16),(0,-14.8),(-1.4,-14.8)])
    route('School to gym',[(2,-7.95),(20,-7.95),(20,-1),(23,3)])
    route('Community gym entrance',[(0,-25),(28,-25),(28,-5),(28,3),(23,3)])
    route('Gym rear exit',[(23,3),(28,3),(28,22)])
    route('Covered bicycle approach',[(0,-25),(-18,-25),(-18,-27)])
    route('Forecourt bench',[(0,-25),(7,-25),(7,-27.7)])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'guard' in mod or 'gallery' in mod or 'stair edge' in mod or 'flight lip' in mod or 'open leaf' in o.name or o.name.startswith(('bike rack','young tree trunk','branch'))
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in o.name for s in ('ceiling','luminaire','diffuser','hanger','support','beam','cap')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    probes=[dict(name='bench',point=[7,-28.5,Z]),dict(name='forecourt tree trunk',point=[28,-30,Z])]+[dict(name='bicycle '+str(x),point=[x,-28,Z]) for x in (-21,-19,-17)]
    landing_probes=[dict(name='half landing '+('left' if side<0 else 'right')+' side guard',point=[side*1.30,-4.3,Z+RISE/2]) for side in (-1,1)]
    return dict(version=2,footprint=[80,76],entrance=[0,-32.7,.04],maxStepM=.18,triangles=tris,obstacles=obs,portals=[[-3,3,-33,-32]],routes=routes,gardenExclusionProbes=probes,circulationExclusionProbes=landing_probes)

def cameras():
    cams=[]
    for n,loc in [('front',(-4,-95,13)),('front_corner',(69,-79,37)),('aerial',(55,-63,86)),('left_side',(-92,-2,25)),('right_side',(93,0,27)),('rear',(0,89,27)),('rear_side',(-68,70,45))]:cams.append(dict(name=n,location=loc,target=(0,-1,4),whole=True,lens=52))
    def add(n,loc,target,lens=26):cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    add('facade_close',(25,-38,8),(13,-21,4),36);add('architecture_close',(12,-32,8),(0,-21,4.4),28)
    add('glass_close',(-16,-26,2),(-16,-17,1.5),30);add('roof_contact',(28,-12,16),(23,-3,8),36)
    add('solar_contact',(-24,-16,12),(-18,-12,8),35);add('commons',(3.8,-19.8,2.0),(0,-8,3.2),22)
    add('entry_closure',(3.6,-17,2.1),(0,-21,3.6),22);add('commons_stair',(-3.2,-9,2.2),(0,-5.6,2.6),20)
    add('upper_landing',(3.2,-8.2,5.7),(0,-5.3,4.0),20);add('gallery',(3.2,-5,5.7),(-2,-14,3),20)
    add('landing_left_contact',(-3.6,-5.1,3.25),(-1.27,-4.3,2.55),28)
    add('landing_right_contact',(3.6,-5.1,3.25),(1.27,-4.3,2.55),28)
    for level in range(2):
        z=Z+level*RISE
        for i,(a,b) in enumerate(ROOMS):add(('classroom_left' if i==0 and level==0 else 'classroom_'+str(i)+'_'+str(level)),(b-.65,-10.0,z+1.7),((a+b)/2,-16.4,z+1.2),20)
        add('washroom_'+str(level),(-21.3,-5.55,z+1.65),(-19.5,-3.8,z+.8),20)
        add('staff_'+str(level),(-30.2,-5.5,z+1.7),(-26.5,-4.3,z+1),22)
        add('resources_'+str(level),(-14.3,-5.4,z+1.65),(-10.9,-3.8,z+.9),24)
    add('washroom_fixture',(-19.2,-5.25,1.65),(-20.9,-3.85,1),25)
    add('classroom_narrow_board',(22.6,-12.5,1.9),(20.9,-9.3,1.5),22)
    add('classroom_wide_board',(-29,-18.6,1.8),(-27,-9.3,1.5),24)
    add('gym',(29,-.8,2.0),(22,12,3.1),22);add('gym_rear',(29,19,2.1),(22,5,2.8),22)
    add('community_entrance',(34,-13,5),(28,-5,1.8),28);add('vestibule',(30.7,-6.4,1.8),(27.8,-3,1.5),20)
    add('forecourt',(-30,-35,9),(-11,-26,1.6),30);add('public_approach',(5,-34,1.1),(0,-31,.14),30)
    return cams

if __name__=='__main__':D.run(__file__,'school-campus-prework.json','school-campus',PALETTE,cameras,build,network,'school-campus-buff-brick.png',[1.20,2.70],extra_scripts=[P.__file__,L.__file__])
