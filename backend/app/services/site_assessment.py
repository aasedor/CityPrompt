"""Bounded Calgary assessments. Sum accounts once, never truncated UI details.

The published assessment includes improvements for LI properties. Intersecting
part of a property does not create an official assessment for that part; the
separate area-weighted figure is only a concept estimate.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import time
from collections import OrderedDict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from starlette.concurrency import run_in_threadpool

from app.services import spatial_engine as se

SOURCE_URL = "https://data.calgary.ca/dataset/Current-Year-Property-Assessments-Parcel-/4bsw-nn7w"
SOURCE_API = "https://data.calgary.ca/resource/4bsw-nn7w.json"
PAGE_SIZE = 1000
MAX_PAGES = 10
DETAIL_LIMIT = 200
CACHE_SECONDS = 3600
_cache: OrderedDict[str, tuple[float, dict]] = OrderedDict()
_pending: dict[str, asyncio.Task] = {}


class AssessmentError(ValueError):
    pass


def validate_boundary(site: Polygon) -> None:
    if not isinstance(site, Polygon) or site.is_empty or not site.is_valid:
        raise AssessmentError("Draw a valid site boundary without crossing edges.")
    if not all(math.isfinite(value) for value in site.bounds) or not box(-114.35, 50.8, -113.85, 51.22).covers(site):
        raise AssessmentError("Assessment data is currently available for Calgary sites.")
    if len(site.exterior.coords) > 1025 or not 0 < se.SiteFrame.from_wgs84(site).area_m2 <= 25_000_000:
        raise AssessmentError("Choose a site smaller than 25 km² to calculate assessments.")


def _money(value: Any) -> Decimal | None:
    try:
        amount = Decimal(str(value))
        return amount if amount.is_finite() and 0 <= amount < Decimal("1e15") else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def summarize_assessments(rows: list[dict], site: Polygon, *, truncated: bool = False) -> dict:
    """Identity is roll number + roll year; different accounts may share land."""
    validate_boundary(site)
    frame = se.SiteFrame.from_wgs84(site)
    accounts: dict[tuple[str, int], dict] = {}
    skipped = 0
    for row in rows:
        geometry = se.shape_of({"geometry": row.get("multipolygon")})
        if geometry is None or geometry.geom_type not in ("Polygon", "MultiPolygon"):
            skipped += 1
            continue
        metric = frame.to_metric(geometry)
        if metric.area <= 0 or metric.intersection(frame.site_m).area <= 0.01:
            continue
        roll = str(row.get("roll_number") or "").strip()
        try:
            year = int(row.get("roll_year"))
        except (ValueError, TypeError):
            skipped += 1
            continue
        if not roll or not 1900 <= year <= 2200:
            skipped += 1
            continue
        account = accounts.setdefault((roll, year), {"geometries": [], "values": set(), "row": row})
        account["geometries"].append(metric)
        amount = _money(row.get("assessed_value"))
        if amount is not None:
            account["values"].add(amount)
    years = {year for _, year in accounts}
    if len(years) > 1:
        raise AssessmentError("Calgary returned multiple assessment years. Retry before using a total.")

    full_total = Decimal(0)
    weighted_total = Decimal(0)
    missing = partial = 0
    records: list[dict] = []
    coverage = []
    for (roll, year), account in sorted(accounts.items()):
        geometry = unary_union(account["geometries"])
        overlap = geometry.intersection(frame.site_m)
        proportion = min(1.0, overlap.area / geometry.area)
        is_partial = proportion < 0.9999
        partial += int(is_partial)
        values = account["values"]
        amount = next(iter(values)) if len(values) == 1 else None
        if amount is None:
            missing += 1
        else:
            full_total += amount
            weighted_total += amount * Decimal(str(proportion))
        coverage.append(overlap)
        records.append({
            "roll_number": roll, "roll_year": year,
            "address": str(account["row"].get("address") or "Address not published")[:300],
            "property_type": account["row"].get("property_type"),
            "assessed_value": float(amount) if amount is not None else None,
            "overlap_pct": round(100 * proportion, 2),
            "partial": is_partial,
        })
    warnings = []
    if truncated:
        warnings.append("Calgary returned more than 10,000 records. These are incomplete subtotals; use a smaller site.")
    if skipped:
        warnings.append(f"{skipped} source records lacked usable geometry or account identity; totals may be incomplete.")
    if missing:
        warnings.append(f"{missing} properties have missing or conflicting values and are excluded from the subtotals.")
    if partial:
        warnings.append("Some properties extend beyond the site. Their full assessments include land outside your boundary.")
    return {
        "roll_year": next(iter(years)) if years else None,
        "property_count": len(records), "partial_property_count": partial,
        "missing_value_count": missing, "skipped_record_count": skipped,
        "complete": not (truncated or skipped or missing),
        "full_property_assessed_total": float(full_total),
        "area_weighted_estimate": float(weighted_total.quantize(Decimal("0.01"))),
        "assessed_coverage_pct": round(100 * unary_union(coverage).area / frame.area_m2, 2) if coverage else 0,
        "records": records[:DETAIL_LIMIT], "details_omitted": max(0, len(records) - DETAIL_LIMIT),
        "warnings": warnings, "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


async def _fetch(site: Polygon) -> dict:
    rows = []
    wkt = site.wkt
    # One deadline for the complete paginated lookup, rather than one per page.
    async with asyncio.timeout(45), httpx.AsyncClient(timeout=15) as client:
        for page in range(MAX_PAGES):
            response = await client.get(SOURCE_API, params={
                "$select": "multipolygon,roll_number,roll_year,address,assessed_value,property_type",
                "$where": f"intersects(multipolygon, '{wkt}')", "$order": ":id",
                "$limit": PAGE_SIZE, "$offset": page * PAGE_SIZE,
            })
            response.raise_for_status()
            if len(response.content) > 20 * 1024 * 1024:
                raise AssessmentError("This assessment lookup is too large. Use a smaller boundary.")
            payload = response.json()
            if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
                raise AssessmentError("Calgary returned an unexpected assessment response. Retry the lookup.")
            rows.extend(payload)
            if len(payload) < PAGE_SIZE:
                return await run_in_threadpool(summarize_assessments, rows, site)
    return await run_in_threadpool(summarize_assessments, rows, site, truncated=True)


async def get_site_assessment(site: Polygon) -> dict:
    validate_boundary(site)
    key = hashlib.sha256(site.wkb).hexdigest()
    cached = _cache.get(key)
    if cached and time.monotonic() - cached[0] < CACHE_SECONDS:
        _cache.move_to_end(key)
        return cached[1]
    if key not in _pending:
        async def load():
            try:
                result = await _fetch(site)
                _cache[key] = (time.monotonic(), result)
                _cache.move_to_end(key)
                while len(_cache) > 128:
                    _cache.popitem(last=False)
                return result
            finally:
                _pending.pop(key, None)
        task = asyncio.create_task(load())
        # A cancelled browser request must not cancel classmates' shared lookup.
        task.add_done_callback(lambda finished: finished.exception() if not finished.cancelled() else None)
        _pending[key] = task
    return await asyncio.shield(_pending[key])
