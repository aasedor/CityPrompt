import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.api.v1 import project_details as endpoint

PAVING = {'id':'paving-1', 'material':'concrete', 'coordinates':[
    [-114.1,51.05],[-114.0998,51.05],[-114.0998,51.0502],[-114.1,51.0502]]}

SITE_DETAIL_IDS = tuple(f'detail-site-{slug}' for slug in (
    'outdoor-stairs', 'accessible-ramp', 'modular-handrail', 'retaining-wall',
    'refuge-island', 'planted-curb-extension', 'tactile-curb-ramp',
    'covered-bike-parking', 'bicycle-locker', 'ev-charger', 'accessible-parking',
    'loading-zone', 'waste-enclosure', 'privacy-screen', 'public-art',
    'food-truck', 'cafe-barrier', 'community-noticeboard', 'rainwater-cistern',
    'public-washroom',
))

@pytest.mark.asyncio
async def test_paving_round_trip_and_old_clients_preserve_surfaces(monkeypatch):
    monkeypatch.setattr(endpoint, 'check_project_permission', AsyncMock(return_value='editor'))
    db, row = session({'keep':'unchanged'})
    saved = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=0, benches=[], surfaces=[PAVING]), SimpleNamespace(), db)
    assert saved['surfaces'] == [PAVING]
    assert row.metadata_['keep'] == 'unchanged'
    loaded = await endpoint.get_details(uuid.uuid4(), SimpleNamespace(), db)
    assert loaded['surfaces'] == [PAVING]
    legacy = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=1, benches=[]), SimpleNamespace(), db)
    assert legacy['surfaces'] == [PAVING]
    cleared = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=2, benches=[], surfaces=[]), SimpleNamespace(), db)
    assert cleared['surfaces'] == []

@pytest.mark.parametrize('patch', [
    {'material':'unknown'}, {'coordinates':[[0,0],[1,0]]},
    {'coordinates':[[0,0],[1,1],[0,1],[1,0]]},
    {'coordinates':[[0,0],[1,0],[2,0]]},
    {'coordinates':[[0,0],[181,0],[1,1]]},
    {'coordinates':[[0,0],[float('nan'),0],[1,1]]},
    {'coordinates':[[0,0],[1,0],[1,1],[0,1]]},
])
def test_rejects_invalid_paving(patch):
    with pytest.raises(ValidationError):
        endpoint.DetailUpdate(expected_revision=0, benches=[], surfaces=[{**PAVING, **patch}])


def session(metadata=None):
    row = SimpleNamespace(metadata_=metadata or {})
    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    db = AsyncMock()
    db.execute.return_value = result
    return db, row


@pytest.mark.asyncio
async def test_independent_benches_save_without_any_zone_and_preserve_metadata(monkeypatch):
    permission = AsyncMock(return_value='editor')
    monkeypatch.setattr(endpoint, 'check_project_permission', permission)
    db, row = session({'address': 'Riley', 'other': {'keep': True}})
    request = endpoint.DetailUpdate(expected_revision=0, benches=[{'id':'bench-1','lng':-114.1,'lat':51.05,'angle':30}])
    saved = await endpoint.save_details(uuid.uuid4(), request, SimpleNamespace(), db)
    assert saved['revision'] == 1 and len(saved['benches']) == 1
    assert row.metadata_['address'] == 'Riley' and row.metadata_['other'] == {'keep': True}
    assert permission.await_args.kwargs['required'] == 'editor'
    loaded = await endpoint.get_details(uuid.uuid4(), SimpleNamespace(), db)
    assert loaded['benches'] == saved['benches']
    assert permission.await_args.kwargs['required'] == 'viewer'
    cleared = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=1,benches=[]),SimpleNamespace(),db)
    assert cleared['benches'] == [] and cleared['revision'] == 2


@pytest.mark.asyncio
async def test_stale_save_does_not_overwrite_and_forbidden_user_cannot_write(monkeypatch):
    permission = AsyncMock(return_value='editor')
    monkeypatch.setattr(endpoint, 'check_project_permission', permission)
    db, row = session({'scene_details':{'version':1,'revision':3,'benches':[]}})
    with pytest.raises(HTTPException) as error:
        await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=1,benches=[]),SimpleNamespace(),db)
    assert error.value.status_code == 409 and row.metadata_['scene_details']['revision'] == 3
    db.flush.assert_not_awaited()
    permission.side_effect = HTTPException(403,'Forbidden')
    with pytest.raises(HTTPException) as error:
        await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=3,benches=[]),SimpleNamespace(),db)
    assert error.value.status_code == 403


def test_invalid_coordinates_duplicate_ids_and_excessive_items_rejected():
    for benches in ([{'id':'a','lng':181,'lat':51,'angle':0}],
                    [{'id':'a','lng':0,'lat':float('nan'),'angle':0}],
                    [{'id':'a','lng':0,'lat':51,'angle':0}]*2,
                    [{'id':str(i),'lng':0,'lat':51,'angle':0} for i in range(257)]):
        with pytest.raises(ValidationError):
            endpoint.DetailUpdate(expected_revision=0,benches=benches)

@pytest.mark.asyncio
async def test_trees_round_trip_legacy_writes_preserve_and_explicit_empty_removes(monkeypatch):
    monkeypatch.setattr(endpoint, 'check_project_permission', AsyncMock(return_value='editor'))
    db, row = session()
    tree = {'id':'tree-1','lng':-114.1,'lat':51.05,'angle':15,'variant':'oak-1'}
    saved = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=0, benches=[], trees=[tree]), SimpleNamespace(), db)
    assert saved['trees'] == [tree]
    legacy = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=1, benches=[]), SimpleNamespace(), db)
    assert legacy['trees'] == [tree]
    cleared = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=2, benches=[], trees=[]), SimpleNamespace(), db)
    assert cleared['trees'] == []

def test_tree_validation_rejects_unknown_assets_and_shared_ids():
    tree = {'id':'same','lng':-114.1,'lat':51.05,'angle':0,'variant':'oak-0'}
    with pytest.raises(ValidationError):
        endpoint.DetailUpdate(expected_revision=0, benches=[], trees=[{**tree,'variant':'arbitrary-url'}])
    with pytest.raises(ValidationError):
        endpoint.DetailUpdate(expected_revision=0, benches=[{k:v for k,v in tree.items() if k!='variant'}], trees=[tree])

@pytest.mark.asyncio
async def test_catalogue_objects_preserve_legacy_details_and_support_explicit_removal(monkeypatch):
    monkeypatch.setattr(endpoint, 'check_project_permission', AsyncMock(return_value='editor'))
    db, row = session()
    prop = {'id':'prop-1','lng':-114.1,'lat':51.05,'angle':15,'variant':'picnic-table-accessible'}
    saved = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=0, benches=[], props=[prop]), SimpleNamespace(), db)
    assert saved['props'] == [prop]
    legacy = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=1, benches=[], trees=[]), SimpleNamespace(), db)
    assert legacy['props'] == [prop]
    cleared = await endpoint.save_details(uuid.uuid4(), endpoint.DetailUpdate(expected_revision=2, benches=[], props=[]), SimpleNamespace(), db)
    assert cleared['props'] == []

def test_catalogue_rejects_unknown_models_bad_coordinates_and_colliding_ids():
    prop={'id':'prop','lng':-114.1,'lat':51.05,'angle':0,'variant':'dual-stream-bin'}
    for bad in ({**prop,'variant':'https://untrusted/model.glb'}, {**prop,'lat':float('nan')}):
        with pytest.raises(ValidationError):
            endpoint.DetailUpdate(expected_revision=0,benches=[],props=[bad])
    with pytest.raises(ValidationError):
        endpoint.DetailUpdate(expected_revision=0,benches=[{k:v for k,v in prop.items() if k!='variant'}],props=[prop])


def test_expanded_catalogue_accepts_existing_kit_parts_and_matches_frontend():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    choices = json.loads((root / 'frontend/src/features/parks/detailCatalogueExtras.json').read_text())
    assert len(choices) == 155
    assert set(endpoint._DETAIL_MODELS['trees']) == {'oak-0','oak-1','oak-2'} | {c['id'] for c in choices if c['kind'] == 'tree'}
    assert set(endpoint._DETAIL_MODELS['props']) == {'picnic-table-accessible','dual-stream-bin','bike-rack-three-stall','drinking-fountain-accessible','boulders','split-rail'} | {c['id'] for c in choices if c['kind'] == 'object'}
    for choice in choices:
        field = 'trees' if choice['kind'] == 'tree' else 'props'
        request = endpoint.DetailUpdate(expected_revision=0, benches=[], **{field: [{
            'id': 'trial', 'lng': -114.1, 'lat': 51.05, 'angle': 15, 'variant': choice['id']
        }]})
        assert getattr(request, field)[0].variant == choice['id']


@pytest.mark.asyncio
@pytest.mark.parametrize('variant', SITE_DETAIL_IDS)
async def test_site_details_save_reload_rotate_and_preserve_project_metadata(monkeypatch, variant):
    monkeypatch.setattr(endpoint, 'check_project_permission', AsyncMock(return_value='editor'))
    metadata = {'address': 'Riley', 'other': {'keep': True}}
    db, row = session(metadata.copy())
    project_id = uuid.uuid4()
    prop = {'id': 'site-prop', 'lng': -114.1, 'lat': 51.05, 'angle': 45, 'variant': variant}
    saved = await endpoint.save_details(project_id, endpoint.DetailUpdate(
        expected_revision=0, benches=[], props=[prop]), SimpleNamespace(), db)
    assert saved['props'] == [prop]
    assert saved['revision'] == 1
    rotated = {**prop, 'angle': -90}
    await endpoint.save_details(project_id, endpoint.DetailUpdate(
        expected_revision=1, benches=[], props=[rotated]), SimpleNamespace(), db)
    loaded = await endpoint.get_details(project_id, SimpleNamespace(), db)
    assert loaded['props'] == [rotated]
    assert loaded['revision'] == 2
    assert {key: row.metadata_[key] for key in metadata} == metadata
    legacy = await endpoint.save_details(project_id, endpoint.DetailUpdate(
        expected_revision=2, benches=[]), SimpleNamespace(), db)
    assert legacy['props'] == [rotated]


@pytest.mark.parametrize('patch', [
    {'variant': 'detail-site-unknown'}, {'variant': '/untrusted/model.glb'},
    {'angle': 361}, {'angle': -361}, {'angle': float('nan')},
])
def test_site_details_reject_unknown_models_and_invalid_rotation(patch):
    prop = {'id': 'site-prop', 'lng': -114.1, 'lat': 51.05, 'angle': 0,
            'variant': 'detail-site-outdoor-stairs'}
    with pytest.raises(ValidationError):
        endpoint.DetailUpdate(expected_revision=0, benches=[], props=[{**prop, **patch}])


def test_site_objects_cannot_be_saved_as_trees():
    with pytest.raises(ValidationError, match='Unknown tree model'):
        endpoint.DetailUpdate(expected_revision=0, benches=[], trees=[{
            'id': 'site-prop', 'lng': -114.1, 'lat': 51.05, 'angle': 0,
            'variant': 'detail-site-outdoor-stairs',
        }])


def test_traffic_details_ship_real_hash_locked_models():
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    choices = json.loads((root / 'frontend/src/features/parks/detailCatalogueExtras.json').read_text())
    traffic = [c for c in choices if c['sourceKit'] == 'traffic-safety-v1']
    assert len(traffic) == 10
    assert sum(c['bytes'] for c in traffic) < 300_000
    for model in traffic:
        data = (root / 'frontend/public' / model['url'].lstrip('/')).read_bytes()
        assert data[:4] == b'glTF', model['id']
        assert hashlib.sha256(data).hexdigest() == model['sha256']
        assert len(data) == model['bytes']
        assert model['triangles'] < 10_000 and model['meshes'] <= 6
