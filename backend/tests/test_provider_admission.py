"""Anonymous presentation reads must not become an unauthenticated paid proxy."""

from unittest.mock import AsyncMock

import pytest

from app.api.v1 import elevation, geocoding
from app.core.security import get_current_user, require_auth
from app.main import app


def test_oversized_batch_rejected_before_coordinate_iteration():
    from pydantic import ValidationError

    # Invalid inner values verify the cheap list-length check runs first.
    with pytest.raises(ValidationError, match="4000"):
        elevation.BatchElevationRequest(points=[None] * 4001)


@pytest.mark.asyncio
async def test_anonymous_address_search_never_calls_provider(client, monkeypatch):
    called = AsyncMock(side_effect=AssertionError("No anonymous provider call"))
    monkeypatch.setattr(geocoding.httpx, "AsyncClient", called)
    response = await client.get("/api/v1/geocoding/autocomplete", params={"q": "Calgary"})
    assert response.status_code == 401
    called.assert_not_called()


@pytest.mark.asyncio
async def test_anonymous_elevation_remains_available_as_explicit_fallback(client, monkeypatch):
    called = AsyncMock(side_effect=AssertionError("No anonymous provider call"))
    monkeypatch.setattr(elevation.httpx, "AsyncClient", called)
    response = await client.get("/api/v1/elevation", params={"lat": 51, "lng": -114})
    assert response.status_code == 200
    assert response.json()["source"] == "renderer_fallback"
    assert response.json()["unavailable_reason"] == "authentication_required"
    response = await client.post("/api/v1/elevation/batch", json={"points": [[-114, 51]]})
    assert response.status_code == 200
    assert response.json()["statuses"] == ["unavailable"]
    called.assert_not_called()


@pytest.mark.asyncio
async def test_authenticated_maps_budget_is_shared_and_precedes_provider(client, monkeypatch, test_user):
    from app.core import provider_limits

    app.dependency_overrides[require_auth] = lambda: test_user
    app.dependency_overrides[get_current_user] = lambda: test_user
    admit = AsyncMock(side_effect=provider_limits.HTTPException(429, "Quota reached"))
    monkeypatch.setattr(provider_limits, "enforce_rate_limit", admit)
    provider = AsyncMock(side_effect=AssertionError("No call over quota"))
    monkeypatch.setattr(elevation.httpx, "AsyncClient", provider)
    response = await client.get("/api/v1/elevation", params={"lat": 51, "lng": -114})
    assert response.status_code == 429
    provider.assert_not_called()
