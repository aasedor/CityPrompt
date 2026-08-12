"""Compile three discrete, non-stretched V97 LEGO mill tiers."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_functionalist_mill_sticker_lego_v97 import (
    BAY_M, ENTRANCE_RECESS_M, FLOOR_H_M, SIZE_MATRIX, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzz_functionalist_mill_sticker_lego_v97.json"
REGISTRY = TOOL_DIR / "functionalist_mill_sticker_lego_v97.json"
PACKAGE = TOOL_DIR / "functionalist_mill_sticker_lego_v97_carrier_packages.json"
CONTRACT = TOOL_DIR / "functionalist_mill_sticker_lego_v97_contract.json"
SOURCE_VARIANT_ID = "brick_multistory_mill"
PROFILE_PREFIX = "functional-mill-sticker-lego"
ORDINARY = "tools/archetype_compiler/sticker_assets/functional_mill_v97/ordinary_five_bay_intrinsic.png"
ENTRANCE = "tools/archetype_compiler/sticker_assets/functional_mill_v97/entrance_bay_square.png"
BRICK_RETURN = "tools/archetype_compiler/sticker_assets/functional_mill_v97/brick_return_intrinsic.png"
ROOF = "tools/archetype_compiler/sticker_assets/functional_mill_v97/slate_roof_intrinsic.png"
TIMBER = "tools/archetype_compiler/sticker_assets/functional_mill_v97/timber_service_intrinsic.png"
ROLE_V = {"ground": (0.0, 0.2), "middle_repeat": (0.4, 0.6), "top_cornice": (0.8, 1.0)}


def profile_id(size_id: str) -> str:
    return f"{PROFILE_PREFIX}-{size_id}"


def family_id(size_id: str) -> str:
    return f"functionalist-brick-mill-v97-{size_id}"


def _base_profile() -> dict[str, Any]:
    payload = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(payload["profiles"]["industrial_brick_original_mill"])


def _wall_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    width, depth = float(geometry["width_m"]), float(geometry["depth_m"])
    result: list[dict[str, Any]] = []
    for mesh in geometry["meshes"]:
        name = str(mesh["name"])
        if mesh.get("material_domain") != "vertical_occupied_floor":
            continue
        axis, bay, floor, role = str(mesh["axis"]), int(mesh["bay"]), int(mesh["floor"]), str(mesh["floor_role"])
        source = (ENTRANCE if axis == "front" and bay == 0 and floor == 0
                  else BRICK_RETURN if axis == "wing_return" else ORDINARY)
        xs = [float(vertex[0]) for vertex in mesh["vertices"]]
        ys = [float(vertex[1]) for vertex in mesh["vertices"]]
        if axis in {"front", "rear"}:
            along_min, along_max = min(xs), max(xs)
            centre = [(along_min + along_max) / 2, sum(ys) / len(ys), (floor + 0.5) * FLOOR_H_M]
        else:
            along_min, along_max = min(ys), max(ys)
            centre = [sum(xs) / len(xs), (along_min + along_max) / 2, (floor + 0.5) * FLOOR_H_M]
        if source == ENTRANCE:
            u0, u1, v0, v1 = 0.0, 1.0, 0.0, 1.0
        elif source == ORDINARY:
            phase = bay % 5
            u0, u1 = phase / 5, (phase + 1) / 5
            v0, v1 = ROLE_V[role]
        else:
            u0, u1, v0, v1 = 0.0, 1.0, 0.0, 1.0
        result.append({
            "id": f"v97_{name}_sticker", "kind": "carrier_skin",
            "surface_id": f"{axis}_bay_{bay}_floor_{floor}", "target_ids": [name],
            "source_image_path": source,
            "source_id": ("v97_fixed_entrance" if source == ENTRANCE else
                          "v97_intrinsic_brick_return" if source == BRICK_RETURN else
                          "v97_rectified_5x5_mill_master"),
            "axis": axis if axis != "wing_return" else "right", "centre": centre,
            "span_m": along_max - along_min, "height_m": FLOOR_H_M,
            "u_min_m": along_min, "u_max_m": along_max,
            "z_min_m": floor * FLOOR_H_M, "z_max_m": (floor + 1) * FLOOR_H_M,
            "uv_u_min": u0, "uv_u_max": u1, "uv_v_min": v0, "uv_v_max": v1,
            "flip_u": axis in {"rear", "left"}, "material_role": "elevation",
            "floor_role": role, "finish_class": "geometry_conditioned_5m_floor_bay_sticker",
            "sticker_layer": f"{role}_bay", "final_surface_coverage": True,
        })
    return result


def _portal_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    width, depth = float(geometry["width_m"]), float(geometry["depth_m"])
    cx = -width / 2 + BAY_M / 2
    y0 = -depth / 2 + ENTRANCE_RECESS_M
    y1 = y0 + 1.25
    common = {
        "source_image_path": BRICK_RETURN, "source_id": "v97_intrinsic_brick_construction_return",
        "material_role": "elevation", "floor_role": "ground",
        "finish_class": "geometry_conditioned_portal_return", "sticker_layer": "entrance_tunnel",
        "final_surface_coverage": True,
    }
    result: list[dict[str, Any]] = []
    for face, label in enumerate(("left_jamb", "right_jamb", "soffit")):
        result.append({
            "id": f"v97_portal_{label}", "kind": "carrier_skin",
            "surface_id": f"fixed_portal_{label}", "target_ids": ["fixed_entrance_tunnel"],
            "axis": "box_projected", "centre": [cx, (y0 + y1) / 2, 1.925],
            "span_m": 2.0, "height_m": 3.85,
            "box_bounds": [cx - 1.0, cx + 1.0, y0, y1, 0.0, 3.85],
            "face_indices": [face], **common,
        })
    result.extend([{
        "id": "v97_portal_door", "kind": "carrier_skin",
        "surface_id": "fixed_recessed_entrance_door", "target_ids": ["fixed_entrance_door"],
        "source_image_path": ENTRANCE, "source_id": "v97_fixed_entrance_door_crop",
        "axis": "front", "centre": [cx, y1, FLOOR_H_M / 2], "span_m": BAY_M, "height_m": FLOOR_H_M,
        "u_min_m": cx - BAY_M / 2, "u_max_m": cx + BAY_M / 2,
        "z_min_m": 0.0, "z_max_m": FLOOR_H_M,
        "uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0,
        "face_indices": [0], "material_role": "elevation", "floor_role": "ground",
        "finish_class": "geometry_conditioned_recessed_door", "sticker_layer": "entrance_door",
        "final_surface_coverage": True,
    }, {
        "id": "v97_portal_threshold", "kind": "carrier_skin",
        "surface_id": "fixed_entrance_threshold", "target_ids": ["fixed_entrance_threshold"],
        "source_image_path": BRICK_RETURN, "source_id": "v97_intrinsic_threshold",
        "axis": "plan", "centre": [cx, (y0 + y1) / 2, 0.025], "span_m": 2.0, "height_m": 0.05,
        "plan_bounds": [cx - 1.0, cx + 1.0, y0, y1], "face_indices": [0],
        "material_role": "elevation", "floor_role": "ground",
        "finish_class": "geometry_conditioned_threshold", "sticker_layer": "entrance_threshold",
        "final_surface_coverage": True,
    }])
    return result


def _roof_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    width, depth = float(geometry["width_m"]), float(geometry["depth_m"])
    wall_top = float(geometry["floor_count"]) * FLOOR_H_M
    result: list[dict[str, Any]] = []
    for mesh in geometry["meshes"]:
        name = str(mesh["name"])
        if name.startswith(("roof_front_strip_", "roof_rear_strip_")):
            index = int(mesh["strip"])
            x0, x1 = -width / 2 + BAY_M + index * BAY_M, -width / 2 + BAY_M + (index + 1) * BAY_M
            front = mesh["roof_side"] == "front"
            bounds = [x0, x1, -depth / 2, 0.0] if front else [x0, x1, 0.0, depth / 2]
            result.append({
                "id": f"v97_{name}_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": ROOF,
                "source_id": "v97_seamless_slate_roof", "axis": "plan",
                "centre": [(x0 + x1) / 2, (-depth / 4 if front else depth / 4), wall_top],
                "span_m": BAY_M, "height_m": depth / 2, "plan_bounds": bounds,
                "uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0,
                "uv_v_max": depth / 10.0, "face_indices": [0],
                "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_repeat_roof_strip",
                "sticker_layer": "roof_repeat", "final_surface_coverage": True,
            })
        elif name in {"roof_left_hip", "roof_right_hip"}:
            left = name.endswith("left_hip")
            bounds = [-width / 2, -width / 2 + BAY_M, -depth / 2, depth / 2] if left else [width / 2 - BAY_M, width / 2, -depth / 2, depth / 2]
            result.append({
                "id": f"v97_{name}_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": ROOF,
                "source_id": "v97_fixed_slate_hip", "axis": "plan", "centre": [sum(bounds[:2]) / 2, 0.0, wall_top],
                "span_m": BAY_M, "height_m": depth, "plan_bounds": bounds,
                "uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": depth / BAY_M,
                "face_indices": list(range(len(mesh["faces"]))), "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_fixed_hip", "sticker_layer": "roof_fixed_end",
                "final_surface_coverage": True,
            })
        elif name == "fixed_rear_annex_roof":
            xs = [vertex[0] for vertex in mesh["vertices"]]
            ys = [vertex[1] for vertex in mesh["vertices"]]
            bounds = [min(xs), max(xs), min(ys), max(ys)]
            result.append({
                "id": "v97_fixed_rear_annex_roof_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": ROOF,
                "source_id": "v97_fixed_annex_slate", "axis": "plan",
                "centre": [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, wall_top],
                "span_m": max(xs) - min(xs), "height_m": max(ys) - min(ys),
                "plan_bounds": bounds, "uv_u_min": 0.0, "uv_u_max": 4.0,
                "uv_v_min": 0.0, "uv_v_max": 2.0, "face_indices": [0],
                "material_role": "elevation", "floor_role": "fixed_annex_roof",
                "finish_class": "geometry_conditioned_fixed_annex_roof",
                "sticker_layer": "roof_fixed_annex", "final_surface_coverage": True,
            })
        elif name == "fixed_entrance_wing_soffit":
            xs = [vertex[0] for vertex in mesh["vertices"]]
            ys = [vertex[1] for vertex in mesh["vertices"]]
            result.append({
                "id": "v97_fixed_entrance_soffit_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": BRICK_RETURN,
                "source_id": "v97_fixed_brick_entrance_soffit", "axis": "plan",
                "centre": [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, wall_top - 0.04],
                "span_m": max(xs) - min(xs), "height_m": max(ys) - min(ys),
                "plan_bounds": [min(xs), max(xs), min(ys), max(ys)],
                "uv_u_min": 0.0, "uv_u_max": 2.0, "uv_v_min": 0.0, "uv_v_max": 0.4,
                "face_indices": [0], "material_role": "elevation", "floor_role": "fixed_entrance_eave",
                "finish_class": "geometry_conditioned_entrance_soffit",
                "sticker_layer": "fixed_entrance_eave", "final_surface_coverage": True,
            })
        elif name == "fixed_entrance_wing_fascia":
            xs = [vertex[0] for vertex in mesh["vertices"]]
            zs = [vertex[2] for vertex in mesh["vertices"]]
            result.append({
                "id": "v97_fixed_entrance_fascia_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": BRICK_RETURN,
                "source_id": "v97_fixed_brick_entrance_fascia", "axis": "front",
                "centre": [(min(xs) + max(xs)) / 2, -depth / 2, (min(zs) + max(zs)) / 2],
                "span_m": max(xs) - min(xs), "height_m": max(zs) - min(zs),
                "u_min_m": min(xs), "u_max_m": max(xs), "z_min_m": min(zs), "z_max_m": max(zs),
                "uv_u_min": 0.0, "uv_u_max": 2.0, "uv_v_min": 0.0, "uv_v_max": 0.06,
                "face_indices": [0], "material_role": "elevation", "floor_role": "fixed_entrance_eave",
                "finish_class": "geometry_conditioned_entrance_fascia",
                "sticker_layer": "fixed_entrance_eave", "final_surface_coverage": True,
            })
        elif name == "fixed_roof_service_dormer_cap":
            xs = [vertex[0] for vertex in mesh["vertices"]]
            ys = [vertex[1] for vertex in mesh["vertices"]]
            result.append({
                "id": "v97_fixed_dormer_cap_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": ROOF,
                "source_id": "v97_fixed_dormer_slate_cap", "axis": "plan",
                "centre": [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(vertex[2] for vertex in mesh["vertices"])],
                "span_m": max(xs) - min(xs), "height_m": max(ys) - min(ys),
                "plan_bounds": [min(xs), max(xs), min(ys), max(ys)],
                "uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0,
                "face_indices": list(range(len(mesh["faces"]))), "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_fixed_dormer_cap",
                "sticker_layer": "roof_fixed_dormer", "final_surface_coverage": True,
            })
        elif name == "fixed_roof_service_dormer_body":
            xs = [vertex[0] for vertex in mesh["vertices"]]
            ys = [vertex[1] for vertex in mesh["vertices"]]
            zs = [vertex[2] for vertex in mesh["vertices"]]
            result.append({
                "id": "v97_fixed_dormer_timber_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": TIMBER,
                "source_id": "v97_fixed_timber_service_dormer", "axis": "box_projected",
                "centre": [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2],
                "span_m": max(xs) - min(xs), "height_m": max(zs) - min(zs),
                "box_bounds": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
                "face_indices": list(range(len(mesh["faces"]))), "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_timber_dormer",
                "sticker_layer": "roof_fixed_dormer", "final_surface_coverage": True,
            })
        elif name.startswith("fixed_chimney_"):
            xs = [vertex[0] for vertex in mesh["vertices"]]
            ys = [vertex[1] for vertex in mesh["vertices"]]
            zs = [vertex[2] for vertex in mesh["vertices"]]
            result.append({
                "id": f"v97_{name}_sticker", "kind": "carrier_skin",
                "surface_id": name, "target_ids": [name], "source_image_path": BRICK_RETURN,
                "source_id": "v97_intrinsic_brick_chimney", "axis": "box_projected",
                "centre": [(min(xs) + max(xs)) / 2, 0.0, (min(zs) + max(zs)) / 2],
                "span_m": max(xs) - min(xs), "height_m": max(zs) - min(zs),
                "box_bounds": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
                "face_indices": list(range(len(mesh["faces"]))),
                "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_brick_chimney", "sticker_layer": "roof_accessory",
                "final_surface_coverage": True,
            })
    return result


def build_profile(size_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    geometry = build_geometry(size_id)
    profile = _base_profile()
    spec = SIZE_MATRIX[size_id]
    width, depth, floors = float(spec["width_m"]), float(spec["depth_m"]), int(spec["floors"])
    wall_top = floors * FLOOR_H_M
    profile["identity"] = f"Functionalist Brick Mill V97 Sticker LEGO — {size_id}"
    profile["dimension_overrides"] = {"width_m": width, "depth_m": depth,
        "default_floors": floors, "min_floors": floors, "max_floors": floors}
    profile["material_overrides"]["primary"] = {
        "base_color": "#6f3026", "roughness": 0.86, "texture_key": "red_brick", "baked_pbr": True,
    }
    profile["material_overrides"]["roof"] = {
        "base_color": "#4b4c4c", "roughness": 0.82, "metallic": 0.02,
        "texture_key": "standing_seam", "baked_pbr": True,
    }
    graph = profile.setdefault("massing_graph", {"schema": "massing-graph@1"})
    graph.update({
        "profile": profile_id(size_id),
        "description": "Discrete 5 m bay and floor modules around a fixed recessed stair wing, rear annex and roof dormer; no sticker stretching.",
        "height_m": wall_top + depth * 0.18 + 1.65,
        "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": floors,
                                 "bay_module_m": BAY_M, "floor_module_m": FLOOR_H_M},
        "nodes": [{
            "id": f"v97_locked_carrier_{size_id}", "kind": "locked_mesh_bundle",
            "location": [0.0, 0.0, 0.0], "geometry_sha256": geometry["geometry_sha256"],
            "meshes": [{"name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
                        "material": "roof" if mesh["material_domain"] in {"roof_only", "roof_access"} else "primary",
                        "material_domain": mesh["material_domain"]} for mesh in geometry["meshes"]],
        }],
        "voids": [{"id": "fixed_recessed_entrance", "size": [2.0, 1.25, 3.85],
                   "location": [-width / 2 + 2.5, -depth / 2 + ENTRANCE_RECESS_M + 0.625, 1.925],
                   "purpose": "single nonrepeatable entrance tunnel"}],
        "assemblies": _wall_carriers(geometry) + _portal_carriers(geometry) + _roof_carriers(geometry) + [{
            "id": "v97_arched_entrance_trim", "kind": "arched_portal_trim",
            "centre_xy": [-width / 2 + 2.5, -depth / 2 + ENTRANCE_RECESS_M], "rotation_z_deg": 0.0,
            "spring_z_m": 2.65, "inner_radius_m": 1.0, "ring_width_m": 0.18,
            "depth_m": 0.24, "material": "primary",
        }],
        "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial", "context"],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.92,
                                "street_x_scale": 0.72, "identity_distance_scale": 1.0,
                                "street_distance_scale": 1.0},
        "floor_sticker_contract": {"required": True, "floor_count": floors,
            "floor_datums_m": geometry["floor_datums_m"], "roof_starts_at_z_m": wall_top,
            "roles": ["ground"] + ["middle_repeat"] * (floors - 2) + ["top_cornice"],
            "bay_module_m": BAY_M, "uv_cell": [0.2, 0.2],
            "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
            "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
        "final_surface_audit": {"required": True, "forbid_generic_materials": True,
                                "required_finish_property": "final_surface_coverage"},
    })
    profile.setdefault("production_contract", {}).update({
        "identity_mode": "massing_graph",
        "fixed_identity": [
            "recessed arched entrance tunnel and trim",
            "hipped roof end assemblies",
            "three brick chimney assemblies",
            "top-floor cornice band",
            "5 m recessed entrance/stair wing",
            "fixed two-storey rear service annex",
            "fixed timber roof service dormer",
        ],
        "repeatable_capacity": [
            "5 m industrial window bays",
            "5 m middle-floor bands",
            "5 m roof strips",
        ],
        "required_reference_roles": ["street_identity", "oblique_massing", "roof_or_aerial"],
        "representation": "locked_geometry_plus_discrete_5m_floor_bay_stickers",
        "placement_model": "lego_polygon_fit_with_discrete_size_tiers",
        "architect_score_target": 95,
        "clay_lock": {"required": True, "status": f"v97_{size_id}_locked"},
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size_id,
            "fixed": ["one-bay entrance wing", "far end bay", "top/cornice", "hip ends", "three chimneys"],
            "repeatable": ["5m ordinary bays", "5m middle floors", "5m roof strips"],
            "whole_modules_only": True, "nonuniform_sticker_scale_allowed": False},
    })
    conditioned, package = condition_profile(profile, geometry, score_target=95)
    return conditioned, package, geometry


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    profiles: dict[str, Any] = {}
    packages: dict[str, Any] = {}
    geometries: dict[str, Any] = {}
    entries = []
    for size_id, spec in SIZE_MATRIX.items():
        profile, package, geometry = build_profile(size_id)
        profiles[profile_id(size_id)] = profile
        packages[size_id] = package
        geometries[size_id] = geometry
        entries.append({"archetype_id": "functionalist_brick_industrial", "variant_id": SOURCE_VARIANT_ID,
                        "signature_profile_id": profile_id(size_id), "family_id": family_id(size_id),
                        "width_m": spec["width_m"], "depth_m": spec["depth_m"], "floors": spec["floors"]})
    profiles[SOURCE_VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    payload = {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles}
    registry = {"schema": "catalogue-rollout-batch@1", "pipeline_version": "v97",
                "batch_id": "FUNCTIONALIST-MILL-STICKER-LEGO-V97", "paid_facade_calls": 2,
                "entries": entries}
    package_payload = {"schema": "siteforge.sticker-lego-size-matrix@1", "packages": packages}
    contract = {"schema": "geometry-conditioned-sticker-lego-contract@1",
                "building_id": "functionalist-brick-industrial--brick-multistory-mill",
                "score_target": 95, "size_matrix": SIZE_MATRIX, "bay_module_m": BAY_M,
                "floor_module_m": FLOOR_H_M, "whole_modules_only": True,
                "statuses": {key: value["status"] for key, value in packages.items()},
                "geometry_sha256": {key: value["geometry_sha256"] for key, value in geometries.items()},
                "carrier_counts": {key: value["carrier_count"] for key, value in packages.items()},
                "hard_stops": ["partial_bay", "nonuniform_sticker_scale", "duplicated_entrance",
                    "repeated_ground_or_crown", "floor_roof_overlap", "exposed_carrier",
                    "window_aspect_drift", "architect_score_below_95"]}
    return payload, registry, package_payload, contract


def main() -> None:
    outputs = build_outputs()
    for path, payload in zip((OUTPUT, REGISTRY, PACKAGE, CONTRACT), outputs):
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "statuses": outputs[3]["statuses"],
                      "carrier_counts": outputs[3]["carrier_counts"]}, indent=2))


if __name__ == "__main__":
    main()
