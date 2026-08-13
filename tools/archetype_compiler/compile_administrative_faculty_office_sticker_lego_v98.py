"""Compile the V98 Administrative Faculty Office Sticker LEGO family."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_administrative_faculty_office_sticker_lego_v98 import (
    ARCHETYPE_ID, SIZE_MATRIX, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile

TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzz_administrative_faculty_office_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "administrative_faculty_office_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "administrative_faculty_office_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "administrative_faculty_office_sticker_lego_v98_contract.json"
PROFILE_PREFIX = "administrative-faculty-office-sticker-lego"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/administrative_faculty_office_v98"
ASSETS = {
    "brick_front": f"{ASSET_ROOT}/umber_brick_front_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/umber_brick_return_intrinsic.png",
    "entry_stone": f"{ASSET_ROOT}/entry_concrete_reveal_intrinsic.png",
    "plinth": f"{ASSET_ROOT}/cast_stone_plinth_intrinsic.png",
    "bronze_panel": f"{ASSET_ROOT}/weathered_bronze_panel_intrinsic.png",
    "bronze_fin": f"{ASSET_ROOT}/weathered_bronze_fin_intrinsic.png",
    "bronze_coping": f"{ASSET_ROOT}/weathered_bronze_coping_intrinsic.png",
    "bronze_screen": f"{ASSET_ROOT}/weathered_bronze_screen_intrinsic.png",
    "glass": f"{ASSET_ROOT}/clear_office_glass_intrinsic.png",
    "fritted_glass": f"{ASSET_ROOT}/fritted_entry_glass_intrinsic.png",
    "interior": f"{ASSET_ROOT}/occupied_office_interior_atlas.png",
    "roof": f"{ASSET_ROOT}/roof_gravel_intrinsic.png",
    "mechanical": f"{ASSET_ROOT}/mechanical_casing_intrinsic.png",
    "mechanical_duct": f"{ASSET_ROOT}/mechanical_duct_intrinsic.png",
    "mechanical_pipe": f"{ASSET_ROOT}/mechanical_pipe_intrinsic.png",
}


def profile_id(size_id: str) -> str:
    return f"{PROFILE_PREFIX}-{size_id}"


def family_id(size_id: str) -> str:
    return f"administrative-faculty-office-v98-{size_id}"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _axis(mesh: dict[str, Any]) -> str:
    side = str(mesh.get("side", ""))
    if side in {"front", "rear", "left", "right"}:
        return side
    # The roof is a closed, locked box carrier. Per-face projection preserves
    # its full top/edge coverage without pretending it is a single plan quad.
    return "box_projected"


def _floor_role(mesh: dict[str, Any], domain: str) -> str:
    if domain in {"gravel_roof", "brick_parapet", "bronze_screen", "bronze_louver",
                  "mechanical_equipment", "mechanical_duct", "mechanical_pipe"}:
        return "roof"
    if "level" in mesh:
        level = int(mesh["level"])
        return "ground" if level == 0 else "top" if level == 4 else "middle"
    return "fixed"


def _source(mesh: dict[str, Any], face_role: str | None = None) -> tuple[str, str, str]:
    domain = str(face_role or mesh["material_domain"])
    side = str(mesh.get("side", ""))
    is_entry_glass = domain == "recessed_glazing" and "vertical_entry_loggia" in str(mesh["name"])
    mapping = {
        "umber_brick": (ASSETS["brick_front"] if side == "front" else ASSETS["brick_return"], "elevation", "umber_brick_masonry"),
        "bronze_and_brick_infill": (ASSETS["brick_front"], "elevation", "projecting_bay_umber_brick_infill"),
        "opening_return": (ASSETS["brick_return"], "elevation", "deep_opening_or_lobby_return"),
        "cream_masonry": (ASSETS["entry_stone"], "elevation", "entry_concrete_reveal"),
        "masonry_slab_band": (ASSETS["brick_return"], "elevation", "subdued_umber_brick_slab_band"),
        "brick_parapet": (ASSETS["brick_return"], "elevation", "brick_parapet"),
        "bronze_frame": (ASSETS["bronze_panel"], "elevation", "projecting_bronze_frame"),
        "bronze_slab_band": (ASSETS["bronze_coping"], "elevation", "projecting_bronze_slab_band"),
        "bronze_mullion": (ASSETS["bronze_fin"], "elevation", "physical_bronze_mullion"),
        "bronze_door": (ASSETS["bronze_panel"], "elevation", "physical_bronze_door"),
        "recessed_glazing": (
            ASSETS["fritted_glass"] if is_entry_glass else ASSETS["glass"],
            "glass",
            "physical_fritted_entry_glass" if is_entry_glass else "physical_clear_office_glass",
        ),
        "interior_card": (ASSETS["interior"], "elevation", "occupied_office_interior_card"),
        "gravel_roof": (ASSETS["roof"], "elevation", "flat_gravel_roof"),
        "bronze_screen": (ASSETS["bronze_screen"], "elevation", "mechanical_screen"),
        "bronze_louver": (ASSETS["bronze_fin"], "elevation", "physical_mechanical_louver"),
        "mechanical_equipment": (ASSETS["mechanical"], "elevation", "bounded_mechanical_equipment"),
        "mechanical_duct": (ASSETS["mechanical_duct"], "elevation", "bounded_low_mechanical_duct"),
        "mechanical_pipe": (ASSETS["mechanical_pipe"], "elevation", "bounded_low_mechanical_pipe"),
    }
    if domain not in mapping:
        raise KeyError(f"unmapped administrative office domain {domain!r} on {mesh['name']!r}")
    return mapping[domain]


def _carrier(mesh: dict[str, Any], face_indices: list[int], face_role: str | None = None) -> dict[str, Any]:
    xs, ys, zs = ([float(v[i]) for v in mesh["vertices"]] for i in range(3))
    axis = _axis(mesh)
    source, material_role, layer = _source(mesh, face_role)
    span = max(xs) - min(xs) if axis in {"front", "rear", "plan"} else max(ys) - min(ys)
    domain = str(face_role or mesh["material_domain"])
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{face_role or 'sticker'}", "kind": "carrier_skin",
        "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs) - min(zs), .01),
        "face_indices": face_indices, "material_role": material_role,
        "floor_role": _floor_role(mesh, domain), "finish_class": f"geometry_conditioned_{layer}",
        "sticker_layer": layer, "final_surface_coverage": True,
    }
    if domain in {"umber_brick", "bronze_and_brick_infill", "opening_return", "masonry_slab_band", "brick_parapet"}:
        item["world_metric_uv_tile_m"] = 1.25
    elif domain == "gravel_roof":
        item.update(world_metric_uv_tile_m=4.7, world_metric_uv_u_offset=.19, world_metric_uv_v_offset=.37)
    elif domain.startswith("bronze"):
        item.update(world_metric_uv_tile_m=3.6, metallic_override=.55, roughness_override=.43)
    if domain == "recessed_glazing":
        if "vertical_entry_loggia" in str(mesh["name"]):
            # Frit is supplied by the registered sticker; retain the proven
            # office glass physical shader and specialize its optical values.
            item.update(glass_profile="office_clear_occupied", transparency_mode="BLENDED",
                        surface_alpha_override=.68, roughness_override=.12, transmission_override=.70,
                        specular_ior_level_override=.56, coat_weight_override=.38, emission_strength_override=.012)
        else:
            item.update(glass_profile="office_clear_occupied", transparency_mode="BLENDED",
                        surface_alpha_override=.62, roughness_override=.08, transmission_override=.80,
                        specular_ior_level_override=.58, coat_weight_override=.42, emission_strength_override=.012)
    if domain == "interior_card":
        side_n = {"front": 0, "right": 1, "rear": 2, "left": 3}.get(str(mesh.get("side")), 0)
        # Co-prime weighting avoids identical cells in adjacent rows/stacks and
        # distributes all eight rooms over front, returns, and constrained rear.
        cell = (side_n * 5 + int(mesh.get("bay", 0)) * 3 + int(mesh.get("level", 0)) * 5) % 8
        col, row = cell % 4, cell // 4
        lobby_card = "vertical_entry_loggia" in str(mesh["name"])
        item.update(uv_u_min=col / 4, uv_u_max=(col + 1) / 4,
                    uv_v_min=row / 2, uv_v_max=(row + 1) / 2,
                    emission_strength_override=.02 if lobby_card else .035)
    if domain in {"mechanical_equipment", "mechanical_duct", "mechanical_pipe"}:
        index = int(str(mesh["name"]).rsplit("_", 1)[-1])
        item.update(world_metric_uv_tile_m=2.1,
                    world_metric_uv_u_offset=(index * .173) % 1.0,
                    world_metric_uv_v_offset=(index * .317) % 1.0)
    return item


def _build_profile(size_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = build_geometry(size_id)
    width, depth = (float(geometry["dimensions"][key]) for key in ("width_m", "depth_m"))
    carriers: list[dict[str, Any]] = []
    for mesh in geometry["meshes"]:
        groups: dict[str, list[int]] = {}
        for index, role in enumerate(mesh.get("face_roles") or [mesh["material_domain"]] * len(mesh["faces"])):
            groups.setdefault(str(role), []).append(index)
        carriers.extend(_carrier(mesh, indices, role) for role, indices in groups.items())
    profile = _base_profile()
    profile.update({
        "identity": f"Administrative Faculty Office V98 Sticker LEGO — {size_id}",
        "massing_graph": {
            "schema": "massing-graph@1", "profile": profile_id(size_id),
            "description": "Five-storey umber-brick academic office with a 1.8 m deep open lobby slot, singular broad bronze projection and six-zone screened mechanical court.",
            "height_m": 21.32,
            "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": 5, "ordinary_stack_module_m": 3.75},
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial", "context"],
            "nodes": [{"id": f"v98_admin_locked_{size_id}", "kind": "locked_mesh_bundle", "location": [0, 0, 0],
                       "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
            "assemblies": carriers, "surface_audit": geometry["surface_audit"],
            "floor_sticker_contract": {"required": True, "floor_count": 5,
                "floor_datums_m": [0.0, 4.2, 7.8, 11.4, 15.0, 18.6], "roof_starts_at_z_m": 18.6,
                "roles": ["ground", "middle", "top", "fixed", "roof"],
                "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
                "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
            "final_surface_audit": {"required": True, "forbid_generic_materials": True,
                                    "required_finish_property": "final_surface_coverage"},
            "size_matrix": SIZE_MATRIX, "selected_size": size_id,
        },
        "presentation": {"identity_yaw_degrees": -28.0, "street_yaw_degrees": -15.0,
                         "street_distance_scale": 1.08, "identity_distance_scale": 1.02},
    })
    profile["dimension_overrides"] = {"width_m": width, "depth_m": depth, "default_floors": 5, "min_floors": 5, "max_floors": 5}
    profile["production_contract"] = {
        "identity_mode": "massing_graph",
        "fixed_identity": ["five occupied storeys", "one 1.8m deep open lobby slot", "one 10m projecting bronze volume", "one six-zone mechanical court"],
        "repeatable_capacity": ["pairs of complete 3.75m ordinary office stacks left of fixed entry"],
        "representation": "locked_geometry_plus_carrier_space_stickers",
        "placement_model": "lego_polygon_fit_with_two_discrete_width_tiers", "architect_score_target": 95,
        "clay_lock": {"required": True, "status": f"v98_{size_id}_locked", "geometry_sha256": geometry["geometry_sha256"]},
        "reference_authority": "exact three images override conflicting generic metadata",
        "rear_reference_class": "constrained_completion_not_exact_rear",
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size_id, "whole_modules_only": True,
                             "vertical_scaling": "forbidden", "depth_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
    }
    return condition_profile(profile, geometry, score_target=95)


def main() -> None:
    profiles: dict[str, Any] = {}
    packages: dict[str, Any] = {}
    registry = {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "tiers": []}
    for size_id in SIZE_MATRIX:
        profile, package = _build_profile(size_id)
        profiles[profile_id(size_id)], packages[size_id] = profile, package
        registry["tiers"].append({"id": size_id, "signature_profile_id": profile_id(size_id), "family_id": family_id(size_id), **SIZE_MATRIX[size_id]})
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles}, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    PACKAGE.write_text(json.dumps({"schema": "sticker-carrier-space-packages@1", "packages": packages}, indent=2) + "\n", encoding="utf-8")
    CONTRACT.write_text(json.dumps({"schema": "siteforge.administrative-faculty-office-sticker-lego@1", "version": "v98.3",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
        "reference_authority": "exact variant_0 images override conflicting rollout metadata",
        "fixed_identity": ["five occupied storeys", "one open deep entry", "one broad projecting bronze volume", "one six-zone mechanical court"],
        "size_matrix": SIZE_MATRIX, "continuous_resize_allowed": False, "vertical_scaling_allowed": False, "depth_scaling_allowed": False,
        "hard_stops": ["wrong floor count", "shallow or sealed entry", "missing narrow or duplicated bronze volume", "generic roof", "unowned visible polygon"]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
