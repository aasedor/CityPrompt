"""Context enrichment preserves edit authorization and revision-safe undo."""

from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import httpx
import pytest
from shapely.geometry import Polygon
from tests.conftest import FakeProject
from app.api.v1 import site_zones


def scalar(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["success", "conflict", "unauthorized"])
async def test_context_revision_contract(mode, client, mock_db, test_user, auth_headers, monkeypatch):
    before = datetime(2026, 9, 16, tzinfo=timezone.utc)
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type="site_boundary",
        geometry=None,
        properties={"terrain_elevation_m": 1102},
        updated_at=before,
    )
    project = FakeProject(id=zone.project_id, owner_id=test_user.id if mode != "unauthorized" else uuid.uuid4())
    mock_db.execute = AsyncMock(side_effect=[scalar(test_user), scalar(zone), scalar(project), scalar(None)])
    fetch = AsyncMock(
        return_value={"buildings": [], "roads": [], "parks": [], "water": [], "fetched_at": before.isoformat()}
    )
    monkeypatch.setattr(site_zones, "OSMContextFetcher", lambda: SimpleNamespace(fetch=fetch))
    monkeypatch.setattr(site_zones, "to_shape", lambda _: Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]))
    lock = AsyncMock()
    monkeypatch.setattr(site_zones, "lock_residual_landscape_project", lock)

    async def refresh(_):
        if mode == "conflict":
            zone.updated_at = before + timedelta(seconds=1)
            zone.properties = {"terrain_elevation_m": 1105, "name": "newer authored edit"}

    mock_db.refresh = AsyncMock(side_effect=refresh)
    response = await client.post(f"/api/v1/site-zones/{zone.id}/fetch-context", headers=auth_headers)
    if mode == "unauthorized":
        assert response.status_code == 403
        fetch.assert_not_called()
        lock.assert_not_called()
    elif mode == "conflict":
        assert response.status_code == 409
        assert zone.properties == {"terrain_elevation_m": 1105, "name": "newer authored edit"}
        mock_db.flush.assert_not_awaited()
    else:
        assert response.status_code == 200
        payload = response.json()
        assert payload["zone_id"] == str(zone.id)
        assert datetime.fromisoformat(payload["source_updated_at"].replace("Z", "+00:00")) == before
        assert datetime.fromisoformat(payload["updated_at"].replace("Z", "+00:00")) > before
        assert zone.properties["terrain_elevation_m"] == 1102
        assert "_osm_context" in zone.properties
        lock.assert_awaited_once_with(mock_db, zone.project_id)


@pytest.mark.anyio
async def test_unavailable_osm_context_does_not_change_saved_boundary(
    client, mock_db, test_user, auth_headers, monkeypatch
):
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type="site_boundary",
        geometry=None,
        properties={"terrain_elevation_m": 1102},
        updated_at=datetime(2026, 9, 23, tzinfo=timezone.utc),
    )
    project = FakeProject(id=zone.project_id, owner_id=test_user.id)
    mock_db.execute = AsyncMock(side_effect=[scalar(test_user), scalar(zone), scalar(project)])
    fetch = AsyncMock(side_effect=httpx.ConnectError("Overpass unavailable"))
    monkeypatch.setattr(site_zones, "OSMContextFetcher", lambda: SimpleNamespace(fetch=fetch))
    monkeypatch.setattr(site_zones, "to_shape", lambda _: Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]))
    response = await client.post(f"/api/v1/site-zones/{zone.id}/fetch-context", headers=auth_headers)
    assert response.status_code == 503
    assert response.json()["detail"] == "Nearby map context is temporarily unavailable; the site boundary is saved."
    assert zone.properties == {"terrain_elevation_m": 1102}
    mock_db.flush.assert_not_awaited()
