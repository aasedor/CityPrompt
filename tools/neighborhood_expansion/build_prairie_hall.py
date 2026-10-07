"""Prairie community hall: broad gathering gable and attached lower hip wing."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy
import build_corner_fourplex as P
import build_library_pavilion as L  # Individual hollow basin/toilet fixtures only.

Z=.14
PALETTE=dict(B.PALETTE,wall=(.66,.54,.36),trim=(.085,.10,.10),roof=(.38,.42,.44),
 timber=(.54,.34,.17),interior=(.80,.78,.70),floor=(.56,.48,.35),furniture=(.31,.39,.33),
 ceiling=(.82,.80,.73),lamp=(.97,.87,.67),leaf=(.22,.32,.13),flower=(.68,.59,.34),grass=(.28,.37,.16))

def wall(face,a,b,holes=(),height=4.33,role='wall',depth=.30,glazed=False):
    P.wall(face,a,b,.54 if role=='wall' else 0,height,holes,role,depth,glazed,flat_door=role=='interior')
    if role=='wall':face.wall('concrete plinth',a,b,0,.54,depth+.015,'stone',holes)
    for h in holes:
        if not h.get('door') and h['w']>2.5 and h['h']>2.5:face.part('high window transom',h['u'],.175,h['z']+h['h']-.62,h['w'],.045,.045,'trim')

def table(x,y,w=2.2,d=1.0):
    C.box('community folding table',(x,y,Z+.75),(w,d,.07),'timber','furniture')
    for dx in (-w/2+.20,w/2-.20):
        for dy in (-d/2+.14,d/2-.14):C.box('folding table leg',(x+dx,y+dy,Z+.37),(.05,.05,.74),'hardware','furniture')
    for dx in (-w*.28,w*.28):
        for sign in (-1,1):
            cy=y+sign*(d/2+.47)
            C.box('stackable chair seat',(x+dx,cy,Z+.46),(.47,.46,.065),'furniture','furniture')
            C.box('stackable chair back',(x+dx,cy+sign*.20,Z+.70),(.47,.055,.44),'furniture','furniture')
            for a in (-.17,.17):
                for b in (-.17,.17):C.box('chair leg',(x+dx+a,cy+b,Z+.23),(.03,.03,.46),'hardware','furniture')

def clip(poly,line,positive=True):
    """Half-plane clipping in XY, keeping shared weathering nodes identical."""
    a,b,c=line;out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        u=(a*p[0]+b*p[1]+c)*(1 if positive else -1)
        v=(a*q[0]+b*q[1]+c)*(1 if positive else -1)
        if u>=-1e-8:out.append(p)
        if (u>1e-8 and v<-1e-8) or (u<-1e-8 and v>1e-8):
            t=u/(u-v);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out

def area(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1])))/2
def value(plane,x,y):return plane[0]*x+plane[1]*y+plane[2]
def mainz(x):return 7.7-.32*abs(x+5)
WING=[(.20,0,3.90),(-.40,0,9.90),(0,.40,8.70),(0,-.40,5.50)]
def wingz(x,y):return min(value(p,x,y) for p in WING)

def roof():
    # Partition by every candidate plane/footprint edge, then keep only the
    # actual upper envelope. No roof plane continues through a valley.
    domains=[((.32,0,9.30),[(-15.6,-12.6),(-5,-12.6),(-5,12.6),(-15.6,12.6)],'main')]
    domains += [((-.32,0,6.10),[(-5,-12.6),(5.6,-12.6),(5.6,12.6),(-5,12.6)],'main')]
    domains += [(p,[(3.8,-12.6),(15.6,-12.6),(15.6,4.6),(3.8,4.6)],'wing') for p in WING]
    boundaries=[(1,0,-3.8),(1,0,-5.6),(0,1,-4.6)]
    allplanes=[q[0] for q in domains]
    patches=[]
    for plane,poly,kind in domains:
        parts=[poly]
        lines=boundaries+[tuple(a-b for a,b in zip(plane,other)) for other in allplanes if other!=plane]
        for line in lines:
            if abs(line[0])+abs(line[1])<1e-8:continue
            pieces=[]
            for p in parts:
                for sign in (True,False):
                    q=clip(p,line,sign)
                    if len(q)>=3 and area(q)>1e-7:pieces.append(q)
            parts=pieces
        for p in parts:
            x=sum(q[0] for q in p)/len(p);y=sum(q[1] for q in p)/len(p);z=value(plane,x,y)
            main=mainz(x) if -15.6<=x<=5.6 else -999
            wing=wingz(x,y) if 3.8<=x<=15.6 and y<=4.6 else -999
            if kind=='wing' and abs(z-wing)>1e-6:continue
            if abs(z-max(main,wing))>1e-6:continue
            top=[(a,b,value(plane,a,b)) for a,b in p]
            C.solid_surface(kind+' roof field',top,.12)
            C.solid_surface(kind+' roof lining',[(a,b,c-.12) for a,b,c in top],.055,'timber','roof')
            patches.append((p,plane,kind))
    # Close the service partition to the actual raised union roof, not the
    # original main eave. Each infill inherits the exact clipped roof plane.
    for poly,plane,kind in patches:
        p=poly
        for line in [(1,0,-5),(-1,0,5.18),(0,1,11.7),(0,-1,4),(plane[0],plane[1],plane[2]-4.49)]:p=clip(p,line)
        if len(p)<3 or area(p)<1e-7:continue
        n=len(p);vs=[(x,y,4.32) for x,y in p]+[(x,y,value(plane,x,y)-.17) for x,y in p]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        C.mesh('partition roof infill',vs,fs,'interior','envelope')
    for a,b in [(-12.6,-10.98),(2.98,4.6)]:
        C.prism('shared eave weather cheek',[(a,wingz(5.6,a)-.035),(b,wingz(5.6,b)-.035),(b,mainz(5.6)+.005),(a,mainz(5.6)+.005)],'x',5.54,5.62,'roof','roof')
    for y in (-12.6,4.6):
        C.prism('shared eave end return',[(5,wingz(5,y)-.035),(5.62,wingz(5.62,y)-.035),(5.62,mainz(5.62)+.005),(5,mainz(5)+.005)],'y',y-.035,y+.035,'roof','roof')
    # Standing seams use surface-clipped straight runs, with no rods across valleys.
    for poly,plane,kind in patches:
        axis=1 if abs(plane[0])>.01 else 0
        for i in range(-23,24):
            v=i*.6;hits=[]
            for p,q in zip(poly,poly[1:]+poly[:1]):
                a,b=p[axis],q[axis]
                if (a<=v<b) or (b<=v<a):
                    t=(v-a)/(b-a);hits.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if len(hits)==2:
                a,b=hits
                C.beam('standing seam',(a[0],a[1],value(plane,*a)+.023),(b[0],b[1],value(plane,*b)+.023),.022,.026,'roof','roof')
    # Visible source ridge, hip caps and the analytic valley.
    C.rod('main ridge cap',(-5,-12.62,7.73),(-5,12.62,7.73),.075,'roof','roof')
    C.rod('wing ridge cap',(10,-7,5.93),(10,-1,5.93),.06,'roof','roof')
    for a,b in [((10,-7),(15.6,-12.6)),((10,-1),(15.6,4.6))]:
        C.beam('outer hip cap',(*a,wingz(*a)+.03),(*b,wingz(*b)+.03),.13,.045,'roof','roof')
    # Valley segments derive directly from equality of active roof planes.
    vx=2.2/.52;vz=mainz(vx);yf=(vz-8.7)/.4;yr=(5.5-vz)/.4
    for a,b in [((5.6,-10.98),(vx,yf)),((vx,yf),(vx,yr)),((vx,yr),(5.6,2.98))]:
        C.beam('closed valley flashing',(*a,mainz(a[0])+.025),(*b,mainz(b[0])+.025),.20,.045,'roof','roof')
    for a,b in [((vx,yf),(10,-7)),((vx,yr),(10,-1))]:C.beam('inner hip cap',(*a,wingz(*a)+.035),(*b,wingz(*b)+.035),.13,.045,'roof','roof')
    C.beam('right rear eave fascia',(5.6,4.6,mainz(5.6)-.08),(5.6,12.62,mainz(5.6)-.08),.17,.20,'roof','roof')
    for y in (-12.62,12.62):
        for a,b in [(-15.6,-5),(-5,5.6)]:C.beam('main gable fascia',(a,y,mainz(a)-.08),(b,y,mainz(b)-.08),.17,.19,'roof','roof')
    C.beam('left eave fascia',(-15.6,-12.62,mainz(-15.6)-.09),(-15.6,12.62,mainz(-15.6)-.09),.17,.20,'roof','roof')
    for a,b in [((5.6,-12.6),(15.6,-12.6)),((15.6,-12.6),(15.6,4.6)),((15.6,4.6),(5.6,4.6))]:
        C.beam('wing fascia',(*a,wingz(*a)-.08),(*b,wingz(*b)-.08),.17,.20,'roof','roof')
    for y in (-10,-5,0,5,10):
        for a,b in [(-15,-5),(-5,5)]:C.beam('hall timber rafter',(a,y,mainz(a)-.35),(b,y,mainz(b)-.35),.20,.36,'timber','structure')
        C.beam('hall truss tie',(-14.7,y,4.08),(4.7,y,4.08),.17,.22,'timber','structure')
        C.beam('king post',(-5,y,4.08),(-5,y,7.33),.17,.17,'timber','structure')

def build():
    P.OBS.clear()
    C.box('earth site base',(0,-1,.0125),(44,38,.025),'soil','site',0)
    C.box('north lawn surface',(0,.1,.0325),(44,35.8,.015),'grass','site',0)
    C.box('street lawn strip',(0,-19.75,.0325),(44,.5,.015),'grass','site',0)
    C.box('main occupied floor',(-5,0,.08),(20,24,.12),'floor','floors',0)
    C.box('wing occupied floor',(10,-4,.08),(10,16,.12),'floor','floors',0)
    front=C.Face((0,-12,0),(1,0,0),(0,1,0),'hall front')
    openings=[P.h('hall window '+str(i),x,.64,3.65,2.80) for i,x in enumerate((-11.6,-6.6,-1.6))]
    openings += [P.h('public door',3.3,Z,1.65,2.6,True),P.h('entry sidelight',1.86,.64,1.0,2.1),P.h('entry transom',3.3,2.95,1.65,.49)]
    wall(front,-15,5,openings,glazed=True)
    for y in (-12,12):C.prism('main masonry gable',[(-15,4.33),(-5,7.53),(5,4.33)],'y',y if y<0 else y-.30,y+.30 if y<0 else y,'wall')
    wall(C.Face((-15,0,0),(0,1,0),(1,0,0),'left hall'),-11.7,11.7,[P.h('side hall '+str(i),y,.64,2.80,2.8) for i,y in enumerate((-8,-2,4,9))])
    wall(C.Face((0,12,0),(1,0,0),(0,-1,0),'rear hall'),-15,5,[P.h('rear hall '+str(i),x,.64,3.2,2.8) for i,x in enumerate((-11,-5))]+[P.h('rear exit',3.3,Z,1.3,2.4,True)])
    wall(C.Face((5,0,0),(0,1,0),(-1,0,0),'hall right rear'),4,11.7,[P.h('rear side light',8,.8,1.6,2.5)])
    wall(C.Face((0,-12,0),(1,0,0),(0,1,0),'wing front'),5,15,[P.h('kitchen front '+str(i),x,.80,1.0,1.9) for i,x in enumerate((6.5,9,11.5))]+[P.h('service door',13.7,Z,1.1,2.2,True)],3.73)
    wall(C.Face((15,0,0),(0,1,0),(-1,0,0),'wing right'),-11.7,3.7,[P.h('wing side '+str(i),y,1.15,1.4,1.5) for i,y in enumerate((-9,-6,-2,2))],3.73)
    wall(C.Face((0,4,0),(1,0,0),(0,-1,0),'wing rear'),5,15,[P.h('meeting rear',11,.80,4.5,2.15)],3.73)
    wall(C.Face((5,0,0),(0,1,0),(1,0,0),'main to service rooms'),-11.7,4,[P.h('kitchen portal',-8,Z,1.35,2.35,True),P.h('washroom approach',-2,Z,1.35,2.35,True),P.h('meeting portal',1.7,Z,1.35,2.35,True)],4.33,'interior',.18)
    for y in (-4.5,-1):wall(C.Face((0,y,0),(1,0,0),(0,1,0),'wing partition'),5.18,14.7,(),3.60,'interior',.13)
    wall(C.Face((7.5,0,0),(0,1,0),(1,0,0),'WC doorway'),-4.37,-1,[P.h('WC door',-2,Z,1.25,2.35,True)],3.60,'interior',.13)
    C.box('wing ceiling',(10,-4,3.66),(9.6,15.5,.12),'ceiling','ceiling',0)
    roof()
    for x in (-11.6,-6.6,-1.6):
        for y in (-8,-2,4):table(x,y)
    # Community notice board and movable-event storage remain against solid walls.
    C.box('community notice backing',(-.5,11.66,2.0),(3.3,.07,.90),'timber','furniture')
    for x in (-1.55,-.85,-.15,.55):C.box('pinned event sheet',(x,11.61,2.0),(.48,.015,.65),'interior','decor')
    C.box('folded table trolley base',(-11,9.8,Z+.18),(2.6,1.0,.15),'hardware','furniture')
    for y in (9.5,9.7,9.9,10.1):C.box('stored folded table',(-11,y,Z+1.05),(2.3,.075,1.45),'timber','furniture')
    for x in (-12.05,-9.95):
        for y in (9.5,10.1):C.rod('trolley wheel',(x-.06,y,Z+.12),(x+.06,y,Z+.12),.12,'hardware','furniture')
    # Kitchen: sink, work bench, oven, hob, fridge and preparation table.
    L.basin(10,-4.9)
    C.box('range',(12.3,-4.98,Z+.45),(1.15,.80,.9),'hardware','furniture')
    C.box('oven door',(12.3,-5.40,Z+.46),(.88,.025,.54),'trim','furniture')
    for x in (12.02,12.58):
        for y in (-5.18,-4.82):C.rod('hob',(x,y,Z+.91),(x,y,Z+.93),.115,'trim','furniture')
    C.box('extractor canopy',(12.3,-4.97,2.25),(1.25,.78,.24),'hardware','furniture')
    C.box('extractor duct',(12.3,-4.70,2.975),(.40,.35,1.25),'hardware','furniture')
    C.box('kitchen fridge',(14.14,-7.55,Z+1.0),(1.0,.96,2.0),'ceiling','furniture')
    C.box('prep counter',(9.2,-8,Z+.46),(2.8,1.0,.92),'timber','furniture')
    C.box('prep counter top',(9.2,-8,Z+.96),(2.86,1.06,.08),'stone','furniture')
    C.box('cutting board',(9.6,-8,Z+1.015),(.55,.38,.025),'timber','decor')
    L.basin(9.5,-1.35);L.toilet(12.8,-1.50)
    C.box('WC mirror',(9.5,-1.015,1.75),(1.1,.03,.7),'glass','furniture')
    C.rod('WC support rail',(13.55,-2.05,Z+.78),(13.55,-1.25,Z+.78),.035,'hardware','furniture')
    for y in (-2.05,-1.25):C.rod('WC support leg',(13.55,y,Z),(13.55,y,Z+.78),.026,'hardware','furniture')
    table(10.5,1.7,2.8,1.0)
    C.box('meeting whiteboard',(14.685,.0,1.8),(.03,1.8,1.0),'ceiling','furniture')
    # Cedar porch supported on concrete-footed posts, with a low complete cap.
    for x in (1.2,5.4):
        C.box('porch masonry foot',(x,-13.6,.54),(.65,.65,1.08),'stone','structure')
        C.box('cedar porch post',(x,-13.6,2.26),(.22,.22,2.50),'timber','structure')
    C.box('cedar porch header',(3.3,-13.6,3.50),(4.65,.27,.30),'timber','structure')
    C.box('porch cedar soffit',(3.3,-12.9,3.66),(4.90,2.45,.18),'timber','roof')
    C.box('porch metal cap',(3.3,-12.9,3.79),(5.0,2.55,.10),'roof','roof')
    C.box('entry forecourt',(5.5,-14.5,.09),(19,5,.10),'paving','site',0)
    C.box('front hall path',(-10,-13.65,.09),(12,2.3,.10),'paving','site',0)
    C.box('side lawn path',(-16.6,-2.5,.09),(2,24.6,.10),'paving','site',0)
    C.box('side bench pad',(-18.3,4,.09),(2.1,3.5,.10),'paving','site',0)
    C.box('rear exit landing',(3.3,13,.09),(3.2,2.5,.10),'paving','site',0)
    C.box('public sidewalk',(0,-18.65,.02),(44,1.7,.04),'paving','site',0)
    C.prism('public approach ramp',[(-18.3,0),(-18.3,.04),(-17,.14),(-17,0)],'x',1.4,5.2,'paving','site')
    for x in (-2,-.8):B.bikehoop(x,-15.7)
    B.bench(8.0,-15.9);B.bench(-18.25,4)
    for x in (-12,-7,-2):R.plantbed(x,-12.6,3.8,.8)
    R.plantbed(9.6,-12.6,6.0,.8)
    for x,y,seed in [(-20,-13,701),(-20,11,702),(19,11,703),(19,-13,704)]:R.tree(x,y,seed)
    for x,y in [(-11,-8),(-6,-8),(-1,-8),(-11,-2),(-6,-2),(-1,-2),(-11,4),(-6,4),(-1,4),(-5,9),(10,-8),(10,-1.5),(10,1.7)]:
        height=3.3 if x>5 else 3.85
        C.qa_room_light('community hall',(x,y,height-.15),260,2.5);R.lamp(x,y,height,.8)
        C.rod('pendant rod',(x,y,height+.035),(x,y,3.60 if x>5 else mainz(x)-.18),.014,'hardware','structure')
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    tris=[];routes=[];obs=P.OBS
    def rect(a,b,c,d,z=Z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    rect(-14.68,-11.68,4.99,11.68);rect(4.99,-11.68,14.68,3.68)
    rect(-4,-17,15,-11.6);rect(-16,-14.8,-4,-12.5);rect(-17.6,-14.8,-15.6,9.8);rect(-19.35,2.25,-17.6,5.75)
    rect(1.7,11.6,4.9,14.25);rect(1.4,-19,5.2,-18.3,.04)
    a=[1.4,-18.3,.04];b=[5.2,-18.3,.04];c=[5.2,-17,Z];d=[1.4,-17,Z];tris.extend([[a,b,c],[a,c,d]])
    def route(name,xy):routes.append(dict(name=name,points=[[x,y,Z] for x,y in xy]))
    routes.append(dict(name='Public ground to hall',points=[[3.3,-18.8,.04],[3.3,-18.3,.04],[3.3,-17,Z],[3.3,-10.3,Z]]))
    route('Hall main aisle',[(3.3,-10.3),(3.3,9)])
    for y in (-8,-2,4):route('Gathering row '+str(y),[(3.3,y-2.2),(-13.7,y-2.2),(-13.7,y)])
    route('Event storage',[(3.3,8),(-8.6,8),(-8.6,9.5)])
    route('Community noticeboard',[(3.3,9),(-.5,9),(-.5,10.8)])
    route('Kitchen entry',[(3.3,-8),(6.6,-8),(6.6,-6),(9,-6)])
    route('Kitchen service door',[(13.7,-16),(13.7,-10.3),(11.5,-10.3),(11.5,-6)])
    route('Washroom',[(3.3,-2),(8.5,-2),(9.5,-2.4)])
    route('Meeting room',[(3.3,1.7),(8.4,1.7)])
    route('Rear exit',[(3.3,9),(3.3,13.4)])
    route('Forecourt bench',[(3.3,-17),(3.3,-14.4),(9.8,-14.4),(9.8,-15.9)])
    route('Bicycle approach',[(3.3,-14.4),(-2,-14.4)])
    route('Side gathering lawn',[(3.3,-14.4),(-16.6,-14.4),(-16.6,2.6),(-18.25,2.6),(-18.25,3.2)])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'open leaf' in o.name or o.name.startswith('bike rack')
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in o.name for s in ('ceiling','luminaire','diffuser','rafter','pendant','truss','king post')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    return dict(version=2,footprint=[44,38],entrance=[3.3,-18.8,.04],maxStepM=.18,triangles=tris,obstacles=obs,portals=[[1.4,5.2,-19,-17.5]],routes=routes,gardenExclusionProbes=[dict(name='bench',point=[8,-15.9,Z]),dict(name='lawn bench',point=[-18.25,4,Z])]+[dict(name='bike'+str(i),point=[x,-15.7,Z]) for i,x in enumerate((-2,-.8))])

def cameras():
    cams=[]
    for n,loc in [('front',(0,-58,7)),('front_corner',(-42,-47,25)),('aerial',(37,-42,53)),('left_side',(-57,0,12)),('right_side',(57,0,12)),('rear',(0,55,14)),('rear_side',(40,37,27))]:cams.append(dict(name=n,location=loc,target=(0,0,3),whole=True,lens=52))
    for n,loc,t,lens in [
      ('facade_close',(-12,-22,5),(-4,-12,2.7),32),('architecture_close',(8,-21,4),(3.3,-12.5,1.8),30),('glass_close',(-6.6,-16,2.0),(-6.6,-8,1.3),30),
      ('roof_contact',(17,-20,17),(5,-3,4.8),35),('roof_rear_contact',(15,17,14),(5,1.5,4.7),35),
      ('program_interior',(3,-10.5,1.8),(-6,-1,1.2),22),('hall_rear',(-13.4,9,1.8),(-4,-4,1.2),23),('hall_trusses',(-13,6,2.1),(-5,0,5.8),24),
      ('community_storage',(-6,7.6,1.8),(-10,10,1.2),25),('kitchen',(5.7,-10.8,1.8),(10.5,-6,1.1),22),('kitchen_sink',(9,-6.2,1.7),(10,-4.9,1.0),27),
      ('kitchen_service',(14.6,-8.8,1.8),(13.7,-12,1.2),25),('washroom',(8,-3.6,1.8),(11.5,-1.6,.9),22),('washroom_sink',(8.7,-3.3,1.7),(9.5,-1.35,1),26),('washroom_toilet',(11.5,-3.2,1.7),(12.9,-1.4,.8),28),
      ('meeting',(5.5,-.5,1.8),(11,1.7,1.2),23),('forecourt',(14,-24,6),(1,-14,1.0),30),('public_approach',(7,-21,1.3),(3.3,-17.4,.14),28),('side_lawn',(-23,-3,6),(-17,4,.9),28)]:cams.append(dict(name=n,location=loc,target=t,whole=False,lens=lens))
    return cams

if __name__=='__main__':D.run(__file__,'hall-prework.json','hall-prairie',PALETTE,cameras,build,network,'hall-buff-brick.png',[1.584,1.68],extra_scripts=[P.__file__,L.__file__])
