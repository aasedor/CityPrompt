"""Source-locked U-school; dedicated plan, roof, room and circulation assembly."""
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C, B, R, bpy
import build_corner_fourplex as P  # Cut-carrier/window/open-leaf atoms only.
import build_library_pavilion as L  # Hollow basin/WC and bookshelf atoms only.
import build_prairie_hall as H  # Half-plane mathematics only.
import build_park_hall as K  # Double open glazed leaf atom only.

Z=.14
RISE=3.8
CORE_X=(-9.7,9.7)
STAIR_Y=-14.2
PALETTE=dict(B.PALETTE,wall=(.66,.54,.38),buff=(.42,.23,.16),
 timber=(.58,.41,.24),stone=(.61,.58,.51),roof=(.38,.42,.43),
 trim=(.085,.095,.09),interior=(.80,.79,.71),floor=(.57,.50,.40),
 furniture=(.28,.37,.32),panel=(.40,.46,.39),ceiling=(.86,.84,.77),lamp=(.98,.88,.70),
 grass=(.29,.38,.18),leaf=(.23,.34,.14),flower=(.67,.60,.42),mirror=(.8,.82,.83))

def room_bounds(index):
    lo=-19.7 if index==0 else -20+index*40/3+.07
    hi=19.7 if index==2 else -20+(index+1)*40/3-.07
    return lo,hi

def cameras():
    cams=[]
    for name,loc in [('front',(0,-100,14)),('front_corner',(88,-91,39)),
                     ('aerial',(74,-65,104)),('left_side',(-112,0,30)),
                     ('right_side',(112,0,30)),('rear',(0,108,32)),
                     ('rear_side',(-85,85,54))]:
        cams.append(dict(name=name,location=loc,target=(0,0,4),whole=True,lens=52))
    def add(n,loc,target,lens=25):
        cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    add('facade_close',(13,-36,7),(-2,-20,4.8),30)
    add('architecture_close',(7,-32,5),(0,-21,2.3),26)
    add('glass_close',(-9,-24,2),(-8,-17.8,1.7),30)
    for sign in (-1,1):
        side='left' if sign<0 else 'right'
        add('roof_valley_'+side,(sign*13,-16,16),(sign*16,-14,9),32)
        add('roof_valley_end_'+side,(sign*8,-4,11),(sign*11.5,-7.5,7.9),30)
        add('gable_contact_'+side,(sign*26,25,12),(sign*20,20,8.5),30)
        add('canopy_post_'+side,(sign*5.5,11.5,1.8),(sign*9.72,13,1.35),24)
        add('canopy_corner_'+side,(sign*7,-1,5),(sign*10,-6,3.2),26)
    add('roof_connector_ridge',(0,-11,16),(0,-14,9.6),30)
    add('cedar_brick_contact',(21,-25,5),(20,-20,3.94),36)
    add('roof_lining_contact',(10,19,7.4),(12,19,7.925),24)
    for level in range(2):
        z=Z+level*RISE
        for sign in (-1,1):
            side='left' if sign<0 else 'right'
            for i in range(3):
                lo,hi=room_bounds(i)
                add(f'classroom_{side}_{i+1}_{level+1}',(sign*17.0,lo+2.8,z+1.75),
                    (sign*21,lo+7.5,z+1.0),20)
            add(f'teaching_wall_{side}_{level+1}',(sign*19.5,-14.5,z+1.75),
                (sign*15.43,-15.2,z+1.6),26)
            add(f'wing_corridor_{side}_{level+1}',(sign*13.7,-5,z+1.65),
                (sign*13.7,15,z+1.5),22)
            label=('staff' if sign<0 else 'meeting') if not level else ('resource' if sign<0 else 'quiet_reading')
            add(label+'_'+str(level+1),(sign*5,-18.7,z+1.65),(sign*9,-17.5,z+1),20)
            add(f'washroom_{side}_{level+1}',(sign*6,-11.1,z+1.65),
                (sign*6,-13.3,z+.9),20)
        add('commons_'+str(level+1),(2.7,-18.4,z+1.7),(-1,-10,z+1.5),22)
        add('front_connection_'+str(level+1),(-10.8,-15.15,z+1.65),(10,-15.15,z+1.5),22)
        add('rear_connection_'+str(level+1),(-10.8,-9.4,z+1.65),(10,-9.4,z+1.5),22)
    for x in CORE_X:
        side='left' if x<0 else 'right'
        sign=-1 if x<0 else 1
        add('stair_'+side,(x+sign*2.8,-15.3,2.0),(x,-11.9,2.2),20)
        add('upper_landing_'+side,(x+sign*2.8,-15.2,5.7),(x,-12.1,3.5),20)
        add('landing_guard_'+side,(x+sign*2.5,-11.3,3.4),(x+sign*1.27,-10.95,2.7),26)
    add('washroom_fixture',(-5.2,-11.8,1.7),(-6.7,-13.7,1),26)
    add('courtyard',(0,23,6),(0,-4,1.8),24)
    add('court_teaching',(6,10,3.0),(3,8,.9),26)
    add('covered_walk',(8,18,1.8),(10.8,-3,1.7),24)
    add('rear_play_lawn',(-16,30,5),(0,23,1),26)
    add('bicycle_shelter',(-13,-30,4),(-20,-25,1),26)
    add('public_ramp',(4,-31,1.2),(0,-28.7,.14),28)
    add('porch_post_contact',(-6,-25,2.0),(-4,-22,1.7),28)
    return cams

# Source-specific materials are bounded face samples. Physical elements own joints.
BRICK_VERTS=[]
BRICK_FACES=[]
BRICK_UV=[]
CEDAR_VERTS=[]
CEDAR_FACES=[]
CEDAR_UV=[]
SKIN=True
BRICK_BEDS=[(48,49),(98,100),(150,152),(200,203),(251,253),(302,304),
            (353,356),(405,407),(456,459),(508,510),(558,561),(611,612),
            (661,663),(714,715),(765,766),(815,817),(866,868),(917,919),
            (969,970),(1020,1021),(1070,1072),(1121,1123),(1171,1173)]

def clipped_cells(a,b,low,top,holes,extra_edges=()):
    edges={a,b}
    for edge in extra_edges:
        if a<edge<b:edges.add(edge)
    for hole in holes:
        for edge in (hole['u']-hole['w']/2,hole['u']+hole['w']/2):
            if a<edge<b:edges.add(edge)
    points=sorted(edges)
    for left,right in zip(points,points[1:]):
        bands=[(low,max(top(left),top(right)))]
        for hole in holes:
            if not hole['u']-hole['w']/2<(left+right)/2<hole['u']+hole['w']/2:continue
            output=[]
            for bottom,high in bands:
                z0=hole['z'];z1=z0+hole['h']
                if high<=z0 or bottom>=z1:output.append((bottom,high));continue
                if bottom<z0:output.append((bottom,z0))
                if high>z1:output.append((z1,high))
            bands=output
        for bottom,high in bands:
            if high-bottom>.001:yield left,right,bottom,high

def append_prism(vs,fs,uvs,face,l,r,z0,zl,zr,d0,d1,mapper):
    offset=len(vs)
    corners=[(l,z0),(r,z0),(r,zr),(l,zl)]
    vertices=[face.p(u,d,z) for d in (d0,d1) for u,z in corners]
    vs.extend(vertices);uvs.extend(mapper(u,z) for d in (d0,d1) for u,z in corners)
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    fs.extend(tuple(offset+i for i in f) for f in faces)

def skin(face,a,b,z0,top,holes):
    if not SKIN:return
    # 120mm pitch=116mm face +4mm actual recess. Fragment UVs inherit parent.
    count=math.ceil((b-a)/.12)
    for j in range(count):
        parent=a+j*.12;left=parent+.002;right=min(b,parent+.12)-.002
        if right<=left:continue
        parent_end=min(b,parent+.12)
        ridges=[u for u in (-19,19) if parent<u<parent_end and top(u)>max(top(parent),top(parent_end))+1e-8]
        full_top=max(top(parent),top(parent_end),*[top(u) for u in ridges])
        full_height=full_top-z0
        if full_height<=.001:continue
        def uv(u,z):
            return ((j%8+.065+.87*(u-parent)/.12)/8*.96/2.4,
                    max(.008,min(.992,(z-z0)/full_height)))
        for l,r,lo,hi in clipped_cells(left,right,z0,top,holes,ridges):
            append_prism(CEDAR_VERTS,CEDAR_FACES,CEDAR_UV,face,l,r,lo,
                         min(hi,top(l)),min(hi,top(r)),-.024,.005,uv)

def brick_skin(face,a,b,holes):
    if not SKIN:return
    for course in range(math.ceil(3.94/.075)):
        low=course*.075+.005;high=min(3.94,(course+1)*.075-.005)
        if high<=low:continue
        start=a-(.12 if course%2 else 0)
        row=1+course%22  # Exclude both cropped exterior image courses.
        for j in range(math.ceil((b-start)/.24)):
            origin=start+j*.24
            left=max(a,origin+.005);right=min(b,origin+.235)
            if right<=left:continue
            # Avoid half faces and all outer image edges; geometry owns mortar.
            column=1+(j%6)
            sample_left=(column+(0.5 if row%2 else 0))*1295/8+8
            sample_right=sample_left+1295/8-16
            sample_top=BRICK_BEDS[row-1][1]+5
            sample_bottom=BRICK_BEDS[row][0]-5
            def uv(u,z):
                f=max(0,min(1,(u-origin-.005)/.23))
                g=max(0,min(1,(z-low)/.065))
                return ((sample_left+(sample_right-sample_left)*f)/1295,
                        1-(sample_bottom-(sample_bottom-sample_top)*g)/1214)
            for l,r,lo,hi in clipped_cells(left,right,low,lambda u:high,holes):
                append_prism(BRICK_VERTS,BRICK_FACES,BRICK_UV,face,l,r,lo,hi,hi,-.012,.299,uv)

def material_meshes():
    for name,vs,fs,coords,role in [('physical source brick courses',BRICK_VERTS,BRICK_FACES,BRICK_UV,'buff'),
                                 ('physical source cedar boards',CEDAR_VERTS,CEDAR_FACES,CEDAR_UV,'wall')]:
        if not vs:continue
        obj=C.mesh(name,vs,fs,role,'envelope')
        obj['bounded_source_uv']=True
        uv=obj.data.uv_layers.new(name='Parent element source face intervals')
        for p in obj.data.polygons:
            for li in p.loop_indices:uv.data[li].uv=coords[obj.data.loops[li].vertex_index]
    original=B.uv_all
    def mapped():
        saved={o.name:[tuple(x.uv) for x in o.data.uv_layers.active.data]
               for o in C.objects() if o.get('bounded_source_uv')}
        for o in C.objects():
            if o.name in saved:
                for layer in list(o.data.uv_layers):o.data.uv_layers.remove(layer)
        original()
        for o in C.objects():
            if o.name not in saved:continue
            for item,value in zip(o.data.uv_layers.active.data,saved[o.name]):item.uv=value
    B.uv_all=mapped

def outside(face,a,b,holes,top=lambda u:7.925):
    # One complete cut carrier, with two physical material zones.
    P.wall(face,a,b,0,7.925,[h for h in holes if not h.get('door')],'interior',.30)
    owner=next(o for o in reversed(C.objects()) if o.get('rlasm_wall_carrier') and o.name.startswith(face.label))
    del P.OBS[-1]
    doors=sorted([h for h in holes if h.get('door')],key=lambda h:h['u'])
    for h in holes:
        if h.get('door') or h['w']<3:continue
        # Deep source timber head shades are geometry, backed into the carrier.
        face.part(h['id']+' supported timber shade',h['u'],-.11,h['z']+h['h']+.09,
                  h['w']+.32,.44,.12,'timber','openings')
        for side in (-1,1):
            face.part(h['id']+' timber shade bracket',h['u']+side*(h['w']/2-.07),.015,
                      h['z']+h['h']+.045,.10,.24,.21,'timber','openings')
    edges=[a]
    for h in doors:
        face.cut(owner,h['id']+' full carrier cut',h['u'],h['z'],h['w'],h['h'],.30)
        if h.get('double'):K.double_door(face,h)
        else:
            u,z,w,ht=h['u'],h['z'],h['w'],h['h']
            for s in (-1,1):face.part(h['id']+' jamb',u+s*(w/2-.035),.15,z+ht/2,.07,.16,ht,'trim')
            face.part(h['id']+' lintel',u,.15,z+ht-.035,w,.16,.07,'trim')
            leaf=C.Face(face.p(u-w/2+.07,-.02,0),tuple(-n for n in face.n),face.t,h['id']+' open leaf')
            leaf.window(h['id']+' open leaf',(w-.14)/2,z,w-.14,ht-.04,1,1,'trim',.035,sill=False,depth=.10)
        edges.extend([h['u']-h['w']/2,h['u']+h['w']/2])
    edges.append(b)
    for l,r in zip(edges[::2],edges[1::2]):
        ps=[face.p(u,d,0) for u in (l,r) for d in (0,.30)]
        P.OBS.append([min(p[0] for p in ps),max(p[0] for p in ps),
                      min(p[1] for p in ps),max(p[1] for p in ps),0,7.925])
    # Gable/end infill uses the active roof profile; no other volume hides holes.
    breaks={a,b}
    for ridge in (-19,19):
        if a<ridge<b:breaks.add(ridge)
    pts=sorted(breaks)
    for l,r in zip(pts,pts[1:]):
        if max(top(l),top(r))<=7.926:continue
        face.panel(face.label+' closed roof infill',[(l,7.925),(r,7.925),(r,top(r)),(l,top(l))],0,.30,'interior')
    brick_skin(face,a,b,holes)
    skin(face,a,b,3.94,top,holes)

def wingz(sign,x):return 9.9-(1.8/7)*abs(x-sign*19)
def connectorz(y):return 9.6-.25*abs(y+14)

def roof_patches(domains,volume_height):
    planes=[d[0] for d in domains]
    lines=[]
    for plane,poly,kind in domains:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            lines.append((q[1]-p[1],p[0]-q[0],q[0]*p[1]-p[0]*q[1]))
    patches=[]
    for plane,poly,kind in domains:
        parts=[poly]
        boundaries=lines+[tuple(a-b for a,b in zip(plane,other)) for other in planes if other!=plane]
        unique={tuple(round(v,10) for v in line) for line in boundaries}
        for line in sorted(unique):
            if abs(line[0])+abs(line[1])<1e-9:continue
            pieces=[]
            for p in parts:
                for sign in (True,False):
                    q=H.clip(p,line,sign)
                    if len(q)>=3 and H.area(q)>1e-7:pieces.append(q)
            parts=pieces
        for p in parts:
            x=sum(q[0] for q in p)/len(p);y=sum(q[1] for q in p)/len(p)
            if abs(H.value(plane,x,y)-volume_height(x,y))<1e-6:patches.append((p,plane,kind))
    return patches

def roof():
    slope=1.8/7;domains=[];end=20.5657142857143
    for sign in (-1,1):
        a,b=(-26.55,-11.45) if sign<0 else (11.45,26.55)
        ridge=sign*19
        domains.extend([((slope,0,9.9-slope*ridge),[(a,-end),(ridge,-end),(ridge,end),(a,end)],'wing'),
                        ((-slope,0,9.9+slope*ridge),[(ridge,-end),(b,-end),(b,end),(ridge,end)],'wing')])
    domains.extend([((0,.25,13.1),[(-19,-end),(19,-end),(19,-14),(-19,-14)],'connector'),
                    ((0,-.25,6.1),[(-19,-14),(19,-14),(19,-7.4342857142857),(-19,-7.4342857142857)],'connector')])
    def height(x,y):
        values=[-999]
        for sign in (-1,1):
            if 11.45<=sign*x<=26.55 and -end<=y<=end:values.append(wingz(sign,x))
        if -19<=x<=19 and -end<=y<=-7.4342857142857:values.append(connectorz(y))
        return max(values)
    patches=roof_patches(domains,height)
    for poly,plane,kind in patches:
        top=[(x,y,H.value(plane,x,y)) for x,y in poly]
        C.solid_surface(kind+' active metal roof',top,.12)
        C.solid_surface(kind+' seated roof lining',[(x,y,z-.12) for x,y,z in top],.055,'timber','roof')
        axis=1 if kind=='wing' else 0
        for i in range(-59,60):
            value=i*.45;hits=[]
            for p,q in zip(poly,poly[1:]+poly[:1]):
                a,b=p[axis],q[axis]
                if (a<=value<b) or (b<=value<a):
                    t=(value-a)/(b-a);hits.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if len(hits)==2:
                a,b=hits
                if math.dist(a,b)>.02:C.beam('clipped standing seam',(*a,H.value(plane,*a)+.02),(*b,H.value(plane,*b)+.02),.018,.024,'roof','roof')
    for sign in (-1,1):
        C.rod('wing continuous ridge',(sign*19,-end,9.93),(sign*19,end,9.93),.065,'roof','roof')
        node=(sign*17.833333333333,-14,9.6)
        for y in (-end,-7.4342857142857):
            x=sign*11.45
            C.beam('derived continuous valley flashing',(x,y,connectorz(y)+.025),
                   (node[0],node[1],node[2]+.025),.18,.04,'roof','roof')
        for y in (-end,end):
            pairs=[(-26.55,-19),(-19,-11.45)] if sign<0 else [(11.45,19),(19,26.55)]
            for a,b in pairs:
                C.beam('gable seated fascia',(a,y,wingz(sign,a)-.09),(b,y,wingz(sign,b)-.09),.15,.20,'timber','roof')
        outer=sign*26.55;inner=sign*11.45
        for x,y0,y1 in [(outer,-end,end),(inner,-7.4342857142857,end)]:
            C.beam('wing continuous eave gutter',(x,y0,wingz(sign,x)-.075),(x,y1,wingz(sign,x)-.075),.16,.18,'roof','roof')
    C.rod('connector bounded ridge',(-17.833333333333,-14,9.63),(17.833333333333,-14,9.63),.065,'roof','roof')
    for y in (-end,-7.4342857142857):
        C.beam('connector eave gutter',(-11.45,y,connectorz(y)-.075),(11.45,y,connectorz(y)-.075),.16,.18,'roof','roof')
    return patches

def partition(face,a,b,z,holes=()):
    P.wall(face,a,b,z,z+3.60,holes,'interior',.14)

def lamp(x,y,z):
    R.lamp(x,y,z+3.585,.95)
    C.qa_room_light('school programme',(x,y,z+3.35),360,3.0)

def transformed_atoms(fn,x,y,z,angle=0):
    before=set(C.objects());fn(x,y,z)
    co=math.cos(angle);si=math.sin(angle)
    for obj in set(C.objects())-before:
        dx=obj.location.x-x;dy=obj.location.y-y
        # Atomic mesh helpers author world vertices with zero object location.
        for v in obj.data.vertices:
            if obj.name.startswith('chair back') and abs(v.co.z-(z+.47))<.001:v.co.z=z+.43
            dx=v.co.x-x;dy=v.co.y-y
            v.co.x=x+co*dx-si*dy;v.co.y=y+si*dx+co*dy

def classroom(sign,index,z):
    low,high=room_bounds(index)
    angle=math.pi/2 if sign<0 else -math.pi/2
    for j in range(6):
        for i in range(4):transformed_atoms(B.desk,sign*(17.6+j*1.4),low+4.5+i*2,z,angle)
    transformed_atoms(lambda x,y,z:B.desk(x,y,z,False),sign*16.5,high-1.25,z,angle)
    # Whiteboard is on the opaque corridor pier between the door and glass.
    C.box('classroom seated whiteboard',(sign*15.415,low+4.5,z+1.75),(.055,2.0,1.15),'ceiling','furniture')
    C.box('classroom supported board tray',(sign*15.48,low+4.5,z+1.155),(.16,2.0,.04),'trim','furniture')
    for j in range(5):
        x=sign*(19+j*1.25)
        C.box('grounded classroom cubby',(x,high-.43,z+.49),(1.10,.65,.98),'timber','furniture')
        C.box('cubby recessed face',(x,high-.77,z+.50),(.94,.028,.76),'panel','decor')
    for y in (low+4.4,low+9.4):lamp(sign*21,y,z)
    # Reading stool group stays behind the entry aisle and beside front glazing.
    for j in range(3):
        x=sign*(18+j*1.3);y=low+1.0
        C.box('reading stool seat',(x,y,z+.40),(.48,.48,.06),'furniture','furniture')
        for dx in (-.16,.16):
            for dy in (-.16,.16):C.box('reading stool leg',(x+dx,y+dy,z+.185),(.035,.035,.37),'timber','furniture',0)

def support_rooms(level,z):
    for sign in (-1,1):
        lo,hi=(-11.7,-4) if sign<0 else (4,11.7)
        partition(C.Face((sign*4,0,0),(0,1,0),(sign,0,0),'front support room door'),
                  -19.7,-16,z,[P.h('support entry '+str((level,sign)),-17.8,z,1.3,2.4,True)])
        # The outer support partition is inset from the shared open interface.
        partition(C.Face((sign*11.7,0,0),(0,1,0),(-sign,0,0),'front support end'),-19.7,-16,z)
        partition(C.Face((0,-16,0),(1,0,0),(0,-1,0),'front support rear'),lo,hi,z)
        if not level:
            for x in (sign*7,sign*9.5):transformed_atoms(lambda x,y,z:B.desk(x,y,z,False),x,-17.8,z)
        else:
            bookshelf(sign*9.3,-16.50,z,3.6,1.8,axis='x',name='resource books')
            transformed_atoms(lambda x,y,z:B.desk(x,y,z,False),sign*7,-18.5,z)
        lamp(sign*8,-17.8,z)
        # WCs flank central commons; all opaque privacy carriers are real.
        lo,hi=(-7.8,-4.2) if sign<0 else (4.2,7.8)
        for x,inward in ((lo,1),(hi,-1)):
            partition(C.Face((x,0,0),(0,1,0),(inward,0,0),'washroom side'),-14.325,-10.395,z)
        partition(C.Face((0,-14.325,0),(1,0,0),(0,1,0),'washroom front'),lo,hi,z)
        partition(C.Face((0,-10.395,0),(1,0,0),(0,-1,0),'washroom rear door'),lo,hi,z,
                  [P.h('washroom door '+str((level,sign)),sign*6,z,1.25,2.35,True)])
        L.Z=z
        # Fixtures face the room, backed to the actual inner front privacy wall.
        before=set(C.objects());L.basin(sign*6.55,-13.82);L.toilet(sign*5.05,-13.82)
        # Rotate each assembly 180deg: tap/cistern sides meet front wall.
        new=list(set(C.objects())-before)
        for obj in new:
            # Flip Y only (geometry and normals repaired), preserving X locations.
            for v in obj.data.vertices:v.co.y=2*(-13.82)-v.co.y
            C.normalise(obj.data)
        C.box('washroom seated mirror',(sign*6.55,-14.174,z+1.75),(1.35,.028,.75),'mirror','furniture')
        lamp(sign*6,-12.2,z)
    # Commons programme sits outside both connecting crosspassages.
    if level==0:
        C.box('reception supported base',(-2,-12.6,z+.48),(2.5,.72,.96),'timber','furniture')
        C.box('reception counter',(-2,-12.6,z+1.0),(2.6,.80,.08),'stone','furniture')
        B.sofa(2,-12.5,z)
    else:
        bookshelf(-2.8,-12.3,z,2.7,1.5,axis='y',name='upper commons books')
        B.sofa(2,-12.5,z)
    for y in (-17.5,-12.3,-9.3):lamp(0,y,z)

def bookshelf(x,y,z,length,height,axis,name):
    before=set(C.objects());L.Z=z;L.shelf(x,y,length,height,axis=axis,name=name)
    made=set(C.objects())-before
    tops=[C.bounds([o])[1][2] for o in made if o.name.startswith(name+' shelf')]
    for o in made:
        if not o.name.startswith(name+' book'):continue
        lo,hi=C.bounds([o]);support=min(tops,key=lambda t:abs(t-lo[2]))
        for v in o.data.vertices:v.co.z+=support-lo[2]

def stairs():
    for cx in CORE_X:
        before=set(C.objects());R.stair(cx,STAIR_Y,Z,RISE,1.25)
        for obj in list(set(C.objects())-before):
            if obj.name.startswith(('outer stair rail','outer guard post','half landing rear guard')):
                bpy.data.objects.remove(obj,do_unlink=True)
        C.railing('seated half landing rear guard',(cx-1.3125,STAIR_Y+3.65,Z+RISE/2),
                  (cx+1.3125,STAIR_Y+3.65,Z+RISE/2),spacing=.10,bottom=0)
        for side in (-1,1):
            pts=[]
            for j in range(11):
                zz=Z+(j+1)*RISE/22 if side<0 else Z+RISE-j*RISE/22
                pts.append((cx+side*.0625,STAIR_Y-.125+j*.25,zz))
            pts.append((cx+side*.0625,STAIR_Y+2.625,pts[-1][2]))
            for p in pts:C.rod('tread seated inner stair post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
            for a,b in zip(pts,pts[1:]):C.beam('inner stair continuous rail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.04,.04,'trim','stair guard')
            for a,b in zip(pts,pts[1:]):
                p=(a[0],(a[1]+b[1])/2,a[2]);top=(a[2]+b[2])/2+1.02
                C.rod('intermediate inner tread picket',p,(p[0],p[1],top),.016,'trim','stair guard')
            outer=[(cx+side*1.27,p[1]+.02,p[2]) for p in pts[:-1]]
            for p in outer:C.rod('tread seated outer stair post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
            for a,b in zip(outer,outer[1:]):C.beam('outer stair continuous rail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.04,.04,'trim','stair guard')
            foot=(cx+side*1.27,STAIR_Y+2.645,Z+RISE/2)
            end=(cx+side*1.27,STAIR_Y+3.65,Z+RISE/2)
            C.rod('seated landing corner post',foot,(foot[0],foot[1],foot[2]+1.02),.018,'trim','stair guard')
            C.railing('seated landing side guard',foot,end,spacing=.10,bottom=0,end_posts=False)
            last=outer[-1]
            for a,b in zip(outer,outer[1:]+[foot]):
                p=(a[0],(a[1]+b[1])/2,a[2]);top=(a[2]+b[2])/2+1.02
                C.rod('intermediate outer tread picket',p,(p[0],p[1],top),.016,'trim','stair guard')
            C.beam('flight landing rail connection',(last[0],last[1],last[2]+1.02),(foot[0],foot[1],foot[2]+1.02),.04,.04,'trim','stair guard')
            C.beam('side rear rail connection',(end[0],end[1],end[2]+1.02),(cx+side*1.3125,end[1],end[2]+1.02),.04,.04,'trim','stair guard')
        for x in (cx-1.50,cx+1.50):C.railing('upper void side guard',(x,-14.325,Z+RISE),(x,-10.395,Z+RISE),bottom=0)
        C.railing('upper void rear guard',(cx-1.50,-10.395,Z+RISE),(cx+1.50,-10.395,Z+RISE),bottom=0)
        C.railing('upper lower flight lip',(cx-1.50,-14.335,Z+RISE),(cx,-14.335,Z+RISE),bottom=0)

def courtyard_canopy():
    # Three connected shed roofs; one envelope with diagonal corner valleys.
    domains=[((-.34/2.4,0,3.42-12*.34/2.4),[(-12,-8),(-9.6,-8),(-9.6,20),(-12,20)],'left'),
             ((.34/2.4,0,3.42-12*.34/2.4),[(9.6,-8),(12,-8),(12,20),(9.6,20)],'right'),
             ((0,-.34/2.4,3.42-8*.34/2.4),[(-12,-8),(12,-8),(12,-5.6),(-12,-5.6)],'rear')]
    def height(x,y):
        values=[-999]
        if -12<=x<=-9.6 and -8<=y<=20:values.append(3.42-(x+12)*.34/2.4)
        if 9.6<=x<=12 and -8<=y<=20:values.append(3.42-(12-x)*.34/2.4)
        if -12<=x<=12 and -8<=y<=-5.6:values.append(3.42-(y+8)*.34/2.4)
        return max(values)
    for poly,plane,name in roof_patches(domains,height):
        top=[(x,y,H.value(plane,x,y)) for x,y in poly]
        C.solid_surface('court canopy clipped '+name,top,.12)
        C.solid_surface('court canopy lining '+name,[(x,y,z-.12) for x,y,z in top],.055,'timber','roof')
    for sign in (-1,1):
        x=sign*9.72;cap=3.42-(12-9.72)*.34/2.4
        for y in (-3,5,13,19):
            C.box('court grounded post',(x,y,(Z+2.91)/2),(.16,.16,2.91-Z),'timber','structure')
        C.box('court outer header',(x,6,2.985),(.20,28,.20),'timber','structure')
        C.box('court wall ledger',(sign*11.95,6,3.21),(.15,28,.12),'timber','structure')
        C.beam('canopy corner seated valley',(sign*12,-8,3.445),(sign*9.6,-5.6,3.105),.16,.04,'roof','roof')
        for y in (-3,5,13,19):
            C.beam('court seated roof rafter',(sign*11.95,y,3.18),(x,y,cap-.14),.12,.14,'timber','structure')
    for x in (-8,0,8):
        C.box('connector court grounded post',(x,-5.72,(Z+2.91)/2),(.16,.16,2.91-Z),'timber','structure')
    C.box('connector court outer header',(0,-5.72,2.985),(19.44,.20,.20),'timber','structure')
    C.box('connector court wall ledger',(0,-7.95,3.21),(24,.15,.12),'timber','structure')
    for x in (-8,0,8):C.beam('court rear seated rafter',(x,-7.95,3.18),(x,-5.72,2.957),.12,.14,'timber','structure')

def build():
    P.OBS.clear();BRICK_VERTS.clear();BRICK_FACES.clear();BRICK_UV.clear()
    CEDAR_VERTS.clear();CEDAR_FACES.clear();CEDAR_UV.clear()
    if SKIN:
        args=sys.argv[sys.argv.index('--')+1:]
        root=Path(args[args.index('--output-root')+1]);version=args[args.index('--version')+1] if '--version' in args else 'v001'
        out=root/('school-timber-'+version)
        import shutil
        tex=root/'materials/school-timber-brick-v001.png';shutil.copy2(tex,out/'textures'/tex.name)
        image=bpy.data.images.load(str(tex));image.pack()
        mat=C.MATS['buff'];mat['source_conditioned']=True;mat['texture_free']=False
        node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.extension='EXTEND'
        mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
        B.write(out/'evidence/secondary-material-authority.json',dict(path='textures/'+tex.name,sha256=C.digest(tex),
                physical_module_m=[.24,.075],mapping='Bounded parent face UVs; physical joints, no raw wrapping'))
    C.MATS['mirror'].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=1
    C.MATS['mirror'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.12
    C.box('earth plot',(0,0,.0125),(68,64,.025),'soil','site',0)
    C.box('landscaped grass',(0,1.25,.0325),(68,61.5,.015),'grass','site',0)
    C.box('public sidewalk',(0,-30.75,.02),(68,2.5,.04),'paving','site',0)
    C.prism('solid public ramp',[(-29.5,0),(-29.5,.04),(-28,.14),(-28,0)],'x',-2,2,'paving','site')
    C.box('entry plateau',(0,-24,.07),(52,8,.14),'paving','site',0)
    for sign in (-1,1):
        C.box('side exterior connection',(sign*28,0,.07),(4,56,.14),'paving','site',0)
        C.box('rear wing exit plateau',(sign*19,21.3,.07),(14,2.6,.14),'paving','site',0)
    C.box('court transverse walk',(0,-6.8,.07),(24,2.4,.14),'paving','site',0)
    for sign in (-1,1):C.box('court longitudinal walk',(sign*10.8,6,.07),(2.4,28,.14),'paving','site',0)
    C.box('court central approach',(0,7.2,.07),(3.2,25.6,.14),'paving','site',0)
    C.box('rear play plateau',(0,23,.07),(24,6,.14),'paving','site',0)
    # Slabs/ceilings meet at x12, never a perimeter wall on that internal seam.
    for level in range(2):
        z=Z+level*RISE
        for sign in (-1,1):
            C.box('occupied wing slab',(sign*19,0,z-.07),(14,40,.14),'floor','floors',0)
            C.box('wing room ceiling',(sign*19,0,z+3.60+.05*level),(14,39.4,.10),'ceiling','ceiling',0)
        slab=C.box('occupied connector slab',(0,-14,z-.07),(24,12,.14),'floor','floors',0)
        ceiling=C.box('connector room ceiling',(0,-14,z+3.60+.05*level),(24,11.4,.10),'ceiling','ceiling',0)
        for cx in CORE_X:
            if level:C.cut_box(slab,'true stair floor void',(cx,-12.36,z),(3,3.93,.70))
            else:C.cut_box(ceiling,'true stair lower ceiling void',(cx,-12.36,z+3.60),(3,3.93,.70))
        front=C.Face((0,-20,0),(1,0,0),(0,1,0),'connector front '+str(level))
        if level:holes=[P.h('front upper group '+str(i),x,z+1.05,6.6,2.15) for i,x in enumerate((-8,0,8))]
        else:
            entry=P.h('main school double entrance',0,z,2.4,2.65,True);entry['double']=True
            holes=[entry]+[P.h('front support group '+str(x),x,z+.75,6.6,2.35) for x in (-8,8)]
            holes += [P.h('main entrance sidelight '+str(x),x,z,1.8,2.65) for x in (-2.3,2.3)]
            holes += [P.h('main entrance transom',0,z+2.72,6.4,.38)]
        # Exterior whole-height walls are emitted once with both levels' cuts.
        if not level:FRONT_HOLES=list(holes)
        else:outside(front,-12,12,FRONT_HOLES+holes)
        rear=C.Face((0,-8,0),(1,0,0),(0,-1,0),'connector court rear '+str(level))
        holes=[P.h('rear connector group '+str((level,x)),x,z+(1.05 if level else .75),4.4,2.15 if level else 2.10) for x in (-8,8)]
        if level:holes.append(P.h('rear connector middle upper',0,z+1.05,6.6,2.15))
        else:
            door=P.h('court double school exit',0,z,2.4,2.40,True);door['double']=True
            holes += [door]+[P.h('court exit sidelight '+str(x),x,z+.15,1.8,2.70) for x in (-2.3,2.3)]
            holes += [P.h('court exit transom',0,2.61,2.4,.38)]
        if not level:REAR_HOLES=list(holes)
        else:outside(rear,-12,12,REAR_HOLES+holes)
        for sign in (-1,1):
            for i in range(3):
                low,high=room_bounds(i)
                door=low+2.3
                partition(C.Face((sign*15.25,0,0),(0,1,0),(sign,0,0),'classroom corridor wall '+str((sign,i,level))),
                          low,high,z,[P.h('classroom door '+str((sign,i,level)),door,z,1.4,2.4,True),
                                     P.h('internal classroom glass '+str((sign,i,level)),low+8.4666666667,z+.85,5,2.3)])
                if i<2:
                    y=-20+(i+1)*40/3-.07
                    a,b=(-25.7,-15.39) if sign<0 else (15.39,25.7)
                    partition(C.Face((0,y,0),(1,0,0),(0,1,0),'classroom crosswall'),a,b,z)
                classroom(sign,i,z)
            for y in (-15,-1,13):lamp(sign*13.7,y,z)
        support_rooms(level,z)
    # Wing envelopes, all exact openings aggregated over both floors.
    for sign in (-1,1):
        a,b=(-26,-12) if sign<0 else (12,26)
        for y in (-20,20):
            holes=[]
            for level in range(2):
                z=Z+level*RISE
                holes.append(P.h('wing end classroom '+str((sign,y,level)),sign*20,z+.95,5.8,2.2))
                if y==20 and not level:holes.append(P.h('rear wing corridor exit '+str(sign),sign*13.9,z,1.4,2.4,True))
                else:holes.append(P.h('wing end corridor '+str((sign,y,level)),sign*13.9,z+.95,1.65,2.2))
            outside(C.Face((0,y,0),(1,0,0),(0,1 if y<0 else -1,0),'wing gable '+str((sign,y))),
                    a,b,holes,lambda u:wingz(sign,u)-.175)
        holes=[]
        for level in range(2):
            z=Z+level*RISE
            for i in range(3):
                low,high=room_bounds(i)
                for dy in (4.3,9.3):holes.append(P.h('outer classroom '+str((sign,level,i,dy)),low+dy,z+.95,3.2,2.2))
        outside(C.Face((sign*26,0,0),(0,1,0),(-sign,0,0),'wing outer '+str(sign)),-19.7,19.7,holes)
        holes=[]
        for level in range(2):
            z=Z+level*RISE
            for y,w in [(-3,6.2),(5,4.8),(14.2,7.0)]:
                holes.append(P.h('court wing group '+str((sign,level,y)),y,z+(1.05 if level else .75),w,2.15 if level else 2.10))
            if not level:holes.append(P.h('wing court door '+str(sign),9.2,z,1.4,2.4,True))
        outside(C.Face((sign*12,0,0),(0,1,0),(sign,0,0),'wing court '+str(sign)),-8,19.7,holes)
    stairs();roof();courtyard_canopy()
    # Front porch: roof, ledger, columns and anchored feet all have load paths.
    for x in (-4,4):
        C.box('front porch foot',(x,-22,.27),(.50,.50,.54),'stone','structure')
        C.box('front seated cedar post',(x,-22,1.945),(.22,.22,3.09),'timber','structure')
    C.box('front porch outer header',(0,-22,3.47),(8.6,.24,.28),'timber','structure')
    C.box('front porch wall ledger',(0,-20.035,3.47),(8.6,.17,.28),'timber','structure')
    C.box('porch supported lining',(0,-21.2,3.63),(8.9,2.8,.12),'timber','roof')
    C.box('porch metal cap',(0,-21.2,3.72),(9,2.9,.06),'roof','roof')
    # Covered bikes on a grounded slab; bench/table atoms translated to .14 floor.
    C.box('bicycle pad',(-20,-25.2,.07),(10,4.8,.14),'paving','site',0)
    for x in (-24,-16):
        for y in (-27,-23.4):C.box('bike seated post',(x,y,1.47),(.14,.14,2.66),'timber','structure')
    C.box('bike shelter header',(-20,-27,2.79),(8.5,.22,.20),'timber','structure')
    C.box('bike rear shelter header',(-20,-23.4,2.79),(8.5,.22,.20),'timber','structure')
    C.box('bike shelter lining',(-20,-25.2,2.925),(8.8,4.4,.12),'timber','roof')
    C.box('bike shelter cap',(-20,-25.2,3.015),(8.9,4.5,.06),'roof','roof')
    def site_atom(fn,x,y,offset=Z):
        before=set(C.objects());fn(x,y)
        for o in set(C.objects())-before:
            for v in o.data.vertices:v.co.z+=offset
    for x in (-23,-21,-19,-17):site_atom(B.bikehoop,x,-25.3,Z-.045)
    for x,y in [(10,-25),(18,-25),(-5,5),(5,16)]:site_atom(B.bench,x,y)
    C.box('left teaching bench union pad',(-5,3.2,.07),(5.4,5.6,.14),'paving','site',0)
    C.box('right teaching table pad',(5,9,.07),(5.4,4.2,.14),'paving','site',0)
    C.box('right court bench pad',(5,16,.07),(3,2,.14),'paving','site',0)
    C.box('right bench path bridge',(2.55,16,.07),(1.9,2,.14),'paving','site',0)
    for x,y in [(-5,2.5),(5,9)]:
        C.box('court table path bridge',(-1.95 if x<0 else 1.95,y,.07),(.7,2.4,.14),'paving','site',0)
        before=set(C.objects());L.Z=Z;L.table(x,y,2.4,1.0)
        for o in set(C.objects())-before:
            if o.name.startswith('reading book'):
                for v in o.data.vertices:v.co.z-=.01
    for x,y,w,d in [(-9,-22.4,6,1.2),(9,-22.4,6,1.2),(19,-21.5,7,1.1),
                    (-6,-2,3.5,3),(6,-2,3.5,3),(-5,13,3,4),(5,3.5,3,3)]:R.plantbed(x,y,w,d)
    for x,y,seed in [(-31,-20,901),(31,-20,902),(-31,23,903),(31,23,904),(-5,24,905),(6,25,906)]:R.tree(x,y,seed)
    for x in (-7,0,7):
        C.box('play balance beam',(x,24,Z+.45),(3.0,.22,.22),'timber','furniture')
        for dx in (-1.1,1.1):C.box('play grounded beam leg',(x+dx,24,Z+.215),(.16,.22,.43),'timber','furniture')
    material_meshes()
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    tris=[];routes=[];obs=list(P.OBS)
    def rect(a,b,c,d,z=Z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    def route(name,xy,z=Z):routes.append(dict(name=name,points=[[x,y,z] for x,y in xy]))
    for level in range(2):
        z=Z+level*RISE
        for sign in (-1,1):
            if sign<0:rect(-25.7,-19.7,-12,19.7,z)
            else:rect(12,-19.7,25.7,19.7,z)
            for i in range(3):
                lo,hi=room_bounds(i);door=lo+2.3
                route(f'{"Left" if sign<0 else "Right"} classroom {i+1} floor {level+1}',
                      [(sign*13.7,-15.1),(sign*13.7,door),(sign*16.4,door),(sign*16.4,lo+4.5)],z)
            route(f'{"Left" if sign<0 else "Right"} wing corridor floor {level+1}',[(0,-9.4),(sign*13.7,-9.4),(sign*13.7,18.5)],z)
            route(f'Front support {sign} floor {level+1}',[(0,-15.1),(0,-17.8),(sign*5.6,-17.8)],z)
            route(f'Washroom {sign} floor {level+1}',[(0,-9.4),(sign*6,-9.4),(sign*6,-12.3)],z)
        # Covered lower core floors cannot compete with the actual stair tops.
        # Physical lower slabs remain; navigation owns only the reachable surface.
        rect(-12,-19.7,12,-14.325,z);rect(-12,-10.395,12,-8.3,z)
        rect(-12,-14.325,-11.2,-10.395,z);rect(-8.2,-14.325,8.2,-10.395,z);rect(11.2,-14.325,12,-10.395,z)
        route('Front cross connection floor '+str(level+1),[(-13.7,-15.1),(13.7,-15.1)],z)
        route('Rear cross connection floor '+str(level+1),[(-13.7,-9.4),(13.7,-9.4)],z)
    for cx in CORE_X:
        for j in range(11):
            rect(cx-1.3125,STAIR_Y-.125+j*.25,cx-.0625,STAIR_Y+.125+j*.25,Z+(j+1)*RISE/22)
            rect(cx+.0625,STAIR_Y-.125+j*.25,cx+1.3125,STAIR_Y+.125+j*.25,Z+RISE-j*RISE/22)
        rect(cx-1.3125,STAIR_Y+2.625,cx+1.3125,STAIR_Y+3.675,Z+RISE/2)
        pts=[[cx-.6875,-14.7,Z],[cx-.6875,-10.95,Z+RISE/2],
             [cx+.6875,-10.95,Z+RISE/2],[cx+.6875,-14.7,Z+RISE]]
        routes += [dict(name=f'Stair {cx} ascent',points=pts),dict(name=f'Stair {cx} descent',points=list(reversed(pts)))]
    rect(-26,-28,26,-20);rect(-2,-29.7,2,-29.5,.04)
    a=[-2,-29.5,.04];b=[2,-29.5,.04];c=[2,-28,Z];d=[-2,-28,Z];tris.extend([[a,b,c],[a,c,d]])
    rect(-3.2,-20.3,3.2,-19.7);rect(-12,-8.3,12,-5.6)
    for sign in (-1,1):
        a,b=(-12,-9.6) if sign<0 else (9.6,12)
        rect(a,-8,b,20);rect(sign*19-7,20,sign*19+7,22.6)
        a,b=(-30,-26) if sign<0 else (26,30);rect(a,-28,b,28)
        route('Courtyard wing exit '+str(sign),[(sign*13.7,9.2),(sign*10.8,9.2),(sign*10.8,18)])
        route('Rear wing exit '+str(sign),[(sign*13.7,18),(sign*13.9,18),(sign*13.9,21.65),(sign*10.8,21.65)])
        rect(sign*13.9-.7,19.7,sign*13.9+.7,20)
    rect(-1.6,-5.6,1.6,26);rect(-12,20,12,26)
    rect(-7.7,.4,-2.3,6);rect(2.3,6.9,7.7,11.1);rect(3.5,15,6.5,17);rect(1.6,15,3.5,17)
    rect(-2.3,1.3,-1.6,3.7);rect(1.6,7.8,2.3,10.2)
    routes.append(dict(name='Public school entrance',points=[[0,-29.7,.04],[0,-29.5,.04],[0,-28,Z],[0,-23,Z],[0,-18,Z],[0,-9.4,Z]]))
    route('School to court and play lawn',[(0,-9.4),(0,-6.8),(.6,-6.8),(.6,-5),(0,-5),(0,21),(2,21)])
    route('Covered U walk',[(-10.3,18),(-10.3,-6.35),(10.3,-6.35),(10.3,18)])
    route('Reception',[(0,-9.4),(0,-12.6),(-.35,-12.6)])
    route('Bicycle shelter',[(0,-26),(-20,-26),(-20,-25.3)])
    route('Front bench',[(0,-26),(10,-26),(10,-25.85)])
    route('Outdoor teaching',[ (0,9),(2.8,9),(2.8,7.5),(5,7.5)])
    route('Right courtyard bench',[(0,16),(2.6,16),(2.6,15.2),(5,15.2)])
    route('Left courtyard bench',[(0,2.5),(-2.6,2.5),(-2.6,4.2),(-5,4.2)])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'guard' in mod or 'flight lip' in o.name or 'open leaf' in o.name or o.name.startswith(('bike rack','young tree trunk','branch'))
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in o.name for s in ('ceiling','luminaire','diffuser','header','ledger','rafter','canopy','hanger','lining','cap')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    garden=[dict(name='bike hoop '+str(x),point=[x,-25.3,Z]) for x in (-23,-21,-19,-17)]
    garden += [dict(name='front bench',point=[10,-25,Z]),dict(name='outdoor table',point=[5,9,Z]),dict(name='court bench',point=[5,16,Z]),dict(name='play beam',point=[0,24,Z]),dict(name='rear tree',point=[6,25,Z])]
    guards=[dict(name=f'Stair {x} landing {side} guard',point=[x+side*1.30,-10.95,Z+RISE/2]) for x in CORE_X for side in (-1,1)]
    guards += [dict(name=f'Stair {x} upper lip',point=[x-.75,-14.335,Z+RISE]) for x in CORE_X]
    return dict(version=2,footprint=[68,64],entrance=[0,-29.7,.04],maxStepM=.18,
                triangles=tris,obstacles=obs,portals=[[-2,2,-30,-29.5]],routes=routes,
                gardenExclusionProbes=garden,circulationExclusionProbes=guards)

if __name__=='__main__':
    D.run(__file__,'school-timber-prework.json','school-timber',PALETTE,cameras,build,network,
          'school-timber-cedar-v001.png',[.96,2.4],extra_scripts=[P.__file__,L.__file__,H.__file__,K.__file__])
