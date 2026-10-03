"""Read-only, bounded map context for optional conceptual street connections."""

import math
from shapely.geometry import Polygon

from app.services.osm_context import OSMContextFetcher


def eligible_public_road(road: dict) -> bool:
    tags = road.get("connection_tags")
    if not isinstance(tags, dict) or road.get("geometry_complete") is not True:
        return False
    if tags.get("highway") not in {"residential", "unclassified", "tertiary", "secondary", "living_street"}:
        return False
    if any(":conditional" in key for key in tags):
        return False
    if any(
        str(tags.get(key, "yes")).lower() not in {"yes", "designated", "permissive"}
        for key in ["access", "vehicle", "motor_vehicle"]
    ):
        return False
    if any(str(tags.get(key, "no")).lower() not in {"no", "false", "0"} for key in ["bridge", "tunnel"]):
        return False
    if str(tags.get("layer", "0")) != "0":
        return False
    width = road.get("width_m")
    return isinstance(width, (int, float)) and math.isfinite(width) and 3 <= width <= 20


async def fetch_public_road_context(shape, clear_inside: bool = False):
    minx, miny, maxx, maxy = shape.bounds
    if (
        abs(shape.centroid.y) > 80
        or (maxx - minx) * 111320 * math.cos(math.radians(shape.centroid.y)) > 1500
        or (maxy - miny) * 111320 > 1500
    ):
        raise ValueError(
            "Automatic connections support sites up to 1.5 km across. Position a connection manually for this site."
        )
    data = await OSMContextFetcher(
        timeout=25, feature_caps={"roads": 500, "buildings": 500, "water": 100, "parks": 100}
    ).fetch(shape)
    if data.get("truncated"):
        raise ValueError("Nearby map data is too dense for automatic connections. Position a connection manually.")
    blockers = []
    for building in data.get("buildings", []):
        coordinates = building["coordinates"]
        if len(coordinates) < 3:
            continue
        polygon = Polygon(coordinates)
        if not polygon.is_valid:
            # Conservative envelope for incomplete/invalid map footprints.
            polygon = polygon.envelope
        outside = polygon.difference(shape) if clear_inside else polygon
        parts = [outside] if outside.geom_type == "Polygon" else getattr(outside, "geoms", [])
        blockers.extend(
            [list(part.exterior.coords) for part in parts if part.geom_type == "Polygon" and not part.is_empty]
        )
    blockers += [
        w["coordinates"]
        for w in data.get("water", [])
        if len(w["coordinates"]) >= 4 and w["coordinates"][0] == w["coordinates"][-1]
    ]
    return {
        "source": "OpenStreetMap",
        "fetched_at": data.get("fetched_at"),
        "blockers": blockers,
        "roads": [
            {
                "id": f"osm:way:{r['osm_id']}",
                "label": r.get("name") or "Mapped public street",
                "points": r["coordinates"],
                "widthM": r["width_m"],
            }
            for r in data.get("roads", [])
            if eligible_public_road(r)
        ],
    }
