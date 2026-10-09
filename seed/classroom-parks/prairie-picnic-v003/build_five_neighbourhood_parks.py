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
    ribbon('continuous pedestrian paving',points,width,'paving',.009)
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


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    r=dict(SPECS[a.kind]);source=a.reference_root/r['slug']/'variant_0.png';data=source.read_bytes();assert len(data)>10000
    r.update(source_references=[dict(role='front',path=str(source),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())],kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),runtime_status='NOT TESTED',terrain_policy='prepared_level',ground_owner='assembly',native_scale_only=True,entrance=dict(x=0,y=-r['dimensions_m'][1]/2,widthM=3.0),generation_provider='built-in image_gen',reference_status='original generated conceptual photograph; not a real project')
    if a.output.exists():raise ValueError('Existing immutable candidate')
    if a.dry_run:print('DRY_RUN_PASS',r['id'],r['dimensions_m']);return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color,rough in [('joint',(.38,.37,.31),.9),('roof',(.19,.22,.21),.8),('grassleaf',(.23,.31,.10),.9),('straw',(.44,.39,.17),.9),('violet',(.40,.20,.38),.9),('cream',(.67,.61,.34),.9),('concrete',(.58,.57,.51),.85),('herb',(.25,.36,.19),.9)]:material(name,color,rough)
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
