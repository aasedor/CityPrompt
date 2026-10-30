import hashlib
import json

import pytest

from tools.claude_bridge_corrections import register_local


def test_registration_rejects_a_hero_from_another_bridge_before_writing(tmp_path, monkeypatch):
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    (candidate / 'review').mkdir()
    model = candidate / 'test.glb'
    model.write_bytes(b'fixed model fixture')
    sha = hashlib.sha256(model.read_bytes()).hexdigest()
    (candidate / 'build-report.json').write_text(json.dumps({
        'candidate': 'clay-timber-covered-footbridge-clay-v004',
        'runtime': {'path': model.name, 'sha256': sha},
    }))
    (candidate / 'review/independent-review.json').write_text(json.dumps({
        'candidate': 'clay-timber-covered-footbridge-clay-v004',
        'holistic_review_performed': True, 'category_closure_only': False,
        'model_sha256': sha, 'architectural_clay_pass': True, 'unresolved_p0': 0, 'unresolved_p1': 0,
    }))
    (candidate / 'source-entry.json').write_text(json.dumps({
        'source_archetype': 'urban_pedestrian_footbridge/variant_2',
        'sources': [{'sha256': '0' * 64, 'original_path': '/locked/variant_2.png'}],
    }))
    hero = tmp_path / 'frontend/public/wrong-bridge.png'
    hero.parent.mkdir(parents=True)
    hero.write_bytes(b'a different bridge photograph')
    monkeypatch.setattr(register_local, 'ROOT', tmp_path)
    monkeypatch.setattr('sys.argv', ['register_local', '--candidate', str(candidate),
        '--archetype', 'urban_pedestrian_footbridge', '--variant', 'urban_pedestrian_footbridge_v2',
        '--title', 'Timber Covered Footbridge', '--hero', '/wrong-bridge.png'])
    with pytest.raises(ValueError, match='locked source'):
        register_local.main()
    assert not (tmp_path / 'frontend/public/street-kits').exists()


@pytest.mark.parametrize('field,value', [
    ('holistic_review_performed', False),
    ('category_closure_only', True),
    ('candidate', 'clay-a-different-bridge-clay-v004'),
])
def test_registration_rejects_scoped_or_mismatched_review_before_writing(tmp_path, monkeypatch, field, value):
    candidate = tmp_path / 'candidate'
    (candidate / 'review').mkdir(parents=True)
    model = candidate / 'test.glb'
    model.write_bytes(b'fixed model fixture')
    sha = hashlib.sha256(model.read_bytes()).hexdigest()
    (candidate / 'build-report.json').write_text(json.dumps({
        'candidate': 'clay-timber-covered-footbridge-clay-v004',
        'runtime': {'path': model.name, 'sha256': sha},
    }))
    review = dict(candidate='clay-timber-covered-footbridge-clay-v004', model_sha256=sha,
                  holistic_review_performed=True, category_closure_only=False,
                  architectural_clay_pass=True, unresolved_p0=0, unresolved_p1=0)
    review[field] = value
    (candidate / 'review/independent-review.json').write_text(json.dumps(review))
    monkeypatch.setattr(register_local, 'ROOT', tmp_path)
    monkeypatch.setattr('sys.argv', ['register_local', '--candidate', str(candidate),
        '--archetype', 'urban_pedestrian_footbridge', '--variant', 'urban_pedestrian_footbridge_v2',
        '--title', 'Timber Covered Footbridge', '--hero', '/front.png'])
    with pytest.raises(ValueError, match='holistic'):
        register_local.main()
    assert not (tmp_path / 'frontend').exists()
