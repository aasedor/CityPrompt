"""Verify Vancouver Open Data (Opendatasoft) datasets before writing DatasetSpecs.

Do-not-retry discipline (the Calgary lesson): never hardcode dataset slugs or
field names from memory. This script confirms each researched dataset's real
fields via the Explore v2.1 catalog API, runs a spatial intersects() probe over
downtown Vancouver, exercises the exports/geojson endpoint the adapter uses,
and live-tests the property-tax-report IN(...) join, so every spec in
backend/app/services/city_connector/cities/vancouver/ is written from verified
facts.

Usage:
    python scripts/verify_vancouver_datasets.py             # verify all targets
    python scripts/verify_vancouver_datasets.py --inspect public-trees

Stdlib only so it runs outside the backend venv.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console crashes on non-ASCII otherwise

DOMAIN = "opendata.vancouver.ca"
API = f"https://{DOMAIN}/api/explore/v2.1/catalog/datasets"
TIMEOUT = 60

# Small polygon over downtown Vancouver (Robson/Burrard), lon lat order.
PROBE_WKT = (
    "POLYGON((-123.125 49.280, -123.115 49.280, -123.115 49.286, "
    "-123.125 49.286, -123.125 49.280))"
)

# Researched 2026-07-10 (web agents). geo=False -> tabular dataset (join target).
TARGETS = [
    {"slug": "zoning-districts-and-labels", "geo": True},
    {"slug": "property-parcel-polygons", "geo": True},
    {"slug": "property-tax-report", "geo": False},
    {"slug": "local-area-boundary", "geo": True},
    {"slug": "rapid-transit-stations", "geo": True},
    {"slug": "parks-polygon-representation", "geo": True},
    {"slug": "designated-floodplain", "geo": True},
    {"slug": "public-trees", "geo": True},
    {"slug": "heritage-sites", "geo": True},
    {"slug": "view-cones", "geo": True},
    {"slug": "issued-building-permits", "geo": True},
]


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "cityprompt-dataset-verifier"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def dataset_fields(slug: str) -> list[dict] | None:
    try:
        meta = _get(f"{API}/{slug}")
    except Exception as exc:  # noqa: BLE001
        print(f"  metadata fetch failed: {exc}")
        return None
    return [{"name": f.get("name"), "type": f.get("type")} for f in meta.get("fields", [])]


def records_probe(slug: str) -> None:
    where = urllib.parse.quote(f"intersects(geom, geom'{PROBE_WKT}')")
    try:
        data = _get(f"{API}/{slug}/records?where={where}&limit=1")
        print(f"  records intersects probe: OK - total_count={data.get('total_count')}")
    except Exception as exc:  # noqa: BLE001
        print(f"  records intersects probe: FAIL - {exc}")


def exports_probe(slug: str) -> int | None:
    """The adapter fetches exports/geojson — verify it honours the where filter."""
    where = urllib.parse.quote(f"intersects(geom, geom'{PROBE_WKT}')")
    try:
        data = _get(f"{API}/{slug}/exports/geojson?where={where}")
        count = len(data.get("features", []))
        print(f"  exports/geojson probe: OK - {count} features")
        return count
    except Exception as exc:  # noqa: BLE001
        print(f"  exports/geojson probe: FAIL - {exc}")
        return None


def tax_join_probe() -> None:
    """parcels.tax_coord -> property-tax-report.land_coordinate, 3 live keys."""
    where = urllib.parse.quote(f"intersects(geom, geom'{PROBE_WKT}')")
    try:
        parcels = _get(
            f"{API}/property-parcel-polygons/records?where={where}&select=tax_coord&limit=5"
        )
        keys = [r.get("tax_coord") for r in parcels.get("results", []) if r.get("tax_coord")]
    except Exception as exc:  # noqa: BLE001
        print(f"  parcel key fetch: FAIL - {exc}")
        return
    keys = sorted(set(keys))[:3]
    if not keys:
        print("  parcel key fetch: no tax_coord values in probe area")
        return
    print(f"  parcel keys: {keys}")
    quoted = ", ".join(f'"{k}"' for k in keys)
    where_in = urllib.parse.quote(f"land_coordinate IN ({quoted})")
    try:
        rows = _get(
            f"{API}/property-tax-report/records?where={where_in}"
            "&select=land_coordinate,current_land_value,current_improvement_value,year_built,zoning_district"
            "&limit=20"
        )
        print(f"  IN(...) join probe: OK - total_count={rows.get('total_count')}")
        for r in rows.get("results", [])[:3]:
            print(f"    {r}")
    except Exception as exc:  # noqa: BLE001
        print(f"  IN(...) join probe: FAIL - {exc}")


def verify_target(target: dict) -> None:
    slug = target["slug"]
    print(f"\n=== {slug} ===")
    fields = dataset_fields(slug)
    if fields is None:
        return
    for f in fields:
        print(f"    {f['name']:<32} {f['type']}")
    if target["geo"]:
        geo = [f for f in fields if f["type"] in ("geo_shape", "geo_point_2d")]
        if not any(f["name"] == "geom" for f in fields):
            print("  WARNING: no `geom` field — adapter assumption breaks here")
        print(f"  geo fields: {[f['name'] for f in geo]}")
        records_probe(slug)
        exports_probe(slug)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", help="inspect one dataset slug")
    args = parser.parse_args()

    if args.inspect:
        verify_target({"slug": args.inspect, "geo": True})
        return
    for target in TARGETS:
        verify_target(target)
    print("\n=== property-tax-report join ===")
    tax_join_probe()


if __name__ == "__main__":
    main()
