import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from geoalchemy2.elements import WKTElement

from app.models.models import Building
from app.services import user_generated_models as models


def source(**changes):
    values = dict(id=uuid.uuid4(), project_id=uuid.uuid4(), name='My house', generation_engine='meshy',
        generation_status='completed', model_url='/api/v1/files/projects/p/models/a.glb', specifications={'photo_generation': {'status': 'completed', 'source_keys': ['private-photo']}},
        height_meters=7.5, floor_count=2, floor_height_meters=3.75, preview_url=None)
    return Building(**{**values, **changes})


def test_discovery_excludes_reviewed_catalogue_and_repeated_placements():
    assert models.is_user_generated(source())
    assert not models.is_user_generated(source(generation_engine='rlasm', specifications={'rlasm': {'source_locked': True}}))
    assert not models.is_user_generated(source(specifications={'user_generated_model': {'catalogue_entry': False}}))
    assert models.is_user_generated(source(specifications={'user_generated_model': {'catalogue_entry': True}}))


def test_private_reference_list_never_returns_original_upload_keys():
    entry = models.generated_entry(source())
    assert 'private-photo' not in str(entry)


def test_generated_entry_provides_model_and_original_plot_size():
    # Roughly 12 m east-west by 16 m north-south near Calgary.
    footprint = WKTElement('POLYGON((-114 51, -113.9998287 51, -113.9998287 51.0001437, -114 51.0001437, -114 51))', srid=4326)
    original = source(footprint=footprint)
    entry = models.generated_entry(original)
    assert entry['model_url'] == original.model_url
    assert entry['size_estimated'] is False
    assert entry['width_m'] == pytest.approx(12, abs=0.2)
    assert entry['depth_m'] == pytest.approx(16, abs=0.2)


def test_generated_entry_falls_back_when_original_plot_is_unavailable():
    entry = models.generated_entry(source(footprint=None))
    assert (entry['width_m'], entry['depth_m'], entry['size_estimated']) == (12, 16, True)


@pytest.mark.asyncio
async def test_reuse_copies_private_model_into_target_project_without_source_photos(monkeypatch):
    original = source()
    result = MagicMock(); result.scalar_one_or_none.return_value = original
    db = SimpleNamespace(execute=AsyncMock(return_value=result), add=MagicMock(), flush=AsyncMock())
    zone = SimpleNamespace(zone_type='building', project_id=uuid.uuid4(), geometry='footprint', properties={})
    user = SimpleNamespace(id=uuid.uuid4())
    monkeypatch.setattr(models, 'copy_generated_file', lambda url, key: f'/api/v1/files/{key}')
    placed = await models.attach_generated_model(db, zone, user, str(original.id))
    assert placed.project_id == zone.project_id
    assert placed.footprint == zone.geometry
    assert str(zone.project_id) in placed.model_url
    assert placed.model_url != original.model_url
    assert 'photo_generation' not in placed.specifications
    assert models.has_user_generated_binding(zone, placed)
    params = db.execute.call_args.args[0].compile().params
    assert user.id in params.values()  # Source query is scoped to the requesting owner.
    placed.model_url = 'replacement.glb'
    assert not models.has_user_generated_binding(zone, placed)


@pytest.mark.asyncio
async def test_missing_or_other_account_model_never_copies(monkeypatch):
    result = MagicMock(); result.scalar_one_or_none.return_value = None
    db = SimpleNamespace(execute=AsyncMock(return_value=result), add=MagicMock())
    copy = MagicMock(); monkeypatch.setattr(models, 'copy_generated_file', copy)
    with pytest.raises(HTTPException) as exc:
        await models.attach_generated_model(db, SimpleNamespace(zone_type='building'), SimpleNamespace(id=uuid.uuid4()), str(uuid.uuid4()))
    assert exc.value.status_code == 404
    copy.assert_not_called(); db.add.assert_not_called()


@pytest.mark.asyncio
async def test_incomplete_model_cannot_be_placed(monkeypatch):
    result = MagicMock(); result.scalar_one_or_none.return_value = source(generation_status='generating')
    db = SimpleNamespace(execute=AsyncMock(return_value=result), add=MagicMock())
    copy = MagicMock(); monkeypatch.setattr(models, 'copy_generated_file', copy)
    with pytest.raises(HTTPException) as exc:
        await models.attach_generated_model(db, SimpleNamespace(zone_type='building'), SimpleNamespace(id=uuid.uuid4()), str(uuid.uuid4()))
    assert exc.value.status_code == 409
    copy.assert_not_called()


@pytest.mark.asyncio
async def test_generated_zone_refreshes_updated_timestamp_before_history(mock_db, test_user, monkeypatch):
    from app.api.v1 import site_zones, lego_assembly
    from app.schemas.schemas import SiteZoneCreate
    from tests.conftest import FakeProject

    project = FakeProject(owner_id=test_user.id)
    project_result = MagicMock(); project_result.scalar_one_or_none.return_value = project
    mock_db.execute.return_value = project_result
    monkeypatch.setattr(site_zones, 'lock_residual_landscape_project', AsyncMock())
    monkeypatch.setattr(site_zones, '_active_site_boundary', AsyncMock(return_value=None))
    monkeypatch.setattr(site_zones, '_invalidate_residual_landscape', AsyncMock())
    expired = False

    async def attach(*args):
        nonlocal expired
        expired = True  # The row update expires its server-generated updated_at.
        return source()

    async def refresh(*args):
        nonlocal expired
        expired = False

    async def history(*args):
        assert not expired, 'History must not trigger async lazy loading of updated_at'

    monkeypatch.setattr(models, 'attach_generated_model', attach)
    monkeypatch.setattr(lego_assembly, '_stamp_community_3d', lambda *args, **kwargs: None)
    monkeypatch.setattr(site_zones, '_record_zone_history', history)
    monkeypatch.setattr(site_zones, '_zone_to_response', lambda zone: {'name': zone.name})
    mock_db.refresh.side_effect = refresh
    payload = SiteZoneCreate(zone_type='building', coordinates=[[-114, 51], [-113.999, 51],
        [-113.999, 51.001], [-114, 51.001]], properties={'user_generated_source_id': str(uuid.uuid4())})
    await site_zones.create_zone(project.id, payload, SimpleNamespace(headers={}), test_user, mock_db)
    mock_db.commit.assert_awaited_once()
