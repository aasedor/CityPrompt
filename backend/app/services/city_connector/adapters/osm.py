"""OSM adapter — the city-agnostic fallback.

Wraps the existing ``OSMContextFetcher`` (services/osm_context.py) so any city
without an open-data connector still produces roads / buildings / parks / water
DNA facts from OpenStreetMap. The spec's ``adapter_params``:

    category  REQUIRED — one of "buildings" | "roads" | "paths" | "water" | "parks"

The public Overpass API allows roughly one query at a time per IP and 429s
readily: all fetches in this process serialize behind a lock and retry once
with backoff. Size ``spec.timeout_s`` to cover queueing behind sibling
datasets, not just one query.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from shapely.geometry import Polygon, mapping

from app.services.city_connector.base import DatasetSpec, Feature, FetchStatus
from app.services.osm_context import OSMContextFetcher

logger = logging.getLogger(__name__)

_LINE_CATEGORIES = {"roads", "paths", "water"}
_PATH_ROAD_TYPES = {"footway", "path", "cycleway", "pedestrian", "bridleway", "steps"}
_QUERY_TIMEOUT_S = 30.0
_RATE_LIMIT_BACKOFF_S = 8.0

# One in-flight Overpass query per process — but asyncio.Lock binds to the
# event loop it first *waits* on, and Celery tasks each run a fresh loop via
# asyncio.run() in a long-lived worker child. A module-level Lock would raise
# "bound to a different event loop" on every build after the first. Keep a
# single-slot holder keyed by the running loop instead.
_overpass_lock_holder: tuple[asyncio.AbstractEventLoop, asyncio.Lock] | None = None


def _get_overpass_lock() -> asyncio.Lock:
    global _overpass_lock_holder
    loop = asyncio.get_running_loop()
    if _overpass_lock_holder is None or _overpass_lock_holder[0] is not loop:
        _overpass_lock_holder = (loop, asyncio.Lock())
    return _overpass_lock_holder[1]


async def fetch(
    spec: DatasetSpec, boundary_wgs84: Polygon
) -> tuple[list[Feature], FetchStatus, list[dict[str, Any]]]:
    from app.services.spatial_engine import buffer_wgs84

    category = spec.adapter_params["category"]
    # Analysis caps: the default 50/20 render-context caps would silently
    # undercount walkshed metrics on dense or park-rich sites.
    fetcher = OSMContextFetcher(
        timeout=min(spec.timeout_s, _QUERY_TIMEOUT_S),
        feature_caps={"buildings": 500, "roads": 500, "water": 100, "parks": 200},
    )
    # Metric-accurate envelope (the fetcher's own degree-averaged buffer is
    # ~18% short east-west at Calgary latitudes), so pass buffer_m=0 below.
    envelope = buffer_wgs84(boundary_wgs84, spec.buffer_m)

    async with _get_overpass_lock():
        try:
            context = await fetcher.fetch(envelope, buffer_m=0)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 429:
                raise
            logger.info("Overpass rate-limited; retrying %s in %.0fs", spec.id, _RATE_LIMIT_BACKOFF_S)
            await asyncio.sleep(_RATE_LIMIT_BACKOFF_S)
            context = await fetcher.fetch(envelope, buffer_m=0)

    features: list[Feature] = []
    source_category = "roads" if category == "paths" else category
    for item in context.get(source_category, []):
        if category == "paths" and item.get("road_type") not in _PATH_ROAD_TYPES:
            continue
        geometry = _coords_to_geometry(item.get("coordinates") or [], category)
        if geometry is None:
            continue
        props = {k: v for k, v in item.items() if k != "coordinates"}
        features.append({"geometry": geometry, "properties": props})

    return features, "ok", []


def _coords_to_geometry(coords: list[tuple[float, float]], category: str) -> dict[str, Any] | None:
    if len(coords) < 2:
        return None
    if category in _LINE_CATEGORIES or len(coords) < 3 or coords[0] != coords[-1]:
        # OSM ways for roads/waterways are open polylines
        if category not in _LINE_CATEGORIES and len(coords) >= 3:
            # Unclosed area way (buildings/parks are areas) — close the ring.
            try:
                return mapping(Polygon(coords))
            except Exception:  # noqa: BLE001
                return None
        return {"type": "LineString", "coordinates": [list(c) for c in coords]}
    try:
        return mapping(Polygon(coords))
    except Exception:  # noqa: BLE001
        return None
