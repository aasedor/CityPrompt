"""Server-side address autocomplete and place resolution.

The frontend previously called Mapbox directly and discarded provider errors.
Keeping provider credentials and error handling here gives project creation a
single stable API while allowing the active Maps provider to change safely.
"""

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.config import get_settings


router = APIRouter()


class GeocodeSuggestion(BaseModel):
    id: str
    place_name: str


class GeocodeAutocompleteResponse(BaseModel):
    suggestions: list[GeocodeSuggestion]


class GeocodeResolveResponse(BaseModel):
    latitude: float
    longitude: float
    address: str


def _maps_api_key() -> str:
    settings = get_settings()
    return settings.google_maps_api_key or settings.gemini_api_key


def _provider_error(data: dict, fallback: str) -> HTTPException:
    message = str(data.get("error_message") or fallback).strip()
    return HTTPException(status_code=502, detail=message)


@router.get("/autocomplete", response_model=GeocodeAutocompleteResponse)
async def autocomplete_address(
    q: str = Query(..., min_length=3, max_length=200),
    limit: int = Query(5, ge=1, le=5),
):
    """Return ranked address/place suggestions for a partial user query."""
    api_key = _maps_api_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="Address search is not configured.")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/autocomplete/json",
                params={
                    "input": q.strip(),
                    "key": api_key,
                    "types": "geocode",
                },
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Address search timed out.") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Address search provider is unavailable.")

    data = response.json()
    status = data.get("status")
    if status == "ZERO_RESULTS":
        return GeocodeAutocompleteResponse(suggestions=[])
    if status != "OK":
        raise _provider_error(data, "Address search provider rejected the request.")

    predictions = data.get("predictions") or []
    suggestions = [
        GeocodeSuggestion(
            id=str(prediction["place_id"]),
            place_name=str(prediction["description"]),
        )
        for prediction in predictions[:limit]
        if prediction.get("place_id") and prediction.get("description")
    ]
    return GeocodeAutocompleteResponse(suggestions=suggestions)


@router.get("/resolve", response_model=GeocodeResolveResponse)
async def resolve_place(
    place_id: str = Query(..., min_length=1, max_length=300),
):
    """Resolve a selected autocomplete suggestion to map coordinates."""
    api_key = _maps_api_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="Address search is not configured.")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "formatted_address,geometry",
                    "key": api_key,
                },
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Address lookup timed out.") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Address lookup provider is unavailable.")

    data = response.json()
    if data.get("status") != "OK":
        raise _provider_error(data, "The selected address could not be resolved.")

    result = data.get("result") or {}
    location = (result.get("geometry") or {}).get("location") or {}
    if not result.get("formatted_address") or "lat" not in location or "lng" not in location:
        raise HTTPException(status_code=502, detail="Address lookup returned incomplete coordinates.")

    return GeocodeResolveResponse(
        latitude=float(location["lat"]),
        longitude=float(location["lng"]),
        address=str(result["formatted_address"]),
    )
