"""City Connector — determines the current city and serves its datasets.

Adding a city: create cities/<city>/ with a connector subclass + DatasetSpecs,
then add its bounds here. Planning Agents never change (they consume DNA only).
"""

from __future__ import annotations

from shapely.geometry import Polygon

from app.services.city_connector.base import CityConnector
from app.services.city_connector.cities.calgary import CalgaryConnector
from app.services.city_connector.cities.osm_fallback import OSMFallbackConnector

# (lon_min, lat_min, lon_max, lat_max) — coarse municipal bounds for detection.
CITY_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "calgary": (-114.35, 50.80, -113.80, 51.25),
}

_CONNECTORS: dict[str, type[CityConnector]] = {
    "calgary": CalgaryConnector,
    "osm": OSMFallbackConnector,
}


def detect_city(lon: float, lat: float) -> str:
    for city_id, (lon_min, lat_min, lon_max, lat_max) in CITY_BOUNDS.items():
        if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
            return city_id
    return "osm"


def get_connector(city_id: str) -> CityConnector:
    connector_cls = _CONNECTORS.get(city_id, OSMFallbackConnector)
    return connector_cls()


def get_connector_for_site(site_polygon_wgs84: Polygon) -> CityConnector:
    centroid = site_polygon_wgs84.centroid
    return get_connector(detect_city(centroid.x, centroid.y))
