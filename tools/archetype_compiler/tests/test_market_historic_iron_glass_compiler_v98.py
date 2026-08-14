import hashlib
import importlib.util
import json
from pathlib import Path

TOOL_DIR = Path(__file__).parents[1]
PATH = TOOL_DIR / "compile_market_historic_iron_glass_sticker_landmark_v98.py"
SPEC = importlib.util.spec_from_file_location("market_historic_compiler_v98", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _carriers():
    return MODULE.build_profile()[0]["massing_graph"]["assemblies"]


def test_compile_is_byte_deterministic():
    MODULE.main()
    paths = [MODULE.OUTPUT, MODULE.REGISTRY, MODULE.PACKAGE, MODULE.CONTRACT]
    first = [_hash(path) for path in paths]
    MODULE.main()
    assert first == [_hash(path) for path in paths]


def test_exact_reference_geometry_and_fixed_landmark_lock():
    profile, package = MODULE.build_profile()
    graph = profile["massing_graph"]
    assert MODULE.build_geometry()["geometry_sha256"] == MODULE.LOCKED_GEOMETRY_SHA256
    assert graph["nodes"][0]["geometry_sha256"] == MODULE.LOCKED_GEOMETRY_SHA256
    assert graph["exact_image_override"]["reference_sha256"] == MODULE.REFERENCE_HASHES
    assert package["status"] == "pass"
    assert graph["reference_dimensions"] == {
        "width_m": 45.0, "depth_m": 60.0, "floors": 2,
        "occupied_hall_levels": 1, "partial_mezzanines": 2,
    }
    assert isinstance(graph["reference_dimensions"]["floors"], (int, float))
    assert profile["production_contract"]["placement_contract"] == {
        "mode": "fixed_landmark", "footprint_m": {"width": 45.0, "depth": 60.0},
        "polygon_fit": False, "repeat_count": 1, "continuous_resize_allowed": False,
    }


def test_surface_audit_owns_all_6409_faces_exactly_once():
    profile, package = MODULE.build_profile()
    audit = profile["massing_graph"]["surface_audit"]
    assert package["carrier_count"] == 1247
    assert audit == {"visible_face_count": 6409, "owned_once_count": 6409,
                     "missing_faces": [], "multiply_owned_faces": [], "status": "pass"}


def test_roles_are_disjoint_and_semantically_complete():
    carriers = _carriers()
    assert {carrier["floor_role"] for carrier in carriers} == {
        "ground_public", "mezzanine_gallery", "high_hall", "flank_masonry",
        "crown", "roof", "ridge_lantern", "rear_service",
    }
    by_surface = {}
    for carrier in carriers:
        by_surface.setdefault(carrier["surface_id"], set()).add(carrier["floor_role"])
    split_surfaces = {name: roles for name, roles in by_surface.items() if len(roles) > 1}
    assert split_surfaces
    assert all(("aisle_roof" in name or name == "right_zinc_dormer_shell")
               and roles == {"roof", "crown"} for name, roles in split_surfaces.items())
    assert all(by_surface[name] == {"ground_public"} for name in (
        "front_left_shop_display_glass", "front_right_shop_display_glass",
        "front_left_shop_counter", "front_right_shop_counter",
    ))
    assert all(by_surface[name] == {"rear_service"} for name in (
        "rear_fan_spring_sill", "rear_left_spring_pier", "rear_right_spring_pier",
    ))


def test_physical_glass_cards_and_backings_are_separate():
    carriers = _carriers()
    glass = [carrier for carrier in carriers if carrier["material_role"] == "glass"]
    cards = [carrier for carrier in carriers if carrier["sticker_layer"] == "ground_market_interior"]
    backing = [carrier for carrier in carriers if carrier["sticker_layer"] == "dark_cavern_backing"]
    assert glass and len(cards) == 18 and len(backing) == 18
    assert all(carrier["glass_profile"] == "low_iron_clear" for carrier in glass)
    assert all(carrier["transmission_override"] >= .82 and carrier["emission_strength_override"] == 0 for carrier in glass)
    assert all(carrier["source_image_path"] not in {MODULE.ASSETS["ground_card"], MODULE.ASSETS["gallery_card"]}
               for carrier in glass)
    assert all(carrier["atlas_columns"] == 4 and carrier["atlas_rows"] == 2 for carrier in cards)
    shop_cards = [carrier for carrier in cards if "shop_" in carrier["surface_id"]]
    arch_cards = [carrier for carrier in cards if "arched_bay" in carrier["surface_id"]]
    assert len(shop_cards) == 4 and len(arch_cards) == 14
    assert all(.28 <= carrier["emission_strength_override"] <= .34 for carrier in shop_cards)
    assert all(carrier["emission_strength_override"] == .09 for carrier in arch_cards)
    assert all(carrier["surface_alpha_override"] == 1 and carrier["transmission_override"] == 0
               and carrier["emission_strength_override"] == 0 for carrier in backing)
    assert MODULE.ASSETS["ground_card"] != MODULE.ASSETS["gallery_card"]


def test_adjacent_side_cards_use_deterministic_nonadjacent_cells():
    cards = [carrier for carrier in _carriers() if carrier["sticker_layer"] == "ground_market_interior"]
    def distance(left, right):
        return abs(left % 4 - right % 4) + abs(left // 4 - right // 4)
    for side in ("left", "right"):
        ordered = sorted((carrier for carrier in cards if f"{side}_arched_bay" in carrier["surface_id"]),
                         key=lambda carrier: int(carrier["surface_id"].split("_")[3]))
        assert len(ordered) == 7
        assert all(distance(a["atlas_cell_index"], b["atlas_cell_index"]) > 1
                   for a, b in zip(ordered, ordered[1:]))


def test_barrel_glass_has_contiguous_equal_arc_registration():
    strips = sorted((carrier for carrier in _carriers() if carrier["surface_id"].startswith("barrel_glass_strip_")),
                    key=lambda carrier: carrier["barrel_strip_index"])
    assert len(strips) == 30
    assert [carrier["barrel_strip_index"] for carrier in strips] == list(range(15)) + list(range(21, 36))
    assert all(carrier["source_image_path"] == MODULE.ASSETS["curved_glass"] for carrier in strips)
    assert all(carrier["curved_mapping_semantics"] == "barrel_arc_length_by_locked_strip" for carrier in strips)
    assert strips[0]["barrel_arc_u_min"] == 0 and strips[-1]["barrel_arc_u_max"] == 1
    assert all(abs((carrier["barrel_arc_u_max"] - carrier["barrel_arc_u_min"]) - 1 / 36) < 1e-12
               for carrier in strips)
    ends = [carrier for carrier in _carriers() if carrier["surface_id"].startswith((
        "barrel_front_ridge_end_glass_", "barrel_rear_ridge_end_glass_"))]
    assert len(ends) == 12
    for end in ("front", "rear"):
        group = sorted((carrier for carrier in ends if carrier["barrel_end"] == end),
                       key=lambda carrier: carrier["barrel_strip_index"])
        assert [carrier["barrel_strip_index"] for carrier in group] == list(range(15, 21))
        assert all(abs(left["barrel_arc_u_max"] - right["barrel_arc_u_min"]) < 1e-12
                   for left, right in zip(group, group[1:]))


def test_roof_fields_upward_only_with_separate_soffit_and_terminals():
    profile, _ = MODULE.build_profile()
    carriers = profile["massing_graph"]["assemblies"]
    meshes = {mesh["name"]: mesh for mesh in MODULE.build_geometry()["meshes"]}
    roof_fields = [carrier for carrier in carriers if carrier["sticker_layer"] in {
        "weathered_slate_roof", "aged_standing_seam_zinc",
    }]
    assert len([carrier for carrier in roof_fields if carrier["sticker_layer"] == "weathered_slate_roof"]) == 14
    assert len([carrier for carrier in roof_fields if carrier["sticker_layer"] == "aged_standing_seam_zinc"]) == 18
    assert all(carrier["axis"] == "plan" and len(carrier["plan_bounds"]) == 4 for carrier in roof_fields)
    assert all(all(MODULE._physical_sloped_face_class(meshes[carrier["surface_id"]], index) == "up"
                   for index in carrier["face_indices"]) for carrier in roof_fields)
    # The source prisms have reversed winding: exterior slopes are the higher
    # centroid faces even when their normal points down.
    for carrier in roof_fields:
        mesh = meshes[carrier["surface_id"]]
        selected = [MODULE._face_centroid_z(mesh, index) for index in carrier["face_indices"]]
        lower = [MODULE._face_centroid_z(mesh, index) for index in range(len(mesh["faces"]))
                 if MODULE._physical_sloped_face_class(mesh, index) == "down"]
        assert lower and min(selected) > max(lower)
    terminals = [carrier for carrier in carriers if carrier["sticker_layer"] == "aged_roof_flashing_coping"]
    soffits = [carrier for carrier in carriers if carrier["sticker_layer"] == "pale_roof_soffit"]
    assert terminals and soffits
    assert all(carrier["source_image_path"] not in {MODULE.ASSETS["slate"], MODULE.ASSETS["zinc"]}
               for carrier in terminals + soffits)
    aisle_non_fields = [carrier for carrier in terminals + soffits
                        if "aisle_roof" in carrier["surface_id"] or "zinc_dormer" in carrier["surface_id"]]
    assert aisle_non_fields and all(carrier["floor_role"] == "crown" for carrier in aisle_non_fields)


def test_roof_role_faces_respect_locked_surface_datum():
    profile, _ = MODULE.build_profile()
    graph = profile["massing_graph"]
    datum = graph["floor_sticker_contract"]["roof_starts_at_z_m"]
    assert datum == MODULE.LOCKED_ROOF_SURFACE_DATUM_M == 7.51
    meshes = {mesh["name"]: mesh for mesh in MODULE.build_geometry()["meshes"]}
    centroids = []
    for carrier in graph["assemblies"]:
        if carrier["floor_role"] != "roof":
            continue
        mesh = meshes[carrier["surface_id"]]
        for face_index in carrier["face_indices"]:
            face = mesh["faces"][face_index]
            centroids.append(sum(float(mesh["vertices"][vertex][2]) for vertex in face) / len(face))
    assert centroids and min(centroids) >= datum
    assert min(centroids) - datum < .01


def test_historic_roof_fan_and_clerestory_glass_has_more_authority_than_wall_glass():
    carriers = _carriers()
    high_kinds = {"barrel_glass_panel", "barrel_ridge_end_glass_panel", "rooflight_glass",
                  "ridge_lantern_glass", "front_side_fan_glass", "front_gable_glass",
                  "rear_gable_glass", "eave_clerestory_glass"}
    high = [carrier for carrier in carriers if carrier["material_role"] == "glass"
            and next(mesh for mesh in MODULE.build_geometry()["meshes"]
                     if mesh["name"] == carrier["surface_id"])["carrier_kind"] in high_kinds]
    wall = [carrier for carrier in carriers if carrier["material_role"] == "glass"
            and carrier not in high]
    assert high and wall
    assert min(carrier["surface_alpha_override"] for carrier in high) > max(
        carrier["surface_alpha_override"] for carrier in wall)
    assert all(carrier["roughness_override"] == .065 for carrier in high)
    assert all(carrier["surface_alpha_override"] == .36 for carrier in high)
    assert all(carrier["transmission_override"] >= .89 for carrier in high)
    assert all(carrier["surface_alpha_override"] == .31 and carrier["transmission_override"] == .89
               for carrier in wall)


def test_rooflight_glass_and_curb_have_distinct_supported_finishes():
    carriers = _carriers()
    glass = [carrier for carrier in carriers if carrier["sticker_layer"] == "rooflight_low_iron_glass"]
    curb = [carrier for carrier in carriers if carrier["sticker_layer"] == "rooflight_flashing"]
    assert len(glass) == 8 and len(curb) == 32
    assert all(carrier["source_image_path"] == MODULE.ASSETS["rooflight_glass"]
               and carrier["glass_profile"] == "low_iron_clear" for carrier in glass)
    assert all(carrier["source_image_path"] == MODULE.ASSETS["flashing"]
               and carrier["metallic_override"] == .54 and carrier["roughness_override"] == .5
               for carrier in curb)


def test_flashing_is_weathered_gray_not_black_metallic_terminal():
    flashing = [carrier for carrier in _carriers()
                if carrier["sticker_layer"] == "aged_roof_flashing_coping"]
    assert flashing
    assert all(carrier["metallic_override"] == .42 and carrier["roughness_override"] == .58
               for carrier in flashing)


def test_open_front_cavern_is_not_closed_by_cards_or_backings():
    geometry = MODULE.build_geometry()
    floor = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "market_hall_floor")
    assert floor["nave_open"] is True
    optical = [carrier for carrier in _carriers() if carrier["sticker_layer"] in {
        "ground_market_interior", "gallery_market_interior", "dark_cavern_backing",
    }]
    assert optical
    assert all(carrier["surface_id"].startswith((
        "left_arched_bay_", "right_arched_bay_", "front_left_shop_", "front_right_shop_",
    )) for carrier in optical)
    assert not any(carrier["surface_id"].startswith("rear_") for carrier in optical)


def test_eave_clerestory_and_recessed_shopfronts_have_physical_depth_stacks():
    carriers = _carriers()
    clerestory_glass = [carrier for carrier in carriers if "eave_clerestory_glass" in carrier["surface_id"]]
    clerestory_rails = [carrier for carrier in carriers if "eave_clerestory_" in carrier["surface_id"]
                       and carrier["sticker_layer"] == "heritage_green_cast_iron"]
    assert len(clerestory_glass) == 18 and len(clerestory_rails) == 36
    assert all(carrier["material_role"] == "glass" and carrier["floor_role"] == "roof"
               for carrier in clerestory_glass)
    shop_glass = [carrier for carrier in carriers if "shop_" in carrier["surface_id"]
                  and carrier["material_role"] == "glass"]
    shop_cards = [carrier for carrier in carriers if "shop_" in carrier["surface_id"]
                  and carrier["sticker_layer"] == "ground_market_interior"]
    shop_backings = [carrier for carrier in carriers if "shop_" in carrier["surface_id"]
                     and carrier["sticker_layer"] == "dark_cavern_backing"]
    assert len(shop_glass) == 4 and len(shop_cards) == 4 and len(shop_backings) == 4
    assert all(carrier["floor_role"] == "ground_public" for carrier in shop_glass + shop_cards + shop_backings)

    warm_backs = [carrier for carrier in carriers if "interior_warm_plane" in carrier["surface_id"]]
    nave_counters = [carrier for carrier in carriers if "interior_counter" in carrier["surface_id"]]
    shop_cues = [carrier for carrier in carriers if "shop_bay_" in carrier["surface_id"]]
    assert len(warm_backs) == 14 and len(nave_counters) == 14 and len(shop_cues) == 6
    assert all(carrier["floor_role"] == "mezzanine_gallery" for carrier in warm_backs + nave_counters)
    assert all(carrier["sticker_layer"] == "gallery_market_interior"
               and .30 <= carrier["emission_strength_override"] <= .39 for carrier in warm_backs)
    assert all(carrier["sticker_layer"] == "warm_oak_market_joinery" for carrier in nave_counters)
    assert all(carrier["emission_strength_override"] == .10 for carrier in nave_counters)


def test_explicit_terminals_use_adjacent_architectural_finishes():
    carriers = _carriers()
    terminal_tokens = ("terminal", "lantern_front_end", "lantern_rear_end", "ridge_end_rail",
                       "spring_sill", "spring_pier", "spring_capital")
    terminals = [carrier for carrier in carriers if any(token in carrier["surface_id"] for token in terminal_tokens)]
    assert terminals
    forbidden = {"ground_market_interior", "gallery_market_interior", "dark_cavern_backing"}
    assert all(carrier["sticker_layer"] not in forbidden for carrier in terminals)
    assert all(carrier["material_role"] != "glass" for carrier in terminals)


def test_generated_registry_and_contract_are_canonical_only():
    MODULE.main()
    registry = json.loads(MODULE.REGISTRY.read_text(encoding="utf-8"))
    contract = json.loads(MODULE.CONTRACT.read_text(encoding="utf-8"))
    assert registry["tiers"] == [{"id": "canonical", "signature_profile_id": MODULE.profile_id(),
        "family_id": MODULE.family_id(), "width_m": 45.0, "depth_m": 60.0, "occupied_storeys": 2}]
    assert contract["approved_tiers"] == ["canonical"]
    assert contract["continuous_resize_allowed"] is False and contract["vertical_scaling_allowed"] is False


def test_roof_dimension_override_is_generator_compatible_not_landmark_crown():
    profile, _ = MODULE.build_profile()
    nominal = profile["dimension_overrides"]["roof_height_m"]
    landmark_crown = profile["massing_graph"]["height_m"]
    expected_export_extent = nominal * MODULE.GENERIC_ROOF_EXPORT_HEIGHT_FACTOR
    assert nominal == 4.8
    assert 3.7 <= expected_export_extent <= 3.8
    assert abs(nominal - expected_export_extent) < MODULE.MODULE_HEIGHT_TOLERANCE_M
    assert landmark_crown == 16.72 and nominal != landmark_crown
