from __future__ import annotations

from build_functionalist_mill_sticker_lego_v97 import BAY_M, FLOOR_H_M, SIZE_MATRIX, build_geometry
from compile_functionalist_mill_sticker_lego_v97 import ORDINARY, ROLE_V, build_outputs, profile_id


EXPECTED_CELLS = {"small": 124, "canonical": 201, "large": 298}


def test_size_matrix_uses_only_whole_bays_and_floors() -> None:
    for size_id, spec in SIZE_MATRIX.items():
        geometry = build_geometry(size_id)
        assert geometry["width_m"] % BAY_M == 0
        assert geometry["depth_m"] % BAY_M == 0
        assert geometry["floor_datums_m"] == [index * FLOOR_H_M for index in range(int(spec["floors"]) + 1)]
        walls = [mesh for mesh in geometry["meshes"] if mesh["material_domain"] == "vertical_occupied_floor"]
        assert len(walls) == EXPECTED_CELLS[size_id]
        assert geometry["repeat_middle_bays"] == int(spec["width_m"] / BAY_M) - 3


def test_every_locked_face_has_exactly_one_sticker_owner() -> None:
    payload, _registry, packages, contract = build_outputs()
    for size_id in SIZE_MATRIX:
        profile = payload["profiles"][profile_id(size_id)]
        geometry_node = profile["massing_graph"]["nodes"][0]
        face_count = {mesh["name"]: len(mesh["faces"]) for mesh in geometry_node["meshes"]}
        owners = {name: [0] * count for name, count in face_count.items()}
        for carrier in profile["massing_graph"]["assemblies"]:
            if carrier.get("kind") != "carrier_skin":
                continue
            for target in carrier["target_ids"]:
                if target not in owners:
                    continue
                for face in carrier.get("face_indices") or range(face_count[target]):
                    owners[target][int(face)] += 1
        assert packages["packages"][size_id]["status"] == "pass"
        assert contract["statuses"][size_id] == "pass"
        assert all(value == 1 for values in owners.values() for value in values)


def test_wall_cells_keep_constant_world_and_uv_scale() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size_id in SIZE_MATRIX:
        profile = payload["profiles"][profile_id(size_id)]
        carriers = [item for item in profile["massing_graph"]["assemblies"]
                    if item.get("kind") == "carrier_skin" and item.get("source_image_path") == ORDINARY]
        assert len(carriers) == EXPECTED_CELLS[size_id] - 1 - int(SIZE_MATRIX[size_id]["floors"])
        for carrier in carriers:
            assert carrier["span_m"] == BAY_M
            assert carrier["height_m"] == FLOOR_H_M
            assert round(carrier["uv_u_max"] - carrier["uv_u_min"], 8) == 0.2
            assert round(carrier["uv_v_max"] - carrier["uv_v_min"], 8) == 0.2
            assert carrier["floor_role"] in ROLE_V


def test_middle_is_the_only_repeatable_vertical_role() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size_id, spec in SIZE_MATRIX.items():
        profile = payload["profiles"][profile_id(size_id)]
        wall = [item for item in profile["massing_graph"]["assemblies"]
                if item.get("kind") == "carrier_skin" and "_bay_" in item.get("surface_id", "")]
        per_stack = int(spec["floors"])
        front_zero = [item for item in wall if item["surface_id"].startswith("front_bay_0_floor_")]
        assert len(front_zero) == per_stack
        roles = [item["floor_role"] for item in sorted(front_zero, key=lambda item: item["z_min_m"])]
        assert roles == ["ground"] + ["middle_repeat"] * (per_stack - 2) + ["top_cornice"]
        middle = [item for item in wall if item["floor_role"] == "middle_repeat"
                  and item.get("source_image_path") == ORDINARY]
        assert {(item["uv_v_min"], item["uv_v_max"]) for item in middle} == {ROLE_V["middle_repeat"]}


def test_entrance_and_roof_are_unique_and_semantically_disjoint() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size_id, spec in SIZE_MATRIX.items():
        profile = payload["profiles"][profile_id(size_id)]
        carriers = [item for item in profile["massing_graph"]["assemblies"] if item.get("kind") == "carrier_skin"]
        entrances = [item for item in carriers if item["id"] == "v97_front_bay_00_floor_00_sticker"]
        assert len(entrances) == 1
        roof_start = int(spec["floors"]) * FLOOR_H_M
        for item in carriers:
            if item["floor_role"] == "roof":
                assert item["material_role"] == "roof"
                assert not any(target.startswith(("front_bay", "rear_bay", "left_bay", "right_bay"))
                               for target in item["target_ids"])
            elif item["floor_role"] in {"ground", "middle_repeat", "top_cornice"}:
                assert item.get("z_max_m", roof_start) <= roof_start


def test_catalogue_variant_defaults_to_canonical_but_tiers_coexist() -> None:
    payload, registry, _packages, contract = build_outputs()
    assert payload["profiles"]["brick_multistory_mill"] == payload["profiles"][profile_id("canonical")]
    assert {entry["signature_profile_id"] for entry in registry["entries"]} == {
        profile_id("small"), profile_id("canonical"), profile_id("large")}
    assert registry["paid_facade_calls"] == 2
    assert contract["whole_modules_only"] is True
    assert contract["carrier_counts"] == {"small": 149, "canonical": 232, "large": 335}
