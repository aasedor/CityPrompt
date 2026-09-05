"""Exercise permissions, atomic persistence and retry semantics without providers."""

import json
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects import postgresql

from app.api.v1 import reference_layers as endpoint
from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import SiteZone
from app.models.reference_layers import ReferenceLayer

PROJECT = uuid.uuid4()
USER = SimpleNamespace(id=uuid.uuid4(), email="student@example.edu", role="editor")
COLLECTION = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"ZONE": "RM"}, "geometry": {"type": "Point", "coordinates": [-123, 49]}}]}


def result(value=None, values=None):
    value_result = MagicMock()
    value_result.scalar_one_or_none.return_value = value
    value_result.scalars.return_value.all.return_value = values or []
    return value_result


@pytest.fixture
def session():
    db = AsyncMock()
    db.add = MagicMock()
    async def refresh(row):
        row.id = row.id or uuid.uuid4()
        row.created_at = datetime.now(timezone.utc)
    db.refresh.side_effect = refresh
    return db


@pytest.fixture
async def ref_client(session):
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1/reference-layers")
    app.dependency_overrides[require_auth] = lambda: USER
    app.dependency_overrides[get_db] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_import_persists_reference_only_even_outside_site(ref_client, session):
    project = SimpleNamespace(id=PROJECT, owner_id=USER.id)
    session.execute.side_effect = [result(project), result(), result(values=[])]
    response = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", files={"file": ("zoning.geojson", json.dumps(COLLECTION), "application/geo+json")}, data={"kind": "zoning", "name": "Zoning"})
    assert response.status_code == 201, response.text
    stored = session.add.call_args.args[0]
    assert isinstance(stored, ReferenceLayer) and not isinstance(stored, SiteZone)
    assert stored.feature_collection == COLLECTION
    assert stored.kind == "zoning"
    assert response.json()["bounds"] == [-123, 49, -123, 49]
    # No authored-zone query, containment check or invalidation occurs.
    statements = [str(call.args[0].compile(dialect=postgresql.dialect())) for call in session.execute.call_args_list]
    assert all("site_zones" not in statement for statement in statements)


@pytest.mark.asyncio
async def test_source_provenance_survives_import_and_metadata_update(ref_client, session):
    project = SimpleNamespace(id=PROJECT, owner_id=USER.id)
    session.execute.side_effect = [result(project), result(), result(values=[])]
    source = "https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh"
    imported = await ref_client.post(
        f"/api/v1/reference-layers/projects/{PROJECT}/import",
        files={"file": ("zoning.geojson", json.dumps(COLLECTION))},
        data={"kind": "zoning", "name": "Calgary zoning", "source_url": source},
    )
    assert imported.status_code == 201, imported.text
    assert imported.json()["source_url"] == source
    layer = session.add.call_args.args[0]
    assert layer.source_url == source
    session.get.return_value = layer
    session.execute.side_effect = [result(project)]
    updated = await ref_client.put(
        f"/api/v1/reference-layers/{layer.id}",
        json={"name": layer.name, "kind": "zoning", "source_url": source, "description": "Dated study-area extract"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["source_url"] == source
    assert updated.json()["description"] == "Dated study-area extract"


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["not-a-url", "ftp://example.com/data", "https://example.com/" + "x" * 2030])
async def test_invalid_source_link_is_validation_error_without_writes(ref_client, session, source):
    session.execute.side_effect = [result(SimpleNamespace(id=PROJECT, owner_id=USER.id))]
    response = await ref_client.post(
        f"/api/v1/reference-layers/projects/{PROJECT}/import",
        files={"file": ("zoning.geojson", json.dumps(COLLECTION))},
        data={"source_url": source},
    )
    assert response.status_code == 422, response.text
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_editor_import_uses_project_share(ref_client, session):
    project = SimpleNamespace(id=PROJECT, owner_id=uuid.uuid4())
    session.execute.side_effect = [result(project), result(SimpleNamespace(permission="editor")), result(), result(values=[])]
    response = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", files={"file": ("ref.json", json.dumps(COLLECTION))})
    assert response.status_code == 201


@pytest.mark.asyncio
@pytest.mark.parametrize("share", [None, SimpleNamespace(permission="viewer")])
async def test_unrelated_and_viewer_cannot_import(ref_client, session, share):
    session.execute.side_effect = [result(SimpleNamespace(id=PROJECT, owner_id=uuid.uuid4())), result(share)]
    response = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", files={"file": ("ref.json", json.dumps(COLLECTION))})
    assert response.status_code == 403
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_duplicate_retry_returns_existing_layer(ref_client, session):
    project = SimpleNamespace(id=PROJECT, owner_id=USER.id)
    session.execute.side_effect = [result(project), result(), result(values=[])]
    request = {"files": {"file": ("ref.json", json.dumps(COLLECTION))}}
    first = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", **request)
    layer = session.add.call_args.args[0]
    session.add.reset_mock()
    session.execute.side_effect = [result(project), result(), result(values=[layer])]
    second = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", **request)
    assert first.status_code == 201 and second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_bad_import_has_no_partial_persistence(ref_client, session):
    session.execute.side_effect = [result(SimpleNamespace(id=PROJECT, owner_id=USER.id))]
    response = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", files={"file": ("ref.json", b"not geojson")})
    assert response.status_code == 400
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_project_capacity_limit(ref_client, session, monkeypatch):
    monkeypatch.setattr(endpoint, "MAX_PROJECT_LAYERS", 1)
    session.execute.side_effect = [result(SimpleNamespace(id=PROJECT, owner_id=USER.id)), result(), result(values=[SimpleNamespace(content_hash="other", storage_bytes=10)])]
    response = await ref_client.post(f"/api/v1/reference-layers/projects/{PROJECT}/import", files={"file": ("ref.json", json.dumps(COLLECTION))})
    assert response.status_code == 409
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_viewer_can_read_but_not_delete(ref_client, session):
    project = SimpleNamespace(id=PROJECT, owner_id=uuid.uuid4())
    session.execute.side_effect = [result(project), result(SimpleNamespace(permission="viewer")), result(values=[])]
    response = await ref_client.get(f"/api/v1/reference-layers/projects/{PROJECT}")
    assert response.status_code == 200 and response.json()["can_edit"] is False
    layer_id = uuid.uuid4()
    session.get.return_value = SimpleNamespace(project_id=PROJECT)
    session.execute.side_effect = [result(project), result(SimpleNamespace(permission="viewer"))]
    deletion = await ref_client.delete(f"/api/v1/reference-layers/{layer_id}")
    assert deletion.status_code == 403
    session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_anonymous_reference_access_is_rejected():
    app = FastAPI()
    app.include_router(endpoint.router)
    async def denied():
        raise HTTPException(401, "Authentication required")
    app.dependency_overrides[require_auth] = denied
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get(f"/projects/{PROJECT}")).status_code == 401
