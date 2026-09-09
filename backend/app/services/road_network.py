"""Deterministic editable road topology, independent of planner/LEGO contracts.

All kernel coordinates and design parameters are metres. Parent IDs never change.
The graph is a derived, content-addressed snapshot of persisted source lines; it
is not inferred by the renderer. Unchanged junction solutions are reused.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math

from shapely.geometry import LineString, Point, Polygon, box, mapping, shape
from shapely.ops import substring, transform, unary_union

EPS = 1e-6


@dataclass(frozen=True)
class Road:
    id: str
    centerline: tuple[tuple[float, float], ...]
    width: float = 10
    level: str = "0"  # explicit grade layer, NOT terrain altitude
    profile_id: str = "local"
    corner_radius: float = 4
    sidewalk_width: float = 0
    median_width: float = 0


def identity(prefix, value):
    return prefix + sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:20]


def point_key(point, level):
    return (level, round(point.x, 6), round(point.y, 6))


def points_of(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "Point":
        return [geometry]
    if geometry.geom_type == "LineString":
        return [Point(geometry.coords[0]), Point(geometry.coords[-1])]
    return [p for part in getattr(geometry, "geoms", []) for p in points_of(part)]


@lru_cache(maxsize=2048)
def resolve_intersection(approaches_json: str, radius: float):
    """Round re-entrant envelope corners with a metric morphological closing.

    Operates relative to the node so moving an unchanged junction reuses its
    solution. Flat approach caps are restored by intersection with a support
    hull. Radius is configurable per node via the contributing road settings.
    """
    approaches = json.loads(approaches_json)
    envelopes = [LineString(a["line"]).buffer(a["width"] / 2, cap_style=2) for a in approaches]
    raw = unary_union(envelopes)
    rounded = raw.buffer(radius, resolution=12).buffer(-radius, resolution=12) if radius else raw
    return rounded.union(raw).intersection(raw.convex_hull)


def build_network(roads: tuple[Road, ...], snap_tolerance: float = 1.5):
    """Only rebuild spatially affected components; retain bounded source caches.

    Bounds include surface/corner influence as well as snapping, so nearby
    unconnected roads still participate in surface ownership.
    """
    if not math.isfinite(snap_tolerance) or not 0 <= snap_tolerance <= 20:
        raise ValueError("snap tolerance must be between 0 and 20 metres")
    roads = tuple(sorted(roads, key=lambda r: r.id))
    if len({r.id for r in roads}) != len(roads):
        raise ValueError("duplicate parent road ID")
    groups = []
    bounds = []
    for road in roads:
        if not road.centerline or not all(math.isfinite(v) for p in road.centerline for v in p):
            raise ValueError("invalid centreline")
        if not all(math.isfinite(v) for v in (road.width, road.corner_radius, snap_tolerance)):
            raise ValueError("non-finite design parameter")
        bounds.append(
            box(*LineString(road.centerline).bounds).buffer(
                max(road.width * 2 + road.corner_radius * 2, snap_tolerance)
            )
        )
    remaining = set(range(len(roads)))
    while remaining:
        group = {min(remaining)}
        remaining -= group
        pending = list(group)
        while pending:
            i = pending.pop()
            neighbors = {j for j in remaining if roads[i].level == roads[j].level and bounds[i].intersects(bounds[j])}
            remaining -= neighbors
            group |= neighbors
            pending.extend(sorted(neighbors))
        groups.append(tuple(roads[i] for i in sorted(group)))
    result = dict(version=1, nodes=[], edges=[], intersections=[], warnings=[])
    for group in groups:
        component = _cached_component(group, snap_tolerance)
        for key in ("nodes", "edges", "intersections", "warnings"):
            # The WGS84 adapter rewrites IDs; never expose mutable cached data.
            result[key].extend(json.loads(json.dumps(component[key])))
    return result


@lru_cache(maxsize=128)
def _cached_component(roads: tuple[Road, ...], snap_tolerance: float = 1.5):
    if not math.isfinite(snap_tolerance) or not 0 <= snap_tolerance <= 20:
        raise ValueError("snap tolerance must be between 0 and 20 metres")
    roads = tuple(sorted(roads, key=lambda r: r.id))
    if len({r.id for r in roads}) != len(roads):
        raise ValueError("duplicate parent road ID")
    lines = {}
    for road in roads:
        if not all(math.isfinite(v) for p in road.centerline for v in p):
            raise ValueError("non-finite road coordinate")
        if not math.isfinite(road.width) or not 0 < road.width <= 200:
            raise ValueError("road width must be positive and at most 200 metres")
        if not math.isfinite(road.corner_radius) or not 0 <= road.corner_radius <= 50:
            raise ValueError("corner radius must be between 0 and 50 metres")
        line = LineString(road.centerline)
        if line.length <= EPS or not line.is_simple:
            raise ValueError("road must be a nonzero simple polyline")
        lines[road.id] = line
    # Move only terminal vertices, never internal curve stations. Stable order
    # and nearest-distance/ID tie breaking prevent input-order dependent snaps.
    for road in roads:
        coords = list(lines[road.id].coords)
        for index in (0, -1):
            point = Point(coords[index])
            candidates = []
            for other in roads:
                if other.id == road.id or other.level != road.level:
                    continue
                target = lines[other.id]
                projected = target.interpolate(target.project(point))
                candidates.append((point.distance(projected), other.id, projected))
            if candidates:
                distance, _, projected = min(candidates, key=lambda c: c[:2])
                if distance <= snap_tolerance:
                    coords[index] = projected.coords[0]
        candidate = LineString(coords)
        if candidate.length > EPS and candidate.is_simple:
            lines[road.id] = candidate
    cuts = {r.id: [0.0, lines[r.id].length] for r in roads}
    warnings = []
    for i, a in enumerate(roads):
        for b in roads[i + 1 :]:
            if a.level != b.level:
                continue
            crossing = lines[a.id].intersection(lines[b.id])
            if crossing.length > EPS:
                warnings.append(f"Collinear overlap: {a.id}, {b.id}; duplicate approaches retained")
            for point in points_of(crossing):
                cuts[a.id].append(lines[a.id].project(point))
                cuts[b.id].append(lines[b.id].project(point))
    nodes, edges = {}, []
    for road in roads:
        stations = []
        for station in sorted(cuts[road.id]):
            if not stations or station - stations[-1] > EPS:
                stations.append(station)
        for start, end in zip(stations, stations[1:]):
            line = substring(lines[road.id], start, end)
            ends = []
            for point in (Point(line.coords[0]), Point(line.coords[-1])):
                key = point_key(point, road.level)
                node_id = identity("node-", key)
                nodes.setdefault(
                    node_id, dict(id=node_id, location=[point.x, point.y], level=road.level, connectedEdgeIds=[])
                )
                ends.append(node_id)
            edge_id = identity("edge-", [road.id, *ends])
            edge = dict(
                id=edge_id,
                parentRoadId=road.id,
                startNodeId=ends[0],
                endNodeId=ends[1],
                centerline=mapping(line),
                width=road.width,
                level=road.level,
                roadProfileId=road.profile_id,
                cornerRadius=road.corner_radius,
                sidewalkWidth=road.sidewalk_width,
                medianWidth=road.median_width,
            )
            edges.append(edge)
            for node_id in ends:
                nodes[node_id]["connectedEdgeIds"].append(edge_id)
    by_id = {e["id"]: e for e in edges}
    junctions = []
    for node in nodes.values():
        degree = len(node["connectedEdgeIds"])
        node["nodeType"] = {1: "dead_end", 2: "continuation", 3: "t_intersection", 4: "four_way"}.get(
            degree, "multi_leg"
        )
        node["intersectionId"] = None
        approaches = []
        max_width = max(by_id[e]["width"] for e in node["connectedEdgeIds"])
        radius = max(by_id[e]["cornerRadius"] for e in node["connectedEdgeIds"])
        x, y = node["location"]
        for edge_id in node["connectedEdgeIds"]:
            edge = by_id[edge_id]
            coords = list(shape(edge["centerline"]).coords)
            if edge["endNodeId"] == node["id"]:
                coords.reverse()
            line = LineString(coords)
            dx, dy = coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            # Reserve space for both ends of very short connecting edges.
            reach = min(line.length * 0.45, max_width * 2 + radius * 2)
            stub = substring(line, 0, reach)
            tip = stub.coords[-1]
            left = [tip[0] - dy * edge["width"] / 2, tip[1] + dx * edge["width"] / 2]
            right = [tip[0] + dy * edge["width"] / 2, tip[1] - dx * edge["width"] / 2]
            approaches.append(
                dict(
                    roadEdgeId=edge_id,
                    parentRoadId=edge["parentRoadId"],
                    direction=[dx, dy],
                    angle=math.atan2(dy, dx) % math.tau,
                    width=edge["width"],
                    roadProfileId=edge["roadProfileId"],
                    sidewalkWidth=edge["sidewalkWidth"],
                    medianWidth=edge["medianWidth"],
                    leftBoundary=left,
                    rightBoundary=right,
                    stopLineCandidate=[left, right],
                    crossingCandidate=[left, right],
                    terminationDistance=reach,
                    line=[[p[0] - x, p[1] - y] for p in stub.coords],
                )
            )
        approaches.sort(key=lambda a: (a["angle"], a["roadEdgeId"]))
        node["approachAngles"] = [a["angle"] for a in approaches]
        if degree == 2:
            separation = abs(approaches[0]["angle"] - approaches[1]["angle"])
            node["nodeType"] = "continuation" if abs(separation - math.pi) < math.radians(15) else "bend"
        if degree < 3 and node["nodeType"] != "bend":
            continue
        local = resolve_intersection(
            json.dumps(
                [{"line": [[round(v, 6) for v in p] for p in a["line"]], "width": a["width"]} for a in approaches],
                sort_keys=True,
            ),
            radius,
        )
        surface = transform(lambda px, py, z=None: (px + x, py + y), local)
        iid = "intersection-" + node["id"]
        node["intersectionId"] = iid
        junctions.append(
            dict(
                id=iid,
                nodeId=node["id"],
                type="STANDARD",
                level=node["level"],
                geometrySettings={"cornerRadius": radius},
                approaches=approaches,
                generatedGeometry=mapping(surface),
            )
        )
    # Partition close junction footprints at their perpendicular bisector.
    # This gives each point one owner without merging semantic nodes.
    for junction in junctions:
        node = nodes[junction["nodeId"]]
        x, y = node["location"]
        surface = shape(junction["generatedGeometry"])
        for other in junctions:
            if other is junction or other["level"] != junction["level"]:
                continue
            ox, oy = nodes[other["nodeId"]]["location"]
            dx, dy = ox - x, oy - y
            distance = math.hypot(dx, dy)
            dx, dy = dx / distance, dy / distance
            mx, my = (x + ox) / 2, (y + oy) / 2
            extent = max(1000, surface.length * 4 + distance * 2)
            half = Polygon(
                [
                    (mx - dy * extent, my + dx * extent),
                    (mx + dy * extent, my - dx * extent),
                    (mx + dy * extent - dx * extent, my - dx * extent - dy * extent),
                    (mx - dy * extent - dx * extent, my + dx * extent - dy * extent),
                ]
            )
            surface = surface.intersection(half)
        junction["generatedGeometry"] = mapping(surface)
        mouths = unary_union([LineString(a["stopLineCandidate"]).buffer(1e-5) for a in junction["approaches"]])
        junction["curbGeometry"] = mapping(surface.boundary.difference(mouths))
    masks = {
        r.level: unary_union([shape(j["generatedGeometry"]) for j in junctions if j["level"] == r.level]) for r in roads
    }
    owned = {}
    for edge in edges:
        envelope = shape(edge["centerline"]).buffer(edge["width"] / 2, cap_style=2)
        edge["envelope"] = mapping(envelope)
        surface = envelope.difference(masks[edge["level"]])
        if edge["level"] in owned:
            surface = surface.difference(owned[edge["level"]])
        owned[edge["level"]] = unary_union([owned.get(edge["level"], Polygon()), surface])
        edge["geometry"] = mapping(surface)
    return dict(version=1, nodes=list(nodes.values()), edges=edges, intersections=junctions, warnings=warnings)


@lru_cache(maxsize=32)
def network_snapshot(source_json: str):
    """WGS84 zone adapter. Explicit opt-in avoids rewriting clipped plan roads."""
    sources = json.loads(source_json)
    eligible = [s for s in sources if s.get("properties", {}).get("procedural_road") == 1]
    if not eligible:
        return dict(
            version=1,
            nodes=[],
            edges=[],
            intersections=[],
            warnings=[],
            features={"type": "FeatureCollection", "features": []},
        )
    origin = eligible[0]["properties"]["plan_centerline"][0]
    sx, sy = 111320 * math.cos(math.radians(origin[1])), 111320
    if abs(sx) < 1000:
        raise ValueError("polar road networks are not supported")
    roads = []
    for source in eligible:
        props = source["properties"]
        coords = props["plan_centerline"]
        if not all(len(p) == 2 and -180 <= p[0] <= 180 and -90 <= p[1] <= 90 for p in coords):
            raise ValueError("invalid WGS84 centreline")
        width = float(props.get("width", 10))
        lanes = float(props.get("lane_count", 2))
        semantic = str(props.get("road_archetype_id", "local"))
        if lanes and not any(token in semantic for token in ("path", "trail", "alley", "laneway", "cycleway")):
            width = max(width, lanes * 3.5)
        roads.append(
            Road(
                source["id"],
                tuple(((p[0] - origin[0]) * sx, (p[1] - origin[1]) * sy) for p in coords),
                width,
                str(props.get("road_level", 0)),
                semantic,
                float(props.get("corner_radius", 4)),
                float(props.get("sidewalk_width", 0)),
                float(props.get("median_width", 0)),
            )
        )
    result = build_network(tuple(roads))
    # Public identities are geographic, independent of the temporary metric
    # origin (which may change when the first parent road is deleted/moved).
    node_ids = {
        n["id"]: identity(
            "node-",
            [n["level"], round(origin[0] + n["location"][0] / sx, 9), round(origin[1] + n["location"][1] / sy, 9)],
        )
        for n in result["nodes"]
    }
    edge_ids = {
        e["id"]: identity("edge-", [e["parentRoadId"], node_ids[e["startNodeId"]], node_ids[e["endNodeId"]]])
        for e in result["edges"]
    }
    for n in result["nodes"]:
        n["id"] = node_ids[n["id"]]
        n["connectedEdgeIds"] = [edge_ids[e] for e in n["connectedEdgeIds"]]
        if n["intersectionId"]:
            n["intersectionId"] = "intersection-" + n["id"]
    for e in result["edges"]:
        e.update(id=edge_ids[e["id"]], startNodeId=node_ids[e["startNodeId"]], endNodeId=node_ids[e["endNodeId"]])
    for j in result["intersections"]:
        j["nodeId"] = node_ids[j["nodeId"]]
        j["id"] = "intersection-" + j["nodeId"]
        for a in j["approaches"]:
            a["roadEdgeId"] = edge_ids[a["roadEdgeId"]]

    def geographic(geometry):
        return mapping(transform(lambda x, y, z=None: (origin[0] + x / sx, origin[1] + y / sy), shape(geometry)))

    features = []

    def feature(geometry, kind, **props):
        features.append(dict(type="Feature", geometry=geographic(geometry), properties=dict(kind=kind, **props)))

    for node in result["nodes"]:
        feature(mapping(Point(node["location"])), "node", id=node["id"], nodeType=node["nodeType"])
    for edge in result["edges"]:
        for key, kind in (("centerline", "edge"), ("envelope", "envelope"), ("geometry", "road_surface")):
            feature(edge[key], kind, id=edge["id"], parentRoadId=edge["parentRoadId"])
    for junction in result["intersections"]:
        parent = junction["approaches"][0]["parentRoadId"]
        feature(junction["generatedGeometry"], "intersection", id=junction["id"], parentRoadId=parent)
        for approach in junction["approaches"]:
            x, y = next(n["location"] for n in result["nodes"] if n["id"] == junction["nodeId"])
            dx, dy = approach["direction"]
            feature(mapping(LineString([(x, y), (x + dx * 8, y + dy * 8)])), "approach", id=approach["roadEdgeId"])
    result["features"] = dict(type="FeatureCollection", features=features)
    result["metricFrame"] = dict(origin=origin, metersPerDegree=[sx, sy])
    return result
