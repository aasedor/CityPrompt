"""API regression tests for site zone batch generation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.models import Building
from tests.conftest import FakeProject


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    result.scalars.return_value = scalars
    return result


@pytest.mark.anyio
async def test_generate_all_handles_invalid_building_ids_payload(client, mock_db, test_user, auth_headers):
    project_id = uuid.uuid4()
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=project_id,
        name="Residential Zone",
        zone_type="residential",
        properties={"unit_count": "", "description_text": "Single detached home"},
        geometry=None,
        building_id=None,
        building_ids=["not-a-uuid", "", None],
    )

    project = FakeProject(id=project_id, owner_id=test_user.id)

    def _assign_building_id(obj):
        if isinstance(obj, Building) and not getattr(obj, "id", None):
            obj.id = uuid.uuid4()

    mock_db.add.side_effect = _assign_building_id
    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalar_result(project),  # project lookup
            _scalars_result([zone]),  # zone list lookup
        ]
    )

    response = await client.post(
        f"/api/v1/site-zones/projects/{project_id}/generate-all",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_zones"] == 1
    assert payload["buildings_created"] == 1
    assert isinstance(payload.get("failed_zones"), list)
    assert zone.building_ids and zone.building_ids[0] != "not-a-uuid"


@pytest.mark.anyio
async def test_generate_all_returns_failed_zone_instead_of_500(client, mock_db, test_user, auth_headers):
    project_id = uuid.uuid4()
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=project_id,
        name="Large Residential Zone",
        zone_type="development_area",
        properties={"unit_count": 24, "description_text": "24 townhomes"},
        geometry=None,  # Triggers layout generation fallback failure path
        building_id=None,
        building_ids=[],
    )

    project = FakeProject(id=project_id, owner_id=test_user.id)

    mock_db.execute = AsyncMock(
        side_effect=[
            _scalar_result(test_user),  # require_auth user lookup
            _scalar_result(project),  # project lookup
            _scalars_result([zone]),  # zone list lookup
        ]
    )

    response = await client.post(
        f"/api/v1/site-zones/projects/{project_id}/generate-all",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_zones"] == 1
    assert payload["generations_queued"] == 0
    assert len(payload["failed_zones"]) == 1
    assert payload["failed_zones"][0]["zone_id"] == str(zone.id)
