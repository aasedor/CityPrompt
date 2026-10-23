"""Explicit exact-byte local publication after a reviewed finite 31-model batch.

Copies only intentional GLB/PNG/WebP files into the established external public
tree; keeps all originals and backups. Does not push, deploy or call providers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[2]
WARDROBE = Path('C:/dev-artifacts/CityPrompt/people-wardrobe-2026-10-23')
INCLUSIVE = Path('C:/dev-artifacts/CityPrompt/people-inclusive-2026-10-23')
PUBLIC = Path('C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows_and_files():
    originals = read(WARDROBE / 'peopleCatalogue.json.baseline')
    previews = read(WARDROBE / 'peopleAppearancePreviews.json.baseline')
    assert len(originals) == len(previews) == 23
    motion = {r['id']: r for r in read(WARDROBE / 'wardrobe-qa.json')}
    measurements = {r['id']: r for r in read(WARDROBE / 'loader-validation.json')['models']}
    fixed = {r['id']: r for r in read(INCLUSIVE / 'loader-validation.json')['models']}
    roles = read(REPO / 'backend/app/data/inclusive_people.json')
    photos = read(INCLUSIVE / 'picker/previews.json')
    names = {r['id']: r for r in photos}
    files, actors, added = [], [], []
    for old in originals:
        row = dict(old)
        model = WARDROBE / 'runtime' / (old['id'] + '.glb')
        thumbnail = WARDROBE / 'qa' / (old['id'] + '.png')
        measured = measurements[old['id']]
        assert measured['sha256'] == sha(model) and measured['skins'] > 0
        idle = next(p for p in measured['poses'] if p['clip'] == 'Idle' and p['fraction'] == 0)
        low, high = idle['min'], idle['max']
        dims = [high[0] - low[0], high[2] - low[2], high[1] - low[1]]
        folder = '/street-kits/people-wardrobe-v1/'
        row.update(url=folder + model.name, thumbnailUrl=folder + thumbnail.name,
                   sha256=sha(model), bytes=model.stat().st_size, thumbnailSha256=sha(thumbnail),
                   dimensions=[round(v, 6) for v in dims])
        assert motion[row['id']]['sha256'] == row['sha256']
        row['people'] = dict(row['people'], sha256=row['sha256'], walkStrideMeters=round(motion[row['id']]['walkStrideMeters'],6))
        preview = next(p for p in previews if p['id'] == old['id'])
        row['label'] = preview['name'] + ' · ' + preview['style']
        row['description'] = f"Stylized adult wearing the {preview['style'].lower()} outfit shown in the picker. Saved action guides poses and image/video direction. Use clear level ground; provide a seat for sitting. No automatic obstacle avoidance."
        actors.append(row)
        files.extend([(model, row['url']), (thumbnail, row['thumbnailUrl'])])
        assert sha(PUBLIC / old['url'].lstrip('/')) == old['sha256'], 'Original model changed'
    for id, representation in roles.items():
        model = INCLUSIVE / 'runtime' / (id + '.glb')
        thumbnail = INCLUSIVE / 'qa' / (id + '.png')
        measured = fixed[id]
        assert measured['sha256'] == sha(model) and measured['skins'] == 0 and not measured['poses']
        assert abs(measured['bounds']['min'][1]) < .003
        folder = '/street-kits/people-inclusive-v1/'
        row = dict(id=id, label=names[id]['name'] + ' · ' + names[id]['style'], category='People', kind='object',
                   description=representation['description'].capitalize() + '. Fixed pose. Move, rotate, duplicate or delete; motion is not animated in the 3D preview. Use clear level ground.',
                   dimensions=[round(v, 6) for v in measured['dimensionsWidthDepthHeight']], datumLift=0,
                   color='#667d79', url=folder + model.name, thumbnailUrl=folder + thumbnail.name,
                   sha256=sha(model), bytes=model.stat().st_size, thumbnailSha256=sha(thumbnail),
                   peopleRepresentation=representation)
        added.append(row)
        files.extend([(model, row['url']), (thumbnail, row['thumbnailUrl']),
                      (INCLUSIVE / 'picker' / (id + '.webp'), names[id]['url'])])
    assert len(actors) == 23 and len(added) == 8 and len({r['id'] for r in actors + added}) == 31
    return actors, added, previews + photos, files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--promote', action='store_true')
    args = parser.parse_args()
    actors, added, previews, files = rows_and_files()
    expected = {r['id']: r['sha256'] for r in actors + added}
    if args.promote:
        review = read(WARDROBE / 'visual-review.json')
        assert review['reviewedModelHashes'] == expected and review['blockingFindings'] == [], 'Exact model review missing'
        for source, url in files:
            target = PUBLIC / url.lstrip('/')
            if target.exists():
                assert sha(source) == sha(target), 'Refusing conflicting immutable runtime file: ' + str(target)
        for source, url in files:
            target = PUBLIC / url.lstrip('/')
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(source, target)
            assert sha(source) == sha(target)
        backup = WARDROBE / 'publication-backups'
        backup.mkdir(exist_ok=True)
        registry_path = REPO / 'backend/app/data/project_detail_models.json'
        registry = read(registry_path)
        for row in added:
            assert row['id'] not in registry.get('trees', []) and row['id'] not in registry.get('benches', [])
            if row['id'] not in registry['props']:
                registry['props'].append(row['id'])
        assert len(registry['props']) == len(set(registry['props']))
        writes = [(REPO / 'frontend/src/features/people/peopleCatalogue.json', actors),
                  (REPO / 'frontend/src/features/people/inclusivePeopleCatalogue.json', added),
                  (REPO / 'frontend/src/features/people/peopleAppearancePreviews.json', previews),
                  (registry_path, registry)]
        for target, value in writes:
            previous = backup / target.name
            if not previous.exists():
                shutil.copy2(target, previous)
            target.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
        proof = dict(localOnly=True, published=False, models=actors + added,
                     files=[dict(path=str(source), url=url, sha256=sha(source), bytes=source.stat().st_size) for source, url in files],
                     limitations=['Picker photos are realistic style illustrations; 3D people remain architectural models.',
                                  'Inclusive eight use authored fixed poses. No automatic navigation or medical equipment certification.',
                                  'No paid AI acceptance renders or physical student-laptop/mobile measurements in this batch.'])
        (REPO / 'tools/people_pilot/people_model_delivery.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(rigged=len(actors), fixed=len(added), previews=len(previews), files=len(files), promoted=args.promote)))
