from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.api.v1 import geocoding


def provider_response(payload: dict, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def mock_provider(monkeypatch, payload: dict, status_code: int = 200):
    response = provider_response(payload, status_code)

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def get(self, *args, **kwargs):
            return response

    monkeypatch.setattr(geocoding.httpx, "AsyncClient", MockAsyncClient)


@pytest.mark.asyncio
async def test_autocomplete_returns_ranked_google_predictions(client, monkeypatch):
    monkeypatch.setattr(
        geocoding,
        "get_settings",
        lambda: SimpleNamespace(google_maps_api_key="maps-key", gemini_api_key=""),
    )
    mock_provider(monkeypatch, {
        "status": "OK",
        "predictions": [
            {"place_id": "place-1", "description": "2448 31 Ave SW, Calgary, AB, Canada"},
            {"place_id": "place-2", "description": "2448 31 Ave NW, Edmonton, AB, Canada"},
        ],
    })

    response = await client.get("/api/v1/geocoding/autocomplete", params={"q": "2448 31"})

    assert response.status_code == 200
    assert response.json() == {
        "suggestions": [
            {"id": "place-1", "place_name": "2448 31 Ave SW, Calgary, AB, Canada"},
            {"id": "place-2", "place_name": "2448 31 Ave NW, Edmonton, AB, Canada"},
        ]
    }


@pytest.mark.asyncio
async def test_resolve_returns_coordinates_for_selected_place(client, monkeypatch):
    monkeypatch.setattr(
        geocoding,
        "get_settings",
        lambda: SimpleNamespace(google_maps_api_key="maps-key", gemini_api_key=""),
    )
    mock_provider(monkeypatch, {
        "status": "OK",
        "result": {
            "formatted_address": "2448 31 Ave SW, Calgary, AB T2T 1T8, Canada",
            "geometry": {"location": {"lat": 51.0260594, "lng": -114.1169517}},
        },
    })

    response = await client.get("/api/v1/geocoding/resolve", params={"place_id": "place-1"})

    assert response.status_code == 200
    assert response.json() == {
        "latitude": 51.0260594,
        "longitude": -114.1169517,
        "address": "2448 31 Ave SW, Calgary, AB T2T 1T8, Canada",
    }


@pytest.mark.asyncio
async def test_autocomplete_surfaces_provider_rejection(client, monkeypatch):
    monkeypatch.setattr(
        geocoding,
        "get_settings",
        lambda: SimpleNamespace(google_maps_api_key="maps-key", gemini_api_key=""),
    )
    mock_provider(monkeypatch, {
        "status": "REQUEST_DENIED",
        "error_message": "Places API is not enabled.",
    })

    response = await client.get("/api/v1/geocoding/autocomplete", params={"q": "2448 31"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Places API is not enabled."
