"""Urban DNA API — auth, permission, generate-queues-task, latest-snapshot reads.

Mock DB per conftest; Celery .delay is monkeypatched (no Redis in tests).
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from tests.conftest import FakeProject

DOWNTOWN_CALGARY = Polygon([
    (-114.075, 51.043), (-114.062, 51.043), (-114.062, 51.049), (-114.075, 51.049),
])


class FakeZone:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.project_id = kwargs.get("project_id", uuid.uuid4())
        self.zone_type = kwargs.get("zone_type", "site_boundary")
        self.geometry = from_shape(kwargs.get("polygon", DOWNTOWN_CALGARY), srid=4326)


class FakeSnapshot:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.zone_id = kwargs.get("zone_id", uuid.uuid4())
        self.project_id = kwargs.get("project_id", uuid.uuid4())
        self.city_id = kwargs.get("city_id", "calgary")
        self.status = kwargs.get("status", "complete")
        self.dna_schema_version = kwargs.get("dna_schema_version", "1.0.0")
        self.dna = kwargs.get("dna", {"city_id": "calgary"})
        self.overall_confidence = kwargs.get("overall_confidence", 0.82)
        self.error = kwargs.get("error", None)
        self.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
        self.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.anyio
async def test_generate_requires_auth(client):
    response = await client.post(f"/api/v1/urban-dna/zones/{uuid.uuid4()}/generate")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_requires_auth(client):
    response = await client.get(f"/api/v1/urban-dna/zones/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_generate_404_for_missing_zone(client, mock_db, test_user, auth_headers):
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),  # require_auth user lookup
        _scalar_result(None),       # zone lookup
    ])
    response = await client.post(
        f"/api/v1/urban-dna/zones/{uuid.uuid4()}/generate", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_generate_forbidden_without_editor_permission(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject()  # owned by someone else
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
        _scalar_result(None),  # no share
    ])
    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/generate", headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_generate_creates_snapshot_and_queues_task(
    client, mock_db, test_user, auth_headers, monkeypatch
):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
    ])

    import app.tasks.urban_dna as tasks_module

    delay_mock = MagicMock()
    monkeypatch.setattr(tasks_module.generate_urban_dna, "delay", delay_mock)

    response = await client.post(
        f"/api/v1/urban-dna/zones/{zone.id}/generate", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["city_id"] == "calgary"  # downtown polygon detected as Calgary
    assert data["zone_id"] == str(zone.id)

    mock_db.add.assert_called_once()
    delay_mock.assert_called_once_with(data["snapshot_id"])


@pytest.mark.anyio
async def test_get_latest_returns_snapshot(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    snapshot = FakeSnapshot(zone_id=zone.id, project_id=zone.project_id, status="partial")
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
        _scalar_result(snapshot),
    ])

    response = await client.get(f"/api/v1/urban-dna/zones/{zone.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "partial"
    assert data["overall_confidence"] == 0.82
    assert data["dna"] == {"city_id": "calgary"}


@pytest.mark.anyio
async def test_get_latest_404_when_no_snapshot(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
        _scalar_result(None),
    ])
    response = await client.get(f"/api/v1/urban-dna/zones/{zone.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_capabilities_lists_calgary_datasets(client, mock_db, test_user, auth_headers):
    zone = FakeZone()
    project = FakeProject(owner_id=test_user.id, id=zone.project_id)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(zone),
        _scalar_result(project),
    ])
    response = await client.get(f"/api/v1/urban-dna/capabilities/{zone.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["city_id"] == "calgary"
    ids = [d["id"] for d in data["datasets"]]
    assert ids == sorted(ids, key=lambda x: [d["id"] for d in data["datasets"]].index(x))
    assert "calgary.land_use_districts" in ids
    assert "land_use.dominant_district" in data["dna_fields"]
