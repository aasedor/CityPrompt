"""Inspect and stage two exact, station-capable elevated rail variants locally."""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.public_realm_assets.stage_street_pilots import inspect_pilot, stage_inspected

SPECS={
 'skytrain_elevated_corridor_v0':('skytrain_elevated_corridor','skytrain-elevated-station-native','skytrain-modern-station-v001'),
 'elevated_rail_transit_corridor_v0':('elevated_rail_transit_corridor','elevated-rail-transit-station-native','civic-flow-station-v001'),
}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(data):return hashlib.sha256(data).hexdigest()
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def immutable(p,data):
    if p.exists() and p.read_bytes()!=data:raise ValueError('Changed immutable deliverable: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

def inspect(package,expected,seed=False):
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
        row['program']=recipe['program']
        row['programSha256']=sha(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())
        row['thumbnailUrl']='/archetypes/streets/'+SPECS[expected][1]+'/variant_0.png'
    parent,slug,_=SPECS[expected]
    if row['id']!=expected or row['sourceArchetypeId']!=parent:raise ValueError('Outside the two-variant station batch')
    if row['program']!=recipe['program'] or sha(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())!=row['programSha256']:raise ValueError('Program changed')
    if row['program']['adapter']!='elevated-station-v1' or row['program']['surfaceRegions']!=recipe['surface_regions']:raise ValueError('Station program changed')
    assembly=package/recipe['assembly']['path']
    if sha(assembly.read_bytes())!=row['sourceAssemblySha256']:raise ValueError('Assembly changed')
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

def run(packages,public_root,seed=False,dry_run=False):
    front=ROOT/'frontend/src/data';back=ROOT/'backend/app/data'
    reviewed=[]
    for identity in SPECS:
        package=ROOT/'seed/classroom-streets'/SPECS[identity][2] if seed else packages[identity]
        reviewed.append((identity,package,*inspect(package,identity,seed)))
    stage_inspected([(row,files) for _,_,row,files,_ in reviewed],public_root,front/'nativeStreetPilots.json',dry_run=True)
    if dry_run:print('DRY_RUN_PASS',','.join(SPECS));return
    if not seed:
        sys.path.insert(0,str(ROOT/'backend'))
        from app.services.public_realm_lego import build_public_realm_capability_catalog,public_realm_capability_fingerprint
        catalog=build_public_realm_capability_catalog();history=read(back/'publicRealmCatalogHistory.json')
        history['catalogs'][catalog.fingerprint]={f'{c.family_id}@{c.family_version}':public_realm_capability_fingerprint(c) for c in catalog.capabilities}
        write(back/'publicRealmCatalogHistory.json',history)
        identities=read(back/'validation_public_realm_variants.json')
        for identity,package,row,files,recipe in reviewed:
            seed_root=ROOT/'seed/classroom-streets'/SPECS[identity][2]
            all_files={**files,'source-recipe.json':(package/'recipe.json').read_bytes(),
                'visual-review.json':(package/'visual-review.json').read_bytes(),
                recipe['assembly']['path']:(package/recipe['assembly']['path']).read_bytes(),
                **{name:(package/name).read_bytes() for name in recipe['source_files']}}
            for name,data in all_files.items():immutable(seed_root/name,data)
            write(seed_root/'manifest.json',row)
            identities['street'][SPECS[identity][0]]=[identity]
        write(back/'validation_public_realm_variants.json',identities)
    stage_inspected([(row,files) for _,_,row,files,_ in reviewed],public_root,front/'nativeStreetPilots.json',dry_run=False)
    for identity,_,row,files,_ in reviewed:
        immutable(public_root/'archetypes/streets'/SPECS[identity][1]/'variant_0.png',files['reference.png'])
    if seed:print('HYDRATED',','.join(SPECS));return
    (back/'nativeStreetPilots.json').write_text(
        json.dumps(read(front/'nativeStreetPilots.json'),indent=2)+'\n',encoding='utf-8')
    import trimesh
    bounds=read(front/'nativeStreetModuleBounds.json')
    for _,package,row,_,_ in reviewed:
        for kind,lock in row['modules'].items():
            lo,hi=trimesh.load(package/'modules'/f'{kind}.glb',force='scene',process=False).bounds
            bounds[lock['sha256']]=dict(plan=[[float(lo[0]),float(-hi[2])],[float(hi[0]),float(-lo[2])]],height=[float(lo[1]),float(hi[1])])
    write(front/'nativeStreetModuleBounds.json',bounds)
    for folder in (front,back):
        roster=read(folder/'classroomStarter.json')
        for identity,_,row,_,_ in reviewed:
            if not any(e.get('variantId')==identity for e in roster['entries']):
                roster['entries'].append(dict(domain='street',representation='native-modules',
                    archetypeId=SPECS[identity][0],variantId=identity,revision=row['sourceRecipeSha256'],status='local-pilot-runtime-pending'))
        write(folder/'classroomStarter.json',roster)
    cards=read(front/'classroomExpansion.json')
    for identity,_,row,_,_ in reviewed:
        if any(e['variant_id']==identity for e in cards['entries']):continue
        parent,slug,_=SPECS[identity]
        hero='/archetypes/streets/'+slug+'/variant_0.png'
        cards['entries'].append(dict(domain='street',title=row['title'],archetype_id=parent,variant_id=identity,
            version=identity,placement_id=identity,sha256=row['sourceAssemblySha256'],
            asset_review='PASS_OFFLINE_NATIVE_REVIEW',runtime_status='NOT TESTED',completed=False))
        cards['assets'].append(dict(id=identity,kind='street',definitionVersion=1,readiness='pilot',
            label=row['title'],description='Elevated twin-track corridor with a movable full station, two platforms, stair access and a static train. Straight 48–288 m on a prepared level site.',
            thumbnail=hero,model=dict(variantId=identity,revision=row['sourceRecipeSha256'],method='native_street_modules_v1'),
            calgaryGuide=dict(groupId='transit',basis='form_reference'),reshapeMode='fixed_section_route',sectionWidth=26,
            properties=dict(road_archetype_id=parent,road_selected_variant_id=identity,width=26,lane_count=0,
                pick_place_street_section=identity,pick_place_automatic_3d=True,pick_place_definition_version=1,
                community_3d_mask_existing_tiles=True,road_standard_citation='City Prompt original elevated rail station concept')))
    write(front/'classroomExpansion.json',cards)
    print('STAGED',','.join(SPECS),'local station pilots; runtime acceptance pending')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--skytrain',type=Path);p.add_argument('--civic',type=Path)
    p.add_argument('--from-seed',action='store_true');p.add_argument('--public-root',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if not a.from_seed and (not a.skytrain or not a.civic):p.error('Both exact pilot packages are required')
    run({'skytrain_elevated_corridor_v0':a.skytrain,'elevated_rail_transit_corridor_v0':a.civic},a.public_root,a.from_seed,a.dry_run)
