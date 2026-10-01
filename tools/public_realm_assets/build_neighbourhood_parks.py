"""Bounded reference-led allotment and nature-play native assemblies."""
import argparse, hashlib, json, math, random, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import scene as S
from build_showcase_parks import material, polygon, ribbon, edge, hedge
from mathutils import Vector

SPECS={
 'allotment':dict(id='student_community_allotment_v1',archetype='community_garden_enhanced',source_variant='garden_classic_allotment',slug='community-garden-design-variants',index=0,title='Community Allotment Garden',dimensions_m=[36,46],programme='Four productive garden rooms, eight individual sheds, open plot gates, trellises and shared orchard'),
 'nature':dict(id='student_forest_adventure_v1',archetype='nature_play_area',source_variant='nature_play_area_v0',slug='nature-play-area',index=0,title='Forest Adventure Nature Play',dimensions_m=[34,46],programme='Woodland play garden with winding stony stream, stepping logs, ropes, climbing deck and willow tunnel'),
}

def hedge(points,width=.7,height=.8,base_z=0):
    # Dense leaf skins on every visible side hide a narrow dark branch core.
    edge('hedge branch core',points,'hedge',height*.83,width*.68,base_z,False)
    rng=random.Random(round(sum(x+y for x,y in points)*113));vs=[];fs=[]
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b);dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length
        for i in range(math.ceil(length*130)):
            t=rng.random();side=rng.choice([-1,0,1]);off=rng.uniform(-width/2,width/2) if side==0 else side*width/2+rng.uniform(-.04,.04)
            x=a[0]+(b[0]-a[0])*t-dy*off;y=a[1]+(b[1]-a[1])*t+dx*off;z=base_z+(height+rng.uniform(-.05,.07) if side==0 else rng.uniform(.06,height))
            rad=rng.uniform(.065,.12);n=len(vs);vs.append((x,y,z+.022))
            for j in range(8):
                ang=j*math.tau/8
                if side==0:vs.append((x+rad*math.cos(ang),y+rad*math.sin(ang),z))
                else:vs.append((x+dx*rad*math.cos(ang),y+dy*rad*math.cos(ang),z+rad*math.sin(ang)))
            fs.extend((n,n+1+j,n+1+(j+1)%8) for j in range(8))
    S.mesh('rounded hedge leaf skin',vs,fs,'leaf')

def gravel_finish():
    rng=random.Random(9842);vs=[];fs=[]
    for _ in range(18000):
        x=rng.uniform(-17,17);y=rng.uniform(-22.8,22.8)
        if S.surface_at(x,y)!='gravel':continue
        r=rng.uniform(.012,.028);z=.003;n=len(vs)
        vs.extend([(x-r,y-r,z),(x+r,y-r,z),(x+r,y+r,z),(x-r,y+r,z),(x,y,z+r*.6)])
        fs.extend([(n,n+1,n+4),(n+1,n+2,n+4),(n+2,n+3,n+4),(n+3,n,n+4)])
    S.mesh('fine irregular gravel aggregate',vs,fs,'aggregate')

def pickets(a,b,h=1.05):
    n=max(1,round(math.dist(a,b)/.17))
    for i in range(n+1):
        t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
        S.box('individual timber picket',(x,y,h/2),(.065,.065,h),'timber')
    for z in (.30,.80):S.beam('picket cross rail',(*a,z),(*b,z),.037,'timber',4)

def shed(x,y,color):
    # Four enclosed walls, actual front door/window apertures, shallow mono-pitch roof.
    w,d=2.7,2.5;z0=.10;roof=lambda yy:2.45+.13*(yy-y)
    S.box('shed slab',(x,y,.05),(w+.18,d+.18,.10),'stone')
    S.box('shed rear wall',(x,y+d/2,1.23),(w,.09,2.46),color)
    for xx in (x-w/2,x+w/2):
        S.mesh('shed side wall',[(xx,y-d/2,z0),(xx,y+d/2,z0),(xx,y+d/2,roof(y+d/2)),(xx,y-d/2,roof(y-d/2))],[(0,1,2,3)],color)
    fy=y-d/2
    # Door from -.95 to -.05; window .25 to1.02; carrier strips do not cross either.
    for lo,hi in ((-1.35,-.95),(-.05,.25),(1.02,1.35)):
        S.box('shed front pier',(x+(lo+hi)/2,fy,1.19),(hi-lo,.10,2.18),color)
    S.box('shed door head',(x-.50,fy,2.20),(.9,.10,.18),color)
    S.box('shed window apron',(x+.635,fy,.54),(.77,.10,.88),color)
    S.box('shed window head',(x+.635,fy,2.05),(.77,.10,.48),color)
    S.box('closed planked shed door',(x-.5,fy+.025,1.07),(.86,.06,1.94),color)
    for j in range(8):S.box('door board joint',(x-.88+j*.107,fy-.011,1.07),(.009,.007,1.88),'timber')
    S.beam('door handle',(x-.17,fy-.07,1.0),(x-.17,fy-.07,1.16),.022,'metal',8)
    S.box('shed optical window',(x+.635,fy+.03,1.395),(.77,.014,.83),'glass')
    for xx in (x+.25,x+.635,x+1.02):S.box('shed window stile',(xx,fy-.03,1.395),(.045,.075,.89),'paint')
    for zz in (.98,1.395,1.81):S.box('shed window rail',(x+.635,fy-.03,zz),(.83,.075,.045),'paint')
    # Horizontal boards carry the coloured-shed identity around the whole shell.
    for j in range(18):
        zz=.14+j*.12
        for xx in (x-w/2-.008,x+w/2+.008):S.box('shed side board shadow',(xx,y,zz),(.012,d,.012),'timber')
        S.box('shed back board shadow',(x,y+d/2+.008,zz),(w,.012,.012),'timber')
    corners=[(x-w/2-.14,y-d/2-.16),(x+w/2+.14,y-d/2-.16),(x+w/2+.14,y+d/2+.16),(x-w/2-.14,y+d/2+.16)]
    vs=[(xx,yy,roof(yy)+dz) for dz in (0,.09) for xx,yy in corners]
    S.mesh('sealed shed roof',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'roof')
    S.box('shed threshold',(x-.5,fy-.15,.08),(1,.40,.08),'stone')

def crops(x,y,w,d,kind,seed):
    S.box('raised growing soil',(x,y,.13),(w,d,.26),'soil')
    edge('garden bed boards',[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],'timber',.29,.065,0,True)
    rng=random.Random(seed);batches={k:([],[]) for k in ('cabbage','crop','leaf')}
    nx=max(1,int(w/.45));ny=max(1,int(d/.49))
    for i in range(nx):
        for j in range(ny):
            xx=x-w/2+(i+.5)*w/nx+rng.uniform(-.045,.045);yy=y-d/2+(j+.5)*d/ny+rng.uniform(-.05,.05)
            mode=j%3 if seed%2==0 else 0
            role=['cabbage','crop','leaf'][mode];vs,fs=batches[role]
            h=rng.uniform(.15,.30) if mode==0 else rng.uniform(.48,.76) if mode==1 else rng.uniform(.9,1.3)
            for k in range(7):
                a=k*math.tau/7+rng.random()*.5;rad=rng.uniform(.19,.29) if mode==0 else rng.uniform(.12,.22);n=len(vs)
                # Curved rounded leaves: broad cabbage cups, narrower chard lobes.
                for t in range(7):
                    u=t/6;rr=rad*u
                    zz=(.27+h*(1-.7*u)+.06*math.sin(math.pi*u) if mode==0 else .27+h*math.sin(u*math.pi*.65) if mode==1 else .36+k*h/8+.05*math.sin(math.pi*u))
                    half=(.15 if mode==0 else .037 if mode==1 else .075)*math.sin(math.pi*u)**.55
                    for jv in range(5):
                        v=(jv-2)/2;ss=half*v
                        vs.append((xx+rr*math.cos(a)-ss*math.sin(a),yy+rr*math.sin(a)+ss*math.cos(a),zz-.055*v*v*math.sin(math.pi*u)))
                for t in range(6):
                    for jv in range(4):
                        k0=n+t*5+jv;fs.append((k0,k0+1,k0+6,k0+5))
            S.beam('edible plant stem',(xx,yy,.25),(xx,yy,.27+h),.011,'crop',5)
            if mode==2:
                S.beam('individual tomato support',(xx+.055,yy,.25),(xx+.055,yy,1.7),.012,'timber',6)
                for z in (.7,1.1):S.beam('vine cross tie',(xx-.06,yy,z),(xx+.08,yy,z),.008,'timber',5)
    for role,(vs,fs) in batches.items():
        if not vs:continue
        obj=S.mesh('edible '+role+' leaf rows',vs,fs,role)
        for f in obj.data.polygons:f.use_smooth=True

def trellis(x,y):
    for dx in (-1.5,1.5):S.beam('trellis grounded post',(x+dx,y,0),(x+dx,y,2.1),.055,'timber',8)
    for zz in (.5,1,1.5,2.05):S.beam('trellis crossbar',(x-1.5,y,zz),(x+1.5,y,zz),.025,'timber',6)
    for dx in (-1.2,-.8,-.4,0,.4,.8,1.2):
        S.beam('climbing support',(x+dx,y,.28),(x+dx,y,2.1),.015,'timber',6)
        for j in range(3):S.kit('flowering_perennial',x+dx,y,.22+j*.5,j*.8,.60)

def allotment(r):
    S.ground(36,46,[(0,-8,34,28,'gravel'),(0,0,3.2,46,'gravel'),(0,8,34,2.4,'gravel')])
    gravel_finish()
    for side in (-1,1):
        for j in range(88):S.box('promenade narrow stone edge',(side*1.68,-22.6+j*.51,.018),(.14,.49,.036),'stone')
    colors=['sage','ochre','blue','terracotta']
    for si,side in enumerate((-1,1)):
        x=side*9.3
        for row,cy in enumerate((-12,-.4)):
            # Each room has a real 1.6 m opening to the central promenade.
            inner=side*2.2;outer=side*16.8;yb=cy-5.4;yt=cy+5.4
            pickets((outer,yb),(outer,yt));pickets((outer,yb),(inner,yb));pickets((outer,yt),(inner,yt))
            pickets((inner,yb),(inner,cy-1));pickets((inner,cy+1),(inner,yt))
            pickets((inner,cy-1),(inner+side*1.5,cy-1))
            # Low hedge retains plot enclosure without blocking the gate.
            hedge([(inner+side*.5,yb+.5),(inner+side*.5,cy-1.4)],.55,.75)
            hedge([(inner+side*.5,cy+1.4),(inner+side*.5,yt-.5)],.55,.75)
            for j,yy in enumerate((cy-2.9,cy+2.9)):
                shed(side*14.5,yy,colors[(row*2+j+si)%4])
                for k,xx in enumerate((side*5,side*9.2)):crops(xx,yy,2.7,3.4,(j+k+row)%2,100*si+20*row+4*j+k)
            trellis(side*7,cy+4.5)
            # Flower/herb margins soften the working plots without filling their routes.
            for j in range(13):
                xx=side*(3.7+j*.7)
                S.kit(['flowering_perennial','meadow_grass'][j%2],xx,cy+4.7,0,j*.8,.85)
            for j in range(12):
                yy=cy-4.9+j*.85
                S.box('shed access paver',(side*12.2,yy,.015),(.65,.80,.03),'stone')
            for yy in (cy-4.8,cy+4.8):
                for xx in (side*10.8,side*11.4):S.kit('flowering_perennial',xx,yy,0,yy,.85)
            S.kit('bench',side*5,cy,0,side*math.pi/2)
            S.box('compost bin',(side*11.8,cy,.48),(1.1,1,.96),'timber')
            for j in range(7):S.box('compost board gap',(side*11.8,cy-.505,.12+j*.12),(1.05,.009,.018),'metal')
    # Shared upper orchard; generous canopy clearances from the main path/boundary.
    for x in (-11,-5.5,5.5,11):
        for y in (12,18):S.kit('ornamental_tree',x,y,0,(x+y)*.2,.9)
    for x in (-7,7):S.kit('bench',x,14.4,0,math.pi)
    for a,b in [((-17.4,-22.4),(-1.8,-22.4)),((1.8,-22.4),(17.4,-22.4)),((-17.4,-22.4),(-17.4,22.4)),((17.4,-22.4),(17.4,22.4)),((-17.4,22.4),(-1.8,22.4)),((1.8,22.4),(17.4,22.4))]:pickets(a,b)
    for x in (-17,17):
        hedge([(x,-20),(x,21)],.5,.7)
    hedge([(-16,21.5),(-1.9,21.5)],.7,.85);hedge([(1.9,21.5),(16,21.5)],.7,.85)
    # A few planted entrance edges and a useful shared tool/water point.
    for x in (-10,10):
        for i in range(16):
            for j in range(2):S.kit(['flowering_perennial','meadow_grass'][(i+j)%2],x-5.5+i*.72,-20.8+j*.7,0,i*.7,.84)
    S.kit('bin',2.7,-20)
    S.beam('allotment water standpipe',(3.4,-19,0),(3.4,-19,.95),.035,'metal',10)
    S.beam('water tap',(3.4,-19,.85),(3.4,-19.22,.85),.025,'metal',8)
    r['clear_routes']=[dict(a=[0,-23],b=[0,22],width=3.2),dict(a=[-15,8],b=[15,8],width=2.4)]
    r['entrance']['widthM']=3.2
    r['adaptations']=['Four garden rooms with eight coloured sheds, productive beds, trellises and shared orchard from the exact reference. Surrounding buildings excluded; plot gates shown open.']

def stone(x,y,rx=.45,ry=.35,h=.24):
    S.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,h*.38))
    o=S.bpy.context.object;o.name='embedded stream stone';o.scale=(rx,ry,h);o.rotation_euler.z=(x+y)*.73;o.data.materials.append(S.MATS['stone'])
    rng=random.Random(round((x+30)*137+(y+30)*197))
    for v in o.data.vertices:v.co*=rng.uniform(.88,1.12)
    for f in o.data.polygons:f.use_smooth=True

def log(a,b,r=.18):
    S.beam('roundwood play log',a,b,r,'timber',14)
    direction=(Vector(b)-Vector(a)).normalized()
    for p,sign in ((a,-1),(b,1)):
        q=Vector(p)+direction*sign*.004
        S.beam('light cut log end',q,q+direction*sign*.007,r*.88,'cutwood',14)

def rope(points):
    for a,b in zip(points,points[1:]):S.beam('tensioned play rope',a,b,.018,'rope',6)

def stream_ribbon(name,points,base,mat,z):
    vs=[]
    for i,(x,y) in enumerate(points):
        half=base/2+.25*math.sin(y*.61)+.15*math.sin(y*1.41)
        vs.extend([(x-half,y,z),(x+half,y,z)])
    S.mesh(name,vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)],mat)

def willow_cover():
    rng=random.Random(312);vs=[];fs=[]
    for i in range(4200):
        t=rng.uniform(.05,math.pi-.05);yy=rng.uniform(2.08,5.92)
        x=-6.5+1.19*math.cos(t);z=1.99*math.sin(t)+rng.uniform(-.06,.09)
        # Pointed hanging leaves wrap the arch; both entrance portals remain open.
        n=len(vs);rad=rng.uniform(.07,.14);drop=rng.uniform(.14,.25)
        vs.extend([(x,yy,z+.04),(x-rad*.55,yy-.025,z-drop*.3),(x-rad*.65,yy,z-drop*.65),(x,yy+.01,z-drop),(x+rad*.65,yy,z-drop*.65),(x+rad*.55,yy-.025,z-drop*.3),(x,yy-.04,z-drop*.45)])
        fs.extend((n+6,n+j,n+(j+1)%6) for j in range(6))
    S.mesh('dense hanging willow leaves',vs,fs,'leaf')

def leafy_mass(name,cx,cy,cz,rx,ry,rz,count,seed):
    rng=random.Random(seed);vs=[];fs=[]
    for i in range(count):
        a=rng.random()*math.tau;u=rng.uniform(-1,1);rr=math.sqrt(1-u*u)
        x=cx+rx*rr*math.cos(a);y=cy+ry*rr*math.sin(a);z=max(.06,cz+rz*u)
        rad=rng.uniform(.075,.145);n=len(vs);vs.append((x,y,z+.035))
        for j in range(6):
            t=j*math.tau/6;vs.append((x+rad*math.cos(t),y+rad*.6*math.sin(t),z+.04*math.sin(t)))
        fs.extend((n,n+1+j,n+1+(j+1)%6) for j in range(6))
    S.mesh(name,vs,fs,'leaf')

def woodland_beds():
    # Connected planted islands remain outside the walking path and play portals.
    for i,(cx,cy) in enumerate(((3.15,1.4),(8,-10.7),(-8.55,4))):
        for j in range(18):
            x=cx+((j%3)-1)*.47+.14*math.sin(j);y=cy+((j//3)-2.5)*.67
            h=.32+.16*(1+math.sin(j*1.7))
            leafy_mass('overlapping woodland bank foliage',x,y,h,.58,.60,h,110,100+i*100+j)
    # A separate asymmetric willow crown with hanging branchlets above the sand corner.
    tx,ty=7,-17.8
    for tree in S.kit('shade_tree',tx,ty,0,.8,.84):tree.scale=(1.25,1.30,.84)
    log((tx,ty,0),(tx-.35,ty,5.3),.19)
    for j in range(10):
        a=j*math.tau/10;xx=tx+2.6*math.cos(a);yy=ty+2.3*math.sin(a)
        S.beam('willow spreading branch',(tx-.2,ty,3.7),(xx,yy,5.0),.045,'timber',7)
        for k in range(4):
            x=xx+.28*math.sin(k+j);y=yy+.25*math.cos(k-j)
            S.beam('hanging willow twig',(x,y,5),(x+.2,y,2.6+.2*k),.012,'timber',5)
            leafy_mass('drooping willow foliage',x,y,3.8+.1*k,.30,.30,1.15,48,400+j*4+k)

def nature(r):
    w,d=r['dimensions_m'];S.ground(w,d,[])
    # Own the whole ground; curved material regions are deliberately kept separate.
    S.box('woodland ground',(0,0,-.06),(w,d,.12),'grass')
    polygon('bark play clearing',[(-11,-21),(11,-21),(13,-15),(12,18),(8,21),(-10,21),(-13,14),(-12,-12)],'mulch',.005)
    rng=random.Random(912);vs=[];fs=[]
    for i in range(19000):
        x=rng.uniform(-10.8,9);y=rng.uniform(-20,20);rr=rng.uniform(.014,.047);n=len(vs)
        vs.extend([(x-rr,y-rr*.4,.008),(x+rr,y-rr*.4,.008),(x+rr,y+rr*.4,.009),(x-rr,y+rr*.4,.009)]);fs.append((n,n+1,n+2,n+3))
    S.mesh('small bark-chip ground detail',vs,fs,'cutwood')
    stream=[(1.4*math.sin(y/6),y) for y in [-21+i*42/140 for i in range(141)]]
    stream_ribbon('irregular shallow stream bed',stream,3.5,'stone',.009)
    stream_ribbon('shallow static stream water',stream,2.15,'water',.018)
    # Dedicated walking route is separated from the stepping-stone challenge.
    walk=[(0,-23),(0,-21.5),(5,-20),(10,-18),(10.5,-10),(10.8,-2),(10.6,8),(9.3,17),(5,20),(0,21.5),(0,23)]
    ribbon('connected accessible concept path',walk,2.6,'gravel',.024)
    rng=random.Random(324)
    for j in range(145):
        y=rng.uniform(-20.8,20.8);x=1.4*math.sin(y/6);half=1.75+.25*math.sin(y*.61)+.15*math.sin(y*1.41)
        for s in (-1,1):stone(x+s*(half+rng.uniform(-.25,.30)),y,rng.uniform(.09,.54),rng.uniform(.08,.45),rng.uniform(.08,.28))
    for j in range(22):
        y=-19+j*1.78;x=1.4*math.sin(y/6)+.43*math.sin(j*1.9)
        pts=[(x+(.62+.07*math.sin(k*2.3+j))*math.cos(k*math.tau/8),y+(.53+.07*math.cos(k+j))*math.sin(k*math.tau/8)) for k in range(8)]
        vs=[(xx,yy,zz) for zz in (.015,.20+(j%3)*.025) for xx,yy in pts]
        S.mesh('broad flat stepping stone',vs,[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(k,(k+1)%8,(k+1)%8+8,k+8) for k in range(8)],'stone')
    # Three grounded logs bridge the stream at the southern play junction.
    for dy in (-.48,0,.48):log((-3.1,-12+dy,.36),(3.1,-12+dy,.36),.24)
    for x in (-2.8,2.8):log((x,-13,.12),(x,-11,.12),.18)
    # Left climbing clearing: roundwood balance structure and rope handholds.
    for x,y in ((-8.5,-10),(-4.5,-5),(-9.5,0)):
        log((x,y,0),(x,y,2.8),.14)
    for a,b in [((-8.5,-10,.25),(-4.5,-5,.65)),((-4.5,-5,.65),(-9.5,0,.30)),((-9.5,0,.30),(-8.5,-10,.25))]:
        log(a,b,.15);rope([(a[0],a[1],1.85),((a[0]+b[0])/2,(a[1]+b[1])/2,1.5),(b[0],b[1],1.85)])
    # Upright stump trail preserves spacing and irregular heights.
    for j in range(15):
        x=-5.5-1.4*math.sin(j*.65);y=8+j*.75;h=.20+(j%4)*.10
        log((x,y,0),(x,y,h),.21)
    # Woven willow tunnel with grounded hoops, longitudinal rods and leaf growth.
    for j in range(9):
        yy=2+j*.5;pts=[(-6.5+1.15*math.cos(t*math.pi/24),yy,1.95*math.sin(t*math.pi/24)) for t in range(25)]
        for a,b in zip(pts,pts[1:]):S.beam('woven willow arch',a,b,.032,'timber',6)
    for j in range(1,12):
        t=j*math.pi/12;x=-6.5+1.15*math.cos(t);z=1.95*math.sin(t)
        S.beam('willow longitudinal weave',(x,2,z),(x,6,z),.018,'timber',6)
        for k in range(4):S.kit('flowering_perennial',x,2.3+k*1.1,z,j+k,.32)
    willow_cover()
    # Climbing deck is built around a real tree hole, with a stair and rope guards.
    tx,ty=5.5,6
    S.kit('shade_tree',tx,ty,0,.7,1.3)
    for dx in (-1.65,1.65):
        for dy in (-1.65,1.65):log((tx+dx,ty+dy,0),(tx+dx,ty+dy,2.55),.11)
    for i in range(20):
        xx=tx-1.68+i*.176
        for a,b in ([(-1.75,-.5),(.5,1.75)] if abs(xx-tx)<.5 else [(-1.75,1.75)]):S.box('tree deck board',(xx,ty+(a+b)/2,1.20),(.165,b-a,.11),'timber')
    for y in (ty-1.65,ty+1.65):log((tx-1.8,y,1.08),(tx+1.8,y,1.08),.12)
    for a,b in [((tx-1.65,ty-1.65),(tx-1.65,ty+1.65)),((tx-1.65,ty+1.65),(tx+1.65,ty+1.65))]:
        for z in (1.6,2.1,2.5):rope([(*a,z),((a[0]+b[0])/2,(a[1]+b[1])/2,z-.12),(*b,z)])
    for i in range(7):S.box('tree deck stair',(tx+1.95+i*.28,ty,.085*(7-i)),(.30,1.1,.17*(7-i)),'timber')
    # Natural sand room and a supported rope climbing frame in the northern clearing.
    polygon('sand play room',[(4,-18),(8,-18),(8.7,-14),(5,-13)],'sand',.031)
    for a,b in [((4,-18,.18),(8,-18,.18)),((8.7,-14,.18),(5,-13,.18))]:log(a,b,.20)
    for x,y in ((4,-17),(4.3,-15),(8,-16),(6,-13.5)):stone(x,y,.5,.4,.3)
    for x in (-9,-3):
        for y in (15,19):log((x,y,0),(x,y,2.8),.12)
    for j in range(11):
        x=-9+j*.6;rope([(x,15,1.15),(x,17,.85),(x,19,1.15)])
    for j in range(8):
        y=15+j*4/7;rope([(-9,y,1.15),(-6,y,.85),(-3,y,1.15)])
    # Dense layered woodland edges; native canopy stays within the declared plot.
    for side in (-1,1):
        for i,y in enumerate((-17,-8,1,10,16)):
            broad=side==1 and i in (1,3,4)
            xx=side*(10.3 if broad else 11.9)
            trees=S.kit('shade_tree',xx,y,0,y*.7,1.35)
            for tree in trees:tree.scale=(1.85 if broad else 1.25,1.85 if broad else 1.35,1.18 if broad else 1.30+i*.025)
        for j in range(8):
            yy=-19+j*5.2;hedge([(side*12.4,yy),(side*13,yy+1.3),(side*12.6,yy+2.8)],2.0,.7+(j%3)*.13)
            for k,(xx,yend) in enumerate(((side*12.4,yy),(side*12.6,yy+2.8))):leafy_mass('hedge rounded end foliage',xx,yend,.45,1.05,.35,.49,60,900+j*2+k)
        for j in range(49):
            y=-21+j*.88;x=side*(14.7+.35*math.sin(j))
            S.kit(['silver_shrub','meadow_grass','flowering_perennial'][j%3],x,y,0,j*.6,1.05)
        for j in range(23):S.kit('silver_shrub',side*12.9,-20+j*1.8,0,j,.75)
    for x,y in ((-3,-5),(-3,9),(4,-6),(4,14)):
        for j in range(8):S.kit('meadow_grass',x+(j%2)*.4,y+(j//2)*.5,0,j,1)
    for i,(x,y) in enumerate(((-3,-17),(3,-8),(-3,1),(-3,11),(4,16),(7,2),(7,-12),(-10,7))):
        S.kit('silver_shrub',x,y,0,i,.85)
        for j in range(2):S.kit('flowering_perennial',x+(j-.5)*1.2,y+.8,0,j,1.0)
        for j in range(4):S.kit('meadow_grass',x+math.sin(j*2)*1.1,y+math.cos(j*2)*1.1,0,j,1.1)
    woodland_beds()
    for x in (-8,8):
        for y in (-21,21):
            for j in range(9):S.kit(['silver_shrub','flowering_perennial'][j%2],x-2+j*.5,y,0,j,.85)
    S.kit('bench',7,-4,.025,math.pi/2);S.kit('bench',7,14,.025,math.pi/2);S.kit('bin',4,-20,.025)
    r['clear_routes']=[dict(a=list(a),b=list(b),width=2.6) for a,b in zip(walk,walk[1:])]
    r['entrance']['widthM']=2.6
    r['adaptations']=['Source stream, logs, stepping stones, woven tunnel, tree climbing deck and woodland edge retained. A separate continuous walking route connects both ends; play structures are static concept geometry, not construction or safety certification.']

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind]);sources=[]
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        path=a.reference_root/r['slug']/f"variant_{r['index']}{suffix}";data=path.read_bytes();assert len(data)>10000
        sources.append(dict(role=role,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    if a.output.exists():raise ValueError('Existing immutable candidate')
    r.update(source_references=sources,kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),runtime_status='NOT TESTED',terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,entrance=dict(x=0,y=-r['dimensions_m'][1]/2,widthM=2.7))
    if a.dry_run:print('DRY_RUN_PASS',r['id']);return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color,rough in [('stone',(.57,.53,.43),.85),('gravel',(.47,.40,.30),.95),('aggregate',(.58,.51,.39),.95),('roof',(.26,.28,.25),.9),('sage',(.28,.38,.23),.9),('ochre',(.58,.46,.18),.9),('blue',(.18,.29,.34),.9),('terracotta',(.43,.20,.12),.9),('hedge',(.09,.18,.065),.95),('leaf',(.17,.25,.07),.9),('crop',(.20,.32,.08),.9),('cabbage',(.18,.29,.17),.9),('glass',(.20,.30,.28),.25)]:material(name,color,rough)
    bs=S.MATS['glass'].node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=.65
    for name,color,rough in [('mulch',(.31,.22,.12),.95),('sand',(.65,.52,.32),.9),('water',(.18,.25,.22),.22),('rope',(.30,.27,.18),.9),('cutwood',(.54,.40,.24),.85)]:material(name,color,rough)
    globals()[a.kind](r)
    files=[Path(__file__),Path(S.__file__),Path(__file__).with_name('build_showcase_parks.py')]
    r['source_build_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for f in files:shutil.copy2(f,a.output/f.name)
    for item in sources:shutil.copy2(item['path'],a.output/Path(item['path']).name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    w,d=r['dimensions_m'];S.deliver(a.output,r,[('aerial',(w*.9,-d*.95,max(w,d)),(0,0,1),max(w,d)*1.42),('top',(0,0,100),(0,.001,0),max(w,d)*1.4),('detail',(w*.32,-d*.30,10),(-7,-10,1),21),('rear',(-w*.8,d*.85,21),(0,0,1),max(w,d)*1.3)],build_surfaces=a.kind!='nature')
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=25
    walks=[('walk',(0,-d/2-2,1.65),(0,-3,1.65)),('plot_walk',(-3,-13,1.65),(-13,-14,1.5))] if a.kind=='allotment' else [('walk',(0,-d/2-2,1.65),(0,-3,2.5)),('plot_walk',(9,-10,1.65),(0,8,2.5))]
    for name,pos,target in walks:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(a.output/'renders'/f'{name}.png');S.bpy.ops.render.render(write_still=True)
    r['runtime_contract']='Complete native park assembly owns ground; preserve geometry at native metric size in schema-v2 park runtime.'
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    report=dict(status='PASS_OFFLINE_GEOMETRY',assembly_sha256=r['assembly']['sha256'],bounds_m=r['bounds_m'],triangles=r['triangles'],dependency_closure='embedded GLB',runtime_status='NOT TESTED',visual_review='pending')
    (a.output/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
