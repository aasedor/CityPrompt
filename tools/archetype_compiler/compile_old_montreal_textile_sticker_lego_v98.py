"""Compile the V98 Old Montreal textile-mill Sticker LEGO pilot."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_old_montreal_textile_sticker_lego_v98 import (
    ARCHETYPE_ID, BAY_M, FLOOR_BANDS, SIZE_MATRIX, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzz_old_montreal_textile_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "old_montreal_textile_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "old_montreal_textile_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "old_montreal_textile_sticker_lego_v98_contract.json"
PROFILE_PREFIX = "old-montreal-textile-sticker-lego"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/old_montreal_textile_v98"
MASTER = f"{ASSET_ROOT}/five_bay_three_floor_intrinsic_v2.png"
BRICK = f"{ASSET_ROOT}/brick_return_intrinsic_v2.png"
STONE_VERTICAL = f"{ASSET_ROOT}/pale_stone_construction_intrinsic_v2.png"
STONE_HORIZONTAL = STONE_VERTICAL
IRON = f"{ASSET_ROOT}/black_iron_metal_intrinsic.png"
INTERIOR = f"{ASSET_ROOT}/warm_interior_card_intrinsic.png"
GROUND_INTERIOR = f"{ASSET_ROOT}/ground_interior_card_intrinsic.png"
MIDDLE_INTERIOR = f"{ASSET_ROOT}/middle_interior_card_intrinsic.png"
TOP_INTERIOR = f"{ASSET_ROOT}/top_interior_card_intrinsic.png"
WINDOW_GLASS = f"{ASSET_ROOT}/neutral_window_glass_intrinsic.png"
INTERIOR_ATLAS = f"{ASSET_ROOT}/five_bay_three_floor_interior_only_v3.png"
ROOF = f"{ASSET_ROOT}/dark_gravel_roof_intrinsic_v2.png"
COPING = f"{ASSET_ROOT}/dark_coping_intrinsic.png"
SKYLIGHT_GLASS = f"{ASSET_ROOT}/skylight_glass_intrinsic.png"
SKYLIGHT_METAL = f"{ASSET_ROOT}/black_iron_metal_intrinsic.png"
HVAC = f"{ASSET_ROOT}/hvac_service_casing_intrinsic.png"

ROLE_V = {"ground": (0.0, 1 / 3), "middle": (1 / 3, 2 / 3), "top": (2 / 3, 1.0)}
INTERIOR_U = tuple((index / 5, (index + 1) / 5) for index in range(5))


def profile_id(size_id: str) -> str:
    return f"{PROFILE_PREFIX}-{size_id}"


def family_id(size_id: str) -> str:
    return f"old-montreal-textile-mill-v98-{size_id}"


def _base_profile() -> dict[str, Any]:
    payload = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(payload["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return (
        [float(vertex[0]) for vertex in mesh["vertices"]],
        [float(vertex[1]) for vertex in mesh["vertices"]],
        [float(vertex[2]) for vertex in mesh["vertices"]],
    )


def _axis(mesh: dict[str, Any]) -> str:
    return str(mesh.get("side") or (
        "plan" if mesh["material_domain"] in {"main_roof"} else "box_projected"
    ))


def _source(mesh: dict[str, Any], face_role: str | None = None) -> tuple[str, str, str, str]:
    domain = str(mesh["material_domain"])
    name = str(mesh["name"])
    if domain == "occupied_wall":
        return BRICK, "elevation", f"{mesh['band_role']}_brick_masonry", str(mesh["band_role"])
    if domain == "opening_return":
        return STONE_VERTICAL if mesh.get("band_role") == "middle" else BRICK, "elevation", "opening_return", str(mesh["band_role"])
    if domain == "recessed_glazing":
        return WINDOW_GLASS, "glass", "physical_window_glass", str(mesh["band_role"])
    if domain == "recessed_door":
        return INTERIOR, "elevation", "recessed_entrance_back", "ground"
    if domain in {"stone_belt", "stone_spandrel", "terrace_stone", "service_volume_cornice"}:
        return STONE_HORIZONTAL, "elevation", "horizontal_cut_stone", str(mesh.get("band_role", "fixed"))
    if domain in {"stone_surround", "principal_corner_stone"}:
        return STONE_VERTICAL, "elevation", "vertical_weathered_limestone", str(mesh.get("band_role", "fixed"))
    if domain == "masonry_pier":
        return BRICK, "elevation", "brick_masonry_pier", str(mesh.get("band_role", "fixed"))
    if domain == "entrance_support":
        return BRICK, "elevation", "entrance_support", "ground"
    if domain in {"terrace_guardrail", "entrance_canopy"}:
        return IRON, "elevation", "black_iron_construction", str(mesh.get("band_role", "fixed"))
    if domain == "main_roof":
        return ROOF, "elevation", "flat_gravel_roof", "roof"
    if domain == "roof_parapet":
        return COPING, "elevation", "parapet_coping", "roof"
    if domain == "roof_monitor_glass":
        return SKYLIGHT_GLASS, "glass", "skylight_glass", "roof"
    if domain == "roof_monitor_metal":
        return SKYLIGHT_METAL, "elevation", "skylight_metal", "roof"
    if domain == "roof_service":
        return HVAC, "elevation", "bounded_roof_service", "roof"
    if domain == "service_volume_wall":
        return BRICK, "elevation", "rear_service_volume", "fixed"
    if domain == "service_panel_recess":
        return INTERIOR, "elevation", "rear_service_panel_recess", "fixed"
    if domain == "interior_card":
        band = str(mesh.get("band_role", "middle"))
        return INTERIOR_ATLAS, "elevation", f"recessed_{band}_interior_only_card", band
    if domain == "window_mullion":
        return IRON, "elevation", "steel_window_mullion", str(mesh.get("band_role", "fixed"))
    if domain == "subordinate_roof":
        # This roof belongs to the deliberately lower rear service step.  Its
        # floor role is fixed so the main-roof datum audit does not mistake it
        # for leakage from the building crown onto an occupied floor.
        return ROOF, "elevation", "subordinate_service_roof", "fixed"
    if domain == "roof_access":
        return COPING, "elevation", "roof_access_hatch", "roof"
    raise KeyError(f"unmapped V98 material domain {domain!r} on {name!r}")


def _carrier(mesh: dict[str, Any], face_indices: list[int], face_role: str | None = None) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh)
    axis = _axis(mesh)
    source, material_role, layer, floor_role = _source(mesh, face_role)
    span = max(xs) - min(xs) if axis in {"front", "rear", "plan"} else max(ys) - min(ys)
    height = max(zs) - min(zs)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{face_role or 'sticker'}",
        "kind": "carrier_skin", "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, 0.01), "height_m": max(height, 0.01), "face_indices": face_indices,
        "material_role": material_role, "floor_role": floor_role,
        "finish_class": f"geometry_conditioned_{layer}", "sticker_layer": layer,
        "final_surface_coverage": True,
    }
    if material_role == "glass":
        item["glass_profile"] = "industrial_sash"
        if mesh["material_domain"] == "recessed_glazing":
            item["surface_alpha_override"] = 0.30
            item["transparency_mode"] = "BLENDED"
            item["roughness_override"] = 0.055
            item["transmission_override"] = 0.92
            item["specular_ior_level_override"] = 0.34
            item["coat_weight_override"] = 0.10
            item["emission_strength_override"] = 0.0
        elif mesh["material_domain"] == "roof_monitor_glass":
            item["surface_alpha_override"] = 0.98
            item["roughness_override"] = 0.28
            item["transmission_override"] = 0.08
            item["specular_ior_level_override"] = 0.04
            item["coat_weight_override"] = 0.0
            item["emission_strength_override"] = 0.0
    if axis in {"front", "rear"}:
        item.update({"u_min_m": min(xs), "u_max_m": max(xs), "z_min_m": min(zs), "z_max_m": max(zs)})
    elif axis in {"left", "right"}:
        item.update({"u_min_m": min(ys), "u_max_m": max(ys), "z_min_m": min(zs), "z_max_m": max(zs)})
    elif axis == "plan":
        item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    else:
        item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if mesh["material_domain"] == "interior_card" and mesh.get("band_role") in ROLE_V:
        side_offset = {"front": 0, "right": 2, "rear": 3, "left": 1}.get(str(mesh.get("side", "front")), 0)
        bay = (int(mesh.get("bay", 0)) + side_offset) % len(INTERIOR_U)
        item.update({"uv_u_min": INTERIOR_U[bay][0], "uv_u_max": INTERIOR_U[bay][1],
                     "uv_v_min": ROLE_V[str(mesh["band_role"])][0],
                     "uv_v_max": ROLE_V[str(mesh["band_role"])][1]})
        item["emission_strength_override"] = {"ground": 0.20, "middle": 0.13, "top": 0.08}[str(mesh["band_role"])]
    elif mesh["material_domain"] in {"occupied_wall", "masonry_pier", "entrance_support", "service_volume_wall", "opening_return"}:
        item.update({"uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0,
                     "world_metric_uv_tile_m": 1.65})
    elif mesh["material_domain"] in {"stone_belt", "stone_spandrel", "stone_surround",
                                      "principal_corner_stone", "terrace_stone", "service_volume_cornice"}:
        item.update({"uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0,
                     "world_metric_uv_tile_m": 3.4})
    elif mesh["material_domain"] in {"main_roof", "subordinate_roof"}:
        item.update({"uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0,
                     "world_metric_uv_tile_m": 4.0})
    else:
        item.update({"uv_u_min": 0.0, "uv_u_max": 1.0, "uv_v_min": 0.0, "uv_v_max": 1.0})
    item["flip_u"] = axis in {"rear", "left"}
    return item


def _carriers(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for mesh in geometry["meshes"]:
        roles = list(mesh["face_roles"])
        for role in dict.fromkeys(roles):
            indices = [index for index, value in enumerate(roles) if value == role]
            result.append(_carrier(mesh, indices, role if mesh["material_domain"] in {"roof_monitor_glass", "roof_monitor_metal"} else None))
    return result


def build_profile(size_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    geometry = build_geometry(size_id)
    profile = _base_profile()
    width = float(geometry["dimensions"]["width_m"])
    depth = float(geometry["dimensions"]["depth_m"])
    profile["identity"] = f"Old Montreal Textile Mill V98 Sticker LEGO — {size_id}"
    profile["dimension_overrides"] = {"width_m": width, "depth_m": depth, "default_floors": 3, "min_floors": 3, "max_floors": 3}
    profile["glass_profile"] = "industrial_sash"
    graph = profile.setdefault("massing_graph", {"schema": "massing-graph@1"})
    graph.update({
        "profile": profile_id(size_id),
        "description": "Exact-image three-storey brick, stone and industrial-glass corner mill with whole-bay horizontal growth only.",
        "height_m": 14.8,
        "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": 3, "bay_module_m": BAY_M},
        "nodes": [{"id": f"v98_locked_carrier_{size_id}", "kind": "locked_mesh_bundle", "location": [0, 0, 0],
                   "geometry_sha256": geometry["geometry_sha256"],
                   "meshes": [{"name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
                               "material": "roof" if mesh["material_domain"].startswith("roof") or mesh["material_domain"] == "main_roof" else "primary",
                               "material_domain": mesh["material_domain"]} for mesh in geometry["meshes"]]}],
        "voids": [{"id": aperture["aperture_id"], "purpose": "true recessed aperture", "recess_depth_m": aperture["recess_depth_m"]}
                  for aperture in geometry["apertures"]],
        "assemblies": _carriers(geometry),
        "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial", "context"],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.92, "street_x_scale": 0.76},
        "floor_sticker_contract": {"required": True, "floor_count": 3,
            "floor_datums_m": [band["z_min_m"] for band in FLOOR_BANDS] + [FLOOR_BANDS[-1]["z_max_m"]],
            "roof_starts_at_z_m": 13.12, "roles": ["ground", "middle", "top"], "bay_module_m": BAY_M,
            "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
            "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
        "final_surface_audit": {"required": True, "forbid_generic_materials": True,
                                 "required_finish_property": "final_surface_coverage"},
    })
    profile["production_contract"] = {
        "identity_mode": "massing_graph",
        "fixed_identity": ["three occupied storeys", "brick/stone/brick vertical sequence", "corner and end piers",
                           "two long roof skylights", "bounded roof equipment", "true recessed apertures"],
        "repeatable_capacity": ["complete 5 m structural bays horizontally"],
        "required_reference_roles": ["street_identity", "oblique_massing", "roof_or_aerial"],
        "representation": "locked_geometry_plus_carrier_space_stickers",
        "placement_model": "lego_polygon_fit_with_two_discrete_width_tiers",
        "architect_score_target": 95,
        "clay_lock": {"required": True, "status": f"v98_{size_id}_locked", "geometry_sha256": geometry["geometry_sha256"]},
        "reference_authority": "exact_images_override_conflicting_4_to_6_floor_metadata",
        "rear_reference_class": "constrained_completion_not_exact_rear",
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size_id, "whole_modules_only": True,
                             "vertical_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
    }
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
        entries.append({"archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
                        "signature_profile_id": profile_id(size_id), "family_id": family_id(size_id),
                        "width_m": spec["width_m"], "depth_m": spec["depth_m"], "floors": 3})
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    payload = {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles}
    registry = {"schema": "catalogue-rollout-batch@1", "pipeline_version": "v98", "batch_id": "OLD-MONTREAL-TEXTILE-V98",
                "paid_facade_calls": 1, "entries": entries}
    package_payload = {"schema": "siteforge.sticker-lego-size-matrix@1", "packages": packages}
    contract = {"schema": "geometry-conditioned-sticker-lego-contract@1",
                "building_id": f"{ARCHETYPE_ID}--{VARIANT_ID}", "score_target": 95,
                "size_matrix": SIZE_MATRIX, "bay_module_m": BAY_M, "vertical_scaling": "forbidden",
                "whole_modules_only": True, "statuses": {key: value["status"] for key, value in packages.items()},
                "geometry_sha256": {key: value["geometry_sha256"] for key, value in geometries.items()},
                "carrier_counts": {key: value["carrier_count"] for key, value in packages.items()},
                "hard_stops": ["partial_bay", "nonuniform_sticker_scale", "floor_roof_overlap", "exposed_carrier",
                               "flat_printed_opening", "generic_material", "architect_mean_not_above_95"]}
    return payload, registry, package_payload, contract


def main() -> None:
    outputs = build_outputs()
    for path, payload in zip((OUTPUT, REGISTRY, PACKAGE, CONTRACT), outputs):
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "statuses": outputs[3]["statuses"],
                      "carrier_counts": outputs[3]["carrier_counts"]}, indent=2))


if __name__ == "__main__":
    main()
