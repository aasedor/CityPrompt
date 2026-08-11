"""Compile the five-storey continuous-shell Belle Epoque V94 pilot."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from belle_epoque_floor_sticker_v93 import build_floor_plan
from build_belle_epoque_continuous_geometry_v94 import (
    CUPOLA_BASE_Z,
    CUPOLA_VERTICAL_SCALE,
    build_continuous_geometry,
)
from compile_belle_epoque_floor_sticker_v93 import (
    _floor_carrier,
    _floor_coverage_carrier,
    build_profile as build_v93_profile,
)


TOOL_DIR = Path(__file__).resolve().parent
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zzz_belle_epoque_continuous_sticker_v94.json"
REGISTRY = TOOL_DIR / "belle_epoque_continuous_sticker_v94.json"
VARIANT_ID = "grand-magasin-belle-epoque-continuous-5"
FAMILY_ID = "belle-epoque-grand-magasin-v94-continuous-5"


def _target_survives(target: str, mesh_names: set[str]) -> bool:
    return target in mesh_names or any(name.startswith(f"{target}_") for name in mesh_names)


def _detail_assemblies() -> list[dict[str, Any]]:
    return [
        {
            "id": "v94_recessed_corner_portal",
            "kind": "recessed_portal_section",
            "outer_centre_xy": [-15.949747, -14.949747],
            "inward_xy": [0.707107, 0.707107],
            "tangent_xy": [0.707107, -0.707107],
            "width_m": 4.85,
            "height_m": 4.38,
            "recess_m": 2.85,
            "sill_z_m": 0.12,
            "frame_profile_m": 0.082,
            "frame_material": "signature_bronze",
            "glass_material": "glass",
            "interior_material": "interior_warm",
            "semantic_role": "occupied_recessed_entrance_section",
        },
        {
            "id": "v94_curved_iron_glass_canopy",
            "kind": "curved_glass_canopy",
            "centre_xy": [-11.0, -10.0],
            "inner_radius_m": 7.02,
            "outer_radius_m": 8.62,
            "angle_start_deg": 200.0,
            "angle_end_deg": 250.0,
            "segments": 10,
            "inner_z_m": 5.25,
            "outer_z_m": 5.08,
            "glass_thickness_m": 0.045,
            "rib_radius_m": 0.035,
            "glass_material": "glass",
            "frame_material": "signature_bronze",
            "semantic_role": "thin_translucent_supported_canopy",
        },
        {
            "id": "v94_portal_glass_sticker",
            "kind": "carrier_skin",
            "surface_id": "principal_entrance_glass",
            "target_ids": ["v94_recessed_corner_portal_GlassDoorWall"],
            "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v92/corner_seam_matched.jpg",
            "source_id": "corner_seam_matched_entrance_crop",
            "axis": "angle",
            "rotation_z_deg": -45.0,
            "centre": [-13.934493, -12.934493, 2.31],
            "span_m": 4.85,
            "height_m": 4.38,
            "z_min_m": 0.12,
            "z_max_m": 4.5,
            "uv_u_min": 0.20,
            "uv_u_max": 0.80,
            "uv_v_min": 0.0,
            "uv_v_max": 0.31,
            "normal_z_min": -1.01,
            "normal_z_max": 1.01,
            "material_role": "glass",
            "finish_class": "registered_entrance_glass_with_occupied_depth",
            "sticker_layer": "entrance_optical_overlay",
            "floor_role": "ground",
            "final_surface_coverage": True,
            "semantic_role": "source_registered_recessed_entrance",
        },
        {
            "id": "v94_central_dome_ribs",
            "kind": "dome_rib_system",
            "centre_xy": [0.0, 0.0],
            "radius_m": 5.9,
            "base_z_m": 25.75,
            "rise_m": 4.0,
            "meridians": 20,
            "ring_steps": 8,
            "ring_fractions": [0.24, 0.48, 0.70],
            "profile_m": 0.045,
            "material": "signature_bronze",
            "semantic_role": "physical_stained_glass_dome_ribs",
        },
        {
            "id": "v94_corner_cupola_ribs",
            "kind": "dome_rib_system",
            "centre_xy": [-14.5, -13.5],
            "radius_m": 3.2,
            "base_z_m": CUPOLA_BASE_Z + (25.05 - CUPOLA_BASE_Z) * CUPOLA_VERTICAL_SCALE,
            "rise_m": 3.3 * CUPOLA_VERTICAL_SCALE,
            "meridians": 16,
            "ring_steps": 7,
            "ring_fractions": [0.28, 0.56, 0.76],
            "profile_m": 0.038,
            "material": "signature_bronze",
            "semantic_role": "physical_stained_glass_cupola_ribs",
        },
    ]


def build_profile() -> dict[str, Any]:
    profile = deepcopy(build_v93_profile(5))
    geometry = build_continuous_geometry()
    if geometry["audit"]["status"] != "pass":
        raise RuntimeError("V94 continuous geometry audit failed")
    plan = build_floor_plan(5, segmented_geometry_sha256=geometry["geometry_sha256"])
    mesh_by_surface = {
        str(mesh["semantic_surface_id"]): mesh
        for mesh in geometry["meshes"] if mesh.get("material_domain") == "vertical_occupied_floor"
    }
    mesh_names = {str(mesh["name"]) for mesh in geometry["meshes"]}

    profile["identity"] = "Belle Epoque Grand Magasin V94, continuous floor-addressed Sticker Method"
    profile["glass_profile"] = "low_iron_clear"
    profile["signature_material_overrides"] = {
        "signature_bronze": {
            "base_color": "#4a3523", "roughness": 0.34, "metallic": 0.78
        },
        "signature_metal": {
            "base_color": "#24201b", "roughness": 0.32, "metallic": 0.76
        }
    }
    graph = profile["massing_graph"]
    graph["profile"] = "belle-epoque-continuous-sticker-v94-5"
    graph["nodes"][0]["geometry_sha256"] = geometry["geometry_sha256"]
    graph["nodes"][0]["meshes"] = [
        {
            "name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
            "material": "roof" if mesh.get("material_domain") == "roof_only" else "primary",
            "material_domain": mesh.get("material_domain"),
        }
        for mesh in geometry["meshes"]
    ]

    retained: list[dict[str, Any]] = []
    for item in graph["assemblies"]:
        if item.get("sticker_layer") in {"floor_band", "floor_coverage_seal"}:
            continue
        # The V92 catch-all edge wrap maps the full roof sheet onto vertical
        # faces after their exact zinc carriers, reintroducing its white image
        # border as a pale band. Exact face carriers already cover these faces.
        if item.get("id") == "v92_skin_perimeter_roof_edge_wrap":
            continue
        targets = [str(value) for value in item.get("target_ids", [])]
        if item.get("kind") == "carrier_skin" and targets and not any(_target_survives(target, mesh_names) for target in targets):
            continue
        retained_item = deepcopy(item)
        if str(retained_item.get("source_image_path", "")).endswith("sticker-roof.png"):
            retained_item["source_image_path"] = (
                "tools/archetype_compiler/sticker_assets/belle_epoque_v94/roof_edge_extended.png"
            )
            retained_item["source_id"] = "roof_edge_extended_v94"
        if any("cornice" in target or "crown_return" in target for target in targets):
            retained_item.update({
                "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v92/front_seam_matched.jpg",
                "source_id": "front_seam_matched_dentil_crop",
                "uv_u_min": 0.0,
                "uv_u_max": 1.0,
                "uv_v_min": 0.755859,
                "uv_v_max": 0.814453,
                "finish_class": "carved_stone_dentil_cornice_finish",
            })
        if any(target in {
            "corner_upper_tower", "corner_tower_crown", "corner_cupola_drum",
            "corner_glass_cupola", "corner_cupola_cap", "corner_cupola_finial",
        } for target in targets) and retained_item.get("axis") != "box_projected":
            centre = list(retained_item.get("centre") or [0.0, 0.0, CUPOLA_BASE_Z])
            centre[2] = CUPOLA_BASE_Z + (float(centre[2]) - CUPOLA_BASE_Z) * CUPOLA_VERTICAL_SCALE
            retained_item["centre"] = centre
            for key in ("z_min_m", "z_max_m", "dome_base_z"):
                if key in retained_item:
                    retained_item[key] = CUPOLA_BASE_Z + (
                        float(retained_item[key]) - CUPOLA_BASE_Z
                    ) * CUPOLA_VERTICAL_SCALE
            for key in ("height_m", "dome_height_m"):
                if key in retained_item:
                    retained_item[key] = float(retained_item[key]) * CUPOLA_VERTICAL_SCALE
        if "corner_upper_tower" in targets:
            retained_item.update({
                "uv_u_min": 0.02,
                "uv_u_max": 0.98,
                "uv_v_min": 0.72,
                "uv_v_max": 0.99,
                "source_id": "corner_seam_matched_upper_crop",
            })
        retained.append(retained_item)

    coverage: list[dict[str, Any]] = []
    hero: list[dict[str, Any]] = []
    for item in plan["floor_instances"]:
        mesh = mesh_by_surface[str(item["surface_id"])]
        revised = deepcopy(item)
        revised["target_ids"] = [str(mesh["name"])]
        floor_key = str(item["floor_index"])
        coverage_carrier = _floor_coverage_carrier(revised, mesh)
        coverage_carrier["face_indices"] = list(mesh["floor_face_indices"][floor_key])
        coverage_carrier["continuous_shell"] = True
        coverage.append(coverage_carrier)
        hero_carrier = _floor_carrier(revised, mesh)
        hero_carrier["face_indices"] = list(mesh["hero_floor_face_indices"][floor_key])
        hero_carrier["continuous_shell"] = True
        if str(item["surface_id"]) == "facade_front":
            hero_carrier["uv_u_min"] = 0.012
        elif str(item["surface_id"]) == "corner_pavilion":
            hero_carrier["uv_u_min"] = 0.012
            hero_carrier["uv_u_max"] = 0.988
        hero.append(hero_carrier)

    graph["assemblies"] = (
        retained + coverage + hero + _detail_assemblies()
        + _roof_edge_carriers() + _principal_corner_return_carriers()
    )
    graph["continuous_floor_sticker_contract"] = {
        "required": True,
        "floor_count": 5,
        "geometry_sha256": geometry["geometry_sha256"],
        "continuous_wall_count": geometry["audit"]["continuous_wall_count"],
        "internal_floor_cap_count": geometry["audit"]["internal_floor_cap_count"],
        "legacy_opaque_canopy": "forbidden",
        "sticker_boundary_crossing_window_or_column": "hard_stop",
        "architect_score_target": 90,
    }
    production = profile["production_contract"]
    production["representation"] = "continuous_geometry_plus_floor_addressed_native_stickers"
    production["clay_lock"]["geometry_sha256"] = geometry["geometry_sha256"]
    production["clay_lock"]["source_v93_geometry_sha256"] = geometry["source_v93_geometry_sha256"]
    production["clay_lock"]["status"] = "approved_continuous_shell_v94"
    production["floor_sticker_method"].update({
        "schema": "continuous-floor-sticker-contract@1",
        "continuous_wall_count": 9,
        "internal_floor_cap_count": 0,
        "floor_coverage_seal_count": len(coverage),
        "floor_hero_sticker_count": len(hero),
        "physical_entrance_section": True,
        "physical_glass_canopy": True,
        "physical_dome_ribs": True,
        "architect_score_target": 90,
    })
    production["image_lock"]["required_assembly_ids"] = [item["id"] for item in graph["assemblies"]]
    production["image_lock"]["required_assembly_kinds"] = {"carrier_skin": len(coverage) + len(hero)}
    return profile


def _roof_edge_carriers() -> list[dict[str, Any]]:
    """Map the zinc edge as four elevations instead of smearing a plan atlas."""

    source = "tools/archetype_compiler/sticker_assets/belle_epoque_v92/cornice_zinc.jpg"
    directions = (
        ("front", "front", [0.0, -1.0], [0, 8, 16], False),
        ("right", "right", [1.0, 0.0], [1, 9, 17], False),
        ("rear", "rear", [0.0, 1.0], [2, 10, 18], True),
        ("left", "left", [-1.0, 0.0], [3, 11, 19], True),
    )
    return [
        {
            "id": f"v94_roof_edge_{name}",
            "kind": "carrier_skin",
            "surface_id": f"roof_edge_{name}",
            "target_ids": ["watertight_perimeter_court_crown"],
            "source_image_path": source,
            "source_id": "v94_directional_zinc_edge",
            "axis": axis,
            "centre": [0.0, 0.0, 22.55],
            "span_m": 36.0 if axis in {"front", "rear"} else 34.0,
            "height_m": 4.3,
            "z_min_m": 20.4,
            "z_max_m": 24.7,
            "normal_xy": normal,
            "normal_dot_min": 0.60,
            "face_indices": faces,
            "flip_u": flip_u,
            "material_role": "roof",
            "finish_class": "directional_zinc_cornice_edge",
            "sticker_layer": "roof_edge_finish",
            "final_surface_coverage": True,
        }
        for name, axis, normal, faces, flip_u in directions
    ]


def _principal_corner_return_carriers() -> list[dict[str, Any]]:
    """Give the straight-wall end cap a source-derived owner at the pavilion join."""

    return [{
        "id": "v94_principal_corner_front_return",
        "kind": "carrier_skin",
        "surface_id": "principal_corner_front_return",
        "target_ids": ["facade_front_continuous_wall"],
        "source_image_path": "tools/archetype_compiler/sticker_assets/belle_epoque_v92/corner_seam_matched.jpg",
        "source_id": "corner_seam_matched_front_return",
        "axis": "left",
        "centre": [-11.0, -16.5, 10.25],
        "span_m": 1.0,
        "height_m": 20.5,
        "z_min_m": 0.0,
        "z_max_m": 20.5,
        "uv_u_min": 0.955,
        "uv_u_max": 0.992,
        "uv_v_min": 0.0,
        "uv_v_max": 1.0,
        "normal_xy": [-1.0, 0.0],
        "normal_dot_min": 0.98,
        "face_indices": [4, 8, 12, 16, 21, 27],
        "material_role": "elevation",
        "finish_class": "registered_corner_to_front_return",
        "sticker_layer": "corner_join_finish",
        "final_surface_coverage": True,
    }]


def build_profiles() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = build_profile()
    payload = {
        "schema": "architectural-signatures@1",
        "override_profiles": ["grand-magasin-belle-epoque"],
        "profiles": {
            VARIANT_ID: profile,
            "grand-magasin-belle-epoque": deepcopy(profile),
        },
    }
    registry = {
        "schema": "catalogue-rollout-batch@1",
        "pipeline_version": "v94",
        "batch_id": "BELLE-EPOQUE-CONTINUOUS-STICKER-V94",
        "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": "grand_magasin", "variant_id": VARIANT_ID,
            "family_id": FAMILY_ID, "width_m": 36.0, "depth_m": 34.0, "floors": 5,
        }],
    }
    return payload, registry


def main() -> None:
    payload, registry = build_profiles()
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "registry": str(REGISTRY)}, indent=2))


if __name__ == "__main__":
    main()
