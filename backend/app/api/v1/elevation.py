"""
Elevation API proxy — fetches terrain elevation from Google Elevation API.

Avoids exposing the Google API key to the frontend.
Returns terrain elevation and an estimated WGS84 ellipsoidal height.
"""

import math
from typing import Literal

import httpx
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, field_validator

from app.core.config import get_settings

router = APIRouter()


class ElevationResponse(BaseModel):
    elevation: float  # meters above sea level
    ellipsoidal_height: float  # estimated WGS84 ellipsoidal height
    resolution: float  # data resolution in meters
    status: Literal["available", "unavailable"]
    source: Literal["google_elevation", "renderer_fallback"]
    approximate: bool = True
    vertical_reference: Literal["mean_sea_level"] = "mean_sea_level"
    unavailable_reason: Literal["not_configured", "network_error", "provider_error", "invalid_response"] | None = None


class BatchElevationRequest(BaseModel):
    points: list[list[float]]  # [[lng, lat], ...]

    @field_validator("points", mode="before")
    @classmethod
    def valid_coordinates(cls, points):
        if not isinstance(points, list):
            raise ValueError("Points must be a list of longitude/latitude pairs.")
        for point in points:
            if not isinstance(point, (list, tuple)) or len(point) != 2 or not all(_finite_number(value) for value in point):
                raise ValueError("Each point must contain two finite longitude/latitude numbers.")
            if not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
                raise ValueError("Coordinates must be within longitude/latitude bounds.")
        return points


class BatchElevationResponse(BaseModel):
    elevations: list[float]  # WGS84 ellipsoidal heights, aligned with input points
    statuses: list[Literal["available", "unavailable"]]
    sources: list[Literal["google_elevation", "renderer_fallback"]]


def _finite_number(value) -> bool:
    try:
        return not isinstance(value, bool) and isinstance(value, (float, int)) and math.isfinite(value)
    except OverflowError:
        return False


def _unavailable(lat: float, lng: float, reason: str) -> ElevationResponse:
    # These numbers are compatibility defaults for existing renderers. The
    # explicit metadata prevents them from being presented as measured data.
    return ElevationResponse(elevation=0, ellipsoidal_height=estimate_geoid_undulation(lat, lng),
                             resolution=1000, status="unavailable", source="renderer_fallback",
                             unavailable_reason=reason)


async def _google_results(client: httpx.AsyncClient, locations: str, api_key: str, count: int):
    try:
        response = await client.get("https://maps.googleapis.com/maps/api/elevation/json",
                                    params={"locations": locations, "key": api_key})
    except httpx.RequestError:
        return None, "network_error"
    if response.status_code != 200:
        return None, "provider_error"
    try:
        data = response.json()
    except ValueError:
        return None, "invalid_response"
    if not isinstance(data, dict):
        return None, "invalid_response"
    if data.get("status") != "OK":
        return None, "provider_error"
    results = data.get("results")
    if not isinstance(results, list) or len(results) != count:
        return None, "invalid_response"
    for result in results:
        if not isinstance(result, dict) or not _finite_number(result.get("elevation")):
            return None, "invalid_response"
        resolution = result.get("resolution", 0)
        if not _finite_number(resolution) or resolution < 0:
            return None, "invalid_response"
    return results, None


# Approximate geoid undulations for quick lookup
# In production, use a geoid model (EGM96/EGM2008)
# These are rough values for major regions
GEOID_UNDULATIONS = {
    # (lat_min, lat_max, lng_min, lng_max): undulation_meters
    # North America
    (25, 55, -130, -60): -25,
    # Europe
    (35, 70, -15, 45): 40,
    # East Asia
    (20, 50, 100, 150): -10,
    # Australia
    (-45, -10, 110, 155): -5,
    # South America
    (-55, 15, -80, -35): -15,
    # Africa
    (-35, 35, -20, 55): 20,
}


def estimate_geoid_undulation(lat: float, lng: float) -> float:
    """Rough geoid undulation estimate. Returns meters."""
    for (lat_min, lat_max, lng_min, lng_max), undulation in GEOID_UNDULATIONS.items():
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return undulation
    return 0  # Default: assume geoid ≈ ellipsoid


@router.get("", response_model=ElevationResponse)
async def get_elevation(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Get terrain elevation at a lat/lng coordinate.

    Returns both elevation above sea level and estimated WGS84 ellipsoidal height.
    """
    s = get_settings()
    # Prefer dedicated Maps key, fallback to Gemini key
    api_key = s.google_maps_api_key or s.gemini_api_key
    if not api_key:
        return _unavailable(lat, lng, "not_configured")
    async with httpx.AsyncClient(timeout=10.0) as client:
        results, reason = await _google_results(client, f"{lat},{lng}", api_key, 1)
    if results is None:
        return _unavailable(lat, lng, reason)
    result = results[0]
    elevation_msl = result["elevation"]
    return ElevationResponse(elevation=elevation_msl,
                             ellipsoidal_height=elevation_msl + estimate_geoid_undulation(lat, lng),
                             resolution=result.get("resolution", 0), status="available", source="google_elevation")


@router.post("/batch", response_model=BatchElevationResponse)
async def get_elevation_batch(body: BatchElevationRequest):
    """Bare-earth ellipsoidal heights for many [lng, lat] points in one call.

    Used to drape imported vector layers onto smooth ground (no canopy / no
    photogrammetry noise). Chunks into Google Elevation API requests (<=512
    locations each) and returns one height per input point, in order.
    """
    points = body.points
    if not points:
        return BatchElevationResponse(elevations=[], statuses=[], sources=[])
    if len(points) > 4000:
        raise HTTPException(status_code=400, detail="Too many points (max 4000).")

    s = get_settings()
    api_key = s.google_maps_api_key or s.gemini_api_key
    if not api_key:
        # No key: best-effort flat geoid so callers degrade rather than fail.
        return BatchElevationResponse(elevations=[estimate_geoid_undulation(lat, lng) for lng, lat in points],
                                      statuses=["unavailable"] * len(points), sources=["renderer_fallback"] * len(points))

    chunk_size = 250  # keep the GET URL well under length limits
    elevations: list[float] = []
    statuses: list[Literal["available", "unavailable"]] = []
    sources: list[Literal["google_elevation", "renderer_fallback"]] = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        for start in range(0, len(points), chunk_size):
            chunk = points[start : start + chunk_size]
            locations = "|".join(f"{lat},{lng}" for lng, lat in chunk)
            results, _ = await _google_results(client, locations, api_key, len(chunk))
            if results is None:
                # Degrade this chunk to geoid estimates rather than abort the import.
                elevations.extend(estimate_geoid_undulation(lat, lng) for lng, lat in chunk)
                statuses.extend(["unavailable"] * len(chunk))
                sources.extend(["renderer_fallback"] * len(chunk))
                continue
            for (lng, lat), result in zip(chunk, results):
                elevations.append(result["elevation"] + estimate_geoid_undulation(lat, lng))
                statuses.append("available")
                sources.append("google_elevation")

    return BatchElevationResponse(elevations=elevations, statuses=statuses, sources=sources)
