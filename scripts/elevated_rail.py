"""Register or hydrate the single reviewed elevated rail delivery, locally."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.public_realm_assets.stage_street_pilots import inspect_pilot, stage_inspected

ID='student_elevated_garden_rail_v1'
PARENT='elevated_garden_rail'
SEED=ROOT/'seed/classroom-streets/elevated-rail-v001'
HERO='/archetypes/streets/elevated-garden-rail/variant_0.png'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(data):return hashlib.sha256(data).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def immutable(p,data):
    if p.exists() and p.read_bytes()!=data:raise ValueError('Changed immutable delivery: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

def inspect(package,seed=False):
    recipe=read(package/('source-recipe.json' if seed else 'recipe.json'))
    if seed:
        row=read(package/'manifest.json');files={}
        if sha((package/'source-recipe.json').read_bytes())!=row['sourceRecipeSha256']:raise ValueError('Source recipe changed')
        for kind,lock in row['modules'].items():
            data=(package/(kind+'.glb')).read_bytes()
            if sha(data)!=lock['sha256'] or len(data)!=lock['bytes'] or lock['sha256']!=recipe['modules'][kind]['sha256']:raise ValueError('Native module changed')
            files[kind+'.glb']=data
        files['reference.png']=(package/'reference.png').read_bytes()
        if sha(files['reference.png'])!=row['referenceSha256']:raise ValueError('Hero changed')
    else:
        row,files=inspect_pilot(package)
        row['program']=recipe['program'];row['programSha256']=sha(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())
        row['thumbnailUrl']=HERO
    if row['id']!=ID or row['sourceArchetypeId']!=PARENT:raise ValueError('Outside the one-street batch')
    if row['program']!=recipe['program'] or sha(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())!=row['programSha256']:raise ValueError('Program changed')
    if row['program']['surfaceRegions']!=recipe['surface_regions']:raise ValueError('Ground ownership changed')
    if sha((package/recipe['assembly']['path']).read_bytes())!=row['sourceAssemblySha256']:raise ValueError('Assembly changed')
    review=read(package/'visual-review.json')
    if review['status']!='PASS_OFFLINE_NATIVE_REVIEW' or review['model_sha256']!=row['sourceAssemblySha256']:raise ValueError('Exact assembly needs visual review')
    for name,digest in recipe['source_files'].items():
        if sha((package/name).read_bytes())!=digest:raise ValueError('Build source changed: '+name)
    for name,data in files.items():
        if not name.endswith('.glb'):continue
        if data[:4]!=b'glTF':raise ValueError('Unhydrated GLB')
        doc=json.loads(data[20:20+int.from_bytes(data[12:16],'little')])
        if any('uri' in x for key in ('buffers','images') for x in doc.get(key,[])):raise ValueError('External module dependency')
    return row,files,recipe

def run(package,public_root,seed=False,dry_run=False):
    row,files,recipe=inspect(package,seed)
    front=ROOT/'frontend/src/data';back=ROOT/'backend/app/data'
    stage_inspected([(row,files)],public_root,front/'nativeStreetPilots.json',dry_run=True)
    if dry_run:print('DRY_RUN_PASS',ID);return
    if not seed:
        # Capture old saved-recipe compatibility before adding this capability.
        sys.path.insert(0,str(ROOT/'backend'))
        from app.services.public_realm_lego import build_public_realm_capability_catalog,public_realm_capability_fingerprint
        catalog=build_public_realm_capability_catalog();history=read(back/'publicRealmCatalogHistory.json')
        history['catalogs'][catalog.fingerprint]={f'{c.family_id}@{c.family_version}':public_realm_capability_fingerprint(c) for c in catalog.capabilities}
        all_files={**files,'source-recipe.json':(package/'recipe.json').read_bytes(),
                   'visual-review.json':(package/'visual-review.json').read_bytes(),
                   recipe['assembly']['path']:(package/recipe['assembly']['path']).read_bytes(),
                   **{name:(package/name).read_bytes() for name in recipe['source_files']}}
        for name,data in all_files.items():immutable(SEED/name,data)
        write(SEED/'manifest.json',row)
        identities=read(back/'validation_public_realm_variants.json')
        identities['street'][PARENT]=[ID];write(back/'validation_public_realm_variants.json',identities)
        write(back/'publicRealmCatalogHistory.json',history)
    stage_inspected([(row,files)],public_root,front/'nativeStreetPilots.json',dry_run=False)
    immutable(public_root/HERO.lstrip('/'),files['reference.png'])
    if seed:print('HYDRATED',ID);return
    write(back/'nativeStreetPilots.json',read(front/'nativeStreetPilots.json'))
    import trimesh
    bounds=read(front/'nativeStreetModuleBounds.json')
    for kind,lock in row['modules'].items():
        lo,hi=trimesh.load(package/'modules'/f'{kind}.glb',force='scene',process=False).bounds
        bounds[lock['sha256']]=dict(plan=[[float(lo[0]),float(-hi[2])],[float(hi[0]),float(-lo[2])]],height=[float(lo[1]),float(hi[1])])
    write(front/'nativeStreetModuleBounds.json',bounds)
    for folder in (front,back):
        roster=read(folder/'classroomStarter.json')
        if not any(e.get('variantId')==ID for e in roster['entries']):roster['entries'].append(dict(domain='street',representation='native-modules',archetypeId=PARENT,variantId=ID,revision=row['sourceRecipeSha256'],status='local-pilot-runtime-pending'))
        write(folder/'classroomStarter.json',roster)
    cards=read(front/'classroomExpansion.json')
    if not any(e['variant_id']==ID for e in cards['entries']):
        cards['entries'].append(dict(domain='street',title=row['title'],archetype_id=PARENT,variant_id=ID,version=ID,placement_id=ID,sha256=row['sourceAssemblySha256'],asset_review='PASS_OFFLINE_NATIVE_REVIEW',runtime_status='NOT TESTED',completed=False))
        cards['assets'].append(dict(id=ID,kind='street',definitionVersion=1,readiness='pilot',label=row['title'],description='Twin-track concrete viaduct with a detailed static metro train, gardens, a cycle path and broad walking routes below. Straight 48–288 m corridor on a prepared level site.',thumbnail=HERO,model=dict(variantId=ID,revision=row['sourceRecipeSha256'],method='native_street_modules_v1'),calgaryGuide=dict(groupId='transit',basis='form_reference'),reshapeMode='fixed_section_route',sectionWidth=26,properties=dict(road_archetype_id=PARENT,road_selected_variant_id=ID,width=26,lane_count=0,pick_place_street_section=ID,pick_place_automatic_3d=True,pick_place_definition_version=1,community_3d_mask_existing_tiles=True,road_standard_citation='City Prompt original elevated rail teaching concept')))
    write(front/'classroomExpansion.json',cards)
    print('STAGED',ID,'local pilot; runtime acceptance pending')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path);p.add_argument('--from-seed',action='store_true');p.add_argument('--public-root',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if bool(a.package)==a.from_seed:p.error('Choose --package or --from-seed')
    run(SEED if a.from_seed else a.package,a.public_root,a.from_seed,a.dry_run)
