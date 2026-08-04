"""
OSM Context Fetcher — retrieves nearby OpenStreetMap features for a site boundary.

Takes a polygon, buffers it by ~50m, and queries the Overpass API for
buildings, roads, water, and parks within the buffered area.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Any

import httpx
from shapely.geometry import Polygon

logger = logging.getLogger(__name__)

METERS_PER_DEG_LAT = 111320
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def _meters_per_deg_lon(lat: float) -> float:
    return METERS_PER_DEG_LAT * abs(math.cos(math.radians(lat)))


def _buffer_polygon(polygon: Polygon, buffer_m: float = 50) -> Polygon:
    """Buffer a lat/lon polygon by approximate meters."""
    centroid = polygon.centroid
    lat = centroid.y
    buf_lat = buffer_m / METERS_PER_DEG_LAT
    buf_lon = buffer_m / _meters_per_deg_lon(lat)
    # Use average of lat/lon buffer for simplicity
    avg_buf = (buf_lat + buf_lon) / 2
    return polygon.buffer(avg_buf)


def _polygon_to_overpass_poly(polygon: Polygon) -> str:
    """Convert a Shapely polygon to Overpass poly: filter string.

    Overpass expects 'lat1 lon1 lat2 lon2 ...' (note: lat before lon).
    """
    coords = list(polygon.exterior.coords)
    parts = []
    for lon, lat in coords:
        parts.append(f"{lat} {lon}")
    return " ".join(parts)


def _parse_height(tags: dict[str, str]) -> float | None:
    """Parse building height from OSM tags."""
    raw = tags.get("height") or tags.get("building:height")
    if raw:
        try:
            return float(raw.replace("m", "").strip())
        except (ValueError, TypeError):
            pass
    levels = tags.get("building:levels")
    if levels:
        try:
            return float(levels) * 3.0
        except (ValueError, TypeError):
            pass
    return None


def _road_width(tags: dict[str, str]) -> float:
    """Estimate road width from OSM tags."""
    raw = tags.get("width")
    if raw:
        try:
            return float(raw.replace("m", "").strip())
        except (ValueError, TypeError):
            pass
    highway = tags.get("highway", "")
    widths = {
        "motorway": 14,
        "trunk": 12,
        "primary": 10,
        "secondary": 8,
        "tertiary": 7,
        "residential": 6,
        "service": 4,
        "footway": 2,
        "cycleway": 2,
        "path": 1.5,
    }
    return widths.get(highway, 6.0)


# Default caps keep the zone-properties payload small for the render-context
# flow. Analysis consumers (the Urban DNA connector) pass higher caps — 50
# buildings / 20 parks silently undercounts any dense-urban walkshed.
DEFAULT_FEATURE_CAPS = {"buildings": 50, "roads": 50, "water": 20, "parks": 20}


class OSMContextFetcher:
    """Fetches OSM features within a buffered polygon."""

    def __init__(self, timeout: float = 30.0, feature_caps: dict[str, int] | None = None):
        self.timeout = timeout
        self.feature_caps = {**DEFAULT_FEATURE_CAPS, **(feature_caps or {})}

    async def fetch(self, polygon: Polygon, buffer_m: float = 50) -> dict[str, Any]:
        """Fetch OSM features for the given polygon + buffer.

        Returns dict with keys: buildings, roads, water, parks, fetched_at, buffer_m
        """
        buffered = _buffer_polygon(polygon, buffer_m)
        poly_str = _polygon_to_overpass_poly(buffered)

        query = f"""
[out:json][timeout:{int(self.timeout)}];
(
  way["building"](poly:"{poly_str}");
  way["highway"](poly:"{poly_str}");
  way["natural"="water"](poly:"{poly_str}");
  relation["natural"="water"](poly:"{poly_str}");
  way["waterway"](poly:"{poly_str}");
  way["leisure"="park"](poly:"{poly_str}");
  relation["leisure"="park"](poly:"{poly_str}");
  way["landuse"="grass"](poly:"{poly_str}");
);
out body;
>;
out skel qt;
"""

        # overpass-api.de rejects default library User-Agents with 406.
        headers = {"User-Agent": "CityPrompt/1.0 (urban planning site context)"}
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            resp = await client.post(OVERPASS_URL, data={"data": query})
            resp.raise_for_status()
            data = resp.json()

        return self._parse_response(data, polygon)

    def _parse_response(self, data: dict[str, Any], original_polygon: Polygon) -> dict[str, Any]:
        """Parse Overpass JSON response into categorized feature lists."""
        elements = data.get("elements", [])

        # Build node lookup for resolving way geometries
        nodes: dict[int, tuple[float, float]] = {}
        for el in elements:
            if el["type"] == "node":
                nodes[el["id"]] = (el["lon"], el["lat"])

        buildings: list[dict[str, Any]] = []
        roads: list[dict[str, Any]] = []
        water: list[dict[str, Any]] = []
        parks: list[dict[str, Any]] = []

        for el in elements:
            if el["type"] != "way":
                continue
            tags = el.get("tags", {})
            node_ids = el.get("nodes", [])
            coords = [nodes[nid] for nid in node_ids if nid in nodes]
            if len(coords) < 2:
                continue

            if tags.get("building"):
                if len(coords) < 3:
                    continue
                height = _parse_height(tags)
                buildings.append(
                    {
                        "osm_id": el["id"],
                        "coordinates": coords,
                        "height_m": height,
                        "building_type": tags.get("building", "yes"),
                        "name": tags.get("name"),
                        "levels": tags.get("building:levels"),
                    }
                )
            elif tags.get("highway"):
                roads.append(
                    {
                        "osm_id": el["id"],
                        "coordinates": coords,
                        "width_m": _road_width(tags),
                        "road_type": tags.get("highway", "residential"),
                        "name": tags.get("name"),
                        "surface": tags.get("surface"),
                        "lanes": tags.get("lanes"),
                    }
                )
            elif tags.get("natural") == "water" or tags.get("waterway"):
                water.append(
                    {
                        "osm_id": el["id"],
                        "coordinates": coords,
                        "water_type": tags.get("waterway") or "water",
                        "name": tags.get("name"),
                    }
                )
            elif tags.get("leisure") == "park" or tags.get("landuse") == "grass":
                parks.append(
                    {
                        "osm_id": el["id"],
                        "coordinates": coords,
                        "park_type": tags.get("leisure") or tags.get("landuse", "park"),
                        "name": tags.get("name"),
                    }
                )

        logger.info(
            "OSM context fetched: %d buildings, %d roads, %d water, %d parks",
            len(buildings),
            len(roads),
            len(water),
            len(parks),
        )

        return {
            "buildings": buildings[: self.feature_caps["buildings"]],
            "roads": roads[: self.feature_caps["roads"]],
            "water": water[: self.feature_caps["water"]],
            "parks": parks[: self.feature_caps["parks"]],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "buffer_m": 50,
        }
