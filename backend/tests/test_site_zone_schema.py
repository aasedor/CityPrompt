"""Request-contract tests for persisted site-zone types."""

import uuid

import pytest
from pydantic import ValidationError

from app.core.security import require_auth
from app.main import app
from app.schemas.schemas import SiteZoneCreate, SiteZoneUpdate


POLYGON = [
    [-114.1, 51.0],
    [-114.09, 51.0],
    [-114.09, 51.01],
    [-114.1, 51.0],
]


@pytest.mark.parametrize(
    "zone_type",
    [
        "site_boundary",
        "building",
        "residential",
        "road",
        "green_space",
        "parking",
        "water",
        "development_area",
    ],
)
def test_site_zone_create_accepts_persisted_zone_types(zone_type: str) -> None:
    zone = SiteZoneCreate(zone_type=zone_type, coordinates=POLYGON)

    assert zone.zone_type == zone_type


@pytest.mark.parametrize("schema", [SiteZoneCreate, SiteZoneUpdate])
def test_site_zone_requests_reject_path_before_database(schema) -> None:
    payload = {"zone_type": "path"}
    if schema is SiteZoneCreate:
        payload["coordinates"] = POLYGON

    with pytest.raises(ValidationError) as exc_info:
        schema(**payload)

    error = exc_info.value.errors()[0]
    assert error["loc"] == ("zone_type",)
    assert error["type"] == "literal_error"


def test_multi_use_trail_uses_road_type_metadata() -> None:
    zone = SiteZoneCreate(
        zone_type="road",
        coordinates=POLYGON,
        properties={"road_type": "multi_use_trail"},
    )

    assert zone.properties == {"road_type": "multi_use_trail"}


@pytest.mark.asyncio
async def test_create_zone_api_returns_422_for_path_before_database(client, mock_db, test_user) -> None:
    app.dependency_overrides[require_auth] = lambda: test_user

    response = await client.post(
        f"/api/v1/site-zones/projects/{uuid.uuid4()}/zones",
        json={"zone_type": "path", "coordinates": POLYGON},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "zone_type"]
    mock_db.execute.assert_not_awaited()
