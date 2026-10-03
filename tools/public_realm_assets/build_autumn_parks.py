"""Finite native park batch; source photographs, whole metric layouts, no paid APIs."""
import argparse,hashlib,json,math,random,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
from build_showcase_parks import material,polygon,ribbon,edge,hedge
from mathutils import Vector

SPECS={
 'splash':dict(id='student_urban_splash_plaza_v1',archetype='splash_pad_area',source_variant='splash_pad_area_v3',slug='splash-pad-water-play',index=3,title='Urban Splash-Play Plaza',dimensions_m=[32,36],programme='Colourful flowing paving, flush jets, supported tipping bucket and planted seating edges'),
 'labyrinth':dict(id='student_stone_labyrinth_garden_v1',archetype='labyrinth_meditation',source_variant='labyrinth_meditation_v0',slug='labyrinth-meditation-garden',index=0,title='Stone Labyrinth Garden',dimensions_m=[34,40],programme='Concentric connected limestone walk, quiet central stone seat, clipped hedges and layered enclosed garden'),
 'dog':dict(id='student_sheltered_dog_park_v1',archetype='dog_park',source_variant='dog_park_v0',slug='dog-park',index=0,title='Sheltered Dog Park',dimensions_m=[36,42],programme='Four turf rooms, three timber shade shelters, gravel circulation, timber rails, meadow edges and double-gate entry'),
}

def disc(name,x,y,r,mat,z=.01):
    polygon(name,[(x+r*math.cos(i*math.tau/80),y+r*math.sin(i*math.tau/80)) for i in range(80)],mat,z)

def planting(x,y,w,d,z=0):
    # Shared native leaf geometry, planted at soil datum, never stretched equipment.
    S.box('planting soil',(x,y,z-.045),(w,d,.09),'soil')
    for i in range(max(1,int(w/.60))):
        for j in range(max(1,int(d/.65))):
            xx=x-w/2+.32+i*.60;yy=y-d/2+.34+j*.65
            S.kit(['meadow_grass','flowering_perennial','silver_shrub'][(i+2*j)%3],xx,yy,z,(i+j)*1.3,.95)

def stonebed(x,y,w,d):
    edge('concrete planter',[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],'stone',.44,.22,0,True)
    planting(x,y,w-.3,d-.3,.34)

def jet(x,y,height=1.3,dx=0):
    disc('flush nozzle',x,y,.085,'metal',.024)
    pts=[(x+dx*t,y,.045+height*4*t*(1-t)) for t in [i/18 for i in range(19)]]
    for a,b in zip(pts,pts[1:]):S.beam('water spray',a,b,.018,'water',6)
    for r in (.20,.32,.46):
        for i in range(28):
            aa=i*math.tau/28;bb=(i+1)*math.tau/28
            S.line((x+dx+r*math.cos(aa),y+r*math.sin(aa)),(x+dx+r*math.cos(bb),y+r*math.sin(bb)),.018,'water',.028)

def splash(r):
    S.ground(32,36,[]);S.box('plaza ground',(0,0,-.06),(32,36,.12),'paving')
    # Adjacent strips share exactly the same curved boundaries, one surface owner.
    def bands(y):return [-11,-7+2*math.sin(y/8),-2+2*math.sin(y/7),3+2*math.sin(y/10),11]
    colors=['blue','sand','terracotta','blue']
    for j in range(144):
        y=-16+j*32/144;yy=y+32/144;aa=bands(y);bb=bands(yy)
        for i in range(4):polygon('flowing colour field',[(aa[i],y),(aa[i+1],y),(bb[i+1],yy),(bb[i],yy)],colors[i],.015)
    disc('dark wet play island',-4,2,5.5,'wet',.021)
    for y in (-1,2,5):
        for x in (-6,-3):jet(x,y,1.1+(x+6)*.20,1.1)
    for x,y in ((6,-6),(8,-6),(6,-3),(8,-3)):jet(x,y,.65,.12)
    # Two bearing legs, top yoke, pivot axle and genuinely hollow tapered bucket.
    for x in (2.3,4.7):
        S.beam('bucket steel column',(x,6,0),(x,6,4.9),.075,'metal',12)
        S.box('column footplate',(x,6,.035),(.32,.32,.07),'metal')
    S.beam('bucket axle',(2.3,6,4.0),(4.7,6,4.0),.065,'metal',12)
    S.beam('top yoke',(2.3,6,4.9),(4.7,6,4.9),.075,'metal',12)
    vs=[];fs=[]
    for radius,z in ((.48,3.5),(.78,4.6),(.73,4.6),(.43,3.55)):
        vs += [(3.5+radius*math.cos(i*math.tau/40),6+radius*math.sin(i*math.tau/40),z) for i in range(40)]
    for ring in range(3):
        for i in range(40):fs.append((ring*40+i,ring*40+(i+1)%40,(ring+1)*40+(i+1)%40,(ring+1)*40+i))
    fs.append(tuple(range(120,160)));S.mesh('hollow bronze splash bucket',vs,fs,'bronze')
    for i in range(15):
        x=2.85+i*.09;S.beam('water curtain',(x,5.55,.1),(x,5.65,3.53),.012,'water',5)
    # The source's large crescent planter is a defining part of the composition.
    crescent=[(-15,-14),(-15,14)]+[(-10-2.1*math.cos(y*math.pi/28),y) for y in [14-j*28/72 for j in range(73)]]
    polygon('crescent planting soil',crescent,'soil',.34)
    edge('crescent concrete planter',crescent,'stone',.44,.22,0,True)
    for j in range(43):
        yy=-13.6+j*.63
        for i in range(7):
            xx=-14.55+i*.60
            if xx < -10-2.1*math.cos(yy*math.pi/28)-.35:
                S.kit(['meadow_grass','silver_shrub','flowering_perennial'][(i+j)%3],xx,yy,.34,j*.9,.95)
    for y in (-10,4):stonebed(14,y,2.4,10)
    for x in (-7,7):stonebed(x,16.4,7,1.5)
    for x,y,rot in ((-9,-10,math.pi/2),(9,0,-math.pi/2),(-4,13,math.pi),(5,13,math.pi)):
        S.kit('bench',x,y,.02,rot)
    # Permeable perimeter represented by real paver joints.
    for side in (-1,1):
        for y in range(-16,17):
            for j in range(3):S.box('permeable paver',(side*(11.4+j*.65),y,.012),(.48,.78,.022),'stone')
    r['clear_routes']=[dict(a=[0,-18],b=[0,-11],width=3),dict(a=[0,-11],b=[9,-11],width=2),dict(a=[9,-11],b=[9,11],width=2)]
    r['adaptations']=['Reference palette, flush spray play, hollow bucket and planted plaza retained; surrounding buildings omitted. Water is static native geometry.']

def labyrinth(r):
    S.ground(34,40,[]);S.box('garden ground',(0,0,-.06),(34,40,.12),'grass')
    # A single continuous winding path rather than disconnected decorative rings.
    path=[]
    def curve(a,b,c,d):
        return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(2)) for t in [j/48 for j in range(49)]]
    radii=(12.4,10.6,8.8,7.0,5.2,3.4)
    for i,rad in enumerate(radii):
        gap=math.asin(1.6/rad);start=-math.pi/2+gap;end=3*math.pi/2-gap
        arc=[(rad*math.cos(start+(end-start)*j/240),rad*math.sin(start+(end-start)*j/240)) for j in range(241)]
        if i%2:arc.reverse()
        if i==0:path+=curve((1.6,-20),(1.6,-15.5),(arc[0][0]-2,arc[0][1]-.26),arc[0])[:-1]
        path+=arc
        if i<len(radii)-1:
            y0=arc[-1][1];y1=-math.sqrt(radii[i+1]**2-1.6**2);ym=(y0+y1)/2;rr=(y1-y0)/2;side=-1 if i%2==0 else 1
            path += [(side*(1.6-rr*math.sin(j*math.pi/36)),ym-rr*math.cos(j*math.pi/36)) for j in range(1,36)]
    last=path[-1];path.append((last[0]-1.5*math.cos(gap),last[1]+1.5*math.sin(gap)))
    ribbon('connected limestone labyrinth',path,1.15,'stone',.014)
    disc('central contemplation room',0,0,2.5,'stone',.017)
    for i in range(0,len(path)-1,5):
        p=path[i];q=path[i+1]
        if math.hypot(*p)<3.5:continue
        v=Vector((q[0]-p[0],q[1]-p[1])).normalized();normal=Vector((-v.y,v.x))*.56
        S.line((p[0]+normal.x,p[1]+normal.y),(p[0]-normal.x,p[1]-normal.y),.015,'edge',.02)
    for x in (-.9,.9):S.box('stone seat bearing',(x,.4,.22),(.32,.45,.44),'stone')
    S.box('central stone bench',(0,.4,.48),(2.5,.65,.15),'stone')
    # Boundary wall, gate piers and deep layered planting around the walk.
    edge('garden wall',[(-16,-19),(-16,19),(16,19),(16,-19),(3,-19)],'stone',1.1,.45,0)
    edge('garden entrance wall',[(-16,-19),(-.4,-19)],'stone',1.1,.45,0)
    for x in (-.4,3):
        S.box('gate pier',(x,-19,.8),(.60,.60,1.6),'stone');S.box('pier cap',(x,-19,1.65),(.74,.74,.12),'stone')
    hedge([(-14,-16),(-14,16),(14,16),(14,-16)],.8,.8)
    hedge([(-14,-16),(-3,-16)],.8,.8);hedge([(4,-16),(14,-16)],.8,.8)
    for side in (-1,1):
        for y in (-12,-7,0,7,12):
            S.kit('silver_shrub',side*14.6,y,0,y*.4,1.1)
        planting(side*10,17.5,8,1.4)
    for x in (-11,11):
        for y in (-15,15):S.kit('ornamental_tree',x,y,0,x*.3,.50)
    r['clear_routes']=[dict(a=[path[0][0],-20],b=[path[0][0],-13],width=1.15)]
    r['entrance']={'x':path[0][0],'y':-20,'widthM':1.15}
    r['adaptations']=['Six concentric limestone circuits and planted enclosure; ambiguous AI reference junctions resolved into a single connected winding walk. South entry aligns with walk.']

def rail(a,b,mesh=False):
    count=max(1,math.ceil(math.dist(a,b)/2.3))
    for i in range(count+1):
        x=a[0]+(b[0]-a[0])*i/count;y=a[1]+(b[1]-a[1])*i/count
        S.beam('timber fence post',(x,y,0),(x,y,1.25),.075,'timber',8)
    for z in (.35,.75,1.1):S.beam('timber fence rail',(*a,z),(*b,z),.052,'timber',8)
    if mesh:
        n=max(1,int(math.dist(a,b)/.14))
        for i in range(n+1):
            t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;S.beam('fine dog containment mesh',(x,y,.04),(x,y,1.1),.005,'metal',4)

def shelter(x,y):
    for dx in (-3,3):
        for dy in (-2,2):
            z=3.0+.10*dy;S.beam('shelter post',(x+dx,y+dy,0),(x+dx,y+dy,z),.11,'timber',8)
            S.beam('knee brace',(x+dx,y+dy,z-.65),(x+dx-math.copysign(.65,dx),y+dy,z),.06,'timber',8)
    for dy in (-2,2):S.beam('shelter bearing beam',(x-3.3,y+dy,3+.1*dy),(x+3.3,y+dy,3+.1*dy),.12,'timber',8)
    for i in range(39):
        xx=x-3.4+i*.175;S.beam('roundwood shelter roof',(xx,y-2.6,2.93),(xx,y+2.6,3.45),.08,'timber',8)

def dog(r):
    S.ground(36,42,[]);S.box('meadow park ground',(0,0,-.06),(36,42,.12),'grass')
    polygon('gravel social court',[(-14,-17),(14,-17),(14,17),(-14,17)],'gravel',.012)
    for x,y in ((-7,-9),(7,-9),(-7,9),(7,9)):
        disc('soft turf room',x,y,4.5,'grass',.019)
        if (x,y)!=(-7,-9):shelter(x,y)
        # Each rail enclosure retains a broad inward opening.
        rail((x-4.6,y-4.6),(x-4.6,y+4.6));rail((x-4.6,y+4.6),(x+4.6,y+4.6));rail((x+4.6,y+4.6),(x+4.6,y-4.6))
        rail((x-4.6,y-4.6),(x-1.6,y-4.6));rail((x+1.6,y-4.6),(x+4.6,y-4.6))
    # Contained perimeter with an entrance vestibule; open gate leaves in plan.
    for a,b in [((-16,-19),(-16,19)),((-16,19),(16,19)),((16,19),(16,-19)),((-16,-19),(-1.5,-19)),((1.5,-19),(16,-19)),((-1.5,-19),(-1.5,-16)),((1.5,-19),(1.5,-16))]:rail(a,b,True)
    for y in (-19,-16):rail((-1.5,y),(-1.5,y+1.2),True)
    ribbon('entry gravel',[(0,-21),(0,-13)],2.8,'gravel',.014)
    for x in (-16.9,16.9):planting(x,0,1.3,36)
    for y in (-19.8,19.8):
        for x in (-9,9):planting(x,y,12,1.0)
    for x,y in ((-12,-1),(12,1),(-3,14),(3,-4)):
        S.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,.4));o=S.bpy.context.object;o.name='grounded play boulder';o.scale=(1,.75,.55);o.data.materials.append(S.MATS['stone'])
    for x in (-3,3):S.kit('bench',x,0,0,math.copysign(math.pi/2,x))
    S.kit('bin',2,-17)
    r['clear_routes']=[dict(a=[0,-21],b=[0,14],width=2.8),dict(a=[-12,0],b=[12,0],width=2.4)]
    r['adaptations']=['Four turf rooms and three rustic shelters preserve reference programme. Fine containment mesh and double-entry vestibule added; gate leaves shown open.']

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind]);sources=[]
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        path=a.reference_root/r['slug']/f"variant_{r['index']}{suffix}";data=path.read_bytes();assert len(data)>10000
        sources.append(dict(role=role,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    if a.output.exists():raise ValueError('Existing immutable candidate')
    r.update(source_references=sources,kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),runtime_status='NOT TESTED',terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,entrance=dict(x=0,y=-r['dimensions_m'][1]/2,widthM=2.7))
    if a.dry_run:print('DRY_RUN_PASS',r['id']);return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color,rough in [('stone',(.57,.53,.43),.85),('gravel',(.44,.37,.27),.95),('water',(.50,.69,.70),.20),('wet',(.20,.23,.22),.5),('blue',(.22,.39,.42),.8),('sand',(.64,.47,.19),.8),('terracotta',(.47,.22,.14),.8),('bronze',(.33,.20,.10),.6),('hedge',(.09,.18,.065),.95),('leaf',(.17,.25,.07),.9)]:material(name,color,rough)
    globals()[a.kind](r)
    r['source_build_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(S.__file__))}
    for p in (Path(__file__),Path(S.__file__)):shutil.copy2(p,a.output/p.name)
    for item in sources:shutil.copy2(item['path'],a.output/Path(item['path']).name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    w,d=r['dimensions_m'];S.deliver(a.output,r,[('aerial',(w*.9,-d*.95,max(w,d)),(0,0,1),max(w,d)*1.42),('top',(0,0,100),(0,.001,0),max(w,d)*1.4),('detail',(w*.38,-d*.28,10),(0,0,1),max(w,d)*.65)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=25;cam.location=(0,-d/2-3,1.65);cam.rotation_euler=(Vector((0,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)
    r['runtime_contract']='Complete native park assembly owns ground; preserve geometry at native metric size in schema-v2 park runtime.'
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    report=dict(status='PASS_OFFLINE_GEOMETRY',assembly_sha256=r['assembly']['sha256'],bounds_m=r['bounds_m'],triangles=r['triangles'],dependency_closure='embedded GLB',runtime_status='NOT TESTED',visual_review='pending',not_claimed=['browser behaviour','human approval'])
    (a.output/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
