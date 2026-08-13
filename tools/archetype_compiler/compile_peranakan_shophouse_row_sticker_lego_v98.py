"""Compile the exact-reference Peranakan shophouse V98 whole-unit Sticker family."""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_peranakan_shophouse_row_sticker_lego_v98 import (
    ARCHETYPE_ID, SIZES, UW, VARIANT_ID, build_geometry,
)
from sticker_carrier_space import SCHEMA as CARRIER_SCHEMA, mapping_method


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzzz_peranakan_shophouse_row_sticker_lego_v98.json"
REGISTRY = TOOL_DIR / "peranakan_shophouse_row_sticker_lego_v98.json"
PACKAGE = TOOL_DIR / "peranakan_shophouse_row_sticker_lego_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "peranakan_shophouse_row_sticker_lego_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/shophouse_peranakan_v98"
ASSET_PROVENANCE = TOOL_DIR / "sticker_assets/shophouse_peranakan_v98/provenance.json"
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/shophouse_southeast_asian/variant_0.png": "c388ea502ac3e7cca481063560fd74f17d06bdf354d48ea821d9a71a8bf17a47",
    "frontend/public/archetypes/buildings/shophouse_southeast_asian/variant_0_angle_60.jpg": "2751220f0b7511eee91ab94aa0b58cce6e6f4f4734167a4ee87480e610109d03",
    "frontend/public/archetypes/buildings/shophouse_southeast_asian/variant_0_angle_90.jpg": "df32530009a81081a8012e856b1d013f0f05ef3c00a7a4168395c1134c38c5ce",
}
EXPECTED_GEOMETRY_HASHES = {
    "canonical": "5d69760c7b41a874c1eb1f68e5e2d9b5b7d32f65c90440b124f80323632def12",
    "extended": "c26e25415557894c1c300908794582d72409ff709947d4b486dfac5f0c0c110f",
}
COLOR_DOMAIN = {
    "turquoise_plaster": "turquoise", "coral_plaster": "coral", "ochre_plaster": "ochre",
    "mint_plaster": "mint", "lavender_plaster": "lavender", "cream_plaster": "cream",
}


def profile_id(size: str) -> str:
    return f"peranakan-shophouse-row-sticker-lego-{size}"


def family_id(size: str) -> str:
    return f"peranakan-shophouse-row-v98-{size}"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _asset(role: str, provenance: dict[str, Any]) -> str:
    return str(provenance["assets"][role]["path"])


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _provenance() -> dict[str, Any]:
    provenance = json.loads(ASSET_PROVENANCE.read_text(encoding="utf-8"))
    if provenance["building"] != "shophouse_southeast_asian--shophouse_peranakan":
        raise ValueError("wrong Peranakan asset provenance")
    for ref, digest in REFERENCE_HASHES.items():
        if _sha(REPO / ref) != digest:
            raise ValueError(f"exact reference mismatch: {ref}")
    for role, record in provenance["assets"].items():
        path = REPO / record["path"]
        if _sha(path) != record["sha256"]:
            raise ValueError(f"asset mismatch for {role}: {path}")
        forbidden = ("contains_printed_openings", "contains_printed_pilasters_or_arches",
                     "contains_printed_rails_or_mullions", "contains_baked_directional_lighting",
                     "contains_printed_reflection_horizon")
        if any(record[key] for key in forbidden):
            raise ValueError(f"non-intrinsic asset forbidden: {role}")
    return provenance


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(vertex[index]) for vertex in mesh["vertices"]] for index in range(3))  # type: ignore[return-value]


def _unit_index(mesh: dict[str, Any]) -> int:
    match = re.search(r"(?:^|_)unit_(\d+)(?:_|$)", str(mesh["name"]))
    return int(match.group(1)) if match else 0


def _floor_role(mesh: dict[str, Any]) -> str:
    kind, name = str(mesh.get("carrier_kind", "")), str(mesh["name"])
    if kind in {"open_tunnel_surface", "arcade_column", "tunnel_soffit_beam", "pale_trim_endpoint_cap"}: return "fixed_arcade_cavern"
    if kind.startswith("shopfront_") or kind in {"ground_shopfront_pier", "selective_pale_shopfront_surround",
                                                  "door_carving_relief", "tile_dado", "vent_grille"}: return "fixed_ground_shop"
    if kind in {"arch_cut_wall_panel", "arch_clipped_glass", "arch_clipped_card", "arched_opening_return",
                "physical_window_mullion", "physical_shutter", "open_shutter_frame_member", "side_shutter_leaf",
                "shaped_pilaster", "shaped_capital", "relief_medallion", "tile_relief_cluster",
                "floral_motif_cluster", "faunal_motif_cluster", "continuous_fretwork_relief",
                "continuous_pendant_relief", "arch_contour_interior_backing"}: return "fixed_upper_residential"
    if kind.startswith("balcony_"): return "fixed_upper_residential"
    if kind == "relief_frieze": return "fixed_crown_fretwork"
    if kind in {"dormer_frame", "dormer_louvre"} or (kind == "closed_pitched_roof" and "dormer_cap" in name): return "main_roof_dormer"
    if kind == "closed_pitched_roof": return "service_roof" if "service_roof" in name else "main_roof"
    if kind in {"roof_profile_party_fire_wall", "slope_following_party_coping", "party_ridge_cap"}: return "party_roof_boundary"
    if kind in {"airwell_vertical_party_wall", "airwell_party_wall_cap", "air_well_wall"}: return "open_airwell"
    if kind == "rear_main_enclosure" or kind == "rear_opening_frame": return "constrained_rear"
    if kind in {"rear_service_wing", "service_rear_wall_panel", "service_rear_glass",
                "service_rear_interior_card", "service_rear_window_frame"}: return "rear_service"
    if kind == "row_end_gable_wall": return "end_return_lower_rear"
    if kind == "row_end_gable_upper_closure": return "end_return_upper_front"
    raise KeyError(f"unclassified floor role: {name} ({kind})")


def _groups(mesh: dict[str, Any]) -> list[tuple[list[int], str]]:
    kind, name = str(mesh.get("carrier_kind", "")), str(mesh["name"])
    if kind == "closed_pitched_roof":
        return [([0, 6], "roof_upface"), ([3, 9], "roof_ridge"),
                ([2, 4, 5, 8, 10, 11], "roof_eave_gable"), ([1, 7], "roof_soffit")]
    if kind == "open_tunnel_surface" and name.endswith("_tunnel_floor"):
        return [([1], "walkway_upface"), ([0, 2, 3, 4, 5], "walkway_edge")]
    if kind == "open_tunnel_surface" and name.endswith("_tunnel_soffit"):
        return [([0], "arcade_soffit"), ([1, 2, 3, 4, 5], "arcade_soffit_return")]
    return [(list(range(len(mesh["faces"]))), "whole_mesh")]


def _plaster_role(mesh: dict[str, Any], suffix: str) -> str:
    colour = COLOR_DOMAIN[str(mesh["material_domain"])]
    return f"plaster_{colour}_{suffix}"


def _source(mesh: dict[str, Any], group: str, provenance: dict[str, Any]) -> tuple[str, str, str]:
    name, domain, kind = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if group == "walkway_upface": return _asset("walkway_tile", provenance), "elevation", "five_foot_way_walkway_tile"
    if group in {"walkway_edge", "arcade_soffit", "arcade_soffit_return"}:
        return _asset("arcade_soffit_reveal", provenance), "elevation", "arcade_soffit_reveal"
    if group == "roof_upface": return _asset("terracotta_roof_field", provenance), "elevation", "terracotta_roof_field"
    if group == "roof_ridge": return _asset("terracotta_ridge_cap", provenance), "elevation", "terracotta_ridge_cap"
    if group == "roof_eave_gable": return _asset("roof_flashing", provenance), "elevation", "roof_eave_gable_flashing"
    if group == "roof_soffit": return _asset("painted_fretwork_fascia", provenance), "elevation", "painted_roof_soffit"
    if domain in COLOR_DOMAIN:
        if kind in {"rear_main_enclosure", "rear_service_wing", "service_rear_wall_panel", "air_well_wall"}: suffix = "rear"
        elif kind == "row_end_gable_wall": suffix = "return"
        elif kind == "row_end_gable_upper_closure": suffix = "front"
        else: suffix = "front"
        return _asset(_plaster_role(mesh, suffix), provenance), "elevation", f"{COLOR_DOMAIN[domain]}_plaster_{suffix}"
    if domain == "plaster_trim":
        if kind == "selective_pale_shopfront_surround":
            return _asset("pale_trim_relief", provenance), "elevation", "pale_shopfront_surround"
        if kind in {"tunnel_soffit_beam", "pale_trim_endpoint_cap"}:
            return _asset("arcade_soffit_reveal", provenance), "elevation", "pale_arcade_soffit_beam"
        if kind == "airwell_party_wall_cap": return _asset("party_wall_coping", provenance), "elevation", "party_wall_coping"
        if kind in {"slope_following_party_coping", "party_ridge_cap"}: return _asset("party_wall_coping", provenance), "elevation", "party_wall_coping"
        if kind == "balcony_slab" and int(mesh.get("unit", -1)) == 2: return _asset("balcony_plaster", provenance), "elevation", "balcony_plaster"
        if kind.startswith("balcony_"):
            colour = COLOR_DOMAIN[build_geometry("extended")["canonical_color_order"][int(mesh["unit"])]]
            return _asset(f"plaster_{colour}_front", provenance), "elevation", f"{colour}_balcony_plaster"
        return _asset("pale_trim_relief", provenance), "elevation", "pale_plaster_trim"
    if domain == "plaster_relief": return _asset("fine_ornament", provenance), "elevation", "fine_plaster_ornament"
    if domain == "peranakan_tile":
        family = int(mesh.get("unit", 0)) % 6
        return _asset(f"ceramic_dado_family_{family}", provenance), "elevation", f"peranakan_ceramic_panel_family_{family}"
    if domain in {"dark_timber", "carved_timber"}: return _asset("carved_dark_timber", provenance), "elevation", "carved_dark_timber"
    if domain == "painted_timber": return _asset("painted_fretwork_fascia", provenance), "elevation", "painted_fretwork_fascia"
    if domain == "dark_iron": return _asset("wrought_iron", provenance), "elevation", "wrought_iron"
    if domain == "recessed_glazing": return _asset("physical_clear_glass", provenance), "glass", "physical_clear_glass"
    if domain == "interior_card":
        role = "ground_shop_interiors" if kind == "shopfront_interior" else "upper_residential_interiors"
        return _asset(role, provenance), "elevation", "ground_shop_interior_card" if kind == "shopfront_interior" else "upper_residential_interior_card"
    if domain == "interior_backing":
        return _asset("upper_residential_interiors", provenance), "elevation", "upper_residential_opaque_backing"
    if domain == "party_wall_plaster": return _asset("party_wall_plaster", provenance), "elevation", "party_wall_plaster"
    if domain == "terracotta_roof": raise KeyError(f"pitched roof was not face-split: {name}")
    raise KeyError(f"unmapped domain {domain!r} on {name!r}")


def _axis(mesh: dict[str, Any], group: str) -> str:
    kind, name = str(mesh.get("carrier_kind", "")), str(mesh["name"])
    if group == "roof_upface": return "plan"
    if kind in {"arch_cut_wall_panel", "arch_clipped_glass", "arch_clipped_card", "arched_opening_return",
                "shopfront_glass", "shopfront_interior", "shopfront_perimeter_member", "shopfront_mullion",
                "door_carving_relief", "tile_dado", "shopfront_transom", "vent_grille", "arcade_column",
                "relief_frieze", "relief_medallion", "shaped_pilaster", "shaped_capital", "open_shutter_frame_member",
                "side_shutter_leaf", "physical_window_mullion", "physical_shutter", "tile_relief_cluster",
                "floral_motif_cluster", "faunal_motif_cluster", "continuous_fretwork_relief",
                "continuous_pendant_relief", "ground_shopfront_pier", "tunnel_soffit_beam",
                "pale_trim_endpoint_cap", "selective_pale_shopfront_surround", "arch_contour_interior_backing"}:
        return "front"
    if kind in {"rear_main_enclosure", "rear_service_wing", "rear_opening_frame", "service_rear_wall_panel",
                "service_rear_glass", "service_rear_interior_card", "service_rear_window_frame"}: return "rear"
    if kind in {"row_end_gable_wall", "row_end_gable_upper_closure"}:
        unit = int(mesh.get("unit", 0))
        return "left" if unit == 0 else "right"
    return "box_projected"


def _atlas_cell(mesh: dict[str, Any]) -> int:
    unit = int(mesh.get("unit", 0)); bay = int(mesh.get("bay", 0))
    match = re.search(r"_(?:window|carved_door)_(\d+)_(?:interior|card)", str(mesh["name"]))
    opening = int(match.group(1)) if match else 0
    return (unit * 5 + bay * 3 + opening * 2) % 8


def _carrier(mesh: dict[str, Any], face_indices: list[int], group: str, provenance: dict[str, Any]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh); source, material_role, layer = _source(mesh, group, provenance); axis = _axis(mesh, group)
    span = max(xs)-min(xs) if axis in {"front", "rear", "plan"} else max(ys)-min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{group}_{'_'.join(map(str, face_indices))}_sticker",
        "kind": "carrier_skin", "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)], "span_m": max(span, .01),
        "height_m": max(max(zs)-min(zs), .01), "face_indices": face_indices,
        "material_role": material_role, "floor_role": _floor_role(mesh), "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer, "semantic_group": group, "final_surface_coverage": True,
    }
    if axis == "box_projected": item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if axis == "plan":
        item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    # Constant metric texture scales are identical in canonical and extended.
    if "plaster" in layer or layer in {"pale_plaster_trim", "fine_plaster_ornament", "arcade_soffit_reveal"}:
        item.update(world_metric_uv_tile_m=1.25, roughness_override=.72)
        if layer == "fine_plaster_ornament":
            strong_kinds = {"relief_medallion", "shaped_capital", "floral_motif_cluster", "faunal_motif_cluster",
                            "continuous_fretwork_relief", "continuous_pendant_relief"}
            item.update(world_metric_uv_tile_m=.52 if str(mesh.get("carrier_kind")) in strong_kinds else .64,
                        roughness_override=.58 if str(mesh.get("carrier_kind")) in strong_kinds else .61,
                        ornament_relief_authority="physical_shaped_motif_plus_dense_intrinsic",
                        ornament_motif_semantic=str(mesh.get("motif", "continuous_frieze")),
                        physical_silhouette_authority=True)
    elif "tile" in layer or "ceramic" in layer:
        unit = _unit_index(mesh)
        item.update(world_metric_uv_tile_m=1.0, roughness_override=.42,
                    world_metric_uv_u_offset=round((unit * .173) % 1.0, 6),
                    world_metric_uv_v_offset=round((unit * .287) % 1.0, 6),
                    whole_panel_phase_index=unit % 8)
    elif "terracotta" in layer:
        item.update(world_metric_uv_tile_m=1.0, roughness_override=.66)
    elif "timber" in layer or "fretwork" in layer:
        item.update(world_metric_uv_tile_m=1.0, roughness_override=.55)
    elif "iron" in layer or "flashing" in layer:
        item.update(world_metric_uv_tile_m=.75, roughness_override=.50)
    if material_role == "glass":
        item.update(glass_profile="low_iron_clear", transparency_mode="BLENDED", surface_alpha_override=.27,
                    transmission_override=.92, roughness_override=.05, specular_ior_level_override=.48,
                    coat_weight_override=.20, emission_strength_override=0.0)
    if str(mesh["material_domain"]) == "interior_card":
        cell = _atlas_cell(mesh); col, row = cell % 4, cell // 4
        kind = str(mesh.get("carrier_kind"))
        emission = .060 if kind == "shopfront_interior" else .042 if kind == "service_rear_interior_card" else .050
        item.update(uv_u_min=col/4, uv_u_max=(col+1)/4, uv_v_min=row/2, uv_v_max=(row+1)/2,
                    atlas_cell_index=cell, emission_strength_override=emission,
                    aperture_containment_status="contained")
    if str(mesh["material_domain"]) == "interior_backing":
        cell = _atlas_cell(mesh); col, row = cell % 4, cell // 4
        item.update(uv_u_min=col/4, uv_u_max=(col+1)/4, uv_v_min=row/2, uv_v_max=(row+1)/2,
                    atlas_cell_index=cell, surface_alpha_override=1.0, transmission_override=0.0,
                    emission_strength_override=0.0, roughness_override=.78,
                    aperture_containment_status="contained", opaque_environment_backing=True,
                    backing_authority="dark_neutral_residential_atlas_opaque",
                    backing_luminance_cap=.28, diagnostic_no_environment_leak=True)
    return item


def _audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = {(str(mesh["name"]), index): 0 for mesh in geometry["meshes"] for index in range(len(mesh["faces"]))}
    for carrier in carriers:
        for index in carrier["face_indices"]: coverage[(carrier["surface_id"], int(index))] += 1
    missing = [f"{name}:{index}" for (name,index), count in coverage.items() if count == 0]
    duplicate = [f"{name}:{index}" for (name,index), count in coverage.items() if count > 1]
    if missing or duplicate: raise ValueError(f"surface audit failure missing={missing[:5]} duplicate={duplicate[:5]}")
    return {"status": "pass", "visible_face_count": len(coverage), "owned_once_count": len(coverage),
            "missing_faces": [], "multiply_owned_faces": []}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _condition_exact(profile: dict[str, Any], geometry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fingerprint exact mesh names; shared prefix matching is unsafe for party-wall children."""
    conditioned = deepcopy(profile); graph = conditioned["massing_graph"]; records = []; failures = []
    named = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}; geometry_sha = geometry["geometry_sha256"]
    for assembly in graph["assemblies"]:
        targets = [str(value) for value in assembly["target_ids"]]; carrier_targets = []
        for target in targets:
            mesh = named.get(target)
            if mesh is None:
                failures.append({"carrier": assembly["id"], "reason": f"unresolved_exact_carrier:{target}"}); continue
            selected = [int(value) for value in assembly["face_indices"]]
            if not selected or min(selected) < 0 or max(selected) >= len(mesh["faces"]):
                failures.append({"carrier": assembly["id"], "reason": f"invalid_face_selection:{target}"}); continue
            used = sorted({vertex for index in selected for vertex in mesh["faces"][index]})
            payload = {"mesh": target, "vertices": [mesh["vertices"][index] for index in used],
                       "faces": [mesh["faces"][index] for index in selected], "selected_face_indices": selected}
            carrier_targets.append({"kind": "locked_mesh_faces", "target": target,
                                    "selected_face_count": len(selected), "fingerprint_sha256": _digest(payload)})
        source = REPO / assembly["source_image_path"]
        if not source.is_file(): failures.append({"carrier": assembly["id"], "reason": f"missing_source:{source}"})
        method = mapping_method(assembly)
        if method.startswith("unsupported:"): failures.append({"carrier": assembly["id"], "reason": method})
        record = {"carrier_id": assembly["id"], "surface_id": assembly["surface_id"],
                  "sticker_layer": assembly["sticker_layer"], "mapping_method": method,
                  "mapping_axis": assembly["axis"], "locked_geometry_sha256": geometry_sha,
                  "carrier_targets": carrier_targets, "source_image_path": assembly["source_image_path"],
                  "source_image_sha256": _sha(source) if source.is_file() else None,
                  "source_uv_bounds": [float(assembly.get("uv_u_min", 0)), float(assembly.get("uv_v_min", 0)),
                                       float(assembly.get("uv_u_max", 1)), float(assembly.get("uv_v_max", 1))],
                  "floor_role": assembly["floor_role"], "approval_space": "rendered_on_locked_carrier",
                  "post_generation_crop_allowed": False, "post_generation_nonuniform_scale_allowed": False}
        record["registration_sha256"] = _digest(record); records.append(record)
        assembly["carrier_space"] = {"schema": CARRIER_SCHEMA, "locked_geometry_sha256": geometry_sha,
            "mapping_method": method, "registration_sha256": record["registration_sha256"],
            "approval_space": "rendered_on_locked_carrier", "post_generation_crop_allowed": False,
            "post_generation_nonuniform_scale_allowed": False}
    package = {"schema": CARRIER_SCHEMA, "status": "pass" if not failures else "fail",
        "locked_geometry_sha256": geometry_sha, "carrier_count": len(records), "score_target": 95,
        "approval_space": "rendered_on_locked_carrier",
        "required_conditioning_maps": ["uv_chart", "position", "normal", "depth", "visibility", "curvature",
            "ambient_occlusion", "floor_id", "construction_role", "opening_mask", "glass_mask", "uv_distortion"],
        "hard_stops": ["carrier_geometry_hash_mismatch", "unresolved_exact_carrier", "post_generation_crop",
                       "post_generation_nonuniform_scale", "source_directional_light_baked_as_surface_albedo",
                       "architect_score_below_95"], "failures": failures, "carriers": records}
    package["package_sha256"] = _digest({key:value for key,value in package.items() if key != "package_sha256"})
    graph["carrier_space_contract"] = {"required": True, "schema": CARRIER_SCHEMA,
        "locked_geometry_sha256": geometry_sha, "package_sha256": package["package_sha256"],
        "carrier_count": len(records), "approval_space": "rendered_on_locked_carrier", "architect_score_target": 95}
    return conditioned, package


def _build_profile(size: str) -> tuple[dict[str, Any], dict[str, Any]]:
    provenance = _provenance(); geometry = build_geometry(size)
    if geometry["geometry_sha256"] != EXPECTED_GEOMETRY_HASHES[size]:
        raise ValueError(f"geometry hash mismatch for {size}")
    carriers = [_carrier(mesh, indices, group, provenance) for mesh in geometry["meshes"] for indices, group in _groups(mesh)]
    audit = _audit(geometry, carriers); profile = _base_profile(); width = float(geometry["dimensions"]["width_m"])
    roles = ["fixed_arcade_cavern", "fixed_ground_shop", "fixed_upper_residential", "fixed_crown_fretwork",
             "main_roof", "main_roof_dormer", "party_roof_boundary", "open_airwell", "constrained_rear",
             "rear_service", "service_roof", "end_return"]
    profile.update({
        "identity": f"Peranakan Shophouse Row V98 Sticker LEGO - {size}", "kits": [],
        "massing_graph": {"schema": "massing-graph@1", "profile": profile_id(size), "height_m": 11.45,
            "description": "Exact-image locked two-storey attached Peranakan shophouse row with continuous five-foot-way cavern, unit roofs and fire walls.",
            "reference_dimensions": {"width_m": width, "depth_m": 28.0, "floors": 2, "whole_unit_m": UW},
            "recipe_contract": {"footprint_projection_allowance_m": 1.0, "projection_owner": "selective_fixed_balconies",
                                "occupied_footprint_excludes_projection": True},
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial"],
            "nodes": [{"id": f"v98_peranakan_locked_{size}", "kind": "locked_mesh_bundle", "location": [0,0,0],
                       "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
            "assemblies": carriers, "surface_audit": audit,
            "floor_sticker_contract": {"required": True, "roles": roles, "floor_datums_m": [0.0, 4.25, 8.25, 11.45],
                                       "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
                                       "forbid_nonuniform_scale": True},
            "five_foot_way_contract": {"required": True, "depth_m": 1.7, "continuous_across_internal_units": True,
                                       "street_open": True, "floor_soffit_reveals_and_occupied_back_required": True},
            "final_surface_audit": {"required": True, **audit, "forbid_generic_materials": True,
                                    "required_finish_property": "final_surface_coverage"},
            "exact_image_override": {"required": True, "authority": "three exact variant_0 images",
                                     "reference_sha256": REFERENCE_HASHES, "asset_provenance_schema": provenance["schema"]},
            "size_matrix": {key: {"units": count, "width_m": w, "depth_m": 28.0} for key,(count,w) in SIZES.items()},
            "selected_size": size},
        "presentation": {"identity_yaw_degrees": -32.0, "street_yaw_degrees": -14.0,
                         "street_distance_scale": 1.12, "identity_distance_scale": 1.08},
    })
    profile["dimension_overrides"] = {"width_m": width, "depth_m": 28.0, "default_floors": 2,
                                      "min_floors": 2, "max_floors": 2, "roof_height_m": 3.47}
    profile["production_contract"] = {
        "identity_mode": "massing_graph", "identity_authority": "exact_image_locked_peranakan_attached_row",
        "fixed_identity": ["continuous five-foot-way cavern", "three upper arches per unit", "selective fixed balconies",
                           "one dormer per unit", "front-to-rear party fire walls", "constrained rear airwells and service wings"],
        "repeatable_capacity": ["complete 5m x 28m two-storey attached units only"],
        "representation": "whole_attached_unit_lego", "placement_model": "bounded_discrete_lego",
        "architect_score_target": 95, "clay_lock": {"required": True, "status": f"v98_{size}_locked",
                                                     "geometry_sha256": geometry["geometry_sha256"]},
        "reference_sha256": REFERENCE_HASHES, "asset_provenance": provenance["assets"],
        "lego_scalability": {"selected_size": size, "whole_unit_m": UW, "whole_modules_only": True,
                             "vertical_scaling": "forbidden", "depth_scaling": "forbidden",
                             "continuous_width_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
        "hard_stops": list(geometry["hard_stops"]) + ["missing_or_multiply_owned_visible_face", "generic_material_fallback",
            "fake_opening_or_rail_in_intrinsic_asset", "interior_card_outside_aperture", "flat_roof_metadata_override",
            "partial_or_stretched_attached_unit", "party_wall_or_five_foot_way_discontinuity"],
    }
    return _condition_exact(profile, geometry)


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    provenance = _provenance(); profiles = {}; packages = {}
    registry = {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
                "identity_mode": "massing_graph", "representation": "whole_attached_unit_lego",
                "registered_assets": provenance["assets"], "tiers": []}
    for size, (units, width) in SIZES.items():
        profile, package = _build_profile(size)
        if package["status"] != "pass": raise RuntimeError(f"carrier conditioning failed for {size}: {package['failures']}")
        profiles[profile_id(size)] = profile; packages[size] = package
        registry["tiers"].append({"id": size, "signature_profile_id": profile_id(size), "family_id": family_id(size),
                                  "units": units, "width_m": width, "depth_m": 28.0,
                                  "geometry_sha256": EXPECTED_GEOMETRY_HASHES[size]})
    profiles[VARIANT_ID] = deepcopy(profiles[profile_id("canonical")])
    _write(OUTPUT, {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles})
    _write(REGISTRY, registry)
    _write(PACKAGE, {"schema": "sticker-carrier-space-packages@1", "packages": packages})
    _write(CONTRACT, {"schema": "siteforge.peranakan-shophouse-row-sticker-lego@1", "version": "v98.1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "identity_authority": "three_exact_variant_0_images",
        "reference_sha256": REFERENCE_HASHES, "geometry_sha256": EXPECTED_GEOMETRY_HASHES,
        "size_matrix": {key: {"units": count, "width_m": width, "depth_m": 28.0} for key,(count,width) in SIZES.items()},
        "continuous_resize_allowed": False, "vertical_scaling_allowed": False, "depth_scaling_allowed": False,
        "whole_attached_units_only": True, "unit_width_m": UW, "registered_asset_count": len(provenance["assets"]),
        "hard_stops": ["partial_attached_unit", "stretched_metric_uv", "blocked_five_foot_way", "missing_party_fire_wall",
                       "flat_roof_substitution", "generic_material_fallback", "unowned_or_multiply_owned_face",
                       "printed_opening_pilaster_arch_rail_or_mullion", "interior_card_outside_aperture"]})
    print(json.dumps({"profile": str(OUTPUT), "tiers": list(SIZES), "assets": len(provenance["assets"])}, indent=2))


if __name__ == "__main__":
    main()
