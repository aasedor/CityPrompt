"""The generator still rebuilds the registered stormwater pond, and its geometry checks pass."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = ROOT / 'seed/classroom-parks/stormwater-pond-v002'


def load(name):
    spec = importlib.util.spec_from_file_location(f'stormwater_pond_{name}', HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rebuilds_the_registered_assembly_byte_for_byte(tmp_path):
    build = load('build')
    build.main(['--output', str(tmp_path / 'pond')])
    recipe = json.loads((tmp_path / 'pond/recipe.json').read_text(encoding='utf-8'))
    seeded = json.loads((SEED / 'recipe.json').read_text(encoding='utf-8'))
    assert recipe['assembly']['sha256'] == seeded['assembly']['sha256']
    assert recipe == seeded, 'recipe drift: build a new candidate version'
    registry = json.loads((ROOT / 'frontend/src/data/nativeParks.json').read_text(encoding='utf-8'))
    layout = next(p for p in registry['layouts'] if p['variantId'] == build.PARK_ID)
    assert layout['assets']['assembly']['sha256'] == recipe['assembly']['sha256']
    assert layout['status'] == 'pilot' and layout['runtimeStatus'] == 'not_tested'
    assert layout['walkSurfaceMaterials'] == ['paving', 'grass', 'deck']


def test_geometry_checks_pass_on_the_registered_package(tmp_path):
    verify = load('verify')
    package = tmp_path / 'package'
    package.mkdir()
    for name in ('recipe.json', 'assembly-preview.glb'):
        data = (SEED / name).read_bytes()
        assert not data.startswith(b'version https://git-lfs'), f'hydrate {name} with git lfs'
        shutil.copyfile(SEED / name, package / name)
    report = verify.main(package)
    assert report['status'] == 'PASS_OFFLINE_GEOMETRY', report['failures']
    seeded = json.loads((SEED / 'geometry-verification.json').read_text(encoding='utf-8'))
    assert seeded['status'] == 'PASS_OFFLINE_GEOMETRY' and seeded['model_sha256'] == hashlib.sha256((SEED / 'assembly-preview.glb').read_bytes()).hexdigest()
