"""Two finite, reference-led native parks. Preserve original catalogue images.

Blender --background --python-exit-code 1 --python <this file> --
  --kind pocket|greenway --kit <kit.json> --reference-root <openspaces> --output <fresh directory>
Always run --dry-run first. Prepared level ground only; no equipment scaling.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent))
import scene as S
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

SPECS = {
    'pocket': dict(id='urban_pocket_park_v0', revision='pocket-native-v003', title='Rustic Pocket Garden',
                   dimensions_m=[30,26], slug='urban-pocket-park',
                   programme='Circular lawn, gravel loop, curved timber bench, rustic pergola and dense flower borders'),
    'greenway': dict(id='linear_park_greenway_v0', revision='greenway-native-v002', title='Railway Meadow Greenway',
                     dimensions_m=[18,64], slug='linear-park-greenway',
                     programme='Curving multi-use path, preserved rail fragments, meadow planting, timber seating and a truss gateway'),
}


def material(name, color, roughness=.85):
    m=S.bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    node=m.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*color,1)
    node.inputs['Roughness'].default_value=roughness;S.MATS[name]=m


def polygon(name, points, mat, z=0):
    vertices=[Vector((x,y,z)) for x,y in points]
    triangles=tessellate_polygon([vertices])
    # Blender 5.2 returns vertex indices; older versions returned vectors.
    coords=[tuple(vertices[v] if isinstance(v,int) else v) for triangle in triangles for v in triangle]
    return S.mesh(name, coords, [tuple(range(i,i+3)) for i in range(0,len(coords),3)], mat)


def disc(name, x,y,r,mat,z=0):
    return polygon(name,[(x+r*math.cos(i*math.tau/128),y+r*math.sin(i*math.tau/128)) for i in range(128)],mat,z)


def ring(name,x,y,inner,outer,mat,start=0,end=math.tau,z=0):
    steps=max(2,math.ceil((end-start)*24))
    for i in range(steps):
        a=start+(end-start)*i/steps;b=start+(end-start)*(i+1)/steps
        S.mesh(name,[(x+r*math.cos(t),y+r*math.sin(t),z) for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]],[(0,1,2,3)],mat)


def flower_drift(x,y,seed,scale=.8):
    # Meadow-led drifts reserve the dense shrub meshes for occasional anchors.
    # This keeps native plant detail while bounding the whole park's triangles.
    kind=['flowering_perennial','meadow_grass','flowering_perennial','meadow_grass',
          'flowering_perennial','meadow_grass','meadow_grass','silver_shrub'][seed%8]
    S.kit(kind,x,y,0,(seed*2.399963)%math.tau,scale)


def pocket(r):
    w,d=r['dimensions_m'];cx=1;radius=7.3
    material('paving',(.49,.41,.29))
    S.ground(w,d,[(0,0,w,d,'soil')])
    # Every adjacent surface shares the same boundary vertices. Independently
    # tessellated arcs otherwise leave millimetre-wide unsupported seams.
    a=math.asin(1.5/radius)
    angles=sorted({i*math.tau/128 for i in range(129)}|{math.pi-a,math.pi+a})
    point=lambda t,r=radius:(cx+r*math.cos(t),r*math.sin(t))
    corners=[(0,math.pi/2,[(cx,d/2),(w/2,d/2),(w/2,0)]),
             (math.pi/2,math.pi-a,[(-w/2,1.5),(-w/2,d/2),(cx,d/2)]),
             (math.pi+a,3*math.pi/2,[(cx,-d/2),(-w/2,-d/2),(-w/2,-1.5)]),
             (3*math.pi/2,math.tau,[(w/2,0),(w/2,-d/2),(cx,-d/2)])]
    for start,end,boundary in corners:
        polygon('planted border',[point(t) for t in angles if start<=t<=end]+boundary,'soil')
    polygon('central lawn',[point(t,4.5) for t in angles[:-1]],'grass')
    for start,end in zip(angles,angles[1:]):
        polygon('gravel walk',[point(start,4.5),point(start),point(end),point(end,4.5)],'paving')
    entrance=[(-w/2,-1.5),(-w/2,1.5)]+[(cx+radius*math.cos(t),radius*math.sin(t))
        for t in angles if math.pi-a<=t<=math.pi+a]
    polygon('west entrance',entrance,'paving')
    ring('lawn stone edge',cx,0,4.48,4.52,'edge',z=.012)
    # Individually supported radial timber slats form the curved southern bench.
    for i in range(140):
        t=math.radians(200+i*140/139)
        centre=(cx+6.82*math.cos(t),6.82*math.sin(t),.47)
        o=S.box('curved seat slat',(0,0,0),(.63,.11,.065),'timber')
        o.location=centre;o.rotation_euler.z=t
        if i%12==0:
            for rr in (6.63,7.01):S.beam('seat support',(cx+rr*math.cos(t),rr*math.sin(t),0),(cx+rr*math.cos(t),rr*math.sin(t),.44),.045,'metal',8)
    # Paired rustic posts keep a clear walkway between their native positions.
    for i in range(7):
        t=math.radians(8+i*14)
        for rr in (4.34,7.05):S.beam('round timber post',(cx+rr*math.cos(t),rr*math.sin(t),0),(cx+rr*math.cos(t),rr*math.sin(t),2.85),.10,'timber',10)
        S.beam('radial pergola beam',(cx+4.0*math.cos(t),4.0*math.sin(t),2.88),(cx+7.34*math.cos(t),7.34*math.sin(t),2.88),.095,'timber',10)
        if i:
            prev=math.radians(8+(i-1)*14)
            for rr in (4.34,7.05):S.beam('curved pergola bearer',(cx+rr*math.cos(prev),rr*math.sin(prev),2.75),(cx+rr*math.cos(t),rr*math.sin(t),2.75),.12,'timber',10)
    trees=[(-7,7),(9,7),(9,-7)]
    for i,(x,y) in enumerate(trees):S.kit('shade_tree',x,y,0,i*1.8,1.45)
    count=0
    for i in range(32):
        for j in range(27):
            x=-13.7+i*.88;y=-11.5+j*.88
            if math.hypot(x-cx,y)<8.0 or (x<cx and abs(y)<2.15):continue
            if any(math.hypot(x-tx,y-ty)<.7 for tx,ty in trees):continue
            flower_drift(x+.1*math.sin(i+j),y+.1*math.cos(i-j),i+3*j,1.05)
            count+=1
    # Four low fieldstone markers remain outside the circulation corridor.
    for i,t in enumerate((math.radians(145),math.radians(195),math.radians(20),math.radians(335))):
        S.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(cx+7.95*math.cos(t),7.95*math.sin(t),.45))
        o=S.bpy.context.object;o.name='fieldstone';o.scale=(.65,.47,.56);o.rotation_euler.z=i*.8;o.data.materials.append(S.MATS['edge'])
    # Low timber fence around planting; west entry remains open.
    for y in (-12.6,12.6):
        for x in range(-14,15,3):
            S.beam('boundary post',(x,y,0),(x,y,.75),.065,'timber',8)
            if x<12:S.beam('boundary rail',(x,y,.55),(x+3,y,.55),.05,'timber',8)
    r['clear_routes']=[dict(a=[-14.8,0],b=[-4.6,0],width=1.8)]
    for i in range(36):
        a=i*math.tau/36;b=(i+1)*math.tau/36
        r['clear_routes'].append(dict(a=[cx+5.65*math.cos(a),5.65*math.sin(a)],b=[cx+5.65*math.cos(b),5.65*math.sin(b)],width=1.6))
    r['native_entrance']=dict(x=-15,y=0,widthM=2.4,arrivalX=-12,arrivalY=0)
    r['plant_count']=count
    r['source_interpretation']='Reference circular lawn, curved seat, rustic pergola, three trees and west entrance retained. Context buildings excluded; dimensions are a concept design.'
    return [('aerial',(31,-36,34),(0,0,0),42),('top',(0,0,65),(0,.001,0),40),('detail',(-21,-12,11),(0,1,1),27)]


def centre(y):
    return 2*math.sin((y+32)*math.tau/64)*min(1,max(0,(32-y)/14))


def steel_member(name,a,b,depth=.40,flange=.26):
    a,b=Vector(a),Vector(b);mid=(a+b)/2;length=(b-a).length
    rotation=(b-a).to_track_quat('Z','Y')
    for label,offset,size in [('web',0,(.025,depth,length)),
                               ('flange',-depth/2+.013,(flange,.026,length)),
                               ('flange',depth/2-.013,(flange,.026,length))]:
        o=S.box(name+' '+label,(0,0,0),size,'rail_steel')
        o.rotation_mode='QUATERNION';o.rotation_quaternion=rotation
        o.location=mid+rotation@Vector((0,offset,0))


def greenway(r):
    w,d=r['dimensions_m'];S.ground(w,d,[(0,0,w,d,'soil')])
    material('rail_steel',(.23,.13,.065),.65)
    for i in range(128):
        a=-32+i*.5;b=a+.5;ca=centre(a);cb=centre(b)
        alcove=next((by for by in (-14,8) if abs((a+b)/2-by)<2.5),None)
        la=ca-2.25 if alcove is None else min(ca-2.25,centre(alcove)-3.75)
        lb=cb-2.25 if alcove is None else min(cb-2.25,centre(alcove)-3.75)
        for name,mat,points in [
            ('path','paving',[(la,a),(ca+2.25,a),(cb+2.25,b),(lb,b)]),
            ('left meadow','soil',[(-9,a),(la,a),(lb,b),(-9,b)]),
            ('right meadow','soil',[(ca+2.25,a),(9,a),(9,b),(cb+2.25,b)])]:polygon(name,points,mat)
        for side in (-1,1):S.beam('path edge',(ca+side*2.27,a,.015),(cb+side*2.27,b,.015),.025,'edge',6)
        S.line((ca,a),(cb,b),.065,'paint')
    for x in (-8.85,8.85):S.box('retained railway edge',(x,0,.32),(.30,64,.64),'edge')
    # Preserved rail fragments run beside the walking route, with sleepers in soil.
    for x in (5.2,6.635):
        S.box('rail head',(x,-10,.07),(.065,28,.065),'rail_steel')
        S.box('rail web',(x,-10,.035),(.025,28,.06),'rail_steel')
    for i in range(45):S.box('rail sleeper',(5.9175,-23.8+i*.62,.015),(2.2,.19,.08),'timber')
    for y in (-14,8):
        x=centre(y)-3.2
        for offset in (-1.2,1.2):S.kit('backless_bench',x,y+offset,0,math.pi/2,1)
    # Source railway truss becomes a level pedestrian gateway, not a road crossing.
    for side in (-1,1):
        x=side*3.4
        for y in (23.5,27.5,31.5):
            S.box('bolted column foot',(x,y,.03),(.6,.65,.06),'rail_steel')
            steel_member('truss upright',(x,y,0),(x,y,4.2),.44,.28)
            for dx in (-.22,.22):
                for dy in (-.23,.23):S.beam('anchor bolt',(x+dx,y+dy,.06),(x+dx,y+dy,.105),.035,'metal',6)
        for z in (.18,4.2):steel_member('truss chord',(x,23.5,z),(x,31.5,z))
        for z in (.55,1.1):S.beam('gateway railing',(x,23.5,z),(x,31.5,z),.035,'rail_steel',8)
        for a,b in ((23.5,27.5),(27.5,31.5)):
            steel_member('truss diagonal',(x,a,.18),(x,b,4.2),.26,.18)
            steel_member('truss diagonal',(x,a,4.2),(x,b,.18),.26,.18)
    for y in (23.5,27.5,31.5):steel_member('gateway crossbeam',(-3.4,y,4.2),(3.4,y,4.2),.44,.28)
    count=0
    for i in range(16):
        for j in range(61):
            x=-7.6+i;y=-30+j
            if abs(x-centre(y))<3.0 or (4.5<x<7.25 and -24.5<y<4.5):continue
            if any(abs(y-by)<3.1 and abs(x-(centre(by)-3.2))<1.15 for by in (-14,8)):continue
            if y>22 and abs(x)<4.15:continue
            flower_drift(x+.23*math.sin(j+i),y+.23*math.cos(i-j),i+2*j,1.05)
            count+=1
    r['clear_routes']=[dict(a=[centre(-31.8),-31.8],b=[centre(-30),-30],width=1.8)]
    for y in range(-30,30,2):r['clear_routes'].append(dict(a=[centre(y),y],b=[centre(y+2),y+2],width=2.4))
    r['clear_routes'].append(dict(a=[centre(30),30],b=[centre(31.8),31.8],width=2.4))
    r['native_entrance']=dict(x=0,y=-32,widthM=2.4,arrivalY=-30)
    r['plant_count']=count
    r['source_interpretation']='Curving path, retained rails, meadow drifts, benches, low retaining edges and truss retained. Local prepared-ground model does not create an elevated connection to surrounding streets.'
    return [('aerial',(44,-56,53),(0,0,0),88),('top',(0,0,110),(0,.001,0),90),('detail',(-14,-29,10),(0,-12,1),31)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=SPECS,required=True);parser.add_argument('--kit',type=Path,required=True)
    parser.add_argument('--reference-root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--dry-run',action='store_true')
    a=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind])
    if a.output.exists():raise ValueError('Use a fresh output directory.')
    r['image_references']=[]
    for name in ('variant_0.png','variant_0_angle_60.jpg','variant_0_angle_90.jpg'):
        p=a.reference_root/r['slug']/name;data=p.read_bytes()
        if len(data)<1000:raise ValueError(f'Missing hydrated reference: {p}')
        r['image_references'].append(dict(path=f"{r['slug']}/{name}",sha256=hashlib.sha256(data).hexdigest()))
    r['kit_sha256']=hashlib.sha256(a.kit.read_bytes()).hexdigest()
    if a.dry_run:print('DRY_RUN_PASS',json.dumps(r));return
    a.output.mkdir(parents=True);S.init(a.kit)
    cameras=pocket(r) if a.kind=='pocket' else greenway(r)
    r['limitations']=['Prepared level concept only; fixed native composition. No competition, structural or accessibility certification.']
    for path in [Path(__file__),Path(S.__file__)]:shutil.copy2(path,a.output/path.name)
    for ref in r['image_references']:
        dest=a.output/'references'/ref['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.reference_root/ref['path'],dest)
    S.deliver(a.output,r,cameras,build_surfaces=False)
    scene=S.bpy.context.scene;cam=scene.camera;cam.data.type='PERSP';cam.data.lens=22
    cam.location=(-17,0,1.65) if a.kind=='pocket' else (0,-34,1.65)
    target=Vector((0,0,1.5)) if a.kind=='pocket' else Vector((0,-12,1.5))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)


if __name__=='__main__':main()
