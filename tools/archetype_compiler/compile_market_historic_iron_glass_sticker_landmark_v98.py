"""Compile Building 10 into an exact-face Sticker Method landmark package."""
from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_market_historic_iron_glass_sticker_lego_v98 import ARCHETYPE_ID, VARIANT_ID, build_geometry
from sticker_carrier_space import SCHEMA as CARRIER_SCHEMA, mapping_method

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzzzzzzzzz_market_historic_iron_glass_sticker_landmark_v98.json"
REGISTRY = TOOL_DIR / "market_historic_iron_glass_sticker_landmark_v98.json"
PACKAGE = TOOL_DIR / "market_historic_iron_glass_sticker_landmark_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "market_historic_iron_glass_sticker_landmark_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/market_historic_iron_glass_v98"
ASSETS = {
    "brick_front": f"{ASSET_ROOT}/warm_brick_front_intrinsic.png",
    "brick_return": f"{ASSET_ROOT}/warm_brick_return_intrinsic.png",
    "brick_rear": f"{ASSET_ROOT}/warm_brick_rear_intrinsic.png",
    "ashlar": f"{ASSET_ROOT}/pale_ashlar_intrinsic.png",
    "plinth": f"{ASSET_ROOT}/weathered_stone_plinth_intrinsic.png",
    "iron": f"{ASSET_ROOT}/heritage_green_cast_iron_intrinsic.png",
    "ornate_iron": f"{ASSET_ROOT}/dark_ornate_rail_intrinsic.png",
    "hardware": f"{ASSET_ROOT}/aged_hardware_intrinsic.png",
    "oak": f"{ASSET_ROOT}/warm_oak_stall_intrinsic.png",
    "smooth_pale": f"{ASSET_ROOT}/pale_counter_stone_intrinsic.png",
    "paver": f"{ASSET_ROOT}/herringbone_market_paver_intrinsic.png",
    "vertical_glass": f"{ASSET_ROOT}/physical_vertical_low_iron_glass_intrinsic.png",
    "curved_glass": f"{ASSET_ROOT}/physical_curved_roof_glass_intrinsic.png",
    "lantern_glass": f"{ASSET_ROOT}/ridge_lantern_glass_intrinsic.png",
    "rooflight_glass": f"{ASSET_ROOT}/rooflight_glass_intrinsic.png",
    "ground_card": f"{ASSET_ROOT}/ground_market_interior_atlas.png",
    "gallery_card": f"{ASSET_ROOT}/gallery_market_interior_atlas.png",
    "backing": f"{ASSET_ROOT}/dark_cavern_backing_intrinsic.png",
    "slate": f"{ASSET_ROOT}/weathered_slate_intrinsic.png",
    "zinc": f"{ASSET_ROOT}/aged_zinc_roof_intrinsic.png",
    "flashing": f"{ASSET_ROOT}/flashing_coping_intrinsic.png",
    "service": f"{ASSET_ROOT}/aged_service_metal_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0.png": "0f04fa934c3b2883f82b3a27ba6883639aff8ab57a065e6b11fbe9c1afe13659",
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0_angle_60.jpg": "e504ab5a6c2af9141b0445d560a77d560d96b5e826949fec9be380f4d58d4c6a",
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0_angle_90.jpg": "af24f5150a12d417f07ae2fd5eab1c0037b984266b70ebb763fd60880dfa6be0",
}
LOCKED_GEOMETRY_SHA256 = "5b200136a81b1b6d75611072674b551ce9a9befcd28d6512f4a8000a36fa729a"
# The generic Blender roof export is about 0.78x its nominal height for this
# roof recipe.  The validator permits a 1.2 m nominal-to-exported difference.
GENERIC_ROOF_EXPORT_HEIGHT_FACTOR = 0.78
MODULE_HEIGHT_TOLERANCE_M = 1.2
LOCKED_ROOF_SURFACE_DATUM_M = 7.51


def profile_id() -> str:
    return "market-historic-iron-glass-sticker-landmark-v98-canonical"


def family_id() -> str:
    return "market-historic-iron-glass-v98-canonical"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(vertex[index]) for vertex in mesh["vertices"]] for index in range(3))  # type: ignore[return-value]


def _normal_z(mesh: dict[str, Any], face_index: int) -> float:
    face = mesh["faces"][face_index]
    a, b, c = (mesh["vertices"][face[index]] for index in range(3))
    u = [float(b[index]) - float(a[index]) for index in range(3)]
    v = [float(c[index]) - float(a[index]) for index in range(3)]
    normal = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    length = math.sqrt(sum(value * value for value in normal))
    return normal[2] / length if length else 0.0


def _face_centroid_z(mesh: dict[str, Any], face_index: int) -> float:
    face = mesh["faces"][face_index]
    return sum(float(mesh["vertices"][vertex][2]) for vertex in face) / len(face)


def _physical_sloped_face_class(mesh: dict[str, Any], face_index: int) -> str:
    """Classify roof-shell slopes by world height, independent of winding.

    The locked aisle/dormer prisms intentionally preserve their source winding,
    where the exterior upper slope has a negative normal.  Height, not normal
    sign, is therefore the stable semantic authority for upper roof versus
    lower soffit ownership.
    """
    sloped = [index for index in range(len(mesh["faces"])) if abs(_normal_z(mesh, index)) > .25]
    if face_index not in sloped:
        return "terminal"
    heights = [_face_centroid_z(mesh, index) for index in sloped]
    midpoint = (min(heights) + max(heights)) / 2
    return "up" if _face_centroid_z(mesh, face_index) > midpoint else "down"


def _role(mesh: dict[str, Any]) -> str:
    name, domain, kind = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if kind in {"ridge_lantern_glass", "ridge_lantern_frame", "ridge_lantern_frame_post",
                "ridge_lantern_sill_head_rail", "ridge_lantern_end", "ridge_lantern_cap"}:
        return "ridge_lantern"
    if kind in {"barrel_glass_panel", "barrel_ridge_end_glass_panel", "barrel_ridge_end_rail",
                "eave_clerestory_glass", "eave_clerestory_rail",
                "closed_aisle_roof_panel", "rooflight_glass", "rooflight_curb",
                "zinc_roof_dormer", "zinc_roof_dormer_wall"}:
        return "roof"
    if name.startswith("rear_") or kind in {"constrained_rear_wall", "rear_gable_arch_ring",
                                             "rear_gable_glass", "rear_gable_mullion",
                                             "rear_gable_horizontal_rail", "rear_service_door"}:
        return "rear_service"
    if kind in {"gallery_deck", "gallery_soffit", "gallery_edge_girder", "gallery_rail_top",
                "gallery_rail_mid", "gallery_rail_post", "gallery_upper_iron_post",
                "front_gallery_filigree_rail", "front_gallery_filigree", "front_gallery_filigree_rosette",
                "gallery_bay_warm_backplane", "gallery_bay_counter_front"}:
        return "mezzanine_gallery"
    if kind in {"barrel_truss_rib", "barrel_longitudinal_rail", "iron_cross_tie", "front_gable_arch_ring",
                "front_gable_glass", "front_gable_mullion", "front_gable_horizontal_rail",
                "front_iron_lattice_girder", "iron_lattice_diagonal"}:
        return "high_hall"
    if kind in {"side_brick_pier", "aperture_sill_wall", "aperture_head_wall", "arch_spandrel_wall",
                "physical_arch_ring", "arch_jamb_return", "arch_sill_return", "recessed_arch_glass",
                "recessed_interior_card", "opaque_interior_backing", "stone_end_quoin", "side_wall_coping"}:
        return "flank_masonry"
    if kind in {"open_market_floor", "occupied_front_side_bay", "front_timber_stall", "front_stall_door",
                "recessed_shop_back_wall", "recessed_shopfront_joinery", "recessed_shopfront_glass",
                "recessed_shopfront_card", "recessed_shopfront_backing", "recessed_shop_counter",
                "recessed_shop_bay_side_cue", "recessed_shop_bay_ceiling_cue",
                "historic_curved_knee_brace", "historic_capital_rosette",
                "historic_shaped_spandrel", "historic_brace_terminal_connector",
                "front_iron_half_gable", "front_side_fan_glass", "front_principal_column",
                "front_principal_capital", "front_terminal_stone_pier", "cast_iron_column_base",
                "cast_iron_column_shaft", "cast_iron_column_capital"}:
        return "ground_public"
    raise KeyError(f"unclassified {name}: {domain}/{kind}")


def _face_groups(mesh: dict[str, Any]) -> list[list[int]]:
    kind = str(mesh.get("carrier_kind", ""))
    if kind in {"closed_aisle_roof_panel", "zinc_roof_dormer"}:
        up, down, terminal = [], [], []
        for index in range(len(mesh["faces"])):
            classification = _physical_sloped_face_class(mesh, index)
            (up if classification == "up" else down if classification == "down" else terminal).append(index)
        return [group for group in (up, down, terminal) if group]
    if kind in {"ridge_lantern_cap", "open_market_floor", "gallery_deck"}:
        up, down, terminal = [], [], []
        for index in range(len(mesh["faces"])):
            nz = _normal_z(mesh, index)
            (up if nz > .25 else down if nz < -.25 else terminal).append(index)
        return [group for group in (up, down, terminal) if group]
    return [list(range(len(mesh["faces"])))]


def _group_class(mesh: dict[str, Any], faces: list[int]) -> str:
    if str(mesh.get("carrier_kind", "")) in {"closed_aisle_roof_panel", "zinc_roof_dormer"}:
        classes = {_physical_sloped_face_class(mesh, index) for index in faces}
        return classes.pop() if len(classes) == 1 else "terminal"
    values = [_normal_z(mesh, index) for index in faces]
    if values and min(values) > .25: return "up"
    if values and max(values) < -.25: return "down"
    return "terminal"


def _source(mesh: dict[str, Any], faces: list[int]) -> tuple[str, str, str]:
    name, domain, kind, side = (str(mesh["name"]), str(mesh["material_domain"]),
                                str(mesh.get("carrier_kind", "")), str(mesh.get("side", "")))
    group = _group_class(mesh, faces)
    if domain == "physical_glass":
        if kind in {"barrel_glass_panel", "barrel_ridge_end_glass_panel"}:
            return ASSETS["curved_glass"], "glass", "curved_barrel_low_iron_glass"
        if kind == "ridge_lantern_glass": return ASSETS["lantern_glass"], "glass", "ridge_lantern_glass"
        if kind == "rooflight_glass": return ASSETS["rooflight_glass"], "glass", "rooflight_low_iron_glass"
        return ASSETS["vertical_glass"], "glass", "vertical_low_iron_glass"
    if domain == "interior_card":
        source = ASSETS["gallery_card"] if "gallery" in name else ASSETS["ground_card"]
        layer = "gallery_market_interior" if source == ASSETS["gallery_card"] else "ground_market_interior"
        return source, "elevation", layer
    if kind == "gallery_bay_warm_backplane":
        return ASSETS["gallery_card"], "elevation", "gallery_market_interior"
    if domain == "interior_backing": return ASSETS["backing"], "elevation", "dark_cavern_backing"
    if domain == "red_brick":
        if side == "rear" or name.startswith("rear_"): return ASSETS["brick_rear"], "elevation", "warm_rear_brick"
        return ASSETS["brick_return"], "elevation", "warm_return_brick"
    if domain == "pale_stone":
        if kind in {"arch_sill_return"} or "sill" in name: return ASSETS["plinth"], "elevation", "weathered_stone_plinth"
        return ASSETS["ashlar"], "elevation", "pale_ashlar"
    if domain == "warm_plaster": return ASSETS["smooth_pale"], "elevation", "warm_smooth_frontage"
    if domain in {"timber_stall", "timber_door", "timber_gallery"}:
        return ASSETS["oak"], "elevation", "warm_oak_market_joinery"
    if domain == "painted_soffit": return ASSETS["smooth_pale"], "elevation", "pale_gallery_soffit"
    if domain == "dark_bronze": return ASSETS["hardware"], "elevation", "aged_service_hardware"
    if domain == "brick_floor":
        return (ASSETS["paver"], "plan", "herringbone_market_paver") if group == "up" else (
            ASSETS["plinth"], "elevation", "weathered_floor_edge")
    if domain == "painted_iron":
        if kind == "rooflight_curb": return ASSETS["flashing"], "elevation", "rooflight_flashing"
        if kind in {"iron_lattice_diagonal", "front_iron_lattice_girder", "gallery_rail_post",
                    "gallery_rail_top", "gallery_rail_mid", "front_gallery_filigree_rail",
                    "front_gallery_filigree", "front_gallery_filigree_rosette",
                    "historic_capital_rosette", "historic_shaped_spandrel"}:
            return ASSETS["ornate_iron"], "elevation", "dark_ornate_cast_iron"
        return ASSETS["iron"], "elevation", "heritage_green_cast_iron"
    if domain in {"slate_roof", "standing_seam_zinc"}:
        if group == "down": return ASSETS["smooth_pale"], "elevation", "pale_roof_soffit"
        if group == "terminal" or kind == "zinc_roof_dormer_wall":
            return ASSETS["flashing"], "elevation", "aged_roof_flashing_coping"
        if domain == "slate_roof": return ASSETS["slate"], "plan", "weathered_slate_roof"
        return ASSETS["zinc"], "plan", "aged_standing_seam_zinc"
    raise KeyError(f"unmapped {name}: {domain}/{kind}")


def _atlas_cell(mesh: dict[str, Any]) -> int:
    cycle = [0, 5, 2, 7, 1, 6, 3, 4]
    name = str(mesh["name"])
    number = next((int(part) for part in reversed(name.split("_")) if part.isdigit()), 0)
    # Each side is an independent seven-bay sequence. Reuse the same
    # nonadjacent walk rather than wrapping the eight-cell walk mid-side.
    return cycle[number % len(cycle)]


def _carrier(mesh: dict[str, Any], faces: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh)
    source, material_role, layer = _source(mesh, faces)
    side, kind, domain = str(mesh.get("side", "")), str(mesh.get("carrier_kind", "")), str(mesh["material_domain"])
    axis = side if side in {"front", "rear", "left", "right"} else "box_projected"
    if str(mesh["name"]).startswith("front_"): axis = "front"
    elif str(mesh["name"]).startswith("rear_"): axis = "rear"
    if material_role == "plan": axis = "plan"
    if kind == "barrel_glass_panel": axis = "box_projected"
    span = max(xs) - min(xs) if axis in {"front", "rear"} else max(ys) - min(ys)
    floor_role = _role(mesh)
    if kind in {"closed_aisle_roof_panel", "zinc_roof_dormer"} and _group_class(mesh, faces) != "up":
        floor_role = "crown"
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{'_'.join(map(str, faces))}_sticker",
        "kind": "carrier_skin", "surface_id": str(mesh["name"]), "target_ids": [str(mesh["name"])],
        "source_image_path": source, "source_id": f"v98_{layer}", "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, .01), "height_m": max(max(zs) - min(zs), .01), "face_indices": faces,
        "material_role": "glass" if material_role == "glass" else "elevation",
        "floor_role": floor_role, "finish_class": f"intrinsic_{layer}", "sticker_layer": layer,
        "final_surface_coverage": True,
    }
    if axis == "plan": item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    elif axis == "box_projected": item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if "brick" in layer: item.update(world_metric_uv_tile_m=2.4, roughness_override=.8)
    elif layer == "herringbone_market_paver": item.update(world_metric_uv_tile_m=1.2, roughness_override=.72)
    elif layer == "weathered_slate_roof": item.update(world_metric_uv_tile_m=1.8, roughness_override=.74)
    elif layer == "aged_standing_seam_zinc": item.update(world_metric_uv_tile_m=2.4, metallic_override=.72, roughness_override=.43)
    elif "iron" in layer: item.update(world_metric_uv_tile_m=.8, metallic_override=.58, roughness_override=.5)
    elif layer == "aged_roof_flashing_coping":
        item.update(world_metric_uv_tile_m=1.0, metallic_override=.42, roughness_override=.58)
    elif layer == "rooflight_flashing":
        item.update(world_metric_uv_tile_m=1.0, metallic_override=.54, roughness_override=.5)
    elif layer == "aged_service_hardware":
        item.update(world_metric_uv_tile_m=1.0, metallic_override=.72, roughness_override=.4)
    elif layer == "warm_oak_market_joinery": item.update(world_metric_uv_tile_m=1.2, roughness_override=.56)
    if material_role == "glass":
        roof_glass = kind in {"barrel_glass_panel", "barrel_ridge_end_glass_panel", "rooflight_glass", "ridge_lantern_glass"}
        historic_high_glass = roof_glass or kind in {
            "front_side_fan_glass", "front_gable_glass", "rear_gable_glass", "eave_clerestory_glass",
        }
        item.update(glass_profile="low_iron_clear", transparency_mode="BLENDED",
                    surface_alpha_override=.36 if historic_high_glass else .31,
                    transmission_override=.90 if roof_glass else .89,
                    roughness_override=.065 if historic_high_glass else .055,
                    specular_ior_level_override=.57 if historic_high_glass else .58,
                    coat_weight_override=.24 if historic_high_glass else .30,
                    emission_strength_override=0.0)
    if domain == "interior_card" or kind == "gallery_bay_warm_backplane":
        cell = _atlas_cell(mesh); col, row = cell % 4, cell // 4
        if kind == "gallery_bay_warm_backplane":
            emission = .30 + .03 * (cell % 4)
        elif kind == "recessed_shopfront_card":
            emission = .28 + .02 * (cell % 4)
        elif source == ASSETS["ground_card"]:
            emission = .09
        else:
            emission = .075
        item.update(uv_u_min=col / 4, uv_u_max=(col + 1) / 4, uv_v_min=row / 2, uv_v_max=(row + 1) / 2,
                    atlas_cell_index=cell, atlas_columns=4, atlas_rows=2,
                    emission_strength_override=emission)
    if kind in {"gallery_bay_counter_front", "recessed_shop_counter"}:
        item["emission_strength_override"] = .10
    if domain == "interior_backing":
        item.update(surface_alpha_override=1.0, transmission_override=0.0, emission_strength_override=0.0,
                    roughness_override=.86)
    if kind in {"barrel_glass_panel", "barrel_ridge_end_glass_panel"}:
        strip = int(mesh["strip"]) if kind == "barrel_glass_panel" else 15 + int(mesh["strip"])
        count = 36
        item.update(curved_mapping_semantics="barrel_arc_length_by_locked_strip", barrel_strip_index=strip,
                    barrel_strip_count=count, barrel_arc_u_min=strip / count, barrel_arc_u_max=(strip + 1) / count)
        if kind == "barrel_ridge_end_glass_panel": item["barrel_end"] = str(mesh["end"])
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = {(str(mesh["name"]), index): 0 for mesh in geometry["meshes"] for index in range(len(mesh["faces"]))}
    for carrier in carriers:
        for index in carrier["face_indices"]: coverage[(str(carrier["surface_id"]), int(index))] += 1
    missing = [f"{name}:{index}" for (name, index), count in coverage.items() if count == 0]
    duplicate = [f"{name}:{index}" for (name, index), count in coverage.items() if count > 1]
    result = {"visible_face_count": len(coverage), "owned_once_count": sum(count == 1 for count in coverage.values()),
              "missing_faces": missing, "multiply_owned_faces": duplicate,
              "status": "pass" if not missing and not duplicate else "fail"}
    if result["status"] != "pass": raise ValueError(result)
    return result


def _provenance() -> dict[str, Any]:
    path = TOOL_DIR / "sticker_assets/market_historic_iron_glass_v98/provenance.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for record in data["assets"].values():
        asset = ROOT / record["path"]
        if hashlib.sha256(asset.read_bytes()).hexdigest() != record["sha256"]: raise ValueError(asset)
    return data


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _condition_exact(profile: dict[str, Any], geometry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    conditioned = deepcopy(profile); graph = conditioned["massing_graph"]
    named = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    records: list[dict[str, Any]] = []; failures: list[dict[str, str]] = []
    for assembly in graph["assemblies"]:
        target = str(assembly["target_ids"][0]); target_mesh = named.get(target); targets = []
        if target_mesh is None: failures.append({"carrier": assembly["id"], "reason": f"unresolved_exact_carrier:{target}"})
        else:
            selected = [int(value) for value in assembly["face_indices"]]
            if not selected or min(selected) < 0 or max(selected) >= len(target_mesh["faces"]):
                failures.append({"carrier": assembly["id"], "reason": f"invalid_face_selection:{target}"})
            else:
                used = sorted({vertex for index in selected for vertex in target_mesh["faces"][index]})
                payload = {"mesh": target, "vertices": [target_mesh["vertices"][index] for index in used],
                           "faces": [target_mesh["faces"][index] for index in selected], "selected_face_indices": selected}
                targets.append({"kind": "locked_mesh_faces", "target": target, "selected_face_count": len(selected),
                                "fingerprint_sha256": _digest(payload)})
        source = ROOT / assembly["source_image_path"]; method = mapping_method(assembly)
        if not source.is_file(): failures.append({"carrier": assembly["id"], "reason": f"missing_source:{source}"})
        if method.startswith("unsupported:"): failures.append({"carrier": assembly["id"], "reason": method})
        record = {"carrier_id": assembly["id"], "surface_id": assembly["surface_id"],
                  "sticker_layer": assembly["sticker_layer"], "mapping_method": method,
                  "mapping_axis": assembly["axis"], "locked_geometry_sha256": geometry["geometry_sha256"],
                  "carrier_targets": targets, "source_image_path": assembly["source_image_path"],
                  "source_image_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None,
                  "source_uv_bounds": [float(assembly.get("uv_u_min", 0)), float(assembly.get("uv_v_min", 0)),
                                       float(assembly.get("uv_u_max", 1)), float(assembly.get("uv_v_max", 1))],
                  "floor_role": assembly["floor_role"], "approval_space": "rendered_on_locked_carrier",
                  "post_generation_crop_allowed": False, "post_generation_nonuniform_scale_allowed": False}
        record["registration_sha256"] = _digest(record); records.append(record)
        assembly["carrier_space"] = {"schema": CARRIER_SCHEMA, "locked_geometry_sha256": geometry["geometry_sha256"],
            "mapping_method": method, "registration_sha256": record["registration_sha256"],
            "approval_space": "rendered_on_locked_carrier", "post_generation_crop_allowed": False,
            "post_generation_nonuniform_scale_allowed": False}
    package = {"schema": CARRIER_SCHEMA, "status": "pass" if not failures else "fail",
        "locked_geometry_sha256": geometry["geometry_sha256"], "carrier_count": len(records), "score_target": 95,
        "approval_space": "rendered_on_locked_carrier", "required_conditioning_maps": ["uv_chart", "position", "normal",
            "depth", "visibility", "curvature", "ambient_occlusion", "floor_id", "construction_role", "opening_mask",
            "glass_mask", "uv_distortion"], "hard_stops": ["carrier_geometry_hash_mismatch", "unresolved_exact_carrier",
            "post_generation_crop", "post_generation_nonuniform_scale", "source_directional_light_baked_as_surface_albedo",
            "architect_score_below_95"], "failures": failures, "carriers": records}
    package["package_sha256"] = _digest({key: value for key, value in package.items() if key != "package_sha256"})
    graph["carrier_space_contract"] = {"required": True, "schema": CARRIER_SCHEMA,
        "locked_geometry_sha256": geometry["geometry_sha256"], "package_sha256": package["package_sha256"],
        "carrier_count": len(records), "approval_space": "rendered_on_locked_carrier", "architect_score_target": 95}
    return conditioned, package


def build_profile() -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = build_geometry()
    if geometry["geometry_sha256"] != LOCKED_GEOMETRY_SHA256:
        raise ValueError(f"geometry lock mismatch: {geometry['geometry_sha256']}")
    provenance = _provenance()
    carriers = [_carrier(mesh, group) for mesh in geometry["meshes"] for group in _face_groups(mesh)]
    audit = _surface_audit(geometry, carriers)
    profile = _base_profile()
    profile.update({
        "identity": "Historic Iron-and-Glass Market Hall Exact-Image Sticker Landmark V98", "kits": [],
        "glass_profile": "low_iron_clear",
        "massing_graph": {"schema": "massing-graph@1", "profile": profile_id(), "height_m": 16.72,
            "description": "Exact-image 45 x 60 metre market landmark: open central nave, two side mezzanines, physical cast-iron frame, arched masonry flanks, closed barrel glazing, asymmetric slate/zinc aisles and ridge lantern.",
            "reference_dimensions": {"width_m": 45.0, "depth_m": 60.0, "floors": 2,
                                     "occupied_hall_levels": 1, "partial_mezzanines": 2},
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial"],
            "nodes": [{"id": "v98_market_hall_locked", "kind": "locked_mesh_bundle", "location": [0, 0, 0],
                       "geometry_sha256": geometry["geometry_sha256"], "meshes": geometry["meshes"]}],
            "assemblies": carriers, "surface_audit": audit,
            "floor_sticker_contract": {"required": True, "floor_datums_m": [0.0, 1.4, 5.5, 7.25, 14.85, 16.72],
                "roof_starts_at_z_m": LOCKED_ROOF_SURFACE_DATUM_M,
                "roles": ["ground_public", "mezzanine_gallery", "high_hall", "flank_masonry", "crown", "roof", "ridge_lantern", "rear_service"],
                "forbid_floor_band_gaps": True, "forbid_floor_band_overlaps": True,
                "forbid_roof_below_roof_datum": True, "forbid_nonuniform_scale": True},
            "final_surface_audit": {"required": True, "status": audit["status"],
                "visible_face_count": audit["visible_face_count"], "owned_once_count": audit["owned_once_count"],
                "forbid_generic_materials": True, "required_finish_property": "final_surface_coverage"},
            "exact_image_override": {"required": True, "authority": "three exact variant_0 images",
                "reference_sha256": REFERENCE_HASHES, "asset_provenance_schema": provenance["schema"]},
            "curved_roof_registration": {"method": "locked_equal_arc_strips", "strip_count": 30,
                "arc_interval": [0.0, 1.0], "post_generation_nonuniform_scale_allowed": False},
            "selected_size": "canonical"},
        "presentation": {"identity_yaw_degrees": -24.0, "street_yaw_degrees": -18.0,
                         "street_distance_scale": 1.10, "identity_distance_scale": 1.06},
    })
    # This is the generic module-export nominal height.  It is intentionally
    # separate from the locked 16.72 m landmark crown in the massing graph.
    profile["dimension_overrides"] = {"width_m": 45.0, "depth_m": 60.0, "default_floors": 2,
        "min_floors": 2, "max_floors": 2, "roof_height_m": 4.8}
    profile["production_contract"] = {
        "identity_mode": "massing_graph", "identity_authority": "exact_image_locked_historic_iron_glass_market",
        "fixed_identity": ["open central nave", "two fixed side mezzanines", "physical cast-iron frame",
                           "fourteen side arches", "closed barrel-glass roof", "asymmetric slate and zinc aisles",
                           "ridge lantern", "enclosed frontage side bays", "glazed rear gable"],
        "repeatable_capacity": ["one complete 45x60 fixed-landmark placement atom"],
        "representation": "locked_geometry_plus_carrier_space_stickers", "placement_model": "fixed_landmark",
        "placement_contract": {"mode": "fixed_landmark", "footprint_m": {"width": 45.0, "depth": 60.0},
                               "polygon_fit": False, "repeat_count": 1, "continuous_resize_allowed": False},
        "architect_score_target": 95, "clay_lock": {"required": True, "status": "v98_canonical_locked",
            "geometry_sha256": geometry["geometry_sha256"]}, "reference_sha256": REFERENCE_HASHES,
        "asset_provenance": provenance["assets"],
        "lego_scalability": {"tiers": ["canonical"], "continuous_resize_allowed": False,
                             "vertical_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
        "hard_stops": geometry["hard_stops"] + ["generic material fallback", "roof domain leakage",
            "card closes open public nave", "barrel arc strip gap or overlap"]}
    return _condition_exact(profile, geometry)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    profile, package = build_profile()
    if package["status"] != "pass": raise RuntimeError(package["failures"])
    profiles = {profile_id(): profile, VARIANT_ID: deepcopy(profile)}
    _write(OUTPUT, {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles})
    _write(REGISTRY, {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID,
        "variant_id": VARIANT_ID, "identity_mode": "massing_graph", "tiers": [{"id": "canonical",
            "signature_profile_id": profile_id(), "family_id": family_id(), "width_m": 45.0, "depth_m": 60.0,
            "occupied_storeys": 2}]})
    _write(PACKAGE, {"schema": "sticker-carrier-space-packages@1", "packages": {"canonical": package}})
    _write(CONTRACT, {"schema": "siteforge.market-historic-iron-glass-sticker-landmark@1", "version": "v98.1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
        "identity_authority": "three_exact_variant_0_images", "reference_sha256": REFERENCE_HASHES,
        "approved_tiers": ["canonical"], "canonical_footprint_m": {"width": 45.0, "depth": 60.0},
        "continuous_resize_allowed": False, "vertical_scaling_allowed": False,
        "hard_stops": ["wrong fixed footprint", "closed or missing open public nave", "missing physical iron frame",
            "missing barrel glass, asymmetric aisle roofs or ridge lantern", "generic fallback",
            "unowned or multiply owned face", "roof domain leakage"]})


if __name__ == "__main__": main()
