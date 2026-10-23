"""Contact sheet and explicit reviewed finite20 local promotion. No network calls.

Run first without --promote to generate the contact sheet and compact provenance.
Only after actual-model review, rerun with --promote to append catalogue rows and
copy exactly forty approved GLB/PNG files into the established external public tree.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from PIL import Image, ImageDraw

ROOT = Path('C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters')
PUBLIC = Path('C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/street-kits/people-community-v1')
REPO = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--promote', action='store_true')
    args = parser.parse_args()
    measured = json.loads((ROOT / 'measurements.json').read_text())
    assert len(measured['actors']) == 20
    for limitation in [
        'The fifteen runtime actions use deterministic procedural poses over these rigs. Running uses a faster Walk clip; no native Run or fifteen-clip action library is included.',
        'Walking needs clear level paths; no automatic obstacle avoidance, chair detection or pathfinding. Sitting needs a student-provided seat.',
    ]:
        if limitation not in measured['limitations']:
            measured['limitations'].append(limitation)
    sheet = Image.new('RGB', (1100, 1120), '#e4e6e2')
    draw = ImageDraw.Draw(sheet)
    rows = []
    for i, actor in enumerate(measured['actors']):
        design = actor['design']
        preview = ROOT / 'qa' / (actor['id'] + '.png')
        model = ROOT / 'runtime' / (actor['id'] + '.glb')
        assert sha(preview) == actor['thumbnailSha256'] and sha(model) == actor['sha256']
        image = Image.open(preview).convert('RGB')
        image.thumbnail((216, 243))
        x, y = (i % 5) * 220, (i // 5) * 280
        sheet.paste(image, (x + 2, y))
        draw.text((x + 6, y + 246), design['name'] + ' / ' + str(round(actor['dimensions'][2], 2)) + ' m', fill='#182b30')
        draw.text((x + 6, y + 262), design['outfit'], fill='#182b30')
        rows.append({'id': actor['id'], 'label': design['name'] + ' · ' + design['outfit'], 'category': 'People',
                     'kind': 'object', 'color': design['jacket'],
                     'description': 'Stylized athletic adult with ' + design['outfit'] + '. Saved action guides the pose and image/video direction. Use a clear level surface; provide a seat for sitting. No automatic obstacle avoidance.',
                     'dimensions': [round(v, 6) for v in actor['dimensions']], 'datumLift': 0,
                     'url': '/street-kits/people-community-v1/' + model.name,
                     'thumbnailUrl': '/street-kits/people-community-v1/' + preview.name,
                     'sha256': actor['sha256'], 'bytes': actor['bytes'], 'thumbnailSha256': actor['thumbnailSha256'],
                     'people': {'walkClip': 'Walk', 'idleClip': 'Idle', 'walkStrideMeters': round(actor['walkStrideMeters'], 6), 'sha256': actor['sha256']}})
        for clip in actor['clips']:
            clip.pop('samples')
    sheet.save(ROOT / 'qa' / 'community-contact-sheet.jpg', quality=94)
    for suffix in ['portrait', 'walk-back']:
        board = Image.new('RGB', (1280, 396), '#e4e6e2')
        labels = ImageDraw.Draw(board)
        for i, slug in enumerate(['ava', 'noah', 'zara', 'jules']):
            preview = ROOT / 'qa' / ('people-community-' + slug + '-' + suffix + '.png')
            image = Image.open(preview).convert('RGB')
            image.thumbnail((320, 360))
            board.paste(image, (i * 320, 0))
            labels.text((i * 320 + 12, 372), slug + ' / ' + suffix, fill='#182b30')
        board.save(ROOT / 'qa' / ('community-' + suffix + '-review.jpg'), quality=95)
    measured['performance'] = {'actorCount': 20, 'totalGLBBytes': sum(a['bytes'] for a in measured['actors']),
                               'totalTriangles': sum(a['triangles'] for a in measured['actors']),
                               'totalEstimatedDecodedBytes': sum(a['estimatedDecodedBytes'] for a in measured['actors']),
                               'minGLBBytes': min(a['bytes'] for a in measured['actors']), 'maxGLBBytes': max(a['bytes'] for a in measured['actors'])}
    if args.promote:
        measured['visualReview'] = {'authority': 'Assistant actual-model visual QA; local concept use only',
                                    'allTwentyThumbnailsReviewed': True, 'representativePortraitWalkBackIds': ['ava', 'noah', 'zara', 'jules'],
                                    'verdict': 'Coherent stylized adult entourage; measured ground contact and closed male necklines. Simple shoulder/collar seams remain visible at close range.',
                                    'boards': [{'path': str(ROOT / 'qa' / name), 'sha256': sha(ROOT / 'qa' / name)}
                                               for name in ['community-contact-sheet.jpg', 'community-portrait-review.jpg', 'community-walk-back-review.jpg']]}
    (REPO / 'tools/people_pilot/community_provenance.json').write_text(json.dumps(measured, indent=2) + '\n')
    if args.promote:
        catalogue = REPO / 'frontend/src/features/people/peopleCatalogue.json'
        original = catalogue.read_text(encoding='utf-8')
        parsed = json.loads(original)
        backup = ROOT / 'peopleCatalogue.original.json'
        if not backup.exists():
            assert len(parsed) == 3
            shutil.copy2(catalogue, backup)
        previous = json.loads(backup.read_text(encoding='utf-8'))
        immutable = lambda actor: {key: value for key, value in actor.items() if key != 'description'}
        assert [immutable(a) for a in parsed[:3]] == [immutable(a) for a in previous] and len(previous) == 3
        assert len(parsed) == 3 or parsed[3:] == rows
        expected_originals = []
        for actor in previous:
            updated_actor = dict(actor)
            outfit = actor['description'].split('. Idle while editing;')[0]
            updated_actor['description'] = outfit + '. Choose a saved action for poses and image/video direction. Use a clear level surface; provide a seat for sitting. No automatic obstacle avoidance.'
            expected_originals.append(updated_actor)
        # This descriptions-only refresh was explicitly authorized by the
        # coordinator. All original identifiers and exact-byte locks stay fixed.
        for old, new in zip(parsed[:3], expected_originals):
            original = original.replace(json.dumps(old['description'], ensure_ascii=False), json.dumps(new['description'], ensure_ascii=False), 1)
        # Preserve the original three entries' source text and metadata.
        if len(parsed) == 3:
            closing = original.rfind(']')
            updated = original[:closing].rstrip() + ',\n' + ',\n'.join('  ' + json.dumps(row, ensure_ascii=False) for row in rows) + '\n]\n'
            catalogue.write_text(updated, encoding='utf-8')
        else:
            catalogue.write_text(original, encoding='utf-8')
        PUBLIC.mkdir(parents=True, exist_ok=True)
        for actor in measured['actors']:
            for folder, extension in [('runtime', '.glb'), ('qa', '.png')]:
                src = ROOT / folder / (actor['id'] + extension)
                dst = PUBLIC / src.name
                shutil.copy2(src, dst)
                assert sha(src) == sha(dst)
        files = []
        archive = ROOT.parent / 'people-community-v1-local-assets.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
            for actor in measured['actors']:
                for extension in ['.glb', '.png']:
                    file = PUBLIC / (actor['id'] + extension)
                    url = '/street-kits/people-community-v1/' + file.name
                    member = 'public' + url
                    info = zipfile.ZipInfo(member, date_time=(2026, 10, 22, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    package.writestr(info, file.read_bytes())
                    files.append({'url': url, 'path': member, 'sha256': sha(file), 'bytes': file.stat().st_size})
        delivery = {'schemaVersion': 1, 'localOnly': True, 'published': False,
                    'archiveFile': str(archive), 'archiveSha256': sha(archive), 'archiveBytes': archive.stat().st_size,
                    'portableRepositorySource': False,
                    'license': 'CC0-1.0', 'creator': 'Quaternius with CityPrompt garment/shape derivatives',
                    'provenance': 'tools/people_pilot/community_provenance.json', 'files': files,
                    'limitation': 'External local archive. Hosted asset preparation requires an approved portable pinned source integration before deployment.'}
        (REPO / 'tools/people_pilot/community_delivery.json').write_text(json.dumps(delivery, indent=2) + '\n')
        assert json.loads(catalogue.read_text(encoding='utf-8'))[:3] == expected_originals
        print('PROMOTED exact 20 GLBs + 20 thumbnails; original3 byte locks preserved, descriptions refreshed')
    print(json.dumps(measured['performance']))
