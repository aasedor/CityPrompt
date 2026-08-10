"""Re-author the V87 ten-building checkpoint with mandatory V88 stage gates.

V87 remains the evidence and material baseline.  V88 replaces the weak graph
decisions, records a complete quality-first workflow, and emits two finite
five-building registries for the existing Blender runner.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math
from pathlib import Path
from typing import Any

from compile_catalogue_round_v87 import (
    REPO,
    TARGETS,
    TOOLS,
    build_profile,
    read_json,
    write_json,
)


DRAFTS = TOOLS / "catalogue_round_v87_authoring_drafts"
PROFILE = TOOLS / "architectural_signature_profiles.d/catalogue_round_v88.json"
RECIPES = TOOLS / "catalogue_round_v88_surface_recipes.json"
BATCH_A = TOOLS / "catalogue_round_v88_batch_a.json"
BATCH_B = TOOLS / "catalogue_round_v88_batch_b.json"
REPAIR_A = TOOLS / "catalogue_round_v88_repair_a.json"
REPAIR_B = TOOLS / "catalogue_round_v88_repair_b.json"
TERRACOTTA_RETRY = TOOLS / "catalogue_round_v88_terracotta_retry.json"
CATALAN_RETRY = TOOLS / "catalogue_round_v88_catalan_retry.json"
CATALAN_STICKER_RETRY = TOOLS / "catalogue_round_v88_catalan_sticker_retry.json"
MOORISH_STICKER_RETRY = TOOLS / "catalogue_round_v88_moorish_sticker_retry.json"
CATALAN_STICKER_MASKS = REPO / "artifacts/catalogue-rollout-v88/round-001/sticker-masks/med_arcade_catalan_modernista"
CATALAN_MULTIVIEW = REPO / "artifacts/catalogue-rollout-v88/round-001/multiview-references/med_arcade_catalan_modernista"
CATALAN_SIDE_STICKER = CATALAN_MULTIVIEW / "left-elevation-wall-sticker-v1.png"
CATALAN_REAR_STICKER = CATALAN_MULTIVIEW / "rear-elevation-wall-sticker-v1.png"
MOORISH_SHEETS = REPO / "artifacts/catalogue-rollout-v87/round-001/facade-sheets/med_arcade_moorish"
MOORISH_PODIUM_STICKER = MOORISH_SHEETS / "podium_albedo.jpg"
MOORISH_CROWN_STICKER = MOORISH_SHEETS / "crown_albedo.jpg"
DIMENSION_OVERRIDES = {
    "glass_office_dark_frame": {
        "width_m": 28.0,
        "depth_m": 20.0,
        "default_floors": 6,
    },
    "modernist_civic_white_corbusian": {
        "width_m": 36.0,
        "depth_m": 23.0,
        "default_floors": 5,
    },
    "modernist_civic_precast_panel": {
        "width_m": 26.0,
        "depth_m": 22.0,
        "default_floors": 5,
    },
    "glass_office_terracotta_fins": {
        "width_m": 32.0,
        "depth_m": 22.0,
        "default_floors": 4,
        "min_floors": 4,
    },
    "nordic_timber_charred_wood": {
        "width_m": 12.0,
        "depth_m": 14.0,
        "default_floors": 3,
    },
    "med_arcade_catalan_modernista": {
        "width_m": 14.0,
        "depth_m": 31.0,
        "default_floors": 6,
    },
}
GLASS_PROFILE_OVERRIDES = {
    "glass_office_terracotta_fins": "office_clear_occupied",
    "glass_office_dark_frame": "office_clear_occupied",
}


def box(node_id: str, size: list[float], location: list[float], material: str, bevel: float = 0.04) -> dict[str, Any]:
    return {"id": node_id, "kind": "box", "size": size, "location": location, "material": material, "bevel_m": bevel}


def skin(skin_id: str, axis: str, centre: list[float], span: float, height: float, band: str = "elevation", *, flip: bool = False) -> dict[str, Any]:
    return {"id": skin_id, "kind": "facade_skin", "axis": axis, "centre": centre, "span_m": span, "height_m": height, "depth_m": 0.045, "band": band, "flip_u": flip}


def stage_workflow(representation: str) -> dict[str, Any]:
    deliverables = {
        "reference_sufficiency": "reference-sufficiency.json",
        "representation_selection": "representation-selection.json",
        "clay_massing": "clay-comparison.png",
        "roof_and_voids": "roof-void-comparison.png",
        "medium_detail": "medium-detail-comparison.png",
        "retopology": "mesh-audit.json",
        "manual_uv_audit": "uv-audit.json",
        "material_bake": "surface-finish-report.json",
        "export_parity": "neutral-source-vs-glb.png",
        "architect_review": "architect-review.json",
    }
    return {
        "representation": representation,
        "required_stages": {
            key: {"deliverable": value, "approval_required": True}
            for key, value in deliverables.items()
        },
        "architect_review_views": ["street", "oblique", "roof", "side", "rear", "close_up"],
        "architect_release_score": 85,
        "hard_stops_block_release": True,
    }


def glazing(assembly_id: str, axis: str, centre: list[float], span: float, height: float, columns: int, rows: int, *, profile: str = "residential_low_e") -> dict[str, Any]:
    return {
        "id": assembly_id, "kind": "glazing_overlay", "axis": axis,
        "centre": centre, "span_m": span, "height_m": height, "depth_m": 0.04,
        "band": "elevation", "columns": columns, "rows": rows,
        "glass_profile": profile, "frame_mode": "mask_only",
        "opening_returns": False, "pane_recess_m": 0.20,
        "cavity_depth_m": 0.48, "room_card_recess_m": 0.12,
        "max_regions": max(6, columns * min(rows, 2)),
    }


def frame_grid(assembly_id: str, axis: str, centre: list[float], span: float, height: float, columns: int, rows: int, material: str, profile: float, depth: float) -> dict[str, Any]:
    return {
        "id": assembly_id, "kind": "frame_grid", "axis": axis,
        "centre": centre, "span_m": span, "height_m": height,
        "columns": columns, "rows": rows, "material": material,
        "profile_m": profile, "depth_m": depth,
        "edge_profile_multiplier": 1.18,
    }


def federal(graph: dict[str, Any], production: dict[str, Any]) -> None:
    nodes = [node for node in graph["nodes"] if not node["id"].startswith("federal_lintel_") and node["id"] not in {"main_mass", "federal_entry_left", "federal_entry_right", "federal_entry_head"}]
    nodes += [
        box("federal_left_mass", [7.35, 11.5, 9.6], [-5.325, -3.25, 4.8], "primary"),
        box("federal_right_mass", [7.35, 11.5, 9.6], [5.325, -3.25, 4.8], "primary"),
        box("federal_entry_bridge", [3.3, 11.5, 5.8], [0.0, -3.25, 6.7], "primary"),
        {
            "id": "federal_entry_arch", "kind": "opening_block", "size": [3.3, 2.2, 4.0],
            "location": [0.0, -7.9, 2.0], "material": "primary", "opening_shape": "round_arch",
            "opening_count": 1, "opening_width_m": 1.95, "opening_base_m": 0.05,
            "opening_height_m": 3.25, "spring_height_m": 2.28, "side_margin_m": 0.58,
            "section_mode": "recessed", "lining_material": "secondary",
            "trim_material": "secondary", "back_material": "signature_door",
            "trim_profile_m": 0.16, "trim_depth_m": 0.22,
        },
    ]
    graph["nodes"] = nodes
    graph["assemblies"] = [
        assembly for assembly in graph["assemblies"]
        if assembly["id"] not in {"front_skin_storey_00_glazing", "front_skin_storey_01_glazing"}
    ]
    for assembly in graph["assemblies"]:
        if assembly["id"] == "front_skin_storey_00":
            assembly["opening_clearances"] = [{
                "void_id": "federal_entry_void", "centre_m": 0.0,
                "base_z_m": 0.05, "width_m": 1.95, "height_m": 3.10,
            }]
        elif assembly["id"] == "front_skin_storey_01":
            assembly["opening_clearances"] = [{
                "void_id": "federal_entry_void", "centre_m": 0.0,
                "base_z_m": 3.21, "width_m": 1.95, "height_m": 0.08,
            }]
    graph.setdefault("voids", []).append({"id": "federal_entry_void", "shape": "round_arch_passage", "axis": "front", "size": [1.95, 2.2, 3.25], "location": [0, -7.9, 1.65], "purpose": "deep ceremonial entry"})
    production["spatial_voids"] = {"required_passages": [{
        "void_id": "federal_entry_void", "target_node_id": "federal_entry_arch",
        "target_node_kind": "opening_block", "shape": "round_arch_passage",
        "section_mode": "recessed", "minimum_depth_m": 2.0,
    }]}


def greystone(graph: dict[str, Any], production: dict[str, Any]) -> None:
    nodes = [node for node in graph["nodes"] if "bay_window" not in node["id"] and not node["id"].startswith("balcony_")]
    graph["nodes"] = nodes
    front_y = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in nodes if "size" in node)
    graph["assemblies"] = [
        assembly for assembly in graph["assemblies"]
        if not (
            assembly.get("axis") == "front"
            and assembly.get("kind") in {"facade_skin", "glazing_overlay"}
        )
    ]
    # The archetype is organized by two broad, genuinely projecting two-storey
    # iron bays.  The V88-a draft incorrectly abstracted these into three flat
    # vertical strips, which changed the building's identity even though the
    # palette and storey count were correct.
    for index, x in enumerate((-4.5, 4.5)):
        graph["nodes"].append(
            box(f"greystone_bay_mass_{index}", [4.15, 1.05, 6.4], [x, front_y - 0.50, 6.55], "secondary", 0.12)
        )
        graph["assemblies"].append({
            "id": f"greystone_true_bay_{index}", "kind": "curtain_wall", "axis": "front",
            "centre": [x, front_y - 1.04, 6.55], "span_m": 3.55, "height_m": 5.72,
            "columns": 3, "rows": 2, "frame_m": 0.085, "depth_m": 0.14,
            "reveal_m": 0.12, "surround_m": 0.18, "surround_depth_m": 0.28,
            "glass_material": "glass", "frame_material": "secondary",
            "surround_material": "primary", "interior_material": "interior_warm",
            "interior_recess_m": 0.42,
        })
        graph["assemblies"].append({
            "id": f"greystone_bay_semantic_{index}", "kind": "facade_skin", "axis": "front",
            "centre": [x, front_y - 1.13, 6.55], "span_m": 3.55, "height_m": 5.72,
            "depth_m": 0.045, "band": "elevation",
            "uv_u_min": 0.055 if index == 0 else 0.60,
            "uv_u_max": 0.40 if index == 0 else 0.945,
            "uv_v_min": 0.22, "uv_v_max": 0.78,
        })
        # Glazed returns make the bay read as a volume in oblique and side
        # evidence views instead of a dark rectangle pasted onto the wall.
        for side, axis, side_x in (
            ("left", "left", x - 2.08),
            ("right", "right", x + 2.08),
        ):
            graph["assemblies"].append({
                "id": f"greystone_bay_{index}_{side}_return", "kind": "curtain_wall", "axis": axis,
                "centre": [side_x, front_y - 0.50, 6.55], "span_m": 0.84, "height_m": 5.72,
                "columns": 1, "rows": 2, "frame_m": 0.07, "depth_m": 0.10,
                "reveal_m": 0.06, "surround_m": 0.10, "surround_depth_m": 0.16,
                "glass_material": "glass", "frame_material": "secondary",
                "surround_material": "primary", "interior_material": "interior_warm",
                "interior_recess_m": 0.28,
            })
        graph["nodes"] += [
            box(f"greystone_bay_{index}_waist", [3.92, 0.16, 0.34], [x, front_y - 1.13, 6.50], "secondary", 0.025),
            box(f"greystone_bay_{index}_crown", [4.18, 0.24, 0.28], [x, front_y - 1.11, 9.62], "secondary", 0.025),
        ]
    graph["assemblies"].append({
        "id": "greystone_ground_openings", "kind": "punched_opening_schedule",
        "axis": "front", "face_coordinate_m": front_y - 0.32,
        "frame_material": "secondary", "surround_material": "primary",
        "glass_material": "glass", "interior_material": "interior_warm",
        "door_material": "signature_door",
        "openings": [
            {"along_m": -6.6, "base_z_m": 0.65, "width_m": 1.55, "height_m": 2.25},
            {"along_m": -3.3, "base_z_m": 0.65, "width_m": 1.55, "height_m": 2.25},
            {"along_m": 0.0, "base_z_m": 0.05, "width_m": 1.75, "height_m": 2.85, "type": "door", "panel_rows": 2, "panel_columns": 2, "transom_height_m": 0.55},
            {"along_m": 3.3, "base_z_m": 0.65, "width_m": 1.55, "height_m": 2.25},
            {"along_m": 6.6, "base_z_m": 0.65, "width_m": 1.55, "height_m": 2.25},
        ],
    })
    graph["nodes"] += [
        box("greystone_base_course", [17.6, 0.30, 0.34], [0, front_y - 0.14, 0.30], "primary", 0.025),
        box("greystone_cornice_course", [17.8, 0.42, 0.42], [0, front_y - 0.20, 10.95], "primary", 0.035),
        box("greystone_balcony_slab", [16.2, 1.05, 0.18], [0, front_y - 0.52, 3.35], "primary", 0.025),
        box("greystone_balcony_top_rail", [15.8, 0.08, 0.10], [0, front_y - 1.02, 4.20], "secondary", 0.02),
    ]
    for index, x in enumerate((-7.7, -6.6, -5.5, -4.4, -3.3, -2.2, -1.1, 0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7)):
        graph["nodes"].append(box(f"greystone_balcony_picket_{index}", [0.055, 0.055, 0.78], [x, front_y - 1.02, 3.78], "secondary", 0.01))
    production["fixed_identity"] = [
        "light grey limestone streetwall", "two broad double-height projecting iron bays",
        "continuous shallow balcony and fine iron rail", "recessed central entrance", "restrained parapet and cornice",
    ]


def white_corbusian(graph: dict[str, Any], production: dict[str, Any]) -> None:
    graph["nodes"] = [node for node in graph["nodes"] if not node["id"].startswith("pergola_")]
    main_block = next(node for node in graph["nodes"] if node["id"] == "main_cantilever_block")
    roof_datum = float(main_block["location"][2]) + float(main_block["size"][2]) / 2
    for node in graph["nodes"]:
        if node["id"] == "roof_garden_membrane":
            node.update({"size": [28.0, 14.0, 0.10], "location": [0.5, 1.0, roof_datum + 0.05]})
        elif node["id"] == "penthouse_block":
            node.update({"size": [12.0, 8.0, 2.8], "location": [-8.0, 4.0, 16.40]})
    graph["assemblies"] = [
        assembly for assembly in graph["assemblies"]
        if assembly["id"] not in {"skin_penthouse_front", "skin_penthouse_front_glazing"}
    ]
    # The inherited rear sheet was authored to the old 20.84 m datum.  Once
    # the main slab was corrected to 15 m it projected above the roof like a
    # billboard in the front three-quarter view.  Keep the rear elevation,
    # but bind both layers to the actual envelope.
    for assembly in graph["assemblies"]:
        if assembly["id"] in {"rear_depth_skin", "rear_depth_skin_glazing"}:
            assembly.update({"centre": [0.0, 12.02, 7.5], "span_m": 36.0, "height_m": 15.0})
    graph["assemblies"].append({
        "id": "penthouse_true_ribbon", "kind": "curtain_wall", "axis": "front",
        "centre": [-8.0, -0.03, 16.45], "span_m": 9.8, "height_m": 1.25,
        "columns": 5, "rows": 1, "frame_m": 0.07, "depth_m": 0.10,
        "reveal_m": 0.08, "surround_m": 0.12, "surround_depth_m": 0.12,
        "glass_material": "glass", "frame_material": "secondary",
        "surround_material": "primary", "interior_material": "interior_warm",
        "interior_recess_m": 0.34,
    })
    graph["reference_dimensions"].update({"width_m": 36.0, "depth_m": 23.0, "floors": 5})
    graph["height_m"] = 17.8
    graph["nodes"] += [
        box("roof_path_main", [23.0, 2.1, 0.14], [-4.0, 0.5, roof_datum + 0.14], "secondary", 0.02),
        box("roof_planter_west", [8.0, 3.0, 0.48], [-12.5, 5.5, roof_datum + 0.26], "roof", 0.06),
        box("roof_planter_east", [7.0, 3.2, 0.48], [12.0, -4.8, roof_datum + 0.26], "roof", 0.06),
        box("pergola_front_beam_v88", [11.5, 0.18, 0.20], [8.0, -2.5, roof_datum + 2.0], "secondary", 0.025),
        box("pergola_rear_beam_v88", [11.5, 0.18, 0.20], [8.0, 3.5, roof_datum + 2.0], "secondary", 0.025),
    ]
    for index, x in enumerate((2.25, 6.1, 9.95, 13.8)):
        graph["nodes"].append(box(f"pergola_post_v88_{index}", [0.15, 0.15, 1.85], [x, -2.5, roof_datum + 0.98], "secondary", 0.015))
    production["fixed_identity"] = [
        "white cantilevered modernist slab", "transparent pilotis ground floor",
        "thin ribbon-window datums", "small occupied roof garden", "restrained skeletal pergola",
    ]


def precast(graph: dict[str, Any], production: dict[str, Any]) -> None:
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] not in {"block_rear_left", "block_rear_right", "roof_volume_left", "roof_volume_right", "canopy_right"}]
    for node in graph["nodes"]:
        if node["id"] == "roof_volume_main":
            node.update({"size": [16.5, 10.5, 2.5], "location": [1.5, 1.3, 21.75]})
        elif node["id"] == "canopy_front":
            node.update({"size": [17.0, 1.55, 0.28], "location": [-3.2, -10.8, 4.0]})
    graph["assemblies"] = [
        assembly for assembly in graph["assemblies"]
        if "rear_depth" not in assembly["id"]
    ]
    graph["reference_dimensions"].update({"width_m": 26.0, "depth_m": 22.0, "floors": 5})
    graph["height_m"] = 23.0
    production["fixed_identity"] = [
        "five-storey pale precast frame", "regular rectangular punched-window grid",
        "transparent recessed ground floor", "short service crown", "localized entrance canopy",
    ]


def terracotta(graph: dict[str, Any], production: dict[str, Any]) -> None:
    production["repeatable_module_geometry_variant"] = "typical_a"
    production["shared_module_geometry_roles"] = ["floor", "setback", "crown"]
    graph["nodes"] = [
        # Thin structural plates preserve a true transparent envelope.  A
        # solid glass cuboid behaves like several metres of glazing and hides
        # the occupied room cards, producing the blank grey panels seen in the
        # rejected V88-a image.
        box("terracotta_ground_slab", [32.0, 22.0, 0.24], [0, 0, 0.12], "primary", 0.025),
        box("terracotta_level_one_slab", [32.0, 22.0, 0.24], [0, 0, 4.22], "primary", 0.025),
        box("terracotta_level_two_slab", [32.0, 22.0, 0.24], [0, 0, 7.62], "primary", 0.025),
        box("terracotta_middle_terrace", [32.6, 22.6, 0.28], [0, 0, 11.43], "primary", 0.025),
        box("terracotta_upper_terrace", [27.5, 18.5, 0.25], [1.2, 1.4, 15.82], "primary", 0.025),
        box("terracotta_service_core", [7.5, 6.0, 17.83], [5.2, 4.8, 8.915], "secondary", 0.04),
        box("terracotta_planter_front", [20.0, 1.0, 0.60], [-1.0, -9.65, 11.72], "roof", 0.055),
        box("terracotta_planter_roof", [18.0, 1.0, 0.60], [0.5, -6.95, 16.10], "roof", 0.055),
    ]
    graph["assemblies"] = [
        # The semantic sheet supplies high-frequency ceiling, room, and glass
        # cues while its masks create real holes for the physical glazing
        # overlay.  Terracotta fins, slabs, and setbacks remain geometry in
        # front of it, so this is not a flat billboard facade.
        skin("terracotta_front_semantic", "front", [0, -11.02, 8.7], 32.0, 17.4),
        glazing("terracotta_front_glazing", "front", [0, -11.07, 8.7], 32.0, 17.4, 10, 5, profile="office_clear_occupied"),
        glazing("terracotta_glass_left", "left", [-16.04, 0, 7.8], 22.0, 15.2, 6, 4, profile="office_clear_occupied"),
        glazing("terracotta_glass_right", "right", [16.04, 0, 7.8], 22.0, 15.2, 6, 4, profile="office_clear_occupied"),
    ]
    for level, z in enumerate((6.0, 9.25)):
        for index in range(11):
            x = -14.5 + index * 2.9
            graph["nodes"].append(box(f"terracotta_fin_v88_{level}_{index:02d}", [0.12, 0.48, 2.60], [x, -11.28, z], "primary", 0.015))
    graph["reference_dimensions"].update({"width_m": 32.0, "depth_m": 22.0, "floors": 4})
    graph["height_m"] = 17.83
    production["fixed_identity"] = [
        "low horizontally layered office pavilion", "two pronounced planted setbacks",
        "terracotta fins limited to window bands", "transparent double-height base", "small recessed service crown",
    ]


def dark_frame(graph: dict[str, Any], production: dict[str, Any]) -> None:
    graph["nodes"] = [
        box(f"dark_frame_slab_{index:02d}", [28.0, 20.0, 0.20], [0, 0, z], "primary", 0.02)
        for index, z in enumerate((0.10, 3.80, 7.60, 11.40, 15.20, 19.00, 22.80))
    ] + [
        box("dark_frame_core", [6.0, 11.0, 22.8], [10.2, 3.0, 11.4], "secondary", 0.03),
        box("dark_frame_roof", [27.6, 19.6, 0.16], [0, 0, 22.88], "roof", 0.02),
        box("dark_crown_front", [27.4, 0.14, 0.14], [0, -9.62, 24.12], "primary", 0.015),
        box("dark_crown_rear", [27.4, 0.14, 0.14], [0, 9.62, 24.12], "primary", 0.015),
        box("dark_crown_left", [0.14, 19.4, 0.14], [-13.62, 0, 24.12], "primary", 0.015),
        box("dark_crown_right", [0.14, 19.4, 0.14], [13.62, 0, 24.12], "primary", 0.015),
    ]
    for index, (x, y) in enumerate(((-13.62, -9.62), (13.62, -9.62), (-13.62, 9.62), (13.62, 9.62))):
        graph["nodes"].append(box(f"dark_crown_post_{index}", [0.14, 0.14, 1.24], [x, y, 23.50], "primary", 0.015))
    graph["assemblies"] = [
        # A masked semantic layer contributes the thin floor edges, ceiling
        # lights, and room variation visible in the photograph.  It sits just
        # behind the real transparent curtain wall and expressed frame.
        skin("dark_front_semantic", "front", [0, -9.94, 11.4], 28.0, 22.45),
        skin("dark_left_semantic", "left", [-13.94, 0, 11.4], 20.0, 22.45, band="side", flip=True),
        skin("dark_right_semantic", "right", [13.94, 0, 11.4], 20.0, 22.45, band="side"),
        glazing("dark_glass_front", "front", [0, -10.03, 11.4], 28.0, 22.45, 5, 6, profile="office_clear_occupied"),
        glazing("dark_glass_left", "left", [-14.03, 0, 11.4], 20.0, 22.45, 4, 6, profile="office_clear_occupied"),
        glazing("dark_glass_right", "right", [14.03, 0, 11.4], 20.0, 22.45, 4, 6, profile="office_clear_occupied"),
        frame_grid("dark_front_structure", "front", [0, -10.11, 11.4], 28.0, 22.45, 5, 6, "primary", 0.18, 0.22),
        frame_grid("dark_left_structure", "left", [-14.11, 0, 11.4], 20.0, 22.45, 4, 6, "primary", 0.18, 0.22),
        frame_grid("dark_right_structure", "right", [14.11, 0, 11.4], 20.0, 22.45, 4, 6, "primary", 0.18, 0.22),
    ]
    graph["reference_dimensions"].update({"width_m": 28.0, "depth_m": 20.0, "floors": 6})
    graph["height_m"] = 24.19
    production["fixed_identity"] = [
        "slender transparent four-level pavilion", "fine consistent external black frame",
        "visible occupied interior depth", "compact solid service core", "flush restrained roof edge",
    ]


def charred(graph: dict[str, Any], production: dict[str, Any]) -> None:
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] not in {"mass_rear", "roof_rear"}]
    for node in graph["nodes"]:
        if node["id"] == "mass_main":
            node.update({"size": [11.5, 14.0, 9.6], "location": [0, 0, 4.8]})
        elif node["id"] == "roof_main":
            node.update({"size": [11.5, 14.0, 5.1], "location": [0, 0, 9.6], "ridge_axis": "y"})
    graph["assemblies"] = [assembly for assembly in graph["assemblies"] if "rear" not in assembly["id"]]
    for assembly in graph["assemblies"]:
        axis = assembly.get("axis")
        if axis == "front":
            assembly["centre"][1] = -7.02
            assembly["span_m"] = 11.5
        elif axis == "left":
            assembly["centre"][0] = -5.77
            assembly["span_m"] = 14.0
        elif axis == "right":
            assembly["centre"][0] = 5.77
            assembly["span_m"] = 14.0
    graph["assemblies"] += [
        frame_grid("charred_asymmetric_reveals", "front", [0, -7.08, 4.8], 11.5, 9.6, 4, 3, "secondary", 0.10, 0.20),
        {"id": "charred_roof_detail", "kind": "pitched_roof_surface_detail", "centre": [0, 0, 9.6], "size": [11.5, 14.0, 5.1], "ridge_axis": "y", "roof_material": "roof", "ridge_material": "secondary", "seam_count": 11, "gutter_enabled": True, "verge_enabled": True},
    ]
    production["fixed_identity"] = [
        "narrow urban infill proportion", "asymmetric black timber opening rhythm",
        "continuous steep standing-seam gable", "warm timber entrance reveals", "deep side-wall returns",
    ]
    graph["reference_dimensions"].update({"width_m": 12.0, "depth_m": 14.0, "floors": 3})


def clt(graph: dict[str, Any], production: dict[str, Any]) -> None:
    graph["nodes"] = [node for node in graph["nodes"] if not node["id"].startswith("clt_pine_reveal_")]
    for node in graph["nodes"]:
        if node["id"] == "sauna_pavilion":
            node.update({"size": [5.0, 3.2, 1.75], "location": [5.0, 0.8, 13.775]})
    # The CLT archetype has quiet panel joints and thin horizontal floor
    # datums—not a full-storey external exoskeleton.  Clip inherited depth
    # sheets to the four-storey body and let their authored panel rhythm carry
    # the elevation without duplicate white frame geometry.
    for assembly in graph["assemblies"]:
        if "depth_skin_storey_" in assembly["id"]:
            storey = int(assembly["id"].split("storey_")[1].split("_")[0])
            assembly.update({"centre": [*assembly["centre"][:2], 1.6 + 3.2 * storey], "height_m": 3.2})
    for index, z in enumerate((3.20, 6.40, 9.60, 12.76)):
        graph["nodes"] += [
            box(f"clt_horizontal_front_{index}", [20.0, 0.12, 0.14], [0, -8.14, z], "secondary", 0.012),
            box(f"clt_horizontal_right_{index}", [0.12, 16.0, 0.14], [10.14, 0, z], "secondary", 0.012),
        ]
    production["fixed_identity"] = [
        "long horizontal timber mid-rise", "fine expressed CLT frame rhythm",
        "transparent community base", "shallow sedum roof", "modest recessed rooftop pavilion",
    ]


def moorish(graph: dict[str, Any], production: dict[str, Any]) -> None:
    # Fixed two-storey landmark reconstructed from the exact street, oblique
    # and roof references.  The inherited metadata elevation had invented a
    # third storey; only the trustworthy ground and single crown bands survive.
    width, depth, ground_h, upper_h, total_h = 20.0, 15.0, 4.5, 3.65, 9.25
    front_y = -depth / 2
    front_centres = [-5.90, 0.65, 7.10]
    side_centres = [1.35, 5.65]
    graph["nodes"] = [
        {
            "id": "moorish_front_deep_arcade", "kind": "opening_block", "axis": "front",
            "size": [width, 6.2, ground_h], "location": [0, -4.4, ground_h / 2],
            "opening_shape": "horseshoe_arch", "opening_count": 3, "opening_centres_m": front_centres,
            "opening_width_m": 4.35, "opening_base_m": 0.0,
            "opening_height_m": 3.95, "spring_height_m": 2.10,
            "arch_segments": 28, "section_mode": "recessed", "material": "primary",
            "lining_material": "primary", "trim_material": "secondary",
            "trim_profile_m": 0.16, "trim_depth_m": 0.38,
            "back_material": "interior_warm", "back_frame_material": "signature_door",
            "lining_setback_m": 0.07, "lower_tile_height_m": 0.90,
            "neck_ratio": 0.74,
            "bevel_m": 0.045,
        },
        # This separate return volume makes the two right-hand market bays
        # actual cavernous spaces.  It is not a stretched side photograph.
        {
            "id": "moorish_right_deep_arcade", "kind": "opening_block", "axis": "right",
            "size": [3.0, 8.8, ground_h], "location": [8.5, 3.1, ground_h / 2],
            "opening_shape": "horseshoe_arch", "opening_count": 2, "opening_centres_m": [-1.75, 2.55],
            "opening_width_m": 3.15, "opening_base_m": 0.0,
            "opening_height_m": 3.85, "spring_height_m": 2.00,
            "arch_segments": 26, "section_mode": "recessed", "material": "primary",
            "lining_material": "primary", "trim_material": "secondary",
            "trim_profile_m": 0.14, "trim_depth_m": 0.34,
            "back_material": "interior_warm", "back_frame_material": "signature_door",
            "lining_setback_m": 0.07, "lower_tile_height_m": 0.86,
            "neck_ratio": 0.74,
            "bevel_m": 0.045,
        },
        box("moorish_rear_ground_body", [17.0, 8.8, ground_h], [-1.5, 3.1, ground_h / 2], "primary", 0.07),
        box("moorish_terrace_slab", [20.15, 15.15, 0.24], [0, 0, 4.62], "secondary", 0.025),
        box("moorish_upper_pavilion", [16.0, 10.0, upper_h], [0, 1.8, ground_h + upper_h / 2], "primary", 0.075),
        box("moorish_upper_roof", [16.25, 10.25, 0.24], [0, 1.8, 8.27], "primary", 0.025),
        # Terracotta terrace coping is a distinct lower roof datum in the exact reference.
        box("moorish_terrace_coping_front", [20.25, 0.22, 0.16], [0, -7.46, 4.75], "roof", 0.025),
        box("moorish_terrace_coping_rear", [20.25, 0.22, 0.16], [0, 7.46, 4.75], "roof", 0.025),
        box("moorish_terrace_coping_left", [0.22, 14.65, 0.16], [-9.86, 0, 4.75], "roof", 0.025),
        box("moorish_terrace_coping_right", [0.22, 14.65, 0.16], [9.86, 0, 4.75], "roof", 0.025),
    ]
    for index, (x, y) in enumerate(((-8.0, -3.2), (8.0, -3.2), (-8.0, 6.8), (8.0, 6.8))):
        graph["nodes"].append(box(
            f"moorish_parapet_pier_{index}", [0.34, 0.34, 1.18], [x, y, 8.82], "primary", 0.04,
        ))

    front_clearances = [{
        "void_id": "moorish_front_arcade", "shape": "horseshoe_arch",
        "centre_m": centre, "width_m": 4.35, "base_z_m": 0.0,
        "height_m": 3.95, "spring_z_m": 2.10, "arch_segments": 28,
        "neck_ratio": 0.74, "shoulder_bulge_ratio": 0.55,
    } for index, centre in enumerate(front_centres)]
    side_clearances = [{
        "void_id": "moorish_right_arcade", "shape": "horseshoe_arch",
        "centre_m": centre, "width_m": 3.15, "base_z_m": 0.0,
        "height_m": 3.85, "spring_z_m": 2.00, "arch_segments": 26,
        "neck_ratio": 0.74, "shoulder_bulge_ratio": 0.55,
    } for index, centre in enumerate(side_centres)]
    graph["assemblies"] = [
        {
            **skin("moorish_front_arcade_sticker", "front", [0, front_y - 0.025, ground_h / 2], width, ground_h, band="podium"),
            "source_image_path": str(MOORISH_PODIUM_STICKER),
            "registration_group": "moorish_front_arcade",
            "opening_clearances": front_clearances,
        },
        {
            **skin("moorish_right_arcade_sticker", "right", [10.025, 3.1, ground_h / 2], 8.8, ground_h, band="podium"),
            "source_image_path": str(MOORISH_PODIUM_STICKER),
            "registration_group": "moorish_right_arcade", "uv_u_min": 0.33, "uv_u_max": 1.0,
            "opening_clearances": side_clearances,
        },
        {
            **skin("moorish_upper_front_sticker", "front", [0, -3.225, 6.325], 16.0, upper_h, band="crown"),
            "source_image_path": str(MOORISH_CROWN_STICKER),
            "registration_group": "moorish_upper_front", "uv_u_min": 0.05, "uv_u_max": 0.75,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {
            **skin("moorish_upper_right_sticker", "right", [8.025, 1.8, 6.325], 10.0, upper_h, band="crown"),
            "source_image_path": str(MOORISH_CROWN_STICKER),
            "registration_group": "moorish_upper_right", "uv_u_min": 0.05, "uv_u_max": 0.50,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {
            **skin("moorish_upper_rear_sticker", "rear", [0, 6.825, 6.325], 16.0, upper_h, band="crown", flip=True),
            "source_image_path": str(MOORISH_CROWN_STICKER), "uv_u_min": 0.05, "uv_u_max": 0.75,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {
            **skin("moorish_upper_left_sticker", "left", [-8.025, 1.8, 6.325], 10.0, upper_h, band="crown", flip=True),
            "source_image_path": str(MOORISH_CROWN_STICKER), "uv_u_min": 0.50, "uv_u_max": 1.0,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {
            **skin("moorish_rear_ground_sticker", "rear", [-1.5, 7.525, ground_h / 2], 17.0, ground_h, band="crown", flip=True),
            "source_image_path": str(MOORISH_CROWN_STICKER), "uv_u_min": 0.0, "uv_u_max": 1.0,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {
            **skin("moorish_left_ground_sticker", "left", [-10.025, 3.1, ground_h / 2], 8.8, ground_h, band="crown", flip=True),
            "source_image_path": str(MOORISH_CROWN_STICKER), "uv_u_min": 0.0, "uv_u_max": 0.55,
            "uv_v_min": 0.0, "uv_v_max": 0.50,
        },
        {"id": "moorish_front_market_stalls", "kind": "market_stall_schedule", "axis": "front", "face_coordinate_m": -1.34, "positions_m": front_centres, "bay_width_m": 4.35, "base_z_m": 0.18, "counter_depth_m": 0.82, "counter_height_m": 0.92, "counter_material": "signature_warm", "frame_material": "signature_warm"},
        {"id": "moorish_right_market_stalls", "kind": "market_stall_schedule", "axis": "right", "face_coordinate_m": 7.03, "positions_m": side_centres, "bay_width_m": 3.15, "base_z_m": 0.18, "counter_depth_m": 0.72, "counter_height_m": 0.88, "counter_material": "signature_warm", "frame_material": "signature_warm"},
        {
            "id": "moorish_geometric_roof_parapet", "kind": "lattice_parapet",
            "base_z_m": 8.36, "height_m": 0.86, "profile_m": 0.028, "material": "primary",
            "runs": [
                {"start": [-8.0, -3.2], "end": [8.0, -3.2], "cells": 24},
                {"start": [8.0, -3.2], "end": [8.0, 6.8], "cells": 16},
                {"start": [8.0, 6.8], "end": [-8.0, 6.8], "cells": 24},
                {"start": [-8.0, 6.8], "end": [-8.0, -3.2], "cells": 16},
            ],
        },
        {"id": "moorish_cornice_corbel", "kind": "corbel_array", "axis": "front", "centre": [0, -3.38, 8.18], "span_m": 16.0, "levels_z": [8.10], "count": 20, "material": "secondary", "depth_m": 0.24, "height_m": 0.16},
    ]
    graph["reference_dimensions"].update({"width_m": width, "depth_m": depth, "floors": 2})
    graph["height_m"] = total_h
    graph["voids"] = [
        {"id": "moorish_front_arcade", "shape": "horseshoe_arch_passage", "axis": "front", "size": [width, 6.2, 4.0], "location": [0, -4.4, 2.0], "purpose": "deep occupied street market arcade"},
        {"id": "moorish_right_arcade", "shape": "horseshoe_arch_passage", "axis": "right", "size": [3.0, 8.8, 3.9], "location": [8.5, 3.1, 1.95], "purpose": "deep occupied return market arcade"},
    ]
    graph["presentation_camera"] = {"oblique_x_scale": 0.37, "identity_distance_scale": 0.68, "street_distance_scale": 0.72}
    production["fixed_identity"] = [
        "three deep occupied street arcade passages", "two deep right-return market arches",
        "white stucco and turquoise zellige sticker registration", "set-back single-storey pavilion",
        "terracotta terrace coping", "continuous crossed-lattice roof parapet",
    ]
    production["placement_contract"] = {
        "method": "sticker_method", "mode": "fixed_landmark", "ui_interaction": "select_and_place",
        "footprint_m": {"width": width, "depth": depth}, "visible_height_m": total_h,
        "translation": "allowed", "rotation": "allowed", "uniform_scale": "discouraged",
        "non_uniform_scale": "forbidden", "floor_count_change": "forbidden", "polygon_fit": False,
        "preferred_context": "freestanding_market_corner", "freestanding_elevations": "authored",
        "lego_compatibility": "fixed_landmark_with_registered_surface_and_true_arcade_voids",
    }
    production["material_continuity"]["node_bindings"] = [{
        "kind": "opening_block",
        "ids": ["moorish_front_deep_arcade", "moorish_right_deep_arcade"],
        "slots": {"material": "primary", "lining_material": "primary", "trim_material": "secondary"},
    }]
    production["spatial_voids"] = {"required_passages": [
        {
            "void_id": "moorish_front_arcade", "target_node_id": "moorish_front_deep_arcade",
            "target_node_kind": "opening_block", "shape": "horseshoe_arch_passage",
            "section_mode": "recessed", "minimum_depth_m": 5.5,
            "minimum_opening_count": 3, "minimum_clearance_count": 3,
        },
        {
            "void_id": "moorish_right_arcade", "target_node_id": "moorish_right_deep_arcade",
            "target_node_kind": "opening_block", "shape": "horseshoe_arch_passage",
            "section_mode": "recessed", "minimum_depth_m": 2.5,
            "minimum_opening_count": 2, "minimum_clearance_count": 2,
        },
    ]}
    production["image_lock"]["measurements"] = [
        {"feature": "facade_width", "role": "street_identity", "value": width, "unit": "metres", "drives": "moorish_front_arcade_sticker"},
        {"feature": "arcade_count", "role": "street_identity", "value": 3, "unit": "count", "drives": "moorish_front_deep_arcade"},
        {"feature": "return_arcade_count", "role": "oblique_massing", "value": 2, "unit": "count", "drives": "moorish_right_deep_arcade"},
        {"feature": "arcade_depth", "role": "oblique_massing", "value": 6.2, "unit": "metres", "drives": "moorish_front_deep_arcade"},
        {"feature": "ground_height", "role": "street_identity", "value": ground_h, "unit": "metres", "drives": "moorish_front_arcade_sticker"},
        {"feature": "upper_setback", "role": "roof_plan", "value": 4.3, "unit": "metres", "drives": "moorish_upper_pavilion"},
        {"feature": "upper_width", "role": "roof_plan", "value": 16.0, "unit": "metres", "drives": "moorish_upper_pavilion"},
        {"feature": "overall_height", "role": "roof_plan", "value": total_h, "unit": "metres", "drives": "moorish_geometric_roof_parapet"},
    ]


def catalan(graph: dict[str, Any], production: dict[str, Any]) -> None:
    # The exact elevation is a narrow, nearly planar streetwall.  The rejected
    # draft wrapped it around a cylinder and then covered it with five generic
    # ring balconies.  V88 instead uses an image-locked 2.5D section: the
    # audited elevation owns fine identity while cropped copies of the same UV
    # field sit on local projection volumes.  The photograph therefore stays
    # registered as bays acquire real depth in oblique views.
    # The exact front image remains the width/height authority.  Casa
    # Batllo's archival narrow/deep row-house proportions are admitted only as
    # a depth prior, producing a fixed landmark rather than a stretched card.
    width, depth, wall_h, total_h = 14.0, 31.0, 17.0, 24.60
    front_y = -depth / 2
    graph["nodes"] = [
        # A three-metre-deep entrance section is kept genuinely hollow.  The
        # back body starts behind it; front piers and a lintel form the portal
        # instead of hiding a solid box behind a black doorway pixel.
        box("catalan_rear_body", [width, depth - 3.0, wall_h], [0, 1.5, wall_h / 2], "primary", 0.10),
        {
            "id": "catalan_entry_opening_block", "kind": "opening_block",
            "size": [width, 3.0, wall_h], "location": [0, front_y + 1.5, wall_h / 2],
            "opening_shape": "round_arch", "opening_count": 1,
            "opening_centres_m": [-5.20],
            "opening_width_m": 2.10, "opening_base_m": 0.0,
            "opening_height_m": 3.00, "spring_height_m": 1.95,
            "section_mode": "recessed", "material": "primary",
            "lining_material": "primary", "trim_material": "primary",
            "back_material": "massing_joint", "back_frame_material": "signature_metal",
            "bevel_m": 0.08,
        },
        # The roof is a sequence: an identity-bearing dragon back at the
        # street, a lower middle roof and a restrained rear roof/terrace.
        {"id": "catalan_main_roof", "kind": "undulating_roof_shell", "size": [14.6, 12.2, 5.15], "location": [0, -9.45, 16.92], "material": "roof", "bevel_m": 0.055, "columns": 44, "rows": 30, "front_wave_m": 1.12, "asymmetry_m": 0.38, "thickness_m": 0.16},
        {"id": "catalan_middle_roof", "kind": "hipped_roof", "size": [13.8, 9.2, 2.55], "location": [0, 0.45, 16.98], "material": "roof", "bevel_m": 0.08, "ridge_axis": "y", "ridge_inset_m": 1.0},
        {"id": "catalan_rear_roof", "kind": "hipped_roof", "size": [13.8, 9.5, 1.75], "location": [0, 10.05, 16.98], "material": "roof", "bevel_m": 0.08, "ridge_axis": "x", "ridge_inset_m": 1.2},
        box("catalan_rear_terrace_parapet_left", [0.24, 8.2, 0.85], [-6.75, 10.5, 17.42], "primary", 0.04),
        box("catalan_rear_terrace_parapet_right", [0.24, 8.2, 0.85], [6.75, 10.5, 17.42], "primary", 0.04),
    ]
    # Central joined chimney pots and the two decorated right-hand stacks are
    # fixed skyline groups, not interchangeable generic roof furniture.
    graph["assemblies"] = [
        # Crop the full elevation below its roof/eave band. The three-dimensional
        # roof owns the upper silhouette and avoids a rectangular photo billboard.
        {
            **skin("catalan_front_image_lock", "front", [0, front_y - 0.025, wall_h / 2], width, wall_h),
            "uv_v_min": 0.0,
            "uv_v_max": 0.79,
            "registration_group": "catalan_front_elevation",
            "mask_semantics": "continuous_registration_base",
            "opening_clearances": [{
                "void_id": "catalan_open_entry_tunnel", "shape": "round_arch",
                "centre_m": -5.20, "width_m": 2.10, "base_z_m": 0.0,
                "height_m": 3.00, "spring_z_m": 1.95, "arch_segments": 24,
            }],
        },
        {
            **skin("catalan_rear", "rear", [0, depth / 2 + 0.025, wall_h / 2], width, wall_h, band="elevation", flip=True),
            "source_image_path": str(CATALAN_REAR_STICKER),
            "registration_group": "catalan_rear_elevation",
            "mask_semantics": "continuous_registration_base",
        },
        {
            **skin("catalan_left_return", "left", [-width / 2 - 0.025, 0, wall_h / 2], depth, wall_h, band="elevation", flip=True),
            "source_image_path": str(CATALAN_SIDE_STICKER),
            "registration_group": "catalan_left_side_elevation",
            "mask_semantics": "continuous_registration_base",
        },
        {
            **skin("catalan_right_return", "right", [width / 2 + 0.025, 0, wall_h / 2], depth, wall_h, band="elevation"),
            "source_image_path": str(CATALAN_SIDE_STICKER),
            "registration_group": "catalan_right_side_elevation",
            "mask_semantics": "continuous_registration_base",
        },
    ]

    graph["assemblies"] += [
        {
            "id": "catalan_left_sculptural_turret", "kind": "striped_turret_array",
            "centres": [[-5.8, -14.1]], "base_z": 17.0, "radius_m": 1.0, "body_height_m": 4.3,
            "body_material": "primary", "stripe_material": "roof", "dark_material": "accent",
            "stripe_levels_m": [1.10, 2.10, 3.10], "stripe_height_m": 0.16,
            "belt_levels_m": [0.30, 3.78], "belt_height_m": 0.18,
            "belt_material": "primary", "roof_material": "primary", "roof_style": "bulbous",
            "roof_height_m": 2.35, "roof_radius_m": 1.32, "vertices": 40,
            "finial_radius_m": 0.11,
        },
        {
            "id": "catalan_central_triple_pots", "kind": "striped_turret_array",
            "centres": [[-1.05, -9.2], [-0.50, -9.2], [0.05, -9.2]],
            "base_z": 20.85, "radius_m": 0.31, "body_height_m": 2.65,
            "body_material": "primary", "stripe_material": "secondary",
            "stripe_levels_m": [0.55, 1.35, 2.15], "stripe_height_m": 0.13,
            "belt_material": "roof", "belt_levels_m": [2.52], "belt_height_m": 0.15,
            "roof_material": "primary", "roof_style": "bulbous",
            "roof_height_m": 0.20, "roof_radius_m": 0.34, "vertices": 24,
            "finial_radius_m": 0.012,
        },
        {
            "id": "catalan_right_sculptural_chimneys", "kind": "striped_turret_array",
            "centres": [[4.25, -10.8], [5.35, -10.8]], "base_z": 19.2,
            "radius_m": 0.50, "body_height_m": 3.55,
            "body_material": "primary", "stripe_material": "roof", "dark_material": "accent",
            "stripe_levels_m": [0.75, 1.55, 2.35], "stripe_height_m": 0.16,
            "belt_levels_m": [3.25], "belt_height_m": 0.18,
            "belt_material": "roof", "roof_material": "roof", "roof_style": "bulbous",
            "roof_height_m": 1.15, "roof_radius_m": 0.69, "vertices": 28,
            "finial_radius_m": 0.08,
        },
    ]
    graph.setdefault("voids", []).append({
        "id": "catalan_open_entry_tunnel", "shape": "round_arch_passage", "axis": "front",
        "size": [2.10, 3.0, 3.00], "location": [-5.20, front_y + 1.5, 1.50],
        "purpose": "three-metre recessed open gate passage",
    })
    production["spatial_voids"] = {"required_passages": [{
        "void_id": "catalan_open_entry_tunnel",
        "target_node_id": "catalan_entry_opening_block",
        "target_node_kind": "opening_block",
        "shape": "round_arch_passage", "section_mode": "recessed",
        "minimum_depth_m": 2.5, "minimum_clearance_count": 1,
    }]}

    def stitched_projection(
        node_id: str,
        x: float,
        z: float,
        span: float,
        height: float,
        projection: float,
        *,
        stone_soffit: bool = False,
    ) -> None:
        """Place one registered crop without a full-height backing box.

        Solid backing volumes exposed bright undersides and dark vertical side
        faces between storeys. A tiny overlap closes texture sampling cracks;
        the continuous base elevation remains the physical wall behind it.
        """
        # The bleed must be applied in *both* object space and image space.
        # V88's first stitched draft widened the physical card while retaining
        # the unexpanded UV crop. That tiny scale mismatch accumulated between
        # storeys, so columns and window jambs visibly jumped at crop edges.
        # A 4 cm bleed on every edge now samples the corresponding 4 cm of the
        # canonical elevation, preserving one exact metres-to-UV transform.
        bleed = 0.04
        registered_span = span + 2 * bleed
        registered_height = height + 2 * bleed
        left = x - span / 2 - bleed
        right = x + span / 2 + bleed
        bottom = z - height / 2 - bleed
        top = z + height / 2 + bleed
        graph["assemblies"].append({
            **skin(node_id, "front", [x, front_y - projection - 0.025, z], registered_span, registered_height),
            "depth_m": 0.030,
            "uv_u_min": (left + width / 2) / width,
            "uv_u_max": (right + width / 2) / width,
            "uv_v_min": max(0.0, bottom / wall_h * 0.79),
            "uv_v_max": min(0.79, top / wall_h * 0.79),
            "registration_group": "catalan_front_elevation",
            "alpha_mask_path": str(CATALAN_STICKER_MASKS / f"{node_id}_alpha.png"),
            "mask_semantics": "alpha_isolated_projected_feature",
        })
        if stone_soffit:
            # The alpha-isolated face owns photographic ornament; this shallow
            # bevelled stone volume owns the visible underside, side return and
            # real contact shadow. It stops just behind the sticker so no
            # rectangular wall pixels travel forward with the construction.
            slab_height = 0.09
            slab_depth = max(0.08, projection - 0.04)
            graph["nodes"].append(box(
                f"{node_id}_stone_soffit",
                [span * 0.88, slab_depth, slab_height],
                # The sticker sits just ahead of the soffit's front edge, so
                # its photographed carved-stone perimeter conceals the simple
                # structural return in a head-on view.
                [x, front_y - projection / 2, z - height / 2 + slab_height / 2],
                "primary",
                0.038,
            ))

    stitched_projection("catalan_piano_nobile_gallery", 0.0, 5.25, 9.4, 3.15, 0.35)
    stitched_projection("catalan_left_oriel_stack", -5.45, 8.70, 2.35, 7.10, 0.55)
    stitched_projection("catalan_right_oriel_stack", 5.45, 8.70, 2.35, 7.10, 0.55)
    # Feature bands are deliberately tight. A previous schedule sampled a
    # complete window/storey rectangle around each projection: the long card
    # included the smaller balcony below it and the upper cards sampled the
    # attic eave. These centres come from the rectified elevation's feature
    # rows, so the sticker owns only the projecting construction.
    stitched_projection("catalan_central_long_balcony", 0.0, 11.05, 6.6, 1.42, 0.78, stone_soffit=True)
    stitched_projection("catalan_mid_left_balcony", -2.15, 8.72, 2.35, 1.38, 0.52, stone_soffit=True)
    stitched_projection("catalan_mid_right_balcony", 2.15, 8.72, 2.35, 1.38, 0.52, stone_soffit=True)
    for index, x in enumerate((-5.25, -1.75, 1.75, 5.25)):
        stitched_projection(f"catalan_upper_balcony_{index}", x, 13.34, 2.05, 1.34, 0.48, stone_soffit=True)

    graph["reference_dimensions"].update({"width_m": width, "depth_m": depth, "floors": 6})
    graph["height_m"] = total_h
    graph.setdefault("reference_views", []).extend([
        {"role": "side_elevation", "path": str(CATALAN_MULTIVIEW / "left-elevation-long-v1.png")},
        {"role": "rear_elevation", "path": str(CATALAN_MULTIVIEW / "rear-elevation-v1.png")},
        {"role": "roof_oblique", "path": str(CATALAN_MULTIVIEW / "roof-oblique-v1.png")},
    ])
    production["image_lock"]["measurements"] = [
        {"feature": "facade_width", "role": "street_identity", "value": width, "unit": "metres", "drives": "catalan_streetwall"},
        {"feature": "wall_height", "role": "street_identity", "value": wall_h, "unit": "metres", "drives": "catalan_front_image_lock"},
        {"feature": "overall_height", "role": "oblique_massing", "value": total_h, "unit": "metres", "drives": "catalan_main_roof"},
        {"feature": "main_body_depth", "role": "oblique_massing", "value": depth, "unit": "metres", "drives": "catalan_streetwall"},
        {"feature": "piano_nobile_projection", "role": "street_identity", "value": 0.95, "unit": "metres", "drives": "catalan_piano_nobile_gallery"},
        {"feature": "oriel_projection", "role": "oblique_massing", "value": 1.10, "unit": "metres", "drives": "catalan_left_oriel_stack"},
        {"feature": "roof_rise", "role": "roof_plan", "value": 5.2, "unit": "metres", "drives": "catalan_main_roof"},
        {"feature": "skyline_groups", "role": "roof_plan", "value": 4, "unit": "count", "drives": "catalan_left_sculptural_turret"},
    ]
    production["fixed_identity"] = [
        "narrow near-planar streetwall", "localized floor-specific sculptural balconies",
        "two stacked end oriels", "piano-nobile organic gallery", "dragon-back roof mass",
        "left mosaic turret, central triple pots and paired decorated right chimneys",
        "narrow deep row-house section with authored long sides and rear",
    ]
    production["placement_contract"] = {
        "method": "sticker_method",
        "mode": "fixed_landmark",
        "ui_interaction": "select_and_place",
        "footprint_m": {"width": width, "depth": depth},
        "visible_height_m": total_h,
        "translation": "allowed",
        "rotation": "allowed",
        "uniform_scale": "discouraged",
        "non_uniform_scale": "forbidden",
        "floor_count_change": "forbidden",
        "polygon_fit": False,
        "preferred_context": "streetwall_party_wall",
        "freestanding_elevations": "authored",
        "lego_compatibility": "fixed_front_and_rear_endcaps_with_repeatable_side_bay_grammar",
    }
    production["image_lock"]["surface_registration"] = {
        "group": "catalan_front_elevation",
        "frame": {
            "centre_x_m": 0.0,
            "base_z_m": 0.0,
            "width_m": width,
            "height_m": wall_h,
            "uv_u_min": 0.0,
            "uv_u_max": 1.0,
            "uv_v_min": 0.0,
            "uv_v_max": 0.79,
        },
        "anchor_types": ["window_centres", "column_centres", "floor_datums"],
        "tolerance_uv": 1e-6,
    }
    graph["presentation_camera"] = {
        "oblique_x_scale": 0.30,
        "identity_distance_scale": 0.95,
        "street_distance_scale": 0.90,
    }


PATCHERS = {
    "classic_brownstone_federal": federal,
    "classic_brownstone_grey_stone": greystone,
    "modernist_civic_white_corbusian": white_corbusian,
    "modernist_civic_precast_panel": precast,
    "glass_office_terracotta_fins": terracotta,
    "glass_office_dark_frame": dark_frame,
    "nordic_timber_charred_wood": charred,
    "nordic_timber_cross_laminated": clt,
    "med_arcade_moorish": moorish,
    "med_arcade_catalan_modernista": catalan,
}


def refresh_contract(profile: dict[str, Any], variant: str) -> None:
    graph = profile["massing_graph"]
    graph["profile"] = f"{variant}_quality_lock_v88"
    graph["target_views"] = ["archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context"]
    production = profile["production_contract"]
    production["quality_contract_version"] = 4
    representation = (
        "registered_sticker_landmark"
        if variant in {"med_arcade_catalan_modernista", "med_arcade_moorish"}
        else "massing_graph"
    )
    production["stage_workflow"] = stage_workflow(representation)
    image_lock = production["image_lock"]
    image_lock["required_node_ids"] = [str(item["id"]) for item in graph.get("nodes") or []]
    image_lock["required_assembly_ids"] = [str(item["id"]) for item in graph.get("assemblies") or []]
    image_lock["required_node_kinds"] = dict(Counter(str(item["kind"]) for item in graph.get("nodes") or []))
    image_lock["required_assembly_kinds"] = dict(Counter(str(item["kind"]) for item in graph.get("assemblies") or []))
    image_lock["minimum_measurements"] = min(8, len(image_lock.get("measurements") or []))


def rename_materials(profile: dict[str, Any], recipes: list[dict[str, Any]]) -> None:
    for spec in profile.get("material_overrides", {}).values():
        key = spec.get("texture_key")
        if isinstance(key, str) and key.startswith("v87_"):
            spec["texture_key"] = "v88_" + key[4:]
    for recipe in recipes:
        key = str(recipe["output_key"])
        recipe["output_key"] = "v88_" + key[4:] if key.startswith("v87_") else key


def registry(batch_id: str, targets: list[tuple[Any, ...]]) -> dict[str, Any]:
    dimensions = {key: (value["width_m"], value["depth_m"], value["default_floors"]) for key, value in DIMENSION_OVERRIDES.items()}
    return {
        "schema": "catalogue-rollout-batch@1",
        "campaign": "tools/archetype_compiler/catalogue_round_v88.json",
        "pipeline_version": "v88",
        "surface_recipe_manifest": "tools/archetype_compiler/catalogue_round_v88_surface_recipes.json",
        "batch_id": batch_id,
        "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": parent, "variant_id": variant,
            "family_id": family.replace("-v87", "-v88"),
            "width_m": dimensions.get(variant, (width, depth, floors))[0],
            "depth_m": dimensions.get(variant, (width, depth, floors))[1],
            "floors": dimensions.get(variant, (width, depth, floors))[2],
            "allow_outside_bounds": variant in {
                "modernist_civic_precast_panel",
                "nordic_timber_charred_wood",
                # The exact terracotta reference is a four-level pavilion;
                # the parent catalogue's generic office defaults are taller.
                "glass_office_terracotta_fins",
            },
            "facade_sheet": f"artifacts/catalogue-rollout-v87/round-001/facade-sheets/{variant}",
        } for parent, variant, _index, family, width, depth, floors in targets],
    }


def main() -> None:
    profiles: dict[str, Any] = {}
    recipes: list[dict[str, Any]] = []
    for parent, variant, index, _family, width, depth, floors in TARGETS:
        draft = read_json(DRAFTS / f"{variant}.json")
        profile, variant_recipes = build_profile(parent, variant, index, width, depth, floors, draft)
        if variant == "glass_office_terracotta_fins" and "curtainwall_fins" not in profile.get("kits", []):
            profile.setdefault("kits", []).append("curtainwall_fins")
        if variant in {
            "glass_office_terracotta_fins",
            "glass_office_dark_frame",
            "med_arcade_catalan_modernista",
        }:
            # Their identity is owned by the exact V88 massing graph.  Parent
            # kit inheritance created dense generic cages in repeatable modules
            # and, in V87, made one optional floor exceed 22 MB.
            # Retain the semantic kit tags for catalogue identity, selection,
            # and regression tests.  The exact V88 graph owns their geometry;
            # rendering the inherited generic kit as well would duplicate the
            # frame/fins into the dense cages rejected in V87.
            profile["production_contract"]["geometry_kit_exclusions"] = list(profile.get("kits") or [])
        PATCHERS[variant](profile["massing_graph"], profile["production_contract"])
        if variant == "glass_office_terracotta_fins":
            profile["identity"] = "Glass office with terracotta fins and planted setbacks"
            profile.setdefault("material_overrides", {}).setdefault("primary", {})["base_color"] = "#a75f43"
        if variant in DIMENSION_OVERRIDES:
            profile["dimension_overrides"] = deepcopy(DIMENSION_OVERRIDES[variant])
        if variant in GLASS_PROFILE_OVERRIDES:
            profile["glass_profile"] = GLASS_PROFILE_OVERRIDES[variant]
        refresh_contract(profile, variant)
        rename_materials(profile, variant_recipes)
        profiles[variant] = profile
        recipes.extend(variant_recipes)
    write_json(PROFILE, {"schema": "architectural-signatures@1", "override_profiles": list(profiles), "profiles": profiles})
    write_json(RECIPES, {"schema": "surface-story-recipes@1", "round_id": "ROUND-001-V88", "recipes": recipes})
    write_json(BATCH_A, registry("ROUND-001-V88-A", list(TARGETS[:5])))
    write_json(BATCH_B, registry("ROUND-001-V88-B", list(TARGETS[5:])))
    repair_targets = [target for target in TARGETS if target[1] in {
        "classic_brownstone_grey_stone", "modernist_civic_white_corbusian",
        "modernist_civic_precast_panel", "glass_office_terracotta_fins",
    }]
    write_json(REPAIR_A, registry("ROUND-001-V88-REPAIR-A", repair_targets))
    repair_b_targets = [target for target in TARGETS if target[1] in {
        "glass_office_dark_frame", "nordic_timber_cross_laminated",
        "med_arcade_moorish", "med_arcade_catalan_modernista",
    }]
    write_json(REPAIR_B, registry("ROUND-001-V88-REPAIR-B", repair_b_targets))
    terracotta_target = [target for target in TARGETS if target[1] == "glass_office_terracotta_fins"]
    write_json(TERRACOTTA_RETRY, registry("ROUND-001-V88-TERRACOTTA-RETRY", terracotta_target))
    catalan_target = [target for target in TARGETS if target[1] == "med_arcade_catalan_modernista"]
    write_json(CATALAN_RETRY, registry("ROUND-001-V88-CATALAN-RETRY", catalan_target))
    write_json(CATALAN_STICKER_RETRY, registry("ROUND-001-V88-CATALAN-STICKER-RETRY", catalan_target))
    moorish_target = [target for target in TARGETS if target[1] == "med_arcade_moorish"]
    write_json(MOORISH_STICKER_RETRY, registry("ROUND-001-V89-MOORISH-STICKER-RETRY", moorish_target))
    print(PROFILE)


if __name__ == "__main__":
    main()
