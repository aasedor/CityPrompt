"""Delivery bytes are portable and match the runtime/source identity locks."""
import shutil
import pytest
from scripts.elevated_rail import inspect, SEED, ID

def test_seed_closes_all_native_module_dependencies():
    row,files,recipe=inspect(SEED,seed=True)
    assert row['id']==ID
    assert len(row['modules'])==10
    assert recipe['triangles']==294073
    assert set(files)=={kind+'.glb' for kind in row['modules']}|{'reference.png'}
    assert row['thumbnailUrl']=='/archetypes/streets/elevated-garden-rail/variant_0.png'

def test_changed_seed_module_is_rejected(tmp_path):
    shutil.copytree(SEED,tmp_path/'seed')
    target=tmp_path/'seed/rail_pier.glb'
    target.write_bytes(target.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='module changed'):inspect(tmp_path/'seed',seed=True)
