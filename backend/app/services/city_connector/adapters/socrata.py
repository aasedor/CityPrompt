"""Socrata (SODA) adapter — fetch-by-boundary with pagination.

Queries ``https://{domain}/resource/{id}.geojson`` with a spatial
``$where=intersects(geo_field, '<WKT>')`` filter built from the buffered site
boundary. Paginates with $limit/$offset so large sites never silently truncate
(a silent cap reads as "covered everything" when it didn't — worse than a
missing dataset). Requests carry the optional app token; without one Socrata
throttles aggressively.

The spec's ``adapter_params``:
    domain     (default "data.calgary.ca")
    geo_field  REQUIRED — verified geometry column (see scripts/verify_calgary_datasets.py)
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from shapely.geometry import Polygon

from app.core.config import get_settings
from app.services.city_connector.base import DatasetSpec, Feature, FetchStatus, note
from app.services.osm_context import _buffer_polygon

logger = logging.getLogger(__name__)

PAGE_SIZE = 2000
MAX_PAGES = 10  # 20k features is far beyond any buffered site envelope


def _boundary_wkt(boundary_wgs84: Polygon, buffer_m: float) -> str:
    """Buffered site boundary as SODA-compatible WKT (lon lat order, exterior ring only)."""
    buffered = _buffer_polygon(boundary_wgs84, buffer_m)
    # Simplify very detailed boundaries so the URL stays well under length limits.
    if len(buffered.exterior.coords) > 80:
        buffered = buffered.simplify(0.0001, preserve_topology=True)
    coords = ", ".join(f"{lon:.6f} {lat:.6f}" for lon, lat in buffered.exterior.coords)
    return f"POLYGON(({coords}))"


async def fetch(
    spec: DatasetSpec, boundary_wgs84: Polygon
) -> tuple[list[Feature], FetchStatus, list[dict[str, Any]]]:
    settings = get_settings()
    domain = spec.adapter_params.get("domain", "data.calgary.ca")
    geo_field = spec.adapter_params["geo_field"]
    wkt = _boundary_wkt(boundary_wgs84, spec.buffer_m)
    url = f"https://{domain}/resource/{spec.api_endpoint}.geojson"

    headers = {}
    app_token = getattr(settings, "calgary_socrata_app_token", "") or ""
    if app_token:
        headers["X-App-Token"] = app_token

    features: list[Feature] = []
    warnings: list[dict[str, Any]] = []
    status: FetchStatus = "ok"

    async with httpx.AsyncClient(timeout=spec.timeout_s, headers=headers) as client:
        for page in range(MAX_PAGES):
            params = {
                "$where": f"intersects({geo_field}, '{wkt}')",
                "$limit": str(PAGE_SIZE),
                "$offset": str(page * PAGE_SIZE),
            }
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            page_features = payload.get("features", [])
            for raw in page_features:
                features.append(_normalize_feature(raw, spec))
            if len(page_features) < PAGE_SIZE:
                break
        else:
            status = "partial"
            warnings.append(
                note(
                    "DATASET_TRUNCATED",
                    f"{spec.name} returned more than {PAGE_SIZE * MAX_PAGES} features; "
                    "results truncated — facts derived from this dataset may undercount.",
                )
            )

    logger.info("Socrata %s: %d features (%s)", spec.api_endpoint, len(features), status)
    return features, status, warnings


def _normalize_feature(raw: dict[str, Any], spec: DatasetSpec) -> Feature:
    props = dict(raw.get("properties") or {})
    for source, canonical in spec.field_map.items():
        if source in props:
            props[canonical] = props.pop(source)
    return {"geometry": raw.get("geometry"), "properties": props}
