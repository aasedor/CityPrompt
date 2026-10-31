"""Authored-storey assemblies must preserve native bytes and complete floor heights."""
from pathlib import Path
import sys
import json
import copy
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_blue_native_uses_original_without_module_reconstruction():
    from scripts.regular_tower_storeys import assembly_plan
    assert assembly_plan('blue', 25) == [{'role': 'source', 'elevation_m': 0.0}]


def test_blue_short_and_tall_keep_podium_and_roof_and_repeat_whole_floors():
    from scripts.regular_tower_storeys import assembly_plan
    low = assembly_plan('blue', 15)
    high = assembly_plan('blue', 40)
    assert len(low) == 14
    assert low[0] == {'role': 'podium', 'elevation_m': 0.0}
    assert low[1] == {'role': 'floor', 'elevation_m': 15.0}
    assert low[-2] == {'role': 'floor', 'elevation_m': 53.5}
    assert low[-1] == {'role': 'roof', 'elevation_m': 57.0}
    assert high[-1] == {'role': 'roof', 'elevation_m': 144.5}
    assert not any('scale' in part for part in low + high)


@pytest.mark.parametrize('count', [0, 14, 41, 15.5, True])
def test_blue_rejects_unadvertised_or_fractional_counts(count):
    from scripts.regular_tower_storeys import assembly_plan
    with pytest.raises(ValueError):
        assembly_plan('blue', count)


def test_changed_source_cannot_start_a_derivation(tmp_path):
    from scripts.regular_tower_storeys import derive
    source = tmp_path / 'wrong.glb'
    source.write_bytes(b'wrong source')
    with pytest.raises(ValueError, match='source'):
        derive('blue', source, tmp_path / 'output')
    assert not (tmp_path / 'output').exists()


@pytest.fixture
def synthetic_program(tmp_path, monkeypatch):
    """Real GLB geometry makes an incorrect axis or accidental scaling observable."""
    import trimesh
    from scripts import regular_tower_storeys as module
    source = tmp_path / 'original.glb'
    source_mesh = trimesh.creation.box(extents=[32,99,30])
    source_mesh.apply_translation([2,49.5,15.5])
    source.write_bytes(source_mesh.export(file_type='glb'))
    spec = dict(module.CONTRACTS['blue'], sha256=module.digest(source))
    monkeypatch.setitem(module.CONTRACTS, 'blue', spec)
    rows = []
    for role, lower, upper, occupied in spec['bands']:
        mesh = trimesh.creation.box(extents=[32, upper-lower, 30])
        mesh.apply_translation([0, (upper-lower)/2, 0])
        path = tmp_path / (role+'.glb')
        path.write_bytes(mesh.export(file_type='glb'))
        rows.append(dict(role=role, path=path.name, source_vertical_band_m=[lower, upper],
            occupied_storeys=occupied, native_dimensions_m=[32,30,upper-lower],bytes=path.stat().st_size,sha256=module.digest(path)))
    program = dict(id=spec['program'],source=dict(path=str(source),sha256=spec['sha256']),modules=rows)
    (tmp_path/'program.json').write_text(json.dumps(program))
    return tmp_path


def test_real_glb_assembly_uses_y_up_translation_and_keeps_native_bytes(synthetic_program):
    import trimesh
    from scripts.regular_tower_storeys import assemble
    source = synthetic_program/'original.glb'
    native = assemble('blue', synthetic_program, 25)
    assert native.read_bytes() == source.read_bytes()
    low = trimesh.load(assemble('blue', synthetic_program, 15),force='scene',process=False)
    high = trimesh.load(assemble('blue', synthetic_program, 40),force='scene',process=False)
    assert low.bounds.tolist() == [[-16,0,-15],[16,64,15]]
    assert high.bounds.tolist() == [[-16,0,-15],[16,151.5,15]]


def test_module_tampering_and_existing_comparison_are_preserved(synthetic_program):
    from scripts.regular_tower_storeys import assemble,load_program
    target = assemble('blue',synthetic_program,15)
    before = target.read_bytes()
    with pytest.raises(ValueError,match='exists'):
        assemble('blue',synthetic_program,15)
    assert target.read_bytes() == before
    (synthetic_program/'floor.glb').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='bytes changed'):
        load_program('blue',synthetic_program)


def test_module_height_metadata_cannot_stretch_real_geometry(synthetic_program):
    from scripts.regular_tower_storeys import load_program
    path = synthetic_program/'program.json'
    program = json.loads(path.read_text())
    program['modules'][1]['native_dimensions_m'][2] = 7.0
    path.write_text(json.dumps(program))
    with pytest.raises(ValueError,match='dimensions'):
        load_program('blue',synthetic_program)


@pytest.mark.parametrize('tower,native,low,high,low_roof,high_roof',[
    ('plus15',17,10,35,46.85,138.1),
    ('slab',13,8,30,25.25,90.15),
])
def test_other_tower_plans_keep_full_lower_context_and_exact_native(tower,native,low,high,low_roof,high_roof):
    from scripts.regular_tower_storeys import assembly_plan
    assert assembly_plan(tower,native) == [{'role':'source','elevation_m':0.0}]
    assert assembly_plan(tower,low)[-1]['elevation_m'] == pytest.approx(low_roof)
    assert assembly_plan(tower,high)[-1]['elevation_m'] == pytest.approx(high_roof)
    with pytest.raises(ValueError):
        assembly_plan(tower,low-1)
    with pytest.raises(ValueError):
        assembly_plan(tower,high+1)


def test_install_refuses_unreviewed_outputs_before_opening_local_services(tmp_path):
    from scripts.regular_tower_storeys import synchronize
    with pytest.raises(ValueError,match='review'):
        synchronize('blue',tmp_path,apply=True)


def test_review_must_bind_current_programme_bytes(synthetic_program):
    from scripts.regular_tower_storeys import validate_review,digest
    path = synthetic_program/'independent-programme-review.json'
    row=dict(candidate='blue-glass-office-storey-program-v001',decision='PASS_SCOPED_ARCHITECTURAL_CLAY_DERIVATIVE',
        reviewer='/root/independent_tower_reviewer',scope='Independent architectural-clay review of the complete authored storey derivative programme.',
        result_class='category_closure_only',unresolved_p0=0,unresolved_p1=0,reviewed_programme_sha256='wrong')
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='review'):
        validate_review('blue',synthetic_program)
    row['reviewed_programme_sha256']=digest(synthetic_program/'program.json')
    path.write_text(json.dumps(row))
    assert validate_review('blue',synthetic_program)['candidate']=='blue-glass-office-storey-program-v001'


def test_all_roles_share_original_whole_model_origin_not_module_centres(synthetic_program):
    from scripts.regular_tower_storeys import load_program
    _,rows=load_program('blue',synthetic_program)
    assert [r['metadata']['lego']['placement_contract']['source_frame_origin_xy_m'] for r in rows] == [[2.0,15.5]]*3


@pytest.mark.parametrize('changed', ['owner','public','url','source','metadata'])
def test_source_origin_migration_refuses_any_unrelated_row_change(synthetic_program,changed):
    from scripts.regular_tower_storeys import load_program,origin_migration_metadata
    _,rows=load_program('blue',synthetic_program)
    new=rows[0];old=copy.deepcopy(new)
    del old['metadata']['lego']['placement_contract']['source_frame_origin_xy_m']
    current=dict(id=old['id'],owner_id='task-owner',is_public=False,model_url=old['model_url'],metadata=copy.deepcopy(old['metadata']))
    if changed=='owner':current['owner_id']='someone-else'
    if changed=='public':current['is_public']=True
    if changed=='url':current['model_url']='/someone-else.glb'
    if changed=='source':current['metadata']['rlasm']['source_model_sha256']='changed'
    if changed=='metadata':current['metadata']['lego']['height_m']=900
    with pytest.raises(ValueError,match='preserv'):
        origin_migration_metadata(current,old,new,'task-owner')


def test_source_origin_migration_only_adds_origin_and_is_idempotent(synthetic_program):
    from scripts.regular_tower_storeys import load_program,origin_migration_metadata
    _,rows=load_program('blue',synthetic_program)
    new=rows[0];old=copy.deepcopy(new)
    del old['metadata']['lego']['placement_contract']['source_frame_origin_xy_m']
    current=dict(id=old['id'],owner_id='task-owner',is_public=False,model_url=old['model_url'],metadata=copy.deepcopy(old['metadata']))
    migrated=origin_migration_metadata(current,old,new,'task-owner')
    assert migrated['lego']['placement_contract']['source_frame_origin_xy_m']==[2.0,15.5]
    current['metadata']=migrated
    assert origin_migration_metadata(current,old,new,'task-owner')==migrated


@pytest.mark.parametrize('change',[
    {'reviewer':None},{'reviewer':''},{'reviewer':'/root/regular_tower_options (builder)'},
    {'scope':None},{'scope':'clay'},{'result_class':None},{'result_class':'keeper_approved'},
    {'unresolved_p0':False},{'unresolved_p1':False},
])
def test_review_requires_independent_identity_scope_category_and_integer_counters(synthetic_program,change):
    from scripts.regular_tower_storeys import validate_review,digest
    row=dict(candidate='blue-glass-office-storey-program-v001',decision='PASS_SCOPED_ARCHITECTURAL_CLAY_DERIVATIVE',
        reviewer='/root/independent_tower_reviewer',scope='Independent architectural-clay review of the complete authored storey derivative programme.',
        result_class='category_closure_only',unresolved_p0=0,unresolved_p1=0,
        reviewed_programme_sha256=digest(synthetic_program/'program.json'))
    row.update(change)
    (synthetic_program/'independent-programme-review.json').write_text(json.dumps(row))
    with pytest.raises(ValueError,match='review'):
        validate_review('blue',synthetic_program)


@pytest.mark.parametrize('change',[
    {'name':'unrelated'},{'category':'park'},{'generation_engine':'generic'},
    {'lod_urls':{'0':'/other.glb'}},{'tags':['public']},
])
def test_complete_existing_row_match_rejects_binding_drift(synthetic_program,change):
    from scripts.regular_tower_storeys import load_program,existing_row_matches
    _,rows=load_program('blue',synthetic_program);row=rows[0]
    existing=SimpleNamespace(owner_id='task-owner',is_public=False,name=row['name'],category='building',
        generation_engine='rlasm',model_url=row['model_url'],lod_urls={'0':row['model_url']},
        tags=['local-student-review',row['variantId']],metadata_=copy.deepcopy(row['metadata']))
    assert existing_row_matches(existing,row,'task-owner')
    for key,value in change.items():setattr(existing,key,value)
    assert not existing_row_matches(existing,row,'task-owner')


def test_origin_migration_field_drift_causes_no_mutation_or_commit(synthetic_program,monkeypatch):
    """A late full-row mismatch must not commit earlier prepared metadata."""
    import uuid
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'backend'))
    from app.core import config
    from app.models.models import User
    from app.services import render_attempt_storage
    import sqlalchemy
    import sqlalchemy.orm
    from scripts import classroom_model_library
    from scripts.regular_tower_storeys import load_program,migrate_blue_source_origin,digest
    _,new_rows=load_program('blue',synthetic_program)
    old_rows=copy.deepcopy(new_rows)
    for row in old_rows:del row['metadata']['lego']['placement_contract']['source_frame_origin_xy_m']
    receipt=synthetic_program/'original-bindings.json';receipt.write_text(json.dumps({'blue':old_rows}))
    (synthetic_program/'local-install-verification.json').write_text(json.dumps([
        dict(id=r['id'],sha256=r['metadata']['rlasm']['model_sha256'],binding='verified',object='verified') for r in old_rows]))
    (synthetic_program/'independent-programme-review.json').write_text(json.dumps(dict(
        candidate='blue-glass-office-storey-program-v001',decision='PASS_SCOPED_ARCHITECTURAL_CLAY_DERIVATIVE',
        reviewer='/root/independent_tower_reviewer',scope='Independent architectural-clay review of complete authored building derivatives.',
        result_class='category_closure_only',unresolved_p0=0,unresolved_p1=0,
        reviewed_programme_sha256=digest(synthetic_program/'program.json'))))
    owner=uuid.uuid4()
    entries={uuid.UUID(r['id']):SimpleNamespace(id=uuid.UUID(r['id']),owner_id=owner,is_public=False,
        name=r['name'],category='building',generation_engine='rlasm',model_url=r['model_url'],
        lod_urls={'0':r['model_url']},tags=['local-student-review',r['variantId']],metadata_=copy.deepcopy(r['metadata'])) for r in old_rows}
    entries[uuid.UUID(old_rows[1]['id'])].name='drifted after original receipt'
    before={key:copy.deepcopy(vars(value)) for key,value in entries.items()}
    class BoundaryDatabase:
        commits=0
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def get(self,model,key,**kwargs):return SimpleNamespace(is_active=True) if model is User else entries.get(key)
        def commit(self):self.commits+=1
    database=BoundaryDatabase()
    monkeypatch.setattr(config,'get_settings',lambda:SimpleNamespace(database_url='postgresql://localhost/test',database_url_sync='postgresql://localhost/test',s3_endpoint_url='http://localhost:9000'))
    monkeypatch.setattr(sqlalchemy,'create_engine',lambda value:SimpleNamespace(dispose=lambda:None))
    monkeypatch.setattr(sqlalchemy.orm,'Session',lambda engine:database)
    monkeypatch.setattr(render_attempt_storage,'_client',lambda:(object(),'test'))
    monkeypatch.setattr(classroom_model_library,'object_matches',lambda *args:'verified')
    with pytest.raises(ValueError,match='preserv'):
        migrate_blue_source_origin(synthetic_program,receipt,owner)
    assert database.commits==0
    assert {key:vars(value) for key,value in entries.items()}==before
    assert not (synthetic_program/'source-origin-migration-preimage.json').exists()
