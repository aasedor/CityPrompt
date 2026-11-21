"""The park batch generator reproduces the registered parks byte for byte. Run: pytest tools/native_park_batch"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('native_park_batch_build', HERE / 'build.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
spec = importlib.util.spec_from_file_location('native_park_batch_verify', HERE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

PACKAGES = {'skate': 'prairie-bowl-skate-v006', 'fitness': 'parkour-yard-v004', 'memorial': 'walled-memorial-v004'}
# The skate park was registered before the shared kit grew for the other two parks. Its assembly
# still rebuilds byte for byte, but its recipe keeps the source hash of the kit it was built with:
# rewriting it would change the registered recipe hash and content revision.
KIT_BEFORE_BATCH = {'skate': '5c4a6527540095ff6f825cd6f66f7e26ece9bf23dcdd2d6b61a9bc4923d4dd17'}
BUILT = {park: batch.build(park) for park in PACKAGES}


def registry(side):
    path = ROOT / side / ('src/data/nativeParks.json' if side == 'frontend' else 'app/data/nativeParks.json')
    return {p['variantId']: p for p in json.loads(path.read_text(encoding='utf-8'))['layouts']}


@pytest.mark.parametrize('park', sorted(PACKAGES))
def test_rebuild_matches_the_registered_assembly_and_recipe(park):
    payload, recipe = BUILT[park]
    seed = json.loads((ROOT / 'seed/classroom-parks' / PACKAGES[park] / 'recipe.json').read_text(encoding='utf-8'))
    if park in KIT_BEFORE_BATCH:
        assert seed['generator_sha256'] == KIT_BEFORE_BATCH[park]
        recipe = {**recipe, 'generator_sha256': seed['generator_sha256']}
    assert recipe == seed
    sha = hashlib.sha256(payload).hexdigest()
    for side in ('frontend', 'backend'):
        layout = registry(side)[recipe['id']]
        assert layout['assets']['assembly']['sha256'] == sha
        assert layout['assets']['assembly']['url'] == f'/native-park-assets/{sha}.glb'
        assert (ROOT / layout['assets']['assembly']['archivePath']).stat().st_size == len(payload)
        assert (layout['widthM'], layout['depthM']) == tuple(recipe['dimensions_m'])
        assert (layout['status'], layout['runtimeStatus'], layout['terrainPolicy']) == ('pilot', 'not_tested', 'prepared_level')


def test_frontend_and_backend_registries_agree():
    front, back = registry('frontend'), registry('backend')
    for _, recipe in BUILT.values():
        assert front[recipe['id']] == back[recipe['id']]


@pytest.mark.parametrize('park', sorted(PACKAGES))
def test_offline_geometry_passes(park, tmp_path):
    payload, recipe = BUILT[park]
    (tmp_path / 'assembly-preview.glb').write_bytes(payload)
    (tmp_path / 'recipe.json').write_text(json.dumps(recipe), encoding='utf-8')
    report = verify.main(park, tmp_path)
    assert report['status'] == 'PASS_OFFLINE_GEOMETRY', report['failures']
    committed = json.loads((ROOT / 'seed/classroom-parks' / PACKAGES[park] / 'geometry-verification.json').read_text(encoding='utf-8'))
    assert committed == report


@pytest.mark.parametrize('park', sorted(PACKAGES))
def test_parks_stay_inside_their_budgets(park):
    _, recipe = BUILT[park]
    assert recipe['triangles'] <= 850_000
    assert recipe['assembly']['bytes'] <= 12_000_000
    assert recipe['runtime_approved'] is False
    module = batch.load(park)
    assert recipe['entrance']['y'] == -module.SITE_D / 2, 'one entrance on the south edge'
