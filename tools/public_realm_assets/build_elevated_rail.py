"""One finite elevated rail pilot. Native modules and source-authored metric geometry."""
import argparse, hashlib, json, math, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import scene as S
import street_furniture as F
from build_autumn_streets import extra_module
from mathutils import Vector

VARIANT='student_elevated_garden_rail_v1'
WIDTH,LENGTH=26,48
SECTIONS=[('west_grove',-11,4,'grass'),('cycle_path',-7.5,3,'cycle'),('rain_garden',-5.5,1,'soil'),('west_walk',-3.25,3.5,'paving'),('pier_garden',0,3,'soil'),('east_walk',3.25,3.5,'paving'),('east_grove',7,4,'grass'),('promenade',11,4,'paving')]

def pier():
    S.box('flush pier foundation',(0,0,.025),(2.2,2.6,.05),'concrete')
    # Chamfered taper, expressed as real faces; cap and bearings remain distinct.
    outline=[(-.72,-.75),(-.52,-.95),(.52,-.95),(.72,-.75),(.72,.75),(.52,.95),(-.52,.95),(-.72,.75)]
    verts=[(x*scale,y,z) for scale,z in ((1,.04),(1,4.55),(2.1,5.65)) for x,y in outline]
    faces=[tuple(reversed(range(8))),tuple(range(16,24))]+[(k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i) for k in range(2) for i in range(8)]
    S.mesh('flared concrete pier',verts,faces,'concrete')
    S.box('pier crosshead',(0,0,5.88),(7.6,1.7,.46),'concrete')
    for x in (-3.2,3.2):
        S.box('bearing sole plate',(x,0,6.145),(.7,.9,.07),'steel')
        S.box('elastomer bearing',(x,0,6.205),(.6,.8,.05),'rubber')
        S.box('bearing top plate',(x,0,6.255),(.72,.9,.05),'steel')
    for z in (1.8,3.6):S.box('concrete form joint',(0,-.953,z),(1.02,.008,.012),'joint')
    S.beam('drain pipe',(.62,.87,.18),(.62,.87,5.65),.045,'steel',10)
    for z in (.5,2.5,4.5):S.box('pipe fixing',(.62,.89,z),(.15,.12,.04),'steel')
    S.box('underpass luminaire',(0,-.97,4.5),(.38,.08,.1),'lamp_lens')

def train():
    # Two original articulated metro cars, a static architectural furnishing.
    for cy in (-9.7,9.7):
        S.box('train underframe',(0,cy,8.51),(2.65,18.7,.28),'steel')
        body=S.box('train body',(0,cy,9.68),(2.78,18.65,2.16),'ivory')
        bevel=body.modifiers.new('formed body corners','BEVEL');bevel.width=.13;bevel.segments=3
        S.bpy.context.view_layer.objects.active=body;S.bpy.ops.object.modifier_apply(modifier=bevel.name)
        roof=S.box('train roof',(0,cy,10.83),(2.6,18.4,.18),'silver')
        bevel=roof.modifiers.new('rounded roof edge','BEVEL');bevel.width=.085;bevel.segments=3
        S.bpy.context.view_layer.objects.active=roof;S.bpy.ops.object.modifier_apply(modifier=bevel.name)
        for side in (-1,1):
            S.box('teal lower belt',(side*1.399,cy,8.97),(.024,18.55,.28),'teal')
            S.box('dark window band',(side*1.4,cy,9.96),(.028,18.1,.87),'glass_dark')
            for y in (-7.4,-4.5,-1.5,1.5,4.5,7.4):
                S.box('window mullion',(side*1.42,cy+y,9.96),(.028,.065,.89),'silver')
                S.box('window reflection',(side*1.421,cy+y+.5,10.16),(.012,.95,.08),'glass_reflect')
            for y in (-5.8,0,5.8):
                S.box('paired sliding doors',(side*1.427,cy+y,9.52),(.024,1.35,1.99),'silver')
                for d in (-.33,.33):S.box('door window',(side*1.445,cy+y+d,9.98),(.018,.53,.69),'glass_dark')
                S.box('door seam',(side*1.451,cy+y,9.52),(.008,.022,1.99),'joint')
        for y in (-6.5,6.5):
            S.box('bogie frame',(0,cy+y,8.27),(2.1,2.6,.26),'steel')
            for yy in (-.8,.8):
                for side in (-1,1):S.beam('steel wheel',(side*.67,cy+y+yy,8.31),(side*.94,cy+y+yy,8.31),.31,'rubber',20)
        for y in (-3.5,3.5):
            S.box('roof equipment',(0,cy+y,11.03),(1.6,2.8,.22),'silver')
            for yy in range(12):S.box('HVAC grille',(0,cy+y-1.2+yy*.21,11.15),(1.3,.035,.013),'joint')
        sign=1 if cy>0 else -1
        yy=cy+sign*9.34
        S.box('cab windshield',(0,yy,10.06),(2.42,.04,.91),'glass_dark')
        for x in (-.97,.97):S.box('cab lamp',(x,yy+sign*.025,9.12),(.24,.06,.13),'lamp_lens')
        S.box('destination display',(0,yy+sign*.025,10.62),(1.45,.045,.18),'metal')
    for yy in (-.22,-.11,0,.11,.22):S.box('articulation bellows',(0,yy,9.57),(2.2,.065,2.1),'rubber')

def buffer():
    for x in (-.72,.72):
        S.beam('buffer diagonal',(x,-.8,8.05),(x,.25,8.85),.09,'steel',8)
        S.box('buffer base',(x,0,8.1),(.18,1.8,.14),'steel')
    S.box('buffer crossbar',(0,.3,8.8),(2,.18,.25),'safety')
    for x in (-.65,.65):S.box('buffer pad',(x,.19,8.8),(.24,.12,.24),'rubber')

def lamp():
    S.box('lamp foot',(0,0,.04),(.32,.32,.08),'steel')
    S.box('lamp mast',(0,0,1.9),(.085,.085,3.8),'steel')
    S.box('lamp arm',(.32,0,3.82),(.72,.1,.09),'steel')
    S.box('lamp lens',(.55,0,3.77),(.33,.13,.025),'lamp_lens')

def end_cap():
    outline=[(-5.2,7.65),(5.2,7.65),(5.2,7.32),(3.65,7.12),(3.2,6.28),(-3.2,6.28),(-3.65,7.12),(-5.2,7.32)]
    S.mesh('girder end diaphragm',[(x,0,z) for x,z in outline],[tuple(range(8))],'concrete')
    for side in (-1,1):
        for x in (3.84,4.85):S.box('maintenance gate post',(side*x,0,8.28),(.05,.06,1.15),'steel')
        for z in (7.85,8.3,8.82):S.box('maintenance gate rail',(side*4.345,0,z),(1.05,.05,.04),'steel')
        for i in range(6):S.box('gate infill',(side*(3.94+i*.16),0,8.33),(.02,.025,.92),'steel')

def main():
    p=argparse.ArgumentParser();p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.kit.is_file()
    if a.output.exists():raise ValueError('Use a fresh immutable output directory')
    if a.dry_run:print('DRY_RUN_PASS',VARIANT,WIDTH,LENGTH);return
    a.output.mkdir(parents=True);S.init(a.kit);F.init()
    for name,color in dict(concrete=(.60,.59,.54),joint=(.28,.29,.27),steel=(.16,.19,.19),rubber=(.025,.03,.031),silver=(.61,.66,.65),ivory=(.88,.88,.8),teal=(.018,.29,.31),glass_dark=(.025,.078,.098),glass_reflect=(.18,.31,.34),safety=(.76,.39,.07),ballast=(.35,.36,.33)).items():F.material(name,color)
    for name in ('silver','ivory','teal','glass_dark'):
        S.MATS[name].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.34
    for n,b in [('rail_pier',pier),('rail_train',train),('rail_buffer',buffer),('rail_lamp',lamp),('rail_end',end_cap)]:extra_module(n,b)
    S.PLACEMENTS.clear();S.ground(WIDTH,LENGTH,[(x,0,w,LENGTH,m) for _,x,w,m in SECTIONS]);details=[];mesh_details=[]
    def detail(name,x,y,w,d,z,h,mat):
        details.append(dict(x=x,y=y,width=w,depth=d,z=z,height=h,material=mat));S.box(name,(x,y,z),(w,d,h),mat)
    # One continuous extrusion. Runtime clips this source at route ends and
    # repeats the same metric section without stretching native modules.
    profile=[(-5.2,7.65),(5.2,7.65),(5.2,7.32),(3.65,7.12),(3.2,6.28),(-3.2,6.28),(-3.65,7.12),(-5.2,7.32)]
    verts=[(x,y,z) for y in (-24,24) for x,z in profile]
    faces=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    S.mesh('continuous box girder',verts,faces,'concrete')
    mesh_details.append(dict(material='concrete',positions=[v for p in verts for v in p],indices=[v for f in faces for v in (f[0],f[1],f[2],f[0],f[2],f[3])]))
    for side in (-1,1):
        detail('edge parapet',side*5.05,0,.3,48,8.21,1.12,'concrete')
        detail('parapet coping',side*5.05,0,.34,48,8.79,.06,'silver')
        detail('recessed edge reveal',side*5.205,0,.012,48,7.88,.06,'joint')
        detail('service walkway',side*4.35,0,1.04,48,7.71,.12,'paving')
        detail('track slab',side*2.05,0,3,48,7.73,.16,'ballast')
        for rail in (-.7175,.7175):
            x=side*2.05+rail
            for w,z,h in ((.15,7.94,.025),(.035,8.005,.105),(.072,8.069,.023)):
                detail('rail section',x,0,w,48,z,h,'steel')
        for i in range(80):
            y=-23.7+i*.6
            detail('sleeper',side*2.05,y,2.6,.23,7.87,.10,'concrete')
            for offset in (-.82,-.61,.61,.82):detail('rail clip',side*2.05+offset,y,.055,.11,7.963,.04,'steel')
        for y in (-12,12):
            S.kit('shade_tree',-10.1 if side<0 else 7,y,0,side*.7,.85)
            S.kit('bench',-10 if side<0 else 8.8,y+4,0,math.pi/2)
            S.kit('rail_lamp',-5.6 if side<0 else 5.6,y-4,0,0)
    for y in (-22,0,22):S.kit('rail_pier',0,y)
    S.kit('rail_train',2.05,0)
    for y,yaw in ((-22.6,0),(22.6,math.pi)):
        for x in (-2.05,2.05):S.kit('rail_buffer',x,y,0,yaw)
    for y,yaw in ((-23.96,0),(23.96,math.pi)):S.kit('rail_end',0,y,0,yaw)
    for y in (-12,12):S.SURFACES.append(dict(x=0,y=y,width=3,depth=3,material='paving'))
    for y in range(-20,21,4):
        if abs(abs(y)-12)<2:continue
        for x in (-.95,.95,-5.5):S.kit('meadow_grass',x,y,0,y*.3,.65)
    for y in range(-22,23,2):
        for x in (-5.5,5.5,8.1,-12.2):
            S.kit('flowering_perennial' if y%4==0 else 'silver_shrub',x,y,0,y*.7,.62)
    r=dict(id=VARIANT,title='Elevated Garden Rail',dimensions_m=[WIDTH,LENGTH],fixed_width_m=WIDTH,fixture_length_m=LENGTH,pattern='stone',runtime_approved=False,reference='elevated-garden-rail/reference.png',sections=[dict(name=n,x=x,width=w,material=m) for n,x,w,m in SECTIONS],clear_routes=[dict(a=[x,-24],b=[x,24],width=3) for x in (-3.25,3.25,11)],image_references=[],source_notes=['Original City Prompt architectural concept. Static metro train, protected rail deck and continuous ground paths. No passenger station or animated transport simulation.','Prepared level site; straight 48–288 m routes. Cross streets must remain outside the landscaped corridor.'],kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest())
    r['program']=dict(schemaVersion=1,adapter='elevated-rail-v1',surfaceRegions=[],details=details,meshDetails=mesh_details,paving='stone',pavingModuleM=[1.2,.8],minLengthM=48,maxLengthM=288,preparedLevelOnly=True,baseLiftM=.025,palette={n:list(m.diffuse_color)[:3] for n,m in S.MATS.items() if n!='kit'})
    for f in (Path(__file__),Path(S.__file__),Path(F.__file__),Path(__file__).with_name('build_autumn_streets.py'),Path(__file__).with_name('sports_furniture.py')):shutil.copy2(f,a.output/f.name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    S.deliver(a.output,r,[('aerial',(54,-63,45),(0,0,3),78),('top',(0,0,100),(0,.001,0),67),('detail',(25,-35,15),(0,0,5),48)])
    shutil.copy2(a.output/'renders/aerial.png',a.output/'reference.png')
    photo=a.output/'reference.png';r['image_references']=[dict(path=photo.name,bytes=photo.stat().st_size,sha256=hashlib.sha256(photo.read_bytes()).hexdigest(),source_kind='render_of_exact_original_asset')]
    r['program']['surfaceRegions']=r['surface_regions']
    r['source_files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.output.glob('*.py')}
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    cam=S.bpy.context.scene.camera;cam.data.type='PERSP';cam.data.lens=27;cam.location=(3.25,-23,1.65);cam.rotation_euler=(Vector((3.25,10,2.7))-cam.location).to_track_quat('-Z','Y').to_euler();S.bpy.context.scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)

if __name__=='__main__':main()
