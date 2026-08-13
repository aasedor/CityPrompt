"""Compile the exact-image-locked Halifax Waterfront Warehouse V98 family."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_halifax_waterfront_warehouse_sticker_lego_v98 import (
    ARCHETYPE_ID, SIZE_MATRIX, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzz_halifax_waterfront_warehouse_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "halifax_waterfront_warehouse_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "halifax_waterfront_warehouse_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "halifax_waterfront_warehouse_sticker_lego_v98_contract.json"
PROFILE_PREFIX = "halifax-waterfront-warehouse-sticker-lego"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/halifax_waterfront_warehouse_v98"
ASSETS = {
    "brick_front": f"{ASSET_ROOT}/warm_brick_front_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/warm_brick_return_intrinsic.png",
    "stone": f"{ASSET_ROOT}/pale_warm_stone_intrinsic.png",
    "plinth": f"{ASSET_ROOT}/weathered_stone_plinth_intrinsic.png",
    "joinery": f"{ASSET_ROOT}/dark_green_joinery_intrinsic.png",
    "cornice": f"{ASSET_ROOT}/patinated_green_grey_cornice_intrinsic.png",
    "upper_glass": f"{ASSET_ROOT}/clear_upper_glass_intrinsic.png",
    "storefront_glass": f"{ASSET_ROOT}/clear_storefront_glass_intrinsic.png",
    "ground_interior": f"{ASSET_ROOT}/ground_retail_interior_atlas.png",
    "upper_interior": f"{ASSET_ROOT}/upper_commercial_interior_atlas.png",
    "roof": f"{ASSET_ROOT}/weathered_flat_membrane_intrinsic.png",
    "roof_perimeter": f"{ASSET_ROOT}/dark_perimeter_membrane_intrinsic.png",
    "chimney_brick": f"{ASSET_ROOT}/chimney_brick_intrinsic.png",
    "chimney_coping": f"{ASSET_ROOT}/chimney_coping_intrinsic.png",
    "service_metal": f"{ASSET_ROOT}/aged_galvanized_service_metal_intrinsic.png",
    "hardware": f"{ASSET_ROOT}/threshold_hardware_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0.png": "ad42ba20d97281337b2a501af57cee64418b3df0486b3fa6c881cd317ef4784c",
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0_angle_60.jpg": "9b2a732476ea85a955d4047463bf7ea34dfed211e8e0f69fdd5b6b9c1ee49efb",
    "frontend/public/archetypes/buildings/halifax-waterfront-warehouse/variant_0_angle_90.jpg": "721b8ef5aff6c9e45b9f1bd0beb6df81219675471aece32fc4826f219a1bcdf3",
}


def profile_id(size_id: str) -> str:
    return f"{PROFILE_PREFIX}-{size_id}"


def family_id(size_id: str) -> str:
    return f"halifax-waterfront-warehouse-v98-{size_id}"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(vertex[index]) for vertex in mesh["vertices"]] for index in range(3))  # type: ignore[return-value]


def _axis(mesh: dict[str, Any]) -> str:
    side = str(mesh.get("side", ""))
    return side if side in {"front", "rear", "left", "right"} else "box_projected"


def _floor_role(mesh: dict[str, Any]) -> str:
    name = str(mesh["name"])
    domain = str(mesh["material_domain"])
    if name.startswith("front_stepped_parapet_") or name.startswith("cornice_layer_") or "modillion" in name:
        return "fixed_crown"
    if domain in {"weathered_membrane_roof", "oxidized_metal_coping", "patinated_coping",
                  "patinated_coping_corner", "oxidized_metal_coping_corner", "dark_metal"} or name in {
        "front_roof_parapet", "rear_roof_parapet", "left_roof_parapet", "right_roof_parapet",
    } or name.startswith("rear_brick_chimney_"):
        return "roof"
    if "level" in mesh:
        return "ground" if int(mesh["level"]) == 0 else "top"
    # Physical quoins span the two occupied bands in separate blocks.
    _xs, _ys, zs = _bounds(mesh)
    return "ground" if (min(zs) + max(zs)) / 2 < 4.7 else "top"


def _source(mesh: dict[str, Any]) -> tuple[str, str, str]:
    name, domain = str(mesh["name"]), str(mesh["material_domain"])
    side = str(mesh.get("side", ""))
    front_asset = ASSETS["brick_front"] if side == "front" or name.startswith("front_") else ASSETS["brick_return"]
    if domain == "red_brick":
        if name.startswith("rear_brick_chimney_") and name.endswith("_shaft"):
            return ASSETS["chimney_brick"], "elevation", "chimney_brick"
        if "roof_parapet" in name:
            return front_asset, "elevation", "warm_brick_roof_parapet"
        return front_asset, "elevation", "warm_brick_masonry"
    if domain == "pale_stone_rustication":
        if "_apron" in name:
            return ASSETS["plinth"], "elevation", "weathered_stone_plinth"
        return ASSETS["stone"], "elevation", "pale_stone_rustication"
    if domain == "pale_stone_return":
        return ASSETS["stone"], "elevation", "deep_pale_stone_reveal"
    if domain == "pale_stone_trim":
        if name.startswith("rear_brick_chimney_") and name.endswith("_independent_cap"):
            return ASSETS["chimney_coping"], "elevation", "chimney_coping"
        if (name.startswith("cornice_layer_") or "modillion" in name or
                "stepped_parapet_layered_coping" in name or name.endswith("_continued_cornice")):
            return ASSETS["cornice"], "elevation", "patinated_cornice"
        return ASSETS["stone"], "elevation", "pale_stone_trim"
    if domain == "dark_metal_frame":
        return ASSETS["joinery"], "elevation", "physical_dark_green_upper_joinery"
    if domain == "dark_green_painted_metal":
        return ASSETS["joinery"], "elevation", "physical_dark_green_ground_joinery"
    if domain == "recessed_glazing":
        if int(mesh.get("level", 0)) == 0:
            return ASSETS["storefront_glass"], "glass", "physical_clear_storefront_glass"
        return ASSETS["upper_glass"], "glass", "physical_clear_upper_glass"
    if domain == "interior_card":
        if int(mesh.get("level", 0)) == 0:
            return ASSETS["ground_interior"], "elevation", "ground_retail_interior_card"
        return ASSETS["upper_interior"], "elevation", "upper_commercial_interior_card"
    if domain == "weathered_membrane_roof":
        return ASSETS["roof"], "elevation", "weathered_flat_membrane_roof"
    if domain == "oxidized_metal_coping":
        if name.startswith("front_stepped_parapet_"):
            return ASSETS["cornice"], "elevation", "patinated_stepped_coping"
        return ASSETS["cornice"], "elevation", "patinated_roof_coping"
    if domain == "patinated_coping":
        layer = "patinated_roof_coping_corner" if "corner_cap" in name else "patinated_roof_coping"
        return ASSETS["cornice"], "elevation", layer
    if domain in {"patinated_coping_corner", "oxidized_metal_coping_corner"}:
        return ASSETS["cornice"], "elevation", "patinated_roof_coping_corner"
    if domain == "dark_metal":
        return ASSETS["service_metal"], "elevation", "aged_galvanized_roof_service"
    raise KeyError(f"unmapped Halifax domain {domain!r} on {name!r}")


def _carrier(mesh: dict[str, Any], face_indices: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh)
    axis = _axis(mesh)
    source, material_role, layer = _source(mesh)
    span = max(xs) - min(xs) if axis in {"front", "rear"} else max(ys) - min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_sticker", "kind": "carrier_skin",
        "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs) - min(zs), .01),
        "face_indices": face_indices, "material_role": material_role,
        "floor_role": _floor_role(mesh), "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer, "final_surface_coverage": True,
    }
    if axis == "box_projected":
        item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if layer in {"warm_brick_masonry", "warm_brick_roof_parapet"}:
        # Both registered brick masters use the same real-world module and
        # phase, so front-to-return courses meet without a scale jump.
        item.update(world_metric_uv_tile_m=1.20, world_metric_uv_u_offset=0.0, world_metric_uv_v_offset=0.0)
        item["roughness_override"] = .68
    elif layer in {"pale_stone_rustication", "deep_pale_stone_reveal", "pale_stone_trim", "weathered_stone_plinth", "chimney_coping"}:
        # Stone must keep one real-world scale across tall piers, horizontal
        # belts, arch mouldings and returns.  Per-carrier fitting stretches the
        # quiet mineral field into vertical wood-like grain on narrow piers.
        item.update(world_metric_uv_tile_m=1.65, world_metric_uv_u_offset=0.0,
                    world_metric_uv_v_offset=0.0, roughness_override=.74)
    elif layer == "weathered_flat_membrane_roof":
        item.update(world_metric_uv_tile_m=3.8, world_metric_uv_u_offset=.17, world_metric_uv_v_offset=.31)
    elif layer in {"patinated_cornice", "patinated_stepped_coping", "patinated_roof_coping", "patinated_roof_coping_corner"}:
        item.update(world_metric_uv_tile_m=2.4, metallic_override=.42, roughness_override=.50)
    elif layer == "aged_galvanized_roof_service":
        item.update(world_metric_uv_tile_m=1.7, metallic_override=.62, roughness_override=.44)
    if material_role == "glass":
        if int(mesh.get("level", 0)) == 0:
            item.update(glass_profile="reflective_curtain_wall", transparency_mode="BLENDED",
                        surface_alpha_override=.72, transmission_override=.78, roughness_override=.075,
                        specular_ior_level_override=.68, coat_weight_override=.52, emission_strength_override=.002)
        else:
            item.update(glass_profile="reflective_curtain_wall", transparency_mode="BLENDED",
                        surface_alpha_override=.68, transmission_override=.80, roughness_override=.07,
                        specular_ior_level_override=.70, coat_weight_override=.54, emission_strength_override=.002)
    if str(mesh["material_domain"]) == "interior_card":
        side_number = {"front": 0, "right": 1, "rear": 2, "left": 3}.get(str(mesh.get("side")), 0)
        level = int(mesh.get("level", 0))
        cell = (side_number * 5 + int(mesh.get("bay", 0)) * 3 + level * 5) % 8
        col, row = cell % 4, cell // 4
        item.update(uv_u_min=col / 4, uv_u_max=(col + 1) / 4,
                    uv_v_min=row / 2, uv_v_max=(row + 1) / 2,
                    atlas_cell_index=cell,
                    emission_strength_override=.008 if level == 0 else .006)
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    mesh_faces = {str(mesh["name"]): len(mesh["faces"]) for mesh in geometry["meshes"]}
    coverage: dict[tuple[str, int], int] = {(name, index): 0 for name, count in mesh_faces.items() for index in range(count)}
    for carrier in carriers:
        surface = str(carrier["surface_id"])
        for index in carrier["face_indices"]:
            coverage[(surface, int(index))] += 1
    missing = [f"{name}:{index}" for (name, index), count in coverage.items() if count == 0]
    duplicate = [f"{name}:{index}" for (name, index), count in coverage.items() if count > 1]
    audit = {"visible_face_count": len(coverage), "owned_once_count": sum(count == 1 for count in coverage.values()),
             "missing_faces": missing, "multiply_owned_faces": duplicate, "status": "pass" if not missing and not duplicate else "fail"}
    if audit["status"] != "pass":
        raise ValueError(f"final surface ownership failed: {audit}")
    return audit


def _build_profile(size_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = build_geometry(size_id)
    width, depth = (float(geometry["dimensions"][key]) for key in ("width_m", "depth_m"))
    carriers = [_carrier(mesh, list(range(len(mesh["faces"])))) for mesh in geometry["meshes"]]
    audit = _surface_audit(geometry, carriers)
    profile = _base_profile()
    profile.update({
        "identity": f"Halifax Waterfront Warehouse V98 Sticker LEGO — {size_id}",
        "kits": [],
        "massing_graph": {
            "schema": "massing-graph@1", "profile": profile_id(size_id),
            "description": "Exact-image-locked two-storey Italianate warm-brick commercial block with tall storefronts, round-arched upper windows, rusticated stone, patinated crown and a concealed flat roof.",
            # Full reviewed silhouette includes the two independently capped
            # rear chimney stacks above the 11.82 m parapet datum.
            "height_m": 13.19,
            "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": 2, "ordinary_bay_m": 2.5},
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial"],
            "nodes": [{"id": f"v98_halifax_locked_{size_id}", "kind": "locked_mesh_bundle", "location": [0, 0, 0],
                       "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
            "assemblies": carriers, "surface_audit": audit,
            "floor_sticker_contract": {"required": True, "floor_count": 2,
                "floor_datums_m": [0.0, 4.4, 5.0, 9.7], "roof_starts_at_z_m": 9.7,
                "roles": ["ground", "top", "fixed_crown", "roof"],
                "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
                "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
            "final_surface_audit": {"required": True, "status": audit["status"], "visible_face_count": audit["visible_face_count"],
                                    "owned_once_count": audit["owned_once_count"], "forbid_generic_materials": True,
                                    "required_finish_property": "final_surface_coverage"},
            "exact_image_override": {"required": True, "authority": "variant_0 three-image set",
                                     "reference_sha256": REFERENCE_HASHES,
                                     "rejected_catalog_identity": "three-and-one-half-storey ironstone gable warehouse"},
            "size_matrix": SIZE_MATRIX, "selected_size": size_id,
        },
        "presentation": {"identity_yaw_degrees": -28.0, "street_yaw_degrees": -15.0,
                         "street_distance_scale": 1.07, "identity_distance_scale": 1.02},
    })
    profile["dimension_overrides"] = {
        "width_m": width, "depth_m": depth,
        "default_floors": 2, "min_floors": 2, "max_floors": 2,
        # Keep the generic modular roof validator compatible with the source
        # profile while the assembled landmark remains the locked flat roof.
        "roof_height_m": 4.2,
    }
    profile["production_contract"] = {
        "identity_mode": "massing_graph",
        "identity_authority": "exact_image_locked_semantic_stack",
        "fixed_identity": ["two occupied storeys", "one fixed 5m front entrance", "round-arched upper windows",
                           "rusticated corner quoins", "patinated projecting cornice", "flat membrane roof behind parapet"],
        "repeatable_capacity": ["complete 2.5m bays only"],
        "representation": "locked_geometry_plus_carrier_space_stickers",
        "placement_model": "lego_polygon_fit_with_two_discrete_width_tiers", "architect_score_target": 95,
        "clay_lock": {"required": True, "status": f"v98_{size_id}_locked", "geometry_sha256": geometry["geometry_sha256"]},
        "reference_authority": "exact three variant_0 images override conflicting catalogue metadata",
        "rear_reference_class": "constrained_completion_not_exact_rear",
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size_id, "whole_modules_only": True,
                             "vertical_scaling": "forbidden", "depth_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
        "hard_stops": list(geometry["geometry_hard_stops"]) + [
            "missing_or_multiply_owned_visible_face", "generic_material_fallback", "printed_window_frame_or_reflection",
            "ground_and_upper_glass_or_interior_conflated", "roof_membrane_assigned_outside_roof_deck",
        ],
    }
    return condition_profile(profile, geometry, score_target=95)


def main() -> None:
    profiles: dict[str, Any] = {}
    packages: dict[str, Any] = {}
    registry = {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID,
                "variant_id": VARIANT_ID, "identity_mode": "massing_graph",
                "identity_authority": "exact_image_locked_semantic_stack", "tiers": []}
    for size_id in SIZE_MATRIX:
        profile, package = _build_profile(size_id)
        if package["status"] != "pass":
            raise RuntimeError(f"carrier conditioning failed for {size_id}: {package['failures']}")
        profiles[profile_id(size_id)], packages[size_id] = profile, package
        registry["tiers"].append({"id": size_id, "signature_profile_id": profile_id(size_id),
                                  "family_id": family_id(size_id), **SIZE_MATRIX[size_id]})
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles}, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    PACKAGE.write_text(json.dumps({"schema": "sticker-carrier-space-packages@1", "packages": packages}, indent=2) + "\n", encoding="utf-8")
    CONTRACT.write_text(json.dumps({
        "schema": "siteforge.halifax-waterfront-warehouse-sticker-lego@1", "version": "v98.1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
        "identity_mode": "massing_graph", "identity_authority": "exact_image_locked_semantic_stack",
        "reference_sha256": REFERENCE_HASHES,
        "size_matrix": SIZE_MATRIX, "continuous_resize_allowed": False, "vertical_scaling_allowed": False,
        "depth_scaling_allowed": False, "whole_bays_only": True,
        "hard_stops": ["wrong two-storey identity", "wrong footprint tier", "partial bay resize",
                       "missing fixed entrance", "generic material fallback", "unowned or multiply owned visible face",
                       "printed glass geometry or reflections", "roof material domain leakage"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
