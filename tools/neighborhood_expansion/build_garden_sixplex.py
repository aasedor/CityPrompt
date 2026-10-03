"""Six garden flats, three private straight stairs and short intersecting gables."""
from pathlib import Path
import math
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy
import build_corner_fourplex as P  # Atomic opening and bed fixtures.
import build_library_pavilion as L  # Hollow ceramic fixtures and domestic table.

Z=.14
RISE=3.1
W=25/3
MS=2.67/7.65
CS=2.12/(W/2)
JOIN=(8.95-9.5)/MS
PATCHES=[]
PALETTE=dict(B.PALETTE,wall=(.72,.65,.54),trim=(.12,.13,.12),roof=(.40,.43,.44),
 timber=(.54,.36,.20),interior=(.82,.80,.73),floor=(.59,.49,.36),furniture=(.34,.41,.32),
 ceiling=(.85,.82,.75),lamp=(.97,.88,.71),leaf=(.23,.34,.14),flower=(.73,.66,.48),
 grass=(.28,.37,.16),mirror=(.79,.81,.81))

def X(bay,u):return -12.5+bay*W+(W-u if bay==2 else u)

def clip(poly,line,positive=True):
    a,b,c=line;out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        u=(a*p[0]+b*p[1]+c)*(1 if positive else -1)
        v=(a*q[0]+b*q[1]+c)*(1 if positive else -1)
        if u>=-1e-8:out.append(p)
        if u*v<-1e-16:
            t=u/(u-v);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out

def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2
def value(p,x,y):return p[0]*x+p[1]*y+p[2]

def roof_graph():
    patches=[((0,-MS,9.5),[(-12.65,0),(12.65,0),(12.65,7.65),(-12.65,7.65)],'main rear')]
    main=(0,MS,9.5)
    for i,cx in enumerate((-W,0,W)):
        a=-12.65 if i==0 else cx-W/2;b=12.65 if i==2 else cx+W/2
        for sign,lo,hi in ((1,a,cx),(-1,cx,b)):
            cross=(sign*CS,0,8.95-sign*CS*cx)
            poly=[(lo,-7.65),(hi,-7.65),(hi,0),(lo,0)]
            line=tuple(a-b for a,b in zip(cross,main))
            for p,positive,label in ((cross,True,'cross'),(main,False,'main front')):
                q=clip(poly,line,positive)
                if len(q)>=3 and area(q)>1e-7:patches.append((p,q,f'{label} {i} {sign}'))
    return patches

def roofs():
    PATCHES.extend(roof_graph())
    for plane,poly,label in PATCHES:
        outline=[(x,y,value(plane,x,y)) for x,y in poly]
        C.solid_surface(label+' metal',outline,.12)
        C.solid_surface(label+' cream lining',[(x,y,z-.12) for x,y,z in outline],.055,'ceiling','roof')
        # Seams follow each plane's fall and stop on the analytic boundaries.
        axis=1 if label.startswith('cross') else 0
        for j in range(-32,33):
            v=j*.45;hits=[]
            for p,q in zip(poly,poly[1:]+poly[:1]):
                if (p[axis]<=v<q[axis]) or (q[axis]<=v<p[axis]):
                    t=(v-p[axis])/(q[axis]-p[axis]);hits.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if len(hits)==2:
                a,b=hits;C.beam(label+' standing seam',(*a,value(plane,*a)+.018),(*b,value(plane,*b)+.018),.018,.026,'roof','roof')
    C.rod('common main ridge',(-12.67,0,9.53),(12.67,0,9.53),.052,'roof','roof')
    for cx in (-W,0,W):
        C.rod('short cross ridge',(cx,-7.67,8.98),(cx,JOIN,8.98),.05,'roof','roof')
        for sign in (-1,1):
            a=(cx+sign*W/2,-7.65,6.83);b=(cx,JOIN,8.95)
            C.beam('analytic valley flashing',(a[0],a[1],a[2]+.024),(b[0],b[1],b[2]+.024),.16,.04,'roof','roof')
            C.beam('front gable fascia',(cx+sign*W/2,-7.66,6.73),(cx,-7.66,8.85),.13,.18,'roof','roof')
    for x in (-12.66,12.66):
        for y in (-7.65,7.65):C.beam('side gable fascia',(x,y,6.73),(x,0,9.40),.13,.18,'roof','roof')
    C.box('rear continuous gutter',(0,7.64,6.72),(25.32,.16,.16),'roof','roof')
    for x in (-12.52,-W/2,W/2,12.52):
        C.rod('front rainwater pipe',(x,-7.56,.15),(x,-7.56,6.79),.046,'roof','structure')
    for x in (-12.52,12.52):C.rod('rear rainwater pipe',(x,7.56,.15),(x,7.56,6.79),.046,'roof','structure')

def roof_wall_fill(a,b,c,d):
    # Every wall-band top follows the actual roof patches through its depth.
    for plane,poly,label in PATCHES:
        q=poly
        for line in ((1,0,-a),(-1,0,b),(0,1,-c),(0,-1,d)):q=clip(q,line)
        if len(q)<3 or area(q)<1e-7:continue
        top=[(x,y,value(plane,x,y)-.17) for x,y in q];n=len(q)
        vs=top+[(x,y,6.60) for x,y in q]
        fs=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
        C.mesh('roof seated masonry '+label,vs,fs,'wall','envelope')

def partition_x(x,a,b,z,doors=()):
    P.wall(C.Face((x,0,0),(0,1,0),(1,0,0),'private stair enclosure'),a,b,z,z+2.96,
           [P.h('upper flat doorway',y,z,1.20,2.30,True) for y in doors],'interior',.14,flat_door=True)

def partition_y(y,a,b,z,doors=(),normal=1):
    P.wall(C.Face((0,y,0),(1,0,0),(0,normal,0),'flat partition'),a,b,z,z+2.96,
           [P.h('room doorway',x,z,1.15,2.30,True) for x in doors],'interior',.13,flat_door=True)

def kitchen(z):
    x=7.60;y=2.40
    base=C.box('kitchen cabinet',(x,y,z+.44),(.68,1.75,.88),'timber','furniture')
    C.cut_box(base,'cabinet basin cavity',(x,y-.40,z+.85),(.48,.64,.40))
    counter=C.box('kitchen stone counter',(x,y,z+.91),(.74,1.81,.06),'stone','furniture')
    C.cut_box(counter,'worktop basin cut',(x,y-.40,z+.91),(.43,.59,.19))
    bowl=C.box('kitchen recessed bowl',(x,y-.40,z+.80),(.46,.62,.23),'hardware','furniture')
    C.cut_box(bowl,'real sink recess',(x,y-.40,z+.87),(.40,.56,.25))
    C.rod('kitchen mixer',(x+.23,y-.40,z+.93),(x+.23,y-.40,z+1.20),.02,'hardware','furniture')
    C.rod('kitchen mixer spout',(x+.23,y-.40,z+1.20),(x,y-.40,z+1.20),.02,'hardware','furniture')
    C.box('two-ring cooktop',(x,y+.40,z+.955),(.52,.58,.035),'hardware','furniture')
    for dx in (-.14,.14):C.rod('hob ring',(x+dx,y+.40,z+.976),(x+dx,y+.40,z+.982),.085,'trim','furniture',16)
    C.box('wall seated upper cabinet',(7.843,2.40,z+1.97),(.38,1.60,.70),'timber','furniture')
    C.box('refrigerator',(5.99,3.18,z+.96),(.82,.75,1.92),'ceiling','furniture')
    for yy in (2.02,2.78):C.box('cabinet handle',(7.245,yy,z+.72),(.025,.22,.025),'hardware','furniture')

def bathroom(z):
    old=L.Z;L.Z=z
    L.toilet(2.20,3.10)
    L.Z=old
    # Domestic vanity fits the side room without penetrating its flank carrier.
    base=C.box('bath vanity cabinet',(1.0,3.18,z+.42),(.95,.68,.84),'timber','furniture')
    C.cut_box(base,'bath basin clearance',(1.0,3.18,z+.83),(.60,.49,.40))
    top=C.box('bath vanity worktop',(1.0,3.18,z+.88),(1.01,.73,.08),'stone','furniture')
    C.cut_box(top,'bath counter aperture',(1.0,3.18,z+.89),(.53,.43,.22))
    bowl=C.box('bath ceramic bowl',(1.0,3.18,z+.77),(.57,.47,.25),'hardware','furniture')
    C.cut_box(bowl,'bath bowl interior',(1.0,3.18,z+.86),(.50,.40,.27))
    C.rod('bath tap',(1.0,3.44,z+.90),(1.0,3.44,z+1.20),.02,'hardware','furniture')
    C.rod('bath spout',(1.0,3.44,z+1.20),(1.0,3.20,z+1.20),.02,'hardware','furniture')
    C.box('bath mirror',(.92,3.7075,z+1.53),(.72,.025,.70),'mirror','furniture')
    C.box('shower tray',(.92,2.00,z+.065),(.92,.95,.13),'stone','furniture')
    C.box('shower side screen',(.46,2.00,z+1.06),(.012,.95,1.96),'glass','furniture')
    C.rod('shower riser',(.50,1.80,z+.85),(.50,1.80,z+2.13),.018,'hardware','furniture')
    C.rod('shower head',(.50,1.80,z+2.13),(.75,1.80,z+2.13),.045,'hardware','furniture')
    for zz in (1.05,1.90):C.rod('shower wall bracket',(.30,1.80,z+zz),(.50,1.80,z+zz),.025,'hardware','furniture')

def chair(u,y,z):
    C.box('balcony chair seat',(u,y,z+.46),(.48,.48,.07),'furniture','furniture')
    C.box('balcony chair back',(u,y+.21,z+.73),(.48,.06,.48),'timber','furniture')
    for dx in (-.18,.18):
        for dy in (-.18,.18):C.box('balcony chair foot',(u+dx,y+dy,z+.22),(.035,.035,.44),'hardware','furniture')

def straight_stair():
    lo=-5.30;step=.28;r=RISE/18;poly=[(lo,0),(lo,Z+r)]
    for j in range(18):
        y=lo+(j+1)*step;zz=Z+(j+1)*r;poly.append((y,zz))
        if j<17:poly.append((y,zz+r))
    poly += [(lo+18*step,Z+RISE-.26),(lo,Z-.14)]
    C.prism('private continuous straight stair',poly,'x',6.62,7.72,'stone','circulation')
    for u in (6.66,7.68):
        pts=[(u,lo+(j+.5)*step,Z+(j+1)*r) for j in range(18)]
        for p in pts:C.rod('seated private stair post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
        for a,b in zip(pts,pts[1:]):C.beam('private stair handrail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.04,.04,'trim','stair guard')
    # Wall-bound stair void sides are enclosed; the upper mouth stays open.
    C.qa_room_light('private upper stair',(7.17,-2.0,5.85),130,1.5)

def transform_bay(bay,objects,openings,obstacles):
    sign=-1 if bay==2 else 1
    for obj in objects:
        if obj.type=='MESH':
            for v in obj.data.vertices:v.co.x=X(bay,v.co.x)
            if sign<0:C.normalise(obj.data)
        else:obj.location.x=X(bay,obj.location.x)
    for opening in openings:
        opening['face_origin'][0]=X(bay,opening['face_origin'][0])
        opening['face_tangent'][0]*=sign;opening['face_inward'][0]*=sign
    for o in obstacles:
        o[0],o[1]=sorted((X(bay,o[0]),X(bay,o[1])))

def bay_geometry(bay):
    before=set(bpy.context.scene.objects);oi=len(C.OPENINGS);ob=len(P.OBS)
    for level in range(2):
        z=Z+level*RISE
        front=C.Face((0,-7.5,0),(1,0,0),(0,1,0),'garden sixplex front '+str((bay,level)))
        if not level:
            hs=[P.h('lower living glazing',2.55,z+.55,3.65,2.05),P.h('lower private entry',5.65,z,1.05,2.45,True),P.h('upper private entry',7.15,z,1.05,2.45,True)]
            P.wall(front,0,W,0,Z+RISE,hs,flat_door=False)
            for u in (5.02,6.40,7.79):front.part('cedar entry pier',u,-.045,1.40,.11,.10,2.53,'timber')
            front.part('paired entry soffit',6.4,-.12,2.72,2.94,.50,.13,'ceiling','structure')
        else:
            hole=P.h('uncovered balcony opening',W/2,z+.30,W-1.40,2.57,True)
            front.wall('upper recessed balcony carrier',0,W,z,6.60,.30,'wall',[hole])
            for a,b in ((0,.70),(W-.70,W)):P.OBS.append([a,b,-7.5,-7.2,z,6.60])
            P.OBS.append([.70,W-.70,-7.5,-7.2,z,z+.30])
            for u,n in ((.70,1),(W-.70,-1)):
                P.wall(C.Face((u,0,0),(0,1,0),(n,0,0),'balcony brick cheek'),-7.2,-5.85,z,6.60,depth=.15)
            back=C.Face((0,-5.85,0),(1,0,0),(0,1,0),'upper occupied glazing')
            P.wall(back,.85,W-.30,z,6.60,[P.h('upper living glazing',2.9,z+.10,4.10,2.40),P.h('balcony door',5.65,z,1.25,2.40,True)],glazed=True)
            C.railing('balcony front guard',(.85,-7.40,z+.30),(W-.85,-7.40,z+.30),bottom=0)
            for y in (-7.05,-6.90,-6.75,-6.60,-6.45,-6.30,-6.15,-6.0):
                C.box('cedar balcony screen',(.866,y,z+1.50),(.035,.09,2.62),'timber','structure')
            chair(2.7,-6.65,z);chair(4.4,-6.65,z)
            C.box('balcony small table',(3.55,-6.70,z+.65),(.65,.55,.065),'timber','furniture')
            for u in (3.30,3.80):C.box('balcony table support',(u,-6.7,z+.315),(.045,.40,.63),'hardware','furniture')
        floor=C.box('flat occupied slab',(W/2,0,z-.07),(W,15,.14),'floor','floors',0)
        ceiling=C.box('flat occupied ceiling',(W/2,0,z+2.91),(W-.6,14.4,.10),'ceiling','ceiling',0)
        if level:C.box('recess front soffit closure',(W/2,-7.35,z+2.91),(W-1.7,.30,.10),'ceiling','ceiling',0)
        if level:C.cut_box(floor,'private stair upper void',(7.17,-2.78,z),(1.40,5.04,.7))
        else:C.cut_box(ceiling,'private stair headroom',(7.17,-2.78,z+2.91),(1.40,5.04,.7))
        start=-5.55 if level else -7.2
        partition_x(6.40,start,1.2,z,(.45,) if level else ())
        P.wall(C.Face((7.95,0,0),(0,1,0),(-1,0,0),'stair outer enclosure'),start,1.2,z,z+2.96,role='interior',depth=.14)
        partition_y(1.20,6.40,7.95,z,normal=-1)
        partition_y(3.85,.30,W-.30,z,(5.15,),normal=-1)
        partition_y(1.30,.30,3.0,z,(2.1,))
        P.wall(C.Face((3.0,0,0),(0,1,0),(-1,0,0),'bath inner wall'),1.30,3.72,z,z+2.96,role='interior',depth=.13)
        B.sofa(2.6,-3.7,z);P.bed(2.2,5.45,z);kitchen(z);bathroom(z)
        old=L.Z;L.Z=z;table_before=set(bpy.context.scene.objects)
        L.table(3.8,1.90,1.5,.85);L.Z=old
        for o in set(bpy.context.scene.objects)-table_before:
            if o.name.startswith('reading book'):
                for v in o.data.vertices:v.co.z-=.01
        C.box('living rug',(2.6,-4.1,z+.003),(3.1,2.6,.006),'interior','decor',0)
        C.box('coffee table',(2.6,-5.05,z+.43),(1.1,.60,.065),'timber','furniture')
        for u in (2.18,3.02):C.box('coffee table foot',(u,-5.05,z+.20),(.055,.44,.40),'hardware','furniture')
        C.box('bedroom wardrobe',(7.20,6.67,z+1.10),(1.45,.66,2.20),'timber','furniture')
        C.box('bedside cabinet',(3.62,5.70,z+.28),(.55,.55,.56),'timber','furniture')
        for u,y in ((3.6,-2.1),(4.6,1.8),(4.4,5.4),(1.8,2.5)):
            C.qa_room_light('garden flat',(u,y,z+2.70),110,1.6);R.lamp(u,y,z+2.845,.65)
    straight_stair()
    transform_bay(bay,set(bpy.context.scene.objects)-before,C.OPENINGS[oi:],P.OBS[ob:])

def build():
    P.OBS.clear();PATCHES.clear()
    bs=C.MATS['mirror'].node_tree.nodes['Principled BSDF'];bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.055
    C.box('earth site',(0,.5,.0125),(34,28,.025),'soil','site',0)
    C.box('shared garden turf',(0,1.5,.0325),(34,26,.015),'grass','landscape',0)
    C.box('public sidewalk',(0,-12.4,.02),(34,1.8,.04),'paving','site',0)
    for i in range(3):bay_geometry(i)
    for level in range(2):
        z=Z+level*RISE
        for x,normal in ((-12.5,1),(12.5,-1)):
            f=C.Face((x,0,0),(0,1,0),(normal,0,0),'garden sixplex flank')
            P.wall(f,-7.2,7.2,0 if not level else z,Z+RISE if not level else 6.60,
                   [P.h('four flank windows '+str((x,level,j)),y,z+(1.25 if j==2 else .75),1.2,1.40 if j==2 else 1.90) for j,y in enumerate((-4.7,-1.6,2.5,5.65))])
        rear=C.Face((0,7.5,0),(1,0,0),(0,-1,0),'garden sixplex rear')
        hs=[P.h('rear bedroom '+str((i,level)),X(i,3.0 if level else 2.8),z+.75,3.2 if level else 3.0,1.9) for i in range(3)]
        hs += [P.h('private rear garden exit '+str(i),X(i,5.15),z,1.15,2.35,True) for i in range(3)] if not level else []
        P.wall(rear,-12.5,12.5,0 if not level else z,Z+RISE if not level else 6.60,hs,flat_door=False)
    # Inferred shared masonry/service bands give every flat the same .30m inset.
    for x in (-W/2,W/2):P.wall(C.Face((x-.30,0,0),(0,1,0),(1,0,0),'party wall'),-7.2,7.2,0,6.60,role='interior',depth=.60)
    roofs()
    for r in [(-12.5,12.5,-7.5,-7.2),(-12.5,12.5,7.2,7.5),(-12.5,-12.2,-7.2,7.2),(12.2,12.5,-7.2,7.2)]:roof_wall_fill(*r)
    for i in range(3):
        lo,hi=sorted((X(i,4.92),X(i,7.88)))
        C.prism('solid paired entry ramp',[(-9.2,0),(-9.2,.04),(-7.7,Z),(-7.7,0)],'x',lo,hi,'paving','site')
        C.box('paired entry threshold',((lo+hi)/2,-7.4,.07),(hi-lo,.60,.14),'paving','site',0)
        C.box('front garden walk',((lo+hi)/2,-10.2,.0475),(hi-lo,2,.015),'paving','site',0)
        R.plantbed(X(i,2.5),-9.6,3.9,1.15)
        C.box('rear exit pad',(X(i,5.15),8.25,.07),(1.55,1.50,.14),'paving','site',0)
        C.prism('rear exit ramp',[(9.0,0),(9.0,Z),(10.0,.04),(10.0,0)],'x',X(i,5.15)-.775,X(i,5.15)+.775,'paving','site')
    C.box('shared side path',(14.9,0,.0475),(1.6,24,.015),'paving','site',0)
    C.box('rear garden path',(0,10.3,.0475),(31.4,1.1,.015),'paving','site',0)
    C.box('bike pad',(-14.7,-9.7,.0475),(2.2,2.5,.015),'paving','site',0)
    for y in (-10.2,-9.2):B.bikehoop(-14.7,y)
    B.bench(0,12.0);B.bench(-9.0,12.0)
    for x in (-12,-5,5,12):R.plantbed(x,13.4,3.1,.65)
    for x,y,seed in ((-15,-6,401),(16.35,-6,409),(-14,11.8,419),(13,12.3,421)):R.tree(x,y,seed)
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':
            o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
            o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    triangles=[];routes=[];obs=list(P.OBS)
    def rect(a,b,c,d,z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];triangles.extend([[p,q,r],[p,r,s]])
    def localrect(i,a,b,c,d,z):
        lo,hi=sorted((X(i,a),X(i,c)));rect(lo,b,hi,d,z)
    def route(i,name,points):routes.append(dict(name='Bay '+str(i+1)+' '+name,points=[[X(i,u),y,z] for u,y,z in points]))
    for i in range(3):
        for level in range(2):
            z=Z+level*RISE
            localrect(i,.30,-7.2,6.40,7.2,z)
            localrect(i,6.40,1.2,W-.30,7.2,z)
            localrect(i,6.54,-.26,7.81,1.2,z)
            if not level:localrect(i,6.54,-7.2,7.81,-5.30,z)
            else:
                localrect(i,.85,-7.46,W-.85,-5.85,z)
                localrect(i,6.40,-.15,6.54,1.05,z)
                route(i,'upper flat entry',[(7.17,.45,z),(5.0,.45,z),(4.9,-2.2,z)])
                route(i,'balcony',[(4.9,-2.2,z),(5.65,-2.2,z),(5.65,-6.5,z),(6.70,-6.5,z)])
            label='lower' if level==0 else 'upper'
            route(i,label+' bedroom',[(4.9,0,z),(5.15,0,z),(5.15,4.7,z)])
            route(i,label+' bathroom',[(4.9,0,z),(2.10,0,z),(2.10,2.15,z)])
            route(i,label+' kitchen',[(4.9,0,z),(4.9,1.5,z),(6.70,1.5,z),(6.70,2.0,z)])
        for j in range(18):localrect(i,6.62,-5.30+j*.28,7.72,-5.30+(j+1)*.28,Z+(j+1)*RISE/18)
        # Interior tread waypoints avoid shared riser edges and float32 ray ambiguity.
        pts=[(7.17,-5.55,Z),(7.17,-5.285,Z+RISE/18),(7.17,-.27,Z+RISE),(7.17,.45,Z+RISE)]
        route(i,'private stair ascent',pts);route(i,'private stair descent',list(reversed(pts)))
        localrect(i,4.92,-11.2,7.88,-9.2,.055)
        a=[X(i,4.92),-9.2,.04];b=[X(i,7.88),-9.2,.04];c=[X(i,7.88),-7.7,Z];d=[X(i,4.92),-7.7,Z];triangles.extend([[a,b,c],[a,c,d]])
        localrect(i,4.92,-7.7,7.88,-7.1,Z)
        route(i,'lower public entry',[(5.65,-12.4,.04),(5.65,-9.2,.04),(5.65,-7.0,Z),(5.65,-3.9,Z),(4.9,-3.9,Z),(4.9,-2.2,Z)])
        route(i,'upper private approach',[(7.15,-12.4,.04),(7.15,-9.2,.04),(7.15,-7.0,Z),(7.17,-5.55,Z)])
        localrect(i,4.375,7.1,5.925,9.0,Z)
        a=[X(i,4.375),9.0,Z];b=[X(i,5.925),9.0,Z];c=[X(i,5.925),10.0,.04];d=[X(i,4.375),10.0,.04];triangles.extend([[a,b,c],[a,c,d]])
        route(i,'lower rear garden exit',[(5.15,4.7,Z),(5.15,8.8,Z),(5.15,10.0,.04)])
    rect(-17,-13.3,17,-11.5,.04);rect(-17,-11.5,17,-9.2,.04)
    rect(13.5,-11.5,16.6,14.0,.04);rect(-16.5,10.0,16.6,14.0,.04);rect(-16.5,-11.5,-13.5,10,.04)
    routes += [dict(name='Public route to shared rear bench',points=[[0,-12.4,.04],[14.9,-12.4,.04],[14.9,10.3,.04],[1.8,10.3,.04],[1.8,11.2,.04],[0,11.2,.04]]),dict(name='Front bicycle approach',points=[[0,-12.4,.04],[-13.5,-12.4,.04],[-13.5,-9.7,.04]])]
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'guard' in mod or 'open leaf' in o.name or o.name.startswith(('bike rack','young tree trunk','branch'))
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in o.name for s in ('ceiling','diffuser','luminaire','soffit')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    gardens=[dict(name=n,point=p) for n,p in [('shared bench',[0,12,.04]),('west bench',[-9,12,.04]),('bike1',[-14.7,-10.2,.04]),('bike2',[-14.7,-9.2,.04]),('west tree',[-14,11.8,.04]),('east tree',[13,12.3,.04])]]
    guards=[dict(name='Bay '+str(i+1)+' balcony front guard',point=[X(i,4.0),-7.25,Z+RISE]) for i in range(3)]
    return dict(version=2,footprint=[34,28],entrance=[X(0,5.65),-12.4,.04],maxStepM=.18,triangles=triangles,obstacles=obs,portals=[[-17,17,-13.3,-11.5]],routes=routes,gardenExclusionProbes=gardens,circulationExclusionProbes=guards)

def cameras():
    cams=[]
    for n,loc in [('front',(0,-51,11)),('front_corner',(37,-43,27)),('aerial',(32,-35,49)),('left_side',(-47,0,15)),('right_side',(47,0,15)),('rear',(0,49,15)),('rear_side',(-34,37,28))]:cams.append(dict(name=n,location=loc,target=(0,0,4.7),whole=True,lens=52))
    def add(n,loc,target,lens=26):cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    add('facade_close',(-18,-23,9),(-8,-7.2,4.5),35);add('architecture_close',(1,-15,3.8),(1,-7.5,2.4),30)
    add('glass_close',(-11,-13,2),(-9,-5,1.7),35)
    add('roof_contact',(-22,-21,17),(-8,-2,8.5),35);add('central_valleys',(7,-19,15),(0,-2.3,8.5),35)
    add('main_ridge_contact',(21,13,17),(8,0,9.4),35);add('public_approach',(-3,-11,1.1),(X(0,5.65),-8.2,.14),28)
    add('rear_garden',(20,19,11),(0,10.5,1.2),30)
    add('program_interior',(X(0,.65),-5.50,Z+1.65),(X(0,4.2),-2.7,Z+1.1),20)
    for i in range(3):
        def view(n,u,y,h,tu,ty,th,lens=22):add('bay'+str(i+1)+'_'+n,(X(i,u),y,h),(X(i,tu),ty,th),lens)
        for level in range(2):
            z=Z+level*RISE;tag=str(level)
            view('living_'+tag,.65,-5.50,z+1.65,4.2,-2.7,z+1.1,20)
            view('kitchen_'+tag,5.5,1.45,z+1.8,7.6,2.5,z+1.1,25)
            view('kitchen_sink_'+tag,6.3,1.3,z+1.9,7.6,2.0,z+.90,29)
            view('bedroom_'+tag,5.15,4.3,z+1.65,2.2,5.45,z+.95,23)
            view('bathroom_'+tag,2.5,1.82,z+1.65,1.45,3.05,z+.85,16)
            view('shower_'+tag,2.3,3.45,z+1.65,.80,2.0,z+1.0,22)
        view('stair',7.16,-6.5,1.80,7.17,-2.4,2.10,19)
        view('upper_landing',7.17,.90,4.9,7.17,-2.1,2.4,20)
        view('balcony',6.9,-6.5,4.89,3.0,-6.8,4.0,23)
    return cams

if __name__=='__main__':D.run(__file__,'sixplex-garden-prework.json','sixplex-garden',PALETTE,cameras,build,network,'sixplex-garden-buff-brick-v003.png',[.96,.90],extra_scripts=[P.__file__,L.__file__])
