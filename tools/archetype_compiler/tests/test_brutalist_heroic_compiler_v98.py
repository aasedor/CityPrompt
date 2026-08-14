import hashlib
import importlib.util
import json
from pathlib import Path

TOOL_DIR = Path(__file__).parents[1]
PATH = TOOL_DIR / "compile_brutalist_heroic_sticker_landmark_v98.py"
SPEC = importlib.util.spec_from_file_location("brutalist_compiler_v98", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_compile_is_byte_deterministic():
    MODULE.main()
    paths = [MODULE.OUTPUT, MODULE.REGISTRY, MODULE.PACKAGE, MODULE.CONTRACT]
    first = [_hash(path) for path in paths]
    MODULE.main()
    assert first == [_hash(path) for path in paths]


def test_surface_audit_owns_every_face_once():
    profile, package = MODULE.build_profile()
    audit = profile["massing_graph"]["surface_audit"]
    assert package["status"] == "pass"
    assert audit["status"] == "pass"
    assert audit["visible_face_count"] == audit["owned_once_count"]
    assert not audit["missing_faces"] and not audit["multiply_owned_faces"]


def test_exact_reference_and_geometry_locks():
    profile, _ = MODULE.build_profile()
    graph = profile["massing_graph"]
    assert graph["exact_image_override"]["reference_sha256"] == MODULE.REFERENCE_HASHES
    assert graph["nodes"][0]["geometry_sha256"] == MODULE.build_geometry()["geometry_sha256"]
    assert profile["production_contract"]["placement_model"] == "fixed_landmark"
    assert profile["production_contract"]["repeatable_capacity"] == ["one complete 50x42 fixed-landmark placement atom"]
    assert profile["production_contract"]["placement_contract"] == {
        "mode": "fixed_landmark", "footprint_m": {"width": 50.0, "depth": 42.0},
        "polygon_fit": False, "repeat_count": 1, "continuous_resize_allowed": False,
    }


def test_glass_cards_backings_and_metric_concrete_are_disjoint():
    profile, _ = MODULE.build_profile()
    carriers = profile["massing_graph"]["assemblies"]
    glass = [carrier for carrier in carriers if carrier["material_role"] == "glass"]
    cards = [carrier for carrier in carriers if "interior" in carrier["sticker_layer"]]
    concrete = [carrier for carrier in carriers if "concrete" in carrier["sticker_layer"] or "reveal" in carrier["sticker_layer"]]
    assert glass and cards and concrete
    assert all(carrier["glass_profile"] == "reflective_curtain_wall" for carrier in glass)
    assert all(carrier["source_image_path"] != other["source_image_path"] for carrier in glass for other in cards)
    assert all(carrier["world_metric_uv_tile_m"] == 2.0 for carrier in concrete)
    assert all(carrier["surface_alpha_override"] == .27 for carrier in glass)
    assert all(carrier["transmission_override"] == .92 for carrier in glass)
    assert all(carrier["roughness_override"] == .042 for carrier in glass)


def test_adjacent_window_cards_use_nonadjacent_atlas_cells_and_low_emission():
    profile, _ = MODULE.build_profile()
    carriers = profile["massing_graph"]["assemblies"]
    cards = [carrier for carrier in carriers if carrier["sticker_layer"] in {
        "ground_public_interior", "upper_institutional_interior"
    }]
    assert cards
    assert all(carrier["emission_strength_override"] <= .025 for carrier in cards)

    def distance(left, right):
        return abs(left % 4 - right % 4) + abs(left // 4 - right // 4)

    for prefix in ("front_monumental_lightbox", "right_monumental_lightbox"):
        ordered = sorted(
            (carrier for carrier in cards if prefix in carrier["surface_id"]),
            key=lambda carrier: carrier["surface_id"],
        )
        assert all(distance(a["atlas_cell_index"], b["atlas_cell_index"]) > 1 for a, b in zip(ordered, ordered[1:]))


def test_piloti_joint_collars_use_adjacent_concrete_not_dark_finish():
    profile, _ = MODULE.build_profile()
    carriers = profile["massing_graph"]["assemblies"]
    collars = [carrier for carrier in carriers if "capital_stem_collar" in carrier["surface_id"]]
    assert len({carrier["surface_id"] for carrier in collars}) == 4
    assert all(carrier["sticker_layer"] == "boardformed_front_concrete" for carrier in collars)
    assert all("dark" not in carrier["sticker_layer"] and "interior" not in carrier["sticker_layer"] for carrier in collars)


def test_roof_only_uses_plan_bounds_and_correct_roles():
    profile, _ = MODULE.build_profile()
    carriers = profile["massing_graph"]["assemblies"]
    roof = [carrier for carrier in carriers if carrier["floor_role"] == "roof"]
    assert roof
    assert all(carrier["axis"] == "plan" and len(carrier["plan_bounds"]) == 4 for carrier in roof)
    assert all("roof" in carrier["sticker_layer"] for carrier in roof)


def test_generated_registry_is_single_canonical_tier():
    MODULE.main()
    registry = json.loads(MODULE.REGISTRY.read_text(encoding="utf-8"))
    assert len(registry["tiers"]) == 1
    assert registry["tiers"][0] == {
        "id": "canonical", "signature_profile_id": MODULE.profile_id(),
        "family_id": MODULE.family_id(), "width_m": 50.0, "depth_m": 42.0,
        "occupied_storeys": 2,
    }
