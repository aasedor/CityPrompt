"""Install a reviewed, finite native park pilot without changing existing bindings.

Usage: python scripts/register_classroom_park.py --package <reading-v002>
The output model/recipe/thumbnail are retained in the LFS-backed seed package.
Stage them with scripts/stage_native_parks.py before starting the local app.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'student_reading_garden_v2': dict(key='reading-v002', archetype='student_reading_garden',
        sha256='3482efa2b69276a5ae88229288bc5f288fdcfebac9bd2aa5c1fb878d05dc47ac',
        description='Two shaded reading pergolas, flowering beds and quiet social seating.',
        entrance=dict(x=0,y=-13,widthM=2.4,arrivalY=-11)),
    'student_pickleball_garden_v1': dict(key='pickleball-tree-wells-v001',archetype='student_pickleball_garden',
        sha256='bdb0f854fab104dba862b0f8f3426b09db8c29e35a6b2bad3c2769d08e00c48a',
        description='A native-size pickleball court, shaded social seating and planted tree wells.',
        entrance=dict(x=0,y=-17,widthM=1.8,arrivalY=-15)),
    'student_tennis_garden_v2': dict(key='tennis-v002',archetype='student_tennis_garden',
        sha256='c94401f7b526e450c194f5ce46fb9976486aca83256fb30e192cc9802b3bd9fd',
        description='A garden tennis court with covered benches, spectator seating and lighting.',
        entrance=dict(x=3.2,y=-28.3,widthM=1.8,arrivalY=-25.3)),
    'student_bocce_garden_v2': dict(key='bocce-v002',archetype='student_bocce_garden',
        sha256='3933e3b09b9b2dd00567d63b9b26af04e3449d5efa6ad209a28e4178cd0eef28',
        description='A native bocce lane with vine pergola, cafe seating and garden borders.',
        entrance=dict(x=3.2,y=-24.5,widthM=1.8,arrivalY=-21.5)),
    'urban_pocket_park_v0': dict(key='pocket-native-v003',archetype='urban_pocket_park',
        sha256='985726fcef5a5964c0038088ceff65b21072e07456844d07994d509ff8493d5e',
        description='A circular lawn, curved timber seat, rustic pergola and layered flowering borders.',
        entrance=dict(x=-15,y=0,widthM=2.4,arrivalX=-12,arrivalY=0)),
    'linear_park_greenway_v0': dict(key='greenway-native-v002',archetype='linear_park_greenway',
        sha256='c99516036b3f990387b91311d34786b3d65b0899c177a00c75e8df684a0de63e',
        description='A curving meadow trail with preserved rails, seating alcoves and an iron truss gateway.',
        entrance=dict(x=0,y=-32,widthM=2.4,arrivalY=-30)),
    'inclusive_accessible_playground_v0': dict(key='inclusive-native-v002',archetype='inclusive_accessible_playground',
        sha256='1e240ac4b5f96f1e1d115c6d5cc681e68bdc29b37a924b6680ca917ab4855f12',
        description='Two timber play towers, a ramp, slides, supported swings, sensory play and sheltered seating.',
        entrance=dict(x=0,y=-18,widthM=2.4,arrivalY=-16)),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def register(package, *, specs=None, thumbnail_name='renders/aerial.png'):
    recipe_bytes = (package / 'recipe.json').read_bytes()
    recipe = json.loads(recipe_bytes)
    spec = (SPECS if specs is None else specs).get(recipe['id'])
    if not spec:
        raise ValueError('This park is outside the reviewed finite batch.')
    report = json.loads((package / 'geometry-verification.json').read_text())
    if report['status'] != 'PASS_OFFLINE_GEOMETRY':
        raise ValueError('The exact delivered model needs a passing geometry review.')
    model = (package / 'assembly-preview.glb').read_bytes()
    if digest(model) != recipe['assembly']['sha256'] or digest(model) != spec['sha256']:
        raise ValueError('Model differs from the reviewed recipe.')
    image = (package / thumbnail_name).read_bytes()
    key = spec['key']
    seed = ROOT / 'seed/classroom-parks' / key
    source_recipe = f'seed/classroom-parks/{key}/recipe.json'
    asset = dict(sha256=digest(model), archivePath=f'seed/classroom-parks/{key}/assembly-preview.glb',
                 url=f'/native-park-assets/{digest(model)}.glb')
    thumbnail = dict(sha256=digest(image), archivePath=f'seed/classroom-parks/{key}/preview.png',
                     url=f'/native-park-assets/{digest(image)}.png')
    w, d = recipe['dimensions_m']
    lo, hi = recipe['bounds_m']
    ow = math.ceil(max(w, 2 * max(abs(lo[0]), abs(hi[0]))) * 10) / 10
    od = math.ceil(max(d, 2 * max(abs(lo[1]), abs(hi[1]))) * 10) / 10
    layout = dict(id=f"{recipe['id']}--native-v1", archetypeId=spec['archetype'], variantId=recipe['id'],
                  title=recipe['title'], label='Original layout', mode='native_assembly', widthM=w, depthM=d,
                  occupiedWidthM=ow, occupiedDepthM=od, measuredBoundsM=recipe['bounds_m'],
                  sourceRecipeSha256=digest(recipe_bytes), sourceRecipePath=source_recipe, sourceStorage='repository',
                  groundOwner='assembly', terrainPolicy='prepared_level', assets={'assembly': asset}, thumbnail=thumbnail,
                  placements=[], surfaceRegions=[],
                  routes=[dict(a=r['a'], b=r['b'], z=0) for r in recipe['clear_routes']],
                  entrances=[spec['entrance']],
                  surfacePalette={'grass': [.21,.28,.105], 'paving': [.53,.50,.43]},
                  status='pilot', visualStatus='agent_native_visual_review_pass', runtimeStatus='not_tested')
    geometry = {k:v for k,v in layout.items() if k not in ('status','visualStatus','runtimeStatus','contentRevision')}
    layout['contentRevision'] = digest(json.dumps(geometry, sort_keys=True, separators=(',', ':')).encode())
    registry_path = ROOT / 'frontend/src/data/nativeParks.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    existing = next((p for p in registry['layouts'] if p['id'] == layout['id']), None)
    if existing and existing['contentRevision'] != layout['contentRevision']:
        raise ValueError('Preserved existing park revision; use a new ID for changed content.')
    if not existing:
        registry['layouts'].append(layout)
    entry = dict(domain='park', title=recipe['title'], archetype_id=layout['archetypeId'], variant_id=layout['variantId'],
                 version=key, placement_id=f"native-park:{layout['id']}", sha256=asset['sha256'],
                 asset_review='agent_native_visual_and_geometry_pass', runtime_status='NOT TESTED', completed=False)
    catalogue_asset = dict(id=entry['placement_id'], kind='object', definitionVersion=2, readiness='pilot',
                          label=recipe['title'], description=spec['description'],
                          thumbnail=thumbnail['url'], calgaryGuide={'groupId':'gardens','basis':'park_function'},
                          zoneType='green_space', reshapeMode='authored_footprint', width=ow, depth=od,
                          minWidth=ow, minDepth=od, maxSize=250,
                          model={'variantId':layout['variantId'],'revision':layout['contentRevision'],'method':'native_park_v2'},
                          reshapeDescription='The complete garden keeps its proportions when the surrounding parcel changes.',
                          properties={'green_space_archetype_id':layout['archetypeId'],
                                      'green_space_selected_variant_id':layout['variantId'],
                                      'green_space_native_layout_id':layout['id'], 'pick_place_automatic_3d':True})
    catalogue_path = ROOT / 'frontend/src/data/classroomExpansion.json'
    catalogue = json.loads(catalogue_path.read_text(encoding='utf-8')) if catalogue_path.exists() else {'entries':[], 'assets':[]}
    if not any(e['variant_id'] == entry['variant_id'] for e in catalogue['entries']):
        catalogue['entries'].append(entry)
        catalogue['assets'].append(catalogue_asset)
    files = {'recipe.json':recipe_bytes, 'assembly-preview.glb':model, 'preview.png':image,
             'geometry-verification.json':(package / 'geometry-verification.json').read_bytes()}
    for name, data in files.items():
        target = seed / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f'Preserved changed seed asset: {target}')
    seed.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (seed / name).write_bytes(data)
    write_json(registry_path, registry)
    shutil.copyfile(registry_path, ROOT / 'backend/app/data/nativeParks.json')
    write_json(catalogue_path, catalogue)
    print(json.dumps({'layout':layout['id'], 'contentRevision':layout['contentRevision'], 'runtime':'NOT TESTED'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package)
