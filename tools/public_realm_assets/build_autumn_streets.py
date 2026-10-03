"""Three reference-led street programs, with independently repeated native furniture."""
import argparse,hashlib,json,math,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
import street_furniture as F
from mathutils import Vector, Matrix

SPECS={
 'mews':dict(id='student_london_cobbled_mews_v1',title='London Cobbled Mews',slug='london-mews-lane',width=8,length=30,pattern='cobble',sections=[('shared_cobbled_lane',0,8,'paving')]),
 'cherry':dict(id='student_cherry_blossom_street_v1',title='Cherry Blossom Neighbourhood Street',slug='vancouver-cherry-blossom-street',width=20,length=40,pattern='stone',sections=[('west_walk',-8.5,3,'paving'),('west_verge',-6,2,'grass'),('road',0,10,'asphalt'),('east_verge',6,2,'grass'),('east_walk',8.5,3,'paving')]),
 'passeig':dict(id='student_barcelona_shaded_promenade_v1',title='Barcelona Shaded Promenade',slug='barcelona-passeig-grand-promenade',width=36,length=48,pattern='stone',sections=[('west_walk',-16,4,'paving'),('west_lane',-12,4,'asphalt'),('central_promenade',0,20,'paving'),('east_lane',12,4,'asphalt'),('east_walk',16,4,'paving')]),
}

def extra_module(name,builder):
    before=set(S.bpy.context.scene.objects);builder();obs=list(set(S.bpy.context.scene.objects)-before)
    S.bpy.context.view_layer.update()
    for o in obs:
        o.data=o.data.copy();o.data.transform(o.matrix_world);o.matrix_world.identity()
    S.KIT[name]=[o.data for o in obs]
    for o in obs:S.bpy.data.objects.remove(o,do_unlink=True)


def flower_planter():
    for z,r in ((.04,.38),(.12,.40)):
        S.beam('terracotta planter',(0,0,max(0,z-.04)),(0,0,z+.04),r,'terracotta',20)
    verts=[(r*math.cos(i*math.tau/24),r*math.sin(i*math.tau/24),z) for r,z in ((.38,.08),(.48,.66)) for i in range(24)]
    S.mesh('tapered planter wall',verts,[(i,(i+1)%24,(i+1)%24+24,i+24) for i in range(24)],'terracotta')
    S.beam('planter soil',(0,0,.60),(0,0,.64),.44,'soil',24)
    F.ring('open terracotta rim',.49,.44,.62,.08,'terracotta')
    S.kit('flowering_perennial',0,0,.64,0,.9)
    S.kit('silver_shrub',0,0,.64,.5,.55)

def planted_trellis():
    F.trellis()
    for o in list(S.bpy.context.scene.objects):
        if o.name.startswith('planter foliage'):S.bpy.data.objects.remove(o,do_unlink=True)
    for i in range(5):
        S.kit('flowering_perennial',-.96+i*.48,0,.55,i*.9,.65)
    for i in range(3):S.kit('silver_shrub',-.85+i*.85,.03,.55,i,.48)

def cherry_tree():
    # Author a broad cherry crown from the native branch/leaf topology. This is
    # baked into its own module; route extension never scales the module.
    for part in S.KIT['grove_tree']:
        data=part.copy()
        data.transform(Matrix.Diagonal((1.8,1.8,.8,1)))
        if 'foliage' in part.name:
            attr=data.color_attributes.get('Color')
            for i,color in enumerate(attr.data):
                f=.82+.18*((i*17)%19)/18;color.color=(.85*f,.42*f,.54*f,1)
        o=S.bpy.data.objects.new('native flowering cherry',data);S.bpy.context.collection.objects.link(o)

def flower_kiosk():
    # Complete florist pavilion: open counter, pitched roof, native planted tubs.
    for x in (-1.3,1.3):
        for y in (-1,1):S.box('florist post',(x,y,1.35),(.09,.09,2.7),'metal')
    S.box('florist counter',(0,.45,.94),(2.5,1,.12),'timber')
    S.box('counter front',(0,.92,.45),(2.5,.10,.85),'sage')
    S.mesh('florist pitched roof',[(-1.6,-1.3,2.65),(1.6,-1.3,2.65),(-1.6,0,3.15),(1.6,0,3.15),(-1.6,1.3,2.65),(1.6,1.3,2.65)],[(0,1,3,2),(2,3,5,4)],'metal')
    for x in (-1.95,1.95):
        for y in (-.75,.65):S.kit('autumn_flower_planter',x,y)
    for x in (-.75,0,.75):S.kit('flowering_perennial',x,.4,1.01,0,.65)

def paving(x,y,w,d):
    # Measured setts. The runtime uses this same running bond and palette.
    S.box('sett mortar bed',(x,y,-.06),(w,d,.12),'paving')
    groups={i:([],[]) for i in range(4)};tw,td=.30,.18
    a,b=x-w/2,x+w/2;c,e=y-d/2,y+d/2
    for j in range(math.floor(c/td),math.ceil(e/td)):
        yy0=max(c,j*td+.004);yy1=min(e,(j+1)*td-.004);offset=j%2*tw/2
        if yy1<=yy0:continue
        for i in range(math.floor((a-offset)/tw),math.ceil((b-offset)/tw)):
            xx0=max(a,i*tw+offset+.004);xx1=min(b,(i+1)*tw+offset-.004)
            if xx1<=xx0:continue
            v,f=groups[(i*13+j*7)%4];n=len(v);v.extend([(xx0,yy0,.003),(xx1,yy0,.003),(xx1,yy1,.003),(xx0,yy1,.003)]);f.append((n,n+1,n+2,n+3))
    for i,(v,f) in groups.items():
        if f:S.mesh('cobbled sett',v,f,'paving.tile'+str(i))

def build(kind,r):
    w,l=r['dimensions_m'];S.ground(w,l,[(x,0,width,l,mat) for _,x,width,mat in SPECS[kind]['sections']]);details=[]
    def detail(x,y,width,depth,z,height,mat):
        details.append(dict(x=x,y=y,width=width,depth=depth,z=z,height=height,material=mat));S.box('route detail',(x,y,z),(width,depth,max(.004,height)),mat)
    if kind=='mews':
        S.paving=paving
        for i,f in enumerate((.82,.94,1.04,1.13)):F.material('paving.tile'+str(i),tuple(c*f for c in (.38,.36,.31)))
        for side in (-1,1):
            for y in (-11,0,11):S.kit('autumn_flower_planter',side*3.25,y)
            for y in (-6,6):S.kit('autumn_planted_trellis',side*3.3,y,0,side*math.pi/2)
            S.kit('heritage_lantern',side*3.3,-13 if side<0 else 13)
        S.kit('bench',3.15,2.5,0,math.pi/2)
        for x in (-2.15,2.15):detail(x,0,.12,l,.007,.014,'edge')
        r['clear_routes']=[dict(a=[0,-15],b=[0,15],width=3.3)]
    elif kind=='cherry':
        for side in (-1,1):
            for y in (-15,-5,5,15):S.kit('autumn_cherry_tree',side*6,y)
            for x in (5,7):detail(side*x,0,.14,l,.05,.1,'warm_concrete')
            for y in (-10,10):
                # Flush side connections through verges, kept between full-size trees.
                S.SURFACES.append(dict(x=side*6,y=y,width=2,depth=1.8,material='paving'))
            S.kit('heritage_lantern',side*6,0)
        r['clear_routes']=[dict(a=[-8.5,-20],b=[-8.5,20],width=2.6),dict(a=[8.5,-20],b=[8.5,20],width=2.6)]
    else:
        for side in (-1,1):
            for y in (-18,-6,6,18):S.kit('shade_tree',side*6.7,y,0,.15*y,1.15)
            for y in (-12,12):S.kit('bench',side*8.5,y,0,side*math.pi/2)
            for y in (-18,0,18):S.kit('heritage_lantern',side*15.1,y)
            S.kit('autumn_florist_kiosk',side*4.8,0,0,side*math.pi/2)
            detail(side*10,0,.18,l,.07,.14,'warm_concrete')
            for y in (-21,-9,3,15):S.kit('street_bollard',side*9.65,y)
        r['clear_routes']=[dict(a=[0,-24],b=[0,24],width=4)]
    r['program']=dict(schemaVersion=1,adapter='showcase-street-v1',surfaceRegions=[],details=details,paving='brick' if kind=='mews' else 'stone',pavingModuleM=[.30,.18] if kind=='mews' else [1.2,.8],minLengthM=l,maxLengthM=480,preparedLevelOnly=True,baseLiftM=.025,palette={n:list(m.diffuse_color)[:3] for n,m in S.MATS.items() if n!='kit'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);spec=SPECS[a.kind];w,l=spec['width'],spec['length']
    refs=[a.reference_root/spec['slug']/('variant_0'+s) for s in ('.png','_angle_60.jpg','_angle_90.jpg')]
    for f in refs:assert f.is_file() and f.stat().st_size>10000,f
    if a.output.exists():raise ValueError('New immutable delivery directory required')
    if a.dry_run:print('DRY_RUN_PASS',spec['id']);return
    a.output.mkdir(parents=True);S.init(a.kit);F.init()
    for n,b in [('autumn_flower_planter',flower_planter),('autumn_planted_trellis',planted_trellis),('autumn_cherry_tree',cherry_tree),('autumn_florist_kiosk',flower_kiosk)]:extra_module(n,b)
    S.PLACEMENTS.clear()
    r=dict(id=spec['id'],title=spec['title'],dimensions_m=[w,l],fixed_width_m=w,fixture_length_m=l,pattern=spec['pattern'],runtime_approved=False,reference=('barcelona-passeig' if a.kind=='passeig' else spec['slug'])+'/reference.png',sections=[dict(name=n,x=x,width=width,material=mat) for n,x,width,mat in spec['sections']],clear_routes=[],image_references=[],source_notes=['Reference-led metre-scale route section; surrounding buildings and cars excluded. Fixed-size repeat furnishings; no assembly stretching.','Barcelona uses shared rectangular stone joints instead of the reference hexagonal paving.'],kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest())
    for i,f in enumerate(refs):
        target=a.output/('reference.png' if i==0 else f.name);shutil.copy2(f,target);r['image_references'].append(dict(path=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
    build(a.kind,r)
    for f in (Path(__file__),Path(S.__file__),Path(F.__file__)):shutil.copy2(f,a.output/f.name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    S.deliver(a.output,r,[('aerial',(w*1.5,-l*.95,l*.8),(0,0,1),l*1.4),('top',(0,0,100),(0,.001,0),l*1.4),('detail',(w*.5,-l*.3,9),(0,0,1),w*1.2)])
    r['program']['surfaceRegions']=r['surface_regions'];(a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    cam=S.bpy.context.scene.camera;cam.data.type='PERSP';cam.data.lens=26;cam.location=(0,-l/2-4,1.65);cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat('-Z','Y').to_euler();S.bpy.context.scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
