"""Compile three new fixed-landmark Sticker Method pilots.

The exact catalogue images own geometry, registration and material decisions.
Metadata is used only for dimensions and material terminology that agrees with
the images.  Each public facade is one continuous sticker; physical geometry
is reserved for silhouette, depth, openings, roofs and construction returns.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from compile_catalogue_round_v87 import REPO, TOOLS, build_profile, write_json
from compile_catalogue_round_v88 import stage_workflow


PROFILE = TOOLS / "architectural_signature_profiles.d/three_sticker_landmarks_v90.json"
RECIPES = TOOLS / "three_sticker_landmarks_v90_surface_recipes.json"
REGISTRY = TOOLS / "three_sticker_landmarks_v90.json"
PILOT_REGISTRY = TOOLS / "three_sticker_landmarks_v90_pilot.json"
REMAINING_REGISTRY = TOOLS / "three_sticker_landmarks_v90_remaining.json"
PARIS_REPAIR_REGISTRY = TOOLS / "three_sticker_landmarks_v90_paris_repair.json"
FACADE_ROOT = REPO / "artifacts/three-sticker-landmarks-v90/facade-sheets"

TARGETS = (
    ("amsterdam_neck_gable_house", "neck_gable_merchant", 1, "amsterdam-neck-gable-merchant-v90", 6.0, 13.0, 4),
    ("parisian_corner_with_dome", "parisian-corner-with-dome-zinc-mansard", 0, "paris-zinc-dome-corner-v90", 20.0, 20.0, 4),
    ("toronto_bay_and_gable_house", "toronto_bay_gable_yellow_brick", 0, "toronto-yellow-bay-gable-v90", 6.0, 12.0, 2),
)


def box(node_id: str, size: list[float], location: list[float], material: str, bevel: float = 0.04) -> dict[str, Any]:
    return {"id": node_id, "kind": "box", "size": size, "location": location, "material": material, "bevel_m": bevel}


def skin(skin_id: str, axis: str, centre: list[float], span: float, height: float, band: str, *, flip: bool = False) -> dict[str, Any]:
    return {"id": skin_id, "axis": axis, "centre": centre, "span_m": span, "height_m": height, "depth_m": 0.045, "band": band, "flip_u": flip}


def measurement(feature: str, role: str, value: float, drives: str) -> dict[str, Any]:
    return {"feature": feature, "role": role, "value": value, "unit": "metres", "drives": drives}


def amsterdam_draft() -> dict[str, Any]:
    return {
        "identity": "Amsterdam merchant canal house with exactly three window bays on one continuous brick elevation, sandstone neck gable and steep tiled roof; never five bays",
        "overall_height_m": 16.0,
        "floors": 4,
        "fixed_identity": [
            "three-bay narrow red-brown brick canal facade",
            "sandstone neck gable with paired scroll shoulders and pediment-like crown",
            "steep dark tiled roof running behind the shaped front parapet",
            "tall recessed timber sash windows and double entrance leaf",
        ],
        "repeatable_capacity": ["fixed select-and-place landmark; no width or floor-count mutation"],
        "materials": {
            "primary": {"source_key": "red_brick", "base_color": "#7f3f2c", "role": "fine Dutch brick wall and chimney"},
            "secondary": {"source_key": "sandstone", "base_color": "#d7c39a", "role": "neck-gable scrolls, lintels and cornice"},
            "roof": {"source_key": "roof_membrane", "base_color": "#303739", "role": "steep dark clay/slate roof"},
        },
        "nodes": [
            box("canal_house_mass", [6.0, 13.0, 11.6], [0.0, 0.0, 5.8], "primary", 0.025),
            {"id": "canal_roof", "kind": "gable_roof", "size": [6.2, 13.4, 3.4], "location": [0.0, 0.0, 11.6], "material": "roof", "ridge_axis": "y", "bevel_m": 0.035},
            box("canal_cornice", [6.35, 0.45, 0.42], [0.0, -6.62, 11.35], "secondary", 0.035),
            box("canal_chimney", [0.75, 1.05, 2.0], [2.15, 3.4, 14.15], "primary", 0.025),
        ],
        "skins": [
            skin("amsterdam_front_sticker", "front", [0.0, -6.535, 5.8], 6.0, 11.6, "elevation"),
            skin("amsterdam_rear_sticker", "rear", [0.0, 6.535, 5.8], 6.0, 11.6, "side", flip=True),
            skin("amsterdam_left_sticker", "left", [-3.035, 0.0, 5.8], 13.0, 11.6, "side", flip=True),
            skin("amsterdam_right_sticker", "right", [3.035, 0.0, 5.8], 13.0, 11.6, "side"),
        ],
        "measurements": [
            measurement("facade width", "street_identity", 6.0, "amsterdam_front_sticker"),
            measurement("wall height", "street_identity", 11.6, "canal_house_mass"),
            measurement("neck gable rise", "street_identity", 4.4, "amsterdam_neck_gable"),
            measurement("roof rise", "roof_plan", 3.4, "canal_roof"),
            measurement("roof depth", "roof_plan", 13.4, "canal_roof"),
            measurement("cornice projection", "oblique_massing", 0.45, "canal_cornice"),
            measurement("front window bay spacing", "street_identity", 1.72, "amsterdam_front_openings"),
            measurement("side window rhythm", "oblique_massing", 3.0, "amsterdam_side_openings"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.55, "identity_distance_scale": 0.87, "street_distance_scale": 0.88},
    }


def paris_draft() -> dict[str, Any]:
    return {
        "identity": "Parisian limestone-and-brick corner building with a chamfered cafe frontage, mansard and ribbed zinc dome",
        "overall_height_m": 21.9,
        "floors": 5,
        "fixed_identity": [
            "two continuous image-registered street elevations meeting at a chamfered cafe corner",
            "projecting iron balconies with aligned supports and openings",
            "dark zinc mansard with dormers and chimney stacks",
            "elliptical ribbed corner dome, glazed drum and lantern",
        ],
        "repeatable_capacity": ["fixed select-and-place corner landmark; rotation and translation only"],
        "materials": {
            "primary": {"source_key": "limestone", "base_color": "#ded3bc", "role": "ashlar limestone frame and ornament"},
            "secondary": {"source_key": "red_brick", "base_color": "#9c624e", "role": "warm brick facade panels"},
            "roof": {"source_key": "zinc", "base_color": "#5f6868", "role": "mansard, dome and flashing"},
        },
        "nodes": [
            {"id": "paris_corner_mass", "kind": "chamfered_box", "size": [20.0, 20.0, 15.2], "location": [0.0, 0.0, 7.6], "material": "primary", "chamfer_m": 2.6, "bevel_m": 0.055},
            {"id": "paris_mansard", "kind": "hipped_roof", "size": [19.8, 19.8, 4.2], "location": [0.0, 0.0, 15.15], "material": "roof", "ridge_axis": "x", "ridge_inset_m": 5.4, "bevel_m": 0.04},
            {"id": "paris_dome_drum", "kind": "cylinder", "location": [-8.2, -8.2, 15.9], "radius_m": 3.0, "height_m": 1.8, "material": "primary", "vertices": 48},
            {"id": "paris_corner_dome", "kind": "dome_roof", "location": [-8.2, -8.2, 16.75], "radius_m": 3.0, "height_m": 3.45, "material": "roof", "rib_material": "roof", "rib_count": 12, "rib_radius_m": 0.052, "segments": 56, "rings": 18},
            {"id": "paris_lantern", "kind": "cylinder", "location": [-8.2, -8.2, 20.55], "radius_m": 0.72, "height_m": 1.35, "material": "secondary", "vertices": 12},
            {"id": "paris_lantern_cap", "kind": "cone", "location": [-8.2, -8.2, 21.45], "radius_m": 0.86, "height_m": 0.75, "material": "roof", "vertices": 16},
            box("paris_cornice_front", [15.1, 0.62, 0.62], [2.15, -10.1, 15.0], "primary", 0.045),
            box("paris_cornice_left", [0.62, 15.1, 0.62], [-10.1, 2.15, 15.0], "primary", 0.045),
            box("paris_chimney_front", [0.85, 1.15, 2.5], [4.6, -2.2, 17.5], "primary", 0.025),
            box("paris_chimney_left", [1.15, 0.85, 2.5], [-2.2, 4.6, 17.5], "primary", 0.025),
        ],
        "skins": [
            skin("paris_front_sticker", "front", [2.15, -10.035, 7.6], 15.1, 15.2, "elevation"),
            skin("paris_left_sticker", "left", [-10.035, 2.15, 7.6], 15.1, 15.2, "elevation", flip=True),
            skin("paris_right_sticker", "right", [10.035, 0.0, 7.6], 20.0, 15.2, "side"),
            skin("paris_rear_sticker", "rear", [0.0, 10.035, 7.6], 20.0, 15.2, "side", flip=True),
            {"id": "paris_corner_sticker", "axis": "angle", "centre": [-8.76, -8.76, 7.6], "span_m": 3.65, "height_m": 15.2, "depth_m": 0.055, "band": "elevation", "rotation_z_deg": -45.0},
        ],
        "measurements": [
            measurement("corner block width", "oblique_massing", 20.0, "paris_corner_mass"),
            measurement("facade wall height", "street_identity", 15.2, "paris_front_sticker"),
            measurement("chamfer width", "street_identity", 4.4, "paris_corner_sticker"),
            measurement("mansard rise", "roof_plan", 4.2, "paris_mansard"),
            measurement("dome diameter", "street_identity", 6.0, "paris_corner_dome"),
            measurement("dome rise", "roof_plan", 3.45, "paris_corner_dome"),
            measurement("continuous balcony length", "oblique_massing", 14.2, "paris_front_balconies"),
            measurement("lantern height", "roof_plan", 2.1, "paris_lantern"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.76, "identity_distance_scale": 0.94, "street_distance_scale": 0.94},
    }


def toronto_draft() -> dict[str, Any]:
    return {
        "identity": "Toronto yellow-brick bay-and-gable house with exactly two occupied storeys plus an attic gable, a true projecting two-storey bay, porch and steep decorated front gable; no third or fourth upper storey",
        "overall_height_m": 10.5,
        "floors": 2,
        "fixed_identity": [
            "narrow yellow-red brick house with deep side elevation",
            "projecting two-storey angled bay carrying the front gable",
            "steep dark shingle roof with visible eaves and chimney",
            "cavernous covered porch with timber columns and recessed green door",
        ],
        "repeatable_capacity": ["fixed select-and-place landmark; party-wall repetition disabled"],
        "materials": {
            "primary": {"source_key": "victorian_brick", "base_color": "#b06b43", "role": "Toronto pressed brick walls and bay"},
            "secondary": {"source_key": "cedar_wood", "base_color": "#4a3527", "role": "carved bargeboard, porch and window trim"},
            "roof": {"source_key": "roof_membrane", "base_color": "#343b3d", "role": "steep slate roof"},
        },
        "nodes": [
            box("toronto_main_mass", [6.0, 12.0, 7.2], [0.0, 0.0, 3.6], "primary", 0.035),
            {"id": "toronto_main_roof", "kind": "gable_roof", "size": [6.35, 12.5, 3.1], "location": [0.0, 0.0, 7.15], "material": "roof", "ridge_axis": "x", "bevel_m": 0.035},
            box("toronto_bay_mass", [3.4, 1.15, 5.75], [-0.8, -6.55, 3.35], "primary", 0.12),
            box("toronto_bay_crown", [3.75, 1.35, 0.30], [-0.8, -6.58, 6.25], "secondary", 0.035),
            box("toronto_chimney", [0.72, 0.95, 1.8], [2.05, 2.5, 9.55], "primary", 0.025),
            box("toronto_porch_canopy", [2.55, 2.05, 0.28], [1.55, -6.75, 3.25], "secondary", 0.04),
        ],
        "skins": [
            skin("toronto_front_sticker", "front", [0.0, -6.035, 3.6], 6.0, 7.2, "elevation"),
            skin("toronto_rear_sticker", "rear", [0.0, 6.035, 3.6], 6.0, 7.2, "side", flip=True),
            skin("toronto_left_sticker", "left", [-3.035, 0.0, 3.6], 12.0, 7.2, "side", flip=True),
            skin("toronto_right_sticker", "right", [3.035, 0.0, 3.6], 12.0, 7.2, "side"),
        ],
        "measurements": [
            measurement("house width", "street_identity", 6.0, "toronto_main_mass"),
            measurement("house depth", "oblique_massing", 12.0, "toronto_main_mass"),
            measurement("wall height", "street_identity", 7.2, "toronto_front_sticker"),
            measurement("front roof rise", "roof_plan", 3.1, "toronto_main_roof"),
            measurement("bay projection", "oblique_massing", 1.15, "toronto_bay_mass"),
            measurement("bay width", "street_identity", 3.4, "toronto_bay_mass"),
            measurement("porch depth", "street_identity", 2.05, "toronto_porch_canopy"),
            measurement("gable rise", "street_identity", 3.55, "toronto_front_gable"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.66, "identity_distance_scale": 0.88, "street_distance_scale": 0.90},
    }


def punched(opening_id: str, axis: str, face: float, openings: list[dict[str, Any]], *, surround: str = "secondary") -> dict[str, Any]:
    return {
        "id": opening_id, "kind": "punched_opening_schedule", "axis": axis,
        "face_coordinate_m": face, "frame_material": "secondary",
        "surround_material": surround, "glass_material": "glass",
        "interior_material": "interior_warm", "door_material": "signature_door",
        "openings": openings,
    }


def customize(variant: str, profile: dict[str, Any]) -> None:
    graph = profile["massing_graph"]
    # One uninterrupted sheet owns facade colour/ornament. Automatic full-wall
    # glazing overlays would create a second, misregistered window system.
    graph["assemblies"] = [item for item in graph["assemblies"] if item.get("kind") == "facade_skin"]
    if variant == "neck_gable_merchant":
        front_skin = next(item for item in graph["assemblies"] if item["id"] == "amsterdam_front_sticker")
        # The rectified source is wider than the exact three-bay landmark.
        # Crop one continuous central three-bay field; never slice by storey.
        front_skin.update({"uv_u_min": 0.20, "uv_u_max": 0.80})
        graph["assemblies"] += [
            {"id": "amsterdam_neck_gable", "kind": "shaped_gable_array", "axis": "front", "base_centre": [0.0, -6.68, 10.8], "positions_m": [0.0], "width_m": 6.1, "height_m": 4.6, "depth_m": 0.42, "material": "secondary", "infill_material": "primary", "profile_style": "ogee_scroll", "window_enabled": True, "window_width_m": 1.0, "window_height_m": 1.45, "window_base_offset_m": 1.35, "finial_enabled": False},
            punched("amsterdam_front_openings", "front", -6.62, [
                *[{"along_m": x, "base_z_m": z, "width_m": 1.18, "height_m": 2.05, "columns": 2, "rows": 2, "surround_m": 0.10} for z in (1.05, 4.0, 7.0) for x in (-1.72, 0.0, 1.72)],
                {"along_m": -0.82, "base_z_m": 0.05, "width_m": 1.35, "height_m": 2.85, "type": "door", "panel_rows": 3, "panel_columns": 1, "transom_height_m": 0.65},
            ]),
            punched("amsterdam_side_openings", "left", -3.08, [
                *[{"along_m": y, "base_z_m": z, "width_m": 1.05, "height_m": 1.9, "columns": 2, "rows": 2} for z in (1.2, 4.2, 7.2) for y in (-3.8, -0.8, 2.2)],
            ]),
            {"id": "amsterdam_roof_tiles", "kind": "pitched_roof_surface_detail", "centre": [0.0, 0.0, 11.6], "size": [6.2, 13.4, 3.4], "ridge_axis": "y", "tile_material": "roof", "weight_enabled": False, "rows": 16, "columns": 9, "gutter_enabled": True, "verge_enabled": True},
        ]
    elif variant == "parisian-corner-with-dome-zinc-mansard":
        front_openings = [{"along_m": x, "base_z_m": z, "width_m": 1.55, "height_m": 2.25, "columns": 2, "rows": 2, "surround_m": 0.10} for z in (1.05, 4.1, 7.15, 10.2) for x in (-3.8, -0.5, 2.8, 6.1)]
        left_openings = [{"along_m": y, "base_z_m": z, "width_m": 1.55, "height_m": 2.25, "columns": 2, "rows": 2, "surround_m": 0.10} for z in (1.05, 4.1, 7.15, 10.2) for y in (-3.8, -0.5, 2.8, 6.1)]
        graph["assemblies"] += [
            punched("paris_front_openings", "front", -10.09, front_openings),
            punched("paris_left_openings", "left", -10.09, left_openings),
            {"id": "paris_front_balconies", "kind": "balcony_array", "axis": "front", "centre": [2.15, -10.05, 0.0], "span_m": 14.2, "levels_z": [6.55, 12.65], "segments": 4, "depth_m": 0.82, "slab_material": "primary", "rail_material": "signature_metal", "pickets_per_segment": 9},
            {"id": "paris_left_balconies", "kind": "balcony_array", "axis": "left", "centre": [-10.05, 2.15, 0.0], "span_m": 14.2, "levels_z": [6.55, 12.65], "segments": 4, "depth_m": 0.82, "slab_material": "primary", "rail_material": "signature_metal", "pickets_per_segment": 9},
            {"id": "paris_cafe_awnings_front", "kind": "awning_schedule", "axis": "front", "face_coordinate_m": -10.18, "base_z_m": 3.0, "positions_m": [-3.15, 0.4, 3.95, 7.5], "width_m": 3.25, "projection_m": 1.55, "materials": ["signature_warm"]},
            {"id": "paris_cafe_awnings_left", "kind": "awning_schedule", "axis": "left", "face_coordinate_m": -10.18, "base_z_m": 3.0, "positions_m": [-3.15, 0.4, 3.95, 7.5], "width_m": 3.25, "projection_m": 1.55, "materials": ["signature_warm"]},
        ]
    elif variant == "toronto_bay_gable_yellow_brick":
        graph["assemblies"] += [
            {"id": "toronto_bay_sticker", "kind": "facade_skin", "axis": "front", "centre": [-0.8, -7.145, 3.35], "span_m": 3.4, "height_m": 5.75, "depth_m": 0.045, "band": "elevation", "uv_u_min": 0.0, "uv_u_max": 0.50, "uv_v_min": 0.08, "uv_v_max": 0.96},
            {"id": "toronto_front_gable", "kind": "shaped_gable_array", "axis": "front", "base_centre": [-0.8, -7.18, 6.15], "positions_m": [0.0], "width_m": 4.45, "height_m": 3.55, "depth_m": 0.36, "material": "secondary", "infill_material": "primary", "profile_style": "steep_triangle", "window_enabled": True, "window_width_m": 0.9, "window_height_m": 1.55, "window_base_offset_m": 0.72, "finial_enabled": True},
            punched("toronto_bay_front_windows", "front", -7.18, [
                {"along_m": -0.8, "base_z_m": 0.9, "width_m": 2.25, "height_m": 2.15, "columns": 3, "rows": 2, "surround_m": 0.12},
                {"along_m": -0.8, "base_z_m": 4.0, "width_m": 2.25, "height_m": 2.15, "columns": 3, "rows": 2, "surround_m": 0.12},
            ]),
            punched("toronto_front_door", "front", -7.22, [
                {"along_m": 1.55, "base_z_m": 0.05, "width_m": 1.15, "height_m": 2.75, "type": "door", "panel_rows": 3, "panel_columns": 1, "transom_height_m": 0.55},
                {"along_m": 1.65, "base_z_m": 4.2, "width_m": 1.15, "height_m": 1.9, "columns": 2, "rows": 2},
            ]),
            punched("toronto_side_windows", "left", -3.08, [
                *[{"along_m": y, "base_z_m": z, "width_m": 0.95, "height_m": 1.75, "columns": 2, "rows": 2} for z in (1.2, 4.2) for y in (-3.3, 0.0, 3.3)],
            ]),
            {"id": "toronto_porch_columns", "kind": "column_array", "start": [0.55, -7.65, 0.0], "end": [2.55, -7.65, 0.0], "count": 2, "section": [0.16, 0.16], "height_m": 3.15, "material": "secondary"},
            {"id": "toronto_roof_shingles", "kind": "pitched_roof_surface_detail", "centre": [0.0, 0.0, 7.15], "size": [6.35, 12.5, 3.1], "ridge_axis": "x", "tile_material": "roof", "weight_enabled": False, "rows": 15, "columns": 15, "gutter_enabled": True, "verge_enabled": True},
        ]
    else:
        raise KeyError(variant)

    # The rectified sticker already owns every visible sash, mullion, curtain
    # and reflection. A second punched-opening assembly covers those exact
    # pixels with generic grey glass and is therefore a hard duplicate-owner
    # failure. Keep projection geometry, but let the registered sheet own the
    # opening appearance until a mask-registered glass overlay is available.
    graph["assemblies"] = [
        item for item in graph["assemblies"]
        if item.get("kind") != "punched_opening_schedule"
    ]

    graph["profile"] = f"{variant}_continuous_sticker_v90"
    graph["target_views"] = ["archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context"]
    production = profile["production_contract"]
    production["quality_contract_version"] = 4
    production["stage_workflow"] = stage_workflow("registered_sticker_landmark")
    production["geometry_kit_exclusions"] = list(profile.get("kits") or [])
    dims = graph["reference_dimensions"]
    production["placement_contract"] = {
        "method": "sticker_method", "mode": "fixed_landmark",
        "ui_interaction": "select_and_place", "polygon_fit": False,
        "footprint_m": {"width": dims["width_m"], "depth": dims["depth_m"]},
        "visible_height_m": graph["height_m"],
        "translation": "allowed", "rotation": "allowed", "uniform_scale": "discouraged",
        "non_uniform_scale": "forbidden", "floor_count_change": "forbidden",
        "preferred_context": "image-matched urban placement",
        "freestanding_elevations": "authored",
        "lego_compatibility": "fixed landmark with continuous registered facade skins",
    }
    production["sticker_method"] = {
        "surface_owner": "one continuous registered facade per elevation",
        "geometry_owner": "silhouette, roof, openings, projections, returns and shadow depth",
        "duplicate_feature_ownership_forbidden": True,
        "registration_anchors": ["window_centres", "column_centres", "floor_datums", "roof_spring_line"],
    }
    production["image_lock"]["required_node_ids"] = [str(item["id"]) for item in graph["nodes"]]
    production["image_lock"]["required_assembly_ids"] = [str(item["id"]) for item in graph["assemblies"]]
    production["image_lock"]["required_node_kinds"] = dict(Counter(str(item["kind"]) for item in graph["nodes"]))
    production["image_lock"]["required_assembly_kinds"] = dict(Counter(str(item["kind"]) for item in graph["assemblies"]))
    production["image_lock"].pop("surface_registration", None)
    profile["evidence_policy"] = {
        "authority": "reference_images", "metadata_mode": "disabled",
        "selected_metadata": [],
        "ignored_metadata": [{"path": "*", "reason": "not used unless visibly corroborated by all exact reference roles"}],
    }


def rename_v90(profile: dict[str, Any], recipes: list[dict[str, Any]]) -> None:
    for spec in profile.get("material_overrides", {}).values():
        key = str(spec.get("texture_key", ""))
        if key.startswith("v87_"):
            spec["texture_key"] = "v90_" + key[4:]
    for recipe in recipes:
        key = str(recipe["output_key"])
        if key.startswith("v87_"):
            recipe["output_key"] = "v90_" + key[4:]


def registry(targets: tuple[tuple[Any, ...], ...] = TARGETS, *, batch_id: str = "THREE-STICKER-LANDMARKS-V90") -> dict[str, Any]:
    return {
        "schema": "catalogue-rollout-batch@1",
        "campaign": "tools/archetype_compiler/three_sticker_landmarks_v90.json",
        "pipeline_version": "v90",
        "surface_recipe_manifest": "tools/archetype_compiler/three_sticker_landmarks_v90_surface_recipes.json",
        "batch_id": batch_id,
        "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": parent, "variant_id": variant, "family_id": family,
            "width_m": width, "depth_m": depth, "floors": floors,
            "facade_sheet": str((FACADE_ROOT / variant).relative_to(REPO)).replace("\\", "/"),
        } for parent, variant, _index, family, width, depth, floors in targets],
    }


def main() -> None:
    drafts = {
        "neck_gable_merchant": amsterdam_draft(),
        "parisian-corner-with-dome-zinc-mansard": paris_draft(),
        "toronto_bay_gable_yellow_brick": toronto_draft(),
    }
    profiles: dict[str, Any] = {}
    recipes: list[dict[str, Any]] = []
    for parent, variant, index, _family, width, depth, floors in TARGETS:
        profile, variant_recipes = build_profile(parent, variant, index, width, depth, floors, deepcopy(drafts[variant]))
        # These catalogue-specific parents do not have a reusable base
        # signature profile. The fixed landmark graph is complete by itself.
        profile.pop("extends", None)
        customize(variant, profile)
        rename_v90(profile, variant_recipes)
        profiles[variant] = profile
        recipes.extend(variant_recipes)
    write_json(PROFILE, {"schema": "architectural-signatures@1", "profiles": profiles})
    write_json(RECIPES, {"schema": "surface-story-recipes@1", "round_id": "THREE-STICKER-LANDMARKS-V90", "recipes": recipes})
    write_json(REGISTRY, registry())
    write_json(PILOT_REGISTRY, registry(TARGETS[:1], batch_id="THREE-STICKER-LANDMARKS-V90-PILOT"))
    write_json(REMAINING_REGISTRY, registry(TARGETS[1:], batch_id="THREE-STICKER-LANDMARKS-V90-REMAINING"))
    write_json(PARIS_REPAIR_REGISTRY, registry(TARGETS[1:2], batch_id="THREE-STICKER-LANDMARKS-V90-PARIS-REPAIR"))
    print(PROFILE)


if __name__ == "__main__":
    main()
