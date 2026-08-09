"""Compact, deterministic massing recipes for repeatable building families."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def _levels(podium: float, floor: float, floors: int) -> list[dict[str, Any]]:
    levels: list[dict[str, Any]] = [{"band": "podium", "height_m": podium}]
    if floors > 1:
        levels.append({"band": "floor", "height_m": floor, "repeat": floors - 1})
    return levels


def _clearances(
    centres: list[float], width: float, base: float, height: float, void_id: str,
) -> list[dict[str, Any]]:
    return [
        {
            "void_id": void_id,
            "centre_m": centre,
            "base_z_m": base,
            "width_m": width,
            "height_m": height,
        }
        for centre in centres
    ]


def _front_opening_landmark(recipe: dict[str, Any], dims: dict[str, Any]) -> dict[str, Any]:
    width = float(dims["width_m"])
    depth = float(dims["depth_m"])
    floors = int(recipe.get("floors", dims["default_floors"]))
    podium = float(recipe.get("podium_height_m", dims["podium_height_m"]))
    floor = float(recipe.get("floor_height_m", dims["floor_height_m"]))
    wall_height = podium + floor * max(0, floors - 1)
    roof_height = float(recipe.get("roof_height_m", dims.get("roof_height_m", 2.4)))
    frontage_depth = float(recipe.get("frontage_depth_m", 2.4))
    body_depth = depth - frontage_depth
    front_y = -depth / 2
    opening_count = int(recipe.get("opening_count", 1))
    opening_width = float(recipe["opening_width_m"])
    side_margin = float(recipe.get("side_margin_m", max(0.55, opening_width * 0.42)))
    usable = width - side_margin * 2
    bay = usable / opening_count
    centres = [-usable / 2 + bay * (index + 0.5) for index in range(opening_count)]
    opening_height = float(recipe["opening_height_m"])
    opening_base = float(recipe.get("opening_base_m", 0.12))
    opening_shape = str(recipe.get("opening_shape", "rectangular"))
    spring = float(recipe.get("spring_height_m", opening_height - opening_width / 2))
    void_id = str(recipe.get("void_id", "front_spatial_opening"))
    wall_material = str(recipe.get("wall_material", "primary"))
    frontage_material = str(recipe.get("frontage_material", wall_material))
    trim_material = str(recipe.get("trim_material", "secondary"))
    lining_material = str(recipe.get("lining_material", trim_material))
    roof_material = str(recipe.get("roof_material", "roof"))

    nodes: list[dict[str, Any]] = [
        {
            "id": "main_body", "kind": "box",
            "size": [width, body_depth, wall_height],
            "location": [0.0, frontage_depth / 2, wall_height / 2],
            "material": wall_material, "bevel_m": 0.10,
        },
        {
            "id": "front_opening_block", "kind": "opening_block",
            "size": [width, frontage_depth, podium],
            "location": [0.0, front_y + frontage_depth / 2, podium / 2],
            "material": frontage_material,
            "lining_material": lining_material,
            "trim_material": trim_material,
            "back_material": str(recipe.get("back_material", "interior_warm")),
            "back_glass_material": recipe.get("back_glass_material"),
            "back_frame_material": recipe.get("back_frame_material"),
            "opening_shape": opening_shape,
            "opening_count": opening_count,
            "opening_width_m": opening_width,
            "opening_base_m": opening_base,
            "opening_height_m": opening_height,
            "spring_height_m": spring,
            "side_margin_m": side_margin,
            "section_mode": str(recipe.get("section_mode", "recessed")),
            "trim_profile_m": float(recipe.get("trim_profile_m", 0.24)),
            "trim_depth_m": float(recipe.get("trim_depth_m", min(frontage_depth, 0.62))),
            "bevel_m": 0.055,
        },
        {
            "id": "upper_front", "kind": "box",
            "size": [width, frontage_depth, wall_height - podium],
            "location": [0.0, front_y + frontage_depth / 2, podium + (wall_height - podium) / 2],
            "material": wall_material, "bevel_m": 0.08,
        },
    ]
    roof_kind = str(recipe.get("roof_kind", "flat"))
    roof_node_ids: list[str] = []
    if roof_kind == "gabled":
        nodes.append({
            "id": "main_roof", "kind": "gable_roof",
            "size": [width + 0.5, depth + 0.5, roof_height],
            "location": [0.0, 0.0, wall_height], "material": roof_material,
            "ridge_axis": str(recipe.get("ridge_axis", "y")), "bevel_m": 0.07,
        })
        roof_node_ids.append("main_roof")
    elif roof_kind == "hipped":
        nodes.append({
            "id": "main_roof", "kind": "hipped_roof",
            "size": [width + 0.5, depth + 0.5, roof_height],
            "location": [0.0, 0.0, wall_height], "material": roof_material,
            "ridge_axis": str(recipe.get("ridge_axis", "x")),
            "ridge_inset_m": float(recipe.get("ridge_inset_m", min(width, depth) * 0.22)),
            "bevel_m": 0.07,
        })
        roof_node_ids.append("main_roof")
    else:
        nodes.append({
            "id": "main_roof", "kind": "roof_slab",
            "size": [width + 0.4, depth + 0.4, 0.38],
            "location": [0.0, 0.0, wall_height + 0.19], "material": roof_material,
            "bevel_m": 0.045,
        })
        roof_node_ids.append("main_roof")

    current_z = wall_height + (0.38 if roof_kind == "flat" else roof_height)
    for index, tier in enumerate(recipe.get("central_tiers") or []):
        tier_width, tier_depth, tier_height = (float(value) for value in tier)
        nodes.append({
            "id": f"central_tier_{index}", "kind": "box",
            "size": [tier_width, tier_depth, tier_height],
            "location": [0.0, 0.0, current_z + tier_height / 2],
            "material": wall_material, "bevel_m": 0.10,
        })
        current_z += tier_height
    if recipe.get("central_tiers"):
        last_tier = recipe["central_tiers"][-1]
        nodes.append({
            "id": "central_tier_cap", "kind": "roof_slab",
            "size": [float(last_tier[0]) + 0.35, float(last_tier[1]) + 0.35, 0.32],
            "location": [0.0, 0.0, current_z + 0.16], "material": roof_material,
            "bevel_m": 0.04,
        })
        roof_node_ids.append("central_tier_cap")

    clearances = _clearances(
        centres, opening_width + float(recipe.get("clearance_extra_m", 0.18)),
        opening_base, opening_height - opening_base + 0.04, void_id,
    )
    assemblies: list[dict[str, Any]] = [
        {
            "id": "front_podium_skin", "kind": "facade_skin", "axis": "front",
            "centre": [0.0, front_y - 0.025, podium / 2],
            "span_m": width - 0.10, "height_m": podium - 0.10, "depth_m": 0.05,
            "band": str(recipe.get("podium_band", "podium")), "opening_clearances": clearances,
        },
        {
            "id": "front_upper_skin", "kind": "facade_skin_stack", "axis": "front",
            "base_centre": [0.0, front_y - 0.025, podium],
            "span_m": width - 0.10, "depth_m": 0.05,
            "levels": [{"band": "floor", "height_m": floor, "repeat": max(1, floors - 1)}],
        },
        {
            "id": "left_skin", "kind": "facade_skin_stack", "axis": "left",
            "base_centre": [-width / 2 - 0.025, 0.0, 0.0],
            "span_m": depth - 0.10, "depth_m": 0.05, "flip_u": True,
            "levels": _levels(podium, floor, floors),
        },
        {
            "id": "right_skin", "kind": "facade_skin_stack", "axis": "right",
            "base_centre": [width / 2 + 0.025, 0.0, 0.0],
            "span_m": depth - 0.10, "depth_m": 0.05,
            "levels": _levels(podium, floor, floors),
        },
        {
            "id": "rear_skin", "kind": "facade_skin_stack", "axis": "rear",
            "base_centre": [0.0, depth / 2 + 0.025, 0.0],
            "span_m": width - 0.10, "depth_m": 0.05, "flip_u": True,
            "levels": _levels(podium, floor, floors),
        },
    ]
    if recipe.get("front_gable"):
        gable_positions = [float(value) for value in recipe.get("front_gable_positions_m", [0.0])]
        assemblies.append({
            "id": "front_identity_gable", "kind": "shaped_gable_array", "axis": "front",
            "base_centre": [0.0, front_y - 0.07, wall_height - 0.05],
            "positions_m": gable_positions,
            "width_m": float(recipe.get("front_gable_width_m", width * 0.72)),
            "height_m": roof_height * 1.15, "depth_m": 0.48,
            "profile_style": "steep_triangle", "material": trim_material,
            "infill_material": wall_material, "infill_enabled": True,
            "window_enabled": False, "finial_enabled": False, "bevel_m": 0.035,
        })
    portico = recipe.get("classical_portico")
    if portico:
        portico = deepcopy(portico)
        portico.setdefault("id", "front_classical_portico")
        portico["kind"] = "classical_portico"
        portico.setdefault("base_centre", [0.0, front_y - 0.05, 0.72])
        assemblies.append(portico)
    steps = recipe.get("ceremonial_steps")
    if steps:
        steps = deepcopy(steps)
        steps.setdefault("id", "front_ceremonial_steps")
        steps["kind"] = "steps"
        steps.setdefault("centre", [0.0, front_y - float(steps.get("depth_m", 3.0)) * 0.70, 0.0])
        assemblies.append(steps)

    void_shape = "round_arch_passage" if opening_shape == "round_arch" else "rectangular_passage"
    return {
        "schema": "massing-graph@1",
        "profile": str(recipe["profile"]),
        "description": str(recipe["description"]),
        "reference_views": deepcopy(recipe.get("reference_views") or []),
        "height_m": current_z + (0.32 if recipe.get("central_tiers") else 0.0),
        "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": floors, "floor_height_m": floor},
        "nodes": nodes,
        "voids": [{
            "id": void_id, "shape": void_shape, "axis": "front",
            "size": [width - side_margin * 2, frontage_depth, opening_height],
            "location": [0.0, front_y + frontage_depth / 2, opening_height / 2],
            "target_node_ids": ["front_opening_block"],
            "purpose": str(recipe.get("void_purpose", "reference-derived spatial opening")),
        }],
        "assemblies": assemblies,
        "target_views": ["archetype_match", "street", "aerial", "roof_audit", "context"],
        "recipe_contract": {"kind": "front_opening_landmark", "roof_node_ids": roof_node_ids},
    }


def _courtyard_passage(recipe: dict[str, Any], dims: dict[str, Any]) -> dict[str, Any]:
    width = float(dims["width_m"])
    depth = float(dims["depth_m"])
    floors = int(dims["default_floors"])
    podium = float(dims["podium_height_m"])
    floor = float(dims["floor_height_m"])
    wall_height = podium + floor * max(0, floors - 1)
    roof_height = float(recipe.get("roof_height_m", dims.get("roof_height_m", 2.4)))
    wing = float(recipe.get("wing_depth_m", 4.0))
    court_width, court_depth = width - wing * 2, depth - wing * 2
    opening_width = float(recipe.get("opening_width_m", 4.2))
    opening_height = float(recipe.get("opening_height_m", 4.0))
    opening_base = float(recipe.get("opening_base_m", 0.12))
    front_y = -depth / 2
    void_id = str(recipe.get("void_id", "courtyard_passage"))
    wall_material = str(recipe.get("wall_material", "primary"))
    lining_material = str(recipe.get("lining_material", "secondary"))
    roof_material = str(recipe.get("roof_material", "roof"))
    nodes: list[dict[str, Any]] = [
        {
            "id": "front_passage_wing", "kind": "opening_block",
            "size": [width, wing, wall_height],
            "location": [0.0, front_y + wing / 2, wall_height / 2],
            "material": wall_material, "lining_material": lining_material,
            "trim_material": wall_material, "opening_shape": "rectangular",
            "opening_count": 1, "opening_width_m": opening_width,
            "opening_base_m": opening_base, "opening_height_m": opening_height,
            "section_mode": "through", "bevel_m": 0.055,
        },
        {"id": "rear_wing", "kind": "box", "size": [width, wing, wall_height],
         "location": [0.0, depth / 2 - wing / 2, wall_height / 2], "material": wall_material, "bevel_m": 0.08},
        {"id": "left_wing", "kind": "box", "size": [wing, court_depth, wall_height],
         "location": [-width / 2 + wing / 2, 0.0, wall_height / 2], "material": wall_material, "bevel_m": 0.08},
        {"id": "right_wing", "kind": "box", "size": [wing, court_depth, wall_height],
         "location": [width / 2 - wing / 2, 0.0, wall_height / 2], "material": wall_material, "bevel_m": 0.08},
    ]
    roof_specs = [
        ("front_roof", [width + 0.4, wing + 0.4, roof_height], [0.0, front_y + wing / 2, wall_height], "x"),
        ("rear_roof", [width + 0.4, wing + 0.4, roof_height], [0.0, depth / 2 - wing / 2, wall_height], "x"),
        ("left_roof", [wing + 0.4, court_depth + 0.4, roof_height], [-width / 2 + wing / 2, 0.0, wall_height], "y"),
        ("right_roof", [wing + 0.4, court_depth + 0.4, roof_height], [width / 2 - wing / 2, 0.0, wall_height], "y"),
    ]
    for node_id, size, location, ridge in roof_specs:
        nodes.append({"id": node_id, "kind": "gable_roof", "size": size, "location": location,
                      "material": roof_material, "ridge_axis": ridge, "bevel_m": 0.065})
    clearances = _clearances(
        [0.0], opening_width + 0.18, opening_base,
        opening_height - opening_base + 0.04, void_id,
    )
    assemblies = [
        {"id": "front_skin", "kind": "facade_skin", "axis": "front",
         "centre": [0.0, front_y - 0.025, wall_height / 2], "span_m": width - 0.10,
         "height_m": wall_height - 0.10, "depth_m": 0.05, "band": "elevation",
         "opening_clearances": clearances},
        {"id": "left_outer_skin", "kind": "facade_skin_stack", "axis": "left",
         "base_centre": [-width / 2 - 0.025, 0.0, 0.0], "span_m": depth - 0.10,
         "depth_m": 0.05, "flip_u": True, "levels": _levels(podium, floor, floors)},
        {"id": "right_outer_skin", "kind": "facade_skin_stack", "axis": "right",
         "base_centre": [width / 2 + 0.025, 0.0, 0.0], "span_m": depth - 0.10,
         "depth_m": 0.05, "levels": _levels(podium, floor, floors)},
        {"id": "rear_outer_skin", "kind": "facade_skin_stack", "axis": "rear",
         "base_centre": [0.0, depth / 2 + 0.025, 0.0], "span_m": width - 0.10,
         "depth_m": 0.05, "flip_u": True, "levels": _levels(podium, floor, floors)},
    ]
    return {
        "schema": "massing-graph@1", "profile": str(recipe["profile"]),
        "description": str(recipe["description"]),
        "reference_views": deepcopy(recipe.get("reference_views") or []),
        "height_m": wall_height + roof_height,
        "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": floors, "floor_height_m": floor},
        "nodes": nodes,
        "voids": [
            {"id": "open_courtyard", "shape": "courtyard", "size": [court_width, court_depth, wall_height],
             "location": [0.0, 0.0, wall_height / 2], "purpose": "open planted courtyard"},
            {"id": void_id, "shape": "rectangular_passage", "axis": "front",
             "size": [opening_width, wing, opening_height],
             "location": [0.0, front_y + wing / 2, opening_height / 2],
             "target_node_ids": ["front_passage_wing"],
             "purpose": str(recipe.get("void_purpose", "timber-lined passage to courtyard"))},
        ],
        "assemblies": assemblies,
        "target_views": ["archetype_match", "street", "aerial", "roof_audit", "context"],
        "recipe_contract": {"kind": "courtyard_passage", "roof_node_ids": [item[0] for item in roof_specs]},
    }


def _stepped_gable_house(recipe: dict[str, Any], dims: dict[str, Any]) -> dict[str, Any]:
    """Compile a narrow image-measured canal house without a stretched atlas."""
    width = float(dims["width_m"])
    depth = float(dims["depth_m"])
    floors = int(recipe.get("floors", dims["default_floors"]))
    podium = float(recipe.get("podium_height_m", dims["podium_height_m"]))
    floor = float(recipe.get("floor_height_m", dims["floor_height_m"]))
    wall_height = podium + floor * max(0, floors - 1)
    roof_rise = float(recipe.get("roof_height_m", 4.1))
    gable_rise = float(recipe.get("gable_height_m", roof_rise + 1.0))
    front_y, rear_y = -depth / 2, depth / 2
    wall_material = str(recipe.get("wall_material", "primary"))
    cap_material = str(recipe.get("cap_material", "signature_stone"))
    roof_material = str(recipe.get("roof_material", "signature_roof"))

    front_openings = deepcopy(recipe.get("front_openings") or [])
    body_front_openings = [
        opening for opening in front_openings
        if float(opening.get("base_z_m", 0.0)) < wall_height - 0.35
    ]
    gable_front_openings = [
        opening for opening in front_openings
        if float(opening.get("base_z_m", 0.0)) >= wall_height - 0.35
    ]
    side_openings = deepcopy(recipe.get("side_openings") or [])
    rear_openings = deepcopy(recipe.get("rear_openings") or [])
    nodes = [
        {
            "id": "canal_house_body", "kind": "box",
            "size": [width, depth, wall_height],
            "location": [0.0, 0.0, wall_height / 2],
            "material": wall_material, "bevel_m": 0.055,
        },
        {
            "id": "canal_house_roof", "kind": "gable_roof",
            "size": [width + 0.18, depth + 0.20, roof_rise],
            "location": [0.0, 0.0, wall_height],
            "material": roof_material, "ridge_axis": "y", "bevel_m": 0.045,
        },
    ]
    assemblies: list[dict[str, Any]] = [
        {
            "id": "front_crow_step", "kind": "shaped_gable_array", "axis": "front",
            "base_centre": [0.0, front_y - 0.03, wall_height - 0.18],
            "positions_m": [0.0], "width_m": width + 0.10, "height_m": gable_rise,
            "depth_m": 0.38, "profile_style": "crow_step_flat",
            "profile_construction": "capped_masonry", "material": cap_material,
            "infill_material": wall_material, "cap_thickness_m": 0.16,
            "cap_projection_m": 0.10, "finial_enabled": False,
            "window_enabled": False, "bevel_m": 0.035,
        },
        {
            "id": "front_opening_schedule", "kind": "punched_opening_schedule",
            "axis": "front", "face_coordinate_m": front_y - 0.07,
            "openings": body_front_openings, "frame_material": "signature_metal",
            "surround_material": cap_material, "door_material": "signature_door",
            "glass_material": "glass", "interior_material": "glazing_interior_1",
            "minimum_rows": 3,
        },
        {
            "id": "front_gable_opening_schedule", "kind": "punched_opening_schedule",
            "axis": "front", "face_coordinate_m": front_y - 0.46,
            "openings": gable_front_openings, "frame_material": "signature_metal",
            "surround_material": cap_material, "glass_material": "glass",
            "interior_material": "glazing_interior_1", "minimum_rows": 3,
        },
        {
            "id": "right_opening_schedule", "kind": "punched_opening_schedule",
            "axis": "right", "face_coordinate_m": width / 2 + 0.07,
            "openings": side_openings, "frame_material": "signature_metal",
            "surround_material": cap_material, "glass_material": "glass",
            "interior_material": "glazing_interior_2", "minimum_rows": 3,
        },
        {
            "id": "left_opening_schedule", "kind": "punched_opening_schedule",
            "axis": "left", "face_coordinate_m": -width / 2 - 0.07,
            "openings": deepcopy(recipe.get("left_openings") or side_openings),
            "frame_material": "signature_metal", "surround_material": cap_material,
            "glass_material": "glass", "interior_material": "glazing_interior_3",
            "minimum_rows": 3,
        },
        {
            "id": "rear_opening_schedule", "kind": "punched_opening_schedule",
            "axis": "rear", "face_coordinate_m": rear_y + 0.07,
            "openings": rear_openings, "frame_material": "signature_metal",
            "surround_material": cap_material, "glass_material": "glass",
            "interior_material": "glazing_interior_4", "minimum_rows": 3,
        },
        {
            "id": "front_wall_anchors", "kind": "tie_grid", "axis": "front",
            "centre": [0.0, front_y - 0.13, 6.5], "span_m": 2.8,
            "height_m": 9.0, "columns": 2, "rows": 3,
            "style": "vertical_bar", "bar_length_m": 0.48,
            "bar_width_m": 0.075, "bar_depth_m": 0.050,
            "material": "signature_metal",
        },
        {
            "id": "right_wall_anchors", "kind": "tie_grid", "axis": "right",
            "centre": [width / 2 + 0.13, 0.0, 6.5], "span_m": depth - 2.0,
            "height_m": 9.0, "columns": 4, "rows": 3,
            "style": "vertical_bar", "bar_length_m": 0.48,
            "bar_width_m": 0.075, "bar_depth_m": 0.050,
            "material": "signature_metal",
        },
        {
            "id": "left_wall_anchors", "kind": "tie_grid", "axis": "left",
            "centre": [-width / 2 - 0.13, 0.0, 6.5], "span_m": depth - 2.0,
            "height_m": 9.0, "columns": 4, "rows": 3,
            "style": "vertical_bar", "bar_length_m": 0.48,
            "bar_width_m": 0.075, "bar_depth_m": 0.050,
            "material": "signature_metal",
        },
        {
            "id": "rear_wall_anchors", "kind": "tie_grid", "axis": "rear",
            "centre": [0.0, rear_y + 0.13, 6.5], "span_m": width - 1.2,
            "height_m": 9.0, "columns": 3, "rows": 3,
            "style": "vertical_bar", "bar_length_m": 0.48,
            "bar_width_m": 0.075, "bar_depth_m": 0.050,
            "material": "signature_metal",
        },
        {
            "id": "clay_roof_courses", "kind": "pitched_roof_surface_detail",
            "centre": [0.0, 0.0, wall_height],
            "size": [width + 0.18, depth + 0.20, roof_rise], "ridge_axis": "y",
            "tile_material": roof_material, "ridge_material": "roof_flashing",
            "verge_material": cap_material, "rows": int(recipe.get("roof_rows", 13)),
            "columns": int(recipe.get("roof_columns", 15)), "tile_thickness_m": 0.045,
            "weight_enabled": False, "gutter_enabled": True, "verge_enabled": True,
        },
        {
            "id": "front_stoep", "kind": "steps",
            "centre": [0.0, front_y - 0.62, 0.0], "width_m": 2.25,
            "depth_m": 1.20, "height_m": 0.48, "count": 3,
            "material": cap_material,
        },
    ]
    chimney = recipe.get("chimney")
    if chimney:
        assemblies.append({
            "id": "rear_chimney", "kind": "chimney_cluster_array",
            "centres": [[float(chimney.get("x_m", 1.55)), float(chimney.get("y_m", 3.8)),
                         wall_height + float(chimney.get("base_offset_m", 1.5))]],
            "count_per_cluster": int(chimney.get("count", 2)),
            "height_m": float(chimney.get("height_m", 2.3)),
            "section_m": float(chimney.get("section_m", 0.34)),
            "spacing_m": float(chimney.get("spacing_m", 0.52)),
            "material": wall_material, "cap_material": cap_material,
        })

    return {
        "schema": "massing-graph@1", "profile": str(recipe["profile"]),
        "description": str(recipe["description"]),
        "reference_views": deepcopy(recipe.get("reference_views") or []),
        "height_m": wall_height + gable_rise,
        "reference_dimensions": {
            "width_m": width, "depth_m": depth, "floors": floors,
            "floor_height_m": floor,
        },
        "nodes": nodes, "voids": [], "assemblies": assemblies,
        "presentation_camera": deepcopy(recipe.get("presentation_camera") or {}),
        "target_views": ["archetype_match", "street", "front_corner_oblique", "aerial", "roof_audit"],
        "recipe_contract": {
            "kind": "stepped_gable_house", "front_opening_count": len(front_openings),
            "side_opening_count": len(side_openings), "roof_node_ids": ["canal_house_roof"],
        },
    }


def _multi_aisle_market_hall(recipe: dict[str, Any], dims: dict[str, Any]) -> dict[str, Any]:
    """Compile a permeable masonry-and-iron market from street and roof evidence."""
    width = float(dims["width_m"])
    depth = float(dims["depth_m"])
    eave_z = float(recipe.get("eave_height_m", 6.2))
    header_height = float(recipe.get("header_height_m", 2.0))
    column_height = eave_z - header_height
    central_width = float(recipe.get("central_aisle_width_m", width * 0.34))
    side_width = (width - central_width) / 2
    central_rise = float(recipe.get("central_rise_m", 7.2))
    side_rise = float(recipe.get("side_rise_m", 4.3))
    cross_depth = float(recipe.get("cross_aisle_depth_m", depth * 0.36))
    cross_rise = float(recipe.get("cross_rise_m", 5.8))
    front_y, rear_y = -depth / 2, depth / 2
    left_x, right_x = -width / 2, width / 2
    wall_material = str(recipe.get("wall_material", "primary"))
    header_material = str(recipe.get("header_material", wall_material))
    backdrop_material = str(recipe.get("backdrop_material", "glass"))
    opaque_roof = str(recipe.get("opaque_roof_material", "signature_roof"))
    glass_roof = str(recipe.get("glass_roof_material", "glass"))
    iron = str(recipe.get("iron_material", "signature_metal"))

    nodes: list[dict[str, Any]] = [
        {
            "id": "market_floor", "kind": "roof_slab", "size": [width, depth, 0.22],
            "location": [0.0, 0.0, 0.11], "material": "concrete", "bevel_m": 0.025,
        },
        {
            "id": "front_header", "kind": "box", "size": [width, 1.15, header_height],
            "location": [0.0, front_y + 0.575, column_height + header_height / 2],
            "material": header_material, "bevel_m": 0.055,
        },
        {
            "id": "rear_header", "kind": "box", "size": [width, 1.15, header_height],
            "location": [0.0, rear_y - 0.575, column_height + header_height / 2],
            "material": header_material, "bevel_m": 0.055,
        },
        {
            "id": "left_header", "kind": "box", "size": [1.15, depth - 2.3, header_height],
            "location": [left_x + 0.575, 0.0, column_height + header_height / 2],
            "material": header_material, "bevel_m": 0.055,
        },
        {
            "id": "right_header", "kind": "box", "size": [1.15, depth - 2.3, header_height],
            "location": [right_x - 0.575, 0.0, column_height + header_height / 2],
            "material": header_material, "bevel_m": 0.055,
        },
        {
            "id": "central_glass_nave", "kind": "gable_roof",
            "size": [central_width, depth, central_rise], "location": [0.0, 0.0, eave_z],
            "material": opaque_roof, "ridge_axis": "y", "bevel_m": 0.035,
        },
        {
            "id": "left_opaque_aisle", "kind": "gable_roof",
            "size": [side_width + 0.20, depth, side_rise],
            "location": [-(central_width + side_width) / 2, 0.0, eave_z],
            "material": opaque_roof, "ridge_axis": "y", "bevel_m": 0.045,
        },
        {
            "id": "right_opaque_aisle", "kind": "gable_roof",
            "size": [side_width + 0.20, depth, side_rise],
            "location": [(central_width + side_width) / 2, 0.0, eave_z],
            "material": opaque_roof, "ridge_axis": "y", "bevel_m": 0.045,
        },
        {
            "id": "cross_glass_nave", "kind": "gable_roof",
            "size": [width, cross_depth, cross_rise], "location": [0.0, 0.0, eave_z + 0.10],
            "material": opaque_roof, "ridge_axis": "x", "bevel_m": 0.035,
        },
    ]
    front_columns = int(recipe.get("front_column_count", 9))
    side_columns = int(recipe.get("side_column_count", 7))
    assemblies: list[dict[str, Any]] = [
        {
            "id": "front_market_columns", "kind": "column_array",
            "start": [left_x + 1.1, front_y + 0.28, 0.22],
            "end": [right_x - 1.1, front_y + 0.28, 0.22], "count": front_columns,
            "section": [0.82, 0.82], "height_m": eave_z - 0.22, "material": wall_material,
        },
        {
            "id": "rear_market_columns", "kind": "column_array",
            "start": [left_x + 1.1, rear_y - 0.28, 0.22],
            "end": [right_x - 1.1, rear_y - 0.28, 0.22], "count": front_columns,
            "section": [0.82, 0.82], "height_m": eave_z - 0.22, "material": wall_material,
        },
        {
            "id": "left_market_columns", "kind": "column_array",
            "start": [left_x + 0.28, front_y + 1.4, 0.22],
            "end": [left_x + 0.28, rear_y - 1.4, 0.22], "count": side_columns,
            "section": [0.82, 0.82], "height_m": eave_z - 0.22, "material": wall_material,
        },
        {
            "id": "right_market_columns", "kind": "column_array",
            "start": [right_x - 0.28, front_y + 1.4, 0.22],
            "end": [right_x - 0.28, rear_y - 1.4, 0.22], "count": side_columns,
            "section": [0.82, 0.82], "height_m": eave_z - 0.22, "material": wall_material,
        },
        {
            "id": "front_market_backdrop", "kind": "curtain_wall", "axis": "front",
            "centre": [0.0, front_y + 5.2, column_height / 2 + 0.25],
            "span_m": width - 8.0, "height_m": column_height - 0.5,
            "columns": front_columns - 1, "rows": 1, "frame_m": 0.10,
            "depth_m": 0.08, "frame_material": iron, "glass_material": backdrop_material,
            "interior_material": "interior_warm", "interior_recess_m": 0.20,
        },
        {
            "id": "rear_market_backdrop", "kind": "curtain_wall", "axis": "rear",
            "centre": [0.0, rear_y - 5.2, column_height / 2 + 0.25],
            "span_m": width - 8.0, "height_m": column_height - 0.5,
            "columns": front_columns - 1, "rows": 1, "frame_m": 0.10,
            "depth_m": 0.08, "frame_material": iron, "glass_material": backdrop_material,
            "interior_material": "interior_warm", "interior_recess_m": 0.20,
        },
        {
            "id": "left_market_backdrop", "kind": "curtain_wall", "axis": "left",
            "centre": [left_x + 5.2, 0.0, column_height / 2 + 0.25],
            "span_m": depth - 8.0, "height_m": column_height - 0.5,
            "columns": side_columns - 1, "rows": 1, "frame_m": 0.10,
            "depth_m": 0.08, "frame_material": iron, "glass_material": backdrop_material,
            "interior_material": "interior_warm", "interior_recess_m": 0.20,
        },
        {
            "id": "right_market_backdrop", "kind": "curtain_wall", "axis": "right",
            "centre": [right_x - 5.2, 0.0, column_height / 2 + 0.25],
            "span_m": depth - 8.0, "height_m": column_height - 0.5,
            "columns": side_columns - 1, "rows": 1, "frame_m": 0.10,
            "depth_m": 0.08, "frame_material": iron, "glass_material": backdrop_material,
            "interior_material": "interior_warm", "interior_recess_m": 0.20,
        },
        {
            "id": "central_front_clerestory", "kind": "gable_end_glazing", "axis": "front",
            "base_centre": [0.0, front_y - 0.04, eave_z], "width_m": central_width,
            "rise_m": central_rise, "head_style": "segmental_arch", "mullions": 7,
            "transoms": 3, "glass_material": "stained_glass", "frame_material": iron,
            "edge_material": wall_material,
        },
        {
            "id": "central_rear_clerestory", "kind": "gable_end_glazing", "axis": "rear",
            "base_centre": [0.0, rear_y + 0.04, eave_z], "width_m": central_width,
            "rise_m": central_rise, "head_style": "segmental_arch", "mullions": 7,
            "transoms": 3, "glass_material": "stained_glass", "frame_material": iron,
            "edge_material": wall_material,
        },
        {
            "id": "cross_left_clerestory", "kind": "gable_end_glazing", "axis": "left",
            "base_centre": [left_x - 0.04, 0.0, eave_z + 0.10], "width_m": cross_depth,
            "rise_m": cross_rise, "head_style": "segmental_arch", "mullions": 5,
            "transoms": 3, "glass_material": "stained_glass", "frame_material": iron,
            "edge_material": wall_material,
        },
        {
            "id": "cross_right_clerestory", "kind": "gable_end_glazing", "axis": "right",
            "base_centre": [right_x + 0.04, 0.0, eave_z + 0.10], "width_m": cross_depth,
            "rise_m": cross_rise, "head_style": "segmental_arch", "mullions": 5,
            "transoms": 3, "glass_material": "stained_glass", "frame_material": iron,
            "edge_material": wall_material,
        },
        {
            "id": "central_roof_iron", "kind": "pitched_roof_frame",
            "centre": [0.0, 0.0, eave_z], "size": [central_width, depth, central_rise],
            "ridge_axis": "y", "rafter_count": 12, "purlin_rows": 4,
            "material": iron, "profile_m": 0.11,
        },
        {
            "id": "cross_roof_iron", "kind": "pitched_roof_frame",
            "centre": [0.0, 0.0, eave_z + 0.10], "size": [width, cross_depth, cross_rise],
            "ridge_axis": "x", "rafter_count": 15, "purlin_rows": 4,
            "material": iron, "profile_m": 0.11,
        },
        {
            "id": "central_skylight_panels", "kind": "pitched_roof_surface_detail",
            "centre": [0.0, 0.0, eave_z], "size": [central_width, depth, central_rise],
            "ridge_axis": "y", "tile_material": "stained_glass",
            "rows": 7, "columns": 14, "tile_thickness_m": 0.026,
            "row_min_fraction": 0.18, "row_max_fraction": 0.72,
            "along_min_fraction": -0.46, "along_max_fraction": 0.46,
            "weight_enabled": False, "ridge_enabled": False,
            "gutter_enabled": False, "verge_enabled": False,
        },
        {
            "id": "cross_skylight_panels", "kind": "pitched_roof_surface_detail",
            "centre": [0.0, 0.0, eave_z + 0.10], "size": [width, cross_depth, cross_rise],
            "ridge_axis": "x", "tile_material": "stained_glass",
            "rows": 7, "columns": 14, "tile_thickness_m": 0.026,
            "row_min_fraction": 0.18, "row_max_fraction": 0.68,
            "along_min_fraction": -0.44, "along_max_fraction": 0.44,
            "weight_enabled": False, "ridge_enabled": False,
            "gutter_enabled": False, "verge_enabled": False,
        },
        {
            "id": "front_market_stalls", "kind": "market_stall_schedule", "axis": "front",
            "face_coordinate_m": front_y - 0.04, "base_z_m": 0.22,
            "positions_m": [
                left_x + (width - 2.2) * (index + 0.5) / (front_columns - 1)
                for index in range(front_columns - 1)
            ],
            "bay_width_m": (width - 4.0) / (front_columns - 1),
            "crate_count": 2, "produce_per_crate": 2, "light_count": 2,
        },
        {
            "id": "rear_market_stalls", "kind": "market_stall_schedule", "axis": "rear",
            "face_coordinate_m": rear_y + 0.04, "base_z_m": 0.22,
            "positions_m": [
                left_x + (width - 2.2) * (index + 0.5) / (front_columns - 1)
                for index in range(front_columns - 1)
            ],
            "bay_width_m": (width - 4.0) / (front_columns - 1),
            "crate_count": 2, "produce_per_crate": 2, "light_count": 2,
        },
        {
            "id": "left_market_stalls", "kind": "market_stall_schedule", "axis": "left",
            "face_coordinate_m": left_x - 0.04, "base_z_m": 0.22,
            "positions_m": [
                front_y + (depth - 2.8) * (index + 0.5) / (side_columns - 1)
                for index in range(side_columns - 1)
            ],
            "bay_width_m": (depth - 4.6) / (side_columns - 1),
            "crate_count": 2, "produce_per_crate": 2, "light_count": 2,
        },
        {
            "id": "right_market_stalls", "kind": "market_stall_schedule", "axis": "right",
            "face_coordinate_m": right_x + 0.04, "base_z_m": 0.22,
            "positions_m": [
                front_y + (depth - 2.8) * (index + 0.5) / (side_columns - 1)
                for index in range(side_columns - 1)
            ],
            "bay_width_m": (depth - 4.6) / (side_columns - 1),
            "crate_count": 2, "produce_per_crate": 2, "light_count": 2,
        },
        {
            "id": "front_market_awnings", "kind": "awning_schedule", "axis": "front",
            "face_coordinate_m": front_y - 0.10, "base_z_m": 3.0,
            "positions_m": [
                left_x + (width - 2.2) * (index + 0.5) / (front_columns - 1)
                for index in range(front_columns - 1)
            ],
            "width_m": (width - 4.0) / (front_columns - 1) * 0.72,
            "projection_m": 2.3, "drop_m": 0.42,
            "materials": ["awning_red", "awning_yellow", "awning_blue"],
        },
        {
            "id": "rear_market_awnings", "kind": "awning_schedule", "axis": "rear",
            "face_coordinate_m": rear_y + 0.10, "base_z_m": 3.0,
            "positions_m": [
                left_x + (width - 2.2) * (index + 0.5) / (front_columns - 1)
                for index in range(front_columns - 1)
            ],
            "width_m": (width - 4.0) / (front_columns - 1) * 0.72,
            "projection_m": 2.3, "drop_m": 0.42,
            "materials": ["awning_blue", "awning_yellow", "awning_red"],
        },
        {
            "id": "left_market_awnings", "kind": "awning_schedule", "axis": "left",
            "face_coordinate_m": left_x - 0.10, "base_z_m": 3.0,
            "positions_m": [
                front_y + (depth - 2.8) * (index + 0.5) / (side_columns - 1)
                for index in range(side_columns - 1)
            ],
            "width_m": (depth - 4.6) / (side_columns - 1) * 0.72,
            "projection_m": 2.3, "drop_m": 0.42,
            "materials": ["awning_yellow", "awning_red", "awning_blue"],
        },
        {
            "id": "right_market_awnings", "kind": "awning_schedule", "axis": "right",
            "face_coordinate_m": right_x + 0.10, "base_z_m": 3.0,
            "positions_m": [
                front_y + (depth - 2.8) * (index + 0.5) / (side_columns - 1)
                for index in range(side_columns - 1)
            ],
            "width_m": (depth - 4.6) / (side_columns - 1) * 0.72,
            "projection_m": 2.3, "drop_m": 0.42,
            "materials": ["awning_red", "awning_blue", "awning_yellow"],
        },
    ]
    for index, centre_x in enumerate((-(central_width + side_width) / 2, (central_width + side_width) / 2)):
        assemblies.append({
            "id": f"opaque_roof_detail_{index}", "kind": "pitched_roof_surface_detail",
            "centre": [centre_x, 0.0, eave_z],
            "size": [side_width + 0.20, depth, side_rise], "ridge_axis": "y",
            "tile_material": opaque_roof, "ridge_material": "roof_flashing",
            "verge_material": iron, "rows": 9, "columns": 20,
            "tile_thickness_m": 0.035, "weight_enabled": False,
            "gutter_enabled": True, "verge_enabled": True,
        })

    front_void_depth = 5.0
    voids = [
        {
            "id": "front_open_market_bays", "shape": "open_perimeter_bays", "axis": "front",
            "size": [width - 2.2, front_void_depth, column_height],
            "location": [0.0, front_y + front_void_depth / 2, column_height / 2],
            "purpose": "reference-visible open produce-stall frontage",
        },
        {
            "id": "rear_open_market_bays", "shape": "open_perimeter_bays", "axis": "rear",
            "size": [width - 2.2, front_void_depth, column_height],
            "location": [0.0, rear_y - front_void_depth / 2, column_height / 2],
            "purpose": "permeable rear market frontage",
        },
        {
            "id": "left_open_market_bays", "shape": "open_perimeter_bays", "axis": "left",
            "size": [front_void_depth, depth - 2.8, column_height],
            "location": [left_x + front_void_depth / 2, 0.0, column_height / 2],
            "purpose": "permeable side market frontage",
        },
        {
            "id": "right_open_market_bays", "shape": "open_perimeter_bays", "axis": "right",
            "size": [front_void_depth, depth - 2.8, column_height],
            "location": [right_x - front_void_depth / 2, 0.0, column_height / 2],
            "purpose": "permeable side market frontage",
        },
    ]
    return {
        "schema": "massing-graph@1", "profile": str(recipe["profile"]),
        "description": str(recipe["description"]),
        "reference_views": deepcopy(recipe.get("reference_views") or []),
        "height_m": eave_z + max(central_rise, cross_rise),
        "reference_dimensions": {
            "width_m": width, "depth_m": depth, "floors": 1,
            "floor_height_m": eave_z,
        },
        "nodes": nodes, "voids": voids, "assemblies": assemblies,
        "presentation_camera": deepcopy(recipe.get("presentation_camera") or {}),
        "target_views": ["archetype_match", "street", "front_corner_oblique", "aerial", "roof_audit"],
        "recipe_contract": {
            "kind": "multi_aisle_market_hall", "front_open_bays": front_columns - 1,
            "side_open_bays": side_columns - 1,
            "footprint_projection_allowance_m": 5.2,
            "roof_node_ids": [
                "central_glass_nave", "left_opaque_aisle", "right_opaque_aisle", "cross_glass_nave",
            ],
        },
    }


def _beaux_arts_trainshed_terminal(recipe: dict[str, Any], dims: dict[str, Any]) -> dict[str, Any]:
    """Compile an image-locked limestone headhouse and open glazed trainshed.

    The terminal is deliberately split into stable modules: a repeated arched
    headhouse, a fixed clock-tower landmark, and a separately framed barrel
    vault.  No opaque roof is placed below the trainshed glazing.
    """
    width = float(dims["width_m"])
    depth = float(dims["depth_m"])
    front_y, rear_y = -depth / 2, depth / 2
    headhouse_depth = float(recipe.get("headhouse_depth_m", depth * 0.32))
    wall_height = float(recipe.get("headhouse_height_m", 20.0))
    ground_height = float(recipe.get("ground_height_m", 7.0))
    upper_height = wall_height - ground_height
    facade_depth = float(recipe.get("facade_depth_m", 2.4))
    facade_y = front_y + facade_depth / 2
    inner_y = front_y + headhouse_depth
    stone = str(recipe.get("stone_material", "primary"))
    trim = str(recipe.get("trim_material", "signature_stone"))
    iron = str(recipe.get("iron_material", "signature_metal"))
    glass = str(recipe.get("glass_material", "glass"))
    roof_glass = str(recipe.get("roof_glass_material", glass))
    brick = str(recipe.get("brick_material", "secondary"))
    roof_metal = str(recipe.get("roof_material", "signature_roof"))
    stone_patina = str(recipe.get("stone_patina_material", trim))
    headhouse_roof = str(recipe.get("headhouse_roof_material", trim))

    ground_count = int(recipe.get("ground_arch_count", 9))
    upper_count = int(recipe.get("upper_arch_count", 5))
    ground_width = float(recipe.get("ground_arch_width_m", 4.6))
    upper_width = float(recipe.get("upper_arch_width_m", 9.2))
    ground_opening_height = float(recipe.get("ground_opening_height_m", 6.2))
    upper_opening_height = float(recipe.get("upper_opening_height_m", 11.3))
    ground_spring = ground_opening_height - ground_width / 2
    upper_spring = upper_opening_height - upper_width / 2
    ground_margin = max(0.55, ground_width * 0.42)
    ground_usable = width - ground_margin * 2
    ground_bay = ground_usable / ground_count
    ground_centres = [
        -ground_usable / 2 + ground_bay * (index + 0.5)
        for index in range(ground_count)
    ]

    shed_width = float(recipe.get("shed_width_m", width * 0.63))
    shed_front_y = inner_y - float(recipe.get("shed_overlap_m", 1.4))
    shed_depth = rear_y - shed_front_y
    shed_eave = float(recipe.get("shed_eave_height_m", 10.2))
    shed_rise = float(recipe.get("shed_rise_m", 13.5))
    shed_centre_y = (shed_front_y + rear_y) / 2
    side_wall = float(recipe.get("shed_wall_thickness_m", 1.25))
    clock_x = float(recipe.get("clock_tower_x_m", width * 0.30))
    clock_y = float(recipe.get("clock_tower_y_m", front_y + headhouse_depth * 0.58))
    clock_width = float(recipe.get("clock_tower_width_m", 7.2))
    clock_height = float(recipe.get("clock_tower_height_m", 14.5))

    nodes: list[dict[str, Any]] = [
        {
            "id": "terminal_floor", "kind": "roof_slab",
            "size": [width, depth, 0.28], "location": [0.0, 0.0, 0.14],
            "material": "concrete", "bevel_m": 0.025,
        },
        {
            "id": "ground_arcade", "kind": "opening_block",
            "size": [width, facade_depth, ground_height],
            "location": [0.0, facade_y, ground_height / 2],
            "material": stone, "lining_material": trim, "trim_material": trim,
            "opening_shape": "round_arch", "opening_count": ground_count,
            "opening_width_m": ground_width, "opening_base_m": 0.18,
            "opening_height_m": ground_opening_height, "spring_height_m": ground_spring,
            "section_mode": "through", "trim_profile_m": 0.24,
            "trim_depth_m": facade_depth, "bevel_m": 0.055,
        },
        {
            "id": "upper_arcade", "kind": "opening_block",
            "size": [width, facade_depth, upper_height],
            "location": [0.0, facade_y, ground_height + upper_height / 2],
            "material": stone, "lining_material": trim, "trim_material": trim,
            "back_glass_material": glass, "back_frame_material": iron,
            "back_enabled": False,
            "opening_shape": "round_arch", "opening_count": upper_count,
            "opening_width_m": upper_width, "opening_base_m": 0.50,
            "opening_height_m": upper_opening_height, "spring_height_m": upper_spring,
            "section_mode": "recessed", "trim_profile_m": 0.42,
            "trim_depth_m": facade_depth, "bevel_m": 0.065,
        },
        {
            "id": "headhouse_rear_wall", "kind": "box",
            "size": [width, 1.1, wall_height],
            "location": [0.0, inner_y - 0.55, wall_height / 2],
            "material": stone, "bevel_m": 0.06,
        },
        {
            "id": "headhouse_left_return", "kind": "box",
            "size": [2.0, headhouse_depth - facade_depth, wall_height],
            "location": [-width / 2 + 1.0, front_y + facade_depth + (headhouse_depth - facade_depth) / 2, wall_height / 2],
            "material": stone, "bevel_m": 0.06,
        },
        {
            "id": "headhouse_right_return", "kind": "box",
            "size": [2.0, headhouse_depth - facade_depth, wall_height],
            "location": [width / 2 - 1.0, front_y + facade_depth + (headhouse_depth - facade_depth) / 2, wall_height / 2],
            "material": stone, "bevel_m": 0.06,
        },
        {
            "id": "headhouse_mid_floor", "kind": "roof_slab",
            "size": [width - 3.5, headhouse_depth - 2.5, 0.38],
            "location": [0.0, front_y + headhouse_depth / 2, ground_height + 0.05],
            "material": trim, "bevel_m": 0.035,
        },
        {
            "id": "headhouse_roof", "kind": "roof_slab",
            "size": [width + 0.7, headhouse_depth + 0.6, 0.55],
            "location": [0.0, front_y + headhouse_depth / 2, wall_height + 0.275],
            "material": headhouse_roof, "bevel_m": 0.055,
        },
        {
            "id": "headhouse_rear_parapet", "kind": "box",
            "size": [width + 0.2, 0.42, 1.35],
            "location": [0.0, inner_y - 0.21, wall_height + 0.675],
            "material": stone_patina, "bevel_m": 0.045,
        },
        {
            "id": "headhouse_left_parapet", "kind": "box",
            "size": [0.42, headhouse_depth, 1.35],
            "location": [-width / 2 + 0.21, front_y + headhouse_depth / 2, wall_height + 0.675],
            "material": stone_patina, "bevel_m": 0.045,
        },
        {
            "id": "headhouse_right_parapet", "kind": "box",
            "size": [0.42, headhouse_depth, 1.35],
            "location": [width / 2 - 0.21, front_y + headhouse_depth / 2, wall_height + 0.675],
            "material": stone_patina, "bevel_m": 0.045,
        },
        {
            "id": "shed_left_wall", "kind": "box",
            "size": [side_wall, shed_depth, shed_eave],
            "location": [-shed_width / 2 + side_wall / 2, shed_centre_y, shed_eave / 2],
            "material": brick, "bevel_m": 0.055,
        },
        {
            "id": "shed_right_wall", "kind": "box",
            "size": [side_wall, shed_depth, shed_eave],
            "location": [shed_width / 2 - side_wall / 2, shed_centre_y, shed_eave / 2],
            "material": brick, "bevel_m": 0.055,
        },
        {
            "id": "clock_tower_core", "kind": "box",
            "size": [clock_width, clock_width, clock_height],
            "location": [clock_x, clock_y, wall_height + clock_height / 2 - 0.3],
            "material": stone, "bevel_m": 0.08,
        },
        {
            "id": "clock_tower_cornice", "kind": "roof_slab",
            "size": [clock_width + 1.15, clock_width + 1.15, 0.55],
            "location": [clock_x, clock_y, wall_height + clock_height - 0.10],
            "material": trim, "bevel_m": 0.05,
        },
        {
            "id": "clock_tower_lower_belt", "kind": "roof_slab",
            "size": [clock_width + 0.42, clock_width + 0.42, 0.24],
            "location": [clock_x, clock_y, wall_height + clock_height * 0.34],
            "material": stone_patina, "bevel_m": 0.035,
        },
        {
            "id": "clock_tower_upper_belt", "kind": "roof_slab",
            "size": [clock_width + 0.54, clock_width + 0.54, 0.28],
            "location": [clock_x, clock_y, wall_height + clock_height * 0.74],
            "material": stone_patina, "bevel_m": 0.035,
        },
        {
            "id": "clock_tower_cupola", "kind": "hipped_roof",
            "size": [clock_width + 0.25, clock_width + 0.25, 2.8],
            "location": [clock_x, clock_y, wall_height + clock_height + 0.18],
            "material": roof_metal, "ridge_axis": "x", "ridge_inset_m": 2.3,
            "bevel_m": 0.045,
        },
    ]

    assemblies: list[dict[str, Any]] = [
        {
            "id": "trainshed_barrel_glazing", "kind": "barrel_vault_glazing",
            "centre": [0.0, shed_centre_y, shed_eave], "span_m": shed_width,
            "depth_m": shed_depth, "rise_m": shed_rise,
            "glass_depth_fraction": float(recipe.get("glass_depth_fraction", 0.58)),
            "front_cap_fraction": float(recipe.get("front_cap_fraction", 0.21)),
            "segments": 36, "rib_count": 8, "purlin_count": 13,
            "glass_material": roof_glass, "frame_material": iron,
            "cap_material": roof_metal, "profile_m": 0.18,
        },
        {
            "id": "shed_front_arch_glazing", "kind": "gable_end_glazing", "axis": "front",
            "base_centre": [0.0, shed_front_y - 0.07, shed_eave],
            "width_m": shed_width - 2.2, "rise_m": shed_rise,
            "head_style": "segmental_arch", "mullions": 11, "transoms": 5,
            "glass_material": roof_glass, "frame_material": iron, "edge_material": brick,
        },
        {
            "id": "shed_rear_arch_glazing", "kind": "gable_end_glazing", "axis": "rear",
            "base_centre": [0.0, rear_y + 0.07, shed_eave],
            "width_m": shed_width - 2.2, "rise_m": shed_rise,
            "head_style": "segmental_arch", "mullions": 11, "transoms": 5,
            "glass_material": roof_glass, "frame_material": iron, "edge_material": brick,
        },
        {
            "id": "clock_faces", "kind": "clock_face_array",
            "centre": [clock_x, clock_y, wall_height + clock_height * 0.61],
            "tower_width_m": clock_width, "diameter_m": clock_width * 0.64,
            "face_material": "clock_face", "hand_material": iron,
        },
        {
            "id": "front_cornice_corbel_course", "kind": "corbel_array", "axis": "front",
            "centre": [0.0, front_y - 0.08, 0.0], "span_m": width - 1.0,
            "levels_z": [wall_height - 1.05, wall_height - 0.55], "count": 44,
            "depth_m": 0.36, "height_m": 0.22, "material": stone_patina,
        },
        {
            "id": "front_balustrade_posts", "kind": "column_array",
            "start": [-width / 2 + 1.2, front_y + 0.20, wall_height + 0.55],
            "end": [width / 2 - 1.2, front_y + 0.20, wall_height + 0.55],
            "count": 38, "section": [0.18, 0.18], "height_m": 1.15,
            "material": trim, "bevel_m": 0.018,
        },
        {
            "id": "front_balustrade_rail", "kind": "shadow_line", "axis": "front",
            "centre": [0.0, front_y + 0.18, wall_height + 1.70],
            "span_m": width - 0.8, "height_m": 0.28, "depth_m": 0.42,
            "material": trim,
        },
        {
            "id": "interior_concourse", "kind": "station_concourse",
            "centre": [0.0, front_y + headhouse_depth * 0.56, 0.28],
            "width_m": width - 8.0, "depth_m": headhouse_depth - 5.0,
            "height_m": ground_height - 0.55, "bay_count": ground_count,
            "structure_material": iron, "interior_material": "interior_warm",
        },
        {
            "id": "upper_headhouse_depth", "kind": "station_concourse",
            "centre": [0.0, front_y + 6.3, ground_height + 0.42],
            "width_m": width - 7.0, "depth_m": 7.0,
            "height_m": upper_height - 1.0, "bay_count": upper_count,
            "structure_material": iron, "interior_material": "glazing_interior_1",
            "floor_material": trim,
        },
        {
            "id": "recessed_entry_doors", "kind": "punched_opening_schedule",
            "axis": "front", "face_coordinate_m": front_y + 6.4,
            "openings": [
                {
                    "type": "door", "along_m": centre, "base_z_m": 0.24,
                    "width_m": ground_width * 0.70, "height_m": 4.9,
                    "depth_m": 0.18, "frame_m": 0.13,
                    "transom_height_m": 1.05, "panel_rows": 2, "panel_columns": 2
                }
                for centre in ground_centres
            ],
            "frame_material": iron, "door_material": "signature_door",
            "glass_material": glass,
        },
        {
            "id": "upper_order_pilasters", "kind": "column_array",
            "start": [-width / 2 + 3.6, front_y - 0.22, ground_height + 0.05],
            "end": [width / 2 - 3.6, front_y - 0.22, ground_height + 0.05],
            "count": upper_count + 1, "section": [0.86, 0.74],
            "height_m": upper_height - 0.25, "material": trim, "bevel_m": 0.035,
        },
        {
            "id": "ground_upper_division_band", "kind": "shadow_line", "axis": "front",
            "centre": [0.0, front_y - 0.30, ground_height + 0.13],
            "span_m": width + 0.40, "height_m": 0.42, "depth_m": 0.72,
            "material": trim,
        },
        {
            "id": "shed_left_window_schedule", "kind": "punched_opening_schedule",
            "axis": "left", "face_coordinate_m": -shed_width / 2 - 0.075,
            "openings": [
                {"type": "window", "along_m": shed_front_y + 4.5 + index * (shed_depth - 9.0) / 4,
                 "base_z_m": 2.0, "width_m": 4.2, "height_m": 6.2,
                 "columns": 2, "rows": 3, "reveal_m": 0.16, "surround_m": 0.12,
                 "interior_recess_m": 0.30}
                for index in range(5)
            ],
            "frame_material": iron, "surround_material": brick,
            "glass_material": glass, "interior_material": "glazing_interior_2",
            "minimum_rows": 3,
        },
        {
            "id": "shed_right_window_schedule", "kind": "punched_opening_schedule",
            "axis": "right", "face_coordinate_m": shed_width / 2 + 0.075,
            "openings": [
                {"type": "window", "along_m": shed_front_y + 4.5 + index * (shed_depth - 9.0) / 4,
                 "base_z_m": 2.0, "width_m": 4.2, "height_m": 6.2,
                 "columns": 2, "rows": 3, "reveal_m": 0.16, "surround_m": 0.12,
                 "interior_recess_m": 0.30}
                for index in range(5)
            ],
            "frame_material": iron, "surround_material": brick,
            "glass_material": glass, "interior_material": "glazing_interior_3",
            "minimum_rows": 3,
        },
        {
            "id": "clock_front_finials", "kind": "pinnacle_array", "axis": "front",
            "base_centre": [clock_x, clock_y - clock_width / 2, wall_height + clock_height + 0.36],
            "span_m": clock_width - 0.7, "count": 2, "shaft_height_m": 0.72,
            "cap_height_m": 0.48, "radius_m": 0.16, "material": trim,
        },
        {
            "id": "clock_rear_finials", "kind": "pinnacle_array", "axis": "rear",
            "base_centre": [clock_x, clock_y + clock_width / 2, wall_height + clock_height + 0.36],
            "span_m": clock_width - 0.7, "count": 2, "shaft_height_m": 0.72,
            "cap_height_m": 0.48, "radius_m": 0.16, "material": trim,
        },
    ]
    for index in range(1, 10):
        assemblies.append({
            "id": f"rustication_joint_{index:02d}", "kind": "shadow_line", "axis": "front",
            "centre": [0.0, front_y - 0.025, 0.62 * index], "span_m": width - 0.25,
            "height_m": 0.045, "depth_m": 0.055, "material": "massing_joint",
        })

    return {
        "schema": "massing-graph@1", "profile": str(recipe["profile"]),
        "description": str(recipe["description"]),
        "reference_views": deepcopy(recipe.get("reference_views") or []),
        "height_m": wall_height + clock_height + 3.0,
        "reference_dimensions": {
            "width_m": width, "depth_m": depth, "floors": 3,
            "floor_height_m": ground_height,
        },
        "nodes": nodes, "voids": [
            {
                "id": "ground_arcade_tunnels", "shape": "round_arch_passage", "axis": "front",
                "size": [width - 5.0, headhouse_depth, ground_opening_height],
                "location": [0.0, front_y + headhouse_depth / 2, ground_opening_height / 2],
                "purpose": "nine image-confirmed recessed entrance tunnels into the concourse",
            },
            {
                "id": "open_trainshed_volume", "shape": "barrel_vault_interior",
                "size": [shed_width - side_wall * 2, shed_depth, shed_eave + shed_rise],
                "location": [0.0, shed_centre_y, (shed_eave + shed_rise) / 2],
                "purpose": "unblocked volume below physical glass and iron roof",
            },
        ],
        "assemblies": assemblies,
        "presentation_camera": deepcopy(recipe.get("presentation_camera") or {}),
        "target_views": ["archetype_match", "street", "front_corner_oblique", "aerial", "roof_audit"],
        "recipe_contract": {
            "kind": "beaux_arts_trainshed_terminal", "ground_arches": ground_count,
            "upper_arches": upper_count, "roof_node_ids": ["trainshed_barrel_glazing"],
        },
    }


def compile_massing_recipe(recipe: dict[str, Any], dimensions: dict[str, Any]) -> dict[str, Any]:
    kind = str(recipe.get("kind", ""))
    if kind == "front_opening_landmark":
        return _front_opening_landmark(deepcopy(recipe), dimensions)
    if kind == "courtyard_passage":
        return _courtyard_passage(deepcopy(recipe), dimensions)
    if kind == "stepped_gable_house":
        return _stepped_gable_house(deepcopy(recipe), dimensions)
    if kind == "multi_aisle_market_hall":
        return _multi_aisle_market_hall(deepcopy(recipe), dimensions)
    if kind == "beaux_arts_trainshed_terminal":
        return _beaux_arts_trainshed_terminal(deepcopy(recipe), dimensions)
    raise ValueError(f"unsupported massing recipe kind {kind!r}")
