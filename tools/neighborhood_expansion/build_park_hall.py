"""Park-edge timber hall: six outer frames, one roof, occupied civic rooms."""
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C, B, R, bpy
import build_corner_fourplex as P  # Atomic cut-carrier/open-leaf helper.
import build_library_pavilion as L  # Hollow sink and toilet only.
import build_prairie_hall as H  # Movable table/chair assembly only.

Z = .14
POSTS = [-15.6, -9.36, -3.12, 3.12, 9.36, 15.6]
SLOPE = 2.6/11.4
BRICKS = []
PALETTE = dict(B.PALETTE, wall=(.65,.43,.23), timber=(.58,.39,.22),
    stone=(.61,.57,.49), buff=(.43,.22,.13), roof=(.15,.18,.21),
    trim=(.075,.085,.08), interior=(.78,.77,.69), floor=(.60,.56,.47),
    furniture=(.28,.34,.31), ceiling=(.85,.83,.76), lamp=(.98,.87,.67),
    grass=(.29,.38,.18), leaf=(.23,.34,.13), flower=(.68,.61,.43), mirror=(.80,.82,.83))

def roofz(y): return 7.4-SLOPE*abs(y)

def brick_part(face,u,d,z,w,t,h):
    points=[face.p(u+du*w/2,d+dd*t/2,z+dz*h/2) for dz in (-1,1) for du,dd in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    BRICKS.append(points)

def brick_mesh():
    vertices=[];faces=[]
    for points in BRICKS:
        offset=len(vertices);vertices.extend(points)
        faces.extend(tuple(offset+i for i in face) for face in C.BOX_FACES)
    C.mesh('physical red brown brick courses',vertices,faces,'buff','envelope')

def clipped_brick(face,lo,hi,z0,z1,holes):
    boundaries={lo,hi}
    for hole in holes:
        for edge in (hole['u']-hole['w']/2,hole['u']+hole['w']/2):
            if lo<edge<hi:boundaries.add(edge)
    edges=sorted(boundaries)
    for left,right in zip(edges,edges[1:]):
        bands=[(z0,z1)]
        for hole in holes:
            if not hole['u']-hole['w']/2<(left+right)/2<hole['u']+hole['w']/2:continue
            pieces=[];bottom=hole['z'];top=bottom+hole['h']
            for low,high in bands:
                if high<=bottom or low>=top:pieces.append((low,high));continue
                if low<bottom:pieces.append((low,bottom))
                if high>top:pieces.append((top,high))
            bands=pieces
        for low,high in bands:
            if high-low>.0001:brick_part(face,(left+right)/2,-.009,(low+high)/2,right-left,.035,high-low)

def cedar(face, a, b, low, top, holes=()):
    """Individual board strips clipped to openings, each using one source board."""
    count=math.ceil((b-a)/.12)
    for i in range(count):
        left=a+i*.12+.002; right=min(b,a+(i+1)*.12)-.002
        if right<=left: continue
        breaks={left,right}
        for hole in holes:
            for edge in (hole['u']-hole['w']/2,hole['u']+hole['w']/2):
                if left<edge<right:breaks.add(edge)
        edges=sorted(breaks)
        for l,r in zip(edges,edges[1:]):
            intervals=[(low,min(top(l),top(r)))]
            for hole in holes:
                if not hole['u']-hole['w']/2 < (l+r)/2 < hole['u']+hole['w']/2:continue
                pieces=[]
                for z0,z1 in intervals:
                    lo=hole['z'];hi=lo+hole['h']
                    if z1<=lo or z0>=hi:pieces.append((z0,z1));continue
                    if z0<lo:pieces.append((z0,lo))
                    if z1>hi:pieces.append((hi,z1))
                intervals=pieces
            for z0,z1 in intervals:
                if z1-z0<.002:continue
                # Small strips retain the actual gable slope at their upper ends.
                upper_l=min(z1,top(l));upper_r=min(z1,top(r))
                obj=face.panel('individual cedar board',[(l,z0),(r,z0),(r,upper_r),(l,upper_l)],-.026,.006,'wall')
                obj['cedar_board']=True;obj['board_origin']=list(face.o)
                obj['board_tangent']=list(face.t);obj['board_left']=left
                obj['board_width']=right-left;obj['board_sample']=i%8
                obj['board_bottom']=.54;obj['board_full_height']=max(top(left),top(right))-.54

def board_uvs():
    original=B.uv_all
    def map_boards():
        original()
        from mathutils import Vector
        for obj in C.objects():
            if not obj.get('cedar_board'):continue
            origin=Vector(obj['board_origin']);tangent=Vector(obj['board_tangent'])
            uv=obj.data.uv_layers.active
            for poly in obj.data.polygons:
                for li in poly.loop_indices:
                    point=obj.matrix_world @ obj.data.vertices[obj.data.loops[li].vertex_index].co
                    fraction=max(0,min(1,((point-origin).dot(tangent)-obj['board_left'])/obj['board_width']))
                    u=(obj['board_sample']+.06+.88*fraction)/8
                    v=max(.005,min(.995,(point.z-obj['board_bottom'])/obj['board_full_height']))
                    # delivery applies its documented physical-tile scaling next.
                    uv.data[li].uv=(u*.96/2.4,v)
    B.uv_all=map_boards

def double_door(face, hole):
    u,z,w,ht=hole['u'],hole['z'],hole['w'],hole['h']
    for sign in (-1,1):
        face.part(hole['id']+' jamb',u+sign*(w/2-.035),.15,z+ht/2,.07,.16,ht,'trim')
        tangent=tuple(-n for n in face.n)
        inward=tuple(-sign*t for t in face.t)
        leaf=C.Face(face.p(u+sign*(w/2-.07),-.02,0),tangent,inward,hole['id']+' open leaf')
        lw=w/2-.08
        leaf.window(hole['id']+' open leaf '+str(sign),lw/2,z,lw,ht-.04,1,1,'trim',.035,sill=False,depth=.10)
        C.rod('entrance pull',leaf.p(lw-.15,-.055,z+.85),leaf.p(lw-.15,-.055,z+1.45),.018,'hardware','openings')
    face.part(hole['id']+' lintel',u,.15,z+ht,w,.16,.07,'trim')

def outside(face,a,b,holes=(),gable=False,front=False):
    height=roofz(11)-.175 if not front else roofz(-7.5)-.175
    P.wall(face,a,b,0,height,[h for h in holes if not h.get('door')], 'interior',.30)
    for h in holes:
        if not h.get('door') and h['h']>4:
            face.part(h['id']+' high transom',h['u'],.152,3.52,h['w'],.10,.055,'trim')
    # Door holes are cut into the same physical carrier and native wall obstacle.
    owner=next(o for o in reversed(C.objects()) if o.get('rlasm_wall_carrier') and o.name.startswith(face.label))
    # P.wall's carrier was entered as an obstacle without doors. Replace that
    # one record with explicit solid intervals around the full-height portals.
    del P.OBS[-1]
    doors=sorted([h for h in holes if h.get('door')],key=lambda h:h['u'])
    edges=[a]
    for h in doors:
        face.cut(owner,h['id']+' full carrier cut',h['u'],h['z'],h['w'],h['h'],.30)
        double_door(face,h)
        edges.extend([h['u']-h['w']/2,h['u']+h['w']/2])
    edges.append(b)
    for l,r in zip(edges[::2],edges[1::2]):
        pts=[face.p(u,d,0) for u in (l,r) for d in (0,.30)]
        P.OBS.append([min(p[0] for p in pts),max(p[0] for p in pts),min(p[1] for p in pts),max(p[1] for p in pts),0,height])
    if gable:
        face.panel(face.label+' closed gable',[(a,height),(b,height),(0,7.225),(a,roofz(a)-.175)],0,.30,'interior')
    top=(lambda u:roofz(u)-.175) if gable else (lambda u:height)
    cedar(face,a,b,.54,top,holes)
    face.wall(face.label+' mortar plinth',a,b,0,.54,.312,'stone',holes)
    # Physical red-brown brick courses rather than cedar texture on masonry.
    for course in range(7):
        z0=.014+course*.075;z1=z0+.062
        start=a-(.12 if course%2 else 0)
        for j in range(math.ceil((b-start)/.24)):
            lo=max(a,start+j*.24+.005);hi=min(b,start+(j+1)*.24-.005)
            if hi<=lo:continue
            clipped_brick(face,lo,hi,z0,z1,holes)

def partition(face,a,b,doors=()):
    P.wall(face,a,b,Z,3.80,doors,'interior',.15,flat_door=False)

def roof():
    for sign in (-1,1):
        y=sign*11.4
        poly=[(-16.6,0,7.4),(16.6,0,7.4),(16.6,y,4.8),(-16.6,y,4.8)]
        C.solid_surface('continuous metal slope',poly,.12)
        C.solid_surface('continuous timber lining',[(x,y,z-.12) for x,y,z in poly],.055,'timber','roof')
        for i in range(-36,37):
            x=i*.45
            if abs(x)>16.6:continue
            C.beam('standing seam',(x,0,7.422),(x,y,4.822),.022,.025,'roof','roof')
        for x in (-16.62,16.62):C.beam('gable fascia',(x,0,7.30),(x,y,4.70),.15,.21,'timber','roof')
        C.box('continuous eave gutter',(0,y,4.70),(33.25,.17,.18),'roof','roof')
    C.rod('single ridge cap',(-16.65,0,7.44),(16.65,0,7.44),.065,'roof','roof')
    # Snow-retention bars are hardware on one planar slope, never roof folds.
    for y in (-10,-8.8):C.beam('front snow rail',(-16.4,y,roofz(y)+.075),(16.4,y,roofz(y)+.075),.055,.075,'roof','roof')
    for x in POSTS:
        for y in (-10.9,-7.35,10.6):
            top=roofz(y)-.34
            base=.88 if y<0 else Z
            if y<0:
                C.box('brick pedestal mortar',(x,y,Z+.35),(.75,.75,.70),'stone','structure')
                for k in range(9):
                    zz=Z+.01+k*.075
                    for axis in (0,1):
                        for side in (-1,1):
                            for offset in (-.25,0,.25):
                                p=(x+offset,y+side*.382,zz+.033) if axis==0 else (x+side*.382,y+offset,zz+.033)
                                size=(.235,.028,.065) if axis==0 else (.028,.235,.065)
                                x0,y0,z0=p;a,b,c=[s/2 for s in size]
                                BRICKS.append([(x0-a,y0-b,z0-c),(x0+a,y0-b,z0-c),(x0+a,y0+b,z0-c),(x0-a,y0+b,z0-c),(x0-a,y0-b,z0+c),(x0+a,y0-b,z0+c),(x0+a,y0+b,z0+c),(x0-a,y0+b,z0+c)])
                C.box('pedestal seated cap',(x,y,.86),(.84,.84,.09),'stone','structure')
            C.box('glulam seated column',(x,y,(base+top)/2),(.28,.30,top-base),'timber','structure')
            for direction in (-1,1):
                if abs(x+direction*1.0)>16:continue
                C.beam('column knee brace',(x,y,top-.85),(x+direction*1.0,y,top-.08),.15,.20,'timber','structure')
        for ya,yb in [(-11.18,0),(0,11.0)]:
            C.beam('glulam roof rafter',(x,ya,roofz(ya)-.31),(x,yb,roofz(yb)-.31),.24,.30,'timber','structure')
    for y in (-10.9,-7.35,10.6):
        C.box('long seated timber header',(0,y,roofz(y)-.35),(32,.30,.28),'timber','structure')
    for x in (-15.95,15.95):
        C.rod('rainwater pipe',(x,-11.42,.16),(x,-11.42,4.70),.05,'roof','structure')

def build():
    P.OBS.clear();BRICKS.clear();board_uvs()
    C.box('earth plot',(0,0,.0125),(46,40,.025),'soil','site',0)
    C.box('park grass behind path',(0,2,.0325),(46,36,.015),'grass','site',0)
    C.box('park grass before path',(0,-19.2,.0325),(46,1.6,.015),'grass','site',0)
    mirror=C.MATS['mirror'].node_tree.nodes['Principled BSDF']
    mirror.inputs['Metallic'].default_value=1;mirror.inputs['Roughness'].default_value=.12
    C.box('enclosed occupied slab',(0,1.75,.08),(32,18.5,.12),'floor','floors',0)
    C.box('open veranda slab',(0,-9.25,.08),(32,3.5,.12),'paving','site',0)
    front=C.Face((0,-7.5,0),(1,0,0),(0,1,0),'park glazed front')
    holes=[P.h('public double entrance',-12.5,Z,2.0,3.15,True),P.h('secondary double exit',12.5,Z,1.8,3.15,True)]
    for name,x,w in [('left entry sidelight',-14.65,.85),('entry right sidelight',-10.37,1.45),('hall bay1',-6.24,5.35),('hall bay2',0,5.40),('hall bay3',6.24,5.35),('exit left sidelight',10.45,1.30),('exit right sidelight',14.55,.85)]:holes.append(P.h(name,x,.20,w,4.25))
    holes += [P.h('entry transom',-12.5,3.52,2.0,.93),P.h('exit transom',12.5,3.52,1.8,.93)]
    outside(front,-16,16,holes,front=True)
    left=C.Face((-16,0,0),(0,1,0),(1,0,0),'left cedar gable')
    outside(left,-7.2,11,[P.h('left narrow '+str(i),y,.8,.8,2.1) for i,y in enumerate((-4,0,4,7.5))],True)
    right=C.Face((16,0,0),(0,1,0),(-1,0,0),'right cedar gable')
    outside(right,-7.2,11,[P.h('right three source windows '+str(i),y,.8,.8,2.1) for i,y in enumerate((-3.8,.5,4.8))],True)
    rear=C.Face((0,11,0),(1,0,0),(0,-1,0),'rear cedar elevation')
    outside(rear,-15.7,15.7,[P.h('rear washroom window',-12.6,2.0,2.0,1.1),P.h('rear hall light1',-6,1.0,3.0,2.7),P.h('rear hall light2',6.24,1.0,4.8,2.7),P.h('rear double exit',12.5,Z,1.8,3.15,True)])
    # Service body closes to the real sloped lining above its flat room ceilings.
    partition(C.Face((-8,0,0),(0,1,0),(1,0,0),'hall service spine'),-2,10.7)
    for ya,yb in [(-2,0),(0,10.7)]:
        C.prism('closed upper service spine',[(ya,3.8),(yb,3.8),(yb,roofz(yb)-.17),(ya,roofz(ya)-.17)],'x',-8,-7.85,'interior')
    corridor=C.Face((-9.8,0,0),(0,1,0),(-1,0,0),'service corridor rooms')
    partition(corridor,-2,10.7,[P.h(name,y,Z,1.25,2.35,True) for name,y in [('kitchen door',0),('meeting A door',3.8),('meeting B door',7.3),('washroom door',9.8)]])
    for y in (-2,2,5.7,9):partition(C.Face((0,y,0),(1,0,0),(0,1,0),'service crosswall '+str(y)),-15.7,-9.95)
    C.box('service ceiling',(-11.825,4.5,3.84),(7.75,13,.08),'ceiling','ceiling',0)
    roof()
    brick_mesh()
    for x in (-3,3,9):
        for y in (-3.5,1.5,6.5):H.table(x,y)
    H.table(-12.8,3.8,2.1,.85);H.table(-12.8,7.3,2.1,.85)
    C.box('commons reception counter',(-14.5,-3.0,Z+.46),(1.8,.75,.92),'timber','furniture')
    C.box('commons notice board',(-15.6675,-6.0,1.9),(.065,1.60,1.15),'timber','furniture')
    for y in (-6.5,-6.0,-5.5):C.box('notice sheet',(-15.629,y,1.9),(.012,.40,.75),'ceiling','decor')
    C.box('community artwork backing',(.8,10.665,2.25),(3.4,.07,1.35),'timber','furniture')
    for x in (-.4,.4,1.2,2.0):C.box('community art panel',(x,10.6175,2.25),(.66,.025,1.1),'furniture','decor')
    for y in (5.7,9):C.box('meeting wall board',(-13,y-.035,1.9),(2.0,.07,.85),'ceiling','furniture')
    L.basin(-14.0,1.36)
    C.box('community range',(-11.95,1.37,Z+.45),(1.05,.80,.90),'hardware','furniture')
    C.box('oven door',(-11.95,.951,Z+.46),(.83,.03,.54),'trim','furniture')
    for x in (-12.2,-11.7):
        for y in (1.15,1.60):C.rod('hob ring',(x,y,Z+.90),(x,y,Z+.93),.11,'trim','furniture')
    C.box('seated extractor',(-11.95,1.44,2.25),(1.17,.75,.22),'hardware','furniture')
    C.box('extractor ceiling duct',(-11.95,1.66,3.05),(.35,.26,1.5),'hardware','furniture')
    C.box('kitchen fridge',(-15.1,-1.1,Z+1),(.95,1.0,2.0),'ceiling','furniture')
    C.box('prep island',(-13.35,-.50,Z+.44),(1.5,.75,.88),'timber','furniture')
    C.box('prep island worktop',(-13.35,-.50,Z+.92),(1.58,.83,.08),'stone','furniture')
    L.basin(-14.4,10.345);L.toilet(-11.5,10.35)
    C.box('washroom mirror',(-14.4,10.685,1.90),(1.3,.03,.70),'mirror','furniture')
    C.rod('WC grab rail',(-12.2,9.85,Z+.78),(-12.2,10.65,Z+.78),.03,'hardware','furniture')
    for y in (9.85,10.65):C.rod('WC grab support',(-12.2,y,Z),(-12.2,y,Z+.78),.025,'hardware','furniture')
    C.box('mobile table rack',(13.8,9.2,Z+.18),(2.2,.9,.14),'hardware','furniture')
    # Four grounded casters overlap the base; folded tables remain seated on it.
    for x in (12.95,14.65):
        for y in (8.88,9.52):
            C.rod('rack grounded caster',(x-.035,y,Z+.075),(x+.035,y,Z+.075),.075,'trim','furniture')
    for y in (8.95,9.15,9.35):C.box('folded event table',(13.8,y,Z+1.0),(1.9,.06,1.50),'timber','furniture')
    for x in (-3,3,9):
        for y in (-3.5,1.5,6.5):
            R.lamp(x,y,3.85,.8);C.rod('hall pendant support',(x,y,3.87),(x,y,roofz(y)-.17),.014,'hardware','structure')
            C.qa_room_light('hall',(x,y,3.65),270,2.5)
    for x,y in [(-12,-4.7),(-12.8,0),(-12.8,3.8),(-12.8,7.3),(-13,9.6)]:
        R.lamp(x,y,3.65,.70);C.rod('service light support',(x,y,3.67),(x,y,roofz(y)-.17 if y< -2 else 3.80),.014,'hardware','structure');C.qa_room_light('service',(x,y,3.45),190,2.0)
    C.box('public park sidewalk',(0,-17.2,.02),(46,2.4,.04),'paving','site',0)
    C.box('front veranda path',(0,-12.65,.08),(34.5,3.3,.12),'paving','site',0)
    C.box('bicycle paved pad',(-19,-12.65,.08),(5,3.3,.12),'paving','site',0)
    C.box('main approach plateau',(-12.5,-13.95,.08),(3.0,1.5,.12),'paving','site',0)
    C.prism('public entry ramp',[(-16,.0),(-16,.04),(-14.7,Z),(-14.7,0)],'x',-14,-11,'paving','site')
    C.box('east side route',(17.25,0,.08),(2.5,25.6,.12),'paving','site',0)
    C.box('rear route',(0,12.5,.08),(37,3.0,.12),'paving','site',0)
    C.box('east bench pad',(19,4,.08),(2.2,3.0,.12),'paving','site',0)
    B.bench(19,4)
    for x in (-17.5,-18.8,-20.1):B.bikehoop(x,-13.0)
    for x in (-6,1,7):R.plantbed(x,-15.05,4.2,1.1)
    R.plantbed(-18.3,-6.0,2.0,5.0);R.plantbed(19.6,-7.2,2.0,3.0)
    for x,y,seed in [(-20,8,801),(-20,-8,802),(20,10,803),(20,-10,804)]:R.tree(x,y,seed)
    for obj in bpy.context.scene.objects:
        if obj.type=='LIGHT':obj.visible_camera=False;obj.visible_glossy=False;obj.visible_transmission=False;obj.data.specular_factor=0;obj.data.transmission_factor=0

def network():
    triangles=[];routes=[];obs=P.OBS
    def rect(a,b,c,d,z=Z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];triangles.extend([[p,q,r],[p,r,s]])
    rect(-15.7,-7.2,15.7,10.7)
    rect(-16,-14.30,16,-7.2)
    rect(-14,-14.7,-11,-13.2)
    rect(-23,-18.4,23,-16,.04)
    rect(16,-14.3,17.25,-12.8);rect(16,-12.8,18.5,12.8);rect(-18.5,11,18.5,14)
    rect(18.5,2.5,20.1,5.5)
    rect(-21,-14.3,-16,-11)
    # Real slab strips through carrier thickness at each exterior portal.
    for x,y in [(-12.5,-7.5),(12.5,-7.5),(12.5,11)]:rect(x-.9,y-.35,x+.9,y+.35)
    a=[-14,-16,.04];b=[-11,-16,.04];c=[-11,-14.7,Z];d=[-14,-14.7,Z];triangles.extend([[a,b,c],[a,c,d]])
    def route(name,xy):routes.append(dict(name=name,points=[[x,y,Z] for x,y in xy]))
    routes.append(dict(name='Public path to entrance',points=[[-12.5,-17.2,.04],[-12.5,-16,.04],[-12.5,-14.7,Z],[-12.5,-12.6,Z],[-12.5,-6.5,Z]]))
    route('Commons to hall',[(-12.5,-6.5),(-12.5,-4.7),(-6,-4.7)])
    route('Reception approach',[(-12.5,-4.7),(-13.1,-4.7),(-13.1,-3.0)])
    route('Commons notice board',[(-12.5,-4.7),(-14.8,-4.7),(-14.8,-6.0)])
    route('Service corridor',[(-12.5,-4.7),(-9,-4.7),(-9,10.1)])
    for name,y in [('Kitchen',0),('Meeting A',3.8),('Meeting B',7.3),('Washroom',9.8)]:route(name+' door',[(-9,-4.7),(-9,y),(-10.8,y)])
    route('Kitchen sink',[(-10.8,0),(-11.0,.40),(-14,.40),(-14,.55)])
    route('Kitchen preparation',[(-10.8,0),(-12.25,0),(-12.25,-1.1)])
    route('WC basin',[(-10.8,9.8),(-12.4,9.5),(-14.4,9.5)])
    route('Hall clear west aisle',[(-6,-4.7),(-6,9.2)])
    for y in (-3.5,1.5,6.5):route('Hall seating row '+str(y),[(-6,y-1.8),(11.7,y-1.8),(11.7,y)])
    route('Community art',[(-6,9.2),(.8,9.2),(.8,9.7)])
    route('Event storage',[(11.7,6.5),(11.7,9.2),(12.4,9.2)])
    route('Secondary park exit',[(11.7,-4.7),(12.5,-4.7),(12.5,-12.65)])
    route('Rear exit',[(11.7,6.5),(11.7,10.1),(12.5,10.1),(12.5,12.5)])
    route('Veranda threshold',[(-12.5,-12.65),(12.5,-12.65)])
    route('Bicycle approach',[(-12.5,-12.65),(-12.5,-11.6),(-17.5,-11.6)])
    route('Park bench',[(-12.5,-12.65),(17.25,-12.65),(17.25,2.8),(19,2.8),(19,3.15)])
    for obj in C.objects():
        mod=obj.get('cityprompt_lego_module','');role=obj.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'open leaf' in obj.name or obj.name.startswith(('bike rack','young tree trunk','branch'))
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in obj.name for s in ('ceiling','luminaire','diffuser','rafter','pendant','knee brace','header','rainwater')):eligible=False
        if eligible:
            low,high=C.bounds([obj]);obs.append([low[0],high[0],low[1],high[1],low[2],high[2]])
    probes=[dict(name='Park bench',point=[19,4,Z])]+[dict(name='Bicycle '+str(i),point=[x,-13,Z]) for i,x in enumerate((-17.5,-18.8,-20.1))]
    return dict(version=2,footprint=[46,40],entrance=[-12.5,-17.2,.04],maxStepM=.18,triangles=triangles,obstacles=obs,portals=[[-14,-11,-18.4,-14.7]],routes=routes,gardenExclusionProbes=probes)

def cameras():
    cams=[]
    for name,loc in [('front',(0,-64,11)),('front_corner',(44,-49,27)),('aerial',(40,-40,55)),('left_side',(-62,0,13)),('right_side',(62,0,13)),('rear',(0,59,14)),('rear_side',(-40,38,26))]:cams.append(dict(name=name,location=loc,target=(0,0,3.5),whole=True,lens=52))
    for name,loc,target,lens in [
        ('facade_close',(-19,-25,6),(-9,-7.5,2.8),32),('architecture_close',(11,-24,5),(12.5,-8.5,2),30),('glass_close',(0,-10,1.9),(3,-3.5,1.2),30),
        ('roof_contact',(25,-25,19),(9,-7,5.8),35),('roof_rear_contact',(26,21,17),(15,6,5.8),35),('single_ridge',(24,0,16),(3,0,7.4),35),
        ('veranda_frame',(-14,-12,2.0),(-9.36,-10.9,4.6),25),('pedestal_contact',(-5,-13,1.7),(-3.12,-10.9,.9),35),('veranda_soffit',(-7,-10.0,2.0),(7,-8.3,5.6),24),
        ('public_approach',(-10,-19,1.5),(-12.5,-14,.14),26),('entrance_double',(-12.5,-11.0,1.8),(-12.5,-7.5,1.8),25),
        ('program_interior',(-6.0,-6.4,1.8),(5,1.5,1.1),22),('hall_rear',(12,9.8,1.8),(2,-1,1.2),23),('hall_frames',(12,4.5,2.0),(3.12,0,6.5),23),
        ('commons',(-9,-6.5,1.8),(-14.4,-3.5,1.2),23),('commons_notice',(-14,-5.0,1.8),(-15.66,-6,1.9),30),('service_corridor',(-9,-1.7,1.8),(-9,8,1.4),20),('kitchen',(-10.6,-1.5,1.8),(-13.5,.8,1.0),22),('kitchen_sink',(-13.3,.20,1.8),(-14,1.36,.98),28),
        ('meeting_A',(-10.6,2.6,1.8),(-13,3.9,1.1),22),('meeting_B',(-10.6,6.2,1.8),(-13,7.3,1.1),22),('washroom',(-10.4,9.5,1.8),(-13,10.3,.9),20),('washroom_sink',(-13.1,9.35,1.8),(-14.4,10.35,1.0),28),('washroom_toilet',(-12.6,9.3,1.7),(-11.5,10.35,.8),27),
        ('event_storage',(11,8.2,1.8),(13.8,9.2,1.1),28),('community_art',(2.5,8.5,1.8),(.8,10.65,2.2),30),('rear_exit',(12.5,8.8,1.8),(12.5,11,1.4),26),
        ('cedar_board_mapping',(21,-3,4),(16,.7,2.5),40),('bicycle_threshold',(-23,-19,5),(-17,-12,1),30),('park_bench',(24,0,5),(19,4,.8),28),('landscape_approach',(10,-22,5),(2,-14.5,.7),30)]:cams.append(dict(name=name,location=loc,target=target,whole=False,lens=lens))
    return cams

if __name__=='__main__':D.run(__file__,'hall-park-prework.json','hall-park',PALETTE,cameras,build,network,'hall-park-cedar-v002.png',[.96,2.4],extra_scripts=[P.__file__,L.__file__,H.__file__])
