"""Locked-source checks for the finite five-style straight bridge handoff."""
from pathlib import Path
import json
import struct

import numpy as np
import pytest
import trimesh

from tools.drawn_bridge_routes import straight_build as b
from tools.drawn_bridge_routes.straight_specs import SPECS


@pytest.fixture(scope="module")
def handoffs(tmp_path_factory):
    root = tmp_path_factory.mktemp("straight-bridge-handoff")
    result = {}
    for style in SPECS:
        row, provenance = b.build(style, root / style)
        result[style] = (root / style, row, provenance)
    return result


def document(path):
    data = path.read_bytes()
    size = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + size])


def scene_meshes(scene):
    for node in scene.graph.nodes_geometry:
        transform, key = scene.graph[node]
        mesh = scene.geometry[key].copy()
        mesh.apply_transform(transform)
        yield mesh


def top_at(scene, across, along, material):
    """Probe glTF triangles with no optional ray acceleration dependency."""
    result = []
    point = np.array([across, -along])
    for mesh in scene_meshes(scene):
        if mesh.visual.material.name != material:
            continue
        for triangle in mesh.triangles:
            xy = triangle[:, [0, 2]]
            a, c = xy[1] - xy[0], xy[2] - xy[0]
            det = np.linalg.det(np.stack((a, c)).T)
            if abs(det) < 1e-11:
                continue
            u, v = np.linalg.solve(np.stack((a, c)).T, point - xy[0])
            if u >= -1e-6 and v >= -1e-6 and u + v <= 1 + 1e-6:
                result.append(triangle[0, 1] + u * (triangle[1, 1] - triangle[0, 1]) + v * (triangle[2, 1] - triangle[0, 1]))
    assert result, (across, along, material)
    return max(result)


@pytest.mark.parametrize("style", SPECS)
def test_locked_source_rejected_before_geometry_loading(style, tmp_path):
    source = tmp_path / f"{style}.glb"
    source.write_bytes(b"wrong source bytes")
    with pytest.raises(ValueError, match="source hash"):
        b.extract_modules(style, source)


@pytest.mark.parametrize("style", SPECS)
def test_three_modules_remain_closed_after_actual_glb_roundtrip(style, handoffs):
    folder, row, provenance = handoffs[style]
    assert set(row["modules"]) == set(b.KIND_ORDER)
    for kind, lock in row["modules"].items():
        path = folder / f"{kind}.glb"
        assert b.sha256(path.read_bytes()) == lock["sha256"]
        assert path.stat().st_size == lock["bytes"]
        scene = trimesh.load(path, force="scene", process=False)
        assert provenance["modules"][kind]["allComponentsClosed"]
        assert provenance["modules"][kind]["triangles"] > 0
        assert np.all(np.isfinite(scene.bounds))
        for mesh in scene_meshes(scene):
            mesh.merge_vertices(merge_tex=True, merge_norm=True)
            assert all(piece.is_watertight for piece in mesh.split(only_watertight=False, repair=False)), (style, kind, mesh.visual.material.name)
        assert not set(provenance["modules"][kind]["materials"]) & {"CLAY_WATER", "CLAY_GROUND", "CLAY_CAR", "CLAY_CAR2", "CLAY_BUS", "CLAY_CABIN", "CLAY_VAN", "CLAY_SILVER", "CLAY_ROOF", "CLAY_TERRACE"}
    assert b.sha256((b.ROOT / f"frontend/public/street-kits/claude-20261023/{row['sourceAssemblySha256']}.glb").read_bytes()) == SPECS[style]["sourceSha256"]


@pytest.mark.parametrize("style", SPECS)
def test_exact_source_material_dictionaries_and_recipe_locks(style, handoffs):
    folder, row, provenance = handoffs[style]
    source = b.ROOT / f"frontend/public/street-kits/claude-20261023/{row['sourceAssemblySha256']}.glb"
    materials = {material["name"]: material for material in document(source)["materials"]}
    for kind in b.KIND_ORDER:
        saved = document(folder / f"{kind}.glb")
        assert all("uri" not in item for item in saved["buffers"])
        assert all(item == materials[item["name"]] for item in saved["materials"])
    assert row["programSha256"] == b.sha256(b.canonical_bytes(row["program"]))
    copy = dict(row)
    recipe_hash = copy.pop("sourceRecipeSha256")
    assert recipe_hash == b.sha256(b.canonical_bytes({"extraction": provenance["recipe"], "nativeStreetPilot": copy}))
    assert len(row["referenceSha256"]) == 64
    assert provenance["recipe"]["toolSources"]


@pytest.mark.parametrize("style", SPECS)
def test_finite_span_schema_and_real_main_deck_seams(style, handoffs):
    folder, row, provenance = handoffs[style]
    spec = SPECS[style]
    program = row["program"]
    assert program["adapter"] == "source-span-bridge-v1"
    assert program["preparedLevelOnly"]
    assert program["minLengthM"] <= row["fixtureLengthM"] <= program["maxLengthM"]
    assert row["widthM"] == spec["widthM"]
    assert sum(section["width"] for section in row["sections"]) == pytest.approx(row["widthM"])
    assert [part["mode"] for part in program["bridge"]["parts"]] == ["fixed", spec["mode"], "fixed"]
    assert [part["lengthM"] for part in program["bridge"]["parts"]] == pytest.approx([spec["intervals"][kind][1] - spec["intervals"][kind][0] for kind in b.KIND_ORDER])
    mesh = trimesh.load(folder / "bridge_main.glb", force="scene", process=False)
    material = {"brick": "CLAY_CONCRETE", "rail": "CLAY_DECK", "truss": "CLAY_ASPHALT", "stone": "CLAY_ASPHALT", "tied": "CLAY_PATH"}[style]
    across = 2.65 if style == "tied" else 0
    half = provenance["modules"]["bridge_main"]["lengthM"] / 2
    for along in [-half + .01, 0, half - .01]:
        assert top_at(mesh, across, along, material) == pytest.approx(spec["deckHeightM"], abs=2e-5)
    for kind in ["bridge_left_end", "bridge_right_end"]:
        assert provenance["modules"][kind]["structuralGradeContacts"]


def test_rail_complete_bents_and_no_train_companion_materials(handoffs):
    folder, _, provenance = handoffs["rail"]
    for kind, count in [("bridge_left_end", 6), ("bridge_main", 2), ("bridge_right_end", 4)]:
        concrete = [record for record in provenance["modules"][kind]["pieces"] if record["material"] == "CLAY_CONCRETE"]
        assert sum(abs(record["sourceNormalizedBoundsM"][0][1]) < 1e-6 for record in concrete) == count
        assert all(record["sourceNormalizedBoundsM"][1][0] - record["sourceNormalizedBoundsM"][0][0] == pytest.approx(1.8, abs=1e-5) for record in concrete if record["sourceNormalizedBoundsM"][0][1] == 0)
        assert not set(provenance["modules"][kind]["materials"]) & {"CLAY_GLASS", "CLAY_SILVER", "CLAY_DARK", "CLAY_PALE"}
        for record in provenance["modules"][kind]["pieces"]:
            bounds = np.array(record["sourceNormalizedBoundsM"])
            if record["material"] == "CLAY_HARDWARE":
                assert bounds[1, 1] <= 14.21
            if record["material"] == "CLAY_PLATE":
                assert not (bounds[0, 1] > 13.94 and bounds[0, 2] > .44 and bounds[1, 2] < 3.36)
    assert provenance["modules"]["bridge_main"]["boundsGltfYUpM"][1][1] < 14.21


def test_tied_rigid_supports_and_seventeen_complete_stair_treads(handoffs):
    _, row, provenance = handoffs["tied"]
    assert "CLAY_PALE" not in provenance["modules"]["bridge_main"]["materials"]
    assert provenance["modules"]["bridge_main"]["boundsGltfYUpM"][0][1] >= 2.699
    assert all(record["sourceNormalizedBoundsM"][0][1] >= 2.939 for record in provenance["modules"]["bridge_main"]["pieces"] if record["material"] == "CLAY_CONCRETE")
    for kind in ["bridge_left_end", "bridge_right_end"]:
        records = provenance["modules"][kind]["pieces"]
        stairs = [record for record in records if record["material"] == "CLAY_PAVING" and record["sourceNormalizedBoundsM"][0][1] == 0]
        assert len(stairs) == 17
        assert len([record for record in records if record["material"] == "CLAY_PALE"]) == 6
    assert row["program"]["bridge"]["endpointPolicy"] == "source-pedestrian-stairs"
    paths = row["program"]["bridge"]["walkingPaths"]
    assert len([path for path in paths if path["widthM"] < .36]) == 34
    assert all(path["points"][0][2] == path["points"][1][2] for path in paths)
    assert {path["partKind"] for path in paths} == set(b.KIND_ORDER)
    assert len(paths) == 39
    assert all(len(path["surfacePolygon"]) == 4 for path in paths)
    assert all(len({point[2] for point in path["surfacePolygon"]}) == 1 for path in paths)


def test_output_refuses_to_write_inside_source_tree():
    with pytest.raises(ValueError, match="outside the source tree"):
        b.build("rail", b.ROOT / "frontend/public/forbidden-straight-output")


def test_export_is_deterministic_with_same_locked_source(handoffs, tmp_path):
    folder, _, _ = handoffs["tied"]
    b.build("tied", tmp_path)
    assert {p.name: p.read_bytes() for p in folder.iterdir()} == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
