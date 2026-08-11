"""Compile the Belle Epoque Grand Magasin V92 clay-and-sticker pilot."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_belle_epoque_clay_v92 import build_geometry, build_lock
from belle_epoque_sticker_v92 import build_registration


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
VARIANT = "grand-magasin-belle-epoque"
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zz_belle_epoque_clay_sticker_v92.json"
REGISTRY = TOOL_DIR / "belle_epoque_clay_sticker_v92.json"
CONTRACT = TOOL_DIR / "belle_epoque_sticker_v92_contract.json"
BASE_PROFILE = TOOL_DIR / "architectural_signature_profiles.d/three_all_surface_stickers_v91.json"
CLAY_OUTPUT = REPO / "artifacts/belle-epoque-clay-v92"
PREPARED_ASSETS = TOOL_DIR / "sticker_assets/belle_epoque_v92"


def carrier(
    surface_id: str,
    target_ids: list[str],
    source: str,
    axis: str,
    *,
    centre: list[float],
    span_m: float,
    height_m: float,
    normal_xy: list[float] | None = None,
    normal_z_min: float = -1.01,
    normal_z_max: float = 1.01,
    material_role: str = "elevation",
    **extra: Any,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": f"v92_skin_{surface_id}",
        "kind": "carrier_skin",
        "surface_id": surface_id,
        "target_ids": target_ids,
        "source_image_path": source,
        "axis": axis,
        "centre": centre,
        "span_m": span_m,
        "height_m": height_m,
        "normal_z_min": normal_z_min,
        "normal_z_max": normal_z_max,
        "material_role": material_role,
    }
    if normal_xy is not None:
        item["normal_xy"] = normal_xy
        item["normal_dot_min"] = 0.90
    item.update(extra)
    return item


def render_carriers(lock: dict[str, Any], registration: dict[str, Any]) -> list[dict[str, Any]]:
    """Translate the Sticker Agent's semantic registration into Blender bindings."""
    surfaces = {item["surface_id"]: item for item in lock["surfaces"]}
    axis_for_role = {
        "front": ("front", [0, -1]), "upper_front_setback": ("front", [0, -1]),
        "right": ("right", [1, 0]), "upper_right_setback": ("right", [1, 0]),
        "rear": ("rear", [0, 1]), "upper_rear_setback": ("rear", [0, 1]),
        "left": ("left", [-1, 0]), "upper_left_setback": ("left", [-1, 0]),
        "court_front": ("rear", [0, 1]), "court_right": ("left", [-1, 0]),
        "court_rear": ("front", [0, -1]), "court_left": ("right", [1, 0]),
        "dormer_front_geometry": ("front", [0, -1]),
        "dormer_right_geometry": ("right", [1, 0]),
        "dormer_rear_geometry": ("rear", [0, 1]),
        "dormer_left_geometry": ("left", [-1, 0]),
    }
    roof_angles = {
        "roof_mansard_front": [225.0, 315.0], "roof_mansard_right": [315.0, 45.0],
        "roof_mansard_rear": [45.0, 135.0], "roof_mansard_left": [135.0, 225.0],
        "roof_terrace_front": [225.0, 315.0], "roof_terrace_right": [315.0, 45.0],
        "roof_terrace_rear": [45.0, 135.0], "roof_terrace_left": [135.0, 225.0],
    }
    target_aliases = {
        "corner_pavilion_facet_assembly": ["corner_pavilion_facet"],
        "corner_pavilion_cornice_assembly": ["corner_pavilion_mid_cornice", "corner_pavilion_crown_cornice"],
        "central_dome_cap_finial_assembly": ["central_dome_cap", "central_dome_finial"],
        "corner_cupola_cap_finial_assembly": ["corner_cupola_cap", "corner_cupola_finial"],
        "dormer_front_assembly": ["dormer_front"],
        "dormer_rear_assembly": ["dormer_rear"],
        "dormer_left_assembly": ["dormer_left"],
        "dormer_right_assembly": ["dormer_right"],
    }

    output: list[dict[str, Any]] = []
    roof_wrap_added = False
    for registered in registration["assemblies"]:
        surface_id = str(registered["carrier_surface_id"])
        surface = surfaces[surface_id]
        role = str(registered["surface_role"])
        source = str(registered["source_path"])
        prepared_by_surface = {
            "facade_front": PREPARED_ASSETS / "front_seam_matched.jpg",
            "facade_left": PREPARED_ASSETS / "left_seam_matched.jpg",
            "corner_pavilion": PREPARED_ASSETS / "corner_seam_matched.jpg",
            "central_dome": PREPARED_ASSETS / "central_dome_polar.jpg",
            "corner_dome": PREPARED_ASSETS / "corner_dome_polar.jpg",
        }
        if surface_id in prepared_by_surface:
            source = prepared_by_surface[surface_id].relative_to(REPO).as_posix()
        points = surface["boundary_m"]
        xs, ys, zs = zip(*points)
        centre = [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2]
        height = max(max(zs) - min(zs), 0.05)
        span = max(max(xs) - min(xs), max(ys) - min(ys), 0.05)
        targets = target_aliases.get(str(registered["carrier_mesh"]), [str(registered["carrier_mesh"])])

        # The perimeter cornice is one semantic seam owner but four differently
        # oriented Blender carriers.  Register each outward face independently.
        if role == "projecting_perimeter_cornice":
            output.append(carrier(
                surface_id,
                ["front_main_cornice", "front_crown_return", "right_main_cornice", "right_crown_return",
                 "rear_main_cornice", "rear_crown_return", "left_main_cornice", "left_crown_return"],
                (PREPARED_ASSETS / "cornice_zinc.jpg").relative_to(REPO).as_posix(), "plan",
                centre=centre, span_m=36.0, height_m=height,
                normal_z_min=-1.01, normal_z_max=1.01, material_role="roof",
                plan_bounds=[-18.0, 18.0, -17.0, 17.0],
            ))
            continue

        if role == "closed_upper_corner_returns":
            for suffix, axis, normal, target in (
                ("front", "front", [0, -1], "corner_upper_front_return"),
                ("left", "left", [-1, 0], "corner_upper_left_return"),
            ):
                item = carrier(
                    f"{surface_id}_{suffix}", [target], source, axis,
                    centre=centre, span_m=span, height_m=height,
                    normal_xy=normal, z_min_m=min(zs), z_max_m=max(zs),
                    flip_u=axis == "left",
                )
                item["semantic_surface_id"] = surface_id
                output.append(item)
            continue

        mapping = str(registered["mapping"])
        if mapping == "planar_anchored":
            axis, normal = axis_for_role[role]
            if role.startswith("dormer_"):
                roof_source = str(next(a for a in registration["assemblies"] if a["source_id"] == "roof")["source_path"])
                output.append(carrier(
                    f"{surface_id}_roof_wrap", targets, roof_source, "plan",
                    centre=centre, span_m=36.0, height_m=height,
                    normal_z_min=-1.01, normal_z_max=1.01, material_role="roof",
                    plan_bounds=[-18.0, 18.0, -17.0, 17.0],
                ))
            item = carrier(
                surface_id, targets, source, axis, centre=centre, span_m=span, height_m=height,
                normal_xy=normal, z_min_m=min(zs), z_max_m=max(zs),
                flip_u=axis in {"rear", "left"},
            )
        elif mapping == "roof_plan_shared":
            if not roof_wrap_added:
                output.append(carrier(
                    "perimeter_roof_edge_wrap", targets, source, "plan",
                    centre=centre, span_m=36.0, height_m=height,
                    normal_z_min=-1.01, normal_z_max=1.01, material_role="roof",
                    plan_bounds=[-18.0, 18.0, -17.0, 17.0],
                ))
                roof_wrap_added = True
            item = carrier(
                surface_id, targets, source, "plan", centre=centre, span_m=36.0, height_m=height,
                normal_z_min=0.05, normal_z_max=1.01, material_role="roof",
                plan_bounds=[-18.0, 18.0, -17.0, 17.0],
                normal_angle_range_deg=roof_angles[role],
            )
        else:
            params = registered["mapping_parameters"]
            origin_x, origin_y = (float(value) for value in params["centre_xy_m"])
            is_dome = mapping == "radial_dome"
            is_corner_envelope = role in {
                "front_left_corner", "projecting_corner_cornices", "wrapped_corner_canopy",
            }
            corner_filter = role == "wrapped_corner_canopy"
            if role == "projecting_corner_cornices":
                source = (PREPARED_ASSETS / "cornice_zinc.jpg").relative_to(REPO).as_posix()
            item = carrier(
                surface_id, targets, source, "dome_radial" if is_dome else "cylindrical_segment",
                centre=centre, span_m=span, height_m=height,
                normal_z_min=-0.05 if is_dome else -0.25,
                normal_z_max=1.01 if is_dome else 0.25,
                material_role="glass" if is_dome else ("roof" if registered["source_id"] == "roof" else "elevation"),
                origin_x=origin_x, origin_y=origin_y,
                angle_start_deg=180.0 if is_corner_envelope else 0.0,
                angle_end_deg=270.0 if is_corner_envelope else 360.0,
                dome_base_z=min(zs), dome_height_m=height,
                dome_radius_m=span / 2,
                **({"normal_angle_range_deg": [180.0, 270.0]} if corner_filter else {}),
            )
        for key in (
            "carrier_mode", "surface_role", "mapping", "mapping_parameters",
            "registration_anchors", "source_id", "source_sha256",
            "source_crop_xyxy", "source_to_canonical_h", "material_binding",
        ):
            item[key] = deepcopy(registered[key])
        output.append(item)
    return output


def build_profile() -> tuple[dict[str, Any], dict[str, Any]]:
    lock = build_lock(CLAY_OUTPUT)
    if lock["status"] != "approved":
        raise RuntimeError("V92 clay lock did not pass")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["accepted_clay_geometry_sha256"] != lock["geometry_sha256"]:
        raise RuntimeError("sticker contract does not accept the current clay geometry")
    geometry = build_geometry()
    meshes = []
    for mesh in geometry["meshes"]:
        name = str(mesh["name"])
        if "dome" in name or "cupola" in name or "crown" in name:
            material = "roof"
        elif "canopy" in name:
            material = "secondary"
        else:
            material = "primary"
        meshes.append({
            "name": name,
            "vertices": mesh["vertices"],
            "faces": mesh["faces"],
            "material": material,
        })

    registration = build_registration(lock, contract, lock_path=CLAY_OUTPUT / "clay_lock.json")
    assemblies = render_carriers(lock, registration)

    base_payload = json.loads(BASE_PROFILE.read_text(encoding="utf-8"))
    profile = deepcopy(base_payload["profiles"][VARIANT])
    profile["identity"] = "Belle Epoque Grand Magasin built from an immutable audited clay shell with native registered stickers"
    profile["dimension_overrides"] = {"width_m": 36.0, "depth_m": 34.0, "default_floors": 5}
    profile["massing_graph"] = {
        "schema": "massing-graph@1",
        "profile": "belle-epoque-clay-sticker-v92",
        "height_m": float(lock["dimensions"]["visible_height_m"]),
        "reference_dimensions": {"width_m": 36.0, "depth_m": 34.0, "floors": 5},
        "reference_views": [
            {"role": "street_identity", "path": "frontend/public/archetypes/buildings/grand-magasin/variant_0.png"},
            {"role": "oblique_massing", "path": "frontend/public/archetypes/buildings/grand-magasin/variant_0_angle_60.jpg"},
            {"role": "roof_plan", "path": "frontend/public/archetypes/buildings/grand-magasin/variant_0_angle_90.jpg"},
        ],
        "nodes": [{
            "id": "v92_locked_clay",
            "kind": "locked_mesh_bundle",
            "location": [0.0, 0.0, 0.0],
            "geometry_sha256": lock["geometry_sha256"],
            "material": "primary",
            "meshes": meshes,
        }],
        "assemblies": assemblies,
        "voids": [{
            "id": "wrapped_corner_entrance",
            "kind": "recessed_tunnel",
            "depth_m": 4.2,
            "contour_sha256": lock["entrance"]["contour_sha256"],
        }],
        "target_views": ["archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context"],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.78, "identity_distance_scale": 0.94, "street_distance_scale": 0.94},
    }
    production = profile["production_contract"]
    production["quality_contract_version"] = 6
    production["representation"] = "immutable_clay_plus_native_surface_stickers"
    production["clay_lock"] = {
        "schema": lock["schema"],
        "geometry_sha256": lock["geometry_sha256"],
        "status": lock["status"],
        "separate_sticker_face_boxes": "forbidden",
        "entrance_topology": lock["entrance"]["topology"],
    }
    production["placement_contract"] = lock["placement"]
    production["sticker_method"] = {
        "contract": str(CONTRACT.relative_to(REPO)).replace("\\", "/"),
        "carrier_mode": "native_surface_material",
        "geometry_mutation_after_clay_gate": "forbidden",
        "registered_surface_roles": [item["surface_id"] for item in assemblies],
        "separate_full_face_boxes": "forbidden",
        "glass_transmission_preserved": True,
    }
    production["sticker_registration"] = {
        "schema": registration["schema"],
        "status": registration["status"],
        "surface_coverage": registration["surface_coverage"],
        "entrance_clearance": registration["entrance_clearance"],
        "feature_ownership": registration["feature_ownership"],
        "reciprocal_seams": registration["reciprocal_seams"],
        "atlas_plan": registration["atlas_plan"],
        "hard_stops": registration["hard_stops"],
    }
    production["image_lock"] = {
        "required_reference_roles": ["street_identity", "oblique_massing", "roof_plan"],
        "minimum_measurements": 8,
        "measurements": [
            {"feature": "block width", "role": "roof_plan", "value": 36.0, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "block depth", "role": "roof_plan", "value": 34.0, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "wall height", "role": "street_identity", "value": 20.5, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "courtyard width", "role": "roof_plan", "value": 18.0, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "courtyard depth", "role": "roof_plan", "value": 15.0, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "central dome diameter", "role": "roof_plan", "value": 16.4, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "corner cupola diameter", "role": "oblique_massing", "value": 6.8, "unit": "metres", "drives": "v92_locked_clay"},
            {"feature": "entrance tunnel depth", "role": "street_identity", "value": 4.2, "unit": "metres", "drives": "wrapped_corner_entrance"},
        ],
        "required_node_ids": ["v92_locked_clay"],
        "required_assembly_ids": [item["id"] for item in assemblies],
        "required_node_kinds": {"locked_mesh_bundle": 1},
        "required_assembly_kinds": {"carrier_skin": len(assemblies)},
    }
    profile["evidence_policy"] = {
        "authority": "reference_images",
        "metadata_mode": "disabled",
        "selected_metadata": [],
        "ignored_metadata": [{
            "path": "*",
            "reason": "the exact three-view evidence lock controls geometry; catalogue metadata is not used to override visible topology",
        }],
    }
    production.pop("metadata_cues", None)
    registry = {
        "schema": "catalogue-rollout-batch@1",
        "pipeline_version": "v92",
        "batch_id": "BELLE-EPOQUE-CLAY-STICKER-V92",
        "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": "grand_magasin",
            "variant_id": VARIANT,
            "family_id": "belle-epoque-grand-magasin-v92",
            "width_m": 36.0,
            "depth_m": 34.0,
            "floors": 5,
            "facade_sheet": "artifacts/three-all-surface-stickers-v91/facade-sheets/grand-magasin-belle-epoque",
        }],
    }
    return profile, registry


def main() -> None:
    profile, registry = build_profile()
    OUTPUT.write_text(json.dumps({
        "schema": "architectural-signatures@1",
        "override_profiles": [VARIANT],
        "profiles": {VARIANT: profile},
    }, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "registry": str(REGISTRY)}, indent=2))


if __name__ == "__main__":
    main()
