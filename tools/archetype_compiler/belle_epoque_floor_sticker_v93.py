"""Build and audit floor-addressed Sticker Method plans for the Grand Magasin.

This module does not render or mutate the approved V92 clay lock.  It is the
Sticker Agent's executable hand-off to geometry/compiler code: each occupied
storey receives its own crop and z interval, while the roof remains a disjoint
material domain.  A six-storey plan is bounded to one inserted middle band and
requires a separately hashed segmented geometry bundle.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


TOOL_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = TOOL_DIR / "belle_epoque_floor_sticker_v93_contract.json"


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _crop_for_band(source: dict[str, Any], band_key: str, order: list[str]) -> dict[str, Any]:
    width, height = (int(value) for value in source["pixel_size"])
    breaks = [int(value) for value in source["vertical_breaks_y_px"]]
    index = order.index(band_key)
    y0, y1 = breaks[index], breaks[index + 1]
    return {
        "source_crop_xyxy": [0, y0, width, y1],
        "uv_crop": [0.0, y0 / height, 1.0, y1 / height],
        "source_pixel_size": [width, height],
        "vertical_orientation": "source_top_to_bottom; renderer converts to Blender bottom-origin UV",
    }


def _sequence_for_floor_count(contract: dict[str, Any], floor_count: int) -> list[str]:
    if floor_count == 5:
        return list(contract["wall_band_sequence_native"])
    if floor_count == 6:
        return list(contract["wall_band_sequence_six_storey"])
    raise ValueError(f"floor_count {floor_count} is outside the bounded [5, 6] pilot")


def build_floor_plan(
    floor_count: int,
    *,
    segmented_geometry_sha256: str | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = deepcopy(contract or load_contract())
    sequence = _sequence_for_floor_count(contract, floor_count)
    height = float(contract["unit_floor_height_m"])
    order = list(contract["break_order_top_to_bottom"])
    wall_top = height * floor_count
    instances: list[dict[str, Any]] = []

    repeat_seen = 0
    for floor_index, band_key in enumerate(sequence):
        if band_key == "middle_repeat":
            repeat_seen += 1
        instance_key = band_key if band_key != "middle_repeat" else f"middle_repeat_{repeat_seen:02d}"
        z0, z1 = floor_index * height, (floor_index + 1) * height
        for surface_id, binding in contract["surface_bindings"].items():
            source = contract["elevation_sources"][binding["source"]]
            item = {
                "id": f"{surface_id}_{instance_key}",
                "domain": "vertical_occupied_floor",
                "surface_id": surface_id,
                "floor_index": floor_index,
                "band_key": band_key,
                "instance_key": instance_key,
                "z_min_m": round(z0, 6),
                "z_max_m": round(z1, 6),
                "source_id": source["source_id"],
                "source_path": source["path"],
                "source_sha256": source["sha256"],
                "target_ids": [f"{surface_id}_{instance_key}"],
                "source_target_meshes": list(binding["targets"]),
                "material_class": f"floor_sticker_{band_key}_pbr",
                "roof_material_allowed": False,
                "repeatable": band_key == "middle_repeat",
            }
            item.update(_crop_for_band(source, band_key, order))
            instances.append(item)

    roof_source = contract["roof_source"]
    roof_shift = round((floor_count - int(contract["native_floor_count"])) * height, 6)
    roof = {
        "id": "roof_fixed",
        "domain": "roof_only",
        "band_key": "roof",
        "z_min_m": round(wall_top, 6),
        "translation_z_m": roof_shift,
        "source_id": roof_source["source_id"],
        "source_path": roof_source["path"],
        "target_class": roof_source["target_class"],
        "material_class": "roof_sticker_pbr",
        "vertical_wall_material_allowed": False,
        "source_crop_xyxy": [0, 0, 1254, 1254],
        "uv_crop": [0.0, 0.0, 1.0, 1.0],
    }

    geometry_status = "approved_v92_shape_requires_topology_subdivision" if floor_count == 5 else (
        "ready_separately_hashed_segmented_bundle" if segmented_geometry_sha256 else
        "blocked_missing_separately_hashed_segmented_bundle"
    )
    plan = {
        "schema": "belle-epoque-floor-sticker-plan@1",
        "building_id": contract["building_id"],
        "floor_count": floor_count,
        "unit_floor_height_m": height,
        "wall_top_z_m": round(wall_top, 6),
        "sequence": sequence,
        "floor_instances": instances,
        "roof_instance": roof,
        "segmented_geometry_sha256": segmented_geometry_sha256,
        "geometry_status": geometry_status,
        "top_crown_translation_z_m": roof_shift,
        "roof_translation_z_m": roof_shift,
        "monolithic_wall_scaling": "forbidden",
        "hard_stops": list(contract["ownership_hard_stops"]),
    }
    plan["audit"] = audit_floor_plan(plan, contract)
    return plan


def audit_floor_plan(plan: dict[str, Any], contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or load_contract()
    floor_count = int(plan["floor_count"])
    surfaces = set(contract["surface_bindings"])
    items = list(plan["floor_instances"])
    failures: list[dict[str, Any]] = []

    for surface in sorted(surfaces):
        bands = sorted((item for item in items if item["surface_id"] == surface), key=lambda item: item["z_min_m"])
        if len(bands) != floor_count:
            failures.append({"code": "missing_floor_band", "surface_id": surface, "count": len(bands), "expected": floor_count})
            continue
        if bands[0]["z_min_m"] != 0.0 or bands[-1]["z_max_m"] != plan["wall_top_z_m"]:
            failures.append({"code": "wall_band_extent_mismatch", "surface_id": surface})
        for lower, upper in zip(bands, bands[1:]):
            delta = round(float(upper["z_min_m"]) - float(lower["z_max_m"]), 6)
            if delta > 0:
                failures.append({"code": "gap_between_floor_bands", "surface_id": surface, "gap_m": delta})
            elif delta < 0:
                failures.append({"code": "overlapping_floor_bands", "surface_id": surface, "overlap_m": -delta})

    roof_source = str(contract["roof_source"]["source_id"])
    roof_on_wall = [item["id"] for item in items if item["source_id"] == roof_source or item["roof_material_allowed"]]
    if roof_on_wall:
        failures.append({"code": "roof_source_on_vertical_wall_or_top_crown", "instances": roof_on_wall})
    roof = plan["roof_instance"]
    if roof["domain"] != "roof_only" or roof["target_class"] != "roof_only" or roof["vertical_wall_material_allowed"]:
        failures.append({"code": "roof_domain_not_isolated", "roof": roof})

    expected_sequence = _sequence_for_floor_count(contract, floor_count)
    if plan["sequence"] != expected_sequence:
        failures.append({"code": "floor_sequence_mismatch", "actual": plan["sequence"], "expected": expected_sequence})
    if floor_count == 6 and not plan.get("segmented_geometry_sha256"):
        failures.append({"code": "six_storey_without_separately_hashed_segmented_geometry"})

    expected_shift = round((floor_count - 5) * float(contract["unit_floor_height_m"]), 6)
    if plan["top_crown_translation_z_m"] != expected_shift or plan["roof_translation_z_m"] != expected_shift:
        failures.append({"code": "fixed_upper_assembly_translation_mismatch", "expected_m": expected_shift})

    return {
        "status": "pass" if not failures else "blocked",
        "floor_band_count": floor_count,
        "elevation_surface_count": len(surfaces),
        "floor_sticker_instance_count": len(items),
        "roof_owned_vertical_wall_conflicts": roof_on_wall,
        "unowned_vertical_ranges": [],
        "failures": failures,
    }


def main() -> int:
    five = build_floor_plan(5)
    six = build_floor_plan(6)
    print(json.dumps({"five_storey": five, "six_storey": six}, indent=2))
    return 0 if five["audit"]["status"] == "pass" and six["audit"]["status"] == "blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
