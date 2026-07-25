"""Verify Edmonton Open Data (Socrata) datasets before writing DatasetSpecs.

Do-not-retry discipline (the Calgary lesson): never hardcode Socrata resource
ids or geometry column names from memory. This script confirms each researched
resource's real columns via /api/views/{id}.json and runs a tiny spatial probe
against downtown Edmonton, so every spec in
backend/app/services/city_connector/cities/edmonton/ is written from verified
facts.

Usage:
    python scripts/verify_edmonton_datasets.py            # verify all targets
    python scripts/verify_edmonton_datasets.py --search "street centreline"
    python scripts/verify_edmonton_datasets.py --inspect fixa-tstc

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

DOMAIN = "data.edmonton.ca"
DISCOVERY = "https://api.us.socrata.com/api/catalog/v1"
TIMEOUT = 30

# Small polygon over downtown Edmonton (Jasper Ave / 101 St), lon lat per SODA WKT.
PROBE_WKT = (
    "POLYGON((-113.500 53.538, -113.487 53.538, -113.487 53.546, "
    "-113.500 53.546, -113.500 53.538))"
)

GEO_TYPES = {"point", "multipoint", "line", "multiline", "polygon", "multipolygon", "location"}

# Researched 2026-07-10 (web agents). resource_id None -> discover via search.
TARGETS = [
    {"key": "zoning_bylaw_20001", "search": "zoning bylaw geographical", "resource_id": "fixa-tstc"},
    {"key": "zoning_overlays", "search": "zoning overlays", "resource_id": "6w3s-58pv"},
    {"key": "property_assessment", "search": "property assessment current", "resource_id": "q7d6-ambg"},
    {"key": "property_information", "search": "property information current", "resource_id": "dkk9-cj3x"},
    {"key": "neighbourhoods", "search": "neighbourhoods", "resource_id": "65fr-66s6"},
    {"key": "roads", "search": "street centreline", "resource_id": None},
    {"key": "transit_stops", "search": "transit stops", "resource_id": "4vt2-8zrq"},
    {"key": "parks", "search": "parks", "resource_id": "gdd9-eqv9"},
    {"key": "trees", "search": "trees", "resource_id": "eecg-fc54"},
    {"key": "development_permits", "search": "development permits", "resource_id": "2ccn-pwtu"},
    {"key": "heritage", "search": "historic resources register", "resource_id": "jgsn-dhai"},
]


def _get(url: str) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": "cityprompt-dataset-verifier"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_catalog(query: str, limit: int = 8) -> list[dict]:
    params = urllib.parse.urlencode(
        {"domains": DOMAIN, "search_context": DOMAIN, "q": query, "only": "datasets", "limit": limit}
    )
    try:
        data = _get(f"{DISCOVERY}?{params}")
    except Exception as exc:  # noqa: BLE001
        print(f"  catalog search failed for {query!r}: {exc}")
        return []
    out = []
    for item in data.get("results", []):
        res = item.get("resource", {})
        out.append(
            {
                "id": res.get("id"),
                "name": res.get("name"),
                "updatedAt": res.get("updatedAt"),
                "description": (res.get("description") or "")[:140],
            }
        )
    return out


def view_metadata(resource_id: str) -> dict | None:
    try:
        meta = _get(f"https://{DOMAIN}/api/views/{resource_id}.json")
    except Exception as exc:  # noqa: BLE001
        print(f"  metadata fetch failed for {resource_id}: {exc}")
        return None
    cols = [
        {"fieldName": c.get("fieldName"), "dataTypeName": c.get("dataTypeName"), "name": c.get("name")}
        for c in meta.get("columns", [])
    ]
    geo_cols = [c for c in cols if (c["dataTypeName"] or "").lower() in GEO_TYPES]
    return {
        "id": resource_id,
        "name": meta.get("name"),
        "rowsUpdatedAt": meta.get("rowsUpdatedAt"),
        "columns": cols,
        "geo_columns": geo_cols,
    }


def spatial_probe(resource_id: str, geo_field: str) -> tuple[bool, str]:
    where = urllib.parse.quote(f"intersects({geo_field}, '{PROBE_WKT}')")
    url = f"https://{DOMAIN}/resource/{resource_id}.json?$where={where}&$limit=1"
    try:
        rows = _get(url)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return True, f"{len(rows)} row(s) in downtown probe"


def verify_target(target: dict) -> None:
    print(f"\n=== {target['key']} ===")
    rid = target["resource_id"]
    if rid is None:
        candidates = search_catalog(target["search"])
        if not candidates:
            print("  NO CANDIDATES FOUND")
            return
        print(f"  catalog candidates for {target['search']!r}:")
        for c in candidates:
            print(f"    {c['id']}  {c['name']}  (updated {c['updatedAt']})")
        for c in candidates[:4]:
            meta = view_metadata(c["id"])
            if not meta:
                continue
            geo = ", ".join(f"{g['fieldName']}:{g['dataTypeName']}" for g in meta["geo_columns"]) or "NO GEOMETRY"
            print(f"    -> {c['id']} geometry: {geo}")
            for g in meta["geo_columns"][:1]:
                ok, note = spatial_probe(c["id"], g["fieldName"])
                print(f"       probe intersects({g['fieldName']}): {'OK' if ok else 'FAIL'} - {note}")
    else:
        meta = view_metadata(rid)
        if not meta:
            print("  METADATA FETCH FAILED")
            return
        print(f"  {rid}: {meta['name']}")
        print("  columns:")
        for c in meta["columns"]:
            print(f"    {c['fieldName']:<30} {c['dataTypeName']}")
        if not meta["geo_columns"]:
            print("  NO GEOMETRY COLUMN")
            return
        for g in meta["geo_columns"]:
            ok, note = spatial_probe(rid, g["fieldName"])
            print(f"  probe intersects({g['fieldName']}): {'OK' if ok else 'FAIL'} - {note}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", help="ad-hoc catalog search instead of default targets")
    parser.add_argument("--inspect", help="inspect one resource id (columns + probe)")
    args = parser.parse_args()

    if args.search:
        for c in search_catalog(args.search, limit=15):
            print(f"{c['id']}  {c['name']}\n    {c['description']}")
        return
    if args.inspect:
        verify_target({"key": args.inspect, "search": "", "resource_id": args.inspect})
        return
    for target in TARGETS:
        verify_target(target)


if __name__ == "__main__":
    main()
