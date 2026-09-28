"""Finite native street trio. Measured bands + rigid modules, never stretched previews."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
import street_furniture as F
from mathutils import Vector

SPECS={
 'tram':dict(id='student_grass_tram_avenue_v1',title='Garden Tram Avenue',slug='light-rail-tram-avenue',index=2,width=22,length=48,
  sections=[('west_walk',-7.3,7.4,'paving'),('tracks',0,7.2,'grass'),('east_walk',7.3,7.4,'paving')]),
 'promenade':dict(id='student_vine_pergola_promenade_v1',title='Vine Pergola Promenade',slug='riverfront-promenade',index=0,width=13,length=36,
  sections=[('garden',-5.25,2.5,'soil'),('promenade',.75,9.5,'paving'),('waterfront_edge',6,1,'paving')]),
 'boulevard':dict(id='student_grand_haussmann_boulevard_v1',title='Grand Haussmann Boulevard',slug='haussmann-boulevard',index=0,width=32,length=48,
  sections=[('west_walk',-11,10,'paving'),('road',0,12,'asphalt'),('east_walk',11,10,'paving')]),
}

def extra_module(name,builder):
    before=set(S.bpy.context.scene.objects);builder();obs=list(set(S.bpy.context.scene.objects)-before)
    S.bpy.context.view_layer.update()
    for o in obs:
        o.data.transform(o.matrix_world);o.matrix_world.identity()
    S.KIT[name]=[o.data for o in obs]
    for o in obs:S.bpy.data.objects.remove(o,do_unlink=True)

def ivy_pergola():
    for x in (-1.8,1.8):
        for y in (-2.6,2.6):
            S.box('stone post shoe',(x,y,.13),(.32,.32,.26),'warm_concrete')
            S.box('timber pergola post',(x,y,1.6),(.18,.18,3.2),'timber')
        S.box('long pergola carrier',(x,0,3.05),(.18,5.6,.30),'timber')
    for y in [i*.35 for i in range(-8,9)]:S.box('pergola cross rafter',(0,y,3.28),(4.0,.075,.24),'timber')
    for x in (-1.8,1.8):
        for y in (-2.6,2.6):
            S.beam('pergola knee',(x,y,2.4),(x,y-math.copysign(.65,y),3),.065,'timber',6)
            for i in range(19):
                z=.3+i*.15;xx=x+.1*math.sin(i);yy=y+.1*math.cos(i)
                S.beam('climbing vine',(xx,yy,z),(x+.1*math.sin(i+1),y+.1*math.cos(i+1),z+.15),.018,'vine',5)
    for i in range(330):
        x=-1.95+((i*1.231)%3.9);y=-2.72+((i*.813)%5.44);z=3.38+.045*math.sin(i)
        S.mesh('overhead vine leaf',[(x-.12,y,z),(x,y-.15,z+.035),(x+.12,y,z),(x,y+.13,z-.035)],[(0,1,2),(0,2,3)],'vine')

def iron_guard():
    for y in (-1.45,1.45):
        S.beam('iron guard post',(0,y,0),(0,y,1.15),.045,'metal',8)
        S.beam('iron finial',(0,y,1.13),(0,y,1.24),.063,'metal',8)
    for z in (.17,1.07):S.beam('continuous iron rail',(0,-1.5,z),(0,1.5,z),.024,'metal',8)
    for i in range(20):S.beam('guard vertical',(0,-1.425+i*.15,.17),(0,-1.425+i*.15,1.07),.012,'metal',6)

def morris_column():
    S.beam('Morris stone foot',(0,0,0),(0,0,.16),.71,'warm_concrete',32)
    S.beam('Morris cylinder',(0,0,.16),(0,0,2.6),.56,'sage',32)
    for z in (.24,2.45,2.64):S.beam('Morris cornice',(0,0,z),(0,0,z+.08),.66,'metal',32)
    for i in range(8):
        a=i*math.tau/8
        for j in range(5):
            b=a+(j-2)*.09
            S.beam('poster cream field',(.569*math.cos(b),.569*math.sin(b),.65),(.569*math.cos(b),.569*math.sin(b),2.15),.04,'cream',4)
        for z in (1.1,1.4,1.7):
            S.beam('poster coloured line',(.605*math.cos(a-.14),.605*math.sin(a-.14),z),(.605*math.cos(a+.14),.605*math.sin(a+.14),z),.014,'terracotta',4)
    verts=[(.83*math.cos(i*math.tau/32),.83*math.sin(i*math.tau/32),2.77) for i in range(32)]+[(0,0,3.2)]
    S.mesh('Morris crown',verts,[(i,(i+1)%32,32) for i in range(32)],'metal')

def catenary():
    S.beam('catenary foundation',(0,0,0),(0,0,.18),.20,'warm_concrete',12)
    S.beam('catenary mast',(0,0,.18),(0,0,7.0),.095,'metal',12)
    S.beam('catenary arm',(0,0,6.55),(-10,0,6.55),.05,'metal',8)
    S.beam('catenary tie',(0,0,6.95),(-9.7,0,6.55),.014,'metal',5)
    for x in (-5.2,-9.2):S.beam('contact dropper',(x,0,6.55),(x,0,6.15),.012,'metal',6)

def tram_stop():
    # Whole 3.2 x 28 m platform, two 1:12 end ramps, 2 m clear boarding strip.
    S.box('native stop platform',(0,0,.15),(3.2,20,.30),'warm_concrete')
    for sign in (-1,1):
        a=sign*10;b=sign*13.6
        S.mesh('full end access ramp',[(-1.6,a,0),(1.6,a,0),(-1.6,a,.30),(1.6,a,.30),(-1.6,b,0),(1.6,b,0)],[(0,1,3,2),(2,3,5,4),(0,4,5,1),(0,2,4),(1,5,3)],'warm_concrete')
    S.box('platform tactile margin',(-1.4,0,.305),(.32,19.8,.01),'cream')
    for y in [i*.27 for i in range(-35,36)]:
        for x in (-1.49,-1.37,-1.25):S.beam('tactile stud',(x,y,.31),(x,y,.32),.019,'warm_concrete',6)
    for y in (-6,0,6):
        S.box('cantilever canopy mast',(1.24,y,1.72),(.13,.14,2.84),'metal')
        S.beam('canopy cantilever',(1.24,y,3.1),(-1.5,y,3.4),.055,'metal',8)
    S.box('sedum shelter roof',(0,0,3.39),(3.12,14,.15),'sage')
    for y in [i*.6 for i in range(-11,12)]:S.box('roof raised seam',(0,y,3.49),(3.12,.035,.035),'metal')
    for y in (-4,4):
        S.box('platform rear windscreen',(1.37,y,1.62),(.024,3.1,2.0),'glass')
        S.box('windscreen safety stripe',(1.35,y,1.32),(.016,3.1,.05),'cream')
        # Bench native dimensions, manually authored inside the stop module.
        for dx in (.76,.88,1.0):S.box('shelter bench slat',(dx,y,.76),(.095,2.3,.06),'timber')
        for yy in (y-.85,y+.85):S.box('shelter bench leg',(.90,yy,.52),(.42,.05,.44),'metal')
    S.box('ticket and route display',(1.22,8,1.4),(.24,.72,2.2),'sage')
    S.box('route display glass',(1.083,8,1.75),(.016,.58,.84),'cream')
    for z in (1.45,1.6,1.75,1.9):S.box('route map line',(1.07,8,z),(.01,.44,.018),'metal')
    S.beam('tram stop flag mast',(1.05,-8,.30),(1.05,-8,3.7),.045,'metal',10)
    S.box('tram stop flag',(1.05,-8,3.32),(.08,.72,.6),'sage')
    S.box('tram icon',(1,-8,3.34),(.012,.42,.23),'cream')

def build(kind,r):
    w,l=r['dimensions_m'];regions=[(x,0,width,l,mat) for _,x,width,mat in SPECS[kind]['sections']]
    S.ground(w,l,regions);details=[]
    def detail(x,y,width,depth,z,height,mat):
        details.append(dict(x=x,y=y,width=width,depth=depth,z=z,height=height,material=mat))
        S.box('native route detail',(x,y,z),(width,depth,max(.004,height)),mat)
    if kind=='tram':
        for track in (-2,2):
            for x in (track-.7175,track+.7175):detail(x,0,.065,l,.025,.05,'metal')
            detail(track,0,.015,l,6.15,.015,'metal')
        for x in (-3.6,3.6):detail(x,0,.16,l,.06,.12,'warm_concrete')
        for y in (-18,6):S.kit('showcase_catenary',7.2,y)
        for side in (-1,1):
            for y in (-18,-6,6,18):S.kit('grove_tree',side*9.3,y)
            for y in (-12,12):S.kit('heritage_lantern',side*9.3,y)
        # Preview includes a chosen stop at its middle. Runtime has none until selected.
        for side in (-1,1):S.kit('showcase_tram_stop',side*5.2,0,0,0 if side>0 else math.pi)
    elif kind=='promenade':
        def brick_paving(x,y,width,depth):
            S.box('brick mortar bed',(x,y,-.06),(width,depth,.12),'paving')
            groups={i:([],[]) for i in range(4)};tw,td=.4,.2
            a,b=x-width/2,x+width/2;c,e=y-depth/2,y+depth/2
            for j in range(math.floor(c/td),math.ceil(e/td)):
                yy0=max(c,j*td+.004);yy1=min(e,(j+1)*td-.004);offset=j%2*tw/2
                if yy1<=yy0:continue
                for i in range(math.floor((a-offset)/tw),math.ceil((b-offset)/tw)):
                    xx0=max(a,i*tw+offset+.004);xx1=min(b,(i+1)*tw+offset-.004)
                    if xx1<=xx0:continue
                    v,f=groups[(i*13+j*7)%4];n=len(v);v.extend([(xx0,yy0,.003),(xx1,yy0,.003),(xx1,yy1,.003),(xx0,yy1,.003)]);f.append((n,n+1,n+2,n+3))
            for i,(v,f) in groups.items():
                if f:S.mesh('terracotta promenade pavers',v,f,'paving.tile'+str(i))
        for i,factor in enumerate((.84,.96,1.06,1.12)):F.material('paving.tile'+str(i),tuple(c*factor for c in (.38,.21,.13)))
        S.paving=brick_paving
        S.bed(-5.25,0,2.25,35.0,trees=True,surface=False)
        for y in (-12,0,12):
            S.kit('showcase_ivy_pergola',.1,y)
            S.kit('bench',3.75,y,0,math.pi/2)
            S.kit('grove_tree',-5.1,y)
            S.kit('heritage_lantern',5.45,y+3)
            F.place(r,'planted_trellis',-3.7,y+4,math.pi/2)
        for y in [-16.5+3*i for i in range(12)]:S.kit('showcase_iron_guard',6.25,y)
        detail(6.24,0,.45,l,.08,.16,'warm_concrete')
        # Full-width paved end entries and long, unobstructed water-side walk.
    else:
        for side in (-1,1):
            for y in (-18,-6,6,18):S.kit('grove_tree',side*8.5,y,0,y*.04,1.15)
            for y in (-12,12):
                S.kit('heritage_lantern',side*7.2,y)
                S.kit('bench',side*10.7,y,0,side*math.pi/2)
            S.kit('showcase_morris_column',side*13.2,0)
            S.kit('promenade_kiosk',side*13.0,17,0,side*math.pi/2)
            for y in (-21,-9,3,15):S.kit('street_bollard',side*6.55,y)
            detail(side*6.0,0,.22,l,.08,.16,'warm_concrete')
        for y in range(-22,24,6):detail(0,y,.1,3,.008,0,'paint')
    r['program']=dict(schemaVersion=1,adapter='showcase-tram-v1' if kind=='tram' else 'showcase-street-v1',surfaceRegions=[],details=details,
      paving='brick' if kind=='promenade' else 'stone',pavingModuleM=[.4,.2] if kind=='promenade' else [1.2,.8],minLengthM=48 if kind!='promenade' else 36,maxLengthM=480,preparedLevelOnly=True,baseLiftM=.025,
      palette={name:list(m.diffuse_color)[:3] for name,m in S.MATS.items() if name!='kit'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True)
    p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);spec=SPECS[a.kind];w,l=spec['width'],spec['length']
    refs=[a.reference_root/spec['slug']/f"variant_{spec['index']}{suffix}" for suffix in ('.png','_angle_60.jpg','_angle_90.jpg')]
    for f in refs:assert f.is_file(),f
    if a.dry_run:print('DRY_RUN_PASS',spec['id']);return
    if a.output.exists():raise ValueError('Choose a new version; preserve prior evidence.')
    a.output.mkdir(parents=True);S.init(a.kit);F.init()
    for n,b in [('showcase_ivy_pergola',ivy_pergola),('showcase_iron_guard',iron_guard),('showcase_morris_column',morris_column),('showcase_catenary',catenary),('showcase_tram_stop',tram_stop)]:extra_module(n,b)
    r=dict(id=spec['id'],title=spec['title'],dimensions_m=[w,l],fixed_width_m=w,fixture_length_m=l,pattern='stone',runtime_approved=False,
      reference=spec['slug']+'/reference.png',sections=[dict(name=n,x=x,width=width,material=mat) for n,x,width,mat in spec['sections']],
      clear_routes=[],image_references=[],source_notes=['Exact catalogue references; background buildings excluded. Metre-scale rigid furnishings and route bands.',
      'Tram stop preview is illustrative; the saved user route starts with zero stops, added only by explicit selection.' if a.kind=='tram' else 'No whole preview stretching.'],
      kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest())
    for i,f in enumerate(refs):
        target=a.output/('reference.png' if i==0 else f.name);shutil.copy2(f,target)
        r['image_references'].append(dict(path=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
    build(a.kind,r)
    S.bpy.context.scene.cycles.denoising_use_gpu=False
    for f in (Path(__file__),Path(S.__file__),Path(F.__file__)):shutil.copy2(f,a.output/f.name)
    S.deliver(a.output,r,[('aerial',(w*1.5,-l*.95,l*.8),(0,0,1),l*1.4),('top',(0,0,100),(0,.001,0),l*1.4),('detail',(w*.5,-l*.3,9),(0,0,1),w*1.2)])
    r['program']['surfaceRegions']=r['surface_regions']
    (a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
    cam=S.bpy.context.scene.camera;cam.data.type='PERSP';cam.data.lens=26;cam.location=(w*.12,-l/2-7,1.65)
    cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat('-Z','Y').to_euler()
    S.bpy.context.scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)

if __name__=='__main__':main()
