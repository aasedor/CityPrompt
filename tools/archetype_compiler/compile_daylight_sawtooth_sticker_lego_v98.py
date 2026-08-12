"""Compile the V98 Daylight Sawtooth Factory Sticker LEGO family."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_daylight_sawtooth_sticker_lego_v98 import (
    ARCHETYPE_ID, SIZE_MATRIX, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzz_daylight_sawtooth_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "daylight_sawtooth_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "daylight_sawtooth_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "daylight_sawtooth_sticker_lego_v98_contract.json"
PROFILE_PREFIX = "daylight-sawtooth-sticker-lego"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/daylight_sawtooth_v98"

ASSETS = {
    "brick": f"{ASSET_ROOT}/red_brick_wall_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/red_brick_return_intrinsic.png",
    "stone": f"{ASSET_ROOT}/pale_stone_sill_cap_intrinsic.png",
    "concrete": f"{ASSET_ROOT}/weathered_dock_concrete_vertical_intrinsic.png",
    "steel": f"{ASSET_ROOT}/black_steel_intrinsic.png",
    "glass": f"{ASSET_ROOT}/neutral_industrial_glass_intrinsic.png",
    "northlight": f"{ASSET_ROOT}/northlight_glass_intrinsic.png",
    "interior": f"{ASSET_ROOT}/occupied_workshop_interior_atlas.png",
    "door": f"{ASSET_ROOT}/rolling_door_intrinsic.png",
    "canopy_top": f"{ASSET_ROOT}/canopy_top_intrinsic.png",
    "canopy_soffit": f"{ASSET_ROOT}/canopy_soffit_intrinsic.png",
    "roof": f"{ASSET_ROOT}/dark_slate_metal_roof_intrinsic.png",
    "chimney": f"{ASSET_ROOT}/chimney_brick_intrinsic.png",
    "throat": f"{ASSET_ROOT}/black_steel_intrinsic.png",
}


def profile_id(size_id: str) -> str:
    return f"{PROFILE_PREFIX}-{size_id}"


def family_id(size_id: str) -> str:
    return f"daylight-sawtooth-factory-v98-{size_id}"


def _base_profile() -> dict[str, Any]:
    payload = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(payload["profiles"]["industrial_brick_original_mill"])


def _axis(mesh: dict[str, Any]) -> str:
    return str(mesh.get("axis") or mesh.get("side") or ("plan" if mesh.get("material_domain") in {"opaque_roof", "canopy_top"} else "box_projected"))


def _source(mesh: dict[str, Any], face_role: str | None = None) -> tuple[str, str, str, str]:
    domain = str(face_role or mesh["material_domain"])
    mapping = {
        "brick_wall": (ASSETS["brick"], "elevation", "ordinary_red_brick_field", "ground"),
        "brick_pier": (ASSETS["brick"], "elevation", "ordinary_red_brick_field", "ground"),
        "brick_gable": (ASSETS["brick"], "elevation", "ordinary_red_brick_field", "roof"),
        "brick_trim": (ASSETS["brick_return"], "elevation", "brick_construction_return", "ground"),
        "opening_return": (ASSETS["brick_return"], "elevation", "brick_construction_return", "ground"),
        "stone_sill": (ASSETS["stone"], "elevation", "pale_stone_sill_cap", "ground"),
        "dock_concrete": (ASSETS["concrete"], "elevation", "dock_concrete", "ground"),
        "steel_sash": (ASSETS["steel"], "elevation", "steel_sash_metal", "ground"),
        "recessed_glazing": (ASSETS["glass"], "glass", "wall_window_glass", "ground"),
        "interior_card": (ASSETS["interior"], "elevation", "wall_window_interior_card", "ground"),
        "rolling_door": (ASSETS["door"], "elevation", "rolling_door_metal", "ground"),
        "dock_canopy": (ASSETS["canopy_top"], "elevation", "canopy_top", "fixed"),
        "canopy_top": (ASSETS["canopy_top"], "elevation", "canopy_top", "fixed"),
        "canopy_fascia": (ASSETS["steel"], "elevation", "canopy_fascia", "fixed"),
        "canopy_soffit": (ASSETS["canopy_soffit"], "elevation", "canopy_soffit", "fixed"),
        "opaque_roof": (ASSETS["roof"], "elevation", "opaque_tooth_roof", "roof"),
        "northlight_glass": (ASSETS["northlight"], "glass", "northlight_glass", "roof"),
        "northlight_frame": (ASSETS["steel"], "elevation", "northlight_frame_flashing", "roof"),
        "brick_chimney": (ASSETS["chimney"], "elevation", "chimney_brick_wrap", "fixed"),
        "chimney_exterior": (ASSETS["chimney"], "elevation", "chimney_brick_wrap", "fixed"),
        "chimney_interior": (ASSETS["throat"], "elevation", "chimney_throat", "fixed"),
        "chimney_ring_cap": (ASSETS["stone"], "elevation", "chimney_band_cap", "fixed"),
        "chimney_bottom_ring": (ASSETS["chimney"], "elevation", "chimney_brick_wrap", "fixed"),
        "dock_steel": (ASSETS["steel"], "elevation", "canopy_fascia", "fixed"),
        "roof_metal": (ASSETS["steel"], "elevation", "northlight_frame_flashing", "roof"),
    }
    if domain not in mapping:
        raise KeyError(f"unmapped daylight factory material domain {domain!r} on {mesh['name']!r}")
    return mapping[domain]


def _carrier(mesh: dict[str, Any], face_indices: list[int], face_role: str | None = None) -> dict[str, Any]:
    xs = [float(vertex[0]) for vertex in mesh["vertices"]]
    ys = [float(vertex[1]) for vertex in mesh["vertices"]]
    zs = [float(vertex[2]) for vertex in mesh["vertices"]]
    axis = _axis(mesh)
    # Locked sloped roof carriers already have exact topology. Dominant-face
    # world projection keeps metric direction without requiring a flat plan quad.
    if axis == "plan":
        axis = "box_projected"
    source, material_role, layer, floor_role = _source(mesh, face_role)
    span = max(xs) - min(xs) if axis in {"front", "rear", "plan"} else max(ys) - min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{face_role or 'sticker'}", "kind": "carrier_skin",
        "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, 0.01), "height_m": max(max(zs) - min(zs), 0.01),
        "face_indices": face_indices, "material_role": material_role, "floor_role": floor_role,
        "finish_class": f"geometry_conditioned_{layer}", "sticker_layer": layer,
        "final_surface_coverage": True,
    }
    if layer in {"ordinary_red_brick_field", "brick_construction_return", "chimney_brick_wrap"}:
        item["world_metric_uv_tile_m"] = 1.35
    if layer == "opaque_tooth_roof":
        # A non-divisor tile size plus a deterministic phase per tooth keeps
        # the continuous roof field at credible slate scale without stamping
        # the same weathering patch onto all six slopes.
        tooth = int(mesh.get("tooth", 0))
        item.update(world_metric_uv_tile_m=5.7,
                    world_metric_uv_u_offset=(tooth * 0.173) % 1.0,
                    world_metric_uv_v_offset=(tooth * 0.311) % 1.0)
    if material_role == "glass":
        item["glass_profile"] = "industrial_sash"
        item["transparency_mode"] = "BLENDED"
        if layer == "wall_window_glass":
            item.update(surface_alpha_override=0.26, roughness_override=0.07, transmission_override=0.90,
                        specular_ior_level_override=0.34, coat_weight_override=0.10,
                        emission_strength_override=0.0)
        else:
            tooth = int(mesh.get("tooth", 0))
            item.update(surface_alpha_override=0.34, roughness_override=0.10, transmission_override=0.82,
                        specular_ior_level_override=0.38, coat_weight_override=0.12,
                        emission_strength_override=0.018 + 0.004 * (tooth % 3),
                        world_metric_uv_tile_m=7.3,
                        world_metric_uv_u_offset=(tooth * 0.137) % 1.0,
                        world_metric_uv_v_offset=(tooth * 0.227) % 1.0)
    if layer == "wall_window_interior_card":
        bay_index = int(mesh.get("bay_index", mesh.get("bay", 0))) % 8
        # The occupied-workshop atlas is 4 columns x 2 rows. Select one cell,
        # never a full-height eighth-width strip spanning both rows; the old
        # mapping created the identical hard horizontal split in every pane.
        atlas_col, atlas_row = bay_index % 4, bay_index // 4
        item.update(uv_u_min=atlas_col / 4, uv_u_max=(atlas_col + 1) / 4,
                    uv_v_min=atlas_row / 2, uv_v_max=(atlas_row + 1) / 2,
                    emission_strength_override=0.24)
    return item


def _build_profile(size_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = build_geometry(size_id)
    width = float(geometry["dimensions"]["width_m"])
    depth = float(geometry["dimensions"]["depth_m"])
    carriers = []
    for mesh in geometry["meshes"]:
        groups: dict[str, list[int]] = {}
        for index, role in enumerate(mesh.get("face_roles") or [mesh["material_domain"]] * len(mesh["faces"])):
            groups.setdefault(str(role), []).append(index)
        carriers.extend(_carrier(mesh, indices, role) for role, indices in groups.items())
    profile = _base_profile()
    profile.update({
        "identity": f"Daylight Sawtooth Factory V98 Sticker LEGO — {size_id}",
        "massing_graph": {
            "schema": "massing-graph@1", "profile": profile_id(size_id),
            "description": "One-storey brick daylight factory with same-handed sawtooth northlights, singular dock and detached chimney.",
            "height_m": 22.0,
            "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": 1,
                                     "tooth_module_m": 10.0},
            "recipe_contract": {
                # Overall assembled bounds include the reference-locked,
                # detached rear/right chimney. The selectable occupied
                # footprint remains width x depth; this bounded envelope is
                # not permission to stretch the factory or its stickers.
                "footprint_projection_allowance_m": 10.0,
                "projection_owner": "detached_hollow_chimney",
                "occupied_footprint_excludes_projection": True,
            },
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial", "context"],
            "nodes": [{"id": f"v98_daylight_locked_{size_id}", "kind": "locked_mesh_bundle",
                       "location": [0, 0, 0], "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
            "assemblies": carriers,
            "surface_audit": geometry["surface_audit"],
            "floor_sticker_contract": {
                "required": True,
                "floor_count": 1,
                "floor_datums_m": [0.0, 6.0],
                "roof_starts_at_z_m": 5.95,
                "roles": ["ground"],
                "tooth_module_m": 10.0,
                "forbid_floor_band_gaps": True,
                "forbid_floor_band_overlaps": True,
                "forbid_roof_below_roof_datum": True,
                "forbid_nonuniform_scale": True,
            },
            "final_surface_audit": {"required": True, "forbid_generic_materials": True,
                                    "required_finish_property": "final_surface_coverage"},
            "size_matrix": SIZE_MATRIX, "selected_size": size_id,
        },
        "presentation": {"identity_yaw_degrees": -32.0, "street_yaw_degrees": -18.0,
                         "street_distance_scale": 1.12, "identity_distance_scale": 1.05},
    })
    profile["dimension_overrides"] = {"width_m": width, "depth_m": depth,
                                      "default_floors": 1, "min_floors": 1, "max_floors": 1}
    profile["production_contract"] = {
        "identity_mode": "massing_graph",
        "fixed_identity": ["one occupied storey", "same-handed sawtooth roof", "singular three-door dock", "detached hollow chimney"],
        "repeatable_capacity": ["complete 10 m tooth plus paired 5 m facade bays horizontally"],
        "representation": "locked_geometry_plus_carrier_space_stickers",
        "placement_model": "lego_polygon_fit_with_two_discrete_width_tiers",
        "architect_score_target": 95,
        "clay_lock": {"required": True, "status": f"v98_{size_id}_locked", "geometry_sha256": geometry["geometry_sha256"]},
        "reference_authority": "exact_images_override_conflicting_rollout_metadata",
        "rear_reference_class": "constrained_completion_not_exact_rear",
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size_id, "whole_modules_only": True,
                             "vertical_scaling": "forbidden", "depth_scaling": "forbidden",
                             "nonuniform_sticker_scale_allowed": False},
    }
    conditioned, carrier_package = condition_profile(profile, geometry, score_target=95)
    return conditioned, carrier_package


def main() -> None:
    profiles: dict[str, Any] = {}
    packages: dict[str, Any] = {}
    registry = {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID,
                "variant_id": VARIANT_ID, "tiers": []}
    for size_id in SIZE_MATRIX:
        profile, package = _build_profile(size_id)
        profiles[profile_id(size_id)] = profile
        packages[size_id] = package
        size = SIZE_MATRIX[size_id]
        registry["tiers"].append({"id": size_id, "signature_profile_id": profile_id(size_id),
                                  "family_id": family_id(size_id), **size})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    OUTPUT.write_text(json.dumps({"schema": "architectural-signatures@1", "override_profiles": [],
                                  "profiles": profiles}, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    PACKAGE.write_text(json.dumps({"schema": "sticker-carrier-space-packages@1", "packages": packages}, indent=2) + "\n", encoding="utf-8")
    CONTRACT.write_text(json.dumps({
        "schema": "siteforge.daylight-sawtooth-sticker-lego@1", "version": "v98.1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
        "reference_authority": "exact variant_0 images override rollout floor conflict",
        "fixed_identity": ["one occupied storey", "same-handed sawtooth northlights", "one three-door dock and canopy", "one detached hollow chimney"],
        "size_matrix": SIZE_MATRIX, "continuous_resize_allowed": False, "vertical_scaling_allowed": False,
        "hard_stops": ["wrong tooth count", "mixed roof handedness", "repeated loading dock", "solid chimney", "unowned visible polygon"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
