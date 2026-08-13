"""Compile the exact-reference B8 collegiate brick courtyard Sticker LEGO family."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_collegiate_brick_corner_block_sticker_lego_v98 import (
    ARCHETYPE_ID, DATUMS, SIZES, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzzzzz_collegiate_brick_corner_block_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "collegiate_brick_corner_block_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "collegiate_brick_corner_block_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "collegiate_brick_corner_block_sticker_lego_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/collegiate_brick_corner_block_v98"
ASSETS = {
    "brick_front": f"{ASSET_ROOT}/warm_tan_brick_front_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/warm_tan_brick_return_intrinsic.png",
    "brick_court": f"{ASSET_ROOT}/subdued_courtyard_brick_intrinsic.png",
    "precast": f"{ASSET_ROOT}/pale_precast_intrinsic.png",
    "base": f"{ASSET_ROOT}/weathered_base_plinth_reveal_intrinsic.png",
    "coping": f"{ASSET_ROOT}/pale_coping_cornice_intrinsic.png",
    "joint": f"{ASSET_ROOT}/dark_joint_sealant_intrinsic.png",
    "bronze_frame": f"{ASSET_ROOT}/bronze_oriel_frames_intrinsic.png",
    "bronze_spandrel": f"{ASSET_ROOT}/bronze_spandrel_casing_intrinsic.png",
    "bronze_screen": f"{ASSET_ROOT}/bronze_mechanical_screen_intrinsic.png",
    "glass_residential": f"{ASSET_ROOT}/physical_residential_glass_intrinsic.png",
    "glass_corner": f"{ASSET_ROOT}/physical_corner_glass_intrinsic.png",
    "interior_residential": f"{ASSET_ROOT}/residential_interior_atlas.png",
    "interior_corner": f"{ASSET_ROOT}/corner_interior_atlas.png",
    "interior_lobby": f"{ASSET_ROOT}/ground_lobby_interior_atlas.png",
    "gravel": f"{ASSET_ROOT}/gravel_ballast_roof_intrinsic.png",
    "membrane": f"{ASSET_ROOT}/dark_inner_membrane_intrinsic.png",
    "service_path": f"{ASSET_ROOT}/membrane_service_path_intrinsic.png",
    "flashing": f"{ASSET_ROOT}/roof_perimeter_flashing_intrinsic.png",
    "hvac": f"{ASSET_ROOT}/aged_galvanized_hvac_intrinsic.png",
    "service": f"{ASSET_ROOT}/galvanized_duct_rails_vents_intrinsic.png",
    "rooflight_glass": f"{ASSET_ROOT}/rooflight_glass_intrinsic.png",
    "rooflight_curb": f"{ASSET_ROOT}/rooflight_curb_intrinsic.png",
    "threshold": f"{ASSET_ROOT}/threshold_intrinsic.png",
    "hardware": f"{ASSET_ROOT}/door_hardware_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/graduate-family-housing/variant_0.png": "975880325493f35fdae5367aeeccd5648ebe38f57baf5d7b7aa2ce024c17f747",
    "frontend/public/archetypes/buildings/graduate-family-housing/variant_0_angle_60.jpg": "3af8854ea010429a2d4cc1c87862b04eb91a93294767467d393b80a41598c4df",
    "frontend/public/archetypes/buildings/graduate-family-housing/variant_0_angle_90.jpg": "21e0c4e9ab7fd36fac73258b6294f492ca4af6424dd0b85c753f8604ef3f2dc5",
}
GEOMETRY_HASHES = {
    "canonical": "a3dc8607f4d04ef819f728762267bca3254ef386390aa689480b045d8833b740",
    "extended": "62d7b04ab8800debbaa3bfc1b7df99afe4d5b8e7eaeaa4665741fffd88e18bd7",
}
SIZE_MATRIX = {
    "canonical": {"width_m": 42.0, "depth_m": 38.0, "horizontal_modules": 0},
    "extended": {"width_m": 49.0, "depth_m": 38.0, "horizontal_modules": 1},
}


def profile_id(size: str) -> str: return f"collegiate-brick-corner-block-sticker-lego-{size}"
def family_id(size: str) -> str: return f"collegiate-brick-corner-block-v98-{size}"


def _base_profile() -> dict[str, Any]:
    profiles = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))["profiles"]
    return deepcopy(profiles["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(v[i]) for v in mesh["vertices"]] for i in range(3))  # type: ignore[return-value]


def _is_corner(mesh: dict[str, Any]) -> bool:
    n = str(mesh["name"])
    return n.startswith(("corner_oriel_", "corner_lobby_", "lobby_", "oriel_")) or "oriel" in n


def _is_court(mesh: dict[str, Any]) -> bool:
    return bool(mesh.get("courtyard")) or str(mesh.get("side", "")).startswith("court_") or str(mesh["name"]).startswith("court_")


def _vertical_role(mesh: dict[str, Any]) -> str:
    level = int(mesh.get("level", mesh.get("floor", 0)) or 0)
    return "ground" if level == 0 else "top" if level == 4 else "middle"


def _floor_role(mesh: dict[str, Any], faces: list[int]) -> str:
    n, d, k = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if d in {"gravel_roof", "dark_roof_membrane"}: return "roof" if faces == [1] else "crown"
    if d == "rooflight_glass": return "roof_equipment"
    if d in {"roof_equipment", "galvanized_metal"}: return "roof_equipment"
    if d == "bronze_screen": return "roof_screen"
    if k in {"closed_parapet_run", "parapet_corner_cap", "parapet_entry_endpoint_cap",
             "parapet_crown_endpoint_cap", "main_coping", "corner_crown", "gravel_roof_endpoint_cap"}:
        return "crown"
    if k == "entry_precast_blade": return "blades"
    if "entry" in n or "lobby" in n: return "corner_ground" if _is_corner(mesh) else "entry"
    role = _vertical_role(mesh)
    if _is_corner(mesh): return f"corner_{role}"
    if _is_court(mesh): return f"courtyard_{role}"
    return role


def _face_groups(mesh: dict[str, Any]) -> list[list[int]]:
    d = str(mesh["material_domain"])
    if d in {"gravel_roof", "dark_roof_membrane", "rooflight_glass"}: return [[1], [0, 2, 3, 4, 5]]
    return [list(range(len(mesh["faces"])))]


def _source(mesh: dict[str, Any], faces: list[int]) -> tuple[str, str, str]:
    n, d, k = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if mesh.get("explicit_underside_role") == "pale_precast_underside":
        if d != "precast":
            raise ValueError(f"pale terminal contract requires precast domain on {n!r}, got {d!r}")
        return ASSETS["precast"], "elevation", "pale_precast_terminal_and_underside"
    if d == "warm_brick":
        if _is_court(mesh): return ASSETS["brick_court"], "elevation", "courtyard_brick"
        if str(mesh.get("side", "")) == "front" or n.startswith("front_"):
            return ASSETS["brick_front"], "elevation", "warm_brick_front"
        return ASSETS["brick_return"], "elevation", "warm_brick_return"
    if d == "precast_return": return ASSETS["base"], "elevation", "precast_opening_return"
    if d == "precast":
        if k in {"main_coping", "closed_parapet_run", "parapet_corner_cap", "parapet_entry_endpoint_cap",
                 "parapet_crown_endpoint_cap", "court_coping_corner_cap"} or "coping" in n:
            return ASSETS["coping"], "elevation", "pale_coping_cornice"
        if "plinth" in n or k in {"ground_closure_corner_cap", "corner_lobby_soffit"}:
            return ASSETS["base"], "elevation", "weathered_base_precast"
        return ASSETS["precast"], "elevation", "pale_precast"
    if d == "bronze":
        if k in {"oriel_spandrel_band", "oriel_cap", "corner_crown"}:
            return ASSETS["bronze_spandrel"], "elevation", "bronze_spandrel_casing"
        return ASSETS["bronze_frame"], "elevation", "bronze_oriel_frame"
    if d == "bronze_screen": return ASSETS["bronze_screen"], "elevation", "bronze_mechanical_screen"
    if d == "interior_architecture":
        return ASSETS["precast"], "elevation", "pale_room_architecture"
    if d == "pale_interior": return ASSETS["precast"], "elevation", "pale_stair_lobby_architecture"
    if d == "bright_interior_card": return ASSETS["interior_lobby"], "elevation", "bright_lobby_back_card"
    if d == "residential_slab": return ASSETS["base"], "elevation", "residential_slab_precast"
    if d == "recessed_glazing":
        corner = _is_corner(mesh) or "entry" in n
        return ASSETS["glass_corner" if corner else "glass_residential"], "glass", "physical_corner_glass" if corner else "physical_residential_glass"
    if d in {"interior_card", "interior_backing"}:
        if "lobby" in n or "entry" in n: key, layer = "interior_lobby", "ground_lobby_card"
        elif _is_corner(mesh): key, layer = "interior_corner", "corner_interior_card"
        else: key, layer = "interior_residential", "residential_interior_card"
        return ASSETS[key], "elevation", f"opaque_{layer}_backing" if d == "interior_backing" else layer
    if d == "gravel_roof":
        return (ASSETS["gravel"], "plan", "gravel_ballast_roof") if faces == [1] else (ASSETS["flashing"], "elevation", "roof_edge_flashing")
    if d == "dark_roof_membrane":
        return (ASSETS["membrane"], "plan", "dark_inner_membrane") if faces == [1] else (ASSETS["flashing"], "elevation", "roof_edge_flashing")
    if d == "roof_equipment": return ASSETS["hvac"], "elevation", "aged_galvanized_hvac"
    if d == "galvanized_metal": return ASSETS["service"], "elevation", "galvanized_roof_service"
    if d == "rooflight_glass":
        return (ASSETS["rooflight_glass"], "glass", "physical_rooflight_glass") if faces == [1] else (ASSETS["rooflight_curb"], "elevation", "rooflight_curb")
    raise KeyError(f"unmapped domain {d!r} on {n!r}/{k!r}")


def _axis(mesh: dict[str, Any], material_role: str, faces: list[int]) -> str:
    if material_role == "plan": return "plan"
    side = str(mesh.get("side", ""))
    return {"court_front": "front", "court_rear": "rear", "court_left": "left", "court_right": "right"}.get(
        side, side if side in {"front", "rear", "left", "right"} else "box_projected")


def _atlas(mesh: dict[str, Any]) -> tuple[int, int, int]:
    n = str(mesh["name"]); side = str(mesh.get("side", "")); level = int(mesh.get("level", 0) or 0)
    bay = int(mesh.get("bay", mesh.get("light", 0)) or 0)
    side_number = {"front": 0, "right": 1, "rear": 2, "left": 3,
                   "court_front": 4, "court_right": 5, "court_rear": 6, "court_left": 7}.get(side, 0)
    cell = (side_number * 5 + bay * 3 + level * 2 + (7 if "entry" in n else 0) + (5 if _is_corner(mesh) else 0)) % 8
    return cell, cell % 4, cell // 4


def _carrier(mesh: dict[str, Any], faces: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh); source, material_role, layer = _source(mesh, faces); axis = _axis(mesh, material_role, faces)
    span = max(xs)-min(xs) if axis in {"front", "rear"} else max(ys)-min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{'_'.join(map(str, faces))}_sticker", "kind": "carrier_skin",
        "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])], "source_image_path": source,
        "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs)-min(zs), .01), "face_indices": faces,
        "material_role": "elevation" if material_role == "plan" else material_role,
        "floor_role": _floor_role(mesh, faces), "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer, "final_surface_coverage": True,
    }
    if axis == "plan": item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    elif axis == "box_projected": item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if layer.startswith(("warm_brick", "courtyard_brick")):
        item.update(world_metric_uv_tile_m=2.4, world_metric_uv_u_offset=0.0,
                    world_metric_uv_v_offset=0.0, roughness_override=.76)
    elif "precast" in layer or layer == "residential_slab_precast": item.update(world_metric_uv_tile_m=2.0, roughness_override=.72)
    elif layer == "gravel_ballast_roof": item.update(world_metric_uv_tile_m=2.4, roughness_override=.84)
    elif layer == "dark_inner_membrane": item.update(world_metric_uv_tile_m=2.4, roughness_override=.73)
    elif layer == "bronze_mechanical_screen": item.update(world_metric_uv_tile_m=1.0, roughness_override=.42,
                                                            metallic_override=.72)
    elif layer == "aged_galvanized_hvac": item.update(world_metric_uv_tile_m=1.2, roughness_override=.38,
                                                       metallic_override=.78)
    elif layer == "galvanized_roof_service": item.update(world_metric_uv_tile_m=.9, roughness_override=.34,
                                                          metallic_override=.82)
    if material_role == "glass":
        corner = layer == "physical_corner_glass"
        item.update(glass_profile="reflective_curtain_wall" if corner else "residential_low_e",
                    transparency_mode="BLENDED", surface_alpha_override=.32 if corner else .25,
                    transmission_override=.88 if corner else .94, roughness_override=.065 if corner else .04,
                    specular_ior_level_override=.56 if corner else .46,
                    coat_weight_override=.30 if corner else .18, emission_strength_override=0.0)
    if str(mesh["material_domain"]) in {"interior_card", "interior_backing", "bright_interior_card"}:
        cell, col, row = _atlas(mesh)
        item.update(uv_u_min=col/4, uv_u_max=(col+1)/4, uv_v_min=row/2, uv_v_max=(row+1)/2,
                    atlas_cell_index=cell,
                    emission_strength_override=(0.0 if str(mesh["material_domain"]) == "interior_backing" else
                                                .12 if str(mesh["material_domain"]) == "bright_interior_card" else
                                                .095 if "lobby" in layer else .072 if "corner" in layer else .060))
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = {(str(m["name"]), i): 0 for m in geometry["meshes"] for i in range(len(m["faces"]))}
    for carrier in carriers:
        for face in carrier["face_indices"]: coverage[(str(carrier["surface_id"]), int(face))] += 1
    missing = [f"{n}:{i}" for (n, i), value in coverage.items() if value == 0]
    duplicate = [f"{n}:{i}" for (n, i), value in coverage.items() if value > 1]
    result = {"visible_face_count": len(coverage), "owned_once_count": sum(v == 1 for v in coverage.values()),
              "missing_faces": missing, "multiply_owned_faces": duplicate,
              "status": "pass" if not missing and not duplicate else "fail"}
    if result["status"] != "pass": raise ValueError(result)
    return result


def _asset_provenance() -> dict[str, Any]:
    path = TOOL_DIR / "sticker_assets/collegiate_brick_corner_block_v98/provenance.json"
    provenance = json.loads(path.read_text(encoding="utf-8"))
    for record in provenance["assets"].values():
        asset = TOOL_DIR.parents[1] / record["path"]
        if hashlib.sha256(asset.read_bytes()).hexdigest() != record["sha256"]: raise ValueError(f"asset mismatch: {asset}")
    return provenance


def _build_profile(size: str) -> tuple[dict[str, Any], dict[str, Any]]:
    provenance = _asset_provenance(); geometry = build_geometry(size)
    if geometry["geometry_sha256"] != GEOMETRY_HASHES[size]: raise ValueError("geometry lock mismatch")
    carriers = [_carrier(mesh, group) for mesh in geometry["meshes"] for group in _face_groups(mesh)]
    audit = _surface_audit(geometry, carriers); profile = _base_profile()
    roles = ["ground", "middle", "top", "entry", "blades", "corner_ground", "corner_middle", "corner_top",
             "courtyard_ground", "courtyard_middle", "courtyard_top", "crown", "roof", "roof_screen", "roof_equipment"]
    profile.update({"identity": f"Collegiate Brick Corner Block V98 Sticker LEGO - {size}", "kits": [],
        "glass_profile": "residential_low_e",
        "massing_graph": {"schema": "massing-graph@1", "profile": profile_id(size), "height_m": 19.45,
        "description": "Exact-reference five-storey brick perimeter courtyard block with singular bronze corner oriel, adjacent recessed entry, precast blades and layered gravel/mechanical roof.",
        "reference_dimensions": {"width_m": SIZES[size], "depth_m": 38.0, "floors": 5, "horizontal_module_m": 7.0},
        "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial"],
        "nodes": [{"id": f"v98_collegiate_locked_{size}", "kind": "locked_mesh_bundle", "location": [0, 0, 0],
                   "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
        "assemblies": carriers, "surface_audit": audit,
        "floor_sticker_contract": {"required": True, "floor_datums_m": list(DATUMS), "roof_starts_at_z_m": 17.2,
            "roles": roles, "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
            "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
        "final_surface_audit": {"required": True, "status": audit["status"], "visible_face_count": audit["visible_face_count"],
            "owned_once_count": audit["owned_once_count"], "forbid_generic_materials": True,
            "required_finish_property": "final_surface_coverage"},
        "exact_image_override": {"required": True, "authority": "three exact variant_0 images",
            "reference_sha256": REFERENCE_HASHES, "asset_provenance_schema": provenance["schema"]},
        "size_matrix": SIZE_MATRIX, "selected_size": size},
        "presentation": {"identity_yaw_degrees": -32.0, "street_yaw_degrees": -18.0,
                         "street_distance_scale": 1.14, "identity_distance_scale": 1.08}})
    profile["dimension_overrides"] = {"width_m": SIZES[size], "depth_m": 38.0, "default_floors": 5,
                                      "min_floors": 5, "max_floors": 5, "roof_height_m": 2.25}
    profile["production_contract"] = {"identity_mode": "massing_graph",
        "identity_authority": "exact_image_locked_collegiate_brick_corner_block",
        "fixed_identity": ["five-storey courtyard ring", "singular bronze corner oriel and crown", "adjacent recessed entry and paired precast blades", "all courtyard elevations", "layered gravel roof and bounded mechanical screen"],
        "repeatable_capacity": ["one complete 7m horizontal ring-and-roof module"],
        "representation": "locked_geometry_plus_carrier_space_stickers", "placement_model": "bounded_discrete_horizontal_lego",
        "architect_score_target": 95, "clay_lock": {"required": True, "status": f"v98_{size}_locked", "geometry_sha256": geometry["geometry_sha256"]},
        "reference_sha256": REFERENCE_HASHES, "asset_provenance": provenance["assets"],
        "lego_scalability": {"matrix": SIZE_MATRIX, "selected_size": size, "whole_modules_only": True,
            "module_width_m": 7.0, "vertical_scaling": "forbidden", "depth_scaling": "forbidden",
            "nonuniform_sticker_scale_allowed": False, "fixed_kit_counts_invariant": True},
        "hard_stops": geometry["hard_stops"] + ["missing_or_multiply_owned_visible_face", "generic_material_fallback",
            "interior_atlas_assigned_to_glass", "roof_domain_leakage", "brick_uv_not_2_4m", "partial_or_stretched_7m_module"]}
    return condition_profile(profile, geometry, score_target=95)


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    profiles = {}; packages = {}; registry = {"schema": "siteforge.sticker-lego-family@1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "identity_mode": "massing_graph", "tiers": []}
    for size in SIZE_MATRIX:
        profile, package = _build_profile(size)
        if package["status"] != "pass": raise RuntimeError(package["failures"])
        profiles[profile_id(size)] = profile; packages[size] = package
        registry["tiers"].append({"id": size, "signature_profile_id": profile_id(size), "family_id": family_id(size), **SIZE_MATRIX[size]})
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    _write(OUTPUT, {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles})
    _write(REGISTRY, registry); _write(PACKAGE, {"schema": "sticker-carrier-space-packages@1", "packages": packages})
    _write(CONTRACT, {"schema": "siteforge.collegiate-brick-corner-block-sticker-lego@1", "version": "v98.0",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "identity_authority": "three_exact_variant_0_images",
        "reference_sha256": REFERENCE_HASHES, "geometry_sha256": GEOMETRY_HASHES, "size_matrix": SIZE_MATRIX,
        "continuous_resize_allowed": False, "vertical_scaling_allowed": False, "depth_scaling_allowed": False,
        "whole_modules_only": True, "module_width_m": 7.0,
        "hard_stops": ["partial or stretched 7m module", "changed fixed corner entry courtyard or roof kit",
                       "generic fallback", "unowned or multiply owned face", "roof domain leakage", "brick UV not 2.4m"]})


if __name__ == "__main__": main()
