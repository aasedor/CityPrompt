"""Additive five-street installer; dry-run by default. Exact review required."""
import argparse,hashlib,json,math,shutil,sys
from pathlib import Path

PARENTS={'rain_garden_residential_street':'narrow_residential_street','compact_one_way_shopping_street':'neighborhood_main_street','neighbourhood_cycle_street':'neighborhood_greenway','separated_walking_cycling_greenway':'multi_use_trail','neighbourhood_transit_stop_street':'floating_bus_stop_transit_street'}
LANES=dict(zip(PARENTS,[2,1,2,0,2]))
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def raw(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
def public_target(root,url):
 if not isinstance(url,str) or not url.startswith('/') or '\\' in url or '..' in Path(url).parts:raise ValueError('Unsafe public asset URL')
 target=(root/url.lstrip('/')).resolve()
 if not target.is_relative_to(root.resolve()):raise ValueError('Public asset leaves staging root')
 return target
def review_gate(review,assembly_hash,recipe_hash):
 if review.get('status')!='PASS_OFFLINE_NATIVE_REVIEW' or review.get('model_sha256')!=assembly_hash:raise ValueError('Exact independent review required')
 if review.get('unresolved_p0')!=0 or review.get('unresolved_p1')!=0:raise ValueError('Independent review has unresolved blockers')
 evidence=review.get('inspected_files')
 if not isinstance(evidence,list) or not evidence:raise ValueError('Independent review needs inspected files')
 locks={e['path']:e['sha256'] for e in evidence}
 if locks.get('recipe.json')!=recipe_hash or locks.get('assembly-preview.glb')!=assembly_hash:raise ValueError('Independent review does not lock exact source recipe and assembly')

def inspect(repo,package):
 sys.path.insert(0,str(repo));from tools.public_realm_assets.stage_street_pilots import inspect_pilot
 row,files=inspect_pilot(package);r=read(package/'recipe.json');key=row['id'].removeprefix('student_').removesuffix('_v1')
 if key not in PARENTS:raise ValueError('Outside the finite five-street batch')
 if type(r.get('motor_lanes')) is not int or r['motor_lanes']!=LANES[key]:raise ValueError('Declared motor lanes differ from exact source recipe')
 review=read(package/'independent-review.json')
 review_gate(review,r['assembly']['sha256'],row['sourceRecipeSha256'])
 for evidence in review.get('inspected_files',[]):
  if sha((package/evidence['path']).read_bytes())!=evidence['sha256']:raise ValueError('Reviewed evidence changed')
 row.update(sourceArchetypeId=PARENTS[key],program=r['program'],programSha256=sha(json.dumps(r['program'],sort_keys=True,separators=(',',':')).encode()),thumbnailUrl=f"/archetypes/streets/neighbourhood-five/{row['id']}.png")
 assert row['program']['surfaceRegions']==r['surface_regions']
 import trimesh
 bounds={};budget=[]
 for kind,lock in row['modules'].items():
  scene=trimesh.load(package/'modules'/f'{kind}.glb',force='scene',process=False);lo,hi=scene.bounds
  bounds[lock['sha256']]=dict(plan=[[float(lo[0]),float(-hi[2])],[float(hi[0]),float(-lo[2])]],height=[float(lo[1]),float(hi[1])])
  count=sum(p['kind']==kind for p in r['placements']);triangles=sum(len(g.faces) for g in scene.geometry.values())
  budget.append(dict(kind=kind,countPer40M=count,moduleTriangles=triangles,moduleBytes=lock['bytes'],submittedTrianglesPer40M=count*triangles))
 return row,files,bounds,budget

def stage_seed(a):
 seed=a.repo/'seed/classroom-streets/neighbourhood-five';rows=read(seed/'manifest.json');updates={}
 allowed={'student_'+key+'_v1' for key in PARENTS}
 if not rows or len(rows)>5 or len({r['id'] for r in rows})!=len(rows) or any(r['id'] not in allowed for r in rows):raise ValueError('Invalid finite seed inventory')
 for row in rows:
  package=seed/row['id'];recipe_bytes=(package/'source-recipe.json').read_bytes();r=json.loads(recipe_bytes)
  if sha(recipe_bytes)!=row['sourceRecipeSha256'] or r['assembly']['sha256']!=row['sourceAssemblySha256']:raise ValueError('Seed recipe changed')
  if sha(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())!=row['programSha256']:raise ValueError('Seed program changed')
  if row['program']!=r['program'] or row['sections']!=r['sections'] or row['widthM']!=r['fixed_width_m']:raise ValueError('Seed executable geometry differs from source')
  expected_poses=[dict(kind=p['kind'],x=p['x'],y=p['y'],z=p.get('z',0),yaw=p.get('yaw',0),scale=p.get('scale',1)) for p in r['placements']]
  expected_wells=[{key:w[key] for key in ('x','y','width','depth','style','tree_kind')} for w in r['tree_wells']]
  if row['placements']!=expected_poses or row['treeWells']!=expected_wells:raise ValueError('Seed placement or tree-well programme differs from reviewed source')
  fixture=row['fixtureLengthM']
  if type(fixture) not in (int,float) or not math.isfinite(fixture) or fixture!=r['fixture_length_m'] or fixture!=r['dimensions_m'][1] or row['routeAxis']!='local_y':raise ValueError('Seed fixture contract differs from reviewed source')
  review=read(package/'independent-review.json')
  review_gate(review,row['sourceAssemblySha256'],row['sourceRecipeSha256'])
  key=row['id'].removeprefix('student_').removesuffix('_v1')
  if type(r.get('motor_lanes')) is not int or r['motor_lanes']!=LANES[key]:raise ValueError('Seed motor lane contract changed')
  for kind,lock in row['modules'].items():
   data=(package/(kind+'.glb')).read_bytes()
   if sha(data)!=lock['sha256'] or len(data)!=lock['bytes'] or lock['sha256']!=r['modules'][kind]['sha256']:raise ValueError('Seed module changed')
   if lock['url']!=f"/street-kits/pilots/{row['id']}/{kind}.glb":raise ValueError('Seed module URL changed')
   updates[public_target(a.public_root,lock['url'])]=data
  photo=(package/'reference.png').read_bytes()
  if sha(photo)!=row['referenceSha256']:raise ValueError('Seed reference changed')
  if row['thumbnailUrl']!=f"/archetypes/streets/neighbourhood-five/{row['id']}.png":raise ValueError('Seed thumbnail URL changed')
  updates[public_target(a.public_root,row['thumbnailUrl'])]=photo
 for path,data in updates.items():
  if path.exists() and path.read_bytes()!=data:raise ValueError('Conflicting public seed bytes')
 if a.install:
  for path,data in updates.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print('SEED_PASS',len(rows),'native module/program bindings', 'staged' if a.install else 'dry run')

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--package',type=Path,action='append');p.add_argument('--from-seed',action='store_true');p.add_argument('--public-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--install',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 if a.from_seed:
  if a.package:p.error('Choose source packages or seed staging')
  stage_seed(a);return
 if not a.package:p.error('--package or --from-seed required')
 inspected=[inspect(a.repo,pkg) for pkg in a.package];ids={r['id'] for r,_,_,_ in inspected}
 if len(ids)!=len(inspected):raise ValueError('Duplicate package')
 front=a.repo/'frontend/src/data';back=a.repo/'backend/app/data';updates={};rows=read(front/'nativeStreetPilots.json');bounds=read(front/'nativeStreetModuleBounds.json');rosters={root:read(root/'classroomStarter.json') for root in (front,back)};cards=read(front/'classroomExpansion.json')
 if rows!=read(back/'nativeStreetPilots.json'):raise ValueError('Existing registry mirrors differ')
 for package,(row,files,module_bounds,budget) in zip(a.package,inspected):
  old=next((x for x in rows if x['id']==row['id']),None)
  if old is not None and old!=row:raise ValueError('Cannot overwrite existing native revision')
  if old is None:rows.append(row)
  for digest,bound in module_bounds.items():
   if digest in bounds and bounds[digest]!=bound:raise ValueError('Existing module bounds differ for immutable bytes')
  bounds.update(module_bounds);key=row['id'].removeprefix('student_').removesuffix('_v1')
  roster=dict(domain='street',representation='native-modules',archetypeId=row['sourceArchetypeId'],variantId=row['id'],revision=row['sourceRecipeSha256'],status='local-pilot-runtime-pending')
  for root,data in rosters.items():
   previous=next((x for x in data['entries'] if x.get('variantId')==row['id']),None)
   if previous is not None and previous!=roster:raise ValueError('Existing roster differs')
   if previous is None:data['entries'].append(roster)
  entry=dict(domain='street',title=row['title'],archetype_id=row['sourceArchetypeId'],variant_id=row['id'],version=row['id'],placement_id=row['id'],sha256=row['sourceAssemblySha256'],asset_review='PASS_OFFLINE_NATIVE_REVIEW',runtime_status='NOT TESTED',completed=False)
  asset=dict(id=row['id'],kind='street',definitionVersion=1,readiness='pilot',label=row['title'],description=f"{row['widthM']} m fixed native section; clear routes, planting and furnishings.",thumbnail=row['thumbnailUrl'],model=dict(variantId=row['id'],revision=row['sourceRecipeSha256'],method='native_street_modules_v1'),calgaryGuide=dict(groupId='transit' if key=='neighbourhood_transit_stop_street' else 'active' if LANES[key]==0 or 'cycle' in key else 'local',basis='form_reference'),reshapeMode='fixed_section_route',sectionWidth=row['widthM'],properties=dict(road_archetype_id=row['sourceArchetypeId'],road_selected_variant_id=row['id'],width=row['widthM'],lane_count=LANES[key],pick_place_street_section=row['id'],pick_place_automatic_3d=True,pick_place_definition_version=1,community_3d_mask_existing_tiles=True,road_standard_citation='City Prompt original teaching concept; not a Calgary standard section'))
  for field,identifier,value in [('entries','variant_id',entry),('assets','id',asset)]:
   previous=[x for x in cards[field] if x.get(identifier)==row['id']]
   if len(previous)>1 or previous and previous[0]!=value:raise ValueError('Existing catalogue card conflicts with exact binding')
   if not previous:cards[field].append(value)
  seed=a.repo/'seed/classroom-streets/neighbourhood-five'/row['id']
  for name,data in {**files,'source-recipe.json':(package/'recipe.json').read_bytes(),'independent-review.json':(package/'independent-review.json').read_bytes(),'build_neighbourhood_streets.py':(package/'build_neighbourhood_streets.py').read_bytes()}.items():
   target=seed/name
   if target.exists() and target.read_bytes()!=data:raise ValueError('Immutable seed bytes changed')
   updates[target]=data
  for name,data in files.items():
   target=a.public_root/'street-kits/pilots'/row['id']/name
   if target.exists() and target.read_bytes()!=data:raise ValueError('Immutable public bytes changed')
   updates[target]=data
  for hero in {public_target(a.repo/'frontend/public',row['thumbnailUrl']),public_target(a.public_root,row['thumbnailUrl'])}:
   if hero.exists() and hero.read_bytes()!=files['reference.png']:raise ValueError('Immutable hero bytes changed')
   updates[hero]=files['reference.png']
  for name in ('independent-geometry-verification.json','geometry-verification.json'):
   if (package/name).exists():updates[seed/name]=(package/name).read_bytes()
  (a.output/(row['id']+'-budget.json')).write_bytes(raw(dict(id=row['id'],assemblyTriangles=read(package/'recipe.json')['triangles'],modules=budget,instanced=True,lod=False,fixtureLengthM=40,maxRouteLengthM=300,estimatedMaxTriangleMultiplier=7.5,note='One pose cycle per40m, never one assembly per sampled vertex; all instances preserved. Runtime desktop responsiveness still untested.')))
 for root in (front,back):updates[root/'nativeStreetPilots.json']=raw(rows);updates[root/'classroomStarter.json']=raw(rosters[root])
 updates[front/'nativeStreetModuleBounds.json']=raw(bounds);updates[front/'classroomExpansion.json']=raw(cards)
 manifest=a.repo/'seed/classroom-streets/neighbourhood-five/manifest.json';old=read(manifest) if manifest.exists() else [];updates[manifest]=raw([r for r in old if r['id'] not in ids]+[r for r,_,_,_ in inspected])
 (a.output/'candidate-manifest.json').write_bytes(raw(rows))
 sys.path.insert(0,str(a.repo/'backend'));from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
 build_native_street_candidate_catalog(a.output/'candidate-manifest.json')
 if not a.install:print('DRY_RUN_PASS',len(inspected),'exact reviewed street packages; no repository writes');return
 from app.services.public_realm_lego import build_public_realm_capability_catalog,public_realm_capability_fingerprint
 catalog=build_public_realm_capability_catalog();history=read(back/'publicRealmCatalogHistory.json');history['catalogs'][catalog.fingerprint]={f'{c.family_id}@{c.family_version}':public_realm_capability_fingerprint(c) for c in catalog.capabilities};updates[back/'publicRealmCatalogHistory.json']=raw(history)
 for path,data in updates.items():
  if path.exists():
   try:relative=path.relative_to(a.repo)
   except ValueError:relative=Path('public-root')/path.relative_to(a.public_root)
   backup=a.output/'backups'/relative
   if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print('INSTALLED',len(inspected),'local pilots; runtime NOT TESTED; no publication')
if __name__=='__main__':main()
