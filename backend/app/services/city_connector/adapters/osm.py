"""OSM adapter — the city-agnostic fallback.

Wraps the existing ``OSMContextFetcher`` (services/osm_context.py) so any city
without an open-data connector still produces roads / buildings / parks / water
DNA facts from OpenStreetMap. The spec's ``adapter_params``:

    category  REQUIRED — one of "buildings" | "roads" | "water" | "parks"
"""

from __future__ import annotations

import logging
from typing import Any

from shapely.geometry import Polygon, mapping

from app.services.city_connector.base import DatasetSpec, Feature, FetchStatus
from app.services.osm_context import OSMContextFetcher

logger = logging.getLogger(__name__)

_LINE_CATEGORIES = {"roads", "water"}


async def fetch(
    spec: DatasetSpec, boundary_wgs84: Polygon
) -> tuple[list[Feature], FetchStatus, list[dict[str, Any]]]:
    category = spec.adapter_params["category"]
    fetcher = OSMContextFetcher(timeout=spec.timeout_s)
    context = await fetcher.fetch(boundary_wgs84, buffer_m=spec.buffer_m)

    features: list[Feature] = []
    for item in context.get(category, []):
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
