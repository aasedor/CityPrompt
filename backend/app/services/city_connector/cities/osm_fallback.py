"""OSM fallback connector — any city outside the registered CITY_BOUNDS.

Produces a reduced-but-honest DNA from OpenStreetMap alone: road hierarchy and
frontage, nearby building context, and parks. Everything Calgary-only (zoning,
parcels, policy plans, transit) simply never appears in ``capabilities()``, so
the DNA builder marks those fields missing and Planning Agents hedge — the same
code path as a Calgary dataset timeout. That is the multi-city story.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import Polygon

from app.services import spatial_engine as se
from app.services.city_connector.base import CityConnector, DatasetSpec, Feature, note


def _props(feature: Feature) -> dict[str, Any]:
    return feature.get("properties") or {}


def _roads(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    if not features:
        return {}, [note("ROADS_EMPTY", "No OSM roads found near the site.")]

    hierarchy = se.length_within_by(
        frame, features, lambda f: _props(f).get("road_type") or "unclassified", radius_m=200.0
    )
    fronting = se.frontage(frame, features, tolerance_m=25.0)
    seen: set[str] = set()
    frontage_streets = []
    for feature, shared_m in fronting:
        name = _props(feature).get("name") or "unnamed"
        if name in seen:
            continue
        seen.add(name)
        frontage_streets.append(
            {
                "name": name,
                "ctp_class": None,
                "street_type": _props(feature).get("road_type"),
                "one_way": None,
                "frontage_m": shared_m,
            }
        )
    named = [s for s in frontage_streets if s["name"] != "unnamed"]
    return {
        "mobility.road_hierarchy": hierarchy,
        "mobility.frontage_streets": frontage_streets[:12],
        "site.corner_site": len(named) >= 2,
    }, []


def _buildings(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    if not features:
        return {}, [note("BUILDINGS_EMPTY", "No OSM buildings found near the site.", severity="info")]
    heights = [h for h in (_props(f).get("height_m") for f in features) if h]
    return {
        "built_form.context_building_count": se.count_within(frame, features, 200.0),
        "built_form.context_avg_height_m": round(sum(heights) / len(heights), 1) if heights else None,
    }, []


def _parks(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    if not features:
        return {}, [note("PARKS_EMPTY", "No OSM parks found near the site.", severity="info")]
    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        nearest_fact = {
            "name": _props(feature).get("name"),
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }
    return {
        "public_realm.parks_within_800m": se.count_within(frame, features, 800.0),
        "public_realm.nearest_park": nearest_fact,
    }, []


class OSMFallbackConnector(CityConnector):
    city_id = "osm"
    display_name = "OpenStreetMap (generic)"


OSMFallbackConnector.register(
    DatasetSpec(
        id="osm.roads",
        name="OSM Roads",
        priority=1,
        geometry_type="line",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "roads"},
        dna_fields=("mobility.road_hierarchy", "mobility.frontage_streets", "site.corner_site"),
        transform=_roads,
        buffer_m=220.0,
    )
)

OSMFallbackConnector.register(
    DatasetSpec(
        id="osm.buildings",
        name="OSM Buildings",
        priority=2,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "buildings"},
        dna_fields=("built_form.context_building_count", "built_form.context_avg_height_m"),
        transform=_buildings,
        buffer_m=220.0,
        confidence_weight=0.6,
    )
)

OSMFallbackConnector.register(
    DatasetSpec(
        id="osm.parks",
        name="OSM Parks",
        priority=3,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "parks"},
        dna_fields=("public_realm.parks_within_800m", "public_realm.nearest_park"),
        transform=_parks,
        buffer_m=850.0,
        confidence_weight=0.6,
    )
)
