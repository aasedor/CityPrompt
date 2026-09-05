import uuid
import asyncio
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


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["create", "update", "delete"])
@pytest.mark.parametrize("commit_fails", [False, True])
async def test_authored_save_waits_for_durable_commit(
    mock_db,
    test_user,
    monkeypatch,
    operation,
    commit_fails,
):
    """A successful HTTP result must be immediately visible to the next read.

    Yield dependency cleanup can run after the response on newer FastAPI.
    Hold the transaction open and ensure the route cannot announce success;
    a failed commit must still reach the request's error handler.
    """
    project = FakeProject(owner_id=test_user.id)
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Park",
        zone_type="green_space",
        properties={},
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.execute.side_effect = (
        [result(project), result(None)] if operation == "create" else [result(zone), result(project)]
    )
    monkeypatch.setattr(site_zones, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(site_zones, "_active_site_boundary", AsyncMock(return_value=None))
    monkeypatch.setattr(site_zones, "_invalidate_residual_landscape", AsyncMock())
    monkeypatch.setattr(site_zones, "_record_zone_history", AsyncMock())
    monkeypatch.setattr(
        site_zones, "_snapshot_from_zone", lambda z: {"zone_type": z.zone_type, "properties": z.properties}
    )
    monkeypatch.setattr(site_zones, "_zone_to_response", lambda z: {"id": str(z.id)})
    entered, release = asyncio.Event(), asyncio.Event()

    async def commit():
        entered.set()
        await release.wait()
        if commit_fails:
            raise RuntimeError("Database commit failed")

    mock_db.commit.side_effect = commit
    request = SimpleNamespace(headers={})
    if operation == "create":
        action = site_zones.create_zone(project.id, create_payload(), request, test_user, mock_db)
    elif operation == "update":
        action = site_zones.update_zone(zone.id, SiteZoneUpdate(name="Renamed park"), request, test_user, mock_db)
    else:
        action = site_zones.delete_zone(zone.id, request, test_user, mock_db)
    task = asyncio.create_task(action)
    gate = asyncio.create_task(entered.wait())
    try:
        # Let either the route complete prematurely or reach the commit gate.
        await asyncio.wait({task, gate}, timeout=0.2, return_when=asyncio.FIRST_COMPLETED)
        assert entered.is_set(), "The route returned before committing its authored change"
        assert not task.done(), "The route announced success while the commit was pending"
        release.set()
        if commit_fails:
            with pytest.raises(RuntimeError, match="Database commit failed"):
                await task
        else:
            await task
    finally:
        release.set()
        if not task.done():
            task.cancel()
        gate.cancel()
        await asyncio.gather(task, gate, return_exceptions=True)
