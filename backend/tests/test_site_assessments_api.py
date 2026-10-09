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
from app.models.models import Project

ZONE = uuid.uuid4()
SITE = box(-114.12, 51.01, -114.119, 51.011)


@pytest.fixture
async def environment(monkeypatch):
    db = AsyncMock()
    boundary = SimpleNamespace(id=ZONE, project_id=uuid.uuid4(), zone_type="site_boundary",
                               is_active_boundary=True, geometry=from_shape(SITE, srid=4326))
    project = SimpleNamespace(id=boundary.project_id, metadata_={"scene_details": {"revision": 4}})
    async def execute(statement):
        result = MagicMock()
        model = statement.column_descriptions[0]['entity']
        result.scalar_one_or_none.return_value = project if model is Project else boundary
        return result
    db.execute.side_effect = execute
    permission = AsyncMock(return_value="owner")
    calculation = AsyncMock(return_value={"property_count": 2})
    monkeypatch.setattr(endpoint, "check_project_permission", permission)
    monkeypatch.setattr(endpoint, "get_site_assessment", calculation)
    app = FastAPI(); app.include_router(endpoint.router)
    app.dependency_overrides[require_auth] = lambda: SimpleNamespace(id=uuid.uuid4())
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, boundary, permission, calculation, project, db


@pytest.mark.asyncio
async def test_calculation_persists_and_read_restores_without_external_lookup(environment):
    client, boundary, permission, calculation, project, db = environment
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 200, response.text
    assert response.json()["boundary_id"] == str(ZONE)
    assert permission.await_args.kwargs["required"] == "viewer"
    calculation.assert_awaited_once()
    assert project.metadata_["scene_details"] == {"revision": 4}
    restored = await client.get(f"/zones/{ZONE}")
    assert restored.json()["assessment"] == response.json()
    calculation.assert_awaited_once()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_access_denied_before_source_lookup(environment):
    client, boundary, permission, calculation, project, db = environment
    permission.side_effect = HTTPException(403, "Access denied")
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 403
    calculation.assert_not_awaited()
    assert (await client.get(f"/zones/{ZONE}")).status_code == 403


@pytest.mark.asyncio
async def test_inactive_boundary_and_pending_save_are_rejected(environment):
    client, boundary, permission, calculation, project, db = environment
    boundary.is_active_boundary = False
    assert (await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})).status_code == 422
    boundary.is_active_boundary = True
    changed = box(-114.121, 51.01, -114.119, 51.011)
    assert (await client.post(f"/zones/{ZONE}", json={"coordinates": list(changed.exterior.coords)})).status_code == 409
    calculation.assert_not_awaited()


@pytest.mark.asyncio
async def test_old_geometry_and_inactive_boundary_never_restore(environment):
    client, boundary, permission, calculation, project, db = environment
    await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    boundary.geometry = from_shape(box(-114.121, 51.01, -114.119, 51.011), srid=4326)
    assert (await client.get(f"/zones/{ZONE}")).json() is None
    boundary.geometry = from_shape(SITE, srid=4326)
    boundary.is_active_boundary = False
    assert (await client.get(f"/zones/{ZONE}")).json() is None


@pytest.mark.asyncio
async def test_viewers_can_calculate_but_do_not_replace_saved_evidence(environment):
    client, boundary, permission, calculation, project, db = environment
    permission.return_value = "viewer"
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 200
    assert 'site_assessment' not in project.metadata_
    db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_boundary_changed_during_lookup_does_not_save_stale_result(environment):
    client, boundary, permission, calculation, project, db = environment
    async def calculate(site):
        boundary.geometry = from_shape(box(-114.121, 51.01, -114.119, 51.011), srid=4326)
        return {"property_count": 2}
    calculation.side_effect = calculate
    response = await client.post(f"/zones/{ZONE}", json={"coordinates": list(SITE.exterior.coords)})
    assert response.status_code == 409
    assert 'site_assessment' not in project.metadata_
    db.flush.assert_not_awaited()
