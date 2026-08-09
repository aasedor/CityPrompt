"""Compile the bounded V87 image-authored pilot into deterministic profiles.

The multimodal drafts remain evidence, not executable geometry.  This compiler
normalizes their coordinate system, applies reviewed architectural repairs,
adds side/rear surface and glazing depth, and emits ordinary checked-in profile
and PBR recipe manifests for the existing Blender pipeline.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools/archetype_compiler"
DEFAULT_DRAFTS = TOOLS / "catalogue_round_v87_authoring_drafts"
DEFAULT_PROFILE = TOOLS / "architectural_signature_profiles.d/catalogue_round_v87.json"
DEFAULT_RECIPES = TOOLS / "catalogue_round_v87_surface_recipes.json"
DEFAULT_BATCH_A = TOOLS / "catalogue_round_v87_batch_a.json"
DEFAULT_BATCH_B = TOOLS / "catalogue_round_v87_batch_b.json"


TARGETS = (
    ("classic_brownstone_streetwall", "classic_brownstone_federal", 1, "classic-brownstone-federal-v87", 18.0, 18.0, 3),
    ("classic_brownstone_streetwall", "classic_brownstone_grey_stone", 2, "classic-brownstone-greystone-v87", 18.0, 18.0, 3),
    ("modernist_civic_block", "modernist_civic_white_corbusian", 1, "modernist-civic-white-v87", 43.0, 26.0, 5),
    ("modernist_civic_block", "modernist_civic_precast_panel", 2, "modernist-civic-precast-v87", 31.0, 25.0, 5),
    ("modern_glass_office_institutional", "glass_office_terracotta_fins", 1, "glass-office-terracotta-v87", 36.0, 25.0, 5),
    ("modern_glass_office_institutional", "glass_office_dark_frame", 2, "glass-office-dark-frame-v87", 36.0, 26.0, 6),
    ("nordic_timber_midrise", "nordic_timber_charred_wood", 1, "nordic-timber-charred-v87", 15.0, 14.0, 3),
    ("nordic_timber_midrise", "nordic_timber_cross_laminated", 2, "nordic-timber-clt-v87", 20.0, 16.0, 4),
    ("mediterranean_arcade_mixed_use", "med_arcade_moorish", 1, "med-arcade-moorish-v87", 20.0, 15.0, 2),
    ("mediterranean_arcade_mixed_use", "med_arcade_catalan_modernista", 2, "med-arcade-catalan-v87", 20.0, 16.0, 6),
)

OUTSIDE_BOUNDS = {"modernist_civic_precast_panel", "nordic_timber_charred_wood"}


SOURCE_FALLBACKS = {
    "natural_timber": "natural_timber",
    "curtain_wall": "curtain_wall",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def node_top(node: dict[str, Any]) -> float:
    location = node.get("location") or [0, 0, 0]
    if "size" in node:
        return float(location[2]) + float(node["size"][2]) / 2
    return float(location[2]) + float(node.get("height_m", 0)) / 2


def normalize_front(nodes: list[dict[str, Any]], skins: list[dict[str, Any]]) -> None:
    front = next((skin for skin in skins if skin.get("axis") == "front"), None)
    if not front or float(front["centre"][1]) <= 0:
        return
    for item in [*nodes, *skins]:
        key = "location" if "location" in item else "centre"
        if key in item:
            item[key][1] = -float(item[key][1])


def four_side_skins(nodes: list[dict[str, Any]], skins: list[dict[str, Any]]) -> None:
    mass_nodes = [node for node in nodes if "size" in node and node.get("kind") in {"box", "chamfered_box", "opening_block"}]
    x0 = min(float(node["location"][0]) - float(node["size"][0]) / 2 for node in mass_nodes)
    x1 = max(float(node["location"][0]) + float(node["size"][0]) / 2 for node in mass_nodes)
    y0 = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in mass_nodes)
    y1 = max(float(node["location"][1]) + float(node["size"][1]) / 2 for node in mass_nodes)
    height = max(node_top(node) for node in mass_nodes)
    existing = {str(skin.get("axis")) for skin in skins}
    specs = {
        "front": ([((x0 + x1) / 2), y0 - 0.05, height / 2], x1 - x0, False),
        "rear": ([((x0 + x1) / 2), y1 + 0.05, height / 2], x1 - x0, True),
        "left": ([x0 - 0.05, ((y0 + y1) / 2), height / 2], y1 - y0, True),
        "right": ([x1 + 0.05, ((y0 + y1) / 2), height / 2], y1 - y0, False),
    }
    for axis, (centre, span, flip) in specs.items():
        if axis not in existing:
            skins.append({
                "id": f"{axis}_depth_skin", "axis": axis, "centre": centre,
                "span_m": span, "height_m": height, "depth_m": 0.05,
                "band": "elevation", "flip_u": flip,
            })


def patch_nodes(variant: str, nodes: list[dict[str, Any]], skins: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    nodes = deepcopy(nodes)
    skins = deepcopy(skins)
    voids: list[dict[str, Any]] = []

    # The source image is a low, terraced office.  The draft correctly found
    # its stepped masses but over-counted storeys and stretched every level.
    # Scale the complete vertical schedule as one system so roofs, facade bands
    # and fixed details stay registered instead of deleting arbitrary floors.
    if variant == "glass_office_terracotta_fins":
        vertical_scale = 0.68
        for node in nodes:
            if "location" in node:
                node["location"][2] = round(float(node["location"][2]) * vertical_scale, 4)
            if "size" in node:
                node["size"][2] = round(float(node["size"][2]) * vertical_scale, 4)
            elif "height_m" in node:
                node["height_m"] = round(float(node["height_m"]) * vertical_scale, 4)
        for skin in skins:
            skin["centre"][2] = round(float(skin["centre"][2]) * vertical_scale, 4)
            skin["height_m"] = round(float(skin["height_m"]) * vertical_scale, 4)
    for node in nodes:
        if node.get("kind") in {"cylinder", "cone"} and "size" in node:
            size = node.pop("size")
            node["radius_m"] = max(float(size[0]), float(size[1])) / 2
            node["height_m"] = float(size[2])
            node.setdefault("vertices", 32)
    by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        if node.get("kind") in {"gable_roof", "hipped_roof"}:
            node.setdefault("ridge_axis", "x" if float(node["size"][0]) >= float(node["size"][1]) else "y")

    if variant == "classic_brownstone_grey_stone":
        height = max(node_top(node) for node in nodes if node.get("kind") != "box" or "chimney" not in node["id"])
        nodes.append({"id": "greystone_roof_membrane", "kind": "box", "size": [17.4, 17.4, 0.14], "location": [0, 0, height + 0.07], "material": "roof", "bevel_m": 0.02})
    elif variant == "classic_brownstone_federal":
        front_y = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in nodes if "size" in node)
        nodes.extend([
            {"id": "federal_entry_left", "kind": "box", "size": [0.42, 0.42, 3.1], "location": [-1.32, front_y - 0.18, 1.55], "material": "secondary", "bevel_m": 0.035},
            {"id": "federal_entry_right", "kind": "box", "size": [0.42, 0.42, 3.1], "location": [1.32, front_y - 0.18, 1.55], "material": "secondary", "bevel_m": 0.035},
            {"id": "federal_entry_head", "kind": "box", "size": [3.05, 0.48, 0.48], "location": [0, front_y - 0.22, 3.25], "material": "secondary", "bevel_m": 0.04},
        ])
        for floor in range(3):
            for bay, x in enumerate((-6.5, -3.25, 0.0, 3.25, 6.5)):
                nodes.append({"id": f"federal_lintel_{floor}_{bay}", "kind": "box", "size": [1.65, 0.28, 0.20], "location": [x, front_y - 0.12, 2.75 + floor * 3.0], "material": "secondary", "bevel_m": 0.025})
    elif variant == "modernist_civic_white_corbusian":
        nodes = [node for node in nodes if node["id"] != "pergola_canopy"]
        top = max(node_top(node) for node in nodes)
        nodes.extend([
            {"id": "roof_garden_membrane", "kind": "box", "size": [42.5, 25.5, 0.12], "location": [0, 0, top + 0.06], "material": "roof", "bevel_m": 0.02},
            {"id": "pergola_front_beam", "kind": "box", "size": [17, 0.22, 0.28], "location": [6, -7, top + 2.2], "material": "secondary", "bevel_m": 0.03},
            {"id": "pergola_rear_beam", "kind": "box", "size": [17, 0.22, 0.28], "location": [6, 5, top + 2.2], "material": "secondary", "bevel_m": 0.03},
            {"id": "pergola_left_beam", "kind": "box", "size": [0.22, 12, 0.28], "location": [-2.4, -1, top + 2.2], "material": "secondary", "bevel_m": 0.03},
            {"id": "pergola_right_beam", "kind": "box", "size": [0.22, 12, 0.28], "location": [14.4, -1, top + 2.2], "material": "secondary", "bevel_m": 0.03},
        ])
    elif variant == "glass_office_terracotta_fins":
        front_y = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in nodes if "size" in node)
        facade_top = max(node_top(node) for node in nodes if "level" in node["id"] or node["id"] == "ground_colonnade")
        for index in range(11):
            x = -17.2 + index * 3.44
            nodes.append({"id": f"terracotta_fin_{index:02d}", "kind": "box", "size": [0.28, 0.72, facade_top], "location": [x, front_y - 0.36, facade_top / 2], "material": "primary", "bevel_m": 0.035})
        for index, z in enumerate((3.4, 6.8, 10.2, 13.6, 17.0)):
            nodes.append({"id": f"terrace_edge_{index:02d}", "kind": "box", "size": [35.6, 1.25, 0.22], "location": [0, front_y - 0.5, z], "material": "primary", "bevel_m": 0.03})
    elif variant == "glass_office_dark_frame":
        nodes = [node for node in nodes if node["id"] != "mass_roof_trellis"]
        top = max(node_top(node) for node in nodes)
        nodes.append({"id": "dark_roof_membrane", "kind": "box", "size": [35.5, 25.5, 0.14], "location": [0, 0, top + 0.07], "material": "roof", "bevel_m": 0.02})
        for name, size, location in (
            ("front", [35.5, .25, .3], [0, -12.6, top + 2.2]), ("rear", [35.5, .25, .3], [0, 12.6, top + 2.2]),
            ("left", [.25, 25.5, .3], [-17.6, 0, top + 2.2]), ("right", [.25, 25.5, .3], [17.6, 0, top + 2.2]),
        ):
            nodes.append({"id": f"dark_crown_{name}", "kind": "box", "size": size, "location": location, "material": "primary", "bevel_m": 0.03})
    elif variant == "nordic_timber_charred_wood":
        front_y = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in nodes if "size" in node)
        # Warm natural-timber returns are a physical depth cue in the source,
        # not merely a colour painted into the facade sheet.
        nodes.extend([
            {"id": "charred_entry_left_reveal", "kind": "box", "size": [0.28, 0.42, 2.65], "location": [-1.18, front_y - 0.18, 1.325], "material": "secondary", "bevel_m": 0.025},
            {"id": "charred_entry_right_reveal", "kind": "box", "size": [0.28, 0.42, 2.65], "location": [1.18, front_y - 0.18, 1.325], "material": "secondary", "bevel_m": 0.025},
            {"id": "charred_entry_head_reveal", "kind": "box", "size": [2.64, 0.42, 0.28], "location": [0, front_y - 0.18, 2.51], "material": "secondary", "bevel_m": 0.025},
        ])
    elif variant == "nordic_timber_cross_laminated":
        front_y = min(float(node["location"][1]) - float(node["size"][1]) / 2 for node in nodes if "size" in node)
        # The pale pine window/reveal layer needs at least one exported PBR
        # owner.  These vertical members also break the flat atlas-card read.
        for index, x in enumerate((-7.5, -3.75, 0.0, 3.75, 7.5)):
            nodes.append({"id": f"clt_pine_reveal_{index:02d}", "kind": "box", "size": [0.22, 0.34, 11.8], "location": [x, front_y - 0.14, 6.1], "material": "secondary", "bevel_m": 0.02})
    elif variant == "med_arcade_catalan_modernista":
        # Keep the image-authored skin, but give its repeated rounded bays and
        # balcony edges real silhouette/shadow ownership.  The initial draft's
        # oversized tower/chimneys made the roof read as a fantasy castle.
        for node in nodes:
            if node["id"] == "left_tower_cyl":
                node.update({"radius_m": 0.85, "height_m": 3.2, "location": [-8.0, -6.2, 19.6]})
            elif node["id"] == "left_tower_cone":
                node.update({"radius_m": 0.95, "height_m": 2.0, "location": [-8.0, -6.2, 22.2]})
            elif node["id"].startswith("chimney_"):
                node["radius_m"] = 0.42
                node["height_m"] = 2.4
                node["location"][2] = 20.2
    elif variant == "med_arcade_moorish":
        ground = by_id["ground_mass"]
        ground.update({
            "id": "ground_arcade", "kind": "opening_block", "opening_shape": "round_arch",
            "opening_count": 3, "opening_width_m": 4.5, "opening_base_m": 0.10,
            "opening_height_m": 4.00, "spring_height_m": 1.75, "side_margin_m": 1.0,
            "section_mode": "recessed", "lining_material": "secondary",
            "trim_material": "secondary", "back_material": "interior_warm",
            "trim_profile_m": 0.20, "trim_depth_m": 0.28,
        })
        usable = 20.0 - 2.0
        centres = [-usable / 2 + usable / 3 * (index + 0.5) for index in range(3)]
        front = next(skin for skin in skins if skin["id"] == "skin_arcade_front")
        front["band"] = "podium"
        front["opening_clearances"] = [
            {"void_id": "moorish_arcade", "centre_m": centre, "base_z_m": 0.10, "width_m": 4.5, "height_m": 3.90}
            for centre in centres
        ]
        for skin in skins:
            if skin["id"] in {"skin_arcade_right"}:
                skin["band"] = "podium"
            elif "parapet" in skin["id"]:
                skin["band"] = "crown"
            elif "upper" in skin["id"]:
                skin["band"] = "floor"
        voids.append({"id": "moorish_arcade", "shape": "round_arch_passage", "axis": "front", "size": [18.0, 15.0, 3.90], "location": [0, 0, 2.05], "purpose": "three construction-depth shaded souk bays"})

    normalize_front(nodes, skins)
    four_side_skins(nodes, skins)
    return nodes, skins, voids


def glazing_overlays(skins: list[dict[str, Any]], variant: str) -> list[dict[str, Any]]:
    overlays = []
    glass_profile = "office_clear_occupied" if variant.startswith("glass_office_") else "residential_low_e"
    for skin in skins:
        if float(skin.get("height_m", 0)) < 1.4 or skin.get("opening_clearances"):
            continue
        if skin.get("axis") not in {"front", "rear", "left", "right"}:
            continue
        overlay = {k: deepcopy(v) for k, v in skin.items() if k not in {"opening_clearances"}}
        overlay.update({
            "id": f"{skin['id']}_glazing", "kind": "glazing_overlay",
            "columns": max(2, round(float(skin["span_m"]) / 3.2)), "rows": 1,
            "glass_profile": glass_profile, "frame_mode": "region_caps",
            "opening_returns": True, "pane_recess_m": 0.20, "cavity_depth_m": 0.48,
            "room_card_recess_m": 0.12,
            # Bound physical reveal/interior geometry independently of the
            # baked facade image. The visible sheet still carries every bay.
            "max_regions": 6 if variant == "glass_office_terracotta_fins" else 8,
        })
        if variant.startswith("glass_office_") or variant.startswith("modernist_civic_"):
            overlay.update({"frame_mode": "mask_only", "opening_returns": False})
        overlays.append(overlay)
    return overlays


def floor_register_skins(skins: list[dict[str, Any]], variant: str, floors: int) -> list[dict[str, Any]]:
    """Use generated storey bands at real storey count instead of squashing a full elevation."""
    banded_variants = {
        "classic_brownstone_federal", "classic_brownstone_grey_stone",
        "modernist_civic_precast_panel", "glass_office_dark_frame",
        "nordic_timber_charred_wood", "nordic_timber_cross_laminated",
        "med_arcade_catalan_modernista",
    }
    if variant not in banded_variants:
        return skins
    resolved: list[dict[str, Any]] = []
    for skin in skins:
        height = float(skin.get("height_m", 0))
        centre_z = float((skin.get("centre") or [0, 0, 0])[2])
        if height < 2.0 or abs(centre_z - height / 2) > 0.15 or skin.get("opening_clearances"):
            resolved.append(skin)
            continue
        storey = height / floors
        for level in range(floors):
            segment = deepcopy(skin)
            segment["id"] = f"{skin['id']}_storey_{level:02d}"
            segment["height_m"] = storey
            segment["centre"][2] = storey * (level + 0.5)
            segment["band"] = "podium" if level == 0 else ("floor_alt" if level % 3 == 0 else "floor")
            resolved.append(segment)
    return resolved


def build_profile(parent: str, variant: str, index: int, width: float, depth: float, floors: int, draft: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    draft = deepcopy(draft)
    if variant == "modernist_civic_precast_panel":
        draft["identity"] = (
            "strict rectilinear five-storey precast civic building with a square concrete grid "
            "and only rectangular dark-recessed windows; no arches, curved heads or historic ornament"
        )
        draft["fixed_identity"] = [
            "rectangular window openings only; no arches or curved heads",
            "five visible storeys above the glazed base",
            *draft["fixed_identity"],
        ]
    nodes, skins, voids = patch_nodes(variant, draft["nodes"], draft["skins"])
    skins = floor_register_skins(skins, variant, floors)
    assemblies = [{"kind": "facade_skin", **skin} for skin in skins]
    assemblies.extend(glazing_overlays(skins, variant))
    graph_height = max(node_top(node) for node in nodes)
    height = (
        graph_height
        if variant in {"glass_office_terracotta_fins", "med_arcade_catalan_modernista"}
        else max(float(draft["overall_height_m"]), graph_height)
    )
    material_overrides: dict[str, Any] = {}
    recipes = []
    for slot, material in draft["materials"].items():
        source = SOURCE_FALLBACKS.get(material["source_key"], material["source_key"])
        output_key = f"v87_{variant}_{slot}"
        recipes.append({
            "output_key": output_key, "source_key": source, "tint": material["base_color"],
            "tint_mix": 0.44, "macro_strength": 0.06, "roughness_strength": 0.09,
            "normal_strength": 4.0 if source == "white_plaster" else 2.6 if source == "limestone" else 1.85,
            "role": material["role"],
        })
        material_overrides[slot] = {
            "texture_key": output_key, "base_color": material["base_color"],
            "roughness": 0.86 if slot != "roof" else 0.82, "metallic": 0.0,
            "baked_pbr": True, "texture_tile_metres": 4.0 if slot != "roof" else 5.5,
            "normal_strength": 0.72,
        }
    node_counts = dict(Counter(str(node["kind"]) for node in nodes))
    assembly_counts = dict(Counter(str(item["kind"]) for item in assemblies))
    required_nodes = [str(node["id"]) for node in nodes]
    required_assemblies = [str(item["id"]) for item in assemblies]
    production: dict[str, Any] = {
        "identity_mode": "massing_graph",
        "fixed_identity": draft["fixed_identity"],
        "repeatable_capacity": draft["repeatable_capacity"],
        "quality_contract_version": 3,
        "image_lock": {
            "required_reference_roles": ["street_identity", "oblique_massing", "roof_plan"],
            "minimum_measurements": 8, "measurements": draft["measurements"],
            "required_node_ids": required_nodes, "required_assembly_ids": required_assemblies,
            "required_node_kinds": node_counts, "required_assembly_kinds": assembly_counts,
        },
        "material_continuity": {"required_textured_materials": list(draft["materials"])},
        "surface_finish": {
            "method": "baked_pbr_story", "required_baked_materials": list(draft["materials"]),
            "material_roles": {slot: value["role"] for slot, value in draft["materials"].items()},
            "required_channels": ["albedo", "roughness", "normal"],
            "uv_contract": {"projection": "metric_box_plus_material_scale", "base_tile_metres": 2.0, "minimum_tile_metres": 3.0, "maximum_tile_metres": 8.0},
            "semantic_weathering": [
                "wall variation remains bounded to the authored wall materials",
                "roof variation remains on horizontal or pitched roof fields",
                "glazing keeps physical pane, reveal and occupied-interior depth",
            ],
            "qa_renders": ["neutral_source", "neutral_glb_roundtrip", "archetype_match", "facade_close", "roof_audit", "rear_corner_oblique"],
        },
    }
    if variant == "med_arcade_moorish":
        production["material_continuity"]["node_bindings"] = [{"kind": "opening_block", "ids": ["ground_arcade"], "slots": {"material": "primary", "lining_material": "secondary", "trim_material": "secondary"}}]
        production["spatial_voids"] = {"required_passages": [{
            "void_id": "moorish_arcade", "target_node_id": "ground_arcade", "target_node_kind": "opening_block",
            "shape": "round_arch_passage", "section_mode": "recessed", "minimum_depth_m": 8.0,
            "minimum_opening_count": 3, "minimum_clearance_count": 3,
        }]}
    refs = [
        {"role": "street_identity", "path": f"/archetypes/buildings/{parent}/variant_{index}.png"},
        {"role": "oblique_massing", "path": f"/archetypes/buildings/{parent}/variant_{index}_angle_60.jpg"},
        {"role": "roof_plan", "path": f"/archetypes/buildings/{parent}/variant_{index}_angle_90.jpg"},
    ]
    return ({
        "extends": parent, "identity": draft["identity"],
        "dimension_overrides": {"width_m": width, "depth_m": depth, "default_floors": floors},
        "material_overrides": material_overrides,
        "evidence_policy": {
            "authority": "reference_images", "metadata_mode": "disabled", "selected_metadata": [],
            "ignored_metadata": [{"path": "*", "reason": "exact three-view reference set is the geometry authority; metadata was not allowed to override visible evidence"}],
        },
        "production_contract": production,
        "massing_graph": {
            "schema": "massing-graph@1", "profile": f"{variant}_image_lock_v87",
            "description": draft["identity"], "height_m": height,
            "reference_dimensions": {"width_m": width, "depth_m": depth, "floors": floors},
            "reference_views": refs, "presentation_camera": draft["presentation_camera"],
            "nodes": nodes, "voids": voids, "assemblies": assemblies,
            "target_views": ["archetype_match", "street", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context"],
        },
    }, recipes)


def build_registry(batch_id: str, targets: list[tuple[Any, ...]]) -> dict[str, Any]:
    return {
        "schema": "catalogue-rollout-batch@1", "campaign": "tools/archetype_compiler/catalogue_round_v87.json",
        "pipeline_version": "v87", "surface_recipe_manifest": "tools/archetype_compiler/catalogue_round_v87_surface_recipes.json",
        "batch_id": batch_id, "paid_facade_calls": 0,
        "entries": [{
            "archetype_id": parent, "variant_id": variant, "family_id": family,
            "width_m": width, "depth_m": depth, "floors": floors,
            "allow_outside_bounds": variant in OUTSIDE_BOUNDS,
            "facade_sheet": f"artifacts/catalogue-rollout-v87/round-001/facade-sheets/{variant}",
        } for parent, variant, _index, family, width, depth, floors in targets],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft-root", type=Path, default=DEFAULT_DRAFTS)
    parser.add_argument("--profile-output", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--recipe-output", type=Path, default=DEFAULT_RECIPES)
    args = parser.parse_args()
    profiles: dict[str, Any] = {}
    recipes: list[dict[str, Any]] = []
    for parent, variant, index, _family, width, depth, floors in TARGETS:
        draft = read_json(args.draft_root / f"{variant}.json")
        profile, variant_recipes = build_profile(parent, variant, index, width, depth, floors, draft)
        profiles[variant] = profile
        recipes.extend(variant_recipes)
    write_json(args.profile_output, {
        "schema": "architectural-signatures@1",
        "override_profiles": ["glass_office_dark_frame", "glass_office_terracotta_fins"],
        "profiles": profiles,
    })
    write_json(args.recipe_output, {"schema": "surface-story-recipes@1", "round_id": "ROUND-001", "recipes": recipes})
    write_json(DEFAULT_BATCH_A, build_registry("ROUND-001-A", list(TARGETS[:5])))
    write_json(DEFAULT_BATCH_B, build_registry("ROUND-001-B", list(TARGETS[5:])))
    print(args.profile_output)


if __name__ == "__main__":
    main()
