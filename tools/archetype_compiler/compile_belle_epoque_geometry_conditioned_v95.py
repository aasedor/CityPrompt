"""Compile the bounded Belle Epoque V95 geometry-conditioned Sticker pilot."""
from __future__ import annotations

import json
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_belle_epoque_continuous_geometry_v94 import build_continuous_geometry
from compile_belle_epoque_continuous_sticker_v94 import build_profile as build_v94_profile
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzz_belle_epoque_geometry_conditioned_v95.json"
REGISTRY = TOOL_DIR / "belle_epoque_geometry_conditioned_v95.json"
PACKAGE = TOOL_DIR / "belle_epoque_geometry_conditioned_v95_carrier_package.json"
CONTRACT = TOOL_DIR / "belle_epoque_geometry_conditioned_v95_contract.json"
VARIANT_ID = "grand-magasin-belle-epoque-geometry-conditioned-5"
FAMILY_ID = "belle-epoque-grand-magasin-v95-conditioned-5"


def _sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_v95_geometry() -> dict[str, Any]:
    """Refine only the V94 dormer proportions while preserving face topology."""
    geometry = deepcopy(build_continuous_geometry())
    for mesh in geometry["meshes"]:
        name = str(mesh.get("name", ""))
        if not name.startswith("dormer_"):
            continue
        vertices = mesh["vertices"]
        centre_x = (min(vertex[0] for vertex in vertices) + max(vertex[0] for vertex in vertices)) / 2
        centre_y = (min(vertex[1] for vertex in vertices) + max(vertex[1] for vertex in vertices)) / 2
        if name.startswith(("dormer_front_", "dormer_rear_")):
            tangent_x, tangent_y = 0.58, 0.74
        else:
            tangent_x, tangent_y = 0.74, 0.58
        mesh["vertices"] = [
            [
                round(centre_x + (float(x) - centre_x) * tangent_x, 6),
                round(centre_y + (float(y) - centre_y) * tangent_y, 6),
                round(22.10 + (float(z) - 22.10) * 0.62, 6),
            ]
            for x, y, z in vertices
        ]
        mesh["v95_dormer_proportion_lock"] = {
            "tangent_scale": 0.58, "depth_scale": 0.74, "height_scale": 0.62,
        }
    # The cupola base crosses the occupied/roof datum in V94 as one cylinder.
    # Split it at 20.5 m so floor and roof agents can own disjoint faces.
    split_meshes: list[dict[str, Any]] = []
    for mesh in geometry["meshes"]:
        if mesh["name"] != "corner_upper_tower":
            split_meshes.append(mesh)
            continue
        source = deepcopy(mesh)
        for name, bottom, top, domain in (
            ("corner_upper_tower", 18.4, 20.5, "vertical_occupied_floor"),
            ("cupola_roof_transition", 20.5, 23.048, "roof_only"),
        ):
            piece = deepcopy(source)
            piece["name"] = name
            piece["material_domain"] = domain
            piece["vertices"] = [
                [float(x), float(y), bottom if index < 16 or index == 32 else top]
                for index, (x, y, _z) in enumerate(source["vertices"])
            ]
            piece["v95_split_at_roof_datum_m"] = 20.5
            split_meshes.append(piece)
    geometry["meshes"] = split_meshes
    geometry["schema"] = "belle-epoque-geometry-conditioned-v95@1"
    geometry["geometry_sha256"] = _sha256(
        {key: value for key, value in geometry.items() if key != "geometry_sha256"}
    )
    return geometry


def _dormer_carriers() -> list[dict[str, Any]]:
    root = "docs/reviews/catalogue-rollout-v91/three-all-surface-sticker-pilot/belle-epoque-grand-magasin"
    zinc = "tools/archetype_compiler/sticker_assets/belle_epoque_v95/dormer_zinc_intrinsic.png"
    result: list[dict[str, Any]] = []
    groups = {
        "front": (3, "front", zinc, [0.0, -1.0], False),
        "rear": (3, "rear", zinc, [0.0, 1.0], True),
        "left": (2, "left", zinc, [-1.0, 0.0], True),
        "right": (2, "right", zinc, [1.0, 0.0], False),
    }
    for direction, (count, axis, source, normal, flip) in groups.items():
        hero_face = 0 if direction in {"front", "left"} else 1
        for index in range(count):
            target = f"dormer_{direction}_{index}"
            result.append({
                "id": f"v95_{target}_front_sticker", "kind": "carrier_skin",
                "surface_id": f"{target}_front", "target_ids": [target],
                "source_image_path": source, "source_id": f"v95_{direction}_dormer_carrier",
                "axis": axis, "centre": [0.0, 0.0, 15.5], "span_m": 36.0,
                "height_m": 31.0, "z_min_m": 0.0, "z_max_m": 31.0,
                "face_indices": [hero_face], "flip_u": flip,
                "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_zinc_dormer_front_behind_physical_window",
                "sticker_layer": "dormer_front", "final_surface_coverage": True,
            })
            remaining = [face for face in range(7) if face != hero_face]
            result.append({
                "id": f"v95_{target}_return_sticker", "kind": "carrier_skin",
                "surface_id": f"{target}_returns", "target_ids": [target],
                "source_image_path": zinc, "source_id": "v95_directional_dormer_zinc",
                "axis": "box_projected", "centre": [0.0, 0.0, 15.5],
                "span_m": 36.0, "height_m": 31.0,
                "box_bounds": [-18.0, 18.0, -17.0, 17.0, 20.5, 25.5],
                "normal_z_min": -1.01, "normal_z_max": 1.01,
                "face_indices": remaining, "material_role": "roof", "floor_role": "roof",
                "finish_class": "geometry_conditioned_dormer_cheek_cap_return",
                "sticker_layer": "dormer_return", "final_surface_coverage": True,
            })
    return result


def _dormer_trim_assemblies() -> list[dict[str, Any]]:
    return [
        {
            "id": f"v95_{direction}_dormer_frames", "kind": "dormer_trim_system",
            "direction": direction, "centres": centres, "front_plane": plane,
            "outward_xy": outward, "tangent_xy": tangent, "width_m": 1.45,
            "sill_z_m": 22.15, "shoulder_z_m": 23.28, "apex_z_m": 23.99,
            "profile_m": 0.038, "material": "signature_bronze",
            "flashing_material": "roof",
            # The reference dormers have small, recessed dark panes inside a
            # much larger zinc pediment.  Keeping these dimensions explicit
            # prevents the glass from reading as a pale applied rectangle.
            "window_width_m": 0.66, "window_height_m": 0.62,
            "window_sill_z_m": 22.29,
            "glass_profile": "heritage_dormer_dark",
            "glass_material": "glass", "interior_material": "interior_warm",
            "semantic_role": "registered_dormer_front_cheek_and_pediment_frame",
        }
        for direction, centres, plane, outward, tangent in (
            ("front", [-9.0, 0.0, 9.0], -15.6, [0.0, -1.0], [1.0, 0.0]),
            ("rear", [-9.0, 0.0, 9.0], 15.6, [0.0, 1.0], [1.0, 0.0]),
            ("left", [-5.0, 5.0], -15.6, [-1.0, 0.0], [0.0, 1.0]),
            ("right", [-5.0, 5.0], 15.6, [1.0, 0.0], [0.0, 1.0]),
        )
    ]


def _outer_corner_return_carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind every thin streetwall end cap to its adjoining elevation atlas."""

    root = "docs/reviews/catalogue-rollout-v91/three-all-surface-sticker-pilot/belle-epoque-grand-magasin"
    configs = (
        ("front_right", "facade_front_continuous_wall", [2, 6, 10, 14, 19, 25], "right", f"{root}/sticker-right.png", False),
        ("front_left", "facade_front_continuous_wall", [4, 8, 12, 16, 21, 27], "left", f"{root}/sticker-left.png", True),
        ("right_front", "facade_right_continuous_wall", [1, 5, 9, 13, 18, 24], "front", f"{root}/sticker-front.png", False),
        ("right_rear", "facade_right_continuous_wall", [3, 7, 11, 15, 20, 26], "rear", f"{root}/sticker-rear.png", True),
        ("rear_right", "facade_rear_continuous_wall", [2, 6, 10, 14, 19, 25], "right", f"{root}/sticker-right.png", False),
        ("rear_left", "facade_rear_continuous_wall", [4, 8, 12, 16, 21, 27], "left", f"{root}/sticker-left.png", True),
        ("left_front", "facade_left_continuous_wall", [1, 5, 9, 13, 18, 24], "front", f"{root}/sticker-front.png", False),
        ("left_rear", "facade_left_continuous_wall", [3, 7, 11, 15, 20, 26], "rear", f"{root}/sticker-rear.png", True),
    )
    mesh_by_name = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    crops = (0.0, 0.287109375, 0.4482421875, 0.609375, 0.783203125, 0.9189453125)
    roles = ("ground", "middle", "middle", "middle", "top_crown")
    result = []
    for name, target, faces, axis, source, flip in configs:
        # The generated elevation masters contain pale isolation pixels at
        # their extreme outer bounds. Sampling those into a 10 cm return made
        # a full-height white stripe in aerial views. Treat this thin return as
        # an explicit limestone construction joint with a de-lit metric skin.
        source = "tools/archetype_compiler/textures/limestone/albedo.jpg"
        along_span = 34.0 if axis in {"left", "right"} else 36.0
        mesh = mesh_by_name[target]
        for floor in range(5):
            selected = [face for face in faces if face in mesh["floor_face_indices"][str(floor)]]
            if not selected:
                raise RuntimeError(f"corner return {name} has no faces on floor {floor}")
            z_min, z_max = floor * 4.1, (floor + 1) * 4.1
            result.append({
                "id": f"v95_corner_return_{name}_floor_{floor}", "kind": "carrier_skin",
                "surface_id": f"corner_return_{name}_floor_{floor}", "target_ids": [target],
                "source_image_path": source, "source_id": f"v95_limestone_corner_joint_floor_{floor}",
                "axis": axis, "centre": [0.0, 0.0, (z_min + z_max) / 2], "span_m": along_span,
                "height_m": 4.1, "z_min_m": z_min, "z_max_m": z_max,
                "uv_v_min": crops[floor], "uv_v_max": crops[floor + 1],
                "u_min_m": -17.0 if axis in {"left", "right"} else -18.0,
                "u_max_m": 17.0 if axis in {"left", "right"} else 18.0,
                "face_indices": selected, "flip_u": flip,
                "material_role": "elevation", "floor_role": roles[floor],
                "finish_class": "geometry_conditioned_floor_addressed_limestone_corner_joint",
                "sticker_layer": "corner_return", "final_surface_coverage": True,
                "shared_boundary_texels": False, "construction_joint": True,
            })
    return result


def _entrance_sign_assemblies() -> list[dict[str, Any]]:
    centre = [-16.12, -15.12, 5.63]
    return [
        {
            "id": "v95_entrance_sign_panel", "kind": "registered_sign_panel",
            "centre": centre, "size": [6.90, 0.16, 0.72],
            "rotation_z_deg": -45.0, "material": "signature_bronze",
            "semantic_role": "principal_entrance_identity_sign_carrier",
        },
        {
            "id": "v95_entrance_sign_sticker", "kind": "carrier_skin",
            "surface_id": "principal_entrance_identity_sign",
            "target_ids": ["v95_entrance_sign_panel"],
            "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v95/entrance_sign_intrinsic.png",
            "source_id": "v95_intrinsic_entrance_sign",
            "axis": "angle", "rotation_z_deg": -45.0, "centre": centre,
            "span_m": 6.90, "height_m": 0.72,
            "material_role": "elevation", "floor_role": "ground",
            "finish_class": "geometry_conditioned_identity_sign",
            "sticker_layer": "entrance_sign", "final_surface_coverage": True,
        },
    ]


def build_profile() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = deepcopy(build_v94_profile())
    geometry = build_v95_geometry()
    profile["identity"] = "Belle Epoque Grand Magasin V95, geometry-conditioned Sticker Method"
    # The registered stickers remain the visible colour authority. Bind the
    # locked carrier cores to construction-role-correct library PBR sets so a
    # fresh checkout can reproduce the pilot without V91's ignored bake cache.
    profile["material_overrides"]["primary"].update({
        "texture_key": "limestone", "baked_pbr": True, "texture_tile_metres": 3.2,
    })
    profile["material_overrides"]["secondary"].update({
        "texture_key": "black_metal", "baked_pbr": True, "texture_tile_metres": 3.0,
    })
    profile["material_overrides"]["roof"].update({
        "texture_key": "zinc", "baked_pbr": True, "texture_tile_metres": 3.8,
    })
    profile["signature_material_overrides"]["dome_glow"] = {
        "base_color": "#8b5a2c", "roughness": 0.72, "metallic": 0.0,
        "emission_color": "#ffc77a", "emission_strength": 0.48,
    }
    graph = profile["massing_graph"]
    graph["profile"] = "belle-epoque-geometry-conditioned-sticker-v95-5"
    # The locked corner pavilion and its moulded returns project 1.59 m past
    # each nominal streetwall edge.  Declare only the extra allowance beyond
    # the validator's standard landmark/eave envelope; this keeps the approved
    # silhouette intact while making the runtime footprint contract explicit.
    graph["recipe_contract"] = {
        **(graph.get("recipe_contract") or {}),
        "kind": "belle_epoque_geometry_conditioned_landmark",
        "footprint_projection_allowance_m": 1.25,
        "projection_source": "locked_corner_pavilion_and_moulded_returns",
    }
    graph["nodes"][0]["geometry_sha256"] = geometry["geometry_sha256"]
    graph["nodes"][0]["meshes"] = [
        {
            "name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
            "material": "roof" if mesh.get("material_domain") == "roof_only" else "primary",
            "material_domain": mesh.get("material_domain"),
        }
        for mesh in geometry["meshes"]
    ]
    roof_target_names = {
        str(mesh["name"]) for mesh in geometry["meshes"]
        if mesh.get("material_domain") == "roof_only"
    }
    dome_glass_targets = {"central_glass_dome", "corner_glass_cupola"}
    retained = [
        item for item in graph["assemblies"]
        if "dormer" not in str(item.get("id", "")).lower()
        and item.get("id") != "v94_principal_corner_front_return"
        and not (
            any(str(target) in dome_glass_targets for target in item.get("target_ids") or [])
            and item.get("id") not in {"v92_skin_central_dome", "v92_skin_corner_dome"}
        )
        and not any("dormer" in str(target).lower() for target in item.get("target_ids") or [])
    ]
    for item in retained:
        carrier_targets = [str(value) for value in item.get("target_ids") or []]
        resolved_targets = {
            mesh_name for target in carrier_targets for mesh_name in roof_target_names
            if mesh_name == target or mesh_name.startswith(f"{target}_")
        }
        if item.get("kind") == "carrier_skin" and carrier_targets and resolved_targets:
            if all(
                any(mesh_name == target or mesh_name.startswith(f"{target}_") for mesh_name in roof_target_names)
                for target in carrier_targets
            ):
                # Floor ownership follows the carrier geometry domain, not the
                # shader class. Glass and elevation-style cupola stickers are
                # still roof-owned and may not bypass the floor/roof gate.
                item["floor_role"] = "roof"
        if item.get("kind") == "carrier_skin" and item.get("material_role") == "roof":
            item["floor_role"] = "roof"
        if item.get("id") == "v92_skin_coverage_068_corner_upper_tower":
            item["floor_role"] = "top_crown"
            item["z_min_m"], item["z_max_m"] = 18.4, 20.5
        if item.get("id") == "v92_skin_corner_tower":
            item.update({
                "centre": [-12.925, -13.5, 19.45], "height_m": 2.1,
                "dome_base_z": 18.4, "dome_height_m": 2.1,
                "z_min_m": 18.4, "z_max_m": 20.5,
                "uv_v_min": 0.72, "uv_v_max": 0.842,
                "floor_role": "top_crown",
            })
        if item.get("id") == "v94_curved_iron_glass_canopy":
            item.update({
                "inner_radius_m": 6.45, "outer_radius_m": 10.15,
                "angle_start_deg": 180.0, "angle_end_deg": 270.0,
                "segments": 28, "rib_radius_m": 0.030,
            })
        if item.get("id") == "v92_skin_central_dome":
            item["glass_profile"] = "heritage_stained_glass_luminous"
            item["finish_class"] = "geometry_conditioned_luminous_stained_glass"
            item["source_image_path"] = "tools/archetype_compiler/sticker_assets/belle_epoque_v95/central_dome_intrinsic.png"
            item["source_id"] = "v95_delit_central_stained_glass"
            item["normal_z_min"] = -1.01
        elif item.get("id") == "v92_skin_corner_dome":
            item["glass_profile"] = "heritage_stained_glass_luminous"
            item["finish_class"] = "geometry_conditioned_luminous_stained_glass"
            item["source_image_path"] = "tools/archetype_compiler/sticker_assets/belle_epoque_v95/corner_dome_intrinsic.png"
            item["source_id"] = "v95_delit_corner_stained_glass"
            item["normal_z_min"] = -1.01
    graph["assemblies"] = (
        retained + _dormer_carriers() + _dormer_trim_assemblies()
        + _outer_corner_return_carriers(geometry) + _entrance_sign_assemblies() + [
        {
            "id": "v95_corner_upper_tower_roof_transition_sticker", "kind": "carrier_skin",
            "surface_id": "corner_upper_tower_roof_transition",
            "target_ids": ["cupola_roof_transition"],
            "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v95/dormer_zinc_intrinsic.png",
            "source_id": "v95_delit_zinc_tower_roof_transition",
            "axis": "box_projected", "centre": [-14.5, -13.5, 21.774],
            "span_m": 6.3, "height_m": 2.548,
            "box_bounds": [-17.65, -11.35, -16.65, -10.35, 20.5, 23.048],
            "normal_z_min": -1.01, "normal_z_max": 1.01,
            "face_indices": list(range(48)), "material_role": "roof", "floor_role": "roof",
            "finish_class": "geometry_conditioned_zinc_cupola_transition",
            "sticker_layer": "roof_landmark_transition", "final_surface_coverage": True,
        },
        {
            "id": "v95_corner_tower_glazed_roof_transition", "kind": "carrier_skin",
            "surface_id": "corner_tower_glazed_roof_transition",
            "target_ids": ["cupola_roof_transition"],
            "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v92/corner_seam_matched.jpg",
            "source_id": "corner_seam_matched_upper_roof_transition_crop",
            "axis": "cylindrical_segment", "centre": [-12.925, -13.5, 21.774],
            "span_m": 3.15, "height_m": 2.548,
            "z_min_m": 20.5, "z_max_m": 23.048,
            "origin_x": -14.5, "origin_y": -13.5,
            "angle_start_deg": 0.0, "angle_end_deg": 360.0,
            "dome_base_z": 20.5, "dome_height_m": 2.548, "dome_radius_m": 1.575,
            "uv_u_min": 0.02, "uv_u_max": 0.98,
            "uv_v_min": 0.842, "uv_v_max": 0.99,
            "normal_z_min": -0.25, "normal_z_max": 0.25,
            "material_role": "elevation", "floor_role": "roof",
            "finish_class": "geometry_conditioned_glazed_cupola_transition",
            "sticker_layer": "roof_landmark_glazing", "final_surface_coverage": True,
        },
        {
            "id": "v95_central_dome_light_well", "kind": "dome_light_well",
            "centre_xy": [0.0, 0.0], "radius_m": 5.12, "z_m": 25.56,
            "thickness_m": 0.12, "material": "dome_glow",
            "semantic_role": "warm_occupied_backing_below_stained_glass_dome",
        },
        {
            "id": "v95_corner_cupola_light_well", "kind": "dome_light_well",
            "centre_xy": [-14.5, -13.5], "radius_m": 2.62, "z_m": 23.76,
            "thickness_m": 0.10, "material": "dome_glow",
            "semantic_role": "warm_occupied_backing_below_stained_glass_cupola",
        },
        ]
    )
    graph["continuous_floor_sticker_contract"]["architect_score_target"] = 95
    production = profile["production_contract"]
    production["representation"] = "locked_geometry_plus_geometry_conditioned_surface_stickers"
    production["clay_lock"]["status"] = "approved_v94_carrier_locked_for_v95_conditioning"
    production["floor_sticker_method"].update({
        "schema": "geometry-conditioned-continuous-sticker-contract@1",
        "architect_score_target": 95,
        "approval_space": "rendered_on_locked_carrier",
        "post_generation_crop_allowed": False,
        "post_generation_nonuniform_scale_allowed": False,
    })
    production["image_lock"]["required_assembly_ids"] = [
        item["id"] for item in graph["assemblies"]
    ]
    production["image_lock"]["required_assembly_kinds"] = {
        "carrier_skin": sum(item.get("kind") == "carrier_skin" for item in graph["assemblies"]),
    }
    return condition_profile(profile, geometry, score_target=95)


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    profile, package = build_profile()
    payload = {
        "schema": "architectural-signatures@1",
        "override_profiles": ["grand-magasin-belle-epoque"],
        "profiles": {
            VARIANT_ID: profile,
            "grand-magasin-belle-epoque": deepcopy(profile),
        },
    }
    registry = {
        "schema": "catalogue-rollout-batch@1", "pipeline_version": "v95",
        "batch_id": "BELLE-EPOQUE-GEOMETRY-CONDITIONED-STICKER-V95", "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": "grand_magasin", "variant_id": VARIANT_ID,
            "family_id": FAMILY_ID, "width_m": 36.0, "depth_m": 34.0, "floors": 5,
        }],
    }
    contract = {
        "schema": "geometry-conditioned-continuous-sticker-contract@1",
        "building_id": "grand-magasin-belle-epoque", "score_target": 95,
        "locked_geometry_sha256": package["locked_geometry_sha256"],
        "carrier_package_sha256": package["package_sha256"],
        "carrier_count": package["carrier_count"], "status": package["status"],
        "hard_stops": package["hard_stops"],
        "focused_repairs": [
            "broadened_curved_entrance_canopy", "luminous_physical_dome_section",
            "face-specific_dormer_front_cheek_cap_return_ownership",
            "geometry-conditioned_curved_pavilion_registration",
        ],
    }
    return payload, registry, package, contract


def main() -> None:
    payload, registry, package, contract = build_outputs()
    for path, value in ((OUTPUT, payload), (REGISTRY, registry), (PACKAGE, package), (CONTRACT, contract)):
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "profile": str(OUTPUT), "registry": str(REGISTRY), "package": str(PACKAGE),
        "contract": str(CONTRACT), "carrier_count": package["carrier_count"],
        "status": package["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
