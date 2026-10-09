"""Register only the independently reviewed five-park neighbourhood batch locally."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from register_classroom_park import register

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'student_prairie_picnic_grove_v1': dict(
        key='prairie-picnic-v003', archetype='prairie_picnic_grove',
        sha256='ac659213d630db8ccd43ac979b925ed10ad91580fd5ddc3377c276e0be7e97ae',
        description='Two timber picnic shelters, communal tables, dense flowering prairie and a continuous shaded walking loop.',
        entrance=dict(x=0,y=-26,widthM=3.0,arrivalY=-23),group='neighbourhood',
        thumbnail_slug='prairie-picnic-grove', walk_surface_materials=['paving','edge']),
    'student_neighbourhood_sports_green_v1': dict(
        key='neighbourhood-sports-v002',archetype='neighbourhood_sports_green',
        sha256='eb6e1b2cec51485405504914d37f6b513cecc9f6d0fd645ed23c921cd73a745e',
        description='A small marked playing field with netted goals, perimeter walk, exercise stations and shaded seating.',
        entrance=dict(x=0,y=-33,widthM=3.0,arrivalY=-30),group='play_sport',
        thumbnail_slug='neighbourhood-sports-green',walk_surface_materials=['paving','edge','rubber','field']),
    'student_sensory_wellness_garden_v1': dict(
        key='sensory-wellness-v003',archetype='sensory_wellness_garden',
        sha256='ecbe94622d7b698efd1085a6a651d2c48f6a0c0ffb8c961c32acbb45f42e8f6e',
        description='A continuous garden loop, fragrant planting rooms, curved timber seating, raised herbs and two quiet pergolas.',
        entrance=dict(x=0,y=-23,widthM=3.0,arrivalY=-20),group='gardens',
        thumbnail_slug='sensory-wellness-garden',walk_surface_materials=['paving','edge']),
    'student_urban_skate_plaza_v1': dict(
        key='urban-skate-v005',archetype='urban_skate_plaza',
        sha256='b29d49b1c976bd1a5022b42c31ab2e1fa808599921ade7bfb7e4b676ac3bc8f0',
        description='A curved concrete bowl, quarter pipes, bank, grind ledge and rail inside a planted spectator loop.',
        entrance=dict(x=0,y=-27,widthM=3.0,arrivalY=-24),group='play_sport',
        thumbnail_slug='urban-skate-plaza',walk_surface_materials=['paving','edge','concrete']),
    'student_bicycle_pump_track_park_v1': dict(
        key='bicycle-pump-v004',archetype='bicycle_pump_track_park',
        sha256='1625b0c7e9a8a8e67126364578888e996af2a48ce77aad235927b94efe28e47b',
        description='A rolling banked cycle circuit, low beginner loop, connected entrances and shaded bicycle gathering.',
        entrance=dict(x=0,y=-30,widthM=3.0,arrivalY=-27),group='play_sport',
        thumbnail_slug='bicycle-pump-track-park',walk_surface_materials=['paving','edge','asphalt']),
}

def preflight_registry(recipe, recipe_bytes, spec):
    front=(ROOT/'frontend/src/data/nativeParks.json').read_bytes()
    back=(ROOT/'backend/app/data/nativeParks.json').read_bytes()
    if front!=back:raise ValueError('Frontend/backend native park mirrors differ; preserve both')
    layouts=[p for p in json.loads(front)['layouts'] if p['variantId']==recipe['id']]
    catalogue=json.loads((ROOT/'frontend/src/data/classroomExpansion.json').read_text(encoding='utf-8'))
    entries=[p for p in catalogue['entries'] if p['variant_id']==recipe['id']]
    assets=[p for p in catalogue['assets'] if p['model']['variantId']==recipe['id']]
    if not layouts and not entries and not assets:return
    if len(layouts)!=1 or len(entries)!=1 or len(assets)!=1:
        raise ValueError('Inconsistent existing same-variant records; preserve catalogue')
    layout,entry,asset=layouts[0],entries[0],assets[0]
    expected_id=recipe['id']+'--native-v1';placement='native-park:'+expected_id
    w,d=recipe['dimensions_m'];lo,hi=recipe['bounds_m']
    ow=math.ceil(max(w,2*max(abs(lo[0]),abs(hi[0])))*10)/10
    od=math.ceil(max(d,2*max(abs(lo[1]),abs(hi[1])))*10)/10
    checks=[layout['id']==expected_id,layout['archetypeId']==spec['archetype'],layout['sourceRecipeSha256']==hashlib.sha256(recipe_bytes).hexdigest(),
        layout['assets']['assembly']['sha256']==spec['sha256'],entry['sha256']==spec['sha256'],entry['archetype_id']==spec['archetype'],entry['placement_id']==placement,
        asset['id']==placement,asset['label']==recipe['title'],asset['model']['revision']==layout['contentRevision'],asset['model']['method']=='native_park_v2',
        asset['width']==ow,asset['depth']==od,asset['calgaryGuide']['groupId']==spec['group'],
        asset['properties'].get('green_space_native_layout_id')==expected_id,asset['thumbnail']==layout['thumbnail']['url']]
    if not all(checks):raise ValueError('Inconsistent existing same-variant card/assets; preserve catalogue')


def main(package):
    recipe = json.loads((package/'recipe.json').read_text(encoding='utf-8'))
    review = json.loads((package/'independent-review.json').read_text(encoding='utf-8'))
    if (recipe['id'] not in SPECS or review.get('status') != 'PASS_OFFLINE_NATIVE_REVIEW'
        or review.get('unresolved_p0') != 0 or review.get('unresolved_p1') != 0
        or review.get('model_sha256') != SPECS[recipe['id']]['sha256']):
        raise ValueError('Exact independent holistic pass required')
    evidence_paths={p['path'] for p in review.get('inspected_files',[])}
    if not {'recipe.json','assembly-preview.glb','geometry-verification.json'}.issubset(evidence_paths):
        raise ValueError('Review must lock nonempty exact recipe, assembly and geometry evidence')
    for evidence in review['inspected_files']:
        path = package / evidence['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']:
            raise ValueError(f'Reviewed evidence changed: {path.name}')
    source = next(s for s in recipe['source_references'] if s['role']=='front')
    hero = Path(source['path']).name
    if hashlib.sha256((package/hero).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Thumbnail must be the exact front reference')
    for name,digest in recipe.get('source_build_files',{}).items():
        if hashlib.sha256((package/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Immutable build source changed: {name}')
    preflight_registry(recipe,(package/'recipe.json').read_bytes(),SPECS[recipe['id']])
    backup = package/'before-registration'
    backup.mkdir(exist_ok=True)
    for relative in ('frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json',
                     'frontend/src/data/classroomExpansion.json'):
        target = backup/relative.replace('/', '__')
        if not target.exists():target.write_bytes((ROOT/relative).read_bytes())
    register(package, specs=SPECS, thumbnail_name=hero)
    seed = ROOT/'seed/classroom-parks'/SPECS[recipe['id']]['key']
    (seed/'independent-review.json').write_bytes((package/'independent-review.json').read_bytes())
    for name in recipe.get('source_build_files',{}):
        (seed/name).write_bytes((package/name).read_bytes())
    for name in ('independent-module-verification.json','runtime-review.md'):
        if (package/name).exists():(seed/name).write_bytes((package/name).read_bytes())

def stage(public):
    layouts = json.loads((ROOT/'frontend/src/data/nativeParks.json').read_text(encoding='utf-8'))['layouts']
    pending=[]
    for layout in (p for p in layouts if p['variantId'] in SPECS):
        for asset in [*layout['assets'].values(), layout['thumbnail']]:
            data = (ROOT/asset['archivePath']).read_bytes()
            if hashlib.sha256(data).hexdigest() != asset['sha256']:
                raise ValueError('Changed registered asset')
            target = public/asset['url'].lstrip('/')
            if not target.resolve().is_relative_to(public.resolve()):raise ValueError('Unsafe path')
            if target.exists() and target.read_bytes() != data:raise ValueError('Preserved existing asset')
            pending.append((target,data))
        print('HASH_VERIFIED_STAGED', layout['variantId'])
    for target,data in pending:
        target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(data)

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package', type=Path);parser.add_argument('--public-dir', type=Path)
    args=parser.parse_args()
    if args.package:main(args.package)
    if args.public_dir:stage(args.public_dir)
    if not args.package and not args.public_dir:parser.error('Select a reviewed package or public directory')
