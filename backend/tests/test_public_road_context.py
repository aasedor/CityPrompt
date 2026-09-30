import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from shapely.geometry import box
from app.services.public_road_context import eligible_public_road, fetch_public_road_context
from app.services.osm_context import OSMContextFetcher
from app.api.v1 import site_zones
from tests.conftest import FakeProject


@pytest.mark.parametrize("tags,eligible", [
    ({"highway": "residential"}, True), ({"highway": "tertiary"}, True),
    ({"highway": "motorway"}, False), ({"highway": "service"}, False),
    ({"highway": "residential", "access": "private"}, False),
    ({"highway": "residential", "vehicle": "destination"}, False),
    ({"highway": "residential", "bridge": "yes"}, False),
    ({"highway": "residential", "tunnel": "yes"}, False),
    ({"highway": "residential", "layer": "1"}, False),
    ({"highway": "residential", "access:conditional": "no @ (school hours)"}, False),
])
def test_restrictions_survive_osm_parsing(tags, eligible):
    data = {"elements": [{"type": "node", "id": 1, "lon": 0, "lat": 0},
                         {"type": "node", "id": 2, "lon": .001, "lat": 0},
                         {"type": "way", "id": 3, "nodes": [1, 2], "tags": tags}]}
    road = OSMContextFetcher()._parse_response(data, box(0, 0, .001, .001))["roads"][0]
    assert eligible_public_road(road) is eligible
    road.pop("connection_tags")
    assert not eligible_public_road(road)  # Legacy snapshots cannot assert eligibility.


@pytest.mark.anyio
async def test_bounded_lookup_rejects_large_sites_and_truncation(monkeypatch):
    fetch = AsyncMock(return_value={"truncated": True})
    monkeypatch.setattr(OSMContextFetcher, "fetch", fetch)
    with pytest.raises(ValueError, match="1.5 km"):
        await fetch_public_road_context(box(0, 0, .1, .1))
    fetch.assert_not_awaited()
    with pytest.raises(ValueError, match="dense"):
        await fetch_public_road_context(box(0, 0, .001, .001))


def scalar(value):
    result = MagicMock(); result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.anyio
async def test_cleared_site_keeps_outside_buildings_blocking(monkeypatch):
    shape = box(0, 0, .001, .001)
    fetch = AsyncMock(return_value={"roads": [], "water": [], "buildings": [
        {"coordinates": list(box(.0001, .0001, .0002, .0002).exterior.coords)},
        {"coordinates": list(box(.0009, .0001, .0012, .0002).exterior.coords)},
    ]})
    monkeypatch.setattr(OSMContextFetcher, "fetch", fetch)
    assert len((await fetch_public_road_context(shape))["blockers"]) == 2
    cleared = await fetch_public_road_context(shape, clear_inside=True)
    assert len(cleared["blockers"]) == 1
    assert min(p[0] for p in cleared["blockers"][0]) == .001


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["success", "unavailable", "unauthorized", "not_boundary"])
async def test_read_only_authorized_lookup(mode, client, mock_db, test_user, auth_headers, monkeypatch):
    zone = SimpleNamespace(id=uuid.uuid4(), project_id=uuid.uuid4(),
                           zone_type="road" if mode == "not_boundary" else "site_boundary", geometry=None, properties={})
    project = FakeProject(id=zone.project_id, owner_id=uuid.uuid4() if mode == "unauthorized" else test_user.id)
    mock_db.execute = AsyncMock(side_effect=[scalar(test_user), scalar(zone), scalar(project), scalar(None)])
    fetch = AsyncMock(return_value={"source": "OpenStreetMap", "roads": [], "blockers": []})
    if mode == "unavailable": fetch.side_effect = httpx.ConnectError("offline")
    monkeypatch.setattr(site_zones, "fetch_public_road_context", fetch)
    monkeypatch.setattr(site_zones, "to_shape", lambda _: box(0, 0, .001, .001))
    response = await client.get(f"/api/v1/site-zones/{zone.id}/public-road-context", headers=auth_headers)
    assert response.status_code == {"success": 200, "unavailable": 503, "unauthorized": 403, "not_boundary": 400}[mode]
    if mode in {"unauthorized", "not_boundary"}: fetch.assert_not_awaited()
    mock_db.flush.assert_not_awaited()
    mock_db.refresh.assert_not_awaited()
