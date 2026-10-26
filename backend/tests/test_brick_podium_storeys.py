import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts import brick_podium_storeys as pilot
from app.services.lego_assembly import AssemblyPlanningError, AssemblyRequest, descriptor_from_library_entry, plan_vertical_assembly


@pytest.fixture
def program(tmp_path, monkeypatch):
    source = tmp_path / 'source.glb'
    source.write_bytes(b'immutable-source-fixture')
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(pilot, 'SOURCE_HASH', source_hash)
    modules = []
    for role, lower, upper, storeys in pilot.BANDS:
        path = tmp_path / f'{role}.glb'
        path.write_bytes(role.encode())
        modules.append(dict(role=role, path=path.name, bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(), occupied_storeys=storeys,
            source_vertical_band_m=[lower, upper], native_dimensions_m=[54 if role=='podium' else 38, 44 if role=='podium' else 30, upper-lower]))
    manifest = dict(id=pilot.PROGRAM, source=dict(path=str(source), sha256=source_hash), modules=modules)
    (tmp_path/'program.json').write_text(json.dumps(manifest), encoding='utf-8')
    return tmp_path


@pytest.mark.parametrize(('storeys','height'), [(15,56.1), (25,86.1), (40,131.1)])
def test_brick_podium_keeps_one_complete_base_and_roof_while_repeating_full_floors(program, storeys, height):
    manifest, rows = pilot.load_program(program)
    descriptors = [descriptor_from_library_entry(SimpleNamespace(**{**row, 'metadata_':row['metadata']})) for row in rows]
    assert all(descriptors)
    plan = plan_vertical_assembly(descriptors, AssemblyRequest(54,44,storeys, archetype_id=pilot.VARIANT,
        model_revision=pilot.SOURCE), allow_forced_fit=False)
    roles = [instance['role'] for instance in plan['instances']]
    assert roles.count('podium') == roles.count('roof') == 1
    assert roles.count('floor') == storeys-3
    assert plan['assembled_height_m'] == pytest.approx(height)
    assert all(instance['scale'] == [1,1,1] for instance in plan['instances'])
    assert all(instance['position'][:2] == [0,0] for instance in plan['instances'])
    assert plan['fit']['delivery_format'] == 'architectural_clay_module_v1'
    assert all(row['metadata']['rlasm']['source_model_sha256']==manifest['source']['sha256'] for row in rows)


@pytest.mark.parametrize('storeys', [12,41])
def test_brick_program_refuses_out_of_range_storeys(program, storeys):
    _, rows = pilot.load_program(program)
    descriptors = [descriptor_from_library_entry(SimpleNamespace(**{**row, 'metadata_':row['metadata']})) for row in rows]
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(descriptors, AssemblyRequest(54,44,storeys, archetype_id=pilot.VARIANT), allow_forced_fit=False)


def test_brick_program_refuses_changed_module_bytes(program):
    (program/'floor.glb').write_bytes(b'changed')
    with pytest.raises(ValueError, match='Changed derived module'):
        pilot.load_program(program)


def test_brick_program_refuses_changed_source_datums(program):
    path=program/'program.json'
    manifest=json.loads(path.read_text())
    manifest['modules'][1]['source_vertical_band_m']=[15,18]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='band contract changed'):
        pilot.load_program(program)
