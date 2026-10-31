"""Extract the five bridge-owned modules from the exact timber v004 source.

This writes a review handoff, never installs a catalogue row or changes the
source. GLBs are Y-up; after runtime's glTF-to-ENU transform X is across the
bridge and Y is along its route. Every module is centred on its nominal interval.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad"
DEFAULT_SOURCE = ROOT / f"frontend/public/street-kits/claude-20261023/{SOURCE_SHA256}.glb"
PILOT_ID = "timber_covered_bridge_route_v1"
REFERENCE_SHA256 = "2d5045f8631465754074095cc48c9fab1b8727dac0be9cde3866d999a821d936"
THUMBNAIL_URL = "/archetypes/streets/urban-pedestrian-footbridge/variant_2.png"
BAY_M, END_M, APPROACH_M = 13 / 3, 41 / 6, 6.3
INTERVALS = {
    "bridge_left_stair": (-21.8, -15.5),
    "bridge_left_end": (-15.5, -26 / 3),
    "bridge_bay": (-13 / 3, 0),
    "bridge_right_end": (26 / 3, 15.5),
    "bridge_right_stair": (15.5, 21.8),
}
MODULE_LENGTHS = {
    "bridge_left_stair": APPROACH_M, "bridge_left_end": END_M,
    "bridge_bay": BAY_M, "bridge_right_end": END_M, "bridge_right_stair": APPROACH_M,
}
CORE_MATERIALS = {"CLAY_DECK", "CLAY_JOINT", "CLAY_GLULAM", "CLAY_TIMBER", "CLAY_GLASS", "CLAY_ROOF", "CLAY_SEAM"}
EPS = 1e-5


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def extraction_recipe():
    """The finite ownership and coordinate contract, independently hashable."""
    return {
        "schemaVersion": 1, "revision": "timber-v004-bridge-only-1", "sourceSha256": SOURCE_SHA256,
        "sourceFrame": "glTF Y-up: source X along, Y up, Z across",
        "outputFrame": "glTF Y-up: X=source Z, Y=source Y, Z=-(source X-interval centre); ENU X across/Y along/Z up",
        "intervalsM": {kind: list(interval) for kind, interval in INTERVALS.items()},
        "moduleLengthM": MODULE_LENGTHS,
        "coreMaterials": sorted(CORE_MATERIALS),
        "ownership": {
            "paving": "whole connected stair boxes only: width4, run0.35, outside abs(source X)>=15.5",
            "hardware": "whole stair guards within abs(across)<=2.106 and outside core; core continuous handrails above4.53 only",
            "concrete": "complete same-side source pier/headstock and abutment/cill belong to each end; bottom vertices at0.6 extended to0",
            "context": "water, planting, broad upper/lower paving and remote guard assemblies excluded",
            "cuts": "structural components clipped to nominal X intervals and cut faces capped; original closed source ends retained",
            "materials": "exact source glTF material dictionaries, semantic extras, alpha and transmission/ior extensions retained",
        },
        "bridge": {"approachM": APPROACH_M, "endM": END_M, "bayM": BAY_M, "deckHeightM": 3.45, "clearWidthM": 4},
        "bounds": {"widthM": 6, "minLengthM": 32, "maxLengthM": 240, "preparedLevelOnly": True},
        "sourceAuthoring": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path.read_bytes())
            for path in [ROOT / "tools/clay_timber_covered_footbridge/family_covered.py", ROOT / "tools/clay_timber_covered_footbridge/family_covered_v004.py"]
        },
    }


def _ears(indices, vertices, wanted_normal):
    """Triangulate a simple cut loop, keeping boundary subdivisions watertight."""
    remaining = list(indices)
    points = vertices[:, 1:3]
    area = sum(points[a, 0] * points[b, 1] - points[b, 0] * points[a, 1]
               for a, b in zip(remaining, remaining[1:] + remaining[:1]))
    if np.sign(area) != wanted_normal:
        remaining.reverse()
    faces = []
    while len(remaining) > 3:
        for index, centre in enumerate(remaining):
            before, after = remaining[index - 1], remaining[(index + 1) % len(remaining)]
            a, b, c = points[[before, centre, after]]
            ab, ac = b - a, c - a
            determinant = ab[0] * ac[1] - ab[1] * ac[0]
            if determinant * wanted_normal <= 1e-12:
                continue
            blocked = False
            for other in remaining:
                if other in (before, centre, after):
                    continue
                ap = points[other] - a
                u = (ap[0] * ac[1] - ap[1] * ac[0]) / determinant
                v = (ab[0] * ap[1] - ab[1] * ap[0]) / determinant
                if u >= -1e-9 and v >= -1e-9 and u + v <= 1 + 1e-9:
                    blocked = True
                    break
            if not blocked:
                faces.append((before, centre, after))
                remaining.pop(index)
                break
        else:
            raise ValueError("Could not cap structural component cut loop")
    if len(remaining) == 3:
        faces.append(tuple(remaining))
    return faces


def _slice_closed(mesh, value, keep_positive):
    normal = [1 if keep_positive else -1, 0, 0]
    cut = mesh.slice_plane([value, 0, 0], normal, cap=False)
    if not len(cut.faces):
        return None
    cut.merge_vertices(merge_tex=True, merge_norm=True)
    counts = np.bincount(cut.edges_unique_inverse)
    boundary = cut.edges_unique[counts == 1]
    adjacency = defaultdict(list)
    for a, b in boundary:
        if abs(cut.vertices[a, 0] - value) > EPS or abs(cut.vertices[b, 0] - value) > EPS:
            raise ValueError("Unexpected open original source component")
        adjacency[int(a)].append(int(b))
        adjacency[int(b)].append(int(a))
    caps = []
    while adjacency:
        start = min(adjacency)
        current, previous, loop = start, None, []
        while True:
            loop.append(current)
            following = next((v for v in sorted(adjacency[current]) if v != previous), None)
            if following is None:
                raise ValueError("Open cut boundary")
            previous, current = current, following
            if current == start:
                break
            if current in loop:
                raise ValueError("Self-intersecting cut boundary")
        caps.extend(_ears(loop, cut.vertices, -1 if keep_positive else 1))
        for vertex in loop:
            del adjacency[vertex]
    if caps:
        cut.faces = np.vstack([cut.faces, caps])
    if not cut.is_watertight:
        raise ValueError("Clipped source component is not closed")
    return cut


def _clip(mesh, low, high):
    if mesh.bounds[1, 0] <= low + 1e-7 or mesh.bounds[0, 0] >= high - 1e-7:
        return None
    out = mesh.copy()
    if out.bounds[0, 0] < low - 1e-7:
        out = _slice_closed(out, low, True)
    if out is not None and out.bounds[1, 0] > high + 1e-7:
        out = _slice_closed(out, high, False)
    return out


def _pieces(source):
    for node in sorted(source.graph.nodes_geometry):
        transform, key = source.graph[node]
        mesh = source.geometry[key].copy()
        mesh.apply_transform(transform)
        mesh.merge_vertices(merge_tex=True, merge_norm=True)
        for index, part in enumerate(mesh.split(only_watertight=False)):
            if not part.is_watertight:
                raise ValueError(f"Source component is open: {node}/{index}")
            yield node, index, part


def _owner(material, piece):
    low, high = piece.bounds
    centre = (low + high) / 2
    if material in CORE_MATERIALS:
        return "core"
    if material == "CLAY_CONCRETE":
        return "left_support" if centre[0] < 0 else "right_support"
    if material == "CLAY_PAVING":
        if abs(piece.extents[2] - 4) < EPS and abs(piece.extents[0] - .35) < EPS and abs(centre[0]) > 15.5:
            return "left_stair" if centre[0] < 0 else "right_stair"
    if material == "CLAY_HARDWARE":
        if max(abs(low[2]), abs(high[2])) <= 2.106 and (low[0] >= 15.48 or high[0] <= -15.48):
            return "left_stair" if centre[0] < 0 else "right_stair"
        if low[1] >= 4.53 and max(abs(low[2]), abs(high[2])) <= 2.01:
            return "core"
    return "context"


def extract_modules(source_path=DEFAULT_SOURCE):
    source_path = Path(source_path)
    if sha256(source_path.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Exact timber v004 source hash mismatch")
    source = trimesh.load(source_path, force="scene", process=False)
    records = {kind: [] for kind in INTERVALS}
    grouped = {kind: defaultdict(list) for kind in INTERVALS}
    ownership = defaultdict(Counter)
    source_materials = {}
    for node, index, piece in _pieces(source):
        material = piece.visual.material.name
        source_materials[material] = deepcopy(piece.visual.material)
        owner = _owner(material, piece)
        ownership[material]["excludedPieces" if owner == "context" else "retainedPieces"] += 1
        for kind, (low, high) in INTERVALS.items():
            if owner == "context":
                continue
            support = kind.endswith("end") and owner == kind.removeprefix("bridge_").replace("_end", "_support")
            stair = kind.endswith("stair") and owner == kind.removeprefix("bridge_")
            if support or stair:
                selected = piece.copy()
                if support:
                    selected.vertices[np.isclose(selected.vertices[:, 1], .6, atol=EPS), 1] = 0
            elif owner == "core" and not kind.endswith("stair"):
                selected = _clip(piece, low, high)
            else:
                continue
            if selected is None:
                continue
            # Right-handed 90-degree rotation about source Y, and interval origin.
            matrix = np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, (low + high) / 2], [0, 0, 0, 1]], dtype=float)
            selected.apply_transform(matrix)
            grouped[kind][material].append(selected)
            records[kind].append({"sourceNode": node, "sourcePiece": index, "material": material,
                                  "ownership": owner, "sourceBounds": piece.bounds.tolist(),
                                  "triangles": len(selected.faces), "gradeExtensionM": .6 if support and np.isclose(piece.bounds[0, 1], .6, atol=EPS) else 0})
    modules, module_info = {}, {}
    for kind, materials in grouped.items():
        scene = trimesh.Scene(base_frame="world")
        for material in sorted(materials):
            mesh = trimesh.util.concatenate(materials[material])
            mesh.visual = trimesh.visual.TextureVisuals(material=deepcopy(source_materials[material]))
            # Source architectural faces are flat; avoid soft averaged box corners.
            mesh.unmerge_vertices()
            mesh.vertex_normals = np.repeat(mesh.face_normals, 3, axis=0)
            scene.add_geometry(mesh, node_name=material, geom_name=material)
        modules[kind] = scene
        lo, hi = INTERVALS[kind]
        module_info[kind] = {
            "nominalSourceIntervalM": [lo, hi], "nominalLengthM": MODULE_LENGTHS[kind],
            "sourceOriginM": (lo + hi) / 2, "boundsGltfYUpM": scene.bounds.tolist(),
            "pieces": records[kind],
            "supportOwnership": "complete adjacent source pier and abutment; feet extended to grade" if kind.endswith("end") else "none",
        }
    provenance = {
        "schemaVersion": 1, "sourceSha256": SOURCE_SHA256, "sourceBytes": source_path.stat().st_size,
        "recipe": extraction_recipe(), "ownership": {key: dict(value) for key, value in sorted(ownership.items())},
        "modules": module_info,
        "limitations": ["Prepared level conceptual pedestrian bridge; stairs, no accessibility or engineering certification.",
                        "Complete end piers overlap the nominal bay boundary below deck by 1.666667m; no end roof/deck overlap.",
                        "Bottom source stair riser is0.191667m above grade; each stair solid has its foot at grade.",
                        "Runtime terrain, endpoint editing, walking, capture and human visual acceptance require separate review."],
    }
    return modules, provenance


def _preserve_source_materials(data, source_data):
    """trimesh's PBR conversion drops extensions/extras and quantizes RGBA."""
    def document(blob):
        length = struct.unpack_from("<I", blob, 12)[0]
        return json.loads(blob[20:20 + length]), 20 + length

    original, _ = document(source_data)
    if original.get("textures") or original.get("images"):
        raise ValueError("This exact texture-free source contract cannot copy texture indices")
    exported, binary_start = document(data)
    materials = {material["name"]: material for material in original["materials"]}
    exported["materials"] = [materials[material["name"]] for material in exported["materials"]]
    extensions = {key for material in exported["materials"] for key in material.get("extensions", {})}
    if extensions:
        exported["extensionsUsed"] = sorted(set(exported.get("extensionsUsed", [])) | extensions)
    required = set(original.get("extensionsRequired", [])) & extensions
    if required:
        exported["extensionsRequired"] = sorted(set(exported.get("extensionsRequired", [])) | required)
    packed = canonical_bytes(exported)
    packed += b" " * (-len(packed) % 4)
    binary = data[binary_start:]
    return struct.pack("<4sII", b"glTF", 2, 20 + len(packed) + len(binary)) + struct.pack("<I4s", len(packed), b"JSON") + packed + binary


def _reference_lock():
    data = (ROOT / "frontend/public" / THUMBNAIL_URL.lstrip("/")).read_bytes()
    pointer = data.startswith(b"version https://git-lfs.github.com/spec/v1\n") or data.startswith(b"version https://git-lfs.github.com/spec/v1\r\n")
    digest = data.decode("ascii").split("oid sha256:")[1].splitlines()[0] if pointer else sha256(data)
    if digest != REFERENCE_SHA256:
        raise ValueError("Exact photographic reference hash mismatch")
    return {"url": THUMBNAIL_URL, "sha256": digest, "hydrated": not pointer,
            "verification": "authoritative Git LFS object OID; original image not hydrated locally" if pointer else "local original image bytes"}


def build(source_path, output_dir):
    output_dir = Path(output_dir)
    if output_dir.resolve().is_relative_to(ROOT):
        raise ValueError("Generated module handoff must be outside the source tree")
    modules, provenance = extract_modules(source_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    locks = {}
    source_data = Path(source_path).read_bytes()
    for kind, scene in modules.items():
        data = _preserve_source_materials(trimesh.exchange.gltf.export_glb(scene, include_normals=True), source_data)
        (output_dir / f"{kind}.glb").write_bytes(data)
        locks[kind] = {"sha256": sha256(data), "bytes": len(data), "url": f"/street-kits/pilots/{PILOT_ID}/{kind}.glb"}
    program = {
        "schemaVersion": 1, "adapter": "modular-bridge-v1", "bridge": extraction_recipe()["bridge"],
        "surfaceRegions": [], "details": [], "paving": "source-native", "pavingModuleM": [.3, .15], "baseLiftM": 0, "palette": {},
        "minLengthM": 32, "maxLengthM": 240, "preparedLevelOnly": True,
    }
    reference = _reference_lock()
    row = {
        "id": PILOT_ID, "sourceArchetypeId": "urban_pedestrian_footbridge", "title": "Timber Covered Bridge — Draw Route",
        "status": "candidate", "sourceAssemblySha256": SOURCE_SHA256, "referenceSha256": reference["sha256"],
        "widthM": 6, "fixtureLengthM": 43.6,
        "routeAxis": "local_y", "junctionSurface": "pavers",
        "sections": [{"name": "left_reserve", "x": -2.5, "width": 1, "material": "timber"},
                     {"name": "clear_walk", "x": 0, "width": 4, "material": "timber"},
                     {"name": "right_reserve", "x": 2.5, "width": 1, "material": "timber"}],
        "placements": [], "treeWells": [], "modules": locks, "program": program,
        "programSha256": sha256(canonical_bytes(program)), "thumbnailUrl": THUMBNAIL_URL,
    }
    row["sourceRecipeSha256"] = sha256(canonical_bytes({"extraction": provenance["recipe"], "nativeStreetPilot": row}))
    provenance["reference"] = reference
    provenance["moduleLocks"] = locks
    provenance["sourceRecipeSha256"] = row["sourceRecipeSha256"]
    provenance["toolchain"] = {"trimesh": trimesh.__version__, "numpy": np.__version__}
    for name, value in [("nativeStreetPilot.json", row), ("provenance.json", provenance)]:
        (output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return row, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="measure/validate ownership without writing GLBs")
    args = parser.parse_args()
    if args.dry_run:
        _, provenance = extract_modules(args.source)
        print(json.dumps({kind: {key: value for key, value in info.items() if key != "pieces"} for kind, info in provenance["modules"].items()}, indent=2))
    else:
        row, _ = build(args.source, args.output_dir)
        print(json.dumps({"id": row["id"], "outputDir": str(args.output_dir), "modules": row["modules"]}, indent=2))


if __name__ == "__main__":
    main()
