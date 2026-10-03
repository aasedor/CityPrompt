from pathlib import Path
import pytest

from scripts.elevated_rail_stations import SPECS, inspect

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('identity',SPECS)
def test_exact_seed_closure(identity):
    package=ROOT/'seed/classroom-streets'/SPECS[identity][2]
    row,files,recipe=inspect(package,identity,seed=True)
    assert row['id']==identity
    assert row['program']['adapter']=='elevated-station-v1'
    assert row['modules']['rail_station']['sha256']==recipe['modules']['rail_station']['sha256']
    assert files['rail_station.glb'][:4]==b'glTF'


def test_changed_station_module_is_rejected(tmp_path):
    identity='skytrain_elevated_corridor_v0'
    package=ROOT/'seed/classroom-streets'/SPECS[identity][2]
    from shutil import copytree
    tampered=tmp_path/'station';copytree(package,tampered)
    module=tampered/'rail_station.glb';module.write_bytes(module.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='Native module changed'):
        inspect(tampered,identity,seed=True)
