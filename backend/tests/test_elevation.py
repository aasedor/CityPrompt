"""Elevation context must never mislabel renderer fallback heights as observations."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from pydantic import ValidationError

from app.api.v1 import elevation as endpoint


@pytest.fixture
def google(monkeypatch):
    monkeypatch.setattr(endpoint, "get_settings", lambda: SimpleNamespace(google_maps_api_key="fake-test-key", gemini_api_key=None))
    client = AsyncMock()
    client.__aenter__.return_value = client
    monkeypatch.setattr(endpoint.httpx, "AsyncClient", lambda **kwargs: client)
    return client


@pytest.mark.asyncio
async def test_google_elevation_exposes_msl_source_resolution_and_separate_approximate_ellipsoid(google):
    google.get.return_value = httpx.Response(200, json={"status": "OK", "results": [{"elevation": 1048.6, "resolution": 19.1}]})
    result = await endpoint.get_elevation(lat=51, lng=-114)
    assert result.elevation == 1048.6
    assert result.ellipsoidal_height == pytest.approx(1023.6)
    assert result.resolution == 19.1
    assert result.source == "google_elevation" and result.status == "available"
    assert result.vertical_reference == "mean_sea_level" and result.approximate is True
    assert result.unavailable_reason is None


@pytest.mark.asyncio
async def test_missing_key_preserves_renderer_contract_but_marks_it_unavailable(monkeypatch):
    monkeypatch.setattr(endpoint, "get_settings", lambda: SimpleNamespace(google_maps_api_key=None, gemini_api_key=None))
    def must_not_call(**kwargs):
        raise AssertionError("No provider request is allowed without a key")
    monkeypatch.setattr(endpoint.httpx, "AsyncClient", must_not_call)
    result = await endpoint.get_elevation(lat=51, lng=-114)
    assert (result.elevation, result.ellipsoidal_height, result.resolution) == (0, -25, 1000)
    assert result.status == "unavailable" and result.source == "renderer_fallback"
    assert result.unavailable_reason == "not_configured"


@pytest.mark.parametrize("error", [httpx.ConnectError("DNS failed"), httpx.ReadTimeout("Timed out"), httpx.RemoteProtocolError("Disconnected")])
@pytest.mark.asyncio
async def test_network_failures_return_explicit_unavailable_fallback(google, error):
    google.get.side_effect = error
    result = await endpoint.get_elevation(lat=51, lng=-114)
    assert result.elevation == 0 and result.status == "unavailable"
    assert result.unavailable_reason == "network_error"


@pytest.mark.parametrize("response, reason", [
    (httpx.Response(503), "provider_error"),
    (httpx.Response(200, json={"status": "REQUEST_DENIED", "error_message": "private provider detail"}), "provider_error"),
    (httpx.Response(200, content=b"not JSON"), "invalid_response"),
    (httpx.Response(200, json={"status": "OK", "results": []}), "invalid_response"),
    (httpx.Response(200, json={"status": "OK", "results": [{"elevation": True}]}), "invalid_response"),
    (httpx.Response(200, content=b'{"status":"OK","results":[{"elevation":NaN}]}'), "invalid_response"),
    (httpx.Response(200, json={"status": "OK", "results": [{"elevation": 10, "resolution": -5}]}), "invalid_response"),
])
@pytest.mark.asyncio
async def test_invalid_or_denied_provider_data_never_becomes_an_available_height(google, response, reason):
    google.get.return_value = response
    result = await endpoint.get_elevation(lat=51, lng=-114)
    assert result.status == "unavailable" and result.unavailable_reason == reason
    assert "private provider detail" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_zero_is_available_only_when_the_provider_really_returns_sea_level(google):
    google.get.return_value = httpx.Response(200, json={"status": "OK", "results": [{"elevation": 0}]})
    result = await endpoint.get_elevation(lat=0, lng=0)
    assert result.elevation == 0 and result.status == "available"
    assert result.source == "google_elevation" and result.resolution == 0


@pytest.mark.asyncio
async def test_batch_failure_marks_aligned_fallbacks_without_losing_renderer_values(google):
    google.get.side_effect = httpx.ConnectError("offline")
    result = await endpoint.get_elevation_batch(endpoint.BatchElevationRequest(points=[[-114, 51], [5, 50]]))
    assert result.elevations == [-25, 40]
    assert result.statuses == ["unavailable", "unavailable"]
    assert result.sources == ["renderer_fallback", "renderer_fallback"]


@pytest.mark.parametrize("point", [[-114], [-114, 51, 3], [181, 51], [-114, 91], [True, 51], [float("inf"), 51]])
def test_batch_rejects_invalid_coordinates_before_provider_requests(point):
    with pytest.raises(ValidationError):
        endpoint.BatchElevationRequest(points=[point])
