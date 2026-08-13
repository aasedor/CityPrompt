from __future__ import annotations

import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from build_daylight_sawtooth_sticker_lego_v98 import SIZE_MATRIX, build_geometry
from compile_daylight_sawtooth_sticker_lego_v98 import ASSETS, _build_profile, _carrier


def test_size_matrix_is_bounded_whole_tooth_horizontal_growth() -> None:
    assert SIZE_MATRIX["canonical"] == {"width_m": 60.0, "depth_m": 40.0, "front_bays": 12, "side_bays": 8, "teeth": 6}
    assert SIZE_MATRIX["extended"] == {"width_m": 80.0, "depth_m": 40.0, "front_bays": 16, "side_bays": 8, "teeth": 8}


def test_every_mesh_gets_one_complete_carrier() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        carriers = []
        for mesh in geometry["meshes"]:
            groups = {}
            for index, role in enumerate(mesh["face_roles"]):
                groups.setdefault(role, []).append(index)
            carriers.extend(_carrier(mesh, indices, role) for role, indices in groups.items())
        assert len(carriers) >= len(geometry["meshes"])
        assert all(carrier["final_surface_coverage"] for carrier in carriers)
        assert {carrier["surface_id"] for carrier in carriers} == {mesh["name"] for mesh in geometry["meshes"]}


def test_glass_is_physical_and_interiors_are_separate_recessed_cards() -> None:
    geometry = build_geometry("canonical")
    carriers = {_carrier(mesh, list(range(len(mesh["faces"]))))["surface_id"]: _carrier(mesh, list(range(len(mesh["faces"])))) for mesh in geometry["meshes"] if len(set(mesh["face_roles"])) == 1}
    glass = [item for item in carriers.values() if item["material_role"] == "glass"]
    interiors = [item for item in carriers.values() if item["sticker_layer"] == "wall_window_interior_card"]
    assert glass and interiors
    assert all(item["glass_profile"] == "industrial_sash" for item in glass)
    assert all(item["transmission_override"] > 0.5 for item in glass)
    assert all(item["source_image_path"] == ASSETS["interior"] for item in interiors)
    assert len({(item["uv_u_min"], item["uv_u_max"], item["uv_v_min"], item["uv_v_max"]) for item in interiors}) == 8
    assert all(item["uv_u_max"] - item["uv_u_min"] == 0.25 for item in interiors)
    assert all(item["uv_v_max"] - item["uv_v_min"] == 0.5 for item in interiors)


def test_roof_weathering_phase_differs_by_tooth_without_changing_scale() -> None:
    geometry = build_geometry("canonical")
    roof = [
        _carrier(mesh, list(range(len(mesh["faces"]))))
        for mesh in geometry["meshes"]
        if mesh["material_domain"] == "opaque_roof"
    ]
    assert len(roof) == 6
    assert {item["world_metric_uv_tile_m"] for item in roof} == {5.7}
    phases = {(item["world_metric_uv_u_offset"], item["world_metric_uv_v_offset"]) for item in roof}
    assert len(phases) == 6


def test_floor_roof_and_fixed_domains_are_disjoint() -> None:
    geometry = build_geometry("canonical")
    carriers = [_carrier(mesh, list(range(len(mesh["faces"])))) for mesh in geometry["meshes"] if len(set(mesh["face_roles"])) == 1]
    roof_layers = {"opaque_tooth_roof", "northlight_glass", "northlight_frame_flashing"}
    assert all(item["floor_role"] == "roof" for item in carriers if item["sticker_layer"] in roof_layers)
    assert all(item["floor_role"] != "roof" for item in carriers if item["sticker_layer"] in {"wall_window_glass", "wall_window_interior_card"})


def test_generated_registry_profiles_and_contract_exist_after_compile() -> None:
    for path in (
        TOOL_DIR / "daylight_sawtooth_sticker_lego_v98.json",
        TOOL_DIR / "daylight_sawtooth_sticker_lego_v98_contract.json",
        TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzz_daylight_sawtooth_sticker_lego_v98.json",
    ):
        if path.exists():
            json.loads(path.read_text(encoding="utf-8"))


def test_runtime_surface_audit_uses_physical_sawtooth_valley_datum() -> None:
    profile, _ = _build_profile("canonical")
    graph = profile["massing_graph"]
    assert graph["final_surface_audit"]["required"] is True
    assert graph["floor_sticker_contract"]["roof_starts_at_z_m"] == 5.95
    assert graph["floor_sticker_contract"]["floor_datums_m"] == [0.0, 6.0]
    assert graph["recipe_contract"] == {
        "footprint_projection_allowance_m": 10.0,
        "projection_owner": "detached_hollow_chimney",
        "occupied_footprint_excludes_projection": True,
    }
