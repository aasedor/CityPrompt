import asyncio
from collections import OrderedDict
from types import SimpleNamespace

import httpx
import pytest
from shapely.geometry import box

from app.services import public_road_context
from app.services.osm_context import OSMContextFetcher


PRIMARY = "https://overpass-api.de/api/interpreter"
MIRROR = "https://overpass.private.coffee/api/interpreter"
SHAPE = box(-114.075, 51.051, -114.074, 51.052)
ELEMENTS = [
    {"type": "node", "id": 1, "lon": -114.075, "lat": 51.051},
    {"type": "node", "id": 2, "lon": -114.074, "lat": 51.051},
    {"type": "way", "id": 3, "nodes": [1, 2], "tags": {"highway": "residential", "name": "Mapped Road"}},
]


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    monkeypatch.setattr(public_road_context, "_context_cache", OrderedDict(), raising=False)


def mock_transport(monkeypatch, handler):
    client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: client(transport=httpx.MockTransport(handler), **kwargs))


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["timeout", "capacity", "partial", "invalid_json"])
async def test_transient_provider_failure_uses_one_read_only_mirror(monkeypatch, failure):
    requests = []

    def handle(request):
        requests.append(request)
        if len(requests) == 1:
            if failure == "timeout":
                raise httpx.ReadTimeout("provider unavailable", request=request)
            if failure == "capacity":
                return httpx.Response(503, text="Overpass at capacity")
            if failure == "partial":
                return httpx.Response(200, json={"elements": [], "remark": "runtime error: Query timed out"})
            return httpx.Response(200, text="<html>Temporary gateway failure</html>")
        return httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    result = await public_road_context.fetch_public_road_context(SHAPE)
    assert [str(request.url) for request in requests] == [PRIMARY, MIRROR]
    assert result["roads"] == [
        {"id": "osm:way:3", "label": "Mapped Road", "points": [(-114.075, 51.051), (-114.074, 51.051)], "widthM": 6}
    ]
    assert result["source"] == "OpenStreetMap"
    assert all(request.headers["User-Agent"].startswith("CityPrompt/") for request in requests)
    assert all(request.extensions["timeout"]["read"] == 8 for request in requests)


@pytest.mark.anyio
async def test_provider_permission_denial_is_not_retried_elsewhere(monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(403, text="Access denied")

    mock_transport(monkeypatch, handle)
    with pytest.raises(httpx.HTTPStatusError):
        await public_road_context.fetch_public_road_context(SHAPE)
    assert len(requests) == 1


@pytest.mark.anyio
async def test_slow_primary_body_yields_time_for_a_healthy_mirror(monkeypatch):
    class SlowBody(httpx.AsyncByteStream):
        async def __aiter__(self):
            # A server may keep each individual read below HTTPX's timeout
            # while the complete response exceeds the attempt's budget.
            for _ in range(12):
                await asyncio.sleep(0.01)
                yield b" "
            yield b'{"elements": []}'

    async def handle(request):
        if str(request.url) == PRIMARY:
            return httpx.Response(200, stream=SlowBody())
        return httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    fetcher = OSMContextFetcher(timeout=0.04, endpoints=(PRIMARY, MIRROR))
    result = await asyncio.wait_for(fetcher.fetch(SHAPE), timeout=0.5)
    assert result["provider_url"] == MIRROR
    assert result["roads"][0]["name"] == "Mapped Road"


@pytest.mark.anyio
async def test_success_is_cached_for_same_boundary_but_not_a_changed_boundary(monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    original = await public_road_context.fetch_public_road_context(SHAPE)
    cleared = await public_road_context.fetch_public_road_context(SHAPE, clear_inside=True)
    assert original["fetched_at"] == cleared["fetched_at"]
    assert len(requests) == 1
    await public_road_context.fetch_public_road_context(box(-114.076, 51.051, -114.074, 51.052))
    assert len(requests) == 2


@pytest.mark.anyio
async def test_failed_lookup_is_not_cached_and_a_retry_can_recover(monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(503) if len(requests) <= 2 else httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    with pytest.raises(httpx.HTTPStatusError):
        await public_road_context.fetch_public_road_context(SHAPE)
    result = await public_road_context.fetch_public_road_context(SHAPE)
    assert len(result["roads"]) == 1
    assert len(requests) == 3


@pytest.mark.anyio
async def test_cache_expires_after_ten_minutes(monkeypatch):
    requests = []
    now = [100.0]
    monkeypatch.setattr(public_road_context, "time", SimpleNamespace(monotonic=lambda: now[0]))

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    await public_road_context.fetch_public_road_context(SHAPE)
    now[0] = 699.0
    await public_road_context.fetch_public_road_context(SHAPE)
    assert len(requests) == 1
    now[0] = 700.0
    await public_road_context.fetch_public_road_context(SHAPE)
    assert len(requests) == 2


@pytest.mark.anyio
async def test_cache_evicts_old_boundaries_at_its_size_limit(monkeypatch):
    requests = []
    monkeypatch.setattr(public_road_context, "CONTEXT_CACHE_MAX_ENTRIES", 1)

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"elements": ELEMENTS})

    mock_transport(monkeypatch, handle)
    await public_road_context.fetch_public_road_context(SHAPE)
    await public_road_context.fetch_public_road_context(box(-114.076, 51.051, -114.074, 51.052))
    await public_road_context.fetch_public_road_context(SHAPE)
    assert len(requests) == 3
