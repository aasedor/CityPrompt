import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1 import site_zones
from app.schemas.schemas import SiteZoneCreate, SiteZoneUpdate
from tests.conftest import FakeProject


def result(value):
    response = MagicMock()
    response.scalar_one_or_none.return_value = value
    return response


def create_payload(**overrides):
    return SiteZoneCreate(
        **{
            "zone_type": "green_space",
            "coordinates": [[-114, 51], [-113.99, 51], [-113.99, 51.01], [-114, 51.01]],
            "client_request_id": uuid.UUID(int=71),
            **overrides,
        }
    )


@pytest.mark.asyncio
async def test_create_retry_returns_saved_zone_before_boundary_or_side_effects(mock_db, test_user, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    payload = create_payload()
    saved = SimpleNamespace(
        properties={
            "_client_request_id": str(payload.client_request_id),
            "_client_request_hash": site_zones._create_request_hash(payload),
        }
    )
    mock_db.execute.side_effect = [result(project), result(saved)]
    lock = AsyncMock()
    history = AsyncMock()
    monkeypatch.setattr(site_zones, "lock_residual_landscape_project", lock)
    monkeypatch.setattr(site_zones, "_record_zone_history", history)
    monkeypatch.setattr(site_zones, "_zone_to_response", lambda zone: {"id": "saved-zone"})
    response = await site_zones.create_zone(project.id, payload, SimpleNamespace(headers={}), test_user, mock_db)
    assert response == {"id": "saved-zone"}
    lock.assert_awaited_once()
    mock_db.add.assert_not_called()
    history.assert_not_called()
    query = mock_db.execute.call_args_list[-1].args[0]
    assert project.id in query.compile().params.values()


@pytest.mark.asyncio
async def test_create_retry_with_changed_geometry_is_conflict(mock_db, test_user, monkeypatch):
    project = FakeProject(owner_id=test_user.id)
    payload = create_payload()
    saved = SimpleNamespace(properties={"_client_request_hash": site_zones._create_request_hash(payload)})
    changed = create_payload(coordinates=[[-114, 51], [-113.98, 51], [-113.98, 51.01], [-114, 51.01]])
    mock_db.execute.side_effect = [result(project), result(saved)]
    monkeypatch.setattr(site_zones, "lock_residual_landscape_project", AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await site_zones.create_zone(project.id, changed, SimpleNamespace(headers={}), test_user, mock_db)
    assert exc.value.status_code == 409
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["update", "delete"])
async def test_stale_update_and_delete_reject_after_lock_refresh(mock_db, test_user, monkeypatch, operation):
    now = datetime.now(timezone.utc)
    project = FakeProject(owner_id=test_user.id)
    zone = SimpleNamespace(id=uuid.uuid4(), project_id=project.id, updated_at=now)
    mock_db.execute.side_effect = [result(zone), result(project)]
    events = []

    async def lock(*args):
        events.append("lock")

    async def refresh(*args):
        events.append("refresh")
        zone.updated_at = now + timedelta(seconds=1)

    monkeypatch.setattr(site_zones, "lock_residual_landscape_project", lock)
    mock_db.refresh.side_effect = refresh
    with pytest.raises(HTTPException) as exc:
        if operation == "update":
            await site_zones.update_zone(
                zone.id,
                SiteZoneUpdate(name="stale", expected_updated_at=now),
                SimpleNamespace(headers={}),
                test_user,
                mock_db,
            )
        else:
            await site_zones.delete_zone(
                zone.id,
                SimpleNamespace(headers={}),
                test_user,
                mock_db,
                expected_updated_at=now,
            )
    assert exc.value.status_code == 409
    assert events == ["lock", "refresh"]
    mock_db.flush.assert_not_called()
    mock_db.delete.assert_not_called()
