"""Finite original park concepts with walking geometry authored with the model.

Run in Blender. One candidate per invocation; output directories are immutable.
Walking polygons are the very same faces exported with material `walk_surface`.
No navigation is inferred from railings, plants, water or bounding boxes.
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
from build_showcase_parks import material, polygon, edge
from mathutils import Vector

SPECS = {
    'quarry': dict(id='student_quarry_garden_v1', archetype='student_quarry_garden',
        title='Quarry Garden', dimensions_m=[60, 68],
        programme='Three descending stone stair flights, planted quarry terraces, a reflective pool and a sheltered lower garden.'),
    'spiral': dict(id='student_spiral_lookout_v1', archetype='student_spiral_lookout',
        title='Spiral Lookout Park', dimensions_m=[64, 68],
        programme='A continuous rising spiral promenade, flowered earthwork, summit outlook and shaded entrance court.'),
    'cascade': dict(id='student_cascade_water_garden_v1', archetype='student_cascade_water_garden',
        title='Cascade Water Garden', dimensions_m=[54, 68],
        programme='Three water cascades, paired stone stairs, connected viewing terraces and a shaded upper garden.'),
}
WALK = []
ROUTES = []


def walk_quad(name, points):
    """Positive winding, metre coordinates, two triangles shared by GLB and nav."""
    p = [list(map(float, xyz)) for xyz in points]
    if (p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0]) < 0:
        p.reverse()
    S.mesh(name, p, [(0, 1, 2), (0, 2, 3)], 'walk_surface')
    WALK.extend([[p[i] for i in ids] for ids in [(0, 1, 2), (0, 2, 3)]])


def floor(name, x0, x1, y0, y1, z, holes=()):
    xs = sorted({x0, x1, *[max(x0, min(x1, h[i])) for h in holes for i in (0, 1)]})
    ys = sorted({y0, y1, *[max(y0, min(y1, h[i])) for h in holes for i in (2, 3)]})
    for a, b in zip(xs, xs[1:]):
        for c, d in zip(ys, ys[1:]):
            if any(h[0] < (a+b)/2 < h[1] and h[2] < (c+d)/2 < h[3] for h in holes):
                continue
            walk_quad(name, [(a, c, z), (b, c, z), (b, d, z), (a, d, z)])
    # Fine modular paving joints have no collision height.
    for i in range(math.ceil(x0/1.25), math.floor(x1/1.25)+1):
        x=i*1.25
        for a,b in zip(ys,ys[1:]):
            if not any(h[0] <= x <= h[1] and h[2] < (a+b)/2 < h[3] for h in holes):
                S.line((x,a),(x,b),.008,'joint',z+.001)
    for j in range(math.ceil(y0/.85), math.floor(y1/.85)+1):
        y=j*.85
        for a,b in zip(xs,xs[1:]):
            if not any(h[0] < (a+b)/2 < h[1] and h[2] <= y <= h[3] for h in holes):
                S.line((a,y),(b,y),.008,'joint',z+.001)


def solid_wall(name, a, b, bottom, top, width=.35):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    o=S.box(name,(0,0,0),(length,width,top-bottom),'stone')
    o.location=((a[0]+b[0])/2,(a[1]+b[1])/2,(bottom+top)/2)
    o.rotation_euler.z=math.atan2(dy,dx)
    # Courses and individually offset seams keep the pedestrian view legible.
    nx,ny=-dy/length,dx/length
    for k in range(1,max(1,round((top-bottom)/.26))):
        zz=bottom+k*.26
        for side in (-1,1):
            S.beam('stone bedding joint',(a[0]+nx*width*.502*side,a[1]+ny*width*.502*side,zz),
                   (b[0]+nx*width*.502*side,b[1]+ny*width*.502*side,zz),.008,'joint',4)
    for i in range(max(1,int(length/1.1))):
        t=(i+.5)/max(1,int(length/1.1))
        for side in (-1,1):
            x=a[0]+dx*t+nx*width*.502*side;y=a[1]+dy*t+ny*width*.502*side
            S.beam('stone vertical seam',(x,y,bottom+.025),(x,y,top-.02),.006,'joint',4)


def rail(points):
    """Outside the clear walking strip; continuous but never across an entry."""
    for a,b in zip(points,points[1:]):
        for height,radius in [(1.02,.032),(.52,.016)]:
            S.beam('slender bronze guard', (a[0],a[1],a[2]+height),(b[0],b[1],b[2]+height),radius,'metal',8)
    for p in points:
        S.beam('guard post',p,(p[0],p[1],p[2]+1.02),.026,'metal',8)
        S.box('guard shoe',(p[0],p[1],p[2]+.025),(.11,.11,.05),'metal')


def stairs(x, y0, y1, z0, z1, width=4.4, open_landing=False):
    count=round(abs(z1-z0)/.15)
    run=(y1-y0-1.5)/count
    for i in range(count):
        a=y0+i*run;b=y0+(i+1)*run;z=z0+(z1-z0)*(i+1)/count
        floor('broad stone tread',x-width/2,x+width/2,a,b,z)
        bottom=min(z0,z1)-.16
        S.box('solid stair support',(x,(a+b)/2,(z+bottom)/2-.004),(width,b-a,z-bottom-.008),'stone')
        S.box('stair riser',(x,a,(z+z0+(z1-z0)*i/count)/2),(width,.025,abs(z1-z0)/count),'stone')
        S.line((x-width/2+.05,a+.04),(x+width/2-.05,a+.04),.025,'nosing',z+.002)
    floor('stair rest landing',x-width/2,x+width/2,y1-1.5,y1,z1)
    bottom=min(z0,z1)-.16
    S.box('solid landing support',(x,y1-.75,(z1+bottom)/2-.004),(width,1.5,z1-bottom-.008),'stone')
    for side in (-1,1):
        xx=x+side*(width/2+.15)
        points=[(xx,y0,z0),(xx,y1-1.5,z1)]
        if not open_landing: points.append((xx,y1,z1))
        rail(points)
    return [(x,y0,z0),(x,y1-1.5,z1),(x,y1,z1)]


def planting_rect(x0,x1,y0,y1,z,seed,spacing=1):
    S.box('recessed planting soil',((x0+x1)/2,(y0+y1)/2,z-.035),(x1-x0,y1-y0,.07),'soil')
    edge('stone bed margin',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],'stone',.09,.14,z,True)
    rng=random.Random(seed)
    for i in range(max(1,int((x1-x0)/(1.05*spacing)))):
        for j in range(max(1,int((y1-y0)/(1.1*spacing)))):
            xx=x0+.5+i*1.05*spacing;yy=y0+.5+j*1.1*spacing
            if xx>x1-.4 or yy>y1-.4:continue
            kind=['flowering_perennial','meadow_grass','flowering_perennial'][(i//3+j//3+seed)%3]
            S.kit(kind,xx,yy,z,rng.random()*math.tau,1.38 if kind=='flowering_perennial' else 1.18)


def seat(x,y,z,yaw=0):
    S.kit('bench',x,y,z,yaw)


def quarry(r):
    # Ground-level rim and three progressively lower inhabited terraces.
    S.box('continuous quarry foundation',(0,0,-4.78),(60,68,.24),'stone')
    floor('entrance apron',-30,30,-34,-30,0)
    floor('rear rim',-30,30,30,34,0)
    floor('west rim',-30,-28,-30,30,0);floor('east rim',28,30,-30,30,0)
    rings=[(28,30,24,26,0),(24,26,19,20,-1.5),(19,20,14,14,-3)]
    beds=[]
    for idx,(ox,oy,ix,iy,z) in enumerate(rings):
        # Long planted rooms leave 2.8 m clear paths on the terrace's inner side.
        bx=ox-1.05
        bh=[(-ox+.35,-ox+1.7,-oy+7,oy-7),(ox-1.7,ox-.35,-oy+7,oy-7),(-ix+4,ix-4,oy-1.7,oy-.35)]
        holes=[(-ix,ix,-iy,iy),*bh]
        if idx==0:
            for x in (-16,16):
                h=(x-2.8,x+2.8,-29.7,-27.9);holes.append(h);planting_rect(*h,0,60+round(x))
        if idx:holes.append((-2.2,2.2,-oy,-iy))
        floor('quarry terrace',-ox,ox,-oy,oy,z,holes)
        for j,h in enumerate(bh):planting_rect(*h,z,idx*11+j)
        # Retaining faces enclose the quarry, with an actual stair opening south.
        bottom=z-1.5
        for a,b in [((-ix,-iy),(-ix,iy)),((-ix,iy),(ix,iy)),((ix,iy),(ix,-iy)),((-ix,-iy),(-2.35,-iy)),((2.35,-iy),(ix,-iy))]:
            solid_wall('quarry retaining courses',a,b,bottom,z)
        # Guard the exposed inner rim; keep stair mouth open.
        for pts in [[(-ix-.23,-iy,z),(-ix-.23,iy+.23,z),(ix+.23,iy+.23,z),(ix+.23,-iy,z)],
                    [(-ix,-iy-.23,z),(-2.4,-iy-.23,z)],[(2.4,-iy-.23,z),(ix,-iy-.23,z)]]:
            dense=[]
            for a,b in zip(pts,pts[1:]):
                n=max(1,math.ceil(math.dist(a,b)/2));dense.extend(tuple(a[k]+(b[k]-a[k])*i/n for k in range(3)) for i in range(n))
            rail(dense+[pts[-1]])
    garden_beds=[(-12,-6,-1,10),(-12,-4,-12,-5),(4,12,-12,-5),(-12,12,12,13.8)]
    bottom_holes=[(-2.2,2.2,-14,-8),(3.8,11,-3,8),*garden_beds]
    floor('lower quarry court',-14,14,-14,14,-4.5,bottom_holes)
    for i,h in enumerate(garden_beds):planting_rect(*h,-4.5,37+i)
    pool(4.1,10.7,-2.7,7.7,-4.5)
    route=[(0,-34,0),(0,-26,0)]
    for y0,y1,z0,z1 in [(-26,-20,0,-1.5),(-20,-14,-1.5,-3),(-14,-8,-3,-4.5)]:
        route.extend(stairs(0,y0,y1,z0,z1,open_landing=True)[1:])
    route.extend([(0,0,-4.5),(0,11,-4.5),(-5,11,-4.5)])
    ROUTES.append(dict(name='Rim to lower garden and return',points=route))
    # Side loops start on each stair landing and reconnect there.
    for ox,oy,z,y in [(24,26,-1.5,-20.7),(19,20,-3,-14.7)]:
        rx=ox-2.7;ry=oy-2.8
        ROUTES.append(dict(name=f'Terrace {abs(z):g} m loop',points=[(0,y,z),(rx,y,z),(rx,ry,z),(-rx,ry,z),(-rx,y,z),(0,y,z)]))
    for x in (-26.95,26.95):
        for y in (-22,-9,7,22):S.kit('ornamental_tree',x,y,0,0,1.02)
    for x in (-16,16):
        for y in (-29,29):S.kit('ornamental_tree',x,y,0,1,1.02)
    for x,y in [(-9,5),(-8,-9),(8,-9)]:S.kit('ornamental_tree',x,y,-4.5,0,1.0)
    # Exposed quarry strata have a rough face and irregular joints, in front of
    # the retaining core. They never intrude into the clear pedestrian corridor.
    rng=random.Random(761)
    for ix,iy,z in [(24,26,0),(19,20,-1.5),(14,14,-3)]:
        for y in range(-iy+2,iy,2):
            for side in (-1,1):
                for j in range(4):
                    xx=side*(ix-.09-rng.random()*.045);zz=z-1.38+j*.34
                    o=S.box('rough quarry face',(xx,y+rng.uniform(-.08,.08),zz),(.24,rng.uniform(1.8,2.05),rng.uniform(.27,.32)),'strata'+str(j%3))
                    bevel=o.modifiers.new('worn rock edges','BEVEL');bevel.width=.055;bevel.segments=2
        for x in range(-ix+2,ix,2):
            for j in range(4):
                o=S.box('quarry back strata',(x,iy-.10,z-1.38+j*.34),(1.95,.24,.29),'strata'+str(j%3))
                bevel=o.modifiers.new('worn rock edges','BEVEL');bevel.width=.055;bevel.segments=2
    for x,y,z,yaw in [(-5,10,-4.5,0),(5,11,-4.5,0),(-22.2,10,-1.5,math.pi/2),(22.2,10,-1.5,-math.pi/2)]:seat(x,y,z,yaw)
    r['walking']['entrance']=[0,-33.5,0]
    r['clear_routes']=[dict(a=[0,-34],b=[0,-27],width=4.4)]
    r['walk_views']=[('entrance',(0,-29,1.65),(0,0,-2)),('lower',(-4,1,-2.85),(4,-15,-1.2))]


def pool(x0,x1,y0,y1,z):
    S.box('dark pool basin',((x0+x1)/2,(y0+y1)/2,z-.13),(x1-x0,y1-y0,.24),'basin')
    polygon('still reflective water',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],'water',z+.035)
    edge('pool coping',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],'stone',.23,.22,z,True)
    # Thin highlights carry ripples in real geometry, without photographic fill.
    for j in range(10):
        yy=y0+.45+j*(y1-y0-.9)/10
        S.line((x0+.45,yy),(x1-.45,yy+.035),.008,'water_glint',z+.038)


def spiral(r):
    w,d=r['dimensions_m'];S.box('earthwork base',(0,0,-.17),(w,d,.30),'grass')
    # A smooth radial earthwork: path elevation and ground derive from the same rise.
    n=160;nr=28;vs=[(0,0,5.4)];faces=[]
    for j in range(nr+1):
        radius=5+j*19/nr;h=max(0,min(5.4,(23-radius)*5.4/16))
        for i in range(n):
            a=i*math.tau/n;x=radius*math.cos(a);y=radius*math.sin(a)
            track=[]
            for turn in range(3):
                angle=(a+math.pi/2)%(math.tau)+turn*math.tau
                if angle<=3*math.pi:
                    t=angle/(3*math.pi);rr=23-16*t
                    if abs(radius-rr)<2.5:track.append(5.4*t-.08)
            vs.append((x,y,min([h-.025,*track])))
    for i in range(n):faces.append((0,1+i,1+(i+1)%n))
    for j in range(nr):
        for i in range(n):
            a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
    mound=S.mesh('sculpted meadow hill',vs,faces,'meadow');
    for f in mound.data.polygons:f.use_smooth=True
    floor('entry promenade',-2.15,2.15,-34,-23,0)
    floor('arrival forecourt',-10,10,-32,-26,0, [(-8,-4,-31,-27),(4,8,-31,-27)])
    planting_rect(-8,-4,-31,-27,0,71);planting_rect(4,8,-31,-27,0,72)
    points=[];sides=[[],[]];segments=240
    for i in range(segments+1):
        t=i/segments;a=-math.pi/2+t*3*math.pi;radius=23-16*t;z=5.4*t+.025
        # Path is radial within its supporting hill. No bridge or overlapping deck.
        points.append((radius*math.cos(a),radius*math.sin(a),z))
        for side in (0,1):
            rr=radius+(-1 if side==0 else 1)*1.75
            sides[side].append((rr*math.cos(a),rr*math.sin(a),z))
    # Zero datum at the mouth avoids an entry lip.
    for side in (0,1):sides[side][0]=(sides[side][0][0],sides[side][0][1],0)
    points[0]=(0,-23,0)
    for i in range(segments):
        walk_quad('spiral paving ribbon',[sides[0][i],sides[1][i],sides[1][i+1],sides[0][i+1]])
        # Visible supporting curb bridges the few centimetres between conical grade and flat crossfall.
        for side in (0,1):
            a,b=sides[side][i],sides[side][i+1]
            S.mesh('stone ribbon retaining edge',[a,b,(b[0],b[1],b[2]-.65),(a[0],a[1],a[2]-.65)],[(0,1,2,3)],'stone')
        if i%3==0:S.beam('radial paving joint',sides[0][i],sides[1][i],.004,'joint',4)
    # Rails sit beyond a broad clear strip and stop before the summit connection.
    for side in (0,1):
        guard = sides[side][4:-12] if side == 0 else sides[side][4:]
        rail(guard[::3]+[guard[-1]])
    floor('summit approach',-1.75,1.75,3.8,7,5.425)
    N=64
    for i in range(N):
        a=i*math.tau/N;b=(i+1)*math.tau/N
        p=[(0,0,5.425),(5.25*math.cos(a),5.25*math.sin(a),5.425),(5.25*math.cos(b),5.25*math.sin(b),5.425)]
        S.mesh('summit plaza',p,[(0,1,2)],'walk_surface');WALK.append([list(v) for v in p])
    rail([(5.5*math.cos(a),5.5*math.sin(a),5.425) for a in [math.pi*.66+i*math.pi*1.68/64 for i in range(65)]])
    # Seating stays at the perimeter; the centre and approach are unobstructed.
    seat(-3,0,5.425,math.pi/2);seat(3,0,5.425,-math.pi/2)
    # Small flowering drifts follow the earthwork, with no plant on the route.
    rng=random.Random(913)
    for i in range(1100):
        a=rng.random()*math.tau;radius=rng.uniform(7,23);x=radius*math.cos(a);y=radius*math.sin(a)
        if min(math.hypot(x-p[0],y-p[1]) for p in points)<3.2:continue
        z=max(0,min(5.4,(23-radius)*5.4/16))
        S.kit('flowering_perennial' if i%4==0 else 'meadow_grass',x,y,z-.025,a,1.02)
    for i in range(16):
        a=i*math.tau/16
        if math.sin(a)<-.80:continue
        S.kit('ornamental_tree',28.0*math.cos(a),28.0*math.sin(a),0,a,.72)
    for x in (-12,12):seat(x,-28,0,0)
    ROUTES.append(dict(name='Complete spiral ascent and descent',points=[(0,-34,0),(0,-23,0),*points[1:],(0,3.8,5.425),(0,0,5.425)]))
    r['walking']['entrance']=[0,-33.5,0]
    r['clear_routes']=[dict(a=[0,-34],b=[0,-27],width=3.5)]
    r['walk_views']=[('entrance',(0,-29,1.65),(6,-17,3)),('summit',(0,0,7.075),(8,-18,3.2))]


def cascade(r):
    S.box('garden foundation',(0,0,-.27),(54,68,.36),'stone')
    levels=[(-34,-17,0),(-17,-3,1.5),(-3,11,3),(11,34,4.5)]
    for i,(y0,y1,z) in enumerate(levels):
        holes=[(-23,-14,y0+1.2,y1-1.2),(14,23,y0+1.2,y1-1.2)]
        water=(-3.4,3.4,y0+1.2,y1 if i<3 else 24)
        if water[3]>water[2]:holes.append(water)
        if i<3:holes.extend([(x-2.2,x+2.2,y1-6,y1) for x in (-8,8)])
        floor('connected water garden terrace',-27,27,y0,y1,z,holes)
        if z:S.box('terrace backing',(0,(y0+y1)/2,z/2-.01),(54,y1-y0,z),'stone')
        for j,h in enumerate(holes[:2]):planting_rect(*h,z,80+i*7+j,1.35)
        if water[3]>water[2]:pool(water[0]+.3,water[1]-.3,water[2]+.3,water[3]-.3,z)
        for side in (-1,1):
            for yy in (y0+4,y1-4):S.kit('ornamental_tree',side*19,yy,z,0,.78)
            seat(side*12,(y0+y1)/2,z,side*math.pi/2)
        if i<3:
            for x in (-8,8):stairs(x,y1-6,y1,z,z+1.5)
            # Wall at the next terrace front; no wall across either stair mouth.
            for a,b in [(-27,-10.25),(-5.75,5.75),(10.25,27)]:solid_wall('cascade terrace face',(a,y1),(b,y1),z,z+1.5)
            # Central water sheet meets the lower pool via its runnel.
            S.mesh('falling water curtain',[(-2.5,y1-.22,z+1.48),(2.5,y1-.22,z+1.48),(2.5,y1-.38,z+.06),(-2.5,y1-.38,z+.06)],[(0,1,2,3)],'water')
            for k in range(24):
                x=-2.4+k*.2;S.beam('cascade sparkling filament',(x,y1-.225,z+1.47),(x+.015,y1-.385,z+.06),.011,'water_glint',5)
            # Shallow stone channel connects lower basin and fall; excluded from nav.
            # Guard the drop edges alongside the stair openings.
            for a,b in [(-26,-10.5),(-5.5,5.5),(10.5,26)]:rail([(a,y1+.18,z+1.5),(b,y1+.18,z+1.5)])
    # A pair of honest shaded resting rooms at the high end.
    for x in (-10,10):
        before=set(S.bpy.context.scene.objects);S.pergola(x,29,6,5)
        for o in set(S.bpy.context.scene.objects)-before:o.location.z+=4.5
        seat(x,30,4.5,0)
    left=[(0,-34,0),(0,-33.5,0),(-8,-33.5,0),(-8,-29,0)]
    for y,z in [(-17,0),(-3,1.5),(11,3)]:left.extend([(-8,y-6,z),(-8,y-1.5,z+1.5),(-8,y,z+1.5)])
    left.extend([(-8,25,4.5),(0,27,4.5),(8,25,4.5)])
    right=[]
    for y,z in [(11,3),(-3,1.5),(-17,0)]:right.extend([(8,y,z+1.5),(8,y-1.5,z+1.5),(8,y-6,z)])
    right.extend([(8,-29,0),(8,-33.5,0),(0,-33.5,0),(0,-34,0)])
    ROUTES.append(dict(name='Twin stairs complete garden loop',points=left+right))
    r['walking']['entrance']=[0,-33.5,0]
    r['clear_routes']=[dict(a=[0,-34],b=[0,-30],width=4.4)]
    r['walk_views']=[('entrance',(0,-32,1.65),(0,13,5.0)),('upper',(-8,21,6.15),(0,-18,1.5))]


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind])
    if a.output.exists():raise ValueError('Existing immutable candidate; choose a new revision directory.')
    kit_bytes=a.kit.read_bytes();kit=json.loads(kit_bytes)
    assert all(k in kit for k in ['ornamental_tree','bench','flowering_perennial','meadow_grass','silver_shrub'])
    r.update(kit_sha256=hashlib.sha256(kit_bytes).hexdigest(),source_kind='original_user_requested_concept',
             design_basis='Quarry Garden, Spiral Lookout Park and Cascade Water Garden brief approved in conversation; conservatory-v013 composition and detail benchmark.',
             terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,runtime_status='NOT TESTED',
             entrance=dict(x=0,y=-r['dimensions_m'][1]/2,widthM=3.5),
             walking=dict(version=1,triangles=WALK,routes=ROUTES,maxStepM=.22,entrance=[]))
    if a.dry_run:print('DRY_RUN_PASS',r['id']);return
    a.output.mkdir(parents=True);S.init(a.kit);S.ground(*r['dimensions_m'],[])
    for name,color,rough in [('walk_surface',(.53,.50,.43),.86),('stone',(.48,.435,.35),.9),('joint',(.29,.28,.24),.95),
        ('nosing',(.68,.64,.52),.86),('meadow',(.26,.32,.12),.97),('basin',(.10,.18,.15),.8),('water',(.13,.29,.27),.18),('water_glint',(.38,.56,.48),.25),
        ('strata0',(.44,.40,.32),.96),('strata1',(.54,.49,.39),.95),('strata2',(.49,.45,.36),.97)]:material(name,color,rough)
    globals()[a.kind](r)
    obstacles=[]
    for item in S.PLACEMENTS:
        if item['kind']=='bench':
            w,d=2.4,1.1
            if abs(math.sin(item['yaw']))>.5:w,d=d,w
            obstacles.append([item['x']-w/2,item['x']+w/2,item['y']-d/2,item['y']+d/2])
        elif item['kind']=='ornamental_tree':
            obstacles.append([item['x']-.45,item['x']+.45,item['y']-.45,item['y']+.45])
    r['walking']['obstacles']=obstacles
    r['walking']['triangles']=WALK;r['walking']['routes']=ROUTES
    r['source_build_files']={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in [Path(__file__),Path(S.__file__),Path(__file__).with_name('build_showcase_parks.py')]}
    for path in [Path(__file__),Path(S.__file__),Path(__file__).with_name('build_showcase_parks.py')]:shutil.copy2(path,a.output/path.name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    w,d=r['dimensions_m']
    S.deliver(a.output,r,[('aerial',(w*.85,-d*.92,62),(0,0,0),88),('top',(0,0,100),(0,.001,0),80),
        ('detail',(17,-26,12),(0,-10,-1 if a.kind=='quarry' else 2),35),('rear',(-w*.85,d*.8,45),(0,0,0),85)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=24
    for name,pos,target in r.pop('walk_views'):
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=str(a.output/'renders'/f'{name}.png');S.bpy.ops.render.render(write_still=True)
    r['runtime_contract']='Complete native assembly on prepared level ground; preserve native scale. Walking faces match exported walk_surface geometry; routes are tested in both directions.'
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    report=dict(status='PASS_OFFLINE_GEOMETRY',assembly_sha256=r['assembly']['sha256'],bounds_m=r['bounds_m'],triangles=r['triangles'],
        dependency_closure='embedded GLB',runtime_status='NOT TESTED',visual_review='pending',walking_review='pending')
    (a.output/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
