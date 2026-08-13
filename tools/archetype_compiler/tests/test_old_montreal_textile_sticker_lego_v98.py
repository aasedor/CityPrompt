from __future__ import annotations

from build_old_montreal_textile_sticker_lego_v98 import BAY_M, SIZE_MATRIX, build_geometry
from compile_old_montreal_textile_sticker_lego_v98 import build_outputs, profile_id


def test_both_width_tiers_pass_carrier_space_conditioning() -> None:
    payload, registry, packages, contract = build_outputs()
    assert contract["statuses"] == {"canonical": "pass", "extended": "pass"}
    assert {entry["signature_profile_id"] for entry in registry["entries"]} == {
        profile_id("canonical"), profile_id("extended")}
    assert payload["profiles"]["old_mtl_textile_mill"] == payload["profiles"][profile_id("canonical")]
    assert all(packages["packages"][size]["carrier_count"] > 700 for size in SIZE_MATRIX)


def test_every_locked_face_has_one_compiled_sticker_owner() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size in SIZE_MATRIX:
        profile = payload["profiles"][profile_id(size)]
        geometry = build_geometry(size)
        expected = {(mesh["name"], face) for mesh in geometry["meshes"] for face in range(len(mesh["faces"]))}
        actual: dict[tuple[str, int], int] = {key: 0 for key in expected}
        for carrier in profile["massing_graph"]["assemblies"]:
            if carrier.get("kind") != "carrier_skin":
                continue
            target = carrier["target_ids"][0]
            for face in carrier["face_indices"]:
                actual[(target, face)] += 1
        assert set(actual) == expected
        assert all(count == 1 for count in actual.values())


def test_physical_glass_is_only_assigned_to_recessed_panes_and_skylights() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size in SIZE_MATRIX:
        profile = payload["profiles"][profile_id(size)]
        glass = [item for item in profile["massing_graph"]["assemblies"] if item.get("material_role") == "glass"]
        assert glass
        assert all(item["glass_profile"] == "industrial_sash" for item in glass)
        assert all("recessed_back" in item["surface_id"] or item["sticker_layer"] == "skylight_glass" for item in glass)
        assert not any(item["floor_role"] == "roof" and item["sticker_layer"] != "skylight_glass" for item in glass)


def test_vertical_sequence_is_fixed_and_only_complete_bays_expand() -> None:
    payload, _registry, _packages, contract = build_outputs()
    assert contract["vertical_scaling"] == "forbidden"
    assert contract["whole_modules_only"] is True
    assert SIZE_MATRIX["extended"]["width_m"] - SIZE_MATRIX["canonical"]["width_m"] == 2 * BAY_M
    for size in SIZE_MATRIX:
        floor_contract = payload["profiles"][profile_id(size)]["massing_graph"]["floor_sticker_contract"]
        assert floor_contract["roles"] == ["ground", "middle", "top"]
        assert floor_contract["floor_count"] == 3
        assert floor_contract["forbid_nonuniform_scale"] is True


def test_roof_and_hidden_returns_have_explicit_owners() -> None:
    payload, _registry, _packages, _contract = build_outputs()
    for size in SIZE_MATRIX:
        assemblies = payload["profiles"][profile_id(size)]["massing_graph"]["assemblies"]
        layers = {item["sticker_layer"] for item in assemblies}
        assert {"opening_return", "flat_gravel_roof", "parapet_coping", "skylight_glass",
                "skylight_metal", "bounded_roof_service"} <= layers
        assert all(item["final_surface_coverage"] is True for item in assemblies)
