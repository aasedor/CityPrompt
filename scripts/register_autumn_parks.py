"""Register only the exact three offline-reviewed autumn park deliveries."""
import argparse
import hashlib
import json
from pathlib import Path
from register_classroom_park import register

SPECS={'student_urban_splash_plaza_v1': {'key': 'autumn-splash-v002', 'archetype': 'splash_pad_area', 'sha256': '3222433e6a629bc5d3328901c96d270619623cb8b758ecda78cda57b5e6e9e6d', 'description': 'Colourful flowing paving, flush jets, supported tipping bucket and planted seating edges', 'entrance': {'x': 0, 'y': -18.0, 'widthM': 2.7, 'arrivalY': -15}, 'group': 'play_sport'}, 'student_stone_labyrinth_garden_v1': {'key': 'autumn-labyrinth-v005', 'archetype': 'labyrinth_meditation', 'sha256': 'af81f58831b58430d0e23608782bc3d62086a34b5335c303a03eccc0e54e8018', 'description': 'Concentric connected limestone walk, quiet central stone seat, clipped hedges and layered enclosed garden', 'entrance': {'x': 1.6, 'y': -20, 'widthM': 1.15, 'arrivalY': -17}, 'group': 'gardens'}, 'student_sheltered_dog_park_v1': {'key': 'autumn-dog-v001', 'archetype': 'dog_park', 'sha256': 'd164bee7af12da298a0e507122bd080143a73346dd0521955715e41a6063515e', 'description': 'Four turf rooms, three timber shade shelters, gravel circulation, timber rails, meadow edges and double-gate entry', 'entrance': {'x': 0, 'y': -21.0, 'widthM': 2.7, 'arrivalY': -17}, 'group': 'play_sport'}}

def main(package):
    recipe=json.loads((package/'recipe.json').read_text());review=json.loads((package/'visual-review.json').read_text())
    if review.get('status')!='PASS_OFFLINE_NATIVE_REVIEW' or review.get('model_sha256')!=recipe['assembly']['sha256']:
        raise ValueError('Require the actual exported-model visual review')
    reference=next(r for r in recipe['source_references'] if r['role']=='front')
    hero=Path(reference['path']).name
    if hashlib.sha256((package/hero).read_bytes()).hexdigest()!=reference['sha256']:raise ValueError('Hero must be the exact photographic reference')
    register(package,specs=SPECS,thumbnail_name=hero)
    # Preserve the readable exact-variant visual ledger with the model seed.
    seed=Path(__file__).resolve().parents[1]/'seed/classroom-parks'/SPECS[recipe['id']]['key']
    (seed/'visual-review.json').write_bytes((package/'visual-review.json').read_bytes())

def stage(public):
    root=Path(__file__).resolve().parents[1]
    registry=json.loads((root/'frontend/src/data/nativeParks.json').read_text())
    selected=[p for p in registry['layouts'] if p['variantId'] in SPECS]
    if len(selected)!=3:raise ValueError('Expected all three exact autumn layouts')
    for layout in selected:
        raw=(root/layout['sourceRecipePath']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=layout['sourceRecipeSha256']:raise ValueError('Recipe changed')
        for asset in [*layout['assets'].values(),layout['thumbnail']]:
            data=(root/asset['archivePath']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=asset['sha256']:raise ValueError('Asset changed')
            if asset['url'].endswith('.glb'):
                if data[:4]!=b'glTF':raise ValueError('Invalid GLB')
                doc=json.loads(data[20:20+int.from_bytes(data[12:16],'little')])
                if any('uri' in item for key in ('buffers','images') for item in doc.get(key,[])):raise ValueError('External dependency')
            target=public/asset['url'].lstrip('/')
            if not target.resolve().is_relative_to(public.resolve()):raise ValueError('Unsafe destination')
            if target.exists() and target.read_bytes()!=data:raise ValueError('Existing asset differs')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        print('HASH_VERIFIED_STAGED',layout['variantId'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path);p.add_argument('--public-dir',type=Path);a=p.parse_args()
    if a.package:main(a.package)
    if a.public_dir:stage(a.public_dir)
    if not a.package and not a.public_dir:p.error('Select package registration or public staging')
