"""Compile bounded five- and six-storey floor-sticker Grand Magasin profiles."""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from belle_epoque_floor_sticker_v93 import build_floor_plan
from build_belle_epoque_floor_geometry_v93 import build_segmented_geometry
from compile_belle_epoque_clay_sticker_v92 import build_profile as build_v92_profile


TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
OUTPUT = TOOL_DIR / "architectural_signature_profiles.d/zz_belle_epoque_floor_sticker_v93.json"
REGISTRY = TOOL_DIR / "belle_epoque_floor_sticker_v93.json"

FLOOR_SURFACE_IDS = {
    "facade_front", "facade_right", "facade_rear", "facade_left", "corner_pavilion",
    "court_front", "court_right", "court_rear", "court_left",
    "upper_front", "upper_right", "upper_rear", "upper_left", "corner_upper_returns",
}

PLANAR_AXES = {
    "facade_front": ("front", [0.0, -1.0], False),
    "facade_right": ("right", [1.0, 0.0], False),
    "facade_rear": ("rear", [0.0, 1.0], True),
    "facade_left": ("left", [-1.0, 0.0], True),
    "court_front": ("rear", [0.0, 1.0], True),
    "court_right": ("left", [-1.0, 0.0], True),
    "court_rear": ("front", [0.0, -1.0], False),
    "court_left": ("right", [1.0, 0.0], False),
}


def _bounds(mesh: dict[str, Any]) -> tuple[list[float], float, float]:
    xs, ys, zs = zip(*mesh["vertices"])
    centre = [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2]
    return centre, max(max(xs) - min(xs), max(ys) - min(ys), 0.05), max(max(zs) - min(zs), 0.05)


def _floor_carrier(item: dict[str, Any], mesh: dict[str, Any]) -> dict[str, Any]:
    centre, span, height = _bounds(mesh)
    surface = str(item["surface_id"])
    carrier: dict[str, Any] = {
        "id": f"v93_skin_{item['id']}",
        "kind": "carrier_skin",
        "surface_id": str(item["id"]),
        "semantic_surface_id": surface,
        "floor_index": int(item["floor_index"]),
        "floor_band": str(item["band_key"]),
        "target_ids": list(item["target_ids"]),
        "source_image_path": str(item["source_path"]),
        "source_id": str(item["source_id"]),
        "source_sha256": str(item["source_sha256"]),
        "source_crop_xyxy": list(item["source_crop_xyxy"]),
        "uv_crop": list(item["uv_crop"]),
        "centre": centre,
        "span_m": span,
        "height_m": height,
        "z_min_m": float(item["z_min_m"]),
        "z_max_m": float(item["z_max_m"]),
        "material_role": "elevation",
        "material_domain": "vertical_occupied_floor",
        "roof_material_allowed": False,
        "uv_u_min": float(item["uv_crop"][0]),
        "uv_u_max": float(item["uv_crop"][2]),
        # Source crops are measured from the raster top; Blender UV starts at
        # the raster bottom. Converting here keeps the renderer generic.
        "uv_v_min": 1.0 - float(item["uv_crop"][3]),
        "uv_v_max": 1.0 - float(item["uv_crop"][1]),
        "finish_class": str(item["material_class"]),
        "sticker_layer": "floor_band",
        "floor_role": "ground" if item["band_key"] == "ground" else (
            "top_crown" if item["band_key"] == "top_crown" else "middle"
        ),
        "final_surface_coverage": True,
    }
    if surface == "corner_pavilion":
        carrier.update({
            "axis": "cylindrical_segment", "origin_x": -11.0, "origin_y": -10.0,
            "angle_start_deg": 180.0, "angle_end_deg": 270.0,
            "normal_z_min": -0.25, "normal_z_max": 0.25,
        })
    else:
        axis, normal, flip = PLANAR_AXES[surface]
        carrier.update({
            "axis": axis, "normal_xy": normal, "normal_dot_min": 0.90,
            "normal_z_min": -1.01, "normal_z_max": 1.01, "flip_u": flip,
        })
    return carrier


def _floor_coverage_carrier(item: dict[str, Any], mesh: dict[str, Any]) -> dict[str, Any]:
    """Texture every cap/return before the registered outward face overrides it."""
    carrier = _floor_carrier(item, mesh)
    carrier.update({
        "id": f"v93_coverage_{item['id']}",
        "axis": "box_projected",
        "normal_z_min": -1.01,
        "normal_z_max": 1.01,
        "box_bounds": [-21.25, 18.35, -20.25, 17.35, 0.0, 35.1],
        "sticker_layer": "floor_coverage_seal",
    })
    carrier.pop("normal_xy", None)
    carrier.pop("normal_dot_min", None)
    carrier.pop("origin_x", None)
    carrier.pop("origin_y", None)
    carrier.pop("angle_start_deg", None)
    carrier.pop("angle_end_deg", None)
    return carrier


def _shift_existing_carrier(item: dict[str, Any], dz: float) -> dict[str, Any]:
    shifted = deepcopy(item)
    if not dz:
        return shifted
    targets = [str(value) for value in shifted.get("target_ids", [])]
    move = any(
        name.startswith("dormer_") or "dome" in name or "cupola" in name or "cornice" in name
        or "crown" in name or name == "corner_upper_tower" or name == "watertight_perimeter_court_crown"
        for name in targets
    )
    if move:
        if "centre" in shifted:
            shifted["centre"][2] = round(float(shifted["centre"][2]) + dz, 6)
        for key in ("z_min_m", "z_max_m", "dome_base_z"):
            if key in shifted:
                shifted[key] = round(float(shifted[key]) + dz, 6)
    return shifted


def build_profile(floor_count: int) -> dict[str, Any]:
    base, _registry = build_v92_profile()
    geometry = build_segmented_geometry(floor_count)
    if geometry["audit"]["status"] != "pass":
        raise RuntimeError(f"segmented {floor_count}-storey geometry did not pass")
    plan = build_floor_plan(floor_count, segmented_geometry_sha256=geometry["geometry_sha256"])
    if plan["audit"]["status"] != "pass":
        raise RuntimeError(f"floor sticker plan for {floor_count} storeys did not pass")
    profile = deepcopy(base)
    mesh_by_name = {str(mesh["name"]): mesh for mesh in geometry["meshes"]}
    profile["identity"] = f"Belle Epoque Grand Magasin V93, {floor_count} storeys, segmented floor stickers"
    profile["dimension_overrides"] = {"width_m": 36.0, "depth_m": 34.0, "default_floors": floor_count}
    graph = profile["massing_graph"]
    graph["profile"] = f"belle-epoque-floor-sticker-v93-{floor_count}"
    graph["height_m"] = 31.0 + geometry["roof_translation_z_m"]
    graph["reference_dimensions"]["floors"] = floor_count
    graph["nodes"][0]["geometry_sha256"] = geometry["geometry_sha256"]
    graph["nodes"][0]["meshes"] = [
        {
            "name": mesh["name"], "vertices": mesh["vertices"], "faces": mesh["faces"],
            "material": "roof" if mesh.get("material_domain") == "roof_only" else "primary",
            "material_domain": mesh.get("material_domain"),
        }
        for mesh in geometry["meshes"]
    ]
    retained = []
    for item in graph["assemblies"]:
        belongs_to_floor_surface = (
            str(item.get("surface_id")) in FLOOR_SURFACE_IDS
            or str(item.get("semantic_surface_id")) in FLOOR_SURFACE_IDS
        )
        surviving_targets = [name for name in item.get("target_ids", []) if name in mesh_by_name]
        keep_fixed_coverage = item.get("sticker_layer") == "coverage_seal" and bool(surviving_targets)
        if belongs_to_floor_surface and not keep_fixed_coverage:
            continue
        retained_item = _shift_existing_carrier(item, float(geometry["roof_translation_z_m"]))
        if keep_fixed_coverage:
            retained_item["target_ids"] = surviving_targets
            # These surviving V92 seals belong to fixed entrance returns, not
            # to the full-height corner elevation. Giving them their own
            # semantic owner prevents them from masquerading as a second
            # corner-pavilion atlas alongside the V93 floor bands.
            retained_item["semantic_surface_id"] = "entrance_jamb"
            retained_item["floor_role"] = "ground"
        retained.append(retained_item)
    floor_coverage = [_floor_coverage_carrier(item, mesh_by_name[item["target_ids"][0]]) for item in plan["floor_instances"]]
    floor_hero = [_floor_carrier(item, mesh_by_name[item["target_ids"][0]]) for item in plan["floor_instances"]]
    graph["assemblies"] = retained + floor_coverage + floor_hero
    graph["floor_sticker_contract"] = {
        "required": True,
        "floor_count": floor_count,
        "unit_floor_height_m": plan["unit_floor_height_m"],
        "roof_starts_at_z_m": plan["wall_top_z_m"],
        "roof_source_on_vertical_wall_or_top_crown": "hard_stop",
        "band_gaps_or_overlaps": "hard_stop",
    }

    production = profile["production_contract"]
    production["representation"] = "segmented_geometry_plus_floor_addressed_native_stickers"
    production["clay_lock"]["geometry_sha256"] = geometry["geometry_sha256"]
    production["clay_lock"]["source_v92_geometry_sha256"] = geometry["source_v92_geometry_sha256"]
    production["clay_lock"]["status"] = "approved_segmented_v93"
    production["placement_contract"] = {
        "mode": "bounded_floor_variant_select_and_place", "allowed_floor_counts": [5, 6],
        "polygon_fit": False, "non_uniform_scale": "forbidden",
    }
    production["floor_sticker_method"] = {
        "schema": plan["schema"], "floor_count": floor_count, "sequence": plan["sequence"],
        "unit_floor_height_m": plan["unit_floor_height_m"], "geometry_sha256": geometry["geometry_sha256"],
        "audit": plan["audit"], "roof_domain": plan["roof_instance"],
        "floor_coverage_seal_count": len(floor_coverage),
        "floor_hero_sticker_count": len(floor_hero),
        "roof_source_on_vertical_wall_or_top_crown": "forbidden",
        "unowned_visible_face": "hard_stop",
        "generic_blue_grey_or_clay_fallback": "hard_stop",
    }
    production["image_lock"]["required_assembly_ids"] = [item["id"] for item in graph["assemblies"]]
    production["image_lock"]["required_assembly_kinds"] = {"carrier_skin": len(graph["assemblies"])}
    return profile


def build_profiles(active_floor_count: int = 5) -> tuple[dict[str, Any], dict[str, Any]]:
    if active_floor_count not in (5, 6):
        raise ValueError("active_floor_count must be 5 or 6")
    profiles = {}
    entries = []
    for floor_count in (5, 6):
        key = f"grand-magasin-belle-epoque-floor-{floor_count}"
        profile = build_profile(floor_count)
        profiles[key] = profile
        entries.append({
            "archetype_id": "grand_magasin", "variant_id": key,
            "family_id": f"belle-epoque-grand-magasin-v93-{floor_count}",
            "width_m": 36.0, "depth_m": 34.0, "floors": floor_count,
        })
    # The catalogue contains one canonical variant id. Keep both bounded plans
    # addressable for tests/review and bind the requested one to that real id
    # for ordinary generate_family execution.
    profiles["grand-magasin-belle-epoque"] = deepcopy(
        profiles[f"grand-magasin-belle-epoque-floor-{active_floor_count}"]
    )
    payload = {
        "schema": "architectural-signatures@1",
        "override_profiles": ["grand-magasin-belle-epoque"],
        "profiles": profiles,
    }
    registry = {"schema": "catalogue-rollout-batch@1", "pipeline_version": "v93", "batch_id": "BELLE-EPOQUE-FLOOR-STICKER-V93", "paid_facade_calls": 0, "entries": entries}
    return payload, registry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--active-floor-count", type=int, choices=(5, 6), default=5)
    args = parser.parse_args()
    profiles, registry = build_profiles(args.active_floor_count)
    OUTPUT.write_text(json.dumps(profiles, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": str(OUTPUT), "registry": str(REGISTRY)}, indent=2))


if __name__ == "__main__":
    main()
