"""Original Gothic church: complete native envelope and navigable sanctuary.

Reference views are generated original design studies, not an existing church.
Builds and renders remain external until independent and human review.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0, str(HERE.parent / 'catalogue_duplex_pilot'))
import clay_core as C
from mathutils import Vector
spec = importlib.util.spec_from_file_location('civic_shared', HERE.parent / 'showcase_building_trio/build.py')
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
from walking import attach_church_walk

PALETTE = dict(B.PALETTE, wall=(.57,.49,.36), stone=(.62,.54,.41), roof=(.095,.115,.135),
    trim=(.49,.42,.31), timber=(.22,.105,.045), interior=(.65,.59,.47), floor=(.49,.45,.36),
    glass=(.38,.46,.5), stained_blue=(.025,.09,.31), stained_red=(.34,.035,.025),
    stained_gold=(.63,.34,.07), stained_green=(.08,.23,.16), lead=(.045,.04,.035))

def box(name, loc, size, role='wall', module='envelope'):
    return C.box(name, loc, size, role, module, 0)

def pointed(x, radius):
    return math.sqrt(max(0, (2*radius)**2-(abs(x)+radius)**2))

def arch_outline(u,z,w,shoulder,segments=48):
    r=w/2
    return [(u-r,z),(u+r,z)]+[(u+r-2*r*i/segments,z+shoulder+pointed(r-2*r*i/segments,r)) for i in range(segments+1)]

def cut_profile(owner, face, ident, profile, depth=.6):
    cutter=face.panel(ident+' cutter',profile,-1,depth+1,'wall','construction cutter')
    C.bpy.context.view_layer.objects.active=owner
    modifier=owner.modifiers.new(ident+' physical void','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    C.bpy.ops.object.modifier_apply(modifier=modifier.name)
    C.remove_cutter(cutter);C.normalise(owner.data)

def ring(face, name, inner, outer, d0, d1, role='stone'):
    n=len(inner);assert n==len(outer)
    vs=[face.p(u,d,z) for d in (d0,d1) for poly in (inner,outer) for u,z in poly]
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                   (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return C.mesh(name,vs,fs,role,'physical opening surround')

def arch_frame(face,name,u,z,w,shoulder,width=.16,d0=-.08,d1=.24):
    inner=arch_outline(u,z,w,shoulder)
    outer=arch_outline(u,z-width,w+2*width,shoulder+width)
    # Entrance archivolts terminate on the floor, never below native grade.
    outer=[(x,max(0,h)) for x,h in outer]
    return ring(face,name,inner,outer,d0,d1)

def record_opening(face,name,u,z,w,h,depth):
    C.OPENINGS.append(dict(id=name,face=face.label,u=u,z=z,width=w,height=h,kind='pointed architectural opening',
        clear_wall_cut=True,carrier_depth_m=depth,frame_inset_m=.24,pane_inset_m=.32,
        face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),
        occupied_space='Continuous accessible sanctuary, no image cards'))

def arch_window(owner,face,name,u,z,w,shoulder,depth=.6,glazed=True):
    cut_profile(owner,face,name,arch_outline(u,z,w,shoulder),depth)
    arch_frame(face,name+' masonry reveal',u,z,w,shoulder,.16,-.08,depth)
    arch_frame(face,name+' recessed tracery',u,z+.08,w-.14,shoulder-.08,.065,.22,.34)
    record_opening(face,name,u,z,w,shoulder,depth)
    if not glazed:return
    # Actual coloured panes, with fine lead joints and room depth beyond.
    radius=(w-.20)/2;step=.33;rows=math.ceil((shoulder+radius*math.sqrt(3))/step)
    cols=max(3,round(2*radius/.34));cw=2*radius/cols
    for col in range(cols):
        cell_left=-radius+col*cw+.009;cell_right=cell_left+cw-.018
        for row in range(rows):
            low=z+.12+row*step;high=low+step-.022
            limit=radius
            if low>z+shoulder-.035:
                limit=math.sqrt(max(0,(2*radius)**2-(low-z-shoulder+.035)**2))-radius
            left=max(cell_left,-limit);right=min(cell_right,limit)
            if right-left<.008:continue
            lh=min(high,z+shoulder+pointed(left,radius)-.07)
            rh=min(high,z+shoulder+pointed(right,radius)-.07)
            # Include partially filled cells at the arch edge, with a clipped
            # curved top instead of leaving a staircase of missing panes.
            top=[(u+x,max(low,min(high,z+shoulder+pointed(x,radius)-.035))) for x in [right-(right-left)*k/6 for k in range(7)]]
            if max(h for _,h in top)<=low+.004:continue
            role=['stained_blue','stained_gold','stained_red','stained_green'][(col*3+row+int(u))%4]
            face.panel(name+' coloured glass',[(u+left,low),(u+right,low),*top],.32,.331,role,'stained glazing')
            if lh>low:C.beam(name+' vertical lead',face.p(u+left,.31,low),face.p(u+left,.31,lh),.018,.022,'lead','stained glazing')
            C.beam(name+' horizontal lead',face.p(u+left,.31,low),face.p(u+right,.31,low),.018,.022,'lead','stained glazing')
    for x in (-w/6,w/6):
        height=shoulder+pointed(x,w/2)-.13
        face.part(name+' main mullion',u+x,.26,z+height/2,.10,.16,height,'stone','stone tracery',0)
    face.part(name+' sill',u,-.02,z-.06,w+.34,.85,.16,'stone','stone tracery',0)

def circle(u,z,r,n=80):return [(u+r*math.cos(i*math.tau/n),z+r*math.sin(i*math.tau/n)) for i in range(n)]

def rose(owner,face,u,z,r):
    cut_profile(owner,face,'rose',circle(u,z,r),.75)
    ring(face,'rose masonry',circle(u,z,r),circle(u,z,r+.3),-.16,.75)
    ring(face,'rose inner molding',circle(u,z,r-.10),circle(u,z,r+.04),-.24,.05)
    for rr in (.58,1.28,r-.18):
        ring(face,'rose tracery annulus',circle(u,z,rr-.05),circle(u,z,rr+.05),.24,.39)
    for i in range(16):
        a=i*math.tau/16;b=(i+1)*math.tau/16
        for j,(r0,r1) in enumerate(((.12,.51),(.65,1.2),(1.35,r-.23))):
            pts=[(u+r0*math.cos(a+.015),z+r0*math.sin(a+.015)),(u+r1*math.cos(a+.015),z+r1*math.sin(a+.015)),
                 (u+r1*math.cos(b-.015),z+r1*math.sin(b-.015)),(u+r0*math.cos(b-.015),z+r0*math.sin(b-.015))]
            face.panel('rose coloured petal',pts,.39,.405,['stained_blue','stained_gold','stained_red'][(i+j)%3],'rose stained glass')
        C.beam('rose radial tracery',face.p(u+.53*math.cos(a),.30,z+.53*math.sin(a)),
               face.p(u+(r-.15)*math.cos(a),.30,z+(r-.15)*math.sin(a)),.07,.13,'stone','rose tracery')

def cone(name,x,y,z,r,height,role='roof',n=8):
    C.prism(name+' base',[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n)) for i in range(n)],'z',z,z+.10,role,'spire')
    vs=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z) for i in range(n)]+[(x,y,z+height)]
    return C.mesh(name,vs,[tuple(range(n-1,-1,-1))]+[(i,(i+1)%n,n) for i in range(n)],role,'spire')

def cross(x,y,z,size=1):
    box('cross upright',(x,y,z+size*.55),(.09*size,.09*size,1.1*size),'bronze','roof cross')
    box('cross arms',(x,y,z+size*.76),(.60*size,.09*size,.085*size),'bronze','roof cross')

def pinnacle(x,y,z,size=.65):
    box('pinnacle seated block',(x,y,z+.5),(size,size,1),'stone','pinnacle')
    cone('stone pinnacle',x,y,z+1,size*.7,2.1,'stone',4)
    for h in (1.3,1.8,2.3):
        r=size*.44*(3.1-h)/2.1
        for sign in (-1,1):
            C.rod('pinnacle crockets',(x+sign*r,y,z+h),(x+sign*(r+.13),y,z+h+.12),.065,'stone','pinnacle',6)

def main_roof():
    for side in (-1,1):
        C.solid_surface('main slate roof',[(0,-22,23),(side*6.8,-22,16.1),(side*6.8,19,16.1),(0,19,23)],.24,'roof')
        C.solid_surface('aisle slate roof',[(side*6.7,-22,12),(side*12.9,-22,8.7),(side*12.9,19,8.7),(side*6.7,19,12)],.20,'roof')
        # Slate courses remain bounded to their actual sloped carrier.
        for i in range(1,34):
            x=side*6.8*i/34;z=23-6.9*i/34
            C.beam('main slate coursing',(x,-22,z+.012),(x,19,z+.012),.018,.018,'roof','roof courses')
        for i in range(1,18):
            x=side*(6.7+6.2*i/18);z=12-3.3*i/18
            C.beam('aisle slate coursing',(x,-22,z+.012),(x,19,z+.012),.018,.018,'roof','roof courses')
        C.solid_surface('aisle interior lining',[(side*6.7,-22,11.77),(side*12.9,-22,8.47),(side*12.9,19,8.47),(side*6.7,19,11.77)],.06,'interior','ceiling lining')
        for y in (-22,19):C.beam('gable weathering coping',(0,y,23.12),(side*6.85,y,16.12),.23,.25,'stone','roof coping')
        C.beam('aisle gutter',(side*12.9,-22,8.7),(side*12.9,19,8.7),.17,.19,'trim','drainage')
    C.beam('ridge coping',(0,-22,23.12),(0,19,23.12),.25,.26,'roof','ridge')
    cross(0,-22,23.23,1.05)

def tower():
    cx,cy=-10,-18.5;w=6.5;depth=7
    for face in B.faces(w,depth):
        face.o+=Vector((cx,cy,0));face.label='bell tower '+face.label
        length=w if abs(face.t.x)>.5 else depth
        owner=face.wall('tower masonry',0,length,.04,28.4,.7)
        for z in (6,14):arch_window(owner,face,'tower lancet',length/2,z,.72,2.1,.7)
        for u in (length*.29,length*.71):
            arch_window(owner,face,'belfry opening',u,22,1.48,3.3,.7,False)
            for zz in (22.4,22.9,23.4,23.9,24.4):face.part('belfry louvre',u,.43,zz,1.23,.22,.14,'roof','belfry louvres',0)
        for z in (4,12,20.8,27.8,28.4):face.part('tower string course',length/2,-.09,z,length+.25,.22,.22,'stone','tower masonry',0)
        # Every quoin bears on the layer below it; no floating ornament.
        for edge in (.26,length-.26):
            face.part('tower corner pier',edge,-.10,14,.54,.32,28,'stone','tower masonry',0)
    box('tower belfry floor',(cx,cy,21.72),(w-.5,depth-.5,.23),'floor','tower structure')
    box('tower spire seat',(cx,cy,28.60),(w+.35,depth+.35,.34),'stone','tower structure')
    cone('octagonal slate spire',cx,cy,28.76,3.45,14.2)
    for i in range(8):
        a=i*math.tau/8
        C.beam('spire lead seam',(cx+3.45*math.cos(a),cy+3.45*math.sin(a),28.80),(cx,cy,42.96),.055,.055,'trim','spire seams')
    for x in (cx-3,cx+3):
        for y in (cy-3.3,cy+3.3):pinnacle(x,y,28.65,.55)
    cross(cx,cy,42.96,.9)

def apse():
    # A continuous five-sided weathering end, with an open sanctuary connection.
    outline=[(8,19),(8,24),(4.8,28),(-4.8,28),(-8,24),(-8,19)]
    C.prism('apse floor',outline,'z',0,.04,'floor','sanctuary')
    for i,(a,b) in enumerate(zip(outline,outline[1:])):
        v=Vector((b[0]-a[0],b[1]-a[1],0));length=v.length;t=v.normalized();normal=Vector((-t.y,t.x,0))
        face=C.Face((*a,0),t,normal,'apse '+str(i))
        wall=face.wall('apse stone wall',0,length,.04,15.15,.6)
        arch_window(wall,face,'apse lancet',length/2,3.2,min(2.6,length-1.3),5.7)
        C.solid_surface('apse hipped slate roof',[(a[0],a[1],15.15),(b[0],b[1],15.15),(0,20.5,21.4)],.23,'roof')
        C.solid_surface('apse ceiling lining',[(a[0],a[1],14.90),(b[0],b[1],14.90),(0,20.5,21.15)],.06,'interior','ceiling lining')
        C.beam('apse hip seam',(a[0],a[1],15.18),(0,20.5,21.42),.12,.14,'trim','roof seam')
        pinnacle(a[0],a[1],14.8,.52)
    # Close the roof transition against the rear nave, with no sheet crossing the sanctuary.
    C.solid_surface('apse front roof plane',[(-8,19,15.15),(8,19,15.15),(0,20.5,21.4)],.23,'roof')
    C.solid_surface('apse front ceiling lining',[(-8,19,14.90),(8,19,14.90),(0,20.5,21.15)],.06,'interior','ceiling lining')
    cross(0,20.5,21.6,.8)

def nave_structure():
    # Pointed longitudinal arcades, column clusters, capitals and true open aisles.
    for side in (-1,1):
        for y in (-20,-14,-8,-2,4,10,16):
            x=side*6
            box('column plinth',(x,y,.16),(.90,.90,.32),'stone','arcade')
            C.rod('arcade column',(x,y,.32),(x,y,8.3),.32,'stone','arcade',16)
            for a in range(4):
                ang=a*math.pi/2
                C.rod('clustered shaft',(x+.29*math.cos(ang),y+.29*math.sin(ang),.35),(x+.29*math.cos(ang),y+.29*math.sin(ang),8.4),.11,'stone','arcade',10)
            box('column capital',(x,y,8.4),(.92,.92,.28),'stone','arcade')
        face=C.Face((side*6,-20,0),(0,1,0),(-side,0,0),'interior arcade')
        for i in range(6):arch_frame(face,'open pointed arcade',3+6*i,.04,5.1,8.35,.22,-.24,.24)
    # Thin closed vault webs follow the pointed cross-section; ribs share the same surface.
    for bay in range(6):
        y0=-20+6*bay;y1=y0+6
        for j in range(48):
            x0=-5.85+11.7*j/48;x1=-5.85+11.7*(j+1)/48
            z0=10.2+pointed(x0,5.85);z1=10.2+pointed(x1,5.85)
            C.solid_surface('pointed vault web',[(x0,y0,z0),(x1,y0,z1),(x1,y1,z1),(x0,y1,z0)],.14,'interior','vault')
        for y in (y0,y1):
            points=[(-5.85+11.7*i/48,y,10.12+pointed(-5.85+11.7*i/48,5.85)) for i in range(49)]
            B.curve_beam('transverse vault rib',points,.14,.18,'stone','vault ribs')
        for sign in (-1,1):
            points=[]
            for i in range(49):
                t=i/48;x=-5.85+11.7*t;y=(y0+6*t) if sign==1 else (y1-6*t)
                points.append((x,y,10.10+pointed(x,5.85)))
            B.curve_beam('diagonal rib',points,.12,.15,'stone','vault ribs')
        C.rod('vault boss',(0,(y0+y1)/2,20.08),(0,(y0+y1)/2,20.27),.22,'bronze','vault boss',12)
    for j in range(48):
        x0=-5.85+11.7*j/48;x1=-5.85+11.7*(j+1)/48
        z0=10.2+pointed(x0,5.85);z1=10.2+pointed(x1,5.85)
        C.solid_surface('rear vault closure',[(x0,16,z0),(x1,16,z1),(x1,19,z1),(x0,19,z0)],.14,'interior','vault')
    # Pew blocks leave a 3 m central aisle, clear side aisles and transverse routes.
    for side in (-1,1):
        for row in range(19):
            y=-15.4+row*1.45
            if 0<y<2:continue
            x=side*3.25
            box('pew seat',(x,y,.47),(3.35,.43,.075),'timber','pews')
            box('pew back',(x,y-.21,.78),(3.35,.065,.64),'timber','pews')
            for dx in (-1.65,1.65):
                box('carved pew end',(x+dx,y,.47),(.085,.60,.90),'timber','pews')
                box('pew foot',(x+dx,y,.08),(.20,.62,.16),'timber','pews')
            box('pew kneeler',(x,y-.51,.18),(3.1,.16,.065),'timber','pews')
    # Altar remains on the same accessible floor, with no hidden collision step.
    box('altar base',(0,23.6,.10),(3.8,1.55,.20),'stone','altar')
    box('altar body',(0,23.6,.63),(3.2,1.15,1.06),'stone','altar')
    box('altar top',(0,23.6,1.22),(3.8,1.55,.13),'stone','altar')
    cross(0,26.9,2.1,2.5)
    for x in (-1.35,1.35):
        C.rod('altar candlestick',(x,23.6,1.29),(x,23.6,1.88),.045,'bronze','altar')
        box('altar candle',(x,23.6,2.02),(.065,.065,.28),'white','altar')
    for y in (-11,1,13):
        for x in (-4,4):
            C.rod('pendant suspension',(x,y,17),(x,y,8),.027,'hardware','lighting')
            for i in range(8):
                a=i*math.tau/8;b=(i+1)*math.tau/8
                C.beam('chandelier ring',(x+.48*math.cos(a),y+.48*math.sin(a),8),(x+.48*math.cos(b),y+.48*math.sin(b),8),.035,.04,'bronze','lighting')
                box('chandelier lamp',(x+.48*math.cos(a),y+.48*math.sin(a),8.17),(.07,.07,.30),'white','lighting')

def church():
    box('grounded nave floor',(0,-1.5,.02),(25,41,.04),'floor','foundation')
    front=C.Face((-12.5,-22,0),(1,0,0),(0,1,0),'front')
    facewall=front.wall('front gable lower',5.7,19.3,.04,16.2,.75)
    cut_profile(facewall,front,'open main portal',arch_outline(12.5,.04,3.8,3.8),.75)
    for width,offset in ((.20,-.1),(.40,-.28),(.65,-.48)):
        arch_frame(front,'recessed main archivolt',12.5,.04,3.8,3.8,width,offset,offset+.22)
    record_opening(front,'main accessible entrance',12.5,.04,3.8,3.8,.75)
    rose(facewall,front,12.5,12.5,2.9)
    # The bell tower owns the left front face; no duplicate buried lancet.
    for poly,u in (([(19.3,.04),(25,.04),(25,8.7),(19.3,12)],21.2),):
        end=front.panel('front aisle end',poly,0,.75,'wall')
        end['rlasm_wall_carrier']=True
        arch_window(end,front,'front aisle lancet',u,2,1.7,3.25,.75)
    front.panel('front upper gable',[(5.7,16.2),(19.3,16.2),(12.5,23)],0,.75,'wall')
    # Open doors parked inside the jambs, outside the centre walking route.
    for x in (-1.87,1.87):
        box('open timber door leaf',(x,-20.95,1.74),(.11,1.85,3.40),'timber','entrance')
        for z in (.65,1.75,2.85):box('door panel',(x-math.copysign(.061,x),-20.95,z),(.025,1.60,.80),'trim','entrance')
    box('level entrance threshold',(0,-22.35,.02),(4.2,1.1,.04),'foundation','access')
    C.mesh('shallow entrance approach',[(-3.5,-27,0),(3.5,-27,0),(2.15,-22,.04),(-2.15,-22,.04),(-2.15,-22,0),(2.15,-22,0)],[(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2),(2,5,4,3)],'foundation','access')
    # Aisle walls and upper nave clerestory use physical cut openings.
    for side in (-1,1):
        face=C.Face((side*12.5,-22,0),(0,1,0),(-side,0,0),'aisle '+str(side))
        owner=face.wall('aisle masonry',7 if side==-1 else 0,41,.04,8.65,.60)
        upper=C.Face((side*6.5,-22,0),(0,1,0),(-side,0,0),'clerestory '+str(side))
        carrier=upper.wall('clerestory carrier',0,41,11.5,16.1,.48)
        for i in range(6):
            u=5+6*i
            if side==1 or i>0:arch_window(owner,face,'aisle bay '+str(i),u,1.8,2.7,3.5,.6)
            arch_window(carrier,upper,'clerestory bay '+str(i),u,12.5,1.9,1.2,.48)
        for y in (-22,-16,-10,-4,2,8,14,19):
            for z,height,width in ((1.2,2.4,1.3),(4.3,3.8,1.0),(7.5,2.6,.74)):
                box('buttress stage',(side*12.75,y,z),(width,1.05,height),'stone','buttress')
            pinnacle(side*12.8,y,8.8,.48)
        for y in (-18,-6,6,18):
            C.rod('rainwater pipe',(side*12.85,y,.08),(side*12.85,y,8.7),.075,'trim','drainage',10)
    # Rear side-aisle walls close the envelope; central apse stays connected.
    rear=C.Face((-12.5,19,0),(1,0,0),(0,-1,0),'rear')
    for lo,hi in ((0,4.5),(20.5,25)):
        wall=rear.wall('rear aisle end',lo,hi,.04,8.65,.6)
        arch_window(wall,rear,'rear aisle lancet',(lo+hi)/2,2.2,1.5,2.8,.6)
        height=lambda u:12-(abs(u-12.5)-6.7)*3.3/6.2
        rear.panel('rear aisle roof closure',[(lo,8.65),(hi,8.65),(hi,height(hi)),(lo,height(lo))],0,.6,'wall')
    rear.panel('rear nave upper gable',[(5.7,14.80),(19.3,14.80),(19.3,16.1),(12.5,23),(5.7,16.1)],0,.6,'wall')
    main_roof();apse();nave_structure();tower()

def cameras():
    target=(0,1,20)
    result=[dict(name=n,location=p,target=target,ortho_scale=72) for n,p in
        [('front',(0,-105,20)),('left_side',(-105,0,20)),('right_side',(105,0,20)),('rear',(0,105,20))]]
    result += [dict(name='front_corner',location=(67,-92,50),target=target),
        dict(name='aerial',location=(62,-88,94),target=(0,0,14)),
        dict(name='top',location=(0,0,135),target=(0,.001,0),ortho_scale=70),
        dict(name='rear_side',location=(-69,92,50),target=target)]
    result += [dict(name=n,location=p,target=t,whole=False,lens=l) for n,p,t,l in
        [('facade_close',(11,-42,13),(0,-22,10),40),('architecture_close',(-26,-40,31),(-10,-18,26),40),
         ('glass_close',(19,-12,6),(12.5,-11,5),44),('program_interior',(0,-18,1.7),(0,24,8),20),
         ('vault_interior',(1,-9,2),(0,8,18),18),('walk',(0,-32,1.7),(0,-21,7),24),
         ('entrance_access',(4,-29,2),(0,-19,1.6),28),('apse_interior',(3,15,1.7),(0,25,6),24)]]
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');p.add_argument('--resolution',type=int,default=1200)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=json.loads(a.lock.read_text())['entries'][0]
    entry=dict(source,directory='.',_reference_root=str(Path(source['sources'][0]['path']).parent),
        sources=[dict(s,original_path=s['path'],path='sources/'+Path(s['path']).name) for s in source['sources']])
    roster=cameras()
    manifest=dict(candidate=f'gothic-community-church-clay-v{a.version:03d}',method=C.METHOD,archetype_id=source['archetype_id'],variant_id=source['variant_id'],
        representation_kind='architectural_clay',camera_roster=roster,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=28,depth=55,height=44),floors=1,front='-Y',bottom_datum_m=0,
            measurement_basis='Original generated design references and plausible metric modules; not a surveyed church'),
        identity_contract=['One front-left square bell tower and octagonal spire','Rose window and open main portal on short front gable',
            'Six-bay nave, lower side aisles, continuous pointed vault, polygonal apse','Open central and side aisles; pews, altar and physical stained glazing'],
        hidden_view_assumptions=['Board lower-left side-entry projection conflicts with exterior front/oblique and is excluded; companion roof image governs topology',
            'Rear openings and detailed room layout are interpreted from the original generated design'],
        source_origin='Original AI design references generated with built-in image generation; not photographs of an existing building',
        limitations=['Architectural clay; no textured keeper claim','Tower is visual architecture and not a visitor climbing route',
            'Fixed authored dimensions; no height stretching','Runtime access and placement require browser evidence'])
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE.parent/'showcase_building_trio/build.py',HERE/'walking.py'])
    if out is None:return
    cams=C.setup(PALETTE,roster,a.resolution);C.fit=B.efficient_fit;C.bpy.context.scene.cycles.samples=20
    for role in ('stained_blue','stained_red','stained_gold','stained_green'):
        mat=C.MATS[role];bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Alpha'].default_value=.65
        bs.inputs['Transmission Weight'].default_value=.32;bs.inputs['Roughness'].default_value=.24;mat.surface_render_method='DITHERED'
    for y in (-14,-2,10,23):C.qa_room_light('sanctuary',(0,y,13),2000,7)
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.45,-.5);sun.data.energy=2.1;sun.data.angle=.18
    church()
    attach_church_walk(C,'gothic')
    C.deliver(out,manifest,cams)

if __name__=='__main__':main()
