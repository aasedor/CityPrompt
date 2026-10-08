import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.api.v1 import project_details as endpoint


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
