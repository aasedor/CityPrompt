"""A stale client must not persist a second overlapping catalogue building."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from fastapi import HTTPException
from shapely.geometry import box

from app.api.v1 import site_zones
from app.schemas.schemas import SiteZoneCreate
from tests.conftest import FakeProject


def result(value=None, rows=()):
    response = MagicMock()
    response.scalar_one_or_none.return_value = value
    response.scalars.return_value.all.return_value = list(rows)
    return response


@pytest.mark.asyncio
@pytest.mark.parametrize('overlap', [True, False])
async def test_new_catalogue_building_checks_saved_neighbours_before_insertion(
    mock_db, test_user, monkeypatch, overlap,
):
    project = FakeProject(owner_id=test_user.id)
    neighbour = SimpleNamespace(id=uuid.uuid4(), zone_type='building', name='Existing tower',
        properties={}, geometry=box(-114, 51, -113.9995, 51.0004))
    # Shared boundary edges are allowed; material overlap is not.
    left = -113.9998 if overlap else -113.9995
    payload = SiteZoneCreate(zone_type='building', client_request_id=uuid.uuid4(),
        coordinates=[[left,51],[-113.999,51],[-113.999,51.0004],[left,51.0004]],
        properties={'pick_place_asset':'clay_vancouver_balcony_podium_tower'})
    mock_db.execute.side_effect = [result(project), result(), result(rows=[neighbour])]
    lock = AsyncMock()
    monkeypatch.setattr(site_zones, 'lock_residual_landscape_project', lock)
    monkeypatch.setattr(site_zones, '_active_site_boundary', AsyncMock(return_value=None))
    monkeypatch.setattr(site_zones, '_invalidate_residual_landscape', AsyncMock())
    monkeypatch.setattr(site_zones, '_record_zone_history', AsyncMock())
    monkeypatch.setattr(site_zones, '_zone_to_response', lambda z: {'id':str(z.id)})
    if overlap:
        with pytest.raises(HTTPException) as failure:
            await site_zones.create_zone(project.id,payload,SimpleNamespace(headers={}),test_user,mock_db)
        assert failure.value.status_code == 422
        assert 'Existing tower' in failure.value.detail
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_awaited()
    else:
        await site_zones.create_zone(project.id,payload,SimpleNamespace(headers={}),test_user,mock_db)
        mock_db.commit.assert_awaited_once()
    lock.assert_awaited_once()


@pytest.mark.asyncio
async def test_saved_retry_returns_existing_building_before_overlap_check(mock_db,test_user,monkeypatch):
    project=FakeProject(owner_id=test_user.id)
    payload=SiteZoneCreate(zone_type='building',client_request_id=uuid.uuid4(),
        coordinates=[[-114,51],[-113.999,51],[-113.999,51.001]],
        properties={'pick_place_asset':'clay_vancouver_balcony_podium_tower'})
    existing=SimpleNamespace(properties={'_client_request_hash':site_zones._create_request_hash(payload)})
    mock_db.execute.side_effect=[result(project),result(existing)]
    monkeypatch.setattr(site_zones,'lock_residual_landscape_project',AsyncMock())
    monkeypatch.setattr(site_zones,'_zone_to_response',lambda z:{'id':'already-saved'})
    assert await site_zones.create_zone(project.id,payload,SimpleNamespace(headers={}),test_user,mock_db)=={'id':'already-saved'}
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_save_allows_reviewed_side_by_side_buildings_with_overlapping_plot_padding():
    from tests.test_building_placement_edges import zone
    from app.services.building_placement_edges import building_edge_contracts
    first = zone()
    first.name = None
    second = zone(x=building_edge_contracts()['validation_cast_iron_italianate']['nativeWidthM']+.02)
    db = SimpleNamespace(execute=AsyncMock(return_value=result(rows=[first])))
    await site_zones._assert_new_catalogue_building_clear(
        db,uuid.uuid4(),'building',second.geometry,second.properties)


@pytest.mark.asyncio
@pytest.mark.parametrize('properties', [{'_plan_role':'framework_height'},
    {'_imported_from':'Alternative A'},{'_plan_snapshot_id':'study'}])
async def test_save_does_not_treat_alternative_plan_or_height_guides_as_manual_buildings(properties):
    neighbour=SimpleNamespace(id='alternative',zone_type='building',name=None,
        geometry=box(-114,51,-113.999,51.001),properties=properties)
    db=SimpleNamespace(execute=AsyncMock(return_value=result(rows=[neighbour])))
    await site_zones._assert_new_catalogue_building_clear(db,uuid.uuid4(),'building',neighbour.geometry,
        {'pick_place_asset':'clay_vancouver_balcony_podium_tower'})
