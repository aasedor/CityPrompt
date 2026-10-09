"""Five source-locked native neighbourhood parks; finite offline candidates only.

Metres, Z-up, complete assembly ground ownership, fixed native programme.
The generated photographs are visual references, never substitutes for geometry.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent))
import scene as S
from build_showcase_parks import material, polygon, ribbon, edge
from mathutils import Vector

SPECS = {
    'picnic': dict(id='student_prairie_picnic_grove_v1', archetype='prairie_picnic_grove',
        slug='prairie-picnic-grove', title='Prairie Picnic Grove', dimensions_m=[40,52],
        programme='Two timber picnic shelters, communal tables, flowering prairie meadow and a continuous shaded walking loop'),
    'sensory': dict(id='student_sensory_wellness_garden_v1', archetype='sensory_wellness_garden',
        slug='sensory-wellness-garden', title='Sensory & Wellness Garden', dimensions_m=[36,46],
        programme='Continuous accessible concept walking loop, fragrant planting rooms, tactile raised herb beds and quiet shaded seating'),
    'skate': dict(id='student_urban_skate_plaza_v1', archetype='urban_skate_plaza',
        slug='urban-skate-plaza', title='Urban Skate Plaza', dimensions_m=[42,54],
        programme='A sculpted concrete bowl, flowing ramps, ledges and rails with a separate planted spectator walk'),
    'pump': dict(id='student_bicycle_pump_track_park_v1', archetype='bicycle_pump_track_park',
        slug='bicycle-pump-track-park', title='Bicycle Pump-Track Park', dimensions_m=[48,60],
        programme='A banked rolling asphalt circuit, separate beginner loop and shaded gathering terrace'),
    'sports': dict(id='student_neighbourhood_sports_green_v1', archetype='neighbourhood_sports_green',
        slug='neighbourhood-sports-green', title='Neighbourhood Sports Green', dimensions_m=[48,66],
        programme='Recreational small playing field with two goals, perimeter walking loop, fitness stations and shade seating'),
}
WALK_EXCLUSIONS=[]
PAD_EXCLUSIONS=[]


def planting_clear(x,y,margin=.28):
    if S.GROUND_SIZE:
        w,d=S.GROUND_SIZE
        if abs(x)>w/2-margin-.4 or abs(y)>d/2-margin-.4:return False
    for cx,cy,w,d in PAD_EXCLUSIONS:
        if abs(x-cx)<w/2+margin and abs(y-cy)<d/2+margin:return False
    for a,b,width in WALK_EXCLUSIONS:
        dx=b[0]-a[0];dy=b[1]-a[1];l2=dx*dx+dy*dy
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/l2))
        if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<width/2+margin:return False
    return True


def ellipse(rx, ry, x=0, y=0, n=128):
    return [(x+rx*math.cos(i*math.tau/n), y+ry*math.sin(i*math.tau/n)) for i in range(n+1)]


def path(points, width=2.6, routes=None):
    if math.dist(points[0],points[-1])<.00001:
        # Closed loops need cyclic tangents: open endpoint normals leave a seam wedge.
        ring=points[:-1];vs=[];n=len(ring)
        for i,p in enumerate(ring):
            a=ring[(i-1)%n];b=ring[(i+1)%n];dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy)
            vs.extend([(p[0]-dy/ll*width/2,p[1]+dx/ll*width/2,.009),(p[0]+dy/ll*width/2,p[1]-dx/ll*width/2,.009)])
        S.mesh('continuous closed pedestrian paving',vs,[(2*i,2*i+1,2*((i+1)%n)+1,2*((i+1)%n)) for i in range(n)],'paving')
    else:
        # Rectangular segment owners overlap by 2 mm at bends and endpoint probes.
        # A single averaged normal narrows an L-turn, despite a constant-width recipe.
        for a,b in zip(points,points[1:]):
            dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy)
            ribbon('continuous pedestrian paving',[(a[0]-.002*dx/ll,a[1]-.002*dy/ll),(b[0]+.002*dx/ll,b[1]+.002*dy/ll)],width,'paving',.009)
    WALK_EXCLUSIONS.extend((a,b,width) for a,b in zip(points,points[1:]))
    if routes is not None:
        routes.extend(dict(a=list(a),b=list(b),width=width*.90) for a,b in zip(points,points[1:]))


def slab(x,y,w,d,mat='paving',top=.008):
    PAD_EXCLUSIONS.append((x,y,w,d))
    S.box('flush '+mat+' terrace',(x,y,top-.065),(w,d,.13),mat)
    if mat=='paving':
        for i in range(1,int(w/1.2)):
            xx=x-w/2+i*1.2;S.line((xx,y-d/2),(xx,y+d/2),.008,'edge',top+.001)
        for i in range(1,int(d/.8)):
            yy=y-d/2+i*.8;S.line((x-w/2,yy),(x+w/2,yy),.008,'edge',top+.001)


def base(w,d):
    S.ground(w,d,[])
    S.box('native continuous soft landscape',(0,0,-.071),(w,d,.12),'grass')


def prairie_patch(cx,cy,rx,ry,count,seed,height=.65,flower=True):
    """Authored elliptical drift: bent narrow blades, stems and actual petal disks."""
    rng=random.Random(seed);batches={m:([],[]) for m in ('grassleaf','straw','violet','cream')}
    for i in range(count):
        a=rng.random()*math.tau;rr=math.sqrt(rng.random());x=cx+rx*rr*math.cos(a);y=cy+ry*rr*math.sin(a)
        if not planting_clear(x,y,.42):continue
        h=height*rng.uniform(.55,1.1)
        for j in range(10):
            angle=rng.random()*math.tau;lean=rng.uniform(.12,.38);vs,fs=batches['grassleaf' if j%3 else 'straw'];n=len(vs)
            for k in range(6):
                t=k/5;wid=.033*(1-t)+.001;off=lean*t*t
                for side in (-1,1):vs.append((x+off*math.cos(angle)+side*wid*math.sin(angle),y+off*math.sin(angle)-side*wid*math.cos(angle),h*t))
            fs.extend((n+k*2,n+k*2+1,n+k*2+3,n+k*2+2) for k in range(5))
        if flower and i%3==0:
            vs,fs=batches['violet' if i%2 else 'cream']
            for j in range(4):
                xx=x+.10*math.cos(j*2);yy=y+.10*math.sin(j*2);z=h*.85+j*.04;n=len(vs);vs.append((xx,yy,z+.022))
                for k in range(10):
                    a=k*math.tau/10;vs.append((xx+.07*math.cos(a),yy+.07*math.sin(a),z))
                fs.extend((n,n+1+k,n+1+(k+1)%10) for k in range(10))
    for m,(vs,fs) in batches.items():
        if vs:S.mesh('living prairie drift '+m,vs,fs,m)


def shelter(x,y,w=6,d=7):
    before=set(S.bpy.context.scene.objects)
    for dx in (-w/2+.25,w/2-.25):
        for dy in (-d/2+.35,d/2-.35):
            S.box('galvanized post shoe',(x+dx,y+dy,.10),(.25,.25,.20),'metal')
            S.box('timber shelter post',(x+dx,y+dy,1.5),(.19,.19,2.9),'timber')
            for side in (-1,1):
                if side==(-1 if dx>0 else 1):S.beam('shelter diagonal brace',(x+dx,y+dy,2.05),(x+dx+side*.78,y+dy,2.90),.065,'timber',4)
    for dy in (-d/2+.35,d/2-.35):
        S.box('shelter gable tie',(x,y+dy,2.86),(w,.16,.20),'timber')
        S.beam('king post',(x,y+dy,2.9),(x,y+dy,4.03),.07,'timber',4)
        for side in (-1,1):S.beam('gable truss',(x+side*w/2,y+dy,2.92),(x,y+dy,4.10),.09,'timber',4)
    for side in (-1,1):
        vs=[(x,y-d/2-.3,4.16),(x+side*(w/2+.3),y-d/2-.3,2.95),(x+side*(w/2+.3),y+d/2+.3,2.95),(x,y+d/2+.3,4.16)]
        obj=S.mesh('standing seam shelter roof',vs,[(0,1,2,3)],'roof')
        mod=obj.modifiers.new('physical roof thickness','SOLIDIFY');mod.thickness=.08
        S.bpy.context.view_layer.objects.active=obj;S.bpy.ops.object.modifier_apply(modifier=mod.name)
        for j in range(20):
            yy=y-d/2-.28+j*(d+.56)/19
            S.beam('fine standing seam',(x,yy,4.18),(x+side*(w/2+.3),yy,2.98),.015,'roof',5)
    key='gable-picnic-shelter'
    if key not in S.RIGID:S.RIGID[key]=(list(set(S.bpy.context.scene.objects)-before),x,y)
    S.PLACEMENTS.append(dict(kind=key,x=x,y=y,z=0,yaw=0,scale=1))


def soft_tree(x,y,i,scale=1):
    S.kit('shade_tree',x,y,0,i*.9,scale)
    prairie_patch(x,y,1.5,1.4,17,110+i,.48,True)


def picnic(r):
    base(40,52);routes=[]
    path(ellipse(9.7,17.7),2.8,routes)
    path([(0,-26),(0,-17.5)],3.0,routes)
    path([(0,17.5),(0,26)],2.6,routes)
    for side in (-1,1):
        for yy in (-13.5,13.5):
            slab(side*9.4,yy,3.4,3.2)
            path([(side*6.1,yy),(side*8.3,yy)],2.0,routes)
            S.kit('bench',side*9.8,yy,0,side*math.pi/2)
    for side in (-1,1):
        x=side*13.1;slab(x,0,8.2,9.6);shelter(x,0,6,7)
        for yy in (-2.35,2.35):S.kit('picnic_table',x,yy,.01,math.pi/2)
        path([(side*9.2,0),(side*13.1,0)],2.5,routes)
        for yy in (-7.1,7.1):
            prairie_patch(x,yy,3.8,1.65,270,round(yy*10+200+side),.85)
            for j in range(5):
                if planting_clear(x-2.5+j*1.25,yy,.75):S.kit('flowering_perennial',x-2.5+j*1.25,yy,0,j,.85)
        for yy in (-15.5,15.5):soft_tree(side*15.7,yy,int(yy+30+side),1.15)
        soft_tree(side*8,22,45+side,1.05)
        soft_tree(side*8,-22,48+side,1.05)
        for i in range(7):
            a=(-.9+i*.30) if side==1 else math.pi-.9+i*.30
            prairie_patch(12.4*math.cos(a),20.3*math.sin(a),1.35,1.45,85,800+i+side*20,.70)
    # Three broad interlocking meadow drifts provide a clear focal landscape.
    for i,(x,y,rx,ry) in enumerate([(0,-8,6.5,6.3),(-1,3,6.7,7.0),(1,11,4.5,3.6)]):
        prairie_patch(x,y,rx,ry,1300,200+i,.95)
    for i in range(32):
        a=i*2.399;rr=math.sqrt((i+.5)/32)
        x=rr*6.7*math.cos(a);y=rr*13.2*math.sin(a)
        S.kit('flowering_perennial' if i%3 else 'meadow_grass',x,y,0,i,.90)
    for i,(x,y) in enumerate([(-4,-10),(3,-6),(-4,2),(4,5),(0,11)]):
        S.kit('flowering_perennial',x,y,0,i,1.0)
    S.kit('bin',2.4,-22,0);S.kit('bike_rack',-3.4,-23,0)
    slab(-2.7,-23,3.7,2);slab(1.9,-22,2.3,1.3)
    r.update(clear_routes=routes,reference_observations=['Two open gabled timber shelters flanking an oval meadow loop','Communal tables, pale entry promenade, mature edge trees and layered flowering prairie margins'],adaptations=['Native footprint 40 x 52 m; shelter roof uses restrained standing seams instead of photograph shingles. Eight shade trees preserve clear canopy containment. No surrounding street/buildings are baked into the asset.'])


def rounded_rectangle(hx,hy,radius=4,x=0,y=0):
    pts=[]
    for cx,cy,start in [(hx-radius,hy-radius,0),(-hx+radius,hy-radius,90),(-hx+radius,-hy+radius,180),(hx-radius,-hy+radius,270)]:
        for i in range(17):
            a=math.radians(start+i*90/16);pts.append((x+cx+radius*math.cos(a),y+cy+radius*math.sin(a)))
    return pts+[pts[0]]


def curved_bench(x,y,radius=2.2,start=0,end=math.pi):
    for j in range(30):
        a=start+(end-start)*(j+.5)/30
        obj=S.box('curved seat individual radial slat',(0,0,0),(.47,.12,.065),'timber')
        obj.location=(x+radius*math.cos(a),y+radius*math.sin(a),.48);obj.rotation_euler.z=a
        obj=S.box('curved back individual slat',(0,0,0),(.055,.12,.50),'timber')
        obj.location=(x+(radius+.22)*math.cos(a),y+(radius+.22)*math.sin(a),.76);obj.rotation_euler.z=a
    for j in range(5):
        a=start+(end-start)*(j+.2)/4.4
        for rr in (radius-.18,radius+.18):S.beam('curved bench anchored leg',(x+rr*math.cos(a),y+rr*math.sin(a),0),(x+rr*math.cos(a),y+rr*math.sin(a),.46),.033,'metal',8)


def sensory(r):
    base(36,46);routes=[]
    path(ellipse(11.3,15.6),2.6,routes)
    path([(0,-23),(0,23)],3.0,routes)
    path([(-11.3,0),(11.3,0)],2.4,routes)
    for side in (-1,1):
        # Two quiet pavilions branch from the loop without narrowing it.
        slab(side*9,17,7,5.8)
        path([(side*7,12.3),(side*9,15),(side*9,16.3)],2.4,routes)
        S.pergola(side*9,17,5.5,4)
        S.kit('bench',side*9,18,0,math.pi)
        S.kit('bench',side*10.4,16.5,0,side*math.pi/2)
        slab(side*6.5,-2.7,4.8,5.0)
        curved_bench(side*6.5,-4.3,1.65,math.pi*.13,math.pi*.87)
        # Four distinct fragrant gardens leave a central open lawn and routes.
        for j,yy in enumerate((-9,8.7)):
            prairie_patch(side*5.6,yy,3.3,4.1,630,530+j+side*10,.70 if j else .52)
            for k in range(10):
                a=k*2.4;xx=side*5.6+math.cos(a)*2.3;yyy=yy+math.sin(a)*2.7
                if planting_clear(xx,yyy,.70):S.kit('flowering_perennial' if k%3 else 'meadow_grass',xx,yyy,0,k,.90)
        # Raised tactile herbs, with plank walls and clear wheelchair-side apron.
        slab(side*6.3,-19.2,7.8,3.4)
        path([(0,-18.2),(side*6.3,-18.2)],2.0,routes)
        for xx in (side*4.3,side*8.2):
            S.box('raised aromatic herb soil',(xx,-20.0,.28),(2.7,1.35,.56),'soil')
            edge('raised tactile herb timber',[(xx-1.4,-20.72),(xx+1.4,-20.72),(xx+1.4,-19.28),(xx-1.4,-19.28)],'timber',.63,.09,0,True)
            for k in range(4):S.kit('flowering_perennial',xx-.90+k*.60,-20,.57,k,.48)
        for j,yy in enumerate((-12,0,11)):soft_tree(side*14.5,yy,70+j+side*5,.95)
        soft_tree(side*3.8,19.5,85+side,.9)
        for j in range(7):prairie_patch(side*14.6,-17+j*5.0,1.65,1.8,90,920+j+side*10,.75)
        for j in range(6):
            xx=side*(3+j*2.0)
            prairie_patch(xx,-22,1.15,.70,45,1010+j+side*10,.50)
    S.kit('bin',3.0,-17.0,0);slab(3.0,-17.0,1.2,1.2)
    r.update(clear_routes=routes,reference_observations=['Oval continuous loop and crossing promenade','Four fragrant planting rooms and open lawn','Two rear pergolas, curved timber seating and front raised herb beds'],adaptations=['Plant forms are conceptual perennial/herb types, not a verified botanical planting schedule. Native routes are level; accessibility compliance is not certified.'])


def ring_surface(name,inner,outer,zinner,zouter,mat):
    verts=[];n=len(inner)
    for i in range(n):verts.extend([(*inner[i],zinner),(*outer[i],zouter)])
    obj=S.mesh(name,verts,[(2*i+1,2*((i+1)%n)+1,2*((i+1)%n),2*i) for i in range(n)],mat)
    return obj


def bowl(x,y,rx,ry,depth=1.65):
    before=set(S.bpy.context.scene.objects);n=144;steps=22;vs=[];fs=[]
    # Flat low floor rises through a continuous quarter-circle transition.
    for j in range(steps+1):
        t=j/steps;factor=.48+.52*math.sin(t*math.pi/2);z=.021+depth*(1-math.cos(t*math.pi/2))
        for i in range(n):
            a=i*math.tau/n;vs.append((x+rx*factor*math.cos(a),y+ry*factor*math.sin(a),z))
    for j in range(steps):
        for i in range(n):fs.append(((j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n,j*n+i))
    obj=S.mesh('continuous concave concrete bowl transition',vs,fs,'concrete')
    for f in obj.data.polygons:f.use_smooth=True
    polygon('bowl low flat floor',ellipse(rx*.48,ry*.48,x,y,n)[:-1],'concrete',.021)
    inner=ellipse(rx,ry,x,y,n)[:-1];outer=ellipse(rx+1.7,ry+1.7,x,y,n)[:-1]
    ring_surface('bowl rim deck',inner,outer,depth+.021,depth+.021,'concrete')
    ring_surface('bowl physical outside wall',outer,outer,.004,depth+.021,'concrete')
    for a,b in zip(inner,inner[1:]+inner[:1]):S.beam('continuous metal bowl coping',(*a,depth+.046),(*b,depth+.046),.035,'metal',8)
    key='raised-skate-bowl'
    S.RIGID[key]=(list(set(S.bpy.context.scene.objects)-before),x,y);S.PLACEMENTS.append(dict(kind=key,x=x,y=y,z=0,yaw=0,scale=1))


def quarter_pipe(x,y,side=1):
    vs=[];fs=[];width=4.8;h=1.35;run=2.7;n=28
    for i in range(n+1):
        t=i/n;xx=x+side*run*math.sin(t*math.pi/2);z=.023+h*(1-math.cos(t*math.pi/2))
        vs.extend([(xx,y-width/2,z),(xx,y+width/2,z)])
    fs.extend((2*i,2*i+1,2*i+3,2*i+2) for i in range(n))
    obj=S.mesh('smooth quarter pipe riding face',vs,fs,'concrete')
    for face in obj.data.polygons:face.use_smooth=True
    for sign in (-1,1):
        pts=[vs[i*2+(1 if sign==1 else 0)] for i in range(n+1)]+[(x+side*run,y+sign*width/2,.01),(x,y+sign*width/2,.01)]
        S.mesh('quarter pipe solid side',pts,[tuple(range(len(pts)))],'concrete')
    S.box('quarter pipe rear deck',(x+side*(run+.4),y,h/2+.021),(.8,width,h),'concrete')
    S.beam('quarter pipe coping',(x+side*run,y-width/2,h+.05),(x+side*run,y+width/2,h+.05),.038,'metal',10)


def skate(r):
    base(42,54);routes=[]
    path(rounded_rectangle(15.9,22.2,5),2.6,routes)
    path([(0,-27),(0,-20)],3.0,routes)
    slab(0,-10,26,19,'concrete',.014)
    bowl(0,8.7,9.1,9.8,1.65)
    # Two rideable quarter pipes and restrained street obstacles.
    quarter_pipe(-8,-9,-1);quarter_pipe(8,-9,1)
    S.box('low grind ledge',(-6,-16,.24),(4,.55,.46),'concrete')
    for yy in (-16.3,-15.7):S.beam('steel ledge angle',(-8,yy,.48),(-4,yy,.48),.022,'metal',6)
    for xx in (1,3,5):S.beam('grind rail grounded leg',(xx,-16,.014),(xx,-16,.48),.027,'metal',8)
    S.beam('round grind rail',(1,-16,.50),(5,-16,.50),.035,'metal',12)
    S.mesh('low double bank funbox',[(-2,-9,.016),(2,-9,.016),(-1,-7,.62),(1,-7,.62),(-1,-5,.62),(1,-5,.62),(-2,-3,.016),(2,-3,.016)],[(0,1,3,2),(2,3,5,4),(4,5,7,6),(0,2,4,6),(1,7,5,3)],'concrete')
    # Banked access to raised rim, kept separate from the perimeter walk.
    S.mesh('bowl deck access bank',[(10.7,-4,.014),(13.5,-4,.014),(10.7,8.7,1.671),(13.5,8.7,1.671),(10.7,8.7,.014),(13.5,8.7,.014)],[(0,1,3,2),(0,2,4),(1,5,3),(2,3,5,4)],'concrete')
    # A real 2.3 m landing crosses the tangent and overlaps the curved rim deck.
    S.box('positive width bowl deck landing',(11.55,7.7,.843),(3.9,2.3,1.656),'concrete')
    # Shade gathering terrace is directly on the arrival walk.
    slab(7.5,-22.0,9.6,6.4);S.pergola(8.2,-22.5,5.3,3.7);S.kit('bench',8.2,-23.2,0,math.pi)
    path([(0,-22),(6.2,-22)],2.4,routes)
    for side in (-1,1):
        for i,yy in enumerate((-14,0,15)):
            S.kit('ornamental_tree',side*18.3,yy,0,i,.82)
            prairie_patch(side*18.3,yy,1.6,3.6,130,145+i+side*7,.70)
        for yy in (-4,11):
            slab(side*14.2,yy,2.9,3.6);S.kit('bench',side*13.8,yy,0,-side*math.pi/2)
        for j in range(5):prairie_patch(side*(3+j*2.6),-25,1.2,1.1,95,710+j+side*9,.70)
    for side in (-1,1):
        prairie_patch(side*14,-9,.45,7.0,260,1820+side,.70)
        prairie_patch(side*8,24.3,5.0,.80,300,1840+side,.68)
    S.kit('bike_rack',-4,-24.3,0);slab(-3.8,-24.3,4,3.0);S.kit('bin',2.4,-24.3,0);slab(2.4,-24.3,1.4,1.4)
    r.update(clear_routes=routes,reference_observations=['Concrete bowl with continuous curved transition and coping','Two quarter pipes, grind ledge and rail','Separate planted spectator loop and entrance pergola'],adaptations=['Bowl is a 1.65 m raised native module with banked access; no terrain excavation is required. Recreational concept riding geometry is not a certified skatepark engineering design. Pedestrian verification covers the separate level spectator routes, not riding manoeuvres.'])


def pump_point(x,y,rx,ry,width,height,rollers,a,u):
    cx=x+rx*math.cos(a);cy=y+ry*math.sin(a);dx=-rx*math.sin(a);dy=ry*math.cos(a);ll=math.hypot(dx,dy)
    bank=abs(math.sin(a))**5;roller=height*(.5+.5*math.cos(a*rollers))*(1-bank*.85)
    return (cx+dy/ll*(u-.5)*width,cy-dx/ll*(u-.5)*width,.045+roller+bank*(.08+height*1.7*u*u))


def pump_loop(x,y,rx,ry,width,height,rollers,key,entry_index):
    before=set(S.bpy.context.scene.objects);n=240;bands=12;vs=[];fs=[]
    for i in range(n):
        a=i*math.tau/n;cx=x+rx*math.cos(a);cy=y+ry*math.sin(a)
        dx=-rx*math.sin(a);dy=ry*math.cos(a);ll=math.hypot(dx,dy);nx=dy/ll;ny=-dx/ll
        bank=abs(math.sin(a))**5
        roller=height*(.5+.5*math.cos(a*rollers))*(1-bank*.85)
        for j in range(bands+1):
            u=j/bands;off=(u-.5)*width
            z=.045+roller+bank*(.08+height*1.7*u*u)
            vs.append((cx+nx*off,cy+ny*off,z))
    for i in range(n):
        for j in range(bands):
            a=i*(bands+1)+j;b=((i+1)%n)*(bands+1)+j;fs.append((a+1,b+1,b,a))
    obj=S.mesh('flowing banked rolling asphalt circuit',vs,fs,'asphalt')
    for f in obj.data.polygons:f.use_smooth=True
    # Grass shoulders reach the exact edge of every roller, avoiding floating track.
    for outer in (False,True):
        verts=[];faces=[];idx=bands if outer else 0
        for i in range(n):
            p=vs[i*(bands+1)+idx];a=i*math.tau/n
            shift=1.0 if outer else -1.0;verts.extend([p,(p[0]+shift*math.cos(a),p[1]+shift*math.sin(a),-.009)])
        faces=[(2*i,2*((i+1)%n),2*((i+1)%n)+1,2*i+1) for i in range(n) if not (outer and entry_index-4<=i<entry_index+4)]
        if outer:faces=[tuple(reversed(f)) for f in faces]
        o=S.mesh('supported grassy track shoulder',verts,faces,'grass')
        for f in o.data.polygons:f.use_smooth=True
    S.RIGID[key]=(list(set(S.bpy.context.scene.objects)-before),x,y);S.PLACEMENTS.append(dict(kind=key,x=x,y=y,z=0,yaw=0,scale=1))


def pump_ingress(start,params,entry_index):
    """Join the exact nine outer-edge vertices, with turf shoulders cut at the mouth."""
    vs=[];fs=[];nx=8;ny=24;targets=[]
    for j in range(nx+1):targets.append(pump_point(*params,(entry_index-4+j)*math.tau/240,1))
    # Angle increases across the track mouth; preserve that orientation at entry.
    direction=Vector(targets[-1])-Vector(targets[0]);direction.z=0;direction.normalize()
    for i in range(ny+1):
        t=i/ny
        for j,end in enumerate(targets):
            p=(start[0]+direction.x*(j/nx-.5)*2.8,start[1]+direction.y*(j/nx-.5)*2.8,.014)
            vs.append(tuple(p[k]*(1-t)+end[k]*t for k in range(3)))
    for i in range(ny):
        for j in range(nx):
            a=i*(nx+1)+j;fs.append((a,a+1,a+nx+2,a+nx+1))
    obj=S.mesh('height matched cycle circuit entrance',vs,fs,'asphalt')
    for face in obj.data.polygons:face.use_smooth=True
    for j in (0,nx):
        vertices=[]
        for i in range(ny+1):
            p=vs[i*(nx+1)+j];vertices.extend([p,(p[0],p[1],-.01)])
        S.mesh('cycle ingress solid shoulder',vertices,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(ny)],'grass')
    return [list(vs[i*(nx+1)+j]) for i in range(ny+1) for j in (1,4,7)]


def pump(r):
    base(48,60);routes=[]
    path(rounded_rectangle(19.6,25.3,5),2.6,routes)
    path([(0,-30),(0,-23)],3.0,routes)
    pump_loop(0,7.5,14.5,11.4,3.2,.65,10,'main-banked-pump-circuit',200)
    pump_loop(-9,-15,6.8,4.7,2.1,.18,8,'beginner-pump-loop',180)
    slab(8.4,-18.3,12.5,8.0);S.pergola(9,-19.1,6.2,4.4)
    S.kit('bench',9,-20.4,0,math.pi);S.kit('bench',11.5,-18.7,0,math.pi/2)
    S.kit('bike_rack',4.8,-18.5,0);S.kit('bike_rack',4.8,-16.8,0)
    path([(0,-25.3),(8.4,-25.3),(8.4,-21)],2.7,routes)
    # Deliberate cyclist ingress tongues to both native circuits.
    ride_checks=pump_ingress((8.4,-14.5),(0,7.5,14.5,11.4,3.2,.65,10),200)
    ribbon('beginner entry across walking edge',[(-9,-26.5),(-9,-23.8)],2.8,'asphalt',.014)
    ride_checks+=pump_ingress((-9,-24.0),(-9,-15,6.8,4.7,2.1,.18,8),180)
    for i,(xx,yy) in enumerate([(-21.7,-18),(-21.7,-4),(-21.7,13),(21.7,-4),(21.7,13),(-13,27.5),(13,27.5),(-12,-27.5),(14,-27.5)]):
        # Edge trees use narrow ornamental canopies where the path is close.
        S.kit('ornamental_tree',xx,yy,0,i,.8)
    for side in (-1,1):
        for j in range(7):prairie_patch(side*22,-20+j*6.6,1.1,2.0,80,1100+j+side*15,.8)
        for j in range(6):prairie_patch(side*(3+j*2.6),-27.3,1.2,1.1,75,1200+j+side*15,.75)
    # Planted central island carries restrained low drifts, away from riding shoulders.
    for i,(xx,yy) in enumerate([(-7,7),(0,9),(7,7),(-3,3),(3,3)]):
        prairie_patch(xx,yy,2.3,1.8,160,1280+i,.85)
        S.kit('flowering_perennial',xx,yy,0,i,.95)
    S.kit('bin',2.5,-26,0);slab(2.5,-26,1.4,1.4)
    r.update(clear_routes=routes,ride_ingress_checks=ride_checks,reference_observations=['Main closed rolling circuit with banked ends and planted island','Separate low beginner circuit','Front-right timber shade gathering and bicycle racks','Independent perimeter pedestrian walk'],adaptations=['Native circuit design is a recreational concept rather than a construction-certified track. The pedestrian loop remains level and outside both riding envelopes; cyclist ingress is separately surfaced.'])


def goal(x,y,side):
    before=set(S.bpy.context.scene.objects);w=3.7;h=1.85;depth=1.25
    for xx in (-w/2,w/2):
        S.beam('goal upright',(x+xx,y,.012),(x+xx,y,h),.035,'paint',12)
        S.beam('goal rear brace',(x+xx,y,h),(x+xx,y+side*depth,.06),.025,'paint',10)
        S.beam('goal base rail',(x+xx,y,.04),(x+xx,y+side*depth,.04),.025,'paint',10)
    S.beam('goal crossbar',(x-w/2,y,h),(x+w/2,y,h),.035,'paint',12)
    for i in range(26):
        xx=x-w/2+i*w/25;S.beam('goal net longitudinal',(xx,y,h),(xx,y+side*depth,.055),.005,'net',4)
    for j in range(16):
        t=j/15;yy=y+side*depth*t;zz=h*(1-t)+.055*t
        S.beam('goal net cross cord',(x-w/2,yy,zz),(x+w/2,yy,zz),.005,'net',4)
        for xx in (-w/2,w/2):S.beam('goal side net cord',(x+xx,yy,.055),(x+xx,yy,zz),.005,'net',4)
    key=f'recreational-goal-{side}'
    S.RIGID[key]=(list(set(S.bpy.context.scene.objects)-before),x,y);S.PLACEMENTS.append(dict(kind=key,x=x,y=y,z=0,yaw=0,scale=1))


def fitness(x,y,kind):
    if kind=='bars':
        for dx,h in [(-1.15,2.2),(0,1.9),(1.15,1.6)]:
            for dy in (-.55,.55):S.beam('fitness grounded steel post',(x+dx,y+dy,.02),(x+dx,y+dy,h),.045,'metal',12)
            S.beam('pullup exercise bar',(x+dx,y-.55,h),(x+dx,y+.55,h),.034,'metal',12)
    elif kind=='parallel':
        for dx in (-.36,.36):
            for dy in (-1,1):S.beam('parallel bar leg',(x+dx,y+dy,.02),(x+dx,y+dy,1.15),.04,'metal',12)
            S.beam('parallel handrail',(x+dx,y-1.25,1.15),(x+dx,y+1.25,1.15),.037,'metal',12)
    elif kind=='steps':
        for i in range(3):
            h=.22+i*.12;S.box('step exercise platform',(x+(i-1)*.7,y,h/2),(.48,.65,h),'timber')
    else:
        for i in range(12):
            yy=y-1.1+i*.2;z=.35+(i/11)*.25;S.box('inclined situp bench slat',(x,yy,z),(.65,.18,.045),'timber')
        for yy,h in [(y-.9,.37),(y+.9,.57)]:
            for xx in (x-.25,x+.25):S.beam('exercise bench leg',(xx,yy,.02),(xx,yy,h),.035,'metal',10)


def sports(r):
    base(48,66);routes=[]
    path(rounded_rectangle(17.6,25.7,3.2),2.6,routes)
    path([(0,-33),(0,-25.6)],3.0,routes)
    # Explicit recreational playing dimensions, with independent complete runoff.
    polygon('recreational playing turf',[(-13,-20),(13,-20),(13,20),(-13,20)],'field',.002)
    S.rectline(0,0,26,40,.075);S.line((-13,0),(13,0),.075);S.arc(0,0,3.6,width=.065)
    for side in (-1,1):
        goal(0,side*20,side)
        yy=side*16.7;S.rectline(0,yy,10,6.6,.065)
        # Equipment pads meet the perimeter walk; their devices leave route clear.
        slab(side*7.2,-28.0,9.6,4.8,'rubber',.003)
        path([(side*7.2,-25.7),(side*7.2,-27.0)],2.3,routes)
        fitness(side*5,-28.5,'bars' if side==-1 else 'parallel')
        fitness(side*9.7,-28.5,'steps' if side==-1 else 'bench')
        for j,yy in enumerate((-21,-7,8,22)):
            soft_tree(side*20.3,yy,1400+j+side*10,.88)
            prairie_patch(side*21.1,yy,1.5,2.8,95,1440+j+side*10,.70)
        for j in range(5):prairie_patch(side*(3.5+j*2.5),-31.8,1.3,.75,70,1500+j+side*10,.72)
        for yy in (-9,12):
            slab(side*19,yy,3.5,3.0);S.kit('bench',side*19.7,yy,0,-side*math.pi/2)
    # Rear corner shade pavilion avoids the complete playing/runoff reserve.
    slab(11.5,29,9,5.5);S.pergola(12,29,5.5,3.5);S.kit('picnic_table',12,29,0)
    path([(11.5,25.7),(11.5,27.5)],2.4,routes)
    S.kit('bin',2.4,-30.2,0);slab(2.4,-30.2,1.4,1.4)
    r.update(clear_routes=routes,playing_dimensions_m=[26,40],full_runoff_dimensions_m=[32,47],goal_dimensions_m=[3.7,1.85,1.25],reference_observations=['Small marked grass playing field with two netted goals','Separate perimeter walk and front paired exercise bays','Edge trees outside runoff and a side shade pavilion'],adaptations=['Deliberate small recreational field: 26 x 40 m, 3.7 x 1.85 m goals; no regulation competition-size claim. Exercise equipment is static concept geometry, not certified equipment.'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    r=dict(SPECS[a.kind]);source=a.reference_root/r['slug']/'variant_0.png';data=source.read_bytes();assert len(data)>10000
    r.update(source_references=[dict(role='front',path=str(source),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())],kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),runtime_status='NOT TESTED',terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,entrance=dict(x=0,y=-r['dimensions_m'][1]/2,widthM=3.0),generation_provider='built-in image_gen',reference_status='original generated conceptual photograph; not a real project')
    if a.output.exists():raise ValueError('Existing immutable candidate')
    if a.dry_run:print('DRY_RUN_PASS',r['id'],r['dimensions_m']);return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color,rough in [('joint',(.38,.37,.31),.9),('roof',(.19,.22,.21),.8),('grassleaf',(.23,.31,.10),.9),('straw',(.44,.39,.17),.9),('violet',(.40,.20,.38),.9),('cream',(.67,.61,.34),.9),('concrete',(.58,.57,.51),.85),('herb',(.25,.36,.19),.9),('field',(.19,.29,.09),.94),('rubber',(.14,.21,.18),.96)]:material(name,color,rough)
    globals()[a.kind](r)
    files=[Path(__file__),Path(S.__file__),Path(__file__).with_name('build_showcase_parks.py')]
    r['source_build_files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    for f in files:shutil.copy2(f,a.output/f.name)
    shutil.copy2(source,a.output/'variant_0.png')
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    w,d=r['dimensions_m'];S.deliver(a.output,r,[('aerial',(w*.8,-d*.90,max(w,d)*.95),(0,0,1),max(w,d)*1.4),('top',(0,0,100),(0,.001,0),max(w,d)*1.4),('detail',(w*.36,-d*.22,11),(w*.23,0,1),23)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=23
    for name,pos,target in [('walk',(0,-d/2+1.5,1.65),(0,0,1.65)),('programme_walk',(w*.18,-d*.20,1.65),(w*.32,0,1.6))]:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(a.output/'renders'/f'{name}.png');S.bpy.ops.render.render(write_still=True)
    r['runtime_contract']='Complete native assembly owns ground. Preserve native metric geometry; plot expansion adds surrounding landscape without stretching programme.'
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    print('READY_FOR_GEOMETRY_AND_INDEPENDENT_REVIEW',a.output,flush=True)


if __name__=='__main__':main()
