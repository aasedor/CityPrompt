import importlib.util
from collections import Counter
from pathlib import Path

import pytest

PATH = Path(__file__).parents[1] / "build_brutalist_heroic_sticker_landmark_v98.py"
SPEC = importlib.util.spec_from_file_location("brutalist_heroic_v98", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


@pytest.fixture(scope="module")
def geometry():
    return MODULE.build_geometry()


def _bounds(mesh):
    return tuple(function(vertex[index] for vertex in mesh["vertices"])
                 for index in range(3) for function in (min, max))


def _positive_overlap(a, b):
    aa, bb = _bounds(a), _bounds(b)
    return all(min(aa[index + 1], bb[index + 1]) - max(aa[index], bb[index]) > 1e-8
               for index in (0, 2, 4))


def test_exact_landmark_dimensions_and_storeys(geometry):
    assert geometry["dimensions"] == {
        "width_m": 50.0, "depth_m": 42.0, "occupied_storeys": 2,
        "main_coping_m": 13.30, "highest_penthouse_m": 16.51,
    }
    assert geometry["size"] == "canonical"
    with pytest.raises(KeyError):
        MODULE.build_geometry("extended")


def test_identity_counts_are_literal(geometry):
    lock = geometry["identity_lock"]
    assert lock["front_monumental_lightboxes"] == 2
    assert lock["right_monumental_lightboxes"] == 3
    assert lock["sculptural_front_pilotis"] == 4
    assert lock["open_roof_courts"] == 2
    assert lock["stepped_roof_penthouses"] == 3
    kinds = Counter(mesh.get("carrier_kind") for mesh in geometry["meshes"])
    assert kinds["flared_piloti_capital"] == 4
    assert kinds["projecting_lightbox_cheek"] == 8
    assert kinds["dominant_projecting_lightbox_blade"] == 2
    assert kinds["splayed_lightbox_sill"] == 5
    assert kinds["stepped_roof_penthouse"] == 3


def test_all_lightboxes_have_real_optical_depth(geometry):
    meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
    assert len(geometry["apertures"]) == 5
    for aperture in geometry["apertures"]:
        base = aperture["name"]
        assert all(base + suffix in meshes for suffix in ("_glass", "_card", "_backing"))
        glass, card, backing = (meshes[base + suffix] for suffix in ("_glass", "_card", "_backing"))
        if aperture["side"] == "front":
            assert _bounds(glass)[2] < _bounds(card)[2] < _bounds(backing)[2]
        else:
            assert _bounds(glass)[0] > _bounds(card)[0] > _bounds(backing)[0]
        assert not _positive_overlap(glass, card)
        assert not _positive_overlap(card, backing)


def test_ground_is_glazed_recess_not_painted_void(geometry):
    kinds = Counter(mesh.get("carrier_kind") for mesh in geometry["meshes"])
    assert kinds["continuous_ground_glass"] == 3
    assert kinds["curtain_wall_mullion"] == 15
    assert kinds["curtain_wall_transom"] == 1
    assert kinds["entry_door_glass"] == 2
    assert kinds["entry_door_frame"] == 6
    assert kinds["recessed_entry_portal"] == 3
    assert kinds["blind_terminal_bookend"] == 1
    assert kinds["left_slot_tower"] == 6
    assert kinds["tower_slot_glass"] == 3
    assert kinds["ground_glazing_head_closure"] == 1


def test_four_piloti_capital_stem_joints_have_closed_concrete_collars(geometry):
    meshes = geometry["meshes"]
    collars = [mesh for mesh in meshes if mesh.get("carrier_kind") == "piloti_capital_stem_collar"]
    stems = [mesh for mesh in meshes if mesh.get("carrier_kind") == "piloti_stem"]
    capitals = [mesh for mesh in meshes if mesh.get("carrier_kind") == "flared_piloti_capital"]
    assert len(collars) == len(stems) == len(capitals) == 4
    assert all(mesh["material_domain"] == "boardformed_concrete" and
               mesh["sticker_owner_id"] == "sticker_board_concrete" for mesh in collars)
    assert all(mesh["closed"] and mesh["outward_winding"] and
               mesh["outward_front_and_returns"] and mesh["no_exposed_terminal"] for mesh in collars)
    assert all(mesh["joint_role"] == "capital_stem_closure" and
               mesh["adjacent_finish"] == "boardformed_concrete" and
               mesh["intentional_bearing_contact"] for mesh in collars)
    for collar, stem, capital in zip(collars, stems, capitals):
        cb, sb, kb = _bounds(collar), _bounds(stem), _bounds(capital)
        assert cb[4:6] == pytest.approx((3.30, 3.55))
        assert cb[0] < sb[0] < sb[1] < cb[1] and cb[2:4] == pytest.approx(sb[2:4])
        assert kb[0] <= cb[0] < cb[1] <= kb[1] and kb[2:4] == pytest.approx(cb[2:4])
        assert cb[4] == pytest.approx(sb[5]) and cb[5] == pytest.approx(kb[4])
        assert not _positive_overlap(collar, stem) and not _positive_overlap(collar, capital)
    # Collars are independent joint closures and never intersect one another.
    assert all(not _positive_overlap(a, b) for index, a in enumerate(collars) for b in collars[index + 1:])


def test_terminal_landmarks_and_parapet_caps_do_not_intersect_shell(geometry):
    meshes = geometry["meshes"]
    shell = [mesh for mesh in meshes if mesh.get("carrier_kind") == "opaque_upper_wall_panel"
             and mesh.get("side") == "front"]
    terminals = [mesh for mesh in meshes if mesh.get("carrier_kind") in
                 {"blind_terminal_bookend", "left_slot_tower"}]
    assert len(terminals) == 7
    assert all(not _positive_overlap(terminal, panel) for terminal in terminals for panel in shell)
    parapets = [mesh for mesh in meshes if mesh.get("carrier_kind") == "outer_parapet"]
    caps = [mesh for mesh in meshes if mesh.get("carrier_kind") == "outer_parapet_corner_cap"]
    assert len(caps) == 4
    assert all(not _positive_overlap(cap, run) for cap in caps for run in parapets)


def test_left_tower_slots_are_literal_voids(geometry):
    meshes = geometry["meshes"]
    tower = [mesh for mesh in meshes if mesh.get("carrier_kind") == "left_slot_tower"]
    glass = [mesh for mesh in meshes if mesh.get("carrier_kind") == "tower_slot_glass"]
    assert all(mesh.get("panelized_around_slots") for mesh in tower)
    assert all(not _positive_overlap(pane, panel) for pane in glass for panel in tower)


def test_two_roof_courts_are_real_voids(geometry):
    meshes = geometry["meshes"]
    floors = [mesh for mesh in meshes if mesh.get("carrier_kind") == "sunken_roof_court_floor"]
    walls = [mesh for mesh in meshes if mesh.get("carrier_kind") == "roof_court_wall"]
    roofs = [mesh for mesh in meshes if mesh.get("carrier_kind") == "upward_roof_field"]
    assert len(floors) == 2 and len(walls) == 8 and roofs
    for floor in floors:
        bounds = _bounds(floor)
        assert all(not _positive_overlap(floor, roof) for roof in roofs)
        assert bounds[4] == pytest.approx(10.35) and bounds[5] == pytest.approx(10.35)


def test_roof_and_parapet_semantics_are_disjoint(geometry):
    meshes = geometry["meshes"]
    roofs = [mesh for mesh in meshes if mesh["material_domain"] in {"roof_membrane", "roof_court_membrane"}]
    verticals = [mesh for mesh in meshes if mesh.get("carrier_kind") in {"outer_parapet", "roof_court_wall"}]
    copings = [mesh for mesh in meshes if mesh.get("carrier_kind") in {"parapet_coping", "penthouse_coping"}]
    assert roofs and len(verticals) == 12 and len(copings) == 7
    assert all(mesh["material_domain"] == "pale_coping" for mesh in copings)
    assert all(mesh["material_domain"] == "boardformed_concrete" for mesh in verticals)


def test_unique_ownership_closure_and_determinism(geometry):
    names = [mesh["name"] for mesh in geometry["meshes"]]
    assert len(names) == len(set(names))
    for mesh in geometry["meshes"]:
        assert len(mesh["faces"]) == len(mesh["face_owners"])
        assert all(owners == [mesh["sticker_owner_id"]] for owners in mesh["face_owners"])
        if len(mesh["faces"]) > 1:
            assert mesh["closed"] and mesh["outward_winding"]
    assert MODULE.build_geometry()["geometry_sha256"] == geometry["geometry_sha256"]


def test_reference_paths_are_exact_variant_zero(geometry):
    assert geometry["reference_evidence"] == MODULE.REFERENCE_PATHS
    assert all(Path(__file__).parents[3].joinpath(path).is_file() for path in MODULE.REFERENCE_PATHS)
