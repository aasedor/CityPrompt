from __future__ import annotations

import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from build_administrative_faculty_office_sticker_lego_v98 import SIZE_MATRIX, build_geometry
from compile_administrative_faculty_office_sticker_lego_v98 import ASSETS, _build_profile, _carrier


def _carriers(size_id: str):
    items = []
    for mesh in build_geometry(size_id)["meshes"]:
        groups = {}
        for index, role in enumerate(mesh["face_roles"]):
            groups.setdefault(role, []).append(index)
        items.extend(_carrier(mesh, indices, role) for role, indices in groups.items())
    return items


def test_size_matrix_is_two_bounded_whole_bay_widths() -> None:
    assert SIZE_MATRIX["canonical"] == {"width_m": 30.0, "depth_m": 20.0, "ordinary_front_stacks": 4, "side_bays": 4, "floors": 5}
    assert SIZE_MATRIX["extended"] == {"width_m": 37.5, "depth_m": 20.0, "ordinary_front_stacks": 6, "side_bays": 4, "floors": 5}


def test_every_mesh_gets_complete_final_surface_coverage() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        carriers = _carriers(size_id)
        assert len(carriers) == len(geometry["meshes"])
        assert {item["surface_id"] for item in carriers} == {mesh["name"] for mesh in geometry["meshes"]}
        assert all(item["final_surface_coverage"] for item in carriers)


def test_glass_and_interior_are_distinct_physical_layers() -> None:
    carriers = _carriers("canonical")
    glass = [item for item in carriers if item["sticker_layer"] == "physical_clear_office_glass"]
    lobby_glass = [item for item in carriers if item["sticker_layer"] == "physical_fritted_entry_glass"]
    interiors = [item for item in carriers if item["sticker_layer"] == "occupied_office_interior_card"]
    assert len(glass) == 105
    assert len(lobby_glass) == 1
    assert len(interiors) == 109
    assert all(item["material_role"] == "glass" for item in glass + lobby_glass)
    assert all(item["source_image_path"] == ASSETS["glass"] for item in glass)
    assert all(item["surface_alpha_override"] == .62 and item["transmission_override"] == .80
               and item["roughness_override"] == .08 for item in glass)
    assert lobby_glass[0]["source_image_path"] == ASSETS["fritted_glass"]
    assert lobby_glass[0]["surface_alpha_override"] == .68
    assert lobby_glass[0]["transmission_override"] == .70
    assert lobby_glass[0]["roughness_override"] == .12
    assert all(item["source_image_path"] == ASSETS["interior"] for item in interiors)
    lobby_interiors = [item for item in interiors if "vertical_entry_loggia" in item["surface_id"]]
    ordinary_interiors = [item for item in interiors if item not in lobby_interiors]
    assert len(lobby_interiors) == 4
    assert all(item["emission_strength_override"] == .02 for item in lobby_interiors)
    assert all(item["emission_strength_override"] == .035 for item in ordinary_interiors)
    cells = {(i["uv_u_min"], i["uv_u_max"], i["uv_v_min"], i["uv_v_max"]) for i in interiors}
    assert len(cells) == 8
    assert all(i["uv_u_max"] - i["uv_u_min"] == 0.25 for i in interiors)
    assert all(i["uv_v_max"] - i["uv_v_min"] == 0.5 for i in interiors)


def test_floor_roles_and_roof_datum_are_disjoint() -> None:
    profile, package = _build_profile("canonical")
    graph = profile["massing_graph"]
    assert package["status"] == "pass" and not package["failures"]
    assert graph["floor_sticker_contract"]["floor_datums_m"] == [0.0, 4.2, 7.8, 11.4, 15.0, 18.6]
    assert graph["floor_sticker_contract"]["roof_starts_at_z_m"] == 18.6
    assert graph["final_surface_audit"]["required"] is True
    carriers = graph["assemblies"]
    roof_layers = {"flat_gravel_roof", "brick_parapet", "mechanical_screen", "physical_mechanical_louver",
                   "bounded_mechanical_equipment", "bounded_low_mechanical_duct", "bounded_low_mechanical_pipe"}
    assert all(item["floor_role"] == "roof" for item in carriers if item["sticker_layer"] in roof_layers)
    assert all(item["floor_role"] != "roof" for item in carriers if item["sticker_layer"] in {"physical_clear_office_glass", "occupied_office_interior_card"})


def test_projection_entry_and_mechanical_modules_do_not_duplicate() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        assert geometry["fixed_modules"]["entry_loggias"] == 1
        assert geometry["fixed_modules"]["projecting_bronze_bays"] == 1
        assert geometry["fixed_modules"]["mechanical_courts"] == 1
        assert geometry["fixed_modules"]["occupied_storeys"] == 5


def test_projection_infill_is_brick_while_explicit_frame_and_bands_remain_bronze() -> None:
    carriers = _carriers("canonical")
    infill = [item for item in carriers if item["sticker_layer"] == "projecting_bay_umber_brick_infill"]
    explicit_bronze = [item for item in carriers if item["sticker_layer"] in {
        "projecting_bronze_frame", "projecting_bronze_slab_band",
    }]
    assert len(infill) == 60 and explicit_bronze
    assert all(item["source_image_path"] == ASSETS["brick_front"] for item in infill)
    assert all("metallic_override" not in item for item in infill)
    assert all(item["source_image_path"] != ASSETS["brick_front"] for item in explicit_bronze)
    assert all(item["metallic_override"] == .55 and item["roughness_override"] == .43
               for item in explicit_bronze)


def test_ordinary_slab_bands_use_subdued_brick_not_pale_plinth() -> None:
    carriers = _carriers("canonical")
    bands = [item for item in carriers if item["sticker_layer"] == "subdued_umber_brick_slab_band"]
    assert len(bands) == 12
    assert all(item["source_image_path"] == ASSETS["brick_return"] for item in bands)
    assert all(item["source_image_path"] != ASSETS["plinth"] for item in bands)


def test_each_refined_roof_service_domain_has_its_own_complete_sticker() -> None:
    carriers = _carriers("canonical")
    expected = {
        "bounded_mechanical_equipment": (6, ASSETS["mechanical"]),
        "bounded_low_mechanical_duct": (6, ASSETS["mechanical_duct"]),
        "bounded_low_mechanical_pipe": (3, ASSETS["mechanical_pipe"]),
    }
    for layer, (count, asset) in expected.items():
        selected = [item for item in carriers if item["sticker_layer"] == layer]
        assert len(selected) == count
        assert all(item["source_image_path"] == asset for item in selected)
        assert all(item["floor_role"] == "roof" and item["final_surface_coverage"] for item in selected)
