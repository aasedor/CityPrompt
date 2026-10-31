"""Landmarks use complete semantic schedules, never clipped/stretched meshes."""
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import landmark_tower_storeys as L


@pytest.mark.parametrize('count,offices,height', [(20, (9, 9), 79.7), (30, (14, 14), 113.7), (40, (20, 18), 147.7)])
def test_twist_complete_stacks_meet_fixed_lobby_garden_and_crown(count, offices, height):
    p = L.programme_for('twisted', count)
    assert p['occupied_storeys'] == count == sum(offices) + 2
    lower, upper = p['stacks']
    assert (lower['floors'], upper['floors']) == offices
    assert lower['base_m'] == 10
    assert lower['top_m'] == pytest.approx(p['garden_base_m'])
    assert upper['base_m'] - lower['top_m'] == pytest.approx(4)
    assert upper['top_m'] == pytest.approx(p['crown_base_m'])
    assert p['height_m'] == pytest.approx(height)
    for stack in p['stacks']:
        assert stack['top_m'] - stack['base_m'] == pytest.approx(stack['floors'] * 3.4)
        assert stack['rotation_degrees'] == [-12, 12]
    assert p['height_m'] - p['crown_base_m'] == pytest.approx(4.5)
    assert p['vertical_scale'] == 1


@pytest.mark.parametrize('count,tiers,height', [(17, [2, 7, 4, 2, 2], 68.6), (25, [2, 11, 6, 3, 3], 95.8), (35, [2, 16, 9, 4, 4], 129.8)])
def test_terracotta_retains_every_occupied_setback_and_rigid_lantern(count, tiers, height):
    p = L.programme_for('gilded', count)
    assert [t['floors'] for t in p['tiers']] == tiers
    assert sum(tiers) == p['occupied_storeys'] == count
    assert p['height_m'] == pytest.approx(height)
    assert p['tiers'][0]['base_m'] == 0
    for a, b in zip(p['tiers'], p['tiers'][1:]):
        assert a['top_m'] == pytest.approx(b['base_m'])
        assert a['width_m'] > b['width_m']
        assert a['depth_m'] > b['depth_m']
    assert p['height_m'] - p['tiers'][-1]['top_m'] == pytest.approx(10.4)
    assert p['vertical_scale'] == 1


@pytest.mark.parametrize('family,count', [('twisted', 21), ('gilded', 30), ('unknown', 17), ('twisted', True)])
def test_rejects_unsupported_counts_and_wrong_family(family, count):
    with pytest.raises(ValueError):
        L.programme_for(family, count)


def test_native_path_uses_original_bytes_and_source_identity():
    for family in ('twisted', 'gilded'):
        spec = L.SOURCES[family]
        p = L.programme_for(family, spec['native_storeys'])
        assert p['native_exact_copy'] is True
        assert p['source_model_sha256'] == spec['model_sha256']
        assert p['source_variant_id'] == spec['variant_id']


def test_wrong_source_fails_before_adaptation(tmp_path):
    path = tmp_path / 'twisted.py'
    path.write_text('not the exact authored source')
    with pytest.raises(ValueError, match='source hash'):
        L.adapt_builder('twisted', 30, path)


def test_twist_reauthored_semantics_have_no_unmoved_native_datums():
    p = Path(L.SOURCES['twisted']['directory']) / 'scripts/twisted.py'
    if not p.exists():
        pytest.skip('External source unavailable')
    code = L.adapt_builder('twisted', 30, p)
    compile(code, str(p), 'exec')
    assert '[(10,20),(82,18)]' not in code
    assert 'z=78.35' not in code
    assert '143.2' not in code
    assert '143.45' not in code
    assert '147.7' not in code
    assert '.scale.z' not in code


def test_native_dry_run_validates_without_copying(tmp_path):
    source = Path(L.SOURCES['twisted']['directory'])
    if not source.exists():
        pytest.skip('External source unavailable')
    output = tmp_path / 'native'
    L.build_worker(SimpleNamespace(family='twisted', storeys=40, output=output, dry_run=True))
    assert not output.exists()


def test_terracotta_adaptation_preserves_entrance_and_moves_complete_crown():
    path = Path(L.SOURCES['gilded']['directory']) / 'scripts/tower.py'
    if not path.exists():
        pytest.skip('External source unavailable')
    source = path.read_text(encoding='utf-8')
    code = L.adapt_builder('gilded', 25, path)
    assert code.split('# Source front entrance hierarchy')[1] == source.split('# Source front entrance hierarchy')[1]
    assert "'z',85.42,86.2" in code  # Native58.22 seated base translated27.2m.
    assert '(0,0,95.8)' in code  # Native68.6 finial.
    assert '.scale.z' not in code


def test_private_native_binding_shares_programme_and_retains_exact_source_pin():
    p=L.programme_for('twisted',40)
    p.update(path='native.glb',sha256=L.SOURCES['twisted']['model_sha256'],bytes=1,
             native_dimensions_m=dict(width=43.49,depth=44.026,height=147.7))
    row=L.private_binding(p)
    assert row['is_public'] is False
    assert row['metadata']['rlasm']['candidate']=='glass-tower-twisted-clay-v005'
    lego=row['metadata']['lego']
    assert lego['native_floors']==lego['occupied_storeys']==lego['min_floors']==lego['max_floors']==40
    assert lego['role']=='assembled' and lego['repeatable_z'] is False
    assert lego['placement_contract']['storey_program_id']==p['id']
    assert lego['source_variant_id']==lego['generation_archetype_id']=='glass_tower_twisted'


def test_reference_resolution_uses_hashes_after_catalogue_filename_rename():
    import json
    spec=L.SOURCES['gilded']
    if not Path(spec['directory']).exists():
        pytest.skip('External source unavailable')
    library=json.loads((L.ROOT/'seed/model-library/rlasm-architectural-clay/library.json').read_text())
    item=next(e for e in library['entries'] if e['candidate']==spec['candidate'])
    sources=L.locked_sources(spec,item)
    assert {s['role'] for s in sources}=={'front','oblique','top'}
    assert Path(sources[0]['original_path']).name=='variant_0.png'
    assert Path(sources[0]['path']).name=='showcase-v1-front.png'
    for source in sources:
        assert L.sha256(Path(source['original_path']))==source['sha256']


def test_local_install_rejects_non_loopback_database_or_storage():
    L.validate_local_target('postgresql://user:password@127.0.0.1:5432/db','http://localhost:9000')
    for db,storage in [('postgresql://example.com/db','http://localhost:9000'),
                       ('postgresql://localhost/db','https://objects.example.com')]:
        with pytest.raises(ValueError,match='loopback'):
            L.validate_local_target(db,storage)


def test_review_gate_rejects_builder_wrong_hash_and_open_findings():
    contract=dict(sha256='a'*64)
    good=dict(model_sha256='a'*64,reviewer='/root/independent_reviewer',unresolved_p0=0,
              unresolved_p1=0,architectural_clay_pass=True,scope='complete authored height architectural clay')
    L.require_independent_review(good,contract)
    for updates in [dict(model_sha256='b'*64),dict(reviewer='/root/landmark_tower_options'),
                    dict(unresolved_p1=1),dict(architectural_clay_pass=False)]:
        with pytest.raises(ValueError,match='review'):
            L.require_independent_review(dict(good,**updates),contract)


def test_install_conflict_check_preserves_public_and_different_rows():
    row=dict(name='authored30',model_url='/api/v1/files/library/test.glb',
             variantId='glass_tower_twisted',metadata={'rlasm':{'model_sha256':'a'*64}})
    existing=SimpleNamespace(owner_id='owner',is_public=False,name=row['name'],category='building',
        generation_engine='rlasm',model_url=row['model_url'],lod_urls={'0':row['model_url']},
        tags=['local-student-review',row['variantId']],metadata_=row['metadata'])
    assert L.existing_row_matches(existing,row,'owner')
    for key,value in [('is_public',True),('owner_id','different'),('model_url','different'),('metadata_',{})]:
        changed=SimpleNamespace(**dict(existing.__dict__,**{key:value}))
        assert not L.existing_row_matches(changed,row,'owner')


def test_twisted_office_proof_camera_follows_occupied_stack_after_shortening():
    roster=[dict(name='glass_close',location=[11,-35,46],target=[3,-19,44]),
            dict(name='roof_contact',location=[47,-60,102],target=[0,0,75])]
    p=L.programme_for('twisted',20)
    revised=L.twisted_camera_roster(roster,p)
    assert p['stacks'][0]['base_m']<revised[0]['target'][2]<p['stacks'][0]['top_m']
    assert revised[0]['target'][2]==pytest.approx(25.3)
    assert revised[1]==roster[1]  # Crown framing stays on its translated datum.
    assert roster[0]['target'][2]==44  # Do not mutate preserved source roster.
    assert L.twisted_camera_roster(roster,L.programme_for('twisted',40))==roster


def test_lantern_panes_have_real_normal_thickness_without_moving_visible_face():
    import numpy as np
    face=[(-1.53,-3.695,86.2),(1.53,-3.695,86.2),(1.53,-3.695,91.3),(-1.53,-3.695,91.3)]
    vertices,faces=L.normal_surface_geometry(face,.025)
    assert vertices[:4]==face
    points=np.asarray(vertices,dtype=np.float32)
    assert points[4:,1]-points[:4,1]==pytest.approx([.025]*4,abs=1e-6)
    for polygon in faces:
        for i in range(1,len(polygon)-1):
            a,b,c=points[list((polygon[0],polygon[i],polygon[i+1]))]
            assert np.linalg.norm(np.cross(b-a,c-a))/2>1e-6


def test_verify_cli_fails_when_binding_or_storage_readback_is_missing(monkeypatch):
    monkeypatch.setattr(L,'synchronize_private',lambda *args,**kwargs:[dict(binding='missing',object='verified')])
    monkeypatch.setattr(sys,'argv',['landmark_tower_storeys.py','--family','twisted','--verify'])
    with pytest.raises(SystemExit) as failure:
        L.main()
    assert failure.value.code==1


def test_historical_native_review_keeps_its_structured_reviewer_identity():
    review=dict(model_sha256='a'*64,reviewer={'agent':'/root/showcase_market_review','role':'independent'},
                unresolved_p0=0,unresolved_p1=0,architectural_clay_pass=True,scope='Holistic native architectural-clay review')
    L.require_independent_review(review,{'sha256':'a'*64})
