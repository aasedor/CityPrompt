import copy
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from geoalchemy2.shape import from_shape
from httpx import ASGITransport, AsyncClient
from shapely.geometry import Polygon, box

from app.api.v1 import zoning_studies as endpoint
from app.core.database import get_db
from app.core.security import require_auth
from app.models.reference_layers import ReferenceLayer

PROJECT, BOUNDARY = uuid.uuid4(), uuid.uuid4()
SITE = box(-114.12, 51.01, -114.119, 51.011)
BODY = {"boundary_id": str(BOUNDARY), "boundary_coordinates": list(SITE.exterior.coords)[:-1],
        "expected_hash": None, "zones": [{"id": "one", "label": "Housing", "color": "#dfb88b",
                                           "origin": "student", "rings": [list(SITE.exterior.coords)]}]}


def result(value=None, values=None):
    response = MagicMock()
    response.scalar_one_or_none.return_value = value
    response.scalars.return_value.all.return_value = values or []
    return response


@pytest.fixture
def db():
    session = AsyncMock()
    session.add = MagicMock()
    async def refresh(row):
        row.id = row.id or uuid.uuid4()
        row.created_at = datetime.now(timezone.utc)
    session.refresh.side_effect = refresh
    boundary = SimpleNamespace(id=BOUNDARY, project_id=PROJECT, zone_type="site_boundary",
                               is_active_boundary=True, geometry=from_shape(SITE, srid=4326))
    session.execute.side_effect = [result(), result(boundary), result(values=[])]
    return session


@pytest.fixture
async def client(db, monkeypatch):
    monkeypatch.setattr(endpoint, "check_project_permission", AsyncMock())
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1/zoning-studies")
    app.dependency_overrides[require_auth] = lambda: SimpleNamespace(id=uuid.uuid4())
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


@pytest.mark.asyncio
async def test_saves_a_reference_layer_and_requires_editor_without_zone_writes(client, db):
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/existing", json=BODY)
    assert response.status_code == 200, response.text
    layer = db.add.call_args.args[0]
    assert isinstance(layer, ReferenceLayer)
    assert layer.name == "Existing zoning study" and layer.feature_count == 1
    assert response.json()["content_hash"] == layer.content_hash
    assert layer.feature_collection["_citypromptStudy"]["condition"] == "existing"
    assert layer.source_url is None
    assert endpoint.check_project_permission.call_args.kwargs["required"] == "editor"
    db.delete.assert_not_called()


@pytest.mark.asyncio
async def test_viewer_cannot_save(client, db, monkeypatch):
    monkeypatch.setattr(endpoint, "check_project_permission", AsyncMock(side_effect=HTTPException(403, "Editor required")))
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/proposed", json=BODY)
    assert response.status_code == 403
    db.execute.assert_not_called()
    db.add.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["unsaved", "inactive", "different-project"])
async def test_changed_or_unrelated_boundary_cannot_receive_a_stale_map(client, db, mode):
    boundary = SimpleNamespace(id=BOUNDARY, project_id=PROJECT if mode != "different-project" else uuid.uuid4(),
                               zone_type="site_boundary", is_active_boundary=mode != "inactive", geometry=from_shape(SITE))
    db.execute.side_effect = [result(), result(boundary)]
    body = copy.deepcopy(BODY)
    if mode == "unsaved": body["boundary_coordinates"][0] = (body["boundary_coordinates"][0][0] + .0001, body["boundary_coordinates"][0][1])
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/existing", json=body)
    assert response.status_code == 409
    db.add.assert_not_called()
    db.flush.assert_not_called()


def managed(condition="existing"):
    return SimpleNamespace(source_filename=f"cityprompt-zoning-study-{condition}.geojson",
        feature_collection={"_citypromptStudy": {"schema": 1, "condition": condition}},
        content_hash="a"*64, storage_bytes=100)


@pytest.mark.asyncio
async def test_existing_and_proposed_are_separate_slots_and_revision_checks_prevent_lost_updates(client, db):
    old = managed()
    boundary = SimpleNamespace(project_id=PROJECT, zone_type="site_boundary", is_active_boundary=True, geometry=from_shape(SITE))
    db.execute.side_effect = [result(), result(boundary), result(values=[old])]
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/existing", json=BODY)
    assert response.status_code == 409
    db.add.assert_not_called()
    db.flush.assert_not_called()
    db.execute.side_effect = [result(), result(boundary), result(values=[old])]
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/proposed", json=BODY)
    assert response.status_code == 200, response.text
    assert db.add.call_args.args[0].name == "Proposed land-use study"
    assert old.content_hash == "a"*64


@pytest.mark.asyncio
async def test_removed_layer_does_not_silently_reappear_from_old_revision(client, db):
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/existing", json={**BODY, "expected_hash": "a"*64})
    assert response.status_code == 409
    db.add.assert_not_called()


def test_validated_shapes_preserve_holes_source_provenance_and_overlay_warning():
    body = copy.deepcopy(BODY)
    hole = box(-114.1198, 51.0102, -114.1196, 51.0104)
    body["zones"][0]["rings"].append(list(hole.exterior.coords))
    body["zones"].append({**body["zones"][0], "id": "two", "origin": "calgary-extract"})
    collection, size, digest, warnings = endpoint.study_collection(endpoint.StudyRequest(**body), "existing", SITE)
    assert len(collection["features"][0]["geometry"]["coordinates"]) == 2
    assert collection["features"][1]["properties"]["origin"] == "calgary-extract"
    assert size > 100 and len(digest) == 64
    assert any("overlap" in warning for warning in warnings)


@pytest.mark.asyncio
@pytest.mark.parametrize("district", [
    {"code": "M-C1", "designation": "M-C1 d75", "description": "Multi-Residential - Contextual Low Profile"},
    {"code": "DC", "designation": "DC48Z84", "description": "Direct Control"},
])
async def test_saves_district_identity_independently_of_student_caption(client, db, district):
    body = copy.deepcopy(BODY)
    body["zones"][0].update(label="Courtyard housing", origin="student", district=district)
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/proposed", json=body)
    assert response.status_code == 200, response.text
    properties = response.json()["feature_collection"]["features"][0]["properties"]
    assert properties["district"] == district
    assert properties["label"] == "Courtyard housing"
    assert response.json()["source_url"].endswith("/qe6k-p9nh")


@pytest.mark.parametrize("district", [{"designation": " "}, {"designation": "x"*121}, {"designation": "M-C1", "code": " "}, {"designation": "M-C1", "description": "x"*301}])
def test_invalid_district_metadata_is_rejected(district):
    body = copy.deepcopy(BODY)
    body["zones"][0]["district"] = district
    with pytest.raises(ValueError):
        endpoint.StudyRequest(**body)


@pytest.mark.asyncio
@pytest.mark.parametrize("opacity", [0, 0.4, 1])
async def test_custom_zone_and_opacity_round_trip_without_city_provenance(client, db, opacity):
    body = copy.deepcopy(BODY)
    body["opacity"] = opacity
    body["zones"][0].update(custom=True, label="Community garden", color="#75b6b0")
    response = await client.put(f"/api/v1/zoning-studies/projects/{PROJECT}/proposed", json=body)
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved["opacity"] == opacity
    assert saved["source_url"] is None
    properties = saved["feature_collection"]["features"][0]["properties"]
    assert properties["custom"] is True
    assert properties["label"] == "Community garden"
    assert properties["color"] == "#75b6b0"
    assert "district" not in properties


@pytest.mark.parametrize("patch", [
    {"opacity": -0.1}, {"opacity": 1.1},
    {"zones": [{**BODY["zones"][0], "custom": True, "district": {"designation": "R-CG"}}]},
])
def test_invalid_opacity_or_custom_city_identity_is_rejected(patch):
    with pytest.raises(ValueError):
        endpoint.study_collection(endpoint.StudyRequest(**{**BODY, **patch}), "proposed", SITE)


@pytest.mark.parametrize("kind", ["crossing", "outside", "unclosed", "duplicate-id", "blank-label"])
def test_invalid_drawings_are_rejected_before_storage(kind):
    body = copy.deepcopy(BODY)
    if kind == "crossing": body["zones"][0]["rings"] = [[(-114.12,51.01),(-114.119,51.011),(-114.12,51.011),(-114.119,51.01),(-114.12,51.01)]]
    if kind == "outside": body["zones"][0]["rings"] = [list(box(-114.12,51.01,-114.118,51.012).exterior.coords)]
    if kind == "unclosed": body["zones"][0]["rings"][0] = body["zones"][0]["rings"][0][:-1]
    if kind == "duplicate-id": body["zones"].append(body["zones"][0])
    if kind == "blank-label": body["zones"][0]["label"] = " "
    with pytest.raises(ValueError): endpoint.study_collection(endpoint.StudyRequest(**body), "proposed", SITE)


@pytest.mark.asyncio
async def test_draft_bylaw_is_a_separate_sourced_layer(client, db):
    body = copy.deepcopy(BODY)
    body['zones'][0]['district'] = {'designation': 'MU-1', 'bylaw': 'draft-2025'}
    response = await client.put(f'/api/v1/zoning-studies/projects/{PROJECT}/draft-2025', json=body)
    assert response.status_code == 200, response.text
    layer = db.add.call_args.args[0]
    assert layer.source_filename == 'cityprompt-zoning-study-draft-2025.geojson'
    assert 'may2025.pdf' in layer.source_url
    assert layer.feature_collection['features'][0]['properties']['district']['bylaw'] == 'draft-2025'


@pytest.mark.parametrize('condition,district,origin', [
    ('proposed', {'designation': 'MU-1', 'bylaw': 'draft-2025'}, 'student'),
    ('existing', {'designation': 'MU-1', 'bylaw': 'draft-2025'}, 'student'),
    ('draft-2025', {'designation': 'MU-1'}, 'student'),
    ('draft-2025', {'designation': 'MU-1', 'bylaw': 'draft-2025'}, 'calgary-extract'),
])
def test_cannot_mix_draft_and_current_bylaw_identity(condition, district, origin):
    body = copy.deepcopy(BODY)
    body['zones'][0].update(district=district, origin=origin)
    with pytest.raises(ValueError, match='draft|Draft'):
        endpoint.study_collection(endpoint.StudyRequest(**body), condition, SITE)
