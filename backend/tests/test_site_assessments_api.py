import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from geoalchemy2.shape import from_shape
from httpx import ASGITransport, AsyncClient
from shapely.geometry import box

from app.api.v1 import site_assessments as endpoint
from app.core.database import get_db
from app.core.security import require_auth

ZONE = uuid.uuid4()
SITE = box(-114.12, 51.01, -114.119, 51.011)


@pytest.fixture
async def environment(monkeypatch):
    db = AsyncMock()
    boundary = SimpleNamespace(id=ZONE, project_id=uuid.uuid4(), zone_type="site_boundary",
                               is_active_boundary=True, geometry=from_shape(SITE, srid=4326))
    result = MagicMock(); result.scalar_one_or_none.return_value = boundary
    db.execute.return_value = result
    permission = AsyncMock(return_value="viewer")
    calculation = AsyncMock(return_value={"property_count": 2})
    monkeypatch.setattr(endpoint, "check_project_permission", permission)
    monkeypatch.setattr(endpoint, "get_site_assessment", calculation)
    app = FastAPI(); app.include_router(endpoint.router)
    app.dependency_overrides[require_auth] = lambda: SimpleNamespace(id=uuid.uuid4())
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, boundary, permission, calculation


@pytest.mark.asyncio
async def test_active_saved_boundary_calculated_without_database_writes(environment):
    client, boundary, permission, calculation = environment
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 200, response.text
    assert response.json()["boundary_id"] == str(ZONE)
    assert permission.await_args.kwargs["required"] == "viewer"
    calculation.assert_awaited_once()


@pytest.mark.asyncio
async def test_access_denied_before_source_lookup(environment):
    client, boundary, permission, calculation = environment
    permission.side_effect = HTTPException(403, "Access denied")
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 403
    calculation.assert_not_awaited()


@pytest.mark.asyncio
async def test_inactive_boundary_and_pending_save_are_rejected(environment):
    client, boundary, permission, calculation = environment
    boundary.is_active_boundary = False
    assert (await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})).status_code == 422
    boundary.is_active_boundary = True
    changed = box(-114.121, 51.01, -114.119, 51.011)
    assert (await client.post(f"/zones/{ZONE}", json={"coordinates": list(changed.exterior.coords)})).status_code == 409
    calculation.assert_not_awaited()
