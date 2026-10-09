"""Finite five-street authoring. Imports the shared engine; writes external packages only."""
import argparse, hashlib, json, math, shutil, sys
from pathlib import Path
REPO=Path('C:/Users/andre/.codex/worktrees/ubst-rlasm-building-pilot/CityPrompt')
sys.path.insert(0,str(REPO/'tools/public_realm_assets'))
import scene as S
import street_furniture as F
from build_streets import arrow,bicycle
from mathutils import Vector

SPECS={
 'rain':('Rain-Garden Residential Street','rain_garden_residential_street',[('west_walk',2.5,'paving'),('west_garden',2.25,'soil'),('road',5.5,'asphalt'),('east_garden',2.25,'soil'),('east_walk',2.5,'paving')],2),
 'shopping':('Compact One-Way Shopping Street','compact_one_way_shopping_street',[('west_walk',2.5,'paving'),('cafe_bay',3,'paving'),('parking',2.25,'asphalt'),('road',3.25,'asphalt'),('east_furniture',2,'paving'),('east_walk',2.5,'paving')],1),
 'cycle':('Neighbourhood Cycle Street','neighbourhood_cycle_street',[('west_walk',2.5,'paving'),('west_garden',1.5,'soil'),('shared_cycle_road',5,'cycle'),('east_garden',1.5,'soil'),('east_walk',2.5,'paving')],2),
 'greenway':('Separated Walking & Cycling Greenway','separated_walking_cycling_greenway',[('west_garden',2,'soil'),('pedestrian_walk',3,'paving'),('separator',1.5,'soil'),('cycle',3.5,'cycle')],0),
 'transit':('Neighbourhood Transit-Stop Street','neighbourhood_transit_stop_street',[('west_walk',2.5,'paving'),('west_garden',2,'soil'),('road',6,'asphalt'),('waiting_bay',4,'paving'),('east_walk',2.5,'paving')],2),
}

def create_recipe(kind):
 title,slug,bands,lanes=SPECS[kind];w=sum(v[1] for v in bands);cursor=-w/2;sections=[]
 for name,width,mat in bands:
  sections.append(dict(name=name,x=cursor+width/2,width=width,material=mat));cursor+=width
 return dict(id='student_'+slug+'_v1',title=title,kind=kind,reference=slug+'/reference.png',dimensions_m=[w,40],fixed_width_m=w,fixture_length_m=40,pattern='stone',sections=sections,motor_lanes=lanes,runtime_approved=False,clear_routes=[],image_references=[],source_notes=['Original reference-informed teaching concept, not an official city section or drainage/traffic certification.','Native dimensions and amenity modules; prepared level support only. Shared engine owns route bends, junctions, terrain and capture.','No neighbouring buildings, cars or context are included; photographs are AI-generated design inspiration.'])

def build(r):
 w,l=r['dimensions_m'];kind=r['kind'];bands={s['name']:s for s in r['sections']};regions=[(s['x'],0,s['width'],l,s['material']) for s in r['sections']];details=[];meshes=[]
 def x(n):return bands[n]['x']
 def place(n,b,y,yaw=0,dx=0,scale=1):S.kit(n,x(b)+dx,y,0,yaw,scale)
 def detail(xx,y,ww,dd,mat='paint',z=.012):
  details.append(dict(x=xx,y=y,width=ww,depth=dd,z=z,height=0,material=mat));S.box('native detail',(xx,y,z),(ww,dd,.003),mat)
 def marks(builder,*args):
  before=set(S.bpy.context.scene.objects);builder(*args)
  for obj in set(S.bpy.context.scene.objects)-before:
   obj.data.calc_loop_triangles();meshes.append(dict(positions=[v for p in obj.data.vertices for v in p.co],indices=[v for t in obj.data.loop_triangles for v in t.vertices],material=obj.data.materials[0].name))
 def garden(b,tree=True):
  bw=bands[b]['width']
  for yy in (-14,-5,5,14):
   if tree:place('grove_tree',b,yy,scale=.78)
  for j in range(55):
   yy=-18.9+j*.70
   if abs(yy)<1.8:continue
   if kind=='greenway' and b=='west_garden' and min(abs(yy-10),abs(yy+10))<1.8:continue
   for i,dx in enumerate((-bw*.28,0,bw*.28)):
    # Three interleaved drifts retain the clear central pedestrian break.
    if any(abs(yy-ty)<.65 and abs(dx)<.3 for ty in (-14,-5,5,14)):continue
    plant=('meadow_grass','flowering_perennial','silver_shrub')[(j//4+i)%3]
    place(plant,b,yy+.12*(i%2),yaw=j*.61,dx=dx,scale=.72 if plant!='silver_shrub' else .62)
  regions.append((x(b),0,bw,2.4,'paving'))
 def walk(n,width=None):r['clear_routes'].append(dict(name=n,a=[x(n),-20],b=[x(n),20],width=width or bands[n]['width']-.2))
 for s in r['sections']:
  if 'walk' in s['name'] or s['name'] in ('road','shared_cycle_road','cycle'):walk(s['name'])
 if kind=='rain':
  for b in ('west_garden','east_garden'):garden(b)
  for b in ('west_garden','east_garden'):
   for yy in (-10,10):place('light',b,yy,scale=.85)
  for side in (-1,1):
   for yy in (-16,-7,7,16):detail(side*2.69,yy,.08,1.2,'metal')
 elif kind=='shopping':
  for yy in (-12,12):place('cafe_table_chairs','cafe_bay',yy)
  for yy in (-5,5):place('grove_tree','cafe_bay',yy,scale=.72)
  for yy in (-14,0,14):place('grove_tree','east_furniture',yy,scale=.72)
  for yy in (-7,7):place('heritage_lantern','east_furniture',yy)
  place('bike_rack','cafe_bay',17,math.pi/2)
  for yy in (-18,-12,-6,6,12,18):detail(x('parking'),yy,2,.07)
  for yy in (-12,12):marks(arrow,x('road'),yy,1)
 elif kind=='cycle':
  for b in ('west_garden','east_garden'):garden(b)
  for yy in (-13,13):
   for dx,sign in ((-1.25,-1),(1.25,1)):marks(bicycle,x('shared_cycle_road')+dx,yy,sign);marks(arrow,x('shared_cycle_road')+dx,yy+sign*2,sign)
  for b in ('west_garden','east_garden'):place('light',b,0,scale=.85)
 elif kind=='greenway':
  garden('west_garden');garden('separator',False)
  for yy in (-10,10):
   regions.append((x('west_garden'),yy,2,2.8,'paving'));place('bench','west_garden',yy,math.pi/2,scale=.85)
  for yy in (-15,15):
   for dx,sign in ((-.875,-1),(.875,1)):marks(bicycle,x('cycle')+dx,yy,sign);marks(arrow,x('cycle')+dx,yy+sign*2,sign)
  for yy in range(-18,19,4):detail(x('cycle'),yy,.06,1.8)
 elif kind=='transit':
  garden('west_garden')
  place('transit_shelter','waiting_bay',-7,-math.pi/2,dx=.65)
  place('transit_stop_pole','waiting_bay',-11,dx=-1.5)
  place('bin','waiting_bay',-3,dx=1.2)
  for yy in (7,15):place('grove_tree','waiting_bay',yy,scale=.78)
  place('bench','waiting_bay',2,-math.pi/2,dx=.6)
  r['clear_routes'].append(dict(name='boarding_strip',a=[x('waiting_bay')-1.35,-10],b=[x('waiting_bay')-1.35,0],width=1.2))
  for yy in range(-18,19,4):detail(x('road'),yy,.09,1.8)
  for yy in (-9,-7,-5):detail(x('waiting_bay')-1.8,yy,.15,1.6,'edge')
 S.ground(w,l,regions)
 r['program']=dict(schemaVersion=1,adapter='showcase-street-v1',surfaceRegions=[],details=details,meshDetails=meshes,paving='stone',pavingModuleM=[1.2,.8],minLengthM=40,maxLengthM=300,preparedLevelOnly=True,baseLiftM=.025,palette={n:list(m.diffuse_color)[:3] for n,m in S.MATS.items() if n!='kit'})

def main():
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=create_recipe(a.kind);source=a.reference_root/(a.kind+'.png')
 assert source.is_file() and a.kit.is_file();assert not a.output.exists()
 if a.dry_run:print('DRY_RUN_PASS',r['id'],r['dimensions_m']);return
 a.output.mkdir(parents=True);shutil.copy2(source,a.output/'reference.png');r['image_references']=[dict(path='reference.png',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size,source=str(source),provenance='Original built-in image_gen design inspiration, 2026-10-09')];r['kit_sha256']=hashlib.sha256(a.kit.read_bytes()).hexdigest()
 S.init(a.kit);F.init();S.PLACEMENTS.clear();build(r)
 for f in (Path(__file__),Path(S.__file__),Path(F.__file__)):shutil.copy2(f,a.output/f.name)
 try:
  cp=S.bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
  for device in cp.devices:device.use=device.type!='CPU'
  S.bpy.context.scene.cycles.device='GPU'
 except Exception:pass
 w,l=r['dimensions_m'];S.deliver(a.output,r,[('aerial',(w*1.6,-l*.9,32),(0,0,1),l*1.32),('top',(0,0,90),(0,.001,0),l*1.15)])
 r['program']['surfaceRegions']=r['surface_regions'];(a.output/'recipe.json').write_text(json.dumps(r,indent=2)+'\n')
 cam=S.bpy.context.scene.camera;cam.data.type='PERSP';cam.data.lens=25;cam.location=(-w/2+1.25,-l/2-2,1.65);cam.rotation_euler=(Vector((-w/2+1.25,12,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();S.bpy.context.scene.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
