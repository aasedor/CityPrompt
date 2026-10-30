"""Source-owned green bridge geometry, landscape and handoff regressions."""
from collections import Counter
import json
import struct

import numpy as np
import pytest
import trimesh

from tools.drawn_bridge_routes import green_builder as b
from tools.drawn_bridge_routes.tests.test_build_timber import meshes, top_at


@pytest.fixture(scope="module")
def extraction():
    return b.extract_modules()


@pytest.fixture(scope="module")
def delivery(tmp_path_factory):
    output = tmp_path_factory.mktemp("green")
    row, provenance = b.build(b.DEFAULT_SOURCE, output)
    return output, row, provenance


def document(path):
    data = path.read_bytes()
    size = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + size])


def test_exact_source_gate_and_external_output_only(tmp_path):
    bad = tmp_path / "wrong.glb"
    bad.write_bytes(b.DEFAULT_SOURCE.read_bytes() + b"wrong")
    with pytest.raises(ValueError, match="source hash"):
        b.extract_modules(bad)
    with pytest.raises(ValueError, match="outside the source tree"):
        b.build(b.DEFAULT_SOURCE, b.ROOT / "artifacts/forbidden-green")


def test_compact_bounds_and_context_removal(extraction):
    modules, provenance = extraction
    assert set(modules) == set(b.ALL_INTERVALS)
    assert provenance["sourceSha256"] == b.sha256(b.DEFAULT_SOURCE.read_bytes())
    for kind, scene in modules.items():
        assert not {"CLAY_WATER", "CLAY_ROCK"} & set(scene.geometry)
        assert np.max(np.abs(scene.bounds[:, 0])) <= 18.486
        if "landscape" not in kind and "centre" not in kind:
            assert np.max(np.abs(scene.bounds[:, 0])) <= 7.251
    assert modules["green_centre"].bounds[1, 0] - modules["green_centre"].bounds[0, 0] == pytest.approx(36.970993, abs=1e-5)
    assert all("Bounded planted bank" not in record.get("sourceNode", "") for info in provenance["modules"].values() for record in info["pieces"])


def test_continuous_path_soil_and_closed_structural_seams(extraction):
    modules, provenance = extraction
    for kind, (low, high) in b.INTERVALS.items():
        if kind.endswith("stair"):
            continue
        length = high - low
        for station in (-length / 2 + .001, 0, length / 2 - .001):
            for across in (-2.2, 0, 2.2):
                assert top_at(modules[kind], across, station, "CLAY_PATH") == pytest.approx(6, abs=1e-5)
            for across in (-5.2, 5.2):
                assert top_at(modules[kind], across, station, "CLAY_SOIL") == pytest.approx(6.15, abs=1e-5)
        plant_materials = {record["material"] for record in provenance["modules"][kind]["pieces"] if record["ownership"] == "complete-plant"}
        # Timber contains both caps and complete multi-stem trunks. Plant bases
        # are deliberately open; all other structural source solids must close.
        for mesh in meshes(modules[kind]):
            if mesh.visual.material.name in plant_materials:
                continue
            mesh.merge_vertices(merge_tex=True, merge_norm=True)
            assert all(piece.is_watertight for piece in mesh.split(only_watertight=False))


def test_thirty_source_stairs_and_complete_grade_support_contacts(extraction):
    modules, provenance = extraction
    for side, sign in (("left", 1), ("right", -1)):
        kind = f"green_{side}_stair"
        scene = modules[kind]
        assert scene.bounds[0, 1] == pytest.approx(0)
        assert top_at(scene, 0, sign * 5.2, "CLAY_PATH") == pytest.approx(6)
        assert top_at(scene, 0, -sign * 5.2, "CLAY_PATH") == pytest.approx(.2, abs=1e-5)
        assert sum(record["material"] == "CLAY_PATH" for record in provenance["modules"][kind]["pieces"]) == 30
    bank_columns = []
    for kind, info in provenance["modules"].items():
        for piece in info["pieces"]:
            if piece.get("gradeExtensionM", 0) > 2:
                bank_columns.append(piece)
                assert piece["gradeExtensionM"] == pytest.approx(2.18, abs=1e-5)
                assert piece["sourceHelperBoundsM"][1][1] == pytest.approx(4)
        if kind.endswith("landscape"):
            concrete = next(mesh for mesh in meshes(modules[kind]) if mesh.visual.material.name == "CLAY_CONCRETE")
            assert concrete.bounds[0, 1] == pytest.approx(0)
    assert len(bank_columns) == 8
    assert sum(record.get("gradeExtensionM", 0) == pytest.approx(.005, abs=1e-5)
               for info in provenance["modules"].values() for record in info["pieces"]) == 6


def test_complete_plant_ownership_and_rigid_companion_budget(extraction):
    modules, provenance = extraction
    plants = provenance["plantAssemblies"]
    assert len(plants) == 916
    assert sum(plant["kind"] == "small_tree" for plant in plants) == 4
    assert all(plant["module"] is not None for plant in plants if plant["kind"] == "small_tree")
    for plant in plants:
        selected = sum(record["triangles"] for info in provenance["modules"].values() for record in info["pieces"] if record.get("sourceAssembly") == plant["id"])
        assert selected == (sum(plant["sourceFacesByMaterial"].values()) if plant["module"] else 0)
    for kind in b.LANDSCAPE_INTERVALS:
        scene = modules[kind]
        assert scene.bounds[0, 2] > -11 and scene.bounds[1, 2] < 11
        assert {"CLAY_LAVENDER", "CLAY_LEAF", "CLAY_FLOWER", "CLAY_STRAW"} <= set(scene.geometry)
        assert sum(len(mesh.faces) for mesh in scene.geometry.values()) < 100000
        assert not set(scene.geometry) & {"CLAY_SOIL", "CLAY_PATH"}
    assert not any(record["ownership"] == "complete-plant" for kind in ("green_left_span", "green_right_span") for record in provenance["modules"][kind]["pieces"])


def _triangle_keys(mesh):
    return Counter(tuple(sorted(tuple(point) for point in triangle))
                   for triangle in np.rint(mesh.triangles * 10000).astype(np.int64))


def test_companion_foliage_faces_are_exact_source_originals(extraction):
    modules, _ = extraction
    source = trimesh.load(b.DEFAULT_SOURCE, force="scene", process=False)
    source_faces = {mesh.visual.material.name: _triangle_keys(mesh) for mesh in meshes(source)}
    for kind, (low, high) in b.LANDSCAPE_INTERVALS.items():
        for mesh in meshes(modules[kind]):
            if mesh.visual.material.name not in b.FOLIAGE | {"CLAY_TIMBER"}:
                continue
            mesh.apply_translation([0, 0, -(low + high) / 2])
            assert not (_triangle_keys(mesh) - source_faces[mesh.visual.material.name])


def test_materials_and_hash_locked_row_survive_export(delivery):
    output, row, provenance = delivery
    assert row["id"] == "planted_green_bridge_route_v1"
    assert row["fixtureLengthM"] == sum(part["lengthM"] for part in row["program"]["bridge"]["parts"]) == 101
    assert row["program"]["minLengthM"] == 101 and row["program"]["maxLengthM"] == 277
    assert row["program"]["adapter"] == "source-span-bridge-v1"
    assert row["program"]["bridge"]["trafficKind"] == "walk"
    assert len(row["program"]["bridge"]["walkingPaths"]) == 61
    assert [part["mode"] for part in row["program"]["bridge"]["parts"]] == ["fixed", "fixed", "span", "fixed", "span", "fixed", "fixed"]
    assert all(part["companions"][0]["pitchM"] == part["companions"][0]["lengthM"] == 22 for part in row["program"]["bridge"]["parts"] if part["mode"] == "span")
    original = {material["name"]: material for material in document(b.DEFAULT_SOURCE)["materials"]}
    for kind, lock in row["modules"].items():
        path = output / f"{kind}.glb"
        assert lock["sha256"] == b.sha256(path.read_bytes()) and lock["bytes"] == path.stat().st_size
        assert all(material == original[material["name"]] for material in document(path)["materials"])
    assert row["programSha256"] == b.sha256(b.canonical_bytes(row["program"]))
    assert provenance["reference"]["sha256"] == b.REFERENCE_SHA256
    assert b.sha256(b.DEFAULT_SOURCE.read_bytes()) == b.SOURCE_SHA256
