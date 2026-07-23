import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from geoalchemy2.elements import WKTElement

from app.api.v1 import model_library
from app.models.models import Building, ModelLibraryEntry, SiteZone
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


def _building(project_id: uuid.UUID) -> Building:
    return Building(
        id=uuid.uuid4(),
        project_id=project_id,
        name="Compiled building",
        footprint=WKTElement("POLYGON((-114 51,-113.999 51,-113.999 51.001,-114 51.001,-114 51))", srid=4326),
        height_meters=18,
        floor_count=6,
        floor_height_meters=3,
        roof_type="flat",
        specifications={"legoAssembly": {"instances": [{"model_url": "/module.glb"}]}},
        generation_status="idle",
        rotation_degrees=0,
        architectural_style="modern",
        preview_status="idle",
        created_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
    )


def _compiled_zone(project_id: uuid.UUID, building_id: uuid.UUID) -> SiteZone:
    return SiteZone(
        id=uuid.uuid4(),
        project_id=project_id,
        name="Compiled zone",
        zone_type="building",
        building_id=building_id,
        building_ids=[str(building_id)],
        properties={
            "_plan_role": "building",
            "community_3d": {
                "schema_version": 1,
                "state": "compiled",
                "kind": "building",
                "generator": "lego_assembly",
                "compiled_at": "2026-07-20T00:00:00Z",
                "source_hash": "1" * 64,
                "representation_hash": "2" * 64,
            },
        },
    )


@pytest.mark.anyio
async def test_representation_update_locks_project_and_stales_linked_community_zone(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = _building(project.id)
    zone = _compiled_zone(project.id, building.id)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building),
        _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
    ])

    response = await client.put(
        f"/api/v1/buildings/{building.id}",
        headers=auth_headers,
        json={
            "floor_count": 8,
            "specifications": {"legoAssembly": {"instances": [{"model_url": "/new.glb"}]}},
            "footprint_coordinates": [
                [-114.0, 51.0],
                [-113.998, 51.0],
                [-113.998, 51.002],
                [-114.0, 51.002],
            ],
        },
    )

    assert response.status_code == 200, response.text
    assert building.floor_count == 8
    assert building.specifications["legoAssembly"]["instances"][0]["model_url"] == "/new.glb"
    assert zone.properties["community_3d"]["state"] == "stale"
    assert "representation changed" in zone.properties["community_3d"]["stale_reason"]
    assert "FOR UPDATE" in str(mock_db.execute.await_args_list[3].args[0])
    assert mock_db.refresh.await_count == 2


@pytest.mark.anyio
async def test_building_delete_locks_project_and_stales_linked_community_zone(
    client, mock_db, test_user, auth_headers
):
    project = FakeProject(owner_id=test_user.id)
    building = _building(project.id)
    zone = _compiled_zone(project.id, building.id)
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(building),
        _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
    ])

    response = await client.delete(
        f"/api/v1/buildings/{building.id}", headers=auth_headers
    )

    assert response.status_code == 204, response.text
    assert zone.properties["community_3d"]["state"] == "stale"
    assert "deleted" in zone.properties["community_3d"]["stale_reason"]
    assert "FOR UPDATE" in str(mock_db.execute.await_args_list[3].args[0])
    mock_db.delete.assert_awaited_once_with(building)


@pytest.mark.anyio
async def test_library_model_swap_locks_project_and_stales_linked_community_zone(
    client, mock_db, test_user, auth_headers, monkeypatch
):
    project = FakeProject(owner_id=test_user.id)
    building = _building(project.id)
    zone = _compiled_zone(project.id, building.id)
    entry = ModelLibraryEntry(
        id=uuid.uuid4(),
        owner_id=test_user.id,
        name="Reusable model",
        category="commercial",
        tags=[],
        model_url="/library/source.glb",
        lod_urls={"0": "/library/source-lod0.glb"},
        generation_prompt="Brick mixed use",
        generation_engine="meshy",
        architectural_style="industrial",
        is_public=False,
        use_count=0,
    )
    monkeypatch.setattr(
        model_library,
        "_copy_s3_object",
        lambda _source, destination: f"/api/v1/files/{destination}",
    )
    mock_db.execute = AsyncMock(side_effect=[
        _scalar_result(test_user),
        _scalar_result(entry),
        _scalar_result(building),
        _scalar_result(project),
        _scalar_result(project.id),
        _scalars_result([zone]),
    ])

    response = await client.post(
        f"/api/v1/model-library/items/{entry.id}/apply",
        headers=auth_headers,
        json={"building_id": str(building.id)},
    )

    assert response.status_code == 200, response.text
    assert building.model_url.endswith(f"/{building.id}_ai.glb")
    assert building.lod_urls["0"].endswith(f"/{building.id}_lod0.glb")
    assert building.architectural_style == "industrial"
    assert zone.properties["community_3d"]["state"] == "stale"
    assert "FOR UPDATE" in str(mock_db.execute.await_args_list[4].args[0])
