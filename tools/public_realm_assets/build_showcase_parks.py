"""Three bounded reference-led native parks, for offline review before browser QA.

Each delivery preserves its references and generated recipe. Fixed native scale,
prepared level ground and complete assembly ownership; no provider calls.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sys

sys.path.insert(0,str(Path(__file__).parent))
import scene as S
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

SPECS={
 'woodland':dict(id='student_woodland_stream_garden_v1',archetype='japanese_garden',source_variant='japanese_garden_v1',index=1,
    title='Woodland Stream & Bridge Garden',slug='japanese-garden',dimensions_m=[46,58],
    programme='Winding stream, arched timber bridge, connected gravel walks, moss rocks, raked gravel room and woodland planting'),
 'reflecting':dict(id='student_reflecting_fountain_garden_v1',archetype='fountain_water_feature',source_variant='fountain_water_feature_v1',index=1,
    title='Reflecting Fountain Garden',slug='fountain-decorative-water-feature',dimensions_m=[34,48],
    programme='Angular two-lobed reflecting basin, four fountain jets, clipped hedges, formal trees and perimeter seating'),
 'court':dict(id='student_terraced_cafe_court_v1',archetype='sunken_plaza',source_variant='sunken_plaza_v0',index=0,
    title='Terraced Café & Fountain Court',slug='sunken-plaza',dimensions_m=[40,48],
    programme='Intimate limestone court, seven U-shaped seat steps, central fountain, clipped rim planting and shaded café terrace'),
}

def material(name,color,roughness=.8):
    m=S.bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness
    S.MATS[name]=m

def polygon(name,points,mat,z):
    verts=[Vector((x,y,z)) for x,y in points];tris=tessellate_polygon([verts])
    coords=[tuple(verts[v] if isinstance(v,int) else v) for tri in tris for v in tri]
    return S.mesh(name,coords,[tuple(range(i,i+3)) for i in range(0,len(coords),3)],mat)

def ribbon(name,points,width,mat,z=.012):
    verts=[]
    for i,p in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
        nx,ny=-dy/length*width/2,dx/length*width/2
        verts += [(p[0]+nx,p[1]+ny,z),(p[0]-nx,p[1]-ny,z)]
    return S.mesh(name,verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)],mat)

def edge(name,points,mat='edge',height=.12,width=.18,z=0,closed=False):
    # One mitered owner per corner; overlapping coplanar boxes flicker in capture.
    verts=[];faces=[];n=len(points)
    for i,p in enumerate(points):
        a=points[(i-1)%n] if closed or i else p;b=points[(i+1)%n] if closed or i<n-1 else p
        before=Vector((p[0]-a[0],p[1]-a[1]));after=Vector((b[0]-p[0],b[1]-p[1]))
        if before.length==0:before=after.copy()
        if after.length==0:after=before.copy()
        before.normalize();after.normalize();normal=Vector((-before.y-after.y,before.x+after.x)).normalized()
        offset=normal*(width/2/max(.3,normal.dot(Vector((-after.y,after.x)))))
        verts.extend((p[0]+s*offset.x,p[1]+s*offset.y,zz) for zz in (z,z+height) for s in (-1,1))
    for i in range(n if closed else n-1):
        a=i*4;b=((i+1)%n)*4
        faces.extend([(a+2,b+2,b+3,a+3),(a,a+1,b+1,b),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
    if not closed:faces.extend([(0,2,3,1),((n-1)*4,(n-1)*4+1,(n-1)*4+3,(n-1)*4+2)])
    S.mesh(name,verts,faces,mat)

def rock(x,y,sx=1,sy=.7,h=.5):
    S.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,h*.42))
    o=S.bpy.context.object;o.name='weathered moss stone';o.scale=(sx,sy,h);o.rotation_euler=(.15,.12,(x+y)*.19);o.data.materials.append(S.MATS['rock'])
    for f in o.data.polygons:f.use_smooth=True

def hedge(points,width=1,height=.75,base_z=0):
    ribbon('hedge rooted soil',points,width,'soil',base_z+.016)
    edge('clipped hedge body',points,'hedge',height,width,base_z+.025)
    rng=random.Random(round(sum(p[0]+p[1] for p in points)*100))
    verts=[];faces=[]
    for a,b in zip(points,points[1:]):
        n=max(1,int(math.dist(a,b)*23))
        for i in range(n):
            t=rng.random();x=a[0]+(b[0]-a[0])*t+rng.uniform(-width*.48,width*.48);y=a[1]+(b[1]-a[1])*t+rng.uniform(-width*.48,width*.48)
            z=base_z+height+rng.uniform(.01,.12);r=.09;k=len(verts)
            verts.extend([(x-r,y,z),(x,y-r,z),(x+r,y,z),(x,y+r,z),(x,y,z+.06)]);faces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
    S.mesh('living hedge leaf detail',verts,faces,'leaf')

def fountain_jet(x,y,h=1.5):
    S.beam('stainless fountain nozzle',(x,y,.06),(x,y,.46),.035,'metal',10)
    for i in range(8):
        a=i*math.tau/8;pts=[]
        for j in range(15):
            t=j/14;r=t*.48;pts.append((x+r*math.cos(a),y+r*math.sin(a),.19+h*(1-t*t)))
        for aa,bb in zip(pts,pts[1:]):S.beam('fountain water jet',aa,bb,.012,'jet',5)
    for radius in (.40,.65,.9):
        for i in range(50):
            a=i*math.tau/50;b=(i+1)*math.tau/50
            S.line((x+radius*math.cos(a),y+radius*math.sin(a)),(x+radius*math.cos(b),y+radius*math.sin(b)),.012,'ripple',.195)

def cafe(x,y,z=0):
    S.kit('picnic_table',x,y,z)
    S.beam('cafe parasol post',(x,y,z+.05),(x,y,z+2.65),.035,'metal',8)
    verts=[(x,y,z+2.8)]+[(x+1.6*math.cos(i*math.tau/8),y+1.6*math.sin(i*math.tau/8),z+2.38) for i in range(8)]
    S.mesh('ivory cafe parasol',verts,[(0,i+1,(i+1)%8+1) for i in range(8)],'canvas')
    for p in verts[1:]:S.beam('parasol rib',verts[0],p,.012,'timber',5)

def woodland(recipe):
    S.ground(46,58,[])
    S.box('native woodland ground',(0,0,-.065),(46,58,.13),'moss')
    def center(y):return 3.2*math.sin(y/8)+.8*math.sin(y/3.8)
    ys=[-27+i*.45 for i in range(121)];stream=[(center(y),y) for y in ys if -23<=y<=24]
    ribbon('stream stone bed',stream,6.2,'rock',.005);ribbon('stream water',stream,5.6,'water',.03)
    start_angle=math.atan2(stream[1][1]-stream[0][1],stream[1][0]-stream[0][0])+math.pi/2
    end_angle=math.atan2(stream[-1][1]-stream[-2][1],stream[-1][0]-stream[-2][0])-math.pi/2
    for (x,y),start in ((stream[0],start_angle),(stream[-1],end_angle)):
        for r,mat,z in ((3.1,'rock',.005),(2.8,'water',.03)):
            polygon('rounded stream head',[(x,y)]+[(x+r*math.cos(start+i*math.pi/24),y+r*math.sin(start+i*math.pi/24)) for i in range(25)],mat,z)
    walks=[]
    for side in (-1,1):
        points=[(center(y)+side*7.4,y) for y in ys]
        ribbon('bound gravel woodland walk',points,2.65,'gravel',.045);walks.append(points)
        recipe['clear_routes'] += [dict(a=a,b=b,width=2.1) for a,b in zip(points[::12],points[12::12])]
    entry=[(0,-29),(0,-27.5),(-5.5,-27.5),(-7.4+center(-24),-24)]
    ribbon('south entrance connection',entry,2.7,'gravel',.048)
    recipe['clear_routes'] += [dict(a=a,b=b,width=2.1) for a,b in zip(entry,entry[1:])]
    yy=-3.5;cx=center(yy);span=15.0
    def deck(t):return .045+.72*math.sin(math.pi*t)**2
    for i in range(62):
        t=(i+.5)/62;x=cx-span/2+span*t;S.box('arched bridge timber tread',(x,yy,deck(t)),(span/62-.012,2.55,.10),'timber')
    for dy in (-1.13,1.13):
        for i in range(61):
            a=i/61;b=(i+1)/61
            S.beam('bridge curved stringer',(cx-span/2+span*a,yy+dy,deck(a)-.10),(cx-span/2+span*b,yy+dy,deck(b)-.10),.13,'timber',8)
            S.beam('bridge timber handrail',(cx-span/2+span*a,yy+dy,deck(a)+1.04),(cx-span/2+span*b,yy+dy,deck(b)+1.04),.045,'timber',8)
        for i in range(16):
            t=i/15;x=cx-span/2+span*t;S.beam('bridge guard post',(x,yy+dy,deck(t)-.12),(x,yy+dy,deck(t)+1.08),.045,'timber',6)
    # Boulders and low drifts occupy banks, never the gravel walks.
    for i,y in enumerate(range(-24,27,3)):
        for side in (-1,1):
            if abs(y-yy)<2.1:continue
            x=center(y)+side*(3.25+(i%3)*.3);rock(x,y,.65+(i%3)*.18,.52,.48+(i%2)*.18)
            for j in range(3):S.kit(('silver_shrub','meadow_grass','flowering_perennial')[j],x+side*1.1,y+j*.48,0,(i+j)*1.8,.7)
    # Raked gravel room, stone group and native-size bench alcoves.
    S.box('raked gravel room',(14.4,13,.018),(9,12,.035),'gravel')
    for i in range(47):S.line((10.2,7.3+i*.24),(18.6,7.3+i*.24),.016,'rake',.044)
    for x,y in ((13,12),(15,14),(13.8,15.2)):rock(x,y,1.0,.65,.85)
    trees=[(-19,y) for y in (-23,-13,-3,7,17,24)]+[(19,y) for y in (-23,-13,-3,23)]
    trees += [(-13,-24),(-13,-10),(-13,5),(-12,24),(12,-24),(15,2),(8,24),(-20.4,-18),(-20,12),(-14,20),(20.2,18),(20.2,8),(10,-11),(12,-2)]
    for i,(x,y) in enumerate(trees):
        S.kit('grove_tree' if i%3 else 'ornamental_tree',x,y,0,i*.8,1.05)
        for j in range(2):S.kit('silver_shrub',x+math.cos(i+j)*1.2,y+math.sin(i+j)*1.1,0,j*1.9,.65)
    for i,(x,y) in enumerate([(-15,-16),(-15,0),(-14,16),(14,-18),(14,-7),(12,23)]):
        S.box('gravel rest alcove',(x,y,.025),(4.2,3.5,.05),'gravel');S.kit('bench',x,y,0,math.pi/2 if x<0 else -math.pi/2)
        nearest=min(walks[0 if x<0 else 1],key=lambda p:abs(p[1]-y));ribbon('connected seating spur',[(x,y),nearest],1.8,'gravel',.048)
    rng=random.Random(9927)
    for i in range(370):
        x=rng.uniform(-20,20);y=rng.uniform(-26,26)
        if abs(x-center(y))<9.6 or (x>9 and y>5):continue
        S.kit('meadow_grass' if i%3 else 'flowering_perennial',x,y,0,i*2.4,.65)
    recipe['adaptations']=['Two eye-height woodland references agree; the supplied 90-degree file repeats the oblique view, so unseen plan proportions are inferred.',
        'The native stand-alone garden excludes background buildings and uses the shared City Prompt tree family.']

def reflecting(recipe):
    S.ground(34,48,[(0,0,34,48,'paving')])
    outline=[(-6,-18),(6,-18),(9,-10),(5,0),(9,10),(6,18),(-6,18),(-9,10),(-5,0),(-9,-10)]
    polygon('opaque reflecting basin bed',outline,'poolstone',.075);polygon('reflecting water',outline,'water',.19)
    edge('limestone basin coping',outline,'stone',.39,.56,0,True)
    for x in (-3,3):
        for y in (-10,10):fountain_jet(x,y,1.45 if x<0 else 1.75)
    for side in (-1,1):
        hedge([(side*7,-19.7),(side*10.9,-10),(side*6.9,0),(side*10.9,10),(side*7,19.7)],.95,.75)
        for y in (-17,-5,7,19):
            S.kit('grove_tree',side*14.8,y,0,y*.1,.82)
        for y in (-11,1,13):S.kit('bench',side*14.65,y,0,side*math.pi/2)
        for y in (-21,21):S.kit('light',side*15.0,y)
    recipe['clear_routes']=[dict(a=[0,-24],b=[0,-22],width=3),dict(a=[0,-22],b=[-12.5,-22],width=2),
        dict(a=[-12.5,-22],b=[-12.5,21],width=1.8),dict(a=[0,-22],b=[12.5,-22],width=2),dict(a=[12.5,-22],b=[12.5,21],width=1.8)]
    recipe['adaptations']=['Exact angular two-lobed basin and four-jet composition; perimeter trees and benches complete the stand-alone park instead of adding surrounding buildings.']

def court(recipe):
    S.ground(40,48,[(0,0,40,48,'paving')])
    # The photographed bowl is seated at the native datum. A clear southern
    # opening reaches that datum; steps rise around three sides. No excavation
    # below prepared ground or hidden stair requirement at the entrance.
    for i in range(7):
        x=13+(i+.5)*.64;z=(i+1)*.18
        for side in (-1,1):S.box('limestone seat step',(side*x,1,z/2),(.64,30,z),'stone')
        S.box('north limestone seat step',(0,16+(i+.5)*.64,z/2),(26+2*(i+1)*.64,.64,z),'stone')
        for side in (-1,1):
            for yy in range(-13,16,2):S.line((side*(x-.28),yy),(side*(x+.28),yy),.014,'edge',z+.004)
    for side in (-1,1):
        S.box('supported raised side rim',(side*18.14,3,.63),(1.32,36,1.26),'stone')
        S.box('raised rim planting soil',(side*18.14,3,1.25),(1.1,36,.20),'soil')
        hedge([(side*18.14,-14),(side*18.14,20)],1.05,.85,1.26)
    S.box('supported north retaining rim',(0,21.14,.63),(37.6,1.32,1.26),'stone')
    S.box('north planter rim',(0,21.14,1.25),(36,1.15,.2),'soil');hedge([(-18,21.14),(18,21.14)],1.05,.85,1.26)
    outline=[(-2.7,-5.2),(2.7,-5.2),(2.7,2.8),(-2.7,2.8)]
    polygon('court basin bed',outline,'poolstone',.07);polygon('court pool',outline,'water',.20);edge('court pool coping',outline,'stone',.48,.50,0,True)
    S.box('bronze fountain pedestal',(0,-1.2,.66),(1.6,1.6,.94),'stone')
    for i in range(3):
        a=i*math.tau/3;S.beam('abstract bronze fountain',(.6*math.cos(a),-1.2+.6*math.sin(a),1.0),(.8*math.cos(a+.8),-1.2+.8*math.sin(a+.8),2.3),.16,'bronze',8)
    for x in (-1.55,1.55):fountain_jet(x,-1.2,.8)
    for x in (-8.8,8.8):
        for y in (-10,7):cafe(x,y,0)
    for x in (-15.2,15.2):
        for y in (-20,22.75):S.kit('grove_tree',x,y,0,y*.12,.65)
    for x in (-9,9):
        S.kit('bench',x,-20,0,0);S.kit('light',x,-22.2)
    recipe['clear_routes']=[dict(a=[0,-24],b=[0,-8],width=3),dict(a=[0,-8],b=[-5,-8],width=2),dict(a=[-5,-8],b=[-5,12],width=2),
        dict(a=[0,-8],b=[5,-8],width=2),dict(a=[5,-8],b=[5,12],width=2)]
    recipe['adaptations']=['U-shaped limestone bowl, central fountain and cafe program follow the reference.',
        'Bowl floor is at prepared-site datum and terraces rise around it, with a flush south entrance; no terrain excavation or surrounding buildings are supplied.']

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=SPECS,required=True)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind]);r['clear_routes']=[]
    sources=[]
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        path=a.reference_root/r['slug']/f"variant_{r['index']}{suffix}";data=path.read_bytes()
        sources.append(dict(role=role,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    if a.output.exists():raise ValueError('Preserve existing candidates; choose a new output directory.')
    r.update(source_references=sources,kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),runtime_status='NOT TESTED',
             terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,entrance={'x':0,'y':-r['dimensions_m'][1]/2,'widthM':2.7})
    if a.dry_run:print('DRY_RUN_PASS',r['id'],len(sources));return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color,rough in [('stone',(.60,.55,.44),.85),('rock',(.23,.27,.23),.95),('moss',(.17,.23,.09),.95),
       ('gravel',(.48,.43,.31),.95),('water',(.055,.18,.16),.14),('poolstone',(.13,.16,.14),.85),('rake',(.32,.30,.22),.9),
       ('jet',(.62,.75,.73),.18),('ripple',(.25,.39,.35),.22),('leaf',(.17,.25,.07),.9),('hedge',(.09,.18,.065),.95),
       ('canvas',(.78,.73,.62),.85),('bronze',(.25,.20,.10),.6)]:material(name,color,rough)
    globals()[a.kind](r)
    S.bpy.context.scene.cycles.denoising_use_gpu=False
    # Grade review checks actual assembly bounds and rejects missing dependencies.
    r['source_build_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(S.__file__))}
    for p in (Path(__file__),Path(S.__file__)):shutil.copy2(p,a.output/p.name)
    for item in sources:shutil.copy2(item['path'],a.output/Path(item['path']).name)
    w,d=r['dimensions_m'];S.deliver(a.output,r,[('aerial',(w*.9,-d*.95,max(w,d)),(0,0,1),max(w,d)*1.42),
        ('top',(0,0,100),(0,.001,0),max(w,d)*1.4),('detail',(w*.42,-d*.28,12),(0,-3,1),max(w,d)*.6)],build_surfaces=a.kind!='woodland')
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=25;cam.location=(0,-d/2-5,1.65)
    cam.rotation_euler=(Vector((0,-d/2+13,1.65))-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)
    report=dict(status='PASS_OFFLINE_GEOMETRY',assembly_sha256=r['assembly']['sha256'],bounds_m=r['bounds_m'],triangles=r['triangles'],
        dependency_closure='embedded GLB',runtime_status='NOT TESTED',visual_review='pending',not_claimed=['terrain fit','browser behaviour','human approval'])
    (a.output/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
