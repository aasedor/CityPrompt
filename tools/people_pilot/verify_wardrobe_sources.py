"""Read-only provenance/input checks for picker-locked wardrobe work."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(root, public, complete=False):
    repo = Path(__file__).resolve().parents[2]
    source = json.loads(Path(__file__).with_name('character_provenance.json').read_text())
    sources = []
    for item in source['sources']:
        for file_key, hash_key in [('archiveFile', 'archiveSha256'), ('licenseFile', 'licenseSha256')]:
            actual = sha(item[file_key])
            assert actual == item[hash_key], item[file_key]
            sources.append(dict(path=item[file_key], sha256=actual, license=item['license']))
    references = json.loads((repo / 'frontend/src/features/people/peopleAppearancePreviews.json').read_text())
    # Main preserves this original catalogue before any exact-byte promotion.
    baseline = json.loads((root / 'peopleCatalogue.json.baseline').read_text())
    ids = {entry['id'] for entry in baseline}
    assert len(ids) == 23
    originals, checked_refs = [], []
    for entry in baseline:
        path = public / entry['url'].lstrip('/')
        assert sha(path) == entry['sha256'], str(path)
        originals.append(dict(id=entry['id'], path=str(path), sha256=entry['sha256']))
    for ref in references:
        if ref['id'] not in ids:
            continue
        path = public / ref['url'].lstrip('/')
        assert sha(path) == ref['sha256'] and path.stat().st_size == ref['bytes'], str(path)
        checked_refs.append(ref)
    assert len(checked_refs) == 23
    if complete:
        assert {p.stem for p in (root / 'runtime').glob('*.glb')} == ids
        for identity in ids:
            path = root / 'runtime' / (identity + '.glb')
            record = json.loads((root / (identity + '.source.json')).read_text())
            qa = json.loads((root / (identity + '.qa.json')).read_text())
            assert record['glbSha256'] == qa['sha256'] == sha(path), identity
            assert record['generatorSha256'] == sha(Path(__file__).with_name('build_wardrobe.py')), identity
            assert record['rulesSha256'] == sha(Path(__file__).with_name('wardrobe_rules.py')), identity
            if 'postprocess' in record:
                assert record['postprocess']['sha256'] == sha(Path(__file__).with_name('finish_wardrobe.py')), identity
    report = dict(localOnly=True, published=False, complete=complete, sourceInputs=sources,
                  immutableOriginals=originals, unchangedPickerReferences=checked_refs)
    (root / 'source-verification.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('C:/dev-artifacts/CityPrompt/people-wardrobe-2026-10-23'))
    parser.add_argument('--public', type=Path, default=Path('C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public'))
    parser.add_argument('--complete', action='store_true')
    args = parser.parse_args()
    result = verify(args.root, args.public, args.complete)
    print('WARDROBE_SOURCES_VERIFIED', len(result['sourceInputs']), len(result['immutableOriginals']), len(result['unchangedPickerReferences']))
