"""Real locked-source regression checks for the finite timber bridge pilot."""
from importlib import import_module
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import pytest
import trimesh


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "frontend/public/street-kits/claude-20261023/0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad.glb"
KINDS = {"bridge_left_stair", "bridge_left_end", "bridge_bay", "bridge_right_end", "bridge_right_stair"}


def builder():
    assert (ROOT / "tools/drawn_bridge_routes/build_timber.py").is_file(), "finite extraction builder is missing"
    return import_module("tools.drawn_bridge_routes.build_timber")


def meshes(scene):
    for node in scene.graph.nodes_geometry:
        transform, key = scene.graph[node]
        mesh = scene.geometry[key].copy()
        mesh.apply_transform(transform)
        yield mesh


def top_at(scene, across, along, material):
    """Vertical triangle probe without optional rtree; coordinates are local ENU."""
    hits = []
    for mesh in meshes(scene):
        if mesh.visual.material.name != material:
            continue
        triangles = mesh.triangles[:, :, [0, 2, 1]].copy()
        triangles[:, :, 1] *= -1
        for tri in triangles:
            a, b, c = tri
            v0, v1, v2 = b[:2] - a[:2], c[:2] - a[:2], np.array([across, along]) - a[:2]
            determinant = v0[0] * v1[1] - v1[0] * v0[1]
            if abs(determinant) < 1e-10:
                continue
            u = (v2[0] * v1[1] - v1[0] * v2[1]) / determinant
            v = (v0[0] * v2[1] - v2[0] * v0[1]) / determinant
            if u >= -1e-7 and v >= -1e-7 and u + v <= 1 + 1e-7:
                hits.append(a[2] + u * (b[2] - a[2]) + v * (c[2] - a[2]))
    assert hits, f"no {material} surface at {across}, {along}"
    return max(hits)


def test_source_hash_gate_rejects_mutated_bytes_before_loading(tmp_path):
    b = builder()
    altered = tmp_path / "altered.glb"
    altered.write_bytes(SOURCE.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="source hash"):
        b.extract_modules(altered)


def test_five_modules_exclude_context_but_preserve_structural_materials():
    modules, provenance = builder().extract_modules(SOURCE)
    assert set(modules) == KINDS
    assert provenance["sourceSha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    for kind, scene in modules.items():
        materials = {mesh.visual.material.name for mesh in meshes(scene)}
        assert not materials & {"CLAY_WATER", "CLAY_PLANTING"}
        assert np.max(np.abs(scene.bounds[:, 0])) <= 2.951
        if kind.endswith("stair"):
            assert materials == {"CLAY_PAVING", "CLAY_HARDWARE"}
            assert np.max(np.abs(scene.bounds[:, 0])) <= 2.106
            assert len([entry for entry in provenance["modules"][kind]["pieces"] if entry["material"] == "CLAY_PAVING"]) == 18
        else:
            assert {"CLAY_DECK", "CLAY_ROOF", "CLAY_GLASS", "CLAY_GLULAM", "CLAY_TIMBER", "CLAY_SEAM"} <= materials
            assert "CLAY_PAVING" not in materials
    # Source's 104 hardware components contain stairs, remote rails and bridge rails.
    assert provenance["ownership"]["CLAY_HARDWARE"]["excludedPieces"] == 74
    assert provenance["ownership"]["CLAY_PAVING"]["excludedPieces"] == 4


def test_module_seams_have_full_width_deck_and_preserved_roof_height():
    b = builder()
    modules, _ = b.extract_modules(SOURCE)
    for kind in ("bridge_left_end", "bridge_bay", "bridge_right_end"):
        scene = modules[kind]
        length = b.MODULE_LENGTHS[kind]
        for station in (-length / 2 + .001, 0, length / 2 - .001):
            for across in (-1.9, 0, 1.9):
                assert top_at(scene, across, station, "CLAY_DECK") == pytest.approx(3.45, abs=1e-5)
        assert scene.bounds[1, 1] == pytest.approx(7.55, abs=1e-5)
    assert modules["bridge_bay"].bounds[:, 0] == pytest.approx([-2.8, 2.8], abs=1e-5)


def test_stairs_reach_native_deck_and_grade_without_landing_rectangle():
    b = builder()
    modules, _ = b.extract_modules(SOURCE)
    length = b.MODULE_LENGTHS["bridge_left_stair"]
    for side, sign in (("left", 1), ("right", -1)):
        scene = modules[f"bridge_{side}_stair"]
        assert scene.bounds[0, 1] == pytest.approx(0)
        assert top_at(scene, 0, sign * (length / 2 - .05), "CLAY_PAVING") == pytest.approx(3.45, abs=1e-5)
        assert top_at(scene, 0, -sign * (length / 2 - .05), "CLAY_PAVING") == pytest.approx(3.45 / 18, abs=1e-5)


def test_complete_end_supports_reach_grade_and_no_pier_is_cut_in_half():
    b = builder()
    modules, provenance = b.extract_modules(SOURCE)
    for side in ("left", "right"):
        kind = f"bridge_{side}_end"
        concrete = [mesh for mesh in meshes(modules[kind]) if mesh.visual.material.name == "CLAY_CONCRETE"]
        merged = trimesh.util.concatenate(concrete)
        merged.merge_vertices(merge_tex=True, merge_norm=True)
        pieces = merged.split(only_watertight=False)
        assert len(pieces) == 4
        assert all(piece.is_watertight for piece in pieces)
        assert sum(piece.bounds[0, 1] == pytest.approx(0) for piece in pieces) == 2
        assert sorted(round(piece.extents[0], 2) for piece in pieces) == [1.98, 4.9, 5.8, 5.9]
        assert provenance["modules"][kind]["supportOwnership"] == "complete adjacent source pier and abutment; feet extended to grade"


def test_output_hashes_provenance_and_row_are_deterministic(tmp_path):
    b = builder()
    first, second = tmp_path / "first", tmp_path / "second"
    b.build(SOURCE, first)
    b.build(SOURCE, second)
    files = sorted(path.name for path in first.iterdir())
    assert files == sorted(path.name for path in second.iterdir())
    assert {path.name: path.read_bytes() for path in first.iterdir()} == {path.name: path.read_bytes() for path in second.iterdir()}
    row = json.loads((first / "nativeStreetPilot.json").read_text(encoding="utf-8"))
    assert row["id"] == "timber_covered_bridge_route_v1"
    assert row["sourceArchetypeId"] == "urban_pedestrian_footbridge"
    assert row["widthM"] == 6
    assert row["fixtureLengthM"] == pytest.approx(43.6)
    assert row["program"]["adapter"] == "modular-bridge-v1"
    assert row["program"]["bridge"] == {"approachM": 6.3, "endM": 41 / 6, "bayM": 13 / 3, "deckHeightM": 3.45, "clearWidthM": 4}
    assert row["program"]["preparedLevelOnly"] is True
    assert row["program"]["minLengthM"] == 32
    assert row["program"]["maxLengthM"] == 240
    assert row["program"]["surfaceRegions"] == row["program"]["details"] == []
    assert row["program"]["paving"] == "source-native"
    assert row["program"]["pavingModuleM"] == [.3, .15]
    assert row["program"]["baseLiftM"] == 0 and row["program"]["palette"] == {}
    assert row["placements"] == row["treeWells"] == []
    assert row["junctionSurface"] == "pavers"
    assert [band["width"] for band in row["sections"]] == [1, 4, 1]
    assert [band["x"] for band in row["sections"]] == [-2.5, 0, 2.5]
    assert row["thumbnailUrl"] == "/archetypes/streets/urban-pedestrian-footbridge/variant_2.png"
    assert row["referenceSha256"] == "2d5045f8631465754074095cc48c9fab1b8727dac0be9cde3866d999a821d936"
    assert row["programSha256"] == b.sha256(b.canonical_bytes(row["program"]))
    provenance = json.loads((first / "provenance.json").read_text(encoding="utf-8"))
    metadata = dict(row)
    revision = metadata.pop("sourceRecipeSha256")
    assert revision == b.sha256(b.canonical_bytes({"extraction": provenance["recipe"], "nativeStreetPilot": metadata}))
    for kind, lock in row["modules"].items():
        data = (first / f"{kind}.glb").read_bytes()
        assert lock == {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "url": f"/street-kits/pilots/{row['id']}/{kind}.glb"}
        reimport = trimesh.load(first / f"{kind}.glb", force="scene", process=False)
        for mesh in meshes(reimport):
            mesh.merge_vertices(merge_tex=True, merge_norm=True)
            assert all(piece.is_watertight for piece in mesh.split(only_watertight=False))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == b.SOURCE_SHA256


def glb_document(path):
    data = path.read_bytes()
    length = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + length])


def test_exact_source_pbr_semantics_survive_glb_export(tmp_path):
    b = builder()
    b.build(SOURCE, tmp_path)
    original = {material["name"]: material for material in glb_document(SOURCE)["materials"]}
    for kind in KINDS:
        document = glb_document(tmp_path / f"{kind}.glb")
        assert all("uri" not in buffer for buffer in document["buffers"])
        for material in document["materials"]:
            assert material == original[material["name"]]
        if "stair" not in kind:
            assert set(document["extensionsUsed"]) >= {"KHR_materials_transmission", "KHR_materials_ior"}


def test_generated_handoff_refuses_source_tree_output():
    b = builder()
    with pytest.raises(ValueError, match="outside the source tree"):
        b.build(SOURCE, ROOT / "frontend/public/forbidden-output")
