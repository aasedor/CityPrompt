"""Opendatasoft (Explore API v2.1) adapter — fetch-by-boundary via exports.

Spatial fetches use ``/exports/geojson?where=intersects(geom, geom'<WKT>')`` —
the /records endpoint caps ``limit`` at 100/page and offset+limit at 10,000,
which is miserable for tree-scale datasets; exports streams the complete
filtered FeatureCollection (verified against opendata.vancouver.ca,
2026-07-11). Truncation is client-side (MAX_FEATURES) with the same
partial/DATASET_TRUNCATED semantics as the socrata adapter.

The spec's ``adapter_params``:
    domain     (default "opendata.vancouver.ca")
    geo_field  REQUIRED — always "geom" on Vancouver's portal; kept explicit
               for spec-sanity symmetry with the socrata adapter
    enrich     OPTIONAL attribute join onto fetched features (see _enrich):
        {
          "dataset":       tabular dataset slug,
          "local_key":     property on fetched features,
          "remote_key":    field on the enrich dataset,
          "prefix":        merged-property prefix, e.g. "tax_",
          "latest_field":  optional — restrict to the latest value of this
                           field (probed with order_by desc; e.g. report_year),
          "aggregations":  ODSQL select fragment, NUMERIC fields only — ODS
                           StatAggregation rejects text (verified live),
          "sample_fields": text fields sampled from raw rows (first non-null
                           per key, <=100 rows/batch — a designed sample),
          "batch_size":    keys per IN(...) query (default 40),
          "max_keys":      enrichment cap (default 300) -> JOIN_TRUNCATED,
        }
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from shapely.geometry import Polygon

from app.core.config import get_settings
from app.services.city_connector.adapters._geometry import boundary_wkt
from app.services.city_connector.base import DatasetSpec, Feature, FetchStatus, note

logger = logging.getLogger(__name__)

MAX_FEATURES = 20_000
RETRY_AFTER_S = 2.0  # single quota-backoff retry; the spec timeout governs overall

# API keys are per-portal; an unknown domain simply goes keyless (shared
# anonymous quota, 429 + X-RateLimit-* headers when exceeded).
_KEY_SETTING_BY_DOMAIN = {
    "opendata.vancouver.ca": "vancouver_ods_api_key",
}


def _api_base(domain: str) -> str:
    return f"https://{domain}/api/explore/v2.1/catalog/datasets"


def _headers(domain: str) -> dict[str, str]:
    settings = get_settings()
    key_setting = _KEY_SETTING_BY_DOMAIN.get(domain, "")
    api_key = (getattr(settings, key_setting, "") or "") if key_setting else ""
    return {"Authorization": f"Apikey {api_key}"} if api_key else {}


async def _get_with_quota_retry(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    response = await client.get(url, params=params)
    if response.status_code == 429:
        await asyncio.sleep(RETRY_AFTER_S)
        response = await client.get(url, params=params)
    response.raise_for_status()
    return response


async def fetch(spec: DatasetSpec, boundary_wgs84: Polygon) -> tuple[list[Feature], FetchStatus, list[dict[str, Any]]]:
    domain = spec.adapter_params.get("domain", "opendata.vancouver.ca")
    geo_field = spec.adapter_params["geo_field"]
    wkt = boundary_wkt(boundary_wgs84, spec.buffer_m)

    url = f"{_api_base(domain)}/{spec.api_endpoint}/exports/geojson"
    params = {"where": f"intersects({geo_field}, geom'{wkt}')"}

    features: list[Feature] = []
    warnings: list[dict[str, Any]] = []
    status: FetchStatus = "ok"

    async with httpx.AsyncClient(timeout=spec.timeout_s, headers=_headers(domain)) as client:
        try:
            response = await _get_with_quota_retry(client, url, params)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                return (
                    [],
                    "error",
                    [
                        note(
                            "RATE_LIMITED",
                            f"{spec.name}: {domain} daily API quota exhausted (429) — retry later or "
                            "configure an API key.",
                        )
                    ],
                )
            raise

        payload = response.json()
        raw_features = payload.get("features", [])
        if len(raw_features) > MAX_FEATURES:
            raw_features = raw_features[:MAX_FEATURES]
            status = "partial"
            warnings.append(
                note(
                    "DATASET_TRUNCATED",
                    f"{spec.name} returned more than {MAX_FEATURES} features; results truncated "
                    "— facts derived from this dataset may undercount.",
                )
            )
        for raw in raw_features:
            features.append(_normalize_feature(raw, spec))

        enrich = spec.adapter_params.get("enrich")
        if enrich and features:
            try:
                enrich_warnings = await _enrich(client, domain, features, enrich)
                warnings.extend(enrich_warnings)
            except Exception as exc:  # noqa: BLE001 — enrichment degrades, never fails the dataset
                logger.warning("ODS enrichment failed for %s: %s", spec.id, exc)
                warnings.append(
                    note(
                        "JOIN_FAILED",
                        f"{spec.name}: attribute enrichment from {enrich.get('dataset')} failed "
                        f"({exc}) — features carry geometry but no joined values.",
                    )
                )

    logger.info("ODS %s: %d features (%s)", spec.api_endpoint, len(features), status)
    return features, status, warnings


async def _enrich(
    client: httpx.AsyncClient, domain: str, features: list[Feature], cfg: dict[str, Any]
) -> list[dict[str, Any]]:
    """Batched IN(...) attribute join; merges values under cfg['prefix']."""
    records_url = f"{_api_base(domain)}/{cfg['dataset']}/records"
    local_key = cfg["local_key"]
    remote_key = cfg["remote_key"]
    prefix = cfg.get("prefix", "")
    batch_size = int(cfg.get("batch_size", 40))
    max_keys = int(cfg.get("max_keys", 300))
    warnings: list[dict[str, Any]] = []

    keys: list[str] = []
    seen: set[str] = set()
    for feature in features:
        value = (feature.get("properties") or {}).get(local_key)
        if value and value not in seen:
            seen.add(value)
            keys.append(str(value))
    if not keys:
        return warnings
    if len(keys) > max_keys:
        warnings.append(
            note(
                "JOIN_TRUNCATED",
                f"Attribute join capped at {max_keys} of {len(keys)} keys — joined values are "
                "missing for the remainder.",
            )
        )
        keys = keys[:max_keys]

    latest_clause = ""
    latest_field = cfg.get("latest_field")
    if latest_field:
        response = await _get_with_quota_retry(
            client,
            records_url,
            {"select": latest_field, "order_by": f"{latest_field} desc", "limit": 1},
        )
        results = response.json().get("results", [])
        latest = results[0].get(latest_field) if results else None
        if latest is not None:
            latest_clause = f' AND {latest_field} = "{latest}"'

    merged: dict[str, dict[str, Any]] = {}
    for start in range(0, len(keys), batch_size):
        batch = keys[start : start + batch_size]
        quoted = ", ".join(f'"{k}"' for k in batch)
        where = f"{remote_key} IN ({quoted}){latest_clause}"

        aggregations = cfg.get("aggregations")
        if aggregations:
            response = await _get_with_quota_retry(
                client,
                records_url,
                {
                    "select": f"{remote_key}, {aggregations}",
                    "where": where,
                    "group_by": remote_key,
                    "limit": min(100, len(batch)),
                },
            )
            for row in response.json().get("results", []):
                key = str(row.pop(remote_key, ""))
                if key:
                    merged.setdefault(key, {}).update(row)

        sample_fields = cfg.get("sample_fields")
        if sample_fields:
            response = await _get_with_quota_retry(
                client,
                records_url,
                {
                    "select": f"{remote_key}, {', '.join(sample_fields)}",
                    "where": where,
                    "limit": 100,
                },
            )
            for row in response.json().get("results", []):
                key = str(row.get(remote_key, ""))
                if not key:
                    continue
                bucket = merged.setdefault(key, {})
                for field in sample_fields:
                    if bucket.get(field) is None and row.get(field) is not None:
                        bucket[field] = row[field]

    matched = 0
    for feature in features:
        props = feature.get("properties") or {}
        values = merged.get(str(props.get(local_key, "")))
        if values:
            matched += 1
            for name, value in values.items():
                props[f"{prefix}{name}"] = value
    logger.info("ODS enrichment: %d/%d features matched from %s", matched, len(features), cfg["dataset"])
    return warnings


def _normalize_feature(raw: dict[str, Any], spec: DatasetSpec) -> Feature:
    props = dict(raw.get("properties") or {})
    for source, canonical in spec.field_map.items():
        if source in props:
            props[canonical] = props.pop(source)
    return {"geometry": raw.get("geometry"), "properties": props}
