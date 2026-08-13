"""Compile the exact-reference industrial tilt-up concrete V98 Sticker LEGO family."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_industrial_tilt_up_concrete_sticker_lego_v98 import ARCHETYPE_ID, SIZES, VARIANT_ID, build_geometry
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzzzz_industrial_tilt_up_concrete_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "industrial_tilt_up_concrete_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "industrial_tilt_up_concrete_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "industrial_tilt_up_concrete_sticker_lego_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/industrial_tilt_up_concrete_v98"
ASSETS = {
    "warm_front": f"{ASSET_ROOT}/warm_buff_concrete_front_intrinsic.png",
    "warm_return": f"{ASSET_ROOT}/warm_buff_concrete_return_intrinsic.png",
    "cool_concrete": f"{ASSET_ROOT}/cool_gray_side_rear_concrete_intrinsic.png",
    "plinth": f"{ASSET_ROOT}/weathered_plinth_reveal_concrete_intrinsic.png",
    "joint": f"{ASSET_ROOT}/dark_joint_sealant_intrinsic.png",
    "coping": f"{ASSET_ROOT}/pale_coping_flashing_intrinsic.png",
    "aluminum": f"{ASSET_ROOT}/charcoal_bronze_aluminum_intrinsic.png",
    "glass": f"{ASSET_ROOT}/physical_neutral_glass_intrinsic.png",
    "lower_interior": f"{ASSET_ROOT}/lobby_lower_office_interior_atlas.png",
    "upper_interior": f"{ASSET_ROOT}/upper_office_interior_atlas.png",
    "canopy_top": f"{ASSET_ROOT}/dark_canopy_top_intrinsic.png",
    "canopy_fascia": f"{ASSET_ROOT}/dark_canopy_fascia_intrinsic.png",
    "canopy_soffit": f"{ASSET_ROOT}/dark_canopy_soffit_posts_intrinsic.png",
    "overhead_door": f"{ASSET_ROOT}/ribbed_overhead_doors_intrinsic.png",
    "dock": f"{ASSET_ROOT}/dock_rubber_hardware_intrinsic.png",
    "threshold": f"{ASSET_ROOT}/galvanized_threshold_intrinsic.png",
    "personnel_door": f"{ASSET_ROOT}/personnel_doors_intrinsic.png",
    "bollard": f"{ASSET_ROOT}/safety_yellow_bollards_intrinsic.png",
    "tpo": f"{ASSET_ROOT}/off_white_tpo_intrinsic.png",
    "roof_patch": f"{ASSET_ROOT}/roof_perimeter_patch_intrinsic.png",
    "rooflight_glass": f"{ASSET_ROOT}/rooflight_glass_intrinsic.png",
    "rooflight_curb": f"{ASSET_ROOT}/rooflight_curb_intrinsic.png",
    "service": f"{ASSET_ROOT}/aged_galvanized_hvac_duct_vents_intrinsic.png",
    "grille": f"{ASSET_ROOT}/service_grille_intrinsic.png",
    "sign": f"{ASSET_ROOT}/blank_sign_plate_intrinsic.png",
    "openwork_backing": f"{ASSET_ROOT}/openwork_shadow_backing_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/industrial_park_modernism/variant_0.png": "de5e08df02bcda3c33c5a0d9eb5f13ac4c8f4d4c50a5ac89ef9d0df7826baab7",
    "frontend/public/archetypes/buildings/industrial_park_modernism/variant_0_angle_60.jpg": "0e2fd31a87d156a3e8a04f0fbaea93b1e0e69606e1c4ebbe8f1a52bb9923c65b",
    "frontend/public/archetypes/buildings/industrial_park_modernism/variant_0_angle_90.jpg": "d6abca22f264b4ba34c4d43af49eb0d311236f5dadebce2ed393220e1be3817e",
}
SIZE_MATRIX = {
    "canonical": {"width_m": 60.0, "depth_m": 42.0, "rear_modules": 0},
    "extended": {"width_m": 60.0, "depth_m": 48.0, "rear_modules": 1},
}


def profile_id(size: str) -> str: return f"industrial-tilt-up-concrete-sticker-lego-{size}"
def family_id(size: str) -> str: return f"industrial-tilt-up-concrete-v98-{size}"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(v[i]) for v in mesh["vertices"]] for i in range(3))  # type: ignore[return-value]


def _floor_role(mesh: dict[str, Any]) -> str:
    n, d, k = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if d in {"tpo_roof", "roof_curb", "rooflight_glass", "roof_equipment", "galvanized_metal"}: return "roof_equipment" if d != "tpo_roof" else "roof"
    if k in {"vertical_openwork_fin", "openwork_screen_backing", "openwork_top_coping"}: return "crown"
    if k in {"parapet_run", "adjacent_finish_endpoint_cap"} and ("parapet" in n or "pylon" in n): return "crown"
    if "canopy" in n or "entrance" in n or d in {"metal_canopy", "safety_yellow"}: return "entry"
    if d in {"ribbed_overhead_door"} or "loading" in n or "receiving" in n: return "loading"
    if "pylon" in n or d == "dark_recess": return "pylon"
    if n.startswith("front_office_ribbon_") or k == "office_window_mullion":
        return "office_upper" if int(mesh.get("level", 0)) == 1 else "office_ground"
    if n.startswith("front_office_l0") or (d == "interior_card" and int(mesh.get("level", 0)) == 0): return "office_ground"
    if n.startswith("front_office_l1") or (d == "interior_card" and int(mesh.get("level", 0)) == 1): return "office_upper"
    if n.startswith("front_panel_office_l0") or n.startswith("front_panel_base"): return "office_ground"
    if n.startswith("front_panel_office_l1") or n.startswith("front_panel_middle"): return "office_upper"
    if n.startswith("rear_"): return "rear"
    if d == "industrial_slab": return "high_bay"
    if d in {"tilt_up_concrete", "concrete_return", "joint_recess", "dark_metal"}: return "high_bay"
    raise KeyError(f"unclassified role {n!r}: {d!r}/{k!r}")


def _face_groups(mesh: dict[str, Any]) -> list[list[int]]:
    n, d = str(mesh["name"]), str(mesh["material_domain"])
    if d == "tpo_roof": return [[1], [0, 2, 3, 4, 5]]
    if n == "entrance_canopy_slab": return [[1], [0], [2, 3, 4, 5]]
    if (str(mesh.get("carrier_kind", "")) in {"parapet_run", "adjacent_finish_endpoint_cap"}
            and ("parapet" in n or "pylon" in n)):
        return [[1], [0, 2, 3, 4, 5]]
    return [list(range(len(mesh["faces"])))]


def _source(mesh: dict[str, Any], faces: list[int]) -> tuple[str, str, str]:
    n, d, k, side = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", "")), str(mesh.get("side", ""))
    if d == "tpo_roof":
        return (ASSETS["tpo"], "elevation", "tpo_roof") if faces == [1] else (ASSETS["roof_patch"], "elevation", "roof_perimeter_return")
    if n == "entrance_canopy_slab":
        if faces == [1]: return ASSETS["canopy_top"], "elevation", "canopy_top"
        if faces == [0]: return ASSETS["canopy_soffit"], "elevation", "canopy_soffit"
        return ASSETS["canopy_fascia"], "elevation", "canopy_fascia"
    if d == "metal_canopy": return ASSETS["canopy_fascia"], "elevation", "canopy_fascia"
    if d == "dark_metal": return (ASSETS["canopy_soffit"] if k == "canopy_post" else ASSETS["aluminum"]), "elevation", "dark_metal"
    if d == "recessed_glazing": return ASSETS["glass"], "glass", "physical_neutral_glass"
    if d == "interior_card":
        upper = int(mesh.get("level", 0)) == 1
        return ASSETS["upper_interior" if upper else "lower_interior"], "elevation", "upper_office_card" if upper else "lower_lobby_office_card"
    if d == "concrete_return": return ASSETS["plinth"], "elevation", "weathered_concrete_reveal"
    if d == "dark_recess" and k == "openwork_screen_backing": return ASSETS["openwork_backing"], "elevation", "openwork_shadow_backing"
    if d in {"joint_recess", "dark_recess"}: return ASSETS["joint"], "elevation", "joint_sealant"
    if d == "ribbed_overhead_door": return ASSETS["overhead_door"], "elevation", "opaque_overhead_door"
    if d == "safety_yellow": return ASSETS["bollard"], "elevation", "safety_yellow"
    if d == "roof_curb": return ASSETS["rooflight_curb"], "elevation", "rooflight_curb"
    if d == "rooflight_glass": return ASSETS["rooflight_glass"], "glass", "physical_rooflight_glass"
    if d in {"roof_equipment", "galvanized_metal"}: return ASSETS["service"], "elevation", "galvanized_service"
    if d == "industrial_slab": return ASSETS["plinth"], "elevation", "weathered_industrial_slab"
    if d == "tilt_up_concrete":
        if k in {"parapet_run", "adjacent_finish_endpoint_cap"} and ("parapet" in n or "pylon" in n):
            if faces == [1]: return ASSETS["coping"], "elevation", "pale_metal_coping"
            # Concrete parapet verticals remain concrete; no dark roof material.
            if side.startswith("front") or "front" in n: return ASSETS["warm_return"], "elevation", "warm_concrete_parapet"
            return ASSETS["cool_concrete"], "elevation", "cool_concrete_parapet"
        if side in {"right", "rear", "left"} or n.startswith(("right_", "rear_", "left_")):
            return ASSETS["cool_concrete"], "elevation", "cool_concrete"
        return ASSETS["warm_front"], "elevation", "warm_front_concrete"
    raise KeyError(f"unmapped domain {d!r} on {n!r}")


def _carrier(mesh: dict[str, Any], faces: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh); source, material_role, layer = _source(mesh, faces)
    side = str(mesh.get("side", "")); axis = side if side in {"front", "rear", "left", "right"} else "box_projected"
    if str(mesh["material_domain"]) == "tpo_roof" and faces == [1]: axis = "plan"
    span = max(xs)-min(xs) if axis in {"front", "rear"} else max(ys)-min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{'_'.join(map(str, faces))}_sticker", "kind": "carrier_skin",
        "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])], "source_image_path": source,
        "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs)-min(zs), .01), "face_indices": faces,
        # Only the upward TPO plane is semantically roof. Its thin
        # edge/underside construction returns use the perimeter-patch source
        # but remain crown-owned, so Blender's polygon-centre roof audit does
        # not treat a vertical edge as a roof deck.
        "material_role": material_role,
        "floor_role": ("crown" if str(mesh["material_domain"]) == "tpo_roof" and faces != [1] else _floor_role(mesh)),
        "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer, "final_surface_coverage": True,
    }
    if axis == "plan": item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    elif axis == "box_projected": item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if "concrete" in layer or layer == "weathered_industrial_slab":
        item.update(world_metric_uv_tile_m=1.5, world_metric_uv_u_offset=0.0, world_metric_uv_v_offset=0.0, roughness_override=.78)
    elif layer == "joint_sealant": item.update(world_metric_uv_tile_m=.5, roughness_override=.68)
    elif layer == "opaque_overhead_door":
        item.update(world_metric_uv_tile_m=4.0, world_metric_uv_u_offset=0.0,
                    world_metric_uv_v_offset=0.0, roughness_override=.60)
    elif layer == "tpo_roof": item.update(world_metric_uv_tile_m=4.0, roughness_override=.77)
    if material_role == "glass":
        item.update(glass_profile="reflective_curtain_wall", transparency_mode="BLENDED", surface_alpha_override=.34,
                    transmission_override=.87, roughness_override=.075, specular_ior_level_override=.55,
                    coat_weight_override=.28, emission_strength_override=0.0)
    if str(mesh["material_domain"]) == "interior_card":
        level=int(mesh.get("level",0)); bay=int(mesh.get("bay",0))
        if "front_office_ribbon_" in str(mesh["name"]): bay=int(str(mesh["name"]).split("front_office_ribbon_")[1].split("_")[0])
        side_no={"front":0,"right":1,"rear":2,"left":3}.get(side,0)
        cell=(side_no*5+bay*2+level+(7 if "entrance" in str(mesh["name"]) else 0))%8; col,row=cell%4,cell//4
        item.update(uv_u_min=col/4,uv_u_max=(col+1)/4,uv_v_min=row/2,uv_v_max=(row+1)/2,
                    atlas_cell_index=cell,emission_strength_override=.025 if level==0 else .018)
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage={(str(m["name"]),i):0 for m in geometry["meshes"] for i in range(len(m["faces"]))}
    for c in carriers:
        for i in c["face_indices"]: coverage[(str(c["surface_id"]),int(i))]+=1
    missing=[f"{n}:{i}" for (n,i),v in coverage.items() if v==0];duplicate=[f"{n}:{i}" for (n,i),v in coverage.items() if v>1]
    result={"visible_face_count":len(coverage),"owned_once_count":sum(v==1 for v in coverage.values()),"missing_faces":missing,"multiply_owned_faces":duplicate,"status":"pass" if not missing and not duplicate else "fail"}
    if result["status"]!="pass": raise ValueError(result)
    return result


def _asset_provenance() -> dict[str, Any]:
    path=TOOL_DIR/"sticker_assets/industrial_tilt_up_concrete_v98/provenance.json";provenance=json.loads(path.read_text(encoding="utf-8"))
    for record in provenance["assets"].values():
        asset=TOOL_DIR.parents[1]/record["path"]
        if hashlib.sha256(asset.read_bytes()).hexdigest()!=record["sha256"]: raise ValueError(f"asset mismatch: {asset}")
    return provenance


def _build_profile(size: str) -> tuple[dict[str, Any], dict[str, Any]]:
    provenance=_asset_provenance();geometry=build_geometry(size);carriers=[_carrier(m,g) for m in geometry["meshes"] for g in _face_groups(m)];audit=_surface_audit(geometry,carriers);profile=_base_profile()
    roles=["office_ground","office_upper","entry","high_bay","pylon","loading","rear","crown","roof","roof_equipment"]
    profile.update({"identity":f"Industrial Tilt-Up Concrete V98 Sticker LEGO - {size}","kits":[],"glass_profile":"reflective_curtain_wall",
        "massing_graph":{"schema":"massing-graph@1","profile":profile_id(size),"height_m":13.35,
        "description":"Exact-reference warm tilt-up office frontage and high-bay warehouse with loading elevation, raised blind pylon and sparse TPO roof kit.",
        "reference_dimensions":{"width_m":60.0,"depth_m":SIZES[size],"floors":2,"rear_module_m":6.0},
        "target_views":["archetype_match","street","front_corner","rear_corner","facade_close","roof_audit","aerial"],
        "nodes":[{"id":f"v98_tiltup_locked_{size}","kind":"locked_mesh_bundle","location":[0,0,0],"geometry_sha256":geometry["geometry_sha256"],"meshes":geometry["meshes"]}],
        "assemblies":carriers,"surface_audit":audit,"floor_sticker_contract":{"required":True,
        "floor_datums_m":[0.0,4.45,8.2,11.1],"roof_starts_at_z_m":11.1,"roles":roles,
        "forbid_floor_band_gaps":True,"forbid_floor_band_overlaps":True,
        "forbid_roof_below_roof_datum":True,"forbid_nonuniform_scale":True},
        "final_surface_audit":{"required":True,"status":audit["status"],"visible_face_count":audit["visible_face_count"],"owned_once_count":audit["owned_once_count"],"forbid_generic_materials":True,"required_finish_property":"final_surface_coverage"},
        "exact_image_override":{"required":True,"authority":"three exact variant_0 images","reference_sha256":REFERENCE_HASHES,"asset_provenance_schema":provenance["schema"]},"size_matrix":SIZE_MATRIX,"selected_size":size},
        "presentation":{"identity_yaw_degrees":-30.0,"street_yaw_degrees":-18.0,"street_distance_scale":1.16,"identity_distance_scale":1.1}})
    profile["dimension_overrides"]={"width_m":60.0,"depth_m":SIZES[size],"default_floors":2,"min_floors":2,"max_floors":2,"roof_height_m":2.25}
    profile["production_contract"]={"identity_mode":"massing_graph","identity_authority":"exact_image_locked_tilt_up_industrial","fixed_identity":["two-band office frontage","singular recessed entrance and supported canopy","raised blind pylon","six loading doors","sparse fixed roof kit"],"repeatable_capacity":["complete 6m rear operational depth module only"],"representation":"locked_geometry_plus_carrier_space_stickers","placement_model":"bounded_discrete_panel_lego","architect_score_target":95,"clay_lock":{"required":True,"status":f"v98_{size}_locked","geometry_sha256":geometry["geometry_sha256"]},"reference_sha256":REFERENCE_HASHES,"asset_provenance":provenance["assets"],"lego_scalability":{"matrix":SIZE_MATRIX,"selected_size":size,"whole_modules_only":True,"vertical_scaling":"forbidden","width_scaling":"forbidden","nonuniform_sticker_scale_allowed":False},"hard_stops":geometry["hard_stops"]+["missing_or_multiply_owned_visible_face","generic_material_fallback","printed_panel_joint","interior_atlas_assigned_to_glass","roof_domain_leakage"]}
    return condition_profile(profile,geometry,score_target=95)


def _write(path: Path,data: dict[str,Any])->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def main()->None:
    profiles={};packages={};registry={"schema":"siteforge.sticker-lego-family@1","archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"identity_mode":"massing_graph","tiers":[]}
    for size in SIZE_MATRIX:
        profile,package=_build_profile(size)
        if package["status"]!="pass":raise RuntimeError(package["failures"])
        profiles[profile_id(size)]=profile;packages[size]=package;registry["tiers"].append({"id":size,"signature_profile_id":profile_id(size),"family_id":family_id(size),**SIZE_MATRIX[size]})
    profiles[VARIANT_ID]=deepcopy(profiles[profile_id("canonical")])
    _write(OUTPUT,{"schema":"architectural-signatures@1","override_profiles":[],"profiles":profiles});_write(REGISTRY,registry);_write(PACKAGE,{"schema":"sticker-carrier-space-packages@1","packages":packages})
    _write(CONTRACT,{"schema":"siteforge.industrial-tilt-up-concrete-sticker-lego@1","version":"v98.1","archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"identity_authority":"three_exact_variant_0_images","reference_sha256":REFERENCE_HASHES,"size_matrix":SIZE_MATRIX,"continuous_resize_allowed":False,"vertical_scaling_allowed":False,"width_scaling_allowed":False,"whole_modules_only":True,"hard_stops":["partial rear module resize","missing fixed office entry pylon loading or roof kit","generic fallback","unowned or multiply owned face","printed panel joints","roof domain leakage"]})


if __name__=="__main__":main()
