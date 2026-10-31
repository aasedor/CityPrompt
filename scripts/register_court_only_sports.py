"""Register the finite visually reviewed four-court local pilot, preserving old IDs.

python scripts/register_court_only_sports.py --packages artifacts/court-only-sports-20261024
Validation and immutable-target checks finish for the whole batch before writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/public_realm_assets'))
from court_only_specs import COURT_ONLY_KINDS, court_only_recipe


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False)+'\n').encode()


def prepare(packages, root=ROOT):
    registry_path = root/'frontend/src/data/nativeParks.json'
    backend_path = root/'backend/app/data/nativeParks.json'
    if registry_path.read_bytes() != backend_path.read_bytes():
        raise ValueError('Resolve the existing frontend/backend registry mismatch first.')
    registry = json.loads(registry_path.read_bytes())
    catalogue = {'assets': []}
    files = {}
    for kind in COURT_ONLY_KINDS:
        package = packages/f'{kind}-v1'
        recipe_bytes = (package/'recipe.json').read_bytes()
        recipe = json.loads(recipe_bytes)
        expected = court_only_recipe(kind)
        if any(recipe.get(k) != expected[k] for k in ('id','sport','playing_m','module_m','dimensions_m','include_enclosure')):
            raise ValueError(f'Unexpected court specification: {kind}')
        model = (package/'assembly-preview.glb').read_bytes()
        image = (package/'renders/aerial.png').read_bytes()
        report_bytes = (package/'geometry-verification.json').read_bytes()
        report = json.loads(report_bytes)
        sha = digest(model)
        if (not model.startswith(b'glTF') or not image.startswith(b'\x89PNG\r\n\x1a\n')
                or report.get('status') != 'PASS_OFFLINE_GEOMETRY'
                or report.get('model_sha256') != sha or recipe['assembly']['sha256'] != sha):
            raise ValueError(f'Exact model verification missing: {kind}')
        slug = f'court-only-{kind.replace("_", "-")}-v001'
        seed = f'seed/classroom-parks/{slug}'
        thumbnail_url = f'/archetypes/openspaces/{slug}/preview.png'
        w, d = expected['module_m']
        route = expected['clear_routes'][0]
        layout = dict(id=f'{expected["id"]}--native-v1', archetypeId=f'court_only_{kind}',
                      variantId=expected['id'], title=expected['title'], label='Court only',
                      mode='native_assembly', widthM=w, depthM=d, occupiedWidthM=w, occupiedDepthM=d,
                      measuredBoundsM=report['bounds_m'], sourceRecipeSha256=digest(recipe_bytes),
                      sourceRecipePath=f'{seed}/recipe.json', sourceStorage='repository',
                      groundOwner='assembly', terrainPolicy='prepared_level',
                      assets={'assembly':dict(sha256=sha,archivePath=f'{seed}/assembly-preview.glb',url=f'/native-park-assets/{sha}.glb')},
                      thumbnail=dict(sha256=digest(image),archivePath=f'{seed}/preview.png',url=thumbnail_url),
                      placements=[],surfaceRegions=[],routes=[dict(a=route['a'],b=route['b'],z=0)],
                      entrances=[dict(x=route['a'][0],y=route['a'][1],arrivalX=route['b'][0],arrivalY=route['b'][1],widthM=1.8)],
                      walkSurfaceMaterials=['court','runoff','paint','key','kitchen','sand'],
                      surfacePalette={'grass':[.21,.28,.105],'paving':[.53,.50,.43]},
                      status='pilot',visualStatus='agent_native_visual_review_pass',runtimeStatus='not_tested')
        geometry = {k:v for k,v in layout.items() if k not in ('status','visualStatus','runtimeStatus')}
        layout['contentRevision'] = digest(json.dumps(geometry,sort_keys=True,separators=(',',':')).encode())
        existing = next((p for p in registry['layouts'] if p['id']==layout['id']),None)
        if existing and existing['contentRevision'] != layout['contentRevision']:
            raise ValueError(f'Preserve existing revision: {layout["id"]}')
        if not existing: registry['layouts'].append(layout)
        catalogue['assets'].append(dict(
            id=f'native-park:{layout["id"]}',kind='object',definitionVersion=2,readiness='pilot',
            label=layout['title'],description='Individual court with markings, equipment and clear playing reserve. Combine and repeat to build an athletic park.',
            thumbnail=thumbnail_url,calgaryGuide={'groupId':'play_sport','basis':'park_function'},
            zoneType='green_space',reshapeMode='fixed_native',width=w,depth=d,minWidth=w,minDepth=d,
            maxWidth=w,maxDepth=d,maxSize=max(w,d),
            model={'variantId':layout['variantId'],'revision':layout['contentRevision'],'method':'native_park_v2'},
            reshapeDescription='Court dimensions stay fixed. Move, rotate or Place another to assemble your athletic park.',
            properties={'green_space_archetype_id':layout['archetypeId'],
                        'green_space_selected_variant_id':layout['variantId'],
                        'green_space_native_layout_id':layout['id'],'court_only_native':True,'pick_place_automatic_3d':True}))
        for name,data in {'recipe.json':recipe_bytes,'assembly-preview.glb':model,'preview.png':image,
                          'geometry-verification.json':report_bytes}.items():
            files[root/seed/name] = data
        files[root/f'frontend/public/native-park-assets/{sha}.glb'] = model
        files[root/f'frontend/public{thumbnail_url}'] = image
    # All promoted assets and catalogue bindings are immutable. A new revision
    # requires a new finite batch/ID rather than overwriting reviewed content.
    files[root/'frontend/src/data/courtOnlySports.json'] = encoded(catalogue)
    for target,data in files.items():
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f'Preserve existing court asset: {target}')
    files[registry_path] = encoded(registry)
    files[backend_path] = encoded(registry)
    return files


def register(packages, root=ROOT):
    files = prepare(packages, root)
    original = {p:p.read_bytes() if p.exists() else None for p in files}
    try:
        for target,data in files.items():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    except Exception:
        for target,data in original.items():
            if data is not None: target.write_bytes(data)
            elif target.exists(): target.unlink()
        raise
    print(json.dumps({'courts':list(COURT_ONLY_KINDS),'files':len(files),'publication':'local pilot only'}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packages',type=Path,required=True)
    register(p.parse_args().packages)
