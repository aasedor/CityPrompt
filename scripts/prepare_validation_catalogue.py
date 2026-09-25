"""Finite local validation installation. No geometry generation or approval promotion."""
import hashlib
import json
import shutil
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('C:/dev-artifacts/CityPrompt/approved-validation-2026-09-24')
PUBLIC = OUT / 'public'
LEDGER = Path('C:/dev/CityPrompt-building-completion-catalogue/docs/catalogue')
ORIGINAL = Path('C:/Users/andre/OneDrive/Documents/CityPrompt/frontend/public')

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
def copy(source, relative, expected=None):
    if expected: assert sha(source) == expected, source
    target=PUBLIC/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): assert sha(target)==sha(source), target
    else: shutil.copy2(source,target)
    return '/'+relative.replace('\\','/')

def main():
    approved=read(LEDGER/'quality-approved.json')['approved']
    upgrades=read(LEDGER/'priority-upgrades.json')['candidates']
    rows=[dict(r, model=Path(r['verified_model_path']), status='Visual baseline approved; app validation pending') for r in approved]
    for r in upgrades:
        f=next(f for f in r['files'] if f['path'].endswith('.glb'))
        rows.append(dict(r,domain=r['kind'],version=r['candidate'],model=Path(f['path']),sha256=f['sha256'],status='Upgrade candidate; visual and app validation pending'))
    assets=[]; trials=[]; bindings=[]; roster=[]
    source_data={domain:read(ROOT/'frontend/src/data'/name)['archetypes'] for domain,name in [('building','buildingArchetypes.json'),('park','openSpaceArchetypes.json'),('street','streetPathArchetypes.json')]}
    base_binding=read(Path('C:/dev/CityPrompt-sol-empty-lot-trial/seed/classroom-release/model-bindings.json'))['entries'][0]['metadata']
    for r in rows:
        model=r['model']; assert sha(model)==r['sha256'],model
        slug=r['version'].replace('/','-'); domain=r['domain']; parent=r['archetype_id']; variant=r['variant_id']
        source=next((s for s in source_data[domain] if s['id']==parent),{})
        sv=next((v for v in source.get('variants',[]) if v['id']==variant),{})
        package=model.parent
        recipe=read(package/'recipe.json') if domain!='building' else read(package/'build-report.json')
        dims=recipe.get('native_dimensions_m') if domain=='building' else recipe['dimensions_m']
        if isinstance(dims,dict): dims=[dims.get('width',dims.get('width_m')),dims.get('depth',dims.get('depth_m')),dims.get('height',dims.get('height_m'))]
        if domain=='building': dims=[b-a for a,b in zip(*recipe['delivered_bounds_m'])]
        thumb=None
        ref=sv.get('thumbnailUrl') or source.get('thumbnailUrl')
        if ref and (ORIGINAL/ref.lstrip('/')).is_file(): thumb=copy(ORIGINAL/ref.lstrip('/'),f'validation-assets/{slug}/reference'+Path(ref).suffix)
        if not thumb:
            refs=sorted((package/'references').rglob('*.png'))+sorted((package/'sources').glob('*.png'))
            if not refs: refs=sorted((package/'renders').glob('*.png'))
            assert refs,package
            thumb=copy(refs[0],f'validation-assets/{slug}/reference.png')
        url=copy(model,f'validation-assets/{slug}/{model.name}',r['sha256'])
        props={}
        group='detached' if domain=='building' else 'gardens' if domain=='park' else 'local'
        asset=dict(id='validation_'+variant,kind='object',definitionVersion=1,readiness='pilot',label=r['title'],description=r['status'],thumbnail=thumb,
                   model=dict(variantId=variant,revision=r['sha256'],method='RLASM 6.1' if domain=='building' else 'native_validation_fixture'),
                   calgaryGuide=dict(groupId=group,basis='form_reference'),zoneType='building' if domain=='building' else 'road' if domain=='street' else 'green_space',
                   reshapeMode='fixed_native',width=dims[0]+(4 if domain=='building' else 0),depth=dims[1]+(4 if domain=='building' else 0),
                   minWidth=dims[0]+(4 if domain=='building' else 0),minDepth=dims[1]+(4 if domain=='building' else 0),maxSize=max(240,*dims[:2]),
                   reshapeDescription='Fixed native model; enlarge its surrounding plot without stretching the building.' if domain=='building' else 'Fixed native review footprint. Move and rotate; extension, irregular shapes and route authoring remain unimplemented for this exact model.',properties=props)
        if domain=='building':
            asset['width']=asset['minWidth']=math.ceil(asset['width'])
            asset['depth']=asset['minDepth']=math.ceil(asset['depth'])
            import copy as cp
            meta=cp.deepcopy(base_binding)
            floors=int(sv.get('minFloors') or source.get('minFloors') or max(1,round(dims[2]/3.5)))
            meta['rlasm'].update(candidate=slug,variant_id=variant,archetype_id=parent,model_sha256=r['sha256'],review_sha256='',review_status=r['status'],native_dimensions_m=dict(zip(['width','depth','height'],dims)),design_dimensions_m=recipe.get('design_dimensions_m',dict(zip(['width','depth','height'],dims))))
            meta['lego'].update(family='validation-'+variant,source_variant_id=variant,generation_archetype_id=variant,variant_key=variant,reuse_keys=[variant],archetype_ids=[parent,variant],width_m=dims[0],depth_m=dims[1],height_m=dims[2],native_floors=floors,min_floors=floors,max_floors=floors,allowed_levels=[floors])
            # Runtime eligibility for a local test is distinct from visual or keeper approval.
            meta['validation_only']=True
            bindings.append(dict(variant=variant,title=r['title'],path=str(model),sha256=r['sha256'],metadata=meta,url=f'/api/v1/files/library/validation/{r["sha256"]}.glb'))
            props.update(building_archetype_id=parent,development_archetype_id=parent,development_selected_variant_id=variant,development_archetype_label=r['title'],native_home_plot=False,native_plot_axes=True,floors=floors,floor_count=floors)
            asset['nativeDimensions']=dims
        elif domain=='park' and variant in ('basketball_court_v1','research_garden_teaching_arboretum_variant_3'):
            props.update(green_space_archetype_id=parent,green_space_selected_variant_id=variant,park_trio_layout='park-trio-v3')
            asset.update(reshapeMode='adaptive_layout',minWidth=52 if variant=='basketball_court_v1' else 32,minDepth=39 if variant=='basketball_court_v1' else 40,reshapeDescription=r['extension_contract'])
            for f in (package/'modules').glob('*.glb'): copy(f,f'validation-assets/{slug}/modules/{f.name}')
        elif domain=='street' and variant in ('student_main_street_v1','student_market_street_v1'):
            # Native route compiler and renderer share this source/module lock.
            import sys
            sys.path.insert(0,'C:/dev/CityPrompt-sol-empty-lot-trial/tools/public_realm_assets')
            from stage_street_pilots import inspect_pilot
            manifest,files=inspect_pilot(package)
            manifest.update(id=variant,sourceArchetypeId=parent)
            for name,m in manifest['modules'].items(): m['url']=f'/street-kits/pilots/{variant}/{name}.glb'
            manifest['thumbnailUrl']=thumb
            for name,data in files.items():
                p=PUBLIC/f'street-kits/pilots/{variant}/{name}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            roster.append(manifest)
            props.update(road_archetype_id=parent,road_selected_variant_id=variant,width=dims[0],pick_place_street_section=variant,pick_place_automatic_3d=True,pick_place_definition_version=1,community_3d_mask_existing_tiles=True)
            asset.update(kind='street',reshapeMode='fixed_section_route',sectionWidth=dims[0],model=dict(variantId=variant,revision=manifest['sourceRecipeSha256'],method='native_street_modules_v1'))
        else:
            props.update(public_realm_trial_asset=slug,validation_fixed_fixture=True,validation_native_url=url)
            asset['description'] += '. Fixed review model: move/rotate only; extension is pending.'
            if domain=='park':props.update(green_space_archetype_id=parent,green_space_selected_variant_id=variant)
            else:props.update(road_archetype_id=parent,road_selected_variant_id=variant,width=dims[0])
            trials.append(dict(id=slug,title=r['title'],kind=domain,dimensions=dims[:2],sha256=r['sha256'],url=url,surfaceRegions=[],preserveNativeGround=True,treeWells=[],junctionSurface='pavers'))
        assets.append(asset)
        r.pop('model');r['local_url']=url;r['placement_id']=asset['id'];r['runtime_status']='NOT TESTED';r['binding']='fixed-native-review' if props.get('validation_fixed_fixture') else 'native-runtime';r['native_dimensions_m']=dims
    write(ROOT/'frontend/src/data/validationCatalogue.json',dict(entries=rows,assets=assets))
    legacy=read(Path('C:/dev/CityPrompt-sol-empty-lot-trial/frontend/src/components/viewer/globe/publicRealmTrialAssets.json'))
    write(ROOT/'frontend/src/components/viewer/globe/publicRealmTrialAssets.json',legacy+trials)
    for target in ['frontend/src/data/nativeStreetPilots.json','backend/app/data/nativeStreetPilots.json']:write(ROOT/target,roster)
    starter=dict(schema='cityprompt.classroom-starter@1',entries=[dict(domain='street',representation='native-modules',archetypeId=r['sourceArchetypeId'],variantId=r['id'],revision=r['sourceRecipeSha256']) for r in roster])
    write(ROOT/'backend/app/data/classroomStarter.json',starter)
    write(OUT/'model-bindings.json',bindings)
    write(OUT/'roster.json',rows)
    print('Prepared 27 exact local candidates: 12 buildings, 8 parks, 7 streets. Eleven fixed review fixtures have explicit behaviour gaps.')

if __name__=='__main__': main()
