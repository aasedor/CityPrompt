"""Compile three new fixed landmarks with registered stickers on every surface."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from compile_catalogue_round_v87 import REPO, TOOLS, build_profile, write_json
from compile_catalogue_round_v88 import stage_workflow


PROFILE = TOOLS / "architectural_signature_profiles.d/three_all_surface_stickers_v91.json"
RECIPES = TOOLS / "three_all_surface_stickers_v91_surface_recipes.json"
REGISTRY = TOOLS / "three_all_surface_stickers_v91.json"
PILOT_REGISTRY = TOOLS / "three_all_surface_stickers_v91_pilot.json"
REMAINING_REGISTRY = TOOLS / "three_all_surface_stickers_v91_remaining.json"
GRAND_REPAIR_REGISTRY = TOOLS / "three_all_surface_stickers_v91_grand_repair.json"
SURFACE_ROOT = REPO / "artifacts/three-all-surface-stickers-v91/surface-stickers"
PREPARED_SURFACE_ROOT = REPO / "artifacts/three-all-surface-stickers-v91/render-ready-stickers"
FACADE_ROOT = REPO / "artifacts/three-all-surface-stickers-v91/facade-sheets"

TARGETS = (
    ("mediterranean_villa_estate", "med_villa_tuscan", 0, "tuscan-farmhouse-v91", 14.0, 10.0, 3),
    ("deco_theater_mainstreet", "deco_theater_egyptian_revival", 2, "egyptian-revival-theater-v91", 24.0, 34.0, 3),
    ("grand_magasin", "grand-magasin-belle-epoque", 0, "belle-epoque-grand-magasin-v91", 34.0, 28.0, 5),
)


def box(node_id: str, size: list[float], location: list[float], material: str, bevel: float = 0.04) -> dict[str, Any]:
    return {"id": node_id, "kind": "box", "size": size, "location": location, "material": material, "bevel_m": bevel}


def source(variant: str, face: str) -> str:
    return str((PREPARED_SURFACE_ROOT / variant / f"{face}.png").resolve())


def skin(
    variant: str, skin_id: str, axis: str, centre: list[float], span: float,
    height: float, face: str, *, flip: bool = False, angle: float | None = None,
    uv: tuple[float, float, float, float] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": skin_id, "kind": "facade_skin", "axis": axis,
        "centre": centre, "span_m": span, "height_m": height,
        "depth_m": 0.045, "band": "elevation", "flip_u": flip,
        "source_image_path": source(variant, face), "surface_role": face,
    }
    if angle is not None:
        payload["rotation_z_deg"] = angle
    if uv is not None:
        payload.update({"uv_u_min": uv[0], "uv_u_max": uv[1], "uv_v_min": uv[2], "uv_v_max": uv[3]})
    return payload


def roof_skin(
    variant: str, skin_id: str, shape: str, size: list[float], location: list[float],
    *, plan_bounds: list[float], **extra: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": skin_id, "kind": "roof_skin", "shape": shape,
        "size": size, "location": location, "band": "elevation",
        "source_image_path": source(variant, "roof"),
        "surface_role": "roof", "plan_bounds": plan_bounds,
    }
    payload.update(extra)
    return payload


def measure(feature: str, role: str, value: float, drives: str) -> dict[str, Any]:
    return {"feature": feature, "role": role, "value": value, "unit": "metres", "drives": drives}


def tuscan_draft() -> dict[str, Any]:
    variant = "med_villa_tuscan"
    return {
        "identity": "three-storey Tuscan farmhouse with ochre plaster, stone quoins, a true three-bay loggia and one broad terracotta hip roof",
        "overall_height_m": 12.2,
        "floors": 3,
        "fixed_identity": [
            "three cavernous round-arch loggia openings with stone piers and a recessed occupied back wall",
            "ochre lime plaster and rough pale-stone corner quoins",
            "restrained shuttered window grid on all four elevations",
            "single low-pitched weathered terracotta hip roof with deep eaves",
        ],
        "repeatable_capacity": ["fixed select-and-place villa; no floor, width or roof mutation"],
        "materials": {
            "primary": {"source_key": "stucco", "base_color": "#c99352", "role": "ochre lime plaster wall fields"},
            "secondary": {"source_key": "sandstone", "base_color": "#9b8468", "role": "rough stone arcade, quoins and reveals"},
            "roof": {"source_key": "terracotta", "base_color": "#8b5136", "role": "weathered overlapping terracotta pantiles"},
        },
        "nodes": [
            box("tuscan_rear_body", [14.0, 7.0, 9.6], [0.0, 1.5, 4.8], "primary", 0.05),
            box("tuscan_front_upper", [14.0, 3.0, 6.2], [0.0, -3.5, 6.5], "primary", 0.05),
            {
                "id": "tuscan_loggia", "kind": "opening_block", "axis": "front",
                "size": [14.0, 3.0, 3.4], "location": [0.0, -3.5, 1.7],
                "opening_shape": "round_arch", "opening_count": 3,
                "opening_centres_m": [-4.35, 0.0, 4.35], "opening_width_m": 3.35,
                "opening_base_m": 0.0, "opening_height_m": 3.2, "spring_height_m": 1.58,
                "arch_segments": 28, "section_mode": "recessed",
                "material": "secondary", "lining_material": "secondary",
                "trim_material": "secondary", "trim_profile_m": 0.13,
                "trim_depth_m": 0.28, "back_material": "interior_warm",
                "back_frame_material": "signature_door", "lining_setback_m": 0.08,
                "bevel_m": 0.04,
            },
            box("tuscan_left_quoin", [0.48, 0.55, 9.6], [-6.82, -4.72, 4.8], "secondary", 0.04),
            box("tuscan_right_quoin", [0.48, 0.55, 9.6], [6.82, -4.72, 4.8], "secondary", 0.04),
        ],
        "skins": [
            skin(variant, "tuscan_front_sticker", "front", [0.0, -5.035, 4.8], 14.0, 9.6, "front"),
            skin(variant, "tuscan_rear_sticker", "rear", [0.0, 5.035, 4.8], 14.0, 9.6, "rear", flip=True),
            skin(variant, "tuscan_left_sticker", "left", [-7.035, 0.0, 4.8], 10.0, 9.6, "left", flip=True),
            skin(variant, "tuscan_right_sticker", "right", [7.035, 0.0, 4.8], 10.0, 9.6, "right"),
            roof_skin(variant, "tuscan_roof_sticker", "hipped", [14.7, 10.7, 2.65], [0.0, 0.0, 9.55], plan_bounds=[-7.35, 7.35, -5.35, 5.35], ridge_axis="x", ridge_inset_m=3.8),
        ],
        "measurements": [
            measure("frontage width", "street_identity", 14.0, "tuscan_front_sticker"),
            measure("wall height", "street_identity", 9.6, "tuscan_rear_body"),
            measure("loggia count", "street_identity", 3.0, "tuscan_loggia"),
            measure("loggia depth", "oblique_massing", 3.0, "tuscan_loggia"),
            measure("loggia clear width", "street_identity", 3.35, "tuscan_loggia"),
            measure("roof rise", "roof_plan", 2.65, "tuscan_roof_sticker"),
            measure("roof width", "roof_plan", 14.7, "tuscan_roof_sticker"),
            measure("roof depth", "roof_plan", 10.7, "tuscan_roof_sticker"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.72, "identity_distance_scale": 0.90, "street_distance_scale": 0.92},
    }


def theater_draft() -> dict[str, Any]:
    variant = "deco_theater_egyptian_revival"
    return {
        "identity": "Egyptian Revival movie palace with battered pylon front, lotus columns, deep triple-door vestibule, marquee and stepped flat auditorium roofs",
        "overall_height_m": 18.2,
        "floors": 3,
        "fixed_identity": [
            "sand-coloured battered pylon facade with winged-sun and turquoise lotus ornament",
            "four aligned lotus columns framing tall upper windows",
            "deep three-opening entrance vestibule beneath a projecting marquee",
            "long brick-and-stucco auditorium sides and stepped stage-house roof",
        ],
        "repeatable_capacity": ["fixed select-and-place theater; auditorium length and facade proportions are locked"],
        "materials": {
            "primary": {"source_key": "sandstone", "base_color": "#c78d52", "role": "warm buff stucco and battered pylon fields"},
            "secondary": {"source_key": "copper", "base_color": "#3d9d93", "role": "turquoise Egyptian cornices, capitals and trim"},
            "roof": {"source_key": "roof_membrane", "base_color": "#6d675d", "role": "weathered flat membrane roofs and parapets"},
        },
        "nodes": [
            # The auditorium starts behind the vestibule: a full-depth box at
            # y=0 would silently brick over otherwise valid opening geometry.
            box("theater_auditorium", [24.0, 30.0, 14.0], [0.0, 2.0, 7.0], "primary", 0.08),
            box("theater_front_left_flank", [6.5, 4.0, 14.0], [-8.75, -15.0, 7.0], "primary", 0.06),
            box("theater_front_right_flank", [6.5, 4.0, 14.0], [8.75, -15.0, 7.0], "primary", 0.06),
            box("theater_front_upper_bridge", [11.0, 4.0, 9.6], [0.0, -15.0, 9.2], "primary", 0.06),
            box("theater_stage_house", [20.0, 13.5, 4.2], [0.0, 8.5, 16.1], "primary", 0.06),
            box("theater_left_pylon", [5.2, 1.0, 2.0], [-8.7, -17.4, 13.0], "primary", 0.06),
            box("theater_right_pylon", [5.2, 1.0, 2.0], [8.7, -17.4, 13.0], "primary", 0.06),
            {
                "id": "theater_entrance_vestibule", "kind": "opening_block", "axis": "front",
                "size": [11.0, 4.0, 4.4], "location": [0.0, -15.0, 2.2],
                "opening_shape": "rectangular", "opening_count": 3,
                "opening_centres_m": [-3.4, 0.0, 3.4], "opening_width_m": 2.35,
                "opening_base_m": 0.0, "opening_height_m": 3.85,
                "section_mode": "recessed", "material": "primary",
                "lining_material": "secondary", "trim_material": "secondary",
                "trim_profile_m": 0.12, "trim_depth_m": 0.26,
                "back_material": "interior", "back_glass_material": "glass",
                "back_frame_material": "signature_door",
                "lining_setback_m": 0.08, "bevel_m": 0.045,
            },
            box("theater_marquee", [13.2, 3.0, 0.42], [0.0, -18.25, 4.45], "secondary", 0.06),
        ],
        "skins": [
            skin(variant, "theater_front_sticker", "front", [0.0, -17.035, 7.0], 24.0, 14.0, "front"),
            skin(variant, "theater_rear_sticker", "rear", [0.0, 17.535, 7.0], 24.0, 14.0, "rear", flip=True),
            skin(variant, "theater_left_sticker", "left", [-12.035, 0.0, 7.0], 34.0, 14.0, "left", flip=True),
            skin(variant, "theater_right_sticker", "right", [12.035, 0.0, 7.0], 34.0, 14.0, "right"),
            roof_skin(variant, "theater_main_roof_sticker", "flat", [24.2, 34.2, 0.12], [0.0, 0.0, 13.98], plan_bounds=[-12.1, 12.1, -17.1, 17.1], thickness_m=0.12),
            roof_skin(variant, "theater_stage_roof_sticker", "flat", [20.2, 13.7, 0.12], [0.0, 8.5, 18.18], plan_bounds=[-12.1, 12.1, -17.1, 17.1], thickness_m=0.12),
        ],
        "measurements": [
            measure("facade width", "street_identity", 24.0, "theater_front_sticker"),
            measure("auditorium depth", "roof_plan", 34.0, "theater_auditorium"),
            measure("front wall height", "street_identity", 14.0, "theater_front_sticker"),
            measure("stage-house height", "oblique_massing", 18.2, "theater_stage_house"),
            measure("entrance tunnel depth", "street_identity", 4.0, "theater_entrance_vestibule"),
            measure("entrance count", "street_identity", 3.0, "theater_entrance_vestibule"),
            measure("marquee projection", "street_identity", 3.0, "theater_marquee"),
            measure("stage-house roof depth", "roof_plan", 13.7, "theater_stage_roof_sticker"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.76, "identity_distance_scale": 0.93, "street_distance_scale": 0.94},
    }


def grand_magasin_draft() -> dict[str, Any]:
    variant = "grand-magasin-belle-epoque"
    bounds = [-17.35, 17.35, -14.35, 14.35]
    cut = 4.5
    diagonal = (2 * cut * cut) ** 0.5
    return {
        "identity": "Belle Epoque corner department store with eight occupied elevations, iron-and-glass bays, perimeter zinc roofs, a central stained-glass dome and corner cupola",
        "overall_height_m": 28.3,
        "floors": 5,
        "fixed_identity": [
            "eight-sided corner block with continuous limestone and gilded iron glazing on every street face",
            "large source-positioned stained-glass dome over the interior court",
            "smaller corner cupola integrated with the chamfered entrance pavilion",
            "four zinc roof wings surrounding the domed court, with no generic square roof cap",
        ],
        "repeatable_capacity": ["fixed select-and-place landmark; all eight street faces and both domes are locked"],
        "materials": {
            "primary": {"source_key": "limestone", "base_color": "#d2c3a6", "role": "pale limestone piers, cornices and upper wall fields"},
            "secondary": {"source_key": "black_metal", "base_color": "#4c4437", "role": "dark iron glazing frames, gilded rails and entrance canopy"},
            "roof": {"source_key": "zinc", "base_color": "#889194", "role": "standing-seam zinc wings, dome ribs and flashing"},
        },
        "nodes": [
            {"id": "grand_magasin_block", "kind": "chamfered_box", "size": [34.0, 28.0, 20.0], "location": [0.0, 0.0, 10.0], "material": "primary", "chamfer_m": cut, "bevel_m": 0.07},
            {
                "id": "grand_magasin_entrance", "kind": "opening_block", "axis": "front",
                "size": [12.0, 4.2, 4.8], "location": [0.0, -11.9, 2.4],
                "opening_shape": "round_arch", "opening_count": 3,
                "opening_centres_m": [-3.75, 0.0, 3.75], "opening_width_m": 2.7,
                "opening_base_m": 0.0, "opening_height_m": 4.25, "spring_height_m": 2.85,
                "arch_segments": 28, "section_mode": "recessed", "material": "primary",
                "lining_material": "primary", "trim_material": "secondary",
                "trim_profile_m": 0.13, "trim_depth_m": 0.26,
                "back_material": "interior", "back_glass_material": "glass",
                "back_frame_material": "signature_door",
                "lining_setback_m": 0.08, "bevel_m": 0.045,
            },
            box("grand_magasin_canopy", [18.0, 3.2, 0.34], [0.0, -15.25, 4.75], "secondary", 0.05),
            box("grand_magasin_central_lantern", [1.8, 1.8, 1.2], [0.0, 0.0, 27.65], "roof", 0.08),
            box("grand_magasin_corner_lantern", [1.35, 1.35, 1.0], [-12.0, -9.0, 26.65], "roof", 0.06),
        ],
        "skins": [
            skin(variant, "grand_front_sticker", "front", [0.0, -14.035, 10.0], 25.0, 20.0, "front"),
            skin(variant, "grand_front_right_sticker", "angle", [14.77, -11.77, 10.0], diagonal, 20.0, "front_right", angle=45.0),
            skin(variant, "grand_right_sticker", "right", [17.035, 0.0, 10.0], 19.0, 20.0, "right"),
            skin(variant, "grand_rear_right_sticker", "angle", [14.77, 11.77, 10.0], diagonal, 20.0, "rear_right", angle=135.0),
            skin(variant, "grand_rear_sticker", "rear", [0.0, 14.035, 10.0], 25.0, 20.0, "rear", flip=True),
            skin(variant, "grand_rear_left_sticker", "angle", [-14.77, 11.77, 10.0], diagonal, 20.0, "rear_left", angle=-135.0),
            skin(variant, "grand_left_sticker", "left", [-17.035, 0.0, 10.0], 19.0, 20.0, "left", flip=True),
            skin(variant, "grand_front_left_sticker", "angle", [-14.77, -11.77, 10.0], diagonal, 20.0, "front_left", angle=-45.0),
            # Inner court surfaces reuse generated occupied elevations rather than flat materials.
            skin(variant, "grand_court_front_sticker", "front", [0.0, -5.95, 16.0], 14.0, 8.0, "rear"),
            skin(variant, "grand_court_rear_sticker", "rear", [0.0, 5.95, 16.0], 14.0, 8.0, "front", flip=True),
            skin(variant, "grand_court_left_sticker", "left", [-6.95, 0.0, 16.0], 12.0, 8.0, "right", flip=True),
            skin(variant, "grand_court_right_sticker", "right", [6.95, 0.0, 16.0], 12.0, 8.0, "left"),
            roof_skin(variant, "grand_front_roof_sticker", "mono_pitch", [34.6, 8.5, 4.0], [0.0, -10.0, 20.0], plan_bounds=bounds, high_side="rear"),
            roof_skin(variant, "grand_rear_roof_sticker", "mono_pitch", [34.6, 8.5, 4.0], [0.0, 10.0, 20.0], plan_bounds=bounds, high_side="front"),
            roof_skin(variant, "grand_left_roof_sticker", "mono_pitch", [9.0, 12.0, 4.0], [-12.7, 0.0, 20.0], plan_bounds=bounds, high_side="right"),
            roof_skin(variant, "grand_right_roof_sticker", "mono_pitch", [9.0, 12.0, 4.0], [12.7, 0.0, 20.0], plan_bounds=bounds, high_side="left"),
            roof_skin(variant, "grand_central_dome_sticker", "dome", [14.0, 14.0, 7.0], [0.0, 0.0, 20.7], plan_bounds=bounds, radius_m=7.0, height_m=7.0, rib_count=16, rib_radius_m=0.07, transmission=0.18, roughness=0.22),
            roof_skin(variant, "grand_corner_dome_sticker", "dome", [7.0, 7.0, 3.8], [-12.0, -9.0, 22.4], plan_bounds=bounds, radius_m=3.5, height_m=3.8, rib_count=12, rib_radius_m=0.055, transmission=0.16, roughness=0.22),
        ],
        "measurements": [
            measure("block width", "roof_plan", 34.0, "grand_magasin_block"),
            measure("block depth", "roof_plan", 28.0, "grand_magasin_block"),
            measure("wall height", "street_identity", 20.0, "grand_front_sticker"),
            measure("corner chamfer", "oblique_massing", cut, "grand_magasin_block"),
            measure("central dome diameter", "roof_plan", 14.0, "grand_central_dome_sticker"),
            measure("central dome rise", "oblique_massing", 7.0, "grand_central_dome_sticker"),
            measure("corner dome diameter", "street_identity", 7.0, "grand_corner_dome_sticker"),
            measure("entrance tunnel depth", "street_identity", 4.2, "grand_magasin_entrance"),
        ],
        "presentation_camera": {"hero_side": "left", "oblique_x_scale": 0.80, "identity_distance_scale": 0.96, "street_distance_scale": 0.96},
    }


def customize(variant: str, profile: dict[str, Any]) -> None:
    graph = profile["massing_graph"]
    draft_skins = graph.pop("_draft_skins", None)
    if draft_skins:
        graph["assemblies"] = draft_skins
    # build_profile places draft skins into assemblies in current compiler versions.
    graph["assemblies"] = [item for item in graph["assemblies"] if item.get("kind") in {"facade_skin", "roof_skin"}]
    if variant == "med_villa_tuscan":
        front = next(item for item in graph["assemblies"] if item["id"] == "tuscan_front_sticker")
        front["opening_clearances"] = [
            {"void_id": "tuscan_loggia", "centre_m": centre, "width_m": 3.35, "base_z_m": 0.0, "height_m": 3.2, "spring_z_m": 1.58, "shape": "round_arch", "arch_segments": 28}
            for centre in (-4.35, 0.0, 4.35)
        ]
    elif variant == "deco_theater_egyptian_revival":
        front = next(item for item in graph["assemblies"] if item["id"] == "theater_front_sticker")
        front["opening_clearances"] = [
            {"void_id": "theater_entrance_vestibule", "centre_m": centre, "width_m": 2.35, "base_z_m": 0.0, "height_m": 3.85}
            for centre in (-3.4, 0.0, 3.4)
        ]
        graph["assemblies"].append({
            "id": "theater_lotus_columns", "kind": "column_array",
            "start": [-5.8, -17.65, 4.55], "end": [5.8, -17.65, 4.55],
            "count": 4, "section": [0.48, 0.38], "height_m": 6.6, "material": "secondary",
        })
    elif variant == "grand-magasin-belle-epoque":
        front = next(item for item in graph["assemblies"] if item["id"] == "grand_front_sticker")
        front["opening_clearances"] = [
            {"void_id": "grand_magasin_entrance", "centre_m": centre, "width_m": 2.7, "base_z_m": 0.0, "height_m": 4.25, "spring_z_m": 2.85, "shape": "round_arch", "arch_segments": 28}
            for centre in (-3.75, 0.0, 3.75)
        ]
    else:
        raise KeyError(variant)

    graph["profile"] = f"{variant}_all_surface_sticker_v91"
    graph["target_views"] = ["archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context"]
    production = profile["production_contract"]
    production["quality_contract_version"] = 5
    production["stage_workflow"] = stage_workflow("all_surface_registered_sticker_landmark")
    production["geometry_kit_exclusions"] = list(profile.get("kits") or [])
    dims = graph["reference_dimensions"]
    production["placement_contract"] = {
        "method": "sticker_method", "mode": "fixed_landmark", "ui_interaction": "select_and_place",
        "polygon_fit": False, "footprint_m": {"width": dims["width_m"], "depth": dims["depth_m"]},
        "visible_height_m": graph["height_m"], "translation": "allowed", "rotation": "allowed",
        "uniform_scale": "discouraged", "non_uniform_scale": "forbidden", "floor_count_change": "forbidden",
        "freestanding_elevations": "authored", "lego_compatibility": "fixed landmark with registered stickers on every exposed wall and roof surface",
    }
    face_skins = [item for item in graph["assemblies"] if item.get("kind") == "facade_skin"]
    roof_skins = [item for item in graph["assemblies"] if item.get("kind") == "roof_skin"]
    production["sticker_method"] = {
        "surface_owner": "unique registered sticker on every exposed exterior wall, chamfer, court wall and roof field",
        "geometry_owner": "source-approved silhouette, void sections, projections, roof section and aligned medium detail",
        "duplicate_feature_ownership_forbidden": True,
        "registration_anchors": ["window_centres", "column_centres", "floor_datums", "roof_spring_line", "plan_bounds"],
        "all_surface_coverage": {
            "status": "required", "facade_skin_ids": [item["id"] for item in face_skins],
            "roof_skin_ids": [item["id"] for item in roof_skins],
            "unskinned_exposed_wall_fields_allowed": False,
            "unskinned_roof_fields_allowed": False,
        },
        "pre_sticker_massing_gate": {
            "silhouette_traced_from": ["street_identity", "oblique_massing", "roof_plan"],
            "all_elevation_occupancy_map": "required", "blank_side_or_rear": "hard_stop",
            "generic_roof_substitution": "hard_stop", "status": "pass_for_bounded_pilot",
        },
    }
    image_lock = production["image_lock"]
    image_lock["required_node_ids"] = [str(item["id"]) for item in graph["nodes"]]
    image_lock["required_assembly_ids"] = [str(item["id"]) for item in graph["assemblies"]]
    image_lock["required_node_kinds"] = dict(Counter(str(item["kind"]) for item in graph["nodes"]))
    image_lock["required_assembly_kinds"] = dict(Counter(str(item["kind"]) for item in graph["assemblies"]))
    image_lock.pop("surface_registration", None)
    profile["evidence_policy"] = {
        "authority": "reference_images",
        "metadata_mode": "disabled",
        "selected_metadata": [],
        "ignored_metadata": [{
            "path": "*",
            "reason": "the exact three-view reference set and cited architectural sources are the complete construction authority",
        }],
    }


def rename_v91(profile: dict[str, Any], recipes: list[dict[str, Any]]) -> None:
    for spec in profile.get("material_overrides", {}).values():
        key = str(spec.get("texture_key", ""))
        if key.startswith("v87_"):
            spec["texture_key"] = "v91_" + key[4:]
    for recipe in recipes:
        key = str(recipe["output_key"])
        if key.startswith("v87_"):
            recipe["output_key"] = "v91_" + key[4:]


def registry(targets: tuple[tuple[Any, ...], ...] = TARGETS, *, batch_id: str = "THREE-ALL-SURFACE-STICKERS-V91") -> dict[str, Any]:
    return {
        "schema": "catalogue-rollout-batch@1", "campaign": "tools/archetype_compiler/three_all_surface_stickers_v91.json",
        "pipeline_version": "v91", "surface_recipe_manifest": "tools/archetype_compiler/three_all_surface_stickers_v91_surface_recipes.json",
        "batch_id": batch_id, "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": parent, "variant_id": variant, "family_id": family,
            "width_m": width, "depth_m": depth, "floors": floors,
            "facade_sheet": str((FACADE_ROOT / variant).relative_to(REPO)).replace("\\", "/"),
        } for parent, variant, _index, family, width, depth, floors in targets],
    }


def main() -> None:
    drafts = {
        "med_villa_tuscan": tuscan_draft(),
        "deco_theater_egyptian_revival": theater_draft(),
        "grand-magasin-belle-epoque": grand_magasin_draft(),
    }
    profiles: dict[str, Any] = {}
    recipes: list[dict[str, Any]] = []
    for parent, variant, index, _family, width, depth, floors in TARGETS:
        draft = deepcopy(drafts[variant])
        profile, variant_recipes = build_profile(parent, variant, index, width, depth, floors, draft)
        profile.pop("extends", None)
        customize(variant, profile)
        rename_v91(profile, variant_recipes)
        profiles[variant] = profile
        recipes.extend(variant_recipes)
    write_json(PROFILE, {"schema": "architectural-signatures@1", "profiles": profiles})
    write_json(RECIPES, {"schema": "surface-story-recipes@1", "round_id": "THREE-ALL-SURFACE-STICKERS-V91", "recipes": recipes})
    write_json(REGISTRY, registry())
    write_json(PILOT_REGISTRY, registry(TARGETS[:1], batch_id="THREE-ALL-SURFACE-STICKERS-V91-PILOT"))
    write_json(REMAINING_REGISTRY, registry(TARGETS[1:], batch_id="THREE-ALL-SURFACE-STICKERS-V91-REMAINING"))
    write_json(GRAND_REPAIR_REGISTRY, registry(TARGETS[2:], batch_id="THREE-ALL-SURFACE-STICKERS-V91-GRAND-REPAIR"))
    print(PROFILE)


if __name__ == "__main__":
    main()
