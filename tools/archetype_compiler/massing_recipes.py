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


def compile_massing_recipe(recipe: dict[str, Any], dimensions: dict[str, Any]) -> dict[str, Any]:
    kind = str(recipe.get("kind", ""))
    if kind == "front_opening_landmark":
        return _front_opening_landmark(deepcopy(recipe), dimensions)
    if kind == "courtyard_passage":
        return _courtyard_passage(deepcopy(recipe), dimensions)
    raise ValueError(f"unsupported massing recipe kind {kind!r}")
