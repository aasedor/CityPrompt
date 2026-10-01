"""Two finite original park concepts, with visible and walkable surfaces shared."""
import argparse, hashlib, json, math, random, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
import build_climbable_parks as C
from build_showcase_parks import material, edge
from mathutils import Vector

SPECS={
 'treetop':dict(id='student_treetop_walk_v1',archetype='student_treetop_walk',title='Treetop Walk Park',dimensions_m=[56,64],programme='Twin stair ascents, a 4.2 m woodland promenade, shaded lookout and planted ground-level resting garden.'),
 'rose':dict(id='student_terraced_rose_v1',archetype='student_terraced_rose',title='Terraced Rose Garden',dimensions_m=[50,64],programme='Three formal rose terraces, paired stairs, flowering pergolas, sculpted fountain and sheltered seating.'),
}

def guard(points):
    dense=[]
    for a,b in zip(points,points[1:]):
        n=max(1,math.ceil(math.dist(a,b)/1.5))
        dense.extend(tuple(a[k]+(b[k]-a[k])*i/n for k in range(3)) for i in range(n))
    C.rail(dense+[points[-1]])
    # Closely spaced balusters make the raised edge visible from walking height.
    for a,b in zip(points,points[1:]):
        n=max(1,math.ceil(math.dist(a,b)/.18))
        for i in range(1,n):
            p=tuple(a[k]+(b[k]-a[k])*i/n for k in range(3))
            S.beam('guard baluster',(p[0],p[1],p[2]+.08),(p[0],p[1],p[2]+1.0),.012,'metal',6)

def deck(x0,x1,y0,y1,z):
    C.walk_quad('continuous timber deck',[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)])
    S.box('deck structural fascia',((x0+x1)/2,(y0+y1)/2,z-.15),(x1-x0,y1-y0,.28),'timber')
    for i in range(math.ceil(y0/.16),math.floor(y1/.16)+1):
        yy=i*.16;S.line((x0,yy),(x1,yy),.007,'joint',z+.001)
    for x in (x0+.35,x1-.35):
        for j in range(max(2,math.ceil((y1-y0)/4))):
            y=y0+.35+j*(y1-y0-.7)/(max(2,math.ceil((y1-y0)/4))-1)
            S.box('column footing',(x,y,.13),(.65,.65,.26),'stone')
            S.beam('paired timber deck column',(x,y,.25),(x,y,z-.18),.16,'timber',8)
    for x in (x0+.15,x1-.15):S.beam('longitudinal girder',(x,y0,z-.35),(x,y1,z-.35),.16,'timber',8)

def raised_pergola(x,y,z,w,d):
    before=set(S.bpy.context.scene.objects);S.pergola(x,y,w,d)
    for o in set(S.bpy.context.scene.objects)-before:o.location.z+=z

def treetop(r):
    S.box('woodland soil foundation',(0,0,-.13),(56,64,.2),'grass')
    C.floor('welcome gravel court',-20,20,-32,-20,0,holes=[(-18,-8,-30,-26),(8,18,-30,-26)])
    for x in (-13,13):C.planting_rect(x-5,x+5,-30,-26,0,31+int(x),1.25)
    C.floor('woodland ground trail',-2,2,-20,5,0)
    C.floor('woodland resting glade',-6,6,5,11,0)
    C.seat(-3,9,0);C.seat(3,9,0)
    left=[(0,-31.5,0),(0,-23,0),(-15,-23,0),(-15,-20,0)]
    right=[]
    for x in (-15,15):
        path=[]
        for y,z in [(-20,0),(-13,2.1)]:path.extend(C.stairs(x,y,y+7,z,z+2.1,width=4)[1:])
        for y,z in [(-20,0),(-13,2.1)]:
            for side in (-1,1):
                for j in range(1,40):
                    yy=y+j*7/40;zz=z+2.1*min((yy-y)/5.5,1)
                    S.beam('stair baluster',(x+side*2.15,yy,zz+.08),(x+side*2.15,yy,zz+1.0),.012,'metal',6)
        # Support the raised second flight all the way to the ground.
        for xx in (x-1.65,x+1.65):
            for yy in (-12.3,-6.7):
                S.box('stair tower footing',(xx,yy,.12),(.65,.65,.24),'stone')
                S.beam('stair tower support',(xx,yy,.24),(xx,yy,1.94),.18,'timber',8)
            S.beam('stair tower bearer',(xx,-13,1.86),(xx,-6,1.86),.15,'timber',8)
        if x<0:left.extend(path)
        else:right=path
        deck(x-2,x+2,-6,19,4.2)
        guard([(x-2.1,-6,4.2),(x-2.1,18.9,4.2)])
        guard([(x+2.1,-6,4.2),(x+2.1,18.9,4.2)])
    # North bridge joins side decks along full-width shared edges.
    deck(-17,17,19,23,4.2)
    guard([(-17.1,18.9,4.2),(-17.1,23.1,4.2),(-6.1,23.1,4.2)])
    guard([(17.1,18.9,4.2),(17.1,23.1,4.2),(6.1,23.1,4.2)])
    guard([(-12.9,18.9,4.2),(12.9,18.9,4.2)])
    deck(-6,6,23,29,4.2)
    guard([(-6.1,23,4.2),(-6.1,29.1,4.2),(6.1,29.1,4.2),(6.1,23,4.2)])
    raised_pergola(0,26,4.2,10,4.8)
    C.seat(-3,27.8,4.2);C.seat(3,27.8,4.2)
    # Tree crowns are measured kit geometry, kept clear of the stair/deck envelope.
    trees=[(-23,-19),(-23,-8),(-23,4),(-23,16),(23,-19),(23,-8),(23,4),(23,16),(-7,-20),(7,-20),(-7,-12),(7,-12),(-7,-1),(7,-1),(-7,11),(7,11),(-22,26),(22,26)]
    for i,(x,y) in enumerate(trees):S.kit('shade_tree',x,y,0,i*2.4,1.1 if abs(x)>20 else 1.03)
    rng=random.Random(601)
    bands=[(-26,-20,-22,28),(20,26,-22,28),(-11,-3.3,-21,3),(3.3,11,-21,3),(-11,11,12.5,17)]
    for k,(x0,x1,y0,y1) in enumerate(bands):
        S.box('woodland drift mulch',((x0+x1)/2,(y0+y1)/2,-.026),(x1-x0,y1-y0,.01),'soil')
        for i in range(math.ceil((x1-x0)/1.25)):
            for j in range(math.ceil((y1-y0)/1.28)):
                x=x0+.55+i*1.25+rng.uniform(-.12,.12);y=y0+.55+j*1.28+rng.uniform(-.12,.12)
                if x>x1-.3 or y>y1-.3 or any(math.hypot(x-a,y-b)<.65 for a,b in trees):continue
                S.kit('flowering_perennial' if (i//2+j//3+k)%4==0 else 'meadow_grass',x,y,0,rng.random()*math.tau,1.15)
    for x in (-22,22):
        for y in (-29,-25):S.kit('silver_shrub',x,y,0,0,1.35)
    C.ROUTES.extend([
        dict(name='Canopy circuit and lookout',points=left+[(-15,21,4.2),(0,21,4.2),(0,26,4.2),(0,21,4.2),(15,21,4.2),(15,-6,4.2),*list(reversed(right[:-1])),(15,-20,0),(15,-23,0),(0,-23,0),(0,-31.5,0)]),
        dict(name='Woodland ground garden',points=[(0,-31.5,0),(0,7,0),(4,7,0)])])
    r['walk_views']=[('entrance',(0,-29,1.65),(-15,-9,3)),('canopy',(-15,4,5.85),(0,24,5)),('lookout',(0,26,5.85),(3,-12,4))]

def petals(x,y,z,seed):
    """A small, reproducible rose shrub with real branching stems and flowers."""
    rng=random.Random(seed)
    for i in range(7):
        a=i*2.4;dx=math.cos(a)*.37;dy=math.sin(a)*.37;zz=z+.60+rng.random()*.40
        S.beam('rose branching stem',(x,y,z),(x+dx,y+dy,zz),.022,'leaf',6)
        for t in (.38,.62):
            cx=x+dx*t;cy=y+dy*t;cz=z+(zz-z)*t
            for s in (-1,1):
                S.mesh('rose lanceolate leaf',[(cx,cy,cz),(cx+.15*s,cy-.10,cz+.02),(cx+.28*s,cy,cz+.08),(cx+.15*s,cy+.10,cz+.04)],[(0,1,2),(0,2,3)],'leaf')
        verts=[];faces=[]
        for ring in range(2):
            for j in range(5):
                angle=j*math.tau/5+ring*.45;rad=.064 if ring else .10
                px=x+dx+rad*math.cos(angle);py=y+dy+rad*math.sin(angle);pz=zz+ring*.055
                base=len(verts);verts.append((px,py,pz+.045))
                for k in range(10):
                    b=k*math.tau/10;verts.append((px+.105*math.cos(b),py+.09*math.sin(b),pz+.028*math.sin(b*2)))
                faces.extend((base,base+1+k,base+1+(k+1)%10) for k in range(10))
        S.mesh('layered rose petals',verts,faces,'rose_pink' if seed%3 else 'rose_cream')

def rose_bed(bounds,z,seed):
    x0,x1,y0,y1=bounds
    S.box('rose bed soil',((x0+x1)/2,(y0+y1)/2,z-.04),(x1-x0,y1-y0,.08),'soil')
    edge('dressed limestone rose border',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],'stone',.12,.20,z,True)
    for i in range(max(1,int((x1-x0)/1.5))):
        for j in range(max(1,int((y1-y0)/1.7))):
            x=x0+.8+i*1.5;y=y0+.8+j*1.7
            if z>2 and math.hypot(x,y-16)<1.85:continue
            petals(x,y,z,seed+i*7+j)
            if (i+j)%3==0:S.kit('flowering_perennial',x+.45,y+.45,z,0,.65)

def rose(r):
    S.box('garden foundation',(0,0,-.16),(50,64,.24),'stone')
    levels=[(-32,-12,0),(-12,8,1.2),(8,32,2.4)]
    for level,(y0,y1,z) in enumerate(levels):
        beds=[(-22,-12,y0+3,y1-3),(12,22,y0+3,y1-3),(-4,4,y0+5,y1-7)]
        if level==2:beds=beds[:2]+[(-4,4,13,20)]
        holes=list(beds)
        if level<2:holes.extend([(x-2.2,x+2.2,y1-5.1,y1) for x in (-8,8)])
        C.floor('limestone garden terrace',-25,25,y0,y1,z,holes)
        if z:S.box('terrace earth and retaining body',(0,(y0+y1)/2,z/2-.03),(50,y1-y0,z-.06),'stone')
        for i,b in enumerate(beds):rose_bed(b,z,level*70+i*19)
        for x in (-23.4,23.4):
            for yy in (y0+3,y1-3):S.kit('ornamental_tree',x,yy,z,0,.58)
        for x in (-17,17):C.seat(x,y0+1.5,z,0)
        if level<2:
            for x in (-8,8):C.stairs(x,y1-5.1,y1,z,z+1.2)
            for a,b in [(-25,-10.25),(-5.75,5.75),(10.25,25)]:
                C.solid_wall('coursed limestone terrace',(a,y1),(b,y1),z,z+1.2)
                guard([(a,y1+.17,z+1.2),(b,y1+.17,z+1.2)])
    # Upper garden pavilion and small fountain retain a generous circulation loop.
    raised_pergola(0,27,2.4,13,6)
    for x in (-5.8,5.8):
        for y in (24.8,29.2):
            for k in range(3):petals(x,y,2.4+k*.65,401+int(y)+k)
    for x in (-4.3,4.3):C.seat(x,28.8,2.4)
    S.beam('fountain basin',(0,16,2.4),(0,16,2.85),1.05,'stone',48)
    S.beam('fountain water',(0,16,2.855),(0,16,2.875),.91,'water',48)
    S.beam('fountain pedestal',(0,16,2.88),(0,16,3.65),.18,'stone',16)
    S.beam('fountain upper bowl',(0,16,3.60),(0,16,3.80),.58,'stone',32)
    left=[(0,-31.5,0),(0,-29,0),(-8,-29,0)]
    for y,z in [(-12,0),(8,1.2)]:left.extend([(-8,y-5.1,z),(-8,y-1.5,z+1.2),(-8,y,z+1.2)])
    left.extend([(-8,23,2.4),(0,23,2.4),(0,27,2.4),(0,23,2.4),(8,23,2.4)])
    for y,z in [(8,1.2),(-12,0)]:left.extend([(8,y,z+1.2),(8,y-1.5,z+1.2),(8,y-5.1,z)])
    left.extend([(8,-29,0),(0,-29,0),(0,-31.5,0)])
    C.ROUTES.append(dict(name='Rose terraces and pergola circuit',points=left))
    r['walk_views']=[('entrance',(0,-29,1.65),(-5,20,4)),('roses',(-8,-3,2.85),(-17,4,1.8)),('pergola',(0,27,4.05),(0,-18,1))]

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind])
    if a.output.exists():raise ValueError('Preserve immutable candidates; choose a new output directory.')
    kit=a.kit.read_bytes();assert all(k in json.loads(kit) for k in ('shade_tree','ornamental_tree','bench','flowering_perennial','meadow_grass'))
    r.update(source_kind='original_user_requested_concept',design_basis='Two new high-quality parks requested in conversation; authored concepts following the conservatory-v013 composition/detail benchmark.',kit_sha256=hashlib.sha256(kit).hexdigest(),terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,runtime_status='NOT TESTED',entrance=dict(x=0,y=-32,widthM=4),clear_routes=[dict(a=[0,-32],b=[0,-29],width=4)])
    if a.dry_run:print('DRY_RUN_PASS',r['id']);return
    a.output.mkdir(parents=True);S.init(a.kit);S.ground(*r['dimensions_m'],[]);C.WALK.clear();C.ROUTES.clear()
    for name,color,rough in [('walk_surface',(.37,.27,.17) if a.kind=='treetop' else (.63,.58,.46),.88),('stone',(.57,.52,.42),.92),('joint',(.24,.20,.15),.96),('nosing',(.75,.68,.53),.88),('leaf',(.11,.25,.07),.9),('rose_pink',(.67,.12,.29),.72),('rose_cream',(.92,.76,.54),.72),('water',(.12,.32,.31),.2)]:material(name,color,rough)
    globals()[a.kind](r)
    obstacles=[]
    for q in S.PLACEMENTS:
        if q['kind']=='bench':
            w,d=(1.1,2.4) if abs(math.sin(q['yaw']))>.5 else (2.4,1.1)
            obstacles.append([q['x']-w/2,q['x']+w/2,q['y']-d/2,q['y']+d/2])
    r['walking']=dict(version=1,triangles=C.WALK,routes=C.ROUTES,maxStepM=.22,entrance=[0,-31.5,0],obstacles=obstacles)
    sources=[Path(__file__),Path(S.__file__),Path(C.__file__),Path(__file__).with_name('build_showcase_parks.py')]
    r['source_build_files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
    for f in sources:shutil.copy2(f,a.output/f.name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    w,d=r['dimensions_m'];views=r.pop('walk_views')
    S.deliver(a.output,r,[('aerial',(w*.9,-d*.92,61),(0,0,2),88),('top',(0,0,100),(0,.001,0),85),('detail',(24,-29,15),(0,-5,2),43),('rear',(-w*.8,d*.85,40),(0,0,1),85)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=24
    for name,pos,target in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(a.output/'renders'/f'{name}.png');S.bpy.ops.render.render(write_still=True)
    r['runtime_contract']='Complete fixed native assembly on prepared level ground; actual exported walk surfaces define circulation. No natural terrain, accessibility or construction certification.'
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    (a.output/'geometry-verification.json').write_text(json.dumps(dict(status='PASS_OFFLINE_GEOMETRY',assembly_sha256=r['assembly']['sha256'],bounds_m=r['bounds_m'],triangles=r['triangles'],dependency_closure='embedded GLB',runtime_status='NOT TESTED',visual_review='pending',walking_review='pending'),indent=2)+'\n')

if __name__=='__main__':main()
