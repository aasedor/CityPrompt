"""
Elevation API proxy — fetches terrain elevation from Google Elevation API.

Avoids exposing the Google API key to the frontend.
Returns terrain elevation and an estimated WGS84 ellipsoidal height.
"""

import httpx
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()


class ElevationResponse(BaseModel):
    elevation: float  # meters above sea level
    ellipsoidal_height: float  # estimated WGS84 ellipsoidal height
    resolution: float  # data resolution in meters


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
    # Try Google Elevation API first
    s = get_settings()
    # Prefer dedicated Maps key, fallback to Gemini key
    api_key = s.google_maps_api_key or s.gemini_api_key
    if not api_key:
        # Fallback: no elevation API key configured
        geoid = estimate_geoid_undulation(lat, lng)
        return ElevationResponse(
            elevation=0,
            ellipsoidal_height=geoid,
            resolution=1000,
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://maps.googleapis.com/maps/api/elevation/json",
                params={
                    "locations": f"{lat},{lng}",
                    "key": api_key,
                },
            )

        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Elevation API error")

        data = resp.json()
        if data.get("status") != "OK" or not data.get("results"):
            # API might not have Elevation API enabled — use fallback
            geoid = estimate_geoid_undulation(lat, lng)
            return ElevationResponse(
                elevation=0,
                ellipsoidal_height=geoid,
                resolution=1000,
            )

        result = data["results"][0]
        elevation_msl = result["elevation"]  # meters above sea level
        resolution = result.get("resolution", 0)

        # Compute estimated ellipsoidal height:
        # h ≈ H + N
        # h: ellipsoidal height, H: orthometric (MSL) elevation, N: geoid undulation
        geoid = estimate_geoid_undulation(lat, lng)
        ellipsoidal_height = elevation_msl + geoid

        return ElevationResponse(
            elevation=elevation_msl,
            ellipsoidal_height=ellipsoidal_height,
            resolution=resolution,
        )

    except httpx.TimeoutException:
        # Timeout fallback
        geoid = estimate_geoid_undulation(lat, lng)
        return ElevationResponse(
            elevation=0,
            ellipsoidal_height=geoid,
            resolution=1000,
        )
