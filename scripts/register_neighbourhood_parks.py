"""Register only the independently reviewed allotment/nature finite batch locally."""
import argparse
import hashlib
import json
from pathlib import Path
from register_classroom_park import register

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'student_forest_adventure_v1': dict(
        key='neighbourhood-nature-v006', archetype='nature_play_area',
        sha256='5d2ac31189fb9ba489af4445549c8a551895d4c5b90280fa0d82925a5d32e327',
        description='Woodland stream, flat stepping stones, log crossings, tree deck and leafy willow tunnel.',
        entrance=dict(x=0, y=-23, widthM=2.6, arrivalY=-20.5), group='play_sport'),
    'student_community_allotment_v1': dict(
        key='neighbourhood-allotment-v006', archetype='community_garden_enhanced',
        sha256='02ce66e57b40653d578aa41389040b9925d1f0c38944a87807176882b3388b6f',
        description='Four productive garden rooms, eight coloured sheds, trellises and a shared orchard.',
        entrance=dict(x=0, y=-23, widthM=3.2, arrivalY=-20), group='gardens'),
}

def main(package):
    recipe = json.loads((package/'recipe.json').read_text())
    review = json.loads((package/'independent-review.json').read_text())
    if (recipe['id'] not in SPECS or review.get('status') != 'PASS_OFFLINE_NATIVE_REVIEW'
        or review.get('unresolved_p0') != 0 or review.get('unresolved_p1') != 0
        or review.get('model_sha256') != SPECS[recipe['id']]['sha256']):
        raise ValueError('Exact independent holistic pass required')
    for evidence in review['inspected_files']:
        path = package / evidence['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']:
            raise ValueError(f'Reviewed evidence changed: {path.name}')
    source = next(s for s in recipe['source_references'] if s['role']=='front')
    hero = Path(source['path']).name
    if hashlib.sha256((package/hero).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Thumbnail must be the exact front reference')
    backup = package/'before-registration'
    backup.mkdir(exist_ok=True)
    for relative in ('frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json',
                     'frontend/src/data/classroomExpansion.json'):
        target = backup/relative.replace('/', '__')
        if not target.exists():target.write_bytes((ROOT/relative).read_bytes())
    register(package, specs=SPECS, thumbnail_name=hero)
    seed = ROOT/'seed/classroom-parks'/SPECS[recipe['id']]['key']
    (seed/'independent-review.json').write_bytes((package/'independent-review.json').read_bytes())

def stage(public):
    layouts = json.loads((ROOT/'frontend/src/data/nativeParks.json').read_text())['layouts']
    for layout in (p for p in layouts if p['variantId'] in SPECS):
        for asset in [*layout['assets'].values(), layout['thumbnail']]:
            data = (ROOT/asset['archivePath']).read_bytes()
            if hashlib.sha256(data).hexdigest() != asset['sha256']:
                raise ValueError('Changed registered asset')
            target = public/asset['url'].lstrip('/')
            if not target.resolve().is_relative_to(public.resolve()):raise ValueError('Unsafe path')
            if target.exists() and target.read_bytes() != data:raise ValueError('Preserved existing asset')
            target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(data)
        print('HASH_VERIFIED_STAGED', layout['variantId'])

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package', type=Path);parser.add_argument('--public-dir', type=Path)
    args=parser.parse_args()
    if args.package:main(args.package)
    if args.public_dir:stage(args.public_dir)
    if not args.package and not args.public_dir:parser.error('Select a reviewed package or public directory')
