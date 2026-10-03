"""Finite, original station-capable elevated railway variants (metres, Z up)."""
import argparse, hashlib, json, math, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import scene as S
import street_furniture as F
import build_elevated_rail as E
from build_autumn_streets import extra_module
from mathutils import Vector

SPECS={
    'skytrain':dict(id='skytrain_elevated_corridor_v0',parent='skytrain_elevated_corridor',
        title='SkyTrain Elevated Corridor · Modern Station Hub',slug='skytrain-elevated-corridor',
        metal=(.18,.32,.39),accent=(.055,.43,.56),glass=(.35,.66,.75),roof=(.72,.81,.82)),
    'civic':dict(id='elevated_rail_transit_corridor_v0',parent='elevated_rail_transit_corridor',
        title='Elevated Rail Transit · Parametric Flow Station',slug='elevated-rail-transit-corridor',
        metal=(.27,.29,.30),accent=(.66,.24,.12),glass=(.33,.49,.54),roof=(.89,.88,.79)),
}
WIDTH,LENGTH=26,48
SECTIONS=E.SECTIONS

def station(kind):
    """Two genuine side platforms, clear entry stairs and distinct canopy forms."""
    civic=kind=='civic'
    for side in (-1,1):
        # Track-side tactile strip, drainage, platform beams and waiting bay.
        x=side*5.7
        S.box('cantilevered platform base',(x,0,7.76),(4.6,36,.28),'concrete')
        S.box('platform deck',(x,0,7.935),(4.45,35.6,.075),'paving')
        S.box('platform tactile warning',(side*3.65,0,7.983),(.36,34.6,.022),'safety')
        for y in range(-16,17):
            S.box('tactile stud',(side*3.65,y,8.001),(.23,.09,.016),'safety')
        for y in (-14,-7,0,7,14):
            S.box('platform seat',(side*7.25,y,8.40),(.5,2.2,.11),'timber')
            S.box('seat pedestal',(side*7.25,y,8.18),(.12,1.1,.32),'metal')
        for y in (-16,-8,0,8,16):
            S.box('canopy column foot',(side*7.55,y,8.03),(.35,.35,.12),'metal')
            S.beam('slender canopy column',(side*7.55,y,8.06),(side*7.55,y,11.95),.085,'metal',12)
            S.box('platform luminaire',(side*7.0,y,11.8),(.72,.18,.04),'lamp_lens')
        # A protected waiting area remains visible through framed glazing.
        for y in range(-16,17,4):
            S.box('wind screen mullion',(side*8.0,y,9.75),(.06,.07,3.15),'metal')
        for y in (-14,-10,-6,-2,2,6,10,14):
            if y in (10,14):continue # real gap to the upper stair landing
            S.box('clear wind screen',(side*8.0,y,9.75),(.028,3.88,2.95),'glass')
        # Forty real treads: 0.193 m rise and 0.7 m run over 28 m.
        sx=side*8.7
        S.box('street entrance landing',(sx,-14.7,.045),(2.2,1.4,.09),'paving')
        for step in range(40):
            y=-14+(step+.5)*.7
            z=(step+1)*7.72/40
            S.box('stair tread',(sx,y,z-.045),(1.8,.69,.09),'paving')
            S.box('stair riser',(sx,y-.335,z/2),(.035,.03,z),'concrete')
            if step%5==0:S.box('stair nosing',(sx,y-.31,z+.006),(1.75,.035,.012),'safety')
        for offset in (-1.02,1.02):
            S.beam('inclined stair stringer',(sx+offset,-14,.12),(sx+offset,14,7.84),.10,'metal',10)
            S.beam('continuous handrail',(sx+offset,-14,1.0),(sx+offset,14,8.72),.045,'metal',10)
            for y in range(-14,15,3):
                z=(y+14)/28*7.72
                S.beam('handrail baluster',(sx+offset,y,z+.12),(sx+offset,y,z+1),.024,'metal',8)
        S.box('upper stair landing',(side*7.95,14,7.935),(3.3,2.3,.1),'paving')
        S.box('station sign panel',(side*7.98,-15.8,10.45),(.06,2.4,.52),'accent')
        S.box('wayfinding map',(side*9.6,-16.3,1.3),(.08,1.4,1.5),'glass')
    # A continuous, open roof; the cross section is fully modelled and
    # materially different for the two catalogue archetypes.
    for y in range(-18,19,2):
        profile=[]
        for i in range(17):
            x=-8+i
            if civic:
                z=12.10+1.10*(1-(x/8)**2)+.35*math.cos(y/7)
            else:
                z=12.15+.55*(1-(x/8)**2)+.18*math.sin(y/5)
            profile.append((x,y,z))
        for a,b in zip(profile,profile[1:]):S.beam('curved roof rib',a,b,.092,'roof',10)
    for side in (-1,1):
        for x in (side*1.5,side*5.5,side*7.7):
            for y in range(-17,18,2):
                mid=y+1
                if civic:
                    z=12.10+1.10*(1-(x/8)**2)+.35*math.cos(mid/7)
                    # White perforated canopy panels leave regular real apertures.
                    S.box('porous roof cassette',(x,mid,z-.10),(1.12,1.57,.08),'roof')
                    for cut in (-.38,.38):S.box('roof opening trim',(x+cut,mid,z-.04),(.028,.88,.028),'metal')
                else:
                    z=12.15+.55*(1-(x/8)**2)+.18*math.sin(mid/5)
                    S.box('translucent blue roof pane',(x,mid,z-.11),(1.35,1.91,.045),'glass')
                    S.box('roof cap seam',(x,mid+1,z-.08),(1.35,.045,.045),'metal')
    for y in (-18,18):
        S.box('canopy end fascia',(0,y,12.2),(16,.16,.28),'roof')
    # Visible concourse landmarks below deck without obstructing the public walks.
    for y in (-18,18):
        for side in (-1,1):
            S.box('arrival pylon',(side*10.2,y,1.65),(.44,.6,3.2),'accent')
            S.box('arrival pylon light',(side*10.2,y,3.22),(.46,.62,.045),'lamp_lens')

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=sorted(SPECS),required=True)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);spec=SPECS[a.kind]
    if not a.kit.is_file():raise ValueError('Missing exact source kit')
    if a.output.exists():raise ValueError('Use a fresh immutable output directory')
    if a.dry_run:print('DRY_RUN_PASS',spec['id'],WIDTH,LENGTH);return
    a.output.mkdir(parents=True);S.init(a.kit);F.init()
    palette=dict(concrete=(.60,.59,.54),joint=(.28,.29,.27),steel=(.16,.19,.19),rubber=(.025,.03,.031),
        silver=(.61,.66,.65),ivory=(.88,.88,.8),teal=spec['accent'],glass_dark=(.025,.078,.098),
        glass_reflect=(.18,.31,.34),safety=(.76,.55,.075),ballast=(.35,.36,.33),
        glass=spec['glass'],roof=spec['roof'],accent=spec['accent'])
    for name,color in palette.items():F.material(name,color)
    for name in ('silver','ivory','teal','glass_dark','glass','roof'):
        S.MATS[name].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.32
    for name,builder in [('rail_pier',E.pier),('rail_train',E.train),('rail_buffer',E.buffer),
                         ('rail_lamp',E.lamp),('rail_end',E.end_cap),('rail_station',lambda:station(a.kind))]:
        extra_module(name,builder)
    S.PLACEMENTS.clear();S.ground(WIDTH,LENGTH,[(x,0,w,LENGTH,m) for _,x,w,m in SECTIONS]);details=[];mesh_details=[]
    def detail(name,x,y,w,d,z,h,mat,station_cut=False):
        details.append(dict(x=x,y=y,width=w,depth=d,z=z,height=h,material=mat,**({'stationCut':True} if station_cut else {})))
        if not station_cut:S.box(name,(x,y,z),(w,d,h),mat)
        else:
            for cy,depth in ((-20,8),(20,8)):S.box(name,(x,cy,z),(w,depth,h),mat)
    profile=[(-5.2,7.65),(5.2,7.65),(5.2,7.32),(3.65,7.12),(3.2,6.28),(-3.2,6.28),(-3.65,7.12),(-5.2,7.32)]
    verts=[(x,y,z) for y in (-24,24) for x,z in profile]
    faces=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    S.mesh('continuous concrete guideway',verts,faces,'concrete')
    mesh_details.append(dict(material='concrete',positions=[v for pt in verts for v in pt],
        indices=[v for f in faces for v in (f[0],f[1],f[2],f[0],f[2],f[3])]))
    for side in (-1,1):
        detail('protective parapet',side*5.05,0,.3,48,8.21,1.12,'concrete',True)
        detail('parapet coping',side*5.05,0,.34,48,8.79,.06,'silver',True)
        detail('sidewalk below',side*4.35,0,1.04,48,7.71,.12,'paving')
        detail('track slab',side*2.05,0,3,48,7.73,.16,'ballast')
        for rail in (-.7175,.7175):
            x=side*2.05+rail
            for w,z,h in ((.15,7.94,.025),(.035,8.005,.105),(.072,8.069,.023)):
                detail('real rail section',x,0,w,48,z,h,'steel')
        for i in range(80):
            y=-23.7+i*.6
            detail('sleeper',side*2.05,y,2.6,.23,7.87,.10,'concrete')
            for offset in (-.82,-.61,.61,.82):detail('rail clip',side*2.05+offset,y,.055,.11,7.963,.04,'steel')
        for y in (-20,20):
            S.kit('shade_tree',-10.1 if side<0 else 10.1,y,0,side*.7,.78)
            S.kit('bench',-10.2 if side<0 else 10.2,y+2,0,math.pi/2)
            S.kit('rail_lamp',-5.6 if side<0 else 5.6,y-2)
    for y in (-22,0,22):S.kit('rail_pier',0,y)
    S.kit('rail_train',2.05,0)
    for y,yaw in ((-22.6,0),(22.6,math.pi)):
        for x in (-2.05,2.05):S.kit('rail_buffer',x,y,0,yaw)
    for y,yaw in ((-23.96,0),(23.96,math.pi)):S.kit('rail_end',0,y,0,yaw)
    S.kit('rail_station',0,0)
    for y in range(-20,21,4):
        for x in (-.95,.95,-5.5,5.5):S.kit('meadow_grass',x,y,0,y*.3,.52)
    r=dict(id=spec['id'],title=spec['title'],dimensions_m=[WIDTH,LENGTH],fixed_width_m=WIDTH,
        fixture_length_m=LENGTH,pattern='stone',runtime_approved=False,reference=spec['slug']+'/reference.png',
        sections=[dict(name=n,x=x,width=w,material=m) for n,x,w,m in SECTIONS],
        clear_routes=[dict(a=[x,-24],b=[x,24],width=3) for x in (-3.25,3.25,11)],
        image_references=[],source_notes=['City Prompt original exact station archetype. Two elevated side platforms and walkable stairs. Static metro display.','Prepared level site, straight 48–288 m; up to four deliberately placed stations.'],
        kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest())
    r['program']=dict(schemaVersion=1,adapter='elevated-station-v1',surfaceRegions=[],details=details,
        meshDetails=mesh_details,paving='stone',pavingModuleM=[1.2,.8],minLengthM=48,maxLengthM=288,
        preparedLevelOnly=True,baseLiftM=.025,palette={n:list(m.diffuse_color)[:3] for n,m in S.MATS.items() if n!='kit'})
    for source in (Path(__file__),Path(E.__file__),Path(S.__file__),Path(F.__file__),
                   Path(__file__).with_name('build_autumn_streets.py'),Path(__file__).with_name('sports_furniture.py')):
        shutil.copy2(source,a.output/source.name)
    try:
        cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for device in cp.devices:device.use=device.type!='CPU'
        S.bpy.context.scene.cycles.device='GPU'
    except Exception:pass
    S.deliver(a.output,r,[('aerial',(53,-63,47),(0,0,5),76),('top',(0,0,100),(0,.001,0),67),
                         ('detail',(26,-32,19),(0,0,8),49)])
    shutil.copy2(a.output/'renders/detail.png',a.output/'reference.png')
    photo=a.output/'reference.png';r['image_references']=[dict(path=photo.name,bytes=photo.stat().st_size,
        sha256=hashlib.sha256(photo.read_bytes()).hexdigest(),source_kind='render_of_exact_original_asset')]
    r['program']['surfaceRegions']=r['surface_regions']
    r['source_files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.output.glob('*.py')}
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    cam=S.bpy.context.scene.camera;cam.data.type='PERSP';cam.data.lens=27
    cam.location=(8.7,-15,1.65);cam.rotation_euler=(Vector((8.7,6,5))-cam.location).to_track_quat('-Z','Y').to_euler()
    S.bpy.context.scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)

if __name__=='__main__':main()
