"""One exact Victorian station pilot: physical interior and measured walk surfaces.

Run in Blender. Candidates are immutable and all experiments stay external.
Low-level clay geometry/export helpers are shared with the reviewed library.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import shutil
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'catalogue_duplex_pilot'))
import clay_core as C
spec = importlib.util.spec_from_file_location('station_shared', HERE.parent / 'showcase_building_trio/build.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

PALETTE = dict(B.PALETTE, wall=(.40,.245,.125), stone=(.59,.46,.28),
               roof=(.14,.17,.18), iron=(.24,.085,.047), trim=(.065,.145,.11),
               floor=(.51,.47,.37), walk_floor=(.51,.47,.37), glass=(.47,.54,.51),
               board=(.028,.05,.042), brass=(.55,.37,.12), track=(.12,.14,.135))
TRIANGLES=[]; OBSTACLES=[]
GROUND=.12; GALLERY=5.22

def box(name, p, size, role='wall', module='envelope'):
    return C.box(name,p,size,role,module,0)

def obstacle(x0,x1,y0,y1,z0,z1):
    OBSTACLES.append([x0,x1,y0,y1,z0,z1])

def wall_obstacle(face,u0,u1,bottom,top):
    points=[face.p(u,d,z) for u in (u0,u1) for d in (0,.42) for z in (bottom,top)]
    obstacle(min(p[0] for p in points),max(p[0] for p in points),min(p[1] for p in points),max(p[1] for p in points),bottom,top)

def floor(name,x0,x1,y0,y1,z,thickness=.12):
    """Same triangles drive the visible slab and walking, with Z in metres."""
    pts=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]
    C.solid_surface(name,pts,thickness,'walk_floor','circulation')
    TRIANGLES.extend([[list(pts[i]) for i in tri] for tri in [(0,1,2),(0,2,3)]])

def floor_with_holes(name,x0,x1,y0,y1,z,holes):
    xs=sorted({x0,x1,*[x for h in holes for x in h[:2]]})
    ys=sorted({y0,y1,*[y for h in holes for y in h[2:]]})
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            if any(l<(a+b)/2<r and lo<(c+d)/2<hi for l,r,lo,hi in holes):continue
            floor(name,a,b,c,d,z)

def beam(name,a,b,w=.07,d=None,role='iron'):
    return C.beam(name,a,b,w,d,role,'structure')

def arc_points(cx,y,z,r,segments=40,rise=None):
    return [(cx-r*math.cos(i*math.pi/segments),y,z+(rise or r)*math.sin(i*math.pi/segments)) for i in range(segments+1)]

def ribbon(name,inner,outer,depth,role='stone'):
    # Connected ribbon, avoiding independent chord highlights.
    vs=[];fs=[]
    for a,b in zip(inner,outer):vs.extend([a,b,(a[0],a[1]+depth,a[2]),(b[0],b[1]+depth,b[2])])
    for i in range(len(inner)-1):
        n=i*4;m=n+4
        fs.extend([(n,m,m+1,n+1),(n+2,n+3,m+3,m+2),(n,n+2,m+2,m),(n+1,m+1,m+3,n+3)])
    fs.extend([(0,1,3,2),tuple(range(len(vs)-4,len(vs)))])
    return C.mesh(name,vs,fs,role,'arched construction')

def opening(face,u,width,bottom,spring,top,*,door=False,pointed=False):
    r=width/2
    def rise(x, radius=r):
        return math.sqrt(max(0,(2*radius)**2-(abs(x)+radius)**2)) if pointed else math.sqrt(max(0,radius*radius-x*x))
    # The opaque spandrel starts exactly at the curved aperture.
    n=24
    for i in range(n):
        x0=-r+width*i/n;x1=-r+width*(i+1)/n
        z0=spring+rise(x0);z1=spring+rise(x1)
        face.panel('arched brick spandrel',[(u+x0,z0),(u+x1,z1),(u+x1,top),(u+x0,top)],0,.42,'wall')
    pts=[face.p(u-r+2*r*i/n,-.05,spring+rise(-r+2*r*i/n)) for i in range(n+1)]
    outer=[face.p(u-(r+.16)+2*(r+.16)*i/n,-.05,spring+rise(-(r+.16)+2*(r+.16)*i/n,r+.16)) for i in range(n+1)]
    # Axis-independent solid arch strips; coherent mesh construction around the aperture.
    vs=[];fs=[]
    for a,b in zip(pts,outer):
        vs.extend([a,b,tuple(C.Vector(a)+face.n*.26),tuple(C.Vector(b)+face.n*.26)])
    for i in range(n):
        k=i*4;l=k+4;fs.extend([(k,l,l+1,k+1),(k+2,k+3,l+3,l+2),(k,k+2,l+2,l),(k+1,l+1,l+3,k+3)])
    fs.extend([(0,1,3,2),(4*n,4*n+2,4*n+3,4*n+1)])
    C.mesh('dressed stone arch',vs,fs,'stone','openings')
    for s in (-1,1):
        face.part('arch jamb',u+s*(r+.075),.07,(bottom+spring)/2,.15,.28,spring-bottom,'stone','openings',0)
    if not door:
        wall_obstacle(face,u-r,u+r,bottom,top)
        # Real glazing, separate inward frame, and common occupied room beyond.
        face.part('window sill',u,.05,bottom-.07,width+.3,.60,.14,'stone','openings',0)
        poly=[(u-r+.06,bottom),(u+r-.06,bottom),(u+r-.06,spring)]
        poly += [(u+r-.06-2*(r-.06)*i/n,spring+rise(r-.06-2*(r-.06)*i/n,r-.06)) for i in range(n+1)]
        face.panel('inset arched glass',poly,.24,.252,'glass','openings')
        for xx in (-r*.45,0,r*.45):
            h=spring+rise(xx)
            face.part('slender iron sash',u+xx,.20,(bottom+h)/2,.045,.07,h-bottom,'trim','openings',0)
        face.part('sash transom',u,.20,spring-.05,width,.07,.05,'trim','openings',0)
    C.OPENINGS.append(dict(id=face.label+str(u),face=face.label,u=u,z=bottom,width=width,height=spring-bottom,
        kind='open passage' if door else 'arched window',clear_wall_cut=True,carrier_depth_m=.42,
        frame_inset_m=.20,pane_inset_m=None if door else .24,face_origin=list(face.o),face_tangent=list(face.t),
        face_inward=list(face.n),occupied_space='modeled shared room',cols=3,rows=1))

def arcade(face,length,centers,width,bottom=.12,spring=3.2,top=6.1,doors=(),pointed=False):
    cursor=0
    for u in centers:
        lo=u-width/2;hi=u+width/2
        if lo>cursor:wall_obstacle(face,cursor,lo,bottom,top)
        if u not in doors and bottom<1:wall_obstacle(face,lo,hi,bottom,1)
        if lo>cursor:face.part('brick pier',(cursor+lo)/2,.21,(bottom+top)/2,lo-cursor,.42,top-bottom,'wall','envelope',0)
        if u not in doors and bottom<1:face.part('brick window apron',u,.21,.55,width,.42,.86,'wall','envelope',0)
        opening(face,u,width,bottom if u in doors else max(bottom,1),spring,top,door=u in doors,pointed=pointed)
        cursor=hi
    if cursor<length:
        wall_obstacle(face,cursor,length,bottom,top)
        face.part('brick end pier',(cursor+length)/2,.21,(bottom+top)/2,length-cursor,.42,top-bottom,'wall','envelope',0)
    for z,h in [(top-.05,.20),(top+.25,.24)]:face.part('continuous dressed cornice',length/2,.13,z,length+.18,.64,h,'stone','cornice',0)

def gable_roof(x0,x1,y0,y1,eave,ridge):
    ym=(y0+y1)/2
    for ya,yb,za,zb in [(y0,ym,eave,ridge),(ym,y1,ridge,eave)]:
        C.solid_surface('slate roof field',[(x0,ya,za),(x1,ya,za),(x1,yb,zb),(x0,yb,zb)],.16,'roof','roof')
        for j in range(1,16):
            t=j/16;y=ya+(yb-ya)*t;z=za+(zb-za)*t+.014
            beam('slate course',(x0,y,z),(x1,y,z),.015,.025,'roof')
    for x in (x0,x1):C.prism('closed roof gable',[(y0,eave),(y1,eave),(ym,ridge)],'x',x-.12,x+.12,'wall','roof')
    beam('slate ridge',(x0,ym,ridge+.02),(x1,ym,ridge+.02),.16,.16,'roof')

def headhouse():
    # Main entrance arcade: open bays, with one common ticket hall behind.
    front=C.Face((-18.2,-42,0),(1,0,0),(0,1,0),'front arcade')
    rear=C.Face((18.2,-34,0),(-1,0,0),(0,-1,0),'rear ticket hall')
    centers=[2.6,7.7,12.8,18.2,23.3,28.4,33.5]
    arcade(front,36.4,centers,3.8,doors=tuple(centers))
    arcade(rear,36.4,centers,3.8,doors=(18.2,))
    for face in (front,rear):
        face.part('full depth eave bearing frieze',18.2,.21,6.34,36.4,.42,.64,'wall','roof contact',0)
    # Main gable fields partition around real dormer and clock penetrations.
    holes=[(x-.65,x+.65,-41.05,-39.25) for x in (-10,-4,2)]+[(8.05,12.95,-42.4,-36.8)]
    height=lambda y:6.6+4.1*(1-abs(y+38)/4)
    xs=sorted({-18.2,18.2,*[x for h in holes for x in h[:2]]})
    ys=sorted({-42,-38,-34,*[y for h in holes for y in h[2:] if -42<y<-34]})
    for xa,xb in zip(xs,xs[1:]):
        for ya,yb in zip(ys,ys[1:]):
            if any(l<(xa+xb)/2<r and lo<(ya+yb)/2<hi for l,r,lo,hi in holes):continue
            C.solid_surface('closed headhouse slate roof',[(xa,ya,height(ya)),(xb,ya,height(ya)),(xb,yb,height(yb)),(xa,yb,height(yb))],.18,'roof','roof')
            for y in [ya+(yb-ya)*i/max(1,math.ceil((yb-ya)/.22)) for i in range(1,max(1,math.ceil((yb-ya)/.22)))]:
                beam('slate coursing',(xa,y,height(y)+.015),(xb,y,height(y)+.015),.018,.025,'roof')
    for x in (-21,21):
        # Two-stage projecting pavilions. Physical paired upper Gothic apertures.
        for y,tangent,inward in [(-43,(1,0,0),(0,1,0)),(-33,(-1,0,0),(0,-1,0))]:
            face=C.Face((x-2.8 if tangent[0]>0 else x+2.8,y,0),tangent,inward,'end pavilion')
            arcade(face,5.6,[2.8],2.8,top=5.8,doors=(2.8,))
            arcade(face,5.6,[1.75,3.85],1.35,bottom=6.6,spring=8.0,top=9.5,pointed=True)
            # Small aprons are explicitly above the ground-floor portal.
            face.part('upper storey apron',2.8,.21,6.35,5.6,.42,1.1,'wall','pavilion',0)
            face.panel('steep pavilion gable',[(0,9.5),(5.6,9.5),(2.8,14.1)],0,.42,'wall')
            for u,v,za,zb in [(0,2.8,9.5,14.1),(2.8,5.6,14.1,9.5)]:beam('Gothic coping',face.p(u,-.10,za),face.p(v,-.10,zb),.38,.42,'stone')
            for k in range(32):
                t=k*math.tau/32;tt=(k+1)*math.tau/32
                beam('gable oculus trim',face.p(2.8+.43*math.cos(t),-.06,11.2+.43*math.sin(t)),face.p(2.8+.43*math.cos(tt),-.06,11.2+.43*math.sin(tt)),.08,.07,'stone')
        for side in (-1,1):
            face=C.Face((x+side*2.8,-43 if side==1 else -33,0),(0,side,0),(-side,0,0),'pavilion return')
            arcade(face,10,[2.5,7.5],2.0,top=5.8)
            face.part('return upper apron',5,.21,6.35,10,.42,1.1,'wall','pavilion',0)
            arcade(face,10,[2,4,6,8],1.25,bottom=6.6,spring=8.0,top=9.5,pointed=True)
            C.solid_surface('pavilion slate slope',[(x+side*3,-43.3,9.5),(x,-43.3,14.2),(x,-32.7,14.2),(x+side*3,-32.7,9.5)],.18,'roof','roof')
        # Side walls are solid construction; public passage continues through the centre.
        for xx in (x-2.8,x+2.8):obstacle(xx-.24,xx+.24,-43,-33,0,9.5)
        floor('pavilion passage',x-1.2,x+1.2,-43.2,-32.8,GROUND)
    for side in (-1,1):
        x=side*25.5
        front=C.Face((x-1.7,-42,0),(1,0,0),(0,1,0),'end wing front')
        rear=C.Face((x+1.7,-34,0),(-1,0,0),(0,-1,0),'end wing rear')
        arcade(front,3.4,[1.7],1.55,top=5.5);arcade(rear,3.4,[1.7],1.55,top=5.5)
        face=C.Face((side*27.2,-42 if side==1 else -34,0),(0,side,0),(-side,0,0),'end wing side')
        arcade(face,8,[2,6],1.75,top=5.5)
        box('end wing flat roof',(x,-38,5.6),(3.4,8,.20),'roof','roof')
    # Clock shaft is an inhabited masonry volume, right of centre, from grade.
    x=10.5;y=-39.6
    for face in [C.Face((8.2,-42.25,0),(1,0,0),(0,1,0),'clock front'),C.Face((12.8,-36.95,0),(-1,0,0),(0,-1,0),'clock rear'),C.Face((12.8,-42.25,0),(0,1,0),(-1,0,0),'clock right'),C.Face((8.2,-36.95,0),(0,-1,0),(1,0,0),'clock left')]:
        length=4.6 if 'front' in face.label or 'rear' in face.label else 5.3
        arcade(face,length,[length*.32,length*.68],.90,bottom=.12,spring=4.3,top=5.6)
        # Tall recessed twin lancets above the lower windows.
        face.part('clock intermediate wall',length/2,.21,6.65,length,.42,2.1,'wall','clock',0)
        for u in (length*.32,length*.68):opening(face,u,.82,7.6,9.9,11.3)
        for a,b in [(0,length*.32-.41),(length*.32+.41,length*.68-.41),(length*.68+.41,length)]:face.part('clock upper pier',(a+b)/2,.21,9.45,b-a,.42,3.7,'wall','clock',0)
        face.part('clock chamber wall',length/2,.21,13.25,length,.42,3.9,'wall','clock',0)
        center=face.p(length/2,-.09,13.25)
        pts=[face.p(length/2+1.10*math.cos(i*math.tau/64),-.08,13.25+1.10*math.sin(i*math.tau/64)) for i in range(64)]
        C.mesh('clock face',pts,[tuple(range(64))],'white','clock')
        for i in range(12):
            t=i*math.tau/12
            beam('clock index',face.p(length/2+.89*math.sin(t),-.11,13.25+.89*math.cos(t)),face.p(length/2+1.03*math.sin(t),-.11,13.25+1.03*math.cos(t)),.047,.04,'hardware')
        beam('minute hand',center,face.p(length/2+.70,-.13,13.65),.065,.045,'hardware')
        beam('hour hand',center,face.p(length/2-.35,-.13,13.75),.08,.045,'hardware')
    obstacle(8.0,13.0,-42.5,-36.7,0,15.2)
    for z in (6.0,11.3,15.1):box('clock stone belt',(x,y,z),(5.0,5.7,.20),'stone','clock')
    box('closed spire bearing course',(x,y,15.23),(5.25,6.25,.30),'stone','clock')
    C.mesh('steep clock spire',[(8,-42.6,15.3),(13,-42.6,15.3),(13,-36.6,15.3),(8,-36.6,15.3),(x,y,24.0)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2,1)],'roof','clock tower')
    beam('spire finial',(x,y,23.8),(x,y,24.9),.07,.07,'brass')
    for x in (-10,-4,2):
        # Dormer has no opaque owner behind its glass; the roof cut is above.
        f=C.Face((x-.65,-41.05,0),(1,0,0),(0,1,0),'seated dormer')
        B.open_wall(f,1.3,7.55,9.3,[dict(id='dormer sash',u=.65,z=7.95,w=.72,h=1.05,cols=2)],role='stone',depth=.18)
        f.panel('dormer gable',[(0,9.3),(1.3,9.3),(.65,10.35)],0,.18,'stone')
        for side in (-1,1):
            # Both faces meet the cap's actual sloped underside. Keep 4 cm of
            # bearing within its 12 cm thickness, never above the slate top.
            xa=x+side*.65-.08;xb=x+side*.65+.08
            outline=[(xa,-41.05),(xb,-41.05),(xb,-39.25),(xa,-39.25)]
            cap=lambda xx:10.35-1.15*abs(xx-x)/.78
            bottom=[(xx,yy,min(height(yy)-.10,cap(xx)-.22)) for xx,yy in outline]
            top=[(xx,yy,cap(xx)-.08) for xx,yy in outline]
            C.mesh('dormer seated cheek',bottom+top,C.BOX_FACES,'stone','dormer')
            C.solid_surface('dormer slate cap',[(x+side*.78,-41.2,9.2),(x,-41.2,10.35),(x,-39.1,10.35),(x+side*.78,-39.1,9.2)],.12,'roof','dormer')
        beam('dormer front flashing',(x-.7,-41.08,7.65),(x+.7,-41.08,7.65),.18,.06,'roof')
    for x in (-15,16):
        box('chimney',(x,-36,10.6),(.7,.8,3.5),'wall','chimney');box('chimney cap',(x,-36,12.4),(.95,1.03,.20),'stone','chimney')

def vault_z(x):return 13.8+17.8*math.sqrt(max(0,1-(x/28)**2))

def shed():
    # One barrel roof with a narrow ridge strip; no intersecting greenhouse roofs.
    n=64;angles=[math.pi*i/n for i in range(n+1)]
    xs=[-28*math.cos(t) for t in angles]
    for a,b in zip(xs,xs[1:]):
        C.solid_surface('continuous glazed barrel',[(a,-29,vault_z(a)),(b,-29,vault_z(b)),(b,46,vault_z(b)),(a,46,vault_z(a))],.018,'glass','vault glazing')
    for y in [-29+i*7.5 for i in range(11)]:
        end=y in (-29,46)
        inner=arc_points(0,y,13.8,26.1 if end else 27.3,64,15.9 if end else 17.1);outer=arc_points(0,y,13.8,28.45,64,18.25)

        for a,b in zip(inner,inner[1:]):beam('lower bow chord',a,b,.20,.32,'iron')
        for a,b in zip(outer,outer[1:]):beam('upper bow chord',a,b,.20,.32,'iron')
        for i in range(64):
            beam('truss diagonal',inner[i],outer[i+1],.10 if end else .065,.10 if end else .065,'iron')
            if end:beam('crossed end truss diagonal',outer[i],inner[i+1],.10,.10,'iron')
        if end:
            mid=[tuple((a[j]+b[j])/2 for j in range(3)) for a,b in zip(inner,outer)]
            for a,b in zip(mid,mid[1:]):beam('end lattice middle chord',a,b,.12,.25,'iron')
        for s in (-1,1):
            box('iron column shoe',(s*28,y,.25),(.95,.95,.5),'stone','structure')
            box('fluted iron pier',(s*28,y,7.1),(.60,.70,13.7),'trim','structure')
            box('iron capital',(s*28,y,13.7),(.78,.82,.26),'trim','structure')
    for x in xs:
        beam('longitudinal glazing bar',(x,-29,vault_z(x)+.03),(x,46,vault_z(x)+.03),.038,.06,'trim')
    for y in [-29+i*1.25 for i in range(61)]:
        for a,b in zip(xs,xs[1:]):beam('roof pane joint',(a,y,vault_z(a)+.03),(b,y,vault_z(b)+.03),.026,.035,'trim')
    for x in (-28.2,28.2):
        box('continuous eave gutter',(x,8.5,13.9),(.32,75.6,.32),'trim','roof drainage')
    box('raised ventilated ridge cap',(0,8.5,32.48),(1.45,75.6,.16),'trim','roof')
    for x in (-.6,.6):
        box('ridge glazing riser',(x,8.5,32.02),(.05,75,.82),'glass','roof')
        for y in [-29+i*2.5 for i in range(31)]:beam('ridge ventilation post',(x,y,31.6),(x,y,32.42),.065,.065,'trim')
    for y in (-29,46):box('closed ridge end',(0,y,32.02),(1.2,.08,.82),'trim','roof')
    # Broad end screens above the open concourse and train access.
    for y in (-29,46):
        for a,b in zip(xs,xs[1:]):
            C.solid_surface('glazed end screen',[(a,y,13.8),(b,y,13.8),(b,y,vault_z(b)),(a,y,vault_z(a))],.012,'glass','end screen')
        for x in range(-26,27,2):beam('end screen mullion',(x,y,13.8),(x,y,vault_z(x)),.075,.12,'iron')
        for z in (13.8,17.2,20.6,24,27.4):
            width=28*math.sqrt(max(0,1-((z-13.8)/17.8)**2))
            beam('end screen transom',(-width,y,z),(width,y,z),.12,.15,'iron')
    # Outer side arcades and glazed upper spandrels retain the source's openness.
    for s in (-1,1):
        for i in range(10):
            ya=-29+i*7.5;yb=ya+7.5;mid=(ya+yb)/2
            pts=[(s*28,mid-3.5*math.cos(j*math.pi/28),9.8+3.5*math.sin(j*math.pi/28)) for j in range(29)]
            for a,b in zip(pts,pts[1:]):beam('long side iron arch',a,b,.19,.26,'iron')
            for j in range(14):
                a=ya+.25+j*.5;b=a+.5
                za=9.8+math.sqrt(max(0,3.5**2-(a-mid)**2));zb=9.8+math.sqrt(max(0,3.5**2-(b-mid)**2))
                beam('open side spandrel diagonal',(s*28,a,za),(s*28,b,13.7),.07,.10,'iron')
                beam('open side spandrel crossing',(s*28,a,13.7),(s*28,b,zb),.07,.10,'iron')
            for y in (ya+.2,yb-.2):beam('side arcade spring',(s*28,y,.12),(s*28,y,10.0),.20,.24,'iron')

def rail(name,a,b,z):
    # Slender constructed railing; omit endpoints at actual stair portals.
    length=math.dist(a,b);n=max(1,math.ceil(length/.14))
    beam(name+' top',(*a,z+1.1),(*b,z+1.1),.055,.05,'brass')
    beam(name+' low',(*a,z+.12),(*b,z+.12),.025,.03,'trim')
    for i in range(n+1):
        t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
        beam(name+' picket',(x,y,z+.12),(x,y,z+1.1),.018,.022,'trim')
    obstacle(min(a[0],b[0])-.025,max(a[0],b[0])+.025,min(a[1],b[1])-.025,max(a[1],b[1])+.025,z,z+1.1)

def stairs(x):
    # Thirty 170 mm risers, 320 mm treads; 3.2 m clear, two independent routes.
    for i in range(30):
        y=-23+i*.32;z=GROUND+(i+1)*.17
        floor('stair tread',x-1.6,x+1.6,y,y+.32,z,z)
    for s in (-1,1):
        a=(x+s*1.72,-23,GROUND);b=(x+s*1.72,-13.4,GALLERY)
        beam('stair stringer',a,b,.14,.26,'iron')
        beam('continuous stair handrail',(a[0],a[1],a[2]+1.1),(b[0],b[1],b[2]+1.1),.06,.055,'brass')
        for i in range(0,30,2):
            y=-23+(i+.5)*.32;z=GROUND+(i+1)*.17
            beam('stair baluster',(a[0],y,z),(a[0],y,z+1.1),.025,.025,'trim')
        obstacle(a[0]-.025,a[0]+.025,-23,-13.4,GROUND,GALLERY+1.1)

def carriage(x,y,length):
    """Static source-compatible passenger coach; no claim of a working train."""
    box('coach underframe',(x,y,.70),(2.75,length,.25),'hardware','train')
    for yy in (y-length*.32,y+length*.32):
        for dy in (-.5,.5):
            for side in (-1,1):
                C.rod('flanged railway wheel',(x+side*.67,yy+dy,.54),(x+side*.80,yy+dy,.54),.30,'hardware','train',20)
            beam('coach axle',(x-.75,yy+dy,.54),(x+.75,yy+dy,.54),.13,.13,'hardware')
    for side in (-1,1):
        face=C.Face((x+side*1.40,y-length/2 if side==1 else y+length/2,0),(0,side,0),(-side,0,0),'coach side')
        count=int(length/1.8)
        holes=[dict(id='coach occupied window',u=(i+.5)*length/count,z=1.75,w=1.12,h=1.10,cols=1) for i in range(count)]
        B.open_wall(face,length,.82,3.30,holes,role='iron',depth=.08)
        for z in (1.6,3.22):face.part('coach cream lining',length/2,-.015,z,length,.03,.05,'stone','train',0)
    for yy in (y-length/2,y+length/2):
        face=C.Face((x-1.4,yy,0),(1,0,0),(0,1 if yy<y else -1,0),'coach end')
        B.open_wall(face,2.8,.82,3.3,[dict(id='coach end window',u=1.4,z=1.65,w=1.3,h=1.25,cols=2)],role='iron',depth=.08)
        C.prism('closed curved coach end',[(x-1.48,3.25),(x+1.48,3.25)]+[(x+1.48*math.cos(i*math.pi/24),3.30+.46*math.sin(i*math.pi/24)) for i in range(25)],'y',yy-.06,yy+.06,'iron','train')
    for i in range(24):
        a=-1.48+2.96*i/24;b=-1.48+2.96*(i+1)/24
        roof=lambda xx:3.30+.46*math.sqrt(max(0,1-(xx/1.48)**2))
        C.solid_surface('coach barrel roof',[(x+a,y-length/2-.1,roof(a)),(x+b,y-length/2-.1,roof(b)),(x+b,y+length/2+.1,roof(b)),(x+a,y+length/2+.1,roof(a))],.07,'roof','train')
    floor_z=.85
    box('coach floor',(x,y,floor_z),(2.7,length-.15,.10),'timber','train')
    for yy in [y-length/2+1.2+i*1.8 for i in range(int(length/1.8)-1)]:
        for side in (-1,1):
            box('passenger seat',(x+side*.86,yy,1.24),(.75,.55,.16),'timber','train')
            box('passenger seat back',(x+side*.86,yy+.23,1.61),(.75,.10,.70),'timber','train')

def bench(x,y,z=GROUND,length=2.4):
    for dy in (-.2,-.1,0,.1,.2):box('bench seat slat',(x,y+dy,z+.46),(length,.075,.055),'timber','furniture')
    for dz in (.63,.77,.91):box('bench back slat',(x,y+.24,z+dz),(length,.055,.09),'timber','furniture')
    for dx in (-length*.38,length*.38):
        box('bench support',(x+dx,y,z+.24),(.06,.44,.48),'trim','furniture')
        beam('bench back upright',(x+dx,y+.24,z+.3),(x+dx,y+.24,z+.98),.055,.055,'trim')
    obstacle(x-length/2-.04,x+length/2+.04,y-.3,y+.3,z,z+1)

def sign(text,x,y,z,w=4):
    box('enamel sign',(x,y,z),(w,.1,.8),'board','signage')
    B.label(text,(x,y-.063,z-.12),.24,'white')

def programme():
    # Public ground-floor surfaces stop at rails, walls, counters and stair undersides.
    floor('front entrance apron',-29,29,-48,-42,GROUND)
    floor('ticket hall',-26.5,26.5,-41.6,-34.4,GROUND)
    for x in (-21,0,21):floor('open entry threshold',x-1.55,x+1.55,-42.6,-33.9,GROUND)
    floor_with_holes('forecourt and main concourse',-27.5,27.5,-34.4,2,GROUND,[(-21.85,-18.15,-23,-13.4),(18.15,21.85,-23,-13.4)])
    # Full ground under galleries is usable; the current-height solver prevents floor snapping.
    floor('left side concourse',-27.5,-16,2,45.5,GROUND)
    floor('right side concourse',16,27.5,2,45.5,GROUND)
    for x in (-13.5,-4.5,4.5,13.5):
        floor('raised platform',x-2,x+2,2,45.5,GROUND)
        for s in (-1,1):
            box('platform safety line',(x+s*1.7,23.7,GROUND+.006),(.13,43.4,.012),'brass','platform markings')
        for y in (10,22,36):bench(x,y,length=2.1)
        sign('PLATFORM '+str(int((x+13.5)/9+1)),x,4,3.5,3.4)
        for y in (4,42):beam('platform sign support',(x+1.65,y,GROUND),(x+1.65,y,3.9),.10,.10,'trim')
        beam('platform canopy ridge',(x,4,4.1),(x,44,4.1),.12,.2,'trim')
        for s in (-1,1):C.solid_surface('platform canopy',[(x,4,4.2),(x+s*1.8,4,3.85),(x+s*1.8,44,3.85),(x,44,4.2)],.08,'roof','platform canopies')
        for y in (8,20,32,44):
            beam('canopy mast',(x,y,GROUND),(x,y,4.1),.10,.12,'trim')
            obstacle(x-.08,x+.08,y-.08,y+.08,GROUND,4.2)
    for x in (-9,0,9):
        box('track ballast',(x,24,.055),(4.2,44,.11),'track','railway')
        for y in [3+i*.65 for i in range(66)]:box('rail sleeper',(x,y,.16),(2.5,.21,.12),'timber','railway')
        for dx in (-.72,.72):box('steel running rail',(x+dx,24,.25),(.085,44,.12),'hardware','railway')
        box('buffer beam',(x,2.3,.73),(2.65,.28,.34),'iron','railway')
        for dx in (-.8,.8):beam('buffer support',(x+dx,2.3,.1),(x+dx,2.3,.8),.18,.24,'iron')
    carriage(0,24,24);carriage(-9,32,20)
    # Side galleries linked over the front concourse. Rear remains a clear train shed.
    for s in (-1,1):
        x=s*22
        floor('gallery deck',x-4.8,x+4.8,-13.4,40,GALLERY,.24)
        stairs(s*20)
        rail('gallery inner guard',(s*17.2,-13.4),(s*17.2,-12.7),GALLERY)
        rail('gallery inner guard',(s*17.2,-8.7),(s*17.2,40),GALLERY)
        rail('gallery outer guard',(s*26.8,-13.4),(s*26.8,40),GALLERY)
        rail('gallery rear guard',(x-4.8,40),(x+4.8,40),GALLERY)
        # Lower landing edge has a 3.6m opening at stair head.
        for a,b in [(x-4.8,s*20-1.85),(s*20+1.85,x+4.8)]:
            if b>a:rail('landing return',(a,-13.4),(b,-13.4),GALLERY)
        for y in (-11,0,12,24,38):
            box('gallery bearing column',(x,y,2.55),(.25,.3,5.1),'trim','gallery structure')
            beam('gallery transverse girder',(x-4.8,y,5.02),(x+4.8,y,5.02),.22,.35,'iron')
            obstacle(x-.17,x+.17,y-.20,y+.20,0,5.05)
        for y in (4,16,28):bench(s*24,y,GALLERY)
    floor('front gallery crossover',-17.2,17.2,-12.7,-8.7,GALLERY,.24)
    for y in (-12.7,-8.7):rail('crossover balustrade',(-17.2,y),(17.2,y),GALLERY)
    for x in (-12,-6,6,12):
        box('bridge pier',(x,-10.7,2.55),(.22,.3,5.1),'trim','gallery structure')
        obstacle(x-.15,x+.15,-10.9,-10.5,0,5.05)
    # Ticket counters, real booths and staffed-space depth, clear public aisle.
    for x in (-15,-10,15):
        box('ticket counter',(x,-39,.65),(3.4,.9,1.05),'timber','ticket office')
        box('countertop',(x,-39,1.22),(3.6,1.03,.09),'stone','ticket office')
        for dx in (-1.75,1.75):box('ticket grille pier',(x+dx,-39,2.1),(.055,.09,1.8),'brass','ticket office')
        for dx in (-1.3,-.85,.85,1.3):box('ticket grille',(x+dx,-39,1.95),(.025,.055,1.3),'brass','ticket office')
        sign('TICKETS',x,-39,3.2,3.5)
        obstacle(x-1.85,x+1.85,-39.6,-38.4,0,3.6)
    # Departure board and freestanding information counter, offset from entrance axis.
    sign('DEPARTURES',0,-28,4.8,9)
    for x in (-4.3,4.3):beam('board suspension',(x,-28,5.2),(x,-28,13.8),.025,.025,'trim')
    for i,t in enumerate(['09:15   NORTHBOUND      1','09:40   RIVERSIDE       2','10:05   CENTRAL        3']):
        box('departure row',(0,-28,4.10-i*.48),(9,.12,.46),'board','signage');B.label(t,(0,-28.075,3.98-i*.48),.22,'white')
    for y in (-29,-25):
        for x in (-11,11):bench(x,y,length=3.0)
    for x in (-24,-19):
        for y in (-31,-27):
            B.table(x,y,GROUND);obstacle(x-.9,x+.9,y-1.1,y+1.1,GROUND,GROUND+1.1)
    box('cafe serving counter',(-24,-24, .7),(4,.9,1.16),'timber','cafe')
    sign('STATION CAFE',-24,-24,2.6,4.6)
    obstacle(-26.2,-21.8,-24.6,-23.4,0,3.1)
    box('espresso machine',(-24,-24,1.55),(.85,.48,.50),'hardware','cafe')
    for x in (-24.25,-23.95):
        C.rod('espresso group',(x,-24.27,1.35),(x,-24.27,1.55),.065,'brass','cafe',12)
    for x in (-25.4,-25.1,-24.8):
        C.rod('coffee cup',(x,-24,1.29),(x,-24,1.43),.06,'white','cafe',16)
    for x in (-25.7,-24.7,-23.7,-22.7):
        box('counter recessed panel',(x,-24.47,.68),(.80,.04,.80),'stone','cafe')
    # Front fascia sits above clear passenger entries.
    B.label('VICTORIA  STATION',(0,-42.47,6.4),.34,'brass')

def roster():
    target=(0,0,14)
    views=[dict(name=n,location=p,target=target,ortho_scale=75 if n in ('front','rear') else 113) for n,p in [('front',(0,-150,14)),('left_side',(-150,0,14)),('right_side',(150,0,14)),('rear',(0,150,14))]]
    views += [dict(name='front_corner',location=(100,-120,55),target=target),dict(name='aerial',location=(90,-125,120),target=target),dict(name='top',location=(0,0,170),target=(0,.001,0),ortho_scale=122),dict(name='rear_side',location=(-100,130,55),target=target)]
    views += [dict(name=n,location=p,target=t,whole=False,lens=l) for n,p,t,l in [
        ('facade_close',(23,-55,8),(10,-39,9),38),('architecture_close',(37,-38,26),(25,-25,15),35),
        ('glass_close',(9,-38,24),(1,-26,23),38),('roof_contact',(35,-40,44),(10,-4,27),42),
        ('dormer_contact',(-6,-47,11),(-4,-40,9),35),('clock_contact',(23,-56,17),(10,-39.5,11.7),32),
        ('program_interior',(0,-27,1.77),(0,15,8),22),('ticket_hall',(4,-36,1.77),(-12,-39,2),24),
        ('gallery_stair',(14,-26,1.77),(20,-14,5),26),('gallery',(19,-10,6.87),(0,16,7),24),
        ('platform_oblique',(-12,9,1.77),(2,36,8),24),('track_axis',(0,3,2),(0,42,10),26),
        ('walk',(0,-47,1.77),(0,-38,3),25)]]
    return views

def main():
    a=C.args();paths=[]
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        path=ROOT/'frontend/public/archetypes/buildings/historic_grand_station'/('variant_1'+suffix)
        data=path.read_bytes();assert len(data)>10000
        paths.append(dict(role=role,path='sources/'+path.name,original_path=str(path),repo_path=str(path.relative_to(ROOT)).replace('\\','/'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    entry=dict(archetype_id='historic_grand_station',variant_id='station_victorian_iron_glass',sources=paths,_reference_root=str(path.parent),directory='.')
    views=roster();manifest=dict(candidate=f'victorian-station-interior-clay-v{a.version:03d}',method=C.METHOD,archetype_id=entry['archetype_id'],variant_id=entry['variant_id'],representation_kind='architectural_clay',camera_roster=views,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=60,depth=96,height=33),floors=2,front='-Y',bottom_datum_m=0,measurement_basis='Compatible catalogue proportions; plausible metric station construction, not surveyed'),
        identity_contract=['One high broad glazed barrel vault on open iron side arcades','Low brick Gothic headhouse with end gabled pavilions and offset right clock spire','Broad glazed transverse end screen, fine longitudinal glazing and narrow ridge strip','Tracks, platforms, ticket hall, cafe, departure board, two connected stairs and upper gallery'],
        hidden_view_assumptions=['Rear continues the same iron end-frame language','Interior room programme, furniture and paired gallery stairs are authored inference','High oblique top source resolves clock offset and roof topology over cropped street reference'],
        limitations=['Architectural-clay profile matching the local library; no PBR texture keeper claim','Fixed two occupied levels; tower is not publicly enterable','No animated trains or working timetable; no live rail connection','Prepared level site pilot; runtime integration pending'])
    out=C.prepare_candidate(a,entry,manifest,__file__)
    if out is None:return
    # Distinct basenames preserve the actual constructor and shared helper independently.
    helper=out/'scripts/showcase_shared.py';shutil.copy2(HERE.parent/'showcase_building_trio/build.py',helper)
    manifest['provenance']['scripts'].append(dict(path='scripts/showcase_shared.py',sha256=C.digest(helper)))
    (out/'prework-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    cams=C.setup(PALETTE,views,a.resolution);C.fit=B.efficient_fit;C.bpy.context.scene.cycles.samples=16
    bs=C.MATS['glass'].node_tree.nodes['Principled BSDF'];bs.inputs['Alpha'].default_value=.15;bs.inputs['Roughness'].default_value=.15
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2;sun.data.angle=.12
    for y in (-37,-26,-8,12,34):
        for x in (-19,0,19):C.qa_room_light('station',(x,y,6 if y==-37 else 12),900,8)
    # Thin grade-supported slab keeps the exact native datum at zero.
    box('station foundation',(0,0,.04),(60,96,.08),'foundation','foundation')
    # Furniture chamfers run before the dense glazing grid is in the scene.
    print('BUILD_PHASE programme',flush=True);programme()
    print('BUILD_PHASE headhouse',flush=True);headhouse()
    print('BUILD_PHASE shed',flush=True);shed()
    print('BUILD_PHASE delivery',flush=True)
    routes=[dict(name='concourse and platforms',points=[[0,-46,GROUND],[0,-36,GROUND],[0,-25,GROUND],[5,-25,GROUND],[5,-16,GROUND],[8,-3,GROUND],[13.5,0,GROUND],[12,5,GROUND],[12,40,GROUND]]),
        dict(name='paired stairs and gallery loop',points=[[0,-46,GROUND],[0,-36,GROUND],[0,-24,GROUND],[17,-24,GROUND],[20,-24,GROUND],[20,-23,GROUND],[20,-13.25,GALLERY],[20,-10.7,GALLERY],[-20,-10.7,GALLERY],[-20,-13.25,GALLERY],[-20,-23,GROUND],[-20,-24.8,GROUND],[-15,-24,GROUND],[0,-24,GROUND]]),
        dict(name='upper gallery promenade',points=[[20,-10.7,GALLERY],[19,0,GALLERY],[19,36,GALLERY],[26,36,GALLERY],[26,-10.7,GALLERY]])]
    walking=dict(version=2,triangles=TRIANGLES,obstacles=OBSTACLES,entrance=[0,-46,GROUND],maxStepM=.20,routes=routes,bodyRadiusM=.22,headroomM=1.8,footprint=[60,96],portals=[[-1.5,1.5,-48,-45]],scope='authored public floor tops, metres Z-up; choose connected current height')
    C.write_json(out/'walking-network.json',walking)
    next(o for o in C.objects() if o.get('cityprompt_semantic_role')=='walk_floor')['cityprompt_walking_json']=json.dumps(walking,separators=(',',':'))
    report=C.deliver(out,manifest,cams)
    C.write_json(out/'walking-model-lock.json',dict(model_sha256=report['runtime']['sha256'],network_sha256=C.digest(out/'walking-network.json')))

if __name__=='__main__':main()
