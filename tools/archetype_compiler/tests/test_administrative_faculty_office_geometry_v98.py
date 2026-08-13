from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "build_administrative_faculty_office_sticker_lego_v98.py"
SPEC = importlib.util.spec_from_file_location("administrative_faculty_v98", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.fixture(scope="module")
def canonical():
    return MODULE.build_geometry("canonical")


@pytest.fixture(scope="module")
def extended():
    return MODULE.build_geometry("extended")


def test_exact_refs_lock_five_storey_frontage_dominant_canonical(canonical):
    assert len(canonical["reference_evidence"]) == 3
    assert canonical["dimensions"] == {
        "width_m": 30.0, "depth_m": 20.0, "occupied_storeys": 5,
        "wall_top_m": 18.6, "parapet_top_m": 19.55,
    }
    assert len(canonical["floor_bands"]) == 5


def test_extended_tier_adds_only_complete_horizontal_bays(canonical, extended):
    assert extended["dimensions"]["width_m"] == 37.5
    assert extended["dimensions"]["depth_m"] == canonical["dimensions"]["depth_m"] == 20.0
    assert extended["dimensions"]["occupied_storeys"] == canonical["dimensions"]["occupied_storeys"] == 5
    assert extended["structural_grid"]["ordinary_front_stacks"] - canonical["structural_grid"]["ordinary_front_stacks"] == 2
    assert extended["fixed_modules"]["entry_loggias"] == canonical["fixed_modules"]["entry_loggias"] == 1
    assert extended["fixed_modules"]["projecting_bronze_bays"] == 1


def test_entry_is_one_deep_full_height_loggia_with_double_height_base(canonical):
    entry = canonical["entry_loggia"]
    assert entry["full_height_recess_m"] >= 1.5
    assert entry["double_height_entry_zone_m"] == [0.0, 7.8]
    assert len(entry["door_meshes"]) == 2
    assert entry["flat_printed_void"] is False
    names = {mesh["name"] for mesh in canonical["meshes"]}
    assert entry["curtain_glass_mesh"] in names
    assert set(entry["mullion_meshes"] + entry["door_meshes"]) <= names
    assert len(entry["interior_card_meshes"]) == 4
    assert set(entry["interior_card_meshes"]) <= names
    assert entry["ground_lobby_open_at_facade"] is True
    assert entry["ground_tunnel_depth_m"] == pytest.approx(1.8)
    assert len(entry["ground_tunnel_return_meshes"]) == 4


def test_projecting_bronze_bay_spans_five_storeys_and_has_physical_edges(canonical):
    projection_apertures = [a for a in canonical["apertures"] if a.get("fixed_identity")]
    assert len(projection_apertures) == 15
    assert {a["level"] for a in projection_apertures} == set(range(5))
    assert {a["bay"] for a in projection_apertures} == {5, 6, 7}
    assert all(a["projection_m"] == pytest.approx(0.9) for a in projection_apertures)
    edges = [m for m in canonical["meshes"] if m.get("carrier_kind") == "projection_edge"]
    cheeks = [m for m in canonical["meshes"] if m.get("carrier_kind") == "solid_projection_return_cheek"]
    assert len(edges) == 4
    assert len(cheeks) == 1
    assert not [m for m in canonical["meshes"] if m.get("carrier_kind") == "physical_vertical_fin"]


def test_all_ordinary_and_projected_windows_are_true_3d_assemblies(canonical):
    names = {mesh["name"] for mesh in canonical["meshes"]}
    assert canonical["apertures"]
    for aperture in canonical["apertures"]:
        assert aperture["flat_printed_void"] is False
        assert aperture["recess_depth_m"] >= 0.6
        assert aperture["return_meshes"] and aperture["mullion_meshes"]
        assert set(aperture["return_meshes"] + aperture["mullion_meshes"]) <= names
        assert aperture["recessed_glass_mesh"] in names
        assert aperture["interior_card_mesh"] in names


def test_every_transmissive_window_has_one_addressable_card_behind_glass(canonical):
    names = {mesh["name"]: mesh for mesh in canonical["meshes"]}
    cards = [mesh for mesh in canonical["meshes"] if mesh.get("carrier_kind") == "recessed_interior_card"]
    assert len(cards) == len(canonical["apertures"]) + 4
    for aperture in canonical["apertures"]:
        glass = names[aperture["recessed_glass_mesh"]]
        card = names[aperture["interior_card_mesh"]]
        assert card["material_domain"] == "interior_card"
        assert set(card["face_roles"]) == {"interior_card"}
        assert card["side"] == aperture["side"]
        assert card["bay"] == aperture["bay"]
        assert card["level"] == aperture["level"]
        assert card["behind_glass_m"] > 0.0
        assert card["carrier_kind"] == "recessed_interior_card"
        assert glass["carrier_kind"] == "recessed_glass"
    entry_cards = [names[name] for name in canonical["entry_loggia"]["interior_card_meshes"]]
    assert {card["level"] for card in entry_cards} == {1, 2, 3, 4}
    assert all(card["side"] == "front" and card["occupied"] for card in entry_cards)


def test_five_floor_slab_banding_is_physical(canonical):
    bands = [m for m in canonical["meshes"] if m.get("carrier_kind") == "slab_band"]
    assert len(bands) == 16  # 4 datums x left/right/rear + 4 projecting-front bands.
    assert all(len(mesh["faces"]) == 6 for mesh in bands)


def test_flat_gravel_roof_has_four_physical_parapets(canonical):
    roof = [m for m in canonical["meshes"] if m.get("carrier_kind") == "roof_deck"]
    parapets = [m for m in canonical["meshes"] if m.get("carrier_kind") == "roof_parapet"]
    assert len(roof) == 1 and roof[0]["material_domain"] == "gravel_roof"
    assert len(parapets) == 4


def test_six_zone_mechanical_court_has_physical_louvers_and_bounded_equipment(canonical):
    court = canonical["mechanical_court"]
    assert court["court_parts"] == 6
    assert len(court["screen_meshes"]) == 7
    assert len(court["physical_louver_meshes"]) == 56
    assert len(court["equipment_meshes"]) == 6
    assert len(court["low_duct_meshes"]) == 6
    assert len(court["low_pipe_meshes"]) == 3
    assert court["equipment_bounded_by_court"] is True
    assert court["gravel_clearance_preserved"] is True
    x0, x1, y0, y1 = court["bounds_xy_m"]
    assert (x1 - x0, y1 - y0) == (15.0, 10.0)
    assert (x1 - x0) * (y1 - y0) / (30.0 * 20.0) == pytest.approx(0.25)
    names = {mesh["name"]: mesh for mesh in canonical["meshes"]}
    assert set(court["screen_meshes"] + court["physical_louver_meshes"] + court["equipment_meshes"] +
               court["low_duct_meshes"] + court["low_pipe_meshes"]) <= set(names)
    screens = [names[name] for name in court["screen_meshes"]]
    assert all(max(v[2] for v in mesh["vertices"]) == pytest.approx(20.45) for mesh in screens)
    equipment = [names[name] for name in court["equipment_meshes"]]
    ducts = [names[name] for name in court["low_duct_meshes"]]
    pipes = [names[name] for name in court["low_pipe_meshes"]]
    assert all((max(v[0] for v in mesh["vertices"]) - min(v[0] for v in mesh["vertices"])) < 3.0
               for mesh in equipment)
    assert all((max(v[1] for v in mesh["vertices"]) - min(v[1] for v in mesh["vertices"])) < 2.0
               for mesh in equipment)
    assert all(max(v[2] for v in mesh["vertices"]) <= 19.80 for mesh in equipment)
    for mesh in equipment + ducts + pipes:
        assert min(v[0] for v in mesh["vertices"]) > x0
        assert max(v[0] for v in mesh["vertices"]) < x1
        assert min(v[1] for v in mesh["vertices"]) > y0
        assert max(v[1] for v in mesh["vertices"]) < y1
        assert max(v[2] for v in mesh["vertices"]) < 20.45


def test_side_and_rear_completion_is_explicitly_constrained(canonical):
    assert canonical["completion_policy"]["rear"].endswith("no_invented_entry")
    rear_left = [a for a in canonical["apertures"] if a["side"] in {"rear", "left"}]
    assert rear_left and all(a["completion_evidence"] == "constrained" for a in rear_left)
    assert all(a["kind"] == "window" for a in rear_left)


def test_extended_rear_aperture_assemblies_never_cross_the_locked_footprint(extended):
    half_width = extended["dimensions"]["width_m"] / 2
    names = {mesh["name"]: mesh for mesh in extended["meshes"]}
    rear = [a for a in extended["apertures"] if a["side"] == "rear"]
    assert len(rear) == 8 * 5
    for aperture in rear:
        owned = aperture["return_meshes"] + aperture["mullion_meshes"] + [
            aperture["recessed_glass_mesh"], aperture["interior_card_mesh"],
        ]
        for name in owned:
            xs = [vertex[0] for vertex in names[name]["vertices"]]
            assert min(xs) >= -half_width
            assert max(xs) <= half_width


def test_each_visible_face_has_exactly_one_sticker_owner(canonical, extended):
    for geometry in (canonical, extended):
        for mesh in geometry["meshes"]:
            assert len(mesh["faces"]) == len(mesh["face_owners"])
            assert all(len(owners) == 1 and owners[0] for owners in mesh["face_owners"])


def test_hard_stops_cover_locked_identity(canonical):
    stops = set(canonical["geometry_hard_stops"])
    assert {
        "occupied_storeys_must_equal_5", "canonical_footprint_must_equal_30x20",
        "depth_must_equal_20", "entry_loggia_count_must_equal_1",
        "projecting_bronze_front_bays_must_equal_1",
        "all_windows_require_returns_recessed_glass_interior_cards_and_physical_mullions",
        "roof_must_remain_flat_gravel_behind_parapet", "mechanical_court_parts_must_equal_6",
        "no_depth_or_vertical_scaling", "no_invented_rear_entry",
        "every_visible_face_requires_exactly_one_sticker_owner",
    } <= stops


def test_hashes_are_deterministic(canonical, extended):
    assert MODULE.build_geometry("canonical")["geometry_sha256"] == canonical["geometry_sha256"]
    assert MODULE.build_geometry("extended")["geometry_sha256"] == extended["geometry_sha256"]
    assert canonical["geometry_sha256"] != extended["geometry_sha256"]


def test_unknown_size_is_rejected():
    with pytest.raises(KeyError):
        MODULE.build_geometry("elastic")
