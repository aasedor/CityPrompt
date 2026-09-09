"""Keep editable polygon strips and semantic road centrelines synchronized."""

import math

from shapely.geometry import LineString


def prepare_road_update(update: dict, previous: dict | None = None) -> dict:
    previous = previous or {}
    props = {**previous, **(update.get("properties") or {})}
    if props.get("procedural_road") != 1:
        return update
    result = dict(update)
    coords = result.get("coordinates")
    explicit_line = (update.get("properties") or {}).get("plan_centerline")
    if coords and previous and explicit_line is None:
        ring = list(coords)
        if ring[0] == ring[-1]:
            ring.pop()
        if len(ring) < 4 or len(ring) % 2:
            raise ValueError("Procedural roads require paired strip vertices; edit the centreline instead")
        props["plan_centerline"] = [
            [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
            for a, b in zip(ring[: len(ring) // 2], reversed(ring[len(ring) // 2 :]))
        ]
    points = props.get("plan_centerline")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("Procedural road requires a centreline")
    if not all(
        isinstance(p, (list, tuple))
        and len(p) == 2
        and all(isinstance(v, (int, float)) and math.isfinite(v) for v in p)
        and -180 <= p[0] <= 180
        and -89 <= p[1] <= 89
        for p in points
    ):
        raise ValueError("Invalid road centreline coordinate")
    line = LineString(points)
    if not line.is_simple or line.length < 1e-10:
        raise ValueError("Road centreline must be simple and have positive length")
    width = float(props.get("width", 10))
    lanes = float(props.get("lane_count", 2))
    if not math.isfinite(lanes) or not 0 <= lanes <= 32:
        raise ValueError("Invalid lane count")
    semantic = str(props.get("road_archetype_id", "local"))
    if lanes and not any(t in semantic for t in ("path", "trail", "alley", "laneway", "cycleway")):
        width = max(width, lanes * 3.5)
    radius = float(props.get("corner_radius", 4))
    if not math.isfinite(width) or not 0 < width <= 200:
        raise ValueError("Road width must be between 0 and 200 metres")
    if not math.isfinite(radius) or not 0 <= radius <= 50:
        raise ValueError("Corner radius must be between 0 and 50 metres")
    # Same paired strip convention as the editor, but normals are calculated
    # in metres (angular dx/dy distort widths at Canadian latitudes).
    sx, sy = 111320 * math.cos(math.radians(points[0][1])), 111320
    left, right = [], []
    for i, p in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dx, dy = (b[0] - a[0]) * sx, (b[1] - a[1]) * sy
        length = math.hypot(dx, dy)
        if length < 1e-8:
            raise ValueError("Duplicate or reversing road station")
        ox, oy = -dy / length * width / 2 / sx, dx / length * width / 2 / sy
        left.append([p[0] + ox, p[1] + oy])
        right.append([p[0] - ox, p[1] - oy])
    result["coordinates"] = left + list(reversed(right))
    result["properties"] = props
    return result
