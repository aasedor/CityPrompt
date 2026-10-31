"""Finite bridge-only extraction of the exact planted green bridge v005.

Immutable GLB geometry is the authority. Original deterministic authoring is
replayed only to identify complete multi-material plants, never to replace the
source geometry. Structural cut solids are closed; original open buried plant
bases remain unchanged. Landscaped spans have unscaled companion tiles.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from tools.drawn_bridge_routes.build_timber import (
    ROOT, EPS, _clip, _preserve_source_materials, canonical_bytes, sha256,
)

SOURCE_SHA256 = "d7dddc9371b5cf554bcb372b6d46c8fc0e6256d7335bd47ff542420463f20066"
DEFAULT_SOURCE = ROOT / f"frontend/public/street-kits/claude-20261023/{SOURCE_SHA256}.glb"
PILOT_ID = "planted_green_bridge_route_v1"
THUMBNAIL_URL = "/archetypes/streets/landscape-park-pedestrian-bridge/variant_2.png"
REFERENCE_SHA256 = "fd3f4b85a8f168fb4684cdcb34750d9654ff8c525d54cfdbb9a7c535a31d32fb"
INTERVALS = {
    "green_left_stair": (-50.5, -40), "green_left_end": (-40, -34),
    "green_left_span": (-34, -12), "green_centre": (-12, 12),
    "green_right_span": (12, 34), "green_right_end": (34, 40),
    "green_right_stair": (40, 50.5),
}
LANDSCAPE_INTERVALS = {"green_left_landscape": (-34, -12), "green_right_landscape": (12, 34)}
ALL_INTERVALS = INTERVALS | LANDSCAPE_INTERVALS
FOLIAGE = {"CLAY_FLOWER", "CLAY_GRASS", "CLAY_LAVENDER", "CLAY_LAVSPIKE", "CLAY_LEAF", "CLAY_MOSS", "CLAY_PLANTING", "CLAY_POPPY", "CLAY_SAGE", "CLAY_SHRUB", "CLAY_STRAW", "CLAY_TREE"}
STRUCTURAL = {"CLAY_CONCRETE", "CLAY_CORTEN", "CLAY_PALE", "CLAY_PATH", "CLAY_RAIL", "CLAY_SOIL", "CLAY_STEEL", "CLAY_STONE", "CLAY_TIMBER"}
FAMILY = ROOT / "tools/clay_planted_green_bridge/family_greenbridge.py"
FAMILY_V005 = ROOT / "tools/clay_planted_green_bridge/family_greenbridge_v005.py"


def _vertex_key(vertex):
    return tuple(np.rint(np.asarray(vertex) * 10000).astype(np.int64))


def plant_assembly_inventory():
    """Replay the locked pure plant maths and label the original vertices.

    This executes no Blender, rendering, filesystem mutation or generation API.
    Every copied source face must map to one complete authored plant assembly.
    """
    records = []
    c = SimpleNamespace(BOX_FACES=[(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    namespace = {"C": c, "G": SimpleNamespace(), "A": SimpleNamespace()}
    tree = ast.parse(FAMILY.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom)) or
                 isinstance(node, ast.Import) and all(alias.name in {"math", "random"} for alias in node.names)]
    exec(compile(tree, str(FAMILY), "exec"), namespace)
    f = SimpleNamespace(**namespace)
    f.Batch.flush = lambda self, name: None
    f.flush_smooth = lambda batch, name: None
    # v005 consumes exactly these bank-riprap random draws before planting.
    b = f.Batch()
    for sign, edge in ((1, f.RN), (-1, -f.RS)):
        for _ in range(45):
            fraction = f.RNG.random()
            f.blob(b, "rock", f.RNG.uniform(-18.6, 18.6), sign * (edge + 2.6 * fraction),
                   f.ZB * fraction + .05, .45, .35, .25, j=.15)

    def begin(batch, smooth, kind, x, y):
        return (kind, x, y, [{role: len(vertices) for role, (vertices, _) in item.g.items()} for item in (batch, smooth)])

    def end(token, batch, smooth):
        kind, x, y, starts = token
        parts = defaultdict(list)
        for item, start in zip((batch, smooth), starts):
            for role, (vertices, _) in item.g.items():
                parts["CLAY_" + role.upper()].extend(vertices[start.get(role, 0):])
        points = np.array([point for vertices in parts.values() for point in vertices])
        records.append({"id": len(records), "kind": kind, "anchorAuthoringM": [x, y, 6.15],
                        "boundsAuthoringM": [points.min(axis=0).tolist(), points.max(axis=0).tolist()],
                        "vertices": dict(parts)})

    namespace_v005 = {"F": f, "C": c, "G": SimpleNamespace(), "_record_begin": begin, "_record_end": end,
                      "disk_inside_convex": __import__("tools.claude_bridge_corrections.plant_clearance", fromlist=["disk_inside_convex"]).disk_inside_convex,
                      "approach_stair_treads": __import__("tools.claude_bridge_corrections.geometry_contract", fromlist=["approach_stair_treads"]).approach_stair_treads}
    tree = ast.parse(FAMILY_V005.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom)) or
                 isinstance(node, ast.Import) and all(alias.name == "math" for alias in node.names)]
    tree.body = [node for node in tree.body if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call)]
    class Instrument(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if node.name in {"clump", "small_tree"}:
                node.body = ast.parse(f"_plant_token = _record_begin(b, smooth, '{node.name}', x, y)").body + node.body + ast.parse("_record_end(_plant_token, b, smooth)").body
            return node
    tree = ast.fix_missing_locations(Instrument().visit(tree))
    exec(compile(tree, str(FAMILY_V005), "exec"), namespace_v005)
    namespace_v005["planting"]()
    lookup = defaultdict(dict)
    for record in records:
        for material, vertices in record["vertices"].items():
            for x, y, z in vertices:
                key = _vertex_key(np.array([x, z, -y], dtype=np.float32))
                previous = lookup[material].setdefault(key, record["id"])
                if previous != record["id"]:
                    raise ValueError("Ambiguous exact source plant assembly ownership")
    return records, lookup


def extraction_recipe():
    return {"schemaVersion": 1, "revision": "planted-green-v005-bridge-only-1", "sourceSha256": SOURCE_SHA256,
            "sourceFrame": "glTF Y-up: X across, Y up, Z minus authoring-Y along",
            "outputFrame": "glTF Y-up: X across, Y up, Z=source Z+interval centre; ENU X across/Y along/Z up",
            "intervalsM": {kind: list(interval) for kind, interval in ALL_INTERVALS.items()},
            "ownership": {"structure": "exact bridge slabs, path, soil, beams, guards, lights, thresholds, whole supports and two stairs; water, banks, bank paths and riprap omitted",
                          "supports": "complete columns assigned by station, bank feet at2.18 extended to0; river column feet0.005 extended to0",
                          "planting": "original deterministic clump/tree assemblies matched to immutable GLB vertices; all trees and alternate complete clumps retained; entire assemblies crossing module boundaries omitted",
                          "foliage": "complete original faces and normals retained; no foliage slicing, no synthetic plant replacements; original buried open bases retained",
                          "spanCompanions": "two22m native complete plant, column, crossbeam, light and post tiles repeat rigidly at22m pitch; continuous deck/path/soil/girders/rails alone scale",
                          "cuts": "structural continuous pieces clipped at nominal stations and closed with caps; complete discrete supports/guards retained by station",
                          "coincidentGuards": "exact duplicate source faces at shared pod-corner posts deduplicated before closed-component extraction",
                          "materials": "exact original glTF material dictionaries"},
            "bounds": {"widthM": 36.971, "minLengthM": 101, "maxLengthM": 277, "deckHeightM": 6, "clearWidthM": 4.6, "preparedLevelOnly": True},
            "sourceAuthoring": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path.read_bytes()) for path in (FAMILY, FAMILY_V005)}}


def _submesh(mesh, selected):
    faces = mesh.faces[np.asarray(selected)]
    used, inverse = np.unique(faces, return_inverse=True)
    out = trimesh.Trimesh(vertices=mesh.vertices[used], faces=inverse.reshape((-1, 3)), vertex_normals=mesh.vertex_normals[used], process=False)
    out.visual = trimesh.visual.TextureVisuals(material=deepcopy(mesh.visual.material))
    return out


def _structural_owner(material, piece):
    """Source-frame X is along, Y up, Z across."""
    low, high = piece.bounds
    station, height, across = (low + high) / 2
    if material == "CLAY_PATH" and abs(high[2] - low[2] - 38.7) < .01:
        return "context"  # two riverside paths, not deck/approach walking surfaces
    if material == "CLAY_PATH" and abs(high[2] - low[2] - 4.6) < .001 and abs(high[0] - low[0] - .35) < .001:
        return "left_stair" if station < 0 else "right_stair"
    if material == "CLAY_RAIL" and abs(station) > 40 + EPS:
        return "left_stair" if station < 0 else "right_stair"
    if material == "CLAY_CONCRETE" and high[1] <= 4.41:
        return "support"
    return "core"


def _module_at(station):
    station = float(np.clip(station, -40 + EPS, 40 - EPS))
    return next(kind for kind, (low, high) in INTERVALS.items() if not kind.endswith("stair") and low <= station < high)


def extract_modules(source_path=DEFAULT_SOURCE):
    source_path = Path(source_path)
    if sha256(source_path.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Exact green v005 source hash mismatch")
    plants, lookup = plant_assembly_inventory()
    source = trimesh.load(source_path, force="scene", process=False)
    grouped = {kind: defaultdict(list) for kind in ALL_INTERVALS}
    records = {kind: [] for kind in ALL_INTERVALS}
    counts = defaultdict(Counter)
    materials = {}
    plant_material_faces = defaultdict(Counter)
    plant_parts = defaultdict(list)
    # Source-to-helper frame is a proper rotation: X along, Y up, Z across.
    to_helper = np.array([[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], dtype=float)
    for node in sorted(source.graph.nodes_geometry):
        transform, key = source.graph[node]
        mesh = source.geometry[key].copy()
        mesh.apply_transform(transform)
        material = mesh.visual.material.name
        materials[material] = deepcopy(mesh.visual.material)
        keys = list(lookup[material])
        if keys:
            distances, nearest = cKDTree(np.asarray(keys) / 10000).query(mesh.vertices)
            owners = np.array([lookup[material][vertex] for vertex in keys])
            ids = np.where(distances < .0002, owners[nearest], -1)
        else:
            ids = np.full(len(mesh.vertices), -1)
        face_ids = ids[mesh.faces]
        if np.any((face_ids.max(axis=1) >= 0) & (face_ids.min(axis=1) != face_ids.max(axis=1))):
            raise ValueError(f"Plant face ownership is incomplete: {material}")
        if material in FOLIAGE - {"CLAY_GRASS"} and np.any(face_ids[:, 0] < 0):
            raise ValueError(f"Exact authoring failed to identify source plant vertices: {material}")
        for plant_id in sorted(set(face_ids[:, 0]) - {-1}):
            face_indices = np.where(face_ids[:, 0] == plant_id)[0]
            plant_parts[int(plant_id)].append((material, _submesh(mesh, face_indices)))
            plant_material_faces[int(plant_id)][material] += len(face_indices)
        structural_faces = np.where(face_ids[:, 0] < 0)[0]
        if material not in STRUCTURAL or not len(structural_faces):
            counts[material]["excludedFaces"] += len(structural_faces)
            continue
        structural = _submesh(mesh, structural_faces)
        structural.apply_transform(to_helper)
        structural.merge_vertices(merge_tex=True, merge_norm=True)
        unique = structural.unique_faces()
        counts[material]["duplicateStructuralFacesRemoved"] += int(len(structural.faces) - np.count_nonzero(unique))
        structural.update_faces(unique)
        for index, piece in enumerate(structural.split(only_watertight=False)):
            if not piece.is_watertight:
                raise ValueError(f"Open original structural source piece: {node}/{index}")
            owner = _structural_owner(material, piece)
            if owner == "context":
                counts[material]["excludedFaces"] += len(piece.faces)
                continue
            low, high = piece.bounds
            station = (low[0] + high[0]) / 2
            for kind, interval in INTERVALS.items():
                support = owner == "support" and kind == _module_at(station)
                stair = owner == kind.removeprefix("green_")
                # All discrete cross-beams, posts, pickets, lights remain whole.
                discrete = owner == "core" and high[0] - low[0] < .6 and kind == _module_at(station)
                extension = 0
                if support or stair or discrete:
                    selected = piece.copy()
                    if support and (np.isclose(low[1], 2.18, atol=EPS) or np.isclose(low[1], .005, atol=EPS)):
                        selected.vertices[np.isclose(selected.vertices[:, 1], low[1], atol=EPS), 1] = 0
                        extension = float(low[1])
                elif owner == "core" and not kind.endswith("stair") and high[0] - low[0] >= .6:
                    selected = _clip(piece, *interval)
                else:
                    continue
                if selected is None:
                    continue
                target = kind.replace("span", "landscape") if kind.endswith("span") and (support or discrete) else kind
                if target != kind and (selected.bounds[0, 0] < interval[0] - EPS or selected.bounds[1, 0] > interval[1] + EPS):
                    raise ValueError(f"Discrete companion assembly crosses full-fit interval: {node}/{index}")
                centre = sum(interval) / 2
                output = np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, centre], [0, 0, 0, 1]], dtype=float)
                selected.apply_transform(output)
                selected.unmerge_vertices()
                selected.vertex_normals = np.repeat(selected.face_normals, 3, axis=0)
                grouped[target][material].append(selected)
                records[target].append({"sourceNode": node, "sourcePiece": index, "material": material, "ownership": owner,
                                      "sourceHelperBoundsM": piece.bounds.tolist(), "triangles": len(selected.faces), "gradeExtensionM": extension})
                counts[material]["retainedFaces"] += len(selected.faces)
    for plant in plants:
        if plant["id"] not in plant_parts:
            raise ValueError("Authored plant has no immutable source faces")
        low, high = np.asarray(plant["boundsAuthoringM"])
        eligible = next((kind for kind, (start, stop) in ALL_INTERVALS.items()
                         if not kind.endswith(("stair", "span")) and low[1] >= start + .001 and high[1] <= stop - .001), None)
        retained = eligible is not None and (plant["kind"] == "small_tree" or plant["id"] % 2 == 0)
        plant.update({"module": eligible if retained else None, "decision": "retained-complete" if retained else "omitted-complete-boundary" if eligible is None else "omitted-complete-budget",
                      "sourceFacesByMaterial": dict(plant_material_faces[plant["id"]])})
        plant.pop("vertices")
        for material, piece in plant_parts[plant["id"]]:
            counts[material]["retainedFaces" if retained else "excludedFaces"] += len(piece.faces)
            if retained:
                piece.apply_translation([0, 0, sum(ALL_INTERVALS[eligible]) / 2])
                grouped[eligible][material].append(piece)
                records[eligible].append({"sourceAssembly": plant["id"], "material": material, "ownership": "complete-plant", "triangles": len(piece.faces)})
    modules, module_info = {}, {}
    for kind, by_material in grouped.items():
        scene = trimesh.Scene(base_frame="world")
        for material in sorted(by_material):
            mesh = trimesh.util.concatenate(by_material[material])
            mesh.visual = trimesh.visual.TextureVisuals(material=deepcopy(materials[material]))
            scene.add_geometry(mesh, node_name=material, geom_name=material)
        modules[kind] = scene
        module_info[kind] = {"nominalSourceIntervalM": list(ALL_INTERVALS[kind]), "nominalLengthM": ALL_INTERVALS[kind][1] - ALL_INTERVALS[kind][0],
                             "sourceOriginM": sum(ALL_INTERVALS[kind]) / 2, "boundsGltfYUpM": scene.bounds.tolist(),
                             "triangles": sum(len(mesh.faces) for mesh in scene.geometry.values()), "pieces": records[kind]}
    return modules, {"schemaVersion": 1, "sourceSha256": SOURCE_SHA256, "sourceBytes": source_path.stat().st_size,
                     "recipe": extraction_recipe(), "ownership": {material: dict(count) for material, count in sorted(counts.items())},
                     "plantAssemblies": plants, "modules": module_info,
                     "limitations": ["Conceptual prepared-level pedestrian bridge with stairs; no engineering/accessibility certification.",
                                     "Original source foliage has deliberately open buried bases; no new cut edges introduced.",
                                     "Complete companion tiles fit at22m pitch; variable residual space remains soil without invented plants.",
                                     "Runtime/browser, native visual acceptance and publication are NOT TESTED/NOT APPROVED."]}


def build(source_path, output_dir):
    output_dir = Path(output_dir)
    if output_dir.resolve().is_relative_to(ROOT):
        raise ValueError("Generated module handoff must be outside the source tree")
    modules, provenance = extract_modules(source_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_data = Path(source_path).read_bytes()
    locks = {}
    for kind, scene in modules.items():
        data = _preserve_source_materials(trimesh.exchange.gltf.export_glb(scene, include_normals=True), source_data)
        (output_dir / f"{kind}.glb").write_bytes(data)
        locks[kind] = {"sha256": sha256(data), "bytes": len(data), "url": f"/street-kits/pilots/{PILOT_ID}/{kind}.glb"}
    native = trimesh.Scene(base_frame="world")
    for kind, scene in modules.items():
        for node in sorted(scene.graph.nodes_geometry):
            transform, key = scene.graph[node]
            mesh = scene.geometry[key].copy()
            mesh.apply_transform(transform)
            mesh.apply_translation([0, 0, -sum(ALL_INTERVALS[kind]) / 2])
            native.add_geometry(mesh, node_name=f"{kind}_{node}", geom_name=f"{kind}_{key}")
    preview_data = _preserve_source_materials(trimesh.exchange.gltf.export_glb(native, include_normals=True), source_data)
    (output_dir / "preview-native-101m.glb").write_bytes(preview_data)
    parts = []
    for kind, (low, high) in INTERVALS.items():
        part = {"kind": kind, "lengthM": high - low, "mode": "span" if kind.endswith("span") else "fixed"}
        if kind.endswith("span"):
            part["companions"] = [{"kind": kind.replace("span", "landscape"), "pitchM": 22, "lengthM": 22}]
        parts.append(part)
    walking = [{"widthM": 4.6, "points": [[0, 10.5, 6], [0, 90.5, 6]]}]
    for step in range(30):
        walking.append({"widthM": 4.6, "points": [[0, step * .35, (step + 1) * .2], [0, (step + 1) * .35, (step + 1) * .2]]})
        walking.append({"widthM": 4.6, "points": [[0, 90.5 + step * .35, (30 - step) * .2], [0, 90.5 + (step + 1) * .35, (30 - step) * .2]]})
    bridge = {"parts": parts, "deckHeightM": 6, "clearWidthM": 4.6, "approachM": 10.5, "endM": 6,
              "trafficKind": "walk", "walkingPaths": walking}
    program = {"schemaVersion": 1, "adapter": "source-span-bridge-v1", "bridge": bridge, "surfaceRegions": [], "details": [],
               "paving": "source-native", "pavingModuleM": [.3, .15], "baseLiftM": 0, "palette": {},
               "minLengthM": 101, "maxLengthM": 277, "preparedLevelOnly": True}
    reference_data = (ROOT / "frontend/public" / THUMBNAIL_URL.lstrip("/")).read_bytes()
    pointer = reference_data.startswith(b"version https://git-lfs.github.com/spec/v1")
    reference_sha = reference_data.decode("ascii").split("oid sha256:")[1].splitlines()[0] if pointer else sha256(reference_data)
    if reference_sha != REFERENCE_SHA256:
        raise ValueError("Exact green photographic reference hash mismatch")
    row = {"id": PILOT_ID, "sourceArchetypeId": "landscape_park_pedestrian_bridge", "title": "Planted Green Bridge — Draw Route", "status": "candidate",
           "sourceAssemblySha256": SOURCE_SHA256, "referenceSha256": reference_sha, "widthM": 36.971, "fixtureLengthM": 101,
           "routeAxis": "local_y", "junctionSurface": "pavers", "sections": [
               {"name": "left_landscape", "x": -10.39275, "width": 16.1855, "material": "planting"},
               {"name": "clear_walk", "x": 0, "width": 4.6, "material": "path"},
               {"name": "right_landscape", "x": 10.39275, "width": 16.1855, "material": "planting"}],
           "placements": [], "treeWells": [], "modules": locks, "program": program, "programSha256": sha256(canonical_bytes(program)), "thumbnailUrl": THUMBNAIL_URL}
    row["sourceRecipeSha256"] = sha256(canonical_bytes({"extraction": provenance["recipe"], "nativeStreetPilot": row}))
    provenance.update(reference={"url": THUMBNAIL_URL, "sha256": reference_sha, "hydrated": not pointer}, moduleLocks=locks,
                      sourceRecipeSha256=row["sourceRecipeSha256"], toolchain={"trimesh": trimesh.__version__, "numpy": np.__version__})
    provenance["nativePreview"] = {"file": "preview-native-101m.glb", "sha256": sha256(preview_data), "bytes": len(preview_data),
                                    "boundsGltfYUpM": native.bounds.tolist(), "triangles": sum(len(mesh.faces) for mesh in native.geometry.values())}
    for name, value in (("nativeStreetPilot.json", row), ("provenance.json", provenance)):
        (output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    review = (ROOT / "docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md").read_text(encoding="utf-8")
    review = review.replace("# Runtime integration review — <archetype / exact variant>", "# Runtime integration review — planted_green_bridge_route_v1 / source v005")
    review = review.replace("(ARCHETYPE_RUNTIME_INTEGRATION.md)", f"({(ROOT / 'docs/ARCHETYPE_RUNTIME_INTEGRATION.md').as_posix()})")
    retained = sum(plant["module"] is not None for plant in provenance["plantAssemblies"])
    note = f"""\n\n## Exact offline extraction evidence — 2026-10-30\n\nSource `{SOURCE_SHA256}` remains immutable. Native preview is a source-owned\nbridge-only reconstruction with rigid complete landscape companions, not a\nrender or visual approval. Exact source material dictionaries are retained.\nThe source authoring was replayed only to identify whole plant assemblies;\nall delivered plant faces and smooth normals come from the immutable GLB.\n\nSeven ordered parts:10.5m stair,6m end,22m span,24m unique pod/threshold centre,\n22m span,6m end,10.5m stair. Nominal length101m, prepared-level range101–277m.\nDeck/path top6m; soil top6.15m; clear central path4.6m; maximum width36.971m.\nUnscaled22m companion tiles carry complete source columns, crossbeams, discrete\nguards/lights and complete plants. Only continuous deck/path/soil/girders/rails\nscale. Companion copies must fully fit their span; no partial tile is allowed.\n\nRetained {retained} of916 complete authored plant assemblies, including all4\nmulti-stem trees. Alternate complete clumps are omitted for budget; complete\nassemblies crossing interval boundaries are omitted instead of cutting foliage.\nSource species, flower colours, smooth normals and authored height are preserved.\nNative preview has {provenance['nativePreview']['triangles']:,} triangles and\n{len(preview_data):,} bytes versus546,955 triangles / {len(source_data):,} source bytes.\nThe original plant domes/blades have deliberately open buried bases. Structural\ncomponents are closed; duplicate coincident source pod-corner guard faces are\ndeduplicated before component extraction. Eight bank column feet are extended\nfrom2.18m to0; six river column feet from0.005m to0. Whole end abutments remain.\nThe original stair solids have30 risers per end,10.5m run,0.2m lowest tread,6m\nupper tread. Guard end overshoot is about11.2mm beyond nominal route endpoints.\n\nFocused real-source tests cover source hash rejection, ownership/bounds, closed\nstructural seams, full-width walking/soil surfaces, stair rise, support contacts,\nwhole multi-material plant ownership, original foliage faces, source materials\nand output locks. Their command is `python -m pytest tools/drawn_bridge_routes/tests/test_green_builder.py -q`.\nThe test report is separate; this note does not claim an unrun test passed.\n\nAll live matrix rows remain NOT TESTED here. Root integration must inspect the\nactual minimum, native and maximum route preview, saved endpoints, terrain,\nwalking, editing, Undo/reload and capture. Source-only checks cannot pass these.\nRuntime decision: NOT REVIEWED. Asset visual decision: NOT REVIEWED.\nPublication/activation: NOT APPROVED. No paid generation, source overwrite or\ncatalogue publication was performed by this extraction.\n"""
    (output_dir / "RUNTIME_REVIEW.md").write_text(review + note, encoding="utf-8", newline="\n")
    return row, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        _, provenance = extract_modules(args.source)
        print(json.dumps({kind: {key: value for key, value in info.items() if key != "pieces"} for kind, info in provenance["modules"].items()}, indent=2))
    else:
        row, _ = build(args.source, args.output_dir)
        print(json.dumps({"id": row["id"], "modules": row["modules"]}, indent=2))


if __name__ == "__main__":
    main()
