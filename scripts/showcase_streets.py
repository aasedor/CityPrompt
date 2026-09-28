"""Additive, hash-verified packaging of the three showcase street pilots."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.public_realm_assets.stage_street_pilots import inspect_pilot,stage_inspected

IDS={'student_grass_tram_avenue_v1','student_vine_pergola_promenade_v1','student_grand_haussmann_boulevard_v1'}
def digest(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def inspect(package):
    row,files=inspect_pilot(package);recipe=read(package/'recipe.json')
    if row['id'] not in IDS:raise ValueError('Outside the finite showcase street batch')
    review=read(package/'visual-review.json')
    if review['model_sha256']!=row['sourceAssemblySha256'] or review['status']!='PASS_OFFLINE_NATIVE_REVIEW':raise ValueError('Exact source assembly needs visual review')
    row['program']=recipe['program']
    if row['id']=='student_vine_pergola_promenade_v1':
        # scene.bed() authors these four rigid edging strips outside the
        # generator's detail recorder. Preserve them in the executable program.
        row['program']['details'] += [dict(x=x,y=y,width=w,depth=d,z=.025,height=.05,material='metal')
            for x,y,w,d in ((-6.375,0,.035,35),(-4.125,0,.035,35),(-5.25,-17.5,2.25,.035),(-5.25,17.5,2.25,.035))]
        row['junctionSurface']='brick'
    row['programSha256']=digest(json.dumps(row['program'],sort_keys=True,separators=(',',':')).encode())
    if row['program']['surfaceRegions']!=recipe['surface_regions']:raise ValueError('Ground ownership drift')
    import trimesh
    bounds={}
    for kind,lock in row['modules'].items():
        scene=trimesh.load(package/'modules'/f'{kind}.glb',force='scene',process=False)
        lo,hi=scene.bounds
        bounds[lock['sha256']]=dict(plan=[[float(lo[0]),float(-hi[2])],[float(hi[0]),float(-lo[2])]],height=[float(lo[1]),float(hi[1])])
    return row,files,bounds

def install(packages,public_root):
    inspected=[inspect(p) for p in packages]
    if len({r['id'] for r,_,_ in inspected})!=len(inspected):raise ValueError('Duplicate package')
    front=ROOT/'frontend/src/data';back=ROOT/'backend/app/data'
    # Preserve the old executable fingerprint before adding capabilities.
    sys.path.insert(0,str(ROOT/'backend'))
    from app.services.public_realm_lego import build_public_realm_capability_catalog,public_realm_capability_fingerprint
    catalog=build_public_realm_capability_catalog();history=read(back/'publicRealmCatalogHistory.json')
    history['catalogs'][catalog.fingerprint]={f'{c.family_id}@{c.family_version}':public_realm_capability_fingerprint(c) for c in catalog.capabilities}
    payload=[(r,f) for r,f,_ in inspected]
    stage_inspected(payload,public_root,front/'nativeStreetPilots.json',dry_run=True)
    # All asset writes are immutable; a rerun cannot silently replace a binding.
    for package,(row,files,_) in zip(packages,inspected):
        seed=ROOT/'seed/classroom-streets/showcase'/row['id']
        for name,data in {**files,'source-recipe.json':(package/'recipe.json').read_bytes(),'visual-review.json':(package/'visual-review.json').read_bytes()}.items():
            target=seed/name
            if target.exists() and target.read_bytes()!=data:raise ValueError('Changed packaged bytes: '+str(target))
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    stage_inspected(payload,public_root,front/'nativeStreetPilots.json',dry_run=False)
    write(back/'nativeStreetPilots.json',read(front/'nativeStreetPilots.json'));write(back/'publicRealmCatalogHistory.json',history)
    bounds=read(front/'nativeStreetModuleBounds.json')
    for _,_,b in inspected:bounds.update(b)
    write(front/'nativeStreetModuleBounds.json',bounds)
    roster=read(front/'classroomStarter.json');cards=read(front/'classroomExpansion.json')
    for row,_,_ in inspected:
        if not any(e.get('variantId')==row['id'] for e in roster['entries']):roster['entries'].append(dict(domain='street',representation='native-modules',archetypeId=row['sourceArchetypeId'],variantId=row['id'],revision=row['sourceRecipeSha256'],status='local-pilot-runtime-pending'))
        if any(e['variant_id']==row['id'] for e in cards['entries']):continue
        group='transit' if 'tram' in row['id'] else 'active' if 'promenade' in row['id'] else 'arterial'
        cards['entries'].append(dict(domain='street',title=row['title'],archetype_id=row['sourceArchetypeId'],variant_id=row['id'],version=row['id'],placement_id=row['id'],sha256=row['sourceAssemblySha256'],asset_review='PASS_OFFLINE_NATIVE_REVIEW',runtime_status='NOT TESTED',completed=False))
        cards['assets'].append(dict(id=row['id'],kind='street',definitionVersion=1,readiness='pilot',label=row['title'],description=f"{row['widthM']} m native section with complete furnishings and drawn-route extension.",thumbnail=row['thumbnailUrl'],model=dict(variantId=row['id'],revision=row['sourceRecipeSha256'],method='native_street_modules_v1'),calgaryGuide=dict(groupId=group,basis='form_reference'),reshapeMode='fixed_section_route',sectionWidth=row['widthM'],properties=dict(road_archetype_id=row['sourceArchetypeId'],road_selected_variant_id=row['id'],width=row['widthM'],pick_place_street_section=row['id'],pick_place_automatic_3d=True,pick_place_definition_version=1,community_3d_mask_existing_tiles=True,road_standard_citation='City Prompt reference-informed teaching concept')))
    write(front/'classroomStarter.json',roster)
    backend_roster=read(back/'classroomStarter.json')
    for entry in roster['entries']:
        if entry.get('variantId') in IDS and not any(e.get('variantId')==entry['variantId'] for e in backend_roster['entries']):
            backend_roster['entries'].append(entry)
    write(back/'classroomStarter.json',backend_roster)
    write(front/'classroomExpansion.json',cards)
    write(ROOT/'seed/classroom-streets/showcase/manifest.json',[r for r,_,_ in inspected])
    print('STAGED',len(inspected),'local pilots; browser acceptance NOT TESTED')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,action='append',required=True);p.add_argument('--public-root',type=Path,required=True)
    a=p.parse_args();install(a.package,a.public_root)
