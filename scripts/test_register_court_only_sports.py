import copy
import json
from pathlib import Path
import pytest
from register_court_only_sports import COURT_ONLY_KINDS, court_only_recipe, digest, encoded, register


def fixture(tmp_path):
    root = tmp_path/'repo'; packages = tmp_path/'packages'
    old = {'layouts':[{'id':'preserved-park','contentRevision':'unchanged'}], 'archivedLayouts':[]}
    for path in ('frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json'):
        p = root/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(encoded(old))
    for kind in COURT_ONLY_KINDS:
        package = packages/f'{kind}-v1'; (package/'renders').mkdir(parents=True)
        model = b'glTF'+kind.encode(); sha=digest(model)
        recipe = court_only_recipe(kind); recipe['assembly']={'sha256':sha}
        (package/'recipe.json').write_bytes(encoded(recipe))
        (package/'assembly-preview.glb').write_bytes(model)
        (package/'renders/aerial.png').write_bytes(b'\x89PNG\r\n\x1a\n'+kind.encode())
        (package/'geometry-verification.json').write_bytes(encoded(dict(
            status='PASS_OFFLINE_GEOMETRY',model_sha256=sha,bounds_m=[[-10,-18,0],[10,18,4]])))
    return root,packages,old


def snapshot(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_batch_validates_last_package_before_any_mutation(tmp_path):
    root,packages,_ = fixture(tmp_path); before=snapshot(root)
    (packages/'beach_volleyball-v1/assembly-preview.glb').write_bytes(b'glTFchanged')
    with pytest.raises(ValueError,match='Exact model verification'):
        register(packages,root)
    assert snapshot(root)==before


def test_register_preserves_old_bindings_is_idempotent_and_refuses_replacement(tmp_path):
    root,packages,old = fixture(tmp_path)
    register(packages,root)
    front=root/'frontend/src/data/nativeParks.json'
    assert front.read_bytes()==(root/'backend/app/data/nativeParks.json').read_bytes()
    assert json.loads(front.read_bytes())['layouts'][0]==old['layouts'][0]
    before=snapshot(root); register(packages,root); assert snapshot(root)==before
    target=root/'seed/classroom-parks/court-only-tennis-v001/assembly-preview.glb'
    target.write_bytes(b'preserved local edit'); before=snapshot(root)
    with pytest.raises(ValueError,match='Preserve existing court asset'):
        register(packages,root)
    assert snapshot(root)==before
