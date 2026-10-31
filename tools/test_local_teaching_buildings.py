import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from tools.local_teaching_buildings import install


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_shipped_manifest_binds_exact_reviewed_candidates_and_additive_lessons():
    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / 'frontend/src/data/localTeachingBuildings.json').read_text(encoding='utf-8'))
    cards = json.loads((repo / 'tools/planning_history/reviewed-inputs/candidates.json').read_text(encoding='utf-8'))['records']
    assert len(manifest['models']) == len(cards) == 7
    assert {m['asset']['properties']['development_archetype_id'] for m in manifest['models']} == {c['archetypeId'] for c in cards}
    for row in manifest['models']:
        asset = row['asset']
        card = next(c for c in cards if c['archetypeId'] == asset['properties']['development_archetype_id'])
        assert card['modelSha256'] == row['model_sha256']
        assert card['variantId'] == asset['model']['variantId']
        model = next(f for f in row['files'] if f['role'] == 'model')
        review = next(f for f in row['files'] if f['role'] == 'review')
        assert model['sha256'] == row['model_sha256']
        assert model['url'] == asset['properties']['validation_native_url']
        assert review['sha256'] == row['review_sha256']
        for record in [manifest['lessons'][asset['id']], manifest['history'][asset['id']]]:
            assert record['modelRevision'] == asset['model']['revision'] == row['candidate']
            assert record['variantId'] == asset['model']['variantId']
            assert record['archetypeId'] == card['archetypeId']
        assert manifest['history'][asset['id']]['constructionYear'] is None


@pytest.fixture
def package(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    # A real minimal box GLB exercises transformed native envelope checks.
    import trimesh
    mesh = trimesh.creation.box(extents=[8, 6, 10])
    mesh.apply_translation([0, 3, 0])  # glTF Y up; width=8, depth=10, height=6
    (source / 'model.glb').write_bytes(mesh.export(file_type='glb'))
    (source / 'front.png').write_bytes(b'locked-front')
    model_hash = digest(source / 'model.glb')
    (source / 'review.json').write_text(json.dumps({
        'candidate': 'pilot-v001', 'model_sha256': model_hash,
        'reviewer': 'independent verifier', 'holistic_review_performed': True,
        'architectural_clay_pass': True, 'unresolved_p0': 0, 'unresolved_p1': 0,
    }))
    files = [{'source': name, 'url': '/local-teaching/' + name, 'sha256': digest(source / name), 'role': role}
             for name, role in [('model.glb', 'model'), ('front.png', 'reference'), ('review.json', 'review')]]
    manifest = {'schema': 'cityprompt.local-teaching-buildings@1', 'local_trial_only': True,
                'models': [{'candidate': 'pilot-v001', 'model_sha256': model_hash,
                            'asset': {'nativeDimensions': [8, 10, 6]}, 'files': files}]}
    return manifest, source, tmp_path / 'public'


def test_dry_run_then_install_and_idempotent_readback(package):
    manifest, source, public = package
    report = install(manifest, source, public, ['pilot-v001'])
    assert report['status'] == 'dry_run'
    assert not public.exists()
    report = install(manifest, source, public, ['pilot-v001'], apply=True)
    assert report['status'] == 'installed_verified'
    assert len(report['files']) == 3
    assert all(row['sha256'] == digest(public / row['url'].lstrip('/')) for row in report['files'])
    assert install(manifest, source, public, ['pilot-v001'], apply=True)['status'] == 'installed_verified'


def test_changed_source_and_existing_destination_are_not_overwritten(package):
    manifest, source, public = package
    (source / 'front.png').write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash'):
        install(manifest, source, public, ['pilot-v001'], apply=True)
    assert not public.exists()  # Validate entire finite batch before copying.
    (source / 'front.png').write_bytes(b'locked-front')
    destination = public / 'local-teaching/model.glb'
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b'existing student asset')
    with pytest.raises(ValueError, match='destination'):
        install(manifest, source, public, ['pilot-v001'], apply=True)
    assert destination.read_bytes() == b'existing student asset'
    assert not (destination.parent / 'front.png').exists()


def test_rejects_wrong_review_or_native_envelope(package):
    manifest, source, public = package
    review = json.loads((source / 'review.json').read_text())
    review['model_sha256'] = 'f' * 64
    (source / 'review.json').write_text(json.dumps(review))
    manifest['models'][0]['files'][2]['sha256'] = digest(source / 'review.json')
    with pytest.raises(ValueError, match='review'):
        install(manifest, source, public, ['pilot-v001'])
    review['model_sha256'] = digest(source / 'model.glb')
    (source / 'review.json').write_text(json.dumps(review))
    manifest['models'][0]['files'][2]['sha256'] = digest(source / 'review.json')
    manifest['models'][0]['asset']['nativeDimensions'][0] = 9
    with pytest.raises(ValueError, match='envelope'):
        install(manifest, source, public, ['pilot-v001'])


def test_accepts_existing_wave2_offline_review_schema_without_rewriting_it(package):
    manifest, source, public = package
    review = json.loads((source / 'review.json').read_text())
    review.pop('architectural_clay_pass')
    review.update(schema='cityprompt.rlasm.independent_architectural_clay_review@1',
                  decision='approved_offline_architectural_clay', holistic=True,
                  unresolved_p0=[], unresolved_p1=[])
    (source / 'review.json').write_text(json.dumps(review))
    manifest['models'][0]['files'][2]['sha256'] = digest(source / 'review.json')
    assert install(manifest, source, public, ['pilot-v001'])['status'] == 'dry_run'
    review['unresolved_p1'] = ['open issue']
    (source / 'review.json').write_text(json.dumps(review))
    manifest['models'][0]['files'][2]['sha256'] = digest(source / 'review.json')
    with pytest.raises(ValueError, match='review'):
        install(manifest, source, public, ['pilot-v001'])


def test_rejects_unknown_candidate_and_path_escape(package):
    manifest, source, public = package
    with pytest.raises(ValueError, match='candidate'):
        install(manifest, source, public, ['unreviewed-v001'])
    manifest['models'][0]['files'][0]['url'] = '/../escape.glb'
    with pytest.raises(ValueError, match='path'):
        install(manifest, source, public, ['pilot-v001'], apply=True)


def test_existing_top_level_runtime_junction_is_an_explicit_asset_namespace(package, tmp_path):
    manifest, source, public = package
    shared = tmp_path / 'shared-assets'
    shared.mkdir()
    public.mkdir()
    namespace = public / 'local-teaching'
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(namespace), str(shared)], check=True, capture_output=True)
    else:
        namespace.symlink_to(shared, target_is_directory=True)
    report = install(manifest, source, public, ['pilot-v001'], apply=True)
    assert report['status'] == 'installed_verified'
    assert digest(shared / 'model.glb') == manifest['models'][0]['model_sha256']
    # A nested escape is still refused; only the configured top namespace is trusted.
    manifest['models'][0]['files'][0]['url'] = '/local-teaching/../escape.glb'
    with pytest.raises(ValueError, match='path'):
        install(manifest, source, public, ['pilot-v001'], apply=True)
