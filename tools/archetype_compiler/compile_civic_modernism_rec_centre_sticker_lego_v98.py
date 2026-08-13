"""Compile the exact-reference Civic Modernism Rec Centre V98 Sticker LEGO family."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_civic_modernism_rec_centre_sticker_lego_v98 import (
    ARCHETYPE_ID, SIZE_MATRIX, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import condition_profile


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzz_civic_modernism_rec_centre_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "civic_modernism_rec_centre_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "civic_modernism_rec_centre_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "civic_modernism_rec_centre_sticker_lego_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/civic_modernism_rec_centre_v98"
ASSETS = {
    "brick_front": f"{ASSET_ROOT}/warm_brick_front_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/warm_brick_return_intrinsic.png",
    "brick_parapet": f"{ASSET_ROOT}/warm_brick_parapet_intrinsic.png",
    "concrete": f"{ASSET_ROOT}/cool_weathered_pale_concrete_intrinsic.png",
    "coping": f"{ASSET_ROOT}/pale_concrete_coping_intrinsic.png",
    "low_roof": f"{ASSET_ROOT}/low_roof_membrane_intrinsic.png",
    "high_roof": f"{ASSET_ROOT}/high_roof_membrane_intrinsic.png",
    "roof_patch": f"{ASSET_ROOT}/roof_perimeter_patch_intrinsic.png",
    "canopy_ribbed": f"{ASSET_ROOT}/ribbed_canopy_top_intrinsic.png",
    "canopy_smooth": f"{ASSET_ROOT}/smooth_canopy_fascia_soffit_posts_intrinsic.png",
    "aluminum": f"{ASSET_ROOT}/dark_aluminum_joinery_intrinsic.png",
    "glass": f"{ASSET_ROOT}/physical_clear_glass_intrinsic.png",
    "pool_interior": f"{ASSET_ROOT}/pool_hall_interior_atlas.png",
    "lobby_interior": f"{ASSET_ROOT}/community_lobby_interior_atlas.png",
    "entry": f"{ASSET_ROOT}/warm_entry_door_finish_intrinsic.png",
    "threshold": f"{ASSET_ROOT}/entry_threshold_intrinsic.png",
    "service": f"{ASSET_ROOT}/aged_galvanized_hvac_service_intrinsic.png",
    "grille": f"{ASSET_ROOT}/dark_service_grille_intrinsic.png",
    "skylight_glass": f"{ASSET_ROOT}/skylight_glass_intrinsic.png",
    "skylight_curb": f"{ASSET_ROOT}/skylight_curb_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0.png": "9183129653aa668116a66add2613d1241b6ebbe342895565001d6a675d90ed37",
    "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0_angle_60.jpg": "cc5c6668c724051a7eca406064ab9d70d0cf4dc79f5e0dc9d742b4e7b049340a",
    "frontend/public/archetypes/buildings/civic_modernism_rec_centre/variant_0_angle_90.jpg": "8e221717803e0c92eb731d7a448687e6dd17cd32fc43d0724d9361b600ad2889",
}


def profile_id(size: str) -> str: return f"civic-modernism-rec-centre-sticker-lego-{size}"
def family_id(size: str) -> str: return f"civic-modernism-rec-centre-v98-{size}"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(v[i]) for v in mesh["vertices"]] for i in range(3))  # type: ignore[return-value]


def _roof_group(mesh: dict[str, Any]) -> str | None:
    kind, name = str(mesh.get("carrier_kind", "")), str(mesh["name"])
    if kind == "low_roof_deck": return "low_roof"
    if kind == "high_roof_deck": return "high_roof"
    if kind == "closed_parapet_corner_cap":
        return "low_roof" if name.startswith("low_") else "high_roof"
    if kind == "roof_junction_endpoint_cap":
        return "low_roof" if name.startswith("low_") else "high_roof"
    if name.startswith("low_") and kind == "nested_roof_parapet": return "low_roof"
    if name.startswith("high_") and kind == "nested_roof_parapet": return "high_roof"
    if kind in {"rooflight_curb", "rooflight_glass", "pyramidal_rooflight_curb",
                "closed_pyramidal_rooflight_glass", "access_ladder_rail", "access_ladder_rung",
                "open_mechanical_well_wall", "closed_mechanical_well_corner_cap", "mechanical_equipment"}: return "roof_equipment"
    if kind in {"closed_roof_step_wedge", "roof_step_terminal_cap"}: return "fixed_crown"
    return None


def _floor_role(mesh: dict[str, Any]) -> str:
    roof = _roof_group(mesh)
    if roof: return roof
    name, kind, domain = str(mesh["name"]), str(mesh.get("carrier_kind", "")), str(mesh["material_domain"])
    if kind in {"canopy_top", "canopy_soffit", "canopy_fascia", "canopy_rib", "canopy_post"}: return "fixed_public_ground"
    if "entrance" in name or kind in {"paired_entry_door_leaf", "glazed_door_frame", "glazed_door_pane", "glazed_door_lobby_card"}: return "fixed_public_ground"
    if kind == "fixed_massing_seam": return "fixed_crown"
    if kind in {"localized_massing_junction_pier", "localized_massing_junction_beam", "junction_beam_outward_terminal_cap",
                "exposed_stepped_inner_gym_wall", "inner_gym_wall_coping"}: return "fixed_crown"
    if kind in {"recessed_glass", "recessed_interior_card", "physical_mullion", "deep_opening_reveal",
                "curtain_wall_exterior_terminal_cap", "opaque_envelope_field"}:
        return "fixed_double_height_hall"
    if kind in {"blind_gym_brick_infill", "exposed_concrete_grid_pier", "exposed_concrete_grid_beam"}: return "fixed_tall_hall"
    raise KeyError(f"unclassified semantic role for {name!r} ({domain!r}, {kind!r})")


def _source(mesh: dict[str, Any], face_indices: list[int]) -> tuple[str, str, str]:
    name, domain, kind = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    side = str(mesh.get("side", ""))
    if kind in {"low_roof_deck", "high_roof_deck"}:
        if face_indices == [1]:
            return ASSETS["low_roof" if kind == "low_roof_deck" else "high_roof"], "elevation", kind
        return ASSETS["coping"], "elevation", f"{kind}_pale_concrete_edge_return"
    if kind == "canopy_top" and face_indices == [1]: return ASSETS["canopy_ribbed"], "elevation", "ribbed_canopy_top"
    if domain == "warm_red_brick":
        if kind in {"open_mechanical_well_wall", "closed_mechanical_well_corner_cap"}: return ASSETS["brick_parapet"], "elevation", "mechanical_well_brick"
        if kind == "exposed_stepped_inner_gym_wall": return ASSETS["brick_parapet"], "elevation", "warm_brick"
        if kind == "closed_roof_step_wedge": return ASSETS["brick_parapet"], "elevation", "warm_brick"
        return ASSETS["brick_front" if side == "front" or name.startswith("front_") else "brick_return"], "elevation", "warm_brick"
    if domain == "pale_exposed_concrete":
        if kind in {"nested_roof_parapet", "closed_parapet_corner_cap", "roof_junction_endpoint_cap", "roof_step_terminal_cap"}:
            return ASSETS["coping"], "elevation", "pale_concrete_roof_parapet"
        return ASSETS["concrete"], "elevation", "pale_exposed_concrete"
    if domain == "recessed_glazing": return ASSETS["glass"], "glass", "physical_clear_glass"
    if domain == "interior_card":
        if "entrance" in name or kind == "glazed_door_lobby_card": return ASSETS["lobby_interior"], "elevation", "community_lobby_interior_card"
        return ASSETS["pool_interior"], "elevation", "pool_hall_interior_card"
    if domain == "silver_aluminum":
        if kind in {"rooflight_curb", "pyramidal_rooflight_curb"}: return ASSETS["skylight_curb"], "elevation", "skylight_curb"
        if kind == "paired_entry_door_leaf": return ASSETS["entry"], "elevation", "warm_entry_door"
        return ASSETS["aluminum"], "elevation", "physical_dark_aluminum_joinery"
    if domain == "white_painted_steel": return ASSETS["canopy_smooth"], "elevation", "smooth_painted_canopy"
    if domain == "rooflight_glass": return ASSETS["skylight_glass"], "glass", "physical_skylight_glass"
    if domain in {"galvanized_metal", "galvanized_mechanical"}: return ASSETS["service"], "elevation", "aged_galvanized_service"
    raise KeyError(f"unmapped rec-centre domain {domain!r} on {name!r}")


def _face_groups(mesh: dict[str, Any]) -> list[list[int]]:
    # Closed roof slabs and canopy top need different finishes on their upward
    # construction face and thin edge/underside faces. Everything else has one
    # semantic material owner across the mesh.
    if str(mesh.get("carrier_kind", "")) in {"low_roof_deck", "high_roof_deck", "canopy_top"}:
        return [[1], [0, 2, 3, 4, 5]]
    return [list(range(len(mesh["faces"])))]


def _carrier(mesh: dict[str, Any], face_indices: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh); source, material_role, layer = _source(mesh, face_indices)
    side = str(mesh.get("side", "")); axis = side if side in {"front", "rear", "left", "right"} else "box_projected"
    span = max(xs)-min(xs) if axis in {"front", "rear"} else max(ys)-min(ys)
    suffix = "_".join(map(str, face_indices))
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{suffix}_sticker", "kind": "carrier_skin", "surface_id": str(mesh["name"]),
        "target_ids": [str(mesh["name"])], "source_image_path": source, "source_id": f"v98_{layer}",
        "axis": axis, "centre": [sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs)-min(zs), .01), "face_indices": face_indices,
        "material_role": material_role, "floor_role": _floor_role(mesh), "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer, "final_surface_coverage": True,
    }
    if axis == "box_projected": item["box_bounds"] = [min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)]
    if layer in {"warm_brick", "mechanical_well_brick"}:
        item.update(world_metric_uv_tile_m=1.10, world_metric_uv_u_offset=0.0, world_metric_uv_v_offset=0.0, roughness_override=.72)
    elif "concrete" in layer:
        item.update(world_metric_uv_tile_m=1.8, roughness_override=.70)
    elif layer in {"low_roof_deck", "high_roof_deck"}:
        item.update(world_metric_uv_tile_m=4.0, roughness_override=.78)
    elif layer in {"low_roof_deck_pale_concrete_edge_return", "high_roof_deck_pale_concrete_edge_return"}:
        item.update(world_metric_uv_tile_m=1.8, roughness_override=.70)
    if material_role == "glass":
        item.update(glass_profile="reflective_curtain_wall", transparency_mode="BLENDED", surface_alpha_override=.30,
                    transmission_override=.91, roughness_override=.055, specular_ior_level_override=.54,
                    coat_weight_override=.30, emission_strength_override=0.0)
    if str(mesh["material_domain"]) == "interior_card":
        side_no={"front":0,"right":1,"rear":2,"left":3}.get(side,0); bay=int(mesh.get("bay",0))
        lobby="entrance" in str(mesh["name"]) or str(mesh.get("carrier_kind"))=="glazed_door_lobby_card"
        cell=(side_no*5+bay*3+(7 if lobby else 0))%8; col,row=cell%4,cell//4
        item.update(uv_u_min=col/4,uv_u_max=(col+1)/4,uv_v_min=row/2,uv_v_max=(row+1)/2,
                    atlas_cell_index=cell, emission_strength_override=.085 if lobby else .075)
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage={(str(m["name"]),i):0 for m in geometry["meshes"] for i in range(len(m["faces"]))}
    for carrier in carriers:
        for index in carrier["face_indices"]: coverage[(str(carrier["surface_id"]),int(index))]+=1
    missing=[f"{n}:{i}" for (n,i),v in coverage.items() if v==0]; duplicate=[f"{n}:{i}" for (n,i),v in coverage.items() if v>1]
    result={"visible_face_count":len(coverage),"owned_once_count":sum(v==1 for v in coverage.values()),
            "missing_faces":missing,"multiply_owned_faces":duplicate,"status":"pass" if not missing and not duplicate else "fail"}
    if result["status"] != "pass": raise ValueError(f"surface audit failed: {result}")
    return result


def _asset_provenance() -> dict[str, Any]:
    path=TOOL_DIR/"sticker_assets/civic_modernism_rec_centre_v98/provenance.json"
    provenance=json.loads(path.read_text(encoding="utf-8"))
    for record in provenance["assets"].values():
        asset=TOOL_DIR.parents[1]/record["path"]
        if hashlib.sha256(asset.read_bytes()).hexdigest()!=record["sha256"]: raise ValueError(f"asset provenance mismatch: {asset}")
    return provenance


def _build_profile(size: str) -> tuple[dict[str, Any], dict[str, Any]]:
    provenance=_asset_provenance(); geometry=build_geometry(size); width=float(geometry["dimensions"]["width_m"]); depth=float(geometry["dimensions"]["depth_m"])
    carriers=[_carrier(mesh,group) for mesh in geometry["meshes"] for group in _face_groups(mesh)]
    audit=_surface_audit(geometry,carriers); profile=_base_profile()
    roles=["fixed_public_ground","fixed_double_height_hall","fixed_tall_hall","fixed_crown","low_roof","high_roof","roof_equipment"]
    profile.update({
        "identity":f"Civic Modernism Rec Centre V98 Sticker LEGO - {size}","kits":[],
        "massing_graph":{"schema":"massing-graph@1","profile":profile_id(size),"height_m":13.5,
            "description":"Exact-reference stepped civic recreation centre with fixed double-height pool glazing, blind brick gym hall and exposed concrete frame.",
            "reference_dimensions":{"width_m":width,"depth_m":depth,"floors":2,"ordinary_bay_m":6.25},
            "recipe_contract":{"footprint_projection_allowance_m":1.2,"projection_owner":"fixed_entrance_canopy",
                "occupied_footprint_excludes_projection":True},
            "target_views":["archetype_match","street","front_corner","rear_corner","facade_close","roof_audit","aerial"],
            "nodes":[{"id":f"v98_rec_locked_{size}","kind":"locked_mesh_bundle","location":[0,0,0],"geometry_sha256":geometry["geometry_sha256"],"meshes":geometry["meshes"]}],
            "assemblies":carriers,"surface_audit":audit,
            "floor_sticker_contract":{"required":True,"roles":roles,"floor_datums_m":[0.0,9.0,13.5],"forbid_floor_band_gaps":True,"forbid_floor_band_overlaps":True,"forbid_nonuniform_scale":True},
            "final_surface_audit":{"required":True,"status":audit["status"],"visible_face_count":audit["visible_face_count"],"owned_once_count":audit["owned_once_count"],"forbid_generic_materials":True,"required_finish_property":"final_surface_coverage"},
            "exact_image_override":{"required":True,"authority":"three exact variant_0 images","reference_sha256":REFERENCE_HASHES,"asset_provenance_schema":provenance["schema"]},
            "size_matrix":SIZE_MATRIX,"selected_size":size},
        "presentation":{"identity_yaw_degrees":-32.0,"street_yaw_degrees":-18.0,"street_distance_scale":1.12,"identity_distance_scale":1.08},
    })
    profile["dimension_overrides"]={"width_m":width,"depth_m":depth,"default_floors":2,"min_floors":2,"max_floors":2,"roof_height_m":4.5}
    profile["production_contract"]={"identity_mode":"massing_graph","identity_authority":"exact_image_locked_stepped_rec_centre",
        "fixed_identity":["double-height pool curtain wall","separate recessed public entrance","supported ribbed canopy",
            "stepped low and high civic hall volumes","two long and one pyramidal rooflights","bounded mechanical court and access ladder"],
        "repeatable_capacity":["complete 6.25m blind gymnasium bays only"],
        "representation":"locked_geometry_plus_carrier_space_stickers","placement_model":"bounded_discrete_lego",
        "architect_score_target":95,"clay_lock":{"required":True,"status":f"v98_{size}_locked","geometry_sha256":geometry["geometry_sha256"]},
        "reference_sha256":REFERENCE_HASHES,"asset_provenance":provenance["assets"],
        "lego_scalability":{"matrix":SIZE_MATRIX,"selected_size":size,"whole_modules_only":True,"vertical_scaling":"forbidden","depth_scaling":"forbidden","nonuniform_sticker_scale_allowed":False},
        "hard_stops":list(geometry["geometry_hard_stops"])+["missing_or_multiply_owned_visible_face","generic_material_fallback","interior_atlas_assigned_to_glass","roof_domain_leakage"]}
    return condition_profile(profile,geometry,score_target=95)


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def main() -> None:
    profiles={};packages={};registry={"schema":"siteforge.sticker-lego-family@1","archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"identity_mode":"massing_graph","tiers":[]}
    for size in SIZE_MATRIX:
        profile,package=_build_profile(size)
        if package["status"]!="pass": raise RuntimeError(f"carrier conditioning failed for {size}: {package['failures']}")
        profiles[profile_id(size)]=profile;packages[size]=package
        registry["tiers"].append({"id":size,"signature_profile_id":profile_id(size),"family_id":family_id(size),**SIZE_MATRIX[size]})
    profiles[VARIANT_ID]=deepcopy(profiles[profile_id("canonical")])
    _write(OUTPUT,{"schema":"architectural-signatures@1","override_profiles":[],"profiles":profiles})
    _write(REGISTRY,registry);_write(PACKAGE,{"schema":"sticker-carrier-space-packages@1","packages":packages})
    _write(CONTRACT,{"schema":"siteforge.civic-modernism-rec-centre-sticker-lego@1","version":"v98.1","archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,
        "identity_authority":"three_exact_variant_0_images","reference_sha256":REFERENCE_HASHES,"size_matrix":SIZE_MATRIX,"continuous_resize_allowed":False,
        "vertical_scaling_allowed":False,"depth_scaling_allowed":False,"whole_bays_only":True,
        "hard_stops":["wrong stepped massing","partial bay resize","missing fixed pool or entrance kit","generic material fallback","unowned or multiply owned face","printed glass geometry","roof domain leakage"]})
    print(f"wrote {OUTPUT}")


if __name__=="__main__": main()
