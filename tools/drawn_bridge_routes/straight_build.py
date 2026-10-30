"""Derive bridge-owned, closed straight-span modules from five locked GLBs.

No source bytes, application files or catalogue entries are modified. Output is
an external review handoff. Every source intersection is explicit and capped;
the retained glTF material dictionaries are copied verbatim after export.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from shapely.geometry import Polygon
import trimesh

from .build_timber import ROOT, _clip, _preserve_source_materials, canonical_bytes, sha256
from .straight_specs import SPECS

EPS = 1e-5
KIND_ORDER = ("bridge_left_end", "bridge_main", "bridge_right_end")
OWNERSHIP_FILE = ROOT / "backend/app/data/public_realm_ownership_contracts.json"


def _normalized_matrix(spec):
    """Temporary right-handed frame: X along, Y up, Z across."""
    if spec["frame"] == "authoring-y":
        return np.array([[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    if spec["frame"] == "tied-heading-only":
        a = math.radians(13)
        return np.array([[math.cos(a), 0, -math.sin(a), 0], [0, 1, 0, 0],
                         [math.sin(a), 0, math.cos(a), 0], [0, 0, 0, 1]], float)
    return np.eye(4)


def _deduplicate_internal_faces(mesh):
    """Remove both copies of coincident source sweep cell interfaces."""
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    _, inverse, counts = np.unique(np.sort(mesh.faces, axis=1), axis=0, return_inverse=True, return_counts=True)
    removed = int(np.sum(counts[inverse] > 1))
    mesh.update_faces(counts[inverse] == 1)
    mesh.remove_unreferenced_vertices()
    return removed


def _vertex_parts(mesh):
    """Group through non-manifold contacts to recognize source assemblies."""
    edge = mesh.edges
    graph = coo_matrix((np.ones(len(edge)), (edge[:, 0], edge[:, 1])), shape=(len(mesh.vertices), len(mesh.vertices)))
    count, labels = connected_components(graph, directed=False)
    face_labels = labels[mesh.faces[:, 0]]
    return [mesh.submesh([np.flatnonzero(face_labels == index)], append=True, repair=False) for index in range(count)]


def _solidify_planar(piece, depth=.001):
    """Give a source joint surface inward relief, retaining its front polygon."""
    piece.remove_unreferenced_vertices()
    _, singular, basis = np.linalg.svd(piece.vertices - piece.vertices.mean(axis=0), full_matrices=False)
    if singular[-1] > 2e-5:
        raise ValueError("Only planar source decorations may receive thin relief")
    normal = basis[-1]
    if np.dot(normal, piece.face_normals[0]) < 0:
        normal *= -1
    vertices = np.vstack((piece.vertices, piece.vertices - normal * depth))
    # The source planar joint is a convex rectangle/triangle; no foliage is cut.
    result = trimesh.convex.convex_hull(vertices)
    if not result.is_watertight:
        raise ValueError("Source decoration relief did not close")
    return result


def _box(bounds):
    bounds = np.asarray(bounds, float)
    mesh = trimesh.creation.box(extents=bounds[1] - bounds[0])
    mesh.apply_translation(bounds.mean(axis=0))
    return mesh


def _brick_carrier():
    """Exact rectangular carrier cells from family_viaduct.py.

    The source merged wall has coincident interior caps with inconsistent
    triangulation, so it cannot be split as closed solids. Its curved spandrels
    are separate closed source components and are never substituted here.
    """
    for across in (-4.5, 4.5):
        yield _box([[-42.3, 7.2, across - .5], [123, 9.8, across + .5]])
    centres = [-36.9 + 8.2 * index for index in range(20)]
    solid = [(-42.3, centres[0] - 3)]
    solid += [(a + 3, b - 3) for a, b in zip(centres, centres[1:])]
    solid += [(centres[-1] + 3, 123)]
    for low, high in solid:
        yield _box([[low, 0, -5], [high, 7.2, 5]])


def _prism(support):
    mesh = trimesh.creation.extrude_polygon(Polygon(support["polygon"]), support["top"] - support["bottom"], engine="earcut")
    mesh.vertices = np.column_stack((mesh.vertices[:, 0], mesh.vertices[:, 2] + support["bottom"], -mesh.vertices[:, 1]))
    # Blender X/Y/Z -> along/up/across is a right-handed rotation.
    return mesh


def _source_pieces(style, source, spec, contract):
    """Yield material, stable source-piece label, closed temporary-frame mesh."""
    whitelist = {
        "brick": {"WALL", "JOINT", "ARCH", "STONE", "CONCRETE", "FLOOR", "INTERIOR", "TIMBER", "BALLAST", "BALLAST2", "BALLAST3", "HARDWARE", "SIGN", "TRIM", "GLASS", "SHUTTER", "DARK"},
        "rail": {"CONCRETE", "DECK", "HARDWARE", "PLATE", "RIVET", "STEEL", "TIMBER"},
        "truss": {"ASPHALT", "BRICK", "CONCRETE", "GUSSET", "HARDWARE", "JOINT", "PAVING", "QUAY", "STEEL", "STEEL2", "WHITE", "YELLOW"},
        "stone": {"ARCH", "ASPHALT", "HARDWARE", "JOINT", "KERB", "PALE", "PAVING", "STONE", "WHITE"},
        "tied": {"ARCH", "CONCRETE", "FLOWER", "GRASS", "HARDWARE", "PALE", "PATH", "PAVING", "PLANTING", "QUAY", "RAIL", "RED", "SHRUB", "STEEL", "STONE", "STRAW", "WHITE"},
    }[style]
    transform = _normalized_matrix(spec)
    for node in sorted(source.graph.nodes_geometry):
        matrix, key = source.graph[node]
        original = source.geometry[key]
        material = original.visual.material.name
        if material.removeprefix("CLAY_") not in whitelist:
            continue
        mesh = original.copy()
        mesh.apply_transform(matrix)
        # The registered compact stone ownership ranges are exclusive-end
        # original triangle indices, matching the fixed preview's selector.
        if style == "stone" and material in contract.get("triangleRanges", {}):
            indices = [index for low, high in contract["triangleRanges"][material] for index in range(low, high)]
            mesh = mesh.submesh([indices], append=True, repair=False)
        mesh.apply_transform(transform)
        mesh.merge_vertices(merge_tex=True, merge_norm=True)
        if style == "rail" or (style == "brick" and material in {"CLAY_BALLAST", "CLAY_HARDWARE", "CLAY_STONE"}):
            _deduplicate_internal_faces(mesh)
        if (style == "truss" and material in {"CLAY_ASPHALT", "CLAY_WHITE", "CLAY_YELLOW"}) or (style == "stone" and material == "CLAY_WHITE") or (style == "brick" and material in {"CLAY_HARDWARE", "CLAY_STONE"}):
            # These original axis-aligned road/marking boxes meet at quay cuts.
            # Recover their actual closed rectangular envelope before capping.
            pieces = _vertex_parts(mesh)
            for index, piece in enumerate(pieces):
                if not _owned(style, material, piece, contract):
                    continue
                if not piece.is_watertight:
                    low, high = piece.bounds
                    on_boundary = np.any(np.isclose(piece.vertices[:, None, :], np.stack((low, high))[None, :, :], atol=EPS), axis=1)
                    if not np.all(on_boundary.sum(axis=1) >= 2):
                        if style == "brick" and material == "CLAY_STONE" and np.allclose([low[1], high[1]], [8.18, 8.42], atol=EPS):
                            # The two source longitudinal string courses touch
                            # the transverse near-end course at shared edges.
                            for number, bounds in enumerate([
                                [[-42.9, 8.18, -5.24], [643, 8.42, -5]],
                                [[-42.9, 8.18, 5], [643, 8.42, 5.24]],
                                [[-43.14, 8.18, -5.24], [-42.9, 8.42, 5.24]],
                            ]):
                                yield material, f"{node}/{index}/course-{number}", _box(bounds), "source-string-course-cell"
                            continue
                        raise ValueError(f"Non-rectangular road source {material}/{index}: {piece.bounds.tolist()}")
                    piece = _box(piece.bounds)
                yield material, f"{node}/{index}", piece, "source-coplanar-box-closure"
            continue
        if style == "brick" and material == "CLAY_WALL":
            pieces = _vertex_parts(mesh)
        else:
            pieces = mesh.split(only_watertight=False, repair=False)
        for index, piece in enumerate(pieces):
            adaptation = "source-triangles"
            if style == "brick" and material == "CLAY_WALL" and not piece.is_watertight and len(piece.faces) > 900:
                for number, carrier in enumerate(_brick_carrier()):
                    yield material, f"{node}/carrier-{number}", carrier, "source-rectangular-carrier-cell"
                continue
            # Exclude context before repairing any open context surfaces.
            if not _owned(style, material, piece, contract):
                continue
            if not piece.is_watertight:
                if style == "brick" and material in {"CLAY_BALLAST2", "CLAY_BALLAST3"}:
                    trimesh.repair.fill_holes(piece)
                    adaptation = "source-ballast-base-cap"
                elif style == "brick" and material == "CLAY_JOINT":
                    piece = _solidify_planar(piece)
                    adaptation = "source-joint-1mm-relief"
                elif style == "brick" and material in {"CLAY_BALLAST", "CLAY_HARDWARE", "CLAY_STONE"}:
                    # Source near/far cells share an end cap. Removing their
                    # internal interfaces restores the original long solid.
                    raise ValueError(f"Unexpected open source seam {material}/{index}")
                else:
                    raise ValueError(f"Owned source component is open: {style} {material}/{index} ({len(piece.faces)} triangles)")
            if not piece.is_watertight:
                raise ValueError(f"Owned source repair remains open: {style} {material}/{index}")
            yield material, f"{node}/{index}", piece, adaptation


def _owned(style, material, piece, contract):
    low, high = piece.bounds
    across = max(abs(low[2]), abs(high[2]))
    if style == "brick":
        if across > 5.501 or low[1] < -EPS or high[1] > 10.41:
            return False
        if material in {"CLAY_BALLAST", "CLAY_CONCRETE"}:
            return True
        if material == "CLAY_STONE" and low[1] >= 8.17 and low[0] >= -43.401:
            return True
        if material == "CLAY_HARDWARE":
            return low[1] >= 8.79 and high[1] <= 8.961 and across <= 2.556
        if material in {"CLAY_GLASS", "CLAY_DARK", "CLAY_TIMBER"} and high[1] > 8.961:
            return False  # Entire train, including companion glazing and bogies.
        return low[0] >= -43.401 and high[0] <= 123.201
    if style == "rail":
        if material == "CLAY_HARDWARE" and high[1] > 14.21:
            return False  # Train window sill frames, not bridge edge guards.
        if material == "CLAY_PLATE" and low[1] > 13.94 and low[2] > .44 and high[2] < 3.36:
            return False  # Complete recessed train door leaves.
        return across <= 5.301 and (material != "CLAY_TIMBER" or low[1] >= 13.04)
    if style == "truss":
        if material in {"CLAY_QUAY", "CLAY_ASPHALT", "CLAY_PAVING", "CLAY_WHITE", "CLAY_YELLOW"}:
            return low[1] < 5.17
        if material == "CLAY_BRICK":
            return across <= 10.201 and low[1] < EPS and high[1] <= 4.001
        if material == "CLAY_JOINT":
            return across <= 10.201 and high[1] <= 4.001
        return across <= 10.401 and low[0] >= -17.61 and high[0] <= 17.61
    if style == "stone":
        if material == "CLAY_WHITE":
            return low[1] >= 10.989 and high[1] <= 11.011 and across <= 3.071
        # Contract bounds are glTF; authoring X stays along, glTF Z across.
        regions = contract.get("meshRegions", {}).get(material, contract["regions"])
        return any(np.all(low >= np.asarray(region[:3]) - EPS) and np.all(high <= np.asarray(region[3:]) + EPS) for region in regions)
    return True


def _clip_axis(mesh, axis, low, high):
    if axis == 0:
        return _clip(mesh, low, high)
    order = [axis] + [index for index in range(3) if index != axis]
    reverse = np.argsort(order)
    rotated = mesh.copy()
    rotated.vertices = rotated.vertices[:, order]
    if np.linalg.det(np.eye(3)[order]) < 0:
        rotated.faces = rotated.faces[:, ::-1]
    clipped = _clip(rotated, low, high)
    if clipped is not None:
        clipped.vertices = clipped.vertices[:, reverse]
        if np.linalg.det(np.eye(3)[order]) < 0:
            clipped.faces = clipped.faces[:, ::-1]
    return clipped


def _clip_convex(mesh, low, high):
    """Exact half-space intersection for the tiny convex joint relief solids."""
    vertices = mesh.vertices
    points = list(vertices[(vertices[:, 0] >= low - 1e-9) & (vertices[:, 0] <= high + 1e-9)])
    for a, b in vertices[mesh.edges_unique]:
        if abs(b[0] - a[0]) < 1e-12:
            continue
        for plane in (low, high):
            t = (plane - a[0]) / (b[0] - a[0])
            if 0 <= t <= 1:
                points.append(a + t * (b - a))
    if len(points) < 4 or np.ptp(np.asarray(points)[:, 0]) < 1e-7:
        return None
    return trimesh.convex.convex_hull(np.asarray(points))


def extract_modules(style, source_path=None):
    spec = SPECS[style]
    source_path = Path(source_path) if source_path else ROOT / f"frontend/public/street-kits/claude-20261023/{spec['sourceSha256']}.glb"
    if sha256(source_path.read_bytes()) != spec["sourceSha256"]:
        raise ValueError(f"Exact {style} source hash mismatch")
    contracts = json.loads(OWNERSHIP_FILE.read_text(encoding="utf-8"))
    contract = contracts.get(spec["candidate"], {})
    source = trimesh.load(source_path, force="scene", process=False)
    materials = {mesh.visual.material.name: deepcopy(mesh.visual.material) for mesh in source.geometry.values()}
    grouped = {kind: defaultdict(list) for kind in KIND_ORDER}
    records = {kind: [] for kind in KIND_ORDER}
    ownership = defaultdict(Counter)
    for material, label, piece, adaptation in _source_pieces(style, source, spec, contract):
        if not _owned(style, material, piece, contract):
            ownership[material]["excludedPieces"] += 1
            continue
        # Compact source bank intersections retain the source's bearing support.
        if style == "truss" and material in {"CLAY_QUAY", "CLAY_ASPHALT", "CLAY_PAVING", "CLAY_WHITE", "CLAY_YELLOW"}:
            piece = _clip_axis(piece, 2, -10.4 if material == "CLAY_QUAY" else -9.4, 10.4 if material == "CLAY_QUAY" else 9.4)
            if piece is None:
                continue
            piece = _clip(piece, -17.6, 17.6)
            if piece is None:
                continue
            adaptation = "compact-source-bank-intersection" if material == "CLAY_QUAY" else adaptation
        if style == "stone" and material == "CLAY_WHITE":
            piece = _clip(piece, -27.5, 41)
            if piece is None:
                continue
        ownership[material]["retainedPieces"] += 1
        for kind, (low, high) in spec["intervals"].items():
            # GLB float32 source coordinates may sit 0.4 micrometres across a
            # rational authoring station. Snap only that serialization noise.
            working = piece.copy()
            for station in (low, high):
                working.vertices[np.isclose(working.vertices[:, 0], station, atol=EPS, rtol=0), 0] = station
            bowstring = style == "rail" and material in {"CLAY_STEEL", "CLAY_PLATE", "CLAY_RIVET"} and piece.bounds[0, 1] >= 12.57 and piece.bounds[0, 0] >= -60.71 and piece.bounds[1, 0] <= -29.29
            tied_bearing = style == "tied" and (material == "CLAY_PALE" or (material == "CLAY_CONCRETE" and abs(piece.bounds.mean(axis=0)[0]) > 18.5 and piece.extents[0] < 4.5 and piece.bounds[0, 1] < 3.31))
            rail_rib = style == "rail" and material in {"CLAY_STEEL", "CLAY_PLATE"} and piece.extents[0] > 10 and piece.extents[2] < 1.1 and piece.bounds[1, 1] < 10
            # Complete narrow bent/portal assemblies have one owner at seams.
            support = style == "rail" and piece.extents[0] <= 1.81 and piece.bounds[0, 1] < 12.81
            if rail_rib:
                centre = piece.bounds.mean(axis=0)[0]
                selected = piece.copy() if low <= centre < high else None
            elif tied_bearing:
                owner = "bridge_left_end" if piece.bounds.mean(axis=0)[0] < 0 else "bridge_right_end"
                selected = piece.copy() if kind == owner else None
            elif bowstring:
                selected = piece.copy() if kind == "bridge_left_end" else None
            elif support:
                centre = piece.bounds.mean(axis=0)[0]
                if kind == "bridge_left_end":
                    selected = piece.copy() if -60.01 <= centre <= -29.99 else None
                elif kind == "bridge_main":
                    selected = piece.copy() if -29.99 < centre <= -14.99 else None
                else:
                    selected = piece.copy() if 30.01 < centre <= 60.01 else None
            else:
                # End ornament/support overhang stays rigid beyond the nominal
                # route interval; only the interior span seam is sliced.
                clip_low = low - 1 if kind == "bridge_left_end" else low
                clip_high = high + 1 if kind == "bridge_right_end" and style != "brick" else high
                try:
                    selected = _clip_convex(working, clip_low, clip_high) if adaptation == "source-joint-1mm-relief" else _clip(working, clip_low, clip_high)
                except ValueError as error:
                    raise ValueError(f"{style}/{kind}/{label} {material}: {error}") from error
            if selected is None:
                continue
            if not selected.is_watertight:
                raise ValueError(f"Open derived piece {style}/{kind}/{label}")
            bounds = selected.bounds.tolist()
            matrix = np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, (low + high) / 2], [0, 0, 0, 1]], float)
            selected.apply_transform(matrix)
            grouped[kind][material].append(selected)
            records[kind].append({"sourcePiece": label, "material": material, "adaptation": adaptation,
                                  "sourceNormalizedBoundsM": bounds, "triangles": len(selected.faces), "closed": True})
    if style == "stone":
        for support in contract["contextSupports"]:
            piece = _prism(support)
            kind = "bridge_left_end" if piece.bounds.mean(axis=0)[0] < 0 else "bridge_right_end"
            low, high = spec["intervals"][kind]
            matrix = np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, (low + high) / 2], [0, 0, 0, 1]], float)
            bounds = piece.bounds.tolist()
            piece.apply_transform(matrix)
            grouped[kind][support["material"]].append(piece)
            records[kind].append({"sourcePiece": support["name"], "material": support["material"],
                                  "adaptation": support["adaptation"], "sourceNormalizedBoundsM": bounds,
                                  "triangles": len(piece.faces), "closed": bool(piece.is_watertight)})
    modules, info = {}, {}
    for kind, groups in grouped.items():
        if not groups:
            raise ValueError(f"Missing {style}/{kind}")
        scene = trimesh.Scene(base_frame="world")
        for name in sorted(groups):
            combined = trimesh.util.concatenate(groups[name])
            combined.visual = trimesh.visual.TextureVisuals(material=deepcopy(materials[name]))
            combined.unmerge_vertices()
            combined.vertex_normals = np.repeat(combined.face_normals, 3, axis=0)
            scene.add_geometry(combined, node_name=name, geom_name=name)
        low, high = spec["intervals"][kind]
        modules[kind] = scene
        info[kind] = {"sourceIntervalM": [low, high], "lengthM": high - low, "sourceOriginM": (low + high) / 2,
                      "boundsGltfYUpM": scene.bounds.tolist(), "componentCount": len(records[kind]),
                      "triangles": sum(record["triangles"] for record in records[kind]),
                      "materials": sorted(groups), "allComponentsClosed": all(record["closed"] for record in records[kind]),
                      "gradeContactComponentCount": sum(abs(record["sourceNormalizedBoundsM"][0][1]) < EPS for record in records[kind]),
                      "structuralGradeContacts": [{"sourcePiece": record["sourcePiece"], "material": record["material"],
                          "boundsGltfYUpM": [[record["sourceNormalizedBoundsM"][0][2], record["sourceNormalizedBoundsM"][0][1], (low + high) / 2 - record["sourceNormalizedBoundsM"][1][0]],
                                              [record["sourceNormalizedBoundsM"][1][2], record["sourceNormalizedBoundsM"][1][1], (low + high) / 2 - record["sourceNormalizedBoundsM"][0][0]]]}
                          for record in records[kind] if abs(record["sourceNormalizedBoundsM"][0][1]) < EPS and record["material"] in {"CLAY_WALL", "CLAY_STONE", "CLAY_CONCRETE", "CLAY_QUAY", "CLAY_BRICK"}],
                      "pieces": records[kind]}
    recipe = {"revision": "straight-source-owned-1", "style": style, "sourceSha256": spec["sourceSha256"],
              "sourceFrame": spec["frame"], "outputFrame": "glTF X across/Y up/Z negative along; module centred on its native interval",
              "intervalsM": spec["intervals"], "mode": spec["mode"], "sourceOwnershipSha256": contract.get("ownershipSha256"),
              "sourceOwnershipFileSha256": sha256(OWNERSHIP_FILE.read_bytes()),
              "toolSources": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path.read_bytes()) for path in
                              [Path(__file__), Path(__file__).with_name("straight_specs.py"), Path(__file__).with_name("build_timber.py")]},
              "authoringSources": _authoring_sources(style), "supportPolicy": "complete supports to native grade; no terrain warping or synthetic ramps",
              "contextPolicy": "exclude surrounding water/city/roads/vegetation by whole source component ownership; source bridge planting and compact structural supports retained"}
    return modules, {"schemaVersion": 1, "sourceSha256": spec["sourceSha256"], "sourceBytes": source_path.stat().st_size,
                     "recipe": recipe, "modules": info, "ownership": {key: dict(value) for key, value in sorted(ownership.items())},
                     "limitations": spec["limitations"] + ["Prepared level conceptual asset; engineering, accessibility, live railway/road connectivity and human visual acceptance are not certified.",
                     "Runtime terrain, endpoints, drawing previews, edit/recovery and capture remain separate integration checks."]}


def _authoring_sources(style):
    import subprocess
    names = {
        "brick": ["tools/clay_brick_arch_viaduct/family_viaduct.py"],
        "rail": ["tools/clay_rail_through_truss/family_railtruss.py"],
        "truss": ["tools/clay_steel_truss_road_bridge/family_trussroad.py"],
        "stone": ["tools/clay_stone_arch_road_bridge/family_stonearch.py"],
        "tied": ["tools/clay_tied_arch_shared_bridge/family_tiedarch.py", "tools/clay_tied_arch_shared_bridge/family_tiedarch_v004.py", "tools/clay_tied_arch_shared_bridge/family_tiedarch_v005.py", "tools/claude_bridge_corrections/tied_arch_plan.py"],
    }[style]
    result = {}
    for name in names:
        if (ROOT / name).exists():
            data = (ROOT / name).read_bytes()
            result[name] = {"sha256": sha256(data), "location": "working-tree"}
        else:
            commit = "2e6f4860b75545aebe5a9cccabb845f3943ba8e9"
            data = subprocess.run(["git", "show", f"{commit}:{name}"], cwd=ROOT, check=True, capture_output=True).stdout
            result[name] = {"sha256": sha256(data), "location": commit}
    return result


def build(style, output_dir, source_path=None):
    output_dir = Path(output_dir)
    if output_dir.resolve().is_relative_to(ROOT):
        raise ValueError("Generated handoff must be outside the source tree")
    spec = SPECS[style]
    source_path = Path(source_path) if source_path else ROOT / f"frontend/public/street-kits/claude-20261023/{spec['sourceSha256']}.glb"
    modules, provenance = extract_modules(style, source_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_data = source_path.read_bytes()
    locks = {}
    for kind, scene in modules.items():
        data = _preserve_source_materials(trimesh.exchange.gltf.export_glb(scene, include_normals=True), source_data)
        (output_dir / f"{kind}.glb").write_bytes(data)
        locks[kind] = {"sha256": sha256(data), "bytes": len(data), "url": f"/street-kits/pilots/{spec['id']}/{kind}.glb"}
    parts = [{"kind": kind, "lengthM": provenance["modules"][kind]["lengthM"], "mode": spec["mode"] if kind == "bridge_main" else "fixed"} for kind in KIND_ORDER]
    native_length = round(parts[0]["lengthM"] + parts[1]["lengthM"] * spec["nativeRepeats"] + parts[2]["lengthM"], 12)
    bridge = {"parts": parts, "deckHeightM": spec["deckHeightM"], "clearWidthM": spec["clearWidthM"],
              "approachM": 0, "endM": parts[0]["lengthM"], "trafficKind": spec["trafficKind"],
              "endpointPolicy": "source-pedestrian-stairs" if style == "tied" else "elevated-source-cut"}
    if style == "tied":
        # Flat tread supports follow the common source trapezoid map. A single
        # longitudinal ramp would float the camera above/below the real risers.
        skew = math.tan(math.radians(6)) / 23
        factor = 1 + skew * 2.65
        paths = [{"partKind": "bridge_main", "points": [[2.65, -19, 3.32], [2.65, 19, 3.32]], "widthM": 4,
                  "surfacePolygon": [[.65, -19, 3.32], [4.65, -19, 3.32], [4.65, 19, 3.32], [.65, 19, 3.32]]}]
        for sign, kind in [(-1, "bridge_left_end"), (1, "bridge_right_end")]:
            origin = sum(spec["intervals"][kind]) / 2
            for lo, hi, height, square_start in [(19, 20.45, 3.32, True), (20.45, 26, 3.3, False)]:
                polygon = [[across, sign * (parameter if square_start and parameter == lo else parameter * (1 + skew * across)) - origin, height]
                           for across, parameter in [(.65, lo), (4.65, lo), (4.65, hi), (.65, hi)]]
                start = lo if square_start else lo * factor
                paths.append({"partKind": kind, "points": [[2.65, sign * start - origin, height], [2.65, sign * hi * factor - origin, height]], "widthM": 4,
                              "surfacePolygon": polygon})
            for index in range(17):
                middle = 26 + (index + .5) * .35
                height = 3.3 * (17 - index) / 17
                # Across-tread paths carry a narrow longitudinal support width.
                # The inscribed band stays inside both skewed riser boundaries.
                width = .35 * (1 + skew * .65) / math.sqrt(1 + (middle * skew) ** 2) * .99999
                points = [[across, sign * middle * (1 + skew * across) - origin, height] for across in [.65, 4.65]]
                lo, hi = 26 + index * .35, 26 + (index + 1) * .35
                polygon = [[across, sign * parameter * (1 + skew * across) - origin, height]
                           for across, parameter in [(.65, lo), (4.65, lo), (4.65, hi), (.65, hi)]]
                paths.append({"partKind": kind, "points": points, "widthM": width, "surfacePolygon": polygon})
        bridge["walkingPaths"] = paths
    program = {"schemaVersion": 1, "adapter": "source-span-bridge-v1", "bridge": bridge,
               "surfaceRegions": [], "details": [], "paving": "source-native", "pavingModuleM": [.3, .15],
               "baseLiftM": 0, "palette": {}, "minLengthM": spec["minLengthM"], "maxLengthM": spec["maxLengthM"], "preparedLevelOnly": True}
    row = {"id": spec["id"], "sourceArchetypeId": spec["sourceArchetypeId"], "title": spec["title"], "status": "candidate",
           "sourceAssemblySha256": spec["sourceSha256"], "sourceCandidateId": spec["candidate"], "widthM": spec["widthM"],
           "fixtureLengthM": native_length, "routeAxis": "local_y", "junctionSurface": "pavers",
           "sections": spec["sections"], "placements": [], "treeWells": [], "modules": locks, "program": program,
           "programSha256": sha256(canonical_bytes(program)), "thumbnailUrl": spec["thumbnailUrl"]}
    reference_data = (ROOT / "frontend/public" / spec["thumbnailUrl"].lstrip("/")).read_bytes()
    pointer = reference_data.startswith(b"version https://git-lfs.github.com/spec/v1")
    reference_sha = reference_data.decode("ascii").split("oid sha256:")[1].splitlines()[0] if pointer else sha256(reference_data)
    row["referenceSha256"] = reference_sha
    provenance["reference"] = {"url": spec["thumbnailUrl"], "sha256": reference_sha, "hydrated": not pointer}
    row["sourceRecipeSha256"] = sha256(canonical_bytes({"extraction": provenance["recipe"], "nativeStreetPilot": row}))
    provenance["moduleLocks"] = locks
    provenance["sourceRecipeSha256"] = row["sourceRecipeSha256"]
    provenance["toolchain"] = {"trimesh": trimesh.__version__, "numpy": np.__version__}
    for name, value in (("nativeStreetPilot.json", row), ("provenance.json", provenance)):
        (output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return row, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=[*SPECS, "all"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for style in SPECS if args.style == "all" else [args.style]:
        if args.dry_run:
            _, provenance = extract_modules(style)
            print(json.dumps({"style": style, "modules": {key: {k: v for k, v in value.items() if k != "pieces"} for key, value in provenance["modules"].items()}}, indent=2))
        else:
            row, _ = build(style, args.output_dir / style)
            print(json.dumps({"style": style, "id": row["id"], "outputDir": str(args.output_dir / style), "modules": row["modules"]}))


if __name__ == "__main__":
    main()
