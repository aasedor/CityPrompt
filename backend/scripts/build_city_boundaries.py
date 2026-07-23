"""Build simplified municipal boundary polygons for two-tier city detection.

detect_city() prefilters on a coarse lon/lat bbox, then confirms against the
polygons this script generates — metro-adjacent suburbs (Chestermere, Burnaby,
Mississauga, St. Albert...) sit inside the coarse boxes but outside the
municipality, and misrouting them to a city connector returns empty datasets
instead of the OSM fallback's roads/buildings/parks.

Run INSIDE the backend container (needs shapely + pyproj via app.services);
the generated GeoJSONs are committed to the repo:
    docker exec -w /app devplatform-backend python scripts/build_city_boundaries.py
    docker exec -w /app devplatform-backend python scripts/build_city_boundaries.py --city vancouver

Each boundary is buffered outward BUFFER_M before simplification so an
edge-of-city site is never false-negatived by vertex reduction, then
simplified to <= MAX_VERTICES. Regenerate after annexations.

Sources (researched + verified 2026-07-10):
    calgary    data.calgary.ca — discovered via Socrata catalog search
    edmonton   data.edmonton.ca resource qqvh-dp5m (City Corporate Boundary)
    vancouver  opendata.vancouver.ca local-area-boundary (22 planning areas,
               unioned — the city-boundary dataset is a MultiLineString)
    toronto    open.toronto.ca CKAN package regional-municipal-boundary
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, ".")  # allow `app.` imports when run from /app

from shapely.geometry import mapping, shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely.validation import make_valid  # noqa: E402

from app.services.spatial_engine import buffer_wgs84  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path("app/services/city_connector/boundaries")
BUFFER_M = 150.0
MAX_VERTICES = 2000
TIMEOUT = 60

# Sanity probes printed after generation: downtown must be inside, metro-adjacent
# suburbs (inside the coarse detection bbox!) must be outside. These same points
# are pinned in backend/tests/test_city_boundaries.py.
PROBES: dict[str, dict[str, list[tuple[float, float]]]] = {
    "calgary": {
        "inside": [(-114.07, 51.045)],
        "outside": [(-113.82, 51.04)],  # Chestermere
    },
    "edmonton": {
        "inside": [(-113.49, 53.54)],
        "outside": [(-113.63, 53.63), (-113.28, 53.52)],  # St. Albert, Sherwood Park
    },
    "vancouver": {
        "inside": [(-123.12, 49.28)],
        "outside": [(-123.24, 49.26), (-123.07, 49.31)],  # UBC/UEL, North Vancouver
    },
    "toronto": {
        "inside": [(-79.38, 43.65)],
        "outside": [(-79.64, 43.59), (-79.51, 43.84)],  # Mississauga, Vaughan
    },
}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "cityprompt-boundary-builder"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _features_union(collection: dict):
    geoms = []
    for feature in collection.get("features", []):
        geometry = feature.get("geometry")
        if not geometry:
            continue
        geom = shape(geometry)
        if not geom.is_valid:
            geom = make_valid(geom)
        if geom.is_empty or geom.geom_type not in ("Polygon", "MultiPolygon", "GeometryCollection"):
            continue
        geoms.append(geom)
    if not geoms:
        raise RuntimeError("no polygonal features in source")
    union = unary_union(geoms)
    if union.geom_type == "GeometryCollection":
        union = unary_union([g for g in union.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    return union


def fetch_calgary():
    """Discover the Calgary city-boundary dataset — never hardcode ids from memory."""
    params = urllib.parse.urlencode({
        "domains": "data.calgary.ca", "search_context": "data.calgary.ca",
        "q": "city boundary", "only": "datasets", "limit": 10,
    })
    catalog = _get_json(f"https://api.us.socrata.com/api/catalog/v1?{params}")
    for item in catalog.get("results", []):
        res = item.get("resource", {})
        name = (res.get("name") or "").lower()
        if "boundary" not in name or any(word in name for word in ("ward", "community", "school")):
            continue
        rid = res.get("id")
        try:
            collection = _get_json(f"https://data.calgary.ca/resource/{rid}.geojson?$limit=50")
            union = _features_union(collection)
        except Exception as exc:  # noqa: BLE001 — try the next candidate
            print(f"  candidate {rid} ({res.get('name')!r}) unusable: {exc}")
            continue
        print(f"  calgary source: {res.get('name')!r} ({rid})")
        return union, f"data.calgary.ca/{rid}"
    raise RuntimeError("no usable Calgary boundary dataset found via catalog search")


def fetch_edmonton():
    collection = _get_json("https://data.edmonton.ca/resource/qqvh-dp5m.geojson?$limit=50")
    return _features_union(collection), "data.edmonton.ca/qqvh-dp5m"


def fetch_vancouver():
    collection = _get_json(
        "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/"
        "local-area-boundary/exports/geojson"
    )
    union = _features_union(collection)
    return union, "opendata.vancouver.ca/local-area-boundary (union of 22 areas)"


def fetch_toronto():
    # regional-municipal-boundary ships SHP only (probed 2026-07-11); the union of
    # the six former municipalities is the same city boundary, with WGS84 GeoJSON.
    package = _get_json(
        "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
        "?id=former-municipality-boundaries"
    )
    resources = package["result"]["resources"]
    candidates = [
        r for r in resources
        if "geojson" in (r.get("format") or "").lower() and "4326" in (r.get("name") or "")
    ]
    if not candidates:
        raise RuntimeError(f"no 4326 GeoJSON resource: {[r.get('name') for r in resources]}")
    url = candidates[0]["url"]
    print(f"  toronto source resource: {candidates[0].get('name')!r}")
    return (
        _features_union(_get_json(url)),
        "open.toronto.ca/former-municipality-boundaries (union of 6, WGS84)",
    )


FETCHERS = {
    "calgary": fetch_calgary,
    "edmonton": fetch_edmonton,
    "vancouver": fetch_vancouver,
    "toronto": fetch_toronto,
}


def _vertex_count(geom) -> int:
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return sum(
        len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors) for p in polys
    )


def build(city_id: str) -> None:
    print(f"{city_id}:")
    union, source = FETCHERS[city_id]()
    buffered = buffer_wgs84(union, BUFFER_M)
    simplified = buffered
    tolerance = 0.0001
    for _ in range(8):
        if _vertex_count(simplified) <= MAX_VERTICES:
            break
        simplified = buffered.simplify(tolerance, preserve_topology=True)
        tolerance *= 2
    if not simplified.is_valid:
        simplified = make_valid(simplified)

    feature = {
        "type": "Feature",
        "properties": {
            "city_id": city_id,
            "source": source,
            "generated": date.today().isoformat(),
            "buffer_m": BUFFER_M,
            "vertices": _vertex_count(simplified),
        },
        "geometry": mapping(simplified),
    }
    out_path = OUT_DIR / f"{city_id}.geojson"
    out_path.write_text(json.dumps(feature), encoding="utf-8")
    print(f"  wrote {out_path} ({out_path.stat().st_size / 1024:.0f} KB, "
          f"{_vertex_count(simplified)} vertices)")

    from shapely.geometry import Point  # local import keeps top import-light

    for label, expected in (("inside", True), ("outside", False)):
        for lon, lat in PROBES[city_id][label]:
            actual = simplified.contains(Point(lon, lat))
            status = "ok" if actual == expected else "!!! MISMATCH"
            print(f"  probe {label} ({lon}, {lat}): contains={actual} [{status}]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", choices=[*FETCHERS, "all"], default="all")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cities = list(FETCHERS) if args.city == "all" else [args.city]
    failures = []
    for city_id in cities:
        try:
            build(city_id)
        except Exception as exc:  # noqa: BLE001 — report and continue; partial output is fine
            print(f"  FAILED: {exc}")
            failures.append(city_id)
    if failures:
        print(f"\nFailed cities: {failures}")
        sys.exit(1)


if __name__ == "__main__":
    main()
