"""Compile Building 9 into a face-audited Sticker Method landmark package."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_brutalist_heroic_sticker_landmark_v98 import ARCHETYPE_ID, VARIANT_ID, build_geometry
from sticker_carrier_space import SCHEMA as CARRIER_SCHEMA, mapping_method

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzzzzzzzzzzzzzz_brutalist_heroic_sticker_landmark_v98.json"
REGISTRY = TOOL_DIR / "brutalist_heroic_sticker_landmark_v98.json"
PACKAGE = TOOL_DIR / "brutalist_heroic_sticker_landmark_v98_carrier_packages.json"
CONTRACT = TOOL_DIR / "brutalist_heroic_sticker_landmark_v98_contract.json"
ASSET_ROOT = "tools/archetype_compiler/sticker_assets/brutalist_heroic_v98"
ASSETS = {
    "front_concrete": f"{ASSET_ROOT}/boardformed_concrete_front_intrinsic.png",
    "return_concrete": f"{ASSET_ROOT}/boardformed_concrete_return_intrinsic.png",
    "reveal": f"{ASSET_ROOT}/deep_concrete_reveal_intrinsic.png",
    "soffit": f"{ASSET_ROOT}/weathered_concrete_soffit_intrinsic.png",
    "coping": f"{ASSET_ROOT}/pale_concrete_coping_intrinsic.png",
    "bronze": f"{ASSET_ROOT}/dark_bronze_joinery_intrinsic.png",
    "glass": f"{ASSET_ROOT}/physical_neutral_glass_intrinsic.png",
    "ground_card": f"{ASSET_ROOT}/ground_public_interior_atlas.png",
    "upper_card": f"{ASSET_ROOT}/upper_institutional_interior_atlas.png",
    "roof": f"{ASSET_ROOT}/roof_membrane_intrinsic.png",
    "court": f"{ASSET_ROOT}/sunken_roof_court_intrinsic.png",
    "flashing": f"{ASSET_ROOT}/roof_perimeter_flashing_intrinsic.png",
    "service": f"{ASSET_ROOT}/aged_service_metal_intrinsic.png",
}
REFERENCE_HASHES = {
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0.png": "955d4d45a2148325e2529d02139192c47080210d304bbc0ad856c50b9ef2abbc",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_60.jpg": "ab69b3ddf450414c39d8fbb3c2e4886ec6748b0d02c6c2d751f000c2b456031b",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_90.jpg": "427226ea95af68f6e54c0302896ca42dd8cb42167294f0396465cec801317bd5",
}


def profile_id() -> str:
    return "brutalist-heroic-sticker-landmark-v98-canonical"


def family_id() -> str:
    return "brutalist-heroic-v98-canonical"


def _base_profile() -> dict[str, Any]:
    data = json.loads((TOOL_DIR / "architectural_signature_profiles.json").read_text(encoding="utf-8"))
    return deepcopy(data["profiles"]["industrial_brick_original_mill"])


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], list[float], list[float]]:
    return tuple([float(vertex[index]) for vertex in mesh["vertices"]] for index in range(3))  # type: ignore[return-value]


def _role(mesh: dict[str, Any]) -> str:
    name, domain, kind = str(mesh["name"]), str(mesh["material_domain"]), str(mesh.get("carrier_kind", ""))
    if domain in {"roof_membrane", "roof_court_membrane"}: return "roof"
    if domain == "service_metal" or "penthouse" in name: return "roof_equipment"
    if domain == "pale_coping" or kind in {"outer_parapet", "roof_court_wall"}: return "crown"
    if "entry" in name: return "entry"
    if "ground" in name or kind in {"piloti_stem", "flared_piloti_capital", "return_piloti"}: return "ground_public"
    if kind in {"projecting_lightbox_cheek", "projecting_lightbox_head", "splayed_lightbox_sill",
                "opaque_upper_wall_panel", "aperture_sill_wall", "aperture_head_wall"}: return "upper_monumental"
    if domain in {"physical_glass", "interior_card", "interior_backing", "dark_bronze"}: return "upper_monumental"
    if domain in {"boardformed_concrete", "deep_concrete_reveal", "weathered_concrete", "weathered_soffit"}: return "upper_monumental"
    raise KeyError(f"unclassified {name}: {domain}/{kind}")


def _face_groups(mesh: dict[str, Any]) -> list[list[int]]:
    domain = str(mesh["material_domain"])
    if domain in {"boardformed_concrete", "deep_concrete_reveal", "weathered_concrete", "weathered_soffit"} and len(mesh["faces"]) == 6:
        return [[0], [1], [2, 3, 4, 5]]
    return [list(range(len(mesh["faces"])))]


def _source(mesh: dict[str, Any], faces: list[int]) -> tuple[str, str, str]:
    name, domain, kind, side = (str(mesh["name"]), str(mesh["material_domain"]),
                                str(mesh.get("carrier_kind", "")), str(mesh.get("side", "")))
    if domain == "physical_glass": return ASSETS["glass"], "glass", "physical_neutral_glass"
    if domain == "interior_card":
        return (ASSETS["ground_card"], "elevation", "ground_public_interior") if int(mesh.get("level", 1)) == 0 else (
            ASSETS["upper_card"], "elevation", "upper_institutional_interior")
    if domain == "interior_backing": return ASSETS["upper_card"], "elevation", "opaque_interior_backing"
    if domain == "dark_bronze": return ASSETS["bronze"], "elevation", "dark_bronze_joinery"
    if domain == "deep_concrete_reveal": return ASSETS["reveal"], "elevation", "deep_boardformed_reveal"
    if domain == "weathered_soffit": return ASSETS["soffit"], "elevation", "weathered_concrete_soffit"
    if domain == "weathered_concrete": return ASSETS["soffit"], "elevation", "weathered_concrete_plinth"
    if domain == "pale_coping": return ASSETS["coping"], "elevation", "pale_concrete_coping"
    if domain == "roof_membrane": return ASSETS["roof"], "elevation", "weathered_roof_membrane"
    if domain == "roof_court_membrane": return ASSETS["court"], "elevation", "sunken_roof_court"
    if domain == "service_metal": return ASSETS["service"], "elevation", "aged_service_metal"
    if domain == "boardformed_concrete":
        source = ASSETS["front_concrete"] if side == "front" or name.startswith(("front_", "entry_")) else ASSETS["return_concrete"]
        layer = "boardformed_front_concrete" if source == ASSETS["front_concrete"] else "boardformed_return_concrete"
        return source, "elevation", layer
    raise KeyError(f"unmapped {name}: {domain}/{kind}")


def _atlas_cell(mesh: dict[str, Any]) -> int:
    """Choose separated 4x2 cells without a repeating adjacent-window walk."""
    name = str(mesh["name"])
    if int(mesh.get("level", 1)) == 0:
        return 7 if "entry" not in name else (0 if "_0_" in name else 5)
    cycle = [0, 5, 2, 7, 1, 6, 3, 4]
    side_start = {"front": 0, "right": 2, "rear": 4, "left": 5}
    start = 4 if "tower" in name else side_start.get(str(mesh.get("side", "")), 0)
    suffix = 0
    for part in reversed(name.split("_")):
        if part.isdigit():
            suffix = int(part)
            break
    return cycle[(start + suffix) % len(cycle)]


def _carrier(mesh: dict[str, Any], faces: list[int]) -> dict[str, Any]:
    xs, ys, zs = _bounds(mesh)
    source, material_role, layer = _source(mesh, faces)
    side = str(mesh.get("side", ""))
    axis = side if side in {"front", "rear", "left", "right"} else "box_projected"
    if str(mesh.get("axis", "")) == "plan" or str(mesh["material_domain"]) in {"roof_membrane", "roof_court_membrane"}:
        axis = "plan"
    span = max(xs) - min(xs) if axis in {"front", "rear"} else max(ys) - min(ys)
    item: dict[str, Any] = {
        "id": f"v98_{mesh['name']}_{'_'.join(map(str, faces))}_sticker",
        "kind": "carrier_skin",
        "surface_id": str(mesh["name"]),
        "target_ids": [str(mesh["name"])],
        "source_image_path": source,
        "source_id": f"v98_{layer}",
        "axis": axis,
        "centre": [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        "span_m": max(span, .01),
        "height_m": max(max(zs) - min(zs), .01),
        "face_indices": faces,
        "material_role": material_role,
        "floor_role": _role(mesh),
        "finish_class": f"intrinsic_{layer}",
        "sticker_layer": layer,
        "final_surface_coverage": True,
    }
    if axis == "plan": item["plan_bounds"] = [min(xs), max(xs), min(ys), max(ys)]
    elif axis == "box_projected": item["box_bounds"] = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
    if "concrete" in layer or "reveal" in layer:
        item.update(world_metric_uv_tile_m=2.0, roughness_override=.84)
    elif layer in {"weathered_roof_membrane", "sunken_roof_court"}:
        item.update(world_metric_uv_tile_m=4.0, roughness_override=.78)
    elif layer == "dark_bronze_joinery":
        item.update(world_metric_uv_tile_m=1.0, metallic_override=.72, roughness_override=.38)
    if material_role == "glass":
        item.update(glass_profile="reflective_curtain_wall", transparency_mode="BLENDED",
                    surface_alpha_override=.27, transmission_override=.92, roughness_override=.042,
                    specular_ior_level_override=.62, coat_weight_override=.38,
                    emission_strength_override=0.0)
    if str(mesh["material_domain"]) in {"interior_card", "interior_backing"}:
        cell = _atlas_cell(mesh)
        col, row = cell % 4, cell // 4
        item.update(uv_u_min=col / 4, uv_u_max=(col + 1) / 4,
                    uv_v_min=row / 2, uv_v_max=(row + 1) / 2,
                    atlas_cell_index=cell,
                    emission_strength_override=.025 if int(mesh.get("level", 1)) == 0 else .015)
        if str(mesh["material_domain"]) == "interior_backing":
            item.update(surface_alpha_override=1.0, transmission_override=0.0,
                        emission_strength_override=0.0, roughness_override=.8)
    return item


def _surface_audit(geometry: dict[str, Any], carriers: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = {(str(mesh["name"]), index): 0 for mesh in geometry["meshes"] for index in range(len(mesh["faces"]))}
    for carrier in carriers:
        for index in carrier["face_indices"]:
            coverage[(str(carrier["surface_id"]), int(index))] += 1
    missing = [f"{name}:{index}" for (name, index), count in coverage.items() if count == 0]
    duplicate = [f"{name}:{index}" for (name, index), count in coverage.items() if count > 1]
    result = {"visible_face_count": len(coverage), "owned_once_count": sum(count == 1 for count in coverage.values()),
              "missing_faces": missing, "multiply_owned_faces": duplicate,
              "status": "pass" if not missing and not duplicate else "fail"}
    if result["status"] != "pass":
        raise ValueError(result)
    return result


def _provenance() -> dict[str, Any]:
    path = TOOL_DIR / "sticker_assets/brutalist_heroic_v98/provenance.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for record in data["assets"].values():
        asset = ROOT / record["path"]
        if hashlib.sha256(asset.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(asset)
    return data


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _condition_exact(profile: dict[str, Any], geometry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fingerprint exact mesh names so penthouse children cannot be prefix-captured."""
    conditioned = deepcopy(profile)
    graph = conditioned["massing_graph"]
    named = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    records: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for assembly in graph["assemblies"]:
        carrier_targets = []
        for target in [str(value) for value in assembly["target_ids"]]:
            target_mesh = named.get(target)
            if target_mesh is None:
                failures.append({"carrier": assembly["id"], "reason": f"unresolved_exact_carrier:{target}"})
                continue
            selected = [int(value) for value in assembly["face_indices"]]
            if not selected or min(selected) < 0 or max(selected) >= len(target_mesh["faces"]):
                failures.append({"carrier": assembly["id"], "reason": f"invalid_face_selection:{target}"})
                continue
            used = sorted({vertex for index in selected for vertex in target_mesh["faces"][index]})
            payload = {"mesh": target, "vertices": [target_mesh["vertices"][index] for index in used],
                       "faces": [target_mesh["faces"][index] for index in selected],
                       "selected_face_indices": selected}
            carrier_targets.append({"kind": "locked_mesh_faces", "target": target,
                                    "selected_face_count": len(selected), "fingerprint_sha256": _digest(payload)})
        source = ROOT / assembly["source_image_path"]
        if not source.is_file():
            failures.append({"carrier": assembly["id"], "reason": f"missing_source:{source}"})
        method = mapping_method(assembly)
        if method.startswith("unsupported:"):
            failures.append({"carrier": assembly["id"], "reason": method})
        record = {"carrier_id": assembly["id"], "surface_id": assembly["surface_id"],
                  "sticker_layer": assembly["sticker_layer"], "mapping_method": method,
                  "mapping_axis": assembly["axis"], "locked_geometry_sha256": geometry["geometry_sha256"],
                  "carrier_targets": carrier_targets, "source_image_path": assembly["source_image_path"],
                  "source_image_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None,
                  "source_uv_bounds": [float(assembly.get("uv_u_min", 0)), float(assembly.get("uv_v_min", 0)),
                                       float(assembly.get("uv_u_max", 1)), float(assembly.get("uv_v_max", 1))],
                  "floor_role": assembly["floor_role"], "approval_space": "rendered_on_locked_carrier",
                  "post_generation_crop_allowed": False, "post_generation_nonuniform_scale_allowed": False}
        record["registration_sha256"] = _digest(record)
        records.append(record)
        assembly["carrier_space"] = {"schema": CARRIER_SCHEMA,
            "locked_geometry_sha256": geometry["geometry_sha256"], "mapping_method": method,
            "registration_sha256": record["registration_sha256"], "approval_space": "rendered_on_locked_carrier",
            "post_generation_crop_allowed": False, "post_generation_nonuniform_scale_allowed": False}
    package = {"schema": CARRIER_SCHEMA, "status": "pass" if not failures else "fail",
        "locked_geometry_sha256": geometry["geometry_sha256"], "carrier_count": len(records), "score_target": 95,
        "approval_space": "rendered_on_locked_carrier",
        "required_conditioning_maps": ["uv_chart", "position", "normal", "depth", "visibility", "curvature",
            "ambient_occlusion", "floor_id", "construction_role", "opening_mask", "glass_mask", "uv_distortion"],
        "hard_stops": ["carrier_geometry_hash_mismatch", "unresolved_exact_carrier", "post_generation_crop",
            "post_generation_nonuniform_scale", "source_directional_light_baked_as_surface_albedo",
            "architect_score_below_95"], "failures": failures, "carriers": records}
    package["package_sha256"] = _digest({key: value for key, value in package.items() if key != "package_sha256"})
    graph["carrier_space_contract"] = {"required": True, "schema": CARRIER_SCHEMA,
        "locked_geometry_sha256": geometry["geometry_sha256"], "package_sha256": package["package_sha256"],
        "carrier_count": len(records), "approval_space": "rendered_on_locked_carrier", "architect_score_target": 95}
    return conditioned, package


def build_profile() -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = build_geometry()
    provenance = _provenance()
    carriers = [_carrier(mesh, group) for mesh in geometry["meshes"] for group in _face_groups(mesh)]
    audit = _surface_audit(geometry, carriers)
    profile = _base_profile()
    profile.update({
        "identity": "Heroic Brutalism Exact-Image Sticker Landmark V98",
        "kits": [],
        "glass_profile": "reflective_curtain_wall",
        "massing_graph": {
            "schema": "massing-graph@1",
            "profile": profile_id(),
            "height_m": 16.51,
            "description": "Exact-image two-level Heroic Brutalist landmark with recessed glazed base, massive cantilevered shell, sculptural pilotis, light boxes, roof courts and stepped penthouses.",
            "reference_dimensions": {"width_m": 50.0, "depth_m": 42.0, "floors": 2},
            "target_views": ["archetype_match", "street", "front_corner", "rear_corner", "facade_close", "roof_audit", "aerial"],
            "nodes": [{"id": "v98_brutalist_heroic_locked", "kind": "locked_mesh_bundle",
                       "location": [0, 0, 0], "geometry_sha256": geometry["geometry_sha256"],
                       "meshes": geometry["meshes"]}],
            "assemblies": carriers,
            "surface_audit": audit,
            "floor_sticker_contract": {
                "required": True,
                "floor_datums_m": [0.0, 5.04, 12.42, 13.30],
                "roof_starts_at_z_m": 10.15,
                "roles": ["ground_public", "upper_monumental", "entry", "crown", "roof", "roof_equipment"],
                "forbid_floor_band_gaps": True,
                "forbid_floor_band_overlaps": True,
                "forbid_roof_below_roof_datum": True,
                "forbid_nonuniform_scale": True,
            },
            "final_surface_audit": {
                "required": True, "status": audit["status"],
                "visible_face_count": audit["visible_face_count"],
                "owned_once_count": audit["owned_once_count"],
                "forbid_generic_materials": True,
                "required_finish_property": "final_surface_coverage",
            },
            "exact_image_override": {
                "required": True, "authority": "three exact variant_0 images",
                "reference_sha256": REFERENCE_HASHES,
                "asset_provenance_schema": provenance["schema"],
            },
            "selected_size": "canonical",
        },
        "presentation": {"identity_yaw_degrees": -26.0, "street_yaw_degrees": -18.0,
                         "street_distance_scale": 1.12, "identity_distance_scale": 1.08},
    })
    profile["dimension_overrides"] = {"width_m": 50.0, "depth_m": 42.0,
                                      "default_floors": 2, "min_floors": 2, "max_floors": 2,
                                      "roof_height_m": 4.09}
    profile["production_contract"] = {
        "identity_mode": "massing_graph",
        "identity_authority": "exact_image_locked_heroic_brutalism",
        "fixed_identity": ["recessed public glass base", "cantilevered concrete shell", "flared pilotis",
                           "five splayed monumental light boxes", "two roof courts", "three stepped penthouses"],
        # The preflight contract requires an explicit capacity declaration.
        # For a fixed landmark that capacity is the one complete canonical
        # placement atom; it is selectable but never stretched or repeated.
        "repeatable_capacity": ["one complete 50x42 fixed-landmark placement atom"],
        "representation": "locked_geometry_plus_carrier_space_stickers",
        "placement_model": "fixed_landmark",
        "placement_contract": {"mode": "fixed_landmark", "footprint_m": {"width": 50.0, "depth": 42.0},
                               "polygon_fit": False, "repeat_count": 1, "continuous_resize_allowed": False},
        "architect_score_target": 95,
        "clay_lock": {"required": True, "status": "v98_canonical_locked",
                      "geometry_sha256": geometry["geometry_sha256"]},
        "reference_sha256": REFERENCE_HASHES,
        "asset_provenance": provenance["assets"],
        "lego_scalability": {"tiers": ["canonical"], "continuous_resize_allowed": False,
                             "vertical_scaling": "forbidden", "nonuniform_sticker_scale_allowed": False},
        "hard_stops": geometry["hard_stops"] + ["generic material fallback", "roof domain leakage"],
    }
    return _condition_exact(profile, geometry)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    profile, package = build_profile()
    if package["status"] != "pass":
        raise RuntimeError(package["failures"])
    profiles = {profile_id(): profile, VARIANT_ID: deepcopy(profile)}
    _write(OUTPUT, {"schema": "architectural-signatures@1", "override_profiles": [], "profiles": profiles})
    _write(REGISTRY, {"schema": "siteforge.sticker-lego-family@1", "archetype_id": ARCHETYPE_ID,
                      "variant_id": VARIANT_ID, "identity_mode": "massing_graph",
                      "tiers": [{"id": "canonical", "signature_profile_id": profile_id(),
                                 "family_id": family_id(), "width_m": 50.0, "depth_m": 42.0,
                                 "occupied_storeys": 2}]})
    _write(PACKAGE, {"schema": "sticker-carrier-space-packages@1", "packages": {"canonical": package}})
    _write(CONTRACT, {"schema": "siteforge.brutalist-heroic-sticker-landmark@1", "version": "v98.1",
                      "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID,
                      "identity_authority": "three_exact_variant_0_images",
                      "reference_sha256": REFERENCE_HASHES,
                      "approved_tiers": ["canonical"], "continuous_resize_allowed": False,
                      "vertical_scaling_allowed": False,
                      "hard_stops": ["wrong occupied floor count", "missing cantilever pilotis or light boxes",
                                     "missing roof courts or penthouses", "generic fallback",
                                     "unowned or multiply owned face", "roof domain leakage"]})


if __name__ == "__main__":
    main()
