"""Compile the second geometry-conditioned Sticker Method pilot (Eixample)."""
from __future__ import annotations

import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_eixample_conditioned_geometry_v96 import FLOOR_Z, INNER, OUTER, build_geometry
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzz_eixample_geometry_conditioned_v96.json"
REGISTRY = TOOL_DIR / "eixample_geometry_conditioned_v96.json"
PACKAGE = TOOL_DIR / "eixample_geometry_conditioned_v96_carrier_package.json"
CONTRACT = TOOL_DIR / "eixample_geometry_conditioned_v96_contract.json"
VARIANT_ID = "eixample-apartment-block-classic-geometry-conditioned-4"
SOURCE_VARIANT_ID = "eixample-apartment-block-classic"
FAMILY_ID = "eixample-apartment-block-v96-conditioned-4"
PRINCIPAL = "tools/archetype_compiler/sticker_assets/eixample_v96/principal_elevation_intrinsic.png"
ORDINARY = "tools/archetype_compiler/sticker_assets/eixample_v96/ordinary_elevation_intrinsic.png"
ROOF = "tools/archetype_compiler/sticker_assets/eixample_v96/terrace_roof_intrinsic.png"
TERRACOTTA = "tools/archetype_compiler/sticker_assets/eixample_v96/terracotta_cap_intrinsic.png"
COURTYARD = "tools/archetype_compiler/sticker_assets/eixample_v96/courtyard_floor_intrinsic.png"
FLOOR_UV = ((0.0000, 0.2707), (0.2707, 0.4844), (0.4844, 0.7020), (0.7020, 0.8948))
FLOOR_ROLE = ("ground", "middle", "middle", "top_crown")


def _base_profile() -> dict[str, Any]:
    payload = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(payload["profiles"]["eixample_apartment_block"])


def _segment_frame(points: tuple[tuple[float, float], ...], index: int) -> dict[str, Any]:
    a, b = points[index], points[(index + 1) % len(points)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    span = math.hypot(dx, dy)
    return {
        "centre": [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 9.75],
        "span": span, "angle": math.degrees(math.atan2(dy, dx)),
        "normal": [dy / span, -dx / span],
    }


def _wall_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    by_name = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    result: list[dict[str, Any]] = []
    for prefix, points in (("outer", OUTER), ("court", INNER)):
        for segment in range(8):
            target = f"{prefix}_wall_{segment}"
            mesh = by_name[target]
            frame = _segment_frame(points, segment)
            source = PRINCIPAL if prefix == "outer" and segment == 1 else ORDINARY
            for floor, ((z0, z1), (v0, v1)) in enumerate(zip(zip(FLOOR_Z, FLOOR_Z[1:]), FLOOR_UV)):
                result.append({
                    "id": f"v96_{target}_floor_{floor}", "kind": "carrier_skin",
                    "surface_id": f"{prefix}_segment_{segment}_floor_{floor}",
                    "target_ids": [target], "source_image_path": source,
                    "source_id": "v96_rectified_eixample_principal" if source == PRINCIPAL else "v96_portal_free_ordinary_bays",
                    "axis": "angle", "rotation_z_deg": frame["angle"],
                    "centre": frame["centre"], "span_m": frame["span"], "height_m": z1 - z0,
                    "z_min_m": z0, "z_max_m": z1, "uv_u_min": 0.03, "uv_u_max": 0.97,
                    "uv_v_min": v0, "uv_v_max": v1,
                    "face_indices": mesh["floor_face_indices"][str(floor)],
                    "flip_u": prefix == "court", "material_role": "elevation",
                    "floor_role": FLOOR_ROLE[floor],
                    "finish_class": "geometry_conditioned_floor_sticker",
                    "sticker_layer": f"{FLOOR_ROLE[floor]}_floor", "final_surface_coverage": True,
                })
    return result


def _roof_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    by_name = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    result: list[dict[str, Any]] = [{
        "id": "v96_terrace_roof_sticker", "kind": "carrier_skin",
        "surface_id": "open_courtyard_terrace_roof", "target_ids": ["terrace_roof_ring"],
        "source_image_path": ROOF, "source_id": "v96_intrinsic_terrace_roof",
        "axis": "plan", "centre": [0.0, 0.0, 19.5], "span_m": 46.0, "height_m": 0.1,
        "plan_bounds": [-23.0, 23.0, -23.0, 23.0], "face_indices": list(range(8)),
        "material_role": "roof", "floor_role": "roof",
        "finish_class": "geometry_conditioned_terrace_roof", "sticker_layer": "roof",
        "final_surface_coverage": True,
    }]
    for prefix, points in (("outer_parapet", OUTER), ("court_parapet", INNER)):
        for segment in range(8):
            target = f"{prefix}_{segment}"
            frame = _segment_frame(points, segment)
            result.append({
                "id": f"v96_{target}_crown_sticker", "kind": "carrier_skin",
                "surface_id": f"{target}_visible_crown", "target_ids": [target],
                "source_image_path": ORDINARY, "source_id": "v96_portal_free_crown_band",
                "axis": "angle", "rotation_z_deg": frame["angle"],
                "centre": [*frame["centre"][:2], 20.15], "span_m": frame["span"], "height_m": 1.3,
                "z_min_m": 19.5, "z_max_m": 20.8, "uv_u_min": 0.03, "uv_u_max": 0.97,
                "uv_v_min": 0.8948, "uv_v_max": 1.0, "face_indices": [0],
                "material_role": "elevation", "floor_role": "top_crown",
                "finish_class": "geometry_conditioned_balustrade_crown",
                "sticker_layer": "crown", "final_surface_coverage": True,
            })
            result.append({
                "id": f"v96_{target}_roof_return_sticker", "kind": "carrier_skin",
                "surface_id": f"{target}_inner_return", "target_ids": [target],
                "source_image_path": ROOF, "source_id": "v96_intrinsic_roof_return", "axis": "box_projected",
                "centre": [0.0, 0.0, 20.15], "span_m": 46.0, "height_m": 1.3,
                "box_bounds": [-23.5, 23.5, -23.5, 23.5, 19.5, 20.8], "face_indices": [1],
                "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_roof_parapet_return",
                "sticker_layer": "roof_return", "final_surface_coverage": True,
            })
            result.append({
                "id": f"v96_{target}_terracotta_cap_sticker", "kind": "carrier_skin",
                "surface_id": f"{target}_terracotta_cap", "target_ids": [target],
                "source_image_path": TERRACOTTA, "source_id": "v96_intrinsic_terracotta_coping",
                "axis": "plan", "centre": [0.0, 0.0, 20.8], "span_m": 46.0, "height_m": 0.1,
                "plan_bounds": [-23.5, 23.5, -23.5, 23.5], "face_indices": [2],
                "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_terracotta_parapet_cap",
                "sticker_layer": "roof_cap", "final_surface_coverage": True,
            })
    result.append({
        "id": "v96_roof_access_sticker", "kind": "carrier_skin",
        "surface_id": "roof_access_house", "target_ids": ["roof_access_house"],
        "source_image_path": ROOF, "source_id": "v96_intrinsic_roof_access",
        "axis": "box_projected", "centre": [15.0, 0.0, 20.475], "span_m": 5.0,
        "height_m": 1.95, "box_bounds": [12.5, 17.5, -2.25, 2.25, 19.5, 21.45],
        "face_indices": list(range(len(by_name["roof_access_house"]["faces"]))),
        "material_role": "roof", "floor_role": "roof",
        "finish_class": "geometry_conditioned_roof_access", "sticker_layer": "roof_access",
        "final_surface_coverage": True,
    })
    result.append({
        "id": "v96_courtyard_floor_sticker", "kind": "carrier_skin",
        "surface_id": "inhabited_open_courtyard_floor", "target_ids": ["courtyard_floor"],
        "source_image_path": COURTYARD, "source_id": "v96_intrinsic_courtyard_pavers",
        "axis": "plan", "centre": [0.0, 0.0, 14.5], "span_m": 22.0, "height_m": 0.1,
        "plan_bounds": [-11.0, 11.0, -11.0, 11.0], "face_indices": [0],
        "material_role": "elevation", "floor_role": "ground",
        "finish_class": "geometry_conditioned_courtyard_ground",
        "sticker_layer": "courtyard_ground", "final_surface_coverage": True,
    })
    return result


def _entrance_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    by_name = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    common = {
        "axis": "box_projected", "centre": [17.0, -17.0, 2.0], "span_m": 5.0,
        "height_m": 4.0, "box_bounds": [13.5, 20.5, -20.5, -13.5, 0.0, 4.0],
        "uv_u_min": 0.36, "uv_u_max": 0.64, "uv_v_min": 0.0, "uv_v_max": FLOOR_UV[0][1],
        "material_role": "elevation", "floor_role": "ground",
        "final_surface_coverage": True,
    }
    return [
        {
            "id": "v96_portal_tunnel_sticker", "kind": "carrier_skin",
            "surface_id": "carved_portal_tunnel_returns", "target_ids": ["hero_portal_tunnel"],
            "source_image_path": "tools/archetype_compiler/textures/limestone/albedo.jpg",
            "source_id": "v96_portal_limestone_construction_return",
            "face_indices": list(range(len(by_name["hero_portal_tunnel"]["faces"]))),
            "finish_class": "geometry_conditioned_carved_portal_return",
            "sticker_layer": "entrance_tunnel", **common,
        },
        {
            "id": "v96_portal_door_sticker", "kind": "carrier_skin",
            "surface_id": "recessed_timber_portal_door", "target_ids": ["hero_portal_door"],
            "source_image_path": PRINCIPAL, "source_id": "v96_portal_door_crop",
            "axis": "angle", "rotation_z_deg": 45.0, "centre": [15.9747, -15.9747, 1.95],
            "span_m": 3.4, "height_m": 3.74, "z_min_m": 0.08, "z_max_m": 3.82,
            "face_indices": [0], "uv_u_min": 0.40, "uv_u_max": 0.60,
            "finish_class": "geometry_conditioned_recessed_wood_door",
            "sticker_layer": "entrance_door", "uv_v_min": 0.0, "uv_v_max": FLOOR_UV[0][1],
            "material_role": "elevation", "floor_role": "ground", "final_surface_coverage": True,
        },
    ]


def _balcony_assemblies() -> list[dict[str, Any]]:
    result = []
    for segment in range(8):
        frame = _segment_frame(OUTER, segment)
        for suffix, levels, count in (("first_upper", [4.72], 3), ("upper_pair", [9.72, 14.72], 4)):
            result.append({
                "id": f"v96_outer_balconies_{segment}_{suffix}", "kind": "balcony_array", "axis": "angle",
                "rotation_z_deg": frame["angle"], "centre": [*frame["centre"][:2], 0.0],
                "span_m": frame["span"] - 0.8, "levels_z": levels,
                "segments": count, "segment_gap_m": 0.46,
                "depth_m": 0.34, "slab_height_m": 0.10, "rail_height_m": 0.72,
                "pickets_per_segment": 10, "slab_material": "signature_stone",
                "rail_material": "signature_metal", "shadow_material": "massing_joint",
                "rail_enabled": False, "planter_enabled": False,
            })
    return result


def build_profile() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = _base_profile()
    geometry = build_geometry()
    profile["identity"] = "Classic Eixample Apartment Block V96, geometry-conditioned Sticker Method"
    profile["dimension_overrides"] = {"width_m": 46.0, "depth_m": 46.0, "default_floors": 4,
                                      "min_floors": 4, "max_floors": 4}
    profile["material_overrides"]["primary"] = {
        "base_color": "#d7c9ab", "roughness": 0.78, "texture_key": "limestone", "baked_pbr": True,
    }
    profile["material_overrides"]["roof"].update({"texture_key": "zinc", "baked_pbr": True})
    profile["signature_material_overrides"]["rooflight_glass"] = {
        "base_color": "#26353a", "roughness": 0.18, "metallic": 0.08,
    }
    graph = profile["massing_graph"]
    graph.update({
        "profile": "eixample-geometry-conditioned-sticker-v96-4",
        "description": "Locked low-wide Cerdà octagon with four image-authoritative storeys, broad chamfers, open court and a real recessed portal.",
        "height_m": 21.45,
        "reference_dimensions": {"width_m": 46.0, "depth_m": 46.0, "floors": 4,
                                 "ground_height_m": 4.5, "repeatable_middle_height_m": 5.0,
                                 "top_occupied_height_m": 5.0},
        "nodes": [{
            "id": "eixample_v96_locked_carrier", "kind": "locked_mesh_bundle",
            "location": [0.0, 0.0, 0.0], "geometry_sha256": geometry["geometry_sha256"],
            "meshes": [{
                "name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
                "material": "roof" if mesh["material_domain"] == "roof_only" else "primary",
                "material_domain": mesh["material_domain"],
            } for mesh in geometry["meshes"]],
        }] + [
            {"id": "v96_rooflight_front", "kind": "box", "size": [4.2, 1.4, 0.28],
             "location": [0.0, -13.2, 19.70], "material": "rooflight_glass", "bevel_m": 0.05},
            {"id": "v96_rooflight_rear", "kind": "box", "size": [4.2, 1.4, 0.28],
             "location": [0.0, 13.2, 19.70], "material": "rooflight_glass", "bevel_m": 0.05},
            {"id": "v96_rooflight_left", "kind": "box", "size": [1.4, 4.2, 0.28],
             "location": [-13.2, 0.0, 19.70], "material": "rooflight_glass", "bevel_m": 0.05},
            {"id": "v96_rooflight_right", "kind": "box", "size": [1.4, 4.2, 0.28],
             "location": [13.2, 0.0, 19.70], "material": "rooflight_glass", "bevel_m": 0.05},
        ],
        "voids": [{"id": "eixample_open_courtyard", "size": [22.0, 22.0, 21.45],
                    "location": [0.0, 0.0, 10.725], "purpose": "true open Eixample light court"},
                   {"id": "eixample_recessed_portal", "size": [3.4, 1.45, 4.0],
                    "location": [17.0, -17.0, 2.0], "purpose": "cavernous diagonal entrance"}],
        "assemblies": _wall_carriers(geometry) + _roof_carriers(geometry)
                      + _entrance_carriers(geometry) + [{
                          "id": "v96_arched_portal_trim", "kind": "arched_portal_trim",
                          "centre_xy": [17.0, -17.0], "rotation_z_deg": 45.0,
                          "spring_z_m": 2.55, "inner_radius_m": 1.70,
                          "ring_width_m": 0.24, "depth_m": 0.30,
                          "material": "signature_stone",
                      }] + _balcony_assemblies(),
        "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "aerial", "facade_close", "context"],
        "presentation_camera": {"hero_side": "right", "oblique_x_scale": 1.88,
                                "street_x_scale": 1.24,
                                "identity_distance_scale": 1.0, "street_distance_scale": 1.0},
        "floor_sticker_contract": {
            "required": True, "floor_count": 4, "floor_datums_m": list(FLOOR_Z),
            "roof_starts_at_z_m": 19.5, "floor_roles": list(FLOOR_ROLE),
            "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
            "forbid_roof_below_roof_datum": True,
        },
        "final_surface_audit": {"required": True, "forbid_generic_materials": True,
                                "required_finish_property": "final_surface_coverage"},
    })
    profile["production_contract"].update({
        "representation": "locked_geometry_plus_geometry_conditioned_floor_stickers",
        "placement_model": "select_and_place_landmark",
        "image_authority": "exact_reference_views_override_conflicting_legacy_floor_metadata",
        "architect_score_target": 95,
        "clay_lock": {"required": True, "status": "v96_locked"},
        "floor_sticker_method": {
            "schema": "geometry-conditioned-continuous-sticker-contract@1",
            "roles": list(FLOOR_ROLE) + ["roof"], "architect_score_target": 95,
            "approval_space": "rendered_on_locked_carrier", "post_generation_crop_allowed": False,
            "post_generation_nonuniform_scale_allowed": False,
        },
    })
    return condition_profile(profile, geometry, score_target=95)


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    profile, package = build_profile()
    # The catalogue exporter accepts the source variant id, while the rollout
    # registry retains a distinct package id.  Override both lookup routes so
    # generate_family cannot silently fall back to the legacy rectangular
    # profile when it is invoked with the real catalogue variant.
    payload = {"schema": "architectural-signatures@1",
               "override_profiles": ["eixample_apartment_block"],
               "profiles": {VARIANT_ID: profile, SOURCE_VARIANT_ID: deepcopy(profile),
                            "eixample_apartment_block": deepcopy(profile)}}
    registry = {"schema": "catalogue-rollout-batch@1", "pipeline_version": "v96",
                "batch_id": "EIXAMPLE-GEOMETRY-CONDITIONED-STICKER-V96", "paid_facade_calls": 0,
                "entries": [{"archetype_id": "eixample_apartment_block", "variant_id": VARIANT_ID,
                             "family_id": FAMILY_ID, "width_m": 46.0, "depth_m": 46.0, "floors": 4}]}
    contract = {"schema": "geometry-conditioned-continuous-sticker-contract@1",
                "building_id": "eixample-apartment-block-classic", "score_target": 95,
                "locked_geometry_sha256": package["locked_geometry_sha256"],
                "carrier_package_sha256": package["package_sha256"],
                "carrier_count": package["carrier_count"], "status": package["status"],
                "hard_stops": package["hard_stops"] + ["exposed_carrier", "closed_courtyard",
                    "wrong_visible_storey_count", "floor_roof_overlap", "flat_portal", "cross_view_mismatch"]}
    return payload, registry, package, contract


def main() -> None:
    values = build_outputs()
    for path, value in zip((OUTPUT, REGISTRY, PACKAGE, CONTRACT), values):
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "carrier_count": values[2]["carrier_count"],
                      "status": values[2]["status"]}, indent=2))


if __name__ == "__main__":
    main()
