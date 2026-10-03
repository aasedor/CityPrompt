"""Revision-locked contact envelopes, separate from persisted compilation plots.

The packaged manifest mirrors the frontend policy. Unknown/custom geometry
retains its whole source polygon; clients cannot supply clearance dimensions.
"""

from functools import lru_cache
import json
import math
from pathlib import Path

from shapely.geometry import Polygon

MANIFEST = Path(__file__).resolve().parents[1] / "data/buildingPlacementEdges.json"


@lru_cache(maxsize=1)
def building_edge_contracts():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["schemaVersion"] != 1:
        raise ValueError("Unknown building contact schema")
    return {row["assetId"]: row for row in data["buildings"]}


def building_contact_geometry(zone, geometry):
    """Return the reviewed envelope, or the unchanged source polygon."""
    p = getattr(zone, "properties", None) or {}
    if (
        getattr(zone, "zone_type", None) not in ("building", "residential")
        or p.get("native_plot_axes") is not True
        or p.get("native_home_plot") is True
        or geometry.geom_type != "Polygon"
        or len(geometry.interiors)
    ):
        return geometry
    row = building_edge_contracts().get(p.get("pick_place_asset"))
    if (
        not row
        or p.get("development_selected_variant_id") != row["variantId"]
        or p.get("pick_place_model_revision") != row["revision"]
    ):
        return geometry
    ring = list(geometry.exterior.coords)[:-1]
    if len(ring) != 4:
        return geometry
    east = 111320 * math.cos(math.radians(ring[0][1]))
    vectors = [
        ((ring[(i + 1) % 4][0] - point[0]) * east, (ring[(i + 1) % 4][1] - point[1]) * 111320)
        for i, point in enumerate(ring)
    ]
    for i, v in enumerate(vectors):
        nxt, opposite = vectors[(i + 1) % 4], vectors[(i + 2) % 4]
        if (
            math.hypot(*v) < 0.01
            or abs(v[0] * nxt[0] + v[1] * nxt[1]) > math.hypot(*v) * math.hypot(*nxt) * 0.001
            or math.hypot(v[0] + opposite[0], v[1] + opposite[1]) > 0.01
        ):
            return geometry
    if vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0] <= 0:
        return geometry
    try:
        if p.get("development_height_override_m") is not None:
            program = row["storeyProgram"]
            floors = float(p.get("floor_count", p.get("floors", 0)))
            height = float(p["development_height_override_m"])
            if not program or not floors.is_integer() or not program["minStoreys"] <= floors <= program["maxStoreys"]:
                return geometry
            expected = round(
                program["podiumHeightM"]
                + (floors - program["podiumStoreys"]) * program["repeatedStoreyHeightM"]
                + program["roofHeightM"],
                2,
            )
            if not math.isfinite(height) or abs(height - expected) > 0.05:
                return geometry
        scale = float(p.get("building_footprint_scale", 1))
        footprint = row["footprintProgram"]
        if not math.isfinite(scale) or (footprint and not footprint["minScale"] <= scale <= footprint["maxScale"]):
            return geometry
        if scale != 1 and (not footprint or p.get("building_footprint_program_id") != footprint["id"]):
            return geometry
    except (TypeError, ValueError):
        return geometry
    fit = row.get("plotFit")
    if fit:
        w, d = math.hypot(*vectors[0]), math.hypot(*vectors[1])
        if not (
            fit["minWidthM"] - 0.01 <= w <= fit["maxWidthM"] + 0.01
            and fit["minDepthM"] - 0.01 <= d <= fit["maxDepthM"] + 0.01
        ):
            return geometry
        scale = round(min(round(w, 1) / row["nativeWidthM"], round(d, 1) / row["nativeDepthM"], fit["maxScale"]), 5)
    center = [sum(point[i] for point in ring) / 4 for i in (0, 1)]
    east = 111320 * math.cos(math.radians(center[1]))
    v = ((ring[1][0] - ring[0][0]) * east, (ring[1][1] - ring[0][1]) * 111320)
    width = math.hypot(*v)
    depth = math.hypot((ring[2][0] - ring[1][0]) * east, (ring[2][1] - ring[1][1]) * 111320)
    c, s = v[0] / width, v[1] / width
    native_width, native_depth = row["nativeWidthM"] * scale, row["nativeDepthM"] * scale
    left = -native_width / 2 if row["left"] == "abut" else -max(width, native_width) / 2
    right = native_width / 2 if row["right"] == "abut" else max(width, native_width) / 2
    front, rear = -native_depth / 2, max(depth, native_depth) / 2
    return Polygon(
        [
            (center[0] + (x * c - y * s) / east, center[1] + (x * s + y * c) / 111320)
            for x, y in ((left, front), (right, front), (right, rear), (left, rear))
        ]
    )
